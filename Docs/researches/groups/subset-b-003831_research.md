# subset-b-003831 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31760.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max31760.c` Research

Purpose: this is an I2C hwmon driver for the Analog Devices/Maxim MAX31760 fan-speed controller. It exposes two tachometer inputs, two temperature inputs, one PWM control, automatic temperature source selection, alert state, and a 48-entry automatic fan-control lookup table.

Important APIs, types, and functions: `struct max31760_state` owns the `regmap`, generated lookup-table sysfs attributes, and extra attribute groups. `max31760_read()`, `max31760_write()`, `max31760_is_visible()`, and `max31760_read_string()` implement the modern `hwmon_ops` path. `lut_show()`/`lut_store()` and `pwm1_auto_point_temp_hyst_*()` provide extra `hwmon-sysfs` attributes outside the generic channel table. `max31760_probe()` creates the I2C regmap, sets comparator alert mode with `CR2_ALERTS`, builds the LUT nodes, and registers the hwmon device. Suspend/resume use `DEFINE_SIMPLE_DEV_PM_OPS()` and toggle `CR2_STBY`.

Control flow: sysfs reads switch first on sensor type, then attribute. Temperature values are two-byte 11-bit-ish values converted with `TEMP11_FROM_REG()`, fan input uses `REG_TACH(channel)` and `tach_to_rpm()`, PWM frequency maps through `max31760_pwm_freq[]`, and automatic channel selection maps hwmon bitmasks to `CR1_TEMP_SRC`. Writes validate ranges, convert millidegrees with `TEMP11_TO_REG()`, update `REG_CR1`/`REG_CR2`/`REG_CR3`, and write LUT PWM bytes directly.

State and persistence: hardware registers are the persistent state. `REGCACHE_MAPLE` caches nonvolatile registers, while `max31760_volatile_reg()` treats registers above `0x50` as volatile. Generated attribute names live in devm-managed driver state. There is no polling cache; each hwmon access reads current hardware or writes registers immediately.

Dependencies and integration points: depends on I2C, regmap-i2c, hwmon, hwmon-sysfs, bitfield helpers, and device tree compatible `adi,max31760`. It integrates with runtime/system sleep through PM ops and with hwmon sysfs including custom LUT attributes such as `pwm1_auto_pointN_pwm`.

Risks and test signals: conversion math and channel indexing are central risks, especially the 48 dynamic attributes and mapping `pwm_auto_channels_temp` values to `CR1_TEMP_SRC`. Tests should probe with a regmap/I2C mock, verify `is_visible` modes, round-trip max/crit temperature writes, verify invalid PWM enable/fan enable values return `-EINVAL`, confirm suspend/resume toggles standby, and confirm all 48 LUT files read/write the expected register range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31760.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31790.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max31790.c` Research

Purpose: this I2C hwmon driver supports the MAX31790 six-channel fan controller. It exposes six primary fan/PWM channels plus six optional companion tach inputs when a channel is configured as tach input.

Important APIs, types, and functions: `struct max31790_data` stores the I2C client, one-second cache validity, fan configuration, dynamics, fault status, tach readings, PWM duty, and target counts. `max31790_update_device()` refreshes cached registers. `max31790_read_fan()`/`write_fan()` handle `fan*_input`, `fan*_target`, `fan*_fault`, and `fan*_enable`; `max31790_read_pwm()`/`write_pwm()` handle `pwm*_input` and mode. `max31790_init_client()` seeds configuration from hardware, and `max31790_probe()` checks SMBus byte/word support before registering `max31790_chip_info`.

Control flow: reads call `max31790_update_device()` if data is older than `HZ` or invalid. The update path reads both fault status bytes, then per-channel tach and, depending on `MAX31790_FAN_CFG_TACH_INPUT`, companion tach or PWM/target count registers. Fan speed conversion uses selected tach period from `fan_dynamics`. Writes to target RPM choose a tach sample-rate field via `bits_for_tach_period()`, then write target count. PWM mode writes manipulate monitor, manual, or RPM mode bits and mirror chip side effects by setting `TACH_INPUT_EN` when RPM mode is selected.

State and persistence: cached fields are transient copies of hardware, with `valid` and `last_updated` controlling refresh. Writes update both hardware and cached configuration, and PWM duty writes invalidate the cache. Fault status is latched in the driver and cleared from the software copy after reporting; the hardware clear is triggered by writing target-count high byte.

Dependencies and integration points: uses SMBus byte and swapped-word operations, hwmon channel callbacks, `jiffies`, and I2C device id `max31790`. It has no device-tree table in this file and no PM hooks.

Risks and test signals: important risks include stale `fault_status` accumulation because it is ORed during refresh, channel modulo handling for companion tach inputs, and mode bit combinations for PWM enable. Tests should verify visibility for direct tach vs PWM channels, RPM conversion for zero/max count, target writes at min/max clamps, fault read clearing behavior, and probe rejection when SMBus capabilities are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31790.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31827.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max31827.c` Research

Purpose: this I2C hwmon driver supports MAX31827/MAX31828/MAX31829 low-power temperature switches. It exposes temperature input, min/max thresholds, hysteresis, alarm status, enable state, update interval, PEC, and a custom `temp1_resolution` sysfs attribute.

Important APIs, types, and functions: `struct max31827_state` keeps the regmap, logical enable state, selected resolution, and update interval. `shutdown_write()` is the key helper: threshold, hysteresis, and resolution writes must occur while the part is in shutdown, so it temporarily clears one-shot/conversion-rate bits and restores conversion rate afterward. `max31827_read()` and `max31827_write()` implement hwmon callbacks, while `max31827_init_client()` parses firmware properties such as `adi,comp-int`, `adi,timeout-enable`, `adi,alarm-pol`, and `adi,fault-q`.

Control flow: probe requires SMBus word access, initializes regmap, enables optional `vref`, calls firmware-driven initialization, then registers hwmon with `max31827_groups`. Temperature reads trigger a one-shot conversion and sleep for the resolution-specific conversion time if the device is disabled. Update-interval writes convert desired milliseconds to the closest conversion-rate code and are rejected while disabled.

State and persistence: hardware registers hold thresholds, configuration, resolution, and PEC. Driver state mirrors enable/resolution/update interval and is used to decide conversion waits and legal operations. There is no regcache; reads and writes go directly through regmap.

Dependencies and integration points: uses I2C, regmap, regulator consumer support, firmware node APIs, hwmon, and OF match data for chip defaults. Device-tree bindings influence polarity and fault queue defaults, with different defaults for MAX31829.

Risks and test signals: the most important risk is sequencing writes that require shutdown without losing conversion-rate bits. There is also a likely fragile check comparing `max31827_resolutions[st->resolution] == 12` even though the table stores millidegree resolution steps, not bit count. Tests should validate one-shot read timing, update-interval selection, invalid `adi,fault-q`, enable write validation, PEC bit writes, threshold round trips, and chip-specific default polarity/fault queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max31827.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6620.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max6620.c` Research

Purpose: this is an I2C hwmon driver for the MAX6620 four-channel fan controller. It exposes fan speed, target RPM, fan divider, and alarm state for four fans.

Important APIs, types, and functions: `struct max6620_data` stores the client, one-second cache metadata, per-fan configuration/dynamics, fault byte, tach counts, and target counts. Conversion helpers are `max6620_fan_div_from_reg()`, `max6620_fan_rpm_to_tach()`, and `max6620_fan_tach_to_rpm()`. `max6620_update_device()` refreshes cached registers and latches fault bits. `max6620_read()`/`max6620_write()` implement hwmon callbacks, and `max6620_init_client()` configures the chip for RPM mode.

Control flow: probe allocates state, initializes global config and each fan, then registers hwmon. Reads refresh at most once per second. Tach and target registers are split across two bytes with 11 significant bits. Alarm reads report latched software fault state and, if set, rewrite the target count to re-enable fault detection. Writes validate divider values, update the high bits in the dynamics register, clamp target RPM, convert to tach count, and write both target bytes.

State and persistence: hardware registers hold all real configuration. The software cache stores sampled registers and a latched fault byte because reading the hardware fault register clears alarms when the fault condition disappears. `valid` and `last_updated` control refresh; target/divider writes update cached fields.

Dependencies and integration points: uses SMBus byte reads/writes, hwmon with `HWMON_F_INPUT`, `HWMON_F_DIV`, `HWMON_F_TARGET`, and `HWMON_F_ALARM`, and an I2C_CLASS_HWMON driver id.

Risks and test signals: risks include divide-by-zero if a malformed zero tach enters conversion paths outside guarded input reads, split-register packing errors, and alarm re-enable side effects during reads. Tests should cover divider encoding for all accepted values, target clamp boundaries, fault latch and clear behavior, cache expiry, init writes for RPM mode, and propagation of SMBus failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6621.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max6621.c` Research

Purpose: this I2C hwmon driver supports the Maxim MAX6621 PECI-to-I2C temperature monitor. It exposes a maximum temperature channel plus socket/domain temperature inputs, critical thresholds and alarms for socket channels, labels, and a global offset.

Important APIs, types, and functions: `struct max6621_data` holds the I2C client, regmap, and a channel-to-register map that disables disconnected or errored inputs. `max6621_verify_reg_data()` translates PECI and device error codes into Linux errors. `max6621_read()`/`write()` implement temperature, offset, critical, and alarm handling. Regmap policy is defined by `max6621_writeable_reg()`, `max6621_readable_reg()`, `max6621_volatile_reg()`, defaults, and little-endian 16-bit values.

Control flow: probe initializes CONFIG0/CONFIG1 for all temperature channels, lockup timeout, PEC, and retry timing, syncs regcache, then probes each temperature register with raw SMBus word reads. Channels that return device/PECI errors are hidden by setting `input_chan2reg[i] = -1`. Runtime reads validate register values, convert the shifted signed temperature field, and clear alerts with SMBus send-byte when active.

State and persistence: regcache holds defaults and nonvolatile config, but temperature and alert registers are volatile. The channel map persists for the life of the device and controls sysfs visibility. Hardware retains offsets and critical thresholds.

Dependencies and integration points: uses hwmon, hwmon labels, I2C, regmap, OF compatible `maxim,max6621`, and SMBus send-byte for alert clear. It depends on PECI error-code semantics encoded in the hardware register values.

Risks and test signals: risks include channel offset math for critical thresholds (`channel -= 1`), suppressing channels permanently after transient startup errors, and alert reads that both report and clear hardware state. Tests should validate PECI error translations, hidden-channel visibility, signed temperature conversion, offset clamp behavior, alert-disabled returning zero rather than an error, and regmap access permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6639.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max6639.c` Research

Purpose: this I2C hwmon driver supports the MAX6639 two-channel temperature monitor and dual PWM fan-speed controller. It exposes fan speed/fault/pulses, PWM duty/frequency, temperature input/fault/limits/alarms, optional fan regulator control, device-tree fan settings, legacy I2C detection, and sleep PM.

Important APIs, types, and functions: `struct max6639_data` contains regmap, PPR, RPM range, target RPM, and optional `fan` regulator. Sensor callbacks are split into `max6639_read_fan()`, `write_fan()`, `read_pwm()`, `write_pwm()`, `read_temp()`, and `write_temp()`. `max6639_probe_child_from_dt()` parses child `fan` nodes. `max6639_init_client()` resets and configures default fan/temperature limits. `max6639_suspend()` and `max6639_resume()` toggle regulator and standby.

Control flow: probe initializes regmap and regulator, then reset/configures the chip. Initialization parses per-fan `reg`, `pulses-per-revolution`, `max-rpm`, and `target-rpm`, sets output mask, PPR, PWM/RPM configuration, polarity, full-speed therm behavior, default 80/90/100 C limits, and target duty derived from target RPM. Runtime reads use direct regmap reads, with temperature input assembled from extended and high bytes and PWM frequency from per-channel and global bits.

State and persistence: hardware holds configured limits and PWM settings. Driver state records selected PPR, RPM range, and target RPM; after `hwmon_fan_pulses` writes, the cached PPR is updated. Regmap caches nonvolatile registers and marks temperature/status/fan count/duty as volatile.

Dependencies and integration points: uses I2C/regmap/hwmon, OF child-node parsing, regulator framework, PM sleep ops, and optional legacy address scan/detect at `0x2c`, `0x2e`, `0x2f`.

Risks and test signals: risks include full chip reset in probe overwriting firmware settings, global PWM high-frequency bit shared by both channels, regulator enable/disable ordering, and channel-specific status bit reversal. Tests should exercise DT validation, init register sequences, frequency table selection, PPR range enforcement, suspend/resume with and without regulator, and detection id checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6639.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6650.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max6650.c` Research

Purpose: this I2C hwmon driver supports MAX6650/MAX6651 fan controllers. It exposes PWM open-loop control, closed-loop fan target, tachometer readings, divider/count setting, fan alarms, optional GPIO alarms, and thermal cooling-device control.

Important APIs, types, and functions: `struct max6650_data` keeps the client, mutex, fan count, one-second cache, speed/config/tach/count/DAC/alarm registers, alarm enable mask, and cooling state. `max6650_update_device()` refreshes tach and latches alarms. `max6650_set_operating_mode()` and `max6650_set_target()` write config/speed for mode and closed-loop target. `max6650_read()`/`write()` implement hwmon callbacks, and `max6650_set_cur_state()` implements thermal cooling by driving DAC/open-loop mode.

Control flow: probe determines one fan for MAX6650 or four for MAX6651 from match data, reads and optionally modifies voltage/prescaler from module parameters or firmware, caches speed/DAC/count/alarm enable, optionally sets a firmware target RPM, registers hwmon, then registers a thermal cooling device if thermal support is enabled. Reads use the cache for tach and alarms, translate DAC to PWM, and translate config mode to hwmon PWM enable values. Writes are serialized with `update_lock`.

State and persistence: hardware stores config, speed, DAC, count, and alarms. The software cache latches alarm bits because hardware clears some alarm state on read. The cooling-device state is stored in `cooling_dev_state`, but actual fan drive is still hardware DAC/mode.

Dependencies and integration points: uses I2C SMBus, hwmon and manual sysfs attributes, OF properties `maxim,fan-microvolt`, `maxim,fan-prescale`, `maxim,fan-target-rpm`, module parameters, and thermal cooling registration.

Risks and test signals: risks include module-parameter behavior overriding board defaults, inverse DAC/PWM math, alarm bits cleared as a side effect of reads, and thermal control racing with hwmon writes. Tests should validate fan-count visibility for MAX6650 vs MAX6651, prescaler/voltage validation messages, target RPM formula, PWM mode mapping, GPIO alarm visibility from `alarm_en`, and thermal state clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6697.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max6697.c` Research

Purpose: this I2C hwmon driver supports a family of Maxim multi-channel temperature sensors: MAX6581, MAX6602, MAX6622, MAX6636, MAX6689, MAX6693, MAX6694, MAX6697, MAX6698, and MAX6699. It exposes local/remote temperature inputs, max/min/crit limits, alarms, faults, and MAX6581-specific offset controls.

Important APIs, types, and functions: `enum chips` selects family behavior. `struct max6697_chip_data` describes channel count and supported ext/crit/fault/config bits. `struct max6697_data` stores regmap, type, chip metadata, extended-range temperature offset, and alarm state. `max6697_read()` and `max6697_write()` implement temperature/limit/offset operations. `max6697_config_of()` applies DT configuration, alert masks, over-temperature masks, resistance cancellation, beta compensation, transistor ideality, and extended range.

Control flow: probe initializes regmap, binds match data to chip capabilities, applies OF config or preserves existing configuration, then registers hwmon. Runtime reads assemble high/low temperature bytes when available, subtract `temp_offset`, and map status bits through chip-specific channel mapping. Writes clamp and offset limit values before writing per-channel registers. Visibility is capability-driven per channel and attribute.

State and persistence: hardware stores configuration, masks, limits, and offsets. Regmap uses MAPLE caching; temperature and status registers are volatile, while writeable registers exclude reserved and volatile addresses. `temp_offset` is software state derived from extended-range mode and used for all conversions.

Dependencies and integration points: uses I2C, regmap, hwmon, OF match data and properties such as `smbus-timeout-disable`, `extended-range-enable`, `beta-compensation-enable`, `alert-mask`, `over-temperature-mask`, `resistance-cancellation`, and `transistor-ideality`.

Risks and test signals: risks include family-specific bit mappings, MAX6581 datasheet revision differences for overtemperature bits, preserving firmware configuration when no DT node exists, and writing MAX6581 offset through a shared value register plus select bits. Tests should cover each chip-data capability mask, extended range offset conversions, status-bit mapping for channel 0/7, DT mask remapping, offset enable/disable, and reserved-register write protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max6697.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max77705-hwmon.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/max77705-hwmon.c` Research

Purpose: this platform hwmon child driver exposes voltage and current telemetry from the MAX77705 PMIC through the parent MFD regmap. It reports two voltage channels and two current channels, including an average current attribute for `ISYS`.

Important APIs, types, and functions: `struct channel_desc` describes the raw register, optional average register, label, and nano-unit resolution. `current_channel_desc[]` covers `IIN_REG` and `ISYS_REG`; `voltage_channel_desc[]` covers `VBYP_REG` and `VSYS_REG`. `max77705_read_and_convert()` handles regmap reads, optional signed extension, and nano-to-milli conversion with `mult_frac()`. `max77705_is_visible()`, `max77705_read_string()`, and `max77705_read()` implement hwmon callbacks.

Control flow: probe obtains the parent regmap with `dev_get_regmap(pdev->dev.parent, NULL)` and registers a `max77705` hwmon device. Reads choose the channel descriptor by hwmon type and channel, then convert current as signed 16-bit values and voltage as unsigned values. Labels are returned from the descriptor tables.

State and persistence: the driver has no private mutable state beyond using the parent regmap as `drvdata`. Hardware registers provide current values, and no cache is maintained.

Dependencies and integration points: depends on `linux/mfd/max77705-private.h` register definitions, regmap, platform bus, and hwmon. It is bound by platform driver name `max77705-hwmon` and is expected to be instantiated by the MAX77705 MFD core.

Risks and test signals: there is a suspicious visibility/read-string mix-up: current label handling uses `hwmon_in_label` in places where `hwmon_curr_label` would be expected. Tests should verify generated sysfs labels for current channels, signed current conversion for negative values, absence of average on channel 0, parent-regmap missing probe failure, and correct millivolt/milliamp scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/max77705-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mc13783-adc.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/mc13783-adc.c` Research

Purpose: this platform hwmon driver exposes ADC readings from Freescale/NXP MC13783 and MC13892 PMICs. It creates legacy sysfs attributes for input voltages, UID/battery-related input, and die temperature.

Important APIs, types, and functions: `struct mc13783_adc_priv` stores the parent `mc13xxx`, registered hwmon device, and shortened device name. `mc13783_adc_read()` performs an `mc13xxx_adc_do_conversion()` in multi-channel mode and extracts the requested 10-bit subchannel. Show helpers convert raw readings for BP, general-purpose inputs, UID, and temperature. Probe manually creates sysfs groups, then calls legacy `hwmon_device_register()`.

Control flow: probe picks behavior from platform id data (`MC13783_ADC_16CHANS`, `MC13783_ADC_BPDIV2`), derives the exported name from id before `-`, creates the base group, optionally creates extra 16-channel and touchscreen-free groups, and registers the hwmon device. Remove unregisters hwmon and removes exactly the groups that probe created.

State and persistence: no conversion cache is kept. Each sysfs read triggers a new PMIC ADC conversion. Group selection is persistent for the device lifetime and depends on platform id and parent touchscreen flags.

Dependencies and integration points: depends on the `mc13xxx` MFD API, platform ids `mc13783-adc` and `mc13892-adc`, legacy hwmon sysfs attributes, and `MC13XXX_USE_TOUCHSCREEN` flags from the parent to decide whether channels 12-15 are available.

Risks and test signals: risks include manual sysfs group cleanup paths, channel remapping for ADIN7 subchannels, and different scaling between MC13783 and MC13892. Tests should cover probe failure unwind at each group/register step, touchscreen flag hiding channels 12-15, raw extraction for channels above 16, BP/UID/temp conversion formulas for both chip variants, and conversion error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mc13783-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mc33xs2410_hwmon.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/mc33xs2410_hwmon.c` Research

Purpose: this auxiliary-bus hwmon driver exposes temperature telemetry for the NXP MC33XS2410 multi-channel high-side switch. It reports central die temperature and four channel temperatures, per-channel overtemperature warning alarms, and a writable warning threshold.

Important APIs, types, and functions: the driver uses the parent SPI device as hwmon data and calls exported MC33XS2410 helpers: `mc33xs2410_read_reg_diag()`, `mc33xs2410_read_reg_ctrl()`, and `mc33xs2410_modify_reg()`. `mc33xs2410_hwmon_read()` handles temperature input, alarm, and max threshold. `mc33xs2410_hwmon_write()` clamps and writes the threshold. `mc33xs2410_read_string()` returns fixed labels.

Control flow: the auxiliary driver binds to `pwm_mc33xs2410.hwmon`, derives the parent `spi_device`, and registers hwmon. Temperature reads use diagnostic registers: channel 0 maps to die temperature and channels 1-4 map to per-output temperature registers. Alarm reads check `MC33XS2410_OUT_STA_OTW` for the output channel. Threshold reads/writes use the shared control register `MC33XS2410_TEMP_WT`.

State and persistence: no driver-local cache exists. Hardware control and diagnostic registers hold all state. The overtemperature threshold is shared across output channels and persists in the chip until changed.

Dependencies and integration points: depends on the MC33XS2410 core header/API, SPI parent device, auxiliary bus, bitfield helpers, and hwmon. It is not an independent bus driver; it is a child function of the broader MC33XS2410 device.

Risks and test signals: alarm reads for channel 0 would compute `OUT_STA(0)` if requested, but channel 0 does not advertise alarm in the channel table. Tests should validate visibility for channel 0 vs channels 1-4, threshold clamp from `-40000` to `215000` mC, temperature conversion from quarter-degree units minus 40 C, label ordering, and error propagation from all parent register helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mc33xs2410_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mc34vr500.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/mc34vr500.c` Research

Purpose: this I2C hwmon driver monitors alarm bits from the NXP MC34VR500 PMIC. It exposes low input-voltage alarm and three temperature alarm levels; with an IRQ it also sends hwmon notifications when alarm status bits fire.

Important APIs, types, and functions: `struct mc34vr500_data` stores the hwmon device and regmap. `mc34vr500_process_interrupt()` reads `INTSTAT0`, sends `hwmon_notify_event()` for low VIN and thermal thresholds, then clears handled interrupts. `mc34vr500_alarm_read()` reads live `INTSENSE0` bits. `mc34vr500_probe()` initializes regmap, validates device id `0x14`, reads revision/fab id, registers hwmon, and configures optional IRQ handling.

Control flow: probe rejects nonmatching device IDs before registering. If `client->irq` is present, it requests a threaded IRQ, clears pending status bits, and unmasks LOWVINS/THERM110/120/130 bits. Sysfs reads do not consume interrupt status; they report sense register state.

State and persistence: there is no cache. Hardware interrupt/sense registers provide state. `hwmon_dev` is retained so the interrupt handler can notify userspace.

Dependencies and integration points: uses I2C, regmap, hwmon notifications, threaded IRQs, and OF compatible `nxp,mc34vr500`. It only monitors alarms; it does not expose measured voltage or temperature values.

Risks and test signals: the interrupt mask write uses bitwise complement cast to unsigned for an 8-bit register, so tests should verify only intended bits are unmasked by regmap/I2C behavior. Other tests should cover no-IRQ probe, IRQ notification and clear sequence, bad device ID rejection, live alarm reads from `INTSENSE0`, and ignored failures in the interrupt handler's final clear write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mc34vr500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mcp3021.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/mcp3021.c` Research

Purpose: this I2C hwmon driver exposes one voltage input from Microchip MCP3021 and MCP3221 ADCs. It reports the converted input in millivolts.

Important APIs, types, and functions: `struct mcp3021_data` stores the client, reference voltage in millivolts, SAR shift/mask, and output resolution. `volts_from_reg()` converts raw ADC code to millivolts. `mcp3021_read()` receives the two-byte big-endian conversion result and extracts either the MCP3021 10-bit code or MCP3221 12-bit code. `mcp3021_probe()` parses reference voltage and chip type, then registers hwmon.

Control flow: probe requires raw I2C transfer support, obtains `reference-voltage-microvolt` from DT or platform data/default, selects decoding constants based on match data, validates Vdd/reference range 2700-5500 mV, and registers a single `in0_input`. Reads call `i2c_master_recv()` and require exactly two bytes.

State and persistence: no cache or persistent software state beyond reference voltage and decode constants. Every sysfs read triggers a conversion read from the ADC.

Dependencies and integration points: uses raw I2C, hwmon, OF compatibles `microchip,mcp3021` and `microchip,mcp3221`, and legacy platform data for reference voltage.

Risks and test signals: risks are mostly data-format and scaling errors. Tests should cover MCP3021 vs MCP3221 bit extraction, default/reference-voltage parsing and range rejection, short I2C reads returning `-EIO`, unsupported hwmon attrs returning `-EOPNOTSUPP`, and full-scale conversion accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mcp3021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mcp9982.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/mcp9982.c` Research

Purpose: this I2C hwmon driver supports the Microchip MCP998X/33 and MCP998XD/33D multichannel automotive temperature monitor family. It exposes up to five temperature channels, labels, min/max/critical limits, alarms, hysteresis, update interval, and firmware-controlled diode/REC/power-state modes.

Important APIs, types, and functions: `struct mcp9982_features` captures per-chip channel count and feature constraints. `struct mcp9982_priv` stores regmap, labels, update interval index, enabled-channel mask, and mode booleans. `mcp9982_read_limit()`/`write_limit()` handle internal one-byte limits and external two-byte limits. `mcp9982_read()` includes standby one-shot conversion handling, temperature register reads, alarm status reads, and update interval reads. `mcp9982_init()` validates chip/mode constraints and writes default configuration and limits. `mcp9982_parse_fw_config()` parses firmware child channels and properties.

Control flow: probe allocates state, initializes cached regmap with read/write access tables, stores match-data features, parses firmware/default channels, initializes hardware defaults, then registers hwmon with a five-channel info table whose visibility hides disabled channels. In standby mode, reads of input/alarm attributes trigger one-shot conversion, wait for wake-up, and poll BUSY clear before reading.

State and persistence: hardware stores all limits, configuration, conversion interval, hysteresis, beta/ideality, and status. Driver state tracks enabled channels, labels, modes, and interval index. Regmap caches nonvolatile registers; status/temperature are volatile.

Dependencies and integration points: uses I2C, regmap access tables, hwmon, firmware property APIs, delay/poll helpers, and OF/I2C match tables for ten chip variants. Firmware properties include `microchip,enable-anti-parallel`, `microchip,parasitic-res-on-channel1-2`, `microchip,parasitic-res-on-channel3-4`, `microchip,power-state`, and child `channel` nodes with `reg`/`label`.

Risks and test signals: risks include many variant constraints, standby read latency, external limit byte packing, shared hysteresis register semantics, and child `reg` validation using `reg_nr >= device_nr_channels`, which can reject the highest external channel depending on numbering expectations. Tests should cover every feature struct, no-fwnode defaults, fwnode channel masks/labels, D-variant constraint failures, one-shot polling, min/max/crit limit round trips, update-interval clamping for D variants, and regmap access-table permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mcp9982.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/menf21bmc_hwmon.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/menf21bmc_hwmon.c` Research

Purpose: this platform hwmon child driver exposes five voltage rails monitored by the MEN 14F021P00 BMC: 3.3 V, 5 V, 12 V, standby 5 V, and VBAT. It reports input, minimum, maximum, and label attributes for each rail.

Important APIs, types, and functions: `struct menf21bmc_hwmon` stores validity, parent I2C client, last update, current input values, and fixed min/max arrays. `menf21bmc_hwmon_update()` refreshes input values once per second. `menf21bmc_hwmon_get_volt_limits()` reads static min/max limits at probe. `label_show()`, `in_show()`, `min_show()`, and `max_show()` back manually declared `SENSOR_DEVICE_ATTR_RO()` attributes.

Control flow: probe obtains the parent BMC I2C client, reads all min/max limits, and registers the hwmon device with static attribute groups. Input reads refresh current values if stale or invalid; min/max reads return cached probe-time limits.

State and persistence: current inputs are cached for up to one second; min/max limits are cached for the device lifetime. Hardware/BMC commands provide persistent values. There are no writes from this driver.

Dependencies and integration points: depends on a platform device created by the MEN BMC core, an I2C parent client, SMBus word reads at command ranges `0x40`, `0x50`, and `0x60`, and legacy hwmon groups.

Risks and test signals: the driver assumes BMC word values are already in hwmon units and does not byte-swap or scale. Tests should cover probe failure when any limit read fails, one-second input cache behavior, each command address mapping, parent I2C lookup, correct label strings, and static min/max caching after input refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/menf21bmc_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mlxreg-fan.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/mlxreg-fan.c` Research

Purpose: this platform hwmon driver exposes Mellanox/NVIDIA platform fan tachometers and PWM controls described by `mlxreg_core_platform_data`. It also registers thermal cooling devices for connected PWM outputs when thermal support is available.

Important APIs, types, and functions: `struct mlxreg_fan_tacho` stores tachometer register, fault mask, presence register, and shift. `struct mlxreg_fan_pwm` stores PWM register and thermal/hwmon state. `struct mlxreg_fan` stores regmap, platform data, arrays for up to 24 tachos and four PWMs, tachos-per-drawer, samples, and divider. `mlxreg_fan_read()`/`write()` implement hwmon. `_mlxreg_fan_set_cur_state()` arbitrates thermal and hwmon PWM state. `mlxreg_fan_config()` parses platform data labels `tacho`, `pwm`, and `conf`.

Control flow: probe reads platform data, configures connected tachos/PWMs and speed formula parameters, registers hwmon, then optionally registers a cooling device per PWM. Fan reads first check presence per drawer, then read tach register and return zero for absent or faulted values; otherwise RPM is calculated from register value, divider, and sample count. PWM writes enforce 20-100 percent duty and, when thermal is enabled, only lower hardware speed if the hwmon-requested state is not below thermal-requested state.

State and persistence: hardware registers store tach/PWM values and capabilities. Driver state records discovered connectivity and last hwmon/thermal states. There is no periodic cache.

Dependencies and integration points: depends on platform data from Mellanox regmap core, regmap, hwmon, optional thermal framework, and platform driver alias `mlxreg-fan`.

Risks and test signals: risks include parsing platform data by substring, a likely bounds typo comparing `pwm_num == MLXREG_FAN_MAX_TACHO` instead of max PWM, presence bit math with `rol32(channel, shift) / tachos_per_drwr`, and arbitration between thermal and hwmon. Tests should cover invalid/duplicate config labels, capability-based connection filtering, drawer/tacho validation, PWM-not-connected handling, duty/state conversions, thermal arbitration, and RPM formula edge cases for fault/min/max register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mlxreg-fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mr75203.c -->
# `sources/distributed-fs/ceph-client/drivers/hwmon/mr75203.c` Research

Purpose: this platform hwmon driver supports the MaxLinear/Moortec MR75203 PVT controller. It configures embedded temperature sensors, process detectors, and voltage monitors, then exposes temperature and voltage inputs through hwmon.

Important APIs, types, and functions: `struct pvt_device` stores common/temperature/process/voltage regmaps, clock/reset handles, debugfs root, voltage-channel mappings, temperature coefficients, counts, and IP frequency. `pvt_calc_temp()`, `pvt_read_temp()`, and `pvt_read_in()` convert sampled hardware data. `pvt_init()` programs clock synthesis and SDIF/IP control registers. `pvt_get_regmap()`, `pvt_get_active_channel()`, `pvt_get_pre_scaler()`, and `pvt_set_temp_coeff()` build runtime configuration from MMIO resources and firmware properties.

Control flow: probe maps the common region, enables clock, deasserts optional reset, reads `PVT_IP_CONFIG` counts, builds dynamic hwmon channel info, maps TS/PD/VM regions as present, parses temperature coefficients and VM channel mapping, initializes hardware, and registers a `pvt` hwmon device. Temperature and voltage reads poll sample-done bits, read sample data, mask to 16 bits, and convert to millidegrees or millivolts-ish voltage units using formulas and pre-scalers.

State and persistence: hardware MMIO registers hold controller state. Driver state records dynamic channel topology, VM mapping, pre-scalers, coefficients, and calculated IP clock frequency. Debugfs entries allow runtime adjustment of temperature coefficients, which affects subsequent conversions but is not persisted by the driver.

Dependencies and integration points: uses platform MMIO resources named `common`, `ts`, `pd`, and `vm`; regmap-mmio; clock and reset frameworks; firmware properties such as `moortec,vm-active-channels`, `moortec,vm-pre-scaler-x2`, `intel,vm-map`, and `moortec,ts-*`; debugfs; and OF compatible `moortec,mr75203`.

Risks and test signals: risks include global mutable static `pvt_temp`, `pvt_in`, and `pvt_chip_info` being patched per probe, which is fragile with multiple devices; complex clock-key calculation; firmware channel-map validation; and debugfs coefficient changes affecting conversion math. Tests should cover zero-sensor `-ENODEV`, dynamic channel counts, VM active-channel and map edge cases, pre-scaler bounds, temperature series defaults/overrides, SDIF timeout paths, reset action cleanup, and multi-instance registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/mr75203.c -->
