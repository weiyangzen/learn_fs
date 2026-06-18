# sources/distributed-fs/ceph/src/osd/PGLog.cc

## Purpose
`PGLog.cc` implements the non-template, storage-facing behavior for `PGLog` and `PGLog::IndexedLog`: trimming PG logs and duplicate-op records, reconciling divergent peer logs during peering, persisting log/missing metadata into the PG metadata object's omap, reading the Crimson variant of that metadata, and rebuilding missing sets that include delete markers. It is the operational half of the PG log contract declared in `PGLog.h`.

## Important APIs and Functions
- `PGLog::IndexedLog::split_out_child()` repartitions an indexed log for a split child PG, temporarily drops indexes, delegates to `pg_log_t::split_out_child()`, then reindexes both parent and target and resets rollback iterator state.
- `PGLog::IndexedLog::trim()` removes log entries through a trim version, converts recent trimmed entries and their `extra_reqids` to `pg_log_dup_t`, bounds dup retention with `osd_pg_log_dups_tracked` and `osd_pg_log_trim_max`, updates `tail`, and adjusts `complete_to` and rollback iterator state.
- `PGLog::trim()` validates trim safety against `info.last_complete` for synchronous applied transactions without missing objects, delegates to `IndexedLog::trim()`, and mirrors the resulting `log.tail` into `pg_info_t::log_tail`.
- `PGLog::proc_replica_log()` rewinds a peer/replica log copy against this primary log to identify divergent entries, updates the peer's missing set via `_merge_divergent_entries()`, and recalculates peer `last_update` and `last_complete`.
- `PGLog::rewind_divergent_log()` truncates local divergent future entries during activation, marks dirty ranges, then uses rollback/remove/missing logic to make local store state consistent with the new head.
- `PGLog::merge_log()` is the central peering merge routine. It extends the local log tail, imports stats and hit-set state, rewinds local divergent entries if the incoming head is older, appends incoming head entries if newer, updates missing and rollback metadata, handles Crimson full-rewrite dirtying, and merges dup records.
- `PGLog::merge_log_dups()` copies or extends duplicate-op records at either end, then removes dup records overlapping live log entries above the current tail.
- `PGLog::write_log_and_missing()` and static `_write_log_and_missing*()` convert dirty intervals and changed missing items into `ObjectStore::Transaction` omap removes/sets.
- `PGLog::rebuild_missing_set_with_deletes()` reconstructs `missing` from the in-memory log and object-info attributes while preserving non-log-derived missing entries.
- Under `WITH_CRIMSON`, `FuturizedShardStoreLogReader` and `read_log_and_missing_crimson()` implement asynchronous omap reads into `IndexedLog` and `pg_missing_tracker_t`.

## Control Flow
Trimming starts in `PGLog::trim()`, which checks whether the proposed trim advances past the current tail. When it does, the indexed log repeatedly pops front entries through the trim target, unindexes each entry, optionally records trimmed versions and dup keys for later omap deletion, creates `pg_log_dup_t` records for the primary and extra request IDs still within the configured dup-tracking window, and resets `complete_to` if trimming crosses it. A second loop slowly trims excess dup records to avoid a single large RocksDB tombstone burst.

Peering reconciliation has two directions. For a peer log, `proc_replica_log()` finds the last shared event or falls back to the maximum tail bound, rewinds a temporary `IndexedLog` copy to that boundary, and merges divergent entries into the peer missing tracker without changing the local log. For the local log, `merge_log()` enforces overlap, may splice older incoming entries before the local tail, rewinds local entries above the incoming head, or appends incoming entries above the local head. When appending, it first rewinds local divergent entries to a lower bound, rolls forward remaining rollback metadata, appends new entries with missing-set updates, and then resolves old divergent entries object-by-object.

Persistence control flow is range based. Dirty ranges (`dirty_to`, `dirty_from`, `writeout_from`, and dup equivalents) are converted into omap key-range deletes plus writes for entries in the affected low and high ranges. Explicitly trimmed entries and trimmed dup keys become exact `omap_rmkeys`. Missing changes come from `pg_missing_tracker_t::get_changed()` and are encoded as `missing/<object>` keys or removed when no longer missing. Rollback boundaries are persisted as `can_rollback_to` and `rollback_info_trimmed_to` when required.

## State and Persistence Behavior
This file maintains the durability boundary between the in-memory PG log and the PG metadata omap. Log entries are stored by version-derived keys using checksum encoding. Duplicate request records use `dup_` keys and are indexed separately from live log entries. Missing objects are stored as individual `missing/<object>` keys, with `may_include_deletes_in_missing` as a separate marker because missing state can include delete events only after newer handling is enabled. Legacy `divergent_priors` can force missing-set rebuilds and is removed when `clear_divergent_priors` is set.

Dirty tracking is intentionally sparse: low dirty ranges, high dirty ranges, and writeout floors let callers rewrite only the affected part of the log or dup list. Full rewrites are still forced for cases such as Crimson log merges. `log_keys_debug` mirrors stored non-underscore log keys in debug mode and is checked after writeout to catch omitted or duplicated writes.

Rollback persistence is tied to EC safety. `require_rollback` controls whether `can_rollback_to` and `rollback_info_trimmed_to` are written. `rewind_divergent_log()` preserves the original rollback boundary before rewinding so `_merge_object_divergent_entries()` can decide whether a divergent operation can be rolled back or must be removed and marked missing.

## Dependencies and Integration Points
- Depends on `PGLog.h` for all type declarations and most template merge/read logic.
- Uses `ObjectStore::Transaction` for omap mutation and `ObjectStore`/collection handles for object-info reads.
- Uses `pg_info_t`, `pg_log_t`, `pg_missing_t`, `pg_missing_tracker_t`, `pg_pool_t`, `pg_log_entry_t`, `pg_log_dup_t`, and `object_info_t` from OSD type headers.
- Integrates with peering via `PeeringState`, which owns `PGLog`, calls merge and append helpers, and consumes dirty-info flags.
- Integrates with `PG` for metadata clear/rebuild operations and with `PGBackend`/EC rollback handlers through `LogEntryHandler`.
- Crimson-specific code depends on `crimson::os::FuturizedStore` and Seastar futures.

## Risks and Edge Cases
- `IndexedLog` indexes store raw pointers into list nodes; any splice/pop/assignment must reindex or carefully update indexes. The implementation drops indexes around split and rewinds to avoid stale pointers.
- Trim correctness depends on `trim_to <= can_rollback_to`; trimming rollback-needed entries can break EC rollback safety.
- Dup trimming is deliberately throttled because inflated dup lists can create expensive RocksDB tombstone bursts. Changing this can cause operational latency spikes.
- Merge correctness depends on log overlap and ordered version keys. Assertions enforce overlap, monotonic versions, and EC partial-write relaxations.
- Divergent-entry handling has multiple cases: newer local update, object creation/clone, currently missing object, fully rollbackable entries, and unrollbackable removal plus missing insertion. Missing any case can produce data loss or stale missing state.
- `may_include_deletes_in_missing` changes missing semantics; consumers that assume delete events are omitted can incorrectly remove missing entries.
- Crimson read path asserts on `divergent_priors`, so legacy metadata that the classic path tolerates may not be accepted by Crimson.

## Test Signals
There is no local test file in this repository snapshot found by name for these exact files, but `PGLog.h` contains a `merge_old_entry()` helper explicitly described as existing for `TestPGLog`. Coverage should focus on `merge_log()`, `_merge_object_divergent_entries()` cases, trim-to-dup conversion including `extra_reqids`, omap range write/remove boundaries, missing rebuild with deletes, and Crimson omap read parity. Existing integration references in `PG.cc`, `PeeringState`, `ECCommon`, and `ECTransaction` are strong signals that peering/recovery and EC suites are the relevant behavioral tests.
