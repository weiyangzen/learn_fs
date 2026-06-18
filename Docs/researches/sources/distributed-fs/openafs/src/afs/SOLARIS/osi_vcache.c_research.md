# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vcache.c

## Purpose
Solaris vcache and vnode lifecycle helpers, including eviction, allocation, initialization, attachment, and hold semantics.

## Important APIs, Types, and Functions
Defines `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

## Control Flow
Eviction calls `afs_FlushVCache` only when vnode refs are zero, no opens exist, and the file is not in unlinked-delete state. Pre-population clears the vcache, initializes `multiPage`, vcache locks, and pre-Solaris-11 `v_data`. Solaris 11 attachment allocates a vnode with `vn_alloc`. Post-populate assigns vnode ops, VFS, regular type, and holds the VFS. `osi_vnhold` increments `v_count` and holds the VFS when transitioning from zero.

## State and Persistence
Manages in-memory vcache, vnode, locks, multipage queue, vnode refcount, and VFS refcount. No disk persistence.

## Dependencies and Integration Points
Depends on Solaris vnode allocation, `afs_ops` from vnodeops registration, `afs_globalVFS`, and VM multi-page conflict logic in `osi_vm.c`/`osi_vnodeops.c`.

## Risks
VFS holds must match vnode refs or unmount will hang/leak. Pre-Solaris-11 `v_data` workaround for KAIO is fragile. Eviction depends on exact ref/open counts and `afs_FlushVCache` behavior.

## Test Signals
Vcache allocation/population, vnode refcount zero-to-one transitions, unmount with root vnode release, cache eviction under pressure, and Solaris 11 `vn_alloc` path.
