# Research: subset-b-008818

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/endpoint.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/endpoint.rs

## Purpose
`endpoint.rs` is the central actor for TiKV backup stream execution. It wires metadata watching, raftstore observation, initial scan scheduling, event routing, flush execution, checkpoint management, task pause/resume, and fatal-error reporting into one `Runnable` endpoint driven by `Task` messages.

## Important APIs, types, and functions
- `Endpoint<S, R, E, PDC>` owns `MetadataClient`, the internal `Scheduler<Task>`, a `Router` for temporary file/event handling, `BackupStreamObserver`, a Tokio runtime, `RegionSubscriptionManager` sender, PD client, `CheckpointManager`, and runtime state such as `last_flush_ts`, failover time, flush waiters, and abort handles.
- `Endpoint::new` constructs the runtime, starts periodic flush ticks, starts task and pause watchers, initializes memory/rate/concurrency controls for initial scans, starts region subscription management, starts checkpoint subscription management, and starts the min-ts worker.
- `Task`, `TaskOp`, `ObserveOp`, `RegionCheckpointOperation`, `RegionSet`, and `FlushResult` form the message protocol for the actor and its collaborators.
- `BackupStreamResolver` abstracts leader resolution for raftstore v1, raftstore v2, and tests.

## Control flow
Startup calls `start_and_watch_tasks`, which repeatedly loads metadata tasks until success, schedules active tasks, then spawns task and pause watch loops from the returned revision. Add/remove/pause/resume events become `Task::WatchTask`. Registering a task loads its ranges, registers them in the router, stores them in the observer range set, and initializes leader regions through `ObserveOp::Start`.

Raftstore command batches enter as `Task::BatchEvent`; `record_batch` checks that the region subscription and PITR handle are current, updates the two-phase resolver, converts the batch into `ApplyEvents`, and `backup_batch` asynchronously sends those events to `Router::on_events`. Out-of-quota events tell the region operator to handle high memory pressure, while stale observation is ignored.

Flushes are driven either by router ticks or explicit force flushes. `prepare_min_ts_and_flush_ts` obtains PD TSO and global min lock ts, falls back to a local monotonic flush ts only after at least one successful TSO, and calls `ObserveOp::ResolveRegions`. `on_exec_flush` freezes checkpoint manager state and runs `do_flush`, whose flush observer can rewrite resolved ts before router flush, then persists progress via the checkpoint observer.

## State and persistence behavior
Durable state is mainly delegated to metadata and PD: task info, ranges, pause markers, last errors, store checkpoints, and PD service safe points. Fatal errors call `on_fatal_error_of_task`, compute a safe point from global progress, set a per-store pause guard with a 24 hour TTL, write V2 pause JSON and last error metadata, then unload the task locally. Runtime-only state includes observed ranges, subscriptions, checkpoint manager state, flush waiters, last flush ts, semaphore capacity, and abort handles.

## Dependencies and integration points
This file integrates `MetadataClient`, `Router`, `BackupStreamObserver`, `RegionSubscriptionManager`, `InitialDataLoader`, `CheckpointManager`, `PdClient`, raftstore CDC handles, resolved-ts leadership resolution, `ConcurrencyManager`, and many backup stream metrics. It is the module re-exported by `lib.rs` for endpoint construction and external task/checkpoint operations.

## Risks and edge cases
- PD/metadata unavailability affects task watching, fatal error reporting, and TSO preparation; retries exist for watch startup and fatal error reporting, but skipped flushes can delay progress.
- `last_flush_ts` fallback is deliberately limited to avoid inventing a first timestamp without PD.
- The endpoint currently clears all observer ranges and subscriptions on unload because only one concurrent task is supported.
- Watch loops update `revision_new` by querying current revision after each event; gaps or repeated reconnects rely on store watch semantics.
- `on_force_flush` replaces any existing waiter for a task and reports an abort error to the older waiter.

## Test signals
This file has no local test module, but is exercised through observer, metadata, event loader, subscription manager, checkpoint manager, and service tests. Failpoints cover loading task ranges, flush delay, fatal error upload, and checkpoint update sleep paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/errors.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/errors.rs

## Purpose
`errors.rs` defines the backup stream error model, error-code mapping, contextual wrapping helpers, reporting helpers, and a small annotation macro used throughout the backup-stream crate.

## Important APIs, types, and functions
- `Error` covers logical backup-stream states (`NoSuchTask`, `ObserveCanceled`, `MalformedMetadata`, `OutOfQuota`) and wrapped subsystem failures from gRPC, protobuf, IO, TiKV transaction code, scheduler, PD, raftstore, encryption, and boxed miscellaneous errors.
- `impl ErrorCodeExt for Error` maps each variant to `error_code::backup_stream::*` codes, preserving the inner code for `Contextual`.
- `ContextualResultExt` adds eager and lazy context wrapping to `Result<T, E> where E: Into<Error>`.
- `ReportableResult` logs `Result<(), E>` failures through `Error::report`.
- `annotate!` converts arbitrary errors into `Error::Other` with formatted context.
- `Error::report`, `report_fatal`, `without_context`, and `context` centralize logging and metrics updates.

## Control flow
Most modules construct ordinary `Result<T, Error>` values. Callers add context near subsystem boundaries and call `report` or `report_if_err` when the error should be logged but not returned. Fatal endpoint paths call `report_fatal` before pausing tasks and writing metadata. `without_context` lets retry logic inspect the root cause, for example initial scan retry behavior.

## State and persistence behavior
The file has no durable state. Its side effects are logging and Prometheus counters: `STREAM_ERROR` and `STREAM_FATAL_ERROR` are incremented with the mapped error kind.

## Dependencies and integration points
It depends on subsystem error types from encryption, grpcio, PD client, protobuf, raftstore, TiKV transaction code, and worker scheduling. It also imports `Task` because `ScheduleError<Task>` is a concrete variant.

## Risks and edge cases
- `Error::Other` erases structured classification except for the generic `OTHER` code.
- The `annotate!` macro boxes string-formatted errors, so callers lose downcastable root types.
- `ReportableResult` only handles unit results; non-unit values still need explicit handling.
- Context strings can be constructed eagerly unless `context_with` is used.

## Test signals
Tests validate contextual formatting and error-code preservation. Benchmarks compare context construction costs for direct formatting, `format_args!`, lazy closure context, baseline error handling, and successful contextual calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/event_loader.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/event_loader.rs

## Purpose
`event_loader.rs` performs initial scanning for a newly observed region. It captures a consistent snapshot from raftstore/CDC, scans MVCC deltas from the region start checkpoint to infinity, converts them to `ApplyEvents`, tracks in-flight locks in the region resolver, and asynchronously sends batches to the backup stream router under memory, throughput, and concurrency limits.

## Important APIs, types, and functions
- `EventLoader<S: Snapshot>` wraps a `DeltaScanner`, region metadata, and a fixed-size `TxnEntry` buffer.
- `EventLoader::load_from` builds a delta scanner over the region key range with `hint_min_ts(from_ts)` and `fill_cache(false)`.
- `fill_entries` reads up to `ENTRY_BATCH_SIZE` entries and stops early when memory quota allocation fails or quota usage exceeds `SLOW_DOWN_INITIAL_SCAN_RATIO`.
- `emit_entries_to` converts `TxnEntry::Prewrite` and `TxnEntry::Commit` into `ApplyEvent`s and tracks eligible prewrite locks in `TwoPhaseResolver`.
- `InitialDataLoader<E, H>` owns the router sink, subscription tracer, scheduler, memory quota, rate limiter, CDC handle, and initial-scan semaphore.
- `capture_change`, `observe_over_with_retry`, `scan_and_async_send`, and `do_initial_scan` are the main initial scan pipeline.

## Control flow
`observe_over_with_retry` repeatedly calls `capture_change`, which registers a `ChangeObserver` through `CdcHandle::capture_change` and waits for a raftstore snapshot callback. Non-retryable region errors such as epoch-not-match, not-leader, stale observe id, and region-not-found stop retrying. After a snapshot is acquired, `do_initial_scan` takes a semaphore permit, constructs an `EventLoader`, and calls `scan_and_async_send`.

`scan_and_async_send` loops: it fills entries while measuring disk-read throughput, validates and mutates the current resolver through `with_resolver`, emits events, consumes rate-limit budget, increments metrics, and spawns an async router send that releases memory when complete. If scanning had to stop because of memory pressure, it joins outstanding send tasks before continuing.

## State and persistence behavior
No durable metadata is written here. Runtime state includes scanner position, buffered entries, memory allocations, joined router-send tasks, resolver lock state, and metrics. Persisted backup data is indirectly produced when `Router::on_events` stores events in temp files or downstream storage.

## Dependencies and integration points
This file bridges raftstore CDC capture, TiKV MVCC scanners, `SubscriptionTracer`/`TwoPhaseResolver`, backup stream `Router`, `Task` scheduler, memory quota, throughput limiter, and metrics. It is constructed by `Endpoint::new` and driven by `RegionSubscriptionManager`.

## Risks and edge cases
- The scan intentionally goes to `TimeStamp::max`, relying on downstream filtering and resolver state.
- Long scans can hold iterators; the semaphore and memory-pressure joins mitigate memtable and memory pressure.
- Resolver lookup also checks region epoch and observe handle id; stale scans are converted to `ObserveCanceled`.
- Shared locks are logged but not tracked, while ordinary locks can fail with `OutOfQuota`.

## Test signals
`test_disk_read` builds a test engine, writes committed data, compacts RocksDB, scans from zero to max, emits events, verifies nonzero events, and verifies measured disk reads are nonzero.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/event_loader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/lib.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/lib.rs

## Purpose
`lib.rs` is the crate root for TiKV backup stream. It declares internal and public modules, enables required nightly features, and re-exports the public construction and service types used by other TiKV components and integration tests.

## Important APIs, types, and functions
- Public modules: `config`, `errors`, `metadata`, `metrics`, `observer`, `router`, and `utils`.
- Private modules: `checkpoint_manager`, `endpoint`, `event_loader`, `service`, `subscription_manager`, `subscription_track`, and `tempfiles`.
- Re-exports: `GetCheckpointResult`, `BackupStreamResolver`, `Endpoint`, `ObserveOp`, `RegionCheckpointOperation`, `RegionSet`, `Task`, and `BackupStreamGrpcService`.

## Control flow
There is no runtime control flow in this file. It controls compile-time visibility and the public crate surface.

## State and persistence behavior
No state is held here. Persistence and runtime state are delegated to the modules it declares.

## Dependencies and integration points
The crate uses `#![feature(trait_alias)]` and `#![feature(test)]`, indicating nightly-only compilation. Re-exporting endpoint and service types makes this root the integration boundary for server setup, gRPC service wiring, and integration tests.

## Risks and edge cases
- Changing module visibility affects integration tests and downstream TiKV components.
- Publicly exporting `utils` for integration tests is called out as a temporary or imperfect boundary.

## Test signals
No direct tests. Compilation of downstream module tests validates that the root exports remain sufficient.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/checkpoint_cache.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/checkpoint_cache.rs

## Purpose
`checkpoint_cache.rs` provides a short-lived per-task cache for global checkpoints used by `MetadataClient::get_region_checkpoint` to avoid repeatedly scanning metadata when many region checkpoint lookups happen close together.

## Important APIs, types, and functions
- `CheckpointCache` stores `last_access`, the cached `checkpoint`, and `cache_lease_time`.
- `Default` sets the checkpoint to zero and the lease to 12 seconds, matching the coordinator tick interval noted in the comment.
- `update` records the current coarse time and monotonically raises the cached checkpoint with `max`.
- `get` returns `None` when the cached checkpoint is zero or the lease expired; otherwise it returns the cached `TimeStamp`.

## Control flow
The client creates caches through `DashMap::entry(...).or_default()`. Reads call `get`; misses fall back to metadata queries and then call `update`.

## State and persistence behavior
State is process-local only. It is intentionally lease-based and monotonic to avoid moving cached checkpoint values backward. Durable checkpoint data remains in metadata storage.

## Dependencies and integration points
It depends on TiKV coarse `Instant` and `txn_types::TimeStamp`. It is not public from `metadata::mod`, but is used internally by `MetadataClient`.

## Risks and edge cases
- A cached global checkpoint can hide newer metadata for up to the lease duration, trading freshness for reduced metadata load.
- Because updates use `max`, a caller cannot lower the cached value before expiry.
- The default zero checkpoint is treated as no cache entry.

## Test signals
`test_basic` uses a 100 ms lease to verify empty cache behavior, monotonic update from 42 over 41, and expiration after sleep.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/checkpoint_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/client.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/client.rs

## Purpose
`metadata/client.rs` is the high-level API over backup stream metadata. It serializes task, range, pause, checkpoint, storage checkpoint, and last-error data into the `MetaStore` key space and translates watch events into `MetadataEvent`s consumed by the endpoint.

## Important APIs, types, and functions
- `MetadataClient<Store>` wraps a generic `MetaStore`, current store id, and per-task `CheckpointCache`s.
- `StreamTask` combines `StreamBackupTaskInfo` with a computed `is_paused` flag.
- `MetadataEvent` represents task add/remove, task pause/resume, and watch errors.
- `CheckpointProvider` and `Checkpoint` model checkpoint sources from store, region, task start, or central global checkpoint.
- Pause support uses `PauseV2`, `Payload`, `RFC3336Time`, and `PauseStatus` to store V1 empty pause markers or V2 JSON containing protobuf-encoded backup errors.
- Main methods include `init_task`, task getters/watchers, pause/resume APIs, last-error APIs, storage/local checkpoint setters/getters, range reads, checkpoint aggregation, task insertion/removal test helpers, and `get_region_checkpoint`.

## Control flow
Task loading reads task protobufs under the task prefix and checks the pause key for each task. `events_from` and `events_from_pause` create store watches from `revision + 1`, filter raw key-value events into typed metadata events, and increment metadata event metrics. Pause with error serializes a V2 JSON payload and writes it before returning; fatal endpoint handling separately records last error.

Checkpoint reads parse all keys under the task checkpoint prefix. `global_checkpoint_of` returns a central task/global checkpoint immediately if present, otherwise selects the smallest store checkpoint and ignores region checkpoints. `get_region_checkpoint` first checks the short-lived global cache, then reads the region checkpoint key, then falls back to global checkpoint or task start ts.

## State and persistence behavior
Durable metadata is written through `MetaStore`: task info protobufs, range start-to-end mappings, pause keys, last-error protobufs, local store checkpoints, storage checkpoints, and checkpoint keys. Checkpoint values are big-endian `u64` timestamps. In-memory cache state is held in a `DashMap<String, CheckpointCache>` and is not authoritative.

## Dependencies and integration points
The client depends on protobuf `StreamBackupTaskInfo` and `StreamBackupError`, metadata `keys`, `MetaStore`, TiKV metrics, `chrono` for pause time, base64/serde JSON for PauseV2, and `txn_types::TimeStamp`. `Endpoint` uses it for metadata watch, task registration, pause/fatal error handling, range loading, and checkpoint persistence.

## Risks and edge cases
- `get_last_error` reads a prefix and returns the first key-value without explicit ordering semantics beyond store behavior.
- `pause_with_err` falls back to an empty value if JSON serialization fails, preserving pause semantics but losing rich error details.
- `parse_ts_from_bytes` requires exactly 8 bytes; malformed values fail hard.
- `init_task` relies on conditional transaction support, which the PD store adapter does not implement through the generic `txn_cond` method.
- The method name `next_bakcup_ts_of_region` is misspelled but forms part of the internal API.

## Test signals
Local tests validate checkpoint key parsing for store and region providers. `metadata/test.rs` validates task/range insertion, watch event conversion, progress aggregation, storage checkpoint keys, storage checkpoint round trip, and idempotent task initialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/keys.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/keys.rs

## Purpose
`metadata/keys.rs` defines the byte key layout for backup stream metadata under `/tidb/br-stream` and provides helpers for constructing, comparing, debugging, and decoding those keys.

## Important APIs, types, and functions
- `MetaKey(Vec<u8>)` is the typed key wrapper; `KeyValue(MetaKey, Vec<u8>)` is the metadata key-value pair.
- Key families include `/info`, `/checkpoint`, `/storage-checkpoint`, `/ranges`, `/pause`, and `/last-error`.
- Constructors include `tasks`, `task_of`, `ranges_of`, `range_of`, `next_backup_ts`, `next_backup_ts_of`, `next_bakcup_ts_of_region`, `storage_checkpoint_of`, `pause_prefix`, `pause_of`, `last_errors_of`, `last_error_of`, and `central_global_checkpoint_of`.
- `next` and `next_prefix` construct exclusive range ends for exact-key and prefix reads.
- `extract_name_from_info` and `extrace_name_from_pause` decode task names from watch keys.

## Control flow
Callers use constructors to create keys, then `Keys::into_bound` in `store/mod.rs` converts them to range bounds. Range records encode the task start key after the ranges prefix and store the end key as the value; `KeyValue::take_range` reverses that encoding.

## State and persistence behavior
This file defines the persistent path contract. Task info and error values are protobuf bytes, checkpoint/storage checkpoint values are big-endian `u64`s, pause values are empty or JSON, and ranges use binary suffix/value pairs.

## Dependencies and integration points
It depends on `kvproto::metapb::Region` for region checkpoint key generation and `tikv_util::codec::next_prefix_of` for prefix bounds. Every metadata client and store adapter depends on this layout.

## Risks and edge cases
- Task names are interpolated directly into path strings, so path separator handling depends on upstream task-name constraints.
- Region/store ids are encoded as decimal path segments despite comments mentioning big-endian ids in the older design note.
- The typo `extrace_name_from_pause` and `next_bakcup_ts_of_region` should be preserved unless all callers are migrated.
- Empty region end keys and arbitrary binary range start keys make range-prefix slicing sensitive to exact prefix length.

## Test signals
`metadata/test.rs::test_storage_checkpoint_of` asserts the storage checkpoint path. `metadata/client.rs::test_parse` verifies checkpoint paths generated here can be parsed back into `Checkpoint` values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/keys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/metrics.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/metrics.rs

## Purpose
`metadata/metrics.rs` registers Prometheus metrics for metadata operations, metadata watch events, and key-level operations in backup stream metadata code.

## Important APIs, types, and functions
- `METADATA_OPERATION_LATENCY` is a histogram vec labeled by operation type.
- `METADATA_EVENT_RECEIVED` is an event counter vec labeled by event type.
- `METADATA_KEY_OPERATION` is a counter vec for key operations, though the assigned source set does not show direct increments.

## Control flow
Metrics are lazily registered through `lazy_static!`. `MetadataClient` records operation latencies with `defer!` and increments event counters in `MetadataEvent::metadata_event_metrics`.

## State and persistence behavior
No durable state. The global Prometheus collectors are process-local observability state.

## Dependencies and integration points
Depends on `prometheus` and `lazy_static`. Integrated by `metadata/client.rs` and available inside the private `metadata` module.

## Risks and edge cases
- Metric names and label values are part of external observability contracts; renaming breaks dashboards and alerts.
- High-cardinality labels are avoided here by using operation/event type rather than task name.

## Test signals
No direct tests. Compile-time registration and use from `MetadataClient` provide basic coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/mod.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/mod.rs

## Purpose
`metadata/mod.rs` is the namespace root for backup stream metadata. It controls which metadata submodules are public and re-exports the high-level client types used by the rest of the crate.

## Important APIs, types, and functions
- Private modules: `checkpoint_cache`, `client`, and `metrics`.
- Public modules: `keys`, `store`, and `test`.
- Re-exports: `Checkpoint`, `CheckpointProvider`, `MetadataClient`, `MetadataEvent`, `PauseStatus`, and `StreamTask`.

## Control flow
There is no runtime control flow. The file defines compile-time module boundaries.

## State and persistence behavior
No state is held here; persistent metadata behavior lives in `client`, `keys`, and `store`.

## Dependencies and integration points
`Endpoint` imports the re-exported `MetadataClient`, `MetadataEvent`, `StreamTask`, and `store::MetaStore`. Integration tests can use `metadata::test` because that module is deliberately public under `cfg(test)` contents.

## Risks and edge cases
- `pub mod test` exists for integration-test ergonomics, but the file contents are guarded by `#![cfg(test)]`; changing this can break test-only consumers.
- Keeping `metrics` private centralizes metric use inside metadata, while making `keys` public exposes key layout helpers to other modules.

## Test signals
No direct tests. The metadata module tree is exercised by client, store, and endpoint-related tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/store/mod.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/store/mod.rs

## Purpose
`metadata/store/mod.rs` defines the generic metadata storage abstraction used by `MetadataClient`, plus transaction, key selection, revision, watch, and snapshot data structures. It also exposes the PD-backed and in-memory test store implementations.

## Important APIs, types, and functions
- `Transaction`, `TransactionOp`, and `PutOption` model write batches with put/delete operations.
- `Condition` and `CondTransaction` model compare-and-branch transactions.
- `WithRevision<T>` attaches a metadata revision to snapshot results and supports `map`.
- `Keys` selects exact keys, prefixes, or ranges and converts them into half-open byte bounds.
- `GetExtra` and `GetResponse` support descending order, limits, historical revision hints, and pagination flags.
- `Snapshot` provides `get_extra`, `revision`, and default `get`.
- `KvEvent`, `KvEventType`, `Subscription`, and `KvChangeSubscription` model cancelable watch streams.
- `MetaStore` defines `snapshot`, `watch`, `txn`, `txn_cond`, plus default `set`, `delete`, and `get_latest`.

## Control flow
High-level clients request `get_latest`, which obtains a snapshot then reads keys from it, preserving the snapshot revision for later watches. Watches return streams plus a lazy cancel future. Default `set` and `delete` lower to `txn`.

## State and persistence behavior
The abstraction itself holds no data. It defines the semantics concrete stores must provide: consistent snapshots, revisioned reads, watch streams from a revision, and atomic or conditional writes.

## Dependencies and integration points
It uses `async_trait`, `tokio_stream::Stream`, and the metadata key wrappers. `PdStore` and `SlashEtcStore` implement this trait; `MetadataClient` is generic over it.

## Risks and edge cases
- Not all concrete stores implement all trait methods meaningfully; `PdStore` returns unsupported errors for generic transactions.
- `GetExtra.rev` is defined but not honored by the visible store implementations in this subset.
- `Keys::Key` uses `key.next()` by appending a zero byte, relying on byte-range ordering to isolate one exact key.

## Test signals
No direct tests in this module. It is covered through PD store tests, SlashEtc-backed metadata tests, and client tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/store/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/store/pd.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/store/pd.rs

## Purpose
`metadata/store/pd.rs` adapts PD meta storage to the generic `MetaStore` abstraction for backup stream metadata. It supports PD get, put, prefix watch, and revision discovery.

## Important APIs, types, and functions
- `PdStore<M>` wraps a PD meta storage client.
- `convert_kv` converts `meta_storagepb::KeyValue` into metadata `KeyValue`.
- `PdWatchStream<S>` flattens PD `WatchResponse` batches into individual `KvEvent`s and converts PD/header errors into backup stream `Error`s.
- `RevOnly` is a snapshot that carries only a revision; point reads are not supported through `Snapshot::get_extra`.
- `MetaStore for PdStore<PD>` implements `snapshot`, prefix `watch`, unsupported `txn`/`txn_cond`, `set` via PD put, and `get_latest` via PD get.

## Control flow
`snapshot` performs a prefixed get on the metadata root with limit 0 to obtain a revision because point queries do not return one as needed. `watch` only accepts `Keys::Prefix`, constructs a PD watch from the requested start revision, wraps it in an abortable stream, and returns a cancel future. `get_latest` converts `Keys` into PD `Get` specs and maps the response key-values.

## State and persistence behavior
PD is the durable metadata backend. This adapter writes keys with `put` and reads current key state plus response revisions. It does not implement generic transaction APIs, so callers that require `txn` or `txn_cond` cannot use those paths against this adapter.

## Dependencies and integration points
Depends on `pd_client::meta_storage::{Get, Put, Watch, MetaStorageClient}`, `kvproto::meta_storagepb`, futures streams, and pin projection. Used by production metadata clients when backed by PD meta storage.

## Risks and edge cases
- `PdWatchStream::poll_next` asserts the internal buffer is empty before loading a new response; this matches the loop structure but assumes no reentrant buffer mutation.
- Watch supports prefixes only; exact-key/range watches return unsupported errors.
- `Snapshot::get_extra`, `txn`, and `txn_cond` are deliberately unsupported, creating an impedance mismatch with the full `MetaStore` trait.
- `get_latest` ignores the `more` flag because pagination is not implemented.

## Test signals
Tests use a mock PD meta storage server to verify exact and prefix query behavior, watch delivery/cancel behavior, source-check errors when the client lacks a log-backup source, and retry behavior under failpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/store/pd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/store/slash_etc.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/store/slash_etc.rs

## Purpose
`metadata/store/slash_etc.rs` implements an in-memory, revisioned metadata store used for tests and integration helpers. It emulates a small etcd-like key-value store with MVCC revisions, tombstones, range reads, watches, and conditional transactions.

## Important APIs, types, and functions
- `SlashEtc` holds a `BTreeMap<Key, Value>`, subscribers, current revision, and subscriber id allocator.
- `SlashEtcStore` is `Arc<Mutex<SlashEtc>>`.
- `Key(Vec<u8>, i64)` orders metadata keys by key bytes and revision.
- `Value` is either `Val(Vec<u8>)` or `Del` tombstone.
- `Snapshot for WithRevision<SlashEtcStore>` reads keys from a captured revision value, with optional descending order and limit.
- Internal `set` and `delete` allocate revisions, mutate MVCC entries, and send watch events.
- `MetaStore for SlashEtcStore` implements snapshots, watches, transactions, and conditional transactions.

## Control flow
Reads convert `Keys` to byte bounds, scan all matching MVCC entries, group by key, and return the latest non-tombstone value for each key. Writes allocate a new revision, notify overlapping subscribers, then insert a value or tombstone. `watch` first sends historical events with revision greater than or equal to `start_rev`, then registers a live subscriber whose cancel future removes it.

## State and persistence behavior
All state is in memory and process-local. Revisions are monotonic. Deletes create tombstones rather than removing old entries. Subscribers receive put/delete events for key ranges intersecting their watch bounds.

## Dependencies and integration points
This store implements the same `MetaStore` trait as PD store and is returned by `metadata/test.rs::test_meta_cli`. It depends on Tokio mutexes and mpsc channels.

## Risks and edge cases
- Snapshot reads store only the revision number but `get_key` reads current data rather than filtering by snapshot revision, so it is not a full historical MVCC snapshot.
- Pending historical watch events are sent while holding the mutex and can panic if more than channel capacity is pending.
- `txn_cond` compares `k.0.0` rather than the value bytes of the selected key, which may not match intended etcd compare semantics.
- Subscriber sends unwrap, so closed receivers can panic during set/delete.

## Test signals
This file has no local test module, but it is heavily exercised by `metadata/test.rs` for task/range/progress/watch behavior and by `metadata/client.rs` checkpoint parsing tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/store/slash_etc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/test.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metadata/test.rs

## Purpose
`metadata/test.rs` contains test-only helpers and integration-style tests for `MetadataClient` using the in-memory `SlashEtcStore`.

## Important APIs, types, and functions
- `test_meta_cli` creates a `MetadataClient<SlashEtcStore>` with store id 42.
- `simple_task` builds a `StreamTask` with name, start/end ts, noop storage backend, and wildcard table filter.
- `assert_range_matches` and `task_matches` compare decoded ranges and task sets.
- Tests cover basic range insertion, watch events, progress computation, storage checkpoint key format, storage checkpoint round trip, and idempotent initialization.

## Control flow
The tests write task info and ranges through `insert_task_with_range`, then read through public client APIs. Watch tests capture a revision from `get_tasks`, subscribe from the next revision, write and delete tasks, cancel the watch, and collect emitted events. Progress tests verify fallback to task start ts, local checkpoint updates, and behavior for another store with no checkpoint.

## State and persistence behavior
All persistence is in-memory through `SlashEtcStore`. The tests exercise durable key layout and value encoding logic as if it were persisted in a metadata backend.

## Dependencies and integration points
Depends on `kvproto::brpb` for task storage protobuf fields, Tokio tests, stream collection, `MetadataEvent`, metadata keys, and `SlashEtcStore`. These helpers support other crate tests because the module is public but cfg-test gated.

## Risks and edge cases
- The helpers use fixed store id 42 unless a test manually creates another client.
- Because the backing store is an approximation, tests may not reveal PD-specific unsupported transaction or pagination behavior.
- `task_matches` compares only task names, not all task fields.

## Test signals
The file itself is the test signal for metadata behavior. It validates task/range APIs, watch conversion to `MetadataEvent`, global progress selection, storage checkpoint path generation, storage checkpoint reads/writes, and `init_task` not rolling progress backward.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metadata/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metrics.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/metrics.rs

## Purpose
`metrics.rs` defines backup stream Prometheus metrics and helper functions for task status gauges.

## Important APIs, types, and functions
- `TaskStatus` encodes `Running`, `Paused`, and `Error` as increasing integers.
- `update_task_status` sets a task status gauge, allowing escalation to higher states and always allowing reset to `Running`.
- `remove_task_status_metric` removes a task label from the hidden `TASK_STATUS` gauge vec.
- Registered metrics cover actor message duration, initial scan reasons/statistics/disk reads/size/duration, event handling stages, errors/fatal errors, heap memory, checkpoint ts, flush duration/file size, upload bytes, skip counters, stream enabled, observed regions, pending initial scans, min-ts resolve duration, temporary file memory/count/swap/read duration, smallest checkpoint, active subscriptions, and static miscellaneous event counters.

## Control flow
Metrics are registered lazily at process startup on first use. Runtime modules update them around endpoint task handling, event loading, router operations, temp-file management, checkpoint manager operations, and observer/subscription logic.

## State and persistence behavior
Metrics are process-local observability state exported through Prometheus. They do not persist backup data, but dashboards and alerts may rely on their names, labels, and monotonic/counter semantics.

## Dependencies and integration points
Depends on `prometheus`, `prometheus_static_metric`, and `lazy_static`. It is imported by endpoint, errors, event loader, metadata, router, tempfiles, checkpoint manager, and observer-related code.

## Risks and edge cases
- Metric names and labels are an external compatibility surface for Grafana dashboards, as the file comment notes.
- `TaskStatus` uses max semantics across stores; incorrect reset or removal can mislead task-level status views.
- Some gauges are global rather than task-scoped, so concurrent tasks would need careful interpretation.

## Test signals
No direct tests. Compile-time metric registration and widespread runtime use provide integration coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/observer.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/observer.rs

## Purpose
`observer.rs` defines `BackupStreamObserver`, a raftstore coprocessor observer that watches apply, role, and region-change events and converts them into backup-stream endpoint tasks.

## Important APIs, types, and functions
- `BackupStreamObserver` stores the endpoint scheduler and an `Arc<RwLock<SegmentSet<Vec<u8>>>>` of task key ranges.
- `new` creates an observer for a scheduler.
- `register_to` installs command, role, and region-change observers into `CoprocessorHost` with fixed priorities.
- `should_register_region` checks whether a region overlaps registered task ranges, treating empty region end key as a synthetic infinity.
- `is_hibernating` returns true when no task ranges are registered.
- Implementations of `CmdObserver`, `RoleObserver`, and `RegionChangeObserver` schedule `Task::BatchEvent` or `Task::ModifyObserve` operations.

## Control flow
On command flush, only `ObserveLevel::All` batches are cloned and scheduled as `Task::BatchEvent`. When a region applies current term as leader and overlaps observed ranges, the observer schedules `ObserveOp::Start`. When a region leaves leadership and the observer is active, it schedules `ObserveOp::Stop`. Leader-side region destroy schedules `Destroy`; region update schedules `RefreshResolver`; create and bucket updates are ignored.

## State and persistence behavior
State is in-memory only: the observed task ranges are loaded by the endpoint from metadata. The observer does not persist data and does not directly manage subscriptions; it delegates all changes to the endpoint/region subscription manager through scheduled tasks.

## Dependencies and integration points
It integrates raftstore coprocessor traits, raft `StateRole`, `SegmentSet`, the backup-stream scheduler, `Task`, and `ObserveOp`. It is created by service wiring and owned by `Endpoint`.

## Risks and edge cases
- Command batches are cloned before scheduling; large batches have memory cost.
- Empty end key is approximated with 32 bytes of `0xff`, which is pragmatic but not a general infinity abstraction.
- If scheduler delivery fails, `try_send!` behavior determines whether events are only logged or dropped.
- Hibernation avoids noise when no tasks exist, but stale range state would suppress or admit observe operations incorrectly.

## Test signals
Tests validate observation cancellation through `ObserveHandle`, basic scheduling of start and batch events, ignoring non-overlapping regions and non-`All` observe levels, stopping on follower role changes, and hibernation suppressing role/region events.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/observer.rs -->
