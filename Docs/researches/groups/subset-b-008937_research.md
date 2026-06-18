# subset-b-008937 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/backward.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/backward.rs

## Purpose

`backward.rs` implements TiKV's descending MVCC key-value scanner, exposed as `BackwardKvScanner<S>`. It scans user keys in reverse order, merges write-CF versions with lock-CF state, applies timestamp visibility rules, and returns visible `(Key, ValueEntry)` pairs for normal transactional scans. It is selected by `ScannerBuilder::desc(true)` in `mod.rs`.

The scanner is optimized for RocksDB iterator behavior. It avoids immediate reverse seeks through a bounded `prev()` loop (`REVERSE_SEEK_BOUND`) and only falls back to seek-like operations when a key has many versions. It also lazily creates a default-CF cursor only when a visible value is not embedded as a short value in the write or lock record.

## Important APIs, Types, And Functions

- `BackwardKvScanner<S: Snapshot>` stores `ScannerConfig`, optional lock cursor, write cursor, lazy default cursor, `is_started`, `Statistics`, and `NewerTsCheckState`.
- `BackwardKvScanner::new` initializes cursors and sets `met_newer_ts_data` to `Unknown` unless newer-ts checking was enabled, in which case it starts at `NotMetYet`.
- `read_next` is the public scanner step. It initializes reverse cursor positions, repeatedly chooses the next highest user key across lock and write CFs, checks locks first, resolves a visible write version, records statistics and resource-metering, and returns one entry or end-of-scan.
- `reverse_get` resolves the visible write for one user key at `cfg.ts`. It tracks the last visible `Put`/`Delete`, detects newer committed versions, raises `RcCheckTs` conflicts, and switches between bounded reverse iteration and targeted seeks.
- `handle_last_version` converts a saved `Write` into an optional `ValueEntry`, honoring GC fence state and deletes.
- `reverse_load_data_by_write` returns an empty value for `omit_value`, a write short value when present, or lazily reads default CF with `near_reverse_load_data_by_write`.
- `move_write_cursor_to_prev_user_key` skips remaining versions for the current key using bounded `prev()` calls and then `internal_seek_for_prev` when the version chain is long.
- `ensure_default_cursor` creates the default-CF cursor using `ScannerConfig::create_cf_cursor(CF_DEFAULT)` only on demand.

## Control Flow

On the first `read_next`, the scanner positions both write and lock cursors at the upper bound with `reverse_seek`, or at the physical last key with `seek_to_last` when the scan is unbounded. Each loop iteration compares the current write user key, after stripping its MVCC timestamp, with the current lock key. Because the scan is descending, the larger user key wins. If both cursors point to the same user key, the lock is handled first.

Lock handling runs only when the configured isolation level requires lock checks. The scanner parses a lock or shared-lock payload, marks `met_newer_ts_data` when applicable, and calls `txn_types::check_ts_conflict`. A lock conflict normally becomes an MVCC error, but when `access_locks` contains the lock start timestamp and `load_commit_ts` is disabled, the scanner reads through `Put` or `Delete` locks through `load_data_by_lock`. When a lock is consumed, the lock cursor moves backward.

Write handling calls `reverse_get`. The write cursor initially points at the newest encoded write for the selected user key in descending user-key order, which is the smallest commit timestamp for that user key from the reverse iterator's perspective. `reverse_get` walks backward across encoded write keys, saving the newest visible `Put` or `Delete` found so far. If it sees a commit timestamp greater than the read timestamp, it records newer data and may throw `WriteConflictReason::RcCheckTs`. If the bounded loop cannot prove the latest visible version, it seeks to `user_key@ts` and walks forward through write records until it reaches already-checked territory.

After a write is resolved, `read_next` calls `move_write_cursor_to_prev_user_key` unless `reverse_get` already crossed into the previous user key. A returned `ValueEntry` increments write processed-key counters, processed size, and read-key metering.

## State And Persistence Behavior

The scanner itself is in-memory and does not mutate MVCC data. Its persistent effects are limited to storage-engine reads and metrics/statistics. It keeps cursor state between calls, so each `read_next` resumes where the previous call left off. `take_statistics` drains accumulated counters. `met_newer_ts_data` is sticky once it reaches `Met`; it remains `Unknown` unless explicitly enabled by the builder.

The default-CF cursor is intentionally lazy because many rows can be served from write-CF short values or filtered out by deletes, locks, and timestamp checks. When created, it consumes the builder's default-CF range bounds through `ScannerConfig`.

## Dependencies And Integration Points

This file depends on `engine_traits::CF_DEFAULT`, `kvproto` isolation and conflict reason enums, `txn_types` key/write parsing, and storage abstractions such as `Cursor`, `Snapshot`, `Statistics`, and `SEEK_BOUND`. It uses helper functions from `scanner/mod.rs`, especially `near_reverse_load_data_by_write` and `load_data_by_lock`.

It integrates with `ScannerBuilder::build` through the `Scanner::Backward` enum variant, and through the store-level `Scanner` trait implementation in `mod.rs`. It shares lock conflict semantics with point gets and forward scanning through `txn_types::check_ts_conflict` and TiKV isolation-level helpers.

## Risks And Edge Cases

- Reverse iteration relies on encoded MVCC key ordering and careful comparison between timestamped write keys and raw lock keys. Mistakes here can skip a user key or duplicate it.
- The `reverse_get` cursor can move in both directions after a targeted seek. The `last_checked_commit_ts` boundary is critical for not re-reading or missing versions.
- `RcCheckTs` currently treats newer `Lock` and `Rollback` write records as conflicts; comments note this could be refined.
- Accessing locks while `load_commit_ts` is enabled is intentionally disabled in the lock path, so callers expecting both should understand that lock read-through is bypassed.
- GC fence checks can suppress older writes even when the physical write record is present.
- Bound handling is asymmetric by direction: descending scans use the upper bound for the initial reverse seek and stop through cursor range constraints.

## Test Signals

The in-file tests cover dense version chains, rollback/delete handling, cursor movement out of bounds, fallback to `seek_for_prev`, range behavior, many RocksDB tombstones, GC fence behavior, `load_commit_ts` with top lock writes, and `RcCheckTs` conflicts. Shared tests in `mod.rs` also exercise backward scanning for locks, bypass/access locks, newer-ts detection, RC lock skipping, old value hints, and commit-ts loading.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/backward.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/forward.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/forward.rs

## Purpose

`forward.rs` implements TiKV's ascending MVCC scanner framework. The central `ForwardScanner<S, P>` owns the cursor loop and delegates lock/write semantics to a `ScanPolicy`. This supports normal key-value reads, latest-entry replication style reads, and delta-entry reads from the same cursor machinery.

The file exports three scanner aliases: `ForwardKvScanner<S>` for visible key-value pairs, `EntryScanner<S>` for latest `TxnEntry` records after a timestamp, and `DeltaScanner<S>` for all commits/prewrites in a timestamp interval. It also provides test builders and fixtures used by scanner tests.

## Important APIs, Types, And Functions

- `ScanPolicy<S>` defines policy-specific `Output`, `handle_lock`, `handle_write`, and `output_size`.
- `HandleRes<T>` communicates policy results back to the shared loop: return an output, skip a key while preserving a user key, or move to the next loop iteration.
- `Cursors<S>` groups optional lock cursor, write cursor, and lazy default cursor. It provides `move_write_cursor_to_next_user_key` and `ensure_default_cursor`.
- `ForwardScanner<S, P>` stores `ScannerConfig`, cursors, start flag, statistics, policy, and newer-ts state.
- `ForwardScanner::read_next` initializes lower-bound positions, merges write and lock cursors by smallest user key, handles locks first, moves the write cursor to the read timestamp, delegates write resolution, and returns policy output.
- `move_write_cursor_to_ts` skips versions newer than `cfg.ts`, records newer data, raises `RcCheckTs` write conflicts, and falls back to a direct seek after `SEEK_BOUND` next steps.
- `LatestKvPolicy` returns visible `(Key, ValueEntry)` pairs. It handles lock conflicts, `access_locks`, short values, default-CF loads, `omit_value`, `load_commit_ts`, `LastChange` shortcuts, deletes, rollbacks, and GC fences.
- `LatestEntryPolicy` returns latest `TxnEntry::Commit` records with commit timestamp greater than `after_ts`, optionally including delete writes.
- `DeltaEntryPolicy` returns prewrite and commit entries in `(from_ts, cfg.ts]`, supports shared locks, and can compute `OldValue` when `ExtraOp::ReadOldValue` is requested.
- `scan_latest_handle_lock` is a shared lock handler for latest-entry style policies.
- `TxnEntryScanner` is implemented for `ForwardScanner` policies that output `TxnEntry`.
- `test_util::EntryBuilder` and `prepare_test_data_for_check_gc_fence` construct expected transactional entries and GC-fence fixtures.

## Control Flow

On first use, `read_next` seeks write and lock cursors to the lower bound or to first keys. In each loop it forms `current_user_key` from the smaller of the write user key and lock key. The write key must be truncated from its timestamped MVCC encoding, while the lock key is already a user key. If both exist for the same key, lock processing runs before write processing.

After lock handling, if a write exists, `move_write_cursor_to_ts` advances over versions whose commit timestamp is greater than the read timestamp. Bounded `next()` calls are preferred; direct seek to `user_key@cfg.ts` is used when the version chain exceeds `SEEK_BOUND`. If the cursor still points to the same user key, the active policy resolves the write.

`LatestKvPolicy::handle_write` loops through write records until it finds a visible `Put`, sees a `Delete`, exhausts the key, or a GC fence invalidates the record. `Lock` and `Rollback` records are skipped, with `LastChange` allowing a direct seek to the last value-changing version for long lock/rollback chains.

`LatestEntryPolicy` is similar but returns raw transactional entries and stops once the key's newest relevant commit is at or below `after_ts`. It can include deletes for consumers that need delete records.

`DeltaEntryPolicy` differs by returning multiple entries per key over successive calls. It may return a lock as `TxnEntry::Prewrite`, then later return commit entries for the same key. It advances the write cursor record-by-record, skips rollback and lock write records, loads default-CF values when needed, and uses `seek_for_valid_value` to attach old values for CDC-style reads.

## State And Persistence Behavior

The scanner maintains cursor positions across calls and does not write persistent data. It reads lock/write/default CFs from the supplied snapshot. `Statistics` accumulate seek, next, processed-key, and size counters until drained. `met_newer_ts_data` is updated when locks or newer commit versions are observed.

The default cursor is optional. Entry and delta scanner builders often create it eagerly because they may need raw default entries. Normal key-value scanning creates it lazily only after a visible non-short value or readable lock requires default-CF access.

## Dependencies And Integration Points

This file depends on MVCC data types from `txn_types`, including `Key`, `WriteRef`, `WriteType`, `Lock`, `LockType`, `OldValue`, and `LastChange`; on `kvproto` `ExtraOp`, `IsolationLevel`, and `WriteConflictReason`; and on TiKV storage abstractions `Cursor`, `Snapshot`, `Statistics`, and `SEEK_BOUND`.

It integrates with `ScannerBuilder` in `mod.rs`: normal forward scans use `LatestKvPolicy`, `build_entry_scanner` uses `LatestEntryPolicy`, and `build_delta_scanner` uses `DeltaEntryPolicy`. The `TxnEntryScanner` implementation lets entry and delta scanners feed transactional scan consumers. `resource_metering::record_read_keys` and statistics connect scanner behavior to TiKV observability.

## Risks And Edge Cases

- The shared loop assumes policy methods move relevant cursors correctly. A policy that returns the wrong `HandleRes` can stall, duplicate keys, or skip data.
- `DeltaEntryPolicy` can return more than one output per user key, so its cursor movement differs from latest-value policies and is more sensitive to off-by-one timestamp bounds.
- Lock handling for `LatestKvPolicy` can read through locks only when `access_locks` allows it and `load_commit_ts` is false.
- `RcCheckTs` conflicts are raised for any newer write record observed, including comments noting possible future skipping of newer `LOCK` or `ROLLBACK` records.
- `LastChange` seek shortcuts rely on correctly maintained version metadata. Bad metadata would affect both performance and possibly which version is reached first.
- Default-CF loading treats missing long values as corruption through shared helpers.

## Test Signals

The tests cover normal latest KV scans, entry scans, and delta scans. They verify range bounds, cursor out-of-bound behavior, fallback seeking after `SEEK_BOUND`, delete output options, `after_ts` filtering, GC fences, old-value reads, shared/prewrite lock output, long value loading from default CF, RC check-ts conflicts, and `LastChange` skipping. The `test_mess` delta test builds mixed locks, puts, deletes, rollbacks, short values, and long values across multiple timestamp windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/forward.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/mod.rs -->
# sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/mod.rs

## Purpose

`mod.rs` is the public assembly point for TiKV MVCC scanners. It wires forward and backward implementations into `ScannerBuilder`, defines shared scanner configuration, exposes the store-level `Scanner` enum, and provides helper functions for default-CF value loading, range probing, and old-value lookup.

The module is responsible for preserving a consistent scanner contract across normal reads, descending reads, entry scans, and delta scans. It centralizes options such as timestamp, isolation level, range bounds, fill-cache behavior, lock bypass/access sets, timestamp hints, newer-ts detection, and commit-ts loading.

## Important APIs, Types, And Functions

- `ScannerBuilder<S>` is the user-facing builder. It supports `fill_cache`, `omit_value`, `isolation_level`, `desc`, `range`, `bypass_locks`, `access_locks`, `hint_min_ts`, `hint_max_ts`, `check_has_newer_ts_data`, and `set_load_commit_ts`.
- `ScannerBuilder::build` creates either `Scanner::Forward(ForwardKvScanner)` or `Scanner::Backward(BackwardKvScanner)`.
- `build_entry_scanner(after_ts, output_delete)` creates a forward `EntryScanner` with a default-CF cursor.
- `build_delta_scanner(from_ts, extra_op)` creates a forward `DeltaScanner` with default CF in mixed scan mode.
- `build_lock_cursor` skips lock-CF cursor construction when the isolation level does not require lock checks.
- `Scanner<S>` wraps forward/backward key-value scanners and implements the storage transaction `Scanner` trait.
- `ScannerConfig<S>` stores the snapshot and all scan options. `create_cf_cursor` and `create_cf_cursor_with_scan_mode` build CF cursors with correct range, cache, scan mode, and write-CF timestamp hints.
- `near_load_data_by_write` and `near_reverse_load_data_by_write` load long values from default CF using seek hints and validate exact default keys.
- `has_data_in_range` probes for any data in a CF range and treats RocksDB "too many internal keys skipped" as evidence that data likely exists.
- `seek_for_valid_write` and `seek_for_valid_value` locate the latest value-changing write and old value while skipping locks/rollbacks and honoring GC fences and timestamp filters.
- `load_data_by_lock` reads values represented by accessible locks, including lock short values and default-CF values.

## Control Flow

Builder methods mutate `ScannerConfig`. During scanner construction, lock and write cursors are created before default cursors. This ordering matters because `ScannerConfig::create_cf_cursor_with_scan_mode` consumes `lower_bound` and `upper_bound` when building the default-CF cursor, while lock and write CFs clone them.

Normal scans call `build`, which selects backward scanning when `desc` is true and forward scanning otherwise. Entry and delta scans are always forward and require default-CF access for raw `TxnEntry` output. Delta scanning uses `ScanMode::Mixed` for the default CF.

Default-value loading constructs `user_key@start_ts`, chooses near seek or normal seek from `Statistics::load_data_hint`, and then verifies both cursor validity and exact key equality. Failure returns `default_not_found_error`, signaling storage corruption or inconsistent MVCC state.

Old-value helpers are used by delta scanning and pessimistic/prewrite paths. `seek_for_valid_write` walks write records for a user key, skipping `Lock` and `Rollback` types and checking GC fences. `seek_for_valid_value` converts a valid `Put` into an `OldValue::Value`, converts deletes or missing writes into `OldValue::None`, and returns `OldValue::SeekWrite` when write-CF timestamp filtering means the real old value may have been filtered out.

## State And Persistence Behavior

`ScannerConfig` owns the read snapshot and scan options. It does not persist state beyond cursor construction, but it deliberately consumes default-CF bounds to avoid applying the same owned range multiple times. The created scanners hold cursor state and statistics between calls.

All helper functions are read-only against the snapshot. They mutate only cursors and statistics. `has_data_in_range` performs a bounded range probe and updates the caller-supplied CF statistics.

## Dependencies And Integration Points

The module depends on TiKV engine abstractions (`Cursor`, `CursorBuilder`, `Snapshot`, `Iterator`, `ScanMode`, `LoadDataHint`, `Statistics`, `CfStatistics`), engine CF names (`CF_DEFAULT`, `CF_LOCK`, `CF_WRITE`), MVCC helpers (`NewerTsCheckState`, `default_not_found_error`), transaction traits (`StoreScanner`, `TxnEntryScanner` indirectly through forward scanners), and MVCC data types from `txn_types`.

It is the integration point between storage transaction callers and concrete scanner implementations. `ScannerBuilder` is used by tests and production MVCC readers to construct scanners with consistent isolation and range semantics. The module also re-exports `DeltaScanner`, `EntryScanner`, and `test_util` from `forward.rs`.

## Risks And Edge Cases

- Default-CF cursor construction consumes range bounds. Adding new cursor creation paths must preserve the existing order or later cursors may get incorrect bounds.
- Timestamp hints apply only to write CF. Callers must be careful using `hint_min_ts` with old-value reads because filtering can force `OldValue::SeekWrite`.
- `near_load_data_by_write` panics by contract if called with a short-value write, and returns corruption errors for missing default data.
- `has_data_in_range` intentionally treats incomplete RocksDB results as positive, which is conservative for range existence but not a precise count.
- `load_data_by_lock` assumes conflict checking already ruled out lock types that cannot be read through; lock, pessimistic, and shared variants are unreachable there.
- Scanner trait methods wrap MVCC errors into transaction-layer results, so changes here affect read API behavior across forward and backward scans.

## Test Signals

The module-level tests validate builder-level behavior across forward and backward scanners: lock and write ordering, SI lock conflicts, bypass/access locks, newer-ts detection, old-value reads with write-CF timestamp hints, RC scans skipping locks, commit-ts loading, and top lock-version behavior across `SEEK_BOUND`. These tests complement the direction-specific test modules in `forward.rs` and `backward.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/mvcc/reader/scanner/mod.rs -->
