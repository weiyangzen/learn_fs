# subset-b-008865 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/cluster.rs -->
# sources/storage-engines/tikv/components/test_raftstore-v2/src/cluster.rs

Purpose: this file is the raftstore-v2 test cluster harness. It abstracts a group of TiKV stores behind `Cluster<T, EK>` where `T: Simulator<EK>` supplies either in-process nodes or full server nodes and `EK: KvEngine` is usually RocksDB-backed tablets. It gives integration tests a compact API for bootstrapping stores, discovering leaders, issuing reads/writes/admin commands, manipulating network filters, inspecting raft metadata, and waiting for split/merge/GC/unsafe-recovery outcomes.

Important APIs, types, and functions: `Simulator<EK>` is the contract implemented by `NodeCluster` and `ServerCluster`: it starts/stops a node, owns send/receive filters, exposes `StoreRouter`, snapshot manager and raft message delivery, and supplies async snapshot/read/peer-message command paths. The default `read` path converts reads into a snapshot request because raftstore v2 only supports snapshot-based local reads here, then answers `Get` commands from the returned `RegionSnapshot`. `call_query_on_node` and `call_command_on_node` translate status/admin/simple write requests into `PeerMsg` variants. Simple writes are encoded through `SimpleWriteEncoder`; `DeleteRange` is supported in synchronous `call_command_on_node` but explicitly unimplemented in the default async path. `Cluster` stores config, leader cache, per-store `TabletRegistry`, `RaftTestEngine`, `StoreMeta`, key managers, IO limiter, stats, SST workers, PD client, and an `engine_creator` hook. `WrapFactory<EK>` adapts the v2 tablet registry plus raft engine to the legacy `Peekable`, `SyncMutable`, and `RawEngine` traits used by older test utilities.

Control flow: `run()` creates engines, bootstraps the first region on every store, and starts all nodes. `run_conf_change()` bootstraps only store 1 with the first region so tests can exercise membership changes. `start()` restarts already registered nodes first, then creates missing engines, store metadata, thread group properties, and simulator nodes. `run_node()` recreates per-store `StoreMeta` before delegating to the simulator. `stop_node()` marks thread group shutdown, stops the simulator node, shuts the store down in the test PD client, and aggressively removes opened tablets after waiting briefly for references to drop. `bootstrap_region()` registers all engines under fixed store IDs, builds region 1 with peers on every store, writes prepare-bootstrap and initial raftstore-v2 states into each raft engine, then mirrors the cluster metadata into test PD. `add_new_engine()` creates a new store after startup and immediately runs it.

Request and admin flow: `leader_of_region()` polls PD for voters, skips stopped stores, asks alive voters for `RegionLeader`, caches a leader only when a quorum observes it and the leader store is still live, and handles joint-state tests approximately with a simple majority. `call_command_on_leader()` retries when `refresh_leader_if_needed()` sees not-leader, stale-command, or "not applied to current term" errors. `request()` finds the current PD region for a key, builds a `RaftCmdRequest`, retries around timeouts, stale leadership, epoch-not-match after splits, and merge-mode errors, then returns the response. Helpers such as `must_put_cf`, `must_delete_range_cf`, `must_transfer_leader`, `must_split`, `try_merge`, `must_remove_region`, `wait_tombstone`, `enter_force_leader`, and flashback helpers encode common raftstore test scenarios and assert on expected protocol behavior.

State and persistence behavior: unlike v1, v2 stores user data in per-region tablets and raft metadata in the raft engine. `create_test_engine`-supplied registries are tracked by store ID. `flush_data`, `must_flush_cf`, and `scan` iterate opened tablets. `scan_region()` intersects the requested data-key range with PD region boundaries before scanning a tablet. `apply_state()` intentionally returns in-memory debug information, because v2 persists `RaftApplyState` infrequently; `region_local_state()` and raft-local-state helpers read through `WrapFactory` from `RaftTestEngine`. `bootstrap_store()` writes `StoreIdent` only to an empty raft engine. `WrapFactory` maps data keys to PD regions, returns no data for tombstone peers, and dispatches reads/writes to the current tablet, but leaves message reads and range deletes unimplemented.

Dependencies and integration points: this harness sits between `test_pd_client`, `raftstore_v2::{StoreRouter, PeerMsg, StoreMeta, StateStorage}`, `raftstore::store` compatibility types, `engine_traits::TabletRegistry`, `engine_test::raft::RaftTestEngine`, TiKV config, resource control, encryption, IO rate limiting, and network filters from `test_raftstore`. It intentionally reuses legacy request builders (`new_request`, `new_admin_request`, `new_peer`, etc.) so the same tests can target v1 and v2 clusters with limited changes.

Risks and test signals: many APIs panic on timeout or unexpected response, which is appropriate for test assertions but can hide whether the root cause is PD metadata, leader discovery, or peer execution. The leader quorum calculation is simplified for joint consensus. Several APIs are placeholders (`send_half_split_region_message`, async `DeleteRange`, range deletes and `get_msg_cf` in `WrapFactory`), so tests depending on those legacy surfaces need v1 or additional v2 implementation. V2-specific tests should watch for non-empty tablets after stop, `StoreMeta` reference leaks, stale leader cache retries, and debug-info consistency because apply state is not always persisted.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/lib.rs -->
# sources/storage-engines/tikv/components/test_raftstore-v2/src/lib.rs

Purpose: this crate root exposes the raftstore-v2 test harness as a single import surface. It enables unstable Rust features needed by the crate, declares private modules for cluster, node, server, and transport simulation, makes `util` public, and publicly re-exports all module exports.

Important APIs, types, and functions: there are no local functions or types. The important behavior is export shaping: `pub use crate::{cluster::*, node::*, server::*, transport_simulate::*, util::*};` lets integration tests import constructors such as `new_node_cluster`, `new_server_cluster`, `Cluster`, `Simulator`, `SimulateTransport`, and utility helpers from `test_raftstore_v2` without module-qualified paths.

Control flow: compile-time module loading only. `cluster`, `node`, `server`, and `transport_simulate` are private modules but their public items are re-exported; `util` is also a public module for callers that want its namespace.

State and persistence behavior: none directly. All persistent test state is owned by the modules this root exposes.

Dependencies and integration points: `#![allow(incomplete_features)]` and `#![feature(type_alias_impl_trait)]` allow the crate to use unstable type-alias impl trait patterns in the v2 harness. The root integrates with TiKV's internal test crates by acting as the facade consumed by raftstore-v2 integration tests.

Risks and test signals: because this is a glob re-export facade, adding public names in submodules can change the crate API or create name ambiguity for downstream tests. Any compile failure here is usually caused by renamed module symbols or removed unstable feature needs rather than runtime logic.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/node.rs -->
# sources/storage-engines/tikv/components/test_raftstore-v2/src/node.rs

Purpose: this file implements the in-process raftstore-v2 simulator. `NodeCluster<EK>` runs `NodeV2` instances without the TiKV gRPC/storage server layer, while still exercising raftstore, tablet snapshots, coprocessor registration, split configuration, SST import, resource control, and simulated network filters.

Important APIs, types, and functions: `ChannelTransport<EK>` is a clonable `Transport` that forwards `RaftMessage`s to destination store routers held in `ChannelTransportCore`. Snapshot messages are special: `send()` copies tablet snapshot files from the sender `TabletSnapManager` to the receiver via `copy_tablet_snapshot`, then reports `SnapshotStatus::Finish` to the sender router. `NodeCluster<EK>` owns the shared transport, PD client, live `NodeV2` map, per-node outbound `SimulateTransport`, concurrency managers, tablet snapshot managers, and config controllers. Public helpers expose a node's `ConcurrencyManager` and `ConfigController`.

Control flow: `run_node()` validates raftstore config for v2, constructs `NodeV2`, bootstraps the store through `try_bootstrap_store`, attaches `StateStorage` to the tablet factory, creates or reuses the tablet snapshot manager, wraps the node router in a raftstore-v2 `RaftRouter`, constructs the coprocessor host, registers replica-read lock checking and split config management, creates an SST importer, background worker, global replication state, and store config, then starts the node. After startup it registers the raftstore config manager, installs snapshot paths and simulated routers into the shared transport core, and records the node and controller maps. `async_snapshot()` and `async_peer_msg_on_node()` look up the simulated router and delegate to snapshot or peer-message APIs. `stop_node()` stops the `NodeV2` and removes the router.

State and persistence behavior: the node simulator uses a supplied `RaftTestEngine` for raft state and a `TabletRegistry<EK>` for per-region KV tablets. Snapshot directories are temp dirs keyed by store ID and reused across restarts when present. `StateStorage` binds the raft engine and node router to the tablet factory so tablet metadata and raftstore-v2 state can coordinate. The transport's snapshot copy path is the main persistence-sensitive path: missing sender/receiver snapshot managers make message delivery fail.

Dependencies and integration points: it integrates `tikv::server::NodeV2`, raftstore-v2 routers and `StoreMeta`, `CoprocessorHost`, `AutoSplitController`, `SplitConfigManager`, `SstImporter`, `GrpcServiceManager`, resource metering handles, encryption key managers, and `test_pd_client`. It implements the `Simulator<EK>` trait from `cluster.rs`, making it usable by the generic `Cluster`.

Risks and test signals: this simulator intentionally omits the server and storage layers, so tests using client RPCs, lock manager behavior, or full storage scheduling must use `ServerCluster`. `set_store_allowlist` is unimplemented. Missing routers produce raftstore errors; tests using filters should distinguish send filters on `simulate_trans` from receive filters on router wrappers. Snapshot tests should verify both the snapshot file copy and snapshot status reporting path. The node asserts the prepared bootstrap region is consumed after startup, which is a strong bootstrap correctness signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/server.rs -->
# sources/storage-engines/tikv/components/test_raftstore-v2/src/server.rs

Purpose: this file implements the full raftstore-v2 server-backed simulator. `ServerCluster<EK>` runs `NodeV2`, `RaftKv2`, TiKV `Storage`, gRPC `Server`, import/debug/diagnostics/deadlock services, GC, lock manager, resource metering, and raft network clients so tests can exercise behavior above the raftstore layer.

Important APIs, types, and functions: `TestRaftKv2<EK>` wraps `RaftKv2<EK, RaftTestEngine>` and implements the storage `Engine` trait while injecting filters into the raft extension. `TestExtension<EK>` wraps TiKV's raft extension and applies `filter_send` to inbound raft messages before feeding them to raftstore. `ServerMeta<EK>` holds all per-store runtime objects: `NodeV2`, gRPC server, simulated store router, simulated server transport, raw router, GC worker, optional resolved-ts worker, and resource-metering cleanup. `ServerCluster<EK>` owns server metadata, address map, storages, region info accessors, snapshot managers, raft clients, security manager, service hooks, health services, txn-extra schedulers, and causal timestamp providers. Constructors build v1-compatible, incompatible-PD, API-version-specific, KV-client, debug-client, and forwarding-test clusters.

Control flow: `run_node_impl<F: KvFormat>()` is the core startup routine. It creates/reuses a tablet snapshot manager, allocates or reuses a listening address, validates v2 raftstore config, bootstraps `NodeV2`, attaches `StateStorage`, creates a raft router and coprocessor host, constructs `RaftKv2` wrapped as `TestRaftKv2`, builds storage read pools, initializes concurrency timestamps from PD TSO, starts GC, optionally starts resolved-ts and API-v2 causal-ts providers, initializes resource metering, builds lock manager, quota limiter and `Storage`, registers replica-read lock checking, constructs import and deadlock services, creates PD resolver and coprocessor endpoints, then retries gRPC bind up to 100 times. After binding, it starts `NodeV2`, starts the lock manager and gRPC server, records metadata, address, concurrency manager, and raft client.

Simulator flow: the `Simulator<EK>` implementation dispatches startup through `dispatch_api_version!`, applies send filters to the server transport and receive filters to the store router wrapper, stops server/node/workers/cleanup on shutdown, delegates snapshots and peer messages to `sim_router`, and sends external raft messages through the per-store `RaftClient` followed by flush. Cluster extension methods add snapshot retrieval from the storage engine, address lookup, and security manager access.

State and persistence behavior: persistent test state spans raft engine, tablet registry, tablet snapshots, gRPC address reuse, PD metadata, transaction status cache, resolved-ts state, and resource-metering workers. Snapshot managers are cached by store ID; temp paths are retained in `snap_paths`. The gRPC address map is reused across restarts to reflect TiKV's cached store address behavior. `get_causal_ts_provider()` exists only when API V2 is active. Resource metering creates recorder/reporter/single-target workers and returns an explicit cleanup closure that `stop_node()` must run.

Dependencies and integration points: this is one of the densest integration files in the harness. It connects `api_version`, `causal_ts`, `concurrency_manager`, `grpcio`, `grpcio_health`, `raftstore_v2`, `resource_metering`, `security`, `service::GrpcServiceManager`, TiKV server/storage/import/coprocessor/read-pool/lock-manager modules, `test_pd_client`, and legacy `test_raftstore` filter/address helpers. It also installs optional pending services and a debug service factory so tests can add custom gRPC surfaces before startup.

Risks and test signals: startup is complex and order-sensitive: state storage must be set before tablets are used, coprocessor observers must be registered before node start, and gRPC bind retries can mask leaked ports from previous tests. `async_snapshot()` has an unreachable branch for missing store metadata, so callers should not request snapshots from stopped nodes. Tests should assert server stop cleans resolved-ts and resource metering workers, that filters affect the intended path, and that API V2 causal timestamp state is present only for API V2. The helper `setup_cluster()` deliberately verifies follower RPC without forwarding headers returns `store_not_match`, making it a useful server-layer sanity test.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/transport_simulate.rs -->
# sources/storage-engines/tikv/components/test_raftstore-v2/src/transport_simulate.rs

Purpose: this file provides transport and router adapters that let raftstore-v2 tests inject message filters while still using the normal raftstore-v2 router and snapshot APIs.

Important APIs, types, and functions: `SimulateTransport<C>` wraps any channel/router-like object `C` plus an `Arc<RwLock<Vec<Box<dyn Filter>>>>`. It exposes `add_filter`, `clear_filters`, and `filters` for tests and higher-level wrappers. Its `Transport` implementation applies `test_raftstore::filter_send` before delegating `RaftMessage` delivery, while pass-through methods preserve allowlist, flush, and need-flush behavior. `SnapshotRouter<EK>` abstracts async snapshot acquisition and is implemented for both raw `RaftRouter<EK, ER>` and `SimulateTransport<C>`. `RaftStoreRouter` abstracts sending peer messages, raft messages, and snapshot status reports; it is implemented for raftstore-v2 `RaftRouter` and for the simulated wrapper.

Control flow: outbound transport sends enter the filter list first; if filters allow the message, the inner transport sends it. Snapshot calls bypass filters and delegate to the inner router snapshot method. Raft message delivery through `RaftStoreRouter` also applies filters in the `SimulateTransport<C>` implementation, which is how receive-side router wrappers simulate dropped or altered inbound messages.

State and persistence behavior: the only local state is the shared filter list. Snapshot persistence is not handled here; snapshot copy/report behavior is supplied by `node.rs` and server transport implementations.

Dependencies and integration points: it bridges legacy `test_raftstore::Filter` with raftstore-v2 `Transport`, `PeerMsg`, `RaftRouter`, and `RegionSnapshot` APIs. `handle_send_error` converts router send errors to raftstore results with region context.

Risks and test signals: filter ordering and shared ownership matter. Clones share the same filter list, so clearing filters on one clone affects all paths derived from it. Snapshot acquisition is not filtered, so tests simulating read/snapshot failures need to filter the underlying raft messages or use router behavior. `send_peer_msg` in the wrapper does not apply filters because filters are raft-message oriented; this distinction is important for tests that inject `PeerMsg` directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/transport_simulate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/util.rs -->
# sources/storage-engines/tikv/components/test_raftstore-v2/src/util.rs

Purpose: this file collects raftstore-v2 test utilities for engine creation, config shaping, data generation, peer reads, delete-range assertions, wait loops, and transactional gRPC peer clients.

Important APIs, types, and functions: `create_test_engine()` builds a temp TiKV data directory, encryption key manager, Rocks environment, `RaftTestEngine`, optional `StoreIdent`, SST recovery worker, and `TabletRegistry<RocksEngine>`. `put_till_size` and `put_cf_till_size` write random batches until an approximate size limit is reached and flush tablets to make size properties observable. `configure_for_encryption`, `configure_for_snapshot`, and `configure_for_lease_read_v2` mutate `Config` for encryption, fast snapshot triggering, and lease timing. Read helpers include `read_on_peer`, `async_read_on_peer`, `batch_read_on_peer`, `async_read_index_on_peer`, and `must_read_on_peer`. `PeerClient` wraps a gRPC `TikvClient` plus region context and delegates raw get/prewrite/commit/rollback/pessimistic-lock helpers to legacy `test_raftstore` utilities.

Control flow: engine creation clones and adjusts `Config`, infers raft paths, builds shared Rocks cache/env, starts lazy SST recovery, builds raft engine, bootstraps a store when `(cluster_id, store_id)` is supplied, then creates a tablet registry rooted under the temp dir. Size-writing loops batch `Put` commands through `Cluster::batch_put` and flush after each chunk. Read helpers construct raft command requests with explicit peers and region epochs, then call the generic `Simulator` async snapshot/read paths. `wait_for_synced()` repeatedly snapshots a leader-backed storage engine until it can assert max-ts synchronization in the snapshot extension.

State and persistence behavior: temp dirs hold Rocks, raft engine, tablet, and import/snapshot state depending on caller. Encryption config uses a test file master key and short data-key rotation. Snapshot config reduces log GC thresholds and intervals to force snapshot transfer. `configure_for_lease_read_v2()` derives leader lease and stale-peer durations from election timing so lease-read tests have internally valid timing. Delete-range tests verify `notify_only` does not delete data before issuing a real full-range delete.

Dependencies and integration points: it coordinates TiKV `KvEngineFactoryBuilder`, `ConfiguredRaftEngine`, `TabletRegistry`, `IoRateLimiter`, encryption export, PD client TSO, gRPC clients, storage `SnapContext`, transaction request helpers, and the generic v2 `Cluster<T, EK>` interface. It also reuses request builders and MVCC test helpers from `test_raftstore`.

Risks and test signals: size estimates are approximate and rely on flushing to SST; tests should not treat exact byte counts as deterministic. Many helpers panic after bounded retries, so failures signal test harness or raftstore liveness issues. `wait_for_synced` depends on server-backed clusters and snapshot transaction extensions; it is not valid for node-only clusters. `PeerClient` contexts can become stale after splits or leadership changes, so tests using it should refresh context when region epoch changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore-v2/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/Cargo.toml -->
# sources/storage-engines/tikv/components/test_raftstore/Cargo.toml

Purpose: this manifest defines the legacy `test_raftstore` internal test-support crate. It is not published and provides the shared v1 harness and helper APIs used directly by tests and indirectly by the raftstore-v2 harness.

Important APIs, types, and functions: the manifest does not define code APIs, but its feature flags select engine backends. Defaults enable `test-engine-kv-rocksdb` and `test-engine-raft-raft-engine` through the `raftstore` crate. Additional feature groups expose `test-engines-rocksdb` and `test-engines-panic`.

Control flow: Cargo resolves this crate as edition 2018 with workspace dependencies for TiKV internals. Feature flags are propagated to `raftstore`, making the test harness compile against selected test engine combinations.

State and persistence behavior: none directly, but dependencies enable RocksDB, raft engine, hybrid/in-memory engines, encryption, import, resource control, resolved-ts, and TiKV server/storage components that create real temp on-disk state during tests.

Dependencies and integration points: the dependency list is intentionally broad: `raftstore` with `testexport`, `tikv`, `test_pd_client`, `engine_rocks`, `engine_test`, `engine_traits`, `kvproto`, `pd_client`, `resource_metering`, `service`, `security`, `grpcio`, `tokio`, and transaction/types crates. This breadth shows `test_raftstore` is the cross-layer test facade rather than a small unit-test helper.

Risks and test signals: changes to defaults can silently move tests to different engines. Removing a dependency may break re-exported helpers even when the manifest appears over-broad. Because `test_raftstore-v2` imports many items from this crate, dependency or feature changes here can affect both legacy and v2 test harnesses.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/cluster.rs -->
# sources/storage-engines/tikv/components/test_raftstore/src/cluster.rs

Purpose: this file is the legacy raftstore v1 test cluster harness. It provides the generic `Cluster<T: Simulator>` API used by integration tests to create multi-store raft clusters, inject failures, route raft commands, inspect Rocks/raft metadata, force split/merge/conf-change/admin flows, and validate persistence outcomes.

Important APIs, types, and functions: `Simulator` is implemented by node-backed and server-backed harnesses. It starts/stops nodes with full `Engines<RocksEngine, RaftTestEngine>`, `StoreMeta`, routers and batch systems, supports async command and read callbacks, exposes snapshot manager/router/apply router, and controls send/receive filters. `Cluster<T>` owns config, leader cache, temp paths, engine bundles, store metadata, key managers, IO limiter, labels, group properties, SST workers, stats, simulator, test PD client, resource manager, and force-partition manager. `RawEngine<EK>` is a compatibility trait combining `Peekable` and `SyncMutable` with region/raft/apply state reads; `RocksEngine` implements it by reading `CF_RAFT` metadata keys.

Control flow: `create_engines()` builds temp engines; `start()` restarts registered stores, then creates raft batch systems and starts missing stores through the simulator. `run()` bootstraps all stores with fixed IDs and region 1 before start. `run_conf_change()` bootstraps only store 1. `run_node()` recreates store metadata and raft batch system, applies labels, sets thread group properties, and delegates to the simulator. `stop_node()` marks shutdown, stops simulator state, and tells test PD the store is down. `restart_engine()` closes and recreates one engine bundle from the same temp directory, allowing restart/recovery tests.

Request and admin flow: reads use `make_cb` and the simulator local-read path; writes and admin commands use router callbacks. `leader_of_region()` and `refresh_leader_if_needed()` mirror the v2 leader cache and retry logic. `request()` locates the PD region for a key, sends through the current leader, and retries timeouts, not-leader, stale command, epoch-not-match, and merge-mode responses. Admin helpers cover async add/remove peer and exit-joint, leader transfer, split/merge, peer GC, force leader, flashback, bucket refresh, half-split, region existence/removal, and bucket retrieval.

State and persistence behavior: v1 stores data and raftstore metadata in Rocks engines with raft metadata under `CF_RAFT`; raft log state is in the raft engine. `bootstrap_region()` writes `StoreIdent` and prepare-bootstrap metadata via legacy helpers. `apply_state`, `region_local_state`, and peer-state waiters read encoded protobufs from `CF_RAFT`. `restore_kv_meta()` copies a region's raftstore metadata and raft log key ranges from a snapshot back into Rocks, which is specific to the legacy storage layout. `flush_data`, `compact_data`, `must_flush_cf`, and `scan` operate directly on Rocks column families.

Dependencies and integration points: this harness binds `raftstore::store::fsm` routers and batch systems, `test_pd_client`, `engine_rocks`, `engine_test::raft`, TiKV config/server result types, encryption, IO rate limiting, resource control, key helpers, protobuf command builders, and legacy transport/filter helpers. It is the API surface consumed by many older TiKV tests and also supplies shared utilities to the v2 harness.

Risks and test signals: this file intentionally panics on assertion failure and timeout, so it is test-only. Leader detection uses simplified quorum logic in joint consensus. The harness has many direct Rocks metadata assumptions that do not apply to v2 tablets. `restart_engine()` indexes by `node_id - 1` and reinserts the last DB clone, so tests with non-contiguous IDs need care. Callback-based async APIs require callers to drain futures; dropped callbacks can look like timeouts. Strong test signals include `must_peer_state`, `wait_applied_to_current_term`, `must_gc_peer`, `refresh_region_bucket_keys` callback validation, and disk/raft metadata reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/common-test.toml -->
# sources/storage-engines/tikv/components/test_raftstore/src/common-test.toml

Purpose: this TOML file defines the common TiKV test configuration used by the legacy raftstore harness. It shrinks thread pools, ports, timeouts, caches, and background work so multi-store integration tests run quickly and deterministically on local temp directories.

Important settings: read pools are unified and set to one thread; server address is `127.0.0.1:0`; gRPC concurrency and raft connection counts are low; storage scheduler concurrency is modest; block cache is 64 MB; raftstore tick intervals and heartbeat/election values are short; log GC, raft-engine purge, PD heartbeat, split/merge checks, and region flow reporting run quickly; hibernate regions and dev assertions are enabled; store IO pool is disabled in the legacy config; apply/store/snapshot generator pools are small; RocksDB/RaftDB background jobs and Titan GC are constrained; resolved-ts is disabled by default.

Control flow: this file is consumed by config construction helpers rather than executed. `Config::new` copies the loaded `TikvConfig` and points `cfg_path` at a temp config file so online-config tests do not mutate this shared TOML.

State and persistence behavior: default paths are supplied elsewhere by temp dirs. The config affects persistent behavior indirectly by accelerating raft log GC, snapshot generation/GC, stale-peer checks, compaction, and import/GC workers. Short durations make state transitions observable inside typical test timeouts.

Dependencies and integration points: sections map to TiKV config modules: `readpool`, `server`, `storage`, `raftstore`, `rocksdb`, `raftdb`, `security`, `import`, `gc`, `pessimistic-txn`, and `resolved-ts`. The same defaults influence both node and server clusters unless tests mutate them.

Risks and test signals: these settings are intentionally non-production. Very short raft and PD intervals can reveal races in tests but may also make timing-sensitive tests flaky under heavy load. Changing a duration here affects many integration tests globally. The v2 cluster overrides store IO pool to at least one because raftstore v2 always uses async write.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/common-test.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/config.rs -->
# sources/storage-engines/tikv/components/test_raftstore/src/config.rs

Purpose: this file wraps `TikvConfig` for tests so each cluster gets an isolated temporary config path while preserving ergonomic access to TiKV configuration fields.

Important APIs, types, and functions: `Config` holds `cfg_dir: Option<TempDir>`, `tikv: TikvConfig`, and `prefer_mem: bool`. `Config::new()` creates a temp config directory, rewrites `tikv.cfg_path` to `<temp>/tikv.toml`, and stores the preference for memory-backed temp dirs. `Clone` deliberately drops `cfg_dir` while cloning the underlying TiKV config and `prefer_mem`. `Deref` and `DerefMut` expose `TikvConfig` fields directly.

Control flow: callers create a `Config` around a `TikvConfig` before passing it to cluster/node/server setup. When a config is cloned for node startup, the clone does not own a temp dir; the original cluster config keeps the temp directory alive.

State and persistence behavior: the temp config directory is the only owned state. It prevents online config writes from modifying `common-test.toml` or other shared files. Dropping cloned `cfg_dir` ownership avoids multiple `TempDir` handles attempting to represent the same persistent location.

Dependencies and integration points: it is used by both legacy and v2 harnesses. Because it dereferences to `TikvConfig`, existing code can pass `Config` into validation and engine path inference with minimal friction.

Risks and test signals: clones have `cfg_dir: None`, so code that needs the temp directory path must use the original `Config` or handle `None`. Helpers such as encryption setup rely on `cfg_dir` being present and should run before cloning into node/server startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/lib.rs -->
# sources/storage-engines/tikv/components/test_raftstore/src/lib.rs

Purpose: this crate root exposes the legacy raftstore test harness. It declares the core modules, enables the `trait_alias` feature, imports `tikv_util` macros, and re-exports cluster, config, node, router, server, transport simulation, and utility APIs.

Important APIs, types, and functions: no local runtime functions are defined. The critical API is the public facade: `pub use crate::{cluster::*, config::Config, node::*, router::*, server::*, transport_simulate::*, util::*};`. This makes request builders, cluster constructors, filters, routers, and helpers available from the crate root.

Control flow: compile-time module declaration and re-export only. `cluster`, `config`, `node`, `router`, `server`, and `transport_simulate` are private modules with public items re-exported; `util` is public as a module as well.

State and persistence behavior: none directly. State is owned by the underlying cluster/node/server modules.

Dependencies and integration points: `#[macro_use] extern crate tikv_util;` makes macros such as `defer!`, `box_err!`, logging helpers, and safe panic utilities available to submodules in the older style used by this crate.

Risks and test signals: glob re-exports make this root sensitive to symbol collisions and API churn in submodules. Feature or macro import changes can break broad parts of the test harness even though this file has no runtime logic.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/node.rs -->
# sources/storage-engines/tikv/components/test_raftstore/src/node.rs

Purpose: this file implements the legacy in-process raftstore node simulator. `NodeCluster` runs `MultiRaftServer` instances without the external TiKV gRPC storage server, providing fast tests for raftstore behavior, local reads, snapshots, coprocessor hooks, import, split checks, and network filters.

Important APIs, types, and functions: `ChannelTransport` delivers `RaftMessage`s between stores by looking up simulated `ServerRaftStoreRouter`s. Snapshot messages register sending/receiving `SnapEntry`s, copy snapshot files, deregister entries with `defer!`, and report `SnapshotStatus::Finish`. `NodeCluster` holds the transport, PD client, live `MultiRaftServer`s, snapshot managers, config controllers, simulated transports, concurrency managers, importers, and an optional post-coprocessor hook. Public helpers expose node routers, nodes, concurrency managers, config controllers, and importers.

Control flow: `run_node()` validates raftstore config for v1, builds background and PD workers, creates a `MultiRaftServer`, creates or reuses a `SnapManager`, constructs a coprocessor host and region info accessor, invokes the optional coprocessor hook, registers replica-read lock checking, creates an SST importer, local reader, config controller, split-check runner, and periodic disk-stat task, bootstraps the store, starts the node, asserts prepare-bootstrap metadata is consumed, registers raftstore config management, installs a `ServerRaftStoreRouter` wrapped in `SimulateTransport`, and records node maps. Async write/admin commands use `send_command`; reads use local-reader `read` with `ReadContext`.

State and persistence behavior: persistent state is in `Engines<RocksEngine, RaftTestEngine>`, snapshot temp dirs, import directories, and raftstore metadata in Rocks CFs. Snapshot copy is file-based and uses legacy `SnapManager` registration. The disk-stat background task periodically computes snapshot plus Rocks CF usage and updates global disk metrics, which can affect disk-full tests. Importers are stored per node for tests that ingest SSTs.

Dependencies and integration points: it integrates `MultiRaftServer`, raftstore fsm routers and local read router, `CoprocessorHost`, split-check runner/config manager, in-memory engine region info accessor, `SstImporter`, `HealthController`, resource metering test handles, TiKV config controller, `test_pd_client`, and legacy filters. It implements the `Simulator` trait from the legacy cluster file.

Risks and test signals: this simulator lacks the full gRPC storage layer, so client RPC and lock-manager tests need the server cluster. Snapshot manager registration/deregistration is a common failure point for snapshot tests. The periodic disk-stat task uses global disk metrics, so concurrent tests can be sensitive if isolation is weak. Missing routers are converted into callback errors for reads or immediate errors for commands. The prepare-bootstrap assertion and local-read callback completion are important startup/read sanity signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/router.rs -->
# sources/storage-engines/tikv/components/test_raftstore/src/router.rs

Purpose: this file defines `MockRaftStoreRouter`, a minimal region-scoped router for tests that need to observe peer messages without running a full raftstore.

Important APIs, types, and functions: `MockRaftStoreRouter` stores a `HashMap<u64, LooseBoundedSender<PeerMsg<RocksEngine>>>` behind `Arc<Mutex<_>>`. `new()` creates an empty router. `add_region(region_id, cap)` creates a loose-bounded channel for a region, registers its sender, and returns the receiver to the test. It implements `CasualRouter<RocksEngine>` by wrapping `CasualMessage` in `PeerMsg::CasualMessage` and `try_send`ing it. It implements `SignificantRouter<RocksEngine>` by wrapping `SignificantMsg` in `PeerMsg::SignificantMsg` and force-sending it.

Control flow: tests register a region, exercise code that sends casual or significant messages, then read the returned receiver to assert message content/order. If a region is not registered, send methods return `RegionNotFound` through raftstore error types and log significant-send failures.

State and persistence behavior: no persisted state. The only state is the in-memory map of region senders.

Dependencies and integration points: it implements selected raftstore router traits for `RocksEngine`/`RocksSnapshot`, making it usable anywhere a casual or significant router is sufficient. `StoreRouter`, `ProposalRouter`, and `RaftStoreRouter::send_raft_msg` are present but unimplemented, explicitly limiting the mock's scope.

Risks and test signals: this mock is intentionally partial. Code paths that send store messages, proposals, or raft messages will panic if routed through it. It is best suited for unit tests of casual/significant peer messages. Channel capacity and `try_send` behavior can be used to test backpressure/error handling, while `force_send` for significant messages bypasses normal capacity failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/test_raftstore/src/router.rs -->
