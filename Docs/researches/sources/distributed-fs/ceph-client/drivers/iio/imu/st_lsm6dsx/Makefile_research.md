<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Makefile

Purpose: build rules for the ST LSM6DSx family.

Important entries: composite `st_lsm6dsx-y` contains `st_lsm6dsx_core.o`, `st_lsm6dsx_buffer.o`, and `st_lsm6dsx_shub.o`. Bus objects are `st_lsm6dsx_i2c.o`, `st_lsm6dsx_spi.o`, and `st_lsm6dsx_i3c.o`.

Control flow: `CONFIG_IIO_ST_LSM6DSX` builds the shared composite object; bus Kconfig symbols build transport modules separately.

State and persistence: no runtime state.

Dependencies and integration: aligns exported namespace `IIO_LSM6DSX` from the core with module imports in bus frontends.

Risks: core, FIFO, and sensor-hub code are always linked together; Kconfig must keep required buffer dependencies selected.

Test signals: module link for core plus each transport and namespace import/export resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Makefile -->
