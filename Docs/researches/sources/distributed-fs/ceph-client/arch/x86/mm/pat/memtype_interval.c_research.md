# sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype_interval.c

## Purpose
This file provides the interval-tree backend for non-RAM PAT memory-type reservations. It stores physical ranges, detects cache-type conflicts among overlapping aliases, supports exact removal, lookup, and debugfs iteration.

## Important APIs, Types, and Functions
- `INTERVAL_TREE_DEFINE()` creates the augmented rb-tree operations for `struct memtype`.
- `memtype_check_insert()` validates overlap compatibility and inserts a new reservation.
- `memtype_erase()` removes an exact `[start,end)` reservation.
- `memtype_lookup()` finds a reservation overlapping a page-sized address range.
- `memtype_copy_nth_element()` copies the nth reservation for debugfs iteration.

## Control Flow and State
The static `memtype_rbroot` stores all interval entries. Conflict checking finds the first overlap, allows success with no overlap, fails when `newtype == NULL` and a different type overlaps, or adopts the first overlapping type and requires all other overlaps to match it. Insert updates `entry_new->type` to the compatible type when requested. Erase scans overlaps until it finds an exact start/end match.

## Dependencies and Integration Points
The tree is protected externally by `memtype_lock` in `memtype.c`. It depends on Linux's generic interval tree macros and the `struct memtype` layout from `memtype.h`. Debugfs list printing uses `memtype_copy_nth_element()`.

## Risks
Overlaps with inconsistent cache types must fail to prevent CPU cache corruption. Exact-endpoint removal means callers must free the same range they reserved. The debugfs nth-element scan is O(n) and safe only because callers copy while holding the lock briefly.

## Test Signals
PAT debug logs should show overlap handling. Tests should include non-overlapping insert, overlapping same-type insert, overlapping type adoption through `newtype`, conflicting insert failure, exact erase, invalid erase, lookup hits/misses, and debugfs iteration.
