# Research group subset-b-003823

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/da9055-hwmon.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/da9055-hwmon.c

### Purpose

`da9055-hwmon.c` is the hwmon child driver for the Dialog DA9055 PMIC. It exposes the PMIC ADC channels as Linux hwmon voltage inputs and a temperature input: VSYS, ADCIN1-3, and chip junction temperature. Voltage channels use the DA9055 continuous ADC registers, while junction temperature uses a manual ADC conversion and the PMIC trim offset.

### Important APIs, types, and functions

The central state is `struct da9055_hwmon`, which holds the parent `struct da9055`, a `hwmon_lock` for normal sysfs reads, an `irq_lock` around manual conversion, and a `completion` signaled by the ADC IRQ. `chan_mux[]` maps hwmon channel indices to DA9055 ADC mux values, and `input_names[]` provides labels.

Important functions are `da9055_adc_manual_read()`, `da9055_auxadc_irq()`, `volt_reg_to_mv()`, `da9055_enable_auto_mode()`, `da9055_disable_auto_mode()`, `da9055_auto_ch_show()`, `da9055_tjunc_show()`, `label_show()`, and `da9055_hwmon_probe()`. Sysfs is declared with `SENSOR_DEVICE_ATTR_RO()` entries and registered through `devm_hwmon_device_register_with_groups()`.

### Control flow

Probe allocates the state, initializes locks/completion, fetches the parent MFD driver data, obtains the named `"HWMON"` platform IRQ, registers `da9055_auxadc_irq()` as a threaded IRQ, then registers the hwmon device with static attributes.

Voltage reads enter `da9055_auto_ch_show()`, lock `hwmon_lock`, enable the selected continuous ADC channel in `DA9055_REG_ADC_CONT`, sleep roughly 10 ms, read `DA9055_REG_VSYS_RES + channel`, disable the continuous channel, convert the raw value to millivolts, and return it. Junction temperature reads call `da9055_adc_manual_read()` for `DA9055_ADC_TJUNC`; that function serializes on `irq_lock`, programs `DA9055_REG_ADC_MAN` with the mux plus manual conversion bit, waits up to 500 ms for the IRQ completion, reads high and low result registers, and returns the raw ADC code. `da9055_tjunc_show()` then reads `DA9055_REG_T_OFFSET` and applies the documented linear formula.

### State and persistence behavior

The driver does not persist settings beyond momentary ADC mode changes. Continuous-mode bits are enabled only long enough to sample a voltage channel and are disabled on exit paths. The completion is reused for manual conversions. There is no cached measurement state; every sysfs read performs hardware access. Device lifetime is devm-managed by the platform device.

### Dependencies and integration points

This file depends on the DA9055 MFD core/register APIs (`da9055_reg_read()`, `da9055_reg_write()`, `da9055_reg_update()`), platform-device IRQ resources, Linux completion/mutex primitives, and the hwmon sysfs registration helpers. It integrates as the `"da9055-hwmon"` platform child of the DA9055 MFD and exports standard hwmon files such as `in0_input`, `in*_label`, `temp1_input`, and `temp1_label`.

### Risks

The main risks are ADC mode interference and IRQ/completion ordering. `da9055_adc_manual_read()` never reinitializes the completion before starting a conversion, so correctness depends on no stale completion being pending; `irq_lock` prevents concurrent manual conversions but not stale IRQ state from earlier operations. Voltage reads must always disable auto mode on errors, which the code handles through the release path. Temperature conversion uses integer arithmetic with a negative coefficient, so changes need care around signed overflow and rounding.

### Test signals

Useful signals are module probe with a DA9055 MFD instance, visible hwmon attributes, repeated voltage reads confirming auto mode is disabled afterward, manual temperature reads with IRQ delivery, timeout behavior when the ADC IRQ is absent, and error injection for DA9055 register reads/writes. Runtime tests should check labels and millivolt/millicelsius scaling against datasheet examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/da9055-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/dell-smm-hwmon.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/dell-smm-hwmon.c

### Purpose

`dell-smm-hwmon.c` exposes Dell laptop and desktop firmware thermal controls through hwmon, optional `/proc/i8k` compatibility, and thermal cooling devices. It talks to Dell SMM either through legacy CPU0 SMM I/O traps or through a WMI method on newer systems. It reports temperature sensors, fan speeds and labels, fan nominal speeds, PWM-like fan control, and selected automatic/manual fan-control operations.

### Important APIs, types, and functions

Firmware calls use `struct smm_regs`, `struct dell_smm_ops`, and `dell_smm_call()`. Runtime state is `struct dell_smm_data`, containing the chosen backend, mutex, fan multiplier/max values, discovered temperature/fan metadata, and nominal-speed tables. Thermal integration uses `struct dell_smm_cooling_data` and `dell_smm_cooling_ops`.

Important backend helpers are `i8k_smm_func()`, `i8k_smm_call()`, `wmi_parse_register()`, `wmi_parse_response()`, and `wmi_smm_call()`. Firmware operations include `i8k_get_fan_status()`, `i8k_get_fan_speed()`, `i8k_get_fan_type()`, `i8k_get_fan_nominal_speed()`, `i8k_set_fan()`, `i8k_enable_fan_auto_mode()`, `i8k_get_temp_type()`, and `i8k_get_temp()`. The hwmon callbacks are `dell_smm_is_visible()`, `dell_smm_read()`, `dell_smm_read_string()`, and `dell_smm_write()`. Initialization is split among DMI setup, legacy probing, WMI probing, data setup, and hwmon registration.

### Control flow

Module init first applies DMI policy through `dell_smm_init_dmi()`, including fan-support blacklists, fan-type-call blacklists, fan multiplier/max overrides, and whitelisted automatic fan-control commands. It then runs `dell_smm_legacy_check()`: if legacy DMI/signature probing fails, it registers the WMI driver; otherwise it creates a platform bundle for the legacy SMM backend.

Legacy SMM calls are forced onto CPU0 with `smp_call_on_cpu()` and execute the `out 0xb2`/`out 0x84` sequence. WMI calls pack EAX/EBX/ECX/EDX into the Dell WMI legacy execute method and parse a length-prefixed buffer response. `dell_smm_call()` times the call, logs slow firmware, rejects carry/status failures, and treats unchanged or `0xffff` responses as invalid.

During hwmon init the driver probes up to ten temperature sensor types and four fan channels. Fans are considered present if status or type calls work. For present fans it may register a thermal cooling device and may allocate a nominal-speed table by querying each firmware fan state. The hwmon visibility callback exposes only channels and attributes that probing found usable. Writes serialize through `i8k_mutex` and either set a fan state, translate a 0-255 PWM value to a firmware fan step, or switch automatic/manual fan mode when supported.

### State and persistence behavior

Driver state is mostly firmware-discovery cache. Fan type is cached because the firmware call is expensive and known-buggy on some systems. Nominal-speed arrays persist for the device lifetime and support `fan*_min`, `fan*_max`, and `fan*_target`. Fan speed and temperature values are not cached by the driver; each read invokes firmware. PWM writes persist in firmware/BIOS fan state until firmware or userspace changes it. Automatic fan-control writes are global on systems with `auto_fan` commands; the driver exposes only one write-only `pwm*_enable` attribute in that case because it cannot read back the actual mode.

### Dependencies and integration points

The driver depends on x86 firmware behavior, DMI matching, WMI/ACPI buffers, CPU hotplug read locking, procfs and i8k uapi definitions when `CONFIG_I8K` is enabled, hwmon core, thermal cooling-device registration, and module parameters. Integration surfaces are `/sys/class/hwmon/...`, optional `/proc/i8k` and i8k ioctls, thermal zones that bind to `dell-smm-fanN`, and module parameters such as `force`, `ignore_dmi`, `fan_mult`, and `fan_max`.

### Risks

Firmware calls can be slow, blocking, or buggy. The file encodes DMI blacklists because some systems change fan behavior after a type query or freeze for hundreds of milliseconds on fan calls. The legacy backend assumes SMM execution on CPU0; CPU hotplug and preemption behavior around `smp_call_on_cpu()` is therefore important. Fan control has safety implications: switching out of automatic mode sets fan speed to maximum when no dedicated auto command exists. The procfs compatibility path exposes serial data unless restricted by `CAP_SYS_ADMIN`. WMI response parsing must reject malformed buffers to avoid consuming invalid register values.

### Test signals

Important tests are DMI match/blacklist behavior, successful fallback from legacy to WMI on modern systems, hwmon visibility on systems with different fan counts, slow-call warnings, fan multiplier autodetection, procfs ioctl permission checks, thermal cooling get/set state, invalid PWM and fan-state writes, and regression tests on blacklisted Dell models. Manual validation should compare SMM temperatures and fan RPMs against BIOS tools or `i8kutils`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/dell-smm-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/dme1737.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/dme1737.c

### Purpose

`dme1737.c` supports the SMSC DME1737, Asus A8000, SMSC SCH5027, SCH311x, and SCH5127 hardware-monitoring blocks. It is a hybrid driver: DME1737/SCH5027 style devices are accessed over I2C, while SCH311x/SCH5127 devices are discovered through Super-I/O and accessed through ISA index/data ports. It exposes voltages, temperatures, fans, PWM controls, automatic fan-control zones, alarms, optional VID, and chip-specific optional channels.

### Important APIs, types, and functions

`struct dme1737_data` is the core state. It stores either an I2C client or ISA port address, hwmon device, chip type/name, update lock, cache validity and timestamps, feature flags, nominal voltage table, config registers, and cached register values for inputs, temperatures, fans, PWMs, zones, hysteresis, VID, and alarms.

Important conversion helpers include `IN_FROM_REG()`, `IN_TO_REG()`, `TEMP_FROM_REG()`, `TEMP_TO_REG()`, `FAN_FROM_REG()`, `FAN_TO_REG()`, `FAN_TPC_FROM_REG()`, `PWM_EN_FROM_REG()`, `PWM_EN_TO_REG()`, `PWM_ACZ_FROM_REG()`, `PWM_ACZ_TO_REG()`, `PWM_FREQ_FROM_REG()`, `PWM_FREQ_TO_REG()`, and ramp/hysteresis conversion helpers. I/O is abstracted by `dme1737_read()` and `dme1737_write()`. Runtime refresh is `dme1737_update_device()`. Sysfs callbacks are grouped by sensor class: `show_in()`/`set_in()`, `show_temp()`/`set_temp()`, `show_zone()`/`set_zone()`, `show_fan()`/`set_fan()`, `show_pwm()`/`set_pwm()`, plus VID/name helpers.

### Control flow

Module init first registers the I2C driver. It then probes Super-I/O config ports `0x2e` and `0x4e`, optionally extra addresses, for ISA devices. If an ISA device is found, it registers a platform driver and platform device for the runtime I/O port.

I2C detection checks SMBus byte-data support, company ID, and revision/step to identify DME1737 or SCH5027. ISA detection enters Super-I/O config mode, validates device IDs, selects logical device A, reads the base address, and maps runtime access to base+0x70. Probe allocates state, sets type/access method, initializes the device, creates sysfs files, and registers the hwmon device.

`dme1737_init_device()` validates monitoring/ready bits, optionally starts monitoring with `force_start`, derives optional features from config registers, Super-I/O runtime feature bits, I2C address, and chip type, checks fan-to-PWM mappings, converts disabled PWMs to manual zero-duty mode on unlocked chips, initializes default zone assignments, and sets VRM. `dme1737_create_files()` creates the base group plus optional groups based on `has_features`, then changes permissions for writable controls when the chip is not locked.

Reads call `dme1737_update_device()`, which refreshes Vbat roughly every ten minutes and all other cached values roughly once per second. It reads MSBs before shared LSB registers for voltage/temperature coherency, reads only enabled optional fans/PWMs/zones, concatenates alarm registers, and explicitly clears ISA alarm bits after capture. Writes update the cached value and hardware register under `update_lock`.

### State and persistence behavior

The file maintains a one-second cache for most readings and a separate ten-minute Vbat trigger. Hardware limits, PWM settings, zone curves, fan types, and VRM persist in device registers or driver state after sysfs writes. The `valid` flag gates cache initialization. `has_features` is fixed at probe and controls both sysfs shape and refresh loops. PWM mode changes also mutate sysfs permissions at runtime; `pwm[1-3]` becomes writable only in manual mode on unlocked chips. ISA alarm bits are clear-on-write by the driver, while I2C alarms are just reported.

### Dependencies and integration points

Dependencies include I2C SMBus byte operations, platform devices/resources, raw I/O port access, ACPI resource conflict checks, hwmon sysfs helpers, `hwmon-vid`, mutexes, and Super-I/O config-port conventions. The driver integrates with I2C class probing at addresses `0x2c-0x2e`, platform devices for ISA runtime ports, and legacy hwmon sysfs registration via `hwmon_device_register()` after manually creating groups.

### Risks

The risk surface is high because the driver mixes two buses, raw port I/O, dynamic sysfs creation, and many chip variants. Incorrect feature detection can expose nonexistent registers or hide real controls. The shared LSB-register read order is required for coherent 12-bit values. Permission changes must match PWM mode and lock state or userspace can write controls that hardware should protect. Super-I/O probing and `force_id` can target the wrong hardware if misused. Some write helpers ignore low-level write errors, so register failures may not be reflected in sysfs return values. ISA alarm clearing changes hardware-visible alarm latch state.

### Test signals

Useful tests include I2C detection for DME1737/SCH5027 IDs, ISA detection for SCH311x/SCH5127 IDs, `force_start` behavior, sysfs file presence per chip variant, read coherence of voltage/temperature LSBs, fan/PWM optional-feature detection, PWM mode transitions and permission changes, locked-chip read-only behavior, alarm reporting and clearing on ISA, and unload cleanup of all dynamic sysfs groups. Hardware-in-loop testing is especially important because emulation must model many variant registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/dme1737.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/drivetemp.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/drivetemp.c

### Purpose

`drivetemp.c` registers a SCSI class interface that creates hwmon devices for SATA disks and zoned block disks with drive temperature reporting. It prefers ATA SCT Command Transport temperature data and limits, and falls back to SMART attributes 194 or 190 when SCT temperature is unavailable or unsafe for a known model family.

### Important APIs, types, and functions

`struct drivetemp_data` stores the SCSI device, owning device, hwmon device, 512-byte ATA/SCT transfer buffer, selected temperature-read callback, presence flags for optional attributes, and static limit values read at probe. A global `drivetemp_devlist` tracks instantiated devices for class-interface removal.

Core helpers are `drivetemp_scsi_command()`, `drivetemp_ata_command()`, `drivetemp_get_smarttemp()`, `drivetemp_get_scttemp()`, `drivetemp_sct_avoid()`, `drivetemp_identify_sata()`, `drivetemp_identify()`, `drivetemp_read()`, `drivetemp_is_visible()`, `drivetemp_add()`, and `drivetemp_remove()`. The hwmon ABI is described through `drivetemp_info`, `drivetemp_ops`, and `drivetemp_chip_info`.

### Control flow

Module init registers a `class_interface` with the SCSI subsystem. For every matching SCSI device node, `drivetemp_add()` allocates state and calls `drivetemp_identify()`. Identification rejects devices without inquiry data and non-disk/non-ZBC device types, then reads ATA Information VPD page 0x89 under RCU to confirm SAT, ATA, and SATA. It records whether SCT, SCT data tables, and SMART are supported/enabled.

If SCT is supported and not blocked by the model-prefix avoid list, the driver reads the SCT status log and accepts only version 2 or 3 with a valid current temperature. It records lowest/highest history flags from the status log. If SCT data tables are available, it sends an SCT table request through SMART write log, reads the SCT read-log page, and records min/max/critical limits. Successful SCT setup installs `drivetemp_get_scttemp()` as the read callback. Otherwise SMART fallback requires SMART support and verifies that a SMART temperature attribute can be read.

Hwmon reads dispatch by attribute. Dynamic SCT values call `get_temp()` for input/lowest/highest. Static limits return the values captured during probe. Visibility exposes optional attributes only when the corresponding probe flags are set.

### State and persistence behavior

Temperature readings are not cached; each sysfs read sends ATA commands through SCSI. Limit values from SCT data tables are captured once at probe and stored in millidegrees. The selected read method persists in the function pointer. The device list persists until SCSI remove, where the hwmon device is unregistered and state is freed.

### Dependencies and integration points

The driver depends on SCSI class interfaces, SAT ATA pass-through via `ATA_16`, `scsi_execute_cmd()`, ATA identify helper macros, RCU-protected `sdev->vpd_pg89`, and the hwmon `*_with_info` API. It integrates under each SCSI disk's generic device and exports `temp1_input`, optional history/limit files, and thermal-zone registration via `HWMON_C_REGISTER_TZ`.

### Risks

The highest risk is polling drives with commands that some firmware handles badly. The SCT avoid list blocks TOSHIBA DT01ACA* because SCT polling can interact with heavy writes and freeze drives. SMART temperature attributes are vendor-defined and only a fallback; attributes 190 and 194 can mean different things on old or unusual drives. `drivetemp_devlist` is a global list without an explicit lock, relying on class-interface serialization. Probe-time static SCT limits may become stale if firmware updates them. ATA pass-through failures are surfaced as I/O errors but can be noisy on bridges with incomplete SAT support.

### Test signals

Tests should cover SATA devices with SCT status, SCT data tables, SMART-only fallback, non-SATA SCSI devices, SAT bridges without VPD page 0x89, known SCT-avoid model prefixes, checksum failure in SMART values, invalid `0x80` temperatures, and SCSI remove while hwmon exists. Practical validation compares hwmon readings with `smartctl -A` and SCT temperature logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/drivetemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ds1621.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/ds1621.c

### Purpose

`ds1621.c` supports Maxim/Dallas DS1621-family I2C temperature sensors and thermostats: DS1621, DS1625, DS1631, DS1721, and DS1731. It exposes current temperature, min/max thresholds, alarms, aggregate alarm bits, and for higher-resolution variants an adjustable conversion/update interval.

### Important APIs, types, and functions

`struct ds1621_data` contains the I2C client, cache lock, validity timestamp, chip kind, cached temperature registers, cached config, resolution zero-bit count, and update interval in milliseconds. `polarity` is a module parameter that can force thermostat output polarity during init.

Important helpers are `DS1621_TEMP_FROM_REG()`, `DS1621_TEMP_TO_REG()`, `ds1621_init_client()`, `ds1621_update_client()`, `temp_show()`, `temp_store()`, `alarms_show()`, `alarm_show()`, `update_interval_show()`, `update_interval_store()`, `ds1621_attribute_visible()`, and `ds1621_probe()`.

### Control flow

Probe allocates state, stores the chip kind from the I2C match data, initializes the client into continuous conversion mode, and registers static hwmon groups. `ds1621_init_client()` reads the config register, clears one-shot mode, optionally applies the module polarity setting, calculates conversion timing and resolution encoding by chip kind, then starts conversions with the appropriate command (`0xee` for DS1621/DS1625 or `0x51` for DS1631/DS1721/DS1731).

Sysfs reads refresh through `ds1621_update_client()` when the cache is invalid or older than `update_interval`. The refresh reads config and three word-swapped temperature registers. It also clears low/high alarm latch bits when current temperature has returned inside limits. Threshold writes parse millidegrees, clamp and convert according to current resolution, write the selected threshold register, and update the cache. Update-interval writes choose the nearest supported DS1721-style conversion rate, rewrite resolution bits, and update `zbits` and `update_interval`.

### State and persistence behavior

The driver caches readings for the sensor conversion interval. Thresholds and resolution/polarity settings are persisted in chip registers, while the cache mirrors their latest written values. Alarm bits are latched in the config register and may be cleared by reads when conditions are no longer active. `update_interval` is hidden for DS1621/DS1625 because those parts do not expose the same configurable resolution model.

### Dependencies and integration points

Dependencies are I2C SMBus byte and word-swapped accesses, hwmon sysfs helpers, jiffies timing, mutexes, and I2C device ID match data. Integration is a normal `module_i2c_driver()` named `"ds1621"` that creates files such as `temp1_input`, `temp1_min`, `temp1_max`, `temp1_min_alarm`, `temp1_max_alarm`, `alarms`, and conditionally `update_interval`.

### Risks

The driver does not check all SMBus read/write return values during initialization and refresh, so bus errors can become cached register values. Resolution changes alter threshold encoding through `zbits`; mismatches can make sysfs limits appear rounded or shifted. Alarm-clearing logic compares raw register encodings and must preserve DS1621-family semantics. The module-level `polarity` parameter affects all probed devices.

### Test signals

Test signals include probing each supported ID, verifying update-interval visibility by chip kind, reading and writing min/max thresholds across clamp boundaries, changing conversion resolution on DS1721-compatible parts, observing alarm bits set and clear, and checking continuous conversion starts after probe. Fault injection for SMBus failures would expose current weak error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ds1621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ds620.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/ds620.c

### Purpose

`ds620.c` supports the Maxim DS620 temperature sensor and thermostat. It exposes current temperature, min/max thermostat thresholds, and min/max alarm bits over the hwmon sysfs ABI. Probe configures continuous conversion, high precision, and thermostat output mode based on optional platform data.

### Important APIs, types, and functions

`struct ds620_data` contains the I2C client, update mutex, cache validity/timestamp, and three signed 16-bit temperature register values. Important functions are `ds620_init_client()`, `ds620_update_client()`, `temp_show()`, `temp_store()`, `alarm_show()`, and `ds620_probe()`. Attributes are static `SENSOR_DEVICE_ATTR_*` entries registered with `devm_hwmon_device_register_with_groups()`.

### Control flow

Probe allocates state, initializes the mutex, calls `ds620_init_client()`, and registers the hwmon group. Initialization reads the config word, clears one-shot mode, sets high-precision resolution bits, configures PO output mode from `struct ds620_platform_data` when present, writes the changed config, and sends the start-conversion command.

Reads call `ds620_update_client()`, which refreshes all three word-swapped temperature registers if the cache is invalid or older than 1.5 seconds. `temp_show()` converts the cached register to millidegrees using the DS620 0.0625 C step encoding. Threshold writes parse millidegrees, clamp to -128000..128000, convert to the register encoding, update the cache, and write the selected threshold register. Alarm reads refresh data, read the config register directly, clear the requested alarm bit by writing config back if set, and return the previous state.

### State and persistence behavior

The driver keeps a 1.5 second cache of temperature registers. Thresholds and config bits persist in the sensor. Alarm flags are latch-like config bits and are cleared on read of the specific alarm sysfs file. Platform thermostat output mode is applied once at probe. Device memory management is devm-managed.

### Dependencies and integration points

Dependencies are I2C SMBus word-swapped and byte commands, optional `linux/platform_data/ds620.h`, hwmon sysfs helpers, jiffies, and mutexes. Integration is a standard I2C driver named `"ds620"` with `temp1_input`, `temp1_min`, `temp1_max`, `temp1_min_alarm`, and `temp1_max_alarm`.

### Risks

Initialization does not fully validate reads before using config values. `ds620_update_client()` returns an ERR_PTR on refresh failures, so callers must continue to check it as `temp_show()` and `alarm_show()` do. Alarm reads clear hardware latch bits, which can surprise consumers expecting non-destructive reads. Conversion math uses integer truncation after scaling and should be tested around negative values and limits.

### Test signals

Useful tests include probe with and without platform data, config register programming, repeated reads observing cache behavior, threshold write/readback at boundaries, alarm bit clear-on-read behavior, and SMBus error injection for refresh and config writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ds620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc1403.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/emc1403.c

### Purpose

`emc1403.c` supports SMSC/Microchip EMC140x/EMC141x/EMC142x/EMC1438/EMC1442 temperature-monitoring chips. It exposes up to eight temperature channels with min/max/critical limits, hysteresis, alarms, faults, update interval, and a legacy `power_state` sysfs attribute. It uses regmap caching to reduce ordinary register traffic while marking live measurement/status registers volatile.

### Important APIs, types, and functions

`struct thermal_data` stores the chip variant and regmap. Chip variants are represented by `enum emc1403_chip`. Important tables are `emc1403_temp_regs`, `emc1403_temp_regs_low`, and `ema1403_temp_map`, mapping hwmon attributes and channels to high/low registers. Important functions are `emc1403_detect()`, `emc1403_regmap_is_volatile()`, `emc1403_get_temp()`, `emc1403_get_hyst()`, `emc1403_temp_read()`, `emc1403_set_temp()`, `emc1403_set_hyst()`, `emc1403_get_convrate()`, `emc1403_set_convrate()`, `emc1403_is_visible()`, and `emc1403_probe()`.

### Control flow

I2C class probing validates manufacturer ID `0x5d`, product IDs, and revision range, then sets the appropriate client type. Probe allocates state, records chip match data, creates an I2C regmap with maple cache, and registers the hwmon device with info-based callbacks plus the extra `power_state` group.

Temperature reads resolve the hwmon attribute to a register map, read the high byte and optional low-byte fraction register, combine 0.125 C units, and sign-extend only on the EMC1428 family. Hysteresis reads use the shared hysteresis register at `0x21` relative to the selected limit. Alarm reads use legacy status bits for EMC1402 and separate high/low/therm status registers for other variants. Writes clamp values based on signed or unsigned chip family behavior, write high and optional low bytes, and write the global hysteresis register for critical hysteresis. Update interval writes choose the closest supported conversion time and program register `0x04`.

### State and persistence behavior

Persistent state is primarily in hardware registers and regmap cache. Volatile temperature/status registers bypass cache. Limit, hysteresis, conversion-rate, and power-state writes persist on the chip. Visibility is determined by chip variant: EMC1402 exposes two channels, EMC1403 exposes three, non-EMC1428 variants expose up to four, and EMC1428-family devices expose up to eight.

### Dependencies and integration points

Dependencies include I2C SMBus/regmap, hwmon info API, sysfs helpers, `find_closest_descending()`, and I2C class address scanning over the listed addresses. Integration surfaces are standard hwmon attributes and the custom `power_state` attribute that toggles bit 6 of register `0x03`.

### Risks

Shared hysteresis means writes through `temp1_crit_hyst` affect all channels; visibility makes non-channel-0 critical hysteresis read-only. Product ID mapping collapses related chips onto a small enum, so signedness/channel-count distinctions must stay correct. Regmap volatility must include every measurement/status register or userspace may see stale data. The conversion-time table is named `ina3221_conv_time`, which is misleading but functional. Detection by fixed revision range can reject newer compatible steppings.

### Test signals

Tests should verify detection for all ID table aliases, channel visibility per variant, signed negative temperatures on EMC1428-family chips, fractional limit read/write round trips, alarm bit mapping for EMC1402 versus later chips, update interval selection, regmap volatility, and `power_state` read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc1403.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc2103.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/emc2103.c

### Purpose

`emc2103.c` supports the SMSC EMC2103 temperature monitor and fan controller. It exposes internal/external temperature channels, temperature limits and alarms, fan tachometer RPM, fan divider, target RPM, fan fault, and RPM-control enable. Some variants support one external diode, while EMC2103-2/-4 can expose three or four external channels depending on anti-parallel diode mode.

### Important APIs, types, and functions

`struct emc2103_data` holds the I2C client, sysfs groups, update lock, cache validity, fan RPM-control state, temperature channel count, timestamps, cached temperature/limit/alarm values, fan multiplier, tach count, and target count. `struct temperature` stores signed degrees plus 0.125 C fractional units.

Important helpers are `read_u8_from_i2c()`, `read_temp_from_i2c()`, `read_fan_from_i2c()`, `write_fan_target_to_i2c()`, `read_fan_config_from_i2c()`, `emc2103_update_device()`, the temperature/fan/pwm sysfs show/store functions, `emc2103_probe()`, and `emc2103_detect()`.

### Control flow

Detection checks SMBus byte-data support, manufacturer ID `0x5d`, and product ID `0x24` or `0x26`. Probe allocates state, reads product ID to determine base channel count, and for multi-diode variants reads `REG_CONF1` to detect APD mode. The module parameter `apd` can force anti-parallel diode mode off or on by changing bit 0 of `REG_CONF1`. Probe then builds a null-terminated group list: base attributes, optional temp3 group, and optional temp4 group.

Reads refresh through `emc2103_update_device()` every 1.5 seconds. The refresh reads temperature high/fraction bytes and min/max bytes for each channel, alarm registers, fan tach and target counts, and fan configuration. Fan RPM is calculated from `FAN_RPM_FACTOR * fan_multiplier / tach`. Divider writes update range bits in `REG_FAN_CONF1`, adjust the cached multiplier, and rescale the fan target so the target RPM remains stable. Target writes clamp requested RPM and convert it to a tach target count, with zero disabling target control. `pwm1_enable` maps hwmon value `0` to open-loop/manual behavior and `3` to RPM control.

### State and persistence behavior

The driver caches sensor data for 1.5 seconds. Limits, fan divider, target count, APD mode, and RPM-control enable persist in chip registers after writes. The group list and `temp_count` are fixed at probe, so changing APD mode later outside the driver will not change sysfs shape. Error handling in low-level reads logs warnings but leaves old cached fields intact for many paths.

### Dependencies and integration points

Dependencies are I2C SMBus byte operations, hwmon sysfs helpers, jiffies, mutexes, and I2C class scanning at address `0x2e`. Integration is a classic sysfs-group hwmon driver with dynamically selected attribute groups rather than the newer info API.

### Risks

The low-level read helpers often return without invalidating cache fields, so transient I2C errors can yield stale or partial readings. Fan target and divider math must avoid divide-by-zero and preserve target RPM across divider changes. APD mode is a module-wide parameter affecting all devices. Temperature fault uses a sentinel degrees value of `-128`; signed conversions need to preserve that. The driver assumes product ID is enough to distinguish channel capability.

### Test signals

Tests should cover product IDs `0x24` and `0x26`, APD default/forced on/forced off behavior, dynamic group count, temperature fractional conversion, min/max writes and alarms, fan tach zero/fault/disabled target handling, divider changes preserving target RPM, and `pwm1_enable` accepting only `0` and `3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc2103.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc2305.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/emc2305.c

### Purpose

`emc2305.c` supports the Microchip EMC2301/2302/2303/2305 fan controllers. It exposes fan tachometer readings, fan fault bits, and PWM drive controls through hwmon, and can register thermal cooling devices that drive one common PWM state or separate per-channel states. It also parses platform data or device-tree child nodes for PWM channel configuration.

### Important APIs, types, and functions

`struct emc2305_data` stores the I2C client, hwmon device, cooling max state, active PWM channel count, output/polarity masks, separate/common mode, minimum PWM values, configured PWM frequencies, and per-channel `struct emc2305_cdev_data`. The cooling data tracks current state plus last states requested by hwmon and thermal subsystems to implement a low-limit policy.

Important functions are `emc2305_identify()`, `emc2305_show_fault()`, `emc2305_show_fan()`, `emc2305_show_pwm()`, `emc2305_set_pwm()`, `__emc2305_set_cur_state()`, `emc2305_set_cur_state()`, `emc2305_set_single_tz()`, `emc2305_set_tz()`, `emc2305_is_visible()`, `emc2305_read()`, `emc2305_write()`, `emc2305_of_parse_pwm_child()`, `emc2305_probe_childs_from_dt()`, and `emc2305_probe()`.

### Control flow

Probe requires SMBus byte and word data, validates vendor ID `0x5d`, allocates state, identifies product ID to determine channel count, and parses optional DT child nodes. If no DT children are found, platform data can override max state, active channel count, masks, separate/common mode, minimum PWM, and frequency; otherwise defaults are used. The driver registers an info-based hwmon device, then if thermal support is reachable registers cooling devices either per child/per channel or one common zone. Finally it writes output mode, polarity, and per-channel minimum drive registers.

Hwmon reads call direct I2C operations: tach counts are read word-swapped, shifted to remove unused bits, converted to RPM, and small/invalid values return zero; faults read the drive-fail status register; PWM input reads the drive register. Hwmon PWM writes either set a raw PWM value directly or, when thermal support is present, update the hwmon low-limit state and only drive hardware if that state is not below the most recent thermal state. Thermal writes clamp to max state, store `last_thermal_state`, and call `__emc2305_set_cur_state()`, which enforces the hwmon minimum and writes either one channel or all channels.

### State and persistence behavior

Raw PWM drive, minimum drive, polarity, and output mode persist in controller registers. Driver state persists current cooling state and last hwmon/thermal requests; these are not read back from hardware after probe. In common-PWM mode, channel zero cooling state represents all fans. Device-tree child parsing can configure frequency/polarity/output masks, though the current probe writes only polarity/output/minimum drive and does not program frequency registers.

### Dependencies and integration points

Dependencies include I2C SMBus, hwmon info API, thermal cooling devices, PWM polarity constants, Open Firmware parsing, platform data `emc2305.h`, and util macros. Integration surfaces are `/sys/class/hwmon` fan/PWM attributes, thermal zone cooling bindings, I2C IDs for EMC2301/2/3/5, and OF compatible `"microchip,emc2305"`.

### Risks

There is no mutex around shared `cdev_data`, so concurrent hwmon and thermal writes can race on last-state/current-state fields and hardware writes. The low-limit interaction between hwmon and thermal is policy-heavy and easy to regress. DT parsing accepts child `reg` values without an explicit bound before indexing arrays, so malformed firmware descriptions can be risky. The output configuration validation condition for open-drain/push-pull is permissive and should be reviewed. Tach conversion depends on datasheet assumptions about pole/edge count and treats low speeds as zero.

### Test signals

Tests should cover all product IDs and channel counts, platform-data and DT configuration paths, common versus separate PWM mode, thermal cooling registration, hwmon low-limit behavior under concurrent thermal requests, PWM min bounds, tach/fault reads, malformed DT child `reg` and `pwms` arguments, and suspend/reprobe behavior preserving expected hardware defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc2305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc6w201.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/emc6w201.c

### Purpose

`emc6w201.c` supports the SMSC EMC6W201 hardware monitor. It exposes six voltage inputs with min/max limits, six temperature inputs with min/max limits, and five fan tachometers with minimum RPM limits. It uses classic hwmon sysfs attributes and periodic I2C register caching.

### Important APIs, types, and functions

`struct emc6w201_data` contains the I2C client, update mutex, cache validity/timestamp, voltage arrays indexed by subfeature and channel, temperature arrays, and fan arrays. `enum subfeature` indexes `input`, `min`, and `max`. Important helpers are `emc6w201_read16()`, `emc6w201_write16()`, `emc6w201_read8()`, `emc6w201_write8()`, `emc6w201_update_device()`, `in_show()`/`in_store()`, `temp_show()`/`temp_store()`, `fan_show()`/`fan_store()`, `emc6w201_detect()`, and `emc6w201_probe()`.

### Control flow

I2C detection requires SMBus byte support, company ID `0x5c`, a version/step high nibble of `0xb`, a known low stepping, a config register matching expected reserved bits, and monitoring enabled. Probe allocates state, initializes the mutex, and registers the static attribute group.

Sysfs reads refresh through `emc6w201_update_device()` when the cache is invalid or older than one second. The refresh reads all voltage current/min/max registers, all temperature current/min/max registers, and all fan current/min registers. Voltage values scale raw register values against per-channel nominal millivolt constants. Temperature values are signed degrees C times 1000. Fan RPM is `5400000 / count`, with zero and `0xffff` treated as stopped/invalid. Writes parse sysfs values, clamp and convert them to register units, update cache, and write the relevant limit register.

### State and persistence behavior

The driver maintains a one-second cache. Limit writes persist to the chip and update cached arrays. Input readings are never written. I2C read failures in cache refresh log errors and substitute arbitrary values (`0`, `0xffff`), then can still mark the cache valid, so error behavior affects visible state until the next refresh.

### Dependencies and integration points

Dependencies are I2C class scanning at `0x2c-0x2e`, SMBus byte operations, hwmon sysfs helper macros, jiffies, and mutexes. Integration is a standard I2C hwmon driver named `"emc6w201"` exposing fixed attribute sets for all supported channels.

### Risks

The read helpers hide I2C failures by returning placeholder values, which can make sysfs show misleading zero or stopped-fan readings. Since all channels are always exposed, board designs with unconnected inputs rely on userspace interpretation. Scaling depends on the fixed `nominal_mv[]` table. Detection rejects monitoring-disabled devices rather than enabling them. Fan limit writes use only the `min` subfeature path; callers should not expect max fan limits.

### Test signals

Tests should verify detection ID/config handling, one-second cache refresh, voltage scaling and limit round trips for all nominal channels, signed temperature limit writes, fan RPM/count conversions including zero and `0xffff`, I2C failure behavior, and cleanup through devm hwmon registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/emc6w201.c -->
