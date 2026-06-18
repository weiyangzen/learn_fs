# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu.c

## Purpose
Main Linux IOMMU driver for Arm SMMU v1/v2 and MMU-400/401/500 style implementations. It discovers hardware capabilities, registers an IOMMU device, translates firmware stream IDs into stream-map entries, allocates context banks and page tables for domains, implements map/unmap/iova-to-phys/fault handling, and provides runtime/system PM.

## Important APIs, Types, And Functions
The public IOMMU contract is `arm_smmu_ops` with identity and blocked domains, `domain_alloc_paging`, `probe_device`, `release_device`, `device_group`, `of_xlate`, reserved region handling, and default domain ops. Domain state is `struct arm_smmu_domain`, device state is `struct arm_smmu_device`, master routing state is `struct arm_smmu_master_cfg`, and stream entries are `arm_smmu_smr`/`arm_smmu_s2cr`. Key functions include TLB invalidation helpers, `arm_smmu_read_context_fault_info()`, `arm_smmu_context_fault()`, `arm_smmu_init_domain_context()`, `arm_smmu_write_context_bank()`, `arm_smmu_master_alloc_smes()`, `arm_smmu_attach_dev()`, map/unmap wrappers, hardware ATOS `arm_smmu_iova_to_phys_hard()`, `arm_smmu_device_cfg_probe()`, reset/probe/remove/shutdown, and PM callbacks.

## Control Flow
Platform probe parses DT or ACPI model data, maps registers, selects implementation hooks, collects IRQs and clocks, enables clocks, probes ID registers, requests global fault IRQs, installs firmware reserved memory region bypass SMRs, resets the SMMU, registers the IOMMU device, and enables runtime PM when appropriate. Device probe resolves an SMMU from `iommu_fwspec`, validates SID/mask bits, creates master config, allocates stream map entries, and links PM to the SMMU. Domain attach lazily allocates a context bank, selects stage and page-table format, allocates io-pgtable ops, writes context bank registers, requests the context fault IRQ, then routes the master's S2CR entries to the context bank. Map/unmap delegate to io-pgtable ops under runtime PM and synchronize TLBs through stage-specific flush ops.

## State And Persistence
All state is runtime kernel memory plus SMMU registers: context bank bitmaps, stream-map entries, context bank register caches, feature flags, IRQ indices, page-table ops, group pointers, and module parameters `force_stage` and `disable_bypass`. There is no disk persistence. Runtime PM resets hardware on resume, so software state must be sufficient to reprogram stream maps and context banks.

## Dependencies And Integration Points
It integrates with Linux IOMMU core, io-pgtable formats, OF/ACPI IORT firmware, PCI and fsl-mc grouping, reserved-memory regions, DMA-IOMMU MSI reservations, platform drivers, clocks, runtime PM, and vendor implementations through `struct arm_smmu_impl`. Qualcomm, Nvidia, Cavium, MMU-500, and generic implementations can override register access, reset, context init, S2CR writes, TLB sync, context faults, and default domain type.

## Risks
Stream-map overlap detection and reference counts must be exact or devices may share/overwrite translations. The `disable_bypass` default is security-sensitive. Domain initialization publishes `pgtbl_ops` only after IRQ/context setup; ordering mistakes would race map/unmap. Runtime PM wraps register access, but paths that ignore errors could touch suspended hardware. Fault handlers clear FSR and resume stalled transactions, so return-code handling from `report_iommu_fault()` matters. Hardware capability parsing and implementation quirks can alter page sizes, context counts, and bypass behavior.

## Test Signals
Boot tests on SMMUv1, SMMUv2, MMU-500, stream-indexing and stream-matching systems; DT and ACPI probing; forced stage module parameter; bypass disabled/enabled; RMR bypass installation; PCI alias SIDs; context fault and global fault injection; runtime suspend/resume with active domains; map/unmap stress with DMA API; iova-to-phys hard/soft fallback; vendor impl hook coverage.
