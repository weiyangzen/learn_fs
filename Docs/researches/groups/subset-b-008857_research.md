# subset-b-008857 Research

Grouped research for TiKV raftstore worker sources under `sources/storage-engines/tikv/components/raftstore/src/store/worker`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/pd.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/pd.rs

## Purpose
This file implements the raftstore PD worker: the asynchronous bridge between local raftstore state and the placement driver (PD). It reports region and store heartbeats, asks PD for split IDs, receives PD scheduling decisions, validates stale peers, forwards PD-directed admin commands into raftstore, reports read/write/store/CPU/bucket statistics, updates slow-score health data, controls gRPC serving state, and coordinates unsafe recovery and graceful shutdown state.

It also owns `StatsMonitor`, a side thread that periodically samples process/thread statistics, feeds the auto-split controller, and schedules latency inspection tasks back to the PD worker.

## Important APIs, Types, and Functions
`FlowStatistics`, `ReadStats`, and `WriteStats` integration is exposed through `FlowStatsReporter`, whose `Scheduler<Task<EK>>` implementation wraps read/write flow reports into PD worker tasks.

`HeartbeatTask` contains the region-heartbeat payload collected by peers: term, region, leader peer, down/pending peers, written bytes/keys, approximate size/keys, replication status, and waiting-data peers.

`Task<EK>` is the central work enum. Important variants include split requests (`AskSplit`, `AskBatchSplit`, `AutoSplit`), PD heartbeats (`Heartbeat`, `StoreHeartbeat`), split/peer validation (`ReportBatchSplit`, `ValidatePeer`), metric ingestion (`ReadStats`, `WriteStats`, `StoreInfos`, `RegionCpuRecords`, `ReportBuckets`), lifecycle hooks (`DestroyPeer`, `GracefulShutdownState`), timestamp safety (`UpdateMaxTimestamp`), query/latency/control paths (`QueryRegionLeader`, `UpdateSlowScore`, `InspectLatency`, `ControlGrpcServer`), and resolved-ts reporting.

`StoreStat` tracks store-wide cumulative and last-reported counters: engine read bytes/keys/query stats, last capacity/used/available bytes, histogram locals for region read/write rates, sampled CPU and IO rate records, and CPU busy thresholds. `PeerStat` tracks per-region cumulative read/write/query/cop statistics plus last region-heartbeat and store-heartbeat baselines. `ReportBucket` stores current and previously reported bucket stats and emits deltas.

`StatsMonitor<T>` starts/stops the stats sampling thread. `collect_store_infos()` samples `ThreadInfoStatistics`; `load_base_split()` flushes the auto-split controller, read stats, and CPU stats into split recommendations; `maybe_send_read_stats()` and `maybe_send_cpu_stats()` use bounded sync channels so the monitor cannot accumulate unbounded memory.

`Runner<EK, ER, T>` is the PD worker `Runnable`. It stores the PD client, raft router, shared per-region stats map, bucket stats, store stats, stats monitor, heartbeat interval, CPU-record accumulators for region and store heartbeats, concurrency manager, snapshot manager, async runtime remote, health reporter/controller, coprocessor host, optional causal timestamp provider, gRPC service manager, graceful-shutdown flag, and split validator.

Helper constructors build raft admin requests: `new_change_peer_request()`, `new_change_peer_v2_request()`, `new_split_region_request()`, `new_batch_split_region_request()`, `new_transfer_leader_request()`, `new_merge_request()`, and `new_batch_switch_witness()`. `send_admin_request()` wraps those into `RaftCommand`s and sends them through `RaftRouter`; `send_destroy_peer_message()` sends a tombstone raft message for stale peers.

## Control Flow
`Runner::new()` initializes store CPU quota thresholds, starts `StatsMonitor`, creates the health reporter, initializes all accumulators, and captures service/control dependencies. The first call to `run()` lazily schedules `schedule_heartbeat_receiver()`, which subscribes to PD region-heartbeat responses and converts PD operators into local actions: change peer, change peer v2, transfer leader, split, merge, witness switching, or auto-split enable/disable.

Split tasks call PD asynchronously through `ask_split()` or `ask_batch_split()`. On success, the worker sends a split admin request to raftstore. If `ask_batch_split()` returns `Error::Incompatible`, it falls back to single-key `AskSplit` for rolling-upgrade compatibility. Load-based split callbacks update load-split success/failure metrics.

`Task::Heartbeat` computes per-region deltas from `PeerStat`, consumes the region's CPU record from `region_cpu_records_since_region_heartbeat`, updates last-report baselines, and calls `handle_heartbeat()` to send `pd_client.region_heartbeat()` asynchronously. `Task::StoreHeartbeat` calls `handle_store_heartbeat()`, which consumes store-heartbeat peer deltas and CPU records for real heartbeats, computes hotspot peer stats, fills store capacity/usage/read/query/CPU/IO/slow-score/gRPC/shutdown fields, and sends `pd_client.store_heartbeat()`. Store-heartbeat responses can update replication mode, execute unsafe recovery plans, awaken hibernated regions in batches, schedule gRPC pause/resume, and mark the snapshot manager offline/serving based on PD node state.

`Task::ReadStats` and `Task::WriteStats` update cumulative store and peer counters. Read stats also merge bucket data and feed `StatsMonitor` for auto-split. `Task::RegionCpuRecords` sends raw records to the auto-split lane and accumulates CPU time into both region-heartbeat and store-heartbeat maps. `Task::ReportBuckets` merges bucket stats and reports a delta to PD.

Latency inspection is driven by `StatsMonitor` scheduling `InspectLatency`. `handle_inspect_latency()` ticks the health reporter, may force a fake store heartbeat when raft disk slow score reporting is delayed, builds a `LatencyInspector`, and sends a `StoreMsg::LatencyInspect` into raftstore. The async inspector callback schedules `UpdateSlowScore`, where the worker records measured durations.

`UpdateMaxTimestamp` loops asynchronously while the region's `TxnExt.max_ts_sync_status` remains at the initial value. It either flushes a rawkv v2 causal timestamp provider or fetches a TSO from PD, then updates `ConcurrencyManager::update_max_ts()` and marks the status as synced with a compare-exchange.

## State and Persistence Behavior
Most state is in memory and is deliberately delta-based. `PeerStat` and `StoreStat` cumulative counters are never persisted by this worker; heartbeat handlers store "last reported" snapshots so PD receives interval deltas. Destroyed peers are removed from `region_peers` and both CPU accumulator maps by `remove_peer_stat_from_maps()`.

CPU records have two independent lifetimes. Region-heartbeat records are consumed by individual region heartbeats; store-heartbeat records are consumed by real store heartbeats. Fake store heartbeats intentionally do not consume peer deltas or CPU records, preserving the next real heartbeat's full interval.

Bucket reporting keeps current bucket stats plus the last reported bucket metadata/stats. `ReportBucket::new_report()` recalculates old stats against current metadata before subtracting, handling bucket boundary changes.

Persistent effects occur through external systems rather than local files: PD heartbeats and reports mutate PD's cluster view; raft admin requests are proposed through raftstore and persisted by raft consensus/apply paths; unsafe recovery and tombstone messages are routed into raftstore; gRPC pause/resume changes service state; `UpdateMaxTimestamp` updates the concurrency manager's max timestamp for correctness after leader movement or rawkv v2 causal timestamp flush.

`collect_engine_size()` delegates to `CoprocessorHost` observers when available, otherwise reads disk capacity/usage/availability from the host. Snapshot manager offline state is toggled from PD store node state.

## Dependencies and Integration Points
The worker depends heavily on `pd_client::PdClient` for split ID allocation, region/store heartbeats, heartbeat-response streaming, resolved-ts reports, region lookups, and leader queries. `RaftRouter` is the local integration point for admin commands, casual messages, store control messages, latency inspection, unsafe recovery actions, and raft tombstones.

Stats and load-split integration spans `AutoSplitController`, `AutoSplitControllerContext`, `SplitValidator`, `ThreadInfoStatistics`, `resource_metering::{Collector, RawRecords, RegionCpuRecord}`, `TopN`, and raftstore worker metrics. Health integration uses `health_controller::{HealthController, RaftstoreReporter, LatencyInspector, InspectFactor}`.

Coprocessor hooks include `on_region_heartbeat()` and `on_compute_engine_size()`. Timestamp safety integrates with `ConcurrencyManager`, `CausalTsProviderImpl`, `TxnExt`, and PD TSO. Runtime async work is spawned on a `yatp::Remote`.

PD response operations integrate with raftstore admin command builders and `StoreMsg` variants. Unsafe recovery integrates with `UnsafeRecoveryForceLeaderSyncer`, `UnsafeRecoveryExecutePlanSyncer`, and `UnsafeRecoveryHandle`. Service control integrates with `GrpcServiceManager` and global readiness state.

## Risks and Edge Cases
Heartbeat data is delta-based, so incorrect baseline updates can under-report or double-report load. The file deliberately treats fake store heartbeats differently from real ones; changing that distinction could consume CPU/read deltas prematurely and hide a full interval from PD.

CPU accounting is approximate and path-specific. Region CPU records only include outside RPC workloads, and the write path currently accounts mainly lock checking. Store-heartbeat hotspot admission uses unified-read CPU for read hotspots and reports scheduler CPU separately; folding scheduler CPU into admission would change PD hotspot behavior.

The stats monitor uses bounded channels and drops samples when full. This prevents memory buildup but means auto-split and CPU-based decisions can miss data under sustained pressure. Tick interval math skips monitoring when configured intervals become too small, especially under failpoint/test settings.

Asynchronous PD operations can race local region changes. Split requests use a `SplitValidator` to disable some load splits, but stale regions, epoch changes, PD incompatibility, or router send failures still need to be handled by callbacks and metrics. Heartbeat response handling assumes PD response ordering and region epochs are sufficient to safely convert operators to local commands.

`UpdateMaxTimestamp` loops until status changes or succeeds; repeated PD/causal-provider failures log periodically but keep retrying. Service pause/resume from PD can make local availability depend on health-controller state and PD decisions.

## Test Signals
In-file tests cover stats monitor collection, top-N hotspot peer selection, CPU threshold admission, orphan CPU-record cleanup, zero-interval CPU handling, unified-read versus scheduler CPU treatment, CPU accumulation before rounding, report interval start fallback, peer-stat removal, region CPU record aggregation by store/region, bucket delta recalculation across boundary changes, coprocessor-provided engine size, and bounded stats monitor channels.

Additional useful signals are integration tests for PD heartbeat response operators, split fallback on incompatible PD, fake versus real store heartbeat delta preservation, unsafe recovery routing, gRPC pause/resume, max-ts retry and stale-status behavior, and load-split callback metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/pd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/raftlog_gc.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/raftlog_gc.rs

## Purpose
This file implements the background worker that garbage-collects obsolete raft log entries from the raft engine. It batches region log-GC requests, syncs the KV engine before deletion to preserve the "applied data is durable before its raft log is removed" invariant, writes raft-engine GC batches, and invokes optional completion callbacks after the batch has been consumed.

## Important APIs, Types, and Functions
`Task` carries one GC range: `region_id`, `start_idx`, `end_idx`, a `flush` flag, and an optional one-shot callback. `Task::gc(region_id, start, end)` constructs a normal GC task; `flush()` forces the runner to flush after enqueueing the task; `when_done()` attaches a callback invoked after the flush path finishes writing the raft batch.

`Runner<EK, ER>` stores queued tasks, `Engines<EK, ER>`, and `compact_sync_interval`. `Runner::new()` wires those dependencies. `raft_log_gc()` consumes a raft log batch with `sync=false` and exposes failpoints around the write. `flush()` is the core implementation. The runner implements both `Runnable` and `RunnableWithTimer`.

Constants control batching and logging: `MAX_GC_REGION_BATCH` flushes after more than 512 queued tasks, and `MAX_REGION_NORMAL_GC_LOG_NUMBER` marks unusually large per-region ranges for warning logs. Metrics include KV sync duration, raft write duration, failed GC count, and seek-operation count for `start_idx == 0`.

## Control Flow
`Runnable::run()` marks the operation as foreground-write IO, saves whether the task requested `flush`, pushes it into `tasks`, and calls `flush()` if the task requested flushing or the queue exceeds the batch limit. `RunnableWithTimer::on_timeout()` also calls `flush()`, and `shutdown()` flushes remaining work.

`flush()` returns immediately when no tasks are queued. Otherwise it hits the `worker_gc_raft_log_flush` failpoint, synchronously calls `kv.sync()` and panics on sync failure, takes the task queue, allocates a raft log batch sized to the task count, and iterates tasks. Callbacks are saved separately. Empty ranges (`start_idx == end_idx`) are treated as flush-only barriers. Non-empty ranges call `engines.raft.gc(region_id, start_idx, end_idx, &mut batch)`, logging and counting failures per task. After the loop, `raft_log_gc(batch)` consumes the batch; callbacks run after that attempt.

## State and Persistence Behavior
The only local state is the in-memory pending task queue. Persistence behavior is the file's main concern: it syncs the KV engine before consuming the raft log batch so applied key/value data is durable before raft logs needed for recovery are discarded. Raft log deletion is persisted by the raft engine's `gc()` plus `consume()` path.

The task callback is not a durability callback for KV sync alone; it runs after the raft batch consume attempt returns, even if some individual GC calls failed or the final consume failed. Empty-range tasks can be used as a flush/callback barrier without deleting logs.

## Dependencies and Integration Points
The worker is generic over `KvEngine` and `RaftEngine` and receives both through `engine_traits::Engines`. It relies on `RaftEngine::log_batch()`, `RaftEngine::gc()`, and `RaftEngine::consume()`, plus `KvEngine::sync()`.

It integrates with TiKV's worker framework through `Runnable` and `RunnableWithTimer`, with IO classification through `file_system::WithIoType(IoType::ForegroundWrite)`, with failpoints for test/fault injection, and with raftstore metrics in `store::worker::metrics`.

Upstream callers are raftstore peers or compact-log scheduling paths that know the safe `[start_idx, end_idx)` range after apply/compact progress.

## Risks and Edge Cases
The correctness-critical risk is deleting raft logs before applied KV data is durable; this is why `kv.sync()` occurs before raft deletion and panics on failure. Any future async/batched change must preserve that ordering.

Callbacks always run after the flush attempt, not only after successful deletion. If callers interpret callbacks as success notifications, failed `gc()` or `consume()` paths could cause incorrect assumptions. The code records metrics and logs but does not retry failed tasks after taking them from the queue.

Large GC ranges are allowed but warned about. `start_idx == 0` increments a seek metric because it likely forces range scanning from the beginning. Flush-only tasks use `start_idx == end_idx`, which means callers must not expect an empty range to validate region state.

## Test Signals
The in-file `test_gc_raft_log` creates test KV/raft engines, writes raft entries `0..100`, then verifies successive GC ranges remove exactly `[0,10)`, `[0,50)`, ignore an empty `[50,50)` range, and remove `[50,60)` while preserving later entries.

Additional useful tests would cover forced flush callbacks, timer/shutdown flush, injected raft consume failure, injected per-task `gc()` failure, and verifying callback semantics under failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/raftlog_gc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/read.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/read.rs

## Purpose
This file implements raftstore's local read fast path. It lets eligible read-only raft commands bypass the raft proposal path when local metadata proves the read is safe: leader lease reads, stale reads guarded by safe timestamps, and follower-read-cache reads. It maintains cached `ReadDelegate`s derived from raftstore peer state, validates request headers and region state, manages snapshot reuse for batched reads, executes read commands against the KV engine snapshot, and redirects unsafe or unsupported requests back to raftstore.

## Important APIs, Types, and Functions
`ReadExecutor` abstracts execution over a tablet/KV engine. It provides `get_tablet()`, `get_snapshot()`, `get_value()`, and `execute()`. `execute()` handles `Get`, `Snap`, and `ReadIndex` commands and returns `ReadResponse`, including `RegionSnapshot` and coprocessor snapshot observation when `ReadContext.read_ts` is present.

`CachedReadDelegate<E>` wraps an `Arc<ReadDelegate>` with the KV engine clone needed to obtain snapshots. It implements `Deref<Target = ReadDelegate>`, `Clone`, and `ReadExecutor`.

`LocalReadContext<'a, E>` and `SnapCache<E>` control snapshot reuse. A `ThreadReadId` lets multiple commands from the same RPC batch share one engine snapshot if the cached read ID matches and the delegate has not changed since the read ID was created. Stale reads pass `None` and use a per-request snapshot instead.

`ReadExecutorProvider` abstracts access to source delegates. `StoreMetaDelegate<E>` implements it by locking `StoreMeta`, reading `store_id`, cloning `StoreMeta.readers[region_id]`, and returning the current reader-map length for LRU sizing.

`TrackVer` is the version invalidation primitive. Source delegates stored in `StoreMeta` have `source=true` and increment a shared atomic on updates/drop/pending-remove; cloned local delegates record the version at clone time and use `any_new()` to detect staleness.

`ReadDelegate` is the read-only peer view: region, peer id, term, applied term, optional remote leader lease, `last_valid_ts`, tag, bucket metadata, transaction extra-op state, transaction extension, `RegionReadProgress`, pending-remove flag, wait-data flag, and `TrackVer`. Key methods include `from_peer()`, `new()`, `update(Progress)`, `mark_pending_remove()`, `is_in_leader_lease()`, `maybe_renew_lease_advance()`, and `check_stale_read_safe()`.

`Progress` enumerates delegate updates: region, term, applied term, leader lease set/unset, region bucket metadata, and wait-data state.

`LocalReaderCore<D, S>` owns per-thread cached delegates in an LRU and validates request metadata. `LocalReader<E, C>` is the main fast-path reader with `propose_raft_command()`, `pre_propose_raft_command()`, `try_local_leader_read()`, `try_local_stale_read()`, `try_local_follower_read()`, `redirect()`, `read()`, and `release_snapshot_cache()`.

`Inspector` implements `RequestInspector` over a `ReadDelegate`, requiring `applied_term == term` and deferring exact lease timestamp validation until after snapshot acquisition.

## Control Flow
A caller enters through `LocalReader::read()` or `propose_raft_command()`. The reader increments local-read metrics, calls `pre_propose_raft_command()`, and either receives a delegate plus request policy, receives `None` and redirects to raftstore, or receives an error and completes the callback with an error response.

`LocalReaderCore::validate_request()` lazily caches store ID, checks store ID, loads or refreshes the region delegate from `StoreMeta`, rejects missing or pending-remove delegates, checks peer ID, term, region epoch, witness status, wait-data state, and flashback constraints. Stale epoch returns `Ok(None)` so raftstore can handle the request with fresher metadata.

`pre_propose_raft_command()` runs `Inspector::inspect()` and accepts local policies `ReadLocal`, `StaleRead`, `ReadIndexReplicaRead`, and `ReadIndex`. Other policies fall back to raftstore. `ReadIndex` is explicitly redirected because it still needs raft consensus.

For `ReadLocal`, `try_local_leader_read()` creates a `LocalReadContext`, obtains/reuses a snapshot before checking the lease, validates the snapshot timestamp against the remote leader lease, executes the read, attaches bucket metadata, and may send `CasualMessage::RenewLease` if the lease is near expiration. If the lease is invalid, the original command is redirected.

For `StaleRead`, `try_local_stale_read()` decodes the read timestamp from header flag data, checks `RegionReadProgress.safe_ts()` or `read_index_safe_ts()`, obtains a per-request snapshot, executes the read, attaches bucket metadata, then checks stale-read safety again to catch a race where safe ts regressed or became insufficient around snapshot creation. If a stale read is not safe and the same local peer is currently a valid leader, the code clears the stale-read flag and attempts a leader-lease fallback; otherwise it returns `DataIsNotReady`.

For `ReadIndexReplicaRead`, `try_local_follower_read()` decodes a nonzero read timestamp and internally attempts the stale-read path. If it cannot serve locally, it redirects to raftstore for normal read-index handling.

After local execution, the reader marks the read tracker as local, updates metrics, binds the delegate term to the response, attaches `txn_ext` and bucket metadata to snapshots, copies `txn_extra_op`, and invokes the callback. Redirects use `ProposalRouter`; full channels return `server_is_busy`, and disconnected channels return `region_not_found`.

## State and Persistence Behavior
This file does not persist raft or KV state. It reads from engine snapshots and from raftstore metadata maintained elsewhere. Its state is safety metadata and caches: per-thread delegate LRU, snapshot cache, delegate versions, lease timestamps, safe timestamps, and transaction/coprocessor attachments.

Snapshot timing is central. For cached reads, the engine snapshot is acquired before a monotonic timestamp is recorded, with a release fence between the two. The lease check uses that snapshot timestamp, ensuring the snapshot was created while the leader lease was valid. Delegate `last_valid_ts` invalidates reuse when metadata changes after the `ThreadReadId` was created.

Stale reads intentionally do not use the shared `SnapCache`; they use per-request snapshots so stale-read and normal local-read batches cannot invalidate each other incorrectly. `release_snapshot_cache()` clears the cached read ID and snapshot, releasing engine snapshot resources such as RocksDB sequence-number retention.

`ReadDelegate` source instances in `StoreMeta` own the version clock. Updating region/term/applied term/lease/buckets/wait-data or marking pending remove increments the version. Dropping the source delegate also increments, allowing local caches to discover removal.

## Dependencies and Integration Points
The local reader depends on raftstore peer metadata (`Peer`, `StoreMeta`, `RegionReadProgress`, `RemoteLease`, `LeaseState`, `TxnExt`), routing traits (`ProposalRouter`, `CasualRouter`), command/response types (`RaftCommand`, `Callback`, `ReadResponse`, `ReadContext`), and request policy inspection through `RequestInspector`.

Engine integration uses `KvEngine`, `Peekable`, snapshots, `SnapshotMiscExt::sequence_number()`, and `RegionSnapshot`. Coprocessor integration uses `CoprocessorHost::on_snapshot()` and bucket metadata from PD. Transaction integration uses `TxnExtraOp`, `WriteBatchFlags::STALE_READ`, and `TimeStamp`.

Safety validation relies on `util::check_store_id`, `check_peer_id`, `check_term`, `check_req_region_epoch`, `check_flashback_state`, `check_key_in_region`, `find_peer_by_id`, and `cmd_resp` helpers for errors and term binding. Metrics are emitted through local-read TLS metrics and `GLOBAL_TRACKERS`.

## Risks and Edge Cases
The fast path is correctness-sensitive. A local leader read is only safe if the snapshot was created within the matching-term leader lease; checking the lease before snapshot acquisition would be unsafe. The code's snapshot-then-lease ordering is intentional.

Delegate cache invalidation depends on `TrackVer` increments from every metadata change that can affect safety. Missing an increment would allow stale local metadata; excessive increments reduce cache effectiveness. `RegionBuckets` updates intentionally ignore older or equal versions.

Stale-read safety depends on decoding `flag_data` as a timestamp and checking safe ts before and after snapshot creation. If `flag_data` is malformed, follower-read cache falls back/redirects while stale-read policy can panic via `unwrap()` on decode. Safe ts lag greater than 200 ms triggers resolved-ts advancement notification.

Request validation has several non-obvious fallbacks: stale epochs redirect rather than error, missing delegates redirect, witness and wait-data states return errors, and flashback state can reject local reads. Replica reads without a usable nonzero read timestamp redirect to raftstore.

Snapshot cache lifetime can retain engine resources. Callers handling batched RPCs should release the cache when the batch ends; tests verify cached and noncached paths release oldest snapshot sequence numbers differently.

## Test Signals
The in-file test suite covers local read redirect versus execution, no-region cache misses, stale applied term, valid leader lease reads, store/peer/term/epoch mismatches, read quorum redirect, lease expiration, channel-full busy responses, lease term mismatch, delegate cache refresh after progress updates, source delegate removal invalidation, stale-read safe-ts success/failure, and leader fallback for stale reads.

It also covers `ReadExecutorProvider`, snapshot sharing across regions with the same `ThreadReadId`, snapshot cache invalidation when delegate `last_valid_ts` is newer than read ID creation, explicit snapshot cache release, stale reads bypassing shared cache, resolved-ts notification for stale reads, follower-read cache based on `read_index_safe_ts`, and follower-read fallback to raftstore.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/refresh_config.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/refresh_config.rs

## Purpose
This file implements a raftstore worker for applying runtime configuration changes to batch-system pools and async store IO components. It can resize raft and apply poller thread pools, update their max batch sizes, resize async store writer threads, and resize the snapshot generator/read future pool.

## Important APIs, Types, and Functions
`PoolController<N, C, H>` groups a `BatchRouter` with its `PoolState`. It provides `decrease_by()`, `increase_by()`, and `cleanup_poller_threads()`. `decrease_by()` sends `FsmTypes::Empty` control messages to ask pollers to exit; `increase_by()` builds new handlers/pollers and spawns named worker threads with foreground-write IO type; `cleanup_poller_threads()` joins poller threads that have reported themselves as joinable.

`WriterContoller<EK, ER, T, N>` stores `StoreWritersContext`, `StoreWriters`, and an expected writer count. It exposes getters/setters used by the runner to resize async writer threads. The name is misspelled in code as `Contoller`.

`BatchComponent` distinguishes `Store` (displayed as `raft`) and `Apply`. `Task` is the public work enum: `ScalePool(BatchComponent, usize)`, `ScaleBatchSize(BatchComponent, usize)`, `ScaleWriters(usize)`, and `ScaleAsyncReader(usize)`.

`Runner<EK, ER, AH, RH, T>` owns the writer controller, apply pool controller, raft pool controller, and snapshot generator `FuturePool`. Its resize helpers are `resize_raft_pool()`, `resize_apply_pool()`, `resize_store_writers()`, and `resize_snap_generator_read_pool()`.

## Control Flow
`Runner::new()` wraps the writer metadata/writers and both batch-system pool states into controllers. `Runnable::run()` pattern-matches tasks and dispatches to the appropriate helper.

Pool resizing reads `expected_pool_size`, updates it to the requested size, compares old and new sizes, sends empty FSMs to shrink or spawns poller threads to grow, then calls `cleanup_poller_threads()` and logs the result. If the size is unchanged, it returns early.

`increase_by()` clones thread-group properties, creates a normal-priority handler, constructs a `Poller` with the shared router/receiver/max batch settings, spawns a named thread using `spawn_wrapper`, sets the inherited thread-group properties, marks IO type as foreground write, and calls `poller.poll()`. The controller increments `id_base` after spawning so future thread names remain unique.

Store writer resizing updates the expected writer size, then calls `StoreWriters::decrease_to(size)` or `increase_to(size, writer_meta.clone())`. Local cached writers in pollers are not updated immediately; comments state each poller corrects its local cache on its next `poller.begin()`.

Snapshot generator pool resizing calls `FuturePool::scale_pool_size(size)`, then compares the requested size with `thread_count_limit()`. Out-of-bound sizes are clamped by the pool and logged as warnings; in-bound sizes are logged as resizes.

Batch-size tasks directly assign `state.max_batch_size` for the selected raft/apply pool.

## State and Persistence Behavior
All effects are in-memory process state. The file does not persist configuration. Resized pool sizes live in `PoolState.expected_pool_size`, `PoolState.max_batch_size`, `StoreWriters` internal thread state, `WriterContoller.expected_writers_size`, and the `FuturePool` worker count.

Shrinking a batch-system pool is cooperative: empty FSM messages cause pollers to drop, and poller drop records thread IDs into `joinable_workers`. `cleanup_poller_threads()` then joins and removes those handles from `workers`. The lock order is intentionally `workers` then `joinable_workers` to avoid deadlock with batch-system shutdown.

Store writer resize state can be temporarily inconsistent because pollers keep local cached writers until the next poller begin cycle. The explicit expected size records the intended target even if `increase_to()` or `decrease_to()` logs an error.

## Dependencies and Integration Points
The code integrates with `batch_system` types (`BatchRouter`, `Fsm`, `HandlerBuilder`, `Poller`, `PoolState`, `Priority`) and concrete raftstore FSMs (`PeerFsm`, `StoreFsm`, `ApplyFsm`, `ControlFsm`). It depends on `StoreWriters` and `StoreWritersContext` from async IO write support, `RaftRouter` as persisted notifier, `Transport`, and `FuturePool` from `tikv_util::yatp_pool`.

Thread behavior integrates with TiKV thread naming (`thd_name!`), `StdThreadBuildWrapper`, thread-group property propagation, and `file_system::set_io_type(IoType::ForegroundWrite)`.

Operationally, tasks are produced by configuration-refresh code elsewhere in raftstore when runtime config values such as raft/apply pool size, max batch size, store IO pool size, or snapshot generator pool size change.

## Risks and Edge Cases
The pool shrink path depends on pollers processing `FsmTypes::Empty`; if a poller is stuck, cleanup may not find/join it promptly. The explicit lock-order comment indicates deadlock risk if shutdown and cleanup acquire locks differently.

`expected_pool_size` and `expected_writers_size` are updated before resize operations can fail. If thread spawning panics or writer resize returns an error, the recorded expected size can diverge from actual workers. `increase_by()` unwraps thread spawn failures, so OS thread creation failure panics the worker.

Changing `max_batch_size` is immediate shared state mutation and does not coordinate with already-running poll loops beyond their normal state access. Snapshot generator pool scaling is advisory and clamped by its configured min/max; warning text mentions "apply pool" even though it is resizing the async reader/snapshot pool.

Thread names for newly increased pools use the local loop index plus `id_base`; after multiple resizes IDs remain unique but not dense. Store writer resizing has an expected transient period where pollers still use stale cached writer handles.

## Test Signals
This file has no local `#[cfg(test)]` module. Useful tests would construct small batch-system pools and verify grow/shrink updates expected sizes, joins exiting pollers without deadlock, preserves thread naming/id base, updates max batch size for raft versus apply independently, handles no-op resize, and logs or clamps out-of-bound snapshot pool sizes.

For writer resizing, tests should verify `increase_to()` receives cloned writer metadata, `decrease_to()` is called with the target size, expected writer size behavior on errors, and poller-local writer cache refresh on subsequent poller begin cycles in integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/refresh_config.rs -->
