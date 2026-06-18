# sources/distributed-fs/openafs/src/afs/HPUX/osi_vnodeops.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_vnodeops.c

Purpose: implements the HP-UX vnode operation table, file operations, VM pagein/pageout glue, ioctl/readdir conversion, and per-thread semaphore-save hash needed by the AFS global lock.

Important APIs/types/functions: `Afs_vnodeops`, `afs_fileops`, `afs_lockf`, `afs_bread`, `afs_brelse`, `afs_bmap`, `afs_inactive`, many `mp_afs_*` wrappers, `afs_pagein`, `afs_pageout`, `afs_mapdbd`, `afs_vm_checkpage`, `afs_hp_strategy`, `afs_pathconf`, `afs_readdir`, `afs_readdir3`, and hash functions `afsHash`, `afsHashInsertFind`, `afsHashFind`, `afsHashRelease`. Vnode wrappers call core AFS operations under `AFS_GLOCK`.

Control flow: standard vnode operations are thin MP-safe wrappers around `afs_open`, `afs_close`, `afs_rdwr`, lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink/fsync/lock/fid. Buffer read uses fake buffers for RFS/NFS translator behavior. `afs_pagein` initializes HP-UX VM fault info, verifies EOF, reserves memory, expands I/O ranges, flushes overlapping blocks, issues `syncpageio`, handles holes for writable mappings, marks DBDs, and returns page counts or SIGBUS. `afs_pageout` scans dirty page ranges, builds buffers, protects pages, flushes stale buffers, writes with `asyncpageio`, handles vhand credential substitution, and updates VM stats. `afs_hp_strategy` maps buffers to kernel space and calls `afs_rdwr`.

State/persistence: vnode ops mutate AFS cache/server-visible state via generic AFS calls. VM operations persist dirty mapped pages back to AFS through strategy/pageout paths. The semaphore hash stores per-thread saved `sv_sema_t` state for global-lock release/reacquire across call chains.

Dependencies/integration: deeply coupled to HP-UX VM internals (`vfspage_t`, DBD/VFD, regions, pregions), buffer cache, vnodeops layout, syscall/fileops, OpenAFS global lock, and version-specific HP-UX 11 headers.

Risks/test signals: very high risk from VM empire locking, pageout credentials, fake buffer lifetime, directory entry conversion sizing, semaphore hash leaks/races, and version-dependent vnodeops slots. Test mmap read/write/page faults, pageout under memory pressure, ENOSPC write accounting, directory listings in 32/64-bit callers, lockf translation, NFS translator paths, and multi-threaded global-lock nesting.
