# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_ad7417_sensor.c

Purpose: registers Windfarm sensors for AD7417 chips on supported PowerMac7,2, PowerMac7,3, and RackMac3,1 systems. It exposes ambient CPU temperature and ADC-derived diode, voltage, and current readings to Windfarm policy code.

Important APIs and functions: `struct wf_ad7417_priv` holds kref, I2C client, cached config, CPU number, MPU calibration data, five `wf_sensor` objects, and a mutex. `wf_ad7417_temp_get()` reads register 0 and converts 8.8 temperature to 16.16 fixed point. `wf_ad7417_adc_get()` selects ADC channels, waits for conversion, reads register 4, converts raw values via `wf_ad7417_adc_convert()`, and retries I2C failures. `wf_ad7417_add_sensor()` registers each Windfarm sensor and bumps the private kref on success. Probe/remove are I2C callbacks.

Control flow: module init restricts registration to known machines. Probe requires `hwsensor-location`, maps `CPU A`/`CPU B` to CPU number, retrieves MPU calibration with `wf_get_mpu()`, allocates state, initializes the AD7417 config registers, then registers five hard-coded sensor names suffixed by CPU number. Remove clears the client pointer, unregisters sensors, and drops the base kref.

State and persistence: per-chip private state plus registered Windfarm sensor objects. Sensor names are dynamically allocated and freed by release callbacks. Hardware config is cached in `pv->config`.

Dependencies and integration: depends on I2C, OF properties, Windfarm core, `windfarm_mpu.h` calibration data, and PowerMac machine matching.

Risks: endian casts use `be16_to_cpup((__le16 *)buf)`, which is unusual and should be handled carefully if refactored. `pv->i2c` is set to NULL on remove while outstanding sensor references may still exist; read paths assume valid client. Sensor registration failures are tolerated individually, so policy may see partial sensor sets.

Test signals: module loads only on supported machines, CPU A/B location parsing, MPU calibration availability, five sensors per chip with expected names, temperature/ADC fixed-point values, retry behavior on I2C errors, and clean kref/name release after unregister.
