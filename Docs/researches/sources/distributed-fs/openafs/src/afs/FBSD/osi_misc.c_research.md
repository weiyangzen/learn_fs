# sources/distributed-fs/openafs/src/afs/FBSD/osi_misc.c

## Purpose
Provides FreeBSD miscellaneous helpers for path lookup, kernel allocation, freeing, and vcache in-use checks.

## Important APIs, Types, And Functions
Exports `osi_lookupname`, `osi_fbsd_alloc`, `osi_fbsd_free`, and `osi_fbsd_checkinuse`.

## Control Flow
`osi_lookupname` drops the AFS global lock if held, builds a FreeBSD `nameidata` lookup with follow/no-follow flags, calls `namei`, returns the vnode, frees pathname buffers, and restores the global lock. Allocation optionally drops the global lock for blocking `malloc(M_WAITOK)` or uses nonblocking `M_NOWAIT`. `osi_fbsd_checkinuse` requires the vnode interlock, rejects vcaches with vnode usecount, opens, or held AFS locks.

## State And Persistence
No local persistent state; allocations use the `M_AFS` malloc type defined in `osi_module.c`. The in-use check observes vnode and vcache state.

## Dependencies And Integration Points
Depends on FreeBSD `namei`, malloc, vnode interlocks, OpenAFS global lock, and vcache recycling code in `osi_vcache.c`/`osi_vm.c`.

## Risks
Path lookup returns a referenced vnode and relies on callers to release it. Dropping the global lock around namei/allocation opens races that callers must tolerate. `osi_fbsd_checkinuse` enforces strict recycling conditions; stale `opens` counts can prevent reclamation.

## Test Signals
Lookup existing/missing paths with both follow modes, allocation under memory pressure, vcache recycle checks with active refs/opens/locks, and lock assertion coverage.
