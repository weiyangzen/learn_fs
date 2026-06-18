# sources/distributed-fs/ceph/src/mds/Migrator.h

## Purpose

`Migrator.h` declares the Ceph MDS migration coordinator. It exposes the API used by `MDCache`, `MDSRank`, balancer, locker, and message dispatch code to move subtree authority and capability ownership between MDS ranks.

## Important APIs, Types, and Members

- Export states range from `EXPORT_LOCKING` through `EXPORT_NOTIFYING`, with explicit cancel states.
- Import states range from `IMPORT_DISCOVERING` through `IMPORT_ABORTING`.
- `get_export_statename()` and `get_import_statename()` provide string names for diagnostics and dump output.
- Public status/query methods include `is_exporting()`, `is_importing()`, `is_ambiguous_import()`, `get_import_state()`, `get_import_peer()`, `get_export_state()`, `export_has_warned()`, and `export_has_notified()`.
- Public control methods include `dispatch()`, `handle_mds_failure_or_stop()`, `audit()`, `quiesce_overdrive_export()`, `export_dir()`, `export_empty_import()`, `export_dir_nicely()`, `maybe_do_queued_export()`, `clear_export_queue()`, and `maybe_split_export()`.
- Public encode/decode helpers are available for export/import inode, caps, and directory data.
- Protected methods are grouped by exporter, importer, cap migration, and bystander notification roles.
- Persistent state maps are `export_state` keyed by `CDir*` and `import_state` keyed by `dirfrag_t`.
- Private config-backed state includes `max_export_size` and `inject_session_race`.

## Control Flow

The header defines an event-driven object. External callers initiate exports, feed messenger messages to `dispatch()`, notify failures, and ask status questions. Most transitions are hidden behind protected helpers and friend context classes used as asynchronous continuations from locks, journal commits, waiters, and gather completions.

## State and Persistence Behavior

The header does not directly persist data but declares the state maps used by the implementation to coordinate journaled export/import events. `export_queue` and `export_queue_gen` model deferred exports and invalidate stale parent restarts. `total_exporting_size` and `num_locking_exports` throttle concurrent export size.

## Dependencies and Integration Points

The declaration depends on `Capability`, `Mutation` for `MDRequestRef`, `LogSegmentRef`, MDS message forward declarations, cache object forward declarations, and common Ceph types. It is central to MDS cache balancing, failure recovery, client cap transfer, and journal replay semantics.

## Risks

- The public helper surface is broad, so call sites can couple to migration internals.
- State constants are numeric and used in persisted diagnostics and many switch statements; adding a state requires updating transition logic, dumps, and failure handling.
- `export_state` keyed by raw `CDir*` assumes cache object lifetime is pinned correctly by the implementation.
- Friend context classes imply asynchronous callbacks can reach protected internals after partial state changes.

## Test Signals

Header-level review should verify every declared state has a name and switch coverage in the implementation, every public entry point has an invariant in `Migrator.cc`, and config changes update `max_export_size` and `inject_session_race`. API users should be tested against both normal and degraded MDS maps.
