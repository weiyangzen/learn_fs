## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Kconfig

Purpose: Kconfig entries for the InvenSense ICM-426xx common core and I2C/SPI bus drivers.

Important APIs, types, and functions: hidden `INV_ICM42600` selects `IIO_BUFFER` and `IIO_INV_SENSORS_TIMESTAMP`. `INV_ICM42600_I2C` depends on I2C, selects common core and `REGMAP_I2C`, and builds `inv-icm42600-i2c`. `INV_ICM42600_SPI` depends on `SPI_MASTER`, selects common core and `REGMAP_SPI`, and builds `inv-icm42600-spi`.

Control flow: bus-specific selections pull in the shared multi-object ICM42600 driver and required timestamp/buffer infrastructure.

State and persistence behavior: no runtime state; controls build dependencies.

Dependencies and integration points: integrates the driver with IIO buffering and the shared InvenSense timestamp helper.

Risks and edge cases: because the common symbol is hidden, it is only built when a bus transport is selected. Missing timestamp helper support would break the common buffer path.

Test signals: build I2C-only, SPI-only, both, modules, built-ins, and dependency-disabled configs.
