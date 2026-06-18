# Research: subset-b-003821

Grouped research for Linux hwmon drivers under `sources/distributed-fs/ceph-client/drivers/hwmon`. Each file section is delimited for reconciliation into source-tree-aligned per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aht10.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/aht10.c

## Purpose
This is an I2C hwmon driver for Aosong AHT10, AHT20, and DHT20 temperature and humidity sensors. It exposes one temperature input, one humidity input, and a writable chip update interval through the modern `hwmon_device_register_with_info()` interface.

## Important APIs, Types, And Functions
The driver is centered on `struct aht10_data`, which stores the `i2c_client`, poll interval, previous poll time, cached temperature and humidity, measurement frame size, CRC use, and variant-specific initialization command. Device matching uses `aht10_id` and `aht10_of_match`, with enum variants `aht10`, `aht20`, and `dht20`.

`aht10_probe()` checks `I2C_FUNC_I2C`, allocates state with `devm_kzalloc()`, selects variant behavior, initializes the chip, performs an initial reading, and registers hwmon channels. `aht10_init()` sends the variant init command and checks the busy bit. `aht10_read_values()` sends measurement command `0xac 0x33 0x00`, waits, reads 6 or 7 bytes, validates optional AHT20/DHT20 CRC8, decodes 20-bit humidity and temperature, and updates cached millipercent and millidegree values. `aht10_hwmon_read()`, `aht10_hwmon_write()`, and `aht10_hwmon_visible()` implement the hwmon callbacks.

## Control Flow And State
Probe performs one-time setup and immediately populates cached sensor values. Runtime reads flow through hwmon callbacks to `aht10_temperature1_read()` or `aht10_humidity1_read()`, both of which call `aht10_read_values()`. The driver rate-limits physical sensor transactions through `aht10_polltime_expired()`: if the configured interval has not elapsed, it returns cached readings instead of touching the bus.

State is per device and devm-managed. There is no explicit mutex, so concurrent sysfs reads can race through `previous_poll_time`, `temperature`, and `humidity`; in practice the accesses are simple scalar updates, but duplicated I2C transactions are possible. Persistence is limited to hardware configuration and cached in-memory readings. The writable update interval is clamped to at least 2000 ms and is not stored across driver reloads.

## Dependencies And Integration Points
The driver depends on Linux I2C core APIs, hwmon with-info APIs, `ktime`, `usleep_range()`, and `crc8` helpers. It integrates through I2C IDs and Open Firmware compatibles `aosong,aht10`, `aosong,aht20`, and `aosong,dht20`.

## Risks
The main operational risks are timing-sensitive sensor transactions, CRC failure handling for AHT20/DHT20, and lack of serialization around cached state. `aht10_init()` treats any one-byte status read other than exactly one byte as `-ENODATA`, and a busy status as `-EBUSY`; marginal hardware could fail probe. Because reads return cached data during the poll interval, test expectations must account for stale values after changing environmental conditions.

## Test Signals
Useful tests are probe with each compatible/device ID, sysfs reads of `temp1_input`, `humidity1_input`, and `update_interval`, update interval writes below and above 2000 ms, simulated short I2C reads, CRC mismatch on 7-byte frames, and verification that two immediate reads do not generate a second measurement transaction while reads after the interval do.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aht10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/amc6821.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/amc6821.c

## Purpose
This driver supports the Texas Instruments AMC6821 temperature monitor and PWM fan controller. It exposes local and remote temperature limits and alarms, fan RPM thresholds and target speed, PWM control modes, auto temperature points, and optional thermal cooling-device integration from device tree.

## Important APIs, Types, And Functions
`struct amc6821_data` owns the `regmap`, an `update_lock` for compound auto-point operations, thermal cooling state, cooling levels, and PWM polarity. Register access is through an 8-bit `REGCACHE_MAPLE` regmap with volatile status, temperature, and tachometer registers declared by `amc6821_volatile_reg()`.

The hwmon path is implemented by `amc6821_read()`, `amc6821_write()`, and `amc6821_is_visible()`, dispatching to temperature, fan, and PWM helpers. Temperature helpers convert signed register values to millidegrees and write min/max/critical limits. Fan helpers convert tachometer counts using `6000000 / count` and write low/high/target tach limits. PWM helpers expose manual, target-RPM, remote-temperature, and max-local/remote auto modes through `pwm1_enable`, plus duty and tach/PWM mode. Extra sysfs attributes for auto points are built with `SENSOR_DEVICE_ATTR*` and guarded by `update_lock`.

## Control Flow And State
`amc6821_probe()` allocates state, initializes regmap, optionally reads a `fan` child node for PWM polarity and `cooling-levels`, initializes hardware, optionally populates subdevices for `tsd,mule`, registers hwmon, and registers a thermal cooling device when configured. `amc6821_init_client()` sets standalone mode, disables selected interrupts, applies PWM inversion, starts monitoring, and if cooling levels exist sets software duty-cycle control to the maximum cooling state.

Persistent state lives mostly in chip registers: temperature thresholds, tach limits, duty cycle, fan mode bits, auto-point settings, and PWM polarity. The driver keeps in-memory thermal state (`fan_state`) and cooling levels but does not restore them from hardware after reload. Auto-point updates are read-modify-write sequences that recompute slopes and therefore need the mutex.

## Dependencies And Integration Points
The driver integrates with the I2C hwmon class, OF compatible strings `ti,amc6821` and `tsd,mule`, regmap, PWM polarity bindings, and optional Linux thermal cooling APIs. Legacy auto-detection scans common addresses and validates device/company IDs.

## Risks
The conversion between RPM and tach counts can lose precision and rejects some zero values by design. Auto-point slope calculation depends on current low-temperature PWM and can silently quantize to hardware-supported steps. The `pwminv` module parameter overrides device-tree polarity, which can surprise board descriptions. Thermal cooling state only tracks successful driver writes, not external hardware changes.

## Test Signals
Check I2C detection ID paths, regmap volatile behavior, read/write permissions from `amc6821_is_visible()`, temperature limit sign extension, tach count conversion including zero and high RPM, PWM mode mappings 1-4, auto-point writes that force valid ordering, device-tree cooling registration, `pwminv` override behavior, and `tsd,mule` child population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/amc6821.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/applesmc.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/applesmc.c

## Purpose
This platform hwmon driver talks directly to Apple SMC I/O ports on Intel-based Apple machines. It exposes SMC key metadata, temperatures, fan control, accelerometer input, ambient light, and keyboard backlight control where the machine supports those keys.

## Important APIs, Types, And Functions
The global `smcreg` structure caches SMC key count, fan count, temperature key index, feature flags, and an array of `struct applesmc_entry` records containing key, length, type, flags, and validity. Low-level transport is implemented by `wait_status()`, `send_byte()`, `send_command()`, `read_smc()`, and `write_smc()` against ports `0x300` and `0x304`. Public internal key helpers are `applesmc_get_entry_by_index()`, `applesmc_get_entry_by_key()`, `applesmc_read_key()`, `applesmc_write_key()`, and `applesmc_read_s16()`.

Subsystem-facing functions include dynamic sysfs node creation through `applesmc_create_nodes()`, fan speed/manual handlers, temperature label/input handlers, input polling via `applesmc_idev_poll()`, LED keyboard backlight handling via `applesmc_brightness_set()` and a workqueue, and PM resume/restore hooks.

## Control Flow And State
Module init first requires a DMI whitelist match, claims the SMC I/O region, registers a platform driver/device, initializes the SMC register cache with retry, creates info/fan/temp sysfs files, then conditionally creates accelerometer, light sensor, keyboard backlight, and hwmon device resources. `applesmc_init_smcreg_try()` reads `#KEY`, allocates or refreshes the cache, discovers fan count, binary-searches key ranges for temperature keys, and checks feature keys.

Runtime operations serialize SMC I/O with `smcreg.mutex`. Key metadata is lazily cached by index. Temperature index state and feature flags persist for the module lifetime. Backlight brightness is remembered in `backlight_state` and re-written on resume. Accelerometer calibration stores `rest_x/rest_y` in memory only. Sysfs `key_at_index` is a global selector for several metadata files.

## Dependencies And Integration Points
The driver uses raw x86 I/O port access, DMI matching, platform devices, hwmon legacy registration, hwmon sysfs attributes, input polling, LED class devices, workqueues, and PM callbacks. It is not a normal discoverable bus driver; the DMI whitelist and I/O port reservation gate loading.

## Risks
The driver is highly timing-sensitive and depends on undocumented SMC status behavior. Global singleton state means one device instance is assumed. Dynamic sysfs creation has many staged failure paths, so cleanup ordering is important. The light sensor data length is cached in a static local and assumes the left/right formats remain compatible. Fan writes and keyboard backlight writes directly affect platform hardware.

## Test Signals
Important tests are DMI rejection, I/O region conflict handling, SMC command timeout/error paths, key-cache lookup and binary-search bounds, dynamic sysfs creation cleanup failures, temperature key enumeration, fan manual/output writes, accelerometer input registration and calibration, LED workqueue behavior, and resume restoring keyboard backlight state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/applesmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aquacomputer_d5next.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/aquacomputer_d5next.c

## Purpose
This HID hwmon driver supports many Aquacomputer USB cooling devices, including D5 Next, Farbwerk, Farbwerk 360, Octo, Quadro, High Flow Next, Aquaero, Aquastream Ultimate/XT, Leakshield, Poweradjust 3, and High Flow USB/MPS Flow devices. It converts HID status and feature reports into hwmon temperature, fan, PWM, voltage, current, power, and debugfs information.

## Important APIs, Types, And Functions
`struct aqc_data` stores HID device handles, kind-specific report IDs and offsets, control report buffers and CRC parameters, counts and offsets for sensors, labels, cached readings, serial/firmware/power-cycle values, and update timestamp. `aqc_probe()` is the large product-ID dispatch that fills this structure for each device family. `aqc_raw_event()` processes periodic status report ID `0x01` for modern devices. Legacy devices use `aqc_legacy_read()` to request feature reports on demand.

Hwmon is implemented through `aqc_is_visible()`, `aqc_read()`, `aqc_read_string()`, and `aqc_write()`. Control report helpers `aqc_get_ctrl_data()`, `aqc_send_ctrl_data()`, `aqc_get_ctrl_val()`, `aqc_set_ctrl_val()`, and `aqc_set_ctrl_vals()` read-modify-write HID feature reports, adding CRC-16/USB where needed and sending the vendor secondary report after writes.

## Control Flow And State
Probe parses and starts HID, opens the device, filters composite Aquaero and Leakshield interfaces, configures offsets/labels/report sizes by product ID, allocates the control/status buffer, registers hwmon, and creates debugfs files for serial, firmware, and power cycles when offsets exist. Modern devices asynchronously update cached sensor values through `raw_event`; reads fail with `-ENODATA` when data is older than `STATUS_UPDATE_INTERVAL`. Legacy devices refresh synchronously during reads.

Writable state lives in device feature reports: temperature offsets, fan/PWM presets, flow pulses, and Aquaero fan preset routing. The in-memory cache stores the most recent sensor report and timestamps. Control report operations are rate-limited using `last_ctrl_report_op` and `ctrl_report_delay`, but there is no explicit mutex around buffer reuse, so concurrent writes could interleave.

## Dependencies And Integration Points
The driver integrates with HID raw requests/events, hwmon with-info APIs, debugfs, `crc16`, unaligned endian helpers, and the USB HID product table. It uses `late_initcall()` so registration happens after HID bus initialization.

## Risks
The main risks are product-specific offset drift, composite-interface misidentification, stale caches before the first report, concurrent control report buffer mutation, and device-specific checksum or secondary-report requirements. Several readings use sentinel `0x7fff` as `-ENODATA`; callers must handle that. Writes intentionally mimic vendor software but can alter pump/fan behavior.

## Test Signals
Test product-ID probe for every supported kind, Aquaero and Leakshield filtering, raw event parsing with N/A sensors, stale read behavior, legacy feature report refresh, control report CRC placement, secondary report emission, PWM percent conversion, temp offset clamping, flow pulse clamping, labels for special channels, debugfs file presence, and remove cleanup of debugfs/hwmon/HID resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aquacomputer_d5next.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/as370-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/as370-hwmon.c

## Purpose
This compact platform driver exposes the Synaptics AS370 SoC PVT temperature monitor as one hwmon temperature input.

## Important APIs, Types, And Functions
`struct as370_hwmon` holds the MMIO base pointer. `init_pvt()` powers and enables the PVT block by programming `CTRL` bits `PD`, `T_SEL`, and `EN`. `as370_hwmon_read()` reads the `STS` register, masks the 12-bit raw code with `BN_MASK`, and converts it to millidegrees using `DIV_ROUND_CLOSEST(val * 251802, 4096) - 85525`. `as370_hwmon_is_visible()` exposes only `hwmon_temp_input`.

## Control Flow And State
`as370_hwmon_probe()` allocates devm state, maps the first platform memory resource with `devm_platform_ioremap_resource()`, initializes the PVT monitor, and registers a devm hwmon device named `as370`. Runtime reads are direct MMIO reads; there is no cache, lock, interrupt, or polling state. Hardware configuration persists in the PVT registers until reset or another agent modifies them.

## Dependencies And Integration Points
The driver depends on platform device probing, device tree compatible `syna,as370-hwmon`, MMIO accessors, and the hwmon with-info API. It has no thermal-zone or regulator integration in this file.

## Risks
The conversion formula and initialization sequence are SoC-specific and not self-validating. The code does not check `EOC`, so it reports the current raw bits whether or not a conversion-complete bit is set. It also never disables or powers down the monitor on remove because all resources are devm-managed and no remove callback exists.

## Test Signals
Probe tests should cover missing MMIO resources, correct compatible matching, `CTRL` write sequence, read conversion for representative raw values, visibility limited to `temp1_input`, and behavior when `EOC` is clear if hardware or a mock can expose that condition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/as370-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asb100.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/asb100.c

## Purpose
This legacy I2C hwmon driver supports Asus ASB100/ASB100-A "BACH" monitoring chips. It exposes seven voltage inputs, three fan inputs and divisors, four temperature channels, alarms, VID/VRM, and one PWM output using manually created sysfs attributes.

## Important APIs, Types, And Functions
`struct asb100_data` stores the hwmon device, two mutexes, update timestamp/valid flag, two LM75 subclient pointers, cached register values, fan divisors, PWM, VID, alarms, and VRM. Conversion helpers map voltage, fan, temperature, PWM, and fan divisor values between hwmon units and chip register encodings.

`asb100_detect()` validates the chip through banked manufacturer/chip ID registers. `asb100_detect_subclients()` registers two LM75 dummy devices at addresses read from `ASB100_REG_I2C_SUBADDR` or forced through the module parameter. `asb100_read_value()` and `asb100_write_value()` handle bank switching and route bank 1/2 temperature accesses to the LM75 subclients. `asb100_update_device()` refreshes all cached readings every 1.5 seconds.

## Control Flow And State
Probe allocates state, initializes locks, creates subclients, starts monitoring by setting the config register, seeds fan minimums, creates one large sysfs group, and registers a legacy hwmon device. Runtime sysfs reads call `asb100_update_device()` and return cached converted values. Runtime writes update the cache and hardware under `update_lock`; banked register access is separately serialized by `lock` to prevent intervening bank changes.

Persistent state is in chip registers: limits, PWM enable/duty, fan divisors, subclient addresses, and config. Cached values are in-memory and invalidated by time only, so external register changes may be hidden for up to the refresh interval. Fan divisor writes preserve the effective fan minimum by converting to RPM first, changing divisor bits, and rewriting the threshold.

## Dependencies And Integration Points
The driver depends on SMBus byte data, I2C class probing at address `0x2d`, hwmon sysfs helper macros, `hwmon-vid`, and local `lm75.h` conversion helpers. It uses `i2c_new_dummy_device()` for subclient access rather than binding full LM75 drivers.

## Risks
Bank switching requires strict serialization; missing the lock would corrupt reads. The plain ASB100 and ASB100-A cannot be distinguished, so PWM attributes may exist even if unsupported. The `force_subclients` module parameter can point to invalid or conflicting addresses and is only lightly guarded. Many sysfs handlers use legacy `sprintf()` style and assume update reads succeed.

## Test Signals
Test chip detection across correct and incorrect ID/bank states, subclient address forcing and duplicate rejection, banked read/write routing, cache refresh timing, fan divisor threshold preservation, temperature conversion for direct and LM75-backed channels, PWM enable/duty behavior, alarm bit exposure, and remove cleanup of hwmon/sysfs/subclients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asb100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asc7621.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/asc7621.c

## Purpose
This I2C hwmon driver supports Andigilog aSC7621 and aSC7621a monitoring/fan-control chips. It exposes a broad manual sysfs surface for voltages, fans, temperatures, alarms, PWM controls, automatic fan zones, PECI options, smoothing, offsets, and critical limits.

## Important APIs, Types, And Functions
`struct asc7621_data` stores the I2C client, hwmon device, update lock, validity/timestamps, and a register cache indexed by register number. `struct asc7621_param` combines a `sensor_device_attribute` with priority and register/mask/shift metadata. The large `asc7621_params[]` table declares every sysfs file and drives both creation and register polling.

Generic show/store helpers handle unsigned bytes, bitfields, fan 16-bit RPM values, 10-bit and 8-bit voltages, multiple temperature encodings, synthesized auto-point2 temperatures, PWM auto-channel mapping, PWM enable mapping, PWM frequency, auto spinup, and temperature smoothing. `sm_asc7621_init()` precomputes `asc7621_register_priorities[]` from the parameter table before registering the I2C driver.

## Control Flow And State
Probe checks SMBus byte support, allocates state, starts monitoring through `asc7621_init_client()`, creates every sysfs file from `asc7621_params[]`, and registers hwmon. Runtime reads call `asc7621_update_device()`, which refreshes high-priority registers every 1.5 seconds and low-priority registers every 60 seconds. Writes use read-modify-write sequences under `update_lock` and update the local cache.

The driver keeps no persistent storage outside hardware registers. The cache is time-based and priority-based. The chip is initialized by clearing the lock bit when possible and setting START in config register `0x40`; if the chip reports locked or not ready, the driver logs errors but continues.

## Dependencies And Integration Points
The driver uses I2C class hwmon probing at addresses `0x2c`-`0x2e`, SMBus byte operations, legacy manual sysfs file creation, and hwmon registration. Detection validates company and version/step registers for both supported chip types.

## Risks
The table-driven design is compact but fragile: wrong register metadata affects both sysfs semantics and polling. In `asc7621_update_device()`, the low-priority refresh loop iterates over `ARRAY_SIZE(asc7621_params)` while indexing `asc7621_register_priorities`, which means priority entries above the number of parameters would not be refreshed by that loop. Many writes quantize to maps and reject non-exact frequencies/timings. Continuing after locked/not-ready warnings can expose a partially controllable device.

## Test Signals
Test detection for both chip IDs, priority map generation, high/low refresh intervals, creation/removal of all sysfs files, fan RPM zero/0xffff handling, voltage scaling, temperature encodings, PWM enable and auto-channel mappings, exact accepted frequency/spinup/smoothing values, config lock warning behavior, and error handling for failed SMBus reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asc7621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-g6-pwm-tach.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-g6-pwm-tach.c

## Purpose
This platform driver supports the newer Aspeed AST2600/AST2700 PWM/tach controller. It registers a Linux PWM chip for 16 PWM outputs and a hwmon device for up to 16 tachometer fan inputs described by device tree child nodes.

## Important APIs, Types, And Functions
`struct aspeed_pwm_tach_data` stores MMIO base, clock/reset handles, clock rate, tach-present bitmap, and current tach divisor. PWM behavior is implemented through `aspeed_pwm_ops`, specifically `aspeed_pwm_get_state()` and `aspeed_pwm_apply()`. Tach hwmon behavior is implemented by `aspeed_tach_hwmon_read()`, `aspeed_tach_hwmon_write()`, and `aspeed_tach_dev_is_visible()`.

`aspeed_pwm_apply()` computes high/low clock divisors for a requested period, fixes the hardware period field to its maximum for duty resolution, maps 0 percent duty to clock-disable and 100 percent duty to equal rising/falling semantics, and writes control/duty registers. `aspeed_present_fan_tach()` programs debounce, edge mode, clock divisor, threshold bits, marks channels present, and enables tach channels.

## Control Flow And State
Probe maps MMIO, enables the clock, deasserts reset with a devm reset action, allocates and registers a 16-channel PWM chip, walks child nodes reading `tach-ch`, initializes each listed tach channel, registers hwmon named `aspeed_tach`, and populates child platform devices. Runtime PWM consumers use the PWM framework; fan reads use hwmon callbacks and return RPM only after `TACH_ASPEED_FULL_MEASUREMENT` is set.

State is mostly hardware register state plus in-memory `tach_present[]` and `tach_divisor`. The single `tach_divisor` is shared across channels even though writes occur per channel, so a user writing `fanN_div` changes the divisor used for later RPM conversion globally. There is no cache of RPM values.

## Dependencies And Integration Points
The driver depends on platform resources, device tree compatibles `aspeed,ast2600-pwm-tach` and `aspeed,ast2700-pwm-tach`, clock and reset frameworks, PWM framework, hwmon with-info APIs, and child-node tach channel descriptions.

## Risks
PWM period/duty changes can still glitch as described in the file comments. Tach RPM conversion can divide by zero if a full measurement reports a zero raw tach value; the read path checks only the full-measurement bit before conversion. Shared `tach_divisor` can produce incorrect RPM if channels use different divisors. Probe returns success without hwmon when `aspeed_create_fan_monitor()` fails, because it warns and returns 0.

## Test Signals
Test PWM get/apply calculations for 0, partial, and 100 percent duty; period clamping and `-ERANGE`; polarity inversion; reset assert on cleanup; child `tach-ch` parsing; tach visibility; fan divisor validation; RPM conversion for no full measurement and representative raw counts; multi-channel divisor behavior; and probe behavior on malformed child nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-g6-pwm-tach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-pwm-tacho.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-pwm-tacho.c

## Purpose
This older Aspeed AST2400/AST2500 PWM/tach platform driver exposes PWM duty controls, fan tachometer inputs, and optional thermal cooling devices from device-tree fan child nodes. It uses direct regmap-backed MMIO register programming rather than the generic PWM framework.

## Important APIs, Types, And Functions
`struct aspeed_pwm_tacho_data` stores the regmap, reset, clock frequency, present bitmaps for eight PWM ports and sixteen tach channels, per-type PWM/tach timing fields, port-to-type/source mappings, cooling devices, sysfs groups, and `tach_lock` for the shared result register. Static `type_params[]` and `pwm_port_params[]` tables describe register layout for PWM types M/N/O and ports A-H.

Hardware helpers configure clocks, PWM port enable/type/duty, tach type values, tach channel enable/source, and fan-control duty. Sysfs handlers `pwm_show()/pwm_store()` expose `pwm1`-`pwm8`; `rpm_show()` exposes `fan1_input`-`fan16_input`. Cooling callbacks map thermal states to configured PWM levels.

## Control Flow And State
Probe maps MMIO, allocates state, initializes a regmap wrapper around relaxed MMIO accessors, deasserts reset with a devm cleanup action, clears tach source registers, reads clock rate, enables clock source, creates the default type-M timing, then walks each child node. `aspeed_create_fan()` reads `reg` for PWM port, enables that PWM at `INIT_FAN_CTRL`, optionally registers a thermal cooling device from `cooling-levels`, reads `aspeed,fan-tach-ch`, and enables tach channels sourced from that PWM port. Finally it registers hwmon with two attribute groups whose visibility depends on present bitmaps.

Persistent state is in hardware registers for port duty, type timing, tach source, and channel enables. In-memory state mirrors current PWM values, mappings, cooling levels/states, and present channels. Tach reads serialize trigger/result access with `tach_lock`, trigger one channel, poll `ASPEED_PTCR_RESULT`, and compute RPM from raw count, edge mode, clock divisor, and clock frequency.

## Dependencies And Integration Points
The driver integrates with platform resources, device tree compatibles `aspeed,ast2400-pwm-tacho` and `aspeed,ast2500-pwm-tacho`, reset and clock frameworks, regmap, hwmon legacy group registration, and optional thermal cooling APIs.

## Risks
The regmap has no cache and all synchronization is manual. Tach polling timeout depends on computed measurement period; invalid timing could make reads slow or fail. PWM sysfs values are not the generic PWM API and are fixed to 0-255. Device-tree mistakes in `reg`, `cooling-levels`, or `aspeed,fan-tach-ch` abort probe. RPM calculation assumes the configured source/type mapping remains consistent with hardware.

## Test Signals
Test child parsing for valid and invalid PWM/tach channels, sysfs visibility for present ports only, PWM writes outside 0-255, duty register behavior for 0 and 255, cooling-device state transitions, tach result timeout, tach RPM math for both-edge and single-edge modes, reset cleanup, clock-rate dependency, and malformed device-tree failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-pwm-tacho.c -->
