<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.c

Purpose: IOMMU page-table/configuration page allocator with memory accounting and optional incoherent-walk DMA/cache management. It backs page-table allocations used by several IOMMU backends.

Important APIs/types/functions: `iommu_alloc_pages_node_sz()`, `iommu_free_pages()`, `iommu_put_pages_list()`, `iommu_pages_start_incoherent()`, `iommu_pages_start_incoherent_list()`, `iommu_pages_stop_incoherent_list()`, and `iommu_pages_free_incoherent()`. Static assertions ensure `struct ioptdesc` overlays `struct page` fields safely.

Control flow: allocation rejects highmem, rounds size to a power-of-two order, handles `NUMA_NO_NODE`, allocates a zeroed folio, marks incoherent false, and charges `NR_IOMMU_PAGES` and `NR_SECONDARY_PAGETABLE`. Free/list free reverse accounting and put the folio. Incoherent start either flushes cache directly on x86 or maps the allocation through the DMA API and verifies DMA address equals physical address; stop/free undo DMA mappings on non-x86.

State and persistence: metadata is stored in the page-overlaid `ioptdesc`, including list node and `incoherent` flag. VM/node accounting persists until pages are freed.

Dependencies and integration: used by Intel IR/PASID/PRQ and io-pgtable backends. Depends on folios, node/lruvec stats, DMA mapping, cacheflush on x86, and `iommu-pages.h`.

Risks: overlay assumptions are guarded by static asserts but fragile across `struct page` changes. Incoherent mode assumes direct DMA mappings and rejects translated/truncated DMA addresses. Lists become invalid after `iommu_put_pages_list()` unless reinitialized.

Test signals: allocation/free accounting in `/proc/vmstat`, NUMA allocation, list splice/free, highmem rejection, incoherent start/stop on x86 and non-x86, and DMA mapping error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-pages.c -->
