# subset-b-008819 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/router.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/router.rs

## Purpose
`router.rs` is the core TiKV backup-stream write router. It turns raftstore apply batches into backup log events, filters and partitions those events by backup task ranges, writes them into local temporary log files grouped by table/region/CF/command type, and flushes merged log plus metadata files to the task external storage. It is also the task registry for stream backup jobs: it tracks task ranges, per-task temp-file pools, flush scheduling state, global checkpoints, task-scoped backup encryption, and online backup-stream config updates.

The file is persistence-critical for point-in-time recovery. It defines what KV changes are recorded, how local non-fsynced temp state becomes durable external-storage log and metadata objects, how retries preserve staged files, and when the endpoint is asked to advance or fail a task.

## Important APIs, Types, And Functions
`TaskSelector` and `TaskSelectorRef` select tasks by task name, key, overlapping range, or all tasks. `TaskSelectorRef::matches()` compares selectors against task names and registered encoded-key ranges and is reused by force flush, fatal error routing, and task queries.

`ApplyEvent` represents one recordable KV mutation with encoded key, value, column family, and raft command type. `ApplyEvents` is a region-scoped batch with helper methods for building from `CmdBatch`, sizing, grouping, range partitioning, and temp-file-key partitioning. `ApplyEvents::from_cmd_batch()` filters admin and error commands, converts supported raft requests through `utils::request_to_triple()`, tracks/untracks lock CF mutations in `TwoPhaseResolver`, skips unsupported requests, and records only `Put`/`Delete` in default/write CF.

`Router` is an `Arc` wrapper over `RouterInner`. `Config::from_backup_stream_config()` adapts `BackupStreamConfig` values into temp path, file-size limit, memory quota, flush interval, S3 multipart size, and GCP v2 flag. `RouterInner` owns `ranges: SegmentMap<Vec<u8>, String>`, `tasks: DashMap<String, Arc<StreamTaskHandler>>`, scheduler, runtime config atomics, and the default `BackupEncryptionManager`.

Task lifecycle APIs are `RouterInner::register_task()`, `unregister_task()`, `register_ranges()`, `unregister_ranges()`, `find_task_by_range()`, `get_task_by_key()`, `select_task_handler()`, `select_task()`, and `get_task_handler()`. `register_task()` builds task-specific temp-file config, task-specific backup encryption manager, external-storage backend config, creates a `StreamTaskHandler`, inserts it, then registers ranges. `build_backup_encryption_manager_for_task()` honors task security config with either plaintext data key or master-key config, falling back to the default manager when no override is present.

Event and flush APIs are `RouterInner::on_events()`, `on_events_by_task()`, `tick()`, `do_flush()`, and `update_global_checkpoint()`. `on_events()` partitions a region batch by registered ranges and concurrently appends each task partition. `on_events_by_task()` writes data and schedules `Task::Flush` when the per-task size crosses `temp_file_size_limit` and the handler can atomically acquire `flushing`. `tick()` schedules `Task::UpdateGlobalCheckpoint` for every task and also schedules interval-based flushes. `do_flush()` invokes the task handler flush, clears the flushing flag on success or failure, updates last flush time on success, and turns repeated failures over `FLUSH_FAILURE_BECOME_FATAL_THRESHOLD` into `Task::FatalError`.

`TempFileKey` groups events by table id, region id, CF, command type, and meta-key status. It also generates local temp names and external V2 paths such as `v1/{date}/{hour}/{store_id}/{min_ts}-{uuid}.log`, `schema-meta/...`, and backup meta file names. `StreamTaskHandler` is the per-task writer/flusher. Its key methods are `new()`, `on_events()`, `on_events_of_key()`, `move_to_flushing_files()`, `generate_backup_metadata()`, `flush_log()`, `merge_and_flush_log()`, `merge_and_flush_log_files_to()`, `flush_backup_metadata()`, `do_flush()`, `clear_flushing_files()`, `flush_global_checkpoint()`, `update_global_checkpoint()`, `build_unpin_reader_with_encryption_if_needed()`, and `update_data_file_metadata()`.

`DataFile` wraps a temp writer with metadata accumulation: min/max event ts, resolved ts, minimum begin ts for write CF, plaintext SHA256, CRC64 xor, key bounds, entry count, file size, and compression type. `DataFile::on_events()` encodes KV events with `EventEncoder`, writes them to the temp file, updates checksums and metadata, decodes write-CF begin ts, and advances key bounds. `DataFile::generate_metadata()` finalizes the plaintext SHA256 and produces `DataFileInfo`. `MetadataInfo` accumulates flushed `DataFileGroup`s and marshals the V2 `Metadata` proto.

## Control Flow
The event path starts in raftstore observation code that supplies a `CmdBatch` and a region `TwoPhaseResolver`. `ApplyEvents::from_cmd_batch()` extracts supported KV operations, updates resolver lock state from lock-CF operations, and produces a region batch. `RouterInner::on_events()` records batch size metrics, partitions events by the current task-range `SegmentMap`, and calls `on_events_by_task()` for each matching task. Events that do not fall into a registered task range are dropped by omission from the partition map.

Within a task, `StreamTaskHandler::on_events()` partitions events by `TempFileKey`. `on_events_of_key()` first tries to reuse an existing temp `DataFile` under `files`; if absent it takes the write lock, double-checks, creates a new `DataFile` with a unique local temp name, and appends the events. The handler atomically increments `total_size` by encoded bytes written. After each task append, the router compares `total_size` with the size limit. If the task is not already flushing, it CASes `flushing` from false to true and schedules `Task::Flush(task)`.

The flush path is deliberately staged for retry. `StreamTaskHandler::do_flush()` returns immediately if `flushing` is false. Otherwise it calls `move_to_flushing_files()`, which drains `files` into `flushing_files` and `flushing_meta_files` only when the flushing lists are empty. While moving, it finalizes each file's metadata exactly once because checksum finalization is destructive. If a previous flush failed, the flushing lists remain populated and subsequent attempts reuse the same files and metadata.

`generate_backup_metadata()` calls `done()` on all staged temp writers so compressed/encrypted spill files are flushed and synced, then returns an empty `MetadataInfo` seeded with store id. `flush_log()` separately merges normal and meta temp files. `merge_and_flush_log()` batches staged `DataFileInfo` by `merged_file_size_limit`; `merge_and_flush_log_files_to()` opens each compressed temp file for raw read, records offsets and compressed lengths, wraps readers in optional external-file encryption plus SHA256 hashing, writes the merged stream to external storage, then updates each `DataFileInfo` with external encryption info and encrypted checksum before pushing a `DataFileGroup` into metadata.

After log upload succeeds, `do_flush()` sets the metadata min resolved ts to at least the caller's resolved ts, fills region epoch/start/end information from `ResolvedRegions`, marshals and writes the backup metadata file, then deletes staged temp files with `clear_flushing_files()`. Any error before clearing increments `flush_fail_count` and leaves flushing lists for retry. Success resets the failure counter and returns the flush resolved ts. The outer `RouterInner::do_flush()` always clears the task flushing flag and updates `last_flush_time` only on success.

Global checkpoint updates are independent. `RouterInner::tick()` schedules `Task::UpdateGlobalCheckpoint`; `StreamTaskHandler::update_global_checkpoint()` CASes `global_checkpoint_ts` forward and writes an 8-byte little-endian file to `v1/global_checkpoint/{store_id}.ts`.

## State And Persistence Behavior
In-memory routing state is held in `ranges`, `tasks`, per-task `files`, `flushing_files`, `flushing_meta_files`, atomics for sizes and flush state, and task-global checkpoint state. Registered task ranges are process memory only; task metadata and checkpoints come from the broader metadata subsystem.

Local temp files are not durable backup output. `DataFile::on_events()` explicitly does not fsync on append. Durability begins when `generate_backup_metadata()` calls writer `done()` and `merge_and_flush_log_files_to()` uploads merged logs to external storage, followed by `flush_backup_metadata()` writing the metadata proto. The retry design protects local staged files after external-storage failures by retaining `flushing_*` lists and not deleting temp files until metadata upload succeeds. However, process crash before successful flush can lose unflushed local temp content; backup-stream relies on checkpoint/resubscription logic to replay from a safe checkpoint.

Metadata state is persisted as V2 `Metadata` proto files under `v1/backupmeta/`, with `DataFileGroup` entries pointing to merged log objects and per-segment `DataFileInfo` containing original table/region/CF/type/key-range/checksum/compression/encryption metadata. Merged log paths use max timestamp for date/hour partitioning to avoid accidental deletion over time ranges. Schema/meta keys are separated into `schema-meta` paths and mark metadata flags.

Encryption has two layers. Temp spill files may be encrypted by `TempFilePool` through the backup encryption manager's data key manager. External backup log objects may be encrypted during upload using either task-provided plaintext data key or master-key-based data keys. The external metadata is updated with per-file IV, method, encrypted data-key information, and checksum of encrypted content when external encryption is used. Without external encryption, merged readers are uploaded as raw compressed temp bytes and no encryption info is attached.

## Dependencies And Integration Points
The router integrates with raftstore apply observation (`CmdBatch`, `CmdType`), `TwoPhaseResolver` lock tracking, `ResolvedRegions` from `subscription_manager`, TiKV backup-stream endpoint tasks (`Task::Flush`, `Task::UpdateGlobalCheckpoint`, `Task::FatalError`), backup metadata (`StreamTask`, `MetadataClient` output), `external_storage`, `BackupEncryptionManager`, `TempFilePool`, TiKV codec helpers (`EventEncoder`, `Key`, `WriteRef`, table-id decode), `BackupStreamConfig`, metrics, failpoints, and utility containers (`SegmentMap`, `SlotMap`, `FilesReader`, `CompressionWriter`).

Downstream restore compatibility depends on the exact event encoding, log object layout, backupmeta filename format, `MetaVersion::V2`, `DataFileInfo` fields, write-CF begin-ts calculation, compression type, checksums, and encryption metadata. Operational integration depends on scheduler backpressure and endpoint handling of flush and fatal-error tasks.

## Risks And Edge Cases
Range routing uses `find_task_by_range()` to return only one arbitrary overlapping task for a region, with a FIXME noting regions that cross many task ranges. Event routing by `partition_by_range()` can route events correctly by key, but subscription setup may still miss multi-task overlap when a region spans tasks. The `SegmentMap` assumes non-overlapping task ranges; overlapping registrations would make selection behavior subtle.

Flush concurrency is guarded by a per-task atomic and lock ordering across `files`, `flushing_files`, and `flushing_meta_files`, but the source comments call out deadlock risk if lock acquisition changes. `test_flush_on_events_race` specifically protects the race where a writer creates a new file while a flush drains the file map. The retry model depends on destructive metadata generation happening only during `move_to_flushing_files()` and flushing lists staying intact after failure.

The `last_flush_time` atomic raw pointer is manually managed with `Box::into_raw` and `Box::from_raw`; mistakes here would leak or use-after-free. Metadata minimum begin ts asserts every flushed data file has nonzero `min_begin_ts_in_default_cf`; malformed write-CF values or empty metadata assumptions could panic. `TempFileKey::of()` maps undecodable table keys and meta keys to table id 0, which is intentional but may group unexpected keys. `TempFileKey::get_file_type()` panics on unsupported command types, relying on earlier filtering.

Failure escalation is coarse: after 30 adjacent flush failures the router sends a fatal task error, but errors before that keep retrying and can accumulate local temp files. External-storage upload writes log files before metadata; failures after a log upload but before metadata can leave orphaned log objects. The global checkpoint file write is not transactional with metadata flush. Encryption paths must keep `content_length` equal to encrypted reader output; tests cover this but provider behavior remains important.

## Test Signals
The file has broad unit and async tests: `test_register` validates range lookup; `test_basic_file` validates event writing, metadata generation retry, backupmeta filename parsing, and log counts; `test_do_flush` validates merged-file batching and cleanup; `test_flush_with_error` validates retry retention after a first write error; `test_empty_resolved_ts` validates flush resolved ts when no files exist; `test_cleanup_when_stop` validates temp cleanup on task drop; `test_flush_with_pausing_self` covers paused task behavior; `test_format_datetime`, `test_decode_begin_ts`, and `test_selector` cover helper logic; `test_update_global_checkpoint` validates checkpoint file bytes; `test_est_len_in_flush` checks estimated content length; config tests cover online config validation; `test_flush_on_events_race` protects the main write/flush race; and encryption tests cover no encryption, plaintext data key, and master-key-based uploads with readback.

Good additional signals are fault-injection tests for metadata upload failure after log upload, overlapping ranges, a region spanning multiple tasks, unsupported compression, malformed write CF records, external-storage partial writes, repeated fatal threshold failures, and process restart cleanup of temp directories.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/service.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/service.rs

## Purpose
`service.rs` exposes the backup-stream gRPC service for operational control and checkpoint queries. It adapts `kvproto::logbackuppb::LogBackup` RPCs into internal backup-stream endpoint tasks, returning flush results, per-region checkpoint state, and a server-streaming subscription for checkpoint flush events.

The file is intentionally thin: it contains no backup data persistence itself. Its importance is in the RPC-to-scheduler boundary, where client-visible commands enter the endpoint event loop and where endpoint callback results are translated back to protobuf responses.

## Important APIs, Types, And Functions
`BackupStreamGrpcService` owns a `tikv_util::worker::Scheduler<Task>` and is `Clone`, allowing gRPC service clones to schedule work into the backup-stream endpoint. `BackupStreamGrpcService::new()` constructs the wrapper.

`id_of(region: &Region) -> RegionIdentity` extracts region id and epoch version into the protobuf identity used by checkpoint responses. `impl From<RegionIdWithVersion> for RegionIdentity` converts checkpoint-manager not-found keys into the same protobuf shape.

The `LogBackup` implementation provides three RPCs. `flush_now()` schedules `Task::ForceFlush(TaskSelector::All, tx)` with an mpsc response channel and streams all internal per-task flush results into a single `FlushNowResponse`. `get_last_flush_ts_of_region()` converts request region identities into a `HashSet<(id, epoch_version)>`, schedules `Task::RegionCheckpointsOp(RegionCheckpointOperation::Get(...))`, and fills `GetLastFlushTsOfRegionResponse` in the callback. `subscribe_flush_event()` schedules `RegionCheckpointOperation::Subscribe(sink)` in non-test builds and intentionally panics under unit tests if invoked.

## Control Flow
`flush_now()` logs the peer, creates a response accumulator and a one-element mpsc channel, then schedules a force flush for all tasks. If scheduling fails, it immediately sends an INTERNAL gRPC failure with a busy/shutdown message. On successful scheduling, it spawns an async response task on the gRPC context. That task receives all items until the endpoint closes the channel, converts each item into `FlushResult` with success boolean, optional error text, and task name, then sends `sink.success(resp)`.

`get_last_flush_ts_of_region()` takes ownership of the request regions, maps them into a set, and builds an endpoint callback. The callback converts each `GetCheckpointResult` variant: `Ok` carries the returned region and checkpoint; `NotFound` carries the requested id/version and error; `EpochNotMatch` carries the actual region and error. The callback uses `tokio::spawn()` to send the unary response, so the endpoint task does not block on gRPC sink completion.

`subscribe_flush_event()` logs the client id. In production it schedules a region-checkpoint subscription operation containing the server-streaming sink; the checkpoint manager/endpoint owns subsequent stream writes.

## State And Persistence Behavior
`BackupStreamGrpcService` keeps only a scheduler handle. It does not cache responses, checkpoint state, or subscription state. Persistence behavior is delegated to endpoint tasks, checkpoint manager, router flush logic, and metadata storage. The RPC methods are asynchronous boundaries: a scheduled task may fail later and must report through the provided channel or callback.

For `flush_now()`, response completion depends on the endpoint dropping the mpsc sender after sending all task results. If the endpoint stalls or forgets to close the sender, the gRPC request remains pending. For checkpoint queries, response shape preserves both successful checkpoints and per-region errors so clients can distinguish absence and epoch mismatch without out-of-band state.

## Dependencies And Integration Points
The service depends on `grpcio`, `kvproto::logbackuppb`, `kvproto::metapb::Region`, `tikv_util` logging and worker scheduler, endpoint task types, `RegionCheckpointOperation`, `RegionSet`, checkpoint-manager result types, and `TaskSelector`. It is integrated into TiKV's gRPC service registration outside this file.

External clients observe the protobuf contracts: `FlushNowRequest/Response`, `FlushResult`, `GetLastFlushTsOfRegionRequest/Response`, `RegionCheckpoint`, `RegionIdentity`, and `SubscribeFlushEventRequest/Response`. Internally, the endpoint must understand `Task::ForceFlush` and `Task::RegionCheckpointsOp`.

## Risks And Edge Cases
The main risk is scheduler failure. `flush_now()` handles schedule errors with an explicit gRPC INTERNAL status, but `get_last_flush_ts_of_region()` and `subscribe_flush_event()` use `try_send!`; depending on macro behavior, schedule failures are logged or converted outside the local function body rather than building a typed gRPC error here.

`flush_now()` accumulates all task flush results in memory before replying. That is acceptable for the expected number of backup tasks but is not streaming. It also clones the response for logging on sink failure. The mpsc channel size is one, so endpoint result production can be backpressured by the response task.

`get_last_flush_ts_of_region()` collapses duplicate requested `(id, epoch_version)` pairs into a set, so duplicate request entries do not produce duplicate response entries. Response ordering follows endpoint result iteration, not request order. The callback spawns with `tokio::spawn()` rather than `ctx.spawn()`, so runtime availability and shutdown behavior matter.

`subscribe_flush_event()` carries a long-lived gRPC sink into endpoint state. Tests deliberately panic if the service path is used, which indicates subscription behavior is expected to be tested below the gRPC layer.

## Test Signals
This file has no local test module beyond the `#[cfg(test)] panic` guard in `subscribe_flush_event()`. Its behavior is indirectly tested through endpoint and checkpoint-manager tests that schedule `Task::ForceFlush` and `RegionCheckpointOperation` variants. Useful direct tests would use a dummy scheduler to assert that `flush_now()` schedules `ForceFlush(All)`, schedule failure maps to INTERNAL, checkpoint results convert each `GetCheckpointResult` variant correctly, duplicate checkpoint request regions are deduplicated, and subscription scheduling transfers the sink in non-test builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/subscription_manager.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/subscription_manager.rs

## Purpose
`subscription_manager.rs` serializes region subscription operations for backup-stream observation. It starts and stops region observation, retrieves the last safe checkpoint for a region, launches initial scans from that checkpoint, retries transient failures with backoff, reacts to region changes and memory pressure, and periodically resolves per-region checkpoints into a store-level `ResolvedRegions` result used by flushing.

The manager is the bridge between raftstore leadership/region events, metadata checkpoints, initial snapshot scanning, incremental event observation, and router task ranges. Its correctness determines whether backup-stream observes the right leader regions from the right timestamp without advancing checkpoints past unfinished initial scans or unresolved locks.

## Important APIs, Types, And Functions
`ResolvedRegions` packages `Vec<ResolveResult>` plus the computed global checkpoint. `new()`, `take_resolve_result()`, `resolve_results()`, and `global_checkpoint()` are consumed by router flush code and checkpoint management.

`InitialScan` is a private async trait abstracting initial scan execution. Its production implementation for `InitialDataLoader<E, RT>` obtains an observe snapshot with `observe_over_with_retry()`, installs a PITR `ChangeObserver`, and scans initial data from the provided start timestamp. `ScanCmd` holds a region, observe handle, last checkpoint, feedback channel, and wait-group work token. `ScanCmd::exec_by()` runs the scan and records CF statistics.

`scan_executor_loop()`, `spawn_executors()`, `spawn_executors_to()`, `create_scan_pool()`, and `ScanPoolHandle::request()` implement the dedicated initial-scan runtime. The pool uses TiKV's log-backup scan thread name and sets filesystem IO type to replication. Queue and executing lengths update `PENDING_INITIAL_SCAN_LEN`.

`RegionSubscriptionManager<S, R>` owns region info provider, metadata client, range router, endpoint scheduler, `SubscriptionTracer`, failure counts, memory quota, weak self-messenger, scan pool handle, wait group for scans, and `advance_ts_interval`. `RegionSubscriptionManager::start()` constructs the mpsc channel and returns `(Sender<ObserveOp>, future)` for the operator loop.

The operator methods are `region_operator_loop()`, `start_observe()`, `try_start_observe()`, `observe_over_with_initial_data_from_checkpoint()`, `spawn_scan()`, `on_observe_result()`, `retry_observe()`, `is_available()`, `refresh_resolver()`, `on_high_memory_usage()`, `schedule_start_observe()`, `get_last_checkpoint_of()`, `find_task_by_region()`, `issue_fatal_of()`, and `wait()`. `should_retry()` classifies errors that should not be retried, such as epoch mismatch, not leader, stale observe id, region not found, observe canceled, and raftstore not-leader/epoch errors. `backoff_for_start_observe()` provides capped exponential retry delay with a failpoint override.

## Control Flow
`RegionSubscriptionManager::start()` creates a bounded mpsc channel, spawns scan executors, copies the sink router and scheduler from the initial loader, and returns `region_operator_loop()`. All `ObserveOp` messages are handled sequentially in that loop, preserving start/stop/refresh ordering for the shared `SubscriptionTracer`.

On `ObserveOp::Start`, `start_observe()` first calls `is_available()` to ensure the region still exists, this store is leader, the supplied epoch is not stale, and any existing running subscription for the same handle can be removed. It then marks the region pending and calls `try_start_observe()`. `try_start_observe()` finds the task by region range, retrieves the last region checkpoint from metadata, and calls `observe_over_with_initial_data_from_checkpoint()`. That method registers the region as running with a `TwoPhaseResolver` stable timestamp equal to the checkpoint, upgrades the weak self-messenger, and enqueues a `ScanCmd` to the scan pool.

The scan pool receives `ScanCmd`, spawns an async task per command, executes the initial scan, then sends `ObserveOp::NotifyStartObserveResult` back to the manager with the region, observe handle, and optional boxed error. On success, `on_observe_result()` clears failure count and calls `phase_one_done()` on the matching subscription resolver. On failure, it moves the matching running subscription back to pending, skips retry for unretryable errors, or calls `retry_observe()`. Retry increments per-region failure count, checks `is_available()` again, and schedules a delayed `ObserveOp::Start` using capped exponential backoff. Too many retries become a fatal endpoint task for the region range.

`ObserveOp::Stop` deregisters the region unconditionally. `Destroy` deregisters only if epoch comparison says the new destroy event covers the active subscription. `RefreshResolver` tries to update only region metadata if the epoch version is unchanged; otherwise it deregisters and, if the region still maps to a task, starts observation again from the latest checkpoint. If refresh fails to get checkpoint or enqueue scan, it synthesizes a `NotifyStartObserveResult` through the endpoint scheduler so normal retry handling applies.

`ObserveOp::ResolveRegions` waits up to five seconds for pending initial scans, asks `BackupStreamResolver` for leader/current regions with an optional `advance_ts_interval`, calls `SubscriptionTracer::resolve_with(min_ts, regions)`, chooses the minimum region checkpoint or `min_ts` when no regions are observed, updates metrics for the smallest checkpoint region, logs non-trivial blockers, and invokes the callback with `ResolvedRegions`.

`ObserveOp::HighMemUsageWarning` deregisters the inconsistent region, logs memory usage, and schedules a delayed restart with a base 60-second backoff plus jitter. This drops resolver lock memory for a problematic region and later rebuilds it by initial scan.

## State And Persistence Behavior
The manager's own state is process memory: subscription map, failure counts, queued scans, and retry timers. Durable input comes from `MetadataClient::get_region_checkpoint(task, region)`, which returns the timestamp from which initial scan should start. Durable output is indirect: resolved region checkpoints flow into router metadata/global checkpoint updates, and fatal errors flow into endpoint task handling.

The subscription state machine uses `Pending` as a placeholder while checkpoint lookup and initial scan are in progress. Running subscriptions contain an `ObserveHandle` and `TwoPhaseResolver`. During initial scan, the resolver's stable ts prevents checkpoint advancement beyond the scan start even while incremental events are being observed concurrently. Only after scan success does `phase_one_done()` replay buffered incremental lock/unlock events and allow normal resolved-ts progression.

The wait group in `scans` tracks in-flight initial scans. `ResolveRegions` waits briefly for it to drain, but if it times out it still resolves with current subscription state; phase-one subscriptions will report their stable timestamp rather than blocking indefinitely. Retry state is bounded by `TRY_START_OBSERVE_MAX_RETRY_TIME`; exceeding it emits a fatal endpoint task and clears failure count.

## Dependencies And Integration Points
This module depends on raftstore region information and observe handles, `InitialDataLoader`, `MetadataClient` and metadata stores, `Router` range lookup, endpoint `ObserveOp` and `Task`, `BackupStreamResolver`, `SubscriptionTracer`, `ResolveResult` and checkpoint types, TiKV memory quota, thread builder hooks, metrics, failpoints, and worker scheduler.

It integrates with leadership/region-change producers that send `ObserveOp::Start`, `Stop`, `Destroy`, and `RefreshResolver`; with initial scan code that writes historical data into the router; with incremental observer code that sends KV events and lock changes; and with checkpoint/flush code that asks for `ResolvedRegions`.

## Risks And Edge Cases
`find_task_by_region()` uses router `find_task_by_range()`, which returns only one overlapping task. If a region overlaps multiple backup task ranges, subscription may only be associated with one task. The router source itself flags this limitation.

Retry behavior must distinguish stale commands from recoverable failures. `is_available()` removes an existing subscription only when the handle id matches; otherwise it treats the retry as stale. Incorrect handle matching could stop a fresh observation or revive an old one. Unretryable errors leave the region pending until a later stop/refresh cleans it up, which is intentional but can be confusing in metrics.

`ResolveRegions` forces progress after a five-second scan wait. The two-phase resolver makes this safe for phase-one regions, but if a subscription is absent or incorrectly marked running without a stable ts, checkpoints could advance too far. `wait()` returns `true` on timeout despite its name, which is easy to misuse outside the current call site.

The scan executor loop spawns per-command tasks inside a dedicated runtime and drops the runtime from within itself using `block_in_place`; shutdown semantics are intentionally asynchronous. The queue is large (`32768`) and scan commands hold work tokens, so prolonged scan failures can accumulate memory and pending metrics. The comments also warn not to use Tokio's blocking pool for scans because temp-file IO uses blocking conversions.

Memory-pressure handling deregisters and later restarts a region. During the backoff window, that region is absent from resolved checkpoints; global checkpoint selection therefore depends on remaining observed regions and `min_ts`. Correctness relies on later checkpoint-based rescan covering the gap.

## Test Signals
Tests cover retry and ordering behavior through a `Suite` with in-memory region provider, dummy scheduler, metadata store, router, and scan functions. `test_backoff_for_start_observe` validates capped exponential backoff. Failpoint-gated `test_message_delay_and_exit` checks executor shutdown under delayed scans. `test_basic_retry` verifies transient scan failure retries and eventual success. `test_on_high_mem` verifies deregistration, delayed restart, and region set restoration. `test_region_split_inflight` validates refresh during split. `test_unretryable_failure` covers epoch mismatch followed by refresh success. `test_always_failure_initial_scan` validates repeated retries until the simulated scan eventually succeeds.

Useful additional tests would cover scheduler send failures, metadata checkpoint lookup failure classes, multiple overlapping tasks, not-leader/region-absent stale starts, resolve timeout while phase-one scans are pending, and fatal emission after `TRY_START_OBSERVE_MAX_RETRY_TIME`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/subscription_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/subscription_track.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/subscription_track.rs

## Purpose
`subscription_track.rs` implements the in-memory subscription state and resolved-ts logic for backup-stream regions. It tracks whether a region is pending initial setup or actively observed, owns the active raftstore observe handle, and wraps TiKV's resolved-ts `Resolver` with a two-phase mechanism that handles concurrent initial scan and incremental observation.

The module is the local correctness guard for checkpoint advancement. It prevents a region's checkpoint from moving beyond the initial-scan start timestamp until the scan is complete, and it buffers incremental lock/unlock events seen during phase one so lock state remains consistent once normal resolving begins.

## Important APIs, Types, And Functions
`SubscriptionTracer` is a cloneable wrapper around `Arc<DashMap<u64, SubscribeState>>` plus `Arc<TxnStatusCache>`. It provides `clear()`, `add_pending_region()`, `register_region()`, `current_regions()`, `resolve_with()`, `set_pending_if()`, `deregister_region_if()`, `try_update_region()`, `is_observing()` for tests, and `get_subscription_of()`.

`SubscribeState` is `Pending(Region)` or `Running(ActiveSubscription)`. `Pending` represents a region between start request and successful initial scan setup. `Running` contains `ActiveSubscription`, which stores region metadata, `ObserveHandle`, and `TwoPhaseResolver`. `ActiveSubscription::new()` creates a resolver with optional stable/start timestamp; `stop()` calls `ObserveHandle::stop_observing()`; `resolver()` and `handle()` expose internals to the manager.

`CheckpointType` describes why a checkpoint has its value: `MinTs`, `StartTsOfInitialScan`, or `StartTsOfTxn(Option<(TimeStamp, TxnLocks)>)`. `ResolveResult` contains region metadata, checkpoint timestamp, and checkpoint type. `ResolveResult::resolve()` asks the active subscription resolver for a timestamp and classifies the blocker.

`Ref` and `RefMut` abstract mutable references returned by `get_subscription_of()`. `ActiveSubscriptionRef` wraps a DashMap mutable ref and guarantees the entry is `Running`.

`TwoPhaseResolver` wraps `resolved_ts::Resolver`, `future_locks: Vec<FutureLock>`, and `stable_ts: Option<TimeStamp>`. Its APIs are `new()`, `in_phase_one()`, `track_phase_one_lock()`, `track_lock()`, `untrack_lock()`, `resolve()`, `resolved_ts()`, `sample_far_lock()`, and `phase_one_done()`. `FutureLock` stores buffered incremental `Lock(key, ts, generation)` and `Unlock(key)` operations while phase one is active.

## Control Flow
A region starts absent. `SubscriptionTracer::add_pending_region()` inserts `Pending(region)` if the entry is vacant and logs if a pending/running entry already exists. Once observation and scan setup starts, `register_region()` increments `TRACK_REGION`, replaces a pending entry with `Running(ActiveSubscription::new(...))`, or logs unexpected transitions for absent/running states. Replacing an already running entry decrements the counter to avoid double counting.

`resolve_with(min_ts, regions)` is called by the subscription manager after the external resolver determines which region ids are currently resolvable leaders. It builds a `HashSet` of those ids, iterates mutable subscription entries, skips pending regions, skips running regions absent from the provided id set with a metric increment, and returns `ResolveResult::resolve()` for included running regions.

`deregister_region_if()` removes pending regions directly. For running regions, it evaluates the caller predicate against the active subscription and new region, decrements `TRACK_REGION`, stops the observe handle, logs, and removes the entry only when the predicate is true. `set_pending_if()` is similar but converts a matching running entry back to pending with the old region metadata; this is used after start/scan failure to retain the placeholder for retry/refresh logic.

`try_update_region()` handles metadata-only refresh. It obtains a running subscription, compares old and new epoch versions, and if the version is unchanged replaces `subscription.meta` without resetting the resolver. A version change returns false so the manager can deregister and rescan.

`TwoPhaseResolver` starts with `stable_ts = Some(start_ts)` when an initial scan is in progress. `resolve(min_ts)` returns `min(min_ts, stable_ts)` and `resolved_ts()` returns `stable_ts`, regardless of incremental locks, while phase one is active. `track_phase_one_lock()` directly tracks locks found by the initial scan. Incremental `track_lock()` and `untrack_lock()` during phase one are appended to `future_locks` instead of mutating the resolver. `phase_one_done()` replays buffered future locks in order, clears `stable_ts`, and advances the underlying resolver to the former stable ts. After that, normal track/untrack and `resolver.resolve(min_ts, TsSource::BackupStream)` behavior applies.

## State And Persistence Behavior
All state in this file is memory-only. The durable implication is through resolved checkpoints emitted by `ResolveResult`: a lower checkpoint prevents backup metadata/global checkpoint from claiming progress that has not been safely scanned or that is blocked by an active transaction lock.

The subscription map also owns observe-handle lifetime. Removing or inactivating a running subscription calls `stop_observing()`, which tells raftstore observation to stop delivering events for that handle. Metrics state (`TRACK_REGION`) must stay balanced with Running entries.

`TwoPhaseResolver` uses an unlimited `MemoryQuota::new(usize::MAX)` internally, with a TODO to limit memory. Lock state is therefore constrained by process memory and by higher-level high-memory handling in `subscription_manager`. The transaction status cache is shared into the underlying resolver.

## Dependencies And Integration Points
This module depends on DashMap, raftstore coprocessor `ObserveHandle`, `resolved_ts::Resolver`, `TxnLocks`, `TsSource`, TiKV `TxnStatusCache`, memory quota types, `kvproto::metapb::Region`, backup-stream metrics, and utility logging helpers.

It is used by `subscription_manager` to serialize region state transitions and checkpoint calculation, by the router/event path through `TwoPhaseResolver` lock tracking while converting raft `CmdBatch` into `ApplyEvents`, and by endpoint/checkpoint code through `ResolveResult` and `CheckpointType` diagnostics.

## Risks And Edge Cases
The two-phase algorithm depends on preserving event order in `future_locks`. If incremental events are buffered out of order or phase-one scan locks are not tracked with `track_phase_one_lock()`, the resolver can retain or drop locks incorrectly. `handle_future_lock()` unwraps memory-quota errors when replaying buffered locks because the quota is currently unlimited; adding a real quota will require error handling here.

`resolve_with()` collects region ids into a set and skips pending regions. If a region stays pending for a long time, it contributes no checkpoint result; the manager relies on phase-one Running state, not Pending, to hold checkpoint back. State transition bugs that leave a region pending after observation begins can therefore affect global checkpoint calculation.

`register_region()` increments `TRACK_REGION` before inspecting the old state and then compensates only for running-to-running replacements. The accounting is subtle and must stay aligned with `clear()`, `set_pending_if()`, and `deregister_region_if()`. Unexpected absent-to-running is allowed with a warning; that path increments the metric and may be correct for tests/refresh but bypasses the intended pending placeholder.

`try_update_region()` only compares epoch version, not conf version. That matches the local refresh intent, but callers must use stronger epoch checks for destroy/stop decisions. `ActiveSubscriptionRef` relies on its constructor to avoid pending states; misuse would hit `unreachable!()`.

## Test Signals
`test_two_phase_resolver` verifies that phase-one stable ts caps resolution, future lock/unlock buffering is replayed after `phase_one_done()`, and normal incremental lock resolving works afterward. `test_delay_remove` checks that deregistration stops observation. `test_cal_checkpoint` builds multiple subscriptions covering phase-one, no-lock, finished initial scan, lock-blocked, and removed-region cases, then validates checkpoint values and `CheckpointType` classification including sampled transaction locks.

Additional useful tests would cover pending-region exclusion, `set_pending_if()` handle predicates, metric balancing under unexpected transitions, region metadata refresh with unchanged and changed epoch versions, future-lock replay order with multiple keys/generations, and memory-quota behavior if the TODO is implemented.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/subscription_track.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/tempfiles.rs -->
# sources/storage-engines/tikv/components/backup-stream/src/tempfiles.rs

## Purpose
`tempfiles.rs` implements backup-stream's local temporary file pool. It offers appendable write handles that keep data in memory until a quota/threshold triggers spill to disk, optional compression for logical file content, optional local spill-file encryption through TiKV's data key manager, raw read handles for uploading the compressed bytes, and cleanup of memory/disk resources.

The module exists because backup-stream writes many small log fragments before flushing them to external storage. It reduces disk IO by buffering small files, spills larger files when memory pressure requires it, and preserves retryability by allowing a completed temp file to be read multiple times until the caller explicitly removes it.

## Important APIs, Types, And Functions
`Config` controls `cache_size`, `swap_files` directory, `content_compression`, `minimal_swap_out_file_size`, and `write_buffer_size`. `TempFilePool::new()` initializes the swap directory, deleting any existing content with encryption-aware removal when needed. `TempFilePool::open_for_write()`, `open_raw_for_read()`, `remove()`, `config()`, and test-only `mem_used()` are the main pool APIs.

`TempFilePool` stores current in-memory capacity usage, a mutex-protected `FileSet`, and a `BackupEncryptionManager`. `FileSet` maps relative paths to `File`, which contains shared `FileCore` and atomic reader/writer counts.

`ForWrite` is either `ZstdCompressed(ZstdCompressionWriter<ForWriteCore>)` or `Plain(ForWriteCore)` and implements `AsyncWrite` plus the crate `CompressionWriter::done()`. `ForWriteCore` owns write state for one file path and closes/syncs spill files in `done()`. `ForRead` implements `AsyncRead` over a file's swapped-out prefix plus in-memory tail and exposes `len()`.

`FileCore` contains the in-memory buffer, optional `SwappedOut` writer, count of in-memory bytes already written to disk, owning pool, and relative path. Key methods are `should_swap_out()`, `poll_swap_out_unpin()`, `append_to_buffer()`, `max_cache_size()`, and `new()`. `SwappedOut` abstracts plain Tokio files, encrypted writers, test dynamic writers, and closed state; it implements `AsyncWrite` and `done()`.

Helper `modify_and_update_cap_diff()` updates a `Vec<u8>` and adjusts the pool memory counter by capacity delta, updating `TEMP_FILE_MEMORY_USAGE`.

## Control Flow
`TempFilePool::new()` treats the swap directory as scratch. If the directory already exists, it logs and removes it recursively, using the data key manager when configured, then recreates it. This makes restart after panic clear leaked temp files rather than reusing stale content.

`open_for_write()` locks the file map, creates a new `FileCore` for the relative path if absent, rejects writes while reader count is nonzero, increments writer count, wraps the `ForWriteCore` in zstd compression if configured, and returns the write handle. Multiple writers are counted, but the router's usage normally has one writer per temp file. `open_raw_for_read()` rejects reads while writer count is positive, opens the swapped file for decrypted raw read if the file has spilled, increments reader count, and returns a `ForRead` cursor.

`ForWriteCore::poll_write()` rejects writes after `done()`, locks `FileCore`, calls `should_swap_out(buf.len())`, and if true drives `poll_swap_out_unpin()` before appending the new bytes to the in-memory buffer. `should_swap_out()` triggers spill when an upcoming reallocation would exceed the memory quota and the file is large enough, when an already spilled file has accumulated more than the write buffer, or when a previous spill has a partial write in progress. `poll_swap_out_unpin()` lazily creates the relative disk file, repeatedly writes `in_mem[written..]`, advances `written`, records swap metrics, then clears and shrinks the memory buffer to the configured write buffer size and resets `written`.

`CompressionWriter::done()` on `ForWrite` first finalizes the zstd writer when present, then calls `ForWriteCore::done()`. `ForWriteCore::done()` is idempotent from the caller's perspective: it caches success or stringified failure in `done_result`. If an external spill file exists, it uses `spawn_blocking()` to lock the core, replace the external writer with `Closed`, call `SwappedOut::done()`, and sync the underlying file. It decrements writer count after attempting closure.

`ForRead::poll_read()` first reads from the decrypted external file if this is the beginning of the read and a spill file exists. When that external file reaches EOF, it reads from the current in-memory buffer starting at `read`. `ForRead::len()` reports disk metadata length plus retained in-memory tail. Dropping `ForRead` decrements reader count. Dropping `ForWriteCore` decrements writer count if `done()` was never called.

`TempFilePool::remove()` removes the map entry and decrements `TEMP_FILE_COUNT`; actual disk cleanup happens when the last `Arc` to `FileCore` drops. `FileCore::drop()` subtracts the buffer capacity from the memory counter and deletes the relative spill file if one exists. This delayed cleanup allows existing readers/writers to finish after pool removal.

## State And Persistence Behavior
The pool's state is intentionally temporary. It may hold file content entirely in memory, partly in a local swap file and partly in memory, or entirely in a local swap file after `done()`. The local swap directory is cleared on pool creation, so content is not persisted across process restart for recovery. Backup durability is supplied later by router upload to external storage.

Within a live process, `done()` provides local spill-file synchronization for files that have been swapped out. Purely in-memory files have no local fsync. `open_raw_for_read()` returns compressed/encrypted-spill-decoded raw content as the router expects to upload compressed bytes to external storage; it does not decompress zstd content.

Local spill encryption uses `backup_encryption_manager.opt_data_key_manager()`. `create_relative()` wraps new spill writers with encrypted writers when available; `open_relative()` wraps readers with decrypting readers or plaintext decryptors; `delete_relative()` delegates encrypted file deletion before removing the OS file. This is separate from external backup-object encryption in `router.rs`.

Memory accounting tracks vector capacity, not logical bytes, through `current`. Shrinking after spill reduces the tracked capacity to the write buffer size. The `cache_size` is an atomic so router config updates can change quota for an existing pool.

## Dependencies And Integration Points
This module depends on Tokio `AsyncRead`/`AsyncWrite`, `async_compression` through the crate's `ZstdCompressionWriter`, encryption crate readers/writers and `BackupEncryptionManager`, `kvproto` compression and encryption enums, TiKV metrics, failpoints, and crate error/annotation utilities.

`router.rs` is the primary consumer: it creates a `TempFilePool` per stream task, opens `ForWrite` handles for `DataFile`s, calls `done()` before flush, opens `ForRead` with `open_raw_for_read()` to merge/upload compressed temp content, and calls `remove()` after successful metadata upload or task drop. Config updates mutate the pool's `cache_size` atomic through `RouterInner::update_config()`.

## Risks And Edge Cases
The file uses synchronous `std::sync::Mutex` inside async `poll_*` implementations. The code keeps critical sections small, but `poll_swap_out_unpin()` polls an async writer while holding the mutex, which can be risky if future writer implementations call back into the same state. The comments acknowledge implementation complexity around async mutexes and polling.

Concurrent access rules are strict: reads are rejected while writers exist, and writes are rejected while readers exist. Writer count correctness depends on `done()` and `Drop` paths; double decrement would allow unsafe reads, while missed decrement would permanently block reads. `ForWriteCore::done()` caches failures because retrying finalization after ownership-consuming writers may be impossible; a failed `done()` can make the task eventually fail and may represent data loss for that temp file.

`ForRead::poll_read()` only reads from the external file while `read == 0`; after any in-memory bytes are read, it will not return to the file. This matches the invariant that the spill file contains the prefix and memory contains the tail, but changes to partial-read logic could break ordering. `len()` uses `st.in_mem.len() - st.written`; after successful spill `written` resets to zero and the in-memory buffer is the tail.

`modify_and_update_cap_diff()` only updates metrics when `diff > 0`, but `diff` is a wrapping subtraction, so shrinkage produces a huge positive wrapped value and relies on atomic wrapping arithmetic to subtract capacity. This is clever but fragile for maintainers. Existing swap directory deletion on pool creation is correct for scratch state, but a misconfigured `swap_files` path could delete unexpected directory contents.

Unsupported compression returns an error from `open_for_write()`. Small files below `minimal_swap_out_file_size` may remain in memory even when quota is tight. The failpoints can override cache size or force swapout, which is useful for tests but must be scoped carefully.

## Test Signals
Tests cover the core invariants. `test_read` validates in-memory reads. `test_swapout` validates spill threshold behavior and combined disk+memory reads. `test_compression` writes zstd content, reads raw, and decompresses to original bytes. `test_write_many_times` uses a dynamic writer that only writes two bytes at a time to validate partial-write spill loops. `test_read_many_times` validates retry reads and write reopening after readers drop. `test_not_leaked` validates memory and disk cleanup after remove. `test_panic_not_leaked` validates stale swap directory cleanup on new pool creation. `test_various_encryption` validates encrypted spill files for AES and SM4 modes and confirms on-disk content is not plaintext while readback matches.

Additional useful tests would cover reader/writer rejection errors, `done()` failure caching, unsupported compression, dynamic quota updates, exact memory counter behavior on growth and shrink, encrypted delete failure, and a misconfigured swap path guard at higher configuration layers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/backup-stream/src/tempfiles.rs -->
