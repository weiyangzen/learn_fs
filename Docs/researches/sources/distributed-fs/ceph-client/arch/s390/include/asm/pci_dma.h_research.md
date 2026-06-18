# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_dma.h

Purpose: This header defines s390 zPCI I/O translation anchor and IOMMU page-table encodings plus DMA mapping counters.

Important APIs/types/functions: `enum zpci_ioat_dtype`, IOTA flags and table-size constants, region/segment/page-table type, shift, mask, valid/protection bits, `struct zpci_iommu_ctrs`, and `zpci_get_iommu_ctrs()` are provided.

Control flow: The zPCI IOMMU code builds I/O translation tables using the defined region/segment/page-table hierarchy, encodes the IOTA for firmware registration, and updates counters for mapped/unmapped pages and RPCIT invalidations.

State and persistence: Persistent state is the DMA translation table tree attached to a zPCI device/domain and its atomic counter block.

Dependencies and integration points: It depends on page default storage key definitions and zPCI device structures, integrating DMA API/IOMMU core with zPCI firmware instructions.

Risks and test signals: Bit encoding mistakes can map wrong DMA addresses or fail invalidation. Tests should cover DMA map/unmap for 4K/1M/2G ranges, IOMMU domain attach, RPCIT counter updates, protection bits, and device DMA under load.
