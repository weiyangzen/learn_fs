# Research: subset-b-003825

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gigabyte_waterforce.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/gigabyte_waterforce.c

## Purpose
`gigabyte_waterforce.c` is a HID-backed hwmon driver for Gigabyte AORUS Waterforce X240/X280/X360 USB AIO coolers. It exposes coolant temperature, fan RPM, pump RPM, and read-only PWM duty values through the hwmon class, while leaving HIDRAW enabled so existing user-space tools can still communicate with the device.

## Important APIs, Types, and Functions
The central state is `struct waterforce_data`, which stores the `hid_device`, hwmon/debugfs handles, completions for status and firmware replies, cached sensor values, a shared report buffer, and the `updated` jiffies timestamp. The hwmon surface is described by `waterforce_chip_info`, `waterforce_info`, and `waterforce_hwmon_ops`. `waterforce_is_visible()` exposes only read-only temp, fan, PWM, and label attributes. `waterforce_read()` and `waterforce_read_string()` serve hwmon reads. `waterforce_raw_event()` parses incoming HID reports. `waterforce_write_expanded()` sends zero-padded output reports, while `waterforce_get_status()` and `waterforce_get_fw_ver()` issue commands and wait for completions. `waterforce_debugfs_init()` adds a firmware-version debugfs file when a version was retrieved.

## Control Flow
Probe allocates state, parses and starts HID with `HID_CONNECT_HIDRAW`, opens the device, allocates the maximum-size report buffer, initializes locks and completions, starts I/O, optionally requests firmware version, registers the hwmon device, then creates debugfs. A hwmon read calls `waterforce_get_status()`, which serializes requesters, reuses cached data for two seconds, otherwise reinitializes the status completion under a spinlock, sends `{0x99, 0xDA}`, and waits for `waterforce_raw_event()` to complete it. Raw HID events distinguish firmware reports from status reports by the first two bytes, update cached fields from fixed offsets, complete waiters, and refresh `updated`.

## State and Persistence
State is entirely in-memory and device-local. Sensor readings persist only as cached values until the next successful status report. `firmware_version` is retained for the device lifetime and exposed through debugfs. No nonvolatile device programming is performed.

## Dependencies and Integration Points
The driver integrates with HID, hwmon, debugfs, completions, mutexes, spinlocks, jiffies, and unaligned little-endian helpers. It binds one USB VID/PID pair through `hid_device_id`, uses late init when built in, and manually unregisters hwmon/debugfs/HID resources on remove.

## Risks
The parser trusts report size enough to index fixed offsets; malformed short reports would be dangerous if HID core delivered them. Status requests rely on completion ordering between hwmon readers and hidraw-originated reports, hence the explicit spinlock/reinit sequence. The large 6144-byte report buffer and full-size output report are protocol assumptions. Reads can block for up to two seconds and return timeout errors if firmware does not answer.

## Test Signals
Useful tests are device binding by VID/PID, `sensors` output for temp/fan/pwm attributes, repeated concurrent sysfs reads verifying cache reuse and no stalled completions, debugfs firmware version visibility, timeout behavior with device disconnects, and continued hidraw access by vendor utilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gigabyte_waterforce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gl518sm.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/gl518sm.c

## Purpose
`gl518sm.c` supports the Genesys Logic GL518SM hardware monitor over SMBus/I2C. It exposes voltage limits and inputs, fan tachometers and divisors, temperature limits, alarms, and beep controls through legacy sysfs attribute groups.

## Important APIs, Types, and Functions
`struct gl518_data` holds the I2C client, chip revision, attribute groups, update mutex, cache validity timestamp, register mirrors for voltages/fans/temp/alarms/beeps, and an `alarm_mask`. `gl518_read_value()` and `gl518_write_value()` hide the chip's mixed byte/word register format and swapped word convention. `gl518_update_device()` is the cache refresh routine. Macro-generated `show()` and `set()` handlers implement most sysfs files; hand-written handlers cover fan RPM/divisor behavior and per-bit alarms/beeps. `gl518_detect()`, `gl518_init_client()`, and `gl518_probe()` implement I2C autodetection, chip startup, and hwmon registration.

## Control Flow
The I2C core scans addresses `0x2c` and `0x2d`, requiring SMBus byte and word operations. Detection checks chip ID, config reset bit, and revision (`0x00` or `0x80`). Probe allocates state, records revision as `gl518sm_r00` or `gl518sm_r80`, initializes the chip, chooses base attributes plus extra voltage-input attributes for revision `0x80`, and registers with `devm_hwmon_device_register_with_groups()`. Reads call `gl518_update_device()`, which refreshes the cache at most every 1.5 seconds. Stores convert user values to register encodings, update the cached field, and write hardware under `update_lock`.

## State and Persistence
The driver caches register values in RAM; hardware threshold, fan divisor, fan auto, beep, and mask writes persist in the chip until changed or reset. Revision `0x00` cannot read some voltage inputs, so those sysfs input attributes are intentionally omitted. Fan minimum writes also mutate `alarm_mask` so disabled fan alarms stop contributing to alarm/beep reporting.

## Dependencies and Integration Points
It uses the I2C hwmon class scanning path (`I2C_CLASS_HWMON`), `hwmon-sysfs` sensor attributes, standard mutex/jiffies cache patterns, and the hwmon core group registration API. User space sees conventional lm-sensors style attributes rather than modern `hwmon_chip_info`.

## Risks
Read and write helpers do not uniformly handle negative SMBus errors in cache population, so bus faults can be reflected as bogus cached byte values. Several read-modify-write paths can overwrite concurrent hardware changes outside this driver. The chip's old revision limitations mean missing input attributes are expected and should not be treated as probe failure. Fan divisor changes do not rescale minimum registers automatically.

## Test Signals
Test by SMBus detection on valid and invalid addresses, sysfs mode/attribute presence by revision, voltage/temp/fan conversions at clamp edges, fan minimum zero masking alarm bits, invalid fan divisors returning `-EINVAL`, and cache refresh cadence around the 1.5 second window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gl518sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gl520sm.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/gl520sm.c

## Purpose
`gl520sm.c` drives the Genesys Logic GL520SM monitor. It exports VDD/VIN voltages, two fan tachometers, temperature channels, alarms, beep controls, and CPU VID. One physical input can be configured as either a second temperature channel or a fifth voltage input.

## Important APIs, Types, and Functions
`struct gl520_data` stores I2C state, dynamic attribute groups, cached register values, `vrm`, `alarm_mask`, and `two_temps`. `gl520_read_value()` and `gl520_write_value()` wrap byte versus swapped-word SMBus access. `gl520_update_device()` refreshes cached sensor values every two seconds. `cpu0_vid_show()` uses `vid_from_reg()` and `vid_which_vrm()` from `hwmon-vid`. Sysfs handlers implement voltage, fan, temperature, alarm, beep, and `fan1_off` files. `extra_sensor_type` is a module parameter controlling autodetect versus forced temp/voltage for the shared input.

## Control Flow
Detection scans `0x2c` and `0x2d`, checks SMBus capabilities, chip ID `0x20`, revision masked to zero, and a clear reset bit. Probe allocates state, sets client data, and calls `gl520_init_client()`. Initialization chooses VRM, applies `extra_sensor_type` by modifying config bit `0x10`, enables monitoring, calls the update routine once, masks fan alarms whose minimum is zero, and writes a sanitized beep mask. Probe then registers the common sysfs group plus either `gl520_group_temp2` or `gl520_group_in4`.

## State and Persistence
The cache is RAM-only and marked valid after refresh. User writes change hardware threshold registers, fan divisors, fan-off state, beep enable, and beep masks. The shared input mode can be changed at module load and persists as a config register bit. `alarm_mask` is local policy derived partly from fan minimum registers.

## Dependencies and Integration Points
The driver uses I2C class probing, SMBus byte/word operations, hwmon sysfs helpers, and `hwmon-vid` for CPU VID presentation. It registers through `devm_hwmon_device_register_with_groups()` rather than the newer callback-based hwmon API.

## Risks
The extra sensor mode is a global module parameter, so a forced choice affects all matching devices. Cache updates do not robustly propagate SMBus read errors. The same alarm/beep bit is used for `temp2` or `in4`, making attribute selection and masks dependent on mode. Read-modify-write register operations can race with firmware or other masters on the bus.

## Test Signals
Verify autodetect and forced extra sensor modes, correct sysfs group selection, voltage/temp/fan conversion and clamping, VID output across VRM values, invalid fan divisor rejection, fan minimum zero alarm masking, and stable behavior when a bus read/write returns an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gl520sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gpd-fan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/gpd-fan.c

## Purpose
`gpd-fan.c` provides hwmon fan RPM and PWM control for selected GPD handheld and mini-PC systems whose embedded controller exposes fan registers through legacy I/O ports. It maps a normalized `pwm1` range of `0..255` onto board-specific EC ranges and supports automatic/manual/disabled modes.

## Important APIs, Types, and Functions
`struct gpd_fan_drvdata` describes a board: module name, board enum, address/data ports, EC offsets, and max PWM. Global `gpd_driver_priv` stores current PWM mode/value and matched board data. The DMI table maps product names to board data, while `gpd_fan_board` allows module-param override. `gpd_ecram_read()` and `gpd_ecram_write()` perform raw EC port I/O. Board-specific helpers implement RPM reads, PWM scaling, dual-register Duo writes, Win Max 2 control-enable behavior, and Win 4 EC initialization. `gpd_fan_hwmon_read()` and `gpd_fan_hwmon_write()` are the hwmon callbacks.

## Control Flow
Module init first matches the override string, then DMI. If matched, it initializes global state to automatic mode and creates a bundled platform device with an I/O resource covering the address/data ports. Probe requests that region, registers the hwmon device with one fan and one PWM channel, and runs board-specific EC initialization. Hwmon reads dispatch by sensor type: RPM reads board EC offsets, `pwm1_enable` returns cached mode, and `pwm1` either returns cached/manual values or reads hardware depending on board. Writes validate ranges, update global state, and then program EC registers when mode permits.

## State and Persistence
Driver state is module-global, assuming only one supported GPD fan controller. PWM mode/value are cached in RAM. Hardware EC writes persist until firmware, reboot, or driver removal changes them. Remove forces automatic mode before unregistering.

## Dependencies and Integration Points
The driver depends on DMI matching, raw x86 I/O port access, platform resources, and the hwmon callback API. It has no ACPI/WMI abstraction; all board knowledge is encoded in local tables and EC offsets.

## Risks
Global state would not support multiple devices. Raw EC I/O is board-sensitive; a wrong DMI match or module override can write unintended EC offsets. There is no mutex around global state or EC access, so concurrent sysfs reads/writes can interleave. Some automatic-mode `pwm1` reads return `-EOPNOTSUPP` by design. Switching to manual sets cached PWM to full speed for safety, which can surprise tests expecting preservation.

## Test Signals
Test DMI and override matching, request-region failure, PWM mode transitions, invalid range handling, board-specific scaling, removal restoring automatic mode, concurrent sysfs access, and Win 4 initialization only on the intended board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gpd-fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gpio-fan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/gpio-fan.c

## Purpose
`gpio-fan.c` drives fans controlled by discrete GPIO lines, optionally with an alarm GPIO, regulator supply, runtime power management, and thermal cooling-device integration. It translates a device-tree speed map into hwmon PWM and fan RPM attributes.

## Important APIs, Types, and Functions
`struct gpio_fan_data` stores device handles, hwmon and thermal devices, GPIO descriptors, speed table, current/resume speed indices, manual-control flag, alarm work, and regulator. Alarm handling uses `fan_alarm_irq_handler()` and `fan_alarm_notify()`. GPIO control is centered on `__set_fan_ctrl()`, `__get_fan_ctrl()`, `set_fan_speed()`, `get_fan_speed_index()`, and `rpm_to_speed_index()`. Sysfs handlers expose `pwm1`, `pwm1_enable`, `pwm1_mode`, `fan1_input`, `fan1_target`, min/max RPM, and optional `fan1_alarm`. Thermal callbacks map cooling states to speed indices.

## Control Flow
Probe allocates state, parses device-tree properties and GPIOs, initializes the mutex, gets the `fan` regulator, configures control GPIOs while preserving current values, registers a cleanup action that stops the fan and disables runtime PM, registers the hwmon device, configures optional alarm IRQs, enables runtime PM, marks an active initial speed as resumed, and registers an OF cooling device. Sysfs or thermal writes lock the device and call `set_fan_speed()`, which handles runtime PM transitions when moving between speed index zero and nonzero.

## State and Persistence
The active speed index, resume speed, and manual PWM enable are in memory. The physical GPIO outputs and regulator state persist while powered. Suspend stores the current speed, stops the fan, and resume restores it. Shutdown and devm cleanup drive the fan to speed index zero when control GPIOs exist.

## Dependencies and Integration Points
The driver depends on OF properties (`gpio-fan,speed-map`), GPIO descriptors, optional alarm IRQs, regulator framework, runtime PM, hwmon group registration, and thermal cooling registration.

## Risks
Speed-map ordering is assumed when mapping PWM/RPM to indices. `fan_alarm_irq_handler()` returns `IRQ_NONE` even after scheduling work, which is unusual for a handled interrupt. Runtime PM and regulator failures can leave `speed_index` out of sync with actual hardware in some error paths. Alarm-only configurations register only alarm attributes. `gpio_fan_shutdown()` calls `set_fan_speed()` without taking the mutex.

## Test Signals
Test DT parsing with missing/odd speed maps, GPIO preservation during init, sysfs visibility for alarm-only and control configurations, PWM and target RPM conversions, regulator enable/disable on zero/nonzero transitions, thermal state mapping, suspend/resume restoration, and alarm IRQ sysfs notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gpio-fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gsc-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/gsc-hwmon.c

## Purpose
`gsc-hwmon.c` exposes Gateworks System Controller ADC, temperature, voltage, and fan channels as hwmon inputs. It can consume platform data or derive channel definitions from device tree, and optionally exposes automatic fan-control point attributes.

## Important APIs, Types, and Functions
`struct gsc_hwmon_data` owns the GSC parent pointer, platform data, regmap, per-type channel arrays, dynamic config arrays, `hwmon_channel_info` objects, and `hwmon_chip_info`. `gsc_hwmon_regmap_bus` adapts `gsc_read()`/`gsc_write()` to regmap. `gsc_hwmon_read()` converts channel register bytes according to `mode_temperature`, `mode_voltage_raw`, `mode_voltage_16bit`, `mode_voltage_24bit`, or `mode_fan`. `gsc_hwmon_read_string()` returns labels. `gsc_hwmon_get_devtree_pdata()` builds platform data from child nodes. Extra sysfs handlers expose six fan auto point temperatures and fixed PWM percentages.

## Control Flow
Probe gets parent `gsc_dev`, loads platform data or parses firmware child nodes, allocates state, initializes an 8-bit regmap on `gsc->i2c_hwmon`, partitions channels by mode into temp/in/fan arrays, builds config arrays with input and label bits, optionally attaches the fan auto-point attribute group if a fan base was found, then registers a callback-based hwmon device. Reads select the channel by type and index, bulk-read two or three bytes, combine little-endian-style by shifting each byte to its offset, and scale the result.

## State and Persistence
The driver keeps only static channel metadata and no measurement cache. Fan auto point writes persist in the controller registers. Device-tree voltage offsets are converted from microvolts to millivolts during parsing and stored in platform data.

## Dependencies and Integration Points
It integrates with the Gateworks MFD core, regmap, OF child nodes, platform data (`linux/platform_data/gsc_hwmon.h`), hwmon callback registration, and optional extra sysfs groups.

## Risks
The byte-combination loop depends on controller byte ordering and should be tested against real hardware. Temperature sign conversion uses `tmp > 0x8000` and subtracts `0xffff`, which is sensitive around the sign boundary. Auto-point sysfs appears whenever `fan_base` is set, independent of whether a fan channel exists. Invalid or excessive DT channels fail probe.

## Test Signals
Test DT parsing for labels, registers, modes, voltage dividers/offsets, per-type channel limits, raw scaling math, 16/24-bit voltage reads, fan RPM conversion, fan auto-point read/write clamping, and probe failure on invalid mode or missing child properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gsc-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gxp-fan-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/gxp-fan-ctrl.c

## Purpose
`gxp-fan-ctrl.c` is a platform hwmon driver for HPE GXP fan controllers. It exposes eight fan fault/enable channels and eight writable PWM channels backed by memory-mapped controller registers.

## Important APIs, Types, and Functions
`struct gxp_fan_ctrl_drvdata` stores three MMIO bases: PWM base, platform register block (`plreg`), and function/status block (`fn2`). `fan_installed()`, `fan_failed()`, and `fan_enabled()` derive fan status from install/fail bits and the platform power bit. `gxp_pwm_read()` and `gxp_pwm_write()` implement PWM access. `gxp_fan_ctrl_read()`, `gxp_fan_ctrl_write()`, and `gxp_fan_ctrl_is_visible()` form the hwmon ops. `gxp_fan_ctrl_info` declares fixed fan and PWM channel counts.

## Control Flow
Probe allocates state, maps the unnamed base resource plus named `pl` and `fn2` resources, and registers `hpe_gxp_fan_ctrl` with `devm_hwmon_device_register_with_info()`. Reads of fan attributes consult installation/failure bits. Reads of PWM first check the power status register; when the platform power bit is clear, PWM reports zero to avoid stale/invalid hardware values. Writes validate `0..255` and write one byte at `base + channel`.

## State and Persistence
There is no software cache. PWM writes directly modify controller registers and persist according to hardware behavior. Fan enable/fault state is always read live from MMIO.

## Dependencies and Integration Points
The driver depends on platform resources described by device tree compatible `hpe,gxp-fan-ctrl`, MMIO accessors, and the hwmon callback API.

## Risks
Channel count is fixed at eight, so hardware variants with fewer registers depend on resource sizing and firmware correctness. PWM writes do not check fan installation or power state, while reads do, so user-observed state can differ after writes to absent/off fans. There is no locking, which is acceptable for simple MMIO bytes but means concurrent writes are last-writer-wins.

## Test Signals
Test resource mapping failures, all eight channel attributes, PWM range validation, power-off read returning zero, installed-bit gating, fault-bit reporting, and writes reaching the expected byte offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/gxp-fan-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hih6130.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/hih6130.c

## Purpose
`hih6130.c` supports Honeywell HIH-6130/6131 humidity and temperature sensors over I2C. It exports `temp1_input` and `humidity1_input` through hwmon sysfs.

## Important APIs, Types, and Functions
`struct hih6130` holds the I2C client, mutex, cache validity, last update jiffies, converted temperature/humidity, and `write_length` for the measurement request. Conversion helpers implement datasheet formulas for 14-bit humidity and temperature ticks. `hih6130_update_measurements()` performs request, delay, read, status validation, conversion, and caching. `hih6130_temperature_show()` and `hih6130_humidity_show()` are the sysfs read paths.

## Control Flow
Probe requires true I2C functionality, allocates state, initializes the mutex, and sets `write_length` to one dummy byte if the adapter lacks SMBus quick support. It registers a grouped hwmon device. A sysfs read calls the update routine. The update routine serializes access, refreshes at most once per second, sends either a zero-length or dummy-byte request, sleeps 40 ms for conversion, reads four bytes with `i2c_transfer()`, rejects nonzero status bits, then updates cached humidity and temperature.

## State and Persistence
The only state is an in-memory one-second measurement cache. The sensor is not configured or programmed; every refresh performs a measurement request and read.

## Dependencies and Integration Points
It uses I2C master send/transfer APIs, hwmon sysfs attribute groups, jiffies cache timing, and a mutex. Device matching supports I2C IDs and OF compatible `honeywell,hih6130`.

## Risks
The update routine treats any nonnegative `i2c_transfer()` return as success, though a short transfer should be considered invalid. The 40 ms conversion wait is fixed. Adapters that mishandle zero-length sends rely on the dummy-byte fallback. No CRC exists for this device protocol.

## Test Signals
Test adapters with and without SMBus quick support, status-bit error handling, conversion math against datasheet vectors, cache reuse within one second, refresh after expiry, short transfer behavior, and OF/I2C device matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hih6130.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hp-wmi-sensors.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/hp-wmi-sensors.c

## Purpose
`hp-wmi-sensors.c` exposes numeric sensors on HP business-class systems through WMI. It maps HP BIOS WMI objects into hwmon temperature, voltage, current, fan, and intrusion attributes, includes debugfs introspection, and optionally subscribes to WMI events for alarms.

## Important APIs, Types, and Functions
Key structures are `hp_wmi_numeric_sensor`, `hp_wmi_platform_events`, `hp_wmi_event`, `hp_wmi_info`, and `hp_wmi_sensors`. Property maps validate ACPI object layouts. String helpers handle normal ACPI strings and raw length-prefixed UTF-16 WMI buffers. `check_numeric_sensor_wobj()` supports both old and new object layouts, including flattened `PossibleStates[]`. `populate_*_from_wobj()` and `update_numeric_sensor_from_wobj()` load and refresh WMI data. `classify_numeric_sensor()`, `scale_numeric_sensor()`, and `numeric_sensor_has_fault()` translate HP semantics to hwmon. `hp_wmi_hwmon_*()` implement the hwmon callbacks. Event helpers classify and match fan, temperature, and intrusion events.

## Control Flow
Probe allocates state for the WMI device, initializes a mutex, and calls `hp_wmi_sensors_init()`. Initialization loads platform event descriptors, enumerates numeric sensor instances, filters disconnected/unsupported sensors, classifies connected sensors into hwmon channel maps, creates debugfs when enabled, finds which events can back alarm attributes, installs a WMI notify handler if useful, builds dynamic `hwmon_channel_info` arrays, and registers `hp_wmi_sensors`. Hwmon reads update each sensor at most once per second via `wmidev_block_query()`, then return scaled values, fault state, labels, alarm flags, or intrusion status.

## State and Persistence
Sensor metadata is devm-managed for the WMI device lifetime. Current readings, current state, unit modifier, cached scaled values, last update times, alarm flags, and intrusion state live in RAM. Reading temp/fan alarm clears that per-channel alarm flag; writing zero to intrusion clears intrusion state. No firmware settings are changed.

## Dependencies and Integration Points
The driver integrates with the WMI bus, ACPI object parsing, hwmon callback registration, thermal zone registration through `HWMON_C_REGISTER_TZ`, debugfs, jiffies, mutexes, and unit conversion helpers.

## Risks
The WMI schemas are firmware-defined and partly reverse-engineered; validation must stay strict to avoid misparsing flattened packages. `hp_wmi_chip_info` is static but its `.info` pointer is assigned per probe, which is risky if multiple WMI devices existed concurrently. Event-to-sensor matching relies on free-form names/descriptions. Alarm reads clear flags, so polling consumers can race each other. The update path ignores refreshes within one second even if an event just occurred.

## Test Signals
Test old and new numeric sensor package layouts, raw UTF-16 string conversion, disconnected sensor filtering, unit scaling for C/F/K and modifier extremes, dynamic channel configs, debugfs contents, WMI event parsing and alarm matching, intrusion clear semantics, thermal-zone registration for temps, and failure tolerance when notify handler installation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hp-wmi-sensors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hs3001.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/hs3001.c

## Purpose
`hs3001.c` is a basic hwmon driver for Renesas HS3001-compatible humidity and temperature sensors. It supports runtime measurement reads only, not programming-mode configuration.

## Important APIs, Types, and Functions
`struct hs3001_data` stores the I2C client, conversion wait time, and last converted temperature/humidity. `hs3001_extract_temperature()` and `hs3001_extract_humidity()` convert raw big-endian samples into millidegrees Celsius and milli-percent relative humidity. `hs3001_data_fetch_command()` validates the four-byte response and status bits. `hs3001_read()` is the hwmon read callback; `hs3001_is_visible()` exposes read-only attributes.

## Control Flow
Probe verifies true I2C support, allocates state, sets a static wait time for 14-bit humidity plus 14-bit temperature and wake-up delay, then registers a callback-based hwmon device. Each hwmon read sends a zero-length I2C command to trigger measurement, sleeps for the configured wait time, fetches four bytes, rejects stale or invalid status, updates cached fields, and returns the requested channel value.

## State and Persistence
The driver has no cache validity window; every read triggers a new conversion. The last converted values are stored in RAM but only used immediately by the read path. No sensor configuration is persisted.

## Dependencies and Integration Points
It uses I2C master send/receive, bitfield helpers, endian helpers, `fsleep()`, and hwmon callback registration. It matches I2C ID `hs3001` and OF compatible `renesas,hs3001`.

## Risks
`hs3001_extract_humidity()` has precedence-sensitive arithmetic: `return hum / (1 << 14) - 1` subtracts one after division, unlike the usual denominator `(2^14 - 1)`. Zero-length `i2c_master_send()` may be adapter-sensitive. There is no mutex, so concurrent reads can overlap trigger/fetch cycles. The fixed maximum-resolution wait time may not match sensors configured differently outside the driver.

## Test Signals
Test raw conversion vectors, stale and invalid status handling, short receive handling, concurrent reads, adapter behavior for zero-length sends, OF/I2C matching, and timing around the configured conversion delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hs3001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/htu31.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/htu31.c

## Purpose
`htu31.c` drives Measurement Specialties HTU31 temperature and humidity sensors. It exposes temperature/humidity via hwmon, a writable heater control sysfs attribute, and the sensor serial number through debugfs.

## Important APIs, Types, and Functions
`struct htu31_data` stores client, mutex, conversion wait time, latest readings, serial number, and heater state. `htu31_data_fetch_command()` triggers conversion, waits, reads six bytes, verifies CRC8 for temperature and humidity words, and converts values. `htu31_read_serial_number()` reads and CRC-checks the serial number. `heater_enable_show()`/`heater_enable_store()` expose heater control. `htu31_read()` implements hwmon reads, with visibility from `htu31_is_visible()`.

## Control Flow
Probe allocates state, initializes a devm mutex, populates the CRC8 table, reads the serial number, creates debugfs under the I2C client's debugfs directory, and registers hwmon with standard temp/humidity channels plus the heater attribute group. Each hwmon read locks, sends the conversion command, sleeps for combined maximum temperature and humidity conversion time, performs a write-then-read I2C transfer, validates both CRC bytes, updates cached readings, and returns the requested value. Heater writes parse a boolean, lock, send one byte, and update cached heater state.

## State and Persistence
Measurements and heater state are in RAM. Heater state is also programmed into the device and persists according to sensor power state. The serial number is read once at probe and retained for debugfs.

## Dependencies and Integration Points
The driver uses I2C transfers, CRC8 table helpers, cleanup guard mutex syntax, debugfs, hwmon callback registration, and OF/I2C matching (`meas,htu31`, `htu31`).

## Risks
`htu31_read_serial_number()` treats any nonnegative `i2c_transfer()` result as success instead of requiring both messages. Debugfs file lifetime relies on the I2C client's debugfs parent. There is no measurement cache, so frequent reads always trigger conversions. Heater state can diverge if hardware changes externally or a positive short send is returned.

## Test Signals
Test CRC mismatch handling, serial read failure, heater boolean parsing and command selection, temperature/humidity conversion vectors, short I2C transfer behavior, concurrent reads and heater writes under the mutex, and debugfs serial formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/htu31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hwmon-vid.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/hwmon-vid.c

## Purpose
`hwmon-vid.c` provides shared VID-to-voltage and CPU-to-VRM helpers for legacy hwmon drivers. It converts raw VID pin/register values into millivolts and, on x86, chooses the expected VRM/VRD table from CPU vendor/family/model/stepping.

## Important APIs, Types, and Functions
`vid_from_reg(int val, u8 vrm)` is exported and implements VRM 8.2/8.4/8.5/9.0/9.1, VRD 10, Intel Conroe VRM 11, AMD K8/NPT/family 10h-15h variants, IMVP-II, Pentium M, and Intel Core tables. `struct vrm_model` and `vrm_models[]` encode x86 CPU matching. `find_vrm()` searches the table. `get_via_model_d_vrm()` uses MSRs to disambiguate VIA model D. `vid_which_vrm()` is exported and returns a VRM code or zero.

## Control Flow
Callers pass a VID value and VRM code to `vid_from_reg()`, which masks the raw code, handles table-specific no-voltage encodings, performs integer arithmetic in millivolts or microvolts with rounding, and warns for unsupported nonzero VRM codes. On x86, `vid_which_vrm()` reads `cpu_data(0)`, rejects pre-family-6 CPUs, finds the matching table row, resolves VIA special code `134` if needed, and logs unknown CPUs.

## State and Persistence
The file has no mutable persistent state except static lookup tables. It reads CPU identity and, for VIA model D, model-specific registers at call time.

## Dependencies and Integration Points
It is a library module for hwmon drivers such as GL520SM. It depends on `linux/hwmon-vid.h`, module exports, and x86 CPU/MSR definitions when `CONFIG_X86` is enabled. Non-x86 builds return VRM zero with an informational message.

## Risks
The CPU table is historical and may not cover newer systems. Some conversions rely on legacy assumptions about motherboard VID pin routing. Unsupported VRM values return zero, which can be indistinguishable from valid no-voltage encodings to callers. MSR reads are VIA-specific and only compiled for x86.

## Test Signals
Test VID conversion vectors for every supported VRM code, no-voltage encodings, rounding boundaries, unsupported VRM warnings, CPU table matching including VIA model D paths, and non-x86 fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hwmon-vid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/hwmon.c

## Purpose
`hwmon.c` is the core hwmon class implementation. It creates `/sys/class/hwmon/hwmonN` devices, generates standard sysfs attributes from `hwmon_chip_info`, serializes driver callbacks, bridges eligible temperature channels into thermal zones, supports optional I2C PEC control, emits notifications, and provides devm registration helpers.

## Important APIs, Types, and Functions
`struct hwmon_device` wraps the class device, name/label, chip info, mutex, thermal-zone data, and generated groups. `struct hwmon_device_attribute` records each generated attribute's ops, type, attr, channel index, and formatted name. Registration funnels through `__hwmon_device_register()`, with exported wrappers `hwmon_device_register_with_info()`, `devm_hwmon_device_register_with_info()`, group-based legacy helpers, thermal-only registration, sanitize-name helpers, `hwmon_notify_event()`, `hwmon_lock()`, and `hwmon_unlock()`. Attribute generation uses template arrays per sensor type and `hwmon_genattr()`.

## Control Flow
Class initialization runs early via `subsys_initcall()`, first applying a PCI quirk for an MSI board. Registration allocates an IDA ID, allocates `hwmon_device`, optionally generates attributes from chip channel configs, merges extra groups, copies a firmware `label`, sets class/parent/of_node/driver data, registers the device, and optionally registers thermal zones and I2C PEC support if chip config requests it. Sysfs reads/writes lock the hwmon device mutex and call driver `read`, `read_string`, or `write` callbacks. Unregister releases the device and ID, while devm wrappers attach unregister actions to the parent.

## State and Persistence
The core owns generated attribute memory, the class device, ID allocation, copied labels, and registered thermal-zone tracking for the hwmon device lifetime. It does not cache sensor values; drivers own sensor state. PEC writes mutate the parent I2C client's flags.

## Dependencies and Integration Points
It integrates with the driver core class subsystem, sysfs, IDA, device properties, I2C, thermal OF, PCI quirks, tracepoints, and exported hwmon APIs consumed by nearly every hwmon driver.

## Risks
Because all generated callback access is serialized by a single mutex, slow driver reads can block unrelated attributes. Attribute generation requires visible modes to match available callbacks; driver mistakes fail registration. The `energy64` path casts a `s64` buffer through `long *`, which relies on callback convention and architecture expectations. PEC support assumes a single hwmon child below an I2C client. ID freeing is split between unregister and release paths and depends on correct device names.

## Test Signals
Test registration failure cleanup, generated attribute names and modes for each sensor type, string versus numeric callbacks, extra group merging, label visibility, name sanitization, thermal zone registration and trip writes, event notification names, I2C PEC toggling, devm unregister, and invalid chip-info rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/i5500_temp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/i5500_temp.c

## Purpose
`i5500_temp.c` exposes the thermal sensor in Intel 5500/5520/X58 chipsets as a single hwmon temperature channel with input, critical threshold, and fault status.

## Important APIs, Types, and Functions
`i5500_read()` is the hwmon read callback and decodes PCI config registers for `temp1_input`, `temp1_crit`, and `temp1_fault`. `i5500_ops`, `i5500_info`, and `i5500_chip_info` describe the hwmon interface. `i5500_temp_probe()` enables the PCI device, checks sensor availability, and registers the hwmon device. `i5500_temp_driver` binds PCI IDs for Intel 5500/5520/X58 thermal sensor devices.

## Control Flow
Probe enables the PCI function with `pcim_enable_device()`, reads `REG_TSTHRCATA`, and rejects the device if the unavailable bit is set. It then registers `intel5500`. Reads use `pci_read_config_word()` or `pci_read_config_byte()` from the PCI device stored as the parent of the hwmon device. Temperature input and critical threshold are derived from register fields as `millidegrees`; fault reports the alarm bit.

## State and Persistence
The driver has no private state and no cache. All values are read live from PCI config space. It does not write thresholds or alter chipset settings.

## Dependencies and Integration Points
It depends on PCI config access, managed PCI enablement, and hwmon callback registration. It is registered with `module_pci_driver()`.

## Risks
The implementation assumes the hwmon device parent is the PCI device and uses `to_pci_dev(dev->parent)`. A config read failure would leave local variables at zero because return codes are not checked. The sensor is rejected only by one availability bit; platform firmware quirks may still expose unusable readings.

## Test Signals
Test PCI ID binding, unavailable-bit probe rejection, config-space decode vectors for input/crit/fault, behavior under failed PCI config reads, and absence of writable attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/i5500_temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/i5k_amb.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/i5k_amb.c

## Purpose
`i5k_amb.c` monitors AMB temperature sensors on Intel 5000-series FB-DIMM chipsets. It dynamically creates sysfs attributes for present AMB devices across memory branches, channels, and DIMM slots.

## Important APIs, Types, and Functions
`struct i5k_amb_data` stores chipset resources, AMB-present bitmasks, dynamically allocated attributes, and hwmon device pointer. `struct i5k_device_attribute` extends `sensor_device_attribute` with node/register metadata. Show helpers expose ambient temperature, status, alarm, and threshold fields. `i5k_channel_probe()` detects populated AMB channels through PCI config space. `i5k_amb_hwmon_init()` creates sysfs files and registers hwmon. `i5k_amb_probe()` identifies the chipset, maps resources, reads AMB presence, and initializes hwmon; `i5k_amb_remove()` tears it down.

## Control Flow
Module init registers a platform driver and platform device. Probe finds a supported Intel memory controller/chipset, maps AMB MMIO, probes channel presence via PCI devices, calculates which AMBs exist, and calls hwmon init. Hwmon init creates a `name` attribute, allocates per-sensor attributes for every present AMB and supported register, creates each sysfs file manually, then registers a legacy hwmon device. On failure or removal it walks the created attributes and removes them.

## State and Persistence
The driver stores discovered AMB presence and the list of created attributes in RAM. Readings and threshold/status values are read live from chipset/AMB registers. No writes are exposed in this source, so hardware thresholds are not changed.

## Dependencies and Integration Points
It uses PCI discovery/config access, platform driver/device plumbing, MMIO access, hwmon legacy registration, and manual sysfs file creation. It predates the modern `hwmon_chip_info` model.

## Risks
Manual sysfs creation has many partial-failure cleanup paths. Dynamic attribute naming/indexing must stay aligned with branch/channel/DIMM register layout. Legacy `hwmon_device_register()` is deprecated. Hardware presence probing is chipset-specific and depends on PCI IDs and config offsets. The report should watch for unchecked low-level read failures and assumptions around AMB bitmaps.

## Test Signals
Test supported and unsupported chipset probing, AMB presence bitmaps, generated attribute names/counts, partial sysfs creation cleanup, remove cleanup, MMIO decode for all exposed fields, and behavior when a channel probe PCI device is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/i5k_amb.c -->
