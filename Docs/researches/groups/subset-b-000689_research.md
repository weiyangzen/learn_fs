# Research: subset-b-000689

Grouped research for ARM64 KVM VGIC/ITS sources. Each section is wrapped for reconciliation into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-its.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-its.c

## Purpose
`vgic-its.c` implements the emulated GICv3 Interrupt Translation Service for KVM guests. It exposes an ITS KVM device, decodes guest ITS commands, maps device/event pairs to LPIs, injects MSIs, tracks ITS device/collection/translation state, supports GICv4 VLPI acceleration hooks, and saves/restores the ITS table ABI used by migration.

## Important APIs, Types, And Functions
The main userspace ABI surface is `kvm_arm_vgic_its_ops`, with `vgic_its_create()`, `vgic_its_destroy()`, `vgic_its_set_attr()`, `vgic_its_get_attr()`, and `vgic_its_has_attr()`. `kvm_vgic_register_its_device()` registers this device when GICv3 VGIC support is registered. `vgic_its_abi` describes table entry sizes and save/restore/commit callbacks; only ABI revision 0 is present, with 8-byte CTE/DTE/ITE entries. LPI-facing APIs include `vgic_add_lpi()`, `vgic_its_resolve_lpi()`, `vgic_its_inject_msi()`, `vgic_its_inject_cached_translation()`, `vgic_msi_to_its()`, `vgic_its_inv_lpi()`, and `vgic_its_invall()`.

ITS state is held in `struct vgic_its` plus linked lists of `its_device`, `its_collection`, and `its_ite`. LPIs live in the VM distributor `lpi_xa`; each ITE holds a reference to a `struct vgic_irq`. The translation cache is an xarray keyed by `(devid,eventid)` and stores extra IRQ references for software MSI fast paths.

## Control Flow
Device creation allocates an ITS, initializes locks/lists/cache, marks the VM as requiring MSI device IDs, initializes BASER/PROPBASER defaults, and commits the ABI. Userspace assigns the ITS MMIO frame through `KVM_DEV_ARM_VGIC_GRP_ADDR`, which registers an `IODEV_ITS` on the KVM MMIO bus.

Guest command processing starts when the guest writes CWRITER or enables CTLR. `vgic_its_process_commands()` walks the circular command buffer at CBASER from CREADR to CWRITER, reads 32-byte commands from guest RAM, and dispatches them through `vgic_its_handle_command()`. MAPD creates or removes devices and ITTs, MAPC creates or retargets collections, MAPI/MAPTI creates ITEs and LPIs, MOVI/MOVALL retarget LPIs, DISCARD/CLEAR remove mappings or pending state, INT injects an LPI, and INV/INVALL reload LPI properties.

MSI injection first tries `vgic_its_inject_cached_translation()`. On a cache miss, `vgic_msi_to_its()` resolves the doorbell GPA to the registered ITS iodev, the ITS lock is taken, and `vgic_its_trigger_msi()` resolves the LPI. Software LPIs set `pending_latch` and queue the IRQ; GICv4-backed LPIs call `irq_set_irqchip_state()` on the host IRQ.

## State And Persistence
Persistent state includes `enabled`, CBASER/CREADR/CWRITER, device and collection BASERs, PROPBASER, device tables, collection tables, ITTs, LPI target, priority, enable, pending, and VLPI hardware mapping. Save/restore is explicit through `KVM_DEV_ARM_ITS_SAVE_TABLES` and `KVM_DEV_ARM_ITS_RESTORE_TABLES`. Save sorts device and ITE lists, writes sparse next-offset encoded DTE/ITE records into guest RAM, and writes CTEs until a terminating invalid entry. Restore scans direct or indirect device tables, collection tables, and ITTs to rebuild lists and LPI references. `kvm_arch_allow_write_without_running_vcpu()` permits table writes during save when `table_write_in_progress` is set, covering dirty-ring tracking.

## Dependencies And Integration Points
This file depends on the common VGIC MMIO dispatcher (`kvm_io_gic_ops`), GICv3 register definitions, KVM guest-memory helpers, xarray, KVM device attributes, VCPU lookup by ID, and GICv4 ITS driver hooks such as `its_map_vlpi()`, `its_unmap_vlpi()`, `its_prop_update_vlpi()`, `its_invall_vpe()`, and vPE data in `vgic_v3_cpu_if`. It integrates with `vgic-mmio-v3.c` via LPI enable/PROP/PEND BASER handling and with `vgic-v3.c` pending table save.

## Risks
The highest-risk areas are lock ordering between `cmd_lock`, `its_lock`, KVM `config_lock`, all-vCPU locking, and xarray reference lifetimes; guest memory validation for direct and indirect BASER tables; migration correctness for sparse next-offset tables; and GICv4 state that cannot be saved on pre-v4.1 hardware. Cache invalidation is deliberately broad after retargeting/unmapping, and missing an invalidation could deliver an MSI to a stale LPI. Several command errors are architected positive ITS error codes rather than Linux errno, so callers must preserve that distinction.

## Test Signals
Useful signals are KVM VGIC ITS device attribute tests, MSI injection tests with valid and invalid DEVID/EVENTID pairs, guest ITS command sequences for MAPD/MAPC/MAPTI/MOVI/DISCARD/INV/INT, migration save/restore of sparse and indirect tables, LPI enable and pending-table synchronization tests, GICv4/v4.1 VLPI forwarding tests when hardware is available, and lockdep/KCSAN coverage for command processing and concurrent MSI injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-its.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-kvm-device.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-kvm-device.c

## Purpose
`vgic-kvm-device.c` is the KVM device API bridge for ARM VGIC models. It validates userspace configuration, exposes model-specific attribute groups, serializes migration register access, registers v2/v3/v5 device ops, and delegates actual register emulation to the MMIO and sysreg helpers.

## Important APIs, Types, And Functions
`vgic_check_iorange()` validates alignment, duplicate assignment, overflow, and IPA size limits. `kvm_set_legacy_vgic_v2_addr()` supports the legacy v2 address API. `kvm_vgic_addr()` handles distributor, CPU interface, redistributor, and redistributor-region address attributes. `vgic_set_common_attr()` and `vgic_get_common_attr()` implement shared address, IRQ-count, and control attributes. Model-specific accessors are `vgic_v2_attr_regs_access()`, `vgic_v3_attr_regs_access()`, and the limited v5 attribute handlers. The exported registrations are `kvm_arm_vgic_v2_ops`, `kvm_arm_vgic_v3_ops`, `kvm_arm_vgic_v5_ops`, and `kvm_register_vgic_device()`.

## Control Flow
Userspace creates a VGIC device, sets address and sizing attributes, then issues `KVM_DEV_ARM_VGIC_CTRL_INIT`. The common setter validates `KVM_DEV_ARM_VGIC_GRP_NR_IRQS` before VGIC initialization and delegates `CTRL_INIT` to `vgic_init()` under `config_lock`. Address writes take `slots_lock` first because v3 redistributor registration may touch the MMIO bus, then take `config_lock` around state mutation.

Register migration access parses CPU IDs or MPIDRs from `attr->attr`, stops all VCPUs using `kvm_trylock_all_vcpus()`, takes `config_lock`, verifies initialization rules, and delegates to `vgic_v2_dist_uaccess()`, `vgic_v2_cpuif_uaccess()`, `vgic_v3_dist_uaccess()`, `vgic_v3_redist_uaccess()`, or v3 CPU sysreg access. v3 allows a small pre-init read/write set for ID-like registers (`GICD_IIDR`, `GICD_TYPER2`) so userspace can discover and select features before final init.

## State And Persistence
The file mutates persistent VM configuration in `kvm->arch.vgic`: model, base addresses, redistributor regions, number of SPIs, maintenance interrupt PPI, implementation revision, and v5 userspace PPI exposure. Migration register access persists distributor, redistributor, CPU interface, level-info, and sysreg state through the common uaccess path. v2 register access may initialize the VGIC on demand, while v3 mostly requires prior initialization except for the pre-init ID registers.

## Dependencies And Integration Points
It depends on KVM device-core callbacks, user copy helpers, `kvm_get_vcpu_by_id()`, `kvm_mpidr_to_vcpu()`, all-vCPU locking, VGIC init/map helpers, MMIO uaccess functions from v2/v3 MMIO files, v3 CPU sysreg helpers, and v5 PPI state in `gicv5_vm`. It also registers the ITS device when the v3 VGIC device registration succeeds.

## Risks
The main risks are ABI regressions in error codes, lock ordering around `slots_lock` and `config_lock`, accepting address ranges that overlap or exceed IPA limits, permitting register writes after initialization when the ABI forbids it, and partial v5 support confusing userspace because most legacy address/sysreg attributes intentionally return `-ENXIO`. The save-pending-tables control path must hold KVM and all-vCPU locks because it writes guest memory and samples LPI state.

## Test Signals
Exercise KVM device `has_attr`, `set_attr`, and `get_attr` for every supported group; invalid alignment and out-of-range address tests; v3 redistributor region indexing and count validation; v2/v3 migration register round trips; pre-init v3 IIDR/TYPER2 access; maintenance IRQ PPI validation; v5 userspace PPI readback; and concurrent access tests that confirm running VCPUs cause `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-kvm-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v2.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v2.c

## Purpose
`vgic-mmio-v2.c` defines the memory-mapped GICv2 distributor and virtual CPU interface register model. It connects GICv2 architectural offsets to common VGIC state handlers, implements v2-only SGI and target-register behavior, and provides userspace migration access for v2 distributor/CPU registers.

## Important APIs, Types, And Functions
The descriptor tables `vgic_v2_dist_registers` and `vgic_v2_cpu_registers` are the central data structures. They map offsets such as `GIC_DIST_CTRL`, `GIC_DIST_IGROUP`, `GIC_DIST_ENABLE_SET`, `GIC_DIST_PENDING_SET`, `GIC_DIST_SOFTINT`, `GIC_CPU_CTRL`, `GIC_CPU_ACTIVEPRIO`, and `GIC_CPU_DEACTIVATE` to read/write callbacks. Exported entry points are `vgic_v2_init_dist_iodev()`, `vgic_v2_init_cpuif_iodev()`, `vgic_v2_has_attr_regs()`, `vgic_v2_cpuif_uaccess()`, and `vgic_v2_dist_uaccess()`.

## Control Flow
Guest MMIO is dispatched by the common `kvm_io_gic_ops` to descriptors initialized here. Distributor misc reads expose enable state, interrupt count, CPU count, and IIDR revision. Writes to `GIC_DIST_CTRL` toggle `dist->enabled` and kick VCPUs when enabling. SGI writes to `GIC_DIST_SOFTINT` decode target list/filter mode, mark target SGIs pending, set source bits, and queue the IRQ. Target-register writes update SPI `targets` and `target_vcpu`; private targets are read-only. SGI pending set/clear registers manipulate the per-source bitmap used by GICv2 SGI migration semantics.

CPU interface uaccess registers expose VMCR fields in the legacy v2 ABI shape. `GIC_CPU_DEACTIVATE` forwards to either `vgic_v2_deactivate()` or `vgic_v3_deactivate()` depending on host VGIC type, allowing GICv2 guests on GICv3 hardware.

## State And Persistence
This file persists distributor enable state, implementation revision, v2 group-writable compatibility, SGI source bitmaps, SPI target masks and target VCPUs, active priority registers, and VMCR fields. Userspace writes to `GIC_DIST_IIDR` validate the non-revision fields and use revision 2 or 3 as the compatibility opt-in that makes v2 interrupt groups writable by userspace.

## Dependencies And Integration Points
It relies heavily on common handlers in `vgic-mmio.c` for enable, pending, active, priority, group, and config state. Runtime deactivation integrates with `vgic-v2.c` and `vgic-v3.c`. MMIO registration is performed by `vgic-register_dist_iodev()` and v2 resource mapping code, while migration access is called from `vgic-kvm-device.c`.

## Risks
GICv2 SGI source state is architecturally awkward and lossy, especially across migration and active-state restore. IIDR revision compatibility must remain stable to avoid breaking migration from older kernels/userspace. Target register writes use online VCPU count masks, so tests must cover sparse VCPU IDs and late VCPU creation assumptions. CPU interface register semantics differ between real GICv2 hosts and GICv3 hosts emulating v2.

## Test Signals
Run v2 distributor and CPU interface KVM device register round trips, SGI injection tests for all target filter modes, IIDR revision migration tests, group writability compatibility tests, target register routing tests, `GIC_CPU_DEACTIVATE` behavior under EOImode, and invalid/unaligned `has_attr` queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v3.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v3.c

## Purpose
`vgic-mmio-v3.c` implements the GICv3 distributor and redistributor MMIO register model. It exposes ITS/LPI capability, GICv4.1 direct SGI controls, redistributor allocation, LPI property and pending base programming, invalidation registers, SGI dispatch helpers, and v3 migration uaccess paths.

## Important APIs, Types, And Functions
Generic utility exports include `extract_bytes()`, `update_64bit_reg()`, cacheability/shareability sanitizers, `vgic_has_its()`, `vgic_supports_direct_msis()`, `system_supports_direct_sgis()`, `vgic_supports_direct_sgis()`, and `vgic_lpis_enabled()`. Descriptor tables are `vgic_v3_dist_registers` and `vgic_v3_rd_registers`. Resource and ABI entry points include `vgic_v3_init_dist_iodev()`, `vgic_register_redist_iodev()`, `vgic_unregister_redist_iodev()`, `vgic_v3_set_redist_base()`, `vgic_v3_has_attr_regs()`, `vgic_v3_dist_uaccess()`, `vgic_v3_redist_uaccess()`, and `vgic_v3_line_level_info_uaccess()`.

## Control Flow
Distributor misc access reports CTLR, TYPER, TYPER2, and IIDR based on VM VGIC state. CTLR writes enable/disable the distributor and update `nassgireq`; changing direct SGI mode reconfigures vSGIs through v4 helpers and may request GICv4 reloads. Redistributor CTLR writes enable or disable LPIs with atomic state transitions, flushing pending LPIs and invalidating ITS caches on disable, or loading LPI state on enable.

PROPBASER and PENDBASER writes are 64-bit-update friendly and sanitized for supported cacheability/shareability and RES0 bits; writes are ignored while LPIs are enabled. INVLPIR and INVALLR set a redistributor busy counter, reload LPI configuration via ITS helpers, and clear the busy state. Redistributor registration picks a free slot from configured redistributor regions, initializes a per-VCPU iodev, and registers a 128 KiB MMIO window. SGI dispatch decodes ICC_SGI* affinity fields and queues target VCPU SGIs or broadcasts to all but the source.

## State And Persistence
Persistent state includes distributor enable, implementation revision, `nassgicap`, `nassgireq`, PROPBASER, each VCPU PENDBASER and redistributor CTLR, redistributor region list, per-VCPU redistributor base/index, SPI IROUTER target MPIDR, LPI pending/config tables, and line-level info for migration. Uaccess writes to TYPER2 can enable direct SGI capability before VGIC initialization if the host supports it.

## Dependencies And Integration Points
It integrates with `vgic-mmio.c` for common per-IRQ state, `vgic-its.c` for LPI invalidation and ITS cache invalidation, `vgic-v4.c` for direct SGI/MSI support, KVM MMIO bus registration, KVM MPIDR/VCPU lookup, guest memory helpers, and system register SGI traps.

## Risks
Redistributor region management is sensitive to overlap, ordering, count, and legacy single-region behavior. Atomic CTLR transitions must prevent simultaneous enable/disable races. LPI base registers are guest-memory pointers, so validation and migration ordering matter. Direct SGI capability is split between host capability, userspace opt-in, and guest request bits. Offsets for shared distributor registers deliberately RAZ/WI private IRQ ranges; descriptor ordering must remain bsearch-compatible.

## Test Signals
Cover v3 distributor and redistributor register uaccess, redistributor-region address APIs with overlap/count/index errors, LPI enable/disable and PROPBASER/PENDBASER sanitization, INVLPIR/INVALLR behavior, TYPER/TYPER2/IIDR migration writes, SGI system-register dispatch routing, direct SGI opt-in paths, and line-level info read/write round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.c

## Purpose
`vgic-mmio.c` is the shared MMIO engine for VGIC register emulation. It implements generic per-interrupt state accessors, region lookup and validation, endian conversion, guest MMIO dispatch, userspace migration access, VMCR model dispatch, and distributor iodev registration.

## Important APIs, Types, And Functions
Common register callbacks include `vgic_mmio_read_group()`, `vgic_mmio_write_group()`, `vgic_mmio_read_enable()`, `vgic_mmio_write_senable()`, `vgic_mmio_write_cenable()`, pending and active read/write pairs, priority/config handlers, line-level info helpers, and RAZ/RAO/WI helpers. Infrastructure functions include `vgic_find_mmio_region()`, `vgic_get_mmio_region()`, `vgic_uaccess()`, `vgic_data_mmio_bus_to_host()`, `vgic_data_host_to_mmio_bus()`, `vgic_set_vmcr()`, `vgic_get_vmcr()`, `kvm_io_gic_ops`, and `vgic_register_dist_iodev()`.

## Control Flow
Guest MMIO accesses enter `dispatch_mmio_read()` or `dispatch_mmio_write()`. The code converts little-endian MMIO bytes to host values, finds a descriptor with `vgic_get_mmio_region()`, validates access size/alignment and IRQ range, then calls the descriptor callback for distributor, CPU interface, redistributor, or ITS iodev type. Userspace migration access goes through `vgic_uaccess()`, forces 32-bit access, chooses redist VCPU if needed, and prefers uaccess-specific callbacks when present.

Per-IRQ operations compute the first INTID from the register offset and bits-per-IRQ, iterate over affected IRQs, take `irq_lock` when mutating state, and queue or unqueue interrupts through VGIC core helpers. Active-state guest MMIO may halt/resume the guest around shared or cross-VCPU active changes to avoid racing list-register state.

## State And Persistence
This file mutates persistent `struct vgic_irq` fields: `group`, `enabled`, `pending_latch`, `line_level`, `active`, `active_source`, `priority`, and `config`. It also touches physical IRQ state for mapped interrupts and hardware SGIs, including pending/active bits and host IRQ enable state. Migration paths intentionally differ from guest MMIO in places, for example v3 userspace pending reads use `pending_latch` while guest reads may sample physical line level.

## Dependencies And Integration Points
It depends on descriptor tables from v2/v3/ITS files, VGIC core IRQ lookup/reference helpers, KVM IO bus APIs, KVM guest halt/resume, arch timer assumptions for PPI configuration, physical IRQ helpers, GICv4 SGI property update, and model-specific VMCR implementations in v2/v3/v5 runtime files.

## Risks
The most important risks are lost pending/active transitions when interacting with hardware-backed IRQs, failure to halt running VCPUs before active-state migration changes, mismatches between guest MMIO and userspace ABI semantics, and region descriptor mistakes that allow unsupported widths or out-of-range INTIDs. Priority writes explicitly do not reschedule already queued interrupts, which is an intentional behavioral limitation.

## Test Signals
Run per-register MMIO width/alignment tests, migration uaccess tests for pending/active/line-level differences, mapped level IRQ resampling tests, hardware SGI enable/disable/group/priority updates, active-state writes while VCPUs are running, endian conversion tests on non-8-byte widths, and descriptor table ordering tests through `has_attr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.h

## Purpose
`vgic-mmio.h` declares the common VGIC MMIO descriptor format, descriptor construction macros, access-size flags, address-to-INTID helpers, and shared MMIO/uaccess function prototypes used by the v2, v3, and ITS MMIO implementations.

## Important APIs, Types, And Functions
`struct vgic_register_region` describes one contiguous register region: offset, length, bits per IRQ, access flags, guest read/write callbacks, ITS-specific read/write callbacks, and optional userspace uaccess callbacks. `VGIC_ACCESS_8bit`, `VGIC_ACCESS_32bit`, and `VGIC_ACCESS_64bit` encode legal access sizes. `VGIC_ADDR_IRQ_MASK()` and `VGIC_ADDR_TO_INTID()` convert register offsets to interrupt IDs for per-IRQ registers. `REGISTER_DESC_WITH_BITS_PER_IRQ()`, `REGISTER_DESC_WITH_LENGTH()`, and `REGISTER_DESC_WITH_LENGTH_UACCESS()` build descriptor table entries.

The header exposes common helpers implemented in `vgic-mmio.c`, v3 utilities from `vgic-mmio-v3.c`, and table initializers for v2/v3 iodevs. It also declares `kvm_io_gic_ops`, the IO bus operations used by distributor, redistributor, CPU interface, and ITS devices.

## Control Flow
The header does not execute logic, but it defines the contract used by bsearch-based region lookup and dispatch. Descriptor arrays must be sorted by `reg_offset`, must describe either fixed-length registers or per-IRQ regions, and must set callbacks matching the iodev type. For per-IRQ descriptors, `bits_per_irq` determines both region length and address-to-INTID conversion.

## State And Persistence
No state is stored here. The header defines access contracts that protect persistent VGIC state in implementation files. The presence of separate guest MMIO and uaccess callbacks is a persistence-relevant ABI detail because migration may need different behavior than live guest register access.

## Dependencies And Integration Points
All listed VGIC MMIO files include this header. It integrates with KVM core types (`struct kvm_vcpu`, `struct kvm`, `struct vgic_its`, `struct vgic_io_device`), GIC register definitions from included C files, and VGIC runtime model helpers through prototypes.

## Risks
Descriptor macro misuse can silently expose the wrong register length or access width. `VGIC_ADDR_TO_INTID()` assumes power-of-two bits per IRQ, so adding unusual encodings would require a different helper. The unioned callback fields require the dispatcher to call the correct member for ITS versus non-ITS iodevs.

## Test Signals
Compile coverage is the primary signal. Runtime signals come from every `has_attr` and MMIO dispatch test that validates descriptor lookup, allowed widths, and per-IRQ INTID conversion for v2/v3 distributor and redistributor tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v2.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v2.c

## Purpose
`vgic-v2.c` implements the runtime interaction between KVM VGIC state and a GICv2-compatible hardware virtual CPU interface. It computes and folds list-register state, manages VMCR/APR save/restore, handles DIR deactivation, maps v2 resources, and probes/registers VGICv2 support.

## Important APIs, Types, And Functions
Runtime entry points include `vgic_v2_init_lrs()`, `vgic_v2_configure_hcr()`, `vgic_v2_fold_lr_state()`, `vgic_v2_deactivate()`, `vgic_v2_populate_lr()`, `vgic_v2_clear_lr()`, `vgic_v2_set_vmcr()`, `vgic_v2_get_vmcr()`, `vgic_v2_reset()`, `vgic_v2_map_resources()`, `vgic_v2_probe()`, `vgic_v2_save_state()`, `vgic_v2_restore_state()`, `vgic_v2_load()`, and `vgic_v2_put()`. `vgic_v2_compute_lr()` is the core private encoder for GICH_LR values.

## Control Flow
Before guest entry, VGIC core selects pending/active IRQs and calls `vgic_v2_populate_lr()` under the IRQ lock. The function encodes virtual INTID, group, active/pending bits, source CPU for SGIs, EOI/resampling hints, HW physical ID if applicable, and five-bit priority. It clears edge pending state once consumed and lowers mapped-level line state to detect later edges. On guest exit, `vgic_v2_save_state()` reads VMCR/HCR/LRs from GICH registers, then `vgic_v2_fold_lr_state()` folds each LR back into `struct vgic_irq`, preserving active state, pending edge state, SGI source bits, and resampling effects.

`vgic_v2_configure_hcr()` enables the virtual interface and requests maintenance interrupts for pending/active work outside LRs. `vgic_v2_deactivate()` handles guest DIR writes in EOImode 1; it either synthesizes a deactivated LR and folds it or falls back to common active-clear MMIO when the IRQ is still resident in an LR.

## State And Persistence
Per-VCPU persistent state includes `vgic_hcr`, `vgic_vmcr`, `vgic_lr[]`, `used_lrs`, and `vgic_apr`. Per-IRQ state folded through this file includes active, pending latch, active source, SGI source bitmap, line level, on-LR marker, and physical resampling state. `vgic_v2_reset()` zeros VMCR so hardware reset behavior supplies default binary points.

## Dependencies And Integration Points
It depends on GICH/GICV MMIO mappings in `kvm_vgic_global_state`, VGIC core ap_list scheduling, common MMIO active-clear fallback, physical IRQ resampling helpers, KVM MMU remapping for GICV, and KVM device registration through `kvm_register_vgic_device()`. GICv3 hosts can still emulate v2, so some v2 MMIO paths may delegate deactivation to v3 runtime code.

## Risks
LR folding must not lose edge pending state, SGI source identity, or hardware resampling transitions. GICv2 SGI active-source state is partially unobservable and can be lossy across migration. Resource mapping must reject overlapping distributor/CPU frames and handle unsafe GICV alignment by trapping. EOICOUNT replay depends on ap_list priority ordering and active interrupt accounting.

## Test Signals
Exercise v2 guest IRQ injection for edge/level/SGI/SPI/HW-mapped cases, LR fold/populate round trips, EOImode 0 and 1 deactivation, maintenance interrupt generation with IRQs outside LRs, save/restore of VMCR/APR/LRs, GICV trap fallback on unsafe firmware resources, and migration tests around SGI active-source behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3-nested.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3-nested.c

## Purpose
`vgic-v3-nested.c` implements nested virtualization support for the GICv3 virtual CPU interface. It lets an L1 hypervisor program virtual ICH_* state for an L2 guest, shadows that state into host hardware LRs when running L2, syncs results back to the VNCR-backed L1 state, and synthesizes maintenance interrupt status.

## Important APIs, Types, And Functions
`struct mi_state` holds computed EISR/ELRSR/pending status. `struct shadow_if` is per-CPU shadow VGIC state with a compact LR map. Public entry points are `vgic_state_is_nested()`, `vgic_v3_get_eisr()`, `vgic_v3_get_elrsr()`, `vgic_v3_get_misr()`, `vgic_v3_flush_nested()`, `vgic_v3_sync_nested()`, `vgic_v3_load_nested()`, `vgic_v3_put_nested()`, `vgic_v3_handle_nested_maint_irq()`, and `vgic_v3_nested_update_mi()`.

## Control Flow
`vgic_state_is_nested()` enables the nested path when the VCPU is in nested context and L1 has set virtual IRQ/FIQ routing with matching IMO/FMO bits. On L2 load, `vgic_v3_create_shadow_state()` copies L1-visible HCR, VMCR, APRs, SRE, and valid LRs from vCPU sysreg storage into the per-CPU shadow. `vgic_v3_create_shadow_lr()` skips invalid LRs, translates guest pINTIDs for HW-backed LRs to host hardware interrupt IDs, compacts them into the real LR array, and records the source-index map. The shadow is restored to hardware and traps are activated.

On L2 put/sync, host LR state is read back using the LR map. State bits are merged into the original L1-visible LR, HW deactivation side effects are emulated through `vgic_v3_deactivate()`, VMCR and EOIcount are copied back, hardware HCR is disabled, and L1 maintenance interrupt level is recomputed. Trapped status registers (`EISR`, `ELRSR`, `MISR`) are synthesized from in-memory L1 LR/HCR/VMCR state rather than stored directly.

## State And Persistence
Persistent nested state lives in the VCPU sysreg array for ICH_LR*, ICH_AP*, ICH_HCR_EL2, and ICH_VMCR_EL2. The per-CPU `shadow_if` is transient and only valid during L2 execution on that CPU. Maintenance interrupt state is not stored as a hardware register snapshot; it is recomputed and injected as the VM's configured maintenance PPI.

## Dependencies And Integration Points
It depends on nested context helpers, VNCR/sysreg storage, low-level GICv3 LR accessors, VGIC IRQ lookup for HW LR translation, `vgic_v3_deactivate()` from the main v3 runtime, trap activation helpers, and KVM virtual IRQ injection. It is called by `vgic_v3_load()` and `vgic_v3_put()` when nested state is active.

## Risks
The compact LR map must preserve correspondence between L1 LR indexes and hardware LR indexes. HW-bit translation must avoid letting L1 name arbitrary host physical interrupts. Maintenance interrupt emulation is approximate because many ICH registers are memory-backed and L0 only observes status at load/put or trapped register reads. The code warns that separate virtual IRQ/FIQ routing is unsupported.

## Test Signals
Use nested KVM tests that run an L2 guest with L1-programmed virtual interrupts, HW-backed timer LR translation, EISR/ELRSR/MISR reads, L2 exit with pending maintenance interrupt, EOICOUNT propagation, and invalid HW-bit pINTID cases. Lockless per-CPU shadow assumptions should be tested under VCPU migration and preemption-disabled entry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3-nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3.c

## Purpose
`vgic-v3.c` is the main runtime backend for GICv3-compatible VGIC CPU interface state. It configures ICH_HCR traps, encodes/folds list registers, handles deactivation, manages VMCR/APR state, saves LPI pending tables, validates v3 MMIO resources, probes host GICv3 capability, and loads/puts v3 or nested state around VCPU execution.

## Important APIs, Types, And Functions
Core runtime functions include `vgic_v3_configure_hcr()`, `vgic_v3_fold_lr_state()`, `vgic_v3_deactivate()`, `vgic_v3_populate_lr()`, `vgic_v3_clear_lr()`, `vgic_v3_set_vmcr()`, `vgic_v3_get_vmcr()`, `vgic_v3_reset()`, `vcpu_set_ich_hcr()`, `vgic_v3_lpi_sync_pending_status()`, `vgic_v3_save_pending_tables()`, `vgic_v3_check_base()`, `vgic_v3_map_resources()`, `vgic_v3_enable_cpuif_traps()`, `vgic_v3_probe()`, `vgic_v3_load()`, and `vgic_v3_put()`. `vgic_v3_compute_lr()` is the private LR encoder.

## Control Flow
Before entry, VGIC core populates LRs with INTID, group, active/pending state, HW physical ID, EOI hints, and full priority. `vgic_v3_configure_hcr()` enables the interface and sets maintenance interrupt controls for IRQs outside LRs, empty SGI tracking, group enable/disable transitions, and DIR trapping when needed. On exit, `vgic_v3_fold_lr_state()` folds used LRs into `vgic_irq` state and replays EOICOUNT deactivations for active interrupts outside LRs. `vgic_v3_deactivate()` handles DIR writes in EOImode 1 and falls back to active-clear MMIO if the target IRQ is still on an LR.

Probe reads ICH_VTR via hyp, derives LR count and feature bits, optionally registers v2 compatibility, registers v3 device ops, handles GICv4 enablement, applies workarounds for broken SEIS, computes CPU interface trap bits, and records global VGIC type and limits. Load/put either delegate to nested VGIC logic or save/restore VMCR/APRs through hyp and coordinate GICv4 vPE residency.

## State And Persistence
Per-VCPU state includes `vgic_hcr`, `vgic_vmcr`, `vgic_sre`, `vgic_lr[]`, APR arrays, `used_lrs`, ID and priority bit counts, and PENDBASER defaults. VM persistent state includes active SPI count, redistributor regions, distributor base, GICv4 capability, and pending LPI tables in guest memory. `vgic_v3_save_pending_tables()` writes LPI pending bits back to guest RAM and temporarily unmaps/remaps vPEs on GICv4.1 to sample VLPI state.

## Dependencies And Integration Points
The file integrates with hyp save/restore routines, common VGIC ap_list scheduling, `vgic-mmio-v3.c` redistributor resource state, `vgic-its.c` LPI structures, GICv4 vPE load/put, nested VGIC support, KVM MMU and firmware GIC info, static keys for trap modes, and CPU erratum/workaround detection.

## Risks
LR fold/populate correctness is central to interrupt delivery and migration. EOICOUNT replay relies on ap_list ordering. DIR trapping is required on hardware without TDIR or with active SPIs outside LRs; missing it can leave stale active state. Pending-table save must coordinate with GICv4.1 residency. Probe paths must preserve v2 compatibility and pKVM restrictions without exposing unsupported devices.

## Test Signals
Exercise v3 IRQ injection/folding for edge, level, SGI, SPI, LPI, and HW-mapped interrupts; EOImode 0/1 deactivation; pending LPI table save/restore; redistributor overlap checks; probe on hosts with and without v2 compatibility/GICv4; trap-bit early params; nested load/put delegation; and migration of VMCR/APR/LR state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v4.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v4.c

## Purpose
`vgic-v4.c` bridges KVM's virtual ITS/VGIC state with GICv4/GICv4.1 hardware direct injection. It manages vPE allocation and residency, doorbell IRQs, direct virtual SGI configuration, VLPI forwarding from VFIO/MSI routing, and cleanup of hardware-backed LPIs.

## Important APIs, Types, And Functions
Entry points include `vgic_v4_configure_vsgis()`, `vgic_v4_get_vlpi_state()`, `vgic_v4_request_vpe_irq()`, `vgic_v4_init()`, `vgic_v4_teardown()`, `vgic_v4_put()`, `vgic_v4_load()`, `vgic_v4_commit()`, `kvm_vgic_v4_set_forwarding()`, and `kvm_vgic_v4_unset_forwarding()`. Internal helpers manage doorbells (`vgic_v4_doorbell_handler()`), vSGI enable/disable, vPE doorbell policy, and lookup of an LPI by host IRQ.

## Control Flow
Initialization allocates VM vPE pointers, asks the ITS driver for vCPU IRQs, configures doorbell IRQ flags, and requests per-VCPU doorbell interrupts. On VCPU load, direct-IRQ support makes the vPE resident after setting doorbell IRQ affinity to the current CPU. On put, the vPE is made non-resident and a doorbell is requested if the VCPU is in WFI or nested execution needs to be interrupted.

When userspace/VFIO configures MSI forwarding, `kvm_vgic_v4_set_forwarding()` resolves the routing entry to a vITS, translates DEVID/EVENTID to a `vgic_irq`, builds an `its_vlpi_map`, and calls `its_map_vlpi()`. If successful, the LPI becomes hardware-backed (`irq->hw`, `host_irq`) and pending software state is transferred to the host irqchip. Unset reverses this by finding the LPI by host IRQ, decrementing the target vPE VLPI count, clearing `hw`, and unmapping the VLPI.

## State And Persistence
The file mutates `dist->its_vm.vpes`, per-VCPU `its_vpe` residency/ready/pending/vlpi_count state, SGI config in the vPE, `vgic_irq->hw`, `host_irq`, and pending latch transfer between software and hardware. It does not own migration table format, but it affects whether ITS save can observe pending state; pre-v4.1 hardware-backed LPIs can cause save to fail elsewhere.

## Dependencies And Integration Points
It depends on the irqchip ITS GICv4 API (`its_alloc_vcpu_irqs`, `its_make_vpe_resident`, `its_map_vlpi`, `its_unmap_vlpi`, etc.), VFIO/KVM MSI routing callbacks, virtual ITS resolution from `vgic-its.c`, common VGIC IRQ state, GICv3 vPE storage, and KVM VCPU wakeup/request mechanisms.

## Risks
Direct injection state spans KVM and the host irqchip, so refcount and lock mistakes can leak or misroute host IRQs. Doorbell races are explicitly handled with `vpe_lock` on v4.1. Forwarding silently falls back to software injection for many invalid states, which is correct but can hide performance regressions. vSGI conversion must transfer pending, priority, group, and enable state without losing software pending bits.

## Test Signals
Use hardware-enabled tests for VLPI forwarding/unforwarding, pending transfer on mapping, doorbell wake from WFI, vPE migration between physical CPUs, GICv4.1 vSGI enable/disable through GICD_CTLR nASSGIreq, teardown after partial init failure, and migration/save behavior with hardware-backed LPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v5.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v5.c

## Purpose
`vgic-v5.c` implements early KVM support for GICv5/GCIE guests and the GICv5 PPI handling model. It probes and registers v5 and legacy v3-compatible devices, tracks implemented PPIs, initializes exposed userspace PPIs, handles mostly hardware-managed PPI state, and saves/restores GICv5 CPU interface state around VCPU execution.

## Important APIs, Types, And Functions
Probe and setup functions are `vgic_v5_probe()`, `vgic_v5_reset()`, `vgic_v5_init()`, `vgic_v5_map_resources()`, and `vgic_v5_finalize_ppi_state()`. PPI helpers include `vgic_v5_ppi_queue_irq_unlock()`, `vgic_v5_set_ppi_dvi()`, `vgic_v5_set_ppi_ops()`, `vgic_v5_has_pending_ppi()`, `vgic_v5_fold_ppi_state()`, and `vgic_v5_flush_ppi_state()`. CPU interface state functions are `vgic_v5_load()`, `vgic_v5_put()`, `vgic_v5_get_vmcr()`, `vgic_v5_set_vmcr()`, `vgic_v5_restore_state()`, and `vgic_v5_save_state()`.

## Control Flow
Probe marks the global type as VGIC_V5, disables v2/GICv4 assumptions, skips v5 registration under protected KVM, discovers implemented architectural PPIs, and registers the v5 KVM device. If legacy GICv3 compatibility is available, it also registers a v3 device, fills ICH_VTR state, enables the global GICv3 CPU interface static branch, and applies v3 trap configuration.

VM init rejects nested GICv5 VMs, then exposes only implemented userspace-drivable PPIs, currently centered on SW_PPI. Finalization inspects VCPU0's implemented PPIs and exposes only PPIs with an owner or the SW_PPI, while recording hardware mode level/edge information. PPI queueing does not put interrupts on the VGIC ap_list; it unlocks and kicks the target VCPU because the hardware CPU interface handles most PPI delivery. Entry flush builds pending PPI shadow state, and exit fold merges hardware exit pending/active state back into `vgic_irq`.

## State And Persistence
Persistent VM state includes implemented PPI capability masks, userspace PPI mask, exposed VGIC PPI mask, PPI hardware mode register, and per-VCPU GICv5 CPU interface fields: VMCR, APR, PPI priority registers, active/pending/direct-virtual-injection bitmaps, and residency flag. Edge pending state is ORed on fold to avoid losing incoming edges, while flush clears edge pending after transferring it to the shadow pending registers.

## Dependencies And Integration Points
It depends on ARM64 GICv5 CPU interface capabilities, GICv5 hyp save/restore helpers, generic VGIC IRQ objects and ops override, PMU feature detection for PMUIRQ exposure, `vgic-v3.c` for legacy compatibility registration/traps, and the KVM device layer for the limited v5 userspace ABI.

## Risks
The implementation is intentionally narrower than v2/v3: no nested GICv5 support and no pKVM v5 guests. PPI exposure depends on owner state sampled from VCPU0, so heterogeneous or late owner changes would be risky. Residency guards avoid double save/restore on WFI paths; mistakes could lose VMCR/APR state. Priority synchronization only happens on WFI entry, so tests should verify priority changes around sleep paths.

## Test Signals
Cover probe on v5-only, v5 plus legacy v3, and pKVM configurations; userspace PPI mask readback; nested VM rejection; PPI finalization with owned and unowned PPIs; pending/active fold and flush for edge and level PPIs; WFI double load/put paths; VMCR get/set; and legacy v3 device behavior on GICv5 hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v5.c -->
