# sources/distributed-fs/ceph/src/osd/PGLog.h

## Purpose
`PGLog.h` declares and partially implements Ceph's placement-group log manager. The file documents the PG log's three core purposes: speeding recovery, detecting duplicate client operations, and preserving enough rollback metadata to make erasure-coded updates safe. It defines `PGLog`, `PGLog::IndexedLog`, the `LogEntryHandler` callback interface, dirty-state bookkeeping, missing-set helpers, log merge algorithms, and static read/write APIs for PG log persistence.

## Important APIs and Types
- `PGLog::LogEntryHandler` abstracts store-side actions driven by log transitions: `rollback`, `rollforward`, `trim`, `trim_after_remove`, `remove`, `try_stash`, and `partial_write`.
- `PGLog::IndexedLog` extends `pg_log_t` with lazy indexes by object, request ID, extra request ID, and duplicate request record. It also tracks recovery iterators (`complete_to`, `last_requested`) and rollback trimming state.
- Index flags `PGLOG_INDEXED_OBJECTS`, `PGLOG_INDEXED_CALLER_OPS`, `PGLOG_INDEXED_EXTRA_CALLER_OPS`, and `PGLOG_INDEXED_DUPS` allow partial lazy index construction.
- Rollback helpers `advance_can_rollback_to()`, `trim_rollback_info_to()`, `roll_forward_to()`, `skip_can_rollback_to_to_head()`, and `rewind_from_head()` maintain `can_rollback_to`, `rollback_info_trimmed_to`, and a reverse iterator into the log.
- Duplicate-detection helpers `logged_req()`, `get_request()`, and `get_object_reqids()` query live log entries, extra reqids, and trimmed duplicate records.
- Missing/recovery APIs include `missing_add()`, `missing_add_next_entry()`, `recover_got()`, `reset_complete_to()`, `activate_not_complete()`, `append_log_entries_update_missing()`, and `append_new_log_entries()`.
- Peering APIs include `proc_replica_log()`, `rewind_divergent_log()`, `merge_log()`, `merge_log_dups()`, `split_into()`, `merge_from()`, and `reset_backfill_claim_log()`.
- Persistence APIs include non-static and static `write_log_and_missing()`, `_write_log_and_missing*()`, `read_log_and_missing()`, and Crimson `read_log_and_missing_crimson()`.

## Control Flow
`IndexedLog` provides most in-memory mutation flow. Appending a log entry asserts monotonic versions, trims large embedded bufferlists, pushes the entry, advances `head`, updates any indexes that were already materialized, and if the entry was not yet applied advances rollback metadata through `LogEntryHandler` callbacks. Rewinding delegates to `pg_log_t::rewind_from_head()`, then rebuilds indexes and rollback iterator state.

Lazy lookup flow is index-on-demand. `logged_object()` builds the object index if absent. `logged_req()` checks primary caller op index, falls back to extra caller ops, then `get_request()` finally checks dup records if live entries do not contain the request. This tiering keeps common lookups fast while avoiding unnecessary multimap and dup scans.

Recovery flow centers on `missing` and `complete_to`. `append_log_entries_update_missing()` appends entries to a log if provided, ignores `ERROR` entries for missing-state mutation, updates or removes missing entries depending on delete semantics, invokes rollback handlers for delete/lost-delete cases, and returns whether stats should be invalidated. `recover_got()` removes recovered objects from missing, updates `num_objects_missing`, and advances `last_complete` until the next oldest missing version or, under EC optimized partial logs, until the end guard.

Divergent merge flow is implemented as templates in the header. `_merge_divergent_entries()` groups divergent entries by object. `_merge_object_divergent_entries()` filters errors and partial writes not written to the shard, derives prior/first/last divergent versions, and handles five cases: superseded by a newer log entry, creation/clone requiring object removal, current missing adjustment, full rollback, or removal plus missing insertion when rollback is impossible.

Read flow in `read_log_and_missing()` iterates the PG metadata object's omap, decodes log entries, duplicate records, rollback markers, `missing/` keys, `may_include_deletes_in_missing`, and legacy `divergent_priors`. It builds a new `IndexedLog`, may rebuild missing from object-info attributes and divergent priors, and optionally verifies stored missing entries against disk state.

## State and Persistence Behavior
`PGLog` owns `pg_missing_tracker_t missing`, `IndexedLog log`, and a set of dirty cursors. `dirty_to`/`dirty_from` mark log ranges needing remove/rewrite; `writeout_from` marks entries needing writeout without necessarily deleting the range; `trimmed` records exact entry keys to remove; dup records have parallel `dirty_to_dups`, `dirty_from_dups`, `write_from_dups`, and `trimmed_dups` fields. `touched_log`, `dirty_log`, `clear_divergent_priors`, and `may_include_deletes_in_missing_dirty` control full touches and special metadata keys.

`is_dirty()` is the authoritative write-needed check. `mark_log_for_rewrite()` forces complete log and dup rewrite. `undirty()` resets dirty cursors, clears trimmed sets, flushes missing tracker changes, and runs debug consistency checks. `needs_write()` also treats a never-touched log as write-needed.

Rollback state is embedded in `IndexedLog` through inherited `pg_log_t` fields and a reverse iterator. `advance_can_rollback_to()` updates rollback boundaries and calls a supplied callback for entries newly crossing the trim/roll-forward point, passing each entry and its previous version. This feeds EC rollback trimming, rollforward, and partial-write last-complete metadata.

On disk, the static read/write methods encode log entries by version keys, duplicate records by `dup_` keys, missing items by `missing/<object>`, and rollback markers by fixed keys. Replicated pools without shards synthesize `rollback_info_trimmed_to` from `info.last_update` when absent.

## Dependencies and Integration Points
- Inherits `DoutPrefixProvider` and uses Ceph logging context from `CephContext`.
- Builds on `pg_log_t`, `pg_log_entry_t`, `pg_log_dup_t`, `pg_missing_tracker_t`, `pg_info_t`, `pg_pool_t`, `hobject_t`, `eversion_t`, and `pg_shard_t` from OSD core types.
- Uses `ObjectStore` for persistence and `object_info_t` via `OI_ATTR` during missing rebuild/read verification.
- Calls into backend-specific rollback/store logic only through `LogEntryHandler`, keeping PG log reconciliation independent from concrete replicated/EC backends.
- Used by `PG`, `PeeringState`, `PGBackend`, EC transaction generation, and Crimson OSD code.

## Risks and Edge Cases
- Raw pointer indexes into `std::list` entries and dup records are safe only if list nodes are not invalidated unexpectedly; every mutation path must keep indexes in sync.
- `unindex(const pg_log_entry_t&)` notes it only works when removing from the tail for object-index correctness; using it elsewhere can leave stale object pointers.
- EC optimized partial writes relax prior-version invariants and can make `complete_to` handling non-intuitive when a shard did not participate in a write.
- `get_request()` for extra reqids warns that it returns a matching request but not necessarily the most recent, which matters for duplicate detection semantics.
- `split_pwlc()` can roll non-primary shard partial-write completion state too far back; comments rely on the primary correcting it during activation.
- Rebuilding missing from divergent priors contains compatibility handling for an old tracker issue; tightening assertions can break upgrades or recovery from legacy metadata.
- Dirty cursors use `eversion_t::max()` and empty sentinel values heavily; off-by-one errors translate directly into missing omap deletes or stale log keys.

## Test Signals
The header names `TestPGLog` as a consumer of `merge_old_entry()`, indicating unit-level expectations around divergent-entry handling. Strong regression coverage should include lazy index construction and invalidation, request/extra-request/dup lookup behavior, split/merge of logs and missing sets, `recover_got()` progression of `last_complete`, EC partial-write paths, and read/write round trips with rollback metadata and delete-bearing missing entries. Integration tests should exercise peering through `PeeringState` and backend rollback through replicated and EC handlers.
