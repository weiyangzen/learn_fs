<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i2c.c

Purpose: I2C frontend for the ST LSM6DSx family. It matches many OF/ACPI/I2C IDs, creates an 8-bit regmap, resolves hardware ID, and calls the shared core probe.

Important APIs/functions: `st_lsm6dsx_i2c_probe()` obtains match data or I2C ID driver data, initializes `devm_regmap_init_i2c()`, and calls `st_lsm6dsx_probe()`. Match tables enumerate all supported names and ACPI IDs `SMO8B30` and `SMOCF00`.

Control flow: device-tree match data takes precedence; fallback is the I2C device ID table. A missing hardware ID fails with `-EINVAL`. Successful regmap creation delegates IRQ, ID, and regmap to the core.

State and persistence: no transport-private state; core stores driver data on the device.

Dependencies and integration: depends on I2C, regmap I2C, OF/ACPI modalias matching, PM ops from the core, and namespace import `IIO_LSM6DSX`.

Risks: if neither firmware match data nor I2C ID data is present, probe fails. The long device table must remain synchronized with core settings and Kconfig help text.

Test signals: I2C probe for each compatible/name, ACPI matches, regmap initialization failure handling, IRQ forwarding, PM suspend/resume through imported PM ops, and module alias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i2c.c -->
