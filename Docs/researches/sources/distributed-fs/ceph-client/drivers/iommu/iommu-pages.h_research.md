<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.h

Purpose: public internal header for IOMMU page-table page allocation, list management, and incoherent page-table cache/DMA synchronization helpers.

Important APIs/types/functions: `struct ioptdesc` overlays `struct page`; converters include `folio_ioptdesc()`, `ioptdesc_folio()`, and `virt_to_ioptdesc()`. Allocation/list helpers include `iommu_alloc_pages_node_sz()`, `iommu_alloc_pages_sz()`, `iommu_free_pages()`, `iommu_pages_list_add()`, `iommu_pages_list_splice()`, `iommu_pages_list_empty()`, and incoherent start/stop/free/flush helpers.

Control flow: callers allocate pages, optionally add them to an `iommu_pages_list`, optionally start incoherent operation for noncoherent page-table walkers, flush updates through `iommu_pages_flush_incoherent()`, and free individually or as a list.

State and persistence: `ioptdesc` stores list linkage and an `incoherent` flag or page index overlay. On x86, incoherent stop is intentionally a no-op for performance and free ignores the flag; on other architectures the DMA API mapping state matters.

Dependencies and integration: included by Intel IOMMU and io-pgtable code. It depends on core IOMMU list type definitions, folios, DMA mapping, and architecture cacheflush support.

Risks: because `ioptdesc` overlays `struct page`, field layout drift is hazardous and must remain paired with `iommu-pages.c` static asserts. Callers must not use highmem allocations and must not reuse lists after splice/free without reinitialization.

Test signals: compile on x86 and non-x86, list helper behavior, incoherent flush semantics, and static assertions after memory-management changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.h -->
