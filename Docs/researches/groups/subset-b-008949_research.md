# subset-b-008949 research

Grouped research report for the TiKV integration-test sources in subset B. Each section preserves the original source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/test_sst_service.rs -->
# sources/storage-engines/tikv/tests/integrations/import/test_sst_service.rs

Purpose: exercises TiKV ImportSST gRPC service behavior end to end against one-node server clusters and raftstore-v2 clusters. It covers raw upload, WriteSST-generated SSTs, ingest/multi-ingest, download from external storage, mode switching, duplicate detection, suspend controls, TDE, cleanup, admission control, and force partition compaction.

Important APIs and functions: `assert_to_string_contains!` normalizes error assertions. `run_test_write_sst` builds txn key/value batches with `send_write_sst`, ingests returned metas with `must_ingest_sst`, and validates committed transactional KVs. `switch_mode` wraps `SwitchModeRequest`. Tests drive `ImportSstClient` methods including `upload`, `write`, `ingest`, `multi_ingest`, `download`, `switch_mode`, `duplicate_detect`, `suspend_import_rpc`, and `add_force_partition_range`. Helpers from `test_sst_importer` generate SST metadata/data and validate ingested ranges.

Control flow: most tests create a cluster/client through `super::util`, create or stream SST data, set region id/epoch from the current context, call the ImportSST RPC, and then validate either the service error or persisted data through `TikvClient`. Split/merge tests mutate PD region metadata and wait for cleanup. Concurrent ingest spawns threads sharing an import client to assert admission-control limits. Flash import mode tests split regions, change mode by key range, then compare ingest acceptance in import vs normal mode.

State and persistence: tests intentionally persist SST files under import directories and RocksDB DB paths, verify duplicate UUID/file detection, check that uploaded files disappear after split/merge or nonexistent-region cleanup, and confirm compaction can repartition SST files on disk. TDE tests use an encrypted security config. Resource-full paths manipulate global disk status and failpoints for memory usage/limit.

Dependencies and integration points: depends on `kvproto::import_sstpb`, TiKV config, `ImportSstClient`, `TikvClient`, PD client region APIs, failpoints, RocksDB ingest behavior, external local storage backends, disk-status hooks, and raftstore split/merge operations.

Risks: timing-sensitive cleanup and region bucket polling can be flaky under slow CI. Some error checks match string fragments. Global disk-status and failpoint state must be reset or later tests can be contaminated. `test_cleanup_sst_v2` appears to set `Range.start` twice where an end bound may have been intended, making that subcase worth reviewing.

Test signals: successful data reads through `check_ingested_kvs`, `check_ingested_txn_kvs`, CF-specific checks, import error variants (`DiskSpaceNotEnough`, `server_is_busy`, `region_not_found`), duplicate-detect pair counts, on-disk SST counts, and cleanup by failed re-upload checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/test_sst_service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/util.rs -->
# sources/storage-engines/tikv/tests/integrations/import/util.rs

Purpose: provides shared setup for ImportSST integration tests. It creates one-node TiKV server clusters, prepares a valid `kvrpcpb::Context`, and opens paired `TikvClient` and `ImportSstClient` gRPC clients.

Important APIs and functions: `new_cluster` and `new_cluster_v2` instantiate raftstore-v1 and raftstore-v2 server clusters, run them, discover leader/epoch for region 1, and return a request context. `open_cluster_and_tikv_import_client` and `_v2` apply default import-test config, create a gRPC channel with keepalive settings and optional TLS credentials, then construct both clients on the same channel. `new_cluster_and_tikv_import_client` is the default convenience wrapper. `new_cluster_and_tikv_import_client_tde` creates a temporary encryption config and returns the tempdir to keep key material alive for the cluster lifetime.

Control flow: caller-provided config is used as-is, otherwise defaults bind the server to `127.0.0.1:0`, reduce cleanup interval to 10 ms, set gRPC concurrency to one, and for v1 enable compaction guard on default/write CFs. Channel construction selects secure or insecure connect based on whether `cfg.security` is default.

State and persistence: cluster engines, import directories, and encrypted storage state are created by the test cluster harness. The returned `Context` carries region id, peer, and epoch, so later ingest calls can pass region validation. TDE setup persists key material in a temporary directory that must outlive the test.

Dependencies and integration points: integrates `test_raftstore`, `test_raftstore_v2`, `engine_rocks::RocksEngine`, `grpcio`, `security`, TiKV config, `HandyRwLock`, and generated kvproto clients.

Risks: the helpers assume a single initial region id of 1 and a one-node cluster, so tests needing split or multi-peer semantics must mutate the cluster afterward. Security comparison against `SecurityConfig::default()` determines TLS setup; partial security config changes must be valid.

Test signals: downstream tests signal setup correctness by successfully connecting to server address from the simulator registry, finding a leader peer, and making import/kv RPCs with the returned context.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/import/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/mod.rs -->
# sources/storage-engines/tikv/tests/integrations/mod.rs

Purpose: root module for TiKV integration tests. It enables nightly test features, selects TiKV's custom test runner, imports `tikv_util` macros, and wires all integration-test submodules into one crate.

Important APIs and declarations: crate attributes enable `test`, `box_patterns`, and `custom_test_frameworks`; `#![test_runner(test_util::run_tests)]` routes execution through the shared TiKV test harness. Module declarations include backup, config, coprocessor, import, pd, raftstore, resource metering, server, encryption, and storage areas.

Control flow: Rust's test discovery compiles this module tree, and each child module exposes its own `#[test]` or macro-generated tests. There is no runtime logic beyond module registration.

State and persistence: no local persistence. State is created by child modules through test clusters, temporary directories, RocksDB engines, mock PD servers, and failpoints.

Dependencies and integration points: acts as the integration point between Cargo's test crate and all TiKV integration domains. The custom runner is a key dependency because it controls test filtering, failpoint setup, logging, and thread handling.

Risks: adding or removing a `mod` declaration changes which integration tests compile and run. The nightly feature gates mean toolchain drift can break the whole integration test crate before any individual test executes.

Test signals: successful compilation and discovery of all child modules is the primary signal. Runtime pass/fail is delegated to the child files.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/pd/mod.rs -->
# sources/storage-engines/tikv/tests/integrations/pd/mod.rs

Purpose: registers PD client integration-test modules for both the current v2 RPC client and the legacy RPC client.

Important APIs and declarations: `mod test_rpc_client;` and `mod test_rpc_client_legacy;` include the two PD client suites.

Control flow: Rust test discovery compiles both modules under the integration-test crate. No executable code exists in this file.

State and persistence: none locally. Child modules create mock PD servers, gRPC clients, feature gates, and retry/reconnect state.

Dependencies and integration points: this file is the boundary between the root integration module and PD-specific test suites. It intentionally keeps v2 and legacy coverage side by side so behavior can be compared across APIs.

Risks: omitting either module would silently drop a large compatibility lane. Keeping both modules registered matters while legacy client behavior remains supported or tested.

Test signals: compile/test discovery for both PD suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/pd/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client.rs -->
# sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client.rs

Purpose: validates `pd_client::RpcClientV2` behavior against mock PD servers: connection retry, endpoint validation, forwarding, metadata APIs, TSO streaming, region/store heartbeats, leader changes, reconnect notifications, cluster version feature gates, and error mapping.

Important APIs and functions: `setup_runtime` creates a one-thread Tokio runtime for stream tests. `must_get_tso` uses `create_tso_stream` with `WakePolicy::Immediately`. Tests construct `MockServer` with mockers such as `Split`, `AlreadyBootstrapped`, `Incompatible`, and `LeaderChange`; instantiate clients with `new_client_v2`; and use `PdConnector::validate_endpoints`, `RpcClientV2::new`, `subscribe_reconnect`, `feature_gate`, `store_heartbeat`, `create_region_heartbeat_stream`, and region/store query methods.

Control flow: tests bind mock PD endpoints, create a v2 client, perform synchronous metadata calls or async stream operations under the runtime, then mutate mock server state or failpoints to force reconnect paths. Leader-change scenarios repeatedly issue harmless region queries until the client notices a new leader, then assert reconnect broadcasts and heartbeat stream recovery.

State and persistence: state lives in mock PD handlers: allocated IDs, stores, regions, tombstone store entries, leader member records, cluster version strings, and stream response queues. Client-side state includes cached cluster id, leader endpoint, feature gate version, reconnect broadcast channel, and heartbeat/TSO streams.

Dependencies and integration points: integrates `grpcio`, `kvproto::pdpb/metapb`, `pd_client::{PdClientV2, PdConnector, RpcClientV2}`, `security::SecurityManager`, `test_pd` mock server/mocker utilities, failpoints, Tokio, futures streams, and `txn_types::TimeStamp`.

Risks: stream tests are timing-sensitive and rely on fixed sleeps around default retry intervals. Error comparisons sometimes stringify gRPC errors. Failpoints such as `connect_leader`, `cluster_id_is_not_ready`, and `region_heartbeat_send_failed` must be removed. Mock behavior may not cover every production PD edge, especially with forwarding enabled.

Test signals: nonzero cluster id, monotonic ID allocation, correct tombstone filtering/error codes, expected `ClusterBootstrapped` and `Incompatible` errors, heartbeat responses after failures and leader changes, reconnect notifications, and monotonic feature-gate enabling as cluster versions advance but not regress.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client_legacy.rs -->
# sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client_legacy.rs

Purpose: validates the legacy `pd_client::RpcClient` API against the same mock PD surface as the v2 suite, preserving compatibility for older synchronous/future-based client methods and callback-style reconnect/heartbeat handling.

Important APIs and functions: tests use `new_client`, `new_client_with_update_interval`, `RpcClient::new`, `get_cluster_id`, `get_tso`, `batch_get_tso`, `handle_region_heartbeat_response`, `region_heartbeat`, `handle_reconnect`, sync/async region and store queries, and `update_service_safe_point`. Shared helper closures `test_retry` and `test_not_retry` assert retryable transport errors are retried while PD error-header responses are not.

Control flow: a mock PD server is started per scenario, the legacy client runs operations through blocking calls or futures driven by `futures::executor::block_on` and a small Tokio poller. Heartbeat tests spawn response handlers and heartbeat futures, then use channels for assertions. Retry tests install mockers that fail a configured fraction of requests. Leader-change tests count reconnect callbacks rather than reading a broadcast receiver.

State and persistence: mock PD state covers cluster bootstrap, stores/regions, tombstone state, leader endpoint, cluster version, and service GC safepoints. Client state includes cached leader, feature gate, reconnect callback list, and heartbeat response handlers.

Dependencies and integration points: uses `pd_client::{PdClient, RpcClient, PdConnector, RegionStat}`, `raftstore::store` constants, `grpcio`, `test_pd`, `security`, Tokio runtime builder, channels, atomics, and `txn_types::TimeStamp`.

Risks: legacy timing constants differ from v2, including sleeps for reconnect intervals. Callback/channel tests can be flaky if runtime scheduling stalls. Stringified gRPC status comparisons are brittle. Service safepoint assertions depend on mock PD faithfully implementing minimum safepoint semantics.

Test signals: successful bootstrap/query/TSO/heartbeat flow, expected retry and non-retry outcomes, callback invocation on leader change, feature-gate monotonicity, correct tombstone and incompatible-version errors, heartbeat recovery after failpoint removal, and `UnsafeServiceGcSafePoint` errors when lowering a service safepoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client_legacy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/mod.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/mod.rs

Purpose: registers the raftstore integration-test suite. The modules cover bootstrap, stale data cleanup, compaction, configuration change, early apply recovery, flashback, hibernation, joint consensus, lease reads, snapshots, transport, replication modes, stale peers, status commands, unsafe recovery, and more.

Important APIs and declarations: a long list of `mod test_*;` declarations includes the files researched in this work item and additional raftstore coverage.

Control flow: there is no runtime body. Rust test discovery includes each declared module, and macro-generated tests in those modules instantiate node/server clusters across raftstore v1/v2 variants.

State and persistence: none in this module. Child tests create all RocksDB, raft engine, PD, failpoint, transport, and snapshot state.

Dependencies and integration points: acts as the root integration point for `test_raftstore`, `test_raftstore_v2`, raftstore core, PD mock clients, engines, and TiKV server components.

Risks: declaration order can matter for compile errors and module visibility diagnostics, though tests should be independent. Removing a module from this file removes its coverage from the integration test crate.

Test signals: successful compilation and test discovery of the raftstore subtree.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_bootstrap.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_bootstrap.rs

Purpose: tests raftstore bootstrap idempotency, recovery from prepared bootstrap data, API-version switching constraints, and raftstore-v2 flush-before-stop persistence guarantees.

Important APIs and functions: `test_bootstrap_idempotent` starts/restarts clusters around `add_first_region`. `test_node_bootstrap_with_prepared_data` manually constructs a `MultiRaftServer`, RocksDB/raft engines, `SnapManager`, `CoprocessorHost`, `SstImporter`, and store metadata to verify `prepare_bootstrap_cluster` artifacts are cleaned during startup. API switching uses `TikvConfig.storage.set_api_version`. Flush tests send `PeerMsg::FlushBeforeClose` through raftstore-v2 routers and inspect raft engine flushed indexes.

Control flow: the prepared-data test bootstraps PD first, writes local prepare state, asserts prepare keys and region state exist, starts the node, and asserts those records are removed while PD still has one region. API-version tests run clusters with from/to combinations and distinguish TiDB-prefixed data from ordinary data. Flush tests write CF data across split regions, trigger flush-before-close through peer routers, and assert admin flushed indexes or bounded non-flushing with failpoints.

State and persistence: directly inspects `PREPARE_BOOTSTRAP_KEY`, region local state in `CF_RAFT`, RocksDB CF data, raft engine group flushed indexes, and persisted data after node restart. Failpoints control flush thresholds and completion.

Dependencies and integration points: integrates raftstore server bootstrap code, `MultiRaftServer`, engines, raftstore-v2 router messages, TiKV import service, coprocessor host, worker infrastructure, PD test client, and API-version metadata rules.

Risks: this file touches low-level startup internals and can break with bootstrap layout changes. Failpoint state must be cleaned. Flush-before-stop assertions depend on raftstore-v2 internals and CF last-modified/flushed-index accounting.

Test signals: region count remains one after repeated bootstrap, prepare records are absent after restart, invalid API-version switches fail only for non-TiDB data, flush indexes advance sufficiently, and data survives restart when write/lock CF flush ordering is tricky.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_bootstrap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_clear_stale_data.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_clear_stale_data.rs

Purpose: verifies stale peer data is physically removed from RocksDB when a node restarts after some regions have been removed from that store.

Important APIs and functions: `init_db_with_sst_files` writes one key per SST in `CF_DEFAULT` and `CF_LOCK`, flushes, and compacts files into a target level. `check_db_files_at_level` reads RocksDB `num-files-at-levelN` properties. `check_kv_in_all_cfs` validates key presence across default/lock CFs. `test_clear_stale_data` performs region splits, peer removals, restart, and assertions.

Control flow: the test disables level-0 compaction triggers, starts a three-node server cluster, splits the keyspace into six regions, manufactures level-6 SST files, removes peers for odd regions from a selected node through PD, restarts that node, and checks that odd-region keys and half the SST files are gone.

State and persistence: manipulates RocksDB SST layout directly and verifies both logical key deletion and physical file-count reduction. Peer state changes are persisted by raftstore and observed after node restart.

Dependencies and integration points: uses `engine_rocks`, `engine_traits` CF APIs, RocksDB raw compaction options/properties, PD peer removal, raftstore split/restart behavior, and test cluster engines.

Risks: file-count assertions are sensitive to RocksDB compaction behavior and configuration. The test disables compaction to stabilize layout, but engine version changes could alter property semantics. It covers default and lock CFs but not write/raft CF payload removal.

Test signals: keys for retained even regions remain present in both CFs, odd-region keys are absent, and level-6 file count drops from six to three in each checked CF after restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_clear_stale_data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_lock_cf.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_lock_cf.rs

Purpose: validates periodic lock CF compaction is triggered only after the configured byte threshold is exceeded.

Important APIs and functions: `flush` flushes `CF_LOCK` for all engines. `flush_then_check` sleeps for two configured intervals and inspects `DBStatisticsTickerType::CompactWriteBytes`. `test_compact_lock_cf` sets `lock_cf_compact_interval`, `lock_cf_compact_bytes_threshold`, disables lock CF auto compaction, writes lock CF keys, and verifies compaction statistics.

Control flow: after cluster startup, the test writes two small batches that remain below threshold and confirms no compact write bytes. A third batch crosses the threshold and the post-flush wait must observe compact write bytes.

State and persistence: data is written into lock CF and flushed into SSTs. The main observed state is RocksDB statistics counters, not final key values.

Dependencies and integration points: integrates raftstore config, RocksDB CF flush, RocksDB statistics, and the server cluster harness.

Risks: statistics counters can be affected by unrelated compactions if isolation breaks. Timing depends on the compaction interval and CI scheduling. The test uses a one-node server cluster, so it does not cover multi-peer coordination.

Test signals: `CompactWriteBytes` remains zero for sub-threshold flushed data and becomes nonzero after threshold-exceeding data is flushed and the periodic worker runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_lock_cf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_log.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_log.rs

Purpose: tests raft log garbage collection by entry count, repeated compaction, size limit, and reserve-max-ticks behavior.

Important APIs and functions: helper tests record each engine's `RaftApplyState.truncated_state` via `keys::apply_state_key(1)`, write many keys, and use `check_compacted` to compare before/after truncation. Config knobs include `raft_log_gc_count_limit`, `raft_log_gc_threshold`, `raft_log_gc_size_limit`, `raft_log_gc_tick_interval`, and `raft_log_reserve_max_ticks`.

Control flow: scenarios start node clusters, write an initial key to establish state, then write enough entries or bytes to cross a specific compaction criterion. Size-limit coverage stops one node to avoid checking lagging state. Reserve-max-ticks sets limits high enough that normal thresholds are not reached, then asserts tick-based reserve policy still compacts.

State and persistence: persisted raft apply state and truncated log index/term are the primary state. Key/value reads ensure writes are applied before compaction checks. Lagging or stopped nodes are intentionally excluded where appropriate.

Dependencies and integration points: uses raftstore log GC, raft apply state encoding, engine traits, `ReadableSize`/`ReadableDuration`, and `test_raftstore` compaction helpers.

Risks: timing sleeps can be flaky if log GC ticks are delayed. Compaction amount is implementation-dependent, so tests mainly compare state advancement, not exact indexes. Size-limit behavior depends on encoded raft log sizes.

Test signals: truncated state advances only after configured thresholds/ticks are reached, repeated compaction can advance at least twice the configured limit, and key reads continue to succeed after log GC.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_log.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_conf_change.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_conf_change.rs

Purpose: broad raftstore membership-change suite covering add/remove peers, learner promotion, PD-driven replica adjustment, split-brain prevention, safety checks under partial failure, leader transfer constraints, stale peer cleanup, snapshot-based learner catchup, and partition removal rules across raftstore v1/v2 node/server clusters.

Important APIs and functions: `call_conf_change!` builds admin conf-change requests with the current PD epoch. `new_conf_change_peer`, `wait_till_reach_count`, and `find_leader_response_header!` support repeated scenarios. Tests use PD helpers such as `must_add_peer`, `must_remove_peer`, `must_joint_confchange`, `must_none_peer`, `region_leader_must_be`, and direct cluster operations for isolation, partition, transfer leader, async remove, and snapshot filters.

Control flow: most tests start from a one-peer region via `run_conf_change`, disable PD default operators, add peers/learners, write keys to force replication or snapshots, then remove/promote/transfer under controlled network conditions. Safety tests stop or isolate leaders/followers to verify unsafe additions/removals are rejected. Slow snapshot tests install a custom filter that drops snapshot messages until pending-peer state is observed, then clears it and verifies promotion.

State and persistence: verifies engine key presence/absence after peer add/remove, PD region peer lists and pending peers, `RegionLocalState` tombstone after self-removal, leader records, stale peer data cleanup, and snapshot-applied data. Partition tests depend on persistent raft logs and peer metadata to prevent old configurations from serving.

Dependencies and integration points: integrates `test_pd_client`, raft admin commands, raft message filters, PD scheduling/operator behavior, learner role helpers, `test_raftstore_macro::test_case`, v1/v2 clusters, and RocksDB engine reads.

Risks: many tests rely on sleeps, polling, and simulated network filters. Default PD operator state must be explicitly controlled. Safety semantics are tightly coupled to raftstore policy, so legitimate policy changes may require updating expected error strings or peer-count behavior.

Test signals: replicated keys appear only on active peers, removed peers lose data or report region not found, duplicate peer operations return errors, unsafe conf changes are rejected while safe ones proceed, learner pending/promoted states transition correctly, stale peers self-destroy, and operations complete faster than heartbeat-only paths in the fast-conf-change test.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_conf_change.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_early_apply.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_early_apply.rs

Purpose: verifies TiKV can recover when apply state has advanced beyond raft log state after simulated raft engine data loss, including leader, follower, and all-node commit-index loss scenarios.

Important APIs and functions: `delete_old_data` scans raft entries, builds a `RaftLocalState` with the last index, and uses `RaftEngineDebug::clean` plus `consume` to remove old raft data. `DataLost` classifies which peers lose commit information. Generic `test` orchestrates packet filtering, action/check execution, raft engine snapshot/restore, node restart, and leader restoration. `test_early_apply` runs put, split, and remove-peer cases under the selected loss mode.

Control flow: a node cluster is configured to avoid automatic log compaction, transfer leadership based on loss mode, and write initial data. For each action, append responses are filtered so selected peers have mismatched raft/apply progress. The test captures raft engine data, verifies the action applied, stops selected nodes, deletes old raft data, restores captured batches, restarts nodes, and then requires the cluster to keep serving.

State and persistence: directly mutates raft engine persisted entries and local state. It validates engine key data, split metadata, remove-peer cleanup, raft local last indexes, and internal apply index used by raft election/campaign logic.

Dependencies and integration points: uses raftstore store helpers, `RaftEngineDebug`, raft message filters, callbacks, snapshot/request configuration, and cluster restart paths.

Risks: intentionally corrupting raft persistence is fragile and tightly coupled to raft engine cleanup semantics. Filtered append responses and asynchronous actions can be timing-sensitive. The all-lost case models severe crash recovery but cannot cover every production disk-loss pattern.

Test signals: after restart, puts and splits remain applied, removed peers are cleaned where expected, leaders can be transferred back, read requests succeed after re-commit, and a later write can commit after internal apply index repair.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_early_apply.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_flashback.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_flashback.rs

Purpose: tests raftstore flashback mode semantics across v1/v2 clusters: pessimistic lock handling, read/write gating, scheduling blocks, split/conf-change races, local reads, persisted flashback metadata, snapshot propagation, and helper request behavior.

Important APIs and functions: `eventually_meet` polls async lock-state changes. `ClusterI` abstracts node-cluster and raftstore-v2 cluster methods. `must_check_flashback_state`, `request`, `must_request_with_flashback_flag`, `must_request_without_flashback_flag`, and error assertion helpers centralize command construction and flashback flag handling. Tests use `AdminCmdType::PrepareFlashback` and `FinishFlashback`, `WriteBatchFlags::FLASHBACK`, and `SnapContext { allowed_in_flashback: true }`.

Control flow: tests create clusters, transfer a known leader, optionally pause apply with failpoints, send flashback admin commands, and then issue read/write/status/schedule/split/conf-change/snapshot flows with or without the flashback flag. Snapshot tests isolate a peer before or during flashback to verify flashback state catches up when snapshots are applied.

State and persistence: checks in-memory pessimistic lock table status, `RegionLocalState.region.is_in_flashback`, raft local indexes for local-read side effects, command error headers, region epoch/peer metadata after split/conf-change, and follower state after snapshot catchup.

Dependencies and integration points: integrates raftstore flashback admin command handling, transaction lock memory extension, raft command flags, snapshot context, failpoints, region status commands, split/conf-change machinery, and both raftstore engines.

Risks: failpoint-gated race tests are sensitive to batching behavior. Local-read assertions depend on exact raft index increments. Flashback flag semantics are security-sensitive: accidental allowance of unflagged writes/reads during flashback would violate intended isolation.

Test signals: unflagged reads/writes fail with `flashback_in_progress` during prepared flashback, flagged requests succeed only when appropriate, unprepared flashback requests return `flashback_not_prepared`, scheduling operations are blocked, persisted flashback state toggles on prepare/finish, and isolated peers converge to correct state after snapshots.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_flashback.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_hibernate.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_hibernate.rs

Purpose: verifies hibernate-region behavior: proposals waking sleeping peers, learner/voter transitions, delayed transfer and split handling, mixed configuration/version gating, joint-state demotion recovery, quorum hibernation with down peers, and matched-peer quorum checks.

Important APIs and functions: `must_wait_until_hibernated` polls `unstable_entries_state` until `GroupState::Idle`. `make_cb`, `make_write_req`, and `CbReceivers` build proposed callbacks for low-level async command assertions. Tests rely heavily on `configure_for_hibernate`, raft message filters, `GroupState`, PD peer changes, and leader transfer.

Control flow: scenarios start hibernate-enabled clusters, force replication, wait for sleep using election-time-derived intervals, then inject proposals, reads, conf changes, splits, delayed transfer messages, or node restarts. Quorum tests stop voters/learners, wait for down-peer detection, and monitor outbound messages with callbacks to decide whether a leader stayed asleep or awake.

State and persistence: validates key replication after wakeup, PD peer roles, raft log truncation state, hibernated group state, down-peer detection, leader identity after demotion/recovery, and persisted data after learners catch up by log or snapshot.

Dependencies and integration points: integrates raftstore hibernate logic, raft message types (`MsgTransferLeader`, `MsgTimeoutNow`, append/heartbeat responses), PD version gates, joint consensus, snapshot/log compaction, node/server clusters, and callback-based proposal plumbing.

Risks: highly timing-sensitive because hibernation, leader election, down-peer detection, and max-peer-down durations are all time based. Message filters must be cleared carefully. Feature-gate behavior depends on PD cluster version strings. Several assertions monitor absence of sends, which can be susceptible to scheduler jitter.

Test signals: hibernated leaders do not send heartbeats while sleeping, proposals/read-index/conf-change wake and complete, learners catch up after restart or snapshot, leaders stay awake when peers do not support hibernate or matched quorum is insufficient, and leaders can still hibernate when a down voter/learner is safe under quorum rules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_hibernate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_joint_consensus.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_joint_consensus.rs

Purpose: tests raft joint consensus configuration changes, including multi-peer changes, entering/leaving joint state, serving requests while joint, peer replacement, invalid request rejection, restart persistence, and leader election while joint.

Important APIs and functions: `call_conf_change_v2`, `call_conf_change`, `leave_joint`, `change_peer`, `put_request`, and `must_has_peer` wrap raft admin commands and role assertions. Tests use PD helpers `must_joint_confchange`, `must_leave_joint`, and `is_in_joint`, along with raft `ConfChangeType` and peer roles including learner/demoting voter.

Control flow: tests create node clusters, disable default PD operators, run initial conf change, then apply joint changes with multiple add/remove/promote/demote operations. Request-in-joint tests isolate old or new configuration peers to assert both configurations need quorum. Invalid request tests submit malformed joint changes and expect specific errors. Restart tests stop/start the leader while joint, then ensure state persists.

State and persistence: verifies PD region peer roles, engine key presence/absence on stores, joint-state flags, leader peer roles, split/merge restrictions, and role state after leaving joint. Restart coverage ensures joint config survives node restart.

Dependencies and integration points: integrates raftstore joint consensus implementation, PD test client commands, raft admin command encoding, isolation filters, `block_on_timeout`, and direct engine key reads.

Risks: expected error substrings are policy-coupled. Joint consensus correctness depends on both old and new quorum semantics; tests cover representative but not exhaustive topology changes. Some helper requests hard-code peer ids matching store ids.

Test signals: multi-change requests replicate data to new peers and remove old peers, normal writes obey joint quorum, invalid changes return targeted errors, merge is rejected in joint state, joint state persists across restart, and both old/new configuration peers can become leaders when valid.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_joint_consensus.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_lease_read.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_lease_read.rs

Purpose: exhaustive lease-read and read-index correctness suite for raft leaders. It covers lease renewal by reads/writes, expired leases, transfer-leader unsafe periods, batch snapshot lease IDs, callback cleanup on destroyed regions, stale read-index protection, local read cache, leadership changes during read-index, automatic lease renewal, continuous local-read renewal, and restart during isolation.

Important APIs and functions: `test_renew_lease!` is the main shared scenario. Tests use `configure_for_lease_read`, `LeaseReadFilter`, `must_read_on_peer`, `must_error_read_on_peer`, `async_read_on_peer`, `batch_read_on_peer`, `make_cb_rocks`, `new_read_index_cmd`, raft message filters, `LeadingFilter`, and PD peer changes. `assert_le!` bounds read-index renewals during continuous reads.

Control flow: scenarios configure long or short election/lease intervals, force a peer to lead, issue local reads while the lease is valid, wait for expiration to require read-index, perform writes to renew lease, and install filters to simulate transfer, isolation, delayed heartbeat responses, or destroyed regions. Several tests use explicit channels/callbacks to observe pending read-index completion.

State and persistence: observed state includes raft local last index, apply index, read-index values, shared `RocksSnapshot` pointers for batched reads, engine key data, leader cache, peer replacement state, and error headers such as stale command or region not found.

Dependencies and integration points: integrates raft leader lease logic, local reader cache, read-index batching, raft transfer-leader flow, PD membership, callbacks, snapshot batching, raftstore v1/v2 cluster variants, and timing configuration.

Risks: extremely timing-sensitive; sleeps model lease expiration, election timeout, heartbeat intervals, and renewal ticks. Some tests are disabled for raftstore-v2 where batch get snapshot is unsupported. Correctness hinges on not batching read-index requests across writes or suspect-lease boundaries.

Test signals: local reads do not increase raft index under valid lease, expired or unsafe leases trigger read-index, callbacks finish with errors rather than deadlocking when regions are destroyed, stale read-index returns stale-command errors, read-index after write is at least applied index, and isolated old leaders cannot serve stale lease reads after restart/election.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_lease_read.rs -->
