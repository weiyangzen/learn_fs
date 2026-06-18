# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_i2c.c

## Purpose
I2C transport glue for the common ST magnetometer driver.

## Important APIs, Types, And Functions
`st_magn_of_match[]` maps ST magnetometer compatibles to names used by common settings. `st_magn_i2c_probe()` normalizes the I2C device name, looks up settings with `st_magn_get_settings()`, allocates `struct st_sensor_data`, configures I2C transport with `st_sensors_i2c_configure()`, enables power, and calls `st_magn_common_probe()`. `st_magn_id_table[]` provides legacy I2C modalias matching.

## Control Flow
Device bind enters the probe, validates that the name is recognized by the common settings table, configures common ST I2C access, enables regulators/power through ST helpers, then delegates all sensor setup to the common core.

## State And Persistence
No independent state beyond the allocated IIO private data. Persistent device identity is from OF/I2C tables; runtime sensor state is held by the common core.

## Dependencies And Integration Points
Uses `st_sensors_i2c_configure()`, `st_sensors_power_enable()`, and namespace `IIO_ST_SENSORS`. It is the bus endpoint for `st_magn_core.c`.

## Risks And Test Signals
Name-table mismatches cause `-ENODEV`. Test OF compatibles and I2C IDs for every name in the table, probe failure on unknown names, and power-enable error handling.
