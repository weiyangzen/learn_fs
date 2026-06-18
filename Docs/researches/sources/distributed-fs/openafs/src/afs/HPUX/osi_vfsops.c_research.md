# sources/distributed-fs/openafs/src/afs/HPUX/osi_vfsops.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_vfsops.c

Purpose: implements HP-UX VFS operations and module/syscall registration for mounting AFS.

Important APIs/types/functions: `afs_mount`, `afs_unmount`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, `afs_getmount`, `Afs_vfsops`, `osi_InitGlock`, `afs_load`, and `afsc_link`. It defines `afs_globalVFS`, `afs_globalVp`, `afs_mountpath`, `afs_global_sema`, and `afs_vfs_slot`.

Control flow: mount rejects remounts, initializes VFS block size/fsid/name, stores mount path, and initializes translator support. Unmount clears global VFS and calls warm shutdown. Root reuses a cached statted root vcache or fetches `afs_rootFid`, holds and marks it `VROOT`, and returns the vnode. Statfs returns fake free space. Vget initializes an AFS request and delegates to `afs_osi_vget`. `afsc_link` initializes OSI, registers VFS type, installs `Afs_syscall`, and replaces system `setgroups` with `Afs_xsetgroups`.

State/persistence: keeps global mount/root vnode pointers and mount path. Global lock semaphore state persists while the module is loaded.

Dependencies/integration: depends on HP-UX VFS registration, dynamic kernel module structures for 11.23, syscall table patching, OpenAFS root fid/cache init, and optional non-filesystem translator.

Risks/test signals: risks include global single-mount assumptions, syscall replacement safety, stale root vcache, unmount with references, and glock initialization race. Test mount/unmount/remount, root lookup, statfs, NFS translator setup, syscall dispatch, and setgroups interception.
