# sources/distributed-fs/ceph-client/include/linux/iommu-dma.h

Purpose: This header declares DMA API operations implemented through IOMMU-backed address translation.

Important APIs, types, and functions: `use_dma_iommu` reports whether a device uses IOMMU DMA. Declared operations include physical and SG map/unmap, coherent allocation/free, mmap/get_sgtable, merge-boundary and mapping-size queries, noncontiguous allocation/free/vmap/mmap, and CPU/device sync functions.

Control flow: DMA API implementations call these helpers when `dev->dma_iommu` is active. Mapping functions create IOVA mappings for physical pages or scatterlists; unmap functions tear them down. Sync functions handle cache maintenance as needed for the DMA direction and device coherency.

State and persistence: Persistent state is in the device's DMA-IOMMU cookie/domain and allocated IOVA mappings. Noncontiguous allocations return `sg_table` state that must be freed through matching helpers.

Dependencies and integration points: Depends on DMA direction definitions, `struct device`, scatterlists, VMAs, IOMMU domains, and the generic DMA mapping layer.

Risks: Mismatched map/unmap sizes or directions can leak IOVAs or corrupt cache coherency. Noncontiguous mappings require careful vmap/vunmap and mmap handling. Disabled `CONFIG_IOMMU_DMA` makes `use_dma_iommu` false but declarations remain for implementation units.

Test signals: Exercise single and SG mapping, sync direction behavior, allocation/free, mmap and get_sgtable, noncontiguous paths, merge-boundary reporting, and devices with and without `dma_iommu`.
