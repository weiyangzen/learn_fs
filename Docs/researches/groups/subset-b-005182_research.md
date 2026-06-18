# subset-b-005182 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6359-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6359-regulator.c

Purpose: implements the MediaTek MT6359/MT6359P PMIC regulator platform driver. It registers the SoC's buck, fixed LDO, table LDO, and linear LDO rails against the Linux regulator framework using the parent MT6397 MFD regmap.

Important APIs/types/functions: `struct mt6359_regulator_info` extends `regulator_desc` with status, forced-PWM, and low-power-mode registers. Descriptor macros `MT6359_BUCK`, `MT6359_LDO_LINEAR`, `MT6359_LDO`, `MT6359_REG_FIXED`, and `MT6359P_LDO1` populate the MT6359 and MT6359P rail tables. Ops are split across `mt6359_volt_linear_ops`, `mt6359_volt_table_ops`, `mt6359_volt_fixed_ops`, and `mt6359p_vemc_ops`. Special functions include `mt6359_get_status()`, `mt6359_regulator_get_mode()`, `mt6359_regulator_set_mode()`, and MT6359P VEMC selector accessors that unlock TMA and select VEMC_VOSEL_0 or VEMC_VOSEL_1 by hardware trap.

Control flow: probe reads `MT6359P_HWCID` from the parent regmap, chooses the MT6359P descriptor table for chip revisions at or above `MT6359P_CHIP_VER`, then loops through `MT6359_MAX_REGULATOR` and registers each descriptor with `devm_regulator_register()`. Runtime voltage and enable operations are delegated to regulator regmap helpers; buck mode changes write force-PWM and low-power bits, including a 100 us delay when returning from idle to normal.

State and persistence: persistent state is PMIC register state: enable bits, voltage selectors, status bits, force-PWM bits, low-power bits, and TMA-protected VEMC selector registers. Driver state is static descriptor data plus per-rdev `driver_data`; no remove/shutdown restoration is implemented.

Dependencies and integration: depends on the MT6397 MFD core, MT6359/MT6359P register headers, regmap, platform-device binding `mt6359-regulator`, regulator core DT matching under `regulators`, and `mt6359_map_mode()` for DT mode constraints.

Risks and test signals: chip revision detection drives different voltage tables and register addresses, especially VCORE, VGPU11, VRFCK, VEMC, and enable/status registers. `mt6359_regulator_get_mode()` returns raw negative regmap errors through an unsigned mode API. The VEMC TMA unlock path must always re-lock on successful selector writes. Test MT6359 and MT6359P probe, all voltage tables with sparse zero entries, status reads from DA registers, mode transitions FAST/NORMAL/IDLE, invalid DT modes, and VEMC trap 0/1/error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6359-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6360-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6360-regulator.c

Purpose: implements the MediaTek/Richtek MT6360 PMIC regulator platform driver for two bucks and six LDOs, including fault-event IRQ notification.

Important APIs/types/functions: `struct mt6360_regulator_desc` wraps a `regulator_desc` with mode/status registers and per-rail IRQ tables. `mt6360_regulator_ops` provides linear-range voltage listing, regmap enable/disable, selector get/set, status, and mode callbacks. Event handlers `mt6360_pgb_event_handler()`, `mt6360_oc_event_handler()`, `mt6360_ov_event_handler()`, and `mt6360_uv_event_handler()` translate named IRQs to regulator notifier events. `MT6360_REGULATOR_DESC` encodes rail metadata, supply names, DT names, voltage ranges, and off-on delay.

Control flow: probe allocates private state, obtains the parent regmap, then registers each descriptor with `config.dev` set to the parent and `config.regmap` set to the MFD regmap. After each regulator is registered, `mt6360_regulator_irq_register()` looks up every named platform IRQ for that rail and requests a threaded handler. Runtime mode mapping accepts NORMAL, LP/IDLE, and ULP/STANDBY; status reads a per-rail state bit.

State and persistence: all meaningful state lives in hardware registers for enable, selector, mode, and state. The driver keeps only static descriptor tables and the parent regmap pointer. IRQ handlers do not latch local state; they emit notifications from hardware events.

Dependencies and integration: depends on the parent MT6360 MFD exposing a regmap and named interrupts such as `buck1_oc_evt` and `ldo5_pgb_evt`; DT regulator nodes are under the singular `regulator` container and use `mediatek,mt6360-regulator` binding constants for modes.

Risks and test signals: probe fails if any named IRQ is absent, so platform IRQ naming is part of the ABI. `mt6360_regulator_get_mode()` and status callbacks return regmap errors through unsigned/int regulator callback conventions. The LDO voltage ranges have many repeated plateau selectors, so selector-to-voltage coverage matters. Test each IRQ-to-event mapping, missing IRQ handling, buck and LDO mode writes, status-bit reads, off-on delay for LDO3/LDO5, and DT initial/allowed modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6360-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6363-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6363-regulator.c

Purpose: implements the MediaTek MT6363 PMIC regulator driver over SPMI, covering seven main bucks, VS rails, many calibrated LDOs, SRAM rails, mode/load control, and optional over-current protection interrupts.

Important APIs/types/functions: `struct mt6363_regulator_info` extends descriptors with LP/FCCM registers, hardware-voted LP registers, load-threshold data, original operation-mode backups, delayed OCP work, and IRQ mapping. Macros `MT6363_BUCK`, `MT6363_LDO_LINEAR_OPS`, `MT6363_LDO_LINEAR_CAL_OPS`, and variants build the rail table. Key functions are set/clear enable helpers, `mt6363_regulator_get_mode()`, `mt6363_regulator_set_mode()`, `mt6363_regulator_set_load()`, `mt6363_vemc_set/get_voltage_sel()`, `mt6363_va15_set_voltage_sel()`, `mt6363_set_ocp()`, `mt6363_spmi_register_regmap()`, and `mt6363_regulator_probe()`.

Control flow: probe creates a child SPMI device/regmap using the `reg` base property, performs a dummy wake read, finds the IRQ parent domain, maps each hardware OCP interrupt to a virtual IRQ, initializes delayed work, registers every regulator, and backs up operation-mode registers where DRMS/load control is supported. Mode control sets FCCM through a BUCK_TOP unlock sequence, toggles LP bits for idle, and rejects FAST on rails without `modeset_reg`. OCP setup requests the mapped IRQ only when a consumer enables regulator over-current protection; the ISR disables the IRQ, notifies if the rail is enabled, and re-enables after 10 ms.

State and persistence: persistent PMIC state includes enable registers, LP/FCCM mode bits, calibrated voltage range/selector registers, trap-selected VEMC registers, and operation enable/config bytes. The driver caches original operation settings for load-based mode restoration and stores IRQ mappings in the static rail table.

Dependencies and integration: depends on SPMI, regmap SPMI extended access, OF IRQ domains, MediaTek MT6363 register definitions, regulator DT mode mapping, delayed work, and parent SPMI identity. Supply names encode internal dependencies such as `vsys-vbuck1` and `vs2-ldo1`.

Risks and test signals: this driver has several protected-write paths that must lock/unlock even on errors. VEMC trap handling chooses a different selector mask/register interpretation and `mt6363_vemc_get_voltage_sel()` has delicate range-selector math. OCP IRQ mappings are created for all rails even if a rail later never enables OCP. Test SPMI regmap creation, sleep-mode wake behavior, IRQ-domain mapping, buck unlock failures, mode transitions, load threshold behavior, VA15 efuse mirror writes, VEMC trap 0/1/>1, delayed OCP re-enable, and probe cleanup actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6363-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6370-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6370-regulator.c

Purpose: implements the MT6370 regulator subdriver for display bias boost/output rails and a vibrator LDO, with fault reporting and optional external GPIO enable control.

Important APIs/types/functions: `struct mt6370_priv` stores the device, regmap, registered rdevs, and whether external control has been requested. `mt6370_regulator_descs[]` describes `dsvbst`, `dsvpos`, `dsvneg`, and `vibldo`. Ops sets `mt6370_dbvboost_ops`, `mt6370_dbvout_ops`, and `mt6370_ldo_ops` expose selector, enable, bypass, active discharge, ramp, and error-flag callbacks. `mt6370_of_parse_cb()` attaches optional enable GPIOs and enables PMIC external-control mode.

Control flow: probe obtains the parent regmap, registers all four regulators, stores rdev pointers, then requests six named platform IRQs for SCP/OCP events. Runtime error flags read `MT6370_REG_DB_STAT` or `MT6370_REG_LDO_STAT` and map bits to `REGULATOR_ERROR_UNDER_VOLTAGE` or `REGULATOR_ERROR_OVER_CURRENT`. IRQ handlers emit regulator notifier events for the affected rdev.

State and persistence: hardware owns voltage selectors, bypass state, enable state, active discharge bits, ramp settings, fault status, and external-control enable. Driver state tracks whether any output rail uses an enable GPIO; when the first GPIO is found it sets `use_external_ctrl` after assigning the GPIO, while the next external rail may actually set `MT6370_DBEXTEN_MASK`.

Dependencies and integration: depends on parent regmap, platform IRQ names, regulator OF children under `regulators`, optional `enable-gpios`, and regulator core support for `ena_gpiod`. The display-bias outputs share external-control semantics.

Risks and test signals: `platform_get_irq_byname()` return values are not checked before `devm_request_threaded_irq()`. External-control enabling depends on registration order and only happens after `priv->use_external_ctrl` was already true from a previous parse. Fault status bits may be sticky, so error reporting should be validated against hardware clear behavior. Test GPIO/no-GPIO combinations, both display output rails with external pins, all named IRQs, bypass on boost, active discharge for outputs and LDO, ramp tables, and `get_error_flags()` bit mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6370-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6380-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6380-regulator.c

Purpose: implements the MediaTek MT6380 PMIC regulator platform driver for three buck rails and five LDO/fixed rails.

Important APIs/types/functions: `struct mt6380_regulator_info` carries a `regulator_desc`, optional hardware control selector register, and mode-set register/mask. Macros `MT6380_BUCK`, `MT6380_LDO`, and `MT6380_REG_FIXED` define the descriptor table. Ops `mt6380_volt_range_ops`, `mt6380_volt_table_ops`, and `mt6380_volt_fixed_ops` share regmap enable/disable and mode callbacks, with range, table, or fixed voltage listing.

Control flow: probe fetches the parent regmap and registers all `MT6380_MAX_REGULATOR` descriptors. Buck voltages are linear ranges; LDOs use small voltage tables; fixed VPHYLDO reports a single 1.8 V rail. `mt6380_regulator_set_mode()` maps NORMAL to AUTO and FAST to FORCE_PWM by writing each rail's mode bit. `mt6380_regulator_get_mode()` reads back and maps the same bit.

State and persistence: rail enable bits, voltage selectors, and mode bits persist in PMIC registers. The driver has no dynamic state beyond the static descriptor table and per-rdev driver-data pointer. No shutdown or remove programming is performed.

Dependencies and integration: depends on a parent MFD/platform regmap, `linux/regulator/mt6380-regulator.h` IDs, DT compatible `mediatek,mt6380-regulator`, and regulator core helpers. Unlike many MediaTek PMIC drivers here, descriptors do not set `regulators_node`, so matching relies on the core's default node search behavior.

Risks and test signals: probe does not check for a missing parent regmap before passing it to regulator registration. Fixed regulator descriptors set `min_uV` but not `fixed_uV`, while using `regulator_list_voltage_linear`. Mode callbacks are exposed for LDOs and fixed rails as well as bucks. Test missing parent regmap, all rail selector masks and tables, mode set/get on every rail, DT matching behavior, and fixed VPHYLDO voltage reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6380-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6397-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6397-regulator.c

Purpose: implements the MediaTek MT6397 PMIC regulator driver for CPU/GPU/core bucks and numerous analog/digital LDOs through the MT6397 MFD regmap.

Important APIs/types/functions: `struct mt6397_regulator_info` extends descriptors with status query masks, hardware-voted VSEL register selection, VSEL control register/mask, and buck mode registers. Descriptor macros create buck, table LDO, and fixed-regulator entries. Key functions are `mt6397_map_mode()`, `mt6397_regulator_set_mode()`, `mt6397_regulator_get_mode()`, `mt6397_get_status()`, `mt6397_set_buck_vosel_reg()`, and `mt6397_regulator_probe()`.

Control flow: probe first calls `mt6397_set_buck_vosel_reg()` to read each buck's VSEL control bit and redirect `desc.vsel_reg` to the active `vselon_reg` when hardware control is selected. It then reads `MT6397_CID`, logs the chip ID, swaps the VGP2 voltage table for revision `MT6397_REGULATOR_ID91`, and registers each regulator. Buck mode changes write AUTO or FORCE_PWM bits; status reads the descriptor enable register and checks `qi`.

State and persistence: PMIC registers persist enable/status, voltage selector, VSEL source selection, and mode bits. The driver mutates the global descriptor table at probe time for active VSEL registers and revision-specific VGP2 voltages.

Dependencies and integration: depends on MT6397 MFD parent data, MT6397 register and regulator ID headers, regmap, regulator OF matching under compatible `mediatek,mt6397-regulator`, and DT binding mode constants.

Risks and test signals: descriptor mutation is global, so multi-instance assumptions would be unsafe even if the hardware is normally singleton. The VSEL-source read must happen before registration or voltage ops target the wrong register. Revision-specific VGP2 values can affect board constraints. Test all bucks with VSELCTRL on/off, chip ID revision 0x91 and default, sparse LDO table mapping, status `qi` masks for bucks versus LDOs, and mode invalid/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6397-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mtk-dvfsrc-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mtk-dvfsrc-regulator.c

Purpose: exposes MediaTek DVFS Resource Collector voltage performance levels as regulator devices for VCORE and, on some SoCs, VSCP.

Important APIs/types/functions: `struct dvfsrc_regulator_pdata` carries a per-compatible descriptor array. `MTK_DVFSRC_VREG` creates table-voltage descriptors using `dvfsrc_vcore_ops`. `dvfsrc_get_cmd()` maps regulator IDs to `MTK_DVFSRC_CMD_VCORE_LEVEL` or `MTK_DVFSRC_CMD_VSCP_LEVEL`. `dvfsrc_set_voltage_sel()` calls `mtk_dvfsrc_send_request()`, and `dvfsrc_get_voltage_sel()` calls `mtk_dvfsrc_query_info()`.

Control flow: probe obtains match data for the SoC, then registers each descriptor in the table. Runtime selector writes do not touch a local regmap; they send a DVFSRC command to the grandparent DVFSRC device. Runtime reads query the same command and return the DVFSRC level selector. Voltage tables differ for MT6873/8192, MT6893, MT8183, MT8195, and MT8196.

State and persistence: the regulator framework stores no voltage state here. DVFSRC firmware/hardware owns the active level, and this driver is a command bridge. Static tables define allowed selector-to-microvolt mapping for consumers.

Dependencies and integration: depends on the MediaTek DVFSRC SoC API, platform-device hierarchy where the regulator device's parent has a DVFSRC parent, regulator OF matching, and compatible match data. It has no enable/disable operations.

Risks and test signals: parent hierarchy assumptions are hard-coded in `to_dvfsrc_dev()`. Selector values are passed directly as DVFSRC levels, so voltage table order must match firmware contracts. Test each compatible's table size and rails, VCORE-only MT8183/MT8196 cases, invalid regulator IDs, DVFSRC request/query error propagation, and consumers that expect enable/is_enabled support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mtk-dvfsrc-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/of_regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/of_regulator.c

Purpose: provides the regulator framework's Open Firmware/device-tree parsing and lookup helpers. It converts regulator DT nodes into `regulator_init_data`, resolves supplies to provider rdevs, validates coupled regulator topology, and supports bulk acquisition from `*-supply` properties.

Important APIs/types/functions: exported functions include `of_get_regulator_init_data()`, `of_regulator_match()`, `of_regulator_dev_lookup()`, `of_regulator_get()`, `of_regulator_get_optional()`, `of_get_n_coupled()`, `of_check_coupling_data()`, `of_parse_coupled_regulator()`, and `of_regulator_bulk_get_all()`. Internal helpers parse protection limits, constraints, suspend states, init nodes, child supply phandles, and supply-name property syntax.

Control flow: `of_get_regulation_constraints()` reads voltage/current ranges, load, status-change permissions, bypass/DRMS flags, ramp and settling times, active discharge, protection limits, initial/allowed modes via `desc->of_map_mode`, coupled-regulator spread arrays, and standby/mem/disk suspend subnodes. `of_regulator_match()` walks child nodes, matches by `regulator-compatible` or node name, parses init data, and stores node references with devres cleanup. Provider lookup finds a supply phandle, then class-searches registered regulators by OF node, returning defer when a node exists but no rdev is registered.

State and persistence: the file owns no persistent hardware state. It allocates devm init-data and devres-managed node references, fills constraint structures consumed by registered regulator devices, and relies on regulator core class devices for lookup lifetime.

Dependencies and integration: depends on OF core, regulator core internals, device class lookup, devres, and common regulator binding property names. It is a central integration point for almost every DT-backed regulator driver in this subset.

Risks and test signals: parsing is permissive in places: invalid modes log errors but do not fail constraints, missing coupled max-spread arrays are not checked after read, and `of_check_coupling_data()` calls phandle counting on `c_node` even after a missing phandle path sets `ret = false`. Recursive child supply lookup may find nested supplies outside the immediate consumer. `of_regulator_bulk_get_all()` uses `regulator_get()` by derived property names and must unwind cleanly on partial failure. Test all binding properties, ambiguous settling times, suspend subnodes, protection limit semantics where value `1` means enable, deprecated `regulator-compatible`, full-name matching, provider probe deferral, coupled-regulator mismatch cases, and bulk get error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/of_regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/palmas-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/palmas-regulator.c

Purpose: implements regulator support for TI Palmas/TWL603x/TPS65913/TPS65914/TPS80036/TPS659038 and TPS65917 PMIC families, including SMPS, LDO, external resource regulators, external sleep request control, and DT-to-platform-data conversion.

Important APIs/types/functions: static chip data includes `palmas_generic_regs_info`, `tps65917_regs_info`, sleep requestor tables, OF match tables, and driver-data structures. Ops cover normal and external-control SMPS, SMPS10 boost/bypass, LDO/LDO9, external resources, and TPS65917-specific variants. Core functions include register access wrappers, `palmas_set_mode_smps()`, `palmas_smps_set_ramp_delay()`, `palmas_regulator_config_external()`, `palmas_smps_init()`, `palmas_ldo_init()`, `palmas_extreg_init()`, registration functions for Palmas and TPS65917 SMPS/LDOs, `palmas_dt_to_pdata()`, and `palmas_regulators_probe()`.

Control flow: probe selects chip driver data from OF, allocates platform and PMIC state, applies TPS659038 register quirks, parses the `regulators` child with `of_regulator_match()`, reads SMPS slaving configuration, then calls family-specific SMPS and LDO registration. Registration skips rails unavailable due to slaving or missing features, initializes sleep/warm-reset/range/external-control settings before registration where required, configures descriptor voltage ranges and ops dynamically, and registers each regulator against the parent regmap.

State and persistence: hardware state includes SMPS/LDO/resource control registers, voltage selector ranges, sleep-mode bits, warm-reset bits, external request routing, and slaving configuration. Driver state caches current SMPS modes, range selection, ramp delays, slaving flags, descriptor data, and parsed per-regulator init data.

Dependencies and integration: depends on the Palmas MFD, `palmas_ext_control_req_config()`, multiple regmap bases, regulator DT parsing, OF compatibles for several PMICs, and platform data fields in `linux/mfd/palmas.h`. It is registered with `subsys_initcall` for early availability.

Risks and test signals: this file mutates global register-info and driver-data for TPS659038, which is risky if multiple variants could coexist. `palmas_dt_to_pdata()` logs parse errors but returns success when `of_regulator_match()` fails, potentially continuing with partial/no constraints. Dynamic descriptor setup must happen before registration because ranges and ops depend on live hardware bits and external-control DT. Test every compatible family, SMPS12/123 and SMPS45/457 slaving, SMPS10 feature absence/presence, TPS65917 differences, LDO8 tracking, LDO6 vibrator enable time, roof-floor external requestor routing, warm-reset/sleep properties, range selection, and failed register reads during init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/palmas-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pbias-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pbias-regulator.c

Purpose: implements TI OMAP/DRA7 PBIAS regulators for MMC/SIM I/O bias voltage selection through a syscon register.

Important APIs/types/functions: `struct pbias_reg_info` describes enable bits, enable mask, disable value, voltage-mode bit, enable time, name, and two-entry voltage table. `struct pbias_of_data` provides the syscon offset for each compatible. `pbias_matches[]` maps child regulator names to static rail data. `pbias_regulator_voltage_ops` uses table voltage listing and regmap selector/enable helpers.

Control flow: probe matches child regulator nodes with `of_regulator_match()`, allocates one descriptor per matched rail, obtains the syscon regmap from the `syscon` phandle, determines the register offset from match data or a legacy memory resource, then fills and registers a descriptor for each matched child. Each descriptor uses the same syscon offset for voltage select and enable control, with rail-specific masks and disable values.

State and persistence: state is the shared SoC control-module/syscon register. The driver keeps no runtime cache; enable and voltage selection persist as register bits managed by regmap helpers.

Dependencies and integration: depends on OF, syscon regmap lookup, platform resources for legacy offset fallback, regulator framework, and OMAP/DRA7 DT child node names such as `pbias_mmc_omap4`.

Risks and test signals: all matched regulators share a single register offset, so masks must be non-overlapping and correct for the SoC. The descriptor pointer is incremented through a contiguous allocation, making `count` and match iteration correctness important. Legacy offset fallback uses `res->start` and warns. Test all compatibles and offsets, both 3.0 V and 3.3 V tables, each enable/disable mask/value, missing syscon phandle, no child matches, partial child matches, and legacy resource fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pbias-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pca9450-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pca9450-regulator.c

Purpose: implements the NXP PCA9450/PCA9451A/PCA9452 PMIC I2C regulator driver, registering buck and LDO regulators, configuring PMIC reset/power timing, handling interrupts, and providing a restart handler.

Important APIs/types/functions: `struct pca9450` stores device, regmap, optional LDO5 SD_VSEL GPIO, chip type, regulator count, IRQ, and SD_VSEL policy. `struct pca9450_regulator_desc` embeds a descriptor plus DVS register metadata. Ops cover DVS bucks with ramp/mode support, non-DVS bucks, normal LDOs, and LDO5 with dynamic high/low selector register access. Key functions include `buck_set_dvs()`, `pca9450_set_dvs_levels()`, `pca9450_buck_set/get_mode()`, `pca9450_ldo5_get_reg_voltage_sel()`, `pca9450_irq_handler()`, `pca9450_i2c_restart_handler()`, `pca9450_of_init()`, and `pca9450_i2c_probe()`.

Control flow: probe selects the regulator table by OF match data, initializes I2C regmap with status registers volatile, reads and validates device ID, registers each regulator while skipping PCA9451A LDO3, requests an optional low-triggered IRQ and unmasks selected fault interrupts, clears BUCK123 preset mode, applies global OF reset/debounce/timing/I2C-level-translator settings, obtains optional LDO5 `sd-vsel` GPIO from the LDO device, records `nxp,sd-vsel-fixed-low`, and registers a sys-off restart handler.

State and persistence: PMIC registers hold regulator enable modes, voltage selectors, DVS run/standby levels, ramp settings, interrupt masks/status, reset behavior, debounce timing, power sequencing, and restart command. Driver state records chip type/count, dynamic LDO5 selector source, and optional GPIO.

Dependencies and integration: depends on I2C, regmap cache, GPIO descriptors, interrupts, sys-off/restart API, regulator OF parsing, NXP PCA9450 headers and DT binding constants. The DVS parse callback consumes regulator child properties `nxp,dvs-run-voltage` and `nxp,dvs-standby-voltage`.

Risks and test signals: `ldo5` is used after registration loop and assumes all selected variants register LDO5 successfully. The property name `npx,pmic-rst-b-debounce-ms` appears misspelled relative to the `nxp,` prefix used elsewhere, which affects DT compatibility. `buck_set_dvs()` leaves `ret` as the last listed voltage when no exact match is found, producing a positive return from an error path. Test each chip compatible and ID mismatch, PCA9451A LDO3 skip, DVS exact/missing/invalid voltages, LDO5 GPIO high/low/fixed-low selector behavior, IRQ mask/status logging, reset and debounce property validation, restart command, and PRESET_EN clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pca9450-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pcap-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/pcap-regulator.c

Purpose: implements the Motorola/EZX PCAP2 regulator platform driver, exposing legacy PCAP voltage rails through regulator descriptors and PCAP MFD bit operations.

Important APIs/types/functions: voltage tables define V1-V10, VAUX1-4, VSIM/VSIM2, VVIB, and SW1/SW2 selector mappings. `struct pcap_regulator` maps each regulator ID to a PCAP register, enable bit, selector bit index, standby bit, and low-power bit. `pcap_regulator_ops` provides table voltage listing, custom selector get/set, and custom enable/disable/is_enabled callbacks using `ezx_pcap_read()` and `ezx_pcap_set_bits()`.

Control flow: the platform driver is registered at `subsys_initcall`. Probe gets the parent PCAP handle, uses `pdev->id` to select one descriptor from `pcap_regulators[]`, passes platform init data as regulator constraints, and registers exactly that rail. Runtime voltage writes reject fixed one-voltage rails and otherwise update selector bits in the mapped PCAP register; enable operations reject rails with `NA` enable bits.

State and persistence: regulator state is entirely in PCAP hardware registers. The standby and low-power bit metadata is present but unused by this driver. No runtime cache or remove-time restoration exists.

Dependencies and integration: depends on the EZX PCAP MFD, platform devices with IDs matching regulator IDs, board/platform init data, and regulator core. It is a non-DT legacy style driver.

Risks and test signals: there is no bounds check on `pdev->id`, so bad platform data can index past `pcap_regulators[]` or `vreg_table[]`. `ezx_pcap_read()` return values are ignored in get/is_enabled paths. Selector masks assume the number of voltages is a power-of-two minus one mask; duplicated voltage table entries may be intentional hardware encodings. Test every valid platform ID, invalid ID handling at platform layer, fixed rails V10/VSIM2, rails with `NA` enable bits, selector read/write masks, and PCAP read/write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/pcap-regulator.c -->
