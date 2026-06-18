# Research Report: subset-b-005176

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bcm590xx-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bcm590xx-regulator.c

Purpose: This driver registers voltage regulators exposed by Broadcom BCM59054 and BCM59056 PMIC MFD devices. It covers normal LDOs, general-purpose LDOs on the secondary I2C slave, switcher regulators, and a fixed 5 V VBUS output. The file is primarily a descriptor-table driver: chip-specific register addresses, voltage tables, and linear ranges are encoded statically, then `bcm590xx_probe()` selects the table based on `pmu_id` and analog revision.

Important APIs, types, and functions: `struct bcm590xx_reg_data` binds a regulator type, primary or secondary regmap selector, and a `regulator_desc`. `struct bcm590xx_reg` stores the parent MFD pointer plus the selected table. The regulator ops are standard regmap-backed helpers: `bcm590xx_ops_ldo` supports enable, voltage get/set, voltage table listing, and iterative mapping; `bcm590xx_ops_dcdc` supports linear ranges; `bcm590xx_ops_vbus` only supports enable state; `bcm590xx_ops_ldo_novolt` handles BCM59054 MICLDO as a fixed 1.8 V regulator without selector ops. Descriptor macros such as `BCM590XX_LDO_DESC()` and `BCM590XX_SR_DESC()` fill common fields including `of_match`, `regulators_node`, `vsel_reg`, `enable_reg`, masks, and inverted enable semantics.

Control flow: Probe obtains the parent `struct bcm590xx` from MFD driver data, allocates private state, chooses `bcm59054_regs`, `bcm59054_a1_regs`, or `bcm59056_regs`, and loops over every descriptor. Each iteration chooses `regmap_pri` or `regmap_sec` from the descriptor metadata and calls `devm_regulator_register()`. Failure aborts probe through `dev_err_probe()`.

State and persistence behavior: The driver keeps no runtime state beyond selected table pointers. Regulator state persists in PMIC registers through regmap. Most LDO and switcher enable bits use `enable_is_inverted = true`, so framework enable operations clear the hardware bit. BCM59054 A1 is represented by a separate static table only to alter the VSR voltage range. There is no suspend/resume or interrupt state.

Dependencies and integration points: The driver depends on the BCM590xx MFD for PMIC identity, revision, device pointer, and two regmaps. It integrates with regulator core constraints, device tree child nodes under `regulators`, and platform alias `bcm590xx-vregs`. Register definitions are local to this file rather than pulled from the MFD header.

Risks: Descriptor mistakes are the main risk: wrong slave regmap, inverted enable flag, selector mask, or revision table can disable or mis-scale rails. The table duplication between BCM59054 and BCM59054 A1 is easy to drift. Error messages report `pdev->name` rather than the descriptor name in one registration path, which may reduce diagnostic precision. There is no dynamic validation that selected PMIC regmaps are non-null.

Test signals: Probe tests should cover BCM59054 normal, BCM59054 A1, BCM59056, unknown PMIC ID, and both primary and secondary regmap regulator registration. Regulator tests should verify inverted enable semantics, VBUS enable bit behavior, MICLDO fixed-voltage behavior, and voltage selector mapping for table and linear-range regulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bcm590xx-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd71815-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bd71815-regulator.c

Purpose: This ROHM BD71815 regulator driver registers five bucks, five configurable LDOs, two fixed LDO-style outputs, and a WLED current regulator. It adds BD71815-specific dynamic voltage scaling support for RUN, SNVS, SUSPEND, and LPSR states, plus special BUCK1/BUCK2 handling for dual voltage registers.

Important APIs, types, and functions: `struct bd71815_regulator` wraps a `regulator_desc` with a `rohm_dvs_config`. Static `rohm_dvs_config` instances describe state-specific voltage and enable masks for bucks and LDOs. `set_hw_dvs_levels()` and `buck12_set_hw_dvs_levels()` are device-tree parse callbacks that call `rohm_regulator_set_dvs_levels()`. `bd7181x_buck12_get_voltage_sel()` and `bd7181x_buck12_set_voltage_sel()` implement the dual high/low selector register scheme. `bd7181x_led_set_current_limit()` wraps the regmap current helper to restore LED enable state if changing the current limit unexpectedly toggles hardware state.

Control flow: `bd7181x_probe()` gets the parent regmap, optionally fetches parent firmware GPIO `rohm,vsel` for LDO4 enable, clears `RESTARTEN` so power-off can enter ship mode, and then registers each descriptor in `bd71815_regulators`. LDO4 alone receives `config.ena_gpiod`; the rest use register enable bits. Device tree parsing for each descriptor can program DVS state voltages and enable masks before the regulator is fully exposed.

State and persistence behavior: The persistent state is in PMIC registers for voltage selectors, enable bits, DVS state selection, ramp settings, WLED current, and ship-mode restart control. BUCK1/BUCK2 use `_H` and `_L` selector registers. If DT specifies hardware DVS levels, `buck12_set_hw_dvs_levels()` may copy the currently selected low value into the high register, switch to the high register, program DVS levels, and enable hardware state based voltage control. Runtime voltage changes then update only RUN voltage when hardware state mode is active.

Dependencies and integration points: The driver uses ROHM MFD headers, `rohm-generic` DVS helpers, the regulator core, OF regulator parsing, GPIO descriptors, and platform ID `"bd71815-pmic"`. It expects its platform device to be created by the parent PMIC/MFD and uses the parent device for regmap and firmware properties.

Risks: BUCK1/BUCK2 have complex register selection semantics; wrong DVS DT properties can move control to the PMIC state machine and make software voltage changes ignore ramp behavior for non-RUN states. `ldolpsr_dvs` uses the same on masks as `dvref_dvs`, which should be checked against hardware definitions. The LED current workaround implies a hardware side effect that tests must preserve. Probe globally disables restart-to-ship-mode behavior, which affects system power behavior beyond regulator registration.

Test signals: Exercise DT DVS parsing for all supported states, BUCK1/BUCK2 active/inactive selector switching, ramp delay programming, LDO4 GPIO enable, WLED current changes with enable-state preservation, regmap failure paths, and registration count `BD71815_REGULATOR_CNT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd71815-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd71828-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bd71828-regulator.c

Purpose: This driver supports ROHM BD71828 and BD72720 PMIC regulator blocks. It registers table-driven buck and LDO descriptors, handles DVS voltage programming from device tree, applies initial mode-control writes that select I2C/register control, and implements a special BD72720 BUCK10 mode where voltage control is removed when BUCK10 follows LDO headroom.

Important APIs, types, and functions: `struct bd71828_regulator_data` contains the descriptor, `rohm_dvs_config`, and optional register initialization array. `struct reg_init` captures one masked write. `buck_set_hw_dvs_levels()` calls `rohm_regulator_set_dvs_levels()` for descriptors with state voltages. `bd71828_ldo6_parse_dt()` interprets DVS voltage properties as state enable/disable for fixed-voltage LDO6. `bd72720_buck10_ldon_head_mode()` parses `rohm,ldon-head-microvolt`, swaps BUCK10 ops to `bd72720_buck10_ldon_head_op`, and writes LDON_HEAD bits.

Control flow: `bd71828_probe()` gets the parent regmap and checks the platform chip type. For BD72720 or BD71828 it duplicates the relevant static regulator data using `devm_kmemdup()` so probe-time descriptor mutation is instance-local. BD72720 first parses BUCK10 LDON_HEAD mode under the parent `regulators` node. Probe then registers every descriptor with the regulator core and runs each descriptor's `reg_inits` masked writes after registration.

State and persistence behavior: Regulator state lives in PMIC enable, voltage, mode, ramp, and DVS-state registers. BD71828 DVS-capable bucks default their DVS control bits to I2C/register control through `bd71828_buck*_inits`. BD72720 disables RUN-level GPIO control for BUCK1 and LDO1 by default. BUCK10 may become enable/ramp-only when LDON_HEAD is configured, leaving automatic voltage adjustment to the PMIC.

Dependencies and integration points: The file depends on `rohm-bd71828.h`, `rohm-bd72720.h`, `rohm_regulator_set_dvs_levels()`, OF regulator nodes, regmap, and regulator core helpers for linear ranges, ramp delay, and voltage-time calculation. Platform IDs are `"bd71828-pmic"` and `"bd72720-pmic"`.

Risks: Most behavior is descriptor-table driven, so incorrect masks or range counts can affect rails silently. BD72720 has documented unsupported RUN0-RUN3 GPIO sub-state functionality; DT users requesting those modes will not get full support. BUCK10 LDON_HEAD parsing assumes a `buck10` child and clamps values above 300 mV with only a warning. Running `reg_inits` after registration means machine constraints may be applied before the final control-mode writes.

Test signals: Cover BD71828 and BD72720 probe selection, DVS DT parsing for run/idle/suspend/LPSR, fixed LDO6 enable-state parsing from zero/nonzero voltage properties, BUCK10 LDON_HEAD absent/present/clamped cases, post-registration initialization writes, ramp delay selectors, and failure paths for missing `regulators` node or regmap errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd71828-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd718x7-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bd718x7-regulator.c

Purpose: This driver registers ROHM BD71837 and BD71847 regulators and handles their dual software-control versus PMIC-hardware-state control model. It also supports DVS state voltages, ramp rates, voltage protection toggles, board-specific feedback-loop voltage scaling, and reset target programming.

Important APIs, types, and functions: `BD718XX_OPS()` creates paired regulator ops: one for software enable/disable and one for hardware-state control where `.is_enabled` is inferred. `voltage_change_prepare()` and `voltage_change_done()` temporarily mask LDO voltage monitoring while raising enabled LDO voltage. `bd718x7_set_*_uvp()` and `bd718x7_set_buck_ovp()` map regulator core protection calls to mask registers. `mark_hw_controlled()`, `setup_feedback_loop()`, and `get_special_regulators()` parse regulator child nodes for `rohm,no-regulator-enable-control` and `rohm,fb-pull-up-microvolt`. `buck_set_hw_dvs_levels()` delegates DVS properties to ROHM helpers.

Control flow: `bd718xx_probe()` selects the BD71837 or BD71847 static descriptor table and the matching software/hardware ops arrays. It unlocks PMIC regulator/power-sequence registers, optionally changes reset transitions from SNVS to READY unless `rohm,reset-snvs-powered` is set, parses special regulator DT settings, then registers all regulators. For each regulator it chooses hardware-control ops when requested by DT; otherwise it chooses software-control ops. After registration and constraints application it may write the descriptor's `init` bits to take register control, except when SNVS reset handling and always-on/boot-on constraints make that unsafe. It then applies any additional init writes.

State and persistence behavior: Persistent state is in PMIC selector, enable, ramp, lock, transition, voltage-monitor mask, and control-selection bits. Descriptor state is also mutated in memory: ops pointers are assigned per probe, and feedback-loop support can replace linear ranges with recalculated device-managed ranges. BD71837 LDO5/LDO6 additional init masks voltage monitors to avoid false emergency-state entry during shutdown sequencing.

Dependencies and integration points: The file integrates with the ROHM BD718x7 MFD header, regulator core, OF regulator constraints, ROHM DVS helpers, and regmap. Supply relationships are encoded for some LDOs, such as BD71847 LDO6 supplied by buck5 and BD71837 LDO5/LDO6 supplied by buck6/buck7.

Risks: The code mutates static global descriptor arrays for ops and feedback ranges, and comments acknowledge multi-PMIC systems may require per-instance copies. Hardware-control mode uses assumed RUN-state status for many regulators, so `.is_enabled` is approximate. Feedback-loop scaling is arithmetic-sensitive and rejects LDOs but still changes descriptor voltage ranges. Reset transition changes can alter platform boot/poweroff behavior. Voltage monitor masking around LDO increases relies on a fixed 1 ms sleep.

Test signals: Test both chip tables, software versus hardware-control DT flags, `rohm,reset-snvs-powered`, DVS parsing, feedback-loop resistor scaling and invalid values, protection enable/disable calls, voltage raises on enabled LDOs with mask re-enable, SNVS always-on/boot-on branch, and BD71837 LDO5/LDO6 shutdown-mask initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd718x7-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd9571mwv-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bd9571mwv-regulator.c

Purpose: This driver registers voltage monitor/control entries for ROHM BD9571MWV-M and BD9574MWF-M PMICs. BD9571 exposes VD09, VD18, VD25, VD33, and DVFS regulators or monitors; BD9574 exposes DVFS only. The file also manages optional DDR backup power behavior across suspend/resume and through a sysfs `backup_mode` attribute.

Important APIs, types, and functions: `struct bd9571mwv_reg` stores the regmap and backup-mode configuration derived from device tree. `BD9571MWV_REG()` builds linear regulator descriptors. `bd9571mwv_avs_get_moni_state()` reads the AVS monitor state used to select the active VD09 VID register. `bd9571mwv_avs_set_voltage_sel_regmap()` and `_get_voltage_sel_regmap()` operate on the AVS VID register selected by monitor state. `bd9571mwv_reg_set_voltage_sel_regmap()` writes DVFS set VID. `backup_mode_show()` and `backup_mode_store()` expose backup mode when sleep PM is enabled.

Control flow: Probe allocates private state, gets the parent regmap, sets the child OF node from the parent, registers all applicable descriptors, and then reads device-tree properties `rohm,ddr-backup-power`, `rohm,rstbmode-level`, and `rohm,rstbmode-pulse`. It rejects invalid backup-power bitfields and mutually exclusive reset-mode properties. If backup power is configured and `CONFIG_PM_SLEEP` is enabled, it creates `backup_mode`; pulse mode enables backup mode by default, while level mode expects user control.

State and persistence behavior: Voltage selector state is stored in PMIC VID registers. Backup mode state is partially driver-held (`bkup_mode_enabled`, saved mode byte) and partially persistent in `BD9571MWV_BKUP_MODE_CNT`. Suspend saves current backup mode and, in pulse mode, writes keep-on bits before sleep. Resume restores the saved value. In level mode the sysfs store path writes keep-on bits immediately when toggled.

Dependencies and integration points: The driver depends on `rohm-generic` chip IDs, `bd9571mwv.h` registers, regmap, regulator core, platform IDs, OF properties, and optional PM sleep. It uses devm regulator registration and platform driver remove only to remove sysfs when PM sleep support compiled it in.

Risks: The AVS VD09 path chooses a VID register based on monitor state at access time, so a state transition between get/set assumptions can surprise callers. Backup mode sysfs exists only under PM sleep builds and only when a nonzero keep-on mask is configured. `bdreg->regmap` is not explicitly checked for NULL before use. Backup mode property validation only checks bit mask validity, not board-level safety.

Test signals: Cover BD9571 versus BD9574 registration filtering, AVS monitor-selected register reads/writes, DVFS set VID writes, invalid backup-power values, conflicting reset-mode DT properties, sysfs backup mode toggling in level mode, suspend/resume save/restore in pulse mode, and no-backup-power paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd9571mwv-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd9576-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bd9576-regulator.c

Purpose: This driver supports ROHM BD9576MUF and BD9573MUF regulators. It registers six mostly fixed or tune-readable outputs, adds BD9576-only protection configuration and IRQ notification support, supports optional VOUT1 GPIO control, and adapts DDR output voltage from board properties.

Important APIs, types, and functions: `struct bd957x_regulator_data` extends each descriptor with protection ranges, notification flags, IRQ configuration registers, and the registered `rdev`. `struct bd957x_data` stores shared regmap and regulator data. Voltage listing is custom in `bd957x_list_voltage()` and `bd957x_vout34_list_voltage()` because selector bit 7 changes sign or table half. `bd9576_set_ocp()`, `bd9576_set_uvp()`, `bd9576_set_ovp()`, and `bd9576_set_tw()` implement regulator protection callbacks. `bd9576_uvd_handler()`, `bd9576_ovd_handler()`, and `bd9576_thermal_handler()` translate PMIC IRQ status bits into regulator error states.

Control flow: Probe gets the parent regmap, optionally acquires `rohm,vout1-en` GPIO when `rohm,vout1-en-low` is present, mutates VDDDR fixed voltage based on `rohm,ddr-sel-low`, selects BD9573 or BD9576 ops arrays, and registers every regulator. For BD9576 it collects rdev arrays and installs regulator IRQ helpers for named UVD, OVD, and thermal IRQs. Missing non-deferred IRQ helpers only warn, so basic regulator registration can still succeed.

State and persistence behavior: Regulator enable and tune status are PMIC-backed and mostly read-only from this driver. Protection configuration writes threshold selector registers, while driver memory records whether each protection maps to WARN or ERR notification. The static global `bd957x_regulators` is mutated at probe for regmap, ops, DDR voltage, GPIO-derived config, and protection flags. IRQ helper `opaque` stores the last status bits to decide whether re-enable should keep IRQs suppressed.

Dependencies and integration points: The file depends on the ROHM BD957x MFD, regulator core protection and IRQ-helper APIs, regmap, platform named IRQs, GPIO descriptors, OF/device properties, and linear-range helpers. Platform IDs distinguish `"bd9573-regulator"` from `"bd9576-regulator"`.

Risks: Static mutable `bd957x_regulators` is not instance-safe for multiple PMICs, and comments acknowledge the limitation. The code uses UVD fields for VOUTS1 over-current warning, which is compact but easy to misinterpret. WARN and ERR cannot be supported simultaneously per protection type; the first or stronger configuration wins with warnings. GPIO mode errors out if the control GPIO is not provided. IRQ registration warnings can hide missing protection notifications.

Test signals: Test BD9573 read-only behavior versus BD9576 protection behavior, VOUT1 GPIO required/absent cases, DDR select property, custom voltage listing sign/table branches, OCP with internal and external FET resistance, WARN/ERR mismatch handling, IRQ handlers for UVD/OVD/thermal bit mapping, IRQ re-enable with unchanged status, and probe behavior with missing or deferred named IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd9576-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd96801-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bd96801-regulator.c

Purpose: This driver supports ROHM BD96801, BD96802, BD96805, and BD96806 scalable PMIC regulator blocks. It intentionally implements a basic feature subset: regulator registration, voltage listing/tuning, keep-on-standby bits, and IRQ notification wiring, while leaving STBY-state safety limit programming unsupported.

Important APIs, types, and functions: `struct bd96801_regulator_data` combines each descriptor with initial-voltage ranges, LDO mode metadata, per-regulator IRQ descriptors, and LDO thermal error mapping. `struct bd96801_pmic_data` is the per-chip template. `bd96801_list_voltage_lr()` adds the cached buck initial voltage to a tune selector range. `buck_get_initial_voltage()` reads initial VOUT from hardware and caches it. `get_ldo_initial_voltage()` switches LDO descriptors to table ops when hardware is in SD or DDR mode. `bd96801_walk_regulator_dt()` applies `rohm,keep-on-stby`. IRQ helpers include `bd96801_rdev_intb_irqs()`, `bd96801_rdev_errb_irqs()`, and `bd96801_global_errb_irqs()`.

Control flow: Probe selects a template pointer from the platform ID, duplicates it, duplicates mutable IRQ info arrays for each regulator, obtains the parent regmap, detects whether parent interrupt names include `errb`, walks the regulator DT nodes to initialize voltage metadata and keep-on-STBY bits, registers every regulator, attaches INTB handlers for configured per-regulator protections, optionally attaches per-regulator and global ERRB handlers, and attaches a shared LDO core-thermal handler when any LDO requested temperature notification.

State and persistence behavior: Regulator enable bits are inverted in `BD96801_REG_ENABLE`. Buck voltage is modeled as immutable initial voltage plus a runtime tuning selector; the initial value is cached at probe. LDO mode is detected from hardware mode bits and can alter descriptor ops, voltage table, selector mask, and selector register. Keep-on-standby state is written to `BD96801_ALWAYS_ON_REG`. IRQ info is copied per instance so err/warn config can be mutated without changing static templates.

Dependencies and integration points: The driver depends on ROHM generic and BD96801 MFD headers, regmap, OF regulator nodes, platform named IRQs, regulator IRQ helpers, and regulator core ramp/timing helpers. Platform IDs carry the data template pointer rather than a simple enum.

Risks: `devm_kmemdup()` copies `sizeof(bd96801_data)` regardless of selected template, which is safe only because smaller templates share the same struct type but is worth preserving intentionally. The file has no STBY synchronization for changing safety limits, so DT or future code must not imply that support exists. Missing named IRQs for configured INTB paths are fatal, while absent ERRB/global IRQs are skipped. Initial voltage cache can become stale if another agent changes initial VOUT after probe.

Test signals: Cover all four chip IDs, two-regulator and seven-regulator templates, buck initial-voltage cache and tune voltage listing for BD96801 and BD96805 ranges, LDO normal/SD/DDR mode detection, keep-on-STBY writes, INTB IRQ registration for per-regulator protections, ERRB detection from parent `interrupt-names`, global ERRB event fan-out, LDO thermal mapping, and absent/failing IRQ/regmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bd96801-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bq257xx-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/bq257xx-regulator.c

Purpose: This compact driver exposes the OTG VBUS output of TI BQ257xx charger MFD devices as a regulator. It supports VBUS voltage selection, current-limit programming, register-backed enable, and optional external GPIO assertion for OTG enable.

Important APIs, types, and functions: `struct bq257xx_reg_data` stores the registered regulator, optional `otg_en_gpio`, and a mutable copy of the descriptor. `bq25703_vbus_get_cur_limit()` reads `BQ25703_OTG_CURRENT` and extracts the current field with `FIELD_GET`. `bq25703_vbus_set_cur_limit()` validates min/max values, rounds max current to register steps, rejects rounding below the requested minimum, and writes the field with `FIELD_PREP`. `bq25703_vbus_enable()` and `_disable()` drive the optional GPIO before delegating to regmap enable helpers. `bq257xx_reg_dt_parse_gpio()` descends into `regulators/vbus` to fetch `enable-gpios`.

Control flow: Probe sets the child OF node from the parent device, allocates private data, copies `bq25703_vbus_desc`, stores driver data, parses the optional GPIO, fills `regulator_config` with the platform device, original OF node, parent regmap, and driver data, then registers one regulator. Missing parent regmap aborts probe; GPIO `-ENOENT` is treated as register-only operation while other GPIO errors are logged and leave the pointer as an error object.

State and persistence behavior: Voltage selection, current limit, and OTG enable are stored in charger registers. The optional GPIO is driven low by default when acquired and is set high or low around regulator enable/disable. There is no suspend/resume or interrupt state. Descriptor state is copied into private memory before registration, allowing future per-device mutation.

Dependencies and integration points: The file depends on `linux/mfd/bq257xx.h` for register definitions and field masks, regulator core regmap helpers, OF regulator child nodes, GPIO descriptors, regmap, and platform-device creation by the charger MFD. It registers as `"bq257xx-regulator"`.

Risks: `bq257xx_reg_dt_parse_gpio()` logs non-ENOENT GPIO errors but does not clear `otg_en_gpio`; enable/disable later treat any non-null error pointer as a valid GPIO and may dereference an error pointer. Current-limit validation checks `max_uA < 0` but not `min_uA < 0`, relying on rounding logic to reject problematic values. The current register write uses `regmap_write()` instead of update-bits, so unrelated bits in `BQ25703_OTG_CURRENT` would be overwritten if any exist.

Test signals: Test register-only mode, valid GPIO mode, non-ENOENT GPIO error handling, voltage selector get/set through regmap helpers, current limit boundaries and rounding rejection, max over range, negative inputs, GPIO sequencing on enable/disable, parent regmap absence, and DT traversal when `regulators` or `vbus` child nodes are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/bq257xx-regulator.c -->
