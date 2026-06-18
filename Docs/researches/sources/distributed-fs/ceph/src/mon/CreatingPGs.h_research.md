<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CreatingPGs.h -->
# sources/distributed-fs/ceph/src/mon/CreatingPGs.h

## Purpose
`CreatingPGs.h` defines the serialized monitor-side state for placement groups and pools that are in the process of being created. OSDMonitor uses this structure to remember in-flight PG creation progress across OSD map updates and monitor persistence.

## Important APIs, types, and functions
`creating_pgs_t` contains `last_scan_epoch`, a map of creating `pgs`, a pool creation `queue`, and `created_pools`. Nested `pg_create_info` stores creation epoch/time, up/acting sets, primaries, PG history, and past intervals. Nested `pool_create_info` stores pool creation epoch/time, current start index, target end, and `done()`.

Helpers include `still_creating_pool()`, `create_pool()`, `remove_pool()`, encode/decode/dump methods, and test-instance generators. Encoder macros expose feature-aware encoding for `pg_create_info` and `creating_pgs_t`.

## Control flow
Pool creation calls `create_pool()` to enqueue a range `[0, pg_num)` and mark the pool as created. As PGs are materialized, OSDMonitor updates `queue.start` and moves entries into `pgs`. `still_creating_pool()` checks both active PGs and queued work. `remove_pool()` erases all PGs in the target pool range plus queue and created-pool state.

## State and persistence behavior
The structure is pure persisted state. Encoding version 3 includes full `pg_create_info`; pre-Octopus feature encoding falls back to legacy pair-like create epoch/stamp data. Decoding handles older structures by reading a count and legacy PG records. `created_pools` prevents duplicate pool creation scheduling.

## Dependencies and integration points
The header depends on Ceph encoding, `utime_t`, and OSD types such as `pg_t`, `pg_history_t`, and `PastIntervals`. It is integrated with OSDMonitor's map update and PG creation logic, not standalone runtime code.

## Risks and edge cases
Backward compatibility is central: pre-Octopus instances lack up/acting/history fields, so users of decoded legacy records must tolerate defaults. `remove_pool()` relies on `pg_t` ordering by pool id and lower-bound ranges. `create_pool()` asserts the pool was not already marked created, so callers must check or maintain idempotency externally.

## Test signals
Encoder tests should cover current and legacy feature paths, empty and populated queues, pool removal range erasure, duplicate pool creation assertions, `done()` boundary behavior, and dump output including PG history and past intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CreatingPGs.h -->
