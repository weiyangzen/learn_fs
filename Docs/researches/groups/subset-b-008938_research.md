# subset-b-008938 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/txn.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/txn.rs

## Purpose
This file defines the write-side accumulator used by TiKV's MVCC transaction actions. `MvccTxn` is not an engine transaction by itself; it records the column-family mutations, pessimistic-lock metadata, memory-lock guards, and lock-wait wakeup information that higher-level actions later turn into a `WriteData` batch. It also defines `ReleasedLock`, used to notify the lock manager after commit or rollback, and `GcInfo`, used for MVCC/GC metrics.

## Important APIs, Types, and Functions
- `MAX_TXN_WRITE_SIZE` is a 32 KiB write-size threshold signal used by transaction code.
- `GcInfo::report_metrics` reports discovered and deleted MVCC version counts.
- `ReleasedLock::new` captures `start_ts`, `commit_ts`, `key`, and whether the released lock was pessimistic.
- `MvccTxn::new` initializes an empty mutation accumulator with a `ConcurrencyManager`.
- `into_modifies`, `take_guards`, and `take_new_locks` transfer accumulated engine modifications, in-memory key guards, and new lock infos to callers.
- `put_lock`, `put_pessimistic_lock`, and `put_shared_locks` write lock CF records and populate `new_locks` when a key is newly locked.
- `unlock_key` appends a lock CF delete and returns a `ReleasedLock`.
- `put_value`, `delete_value`, `put_write`, and `delete_write` encode timestamped default/write CF mutations.
- `mark_rollback_on_mismatching_lock` annotates an async-commit lock with rollback timestamps when a protected rollback would otherwise be overwritten.
- `get_pending_lock_bytes` scans pending lock CF modifications in reverse order so same-batch shared-lock cleanup can observe prior in-memory changes.
- `make_txn_error` is failpoint-only error injection for transaction actions.

## Control Flow
Transaction actions call `MvccTxn` methods after reading a snapshot with `SnapshotReader`. The object simply records intent: lock CF puts/deletes, default CF value writes/deletes, and write CF records. `write_size` is incremented for mutations whose `Modify::size` is meaningful; shared-lock updates only add to size when a new shared-lock record is created. `into_modifies` asserts that `locks_for_1pc` has already been drained, preserving the special 1PC lock processing path.

Rollback and cleanup paths use `unlock_key` to emit a lock delete and a `ReleasedLock`. Shared-lock cleanup may call `get_pending_lock_bytes` between sub-lock operations so it does not reload stale snapshot state after one sub-lock has already been removed in the same transaction batch.

## State and Persistence Behavior
Persistent state is represented as `Modify` values for TiKV column families:
- `CF_LOCK` stores optimistic locks, pessimistic locks, and serialized `SharedLocks`.
- `CF_DEFAULT` stores long values at `key.append_ts(start_ts)`.
- `CF_WRITE` stores commit, rollback, lock, and delete write records at `key.append_ts(commit_ts_or_start_ts)`.

`MvccTxn` also tracks transient in-memory state: `locks_for_1pc`, `new_locks` for lock-manager bookkeeping, `guards` for concurrency-manager memory locks, and `write_size`. `clear` discards only local accumulated state, not engine state.

## Dependencies and Integration Points
The file depends on `txn_types` for key, lock, timestamp, and value encodings; `engine_traits` for CF names; `concurrency_manager` for memory-lock visibility; and storage `Modify` for engine writes. It is called by transaction actions such as prewrite, commit, rollback, cleanup, check-txn-status, and pessimistic-lock acquisition. `ReleasedLock` integrates with the lock manager wakeup path, while `new_locks` feeds wait-for/deadlock metadata.

## Risks
Correctness depends on callers using `is_new` accurately when writing locks; otherwise lock-wait metadata and `write_size` can be wrong. `get_pending_lock_bytes` is order-sensitive and only understands lock CF `Put`/`Delete` mutations. Protected rollback handling for async commit is subtle: missing a rollback timestamp can allow a later async commit to overwrite rollback evidence. `into_modifies` will panic if 1PC locks remain unprocessed.

## Test Signals
The in-file test suite is broad. It covers MVCC reads, prewrite/commit/rollback, insert and not-exist constraints, write-size accounting, rollback collapse, async commit min-commit-ts behavior, timestamp overlap, GC fences, pessimistic lock amendment, shared-lock serialization, and pending shared-lock behavior. These tests are strong regression signals for transaction state transitions and edge cases around overlapped rollback records.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/txn.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/encoded.rs -->
# sources/storage-engines/tikv/src/storage/raw/encoded.rs

## Purpose
This file adapts a raw snapshot whose stored keys and values use an `api_version::KvFormat` encoding into the plain raw-storage `Snapshot` interface expected by scan/get callers. It decodes raw values, filters expired TTL values, hides tombstones, and exposes user values through a wrapping iterator.

## Important APIs, Types, and Functions
- `RawEncodeSnapshot<S, F>` wraps an inner `Snapshot`, captures `ttl_current_ts()` once, and carries the selected `KvFormat`.
- `from_snapshot` constructs the wrapper.
- `map_value` decodes an owned raw value and returns only valid, non-expired user data.
- `get_key_ttl_cf` returns remaining TTL for a key in a CF: `None` for absent/expired, `Some(0)` for no TTL, or remaining seconds/timestamp units for expiring values.
- The `Snapshot` implementation delegates bounds and extension access to the inner snapshot, and returns `RawEncodeIterator`.
- `RawEncodeIterator<I, F>` wraps an engine iterator and filters invalid values on movement.
- `find_valid_value` loops forward or backward until the iterator is invalid, errored, or points at a valid raw value.
- `Drop` records skipped invalid values in the thread-local `RAW_VALUE_TOMBSTONE`.
- `MetricsExt` exposes RocksDB perf-context counters via `RawEncodeIterMetricsCollector`.

## Control Flow
Point reads call the inner snapshot, then `map_value`. Iteration calls inner movement methods first, then `find_valid_value`, which decodes each candidate and skips expired or deleted values in the requested direction. `value()` decodes the current raw value and returns the embedded `user_value`; it assumes the iterator has already been positioned on a valid encoded raw value.

## State and Persistence Behavior
This wrapper does not persist anything. It interprets persisted raw values encoded by the selected `KvFormat`. The captured `current_ts` makes expiration checks stable for the lifetime of a snapshot/iterator. `skip_invalid` is transient accounting and is flushed to `RAW_VALUE_TOMBSTONE` on iterator drop.

## Dependencies and Integration Points
It depends on `api_version::KvFormat` for key/value decoding, `engine_traits` for iterator options and metrics, `raw_ttl::ttl_current_ts` for TTL comparison, and `crate::storage::kv::Snapshot`/`Iterator` traits. `RawStore` uses it for API V1 TTL and API V2 raw paths. API V2 composes it on top of `RawMvccSnapshot`.

## Risks
`value()` uses `unwrap()` on decode, so corrupt encoded values or misuse on an invalid iterator can panic. Because `current_ts` is captured once, very long scans may return values that expire during the scan. Filtering invalid values can turn a single seek into multiple RocksDB iterator steps, so tombstone-heavy ranges can cost more than callers expect. TTL accounting must stay aligned with `KvFormat::decode_raw_value*` semantics.

## Test Signals
There are no tests in this file, but `raw_mvcc.rs` tests exercise `RawEncodeSnapshot<ApiV2>` layered over MVCC raw data. Coverage should include TTL expiry, tombstones, forward/reverse filtering, key-only scans, and malformed value handling in integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/encoded.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/mod.rs -->
# sources/storage-engines/tikv/src/storage/raw/mod.rs

## Purpose
This is the module boundary for raw-storage snapshot adapters and the public raw-store facade. It exposes encoded-value handling, raw MVCC projection, and `RawStore`.

## Important APIs, Types, and Functions
- `pub mod encoded` exports TTL/value decoding wrappers.
- `pub mod raw_mvcc` exports latest-version projection for API V2 raw MVCC keys.
- `mod store` keeps implementation details private.
- `pub use store::RawStore` makes `RawStore` the public entry point.

## Control Flow
There is no runtime control flow in this file. It determines which submodules are externally reachable and hides `store` internals except for the `RawStore` type.

## State and Persistence Behavior
No state is stored here. The persistence behavior lives in the submodules: encoded raw values, timestamped raw MVCC keys, and raw scan/checksum logic.

## Dependencies and Integration Points
Other storage code imports `storage::raw::RawStore` through this re-export. Tests and API-version-specific code may also import `storage::raw::encoded` and `storage::raw::raw_mvcc` directly.

## Risks
The main risk is API surface drift. Making `store` private while re-exporting `RawStore` is clean, but moving or renaming submodules affects downstream imports. Any new raw adapter module must be added here or it will not be visible.

## Test Signals
No direct tests are needed for this module declaration. Build failures and raw-storage integration tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/raw_mvcc.rs -->
# sources/storage-engines/tikv/src/storage/raw/raw_mvcc.rs

## Purpose
This file adapts API V2 raw MVCC data, where multiple timestamped internal keys can exist for one user key, into a raw snapshot that exposes only the latest version per user key. It is intentionally one-directional per iterator positioning mode to avoid ambiguous movement across version groups.

## Important APIs, Types, and Functions
- `RawMvccSnapshot<S>` wraps an inner `Snapshot`.
- `seek_first_key_value_cf` performs a prefix seek over a timestamped key range and returns the first value, which is the latest version because timestamps are descending-encoded.
- The `Snapshot` implementation routes point reads through `seek_first_key_value_cf` and wraps iterators in `RawMvccIterator`.
- `RawMvccIterator<I>` stores an inner iterator plus optional cached current key/value for reverse iteration.
- `is_user_key_eq` compares encoded timestamped keys by truncated user key.
- `move_to_prev_max_ts` walks backward through a version group and caches the first/latest version for the previous user key.
- `next` skips all remaining versions of the current user key in forward scans.
- `prev`, `seek_for_prev`, and `seek_to_last` use cached key/value state because backward movement needs to land on the max timestamp of the previous user key.
- `MetricsExt` forwards RocksDB perf counters via `RawMvccIterMetricsCollector`.

## Control Flow
Forward scans seek to the first internal key for the requested user-key range and use `next` to skip over all versions sharing the same user key. Reverse scans call `seek_for_prev` or `seek_to_last`, then `move_to_prev_max_ts` backs up until it finds the max-timestamp entry for the previous user key, caching the key/value so `key()` and `value()` stay stable even though the inner iterator has moved behind the cached item. Switching scan direction after positioning returns an error.

## State and Persistence Behavior
No writes occur. The wrapper interprets persisted API V2 raw keys, which include timestamps, and exposes one visible value per user key. It uses iterator upper bounds for point reads and transient buffers for reverse-scan cached key/value. Large cached buffers are shrunk when capacity is excessive.

## Dependencies and Integration Points
It depends on `txn_types::Key` timestamp encoding, `TimeStamp::zero` for the upper bound, `engine_traits::DATA_KEY_PREFIX_LEN` and `IterOptions` for bounded prefix seeking, and storage `Snapshot`/`Iterator` traits. `RawStore::V2` composes `RawMvccSnapshot` under `RawEncodeSnapshot<ApiV2>`, so this module projects latest versions before TTL/tombstone decoding.

## Risks
The iterator assumes timestamped key encoding and descending timestamp order. Direction switching is explicitly unsupported and produces an error. `is_user_key_eq` unwraps timestamp truncation, so invalid encoded keys can panic. The point-read upper-bound construction is sensitive to data-key prefix length and timestamp encoding; mistakes can leak adjacent keys or miss versions.

## Test Signals
`test_raw_mvcc_snapshot` writes multiple API V2 timestamped raw versions, wraps the engine snapshot in `RawMvccSnapshot` and `RawEncodeSnapshot`, then verifies point reads, forward scan order, reverse scan order, and that two-way direction use is rejected.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/raw_mvcc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/store.rs -->
# sources/storage-engines/tikv/src/storage/raw/store.rs

## Purpose
This file implements the raw-storage read facade over snapshots for API V1, API V1 TTL, and API V2. It centralizes raw get, TTL get, forward/reverse scan, and checksum logic while selecting the right snapshot adapter for each API version.

## Important APIs, Types, and Functions
- `RawStore<S>` is an enum with `V1`, `V1Ttl`, and `V2` variants.
- `RawStore::new` selects plain snapshot, `RawEncodeSnapshot<ApiV1Ttl>`, or `RawEncodeSnapshot<RawMvccSnapshot<S>, ApiV2>`.
- `raw_get_key_value` dispatches point reads and records flow stats.
- `raw_get_key_ttl` is valid only for TTL-capable API versions; V1 panics.
- `forward_raw_scan` and `reverse_raw_scan` configure bounds and dispatch to the inner generic implementation.
- `raw_checksum_ranges` computes CRC64 xor checksum, key/value count, and total bytes across key ranges.
- `RawStoreInner<S, F>` holds a snapshot and `KvFormat` marker.
- `MAX_TIME_SLICE` and `MAX_BATCH_SIZE` bound cooperative scan work before `yatp::reschedule`.

## Control Flow
Public `RawStore` methods pattern-match on API version and delegate to `RawStoreInner`. Forward scans build upper bounds from the optional end key, seek, then collect up to `limit` pairs while periodically yielding after enough rows and elapsed time. Reverse scans similarly set lower bounds and use `reverse_seek`/`prev`. For V1 key-only scans, iterator options can avoid reading values; TTL/V2 still route through decoding wrappers.

Checksum iterates each `KeyRange`, builds an upper-bounded iterator, decodes raw keys with the selected `KvFormat`, and updates `checksum_crc64_xor` with user key and value. Per-range `Statistics` are collected into the caller-provided vector.

## State and Persistence Behavior
The file is read-only. It interprets persistent raw data according to API version:
- V1 uses the snapshot directly.
- V1 TTL stores encoded raw values and filters/decodes them through `RawEncodeSnapshot`.
- V2 stores timestamped raw MVCC keys, projects latest versions with `RawMvccSnapshot`, then decodes values with `RawEncodeSnapshot<ApiV2>`.

Flow statistics are mutable output state. Scan results are returned as `Vec<Result<KvPair>>`, preserving per-pair error shape even though the implementation mostly returns whole-operation errors.

## Dependencies and Integration Points
It integrates `api_version` formats, engine iterator options, protobuf `ApiVersion` and `KeyRange`, `Cursor`, `Statistics`, `checksum_crc64_xor`, and YATP cooperative scheduling. It is the main raw read path used by storage commands after a snapshot has been acquired.

## Risks
`raw_get_key_ttl` panics on non-TTL V1 callers instead of returning an error. Scan fairness depends on both row count and elapsed time; very expensive per-row decoding before the threshold can still occupy a worker. Bound correctness depends on encoded keys and `DATA_KEY_PREFIX_LEN`. Checksum decodes keys with `decode_raw_key_owned(..., true)`, so malformed data surfaces as operation errors.

## Test Signals
Direct tests are absent in this file. Coverage comes through raw API command tests and `raw_mvcc.rs` adapter tests. Important scenarios include API-version dispatch, TTL filtering, zero-limit scans, key-only scans, reverse bounds, cooperative rescheduling under large scans, and checksum parity with client-visible keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/raw/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/read_pool.rs -->
# sources/storage-engines/tikv/src/storage/read_pool.rs

## Purpose
This file builds the three storage read thread pools used for low, normal, and high priority read commands. It attaches per-thread engine TLS, marks I/O as foreground reads, and flushes read metrics through a pool ticker.

## Important APIs, Types, and Functions
- `FuturePoolTicker<R>` stores a `FlowStatsReporter`.
- `PoolTicker::on_tick` calls `metrics::tls_flush`.
- `build_read_pool` converts `StorageReadPoolConfig` into three YATP configs and builds pools named `store-read-low`, `store-read-normal`, and `store-read-high`.
- `build_read_pool_for_test` builds the same pool layout using `DefaultTicker`.

## Control Flow
Both builders assert that config expansion returns exactly three pool configs. For each config/name pair, they clone the reporter and engine, wrap the engine in `Arc<Mutex<_>>`, configure a `YatpPoolBuilder`, and install lifecycle hooks. `after_start` stores the engine in thread-local storage and sets `IoType::ForegroundRead`; `before_stop` destroys TLS for the engine type.

## State and Persistence Behavior
No persistent state is written. Runtime state is thread-local engine handles, thread-local metrics, pool workers, and file-system I/O type tagging. The `Arc<Mutex<E>>` is only used to clone the engine safely inside worker start hooks.

## Dependencies and Integration Points
This module depends on `StorageReadPoolConfig`, storage engine traits (`Engine`, `FlowStatsReporter`, TLS setters/destructors), `file_system::set_io_type`, and TiKV's YATP pool utilities. Schedulers use the returned `Vec<FuturePool>` to route read work by priority.

## Risks
The `assert_eq!(configs.len(), 3)` makes config shape a hard invariant. The unsafe `destroy_tls_engine::<E>()` relies on setting and destroying the same concrete engine type. If `after_start` panics on the mutex or engine clone, workers may fail to initialize. Metrics flushing depends on ticker execution; stalled pools delay TLS metrics reporting.

## Test Signals
The file has no local tests. Relevant verification is construction from default/test configs, worker lifecycle behavior, TLS engine availability inside read tasks, foreground I/O tagging, and metrics flush behavior under real read workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/read_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/acquire_pessimistic_lock.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/acquire_pessimistic_lock.rs

## Purpose
This file implements single-key pessimistic lock acquisition for TiKV transactions. It handles exclusive and shared pessimistic locks, idempotent retries, read-value and old-value return modes, not-exist constraints, conflict detection, lock-only-if-exists behavior, and the `allow_lock_with_conflict` mode that records a lock after advancing `for_update_ts` to a conflicting commit timestamp.

## Important APIs, Types, and Functions
- `acquire_pessimistic_lock` is the public action. It returns `(PessimisticLockKeyResult, OldValue)`.
- `load_old_value` chooses between already-loaded value state and `SnapshotReader::get_old_value`.
- `handle_existing_exclusive_lock` validates same-transaction exclusive pessimistic locks, updates `for_update_ts` and lock metadata, and serves duplicate/stale requests.
- `handle_existing_shared_lock` updates a same-transaction sub-lock inside `SharedLocks` for shared lock requests.
- `ConflictInfo` converts latest-write conflicts into either a locked-with-conflict result timestamp or a `WriteConflict` error.
- `is_already_exist` recognizes constraint failures that should become write conflicts under conflict-lock mode.

## Control Flow
The action validates `lock_only_if_exists`, updates the concurrency manager max timestamp when the request implies a read, and loads the current lock. Existing exclusive locks either route to idempotent exclusive handling or block shared requests. Existing shared locks block exclusive requests unless shrink-only rules apply; shared requests may update their own sub-lock, reject shrink-only sets, or merge a new sub-lock.

If no blocking current lock exists, the action seeks the latest write. A commit newer than `for_update_ts` is either a `WriteConflict` or, when `allow_lock_with_conflict` is true, advances `for_update_ts`, marks conflict info, and forces value loading. Rollback records and overlapped rollback flags for the same start timestamp reject the lock as rolled back. `check_data_constraint` enforces `should_not_exist`. The function computes `LastChange`, loads requested value/existence/old-value information, builds a `PessimisticLock`, and writes either a shared-lock record or an exclusive pessimistic lock unless `lock_only_if_exists` suppresses locking for a missing key.

## State and Persistence Behavior
Successful acquisition writes to `CF_LOCK` through `MvccTxn`: either `Modify::PessimisticLock` for exclusive locks or a serialized `SharedLocks` `Put`. Repeated requests may update TTL, `for_update_ts`, `min_commit_ts`, `last_change`, and conflict flags. The action does not write `CF_WRITE` or `CF_DEFAULT`; it only reads them to detect conflicts and return values.

## Dependencies and Integration Points
The action depends on `SnapshotReader` for lock/write/value reads, `MvccTxn` for lock writes, `check_data_constraint`, `next_last_change_info`, feature-gated `LAST_CHANGE_TS`, MVCC metrics, `PessimisticLockKeyResult`, and `txn_types` lock/value structures. It is called by pessimistic-lock commands and interacts closely with prewrite, cleanup, pessimistic rollback, and lock-manager wait handling.

## Risks
The branch matrix is large: exclusive versus shared, repeated versus new, conflict-allowed versus conflict-error, and value/existence/old-value combinations. `allow_lock_with_conflict` intentionally changes the persisted `for_update_ts`, so stale retries must not regress it. Shared lock shrink-only behavior can block lock upgrades/downgrades. Some helper comments note currently unchecked cases around commit timestamps and non-pessimistic keys in pessimistic transactions. Linearizability relies on max-ts updates whenever the request reads existence or value.

## Test Signals
The test module is extensive. It covers normal pessimistic locking, lock/data conflicts, rollback and idempotency, return-value and lock-only-if-exists modes, GC fence visibility, old-value correctness, `should_not_exist`, existence checks, last-change computation, `allow_lock_with_conflict`, repeated requests, shared-lock creation/merge/idempotency, upgrade/downgrade blocking, and shrink-only error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/acquire_pessimistic_lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/check_data_constraint.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/check_data_constraint.rs

## Purpose
This file implements the not-exists/existence constraint check used by prewrite and pessimistic lock acquisition. It decides whether a key already exists when a mutation requests `should_not_exist`.

## Important APIs, Types, and Functions
- `check_data_constraint` is the only production function. The caller must pass the latest write for the key.
- It returns `Ok(())` when no constraint applies, the latest write is a delete, or the latest put has a nonzero GC fence that makes it invalid as the latest visible version.
- It returns `ErrorInner::AlreadyExist` with the raw key and existing start timestamp when the key exists.

## Control Flow
The function first treats nonzero `gc_fence` as invalid latest data. If `should_not_exist` is false, or the latest write is `Delete`, or the write is invalidated by GC fence, it returns success. Otherwise a latest `Put` is immediate evidence of existence. For latest `Rollback` or `Lock`, it asks `SnapshotReader::get_write` for an older visible write before `write_commit_ts`; if one exists, the key exists.

## State and Persistence Behavior
The function is read-only. It may perform an additional write-CF lookup for older versions but does not mutate `MvccTxn` or engine state.

## Dependencies and Integration Points
It depends on `txn_types::{Key, TimeStamp, Write, WriteType}` and `SnapshotReader`. It is used by pessimistic lock acquisition and related prewrite paths to implement insert/not-exist assertions against MVCC history and GC fence semantics.

## Risks
Correctness depends on the caller's guarantee that `write` is the latest version. Passing an older write can allow duplicate inserts or false `AlreadyExist` errors. The GC-fence shortcut assumes nonzero fence means the latest data is logically deleted for this check. For `Rollback` and `Lock`, one extra historical lookup is needed, so behavior depends on `SnapshotReader::get_write` skipping irrelevant records consistently.

## Test Signals
`test_check_data_constraint` covers skip cases, delete, latest put conflict, and older-version detection behind rollback/lock records. More coverage would be useful for GC-fence invalidation and real prewrite/acquire paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/check_data_constraint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/check_txn_status.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/check_txn_status.rs

## Purpose
This file implements transaction-status resolution for primary locks and missing-lock cases. It decides whether a transaction is committed, rolled back, still locked, expired, pessimistically rolled back, or missing, and emits rollback/unlock mutations when resolution requires state changes.

## Important APIs, Types, and Functions
- `check_txn_status_lock_exists` handles a found primary lock and returns `(TxnStatus, Option<ReleasedLock>)`.
- `check_txn_status_from_pessimistic_primary_lock` handles TTL and stale forced-lock checks for pessimistic primary locks.
- `check_determined_txn_status` is a read-only lookup of existing commit/rollback records.
- `check_txn_status_missing_lock` handles absent primary locks according to `MissingLockAction`.
- `rollback_lock` removes an exclusive lock, deletes long put values when needed, writes rollback or overlapped-rollback records, and returns a release signal.
- `rollback_shared_lock` removes one sub-lock from `SharedLocks`, writes rollback records, and only deletes the lock CF key when the set becomes empty.
- `collapse_prev_rollback` deletes a previous unprotected rollback record.
- `make_rollback` builds either a rollback write or an overlapped-rollback update to an existing write.
- `MissingLockAction` encodes rollback, protected rollback, or return-error behavior.

## Control Flow
For existing locks, the action first validates that the lock's primary matches the requested key when requested. Invalid stale pessimistic primary locks can be unlocked and then resolved via the missing-lock path; other mismatches return `PrimaryMismatch`. Async-commit locks normally return uncommitted status without rollback or min-commit-ts pushing unless `force_sync_commit` is set.

Expired pessimistic primary locks are either pessimistically rolled back without a rollback record when resolving a pessimistic lock, or fully rolled back with a protected rollback record when resolving a prewrite lock. Expired non-pessimistic locks are rolled back. Unexpired locks may have `min_commit_ts` pushed above the caller's start timestamp and current timestamp, then return uncommitted status with a min-commit-ts-pushed flag.

Missing-lock resolution checks commit records first. Existing commit records return committed or rolled-back status. If no record exists, `MissingLockAction` decides whether to error, do nothing for resolving pessimistic locks, collapse previous rollback, mark rollback on a mismatching async lock, and write a rollback or overlapped rollback.

## State and Persistence Behavior
This file mutates `CF_LOCK`, `CF_WRITE`, and sometimes `CF_DEFAULT` through `MvccTxn`. Rollbacks delete locks, may delete long values from default CF for put locks, and either write rollback records or mark an existing overlapped write with `has_overlapped_rollback` plus optional GC fence. Min-commit-ts push rewrites the lock in lock CF. Shared-lock rollback rewrites or deletes the serialized shared-lock set.

## Dependencies and Integration Points
It depends on `SnapshotReader`, `MvccTxn`, `TxnCommitRecord`, `OverlappedWrite`, `TxnStatus`, lock types, and MVCC metrics. Cleanup and lock-resolution commands call these helpers. `MvccTxn::mark_rollback_on_mismatching_lock` is used for protected rollback evidence when another async commit lock is present.

## Risks
The panic in `rollback_lock` and `rollback_shared_lock` for unexpected committed records reflects a strong invariant: callers should not roll back once a non-rollback commit record exists. Primary mismatch handling has different behavior for stale pessimistic locks versus other locks. `MissingLockAction::collapse_rollback` uses `unreachable!` for `ReturnError`, so callers must not ask collapse behavior in that state. GC fence and overlapped rollback updates are consistency-critical and easy to regress.

## Test Signals
This file has no local test module, but its functions are heavily exercised by `mvcc/txn.rs`, `cleanup.rs`, and transaction command tests. Key signals include TTL expiry, async commit handling, min-commit-ts push, primary mismatch, missing-lock rollback protection, overlapped rollback flags, GC fences, shared-lock rollback, and rollback collapse.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/check_txn_status.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/cleanup.rs -->
# sources/storage-engines/tikv/src/storage/txn/actions/cleanup.rs

## Purpose
This file implements cleanup of a single transaction lock by start timestamp. Cleanup removes expired or forced locks, writes rollback evidence when appropriate, reports committed transactions as errors, and supports both exclusive locks and shared-lock sub-locks.

## Important APIs, Types, and Functions
- `cleanup` is the production action. It returns an optional `ReleasedLock`.
- It first checks `MvccTxn::get_pending_lock_bytes` so batched cleanup of multiple shared sub-locks sees earlier in-batch lock mutations.
- It uses `rollback_lock` for exclusive lock rollback and `rollback_shared_lock` for shared sub-lock rollback.
- It falls back to `check_txn_status_missing_lock` when the target lock is absent or belongs to another transaction.
- Test helpers `must_succeed`, `must_err`, and `must_cleanup_with_gc_fence` exercise engine-level writes and GC-fence assertions.

## Control Flow
The function loads lock state from pending transaction mutations when available, otherwise from the snapshot. If it finds an exclusive lock for `reader.start_ts`, it checks TTL unless `current_ts` is zero. Non-expired locks return `KeyIsLocked`; expired or forced cleanup rolls the lock back. If it finds a shared-lock set containing `reader.start_ts`, it applies the same TTL rule to that sub-lock and then removes only that sub-lock.

When the target lock is absent, or the current lock state is unrelated, cleanup delegates to `check_txn_status_missing_lock` with rollback protection controlled by `protect_rollback`. A committed status becomes `ErrorInner::Committed`; an existing rollback is treated as an idempotent success; a newly missing lock returns success after rollback evidence is written if needed.

## State and Persistence Behavior
Cleanup writes through `MvccTxn`. It deletes lock CF records for exclusive locks or the last shared sub-lock, rewrites shared-lock records when other sub-locks remain, writes rollback records or overlapped rollback updates in write CF, and may delete long default CF values via `rollback_lock`. It returns `ReleasedLock` only when a lock CF key is actually released; removing a non-final shared sub-lock returns `None`.

## Dependencies and Integration Points
It depends on `SnapshotReader`, `MvccTxn`, `check_txn_status_missing_lock`, `rollback_lock`, `rollback_shared_lock`, `TxnStatus`, MVCC metrics, and `txn_types::parse_lock` for pending lock bytes. It is used by cleanup and resolve-lock commands, and its released-lock output feeds lock-manager wakeups.

## Risks
TTL comparison uses physical time components; timestamp composition errors can cause premature or delayed cleanup. Pending lock bytes are essential for multi-sub-lock batches; ignoring them would resurrect removed shared locks from the snapshot. `protect_rollback` changes whether previous rollback records can be collapsed, so callers must choose it according to primary/pessimistic semantics. Committed transactions must return errors rather than writing rollback evidence.

## Test Signals
Tests cover TTL-not-expired errors, forced and expired cleanup, cleanup of another transaction's lock, protected rollback behavior, pessimistic primary rollback protection, GC-fence helper behavior, shared pessimistic and prewrite lock cleanup, released-lock return semantics for final shared-lock removal, and pending-lock-byte handling across multiple sub-lock cleanup operations in one `MvccTxn`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/actions/cleanup.rs -->
