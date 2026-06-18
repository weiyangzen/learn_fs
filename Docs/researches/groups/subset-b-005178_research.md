# subset-b-005178 Research

Grouped research for `subset-b-005178`. Each section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9062-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9062-regulator.c

Purpose: Implements the Linux regulator subdriver for Dialog/Renesas DA9061 and DA9062 PMIC regulators. It exposes chip buck and LDO rails to the regulator framework using regmap-backed enable, voltage selector, current-limit, mode, suspend, and status operations.

Important APIs, types, and functions: `struct da9062_regulator_info` describes each rail's `regulator_desc` plus regmap fields for mode, suspend enable, sleep mode, suspend sleep, suspend voltage register, and LDO overcurrent event bits. `struct da9062_regulator` stores the runtime descriptor copy, `rdev`, parent `struct da9062`, static info, and allocated `regmap_field` handles. The main operation tables are `da9062_buck_ops` and `da9062_ldo_ops`. Key helpers include `da9062_map_buck_mode()`, buck/LDO `set_mode` and `get_mode`, `da9062_set_suspend_voltage()`, `da9062_suspend_enable()`, `da9062_suspend_disable()`, and `da9062_ldo_lim_event()`.

Control flow: Probe obtains the parent MFD `struct da9062`, selects either `local_da9061_regulator_info` or `local_da9062_regulator_info` based on `chip_type`, allocates a flex-array `struct da9062_regulators`, then iterates over the selected descriptor table. For each rail it copies the descriptor, marks it voltage type/owned by this module, allocates any declared regmap fields, fills `regulator_config` with parent device, regmap, and driver data, and calls `devm_regulator_register()`. If an optional `LDO_LIM` IRQ exists, it requests a threaded handler that reads `DA9062AA_STATUS_D`, maps asserted LDO limit bits to regulator devices, and emits `REGULATOR_EVENT_OVER_CURRENT`.

State and persistence: Runtime state is mostly hardware-backed in PMIC registers and regmap fields. The driver keeps per-rail field handles and descriptor copies for the life of the platform device. Suspend configuration persists by writing alternate VSEL registers and suspend/sleep bits. There is no explicit remove path because all allocations, field handles, IRQs, and registered regulators are devm-managed.

Dependencies and integration points: This file integrates with the DA9062 MFD core, DA9062 register definitions, regulator core helpers, OF regulator matching via descriptor `of_match`/`regulators_node`, and dt-binding mode constants shared with DA9063. It registers as platform driver `da9062-regulators` at `subsys_initcall` with asynchronous probe preference.

Risks and test signals: Test chip-type selection for DA9061 versus DA9062 rail counts and descriptor mappings, buck current-limit table selection, mode translations including invalid modes, suspend voltage selector masking/shifting, optional absence of `LDO_LIM`, and IRQ notification for each LDO limit bit. Regressions are likely if register-field masks from MFD headers change, because descriptor tables depend on computed bit positions and suspend/normal fields sharing the correct registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9062-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9063-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9063-regulator.c

Purpose: Provides the regulator platform driver for DA9063 and DA9063L PMICs. It registers buck and LDO rails, handles DA9063 buck merge modes, supports current-limit overdrive on selected bucks, exposes voltage monitoring enable/disable through regulator protection callbacks, and reports LDO overcurrent events.

Important APIs, types, and functions: `struct da9063_regulator_info` combines a `regulator_desc` with regmap fields for mode, suspend, sleep, suspend sleep, LDO overcurrent, and voltage monitor enable. `struct da9063_dev_model` binds a descriptor table and count to a PMIC model. Descriptor macros `DA9063_LDO()`, `DA9063_BUCK()`, and `DA9063_BUCK_COMMON_FIELDS()` define most rails. Runtime helpers include `da9063_set_xvp()`, `da9063_buck_set_current_limit()`, `da9063_buck_get_current_limit()`, `da9063_check_xvp_constraints()`, `da9063_parse_regulators_dt()`, and `da9063_regulator_probe()`.

Control flow: Probe parses the `regulators` DT child into platform data, selects a model entry for DA9063 or DA9063L, reads `DA9063_REG_CONFIG_H` to discover merged BCORE and BMEM/BIO buck topology, reduces the number of registered regulators accordingly, then walks the descriptor table while skipping inactive individual or merged IDs. For each active rail it allocates declared regmap fields, validates voltage-protection constraints when init data exists, and registers the regulator. Finally it requests the mandatory `LDO_LIM` IRQ and routes status bits in `DA9063_REG_STATUS_D` into regulator overcurrent notifications.

State and persistence: The registered rails are described by copied descriptors and hardware register fields. Current-limit overdrive toggles bits in `DA9063_REG_CONFIG_H`; enabling overdrive happens before lowering the encoded current-limit value, while disabling overdrive happens after programming the normal limit so supply capability is preserved during transitions. Voltage monitor state persists in PMIC monitor registers and can only be enabled/disabled with zero microvolt thresholds. No manual remove path is needed because resources are devm-managed.

Dependencies and integration points: The driver depends on the DA9063 MFD parent, DA9063 register headers, regulator framework regmap helpers, OF regulator matching, and regulator notification constraints for under/over-voltage protection. It registers under `DA9063_DRVNAME_REGULATORS` with asynchronous platform probing.

Risks and test signals: Test merged and unmerged buck configurations, DA9063L exclusion of six DA9063-only LDOs, overdrive current limits above table maximum and rollback paths, invalid XVP constraints where UV/OV severities differ, missing regulator DT nodes, and LDO limit IRQ handling. A high-risk area is the correspondence between descriptor IDs, DT match array indexes, and skip logic in merged modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9063-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9121-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9121-regulator.c

Purpose: Implements the I2C regulator driver for the DA9121 family and related DA9130/DA9131/DA9132, DA9217, DA9220, DA9141, and DA9142 buck converters. It supports one-channel and two-channel variants, variant-specific current limits, runtime PM, GPIO enable integration, regmap caching, event IRQ handling, and optional temperature hwmon support through the companion chip features exposed in this device family.

Important APIs, types, and functions: `struct da9121` is the runtime device state, holding the device, delayed work, platform data, regmap, regulator devices, persistent event masks, passive polling delay, IRQ, and selected variant/subvariant IDs. `struct da9121_range` and `struct da9121_variant_info` encode current-limit ranges by topology. Regulator operations are in `da9121_buck_ops`, with `da9121_get_current_limit()`, `da9121_set_current_limit()`, `da9121_ceiling_selector()`, `da9121_buck_set_mode()`, and `da9121_buck_get_mode()`. Probe/setup is split across `da9121_assign_chip_model()`, `da9121_check_device_type()`, `da9121_set_regulator_config()`, `da9121_config_irq()`, and `da9121_i2c_probe()`.

Control flow: I2C probe allocates state, stores platform data/subvariant match data, selects a regmap configuration based on subtype and `dlg,no-gpio-control`, verifies OTP device and variant IDs, masks all IRQs, registers the appropriate one or two buck descriptors, and configures the IRQ path if an I2C IRQ exists. The OF parse callback counts buck nodes, rejects more regulators than the variant supports, optionally takes per-regulator enable GPIOs, rejects `dlg,no-gpio-control` with enable GPIOs, and tries to apply two-channel ripple-cancel settings. IRQ handling bulk-reads event and mask banks, filters events by variant relevance and mask state, emits regulator notifications for persistent OV/UV/OC/temperature events, masks persistent event bits, clears handled event bits, and schedules delayed polling. The delayed work reads status banks and unmasks persistent events after their status bits clear.

State and persistence: Hardware state is cached through `REGCACHE_MAPLE`; volatile register tables differ when GPIO control is disabled. The driver tracks `persistent[]` event bits so level-like fault conditions remain masked until passive polling confirms they cleared. Current limit changes are refused while the regulator is enabled. Enable GPIOs and PMIC enable bits are managed by regulator core registration. IRQ masks are reset to all masked during probe setup and remove.

Dependencies and integration points: The file depends on I2C, regmap access tables, GPIO descriptors, OF regulator parsing, regulator core regmap operations, threaded IRQs, delayed work on `system_freezable_wq`, and device-tree compatibles for all supported subvariants. It uses constants from `da9121-regulator.h` and dt-binding mode/ripple constants.

Risks and test signals: Test all subtype-to-variant mappings, OTP VRC/MRC rejection, one-channel versus two-channel regmap accessibility, current-limit range bounds, disabled-regulator requirement for current changes, GPIO-control/no-GPIO-control paths, IRQ persistence and unmask sequencing, remove-time IRQ/free and work cancellation, and regulator node counts. The ripple-cancel parse path should be reviewed carefully: the code enters the write block when `of_property_read_u32()` reports failure, which can leave `ripple_cancel` uninitialized and appears opposite to the intended optional-property behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9121-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9121-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9121-regulator.h

Purpose: Defines the DA9121-family private register map, variant enums, subvariant enums, event/status/mask bits, timing defaults, buck field masks, OTP identifiers, and mode/ripple dependencies used by `da9121-regulator.c`.

Important APIs, types, and symbols: `enum da9121_variant` groups electrically similar variants into descriptor/current-limit classes, while `enum da9121_subvariant` names the exact compatible strings. Timing constants `DA9121_DEFAULT_POLLING_PERIOD_MS`, `DA9121_MAX_POLLING_PERIOD_MS`, and `DA9121_MIN_POLLING_PERIOD_MS` bound passive IRQ polling. Register constants cover system status/event/mask/config banks, GPIO banks, buck1/buck2 register windows, and OTP device/variant/config IDs. Bit masks define fault bits such as `TEMP_CRIT`, `TEMP_WARN`, per-buck `PG`, `OV`, `UV`, `OC`, GPIO events, IRQ masks, buck enable, mode, voltage selector, current-limit, and ripple cancel fields.

Control flow support: The C file uses the OTP constants in `da9121_check_device_type()` to reject mismatched DT compatible strings and unsupported metal revisions. It uses status/event/mask macros through `DA9121_STATUS()` and `DA9xxx_STATUS()` to build the fault table consumed by the IRQ handler and delayed poll worker. Buck register and mask constants drive current-limit get/set, mode get/set, vsel descriptors, enable descriptors, and regmap readable/writeable/volatile tables.

State and persistence: This header has no runtime state, but it defines which registers are persistent configuration versus volatile status. The split between `DA9121_REG_*` and `DA9xxx_REG_*` names is important for two-channel variants that reuse the family driver with a second buck bank.

Dependencies and integration points: It includes `dt-bindings/regulator/dlg,da9121-regulator.h` because mode and ripple-cancel values are shared with device-tree bindings. The header is private to the driver and not a generic public kernel API.

Risks and test signals: Validate that every mask used in the C event table matches the correct status/event/mask bank and bit. Device-ID constants must align with silicon; a wrong VRC or MRC value causes legitimate boards to fail probe. Regmap access tables should be retested after any register addition, especially DA914x-specific GPIO/ADMUX addresses that are defined here but not fully exposed by the current C regmap ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9121-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.c

Purpose: Implements a compact I2C regulator driver for the single DA9210 buck regulator. It exposes voltage selection, enable/disable, current-limit programming, and fault notifications through the regulator framework.

Important APIs, types, and functions: `struct da9210` stores the single `regulator_dev` and regmap. `da9210_buck_ops` uses standard regulator regmap helpers for enable, voltage selector, and current limit. `da9210_reg` defines the rail's linear 300 mV to 1570 mV range, current-limit table, `VBUCK_A` selector register, `BUCK_CONT` enable bit, and `BUCK_ILIM` current selector. `da9210_irq_handler()` maps `EVENT_B` bits to overcurrent, undervoltage, overtemperature, and regulation-out notifications.

Control flow: Probe allocates state, creates an 8-bit regmap, resolves init data from platform data or OF regulator constraints, masks all interrupt sources to deassert the IRQ line, registers the regulator, then requests a shared threaded IRQ when `i2c->irq` is present. After requesting the IRQ it unmasks selected fault bits in `MASK_B`.

State and persistence: The driver relies on PMIC registers for enabled state, voltage selector, and current limit. The only in-memory state is the rdev/regmap pair. Interrupt mask state is programmed at probe; handled events are cleared by writing their bits back to `EVENT_B`.

Dependencies and integration points: It depends on I2C, regmap, OF regulator data, optional legacy platform data from `struct da9210_pdata`, and the private register header. Compatible string `dlg,da9210` and I2C ID `da9210` bind the driver.

Risks and test signals: Test no-IRQ operation, IRQ event clearing, mask register writes, OF/platform init-data selection, current-limit selector values, and voltage boundaries. Because the regmap config does not model paged ranges from the header, accesses used by this driver must stay within the simple 8-bit register window it actually touches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.h

Purpose: Provides DA9210-specific platform data and register/bit definitions for the DA9210 regulator driver.

Important APIs, types, and symbols: `struct da9210_pdata` carries legacy `regulator_init_data`. Register constants define page control, status/event/mask banks, GPIO control registers, buck control/current/voltage registers, interface settings, OTP/configuration registers, and paged address regions. Bit definitions cover event and mask bits for GPIOs, overcurrent, not-power-good, temperature warnings/critical events, voltage max events, buck enable, GPI routing, dynamic voltage control, current-limit selector, mode, startup/powerdown controls, voltage selector masks, and standalone configuration.

Control flow support: `da9210-regulator.c` uses `DA9210_REG_VBUCK_A`, `DA9210_VBUCK_MASK`, `DA9210_REG_BUCK_CONT`, `DA9210_BUCK_EN`, `DA9210_REG_BUCK_ILIM`, and `DA9210_BUCK_ILIM_MASK` in the regulator descriptor. It uses `EVENT_B` and `MASK_B` bit definitions in the IRQ path.

State and persistence: The header defines hardware state fields but keeps no runtime state. Page selection constants indicate the chip has wider logical address space than the simple operations used by the C driver.

Dependencies and integration points: This is a private header consumed by the DA9210 driver. Its platform data type connects older board files to regulator constraints, while OF users bypass it.

Risks and test signals: Confirm register constants against the DA9210 datasheet, especially event bits and current-limit masks. If future driver changes access page-2 or configuration registers, the regmap setup in the C file may need range configuration similar to DA9211.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9211-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9211-regulator.c

Purpose: Implements the I2C regulator driver for DA9211/DA9212/DA9213/DA9223/DA9214/DA9224/DA9215/DA9225 devices, exposing one or two buck regulators depending on platform configuration and chip phase configuration.

Important APIs, types, and functions: `struct da9211` stores device, paged regmap, parsed platform data, rdev array, regulator count, IRQ, and chip family ID. `da9211_regmap_range` and `da9211_regmap_config` model the paged register map. `da9211_buck_ops` implements mode get/set, standard regmap voltage/enable operations, and chip-dependent current limits. `DA9211_BUCK()` builds the two buck descriptors. DT parsing is handled by `da9211_parse_regulators_dt()`, initialization by `da9211_regulator_init()`, and fault handling by `da9211_irq_handler()`.

Control flow: Probe creates the ranged regmap, reads `DA9211_REG_DEVICE_ID`, maps supported device IDs into `DA9211`, `DA9213`, or `DA9215` current-limit families, obtains platform data or parses the `regulators` DT child, records the I2C IRQ, and calls regulator initialization. Initialization reads `CONFIG_E`/`DA9211_SLAVE_SEL` to ensure requested one-buck or two-buck platform data matches hardware phase configuration. It then registers each regulator, handing optional enable GPIO descriptors to the regulator core, and unmasks the corresponding overcurrent event bit when IRQs are available. The threaded IRQ reads `EVENT_B`, notifies overcurrent on BUCKA and/or BUCKB, and clears handled bits.

State and persistence: Hardware registers hold enable, voltage, mode, phase, event, and current-limit state. The driver keeps chip identity to choose current-limit tables and `num_regulator` for registered rails. GPIO descriptors are intentionally unhinged from devres when passed as regulator enable GPIOs so ownership transfers to the regulator core.

Dependencies and integration points: It integrates with I2C, regmap range windows, regulator core/OF parsing, optional GPIO enables, chip DT bindings for regulator modes, and private DA9211 register definitions. OF compatibles map to I2C ID table entries, but runtime device ID validation reduces supported current-limit families to three silicon IDs.

Risks and test signals: Test one-buck versus two-buck mismatch rejection, device ID rejection, per-chip current-limit table selection, BUCKA/BUCKB current selector nibble writes, GPIO enable descriptor transfer, no-IRQ warning path, and IRQ notification/clearing for each rail. Mode set lacks an explicit default error for invalid modes and writes zero for unrecognized values, so invalid-mode tests should confirm regulator core never passes unsupported modes or consider hardening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9211-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9211-regulator.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9211-regulator.h

Purpose: Defines DA9211-family register addresses and masks used by the DA9211 regulator driver.

Important APIs, types, and symbols: The header declares page control, status/event/mask registers, GPIO control registers, buck control/configuration/current/voltage registers, interface register, `CONFIG_E`, and `DEVICE_ID`. Bit definitions include page selection, GPIO pin/type/mode options, event and mask bits for power-good, temperature, and overcurrent, buck enable/GPI routing, voltage selector routing, current-limit nibbles, buck mode values, phase selection, and `DA9211_SLAVE_SEL`.

Control flow support: The C driver uses `DA9211_REG_PAGE_CON`, page mask/shift, and max range to configure paged regmap access; it marks status/event registers volatile. It uses `DEVICE_ID` to detect supported chips, `CONFIG_E`/`SLAVE_SEL` to validate one- versus two-buck hardware configuration, buck control and voltage registers to build descriptors, and overcurrent event/mask bits for IRQ handling.

State and persistence: The header defines persistent PMIC configuration and volatile event/status fields but has no memory state. Register naming assumes BUCKA and BUCKB are adjacent in several areas, which the C driver uses through arithmetic offsets.

Dependencies and integration points: Private to the DA9211 regulator driver and tied to `dt-bindings/regulator/dlg,da9211-regulator.h` mode constants included by the C file.

Risks and test signals: Verify adjacent-register arithmetic remains valid for every supported chip alias. Event masks should be tested for both rails, and `SLAVE_SEL` interpretation should be validated on one-phase and two-phase board configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9211-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/db8500-prcmu.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/db8500-prcmu.c

Purpose: Provides DB8500 PRCMU-backed regulators and power-domain switches for the UX500 platform. It represents always-on/platform-controlled rails and EPOD power domains as regulator framework devices.

Important APIs, types, and functions: The normal regulator ops are `db8500_regulator_enable()`, `db8500_regulator_disable()`, and `db8500_regulator_is_enabled()`, which update `dbx500_regulator_info` state and the global power-state active count. EPOD switch helpers `enable_epod()` and `disable_epod()` coordinate on/off and RAM-retention states. Switch regulator ops call these helpers through `db8500_regulator_switch_enable()`, `db8500_regulator_switch_disable()`, and `db8500_regulator_switch_is_enabled()`. `dbx500_regulator_info[]` is the static descriptor table for rails and EPOD switches.

Control flow: Probe obtains optional platform init data, iterates all DB8500 regulator descriptors, fills `regulator_config` with per-descriptor driver data and optional init constraints, and registers each regulator. It then initializes optional debugfs support through `ux500_regulator_debug_init()`. Remove only tears down debugfs. The driver registers at `arch_initcall`, reflecting early platform power dependency.

State and persistence: Per-regulator `is_enabled` flags are stored in the static descriptor array. Global EPOD state is tracked by `epod_on[]` and `epod_ramret[]` arrays so on and RAM-retention views of the same EPOD are coordinated. Non-switch regulators update a shared active power-state reference count unless flagged `exclude_from_power_state`. The actual EPOD state persists in PRCMU firmware/hardware through `prcmu_set_epod()`.

Dependencies and integration points: It depends on DB8500 regulator IDs, PRCMU MFD APIs, EPOD constants, regulator core, OF match names embedded in descriptors, and shared DBX500 debug/power-state helpers from `dbx500-prcmu.c`.

Risks and test signals: Test balanced enable/disable calls, `exclude_from_power_state` behavior for VSMPS2, EPOD on versus RAM-retention interactions, default enabled ESRAM switches, PRCMU call failure propagation, debugfs init/remove, and platform init-data indexing. Static global state means repeated bind/unbind or multiple platform instances would be unsafe; this matches the SoC-global design but should be considered in tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/db8500-prcmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.c

Purpose: Implements shared UX500 regulator support for DBX500 PRCMU-backed regulators, specifically the active power-state reference counter and optional debugfs inspection.

Important APIs, types, and functions: `power_state_active_enable()` increments a spinlock-protected global count, and `power_state_active_disable()` decrements it with unbalanced-call detection. Under `CONFIG_REGULATOR_DEBUG`, `struct ux500_regulator_debug` stores debugfs root, regulator array, counts, and suspend-state snapshots. Debugfs show callbacks expose the active count and per-regulator current/before/after states. `ux500_regulator_debug_init()` creates `ux500-regulator/status` and `ux500-regulator/power-state-count`; `ux500_regulator_debug_exit()` removes the tree and frees snapshots.

Control flow: DB8500 regulators call the power-state helpers from enable/disable paths. DB8500 probe calls debug init with the static regulator array; remove calls debug exit. Debugfs reads format live information from the shared regulator array.

State and persistence: `power_state_active_cnt` is a process-global integer protected by `power_state_active_lock`. Debug state is stored in a single static `rdebug` object. Snapshot arrays are allocated during debug init and freed at exit, though this file does not itself populate before/after suspend snapshots.

Dependencies and integration points: This file depends on regulator descriptors from `dbx500-prcmu.h`, platform devices, debugfs, seq_file, and module infrastructure. It is shared support for platform-specific files such as `db8500-prcmu.c`.

Risks and test signals: Test unbalanced disable detection, concurrent enable/disable with IRQ-safe spinlock coverage, debugfs file creation failure tolerance, and cleanup after partial debug init allocation failure. Since the active count is global, tests should not assume per-device isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.h

Purpose: Declares the shared data structure and helper prototypes used by UX500/DBX500 PRCMU regulator drivers.

Important APIs, types, and symbols: `struct dbx500_regulator_info` wraps a `regulator_desc` with software state fields: `is_enabled`, `epod_id`, `is_ramret`, and `exclude_from_power_state`. It declares `power_state_active_enable()` and `power_state_active_disable()`. When `CONFIG_REGULATOR_DEBUG` is enabled it declares debug init/exit functions; otherwise inline stubs return success.

Control flow support: DB8500 descriptor entries embed this structure in a global array. Enable/disable paths use the state fields and helper functions, while probe/remove call debug hooks regardless of build configuration.

State and persistence: The header defines the shape of persistent in-memory regulator state but does not allocate it. Its inline debug stubs make debug optional without conditional code at call sites.

Dependencies and integration points: It includes `linux/platform_device.h` and assumes regulator descriptor definitions are visible to C files including it through their own includes.

Risks and test signals: Adding fields changes the shared contract between DB8500 descriptors and debugfs formatting. Test builds with and without `CONFIG_REGULATOR_DEBUG` to ensure both real and stub paths compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/devres.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/devres.c

Purpose: Implements device-managed regulator framework APIs. It wraps regulator consumer acquisition, enable/disable actions, bulk consumers, provider registration, supply aliases, notifiers, IRQ helpers, and OF-specific regulator acquisition in devres lifetimes.

Important APIs, types, and functions: Consumer helpers include `devm_regulator_get()`, `devm_regulator_get_exclusive()`, `devm_regulator_get_optional()`, `devm_regulator_get_enable()`, `devm_regulator_get_enable_optional()`, `devm_regulator_get_enable_read_voltage()`, and `devm_regulator_put()`. Bulk helpers include `devm_regulator_bulk_get()`, `_exclusive()`, `_const()`, `devm_regulator_bulk_put()`, and `devm_regulator_bulk_get_enable()`. Provider and integration helpers include `devm_regulator_register()`, `devm_regulator_register_supply_alias()`, `devm_regulator_bulk_register_supply_alias()`, `devm_regulator_register_notifier()`, `devm_regulator_unregister_notifier()`, `devm_regulator_irq_helper()`, `devm_of_regulator_get()`, and `devm_of_regulator_get_optional()`.

Control flow: Each get/register helper allocates a devres record, calls the underlying unmanaged regulator API, stores enough information to undo the operation, and adds the record to the device on success. Enable helpers add devm actions to disable regulators on detach, with cleanup on intermediate failure. Bulk helpers allocate a devres object storing the caller's consumer array and count, unwind already-enabled consumers on failure, and release the bulk get if action registration fails. Supply alias and notifier helpers register one resource at a time and unwind already registered entries when bulk alias registration fails.

State and persistence: Devres records are the core state. They store pointers to regulators, bulk consumer arrays, registered `regulator_dev` providers, supply alias keys, notifier blocks, and IRQ-helper handles. Lifetimes are bound to the relevant device: consumers generally bind to the consumer device, provider registrations bind to provider device, and notifiers bind to `regulator->dev`.

Dependencies and integration points: This file is tightly integrated with regulator core internals from `internal.h`, including `_regulator_get()`, `_regulator_bulk_get()`, `_of_regulator_get()`, `regulator_register()`, alias APIs, notifier APIs, and IRQ helper APIs. It exports GPL symbols for broad driver use.

Risks and test signals: Test every failure unwind path: allocation failure, get failure, enable failure, action registration failure, bulk partial enable failure, alias registration failure after some aliases succeeded, notifier unregister, and IRQ helper action reset. `devm_regulator_bulk_put()` assumes `consumers[0].consumer` is valid to find the device; callers must not pass an empty or uninitialized array. `devm_regulator_get_enable_read_voltage()` intentionally uses optional get to distinguish missing supplies from dummy regulators, so tests should verify error-code behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dummy.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/dummy.c

Purpose: Creates the global dummy regulator used by the regulator framework for systems or tests without a controllable backing regulator.

Important APIs, types, and functions: The global `dummy_regulator_rdev` stores the registered regulator device. `dummy_initdata` marks the dummy regulator always-on. `dummy_desc` describes a voltage regulator named `regulator-dummy` with id `-1` and an empty operation table. `dummy_regulator_probe()` registers the descriptor on a faux device. `regulator_dummy_init()` creates the faux device named `reg-dummy`.

Control flow: Initialization creates a faux device with `dummy_regulator_driver` ops. The faux device probe registers the dummy regulator using devm registration and stores the returned rdev globally. If faux device allocation or regulator registration fails, the code logs errors and leaves the global unset or error-free only on success.

State and persistence: The dummy regulator has no controllable hardware state; its constraints mark it always on. Lifetime is bound to the faux device, and the rdev pointer is global for framework use.

Dependencies and integration points: It depends on faux device infrastructure, regulator provider registration, machine constraints, and the local `dummy.h` declaration. It is intended for regulator core fallback behavior and tests.

Risks and test signals: Test initialization failure handling, that the dummy regulator is always-on, that consumers do not expect voltage operations from the empty ops table, and that framework users correctly distinguish dummy supplies from real optional supplies when needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dummy.h -->
# sources/distributed-fs/ceph-client/drivers/regulator/dummy.h

Purpose: Declares the dummy regulator rdev and initialization entry point for regulator framework fallback support.

Important APIs, types, and symbols: It forward-declares `struct regulator_dev`, exports `extern struct regulator_dev *dummy_regulator_rdev`, and declares `void __init regulator_dummy_init(void)`.

Control flow support: The regulator core can include this header to initialize and reference the dummy regulator implemented in `dummy.c`.

State and persistence: The only state contract is the external global pointer. This header does not define ownership rules beyond the dummy implementation's faux-device lifetime.

Dependencies and integration points: Private to the regulator subsystem and paired with `dummy.c`.

Risks and test signals: Ensure all users see the same global declaration and that initialization order makes the dummy regulator available before fallback consumers require it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/dummy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/event.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/event.c

Purpose: Provides generic netlink multicast delivery for regulator events, allowing kernel regulator notifications to be surfaced to userspace through a regulator generic-netlink family.

Important APIs, types, and functions: `reg_event_seqnum` is an atomic message sequence counter. `reg_event_mcgrps[]` declares the multicast group. `reg_event_genl_family` declares the family name, version, max attribute, and multicast group from `regnl.h`. `reg_generate_netlink_event()` builds and multicasts a `REG_GENL_CMD_EVENT` message containing `struct reg_genl_event` with regulator name and event mask.

Control flow: `fs_initcall(reg_event_init)` registers the generic netlink family. When `reg_generate_netlink_event()` is called, it allocates an skb with `GFP_ATOMIC`, adds a generic netlink header with an incremented sequence number, reserves the event attribute, zeroes and fills the event payload, finalizes the message, and multicasts it. Allocation/header/attribute failures free the skb and return an error.

State and persistence: Persistent state is limited to the registered generic-netlink family and atomic sequence number. Event messages are transient and allocated in atomic context.

Dependencies and integration points: It depends on netlink/genetlink APIs, regulator netlink ABI definitions in `regnl.h`, and regulator event callers elsewhere in the subsystem.

Risks and test signals: Test family registration, multicast group visibility, event payload string truncation via `strscpy()`, sequence increments, allocation failure paths, and behavior when no listeners exist. Because events are sent with `GFP_ATOMIC`, high-rate fault storms should be tested for allocation pressure and dropped messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fan53555.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/fan53555.c

Purpose: Implements an I2C regulator driver for Fairchild/ON FAN53526/FAN53555 and compatible Rockchip, Silergy, and TCS programmable buck regulators. It handles vendor-specific voltage ranges, VSEL register layouts, mode bits, ramp-delay tables, enable timing, and suspend voltage selection.

Important APIs, types, and functions: `struct fan53555_device_info` stores vendor, device, descriptor, init data, chip ID/revision, selected voltage/sleep/enable/mode/ramp registers, voltage range parameters, sleep voltage cache, and timing/ramp metadata. Regulator ops include voltage selector, voltage-time, linear mapping/listing, suspend voltage/enable/disable, enable/disable/is_enabled, mode get/set, and ramp-delay programming. Setup helpers are split by vendor: `fan53526_voltages_setup_fairchild()`, `fan53555_voltages_setup_fairchild()`, `fan53555_voltages_setup_rockchip()`, `rk8602_voltages_setup_rockchip()`, `fan53555_voltages_setup_silergy()`, and `fan53526_voltages_setup_tcs()`. `fan53555_device_setup()` chooses active/sleep VSEL and mode registers.

Control flow: Probe obtains platform data or parses DT regulator init data and `fcs,suspend-voltage-selector`, resolves vendor from match data, optionally applies legacy platform ramp-delay constraints, initializes regmap, reads chip ID and revision registers, runs vendor/device setup, constructs the regulator descriptor dynamically, and registers it. Suspend voltage writes the sleep VSEL register only when the requested microvolt value differs from the cached value. Mode get/set reads or writes the vendor-selected mode register and mask.

State and persistence: Hardware registers hold voltage selector, enable, mode, and ramp state. The driver caches only the requested sleep voltage in `sleep_vol_cache`, which may not equal the rounded selector voltage. Descriptor fields are populated at probe based on chip ID/revision and vendor. There is no IRQ support or manual remove path.

Dependencies and integration points: It depends on I2C, regmap, regulator OF/platform data, `linux/regulator/fan53555.h`, and OF/I2C match tables for Fairchild, Rockchip, Silergy, and TCS compatible strings. The descriptor supplies `"vin"` and uses regulator core ramp-delay helpers.

Risks and test signals: Test every vendor/chip-ID/chip-revision matrix, sleep VSEL 0/1 selection, RK8602 alternate register addresses, TCS mode/ramp registers, invalid platform `slew_rate`, ramp-delay constraint behavior, suspend voltage cache behavior after failed writes, and unsupported chip rejection. `fan53555_set_mode()` ignores the return value of `regmap_update_bits()` and always returns zero for supported modes, so tests should include injected regmap failures if hardening is considered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fan53555.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fan53880.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/fan53880.c

Purpose: Implements an I2C regulator driver for the FAN53880 PMIC, registering four LDOs, one buck, and one boost regulator.

Important APIs, types, and functions: `enum fan53880_regulator_ids` indexes LDO1-4, BUCK, and BOOST. `enum fan53880_registers` defines product ID, voltage, output-current, and enable registers. `fan53880_ops` uses standard linear-range voltage and regmap enable/selector helpers. The `FAN53880_LDO()` macro creates LDO descriptors with fixed default selector zero plus selectable 800 mV upward ranges. `fan53880_regulators[]` contains all six descriptors.

Control flow: Probe creates the regmap, reads and validates `FAN53880_PRODUCT_ID` against `FAN53880_ID`, then iterates all descriptors and registers them with a shared config. There is no custom per-regulator state or IRQ path.

State and persistence: Regulator state is entirely hardware-backed in vsel and enable registers. Descriptor arrays are static, and resources are devm-managed.

Dependencies and integration points: It depends on I2C, regmap, regulator linear-range helpers, OF compatible `onnn,fan53880`, and I2C ID `fan53880`. Supply names encode input rails such as `VIN12`, `VIN3`, `VIN4`, and `PVIN`.

Risks and test signals: Test product-ID rejection, registration of all six regulators, LDO/buck/boost voltage boundary selectors, enable masks, and input supply names. Since `config.regmap` is not explicitly assigned in probe, regmap-based operations rely on regulator core lookup behavior; this should be validated on real or emulated hardware and may be a regression risk compared with drivers that pass `config.regmap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fan53880.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fixed-helper.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/fixed-helper.c

Purpose: Provides a small helper for registering a fixed always-on regulator backed by a platform device, primarily for board/setup code that needs to create a fixed supply programmatically.

Important APIs, types, and functions: `struct fixed_regulator_data` bundles `fixed_voltage_config`, `regulator_init_data`, and an embedded `platform_device`. `regulator_fixed_release()` frees the duplicated supply name and containing allocation. `regulator_register_always_on()` allocates and initializes the bundle, marks constraints always-on, assigns consumer supplies, configures platform data for `"reg-fixed-voltage"`, registers the platform device, and returns it.

Control flow: Callers provide an ID, name, consumer supply array, count, and microvolt value. The helper allocates state, duplicates the name with `kstrdup_const()`, fills fixed regulator config and init data, sets the platform release callback, calls `platform_device_register()`, and returns the embedded platform device pointer.

State and persistence: The platform device owns the allocated bundle. The fixed regulator config points to embedded init data, and release frees both the constant-or-allocated supply name and the bundle.

Dependencies and integration points: It integrates with the fixed voltage regulator platform driver (`fixed.c`), platform device core, and regulator machine constraints.

Risks and test signals: Test allocation failure, supply name lifetime, platform registration failure behavior, release callback execution, always-on constraints, and consumer supply propagation. The helper currently returns the platform device even if `platform_device_register()` fails; callers should be checked for error handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fixed-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fixed.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/fixed.c

Purpose: Implements the fixed-voltage regulator platform driver. It supports plain fixed supplies, fixed supplies enabled by a clock, fixed supplies represented as PM-domain performance states, optional enable GPIOs, input supply naming, startup/off-on delays, and optional under-voltage IRQ notification.

Important APIs, types, and functions: `struct fixed_voltage_data` stores the runtime descriptor, registered rdev, optional enable clock, enable counter, and performance state. `struct fixed_dev_type` selects clock-enabled or domain-enabled behavior. Operation tables are empty for pure fixed regulators, `fixed_voltage_clkenabled_ops` for clock enable/disable/is_enabled, and `fixed_voltage_domain_ops` for PM-domain performance state control. OF parsing is in `of_get_fixed_voltage_config()`, IRQ setup in `reg_fixed_get_irqs()`, and main registration in `reg_fixed_voltage_probe()`.

Control flow: Probe obtains configuration from DT or platform data, duplicates the supply name, selects an ops table based on OF match data, gets an enable clock or required OPP performance state when needed, sets descriptor delays and input supply, configures a nonexclusive optional enable GPIO with boot state, registers the regulator, stores driver data, and requests an optional IRQ for under-voltage notification. Clock/domain enable increments `enable_counter`; disable decrements it after disabling clock or clearing performance state.

State and persistence: The hardware model is fixed voltage; only enable state may be controlled by GPIO, clock, or PM-domain. `enable_counter` tracks software enable state for clock/domain variants. The regulator core takes ownership of the optional enable GPIO, so the driver intentionally does not use devm for that descriptor.

Dependencies and integration points: It integrates with platform devices, OF regulator constraints, GPIO descriptors, clocks, generic PM domains, OPP performance state parsing, regulator notifications, and fixed regulator platform data. It registers as `reg-fixed-voltage` at `subsys_initcall` and supports compatibles `regulator-fixed`, `regulator-fixed-clock`, and `regulator-fixed-domain`.

Risks and test signals: Test fixed voltage constraint equality, boot-on GPIO polarity, shared nonexclusive enable GPIOs, clock prepare/enable failures, PM-domain performance-state failures, enable counter balance, optional IRQ absence versus request failure, and regulator core ownership of GPIO descriptors. Fixed regulators with variable min/max constraints should fail probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fp9931.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/fp9931.c

Purpose: Implements the Fitipower FP9931 I2C regulator driver for e-paper style supplies, exposing `v3p3`, `vposneg`, and `vcom` regulators plus optional temperature hwmon reporting. It coordinates VIN power, enable GPIOs, power-good GPIO/IRQ, runtime PM, regmap cache, and programmable timing.

Important APIs, types, and functions: `struct fp9931_data` stores device, regmap, VIN regulator, power-good and enable GPIOs, optional temperature-sensor enable GPIO, completion, and IRQ. Regulator ops are split into `fp9931_v3p3ops`, `fp9931_vposneg_ops`, and `fp9931_vcom_ops`. Runtime PM callbacks are `fp9931_runtime_suspend()` and `fp9931_runtime_resume()`. Other key helpers include `setup_timings()`, `fp9931_hwmon_read()`, `fp9931_set_enable()`, `fp9931_clear_enable()`, voltage selector wrappers that resume the device, and `pgood_handler()`.

Control flow: Probe initializes regmap with cache defaults, gets required VIN and GPIOs, converts the power-good GPIO to an IRQ, requests a rising-edge threaded IRQ that completes `pgood_completion`, enables runtime PM or performs a non-PM resume with cleanup action, programs optional `fitipower,tdly-ms` timing fields, registers all three regulators, and optionally registers a hwmon device. Enabling `vcom` resumes the chip, reinitializes completion, asserts the enable GPIO, waits up to 200 ms for PGOOD, validates the GPIO, and keeps the runtime PM reference until disable. `vposneg` is considered enabled when PGOOD is high because it is enabled along with `vcom`.

State and persistence: Regmap uses `REGCACHE_FLAT`; temperature is volatile and VCOM has a default cached value. Runtime suspend disables the optional temperature sensor GPIO and VIN regulator, then marks regcache dirty. Resume enables VIN, turns on the optional temperature sensor, waits for one ADC conversion, and syncs regcache. PGOOD completion is transient synchronization state.

Dependencies and integration points: It depends on I2C, regmap, runtime PM, regulator consumer/provider APIs, GPIO descriptors, completions, optional hwmon, and DT compatible `fitipower,fp9931`.

Risks and test signals: Test VIN enable/disable and regcache sync across runtime PM, PGOOD timeout and IRQ completion races, vcom/vposneg enable semantics, timing property validation for exactly four entries and disallowed value 3, hwmon reads while suspended, no-CONFIG_PM cleanup, and regulator registration after setup failures. Because `vcom` enable intentionally holds a runtime PM reference until disable, tests should verify balanced references on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/fp9931.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/gpio-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/gpio-regulator.c

Purpose: Implements a generic GPIO-programmable regulator. It maps a set of GPIO output bit patterns to discrete voltage or current states and registers either a voltage or current regulator.

Important APIs, types, and functions: `struct gpio_regulator_data` stores descriptor, GPIO descriptor array, state table, and current GPIO bitmask state. Voltage operations are `gpio_regulator_get_value()`, `gpio_regulator_set_voltage()`, and `gpio_regulator_list_voltage()`. Current operations use `gpio_regulator_get_value()` and `gpio_regulator_set_current_limit()`. DT parsing is handled by `of_get_gpio_regulator_config()`, and registration by `gpio_regulator_probe()`.

Control flow: Probe allocates state, obtains platform data or parses DT regulator constraints, GPIO initial states, `states` value/bitmask pairs, regulator type, startup delay, and optional `vin` input supply. It acquires each programming GPIO at its configured initial level, copies the state table, chooses the voltage or current ops table, derives the initial software state from GPIO flags, gets an optional nonexclusive enable GPIO, and registers the regulator. Setting voltage searches for the lowest state value within the requested range; setting current searches for the highest state value within range. Both then write each GPIO bit and update `data->state`.

State and persistence: The driver tracks only the last programmed GPIO bitmask in `state`. Actual output state is held by GPIO lines. Enable GPIO ownership is passed to the regulator core through `cfg.ena_gpiod`, while programming GPIOs stay devm-managed by this driver.

Dependencies and integration points: It integrates with platform devices, OF regulator constraints, GPIO descriptor APIs, regulator machine/OF helpers, and compatible `regulator-gpio`. It also preserves legacy DT ABI for undocumented `enable-at-boot`.

Risks and test signals: Test missing or malformed `states`, odd-length state arrays, voltage/current selection policy, zero GPIO counts, GPIO initial state derivation, active-low GPIO descriptor behavior, optional enable GPIO ownership, unknown regulator type warning/default, and `vin-supply` mapping. Duplicate state bitmasks or nonmonotonic state values can make get/list/set behavior surprising and should be validated in board data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/gpio-regulator.c -->
