# sources/distributed-fs/openafs/src/afs/OBSD/osi_vfsops.c

## Purpose
OpenBSD VFS and loadable-kernel-module glue for mounting AFS, obtaining the root vnode, registering syscalls, and loading/unloading vnode/VFS operations.

## Important APIs, Types, and Functions
Defines `afs_vfsops`, `afs_obsd_lookupname`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, `afsinit`, `afs_vfs_load`, `afs_vfs_unload`, and `libafs_lkmentry`. Also provides unsupported `quotactl`, `sysctl`, export, and file-handle conversion stubs.

## Control Flow
Mount rejects updates and remounts, sets global VFS and statfs fields, and returns fake capacity. Root initializes an AFS request, checks CM init, fetches `afs_rootFid`, holds it as `afs_globalVp`, sets `VROOT`, and returns it locked. Unmount rejects busy vnodes, releases the global root, flushes, runs cold shutdown, and restores stolen syscall entries. Module load registers vnode ops and memory type names; unload refuses while AFS is active and restores syscall state.

## State and Persistence
Global kernel state includes `afs_globalVFS`, `afs_globalVp`, `lkmid`, `old_sysent`, VFS config, memory type names, and modified `sysent` entries. Persistent filesystem state is remote AFS, not local here.

## Dependencies and Integration Points
Depends on OpenBSD VFS/LKM/namei/syscall internals, common AFS init/shutdown, `afs3_syscall`, `afs_xioctl`, `Afs_xsetgroups`, and vnode ops from `OBSD/osi_vnodeops.c`.

## Risks
Patching syscall tables is invasive and must be restored exactly. Unmount busy checks only v_usecount and does not support forced unmount. Root vnode over-holding is controlled by compile-time behavior. VFS API drift is high risk.

## Test Signals
Load/unload cycles, mount/remount rejection, root lookup, statfs values, busy unmount, syscall interception/restoration, and module unload refusal while root vnode or ioctl hook is active.
