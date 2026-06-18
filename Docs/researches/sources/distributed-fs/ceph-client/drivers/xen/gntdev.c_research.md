# sources/distributed-fs/ceph-client/drivers/xen/gntdev.c

Purpose: implements `/dev/xen/gntdev`, allowing userspace to map grants from other domains, unmap them, set unmap notifications, query offsets, and perform grant-copy operations.

Important APIs/functions: file operations are `gntdev_open`, `gntdev_release`, `gntdev_ioctl`, and `gntdev_mmap`. Shared helpers include `gntdev_alloc_map`, `gntdev_add_map`, `gntdev_put_map`, `gntdev_test_page_count`, and `gntdev_map_grant_pages`. IOCTL handlers cover map/unmap grant ref, get offset for vaddr, set unmap notify, grant copy, and optional dma-buf commands.

Control flow: map-grant-ref allocates a `gntdev_grant_map`, copies refs from userspace, adds it to a sorted per-file list, and returns a page-offset token. `mmap` finds the map, validates shared writable semantics, sets VMA flags, initializes PV MMU interval notification and PTE map ops if needed, maps grants through Xen, and maps pages into userspace for non-PV. Unmap removes the map from the list and drops a ref. Async unmap waits for page refs to drop, clears notifications, issues Xen unmap ops, clears foreign mappings, updates live-grant counts, and releases the map. Grant-copy batches pin user pages, builds `GNTTABOP_copy` operations, and updates per-segment statuses.

State and persistence: per-open `gntdev_priv` tracks maps, locks, reusable copy batch, optional DMA device, and optional dma-buf private state. Each map tracks arrays of grants, map/unmap ops, pages, removal flags, live grants, refcount, PV notifier, and unmap notification.

Dependencies and integration: depends on Xen grant-table mapping/copy APIs, balloon/unpopulated pages, event-channel notifications, Linux VMA and MMU interval notifiers, miscdevice, DMA mapping, and optional dma-buf extension.

Risks: PV paths pass PTE addresses to the hypervisor and rely on MMU interval invalidation; async unmap can recurse through refcount release if not guarded; grant-copy pins user pages and must dirty/unpin correctly; map offsets are per-file logical indices; readonly and private writable mappings are rejected; page-count limits protect memory pressure.

Test signals: map/unmap grants from a peer domain, mmap read-only and writable cases, split/unmap VMAs on PV, close while mappings remain, exercise unmap notifications, grant copy local-to-grant and grant-to-local paths, dma-buf IOCTLs when enabled, and stress async unmap with elevated page refs.
