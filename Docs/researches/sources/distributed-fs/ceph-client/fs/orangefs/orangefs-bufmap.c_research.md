## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-bufmap.c

### Purpose
This file manages the shared userspace buffer map used for OrangeFS file I/O and the separate slot map used for readdir operations.

### Important APIs, types, and functions
- `struct slot_map` tracks available slots with a bitmap, count, and waitqueue.
- Slot helpers `install()`, `mark_killed()`, `run_down()`, `get()`, and `put()` manage map lifecycle and blocking slot acquisition.
- `struct orangefs_bufmap_desc` records the userspace address and grouped folios for each descriptor.
- `orangefs_bufmap_initialize()` validates daemon-provided mapping parameters, pins user pages, groups them into folios, builds descriptor mappings, publishes the global map, and installs slot maps.
- `orangefs_bufmap_finalize()` and `orangefs_bufmap_run_down()` kill, drain, unpin, and free the map.
- `orangefs_bufmap_get()`, `orangefs_bufmap_put()`, `orangefs_readdir_index_get()`, and `orangefs_readdir_index_put()` allocate/release slots.
- `orangefs_bufmap_copy_from_iovec()` and `orangefs_bufmap_copy_to_iovec()` copy between iov_iter data and mapped folios, with a fast path for two 2 MiB folios.

### Control flow
The daemon maps a page-aligned shared memory region through `ORANGEFS_DEV_MAP`. Initialization validates total size, descriptor size/count consistency, page divisibility, and alignment, then pins pages with `pin_user_pages_fast(FOLL_WRITE)`. It groups consecutive pages by folio and assigns enough folios to each descriptor. File I/O gets a free slot, copies data into or out of the descriptor, and returns the slot. Device release marks maps killed, wakes waiters, waits for outstanding slots to return, then unpins and frees all structures.

### State and persistence behavior
The global `__orangefs_bufmap` is runtime state tied to the daemon process lifetime. Pinned user pages are not persistent storage, but they are the transport for persistent file data between kernel and userspace daemon. Slot waiters use configurable `slot_timeout_secs` and a shorter wait while the map is not installed.

### Dependencies and integration points
Used by `file.c` for read/write data transfer, `dir.c` for readdir slot indexes, and `devorangefs-req.c` for map setup/teardown. Depends on GUP, folios, bitmaps, waitqueues, and protocol `ORANGEFS_dev_map_desc`.

### Risks
Pinned user memory lifetime is sensitive: unpin must happen after all users release slots. The code allows degraded folio layouts but has a special fast path for a two-THP descriptor; both paths need identical correctness. `orangefs_bufmap_size_query()` can return 0 before mapping, affecting I/O chunking if callers do not handle daemon-not-ready states. Timeout and signal behavior in slot waits is observable by file I/O.

### Test signals
Test mapping validation, partial pin failure rollback, daemon exit while slots are held, slot timeout and interrupt paths, highmem/folio layouts, fast path and generic copy path, large I/O chunking, and readdir slot exhaustion.
