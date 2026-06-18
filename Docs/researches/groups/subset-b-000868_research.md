# Research: subset-b-000868

Work item `subset-b-000868` covers two x86 perf-event source files. Each file section below is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_snbep.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_snbep.c

## Purpose

This file implements Intel server uncore PMU support for a long sequence of Xeon and Xeon Phi platforms: Sandy Bridge-EP, IvyTown, Knights Landing, Haswell-EP, Broadwell-EP, Skylake server, Snow Ridge, Ice Lake Xeon, Sapphire Rapids, Granite Rapids, and Diamond Rapids style discovery-table platforms. It is not Ceph-specific code despite living under the imported `distributed-fs/ceph-client` source tree. Its role is to describe package-level performance monitoring units outside the CPU core and wire them into the Linux x86 perf uncore framework.

The code translates platform-specific MSR, PCI config-space, and MMIO PMON register layouts into `struct intel_uncore_type` descriptors, `struct intel_uncore_ops` callbacks, sysfs format/event metadata, PCI ID tables, topology mappings, and initialization entry points. Higher-level uncore code selects these entry points based on CPU model and then registers perf PMUs such as uncore CBox/CHA, UBox, PCU, IMC, IIO, UPI/QPI, M2M, M2PCIe, and free-running bandwidth counters.

## Important APIs, Types, And Data

The primary integration contract is the Intel uncore core API from `uncore.h` and `uncore_discovery.h`. This file fills global framework pointers such as `uncore_msr_uncores`, `uncore_pci_uncores`, `uncore_mmio_uncores`, `uncore_pci_driver`, and `uncore_pci_sub_driver`.

Key data structures:

- `struct intel_uncore_type`: one PMU type descriptor per hardware block. The file fills names, counter counts, box counts, register bases, register offsets, event masks, fixed counter metadata, constraints, operations, event aliases, format groups, topology hooks, and discovery metadata.
- `struct intel_uncore_ops`: callback tables for box initialization, box freeze/unfreeze, event enable/disable, counter reads, event hardware configuration, and shared-register constraint management.
- `struct pci_device_id` and `struct pci_driver`: platform PCI discovery tables for legacy PCI-config uncore PMUs and extra filter devices.
- `struct attribute_group` and format attributes created by `DEFINE_UNCORE_FORMAT_ATTR`: sysfs `format/` metadata describing how perf event fields map into `config`, `config1`, and `config2`.
- `struct uncore_event_desc`: named perf aliases such as IMC `cas_count_read`, `cas_count_write`, QPI events, and free-running bandwidth events with scale/unit metadata.
- `struct event_constraint` and `struct extra_reg`: counter-placement and shared-filter constraints for boxes whose event filters are not per-counter.
- `struct freerunning_counters`: descriptors for free-running MSR/MMIO counters, especially IIO and IMC bandwidth/cycle counters.

Externally visible init entry points include:

- `snbep_uncore_cpu_init()` and `snbep_uncore_pci_init()`.
- `ivbep_uncore_cpu_init()` and `ivbep_uncore_pci_init()`.
- `knl_uncore_cpu_init()` and `knl_uncore_pci_init()`.
- `hswep_uncore_cpu_init()` and `hswep_uncore_pci_init()`.
- `bdx_uncore_cpu_init()` and `bdx_uncore_pci_init()`.
- `skx_uncore_cpu_init()` and `skx_uncore_pci_init()`.
- `snr_uncore_cpu_init()`, `snr_uncore_pci_init()`, and `snr_uncore_mmio_init()`.
- `icx_uncore_cpu_init()`, `icx_uncore_pci_init()`, and `icx_uncore_mmio_init()`.
- `spr_uncore_cpu_init()`, `spr_uncore_pci_init()`, and `spr_uncore_mmio_init()`.
- `gnr_uncore_cpu_init()`, `gnr_uncore_pci_init()`, and `gnr_uncore_mmio_init()`.
- `dmr_uncore_pci_init()` and `dmr_uncore_mmio_init()`.

## Control Flow

The file starts with register addresses, bit masks, and raw event masks grouped by platform and PMON block. These constants drive later descriptors. It then defines common Sandy Bridge-EP style MSR and PCI operations:

- PCI boxes use `snbep_uncore_pci_init_box()`, `snbep_uncore_pci_disable_box()`, `snbep_uncore_pci_enable_box()`, `snbep_uncore_pci_enable_event()`, `snbep_uncore_pci_disable_event()`, and `snbep_uncore_pci_read_counter()`. These functions read and write PCI config dwords for box control, event control, and 64-bit counters.
- MSR boxes use `snbep_uncore_msr_init_box()`, `snbep_uncore_msr_disable_box()`, `snbep_uncore_msr_enable_box()`, `snbep_uncore_msr_enable_event()`, and `snbep_uncore_msr_disable_event()`. They use `rdmsrq()`/`wrmsrq()` and optionally program `event->hw.extra_reg`.
- Platform variants reuse these callbacks when register semantics match, and override only the pieces that differ.

Shared-register control is a major control path:

- `__snbep_cbox_get_constraint()` protects `box->shared_regs[0]` with `raw_spin_lock_irqsave()`, compares the requested filter bits against currently allocated filter state, increments atomic per-field reference counts, and returns `&uncore_constraint_empty` on a conflict. `snbep_cbox_put_constraint()` releases those references.
- `snbep_cbox_hw_config()`, `ivbep_cbox_hw_config()`, `hswep_cbox_hw_config()`, `knl_cha_hw_config()`, `skx_cha_hw_config()`, `snr_cha_hw_config()`, `icx_cha_hw_config()`, and `spr_cha_hw_config()` translate perf `config1` filters into the correct extra register and mask for each generation.
- `snbep_pcu_get_constraint()` allocates one of four PCU occupancy filter lanes, using `snbep_pcu_alter_er()` to shift config fields when it has to move an event to another lane.

PCI bus to package/die mapping is established before legacy PCI PMUs are registered:

- `snbep_pci2phy_map_init()` locates UBox devices, reads node-id and group-id mapping registers via `upi_nodeid_groupid()`, maps them through `topology_gidnid_map()`, and fills `pci2phy_map` bus-to-die arrays. For larger systems it falls back to `uncore_device_to_die()`.
- Empty bus slots are backfilled either forward or reverse depending on the platform, so later PCI PMU probes can derive a die id from a device bus.

The rest of the file is platform-section driven:

- SNBEP defines UBox/CBox/PCU MSR PMUs and HA/IMC/QPI/R2PCIe/R3QPI PCI PMUs. QPI has a special filter path through extra PCI devices.
- IVBEP adjusts initialization masks, expands CBox filter layout, adds IRP with non-uniform counter/control offsets, and has its own PCI IDs.
- KNL uses UBox/CHA/PCU MSR PMUs plus PCI IMC, EDC, M2PCIe, and IRP PMUs, including duplicated PCI IDs distinguished by bus/device/function data.
- HSWEP adds UBox filter support, CBox/SBox/PCU MSR PMUs, SBox special initialization to avoid spurious faults, PCI HA/IMC/IRP/QPI/R2PCIe/R3QPI, and capability probing for limited SBox systems.
- BDX reuses Haswell-EP structures with Broadwell-specific CBox constraints, PCU constraints, and SBox removal on Broadwell-D or limited SBox systems.
- SKX introduces CHA, IIO, IIO free-running, IRP, PCU, PCI IMC/UPI/M2M/M2PCIe/M3UPI, dynamic sysfs mapping attributes, and topology extraction from `SKX_MSR_CPU_BUS_NUMBER` and UPI PCI registers.
- SNR and ICX add MSR IIO/IRP/M2PCIe/CHA/PCU, PCI M2M/UPI/M3UPI, SAD_CONTROL based IIO mapping, and MMIO IMC support through `ioremap()`.
- SPR, GNR, and DMR increasingly use the uncore discovery-table path. Static descriptors customize generic discovered types, provide aliases, add extra free-running PMUs, and work around broken UPI/M3UPI discovery on some SPR systems.

## State And Persistence Behavior

There is no filesystem persistence. Runtime state is in kernel globals, static descriptor tables, and per-box/per-event perf structures.

Persistent-for-boot global effects include:

- The selected init function assigns arrays into `uncore_msr_uncores`, `uncore_pci_uncores`, and `uncore_mmio_uncores`.
- PCI init functions assign `uncore_pci_driver` and sometimes `uncore_pci_sub_driver`.
- CPU init functions mutate static descriptors for detected hardware, such as CBox/CHA `num_boxes`, BDX SBox presence, PCU constraints, and free-running box counts.
- Mapping setup allocates `type->topology` and dynamic sysfs attributes. Cleanup hooks free those allocations.
- Discovery-table paths allocate or replace `type->boxes` red-black trees for special cases such as SPR UPI/M3UPI.

Event-local state lives in `perf_event->hw`: `config`, `config_base`, `event_base`, `idx`, `extra_reg`, `branch_reg`, and fixed/free-running counter metadata. Shared filter state lives in `box->shared_regs[]` and is protected by spinlocks plus atomic reference counts.

MMIO PMUs map physical register windows into `box->io_addr`; `uncore_mmio_exit_box` releases them. Failed MMIO mapping leaves the box inert and logs a warning.

## Dependencies And Integration Points

Core dependencies are x86 perf uncore infrastructure, PCI APIs, topology helpers, MSR accessors, MMIO accessors, sysfs attribute helpers, CPU model/feature metadata, and generic uncore discovery support.

Important integration surfaces:

- Perf event creation consumes the `format_group`, `event_mask`, `event_mask_ext`, constraints, and `ops` populated here.
- `/sys/devices/uncore_*/format`, `/sys/devices/uncore_*/events`, mapping files, and alias files are built from the attribute groups and event descriptors.
- PCI registration depends on the per-platform `pci_device_id` tables and bus-to-die mapping.
- MSR registration depends on model-specific register addresses and available box counts.
- MMIO IMC registration depends on memory-controller PCI config registers that expose MMIO base addresses.
- Discovery-table platforms depend on `intel_uncore_generic_init_uncores()`, discovery unit trees, and type-id constants.

## Risks And Edge Cases

The main risk is hardware specificity. Incorrect register offsets, event masks, PCI IDs, device/function encodings, box counts, or topology mappings can silently expose wrong counters or fail PMU registration only on affected server platforms.

Shared-filter constraints are subtle. A missing filter bit, wrong mask, or incorrect reference accounting in the CBox/CHA/PCU paths can permit incompatible events to run together or unnecessarily reject valid groups. Fake boxes are treated specially and must not consume shared state.

PCI reference handling and topology allocation cleanup are important because many paths iterate with `pci_get_device()` or allocate dynamic sysfs attributes. The code usually calls `pci_dev_put()` and has cleanup routines, but error paths in mapping/discovery code deserve review whenever changed.

MMIO handling is risk-prone because physical addresses are derived from PCI config registers. A bad base, stride, or bounds check can map the wrong window. Event enable/disable paths guard with `box->io_addr` and `uncore_mmio_is_valid_offset()`, but platform constants still carry the correctness burden.

Initialization mutates static descriptors. That is normal for this driver, but it means CPU-model-specific init ordering matters. Reusing a descriptor across related platforms, as with HSWEP/BDX/SKX pieces, requires care when changing constraints or `num_boxes`.

Several paths work around known firmware or hardware errata: Haswell SBox bit-by-bit init, SPR CBO count replacement through `SPR_MSR_UNC_CBO_CONFIG`, and SPR UPI/M3UPI location replacement. Removing or generalizing these paths can regress only specific steppings or SKUs.

## Test Signals

Useful validation signals are mostly build-time and hardware-runtime:

- Build the x86 perf subsystem with this file enabled and watch for missing symbols from `uncore.h`/`uncore_discovery.h`.
- Boot on matching platforms and check that the expected `/sys/devices/uncore_*` PMUs, `format/` files, `events/` aliases, mapping files, and aliases appear.
- Run `perf list uncore` and verify generation-specific aliases such as IMC CAS counts and IIO/IMC free-running bandwidth events.
- Use `perf stat -e` on representative raw and named uncore events, including filtered CBox/CHA events, PCU occupancy events, fixed counters, and free-running counters.
- Test multi-socket and multi-die systems to validate `snbep_pci2phy_map_init()`, UPI/IIO mapping files, and bus-to-die resolution.
- Exercise event groups that should conflict and event groups that should share identical filters to validate constraint paths.
- For MMIO IMC platforms, verify that invalid mapping failures are logged without crashes and valid boxes return nonzero counters under memory traffic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_snbep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/msr.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/msr.c

## Purpose

This file implements the x86 perf `msr` PMU, a small software-facing PMU that exposes selected model-specific-register counters through perf. It provides count-only events for TSC, APERF, MPERF, PPERF, SMI count, PTSC, IRPERF, and CPU thermal margin when supported by the boot CPU and by direct probing.

The PMU does not program hardware counters. It reads existing architectural or vendor MSRs, stores the previous value in each perf event, and reports deltas or snapshots through perf's generic software context.

## Important APIs, Types, And Data

Key types and globals:

- `enum perf_msr_id`: stable event ids used as perf `config` values. The ids run from `PERF_MSR_TSC` through `PERF_MSR_THERM`, with `PERF_MSR_EVENT_MAX` as the upper bound.
- `static struct perf_msr msr[]`: one descriptor per event. Each entry supplies an MSR number, an optional event attribute group, and an availability test. The TSC entry has `.no_check = true` and uses a zero MSR number as a sentinel for `rdtsc_ordered()`.
- `static unsigned long msr_mask`: bitmask produced by `perf_msr_probe()` describing which enum ids are usable on this machine.
- `static struct pmu pmu_msr`: perf PMU callback table registered under the name `msr`.

Availability tests:

- `test_aperfmperf()` checks `X86_FEATURE_APERFMPERF`.
- `test_ptsc()` checks `X86_FEATURE_PTSC`.
- `test_irperf()` checks `X86_FEATURE_IRPERF`.
- `test_therm_status()` checks `X86_FEATURE_DTHERM`.
- `test_intel()` restricts PPERF and SMI to Intel CPUs, leaving final MSR availability to `perf_msr_probe()`.

Sysfs/perf metadata is built with `PMU_EVENT_ATTR_STRING`, `PMU_EVENT_GROUP`, `PMU_FORMAT_ATTR`, and explicit `attribute_group` arrays. The default `events` group always exposes `tsc`; `attr_update` can add supported optional event groups after probing. Thermal margin has additional `.snapshot` and `.unit` event attributes.

## Control Flow

Initialization starts at `msr_init()` via `device_initcall()`:

1. If the boot CPU lacks TSC, it prints a continuation message and leaves the PMU unregistered.
2. It calls `perf_msr_probe(msr, PERF_MSR_EVENT_MAX, true, NULL)` to test the MSR table and populate `msr_mask`.
3. It registers `pmu_msr` as `msr` with `perf_pmu_register()`.

Event creation is handled by `msr_event_init()`:

1. Reject events for another PMU type with `-ENOENT`.
2. Reject sampling by checking `event->attr.sample_period`; this PMU is counting-only.
3. Reject out-of-range `config` values.
4. Apply `array_index_nospec()` before indexing the `msr[]` table.
5. Reject unavailable events whose bit is not present in `msr_mask`.
6. Initialize `event->hw.idx = -1`, `event->hw.event_base = msr[cfg].msr`, and `event->hw.config = cfg`.

Counter reads use `msr_read_counter()`:

- If `event->hw.event_base` is nonzero, read that MSR with `rdmsrq()`.
- Otherwise read the ordered TSC with `rdtsc_ordered()`.

Runtime callbacks are straightforward:

- `msr_event_add()` starts the event when `PERF_EF_START` is set.
- `msr_event_start()` records the current counter in `event->hw.prev_count`.
- `msr_event_stop()` and `msr_event_del()` update the event count.
- `msr_event_update()` reads the current value, atomically swaps `prev_count` using `local64_try_cmpxchg()`, computes a delta, and updates `event->count`.

Special update rules:

- `MSR_SMI_COUNT` deltas are sign-extended from bit 31 before being added, matching a narrower counter width.
- `MSR_IA32_THERM_STATUS` is treated as a snapshot. If bit 31 indicates a valid digital readout, bits 16-21 become the current count; otherwise the event count is set to `-1`.
- Other counters add the unsigned wraparound delta.

## State And Persistence Behavior

There is no persistent storage. System-wide availability state is held in `msr_mask` after boot-time probing. Each perf event stores its selected MSR in `event->hw.event_base`, the enum id in `event->hw.config`, and the previous raw value in `event->hw.prev_count`.

The PMU uses `perf_sw_context`, so events are managed in perf's software context rather than by a fixed hardware counter allocator. It also advertises `PERF_PMU_CAP_NO_INTERRUPT` and `PERF_PMU_CAP_NO_EXCLUDE`, which signals no interrupt-driven sampling and no privilege exclusion filtering.

`msr_event_update()` is written to tolerate an NMI updating `prev_count` concurrently by using a compare-exchange loop around the previous count.

## Dependencies And Integration Points

The file depends on:

- `linux/perf_event.h` for PMU registration and perf callback structures.
- `linux/sysfs.h` for event and format attribute exposure.
- `linux/nospec.h` for bounds-safe array indexing.
- `asm/msr.h` for `rdmsrq()` and `rdtsc_ordered()`.
- `probe.h` for `struct perf_msr` and `perf_msr_probe()`.
- x86 CPU feature and vendor state from `boot_cpu_has()` and `boot_cpu_data`.

Integration points:

- Registered perf PMU name is `msr`.
- User-visible event names include `tsc`, `aperf`, `mperf`, `pperf`, `smi`, `ptsc`, `irperf`, and `cpu_thermal_margin`.
- Event syntax uses `format/event` as `config:0-63`, though valid values are constrained by `PERF_MSR_EVENT_MAX` and `msr_mask`.
- Optional event groups are attached through `pmu_msr.attr_update`, allowing sysfs to reflect probed support.

## Risks And Edge Cases

The PMU assumes boot-CPU feature checks are enough for event availability. On heterogeneous or unusual systems, a feature present on the boot CPU but not on all online CPUs could make per-CPU reads fragile.

`perf_pmu_register()` return value is ignored. If registration fails, the init path does not report or undo anything beyond the failed call.

TSC uses `event_base == 0` as a sentinel, so any future event using MSR 0 would collide with the TSC path. That is intentional for the current table but should be preserved consciously.

The PMU rejects only `sample_period` for unsupported sampling. Other event attributes are mostly ignored because capabilities state no interrupts and no exclude support; tests should verify perf rejects or handles unexpected combinations consistently.

Thermal margin is a gauge-like snapshot, not a monotonically increasing counter. It overwrites `event->count`, while most other events add deltas. Consumers must treat its `.snapshot` metadata accordingly.

SMI count wrap handling relies on 32-bit sign extension. If hardware width differs on a future platform, deltas could be wrong.

## Test Signals

Useful validation signals:

- Build the x86 perf event code and confirm `probe.h` provides `perf_msr_probe()` and `struct perf_msr` with the expected fields.
- Boot on Intel and AMD systems and inspect `/sys/devices/msr/events` and `/sys/devices/msr/format/event`.
- Run `perf list msr` and confirm optional events appear only when feature/probe checks pass.
- Run `perf stat -e msr/tsc/`, `msr/aperf/`, `msr/mperf/`, and other supported events to confirm counts advance.
- Verify `perf stat -e msr/event=0xffff/` and unavailable events fail with `-EINVAL`.
- Verify sampling attempts are rejected because `sample_period` is unsupported.
- On systems with digital thermal status, confirm `msr/cpu_thermal_margin/` reports a snapshot in Celsius or `-1` when invalid.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/msr.c -->
