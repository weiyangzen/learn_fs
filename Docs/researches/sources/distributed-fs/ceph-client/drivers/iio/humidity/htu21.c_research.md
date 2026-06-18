# sources/distributed-fs/ceph-client/drivers/iio/humidity/htu21.c

Purpose: I2C IIO driver for Measurement Specialties HTU21 humidity/temperature sensors and the humidity function of MS8607. It wraps common measurement-specialties helper routines.

Important APIs/types/functions: Uses `struct ms_ht_dev` from `ms_sensors_i2c.h` as private state. `htu21_read_raw()` returns processed temperature/humidity or current sample frequency. `htu21_write_raw()` maps requested sample frequency to a resolution index and calls `ms_sensors_write_resolution()`. Sysfs helpers expose sampling frequencies, battery-low status, and heater enable through common helper functions. `htu21_probe()` checks SMBus/I2C capabilities, allocates IIO, selects HTU21 two-channel or MS8607 humidity-only channel table, resets the chip, reads serial number, and registers IIO.

Control flow: Direct processed reads call common helpers for temperature/humidity. Sample frequency writes serialize through `dev_data->lock`, update `res_index`, and program resolution. Probe uses I2C id driver data to decide whether to suppress the temperature channel for MS8607.

State and persistence: Private state stores client, resolution index, and mutex. Hardware state includes resolution, heater, and reset defaults managed by common helpers. Serial number is read and logged but not persisted in driver state.

Dependencies and integration points: Depends on I2C, `IIO_MS_SENSORS_I2C`, common helper namespace `IIO_MEAS_SPEC_SENSORS`, OF/I2C ids `meas,htu21` and `meas,ms8607-humidity`.

Risks: OF match entries do not provide driver data, so OF-created MS8607 clients must still map to the correct I2C id data for humidity-only behavior. The sample frequency array is reverse-mapped by exact integer values only. Common helper behavior is a critical dependency not visible in this file.

Test signals: Probe HTU21 and MS8607 ids, verify channel set selection, processed temp/humidity reads, sample frequency writes/readback, heater and battery sysfs, reset/serial failure paths, and adapter capability rejection.
