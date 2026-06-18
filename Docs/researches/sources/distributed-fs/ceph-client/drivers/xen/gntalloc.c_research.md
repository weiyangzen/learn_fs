# sources/distributed-fs/ceph-client/drivers/xen/gntalloc.c

Purpose: implements `/dev/xen/gntalloc`, a userspace device for allocating local pages, granting them to another Xen domain, and mapping those pages into the allocating process.

Important APIs/functions: file operations are `gntalloc_open`, `gntalloc_release`, `gntalloc_ioctl`, and `gntalloc_mmap`. IOCTL helpers implement grant allocation, deallocation, and unmap notification. Core types are `struct gntalloc_gref`, `struct notify_info`, `struct gntalloc_file_private_data`, and `struct gntalloc_vma_private_data`.

Control flow: allocation copies a request from userspace, enforces the global `limit`, assigns file offsets, allocates zeroed pages, creates grant refs via `gnttab_grant_foreign_access`, and returns refs and offsets. `mmap` requires `VM_SHARED`, finds contiguous grant records by offset, installs pages with `vm_insert_page`, and increments per-grant use counts. Deallocation removes grant records from the file list and cleanup frees records whose local users dropped to zero. VMA close decrements use counts and frees grants only when no mappings remain and Xen permits access teardown.

State and persistence: global `gref_list`, `gref_size`, and `gref_mutex` track all live allocations and enforce the module limit. Per-file lists track offsets owned by the file. Optional unmap notification clears a byte and/or sends an event channel when a grant is finally deleted.

Dependencies and integration: depends on Xen grant-table APIs, event-channel refs for notifications, Linux miscdevice, VM insertion, highmem mapping for clear-byte, and userspace ABI in `<xen/gntalloc.h>`.

Risks: remote domains can keep grants mapped so pages remain allocated after userspace exit; offset guessing can race failed user copies as documented in the code; notification event refs must be balanced; global limit cleanup only happens on grant operations; mappings must be shared.

Test signals: allocate/deallocate multiple grants, mmap shared pages, verify readonly/writable grant flags with a peer domain, exercise unmap notification clear-byte and event delivery, close while remote mappings remain, and enforce `limit`.
