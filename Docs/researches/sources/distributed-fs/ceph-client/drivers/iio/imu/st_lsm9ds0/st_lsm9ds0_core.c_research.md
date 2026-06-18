<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_core.c

Purpose: shared wrapper that exposes an LSM9DS0/LSM303D IMU as separate ST common accelerometer and magnetometer IIO devices over one regmap.

Important APIs/functions: `st_lsm9ds0_probe_accel()` finds ST accel settings by name, allocates accel IIO device, fills `struct st_sensor_data`, and calls `st_accel_common_probe()`. `st_lsm9ds0_probe_magn()` does the same with magnetometer settings and `st_magn_common_probe()`. Exported `st_lsm9ds0_probe()` enables regulators then probes both children.

Control flow: bus probe resolves a canonical device name and regmap, then core enables `vdd`/`vddio`, creates the accelerometer child, and creates the magnetometer child. Both children share the same regmap and IRQ.

State and persistence: persistent state is in the wrapper's `accel` and `magn` IIO device pointers and in each child `st_sensor_data`. Regulators are enabled for the device lifetime through devm bulk enable.

Dependencies and integration: depends on `linux/iio/common/st_sensors.h`, `st_accel_get_settings()`, `st_magn_get_settings()`, and the common ST accel/magn probe implementations. Exports namespace `IIO_ST_SENSORS`.

Risks: both child probes depend on the same `name` resolving in both accel and magn settings tables. A magnetometer probe failure after accelerometer probe relies on devm cleanup. Shared regmap access correctness is delegated to common ST sensor code.

Test signals: regulator enable, name resolution for `lsm303d-imu` and `lsm9ds0-imu`, accel and magn IIO registration, shared IRQ behavior, and namespace import from bus modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_core.c -->
