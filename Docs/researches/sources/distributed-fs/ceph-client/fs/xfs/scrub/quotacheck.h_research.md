# sources/distributed-fs/ceph-client/fs/xfs/scrub/quotacheck.h

## Purpose
`quotacheck.h` defines shared live quotacheck state and counter records for scrub and repair.

## Important APIs, Types, And Functions
`struct xqcheck_dquot` stores observed block, inode, and realtime block counts plus record flags. Flags are `XQCHECK_DQUOT_WRITTEN`, `XQCHECK_DQUOT_COMPARE_SCANNED`, and `XQCHECK_DQUOT_REPAIR_SCANNED`. `struct xqcheck` owns scrub context, per-type `xfarray` counters, a mutex, an inode scan, quota hooks, and the shadow transaction rhashtable. `xqcheck_counters_for` maps a dquot type to the matching counter array.

## Control Flow
The header has no standalone flow. Scrub initializes and fills the structure, comparison marks records scanned, and repair marks records repaired while committing counters.

## State And Persistence Behavior
State is volatile and shared across scrub-to-repair for a single operation. The flags prevent uninitialized records from being mistaken for real zero counters and allow second passes to find unvisited observations.

## Dependencies And Integration Points
It depends on XFS quota types, `xfarray`, `xchk_iscan`, quota transaction hooks, and Linux rhashtable. It is consumed by `quotacheck.c` and `quotacheck_repair.c`.

## Risks And Edge Cases
`xqcheck_counters_for` asserts on invalid dquot types and returns NULL, so callers must validate types. Repair depends on the scrub phase leaving complete, current observations.

## Test Signals
Compile and runtime coverage should verify all quota-type mappings, record flag transitions through compare and repair passes, and behavior with only one quota type enabled.
