# sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp40.c

Purpose: I2C IIO driver for the Sensirion SGP40 gas sensor. It exposes raw resistance, output temperature and humidity compensation inputs, a resistance calibration bias, and a computed VOC index using integer math.

Important APIs, types, and functions: `struct sgp40_data` stores client, device, relative humidity, temperature, resistance calibration bias, and mutex. `sgp40_measure_resistance_raw()` converts stored humidity and temperature into sensor ticks, adds CRC8 for each word, sends command 0x260f, waits 30 ms, receives resistance ticks, and validates CRC. `sgp40_exp()` approximates exponentials in fixed point; `sgp40_calc_voc()` applies the documented logistic VOC-index estimate around `res_calibbias`. `sgp40_read_raw()` handles raw resistance/temp/humidity, processed VOC, and calibration bias. `sgp40_write_raw()` validates and updates temp, humidity, and bias. `sgp40_probe()` sets defaults of 50 percent RH, 25 C, and bias 30000, then registers the IIO device.

Control flow: every raw resistance or processed VOC read performs a live measurement. Compensation and bias reads/writes operate on driver state under the mutex. Processed VOC reads measure resistance first, then compute a fixed-point VOC result returned as integer plus micro.

State and persistence: temperature, humidity, and calibration bias are volatile driver state; they reset to defaults at probe and are not written to hardware. The sensor measurement itself is stateless apart from command timing.

Dependencies and integration: depends on I2C, CRC8 polynomial 0x31/init 0xff, mutex, IIO direct mode, and OF/I2C ids `sensirion,sgp40` / `sgp40`.

Risks and test signals: fixed-point exponential overflow control and VOC scaling are subtle. Tests should cover compensation bounds, bias bounds, CRC mismatch, send/receive short transfers, default compensation tick conversion, VOC monotonicity around the bias point, and concurrent writes during measurement.
