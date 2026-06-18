# sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu_v1.c

## Purpose
`mtk_iommu_v1.c` is the older MediaTek MT2701 M4U v1 IOMMU driver. Unlike the modern driver, it supports a single shared 4GB IOVA domain with 4K-only mappings and manually managed first-level page-table entries.

## Important APIs, Types, and Functions
Runtime state is `struct mtk_iommu_v1_data`, which stores MMIO base, IRQ, device, clock, protect buffer address, active domain, embedded `iommu_device`, legacy ARM DMA mapping, SMI larb data, and suspend registers. Domains are `struct mtk_iommu_v1_domain`, with a spinlock, `iommu_domain`, coherent page-table VA/PA, and owning data pointer.

Core functions include `mtk_iommu_v1_probe()`, `mtk_iommu_v1_remove()`, `mtk_iommu_v1_create_mapping()`, `mtk_iommu_v1_probe_device()`, `mtk_iommu_v1_probe_finalize()`, `mtk_iommu_v1_attach_device()`, `mtk_iommu_v1_identity_attach()`, `mtk_iommu_v1_domain_finalise()`, `mtk_iommu_v1_map()`, `mtk_iommu_v1_unmap()`, `mtk_iommu_v1_iova_to_phys()`, `mtk_iommu_v1_hw_init()`, `mtk_iommu_v1_isr()`, and suspend/resume callbacks.

## Control Flow and State
Probe allocates data, creates a DMA-capable protect buffer, maps registers, obtains IRQ and `bclk`, discovers larb devices, initializes hardware, registers the IOMMU, and becomes a component master. Device probing walks the consumer's `iommus` phandles itself, creates/updates the fwspec, creates a single legacy ARM DMA mapping if needed, validates all ports are in one larb, and adds a runtime-PM device link to that larb. Probe-finalize attaches the device to the ARM DMA mapping.

Attach only operates on the internally created domain. The first attach allocates a 4MB coherent page table, writes its physical address to `REG_MMU_PT_BASE_ADDR`, and stores the domain as `data->m4u_dom`; every attach enables SMI MMU bits for the relevant ports. Map writes one 32-bit descriptor per 4K page under `pgtlock`, flushes the mapped range, and returns `-EEXIST` if an existing PTE is encountered. Unmap zeroes PTEs and flushes. ISR reads fault status, IOVA, PA, and larb/port, reports a read fault, clears interrupts, and flushes all TLBs. Suspend saves selected registers; resume restores registers, TTBR, and protect address.

## Dependencies and Integration Points
The driver integrates with legacy ARM `dma_iommu_mapping`, the IOMMU core, SMI larb component framework, device links, platform resources, clocks, DT memory-port bindings, and generic device groups. It does not use `io_pgtable_ops`; page-table management is local.

## Risks and Test Signals
Risks include assuming one global domain, no write/read fault distinction, manual PTE management, possible NULL `m4u_dom` on resume if suspend occurs before attach, partial map behavior after encountering an existing PTE, and strict single-larb validation. Test signals include 4K map/unmap, duplicate map returning `-EEXIST`, fault injection, suspend/resume after attach, DMA mapping creation on ARM, device-link cleanup, and larb phandle probe deferral.
