# sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.c

## Purpose

`lockprocs.c` provides helper routines for locating and editing VLDB server/partition entries and for managing a small linked-list queue used by VOS volume-operation code. Despite the filename, the file does not acquire pthread or OS locks; it manipulates VLDB entry fields and queue structures.

## Important APIs, Types, and Functions

The central helper is `FindIndex`, which searches an `nvldbentry` for a matching server, partition, and volume type flag. `SetAValue` updates or removes a matching entry. Exported wrappers include `Lp_SetRWValue`, `Lp_SetROValue`, `Lp_Match`, `Lp_ROMatch`, and `Lp_GetRwIndex`.

Queue helpers are `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, and `Lp_QEnumerate`, operating on `struct qHead` and `struct aqueue` from volserver lockdata headers.

## Control Flow

`FindIndex` iterates over VLDB server slots. It uses `VLDB_IsSameAddrs` to account for multihomed/equivalent server addresses. For RW lookups it returns early after failing a matching RW slot, based on the invariant that a VLDB entry has only one RW site. `SetAValue` calls `FindIndex`, writes the new server/partition, and if the new server and partition are both zero, shifts later entries left to remove the site.

The queue functions implement a simple push-front list. `Lp_QEnumerate` pops the head, copies fixed fields into a caller-supplied element, frees the stored node, and reports success.

## State and Persistence Behavior

The VLDB helpers mutate only the in-memory `nvldbentry` passed by the caller; persistence occurs only if the caller later writes the entry back to the VLDB. Queue helpers allocate no memory themselves, but `Lp_QEnumerate` frees queue nodes that were previously allocated by callers.

## Dependencies and Integration Points

The file includes `lockprocs.h`, which pulls in VLDB, volserver, RX, fsint, util admin, admin internals, and `vosutils.h`. `FindIndex` depends on `VLDB_IsSameAddrs` from `vosutils.c`.

## Risks and Edge Cases

`SetAValue` shifts entries left when removing a site but does not decrement `entry->nServers` or clear the trailing slot, so callers must compensate or risk stale duplicate entries. `FindIndex` suppresses status details from `VLDB_IsSameAddrs` other than stopping on `tst`; exported match functions mostly ignore the `st` pointer. Queue operations are not synchronized and assume single-threaded use or external locking. `Lp_QEnumerate` uses `strncpy` with `VOLSER_OLDMAXVOLNAME` and does not explicitly terminate `elem->name`.

## Test Signals

Tests should construct synthetic `nvldbentry` records with RW, RO, backup, multihomed-equivalent, and no-match cases. Removal tests should verify `nServers` and trailing slots in the caller's final write path. Queue tests should cover empty enumeration, LIFO order, scan success/failure, and copied id/copyDate/isValid fields.
