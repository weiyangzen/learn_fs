# Research: subset-b-005177 regulator drivers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/core.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/core.c

## Purpose
This file is the Linux regulator framework core. It registers the regulator class and private regulator bus, owns regulator provider registration, maps consumer supply names to provider devices, mediates voltage/current/mode/enable requests, applies machine and DT constraints, coordinates coupled regulators, exposes sysfs/debugfs state, and forwards regulator events. In this source tree it is the integration hub used by the concrete provider drivers in the same folder through `regulator_register()`, `devm_regulator_register()`, `struct regulator_desc`, `struct regulator_ops`, regmap helpers, and notifier APIs.

## Important APIs, Types, And Functions
Key internal state includes `struct regulator_dev` instances registered in `regulator_class`, per-consumer `struct regulator` handles on each `rdev->consumer_list`, `regulator_map_list` for board supply aliases, `regulator_supply_alias_list`, shared `regulator_ena_gpio_list`, `regulator_coupler_list`, and the global `has_full_constraints` flag. Locking is built around per-rdev wound/wait mutexes plus `regulator_list_mutex` and `regulator_nesting_mutex`; `regulator_lock_dependent()` recursively locks coupled regulators and upstream supplies.

Provider-facing APIs include `regulator_register()`, `regulator_unregister()`, `regulator_set_voltage_rdev()`, `regulator_notifier_call_chain()`, `rdev_get_drvdata()`, `rdev_get_id()`, `rdev_get_dev()`, and `rdev_get_regmap()`. Consumer-facing APIs include `regulator_get()`, `regulator_get_optional()`, `regulator_get_exclusive()`, `regulator_put()`, enable/disable/force/deferred disable, voltage and current setters/getters, mode and load APIs, bypass control, power budget APIs, bulk helpers, notifier registration, and supply alias registration.

Major internal paths are `set_machine_constraints()`, `regulator_resolve_supply()`, `_regulator_get_common()`, `_regulator_enable()`, `_regulator_disable()`, `_regulator_do_set_voltage()`, `regulator_balance_voltage()`, `regulator_init_coupling()`, `regulator_late_cleanup()`, and the suspend/resume helpers.

## Control Flow
Initialization runs from `core_initcall(regulator_init)`: it registers the regulator bus, class, one asynchronous bus driver, debugfs root, dummy regulator support, and the generic coupler. `late_initcall_sync(regulator_init_complete)` later sets full constraints for DT systems and schedules delayed cleanup of unused regulators unless `regulator_ignore_unused` is set.

Provider registration starts in `regulator_register()`. It validates the descriptor, duplicates the config, obtains OF or platform init data, initializes `struct regulator_dev`, copies constraints, handles enable GPIOs, applies constraints, initializes coupling, registers consumer supply mappings, adds the class device, attempts supply resolution, optionally adds a regulator bus device for future supply resolution, initializes debugfs, and attempts coupling resolution for already registered peers. Error paths unwind mappings, coupling, GPIOs, supply references, config allocations, and device references.

Consumer acquisition starts with `regulator_get()` and variants. `_regulator_get()` validates the requested id, does DT lookup, board mapping lookup, and name lookup via `regulator_dev_lookup()`, then `_regulator_get_common()` handles dummy fallback under full constraints, exclusivity, unresolved coupling deferral, supply resolution, provider module pinning, per-consumer handle creation, debugfs/sysfs links, open counts, exclusive state propagation, and stateless device links.

Enable/disable operations lock the target, its supply chain, and coupled peers. `_regulator_enable()` enables upstream supply first, balances coupled voltage, updates consumer load accounting, turns hardware on if this is the first use, and emits enable events. `_regulator_disable()` checks balanced consumer counts, honors `always_on`, sends pre/abort/final disable events, updates use counts, rebalances coupled voltage, and disables the supply when no longer used. Deferred disable queues `rdev->disable_work`.

Voltage changes validate per-board constraints and aggregate all consumer ranges, then use `regulator_balance_voltage()` even for a single regulator. `_regulator_do_set_voltage()` supports direct `set_voltage`, selector based `set_voltage_sel`, voltage mapping helpers, stepped selector transitions, delay calculation through driver callbacks or ramp/settling constraints, and voltage change notifiers. Supply voltage can be raised before and lowered after a child change when dropout requirements demand it. Coupled regulator balancing iteratively chooses the largest safe voltage delta while respecting max spread and max step constraints.

## State And Persistence
State is in kernel memory and hardware, not persisted across boot by this file. Runtime state includes per-rdev use/open/bypass counts, cached error bits, consumer voltage requests for each suspend state, deferred disable counts, load requests, power budget accounting, last-off timestamps for off/on delay, supply handles, constraints pending state, coupling descriptors, and debugfs/sysfs objects. Hardware state changes are delegated to provider ops or regmap helpers; late cleanup may disable unused hardware rails once full constraints are known.

## Dependencies And Integration Points
The file depends on the device model, OF regulator parsing, regmap, GPIO descriptors, debugfs, PM suspend, reboot hardware protection, async work, module refs, notifiers, netlink regulator events, tracepoints, and regulator internals (`dummy.h`, `internal.h`, `regnl.h`). Provider drivers integrate by filling `struct regulator_desc` and `struct regulator_ops`; consumers integrate through exported regulator APIs. DT integration includes supply lookup, init constraints, coupled regulator phandles, and full-constraints behavior.

## Risks
The main risks are concurrency and partial-unwind correctness. Supply resolution can race with registration and constraint application, so this file uses two-regulator and recursive wound/wait locking. Incorrect provider descriptors can expose invalid sysfs attributes, bad voltage tables, missing `list_voltage` for selector ops, or unsafe enable/disable behavior. Full-constraints cleanup can disable hardware rails if board constraints are wrong. Coupling is deliberately limited by generic support, and multiple-coupled non-custom cases may fail. Event forwarding currently forwards only selected events and uses deferred work, so refcounting and notifier unregister order matter.

## Test Signals
Useful tests include boot/probe logs for constraint errors and supply deferrals, `regulator_summary` and `supply_map` debugfs output, sysfs attributes under regulator devices, consumer enable/disable balance warnings, voltage/current/mode API return codes, late cleanup logs, suspend/resume callbacks, notifier delivery including under-voltage forwarding and system-critical shutdown paths, and lockdep coverage for coupled and nested supply operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/cpcap-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/cpcap-regulator.c

## Purpose
This file is the Motorola CPCAP PMIC regulator provider. It describes CPCAP rails for several SoC/product configurations and registers the supported rails with the regulator core using regmap-backed operations.

## Important APIs, Types, And Functions
`struct cpcap_regulator` wraps `struct regulator_desc` with resource-assignment register metadata. `struct cpcap_ddata` stores the parent regmap, platform device, and SoC-specific descriptor table. `CPCAP_REG()` builds descriptors with `volt_table`, `vsel_reg`, `enable_reg`, masks, enable/disable values, ramp delay, `of_match`, and `of_map_mode`.

The operational hooks are `cpcap_regulator_enable()`, `cpcap_regulator_disable()`, `cpcap_regulator_get_mode()`, `cpcap_regulator_set_mode()`, and `cpcap_map_mode()`. The `cpcap_regulator_ops` table combines those hooks with standard regmap helpers for enable, voltage selector, and voltage table mapping.

## Control Flow
Probe obtains SoC-specific match data from the OF compatible string, allocates driver data, fetches the parent CPCAP regmap, initializes a shared `regulator_config`, and iterates up to `CPCAP_NR_REGULATORS`. Entries with the sentinel name end the loop; entries using `unknown_val_tbl` are skipped because their voltage tables are not known. Each real entry is passed to `devm_regulator_register()` with the entry as `driver_data`.

Enable first calls `regulator_enable_regmap()`. For descriptors whose `enable_val` contains `CPCAP_REG_OFF_MODE_SEC`, it also sets the assignment bit so off mode uses the primary assignment while enabled; if assignment update fails, it disables the rail again. Disable reverses the assignment bit first, then calls `regulator_disable_regmap()`, restoring the assignment bit if disable fails.

## State And Persistence
The driver stores no dynamic per-rail state beyond `driver_data`; rail state lives in CPCAP registers and in the regulator core. Static state is encoded in voltage tables and three SoC-specific descriptor arrays: `omap4_regulators`, `mot_regulators`, and `xoom_regulators`. Some rails share registers or assignment masks, notably VSIM and VSIMCARD.

## Dependencies And Integration Points
It depends on the Motorola CPCAP MFD for register definitions and parent regmap, OF match data for board variant selection, and regulator core regmap helpers. DT nodes are expected under a `regulators` child node with names matching descriptor `of_match` strings.

## Risks
Unknown voltage tables are intentionally skipped, so DT references to those rails will not resolve. Incorrect SoC match data can program wrong enable values or assignment bits. Shared VSIM/VSIMCARD masks and off-mode assignment logic need board-specific validation. `cpcap_regulator_get_mode()` ignores `regmap_read()` failure and defaults through the returned value path, so read errors may be hidden.

## Test Signals
Check probe success per compatible, number of registered rails, regulator debugfs/sysfs voltage lists, enable/disable register transitions, off-mode assignment bit behavior for SW5-style rails, standby/normal mode mapping, and failures from parent regmap access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/cpcap-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/cros-ec-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/cros-ec-regulator.c

## Purpose
This provider exposes a ChromeOS EC controlled voltage regulator to the Linux regulator framework. Hardware operations are not local register writes; they are EC host commands keyed by a regulator index from DT.

## Important APIs, Types, And Functions
`struct cros_ec_regulator_data` owns a dynamically filled `regulator_desc`, the registered `regulator_dev`, the parent `cros_ec_device`, DT `reg` index, and a copied EC voltage table. Regulator ops are `cros_ec_regulator_enable()`, `disable()`, `is_enabled()`, `list_voltage()`, `get_voltage()`, and `set_voltage()`. `cros_ec_regulator_init_info()` sends `EC_CMD_REGULATOR_GET_INFO` to discover the name and supported millivolt table.

## Control Flow
Probe allocates driver data, fetches the EC device from the parent, reads regulator init data and the DT `reg` index, initializes descriptor owner/type/ops and `supply_name = "vin"`, then queries EC metadata. It registers one regulator with `devm_regulator_register()` and stores the driver data.

Enable/disable/is-enabled/get-voltage/set-voltage each creates the matching EC command parameter structure with the stored index and calls `cros_ec_cmd()`. Voltage setting converts the core's uV range to an exact mV-compatible range using round-up for the minimum and floor for the maximum; empty ranges return `-EINVAL`.

## State And Persistence
The cached state is the EC-provided descriptor name and voltage table. Actual enable and voltage state persists in the EC/hardware, not this driver. The regulator core tracks consumers and constraints around these EC operations.

## Dependencies And Integration Points
It depends on ChromeOS EC protocol structures and commands, OF regulator constraints, a DT `reg` property for the EC regulator index, and a `vin` upstream supply name. The descriptor name is runtime data returned by firmware, not a compile-time table.

## Risks
Firmware is the authority for names and voltage tables, so malformed EC responses can affect registration. The driver caps copied voltages to the response array size and terminates the name, which mitigates common response issues. No selector is returned from `set_voltage()`, so selector-aware consumers only have `list_voltage()` for enumeration. EC command latency/failure directly affects regulator API calls.

## Test Signals
Test with EC command tracing, successful DT init data parsing, correct `reg` index per node, voltage table sysfs enumeration, uV-to-mV boundary cases in `set_voltage`, enable/is-enabled consistency, and probe failure when EC commands are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/cros-ec-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da903x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da903x-regulator.c

## Purpose
This file is the Dialog/Marvell DA9030, DA9034, and DA9035 regulator provider. It maps platform-device IDs from the DA903x MFD into regulator descriptors for DVC bucks and LDOs, including several chip-specific voltage programming quirks.

## Important APIs, Types, And Functions
`struct da903x_regulator_info` combines a `regulator_desc` with voltage register location, selector shift/width, optional update register/bit, and enable register/bit. `DA903x_LDO()` and `DA903x_DVC()` macros generate descriptor entries. Common ops include `da903x_set_voltage_sel()`, `da903x_get_voltage_sel()`, `da903x_enable()`, `da903x_disable()`, and `da903x_is_enabled()`.

Special ops cover DA9030 LDO1/LDO15 unlock writes (`da9030_set_ldo1_15_voltage_sel()`), DA9030 LDO14's non-linear selector ordering (`da9030_map_ldo14_voltage()` and `da9030_list_ldo14_voltage()`), DA9034 DVC update strobes (`da9034_set_dvc_voltage_sel()`), and DA9034 LDO12 linear ranges.

## Control Flow
The driver is registered with `subsys_initcall()`. Probe finds the matching descriptor by `pdev->id`, patches the ops and range metadata for special IDs, prepares `regulator_config` from platform data and the descriptor pointer, registers through `devm_regulator_register()`, and stores the returned `rdev`.

Voltage selector writes use the DA903x MFD byte update helpers. For DVC rails, the driver writes the selector then sets an update bit. Enable/disable use set/clear bit helpers on the configured enable register. Fixed-voltage descriptors have `n_voltages == 1`; common selector setters reject writes for those.

## State And Persistence
The descriptor table is static and shared. Probe mutates selected descriptor entries for special-case ops/ranges, which persists for the lifetime of the module. Hardware state is stored in DA903x registers; the regulator core tracks consumer state.

## Dependencies And Integration Points
The file depends on the DA903x MFD accessors (`da903x_read`, `da903x_update`, `da903x_set_bits`, `da903x_clr_bits`), platform-device IDs from MFD cells, platform regulator init data, and regulator core linear/range voltage helpers.

## Risks
The static descriptor array is modified at probe time, which is acceptable for fixed IDs but risky if assumptions about one-time immutable descriptors change. `check_range()` validates only the minimum against min/max and ignores `max_uV`, so mapping relies on later list/constraint checks. Special rails require exact unlock/update behavior; missed double writes or update strobes would leave hardware unchanged. Invalid platform IDs fail probe.

## Test Signals
Exercise probe for each DA9030/DA9034/DA9035 ID, read/write selectors, enable bits, fixed-voltage rails, DA9030 LDO14 selector mapping, DA9030 LDO1/LDO15 double unlock writes, DA9034/DA9035 DVC update bits, and platform constraint application from the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da903x-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9052-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9052-regulator.c

## Purpose
This provider supports DA9052 and DA9053 PMIC buck and LDO regulators. It supplies chip-specific descriptor tables, voltage mapping, DVC activation behavior, and buck current limit handling.

## Important APIs, Types, And Functions
`struct da9052_regulator_info` contains a `regulator_desc`, voltage step/range, and activate bit. `struct da9052_regulator` holds the parent MFD pointer, selected info, and registered `rdev`. The main helpers are `da9052_dcdc_get_current_limit()`, `da9052_dcdc_set_current_limit()`, `da9052_list_voltage()`, `da9052_map_voltage()`, `da9052_regulator_set_voltage_sel()`, and `da9052_regulator_set_voltage_time_sel()`.

`DA9052_DCDC()` and `DA9052_LDO()` generate descriptors using regmap-backed enable and voltage selector fields. `da9052_dcdc_ops` adds current limit operations for bucks; `da9052_ldo_ops` omits them.

## Control Flow
The platform driver registers at `subsys_initcall()`. Probe gets the MFD cell ID and parent `struct da9052`, selects the descriptor table based on chip ID, optionally reads platform regulator init data, passes the parent regmap to the regulator core, and registers the selected descriptor with `devm_regulator_register()`.

Voltage listing is normally linear from `min_uV` and `step_uV`, except DA9052 BUCK4 switches to 100 mV steps above 3.0 V. Mapping verifies overlap with the rail range, clamps the minimum upward, applies the BUCK4 high-voltage rule, and validates the resulting selector by listing it. Selector writes update the vsel field and, for DVC-controlled bucks/LDOs, set the matching GO bit in `DA9052_SUPPLY_REG`. Ramp time for those DVC rails is calculated from selector delta at 6.25 mV/us.

## State And Persistence
Static tables distinguish DA9052 from DA9053 variants. Dynamic state consists of the selected table entry and parent chip pointer. Hardware state is in PMIC registers; current-limit range selection depends on chip ID and buck ID.

## Dependencies And Integration Points
The driver depends on DA9052 MFD register accessors and regmap, MFD cell IDs, optional platform data, regulator core regmap selector helpers, and platform-driver lifecycle. OF headers are included for descriptors using `of_match`/`regulators_node`, although probe primarily uses MFD/platform data.

## Risks
Current-limit field placement differs for even and odd buck IDs, so ID/register alignment is critical. BUCK4 voltage mapping differs between DA9052 and DA9053. DVC-controlled rails require activate bits after selector writes; missed activation means the output may not change. Probe assumes `mfd_get_cell(pdev)` and parent driver data are valid.

## Test Signals
Test both DA9052 and DA9053 descriptor selection, BUCK4 mapping around 3.0 V, current limit get/set fields for even and odd bucks, DVC GO-bit writes, ramp-time calculations, enable/disable through regmap, and core constraint rejection for unsupported voltage/current ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9052-regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9055-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/da9055-regulator.c

## Purpose
This file provides DA9055 PMIC buck and LDO regulators. It supports voltage register set A/B selection, suspend voltage programming, regulator mode control, buck current limits, optional GPIO-controlled enable/register selection, and over-current notification for LDO5/LDO6.

## Important APIs, Types, And Functions
Descriptor metadata is split across `struct da9055_conf_reg`, `struct da9055_volt_reg`, `struct da9055_mode_reg`, and `struct da9055_regulator_info`. Runtime state in `struct da9055_regulator` includes the parent DA9055 pointer, selected descriptor, registered `rdev`, and register-select GPIO mode.

Key operations are `da9055_buck_get_mode()`, `da9055_buck_set_mode()`, `da9055_ldo_get_mode()`, `da9055_ldo_set_mode()`, `da9055_regulator_get_voltage_sel()`, `da9055_regulator_set_voltage_sel()`, `da9055_regulator_set_suspend_voltage()`, `da9055_suspend_enable()`, `da9055_suspend_disable()`, `da9055_gpio_init()`, and `da9055_ldo5_6_oc_irq()`.

## Control Flow
The platform driver registers at `subsys_initcall()`. Probe selects descriptor info by `pdev->id`, binds parent DA9055/regmap/platform data into `regulator_config`, initializes optional GPIO control, registers the regulator, and for LDO5/LDO6 requests the named `REGULATOR` IRQ to emit `REGULATOR_EVENT_OVER_CURRENT`.

Voltage reads first inspect the active A/B register select bit, then read the corresponding voltage register. Voltage writes select register set A and update A when no external register-select GPIO is configured; if a GPIO selects A/B, the driver reads the active selection and writes the matching register. Suspend voltage is mapped linearly and written to register set B, with software selecting B when no GPIO handles selection. Suspend enable/disable switch between B and A in the same no-GPIO case.

## State And Persistence
Static descriptor data covers BUCK1, BUCK2, and LDO1-LDO6. Runtime state tracks whether register selection is software controlled or external GPIO controlled. Hardware state is in DA9055 PMIC registers, including mode fields, voltage A/B registers, enable bits, and current-limit selector bits.

## Dependencies And Integration Points
It depends on the DA9055 MFD core/register definitions, regmap, optional platform data arrays for regulator init and GPIO mux selections, GPIO descriptors named `regulator-enable`, `enable`, and `regulator-select`, regulator core regmap helpers, and threaded IRQ delivery for over-current events.

## Risks
`da9055_gpio_init()` dereferences `pdata` for GPIO mux arrays when optional GPIOs are present, so DT/platform configurations with GPIO properties but no platform data can fail badly. Mode setters default `val = 0` and do not reject unsupported mode values, which can silently program an unintended mode. Register-set A/B behavior is sensitive to GPIO mux configuration. LDO5/LDO6 IRQ request tolerates `-EBUSY`, so shared interrupt behavior should be verified.

## Test Signals
Validate probe for every ID, GPIO and non-GPIO A/B selection paths, normal and suspend voltage writes, mode get/set for bucks and LDOs, buck current limit selector fields, enable/disable regmap behavior, LDO5/LDO6 over-current notifier delivery, and error handling for missing platform data or IRQ resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/da9055-regulator.c -->
