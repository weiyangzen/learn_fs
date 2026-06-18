# subset-b-003822 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus-ec-sensors.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/asus-ec-sensors.c

Purpose: ASUS motherboard hwmon driver for sensors exposed through embedded-controller registers. It is DMI-gated to known ASUS boards and translates board-specific EC register layouts into standard hwmon temperature, voltage, current, fan, and chip attributes.

Important APIs, types, and functions: `sensor_address`, `ec_sensor_info`, `ec_board_info`, `ec_sensor`, `lock_data`, and `ec_sensors_data` hold the board mask, sensor metadata, cached values, register list, bank list, and ACPI lock method. The sensor-family arrays define register addresses per board generation, while `dmi_table` maps exact board names to `ec_board_info`. `setup_sensor_data()` expands the board bitmask into active sensors and sorted bank IDs; `fill_ec_registers()` builds the ordered EC register list. `setup_lock_data()` selects either a named ACPI mutex, the ACPI global lock pseudo-path, or returns an error. `asus_ec_bank_switch()`, `asus_ec_block_read()`, `get_sensor_value()`, `update_sensor_values()`, and `update_ec_sensors()` implement locked EC banked reads. `asus_ec_hwmon_read()`, `asus_ec_hwmon_read_string()`, and `asus_ec_hwmon_is_visible()` back the hwmon callbacks, and `asus_ec_probe()` creates dynamic channel info before `devm_hwmon_device_register_with_info()`.

Control flow: module init creates a bundled platform device/driver pair. Probe first finds a DMI match, picks the sensor family from the board family enum, allocates active sensor/register/read-buffer arrays, resolves the ACPI guard, fills register metadata, counts hwmon channels by type, constructs `hwmon_channel_info` arrays, and registers the `asusec` hwmon device. Reads map `(type, channel)` to an active sensor, refresh all EC values when the one-second cache expires, scale temperatures and currents to milli-units, and return labels from the sensor metadata.

State and persistence: runtime state is entirely in devm-managed `ec_sensors_data`. Sensor values are cached in `ec_sensor.cached_value` and refreshed no more than once per `HZ`. The only module parameter is `mutex_path`, which overrides the board-selected ACPI mutex path. Hardware state is not persisted, except the EC bank is restored to the previously observed bank after block reads.

Dependencies and integration points: depends on ACPI EC accessors (`ec_read`, `ec_write`), ACPI mutex/global-lock APIs, DMI matching, hwmon core, platform devices, jiffies, sort, bit operations, and unaligned big-endian loads. Integration is through exact ASUS board DMI strings and hwmon sysfs; no device tree or PCI probe path exists.

Risks: correctness depends on board-specific register maps and sorted bank/register assumptions. EC access can race firmware or other EC users; the driver warns if the previous bank is nonzero and relies on the selected ACPI mutex/global lock to reduce risk. A wrong `mutex_path` or firmware path change prevents probe. `ASUS_EC_MAX_BANK` is a fixed bound, so future boards with more banks need updates. Signed temperature handling is guessed from DSDT behavior, and adding sensors with wrong size or type can produce bad scaling.

Test signals: test by loading on matching DMI systems and checking `sensors` output for labels, units, channel count, and one-second cache behavior. Exercise `mutex_path=` override, boards using named mutexes and global lock, EC bank restore after repeated reads, and missing/failed ACPI lock paths. Regression checks should include DMI table additions, sensor family order, `find_ec_sensor_index()` channel mapping, and warnings during concurrent EC access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus-ec-sensors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus_atk0110.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/asus_atk0110.c

Purpose: legacy ASUS ATK0110 ACPI hwmon driver. It exposes ACPI-enumerated voltage, temperature, and fan sensors through manually built sysfs groups and supports both the old per-class ACPI methods and the newer GGRP/GITM/SITM multiplexed interface.

Important APIs, types, and functions: `atk_data` tracks ACPI handles, interface type, EC enable state, sensor counts, debugfs state, and attribute groups. `atk_sensor_data` stores per-sensor sysfs attributes, ACPI ID/type/limits, cached value, validity, and label. `validate_hwmon_pack()` validates old/new ACPI package layouts; `atk_get_pack_member()` hides layout offsets. `atk_read_value_old()` calls RTMP/RVLT/RFAN methods; `atk_ggrp()`, `atk_gitm()`, and `atk_sitm()` implement the new ACPI enumerate/read/write calls. `atk_add_sensor()`, `atk_enumerate_old_hwmon()`, and `atk_enumerate_new_hwmon()` build sensor lists. Debugfs helpers expose raw GITM/GGRP inspection when enabled.

Control flow: init first rejects unsafe ACPI resource enforcement and applies a DMI force-new-interface quirk. Probe gets the ACPI handle, optionally reads the board ID, probes available methods, chooses old or new interface, enumerates enabled sensors, creates four sysfs attributes per sensor (`input`, `label`, two limits), registers an `atk0110` hwmon device, and initializes debugfs. New-interface enumeration may enable the ATK EC before reading hwmon groups and remember to disable it during remove if it was previously off.

State and persistence: each sensor caches a value for `CACHE_TIME` (`HZ`) in `cached_value`, guarded by per-sensor validity timestamps but without a global mutex around all sensors. The driver may change device state by enabling/disabling the ATK EC during new-interface probe and removal. `new_if` is a module parameter that overrides method selection.

Dependencies and integration points: depends on ACPI platform matching for HID `ATK0110`, hwmon group registration, debugfs, DMI quirks, and ACPI method return formats. The code uses classic `hwmon_device_register_with_groups()` rather than the newer `hwmon_ops` channel-info model.

Risks: ACPI package validation must match firmware quirks; new and old interfaces can both exist but the new one may be broken, hence the heuristic. Limit interpretation differs between interfaces (`limit2` is a delta in new mode). New-interface EC enable/disable behavior can affect firmware-visible state if probe or remove paths fail. Debugfs raw reads can compete with normal hwmon reads. The code trusts package string lifetimes only after duplicating names with devm memory.

Test signals: probe old-interface boards, new-interface boards, and DMI-force-new boards. Verify voltage/temp/fan channel numbering and limit scaling, one-second cache reuse, disabled sensors being skipped, EC re-disable on unload, and error returns for malformed ACPI packages. `acpi_enforce_resources` settings and debugfs GITM/GGRP paths are important smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus_atk0110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus_rog_ryujin.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/asus_rog_ryujin.c

Purpose: HID hwmon driver for the ASUS ROG Ryujin II 360 AIO cooler. It reports coolant temperature, pump/internal/controller fan speeds, and exposes writable PWM duty controls for pump, internal fan, and controller fans.

Important APIs, types, and functions: `rog_ryujin_data` stores HID device pointers, hwmon device, completions for each command/response class, cached temp/speed/duty arrays, a shared report buffer, and update timestamp. `rog_ryujin_execute_cmd()` reinitializes a selected completion under `status_report_request_lock`, sends a padded output report, and waits up to `STATUS_VALIDITY`. `rog_ryujin_get_status()` sequences four GET commands. `rog_ryujin_raw_event()` parses response headers and updates cached arrays. `rog_ryujin_read()`, `rog_ryujin_read_string()`, and `rog_ryujin_write()` implement hwmon callbacks.

Control flow: late init registers the HID driver for ASUS vendor/product IDs. Probe parses and starts HID with hidraw enabled, opens the device, allocates the report buffer, initializes completions, and registers `rog_ryujin` hwmon. A read refreshes all status groups when the 1.5-second cache expires. A PWM write for pump/internal fan first reads current cooler duty because those two values are set in one command, modifies one field, and waits for a set completion; controller fan duty writes directly.

State and persistence: temperature, RPM, and duty values are cached in memory until the refresh window expires. The driver does not persist settings across unload or suspend. After controller-duty writes, `duty_input[channel]` is pinned to the requested value until the next refresh. Completions represent in-flight command state and are also affected by hidraw traffic.

Dependencies and integration points: depends on HID output reports/raw events, hwmon core, completions, spinlocks, jiffies, and unaligned little-endian loads. It deliberately enables `HID_CONNECT_HIDRAW` so existing user-space tools can coexist, although that increases response ambiguity.

Risks: the protocol has ambiguous zero-duty reports because the device uses zero fields as write acknowledgements; the driver tries to distinguish expected read versus write completions. Concurrent hidraw users can trigger raw events and complete requests, so the spinlock/reinit scheme is critical. No mutex serializes all command sequences, so overlapping sysfs reads/writes could interleave commands. Channel 2 set command stores raw PWM while cooler channels convert to percent, so conversion consistency is a regression risk.

Test signals: test with actual Ryujin II 360 hardware, reading all labels and channels, writing 0/255/mid PWM values to each channel, and running concurrent hidraw traffic. Verify timeout behavior when the device is unplugged or silent, zero-duty read/write ambiguity, and cleanup through `hid_hw_close()`/`hid_hw_stop()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus_rog_ryujin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus_wmi_sensors.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/asus_wmi_sensors.c

Purpose: ASUS Ryzen-era motherboard hwmon driver that enumerates sensors through the ASUS WMI monitoring GUID and exposes them as hwmon voltage, temperature, fan, current, and water-flow channels.

Important APIs, types, and functions: `asus_wmi_sensor_info` stores WMI ID, class, location, name, source, type, and cached value. `asus_wmi_wmi_info` holds per-source timestamps, channel tables by hwmon type, and an `info_by_id` lookup. `asus_wmi_call_method()` wraps `wmi_evaluate_method()`. `asus_wmi_get_version()`, `asus_wmi_get_item_count()`, `asus_wmi_sensor_info()`, `asus_wmi_update_buffer()`, and `asus_wmi_get_sensor_value()` implement the firmware protocol. `asus_wmi_configure_sensor_setup()` enumerates sensors twice to count and then allocate/populate hwmon channel tables.

Control flow: the WMI driver probes only when the ASUS monitoring GUID is present and the board matches the DMI allowlist. Probe checks interface version and sensor count, initializes the cache mutex, enumerates supported sensor classes, builds channel info arrays and sensor pointers, then registers `asus_wmi_sensors`. Reads fetch the sensor pointer for type/channel, refresh all sensors sharing that sensor source once per second using QWEC then RWEC reads, scale units, and return labels from firmware names.

State and persistence: cached values live in each `asus_wmi_sensor_info`, with `source_last_updated[source]` controlling refresh granularity. The mutex protects cache updates. No persistent hardware configuration is written; the driver is read-only.

Dependencies and integration points: depends on WMI, ACPI object parsing, DMI board matching, hwmon core, mutexes, jiffies, and unit helpers. The driver maps ASUS firmware sensor classes to hwmon classes and assumes source IDs fit the fixed `source_last_updated[3]` array.

Risks: firmware packages must have exactly five elements and valid string/integer types. Unsupported or new sensor classes are ignored. `source` values outside the small timestamp array would be unsafe if firmware returns unexpected data. Enumeration is performed twice and failed second-pass sensor reads are skipped, which can reduce channel population relative to initial counts. Unit scaling assumes WMI voltage is microvolts, temperature Celsius, current amperes, and fans/flow already hwmon-ready.

Test signals: use DMI-allowed ASUS X370/X470/B450/X399 boards; verify version >= 2, sensor count, names, channel order, source-specific cache refresh, and WMI error handling. Tests should simulate malformed ACPI objects, unsupported classes, changing sensor counts, and source IDs. Compare reported values against firmware/BIOS tools for scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/asus_wmi_sensors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/atxp1.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/atxp1.c

Purpose: I2C hwmon/sysfs driver for the Attansic ATXP1 chip, providing CPU VID voltage control and two GPIO data registers. The chip is not autodetected and must be instantiated explicitly.

Important APIs, types, and functions: `atxp1_data` stores the I2C client, cache mutex, one-second validity state, cached register bytes, and detected VRM version. `atxp1_update_device()` reads VID, CPU VID, GPIO1, and GPIO2 via SMBus byte reads. `cpu0_vid_show()`/`cpu0_vid_store()` convert between millivolts and VID register values using `hwmon-vid`. `gpio1_show/store()` and `gpio2_show/store()` expose hex GPIO values. Probe checks `vid_which_vrm()` for VRM 9.0/9.1 support and registers `atxp1_groups`.

Control flow: module_i2c_driver registers an `atxp1` I2C driver. Probe allocates state, checks the CPU VRM, initializes the update mutex, and registers hwmon attributes. Reads refresh the register cache if stale. Writes parse user input, write changed register values over SMBus, and invalidate the cache.

State and persistence: register values are cached for up to one second in `data->reg`. Writes persist in the hardware until changed externally or reset. CPU VID writes are stepped one VID code at a time to improve stability and enable ATXP1 output with `ATXP1_VIDENA`.

Dependencies and integration points: depends on explicit I2C device instantiation, SMBus byte-data operations, hwmon group registration, `hwmon-vid` VRM conversion helpers, and sysfs attributes. There is no device-tree match table or automatic detection.

Risks: changing CPU VID is inherently risky and can destabilize hardware. `atxp1_update_device()` does not check negative SMBus read errors before assigning to `u8` cache fields. `last_updated` is never updated in the function, so cache validity does not actually throttle reads despite the intended design. GPIO2 write log incorrectly says GPIO1. Unsupported VRM versions refuse probe.

Test signals: instantiate on known ATXP1 hardware at supported addresses, verify VID conversion and stepped writes with safe values, verify GPIO masks and cache invalidation after writes, and test SMBus error behavior. Static tests should catch the missing `last_updated = jiffies` update and misleading GPIO2 log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/atxp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/axi-fan-control.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/axi-fan-control.c

Purpose: platform hwmon driver for Analog Devices AXI Fan Control HDL core. It exposes PWM duty, fan RPM/fault, die temperature, and programmable automatic PWM temperature thresholds.

Important APIs, types, and functions: `axi_fan_control_data` stores MMIO base, hwmon device, clock rate, IRQ, pulses-per-revolution, and IRQ-derived state flags. `axi_ioread()`/`axi_iowrite()` wrap register access. `axi_fan_control_get_pwm_duty()` and `axi_fan_control_set_pwm_duty()` convert between sysfs PWM 0-255 and core PWM width/period registers. `axi_fan_control_get_fan_rpm()` converts tach period to RPM using clock rate and PPR. `axi_fan_control_irq_handler()` handles PWM changes, tach errors, temperature-triggered changes, and new measurements. Extra threshold attributes are built with `SENSOR_DEVICE_ATTR_RW`.

Control flow: probe matches a device-tree compatible, maps registers, enables the clock, verifies AXI core major version, reads `pulses-per-revolution`, unmasks selected interrupts, releases reset, registers hwmon with extra groups, then requests a threaded IRQ. Reads and writes are direct MMIO operations. IRQs update software flags, notify hwmon on hardware PWM changes, update tach reference/tolerance after software PWM changes, and latch fan fault until read.

State and persistence: hardware registers hold PWM width, threshold points, tach period/tolerance, and reset/IRQ state. Software state includes `fan_fault` latch cleared on `fan1_fault` read, `hw_pwm_req` to distinguish automatic core changes, and `update_tacho_params` to defer tach parameter updates until a fresh measurement. No cache is used for normal values.

Dependencies and integration points: depends on platform/OF matching, `adi-axi-common.h` version macros, MMIO I/O, clocks, interrupts, hwmon core, and device properties. It integrates with hwmon notifications and exposes nonstandard auto-point attributes as sysfs groups.

Risks: code trusts `PWM_PERIOD` is nonzero. RPM math depends on valid clock rate and PPR property. IRQ comments mention hardware stabilization delays and distinguish software versus automatic PWM changes; missed or reordered IRQs could leave tach parameters stale. Threshold conversion uses two formulas in different paths (`show/store` versus input temperature read), so unit consistency deserves attention. `fan_fault` is not protected by a lock.

Test signals: test device-tree probe with valid/invalid PPR and version mismatch, read/write PWM endpoints and auto thresholds, verify RPM against known tach signal, induce tach error and confirm `fan1_fault` latch clears, and confirm hwmon notification on hardware-driven PWM changes. IRQ path testing should cover software PWM update followed by new measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/axi-fan-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/cgbc-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/cgbc-hwmon.c

Purpose: hwmon child driver for Congatec Board Controller devices. It discovers controller-reported sensors and exposes active temperature, voltage, current, and fan channels with fixed labels.

Important APIs, types, and functions: `cgbc_hwmon_sensor` records hwmon type, active flag, controller index/channel, and label. `cgbc_hwmon_data` links to the parent `cgbc_device_data` and discovered sensor array. `cgbc_hwmon_cmd()` sends board-controller command `0x77`. `cgbc_hwmon_probe_sensors()` asks sensor zero for the total count, then decodes each sensor's type, ID, active bit, and label. `cgbc_hwmon_find_sensor()` maps hwmon type/channel to discovered sensor, including current channels offset after voltage channels. `cgbc_hwmon_read()`, `is_visible()`, and `read_string()` implement hwmon callbacks.

Control flow: as a platform child, probe gets the parent MFD data, allocates driver state, probes the controller sensor table, then registers `cgbc_hwmon`. Visibility hides inactive or unknown sensors. Reads issue a fresh controller command for the sensor index and convert little-endian data bytes into a value; temperatures convert 0.1 degree C units to hwmon millidegrees.

State and persistence: discovered sensor metadata is stored once during probe. Read values are not cached and are fetched from the board controller each time. No writable hardware state is exposed.

Dependencies and integration points: depends on the Congatec MFD core (`linux/mfd/cgbc.h` and `cgbc_command()`), platform-device child creation, hwmon core, and bitfield helpers. Channel labels are compiled in and indexed by controller channel IDs.

Risks: `cgbc_hwmon_read()` and `read_string()` assume visibility has found a sensor; direct callback calls with missing mappings would dereference NULL. Controller channel IDs are decremented, so a returned ID of zero underflows the unsigned channel variable. The static hwmon channel arrays define maximum visible channels; controller firmware returning more valid sensors than arrays support will be ignored. No cache means frequent sysfs polling can generate many controller transactions.

Test signals: test with board controllers returning valid active/inactive temp, voltage, current, and fan entries; unknown type/channel warnings; zero/invalid IDs; and command failures. Verify current channel offset mapping, labels, temperature scaling, and that inactive sensors are hidden.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/cgbc-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/chipcap2.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/chipcap2.c

Purpose: I2C hwmon driver for Amphenol ChipCap 2 humidity/temperature sensors. It supports on-demand measurements, optional ready and alarm IRQs, humidity alarm threshold registers, and regulator-controlled power cycling.

Important APIs, types, and functions: `cc2_data` stores alarm state, completion, hwmon device, I2C client, exclusive `vdd` regulator, IRQ numbers, and IRQ processing flag. Conversion helpers `cc2_rh_convert()`, `cc2_rh_to_reg()`, and `cc2_temp_convert()` translate raw humidity and temperature. `cc2_enable()`/`cc2_disable()` control power and IRQ acceptance. `cc2_command_mode_start()` enters the sensor's startup-only command window with retries, and `cc2_read_reg()`/`cc2_write_reg()` access EEPROM alarm registers. `cc2_measurement()` performs enable-wait-read-disable measurement cycles. IRQ handlers complete ready events and latch/notify humidity alarms.

Control flow: probe requires raw I2C functionality, obtains the exclusive regulator, optionally requests named `ready`, `low`, and `high` IRQs, then registers temp and humidity hwmon channels. Normal reads power the device, wait for automatic measurement via IRQ or sleep, fetch four measurement bytes, validate status, convert the requested type, and power off. Alarm threshold reads enter command mode; alarm status reads combine hysteresis register reads with a fresh measurement to determine whether a latched alarm remains active. Writes validate 0..100000 permille humidity values, enter command mode, write EEPROM, wait for acknowledgement, then power off.

State and persistence: humidity alarm threshold/hysteresis writes persist in sensor EEPROM. The driver intentionally power-cycles for measurements and command-window retries. `rh_alarm.low_alarm` and `high_alarm` are software latches set by IRQ and cleared only after status reads observe recovery across hysteresis. No measurement cache is maintained.

Dependencies and integration points: depends on I2C master transfers/SMBus word writes, exclusive regulator control, fwnode named IRQs, hwmon, completions, hwmon event notifications, and OF/I2C ID tables for CC2D variants. Named IRQs are optional; sleep-based fallback is used without ready IRQ.

Risks: command mode is only available during a short startup window, so regulator timing and retry logic are critical. `cc2_cmd_response_diagnostic()` tries to inspect error bits through `resp`, but `resp` is the low two response bits after `FIELD_GET`, making the EEPROM/RAM/config diagnostics ineffective. Some error paths in `cc2_read_reg()` return without disabling the regulator, relying on callers inconsistently; this can leave the device powered. Alarm IRQs during power transitions are suppressed by `process_irqs`, but race timing remains important. EEPROM writes have wear and latency implications.

Test signals: test both IRQ and polling modes, regulator enable/disable sequencing, command-window retries, stale-data handling, humidity/temp conversion boundaries, alarm threshold writes/readbacks, and alarm notification/status clearing across hysteresis. Fault injection should cover I2C short reads, NACK/busy command status, missing regulator, and timeout paths that must disable power.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/chipcap2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/coretemp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/coretemp.c

Purpose: Intel CPU digital thermal sensor hwmon driver. It creates per-package platform devices and per-package/per-core temperature sysfs attributes based on CPU hotplug state and MSR readings.

Important APIs, types, and functions: `temp_data` holds one package or core temperature source, cached temperature, TjMax, target CPU, MSR register, generated sysfs attributes, and update mutex. `platform_data` represents a physical package/die with hwmon device, package ID, online CPU mask, core `ida`, package data, and core data pointers. `get_tjmax()`, `adjust_tjmax()`, and `get_ttarget()` determine critical and target temperatures through MSRs, PCI/model tables, or `tjmax=` override. `create_core_attrs()` creates `tempN_label`, `crit_alarm`, `input`, `crit`, and optional `max` sysfs attributes. CPU hotplug callbacks add/remove or retarget core/package data.

Control flow: init checks Intel DTS CPU match, allocates a zone device array sized by packages times dies, creates platform devices for each zone, and registers CPU hotplug callbacks. On CPU online, it checks CPUID thermal sensor support and microcode errata, registers the package hwmon device if this is the first online CPU in the package, adds package temp if supported, and adds a core temp only if no sibling thread already represents that core. On CPU offline, it removes a core when the last sibling leaves or retargets reads to another sibling, and unregisters hwmon when the package is empty.

State and persistence: temperatures are cached per `temp_data` for one second. `tjmax` may be permanently cached when forced or derived heuristically; a zero `tjmax` means dynamic MSR TjMax remains available. Sysfs attributes are dynamically created and removed according to hotplug state. No hardware state is written.

Dependencies and integration points: depends on x86 CPU feature matching, MSR reads on target CPUs, topology package/die/core/sibling masks, CPU hotplug framework, platform devices, hwmon sysfs groups, PCI host bridge lookup for TjMax quirks, and housekeeping CPU isolation checks.

Risks: TjMax heuristics for old CPUs can be inaccurate, and the driver explicitly warns when using relative scales. Hotplug handling must avoid dangling sysfs attributes while retargeting sibling CPUs. `NUM_REAL_CORES` is a hardcoded allocation limit pending better topology information. Reads use `rdmsr_on_cpu()` in some paths without explicit error handling after initial validation. Isolated non-housekeeping CPUs are skipped, affecting visibility on tuned systems.

Test signals: test on Intel CPUs with and without package temperature support, SMT on/off, CPU online/offline cycles, suspend/resume frozen hotplug, forced `tjmax=` parameter, and older Atom/Core2 quirk paths. Verify sysfs numbering (`temp1` package, `core_id + 2` cores), `crit_alarm`, one-second cache, and removal when the last package CPU goes offline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/coretemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/corsair-cpro.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/corsair-cpro.c

Purpose: HID hwmon driver for Corsair Commander Pro and Corsair 1000D controllers. It exposes connected temperature probes, fan RPMs, fan PWM/target controls, and voltage rails while keeping hidraw access available.

Important APIs, types, and functions: `ccp_device` stores HID/hwmon/debugfs pointers, command and response buffers, completion/spinlock for report waits, a mutex serializing command buffer usage, fan target cache, connection bitmaps, labels, and firmware/bootloader versions. `send_usb_cmd()` builds 63-byte output reports, reinitializes completion under spinlock, sends the command, waits for a 16-byte response, and maps device status bytes via `ccp_get_errno()`. `ccp_raw_event()` copies one pending input report. `get_data()`, `set_pwm()`, and `set_target()` implement common protocol operations. Probe reads connection status and versions before hwmon registration.

Control flow: late init registers the HID driver. Probe allocates buffers, parses/starts/opens HID with hidraw, initializes synchronization, starts HID I/O, reads temp and fan connection bitmaps, creates debugfs version files, and registers `corsaircpro`. Visibility depends on connection bitmaps. Reads send command-per-value requests; writes convert PWM 0-255 to device percent or set fan target RPM. Fan target reads return only the last value set by this driver.

State and persistence: connection status is sampled once at probe and does not update until reprobe. Firmware/bootloader versions are cached for debugfs. `target[channel]` is a software-only cache initialized to `-ENODATA` and invalidated by fixed PWM writes. Hardware fan settings persist in the device until changed, but the driver does not restore state.

Dependencies and integration points: depends on HID output reports/raw events, hwmon info API, debugfs, completions, mutexes, spinlocks, and bitmaps. Hidraw remains enabled, and comments note simultaneous userspace may switch reports.

Risks: hidraw concurrency can consume or inject reports for the driver's pending command. Connection status is only accurate at power-on/probe. Reads have no caching, so frequent polling issues many HID commands. Fan target readback is not supported by protocol and may mislead users after external changes. Error code mapping depends on the first response byte only.

Test signals: test Commander Pro and 1000D IDs, connected/disconnected temp and fan channels, 3-pin/4-pin labels, PWM endpoint conversion, target writes/readbacks, voltage rails, debugfs version files, timeout and wrong-size report handling, and concurrent hidraw traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/corsair-cpro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/corsair-psu.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/corsair-psu.c

Purpose: HID hwmon driver for Corsair HXi/RMi/HX-series PSUs with a proprietary sensor protocol. It reports input/output voltages, currents, power, temperatures, fan RPM/PWM, and selected critical thresholds, plus debugfs metadata and uptime.

Important APIs, types, and functions: `corsairpsu_data` stores HID/hwmon/debugfs pointers, completion, command buffer, vendor/product strings, cached critical thresholds, support bitmasks, and input-current command support. `corsairpsu_usb_cmd()` sends a 64-byte report, waits for a raw-event completion, validates command echo, and copies reply data. `corsairpsu_request()` selects rails before rail-specific commands. `corsairpsu_get_value()` handles little-endian reply assembly and LINEAR11 conversion. `corsairpsu_get_criticals()` and `corsairpsu_check_cmd_support()` populate feature state. `corsairpsu_hwmon_ops_*` implement visibility, reads, and labels.

Control flow: late init registers the HID driver. Probe parses/starts/opens HID, initializes completion, starts HID I/O, sends the special init command, queries firmware strings, probes thresholds and supported commands, registers `corsairpsu`, and initializes debugfs. Each hwmon read sends the appropriate PSU command, selecting a rail first when needed. Debugfs reads uptime, total uptime, vendor, product, and OCP mode. Resume reissues the init command because some PSUs power down the controller in standby.

State and persistence: threshold values and support bitmasks are cached at probe. Current sensor values are not cached. The driver is read-only for hwmon; it deliberately does not expose OCP mode switching because it is considered dangerous. Resume restores only protocol initialization, not cached threshold refresh.

Dependencies and integration points: depends on HID reports/raw events, hwmon channel info, debugfs, completions, PM resume hooks, and LINEAR11 conversion for PMBus-like values. Supported products are listed by USB VID/PID.

Risks: there is no mutex around `cmd_buffer` and completion use, so concurrent hwmon/debugfs reads can race command/response state. Hidraw is available by raw events and can interfere similarly. Visibility for temp channel 0 exposes `temp_crit` even though support bit checks apply only channel > 0, so unsupported critical values may appear as zero. Command support differs by PSU class, and unsupported commands are detected by echo mismatch. LINEAR11 conversion and rail selection must be correct to avoid misleading units.

Test signals: test all listed product IDs where possible, unsupported command handling, rail-specific values and labels, cached critical visibility, debugfs uptime/vendor/product/OCP mode, suspend/resume init, and concurrent reads from hwmon plus debugfs/hidraw. Unit checks should compare volts/currents/power/fan values against vendor tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/corsair-psu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/cros_ec_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/cros_ec_hwmon.c

Purpose: ChromeOS EC hwmon platform driver. It exposes EC temperature sensors, fan speeds/faults/targets, PWM duty/mode controls, thermal thresholds, and registers EC fans as thermal cooling devices when supported.

Important APIs, types, and functions: `cros_ec_hwmon_priv` stores the EC pointer, discovered temperature sensor names, usable fan bitmask, command-support booleans, and manual fan state saved for suspend. `cros_ec_hwmon_read_fan_speed()`, `read_pwm_value()`, `read_pwm_enable()`, `read_fan_target()`, `read_temp()`, and `read_temp_threshold()` wrap EC memory map or EC commands. `cros_ec_hwmon_probe_temp_sensors()` discovers sensor labels, `cros_ec_hwmon_probe_fans()` discovers usable fans, and `cros_ec_hwmon_probe_fan_control_supported()` checks command versions. Thermal cooling callbacks reuse PWM read/write helpers.

Control flow: probe obtains the parent `cros_ec_dev`, reads thermal version from EC memory, rejects version zero, discovers temps/fans and optional feature support, registers cooling devices for controllable fans, then registers the `cros_ec` hwmon device. Reads branch by hwmon type and attribute, converting EC special error values to `-ENODATA` or fault booleans. PWM writes support manual duty only when the EC fan is already in manual mode and mode writes switch between manual and auto. Suspend records manual PWM settings; resume restores manual PWM values, which also switches fans back to manual.

State and persistence: discovery state is stored at probe. Sensor values are read live from EC memory or commands, with no cache. `manual_fans` and `manual_fan_pwm[]` persist across system suspend/resume in driver memory to restore manual control. EC itself may reset fan control to automatic during suspend.

Dependencies and integration points: depends on ChromeOS EC protocol/memory map, platform child registration, hwmon, thermal cooling framework, command version discovery, unit conversion from EC Kelvin offsets, and optional PM callbacks.

Risks: `pwm_input` writes reject auto mode, so users must set `pwm_enable=1` first. `fan_target` visibility calls the EC from `is_visible()`, which may be relatively expensive and can hide only on `-EOPNOTSUPP`. `manual_fan_pwm` is sized by `EC_FAN_SPEED_ENTRIES`, while `manual_fans` is a `u8`, so assumptions about fan count matter. Sensor labels are absent if info commands fail, hiding otherwise readable sensors. Resume restoration may fail partially.

Test signals: test EC thermal versions before and after v2, boards with no fans, multiple fans, unsupported PWM commands, temp thresholds, fan target unsupported, error sentinel values for fans/temps, cooling-device registration, and suspend/resume preserving manual fan settings. Verify labels from `EC_CMD_TEMP_SENSOR_GET_INFO` and Kelvin-to-millicelsius conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/cros_ec_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/da9052-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/da9052-hwmon.c

Purpose: platform hwmon driver for the Dialog DA9052 PMIC/MFD. It exposes PMIC ADC channels for voltages, charge current, battery and junction temperatures, optional touchscreen-interface ADC channels, and labels through static sysfs attributes.

Important APIs, types, and functions: `da9052_hwmon` stores the parent `da9052`, a hwmon mutex, `tsi_as_adc` mode, TSI reference millivolts, and a completion for TSI conversion. Conversion helpers map ADC register values to millivolts or millidegrees. Channel show functions call parent MFD ADC/register helpers (`da9052_adc_manual_read()`, `da9052_adc_read_temp()`, `da9052_reg_read()`, `da9052_group_read()`). `da9052_request_tsi_read()`, `__da9052_read_tsi()`, and `da9052_tsi_datardy_irq()` manage TSI manual conversions. `da9052_channel_is_visible()` hides TSI ADC attributes unless configured.

Control flow: probe allocates state, gets the parent MFD pointer, reads the parent property `dlg,tsi-as-adc`, optionally enables and validates `tsiref`, disables touchscreen features, configures ADC mode, and requests the DA9052 TSI ready IRQ. It then registers the static `da9052` hwmon groups. Reads are direct register/ADC operations; VDDOUT temporarily enables/disables an automatic channel under `hwmon_lock`, while TSI reads request conversion and wait up to 500 ms for completion.

State and persistence: most values are live reads with no cache. Probe may persistently reconfigure the PMIC touchscreen/ADC mode when `tsi_as_adc` is true. TSI reference voltage is stored in driver state for scaling. The TSI IRQ is explicitly freed on remove or registration failure.

Dependencies and integration points: depends on the DA9052 MFD core, DA9052 register definitions, regulator API for `tsiref`, platform devices, hwmon sysfs attributes, and parent device properties. It uses the legacy static attribute-group hwmon registration style.

Risks: static channel numbers are sparse (`in70`..`in73`) for TSI channels and may surprise userspace. Some register writes in probe (`TSI_CONT_A`, ADC mode) do not check errors. VDDOUT enable/disable has careful cleanup, but failure to disable is surfaced only as read error. TSI conversion depends on the PMIC interrupt; timeout returns `-ETIMEDOUT`. `da9052_tjunc_show()` uses trim register math that must match hardware calibration.

Test signals: test with and without `dlg,tsi-as-adc`, valid and invalid `tsiref` voltages, TSI IRQ completion and timeout, VDDOUT enable/disable cleanup, ADC channel scaling, label visibility, and remove/error-path IRQ freeing. Compare PMIC voltage/temp readings to known rails and battery data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/da9052-hwmon.c -->
