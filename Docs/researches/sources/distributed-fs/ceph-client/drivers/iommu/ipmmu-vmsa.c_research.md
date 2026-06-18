# sources/distributed-fs/ceph-client/drivers/iommu/ipmmu-vmsa.c

## Purpose
`ipmmu-vmsa.c` is the Renesas VMSA-compatible IPMMU driver. It registers an `iommu_ops` implementation, creates ARM LPAE stage-1 page tables, manages IPMMU contexts and micro-TLBs, handles faults, and supports SoC-specific register layouts for R-Car Gen2/Gen3/Gen4 and related RZ/G2 parts.

## Important APIs, Types, and Functions
Important types are `struct ipmmu_features`, `struct ipmmu_vmsa_device`, and `struct ipmmu_vmsa_domain`. Feature data describes context counts, uTLB count, register offsets, secure alias behavior, cache snooping, reserved contexts, and generation-specific control bits. The device tracks MMIO base, root/leaf relationship, context bitmap, active domain table, uTLB-to-context map, optional ARM DMA mapping, and embedded `iommu_device`. Domains track page-table configuration, `io_pgtable_ops`, context ID, associated MMU, and a mutex.

Core functions include `ipmmu_probe()`, `ipmmu_remove()`, `ipmmu_domain_alloc_paging()`, `ipmmu_attach_device()`, `ipmmu_iommu_identity_attach()`, `ipmmu_map()`, `ipmmu_unmap()`, `ipmmu_iova_to_phys()`, `ipmmu_domain_init_context()`, `ipmmu_domain_setup_context()`, `ipmmu_tlb_invalidate()`, `ipmmu_utlb_enable()`, `ipmmu_utlb_disable()`, and `ipmmu_irq()`.

## Control Flow and State
Probe allocates device state, maps registers, applies non-secure alias offsets when required, identifies whether the instance is a root IPMMU or leaf/cache IPMMU, requests the root IRQ, resets contexts, reserves context 0 on affected SoCs, and registers leaf-capable instances with the IOMMU core. Device tree `of_xlate` validates SoC allow/deny policy, records uTLB IDs in the fwspec, and attaches the device to the platform IPMMU.

On attach, the domain lazily initializes a context on the root IPMMU, creates `ARM_32_LPAE_S1` page-table ops with non-secure quirks, programs TTBR/TTBCR/MAIR/IMBUSCR/IMCTR, then enables each uTLB from the fwspec. Detaching to the identity domain disables the associated uTLBs but leaves context lifetime tied to domain free. Map and unmap delegate to io-pgtable; TLB operations flush the whole context. Resume resets the root and reprograms active contexts and micro-TLBs.

Runtime state is volatile hardware and kernel memory: context bitmap, `domains[]`, `utlb_ctx[]`, `mapping`, page-table ops, and saved domain references. No persistent storage is used.

## Dependencies and Integration Points
The driver integrates with platform devices, device tree, `iommu_device_register()`, io-pgtable `ARM_32_LPAE_S1`, generic device groups, ARM legacy `dma_iommu_mapping` when `CONFIG_ARM && !CONFIG_IOMMU_DMA`, PCI device checks, SoC matching, runtime register access, and IRQ fault reporting through `report_iommu_fault()`.

## Risks and Test Signals
Important risks include root discovery ordering, reserved context handling, uTLB sharing without reference counting, whole-context flush granularity, context lifetime while devices detach, SoC allowlist/denylist drift, secure/non-secure alias assumptions, and resume correctness. Test signals include probe deferral on leaf before root, multiple device attach to the same domain, fault interrupt reporting, suspend/resume with active uTLBs, Gen2 versus Gen3/Gen4 register offsets, denied SoCs/devices, and DMA map/unmap workloads validating TLB flush behavior.
