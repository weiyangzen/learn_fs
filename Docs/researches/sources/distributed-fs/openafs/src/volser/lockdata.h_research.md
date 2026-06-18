# sources/distributed-fs/openafs/src/volser/lockdata.h

## Purpose
Defines small queue data structures used by volser lock/list processing to group related RW/RO/backup volume ids.

## Important APIs And Types
`struct aqueue` stores a volume name, three ids, three copy dates, validity flags, and a next pointer. `struct qHead` stores a queue count and head pointer. Constants include `ZERO`, a placeholder value intended to be replaced by zero, and `N_SECURITY_OBJECTS`.

## Control Flow, State, And Persistence
This header has no executable control flow. Queue state is in-memory only and is managed by `lockprocs.c` functions such as `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, and `Lp_QEnumerate`.

## Dependencies And Integration
It relies on `VOLSER_MAXVOLNAME` and volume-type indexes such as `RWVOL`, `ROVOL`, and `BACKVOL` from volser headers. It is part of VLDB/volser utility support, not persistent volume metadata.

## Risks And Test Signals
Risks include fixed-size name truncation, ambiguous `ZERO`, and ownership expectations for queued `aqueue` allocations. Test signals include queue add/enumerate memory behavior, scan by RW id, and boundary tests for maximum volume names.
