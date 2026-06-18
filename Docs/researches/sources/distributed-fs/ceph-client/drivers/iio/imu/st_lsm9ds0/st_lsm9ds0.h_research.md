<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0.h

Purpose: small shared header for ST LSM9DS0 bus wrappers and core.

Important APIs/types: `struct st_lsm9ds0` stores device pointer, resolved chip name, IRQ, child accel/magn IIO devices, and regulator pointers. `st_lsm9ds0_probe()` is declared as the shared core entry point.

Control flow: bus frontends allocate/fill `struct st_lsm9ds0`, initialize bus regmap, and call the shared probe.

State and persistence: runtime wrapper state holds references to the two IIO children and supplies. In the current core, regulators are enabled through bulk devm helpers rather than stored in the struct fields.

Dependencies and integration: forward-declares `device`, `regmap`, `regulator`, and `iio_dev`, keeping transport files decoupled from full headers.

Risks: unused regulator pointer fields may be legacy leftovers; callers must set `dev`, `name`, and `irq` before calling probe.

Test signals: compile coverage and successful use from both I2C and SPI frontends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0.h -->
