# subset-b-005179 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/helpers.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/helpers.c

Purpose: shared helper implementation for Linux regulator drivers, especially regmap-backed regulators. It supplies exported operations for enable/disable/status, selector read/write, voltage/current/ramp mapping, bypass and discharge controls, and small consumer helpers.

Important APIs/types/functions: `regulator_is_enabled_regmap()`, `regulator_enable_regmap()`, `regulator_disable_regmap()`, `regulator_get_voltage_sel_regmap()`, `regulator_set_voltage_sel_regmap()`, pickable-range helpers, map/list-voltage helpers, current-limit helpers, `regulator_find_closest_bigger()`, and `regulator_set_ramp_delay_regmap()` are exported GPL symbols consumed by many regulator drivers.

Control flow: helper operations use descriptor fields in `struct regulator_desc` to translate framework calls into regmap reads or masked updates. Voltage mapping either iterates `list_voltage()`, uses linear descriptors, walks `linear_ranges`, or indexes voltage/current tables. Pickable range setting converts a global selector into a range selector plus local voltage selector and optionally toggles apply bits.

State and persistence: this file owns no persistent device state; it mutates hardware registers through `rdev->regmap`. Cached or policy state remains in the regulator core and device-specific drivers.

Dependencies and integration: depends on regmap, bit operations, linear range helpers, and regulator core descriptor contracts from `driver.h`. It is the common integration point for simple PMIC drivers in this subset.

Risks and test signals: descriptor masks must be nonzero and aligned because `ffs(mask)` drives shifts. `BUG_ON()` catches invalid descriptor setup in several paths. Tests should exercise table, linear, range, pickable-range, inverted-enable, apply-bit, current-limit, ramp-delay, and fixed-voltage descriptors under regmap failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi6421-regulator.c

Purpose: platform regulator driver for the HiSilicon Hi6421 PMIC, registering 21 LDOs, one audio LDO, and six buck regulators from a parent MFD regmap.

Important APIs/types/functions: `struct hi6421_regulator_pdata` holds the enable mutex; `struct hi6421_regulator_info` embeds each descriptor plus mode metadata. Descriptor macros define table, linear, linear-range, and buck variants. Mode handlers implement ECO idle for LDOs and standby for buck regulators.

Control flow: probe retrieves the parent `hi6421_pmic`, allocates shared private data, initializes the mutex, then iterates the static descriptor table and calls `devm_regulator_register()`. Enable operations are serialized by `hi6421_regulator_enable()` before calling the regmap helper.

State and persistence: runtime state is only the mutex-containing private object. Voltage selectors, enable bits, and mode bits persist in PMIC registers according to hardware behavior, not driver-managed storage.

Dependencies and integration: integrates with `linux/mfd/hi6421-pmic.h`, platform-device MFD enumeration, device tree regulator nodes named `regulators`, and standard regulator regmap helpers.

Risks and test signals: enable serialization is hardware-critical because concurrent regulator startup can damage the chip, but the function ignores the return value of `regulator_enable_regmap()`. Mode read/write calls ignore regmap errors. Test signals include registration of all descriptors, DT matching names, serialized enable behavior, ECO threshold selection, and failure handling on regmap write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v530-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi6421v530-regulator.c

Purpose: small platform regulator driver for five Hi6421V530 LDO rails, using table voltages and ECO idle mode support.

Important APIs/types/functions: `struct hi6421v530_regulator_info` stores `regulator_desc` and `mode_mask`; `HI6421V530_LDO()` builds descriptors; `hi6421v530_regulator_ldo_get_mode()` and `_set_mode()` translate normal/idle to masked enable-register bits.

Control flow: probe checks that the parent MFD has `struct hi6421_pmic`, prepares a config with parent device and regmap, then registers each LDO descriptor with devm cleanup. Regulator operations are mostly standard regmap helpers.

State and persistence: no software cache beyond descriptor constants. Enable state, voltage selector, and ECO mode are register state in the PMIC.

Dependencies and integration: depends on `hi6421-pmic` MFD parent data, platform device IDs, OF regulator matching under `regulators`, and the regulator core.

Risks and test signals: mode handlers ignore `regmap_read()`/`regmap_update_bits()` failures and always report success except for invalid mode. Probe is simple, so the main test signals are absent-parent rejection, per-LDO registration, voltage table correctness, mode bit setting, and DT names matching bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v530-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v600-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi6421v600-regulator.c

Purpose: SPMI-era Hi6421V600 regulator platform driver for eight known LDO rails, backed by a parent regmap supplied by `hi6421-spmi-core`.

Important APIs/types/functions: `struct hi6421_spmi_reg_priv` serializes enables; `struct hi6421_spmi_reg_info` stores descriptors plus ECO metadata; `HI6421V600_LDO()` defines rails. Custom enable, mode, and optimum-mode callbacks wrap standard table-voltage regmap operations.

Control flow: probe obtains the parent regmap from driver data, allocates the mutex private object, and registers every descriptor. Enable sets the enable mask while holding the mutex, then sleeps for the descriptor off/on delay to avoid simultaneous power-up.

State and persistence: only the enable mutex and static descriptor metadata are driver state. Voltage, enable, and idle-mode state live in SPMI PMIC registers.

Dependencies and integration: platform child of a SPMI PMIC core, standard regmap helpers, OF regulator nodes, and regulator consumer load-to-mode selection.

Risks and test signals: parent drvdata absence is a WARN path. ECO mode is rejected when a rail lacks an ECO mask, but get-mode still reads the register without error handling. Test with serialized concurrent enables, no-parent probe, each LDO’s voltage table, idle eligibility, and off/on delay timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v600-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi655x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi655x-regulator.c

Purpose: HiSilicon Hi655x LDO regulator driver registering selected LDO rails from an MFD parent.

Important APIs/types/functions: `struct hi655x_regulator` extends `regulator_desc` with separate disable and status registers. `hi655x_is_enabled()` reads status, `hi655x_disable()` writes a disable latch, and descriptor macros define table and linear LDO variants.

Control flow: probe retrieves `struct hi655x_pmic`, fills a shared config with parent regmap, sets `driver_data` to each static regulator record, and registers all descriptors. Enables and voltage selector operations use standard regmap helpers; disable and status use chip-specific registers.

State and persistence: no mutable driver state beyond static descriptor records. Register writes persist according to PMIC state; disable is not a normal masked clear but a write to a disable register.

Dependencies and integration: depends on `linux/mfd/hi655x-pmic.h`, platform MFD enumeration, OF regulator matching, and regulator core table/linear helpers.

Risks and test signals: `hi655x_is_enabled()` ignores read failures and returns a masked value as a boolean-ish integer. Several enum IDs are not implemented in the descriptor array, so platform data and bindings must match supported rails. Tests should cover enable/status/disable register separation, DT naming, and invalid parent data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi655x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/internal.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/internal.h

Purpose: private regulator framework header defining internal consumer state, logging helpers, OF lookup hooks, and common get/bulk-get entry points.

Important APIs/types/functions: `struct regulator` represents one consumer handle with voltage requests per suspend state, load, enable count, deferred disables, supply name, device link flag, and debugfs/sysfs fields. `struct regulator_voltage`, `enum regulator_get_type`, `dev_to_rdev()`, `rdev_*()` logging macros, and OF helper prototypes form the main interface.

Control flow: this header has no runtime control flow. It controls compile-time contracts between regulator core source files and provides stub OF functions when `CONFIG_OF` is disabled.

State and persistence: documents the in-memory per-consumer state used by the core; persistence is runtime only and tied to consumer handles, not hardware NVM.

Dependencies and integration: includes suspend state constants and relies on public regulator consumer/driver types included by users. It bridges core lookup paths, OF parsing, coupled regulators, and common regulator acquisition semantics.

Risks and test signals: layout changes affect regulator core internals broadly. OF stubs must preserve error semantics for non-DT builds. Test signals are compile coverage with `CONFIG_OF=y/n`, optional/exclusive get paths, coupled regulator parsing, and suspend-state voltage arrays sized by `PM_SUSPEND_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/irq_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/irq_helpers.c

Purpose: framework helper for regulator drivers that report fault or warning events through IRQs, including retry, cached error, notification, and fatal recovery handling.

Important APIs/types/functions: `struct regulator_irq` stores descriptor, IRQ, retry count, event data, and delayed work. Public APIs are `regulator_irq_helper()`, `regulator_irq_helper_cancel()`, and `regulator_irq_map_event_simple()`. Internal helpers update `rdev->cached_err` under `err_lock`.

Control flow: the threaded IRQ maps a hardware event to one or more regulator states, optionally skips events when relevant regulators are off, disables asserted IRQ lines, emits notifier events, records cached errors, and schedules delayed re-enable/status polling. Workqueue logic calls optional `renable()` until clear or fatal count is exceeded, then calls `die()` or `hw_protection_trigger()`.

State and persistence: per-helper retry count and cached regulator error bits persist during driver lifetime. There is no disk state.

Dependencies and integration: integrates with genirq, delayed workqueues, regulator notifier chains, cached-error reporting, and system hardware-protection shutdown.

Risks and test signals: `regulator_irq_helper_cancel()` sets only a local `h = NULL`, not `*handle`, so callers do not get a nulled handle despite the comment. `skip_off` assumes `is_enabled` exists. Test status-map failures, persistent asserted IRQs, fatal recovery, high-priority work, cached-error clearing, and cancellation races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/irq_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/isl6271a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/isl6271a-regulator.c

Purpose: I2C regulator driver for the Intersil ISL6271A, exposing one programmable core buck and two fixed LDO outputs.

Important APIs/types/functions: `struct isl_pmic` stores the client and mutex. `isl6271a_get_voltage_sel()` and `_set_voltage_sel()` perform raw SMBus byte read/write for the core buck. Descriptor array `isl_rd[]` defines the core and fixed LDO regulators.

Control flow: `subsys_initcall()` registers the I2C driver. Probe checks SMBus byte-data support, allocates state, initializes the mutex, and registers all three descriptors, applying platform init data only to the core regulator.

State and persistence: the driver caches no hardware selector; it reads the core selector on demand. Fixed LDOs are static descriptors. Hardware voltage state persists in the device register.

Dependencies and integration: I2C SMBus byte operations, platform regulator init data, and regulator linear helpers.

Risks and test signals: no DT support and no enable/disable operations. The core selector is not bounds-checked before SMBus write beyond framework selector validation. Test signals include adapter functionality rejection, locked I2C access, selector read/write errors, and registration of fixed LDO voltage values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/isl6271a-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/isl9305.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/isl9305.c

Purpose: I2C/regmap regulator driver for the Intersil/Renesas ISL9305 and ISL9305H, exposing two DCDC rails and two LDO rails.

Important APIs/types/functions: `isl9305_regulators[]` defines four descriptors with linear voltages, enable masks, and supply names. `isl9305_ops` uses standard regmap enable/status and voltage selector helpers. `isl9305_regmap` configures 8-bit register access with maple cache.

Control flow: probe initializes an I2C regmap, then registers all four regulators, optionally using legacy platform init data. OF and I2C IDs cover both old `isl,*` compatible strings and preferred `isil,*` strings.

State and persistence: no software state is allocated beyond devm objects. Regmap cache represents register state while actual regulator state lives in hardware.

Dependencies and integration: I2C, regmap, platform data `isl9305_pdata`, OF regulator matching, and regulator core.

Risks and test signals: probe creates `regmap` but does not assign `config.regmap`, so registered regulators relying on `rdev->regmap` would lack the map unless supplied elsewhere; this is a high-value review/test point. Test with OF and platform-data enumeration, enable/status operations, and regmap failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/isl9305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lm363x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lm363x-regulator.c

Purpose: platform regulator child driver for TI LM3631, LM3632, and LM36274 backlight/biased-display PMIC devices.

Important APIs/types/functions: `lm363x_regulator_desc[]` contains boost and positive/negative/contrast LDO descriptors for multiple chip IDs. `lm363x_regulator_enable_time()` decodes LM3631 enable-time registers. GPIO helpers optionally wire external enable pins for LM3632/LM36274 LDOs and set external-enable bits.

Control flow: probe uses `pdev->id` as an index into the descriptor table, gets the parent `ti_lmu` regmap, optionally acquires nonexclusive enable GPIOs, configures external-enable mode, and registers one regulator.

State and persistence: no per-device mutable state is stored. Enable GPIO ownership is passed to the regulator core. Hardware registers hold voltage, enable, and timing state.

Dependencies and integration: MFD `ti-lmu`, register definitions in `ti-lmu-register.h`, GPIO descriptors, OF matching via descriptor `of_match`, and regulator regmap helpers.

Risks and test signals: `pdev->id` must be valid; there is no explicit bounds check before indexing descriptors. GPIO lifecycle is deliberately non-devm because regulator core owns it. Test with each chip child ID, optional GPIO absence/presence, external-enable write failure, and LM3631 enable-time decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lm363x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lochnagar-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lochnagar-regulator.c

Purpose: regulator driver for Cirrus Logic Lochnagar board rails, including MICVDD, MIC1VDD, MIC2VDD, and VDDCORE.

Important APIs/types/functions: descriptor table `lochnagar_regulators[]`, linear ranges for MICVDD and VDDCORE, custom micbias enable/disable wrappers, and `lochnagar_micbias_of_parse()` for `cirrus,micbias-input` routing.

Control flow: platform probe selects a descriptor from OF match data, fills config with parent regmap and `struct lochnagar`, then registers one regulator. MICBIAS enable/disable operations update register bits under `analogue_config_lock` and call `lochnagar_update_config()`.

State and persistence: state lives in Lochnagar hardware registers and parent MFD locks. The regulator driver stores no private allocation.

Dependencies and integration: depends on Lochnagar MFD core and register headers, OF compatible strings per regulator, regmap helpers, and the regulator framework.

Risks and test signals: micbias input parsing writes a shifted raw DT value without range validation against the mask width. Register changes are tied to parent analogue config synchronization. Test each compatible, voltage range mapping, micbias GPIO/source routing, lock usage, and update-config failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lochnagar-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp3971.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp3971.c

Purpose: legacy I2C regulator driver for National Semiconductor LP3971 PMIC, exposing five LDOs and three DCDC converters through platform data.

Important APIs/types/functions: `struct lp3971` stores device, client, and I/O mutex. Custom SMBus helpers implement locked byte reads and read-modify-write. LDO and DCDC ops implement enable, disable, selector get/set, table listing, and buck voltage-change triggering.

Control flow: probe requires platform data, detects the chip by checking `SYS_CONTROL1`, then registers only the regulators listed in `pdata->regulators`. DCDC voltage changes write target voltage and pulse the GO bit in the voltage-change register.

State and persistence: no selector cache. PMIC registers store enable and voltage state. Platform data controls which regulators exist and their init constraints.

Dependencies and integration: I2C SMBus byte data, `linux/regulator/lp3971.h`, platform init data, and regulator table helpers.

Risks and test signals: `lp3971_reg_read()` ignores read errors and returns zero-like data. No DT support. Descriptor indexes from platform data are trusted. Test chip detection, platform-data absence, each regulator ID, DCDC GO bit sequencing, and I2C failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp3971.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp3972.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp3972.c

Purpose: legacy LP3972 PMIC regulator driver, modeled after LP3971, for five LDOs and three DCDC converters.

Important APIs/types/functions: `struct lp3972`, locked SMBus read/write helpers, LDO enable/voltage functions using per-LDO register tables, DCDC functions, and descriptor array `regulators[]` with chip-specific voltage tables.

Control flow: `subsys_initcall()` registers the I2C driver. Probe requires platform data, reads `SCR1` for detection, initializes locked I/O state, and registers platform-listed regulators. LDO1/LDO5 and DCDC1 pulse voltage-change GO bits after selector writes.

State and persistence: runtime state is only the I2C client and mutex. PMIC registers hold output enables, selectors, and voltage-change target selection.

Dependencies and integration: I2C SMBus byte data, `linux/regulator/lp3972.h`, platform regulator init data, and regulator framework table helpers.

Risks and test signals: read helper ignores errors when called through `lp3972_reg_read()`, leading to possible false disabled/selector zero reports. Platform IDs are trusted. Test detection-mask behavior, absent platform data, LDO-specific masks, buck1-only GO behavior, and error cleanup on partial registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp3972.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp872x.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp872x.c

Purpose: combined I2C/regmap driver for TI/National LP8720 and LP8725 PMU regulators, covering LDOs, LILO outputs, and bucks with dynamic voltage scaling.

Important APIs/types/functions: `struct lp872x` stores regmap, chip ID, platform/DT data, regulator count, and DVS pin state. Buck helpers select active VOUT registers from DVS mode/pins, LDO helpers use standard regmap ops, and DT parsing builds `lp872x_platform_data`.

Control flow: probe obtains platform data or synthesizes it from DT, initializes regmap, optionally enables the hardware GPIO, applies general config, initializes DVS mode, and registers all descriptors for the selected chip. Buck voltage set may first drive DVS GPIOs, then update the selected VOUT register.

State and persistence: driver state includes DVS pin state and platform configuration. Regmap/hardware store voltage selectors, enable bits, PWM mode, and timing.

Dependencies and integration: I2C, regmap, GPIO descriptors, OF regulator matching, platform data `lp872x.h`, and current-limit helpers for LP8725 bucks.

Risks and test signals: DT compatible table lacks `.data`, so OF-only probe still relies on I2C ID driver data. `lp872x_hw_enable()` returns `-EINVAL` when no platform data exists, making sparse DT data risky. Test DVS GPIO modes, buck address selection, DT/platform parsing, enable GPIO delay, and current-limit masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp872x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp873x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp873x-regulator.c

Purpose: platform regulator driver for TI LP873x PMICs, registering two bucks and two LDOs from an MFD parent.

Important APIs/types/functions: `LP873X_REGULATOR()` builds descriptors plus a `ctrl2_reg` field. Buck callbacks include voltage, ramp, voltage-time, and current-limit operations; LDO callbacks cover voltage and enable. `lp873x_buck_set_ramp_delay()` maps requested slew to register codes and updates constraints.

Control flow: probe gets parent `struct lp873x`, points config OF node at the parent node, then registers all four descriptors. Runtime operations are standard regmap helpers except buck ramp-delay selection.

State and persistence: no private regulator state. Hardware and regmap hold voltage, enable, slew, and current-limit settings; constraints are updated with the selected ramp delay.

Dependencies and integration: `linux/mfd/lp873x.h`, platform MFD child, regmap, regulator linear ranges, bitfield helpers.

Risks and test signals: LDO descriptors inherit buck current-limit fields with dummy control register values from the macro, though LDO ops do not use them. Test all four registrations, ramp-delay bucket boundaries, current-limit selection, OF node parsing, and regmap failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp873x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8755.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp8755.c

Purpose: I2C regulator driver for TI LP8755 high-performance PMU, supporting multi-phase buck configurations and fault IRQ notifications.

Important APIs/types/functions: `struct lp8755_chip` stores regmap, platform data, IRQ mask, phase configuration, and registered buck devices. `mphase_buck[]` maps hardware phase modes to active buck IDs. Buck ops implement voltage, enable, mode, ramp, and enable-time behavior.

Control flow: probe initializes regmap and platform data. If board data is absent, it reads the phase configuration and builds default constraints. It registers only active bucks for the phase mode, then configures an optional threaded IRQ. IRQ handling clears flag registers and emits power-fault, OCP, or OVP notifier events.

State and persistence: software state includes active buck map, IRQ mask, and regulator pointers. Hardware stores phase, voltage, mode, ramp, and fault flags. Remove and some error paths disable buck outputs.

Dependencies and integration: I2C, regmap, platform data `lp8755.h`, regulator notifier chains, and IRQ framework.

Risks and test signals: `mphase` read from hardware is used as an array index without bounds validation. Remove disables all buck registers, which may surprise shared systems. Test phase modes, IRQ mask/event mapping, ramp table, mode transitions, and probe failure output-disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8755.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp87565-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp87565-regulator.c

Purpose: platform regulator driver for TI LP87565-family buck regulators, including grouped multiphase variants.

Important APIs/types/functions: `LP87565_REGULATOR()` defines descriptors and control-register metadata. `lp87565_buck_set_ramp_delay()` maps requested ramp to register codes, writes slew-rate bits, and adjusts constraints. Descriptor entries cover BUCK0-3 plus BUCK10, BUCK23, and BUCK3210 grouped rails.

Control flow: probe retrieves parent `struct lp87565`, chooses descriptor index range based on `dev_type`, and registers the matching rails. Standard regmap helpers handle enable, voltage, current limit, and voltage timing.

State and persistence: driver stores no private mutable state. Register state persists in the PMIC; selected ramp delay is reflected in regulator constraints with a conservative margin.

Dependencies and integration: `linux/mfd/lp87565.h`, platform MFD enumeration, regmap, bitfield helpers, linear ranges, and current-limit tables.

Risks and test signals: descriptor selection by device type must match hardware phase grouping. The ramp-delay margin multiplies by 85/100 despite the comment saying 15 percent margin, so effective timing semantics deserve review. Test each device type, grouped rail registration, enable mask/value behavior, current limits, and ramp boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp87565-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-buck.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp8788-buck.c

Purpose: LP8788 MFD child driver for four buck regulators, with dynamic voltage scaling support on BUCK1 and BUCK2.

Important APIs/types/functions: `struct lp8788_buck` stores parent pointer, regulator, DVS data, and DVS GPIOs. Helpers select active BUCK1/2 VOUT registers from GPIO or register DVS state; buck ops implement voltage, enable, startup time, and forced/auto PWM mode.

Control flow: probe validates platform ID, allocates per-buck data, initializes DVS mode for BUCK1/2, and registers the selected descriptor. If platform DVS data and GPIOs are present, DVS is configured for external pins; otherwise the driver selects I2C register DVS control.

State and persistence: DVS GPIO state and platform DVS pointers are runtime state. Voltage selectors, enable bits, DVS mode, startup timing, and PWM mode live in LP8788 registers.

Dependencies and integration: LP8788 MFD helpers (`lp8788_read_byte`, `lp8788_update_bits`), GPIO descriptors, platform children, regulator linear-range helpers.

Risks and test signals: GPIO request failure silently falls back to register DVS mode in `lp8788_init_dvs()`, which can mask board wiring errors. Read errors in DVS mode selection are not checked. Test BUCK1/2 DVS pin combinations, BUCK3/4 normal selector path, PWM mode, startup time, and invalid platform IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-buck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-ldo.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp8788-ldo.c

Purpose: LP8788 MFD child driver for twelve digital LDOs and ten analog LDOs, split across DLDO and ALDO platform drivers.

Important APIs/types/functions: `struct lp8788_ldo` stores parent, descriptor, regulator, and optional enable GPIO. Voltage tables cover chip-specific DLDO/ALDO groups. `lp8788_config_ldo_enable_mode()` maps selected rails to external enable IDs and optional GPIOs.

Control flow: module init registers both DLDO and ALDO platform drivers. Each probe allocates state, configures external-enable mode if applicable, fills regulator config from parent platform data, and registers one descriptor. Enable-time callbacks decode per-rail startup registers.

State and persistence: optional enable GPIO ownership is transferred to the regulator core. Hardware registers store voltage selectors, enable bits, enable-source selection, and startup timing.

Dependencies and integration: LP8788 MFD accessors, GPIO descriptors, platform children, regulator table/linear helpers, and parent platform data arrays.

Risks and test signals: external-enable GPIO absence deliberately forces default register-enable mode, while GPIO acquisition errors abort probe. Some voltage tables contain repeated values for reserved selectors. Test every DLDO/ALDO ID, external enable IDs and indexes, enable-time reads, fixed/table voltage behavior, and platform-data constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-ldo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ltc3589.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/ltc3589.c

Purpose: I2C/regmap regulator driver for Linear Technology LTC3589, LTC3589-1, and LTC3589-2 PMICs.

Important APIs/types/functions: `struct ltc3589` holds copied descriptors and registered regulator pointers. Descriptor macros define SW1-3, BB_OUT, LDO1-4. `ltc3589_of_parse_cb()` scales voltage values from DT feedback dividers. Suspend voltage/mode callbacks use secondary DTV registers and VCCR apply/reference bits.

Control flow: probe copies base descriptors, patches LDO3/LDO4 variant data from match info, initializes regmap, registers all regulators, and optionally requests a threaded IRQ. ISR broadcasts over-temperature and undervoltage warning events, then clears IRQs.

State and persistence: copied descriptors are mutable per device to account for feedback dividers and variants. Regmap cache and hardware registers hold voltage, enable, ramp, suspend, and IRQ state.

Dependencies and integration: I2C, OF match data, regmap with readable/writeable/volatile filters, regulator notifier chains, and DT `lltc,fb-voltage-divider`.

Risks and test signals: regulator config does not set `config.regmap`, so standard regmap ops may lack `rdev->regmap`; this should be tested or reviewed against core behavior. Test divider parsing, variant tables, suspend DTV paths, ramp table writes, and IRQ event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ltc3589.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ltc3676.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/ltc3676.c

Purpose: I2C/regmap regulator driver for Linear Technology LTC3676 PMIC, exposing four switchers and four LDOs.

Important APIs/types/functions: `struct ltc3676` stores copied descriptors and regulator pointers. `ltc3676_of_parse_cb()` applies DT feedback divider scaling. Switcher ops implement selector writes, suspend voltage/mode, and pgood masking. ISR broadcasts warning notifier events.

Control flow: probe copies descriptors, sets LDO3 fixed voltage, initializes regmap, registers all regulators, clears IRQs, and requests an optional threaded IRQ. Switcher selector changes first set the DVBxB pgood mask, then write the active selector.

State and persistence: per-device copied descriptors hold scaled voltage values. Hardware/regmap store enable, selector, suspend reference, pgood, and IRQ state. Optional platform init data can provide per-regulator constraints.

Dependencies and integration: I2C, OF regulator matching, platform init data, regmap, notifier chains, and DT `lltc,fb-voltage-divider`.

Risks and test signals: no `config.regmap` is assigned during registration despite use of standard regmap helpers. Feedback divider parsing does not reject zero divider values. Test switcher/LDO registration, platform data arrays, divider scaling, suspend mode polarity, IRQ warnings, and regmap helper paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/ltc3676.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max14577-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max14577-regulator.c

Purpose: MFD child regulator driver for Maxim MAX14577 and MAX77836, covering SAFEOUT, charger current regulation, and MAX77836 LDO1/LDO2.

Important APIs/types/functions: charger callbacks implement multi-register enable status and current-limit get/set using shared Maxim charger-current tables. `max14577_get_regmap()` selects between charger/safeout regmap and MAX77836 PMIC regmap. Descriptor arrays differ by device type.

Control flow: init performs build-time descriptor-size and voltage-range checks, then registers the platform driver. Probe selects the supported descriptor array by `dev_type`, applies optional platform init/of nodes by matching array index, selects each regulator’s regmap, and registers it.

State and persistence: no private mutable state. Hardware registers store charger enable/current, safeout enable, and LDO voltage/enable state.

Dependencies and integration: MAX14577 MFD private APIs, platform data, OF regulator matching, regulator current and voltage types, and standard regmap helpers.

Risks and test signals: charger `is_enabled()` does not check `max14577_read_reg()` return values. Platform regulator arrays must align with descriptor indexes. Test both device types, regmap selection for MAX77836 LDOs, current-limit boundary calculations, charger status logic, and BUILD_BUG_ON invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max14577-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max1586.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max1586.c

Purpose: I2C regulator driver for Maxim MAX1586 V3 and V6 outputs, including DT parsing for V3 external gain.

Important APIs/types/functions: `struct max1586_data` stores client, scaled V3 min/max, and cached V3/V6 selectors. V3/V6 set callbacks write one command byte because hardware has no readback. `of_get_max1586_platform_data()` parses `v3-gain` and child regulator constraints.

Control flow: probe obtains platform data or DT-derived data, allocates state, computes scaled V3 voltage range, initializes default selector cache, and registers subdevices with platform constraints. `subsys_initcall()` registers the I2C driver.

State and persistence: selector state is cached in software because the chip cannot report it. Hardware output state changes on SMBus byte writes; cache is initialized to assumed power-up defaults.

Dependencies and integration: I2C SMBus byte writes, platform data `max1586.h`, OF regulator matching under a `regulators` child, and regulator linear/table helpers.

Risks and test signals: if neither platform data nor DT data is available, `pdata` can remain NULL before dereference. DT matching fills subdevice IDs by match array index rather than a matched regulator identity. Test no-data probe, `v3-gain` scaling, cache correctness after write failures, V6 1uV off surrogate, and subdevice constraint registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max1586.c -->
