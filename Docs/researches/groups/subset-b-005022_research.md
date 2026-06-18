# Research: subset-b-005022

Grouped research for Linux perf PMU drivers under `sources/distributed-fs/ceph-client/drivers/perf`. Each section preserves the source path and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/cxl_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/cxl_pmu.c

Purpose: Implements the CXL 3.0 Component PMU perf driver for CXL PMU devices. It discovers CPMU capabilities from MMIO registers, exposes supported CXL events through perf sysfs, allocates fixed or configurable counters, handles overflow interrupts, and migrates its perf context/IRQ affinity across CPU hotplug.

Important APIs, types, and functions: `struct cxl_pmu_info` stores the `struct pmu`, MMIO base, counter bitmap state, event capability lists, IRQ, CPU owner, and HDM filter support. `struct cxl_pmu_ev_cap` records event capability VID/GID/mask mappings for fixed and configurable counters. `cxl_pmu_parse_caps()` reads `CXL_PMU_CAP_REG`, counter configuration registers, and event capability registers to build those lists. Perf callbacks include `cxl_pmu_event_init()`, `cxl_pmu_event_add()`, `cxl_pmu_event_del()`, `cxl_pmu_event_start()`, `cxl_pmu_event_stop()`, `cxl_pmu_read()`, `cxl_pmu_enable()`, and `cxl_pmu_disable()`. Sysfs groups expose `events`, `format`, and `cpumask`; HDM filter fields are hidden when unsupported.

Control flow: Module init registers a CPU hotplug state and the CXL driver. Probe allocates state, parses capabilities, allocates the active event array, derives a `cxl_pmu_mem<assoc>.<index>` name, requests the discovered MSI vector from the parent PCI device, adds a CPU hotplug instance, and registers the perf PMU. Event init rejects sampling and task-bound use, validates VID/GID/mask against fixed or configurable capability lists, and pins events to `on_cpu`. Add chooses a fixed counter if available or a free configurable counter, then optional start programs filters, event group/index, mask, threshold, edge/invert, interrupt-on-overflow, freeze-on-overflow, and enable bits. IRQ reads the overflow bitmap, updates each active event with overflow-aware delta accounting, and clears the hardware overflow status.

State and persistence: Runtime state is entirely in kernel memory plus device MMIO registers. `used_counter_bm` and `conf_counter_bm` protect allocation; `hw_events` maps counters to active perf events; `prev_count` in `struct hw_perf_event` drives delta calculation. Device-managed allocations and `devm_add_action_or_reset()` unwind perf and CPU-hotplug registration.

Dependencies and integration: Depends on CXL core headers and bus registration (`cxl_driver_register`, `MODULE_ALIAS_CXL`), PCI IRQ vectors, Linux perf uncore PMU APIs, sysfs attribute groups, and CPU hotplug helpers. The driver imports the `CXL` namespace.

Risks and test signals: Probe fails if counters are not writable while frozen or if no IRQ is advertised, so test hardware must expose compliant CXL CPMU capabilities. Edge cases include correct masking for sub-64-bit counters, fixed/configurable capability conflicts, HDM filter visibility, shared IRQ handling, and CPU hotplug migration. Useful signals are `perf list` event visibility matching event capability registers, `perf stat -e cxl_pmu_mem*/.../`, overflow interrupt delivery, and hot-unplug migration without lost affinity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/cxl_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/dwc_pcie_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/dwc_pcie_pmu.c

Purpose: Provides a perf PMU for Synopsys DesignWare PCIe Root Port RAS DES vendor capabilities. It supports manually controlled time-based counters and per-lane event counters for PCIe/CCIX link activity, discovered by scanning PCIe VSEC capabilities.

Important APIs, types, and functions: `struct dwc_pcie_pmu` holds the perf PMU, root-port PCI device, RAS DES offset, lane count, one active time-based event, lane event bitmap, CPU hotplug node, and active CPU. `struct dwc_pcie_dev_info` tracks synthetic platform devices created for matching PCI devices. Key paths are `dwc_pcie_des_cap()`, `dwc_pcie_register_dev()`, `dwc_pcie_pmu_probe()`, `dwc_pcie_pmu_event_init()`, `dwc_pcie_pmu_event_add()`, `dwc_pcie_pmu_event_start/stop/del()`, and `dwc_pcie_pmu_event_update()`.

Control flow: Module init scans all PCI devices for matching DWC RAS DES VSECs, creates platform devices, sets up CPU hotplug, registers the platform driver, and installs a PCI bus notifier for hotplug add/delete. Probe reconstructs the PCI device from SBDF platform ID, validates the VSEC, computes link width, names the PMU `dwc_rootport_<sbdf>`, adds CPU hotplug, and registers perf callbacks. Event init validates PMU type, rejects sampling/task events, checks group PMU compatibility, validates lane bounds, and enforces that a group has at most one time-based event and no duplicate lane event/group slots.

State and persistence: State is volatile in kernel memory and PCI config space. Lane event occupancy is tracked in a bitmap indexed by group 6/7 event number; the time-based counter is exclusive via `time_based_event`. Counter values live in RAS DES registers and are read/cleared through PCI config operations.

Dependencies and integration: Integrates with PCI enumeration and hotplug notifier APIs, DesignWare PCIe VSEC ID tables from `<linux/pcie-dwc.h>`, platform devices, perf PMU registration, CPU hotplug migration, and sysfs `events`, `format`, and `cpumask` groups.

Risks and test signals: The driver uses PCI config-space operations for live counter control, so races around hot-unplug and stale `pdev` references are important. Time-based 64-bit reads use a high/low/high loop; tests should exercise wrap and consistency. Signals include platform device creation for each VSEC, `perf list` lane/time events, rejection of invalid lanes and duplicate grouped lane events, hotplug add/remove cleanup, and context migration when the owner CPU goes offline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/dwc_pcie_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/fsl_imx8_ddr_perf.c -->
# sources/distributed-fs/ceph-client/drivers/perf/fsl_imx8_ddr_perf.c

Purpose: Implements the Freescale/NXP i.MX8 DDR and DB perf PMU. It exposes DDR controller transaction, command, queue, credit, and AXI-ID filtered events through perf, handling multiple SoC quirks and two PMU types (`imx8_ddr*` and `imx8_db*`).

Important APIs, types, and functions: `struct ddr_pmu` stores PMU state, MMIO base, IRQ, CPU, active events, counter ownership, IDA instance, and devtype data. `struct fsl_ddr_devtype_data` captures quirks, identifier, and PMU type. Event/filter sysfs is built from `ddr_perf_events_attrs`, format attributes for `event`, `axi_id`, `axi_mask`, `axi_port`, and `axi_channel`, capability attributes under `caps`, and optional `identifier`. Runtime paths are `ddr_perf_event_init()`, `ddr_perf_event_add()`, `ddr_perf_event_start()`, `ddr_perf_event_stop()`, `ddr_perf_event_update()`, and `ddr_perf_irq_handler()`.

Control flow: OF probe maps MMIO, enables all clocks, selects devtype data, allocates a PMU ID, chooses name prefix by DDR vs DB type, sets up a dynamic CPU hotplug state, requests the IRQ, pins it to the chosen CPU, and registers the PMU. Event init rejects sampling and task-bound events, enforces PMU group compatibility, and enforces compatible AXI filters for filtered events. Add programs filter registers for legacy/enhanced/super filter variants, allocates counter 0 only for cycles and counters 1-3 for other events, stores the event, and optionally starts it. IRQ is driven by cycle-counter overflow; it drains all active events and restarts the cycle counter.

State and persistence: Counter ownership is in `events[NUM_COUNTERS]`; `active_counter` keeps the cycle counter running while any event is active. Hardware counters are cleared after every read. Filter programming is global or per-counter depending on quirk flags, so grouped filtered events must share compatible filters.

Dependencies and integration: Uses platform/OF matching, clock bulk enable, MMIO, IRQ affinity, Linux perf PMU callbacks, IDA allocation, CPU hotplug, and NXP device-tree compatible strings for i.MX8 variants.

Risks and test signals: Risks include filter incompatibility across grouped events, AXI mask/channel bit inversion errors, cycle-counter bias handling on enhanced-filter SoCs, and event loss when non-cycle counters overflow before the cycle IRQ drains them. Test with `perf stat` on each advertised event, DB-type visibility restrictions, invalid filter group rejection, IRQ affinity migration, and overflow warning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/fsl_imx8_ddr_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/fsl_imx9_ddr_perf.c -->
# sources/distributed-fs/ceph-client/drivers/perf/fsl_imx9_ddr_perf.c

Purpose: Implements the NXP i.MX9 DDRC PerfMon PMU for i.MX91/93/94/95. It exposes reference and counter-specific DDR controller events, supports AXI ID/mask filters with v1/v2 layouts, and manages a 64-bit cycle counter plus ten normal counters.

Important APIs, types, and functions: `struct ddr_pmu` tracks `struct pmu`, MMIO base, active CPU, IRQ, IDA ID, event array, active count, and `imx_ddr_devtype_data`. Event descriptors use `struct imx9_pmu_events_attr` with optional device-type visibility. Key helpers include `ddr_perf_counter_global_config()`, `ddr_perf_counter_local_config()`, `imx93_ddr_perf_monitor_config()`, `imx95_ddr_perf_monitor_config()`, `ddr_perf_alloc_counter()`, `ddr_perf_event_add()`, and `ddr_perf_irq_handler()`.

Control flow: Probe maps MMIO, initializes PMU callbacks, reads match data, allocates an ID/name, installs CPU-hotplug callbacks, requests and pins IRQ, and registers perf. PMU enable globally freezes/resets then enables interrupts and freeze-on-condition. Event add decodes event ID and requested counter from `config`, allocates the dedicated cycle counter, a requested counter-specific slot, or any free normal counter, programs AXI filter registers for v1/v2 devices, and starts if requested. Interrupt updates all active counters, clears counters, and re-enables global monitoring.

State and persistence: State is volatile. `events[11]` owns counters and `active_events` counts scheduled events. Hardware counters are cleared after reads; global control register freezes all counters on disable/overflow. Filter state is in PMCFG registers and depends on SoC generation.

Dependencies and integration: Uses OF platform matching, perf PMU sysfs groups, MMIO, IRQ affinity, CPU hotplug migration, and IDA naming. It does not enable clocks itself, unlike the i.MX8 driver.

Risks and test signals: Counter encoding is easy to misuse because `event` spans both event ID and counter-specific bits. V1/v2 filter programming has distinct register layouts and visibility rules. Probe error handling should be checked for `ida_alloc()` failures and IRQ affinity failures. Test signals are event visibility by compatible string, dedicated counter allocation rejection, overflow IRQ updates, AXI filter counts, and CPU offline migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/fsl_imx9_ddr_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/fujitsu_uncore_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/fujitsu_uncore_pmu.c

Purpose: Provides ACPI platform perf PMUs for Fujitsu uncore MAC and PCI blocks. Both variants share generic counter control while exposing different event catalogs and names derived from ACPI UID fields.

Important APIs, types, and functions: `struct uncore_pmu` stores counter count, `struct pmu`, MMIO registers, active events, used bitmap, CPU, IRQ, and device. Counter paths are `fujitsu_uncore_counter_start()`, `fujitsu_uncore_counter_stop()`, `fujitsu_uncore_counter_update()`, and `fujitsu_uncore_init()`. Perf callbacks include `fujitsu_uncore_event_init/add/del/start/stop/read()` and `fujitsu_uncore_pmu_enable/disable()`. ACPI IDs `FUJI200C` and `FUJI200D` select MAC or PCI event groups.

Control flow: Module init registers a CPU hotplug state and the platform driver. Probe reads ACPI UID, allocates state, chooses MAC vs PCI counter count/event groups/name, allocates event and bitmap arrays, maps MMIO, resets hardware, requests IRQ, sets IRQ affinity, adds hotplug instance, and registers perf. Event init rejects sampling and CPU-less task mode, validates group capacity, and pins the event to the selected CPU. Add allocates one of eight counters, start writes event type, enables interrupt, and enables the counter. IRQ reads overflow status, clears it, and updates active events.

State and persistence: State is in device memory and MMIO only. The used bitmap owns counters; `events[idx]` maps counters to perf events; `prev_count` tracks deltas. Remove disables PMU control, unregisters perf, and removes CPU hotplug.

Dependencies and integration: Uses ACPI matching and UID parsing, platform MMIO/IRQ resources, perf PMU APIs, CPU hotplug, IRQ affinity, and sysfs format/events/cpumask groups.

Risks and test signals: The PMU advertises `PERF_PMU_CAP_NO_INTERRUPT` despite requesting overflow IRQs, which should be verified against perf semantics. Group validation counts only number of PMU events, not event-code validity beyond 8-bit masking. Test with both ACPI IDs, event listing, overflow IRQ update, NUMA-local CPU migration on online/offline, and UID-derived names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/fujitsu_uncore_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Kconfig

Purpose: Defines build-time configuration entries for HiSilicon SoC and PCIe PMU drivers and the HNS3 PMU driver.

Important APIs/types/functions: The file has three tristate symbols: `HISI_PMU` for ACPI ARM64 uncore L3C/HHA/DDRC and related SoC PMUs, `HISI_PCIE_PMU` for HiSilicon PCIe RCiEP PMUs, and `HNS3_PMU` for HNS3 PCI PMUs.

Control flow: Kconfig symbols control which objects the sibling Makefile builds. `HISI_PMU` depends on `ARM64 && ACPI`; `HISI_PCIE_PMU` depends on `PCI && ARM64`; `HNS3_PMU` depends on PCI and either ARM64 or compile testing.

State and persistence: No runtime state; selections persist through kernel configuration.

Dependencies and integration: Integrates with the kernel Kconfig system and `drivers/perf/hisilicon/Makefile`.

Risks and test signals: Dependency mistakes can hide drivers on supported systems or allow unsupported builds. Test with `make olddefconfig`, `allyesconfig`, `COMPILE_TEST`, ARM64 ACPI builds, and checking expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Makefile

Purpose: Maps HiSilicon perf Kconfig symbols to object files.

Important APIs/types/functions: `obj-$(CONFIG_HISI_PMU)` builds the common `hisi_uncore_pmu.o` plus L3C, HHA, DDRC, SLLC, PA, CPA, UC, NoC, and MN uncore PMU modules. `obj-$(CONFIG_HISI_PCIE_PMU)` builds `hisi_pcie_pmu.o`; `obj-$(CONFIG_HNS3_PMU)` builds `hns3_pmu.o`.

Control flow: Kernel kbuild expands selected config symbols into object lists during build.

State and persistence: No runtime state; build artifact selection is determined by `.config`.

Dependencies and integration: Closely tied to `Kconfig` and the shared `hisi_uncore_pmu` helper used by most objects in the `CONFIG_HISI_PMU` bundle.

Risks and test signals: Adding a new uncore file without updating this list prevents builds; building dependent uncore files without the helper object breaks links. Test by toggling each config and running ARM64 build/link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_pcie_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_pcie_pmu.c

Purpose: Implements the HiSilicon PCIe PMU for Huawei RCiEP PCI devices. It monitors PCIe bandwidth, latency, utilization, and packet/time companion metrics through BAR2 registers and exposes filters for event, threshold, trigger, length mode, root port, and requester BDF.

Important APIs, types, and functions: `struct hisi_pcie_pmu` stores eight active counter events, PCI device, PMU, BAR base, IRQ, identifier, monitored BDF range, and CPU owner. Filter extractors decode `config`, `config1`, and `config2`. Key functions are `hisi_pcie_pmu_get_event_ctrl_val()`, `hisi_pcie_pmu_valid_filter()`, `hisi_pcie_pmu_validate_event_group()`, `hisi_pcie_pmu_get_event_idx()`, `hisi_pcie_pmu_start/stop/add/del/read()`, `hisi_pcie_pmu_irq()`, and PCI probe/remove helpers.

Control flow: Module init registers a fixed CPU hotplug state and PCI driver. Probe enables the PCI device, requests BAR2, maps it, reads BDF range/info/version registers, requests one MSI vector, adds CPU hotplug, and registers perf. Event init chooses normal vs extended counter base from bit 16 of the event code, rejects sampling/task events, validates threshold/trigger limits and requester/root-port filters, validates grouped events while allowing related events with identical control values to share counters, and pins events to `on_cpu`. Start programs event control, enables counter/interrupt, initializes both normal and ext counters to `BIT_ULL(63)`, and updates userspace.

State and persistence: State is runtime-only. `hw_events[idx]` owns hardware counters; related grouped events can share a counter. Hardware counter registers are reset around starts and overflow IRQs. BDF range and identifier are read from hardware and exposed in sysfs.

Dependencies and integration: Uses PCI device IDs, MSI, BAR mapping, PCI topology helpers (`pcie_find_root_port`), perf PMU callbacks, sysfs groups, CPU hotplug, IRQ affinity, and Huawei vendor ID `0xa12d`.

Risks and test signals: BDF validation depends on PCI topology and proper refcounting; related-event sharing can be broken if group leaders differ; unsupported events may make counters unwritable, handled by period verification. Test filter rejection, shared latency/count event groups, overflow MSI accounting, sysfs BDF metadata, CPU hotplug affinity, and module remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_pcie_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_cpa_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_cpa_pmu.c

Purpose: Provides the HiSilicon Coherency Protocol Agent uncore PMU shell over the shared `hisi_uncore_pmu` framework.

Important APIs, types, and functions: Device-specific ops implement counter offsets, 64-bit reads/writes, two packed event-type registers, global counter start/stop, per-counter enable/interrupt mask, interrupt status/clear, and CPA power-management disable/enable. `hisi_cpa_pmu_dev_probe()` initializes topology, MMIO, IRQ, counter metadata, attribute groups, and framework ops.

Control flow: ACPI match `HISI0281` binds the platform driver. Probe requires `sicl_id` and `index_id`, maps resources, reads `CPA_VERSION`, initializes IRQ through the common helper, names the PMU `hisi_sicl%d_cpa%d`, initializes the common PMU, disables CPA power management, adds CPU hotplug, and registers perf. Remove unregisters perf, removes hotplug, and re-enables CPA power management.

State and persistence: Runtime state is in `struct hisi_pmu` plus CPA MMIO registers. Disabling PM is a persistent hardware side effect for the device lifetime and is restored on failure/remove.

Dependencies and integration: Depends on ACPI properties, platform MMIO/IRQ resources, the exported HiSilicon uncore framework, perf PMU registration, CPU hotplug, and `MODULE_IMPORT_NS("HISI_PMU")`.

Risks and test signals: Failure paths must restore PM control when hotplug or perf registration fails. Event encoding is limited to 8-bit event types but sysfs advertises `config:0-15`. Test ACPI topology parsing, PM restore on probe failure/remove, interrupt overflow handling through the common ISR, and advertised CPA events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_cpa_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_ddrc_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_ddrc_pmu.c

Purpose: Implements HiSilicon DDR Controller uncore PMUs for three ACPI generations. It supports fixed-counter v1 hardware and programmable v2/v3 hardware through the common uncore framework.

Important APIs, types, and functions: `struct hisi_ddrc_pmu_regs` abstracts generation-specific offsets. `hisi_ddrc_pmu_read/write_counter()`, `hisi_ddrc_pmu_write_evtype()`, `hisi_ddrc_pmu_get_event_idx()`, and control/interrupt helpers populate `hisi_uncore_ddrc_ops`. Device info records counter width, event range, attr groups, and private register layout for v1/v2/v3.

Control flow: ACPI IDs `HISI0233`, `HISI0234`, and `HISI0235` select v1, v2, or v3 info. Probe reads topology and `hisilicon,ch-id`, maps MMIO, reads version, requires `sub_id` for v2+, initializes IRQ, selects attributes/counter bits/check range, names the PMU with SCCL/channel and optional sub-id, adds CPU hotplug, initializes common perf callbacks, and registers the PMU.

State and persistence: State is in common `struct hisi_pmu`; v1 uses fixed register offsets and event ID equals counter index, while v2/v3 use programmable event type and 48-bit counters. No disk persistence.

Dependencies and integration: Uses ACPI/platform resources, device properties, shared HiSilicon uncore framework, perf PMU, CPU hotplug, and namespace import.

Risks and test signals: V1 fixed-counter allocation differs from normal bitmap allocation and must prevent duplicate event/counter use. Version/topology property requirements can cause probe failures. Test each ACPI ID, v1 fixed events, v2/v3 programmable events, interrupt masks/status offsets, naming with sub-id, and CPU migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_ddrc_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_hha_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_hha_pmu.c

Purpose: Implements the HiSilicon Hydra Home Agent uncore PMU for v1/v2 hardware. It exposes HHA request, snoop, DDR, retry, and cycle events, with optional v2 filters for source ID, trace tag, and data source socket.

Important APIs, types, and functions: Filter extractors decode `srcid_cmd`, `srcid_msk`, `tracetag_en`, and `datasrc_skt`. HHA ops implement packed event-type programming, counter read/write, global and per-counter enable, interrupt mask/status/clear, and filter enable/disable hooks. Probe helpers read topology, support legacy `_UID` as fallback index, map MMIO, read `HHA_VERSION`, select v1/v2 metadata, and register with the common uncore framework.

Control flow: ACPI IDs `HISI0243` and `HISI0244` bind the driver. Probe validates SCCL and index ID, maps resources, initializes IRQ, chooses 16 48-bit v1 counters or eight 64-bit v2 counters, names the PMU `hisi_sccl%d_hha%d`, adds CPU hotplug, initializes common perf callbacks, and registers perf. The common start/stop paths call HHA-specific filter hooks around counter programming.

State and persistence: Runtime state is in `struct hisi_pmu` and HHA MMIO. Filter registers are shared at PMU level, so enable/disable hooks must clear only fields that were requested by the event.

Dependencies and integration: Depends on ACPI, platform MMIO/IRQ, common HiSilicon uncore helpers, CPU hotplug, perf PMU APIs, and sysfs attribute groups.

Risks and test signals: Shared filter fields can conflict when multiple events request different source/data filters. Legacy `_UID` fallback must be verified on older firmware. Test v1/v2 event visibility, filter sysfs formats, source-ID masking, interrupt-driven overflow accounting, and CPU hotplug migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_hha_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_l3c_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_l3c_pmu.c

Purpose: Implements HiSilicon L3 cache uncore PMUs across v1/v2/v3 hardware, including v3 extension counter banks with separate MMIO/IRQ resources and trace/data filters.

Important APIs, types, and functions: `struct hisi_l3c_pmu` wraps `struct hisi_pmu` and extension bases/IRQs. `hisi_l3c_pmu_get_event_idx()` allocates normal or extension ranges and stores the correct MMIO base in `hw.event_base`. Filter helpers configure request trace tag, core trace tag, data source, and socket filtering. Ops cover event type programming, counter access, multi-bank start/stop, interrupt status aggregation, and filter validation.

Control flow: ACPI IDs select v1/v2/v3 device info. Probe validates SCCL/CCL topology, maps base MMIO, initializes the normal IRQ, initializes extension MMIO/IRQs for v3, expands `num_counters` by extension bank count, names the PMU with SCCL/CCL/sub-id, adds a custom hotplug state, initializes the common PMU, and registers perf. Online/offline callbacks delegate to common CPU migration and then migrate extension IRQ affinities.

State and persistence: Counter allocation spans normal and extension bit ranges in the common used mask. Event MMIO base is per-event, allowing common paths to operate on normal or extension registers. Filter state is hardware MMIO and must be cleared on stop.

Dependencies and integration: Uses platform MMIO/IRQ arrays, ACPI matching, common HiSilicon uncore framework, perf PMU, CPU hotplug, sysfs filters, and IRQ affinity.

Risks and test signals: Extension initialization requires enough IRQ resources and matching extra MMIO resources. `ext` filter validation and deprecated/new `tt_core` mutual exclusion are important. Test v1/v2/v3 event visibility, extension event allocation, aggregate overflow status, extension IRQ affinity migration, and filter cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_l3c_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_mn_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_mn_pmu.c

Purpose: Implements the HiSilicon MN uncore PMU for DVM/barrier request and latency events.

Important APIs, types, and functions: `struct hisi_mn_pmu_regs` abstracts register offsets. Device-specific ops implement 48-bit counter access, packed event-type programming, global/per-counter control, interrupt mask/status/clear, and `hisi_mn_pmu_counter_flush()` to drain dynamic requests after stopping counters.

Control flow: ACPI ID `HISI0222` selects v1 metadata. Probe reads SCL and index topology, maps MMIO, initializes IRQ, reads version, names the PMU `hisi_scl%d_mn%d`, adds a dynamic CPU hotplug instance with devm cleanup, initializes common perf callbacks, registers perf, and adds devm unregister cleanup. There is no remove callback; cleanup is devm/platform-driver driven.

State and persistence: Runtime state is common `struct hisi_pmu`. Stop clears perf enable and polls dynamic control until outstanding requests complete or a timeout warns, improving latency counter accuracy.

Dependencies and integration: Uses ACPI/platform resources, property topology, `readl_poll_timeout_atomic`, common HiSilicon uncore helpers, perf, CPU hotplug, IRQ, and devm action cleanup.

Risks and test signals: The driver suppresses bind attributes because unbinding while sampling is unsafe. Flush timeout behavior is a key accuracy and reliability risk. Test event visibility, latency event reads after stop, timeout warning path, CPU hotplug cleanup via devm actions, and platform driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_mn_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_noc_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_noc_pmu.c

Purpose: Implements the HiSilicon NoC uncore PMU for network-on-chip flow, buffer, failure, and cycle events.

Important APIs, types, and functions: `struct hisi_noc_pmu_regs` stores register offsets. Filter extractors decode channel (`ch`) and global trace-tag enable (`tt_en`). Ops implement event type programming, four 64-bit counters, counter enable/disable, no-op interrupt mask hooks, global PMU start/stop, overflow status clear, and channel/global trace-tag filter hooks.

Control flow: ACPI ID `HISI04E0` binds v1 metadata. Probe reads SCL, index, and sub-id topology, maps MMIO, selects metadata, reads version, adds CPU hotplug with devm cleanup, initializes the common PMU, names it `hisi_scl%d_noc%d_%d`, registers perf, and installs devm unregister cleanup. Event allocation rejects a new event when its global trace-tag setting conflicts with currently scheduled events.

State and persistence: State is common `struct hisi_pmu`; channel selection is per counter, while trace-tag filtering is global and only cleared when the last counter stops. The hardware has no supported interrupt masking, but overflow status is still read/cleared by common paths if used.

Dependencies and integration: Uses ACPI/platform matching, common HiSilicon uncore framework, perf sysfs groups, CPU hotplug, and devm cleanup.

Risks and test signals: Global trace-tag state can affect all active counters, making group compatibility critical. Channel 0 resets counter value, so default channel 7 is used when unspecified. Test channel defaulting, trace-tag conflict rejection, PMU start/stop, overflow status clearing, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_noc_pmu.c -->
