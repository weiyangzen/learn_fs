# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-bufmap.c

## Purpose
`pvfs2-bufmap.c` implements the OrangeFS/PVFS2 shared-memory buffer map used to move file I/O data between VFS callers in the kernel and the user-space `pvfs2-client-core` daemon. The daemon passes a page-aligned userspace region through `PVFS_DEV_MAP`; this file pins those pages, slices them into descriptors, hands descriptor indices to file and directory paths, and provides copy helpers between mapped pages, user iovecs, kernel buffers, and page-cache pages.

## Important APIs, types, and functions
The public API exported through `pvfs2-bufmap.h` includes `pvfs_bufmap_initialize`, `pvfs_bufmap_finalize`, `pvfs_bufmap_get`, `pvfs_bufmap_put`, `readdir_index_get`, `readdir_index_put`, descriptor size queries, and the copy helpers. `struct slot_args` is a local adapter that lets normal I/O descriptors and fixed readdir descriptor indices use the same wait-and-claim logic. Global state includes descriptor sizing, `bufmap_init`, `bufmap_page_array`, `buffer_index_array`, `readdir_index_array`, `desc_array`, and wait queues for initialization and slot availability.

## Control flow
Initialization validates alignment, total size, descriptor size, and descriptor count from `struct PVFS_dev_map_desc`, allocates descriptor tracking arrays, pins user pages with `get_user_pages`, marks or flushes each page as needed, constructs `desc_array`, clears all descriptor usage bits, sets `bufmap_init`, and wakes callers blocked on `pvfs2_bufmap_init_waitq`. Finalization reverses this by clearing reserved status, releasing pinned pages, freeing arrays, and dropping `bufmap_init`.

`pvfs_bufmap_get` and `readdir_index_get` both call `wait_for_a_slot`. That function holds a read lock on `bufmap_init_sem`, scans the relevant slot bitmap under a spinlock, sleeps on an exclusive waitqueue entry when full, times out based on `slot_timeout_secs`, and returns `-EINTR` on signal. The copy helpers take the init read semaphore, then kmap one page at a time so highmem systems do not require permanently mapped pages.

## State and persistence behavior
All state is in-memory kernel module state tied to a live daemon mapping. There is no disk persistence. Descriptor usage is represented by integer arrays protected by spinlocks. Pinned pages persist until `pvfs_bufmap_finalize`, normally invoked when `/dev/pvfs2-req` closes. `pvfs_bufmap_size_query` and `pvfs_bufmap_shift_query` provide block-size signals to inode/superblock setup.

## Dependencies and integration points
This file depends on `pvfs2-kernel.h` for locking, timeouts, debug, kernel-version wrappers, and page helpers; on `pint-dev-shared.h` for the device map descriptor; and on `pvfs2-bufmap.h` for declarations. `devpvfs2-req.c` initializes/finalizes the map from device ioctls and close. `file.c` uses the descriptor copy helpers for read/write staging. `dir.c` uses the readdir index pool. `super.c` and inode setup query descriptor size for VFS block sizing.

## Risks and edge cases
Copy routines assume callers keep `size` within the descriptor capacity; most functions do not explicitly bound `buffer_index` or total bytes against `desc_array[buffer_index].array_count`. `get_bufmap_init` returns `0` both when uninitialized and when it cannot acquire the read semaphore, so callers must not treat it as a stable state transition. `pvfs_bufmap_initialize` failure after `bufmap_page_array` allocation may leave that array freed locally but not reset in all paths before descriptor cleanup. Long `slot_timeout_secs` values can make descriptor exhaustion look like a hang. AIO task-iovec copying maps remote task pages and then calls `copy_to_user` on a kmap address, a fragile kernel-version-sensitive path.

## Test signals
Useful tests exercise daemon restart with outstanding I/O, `PVFS_DEV_MAP` alignment/size failures, descriptor exhaustion and wakeup, signal interruption, timeout behavior, reads/writes spanning multiple pages, iovecs that split exactly on page boundaries, readdir descriptor reuse, and cleanup after daemon close. Kernel debug class `GOSSIP_BUFMAP_DEBUG` should show slot waits, descriptor acquisition, and copy failures.
