# subset-b-003829 Research

Grouped research for the listed Ceph-client hwmon source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm90.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm90.c

## Purpose
`lm90.c` is a broad Linux hwmon I2C driver for LM90-compatible local/remote temperature sensors and many vendor variants: ADM102x/ADM1032/ADT7461/ADT7481, G781, LM84/LM86/LM89/LM90/LM99, MAX1617/MAX664x/MAX665x/MAX668x/MAX669x, NCT/Nuvoton, SA56004, TMP451/TMP461, W83L771, and aliases. It exposes up to three temperature channels, thresholds, hysteresis, remote offsets, faults, alarms, emergency limits, conversion interval, PEC, thermal-zone registration, and optional interrupt/SMBus-alert reporting through the modern hwmon ops interface.

## Important APIs, Types, And Functions
The main device contract is `struct i2c_driver lm90_driver` with `.probe`, `.detect`, `.alert`, `.id_table`, OF match table, and an address scan list. `struct lm90_params` is the chip capability matrix; its flags control register layout, signedness, temperature resolution, PEC behavior, low/critical/emergency limits, secondary status registers, and fault-queue support. `struct lm90_data` stores the client, hwmon metadata, dynamic channel configs, work items, cached registers, original configuration, conversion interval, alarm masks, and per-chip register quirks.

The hwmon API entry points are `lm90_read`, `lm90_write`, `lm90_read_string`, and `lm90_is_visible`, backed by `lm90_temp_read/write` and `lm90_chip_read/write`. Core bus helpers are `lm90_read_reg`, `lm90_write_reg`, `lm90_read16`, `lm90_write16`, `lm90_update_confreg`, and `lm90_select_remote_channel`. Temperature conversion is centralized in `lm90_temp_from_reg`, `lm90_temp_to_reg`, `lm90_get_temp`, `lm90_set_temp`, `lm90_get_temphyst`, `lm90_set_temphyst`, and offset helpers.

Detection is split by manufacturer and register behavior: `lm90_detect_lm84`, `lm90_detect_max1617`, `lm90_detect_national`, `lm90_detect_on`, `lm90_detect_analog`, `lm90_detect_maxim`, `lm90_detect_nuvoton`, `lm90_detect_nuvoton_50`, `lm90_detect_nxp`, `lm90_detect_gmt`, `lm90_detect_ti49`, and `lm90_detect_ti`. Runtime alert handling is in `lm90_update_alarms_locked`, `lm90_update_alarms`, `lm90_report_alarms`, `lm90_alert_work`, `lm90_alert`, and the IRQ thread.

## Control Flow
Probe enables an optional `vcc` regulator, allocates `lm90_data`, resolves the matched chip kind, copies per-chip parameters, disables unsupported PEC modes if the adapter lacks functionality, builds hwmon channel configuration dynamically, parses optional DT channel labels and remote offsets, initializes the chip, registers the hwmon device, installs cleanup actions, and optionally requests a threaded IRQ.

Initialization reads and saves the original conversion rate and configuration, chooses a 500 ms conversion interval for chips with configurable conversion rate, honors `ti,extended-range-enable` for extended temperature mode, applies chip-specific range/resolution setup, selects remote channel 0 for three-channel chips, unmasks interrupt output when an IRQ is present, clears STOP, and registers a devm restore action. Reads call `lm90_update_device`, which refreshes limits once and volatile temperatures/alarms after `update_interval`. For three-channel chips, the driver temporarily selects the second remote channel under the hwmon lock before reading or writing registers whose meaning changes with channel selection.

Writes update cached values and then write chip registers, including extended low-byte registers where supported. Conversion interval writes choose the nearest supported rate and update `data->update_interval`. Alert flow reads status registers, tracks current and unreported alarms, emits hwmon notifications, works around broken SMBus alert chips by disabling ALERT# until the triggering bits clear, and reschedules delayed work if alerts remain asserted.

## State And Persistence
Persistent hardware state includes configuration, conversion rate, thresholds, offsets, hysteresis, fault queue configuration, remote diode channel selection bits, and alert enable state. The driver saves `config_orig` and `convrate_orig` and restores them through a devm action on removal/failure. Runtime cache state lives in `temp[]`, `temp_hyst`, `conalert`, `current_alarms`, `alarms`, `reported_alarms`, validity booleans, and jiffies timestamps. `shutdown` gates alarm updates during teardown; work items are synchronously canceled by `lm90_stop_work`.

## Dependencies And Integration Points
The driver depends on the I2C/SMBus core, hwmon core, OF properties, jiffies, workqueues, interrupts, and optional regulator support. It integrates with device tree through compatible strings plus child `channel` nodes with `reg`, `label`, and `temperature-offset-millicelsius`. It integrates with hwmon thermal-zone registration via `HWMON_C_REGISTER_TZ`, SMBus alert via the I2C alert callback, uevent/sysfs notification through `hwmon_notify_event`, and PM by disabling/enabling the IRQ across suspend/resume.

## Risks And Edge Cases
The largest risk is the number of chip-specific register quirks: signed versus unsigned and extended formats, LM99 remote offset semantics, swapped critical alarm bits, partial PEC transactions, register aliases that change under remote-channel selection, and detection heuristics for chips lacking ID registers. Missing error propagation in some non-critical cleanup paths is intentional but can hide restore failures. The alert workaround changes config bit 7 and relies on periodic re-enable logic; regressions can leave alerts masked or storming. DT-provided offsets are written before final chip initialization, so invalid channel IDs or internal-channel offsets must reject probe.

`lm90_read16` handles volatile high/low byte races by rereading the high byte; that logic is important for accurate temperature readings. Any changes to locking around channel selection are risky because a selected remote channel changes the meaning of shared register addresses. Auto-detection can misidentify known ambiguous devices, especially LM89/LM99 and MAX6657/MAX6659 at common addresses, and the comments document accepted tradeoffs.

## Test Signals
Useful tests include build coverage with I2C, hwmon, OF, IRQ, regulator, and PM enabled; probe tests for explicit `i2c_device_id` and OF matches; sysfs/hwmon reads for all visible attributes per chip flag combination; writes for thresholds, hysteresis, offsets, conversion interval, and fault queue; simulated SMBus errors and partial PEC reads; interrupt/SMBus-alert tests that verify `hwmon_notify_event`; removal tests that verify config/conversion restore and work cancellation; and detection tests using register maps for ambiguous chip families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm90.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm92.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm92.c

## Purpose
`lm92.c` is a compact hwmon I2C driver for National LM92 and Maxim MAX6635 local temperature sensors. It exposes one temperature channel with input, min, max, critical threshold, hysteresis-derived threshold values, individual alarms, and aggregate chip alarms through the modern `hwmon_device_register_with_info` interface.

## Important APIs, Types, And Functions
`struct lm92_data` stores the regmap and limit-register resolution, which differs between LM92 and MAX6635. `TEMP_FROM_REG`, `TEMP_TO_REG`, and `ALARMS_FROM_REG` translate the LM92 left-justified 13-bit signed register format and alarm bits. The hwmon callbacks are `lm92_read`, `lm92_write`, and `lm92_is_visible`, with type-specific helpers `lm92_temp_read`, `lm92_temp_write`, and `lm92_chip_read`.

Regmap is customized through `lm92_reg_read` and `lm92_reg_write`, because config is an 8-bit SMBus byte while the temperature registers are swapped 16-bit SMBus words. `lm92_regmap_is_volatile` marks only live temperature as volatile, and `lm92_regmap_is_writeable` allows config and threshold writes. `lm92_detect`, `lm92_init_client`, and `lm92_probe` provide discovery, startup, and registration.

## Control Flow
Probe creates a regmap on the custom SMBus bus, allocates state, records the matched resolution from `i2c_device_id` driver data, clears the shutdown bit in the configuration register, and registers the hwmon chip. Reads dispatch by sensor type; temperature reads either read one threshold/input register, combine a threshold with the common hysteresis register using `regmap_multi_reg_read`, or read the live temperature register to expose alarm bits. Writes update min, max, critical, or critical hysteresis; hysteresis writes read the current critical limit, convert the requested critical-hysteresis temperature into a hysteresis delta, and write the shared hysteresis register.

Detection scans addresses 0x48-0x4b, requires byte and word SMBus support, and reads manufacturer/config registers twice at repeated register aliases separated by eight to improve confidence. Only LM92 is auto-detected; MAX6635 is supported by explicit ID.

## State And Persistence
The hardware persists config, min/max/critical thresholds, and hysteresis. Regmap caches non-volatile registers with `REGCACHE_MAPLE`, while live temperature remains volatile. The only driver state is `resolution`, which changes limit quantization, and the regmap pointer. There is no explicit remove-time restore of previous config; initialization always starts conversions by clearing config bit 0.

## Dependencies And Integration Points
The driver depends on I2C SMBus byte/word operations, regmap, and hwmon. It integrates with legacy I2C class scanning through `.class = I2C_CLASS_HWMON`, explicit IDs `lm92` and `max6635`, and source-tree standard hwmon channel descriptors. It has no OF table, IRQ path, workqueue, or thermal-zone registration flag.

## Risks And Edge Cases
The mixed 8-bit/16-bit register model makes the custom regmap bus important; using a plain I2C regmap would corrupt config or endian handling. `TEMP_FROM_REG` intentionally truncates without rounding. The shared hysteresis register means min/max/crit hysteresis reads are derived, while only `crit_hyst` is writable; writes depend on the current critical limit. Auto-detection relies on LM92 manufacturer ID and repeated register behavior, so compatible unsupported chips may need explicit IDs rather than scan detection.

## Test Signals
Test signals include compile coverage, regmap read/write traces for byte config and swapped-word temperatures, hwmon sysfs reads for input/limits/hysteresis/alarms, writes that verify LM92 13-bit versus MAX6635 9-bit limit rounding, probe initialization clearing shutdown, and detection fixtures with valid and invalid repeated manufacturer/config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm92.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm93.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm93.c

## Purpose
`lm93.c` is a legacy hwmon driver for National LM93/LM94 system hardware monitors. It exposes a large fixed sysfs attribute group for sixteen voltage inputs, three temperature zones with automatic fan-control parameters, four fans, two PWM outputs, VID, PROCHOT/VRDHOT status and override controls, GPIO state, and a compact 32-bit alarm view derived from wider hardware status.

## Important APIs, Types, And Functions
The driver uses `devm_hwmon_device_register_with_groups` with a manually declared `lm93_attrs` array rather than the newer `hwmon_chip_info` callback model. `struct lm93_data` is the central cache, organized around the chip's fixed block-read groups: alarm block, temperatures, VINs, PROCHOT, fan tach counts, limits, PWM control registers, auto-temperature base/offset registers, config, VID, GPIO, PROCHOT override/interval, boost and hysteresis registers, and saved PWM override duty values.

Conversion helpers encode the hardware units and bit layouts: `LM93_IN_FROM_REG`, `LM93_IN_TO_REG`, `LM93_IN_REL_FROM_REG`, `LM93_IN_REL_TO_REG`, `LM93_TEMP_FROM_REG`, `LM93_TEMP_TO_REG`, auto-offset helpers, PWM duty/frequency maps, `LM93_FAN_FROM_REG`, `LM93_FAN_TO_REG`, spinup/ramp/prochot interval conversions, `LM93_GPI_FROM_REG`, and `LM93_ALARMS_FROM_REG`. Bus helpers `lm93_read_byte`, `lm93_read_word`, `lm93_write_byte`, `lm93_write_word`, and `lm93_read_block` wrap SMBus operations with retry logging. Update paths are `lm93_update_client_full`, `lm93_update_client_min`, `lm93_update_client_common`, and `lm93_update_device`.

## Control Flow
Probe selects the update method from adapter functionality and the `disable_block` module parameter. Full mode uses SMBus block commands for grouped reads; minimum mode reads all bytes/words individually. Probe allocates state, initializes the mutex, calls `lm93_init_client`, and registers the complete attribute group.

`lm93_update_device` locks the cache, refreshes after 1.5 seconds or when invalid, calls the selected update routine, and marks the cache valid. Full update reads voltage, temperature, PROCHOT, fan, PWM, alarm, and auto/PWM blocks, then calls the common update routine for registers not covered by block commands. Minimum update reads the same data through individual byte/word operations. Common update reads temperature limits, config, VID, PROCHOT limits, VCCP relative limits, GPIO, override/interval, boost, hysteresis, ramp, setup registers, and writes the previous alarm bytes back to clear them.

Each sysfs callback reads cached data through `lm93_update_device` for show paths or locks `update_lock` for store paths. Store callbacks parse numeric input, clamp or map to hardware encoding, update cached fields, and write affected registers. Several writes modify packed nibbles or bitfields, such as automatic temperature offsets, PWM min/hysteresis, smart tach mappings, PROCHOT intervals, and PWM frequency. `lm93_init_client` optionally forces broader chip initialization when the `init` module parameter is set, starts monitoring, and polls for readiness.

## State And Persistence
State persists primarily in chip registers: voltage/temp/fan thresholds, fan-control tables, smart tach mappings, PWM mode/frequency/duty, PROCHOT override/interval, VCCP limit mode, GPIO/VID threshold setup, alert/status-control settings, and sleep/monitoring state. Runtime cache persists all block values for up to 1.5 seconds. Module parameters alter behavior globally: `disable_block`, `init`, `vccp_limit_type[2]`, and `vid_agtl`. `pwm_override[]` is driver-only state preserving the user-commanded PWM value because the corresponding hardware field can read back differently when override is active.

## Dependencies And Integration Points
The driver depends on I2C SMBus byte/word support and optionally block data, hwmon sysfs helpers, `hwmon-vid` for VRM/VRD10 VID conversion, jiffies, mutexes, and sleep/delay APIs. It integrates with I2C hwmon class scanning at 0x2c-0x2e and detects LM93/LM94 by manufacturer/version registers. User space integration is the legacy libsensors-compatible sysfs names rather than dynamic hwmon channel descriptors.

## Risks And Edge Cases
The largest risk is error handling: `lm93_read_byte` and `lm93_read_word` return zero after all retries rather than propagating an error, so failed transactions can populate plausible low values and mark the cache valid. `lm93_read_block` leaves destination values unchanged if all retries fail. Several store callbacks ignore write errors and return `count`, so hardware write failures may be invisible. The global `lm93_block_buffer` is shared, but update paths are serialized per device by `update_lock`; cross-device concurrent block reads could still share the static buffer if multiple LM93 devices are active.

Packed bitfield writes are easy to regress, especially where setting one temp zone affects a shared register or where PWM frequency 22.5 kHz disables smart tach. `pwm_auto_vrdhot_ramp_store` returns `0` on success instead of `count`, which can surprise sysfs writers. The alarm conversion intentionally drops some hardware alarm bits to fit a 32-bit value. Module parameters shape ABI behavior and can make in7/in8 thresholds absolute or VID-relative.

## Test Signals
Useful tests include compile coverage, sysfs attribute presence and permissions, full and minimum SMBus update paths, retry/error injection for byte/word/block reads, write-path tests for each packed field, validation of VIN scaling per channel, VID-relative threshold behavior under both `vccp_limit_type` modes, fan RPM edge cases for stopped and overflow counts, alarm clearing by writeback, and probe detection for LM93 versus LM94 version IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm95234.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm95234.c

## Purpose
`lm95234.c` is a hwmon I2C driver for TI/National LM95233 and LM95234 multi-channel temperature sensors. It exposes local and remote temperatures, per-channel enable, max/critical limits, hysteresis, remote diode type, offsets, faults, alarms, and conversion update interval through regmap-backed hwmon callbacks.

## Important APIs, Types, And Functions
`struct lm95234_data` stores the regmap and chip type (`lm95233` or `lm95234`). `lm95234_read_temp` reads local signed temperatures and remote unsigned temperatures, falling back to signed remote registers when the unsigned value is zero. `lm95234_temp_read` and `lm95234_temp_write` implement hwmon temp attributes; `lm95234_chip_read/write` handle `update_interval`. `lm95234_crit_reg`, `lm95234_alarm_reg`, `lm95234_hyst_get`, and `lm95234_hyst_set` capture register sharing and channel-specific limit layout.

Regmap policy is defined by `lm95234_volatile_reg`, `lm95234_writeable_reg`, and `lm95234_regmap_config`. `lm95234_detect` validates manufacturer ID, chip ID, legal addresses, status/config/conversion/model masks, and writes the matched type string. `lm95234_init_client` starts conversions and repairs remote diode type misconfiguration if status indicates a mismatch between model and model-status registers.

## Control Flow
Probe allocates state, stores match data, initializes I2C regmap, starts the chip by clearing the stop bit, optionally fixes diode model configuration, and registers the hwmon chip. Visibility depends on chip type and channel: LM95233 hides channels above two, local channel hides remote-only type/offset/fault attributes, remote channels expose diode type and offset, and only channels one and two expose critical limits/alarms.

Read flow maps hwmon attributes to one or more register reads. Temperature input reads use signed local registers for channel 0 and remote unsigned/signed pairs for remote channels. Max and critical alarms read separate status registers depending on channel. Hysteresis reads subtract the shared hysteresis register from the relevant limit. Fault reads use two-bit masks per remote channel. Write flow validates booleans and diode type values, updates enable/model bits, writes remote offsets in 0.5 degree steps, clamps limits, and updates shared hysteresis relative to local TCRIT1.

## State And Persistence
Persistent hardware state includes enable bits, conversion rate, remote model bits, offsets, TCRIT/TCRIT2 limits, max limits, and the shared TCRIT hysteresis. Regmap caches non-volatile writable registers with `REGCACHE_MAPLE`; temperatures, fault/status, TCRIT status, and model status are volatile. Driver state is small and does not cache readings independently of regmap.

## Dependencies And Integration Points
The driver depends on I2C SMBus byte operations through regmap, hwmon core, `find_closest`, and standard I2C class scanning. It integrates with explicit IDs `lm95233` and `lm95234`, scan addresses 0x18/0x2a/0x2b/0x4d/0x4e, and the hwmon channel API. There is no OF match table in this file, no IRQ handling, and no explicit regulator or PM integration.

## Risks And Edge Cases
The main semantic risk is channel/register asymmetry: channels 1 and 2 have TCRIT2 registers for max, while other channels use TCRIT1; only some channels support critical attributes. Hysteresis is shared and `lm95234_hyst_set` is based on local TCRIT1, so user expectations for per-channel hysteresis can be wrong. Remote temperature signed/unsigned fallback treats an unsigned zero as a signal to read signed registers, which is device-specific and must not be generalized without care. Offset writes use `channel - 1`, so visibility must continue hiding offset for channel 0.

## Test Signals
Useful signals include regmap compile coverage, probe/detect fixtures for LM95233 and LM95234 legal addresses and invalid mask bits, visibility tests for channel count and per-channel attributes, temperature conversion tests for signed and unsigned remote reads, write/readback tests for enable/model/offset/limits/hysteresis/update interval, and fault/alarm bit mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm95234.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm95241.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm95241.c

## Purpose
`lm95241.c` is a hwmon I2C driver for National LM95231/LM95241 temperature sensors with one local and two remote channels. It exposes temperature inputs, remote range min/max controls, diode type selection, fault flags, and update interval.

## Important APIs, Types, And Functions
`struct lm95241_data` stores the I2C client, cache timestamp, selected interval, validity flag, six temperature bytes, status, config, remote model, and TruTherm configuration. `temp_from_reg_signed` and `temp_from_reg_unsigned` convert high/low byte pairs at 1/256 degree resolution. `lm95241_update_device` refreshes temperature/status cache. `lm95241_read_chip`, `lm95241_read_temp`, `lm95241_write_chip`, and `lm95241_write_temp` implement hwmon callbacks.

The driver uses static register lists in `lm95241_reg_address` rather than regmap. `lm95241_detect` validates manufacturer and chip ID. `lm95241_init_client` sets a 1-second conversion rate, enables remote filters, disables TruTherm by default, writes remote model state, and starts the chip. HWMON descriptors expose one local input-only channel and two remote input/min/max/type/fault channels.

## Control Flow
Probe allocates state, stores the client, initializes the chip, and registers with hwmon. Reads of temperature attributes call `lm95241_update_device`; the cache refreshes after `data->interval` or when invalid. For temperature input, local values are always signed, while remote values are signed when the corresponding config range bit is set and unsigned otherwise. Remote min/max reads do not read hardware limit registers; they report the effective range implied by signed/unsigned configuration bits. Fault reads report diode-missing bits from status.

Writes to `update_interval` choose one of four hardware conversion rates by threshold and update `config`, `interval`, and the config register. Writes to remote min/max toggle the signed-range bits based on whether the requested range needs negative or above-127.875C temperatures. Writes to diode type validate values 1 or 2, update remote model bits, and keep TruTherm enabled for transistor mode and disabled for diode mode.

## State And Persistence
Hardware state persisted by the driver is config conversion/range bits, remote filter enable, TruTherm bits, and remote model bits. Cached state includes last-read temperatures, status, config/model/trutherm mirrors, validity, and interval. There is no locking around the cache or writes; hwmon callbacks can race in theory if sysfs accesses overlap, although operations are small SMBus byte transactions.

## Dependencies And Integration Points
The driver depends on raw I2C SMBus byte data, hwmon, jiffies, and I2C class scanning. It integrates through IDs `lm95231` and `lm95241`, scan addresses 0x19/0x2a/0x2b, and standard hwmon callback registration. There is no regmap, OF table, interrupt path, or remove-time restoration.

## Risks And Edge Cases
`lm95241_update_device` stores raw SMBus return values into `u8` fields without checking for negative errors, so read failures can become 0xff-like cached data and still mark the cache valid. Lack of an update mutex can allow concurrent sysfs writes and reads to observe partially updated mirrors. The R2DF mask is defined as `BIT(2)`, the same as `R2MS_MASK`, so range and model semantics share a bit name space and must be checked against the datasheet before modifications. Min/max attributes are effectively mode selectors, not programmable threshold registers.

## Test Signals
Test with build coverage, probe/detect register fixtures, cache refresh timing, error injection for SMBus reads, update interval thresholds, remote signed/unsigned conversion and range toggling, diode type writes that update both model and TruTherm registers, and concurrent sysfs read/write stress if modifying state handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm95241.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm95245.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lm95245.c

## Purpose
`lm95245.c` is a regmap-backed hwmon I2C driver for TI/National LM95235/LM95245 two-channel temperature sensors. It exposes local critical temperature and remote temperature input, max/critical limits, common hysteresis, remote diode type, offset, fault, alarms, and update interval.

## Important APIs, Types, And Functions
`struct lm95245_data` contains the regmap and current conversion interval. Temperature conversion helpers are `temp_from_reg_unsigned` and `temp_from_reg_signed`. Conversion rate handling is in `lm95245_read_conversion_rate` and `lm95245_set_conversion_rate`. Hwmon operations are implemented by `lm95245_read`, `lm95245_write`, `lm95245_is_visible`, with type-specific `lm95245_read_temp/write_temp` and `lm95245_read_chip/write_chip`.

Regmap behavior is described by `lm95245_is_writeable_reg`, `lm95245_is_volatile_reg`, and `lm95245_regmap_config`; single reads/writes are forced. `lm95245_detect` validates manufacturer ID, revision, and LM95235 address restrictions. `lm95245_init_client` reads the initial conversion rate and clears STOP. The driver includes both I2C IDs and OF compatibles for `national,lm95235` and `national,lm95245`.

## Control Flow
Probe allocates state, creates regmap, initializes conversion state/startup, and registers hwmon. Input reads for the local channel use signed local high/low registers. Remote input first reads signed remote low/high registers; if the signed high byte indicates a negative value or a value below the signed upper limit, it returns signed conversion, otherwise it reads the remote unsigned register pair and returns unsigned conversion. Limit and hysteresis reads map to remote OS, local/remote TCRIT, and common hysteresis registers. Alarm/fault reads use status register 1.

Writes clamp and convert remote max, local/remote critical limits, local-based common critical hysteresis, remote offset, remote diode type, and update interval. `temp_crit_hyst` is writable only on channel 0; channel 1 exposes it read-only through visibility. Update interval writes select the nearest supported 63/364/1000/2500 ms conversion rate.

## State And Persistence
Hardware state includes config1 STOP, conversion rate, config2 diode/filter bits, remote offset, remote OS limit, local/remote TCRIT limits, and common hysteresis. Regmap caches non-volatile registers with `REGCACHE_MAPLE`, while status and live temperature registers are volatile. Driver state caches only the currently selected interval.

## Dependencies And Integration Points
The driver depends on I2C, regmap, hwmon, OF match support, and I2C class scanning. It exposes modern hwmon channel descriptors and supports firmware-instantiated devices through OF. It does not use IRQs, regulators, thermal-zone registration flags, or explicit PM callbacks.

## Risks And Edge Cases
Remote signed-versus-unsigned selection is subtle and based on high-byte thresholds; changes can break high positive remote temperatures. `temp_from_reg_signed` ignores the low byte for negative values, so negative fractional temperatures are truncated to whole degrees by current design. Hysteresis is common and written relative to the local OS/TCRIT register, not independently per channel. `lm95245_history`-style persistence is not present; alarms are direct status reads. Detect permits LM95245 revision at all scanned addresses but restricts LM95235 to documented addresses.

## Test Signals
Useful tests include probe through I2C ID and OF match, detection fixtures for revisions/address restrictions, regmap volatile/writeable policy checks, conversion-rate read/write tests, remote signed/unsigned transition cases, offset two-byte writes, local versus remote critical limit clamping, common hysteresis read/write behavior, and status-bit mapping for max/critical/fault alarms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lm95245.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lochnagar-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/lochnagar-hwmon.c

## Purpose
`lochnagar-hwmon.c` is a platform hwmon driver for Cirrus Logic Lochnagar2 board monitoring. It exposes one board temperature input plus voltage, current, and average power readings for eight named supply channels, with a writable power averaging interval per channel.

## Important APIs, Types, And Functions
`struct lochnagar_hwmon` stores the parent MFD regmap and per-channel power sample counts. `enum lochnagar_measure_mode` selects current, voltage, or temperature measurements. `float_to_long` converts the hardware's IEEE-754-like 32-bit measurement value into integer milli/micro units with saturation. `do_measurement` programs the IMON measurement control registers, waits for configure and measurement completion, and clears control state. `request_data` asks the hardware for one channel's measured data and assembles the 32-bit value. `read_sensor` composes measurement and data fetch, while `read_power` computes power from voltage and current.

Hwmon integration is through `lochnagar_read`, `lochnagar_read_string`, `lochnagar_write`, `lochnagar_is_visible`, and `lochnagar_chip_info`. `lochnagar_hwmon_probe` retrieves the parent regmap, initializes default averaging samples, and registers the hwmon device. The platform driver binds to `cirrus,lochnagar2-hwmon`.

## Control Flow
Probe allocates state, gets the regmap from the parent MFD device, initializes all power sample counts to 96, and registers the hwmon device named `Lochnagar`. For each read, the hwmon core dispatches by type: voltage and current perform a one-sample measurement, temperature performs a one-sample temperature measurement, and power average performs voltage measurement plus current measurement using the stored sample count. SYSVDD voltage is hidden and power uses a fixed 5 V multiplier for that channel.

Measurement flow writes `IMON_CTRL1` with enable, channel mask, and mode, writes sample count to `IMON_CTRL2`, writes configure to `IMON_CTRL3`, polls done, writes measure to `IMON_CTRL3`, sleeps approximately 1.5 ms per sample, polls completion, and clears control. Data request writes `IMON_CTRL4`, polls data ready, reads `DATA1` and `DATA2`, and clears the request. Average interval writes clamp the requested milliseconds to the hardware sample range, convert to sample count, and store it in driver memory.

## State And Persistence
The driver does not persist calibration or thresholds. Runtime state is the per-channel `power_nsamples[]` array; it is not written to hardware until a power measurement request. Hardware measurement control registers are transient and cleared after each operation. The parent MFD regmap is shared with other Lochnagar functions, so measurement control state must be left idle after reads.

## Dependencies And Integration Points
The driver depends on the Lochnagar MFD core, Lochnagar2 register definitions, regmap, hwmon, platform bus, OF matching, polling helpers, sleep timing, and 64-bit division/math helpers. It integrates with parent-provided regmap rather than owning an I2C/SPI device directly. User-space labels come from the fixed channel name table.

## Risks And Edge Cases
There is no explicit mutex around measurement sequences, so concurrent hwmon reads could interleave writes to shared IMON control registers unless higher layers serialize accesses. Measurements can sleep for up to the sample-dependent delay and poll up to 200 ms, so high-frequency user-space polling can be costly. `float_to_long` handles overflow by saturating to `LONG_MAX`, but assumes hardware never returns NaN. SYSVDD has special visibility and fixed-voltage behavior that must remain aligned with channel-name ordering.

## Test Signals
Test signals include platform probe with and without parent regmap, OF match binding, visibility for SYSVDD voltage hiding, label reads for voltage/current/power channels, average interval clamping and sample conversion, mocked regmap sequences for configure/measure/data-ready success and timeout, IEEE conversion edge cases including negative and saturating values, and concurrent read stress if locking changes are introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/lochnagar-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2945.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2945.c

## Purpose
`ltc2945.c` is a hwmon I2C driver for the Linear Technology/ADI LTC2945 power monitor. It exposes VIN and ADIN voltages, sense current, power, min/max thresholds, historical min/max registers, reset-history controls, and fault alarms through a legacy hwmon sysfs attribute group.

## Important APIs, Types, And Functions
`struct ltc2945_data` stores the regmap and shunt resistor value in micro-ohms. `is_power_reg` distinguishes 24-bit power registers from 12-bit voltage/current registers. `ltc2945_reg_to_val` converts hardware registers into microwatts, millivolts, or milliamps using the shunt resistor and the control register's multiplier selection bit. `ltc2945_val_to_reg` performs the reverse conversion for threshold writes. Sysfs callbacks are `ltc2945_value_show`, `ltc2945_value_store`, `ltc2945_history_store`, and `ltc2945_bool_show`.

Attributes are declared with `SENSOR_DEVICE_ATTR_*` for `in1`, `in2`, `curr1`, and `power1` values, thresholds, historical extremes, reset-history controls, and alarms. Regmap is a simple 8-bit register/8-bit value map up to `LTC2945_MIN_ADIN_THRES_L`. `ltc2945_probe` handles allocation, regmap setup, device-property parsing, fault clearing, and hwmon registration. The driver has an OF compatible `adi,ltc2945` plus an I2C ID.

## Control Flow
Probe allocates state, initializes I2C regmap, reads optional `shunt-resistor-micro-ohms` from firmware defaulting to 1000, rejects zero shunt resistance, clears the fault register, and registers the attribute group. Show paths bulk-read either three bytes for power or two bytes for other measurement registers, convert to user units, and print with `sysfs_emit`. Store paths parse unsigned integers, convert to register units, clamp to 24-bit or 12-bit width, and bulk-write threshold registers.

History reset requires writing `1`. It sets CONTROL test mode, writes all-ones to the selected minimum register, maps to the corresponding maximum register, writes zeros there, and attempts to clear test mode even if the maximum reset fails. Alarm reads fetch the fault register, mask the requested bit, clear reported bits by updating the fault register, and return a boolean.

## State And Persistence
Persistent hardware state includes threshold registers, min/max history registers, fault register bits, and control register bits. The driver persists only the configured shunt resistor. There is no software cache of measurements. Fault alarm reads have side effects because reported bits are cleared. History reset temporarily changes CONTROL test mode and restores it before returning.

## Dependencies And Integration Points
The driver depends on I2C, regmap, hwmon sysfs helpers, firmware device properties, and OF matching. It integrates through `devm_hwmon_device_register_with_groups`, so the ABI is fixed by the declared sysfs attributes rather than dynamic hwmon channel descriptors. Scaling depends on board-specific shunt resistance supplied by firmware.

## Risks And Edge Cases
Conversion math is the critical area: power scaling depends on `CONTROL_MULT_SELECT`, shunt resistance, and 24-bit values, with overflow explicitly considered through 64-bit math. Wrong shunt properties produce consistently wrong current and power. `ltc2945_history_store` does not check the return from setting test mode before resetting history, so a control write failure can be followed by history writes. Alarm reads clear latched fault bits, so polling changes hardware-observable state. Store paths accept only unsigned values and clamp silently to hardware ranges.

## Test Signals
Useful tests include probe with default, custom, and zero shunt resistor properties; conversion fixtures for power in both multiplier modes, VIN, ADIN, and sense current; threshold write encoding and clamping; reset-history behavior including test-mode clear on failures; alarm read-and-clear side effects; OF/I2C binding; and sysfs attribute presence/permissions for all voltage/current/power groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ltc2945.c -->
