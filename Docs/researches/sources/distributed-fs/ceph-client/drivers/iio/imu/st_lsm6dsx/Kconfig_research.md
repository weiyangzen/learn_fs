<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Kconfig

Purpose: Kconfig for the ST LSM6DSx family IMU driver and its I2C, SPI, and I3C frontends.

Important symbols: `IIO_ST_LSM6DSX` is the shared core and depends on at least one of I2C/SPI/I3C, selecting IIO buffer, triggered buffer, and kfifo buffer support. `IIO_ST_LSM6DSX_I2C`, `_SPI`, and `_I3C` depend on the relevant bus and core, default to enabled when bus/core are enabled, and select matching regmap backends.

Control flow: selecting the core builds `st_lsm6dsx.o`; selecting frontends builds bus modules that call the exported core probe.

State and persistence: no runtime state; this controls build-time inclusion for a broad device list.

Dependencies and integration: integrates with IIO, regmap, I2C, SPI master, and I3C subsystem options.

Risks: the core depends on any bus but no frontend is strictly selected by the core; users can select core without an interface if defaults are overridden. The supported device list must stay in sync with match tables and core settings.

Test signals: config/build matrix for I2C, SPI, I3C, all buses, and no frontend; help text device names matching module aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Kconfig -->
