# Research Group subset-b-008930

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/kv.rs -->
# sources/storage-engines/tikv/src/server/service/kv.rs

## Purpose
`kv.rs` implements TiKV's public `Tikv` gRPC service. It is the transport-facing bridge from kvproto RPCs into storage transaction commands, raw KV commands, coprocessor endpoints, raft message ingestion, snapshot scheduling, region split/check-leader helpers, health feedback, and batch-command multiplexing. The file is on TiKV's critical path because it performs request validation, request-source/resource-control accounting, async dispatch, response shaping, gRPC stream management, and raft/snapshot backpressure decisions.

## Important APIs, Types, and Functions
`Service<E, L, F>` is the main service object, parameterized by the storage engine, lock manager, and API-version key format. It holds cluster and store ids, `Storage`, GC worker, coprocessor v1/v2 endpoints, snapshot and check-leader schedulers, gRPC thread-load tracking, proxy forwarding, resource-group manager, health controller, health feedback sequence state, and a raft message filter.

`RaftGrpcMessageFilter` abstracts rejection policy for incoming raft append and snapshot traffic. `DefaultGrpcMessageFilter` rejects `MsgAppend` only when memory pressure crosses `reject_messages_on_memory_ratio`, while failpoints can force raft append or snapshot rejection.

The `handle_request!` macro implements most unary methods. It rejects cluster-id mismatches, optionally forwards through `Proxy`, consumes resource-control penalty, records resource-group counters, awaits a `future_*` helper, sets total RPC time for selected responses, sends the unary result, and records success/failure metrics. `reject_if_cluster_id_mismatch!` and `set_total_time!` are the related validation/timing helpers.

Hand-written service methods cover flashback, coprocessor, raw coprocessor, unsafe destroy range, streaming coprocessor, raft streams, batch raft streams, snapshot streams, tablet snapshots, split region, batch commands, check-leader, store safe ts, lock-wait dump, and health feedback. `handle_raft_message` validates destination store id, applies raft-append rejection policy, reports rejected messages, and feeds accepted messages to `RaftExtension`.

`handle_batch_commands_request`, `response_batch_commands_request`, `MeasuredSingleResponse`, `MeasuredBatchResponse`, `GrpcRequestDuration`, and `collect_batch_resp` implement the bidirectional batch command protocol. `HealthFeedbackAttacher` injects store slow-score feedback into batch responses on demand or at an interval.

The `future_*` functions translate kvproto request types into storage APIs. Important families include transactional read helpers (`future_get`, `future_scan`, `future_batch_get`, `future_buffer_batch_get`, `future_scan_lock`), raw KV helpers (`future_raw_get`, `future_raw_batch_get`, `future_raw_put`, `future_raw_batch_put`, `future_raw_delete`, `future_raw_batch_delete`, `future_raw_scan`, `future_raw_batch_scan`, `future_raw_delete_range`, `future_raw_get_key_ttl`, `future_raw_compare_and_swap`, `future_raw_checksum`), flashback helpers, coprocessor helpers, and `txn_command_future!`-generated transaction command futures for prewrite, pessimistic lock/rollback, commit, cleanup, heartbeat, check txn status, check secondary locks, MVCC inspection, flush, and resolve/batch rollback.

## Control Flow
Most unary RPCs enter a generated `handle_request!` method. The request context is checked against `Service.cluster_id`, then the request may be forwarded by proxy. Resource-group metadata is observed before a storage future is created. The async task awaits the future, decorates timing fields where supported, sends the response via `UnarySink`, records histogram/source metrics, and maps network/storage errors to log counters.

Storage futures are response adapters around `Storage` methods. Read paths usually create a global request tracker, record request protobuf size, translate raw keys into `txn_types::Key`, await storage, extract region errors ahead of key errors, write scan/time/RU details, and remove the tracker. Write-like APIs use `paired_future_callback`: a command is scheduled synchronously, then the async future awaits the callback result before constructing the protobuf response.

The transaction-command macro centralizes conversion from request protobuf into typed storage commands. It schedules the command through `storage.sched_txn_command`, extracts region errors first, then command-specific branches fill fields such as `min_commit_ts`, `one_pc_commit_ts`, pessimistic-lock result arrays, commit version, lock TTL, txn action, secondary lock status, MVCC info, and per-key errors. It also writes scan/write/time/RU tracker details for most transaction commands.

Raft ingestion is stream-oriented. `raft` reads individual `RaftMessage`s; `batch_raft` reads `BatchRaftMessage`s, measures receive delay from `last_observed_time`, and iterates contained messages. Both use metadata to count messages by source store, reject only `StoreNotMatch` as a stream-breaking error, and otherwise keep the stream open until peer shutdown or transport error.

Snapshot and tablet-snapshot RPCs do not process bytes locally. They wrap the gRPC stream/sink into `SnapTask::Recv` or `SnapTask::RecvTablet` and schedule it on the snapshot worker. Rejection occurs before scheduling if the raft message filter refuses snapshots or if the scheduler is full.

`batch_commands` splits into two tasks. The request task reads each `BatchCommandsRequest`, creates a request batcher, dispatches or batches individual subrequests, and commits any compatible get/raw-get batches. Each subrequest response is sent through an internal channel as `MeasuredSingleResponse`. The response task uses `BatchReceiver` to coalesce responses up to `GRPC_MSG_MAX_BATCH_SIZE`, records per-command elapsed and wait times, attaches transport load and health feedback, then sends a `BatchCommandsResponse` over the duplex sink.

## State and Persistence Behavior
`Service` itself owns mostly process-local routing and accounting state. Persistent data changes happen through `Storage`, `GcWorker`, `RaftExtension`, and snapshot worker integrations rather than direct disk writes in this file. Transactional and raw write futures schedule storage commands that later persist through raftstore/engine layers. Flashback is a special multi-step operation: prepare starts engine flashback state and schedules a prewrite-like command to block resolved-ts advancement; execute schedules the flashback transaction command and only calls `end_flashback` after the data operation succeeds.

Raft messages are persisted by downstream raftstore after `RaftExtension::feed`. This file can drop or reject inbound raft traffic under memory pressure, but it does not append logs itself. Snapshot RPCs schedule receive work; persistence of snapshot files and raft feed happen in `snap.rs`.

Mutable in-service state includes the atomic health feedback sequence, scheduler handles, and cloned counters/load pools. `HealthFeedbackAttacher` keeps per-stream last-feedback time and generates monotonically increasing feedback sequence numbers through the shared `AtomicU64`.

## Dependencies and Integration Points
The file integrates with `kvproto` request/response types, `grpcio`, `Storage<E, L, F>`, lock managers, API-version key encoding, coprocessor v1 and v2 endpoints, raftstore `RaftExtension`, snapshot worker tasks, check-leader scheduler, GC worker, resource-control manager, health controller, request trackers, TiKV metrics, failpoints, and proxy forwarding macros.

The public re-exports in `service/mod.rs` expose `Service` as `KvService`, raft message filters, batch-command request/response aliases, measured response structures, and flashback futures to other server modules/tests.

## Risks and Edge Cases
Cluster-id validation is repeated in unary and batch paths; missing it on a hand-written method can admit cross-cluster requests. Batch-command cluster-id mismatch returns both an in-band response item and a gRPC invalid-argument error, so client behavior depends on stream handling. Resource-group counter labels currently use the same resource group name twice, which may be intentional metric schema behavior but is worth checking before changing.

The raft rejection path must only reject traffic that raftstore can recover from. `StoreNotMatch` intentionally breaks the stream so the sender can resolve the correct address from PD, while other raft feed errors are swallowed. The memory-based append rejection policy depends on global high-water memory reporting and memory trace counters for raft messages, entry cache, and applying entries.

Several methods remain `unimplemented!` (`kv_import`, batch coprocessor, MPP dispatch/cancel/connection) or explicitly return unimplemented (`kv_gc`/`future_gc`). `unsafe_destroy_range` uses assertions to reject empty boundaries; malformed external requests can panic rather than return a protobuf error. Flashback sequencing is sensitive because prepare locks a region and execute must only end flashback after successful modification.

The tracker lifecycle is manual in several futures. Most paths remove trackers explicitly or via `defer!`; early returns or future rewrites must preserve removal to avoid tracker leaks and incorrect RU/scan metrics. Batch response timing is measured at collection time, so channel backpressure affects `kv_grpc_wait_time_ns`.

## Test Signals
Local tests cover RU v2 fields for `future_get`, `future_batch_get`, and `future_prewrite`; `poll_future_notify` behavior when futures are completed from another thread or polled by a slow poller; and `HealthFeedbackAttacher` interval/on-demand behavior, sequence increments, slow-score propagation, and multiple `GetHealthFeedback` responses in one batch. Compile coverage also validates the large RPC-to-future mapping. Broader behavioral coverage should come from integration tests around gRPC batch commands, raft stream rejection, snapshot scheduling, cluster-id mismatch, and flashback error paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/kv.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/mod.rs -->
# sources/storage-engines/tikv/src/server/service/mod.rs

## Purpose
`service/mod.rs` is the module boundary for TiKV server gRPC services. It wires submodules into a small public surface and defines the shared network-error logging macro used by service implementations.

## Important APIs, Types, and Functions
The module declares private `batch`, `debug`, and `kv` modules plus public `diagnostics`. Its `pub use` block exports `DebugService`, `DiagnosticsService`, `KvService`, `ResolvedTsDiagnosisCallback`, `DefaultGrpcMessageFilter`, `RaftGrpcMessageFilter`, batch-command request/response aliases, measured batch response helpers, `GrpcRequestDuration`, and the public flashback futures.

`log_net_error!` is exported with `#[macro_export]`. It evaluates an error expression once, logs gRPC transport errors at `info!`, and logs all other server errors at `debug!`, adding the caller-supplied structured fields plus `"err"`.

## Control Flow
There is no runtime control flow beyond macro expansion. Importers access service implementations through these re-exports rather than reaching into private modules. Call sites such as `kv.rs` use `log_net_error!` in async error handlers after failed sink sends or storage futures.

## State and Persistence Behavior
This file has no state and no persistence behavior. It only changes compile-time module visibility and generated logging code.

## Dependencies and Integration Points
It integrates the server service tree with the rest of TiKV by exposing stable type aliases and service names. `log_net_error!` depends on `$crate::server::Error::Grpc` to classify transport errors. The macro is available crate-wide because of `#[macro_export]`, while service modules remain mostly encapsulated.

## Risks and Edge Cases
Changing re-exports can break downstream modules that import `KvService`, flashback helpers, or batch-command aliases from `server::service`. Because `log_net_error!` matches only `server::Error::Grpc`, wrapped or converted gRPC errors may be logged at `debug!` instead of `info!`. The macro consumes the error expression into a local binding, so callers cannot reuse that expression afterward.

## Test Signals
There are no local tests. Compile-time use sites validate module visibility and macro availability. Runtime logging behavior is indirectly exercised by service tests and integration tests that trigger gRPC failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/snap.rs -->
# sources/storage-engines/tikv/src/server/snap.rs

## Purpose
`snap.rs` implements TiKV's v1 snapshot transport worker. It sends raft snapshots to remote TiKV nodes over gRPC, receives incoming snapshot chunk streams, writes snapshot files through `SnapManager`, feeds completed snapshot raft messages back into raftstore, enforces snapshot send/receive concurrency limits, refreshes snapshot I/O limits from dynamic config, and delegates tablet-snapshot receive traffic for raftstore v2/TiFlash cases.

## Important APIs, Types, and Functions
`Task` is the worker input enum: `Recv` for v1 snapshot client-streaming RPCs, `RecvTablet` for raftstore-v2 tablet snapshot duplex streams, `Send` for outbound snapshots, `RefreshConfigEvent`, and `Validate`. `Runner<R: RaftExtension>` implements `Runnable<Task>` and owns the gRPC environment, `SnapManager`, Tokio runtime, raft router, security manager, config tracker/current config, and atomic send/receive counters.

`send_snap` builds an outbound gRPC snapshot future. It decodes `RaftSnapshotData` from the raft message, derives a `SnapKey`, registers `SnapEntry::Sending`, opens the snapshot file, streams a first chunk containing the raft message followed by file chunks, waits for the remote `Done`, records stats, deregisters, and deletes the local sending snapshot.

`SnapChunk` is a `Stream` over `(SnapshotChunk, WriteFlags)`. It emits the first metadata chunk, then reads the snapshot file in `SNAP_CHUNK_LEN` one-megabyte chunks under the correct `IoType`.

`RecvSnapContext` parses the first inbound chunk, verifies it contains a raft message, derives the snapshot key and I/O type, opens a receiving snapshot file unless it already exists, and later `finish`es by saving the file and feeding the raft message to `RaftExtension`.

`recv_snap` consumes the inbound stream. It creates a receive context, registers `SnapEntry::Receiving`, writes every non-empty data chunk, saves the file, feeds raftstore, and replies with `Done` or a gRPC failure. `cleanup_after_recv` releases the receive counter and notifies `SnapManager::recv_snap_complete`.

Config and limit helpers include `get_snap_timeout`, `Runner::refresh_cfg`, and `Runner::receiving_busy`. `DEFAULT_POOL_SIZE`, `SNAP_SEND_TIMEOUT_DURATION`, `MIN_SNAP_SEND_SPEED`, and `SNAP_CHUNK_LEN` define runtime defaults.

## Control Flow
Outbound snapshot flow starts when raftstore schedules `Task::Send`. The runner rejects the task if `sending_count` has reached `concurrent_send_snap_limit`; otherwise it increments the counter, calls `send_snap`, spawns the returned future on the snapshot runtime, and invokes the supplied callback with success or failure. `send_snap` sends the raft snapshot message before data bytes so the receiver can derive metadata and open the correct file. It races send/receive completion against a timeout computed as the larger of the default timeout and `size / MIN_SNAP_SEND_SPEED`.

Inbound v1 flow starts when `kv.rs` schedules `Task::Recv` from the gRPC `snapshot` service method. The runner checks `receiving_busy`, increments `recving_count`, and spawns `recv_snap`. `recv_snap` reads the head chunk, initializes `RecvSnapContext`, records the region id for cleanup, writes remaining chunks into the receiving snapshot file, and finally calls `finish` to save and feed the raft message. The sink returns `Done` only after the snapshot has been saved and delivered to raftstore.

Inbound tablet flow is similar at the runner level but delegates the stream to `crate::server::tablet_snap::recv_snap` with a tablet snapshot manager, raft router, limiter, and the v1 `SnapManager` for shared receive-complete coordination. If tablet snapshots are unsupported, it fails the stream with `UNIMPLEMENTED`.

Dynamic config refresh arrives as `Task::RefreshConfigEvent`. The runner pulls from `VersionTrack<Config>`, updates snapshot speed limit, max total snapshot size, minimum ingest CF size, concurrent receive limit, and its local config copy. `Task::Validate` gives tests or callers a read-only view of the current config.

## State and Persistence Behavior
Snapshot file state is mediated by `SnapManager`. Sending registers `SnapEntry::Sending` and deregisters through `DeferContext`; receiving registers `SnapEntry::Receiving` and deregisters with `defer!`. The send path deletes the local sending snapshot after the remote side responds or the send fails. The receive path writes chunk bytes into a snapshot file, calls `Snapshot::save`, and only then feeds the raft message with the `is_snapshot` flag set.

`recving_count` and `sending_count` are process-local concurrency guards. `cleanup_after_recv` decrements receive count and calls `recv_snap_complete(region_id)` so the snapshot manager's limiter releases region-level resources. Snapshot statistics are collected after successful sends when total duration is at least one second, including transport size, generate duration, send duration, and total duration.

I/O classification is preserved from snapshot metadata: balance snapshots use `IoType::LoadBalance`, other snapshots use `IoType::Replication`. `WithIoType` wraps file reads, writes, saves, and receives so lower layers can account or throttle by I/O class.

## Dependencies and Integration Points
The module depends on `grpcio` client/server streaming primitives, `kvproto` raft snapshot messages and PD snapshot stats, `SnapManager`/`SnapKey`/`Snapshot`, `SecurityManager` for secure outbound channels, `tikv_kv::RaftExtension` for delivering completed snapshots, TiKV config tracking, global timer, metrics, failpoints, Tokio runtime construction, and tablet snapshot support. `kv.rs` schedules receive tasks, while raftstore schedules send tasks with callbacks.

Outbound connections use the server `Config` gRPC settings for stream window size, keepalive, compression algorithm/level, and minimum compression size. Security setup is centralized through `security_mgr.connect`.

## Risks and Edge Cases
The first chunk is mandatory and must contain the raft message; empty streams or data-only first chunks fail. Empty data chunks after the head are treated as errors. If the receiving snapshot file already exists, the receiver skips byte reception and immediately feeds the raft message, relying on `SnapManager` file presence as idempotence.

Timeout behavior scales with snapshot size, but very slow networks below `MIN_SNAP_SEND_SPEED` can still fail. Send completion deletes the snapshot file even after errors, so callers must be prepared to regenerate failed snapshots. Counter cleanup is manual; v1 receive uses `cleanup_after_recv`, while tablet receive decrements directly after the delegated future. Any future refactor must preserve decrement and `recv_snap_complete` ordering.

Concurrency checks happen before incrementing counters and are process-local. Config refresh changes limits asynchronously, so an already-running workload may temporarily exceed a newly lowered limit. `Task::Send` clones `self.cfg` before calling `send_snap`, so an in-flight send uses the config snapshot from scheduling time.

## Test Signals
This file contains no local unit tests, but it is instrumented with failpoints for send errors, send timer delay, send timeout duration, delete-after-send, send task scheduling, receive callbacks, and receive network errors. Useful coverage should exercise missing snapshot files, timeout selection by size, first-chunk validation, existing-file receive idempotence, receive cleanup on success and failure, send/receive concurrency limits, config refresh effects on `SnapManager`, and tablet-snapshot unsupported behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/snap.rs -->
