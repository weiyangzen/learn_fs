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

Externally visible init entry points include `snbep_uncore_cpu_init()`, `snbep_uncore_pci_init()`, `ivbep_uncore_cpu_init()`, `ivbep_uncore_pci_init()`, `knl_uncore_cpu_init()`, `knl_uncore_pci_init()`, `hswep_uncore_cpu_init()`, `hswep_uncore_pci_init()`, `bdx_uncore_cpu_init()`, `bdx_uncore_pci_init()`, `skx_uncore_cpu_init()`, `skx_uncore_pci_init()`, `snr_uncore_cpu_init()`, `snr_uncore_pci_init()`, `snr_uncore_mmio_init()`, `icx_uncore_cpu_init()`, `icx_uncore_pci_init()`, `icx_uncore_mmio_init()`, `spr_uncore_cpu_init()`, `spr_uncore_pci_init()`, `spr_uncore_mmio_init()`, `gnr_uncore_cpu_init()`, `gnr_uncore_pci_init()`, `gnr_uncore_mmio_init()`, `dmr_uncore_pci_init()`, and `dmr_uncore_mmio_init()`.

## Control Flow

The file starts with register addresses, bit masks, and raw event masks grouped by platform and PMON block. These constants drive later descriptors. It then defines common Sandy Bridge-EP style MSR and PCI operations. PCI boxes use config-space reads and writes for box control, event control, and 64-bit counter reads. MSR boxes use `rdmsrq()`/`wrmsrq()` and optionally program `event->hw.extra_reg` before enabling an event. Platform variants reuse these callbacks when register semantics match, and override only the pieces that differ.

Shared-register control is a major control path. `__snbep_cbox_get_constraint()` protects `box->shared_regs[0]` with `raw_spin_lock_irqsave()`, compares the requested filter bits against currently allocated filter state, increments atomic per-field reference counts, and returns `&uncore_constraint_empty` on a conflict. `snbep_cbox_put_constraint()` releases those references. The generation-specific CBox/CHA `hw_config` functions translate perf `config1` filters into the correct extra register and mask. `snbep_pcu_get_constraint()` allocates one of four PCU occupancy filter lanes, using `snbep_pcu_alter_er()` to shift config fields when it has to move an event to another lane.

PCI bus to package/die mapping is established before legacy PCI PMUs are registered. `snbep_pci2phy_map_init()` locates UBox devices, reads node-id and group-id mapping registers via `upi_nodeid_groupid()`, maps them through `topology_gidnid_map()`, and fills `pci2phy_map` bus-to-die arrays. For larger systems it falls back to `uncore_device_to_die()`. Empty bus slots are backfilled either forward or reverse depending on the platform, so later PCI PMU probes can derive a die id from a device bus.

The rest of the file is platform-section driven. SNBEP defines UBox/CBox/PCU MSR PMUs and HA/IMC/QPI/R2PCIe/R3QPI PCI PMUs. IVBEP adjusts initialization masks, expands CBox filters, and adds IRP with non-uniform offsets. KNL uses UBox/CHA/PCU MSR PMUs plus PCI IMC, EDC, M2PCIe, and IRP PMUs. HSWEP and BDX add SBox handling, capability checks, and model-specific constraints. SKX introduces CHA, IIO, free-running IIO counters, UPI/M2M/M2PCIe/M3UPI, and dynamic topology mapping. SNR and ICX add SAD_CONTROL mapping and MMIO IMC. SPR, GNR, and DMR increasingly use discovery-table generic uncore descriptors with static customization and special free-running PMUs.

## State And Persistence Behavior

There is no filesystem persistence. Runtime state is in kernel globals, static descriptor tables, and per-box/per-event perf structures.

The selected init function assigns arrays into `uncore_msr_uncores`, `uncore_pci_uncores`, and `uncore_mmio_uncores`. PCI init functions assign `uncore_pci_driver` and sometimes `uncore_pci_sub_driver`. CPU init functions mutate static descriptors for detected hardware, such as CBox/CHA `num_boxes`, BDX SBox presence, PCU constraints, and free-running box counts. Mapping setup allocates `type->topology` and dynamic sysfs attributes, while cleanup hooks free those allocations. Discovery-table paths allocate or replace `type->boxes` red-black trees for special cases such as SPR UPI/M3UPI.

Event-local state lives in `perf_event->hw`: `config`, `config_base`, `event_base`, `idx`, `extra_reg`, `branch_reg`, and fixed/free-running counter metadata. Shared filter state lives in `box->shared_regs[]` and is protected by spinlocks plus atomic reference counts. MMIO PMUs map physical register windows into `box->io_addr`; `uncore_mmio_exit_box` releases them.

## Dependencies And Integration Points

Core dependencies are x86 perf uncore infrastructure, PCI APIs, topology helpers, MSR accessors, MMIO accessors, sysfs attribute helpers, CPU model/feature metadata, and generic uncore discovery support.

Important integration surfaces include perf event creation through `format_group`, `event_mask`, `event_mask_ext`, constraints, and `ops`; sysfs exposure under `/sys/devices/uncore_*`; PCI registration through platform ID tables; MSR registration through model-specific register addresses; MMIO IMC registration through memory-controller base address registers; and discovery-table registration through `intel_uncore_generic_init_uncores()` and discovery unit trees.

## Risks And Edge Cases

The main risk is hardware specificity. Incorrect register offsets, event masks, PCI IDs, device/function encodings, box counts, or topology mappings can silently expose wrong counters or fail PMU registration only on affected server platforms.

Shared-filter constraints are subtle. A missing filter bit, wrong mask, or incorrect reference accounting in the CBox/CHA/PCU paths can permit incompatible events to run together or unnecessarily reject valid groups. Fake boxes are treated specially and must not consume shared state.

PCI reference handling and topology allocation cleanup are important because many paths iterate with `pci_get_device()` or allocate dynamic sysfs attributes. MMIO handling is risk-prone because physical addresses are derived from PCI config registers. Several paths also work around known firmware or hardware errata, including Haswell SBox bit-by-bit init, SPR CBO count replacement, and SPR UPI/M3UPI location replacement.

## Test Signals

Useful validation signals are build-time and hardware-runtime. Build the x86 perf subsystem with this file enabled; boot on matching platforms and check expected `/sys/devices/uncore_*` PMUs, `format/` files, `events/` aliases, mapping files, and aliases; run `perf list uncore`; run `perf stat -e` on representative raw and named uncore events; validate multi-socket and multi-die bus-to-die mapping; exercise compatible and conflicting filtered event groups; and verify MMIO IMC counters under memory traffic.
