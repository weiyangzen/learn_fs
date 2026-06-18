
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_dev.c

## Purpose
`ssp_dev.c` is the Samsung SSP sensorhub SPI parent driver. It owns device-tree parsing, MFD child creation for SSP IIO consumers, MCU reset/firmware revision checks, MCU initialization, watchdog recovery, suspend/resume, and the exported sensor lifecycle APIs used by child accelerometer/gyroscope style drivers.

## Important APIs, types, and functions
- `struct ssp_instruction` is the packed payload used for sensor add/change-delay instructions: delay, batch latency, and batch option.
- `ssp_rinato_info` and `ssp_thermostat_info` bind compatible strings to firmware names, expected firmware revisions, and the magnetic calibration table.
- `sensorhub_sensor_devs` creates `ssp-accelerometer` and `ssp-gyroscope` MFD children.
- Exported `ssp_get_sensor_delay()`, `ssp_enable_sensor()`, `ssp_change_delay()`, `ssp_disable_sensor()`, and `ssp_register_consumer()` are the main child-driver interface under namespace `IIO_SSP_SENSORS`.
- `ssp_probe()` wires the SPI mode, locks, pending list, watchdog work/timer, threaded IRQ, firmware validation, and MCU initialization.
- `ssp_suspend()` and `ssp_resume()` notify the MCU about AP state and manage IRQ/watchdog state.
- `ssp_initialize_mcu()` verifies chip ID, pushes the magnetic matrix, reads available sensors and firmware revision, then asks the MCU to check dump state.

## Control flow
Probe parses GPIOs and matched sensorhub info, adds MFD children, configures SPI mode 1, initializes per-sensor delay/batch/status arrays, requests a falling-edge threaded IRQ, enables IRQ wake, checks firmware revision, and initializes the MCU. Sensor enable builds an `ssp_instruction` and either sends an add instruction, changes delay for a running sensor, or moves unknown states back to add state. Disable sends a remove instruction, clears `sensor_enable`, resets check state, and may stop the watchdog when the atomic enable refcount reaches zero. Watchdog timer periodically queues reset work if timeout or communication-failure counters exceed thresholds. Refresh work reinitializes the MCU after reset requests and then resynchronizes enabled sensors and last AP/resume state.

## State and persistence behavior
All state is in-memory in `struct ssp_data`: GPIO descriptors, SPI pointer, firmware download state, current firmware revision, available and enabled sensor bitmasks, per-sensor delay/batch/status arrays, sensor IIO device pointers, pending transport list, counters, watchdog timer/work, and last AP/resume state. No durable persistence is written; the driver relies on firmware files and DT properties as external configuration. `enable_refcount` controls watchdog lifetime across enabled sensors, and `check_status[]` tracks the MCU-side lifecycle of each sensor.

## Dependencies and integration points
This file integrates with Linux SPI, GPIO descriptor, IRQ, timer/workqueue, MFD, IIO, module OF matching, and PM frameworks. It depends on `ssp.h` for command constants, sensor types, `struct ssp_data`, and transport helpers implemented in `ssp_spi.c`. Child IIO devices call exported SSP APIs and register themselves through `ssp_register_consumer()`. Firmware identity is checked against `struct ssp_sensorhub_info` selected by `samsung,sensorhub-rinato` or `samsung,sensorhub-thermostat`.

## Risks and edge cases
- `ssp_enable_sensor()` increments `enable_refcount` on every call, including delay changes for already-running sensors; repeated enable/change paths must be balanced by disables or the watchdog can remain active.
- `ssp_disable_sensor()` decrements `enable_refcount` even if the sensor was not enabled, so unexpected child disable calls can underflow the logical count and disrupt watchdog state.
- Firmware mismatch currently fails probe with `-EPERM`; no download path is implemented here despite state names suggesting one.
- Refresh work resynchronizes all bits in `available_sensors`, which appears to mean physically available sensors rather than currently enabled sensors; this can enable more sensors than userspace requested if used as written.
- IRQ wake is enabled during probe and disabled in `ssp_enable_mcu(false)`/remove paths; IRQ wake balance and suspend failures need hardware testing.

## Test signals
Useful signals are successful probe logs for firmware revision and MCU ID, populated MFD children, IIO child registration through `ssp_register_consumer()`, successful enable/change/disable commands, IRQ packet delivery without timeout counter growth, watchdog reset behavior under forced communication failures, and suspend/resume AP-status commands with no unbalanced IRQ warnings.
