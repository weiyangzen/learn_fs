<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntalloc.h -->
# sources/distributed-fs/ceph-client/include/uapi/xen/gntalloc.h

Purpose: defines the `/dev/xen/gntalloc` ABI for allocating local pages, granting them to another Xen domain, deallocating grant references, and configuring unmap notifications.

Important APIs and types: `ioctl_gntalloc_alloc_gref` takes domid, flags, count and returns an mmap offset plus flexible grant-reference IDs. `ioctl_gntalloc_dealloc_gref` releases a range by index/count. `ioctl_gntalloc_unmap_notify` configures byte clearing and/or event-channel notification on unmap. Flags include `GNTALLOC_FLAG_WRITABLE`, `UNMAP_NOTIFY_CLEAR_BYTE`, and `UNMAP_NOTIFY_SEND_EVENT`.

Control flow: userspace allocates grants, mmaps the returned offset, shares grant refs with a peer domain, optionally sets crash/unmap notification, and deallocates after peers stop using the pages.

State and persistence: per-device/file state tracks allocated pages, grant refs, mmap offsets, peer access, and unmap notifications. Pages are transient but may carry shared-memory protocol state while mapped.

Dependencies and integration points: depends on Linux types and Xen grant-table/event-channel mechanisms. It integrates with interdomain shared-memory protocols and robust mutex/close notification schemes.

Risks and test signals: risks include flexible-array count sizing, writable grant policy, deallocating while mapped by peers, notification overwrite behavior, and index/page offset validation. Test allocate/mmap/share/dealloc, invalid counts, notification clear/send paths, peer crash cleanup, and 32/64-bit ioctl layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/xen/gntalloc.h -->
