# Research Report: subset-b-003839

Grouped research for hwmon drivers under `sources/distributed-fs/ceph-client/drivers/hwmon`. Each section is source-tree aligned for reconciliation into per-file research artifacts.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp464.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tmp464.c

## Purpose
Texas Instruments TMP464/TMP468 I2C hwmon driver for one local and 4 or 8 remote temperature channels. It exposes temperature inputs, thresholds, hysteresis, critical limits, remote-open faults, labels, per-channel enable controls, offsets, and chip update interval through the modern `devm_hwmon_device_register_with_info()` API.

## Important APIs, Types, and Functions
`struct tmp464_data` stores the regmap, channel count, original config, cached remote-open status, update interval, and per-channel labels/enabled flags. `tmp464_ops` implements hwmon `.is_visible`, `.read`, `.read_string`, and `.write`. Conversion helpers map TMP464 fixed-point temperature registers to millidegrees and back. `tmp464_init_client()` handles lock/unlock, saves/restores the original config with devm actions, sets a 500 ms conversion rate, clears shutdown, and enables channels. `tmp464_detect()` supports legacy I2C class probing by checking manufacturer/device IDs and status reserved bits. DT support is split across `tmp464_probe_from_dt()` and `tmp464_probe_child_from_dt()`.

## Control Flow
Probe validates SMBus word support, allocates state, derives channel count from I2C/OF match data, initializes an endian-aware cached regmap, defaults all channels enabled, initializes the chip, then overlays DT channel configuration if present before registering hwmon. Runtime reads dispatch by sensor type. Fault reads cache `TMP464_REMOTE_OPEN_REG` for one measurement interval because the hardware clears that register on read. Writes update thresholds, offsets, channel enables, and conversion rate through regmap operations.

## State and Persistence
Persistent hardware state is limited to registers changed by the driver: lock state and config are restored automatically on driver teardown. Channel labels and enable states live in RAM after probe; enable changes are also written to config REN bits. Fault state is cached using `last_updated`/`valid` to avoid losing read-clear open-circuit flags. Regmap uses maple cache but volatile temperature/status registers bypass stale caching.

## Dependencies and Integration Points
Depends on I2C SMBus word transactions, regmap with big-endian 16-bit values, Linux hwmon channel-info APIs, OF child nodes named `channel`, and optional I2C class detection at addresses `0x48`-`0x4b`. DT properties include `reg`, `label`, `status`, and `ti,n-factor`.

## Risks
Channel enable changes update RAM before writing hardware; a failed `tmp464_enable_channels()` leaves in-memory enable state ahead of hardware. DT `ti,n-factor` validation rejects local-channel use and out-of-range signed values, but bad board data can still make readings misleading. Hysteresis is global in hardware, so `temp*_max_hyst` writes on any channel are effectively derived from channel 0 max. Fault caching depends on `update_interval`; conversion-rate changes alter cache lifetime.

## Test Signals
Check probe on TMP464 and TMP468 IDs, DT child parsing for disabled channels/labels/n-factor, sysfs visibility for channels beyond TMP464's count, remote fault read-clear caching across update intervals, update interval clamping from 125 to 16000 ms, threshold conversion edge values, and cleanup restoration of lock/config registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp464.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp513.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tmp513.c

## Purpose
Driver for TI TMP512/TMP513 thermal and power monitors. It exposes local/remote temperature channels, bus voltage, shunt-derived current, bus current, power, limit registers, alarms, and temperature hysteresis through modern hwmon callbacks.

## Important APIs, Types, and Functions
`struct tmp51x_data` carries shunt config, PGA gain, bus range, n-factor array, shunt value, derived current/power LSBs, channel count, and regmap. `tmp51x_get_value()` and `tmp51x_set_value()` implement register-to-hwmon conversions for status flags, current, voltage, power, temperature, and hysteresis. `tmp51x_get_reg()` and `tmp51x_get_status_pos()` map hwmon attributes to registers/status bits. `tmp51x_calibrate()` computes the calibration register and LSB scaling from shunt resistance and PGA range. `tmp51x_read_properties()` parses firmware properties.

## Control Flow
Probe allocates state, determines TMP512 versus TMP513 channel count, configures defaults or firmware properties, creates the I2C regmap, initializes shunt/temp/n-factor/calibration registers, reads status once as recommended, then registers hwmon. Read/write callbacks resolve a register for the requested sensor attribute, perform regmap I/O, and convert values. Visibility hides current and power if the configured shunt is zero and hides channel 3 on TMP512.

## State and Persistence
The driver programs TMP51x configuration and calibration at probe and keeps derived LSB values in memory. Limit writes persist in device registers until hardware reset or later writes. No runtime cache is used for measurement values. If `shunt-resistor-micro-ohms` is zero, calibration is set to zero and current/power channels are hidden while temperature/voltage continue.

## Dependencies and Integration Points
Uses I2C, regmap, device properties/OF compatible strings `ti,tmp512` and `ti,tmp513`, `linux/units.h` scaling constants, and hwmon channel-info APIs. Firmware properties include `shunt-resistor-micro-ohms`, `ti,bus-range-microvolt`, `ti,pga-gain`, and `ti,nfactor`.

## Risks
Current and power accuracy depends on board shunt data and PGA gain. Property validation rejects impossible bus ranges, PGA gains, and shunts larger than the PGA full-scale sense voltage, but defaulting can silently produce wrong readings on boards with non-default shunts. Arithmetic uses mixed signed/unsigned conversion; tests should cover negative shunt current and limit edge cases. `tmp51x_get_reg()` returns zero for unsupported mappings, which is safe because register zero is not exposed as a readable hwmon data register.

## Test Signals
Test TMP512/TMP513 visibility differences, zero-shunt behavior, calibration calculations for each supported PGA, bus range limit clamping, signed shunt current conversion, temperature hysteresis masking in `N_FACTOR_AND_HYST_1`, property parse errors, and alarm bit mapping for all status-backed attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp513.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tps23861.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tps23861.c

## Purpose
I2C hwmon driver for the TI TPS23861 Power-over-Ethernet PSE controller. It reports die temperature, four per-port voltages and currents, input voltage, labels, and write-only per-port enable control. It also provides debugfs port status decoding for operating mode, detection, class, PoE Plus state, and measured resistance.

## Important APIs, Types, and Functions
`struct tps23861_data` stores the 8-bit regmap, shunt-resistor selection, and client. `tps23861_read_temp()`, `tps23861_read_voltage()`, and `tps23861_read_current()` convert raw device registers with datasheet LSBs. `tps23861_port_enable()` and `tps23861_port_disable()` write command registers. `tps23861_hwmon_ops` implements visibility, read, write, and label callbacks. Debugfs helpers convert status/class/detect fields into text and `tps23861_port_status_show()` emits a per-port report.

## Control Flow
Probe allocates state, initializes regmap, reads optional `shunt-resistor-micro-ohms`, programs the general mask bit to select 250 or 255 mOhm current scaling, registers the hwmon device, and creates `debugfs/port_status` under the I2C client debugfs directory. Runtime reads bulk-read little-endian two-byte measurement registers. Writes to `in[1-4]_enable` dispatch to enable or disable commands, while invalid values are rejected.

## State and Persistence
The driver maintains only shunt selection and regmap pointer in RAM. Port enable/disable actions are immediate hardware commands rather than cached state; there is no readable enable state. Debugfs status reads reflect current hardware registers and do not cache. Shunt selection is written during probe and persists in the chip until changed/reset.

## Dependencies and Integration Points
Uses I2C, regmap, hwmon, OF property parsing, bitfield helpers, and debugfs. It expects compatible `ti,tps23861` and optionally `shunt-resistor-micro-ohms`. The hwmon chip channel includes `HWMON_C_REGISTER_TZ`, enabling thermal-zone registration.

## Risks
The driver only distinguishes the default 255 mOhm shunt from all other values as 250 mOhm; arbitrary firmware values can select the alternate bit but still produce inaccurate scaling. Several debugfs regmap reads ignore errors, so status output can contain stale zero-like interpretations after bus failures. `in_enable` is write-only, which can surprise tests expecting round-trip state. Port control writes use command bits and must be verified against hardware side effects.

## Test Signals
Verify measurement scaling for default and non-default shunt modes, input-voltage channel index handling, invalid `in_enable` writes, per-port label strings, debugfs text for all detect/class enum values, regmap error propagation in hwmon reads, and probe behavior with absent OF property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tps23861.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tsc1641.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tsc1641.c

## Purpose
ST TSC1641 I2C power monitor driver. It exposes load voltage, bidirectional current, power, temperature, alert alarms, writable limits, update interval, and a custom `shunt_resistor` sysfs attribute.

## Important APIs, Types, and Functions
`struct tsc1641_data` stores current shunt resistance, derived current LSB, and regmap. Regmap writeability/volatility callbacks protect cached configuration while bypassing dynamic registers. `tsc1641_set_shunt()` programs the RSHUNT register and recalculates current scaling. `tsc1641_reg_to_upd_interval()` and `tsc1641_upd_interval_to_reg()` translate config conversion-time bits. Per-sensor read/write functions handle voltage, current, power, temperature, and flag-backed alarms. `DEVICE_ATTR_RW(shunt_resistor)` exposes runtime shunt adjustment.

## Control Flow
Probe creates a cached 16-bit regmap, calls `tsc1641_init()` to validate firmware shunt, set shunt/config/default alert mask and alert polarity, then registers hwmon with the extra shunt attribute group. Reads dispatch by hwmon type and often consult `TSC1641_FLAG` using `regmap_read_bypassed()` for current alert state. Writes clamp hwmon units to register ranges before programming limit registers.

## State and Persistence
The shunt value and derived current LSB are persistent driver state and are also written to hardware. Configuration, mask, and limits persist in the device registers. Measurement values are not cached by the driver, but regmap uses maple cache for nonvolatile registers. Updating `shunt_resistor` changes subsequent current interpretation and hardware scaling immediately.

## Dependencies and Integration Points
Depends on I2C, 16-bit regmap, hwmon channel-info APIs, sysfs attributes, and firmware properties. Compatible string is `st,tsc1641`; properties include `shunt-resistor-micro-ohms` and boolean `st,alert-polarity-active-high`.

## Risks
Changing shunt at runtime changes current scaling while existing current limit registers remain raw shunt-voltage-derived values; tests and users must account for semantic changes. Saturation handling returns `-ENODATA` for load voltage/current out-of-range cases based on flag and sentinel raw values. Conversion-time code intentionally clamps to 1-33 ms because hwmon cannot express sub-ms intervals. Alert flags are read bypassing regcache; bus errors must propagate cleanly.

## Test Signals
Cover shunt validation min/max, rounded RSHUNT programming, current and power conversions after shunt changes, update interval conversion nearest-match behavior, alert polarity mask programming, saturation `-ENODATA` paths, signed current limits, temperature disabled sentinel `0x8000`, and sysfs `shunt_resistor` store errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tsc1641.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ultra45_env.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ultra45_env.c

## Purpose
Platform hwmon driver for the Sun Ultra 45 PIC16F747 environmental monitor. It exposes fan speeds/setpoints, fan fault bits, several board temperatures, status bits, firmware version, and a legacy `name` attribute.

## Important APIs, Types, and Functions
`struct env` stores MMIO base, spinlock, and hwmon device. `env_read()` and `env_write()` serialize indirect register access through `REG_ADDR`/`REG_DATA`. Sysfs callbacks implement fan RPM conversion, fan speed writes, fan fault/status bits, temperature reads, firmware version, and name. `env_probe()` maps OF resources, creates a static sysfs attribute group, and registers hwmon.

## Control Flow
The OF platform driver matches `SUNW,ebus-pic16f747-env`. Probe allocates state, initializes the spinlock, maps the PIC register window with `of_ioremap()`, creates the custom sysfs group, registers the hwmon device, and stores drvdata. Reads and writes access indirect PIC registers under the spinlock except status/firmware direct register reads. Remove reverses sysfs, hwmon registration, and MMIO mapping.

## State and Persistence
No periodic cache is maintained. Fan speed writes persist in the environmental controller register. The only driver state is the mapped base and lock. Status/fault/temp reads reflect current controller data; the controller may independently mark data stale/busy/faulted through status bits exposed by sysfs.

## Dependencies and Integration Points
Depends on OF platform resources, MMIO accessors, legacy hwmon sysfs macros, and Sun EBus/OpenFirmware node naming. It uses `hwmon_device_register()` plus a manually created sysfs group rather than channel-info APIs.

## Risks
Temperature values are returned as whole degrees Celsius after subtracting 64, not millidegrees as modern hwmon convention expects for standard `temp*_input` names; attribute names are mostly board-specific legacy names. Fan conversion only stores the high byte of the period, limiting precision. Direct status reads are not spinlock-protected, though they do not use the indirect address register. Error unwinding is manual and must keep sysfs/hwmon/iounmap ordering correct.

## Test Signals
Validate OF match/probe/remove unwinding, sysfs file presence, fan RPM zero/invalid-period handling, rejecting zero RPM writes, spinlock coverage for indirect access, status bit mapping, firmware version upper-nibble extraction, and expected board-specific temperature naming/units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ultra45_env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/vexpress-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/vexpress-hwmon.c

## Purpose
ARM Versatile Express platform hwmon bridge. It exposes firmware/config-bus values as voltage, current, temperature, power, or energy sysfs attributes depending on OF compatible string.

## Important APIs, Types, and Functions
`struct vexpress_hwmon_data` stores the hwmon device and vexpress config regmap. `struct vexpress_hwmon_type` binds a hwmon name to attribute groups. `vexpress_hwmon_u32_show()` reads register 0 and divides by the per-attribute scale factor. `vexpress_hwmon_u64_show()` combines registers 1:0 for energy. `vexpress_hwmon_attr_is_visible()` hides labels when the OF node lacks `label`.

## Control Flow
Probe allocates state, retrieves match data for the compatible type, initializes the vexpress config regmap, and registers a hwmon device with the selected static attribute group. Runtime sysfs reads synchronously read one or two config registers and format scaled values. Label reads return the node's `label` property.

## State and Persistence
The driver keeps no measurement cache and writes no hardware state. All values come from the platform config regmap on demand. Attribute availability is fixed at probe by compatible type and at visibility time by the optional label property.

## Dependencies and Integration Points
Depends on platform OF matching, `devm_regmap_init_vexpress_config()`, legacy hwmon attribute groups, and `linux/vexpress.h`. Compatible strings include `arm,vexpress-amp`, `arm,vexpress-temp`, `arm,vexpress-power`, `arm,vexpress-energy`, and conditionally `arm,vexpress-volt` when the regulator driver is not configured.

## Risks
`vexpress_hwmon_label_show()` assumes visibility has hidden the label attribute when the property is absent; direct misuse would pass NULL to formatting. U64 energy reads are not atomic across low/high registers and can race rollover. Scaling is encoded in attribute indices, so mistakes in static attributes directly affect units. Voltage support is conditionally compiled to avoid conflict with the regulator driver.

## Test Signals
Check each compatible's hwmon name and attributes, label visibility with and without `label`, regmap error propagation, u32 scaling for milli-units, u64 high/low composition, and build coverage with `CONFIG_REGULATOR_VEXPRESS` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/vexpress-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/via-cputemp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/via-cputemp.c

## Purpose
x86 hwmon driver exposing VIA/Centaur CPU core temperature via model-specific registers, with optional CPU VID reporting on selected C7 models.

## Important APIs, Types, and Functions
`struct via_cputemp_data` stores hwmon device, CPU id, MSR addresses, VRM, and name. `temp_show()` reads the temperature MSR on the target CPU with `rdmsr_safe_on_cpu()`. `cpu0_vid_show()` reads VID MSR and converts with `vid_from_reg()`. CPU hotplug callbacks create and remove per-CPU platform devices. `via_cputemp_init()` registers the platform driver and dynamic CPUHP state after matching supported VIA CPU IDs.

## Control Flow
Module init first checks `x86_match_cpu()`, registers a platform driver, then installs CPU hotplug callbacks. When a CPU comes online, a platform device named `via_cputemp` is allocated for that CPU id; probe chooses MSR addresses by family/model, verifies temperature MSR access, creates sysfs attributes, optionally adds `cpu0_vid`, and registers hwmon. CPU down-prep unregisters the matching platform device.

## State and Persistence
State is per-online-CPU and exists only while the CPU platform device is registered. Readings are never cached; each sysfs read performs an MSR read on the relevant CPU. The pdev list persists module-wide under a mutex to coordinate hotplug removal.

## Dependencies and Integration Points
Depends on x86 Centaur CPU IDs, CPU hotplug framework, platform devices, MSR accessors, legacy hwmon sysfs groups, and `hwmon-vid`. It integrates with hwmon through `hwmon_device_register()` and manual sysfs group creation.

## Risks
Temperature conversion assumes the low 24 bits of EAX are degrees Celsius and reports millidegrees. If MSR access fails after probe, reads return `-EAGAIN`. The code is VIA-specific and intentionally rejects unsupported models. Hotplug bookkeeping must avoid list leaks if platform device allocation/addition fails. Optional VID only appears when both model MSR and VRM detection are available.

## Test Signals
Test CPU ID matching, model-to-MSR selection, probe failure on MSR read error, CPU online/offline lifecycle, optional `cpu0_vid` creation/removal, per-core labels, module init path without hotplug CPU support, and read error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/via-cputemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/via686a.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/via686a.c

## Purpose
Legacy hwmon driver for VIA VT82C686A/VT82C686B southbridge integrated sensors. It reports five voltage inputs, two fans, three temperatures, limits, fan dividers, alarms, and name through manually defined sysfs attributes.

## Important APIs, Types, and Functions
`struct via686a_data` caches ISA I/O base, hwmon device, update mutex, register snapshots, fan dividers, and alarm bits. Conversion helpers implement board-specific voltage factors, fan RPM conversion, and LUT-based temperature conversion. `via686a_update_device()` refreshes all measurements every 1.5 seconds. `via686a_pci_probe()` discovers the ISA base from PCI config, optionally forces/enables it, then registers a platform driver/device for the I/O region.

## Control Flow
The PCI driver probes the VIA southbridge function, determines the monitoring I/O base, enables sensors if forced, registers the platform driver, and adds a platform device. Platform probe reserves the ISA region, allocates state, starts monitoring, configures temperature interrupt mode, creates a single sysfs group, and registers hwmon. Sysfs reads use the cached update routine; writes update cached limits/dividers and immediately write ISA registers.

## State and Persistence
Measurements and limits are cached for 1.5 seconds under `update_lock`. User-written min/max/fan divider/temp thresholds persist in chip registers and cached fields. The module keeps global `pdev` and `s_bridge` because only a single device is supported and the PCI probe deliberately returns failure after holding a reference so other drivers can bind the same PCI device.

## Dependencies and Integration Points
Depends on PCI ID `PCI_DEVICE_ID_VIA_82C686_4`, ISA port I/O, ACPI resource conflict checks, platform device wrappers, legacy hwmon sysfs helpers, and module parameter `force_addr`.

## Risks
Legacy manual sysfs and ISA access have many scaling edge cases. Temperature conversion relies on historical LUTs rather than a datasheet formula. PCI probe intentionally returns `-ENODEV` after creating side effects, so init/exit lifecycle depends on the global bridge reference. Only one device is supported. Fan divider writes do not preserve fan minimum RPM semantics beyond raw register recalculation at the current divider.

## Test Signals
Verify PCI config base/enable handling, `force_addr` path, ACPI conflict rejection, sysfs group unwind, cache refresh timing, voltage conversion round trips, temperature LUT boundaries, fan RPM zero/saturation behavior, alarm bit mapping, and module exit unregistering platform resources only when `s_bridge` was acquired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/via686a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/vt1211.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/vt1211.c

## Purpose
VIA VT1211 Super-I/O hwmon driver exposing configurable universal channels as voltages or temperatures, two fans, PWM/SmartGuardian controls, VID/VRM, alarms, and legacy name attributes.

## Important APIs, Types, and Functions
`struct vt1211_data` holds ISA base, cached readings/limits/PWM state, VRM/VID, UCH config, alarms, and synchronization. Super-I/O helpers enter/exit config mode and read device ID/base. `ISVOLT()`/`ISTEMP()` interpret UCH configuration. Conversion helpers handle voltage, temperature mode differences, fan RPM/dividers, and PWM frequencies. Many `SENSOR_ATTR_2` arrays generate per-channel sysfs groups and PWM auto-point files. `vt1211_find()` detects the Super-I/O chip and address.

## Control Flow
Module init probes Super-I/O ports `0x2e` then `0x4e`, validates module parameters `uch_config`, `int_mode`, and `force_id`, registers the platform driver, and creates an I/O resource platform device. Platform probe reserves the region, initializes chip settings, conditionally creates voltage/temp sysfs groups based on UCH config, creates fan/PWM/misc files, and registers hwmon. Runtime reads refresh the whole register cache once per second; writes update cached fields and hardware registers under mutex.

## State and Persistence
The driver caches all measurements and control registers for one second. Module parameters can persistently alter hardware UCH configuration and interrupt mode at init. PWM auto point endpoints are hard-coded in RAM for off/full-speed values while middle points are read/written. User writes to limits, fan dividers, PWM mode/frequency/channel, VRM, and auto points persist in hardware registers until reset.

## Dependencies and Integration Points
Depends on Super-I/O configuration ports, ISA I/O, ACPI resource conflict checks, platform devices, legacy hwmon sysfs APIs, and `hwmon-vid`. Module parameters `uch_config`, `int_mode`, and `force_id` are key integration hooks for board quirks.

## Risks
The UCH mode determines which attributes exist; wrong firmware or forced `uch_config` can expose nonsensical voltage/temp channels. PWM control is complex and shared: disabling one PWM may clear global SmartGuardian when the other is disabled. Some auto temperature points are shared by both PWM controllers even though sysfs exposes two sets. Manual sysfs creation has large unwind surface. The driver supports one detected device via global `pdev`.

## Test Signals
Cover detection at both Super-I/O addresses, invalid module parameter rejection, UCH-driven sysfs visibility, cache refresh timing, voltage/temp conversion per channel type, fan divider invalid values and min preservation, PWM enable/frequency/auto-channel writes, shared auto-point behavior, VRM/VID conversion, and cleanup of partially created sysfs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/vt1211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/vt8231.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/vt8231.c

## Purpose
Legacy hwmon driver for VIA VT8231 southbridge embedded sensors. It exposes configurable voltage/temperature channels, two fans, fan dividers, limits, alarms, and name through manual sysfs groups.

## Important APIs, Types, and Functions
`struct vt8231_data` stores ISA base, cached voltage/temp/fan registers, fan dividers, alarms, and UCH configuration. `vt8231_update_device()` refreshes measurements every 1.5 seconds, reconstructs 10-bit temperatures from low-bit registers, and adjusts fan alarm bits for zero/min cases. Conversion helpers handle fan RPM and voltage/thermistor scaling, with special-case 3.3V input scaling. PCI discovery functions read/force base address and enable bits, then create a platform device.

## Control Flow
Module init registers a PCI driver. PCI probe reads the monitoring base from config register `0x70`, optionally forces it, enables the sensor block if needed, registers the platform driver, and adds a platform I/O resource. Platform probe reserves the ISA region, initializes temperature interrupt mode, creates common fan/alarm sysfs files, reads UCH config, creates only active temp/voltage groups, and registers hwmon. Sysfs reads use cached snapshots; writes update limits/dividers in hardware.

## State and Persistence
The driver caches readings for 1.5 seconds under `update_lock`. User-written voltage/temp/fan thresholds and fan dividers are stored in device registers and cached fields. Global `pdev` and `s_bridge` track the single supported instance; PCI probe returns failure after side-effect device creation to allow other drivers to bind the PCI function while this module holds a reference.

## Dependencies and Integration Points
Depends on VIA PCI ID `PCI_DEVICE_ID_VIA_8231_4`, ISA port I/O, ACPI resource conflict checks, platform device layering, hwmon sysfs helpers, and module parameter `force_addr`.

## Risks
Temperature channels can represent thermistor voltages rather than true temperatures, requiring user-space calibration. PCI probe's intentional `-ENODEV` return with side effects is fragile but mirrors older southbridge hwmon patterns. Fan alarm bits are corrected in software because hardware semantics around zero fan/min are awkward. Manual sysfs group creation must remove both common and conditional groups on failure.

## Test Signals
Test base address forced/default paths, sensor enable writes, UCH-dependent attribute creation, 10-bit temperature reconstruction, special in5 scaling, fan divider changes preserving minimum RPM, software fan alarm correction, cache invalidation timing, ACPI conflict handling, and exit cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/vt8231.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83627ehf.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83627ehf.c

## Purpose
Comprehensive hwmon driver for Winbond/Nuvoton W83627EHF/EHG/DHG/DHG-P/UHG and W83667HG/HG-B Super-I/O monitoring blocks. It reports voltage inputs, fans, PWMs, temperatures, alarms, intrusion, VID, and many SmartFan control attributes.

## Important APIs, Types, and Functions
`enum kinds` identifies chip variants. `struct w83627ehf_data` is the central state: I/O base, bank lock, feature masks, register tables, scaling tables, cached measurements/limits, PWM state, VID/VRM, temperature sources, and suspend-resume snapshots. Super-I/O helpers detect IDs and logical device resources. `w83627ehf_read_value()`/`write_value()` handle banked byte/word ISA register access. `w83627ehf_update_device()` refreshes all cached readings every 1.5 seconds and can auto-increase fan dividers. Modern hwmon callbacks implement standard attributes, while `w83627ehf_group` adds non-standard SmartFan sysfs files.

## Control Flow
Module init probes Super-I/O config ports `0x2e` and `0x4e`, maps chip ID to variant, obtains and enables the HWM logical-device base, checks ACPI conflicts, and creates a platform bundle. Probe reserves the data I/O ports, initializes variant-specific counts/scaling/temp source tables, starts monitoring, reads VID through Super-I/O when available, detects fan input pins, snapshots fan dividers/PWM modes, and registers hwmon with standard and extra groups. Reads update the cache then dispatch by type; writes call focused store helpers for limits, fan min/divider selection, temp offsets, PWM modes, SmartFan values, and intrusion clear.

## State and Persistence
The driver caches sensor state for 1.5 seconds and protects banked I/O separately from cache updates. Hardware register writes persist until reset or later writes. It stores original PWM enable modes to allow chips with unsupported modes to retain their original value. Suspend saves VBAT and cached limits; resume restores voltage, fan, temp, offset, and VBAT state and invalidates the cache.

## Dependencies and Integration Points
Depends on Super-I/O config access, ISA I/O, ACPI resource conflict checks, platform bundle registration, hwmon channel-info APIs, legacy extra sysfs groups, `hwmon-vid`, and `lm75.h` temperature conversion helpers. Module parameter `force_id` can override detection for testing or broken firmware.

## Risks
The driver has large variant-specific feature detection: wrong pin/source interpretation can expose missing fans, skip VIN3, or duplicate temperature sources. Banked register access must remain serialized or reads/writes can hit wrong banks. `w83627ehf_do_read_pwm()` returns `pwm_enable` for `hwmon_pwm_mode`, which is a likely semantic bug because mode should reflect DC/PWM output mode. Auto fan-divider increases modify hardware during reads. Extra sysfs attributes depend on `dev->parent` in show paths, so registration hierarchy matters.

## Test Signals
Cover chip ID mapping, force-id path, ACPI conflict rejection, fan input detection for each variant, temp source deduplication on W83667HG-B/UHG, banked word/byte register access, cache refresh timing, fan divider auto-increment and min preservation, PWM mode/enable writes, SmartFan extra visibility, intrusion clear sequence, VID availability, suspend/resume restoration, and standard hwmon visibility masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83627ehf.c -->
