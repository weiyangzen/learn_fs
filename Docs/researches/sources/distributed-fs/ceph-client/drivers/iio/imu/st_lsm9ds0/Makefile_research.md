<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Makefile

Purpose: build rules for the ST LSM9DS0 IMU wrapper.

Important entries: `obj-$(CONFIG_IIO_ST_LSM9DS0) += st_lsm9ds0.o`, composite `st_lsm9ds0-y := st_lsm9ds0_core.o`, plus transport objects for I2C and SPI.

Control flow: Kconfig determines whether the core wrapper and bus frontend modules are built.

State and persistence: no runtime state.

Dependencies and integration: bus frontends call the namespace-exported core probe and rely on selected ST sensor common modules.

Risks: minimal; object naming must match module import expectations and Kconfig selections.

Test signals: module link for core, I2C, and SPI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Makefile -->
