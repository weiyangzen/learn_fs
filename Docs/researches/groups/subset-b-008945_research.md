# Research Group subset-b-008945

This grouped report covers TiKV failpoint tests under `sources/storage-engines/tikv/tests/failpoints/cases/`. Each section is source-tree-aligned and bounded by markers for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_in_memory_engine.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_in_memory_engine.rs

## Purpose
This file is a regression suite for TiKV's hybrid in-memory region cache engine. It verifies that cached regions can be loaded, read by coprocessor point queries, updated by apply write batches, evicted or reloaded on topology changes, and kept consistent through split, merge, rollback, flashback, delete-range, SST ingest, leader transfer, and peer destruction events.

## Important APIs, Types, and Functions
- `copr_point_get`, `must_copr_point_get`, `must_copr_point_get_empty`, and `must_copr_load_data` build TiDB DAG requests against `ProductTable` data and assert whether reads observe rows through the coprocessor path.
- `async_put` starts data loading in a separate thread and is used to create deterministic races with apply and cache-load failpoints.
- `RegionCacheEngine`, `RegionCacheEngineExt`, `CacheRegion`, `EvictReason`, and `DATA_CFS` are the main cache-engine contracts under test.
- `new_server_cluster_with_hybrid_engine`, `configure_for_merge`, `new_region`, `new_peer`, `new_learner_peer`, and `Callback` are the raftstore test harness integration points.
- The tests use many IME-specific failpoints, including `ime_on_snapshot_load_finished`, `ime_on_iterator_seek`, `ime_on_region_cache_write_batch_write_impl`, `ime_on_load_region`, `ime_background_check_load_pending_interval`, `ime_fail_to_schedule_load`, and `on_apply_in_memory_engine_load_region`.

## Control Flow
The file starts with helper routines that translate table rows into coprocessor reads and writes. The tests then move through cache lifecycle scenarios: manual cache region registration, explicit `load_region`, snapshot-load completion, cached iterator verification, split-time range correction, write-batch races, cache eviction, and reload. Later tests drive merge and rollback events, leader transfers with warmup, SST ingestion, flashback, delete ranges, apply-fsm change handling, and peer destroy messages. Most tests follow the same pattern: build a small cluster, configure raftstore/apply concurrency, inject a failpoint to pause a narrow stage, mutate region state, then assert cache hit/miss behavior through `snapshot`, `region_cached`, or coprocessor iterator failpoint signals.

## State and Persistence Behavior
The suite validates that cached metadata tracks region id, epoch version, range boundaries, safe points, and manual load ranges. Split tests prove pending snapshot loads are narrowed to real post-split regions and do not wrongly cache the old super-range. Merge and rollback tests verify cached source/target regions are evicted or reloaded after epoch changes. SST ingest, delete range, unsafe destroy range, flashback, and peer tombstone paths must invalidate cached data so stale in-memory snapshots are not served. Warmup tests check that leader transfer can block until cache warmup finishes but eventually proceeds on timeout. Destroy-uninitialized-peer tests ensure cache observers tolerate peers without initialized region state.

## Dependencies and Integration Points
The file depends on Rocks SST writer/importer APIs, `engine_traits` cache abstractions, `in_memory_engine::test_util`, TiKV raftstore cluster utilities, PD client region management, coprocessor DAG helpers, and TiDB datum encoding. It integrates cache-engine behavior with raft apply tasks, raft command callbacks, import SST commands, GC worker unsafe destroy range, flashback admin commands, and raft message routing.

## Risks and Test Signals
The main risks are stale cached reads after region epoch changes, missing eviction after destructive operations, deadlocks or permanent stalls during warmup, and panics from uninitialized peer lifecycle events. Positive test signals include receiving `ime_on_iterator_seek` when reads should hit IME, `snapshot(...).is_err()` after eviction, successful `eventually` checks after reload, and row absence after delete/flashback. Several tests are race-sensitive and use sleeps, sync channels, and apply failpoints; failures often indicate subtle ordering bugs rather than simple data-path errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_in_memory_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_kv_service.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_kv_service.rs

## Purpose
This file tests KV service failpoint behavior around snapshot errors, gRPC responsiveness, stale reads, transaction status cache correctness, in-memory pessimistic locks, and duplicate-key diagnostics.

## Important APIs, Types, and Functions
- Test cases are parameterized across raftstore v1 and v2 where behavior is shared via `test_case`.
- `must_new_cluster_and_kv_client`, `must_new_cluster_mul`, `new_server_cluster`, and `configure_for_lease_read` build service-facing clusters and clients.
- KV RPC types include `BatchGetRequest`, `ScanRequest`, `GetRequest`, `PrewriteRequest`, `CommitRequest`, `ScanLockRequest`, and `TikvClient`.
- `must_kv_prewrite`, `must_kv_commit`, `must_kv_pessimistic_lock`, `try_kv_prewrite_with`, and `must_kv_have_locks` drive transactional storage behavior.

## Control Flow
The first two tests inject `raftkv_async_snapshot_err` and assert batch-get and scan return the compatibility error both per item and at top-level response. `test_snapshot_not_block_grpc` pauses snapshot acquisition after one successful write and proves a second RPC does not trip keepalive timeout. `test_undetermined_write_err` injects `applied_cb_return_undetermined_err`, expects a cancelled RPC failure, and then verifies the cluster panic is still captured on drop. Stale-read and status-cache tests build one-node clusters, create locks or write errors, then verify fallback and cache-hit/miss behavior. The scan-lock test stages in-memory pessimistic locks, starts a leader transfer failpoint after proposing locks, then confirms scans do not return duplicate locks from memory and storage. The ignored duplicate-key test exercises scheduler duplicate-key checks.

## State and Persistence Behavior
The tests distinguish memory locks from persisted lock CF entries, ensuring scan-lock merges both sources without duplicates. Transaction status cache is allowed to cache successful writes but must not be updated by region-error write failures. Stale read on a local leader should fall back to a safe read path when a lock at a later timestamp exists. The gRPC test targets runtime scheduling state rather than RocksDB persistence.

## Dependencies and Integration Points
This suite integrates storage RPC handlers with raftstore snapshots, lease-read configuration, pessimistic lock memory tables, lock CF reads through `engine_traits::Peekable`, and TiKV gRPC clients. Failpoints such as `after-snapshot`, `raftkv_early_error_report`, `finish_proposing_transfer_cmd_after_proposing_locks`, and `scheduler_dup_key_check` isolate service/raftstore boundaries.

## Risks and Test Signals
Risks include returning errors in only one legacy response field, gRPC keepalive watchdog false positives, stale reads incorrectly surfacing locks, transaction status cache pollution after failed writes, and duplicate lock reporting during leader transfer. Test signals are explicit response fields, CF lock absence/presence checks, panic failpoints for impossible cache paths, and lock-count assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_kv_service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_life.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_life.rs

## Purpose
This small raftstore-v2-only test verifies peer GC behavior when a store has been tombstoned or stopped during peer removal.

## Important APIs, Types, and Functions
- `test_gc_peer_on_tombstone_store` is parameterized with `test_raftstore_v2::new_server_cluster`.
- It uses `configure_for_merge`, `gc_peer_check_interval`, `disable_default_operator`, `must_remove_peer`, `stop_node`, and `must_empty_region_removed_records`.
- `mock_store_refresh_interval_secs` forces immediate invalidation of store address cache.

## Control Flow
The test creates a three-store server cluster, writes data, transfers leadership to store 1, isolates store 3, and removes store 3's peer from the region. It then invalidates the store address cache, stops node 3, clears send filters, waits several GC peer intervals, and asserts removed-region records are empty.

## State and Persistence Behavior
The state under observation is raftstore's region removed-record bookkeeping for a peer on a stopped/tombstone store. The expected behavior is that GC does not keep stale removed-records or require a live address for the tombstoned store.

## Dependencies and Integration Points
The test integrates PD peer removal, raftstore GC peer ticks, store address cache refresh, isolation filters, and server-cluster shutdown behavior.

## Risks and Test Signals
The primary risk is leaked or stuck removed-region metadata after store tombstone handling. The final `must_empty_region_removed_records` assertion is the test signal; timing depends on the configured 500 ms GC interval.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_life.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_local_read.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_local_read.rs

## Purpose
This file verifies local-reader consistency when a lease-read request has already passed lease validation but the peer is then removed and its local range is cleaned before the async response is returned.

## Important APIs, Types, and Functions
- `test_consistency_after_lease_pass` uses raw KV requests through `TikvClient`.
- `localreader_before_redirect` proves the request is served by local reader.
- `after_pass_lease_check` pauses after lease validation, and `apply_snap_cleanup_range` pauses snapshot cleanup.
- `must_raw_put`, `must_raw_get`, `must_get_equal`, `must_get_none`, and PD peer add/remove helpers are the core harness calls.

## Control Flow
The test starts a three-store cluster, transfers leadership to store 1, writes `key1`, and verifies a local lease read. It then pauses immediately after lease check and sends an async raw-get. While the request is paused, it transfers leadership away, removes the old peer, adds a replacement peer with snapshot cleanup paused, waits until old data is deleted locally, resumes the read, and asserts the paused request still returns the original value.

## State and Persistence Behavior
The important state is the snapshot acquired after passing lease validation. Even if the range is later cleaned from the engine due to peer removal and replacement snapshot application, the read must remain backed by the already-acquired snapshot and return consistent data.

## Dependencies and Integration Points
The test spans local reader lease validation, raw KV RPC, PD conf change, peer removal, snapshot application cleanup, and raftstore storage snapshots.

## Risks and Test Signals
The risk is a time-of-check/time-of-use bug where local reader validates lease before snapshot acquisition or lets cleanup invalidate the read. Signals are `must_get_none` after cleanup and the async raw-get returning `value1` after resume.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_local_read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_memory_usage_limit.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_memory_usage_limit.rs

## Purpose
This file validates raftstore behavior when memory usage crosses high-water limits: committed entries still apply, entry cache can be evicted aggressively, and raft append rejection/unreachable behavior is controlled by memory pressure.

## Important APIs, Types, and Functions
- `test_memory_usage_reaches_high_water`, `test_evict_entry_cache`, `test_memory_full_cause_of_raft_message`, and `test_evict_early_avoids_reject` are the main tests.
- `MEMTRACE_ENTRY_CACHE` is used as a memory accounting signal.
- Helper functions `setup_server_cluster`, `put_n_entries`, `add_message_filter`, `add_filter_append_and_unreachable`, and `wait_msg_counter` set up learners and count raft messages.
- Failpoints include `memory_usage_reaches_high_water`, `needs_evict_entry_cache`, `needs_reject_raft_append`, `mock_memory_usage`, `mock_memory_usage_high_water`, and `mock_memory_usage_entry_cache`.

## Control Flow
The first test forces high-water state and ensures repeated puts still apply. The entry-cache eviction test blocks normal log GC cleanup on one store, grows the cache with large values, then enables high-water and eviction failpoints and confirms cache size drops despite long lifetime. The message rejection test adds a learner, counts `MsgAppend` and `MsgUnreachable`, forces append rejection, and expects both counters to rise. The final test first disables eviction to grow cache, then simulates near-high-water memory so early eviction prevents `MsgUnreachable`.

## State and Persistence Behavior
The tests separate committed data persistence from volatile raft entry cache accounting. High memory should not prevent committed writes from being applied, but it should evict cache before rejecting append messages when possible. Learner replication state is used to observe rejection behavior through raft messages rather than persisted data only.

## Dependencies and Integration Points
The suite integrates raftstore memory tracing, raft log GC ticks, entry cache eviction ticks, learner replication, `RegionPacketFilter` message callbacks, and memory failpoint instrumentation.

## Risks and Test Signals
Risks include data apply starvation under memory pressure, entry cache not shrinking, premature append rejection, or missing unreachable responses. Signals are successful `must_get_equal`, `MEMTRACE_ENTRY_CACHE.sum()` thresholds, and message counter assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_memory_usage_limit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_merge.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_merge.rs

## Purpose
This is the central failpoint regression suite for raftstore region merge. It validates prepare/commit/rollback merge correctness across raftstore v1 and v2, restarts, snapshots, log compaction, leader transfer, pessimistic locks, timestamp synchronization, source-peer destruction, read delegates, and atomic snapshot races.

## Important APIs, Types, and Functions
- Tests use `configure_for_merge`, `must_split`, `must_try_merge`, `pd_client.must_merge`, `merge_region`, `check_merged_timeout`, `region_local_state`, `truncated_state`, `raft_local_state`, and direct raft command construction.
- Important state types include `RegionLocalState`, `PeerState`, `RaftMessage`, `PessimisticLock`, `LastChange`, `LocksStatus`, `ReadDelegate`, and raftstore/v2 `PeerMsg` and `PeerTick`.
- Custom filters `MsgTimeoutFilter` and `MsgVoteFilter` intercept leader-transfer and election traffic.
- Failpoints cover scheduling, applying, persistence, compact log, snapshot handling, lock proposal, disk-full, destroy-peer, and commit/rollback race boundaries.

## Control Flow
The file progresses from basic rollback and restart scenarios to increasingly specific historical regressions. Early tests verify rollback after target epoch changes and restart recovery from `Merging` state. Catch-up-log tests isolate peers, compact raft logs, and ensure lagging peers either recover by logs or snapshot. Snapshot tests deliver pre-merge and post-merge snapshots together or apart. Later tests stress compact-log interactions after prepare merge, failed-then-successful merges to the same target, leader transfer during commit, cascading merge with apply yield, majority rollback rules, and protection against writes to source after merge. The final group covers snapshot atomicity, timestamp max-ts synchronization, source read delegate lifecycle, pessimistic-lock proposal ordering, source peer destruction while merging, deterministic commit-vs-rollback behavior, lost merging state on restart, atomic snapshot destroy races, raft-log GC after merge, and apply-ahead-of-persist recovery.

## State and Persistence Behavior
The suite inspects persisted raft CF region state to distinguish `Normal`, `Merging`, `Tombstone`, and `Applying`. It verifies epoch version/conf-ver changes after split, prepare merge, rollback, conf change, and commit merge. Several tests stop nodes with unpersisted raft logs or applied-but-not-persisted indexes to ensure recovery does not lose merge state or compact required entries. Snapshot tests ensure source-peer destruction and target snapshot application are atomic enough to survive crash and restart. Pessimistic-lock tests validate `LocksStatus` transitions and that in-memory locks are proposed or rejected at correct merge stages. Timestamp tests protect raw/txn writes until max timestamp is synced after merge.

## Dependencies and Integration Points
The file integrates PD operators, raftstore peer FSMs, apply FSMs, raft log engine reads, Rocks CF reads, gRPC KV client prewrite/lock RPCs, concurrency manager locks, raftstore v2 router ticks, packet filters, and storage snapshots. It is a heavy cross-layer suite touching scheduling, persistence, transaction lock memory, leader transfer, and region metadata.

## Risks and Test Signals
Risks include data loss from rollback after commit, stale merge state after restart, compacted logs needed by commit merge, panic from missing source peers, accepting stale writes to source regions, incorrect pessimistic lock status, non-deterministic commit/rollback, and read delegate removal too early. Test signals include persisted `PeerState`, PD merged checks, successful puts after recovery, absence/presence of keys on isolated stores, lock status assertions, response error checks, and failpoint callbacks at exact state-machine boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_merge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_metrics_overflow.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_metrics_overflow.rs

## Purpose
This file tests a narrow memory-metrics overflow path for raft messages to ensure overflow checking does not incorrectly panic in peer receive accounting.

## Important APIs, Types, and Functions
- `test_memory_metrics_overflow` builds a three-node server cluster.
- It sets `store_batch_system.pool_size = 1` to make store disk usage/memory information available on the target thread.
- Failpoints `memtrace_raft_messages_overflow_check_send` and `memtrace_raft_messages_overflow_check_peer_recv` control the overflow path.

## Control Flow
The test starts the cluster, pauses the send-side overflow check briefly, sets the peer-receive overflow check to panic, then performs a put and get. If the receive-side overflow path were incorrectly reached, the test would panic.

## State and Persistence Behavior
The persisted state is minimal: a single key is written and read to force raft message traffic. The focus is volatile memory metric accounting and overflow guard behavior.

## Dependencies and Integration Points
This test integrates raftstore message flow, memory tracing failpoints, and basic cluster put/get paths.

## Risks and Test Signals
The risk is an overflow accounting bug that triggers peer-receive panic or corrupts memory metrics under delayed send accounting. The signal is successful `must_put` and `must_get` with the panic failpoint enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_metrics_overflow.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client.rs

## Purpose
This file tests the v2 PD RPC client under reconnect pauses, shared gRPC environment contention, request timeout/backoff, retry behavior, and service GC safe point monotonicity.

## Important APIs, Types, and Functions
- `new_test_server_and_client` creates a mock PD server and `RpcClientV2`.
- The `request!` macro wraps both sync and async PD client methods for deadlock testing.
- `run_on_bad_connection` resets the client to a lame connection and forces reconnect behavior.
- Main APIs under test include `reconnect`, `fetch_cluster_id`, bootstrap/store/region/split/heartbeat/scatter/operator methods, `get_gc_safe_point`, `get_store_and_stats`, and `update_service_safe_point`.

## Control Flow
`test_pd_client_deadlock` pauses `pd_client_reconnect`, then invokes each public client method from a spawned thread and ensures it completes once reconnect resumes. `test_slow_periodical_update` creates two clients sharing one gRPC environment and proves a paused periodical leader update in one client does not block `alloc_id` in another. `test_backoff` simulates short timeouts and longer backoff so the second bad request hits backoff and later succeeds. `test_retry` disables backoff and verifies retry success across many PD methods. `test_update_service_gc_safe_point` updates, rejects unsafe regressions, clears, and updates service safe points.

## State and Persistence Behavior
The client state under test includes leader connection state, initialized/lame connection status, reconnect backoff timers, timeout handling, and in-memory service safe point minimum tracking from mock PD responses. There is no TiKV storage persistence in this file.

## Dependencies and Integration Points
The file uses `test_pd` mock server/service, `grpcio::EnvBuilder`, `SecurityManager`, futures `block_on`, PD proto request/response types, and `TimeStamp`.

## Risks and Test Signals
Risks include client-wide deadlocks during reconnect, shared gRPC CQ starvation, retry loops that do not recover, excessive reconnect attempts, and accepting lower service GC safe points. Signals are `recv_timeout` completion, expected `unwrap_err` on bad connection, later `unwrap` success, and exact `UnsafeServiceGcSafePoint` fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client_legacy.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client_legacy.rs

## Purpose
This file provides equivalent failpoint coverage for the legacy `RpcClient`, focusing on reconnect deadlocks, slow periodical PD leader updates, and reconnect rate limiting.

## Important APIs, Types, and Functions
- `new_test_server_and_client` constructs a mock PD server and legacy client.
- The `request!` macro wraps legacy `PdClient` APIs including async region info, region heartbeat, split, store heartbeat, GC safe point, store stats, operator, and TSO calls.
- `handle_reconnect` is used in the deadlock test to force only one reconnect step per request.

## Control Flow
`test_pd_client_deadlock` wraps the client in `Arc`, pauses `pd_client_reconnect`, launches each PD method in a spawned thread, uses `handle_reconnect` to return from the reconnect failpoint once, removes the pause, and expects method completion within 500 ms. `test_slow_periodical_update` mirrors the v2 test with two clients sharing one gRPC environment. `test_reconnect_limit` waits beyond the default retry interval, allows one reconnect, then asserts subsequent reconnect calls are canceled by the speed limit.

## State and Persistence Behavior
The state is client-side reconnect scheduling, last-update tracking, and shared environment behavior. No raftstore or RocksDB state is created.

## Dependencies and Integration Points
The test uses `test_pd` mock server/service, legacy `RpcClient`, `PdClient`, `RegionInfo`, `RegionStat`, `grpcio::EnvBuilder`, and `SecurityManager`.

## Risks and Test Signals
Risks include legacy client methods blocking behind reconnect, one client's periodical update blocking another client's RPC, or reconnect storming. Signals are spawned-thread timeout checks and errors containing `cancel reconnection`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_pd_client_legacy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_pending_peers.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_pending_peers.rs

## Purpose
This file tests PD pending-peer and store-busy reporting when snapshot apply is delayed or fails, when raft/apply state races around truncated state, and when stores have peers busy applying logs.

## Important APIs, Types, and Functions
- Tests include `test_pending_peers`, `test_pending_snapshot`, `test_on_check_busy_on_apply_peers`, and `test_on_apply_snap_failed`.
- Important helpers include `configure_for_snapshot`, `configure_for_lease_read`, `get_pending_peers`, `get_store_stats`, `must_send_store_heartbeat`, and `apply_state`.
- Failpoints include `region_apply_snap`, `apply_on_handle_snapshot_*`, `on_handle_apply_1003`, `on_mock_store_completed_target_count`, and `region_apply_snap_io_err`.

## Control Flow
The first test delays snapshot apply for a newly added peer and checks PD reports it as pending until data is applied. `test_pending_snapshot` pauses snapshot handling, isolates a peer, compacts logs to force snapshot, and checks truncated state monotonicity despite concurrent raftstore/apply writes. The busy-store test creates lag on peer 1003, restarts it with apply paused, captures append/read-index messages to confirm committed indexes, then checks store heartbeat `is_busy` under incomplete apply progress and mocked target counts. The final test injects snapshot IO error, expects the new peer to remain pending, confirms data absence, and verifies damaged region reporting in store stats.

## State and Persistence Behavior
The file observes pending peer maps in mock PD, raft apply/truncated state, store heartbeat stats, and damaged region IDs. It ensures snapshot apply progress and failures are reflected in PD-visible metadata without corrupting raft apply state.

## Dependencies and Integration Points
The tests integrate PD heartbeat/reporting, snapshot generation/application, raft message filters, apply worker failpoints, store stats, and raftstore conf changes.

## Risks and Test Signals
Risks include premature removal from pending peers, dirty writes of truncated state, false-negative store busy reports, and missing damaged-region reporting after snapshot failure. Signals are pending-peer map contents, `applied_index` comparisons, `is_busy` assertions, data presence/absence, and `damaged_regions_id` checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_pending_peers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_rawkv.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_rawkv.rs

## Purpose
This file tests RawKV API v2 behavior with causal timestamps during leader transfer, region merge, and in-flight raw put key guards.

## Important APIs, Types, and Functions
- `TestSuite` wraps a `ServerCluster`, API version, context/client construction, raw put/get helpers, timestamp flushing, causal timestamp provider access, region merge, and leader-transfer checks.
- `FP_GET_TSO` (`test_raftstore_get_tso`) mocks TSO fetches to simulate stores with stale timestamp batches.
- Tests are `test_leader_transfer`, `test_region_merge`, and `test_raw_put_key_guard`.

## Control Flow
The leader-transfer test writes on store 1, flushes its timestamp, forces TSO fetch to return an older timestamp, transfers leadership to store 2, and expects raw puts to fail with `max_timestamp_not_synced` until timestamp sync succeeds. The merge test splits into three adjacent regions with leaders on different stores, writes/flushes on one source region, forces stale TSO during merge into another leader, verifies raw puts are rejected, then allows TSO and merges again with successful writes. The key-guard test pauses raw async write, waits for `global_min_lock_ts`, verifies it matches the raw put guard timestamp and that the key is invisible, then resumes and checks guard cleanup.

## State and Persistence Behavior
The suite tracks API v2 raw key/value state, causal timestamp provider batches, concurrency manager `global_min_lock_ts`, and merged-region boundaries. Raw writes must not persist when max timestamp is not synchronized; key guards must exist only while the write is in progress.

## Dependencies and Integration Points
It integrates causal timestamp providers, PD TSO, raw KV gRPC requests, region split/merge, leader transfer, concurrency manager lock state, and API-version-aware request contexts.

## Risks and Test Signals
Risks include accepting raw writes with stale timestamp after leader transfer or merge, corrupting causal ordering, or leaking key guards after raw writes. Signals are `max_timestamp_not_synced` region errors, stable raw-get values before allowed writes, merged range boundary assertions, and `global_min_lock_ts` equality/absence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_rawkv.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_read_execution_tracker.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_read_execution_tracker.rs

## Purpose
This file verifies that execution detail metrics distinguish lease reads from read-index reads for get, batch get, and coprocessor requests.

## Important APIs, Types, and Functions
- `test_read_execution_tracking` is parameterized across raftstore v1 and v2 cluster/client constructors.
- It uses `ScanDetailV2` fields: `read_index_propose_wait_nanos`, `read_index_confirm_wait_nanos`, and `read_pool_schedule_wait_nanos`.
- KV helpers `kv_read`, `kv_batch_read`, `must_kv_prewrite`, `must_kv_commit`, and coprocessor `DagSelect` drive three read surfaces.
- Failpoints `perform_read_local` and `perform_read_index` force the intended read path.

## Control Flow
The test configures lease reads with a very small pre-renew duration, writes and commits two keys, defines a checker that expects no read-index waits for lease reads, forces local read, and validates get, batch get, and coprocessor responses. It then removes the local-read failpoint, defines a checker expecting positive read-index propose/confirm waits, forces read-index twice per request path, and validates the same three read surfaces.

## State and Persistence Behavior
The persisted state is simple committed MVCC data for two keys and a ProductTable row. The primary state under test is response execution detail accounting for scheduling and read-index phases.

## Dependencies and Integration Points
The test integrates transactional KV writes, lease-read configuration, read pool scheduling, read-index handling, coprocessor DAG execution, and response `exec_details_v2` metrics.

## Risks and Test Signals
Risks include metrics missing read-index waits, incorrectly charging lease reads for read-index waits, or failing to populate read-pool scheduling wait. Signals are strict zero/non-zero assertions over `ScanDetailV2` for all three read request types.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_read_execution_tracker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_replica_read.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_replica_read.rs

## Purpose
This file is a failpoint suite for replica reads, read-index correctness, and read-index safe timestamp caching across follower lag, snapshot application, leader transfer, split, merge, destroyed peers, and lock checking.

## Important APIs, Types, and Functions
- Tests are parameterized across raftstore v1/v2 where supported; read-index-cache tests are mostly raftstore v1/server-cluster specific.
- Core helpers include `async_command_on_node`, `async_read_on_peer`, `async_read_index_on_peer`, `get_snapshot`, `get_region_read_index_safe_ts`, `make_cb_rocks`, and `block_on_timeout`.
- Important types include `Context`, `KeyRange`, `RegionLocalState`, `PeerState`, `RaftMessage`, `SnapContext`, `Snapshot`, `Lock`, and `TimeStamp`.
- Failpoints include `on_apply_write_cmd`, `before_handle_snapshot_ready_3`, `region_apply_snap`, `send_snapshot`, `apply_snap_cleanup_range`, `on_peer_collect_message_2`, `on_handle_apply_2`, `before_propose_readindex`, `skip_check_stale_read_safe`, and cache-path panic failpoints.

## Control Flow
Early tests prove follower reads wait for apply index, duplicate read-index contexts are not dropped, uninitialized peers reject reads, peers applying snapshots block or error correctly, and reads do not complete against a range cleaned for snapshot. Middle tests validate split learners know leaders quickly, read-index responses remain correct after transfer leader, batch read-index terms are current, and lock checking happens on the true leader or returns an error from false-leader situations. Later tests validate read-index safe-ts cache behavior: cache is not used while locks are present, destroyed peers do not return snapshots, split propagates safe-ts and lock checks to both child regions, merge resets safe-ts on the merged region, and leader transfer keeps safe-ts valid under new max-ts.

## State and Persistence Behavior
The suite observes raft apply index, raft log entries, region local state, read-index response terms/indexes, concurrency-manager locks, `read_index_safe_ts`, peer destruction, and snapshots. It ensures replica reads never bypass unapplied writes, uninitialized/applying peers, destroyed peers, stale ranges, or locks at/above the read timestamp. Split and merge tests ensure safe-ts metadata is reset or scoped to the correct region.

## Dependencies and Integration Points
It integrates raftstore lease-read configuration, PD peer management, raft message filters, snapshot cleanup/application, storage `async_snapshot`, concurrency manager lock checking, raft engine entry reads, and both raftstore v1/v2 read paths.

## Risks and Test Signals
Risks include stale follower reads, dropped duplicate read-index responses, invalid reads during snapshot cleanup, leader-transfer read-index term/index bugs, cache hits despite locks, safe-ts leakage across split/merge, and snapshots from destroyed peers. Signals are timeout-vs-success boundaries, explicit header errors, command type `Snap` or `Invalid`, lock-info equality, safe-ts values, and `region_not_found` errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_replica_read.rs -->
