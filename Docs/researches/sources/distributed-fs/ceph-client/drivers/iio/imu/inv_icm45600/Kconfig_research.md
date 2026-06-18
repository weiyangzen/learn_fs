# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Kconfig

Purpose: defines kernel configuration symbols for the ICM45600 driver family and its I2C, SPI, and I3C transports.

Important entries: hidden `INV_ICM45600` selects `IIO_BUFFER`, `IIO_KFIFO_BUF`, and `IIO_INV_SENSORS_TIMESTAMP`. `INV_ICM45600_I2C`, `INV_ICM45600_SPI`, and `INV_ICM45600_I3C` are tristate user-visible transport options with bus dependencies and regmap selections. Help text lists supported ICM-45605/606/608/634/686/687/688-P/689 devices and module names.

Control flow and state: this is build-time configuration only. Selecting any transport pulls in the shared core object through `INV_ICM45600`.

Dependencies and integration: integrates with the IIO subsystem, regmap backends, and bus cores. It is paired with the local Makefile that builds the shared object plus transport modules.

Risks and tests: dependency mistakes cause link failures or unusable modules. Test signals include Kconfig visibility under relevant bus configs, all selected transports linking with `inv-icm45600.o`, module autoload metadata, and build coverage for I2C/SPI/I3C combinations.
