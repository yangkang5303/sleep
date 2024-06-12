import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def read_bys_file(file_path):
    """读取二进制文件并返回十六进制字符串。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'rb') as file:
        binary_data = file.read()
    # 将二进制数据转换为十六进制字符串
    hex_data = binary_data.hex()
    return hex_data

def parse_time(hex_str):
    """将16进制字符串解析为人类友好的时间字符串。"""
    year = int(hex_str[0:2], 16) + 2000  # 从2000年开始
    month = int(hex_str[2:4], 16)
    day = int(hex_str[4:6], 16)
    hour = int(hex_str[6:8], 16)
    minute = int(hex_str[8:10], 16)
    second = int(hex_str[10:12], 16)
    return datetime(year, month, day, hour, minute, second)

def parse_header(hex_data):
    """解析文件头部信息，返回人类友好的信息。"""
    # 假设的头部字段及其解释
    fields = {
        'start_time': hex_data[0:12],  # 例：18060b162100 -> 2024-06-11 22:33
        'end_time': hex_data[12:24],   # 例：18060c061d00 -> 2024-06-12 06:29
        'device_model': hex_data[64:96],  # 示例：5948353630412d323433323230343932 -> YH560A-243220492
    }

    # 转换时间格式
    start_time = parse_time(fields['start_time'])
    end_time = parse_time(fields['end_time'])

    # 转换设备型号
    try:
        device_model = bytes.fromhex(fields['device_model']).decode('latin1')
    except UnicodeDecodeError:
        device_model = "Unknown Model"

    return {
        'start_time': start_time,
        'end_time': end_time,
        'device_model': device_model,
    }

def parse_hex_data(hex_data):
    """将十六进制字符串解析为压力值列表。"""
    # 每4个字符（十六进制表示2字节）为一个数据点，转换为整数
    hex_values = [hex_data[i:i + 4] for i in range(0, len(hex_data), 4)]
    pressure_values = [int(h, 16) for h in hex_values]
    return pressure_values

def analyze_pressure_data(start_time, pressure_values):
    """分析压力数据并生成统计信息和图表。"""
    # 呼吸统计分析
    valid_pressures = [value for value in pressure_values[26:-1] if value > 1]
    if not valid_pressures:
        raise ValueError("No valid pressure values found.")

    max_pressure = np.max(valid_pressures)
    min_pressure = np.min(valid_pressures)
    median_pressure = np.median(valid_pressures)
    sleep_mins = len(valid_pressures)

    # 生成 x 轴坐标，确保起点为整点
    x = [start_time + timedelta(minutes=i) for i in range(sleep_mins)]

    # 绘制曲线图
    plt.figure(figsize=(12, 6))
    plt.plot(x, valid_pressures, marker='o', linestyle='-', color='b', label='Pressure')

    # 设置图形标题和坐标轴标签
    plt.title('Pressure Data')
    plt.xlabel('Time')
    plt.ylabel('Pressure')
    plt.legend()

    # 添加最大值、最小值和中位数标记
    plt.axhline(y=max_pressure, color='r', linestyle='--', label='Max Pressure')
    plt.axhline(y=min_pressure, color='g', linestyle='--', label='Min Pressure')
    plt.axhline(y=median_pressure, color='y', linestyle='--', label='Median Pressure')

    # 设置X轴为时间格式
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))
    plt.gcf().autofmt_xdate()

    # 在图中添加网格线
    plt.grid(True)

    # 显示图形
    plt.show()

    return {
        'sleep_mins': sleep_mins,
        'max_pressure': max_pressure,
        'min_pressure': min_pressure,
        'median_pressure': median_pressure,
        'valid_pressures': valid_pressures
    }

def main():
    """主函数，读取文件、解析数据并进行分析。"""
    # 从文件中读取数据
    file_path = '00100009.bys'
    try:
        hex_data = read_bys_file(file_path)

        # 解析头部信息
        header_info = parse_header(hex_data)
        print(f"开始时间: {header_info['start_time']}")
        print(f"结束时间: {header_info['end_time']}")
        print(f"设备型号: {header_info['device_model']}")

        # 解析数据
        pressure_values = parse_hex_data(hex_data)

        # 可视化数据
        analysis_results = analyze_pressure_data(header_info['start_time'], pressure_values)

        # 输出结果
        print(f"睡眠时长(分钟): {analysis_results['sleep_mins']}")
        print(f"最大工作气压: {analysis_results['max_pressure']}")
        print(f"最小工作气压: {analysis_results['min_pressure']}")
        print(f"送压中间值: {analysis_results['median_pressure']}")
        # 输出前10个有效压力值
        print(f"所有送压值(前10个): {analysis_results['valid_pressures'][:10]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
