# subset-b-003838 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht4x.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sht4x.c

Purpose: I2C hwmon driver for Sensirion SHT4x humidity and temperature sensors. It exports `temp1_input`, `humidity1_input`, `update_interval`, plus custom heater controls for enable, power, and duration.

Important APIs, types, and functions: `struct sht4x_data` stores the I2C client, cached readings, jiffy timestamps, and heater state. `sht4x_read_values()` issues high precision measurements, waits for conversion or heater completion, receives six bytes, validates Sensirion CRC8 words, and converts raw ticks to millidegrees and millipercent. `sht4x_hwmon_read()`, `sht4x_hwmon_write()`, and `sht4x_hwmon_visible()` implement the hwmon callbacks; `heater_*_show/store()` implement extra sysfs attributes.

Control flow, state, and persistence: probe requires full I2C, initializes CRC table, resets the sensor, sets default interval 2000 ms and heater 200 mW for 1000 ms, then registers with `devm_hwmon_device_register_with_info()`. Runtime state is in memory only. Temperature and humidity are cached until `update_interval` expires, while heater mode tracks `heating_complete` and `data_pending` in jiffies.

Dependencies and integration points: uses I2C core, hwmon core, `hwmon-sysfs`, jiffies, sleep helpers, and Linux CRC8 support. Device matching is via I2C id `sht4x` and OF compatible `sensirion,sht4x`.

Risks and test signals: there is no mutex around cache and heater state, so concurrent sysfs reads/writes can race in theory. Heater enable only accepts writes of true and returns `-EBUSY` while active. Test with successful probe/reset, CRC failure injection, interval clamping, heater command selection, short I2C transfers returning `-ENODATA` or `-EIO`, and repeated reads proving cache suppression before the interval expires.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht4x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/shtc1.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/shtc1.c

Purpose: I2C hwmon driver for Sensirion SHTC1, SHTW1, and SHTC3 humidity and temperature sensors. It exposes read-only temperature and relative humidity attributes using the older hwmon groups API.

Important APIs, types, and functions: `struct shtc1_data` contains the client, `update_lock`, cache validity, selected command, nonblocking wait time, platform or device-tree setup, chip type, and cached readings. `shtc1_update_values()` sends the selected two-byte measurement command and reads six response bytes. `shtc1_update_client()` serializes updates, caches for `HZ / 10`, and converts raw big-endian words. `shtc1_select_command()` chooses blocking/nonblocking and high/low precision command variants.

Control flow, state, and persistence: probe requires plain I2C, reads and validates the chip ID with chip-specific masks, allocates data, defaults to nonblocking high precision, then overrides options from `sensirion,blocking-io`, `sensirion,low-precision`, or platform data. Runtime state is volatile cache only; no configuration is restored on remove.

Dependencies and integration points: uses I2C transfers rather than SMBus, hwmon groups, OF matching, and optional `linux/platform_data/shtc1.h`. I2C ids cover `shtc1`, `shtw1`, and `shtc3`; OF compatibles mirror those names.

Risks and test signals: the driver does not validate the two CRC bytes in measurement responses, so corrupted readings can pass through. Blocking I/O can hold the bus while the device stretches clock. Test detection for all IDs, DT/platform option selection, nonblocking delays, failed send/receive paths, cache reuse within 100 ms, and conversion formulas for temperature and humidity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/shtc1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sis5595.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sis5595.c

Purpose: legacy hwmon driver for the SiS5595 southbridge LM78-like monitoring block. It exposes voltage inputs and limits, two fans, optional temperature or fifth voltage input depending on revision and pin configuration, alarms, fan divisors, and device name.

Important APIs, types, and functions: `struct sis5595_data` holds the ISA base address, PCI revision, cache arrays, alarm bits, locks, and hwmon device. `sis5595_read_value()` and `sis5595_write_value()` serialize indexed ISA I/O port access. `sis5595_update_device()` refreshes cached registers about every 1.5 seconds. Sysfs show/store handlers convert voltage, fan RPM, fan divisor, and temperature values. `sis5595_pci_probe()` performs blacklist filtering, base address discovery or `force_addr`, hardware enable, and platform-device creation.

Control flow, state, and persistence: module init registers a PCI probe that deliberately returns failure after creating the platform device, so other drivers can still bind the PCI function. Probe reserves the ISA range, initializes the monitoring config, creates core plus optional sysfs groups, and registers a legacy hwmon device. Writable sysfs attributes immediately update both cache and hardware registers.

Dependencies and integration points: depends on PCI config access, ACPI resource checks, ISA I/O ports, platform devices, hwmon sysfs, and `I2C_CLASS_HWMON` style legacy conventions.

Risks and test signals: old hardware probing is fragile; blacklist coverage and ACPI conflict checks are critical. `FAN_FROM_REG(0)` returns `-1`, which user space must tolerate. Test forced and BIOS-provided addresses, rev1 versus rev2 temperature/IN4 selection, divisor changes preserving fan minimum, sysfs group cleanup, and unsupported-chip blacklist behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sis5595.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sl28cpld-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sl28cpld-hwmon.c

Purpose: platform hwmon driver for the Kontron SL28 CPLD fan counter. It exposes one read-only fan input.

Important APIs, types, and functions: `struct sl28cpld_hwmon` stores the parent regmap and register offset from the device property `reg`. `sl28cpld_hwmon_read()` reads the fan register, interprets the high bit as an x8 scale flag, extracts the 7-bit count with `FIELD_GET()`, and converts a one-second, two-pulse-per-revolution counter to RPM. The hwmon chip info declares only `HWMON_F_INPUT`.

Control flow, state, and persistence: probe requires a parent device and parent regmap, reads the child offset from firmware properties, then registers `sl28cpld_hwmon`. No state is cached or persisted by the driver.

Dependencies and integration points: integrates as an OF platform child compatible `kontron,sl28cpld-fan` under an MFD or parent exposing a regmap. Uses hwmon info API, regmap, platform device helpers, and property API.

Risks and test signals: a missing parent, regmap, or `reg` property fails probe. Conversion assumes 1000 ms counter period and two pulses per revolution. Test both scaled and unscaled register values, invalid property paths, and regmap read error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sl28cpld-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smpro-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/smpro-hwmon.c

Purpose: platform hwmon driver for Ampere Altra SMPro logical sensors. It exposes SoC, VRD, DIMM, and RCA temperature, voltage, current, and power channels with labels.

Important APIs, types, and functions: `struct smpro_hwmon` wraps the parent regmap. `struct smpro_sensor` maps each channel to a main register, optional extension register, and label. `smpro_read_temp()`, `smpro_read_in()`, `smpro_read_curr()`, and `smpro_read_power()` read regmap values and scale them into hwmon units. `smpro_read_string()` returns channel labels. `smpro_is_visible()` hides unavailable temperature channels when their register reads as `0xffff`.

Control flow, state, and persistence: probe allocates state, fetches the parent regmap, and registers with `devm_hwmon_device_register_with_info()`. There is no cache; each read queries the SMPro regmap. Threshold registers are read-only from this driver.

Dependencies and integration points: depends on a parent platform/MFD driver named `smpro-hwmon` that exposes a regmap. It uses hwmon info API, regmap, bit helpers, and fixed SMPro register contracts.

Risks and test signals: `smpro_is_visible()` only actively suppresses missing temperature channels; voltage/current/power channels are always visible even if platform firmware does not implement them. Temperature values use `sign_extend32(value, 8)`, so tests should verify signed register handling. Test register error propagation, label ordering, unavailable DIMM temperatures, and power aggregation from whole watt plus milliwatt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smpro-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smsc47b397.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/smsc47b397.c

Purpose: legacy Super-I/O hwmon driver for SMSC LPC47B397-compatible chips. It exposes four temperature inputs and four fan inputs.

Important APIs, types, and functions: `superio_enter()`, `superio_exit()`, `superio_inb()`, and `superio_select()` control configuration-space access at ports 0x2e/0x2f. `struct smsc47b397_data` stores the runtime I/O address, locks, cache validity, four fan counters, and four temperature registers. `smsc47b397_update_device()` refreshes all sensor registers once per second and reads fan LSB before MSB as required. `smsc47b397_find()` identifies supported chip IDs and extracts logical device 8 base address.

Control flow, state, and persistence: module init finds a supported Super-I/O device, registers the platform driver, adds a platform device with the detected I/O resource, and registers hwmon groups. Runtime state is volatile cache; no writable hwmon attributes are provided.

Dependencies and integration points: uses raw port I/O, `request_muxed_region()` for Super-I/O entry, ACPI resource conflict checks, platform devices, and hwmon groups.

Risks and test signals: base address zero is not explicitly rejected in `smsc47b397_find()`, so platform resource validity depends on hardware reporting a sane base. Fan conversion returns zero for stopped or invalid counter values. Test force_id override, supported ID matrix, ACPI conflicts, port reservation failures, fan LSB/MSB ordering, signed temperature conversion, and one-second cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smsc47b397.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smsc47m1.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/smsc47m1.c

Purpose: legacy Super-I/O hwmon driver for SMSC LPC47M1xx and related fan/PWM blocks. It exposes configured fan tachometers, fan minimums and divisors, PWM duty and enable controls, alarms, and chip name.

Important APIs, types, and functions: `struct smsc47m1_sio_data` preserves detected chip type and original activation state. `struct smsc47m1_data` holds base address, type, cache arrays, and hwmon device. `smsc47m1_find()` detects chip IDs and enables the logical fan device if needed. `smsc47m1_handle_resources()` checks or reserves only used I/O subranges. `smsc47m1_update_device()` refreshes fan/PWM/divisor/alarm cache and clears latched alarm bits. Store handlers update fan minimum, fan divisor, PWM duty, and PWM enable.

Control flow, state, and persistence: init detects Super-I/O, creates a platform device, and probes once through `platform_driver_probe()`. Probe checks pin configuration before exposing only actually enabled fan and PWM groups. On exit or probe failure it restores the Super-I/O activation bit if the driver enabled it.

Dependencies and integration points: uses port I/O, ACPI resource checks, platform devices, sysfs groups, and legacy `hwmon_device_register()`.

Risks and test signals: alarms are cleared during cache refresh, which affects repeated reads. PWM disabled at 0 percent can suppress tach monitoring. Test pin-config gating, LPC47M292 third-channel paths, resource-region subsets, restore-on-exit, fan divisor changes preserving minimum RPM, invalid PWM and divisor writes, and cleanup after partial sysfs group creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smsc47m1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smsc47m192.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/smsc47m192.c

Purpose: I2C hwmon driver for the SMSC LPC47M192 monitoring block. It exposes eight voltage channels, three temperature channels with offsets and limits, VID/VRM attributes, and alarms/faults.

Important APIs, types, and functions: `struct smsc47m192_data` contains the client, dynamic attribute group list, cached register arrays, combined alarms, VID, and VRM. `smsc47m192_update_device()` refreshes all inputs, limits, offsets, VID, config, and alarm registers every 1.5 seconds. Conversion helpers scale nominal voltage rails and signed temperature registers. Store handlers write voltage limits, temperature limits, offsets, and VRM. `smsc47m192_init_client()` starts monitoring and initializes limits when not already configured.

Control flow, state, and persistence: detection scans 0x2c and 0x2d using manufacturer/version/VID sanity checks. Probe allocates data, initializes the chip, conditionally exposes IN4 depending on config bit 5, and registers hwmon groups. Writes persist in device registers until hardware reset or later user writes; cache mirrors the latest store.

Dependencies and integration points: uses SMBus byte data, hwmon sysfs, `hwmon-vid`, I2C detection class, and dynamic group selection.

Risks and test signals: offset registers for temp1 and temp2 share hardware state via SFR bit 4, so stores can clear the alternate offset. SMBus reads are not checked inside update for every value. Test detection filters, IN4 versus VID4 group selection, shared offset switching, VID5 handling, VRM validation, alarm bit mapping, and initialization of disabled chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/smsc47m192.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sparx5-temp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sparx5-temp.c

Purpose: platform hwmon driver for the Microchip Sparx5 SoC temperature sensor. It exposes a single temperature input and registers the channel as eligible for thermal-zone use.

Important APIs, types, and functions: `struct s5_hwmon` stores the MMIO base and enabled clock. `s5_temp_enable()` programs the conversion cycle field from the clock rate and sets the enable bit. `s5_read()` checks the valid bit in `TEMP_STAT`, extracts the 12-bit raw temperature, applies the documented linear conversion, and returns millidegrees. `s5_is_visible()` exposes only `temp1_input`.

Control flow, state, and persistence: probe allocates state, maps MMIO resource 0, enables the clock with `devm_clk_get_enabled()`, enables the sensor, and registers hwmon info. No software cache is maintained; every read hits MMIO.

Dependencies and integration points: uses platform devices, OF compatible `microchip,sparx5-temp`, MMIO accessors, clock framework, bitfield helpers, and hwmon thermal-zone registration flag.

Risks and test signals: reads return `-EAGAIN` until hardware marks data valid. Conversion depends on clock rate and register specification. Test invalid MMIO/clock probe paths, cycle field programming, valid-bit gating, raw-to-millidegree conversion at low/mid/high raw values, and integration with thermal zone registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sparx5-temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/spd5118.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/spd5118.c

Purpose: I2C hwmon and nvmem driver for JEDEC SPD5118 DDR5 module temperature sensors and SPD EEPROM access. It exposes current temperature, programmable min/max/crit/lcrit limits, alarms, enable, and read-only EEPROM contents.

Important APIs, types, and functions: `struct spd5118_data` stores the regmap, nvmem lock, and 8-bit versus 16-bit addressing mode. `spd5118_read_temp()`, `spd5118_write_temp()`, `spd5118_read_alarm()`, and `spd5118_write_enable()` implement hwmon access. `spd5118_nvmem_read()` serializes and splits EEPROM reads on 128-byte page boundaries. Regmap configs model 8-bit paged legacy addressing or native 16-bit addressing. `spd5118_common_probe()` validates capability, revision, and JEP106-style vendor parity before registering nvmem and hwmon.

Control flow, state, and persistence: I2C init verifies device type and handles chips that boot with a nonzero legacy page selected. Probe preserves BIOS-selected addressing mode, rejects 16-bit mode without full I2C support, and registers hwmon. Suspend disables the temperature sensor while keeping regcache coherent; resume syncs cached configuration back.

Dependencies and integration points: uses I2C, optional detection on DDR5 SPD addresses, regmap with cache/ranges, nvmem provider, hwmon thermal-zone flag, PM ops, and JEDEC-compatible OF matching.

Risks and test signals: address-mode handling is subtle; changing BIOS-selected mode is intentionally avoided. Alarm reads clear latched bits. Test 8-bit page windows, 16-bit I2C-only mode, page-crossing nvmem reads, vendor parity rejection, capability filtering, suspend/resume cache sync, and optional detection disabled by Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/spd5118.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/stts751.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/stts751.c

Purpose: I2C hwmon driver for ST STTS751 temperature sensors. It provides temperature input, min/max event limits, therm critical limit and hysteresis, alarm flags, update interval, and SMBus alert support.

Important APIs, types, and functions: `struct stts751_priv` stores client, locks, config, interval/resolution, cached temperatures and alarms, timestamps, and notification flags. `stts751_update_temp()` performs high-low-high reads to avoid torn conversions. `stts751_update_alert()` handles status bits that clear on read and maintains a cache across conversion intervals. `stts751_alert()` reacts to SMBus alerts with sysfs notifications and uevents. Store handlers update limits, hysteresis, therm threshold, and conversion interval.

Control flow, state, and persistence: detection validates manufacturer, product, reserved bits, and timeout register shape. Probe optionally sets `smbus-timeout-disable`, reads revision/config/limits, clears STOP and event-disable bits, then registers hwmon groups. Runtime state is protected by `access_lock`; hardware thresholds persist in device registers.

Dependencies and integration points: uses SMBus byte data, I2C alert protocol, hwmon sysfs, device properties, `find_closest_descending()`, and OF compatible `st,stts751`.

Risks and test signals: alarm flags clear on status reads, making cache timing important. Interval changes also adjust resolution in a conservative order. Test alert handling, sysfs poll wakeups, limit clamping, hysteresis relative to therm, invalid conversion-rate rejection, update interval to resolution mapping, and communication failure fallback that asserts both alarms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/stts751.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/surface_fan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/surface_fan.c

Purpose: Surface System Aggregator Module hwmon driver exposing Surface fan RPM as `fan1_input`.

Important APIs, types, and functions: `SSAM_DEFINE_SYNC_REQUEST_CL_R(__ssam_fan_rpm_get, __le16, ...)` defines the synchronous controller request for target category FAN command 0x01. `surface_fan_hwmon_read()` retrieves the `ssam_device` from driver data, sends the request, converts little-endian RPM, and returns it through hwmon. The channel info declares one fan input with fixed read-only visibility.

Control flow, state, and persistence: probe directly registers `surface_fan` with hwmon info using the SSAM device as driver data. There is no cache, no writable state, and no persistence. Each read synchronously asks firmware.

Dependencies and integration points: depends on Surface Aggregator device bus and controller request helpers, SSAM device id `SSAM_SDEV(FAN, SAM, 0x01, 0x01)`, and hwmon core. Probe is marked asynchronous-preferred.

Risks and test signals: user reads block on SSAM command completion and propagate firmware errors. Test SSAM match/probe, little-endian conversion, command failure propagation, repeated reads, and behavior when firmware reports zero RPM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/surface_fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/surface_temp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/surface_temp.c

Purpose: Surface System Aggregator Module hwmon driver for firmware-provided thermal sensors. It exposes up to 16 labeled temperature channels.

Important APIs, types, and functions: `ssam_tmp_get_available_sensors()` reads a 16-bit availability bitmask. `ssam_tmp_get_temperature()` requests channel temperatures and converts firmware units from tenths Kelvin to millidegrees Celsius. `ssam_tmp_get_name()` fetches fixed-size sensor names and rejects non-terminated strings. `struct ssam_temp` stores the SSAM device, bitmask, and channel names. HWMON callbacks gate visibility by the bitmask, read temperatures, and return labels.

Control flow, state, and persistence: probe reads available sensors, allocates state, fetches labels for every set bit using channel IDs offset by one, and registers `surface_thermal`. There is no temperature cache; labels and availability are captured at probe.

Dependencies and integration points: depends on the Surface Aggregator device bus/controller, SSAM TMP target category commands, hwmon info API, and thermal-zone registration flag.

Risks and test signals: firmware name formatting is validated strictly; bad strings fail probe. Availability changes after probe are not reflected. Test bitmask visibility, Kelvin-to-Celsius conversion including negative Celsius values, label fetch errors, all 16 channel slots, and SSAM command failures during probe and reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/surface_temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sy7636a-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sy7636a-hwmon.c

Purpose: platform hwmon child for the SY7636A MFD, exposing the PMIC thermistor readout as a temperature channel.

Important APIs, types, and functions: `sy7636a_read()` reads `SY7636A_REG_TERMISTOR_READOUT` through the parent regmap and scales the register value by 1000 to hwmon millidegrees. `sy7636a_is_visible()` only exposes `hwmon_temp_input`. `sy7636a_sensor_probe()` obtains the parent regmap, enables the `vcom` regulator, and registers `sy7636a_temperature`.

Control flow, state, and persistence: probe defers if no parent regmap exists, requires regulator enable success, then registers hwmon. No cache or writable state is kept by this driver.

Dependencies and integration points: integrates with the `sy7636a` MFD header, parent regmap, regulator framework, platform alias `sy7636a-temperature`, and hwmon thermal-zone flag.

Risks and test signals: the sensor depends on `vcom` being enabled, so regulator errors block hwmon registration. Scaling assumes the MFD register already reports degrees C units. Test probe deferral, regulator failure, regmap read errors, normal conversion, and platform alias autoload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sy7636a-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tc654.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tc654.c

Purpose: I2C hwmon driver for Microchip TC654/TC655 fan speed controllers. It exposes two fan RPM channels, fan fault thresholds and alarms, fan pulses-per-rotation, PWM mode, PWM duty, and optional thermal cooling-device control.

Important APIs, types, and functions: `struct tc654_data` stores the client, update lock, one-second cache, RPM outputs, fault thresholds, config/status, and duty cycle. `tc654_update_client()` refreshes all registers and encodes errors as `ERR_PTR`. Sysfs handlers convert RPM resolution, threshold units, pulse config, shutdown mode, and duty-cycle map. `_set_pwm()` updates shutdown/config and duty registers. Thermal callbacks map cooling states 0..16 to fan-off or 16 PWM levels.

Control flow, state, and persistence: probe checks SMBus byte support, reads initial config, registers hwmon groups, then optionally registers a thermal cooling device using OF node data. Writable attributes update hardware immediately and mirror cache fields.

Dependencies and integration points: uses I2C SMBus byte data, hwmon sysfs, thermal framework when enabled, `find_closest()`, and I2C ids `tc654`/`tc655`.

Risks and test signals: `_set_pwm()` writes config before duty; a duty write failure can leave shutdown cleared or set. RPM scaling depends on config resolution bit. Test all writable range checks, pulse values 1/2/4/8, PWM map closest selection, cooling-state clamp, cache refresh, and fault bit mapping for both fans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tc654.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tc74.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tc74.c

Purpose: simple I2C hwmon driver for Microchip TC74 temperature sensors. It exposes read-only `temp1_input`.

Important APIs, types, and functions: `struct tc74_data` stores the client, interruptible mutex, cache validity, next update time, and signed 8-bit temperature. `tc74_update_device()` reads the config register, checks the ready bit, reads temperature, and caches it for 250 ms. `temp_input_show()` calls the update helper and scales degrees C to millidegrees.

Control flow, state, and persistence: probe requires SMBus byte data, allocates state, verifies reserved config bits are zero, clears standby bit if set, and registers hwmon groups. Runtime state is only the cache; clearing standby modifies device state but is not restored on remove.

Dependencies and integration points: uses I2C SMBus byte data, hwmon sysfs groups, jiffies, and mutex locking. Matching is via I2C id `tc74`.

Risks and test signals: reads return `-EAGAIN` while the ready bit is clear. Probe warns but continues if clearing standby fails. Test invalid config rejection, standby clear path, signed negative temperatures, cache timing, interruptible lock interruption, and read error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tc74.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/thmc50.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/thmc50.c

Purpose: I2C hwmon driver for THMC50 and ADM1022 temperature monitors. It exposes two base temperature channels, optional ADM1022 third temperature channel, temperature limits/critical values, alarms/faults, and a DC PWM analog output.

Important APIs, types, and functions: `struct thmc50_data` stores client, dynamic groups, chip type, optional temp3 mode, cache, temperature registers, analog output, and alarms. `thmc50_update_device()` refreshes data after 200 ms for ADM1022 or about 1.2 seconds for THMC50. `thmc50_detect()` validates company/revision/config and can enable ADM1022 temp3 mode via the `adm1022_temp3` module parameter. `thmc50_init_client()` starts the chip and ensures analog output is nonzero.

Control flow, state, and persistence: probe initializes hardware, builds the group list with optional temp3 attributes, and registers hwmon groups. Store handlers update min/max temperatures and analog output; analog output also toggles the fan-off config bit.

Dependencies and integration points: uses I2C class scanning at 0x2c-0x2e, SMBus byte data, module parameter pairs for ADM1022 temp3, and hwmon sysfs.

Risks and test signals: update reads do not check every SMBus return before caching. ADM1022 temp3 enable is controlled by adapter/address pairs and writes config during detection. Test both company IDs, temp3 parameter parsing, analog output zero behavior, nFANOFF updates, alarm bit mapping, cache timeout differences, and min/max clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/thmc50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp102.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tmp102.c

Purpose: I2C hwmon driver for TI TMP102 temperature sensors. It exposes temperature input, high limit, low hysteresis limit, optional label, and update interval.

Important APIs, types, and functions: `struct tmp102` stores label, regmap, original config, first-conversion ready time, and selected sample time. Conversion helpers translate left-adjusted 13-bit register values to and from millidegrees. `tmp102_read()` and `tmp102_write()` route chip and temp attributes. `tmp102_update_interval()` maps requested intervals to supported conversion-rate bits. `tmp102_restore_config()` restores original config through a devm action.

Control flow, state, and persistence: probe requires SMBus word transactions, optionally enables `vcc`, creates a big-endian 16-bit regmap, validates config reserved bits, saves original config, sets thermostat/extended/conversion mode bits, delays reads until first conversion, and registers hwmon. Suspend sets shutdown; resume clears it and resets ready time.

Dependencies and integration points: uses regmap, optional regulator, OF `label`, OF compatible `ti,tmp102`, PM ops, and hwmon thermal-zone registration.

Risks and test signals: initial reads can return `-EAGAIN`. The sample-time array is static and update interval writes must keep config bits byte-swapped correctly. Test config validation, regulator optional paths, restore action, suspend/resume, label visibility, update interval mapping, and limit clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp103.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tmp103.c

Purpose: I2C hwmon driver for TI TMP103 temperature sensors. It exposes current temperature and writable min/max thresholds.

Important APIs, types, and functions: the driver uses a simple 8-bit regmap with volatile temperature register. `tmp103_read()` maps `hwmon_temp_input`, `hwmon_temp_min`, and `hwmon_temp_max` to TEMP, TLOW, and THIGH registers. `tmp103_write()` clamps thresholds to -55 C through 127 C and writes rounded degree-C register values. `tmp103_probe()` initializes config bits for conversion rate and shutdown/mode selection before registering hwmon.

Control flow, state, and persistence: probe initializes regmap, writes config with `regmap_update_bits()`, stores the regmap as client data, and registers hwmon info. Suspend and resume update mode bits through `TMP103_CONF_SD_MASK`; thresholds remain in hardware registers.

Dependencies and integration points: uses I2C, regmap, hwmon info API, OF compatible `ti,tmp103`, and simple PM ops.

Risks and test signals: the file does not explicitly check adapter SMBus functionality before regmap operations. Temperature precision is whole-degree only. Test config write failures, signed conversion for negative temperatures, min/max clamping, visibility modes, suspend/resume mode bit values, and regmap read/write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp103.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp108.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tmp108.c

Purpose: hwmon driver for TI TMP108 and NXP P3T1035/P3T1085 temperature sensors over I2C and I3C. It exposes temperature input, min/max thresholds, alarms, update interval, and hysteresis where supported.

Important APIs, types, and functions: `struct tmp108` stores regmap, original config, ready time, and variant parameters. `struct tmp108_params` selects 8-bit versus 16-bit config register behavior and supported sample times. HWMON callbacks implement temperature, alarm, hysteresis, and update-interval reads/writes. Custom `tmp108_i2c_regmap_bus` and `tmp108_i3c_regmap_bus` handle byte/word differences and I3C transfers. `tmp108_common_probe()` centralizes regulator, config, restore, and hwmon registration.

Control flow, state, and persistence: I2C probe checks SMBus byte and word support; I3C probe matches device IDs. Common probe enables `vcc`, saves config, forces continuous comparator mode, schedules first-conversion wait if waking from shutdown, registers a config restore action, and registers hwmon. PM suspend/resume toggles shutdown and continuous mode.

Dependencies and integration points: uses I2C, I3C, regmap, regulator, OF and I3C IDs, hwmon thermal-zone flag, and `module_i3c_i2c_driver()`.

Risks and test signals: variant-specific config width is easy to regress. Hysteresis writes translate absolute threshold-relative requests into coarse 0/1/2/4 C config bits. Test I2C and I3C transfer encodings, p3t1035 hysteresis invisibility, sample-time mapping, first-read `-EAGAIN`, config restore, alarms from volatile config, and PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp401.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tmp401.c

Purpose: I2C hwmon driver for TI TMP401, TMP411, TMP431, TMP432, and TMP435 local/remote temperature sensors. It exposes local and remote temperatures, min/max/critical thresholds, alarms/faults, optional history, update interval, and variant-specific channels.

Important APIs, types, and functions: `struct tmp401_data` stores client, regmap, chip kind, extended-range flag, and dynamically built hwmon channel config. Custom regmap read/write callbacks handle mixed byte/word registers, write-address aliases, TMP411/TMP432 register overlap, and simulated per-channel status registers. `tmp401_temp_read/write()` and `tmp401_chip_read/write()` implement hwmon behavior. `tmp401_init_client()` sets conversion rate, clears shutdown, handles DT `ti,extended-range-enable`, `ti,n-factor`, and `ti,beta-compensation`.

Control flow, state, and persistence: detection checks manufacturer/device IDs, legal addresses, config reserved bits, and conversion rate. Probe builds channel config by chip kind, initializes hardware, and registers hwmon info. Writes update hardware registers; no software cache is kept beyond regmap cache.

Dependencies and integration points: uses SMBus byte/word operations via regmap, I2C class scanning, OF matching, and hwmon info API.

Risks and test signals: custom register aliasing is the main risk. TMP432 has a third channel and real status registers, while other variants simulate them from the shared status register. Test each device ID/address rule, extended range conversion, critical hysteresis math, history reset, n-factor/beta validation, write-address remapping, and TMP411 high/low history channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp421.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/tmp421.c

Purpose: I2C hwmon driver for TI TMP421, TMP422, TMP423, TMP441, and TMP442 multi-channel temperature sensors. It exposes temperature input, fault, enable, and optional channel labels for two to four channels depending on chip.

Important APIs, types, and functions: `struct tmp421_data` stores client, dynamic hwmon config, cache state, channel count, config register, and per-channel label/enabled/temp. `tmp421_update_device()` refreshes config and channel MSB/LSB values every 500 ms. `tmp421_enable_channels()` writes remote-enable bits in config register 2. `tmp421_probe_child_from_dt()` handles per-channel `reg`, `label`, availability, and `ti,n-factor`. `tmp421_read/write()` implement hwmon input/fault/enable attributes.

Control flow, state, and persistence: probe derives channel count from match data, enables all channels by default, applies DT child overrides, sets conversion rate to 2 Hz, clears shutdown, writes enable bits, then registers hwmon. Channel enable state is stored in memory and hardware register 2.

Dependencies and integration points: uses SMBus byte data, I2C class scanning, OF child nodes named `channel`, and hwmon info API.

Risks and test signals: `tmp421_write()` assigns `enabled = val` without validating val as boolean before programming hardware. Disabled channels remain visible but reads return `-ENODATA` for input/fault. Test detection ID/address constraints, extended-range conversion, DT invalid reg and n-factor errors, channel labels, enable writes for nonzero values, status fault bits, and cache expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/tmp421.c -->
