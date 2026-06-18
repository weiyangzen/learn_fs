<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.c

Purpose: Implements the VDUSE MMU-based software IOTLB and bounce-buffer domain used to map kernel DMA/I/O virtual addresses to userspace-visible memory.

Important APIs/functions: Public functions include map set/clear, sync for device/CPU, streaming map/unmap page, coherent alloc/free, bounce map reset, user bounce page add/remove, domain create/destroy, and global init/exit. Internal helpers manage vhost IOTLB ranges with file references, allocate/free IOVA ranges, map/unmap bounce pages, copy bounce data, fault mmap pages, and release all resources.

Control flow: `vduse_domain_create()` allocates the domain, vhost IOTLB, bounce map array, anon inode file, locks, and two IOVA domains: stream IOVAs below the bounce window and coherent IOVAs above it. Streaming `map_page` allocates an IOVA from the bounce window, ensures the bounce IOTLB mapping exists, records original physical addresses per 4 KiB bounce segment, and optionally copies CPU data into bounce pages. `unmap_page` optionally copies back and frees the IOVA. Coherent alloc maps `virt_to_phys(orig)` into the IOTLB with the domain file as mmap backing. `mmap` faults return either bounce pages or coherent pages.

State and persistence: `struct vduse_iova_domain` owns stream and coherent `iova_domain`s, `bounce_maps`, bounce size, IOVA limit, vhost IOTLB, anon file, user-bounce mode, and locks. IOTLB entries hold `vdpa_map_file` references. All state is runtime-only and released on anon file close.

Dependencies and integration points: Uses vhost IOTLB, Linux IOVA allocator/cache, anon inode mmap, page copy helpers, DMA directions/attrs, and vDPA map-file context. Called by VDUSE device code for DMA mapping and userspace mmap of DMA windows.

Risks: Locking is subtle: `iotlb_lock` protects IOTLB mutations and `bounce_lock` protects bounce page/user page switching. Release calls `vduse_domain_remove_user_bounce_pages()` and kernel bounce free while holding `iotlb_lock`, while those functions take `bounce_lock`, so callers must avoid inverse ordering. Bounce segments are 4 KiB even on larger PAGE_SIZE, requiring shared page handling. User bounce pages require full mapping, not partial. Incorrect sync direction loses data.

Test signals: Create/destroy domains, map/unmap streaming pages with all DMA directions and skip-sync attrs, add/remove user bounce pages with data preservation, mmap bounce and coherent ranges, set/clear external IOTLB maps with file reference accounting, fault invalid pages to SIGBUS, and run with PAGE_SIZE larger than 4 KiB if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_user/iova_domain.c -->
