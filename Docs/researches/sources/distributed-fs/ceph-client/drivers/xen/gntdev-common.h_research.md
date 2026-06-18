# sources/distributed-fs/ceph-client/drivers/xen/gntdev-common.h

Purpose: declares shared state and helper prototypes used by the gntdev core and dma-buf extension for mapping foreign grants into kernel, userspace, or DMA-capable memory.

Important APIs/functions: defines `struct gntdev_priv`, `struct gntdev_unmap_notify`, and `struct gntdev_grant_map`. Declares `gntdev_alloc_map`, `gntdev_add_map`, `gntdev_put_map`, `gntdev_test_page_count`, and `gntdev_map_grant_pages`.

Control flow: gntdev users allocate a `gntdev_grant_map`, fill grant refs, add it to a file's sorted map list, map grant pages, and later drop references through `gntdev_put_map`. dma-buf code reuses the same map structure for exported buffers backed by foreign grants.

State and persistence: `gntdev_priv` stores per-file map lists, locks, reusable grant-copy batches, and optional DMA/dma-buf context. `gntdev_grant_map` stores all per-mapping arrays, page backing, grant map/unmap ops, user refcounting, removal flags, live grant count, MMU notifier state, optional DMA allocation metadata, and unmap notification.

Dependencies and integration: depends on Linux MM/MMU interval notifier types, Xen grant-table definitions, event channels, and optional `CONFIG_XEN_GRANT_DMA_ALLOC` and `CONFIG_XEN_GNTDEV_DMABUF`.

Risks: this structure is a cross-file contract; layout or semantic changes affect normal mmap, copy, asynchronous unmap, PV PTE handling, and dma-buf export paths. The `being_removed` and `live_grants` fields are central to avoiding duplicate unmap operations.

Test signals: build with and without grant DMA allocation and dma-buf config, run gntdev mmap/unmap, PV invalidation, grant copy, and dma-buf export/import tests.
