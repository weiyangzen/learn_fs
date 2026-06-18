# sources/distributed-fs/openafs/src/afs/FBSD/osi_vcache.c

## Purpose
Implements FreeBSD vcache allocation, vnode attachment, eviction, post-population, and safe vnode holds for OpenAFS.

## Important APIs, Types, And Functions
Exports `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and version-dependent `osi_vnhold`.

## Control Flow
Eviction tries to lock the vnode interlock, checks in-use state, skips doomed vnodes as already evicted, holds the vnode, drops AFS locks, attempts nonblocking exclusive `vn_lock`, calls `vrecycle`, unlocks/drops, then restores AFS locks. Attach drops AFS locks, calls `getnewvnode`, inserts into the mount queue if needed, restores locks, handles rare races where another thread already attached a vnode, assigns `v_data`, and initializes the vcache lock.

## State And Persistence
State lives in `vcache->v`, vnode `v_data`, vnode mount queue membership, per-vcache `rwlock`, and vnode hold/reference counts.

## Dependencies And Integration Points
Depends on FreeBSD vnode lifecycle APIs, `afs_globalVFS`, `afs_vnodeops`, `osi_fbsd_checkinuse`, `afs_xvcache`, and generic OpenAFS vcache management.

## Risks
Reference and interlock ordering around `vrecycle` is delicate. `osi_AttachVnode` documents a possible race if `avc->v` becomes non-null while locks were dropped. Version-specific `vref`/`vrefl` handling must avoid holding doomed vnodes.

## Test Signals
Stress vcache creation and reclamation under memory pressure, vnode recycle races, mount queue insertion, `AFS_IS_DOOMED` paths, and `osi_vnhold` on active and doomed vnodes.
