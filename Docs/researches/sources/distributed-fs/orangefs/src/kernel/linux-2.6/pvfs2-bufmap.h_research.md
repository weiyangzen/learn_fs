# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.h

## Purpose
`pvfs2-bufmap.h` declares the kernel-side shared-memory buffer map contract used by OrangeFS I/O and directory paths. It exposes the descriptor layout and the operations that initialize the daemon-provided map, reserve descriptor indices, release them, and copy data between mapped pages and VFS/user buffers.

## Important APIs and types
`struct pvfs_bufmap_desc` stores the userspace base address, the array of pinned `struct page *`, a page count, and an unused list hook. The core lifecycle calls are `pvfs_bufmap_initialize`, `get_bufmap_init`, and `pvfs_bufmap_finalize`. Slot management is split between `pvfs_bufmap_get`/`pvfs_bufmap_put` for normal I/O and `readdir_index_get`/`readdir_index_put` for directory operations. Copy APIs cover user buffers, kernel buffers, user iovecs, kernel iovecs, page-cache pages, and AIO completion into another task when `HAVE_AIO_VFS_SUPPORT` is enabled.

## Control flow and integration
The header is included by `pvfs2-bufmap.c`, file I/O code, directory code, inode/superblock setup, and device request handling. Callers normally reserve a descriptor, copy write data into the mapped descriptor or receive read data from it, send an upcall to the daemon that references the descriptor index, wait for a downcall, and then release the descriptor.

## State and persistence behavior
The header itself has no state, but it exposes routines over module-global bufmap state in `pvfs2-bufmap.c`. That state is per-loaded-module and per-active-client mapping rather than persistent storage.

## Dependencies
The header depends on `pint-dev-shared.h` for `struct PVFS_dev_map_desc` and on kernel types already included by `pvfs2-kernel.h` in most users. The `__user`, `struct iovec`, `struct page`, and `struct task_struct` types reflect tight coupling to Linux VFS and memory-management APIs.

## Risks and test signals
The API accepts raw descriptor indices and byte sizes, so correctness depends on callers validating indices, sizes, and release-on-error paths. Test signals should include every declared copy direction, zero-length and page-boundary iovec cases, missing daemon mapping behavior, AIO-only build coverage, and lockstep `get`/`put` accounting under concurrent I/O.
