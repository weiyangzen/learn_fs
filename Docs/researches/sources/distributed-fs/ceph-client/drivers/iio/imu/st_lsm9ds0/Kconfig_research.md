<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Kconfig

Purpose: Kconfig for the ST LSM9DS0/LSM303D IMU wrapper and I2C/SPI bus frontends.

Important symbols: `IIO_ST_LSM9DS0` depends on I2C or SPI master plus SYSFS, excludes legacy `SENSORS_LIS3_*`, and selects shared ST accelerometer and magnetometer 3-axis cores. `IIO_ST_LSM9DS0_I2C` and `_SPI` depend on the bus and core, default with the bus/core, select ST sensor bus helpers and regmap backends.

Control flow: core symbol builds the wrapper that instantiates accel and magn common drivers; frontend symbols build transport-specific regmap/probe code.

State and persistence: no runtime state; it shapes build-time composition.

Dependencies and integration: integrates with the older `st_sensors` accel/magn common framework, SYSFS, regmap, I2C, and SPI.

Risks: mutually excluding LIS3 legacy drivers avoids duplicate ownership. SPI help text says "I2C interface" in the viewed copy, a documentation typo.

Test signals: config/build with I2C-only, SPI-only, both, and conflicts with LIS3 drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Kconfig -->
