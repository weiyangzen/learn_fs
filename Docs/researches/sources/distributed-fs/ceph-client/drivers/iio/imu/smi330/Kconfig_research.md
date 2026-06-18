<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Kconfig

Purpose: Kconfig entries for the Bosch SMI330 6-axis IMU core and I2C/SPI bus frontends.

Important symbols: hidden `SMI330` selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`; visible `SMI330_I2C` depends on `I2C`, selects `SMI330` and `REGMAP_I2C`; visible `SMI330_SPI` depends on `SPI`, selects `SMI330` and `REGMAP_SPI`.

Control flow: enabling either bus option pulls in the shared core and the relevant regmap backend. Module names in help text are `smi330_i2c` and `smi330_spi`.

State and persistence: no runtime state; this controls build-time object inclusion.

Dependencies and integration: integrates the new SMI330 driver with the IIO and regmap build system.

Risks: the hidden core has no prompt, so it must always be selected by a bus frontend. Missing IRQ dependency is acceptable because the core can operate in polling/direct mode.

Test signals: `allyesconfig`/module builds for I2C-only, SPI-only, both enabled, and both disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Kconfig -->
