# sources/storage-engines/tikv/src/storage/mod.rs lines 1-7120

## Scope

This chunk covers the top-level `storage` module definition through the first raw batch delete test setup. It includes the public `Storage<E, L, F>` API surface for transactional reads, raw KV reads/writes/scans/checksum, scheduler dispatch, snapshot preparation, API-version validation, test builders, test utility callbacks, and tests from `test_prewrite_blocks_read` through the beginning of `test_raw_batch_delete_impl`.

The requested boundary ends at line 7120 in the middle of `test_raw_batch_delete_impl`, immediately after the second delete batch is invoked. Assertions after that invocation and later raw scan/API-version/lock tests are outside this chunk.

## Purpose

`storage/mod.rs` is TiKV's storage-layer facade. It binds together the engine abstraction, MVCC transaction logic, raw KV APIs, read pools, latch/scheduler write execution, lock-manager integration, resource metering, quota limiting, and test scaffolding. The module-level documentation states the main layering: `txn` lowers transactional commands onto MVCC, `mvcc` implements MVCC reads and writes, and `kv` abstracts persistent storage.

The central type in this chunk is `Storage<E, L, F>`, parameterized by an `Engine`, a `LockManager`, and an API/key format (`ApiV1`, `ApiV2`, or TTL-capable V1). `Storage` is cloneable and reference-counted; clones share the engine, transaction scheduler, read-pool handle, concurrency manager, resource tag factory, quota limiter, causal timestamp provider, and resource manager. Public methods then expose:

- MVCC point and range reads: `get`, `get_entry`, `batch_get_command`, `buffer_batch_get`, `batch_get`, `scan`, and `scan_lock`.
- Transaction command dispatch: `sched_txn_command` and raw atomic dispatch wrappers.
- MVCC destructive range cleanup: `delete_range`.
- Raw KV reads and writes: `raw_get`, `raw_batch_get_command`, `raw_batch_get`, `raw_put`, `raw_batch_put`, `raw_delete`, `raw_delete_range`, `raw_batch_delete`, `raw_scan`, `raw_batch_scan`, `raw_get_key_ttl`, `raw_compare_and_swap_atomic`, raw atomic batch put/delete, and `raw_checksum`.
- Support routines for snapshot context preparation, API-mode validation, key range validation, raw key locking for API V2 CDC timestamp ordering, and transaction status cache updates.

## Important APIs, Types, And Functions

- `Storage<E, L, F>` owns the active engine handle, `TxnScheduler`, read-pool handle, `ConcurrencyManager`, `max_key_size`, API version, `ResourceTagFactory`, optional causal timestamp provider, `QuotaLimiter`, and optional `ResourceGroupManager`.
- `Storage::from_engine()` constructs the scheduler with dynamic switches, flow controller, feature gate, causal timestamp provider, resource controller, resource manager, flow stats reporter, and transaction status cache. It asserts the runtime config API version matches `F::TAG`.
- `check_key_size!` is a local macro used before write scheduling to reject oversized keys through the user's callback.
- `Storage::snapshot()` wraps `kv::snapshot`, converting transaction/engine errors into `storage::Error`.
- `rawkv_cf()` enforces raw column-family rules: API V1/V1ttl allow default/lock/write CF names, while API V2 only accepts an empty CF and maps it to `CF_DEFAULT`.
- `check_api_version()` and `check_api_version_ranges()` enforce compatibility between storage API version, request API version, command kind, and key mode. API V2 accepts V1 requests only for transaction/TiDB keys, V2 raw commands only for raw keys, and V2 transaction commands only for txn keys.
- `prepare_snap_ctx()` updates the concurrency manager's max read timestamp for non-stale reads, checks in-memory locks for SI or RC-check-ts isolation, and attaches point key ranges for replica reads that need lock checking.
- `get_raw_key_guard()` and `get_causal_ts()` are API V2 raw-write helpers. They fetch a causal timestamp and place a synthetic raw-prefix lock in the concurrency manager so CDC resolved-ts cannot move beyond raw writes that are still being applied.
- `ResponseBatchConsumer<T>` abstracts per-request result delivery for server-side request batching. `GetConsumer` in `test_util` is the test implementation for transactional and raw batch get results.
- `TestStorageBuilder`, `TxnTestEngine`, and `TxnTestSnapshot` provide test-only storage construction, including a snapshot extension carrying `TxnExt` for in-memory pessimistic-lock tests and resource-controller tests.

## Control Flow

Most read APIs follow the same shape. The public method captures priority, resource-control metadata, an optional resource limiter, a resource tag, the current API version, and the request's busy threshold. It then submits an async task through `read_pool_spawn_with_busy_check()`. Inside the task, it records command counters, validates API version and key mode, checks deadlines where applicable, prepares a `SnapContext`, gets a snapshot through the TLS engine, builds a `SnapshotStore`, `PointGetter`, `MvccReader`, or `RawStore`, performs the actual read, records scan/read-flow/network/logical-read metrics, consumes quota samples for some MVCC reads, and returns a storage-level result.

Point MVCC reads use `get_entry()`. It converts `resolved_locks` and `committed_locks` from the request context into `TsSet`s, calls `prepare_snap_ctx()`, builds `SnapshotStore`, then calls `SnapshotStore::get_entry()`. `get()` is a thin wrapper that drops the optional commit timestamp metadata and returns only the value.

`batch_get_command()` is optimized for server request batching. It builds snapshots for every request first, releases the TLS engine snapshot handle after all requests are queued, then awaits each snapshot and sends per-ID results through `ResponseBatchConsumer`. It uses `PointGetterBuilder` rather than `SnapshotStore::batch_get()`, allowing each request to keep its own context, start timestamp, lock bypass/access sets, and `need_commit_ts` flag.

`batch_get()` handles a single request with many keys. It gets one snapshot, calls `SnapshotStore::batch_get()`, filters out missing keys, preserves the requested key order among returned entries, and aggregates per-key `Statistics`. `buffer_batch_get()` is specialized for pipelined-DML-style buffered locks: it sorts/deduplicates keys and reads only locks belonging to the same `start_ts`, returning put/delete lock contents rather than committed MVCC versions.

`scan()` handles forward and reverse MVCC range scans. For reverse scans it swaps `start_key` and `end_key` for internal lower/upper bound checks, updates max-ts and checks memory locks across the range, optionally attaches a replica-read key range, then constructs a `Scanner` from `SnapshotStore` and calls `scanner.scan(limit, sample_step)`.

`scan_lock()` does not allow replica read. It updates max-ts with request-origin checking, checks the in-memory lock table for locks at or below `max_ts`, then scans lock CF records through `MvccReader::scan_locks()`. Both normal locks and shared lock sets are converted into protobuf `LockInfo`.

Write-like transaction commands enter through `sched_txn_command()`. Before passing a `TypedCommand` to `TxnScheduler::run_cmd()`, it special-cases prewrite, pessimistic prewrite, flush, acquire pessimistic lock, and resumed acquire pessimistic lock to validate API version and key size. The scheduler owns latch ordering and command execution.

Raw non-atomic writes (`raw_put`, `raw_batch_put`, `raw_delete`, `raw_batch_delete`) run on the scheduler worker pool via `sched_raw_command()` but write directly through `kv::write()`. They check deadline, for API V2 verify causal-ts/max-ts synchronization with `check_causal_ts_flushed()`, acquire a raw key guard, fetch a causal timestamp, encode raw keys/values using `F`, build `Modify` records, mark the batch allowed on almost-full disks, and invoke the callback with the write result. API V2 raw delete is a logical delete (`ApiV2::ENCODED_LOGICAL_DELETE`) for single/batch delete; raw delete range remains physical.

Raw reads (`raw_get`, `raw_batch_get_command`, `raw_batch_get`, `raw_scan`, `raw_batch_scan`, `raw_get_key_ttl`, `raw_checksum`) build `RawStore` over a snapshot. They encode request keys to the configured raw format before engine access and decode returned keys back to user keys. `raw_batch_scan()` validates range direction with `check_key_ranges()` and treats an empty end key as either unbounded for the last range or the next range's start key for intermediate ranges. `raw_checksum()` only accepts `ChecksumAlgorithm::Crc64Xor`, encodes all ranges, and returns `(checksum, total_kvs, total_bytes)`.

Raw atomic operations (`raw_compare_and_swap_atomic`, `raw_batch_put_atomic`, `raw_batch_delete_atomic`) wrap raw operations into transaction scheduler commands (`RawCompareAndSwap` and `RawAtomicStore`) so they can serialize on scheduler/latch keys. Batch delete atomic intentionally does not encode a timestamp before constructing modifies because `RawAtomicStore` uses the key to generate locks.

## State And Persistence Behavior

Persistent state is ultimately stored by the engine column families. Transactional MVCC writes are handled by command implementations under `txn::commands`, while this chunk's storage facade validates and schedules them. `delete_range()` constructs `Modify::DeleteRange` entries for every data CF (`DATA_CFS`) and permanently removes all versions in the range, independent of timestamp. Raw non-atomic writes build `WriteData` batches with `Modify::Put`, `Modify::Delete`, or `Modify::DeleteRange` and send them to `kv::write()`.

Read state is snapshot based. The read pool provides a TLS engine handle, and every read gets an engine snapshot using a `SnapContext` carrying region/request context, optional start timestamp, optional read id, and replica-read lock-check ranges. For non-stale transactional reads, `prepare_snap_ctx()` advances the concurrency manager's max timestamp before snapshot acquisition; this prevents new conflicting in-memory locks from being hidden by an older read timestamp.

In-memory concurrency state matters for both reads and raw API V2 writes. Transactional reads check the in-memory lock table for SI/RC-check-ts before snapshot reads. `scan_lock()` checks both memory locks and persisted lock CF entries. Raw API V2 writes use causal timestamps and temporary raw-prefix locks so CDC resolved-ts can account for raw writes in flight. Tests assert `global_min_lock_ts()` returns `None` after raw operations complete, confirming guards are dropped.

Resource and telemetry state is also updated throughout the flow: command counters, priority counters, scheduler histograms, read-flow stats, scan details, network in/out bytes, logical read bytes, quota samples, and tracker fields such as `grpc_process_nanos`, read-pool schedule wait, and processed-key counts.

## Dependencies And Integration Points

- Engine abstraction: `kv::Engine`, `Snapshot`, `RocksEngine`, `WriteData`, `Modify`, and `kv::write`/`kv::snapshot`.
- MVCC layer: `SnapshotStore`, `MvccReader`, `PointGetterBuilder`, `Scanner`, `txn_types::{Key, Lock, LockType, TimeStamp, TsSet, ValueEntry}`.
- Scheduler layer: `TxnScheduler`, `TypedCommand`, `Command`, raw atomic command types, latches, lock manager, and transaction status cache.
- Concurrency layer: `ConcurrencyManager`, in-memory key/range lock checks, max-ts updates, and `KeyHandleGuard`.
- API versioning: `ApiV1`, `ApiV2`, `KvFormat`, raw key/value encoding, key mode parsing, TTL value encoding, and request `ApiVersion`.
- Server/request integration: kvproto `Context`, request priority, request source, replica-read settings, region/peer query collection, and protobuf `LockInfo`.
- Resource control and metering: `ResourceGroupManager`, `ResourceController`, `ResourceLimiter`, `TaskMetadata`, `ResourceTagFactory`, quota limiter samples, and resource-metering futures.
- Tests integrate with `MockLockManager`, `TestEngineBuilder`, `RocksEngine`, `TxnExt`, callback channels, and helper assertions from `mvcc::tests`/`txn::tests`.

## Risks And Edge Cases

- API-version and key-mode validation is security- and correctness-critical. Relaxing `check_api_version*` can allow raw keys through transaction APIs or transaction keys through raw APIs, especially in API V2 where prefixes encode key mode.
- Raw CF handling diverges sharply between API versions. API V2 rejects explicit CFs, while V1 allows `default`, `lock`, and `write`; callers relying on custom CF strings must be rejected before engine access.
- `batch_get_command()` assumes a non-empty request vector (`requests[0]`, random index). Upstream batching code must not call it with zero requests.
- Several raw read paths decode raw keys with `unwrap()` after engine reads. This depends on all scanned keys in range having been encoded by the selected `KvFormat`; mixed-format data or incorrect range encoding would panic.
- `buffer_batch_get()` expects only pipelined-DML optimistic locks and marks `Lock`, `Pessimistic`, and `Shared` lock types unreachable. Expanding its caller set without changing these assumptions would be dangerous.
- `prepare_snap_ctx()` checks in-memory locks before snapshot acquisition. Stale reads skip max-ts updates, so callers must set stale-read semantics only when the consistency contract permits it.
- `scan_lock()` intentionally avoids API-version checks for compatibility with TiDB GC worker region boundaries. That compatibility path makes its range handling broader than ordinary user-facing API validation.
- Raw API V2 delete semantics are split: point/batch delete are logical deletes for CDC, while delete range is physical. Consumers must not assume all raw delete forms have the same CDC visibility.
- `check_key_ranges()` treats empty intermediate range ends as the next range's start. Incorrect ordering or reverse-scan bounds return `Invalid KeyRanges`.
- `get_raw_key_guard()` uses a synthetic key built from raw prefix plus timestamp. The comment notes this prevents CDC resolved-ts from passing an in-flight raw write; reusing or omitting this timestamp would break that ordering constraint.
- The requested chunk ends before the raw batch delete test completes, so this research can identify setup and invocation coverage but not the post-delete assertions in the same test body.

## Test Signals

The in-chunk tests provide broad behavioral signals:

- `test_prewrite_blocks_read`, `test_get_put`, and `test_txn` verify lock conflicts, prewrite/commit visibility, old-timestamp reads, and write-conflict propagation.
- `test_cf_error` verifies that missing column families surface through get, scan, batch get, and batch get command paths.
- `test_scan` and `test_scan_with_key_only` cover forward/reverse MVCC scans, bounds, limits, sample steps, pre-commit lock-hidden values, committed values, and key-only scans with Titan-enabled Rocks options.
- `test_batch_get`, `test_batch_get_command`, and `test_batch_get_command_need_commit_ts` cover ordered batch results, per-request errors, returned commit timestamps, and `committed_locks` interactions.
- `test_sched_too_busy`, `test_high_priority_get_put`, and `test_high_priority_no_block` exercise scheduler pending thresholds and high-priority read/write behavior.
- `test_cleanup` and `test_cleanup_check_ttl` verify cleanup rollback behavior, TTL-based lock preservation, and concurrency manager max-ts update.
- Flashback tests (`test_flashback_to_version`, lock, multi-batch, deleted-key, retry-prepare) verify rollback/write phases over locks and committed versions, idempotence, batch limits, deleted-key behavior, and non-short values.
- `test_delete_range` confirms MVCC delete-range removes `[start, end)` across data CFs and preserves the exclusive end key.
- Raw tests through the boundary cover `raw_put`/`raw_get`, checksum range encoding, API V2 raw multi-version visibility, raw delete, raw delete range, raw batch put including TTL and atomic variants, raw batch get, raw batch get command, and setup plus invocation for raw batch delete in both normal and atomic forms.

Useful additional regression focus for this chunk would include empty batch inputs for batched command entry points, malformed API V2 raw ranges that decode incorrectly, explicit CF rejection in API V2 raw paths, quota/resource-limiter behavior under throttling, and CDC resolved-ts ordering around raw API V2 write failures.
