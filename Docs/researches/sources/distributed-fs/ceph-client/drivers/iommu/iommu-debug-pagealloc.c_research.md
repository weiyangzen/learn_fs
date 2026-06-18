<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debug-pagealloc.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-debug-pagealloc.c

Purpose: optional IOMMU API debug page-allocation sanitizer. It tracks physical pages mapped through IOMMU domains using `page_ext` metadata and warns when pages are freed while still IOMMU-mapped or when map/unmap accounting underflows.

Important APIs/types/functions: `page_iommu_debug_ops`, static key `iommu_debug_initialized`, `__iommu_debug_check_unmapped()`, `__iommu_debug_map()`, `__iommu_debug_unmap_begin()`, `__iommu_debug_unmap_end()`, `iommu_debug_init()`, and early parameter `iommu.debug_pagealloc`.

Control flow: early parameter sets `needed`; page-ext allocates `struct iommu_debug_metadata` when needed. Init enables the static key. Map increments per-minimum-IOMMU-page refcounts for the physical range. Unmap begin decrements by translating IOVA to PA first; unmap end re-increments the failed tail if unmap was partial. Free checks warn and dump page owner for any page with nonzero IOMMU refcount.

State and persistence: per-page `page_ext` atomic refcounts persist while debug mode is active. Static key gates low-overhead wrappers in `iommu-priv.h`.

Dependencies and integration: integrates with the core IOMMU map/unmap wrappers, page owner, page_ext operations, and domain `pgsize_bitmap`.

Risks: debug accounting relies on `iommu_iova_to_phys()` during unmap begin and on the smallest domain page size for symmetric accounting. It adds overhead and can miss pages without page_ext metadata. Partial unmap handling must mirror core unmap return values.

Test signals: boot with `iommu.debug_pagealloc=1`, map/unmap balanced ranges, forced partial unmap, freeing still-mapped pages to trigger warnings/page-owner dumps, and static-key disabled overhead checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debug-pagealloc.c -->
