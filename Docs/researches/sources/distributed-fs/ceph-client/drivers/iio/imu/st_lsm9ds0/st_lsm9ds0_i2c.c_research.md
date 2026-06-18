<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_i2c.c

Purpose: I2C frontend for ST LSM9DS0/LSM303D IMUs.

Important APIs/functions: OF table maps `st,lsm303d-imu` and `st,lsm9ds0-imu` to common ST sensor names; ACPI table maps `ACCL0001`; `st_lsm9ds0_i2c_probe()` normalizes the device name with `st_sensors_dev_name_probe()`, allocates wrapper state, initializes an 8-bit regmap with `read_flag_mask = 0x80`, stores client data, and calls `st_lsm9ds0_probe()`.

Control flow: I2C probe prepares the shared wrapper and regmap, then core creates accel and magnetometer IIO children.

State and persistence: frontend stores `struct st_lsm9ds0` as I2C client data; runtime child state is owned by the core/common ST sensors.

Dependencies and integration: depends on I2C, regmap I2C, `st_sensors_i2c.h`, OF/ACPI/I2C matching, and namespace import `IIO_ST_SENSORS`.

Risks: correct name normalization is required before common settings lookup. Regmap read flag must match the chip protocol. No PM ops are defined in this wrapper; power handling is through devm regulator enable and common child drivers.

Test signals: I2C and ACPI probe, device-name normalization, regmap reads, accel/magn child registration, and module alias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_i2c.c -->
