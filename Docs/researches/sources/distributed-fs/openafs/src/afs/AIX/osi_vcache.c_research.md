# sources/distributed-fs/openafs/src/afs/AIX/osi_vcache.c

Purpose: AIX-specific vcache/vnode allocation, population, attachment, eviction, and hold support.

Important APIs and functions: `osi_TryEvictVCache` flushes eligible vcaches; `osi_NewVnode` allocates and optionally pins a `struct vcache`; `osi_PrePopulateVCache` clears it and allocates a companion `gnode`; `osi_AttachVnode` is a no-op hook; `osi_PostPopulateVCache` wires vnode ops, vfs, type, vfs list links, and gnode backpointer; `osi_vnhold` calls `VN_HOLD`.

Control flow: vcache allocation and population are staged so common code can fill AFS fields between pre/post hooks. Eviction requires zero references, no opens, and not `CUnlinkedDel`, then delegates to `afs_FlushVCache`.

State and persistence: mutates in-memory vcache, vnode, gnode, and `afs_globalVFS->vfs_vnodes` list membership. No disk state.

Dependencies and integration: uses `afs_ops` from AIX vnode operations, `afs_globalVFS` from `osi_vfsops.c`, and AIX pinning where available.

Risks and test signals: list insertion must be balanced by `aix_gnode_rele`; allocation failures return NULL. Signals include stable vnode lookup/reclamation and no corrupted vfs vnode chain.
