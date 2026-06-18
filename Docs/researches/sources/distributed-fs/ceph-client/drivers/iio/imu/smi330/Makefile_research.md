<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Makefile

Purpose: object mapping for the Bosch SMI330 IMU driver.

Important entries: `obj-$(CONFIG_SMI330) += smi330_core.o`, `obj-$(CONFIG_SMI330_I2C) += smi330_i2c.o`, and `obj-$(CONFIG_SMI330_SPI) += smi330_spi.o`.

Control flow: Kconfig selections decide whether the shared core and each transport frontend are built in or as modules.

State and persistence: no runtime state.

Dependencies and integration: pairs with `Kconfig`; bus modules import the `IIO_SMI330` namespace exported by the core.

Risks: if a bus object were built without the core symbol, namespace/probe references would fail; Kconfig selection prevents that.

Test signals: kernel/module build with each SMI330 configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Makefile -->
