# sources/distributed-fs/ceph-client/drivers/iio/temperature/tsys02d.c

Purpose: IIO direct-mode driver for Measurement Specialties TSYS02D temperature sensors. It exposes processed temperature, sampling-frequency/resolution control, and a battery-low sysfs attribute.

Important APIs/types/functions: Uses common `struct ms_ht_dev` from Measurement Specialties helpers. Main functions are `tsys02d_read_raw()`, `tsys02d_write_raw()`, `tsys02_read_battery_low()`, and `tsys02d_probe()`.

Control flow: probe checks I2C capabilities, allocates IIO device/private state, initializes resolution index and mutex, resets the sensor, reads and logs serial number, and registers a single temperature channel. Processed temperature reads delegate to `ms_sensors_ht_read_temperature()`. Sampling-frequency writes map 20/40/70/140 Hz-style values to resolution index and call `ms_sensors_write_resolution()` under mutex.

State and persistence: `res_index` tracks current resolution/sampling setting in RAM and hardware. Serial number is read once for logging. No persistent driver storage exists.

Dependencies/integration: depends on Measurement Specialties I2C helpers, IIO sysfs attributes, and namespace `IIO_MEAS_SPEC_SENSORS`. Device IDs match `tsys02d`.

Risks: sampling-frequency labels are tightly coupled to helper resolution indexes; changing one without the other breaks user ABI. The driver has no OF table here. Battery-low output fully depends on helper semantics.

Test signals: probe/reset/read-serial success, processed temperature reads, valid/invalid sampling-frequency writes, `sampling_frequency_available`, and `battery_low` sysfs output.
