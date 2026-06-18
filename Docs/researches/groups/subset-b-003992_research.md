# subset-b-003992 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.c

## Purpose

`arm-smmu-v3.c` is the main Linux IOMMU driver for architected Arm SMMUv3 devices. It probes the platform SMMU instance, discovers hardware and firmware-advertised capabilities, allocates command/event/PRI queues and stream tables, registers `iommu_ops`, manages device stream IDs, builds context descriptors and stream table entries, attaches domains, and issues SMMU command queue operations for configuration and TLB/ATC invalidation. In this tree it also contains the newer invalidation-array machinery used to keep per-domain invalidation state coherent across shared domains, PASID attachments, ATS devices, nested domains, and virtual SMMU support.

## Important APIs, Types, and Functions

The file implements the `arm_smmu_ops` object consumed by the IOMMU core. Its default domain operations include `arm_smmu_attach_dev`, `arm_smmu_s1_set_dev_pasid`, `arm_smmu_map_pages`, `arm_smmu_unmap_pages`, `arm_smmu_flush_iotlb_all`, `arm_smmu_iotlb_sync`, `arm_smmu_iova_to_phys`, and `arm_smmu_domain_free_paging`. It also exposes identity and blocked domains with custom attach paths.

Queue support is centered on `arm_smmu_queue`, `arm_smmu_cmdq`, and helpers such as `queue_has_space`, `queue_sync_prod_in`, `queue_remove_raw`, `arm_smmu_cmdq_build_cmd`, `arm_smmu_cmdq_issue_cmdlist`, `arm_smmu_cmdq_batch_add`, and `arm_smmu_cmdq_batch_submit`. `arm_smmu_get_cmdq` lets implementation hooks route selected commands to a secondary command queue, as used by Tegra241 CMDQV.

Entry programming is handled by `arm_smmu_get_ste_used`, `arm_smmu_get_ste_update_safe`, `arm_smmu_get_cd_used`, `arm_smmu_write_entry`, `arm_smmu_write_cd_entry`, `arm_smmu_write_ste`, and the builder helpers `arm_smmu_make_abort_ste`, `arm_smmu_make_bypass_ste`, `arm_smmu_make_cdtable_ste`, `arm_smmu_make_s1_cd`, and `arm_smmu_make_s2_domain_ste`. Several of these are exported to KUnit with `EXPORT_SYMBOL_IF_KUNIT`.

Invalidation state uses `arm_smmu_inv`, `arm_smmu_invs`, `arm_smmu_invs_merge`, `arm_smmu_invs_unref`, `arm_smmu_invs_purge`, `arm_smmu_master_build_invs`, `arm_smmu_attach_prepare_invs`, `arm_smmu_install_new_domain_invs`, and `arm_smmu_install_old_domain_invs`. Runtime invalidation flows through `arm_smmu_domain_inv_range`, `__arm_smmu_domain_inv_range`, `arm_smmu_inv_to_cmdq_batch`, `arm_smmu_cmdq_batch_add_range`, and ATS helpers such as `arm_smmu_atc_inv_to_cmd` and `arm_smmu_atc_inv_master`.

Probe and reset are driven by `arm_smmu_device_probe`, `arm_smmu_device_dt_probe`, `arm_smmu_device_acpi_probe`, `arm_smmu_impl_probe`, `arm_smmu_device_hw_probe`, `arm_smmu_init_structures`, `arm_smmu_init_queues`, `arm_smmu_init_strtab`, `arm_smmu_device_reset`, `arm_smmu_setup_irqs`, and `arm_smmu_device_remove`.

## Control Flow

Probe starts in the platform driver. Firmware parsing sets initial feature and option bits from DT or ACPI, including coherency, vendor options, and optional Tegra241 CMDQV companion detection. Implementation probing can replace the base `arm_smmu_device` allocation with a larger implementation-specific structure and install early implementation ops. The driver maps page 0 and page 1 MMIO regions, collects interrupts, reads ID registers, applies IIDR errata masks, initializes queues and stream tables, installs RMR bypass STEs, resets the hardware, registers sysfs and the IOMMU device, then hands device probing to the IOMMU core.

Device probing looks up the SMMU by firmware node, allocates an `arm_smmu_master`, sorts firmware stream IDs, initializes required two-level stream-table leaves, inserts each stream into the SMMU red-black tree, enables PCI PASID when available, records SSID/stall capability, and prepares ATS. Device release disables PASID, removes stream IDs, frees context descriptor tables, and releases the master.

Domain allocation chooses stage 1 or stage 2 from hardware features and requested flags. `arm_smmu_domain_finalise` allocates io-pgtable ops, sets aperture and page-size metadata, allocates an ASID through the global xarray for stage 1 or a VMID through the per-SMMU IDA for stage 2, and wires dirty tracking when supported by hardware access/dirty updates plus coherent walks.

Attach is deliberately multi-phase. `arm_smmu_attach_prepare` decides ATS state, prepares new and old invalidation arrays, optionally prepares nested vmaster state, adds the new `arm_smmu_master_domain` to the new domain list before hardware is changed, installs the new domain invalidation array, and disables PCI ATS early when the new STE cannot support ATS. The caller then writes CDs and/or STEs. `arm_smmu_attach_commit` performs final ATC synchronization, removes the old master-domain record, unrefs the old invalidation entries, and updates `master->ats_enabled`.

Command queue insertion uses a scalable producer-ownership algorithm. Producers reserve slots with a cmpxchg on the low-level queue, write commands, mark a validity bitmap after a DMA write barrier, and only the current owner publishes contiguous valid work to the hardware producer register. Synchronous commands take a shared lock so queue wrap and completion polling cannot race with producer advancement. Completion is detected by MSI writeback when enabled, or by polling the hardware consumer pointer.

Event IRQ flow drains EVTQ entries, decodes raw event fields into `arm_smmu_event`, reports stall faults through the IOPF path when possible, forwards stage-1 virtual master events to iommufd when configured, and rate-limits raw diagnostic dumps otherwise. PRI queue handling denies unexpected page requests. Global errors report MSI/queue aborts, handle service failure by disabling the SMMU, and call command-skip recovery for command queue errors.

## State and Persistence Behavior

Persistent driver state is kernel-resident. `arm_smmu_device` stores MMIO bases, queue state, IRQs, feature and option masks, address-size and page-size properties, ASID/VMID sizes, stream-table layout, stream-ID tree, and implementation hooks. `arm_smmu_master` stores a device's stream list, PASID/CD table state, current ATS state, stall and IOPF state, and a preallocated scratch invalidation array. `arm_smmu_domain` stores io-pgtable ops, ASID or VMID, stage, RCU invalidation array, attached-device list, dirty/enforced coherency state, and nested-parent state.

Hardware-visible persistence is in DMA-coherent queues, stream tables, context descriptor tables, and SMMU registers. The driver writes these structures with DMA barriers and then issues CFGI/TLBI/CMD_SYNC commands so the SMMU observes changes in the required order. There is no disk persistence; reset, remove, or reboot reconstructs all state from firmware descriptions and hardware registers. RMR bypass STEs are installed before the stream table is programmed to preserve firmware reserved-memory mappings.

ASIDs are globally serialized by `arm_smmu_asid_lock` and `arm_smmu_asid_xa`; VMIDs are per SMMU through `ida`. Invalidation arrays are RCU-protected and can contain trash entries until a purge pass allocates a compact replacement. ATS operations take the invalidation-array read lock only when ATS entries exist, avoiding locking on common non-ATS invalidation paths.

## Dependencies and Integration Points

The driver depends on the Linux IOMMU core, io-pgtable arm-lpae formats, DMA coherent allocation, PCI ATS/PASID/PRI support, ACPI IORT, device tree, MSI platform domains, iopf queues, irq threading, xarray/IDA/RCU/spinlock/mutex primitives, and Arm64 CPU feature checks for E2H. It includes `../../dma-iommu.h` for reserved DMA regions and `arm-smmu-v3.h` for the hardware ABI.

Implementation integration is via `struct arm_smmu_impl_ops`, especially `init_structures`, `device_reset`, `device_remove`, `get_secondary_cmdq`, `hw_info`, `get_viommu_size`, and `vsmmu_init`. Tegra241 CMDQV plugs in through this path. Optional SVA and iommufd support are linked through functions declared in the header; when those configs are absent, the header supplies NULL or no-op fallbacks.

Firmware integration is split between DT and ACPI. DT validates `#iommu-cells`, checks coherency, parses vendor option booleans, and discovers NVIDIA CMDQV phandles for Tegra264-compatible SMMUs. ACPI IORT provides coherency and HTTU overrides, implementation model options for Cavium/HiSilicon/generic, and optional DSDT CMDQV matching by `_UID`.

## Risks and Edge Cases

The command queue algorithm is highly concurrency-sensitive. Reordering around relaxed atomics, validity bits, DMA barriers, shared locks, or MSI completion writeback can lead to missed commands, stale queue entries, or producer/consumer corruption. Secondary command queues add another dimension because commands may need fallback to the main SMMU command queue if unsupported.

STE/CD updates are designed to be hitless when possible, but the safety depends on accurate `get_used` masks and safe-bit calculations. If a builder sets bits not marked used, the WARN catches it, but hardware can still see invalid intermediate states if sequencing assumptions are wrong.

Attach sequencing crosses several subsystems: domain lists, invalidation arrays, ATS enable/disable, PASID CDs, nested domains, and IOPF registration. Failure paths before hardware changes free prepared arrays and vmaster state, while success paths must always reach commit. Bugs here can leave a master included in the wrong domain invalidation array or leave ATC entries stale.

Firmware feature overrides can hide or force capabilities contrary to ID registers. The code warns on coherency and HTTU mismatches, and IIDR errata disable features such as SEV, BTM, and nesting for affected Arm MMU products. Regression risk is high when adding new hardware IDs or changing feature-gating logic.

Event handling assumes stream IDs can be resolved under `streams_mutex`; unsupported aliases are rejected except PCI RID aliases. IOPF is only enabled for single-stream stalled devices, and unhandled events are intentionally logged/pinned rather than resumed.

## Test Signals

KUnit-level signals already target entry-writing and invalidation helpers via exported symbols. Valuable tests include command encoding for every opcode, unsupported-command fallback, CMDQ timeout and error-skip recovery, hitless versus disruptive STE/CD updates, invalidation merge/unref/purge ordering and trash handling, range invalidation chunking, ATS full/ranged invalidation generation, attach prepare/commit reattach cases, PASID attach/detach with CD table downgrade, and dirty-tracking capability gating.

Integration tests should cover DT and ACPI probe paths, two-level and linear stream tables, two-level and linear context descriptor tables, RMR bypass STE installation, MSI fallback to wired IRQs, combined versus unique IRQ handling, kdump disabling of event/PRI queues, SVA/iommufd config-off stubs, Tegra241 secondary command queue fallback, PCI ATS/PASID enable ordering, IOPF stall reporting, and remove/shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.h

## Purpose

`arm-smmu-v3.h` is the private hardware ABI and shared driver-state header for the Arm SMMUv3 driver family. It defines MMIO register offsets, register bitfields, stream table and context descriptor layouts, command/event/PRI queue encodings, in-memory queue and domain structures, implementation hook contracts, feature and option masks, SVA/iommufd/Tegra extension entry points, and helper inlines used by the main driver and companion implementation files.

## Important APIs, Types, and Functions

The register macro blocks cover ID registers, CR0/CR1/CR2, GBPA, IRQ control, global errors, MSI config registers, stream table base/config registers, command/event/PRI queue base/prod/cons registers, common memory attributes, and queue index/wrap helpers. The header also defines natural queue sizing through `Q_MAX_SZ_SHIFT` and per-queue maximum shifts.

Hardware table types include `struct arm_smmu_ste`, `struct arm_smmu_strtab_l1`, `struct arm_smmu_strtab_l2`, `struct arm_smmu_cd`, `struct arm_smmu_cdtab_l1`, and `struct arm_smmu_cdtab_l2`. Helpers such as `arm_smmu_strtab_l1_idx`, `arm_smmu_strtab_l2_idx`, `arm_smmu_cdtab_l1_idx`, and `arm_smmu_cdtab_l2_idx` encode the split between L1 and L2 tables.

Command-related definitions include `struct arm_smmu_cmdq_ent`, command opcodes, TLBI range fields, ATC invalidation fields, PRI response fields, CMD_SYNC fields, `struct arm_smmu_ll_queue`, `struct arm_smmu_queue`, `struct arm_smmu_cmdq`, `struct arm_smmu_cmdq_batch`, and `arm_smmu_cmdq_supports_cmd`.

Driver state types include `struct arm_smmu_device`, `struct arm_smmu_master`, `struct arm_smmu_domain`, `struct arm_smmu_nested_domain`, `struct arm_smmu_master_domain`, `struct arm_smmu_invs`, `struct arm_smmu_inv`, `struct arm_smmu_inv_state`, `struct arm_smmu_attach_state`, `struct arm_smmu_event`, `struct arm_smmu_vmaster`, and `struct arm_vsmmu`. `struct arm_smmu_impl_ops` is the extension point for vendor-specific SMMUv3 implementations.

Extern and prototype declarations expose cross-file functions such as `arm_smmu_domain_alloc`, `arm_smmu_clear_cd`, `arm_smmu_get_cd_ptr`, `arm_smmu_make_s1_cd`, `arm_smmu_write_cd_entry`, `arm_smmu_set_pasid`, `arm_smmu_domain_inv_range`, `__arm_smmu_cmdq_skip_err`, `arm_smmu_init_one_queue`, `arm_smmu_cmdq_init`, `arm_smmu_attach_prepare`, `arm_smmu_attach_commit`, `arm_smmu_install_ste_for_dev`, and `arm_smmu_cmdq_issue_cmdlist`. KUnit-only declarations expose STE/CD and invalidation-array internals for direct tests.

## Control Flow

The header itself has no runtime control flow, but it shapes the driver flow. Probe code reads `IDR*` fields into `ARM_SMMU_FEAT_*` flags, configures queues using `Q_*` and queue-size macros, and programs hardware tables using the STRTAB and CTXDESC definitions. Command construction fills an `arm_smmu_cmdq_ent` union and the main driver encodes it into the CMDQ bitfields declared here.

Attach and invalidation sequencing are modeled in the structures declared here. `arm_smmu_attach_state` carries old domain, master, SSID, ATS policy, vmaster state, and two invalidation states across prepare and commit. `arm_smmu_invs` describes the RCU-protected per-domain invalidation array that fast-path invalidation readers consume. The enum ordering of `arm_smmu_inv_type` is intentionally used for command issue ordering, with TLBI before ATC invalidation.

Configuration conditionals define build-time flow. When `CONFIG_ARM_SMMU_V3_SVA` is disabled, SVA helpers become stubs or NULL function pointers. When `CONFIG_TEGRA241_CMDQV` is disabled, `tegra241_cmdqv_probe` returns `-ENODEV`. When `CONFIG_ARM_SMMU_V3_IOMMUFD` is disabled, iommufd hardware-info, viommu, nested-domain, and vmaster hooks are NULL or no-op fallbacks.

## State and Persistence Behavior

The types in this header define all important persistent in-kernel state for the SMMUv3 driver. `arm_smmu_device` persists for the platform device lifetime and owns MMIO mappings, feature masks, command/event/PRI queues, stream tables, ID allocators, IOMMU core handle, stream tree, and stream mutex. `arm_smmu_master` persists while an endpoint is attached to the IOMMU core and owns stream IDs, CD table storage, ATS/stall flags, PASID width, and IOPF refcount. `arm_smmu_domain` persists for a paging/SVA domain and owns io-pgtable ops, ASID/VMID state, domain geometry, invalidation arrays, and attached device list.

Hardware-visible state is represented with little-endian entry arrays (`__le64`) and DMA addresses. Stream table entries and context descriptors are fixed at eight dwords in the main driver, and the header layout must stay aligned with the architecture. Queue state combines software producer/consumer shadow fields, hardware MMIO registers, coherent queue memory, and DMA base register encodings.

The header also encodes reference/lifetime expectations. `arm_smmu_invs` is RCU-freed. `arm_smmu_domain_free` assumes no invalidation concurrency remains. `arm_smmu_master_canwbs` derives write-back-safe coherency from firmware spec flags at runtime rather than storing a duplicate property.

## Dependencies and Integration Points

The header depends on kernel bitfield, IOMMU, iommufd, kernel utility, memory-zone, and size definitions. It is consumed by the main SMMUv3 driver, Tegra241 CMDQV, SVA support, iommufd support, and KUnit tests. Its public surface bridges Linux IOMMU core concepts (`struct iommu_domain`, `iommufd_viommu`, user data arrays, `enum iommu_hw_info_type`, `enum iommu_viommu_type`) with architecture-specific SMMUv3 state.

`struct arm_smmu_impl_ops` is a key integration point for implementation extensions. A vendor implementation can add reset/remove hooks, allocate extra structures, route commands to a secondary command queue, expose vendor-specific hardware info, and initialize virtual SMMU state. The main driver checks that `get_viommu_size` and `vsmmu_init` are paired.

## Risks and Edge Cases

This header is tightly coupled to hardware layout. Wrong bit masks, endian conversions, table sizes, or queue sizing constants can corrupt hardware-visible descriptors. Queue index and wrap macros depend on `max_n_shift`; callers must preserve natural alignment and power-of-two sizes.

Feature and option flags are bit positions in a shared `u32`, so additions need care to avoid overlap. The enum ordering of `arm_smmu_inv_type` is semantically significant for invalidation command order. `struct arm_smmu_cmdq_ent` is a union; command builders must only read fields valid for the selected opcode.

Conditional stubs are intentionally NULL/no-op in some configurations. Callers must be prepared for unsupported SVA, iommufd, and CMDQV paths. The iommufd fallback definitions make compile-time integration simple, but runtime behavior depends on the main driver checking capabilities before advertising user-facing features.

## Test Signals

Build tests should cover all relevant config combinations: SVA on/off, iommufd on/off, Tegra241 CMDQV on/off, KUnit on/off, PCI PRI/ATS on/off, and CMA alignment variants. KUnit tests should validate descriptor used-bit masks, hitless entry update helpers, invalidation-array helpers, queue macro wrap behavior, table index helpers, and command support filtering. Static analysis should watch flexible-array bounds, `__counted_by(max_invs)`, endian conversions, and struct-size assumptions shared with vendor files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/tegra241-cmdqv.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/tegra241-cmdqv.c

## Purpose

`tegra241-cmdqv.c` implements NVIDIA Tegra241/Tegra264 CMDQ-V support for the Arm SMMUv3 driver. CMDQ-V provides multiple virtual command queues and virtual interfaces that can accelerate command submission for the kernel and expose guest-owned command queues through iommufd. The file plugs into `arm_smmu_impl_ops`, allocates and maps CMDQV resources, routes supported SMMU commands to secondary queues, handles CMDQV errors, and implements iommufd viommu/hw_queue/vdevice operations for user-owned virtual interfaces.

## Important APIs, Types, and Functions

Core types are `struct tegra241_cmdqv`, `struct tegra241_vintf`, `struct tegra241_vcmdq`, and `struct tegra241_vintf_sid`. `tegra241_cmdqv` embeds `struct arm_smmu_device` as its first member so `devm_krealloc` can replace the generic SMMU object. `tegra241_vintf` embeds `struct arm_vsmmu` for iommufd virtual SMMU integration. `tegra241_vcmdq` embeds `struct iommufd_hw_queue` and contains an `arm_smmu_cmdq`.

Hardware config helpers include `tegra241_cmdqv_write_config`, `cmdqv_write_config`, `vintf_write_config`, `vcmdq_write_config`, and `lvcmdq_error_header`. Interrupt and error handling is in `tegra241_cmdqv_isr`, `tegra241_vintf0_handle_error`, and `tegra241_vintf_user_handle_error`. Queue selection is in `tegra241_cmdqv_get_cmdq`, with guest queue command filtering in `tegra241_guest_vcmdq_supports_cmd`.

Reset and hardware lifecycle are handled by `tegra241_cmdqv_hw_reset`, `tegra241_vintf_hw_init`, `tegra241_vintf_hw_deinit`, `tegra241_vcmdq_hw_init`, `tegra241_vcmdq_hw_deinit`, `tegra241_vcmdq_hw_flush_timeout`, `tegra241_vcmdq_map_lvcmdq`, and `tegra241_vcmdq_unmap_lvcmdq`. Allocation helpers include `tegra241_vcmdq_alloc_smmu_cmdq`, `tegra241_vintf_alloc_lvcmdq`, `tegra241_cmdqv_init_vintf`, `tegra241_cmdqv_init_structures`, and removal helpers.

Implementation registration uses `tegra241_cmdqv_probe`, `__tegra241_cmdqv_probe`, `tegra241_cmdqv_impl_ops`, `tegra241_cmdqv_hw_info`, `tegra241_cmdqv_get_vintf_size`, and `tegra241_cmdqv_init_vintf_user`. iommufd-facing operations include `tegra241_vintf_get_vcmdq_size`, `tegra241_vintf_alloc_lvcmdq_user`, `tegra241_vintf_destroy_lvcmdq_user`, `tegra241_vintf_init_vsid`, `tegra241_vintf_destroy_vsid`, `tegra241_cmdqv_destroy_vintf_user`, and `tegra241_cmdqv_viommu_ops`.

## Control Flow

The main SMMUv3 probe discovers a CMDQV companion device and calls `tegra241_cmdqv_probe`. This file maps the CMDQV resource, honors the `disable_cmdqv` module parameter by disabling hardware and falling back, optionally requests the CMDQV interrupt, reads parameter registers to calculate the number of VINTFs, global VCMDQs, LVCMDQs per VINTF, and SID slots per VINTF, allocates the VINTF pointer table and IDA, and installs early implementation ops.

During main SMMU structure initialization, `tegra241_cmdqv_init_structures` allocates VINTF0 for in-kernel use, preallocates every logical VCMDQ under VINTF0, allocates a normal `arm_smmu_cmdq` for each LVCMDQ, and then installs the final implementation ops. During SMMU reset, `tegra241_cmdqv_hw_reset` disables and re-enables CMDQV, programs global VCMDQ allocation registers to assign queues to VINTFs/LVCMDQs, and initializes VINTF0 as hypervisor-owned.

Command routing happens from the main driver's `arm_smmu_get_cmdq`. If `bypass_vcmdq` is false, VINTF0 is enabled, and the selected per-CPU LVCMDQ exists and supports the command, `tegra241_cmdqv_get_cmdq` returns that secondary command queue. Otherwise the main SMMU command queue is used. LVCMDQ choice is currently `raw_smp_processor_id() % num_lvcmdqs_per_vintf`.

Error IRQ flow reads the VINTF error map and global VCMDQ error maps. VINTF0 errors are handled in-kernel by iterating LVCMDQ error bits, using the common SMMUv3 command error skipper, and acknowledging VCMDQ `GERRORN`. User VINTF errors are packaged into `iommu_vevent_tegra241_cmdqv` and reported through the iommufd viommu event queue.

User VINTF creation initializes a non-hypervisor-owned VINTF, allocates an mmap region for its VINTF page0, copies offsets back to userspace, initializes SID and LVCMDQ locks/IDAs, and installs `tegra241_cmdqv_viommu_ops`. User LVCMDQ allocation validates queue type, local index, strict ascending allocation dependency, power-of-two length, maximum IDR1 command queue size, physical address mask and alignment, maps the global VCMDQ, programs the queue base, and registers a destroy callback. User vdevice initialization allocates a SID mapping slot and writes SID_REPLACE/SID_MATCH for a physical SID to virtual SID mapping.

## State and Persistence Behavior

CMDQV state is volatile kernel and MMIO state. `tegra241_cmdqv` stores hardware parameters, the CMDQV MMIO base and physical base, IRQ, VINTF ID allocator, and VINTF pointer array. VINTF state tracks index, enable state, hypervisor ownership read back from hardware, local command queues, userspace mutex, mmap offset, and SID mapping allocator. VCMDQ state tracks global/local queue indexes, enabled state, queue dependency, parent pointers, embedded SMMU command queue, and two MMIO pages.

Hardware state persists until reset/remove: CMDQV enable state, global VCMDQ allocation registers, VINTF enable/config including VMID and ownership, SID replacement/match registers, VCMDQ queue base and enable state, and error status registers. Removal deinitializes VINTFs, LVCMDQs, global allocations, IRQ, MMIO mapping, and the companion device reference.

User-owned resources are lifetime-managed through iommufd destroy callbacks. The driver relies on iommufd dependency tracking to enforce descending destruction order for LVCMDQs after requiring ascending allocation order.

## Dependencies and Integration Points

The file depends on the SMMUv3 core header, iommufd viommu/hw_queue/vdevice APIs, uapi iommufd Tegra241 structures, DMA mapping, debugfs, platform resources, interrupts, and polling helpers. It imports the `IOMMUFD` namespace. It integrates with the main driver through `arm_smmu_impl_ops`, with `get_secondary_cmdq` for kernel acceleration and with `hw_info`/`get_viommu_size`/`vsmmu_init` for user-visible virtual SMMU support.

It also uses common SMMUv3 queue initialization and command issue helpers. Each LVCMDQ is represented as an `arm_smmu_cmdq`, so most command publication, valid-map, and sync logic remains in the generic driver.

## Risks and Edge Cases

The hardware has strict order requirements: LVCMDQs must be mapped in ascending order and unmapped in descending order. User allocation enforces the forward dependency, and iommufd dependencies help enforce destruction order, but failures in mid-initialization need to undo mapping, local table insertion, and dependencies exactly once.

Guest-owned queues support only `TLBI_NH_ASID`, `TLBI_NH_VA`, and `ATC_INV`. Unsupported commands must fall back to the kernel queue; otherwise a guest queue could receive commands hardware does not permit. The module parameter `bypass_vcmdq` and debugfs bool intentionally force fallback for comparison/debugging.

`tegra241_vcmdq_hw_deinit` issues a CMD_SYNC on the main SMMU queue to flush a possible guest ATC timeout before reassigning a queue. This protects future VMs from stale timeout reports, but it assumes the main queue remains operational during deinit.

User physical queue base validation is security-sensitive. The base must fit the VCMDQ address field and align to queue length. The userspace VINTF mmap exposes only the VINTF page0 window, while queue memory is supplied by userspace physical address through iommufd.

Error reporting splits VINTF0 and user VINTFs. VINTF0 actively rewrites bad commands to CMD_SYNC via common skip logic, while user errors become events. Event delivery depends on a configured iommufd event queue; otherwise diagnostics may be limited to kernel warnings.

## Test Signals

Tests should cover probe fallback when resource mapping, IRQ request, parameter allocation, or `disable_cmdqv` fails; VINTF0 preallocation and reset ordering; secondary command queue routing and fallback for unsupported commands; `bypass_vcmdq`; per-CPU LVCMDQ selection; VCMDQ enable/disable polling timeouts; guest queue timeout flushing; VINTF error IRQ handling for VINTF0 and user VINTFs; hardware info output; viommu mmap output; user queue length/address/index validation; ascending allocation and descending destruction dependency; SID replacement allocation/exhaustion; and cleanup paths for partially initialized user VINTFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/tegra241-cmdqv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/Makefile

## Purpose

This Makefile selects the objects that build the legacy Arm SMMU v1/v2 driver. It wires the common `arm_smmu` module/built-in object from the core driver, implementation-quirk file, and NVIDIA integration file, and conditionally includes Qualcomm support objects.

## Important APIs, Types, and Functions

There are no C APIs in this file. Its important build targets are `qcom_iommu.o`, `arm_smmu.o`, `arm-smmu.o`, `arm-smmu-impl.o`, `arm-smmu-nvidia.o`, `arm-smmu-qcom.o`, and `arm-smmu-qcom-debug.o`. The `arm_smmu-objs` assignment means the final `arm_smmu` object always includes the core, generic implementation quirks, and NVIDIA implementation code when `CONFIG_ARM_SMMU` is enabled.

## Control Flow

Kbuild evaluates the `obj-*` and `arm_smmu-*` variables based on configuration symbols. `CONFIG_QCOM_IOMMU` builds a separate Qualcomm IOMMU driver object. `CONFIG_ARM_SMMU` builds the Arm SMMU aggregate. `CONFIG_ARM_SMMU_QCOM` appends Qualcomm Arm SMMU implementation support to that aggregate. `CONFIG_ARM_SMMU_QCOM_DEBUG` appends optional Qualcomm debug support.

## State and Persistence Behavior

The file has no runtime state. Its build-time state determines which implementation hooks are linked into the kernel or module. Because `arm-smmu-nvidia.o` is unconditional inside `arm_smmu-objs`, NVIDIA implementation probing is compiled with the generic legacy driver whenever `CONFIG_ARM_SMMU` is enabled.

## Dependencies and Integration Points

The Makefile integrates the `drivers/iommu/arm/arm-smmu/` directory with Linux Kbuild and with Kconfig symbols. It must match prototypes and conditional calls in `arm-smmu.h` and `arm-smmu-impl.c`; for example, `arm-smmu-impl.c` can call `qcom_smmu_impl_init` only when the related config is enabled.

## Risks and Edge Cases

Build linkage is the main risk. Removing a file from `arm_smmu-objs` without guarding its referenced symbols can break all `CONFIG_ARM_SMMU` builds. Adding an implementation object unconditionally increases the baseline driver footprint and can expose missing dependency headers on non-target architectures. Conditional debug objects must remain tied to the correct parent support config.

## Test Signals

Useful validation is matrix build coverage for `CONFIG_ARM_SMMU`, `CONFIG_QCOM_IOMMU`, `CONFIG_ARM_SMMU_QCOM`, and `CONFIG_ARM_SMMU_QCOM_DEBUG` combinations. Link tests should verify the aggregate `arm_smmu` object contains the implementation init/exit paths expected by the core and that no stale object names remain after source renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-impl.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-impl.c

## Purpose

`arm-smmu-impl.c` contains model-specific and platform-specific implementation quirks for the legacy Arm SMMU v1/v2 driver. It supplies alternate register accessors, reset hooks, context initialization hooks, feature masking, and implementation selection for Calxeda secure/non-secure register access, Cavium SMMUv2 erratum handling, Arm MMU-500 behavior, Marvell Armada AP806 MMU-500 access quirks, NVIDIA Tegra integration, and optional Qualcomm support.

## Important APIs, Types, and Functions

Calxeda support is implemented by `arm_smmu_gr0_ns`, `arm_smmu_read_ns`, `arm_smmu_write_ns`, and `calxeda_impl`, redirecting selected secure GR0 register offsets to non-secure aliases.

Cavium support uses `struct cavium_smmu`, `cavium_cfg_probe`, `cavium_init_context`, `cavium_impl`, and `cavium_smmu_impl_init`. It extends the base device allocation to store an `id_base` and offsets ASIDs/VMIDs per SMMU instance for erratum 27704.

MMU-500 support is centered on `arm_mmu500_reset` and `arm_mmu500_impl`. The reset hook clears ACR cache lock on r2p0+, enables unmatched stream ID/context-bank bypass TLB allocation, and optionally disables context-bank next-page prefetch with `CONFIG_ARM_SMMU_MMU_500_CPRE_ERRATA`.

Marvell support uses `mrvl_mmu500_readq`, `mrvl_mmu500_writeq`, `mrvl_mmu500_cfg_probe`, and `mrvl_mmu500_impl`. It splits 64-bit accesses into ordered 32-bit accesses and hides AArch64 page table format support to avoid erratum 582743.

Top-level entry points are `arm_smmu_impl_init`, `arm_smmu_impl_module_init`, and `arm_smmu_impl_module_exit`.

## Control Flow

`arm_smmu_impl_init` first selects model-specific implementation hooks by `smmu->model`. `ARM_MMU500` installs the MMU-500 reset implementation. `CAVIUM_SMMUV2` replaces the generic allocation with a `cavium_smmu` and installs Cavium hooks. It then checks platform integration quirks by device-tree compatibility or property: Calxeda secure-config access installs non-secure register accessors; NVIDIA Tegra compatible strings delegate to `nvidia_smmu_impl_init`; Qualcomm support is initialized when configured; Marvell AP806 installs Marvell access and reset hooks. The function returns the original or replacement `arm_smmu_device`.

Module init/exit only forward to Qualcomm module hooks when `CONFIG_ARM_SMMU_QCOM` is enabled. This keeps the generic implementation file as the central dispatcher without making Qualcomm support mandatory.

## State and Persistence Behavior

Most state is static hook tables. Cavium allocates a larger device structure containing `id_base`; `cavium_cfg_probe` uses a static atomic `context_count` to ensure unique ASID/VMID windows across SMMUs. MMU-500 and Marvell hooks persist by assigning `smmu->impl`. Calxeda and Marvell register accessor changes affect all later reads/writes through the legacy driver's `arm_smmu_*` access wrappers.

Hardware state changes occur in reset/config hooks: MMU-500 ACR/ACTLR fields are modified, Marvell feature bits are masked before page table format selection, and Cavium ASID/VMID offsets alter context bank programming. There is no filesystem persistence.

## Dependencies and Integration Points

The file depends on `arm-smmu.h`, device-tree matching, bitfield helpers, and optional Qualcomm/NVIDIA implementation prototypes from the legacy SMMU header. It is linked into the `arm_smmu` object by the local Makefile. It integrates with the legacy driver through `struct arm_smmu_impl`, whose members include register accessors, reset, config probe, init context, and platform finalize hooks.

## Risks and Edge Cases

Implementation selection order matters. Model quirks are installed first so platform integration quirks can inherit or override them. A later assignment such as Marvell replacing `smmu->impl` can discard previously selected MMU-500 hooks unless the replacement table includes equivalent reset behavior, which this file does for Marvell.

Cavium ID offsetting depends on `num_context_banks` and a global atomic count. Incorrect ordering or reuse across hotplug paths could produce overlapping ASID/VMID allocations. Calxeda register remapping only covers selected GR0 secure registers; missing an offset would leave access to the wrong security alias.

MMU-500 CPRE errata handling depends on secure firmware clearing SACR cache lock; the driver warns if ACTLR writes do not stick. Marvell disables AArch64 formats to work around access-width restrictions, which can reduce functionality on affected systems.

## Test Signals

Build tests should cover Qualcomm configured and unconfigured, MMU-500 CPRE errata on/off, and NVIDIA support linked through the unconditional object. Runtime or emulated tests should exercise implementation selection for each compatible/model, verify Calxeda non-secure offset remapping, Cavium ASID/VMID offset uniqueness, MMU-500 ACR/ACTLR reset writes and warning path, Marvell split 64-bit accessors, and preservation of reset hooks when platform quirks override model hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-impl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-nvidia.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-nvidia.c

## Purpose

`arm-smmu-nvidia.c` implements NVIDIA Tegra integration quirks for the legacy Arm SMMU driver. Tegra194/Tegra234 systems can expose multiple MMU-500 instances that must be programmed identically for non-isochronous clients, and the SMMU driver must coordinate with the Tegra memory controller to program stream ID overrides. This file wraps the generic SMMU device in an NVIDIA-specific structure, mirrors register writes across instances, aggregates TLB sync and fault handling across instances, limits page sizes for a Tegra walk-cache erratum, and finalizes memory-controller device probing.

## Important APIs, Types, and Functions

`struct nvidia_smmu` embeds `struct arm_smmu_device`, stores up to `MAX_SMMU_INSTANCES` MMIO bases, tracks `num_instances`, and holds a `struct tegra_mc *`. Helpers `to_nvidia_smmu` and `nvidia_smmu_page` convert generic SMMU state into instance-specific MMIO pages.

Register accessors are `nvidia_smmu_read_reg`, `nvidia_smmu_write_reg`, `nvidia_smmu_read_reg64`, and `nvidia_smmu_write_reg64`. TLB and reset hooks are `nvidia_smmu_tlb_sync` and `nvidia_smmu_reset`. Fault handling is split across `nvidia_smmu_global_fault_inst`, `nvidia_smmu_global_fault`, `nvidia_smmu_context_fault_bank`, and `nvidia_smmu_context_fault`.

Integration hooks are `nvidia_smmu_probe_finalize`, `nvidia_smmu_init_context`, `nvidia_smmu_impl`, `nvidia_smmu_single_impl`, and `nvidia_smmu_impl_init`.

## Control Flow

`nvidia_smmu_impl_init` is called from the legacy implementation dispatcher for Tegra186/Tegra194/Tegra234 compatible strings. It reallocates the generic SMMU object to `struct nvidia_smmu`, obtains the Tegra memory controller handle, records the already mapped instance-0 base, maps additional memory resources up to two instances, and selects either a single-instance implementation table or a multi-instance mirroring implementation table.

For multi-instance systems, generic register reads come from instance 0 while writes are broadcast to all instances. TLB sync writes the sync register through the generic accessor and then polls the status register on every instance, ORing active bits until all instances are inactive or timeout. Reset clears global fault status on every instance.

Global fault handling scans every instance and reports/clears any nonzero GR0 global fault status with syndrome registers. Context fault handling scans every context bank on every instance because the interrupt line is shared, reports FSR/FSYNR/FAR/CBFRSYNRA, and clears the fault status.

Context initialization restricts page mappings to `PAGE_SIZE` for Tegra194 and Tegra234. This avoids stale walk-cache entries caused by a hardware erratum where the walk-cache index differs between translation and invalidation requests. Probe finalize calls into the memory controller driver for each attached device so SID overrides are programmed.

## State and Persistence Behavior

`struct nvidia_smmu` persists for the SMMU device lifetime. It stores per-instance MMIO mappings, instance count, and memory-controller reference. The selected `smmu.impl` table persists as the legacy core's hook table. Runtime hardware state is written identically across instances for multi-instance configurations, so stream table, context bank, and control register programming stay mirrored.

Fault state is not persisted; handlers read and clear hardware fault registers. Page-size restriction mutates `smmu->pgsize_bitmap` and the io-pgtable config for affected SoCs during context initialization, affecting subsequent domain mappings.

## Dependencies and Integration Points

The file depends on the legacy `arm-smmu.h` interface, Tegra memory-controller API (`devm_tegra_memory_controller_get`, `tegra_mc_probe_device`), platform resources, device-tree matching, MMIO helpers, and Linux IRQ interfaces. It is linked into the legacy `arm_smmu` aggregate by the Makefile and selected by `arm-smmu-impl.c`.

The memory controller integration is essential for SID override programming. The SMMU integration hooks are consumed by the generic legacy driver through `struct arm_smmu_impl`, including register accessors, reset, tlb_sync, fault handlers, probe_finalize, and init_context.

## Risks and Edge Cases

Mirrored writes assume all non-isochronous SMMU instances require identical programming and are compatible. Reads always come from instance 0, so divergent state in another instance is only caught by sync/fault paths. TLB sync timeout ORs status from all instances; one stuck instance reports the same generic timeout message.

Context fault handling scans every bank and every instance on a shared interrupt, which is robust but can be expensive under repeated faults. Fault logs are rate-limited but still indicate serious device or programming errors.

The page-size workaround for Tegra194/Tegra234 reduces mapping granularity to base pages and can impact performance. It mutates the device page-size bitmap during context initialization, so callers must not assume larger MMU-500 page sizes remain available on those SoCs.

`nvidia_smmu_impl_init` supports at most two mirrored instances via `MAX_SMMU_INSTANCES`, while comments mention a third Tegra194 instance used for isochronous devices. The code intentionally handles the paired non-isochronous instances and stops mapping when platform resources end.

## Test Signals

Tests should cover single-resource and dual-resource probe paths, failure to acquire the Tegra memory controller, additional resource mapping failure, correct selection of single versus multi-instance hook tables, write mirroring across instances, read-from-instance-0 behavior, TLB sync success and timeout with one active instance, global and context fault aggregation/clearing, page-size limiting for Tegra194/Tegra234 only, and memory-controller probe-finalize error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-nvidia.c -->
