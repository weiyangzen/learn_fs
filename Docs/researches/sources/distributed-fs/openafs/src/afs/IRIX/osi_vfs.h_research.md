# sources/distributed-fs/openafs/src/afs/IRIX/osi_vfs.h

## sources/distributed-fs/openafs/src/afs/IRIX/osi_vfs.h

Purpose: IRIX VFS/vnode compatibility header for OpenAFS, hiding XFS, behavior-descriptor, page-cache, vnode-layout, and directory/lock differences.

Important APIs/types/functions: defines XFS conversion macros (`XFS_VTOI`, `XFS_ITOV`), `xfs_iget` prototype, `VnodeToIno/Dev/Size` prototypes, page operation macros (`PTOSSVP`, `PFLUSHVP`, etc.), VOP wrapper macros (`AFS_VOP_*`), `AFS_VN_OPEN`, vnode dirty/mapped/page-count accessors, flock constants, `afs_fid2_t` for checkpoint restart, and compatibility aliases such as `ucred` to `cred`.

Control flow: macro wrappers optionally prevent behavior insertion around VOP calls when `AFS_SGI_VNODE_GLUE` is enabled, with NUMA-specific behavior. Vnode field accessors select between native vnode layout and `vnode1_t` shim depending on `afs_is_numa_arch`.

State/persistence: no direct state, but macros read/write vnode page-cache fields and behavior heads.

Dependencies/integration: included by most IRIX platform files, especially file, inode, VM, vcache, and vfsops implementations.

Risks/test signals: version/layout shims are fragile; wrong NUMA detection or behavior locking can corrupt vnode state. Test with and without `AFS_SGI_VNODE_GLUE`, NUMA and non-NUMA systems, XFS VOP calls, page flush/invalidate operations, and checkpoint fid vget.
