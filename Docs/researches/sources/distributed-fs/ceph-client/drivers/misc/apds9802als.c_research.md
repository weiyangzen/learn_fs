# sources/distributed-fs/ceph-client/drivers/misc/apds9802als.c

Purpose: implements a simple I2C sysfs driver for the Avago APDS9802 ambient light sensor.

Important APIs and functions: probe/remove are `apds9802als_probe` and `apds9802als_remove`. Sysfs attributes under group `apds9802als` are `lux0_sensor_range` and `lux0_input`. Runtime/system PM uses `apds9802als_suspend` and `apds9802als_resume`. Helpers include `als_wait_for_data_ready`, `als_set_default_config`, and `als_set_power_state`.

Control flow: probe allocates `struct als_data`, stores it as I2C client data, creates the sysfs group, writes default power/range/manual-measurement configuration, initializes the mutex, and enables runtime PM. Reading `lux0_input` runtime-resumes the device, locks the mutex, clears EOC status, starts a measurement, waits up to ten 30 ms retries for data-ready, reads LSB/MSB result bytes, unlocks, and runtime-suspends. Range writes parse lux range and adjust register 0x81 bits under the same mutex.

State and persistence: software state is only a mutex. Sensor configuration persists in device registers while powered. No cached lux value is kept.

Dependencies and integration points: depends on I2C SMBus byte operations, sysfs, mutex, sleep, and runtime PM. It registers through `module_i2c_driver` with id `apds9802als`.

Risks: probe calls `als_set_default_config` before `mutex_init`, but that helper path itself does not take the mutex. `pm_runtime_get_sync` return values are ignored. I2C write failures during measurement setup are mostly unchecked. The module author string is missing a closing angle bracket.

Test signals: sysfs range/read tests, data-ready timeout path, suspend/resume and runtime PM cycles, I2C fault injection, and validation of first-measurement discard behavior after power-on.
