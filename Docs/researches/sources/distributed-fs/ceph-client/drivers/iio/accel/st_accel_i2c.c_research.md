# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_i2c.c

Purpose: I2C transport wrapper for the shared ST accelerometer core.

Important APIs/types/functions: the OF match table maps many `st,*-accel` and compatible strings to canonical device names. The ACPI table handles `SMO8840` and `SMO8A90`. The I2C id table lists supported modalias names. `st_accel_i2c_probe()` normalizes the device name, looks up settings with `st_accel_get_settings()`, allocates the IIO device, stores the settings pointer, calls `st_sensors_i2c_configure()`, enables power, and delegates to `st_accel_common_probe()`.

Control flow: `module_i2c_driver()` registers the wrapper. Probe fails early on unknown names, allocation failure, bus configuration failure, or regulator/power failure. All sensor initialization, IIO registration, buffering, and trigger setup happen in the common core.

State and persistence behavior: the wrapper owns no independent runtime state beyond IIO private `struct st_sensor_data`. Power enable and register programming are delegated to shared ST helpers and the common probe.

Dependencies and integration points: depends on Linux I2C, OF/ACPI modalias matching, `st_sensors_i2c_configure()`, `st_sensors_power_enable()`, and exported common ST accelerometer symbols.

Risks: compatible strings and id-table names must match the header constants and settings table. `st_sensors_dev_name_probe()` mutates `client->name` based on firmware match data, so name length and firmware data correctness affect probe. Adding a new chip requires updates in the settings table, header, and this bus table.

Test signals: compile as module or built-in, instantiate through I2C id, OF, and ACPI paths, verify unknown names return `-ENODEV`, inject I2C configure and power failures, and confirm successful devices get the channel set and sysfs attributes from `st_accel_common_probe()`.
