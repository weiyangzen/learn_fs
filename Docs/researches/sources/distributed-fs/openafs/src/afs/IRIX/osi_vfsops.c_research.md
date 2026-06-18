# sources/distributed-fs/openafs/src/afs/IRIX/osi_vfsops.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_vfsops.c

Purpose: implements IRIX AFS filesystem initialization, VFS operations, syscall hook installation, IDBG hook registration, mount/root/statfs/sync/vget behavior, and MP wrappers.

Important APIs/types/functions: `Afs_init`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, MP wrapper functions, `Afs_vfsops`, and globals `afs_globalVFS`, `afs_globalVp`, `afs_fstype`, `afs_rxlock`, `afs_vfs_bhv`.

Control flow: initialization calls `osi_Init`, records fstype, sets exported operation pointers, installs AFS syscalls (`AFS_SYSCALL`, `AFS_PIOCTL`, `AFS_SETPAG`, inode syscalls), replaces `setgroupsp`, and registers IDBG commands. Mount requires superuser and directory mountpoint, rejects remounts, initializes VFS fsid/type/dev, and inserts a behavior. Unmount flushes all vcaches from `VLRU`, handles the root vnode specially, clears globals, warms shutdown, and removes VFS behavior. Root fetches or reuses `afs_rootFid`. Sync walks active dirty vcaches, obtains nonblocking or blocking rwlocks, flushes/invalidates pages according to sync flags, and restarts if `vcachegen` changes. Vget handles checkpoint fids or delegates to `afs_osi_vget`.

State/persistence: global VFS/root vnode cache, syscall table hooks, setgroups hook, IDBG hooks, VFS behavior state, and AFS fstype are maintained while loaded.

Dependencies/integration: deeply coupled to IRIX VFS behavior APIs, syscall table layout, OpenAFS vcache list/locks, VM page flush macros, credential APIs, and optional SGI vnode glue.

Risks/test signals: risks include unsafe syscall replacement, unmount with referenced/dirty vcaches, sync races while `VLRU` mutates, root vnode reference manipulation, and checkpoint fid conversion. Test mount/unmount under active files, sync flags, dirty mmap flush, syscall dispatch, setgroups PAG preservation, IDBG registration, and CKPT restart fids.
