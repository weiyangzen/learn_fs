# Research: subset-b-005181

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8997-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8997-regulator.c

## Purpose
Implements the regulator subdriver for Maxim MAX8997/MAX8966 PMICs. It exposes LDOs, bucks, safeout outputs, 32 kHz outputs, charger constant-voltage/current controls, and topoff current as Linux regulator devices behind the parent MFD I2C device.

## Important APIs, Types, And Functions
`struct max8997_data` stores parent `max8997_dev`, registered count, ramp delay, GPIO-DVS enable flags, cached BUCK1/2/5 DVS selector tables, three DVS GPIO descriptors, current DVS GPIO index, side-effect policy, and saved suspend states. `regulators[]` is the `struct regulator_desc` table. Key callbacks are `max8997_get_enable_register()`, `max8997_get_voltage_register()`, `max8997_set_voltage_ldobuck()`, `max8997_set_voltage_buck()`, `max8997_assess_side_effect()`, `max8997_set_voltage_charger_cv()`, `max8997_set_voltage_safeout_sel()`, current-limit helpers, and `max8997_reg_disable_suspend()`. Probe uses `max8997_pmic_dt_parse_pdata()`, `devm_gpiod_get_index()`, and `devm_regulator_register()`.

## Control Flow
The platform driver binds to `max8997-pmic`, gets the MFD parent data, optionally parses the `regulators` DT subnode and MAX8997-specific buck DVS properties, converts requested DVS voltages to hardware selectors, initializes all BUCK1/2/5 DVS slots to safe maximums, then writes configured DVS slots. If any BUCK1/2/5 rail uses GPIO-DVS, probe acquires three DVS GPIOs, sets their initial levels from the default DVS index, and enables GPIO-DVS bits in BUCK control registers. Each regulator operation resolves the target enable or voltage register by regulator ID, then reads or updates the parent I2C register. GPIO-DVS buck voltage changes pick a DVS index that contains the requested selector and minimizes voltage movement on other GPIO-DVS bucks.

## State And Persistence
Runtime state is held in `struct max8997_data` and in hardware registers. The DVS selector arrays mirror platform/DT configuration, `buck125_gpioindex` tracks the currently selected GPIO state, and `saved_states[]` stores old enable-register bytes when regulators are disabled for suspend. The driver does not persist state outside the PMIC; hardware register values and GPIO levels survive until changed by firmware, reset, suspend, or another driver path.

## Dependencies And Integration Points
Depends on the MAX8997 MFD core, MAX8997 private register helpers, GPIO consumer API, OF regulator parsing, platform devices, and the regulator framework. Integration surfaces are DT regulator child nodes named after descriptor names, properties such as `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck125-default-dvs-idx`, `max8997,pmic-buck*-dvs-voltage`, and the parent MFD I2C client.

## Risks And Test Signals
Main risks are wrong DVS voltage arrays, invalid default DVS index, unintended cross-rail voltage movement when several bucks share GPIO-DVS, ignored I2C update failures during bulk DVS initialization, suspend disable behavior for special LDOs, and register descriptor drift against PMIC headers. Test by probing with and without OF data, registering every descriptor, sweeping LDO/buck voltage selections, exercising GPIO-DVS transitions while observing all three buck outputs, validating current limit and charger CV selectors, and suspend/resume tests for `set_suspend_disable()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8997-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8998.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8998.c

## Purpose
Provides the regulator subdriver for Maxim MAX8998 and compatible LP3974 PMICs. It registers LDO, buck, safeout, 32 kHz, charger, and miscellaneous enable-only regulators from the parent MFD device.

## Important APIs, Types, And Functions
`struct max8998_data` stores parent device state, BUCK1/2 predefined voltage selectors, last selected DVS index, and optional BUCK DVS GPIOs. `regulators[]` defines linear voltage descriptors and the charger current table. Important helpers include `max8998_get_enable_register()`, `max8998_get_voltage_register()`, `max8998_set_voltage_ldo_sel()`, `max8998_set_voltage_buck_sel()`, `buck1_gpio_set()`, `buck2_gpio_set()`, `max8998_set_voltage_buck_time_sel()`, current-limit helpers, and `max8998_pmic_dt_parse_pdata()`.

## Control Flow
Probe binds to `max8998-pmic` or `lp3974-pmic`, gets parent platform data, parses OF regulator children and buck DVS properties when present, allocates private state, obtains optional BUCK1 and BUCK2 DVS GPIOs, and preloads BUCK voltage registers from DT/platform voltage arrays. Register callbacks compute ONOFF and voltage register locations from regulator ID, then use MAX8998 MFD I2C helpers. BUCK1 can use four GPIO-selected voltage slots, BUCK2 can use two, and unlocked operation can overwrite a slot when no existing slot matches the requested selector.

## State And Persistence
Driver state tracks the selected BUCK1/2 DVS slot and cached selector values. Hardware state is stored in PMIC ONOFF, LDO, BUCK, CHGR, and ramp registers. The charger enable bit is inverted, so charger operations intentionally swap enable and disable behavior. No persistent filesystem state exists.

## Dependencies And Integration Points
Depends on the MAX8998 MFD core, private register helpers, GPIO consumer API, OF regulator parsing, platform driver matching, and regulator core. DT integration uses a parent `regulators` node plus MAX8998 buck voltage lock/default-index/voltage-array properties.

## Risks And Test Signals
Risks include bad descriptor index arithmetic from `id - MAX8998_LDO2`, mismatched optional DVS GPIO wiring, DVS slot overwrite surprises when `buck_voltage_lock` is false, inverted charger enable semantics, and ramp-delay differences between MAX8998 and LP3974. Test by registering both compatible types, reading and changing all linear regulators, toggling charger enable/current limit, verifying GPIO DVS slot selection on hardware, and checking that invalid DT DVS arrays fail probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8998.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13783-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mc13783-regulator.c

## Purpose
Defines the MC13783-specific regulator table and platform driver on top of the shared MC13xxx regulator core. It covers switchers, LDOs, GPO outputs, and power gate outputs for the Freescale/NXP MC13783 PMIC.

## Important APIs, Types, And Functions
`mc13783_regulators[]` is an indexed array of `struct mc13xxx_regulator` descriptors built with MC13xxx macros and MC13783 voltage tables. The special GPO/power-gate path is implemented by `mc13783_powermisc_rmw()`, `mc13783_gpo_regulator_enable()`, `mc13783_gpo_regulator_disable()`, `mc13783_gpo_regulator_is_enabled()`, and `mc13783_gpo_regulator_ops`. Probe is `mc13783_regulator_probe()`.

## Control Flow
The platform driver binds to `mc13783-regulator`, determines regulator count from DT `regulators` children or platform data, allocates `struct mc13xxx_regulator_priv`, attaches the parent `struct mc13xxx`, parses DT regulator init data through the shared core, and registers each requested descriptor. Normal regulators use exported MC13xxx ops for register read/modify/write. GPO and power-gate regulators use the local POWERMISC helper to preserve power-gate state and handle the inverted enable value for `PWGT1SPI` and `PWGT2SPI`.

## State And Persistence
The private state stores the parent PMIC pointer, descriptor array pointer, regulator devices, and `powermisc_pwgt_state`, which mirrors inverted power-gate bits so mixed writes to POWERMISC do not lose gate state. Persistent state is PMIC register state only.

## Dependencies And Integration Points
Depends on the MC13xxx MFD API (`mc13xxx_reg_read`, `mc13xxx_reg_rmw`, locking), shared `mc13xxx.h`/core ops, platform data or OF regulator parsing, and regulator framework. The platform device is normally created by the parent MC13783 MFD.

## Risks And Test Signals
Risks include wrong voltage tables for duplicated selectors, active-low power-gate semantics, POWERMISC updates racing without the MC13xxx lock, and mismatch between DT child names and descriptor names. Test by DT and platform-data registration, voltage table listing for every rail, GPO/power-gate enable/disable/is_enabled cycles, and concurrent POWERMISC updates under debug tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13783-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13892-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mc13892-regulator.c

## Purpose
Implements MC13892-specific regulators using the shared MC13xxx regulator core, including switchers with high-range selector behavior, LDOs, fixed rails, GPOs, power gates, USB, and VCAM mode support.

## Important APIs, Types, And Functions
`mc13892_regulators[]` defines descriptor metadata and voltage tables. Special callbacks are `mc13892_sw_regulator_get_voltage_sel()`, `mc13892_sw_regulator_set_voltage_sel()`, `mc13892_powermisc_rmw()`, GPO/power-gate callbacks, and `mc13892_vcam_set_mode()`/`mc13892_vcam_get_mode()`. Probe reads silicon revision, enables switcher auto mode on revision `0x45d0`, installs VCAM mode ops by copying and patching regulator ops, and registers regulators.

## Control Flow
Probe gets the parent MC13892 device and requested regulator list, allocates MC13xxx private state, locks the parent to read revision and configure switcher mode registers on 2.0A silicon, then parses OF or platform regulator data. Normal LDO/fixed regulators use shared ops. Switcher ops translate Linux selectors to hardware low/high range by using `SWxHI` and `MC13892_SWxHI_SEL_OFFSET`, excluding SW1 from high-range handling. VCAM mode toggles `VCAMCONFIGEN` for FAST mode.

## State And Persistence
State lives in MC13xxx private data and PMIC registers. `powermisc_pwgt_state` preserves inverted power-gate bits. The patched global `mc13892_vcam_ops` and descriptor ops pointer are process-global driver state initialized at probe. No disk persistence exists.

## Dependencies And Integration Points
Depends on MC13892 MFD headers, MC13xxx core APIs and locking, platform/OF regulator init data, and the regulator framework. It integrates through a `mc13892-regulator` platform device and child regulator names matching the descriptor names.

## Risks And Test Signals
Risks are high-range selector off-by-one bugs, unsupported silicon revisions with different voltage tables, global mutation of VCAM ops, inverted power-gate state, and GPO4 masking with `GPO4ADINEN`. Test by voltage get/set around the 1.375 V high-range boundary, SW1 high-bit avoidance, revision-specific auto-mode writes, VCAM mode toggles, GPO/power-gate cycles, and DT child-name coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13892-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx-regulator-core.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx-regulator-core.c

## Purpose
Provides shared regulator operations and OF parsing helpers for MC13xxx-family PMIC regulator drivers.

## Important APIs, Types, And Functions
Exports `mc13xxx_regulator_ops`, `mc13xxx_fixed_regulator_ops`, `mc13xxx_fixed_regulator_set_voltage()`, `mc13xxx_get_num_regulators_dt()`, and `mc13xxx_parse_regulators_dt()`. Runtime callbacks include enable, disable, is_enabled, table voltage listing, selector set, and voltage read through `struct mc13xxx_regulator_priv` and per-chip `struct mc13xxx_regulator` metadata.

## Control Flow
Generic regulator ops retrieve private state with `rdev_get_drvdata()`, index the chip descriptor by regulator ID, and call MC13xxx register read/modify/write helpers. OF helpers locate the parent MFD `regulators` child, count children, allocate init-data records, match child node names against descriptor names, and return a compact parsed list while updating `priv->num_regulators` to the parsed count.

## State And Persistence
The core does not own long-lived state beyond data stored by chip drivers in `mc13xxx_regulator_priv`. It reads and writes PMIC registers through the parent MFD. DT parse results are devm-managed and persist for the platform device lifetime.

## Dependencies And Integration Points
Depends on MC13xxx MFD APIs, OF regulator parsing, platform devices, exported GPL symbols, and regulator core helpers. Chip drivers include `mc13xxx.h` and use this file as their common implementation.

## Risks And Test Signals
Risks include `BUG_ON()` if a hardware selector exceeds table length, descriptor IDs not matching array indexes, OF child names silently skipped except for warnings, and fixed-voltage constraints rejecting valid board data if tables are wrong. Test through MC13783 and MC13892 probe paths, OF parsing with known and unknown children, selector read/write for every table-backed regulator, and module symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx-regulator-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx.h

## Purpose
Defines the private data structures, exported function declarations, and descriptor-construction macros shared by MC13xxx regulator drivers.

## Important APIs, Types, And Functions
`struct mc13xxx_regulator` combines a `struct regulator_desc` with enable and voltage selector register metadata. `struct mc13xxx_regulator_priv` stores the parent `struct mc13xxx`, POWERMISC power-gate state, descriptor table pointer, regulator count, and a flexible array of registered regulator devices. Macros `MC13xxx_DEFINE`, `MC13xxx_FIXED_DEFINE`, `MC13xxx_GPO_DEFINE`, `MC13xxx_DEFINE_SW`, and `MC13xxx_DEFINE_REGU` build indexed descriptor entries from per-chip register-token prefixes.

## Control Flow
The header has no runtime control flow. Its macros expand in MC13783/MC13892 sources to populate descriptor arrays with names, voltage tables, ops, IDs, register addresses, enable bits, selector shifts, and selector masks.

## State And Persistence
State shape is defined here but allocated by chip drivers. `powermisc_pwgt_state` exists to persist the logical state of inverted power-gate bits across POWERMISC read/modify/write cycles during the device lifetime.

## Dependencies And Integration Points
Depends on regulator driver types and platform-device declarations when OF helpers are enabled. It is the contract between the shared MC13xxx core and chip-specific tables.

## Risks And Test Signals
Risks are macro token-pasting mistakes, descriptor IDs diverging from array indexes, and flexible-array allocation size mismatches. Test by compiling both OF and non-OF configurations, checking generated descriptors for each chip, and verifying `struct_size(priv, regulators, num_regulators)` allocations match use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mc13xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mcp16502.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mcp16502.c

## Purpose
Implements the Microchip MCP16502 PMIC regulator driver for four buck regulators and two LDOs, including active, low-power, hibernate register banks and suspend GPIO transitions.

## Important APIs, Types, And Functions
`struct mcp16502` stores the optional `lpm` GPIO. Descriptor macro `MCP16502_REGULATOR()` builds per-rail `struct regulator_desc` entries with linear ranges, enable/vsel/ramp registers, and OF mode mapping. Important functions include `mcp16502_gpio_set_mode()`, `mcp16502_get_state_reg()`, `mcp16502_get_mode()`, `_mcp16502_set_mode()`, `mcp16502_get_status()`, `mcp16502_set_voltage_time_sel()`, suspend voltage/mode/enable helpers, `mcp16502_probe()`, and noirq suspend/resume callbacks.

## Control Flow
I2C probe creates an 8-bit regmap over registers `0x00..0x65`, obtains optional `lpm` GPIO low, registers all six regulators, and leaves the PMIC in active mode. Normal regulator operations use the Active register bank. Suspend callbacks choose LPM registers for standby and HIB registers for suspend-to-RAM style targets, then noirq suspend asserts the LPM GPIO and resume deasserts it. Buck mode operations toggle the FPWM/PFM bit; LDOs do not expose runtime mode switching.

## State And Persistence
The active/low-power/hibernate PMIC register banks persist in hardware until rewritten. Driver state is minimal: only the GPIO descriptor is stored. Suspend target selection depends on global `pm_suspend_target_state`.

## Dependencies And Integration Points
Depends on I2C, regmap, GPIO consumer API, regulator core, OF matching (`microchip,mcp16502`), and PM sleep infrastructure. Regulator descriptors use `regulators` DT node matching and support OF mode mapping for NORMAL and IDLE.

## Risks And Test Signals
Risks include incorrect target register selection for suspend states, absent or miswired LPM GPIO, ramp-time math based on selector deltas and ramp tables, status interpretation of FLT/ENS bits, and LDOs being configured with unsupported modes. Test by registering all six rails, changing voltages and ramp delays, toggling buck modes, reading fault/status bits, configuring suspend constraints, and measuring LPM GPIO level across standby and mem suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mcp16502.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mp5416.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mp5416.c

## Purpose
Implements an I2C/regmap regulator driver for MPS MP5416 and MP5496 PMICs, exposing four bucks and four LDOs.

## Important APIs, Types, And Functions
Descriptor macros `MP5416BUCK()` and `MP5416LDO()` define enable, voltage selector, current-limit, active-discharge, and ramp fields. `mp5416_regulators_desc[]` and `mp5496_regulators_desc[]` capture chip variants. Regulator ops are regmap generic helpers for enable, voltage, current limit, ramp delay, and active discharge. Probe is `mp5416_i2c_probe()`.

## Control Flow
Probe initializes an 8-bit regmap, selects the descriptor array from I2C/OF match data, configures `regulator_config` with device and regmap, then registers all eight regulators. Runtime control is almost entirely delegated to regulator-regmap helpers using descriptor register fields.

## State And Persistence
No private driver state is allocated. State is held in PMIC registers and the regulator core's registered devices. Active-discharge and ramp settings are hardware register bits.

## Dependencies And Integration Points
Depends on I2C, regmap, OF/I2C match data, and regulator core. DT compatible strings are `mps,mp5416` and `mps,mp5496`, with per-regulator nodes under `regulators`.

## Risks And Test Signals
Risks include wrong variant descriptor selection, current-limit mask mismatch in the shared ILIM register, MP5496 buck voltage range differences, and active-discharge bit placement. Test by probing both compatibles, listing and setting every buck/LDO voltage, setting current limits on bucks, verifying ramp register values, and checking active discharge bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mp5416.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mp8859.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mp8859.c

## Purpose
Provides a single-output regulator driver for the MPS MP8859 DCDC converter, including voltage programming, current limit, mode, active discharge, status, and error reporting.

## Important APIs, Types, And Functions
Key callbacks are `mp8859_set_voltage_sel()`, `mp8859_get_voltage_sel()`, `mp8859_set_voltage_time_sel()`, `mp8859_set_mode()`, `mp8859_get_mode()`, `mp8859_set_current_limit()`, `mp8859_get_status()`, and `mp8859_get_error_flags()`. `mp8859_readable()` and `mp8859_volatile()` constrain regmap caching. `mp8859_i2c_probe()` verifies manufacturer, device, revision, and ID registers before registration.

## Control Flow
Probe creates a cached regmap, reads MFR/DEV/revision/ID registers, validates MFR `0x9` and device `0x58`, logs the chip ID, then registers one regulator. Voltage setting writes low 3 selector bits, high 8 selector bits, then asserts the GO bit. Current limit is in 50 mA steps; if the status register says current limiting is active, the driver ramps the current-limit register stepwise instead of writing the final value directly.

## State And Persistence
The driver has no private data. Regmap uses MAPLE cache with GO/status/interrupt volatile. Hardware registers hold voltage, mode, current limit, discharge, and status state.

## Dependencies And Integration Points
Depends on I2C, regmap, OF/I2C matching (`mps,mp8859`), and regulator framework. The regulator is named `mp8859_dcdc` with `vin` supply.

## Risks And Test Signals
Risks include selector split/write ordering, GO bit volatility, current-limit ramp loop mistakes while limiting, error-flag construction accidentally mixing raw status bits with regulator error flags, and strict ID checks rejecting variants. Test by probing real hardware, sweeping voltage selectors, measuring ramp timing, toggling mode and discharge, injecting/observing PG/OTP/OTW/CC-CV status, and validating current limit changes under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mp8859.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mp886x.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mp886x.c

## Purpose
Implements the MPS MP8867/MP8869 single buck regulator driver with feedback-divider scaling, enable GPIO, switch-frequency configuration, mode control, voltage selection, and ramp delay.

## Important APIs, Types, And Functions
`struct mp886x_cfg_info` carries per-chip ops, slew-rate table, frequency table, and frequency register location. `struct mp886x_device_info` stores descriptor, init data, enable GPIO, match config, feedback resistor values, and current selector. Important functions are `mp886x_set_switch_freq()`, `mp886x_set_mode()`, `mp886x_get_mode()`, `mp8869_set_voltage_sel()`, `mp8869_get_voltage_sel()`, `mp8867_set_voltage_sel()`, `mp8867_get_voltage_sel()`, `mp886x_regulator_register()`, and `mp886x_i2c_probe()`.

## Control Flow
Probe requires regulator init data, reads `mps,fb-voltage-divider`, asserts the `enable` GPIO high, creates regmap, optionally sets `mps,switch-frequency-hz`, builds a runtime descriptor, registers the regulator, then caches the initial voltage selector. MP8869 writes GO before updating VSEL. MP8867 reuses that path but clears GO for small selector deltas. Get-voltage paths account for `V_BOOT` feedback-loop scaling using the DT resistor divider.

## State And Persistence
Driver state includes feedback resistors, chip config, enable GPIO, generated descriptor, and cached selector. Hardware registers hold enable, mode, slew, frequency, GO, V_BOOT, and VSEL bits.

## Dependencies And Integration Points
Depends on I2C, regmap, GPIO consumer API, OF regulator init parsing, and regulator core. Compatible strings are `mps,mp8867` and `mps,mp8869`; DT must provide an enable GPIO and feedback divider.

## Risks And Test Signals
Risks include missing DT properties causing probe failure, invalid switch-frequency values only logging an error, feedback-divider arithmetic affecting reported voltage, V_BOOT semantics differing between chips, and cached selector drift if hardware changes externally. Test by probing both variants, verifying voltage reports with divider values, sweeping selector changes across the MP8867 small-delta GO behavior, testing mode/ramp/frequency settings, and checking enable GPIO polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mp886x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mpq7920.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mpq7920.c

## Purpose
Implements the MPS MPQ7920 PMIC regulator driver for four bucks, RTC LDO, and four additional LDOs with voltage, current limit, active discharge, soft start, ramp, OVP, phase-delay, and switch-frequency controls.

## Important APIs, Types, And Functions
Descriptor macros `MPQ7920BUCK()` and `MPQ7920LDO()` build the static descriptor table. `struct mpq7920_regulator_info` stores regmap and mutable descriptor pointer for parse callbacks. Important functions are `mpq7920_set_ramp_delay()`, `mpq7920_parse_cb()`, `mpq7920_parse_dt()`, and `mpq7920_i2c_probe()`.

## Control Flow
Probe allocates driver info, initializes an 8-bit regmap, parses the top-level `regulators` node for switch frequency, then registers all nine regulators. Buck descriptors use an OF parse callback to process per-buck properties: disable OVP, set phase delay, and stash soft-start value. Generic regulator-regmap helpers handle enable, voltage, current, active discharge, and soft start based on descriptor fields. `ldortc` is intentionally always-on from the driver's perspective.

## State And Persistence
Driver state is the regmap pointer and descriptor table pointer. Per-regulator parse callbacks mutate descriptor soft-start values in the static table, so those values persist for the module lifetime. PMIC registers hold configured frequency, OVP, phase, soft-start, voltage, enable, current, and discharge state.

## Dependencies And Integration Points
Depends on I2C, regmap, OF regulator parsing, `mpq7920.h`, and regulator core. DT compatible is `mps,mpq7920`, with a top-level `regulators` child plus per-regulator properties such as `mps,buck-ovp-disable`, `mps,buck-phase-delay`, `mps,buck-softstart`, and `mps,switch-freq`.

## Risks And Test Signals
Risks include descriptor mutation in a static array, `MPQ7920_OVP_DISABLE` being a complemented constant used as an update value, silent parse failures for optional properties, LDO1 enable register set to zero, and register offset arithmetic for buck-specific callbacks. Test by probing with full DT properties, reading written CTL and buck C-register bits, sweeping buck/LDO voltages, checking current limits on supported rails, verifying RTC LDO behavior, and validating all optional DT properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mpq7920.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mpq7920.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/mpq7920.h

## Purpose
Defines MPQ7920 register addresses, bit masks, enable offsets, and voltage range constants consumed by `mpq7920.c`.

## Important APIs, Types, And Functions
The header provides no functions or types. It defines CTL registers, per-buck A/B/C/D registers, per-LDO A/B/C registers, mode and regulator-enable registers, masks for voltage reference, current limits, discharge, mode, soft start, switch frequency, phase delay, DVS slew rate, OVP, and voltage min/max/step constants.

## Control Flow
No runtime control flow. Constants are expanded into descriptor macros and parse callbacks in `mpq7920.c`.

## State And Persistence
No state is stored in the header. The constants describe hardware register state persisted in the PMIC.

## Dependencies And Integration Points
Depends on `BIT()` being available through includers. It is tightly coupled to `mpq7920.c` descriptor definitions and DT parse behavior.

## Risks And Test Signals
Risks are incorrect register addresses or masks propagating to every regulator operation, the misspelled `MPQ7920_MASK_BUCK_PHASE_DEALY` being part of the local API, and complemented `MPQ7920_OVP_DISABLE` requiring careful masked writes. Test by compiling the driver, comparing constants to the datasheet, and reading back each register programmed by descriptor fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mpq7920.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.c

## Purpose
Implements the MediaTek MT6311 I2C regulator driver for one VDVFS buck and one VBIASN LDO.

## Important APIs, Types, And Functions
`mt6311_regulators[]` defines a linear buck and enable-only LDO using `MT6311_BUCK()` and `MT6311_LDO()`. Buck ops use generic regmap voltage, enable, and transition-time helpers. LDO ops only expose enable, disable, and is_enabled. Probe is `mt6311_i2c_probe()`.

## Control Flow
Probe initializes an 8-bit regmap with MAPLE cache, reads `MT6311_SWCID`, accepts only E1/E2/E3 chip IDs, and registers both regulators with the shared regmap. All runtime operations are descriptor-driven by regulator-regmap helpers.

## State And Persistence
The driver does not allocate private state. Voltage and enable state lives in MT6311 registers. Regmap cache mirrors register values during the I2C device lifetime.

## Dependencies And Integration Points
Depends on I2C, regmap, regulator core, OF regulator support, `linux/regulator/mt6311.h`, and local register definitions in `mt6311-regulator.h`. OF compatible is `mediatek,mt6311-regulator`.

## Risks And Test Signals
Risks include unsupported chip ID handling, cache coherency for hardware-updated registers, LDO lacking voltage/status callbacks, and register/mask drift from the companion header. Test by probing all supported chip revisions, reading VDVFS voltage selector, setting voltage across the 600 mV to 1.39375 V range, toggling VDVFS and VBIASN, and validating DT regulator matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.h

## Purpose
Provides MT6311 local register addresses and bit masks used by the MT6311 regulator driver.

## Important APIs, Types, And Functions
The header defines SWCID, interrupt, VDVFS control, LDO control, frequency meter registers, interrupt masks, VDVFS enable/control/vosel masks, and VBIASN enable mask. It has no functions or structures.

## Control Flow
No runtime control flow. The C driver uses these constants to configure `struct regulator_desc` fields and validate chip ID through registers declared elsewhere.

## State And Persistence
No driver state exists here. The constants describe persistent PMIC register bits for buck voltage, buck enable, LDO enable, and status/interrupt controls.

## Dependencies And Integration Points
Included only by `mt6311-regulator.c`. It is coupled to `linux/regulator/mt6311.h` for regulator IDs and chip ID constants.

## Risks And Test Signals
Risks include incorrect masks for voltage and enable bits, stale register offsets, and missing definitions for new silicon revisions. Test through compile coverage and hardware read/write validation of VDVFS and VBIASN registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6315-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6315-regulator.c

## Purpose
Implements MediaTek MT6315 SPMI buck regulator support for four buck rails, including voltage control, enable, status, mode switching, and shutdown power-off sequencing.

## Important APIs, Types, And Functions
`struct mt6315_regulator_info` wraps descriptors with status and low-power mode metadata. `struct mt_regulator_init_data` stores per-buck mode-set masks that vary by SPMI USID. Key functions are `mt6315_map_mode()`, `mt6315_regulator_get_mode()`, `mt6315_regulator_set_mode()`, `mt6315_get_status()`, `mt6315_regulator_probe()`, and `mt6315_regulator_shutdown()`.

## Control Flow
SPMI probe creates a 16-bit-address regmap, allocates chip and mode data, chooses VBUCK1 mode-set masks based on `pdev->usid`, sets common one-bit masks for remaining bucks, then registers VBUCK1 through VBUCK4. Mode get checks force-PWM bits first, then low-power bits. Mode set writes force-PWM, clears force-PWM or low-power when returning normal, and sleeps briefly after leaving low-power. Shutdown unlocks protected TMA registers, enables a power-off sequence bit, then relocks.

## State And Persistence
Driver state includes the regmap in `struct mt6315_chip` and per-device mode masks in `mt_regulator_init_data`. Hardware registers persist voltage, enable, mode, and shutdown sequence configuration.

## Dependencies And Integration Points
Depends on SPMI, regmap, regulator core, OF match `mediatek,mt6315-regulator`, and public MT6315 regulator register/ID header. It integrates as an SPMI child device rather than an MFD platform subdevice.

## Risks And Test Signals
Risks include USID-specific mode masks, mode transition timing, shutdown protected-key sequence, lack of chip ID validation in this file, and global four-buck assumptions. Test by probing each USID role, changing all buck voltages, toggling FAST/NORMAL/IDLE modes, reading debug status registers, and validating shutdown sequence writes on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6315-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6316-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6316-regulator.c

## Purpose
Implements the MediaTek MT6316 SPMI regulator driver for 2-phase, 3-phase, and 4-phase buck configurations.

## Important APIs, Types, And Functions
`enum mt6316_type` selects phase topology from OF match data. `struct mt6316_regulator_info` wraps descriptors with debug, low-power, and mode-set register metadata. Important functions are 9-bit endian helpers `mt6316_be9_to_cpu()` and `mt6316_cpu_to_be9()`, set/clear enable callbacks, voltage selector bulk read/write callbacks, status/mode get/set callbacks, and `mt6316_regulator_probe()`.

## Control Flow
Probe initializes an SPMI regmap, performs an expected first chip-ID read to wake the PMIC, requires the second chip-ID read to succeed, selects the descriptor array for 2-phase (`vbuck12`, `vbuck34`), 3-phase (`vbuck124`, `vbuck3`), or 4-phase (`vbuck1234`) compatible, and registers each regulator. Enable and disable write to set/clear alias registers. Voltage selectors are 9-bit big-endian fields written with bulk I/O. Mode set manipulates force-PWM and low-power bits and delays after clearing low-power.

## State And Persistence
The driver stores no separate private allocation beyond descriptor pointer passed as regulator driver data. Hardware registers persist voltage, enable, status, and mode. The first-read wake behavior is transient SPMI/PMIC state.

## Dependencies And Integration Points
Depends on SPMI, regmap, regulator core, OF compatibles `mediatek,mt6316b-regulator`, `mediatek,mt6316c-regulator`, and `mediatek,mt6316d-regulator`. It uses `device_get_match_data()` to select topology.

## Risks And Test Signals
Risks include 9-bit selector byte order, set/clear enable register offsets, the intentionally ignored first chip-ID read, topology descriptor mismatch, and mode register errors being reported as regulator modes. Test by probing all three compatibles, reading/writing voltage selectors with known raw bytes, toggling enable through set/clear registers, switching FAST/NORMAL/IDLE modes, and checking debug QI status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6316-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6323-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6323-regulator.c

## Purpose
Provides the MT6323 platform regulator subdriver for the MT6397-family MFD core, registering bucks, table LDOs, and fixed LDOs.

## Important APIs, Types, And Functions
`struct mt6323_regulator_info` stores descriptor data plus QI status, alternate voltage selector registers, voltage-control register metadata, and LDO mode registers. Key functions are `mt6323_get_status()`, `mt6323_ldo_set_mode()`, `mt6323_ldo_get_mode()`, `mt6323_set_buck_vosel_reg()`, and `mt6323_regulator_probe()`.

## Control Flow
Probe receives the parent `mt6397_chip`, checks buck control registers to decide whether each buck should use normal `vosel` or active `voselon` register, reads and logs chip ID, then registers all MT6323 regulators. Buck regulators use linear ranges. LDOs use voltage tables or fixed voltages. LDO mode callbacks map NORMAL/STANDBY to one-bit low-power controls when the descriptor provides a mode register.

## State And Persistence
The static regulator table is mutated at probe when a buck's active selector register is selected. The parent regmap stores all hardware state. No additional private state is allocated per driver instance beyond passing each table entry as driver data.

## Dependencies And Integration Points
Depends on the MT6397 MFD parent, MT6323 register and regulator ID headers, platform driver infrastructure, regmap, and regulator core. The driver uses the parent device's regmap and platform ID `mt6323-regulator`.

## Risks And Test Signals
Risks include static descriptor mutation, incorrect buck control register selection, LDOs with no mode register returning errors if mode callbacks are invoked, and voltage table holes represented as zero. Test by probing under the parent MFD, validating selected `vsel_reg` for each buck, registering all regulators, checking QI-based status, setting LDO standby/normal modes where supported, and exercising voltage mapping for table holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6323-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6331-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6331-regulator.c

## Purpose
Implements MT6331 regulator registration for MT6397-family MFD systems, covering multiple DVFS bucks, fixed regulators, table LDOs, always-on LDOs, and status-register-backed LDO variants.

## Important APIs, Types, And Functions
`struct mt6331_regulator_info` extends descriptors with QI status bits, alternate buck selector registers, mode registers, and optional status registers. Important functions include `mt6331_get_status()`, `mt6331_ldo_set_mode()`, `mt6331_ldo_get_mode()`, `mt6331_set_buck_vosel_reg()`, and `mt6331_regulator_probe()`. Several ops tables distinguish range, table, no-mode, no-QI, always-on, and fixed regulators.

## Control Flow
Probe selects active buck selector registers based on hardware control bits, reads `MT6331_HWCID`, rejects chip ID `0x10` because its voltage tables differ, and registers every descriptor using the parent MFD regmap. LDO mode callbacks write normal/low-power mode fields. Always-on regulators expose voltage operations without enable control. Status for most regulators is QI-based; some special LDOs carry separate status register metadata but the no-QI ops do not currently call `mt6331_get_status()`.

## State And Persistence
The static descriptor table is mutated at probe for active buck VSEL registers. Parent PMIC registers persist enable, status, voltage, and mode state. No dynamic private state beyond regulator device registrations.

## Dependencies And Integration Points
Depends on MT6397 core, MT6331 register and regulator ID headers, platform devices, regmap, and regulator framework. The platform device ID is `mt6331-regulator`.

## Risks And Test Signals
Risks include unsupported E1 chip overvoltage if the ID check regresses, static descriptor mutation across instances, status behavior divergence for `LDO_S` no-QI descriptors, mode masks of zero in no-mode ops, and zero entries in voltage tables. Test by forcing supported and E1 HWCID reads, checking each buck's selected VSEL register, registering all regulators, setting voltage/mode across all LDO categories, and verifying status for QI and status-register rails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6331-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6332-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6332-regulator.c

## Purpose
Provides MT6332 regulator support for MT6397-family MFD systems, including bucks, boost, linear LDO, table LDOs, always-on LDO, and fixed regulators.

## Important APIs, Types, And Functions
`struct mt6332_regulator_info` mirrors MT6331-style metadata: QI bits, alternate selector registers, mode registers, and optional status registers. Key callbacks are `mt6332_get_status()`, `mt6332_ldo_set_mode()`, `mt6332_ldo_get_mode()`, `mt6332_set_buck_vosel_reg()`, and `mt6332_regulator_probe()`. Ops tables cover buck linear ranges, LDO linear ranges, voltage tables, always-on tables, and fixed regulators.

## Control Flow
Probe selects each buck/LDO linear regulator's active voltage selector register based on control bits, reads and masks `MT6332_HWCID`, rejects chip ID `0x10` for unsupported E1 voltage tables, and registers every descriptor. Status uses QI when present and falls back to descriptor status register/mask otherwise. LDO mode callbacks map NORMAL/STANDBY to low-power mode bits.

## State And Persistence
The static descriptor table can be modified at probe by switching `desc.vsel_reg` to `vselon_reg`. Hardware state is held in parent PMIC registers. No extra dynamic per-device state is kept.

## Dependencies And Integration Points
Depends on MT6397 MFD core, MT6332 register and regulator ID headers, platform driver matching, regmap, and regulator framework. Platform ID is `mt6332-regulator`.

## Risks And Test Signals
Risks include E1 voltage-table incompatibility, active selector register selection, mixed QI/status status paths, mode ops on descriptors with invalid masks, and boost/buck voltage range limits. Test by HWCID gating, register selection checks, voltage sweeps for buck/boost/LDO ranges, mode toggles on mode-capable LDOs, and status readback for fixed regulators using `MT6332_EN_STATUS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6332-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6357-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6357-regulator.c

## Purpose
Implements MT6357 regulator registration for the MT6397-family PMIC core, covering bucks, selectable LDOs, SRAM LDOs with monitor selectors, and fixed LDOs.

## Important APIs, Types, And Functions
`struct mt6357_regulator_info` wraps descriptors with DA voltage monitor register and mask. Descriptor macros define buck, table LDO, linear SRAM LDO, and fixed regulator entries. The main custom callback is `mt6357_get_buck_voltage_sel()`, shared by buck/range/fixed ops where DA monitor readback is needed. Probe is `mt6357_regulator_probe()`.

## Control Flow
Probe inherits the parent OF node, iterates the static regulator table, passes each entry as driver data, and registers all regulators against the parent regmap. Voltage set uses normal descriptor VSEL registers, while get-voltage for bucks and linear SRAM LDOs reads DA debug registers to report actual hardware-selected values.

## State And Persistence
The driver uses a static descriptor table and no per-device allocation. Hardware register values and parent regmap hold regulator state. No static table mutation is performed.

## Dependencies And Integration Points
Depends on MT6397 core, MT6357 register and regulator headers, platform devices, regmap, OF regulator matching, and regulator core. Platform ID is `mt6357-regulator`.

## Risks And Test Signals
Risks include voltage table holes, DA monitor mask/shift mistakes, fixed regulators exposing calibrated selector behavior inconsistently, and assuming parent regmap readiness. Test by registering all MT6357 regulators, reading DA selectors after voltage changes, checking fixed LDO enables, validating table voltage mapping with zero entries, and confirming child regulator DT names match descriptor `of_match` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6357-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6358-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6358-regulator.c

## Purpose
Implements MT6358 and MT6366 regulator support for MT6397-family PMIC devices, including bucks, pickable-range LDOs, linear SRAM LDOs, fixed calibrated LDOs, buck modes, status readback, and VCN33 enable-bit synchronization.

## Important APIs, Types, And Functions
`struct mt6358_regulator_info` stores descriptor, status/QI, DA selector, and mode-register metadata. Descriptor macros define MT6358 and MT6366 buck/LDO/fixed variants. Important functions include `mt6358_map_mode()`, `mt6358_get_buck_voltage_sel()`, `mt6358_get_status()`, `mt6358_regulator_set_mode()`, `mt6358_regulator_get_mode()`, `mt6358_sync_vcn33_setting()`, and `mt6358_regulator_probe()`.

## Control Flow
Probe selects the MT6358 or MT6366 descriptor table based on the parent `mt6397->chip_id`, synchronizes VCN33 WiFi enable state into the BT enable bit and disables the duplicate WiFi bit, then registers every regulator. Buck mode operations map AUTO to NORMAL and FORCE_PWM to FAST through mode registers. Buck and linear/fixed get-voltage paths read DA monitor selectors; pickable LDOs use regulator core pickable range helpers with selector bitfields.

## State And Persistence
Regulator descriptors are static const tables; runtime state is in parent PMIC registers. `mt6358_sync_vcn33_setting()` intentionally changes hardware enable bits at probe to collapse two controls into one logical regulator. No private state is allocated.

## Dependencies And Integration Points
Depends on MT6397 core, MT6358 register and regulator headers, MT6397 regulator DT binding constants, platform devices, regmap, and regulator framework. Platform ID is `mt6358-regulator`; supported parent chip IDs are MT6358 and MT6366.

## Risks And Test Signals
Risks include chip-ID table mismatch, VCN33 sync changing bootloader state, DA monitor masks, pickable range selector arrays, fixed LDO calibration semantics, and mode mapping that only supports NORMAL/FAST. Test by probing both chip IDs, validating VCN33 sync read/write effects, registering every regulator, sweeping buck and LDO voltages, checking status registers, toggling buck FAST/NORMAL modes, and verifying MT6366-specific selector ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6358-regulator.c -->
