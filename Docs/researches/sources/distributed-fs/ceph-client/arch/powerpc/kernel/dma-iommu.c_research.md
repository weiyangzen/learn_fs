<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-iommu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-iommu.c

## Purpose
`dma-iommu.c` provides PowerPC DMA mapping operations for devices using the architecture IOMMU/TCE infrastructure, plus direct-DMA bypass decisions for platforms that pre-map RAM.

## Important APIs, Types, And Functions
Architecture hooks include `arch_dma_map_phys_direct()`, `arch_dma_unmap_phys_direct()`, `arch_dma_map_sg_direct()`, `arch_dma_unmap_sg_direct()`, `arch_dma_alloc_direct()`, and `arch_dma_free_direct()` when direct map support is configured. The IOMMU map ops are implemented by `dma_iommu_alloc_coherent()`, `dma_iommu_free_coherent()`, `dma_iommu_map_phys()`, `dma_iommu_unmap_phys()`, `dma_iommu_map_sg()`, `dma_iommu_unmap_sg()`, `dma_iommu_dma_supported()`, `dma_iommu_get_required_mask()`, and exported `dma_iommu_ops`.

## Control Flow
Direct bypass is allowed only when `dev->bus_dma_limit` and DMA offsets show the address/handle fits the direct aperture. IOMMU operations delegate to `iommu_alloc_coherent`, `iommu_map_phys`, `ppc_iommu_map_sg`, and matching unmap/free helpers using `get_iommu_table_base(dev)`. `dma_supported` enables `dma_ops_bypass` for PCI devices whose PHB supports bypass for the requested mask; otherwise it validates IOMMU table availability and table offset against the device mask.

## State And Persistence
Runtime state changes include `dev->dma_ops_bypass`. IOMMU mapping state is maintained in platform IOMMU tables, not in this file. No persistent storage exists.

## Dependencies And Integration Points
It integrates with Linux DMA API, PCI host bridge controller ops, PowerPC IOMMU table management, `dma_common_*` helpers, scatterlist iteration, and device masks.

## Risks
Off-by-one checks around `bus_dma_limit`, scatterlist end addresses, and table offset/mask validation can cause invalid DMA or unnecessary bounce/IOMMU use. Calling `to_pci_dev()` in bypass support assumes PCI devices.

## Test Signals
Signals include DMA API tests, PCI devices with 32-bit and 64-bit masks, IOMMU table absence errors, direct-bypass logging, coherent allocation/free, scatter-gather map/unmap, and stress with memory above 4GB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-iommu.c -->
