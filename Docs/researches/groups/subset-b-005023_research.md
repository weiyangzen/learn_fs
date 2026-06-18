# subset-b-005023 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pa_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pa_pmu.c

Purpose: This file is the HiSilicon Protocol Adapter uncore PMU leaf driver. It exposes PA traffic events through Linux perf, using the shared HiSilicon uncore framework in `hisi_uncore_pmu.c` for perf lifecycle, interrupt handling, CPU hotplug ownership, and sysfs helper behavior.

Important APIs, types, and functions: `struct hisi_pa_pmu_int_regs` abstracts interrupt mask, clear, and status offsets so H32 and H60 PA variants can share the same operations. The `HISI_PMU_EVENT_ATTR_EXTRACTOR()` helpers decode `config1` filter fields for target ID, source ID, and trace tag enable. `hisi_pa_pmu_read_counter()`, `hisi_pa_pmu_write_counter()`, `hisi_pa_pmu_write_evtype()`, counter enable/disable, interrupt enable/disable, and interrupt status functions implement `struct hisi_uncore_ops`. `hisi_pa_pmu_init_data()` reads firmware topology, maps MMIO, and reads `PA_PMU_VERSION`. `hisi_pa_pmu_probe()` allocates `struct hisi_pmu`, names the PMU as `hisi_sicl%d_%s%d`, registers a CPU hotplug instance, initializes common perf callbacks with `hisi_pmu_init()`, and registers with perf.

Control flow: module init installs the PA CPU hotplug state and registers a platform driver. Probe validates `sicl-id` and `idx-id`, binds ACPI match data to variant attributes and interrupt registers, maps registers, requests the platform IRQ through the common ISR, and registers the PMU. At event start, the common framework calls PA operations to program the event type register, configure optional filters, enable overflow interrupts, and enable the counter. Global PMU enable toggles `PA_PERF_CTRL_EN`.

State and persistence: Runtime state is volatile in `struct hisi_pmu`: MMIO base, interrupt number, event slots, used counter bitmap, topology, and current owner CPU. Hardware counters are reset/reloaded by the common period code. No persistent storage is used. Variant state is static const match data and attribute-group tables.

Dependencies and integration points: Depends on ACPI IDs `HISI0273`, `HISI0275`, and `HISI0274`; platform resources; Linux perf PMU callbacks; CPU hotplug state `CPUHP_AP_PERF_ARM_HISI_PA_ONLINE`; and the exported `HISI_PMU` namespace from the common HiSilicon framework. Sysfs exposes format fields, event aliases, cpumask, associated CPUs from the common group, and identifier.

Risks: Filter registers appear global to the PA PMU, so multiple simultaneous filtered events can overwrite shared target/source/trace-tag state if perf schedules incompatible filters together. The common group validation only checks counter count and PMU identity, not filter exclusivity. Probe depends on firmware topology properties; missing `sicl-id` or `idx-id` rejects the device. Interrupt clearing differs for H60 using status-as-clear, so wrong match data can break overflow handling.

Test signals: Build with the HiSilicon uncore framework and PA driver enabled. Boot on matching ACPI hardware and verify `/sys/bus/event_source/devices/hisi_sicl*_pa*` or `hisi_sicl*_h60pa*` exists with expected `events`, `format`, `cpumask`, and `identifier`. Run `perf stat -e <pmu>/rx_req/` or `tx_req` and verify counts advance. Exercise filtered events with `config1` fields and verify teardown clears filter registers. CPU hotplug should migrate `cpumask` and interrupt affinity without losing perf context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pa_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pmu.c

Purpose: This is the reusable HiSilicon uncore PMU framework used by multiple SoC uncore leaf drivers. It supplies sysfs helpers, perf event validation, counter allocation, overflow handling, event start/stop/read logic, CPU hotplug migration, topology parsing, and PMU initialization.

Important APIs, types, and functions: Exported helpers include `hisi_event_sysfs_show()`, `hisi_cpumask_sysfs_show()`, `hisi_uncore_pmu_identifier_attr_show()`, `hisi_uncore_pmu_get_event_idx()`, `hisi_uncore_pmu_isr()`, `hisi_uncore_pmu_init_irq()`, `hisi_uncore_pmu_event_init()`, `hisi_uncore_pmu_add()`, `hisi_uncore_pmu_del()`, `hisi_uncore_pmu_start()`, `hisi_uncore_pmu_stop()`, `hisi_uncore_pmu_read()`, `hisi_uncore_pmu_enable()`, `hisi_uncore_pmu_disable()`, `hisi_uncore_pmu_online_cpu()`, `hisi_uncore_pmu_offline_cpu()`, `hisi_uncore_pmu_init_topology()`, and `hisi_pmu_init()`. It is driven by `struct hisi_pmu` and the leaf-provided `struct hisi_uncore_ops`.

Control flow: Leaf drivers fill `struct hisi_pmu`, provide MMIO operations in `ops`, register hotplug instances, call `hisi_pmu_init()`, then register a perf PMU. `event_init` rejects wrong PMU types, sampling, per-task events, invalid CPU targets, oversized groups, invalid event codes, missing owner CPU, and leaf-specific filter failures. `add` allocates a hardware counter and optionally starts. `start` programs a half-range initial period, reloads if requested, and enables event MMIO. `stop` disables MMIO and updates counts. `read` updates count using a compare/exchange loop. The ISR reads leaf interrupt status, clears each overflow bit, updates the event, and reloads the period.

State and persistence: State lives in memory and device MMIO only. `pmu_events.used_mask` tracks allocated counters and `pmu_events.hw_events[]` maps counter index to `struct perf_event`. `on_cpu` stores the current CPU context for perf scheduling. `associated_cpus` is derived dynamically through hotplug and topology. No persistent files or nonvolatile state are written.

Dependencies and integration points: Integrates with Linux perf core, CPU hotplug, platform IRQ APIs, firmware device properties, ARM MPIDR topology helpers, and the `HISI_PMU` export namespace. Leaf drivers provide register semantics and attribute groups.

Risks: The group validator checks only PMU identity and counter count; it does not model leaf-specific shared filters or mutually exclusive hardware modes. `hisi_uncore_pmu_enable()` starts global counters whenever the used bitmap is non-empty, so corrupted bitmap state would affect all active events. CPU association relies on MPIDR decoding and firmware topology; mismatches can produce nonlocal owner CPUs or no valid owner. The ISR assumes `get_int_status()` returns a bitmask compatible with `for_each_set_bit()` over `num_counters`.

Test signals: Unit-level review should verify every leaf ops table supplies all callbacks used by the common code. Runtime tests should inspect sysfs `cpumask`, `associated_cpus`, and `identifier`, run `perf stat` on leaf events, trigger overflows if practical, and offline/online the owner CPU while an event is active to verify `perf_pmu_migrate_context()` and IRQ affinity changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pmu.h -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pmu.h

Purpose: This header is the contract between the HiSilicon common uncore PMU framework and the individual HiSilicon uncore PMU drivers. It defines event/sysfs macros, core data structures, topology representation, leaf operation callbacks, and exported function prototypes.

Important APIs, types, and functions: `struct hisi_uncore_ops` is the key abstraction and contains callbacks for event validation, event type programming, counter allocation, counter read/write, counter enable/disable, interrupt enable/disable, global start/stop, interrupt status/clear, and optional filter enable/disable. `struct hisi_pmu_dev_info` carries per-compatible metadata such as sysfs groups, counter width, event range, and private register data. `struct hisi_pmu_hwevents` tracks active event pointers and the used counter bitmap. `struct hisi_pmu_topology` records `sccl_id`, `sicl_id` or `scl_id`, `ccl_id`, `index_id`, and `sub_id`. `struct hisi_pmu` embeds `struct pmu` and stores ops, device info, topology, CPU ownership, IRQ, MMIO base, counters, event limit, and identifier.

Control flow: Leaf drivers include this header, define format/event attributes with `HISI_PMU_FORMAT_ATTR()` and `HISI_PMU_EVENT_ATTR()`, decode custom perf config fields with `HISI_PMU_EVENT_ATTR_EXTRACTOR()`, fill a `struct hisi_pmu`, then call exported common functions. The common framework uses the callback table to translate generic perf operations into leaf-specific MMIO accesses.

State and persistence: The header itself has no runtime state, but it defines all in-memory state that persists for a probed PMU lifetime. `HISI_MAX_COUNTERS` bounds bitmap and event arrays. The topology struct uses `-1` sentinel values for absent firmware topology fields.

Dependencies and integration points: Depends on Linux perf, platform device, cpumask, module, device, bitfield, and type headers. It exports common attribute groups and functions from namespace `HISI_PMU`, so leaf modules use `MODULE_IMPORT_NS("HISI_PMU")`.

Risks: Because leaf callbacks are raw function pointers, incomplete ops tables can fail at runtime if the common framework calls a missing mandatory callback. `HISI_PMU_EVENT_ATTR_EXTRACTOR()` assumes the selected bit range maps to `event->attr.config` or `config1` as passed by macro users; mistakes silently decode wrong fields. `HISI_MAX_COUNTERS` must cover all leaf hardware counter counts. Topology union naming means SCCL, SICL, and SCL share storage, so callers must interpret the field according to device type.

Test signals: Compile coverage is important because this header is shared by several modules. Static checks should confirm all leaf ops tables satisfy the callbacks used by `hisi_uncore_pmu.c`. Sysfs format output should match the extractor bit ranges documented by each driver. Runtime tests should verify event IDs are masked by `HISI_EVENTID_MASK` and that counter arrays are not indexed past `HISI_MAX_COUNTERS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_sllc_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_sllc_pmu.c

Purpose: This file implements the HiSilicon system-level last-level cache uncore PMU. It exposes SLLC events and optional target/source/trace-tag filters through perf while reusing the common HiSilicon uncore PMU framework for scheduling, overflow, and hotplug.

Important APIs, types, and functions: `struct hisi_sllc_pmu_regs` captures register offsets and bit shifts for SLLC v2 and v3 variants. Filter helpers decode `config1` fields for target ID minimum/maximum, source ID command/mask, and trace tag enable. `hisi_sllc_pmu_write_evtype()`, counter read/write, counter and interrupt enable/disable, global start/stop, status/clear, and filter operations implement `struct hisi_uncore_ops`. `hisi_sllc_pmu_init_data()` reads topology, maps MMIO, and reads the version register. Static match data supplies v2 and v3 register maps.

Control flow: module init creates the SLLC CPU hotplug state and registers the platform driver. Probe allocates a `struct hisi_pmu`, validates `sccl-id` and `idx-id`, selects match data for `HISI0263` or `HISI0264`, maps MMIO, requests IRQ, sets eight 64-bit counters and event limit `0xff`, registers a hotplug instance, initializes the common PMU, and registers a named PMU such as `hisi_sccl%d_sllc%d`. At event start, common code writes the event type, configures optional filters, enables interrupts, enables the counter, and starts global counting.

State and persistence: Device lifetime state is in `struct hisi_pmu`; variant register state is static. Hardware filter registers are shared per PMU and are set/cleared when events start/stop. There is no persistent storage. Counter values and overflow reload state are volatile.

Dependencies and integration points: Requires ACPI device IDs, platform memory and IRQ resources, CPU hotplug `CPUHP_AP_PERF_ARM_HISI_SLLC_ONLINE`, perf PMU registration, and common exported HiSilicon framework functions. Sysfs events include receive/transmit request/data and cycles, with format fields for filter controls.

Risks: Filter enable bits (`SLLC_FILT_EN`, trace tag, target, source) are global to the PMU, so concurrent filtered events can conflict. `tgtid_is_valid()` only accepts `max > 0 && max >= min`; target ID zero ranges cannot be expressed as a valid active filter. SLLC v2 and v3 register layouts differ substantially, so wrong ACPI match data would misprogram MMIO. The code sets `pmu_events.attr_groups` to v2 groups for both variants, so event/filter sysfs is shared even when v3 hardware semantics differ.

Test signals: Verify ACPI enumeration creates `hisi_sccl*_sllc*`, sysfs `identifier`, `format`, and event files. Run `perf stat` for `cycles`, `rx_req`, and `tx_req`; verify counts change. Test `config1` filters individually and in combinations. Exercise CPU hotplug and overflow IRQ handling under high event rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_sllc_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_uc_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_uc_pmu.c

Purpose: This file implements the HiSilicon unified cache uncore PMU. It exposes UC traffic, pipeline, ring, and cycle events with optional request trace-tag, source ID, and U-ring channel filtering. It is a leaf driver over the common HiSilicon uncore PMU framework.

Important APIs, types, and functions: `hisi_uc_pmu_check_filter()` validates filter dependencies and warns when channel filtering is requested for an unsupported event range. Filter helpers configure and clear request trace tags, source ID trace tags, and U-ring channel bits. Counter operations include event type programming, global enable, per-counter enable, read/write, interrupt mask/status/clear, and a v2 write-counter erratum path. `hisi_uc_pmu_write_counter()` detects identifier `HISI_PMU_V2` and temporarily enables global counting to provide the clock needed to write counters when disabled.

Control flow: module init allocates a dynamic CPU hotplug state, registers the platform driver, and stores the hotplug state ID globally. Probe allocates `struct hisi_pmu`, sets driver data early, validates `sccl-id`, `ccl-id`, and `sub-id`, maps MMIO, reads the UC version, requests IRQ, fills common fields, registers the hotplug node using devm cleanup actions, calls `hisi_pmu_init()`, registers the perf PMU under a name such as `hisi_sccl%d_uc%d_%d`, and installs a devm unregister action. The driver suppresses bind attributes because unbinding during sampling is documented as unsafe.

State and persistence: Runtime state is in `struct hisi_pmu` and hardware registers. Filter configuration is global per PMU and cleared on event stop. The dynamic hotplug state persists for the module lifetime. No persistent storage is used.

Dependencies and integration points: Depends on ACPI ID `HISI0291`, platform resources, perf PMU APIs, CPU hotplug dynamic states, and the exported common HiSilicon uncore functions. Sysfs exposes event aliases including `sq_time`, `pq_time`, `cpu_rd`, `cycles`, `spipe_hit`, `hpipe_hit`, and ring data counters, plus format fields for `event`, `rd_req_en`, `uring_channel`, `srcid`, and `srcid_en`.

Risks: `srcid_en` depends on `rd_req_en`; the code rejects that invalid combination. However, U-ring channel filtering outside events `0x47` through `0x59` only logs a warning and allows the event, so users may get unfiltered or hardware-specific behavior. Shared filter registers can conflict across concurrently running filtered events. The v2 erratum workaround toggles global enable around counter writes when disabled; regressions here can perturb active state or counts if enable-state detection is wrong.

Test signals: Confirm sysfs PMU name and attributes on `HISI0291` systems. Run basic events and filtered variants, including invalid `srcid_en` without `rd_req_en`, expecting `-EINVAL`. Verify the warning path for unsupported U-ring channel filter. Test on identifier `0x30` hardware or with instrumentation to ensure write-counter erratum path is exercised. CPU hotplug should update the cpumask and migrate perf context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hisi_uncore_uc_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hns3_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hns3_pmu.c

Purpose: This driver exposes the HNS3 PCI endpoint PMU through Linux perf. It measures network datapath bandwidth, packet rate, latency, and interrupt rate using per-event counter blocks, plus paired extended counters for time or packet denominators.

Important APIs, types, and functions: `struct hns3_pmu` stores PCI device, PMU, BAR base, IRQ, owner CPU, identifier, hardware clock frequency, and valid BDF range. `struct hns3_pmu_event_attr` binds each event ID to a supported filter-mode bitmask. Event accessor macros split `config` into subevent, event type, and ext-counter selection and split `config1` into port, TC, BDF, queue, interrupt, and global filter values. Key paths include `hns3_pmu_select_filter_mode()`, BDF and queue validation, filter programming, counter read/write, event init/add/start/stop/del, global enable/disable, MSI IRQ registration, CPU hotplug migration, PCI probe/remove, and sysfs event/filter-mode tables.

Control flow: PCI probe enables the device, maps BAR 2, builds a PMU name from the hardware device ID, reads clock, BDF range, and version, allocates one MSI vector, requests the IRQ, adds a CPU hotplug instance, and registers the PMU. Event init validates perf type, rejects sampling and per-task mode, chooses a provisional hardware slot for validation, selects a legal filter mode from event capabilities and config1, validates groups allowing related primary/ext events to share one hardware slot, and chooses primary or extended counter register. Add either shares a slot with a related event in the same group or allocates a new slot. Start programs filter/control registers, zeros both counters, unmasks overflow interrupt, and enables the slot.

State and persistence: Active event pointers live in `hw_events[8]`; related grouped events can share a slot. Hardware counter blocks are reset on start. The device stores owner CPU and IRQ affinity. No persistent storage is used.

Dependencies and integration points: Integrates with PCI device ID `PCI_VENDOR_ID_HUAWEI, 0xa22b`, BAR 2 MMIO, MSI, CPU hotplug `CPUHP_AP_PERF_ARM_HNS3_PMU_ONLINE`, perf PMU core, sysfs event aliases, filtermode descriptions, BDF range files, and hardware clock frequency.

Risks: `hns3_pmu_event_init()` calls `hns3_pmu_get_event_idx()` before add time but does not reserve the slot, so validation of queue IDs depends on a temporary index that can differ by add time. Related events share hardware slots, but `hns3_pmu_del()` unconditionally clears `hw_events[idx]`; deleting one event in a related pair can orphan the other event's slot association. BDF validation uses `pci_get_domain_bus_and_slot()` and allows only a range read from hardware, so hotplug or virtualized endpoint topology can affect validity. IRQ handler clears overflow without updating counts because hardware restarts counters from zero, so perf users rely on periodic reads for totals.

Test signals: Probe should create `hns3_pmu_sicl_*` with event, filtermode, format, BDF range, identifier, cpumask, and `hw_clk_freq` files. Run paired events such as byte/time or packet/time in one group and confirm they share hardware. Test each filter mode: global, port, port-TC, function, function-queue, and function-interrupt. Validate invalid BDF, nonexistent BDF, and invalid queue paths. Exercise CPU hotplug and MSI overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/hisilicon/hns3_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/marvell_cn10k_ddr_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/marvell_cn10k_ddr_pmu.c

Purpose: This file implements the Marvell CN10K and Odyssey DRAM Subsystem PMU. It exposes programmable DDR controller events plus fixed free-running read and write counters through perf.

Important APIs, types, and functions: `struct cn10k_ddr_pmu` holds PMU registration state, MMIO base, platform data, ops table, owner CPU, active event count, event slots, hrtimer, and hotplug node. `struct ddr_pmu_platform_data` captures per-platform register offsets, counter masks, and CN10K/Odyssey booleans. `struct ddr_pmu_ops` abstracts fixed-counter enable/clear and overflow behavior. Key functions include event sysfs show, event bitmap translation, counter allocation/free, event init/add/start/stop/del/update, global PMU enable/disable, hrtimer overflow polling, platform-specific freerun ops, probe/remove, and CPU offline migration.

Control flow: module init creates a multi hotplug state with only an offline callback and registers the platform driver. Probe obtains OF/ACPI match data, maps the controller resource, selects CN10K or Odyssey ops and attr groups, sets manual mode where needed, creates a unique PMU name from the resource address, initializes an hrtimer, adds the hotplug instance without callbacks, and registers the PMU. Event add allocates either one of eight generic counters or fixed read/write slots, starts the hrtimer on first active event, programs generic event bitmaps or clears fixed counters, and optionally starts counting.

State and persistence: Active events are stored in `events[10]`; `active_events` controls the overflow polling timer. Counter previous values live in perf `hw.prev_count`. Platform data is static. No persistent storage is used. The hrtimer periodically updates overflow-prone counters because hardware has no IRQ path in this driver.

Dependencies and integration points: Supports OF compatible `marvell,cn10k-ddr-pmu` and ACPI IDs `MRVL000A` and `MRVL000C`. Integrates with perf, hrtimer, platform MMIO, and CPU hotplug `CPUHP_AP_PERF_ARM_MARVELL_CN10K_DDR_ONLINE`. Sysfs exposes platform-specific event lists, `format/event`, and `cpumask`. A module parameter `poll_period_sec` controls polling.

Risks: In `cn10k_ddr_perf_event_add()`, if `ddr_perf_get_event_bitmap()` fails after a counter is allocated and `active_events` is incremented, the function returns without freeing the counter or decrementing active state. The counter bounds check uses `counter > DDRC_PERF_NUM_COUNTERS`, so `counter == DDRC_PERF_NUM_COUNTERS` would pass though valid indices end at `DDRC_PERF_NUM_COUNTERS - 1`; current allocation should not produce that value. Overflow handling is timer based, so long poll periods can lose multiple wraps for fixed counters. CN10K and Odyssey register behavior differs and is selected entirely by firmware match data.

Test signals: Verify sysfs PMUs named `mrvl_ddr_pmu_<addr>` with correct CN10K or Odyssey event tables. Run generic events and fixed `ddr_ddr_reads`/`ddr_ddr_writes`. Test invalid raw events for cleanup behavior. Change `poll_period_sec` and verify timer starts only with active events and cancels on last delete. CPU offline should migrate the PMU context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/marvell_cn10k_ddr_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/marvell_cn10k_tad_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/marvell_cn10k_tad_pmu.c

Purpose: This file implements the Marvell CN10K LLC-TAD PMU. TAD counters are distributed across multiple regions, and the driver exposes a single perf PMU whose event reads sum the same counter index across all mapped regions.

Important APIs, types, and functions: `struct tad_region` wraps an MMIO base. `struct tad_pmu` stores PMU state, regions, region count, owner CPU, hotplug node, active event pointers, and counter bitmap. `struct tad_pmu_data` identifies v1 versus v2 event tables. Important functions include `tad_pmu_event_counter_read()`, start/stop/add/del, `tad_pmu_event_init()`, sysfs event show, probe/remove, CPU offline migration, and module init/exit. Register macros map per-counter count registers (`TAD_PFC`) and event select registers (`TAD_PRF`).

Control flow: Probe reads match data, memory resource, and firmware properties `marvell,tad-page-size`, `marvell,tad-pmu-page-size`, and `marvell,tad-cnt`. It maps each distributed TAD PMU page by stepping the parent resource start by `tad-page-size`, assigns attr groups by version, selects the current CPU, registers a dynamic hotplug instance, and registers the PMU named `tad`. Event init rejects events that are not initially disabled or not in `PERF_EVENT_STATE_OFF`, pins event CPU to owner CPU, and stores raw config. Add allocates a free counter bit. Start zeros the counter in every region then writes the event selector to every region. Read sums all region counters and updates the perf count. Stop writes zero selectors, reads a final delta, and marks the event stopped and up to date.

State and persistence: State is volatile in `struct tad_pmu`, the counter bitmap, event pointer array, and hardware registers. No persistent storage is used. Counter values are reset on start.

Dependencies and integration points: Supports OF compatible `marvell,cn10k-tad-pmu` and ACPI IDs `MRVL000B` and `MRVL000D`. Uses perf PMU APIs, platform device resources/properties, dynamic CPU hotplug, and sysfs `events`, `format`, and `cpumask`. It advertises `PERF_PMU_CAP_NO_INTERRUPT` because there is no overflow IRQ handling.

Risks: Probe mutates `res->start` while mapping regions; that is unusual because resources are normally treated as descriptors, and later diagnostics using the same resource may see the advanced start. All instances register with PMU name `tad`, which can collide if multiple devices are present. Event init requires disabled/off state, unlike many other PMU drivers, so common perf usage that starts immediately may fail. No overflow handling means large counts can wrap between reads.

Test signals: Confirm required firmware properties are present and region count matches hardware. Verify one PMU appears with the expected v1 or Odyssey event table. Run disabled-then-enabled `perf stat` events and compare summed counts across regions with direct register observations if available. Exercise more than eight simultaneous events to get `-EAGAIN`. CPU offline should migrate context to another online CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/marvell_cn10k_tad_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/marvell_pem_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/marvell_pem_pmu.c

Purpose: This driver exposes Marvell PEM, a PCIe root-complex performance monitor, as a perf PMU. Each event maps to a fixed free-running 64-bit hardware counter for inbound, outbound, and ATS activity.

Important APIs, types, and functions: `enum pem_events` defines fixed event IDs. `eventid_to_offset_table[]` maps event IDs to MMIO offsets. `struct pem_pmu` stores PMU, base, owner CPU, device, and hotplug node. Key functions are `pem_perf_event_init()`, `pem_perf_read_counter()`, `pem_perf_event_update()`, start/add/stop/del, `pem_pmu_offline_cpu()`, probe/remove, and module init/exit. Sysfs helpers expose event aliases, `format/event`, and `cpumask`.

Control flow: module init registers a CPU hotplug state with an offline callback and registers the platform driver. Probe allocates state, maps the platform resource, fills a perf PMU with callback pointers and attr groups, chooses the current CPU, builds a PMU name from the resource address, adds the hotplug instance, and registers the PMU. Event init validates type, raw event ID range, no sampling, no per-task mode, real CPU target, and no mixed-PMU groups. Add sets `hw.idx` directly to the fixed event ID. Start snapshots the current free-running counter into `prev_count`; stop or read computes deltas.

State and persistence: The driver does not allocate programmable counters because all counters are fixed and free-running. It stores only the owner CPU and MMIO base plus perf event-local previous count. No persistent storage is used, and counters are not reset by this driver.

Dependencies and integration points: Supports ACPI ID `MRVL000E`; integrates with platform MMIO, perf core, CPU hotplug `CPUHP_AP_PERF_ARM_MRVL_PEM_ONLINE`, and sysfs. It does not use interrupts and does not advertise an explicit no-interrupt capability in the PMU struct.

Risks: `eventid_to_offset()` indexes the offset table directly, relying on event init and add range checks to prevent invalid IDs. Counters are free-running and deltas are simple unsigned subtraction, so wrap behavior depends on read frequency and 64-bit width. Because hardware counters are not reset, two perf sessions observe deltas from their start snapshot but cannot isolate activity system-wide. Multiple platform instances are named by resource address, which should be unique but depends on firmware resources.

Test signals: Verify PMU names like `mrvl_pcie_rc_pmu_<addr>` and sysfs event aliases for inbound/outbound/ATS counters. Run `perf stat` on fixed events and confirm counts increase under PCIe traffic. Test invalid raw event IDs return `-EINVAL`. Offline the owner CPU and verify context migration and cpumask update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/marvell_pem_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/nvidia_t410_c2c_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/nvidia_t410_c2c_pmu.c

Purpose: This file implements NVIDIA Tegra410 chip-to-chip PMUs for NVLINK, NVCLINK, and NVDLINK interfaces. It exposes C2C cycle, inbound request/outstanding, and outbound request/outstanding counters, with peer filtering for GPU links.

Important APIs, types, and functions: `struct nv_c2c_pmu_data` describes C2C type, instance count, and PMU name format. `struct nv_c2c_pmu` stores device/ACPI identity, socket, peer type/count, peer instance bitmaps, default filter mask, active and associated CPUs, attribute groups, per-instance MMIO bases, and broadcast base. Important paths include event/group validation, high-low-high 64-bit register read, status checking, filtered counter summation, PMU enable/disable, sysfs identifier/peer/cpumask/event/format groups, CPU hotplug callbacks, ACPI UID parsing, filter initialization from properties, MMIO mapping, PMU registration, and platform probe/remove.

Control flow: Probe builds PMU state from ACPI companion and match data, parses UID as socket, derives name and identifier, initializes peer filters from `cpu_en_mask`, `gpu0_en_mask`, `gpu1_en_mask`, or NVDLINK defaults, maps all per-instance resources plus a broadcast resource, associates CPUs whose NUMA node equals the socket, adds the hotplug instance, fills perf callbacks, and registers the PMU. Event init validates type, event number, non-sampling and non-task constraints, requested CPU within associated CPUs, active CPU availability, and group schedulability. PMU enable writes the broadcast control register to enable all counters if any logical event is active. Reads sum selected peer instances, except cycle reads use one instance because clocks are shared.

State and persistence: State is volatile. Active logical events use a bitmap and event pointer array up to 32 entries, not one hardware counter per event. `peer_insts` bitmaps and `filter_default` persist for device lifetime. Disable updates active events and resets previous counts because hardware restarts counters from zero on re-enable.

Dependencies and integration points: Supports ACPI IDs `NVDA2023`, `NVDA2022`, and `NVDA2020`; platform MMIO resources; ACPI UID; device properties for peer masks; perf PMU core; dynamic CPU hotplug; and sysfs groups tailored to CPU, GPU, or CXL memory peers.

Risks: `read_reg64_hilohi()` returns zero on polling timeout, which can cause a large negative-looking unsigned delta if previous count was nonzero. Overflow status is only warned, not corrected or cleared here. PMU enable/disable controls all instances via broadcast, so concurrent events share lifetime. CPU association assumes `cpu_to_node(cpu) == socket`. Filter masks are limited to low bits of `config1` and default to all peers when zero, which users must understand.

Test signals: On matching ACPI systems, verify PMU names and `peer`, `identifier`, `cpumask`, and `associated_cpus` files. Validate GPU peer format includes `gpu_mask`. Run each event, with default and explicit peer masks. Force CPU hotplug for associated CPUs and confirm active CPU migration. Inspect dmesg for overflow warnings during stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/nvidia_t410_c2c_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/nvidia_t410_cmem_latency_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/nvidia_t410_cmem_latency_pmu.c

Purpose: This driver exposes NVIDIA Tegra410 CPU memory latency counters. It aggregates cycle, read request, and accumulated outstanding request counters across 14 memory-latency PMU instances and three memory controllers per instance.

Important APIs, types, and functions: `struct cmem_lat_pmu` stores PMU registration state, device identity, broadcast and per-instance MMIO bases, associated/active CPU masks, hotplug node, and logical event slots. `read_counter_fn[]` maps event IDs to cycle, request, and accumulated-outstanding read functions. Key functions include event/group validation, event init/add/del/start/stop/read, per-event update, broadcast clock-gate/control writes, PMU enable/disable, sysfs identifier/format/events/cpumask groups, CPU hotplug callbacks, socket CPU association, probe/remove, and module init/exit.

Control flow: Probe requires an ACPI companion, parses ACPI UID as socket, allocates state and name `nvidia_cmem_latency_pmu_%u`, fills perf callbacks, maps 14 instance resources plus one broadcast resource, associates CPUs by NUMA node, adds a hotplug instance, clears hardware counters by enabling clock gate, writing clear, and disabling clock gate, then registers the PMU. Event init validates type, event number, no sampling/per-process/per-task usage, requested CPU in associated mask, active CPU availability, and group schedulability. PMU enable enables clock gate and counters if any logical event is active. PMU disable disables counters, updates each active event before clearing, clears hardware, and disables clock gate.

State and persistence: Active logical events are tracked in a 32-bit bitmap and pointer array. Hardware counters reset on broadcast clear. Previous counts are stored in perf event state and reset to zero after PMU disable because hardware starts from zero on re-enable. No persistent storage exists.

Dependencies and integration points: Supports ACPI ID `NVDA2021`, platform resources, perf PMU core, dynamic CPU hotplug, ACPI UID, and CPU NUMA node association. Sysfs exposes `events/cycles`, `rd_req`, `rd_cum_outs`, `format/event`, `identifier`, `cpumask`, and `associated_cpus`.

Risks: `cmem_lat_pmu_event_update()` returns immediately if `PERF_HES_STOPPED` is set. `cmem_lat_pmu_disable()` calls update after `cmem_lat_pmu_stop()` may have set stopped for individual events, so some disable-time accounting can be skipped depending on perf callback ordering. Overflow status only logs warnings and does not compensate. Reads sum many registers without locking against hardware clear/disable beyond perf PMU serialization. CPU association assumes socket equals NUMA node.

Test signals: Verify ACPI enumeration creates the socket-specific PMU and maps all 15 resources. Run each event and compare request/outstanding movement under memory load. Exercise PMU enable/disable cycles and confirm counts are not lost. Trigger CPU hotplug on associated CPUs. Check dmesg for overflow warnings under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/nvidia_t410_cmem_latency_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/qcom_l2_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/qcom_l2_pmu.c

Purpose: This file implements the Qualcomm Kryo L2 cache PMU. It presents one aggregate perf PMU while managing multiple hardware cluster PMUs, each associated with a CPU cluster and accessed through Kryo indirect L2 registers.

Important APIs, types, and functions: `struct l2cache_pmu` is the aggregate PMU and stores clusters, per-CPU cluster mapping, cpumask, number of counters, and platform device. `struct cluster_pmu` stores per-cluster event pointers, used counter/group bitmaps, IRQ, cluster ID, owner CPU, cluster CPU mask, and a spinlock for RESR updates. Key functions include indirect register wrappers, cluster reset/enable/disable, counter value/enable/interrupt operations, RESR programming, overflow handling, perf enable/disable, event init/add/start/stop/del/read, sysfs attributes, cluster probing, CPU online/offline association and migration, platform probe/remove, and device init.

Control flow: Device init registers the CPU hotplug state and platform driver. Probe initializes the aggregate PMU, reads the number of counters from `L2PMCR`, computes the cycle counter index and present mask, allocates per-CPU cluster pointers, probes child devices as clusters using ACPI UID and IRQ, adds the hotplug instance, and registers `l2cache_0`. CPU online associates the CPU to a cluster using MPIDR affinity, selects an owner CPU when the cluster becomes active, resets hardware, sets IRQ affinity, and enables the IRQ. Event init validates type, no sampling, no per-task mode, event config encoding, mixed PMU groups, same-cluster grouping, and group column exclusion. Start programs cycle counter or event type, RESR group selection, filter mode for all CPUs, interrupt, and counter enable. IRQ handling updates and reloads overflowed counters.

State and persistence: Runtime state is in aggregate and cluster structs plus per-CPU cluster pointers. Used event columns are tracked in `used_groups` because hardware allows only one event from each group at a time. Counter periods are half-range reloads: bit 31 for normal counters and bit 63 for cycle counter. No persistent storage is used.

Dependencies and integration points: Depends on ACPI ID `QCOM8130`, child platform devices for clusters, IRQ resources, CPU hotplug `CPUHP_AP_PERF_ARM_QCOM_L2_ONLINE`, perf PMU APIs, ARM MPIDR topology, and `soc/qcom/kryo-l2-accessors.h` indirect register accessors. Sysfs exposes event aliases, raw format fields, and aggregate cpumask.

Risks: Hardware accessors operate on the current CPU's cluster, so perf CPU pinning and hotplug ownership are critical; wrong CPU association can program the wrong cluster. Cluster ID derivation from MPIDR may need updating for future topology encodings. Group validation only checks direct leader and siblings for column conflicts, so complex group behavior should be tested carefully. `register_l2_cache_pmu_driver()` does not remove the hotplug state if platform driver registration fails. IRQs are disabled when no CPU in a cluster is online, so events cannot run until a cluster owner returns.

Test signals: Boot on supported Qualcomm hardware and verify `l2cache_0` sysfs files. Run cycle and group-coded events with `perf stat`, including conflicting same-group events expecting rejection. Generate enough traffic to trigger overflow IRQs and verify counts continue after reload. Offline owner CPUs to verify cluster migration or IRQ disable when a cluster has no online CPUs. Check probe logs for cluster registration and CPU association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/qcom_l2_pmu.c -->
