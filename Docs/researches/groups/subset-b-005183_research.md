# subset-b-005183 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf0900-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pf0900-regulator.c

Purpose: implements the NXP PF0900 PMIC regulator driver over I2C. It exposes five buck switchers, three LDOs, and VAON through the regulator framework, with optional I2C CRC support and IRQ-driven regulator fault notifications.

Important APIs/types/functions: `struct pf0900` stores the device, custom regmap, IRQ, I2C address, CRC flag, and `rdevs[]`. `struct pf0900_regulator_desc` extends `regulator_desc` with suspend enable and standby voltage metadata. `pf0900_regmap_read()` and `pf0900_regmap_write()` implement the custom `regmap_bus`, using SMBus byte transfers normally and SMBus word transfers with SAE-J1850 CRC when `nxp,i2c-crc-enable` is set. Regulator operations are split into VAON, DVS buck, and LDO op tables. `pf0900_suspend_enable()`, `pf0900_suspend_disable()`, and `pf0900_set_suspend_voltage()` manage standby mode and voltage. `pf0900_irq_handler()` maps status registers to regulator notifier events.

Control flow: probe requires an IRQ, allocates state, reads match data, enables optional CRC, initializes regmap, validates device family/id, registers all regulators, requests the threaded IRQ, clears the default power-up interrupt, masks it, and unmasks switch/LDO current-limit, under-voltage, and over-voltage events. IRQ handling reads each fault register, clears asserted bits, then calls `regulator_notifier_call_chain()` for affected switch or LDO/VAON regulators.

State and persistence: runtime state is devm-managed. The regmap uses `REGCACHE_MAPLE` while all chip registers are treated volatile. Suspend voltage caches avoid duplicate standby writes but are memory-only. Hardware register settings persist only as PMIC state.

Dependencies and integration: depends on I2C/SMBus, regmap, OF regulator parsing, GPIO consumer headers, and regulator core helpers. Device tree compatible is `nxp,pf0900`; regulator children are under `regulators`.

Risks and test signals: CRC mode must match hardware framing exactly. The device-id check only rejects some mismatches, so board DT correctness matters. IRQ paths assume all `rdevs[]` entries were registered before events. Test by probing with and without CRC, validating regulator voltage tables, suspend voltage writes, IRQ fault clearing/notifier events, and failure paths for bad ID, missing IRQ, and SMBus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf0900-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf1550-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pf1550-regulator.c

Purpose: implements the regulator child driver for the NXP/Freescale PF1550 PMIC behind the PF1550 MFD core. It registers three switchers, VREFDDR, and three LDOs and forwards PMIC IRQs to regulator notifications.

Important APIs/types/functions: `struct pf1550_desc` wraps each `regulator_desc` with standby voltage and standby enable register data. `struct pf1550_regulator_info` keeps the parent MFD data, copied descriptors, and registered `rdevs[]`. `pf1550_set_ramp_delay()` programs buck ramp bits. `pf1550_set_suspend_enable()`, `pf1550_set_suspend_disable()`, `pf1550_buck_set_table_suspend_voltage()`, and `pf1550_buck_set_linear_suspend_voltage()` implement suspend behavior. Descriptor macros `PF_SW`, `PF_VREF`, `PF_LDO1`, and `PF_LDO2` build the regulator table.

Control flow: platform probe obtains the parent `struct pf1550_ddata`, gets the parent regmap, copies static descriptors into per-device storage, adjusts SW1/SW2 voltage mode based on OTP DVS enable bits, registers every regulator, stores driver data, and requests all platform IRQs. The threaded IRQ handler maps platform IRQ index to current-limit, LDO fault, or thermal events and emits regulator notifier events.

State and persistence: descriptors are copied at probe because SW1/SW2 ops and voltage tables may be changed based on parent OTP-derived state. Runtime state is devm-managed. Regulator settings are PMIC register state; the driver does not persist policy beyond hardware writes.

Dependencies and integration: depends on the PF1550 MFD header for IDs, register addresses, IRQ numbers, and parent data. Integrates with platform bus, parent regmap, and regulator framework. Device tree matching and regmap ownership live in the MFD layer.

Risks and test signals: `pf1550_set_ramp_delay()` divides `6250 / ramp_delay` after accepting zero because only `< 0` is rejected, so zero input is a bug risk. IRQ mapping loops through `platform_get_irq()` on every interrupt and notifier targeting appears hard-coded to names such as `SW3`/`LDO3` for groups, which deserves hardware validation. Test with DVS enabled/disabled OTP states, all IRQ indices, ramp-delay corner cases, suspend voltage setting, and missing parent regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf1550-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf530x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pf530x-regulator.c

Purpose: provides an I2C regulator driver for NXP PF5300/PF5301/PF5302 single-buck PMICs. It registers the SW1 regulator, exposes voltage, bypass, status, and error flag operations, and validates the detected chip identity.

Important APIs/types/functions: `struct pf530x_chip` contains the device and regmap. `pf530x_get_status()` maps interrupt sense and PMIC state registers to regulator status values. `pf530x_get_error_flags()` maps over-voltage, under-voltage, current-limit, and thermal bits into regulator error flags. `pf530x_identify()` reads device ID, revision, EM revision, and program ID registers and logs a decoded chip revision string. `pf530x_reg_desc` describes SW1 with an 0.5 V to 1.2 V style linear range, enable bits, and bypass bits.

Control flow: I2C probe allocates state, initializes an 8-bit regmap, identifies the chip, obtains OF regulator init data from the device node, builds a regulator config, and registers one regulator. Status calls first inspect fault sense bits, then read the PMIC state register to distinguish run, standby, and low-power-off states.

State and persistence: state is minimal and devm-managed. The driver does not cache voltage or enable state. The regmap uses `REGCACHE_MAPLE`; hardware register state persists according to PMIC behavior.

Dependencies and integration: depends on I2C, regmap, regulator core, and OF regulator helpers. Device tree compatible is `nxp,pf5300`; I2C IDs also list `pf5300`, `pf5301`, and `pf5302`.

Risks and test signals: `pf530x_identify()` returns `ret` after an unknown family even though `ret` is zero from a successful read, so unknown-family detection can incorrectly succeed. The OF table only lists `nxp,pf5300` despite I2C IDs for the family. Test chip identification for all device IDs and bad families, regulator voltage selection, bypass on/off, status mapping for RUN/STANDBY/LP_OFF/fault states, and error flag reads from both interrupt status registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf530x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf8x00-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pf8x00-regulator.c

Purpose: implements the NXP PF8100/PF8121A/PF8200 regulator driver over I2C. It registers four LDOs, seven buck regulators, and VSNVS with voltage, enable, suspend, and current-limit controls.

Important APIs/types/functions: `struct pf8x00_regulator_data` extends `regulator_desc` with suspend enable/voltage metadata and a cache. `struct pf8x00_chip` holds regmap and device. `swxilim_select()`, `handle_ilim_property()`, and `handle_shift_property()` parse legacy `nxp,ilim-ma` and `nxp,phase-shift` DT properties for buck configuration. `pf8x00_suspend_enable()`, `pf8x00_suspend_disable()`, and `pf8x00_set_suspend_voltage()` implement standby regulator state. Descriptor macros construct LDO, buck1-6, buck7, and VSNVS entries.

Control flow: probe initializes regmap, validates the PF8x00 family/device ID, then iterates `pf8x00_regs_data` and registers every regulator with config driver data pointing at the descriptor wrapper. Buck OF parsing may adjust current-limit and phase-shift registers during registration. Suspend voltage writes map requested voltages through regulator linear/table helpers and write standby voltage registers.

State and persistence: global descriptor data is mutated only through per-regulator cache fields and DT callbacks; this is acceptable for one device instance but would be risky for multiple instances. Suspend voltage caches are volatile memory. Hardware configuration is PMIC register state.

Dependencies and integration: integrates with I2C, regmap, regulator core, and OF regulator parsing. Compatible strings are `nxp,pf8100`, `nxp,pf8121a`, and `nxp,pf8200`.

Risks and test signals: `pf8x00_identify()` has the same unknown-family pattern as PF530x, returning `ret` after a successful read instead of an error. `handle_shift_property()` computes `id = desc->id - PF8X00_LDO4`, which gives buck numbering but is easy to misread. Global regulator descriptor mutation can leak between devices. Test all compatibles, invalid IDs, current-limit programming, phase-shift validation, buck/LDO/VSNVS voltage tables, suspend voltage/enable behavior, and multi-instance probe assumptions if hardware permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf8x00-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf9453-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pf9453-regulator.c

Purpose: implements the NXP PF9453 PMIC regulator driver over I2C. It registers four buck regulators, two LDOs, and LDOSNVS, supports protected-register writes, DVS properties for BUCK2, IRQ logging, watchdog reset configuration, and optional SD_VSEL GPIO control.

Important APIs/types/functions: `struct pf9453` stores device, regmap, IRQ, and optional `sd-vsel` GPIO. `struct pf9453_regulator_desc` carries a `regulator_desc` plus DVS register metadata. `is_reg_protect()` identifies voltage registers that require lock/unlock sequencing. `pf9453_pmic_write()` performs masked writes and unlocks protected registers with `PF9453_UNLOCK_KEY`. Custom enable, disable, voltage-select, and ramp-delay ops wrap regulator helpers to use protected writes. `pf9453_set_dvs_levels()` parses `nxp,dvs-run-voltage` and `nxp,dvs-standby-voltage`.

Control flow: probe requires an IRQ, initializes regmap, validates device ID high nibble, registers regulators from OF match data until the sentinel, requests a shared threaded IRQ, unmasks selected interrupts, configures WDOG_B warm/cold reset behavior from DT, and drives optional `sd-vsel` high so LDO1 uses `LDO1OUT_H`. The IRQ handler reads `INT1` and logs asserted reset, key, VR fault, low system voltage, and thermal events.

State and persistence: no per-regulator runtime cache except hardware registers. DVS settings and reset behavior are written to PMIC registers during probe. GPIO lifetime is devm-managed.

Dependencies and integration: depends on I2C, regmap, GPIO descriptors, OF, and regulator core. Compatible is `nxp,pf9453`.

Risks and test signals: `pf9453_pmic_write()` may return `-EINVAL` for invalid registers but silently skips writes when `reg >= PF9453_MAX_REG`; call sites should never pass bad registers. DVS parsing loops standby and deep-standby over the same property/register, causing duplicate writes. IRQ handling logs but does not notify regulator consumers. Test protected writes, DVS property exact-match failures, WDOG_B DT property, SD_VSEL GPIO behavior, IRQ status handling, and voltage/ramp operations on BUCK2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pf9453-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pfuze100-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pfuze100-regulator.c

Purpose: supports Freescale/NXP PFUZE100, PFUZE200, PFUZE3000, and PFUZE3001 PMIC regulator variants over I2C. It selects variant-specific regulator tables, parses regulator DT nodes, handles ramp delay, optional switcher disable support, and optional system power-off preparation.

Important APIs/types/functions: `struct pfuze_regulator` extends `regulator_desc` with standby register/mask and switcher flag. `struct pfuze_chip` holds chip ID, flags, regmap, copied descriptors, registered regulators, and selected static table. Descriptor macros generate fixed, switcher, SWBST, VGEN, COIN, and PFUZE3000-specific regulators. `pfuze100_set_ramp_delay()` programs ramp bits for supported switchers. `pfuze_parse_regulators_dt()` chooses the correct `of_regulator_match` table. `pfuze_power_off_prepare()` changes PFUZE100 switcher and VGEN standby behavior for poweroff.

Control flow: probe determines chip type from OF or I2C ID, initializes regmap, validates identity and revision/fab registers, selects regulator table and switcher high-bit range, copies descriptors, parses DT, optionally adjusts voltage ranges based on current selector high bits, optionally enables switcher disable semantics for old-DTB compatibility, registers every regulator, and registers the power-off-prepare handler if `fsl,pmic-stby-poweroff` is set.

State and persistence: per-device descriptor copies are mutated for detected voltage range and optional disable support. The global `pfuze_matches` points at the active match table during probe. Power-off preparation writes PMIC standby mode registers.

Dependencies and integration: depends on I2C, OF, regmap, regulator framework, sys-off handlers, and `linux/regulator/pfuze100.h` IDs.

Risks and test signals: `pfuze_matches` is global, which is fragile for multiple PFUZE instances probing concurrently. Ramp delay calculation has non-obvious integer math and accepts zero by programming zero bits. Backward compatibility around `fsl,pfuze-support-disable-sw` must be preserved. Test each compatible, ID mismatch, high-bit voltage range selection, DT match ordering, switcher disable behavior, ramp delay, and power-off prepare register writes only on PFUZE100.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pfuze100-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.c

Purpose: implements the Powerventure/Dialog PV88060 I2C regulator driver. It registers one buck, seven LDOs, and six fixed-voltage switches, and reports global VDD fault and over-temperature events to all registered regulators.

Important APIs/types/functions: `struct pv88060_regulator` wraps `regulator_desc` with a buck configuration register. `struct pv88060` stores device, regmap, and registered regulator devices. `pv88060_buck_get_mode()` and `pv88060_buck_set_mode()` map chip buck mode bits to regulator FAST/NORMAL/STANDBY modes. Descriptor macros `PV88060_BUCK`, `PV88060_LDO`, and `PV88060_SW` define regulator descriptors and register/mask fields. `pv88060_irq_handler()` handles event register bits.

Control flow: probe allocates state, initializes an 8-bit regmap, optionally masks interrupt banks A/B/C, requests a low-triggered threaded IRQ, unmasks VDD fault and over-temperature events, then registers all regulators. IRQ handling reads `EVENT_A`, broadcasts under-voltage or over-temperature notifier events to every registered regulator, and clears handled event bits by writing back to `EVENT_A`.

State and persistence: there is no voltage or mode cache. Optional platform data can provide per-regulator init data. PMIC register state persists according to hardware; driver state is devm-managed.

Dependencies and integration: depends on I2C, regmap, interrupt handling, regulator core, and optional OF matching (`pvs,pv88060`). Register constants come from `pv88060-regulator.h`.

Risks and test signals: no chip identity register is checked, so compatible/I2C binding correctness is critical. Global fault events are broadcast to all regulators rather than source-specific. If no IRQ is configured the driver still works but fault notification is absent. Test regulator registration, buck current-limit table, buck mode transitions, LDO voltage ranges, switch enable bits, IRQ mask/unmask/clear behavior, and operation with no IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.h

Purpose: defines the PV88060 register map and bit masks consumed by `pv88060-regulator.c`.

Important APIs/types/functions: this header has no functions or types. It defines event/mask registers (`PV88060_REG_EVENT_A`, `PV88060_REG_MASK_A/B/C`), regulator configuration registers for BUCK1, LDO1-7, and SW1-6, event bits (`PV88060_E_VDD_FLT`, `PV88060_E_OVER_TEMP`), interrupt mask bits, enable bits, voltage selector masks, buck current-limit mask, and buck mode encodings.

Control flow: none directly. The C driver uses these constants to build regulator descriptors, set and get buck mode, mask/unmask interrupts, and clear event latches.

State and persistence: none in the header. It describes persistent PMIC register fields used by runtime code.

Dependencies and integration: guarded by `__PV88060_REGISTERS_H__` and included only by the PV88060 regulator implementation. Its names are tightly coupled to descriptor macros such as `PV88060_REG_##regl_name##_CONF`.

Risks and test signals: incorrect register addresses or masks would cause wrong regulator control or missed fault interrupts. Because macro-generated descriptor fields rely on exact naming patterns, renaming constants can break builds. Test signals are compile coverage of all macro expansions and hardware/regmap tests for event bits, enable masks, selector masks, current limits, and buck mode values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88060-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.c

Purpose: implements the PV88080 regulator driver for AA/BA register-layout variants. It registers three buck regulators and one HVBUCK, supports dynamic voltage range calculation, buck current limits, buck modes, and global fault IRQ notifications.

Important APIs/types/functions: `struct pv88080_compatible_regmap` describes variant-specific register addresses and masks for AA and BA silicon. `struct pv88080_regulator` wraps descriptors with mode and range config registers. `pv88080_buck_get_mode()` and `pv88080_buck_set_mode()` map mode bits to regulator modes. Descriptor macros define generic buck and HVBUCK descriptors, which are completed at probe from variant regmap data. `pv88080_irq_handler()` broadcasts VDD fault and over-temperature events.

Control flow: probe initializes regmap, selects match data through `i2c_get_match_data()`, sets up optional IRQ masking and unmasking, then iterates buck1-3. For each buck it fills descriptor register fields from variant data, reads `conf2` and `conf5`, derives min/step/count from voltage range and gain bits, and registers the regulator. HVBUCK register fields are then filled and registered separately.

State and persistence: `pv88080_regulator_info` is a static mutable descriptor array. Probe writes variant-specific register fields and voltage ranges into it, which is simple for one instance but risky for multiple instances. Hardware config registers determine runtime voltage range.

Dependencies and integration: depends on I2C, regmap, OF/I2C match data, interrupts, and regulator framework. Compatible strings include `pvs,pv88080`, `pvs,pv88080-aa`, and `pvs,pv88080-ba`. Register constants are in `pv88080-regulator.h`.

Risks and test signals: static descriptor mutation can leak between devices or variants. The voltage range index is taken directly from two one-bit fields and assumes valid hardware encodings. Global IRQs are broadcast to all regulators. Test AA and BA variants, dynamic voltage range derivation, HVBUCK registration, current-limit tables, buck mode transitions, IRQ handling, no-IRQ operation, and multiple-instance behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.h

Purpose: defines PV88080 event, mask, regulator register, voltage-range, current-limit, and mode bit constants for both AA and BA register-layout variants.

Important APIs/types/functions: no functions or structs are declared. The header provides AA and BA addresses for HVBUCK and BUCK1-3 control/config registers, event and mask bits, enable masks, voltage selector masks, current-limit masks, buck mode encodings, and VDAC/range-gain selectors.

Control flow: none directly. The C driver maps these constants into `struct pv88080_compatible_regmap` tables, then uses them to fill mutable regulator descriptors and calculate runtime voltage ranges.

State and persistence: none. Constants describe PMIC register fields that back persistent hardware state.

Dependencies and integration: guarded by `__PV88080_REGISTERS_H__` and included by `pv88080-regulator.c`. The constants are coupled to both variant regmap tables and regulator descriptor initialization.

Risks and test signals: AA/BA address mismatches would silently control the wrong registers. Current-limit masks are per buck but mode operations use the BUCK1 mode mask constant for all bucks, so mask equivalence matters. Test by compiling both match-data tables, validating register access on AA and BA hardware, reading VDAC/range-gain fields, and exercising event/mask bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88080-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.c

Purpose: implements the PV88090 I2C regulator driver. It registers three buck regulators and two LDOs, supports buck mode/current-limit control, dynamically derives BUCK2/BUCK3 voltage ranges, and reports global VDD fault and over-temperature events.

Important APIs/types/functions: `struct pv88090_regulator` wraps descriptors with buck mode/current config registers. `pv88090_buck_get_mode()` and `pv88090_buck_set_mode()` map register mode bits to regulator FAST/NORMAL/STANDBY. Descriptor macros `PV88090_BUCK` and `PV88090_LDO` build the regulator table. `pv88090_irq_handler()` broadcasts fault events and clears latches. Probe reads BUCK2/3 `CONF2` and `BUCK_FOLD_RANGE` to select one of three voltage range definitions.

Control flow: probe allocates state, initializes regmap, optionally masks event banks, requests a low-triggered threaded IRQ, unmasks VDD fault and over-temperature events, then registers each regulator. During BUCK2/3 registration it computes a range index from VDAC range and gain bits, rewrites descriptor min/step/count, and then calls `devm_regulator_register()`.

State and persistence: descriptors live in a static mutable array and are modified at probe based on hardware range bits. Runtime state is otherwise devm-managed with no voltage cache. Optional platform data can feed regulator init data.

Dependencies and integration: depends on I2C, regmap, interrupts, regulator core, optional OF compatible `pvs,pv88090`, and register constants from `pv88090-regulator.h`.

Risks and test signals: static descriptor mutation has multi-instance risk. BUCK2/3 range index validation only accepts indexes up to the enum value for BUCK3, which happens to match the voltage table size but is semantically odd. Global fault events are broadcast to all regulators. Test dynamic range calculation, buck1 large current-limit table, buck2/3 current limits, LDO voltage ranges, IRQ paths, no-IRQ operation, and invalid range combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.h

Purpose: defines PV88090 register addresses and bit masks used by `pv88090-regulator.c`.

Important APIs/types/functions: no functions or structs are provided. Constants cover system event/mask registers, BUCK1-3 config registers, LDO control registers, BUCK_FOLD_RANGE, event and mask bits, enable bits, voltage selector masks, current-limit masks, buck mode encodings, and VDAC/range-gain selectors.

Control flow: none directly. The C driver uses these constants for descriptor macro expansion, buck mode/current-limit operations, interrupt masking/clearing, and dynamic BUCK2/3 voltage range selection.

State and persistence: none in the header. It documents hardware register fields whose values persist in PMIC state.

Dependencies and integration: guarded by `__PV88090_REGISTERS_H__` and included by the PV88090 driver. Naming is coupled to `PV88090_BUCK`/`PV88090_LDO` token-pasting macros.

Risks and test signals: wrong masks or shifts would break current-limit reporting and range selection. The header defines `PV88090_REG_LDO3_CONT` though the C driver registers only LDO1 and LDO2, which may confuse future changes. Test through compile coverage, register read/write validation for all descriptor-generated fields, event bit handling, and voltage range selection from `CONF2` plus `BUCK_FOLD_RANGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pv88090-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pwm-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pwm-regulator.c

Purpose: implements a generic platform regulator whose output voltage is controlled by a PWM duty cycle, optionally gated by an enable GPIO. It supports discrete voltage-table mode and continuous voltage-range mode.

Important APIs/types/functions: `struct pwm_regulator_data` stores the PWM, optional voltage table, continuous-mode mapping, descriptor, cached table selector, and enable GPIO. `pwm_regulator_init_table()` parses `voltage-table` entries of `{uV, dutycycle}`. `pwm_regulator_init_continuous()` parses optional `pwm-dutycycle-range` and `pwm-dutycycle-unit`. Table ops implement selector get/set/list/map. Continuous ops implement voltage get/set by linear interpolation between regulator constraints and dutycycle bounds. Enable/disable ops coordinate GPIO and PWM state.

Control flow: probe requires a DT node, allocates state, copies a base descriptor, chooses table or continuous mode, obtains regulator init data, gets the PWM, configures optional enable GPIO according to `boot_on`/`always_on`, adjusts PWM config, preserves boot-on output state if needed, and registers the regulator. Table mode lazily initializes the cached selector by comparing current duty cycle to table entries.

State and persistence: `drvdata->state` caches the selected table row and starts as `-ENOTRECOVERABLE`. Continuous mode has no selector cache. PWM hardware state and enable GPIO state are runtime state; no persistent storage is used.

Dependencies and integration: depends on platform bus, OF regulator data, PWM framework, GPIO descriptors, and regulator core. Compatible is `pwm-regulator`.

Risks and test signals: table parsing casts a property into `struct pwm_voltages`, relying on two 32-bit cells and native layout. Continuous `set_voltage()` uses `req_min_uV` and does not explicitly verify `req_max_uV` after interpolation. `pwm_regulator_enable()` calls `gpiod_set_value_cansleep()` even when the optional GPIO is absent, relying on GPIO helper NULL tolerance. Test both DT modes, inverted duty ranges, boot-on preservation, GPIO present/absent cases, PWM apply failures, invalid voltage-table lengths, and get-voltage behavior when PWM is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pwm-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-labibb-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom-labibb-regulator.c

Purpose: implements Qualcomm PMI8998 LAB/IBB display bias regulators. It controls positive LAB and negative IBB supplies, current limits, soft-start/discharge settings, pull-down/active discharge, and safety recovery for over-current and short-circuit interrupts.

Important APIs/types/functions: `struct labibb_regulator` holds the copied descriptor, regmap, base address, type, IRQs, recovery work, current-limit parameters, and fault counters. `qcom_labibb_set_current_limit()` uses secure access before programming current limits. `qcom_labibb_set_ocp()` configures level-triggered VREG_OK OCP interrupts and installs `qcom_labibb_ocp_isr()`. `qcom_labibb_sc_isr()` and `qcom_labibb_sc_recovery_worker()` handle short-circuit conditions across both LAB and IBB. `qcom_labibb_of_parse_cb()` parses discharge resistor and soft-start DT values. Static descriptors define PMI8998 LAB and IBB register fields.

Control flow: platform probe gets the parent regmap, iterates match data for `lab` and `ibb`, validates peripheral type registers, finds child DT nodes, requires `sc-err` IRQs and optionally records `ocp` IRQs, initializes delayed work, sets type-specific current-limit metadata, copies and names descriptors, registers regulators, and requests short-circuit IRQs. OCP setup is deferred until regulator core calls the protection op.

State and persistence: fault counters and delayed work are in-memory runtime state. Current limit, voltage, pull-down, discharge, and enable settings live in PMIC registers. Recovery workers may disable or re-enable hardware after fault events.

Dependencies and integration: depends on parent Qualcomm regmap, OF child nodes and IRQ names, regulator core protection callbacks, delayed workqueues, and notifier chains. Compatible is `qcom,pmi8998-lab-ibb`.

Risks and test signals: OCP recovery can call `BUG_ON()` after repeated fatal disable failures, intentionally prioritizing hardware protection. Probe error path calls `dev_err_probe(vreg->dev, ...)` before `vreg` is allocated on missing short-circuit IRQ, which is a bug risk. Short-circuit recovery coordinates both LAB and IBB by fixed offset and assumes PMI8998 layout. Test peripheral type mismatch, required/optional IRQ handling, OCP enable and polarity, SC/OCP recovery counters, current-limit secure writes, DT table validation, and notifier events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-labibb-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-pm8008-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom-pm8008-regulator.c

Purpose: implements the Qualcomm PM8008 PMIC regulator child driver. It registers seven LDO regulators using a parent secondary regmap, with NLDO/PLDO voltage ranges, enable control, dropout metadata, and ramp delay derived from hardware step-rate bits.

Important APIs/types/functions: `struct pm8008_regulator` stores the parent regmap, per-instance descriptor, and base offset. `struct pm8008_regulator_data` defines each LDO name, supply name, base, dropout, and voltage range. `pm8008_regulator_set_voltage_sel()` converts selected microvolts to millivolts and writes a little-endian 16-bit value via `regmap_bulk_write()`. `pm8008_regulator_get_voltage_sel()` bulk reads the 16-bit millivolt register and maps it back to a selector.

Control flow: probe gets the parent `"secondary"` regmap, iterates the seven static LDO data entries, allocates a regulator object and descriptor, fills descriptor names, OF match, supply, voltage range, selector count, step/dropout, reads stepper control to compute `ramp_delay`, sets enable register/mask, and registers each regulator.

State and persistence: descriptors and state are per-regulator devm allocations. Voltage and enable settings are PMIC register state. No software voltage cache is used.

Dependencies and integration: depends on platform bus, parent MFD/regmap exposing `"secondary"`, regulator core, OF regulator child nodes under `regulators`, and little-endian register encoding.

Risks and test signals: config uses `config.dev = dev->parent` while allocation and registration use the child device, so sysfs/regulator parentage should be checked. Voltage writes round up to millivolts; selector mapping on read should tolerate hardware values not exactly on a linear step. Test all seven LDOs, missing secondary regmap, step-rate-derived ramp delay values, LE bulk read/write behavior, dropout constraints, and enable/disable bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-pm8008-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-refgen-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/qcom-refgen-regulator.c

Purpose: implements Qualcomm REFGEN MMIO-backed regulator support for SDM845 and SM8250-style reference generator blocks.

Important APIs/types/functions: SDM845 uses custom `qcom_sdm845_refgen_enable()`, `qcom_sdm845_refgen_disable()`, and `qcom_sdm845_refgen_is_enabled()` because enabling requires programming both bandgap control and bias-enable registers. SM8250 uses standard regmap enable/disable helpers on `REFGEN_REG_PWRDWN_CTRL5`. Two static `regulator_desc` instances are selected by OF match data. `qcom_refgen_probe()` maps MMIO, creates a 32-bit stride-4 regmap, gets regulator init data, and registers the regulator.

Control flow: probe retrieves the descriptor from the compatible, maps the platform resource, initializes an MMIO regmap, obtains DT regulator constraints, builds config, and registers one regulator. SDM845 enable writes BG control then bias enable; disable reverses the order. `is_enabled` checks both fields.

State and persistence: no software state is stored beyond devm-managed regmap and regulator device. Enable state lives in MMIO registers.

Dependencies and integration: depends on platform MMIO resources, regmap-mmio, OF regulator init data, and regulator core. Compatibles are `qcom,sdm845-refgen-regulator` and `qcom,sm8250-refgen-regulator`.

Risks and test signals: SDM845 helper functions ignore regmap return values and always report success for enable/disable; `is_enabled()` also ignores read errors. The descriptor embeds compound-literal ops with static storage duration through the descriptor initializer pattern. Test both compatibles, MMIO mapping failures, constraint absence, enable/disable/is_enabled register values, and injected regmap errors if test infrastructure supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/qcom-refgen-regulator.c -->
