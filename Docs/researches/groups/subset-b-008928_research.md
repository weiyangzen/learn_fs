# subset-b-008928 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/rawkv_compaction_filter.rs -->
# sources/storage-engines/tikv/src/server/gc_worker/rawkv_compaction_filter.rs

Purpose: implements the RawKV API v2 RocksDB compaction filter used by GC to remove obsolete RawKV MVCC versions and enqueue asynchronous deletion/TTL cleanup for latest deleted or expired records.

Important APIs/types/functions: `RawCompactionFilterFactory` implements `CompactionFilterFactory`; `RawCompactionFilter` implements `CompactionFilter`; `featured_filter` wraps error handling; `do_filter` owns key/value classification; `raw_gc_mvcc_deletions`, `schedule_gc_task`, and `raw_handle_delete` bridge to `GcTask::RawGcKeys`; `make_key` is test/export support.

Control flow: factory creation is gated by global `GC_CONTEXT`, nonzero safe point, non-stalled DB, and `check_need_gc`. Filtering ignores non-data keys, non-Raw API v2 key modes, and non-value records. For a new user-key prefix, it treats the first version as latest: versions at or above safe point are kept; latest versions below safe point are decoded and, when deleted or expired on the bottommost level, queued for async raw GC while still kept in this compaction pass. Later versions of the same key with commit timestamp below safe point are removed.

State and persistence: the filter holds only per-compaction in-memory state: current key prefix, version counters, pending `mvcc_deletions`, histograms, and an `encountered_errors` fail-open flag. Actual persistence changes happen through RocksDB compaction decisions and later GC worker deletes. `Drop` flushes pending async deletions and metrics before compaction result installation.

Dependencies and integration: depends on `api_version::ApiV2`, RocksDB raw compaction filter traits, `ttl_current_ts`, `RegionInfoProvider`, GC worker scheduling, and MVCC/GC metrics. It is specific to RawKV key mode under API v2 and uses raftstore region info for the later async delete task.

Risks: malformed API v2 keys or raw values make the filter fail open for the rest of the compaction, preserving data but reducing GC. Scheduler saturation drops async latest-delete cleanup and records failure metrics. Only bottommost compactions enqueue latest deleted/expired keys, so behavior depends on compaction level. Prefix tracking assumes keys are visited in RocksDB order.

Test signals: unit tests verify safe-point removal/retention boundaries, equality to safe point, deleted latest-version async GC, expired latest-version async GC, and generated raw key encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/gc_worker/rawkv_compaction_filter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/load_statistics/linux.rs -->
# sources/storage-engines/tikv/src/server/load_statistics/linux.rs

Purpose: Linux implementation of thread load statistics for selected TiKV threads, feeding shared `ThreadLoadPool` atomics that other code can use to detect heavy load.

Important APIs/types/functions: `ThreadLoadStatistics::new(slots, prefix, thread_loads)` discovers current process threads whose command starts with `prefix`; `record(instant)` samples `/proc/<pid>/task/<tid>` CPU counters; `calc_cpu_load` converts CPU counter deltas over elapsed milliseconds into a percentage-like integer.

Control flow: construction captures the process id, scans thread ids, filters by thread-name prefix, initializes an atomic load entry per matching tid, and seeds a ring buffer of CPU totals and instants. `record` writes the current slot, refreshes known tids, compares against the oldest slot in the ring, updates each thread's atomic load, and stores total load.

State and persistence: all state is in-memory. The object owns a fixed-size ring of historical CPU usage snapshots, a static tid list, and a shared `Arc<ThreadLoadPool>`. No persistent data is written.

Dependencies and integration: uses `tikv_util::sys::thread` for Linux `/proc` access and `ThreadLoadPool` from the sibling module. `raft_client` consumes the load pool indirectly to delay raft batch flushing under heavy send-thread load.

Risks: threads created after `new` are not discovered and exited/restarted tids are not refreshed. `thread_ids(pid).unwrap()` can panic if process thread enumeration fails. CPU load is clamped to 100 per thread, which hides oversubscription detail for individual threads but keeps threshold checks simple.

Test signals: `test_thread_load_statistic` starts a named busy-loop thread, records high load, then sleeps and verifies the load drops below threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/load_statistics/linux.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/load_statistics/mod.rs -->
# sources/storage-engines/tikv/src/server/load_statistics/mod.rs

Purpose: provides the platform-neutral public surface for thread load tracking and exports the Linux implementation or a non-Linux no-op implementation.

Important APIs/types/functions: `ThreadLoadPool::with_threshold`, `current_thread_in_heavy_load`, and `total_load` are the main API. Thread-local `CURRENT_LOAD` caches the current thread's atomic load entry. `ThreadLoadStatistics` is re-exported from `linux` on Linux and from `other_os` elsewhere.

Control flow: `current_thread_in_heavy_load` lazily inserts or retrieves the current thread id in the shared `stats` map, then compares the atomic load against the configured threshold. `total_load` reads the aggregate atomic. Non-Linux `ThreadLoadStatistics` accepts calls but records nothing.

State and persistence: state is process-local: a mutex-protected map of thread ids to atomics, a threshold, an aggregate atomic, and thread-local cached handles. No persistence or network behavior exists.

Dependencies and integration: uses `parking_lot::Mutex`, TiKV thread id helpers, and is integrated by components that need adaptive behavior under CPU load, notably raft batching.

Risks: the current-thread cache can create entries that are never sampled by a `ThreadLoadStatistics` collector if the thread did not match the collector prefix. Relaxed atomics are appropriate for approximate metrics but should not be treated as synchronization. Non-Linux behavior silently reports no load.

Test signals: direct tests live in `linux.rs`; module-level behavior is covered through that implementation and downstream consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/load_statistics/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/client.rs -->
# sources/storage-engines/tikv/src/server/lock_manager/client.rs

Purpose: deadlock detector follower-side gRPC client wrapper for the bidirectional `Detect` stream to the current detector leader.

Important APIs/types/functions: `env()` builds the shared gRPC environment; `Client::new` creates a `DeadlockClient` channel through `SecurityManager`; `register_detect_handler` creates send/receive futures for the streaming RPC; `detect` enqueues `DeadlockRequest`s onto the unbounded sender. `Callback` handles `DeadlockResponse`.

Control flow: after construction, `register_detect_handler` opens the `detect` stream, stores an unbounded request sender, creates a send task that forwards channel items to gRPC with default write flags, and creates a receive task that invokes the callback for each response. `detect` pushes requests into the sender and converts send failure into lock-manager `Error`.

State and persistence: client state is only the gRPC stub and optional stream sender. It persists no lock state; the detector leader owns the graph.

Dependencies and integration: depends on `kvproto::deadlock`, `grpcio`, futures mpsc, TiKV security, and the detector thread name prefix. `deadlock.rs` uses this client when a follower forwards local wait-for events to the leader.

Risks: `register_detect_handler` and `detect` use `unwrap` on stream creation and sender presence, so callers must follow lifecycle ordering and handle stream creation assumptions. The unbounded channel can grow if the network stream stalls. Send task cancellation closes the gRPC sink.

Test signals: tested indirectly by detector tests and production stream wiring; no standalone tests in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/config.rs -->
# sources/storage-engines/tikv/src/server/lock_manager/config.rs

Purpose: defines pessimistic transaction lock-manager configuration, validation, backward-compatible duration decoding, and online config dispatch into running manager/detector state.

Important APIs/types/functions: `Config` contains `wait_for_lock_timeout`, `wake_up_delay_duration`, `pipelined`, `in_memory`, and in-memory lock size limits. `readable_duration_or_u64` preserves v3.x numeric millisecond compatibility. `LockManagerConfigManager` implements `ConfigManager::dispatch`.

Control flow: deserialization accepts readable duration strings or unsigned millisecond numbers for duration fields. `validate` rejects zero wait timeout. Online dispatch removes known config changes, forwards timeout changes to waiter manager and deadlock detector TTL, logs wake-up delay changes, and stores feature flags/limits into shared atomics used by storage.

State and persistence: config values are loaded from config files or online config changes; runtime state is stored in scheduler messages and atomics. This file itself does not persist anything.

Dependencies and integration: uses `online_config`, serde, `ReadableDuration`, `ReadableSize`, waiter-manager scheduler, deadlock scheduler, and atomics returned through `LockManager::get_storage_dynamic_configs`.

Risks: zero timeout is invalid because it would immediately fail waits. Dispatch ignores unknown removed keys by design but relies on online-config machinery to supply valid field names. `Ordering::Relaxed` is sufficient for config visibility but not a sequencing primitive.

Test signals: `test_config_deserialize` verifies mixed string/numeric duration parsing and readable size parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/deadlock.rs -->
# sources/storage-engines/tikv/src/server/lock_manager/deadlock.rs

Purpose: implements distributed deadlock detection for pessimistic transactions by maintaining a TTL-bound wait-for graph on a single elected detector leader and forwarding follower wait events to that leader.

Important APIs/types/functions: `DetectTable` stores wait edges and exposes `detect`, cleanup, TTL reset, and wait-chain generation. `Scheduler` wraps `FutureScheduler<Task>`. `RoleChangeNotifier` observes raftstore region/role changes for the leader region containing `LEADER_KEY`. `Detector` owns leader/follower behavior. `Service` exposes deadlock gRPC.

Control flow: local lock waits schedule `Task::Detect`. Leaders process events in `handle_detect_locally`; followers discover the leader via PD, resolve its address, establish a streaming `Client`, and forward `DeadlockRequest`s. `DetectTable::detect` expires old edges, refreshes duplicate edges, searches from lock owner back toward waiter, returns a deadlock key hash plus wait chain if a cycle is found, otherwise registers the edge. Cleanup tasks remove a single lock digest or all entries for a transaction. Incoming remote streams are accepted only while the node is leader.

State and persistence: the wait-for graph, role, cached leader info, and leader client are in memory. Role changes reset graph/client state. Edges expire by timeout and active cleanup. There is no disk persistence; correctness relies on retries/timeouts if detect requests are dropped.

Dependencies and integration: integrates with PD for leader region lookup, store address resolver, raftstore coprocessor observers, gRPC `deadlock` service, waiter manager callbacks, `txn_types::TimeStamp`, and lock diagnostic context including resource group tags.

Risks: dropped follower detect requests can delay deadlock reporting until transaction timeout/retry. Active expiration scans only after a large threshold and interval, so low-volume stale edges are mainly cleaned during searches. Leader changes clear state and can miss transient cycles. The graph stores one diagnostic key per hash, so hash collisions may reduce diagnostic precision.

Test signals: tests cover cycle detection, edge cleanup, TTL expiration, wait-chain reconstruction across graph shapes, role-change notifier behavior for create/update/destroy events, and leader/follower role transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/deadlock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/metrics.rs -->
# sources/storage-engines/tikv/src/server/lock_manager/metrics.rs

Purpose: declares Prometheus metrics for lock-manager tasks, errors, wait lifetimes, detection latency, detector leadership, and wait-table gauges.

Important APIs/types/functions: static metric families include `LocalTaskCounter`, `LocalErrorCounter`, `WaitTableStatusGauge`, `TASK_COUNTER_VEC`, `ERROR_COUNTER_VEC`, `WAITER_LIFETIME_HISTOGRAM`, `DETECT_DURATION_HISTOGRAM`, `DETECTOR_LEADER_GAUGE`, and auto-flushing local handles.

Control flow: there is no runtime control flow beyond lazy registration. Other lock-manager modules increment task/error counters, observe lifetimes and detect duration, and set the leader gauge during role changes.

State and persistence: metrics live in Prometheus registry/global statics and local auto-flush counters. They are process metrics only.

Dependencies and integration: uses `lazy_static`, `prometheus`, and `prometheus_static_metric`. Integrated throughout `deadlock.rs` and `waiter_manager.rs`.

Risks: label sets are fixed at compile time; adding task/error categories requires updating static metric definitions. Metrics registration unwraps and will panic on duplicate registration, as expected for TiKV metric statics.

Test signals: no direct tests; metrics are exercised by lock-manager unit tests that increment counters and observe histograms.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/mod.rs -->
# sources/storage-engines/tikv/src/server/lock_manager/mod.rs

Purpose: top-level server lock manager that wires the waiter manager and deadlock detector workers and implements the storage `LockManager` trait.

Important APIs/types/functions: `LockManager::new`, `start`, `stop`, worker start/stop helpers, `register_detector_role_change_observer`, `deadlock_service`, `config_manager`, `get_storage_dynamic_configs`, and trait methods `allocate_token`, `wait_for`, `update_wait_for`, `remove_lock_wait`, `has_waiter`, `dump_wait_for_entries`.

Control flow: construction creates two `FutureWorker`s and schedulers plus shared atomics. `start` launches the waiter manager and detector; `stop` joins both workers while ignoring join failures. `wait_for` converts no-timeout waits into immediate `KeyIsLocked`, otherwise increments `waiter_count`, schedules waiter registration, and schedules deadlock detection unless this is the transaction's first lock.

State and persistence: worker handles exist only on the owning instance; clones keep schedulers and shared atomics but not worker handles. Token allocation is an atomic counter. Wait state is in the waiter manager; detect graph is in the detector; no state is persisted.

Dependencies and integration: bridges storage lock-manager traits to server implementations, depends on PD, security, raftstore coprocessor host, storage dynamic configs, and lock diagnostic/wait types.

Risks: `waiter_count` is incremented before waiter manager processing to avoid lost wakeups, so scheduling failure paths must decrement through waiter-manager behavior or callback handling. First-lock detection bypass is a correctness/performance assumption for pessimistic transactions. Clones cannot start/stop workers.

Test signals: integration-style unit tests cover timeout, removal, deadlock reporting, first-lock no-detect behavior, no-timeout immediate failure, and clone benchmark.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/waiter_manager.rs -->
# sources/storage-engines/tikv/src/server/lock_manager/waiter_manager.rs

Purpose: manages in-memory lock waiters for pessimistic transactions, delivering callbacks when locks are released, waits time out, wait-for targets change, or deadlocks are detected.

Important APIs/types/functions: `Delay` wraps `tokio_timer::Delay` with cancellation/reset; `Task` enumerates waiter operations; `Waiter` owns transaction wait context and cancellation methods; `WaitTable` indexes waiters by token and `(lock_hash, waiter_ts)`; `Scheduler` exposes task helpers; `WaiterManager` implements `FutureRunnable<Task>`.

Control flow: `Task::WaitFor` normalizes deadline, creates a `Waiter`, inserts it into `WaitTable`, and spawns its timeout future. Timeout removes the waiter, returns `KeyIsLocked`, and asks detector to clean the wait edge. Explicit removal cancels without error and also cleans the detector. Updates replace wait info, track last update time, and for non-first-lock allowed-conflict waits, clean old detector edges and register new detect edges. Deadlock tasks remove the matching waiter and return an MVCC deadlock error.

State and persistence: all waiters are memory-only. `WaitTable` maintains two maps plus shared `waiter_count`. Metrics record waiter lifetime and task counts. No durable state exists; lost state results in timeout/retry behavior at higher layers.

Dependencies and integration: depends on global timer handle, tracker metrics, storage lock-manager types, MVCC/txn errors, detector scheduler, and lock-manager metrics. It is started by `lock_manager/mod.rs`.

Risks: delay cancellation completes at arbitrary time, so removal paths rely on taking the waiter atomically from the table to avoid double callback. The compatibility index by `(hash, waiter_ts)` assumes one relevant waiter per hash/transaction pair. Update logic has explicit caveats for future shared-lock shrink behavior.

Test signals: tests cover delay timeout/reset/cancel, waiter timeout/deadlock callbacks, wait-table add/remove/count/export, default/custom/max timeout behavior, deadlock handling, and `duration_to_last_update_ms`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/lock_manager/waiter_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/metrics.rs -->
# sources/storage-engines/tikv/src/server/metrics.rs

Purpose: central server metrics module declaring Prometheus counters, gauges, histograms, static label enums, and local auto-flush handles for gRPC, GC, snapshot, raft transport, config, async storage, resource priority, and request-source metrics.

Important APIs/types/functions: static metric enums include `GrpcTypeKind`, `GcCommandKind`, `SnapTask`, `ResolveStore`, `ResourcePriority`, raft duration/flush labels, request status/type labels, and `From<ErrorHeaderKind>`/`From<u64>` mappings. Runtime helper `record_request_source_metrics` keeps thread-local per-source counters and flushes periodically.

Control flow: most code lazily registers metrics and exports static handles. `record_request_source_metrics` checks a thread-local last-flush timestamp, lazily creates local counters per source string, increments count and duration, and flushes once per second. Error header conversion maps storage response error categories to async request metric labels.

State and persistence: state is process metrics registry plus thread-local metric maps. No durable state exists.

Dependencies and integration: used by many server modules including raft client, proxy, GC worker, raftstore-facing services, and config reporting. Re-exports GC key metric types from storage KV metrics.

Risks: high-cardinality `source` values in `record_request_source_metrics` can grow thread-local maps and Prometheus label series. Registration unwraps can panic on duplicate metric names. Static label enums require coordinated updates with call sites.

Test signals: no local unit tests; metrics are indirectly exercised by components that use the exported statics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/mod.rs -->
# sources/storage-engines/tikv/src/server/mod.rs

Purpose: server module root that declares submodules and re-exports the server-facing public API used by the rest of TiKV.

Important APIs/types/functions: exposes config, errors, GC/load/lock manager modules, raft server/KV transports, status/debug services, engine factory types, `GRPC_SERVER_THREAD`, server config constants, proxy helpers, `ConnectionBuilder`, `RaftClient`, `MultiRaftServer`, `RaftKv`, `RaftKv2`, store address resolvers, and server transport.

Control flow: no runtime logic; this is a compile-time module boundary and re-export surface.

State and persistence: none.

Dependencies and integration: coordinates all `crate::server` import paths. Visibility choices here determine which internals are reachable by other crates/modules.

Risks: re-export churn can break downstream imports. Keeping `metrics` crate-visible while re-exporting selected gauges narrows public surface but still permits server internals to share metrics.

Test signals: no direct tests; compilation and downstream module tests validate exports.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/proxy.rs -->
# sources/storage-engines/tikv/src/server/proxy.rs

Purpose: implements gRPC forwarding support so one TiKV node can receive a client RPC and forward it to another TiKV address identified by request metadata.

Important APIs/types/functions: `get_target_address` reads forwarding metadata; `build_forward_option` creates call options with that metadata; `Proxy::new` and `Proxy::call_on` manage forwarding clients; `forward_unary!` and `forward_duplex!` macros redirect service handlers.

Control flow: service macros inspect request metadata and return early if forwarding is requested. `Proxy::call_on` gets or creates a per-address pooled client, waits up to three seconds for channel connectivity, then invokes the supplied callback. Unary forwarding maps async client result to original response sink; duplex forwarding bridges request and response streams with batching enabled.

State and persistence: proxy state is an in-memory map from target address to a round-robin `ClientPool`. Cloned proxies share security/config/env references but start with an empty pool. No durable state.

Dependencies and integration: depends on gRPC channels/call options, `TikvClient`, `SecurityManager`, server `Config`, and proxy metrics from server metrics. Service implementations can use the exported macros.

Risks: forwarded target metadata must be valid UTF-8 and ASCII when built. Pools are never pruned, so long-lived nodes forwarding to many addresses may retain clients. If the weak gRPC environment cannot be upgraded or connection is not ready within three seconds, the callback is skipped without a response written by this layer.

Test signals: no local tests; macro behavior is covered by service-level integration paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/proxy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raft_client.rs -->
# sources/storage-engines/tikv/src/server/raft_client.rs

Purpose: manages outbound raft transport streams to peer stores, including per-store queues, gRPC stream lifecycle, batching, snapshot side-channel scheduling, connection health inspection, pause/disconnect handling, and metrics.

Important APIs/types/functions: `MetadataSourceStoreId` formats/parses source-store metadata. `Queue` is the bounded stateful message queue. `Buffer`, `BatchMessageBuffer`, and `MessageBuffer` define batching behavior. `AsyncRaftSender` drains queues to gRPC and diverts snapshots. `StreamBackEnd` resolves/connects/retries streams. `ConnectionBuilder` packages dependencies. `RaftClient` exposes `send`, `flush`, allowlist, and health APIs. `HealthChecker` runs periodic gRPC health probes.

Control flow: `send` hashes region id to a raft connection, loads or starts a stream backend, pushes into the queue, and marks the queue dirty for later `flush`. `flush` wakes dirty queues. Backend `start` loops through backoff, store address resolution, channel connection, batch raft call, fallback to legacy raft RPC on unimplemented, and reconnect on disconnect. `AsyncRaftSender` fills buffers until full/empty, sends snapshots via snapshot scheduler, waits under heavy load when configured, and flushes to gRPC. Health checker watches stores in the connection pool and spawns per-store inspection loops.

State and persistence: all state is memory-only: global connection pool, per-client LRU queue cache, dirty/full lists, queues, channels, tombstone set, allowlist, health task handles, and latency map. Raft messages are not persisted here; raftstore is responsible for raft durability before transport.

Dependencies and integration: integrates with `StoreAddrResolver`, `SecurityManager`, gRPC `TikvClient`, snapshot scheduler, raft router extension callbacks, server config `VersionTrack`, load statistics, metrics, `health_controller`, and raftstore discard reasons.

Risks: queue full/paused/disconnected paths drop or reject transport sends and depend on callers handling `DiscardReason`. Address resolution or connection failures clear pending messages and report peers/store unreachable. Snapshot parsing unwraps snapshot data bytes. Health checker uses mutex-protected shared maps and must stop tasks on drop. Batch size is estimated, so config buffer margins matter for gRPC max message size.

Test signals: tests cover batch buffer fullness with context/extra context, config refresh impact on batch sizing, buffer push benchmark, and health checker creation/latency/start-stop management.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raft_client.rs -->
