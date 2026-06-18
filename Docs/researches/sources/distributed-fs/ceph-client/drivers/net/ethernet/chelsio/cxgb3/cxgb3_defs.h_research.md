# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_defs.h

## Purpose
`cxgb3_defs.h` provides small inline helpers for mapping T3 offload connection IDs to TID table entries. It is part of the offload-facing internal API.

## Important APIs, Types, And Functions
- `VALIDATE_TID` enables validation behavior in included offload definitions.
- `atid2entry` and `stid2entry` convert active-open and server TID numbers into their table entries by subtracting base IDs.
- `lookup_tid` validates a regular TID against `ntids` and returns the entry only if it has an attached client.
- `lookup_stid` and `lookup_atid` validate server/active-open TID ranges and reject entries whose `next` pointer indicates the entry is on a free list rather than live.

## Control Flow And State
The helpers are used in offload receive/control paths when firmware messages identify a connection by TID/STID/ATID. They translate IDs into `struct t3c_tid_entry` pointers after range and live-entry checks.

## State And Persistence Behavior
The file owns no state. It reads `struct tid_info` tables defined by `cxgb3_offload.h`/`t3cdev.h`. The pointer-range checks depend on table/free-list layout in those structures.

## Dependencies And Integration Points
The header includes Linux SKB/TCP headers, `t3cdev.h`, and `cxgb3_offload.h`. It integrates firmware TID values with offload client connection state, listen entries, and active-open entries.

## Risks And Edge Cases
The free-list detection uses pointer comparisons across table regions, so it is tightly coupled to allocation layout. Invalid IDs return NULL; callers must handle NULL before dereferencing. `atid2entry` and `stid2entry` do no range checks themselves and must be called only after validation.

## Test Signals
Signals include offload connection setup/teardown, active-open and listen lookup behavior, invalid TID message handling without crashes, and tests that freed STID/ATID entries are not treated as live connections.
