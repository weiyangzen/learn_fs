# Research group subset-b-003835

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/inspur-ipsps.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/inspur-ipsps.c

### Purpose
`inspur-ipsps.c` is a PMBus hwmon driver for Inspur Power System power supplies. It exposes the standard PMBus voltage, current, power, fan, temperature, and status sensors for one page, and adds vendor-specific sysfs attributes for identity strings, firmware version, hardware version, part/serial numbers, and supply operating mode.

### Important APIs, types, and functions
The file defines vendor registers `IPSPS_REG_VENDOR_ID`, `IPSPS_REG_MODEL`, `IPSPS_REG_FW_VERSION`, `IPSPS_REG_PN`, `IPSPS_REG_SN`, `IPSPS_REG_HW_VERSION`, and `IPSPS_REG_MODE`. `enum ipsps_index` and `ipsps_regs[]` map hwmon sensor attributes to those SMBus registers. `ipsps_string_show()` reads block strings and terminates at `#`; `ipsps_fw_version_show()` validates the six-byte firmware payload; `ipsps_mode_show()` renders active/standby/redundancy state; `ipsps_mode_store()` writes only active or standby values. `ipsps_info` declares the PMBus sensor surface and `ipsps_pdata` sets `PMBUS_SKIP_STATUS_CHECK`.

### Control flow
Probe stores `ipsps_pdata` in `client->dev.platform_data` and calls `pmbus_do_probe()`. The PMBus core creates the standard hwmon attributes from `ipsps_info.func[0]`; `ATTRIBUTE_GROUPS(ipsps)` adds the vendor attributes. Mode writes are string-matched through `sysfs_streq()` and translated to byte writes.

### State and persistence behavior
The driver has no allocated private data. Persistent state lives on the PSU and includes the vendor identity fields and writable mode register. The platform-data pointer is a static object. The mode sysfs attribute can persistently alter PSU behavior depending on device firmware.

### Dependencies and integration points
It depends on the PMBus core, Linux hwmon sensor-device-attribute helpers, I2C SMBus byte/block operations, optional OF matching through `inspur,ipsps1`, and the I2C id `ipsps1`.

### Risks
`ipsps_string_show()` uses `memscan()` and writes `*p = '\0'`; if no `#` appears, `p` points at `data + rc`, which is safe only because the buffer has one extra byte and `rc` is bounded by SMBus block length. Firmware parsing rejects any length other than six bytes. `PMBUS_SKIP_STATUS_CHECK` avoids probe failures on status reads but can hide broken status behavior.

### Test signals
Useful tests include successful probe with standard PMBus sensors, sysfs reads for every vendor attribute, malformed firmware block returning `-EPROTO`, unknown mode rendering `unspecified`, active/standby writes changing the mode byte, invalid mode writes returning `-EINVAL`, OF and I2C modalias binding, and behavior when status checks would otherwise fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/inspur-ipsps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir35221.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir35221.c

### Purpose
`ir35221.c` supports the Infineon/International Rectifier IR35221 dual-page PMBus controller. It validates the device identity at probe and exposes standard linear-format telemetry plus virtual min/max history sensors backed by manufacturer peak and valley registers.

### Important APIs, types, and functions
The key register definitions are `IR35221_MFR_*_PEAK` and `IR35221_MFR_*_VALLEY` for VIN, VOUT, IOUT, and temperature. `ir35221_read_word_data()` translates PMBus virtual registers such as `PMBUS_VIRT_READ_VIN_MAX`, `PMBUS_VIRT_READ_IOUT_MIN`, and `PMBUS_VIRT_READ_TEMP_MAX` into those manufacturer registers. `ir35221_probe()` performs SMBus capability checks, validates `PMBUS_MFR_ID` as `"RI"`, validates the two-byte model payload `0x6c 0x00`, allocates a `pmbus_driver_info`, and sets two pages with linear formats.

### Control flow
The I2C driver binds on id `ir35221`. Probe rejects adapters that lack byte, word, and block reads, reads and checks manufacturer identity, constructs `pmbus_driver_info` with identical functions for both pages, and delegates registration to `pmbus_do_probe()`. Later virtual history reads call back into `ir35221_read_word_data()`, while unhandled registers fall through to the PMBus core through `-ENODATA`.

### State and persistence behavior
Only a device-managed `pmbus_driver_info` is allocated. The driver does not cache telemetry or clear peak/valley state; it reports the device's own manufacturer registers. Any history persistence is implemented by the controller firmware.

### Dependencies and integration points
It integrates with the PMBus core through `read_word_data`, I2C SMBus block/word/byte reads, the I2C id table, and exported PMBus virtual register conventions.

### Risks
Probe is intentionally strict about identity payload length and content, so variants with different string encodings will not bind. There are no virtual reset handlers for the peak/valley registers, so users can observe history but cannot clear it through this driver. The author string has a missing closing angle bracket, which is cosmetic metadata only.

### Test signals
Test by probing with valid and invalid `MFR_ID`/`MFR_MODEL`, verifying two hwmon pages, reading virtual min/max attributes for VIN/VOUT/IOUT/temp, confirming unsupported virtual writes are absent, and checking adapter-functionality failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir35221.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir36021.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir36021.c

### Purpose
`ir36021.c` is a compact PMBus driver for the Infineon IR36021. It exposes one page of linear-format voltage, current, power, temperature, and temperature status sensors after verifying the model register.

### Important APIs, types, and functions
`ir36021_info` is the central `pmbus_driver_info`: one page, linear formats for voltage in/out, current in/out, power, and temperature, and `func[0]` flags for VIN, VOUT, IIN, IOUT, PIN, POUT, TEMP, TEMP2, and temperature status. `ir36021_probe()` checks SMBus read capabilities and reads two bytes from `PMBUS_MFR_MODEL` using `i2c_smbus_read_i2c_block_data()`.

### Control flow
The driver binds through I2C id `ir36021` or OF compatible `infineon,ir36021`. Probe validates that `PMBUS_MFR_MODEL` returns exactly `0x01 0x2d`; on success it calls `pmbus_do_probe()` with static `ir36021_info`. No custom read or write callbacks are installed, so all telemetry uses PMBus core defaults.

### State and persistence behavior
There is no private mutable state. All runtime readings come directly from the PMBus device. The only static state is the driver-info structure and match tables.

### Dependencies and integration points
The file depends on I2C SMBus byte, word, and block reads, the PMBus core, device-tree matching, and the Linux module I2C driver registration macro.

### Risks
The model check is strict and will reject compatible devices with different model bytes. The `func` surface includes only `PMBUS_HAVE_STATUS_TEMP`, not input/output status bits, so status sysfs coverage is limited to temperature despite voltage/current sensors being exposed.

### Test signals
Validation should include successful OF and I2C modalias binding, adapter capability rejection, model mismatch rejection, one hwmon page with the advertised linear sensors, and PMBus-core fallback behavior for unsupported attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir36021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir38064.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir38064.c

### Purpose
`ir38064.c` supports Infineon IR38060, IR38064, IR38164, and IR38263 regulators. It exposes a single PMBus page and compensates for devices that do not support `VOUT_MODE` by modeling VOUT as direct mode with coefficients equivalent to linear16 exponent -8.

### Important APIs, types, and functions
`ir38064_info` declares one PMBus page, linear VIN/IOUT/POUT/temperature formats, direct VOUT format, and direct coefficients `m=256`, `b=0`, `R=0`. `func[0]` includes VIN, VOUT, IOUT, POUT, temperature, and matching status flags. If `CONFIG_SENSORS_IR38064_REGULATOR` is enabled, `ir38064_reg_desc` exposes one regulator named `vout`.

### Control flow
Probe contains no identity reads; binding is controlled by I2C ids and OF compatibles. `ir38064_probe()` simply calls `pmbus_do_probe()` with the static info. The PMBus core handles all register accesses and optional regulator registration.

### State and persistence behavior
There is no per-device allocation or cached state. If regulator support is enabled, persistent control state is the PMBus-controlled output regulator state on the chip.

### Dependencies and integration points
The driver integrates with PMBus hwmon, optional PMBus regulator helpers, OF matching for four Infineon compatibles, and I2C id matching.

### Risks
Since probe does not validate manufacturer or model registers, a misdeclared device node can bind and expose incorrect scaling. The comment notes unsupported peak registers; history sensors are intentionally absent. VOUT scaling relies on the hard-coded direct-mode workaround.

### Test signals
Tests should cover all compatibles and ids, VOUT conversion accuracy against raw linear16 exponent -8 data, optional regulator registration, standard status reporting, and misbinding behavior in board descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ir38064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/irps5401.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/irps5401.c

### Purpose
`irps5401.c` supports the Infineon IRPS5401M PMIC. It declares five PMBus pages representing four switching regulators and one LDO, exposing common voltage, current, power, temperature, and status sensors.

### Important APIs, types, and functions
Two function masks define the sensor surfaces: `IRPS5401_SW_FUNC` for pages 0 through 3 and `IRPS5401_LDO_FUNC` for page 4. `irps5401_info` sets `.pages = 5` and assigns those masks. `irps5401_probe()` delegates directly to `pmbus_do_probe()`.

### Control flow
The I2C id `irps5401` binds the driver. No custom identity check, read callback, write callback, or format override is provided, so the PMBus core discovers/uses device-provided formats and standard PMBus registers.

### State and persistence behavior
The driver owns no mutable state. Sensor values and limits are read from and written to the hardware through PMBus core logic when exposed.

### Dependencies and integration points
It depends entirely on the PMBus core and I2C driver framework. There is no OF table in this file, so device-tree systems need ordinary I2C modalias support or another matching path.

### Risks
The declared page map is fixed and unverified at probe, so board configuration must ensure the target really is an IRPS5401-compatible device. Peak telemetry mentioned in comments is not implemented. Format behavior is left to the PMBus core and device registers.

### Test signals
Validation should check five pages, correct switcher versus LDO attribute sets, standard status attributes, absence of unsupported peak history attributes, and successful module bind/unbind through the I2C id table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/irps5401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/isl68137.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/isl68137.c

### Purpose
`isl68137.c` supports Renesas/ISL digital multiphase voltage regulators across many ISL68xxx, ISL69xxx, and RAA22xxxx variants. It exposes variant-specific page counts, direct or linear formats, optional AVSBus enable sysfs controls, VMON support, and device-tree voltage-divider compensation.

### Important APIs, types, and functions
`enum variants` selects the supported topology. `struct isl68137_data` embeds `pmbus_driver_info` and per-channel `vout_voltage_divider` arrays. `isl68137_avs_enable_show_page()` and `isl68137_avs_enable_store_page()` expose AVS control on selected devices; the store path locks the PMBus bus, rewrites `VOUT_COMMAND` before enabling AVS, and updates `PMBUS_OPERATION`. `raa_dmpvr2_read_word_data()` remaps `PMBUS_VIRT_READ_VMON` and scales `READ_VOUT`/`READ_POUT` through the voltage divider. `raa_dmpvr2_write_word_data()` inversely scales VOUT-related commands. DT parsing is handled by `isl68137_probe_child_from_dt()` and `isl68137_probe_from_dt()`.

### Control flow
Probe allocates `isl68137_data`, initializes all dividers to 1:1, copies `raa_dmpvr_info`, then switches on `i2c_get_match_data()` to select pages, formats, function masks, callbacks, AVS groups, and HV coefficients. It parses child nodes named `channel`, validates `reg` against page count, reads optional `vout-voltage-divider`, and calls `pmbus_do_probe()`.

### State and persistence behavior
Per-device state persists in devm memory and includes copied driver info plus voltage-divider ratios. The AVS enable sysfs attribute writes `PMBUS_OPERATION` and can switch device control mode. The VOUT rewrite before AVS enable is a persistence workaround for firmware retaining AVSBus setpoints.

### Dependencies and integration points
The driver depends on PMBus locking/read/write helpers, hwmon sysfs attribute groups, OF child-node parsing, I2C and OF match data, and PMBus direct/linear conversion coefficients.

### Risks
Voltage-divider math affects both telemetry and command writes; invalid divider values are rejected, but missing properties default to 1:1. `raa_dmpvr2_write_word_data()` returns a scaled value rather than directly writing a register, matching PMBus callback expectations only if the core performs the final write. AVS mode changes can alter regulator control semantics. Variant matching is large and easy to drift between I2C and OF tables.

### Test signals
Tests should cover each variant group, DT divider parsing and rejection, VOUT/POUT scaling and inverse write scaling, AVS enable/disable behavior, VMON exposure only on supported pages, PMBus format selection for the PMBus-native variant, and consistency between OF and I2C match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/isl68137.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lm25066.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lm25066.c

### Purpose
`lm25066.c` supports TI LM25056, LM25066, LM5064, LM5066, and LM5066I hot-swap/power monitor devices. It maps manufacturer telemetry and limits into PMBus virtual sensors, applies chip-specific direct-mode coefficients, scales current and power by shunt-resistor value, and optionally exposes a regulator for devices supporting `OPERATION`.

### Important APIs, types, and functions
`enum chips` selects coefficient rows in `lm25066_coeff`. `struct lm25066_data` stores chip id, maximum register value, and driver info. `lm25066_read_word_data()` handles VAUX/VMON, manufacturer input current/power, averages, peak PIN, samples, and reset pseudo-registers. `lm25056_read_word_data()` adds LM25056 VAUX warn limits; `lm25056_read_byte_data()` translates manufacturer VAUX status into PMBus voltage bits. `lm25066_write_word_data()` clamps writable limits, maps virtual limits to manufacturer registers, clears PIN peak, and writes averaging sample count as `ilog2()`.

### Control flow
Probe checks byte-data support, allocates private data, reads `LM25066_DEVICE_SETUP` to select high/low current-limit coefficients, determines chip id from match data, fills one-page direct-format `pmbus_driver_info`, selects LM25056-specific callbacks when needed, copies coefficients, applies `shunt-resistor-micro-ohms` from DT or a 1 milliohm default, optionally configures regulator descriptors, and calls `pmbus_do_probe()`.

### State and persistence behavior
Per-device state is devm-managed. Device-side averaging samples, warning limits, and peak history are persistent until changed or cleared. `data->rlimit` constrains writes to device register width. Shunt scaling is fixed at probe from firmware description.

### Dependencies and integration points
It depends on PMBus virtual attributes, direct-mode coefficient conversion, I2C SMBus byte/word operations, OF properties, and optional PMBus regulator support through `CONFIG_SENSORS_LM25066_REGULATOR`.

### Risks
Conversion correctness depends on chip id, device setup bit `LM25066_DEV_SETUP_CL`, and shunt value. The sample count is coerced to a power-of-two exponent, so arbitrary user writes are quantized. LM25056 has no VOUT and no regulator support. Bad DT shunt values can make current/power scaling inaccurate.

### Test signals
Validate each chip id, current-limit coefficient branch, default and DT shunt scaling, VAUX/VMON conversions, virtual average/peak/sample attributes, clamped limit writes, LM25056 status translation, regulator registration excluding LM25056, and partial probe failure on failed `DEVICE_SETUP` reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lm25066.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lt3074.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lt3074.c

### Purpose
`lt3074.c` supports the Analog Devices LT3074 PMBus regulator. It exposes standard VIN, VOUT, IOUT, temperature, status sensors, virtual VBIAS monitoring through VMON, and optional regulator integration.

### Important APIs, types, and functions
Manufacturer registers include `LT3074_MFR_READ_VBIAS`, `LT3074_MFR_BIAS_OV_WARN_LIMIT`, `LT3074_MFR_BIAS_UV_WARN_LIMIT`, and `LT3074_MFR_SPECIAL_ID`. `lt3074_read_word_data()` maps virtual VMON read and VMON warn limits to the bias registers. `lt3074_write_word_data()` writes the bias warn limits. `lt3074_info` installs those callbacks, sets one page with linear formats, and conditionally attaches `lt3074_reg_desc`.

### Control flow
Probe checks SMBus word-read support, reads `LT3074_MFR_SPECIAL_ID`, requires value `0x1c1d`, and calls `pmbus_do_probe()`. All non-bias telemetry is handled by the PMBus core.

### State and persistence behavior
There is no driver-private mutable state. Bias warning limit writes persist on the hardware according to device behavior. Optional regulator state is managed by PMBus regulator helpers.

### Dependencies and integration points
It integrates with PMBus hwmon and optional regulator support, I2C/OF matching through `adi,lt3074`, and SMBus word operations.

### Risks
The special-ID check is strict; unrevised compatible silicon with a different ID would fail probe. The driver does not expose bias status bits separately, only VMON and limits. Optional regulator behavior depends on PMBus core support for the `regulator` descriptor.

### Test signals
Test valid and invalid special ID, VMON value and limit reads/writes, one-page sensor exposure, optional regulator registration, OF/I2C binding, and word-read capability failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lt3074.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lt7182s.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lt7182s.c

### Purpose
`lt7182s.c` supports the Analog Devices LT7182S dual-output controller. It exposes two standard PMBus pages, optional third VMON-only debug telemetry page, peak-history virtual sensors, and runtime format selection between linear and IEEE754 based on configuration.

### Important APIs, types, and functions
Important manufacturer registers include `MFR_READ_EXTVCC`, `MFR_READ_ITH`, `MFR_CONFIG_ALL_LT7182S`, `MFR_ADC_CONTROL_LT7182S`, `MFR_IOUT_PEAK`, `MFR_VOUT_PEAK`, `MFR_VIN_PEAK`, `MFR_TEMPERATURE_1_PEAK`, and `MFR_CLEAR_PEAKS`. `lt7182s_read_word_data()` maps VMON and peak virtual reads and supports reset pseudo-read for VIN history on page 0. `lt7182s_write_word_data()` clears peaks through `MFR_CLEAR_PEAKS`. Probe validates `MFR_ID` as `ADI`, model as `LT7182S`, duplicates `lt7182s_info`, and mutates formats/page count.

### Control flow
After identity validation, probe reads `MFR_CONFIG_ALL_LT7182S`; if `MFR_CONFIG_IEEE` is set it changes all sensor formats to IEEE754. It reads `MFR_ADC_CONTROL_LT7182S`; if debug telemetry is enabled, it expands pages to three and marks VMON on pages 0, 1, and a VMON-only page 2 before calling `pmbus_do_probe()`.

### State and persistence behavior
The copied driver-info object is devm-managed and reflects hardware configuration captured at probe. Peak history lives on the device and is cleared with `MFR_CLEAR_PEAKS`. Debug telemetry exposure is fixed until re-probe.

### Dependencies and integration points
It depends on PMBus virtual history attributes, SMBus byte/word/block reads, OF compatible `adi,lt7182s`, and PMBus support for IEEE754 sensor formats.

### Risks
Identity mismatch paths write a temporary NUL at `buf[ret]`; the buffer has one extra byte, but negative reads are handled first. The peak clear command clears multiple histories together. Page 2 exists only when the ADC debug bit is set, so userspace must tolerate topology changes across devices.

### Test signals
Test manufacturer/model mismatch, linear versus IEEE754 format selection, debug telemetry page creation, VMON routing for pages 0/1/2, peak read attributes, peak reset write behavior, and adapter capability rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/lt7182s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc2978.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc2978.c

### Purpose
`ltc2978.c` is a broad Analog Devices/Linear Technology PMBus driver for LTC297x managers, LTC388x controllers, LT717x, LTC7132/LTC7841/LTC7880, and LTM power modules. It detects exact chip families, selects page counts and function masks, provides virtual min/max history with software caching, handles busy polling for selected chips, and optionally registers PMBus regulators.

### Important APIs, types, and functions
`enum chips` enumerates managers, controllers, and modules. `struct ltc2978_data` stores chip id, cached min/max values for VIN/VOUT/IOUT/IIN/PIN/temp/temp2, feature bits, and driver info. `ltc_wait_ready()` polls `LTC2978_MFR_COMMON` for `LTC_NOT_BUSY` and usually `LTC_NOT_PENDING`. Wrapper functions `ltc_read_word_data()`, `ltc_read_byte_data()`, `ltc_write_byte_data()`, and `ltc_write_byte()` gate accesses on readiness. Family callbacks `ltc2978_read_word_data()`, `ltc2974_read_word_data()`, `ltc2975_read_word_data()`, `ltc3880_read_word_data()`, and `ltc3883_read_word_data()` implement virtual history. `ltc2978_write_word_data()` resets software caches and clears device peaks.

### Control flow
Probe checks word-read support, allocates `ltc2978_data`, detects chip id through `LTC2978_MFR_SPECIAL_ID` or fallback `MFR_ID`/`MFR_MODEL`, warns if configured id mismatches detected id, initializes sentinel cache values, selects callback/page/function matrix in a large switch, conditionally installs regulator descriptors, and calls `pmbus_do_probe()`.

### State and persistence behavior
This driver has meaningful per-device runtime state: cached history values survive ordinary PMBus `CLEAR_FAULTS` updates and reset only through explicit virtual reset writes. Devices with `FEAT_CLEAR_PEAKS` use `LTC3880_MFR_CLEAR_PEAKS`; others clear via `PMBUS_CLEAR_FAULTS`. Polling features control access timing and do not persist beyond the driver instance.

### Dependencies and integration points
It integrates with PMBus core callbacks, regulator descriptors under `CONFIG_SENSORS_LTC2978_REGULATOR`, I2C SMBus word/block operations, OF compatibles for every family, and PMBus virtual history conventions.

### Risks
The chip matrix is large, so id constants, page counts, and function masks can drift. Busy polling handles PEC/NACK as transient; timeout behavior is critical for slow devices. Software history caches use linear11 comparisons for most values and direct comparisons for VOUT; wrong sentinel or conversion handling corrupts min/max reporting. Some fallback model matching accepts prefix names, so ambiguous strings require care.

### Test signals
Tests should include id detection by special ID and fallback strings, mismatch warnings, every switch family page/function set, polling timeout and transient NACK/PEC handling, history cache update/reset behavior, `CLEAR_PEAKS` versus `CLEAR_FAULTS` paths, regulator descriptor selection and bounds warnings, and OF/I2C match coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc2978.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc3815.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc3815.c

### Purpose
`ltc3815.c` supports the Linear/Analog LTC3815 PMBus controller. It overrides VOUT mode, emulates unsupported clear-fault behavior, exposes manufacturer peak registers as virtual history sensors, and uses direct-mode coefficients for all supported sensor classes.

### Important APIs, types, and functions
Manufacturer registers include `LTC3815_MFR_IOUT_PEAK`, `LTC3815_MFR_VOUT_PEAK`, `LTC3815_MFR_VIN_PEAK`, `LTC3815_MFR_TEMP_PEAK`, `LTC3815_MFR_IIN_PEAK`, and `LTC3815_MFR_SPECIAL_ID`. `ltc3815_read_byte_data()` returns direct VOUT mode for `PMBUS_VOUT_MODE`. `ltc3815_write_byte()` emulates `PMBUS_CLEAR_FAULTS` by reading and writing `PMBUS_STATUS_WORD`. `ltc3815_read_word_data()` maps peak virtual reads and reset pseudo-reads. `ltc3815_write_word_data()` clears individual peak registers.

### Control flow
Probe checks word-read support, validates the masked special ID against `0x8000`, and calls `pmbus_do_probe()` with static `ltc3815_info`. The PMBus core routes VOUT mode, clear faults, and virtual history calls to this driver's callbacks.

### State and persistence behavior
The driver has no private cache. Peak registers are device-resident and can be reset through virtual history writes. The clear-fault emulation persists by writing the current status bits back to the status register.

### Dependencies and integration points
It depends on PMBus virtual history APIs, direct-mode PMBus conversion coefficients, I2C SMBus word reads/writes, and the I2C id table.

### Risks
Clear-fault emulation assumes writing `STATUS_WORD` with current bits clears them. VOUT mode is forcibly represented as direct despite the device returning manufacturer-specific VID. Peak reset writes use fixed zero or register-specific values, so hardware semantics must match.

### Test signals
Validate special ID masking, direct VOUT mode exposure, coefficient conversion for VIN/VOUT/current/temp, peak history reads and resets, `CLEAR_FAULTS` emulation, and unsupported-register fallback to PMBus core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc3815.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc4286.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc4286.c

### Purpose
`ltc4286.c` supports LTC4286 and LTC4287 hot-swap/power monitor devices. It validates manufacturer/model strings, configures voltage range from firmware properties, scales current and power coefficients by shunt resistor value, and registers one direct-format PMBus page.

### Important APIs, types, and functions
The file defines `LTC4286_MFR_CONFIG1` and `VRANGE_SELECT_BIT`. `ltc4286_info` contains default direct coefficients for VIN, VOUT, IOUT, PIN, and temperature. `ltc4286_probe()` validates `PMBUS_MFR_ID == "LTC"`, matches `PMBUS_MFR_MODEL` against `ltc4286_id`, reads `shunt-resistor-micro-ohms`, clones driver info, reads and optionally writes `LTC4286_MFR_CONFIG1`, adjusts voltage/power coefficients for `adi,vrange-low-enable`, sets current `m` from `rsense`, and calls `pmbus_do_probe()`.

### Control flow
Probe is the only custom path. It rejects unsupported manufacturer/model strings, zero or overflow-prone shunt values, and failed config reads/writes. If the desired voltage range differs from the current MFR config, it writes the new value before PMBus registration.

### State and persistence behavior
Per-device `pmbus_driver_info` is devm-copied. The shunt resistor and voltage range are fixed for the driver instance; the voltage range bit is written to the device and may persist depending on chip configuration. Sensor readings are otherwise stateless.

### Dependencies and integration points
It depends on PMBus direct-mode conversion, I2C SMBus block/word operations, OF/device properties `shunt-resistor-micro-ohms` and `adi,vrange-low-enable`, and OF compatibles `lltc,ltc4286`/`lltc,ltc4287`.

### Risks
Changing `VRANGE_SELECT` at probe alters hardware configuration. Incorrect shunt property values directly corrupt current and power scaling; overflow protection rejects very large values. Model matching uses case-insensitive prefix comparison against the model block.

### Test signals
Test manufacturer/model validation, default 300 micro-ohm shunt, zero and oversized shunt rejection, low/high voltage-range coefficient changes and config writes, current/power scaling, and both LTC4286/LTC4287 match paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/ltc4286.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max15301.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max15301.c

### Purpose
`max15301.c` supports Maxim MAX15301/MAX15303 and Flex BMR461 PMBus modules. It exposes a one-page PMBus sensor set and applies an access delay workaround to avoid random limit-register autodetection failures.

### Important APIs, types, and functions
`max15301_id` lists `bmr461`, `max15301`, and `max15303`. `struct max15301_data` embeds `pmbus_driver_info`, although the file uses a static instance. The module parameter `delay` defaults to `MAX15301_WAIT_TIME` 100 microseconds. `max15301_probe()` checks SMBus byte/block support, reads `PMBUS_IC_DEVICE_ID`, matches it case-insensitively against known ids, assigns `info->access_delay`, and calls `pmbus_do_probe()`.

### Control flow
The driver binds by I2C id. Probe validates the device-id block before registering with PMBus. After registration, the PMBus core spaces accesses according to `access_delay`.

### State and persistence behavior
The main mutable state is static `max15301_data.info.access_delay`, set from the module parameter at each probe. There is no per-device allocation, so multiple devices share the same driver-info object and delay value.

### Dependencies and integration points
It depends on PMBus core access-delay support, I2C SMBus block reads, the Linux module-parameter API, and the I2C id table.

### Risks
The static driver-info object means all bound devices share callback/configuration state; this is acceptable because the only changed value is global delay, but it is a pattern to avoid if per-device data is added. Probe identity depends on `PMBUS_IC_DEVICE_ID` string prefixes. Reducing `delay` can reintroduce empirically observed detection flakiness.

### Test signals
Validate identity matching for all three names, unsupported id rejection, default and overridden delay behavior, PMBus sensor exposure, and repeated multi-device probes with consistent shared delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max15301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max16064.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max16064.c

### Purpose
`max16064.c` supports the Maxim MAX16064 four-page PMBus monitor. It exposes VOUT and temperature monitoring with direct-mode coefficients and maps manufacturer peak registers into virtual history attributes.

### Important APIs, types, and functions
The driver defines `MAX16064_MFR_VOUT_PEAK` and `MAX16064_MFR_TEMPERATURE_PEAK`. `max16064_read_word_data()` handles virtual VOUT and temperature max reads plus reset pseudo-reads. `max16064_write_word_data()` clears VOUT peak to zero and temperature peak to `0xffff`. `max16064_info` declares four pages, direct VIN/VOUT/temp coefficients, page 0 VOUT/temp status, and pages 1-3 VOUT status only.

### Control flow
Probe simply calls `pmbus_do_probe()` with static info. The PMBus core uses the read/write callbacks only for virtual history paths and otherwise performs standard direct-format PMBus transactions.

### State and persistence behavior
No private state exists. Peak history is stored on the device and reset by writing the manufacturer registers. Limit and sensor values persist according to device hardware.

### Dependencies and integration points
It depends on the PMBus core, I2C id matching for `max16064`, and SMBus word transactions through PMBus helpers.

### Risks
There is no identity validation beyond binding. Reset values are register-specific and assume Maxim semantics. The info exposes VIN format coefficients even though the function mask does not advertise VIN sensors.

### Test signals
Test four-page enumeration, page-specific sensor visibility, virtual VOUT/temp max reads, history reset writes, direct coefficient conversion, and fallback behavior for unsupported pages/registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max16064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max16601.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max16601.c

### Purpose
`max16601.c` supports Maxim MAX16508/MAX16600/MAX16601/MAX16602 multiphase VR controllers. It presents VCORE, alternate VCORE input-sensor telemetry, and VSA rail telemetry as three PMBus pages, creates a dummy I2C client for the adjacent VSA address, and exposes per-phase VCORE current/temperature data.

### Important APIs, types, and functions
`struct max16601_data` stores chip id, copied driver info, the dummy `vsa` client, and cached VSA IOUT peak. `max16601_read_word()` routes page 0 phase reads through `REG_PHASE_ID` and `REG_PHASE_REPORTING`, page 1 through `REG_IIN_SENSOR`/`REG_TOTAL_INPUT_POWER`, and page 2 through the dummy VSA client. `max16601_write_byte()` and `max16601_write_word()` forward clear-fault and limit writes to VSA where applicable. `max16601_identify()` selects VR12/VR13 VID mode and detects populated phase count. `max16601_get_id()` parses `PMBUS_IC_DEVICE_ID`.

### Control flow
Probe checks SMBus support, detects chip id, warns on configured/detected mismatch, requires the bound address to be the CORE rail via `REG_PHASE_ID`, allocates data, creates `client->addr + 1` as a dummy VSA client with devm cleanup, copies `max16601_info`, and calls `pmbus_do_probe()`.

### State and persistence behavior
Driver state includes the VSA client reference, per-device copied info, dynamic phase count, VID version, and cached VSA IOUT peak initialized/reset to a low sentinel. Device-side limits and faults persist. Dummy client lifetime is tied to the main device through `devm_add_action_or_reset()`.

### Dependencies and integration points
It uses PMBus virtual pages and phases, PMBus VID format handling, I2C dummy-device APIs, SMBus byte/block/word operations, and the I2C id table.

### Risks
Binding on the VSA address instead of the CORE address is rejected, but board descriptions must still choose the right address. Page and phase routing is complex and returns a mix of `-ENODATA` and `-EOPNOTSUPP`; regressions can expose invalid sysfs attributes. The dummy client assumes the adjacent address is reserved for VSA. Phase report block length must be at least six bytes.

### Test signals
Validate id parsing for all supported strings, CORE-address rejection, dummy-client cleanup, VR12/VR13 selection, default and detected phase counts, per-phase VCORE telemetry, page 1 input-sensor telemetry, VSA page reads/writes, IOUT history reset, and mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max16601.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max17616.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max17616.c

### Purpose
`max17616.c` supports Analog Devices MAX17616/MAX17616A PMBus regulators. It exposes a one-page direct-format PMBus sensor set for VIN, VOUT, IOUT, temperature, and associated status flags.

### Important APIs, types, and functions
The only substantial object is `max17616_info`, a `pmbus_driver_info` with direct coefficients for voltage input/output, output current, and temperature. `max17616_probe()` calls `pmbus_do_probe()`. Match tables include I2C id `max17616` and OF compatible `adi,max17616`.

### Control flow
Probe performs no custom identity validation or adapter capability check. PMBus core registration drives all subsequent sensor and status accesses.

### State and persistence behavior
There is no mutable private state. All persistent behavior is in the device registers accessed by the PMBus core.

### Dependencies and integration points
It depends on the PMBus core, I2C and OF matching, and direct-mode PMBus conversion.

### Risks
No manufacturer/model validation means correctness depends on accurate platform binding. Direct coefficients are hard-coded and must match both MAX17616 and MAX17616A. The driver exposes no limit write customizations or regulator descriptor.

### Test signals
Test OF and I2C matching, one-page hwmon attribute creation, direct conversion values for each sensor class, standard PMBus status reads, and behavior on misdeclared devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max17616.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max20730.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max20730.c

### Purpose
`max20730.c` supports Maxim MAX20710, MAX20730, MAX20734, and MAX20743 integrated regulators. It validates the chip series, applies variant-specific direct coefficients, exposes selected fault limits backed by manufacturer configuration bits, supports optional VOUT divider scaling, and creates debugfs files describing nonstandard configuration fields.

### Important APIs, types, and functions
`struct max20730_data` stores chip id, copied driver info, a write mutex, cached `MFR_DEVSET1/2`, cached `MFR_VOUT_MIN`, and optional `vout_voltage_divider`. Debugfs support uses `struct max20730_debugfs_data`, `max20730_debugfs_read()`, and `max20730_init_debugfs()`. `val_to_direct()` and `direct_to_val()` convert between milli-unit values and PMBus direct register format. `max20730_read_word_data()` synthesizes `OT_FAULT_LIMIT`, `IOUT_OC_FAULT_LIMIT`, and scaled `READ_VOUT`. `max20730_write_word_data()` updates `MFR_DEVSET1` under a mutex and clears PMBus cache.

### Control flow
Probe checks SMBus byte/word/block capabilities, validates `MFR_ID == "MAXIM"`, `MFR_MODEL == "M20743"`, and revision `"F"`, obtains match-data chip id, allocates data, copies the variant's `max20730_info`, reads optional `vout-voltage-divider`, validates total resistance, reads `MFR_DEVSET1`, registers with PMBus, and then initializes debugfs if available.

### State and persistence behavior
Per-device cached manufacturer config fields are used both for debugfs and virtual limit synthesis. Writes to fault limits modify `MFR_DEVSET1` on hardware and update the cache. VOUT divider scaling is fixed at probe. Debugfs files are informational and backed by cached plus live SMBus reads.

### Dependencies and integration points
The driver integrates with PMBus direct and linear formats, debugfs through `pmbus_get_debugfs_dir()`, OF properties, I2C/OF match data, Linux mutexes, SMBus operations, and PMBus cache invalidation.

### Risks
The series is not uniquely identifiable by model, so match data determines exact variant after broad validation. Debugfs `len` is overwritten with `strlen(result)` even after `scnprintf()` into `tbuf`; this works because `result` points at `tbuf` or literals, but changes need care. Limit writes quantize to the closest supported hardware enum. Divider validation allows a zero pair to mean no scaling.

### Test signals
Validate identity mismatch paths, every variant's coefficient table, OT and IOUT limit synthesis and writes, PMBus cache clear after `MFR_DEVSET1` updates, VOUT divider scaling and invalid divider rejection, debugfs file contents, and operation with `CONFIG_DEBUG_FS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max20730.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max20751.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max20751.c

### Purpose
`max20751.c` is a minimal PMBus driver for the Maxim MAX20751. It exposes one VR12 VID-format output rail with VIN, VOUT, IOUT, POUT, temperature, and related status sensors.

### Important APIs, types, and functions
`max20751_info` sets `.pages = 1`, linear VIN/current/power/temperature, VID VOUT with `vrm_version[0] = vr12`, and `func[0]` for VIN, VOUT/status, IOUT/status, TEMP/status, and POUT. `max20751_probe()` delegates to `pmbus_do_probe()`.

### Control flow
The I2C id `max20751` binds the driver. There are no custom callbacks or identity checks; the PMBus core handles all operations with the declared formats and functions.

### State and persistence behavior
No private state exists. Any PMBus limits or operational changes are handled directly by the PMBus core and device.

### Dependencies and integration points
It depends on PMBus VID conversion, PMBus hwmon core, and the I2C driver framework.

### Risks
No model validation protects against incorrect binding. VOUT is fixed to VR12 VID, so a different VID mode would be reported incorrectly. There is no OF match table.

### Test signals
Test one-page sensor creation, VR12 VOUT conversion, I2C modalias binding, standard status reads, and absence of unsupported virtual history attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max20751.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max31785.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max31785.c

### Purpose
`max31785.c` supports Maxim MAX31785/MAX31785A/MAX31785B fan controllers. It exposes six fan/PWM pages, temperature pages, voltage pages, and virtual secondary tachometer pages for dual-tach variants, while working around device communication timing issues.

### Important APIs, types, and functions
`struct max31785_data` stores last access time and copied driver info. `max31785_wait()` plus raw SMBus wrappers space pre-probe accesses. `max31785_read_long_data()` performs a raw I2C four-byte read after setting PMBus page and updating PMBus timing state. `max31785_get_pwm()`, `max31785_get_pwm_mode()`, `max31785_pwm_enable()`, and `max31785_scale_pwm()` implement hwmon PWM attributes. `max31785_configure_dual_tach()` scans fan pages for `MFR_FAN_CONFIG_DUAL_TACH` and creates virtual fan pages above page 22.

### Control flow
Probe checks SMBus byte/word support, allocates data, copies `max31785_info`, sets page `0xff`, reads `MFR_REVISION`, determines whether dual tach is supported, configures virtual tach pages if needed, waits once more, and calls `pmbus_do_probe()`. Runtime reads redirect virtual fan pages to raw long reads on the physical fan pages.

### State and persistence behavior
Per-device state includes copied page/function masks and last raw-access timestamp. PWM enable and PWM value writes change fan command/config registers on the device. Dual-tach virtual page count is fixed at probe after reading fan configuration.

### Dependencies and integration points
It depends on PMBus fan helpers, raw I2C transfers, PMBus timing helpers `pmbus_wait()` and `pmbus_update_ts()`, I2C/OF match tables, and hwmon PWM virtual registers.

### Risks
Timing is central: raw pre-probe accesses and PMBus-mediated accesses must remain spaced to avoid NACKs. Virtual pages above the normal page count must not expose writable fan target attributes incorrectly. PWM mode semantics map hwmon values 0/1/2/3 onto full off, manual PWM, RPM, and automatic behavior.

### Test signals
Validate revision detection for MAX31785/A/B, warning when A/B is configured but base revision is found, dual-tach virtual page creation, raw four-byte tach reads, PWM read/write/enable modes, access-delay behavior under repeated transactions, and cleanup on failed dual-tach scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max31785.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max34440.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max34440.c

### Purpose
`max34440.c` supports a family of Maxim and ADPM power monitors/controllers: ADPM12160, ADPM12200, MAX34440, MAX34441, MAX34446, MAX34451, MAX34460, and MAX34461. It supplies variant-specific page maps, direct coefficients, manufacturer history registers, status-bit translations, page-change delay, and dynamic channel discovery for MAX34451.

### Important APIs, types, and functions
`struct max34440_data` stores variant id, copied driver info, and the effective IOUT OC warning/fault limit register addresses. `max34440_read_word_data()` maps swapped IOUT limit registers and virtual min/max/average history registers. `max34440_write_word_data()` writes swapped limits and clears history registers. `max34440_read_byte_data()` translates manufacturer OC/OT status bits into PMBus status bytes. `max34451_set_supported_funcs()` reads `MFR_REVISION`, handles the MAX34451ETNA6 register-fix variant, scans 16 channel configs, and assigns function masks.

### Control flow
Probe allocates data, copies the variant table entry from `max34440_info`, initializes swapped IOUT limit addresses, runs MAX34451 dynamic discovery if needed, fixes ADPM limit addresses to standard PMBus registers, and calls `pmbus_do_probe()`. PMBus page changes are delayed by 50 microseconds for affected devices.

### State and persistence behavior
Per-device copied info captures dynamic MAX34451 function masks and revision-specific limit register mapping. History reset writes persist on hardware. Page configuration is read at probe and not refreshed later.

### Dependencies and integration points
It integrates with PMBus virtual history attributes, direct-mode conversion, I2C match data, SMBus page/register operations, and PMBus status flag conventions.

### Risks
The family has variant-specific page layouts; a wrong match id exposes wrong attributes. The MAX34440 family historically swaps IOUT warn/fault limit addresses, except ADPM devices and newer MAX34451 revisions. Dynamic MAX34451 scanning requires manual page writes and delay. Status translation reads `PMBUS_STATUS_MFR_SPECIFIC` after setting page.

### Test signals
Validate every variant table's page/function surface, swapped versus standard IOUT limit register behavior, virtual history reads/resets, MAX34451 channel-config discovery and ETNA6 revision branch, manufacturer OC/OT status translation, page-change delay, and ADPM-specific average current support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max34440.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max8688.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max8688.c

### Purpose
`max8688.c` supports the Maxim MAX8688 one-page PMBus controller. It exposes VOUT, IOUT, temperature, and status sensors, with direct-mode coefficients and manufacturer peak/status register translations.

### Important APIs, types, and functions
Manufacturer registers are `MAX8688_MFR_VOUT_PEAK`, `MAX8688_MFR_IOUT_PEAK`, `MAX8688_MFR_TEMPERATURE_PEAK`, and `MAX8688_MFG_STATUS`. `max8688_read_word_data()` maps virtual peak reads and reset pseudo-reads. `max8688_write_word_data()` clears peak registers. `max8688_read_byte_data()` maps manufacturer voltage, current, and temperature status bits into PMBus status flags. `max8688_info` defines direct coefficients and callback hooks.

### Control flow
Probe calls `pmbus_do_probe()` with static info. Runtime callbacks reject pages above zero with `-ENXIO`, translate supported virtual/status attributes, and return `-ENODATA` for PMBus core fallback where appropriate.

### State and persistence behavior
There is no private state. Peak history and status bits live on the device and are cleared or updated by hardware. History reset writes alter manufacturer registers.

### Dependencies and integration points
The driver depends on PMBus virtual history/status conventions, direct-mode conversion, I2C id matching, and SMBus word operations.

### Risks
No explicit identity validation is performed. Manufacturer status mapping must remain aligned with PMBus status bits. Reset values are hard-coded and assume device-specific peak register semantics.

### Test signals
Validate page-zero-only behavior, VOUT/IOUT/temp direct conversions, virtual peak reads and resets, manufacturer status translation for UV/OV/OC/UC/OT flags, and unsupported-register fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/max8688.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2856.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2856.c

### Purpose
`mp2856.c` supports MPS MP2856 and MP2857 multiphase VR controllers. It exposes one or two rails, detects active rail/phase counts, converts nonstandard VOUT and phase-current telemetry, and forces VOUT to direct format for PMBus core reporting.

### Important APIs, types, and functions
`struct mp2856_data` stores copied driver info, per-page VOUT format, current-sense gain, and max phase counts. `val2linear11()` converts milli-unit phase current into PMBus linear11. `mp2856_read_vout()` converts raw VOUT from either VID-style or linear scaling to direct units. `mp2856_read_phase()` and `mp2856_read_phases()` extract packed two-phase current readings from manufacturer registers. `mp2856_identify_multiphase_*()`, `mp2856_current_sense_gain_get()`, `mp2856_identify_vout_format()`, and `mp2856_is_rail2_active()` populate runtime topology.

### Control flow
Probe allocates data, selects MP2856/MP2857 max phase limits, copies base info, detects rail 1 phases, optionally detects rail 2 and reduces pages to one if inactive, reads current-sense gain and VOUT format for each page, restores PMBus page 0, and calls `pmbus_do_probe()`. Runtime reads override `PMBUS_READ_VOUT` and per-phase `PMBUS_READ_IOUT`.

### State and persistence behavior
Per-device state is fixed at probe: active page count, phase counts, VOUT format flags, and current-sense gain. No hardware configuration is intentionally changed other than PMBus page selection during discovery.

### Dependencies and integration points
It depends on PMBus phase-virtual support, I2C/OF match data, manufacturer page/register reads, PMBus direct and linear11 conversions, and the I2C id table.

### Risks
The rail 2 phase function loop appears to iterate `data->info.phases[0]` instead of `phases[1]`, which may mark the wrong phase functions if rail 2 differs. The phase-current formula reads `curr_sense_gain` but the helper currently does not divide by it, so reported phase values deserve scrutiny. Probe writes page 2 for configuration registers, so devices with different hidden page layout may fail.

### Test signals
Test MP2856 versus MP2857 phase limits, inactive rail 2 page reduction, VOUT VID/linear conversion, per-phase IOUT mapping across packed registers, current-sense gain detection, phase function masks, page reset to zero after probe, and failure paths for invalid phase counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2856.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2869.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2869.c

### Purpose
`mp2869.c` supports MPS MP2869-family two-rail VR controllers, including MP29608, MP29612, and MP29816 ids. It translates many vendor-defined or nonstandard telemetry and limit encodings into PMBus direct/linear values and adjusts temperature status when a TSNS digital fault mode is enabled.

### Important APIs, types, and functions
`struct mp2869_data` stores copied driver info, TSNS fault enable, and per-page VOUT/IOUT scales. `mp2869_reg2data_linear11()` converts linear11 to integer units. Identify helpers read `MFR_TSNS_FLT_SET`, `PMBUS_VOUT_SCALE_LOOP`, and `MFR_SVI3_IOUT_PRT`. `mp2869_read_byte_data()` fixes `VOUT_MODE` and remaps temperature fault bits. `mp2869_read_word_data()` handles VIN/IIN/PIN/VOUT/IOUT/POUT/temp and many limit conversions. `mp2869_write_word_data()` preserves reserved bits while writing converted limits.

### Control flow
Probe allocates data, copies `mp2869_info`, and calls `pmbus_do_probe()`. During PMBus identification, `mp2869_identify()` samples TSNS fault state and per-rail VOUT/IOUT scales. Runtime reads and writes branch by register to mask raw fields, apply scales, convert linear11 power, or return unsupported errors.

### State and persistence behavior
Per-device scale factors and TSNS mode are captured at probe. Limit writes persist on hardware and often read-modify-write to preserve upper bits. No telemetry cache is kept.

### Dependencies and integration points
It uses PMBus identify/read/write callbacks, Linux bitfield helpers, I2C/OF matching, direct-format coefficients, and MPS vendor registers that redefine standard PMBus addresses.

### Risks
The file references `PMBUS_VOUT_SCALE_LOOP` while defining the related concept only in comments; correctness depends on that macro existing in included PMBus headers. Many conversions preserve high bits; mistakes can corrupt unrelated protection settings. `mp2869_identify_thwn_flt()` failure is ignored by returning success from identify, so missing TSNS register silently disables that behavior.

### Test signals
Validate all supported ids, VOUT and IOUT scale discovery per rail, TSNS status remapping on/off, VIN/IIN/PIN/POUT conversions, VOUT OV/UV delta handling, temperature offset writes, reserved-bit preservation, and error behavior for unsupported attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2869.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2888.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2888.c

### Purpose
`mp2888.c` supports the MPS MP2888 multiphase digital VR controller. It exposes one PMBus page with virtual phase-current telemetry, corrects several nonstandard raw register encodings, and detects phase count and current resolution at probe.

### Important APIs, types, and functions
`struct mp2888_data` stores copied driver info, total and phase current resolution flags, and current-sense gain. `mp2888_current_sense_gain_and_resolution_get()` reads `MP2888_MFR_SYS_CONFIG`. `mp2888_read_phase()` extracts packed current-sense bytes and applies gain/resolution conversion. `mp2888_read_word_data()` fixes `READ_VIN`, temperature warn limits, total and phase `READ_IOUT`, power reads, and selected warning limits, while hiding unsupported standard registers with `-ENXIO`. `mp2888_write_word_data()` inversely scales writable warn limits.

### Control flow
Probe allocates data, copies base info, reads phase count from `MP2888_MFR_VR_CONFIG1`, validates it against `MP2888_MAX_PHASE`, reads current-sense gain/resolution, and registers with PMBus. Runtime per-phase reads are routed through `PMBUS_PHASE_VIRTUAL`.

### State and persistence behavior
Probe-captured phase count, current-sense gain, and resolution flags persist in driver memory. Limit writes update device registers directly. No caches are maintained.

### Dependencies and integration points
It depends on PMBus phase virtual support, direct and linear formats, I2C/OF matching, SMBus word reads/writes, and Linux bit masks.

### Risks
The comments distinguish total and phase resolution, but `mp2888_read_phase()` scales using `total_curr_resolution`; this deserves hardware validation. Many standard limit registers are explicitly suppressed to avoid invalid sysfs inputs. Current sensing is documented as inaccurate at light load, so tests need tolerance.

### Test signals
Validate phase-count detection and rejection above ten, per-phase packed current extraction, current-sense gain cases, total/phase resolution scaling, hidden unsupported registers, scaled reads/writes for IOUT/POUT/temp warning limits, and OF/I2C binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2888.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2891.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2891.c

### Purpose
`mp2891.c` supports the MPS MP2891 two-rail VR controller. It compensates for nonstandard VOUT mode, vendor-defined input telemetry registers, per-rail voltage/current scale settings, and several raw limit encodings.

### Important APIs, types, and functions
`struct mp2891_data` stores copied driver info plus per-page `vout_scale` and `iout_scale`. `mp2891_reg2data_linear11()` converts vendor linear11 values. `mp2891_identify_vout_scale()` reads `MFR_VOUT_LOOP_CTRL`; `mp2891_identify_iout_scale()` reads `MFR_SVI3_IOUT_PRT`. `mp2891_read_byte_data()` forces direct VOUT mode. `mp2891_read_word_data()` remaps IIN/PIN through `READ_IIN_EST`/`READ_PIN_EST`, converts POUT, scales VOUT/IOUT and limits, and suppresses some unsupported VIN/temp registers. `mp2891_write_word_data()` writes converted limits with reserved-bit preservation.

### Control flow
Probe allocates data, copies static info, and registers with PMBus. The PMBus identify callback discovers per-rail scales. Subsequent PMBus core reads/writes call the conversion callbacks for affected registers.

### State and persistence behavior
Scale arrays are set at probe and remain fixed. Limit writes persist on the device. No history or telemetry cache exists.

### Dependencies and integration points
It depends on PMBus direct-mode conversion, Linux bitfield helpers, I2C/OF matching for `mps,mp2891`, and vendor registers that either redefine or replace standard PMBus telemetry.

### Risks
The file returns `-EINVAL` for many unsupported default cases instead of `-ENODATA`, which can affect PMBus core probing behavior. Read and write paths for some input limits use page 0 regardless of requested page, matching comments but requiring hardware confirmation. Reserved-bit read-modify-write logic is critical for protection registers.

### Test signals
Validate VOUT and IOUT scale discovery on both pages, forced direct VOUT mode, IIN/PIN/POUT linear11 conversion, VOUT OV/UV delta math, temperature-offset writes, input and output current/power limit scaling, reserved-bit preservation, and unsupported-register visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2891.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2925.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2925.c

### Purpose
`mp2925.c` supports MPS MP2925 and MP2929 two-rail VR controllers. It forces direct VOUT mode, discovers per-rail VOUT scaling and VID offset, converts VOUT fault limits, and rewrites selected linear11 limits to fixed exponents expected by hardware.

### Important APIs, types, and functions
`struct mp2925_data` stores copied driver info, `vout_scale[]`, and `vid_offset[]`. `mp2925_linear_exp_transfer()` rewrites a linear11 word to a target exponent while preserving scaled value approximately. `mp2925_read_byte_data()` overrides `PMBUS_VOUT_MODE`. `mp2925_read_word_data()` converts `READ_VOUT` and VOUT OV/UV fault limits while deferring or suppressing other standard registers. `mp2925_write_word_data()` converts VIN/temp/current/VOUT limits to hardware-specific formats. `mp2925_identify_vout_scale()` samples `PMBUS_VOUT_MODE` and, for VID mode, reads hidden pages 3/4 `MFR_VR_MULTI_CONFIG`.

### Control flow
Probe allocates data, copies `mp2925_info`, and calls `pmbus_do_probe()`. The identify callback discovers VOUT scale for both rails. Runtime callbacks convert only the registers needing nonstandard handling.

### State and persistence behavior
Per-rail VOUT scale and VID offset persist in driver memory. Limit writes persist on the device and may preserve upper register bits by read-modify-write. No caches are kept.

### Dependencies and integration points
It depends on PMBus direct and linear11 formats, Linux bitfield helpers, I2C/OF matching for `mps,mp2925` and `mps,mp2929`, and vendor hidden configuration pages.

### Risks
The source contains a non-ASCII comma in one comment, but code is unaffected. Hidden page reads for VID scaling depend on page 3/4 behavior. `mp2925_linear_exp_transfer()` can lose precision or overflow mantissa when changing exponents. Several standard registers return `-ENODATA`, leaving PMBus core to decide exposure.

### Test signals
Test MP2925/MP2929 binding, VOUT mode branches and hidden-page scale detection, VID offset conversion, VOUT OV/UV read/write scaling, fixed-exponent VIN/temp/current limit writes, reserved-bit preservation, and page state after identify.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp2925.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp29502.c -->
## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp29502.c

### Purpose
`mp29502.c` supports the MPS MP29502 single-rail VR controller. It converts extensive nonstandard telemetry and limit encodings, including vendor input telemetry, VOUT scale/divider compensation, OVP divider handling on page 1, IOUT scaling, and temperature offsets.

### Important APIs, types, and functions
`struct mp29502_data` stores copied driver info, VOUT scale, VOUT divider components, OVP divider, and IOUT scale. Identify helpers read `MFR_VOUT_SCALE_LOOP`, `MFR_VOUT_PROT1`, `MFR_VOUT_PROT2`, `MFR_SLOPE_CNT_SET`, and `MFR_SVI3_IOUT_PRT`. `mp29502_read_vout_ov_limit()` and `mp29502_write_vout_ov_limit()` temporarily switch to PMBus page 1 for OVP fields and restore page 0. `mp29502_read_word_data()` converts VIN, VOUT, IIN, PIN, POUT, IOUT, temp, and protection limits. `mp29502_write_word_data()` preserves reserved bits while writing converted limits.

### Control flow
Probe allocates data, copies static info, and calls `pmbus_do_probe()`. Identify discovers scale/divider values, sometimes reading page 1 despite the PMBus surface having one page. Runtime read/write callbacks force page 0 at entry for byte writes and many word writes, with special page 1 handling for VOUT OV fault limit.

### State and persistence behavior
Scale and divider fields are captured at probe and persist in driver memory. Limit writes persist on hardware. The callbacks actively manipulate the PMBus page register, so page restoration is part of state correctness.

### Dependencies and integration points
It depends on PMBus direct conversion, Linux bitfield helpers, I2C/OF matching for `mps,mp29502`, and MPS vendor registers with page-specific meanings.

### Risks
Divider fields are used as divisors without explicit zero checks; malformed hardware configuration could fault through divide-by-zero. Page switching for OVP must always restore page 0, including error paths; some read error paths return before restoring. The author metadata has a missing closing angle bracket. Conversion formulas are dense and should be tested against datasheet vectors.

### Test signals
Validate VOUT scale/divider/OVP/IOUT discovery, zero-divider handling if possible, page restoration after OVP reads/writes and failures, telemetry conversions for all exposed sensors, VIN/VOUT/IOUT/temp limit writes with reserved bits preserved, and unsupported `STATUS_WORD` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/mp29502.c -->
