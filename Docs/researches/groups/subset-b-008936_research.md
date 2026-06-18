# Research Report: subset-b-008936

Work item `subset-b-008936` covers TiKV MVCC consistency checking, metrics, module exports/errors, read activity tracking, and point/snapshot reader behavior. Each file section below is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/consistency_check.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/consistency_check.rs

## Purpose

This file implements MVCC-aware raftstore consistency checking and reusable MVCC info scanning over TiKV's three MVCC column families. It serves two related purposes: `Mvcc<E>` is a raftstore `ConsistencyCheckObserver` that computes a CRC32 hash over live MVCC state plus region state, and `MvccInfoScanner`/`MvccInfoIterator` expose structured MVCC information for debugging or RPC-style inspection.

## Important APIs, Types, and Functions

- `Mvcc<E: KvEngine>` is the consistency-check coprocessor. It carries an `Arc<AtomicU64>` local GC safe point and has no engine instance of its own, only `PhantomData<E>`.
- `get_safe_point_for_check` widens the loaded safe point by `SAFE_POINT_WINDOW` seconds after shifting through TiKV's physical timestamp bits. The leader embeds this adjusted safe point into the consistency-check context.
- `ConsistencyCheckObserver::update_context` appends the MVCC check method byte and little-endian safe point to raftstore's context buffer, then returns `true` to skip later observers.
- `ConsistencyCheckObserver::compute_hash` validates the method byte, reads the safe point, skips stale or zero-window checks, scans MVCC data from region start/end data keys, and folds the raft region-state key/value into the checksum.
- `MvccInfoObserver` is the scanner callback contract. It receives `on_new_item`, per-CF callbacks for write/lock/default entries, and an `emit` hook for a completed user key.
- `MvccInfoScanner<Iter, Ob>` merges the write, lock, and default CF iterator streams by user-key prefix and delegates parsing/selection to an observer.
- `MvccInfoCollector` builds `kvproto::kvrpcpb::MvccInfo` values with writes, lock, and default values converted into protobuf MVCC records.
- `MvccInfoIterator` wraps the scanner as a bounded Rust iterator.
- `MvccChecksum` hashes non-stale writes, locks, and only default values that correspond to committed writes after the safe point.

## Control Flow

`update_context` serializes a method discriminator and adjusted safe point. Followers call `compute_hash`, which rejects empty context, checks stale local safe-point conditions, creates three CF iterators over the data-key range, and repeatedly calls `MvccInfoScanner::next_item` until exhausted. The scanner chooses the next user-key prefix by comparing the lock key with the timestamp-truncated write key. It then drains all writes for that prefix, all matching lock records, and all matching default records, stopping each CF loop when the observer returns `false` because the iterator has reached another user key.

For checksums, `on_write` skips records whose commit timestamp is at or below the safe point, hashes newer write records, and records their start timestamps. `on_default` sorts the collected start timestamps lazily and hashes a default CF value only when its start timestamp belongs to a committed write newer than the safe point. This prevents uncommitted default values from affecting consistency hashes.

## State and Persistence Behavior

The code is read-only with respect to RocksDB. It reads `CF_WRITE`, `CF_LOCK`, `CF_DEFAULT`, and `CF_RAFT` snapshots, and uses the local safe point atomically with acquire ordering. Persistent MVCC state remains in the engine; transient scanner state includes iterator positions, current user key, collected protobuf info, checksum digest, and per-key committed start timestamps.

## Dependencies and Integration Points

The observer plugs into `raftstore::coprocessor::ConsistencyCheckObserver`. It depends on `engine_traits` iterators and CF constants, `keys::*` data/region key encoding, `txn_types::Key`, `WriteRef`, `parse_lock`, TiKV's `Either`, and kvproto MVCC protobuf structures. The public re-exports in `mvcc/mod.rs` expose `MvccConsistencyCheckObserver`, `MvccInfoScanner`, `MvccInfoCollector`, and `MvccInfoIterator` to the rest of storage.

## Risks and Edge Cases

- `update_context` uses `unsafe set_len` plus pointer copy. The length reservation and copy size are straightforward, but changes here require care.
- Shared locks parsed by `txn_types::parse_lock` are explicitly `unimplemented!` in collector and checksum paths. If shared-lock encoding can appear in these code paths, consistency checks or debug scans may panic.
- Safe-point logic intentionally skips checks when the embedded safe point is stale relative to the local safe point; this avoids false mismatches but can reduce coverage during fast GC movement.
- Iterator bounds reject non-MVCC data keys except `DATA_MAX_KEY`; callers must pass data-key encoded region boundaries.
- `MvccChecksum` depends on write/default ordering per key and hashes default values only after seeing writes for that item.

## Test Signals

Tests cover context serialization and 120-second safe-point adjustment, checksum stability when safe points move within a stale range and difference when old committed data becomes included, and `MvccInfoCollector` behavior across default, lock, and write CF records. Test fixtures use `TestEngineBuilder`, transaction helpers, and explicit CF writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/consistency_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/metrics.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/metrics.rs

## Purpose

This file centralizes Prometheus metric definitions for MVCC transaction conflict paths, duplicate command handling, check-txn-status outcomes, prewrite assertion behavior, post-commit retry detection, scan-lock read-lock hold time, and MVCC/GC version histograms. It contains no business logic; it defines stable metric names and static label enums used by MVCC readers and transaction commands.

## Important APIs, Types, and Functions

- `MvccConflictKind` labels conflict counters for prewrite conflicts, rollback observations, commit lock misses, rollback-after-commit, pessimistic lock conflicts, and pipelined pessimistic amend results.
- `MvccDuplicateCommandKind` labels duplicate command counters for prewrite, commit, rollback, and pessimistic lock acquisition variants.
- `MvccCheckTxnStatusKind` labels check-txn-status result categories: rollback, timestamp update, commit-info lookup, and pessimistic rollback.
- `MvccPrewriteAssertionPerfKind` describes whether prewrite assertions loaded writes, reloaded non-data/write-not-loaded versions, or skipped reloads.
- `ScanLockReadTimeSource` is used by `MvccReader::load_in_memory_pessimistic_lock_range` to distinguish resolve-lock and pessimistic-rollback scan-lock timing.
- `MVCC_VERSIONS_HISTOGRAM` and `GC_DELETE_VERSIONS_HISTOGRAM` are dynamic histograms keyed by `key_mode`.
- `MVCC_CONFLICT_COUNTER`, `MVCC_DUPLICATE_CMD_COUNTER_VEC`, `MVCC_CHECK_TXN_STATUS_COUNTER_VEC`, `MVCC_PREWRITE_ASSERTION_PERF_COUNTER_VEC`, `MVCC_PREWRITE_REQUEST_AFTER_COMMIT_COUNTER_VEC`, and `SCAN_LOCK_READ_TIME_VEC` are lazy static metric handles.

## Control Flow

There is no runtime control flow beyond `lazy_static!` initialization. At first use, each metric is registered in the global Prometheus registry. Static metric macros generate typed accessors so call sites use enum variants instead of ad hoc label strings. Histogram buckets use exponential series: MVCC version histograms start at 1 and double for 30 buckets; scan-lock read duration starts at 10 microseconds and doubles for 20 buckets.

## State and Persistence Behavior

All state is process-local metric state held by the Prometheus registry. Counters and histograms are monotonic or cumulative for process lifetime and are not persisted by this file. Metric samples become externally visible through TiKV's metrics exposition path.

## Dependencies and Integration Points

The file depends on `prometheus`, `prometheus_static_metric`, and `lazy_static`. `mvcc/mod.rs` re-exports `GC_DELETE_VERSIONS_HISTOGRAM` and `MVCC_VERSIONS_HISTOGRAM`. Other MVCC transaction modules increment the conflict, duplicate, check-status, assertion, and request-after-commit counters. `reader/reader.rs` imports `SCAN_LOCK_READ_TIME_VEC` and `ScanLockReadTimeSource` to observe time spent holding the in-memory pessimistic-lock table read guard.

## Risks and Edge Cases

- Registration uses `.unwrap()`, so duplicate metric registration at process initialization would panic. This is normal for TiKV statics but important for tests that isolate registries poorly.
- Label sets are fixed at compile time. New MVCC behaviors need corresponding enum additions or they will be folded into existing labels elsewhere.
- The metric description for `MVCC_PREWRITE_REQUEST_AFTER_COMMIT_COUNTER_VEC` contains a spelling typo in `TxnStatucCache`; this is cosmetic but part of exported metadata.
- Histograms with broad exponential buckets are stable but coarse at high values.

## Test Signals

This file has no local tests. Coverage is indirect through compilation of generated static metric accessors and runtime use in transaction/reader tests that touch scan-lock and MVCC paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/mod.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/mod.rs

## Purpose

This is the MVCC module root. It declares MVCC submodules, re-exports the primary transaction/reader/checker APIs, defines the storage-layer MVCC error type and error-code mapping, provides default-value-missing critical handling, and contains test helpers used across transaction and reader tests.

## Important APIs, Types, and Functions

- Submodules: `consistency_check`, `metrics`, `mvcc_read_tracker`, `reader`, and `txn`.
- Public re-exports include MVCC keys/locks/writes from `txn_types`, consistency-check and MVCC-info scanners, reader APIs, transaction APIs such as `MvccTxn`, and selected histograms.
- `ErrorInner` is the central MVCC error taxonomy. It covers engine/IO/codec errors, lock conflicts, committed/rollback states, missing locks, write conflicts, deadlocks, assertions, commit timestamp validity, pessimistic lock failure reasons, flashback-era generation errors, shared-lock shrink-mode violations, and miscellaneous boxed errors.
- `Error` boxes `ErrorInner`, provides transparent error behavior, and supports `maybe_clone` for cloneable variants.
- `From` implementations convert storage KV errors, IO, codec, PD, and `txn_types` errors into MVCC errors.
- `ErrorCodeExt for Error` maps each MVCC error variant to the stable storage error code used by clients and telemetry.
- `default_not_found_error` increments the critical error metric, optionally sets a panic mark and panics depending on config, or logs a backtrace and returns `DefaultNotFound`.
- `PessimisticLockNotFoundReason` classifies why a pessimistic lock was not found.
- `tests` contains helper assertions and write/read routines such as `must_get`, `must_locked`, `must_written`, `must_get_commit_ts`, and shared-lock loading helpers.

## Control Flow

Normal MVCC code returns `Result<T> = std::result::Result<T, Error>`. Errors from lower layers are converted into `ErrorInner`, optionally cloned for retry or propagation, then mapped to a public error code when needed. The `default_not_found_error` path is intentionally special: default CF absence after a write record points to it is treated as data corruption or unexpected data loss, so it records `CRITICAL_ERROR` and either panics under strict config or returns a structured `DefaultNotFound`.

The test helper flow builds snapshots, constructs `SnapshotReader` or `MvccReader`, checks lock conflicts where needed, then asserts reads/writes/locks against encoded MVCC state.

## State and Persistence Behavior

The module root does not persist MVCC data directly. Its state effects are diagnostic: critical-error metrics, panic marks, logs with backtraces, and helper test writes through the storage engine. Persistent state is handled by transaction modules and readers re-exported here.

## Dependencies and Integration Points

This file is the integration boundary between `txn_types`, `kvproto`, `engine_traits`, error-code infrastructure, TiKV utility logging/panic behavior, storage KV abstractions, MVCC reader/txn modules, and raftstore consistency checking. Client-facing behavior depends on the exact `ErrorCodeExt` mapping, so changing variants or mappings affects RPC error contracts.

## Risks and Edge Cases

- `ErrorInner::maybe_clone` intentionally returns `None` for IO and opaque `Other` errors; callers must tolerate non-cloneable errors.
- The blanket `impl<T: Into<ErrorInner>> From<T> for Error` uses specialization-style `default fn`, so compiler/toolchain compatibility matters.
- `GenerationOutOfOrder`'s format string appears to use `{1:?}` for both key and lock text, which may make logs misleading.
- `default_not_found_error` can panic depending on runtime config; paths that call it are high-severity consistency assumptions, not ordinary missing-key cases.
- Test helpers assume shared locks are unsupported in several legacy single-lock assertion paths and use `unimplemented!` if encountered.

## Test Signals

Local content is mostly reusable test support rather than direct tests. It is exercised by MVCC transaction and reader suites that validate locking, commits, rollbacks, overlapped rollbacks, old value retrieval, shared locks, and error cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/mvcc_read_tracker.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/mvcc_read_tracker.rs

## Purpose

This file implements a process-local MVCC read activity tracker used to identify regions with high redundant MVCC version scans. It aggregates per-region scanned-version counts and request counts above a configurable threshold, then exposes versions-per-second throughput for compaction scoring.

## Important APIs, Types, and Functions

- `MVCC_READ_TRACKER: OnceLock<MvccReadTracker>` is the global tracker slot.
- `init_mvcc_read_tracker` initializes the global tracker with a `GcWorkerConfigManager`; repeated calls are ignored by `OnceLock::set`.
- `RegionMvccReadStats` stores `redundant_versions_scanned` and `total_requests` as `AtomicU64`.
- `RegionMvccReadStats::add_mvcc_versions` increments both counters with relaxed ordering.
- `MvccReadTracker` owns `Arc<DashMap<u64, RegionMvccReadStats>>`, a shared `reset_time_secs`, and the GC worker config tracker.
- `MvccReadTracker::record_read` checks `auto_compaction.mvcc_scan_threshold` dynamically and only records reads whose scanned version count is greater than the threshold.
- `get_mvcc_versions_scanned` returns total scanned versions divided by elapsed seconds since last reset.
- `reset_if_needed` clears all stats and updates the reset time; despite its name, it resets unconditionally.
- `tracked_region_count` and test-only `clear` expose map size and cleanup.

## Control Flow

Readers call `record_read(region_id, mvcc_versions_scanned)`. The tracker reads the current GC worker config, filters below-threshold reads, then inserts or updates a region's stats in the concurrent map. Compaction/scoring code calls `get_mvcc_versions_scanned`, which reads the atomic total for a region, computes elapsed wall-clock seconds from `reset_time_secs`, and returns integer throughput. A periodic compaction runner is expected to call `reset_if_needed` to start a new measurement window.

## State and Persistence Behavior

All state is in memory and shared across tracker clones through `Arc`s. Region counters live in `DashMap`; per-region counters are atomic. There is no persistence across process restarts and no write to the storage engine. Reset clears the whole map, losing all accumulated per-region samples for the previous window.

## Dependencies and Integration Points

The tracker depends on `dashmap` for concurrent per-region storage, `GcWorkerConfigManager` for the dynamic threshold, `OnceLock` for global initialization, and wall-clock `SystemTime`. It integrates with GC/auto-compaction configuration and is intended to feed compaction prioritization with observed MVCC scan pressure.

## Risks and Edge Cases

- `reset_if_needed` does not check time or config; callers must schedule it correctly.
- `SystemTime::duration_since(UNIX_EPOCH).unwrap()` assumes non-pre-epoch system time.
- Reads within the same second as reset return zero throughput because elapsed seconds is zero.
- Relaxed atomics are appropriate for approximate metrics, but not for strict accounting.
- `OnceLock` means tests or subsystems cannot replace the global tracker after first initialization in a process.
- The tracker stores one map entry per region that exceeds threshold during a window; very broad workloads may create many entries until reset.

## Test Signals

Tests cover atomic accumulation, throughput calculation with timing tolerance, non-resetting reads, manual clear, and threshold filtering. Tests build a `GcWorkerConfigManager` through `VersionTrack` and use short sleeps to force nonzero elapsed time.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/mvcc_read_tracker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/mod.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/reader/mod.rs

## Purpose

This file is the MVCC reader submodule facade. It wires together point gets, full MVCC readers, scanners, and small shared result/state types used by transaction commands to interpret write CF history.

## Important APIs, Types, and Functions

- Submodules: `point_getter`, `reader`, and `scanner`.
- Re-exports: `PointGetter`, `PointGetterBuilder`, `MvccReader`, `SnapshotReader`, `Scanner`, `ScannerBuilder`, `DeltaScanner`, `EntryScanner`, scanner utilities such as `has_data_in_range`, `near_load_data_by_write`, and `seek_for_valid_write`.
- `NewerTsCheckState` tracks whether a read path has not checked, has seen newer timestamp data, or has checked without seeing it. `PointGetter` uses it for newer-version detection and `RcCheckTs` behavior.
- `TxnCommitRecord` models the result of looking for a transaction's commit record: no record with optional overlapped write, a single matching write record, or an overlapped rollback embedded in another write.
- `OverlappedWrite` carries a write record plus GC fence for the case where another transaction's commit timestamp equals the current transaction's start timestamp.
- Convenience methods on `TxnCommitRecord` expose existence, `(commit_ts, WriteType)` info, and panic-on-wrong-variant unwrap helpers for internal/test use.

## Control Flow

The facade has little control flow of its own. It defines result shapes that `reader.rs` fills in `MvccReader::get_txn_commit_record`. Consumers can call `exist` for boolean status, `info` for command-level commit status, or unwrap helpers in code paths that have already established the expected variant.

## State and Persistence Behavior

No persistent state is owned here. The enums and structs are value types passed between reader and transaction logic. `OverlappedWrite` preserves enough write metadata to avoid overwriting an unrelated write when rolling back a transaction whose start timestamp collides with another transaction's commit timestamp.

## Dependencies and Integration Points

The module depends on `txn_types::{TimeStamp, Write, WriteType}` and integrates the concrete reader implementations with transaction status commands, cleanup/rollback logic, scanners, and tests. The `#[cfg(test)] pub use self::reader::tests as reader_tests;` export lets other MVCC tests reuse reader fixtures.

## Risks and Edge Cases

- `unwrap_*` helpers panic when called on the wrong variant, so production call sites should prefer `exist`/`info` or explicit matching unless invariants are already guaranteed.
- `TxnCommitRecord::None` can still contain `overlapped_write`; treating `None` as "safe to write rollback blindly" would be wrong.
- `OverlappedRollback` exists because rollback state can be encoded inside another transaction's write when timestamps overlap.

## Test Signals

Behavior is validated by `reader.rs` tests for normal commit lookup, pessimistic transaction ordering where commit timestamp and start timestamp order differ, overlapped writes, and overlapped rollbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/point_getter.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/reader/point_getter.rs

## Purpose

This file implements the optimized MVCC point-read path. `PointGetter` reads a single user key at a timestamp, checks lock conflicts when required, skips rollback/lock write records, honors GC fences, optionally reports newer timestamp data, supports read-through of selected locks, and gathers storage statistics.

## Important APIs, Types, and Functions

- `PointGetterBuilder<S: Snapshot>` configures snapshot, cache filling, value omission, isolation level, read timestamp, bypass/access lock sets, and newer-ts checking.
- `PointGetter<S>` stores the snapshot, read options, `NewerTsCheckState`, accumulated `Statistics`, and a prefix-seek write cursor over `CF_WRITE`.
- `get` returns `Option<Value>` for a user key.
- `get_entry` returns `Option<ValueEntry>` and can load the visible commit timestamp when requested.
- `load_and_check_lock` uses `snapshot.get_cf(CF_LOCK, user_key)` for the common no-lock fast path, parses single/shared lock encodings, applies `txn_types::check_ts_conflict`, supports bypass locks, and can return an accessible committed lock for read-through.
- `load_data` seeks write CF to the visible version, handles newer-ts/RcCheckTs probing, skips rollbacks and locks, uses `LastChange` shortcuts when many lock records sit above the last PUT/DELETE, checks GC fences, and loads short/default values.
- `load_data_from_default_cf` performs direct `get_cf(CF_DEFAULT)` and raises `default_not_found_error` if a referenced default value is missing.
- `load_data_from_lock` reads a value directly from an accessible committed lock when the lock's value is visible but not committed in write CF yet.

## Control Flow

`get_entry` first checks locks under SI or `RcCheckTs`. If a conflict lock is in `access_locks` and commit timestamp is not requested, it reads through the lock. Otherwise it calls `load_data`. `load_data` optionally first seeks to `user_key@TimeStamp::max()` to detect newer committed data or implement `RcCheckTs`; for `RcCheckTs`, a newer commit timestamp produces a write-conflict error. It then seeks or near-seeks to `user_key@read_ts`, parses the write record, and loops until it finds a visible `Put`, a `Delete`, an absence marker, or exhaustion. `Lock` and `Rollback` writes may terminate early via `LastChange::NotExist`, jump by direct `get_cf` when `estimated_versions_to_last_change >= SEEK_BOUND`, or continue to the next write record.

## State and Persistence Behavior

The getter is read-only. It uses a snapshot and CF cursors, mutating only in-memory cursor position, statistics, and newer-ts state. It reads `CF_LOCK`, `CF_WRITE`, and `CF_DEFAULT`. It records read-key resource metering for visible puts and updates processed size for returned values.

## Dependencies and Integration Points

Dependencies include storage `Snapshot`, `CursorBuilder`, `Statistics`, `ScanMode`, `txn_types` key/write/lock structures, `TsSet`, `LastChange`, `tikv_kv::SEEK_BOUND`, isolation-level helpers, resource metering, and MVCC errors. It is the likely read path for batch/point get commands that do not require full scanner behavior.

## Risks and Edge Cases

- Prefix seek is safe only because the cursor is built with prefix seeking and callers use encoded `Key`; changing cursor semantics would require explicit user-key checks.
- `load_commit_ts = true` deliberately ignores `access_locks`, because lock records do not have a final commit timestamp.
- `RcCheckTs` currently treats any newer write record as conflict, with a TODO noting that newer `LOCK` or `ROLLBACK` write types might be skippable.
- Missing default CF data triggers critical error behavior and may panic under config.
- `LastChange` shortcut correctness depends on transaction write records preserving accurate last-change metadata, especially across upgrades and GC fences.
- Shared-lock parsing is delegated to `txn_types::check_ts_conflict`; conflict extraction assumes error results for single locks.

## Test Signals

Tests cover basic timestamp visibility, prefix seek isolation from neighboring keys, tombstone behavior, iterator lower bounds, lock conflicts, omitted values, latest-value semantics, bypass/access locks, newer-ts detection, GC fence filtering, `RcCheckTs`, skipping lock-only histories with `LastChange`, row checksum preservation, commit timestamp loading, and shortcut behavior above PUT and DELETE records with both below- and above-`SEEK_BOUND` lock chains.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/point_getter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/reader.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/reader/reader.rs

## Purpose

This file implements the general MVCC snapshot reader used by transaction commands, lock resolution, flashback reads, CDC old-value extraction, key scans, and test fixtures. It is broader than `PointGetter`: it manages cursors over all MVCC CFs, in-memory pessimistic lock table integration, transaction commit-record lookup, range scans, timestamp-filtered reads, and default CF value loading.

## Important APIs, Types, and Functions

- `SnapshotReader<S>` binds an `MvccReader<S>` to a transaction `start_ts` and exposes transaction-oriented wrappers such as `get_txn_commit_record`, `load_lock`, `key_exist`, `get`, `get_write`, `get_write_with_commit_ts`, `seek_write`, `load_data`, `get_old_value`, and `take_statistics`.
- `MvccReader<S>` stores the engine snapshot, statistics, optional CF cursors, range bounds, timestamp hints, scan mode, current key for prefix-seek reuse, fill-cache choice, region term/version, and flashback permission.
- `load_lock` checks the in-memory pessimistic-lock table first, then persisted `CF_LOCK`.
- `check_term_version_status` prevents stale in-memory lock-table reads by returning stale-command, epoch-not-match, or flashback-in-progress errors when snapshot context does not match lock table status.
- `scan_locks` merges in-memory pessimistic locks and persisted lock CF records in key order, deduplicating keys.
- `load_in_memory_pessimistic_lock_range` times read-lock hold duration with `SCAN_LOCK_READ_TIME_VEC`.
- `seek_write` finds the latest write record at or before a timestamp for a key.
- `get_write_with_commit_ts` skips `Lock`/`Rollback` records and uses `LastChange` direct-get shortcuts for long chains.
- `get_txn_commit_record` scans from `TimeStamp::max()` down to a start timestamp to handle pessimistic transaction commit-order inversions and overlapped rollback/write cases.
- `scan_locks_from_storage`, `scan_latest_user_keys`, `scan_keys`, `scan_values_in_default`, `get_old_value`, `set_range`, `set_hint_min_ts`, and `set_allow_in_flashback` support range and maintenance use cases.

## Control Flow

`SnapshotReader` delegates to `MvccReader` while supplying its transaction start timestamp as the GC fence limit for transactional reads. `MvccReader::seek_write` creates or resets a write cursor, near-seeks to `key@ts`, validates the found key belongs to the requested user key, and parses the write. `get_write_with_commit_ts` repeatedly calls `seek_write`, returning visible PUTs, treating DELETE as absence, and skipping LOCK/ROLLBACK records. When a LOCK/ROLLBACK says no prior change exists, it returns none; when `LastChange` indicates a distant prior PUT/DELETE, it does a direct `get_cf` instead of many `next` calls.

`get_txn_commit_record` scans all versions from max timestamp down because pessimistic transactions can commit out of start-ts order. It returns a matching record by `write.start_ts`, an `OverlappedRollback` if a record at `commit_ts == start_ts` carries one, or `None` with `OverlappedWrite` if another transaction's write occupies that timestamp and must not be overwritten.

`scan_locks` first reads matching in-memory locks, then storage locks, and merges the streams by key. Persisted shared locks can be filtered/truncated by individual shared-lock entries to respect limits.

## State and Persistence Behavior

The reader is read-only from the perspective of MVCC data. It reads `CF_DEFAULT`, `CF_LOCK`, and `CF_WRITE`, plus the in-memory pessimistic lock table exposed through the snapshot extension. It mutates only cursor positions, range/hint settings, statistics, and local flags. `load_data` may call `default_not_found_error` if persistent write/default CF state is inconsistent. Test fixtures in this file do write to engines, but production reader methods do not.

## Dependencies and Integration Points

The file depends on storage snapshot/cursor abstractions, `engine_traits` CF constants, `txn_types` MVCC encodings, raftstore lock-table structures, kvproto region errors, `tikv_kv::SnapshotExt` and `SEEK_BOUND`, scan-lock metrics, and MVCC transaction functions in tests. Integration points include prewrite/commit/cleanup logic, lock resolver and pessimistic rollback, flashback commands, CDC old value handling, scanner utilities, resource metering, and region snapshot bounds.

## Risks and Edge Cases

- Correctness depends on encoded-key ordering and timestamp-descending MVCC key layout.
- Prefix seek is reset when the current user key changes in non-scan mode; missing that reset could read the wrong key range.
- In-memory lock-table reads must honor term/version/flashback status or clients could receive false lock results after leader changes or region changes.
- `LastChange` shortcuts depend on accurate metadata across old versions, upgrades, rollbacks interleaved with locks, and delete records.
- Shared-lock limit handling must count individual locks, not just lock keys; tests explicitly guard this.
- `gc_fence_limit` must be supplied for transactional reads or GC-fenced historical data can be interpreted incorrectly.
- `get_txn_commit_record` must preserve overlapped writes/rollbacks to avoid corrupting another transaction's record during rollback.

## Test Signals

The extensive local test module covers timestamp table property filters, lost-delete prevention, commit-record lookup including overlapped and pessimistic ordering cases, `seek_write`, `get_write`, lock scans and shared-lock limits, latest user key scans, default data loading and missing-default errors, `get`, CDC old value extraction, prefix-seek/tombstone behavior, `LastChange` shortcuts after upgrade and across rollback interleavings, plus reusable region-engine fixtures for MVCC transaction setup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/reader.rs -->
