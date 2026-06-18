# Research: subset-b-004994

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/core.c -->
# sources/distributed-fs/ceph-client/drivers/opp/core.c

## Purpose
`core.c` is the central implementation of the Linux generic OPP framework. It owns global OPP table registration, lookup, reference counting, dynamic OPP insertion/removal, availability changes, notifier dispatch, and the actual device transition sequence for clocks, regulators, interconnect bandwidth, PM-domain performance states, and required OPP dependencies. The file is not Ceph-specific; in this source tree it is kernel infrastructure used by device drivers that describe operating points.

## Important APIs, Types, And Functions
The global state is `opp_tables`, protected by `opp_table_lock`, plus an `opp_configs` xarray that stores opaque tokens from `dev_pm_opp_set_config()`. Per-table state is defined in `opp.h` as `struct opp_table`, with `opp_list`, `dev_list`, `kref`, `lock`, notifier `head`, clock/regulator/interconnect handles, required OPP tables/devices, and current transition state.

Public exported APIs include getters such as `dev_pm_opp_get_voltage()`, `dev_pm_opp_get_supplies()`, `dev_pm_opp_get_power()`, `dev_pm_opp_get_freq_indexed()`, `dev_pm_opp_get_level()`, `dev_pm_opp_get_required_pstate()`, latency/count helpers, search APIs for exact/ceil/floor frequency, level, bandwidth, and key matches, transition APIs `dev_pm_opp_set_rate()` and `dev_pm_opp_set_opp()`, table/config lifecycle APIs, dynamic add/remove, voltage adjustment, regulator sync, enable/disable, notifier registration, and table removal.

Internal helpers include `_add_opp_table_indexed()`, `_allocate_opp_table()`, `_opp_add()`, `_opp_compare_key()`, `_set_opp()`, `_disable_opp_table()`, `_set_required_opps()`, `_opp_set_regulators()`, `_opp_set_clknames()`, and `_opp_clear_config()`.

## Control Flow
Table lookup walks the global `opp_tables` list and matches devices through each table's `dev_list`, then returns a kref-held `opp_table`. Table creation uses a careful `opp_tables_busy` protocol: callers briefly hold `opp_table_lock`, drop it for allocations and framework calls that may re-enter OPP/debugfs/clock/interconnect code, then re-acquire it to publish the new table.

OPP searches share generic list-walking helpers. Exact, ceil, and floor queries select available or unavailable entries and increment the returned OPP kref. OPP list ordering is maintained by `_opp_compare_key()`, which compares all clocks, then peak bandwidths, then level.

The transition path is `_set_opp()`. It identifies the current OPP, skips no-op transitions unless forced, compares old and new keys to infer scaling direction, then sequences dependencies. On scale-up it sets required OPPs, PM-domain level, interconnect bandwidth, and regulator voltages before clocks. On scale-down it changes clocks first, then regulators, bandwidth, level, and required OPPs in reverse order. `dev_pm_opp_set_rate()` rounds the requested clock, finds the ceiling OPP, and can force a clock update when the same OPP still covers a different rounded frequency. Passing `NULL` or zero frequency disables bandwidth, the primary regulator, PM-domain level, and required OPP state.

## State And Persistence
The file persists kernel runtime state only. OPP tables live until their krefs reach zero; OPP entries live until their own krefs are dropped. Dynamic OPPs hold an extra table reference that is released when removed. Static OPPs are reference-counted through `parsed_static_opps`. Current programmed state is tracked by `current_opp`, `current_rate_single_clk`, and `enabled`.

Hardware-visible persistence is delegated to subsystems: `clk_set_rate()`, `regulator_set_voltage_triplet()`, `regulator_enable/disable()`, `icc_set_bw()`, and `dev_pm_domain_set_performance_state()`. Notifier chains report add, remove, enable, disable, and voltage-adjust events to interested clients.

## Dependencies And Integration Points
This file integrates with the clock framework, regulator framework, interconnect framework, PM domains/genpd, device tree helpers from `of.c`, debugfs hooks from `debugfs.c`, CPU helpers from `cpu.c`, and consumers through `<linux/pm_opp.h>`. The `__free(put_opp)` and `__free(put_opp_table)` cleanup attributes are used throughout to make reference release less error-prone.

## Risks
Transition ordering is high risk: wrong scale direction or an early return after partially updating dependencies can leave hardware overclocked, undervolted, or with stale bandwidth/performance state. `dev_pm_opp_get_voltage()` assumes a single supply and dereferences `supplies[0]`, so callers must not use it for multi-regulator tables. Duplicate detection mostly reports the first supply in warnings and duplicate policy. `opp_tables_busy` uses a busy wait with `cpu_relax()`, so table creation bugs could spin. Notifier callbacks are invoked after state changes and may observe partially removed objects if reference rules are violated.

## Test Signals
Useful tests include OPP table creation/removal races, duplicate dynamic/static OPP additions, ceil/floor searches with multi-clock and bandwidth tables, `set_rate()` scale-up/scale-down ordering under tracepoints, regulator failure injection, required-opps lazy-link failures, notifier ordering, `dev_pm_opp_clear_config()` token misuse, and KASAN/lockdep coverage for table and OPP lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/cpu.c -->
# sources/distributed-fs/ceph-client/drivers/opp/cpu.c

## Purpose
`cpu.c` provides CPU-oriented helpers on top of the generic OPP core. It builds cpufreq frequency tables from OPP entries, frees those tables, removes OPP tables over CPU masks, and records/query CPU sharing relationships for OPP tables.

## Important APIs, Types, And Functions
Under `CONFIG_CPU_FREQ`, `dev_pm_opp_init_cpufreq_table()` allocates and fills a `struct cpufreq_frequency_table` from available OPPs. `dev_pm_opp_free_cpufreq_table()` releases it. Always-built helpers include `_dev_pm_opp_cpumask_remove_table()`, `dev_pm_opp_cpumask_remove_table()`, `dev_pm_opp_set_sharing_cpus()`, and `dev_pm_opp_get_sharing_cpus()`.

## Control Flow
`dev_pm_opp_init_cpufreq_table()` first obtains the count of available OPPs. It allocates one extra entry for `CPUFREQ_TABLE_END`, repeatedly calls `dev_pm_opp_find_freq_ceil()` with a monotonically increasing `rate`, stores kHz frequencies, and marks boost OPPs with `CPUFREQ_BOOST_FREQ`. The loop relies on OPP list ordering and the find helper updating `rate` to the matched frequency.

CPU mask removal iterates CPUs until an optional `last_cpu` stop point and calls `dev_pm_opp_remove_table()` for each resolved CPU device. Sharing setup finds the existing table for a representative CPU, adds `opp_device` entries for each other CPU, and marks the table `OPP_TABLE_ACCESS_SHARED`. Sharing query refuses unknown access mode, then returns either every `opp_dev->dev->id` in the table or only the requested CPU for exclusive tables.

## State And Persistence
The cpufreq table is caller-owned heap memory and must be freed by the matching helper. Sharing persists in the shared `opp_table->dev_list` and `shared_opp` enum until table teardown. No hardware is programmed here; the helpers only prepare data and modify table membership.

## Dependencies And Integration Points
This file depends on CPU device lookup (`get_cpu_device()`), cpumask iteration, cpufreq table structures, and OPP core internals `_find_opp_table()`, `_add_opp_dev()`, and `_dev_pm_opp_cpumask_remove_table()`. It is commonly used by CPUFreq drivers that consume DT OPP tables.

## Risks
The generated cpufreq table is a snapshot; callers must rebuild it after OPP availability or voltage/frequency changes. `dev_pm_opp_set_sharing_cpus()` logs but continues if some CPUs cannot be resolved or added, which can leave a partial sharing mask. It assumes CPU device IDs correspond to CPU numbers. Removal over masks can encounter absent CPU devices and continue, so cleanup errors are not fatal.

## Test Signals
Tests should cover cpufreq table generation order, boost flags, empty/no-table error returns, rebuild after enable/disable, shared CPU mask reporting for exclusive and shared tables, partial CPU device failures, and table teardown over policy masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/opp/debugfs.c

## Purpose
`debugfs.c` exposes OPP tables, devices, OPP entries, clocks, supplies, and interconnect bandwidth values under `/sys/kernel/debug/opp`. It is observability infrastructure for the runtime OPP state maintained by `core.c`.

## Important APIs, Types, And Functions
The file keeps a single `rootdir`. OPP core calls `opp_debug_register()`, `opp_debug_unregister()`, `opp_debug_create_one()`, and `opp_debug_remove_one()`. Internal helpers create device names, per-clock rate files, per-supply voltage/current/power files, per-interconnect directories, and a `name` file backed by `bw_name_fops`.

## Control Flow
`opp_debug_init()` creates the root directory at `core_initcall` time. When a device is attached to an OPP table, `opp_debug_register()` creates the real directory for the first device or a symlink for later devices sharing the table. When an OPP is added, `opp_debug_create_one()` chooses a stable-ish directory name from rate and level for single-clock OPPs, otherwise from the current OPP count, then creates read-only files for availability, flags, level, latency, DT node name, clocks, supplies, and bandwidth.

Unregistering a device removes its symlink. If the removed device owns the real directory and the table is shared, `opp_migrate_dentry()` renames the directory to another device and removes that other device's old symlink.

## State And Persistence
Debugfs entries point directly at live fields inside `struct dev_pm_opp` and `struct opp_table`. The data persists only while the OPP/table exists and debugfs is mounted. The module stores `opp->dentry`, `opp_dev->dentry`, `opp_table->dentry`, and `opp_table->dentry_name` for cleanup/migration.

## Dependencies And Integration Points
This file depends on `CONFIG_DEBUG_FS`, debugfs primitives, device names, OF node names, interconnect path names, and OPP core lifecycle callbacks. Stub functions in `opp.h` remove this dependency when debugfs is disabled.

## Risks
Because files expose live object fields, lifetime ordering is critical. Debugfs removal must happen outside some locks to avoid circular dependencies, which is why OPP core defers certain `put` operations. The fallback directory name using `_get_opp_count()` can be unstable for non-rate/multi-clock tables. `opp_migrate_dentry()` uses `BUG_ON(!new_dev)` and assumes caller guarantees a shared table. Long device names are truncated by `NAME_MAX`.

## Test Signals
Validate debugfs creation for exclusive and shared OPP tables, symlink migration when the primary device is removed, OPP add/remove cleanup, multi-clock file names, regulator and interconnect files, concurrent table teardown under lockdep, and boot with debugfs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/of.c -->
# sources/distributed-fs/ceph-client/drivers/opp/of.c

## Purpose
`of.c` parses device-tree OPP bindings and connects them to the generic OPP core. It supports old `operating-points` v1 tuples, `operating-points-v2` tables, shared OPP tables, indexed OPP tables, named voltage/current properties, required-opps dependency graphs, interconnect bandwidth, CPU sharing masks, required performance-state translation, and Energy Model registration.

## Important APIs, Types, And Functions
Public APIs include `dev_pm_opp_of_get_opp_desc_node()`, `dev_pm_opp_of_find_icc_paths()`, `dev_pm_opp_of_add_table()`, `devm_pm_opp_of_add_table()`, indexed variants, CPU mask add/remove/share helpers, `of_get_required_opp_performance_state()`, `dev_pm_opp_of_has_required_opp()`, `dev_pm_opp_get_of_node()`, `dev_pm_opp_calc_power()`, and `dev_pm_opp_of_register_em()`. Internal mechanisms include `lazy_opp_tables`, `_managed_opp()`, `_opp_table_alloc_required_tables()`, `_of_opp_alloc_required_opps()`, `lazy_link_required_opp_table()`, `_opp_is_supported()`, `opp_parse_supplies()`, and `_opp_add_static_v2()`.

## Control Flow
Table initialization starts in `_of_init_opp_table()`, which reads backward-compatible latency/tolerance properties, detects genpd providers, obtains the indexed `operating-points-v2` node, sets shared/exclusive access, and pre-allocates required OPP table references from the first child OPP. Missing required tables place the table on `lazy_opp_tables`.

Adding a table uses `_of_add_table_indexed()`: it creates or finds an `opp_table`, then parses v2 if an OPP node exists, otherwise v1. V2 parsing iterates child nodes, allocates an OPP, reads key properties (`opp-hz`, peak/avg bandwidth, `opp-level`), checks `opp-supported-hw`, reads turbo/suspend/latency/supply properties, links required-opps when possible, and calls `_opp_add()`. After adding a table, `lazy_link_required_opp_table()` revisits pending tables and fills required OPP pointers when their target table appears.

CPU helpers add/remove OPP tables over masks and derive sharing masks by comparing `operating-points-v2` phandles plus `opp-shared`. Energy Model registration prefers per-OPP `opp-microwatt`; otherwise it uses `dynamic-power-coefficient` and voltage/frequency values.

## State And Persistence
The file stores OF node references in `opp_table->np` and `opp->np`, required table references in `required_opp_tables`, required OPP references in each OPP, static parse counts in `parsed_static_opps`, and optional interconnect paths in the table. All state is kernel runtime state backed by the DT; no DT is modified.

## Dependencies And Integration Points
This file depends on OF APIs, genpd, interconnect, Energy Model, CPU device-node helpers, and OPP core internals. It is the main bridge between platform firmware descriptions and consumers such as CPUFreq, devfreq, genpd, and power/thermal code.

## Risks
Required-opps lazy linking is subtle: until all tables are available, users may receive `-EBUSY` or OPPs may be marked unavailable. `_managed_opp()` shares tables only when the DT table has `opp-shared`; otherwise identical nodes can still produce separate tables. Supply parsing mutates `regulator_count` based on the first discovered property, so inconsistent OPP nodes fail later. 64-bit `opp-hz` is cast to `unsigned long`, which warns but still truncates on 32-bit. Energy Model registration fails if power data is incomplete.

## Test Signals
Test v1 and v2 bindings, named microvolt/microamp/microwatt properties, multi-clock `opp-hz`, interconnect peak/avg bandwidth counts, unsupported hardware masks, duplicate OPPs, suspend OPP selection, required-opps across genpds with late table registration, CPU shared masks, indexed tables, and Energy Model registration from both `opp-microwatt` and `dynamic-power-coefficient`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/opp.h -->
# sources/distributed-fs/ceph-client/drivers/opp/opp.h

## Purpose
`opp.h` is the private header for the OPP implementation. It defines the in-memory representation of OPPs, OPP tables, devices attached to a table, configuration token data, interconnect bandwidth values, internal lifecycle helpers, and debugfs/OF conditional hooks.

## Important APIs, Types, And Functions
Core types are `struct dev_pm_opp_icc_bw`, `struct dev_pm_opp`, `struct opp_device`, `enum opp_table_access`, and `struct opp_table`. `struct dev_pm_opp` stores availability, dynamic/static status, turbo/suspend/removed flags, rates, level, supplies, bandwidth, required OPP pointers, owning table, OF node, and optional debugfs fields. `struct opp_table` stores list nodes, notifier head, device and OPP lists, locks, OF state, current and suspend OPPs, required OPP tables/devices, supported hardware, property name, clocks, regulators, interconnect paths, enable/genpd state, and debugfs fields.

Internal prototypes expose table lookup, allocation, add/remove, key comparison, CPU mask cleanup, indexed table creation, required OPP availability, OF init/clear, and debugfs create/remove/register functions.

## Control Flow
This header has no runtime flow, but it defines the contracts that `core.c`, `of.c`, `cpu.c`, `debugfs.c`, and platform helpers rely on. Conditional inline stubs make OF and debugfs optional without changing core call sites. `lazy_linking_pending()` centralizes the required-opps pending test by checking `opp_table->lazy`.

## State And Persistence
All fields are runtime kernel state. The header defines ownership relationships: OPP tables own OPP entries and `opp_device` records; OPP entries hold references to required OPPs and OF nodes; configs hold an OPP table reference and flags indicating which resources must be unwound. The layout also places debugfs-only fields under `CONFIG_DEBUG_FS`.

## Dependencies And Integration Points
The header includes device, interconnect, kref, list, limits, public PM OPP, and notifier headers. It forward-declares clock and regulator types and binds the OPP implementation to OF, debugfs, CPU, regulator, interconnect, and notifier subsystems.

## Risks
This header is the shared ABI inside the OPP implementation; field semantics must stay synchronized across files. `regulator_count` uses `-1`, `0`, and positive values with distinct meanings, so allocation and parsing code must preserve that convention. The flexible allocation pattern in `_opp_allocate()` depends on field ordering and count values for supplies, rates, and bandwidth. Debugfs and OF fields are conditional, so code must use the provided hooks.

## Test Signals
Build coverage with `CONFIG_OF` and `CONFIG_DEBUG_FS` enabled and disabled is essential. Runtime signals include correct kref release, no list corruption, correct allocations for zero/multiple regulators, clocks, and interconnect paths, and valid required-opps state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/ti-opp-supply.c -->
# sources/distributed-fs/ceph-client/drivers/opp/ti-opp-supply.c

## Purpose
`ti-opp-supply.c` is a TI OMAP-specific platform driver that plugs a custom regulator transition callback into the generic OPP core. It supports OPP supply handling where a CPU VDD rail may need efuse-optimized voltage values and a second ABB/VBB rail must be sequenced with VDD.

## Important APIs, Types, And Functions
Private data types include `struct ti_opp_supply_optimum_voltage_table`, `struct ti_opp_supply_data`, and `struct ti_opp_supply_of_data`. The single static `opp_data` stores the optimized voltage table, absolute max voltage, and scratch arrays for old/new two-regulator supply values.

Key functions are `_store_optimized_voltages()`, `_free_optimized_voltages()`, `_get_optimal_vdd_voltage()`, `_opp_set_voltage()`, `ti_opp_config_regulators()`, and `ti_opp_supply_probe()`. The OF match table recognizes `"ti,omap-opp-supply"`, `"ti,omap5-opp-supply"`, and `"ti,omap5-core-opp-supply"`.

## Control Flow
Probe reads match data, stores it as driver data, optionally maps efuse registers and parses `ti,efuse-settings` plus `ti,absolute-max-voltage-uv`, then registers `ti_opp_config_regulators()` with the OPP core for CPU0 through `dev_pm_opp_set_config_regulators()`.

During an OPP transition, `ti_opp_config_regulators()` fetches new supplies, compares old and new OPP frequencies, maps nominal VDD to an optimized voltage if an efuse table exists, raises the minimum VDD when necessary, and programs rails. On scale-up it programs VDD before VBB; on scale-down it programs VBB before VDD. On failure it fetches old supplies and attempts to restore VBB then VDD.

## State And Persistence
The efuse-derived voltage table and absolute max voltage persist in global static `opp_data`. The OPP core stores the callback as part of the CPU OPP table configuration. Hardware-visible state is regulator voltage settings for VDD and VBB. There is no remove path in this file, so resource cleanup is only covered for probe failure.

## Dependencies And Integration Points
The driver depends on platform resources, OF properties, regulator consumers, CPU device lookup, OPP core regulator configuration APIs, and efuse register MMIO. It is loaded as a platform driver and affects CPU OPP transitions performed elsewhere.

## Risks
`opp_data` is global, so multiple instances would conflict. Probe assumes CPU0 is the target OPP device. `OPPDM_HAS_NO_ABB` is defined in match data but not used to reduce regulator count or alter sequencing, so DT/regulator configuration must still match the callback's two-regulator expectation. There is no driver remove cleanup for the OPP config token returned by `dev_pm_opp_set_config_regulators()`. Restore logic depends on old OPP supply data being valid.

## Test Signals
Test efuse parsing, missing/invalid `ti,efuse-settings`, absolute max voltage bounds, zero efuse fallback to reference voltage, scale-up and scale-down ordering, regulator failure restoration, two-regulator count warnings, probe failure cleanup, and behavior on OMAP5 core variants marked as no-ABB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/ti-opp-supply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/parisc/Kconfig

## Purpose
This Kconfig file defines PA-RISC bus, IOMMU, PCI bridge, legacy bus, chassis, SuperIO, and stable-storage options. It controls which drivers in `drivers/parisc` are built for PA-RISC machines.

## Important APIs, Types, And Functions
The file declares `GSC`, `HPPB`, `IOMMU_CCIO`, `GSC_LASI`, `GSC_WAX`, `ISA`, `GSC_DINO`, `PCI_LBA`, hidden `IOSAPIC` and `IOMMU_SBA`, plus PA-RISC-specific `SUPERIO`, `CHASSIS_LCD_LED`, `PDC_CHASSIS`, `PDC_CHASSIS_WARN`, and `PDC_STABLE`.

## Control Flow
There is no executable control flow. The dependency graph controls build selection: `GSC` selects EISA and I/O port support; `IOMMU_CCIO` depends on GSC; Dino depends on PCI and GSC; LBA enables IOSAPIC and SBA IOMMU by default through hidden bools; chassis warning support depends on procfs; stable storage can be modular.

## State And Persistence
Kconfig choices persist in kernel configuration and determine compiled driver availability. Defaults are mostly `y` for platform features likely present on supported PA-RISC systems.

## Dependencies And Integration Points
The options map directly to the Makefile objects in the same directory. They also gate architecture-level services such as PCI, EISA, procfs, sysfs, LED class support, and I/O port availability.

## Risks
Incorrect dependencies can build drivers without required architecture services or omit required bus/IOMMU drivers. Help text encodes platform coverage knowledge; stale descriptions can lead users to disable necessary hardware support. Defaults to `y` are practical for old platform bootability but increase kernel surface.

## Test Signals
Build matrix coverage should include PCI and non-PCI PA-RISC configs, GSC with/without Dino and CCIO, LBA with implicit IOSAPIC/SBA, procfs-disabled chassis warnings, LED-class-disabled chassis LED support, and modular `PDC_STABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/parisc/Makefile

## Purpose
This Makefile maps PA-RISC Kconfig symbols to driver objects and documents ordering constraints required for bus enumeration, IRQ regions, PCI, EISA, and IOMMU setup.

## Important APIs, Types, And Functions
Object mappings include `iosapic.o`, `sba_iommu.o`, `lba_pci.o`, `ccio-dma.o`, `gsc.o`, `lasi.o asp.o`, `wax.o`, EISA objects, `hppb.o`, `dino.o`, `superio.o`, `led.o`, `pdc_stable.o`, and always-built `power.o`.

## Control Flow
The build order is the only flow. Comments specify that CCIO must come before potential subdevices, GSC before LASI/WAX, ASP/WAX before EISA adapters for IRQ regions, and EISA before PCI so it gets an IRQ region.

## State And Persistence
No runtime state is present. The ordering persists in the linked kernel object order and can affect initcall probing behavior on PA-RISC hardware.

## Dependencies And Integration Points
The Makefile consumes symbols defined in `Kconfig` and produces object inclusion for the architecture's platform bus, PCI, IOMMU, LED, stable-storage, and power drivers.

## Risks
Reordering can break early resource/IRQ ownership and bus discovery. Conditional inclusion must match Kconfig dependencies; otherwise objects may reference unavailable symbols or probe before required infrastructure is initialized.

## Test Signals
Use build tests for relevant Kconfig combinations and boot tests on systems with CCIO, GSC/LASI/ASP/WAX, EISA, Dino PCI, LBA PCI, SuperIO, chassis LEDs, and stable storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/asp.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/asp.c

## Purpose
`asp.c` initializes the ASP/Cutoff GSC ASIC on older PA-RISC systems. It claims the hardwired GSC interrupt, installs the common GSC ASIC interrupt handler, programs the VIPER interrupt word, assigns local IRQs to known ASP child devices, and optionally registers old-style chassis LED support.

## Important APIs, Types, And Functions
The static `struct gsc_asic asp` holds ASP state. `asp_choose_irq()` maps child `sversion` values to local IRQ lines and optional auxiliary IRQs. `asp_init_chip()` probes the ASIC, claims/request IRQs, initializes the GSC common layer, fixes child IRQs, and registers LEDs. The `parisc_driver` matches `HPHW_BA` with sversion `0x00070`.

## Control Flow
At `arch_initcall`, `asp_init()` registers the PA-RISC driver. Probe reads the ASP version from `dev->hpa.start + ASP_VER_OFFSET`, names it `"Asp"` or `"Cutoff"`, uses the separate interrupt register base `ASP_INTERRUPT_ADDR`, claims hardcoded GSC IRQ 3, constructs `asp.eim`, and requests `gsc_asic_intr`. It then writes VIPER so ASP interrupts arrive on that line, calls `gsc_common_setup()`, and walks both ASP children and a sibling Mongoose device through `gsc_fixup_irqs()`.

## State And Persistence
Runtime state is in the single static `asp` object and assigned IRQ fields in `parisc_device` children. Hardware state includes VIPER interrupt programming and LED registration at fixed legacy addresses. There is no remove path; this is boot-time platform setup.

## Dependencies And Integration Points
The driver depends on PA-RISC inventory/probing, GSC interrupt helpers, raw GSC I/O access, parent device traversal, and optional `CONFIG_CHASSIS_LCD_LED` LED registration.

## Risks
IRQ routing is hardcoded by historical sversion tables and hardware path checks. Unknown child devices are left untouched. ASP has two register windows, but firmware reports only the special-register base, so incorrect use of `hpa` versus `ASP_INTERRUPT_ADDR` would break interrupt handling. Error paths after `request_irq()` do not visibly undo earlier allocation.

## Test Signals
Boot tests should confirm ASP/Cutoff detection, GSC IRQ claim, child SCSI/LAN/HIL/parallel/serial/EISA/graphics/audio/FDDI IRQ assignment, aux IRQ assignment for HIL and EISA, Mongoose sibling fixups, VIPER interrupt delivery, and LED operation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/asp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/ccio-dma.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/ccio-dma.c

## Purpose
`ccio-dma.c` implements DMA mapping for first-generation PA-RISC cache-coherent systems with U2/UTurn I/O adapters. It programs the CCIO IOMMU in virtual mode, allocates I/O virtual pages, fills the I/O page directory, purges I/O TLB entries, provides PA-RISC DMA map ops, registers IOC MMIO resources, and supports Dino/LBA resource allocation under CCIO windows.

## Important APIs, Types, And Functions
`struct ioc` is the central controller state: MMIO registers, resource bitmap, I/O PDIR, pdir size, allocation hint, lock, Cujo workaround flag, chain ID shift, linked-list pointer, hardware path, fake PCI device, and two routed MMIO resources. Important functions include `ccio_alloc_range()`, `ccio_free_range()`, `ccio_io_pdir_entry()`, `ccio_clear_io_tlb()`, `ccio_mark_invalid()`, DMA ops `ccio_map_phys()`, `ccio_unmap_phys()`, `ccio_alloc()`, `ccio_free()`, `ccio_map_sg()`, `ccio_unmap_sg()`, lookup helpers `ccio_get_iommu()` and `ccio_find_ioc()`, `ccio_cujo20_fixup()`, `ccio_ioc_init()`, resource helpers `ccio_allocate_resource()` and `ccio_request_resource()`, and `ccio_probe()`.

## Control Flow
Probe allocates an IOC, links it into `ioc_list`, maps registers, initializes the I/O PDIR and resource map, switches hardware into virtual mode, initializes resource windows from IOA registers, installs global `hppa_dma_ops`, attaches an HBA-like platform data object, and optionally creates `/proc/bus/runway/ccio` entries.

Mapping a single DMA buffer computes the page offset, rounds to I/O pages, locks the IOC resource map, allocates a contiguous bitmap range, fills PDIR entries with physical addresses and DMA hints, flushes entries, and returns IOVA plus offset. Unmapping rounds back to pages, invalidates PDIR valid bits, purges matching I/O TLB entries, and frees the bitmap range. Scatter-gather mapping uses shared `iommu-helpers.h` to coalesce chunks and fill the PDIR in two passes, preserving virtual-coherence information.

Resource allocation first tries existing IOC windows, then expands one of the two IO ranges and writes updated low/high registers before allocating from that parent.

## State And Persistence
IOC state persists for the boot lifetime in `ioc_list`. The resource map tracks allocated IOVA pages; `pdir_base` holds hardware-consumed mappings. Hardware state includes IO chain ID mask, PDIR base, IO control virtual mode, TLB entries, IO low/high windows, and TLB purge commands. Optional procfs state reports controller and bitmap details.

## Dependencies And Integration Points
The file depends on PA-RISC device inventory, raw MMIO, DMA map ops, scatterlist/IOMMU helpers, PCI HBA data, procfs, resource management, cache flush/sync assembly helpers, and Dino through exported resource helpers and `ccio_get_iommu()`.

## Risks
Resource exhaustion and oversize mappings call `panic()`. The allocator intentionally allocates coarse bitmap units for small mappings, trading space for TLB locality. Mapping assumes 32-bit-or-better DMA masks. Cache/TLB correctness depends on architecture-specific `lci`, `fdc`, and `sync` sequences. `hppa_dma_ops` is global, so probe order matters. Cujo 2.0 workaround reserves repeating bad pages; missing it risks silent corruption. Resource expansion rewrites IOA windows and must not conflict with firmware-registered child resources.

## Test Signals
Test single and scatter-gather DMA map/unmap, sub-cacheline SAFE_DMA behavior, bidirectional consistent allocations, IOVA reuse after unmap, TLB purge coverage, procfs reporting, DMA mask rejection, resource allocation under both IOC windows, Cujo 2.0 bad-page reservation, multi-IOC lookup by hardware path, and stress tests for mapping exhaustion and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/ccio-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/dino.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/dino.c

## Purpose
`dino.c` manages Dino/Cujo GSC-to-PCI bridges on PA-RISC systems. It provides PCI config-space access, I/O port emulation, local interrupt masking/demultiplexing, card-mode and bridge-mode initialization, PCI bus/resource fixups, and root bus creation.

## Important APIs, Types, And Functions
`struct dino_device` embeds `struct pci_hba_data`, a spinlock, interrupt mask state, GSC IRQ transaction data, and local-to-global IRQ mapping. Important functions include `dino_cfg_read()`, `dino_cfg_write()`, generated `dino_in/out*()` I/O port accessors, IRQ chip callbacks `dino_mask_irq()`, `dino_unmask_irq()`, optional `dino_set_affinity_irq()`, ISR `dino_isr()`, IRQ assignment/fixup helpers, `dino_card_setup()`, `dino_card_fixup()`, `dino_fixup_bus()`, `dino_card_init()`, `dino_bridge_init()`, `dino_common_init()`, and `dino_probe()`.

## Control Flow
The PA-RISC driver registers at `arch_initcall`. Probe identifies Dino, Cujo, and card-mode variants, reserves MMIO, applies Cujo 2.0 CCIO workaround when configured, allocates and maps `dino_device`, initializes card-mode hardware or bridge-mode resource windows, performs common interrupt and I/O-port setup, then creates a PCI root bus with Dino config ops. The bus is scanned, resources assigned, devices added, and the global `dino_current_bus` advances.

Config access serializes on `dinosaur_pen`, writes `DINO_PCI_ADDR`, then reads or writes `DINO_CONFIG_DATA`; writes perform an extra vendor/product read to avoid Dino address stepping. I/O port ops use the same address register with `DINO_IO_DATA`.

Interrupt flow maps each local Dino input to a Linux IRQ via `gsc_assign_irq()`. The top ISR reads and clears `DINO_IRR0`, handles each pending local bit through `generic_handle_irq()`, then checks `DINO_ILR` for still-asserted level interrupts and loops up to 100 times before rate-limited warnings.

## State And Persistence
Per-bridge state persists in `dino_device` and `dev->dev.platform_data`. Hardware state includes PCI address/config registers, IMR, IAR0, bridge feature/control registers, MMIO decode windows, port resources, and card-mode PCI command/timing registers. PCI bus numbering persists through the global `dino_current_bus`.

## Dependencies And Integration Points
The driver integrates with PA-RISC GSC IRQ helpers, PCI core root-bus/resource APIs, CCIO IOMMU/resource helpers, architecture HBA data, optional Tulip and Cirrus PCI fixups, and PARISC firmware inventory.

## Risks
The code assumes PCI scanning is single-threaded because of the global bus counter. SMP interrupt comments warn that broadcast EIR behavior is poor. Card-mode Dino has limited MMIO support and explicitly rejects PCI-PCI bridges. IRQ fixup for unassigned devices is enabled but platform mappings vary. Config and I/O access depend on the spinlock and Dino address-stepping workaround. Some error paths after allocations/requested resources do not fully unwind.

## Test Signals
Boot tests should cover built-in Dino, Cujo, and card-mode Dino, config read/write correctness, I/O port access, level-triggered shared IRQs, stuck interrupt warnings, SMP affinity updates, PCI bridge resource assignment, card-mode 8 MB LMMIO allocation, Cirrus CardBus and Tulip fixups, Cujo 2.0 workaround interaction with CCIO, and root bus numbering across multiple bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/dino.c -->
