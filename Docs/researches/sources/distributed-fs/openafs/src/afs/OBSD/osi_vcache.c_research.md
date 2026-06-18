# sources/distributed-fs/openafs/src/afs/OBSD/osi_vcache.c

## Purpose
OpenBSD vcache allocation, vnode attachment, vnode hold, and eviction helpers.

## Important APIs, Types, and Functions
Defines `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

## Control Flow
Eviction checks zero vnode refs, no opens, and not `CUnlinkedDel`; then drops GLOCK and calls `vgone`, causing vnode reclaim and `afs_FlushVCache`. Allocation creates a zero-prepared `struct vcache`. Attachment temporarily releases `afs_xvcache` and GLOCK to call `afs_obsd_getnewvnode`, then re-acquires and initializes the vcache rwlock. Post-populate sets mount and regular-file type.

## State and Persistence
Manages in-memory `struct vcache` and its associated `struct vnode`. No disk persistence.

## Dependencies and Integration Points
Depends on OpenBSD vnode lifecycle (`vgone`, `getnewvnode`, `vget`) and `afs_xvcache`. Works with `OBSD/osi_vfsops.c` for vnode allocation and `OBSD/osi_vnodeops.c` for reclaim.

## Risks
Dropping global/vcache locks during vnode allocation permits races, so `seq` and higher-level cache population must guard reuse. Eviction relies on accurate ref/open counts.

## Test Signals
Cache pressure eviction, vnode creation/reclaim, root vnode holds, unlinked-open file behavior, and lock-order diagnostics around `osi_AttachVnode`.
