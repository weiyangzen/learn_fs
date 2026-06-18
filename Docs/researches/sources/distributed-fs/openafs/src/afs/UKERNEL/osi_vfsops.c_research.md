# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vfsops.c

## Purpose

`osi_vfsops.c` provides the UKERNEL VFS operation table and mount/root/statfs shims for the user-space AFS filesystem.

## Important APIs, Types, and Functions

`Afs_vfsops` maps mount, unmount, root, statfs, and sync operations. Global state includes `afs_globalVFS`, `afs_globalVp`, and `afs_rootCellIndex`. Functions are `afs_mount`, `afs_unmount`, `afs_root`, `afs_sync`, `afs_statfs`, `afs_statvfs`, `afs_mountroot`, and `afs_swapvp`.

## Control Flow

`afs_mount` rejects remounts by returning `EBUSY` through `setuerror`, sets VFS block size, and installs AFS magic fsid values. `afs_root` reuses `afs_globalVp` if statted, otherwise initializes a request, checks cache-manager init, fetches the root vcache from `afs_rootFid`, holds it, marks it `VROOT`, and returns its vnode. `afs_unmount` clears the global VFS and calls `afs_shutdown(AFS_WARM)`.

## State and Persistence Behavior

Mount state is process-global and in-memory. The root vcache is deliberately retained in `afs_globalVp`. `statfs`/`statvfs` return synthetic capacity and filesystem identity values rather than querying a backing store.

## Dependencies and Integration Points

The file depends on request creation, `afs_CheckInit`, `afs_GetVCache`, `afs_PutVCache`, `afs_shutdown`, tracing, and UKERNEL VFS/vnode types. It is called by `uafs_mount` and `uafs_statvfs`.

## Risks and Edge Cases

Only one mount is supported. `afs_unmount` does not inspect outstanding vnodes or file descriptors. `afs_statvfs` returns fake free-space values, so applications should not treat them as authoritative quota data.

## Test Signals

Test successful mount/root/statvfs/unmount, remount rejection, root vnode reuse, warm shutdown invocation, and behavior when `afs_CheckInit` or root vcache fetch fails.
