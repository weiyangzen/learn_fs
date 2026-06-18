# sources/distributed-fs/ceph-client/fs/xfs/scrub/quota.h

## Purpose
`quota.h` exposes the shared quota scrub helper needed by quota repair.

## Important APIs, Types, And Functions
The file declares `xchk_quota_to_dqtype(struct xfs_scrub *sc)`, which converts scrub operation types into `xfs_dqtype_t`.

## Control Flow
There is no internal control flow. Callers use the helper before quota scrub or repair to choose user, group, or project quota metadata.

## State And Persistence Behavior
No state is stored or persisted.

## Dependencies And Integration Points
It depends on `struct xfs_scrub` and quota type definitions. `quota.c` implements the helper, and `quota_repair.c` reuses it.

## Risks And Edge Cases
Callers must handle a zero return as invalid scrub type. There is no compile-time enforcement that only quota scrub types call it.

## Test Signals
Basic coverage should verify all three quota scrub types and the invalid default case.
