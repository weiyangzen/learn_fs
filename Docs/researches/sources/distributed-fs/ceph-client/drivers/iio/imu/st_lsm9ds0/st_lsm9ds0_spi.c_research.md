<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_spi.c

Purpose: SPI frontend for ST LSM9DS0/LSM303D IMUs.

Important APIs/functions: OF and SPI ID tables cover `lsm303d-imu` and `lsm9ds0-imu`. `st_lsm9ds0_spi_probe()` normalizes `spi->modalias`, allocates wrapper state, initializes SPI regmap with `read_flag_mask = 0xc0`, stores driver data, and calls `st_lsm9ds0_probe()`.

Control flow: SPI probe resolves the common ST sensor name, creates bus regmap, and delegates child accel/magn setup to the core.

State and persistence: frontend stores wrapper state as SPI driver data; core/common sensor code owns the child devices and hardware configuration.

Dependencies and integration: depends on SPI, regmap SPI, `st_sensors_spi.h`, OF/SPI matching, and namespace import `IIO_ST_SENSORS`.

Risks: SPI uses a different read flag mask from I2C; wrong mask breaks register reads. OF match data is name-oriented while probe uses modalias normalization, so modalias/name consistency is important.

Test signals: SPI probe for both IDs, regmap read/write traces, child accel/magn registration, and module alias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_spi.c -->
