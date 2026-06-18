# subset-b-003837 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ucd9000.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ucd9000.c

Purpose: PMBus hwmon driver for TI UCD90xxx sequencer/system health controllers. It discovers configured rails, maps monitor configuration entries into PMBus capabilities, adds special fan support for UCD90124, optional GPIO support for devices with GPIO pins, and debugfs exposure for manufacturer status and GPI alarms.

Important APIs/types/functions: `struct ucd9000_data` embeds `pmbus_driver_info`, cached fan blocks, optional `gpio_chip`, and debugfs root. `ucd9000_probe()` is the main setup path. PMBus hooks include `ucd9000_read_byte_data()` for synthesized fan config bytes. GPIO helpers select `UCD9000_GPIO_SELECT`, read/write `UCD9000_GPIO_CONFIG`, and implement direction/value callbacks. Debugfs helpers read `UCD9000_MFR_STATUS`.

Control flow: probe validates SMBus byte/block support, reads `UCD9000_DEVICE_ID`, matches against supported IDs, reads active pages, seeds page 0 with internal temperature, parses `UCD9000_MONITOR_CONFIG`, optionally reads fan config blocks, registers GPIOs, calls `pmbus_do_probe()`, then creates debugfs files.

State and persistence: driver state is devm-managed. PMBus functionality is static after probe except cached fan config. GPIO operations persist hardware output direction/value through PMBus manufacturer registers. Debugfs reads live device status. UCD90320 gets `info->write_delay = 500us` to mitigate access failures after writes.

Dependencies/integration: depends on I2C SMBus, PMBus core, gpiolib, debugfs, OF/I2C matching, and PMBus debugfs directory support.

Risks: device ID matching is string-prefix based; monitor config beyond valid pages is ignored; GPIO lacks pinmux integration; debugfs GPI bit indexing assumes MFR status layout; UCD90320 reliability depends on empirical delay.

Test signals: probe logs showing device ID/pages, populated PMBus attributes per monitor type, UCD90124 fan config reads, GPIO direction/value sysfs or gpiod tests, debugfs `mfr_status` and `gpi*_alarm`, and stress reads around UCD90320 writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ucd9000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ucd9200.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ucd9200.c

Purpose: PMBus hwmon driver for TI UCD9200/UCD922x/UCD924x digital PWM system controllers. It detects the concrete chip, derives configured rails from the PHASE_INFO block, programs PHASE registers so per-rail reads aggregate all phases, and registers PMBus capabilities.

Important APIs/types/functions: `enum chips`, `ucd9200_id`, OF match table, and `ucd9200_probe()` form the full driver. `pmbus_driver_info` is allocated per client and filled with page count and `func[]` capability masks.

Control flow: probe checks SMBus byte/block support, reads `UCD9200_DEVICE_ID`, resolves the supported device, warns on configured/detected mismatch, reads `UCD9200_PHASE_INFO`, counts sequential nonzero rails, then for each page retries PAGE/PHASE writes up to three times with `PMBUS_PHASE = 0xff`. It then exposes input/current/power/temp capabilities and UCD9240 fan support before `pmbus_do_probe()`.

State and persistence: no custom runtime cache beyond PMBus core state. The probe-time PHASE programming persists in hardware so later PMBus reads report all phases for a rail.

Dependencies/integration: I2C SMBus, PMBus core, OF/I2C tables. It relies on PMBus core for all sensor reads after registration.

Risks: OF compatible strings are `ti,cd92xx` rather than the ID table names, so binding compatibility must be intentional. Rails must be sequential; nonzero rails after a zero entry are ignored. PAGE/PHASE writes are known flaky and only retried three times.

Test signals: device ID and rail count logs, PHASE retry behavior on marginal hardware, PMBus values for multi-phase READ_IOUT/READ_TEMPERATURE2, and UCD9240 fan attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ucd9200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdp710.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdp710.c

Purpose: PMBus driver for Infineon XDP710 hot-swap controllers. It supplies direct-format scaling coefficients and adapts voltage/current/power scaling from device configuration registers.

Important APIs/types/functions: static `xdp710_info` defines one-page PMBus formats, coefficients, and capability bits. `xdp710_probe()` copies that template, reads `XDP710_CS_RNG`, `XDP710_V_SNS_CFG`, and `XDP710_REG_CFG`, and adjusts coefficients.

Control flow: probe creates a per-device `pmbus_driver_info`, reads current-sense range and voltage telemetry range, indexes the six-bit sense-resistor configuration through `micro_ohm_rsense[]`, shifts voltage `m` coefficients by voltage range, scales current/power `m` coefficients by sense resistor and current-sense range, then calls `pmbus_do_probe()`.

State and persistence: only per-client PMBus coefficient state persists. No runtime cache or writable hardware state is kept by the driver.

Dependencies/integration: I2C word reads, PMBus core, OF and I2C matching. The core performs all normal PMBus reads using the adjusted direct-format data.

Risks: register field interpretation drives all scaling accuracy. The resistor table assumes all 64 encoded values are valid. Errors are fatal during probe, so hardware that NACKs manufacturer registers cannot expose even basic telemetry.

Test signals: coefficient changes for representative `CS_RNG`, `V_SNS_CFG`, and resistor encodings; sensible VIN/VOUT/IOUT/PIN units; probe failures on missing registers; DT/I2C match coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdp710.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdp720.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdp720.c

Purpose: PMBus hwmon driver for Infineon XDP720 digital eFuse controllers. It exposes one PMBus page and computes current/power scaling from device telemetry gain and board RIMON resistor configuration.

Important APIs/types/functions: `xdp720_info` is the PMBus template. `xdp720_probe()` enables the optional `vdd-vin` regulator, reads `XDP720_TELEMETRY_AVG`, parses the GIMON bit, reads `infineon,rimon-micro-ohms`, updates coefficients with 64-bit division, and registers PMBus.

Control flow: after allocating a copy of the template, probe requires regulator enable success, reads telemetry gain, chooses 18.2 or 9.1 microA/A, falls back to a 2 kOhm RIMON default, rejects zero RIMON, scales current/power `m` values, then calls `pmbus_do_probe()`.

State and persistence: devm regulator enable persists for the device lifetime; coefficient state is fixed after probe.

Dependencies/integration: PMBus core, regulator consumer API, OF property parsing, I2C word reads, 64-bit math helpers.

Risks: RIMON property units and default value are critical for correct telemetry. A missing regulator provider blocks probe. The driver trusts one telemetry bit for GIMON and does not validate reserved values beyond that bit.

Test signals: regulator enable path, DT property parsing including zero rejection, current/power readings under both GIMON modes, and PMBus status/temp/input attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdp720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe12284.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe12284.c

Purpose: PMBus driver for Infineon XDPE11280/XDPE12254/XDPE12284 multi-phase VR controllers. It supports two pages, linear PMBus telemetry, VID-format VOUT handling, and optional regulator descriptors.

Important APIs/types/functions: `xdpe122_identify()` determines VOUT format and VRM versions. `xdpe122_read_word_data()` maps VOUT fault limit reads from LINEAR11 register values to VID values for VR13, VR12, IMVP9, and AMD 6.25 mV modes. `xdpe122_info` provides capabilities and optional `PMBUS_REGULATOR()` descriptors.

Control flow: probe copies `xdpe122_info` and invokes PMBus core. During PMBus identification, the driver reads `PMBUS_VOUT_MODE`: linear format exits early; VID format installs the custom read hook and decodes per-page VOUT parameters to `info->vrm_version[]`.

State and persistence: per-device PMBus metadata stores format, read hook, VRM version, and optional regulator mapping. No extra cache exists.

Dependencies/integration: PMBus core, regulator framework under `CONFIG_SENSORS_XDPE122_REGULATOR`, I2C/OF IDs.

Risks: invalid VOUT_MODE encodings fail identification. The custom conversion only handles OV/UV fault limits; unsupported VID modes return errors. Per-page mode reads assume exactly two pages.

Test signals: linear and VID VOUT mode probes, limit conversion for each supported VRM mode, regulator registration when enabled, and PMBus readings for both pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe12284.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe152c4.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe152c4.c

Purpose: compact PMBus driver for Infineon XDPE152C4/XDPE15284 VR controllers. It exposes two linear-format PMBus pages with voltage, current, power, input, and temperature capabilities.

Important APIs/types/functions: `xdpe152_info` is the driver’s primary contract: two pages, linear formats for all supported classes, page-specific `func[]` masks. `xdpe152_probe()` copies that template and delegates to PMBus core.

Control flow: I2C/OF matching selects the driver, probe allocates a per-client `pmbus_driver_info` copy, and `pmbus_do_probe()` handles all PMBus discovery and sysfs creation.

State and persistence: only PMBus core state persists. The driver does not cache telemetry, write registers, or implement custom read/write hooks.

Dependencies/integration: I2C, OF matching, PMBus core.

Risks: capabilities are static and assume the hardware exposes the listed sensors on both pages. There is no chip-specific runtime validation or format negotiation.

Test signals: successful probe for both IDs, visible two-page PMBus attributes, linear-format value sanity, and error-free module namespace import for PMBus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe152c4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe1a2g7b.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe1a2g7b.c

Purpose: PMBus driver for Infineon XDPE1A2G5B/XDPE1A2G7B multi-phase VR controllers. It supports two pages and identifies whether VOUT is linear or NVIDIA PWM VID.

Important APIs/types/functions: `xdpe1a2g7b_identify()` reads page 0 `PMBUS_VOUT_MODE`, selects linear or VID format, and sets `nvidia195mv` VRM version for both pages when the VID code type is supported. `xdpe1a2g7b_info` holds capabilities and the identify callback.

Control flow: probe copies the info template and calls PMBus core. During PMBus identification, VOUT mode bits choose format; unsupported VID parameters return `-EINVAL`, and unsupported mode classes return `-ENODEV`.

State and persistence: per-client PMBus info stores format and VRM version; comments note the loops are not fully independent and should not be programmed separately.

Dependencies/integration: PMBus core and I2C/OF matching. VOUT VID semantics depend on PMBus core VRM conversion support for `nvidia195mv`.

Risks: only one NVIDIA VID code type is accepted. Page 1 inherits page 0 configuration, which is intentional for shared device configuration but risky if future hardware has independent pages.

Test signals: linear and NVIDIA VID probes, VOUT readings on both pages, rejection of unsupported VOUT params, and PMBus sysfs visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/xdpe1a2g7b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/zl6100.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/zl6100.c

Purpose: PMBus driver for ZL6100-compatible digital power controllers and Ericsson BMR aliases. It detects device IDs, applies mandatory inter-access delays, exposes standard PMBus telemetry, and maps manufacturer VMON registers into PMBus virtual sensors.

Important APIs/types/functions: `struct zl6100_data` stores chip ID and PMBus info. `zl6100_l2d()`/`zl6100_d2l()` convert LINEAR11 values. Custom PMBus hooks `zl6100_read_word_data()`, `zl6100_read_byte_data()`, and `zl6100_write_word_data()` implement VMON reads/status/limits and chip quirks. Module parameter `delay` controls access delay.

Control flow: probe validates SMBus functions, reads `ZL6100_DEVICE_ID`, matches the chip, initializes base capabilities, conditionally exposes VMON and multi-page ZL8802 features, reads manufacturer config to add external temperatures, sets access delay and custom hooks, then calls `pmbus_do_probe()`.

State and persistence: PMBus info persists chip ID, page count, access delay, and hooks. VMON warning limits are derived from fault limits at 90%/110% and writes clear PMBus cache.

Dependencies/integration: I2C SMBus, PMBus core, udelay timing, module parameters.

Risks: device ID is string-prefix matched; all supported chips are assumed to need delay; ZL2005 register detection is explicitly unreliable; virtual warning/fault limits share the same hardware registers and require careful cache invalidation.

Test signals: ID detection across aliases, access-delay behavior, ZL8802 shared/independent page mode, VMON status bit mapping, warning/fault limit conversions, and external temperature capability detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/zl6100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/powerz.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/powerz.c

Purpose: USB hwmon driver for ChargerLAB POWER-Z KM002C/KM003C USB-C testers. It sends a vendor command over bulk OUT, reads a packed sensor frame over bulk IN, and exposes voltage/current/temperature channels.

Important APIs/types/functions: `struct powerz_sensor_data` describes the 64-byte response layout. `struct powerz_priv` owns a DMA-safe transfer buffer, mutex, completion, URB, and status. `powerz_read_data()` orchestrates command and data URB phases; `powerz_read()` converts fields to hwmon units.

Control flow: probe allocates state and one URB, registers hwmon. On each read, the mutex serializes access, command bytes are written to endpoint 0x01, the command completion resubmits the same URB for endpoint 0x81, and the reader waits up to 5 ms for completion.

State and persistence: no cached measurements; every sysfs read triggers USB I/O. Disconnect kills and frees the URB under the mutex and sets it NULL.

Dependencies/integration: USB core, hwmon, completions, DMA annotations, little-endian conversion helpers.

Risks: the response structure contains unknown fields and relies on exact firmware layout. A single URB is reused for both phases, so locking and disconnect ordering are critical. Timeout is short and returns `-EIO`.

Test signals: USB ID matching, bulk endpoint transfers, disconnect during read, short frame handling, labels for VBUS/VCC/DP/DM/VDD, and unit sanity for averages and temperature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/powerz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/powr1220.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/powr1220.c

Purpose: hwmon driver for Lattice POWR1014/POWR1220 programmable supply monitors. It exposes ADC input voltages and highest-seen values with labels.

Important APIs/types/functions: `struct powr1220_data` stores channel count, per-channel validity, last update, maxes, and cached ADC values. `powr1220_read_adc()` performs mux selection, attenuation choice, conversion delay, raw read, scaling, and caching. `powr1220_read*` and `powr1220_is_visible()` implement hwmon callbacks.

Control flow: probe checks SMBus byte support, sets max channels to 10 or 12 depending on chip, registers a fixed hwmon channel table. Reads validate channel visibility, update channel cache if older than one second, and return current or highest value.

State and persistence: per-channel readings are cached for one second. `adc_maxes[]` persists runtime high-water values and also influences whether attenuation is enabled for future measurements.

Dependencies/integration: I2C SMBus byte operations, hwmon info API, jiffies caching.

Risks: no mutex protects cache/max arrays, so concurrent reads can race. Highest values reset on driver reload. Attenuator selection depends on previously observed max and can initially use high range.

Test signals: channel count differences between POWR1014 and POWR1220, ADC mux writes, one-second cache behavior, highest-value updates, and input labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/powr1220.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pt5161l.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pt5161l.c

Purpose: hwmon/debugfs driver for Astera Labs PT5161L Aries PCIe retimers. It reads firmware status/version and exposes retimer temperature derived from an internal ADC code.

Important APIs/types/functions: `struct pt5161l_data` owns client, firmware version, lock, init flags, health flags, and wide-register capability. `pt5161l_read_block_data()`/`write_block_data()` implement the Aries SMBus block protocol. `pt5161l_read_wide_reg()` uses a firmware mailbox on FW >= 2.2.0. `pt5161l_fwsts_check()` validates code load and heartbeat and reads firmware version via indirect SRAM.

Control flow: probe allocates state, initializes device once, registers hwmon, and creates debugfs files. Temperature reads lazily initialize if needed, read `ARIES_CURRENT_AVG_TEMP_ADC_CSR`, validate ADC range, and convert to millidegrees. Debugfs status reads refresh firmware checks under lock.

State and persistence: initialization records firmware version, load/heartbeat health, `mm_wide_reg_access`, and `init_done`. Accesses are serialized by `lock`.

Dependencies/integration: I2C SMBus block protocol, hwmon, debugfs, ACPI/OF/I2C matching.

Risks: probe calls `pt5161l_init_dev()` but ignores its return, relying on lazy read retry. Mailbox status loops can timeout. Firmware version gating determines safe wide register access. Temperature conversion uses fixed calibration constants.

Test signals: FW load and heartbeat debugfs values, version parsing, FW < and >= 2.2 wide-register paths, invalid ADC rejection, timeout/error propagation, and ACPI/OF probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pt5161l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pwm-fan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/pwm-fan.c

Purpose: platform hwmon driver for fans controlled by a PWM line, optional regulator, tachometer IRQs, and optional thermal cooling levels.

Important APIs/types/functions: `struct pwm_fan_ctx` stores PWM state, regulator state, tachometer data, timer, cooling levels, and stop/start/shutdown policy. `set_pwm()`/`__set_pwm()` change duty cycle and power. `sample_timer()` calculates RPM from IRQ pulse counts. Thermal callbacks expose cooling states.

Control flow: probe gets PWM/regulator, sets `usage_power`, validates period math, parses `cooling-levels`, starts fan at maximum/default, sets cleanup action, configures tachometer IRQs and pulses-per-revolution, parses stop/start and shutdown properties, registers hwmon and thermal cooling device.

State and persistence: `pwm_value`, `enable_mode`, `enabled`, `regulator_enabled`, RPM values, cooling state, and PWM hardware state persist. Cleanup either sets shutdown duty or forces power off.

Dependencies/integration: PWM framework, regulator API, platform IRQs, hwmon, thermal OF cooling, timers, device properties, PM suspend/resume.

Risks: `pwm_fan_update_enable()` ignores return values from some PWM/regulator updates when disabled. Tachometer accuracy depends on correct pulses-per-revolution and one-second sampling. Stop-to-start boost timing is property-driven. Suspend powers off and resume restores stored PWM.

Test signals: PWM sysfs read/write, enable modes 0-3, regulator transitions, tachometer RPM with known pulses, cooling-level state changes, suspend/resume, shutdown percent behavior, and invalid property handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pwm-fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/qnap-mcu-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/qnap-mcu-hwmon.c

Purpose: hwmon and thermal cooling driver for fan and temperature functions exposed by QNAP MCU MFD devices.

Important APIs/types/functions: `struct qnap_mcu_hwmon` stores MCU pointer, PWM bounds from variant data, fan cooling levels, fwnode, and hwmon info. `qnap_mcu_hwmon_get_rpm()`, `get_pwm()`, `set_pwm()`, and `get_temp()` issue small MCU command/reply transactions. Thermal callbacks map cooling state to PWM.

Control flow: probe obtains parent MCU and variant limits, sets fan PWM to max, parses optional `fan-0/cooling-levels`, registers hwmon, then registers a thermal cooling device only when valid cooling levels exist. Runtime reads poll MCU; writes clamp nonzero PWM into variant min/max.

State and persistence: fan state is tracked only when thermal cooling changes it; actual PWM is read live. Fan fwnode is retained until unbind via devm action.

Dependencies/integration: QNAP MCU MFD API, hwmon, thermal OF cooling, firmware node properties, platform data.

Risks: MCU reply validation checks only command echo bytes; protocol comments leave fan id semantics uncertain. Direct hwmon PWM writes do not update `fan_state`. Probe forces max PWM, which may surprise systems expecting firmware policy.

Test signals: MCU command/ack traces, RPM scaling by 30, PWM min/max clamping, temperature bit7 masking, optional cooling-device registration, and malformed cooling-level rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/qnap-mcu-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/raspberrypi-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/raspberrypi-hwmon.c

Purpose: Raspberry Pi voltage alarm hwmon driver. It polls firmware throttling state, exposes undervoltage sticky alarm as `in0_lcrit_alarm`, logs state transitions, and notifies hwmon listeners.

Important APIs/types/functions: `struct rpi_hwmon_data` stores firmware handle, hwmon device, last throttled value, and delayed work. `rpi_firmware_get_throttled()` calls `RPI_FIRMWARE_GET_THROTTLED`, clears sticky bits via request value `0xffff`, compares undervoltage bit, logs, and emits `hwmon_notify_event()`.

Control flow: probe obtains parent firmware pointer, registers hwmon, initializes autocancel delayed work, and schedules polling every two seconds. Suspend cancels polling; resume immediately invokes the poll worker.

State and persistence: `last_throttled` stores the latest firmware status. Sticky bits are cleared as part of polling, so user-visible state is the last sampled alarm bit.

Dependencies/integration: Raspberry Pi firmware property interface, hwmon, delayed work, platform PM.

Risks: polling cadence can miss very short events except for firmware sticky behavior. Firmware errors are logged once and leave old state. Resume calls the worker directly, which also reschedules delayed work.

Test signals: undervoltage log transitions, `in0_lcrit_alarm`, hwmon uevents, suspend/resume polling, and firmware error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/raspberrypi-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sbtsi_temp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sbtsi_temp.c

Purpose: I2C hwmon driver for AMD SB-TSI temperature sensors. It exposes CPU temperature plus writable min/max limits.

Important APIs/types/functions: `struct sbtsi_data` stores client, extended-range mode, and read order. `sbtsi_reg_to_mc()` and `sbtsi_mc_to_reg()` convert integer/decimal registers to millidegrees. `sbtsi_read()` and `sbtsi_write()` implement hwmon temp callbacks.

Control flow: probe reads `SBTSI_REG_CONFIG` to detect extended range and atomic-read order, then registers hwmon. Input reads follow configured integer/decimal order; limit reads use high/low registers; writes clamp values and write integer then decimal registers.

State and persistence: range/read-order flags persist from probe. Limit writes persist in device registers. No measurement cache exists.

Dependencies/integration: I2C SMBus byte operations, hwmon, OF/I2C matching, bitfield helpers.

Risks: no locking around multi-register reads/writes. Extended range adjusts all readings by 49 C. Writes clamp to encoded 0..255.875 C after range adjustment, which limits accepted user values.

Test signals: config bit decoding, read-order behavior, input/min/max conversions at fractional 0.125 C boundaries, writable limits, and OF match `amd,sbtsi`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sbtsi_temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch5627.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sch5627.c

Purpose: hwmon driver for SMSC SCH5627 Super-I/O embedded controller. It exposes temperatures, fans, PWM temperature-channel mapping, voltage inputs, and optional watchdog registration through shared SCH56xx virtual-register helpers.

Important APIs/types/functions: `struct sch5627_data` stores address, control byte, regmap, cache fields, and lock. Update helpers cache temp/fan/in readings for one second and trigger VBAT refresh every five minutes. `sch5627_read()`, `write()`, and `read_string()` implement modern hwmon callbacks. `sch5627_regmap_config` limits writable tunables.

Control flow: probe validates hardware/company/primary IDs and control START bit, initializes regmap over SCH56xx virtual registers, triggers VBAT measurement, registers hwmon, and then registers the watchdog non-fatally. Runtime reads use cached virtual register values or regmap tunables.

State and persistence: one-second caches reduce EC traffic. Writable temp/fan/PWM tunables persist in hardware and regmap cache unless the SCH lock bit makes registers read-only. Suspend marks regcache dirty; resume syncs or drops cache if locked.

Dependencies/integration: `sch56xx-common`, regmap, hwmon, platform device from common Super-I/O scanner, PM, watchdog helper.

Risks: lock bit changes visibility to read-only and prevents resume sync. Virtual register reads can fail mid-cache update. RPM register zero is treated as I/O error. Voltage scaling is table-driven.

Test signals: ID validation, START-bit failure, cache refresh timing, writable tunable sync after resume, lock-bit read-only mode, watchdog registration, and voltage/fan/temp conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch5627.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch5636.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sch5636.c

Purpose: hwmon driver for Fujitsu Theseus/SMSC SCH5636 hardware monitor. It exposes voltage, temperature, and fan sysfs attributes using older explicit sysfs file creation.

Important APIs/types/functions: `struct sch5636_data` stores base address, hwmon device, one-second cache, and active/inactive sensor control bytes. `sch5636_update_device()` reads active sensors, caches values, and write-clears alarm bits. Numerous `*_show()` functions back sensor attributes.

Control flow: probe verifies Fujitsu ID `"THS"` and revision registers, reads all temp/fan control registers to skip deactivated channels, creates base/temp/fan sysfs files, registers hwmon, and registers watchdog non-fatally. On error or remove it removes created files and unregisters hwmon.

State and persistence: cached sensor readings persist for one second. Alarm bits are cleared during update by writing their control register value back. Active channel set is discovered once at probe.

Dependencies/integration: `sch56xx-common` virtual register access and watchdog helper, platform device from common scanner, legacy hwmon sysfs API.

Risks: manual sysfs creation/removal is more error-prone than devm hwmon info tables. Probe cleanup removes the full possible file set, including files that may not have been created. Alarm read has side effects because update clears alarm bits.

Test signals: ID/revision detection, deactivated channel omission, voltage scaling labels, fan RPM/fault/alarm behavior, temp fault/alarm behavior, and cleanup on mid-probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch5636.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.c

Purpose: shared infrastructure for SCH5627/SCH5636. It scans Super-I/O ports, creates the matching platform device, implements mailbox virtual-register access, exposes a regmap bus wrapper, and registers an optional watchdog.

Important APIs/types/functions: exported register helpers include `sch56xx_read_virtual_reg()`, `write_virtual_reg()`, `read_virtual_reg16()`, `read_virtual_reg12()`, `sch56xx_regmap_read16()`, `write16()`, `devm_regmap_init_sch56xx()`, and `sch56xx_watchdog_register()`. Internal helpers handle Super-I/O enter/select/exit and mailbox command polling.

Control flow: module init probes 0x4e then 0x2e, selects embedded controller logical device, validates enable/address, checks ACPI resource conflicts, and registers a platform device. Virtual-register commands write a request packet into mailbox registers, trigger execution, poll interrupt/source and EC-to-host completion, then read or write payload.

State and persistence: global `sch56xx_pdev` tracks the created platform device. Regmap contexts hold address and shared lock. Watchdog state caches control/output/preset registers and persists as a devm watchdog device.

Dependencies/integration: raw I/O port access, ACPI resource conflict checks, platform bus, regmap, watchdog core, mutexes.

Risks: mailbox timing is empirical and uses busy plus sleep polling. Raw I/O ordering must match vendor app notes. `devm_regmap_init_sch56xx()` checks `reg_bits != 16 && val_bits != 8`, which accepts some invalid configs if only one field differs. Watchdog cannot truly stop, only disables reset output.

Test signals: Super-I/O detection at both base ports, unsupported/disabled/no-address cases, mailbox read/write retries, regmap read/write16, watchdog start/stop/ping/timeout, and ACPI conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.h -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.h

Purpose: shared header for SCH56xx hwmon drivers. It declares virtual-register, regmap, and watchdog helper APIs implemented by `sch56xx-common.c`.

Important APIs/types/functions: declarations cover `devm_regmap_init_sch56xx()`, 16-bit regmap read/write helpers, raw virtual register read/write helpers, 16-bit and 12-bit latched reads, and `sch56xx_watchdog_register()`.

Control flow: SCH5627/SCH5636 include this header to access the common mailbox protocol and watchdog registration after the common module has created their platform devices.

State and persistence: the header defines no state, but its prototypes expose stateful operations over a shared EC mailbox that callers must serialize with their provided mutexes.

Dependencies/integration: includes Linux mutex and regmap declarations; relies on `struct device` declarations from included kernel headers.

Risks: callers must understand latch ordering for 12/16-bit reads and must pass the same lock used for hardware access. No inline documentation specifies error semantics beyond integer errno returns.

Test signals: compile coverage for SCH5627/SCH5636, symbol export/import resolution, and matching prototypes with implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/scmi-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/scmi-hwmon.c

Purpose: hwmon bridge for ARM SCMI sensor protocol. It discovers firmware-described sensors, maps supported classes to hwmon channels, scales readings into Linux hwmon units, and registers thermal zones for temperature sensors.

Important APIs/types/functions: `struct scmi_sensors` stores protocol handle and per-hwmon-type sensor arrays. `scmi_hwmon_scale()` adjusts sensor readings using SCMI scale plus class-specific milli/micro units. `scmi_hwmon_probe()` builds dynamic channel info and sensor arrays. `scmi_thermal_sensor_register()` attaches temperature sensors to thermal zones.

Control flow: probe obtains SCMI sensor ops, counts sensors, counts supported classes, allocates channel tables, fills per-type sensor arrays in stable order, registers hwmon, enables temperature sensors via `config_set()`, then tries thermal zone registration.

State and persistence: discovered sensor pointers and protocol handle persist for device lifetime. Readings are not cached. Temperature sensors are explicitly enabled after hwmon registration.

Dependencies/integration: SCMI protocol core, hwmon info API, thermal OF zones, sysfs labels from firmware sensor names.

Risks: `sensor_ops` is file-global even though probe stores protocol handles per device. Thermal enabling uses loop index `i` from hwmon temp array rather than `sensor->id`, which should be validated against SCMI expectations. Scaling rejects absolute scale over 19.

Test signals: mixed sensor-class discovery, labels, scaled units, thermal-zone attachment and ENODEV skip path, config_set failures, and unsupported sensor classes being ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/scmi-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/scpi-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/scpi-hwmon.c

Purpose: hwmon bridge for ARM SCPI sensor protocol. It dynamically creates sysfs attributes for SCPI sensors, scales readings to hwmon units, and optionally registers temperature sensors with thermal zones.

Important APIs/types/functions: `struct sensor_data` stores SCPI info, scale, generated input/label attributes, and attribute names. `scpi_scale_reading()` normalizes firmware values. `scpi_show_sensor()` and `scpi_show_label()` back generated sysfs attributes. `scpi_hwmon_probe()` builds all attributes from firmware sensor metadata.

Control flow: probe obtains SCPI ops, reads sensor capability count, allocates sensor and attribute arrays, selects scale table from OF compatible, iterates sensors, assigns hwmon names by class, initializes attributes, registers hwmon with groups, then registers thermal zones for temperature sensors.

State and persistence: sensor metadata, generated attribute names, and scaling factors persist. Sensor values are read live on every sysfs access.

Dependencies/integration: SCPI protocol ops, OF match data, hwmon group API, thermal OF zones.

Risks: unsupported sensor classes leave holes in `data[]`; later thermal-zone loop iterates `nr_sensors` rather than the populated `idx`, so uninitialized entries can be examined. Uses `sprintf` rather than `sysfs_emit`. Thermal registration errors are ignored.

Test signals: OF scale selection including Amlogic variant, generated attribute names and labels for each class, signed temperature output, unsupported class handling, and thermal-zone registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/scpi-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sfctemp.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sfctemp.c

Purpose: platform hwmon driver for StarFive JH7100/JH7110 temperature sensors. It controls clocks/resets/power state and exposes temperature plus enable control.

Important APIs/types/functions: `struct sfctemp` stores MMIO base, sense/bus clocks, sense/bus resets, and enabled state. `sfctemp_enable()` sequences clocks, resets, power-up, and run. `sfctemp_disable()` stops conversion and powers down. `sfctemp_convert()` reads DOUT and applies fixed calibration.

Control flow: probe maps registers, acquires clocks/resets, asserts resets, registers a cleanup action, enables the sensor, and registers hwmon. Runtime writes to `temp_enable` call enable/disable; reads return enabled state or converted temperature.

State and persistence: enabled state mirrors hardware sequencing. Cleanup disables sensor on device removal. No measurement cache exists.

Dependencies/integration: platform MMIO, clk, reset controls, hwmon, OF matching.

Risks: no lock protects concurrent enable/read/write. Conversion assumes fixed constants for both compatible strings. `temp_input` returns `-ENODATA` when disabled. Probe leaves sensor enabled by default.

Test signals: clock/reset error unwinds, enable/disable sysfs behavior, DOUT conversion sanity, remove cleanup, and both StarFive compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sfctemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sg2042-mcu.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sg2042-mcu.c

Purpose: I2C hwmon/debugfs/sysfs driver for Sophgo SG2042 power-control MCU. It exposes SoC/board temperatures, critical/repower thresholds, reset/uptime/policy attributes, and debug MCU metadata.

Important APIs/types/functions: `struct sg2042_mcu_data` stores client and mutex. `sg2042_mcu_read()` reads temperature registers in millidegrees. `sg2042_mcu_write()` updates critical or repower hysteresis with ordering validation under `guard(mutex)`. Device attributes expose reset count, uptime, reset reason, and repower policy. `DEFINE_MCU_DEBUG_ATTR` generates debugfs readers.

Control flow: probe checks SMBus byte/block support, allocates state, registers hwmon with extra device groups, then creates debugfs files. Runtime threshold writes read the paired threshold, enforce `crit >= hyst`, clamp to one byte, and write the target register.

State and persistence: MCU register settings persist in hardware. Driver state only serializes threshold updates.

Dependencies/integration: I2C SMBus, hwmon, debugfs, sysfs groups, mutex cleanup guard macros, OF/I2C matching.

Risks: `devm_kmalloc()` leaves padding/unset fields but current struct fields are initialized. Uptime reads two bytes and only checks negative return, not short block length. Temperature threshold units are truncated to whole degrees.

Test signals: threshold write ordering, repower policy strings, debugfs metadata reads, uptime endianness, SMBus functionality gating, and hwmon visibility for writable channel 0 thresholds only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sg2042-mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht15.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sht15.c

Purpose: bit-banged GPIO platform driver for Sensirion SHT1x temperature/humidity sensors. It implements the sensor’s custom two-wire protocol, optional CRC checking, regulator-aware temperature compensation, interrupt-driven conversion completion, and legacy hwmon sysfs attributes.

Important APIs/types/functions: `struct sht15_data` stores GPIOs, workqueue, waitqueue, cached raw values/status, CRC flags, regulator state, and read lock. Low-level protocol functions implement transmission start, bit/byte send/read, ACK/NAK, status read/write, soft reset, and connection reset. `sht15_measurement()` starts conversions and waits for IRQ/work completion.

Control flow: probe enables optional regulator and notifier, requests clock/data GPIOs and falling-edge IRQ, resets the sensor, creates sysfs group, and registers hwmon. Reads refresh status or humidity+temperature if stale, then calculate compensated values. IRQ disables itself and schedules bottom-half work to read conversion data and wake waiters.

State and persistence: measurements/status are cached for one second. `val_status` mirrors device status and persists heater/low-resolution bits. Supply voltage is cached and updated asynchronously after regulator notifications.

Dependencies/integration: GPIO descriptors, platform IRQs, regulators, workqueues, waitqueues, hwmon legacy API.

Risks: protocol timing is software bit-banged. Checksum mode exists but is never enabled in this file. Regulator notifier scheduling can leave `supply_uv_valid` unused. Remove performs soft reset and regulator cleanup but outstanding work ordering needs hardware testing.

Test signals: GPIO waveform/IRQ completion, timeout/reset path, heater sysfs writes, low battery fault, regulator voltage compensation, cache timing, and probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht21.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sht21.c

Purpose: I2C hwmon driver for Sensirion SHT20/SHT21/SHT25 humidity and temperature sensors. It exposes temperature, humidity, and electronic identification code.

Important APIs/types/functions: `struct sht21` stores client, lock, cached readings, validity, and EIC text. `sht21_update_measurements()` triggers hold-master temperature and humidity SMBus word reads, converts raw ticks, and caches results. `eic_read()` performs two raw I2C command/read transfers to assemble the serial/electronic code.

Control flow: probe checks SMBus word support, allocates state, initializes mutex, and registers hwmon with legacy attribute group. Reading temp or humidity refreshes both values at most twice per second. EIC is read once lazily and cached as text.

State and persistence: temperature/humidity cache for half a second to satisfy sensor duty-cycle guidance. EIC string persists after first successful read.

Dependencies/integration: I2C SMBus word reads plus raw I2C transfers for EIC, hwmon group API, I2C/OF matching.

Risks: no CRC validation is performed on measurement words. `i2c_transfer()` return values are only checked for negative errors, not partial message counts. EIC cache remains empty after failures and will retry.

Test signals: SMBus functionality gating, conversion formulas, half-second cache behavior, EIC read formatting, and support for all three IDs/compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht3x.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/sht3x.c

Purpose: I2C hwmon driver for Sensirion SHT3x/SHT85 humidity-temperature sensors and STS3x temperature-only sensors. It supports single-shot and periodic measurement modes, repeatability selection, heater control, alarms, writable limits, update interval, and debugfs serial number.

Important APIs/types/functions: `struct sht3x_data` stores mode, selected command, wait time, repeatability, cached readings/limits, serial number, and two mutexes. `sht3x_read_from_command()` serializes I2C command/response. `sht3x_update_client()` refreshes cached readings. `limits_update()` and `limit_write()` read/write packed temp/humidity limits with CRC. Hwmon callbacks cover chip/temp/humidity attributes.

Control flow: probe requires full I2C, clears status, initializes data and CRC table, waits for limit-read readiness, caches limits, registers hwmon, and reads serial debugfs value. Update interval writes break periodic mode if needed, start the selected periodic command, update mode, and select read command.

State and persistence: readings are cached according to selected update interval; single-shot mode refreshes on every read due zero interval. Limit arrays mirror device limit registers. Repeatability and mode persist in driver and device until changed.

Dependencies/integration: I2C master transfers, hwmon info API, debugfs, CRC8, jiffies timing.

Risks: response CRC is not checked for normal reads/status/limits, though CRC is generated for writes. `heater_enable_store()` returns raw `i2c_master_send()` byte count instead of `count` on success. `repeatability_store()` does not reselect commands or restart periodic mode immediately.

Test signals: single-shot waits by repeatability, periodic mode transitions and break command, humidity hidden for STS3x, limit write/read round trips, alarm/status bits, heater control return behavior, and serial debugfs creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/sht3x.c -->
