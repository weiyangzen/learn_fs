# sources/distributed-fs/openafs/src/afs/FBSD/osi_vfsops.c

## Purpose
Implements FreeBSD VFS operations for OpenAFS: module init/uninit, mount, cmount, unmount, root, statfs, sync, syscall registration, and pbuf pool setup.

## Important APIs, Types, And Functions
Key functions are `afs_init`, `afs_uninit`, `afs_statfs`, `afs_omount`, `afs_mount`, `afs_cmount`, `afs_unmount`, `afs_root`, `afs_sync`, and the exported `struct vfsops afs_vfsops`. Globals include `afs_globalVp`, `afs_globalVFS`, `afs_pbuf_zone` or `afs_pbuf_freecnt`, and the `afs_syscalls` helper table.

## Control Flow
Initialization registers `AFS_SYSCALL`, calls `osi_Init`, and creates pbuf resources. Mount rejects updates and existing global mounts, records `afs_globalVFS`, sets block size/fsid/mount names, marks the mount non-local/MPSAFE as needed, and fills statfs. Root duplicates the current credential, obtains or reuses `afs_globalVp`, handles races while replacing the global root, drops the global lock around `vget`, revalidates the global root after lock reacquisition, marks `VV_ROOT`, and returns the vnode. Unmount drops the root vcache if forced or unreferenced, flushes remaining vnodes, clears `afs_globalVFS`, and performs warm shutdown.

## State And Persistence
Persistent state includes the singleton global mount, cached root vcache, registered syscall helper, pbuf resources, and fake statfs values. Root vnode references intentionally persist until unmount.

## Dependencies And Integration Points
Depends on FreeBSD VFS/module/syscall helper APIs, OpenAFS initialization/shutdown, root fid lookup, vcache/vnode lifecycle, pbuf allocation used by vnode operations, and `osi_module.c` registration.

## Risks
Singleton mount assumptions reject multiple mounts. Root acquisition deliberately drops locks and must revalidate to avoid races. Uninit must refuse while mounted. Version guards around `vget`, syscall helper registration, and pbuf allocation are ABI-sensitive.

## Test Signals
Module load/unload, syscall registration conflict, mount/remount rejection, root lookup races, statfs contents, forced and normal unmount, warm shutdown, and pbuf resource cleanup should all be exercised.
