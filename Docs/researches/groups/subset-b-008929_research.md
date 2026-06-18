# subset-b-008929 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raft_server.rs -->
# sources/storage-engines/tikv/src/server/raft_server.rs

Purpose: owns legacy raftstore node bootstrap and lifecycle through `MultiRaftServer<C, EK, ER>`. It turns server config into a PD-visible `metapb::Store`, verifies or creates the on-disk store identity, prepares/bootstraps the first region, registers the store in PD, initializes replication-mode metadata, and starts/stops the raftstore batch system.

Important APIs and types: `init_store` fills address, peer address, status address, version, deploy path, start timestamp, git hash, and labels from `server::Config`; `MultiRaftServer::new` wires PD, config tracking, background worker, health controller, and global replication state; `try_bootstrap_store` calls `check_store`, allocates a store id through PD, writes `StoreIdent` via `store::bootstrap_store`, and checks API-version compatibility; `start` coordinates first-region bootstrap and `start_store`; `refresh_config_scheduler`, `pd_scheduler`, `get_router`, and `get_apply_router` expose raftstore channels.

Control flow: startup reads `STORE_IDENT_KEY`; missing identity means a fresh store id is allocated and persisted. `check_api_version` compares persisted and configured `ApiVersion`, allowing V1/V1ttl interchange, and otherwise scans data CFs for non-TiDB API-v2-incompatible keys before rewriting `StoreIdent`. Cluster bootstrap first reuses `PREPARE_BOOTSTRAP_KEY`, then checks PD bootstrap state, allocates region/peer ids, writes prepared bootstrap metadata, retries PD bootstrap up to 60 times with 3-second sleeps, and clears prepared keys according to whether this node's first region won. Only after bootstrap does it `put_store` and spawn raftstore.

State and persistence: persistent state is in KV engine keys `STORE_IDENT_KEY` and `PREPARE_BOOTSTRAP_KEY`, plus first-region bootstrap records managed by raftstore helpers. Volatile state includes `has_started`, `store_meta.store_id`, `GlobalReplicationState`, and the `RaftBatchSystem`. API-version switching persists a new `StoreIdent` and syncs KV. Bootstrap retries are synchronous and can delay startup for minutes.

Dependencies and integration points: depends on PD allocation/bootstrap/store registration, raftstore `RaftBatchSystem`, `CoprocessorHost`, split check, importer, `SnapManager`, causal timestamp provider, disk checker, `GrpcServiceManager`, and metrics/health plumbing. The public routers feed storage, transport, apply, PD, and dynamic config consumers.

Risks: `panic!` on `get_all_stores` failure aborts startup; `unwrap`/`expect` assume store bootstrap invariants; bootstrap retry sleeps block the calling thread; API-version scanning is potentially expensive and only checks key ranges defined by `TIDB_RANGES_COMPLEMENT`; failure between prepared bootstrap and PD bootstrap relies on persisted prepare keys for recovery. Tests are not in this file, so coverage is mostly integration-level via raftstore/server tests and failpoints such as `node_after_bootstrap_store`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raft_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv/mod.rs -->
# sources/storage-engines/tikv/src/server/raftkv/mod.rs

Purpose: implements the legacy `tikv_kv::Engine` adapter over raftstore. It converts storage-layer reads/writes/admin operations into raft commands, maps raftstore responses back into KV errors/results, handles async write event streams, exposes local-engine modifications for unsafe paths, and registers read-index lock checking for replica reads.

Important APIs and types: `Error` represents raft request, IO, server, response, request, undetermined, and timeout errors; `get_status_kind_from_engine_error` maps storage errors to metrics labels; `new_request_header` and `new_flashback_req` build raft headers with context, resource group, epoch, peer, term, sync log, replica read, and flashback flags; `RaftKv<E, S>` stores a `RaftRouterWrap`, local engine, optional txn-extra scheduler, region-info accessor, and current leader set; `ReplicaReadLockChecker` implements `ReadIndexObserver`.

Control flow: `async_write` rejects empty writes, supports failpoint error injection, converts `Modify` values into raft `Request`s, optionally checks duplicate lock-CF puts, sets one-pc/flashback flags, schedules txn extra, and sends a raft command with applied/proposed/committed callbacks. `WriteResFeed` and `WriteResSub` bridge callbacks into a `Stream<Item = WriteEvent>` using an atomic event byte, `UnsafeCell` result slot, and `AtomicWaker`. `async_snapshot` builds a `Snap` request, encodes stale-read/flashback start-ts flag data, sends through `LocalReadRouter::read`, then distinguishes real snapshots from lock-conflict read-index responses. Flashback start/end are admin commands via `exec_admin`.

State and persistence: normal writes are persisted by raftstore apply; `modify_on_kv_engine` bypasses raft and writes directly to the local KV engine after wrapping user keys with `keys::data_key`, rejecting SST ingest. `release_snapshot` clears router snapshot cache. `precheck_write_with_ctx` reads the `region_leaders` set to fail fast for non-leaders but is only a memory precheck.

Dependencies and integration points: integrates with `raftstore::router::{RaftStoreRouter, LocalReadRouter}`, `StoreCallback`, `RegionSnapshot`, `ReadIndexContext`, `tracker::GLOBAL_TRACKERS`, concurrency manager, metrics, hybrid in-memory snapshots, resource control metadata, and txn-extra scheduling. `RaftRouterWrap` is the raft extension exported to transport/debug layers.

Risks: unsafe callback stream state requires single-result ordering; callback drops are translated to undetermined errors to avoid false success; duplicate-key debug can panic in production if enabled; `ReadIndexContext::parse(...).unwrap()` assumes well-formed read-index payloads; local-engine modification bypasses raft consensus and must remain restricted to unsafe/admin flows. Test signals cover `ReplicaReadLockChecker` UUID preservation and follower no-op behavior; many write/snapshot paths depend on failpoints and integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv/raft_extension.rs -->
# sources/storage-engines/tikv/src/server/raftkv/raft_extension.rs

Purpose: adapts a legacy raftstore router to the `tikv_kv::RaftExtension` trait consumed by server transport, debug service, split callers, and diagnostics paths. It is a thin `RaftRouterWrap<S, E>` that derefs to the underlying router while adding trait methods with storage-layer error types.

Important APIs and types: `RaftRouterWrap::new` constructs the wrapper; `Deref` and `DerefMut` allow direct use as the wrapped router; `feed` forwards inbound `RaftMessage`; report methods notify unreachable peers/stores, rejected append messages, snapshot status, resolved DR group membership, and maybe tombstone stores through legacy router channels; `split`, `query_region`, and `check_consistency` expose async operations returning `BoxFuture`.

Control flow: `feed` logs send failures only for key messages because channel-full or missing-region errors are expected during normal churn. `split` sends a `CasualMessage::SplitRegion` with a write callback, waits for the paired future, validates the raft command response, and returns split regions. `query_region` sends `CasualMessage::AccessPeer` and resolves with `RegionMeta`. `check_consistency` first queries region meta, verifies the current peer is leader, finds the leader peer, then sends `AdminCmdType::ComputeHash` through the shared `exec_admin`.

State and persistence: the wrapper owns no durable state; all persistence happens inside raftstore as a result of forwarded commands. `report_snapshot_status` and unreachable reports update raftstore memory/raft state rather than local files directly.

Dependencies and integration points: depends on `RaftStoreRouter`, `CasualMessage`, `RegionMeta`, `RaftStateRole`, `SnapshotStatus`, and paired future callbacks. It is returned by `RaftKv::raft_extension` and passed to `ServerTransport`, raft clients, debug consistency checks, and snapshot handlers.

Risks: `check_consistency` unwraps the leader peer after checking leader role, which assumes leader id exists in region peers; split callback cancellation becomes an error through paired future handling; non-key `feed` failures are intentionally silent and can hide unexpected drops if caller misclassifies messages. No local unit tests; behavior is covered indirectly by server peer-resolve and raftstore integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv/raft_extension.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv2/mod.rs -->
# sources/storage-engines/tikv/src/server/raftkv2/mod.rs

Purpose: implements the raftstore-v2 `tikv_kv::Engine` adapter. Compared with legacy `RaftKv`, it routes simple binary write payloads and snapshot/admin requests through `raftstore_v2::router::RaftRouter`, with tablet-oriented storage under the raftstore-v2 system.

Important APIs and types: `RaftKv2<EK, ER>` stores a v2 router, optional txn-extra scheduler, and leader set. `modifies_to_simple_write` serializes `Modify` operations into `SimpleWriteBinary` using `SimpleWriteEncoder`, including SST ingest payloads. `Transform` maps v2 `CmdResStream` events into `WriteEvent`. `exec_admin` sends v2 admin peer messages and waits for a result subscription.

Control flow: `modify_on_kv_engine` turns each region's modifies into a simple-write binary and sends `PeerMsg::unsafe_write`. `async_snapshot` mirrors legacy snapshot header construction: set snap command, read-index key ranges/start-ts when present, encode stale-read/flashback flags, run failpoint checks, call `router.snapshot`, and map lock conflicts/header errors to KV errors while recording metrics. `async_write` builds a boxed header, flags for one-pc/flashback, schedules txn-extra, freezes binary data when `avoid_batch` is requested, configures proposed/committed subscriptions, installs a before-set callback for metrics and `on_applied`, and sends `PeerMsg::SimpleWrite`. Early failpoint-injected region-not-found errors are reported into the command channel and also stored in `Transform`.

State and persistence: raft consensus/apply owns persistence; this adapter itself has only in-memory router and leader information. `kv_engine()` returns `None`, signaling that v2 does not expose the local engine through this adapter. Flashback admin commands persist region flashback state through raftstore-v2 apply.

Dependencies and integration points: integrates with `raftstore_v2::{SimpleWriteEncoder, CmdResChannelBuilder, PeerMsg, RaftRouter}`, legacy header helpers from `raftkv`, `tracker`, async request metrics, `TxnExtraScheduler`, and `tikv_kv::Engine`. `raft_extension()` returns the v2 `Extension` for network/snapshot/debug integration.

Risks: direct `unsafe_write` is intentionally outside normal raft command validation; `async_snapshot` uses `unwrap` on an optional future after checking failpoint state, so invariants must be preserved; `on_applied` is invoked from the v2 channel before-set hook and does not itself control final stream emission; v2 lacks some legacy helper methods such as local MVCC property access. Test signals are mostly indirect; comments flag known inaccurate snapshot duration measurement and temporary associated-type workaround.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv2/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv2/node.rs -->
# sources/storage-engines/tikv/src/server/raftkv2/node.rs

Purpose: owns raftstore-v2 node bootstrap and lifecycle. `NodeV2<C, EK, ER>` initializes store identity from server config, bootstraps raft-engine metadata through `raftstore_v2::Bootstrap`, creates the v2 store batch system, optionally bootstraps the first tablet/region, registers the store in PD, initializes replication state, starts the v2 store system, and shuts it down.

Important APIs and types: `new` builds an unstarted node with PD client, logger, resource controller, and default store metadata from `init_store`. `try_bootstrap_store` calls `Bootstrap::bootstrap_store`, sets the store id, and creates `(StoreRouter, StoreSystem)`. `router`, `system`, `refresh_config_scheduler`, `id`, `store`, and `logger` expose lifecycle state. `start` and `start_store` wire raft engine, tablet registry, transport, tablet snapshots, concurrency manager, coprocessors, split controller, collectors, background workers, PD worker, importer, key manager, and gRPC service manager.

Control flow: after store bootstrap, `start` calls `Bootstrap::bootstrap_first_region`. If PD/raft metadata requires creating an initial region, the node computes the tablet path at `RAFT_INIT_LOG_INDEX`, builds `TabletContext`, and opens the tablet before store startup. It then `put_store`s to PD, loads all stores for replication labels/status, and starts the `StoreSystem` exactly once.

State and persistence: durable metadata is in the raft engine and tablet registry rather than legacy KV bootstrap keys. Opening the initial tablet is persistent filesystem/tablet-factory state. Volatile state includes `system: Option<(StoreRouter, StoreSystem)>`, `has_started`, logger, and resource controller. Global replication status and store labels are written into `GlobalReplicationState` under a mutex.

Dependencies and integration points: depends on `raftstore_v2::Bootstrap`, `create_store_batch_system`, `StoreSystem::start`, tablet registry/factory, `TabletSnapManager`, encryption key manager, PD, resource controller, raftstore coprocessor host, importer, and gRPC service manager. It reuses legacy `raft_server::init_store` for store metadata consistency.

Risks: `router()`/`system()` unwrap `system` and require `try_bootstrap_store` first; first-tablet open currently `unwrap`s with a TODO about recovery from abort; `load_all_stores` panics on PD failure; API-version checking is TODO and unlike legacy `MultiRaftServer`; dynamic config support is TODO. No local tests; coverage likely comes from raftstore-v2 integration/bootstrap tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv2/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv2/raft_extension.rs -->
# sources/storage-engines/tikv/src/server/raftkv2/raft_extension.rs

Purpose: implements `tikv_kv::RaftExtension` for raftstore-v2. It bridges network transport and higher-level raft extension operations to v2 `StoreRouter`/`PeerMsg`/`StoreMsg` primitives.

Important APIs and types: `Extension<EK, ER>` stores a cloneable `StoreRouter`; `feed` forwards inbound raft messages; report methods emit `PeerUnreachable`, `StoreUnreachable`, `StoreMaybeTombstone`, `SnapshotSent`, or no-op placeholders; `split` sends `PeerMsg::request_split`; `query_region` sends `PeerMsg::QueryDebugInfo` over a `DebugInfoChannel`.

Control flow: `feed` boxes and sends raft messages, logging failures only for key messages. Peer/store reachability methods use normal, control, or force-send paths depending on severity. `split` builds a request with `share_source_region_size` true, checks send success, waits for the subscription result, returns split regions on a clean header, and converts header errors to KV errors. `query_region` similarly checks send and waits for debug info, returning an aborted error if the result channel closes.

State and persistence: no local persistence. Split and snapshot-status operations eventually affect raftstore-v2 region metadata and raft state through peer FSMs.

Dependencies and integration points: used by `RaftKv2::raft_extension`, `ServerTransport`, raft clients, snapshot handling, and debug service. It depends on `raftstore_v2` router message types and legacy `RegionMeta` type for debug/query compatibility.

Risks: `report_reject_message` and `report_resolved` are TODO/no-op, so behavior is not yet feature-equivalent with legacy raft extension for rejected appends and DR commit-group reporting. `force_send` snapshot status ignores returned errors. `split`/`query_region` can fail on aborted subscriptions. No local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/raftkv2/raft_extension.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/reset_to_version.rs -->
# sources/storage-engines/tikv/src/server/reset_to_version.rs

Purpose: provides a debug/admin reset-to-version worker for RocksEngine. It removes MVCC writes newer than a target timestamp, deletes matching default-CF values, then removes all locks.

Important APIs and types: `ResetToVersionState` tracks `RemovingWrite { scanned }`, `RemovingLock { scanned }`, and `Done`. `ResetToVersionWorker` owns write and lock iterators plus target timestamp and shared state. `ResetToVersionManager` owns engine, shared state, and optional worker thread handle; `start`, `state`, and `wait` are the user-facing controls.

Control flow: `ResetToVersionWorker::new` seeks both iterators to first and marks state as removing writes. `next_write` parses a `WriteRef`, advances the write iterator, and increments scanned count. `scan_next_batch` filters writes by commit timestamp decoded from the encoded key; only commit_ts greater than the reset timestamp are selected. `process_next_batch` deletes the selected write-CF key and the corresponding default-CF key formed by truncating commit ts and appending `write.start_ts`, then writes and clears the batch. After write scanning finishes, the manager thread sets state to `RemovingLock` and `process_next_batch_lock` deletes every lock-CF key in batches before setting `Done`.

State and persistence: mutations are direct RocksDB write batches on `CF_WRITE`, `CF_DEFAULT`, and `CF_LOCK`. WAL is not explicitly disabled; comments note v2 needs `disable_wal=true`. The manager joins the background thread on drop, avoiding detached reset work.

Dependencies and integration points: invoked by debug service through debugger `reset_to_version`. Depends on Rocks-specific iterators/write batches and txn_types MVCC encodings. Uses TiKV thread-group property propagation for the spawned thread.

Risks: many iterator and write operations `unwrap`/`expect`, so corruption or engine errors can panic the reset thread; it is RocksEngine-only and not consensus-mediated; deleting all locks is broad and assumes this debug operation is used in controlled contexts; there is no cancellation. Test `test_basic` builds writes/defaults/locks and verifies newer writes/defaults and all locks are removed while older data remains.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/reset_to_version.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/resolve.rs -->
# sources/storage-engines/tikv/src/server/resolve.rs

Purpose: asynchronously resolves TiKV store IDs to raft peer addresses through PD, caches addresses, and updates global replication label/group state. It backs raft transport connection creation.

Important APIs and types: `StoreAddrResolver` exposes async `resolve(store_id, cb)`. `PdStoreAddrResolver` schedules `Task` values onto a worker. `new_resolver` creates a `Runner` and shared `GlobalReplicationState`. `Runner<T, R>` stores PD client, address cache, replication state, and raft extension. `MockStoreAddrResolver` is a test hook.

Control flow: `Runner::resolve` returns cached addresses younger than `STORE_ADDRESS_REFRESH_SECONDS` unless a failpoint overrides the interval. On miss/stale cache it calls `get_address`, stores the result with current timestamp, and returns it. `get_address` calls `pd_client.get_store`; tombstone or "not found" errors increment metrics, report maybe-tombstone to raft, and return `StoreTombstone`. For DR auto-sync, it registers store labels into replication groups and reports resolved group id; otherwise it backs up labels. It finally prefers peer address via `take_peer_address` and rejects empty addresses. The worker's `run` invokes the callback and records latency.

State and persistence: only in-memory cache and `GlobalReplicationState` are changed. PD remains source of truth. Tombstone reporting is a side effect into raftstore through `RaftExtension`.

Dependencies and integration points: used by `server::Server`/`RaftClient` transport. Depends on PD store metadata, replication-mode state, metrics, worker scheduler, and raft extension methods `report_store_maybe_tombstone` and `report_resolved`.

Risks: error classification checks debug string for "not found"; cached addresses can be stale up to 60 seconds; empty-address rejection exists for tests and may hide bad PD metadata; callback execution happens on the resolver worker. Tests cover UP/OFFLINE/TOMBSTONE handling, not-found mapping, peer-address preference, and cache refresh semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/resolve.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/server.rs -->
# sources/storage-engines/tikv/src/server/server.rs

Purpose: constructs and manages the TiKV gRPC server, raft transport, snapshot worker, health service, load/memory stats tasks, and service registration. `Server<S, E>` is the top-level runtime holder for client-facing and raft-facing networking.

Important APIs and types: `GrpcBuilderFactory` abstracts building a bound `grpcio::ServerBuilder`; `BuilderFactory` applies configured compression, HTTP/2 window/stream settings, memory quota, health service, security binding, and Tikv service registration. `Server::new` wires storage, coprocessors, GC worker, resolver, snapshot managers, raft extension, `RaftClient`, health controller, and metrics/runtime pools. `build_and_bind`, `start`, `stop`, `pause`, `resume`, `transport`, and `register_service` are the lifecycle surface.

Control flow: construction builds optional stats runtime, thread-load tracker, lazy snapshot worker, raft extension from storage engine, TiKV gRPC service through `KvService::new`, memory quota, server builder, connection builder, raft client, and transport. `build_and_bind` consumes the builder, builds/binds a gRPC server, stores actual listening address, and transitions `builder_or_server` from left to right. `start` starts the appropriate snapshot runner, starts gRPC, starts periodic load/memory-stat timers when configured, exports startup build/version gauge, and marks health serving. `pause` builds a fresh builder before dropping the running server; `resume` rebinds and restarts.

State and persistence: no direct storage persistence, but it owns runtime state: `builder_or_server`, gRPC memory quota, local address, raft transport client, snapshot worker, stats pool, read/debug pools, and health status. Memory usage and server info are exported as metrics.

Dependencies and integration points: integrates with `KvService`, `Proxy`, `RaftClient`, `ServerTransport`, legacy/tablet snapshot runners, security manager, health controller, resource group manager, coprocessor endpoints, read pool, and global timer. Test-only `TestRaftStoreRouter` lets tests observe peer/store messages.

Risks: lifecycle methods rely on `builder_or_server` shape and use unwraps; service registration fails after build/start by returning the service; pause/resume can skip if builder creation fails; background stat tasks run until runtime shutdown. Test `test_peer_resolve` verifies unresolved peers report unreachable, resolver address enables raft send, and resolver quick-fail reports unreachable.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/batch.rs -->
# sources/storage-engines/tikv/src/server/service/batch.rs

Purpose: batches eligible normal-priority `Get` and `RawGet` requests from batch-command streams to reduce per-request readpool overhead while preserving per-request responses and metrics.

Important APIs and types: constants cap batching (`MAX_BATCH_GET_REQUEST_COUNT`, `MIN_BATCH_GET_REQUEST_COUNT`, `MAX_QUEUE_SIZE_PER_WORKER`). `ReqBatcher` buffers KV gets, raw gets, request IDs, tracker tokens, and begin time. `BatcherBuilder` decides whether batching is useful from config, pool size, queue depth, and request batch size. `GetCommandResponseConsumer` implements `ResponseBatchConsumer` for transactional and raw get results.

Control flow: `can_batch_get`/`can_batch_raw_get` accept only normal-priority requests. `add_get_request` creates a tracker with context/version and records request size; raw gets do not use trackers. `maybe_commit` flushes when either buffer reaches batch size; `commit` flushes leftovers. `future_batch_get_command` observes batch size, captures request sources and priority, calls `storage.batch_get_command`, and arranges per-item responses through `GetCommandResponseConsumer`; if the whole future returns a region error, it broadcasts that error to all IDs and removes trackers. Raw get mirrors this through `raw_batch_get_command`.

State and persistence: no persistent state; this is request buffering only. Responses are sent through the batch-command response channel with immediate wake policy.

Dependencies and integration points: used by `KvService` batch command processing. Depends on storage batch APIs, tracker registry, protobuf response types, request duration metrics, response batch consumers, and error extraction helpers.

Risks: batching assumes grouped priority from first request; if request mix changes in future, priority/source accounting could be too coarse. Dropped response channels only warn. Region-level failures from the batch future are fanned out uniformly, while per-item errors are handled by consumers. Unit tests verify commit-ts propagation in batched get responses, including default zero when absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/debug.rs -->
# sources/storage-engines/tikv/src/server/service/debug.rs

Purpose: implements the gRPC Debug service by delegating expensive or blocking operations to a Tokio runtime and a `Debugger` abstraction, plus raft extension operations for consistency checks and store metadata for read-progress diagnostics.

Important APIs and types: `Service<T, D, S>` holds runtime handle, debugger, raft router, store metadata, and resolved-ts scheduler. Type aliases define generic callbacks and resolved-ts diagnosis scheduler. `error_to_status`, `error_to_grpc_error`, and `handle_response` centralize error mapping and unary response handling.

Control flow: most unary RPCs clone the debugger, spawn an async task on the debug pool, transform debugger output into protobuf responses, and call `handle_response`. Covered operations include engine get, raft log, region info/size, compaction, failpoint inject/recover/list, metrics dump, config modification, region/range properties, store/cluster info, all regions, flashback, and consistency checks. `scan_mvcc` is server-streaming and streams iterator rows to the sink. `reset_to_version` directly starts debugger reset and replies immediately. `get_region_read_progress` first reads in-memory region read-progress state under store-meta lock, then asks the resolved-ts scheduler through a paired future and enriches the response.

State and persistence: the service itself persists nothing. Some RPCs intentionally mutate system state: failpoints, config, compaction, reset-to-version, flashback, and raft consistency admin commands. Read-progress and resolved-ts inspection is in-memory.

Dependencies and integration points: depends on `Debugger`, `tikv_kv::RaftExtension`, `StoreRegionMeta`, failpoint crate, metrics dump, paired callbacks, grpcio sinks, and debug protobufs. It is registered as an extra service on the main server.

Risks: debug RPCs are powerful and can mutate live storage; many spawned task joins use `unwrap`, so panic in task propagates; `reset_to_version` does not wait for completion or return state; streaming scan silently returns on iterator creation error. No local tests here; behavior relies on debugger tests and integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/debug.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/diagnostics/log.rs -->
# sources/storage-engines/tikv/src/server/service/diagnostics/log.rs

Purpose: implements log search for the Diagnostics service, including rotated-file discovery, timestamp/level parsing, regex filtering, time-range filtering, and batching into streaming responses.

Important APIs and types: `LogIterator` holds matching files, current line iterator, filters, and previous valid log metadata for multiline/invalid lines. `Error` distinguishes invalid request, parse, search, and IO failures. `search` validates request filters and returns a stream of `SearchLogResponse`. Parser helpers include `is_log_file`, `parse_time`, `parse_level`, `parse`, `parse_time_range`, `parse_start_time`, and `parse_end_time`.

Control flow: `LogIterator::new` derives log directory/name, scans sibling files, keeps normal and rotated files whose stem matches TiKV rotation format, opens files, parses start/end time from first/last valid lines, filters files outside the requested range, sorts by start time, and begins with the oldest relevant file. `Iterator::next` reads lines, parses valid TiKV log headers, attaches invalid continuation lines to the previous valid timestamp/level, stops after end time, skips before begin time, applies level bitmask and all regex patterns, and yields `LogMessage`s. `batch_log_item` groups up to 256 messages per response.

State and persistence: read-only filesystem access. It does not tail live logs beyond current file contents. Missing log path returns an empty iterator rather than an error.

Dependencies and integration points: used by `diagnostics::Service::search_log`. Depends on chrono, nom, regex, rev_lines, itertools, futures streams, and diagnostic protobufs.

Risks: file-stem unwraps assume valid paths during directory scanning; only first/last 10 lines are tried for time range, so heavily malformed log edges can skip a file; invalid lines inherit previous level/time, which is useful for stack traces but can include unrelated malformed lines; regexes are user-provided and may be expensive. Tests cover parsing, time range extraction with invalid edges, iterator filtering, rotated-file recognition, and stream search.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/diagnostics/log.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/diagnostics/mod.rs -->
# sources/storage-engines/tikv/src/server/service/diagnostics/mod.rs

Purpose: exposes the gRPC Diagnostics service by composing log search and system information collectors on a Tokio runtime.

Important APIs and types: `Service` stores runtime handle, normal log path, and slow log path. `SYS_INFO` is a global `Mutex<sysinfo::System>` shared by diagnostics collectors. Public submodule `sys` contains host telemetry; private submodule `log` contains search implementation.

Control flow: `search_log` chooses normal or slow log path from request target, spawns `log::search`, maps each `SearchLogResponse` into a buffered gRPC write, and streams all responses to the sink, logging gRPC errors. `server_info` optionally captures a baseline snapshot for load info (CPU, networks, IO), waits about one second through the global timer, then collects hardware/load/system info according to `ServerInfoType`, sorts items by `(tp, name)`, and replies unary.

State and persistence: no persistence. `SYS_INFO` caches and refreshes host data under a mutex. Load-info collection intentionally samples state twice about one second apart for rate calculations.

Dependencies and integration points: registered on the server as a diagnostics gRPC service. Depends on `sysinfo`, TiKV global timer, grpcio sinks, futures compatibility, and `server::Error` conversion for sink failures.

Risks: lock contention on global `SYS_INFO`; `stream.await.unwrap()` and sink `res.unwrap()` assume spawned tasks do not panic; `ServerInfoType::All` includes potentially expensive `/proc/sys` walking from `sys::system_info`; unsupported enum values are not explicitly handled beyond match arms present. Test signals are in `log.rs` and `sys.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/diagnostics/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/diagnostics/sys.rs -->
# sources/storage-engines/tikv/src/server/service/diagnostics/sys.rs

Purpose: collects host diagnostics for CPU, memory, disk, network, IO, kernel/sysctl, transparent hugepage, and process information and converts them into diagnostic protobuf `ServerInfoItem`s.

Important APIs and types: `NicSnapshot` captures cumulative network counters and converts deltas to per-second-style pairs. `cpu_time_snapshot` returns Linux CPU times for load sampling. `load_info`, `hardware_info`, `system_info`, and `process_info` are the main collectors. Internal helpers collect CPU/memory/network/IO load, CPU/memory/disk/NIC hardware, sysctl key-values, and transparent hugepage setting.

Control flow: load collection receives previous CPU/NIC/IO snapshots and compares them with current data. CPU load emits load averages and, when CPU time is available, fractional user/system/idle/etc deltas. Memory load emits virtual and swap totals/used/free percentages. NIC and IO load emit deltas only for devices present in the previous snapshot. Hardware collection refreshes `SYS_INFO`, emits CPU quota/physical cores/frequency/vendor/arch/cache info, memory quota, disks excluding `rootfs`, and NIC flags/MAC/IPs. System collection walks `/proc/sys`, sorts sysctl pairs, and optionally reads transparent hugepage status. Process collection refreshes processes and emits command/exe/cwd/start/memory/status/cpu usage for processes with commands.

State and persistence: read-only access to OS state via `sysinfo`, TiKV sys helpers, `/proc/sys`, `/sys/kernel/mm/transparent_hugepage/enabled`, and network interface enumeration. Shared `SYS_INFO` is updated under a mutex.

Dependencies and integration points: called by `diagnostics::Service::server_info`. Depends on `tikv_util::sys::{SysQuota, LinuxStyleCpuTime, ioload}`, `walkdir`, `pnet_datalink`, `num_cpus`, and diagnostic protobufs.

Risks: percentage calculations can divide by zero for unusual memory/swap totals; Linux-specific procfs/sysfs collectors naturally degrade on non-Linux by returning fewer items; `/proc/sys` walking can be broad and permission-sensitive; tests are environment-sensitive and include docker exclusions for memory. Tests cover load, system, process, memory quota, and hardware key shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/server/service/diagnostics/sys.rs -->
