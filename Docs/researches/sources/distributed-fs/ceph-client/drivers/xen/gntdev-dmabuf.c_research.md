# sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.c

Purpose: adds dma-buf import/export IOCTL support to gntdev, allowing Xen grant mappings to be exported as dma-buf FDs and external dma-bufs to be converted into grant references for another domain.

Important APIs/functions: exports `gntdev_ioctl_dmabuf_exp_from_refs`, `gntdev_ioctl_dmabuf_exp_wait_released`, `gntdev_ioctl_dmabuf_imp_to_refs`, `gntdev_ioctl_dmabuf_imp_release`, `gntdev_dmabuf_init`, and `gntdev_dmabuf_fini`. Core objects are `struct gntdev_dmabuf`, `struct gntdev_dmabuf_priv`, wait objects, and dma-buf attachment state.

Control flow: export-from-refs allocates a gntdev map, fills foreign grant refs, maps them into pages, creates a dma-buf with `dma_buf_export`, installs an FD, and keeps the gntdev file alive. dma-buf attach/map creates an sg table from pages and maps it for the attachment device, caching one direction per attachment. Release removes the underlying gntdev map and signals any waiter. Import-to-refs attaches to an external dma-buf, maps it bidirectionally, validates zero offset and expected size, derives GFNs from DMA addresses, grants those GFNs to the requested domid, returns grant refs to userspace, and tracks the imported object until release.

State and persistence: per-open dma-buf private state tracks exported buffers, import buffers, and wait objects under one mutex. Exported objects are kref-managed and hold a file reference. Imported objects hold dma-buf attachments, sg tables, and grant refs until explicitly released or gntdev teardown.

Dependencies and integration: depends on dma-buf core, DMA mapping APIs, Xen grant-table APIs, gntdev map helpers, and a configured DMA device from gntdev. It is disabled for PV export because dma-buf support requires the non-PV path in this implementation.

Risks: imported dma-bufs are interpreted from DMA addresses rather than struct pages; mismatched size or offsets fail; grant references must be ended before detach; export wait semantics depend on kref release; attachment direction cannot change without detach; failures after partial grant creation must end foreign access.

Test signals: export grant refs to a dma-buf FD, attach/map/unmap from another driver, wait for release with timeout and success cases, import a dma-buf into refs, release imports, close gntdev with imports live, and verify error paths for PV, bad count, wrong size, nonzero sg offset, and stale fd.
