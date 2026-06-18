# `sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_i2c.h`

Purpose: I2C transport configuration entry point for ST common IIO sensor drivers.

Important APIs/types/functions: `st_sensors_i2c_configure(struct iio_dev *, struct i2c_client *)`.

Control flow and state: implementation configures the `iio_dev` transport/regmap and device identity for an I2C-backed ST sensor.

Dependencies/integration: depends on I2C and `st_sensors.h`; used by ST accelerometer/gyro/magnetometer/pressure I2C drivers before common probe logic.

Risks: I2C regmap address width, multi-read behavior, and client device data must align with common settings; probe unwind must handle partial configuration.

Test signals: I2C probe/configure for supported chips, register read/write through common debugfs path, multi-byte sample reads, and remove cleanup.
