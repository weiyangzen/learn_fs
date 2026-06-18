# sources/distributed-fs/openafs/src/afs/HPUX/osi_vcache.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_vcache.c

Purpose: implements HP-UX vcache/vnode allocation and attachment hooks for the portable AFS vcache layer.

Important APIs/types/functions: `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

Control flow: eviction checks that the vcache has no references, no opens, and is not pending unlinked deletion before calling `afs_FlushVCache`. New vnodes are allocated as `struct vcache`. Pre-population zeroes the vcache and initializes `flushDV` to `AFS_MAXDV`. Post-population assigns `afs_ops`, `afs_globalVFS`, and regular-file type. Hold increments the vnode reference.

State/persistence: initializes in-memory vcache/vnode state only. Persistent file state is managed elsewhere.

Dependencies/integration: depends on HP-UX vnode fields, global VFS from `osi_vfsops.c`, OpenAFS vcache state flags, and `afs_ops` from `osi_vnodeops.c`.

Risks/test signals: simplistic `osi_AttachVnode` and default `VREG` type rely on later core AFS setup. Test vcache allocation/reuse, vnode reference counts, root vnode setup, and eviction under open/unlinked/reference states.
