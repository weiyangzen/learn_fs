# subset-b-005187 regulator driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ti-abb-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/ti-abb-regulator.c

Purpose: TI SoC Adaptive Body Bias regulator driver for ABB LDO blocks. It presents body-bias operating points as regulator voltage selectors so OPP code can move between nominal, forward body bias, and reverse body bias modes.

Important APIs/types/functions: `struct ti_abb`, `struct ti_abb_info`, and `struct ti_abb_reg` hold mapped MMIO, per-voltage ABB mode data, masks, clock/timing data, and optional efuse/LDOVBB override resources. Regulator operations are `regulator_list_voltage_table`, `ti_abb_set_voltage_sel`, and `ti_abb_get_voltage_sel`. Hardware sequencing lives in `ti_abb_set_opp`, with helpers for read-modify-write, transaction-done polling/clearing, and LDOVBB override programming. Probe selects register layout from `ti_abb_of_match` and registers one always-on voltage regulator.

Control flow: probe maps base/control/setup, shared interrupt status, optional efuse and LDO override registers, reads timing and ABB table properties, programs SR2 wait count from clock rate, registers the regulator, then enables the ABB LDO. Voltage changes validate selector bounds, avoid redundant transitions, optionally fold efuse recommendations into ABB mode/vset, clear stale transaction bits, program FBB/RBB and OPP selection, apply LDOVBB override in mode-dependent order, trigger `opp_change`, wait for transaction completion, and update `current_info_idx`.

State and persistence: persistent hardware state is in MMIO control/setup/LDOVBB registers and shared interrupt status. Driver state caches the current selector, but starts at `-EINVAL` because bootloader bias state is unknown. DT tables and efuse data define the supported selector-to-bias mapping.

Dependencies and integration points: platform device, OF properties/resources, clock framework, regulator core, MMIO accessors, and OPP/regulator consumers. The interrupt-status resource may be shared, so it is mapped without exclusive resource reservation.

Risks: transition sequencing is hardware sensitive; LDOVBB override ordering is explicitly required to avoid VBB glitches. Missing or zero DT timing/mask properties fail probe. Poll loops depend on `ti,settling-time`; bad values can cause false timeouts. Shared interrupt status clearing must not disturb other ABB users beyond the documented mask.

Test signals: boot probe with all compatible layouts, DT validation for `ti,abb_info`, efuse and no-efuse paths, voltage selector changes across all ABB modes, timeout injection for transaction done, and OPP transitions that verify no redundant writes when two selectors map to identical ABB data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ti-abb-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps51632-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps51632-regulator.c

Purpose: I2C regulator driver for the TI TPS51632 D-CAP step-down controller with serial VID and optional PWM DVFS operation.

Important APIs/types/functions: `struct tps51632_chip` owns the regulator descriptor, regmap, and registered rdev. `tps51632_dcdc_ops` uses generic regmap selector helpers plus `tps51632_dcdc_set_ramp_delay`. `tps51632_init_dcdc` programs base voltage, optional 20 mV DVFS step mode, VMAX, and DVFS control. Regmap access rules mark offset/fault/current-monitor registers volatile and restrict writes to supported control registers.

Control flow: probe builds a single voltage descriptor, obtains platform data or OF-derived init data, validates PWM DVFS base/max voltages, chooses either `VOLTAGE_BASE_REG` or `VOLTAGE_SELECT_REG` as the selector register, initializes regmap, initializes chip DVFS configuration, and registers one regulator. If VMAX is requested, the driver reads the VMAX lock bit and writes only if the register has not already been locked by prior boot firmware or a previous write.

State and persistence: register state persists in the controller. The driver does not maintain runtime selector state beyond regmap cache and descriptor fields. VMAX is hardware one-time writable until power reset, so boot order matters.

Dependencies and integration points: I2C, regmap, regulator core, OF regulator init data, legacy `tps51632_regulator_platform_data`, and `subsys_initcall` registration.

Risks: ramp delay maps directly to a bit position via `DIV_ROUND_UP(ramp_delay, 6000) - 1`; unusually high values may select undefined bits unless constrained by callers. VMAX lock behavior can surprise tests or repeated probes. OF data is required when platform data is absent.

Test signals: probe from DT and platform data, PWM DVFS enabled/disabled, invalid voltage constraints, VMAX locked/unlocked behavior, ramp delay writes, and regmap read/write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps51632-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6105x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps6105x-regulator.c

Purpose: Platform child driver for the TPS61050/TPS61052 MFD boost converter when the chip is configured as a voltage regulator rather than LED/flash mode.

Important APIs/types/functions: `tps6105x_regulator_desc` describes a single boost regulator with four voltage table entries and regmap-backed enable, disable, is-enabled, get/set selector, and list-voltage operations. `tps6105x_regulator_probe` consumes the parent MFD platform data and regmap.

Control flow: probe gets the parent `struct tps6105x` from platform data, checks `pdata->mode`, returns success without registering anything unless the mode is `TPS6105X_MODE_VOLTAGE`, builds a regulator config using the parent I2C device, init data, OF node, and regmap, then registers one regulator.

State and persistence: all state is in the parent regmap, especially `TPS6105X_REG_0` mode and voltage fields. The driver keeps no private cache except the parent `tps6105x->regulator` pointer.

Dependencies and integration points: depends on the TPS6105x MFD core for I2C/regmap ownership and platform data. Regulator consumers see `tps6105x-boost`; OF matching uses child name `regulator`.

Risks: probe assumes parent platform data and `tps6105x->pdata` are valid. Returning success when not in voltage mode is intentional but means no regulator appears. The voltage table contains two 5 V selectors, so selector-specific tests should not assume voltage uniqueness.

Test signals: MFD mode gating, successful regulator registration in voltage mode, enable/mode bit programming, selector round trips for duplicate 5 V entries, and missing parent-data failure coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6105x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps62360-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps62360-regulator.c

Purpose: I2C regulator driver for TPS62360/361/362/363 processor-core buck regulators with optional GPIO-controlled VSET register selection.

Important APIs/types/functions: `struct tps62360_chip` stores regmap, descriptor, VSEL GPIOs, current VSET register, LRU table, voltage mask, and shutdown options. Core operations include custom get/set voltage selector, force-PWM set/get mode, generic linear list/map/time helpers, and `tps62360_shutdown` for output discharge. `find_voltage_set_register` implements the four-entry VSET LRU cache.

Control flow: probe identifies the chip from OF or I2C ID, parses platform/OF settings, configures voltage range/mask by chip variant, initializes regmap, obtains optional `vsel0` and `vsel1` GPIOs, initializes VSET LRU state, programs control/ramp defaults, derives ramp delay from `REG_RAMPCTRL`, then registers one buck regulator. Voltage setting either updates the current register or reuses a cached selector and switches GPIOs to select the requested VSET slot.

State and persistence: hardware registers persist selected voltages, force-PWM bits, ramp config, and discharge setting. Driver state tracks current VSET ID and per-slot selector values; this must stay synchronized with GPIO state.

Dependencies and integration points: I2C, OF/platform data, GPIO descriptors, regmap, regulator core, and shutdown callback.

Risks: the LRU cache is only valid when both VSEL GPIOs are present; partial GPIO availability falls back to one VSET register. `tps62360_shutdown` enables output discharge only if configured. Error log in regulator registration prints `id->name`, but `id` can be null for pure OF probe.

Test signals: all chip IDs, GPIO and no-GPIO selector changes, LRU reuse, force-PWM across all VSET registers, ramp-delay derivation, and shutdown discharge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps62360-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6286x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps6286x-regulator.c

Purpose: Compact I2C regulator driver for TI TPS62864/866/868/869 buck converters.

Important APIs/types/functions: a single `regulator_desc` named `tps6286x` exposes SW under the `regulators` node. It uses regmap helpers for enable, disable, is-enabled, voltage selector access, and linear voltage listing. `tps6286x_set_mode`, `tps6286x_get_mode`, and `tps6286x_of_map_mode` map regulator fast mode to the FPWM bit and DT binding mode constants.

Control flow: probe initializes an 8-bit regmap with STATUS marked volatile, fills a minimal regulator config with OF node and regmap, and registers the single regulator. Runtime control is direct regmap bit manipulation in `CONTROL` for SW enable and FPWM, and selector updates in `VOUT1`.

State and persistence: no private state; hardware registers and regmap cache hold enable, mode, and voltage. STATUS is volatile and therefore not cached.

Dependencies and integration points: I2C, OF match table, dt-bindings for TPS62864 modes, regmap, and regulator framework.

Risks: `get_mode` returns 0 on regmap read failure, which is not a normal regulator mode and can hide bus errors from consumers. The descriptor is shared across all compatibles and assumes identical voltage range and control layout.

Test signals: probe for each compatible string, DT mode mapping, enable/disable bit state, voltage selector min/max, FPWM toggling, and simulated regmap read failure for mode reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6286x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6287x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps6287x-regulator.c

Purpose: I2C regulator driver for TPS62870/871/872/873 PMIC buck regulators with pickable voltage ranges and programmable ramp rates.

Important APIs/types/functions: `tps6287x_reg` defines a single regulator using pickable linear ranges across four VRANGE settings, VSET as selector, CTRL2 as range selector, CTRL1 for enable/FPWM/ramp, and `range_applied_by_vsel`. `struct tps6287x_reg_data` stores an optional best range selected from init constraints. Custom functions implement best-range selection, mode mapping, and range-aware `map_voltage`.

Control flow: probe allocates `reg_data`, initializes regmap, reads OF regulator init data, chooses a best fixed range if constraints have `apply_uV` and fit in one range, registers the regulator, and stores `reg_data` on `rdev`. Voltage mapping uses the chosen range when available to avoid regulator-core picking a different range; otherwise it falls back to generic pickable range mapping.

State and persistence: persistent state is in VSET, CTRL1, and CTRL2. Driver state only records preferred range for voltage mapping. STATUS is volatile.

Dependencies and integration points: I2C, regmap, regulator core pickable linear range helpers, OF init constraints, and standard regulator mode constants.

Risks: `rdev->reg_data` is assigned after registration; callbacks during registration must not depend on it. If constraints are missing or not `apply_uV`, generic range picking may choose any valid range. `get_mode` masks read errors by returning 0.

Test signals: fixed-range and generic mapping paths, voltage mapping boundary checks, ramp-delay table programming, FPWM mode toggling, and compatibles for all four device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6287x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65023-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65023-regulator.c

Purpose: I2C regulator driver for TPS65020/TPS65021/TPS65023 PMICs with three DCDC regulators and two LDOs.

Important APIs/types/functions: `struct tps_pmic` holds registered rdevs, chip-specific descriptor data, and regmap. `struct tps_driver_data` selects descriptor arrays and identifies the adjustable core DCDC. Macros build DCDC and LDO descriptors from voltage tables. DCDC ops restrict voltage changes to the chip-specific core regulator; LDO ops use generic regmap selector helpers.

Control flow: probe allocates PMIC state, chooses driver data from I2C ID, initializes regmap, registers five regulators using optional platform init data array, stores client data, then clears `CORE_ADJ` so output voltage is controlled through I2C. Non-core DCDCs report selector 0 and reject set-voltage requests because they are fixed rails on those variants.

State and persistence: register state lives in the PMIC; the driver keeps descriptor selection and rdev pointers. Voltage changes for DCDC use `DEF_CORE` plus the GO bit in `CON_CTRL2`; enables use `REG_CTRL`.

Dependencies and integration points: I2C, regmap, regulator core, OF/I2C device IDs, and optional legacy platform init data.

Risks: OF match data exists but probe uses `i2c_client_get_device_id()` driver data, so ID table matching must be correct for OF-created clients. `regmap_update_bits` enabling I2C adjustment is not checked. Platform init data is indexed by regulator order.

Test signals: each chip variant, core vs fixed DCDC set-voltage behavior, GO-bit application, LDO selector masks, init-data indexing, and error injection in registration/regmap init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65023-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6507x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps6507x-regulator.c

Purpose: Platform child regulator driver for the TPS6507x MFD, registering three DCDC regulators and two LDOs.

Important APIs/types/functions: `struct tps6507x_pmic` contains per-regulator descriptors, parent MFD pointer, per-rail `tps_info`, and an I/O mutex. Helpers wrap parent `read_dev`/`write_dev` and provide locked set/clear/read/write operations. Regulator ops manually implement enable, disable, is-enabled, get/set selector, and table listing.

Control flow: probe obtains the parent MFD and optional board init data, allocates PMIC state, initializes a mutex, builds five descriptors from `tps6507x_pmic_regs`, applies platform or OF `ti,defdcdc_default` selection for DCDC2/DCDC3 high/low default registers, and registers each regulator. Runtime ops compute register and mask by regulator ID, use `CON_CTRL1` enable bits, and write voltage selectors into the appropriate DCDC/LDO register.

State and persistence: state is in parent MFD registers. Driver state stores `defdcdc_default` choices and serializes register access with `io_lock`. The parent stores `tps6507x_dev->pmic`.

Dependencies and integration points: TPS6507x MFD callbacks, platform driver model, regulator core, OF regulator parsing, and legacy board data.

Risks: manual RMW must remain locked to avoid lost updates. `config.init_data = init_data` is not indexed in the loop, so legacy platform init data handling should be reviewed against regulator-core expectations. Selector values are ORed without shifting because masks are low-aligned for used fields.

Test signals: enable bit mapping, DCDC2/DCDC3 high-vs-low selection, OF parse callback, concurrent set/enable operations, and parent read/write failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6507x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65086-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65086-regulator.c

Purpose: Platform child regulator driver for TPS65086/TPS650864x PMIC families, registering bucks, LDOs, VTT, and load switches according to chip ID.

Important APIs/types/functions: `struct tps65086_regulator` wraps a `regulator_desc` plus decay register/mask. `struct tps65086_regulator_config` selects a per-chip descriptor array. `reg_ops` handles voltage regulators through linear ranges and regmap helpers; `switch_ops` handles load switches. `tps65086_of_parse_cb` applies DT options for 25 mV buck step size and decay mode.

Control flow: probe reads parent `struct tps65086`, maps parent chip ID to a descriptor array, stores it in `tps->reg_config`, prepares a regulator config with parent OF node and regmap, and registers every descriptor. During OF parsing, buck descriptors can have their linear range table replaced in-place for 25 mV mode; decay mode writes chip-specific decay bits.

State and persistence: descriptor arrays are static and mutated at parse time for step-size selection, so state can persist across probes in the same kernel image. Hardware state is in parent regmap enable, voltage, and decay registers.

Dependencies and integration points: TPS65086 MFD, platform device IDs, OF regulator child nodes, regmap, and regulator core.

Risks: static descriptor mutation can leak one board’s 25 mV selection into later instances if multiple devices differ. Unknown chip IDs fail probe. Decay writes happen during parse and can fail registration. Some variants omit SWB2 or use different enable registers.

Test signals: all chip IDs, 10 mV and 25 mV buck ranges, decay property success/failure, variant-specific regulator counts, switch enable bits, and multiple-instance descriptor mutation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65086-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65090-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65090-regulator.c

Purpose: Platform child regulator driver for TPS65090 PMIC rails, including fixed DCDCs, FET switches, and fixed LDO rails.

Important APIs/types/functions: `struct tps65090_regulator` stores per-rail descriptor, rdev, and FET overcurrent wait settings. Descriptor macros define 12 rails. FET enable uses `tps65090_fet_enable`, which retries `tps65090_try_enable_fet` up to 1000 times and checks timeout/power-good bits. DT parsing supports external DCDC control GPIOs and `ti,overcurrent-wait`.

Control flow: probe gets parent MFD data and platform/DT regulator data, allocates per-rail state, optionally configures DCDC external control, registers each regulator with parent regmap and optional OF node, applies overcurrent wait, and enables external control when requested. For FETs, enable sets control bits, polls timeout status, requires power-good, and retries by disabling/re-enabling on recoverable failures.

State and persistence: hardware enable/control bits persist in the MFD regmap. Driver state keeps overcurrent wait values and external-control mode. GPIO descriptors for external control are handed over to the regulator core with `devm_gpiod_unhinge`.

Dependencies and integration points: TPS65090 MFD helpers/regmap, OF regulator matching, GPIO descriptors, regulator core, and platform data.

Risks: FET enable can spin for many attempts and intentionally `WARN_ON(1)` on final failure. External-control ops are empty because GPIO enable is delegated to the core, so descriptor ops change based on DT. Missing regulator node or platform data fails probe.

Test signals: FET retry success/failure, overcurrent wait bounds, external-control GPIO handoff, always-on/boot-on behavior when disabling external control, and DT parsing for every rail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65090-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65132-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65132-regulator.c

Purpose: I2C regulator driver for TPS65132 positive and negative display bias supplies.

Important APIs/types/functions: `struct tps65132_regulator` owns per-device state; `struct tps65132_reg_pdata` stores optional enable and active-discharge GPIOs, discharge duration, and cached enable GPIO state. Two descriptors expose `outp` and `outn` with linear 4.0 V to 6.0 V selectors, regmap active discharge, and custom GPIO-aware enable/disable/is-enabled operations.

Control flow: probe allocates state, creates a no-cache regmap with inaccessible register ranges, and registers two regulators. Each regulator’s OF parse callback optionally obtains an enable GPIO and an active-discharge GPIO. Enable asserts the GPIO and, if constraints request active discharge disabled, clears the hardware discharge bit. Disable deasserts enable and pulses active-discharge GPIO for the configured time.

State and persistence: voltage and active-discharge bits live in I2C registers. Enable state is cached only when an enable GPIO is available; without it `is_enabled` reports true because the driver has no readable enable bit. Active discharge timing is per-regulator DT state.

Dependencies and integration points: I2C, regmap access tables, GPIO descriptors, OF regulator child nodes, and regulator constraints.

Risks: missing optional GPIOs are ignored except deferred probe, so boards without enable GPIOs cannot observe actual enabled state. If active-discharge GPIO is present, `ti,active-discharge-time-us` is mandatory. `TPS65132_REG_CONTROL` is `0x0FF` while reg bits are 8, a value worth checking against regmap expectations.

Test signals: both regulators with and without GPIOs, deferred GPIO probe, active-discharge pulse timing, voltage selector boundaries, inaccessible register filtering, and active-discharge constraint handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65132-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65185.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65185.c

Purpose: I2C driver for TPS65185 e-paper/display power management, exposing regulators for `v3p3`, `vposneg`, and `vcom`, plus optional hwmon temperature reporting.

Important APIs/types/functions: `struct tps65185_data` holds regmap, power-good/power-up/wakeup/VCOM GPIOs, completions, and IRQ numbers. Regulator ops cover regmap-backed `v3p3`, power-good-gated `vposneg`, reversed selector mapping for positive/negative rails, and split-register `vcom` voltage programming. `tps65185_hwmon_read` starts temperature acquisition and waits for completion.

Control flow: probe initializes regmap, requires power-good GPIO and IRQ, obtains optional control GPIOs, enables `vin`, initializes completions, requests PGOOD and optional chip IRQs, enables temperature interrupt, registers two main regulators and VCOM with optional enable GPIO, and registers hwmon when available. `vposneg_enable` asserts PWRUP or ACTIVE, waits for PGOOD completion, then verifies GPIO state.

State and persistence: hardware registers hold enable, voltage, interrupt, and temperature state. Completions synchronize IRQs with enable and temperature-read paths. VCOM enable may be controlled by a GPIO passed to the regulator core.

Dependencies and integration points: I2C, regmap, GPIO, IRQs, regulator consumer/core APIs, `vin` supply, hwmon, completions, and optional PM/runtime-related headers.

Risks: `tps65185_hwmon_read` does not check the return from the initial update/read of TMST1 before testing conversion bits. PGOOD timeout is fixed at 200 ms. `vposneg_disable` sets STANDBY but does not clear ACTIVE in the register path. IRQ availability and GPIO polarity are board-critical.

Test signals: PGOOD IRQ completion and timeout, GPIO and register enable paths, reversed VADJ selector mapping, VCOM high bit handling, temperature conversion interrupt, hwmon registration failure tolerance, and regulator dependency from VCOM to `vposneg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65185.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65217-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65217-regulator.c

Purpose: Platform child regulator driver for TPS65217 PMIC DCDC1-3 and LDO1-4 rails.

Important APIs/types/functions: descriptor macro `TPS65217_REGULATOR` defines voltage tables/ranges, enable masks, selector registers, and suspend bypass/strobe registers. Custom ops wrap TPS65217 password-protected set/clear helpers for enable, disable, set voltage, and suspend sequencing. LDO1 uses a table; other adjustable regulators use linear ranges.

Control flow: probe obtains parent MFD and optional board data, allocates `tps->strobes`, registers all regulators with parent regmap and driver data, reads each bypass register, and stores default strobe bits. Voltage setting writes protected selector bits and sets the GO bit for DCDC1-3. Suspend disable restores stored strobe sequencing, while suspend enable clears the bypass mask.

State and persistence: voltage/enable/suspend bits live in parent registers. Driver stores initial strobe values so suspend operations can restore board sequencing. All writes use PMIC protection levels.

Dependencies and integration points: TPS65217 MFD, regmap, regulator core, OF descriptor matching, and legacy board init data.

Risks: protected writes must use the correct level; selector writes for DCDCs require GO bit or voltage may not transition. If stored strobe is zero, suspend-disable returns `-EINVAL`. The probe reads bypass registers even for every descriptor, so invalid bypass metadata would break registration.

Test signals: protected enable/disable paths, DCDC GO bit, LDO1 table vs linear regulators, suspend enable/disable with stored strobes, and parent regmap read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65217-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65218-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65218-regulator.c

Purpose: Platform child regulator driver for TPS65218 PMIC voltage rails and LS2/LS3 current-limited load switches.

Important APIs/types/functions: `TPS65218_REGULATOR` builds descriptors with voltage selector, enable, current-limit, suspend bypass, ramp, and fixed-voltage metadata. Ops are split for DCDC1/2, DCDC3/4/LDO1, LS2/LS3 current regulators, and fixed DCDC5/6. Custom helpers perform protected enable/disable, voltage changes with GO bit, suspend sequencing, and current limit selection.

Control flow: probe prepares config from parent MFD, allocates `tps->strobes`, registers all descriptors, reads each bypass register, and stores default strobe bits. Voltage setting writes protected VSEL and triggers slew GO for DCDC1/2. Current limit ops choose exact input limit or largest supported value within requested min/max. Suspend disable preserves DCDC3 on revision 2.1 and applies a fallback strobe for DCDC3 when absent.

State and persistence: hardware registers store voltage, enable, current limit, and sequence bits. Driver stores original strobe fields on the parent object.

Dependencies and integration points: TPS65218 MFD, regmap, regulator core, OF matching through descriptor names, protected register helper API, and platform device IDs.

Risks: descriptors for current regulators have zero/unused voltage fields and must only use current ops. Revision-specific DCDC3 behavior prevents poweroff reboot issues and should not regress. Reading bypass register 0 for LS descriptors relies on harmless regmap behavior.

Test signals: DCDC1/2 voltage GO, revision 2.1 DCDC3 suspend behavior, current limit exact/range selection, fixed DCDC5/6 enable-only operation, and strobe restore error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65218-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65219-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65219-regulator.c

Purpose: Platform child regulator driver for TPS65214/TPS65215/TPS65219 PMIC families, covering common buck rails, variant LDO rails, bypass-capable LDOs, standby mode, and regulator fault IRQ notifications.

Important APIs/types/functions: `struct tps65219_chip_data` selects common and variant regulator descriptors plus common and variant IRQ type tables. `TPS65219_REGULATOR` builds descriptors with voltage/current fields, enable masks, linear ranges, ramp delays, and bypass masks. Ops use generic regmap helpers plus custom standby-mode set/get. `tps65219_regulator_irq_handler` maps named platform IRQs to regulator notifier events.

Control flow: probe chooses chip data from platform ID, registers common bucks, registers variant LDOs, then requests every named common and variant IRQ. Runtime mode writes `STBY_1_CONFIG` bits; voltage and bypass use regmap helpers. IRQ handler reports timeout globally or calls `regulator_notifier_call_chain` for rail-specific overcurrent, undervoltage, residual-voltage, short-circuit, and thermal events.

State and persistence: state is in parent regmap. IRQ data is devm-allocated per IRQ and stores the event type, but the current code does not populate `irq_data->rdev`, so notifier delivery has a null regulator device for rail-specific events.

Dependencies and integration points: TPS65219 MFD, platform IRQ resources by name, regulator core/notifier API, regmap, OF regulator nodes, and platform device IDs for chip variants.

Risks: all listed IRQ names are mandatory; missing one aborts probe. `tps65219_get_mode` appears to return STANDBY when the bit is set despite `set_mode(NORMAL)` setting the bit, suggesting inverted semantics. Null `rdev` in IRQ data is a likely notifier bug.

Test signals: all three chip IDs, regulator count/ranges per variant, standby mode round trips, bypass for LDO1/2, complete IRQ resource tables, and notifier behavior with real rdev association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65219-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6524x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps6524x-regulator.c

Purpose: SPI regulator driver for TPS6524x PMICs, exposing three DCDCs, two LDOs, USB switch, and LCD switch.

Important APIs/types/functions: `struct tps6524x` owns SPI device, mutex, and generated descriptors. `struct supply_info` describes each rail’s voltage table, current-limit table, enable field, voltage field, and current-limit field. Low-level SPI helpers perform nonstandard 12/16/4-bit read/write transactions and status validation. Regulator ops manually implement enable, disable, is-enabled, voltage selector, and current limit.

Control flow: probe requires an array of platform `regulator_init_data`, allocates state, initializes mutex, creates descriptors from `supply_info`, and registers seven regulators. Writes go through `rmw_protect`, which sets write-enable, performs a locked RMW, then clears write-enable. Voltage/current ops validate fixed rails and selector bounds before writing encoded fields.

State and persistence: all rail state is in PMIC SPI registers. Driver state is descriptor metadata and lock only. Write-enable is explicitly toggled around protected updates.

Dependencies and integration points: SPI core, regulator framework, platform data, and PMIC-specific SPI framing/status bits. There is no OF parser in this file.

Risks: no regulator can probe without platform data. SPI transaction bit widths are unusual and controller-dependent. `rmw_protect` may leave write-enable set if the protected RMW fails before the final clear. Fixed rails reject set-voltage/current-limit requests.

Test signals: SPI status error decoding, write-enable set/clear sequencing under failures, all rail voltage/current tables, fixed rail behavior, mutex serialization, and platform-data array ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6524x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6586x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps6586x-regulator.c

Purpose: Platform child regulator driver for TPS6586x PMIC variants, registering SYS, SM, and LDO regulators with variant-specific voltage tables.

Important APIs/types/functions: `struct tps6586x_regulator` wraps a descriptor plus two possible enable bit locations. Macros define table-based, linear, fixed, DVM, and SYS regulators. `find_regulator_info` overlays variant-specific descriptors on the base table. `tps6586x_regulator_preinit` normalizes dual enable-bit state so the driver controls one bit. DT parsing maps regulator child names to IDs and patches SYS supply names for LDO5/LDO_RTC.

Control flow: probe gets platform data or parses DT, identifies parent PMIC version, loops all regulator IDs, finds descriptor info, preinitializes enable bits, registers each regulator with optional OF node, and applies board slew-rate settings for SM0/SM1. Version-specific tables override SM2/LDO voltage data for TPS658623/624/640/643 variants.

State and persistence: hardware enable and voltage state lives in the parent MFD. Driver state is static descriptor tables and parent platform data. Preinit may actively rewrite enable bits while preserving an already-on rail.

Dependencies and integration points: TPS6586x MFD register helpers, regulator core, OF regulator matching, platform data, and parent version detection.

Risks: probe loops every possible ID and expects `reg_init_data` array indexing to match IDs. Static descriptor tables are reused globally. Preinit changes live enable bits and must not create brownouts. Slew rate is valid only for SM0/SM1.

Test signals: each PMIC version override, DT parsing and SYS supply propagation, dual enable-bit normalization, SM0/SM1 slew programming, fixed/read-only regulators, and missing platform-data failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps6586x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65910-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65910-regulator.c

Purpose: Platform child regulator driver for TPS65910/TPS65911 PMICs, registering all chip-specific voltage rails with custom DCDC/LDO selector logic and external sleep-control configuration.

Important APIs/types/functions: `struct tps_info` describes rail names, input supplies, voltage tables/counts, and enable times. `struct tps65910_reg` owns dynamic descriptors, rdevs, chip ops, and external sleep-control tables. Custom ops implement mode control, DCDC voltage selectors, TPS65910 table selectors, TPS65911 computed LDO voltages, VDD3 fixed voltage, and VBB mapping. `tps65910_set_ext_sleep_config` programs EN1/EN2/EN3/SLEEP assignment registers.

Control flow: probe obtains board or DT data, gives register control to I2C, selects TPS65910 vs TPS65911 rail tables and control-register mapper, applies a TPS65910 DCDC clock-sync erratum workaround, allocates descriptors/info/rdev arrays, configures external sleep per rail, registers each regulator, and saves rdevs for shutdown. Shutdown clears external sleep control for every registered rail so reboot does not depend on external control pin state before bootloader setup.

State and persistence: regulator state is in parent regmap. Driver dynamically builds descriptors and stores board external-control configuration. DCDC OP/SR registers and gain fields encode selectors; external sleep assignment persists until cleared.

Dependencies and integration points: TPS65910 MFD, regmap, OF regulator matching, platform data, regulator core, and PMIC-specific sleep-control definitions.

Risks: external sleep config is complex and only warns on per-rail failure during probe. The function restricts a regulator to one external control input. DCDC selector math must preserve gain/OP/SR semantics. Shutdown clearing is important for reboot reliability.

Test signals: TPS65910 and TPS65911 variants, DCDC selector list/get/set, TPS65911 LDO voltage mapping, invalid multi-input sleep control, EN assignment register writes, erratum bit clearing, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65910-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65912-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps65912-regulator.c

Purpose: Platform child regulator driver for TPS65912 PMICs with four DCDC regulators and ten LDO regulators.

Important APIs/types/functions: `TPS65912_REGULATOR` builds descriptors with OF names, selector register, enable register, 6-bit selector mask, and linear ranges. DCDC ops use generic regmap enable/disable/get/set/list helpers. LDO ops add linear range voltage mapping.

Control flow: probe gets the parent `struct tps65912`, sets platform driver data, prepares config with parent OF node and regmap, and registers all 14 descriptors. There is no custom runtime state or parsing beyond descriptor metadata; per-regulator init comes from regulator-core OF matching through `of_match` names under `regulators`.

State and persistence: enable and voltage state lives in the parent PMIC registers. The driver holds no mutable per-regulator private state after registration.

Dependencies and integration points: TPS65912 MFD, platform device ID `tps65912-regulator`, regulator core, regmap, and OF regulator child nodes.

Risks: DCDC ops do not provide `map_voltage`, so consumer mapping support differs from LDOs. All descriptors assume 64 selectors and common enable bit 7. Probe aborts on the first registration failure and does not register a partial set.

Test signals: registration of all 14 rails, DCDC/LDO selector boundaries, OF child matching, parent regmap failures, and consumer behavior for DCDC voltage mapping without explicit `map_voltage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps65912-regulator.c -->
