# subset-b-008862 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/server2.rs -->
# sources/storage-engines/tikv/components/server/src/server2.rs

Purpose: this is the RaftKV v2 TiKV server bootstrap and lifecycle module. `run_tikv` selects the configured raft engine, runs pre-start environment checks, dispatches on storage API version, and delegates to `run_impl`, which constructs `TikvServer`, initializes every core subsystem, starts gRPC/status servers, then waits on `ServiceEvent` messages for pause, resume, graceful shutdown, or exit.

Important APIs and types: `TikvServer<ER>` owns all long-lived server state: `TikvServerCore`, `ConfigController`, security and PD clients, `RaftRouter`, `NodeV2`, tablet snapshot manager, `TikvEngines`, Rocks statistics, service handles, coprocessor host, concurrency manager, grpc environment, CDC/backup/resolved-ts workers, quota/resource managers, causal timestamp provider, tablet registry, and `GrpcServiceManager`. `TikvEngines` couples raft engine with `RaftKv2`; `Servers` holds lock manager, local gRPC `Server`, `SstImporter`, and resource metering pubsub service.

Control flow: `init` builds security, gRPC environment hooks, PD client, config controller, background worker, concurrency manager, quota limiter, optional resource control, and API-v2 causal timestamp provider. `init_engines` opens raft and tablet engines, bootstraps store identity, creates `TabletRegistry`, registers RocksDB/raft config managers, constructs `RaftRouter`, coprocessor host, region info accessor, CDC worker, and `RaftKv2`. `init_servers` creates flow control, GC, read pools, resource metering, storage, resolver, snapshot manager, coprocessor endpoint, CDC/resolved-ts/backup stream endpoints, `Server`, SST importer, split controller, consistency observer, starts `NodeV2`, registers dynamic config managers, and starts auto GC. `register_services` wires backup, import SST, log backup, debug, CDC, diagnostics, deadlock, and resource metering services into gRPC. Background tasks flush engine/IO/memory metrics, disk stats, cgroup gauges, and max-ts.

State and persistence behavior: persistent state is opened through raft engine, tablet registry, snapshot directory, import directory, RocksDB options, store identity, and PD metadata. Startup mutates dynamic config controller registrations and may bootstrap local store state. Shutdown first raises raftstore store pool size/high-priority background threads, sends `FlushBeforeClose` to all raft groups, then stops gRPC, node, region info accessor, lock manager, SST recovery worker, and registered stoppables. Graceful shutdown tells PD state via `PdTask::GracefulShutdownState`, waits for local leader eviction until configured timeout, then clears the state.

Dependencies and integration points: this file integrates most TiKV components: PD, raftstore-v2, Rocks/raft-log engines, tablet registry, storage, coprocessor, CDC, resolved-ts, backup-stream, resource metering/control, quota limiter, import SST, status/debug services, signal handler, and `service` event routing. `utils::build_backup_encryption_manager` is used for log backup encryption manager construction.

Risks: ordering is critical because many fields are `Option::unwrap()` after staged initialization. Fatal exits are used for startup failures. Disk usage calculations must handle separated raft/tablet/auxiliary mount points correctly. Service registration must happen before server start, and observers must register before `NodeV2::start`. `flush_before_stop` force-sends to every raft group and waits on all responses, so stuck groups can delay shutdown. Graceful shutdown correctness depends on PD worker scheduling and accurate region leader tracking.

Test signals: the local test `test_engines_resource_info_update` checks that `EnginesResourceInfo::update` uses latest tablets, clears its cache, preserves map capacity, and computes normalized pending compaction bytes. Most behavior here is integration-heavy and indirectly tested through subsystem tests and TiKV startup/shutdown coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/server2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/setup.rs -->
# sources/storage-engines/tikv/components/server/src/setup.rs

Purpose: central startup setup utilities for logging, metrics, command-line config overrides, validation, and fatal process termination. It is used before and during server startup so failures are reported consistently even before the logger is initialized.

Important APIs and functions: `fatal!` logs through slog when `LOG_INITIALIZED` is true, otherwise writes to stderr, clears the global logger, and exits. `initial_logger` builds normal, RocksDB, raftdb, and optional slow-log drains, selecting text or JSON format and terminal or file output. `initial_metric` starts process, thread, and allocator metric monitors and warns that metrics push is unsupported. `overwrite_config_with_cmd_args` maps CLI arguments into `TikvConfig`. `validate_and_persist_config` delegates validation/persistence and aborts on failure. `ensure_no_unrecognized_config` aborts if unknown config keys remain.

Control flow: log setup computes RocksDB and raftdb info log paths via configured info-log directories or data dir, creates needed directories, canonicalizes paths, creates rotating file writers using `rename_by_timestamp`, builds a `LogDispatcher`, and initializes global logging with slow-log threshold. CLI override handling updates log, server addresses, data dir, PD endpoints, labels, capacity, and metrics warning in place.

State and persistence behavior: this file creates log directories and rotating log files. `rename_by_timestamp` renames rotated files using local timestamp. Config validation may persist configuration through `tikv::config::validate_and_persist_config` depending on the `persist` flag. It also sets global redaction behavior and `LOG_INITIALIZED`.

Dependencies and integration points: relies on `tikv_util::logger`, `tikv_util::config`, `chrono`, `clap::ArgMatches`, and TiKV config types. Server startup imports this module and `fatal!` is used broadly in `server2.rs`.

Risks: process exit is immediate and not recoverable. Timestamp-based rotation has a documented small duplicate-name risk under intense rotation. Path conversion uses `to_str().unwrap_or_else(fatal!)`, so non-UTF8 paths terminate startup. Label parsing is strict and rejects malformed `key=value` entries.

Test signals: no direct unit tests in this file. Behavior is exercised through startup/config tests elsewhere; failpoint `mock_force_uninitial_logger` covers the stderr fallback path.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/setup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/signal_handler.rs -->
# sources/storage-engines/tikv/components/server/src/signal_handler.rs

Purpose: platform-specific signal loop for TiKV process control and diagnostic dumping. On Unix it converts OS signals into service events or metric/stat dumps; non-Unix builds provide a no-op shim.

Important APIs and functions: public re-export `wait_for_signal`. Unix `wait_for_signal` accepts optional engines, optional Rocks statistics, config controller, and optional service event sender. It listens for `SIGTERM`, `SIGINT`, `SIGHUP`, `SIGUSR1`, and `SIGUSR2`.

Control flow: `SIGTERM` checks current `server.graceful_shutdown_timeout`; if non-zero it sends `ServiceEvent::GracefulShutdown`, otherwise `ServiceEvent::Exit`, then breaks. `SIGINT` and `SIGHUP` send `Exit` and break. `SIGUSR1` logs TiKV metrics plus optional KV and raft engine stats and Rocks statistics. `SIGUSR2` is registered but falls through to the unreachable arm because only `SIGUSR1` is handled as a diagnostic signal.

State and persistence behavior: no persistent writes. It reads current config dynamically, sends messages through TiKV mpsc, and logs diagnostics.

Dependencies and integration points: used by `server2.rs` in a background thread after server startup. Integrates `signal_hook`, TiKV metrics, `service::ServiceEvent`, `ConfigController`, and engine statistic dumping.

Risks: if the service event channel is disconnected, shutdown signals only log a warning and the signal loop exits. Graceful shutdown behavior can change at runtime because it reads the current config at signal time. Non-Unix function signature differs from Unix by omitting `ConfigController`, which is hidden behind cfg but worth preserving carefully.

Test signals: no direct unit tests. Behavior is mostly covered by integration/manual signal tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/signal_handler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/utils.rs -->
# sources/storage-engines/tikv/components/server/src/utils.rs

Purpose: small server helper for constructing backup encryption manager state used by backup stream setup.

Important APIs and functions: `build_backup_encryption_manager` accepts an optional `Arc<DataKeyManager>` and returns `BackupEncryptionManager` configured with no explicit backend, plaintext method, a new `MultiMasterKeyBackend`, and the optional data key manager.

Control flow: the function is a straight constructor wrapper returning `io::Result`, currently without fallible operations beyond the wrapped type contract.

State and persistence behavior: no direct persistence. It passes through the server encryption key manager so backup/log-backup paths can resolve file encryption metadata consistently.

Dependencies and integration points: used by `server2.rs` while starting backup stream. Depends on `encryption::{BackupEncryptionManager, DataKeyManager, MultiMasterKeyBackend}` and `kvproto::encryptionpb::EncryptionMethod`.

Risks: hard-coded plaintext method means actual encryption behavior depends on the optional data key manager and backup manager semantics. Future backup encryption changes should revisit this constructor instead of duplicating manager setup.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/service/Cargo.toml -->
# sources/storage-engines/tikv/components/service/Cargo.toml

Purpose: crate manifest for the lightweight `service` component that carries service lifecycle events and a gRPC service manager.

Important APIs and dependencies: package `service`, edition 2021, unpublished Apache-2.0 crate. Runtime dependencies are `atomic`, workspace `crossbeam`, and workspace `tikv_util`.

Control flow and integration: this manifest supports `service_event.rs` and `service_manager.rs`, which are consumed by server startup and status/control paths to pause/resume gRPC and trigger shutdown events.

State and persistence behavior: no build-time persistence beyond Cargo metadata.

Risks: the crate is intentionally tiny; dependency additions should be scrutinized because this component is imported by startup/control paths.

Test signals: no manifest-local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/service/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/service/src/lib.rs -->
# sources/storage-engines/tikv/components/service/src/lib.rs

Purpose: crate root exposing the service event and service manager modules.

Important APIs: declares `pub mod service_event;` and `pub mod service_manager;`.

Control flow, state, and integration: no runtime logic here. It defines the public module surface used by `server2.rs`, signal handling, and status/control components.

Risks: minimal. Removing or privatizing either module breaks external imports.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/service/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/service/src/service_event.rs -->
# sources/storage-engines/tikv/components/service/src/service_event.rs

Purpose: defines the service-control messages sent from signal/control code to the server event loop.

Important APIs and types: `ServiceEvent` variants are `PauseGrpc`, `ResumeGrpc`, `GracefulShutdown`, and `Exit`. A manual `Debug` implementation emits stable tuple-style variant names.

Control flow and integration: `server2.rs` receives these events and calls `pause`, `resume`, `graceful_shutdown`, or breaks the main loop. `signal_handler.rs` sends `GracefulShutdown` or `Exit` on process signals. `GrpcServiceManager` sends pause/resume variants.

State and persistence behavior: no local state or persistence; this is an in-memory channel protocol.

Risks: enum changes must update all match sites in server and service manager. `Debug` is manual, so new variants require manual formatting.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/service/src/service_event.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/service/src/service_manager.rs -->
# sources/storage-engines/tikv/components/service/src/service_manager.rs

Purpose: a cloneable handle for requesting gRPC service pause/resume and exposing current serving state.

Important APIs and types: private `GrpcServiceStatus` has `Init`, `Serving`, and `NotServing`. `GrpcServiceManager` stores `Arc<Atomic<GrpcServiceStatus>>` plus a TiKV mpsc sender. Public constructors are `new` and `dummy`; public actions are `pause`, `resume`, and `is_paused`.

Control flow: `pause` is idempotent if already paused; otherwise it sends `ServiceEvent::PauseGrpc` and stores `NotServing` only if send succeeds. `resume` mirrors this with `ResumeGrpc` and `Serving`. `is_serving` is private and used to avoid duplicate resume sends.

State and persistence behavior: state is in-memory relaxed atomic status. It deliberately tracks requested service state, not necessarily full server-side completion. No persistence.

Dependencies and integration points: used by `server2.rs` to give status service and raftstore/node code a way to pause or resume the gRPC server through the main event loop.

Risks: status updates occur after successful send, before the receiver acts, so callers must not treat the flag as a synchronous server-state guarantee. `dummy` starts in `Init`, so tests using it must account for resume semantics from a non-serving/non-paused initial state.

Test signals: no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/service/src/service_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/Cargo.toml -->
# sources/storage-engines/tikv/components/snap_recovery/Cargo.toml

Purpose: manifest for the snapshot recovery component that exposes recovery-mode setup and gRPC recovery services.

Important APIs and dependencies: package `snap_recovery`, edition 2021. Default features enable test KV RocksDB and raft-engine backends through `tikv`. Dependencies include engine traits/Rocks, raft-log-engine, raftstore, PD client, grpcio, kvproto, encryption export, prometheus, tokio, futures, txn_types, and TiKV utilities.

Control flow and integration: the dependency set matches the crate responsibilities: open local engines, mutate config for recovery mode, serve `RecoverData` RPCs, inspect raft metadata, force leadership, wait apply, resolve MVCC data, and emit metrics.

State and persistence behavior: manifest only, but features select engine implementations that affect tests and local-engine service construction.

Risks: default test-engine features mean build/test behavior differs from production feature selection. Recovery code spans storage, raft, and PD, so dependency version drift can break broad contracts.

Test signals: crate tests live in source modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/data_resolver.rs -->
# sources/storage-engines/tikv/components/snap_recovery/src/data_resolver.rs

Purpose: deletes MVCC data newer than a recovery resolved timestamp and reports progress to BR during snapshot recovery.

Important APIs and types: `DataResolverManager` owns a `RocksEngine`, progress sender, worker join handles, and `resolved_ts`. `LockResolverWorker` deletes all lock CF entries seen by its iterator. `WriteResolverWorker` scans write CF, filters commits above `resolved_ts`, deletes corresponding write and default CF records, and reports batch progress. `Error` wraps invalid argument, not found, engine, and boxed errors.

Control flow: `DataResolverManager::start` spawns separate `cleanup_lock` and `resolve_write` threads. `resolve_lock` creates a lock CF iterator with min-ts hint, deletes every lock, sync-writes the batch, and sends resolved key count. `resolve_write` creates a write CF iterator, loops `batch_resolve_write`, and logs duration. `scan_next_batch` pulls up to `BATCH_SIZE_LIMIT` items, decodes commit ts from the encoded key, and keeps only keys with commit ts greater than the resolved timestamp. `batch_resolve_write` removes each write key and its default CF key built from the write start ts, syncs the write batch, and streams key count/current commit ts.

State and persistence behavior: this code destructively mutates RocksDB CFs `lock`, `write`, and `default` with synchronous writes. The same write batch object is reused across batches, which relies on engine write-batch semantics. Progress is transient over futures mpsc.

Dependencies and integration points: used by `RecoveryService::resolve_kv_data`. Depends on Rocks iterators/write batches, `keys`, `txn_types::{Key, TimeStamp, WriteRef}`, and recoverdata protobuf responses.

Risks: destructive cleanup has no retry/rollback and comments state repeat restore is unsupported. Iterator validity and timestamp decoding must match data-key layout. `cleanup_lock` deletes all lock entries, while write/default cleanup only removes commits above resolved ts. Panics in worker threads propagate through `wait` as `safe_panic!`. Disconnected progress channel stops lock reporting but write cleanup continues after warning.

Test signals: `test_data_resolver` builds a fake engine with write/default/lock records around resolved ts 100, runs manager, and asserts newer writes/defaults and all locks are removed while older records remain.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/data_resolver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/init_cluster.rs -->
# sources/storage-engines/tikv/components/snap_recovery/src/init_cluster.rs

Purpose: prepares TiKV for snapshot recovery mode and updates local/PD cluster metadata before startup.

Important APIs and types: `enter_snap_recovery_mode` mutates `TikvConfig` for recovery. `start_recovery` opens local engines, updates local cluster id, fetches store id, and bootstraps PD using `bootcluster`. `LocalEngineService` abstracts local engine operations; `LocalEngines<EK, ER>` implements it. `create_local_engine_service` opens KV and raft engines based on config. `LOCK_FILE_ERROR` identifies running-process lock conflicts.

Control flow: recovery mode greatly extends election/stale/leader-missing timeouts, increases snapshot IO/concurrency/file-size settings, disables hibernate regions, disables prevote/check quorum, allows unsafe vote after start, disables RocksDB auto compactions, raises background jobs based on CPU quota, disables resolved-ts, increases raft client backoff, and disables practical region splitting by setting huge split thresholds. `bootcluster` constructs a PD store descriptor from server addresses, labels, binary path, timestamp, and git hash, allocates first region/peer IDs, then retries PD bootstrap up to 60 times while accepting an already-bootstrapped matching first region.

State and persistence behavior: `LocalEngines::set_cluster_id` reads and rewrites `STORE_IDENT_KEY`, then syncs KV. `create_local_engine_service` opens the actual data dir and raft dir/engine, including encryption manager setup. `handle_engine_error` exits gracefully and warns strongly on LOCK file conflicts.

Dependencies and integration points: integrates config, encryption export, Rocks engine factory, raft-log-engine, raftstore initial region, PD client, and TiKV server config. Used before normal TiKV startup in recovery workflows.

Risks: config changes are intentionally unsafe for normal operation and must be scoped to recovery. `get_store_id` unwraps missing store ident and can panic. PD bootstrap retry logs and sleeps synchronously. Opening live engines while TiKV is running is dangerous; LOCK file handling explicitly warns not to delete locks.

Test signals: no direct tests in this file; behavior is covered through recovery integration and engine-opening paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/init_cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/leader_keeper.rs -->
# sources/storage-engines/tikv/components/snap_recovery/src/leader_keeper.rs

Purpose: repeatedly forces and verifies raft leadership for selected regions during snapshot recovery.

Important APIs and types: `LeaderKeeper<'a, EK, Router>` stores a router and `not_leader` region set. `StepResult` reports `failed_leader` checks and `campaign_failed` sends. `elect_and_wait_all_ready` loops until all regions verify as leaders. `step` checks and campaigns in chunks of 256.

Control flow: `step` snapshots pending regions, for each batch asynchronously checks leader readiness by sending `SignificantMsg::LeaderCallback`. If the callback response has an error, it records failed leader and sends a casual `Campaign(ForceLeader)` message. Successfully checked regions are removed from `not_leader`. `elect_and_wait_all_ready` logs each step, waits 10 seconds via global timer, and returns when no failed leaders remain.

State and persistence behavior: only in-memory pending-region state. Actual raft leadership is changed through raftstore router messages.

Dependencies and integration points: used by `RecoveryService::recover_region`. Depends on raftstore `CasualRouter`, `SignificantRouter`, callbacks, global timer, and `KvEngine` snapshot type.

Risks: convergence depends on raftstore accepting force campaigns and callbacks. Missing regions remain pending and campaign failures are retried. The loop exits only when `failed_leader` is empty, so persistent router/store failures can hang recovery. Debug formatting intentionally truncates long result lists.

Test signals: `test_basic`, `test_failure`, and `test_many_regions` use a mock router to verify first-step campaigns, handling of missing regions, eventual success after region insertion, and batching beyond 2048 regions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/leader_keeper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/lib.rs -->
# sources/storage-engines/tikv/components/snap_recovery/src/lib.rs

Purpose: crate root for snapshot recovery.

Important APIs: publicly exposes `init_cluster` and `services`, re-exports `enter_snap_recovery_mode`, `start_recovery`, and `RecoveryService`, imports TiKV logging macros, and keeps helper modules private: `data_resolver`, `leader_keeper`, `metrics`, and `region_meta_collector`.

Control flow, state, and integration: no direct runtime logic. The public surface is intentionally narrow: callers can enter recovery mode, start recovery bootstrap, and register/use the recovery gRPC service.

Risks: changing visibility affects external recovery orchestration. Private modules are tightly coupled to `services`.

Test signals: source module tests cover private logic.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/metrics.rs -->
# sources/storage-engines/tikv/components/snap_recovery/src/metrics.rs

Purpose: Prometheus metric definitions for snapshot recovery progress and waits.

Important APIs and metrics: `REGION_EVENT_COUNTER` is a static int counter vec with labels generated by `RegionEventType`: `collect_meta`, `promote_to_leader`, `keep_follower`, `start_wait_leader_apply`, and `finish_wait_leader_apply`. `CURRENT_WAIT_APPLY_LEADER` and `CURRENT_WAIT_ELECTION_LEADER` are gauges tracking the region currently waiting for apply/election.

Control flow and integration: metrics are incremented by `RegionMetaCollector` and `RecoveryService`; gauges are updated while waiting for leaders to apply.

State and persistence behavior: process-local Prometheus registry state only.

Risks: typo/label changes affect dashboards and alerting. `CURRENT_WAIT_ELECTION_LEADER` is defined but not used in the read subset.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/region_meta_collector.rs -->
# sources/storage-engines/tikv/components/snap_recovery/src/region_meta_collector.rs

Purpose: scans local raft metadata and streams region metadata to BR during snapshot recovery.

Important APIs and types: `RegionMetaCollector<EK, ER>` owns engines, an unbounded sender, and a worker handle. `CollectWorker` performs the scan. `LocalRegion` groups optional `RaftLocalState`, `RaftApplyState`, and `RegionLocalState`, and converts to recoverdata `RegionMeta`.

Control flow: `start_report` spawns `collector_region_meta`; `CollectWorker::collect_report` scans KV `CF_RAFT` between `REGION_META_MIN_KEY` and `REGION_META_MAX_KEY`, records keys with `REGION_STATE_SUFFIX`, loads raft/apply/region states for each region, skips tombstones, requires raft and apply state, converts to `RegionMeta`, increments `collect_meta`, and sends to BR. `wait` joins the worker thread.

State and persistence behavior: read-only inspection of KV and raft engine metadata. Sends transient protobufs over mpsc. `to_region_meta` chooses peer id as the max peer id in region peer list and records epoch version, tombstone flag, key range, hard-state term, and last index.

Dependencies and integration points: used by `RecoveryService::read_region_meta`. Depends on engine traits, raft server protobufs, `keys` region metadata encoding, and recovery metrics.

Risks: missing raft/apply state for a non-tombstone region is treated as an error and can fail collection. `to_region_meta` unwraps region state, peers, raft state, and apply state, so prevalidation must remain aligned. Large region counts are buffered in memory before per-region loads.

Test signals: no direct unit tests in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/region_meta_collector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/services.rs -->
# sources/storage-engines/tikv/components/snap_recovery/src/services.rs

Purpose: implements the snapshot recovery gRPC service (`RecoverData`) that BR drives to collect region metadata, assign leaders, wait raft apply, and resolve KV data.

Important APIs and types: `RecoveryService<EK, ER>` stores engines, raft router, a 4-thread futures pool, and `last_recovery_region_rpc` for aborting overlapping recover-region tasks. `RecoverRegionState` wraps abortable futures and records start/finished state. `set_db_options` raises RocksDB level0 slowdown/stop triggers. `wait_apply_last` broadcasts a relaxed snapshot wait-apply request. `compact` manually compacts every CF after data resolution.

Control flow: `new` creates the worker pool and configures every Rocks CF for recovery. `read_region_meta` starts `RegionMetaCollector`, streams collected `RegionMeta` values to the server-streaming sink, and aborts any previous recover-region task. `recover_region` consumes a client stream, separates requested leaders/followers, runs `LeaderKeeper::elect_and_wait_all_ready`, sends per-leader `SnapshotBrWaitApply` requests and awaits oneshots, then returns store id. It replaces/aborts any prior recovery-region task. `wait_apply` broadcasts wait-apply to all regions and responds after the shared syncer fires. `resolve_kv_data` starts `DataResolverManager`, streams progress with store id, runs manual compaction, and closes the stream.

State and persistence behavior: mutates RocksDB options, raft leadership, raft apply synchronization, and KV data through `DataResolverManager`. `compact` performs manual compactions on all CFs with high subcompaction count and skips bottommost-level compaction. Overlapping recovery-region RPC state is in-memory and abortable.

Dependencies and integration points: integrates grpcio, recoverdata protobuf service trait, raftstore router/significant messages, snapshot backup wait-apply syncer, `LeaderKeeper`, `RegionMetaCollector`, `DataResolverManager`, Rocks compaction APIs, and recovery metrics.

Risks: recovery RPCs are stateful and ordering-sensitive. `recover_region` starts work only after the client closes its send stream; a stuck leader election can keep the call open until another RPC aborts it. `read_region_meta` aborts prior recover-region tasks as a protocol workaround. Many errors are logged rather than sent as structured RPC failures. Manual compaction and data deletion are heavy operations on production data. `set_db_options` unwraps Rocks option setting.

Test signals: `test_state` validates abortable recovery task state: aborting a pending future yields `Aborted`, and a completed future flips the finished flag.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/snap_recovery/src/services.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/Cargo.toml -->
# sources/storage-engines/tikv/components/sst_importer/Cargo.toml

Purpose: manifest for the SST importer crate, which handles SST upload/download, caching, import-mode switching, writing, ingestion, metrics, and errors.

Important APIs and dependencies: package `sst_importer`, edition 2021, unpublished. Features include test engine selections and failpoints. Dependencies cover API version handling, storage engines, encryption, external storage, file system, grpc/protobuf, metrics, online config, futures/tokio, txn types, UUIDs, and TiKV utilities.

Control flow and integration: the dependency graph supports both local upload/import and remote external-storage download/apply flows. Dev dependencies include test engines, importer test utilities, async compression, tempfile, and tokio-util.

State and persistence behavior: manifest only, but feature choices affect tests and engine backends.

Risks: broad workspace integration means dependency/version changes can affect importer behavior across storage, encryption, API-version, and gRPC boundaries.

Test signals: source modules contain extensive unit/integration tests; this subset includes tests for caching, import files, and import mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/caching/cache_map.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/caching/cache_map.rs

Purpose: generic keyed cache for expensive resources such as external storage pools, with lightweight time-based garbage collection.

Important APIs and types: `CacheMap<M>` wraps `Arc<CacheMapInner<M>>`. `MakeCache` abstracts construction of a cached resource; cached resources must implement `ShareOwned` to return a shareable/owned handle. `Cached<R>` tracks resource and last-used tick. `gc_loop` periodically ticks and prunes old entries. `cached_or_create` returns an existing shared resource or builds/inserts a new cached resource.

Control flow: `cached_or_create` first attempts `DashMap::get_mut`; on miss it uses entry API to avoid duplicate insertion races, increments `EXT_STORAGE_CACHE_COUNT` hit/miss metrics, constructs via `backend.make_cache`, logs insertion, stores `Cached::new`, and returns `share_owned`. `tick` increments `now` and retains entries whose `now - last_used` is below `gc_threshold`.

State and persistence behavior: process-local cache in `DashMap<String, Cached<_>>`; no persistence. GC stops automatically when the cache map is dropped because `gc_loop` holds a weak reference.

Dependencies and integration points: used by storage cache code and importer external-storage paths. Depends on `dashmap`, `tokio::time`, and importer metrics.

Risks: GC is tick-based rather than wall-clock per entry; an entry created but never hit has `last_used = 0` and can expire after enough ticks. Concurrent misses for the same key are guarded by DashMap entry insertion, but `make_cache` still runs while holding the shard entry path. `SeqCst` is conservative but not performance-free.

Test signals: `test_basic` verifies cache creation, hit reuse, and expiration behavior with a threshold of 1.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/caching/cache_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/caching/mod.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/caching/mod.rs

Purpose: module declaration for importer caching helpers.

Important APIs: exposes `cache_map` and `storage_cache` modules within the crate.

Control flow, state, and integration: no runtime logic. It groups the generic cache map and external-storage pool cache implementation used by SST importer download/apply paths.

Risks: minimal; module visibility changes affect internal imports.

Test signals: tests live in `cache_map.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/caching/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/caching/storage_cache.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/caching/storage_cache.rs

Purpose: adapts `CacheMap` to cache pools of external storage clients for a `StorageBackend`.

Important APIs and types: `StorageBackendFactory` holds a protobuf `StorageBackend` and `BackendConfig`, implements `MakeCache`, and creates a `StoragePool`. `StoragePool` stores boxed `Arc<dyn ExternalStorage>` clients and implements `ShareOwned` by returning a randomly selected storage client.

Control flow: `StoragePool::create` creates `size` external-storage clients with cloned backend config, supports failpoint `create_storage_slowly`, and returns the pool. `get` chooses a random index. `Debug` prints the URL of a selected storage or `<unknown>`.

State and persistence behavior: process-local cacheable storage clients only. No direct file writes. Failpoint may simulate slow/failing creation.

Dependencies and integration points: used by SST importer external storage cache. Depends on `external_storage`, `kvproto::brpb::StorageBackend`, `rand`, failpoints, and importer `Error`.

Risks: random selection assumes the pool is non-empty; current factory uses size 16. Creation failure of any one client fails the whole pool. URL in debug uses a random member and can vary between logs.

Test signals: covered indirectly through `CacheMap` tests and importer external-storage tests outside this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/caching/storage_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/config.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/config.rs

Purpose: online-configurable importer settings and config manager.

Important APIs and types: `Config` contains `num_threads`, `stream_channel_window`, `import_mode_timeout`, and `memory_use_ratio`; `OnlineConfig` derive enables online updates except skipped fields. `ConfigManager` wraps `Arc<RwLock<Config>>` and a weak pointer to a resizable runtime pool.

Control flow: defaults are 8 threads, stream window 128, import-mode timeout 10 minutes, memory ratio 0.3. `validate` repairs zero thread/window values to defaults and rejects memory ratios outside `[0.0, 0.5]`. `dispatch` clones current config, applies an `online_config::ConfigChange`, validates it, adjusts runtime thread count if the pool still exists, and stores the new config.

State and persistence behavior: in-memory config under RwLock. Runtime thread pool size can be changed live. Persistence, if any, is handled by the surrounding TiKV config controller.

Dependencies and integration points: imported by `sst_importer` and import-mode switchers. Uses `online_config`, `tikv_util::config::ReadableDuration`, `ResizableRuntime`, and `HandyRwLock`.

Risks: skipped fields cannot be updated online. Invalid memory ratios reject dispatch, while zero thread/window silently repair during validation. Runtime adjustment only happens if the weak pool upgrades.

Test signals: direct tests are outside this file in importer config/update paths; `sst_importer.rs` tests reference invalid config and thread update behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/errors.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/errors.rs

Purpose: unified importer error type, metric labeling, protobuf conversion, and error-code mapping.

Important APIs and types: `Error` covers IO, gRPC, UUID, future cancellation, RocksDB string errors, engine traits, parse int, file existence/corruption/path/chunk, boxed engine errors, external storage read errors, wrong key prefix, bad format, encryption, codec, file conflict, TTL/API/key-mode/resource/suspension/disk/mismatch/wrapper cases. `Result<T>` aliases this error. `error_inc` maps selected variants to `IMPORTER_ERROR_VEC` labels. `invalid_key_mode` formats invalid keys in uppercase hex. `From<Error> for import_sstpb::Error` produces gRPC response errors, including server-is-busy backoff for resource/suspension cases. `ErrorCodeExt` maps each variant to `error_code::sst_importer`.

Control flow: callers construct specific errors, optionally increment metrics with operation type, and gRPC service code can convert into protobuf errors. Error-code mapping delegates nested engine/encryption/codec mappings where available.

State and persistence behavior: increments Prometheus counters only. No persistence.

Dependencies and integration points: used throughout SST importer crate and exported from `lib.rs`. Integrates `error_code`, `kvproto`, `grpcio`, `encryption`, `engine_traits`, `tikv_util::codec`, and importer metrics.

Risks: `error_inc` intentionally ignores variants not in its match, so new errors may lack metrics unless added. Typo `RESOURCE_NOT_ENOUTH` is in the existing error-code constant and must stay aligned. Protobuf conversion loses detailed structured fields for most variants.

Test signals: no direct tests in this file; behavior is exercised by importer service tests and error-code tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/import_file.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/import_file.rs

Purpose: manages on-disk SST upload files, file naming, validation, deletion, ingestion preparation, checksum verification, and listing.

Important APIs and types: `ImportPath` holds `save`, `temp`, and `clone` paths. `ImportFile` writes an uploaded SST to temp while tracking CRC32 and renames it to save on finish. `ImportDir<E>` owns root, `.temp`, and `.clone` directories and provides path, create, delete, exist, validate, API-version check, ingest, checksum, and list operations. `sst_meta_to_path`, `sst_meta_to_path_v1`, and `parse_meta_from_path` encode/decode SST filenames. `API_VERSION_2` is the current filename version.

Control flow: `ImportDir::new` clears and recreates temp/clone dirs. `ImportFile::create` uses `DataKeyManager` encrypted writer when present or `create_new` file open otherwise. `append` writes bytes and updates CRC. `finish` validates CRC, syncs file, rejects existing save path, links encryption metadata if needed, renames temp to save, and leaves directory sync to `ImportPath::save` for callers using that path helper. `Drop` cleans unfinished temp files and encryption metadata. `join_for_read` prefers v2 filenames if they exist and falls back to v1 for old TiKV files. `ingest` checks API compatibility, prepares hard-linked/copied clone files, groups paths by CF, and calls `ingest_external_file_cf` with `force_allow_write`.

State and persistence behavior: creates/removes directories and files under importer root, syncs file contents, renames temp to durable save path, creates clone files for ingestion, removes encryption metadata on cleanup, and reads SST metadata/checksums. API compatibility may scan SST key ranges against TiDB range complements.

Dependencies and integration points: used by `SstImporter` and writers. Depends on engine `SstReader`/ingestion traits, file system helpers, encryption `DataKeyManager`, `keys`, `api_version`, import protobuf metadata, UUID, CRC32, and importer metrics.

Risks: file lifecycle must be crash-safe; temp/clone dirs are wiped at `ImportDir::new`. `finish` does not sync the directory after rename, while `ImportPath::save` does. `check_api_version` unwraps its result inside `ingest`, and incompatible version panics rather than returning an error. Filename parsing supports legacy formats with missing CF/API version, so callers must handle partially populated metadata. `Drop` cleanup can race with external use if ownership semantics are misused.

Test signals: tests cover v2 path encoding/decoding, legacy path parsing, v2/v1 read fallback, and feature-gated SST path handling with and without encryption key manager.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/import_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/import_mode.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/import_mode.rs

Purpose: switches the whole RocksDB instance between normal mode and importer-optimized mode, then automatically restores normal mode after a timeout.

Important APIs and types: `ImportModeSwitcher` wraps `ImportModeSwitcherInner` and an atomic `is_import`. Public methods are `new`, `start_resizable_threads`, `enter_normal_mode`, `enter_import_mode`, and `get_mode`. `ImportModeDbOptions` stores `max_background_jobs`; `ImportModeCfOptions` stores L0 stop/slowdown triggers and pending-compaction limits. `RocksDbMetricsFn` reports option values.

Control flow: entering import mode snapshots current DB/CF options, sets DB `max_background_jobs` to at least 32, sets CF L0 stop/slowdown triggers to at least `1 << 30`, and disables soft/hard pending compaction byte limits. Entering normal mode restores all saved options. The background timer checks `next_check`; if timeout has elapsed and import mode is still active, it restores normal mode and schedules the next check. Each explicit `enter_import_mode` refreshes timeout and metrics function.

State and persistence behavior: mutates live RocksDB options and stores backups in memory. No on-disk metadata records the prior mode, so process restart relies on Rocks/default config rather than switcher memory.

Dependencies and integration points: used by `SstImporter` to reduce write stalls during bulk import. Depends on `KvEngine` option traits, global timer, resizable runtime handle, import config, and import protobuf `SwitchMode`.

Risks: correctness depends on capturing options before the first import-mode transition and restoring them exactly. `ImportModeCfOptions::new_options` unwraps CF option access. If the process exits while in import mode, in-memory backup is lost. The timer loop uses a weak reference and exits when switcher drops.

Test signals: tests verify option transitions, idempotent enter/exit, automatic timeout restoration, and that import mode does not reduce an already-high L0 stop writes trigger.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/import_mode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/import_mode2.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/import_mode2.rs

Purpose: tracks import mode at key-range granularity for V2 import flows rather than mutating global RocksDB options.

Important APIs and types: `HashRange` is a hashable start/end key range converted from protobuf `Range`. `ImportModeSwitcherV2` wraps a mutex containing timeout and `HashMap<HashRange, Instant>`. Public methods add ranges, clear ranges, check whether a region or range overlaps active import ranges, list active ranges, and start timeout cleanup.

Control flow: `ranges_enter_import_mode` inserts or refreshes ranges with `now + timeout`. `start_resizable_threads` runs a background timer that clears previously selected expired ranges, then finds the minimum next expiration and waits until then. `region_in_import_mode` and `range_in_import_mode` scan active ranges and use half-open overlap checks where empty end key means unbounded.

State and persistence behavior: in-memory map only. Import-mode membership disappears on process restart or switcher drop.

Dependencies and integration points: used by SST importer V2 range import tracking and exported helper `range_overlaps` from crate root. Depends on import protobuf `Range`, metapb `Region`, global timer, and resizable runtime handle.

Risks: overlap checks are byte-lexicographic and assume encoded key ordering. The timer loop only clears ranges that were identified in the previous iteration as earliest expirations, then recomputes; correctness depends on renewed ranges updating their expiration before cleanup. Scanning all ranges for every region/range check can be costly with many active ranges.

Test signals: tests cover region/range overlap edge cases, adding/clearing ranges and region membership, and timeout behavior with renewed ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/import_mode2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/lib.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/lib.rs

Purpose: crate root for SST importer functionality.

Important APIs: enables nightly `min_specialization` and `error_reporter`, imports serde derive and TiKV macros, declares internal modules (`config`, `errors`, `import_file`, `sst_merge_iter`, `sst_writer`, `util`, `caching`) and public modules (`import_mode`, `import_mode2`, `metrics`, `sst_importer`). Re-exports core API: `Config`, `ConfigManager`, `Error`, `Result`, `error_inc`, `API_VERSION_2`, `sst_meta_to_path`, `range_overlaps`, `SstImporter`, `BinaryIterator`, `RawSstWriter`, `TxnSstWriter`, `copy_sst_for_ingestion`, and `prepare_sst_for_ingestion`.

Control flow, state, and integration: no direct runtime logic. It defines the public crate surface consumed by TiKV server, import services, and tests.

Dependencies and integration points: `server2.rs` imports `ImportSstService` and `SstImporter` through TiKV, while this crate exports lower-level importer building blocks.

Risks: public re-export changes are breaking for downstream modules. Nightly feature usage ties the crate to compiler capabilities.

Test signals: tests live in module files.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/metrics.rs -->
# sources/storage-engines/tikv/components/sst_importer/src/metrics.rs

Purpose: Prometheus metric definitions for SST importer RPCs, upload/write/download/apply/ingest operations, external storage caching, in-memory file cache, and applier engine requests.

Important APIs and metrics: histograms include `IMPORT_RPC_DURATION`, upload chunk bytes/duration, local write chunk duration, download duration/bytes, apply bytes/duration, ingest duration/bytes/count, and applier engine request duration. Counters/gauges include RPC count, local write bytes/keys, importer error counter, apply count, compacted download keys, external storage cache operations, cached file bytes, cache events, and applier events.

Control flow and integration: importer code observes these metrics around gRPC calls, file upload/write paths, external downloads, ingestion, apply, cache operations, and error handling. `errors.rs` increments `IMPORTER_ERROR_VEC`; `cache_map.rs` increments `EXT_STORAGE_CACHE_COUNT`.

State and persistence behavior: process-local Prometheus registry state only.

Risks: metric names include historical typos such as `INPORTER_INGEST_COUNT` and `INPORTER_APPLY_COUNT`; renaming would break dashboards. Label cardinality should remain bounded (`request/result`, `type`, `operation`, `error`).

Test signals: no direct tests; metrics are validated indirectly by compile/link and runtime metric registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/sst_importer/src/metrics.rs -->
