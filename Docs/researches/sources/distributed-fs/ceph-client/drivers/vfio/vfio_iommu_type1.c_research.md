<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_type1.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_type1.c

## Purpose
This file implements the generic VFIO Type1 IOMMU backend used for DMA mapping userspace memory into IOMMU domains. It supports v1 and v2 semantics, page pinning, IOVA aperture and reserved-region management, dirty page tracking, external device pin/unpin, and CPU-mediated DMA read/write.

## Important APIs, types, and functions
Main state types are `struct vfio_iommu`, `struct vfio_domain`, `struct vfio_dma`, `struct vfio_iommu_group`, `struct vfio_iova`, and `struct vfio_pfn`. The backend registers `vfio_iommu_driver_ops_type1`. Important functions include `vfio_dma_do_map`, `vfio_dma_do_unmap`, `vfio_pin_map_dma`, `vfio_unmap_unpin`, `vfio_iommu_replay`, `vfio_iommu_type1_attach_group`, `vfio_iommu_type1_detach_group`, `vfio_iommu_type1_dirty_pages`, `vfio_iommu_type1_pin_pages`, `vfio_iommu_type1_unpin_pages`, and `vfio_iommu_type1_dma_rw`.

## Control flow
Open allocates an IOMMU object, initializes domain/IOMMU lists and DMA rb-tree, sets `dma_avail`, and distinguishes v1 from v2. Attach allocates an IOMMU domain for the group, attaches it, validates interrupt remapping unless explicitly unsafe, intersects domain apertures, excludes reserved regions, attempts compatible-domain sharing, replays existing mappings into a new domain, and updates supported page sizes. MAP_DMA validates overflow, permissions, alignment, overlap, IOVA validity, and mapping limits, then pins userspace pages in batches, accounts memlock, maps them into every domain, and inserts a `vfio_dma` rb-tree node. UNMAP_DMA validates v1/v2 granularity rules, optionally invalidates vaddrs for update, notifies device DMA-unmap users, returns dirty bitmaps if requested, unmaps IOMMU entries, unpins pages, and removes DMA nodes. Dirty tracking allocates per-DMA bitmaps, populates them when scope changes, and reports by user bitmap.

## State and persistence behavior
All state is in kernel memory tied to a VFIO container: domain list, emulated groups, valid IOVA ranges, rb-tree of user DMA mappings, per-DMA pinned PFN tree, per-DMA dirty bitmap, owning task/mm, memlock accounting, dirty tracking flag, and device callback list. No disk persistence exists. Mappings can outlive the task thread because the mm and group leader references are retained.

## Dependencies and integration points
The backend depends on IOMMU API, mm/GUP long-term pinning, rbtree, VFIO core IOMMU driver registration, user access helpers, iova bitmap helpers, and optional emulated-IOMMU devices that use external pin/unpin callbacks. It feeds VFIO container ioctls and device helper APIs such as `vfio_pin_pages()` and `vfio_dma_rw()`.

## Risks and test signals
Risks include long-term pin accounting errors, reserved-region/aperture conflicts, unsafe-interrupt opt-in, dirty bitmap size validation, invalid-vaddr update races, and detach cleanup with external pinned pages. Test signals include v1 versus v2 unmap granularity, map overlap/overflow/alignment failures, `dma_entry_limit`, dirty tracking start/stop/get, update-vaddr rejection with mdevs, attach replay after mappings exist, detach of last domain, memlock limit failures, and kthread `dma_rw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_iommu_type1.c -->
