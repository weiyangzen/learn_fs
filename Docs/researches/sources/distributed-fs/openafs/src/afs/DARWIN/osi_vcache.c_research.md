# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vcache.c

## Purpose
Provides Darwin vcache allocation, vnode attachment, eviction, and hold helpers for OpenAFS.

## Important APIs, Types, And Functions
`osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, `osi_TryEvictVCache`, and `osi_vnhold` implement the platform vcache lifecycle.

## Control Flow
Allocation creates a zeroable `struct vcache` and clears `v`. Pre-populate zeros the structure. Attach drops the vcache lock and AFS global lock, calls `afs_darwin_getnewvnode`, reacquires locks, and initializes the per-vcache vnode lock. Post-populate sets mount/type defaults, using `VNON` on modern Darwin until finalization. Eviction recycles vnodes with no visible refs/opens/unlinked-delete state, dropping global locks around `vnode_recycle` or `vgone`.

## State And Persistence
State lives in `vcache->v`, per-vcache `rwlock`, vnode refs/iocounts, `CUnlinkedDel`, and Darwin vnode lifecycle flags such as `CDeadVnode`.

## Dependencies And Integration Points
Depends on `osi_vnodeops.c` for `afs_darwin_getnewvnode`, Darwin vnode recycling APIs, global `afs_xvcache`, and generic OpenAFS vcache allocation/population code.

## Risks
Eviction correctness depends on distinguishing usecounts from iocounts. Dropping and reacquiring locks during vnode allocation/recycle creates races that are mitigated by rechecking `avc->v`. Incorrect initial vnode type can expose incomplete vnodes to VFS.

## Test Signals
Stress vcache creation/reuse/reclaim, lookup races, unlinked file deletion, vnode recycling under memory pressure, and shutdown. Lockdep/assertion failures around `afs_xvcache` are important signals.
