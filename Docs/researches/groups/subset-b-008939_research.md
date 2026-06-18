# subset-b-008939 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/commit.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/commit.rs

## Purpose
Implements the MVCC commit action for one key. It turns a matching prewrite lock into a write record at `commit_ts`, removes or updates the lock state, handles duplicate commits idempotently, and returns a `ReleasedLock` when the lock should be released from the lock manager. It is on TiKV's transactional write path and includes special handling for async/large transaction `min_commit_ts`, stale pessimistic locks, and shared-lock containers.

## Important APIs, types, and functions
- `commit<S: Snapshot>(txn, reader, key, commit_ts, commit_role) -> MvccResult<Option<ReleasedLock>>` is the exported action. It reads the current lock state from `MvccTxn` pending lock bytes first, then snapshot storage, writes a `Write` record, and unlocks or updates lock CF.
- `handle_lock_not_found` centralizes absent/mismatched lock behavior. It reads `reader.get_txn_commit_record(&key)?.info()`: rollback/no record becomes `TxnLockNotFound`; put/delete/lock records are treated as duplicate committed commands and return `Ok(None)`.
- `CommitRole` affects diagnostics. Secondary lock-not-found and secondary commit-ts-expired paths collect `MvccInfo` through `collect_mvcc_info_for_debug`.
- `Write::new(WriteType::from_lock_type(lock.lock_type).unwrap(), reader.start_ts, lock.short_value.take())` persists the committed version and carries `last_change` and `txn_source` from the lock.

## Control flow
The function first installs a failpoint, builds a closure that can collect debug MVCC state, and resolves the effective lock state. Pending lock bytes are preferred because batched resolve-lock can modify a shared lock and then commit another sub-lock on the same key before the batch is written. A normal lock must match `reader.start_ts`; a shared lock must contain a sub-lock with `reader.start_ts`, which is removed from the in-memory `SharedLocks` before commit processing.

If no matching lock exists, `handle_lock_not_found` distinguishes duplicate commits from real conflicts. If `commit_ts < lock.min_commit_ts`, the function returns `CommitTsExpired`, logging primary cases as expected and collecting MVCC info for secondaries or non-primary keys. Pessimistic-only locks are abnormal on commit; they are rolled back instead of committed, preserving other sub-locks when the stale pessimistic lock is inside `SharedLocks`.

For a real commit, the action builds the `Write`, marks overlapped rollback when `lock.rollback_ts` contains `commit_ts`, writes it to write CF via `txn.put_write`, and then either removes the lock (`txn.unlock_key`) or rewrites the remaining `SharedLocks`.

## State and persistence behavior
State changes are staged in `MvccTxn`: write CF receives the commit record, default CF is not touched here because prewrite wrote long values, and lock CF is deleted or rewritten. `unlock_key` returns `ReleasedLock` with commit metadata when the lock manager should observe release. Shared lock persistence is incremental: a partially committed shared-lock set remains in lock CF; the final sub-lock removal deletes lock CF. Duplicate commits increment `MVCC_DUPLICATE_CMD_COUNTER_VEC.commit` and do not mutate state.

## Dependencies and integration points
This action depends on `SnapshotReader`, `MvccTxn`, `txn_types::{Lock, SharedLocks, Write, WriteType}`, MVCC conflict/duplicate metrics, and `actions::mvcc::collect_mvcc_info_for_debug`. Command-layer commit and resolve-lock flows call this action with a transaction start timestamp already loaded in the reader.

## Risks and edge cases
The highest-risk areas are shared-lock batch visibility through pending lock bytes, preserving unrelated sub-locks when committing or rolling back one sub-lock, and correctly classifying lock-not-found as duplicate commit versus rollback/collapse. `min_commit_ts` handling is also correctness-critical for async commit and large transactions. Stale pessimistic lock rollback deliberately writes no commit record; changing that behavior would affect resolve-lock and lock-manager release semantics.

## Test signals
The module tests cover normal put/lock/delete commits, idempotent duplicate commit, lock-not-found errors, `min_commit_ts`/`CommitTsExpired`, `last_change` and `txn_source` propagation, stale pessimistic lock rollback, MVCC info collection for unexpected secondary errors, shared-lock partial commit, pending-lock-byte reads across a batch, and preservation of other shared sub-locks when a stale pessimistic sub-lock is removed.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/commit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/common.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/common.rs

## Purpose
Provides shared helpers for transactional actions, currently focused on `last_change` metadata calculation and idempotence after prewrite errors. The helpers let prewrite/commit preserve newer TiKV metadata while still handling older records that lack that metadata.

## Important APIs, types, and functions
- `next_last_change_info(key, write, start_ts, original_reader, commit_ts) -> Result<LastChange>` returns the next `LastChange` for a new lock/write derived from the current latest write.
- `check_committed_record_on_err(prewrite_result, txn, reader, key)` converts selected prewrite errors into a successful idempotent response if the same transaction is already committed.
- Uses `TxnCommitRecord`, `LastChange`, `OldValue`, `Write`, `WriteType`, `SnapshotReader`, and `MvccTxn`.

## Control flow
`next_last_change_info` treats `Put` and `Delete` as fresh data changes at `commit_ts`. For `Lock` and `Rollback`, it reuses existing `LastChange` if it is `Exist` or `NotExist`. When the field is `Unknown`, usually from older TiKV data, it creates a new `SnapshotReader`, seeks the visible write at `commit_ts`, merges the temporary reader statistics back into the original reader, and returns either `NotExist` or a found put timestamp with an estimated distance.

`check_committed_record_on_err` checks `reader.get_txn_commit_record(key)`. If it finds one non-rollback commit record for the transaction, it logs the idempotent condition, clears `txn` to discard staged mutations, and returns an empty per-key result plus the found commit timestamp. Other cases rethrow the original prewrite error.

## State and persistence behavior
`next_last_change_info` is read-only except for accumulating read statistics. `check_committed_record_on_err` can clear staged `MvccTxn` modifications, so callers must only use it when a committed record supersedes the current failed prewrite attempt.

## Dependencies and integration points
`prewrite.rs` uses `next_last_change_info` for lock `last_change` calculation and pessimistic amend. Command prewrite paths can use `check_committed_record_on_err` to make retries idempotent when the write has already committed.

## Risks and edge cases
The compatibility scan for `LastChange::Unknown` may be expensive on long version chains but is required for old data. Correctly adding temporary statistics back to the original reader matters for observability. The idempotence helper cannot prove a transaction committed if MVCC GC removed the commit record, so it intentionally returns the original error in that case.

## Test signals
Coverage is mainly through `prewrite.rs` tests that verify last-change calculation from put/delete/lock/rollback records and through higher-level prewrite command idempotence tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/flashback_to_version.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/flashback_to_version.rs

## Purpose
Implements the low-level actions for flashback-to-version over a key range. Flashback rolls back current locks, writes synthetic MVCC versions that restore each key to a target `flashback_version`, and uses a special prewrite/commit key to make the operation resumable and detectable.

## Important APIs, types, and functions
- `FLASHBACK_BATCH_SIZE` is `257`, reserving one slot for the next-key cursor across batches.
- `flashback_to_version_read_lock` scans lock CF, skipping the flashback transaction's own prewrite lock.
- `rollback_locks` rolls back exclusive and shared locks using `rollback_lock`/`rollback_shared_lock`.
- `flashback_to_version_read_write` scans latest user keys in write CF and returns keys needing restoration.
- `flashback_to_version_write` writes synthetic `Put` or `Delete` write records at `flashback_commit_ts`, using `flashback_start_ts` as the start timestamp.
- `prewrite_flashback_key`, `commit_flashback_key`, `check_flashback_commit`, and `get_first_user_key` manage the special marker key.

## Control flow
The read-lock phase scans `[next_lock_key, end_key)` and filters out locks at `flashback_start_ts`, allowing retries after the flashback marker lock has been written. `rollback_locks` iterates the collected locks until `MAX_TXN_WRITE_SIZE`, setting `reader.start_ts` to each lock's timestamp before calling normal rollback logic. For shared locks it snapshots timestamps, rolls each sub-lock back, and updates the local `SharedLocks` value between iterations.

The write phase scans latest committed user keys and filters out the prewrite marker key, keys whose latest version is already at or before `flashback_version`, and keys already written at `flashback_commit_ts`. For every key, it fetches the visible write at `flashback_version`; a visible long put also copies default CF data to `flashback_start_ts`, while a missing visible write becomes a `WriteType::Delete`.

The marker-key prewrite picks the first user key that needs flashback, writes a lock representing the old value at the target version, and is idempotent if the lock or copied long value already exists. Commit converts that marker lock into a write and unlocks it. `check_flashback_commit` returns false for the expected live marker lock, true for the expected committed marker write, and `FlashbackNotPrepared(region_id)` for mismatched state.

## State and persistence behavior
Flashback mutates lock CF by rolling back locks and by writing/removing the marker lock. It mutates write CF with rollback records for old locks, synthetic versions for restored keys, and the marker commit record. It mutates default CF only when restoring long values. Batches stop early with `Some(next_key)` if `txn.write_size() >= MAX_TXN_WRITE_SIZE`.

## Dependencies and integration points
The module integrates with `MvccReader`, `SnapshotReader`, `MvccTxn`, `check_txn_status::{rollback_lock, rollback_shared_lock}`, `txn_types::{Lock, SharedLocks, Write}`, and command-layer flashback phases. It relies on range scans over lock/write CF and normal MVCC read helpers for value lookup.

## Risks and edge cases
Flashback assumes no writes commit after flashback begins; `flashback_to_version_read_write` asserts latest commit timestamps are not beyond `flashback_commit_ts`. Retry safety depends on skipping already flashed-back keys and on marker-key idempotence. Shared lock rollback must preserve/update local state as sub-locks are removed. Long-value copying must avoid duplicate default CF writes while still restoring data for non-short values.

## Test signals
Tests cover restoring across put/delete/rollback/lock histories, deleted keys, pessimistic locks, duplicate flashback writes, duplicate marker prewrite, start/end-key marker selection including last-region `None` end key, marker commit, and rolling back multiple shared pessimistic locks before writing restored versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/flashback_to_version.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/gc.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/gc.rs

## Purpose
Implements per-key MVCC garbage collection. Given a safe point, it removes obsolete write records and long default values while preserving the latest state needed to answer reads at or after the safe point.

## Important APIs, types, and functions
- `gc(txn, reader, key, safe_point) -> MvccResult<GcInfo>` is the exported action and reports `GcInfo` metrics to `STAT_TXN_KEYMODE`.
- `Gc` holds the key, current seek timestamp, info counters, `MvccTxn`, and `MvccReader`.
- `State::{Rewind, RemoveIdempotent, RemoveAll}` models the version-removal rules.
- `delete_write` deletes write CF and deletes default CF only for non-short `Put` writes.

## Control flow
`Gc::run` starts in `Rewind(safe_point)` and repeatedly `seek_write`s backward from `cur_ts`, updating `cur_ts = commit.prev()` and counting found versions. It stops and returns partial `GcInfo` if `txn.write_size >= MAX_TXN_WRITE_SIZE`.

Before the safe point, `Rewind` keeps versions. At the first version at or below safe point, it switches to `RemoveIdempotent`. This removes rollback and lock records until it sees a data state. A `Put` switches to `RemoveAll(None)` and is kept as the latest value before the safe point. A `Delete` switches to `RemoveAll(Some(delete))`, deferring deletion of that delete marker until the scan completes. Once in `RemoveAll`, every older write is deleted. If the scan completes with a deferred delete, it is also removed, allowing an all-deleted history to disappear.

## State and persistence behavior
All mutations are staged in `MvccTxn`: write CF deletes and, for long put values, default CF deletes keyed by the write start timestamp. `GcInfo` records found/deleted version counts and whether the key was fully processed. Partial completion leaves `is_completed = false`.

## Dependencies and integration points
The action depends on `MvccReader::seek_write`, `MvccTxn::delete_write/delete_value`, `MAX_TXN_WRITE_SIZE`, `txn_types::WriteType`, and GC worker metrics. Tests compare this action with compaction-filter GC behavior.

## Risks and edge cases
The state machine must keep exactly one visible value before the safe point unless a delete history can be fully removed. Removing default CF values only for long puts is essential; short values live inside write records. Partial batches must be resumable and must not mark completion. Off-by-one timestamp handling uses `commit.prev()` and `commit_ts <= safe_point`.

## Test signals
Tests build a multi-version history containing put, delete, lock, rollback, short values, and long values. They run safe points through multiple stages and verify reads before and after GC. A parallel test exercises `gc_by_compact` for the same scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/gc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/mod.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/mod.rs

## Purpose
Defines the storage transaction action module surface. These action modules are higher-level operations over `MvccTxn`, `MvccReader`, and `SnapshotReader` that command handlers compose into transactional behavior.

## Important APIs, types, and functions
This file exports modules: `acquire_pessimistic_lock`, `check_data_constraint`, `check_txn_status`, `cleanup`, `commit`, `common`, `flashback_to_version`, `gc`, `mvcc`, `prewrite`, and `tests`.

## Control flow
There is no runtime control flow. The documentation comment frames actions as groups of basic MVCC operations such as `MvccReader::load_lock` and `MvccTxn::put_write`.

## State and persistence behavior
No direct state mutation occurs here. State behavior is delegated to the exported action modules.

## Dependencies and integration points
This module is the namespace used by command handlers and tests, such as `txn::actions::commit::commit`, `txn::actions::prewrite::prewrite`, and shared testing helpers under `txn::actions::tests`.

## Risks and edge cases
Adding or removing exports here changes module visibility and can break command-layer imports. Exporting `tests` in normal module structure means test helpers are available under cfg-controlled uses elsewhere.

## Test signals
No direct tests. Build coverage and downstream module tests validate this module map.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/mvcc.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/mvcc.rs

## Purpose
Provides debug/introspection helpers for collecting all MVCC state for one key: current lock, write records, and default CF values. This is used for diagnostics and tests, not for normal transactional mutation.

## Important APIs, types, and functions
- `LockWritesVals` is `(Option<MvccLock>, Vec<(TimeStamp, Write)>, Vec<(TimeStamp, Value)>)`.
- `find_mvcc_infos_by_key(reader, key)` loads lock state, scans all write records backward, and scans default CF values for the key.
- `collect_mvcc_info_for_debug(snapshot, key)` creates an `MvccReader` and returns `None` on errors after logging.

## Control flow
The helper first calls `reader.load_lock`. Exclusive locks are returned directly. For `SharedLocks`, the first sub-lock by timestamp is returned for debug compatibility because the result type only carries one lock. It then seeks write records from `TimeStamp::max()` backward until no more writes or zero timestamp. Finally it appends all default CF values from `scan_values_in_default`.

## State and persistence behavior
Read-only. It consumes read statistics on the supplied `MvccReader` for the direct API and logs errors for the snapshot wrapper.

## Dependencies and integration points
`commit.rs` calls `collect_mvcc_info_for_debug` when unexpected secondary commit failures need richer diagnostics. Tests and debug paths use `must_find_mvcc_infos` to compare lock/write/value state.

## Risks and edge cases
This can scan unbounded MVCC history for a key; the source has a TODO to add a limit. Shared-lock reporting loses all but the first sub-lock, so it is diagnostic rather than a complete shared-lock dump. Errors are suppressed to `None` in `collect_mvcc_info_for_debug`, which is appropriate for logging paths but not for correctness decisions.

## Test signals
Tests construct a key with a live lock, two writes, and one long value in default CF. They verify the collected lock matches storage, writes are ordered by commit timestamp, short versus long value handling is correct, and `collect_mvcc_info_for_debug` returns the same tuple.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/mvcc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/prewrite.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/prewrite.rs

## Purpose
Implements the MVCC prewrite action for one mutation. It validates locks and committed versions, handles optimistic and pessimistic transaction modes, writes prewrite locks and long values, calculates async/1PC `min_commit_ts`, returns old values when requested, and supports pipelined-DML generations plus shared pessimistic lock upgrade.

## Important APIs, types, and functions
- `prewrite` is the public wrapper; `prewrite_with_generation` adds a generation for pipelined DML/flush.
- `TransactionProperties` carries start timestamp, transaction kind, commit kind, primary key, TTL, txn size, min commit timestamp, old-value requirement, retry flag, assertion level, and transaction source.
- `CommitKind::{TwoPc, OnePc(max_commit_ts), Async(max_commit_ts)}` controls commit timestamp calculation and lock flags.
- `TransactionKind::{Optimistic(skip_constraint_check), Pessimistic(for_update_ts)}` controls conflict checking.
- `PrewriteMutation` normalizes `Mutation` and owns most validation: `check_lock`, `check_for_newer_version`, `check_assertion`, `write_lock`.
- `async_commit_timestamps` calculates and installs in-memory locks under the concurrency manager; `amend_pessimistic_lock` recovers when a pipelined pessimistic lock was not persisted.

## Control flow
`prewrite_with_generation` converts the mutation, updates the concurrency manager for insert/check-not-exists reads, applies failpoints, and loads lock CF. Existing exclusive locks go through `check_lock`; shared locks require the current transaction to be present and the mutation to be `SharedLock`. Missing locks under `DoPessimisticCheck` trigger pessimistic amend for normal mutations and `PessimisticLockNotFound` for shared lock prewrite.

Duplicate prewrites at generation zero return the existing min commit timestamp. Otherwise the action optionally checks newer versions, runs assertion checks, computes old value if requested, and exits early for `should_not_write` mutations. For writes, `write_lock` creates a lock with TTL, primary, for-update timestamp, transaction size, min commit timestamp, transaction source, optional `last_change`, and short or long value placement. Async commit and 1PC calculate a final min commit timestamp under the key latch and may fall back to 2PC on `CommitTsTooLarge`. Shared lock prewrite updates a sub-lock inside `SharedLocks` and rejects async commit, 1PC, and nonzero generation.

## State and persistence behavior
Prewrite stages mutations in `MvccTxn`: lock CF receives `Lock` or `SharedLocks`, default CF receives long values, and in-memory latch guards are stored in `txn.guards` for async/1PC conflict visibility. It also updates `ConcurrencyManager::max_ts` for insert/check-not-exists linearizability and stores in-memory locks for async/1PC. Old values are returned as `OldValue::{None, Value, ValueTimeStamp, Unspecified}` without necessarily writing state.

## Dependencies and integration points
The action uses `check_data_constraint`, `common::next_last_change_info`, MVCC metrics, `txn_types::{Mutation, Lock, SharedLocks, Write}`, `SnapshotReader`, `MvccTxn`, scheduler TLS feature gating for `LAST_CHANGE_TS`, and command prewrite/flush/acquire-pessimistic-lock flows. `actions/tests.rs` wraps it for many cross-action tests.

## Risks and edge cases
Correctness hinges on not skipping constraint checks in retry paths that can lose idempotence, respecting `expected_for_update_ts` for force-locked pessimistic locks, and handling rollback records without false conflicts. Assertion checks have performance-sensitive reload rules and strict/fast/off semantics. Async/1PC fallback must clear lock flags and secondaries. Shared lock prewrite is intentionally narrow; accepting wrong mutation types, generations, or commit modes would corrupt shared-lock state. Long value placement and old-value reads must respect GC fences and short-value encoding.

## Test signals
The large test module covers async commit and 1PC max/min commit timestamps, pessimistic variants, GC fence handling, resend/retry behavior for non-pessimistic keys, old value over rollback/lock/delete/random histories, assertion levels, deferred uniqueness checks, last-change calculation and inheritance, expected `for_update_ts`, 1PC in-memory lock visibility, and shared-lock prewrite merge/rejection cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/prewrite.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/tests.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/tests.rs

## Purpose
Defines reusable test helpers for the transaction action layer. These helpers perform prewrite, flush, pessimistic prewrite, delete, lock, shared lock, and rollback operations against a test engine and assert success or failure.

## Important APIs, types, and functions
- `must_prewrite_put_impl`, `must_prewrite_put_impl_with_should_not_exist`, and `must_prewrite_insert_impl` are the central successful prewrite wrappers.
- `flush_put_impl`, `flush_put_impl_with_assertion`, and `must_flush_put` exercise command-layer `Flush` with generations.
- `must_pessimistic_prewrite_*`, `must_prewrite_put_async_commit`, and `must_pessimistic_prewrite_put_async_commit` cover pessimistic and async paths.
- `must_prewrite_put_err_impl*`, `must_prewrite_insert_err_impl`, and related wrappers return expected `mvcc::Error`.
- `must_prewrite_delete`, `must_prewrite_lock`, `must_shared_prewrite_lock`, and `must_rollback` stage common MVCC histories.

## Control flow
Most helpers build a `Context`, take an engine snapshot, create a `ConcurrencyManager`, `MvccTxn`, and `SnapshotReader`, construct `TransactionProperties`, call `prewrite` or `txn::cleanup`, then write `txn.into_modifies()` to the engine. Error helpers stop before writing and return the unwrapped error. Flush helpers construct a command and run `process_write` with a `WriteContext` that includes `MockLockManager`, statistics, and a test `TxnStatusCache`.

## State and persistence behavior
Successful helpers persist staged lock/write/default CF mutations through the engine's `write` method or `mvcc::tests::write`. Error helpers are read/validation paths and do not persist `MvccTxn` modifications. Helpers can set region id and transaction source in `Context`, set async commit secondaries, TTLs, min/max commit timestamps, assertions, retry flags, and expected for-update timestamps.

## Dependencies and integration points
This file sits under `actions` but integrates command and action layers: `prewrite`, `Flush`, `WriteContext`, `MockLockManager`, `TxnStatusCache`, `MvccTxn`, `SnapshotReader`, and test MVCC write utilities. Other action tests import these helpers to assemble repeatable histories.

## Risks and edge cases
Because these are assertion helpers, parameter defaults encode assumptions used by many tests. A subtle change in defaults for `pessimistic_action`, `for_update_ts`, assertion level, region id, transaction source, or async secondaries can change broad test semantics. Helpers that write immediately are unsuitable for tests needing to inspect staged but unapplied modifications.

## Test signals
This file is itself test infrastructure. Its signal comes from downstream modules: commit, prewrite, gc, flashback, cleanup, and command tests rely on these helpers to create committed versions, locks, rollbacks, shared-lock upgrades, async commit locks, and failure cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/acquire_pessimistic_lock.rs -->
# sources/storage-engines/tikv/src/storage/txn/commands/acquire_pessimistic_lock.rs

## Purpose
Implements the command-layer wrapper for acquiring pessimistic locks on one or more keys. It converts request fields into action calls, handles lock-wait/resumable results, returns optional old/current values, stages writes, and reports newly acquired locks to the scheduler.

## Important APIs, types, and functions
- The `command!` macro defines `AcquirePessimisticLock` fields: keys `(Key, should_not_exist, is_shared_lock)`, primary, `start_ts`, TTL, first-lock flag, `for_update_ts`, wait timeout, return-values flag, `min_commit_ts`, existence flags, and `allow_lock_with_conflict`.
- `CommandExt` supplies context, request tag/type, timestamp, write byte accounting, pipelining, and lock key extraction.
- `WriteCommand::process_write` is the execution entry point.
- `make_write_data(modifies, old_values)` attaches `TxnExtra { old_values, one_pc: false, allowed_in_flashback: false }` when writes exist.

## Control flow
`process_write` rejects multi-key requests when `allow_lock_with_conflict` is enabled. It creates `MvccTxn` and `ReaderWithStats<SnapshotReader>`, then iterates keys. Each key calls `txn::acquire_pessimistic_lock` with request flags including existence checks, old-value requirement, lock-only-if-exists, conflict allowance, and shared-lock mode.

Successful keys push a `PessimisticLockKeyResult` and, when available, insert old values. `KeyIsLocked` builds `PessimisticLockParameters` and `WriteResultLockInfo`, clears prior mutations/results, marks the response as `Waiting`, and stops. `NotInShrinkMode` marks existing shared locks shrink-only, clears previous mutations/results/old values, writes the updated shared lock, and returns a `KeyIsLocked`-style error for the shared lock. Other MVCC errors are returned directly.

After the loop, the command extracts new locks and modifies. If an encountered lock has no wait timeout, legacy requests return a command error while resumable `allow_lock_with_conflict` requests store a per-key `Failed` result. The final `WriteResult` uses `ResponsePolicy::OnProposed`, includes lock-wait info, staged `WriteData`, rows, process result, and no released locks.

## State and persistence behavior
The command itself stages, but does not apply, lock CF modifications in `WriteData`. It may also stage a shrink-only update to an existing `SharedLocks` value. `TxnExtra.old_values` carries resolved old values for CDC/extra-op consumers. `new_acquired_locks` are taken from `MvccTxn` for lock manager bookkeeping.

## Dependencies and integration points
This command depends on the lower-level `txn::acquire_pessimistic_lock` action, `LockManager` wait semantics, `ReaderWithStats`, `WriteContext`, `PessimisticLockResults`, `PessimisticLockParameters`, resource metering, and `TxnStatusCache` in tests. It is the command executed by scheduler/write workers for TiDB pessimistic locking.

## Risks and edge cases
Clearing prior successful locks on the first wait/error is deliberate; otherwise a partially successful multi-key request could persist locks before waiting. The protocol split for `allow_lock_with_conflict` is subtle: only single-key requests are supported and errors become per-key failures. Shared lock shrink-only conversion must be persisted even though the command returns a lock error. Old values must be cleared if mutations are cleared to avoid reporting values for unapplied locks.

## Test signals
Tests cover return-values across put/delete/lock/rollback histories, per-key equality for `PessimisticLockKeyResult`, shared lock acquisition by multiple transactions, exclusive lock conversion to shrink-only, subsequent wait behavior for exclusive and shared requests, and helper execution through a full `WriteContext`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/acquire_pessimistic_lock.rs -->
