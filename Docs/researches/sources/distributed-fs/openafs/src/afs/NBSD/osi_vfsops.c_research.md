## sources/distributed-fs/openafs/src/afs/NBSD/osi_vfsops.c

Purpose: NetBSD VFS operations, mount/root/unmount/statfs lifecycle, pathname lookup wrapper, and legacy LKM registration for OpenAFS.

Important APIs and state: defines `afs_vfsops`, `afs_nbsd_lookupname`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_statvfs`, `afs_sync`, `afs_init`, `afs_reinit`, `afs_done`, and older `libafs_lkmentry`/LKM load-unload helpers. Globals include `afs_globalVFS`, `afs_globalVp`, and `afs_dynamic_fsid`. For older NetBSD it also defines `afs_sysent`, `old_sysent`, `old_setgroups`, and `lkmid`.

Control flow: `afs_nbsd_lookupname` builds a NetBSD `nameidata`/`pathbuf` according to kernel version, calls `namei`, and returns the leaf vnode. `afs_mount` rejects updates and multiple mounts, initializes disconnected vcaches when enabled, records the mount globally, populates mount stat fields and names, obtains a new fsid, and calls `afs_statvfs`. `afs_unmount` gives up callbacks for disconnected mode, releases global root vnode, flushes vnodes with `vflush`, clears globals, calls `afs_shutdown(AFS_COLD)`, clears `mnt_data`, and logs unmount. `afs_root` loops until it has a stable `afs_globalVp`, initializes request/checks AFS, fetches root vcache, refs and locks vnode, sets `VV_ROOT`, updates global VFS, and returns it. `afs_statvfs` reports fake capacity. `afs_sync` stores dirty vcaches when disconnected mode is enabled. Legacy LKM load patches `AFS_SYSCALL` and `SYS_setgroups`; unload restores them.

Dependencies and integration: depends on NetBSD VFS/vnode/namei APIs, OpenAFS root fid/cache initialization, disconnected-mode helpers, common shutdown, syscall handlers, and vnode operation descriptors. Modern module attachment is handled in `osi_kmod.c`, while this file still contains older LKM support for non-NetBSD-6 builds.

State and persistence: maintains one live AFS mount in kernel globals and reports fake filesystem capacity. Shutdown affects in-memory AFS client state and local cache lifecycle via common shutdown.

Risks: `afs_root` has delicate races around `afs_globalVp`, vnode locking, and stale root vcaches. `vflush` does not support forced unmount here. Multiple mount rejection is global. The code checks `VOP_ISLOCKED(*vpp)` before `*vpp` is assigned, which is suspicious and should be validated in the target NetBSD API context. Legacy syscall patching has the same restore risks as other syscall-hook code.

Test signals: mount/update/remount rejection, root lookup under callback/root-volume change, unmount with active vnodes, statvfs values, disconnected dirty sync, name lookup for user/system paths, modern module vs legacy LKM builds, and load/unload syscall restoration.
