<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_i2c.c

## Purpose
`st_pressure_i2c.c` is the I2C bus wrapper for STMicroelectronics pressure sensors. It maps firmware/device names to shared settings, configures the generic ST I2C transport, enables power, and delegates to the common pressure core.

## Important APIs, types, and functions
OF match entries map ST compatibles to device-name strings. ACPI match includes `SNO9210` for LPS22HB. I2C IDs map names to `enum st_press_type`. `st_press_i2c_probe()` normalizes the device name, looks up settings with `st_press_get_settings()`, allocates `struct st_sensor_data`, calls `st_sensors_i2c_configure()`, enables power, and calls `st_press_common_probe()`.

## Control flow
The I2C core probes the device, name normalization reconciles firmware IDs, settings lookup selects the chip table, and the wrapper wires the I2C regmap/transfer functions through the ST common layer. The common core handles ID verification and IIO registration.

## State and persistence behavior
Wrapper state is the common `st_sensor_data` allocated as IIO private data. Power enable persists for the device lifetime subject to common ST power handling.

## Dependencies and integration points
It depends on Linux I2C, OF/ACPI/I2C ID matching, `st_sensors_i2c_configure()`, `st_sensors_power_enable()`, and namespace `IIO_ST_SENSORS`.

## Risks
Name normalization and settings lookup must match the core settings table; an unsupported alias fails probe. Power enable happens before WAI verification, so probe failure paths rely on devm/common cleanup. ACPI support is much narrower than OF/I2C tables.

## Test signals
Probe every OF compatible and I2C ID, verify ACPI `SNO9210`, exercise unsupported names, inject I2C configure/power failures, and run common ST raw/buffer tests through I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_i2c.c -->
