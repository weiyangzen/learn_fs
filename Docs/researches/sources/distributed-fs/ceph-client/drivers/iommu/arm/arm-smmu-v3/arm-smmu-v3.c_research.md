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
