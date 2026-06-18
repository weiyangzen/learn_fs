# Research Group: subset-b-008820

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/utils.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/utils.rs

## Purpose
This file is the shared utility layer for TiKV backup-stream. It collects key encoding helpers, CF name normalization, backup metadata filename parsing, non-overlapping range indexing, raft command extraction, scheduler/error macros, backup-stream statistics recording, lock-filtering policy, async task waiting, read-throughput measurement, range predicates, sequential async file reading, compression writer dispatch, and redacted debug/log formatting for regions and key ranges.

## Important APIs, Types, And Functions
`wrap_key` converts raw user keys to MVCC encoded data keys with `txn_types::Key`. `cf_name` maps user/protobuf CF strings to `engine_traits` CF constants and reports invalid names as `ERR_CF`. `ParsedBackupMetaFileName` and `parse_backupmeta_filename` parse backupmeta file stems into `flush_ts`, `store_id`, min/max timestamp tags, and optional flags; the parser accepts reordered tags and rejects malformed ASCII/hex/tag layouts.

`SegmentMap<K,V>` stores non-overlapping half-open ranges in a `BTreeMap` keyed by range start. It supports insertion with overlap rejection, point lookup, interval lookup, and overlap detection. `request_to_triple` extracts put/delete raft command payloads into `(key,value,cf)`. `try_send!`, `debug!`, and `future!` are convenience macros for scheduler reporting, feature-gated debug logging, and opaque future signatures.

`FutureWaitGroup` tracks spawned async work via RAII `Work` handles and wakes all waiters when the running count returns to zero. `with_record_read_throughput` records read bytes using Linux thread IO stats when available, falling back to RocksDB `ReadPerfInstant`. `FilesReader` implements `AsyncRead` over a list of readers. `CompressionWriter`, `NoneCompressionWriter`, `ZstdCompressionWriter`, and `compression_writer_dispatcher` abstract local temp-file writing for uncompressed and zstd data. `debug_key_range`, `slog_region`, `debug_region`, and `debug_iter` centralize redacted diagnostics.

## Control Flow
Most helpers are leaf utilities, but several define small protocols. `parse_backupmeta_filename` validates the prefix, walks fixed-width tagged suffix chunks, stores tags in a `BTreeMap`, then requires the min-begin/min/max tags before returning a parsed struct. `SegmentMap::insert` rejects overlapping ranges before mutating the map; overlap checks first test whether the query start lies inside a prior range, then check the last range starting before the query end. `FutureWaitGroup::wait` uses a fast path for zero running work, registers a waker under a mutex, then rechecks the counter to avoid lost wakeups. `FilesReader::poll_read` advances to the next file only when the current reader produces no bytes.

## State And Persistence Behavior
The file has no durable state of its own. It defines in-memory state containers (`SlotMap`, `SegmentMap`, `FutureWaitGroup`) and local filesystem writers. `NoneCompressionWriter::done` flushes and calls `sync_all`; `ZstdCompressionWriter::done` shuts down the encoder and flushes the underlying buffer, relying on encoder shutdown for compressed stream finalization. Backupmeta parsing is pure but constrains persisted metadata naming consumed by later flush/checkpoint code.

## Dependencies And Integration Points
The module integrates with `engine_traits` CF names, RocksDB read performance counters, `tikv_util` logging/worker scheduling, `kvproto` backup/raft/region messages, `txn_types` key/lock types, `async_compression`, Tokio async IO, and backup-stream local modules (`Task`, `errors`, `router::TaskSelector`, metrics). The metrics helper records `CfStatistics` into `INITIAL_SCAN_STAT`; `handle_on_event_result` sends fatal backup-stream tasks through the scheduler when event recording fails.

## Risks And Edge Cases
The segment map assumes half-open ranges and disallows overlaps; callers needing overlapping intervals must not use it as a general segment tree. Empty end keys are treated as infinity in simple byte-range helpers, so callers must maintain the same convention. `FutureWaitGroup` can accumulate duplicate wakers if polled repeatedly before completion. Zstd `done` does not explicitly call `sync_all` on the file, unlike the uncompressed writer. `cf_name` reports unknown CFs but returns a sentinel string, so downstream code must ignore or reject `ERR_CF`.

## Test Signals
Inline tests cover redacted region/range formatting, range inclusion, backupmeta parser tag order and flags, malformed tag rejection, segment overlap behavior, heavy wait-group race patterns, read-throughput measurement, sequential `FilesReader`, and zstd/uncompressed compression writer round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/tests/failpoints/mod.rs -->
# sources/storage-engines/tikv/components/backup-stream/tests/failpoints/mod.rs

## Purpose
This file is the failpoint-backed backup-stream integration test module. It uses a custom failpoint test runner and the shared `suite.rs` harness to verify recovery and correctness under injected failures in task registration, observation startup, initial scanning, region refresh, retry abort, flush/resolve races, encryption, fatal error handling, and force-flush concurrency.

## Important APIs, Types, And Functions
The module reexports the shared suite and defines tests inside `mod all`. Tests use `SuiteBuilder`, `Suite`, `run_async_test`, key constructors, `mutation`, metadata clients/stores, `Task`, `RegionCheckpointOperation`, `RegionSet`, `TaskSelector`, `PauseStatus`, failpoint configuration APIs, and walkdir inspection. Notable scenarios include `failed_register_task`, `basic`, `frequent_initial_scan`, `initial_region_scan_does_not_deadlock_when_operator_queue_fills`, `region_failure`, `initial_scan_failure`, `failed_during_refresh_region`, `test_retry_abort`, `failure_and_split`, `memory_quota`, `resolve_during_flushing`, `commit_during_flushing`, `encryption`, `failed_to_get_task_when_pausing`, `fatal_error`, and `pending_flush_when_force_flush`.

## Control Flow
Each test builds a simulated TiKV cluster, registers a backup stream task through metadata, injects failpoints at a specific backup-stream stage, performs writes/splits/leader changes/flushes, and then validates either flushed data or control-plane state. The tests generally follow the pattern: prepare data, register task, trigger failure or race, wait for suite synchronization/flush completion, then assert recovered output or uploaded metadata. Retry-oriented tests remove pause/error metadata and verify that routers recreate task handlers after recovery.

## State And Persistence Behavior
The tests exercise both metadata state and file state. Metadata assertions inspect task last errors, pause status JSON/protobuf payloads, safepoints, global/region checkpoints, and task handler presence in routers. File assertions inspect flushed backup data under temp local storage and, for encryption, temporary files under the backup-stream temp directory. Several tests explicitly verify that checkpoints do not advance past unsafe timestamps during races and that fatal errors pause tasks and install GC safepoints.

## Dependencies And Integration Points
This module depends on the suite harness, backup-stream metadata store/client abstractions, task scheduler, region checkpoint operations, encryption configuration, failpoints, TiKV test cluster utilities, PD safepoint state, and external local backup file layout. It is a high-level integration point between raftstore observers, backup-stream endpoints, metadata persistence, flushing, region checkpoint resolution, and gRPC control APIs.

## Risks And Edge Cases
The tests are timing-sensitive: several use sleeps to allow retries, flushes, or resolve operations. They rely on failpoint names matching production code. Some race tests only prove expected behavior in the test cluster timing model. The encryption test verifies absence of plain zstd headers and raw values, but does not fully decrypt and authenticate every byte. The memory quota assertion samples a metric in a failpoint callback, so it catches large overages but may miss short transient spikes outside the callback.

## Test Signals
The file itself is a test signal collection for backup-stream resilience. It validates retry after observer/initial-scan failure, nonblocking region operator handoff, memory quota enforcement, flush/commit/resolve ordering, encrypted temp-file spill behavior, pause/error metadata shape, safepoint preservation after fatal errors, and idempotent force flush while a flush is pending.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/tests/failpoints/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/tests/integration/mod.rs -->
# sources/storage-engines/tikv/components/backup-stream/tests/integration/mod.rs

## Purpose
This file is the non-failpoint backup-stream integration suite. It validates normal and adverse cluster behavior for PiTR/log backup, including region splits, region metadata boundaries, large transaction ordering around initial scans, leader loss, async commit, checkpoint querying, upload cancellation, pessimistic locks, flush subscriptions, follower resolution, network partition safety, dynamic config changes, force flush, and monotonic flush timestamps across PD TSO failures.

## Important APIs, Types, And Functions
The module uses `SuiteBuilder`, `run_async_test`, record/split key helpers, backup-stream `Task`, `RegionCheckpointOperation`, `RegionSet`, `GetCheckpointResult`, `TaskSelector`, `utils::parse_backupmeta_filename`, PD client failure hooks, grpc flush subscription streams, and `WalkDir` metadata inspection. Helper functions `collect_all_current`, `collect_current`, and `collect_meta_filenames` support async stream assertions and backupmeta filename validation.

## Control Flow
Tests construct simulated clusters, optionally split regions or alter leaders, register stream backup tasks, perform transactional writes, force flushes, and verify produced files/checkpoints. Subscription tests collect flush events until expected counts or timeout. Network partition tests isolate a leader, force leader expiration, write unresolved data, flush, and assert emitted checkpoints do not pass the locked timestamp. TSO failure tests repeatedly invoke `flush_now`, inspect success/failure results, and compare generated backupmeta names.

## State And Persistence Behavior
The suite validates persisted backup data files and `v1/backupmeta` contents. `region_boundaries` parses metadata and checks region start/end keys and epochs for data files. `monotonic_flush_ts_across_pd_failure` ensures no metadata files are produced before any successful TSO allocation, then ensures later flushes continue with monotonic local flush timestamps even if PD TSO fails again. `flush_status_is_cleared_when_tso_allocation_fails` verifies in-memory flushing flags are reset and later flushes recover.

## Dependencies And Integration Points
The tests integrate backup-stream endpoints, raftstore region state, PD TSO and region APIs, gRPC `LogBackupClient`, TiKV transactional KV APIs, flush subscription protocol, backup-stream metadata naming utilities, and the local backup file reader/checker in the shared suite. They also use `IsolationFilterFactory` to simulate network partitions.

## Risks And Edge Cases
Several assertions are bounded by timeouts or sleeps and can be sensitive to slow CI. The checkpoint tests rely on the shared suite's global checkpoint approximation, which explicitly does not check full region consistency. Network partition safety hinges on the simulated isolation filter and unresolved lock pattern. The metadata monotonicity test assumes exactly two successful metadata files for the chosen workload.

## Test Signals
The integration suite provides strong behavioral coverage for split handling, region epoch metadata, split transactions with more than 1024 short-value mutations, leader failure continuity, async commit checkpoint blocking/unblocking, pessimistic lock nonblocking behavior, flush subscription event ranges, follower checkpoint resolution, network partition safety, online config semaphore resizing, and PD TSO failure recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/tests/integration/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/tests/suite.rs -->
# sources/storage-engines/tikv/components/backup-stream/tests/suite.rs

## Purpose
This file is the shared integration-test harness for backup-stream tests. It builds simulated TiKV clusters, starts backup-stream observers/endpoints and gRPC log-backup services, provides metadata-store error injection, writes transactional test data, forces flushes, computes checkpoint views, verifies flushed backup files, and wraps KV client operations with assertions.

## Important APIs, Types, And Functions
`SuiteBuilder` configures test name, node count, metadata-store error injection, backup-stream config mutation, and cluster config mutation. `Suite` owns endpoint workers, the `ErrorStore<SlashEtcStore>`, cluster, clients, observers, gRPC servers, and temp directories. Key helpers include `make_table_key`, `make_record_key`, `make_split_key_at_record`, and `make_encoded_record_key`. Data helpers include `write_records`, `write_records_batched`, `commit_keys`, `just_commit_a_key`, and `just_async_commit_prewrite`. Control helpers include `must_register_task`, `force_flush_files`, `force_flush_files_and_wait`, `run`, `sync`, `wait_with`, `wait_with_router`, `wait_for_flush`, and `must_shuffle_leader`. Verification helpers include `get_files_to_check` and `check_for_write_records`.

## Control Flow
`SuiteBuilder::build` creates a server cluster, installs backup-stream observers into coprocessor hosts, runs the cluster, starts endpoints with local temp paths and backup encryption managers, starts per-store gRPC log-backup services, and waits for metadata watches to initialize. `must_register_task` writes a `StreamTask` with a table range and waits until routers load it. Write helpers generate deterministic TiDB table/record keys, issue prewrite/commit RPCs to region leaders, and return encoded committed MVCC keys. Flush helpers schedule `Task::ForceFlush` and wait on channel completion.

## State And Persistence Behavior
The harness persists metadata into an in-memory slash-etcd-like store and backup files into temp directories. `simple_task` points storage to `flushed_files` and sets zstd compression. `get_files_to_check` parses `v1/backupmeta/*.meta`, extracts file groups and per-CF byte ranges, then `check_for_write_records` reads compressed data segments from data files, decodes stream events, matches write CF keys, follows long-value references into default CF, and rejects missing default entries. `global_checkpoint` queries all endpoints for region checkpoints and returns the minimum.

## Dependencies And Integration Points
The harness binds together backup-stream endpoint/service/resolver/observer/router modules, raftstore `CdcRaftRouter`, region info accessors, resolved-ts leadership resolver, encryption manager, test PD/client/raftstore infrastructure, TiKV transactional RPC clients, protobuf metadata, zstd decoders, and event iterators. It is the main integration boundary for both failpoint and normal backup-stream test modules.

## Risks And Edge Cases
`SuiteBuilder::build` uses a one-second sleep to avoid missing metadata watch updates; that is acknowledged as a harness limitation. `global_checkpoint` is a simplified minimum over endpoint checkpoint reports and does not fully validate region consistency. `check_for_write_records` allows extra keys but reports them, while missing expected keys/default entries fail. The file assumes local Unix sockets/paths and gRPC loopback availability.

## Test Signals
Because this is a harness, its signal comes through the integration tests that consume it. Inline assertions validate every KV prewrite/commit response has no region or key errors, flushes finish within 30 seconds, endpoint sync downcasts to the expected test endpoint type, and decoded backup files contain expected write/default CF records.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/tests/suite.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/Cargo.toml -->
# sources/storage-engines/tikv/components/backup/Cargo.toml

## Purpose
This manifest defines the TiKV `backup` component crate. It is an unpublished Rust 2021 crate that implements backup endpoint/service behavior, disk snapshot backup support, writers, metrics, errors, and utility code used by TiKV backup/BR paths.

## Important APIs, Types, And Functions
The manifest exposes feature wiring rather than Rust APIs. Default features enable RocksDB KV test engine and raft-engine test engine support through the workspace `tikv` crate. Additional features forward allocator, CPU portability/SSE, memory profiling, failpoint, and alternate test-engine selections to `tikv`.

## Control Flow
There is no runtime control flow in the manifest. Build-time behavior is controlled by feature selection. The crate depends on many workspace components and a few external crates; dev-dependencies add `rand`, `tempfile`, and Tokio test/time/macros.

## State And Persistence Behavior
The manifest controls which storage, encryption, and external-storage dependencies are compiled. It does not persist state itself, but its dependency graph enables backup code to interact with RocksDB engines, external storage backends, encryption metadata, Prometheus metrics, and Tokio runtimes.

## Dependencies And Integration Points
Key dependencies include `api_version`, `causal_ts`, `concurrency_manager`, `engine_traits`, `engine_rocks`, `external_storage`, `file_system`, `grpcio`, `kvproto`, `raftstore`, `resource_control`, `tikv`, `tikv_util`, `txn_types`, `tokio`, `prometheus`, and `thiserror`. This positions the crate at the integration point between BR RPCs, TiKV storage engines, raftstore region metadata, resource control, encryption, and object/local storage backends.

## Risks And Edge Cases
Feature forwarding means changes in workspace `tikv` feature names can break this crate. The default feature set is test-engine oriented, which is useful for component tests but should be understood when comparing production build profiles. The crate uses nightly-only Rust features in `lib.rs`, so toolchain compatibility matters.

## Test Signals
The manifest’s dev-dependencies support the extensive unit tests embedded in `endpoint.rs` and likely other backup modules. Feature flags such as `failpoints` and test-engine selections determine which test scenarios compile.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/disk_snap.rs -->
# sources/storage-engines/tikv/components/backup/src/disk_snap.rs

## Purpose
This module implements the server-side loop for preparing disk snapshot backup over a bidirectional gRPC stream. It manages snapshot backup lease updates, wait-apply requests for regions, reset/finish semantics, stream aborts, and conversion of raftstore/snapshot preparation failures into either stream-level RPC failures or protobuf region errors.

## Important APIs, Types, And Functions
`Env<SR>` carries a `SnapshotBrHandle`, a `PrepareDiskSnapObserver` rejector/lease gate, an active stream counter, and either an injected Tokio handle or a default runtime. `ResultSink` wraps `grpcio::DuplexSink<PResp>` and sends success responses, protobuf error responses, or aborts the stream. Internal `Error` variants distinguish uninitialized observer, expired lease, wait-apply aborts, and raftstore errors. `HandleErr` decides whether an error is returned as a gRPC status or a `errorpb::Error`. `StreamHandleLoop<SR>` owns pending wait-apply futures and an abortable pending future; `run` drives the request/response loop.

## Control Flow
Clients send `UpdateLease`, `WaitApply`, and `Finish` requests. `UpdateLease` validates initialization and extends the observer lease, returning whether the previous lease was valid. `WaitApply` first checks that the observer is initialized and currently rejecting normal writes; then it sends strict wait-apply requests to raftstore for each region and stores futures in `pending_regions`. `next_event` races incoming stream items, completed wait-apply futures, and server abort. Completed wait-apply futures emit `WaitApplyDone` responses or region errors. `Finish` resets the observer, sends a final lease result, closes the sink, and exits.

## State And Persistence Behavior
State is in-memory: active stream count, observer lease/rejector state, and pending region futures. Dropping `StreamHandleLoop` decrements `active_stream`. There is no durable persistence in this file. The lease state controls whether wait-apply requests are meaningful; expired leases abort the stream with `FAILED_PRECONDITION`.

## Dependencies And Integration Points
The module integrates with raftstore snapshot backup APIs (`PrepareDiskSnapObserver`, `SnapshotBrHandle`, `SnapshotBrWaitApplyRequest`, `SnapshotBrWaitApplySyncer`, `AbortReason`), `kvproto::brpb` prepare snapshot messages, `errorpb` region errors, grpcio duplex streaming, Tokio runtime/oneshot, and TiKV utility runtime/thread naming.

## Risks And Edge Cases
If the observer is uninitialized, the stream aborts as unavailable. If the lease expires, further wait-apply attempts abort the stream because the backup-side write rejection window is no longer valid. Wait-apply abort reasons are mapped best-effort; epoch mismatch and stale command receive structured fields, other reasons become messages only. Pending futures are scanned linearly and `swap_remove` changes completion order, which is acceptable for region wait responses but should be noted.

## Test Signals
No inline tests are present in this file. Behavior is likely exercised through service-level disk snapshot backup tests elsewhere. Important observable signals are active stream count, gRPC status codes, response event types, and errorpb fields for epoch mismatch or stale command.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/disk_snap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/endpoint.rs -->
# sources/storage-engines/tikv/components/backup/src/endpoint.rs

## Purpose
This module is the core TiKV backup endpoint. It translates `BackupRequest` messages into region-range backup work, scans transactional MVCC or raw KV data from local snapshots, writes SST files through backup writers, persists them to external storage, sends `BackupResponse` messages, adapts worker concurrency, and reports metrics/errors.

## Important APIs, Types, And Functions
`storage_backend_config` converts online `BackupConfig` to external-storage backend options. `Task::new` validates CF names, builds a cancellable `Request`, sets rate limiting, request origin, lock bypass/access sets, raw/API version flags, compression, encryption cipher, and resource-control metadata. `BackupRange` represents one region-bounded scan. `KvWriter` abstracts transactional and raw writers. `InMemBackupFiles` carries a built writer plus response metadata to IO workers. `save_backup_file_worker` persists files and sends responses. `BackupRange::backup` scans MVCC entries through `SnapshotStore` and `TxnEntryScanner`; `backup_raw` and `backup_raw_kv_to_file` scan raw KV snapshots.

`ConfigManager` applies online backup config changes. `SoftLimitKeeper` adjusts a `SoftLimit` based on CPU statistics and config. `Endpoint` owns worker/io runtimes, engines/tablets, region info, config, concurrency manager, API version, causal timestamp provider, and optional resource control. `Progress` slices requested key ranges/subranges into leader or replica `BackupRange`s. Public exports include `Endpoint`, `Task`, `backup_file_name`, and `storage_backend_config`.

## Control Flow
`Runnable::run` rejects pre-canceled tasks and calls `handle_backup_task`. `handle_backup_task` constructs a `KeyValueCodec`, validates API-version compatibility, flushes causal timestamps for raw KV, builds progress, creates external storage, resizes worker runtime, and spawns `num_threads` scan workers plus IO save workers connected by a bounded channel. Each scan worker repeatedly obtains a soft-limit guard, advances shared `Progress`, checks cancellation, resolves a tablet and backup file name, then scans either raw KV or transactional MVCC. Transactional backup updates max-ts, performs lock checks for leader reads or read-index context for replica reads, takes a snapshot, scans batches, splits SST writers when needed, and sends completed writers to IO. Raw backup uses cursor scans, TTL filtering, API-version key/value conversion, and raw MVCC snapshot wrappers when needed.

## State And Persistence Behavior
Endpoint state includes resizable worker pools, IO runtime, mutable online config, soft-limit permits, local tablets, and a shared progress cursor per task. Persistence is external: built SST files are saved through `ExternalStorage` implementations, and responses carry file metadata with converted key ranges, versions, API version, sizes, and checksums. Backup file names encode store id, region id, epoch, optional start-key hash, and timestamp; S3/local layouts use store-id directory prefixes. Metrics record scan/snapshot durations, range sizes, errors, writer wait time, raw expired values, thread pool size, and soft limits.

## Dependencies And Integration Points
The endpoint integrates with TiKV storage snapshots, MVCC scanners, raw KV encoding, raftstore region info, concurrency manager lock/max-ts checks, resource-control limiters, external storage backends, encryption cipher info, backup writers, online config, Prometheus metrics, causal timestamp providers, and `tikv_util` resizable runtimes. It also maps errors through `errors.rs` into BR protobuf errors.

## Risks And Edge Cases
Correctness depends on region epoch/leader state staying valid between progress slicing and snapshot acquisition; errors are returned for retry when not. Replica reads skip the explicit in-memory lock check but set snapshot context start_ts/ranges and still update max-ts with request-origin validation. The bounded save channel can backpressure scanners; metrics measure wait time. Raw API-version conversion only permits selected source/destination combinations. Cancellation is checked between ranges, not inside every low-level scan. IO worker count equals backup thread count even though they share one bounded receiver, so throughput and ordering are nondeterministic.

## Test Signals
Inline tests cover thread-pool resizing, storage config propagation, online GCP config changes, range and subrange slicing, replica-read inclusion of followers, lock bypass behavior, transactional backup file counts/checksums, raw backup API-version conversion and TTL expiry metrics, raw API v2 causal timestamp flush, scan error conversion for locks/not-leader/server-busy, cancellation before and during work, dynamic worker pool resizing, backup file naming by backend, and timestamp set conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/errors.rs -->
# sources/storage-engines/tikv/components/backup/src/errors.rs

## Purpose
This module defines the backup crate’s error type and conversion into BR protobuf errors. It centralizes how storage, transaction, region, IO, semaphore, codec, and cluster-id failures become client-visible `brpb::Error` values and backup error metrics.

## Important APIs, Types, And Functions
`Error` is a `thiserror` enum with variants for boxed generic errors, RocksDB string errors, IO, TiKV KV errors, engine-traits errors, transaction errors, cluster-id mismatch, invalid CF, semaphore acquire failure, closed channel, and codec errors. `impl From<Error> for ErrorPb` converts structured backup errors to protobuf response errors. `impl_from!` maps `String` into `Rocks`, and `From<async_channel::SendError<T>>` maps send failure to `ChannelClosed`. `Result<T>` aliases `std::result::Result<T, Error>`.

## Control Flow
The protobuf conversion pattern-matches nested TiKV error enums. Region request errors are recognized through nested `KvError`, `TxnError`, and `MvccError` wrappers and passed through as `region_error`, while metrics label the exact region failure kind when known. `KeyIsLocked` becomes a `kvrpcpb::KeyError`. KV timeouts become `ServerIsBusy` region errors with a message. Cluster-id mismatch fills `cluster_id_error`. Unknown cases become string messages.

## State And Persistence Behavior
The module has no durable state. It mutates Prometheus counters in `BACKUP_RANGE_ERROR_VEC` while converting errors, so error serialization has a metric side effect. That coupling means repeated conversions of the same error would increment counters repeatedly.

## Dependencies And Integration Points
It depends on `kvproto` BR/error/KV protobufs, TiKV storage KV/MVCC/transaction error internals, `engine_traits::Error`, `tikv_util::codec::Error`, Tokio semaphore acquire errors, `thiserror`, and crate metrics. It is consumed by endpoint and disk/save flows when setting `BackupResponse.error`.

## Risks And Edge Cases
The matching relies on nested boxed error shapes and the crate-level `box_patterns` feature. New TiKV error variants may fall into the generic `other` branch until explicitly handled, reducing retry precision. Timeout handling only matches `Error::Kv` timeouts, not every possible nested transaction timeout. Metric increments during conversion are useful but can make tests or callers sensitive to conversion count.

## Test Signals
There are no inline tests in this file, though a TODO notes error conversion testing. Endpoint tests exercise key-is-locked, not-leader, and timeout-to-server-is-busy conversion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/lib.rs -->
# sources/storage-engines/tikv/components/backup/src/lib.rs

## Purpose
This is the crate root for TiKV’s `backup` component. It declares the module graph, enables a nightly feature required by nested boxed error pattern matching, wires allocator support, and reexports the public backup API surface.

## Important APIs, Types, And Functions
The crate exposes modules `disk_snap`, `endpoint`, `errors`, `metrics`, `service`, `softlimit`, `utils`, and `writer`. Public reexports include `Endpoint`, `Task`, `backup_file_name`, `storage_backend_config`, `Error`, `Result`, `Service`, `BackupRawKvWriter`, and `BackupWriter`.

## Control Flow
There is no runtime control flow in this file. It determines which internal modules compile and which types/functions downstream crates can import directly from `backup`.

## State And Persistence Behavior
No state or persistence is implemented here. It enables allocator linkage through `tikv_alloc` and exposes modules that own backup state, storage writing, metrics, and service wiring.

## Dependencies And Integration Points
The crate root is the integration point for TiKV/BR code importing backup endpoint and service functionality. `#![feature(box_patterns)]` supports `errors.rs` conversions that destructure boxed nested errors.

## Risks And Edge Cases
The nightly feature makes the crate toolchain-sensitive. Only selected endpoint/error/service/writer items are reexported; consumers needing lower-level utilities must use module paths or add exports.

## Test Signals
No tests live in this file. Its behavior is validated indirectly by successful compilation and tests of the reexported endpoint/service/writer modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/metrics.rs -->
# sources/storage-engines/tikv/components/backup/src/metrics.rs

## Purpose
This module registers Prometheus metrics used by the backup component to observe backup range latency, output sizes, worker pool sizing, errors, soft limits, scanner backpressure, scanned KV counts/sizes, and raw KV TTL expiration.

## Important APIs, Types, And Functions
The file uses `lazy_static!` to define `BACKUP_RANGE_HISTOGRAM_VEC`, `BACKUP_RANGE_SIZE_HISTOGRAM_VEC`, `BACKUP_THREAD_POOL_SIZE_GAUGE`, `BACKUP_RANGE_ERROR_VEC`, `BACKUP_SOFTLIMIT_GAUGE`, `BACKUP_SCAN_WAIT_FOR_WRITER_HISTOGRAM`, `BACKUP_SCAN_KV_COUNT`, `BACKUP_SCAN_KV_SIZE`, and `BACKUP_RAW_EXPIRED_COUNT`.

## Control Flow
Metric registration occurs lazily on first access through Prometheus registration macros. Histograms use exponential buckets for range duration and range size. Counters/gauges are mutated by endpoint scanning, error conversion, writer behavior, and soft-limit updates.

## State And Persistence Behavior
The module maintains process-global metric collectors registered in Prometheus’s default registry. It does not persist data to disk; metric state lives in process memory and is scraped/exported by TiKV’s metrics subsystem.

## Dependencies And Integration Points
It depends on `prometheus` and `lazy_static`. Endpoint code observes snapshot/scan/raw-scan durations, thread pool size, soft-limit cap, scanner wait time, and raw expired count. `errors.rs` increments `BACKUP_RANGE_ERROR_VEC`. Writer/scanner modules likely update size/count histograms and counters.

## Risks And Edge Cases
Prometheus registration uses `.unwrap()`, so duplicate metric names in the same process would panic at first access. Label cardinality is intentionally small (`type`, `cf`, `error`), and callers should preserve that. A comment reminds maintainers to update Grafana dashboards when metrics change.

## Test Signals
There are no inline tests. Metrics are indirectly exercised by endpoint tests that update gauges/counters/histograms during backup, error, and raw TTL scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup/src/metrics.rs -->
