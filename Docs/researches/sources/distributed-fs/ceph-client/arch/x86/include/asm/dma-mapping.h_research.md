
# sources/distributed-fs/ceph-client/arch/x86/include/asm/dma-mapping.h

Purpose: x86 hook for generic DMA mapping operations.

Important APIs and control flow: declares global `dma_ops` and returns it from `get_arch_dma_ops()`. Generic DMA code uses this to dispatch map/unmap/sync behavior.

State, dependencies, and risks: state is the selected DMA operations table, commonly influenced by IOMMU, SWIOTLB, or direct DMA setup. Dependencies include DMA-mapping core. Risks include `dma_ops` not initialized before use or being inconsistent with device/IOMMU state. Test signals are DMA API debug, IOMMU/SWIOTLB boot tests, and driver DMA mapping coverage.
