# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_prototypes.h

## Purpose

`osi_prototypes.h` declares exported UKERNEL OSI support functions for VFS and vnode operations.

## Important APIs, Types, and Functions

It declares VFS routines from `osi_vfsops.c`: `afs_statvfs`, `afs_mount`, `afs_unmount`, `afs_root`, `afs_sync`, `afs_statfs`, `afs_mountroot`, and `afs_swapvp`. It declares vnode glue from `osi_vnodeops.c`: `afs_vrdwr` and `afs_inactive`.

## Control Flow

No runtime behavior exists in this header. Its layout mirrors the implementing files and allows common OpenAFS code to call these user-space OSI functions.

## State and Persistence Behavior

No state is defined. Implementations manipulate `afs_globalVFS`, `afs_globalVp`, vnode references, and cache-manager state.

## Dependencies and Integration Points

It depends on UKERNEL types such as `struct vfs`, `struct vnode`, `struct usr_uio`, `struct vcache`, and `afs_ucred_t`, defined through `sysincludes.h` and `osi_machdep.h`.

## Risks and Edge Cases

Prototype drift is the main risk, especially because many VNOP signatures vary by platform. Any mismatch can compile on one platform and fail on another.

## Test Signals

Compile UKERNEL with strict prototypes enabled and ensure every declaration matches its implementation. Link tests should reference each declared function.
