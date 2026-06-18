<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/gntdev.h

Purpose: defines the `/dev/xen/gntdev` ABI for mapping foreign grant references, unmapping them, resolving mmap offsets, limiting grants, setting unmap notifications, copying grant segments, and exporting/importing grants through dma-buf.

Important APIs and types: `ioctl_gntdev_map_grant_ref`, `unmap_grant_ref`, `get_offset_for_vaddr`, `set_max_grants`, and `unmap_notify` define core mapping control. `gntdev_grant_copy_segment` and `ioctl_gntdev_grant_copy` describe local/foreign copy operations with per-segment status. dma-buf structs export refs to an fd, wait for release, import an fd to refs, and release imports. DMA flags select write-combine or coherent backing.

Control flow: userspace inserts grant refs into a mapping table, mmaps the returned opaque offset, uses or shares the memory, then munmaps before unmapping. Copy ioctls perform grant-table copy operations without persistent mappings. dma-buf ioctls bridge Xen grant memory with Linux dma-buf sharing.

State and persistence: state is per gntdev instance: mapping table entries, maximum grant limit, live VMAs, unmap notifications, copy status, exported/imported dma-buf references, and backing allocation type. No state persists after fd/release except peer-visible effects.

Dependencies and integration points: depends on Linux types and Xen grant types (`grant_ref_t`, `domid_t`) plus `__user` annotations. It integrates with Xen grant tables, mmap, dma-buf, graphics/Wayland use cases, and interdomain copy protocols.

Risks and test signals: risks include refs flexible-array sizing, requiring munmap before unmap, split local buffers across Xen page boundaries, per-segment status handling, dma-buf lifetime waits, and access-control to foreign grants. Test map/unmap/mmap-offset recovery, copy success/failure statuses, invalid mixed local source/dest segments, dma-buf export/import/release, and max grant limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntdev.h -->
