# sources/distributed-fs/openafs/src/volser/lockprocs.c

## Purpose
Implements helper routines for manipulating VLDB server/partition entries and in-memory queues of related volume ids.

## Important APIs And Functions
`FindIndex` searches an `nvldbentry` for a matching server, partition, and volume type, using `VLDB_IsSameAddrs` for address equivalence. `Lp_SetRWValue` and `Lp_SetROValue` update or remove RW/RO site entries. `Lp_Match`, `Lp_ROMatch`, `Lp_AnyMatch`, and `Lp_GetRwIndex` query entry placement. Queue helpers `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, `Lp_QEnumerate`, and `Lp_QTraverse` manage `qHead`/`aqueue`.

## Control Flow And State
`SetAValue` finds the matching site, rewrites server/partition, and compacts arrays when both new server and partition are zero. `FindIndex` stops early for RW searches because only one RW site is expected. Queue operations maintain a singly linked head insertion list; enumeration pops and frees the first node while copying its fields.

## Persistence And Integration
The file mutates in-memory VLDB entries before callers commit them through VLDB APIs. It depends on volser generated headers, VLDB flags, network-order server ids, and `vsutils` address matching.

## Risks And Test Signals
Risks include array compaction without visibly decrementing `nServers` in this helper, address-lookup failures while using index `e` in diagnostics, fixed-size string copying, and queue traversal assuming non-empty state. Test signals include RW/RO match/update/remove cases, multi-address server equivalence, no-match behavior, VLDB error injection, and queue memory ownership tests.
