# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.c

Purpose: shared I2C helper implementation for Measurement Specialties humidity/temperature and temperature/pressure sensors. It centralizes reset, PROM reads, ADC conversion reads, serial-number assembly, CRC checks, resolution/heater/battery sysfs helpers, humidity/temperature formulas, PROM CRC, and compensated pressure calculation.

Important APIs, types, and functions: exported helpers include `ms_sensors_reset()`, `ms_sensors_read_prom_word()`, `ms_sensors_convert_and_read()`, `ms_sensors_read_serial()`, `ms_sensors_write_resolution()`, `ms_sensors_show_battery_low()`, `ms_sensors_show_heater()`, `ms_sensors_write_heater()`, `ms_sensors_ht_read_temperature()`, `ms_sensors_ht_read_humidity()`, `ms_sensors_tp_read_prom()`, and `ms_sensors_read_temp_and_pressure()`. Internal CRC helpers validate HT/serial bytes and 112/128-bit PROM coefficient sets.

Control flow: concrete drivers pass their `ms_ht_dev` or `ms_tp_dev`. Conversion helpers send a command, sleep the resolution-specific conversion time, then read ADC bytes. HT functions lock around conversions, validate CRC, and apply datasheet formulas. TP functions read T and P ADCs, then apply first and second order compensation using PROM coefficients.

State and persistence: mutable state is in caller-owned structs: I2C client, mutex, resolution index, hardware PROM length/max resolution, and PROM coefficient cache. Resolution/heater bits are stored in sensor config registers.

Dependencies and integration: depends on I2C SMBus/master receive, IIO/sysfs conventions, delays, mutexes, and `ms_sensors_i2c.h`. Exports namespace `IIO_MEAS_SPEC_SENSORS`.

Risks and test signals: CRC algorithms and fixed-point compensation formulas are critical. Header declares `ms_sensors_show_serial()` but this file does not define it, so users must not expect it from this object. Tests should cover serial CRC/assembly, PROM CRC variants, conversion timeout/error paths, resolution bit encoding, heater validation, humidity clamp, low-temperature second-order compensation, and endian handling of ADC/PROM values.
