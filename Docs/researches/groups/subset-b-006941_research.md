# Research: subset-b-006941

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGLog.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGLog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGLog.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGLog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGPeeringEvent.cc -->
# sources/distributed-fs/ceph/src/osd/PGPeeringEvent.cc

## Purpose
`PGPeeringEvent.cc` provides the small out-of-line definitions for peering-event support: the mempool object factory for `PGPeeringEvent` and the `MLogRec` constructor/formatter. The implementation keeps heavyweight message printing out of the header while preserving statechart event semantics.

## Important APIs and Functions
- `MEMPOOL_DEFINE_OBJECT_FACTORY(PGPeeringEvent, pg_peering_evt, osd)` registers `PGPeeringEvent` allocation with the OSD mempool helpers used by `MEMPOOL_CLASS_HELPERS()` in the class declaration.
- `MLogRec::MLogRec(pg_shard_t from, MOSDPGLog *msg)` stores the source shard and intrusive pointer to the PG log message.
- `MLogRec::print(std::ostream *out) const` prints the source shard and delegates detailed message formatting to `MOSDPGLog::inner_print()`.

## Control Flow
Construction of `MLogRec` is direct: callers pass the sender shard and raw `MOSDPGLog*`, and the boost intrusive pointer member takes ownership/reference tracking. Printing first emits `"MLogRec from <shard>"`, then calls into the message object to render the log payload.

## State and Persistence Behavior
This file has no persistent state. Its state effects are memory-management related: the mempool factory controls allocation accounting for queued peering events, and the `MLogRec` intrusive pointer keeps the message alive while the statechart event is queued or processed.

## Dependencies and Integration Points
- Includes `osd/PGPeeringEvent.h` for event declarations.
- Includes `include/mempool.h` for factory registration.
- Includes `messages/MOSDPGLog.h` for `inner_print()` and intrusive message ownership.
- Integrated with `PeeringState` reactions that consume `MLogRec` during log exchange.

## Risks and Edge Cases
- `MLogRec::print()` assumes `msg` is non-null. A null `MOSDPGLog*` would dereference during diagnostics.
- Factory registration must match the declaration's mempool helpers; mismatches would affect allocation tracking and possibly build linkage.
- Formatting depends on `MOSDPGLog::inner_print()` remaining safe for partially decoded or otherwise unusual messages.

## Test Signals
Relevant signals are compile/link tests for the mempool factory and peering-message tests that construct and print `MLogRec`. Integration coverage should observe queued `MOSDPGLog` events in `PeeringState` reactions and ensure diagnostics remain useful during peering failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGPeeringEvent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGPeeringEvent.h -->
# sources/distributed-fs/ceph/src/osd/PGPeeringEvent.h

## Purpose
`PGPeeringEvent.h` defines the event envelope and concrete Boost.Statechart events used by OSD placement-group peering. It packages incoming peering messages, local reservation callbacks, lease events, creation metadata, and simple control events into types that `PeeringState` can react to uniformly.

## Important APIs and Types
- `PGCreateInfo` carries the data needed to instantiate a PG: `spg_t pgid`, creation epoch, `pg_history_t`, `PastIntervals`, and whether creation came from the monitor.
- `PGPeeringEvent` wraps a statechart `event_base` intrusive pointer with `epoch_sent`, `epoch_requested`, a printable description, `requires_pg`, and optional `PGCreateInfo`.
- `PGPeeringEventRef` and `PGPeeringEventURef` provide shared and unique ownership forms used by queues and callbacks.
- Message-backed statechart events include `MInfoRec`, `MLogRec`, `MNotifyRec`, `MQuery`, `MTrim`, `MLease`, and `MLeaseAck`.
- Priority/control events include `RequestBackfillPrio`, `RequestRecoveryPrio`, `DeferRecovery`, `DeferBackfill`, and trivial macro-generated events such as `NullEvt`, `PgCreateEvt`, reservation outcomes, `RecoveryDone`, and `RenewLease`.

## Control Flow
Callers construct a concrete statechart event, then wrap it in `PGPeeringEvent`. The templated constructor stores an intrusive pointer via `evt_.intrusive_from_this()`, records the epoch metadata, builds a stable string description by calling the concrete event's `print()`, and appends `+create_info` when present. `PeeringState` later reads `get_event()` and dispatches to statechart reactions while queueing and logging can use `get_desc()`.

Each concrete event is mostly a typed data holder with a `print()` method. Message wrappers preserve sender PG/shard and message payloads. Lease wrappers carry epoch and lease state. Delay and priority events carry scheduler inputs for recovery/backfill reservation control.

## State and Persistence Behavior
These event types are transient in-memory control records. They do not write persistent state themselves. Their epoch fields are safety gates for peering: consumers can compare the event's sent/requested epoch against current OSD maps before applying state transitions. Optional `PGCreateInfo` is owned by the event envelope and transfers PG creation metadata into the peering state machine.

## Dependencies and Integration Points
- Depends on Boost.Statechart and Boost intrusive pointers.
- Uses OSD types such as `spg_t`, `pg_history_t`, `PastIntervals`, `pg_info_t`, `pg_notify_t`, `pg_query_t`, `pg_lease_t`, and shard identifiers.
- Forward-declares `MOSDPGLog`; the out-of-line `MLogRec` implementation includes the message header.
- Integrated directly by `PG::queue_peering_event()`, `PG::do_peering_event()`, and `PeeringState` custom reactions for message, reservation, lease, and recovery events.

## Risks and Edge Cases
- The templated envelope requires the concrete event to support `intrusive_from_this()` and `print(std::ostream*)`; adding a new event without those conventions will fail at compile time.
- `get_current_event()` style access is by base reference; downstream code must use statechart reaction typing rather than unsafe casts.
- Description strings are built at construction time, so later mutation of the underlying message/event is not reflected in `desc`.
- `requires_pg` must be set carefully for create and non-PG-specific events; incorrect values can make queue handling drop or mishandle legitimate creation events.

## Test Signals
Compile-time coverage is important because most contracts are type-level. Runtime tests should cover queueing events across epoch changes, PG creation events with `PGCreateInfo`, `MLogRec` dispatch into `PeeringState`, and formatting for diagnostics. Lease and reservation events should be exercised by peering/recovery scheduler tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGPeeringEvent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGStateUtils.cc -->
# sources/distributed-fs/ceph/src/osd/PGStateUtils.cc

## Purpose
`PGStateUtils.cc` implements lightweight PG state-history instrumentation. It records entry/exit timestamps for nested named states, groups completed state traces by OSD map epoch, stores a bounded recent history, and dumps that history through Ceph's formatter.

## Important APIs and Functions
- `NamedState::NamedState()` captures the current time and calls `PGStateHistory::enter()` when a history object is present.
- `NamedState::~NamedState()` calls `PGStateHistory::exit()` for RAII-style state timing.
- `PGStateHistory::enter()` lazily creates the current `PGStateInstance` and pushes an embedded state.
- `PGStateHistory::exit()` stamps the instance with the current OSD map epoch, records an exit time, and moves a complete instance into the circular buffer when all nested states have exited.
- `PGStateHistory::dump()` emits an array of epochs, each with a sequence of state records containing state name, enter time, and exit time.

## Control Flow
State tracking is stack based. Entering a `NamedState` pushes `(time, state_name)` onto the active instance. Exiting sets the epoch, pops the top embedded state into `state_history`, and if the stack is empty calls `reset()` to move the finished instance into the bounded buffer and clear the active pointer. Dumping iterates only completed instances in the buffer.

## State and Persistence Behavior
State history is in-memory diagnostic state only. `PGStateHistory` keeps at most ten completed `PGStateInstance` objects in a boost circular buffer. It does not serialize to disk. It relies on `EpochSource::get_osdmap_epoch()` at exit time, so the epoch attached to an instance reflects the latest exit, not necessarily every nested state's entry epoch.

## Dependencies and Integration Points
- Includes `PGStateUtils.h` and `common/Clock.h`.
- Uses `ceph_clock_now()` for timestamps and `ceph::Formatter` for dumps.
- Integrated by peering state classes through `NamedState` RAII objects and `PGStateHistory` owned by `PeeringState`.

## Risks and Edge Cases
- `PGStateHistory::exit()` assumes `pi` is non-null and the embedded stack is non-empty; unbalanced enter/exit calls will crash or assert elsewhere.
- `NamedState` stores `state_name` as `const char*`, so callers must pass storage with static or sufficiently long lifetime.
- `dump()` omits the currently active incomplete instance because it only iterates the completed circular buffer.
- Nested state names are recorded by stack order on exit, so history order is exit order, not necessarily entry order.

## Test Signals
Useful tests should create nested `NamedState` scopes, verify a completed history appears only after the outermost exit, check circular-buffer truncation after more than ten instances, and validate formatter field names (`history`, `epochs`, `epoch`, `states`, `state`, `enter`, `exit`). Integration coverage should inspect peering diagnostics after state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGStateUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGStateUtils.h -->
# sources/distributed-fs/ceph/src/osd/PGStateUtils.h

## Purpose
`PGStateUtils.h` declares the diagnostic state-history helpers used around PG peering state transitions. The file provides an abstract epoch source, an RAII state marker, a per-epoch state instance, and a bounded history container.

## Important APIs and Types
- `EpochSource` is a small interface exposing `get_osdmap_epoch()`.
- `NamedState` holds a `PGStateHistory*`, `state_name`, and `enter_time`; its constructor/destructor enter and exit the named state.
- `state_history_entry` is `(enter_time, exit_time, state_name)`.
- `embedded_state` is `(enter_time, state_name)` for active nested states.
- `PGStateInstance` stores one epoch's `state_history` and stack of active `embedded_states`; `enter_state()` pushes and `exit_state()` pops into history.
- `PGStateHistory` owns the current instance, a circular buffer of ten completed instances, an `EpochSource`, and dump/current-state helpers.

## Control Flow
Clients typically allocate `NamedState` at the start of a state scope. That constructor delegates to `PGStateHistory::enter()`. Scope exit triggers the destructor, which delegates to `PGStateHistory::exit()`. `PGStateInstance` manages nesting with a stack; `PGStateHistory::reset()` moves completed instances into the circular buffer and clears active state.

## State and Persistence Behavior
All state is transient and diagnostic. The bounded buffer avoids unbounded memory growth in long-running OSDs. `get_current_state()` returns `"unknown"` when there is no active instance and otherwise returns the top embedded state's name. No object-store or monitor persistence is involved.

## Dependencies and Integration Points
- Depends on `epoch_t`, `utime_t`, and `ceph::Formatter`.
- Uses `boost::circular_buffer` and `std::stack` to bound completed history while representing nested active states.
- `PeeringState` owns/uses these helpers for state-machine diagnostics.

## Risks and Edge Cases
- `PGStateInstance::exit_state()` does not validate that the requested state name matches the stack top; misuse can record misleading histories.
- `get_current_state()` assumes that a non-null active instance has at least one embedded state.
- `const char*` state names are not copied into `std::string`; dynamic strings with shorter lifetime are unsafe.
- The circular buffer size is fixed at ten; longer debugging windows require code changes or external logging.

## Test Signals
Tests should cover balanced and nested enter/exit, `get_current_state()` before/during/after active states, history buffer rollover, and formatter output shape. Misbalanced enter/exit behavior is a risk worth catching with debug or death tests if the surrounding framework supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGStateUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGTransaction.h -->
# sources/distributed-fs/ceph/src/osd/PGTransaction.h

## Purpose
`PGTransaction.h` defines `PGTransaction`, the PG-backend-level transaction description consumed by replicated and erasure-coded backends. It records object creation/removal/clone/rename intent, data writes, zeros, clone ranges, truncates, attr and omap mutations, snap updates, allocation hints, and object-context references in a normalized form that backends can traverse safely.

## Important APIs and Types
- `PGTransaction::obc_map` maps `hobject_t` to `ObjectContextRef` for object contexts touched by the transaction.
- `ObjectOperation::InitType` is a variant over `None`, `Create`, `Clone{source}`, and `Rename{source}` describing how an object is initialized.
- `delete_first` distinguishes deletion of an existing object before recreation from creation of a new object.
- Object-operation predicates `deletes_first()`, `is_delete()`, `is_none()`, `is_fresh_object()`, `is_rename()`, and `has_source()` expose transaction topology to backends.
- Mutation fields include `clear_omap`, `truncate`, `attr_updates`, `omap_updates`, `omap_header`, `updated_snaps`, `alloc_hint`, and interval-mapped `buffer_updates`.
- `BufferUpdateType` is a variant over `Write{buffer,fadvise_flags}`, `Zero{len}`, and `CloneRange{from,offset,len}`.
- Public mutation methods include `create`, `clone`, `rename`, `remove`, `update_snaps`, `omap_clear`, `truncate`, `setattrs`, `setattr`, `rmattr`, `set_alloc_hint`, `write`, `clone_range`, `zero`, `omap_setkeys`, `omap_rmkeys`, `omap_rmkeyrange`, `omap_setheader`, `nop`, `empty`, `get_bytes_written`, and `safe_create_traverse`.

## Control Flow
Callers build a `PGTransaction` by requesting an `ObjectOperation` for each modified object. Creation methods assert the target is empty or delete-first, then set the initialization variant. `rename()` requires a temp source and non-temp target; if the source already has an operation, it moves that operation to the target while preserving whether the target must be deleted first. `remove()` either converts an existing-object operation to delete-first or erases a fresh non-rename object operation as a no-op.

Data writes are stored in an `interval_map` so overlapping and adjacent updates are split and merged deterministically. `SplitMerger::split()` slices writes, zeros, or clone ranges; `can_merge()` allows adjacent writes with matching fadvise flags and adjacent zeros; `merge()` concatenates buffers or zero lengths and refuses clone-range merging. `truncate()` erases buffer updates beyond the truncation offset and tracks both the lowest and final truncate offsets.

`safe_create_traverse()` builds a source-to-destination graph from clone and rename edges, seeds roots from operations without sources plus external sources referenced by operations, then performs post-order traversal so sinks are visited before sources. This ordering lets backends create clone/rename targets before operations that could mutate their sources.

## State and Persistence Behavior
`PGTransaction` is an in-memory planning structure; it does not persist itself. Backends translate its operations into `ObjectStore::Transaction` or EC-specific subtransactions. The state model is designed to preserve enough intent for EC rollback/stash decisions: delete-before-create, clone/rename source identity, snap-only updates, truncation history, and exact byte ranges are all kept separate until backend generation.

Buffer and omap payloads are stored as `ceph::buffer::list` values. Some methods copy and rebuild buffers (`setattrs`, `setattr`) to avoid pinned larger buffers; omap set/remove/range methods encode key maps or sets into bufferlists for backend consumption. `get_bytes_written()` sums only buffer update lengths, not omap/attr/header sizes.

## Dependencies and Integration Points
- Depends on `hobject_t`, `ObjectContextRef`, `interval_map`, `inline_variant::match`, Ceph bufferlists, snap IDs, and OSD internal types or Crimson object contexts depending on `WITH_CRIMSON`.
- Used by `ECTransaction`, `ECCommon`, `ECSwitch`, and backend code to generate concrete object-store work from PG-level operations.
- The file's constraints are tuned for `PrimaryLogPG` and ECBackend workflows such as copy-from rename, make-writeable clone, rollback clone-to-head, and combined clone/rollback sequences.

## Risks and Edge Cases
- The transaction graph must be acyclic and each source can have at most one sink. Violations can lead to traversal errors or assertions.
- `clone_range` sources must not be modified by the same transaction; the class documents this but relies on callers/backends to respect it.
- `remove()` on a fresh object erases the operation as a no-op, but removing a rename target is asserted against; callers must sequence rename/remove carefully.
- `update_snaps()` asserts there are no buffer updates or truncate, so combining snap-only and data mutations on the same operation is invalid.
- `truncate()` stores both lowest and final truncate offsets; backends must interpret the pair correctly when multiple truncates occur.
- `setattrs()`/`setattr()` assign optional bufferlists and call `rebuild()`, which is important for memory pinning; future methods adding buffers should follow the same pattern.
- `omap_rmkeyrange()` takes non-const string references even though it only encodes them, which can surprise callers expecting const inputs.

## Test Signals
Focused tests should cover overlapping writes/zeros/clone ranges in the interval map, truncate interaction with prior writes, rename moving source operations to target, remove-after-create no-op behavior, snap-update assertions, byte-count accounting, and `safe_create_traverse()` ordering for copy-from, make-writeable, rollback, and combined clone/rollback graphs. Integration tests should validate EC transaction generation from this structure through `ECTransaction` and `ECCommon`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGTransaction.h -->
