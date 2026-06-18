# Research: subset-b-008842

This grouped report covers the requested raftstore-v2 worker/test files and raftstore crate support files. Each source file has its own marker-delimited section so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/store.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/store.rs

## Purpose
This file implements raftstore-v2 PD store-heartbeat handling on `Runner<EK, ER, T>`. It builds `pdpb::StoreStats`, filters and caps per-region hotspot read statistics, records disk/engine/query/slowness metadata, sends store heartbeats to PD, and applies selected PD heartbeat responses such as unsafe recovery plans and gRPC pause/resume control. It also supports fake store heartbeats when normal heartbeat scheduling is delayed by local slowness.

## Important APIs, Types, and Functions
- `StoreStat` is the runner-owned aggregate state for store heartbeat deltas. It tracks cumulative read bytes/keys/query counts, last reported counters, last report timestamp, local histograms for region read/write bytes/keys, and recorded CPU/read-IO/write-IO metrics.
- `hotspot_*_report_threshold()` centralize read hotspot thresholds for keys, bytes, query count, and CPU usage. The `mock_hotspot_threshold` failpoint can force threshold zero for tests.
- `PeerCmpReadStat` is a small ordering wrapper used with `TopN` to select peer stats by metric.
- `collect_report_read_peer_stats()` sends all peer stats when the candidate map is modest; otherwise it includes the top regions by read keys, read bytes, read query count, and unified-read CPU usage, with duplicate regions removed by map deletion.
- `get_read_query_num()` maps PD query stats to the read-query sum used for ranking.
- `Runner::handle_store_heartbeat()` is the core path. It computes deltas since `last_report_ts`, fills capacity/used/available, flushes local histograms, updates slowness, marks stopping state, calls `pd_client.store_heartbeat`, and asynchronously processes PD response actions.
- `Runner::handle_fake_store_heartbeat()` constructs a busy heartbeat with store id, region count, snapshot counts, and snapshot traffic gauges, then calls the normal heartbeat path with `is_fake_hb = true`.
- `Runner::is_store_heartbeat_delayed()` decides whether delayed heartbeat reporting should synthesize a fake heartbeat, bounded by `STORE_HEARTBEAT_DELAY_LIMIT`.
- `Runner::handle_inspect_latency()` forwards latency inspection to the store control router.
- `Runner::handle_update_store_infos()` refreshes store-level CPU and IO metric samples.
- `collect_engine_size()` reads disk capacity/used/available, with a testexport branch that resets global disk stat mocks from current path stats.

## Control Flow
Normal heartbeat collection walks `self.region_peers`, computes each peer's deltas from last store report counters, subtracts last query stats, converts accumulated CPU milliseconds to an interval percentage, clears orphan CPU records, and skips regions below all hotspot thresholds. Qualified regions become `pdpb::PeerStat` entries, then `collect_report_read_peer_stats()` caps the payload. Store-level stats are enriched with disk size, total read deltas, query deltas, CPU/IO samples, gRPC pause status, interval start, slowness metadata, and stopping state before being sent to PD.

The PD response future handles unsafe recovery first. Force-leader plans build a failed-store set and send `enter_force_leader` messages through an `UnsafeRecoveryRouter`. Other plans send create, destroy, and demote messages with an execute-plan syncer. Awaken regions are logged and ignored because raftstore-v2 has no hibernated regions. `control_grpc` responses call `GrpcServiceManager::pause` or `resume`.

Fake heartbeats reuse the normal heartbeat construction but deliberately do not advance `last_report_ts`, so a busy/slowness report does not make the node appear normally scheduled.

## State and Persistence Behavior
The file does not directly persist raft data. It mutates in-memory heartbeat accounting on the runner: last read counters, last query counts, last report timestamp, store metrics, and per-peer last store-report counters. It reports persistent storage capacity through global disk stats and PD `StoreStats`. It also triggers persistent recovery-related actions indirectly by routing unsafe recovery plans to raftstore control paths. Histogram flushing is important because metrics are local collectors.

## Dependencies and Integration Points
It integrates with `pd_client::PdClient` and `kvproto::pdpb` for store heartbeat RPCs, `raftstore::store` unsafe recovery syncers and snapshot metrics, `health_controller::LatencyInspector`, `tikv_util` disk/time/topn/query stats helpers, and raftstore-v2 `StoreMsg`/`UnsafeRecoveryRouter`. Failpoint hooks support hotspot threshold testing. PD heartbeat tests in this subset exercise the fake-heartbeat path.

## Risks and Edge Cases
- Hotspot filtering depends on unsigned deltas from monotonically increasing counters; any counter reset before the last-report fields are reset can underflow.
- Fake heartbeats intentionally leave `last_report_ts` unchanged; callers must avoid repeated fake reports outside the delay guard.
- Unsafe recovery response handling is asynchronous and logs send failures, so later recovery syncer behavior must handle partial routing failures.
- Top-N selection can report up to four dimensions of `HOTSPOT_REPORT_CAPACITY`, not a strict 1000 total, because each metric contributes independently.
- Disk stat mocking in testexport builds changes global disk metrics and can affect tests that share process state.

## Test Signals
`tests/failpoints/test_pd_heartbeat.rs` forces small tick intervals and slowness failpoints to validate fake store heartbeat behavior. `tests/integrations/test_pd_heartbeat.rs` validates normal store heartbeat stats, region leader reporting, and bucket reporting. The hotspot threshold failpoint indicates tests can force peer-stat emission when validating PD payloads elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/refresh_config.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/refresh_config.rs

## Purpose
This file provides the raftstore-v2 worker that applies online refresh-config tasks affecting runtime pools: raft batch-system poller threads, apply future-pool threads, and store writer threads. It converts `RefreshConfigTask` messages into bounded resizing operations without restarting the store.

## Important APIs, Types, and Functions
- `PoolController<N, C, H>` wraps a `BatchRouter` and `PoolState` for a batch-system pool. It owns the low-level increase/decrease operations for raft poller workers.
- `PoolController::decrease_by()` sends `FsmTypes::Empty` sentinel messages into the FSM sender, causing pollers to exit.
- `PoolController::increase_by()` builds new normal-priority handlers, creates `Poller` instances, preserves current thread-group properties, sets IO type to `ForegroundWrite`, and spawns named worker threads with `spawn_wrapper`.
- `Runner<EK, ER, H, T>` holds the logger, raft pool controller, `WriterContoller`, and apply `FuturePool`.
- `resize_raft_pool()`, `resize_apply_pool()`, and `resize_store_writers()` implement the three supported scaling surfaces.
- The `Runnable` implementation handles `RefreshConfigTask::ScalePool(BatchComponent::Store|Apply, size)` and `RefreshConfigTask::ScaleWriters(size)`, logging unsupported tasks.

## Control Flow
The worker receives a `RefreshConfigTask` from the background worker scheduler. Store-pool changes compare requested size with `expected_pool_size`, update the expectation, and either inject empty FSMs to shrink or spawn new pollers to grow. Apply-pool changes call `FuturePool::scale_pool_size()` and log when the requested size is clamped by configured thread-count limits. Store-writer changes update the expected writer size, then call `decrease_to` or `increase_to` on the underlying writer pool using cloned writer metadata.

## State and Persistence Behavior
This code changes only live process state. It mutates `PoolState.expected_pool_size`, `PoolState.id_base`, the `workers` vector, apply-pool runtime size, and writer-controller expected writer count. It does not persist configuration values; persistence and config distribution are upstream online-config concerns.

## Dependencies and Integration Points
It is built around `batch_system::{BatchRouter, PoolState, Poller, HandlerBuilder}`, `raftstore::store::{RefreshConfigTask, BatchComponent, WriterContoller}`, `StoreRouter`, and the raftstore-v2 `PeerFsm`/`StoreFsm` FSM types. It uses TiKV thread wrappers, thread names, IO type tagging, and `FuturePool` for apply scaling.

## Risks and Edge Cases
- Shrink requests rely on empty FSM sentinel delivery; a saturated or closed FSM channel logs an error and can leave the actual pool larger than expected.
- `increase_by()` unwraps thread spawning, so thread creation failure will panic.
- Apply-pool scaling may be clamped, but the method only logs the clamp and does not update the requested configuration.
- Store writer resizing relies on pollers refreshing cached writer handles later in `poller.begin()`, so there can be a temporary mismatch between expected and local cached writers.

## Test Signals
No direct tests are in this file. Integration coverage is indirect through raftstore-v2 tests that start systems, dispatch writes/admin commands, and rely on working raft/apply/store writer pools. The explicit warning logs for unsupported tasks are a signal that tests should assert only supported `RefreshConfigTask` variants if this worker is isolated later.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/refresh_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/tablet.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/tablet.rs

## Purpose
This file implements the raftstore-v2 tablet background worker. It performs time-consuming or destructive tablet maintenance outside the main raftstore FSM path: trimming data outside a region range, staged and direct tablet destruction, imported SST cleanup, memtable flushes, range deletes, and snapshot GC. It also retries destroy operations that are blocked by open RocksDB locks.

## Important APIs, Types, and Functions
- `Task<EK>` is the worker command enum. Variants include `Trim`, `PrepareDestroy`, `Destroy`, `DirectDestroy`, `CleanupImportSst`, `Flush`, `DeleteRange`, and `SnapGc`.
- `Task` helper constructors build correctly shaped commands, including path-based destroy tasks for tablets that were never opened.
- `Display for Task` provides structured task logging with region ids, keys, priorities, flush thresholds, and snapshot keys.
- `Runner<EK>` owns the `TabletRegistry`, `SstImporter`, `TabletSnapManager`, logger, destroy queues, and two YATP future pools: `high_pri_pool` for urgent non-CPU waits and `low_pri_pool` for background work.
- `trim()` deletes data outside `[region.start, region.end)` with WAL disabled, then asynchronously compacts both outside ranges and validates `check_in_range`.
- `pause_background_work()` disables flush during shutdown for open tablets and asynchronously waits for background compactions to pause before returning the path.
- `prepare_destroy()`, `destroy()`, `direct_destroy()`, and `process_destroy_task()` implement staged path deletion, persisted-index gating, locked-path retry, and final factory destruction.
- `flush_tablet()` flushes `DATA_CFS`, optionally synchronously for leader-triggered callbacks and with a threshold to skip recent active memtables.
- `delete_range()` uses WAL-disabled `DeleteFiles` plus `DeleteByKey` for a CF range and reports whether anything was written.
- `RunnableWithTimer::on_timeout()` retries pending destroys every ten seconds.

## Control Flow
Task dispatch is a direct match in `Runnable::run`. Trim tasks issue fast file-range deletes, then compact and validate asynchronously before dropping the tablet and invoking the callback. Prepare-destroy pauses background work and queues `(path, wait_for_persisted, callback)` under the region id, deduplicating by path. Destroy tasks compare the persisted index against each queued wait point; eligible paths are destroyed immediately if unlocked or moved to `pending_destroy_tasks` for timer retry. Direct destroys skip the persisted-index queue and try the same destroy path immediately.

Flush tasks first resolve the latest tablet from the registry. Missing tablets log a warning and still invoke callbacks. Leader flushes with callbacks are run in a future pool with synchronous flush and callback after tablet drop. Followers flush directly and asynchronously at RocksDB level. Delete-range tasks panic on unexpected task shape and on RocksDB delete failures, reflecting that partial delete failure is considered fatal.

## State and Persistence Behavior
This file directly changes tablet RocksDB state. Trim and delete-range use WAL-disabled writes and file deletion strategies; correctness depends on raft apply trace and flushed-index persistence elsewhere. Flush persists memtables into SSTs. Destroy removes tablet directories only after registry locks are gone and, for staged destroys, after the persisted apply index reaches the requested wait point. Snapshot GC removes tablet snapshot files via `TabletSnapManager`. SST cleanup deletes importer files.

## Dependencies and Integration Points
Key dependencies include `engine_traits` tablet APIs, `TabletRegistry`, `TabletContext`, `DATA_CFS`, `DeleteStrategy`, `ManualCompactionOptions`, `WriteOptions`, `raftstore::store::{TabletSnapKey, TabletSnapManager}`, `sst_importer::SstImporter`, `keys` data key helpers, and TiKV YATP pools. Failpoint `tablet_trimmed_finished` lets tests synchronize trim completion. The worker is used by split, merge, life-cycle, apply, and snapshot paths.

## Risks and Edge Cases
- Destroy is intentionally best-effort when paths are locked; pending tasks can accumulate if registry references are leaked.
- `process_destroy_task()` treats missing paths as consumed, which is correct for idempotence but can hide unexpected external deletion.
- Trim validates range cleanup but logs and returns without callback if delete or compaction fails; callers must tolerate callback absence on failure.
- Delete-range currently does not delete Titan blobs and panics on engine errors.
- High-priority flush routing depends on low-priority running task count; starvation or pool saturation could delay leader callbacks.
- The code sets `avoid_flush_during_shutdown` before background-work pause to prevent destroy from being blocked by wasteful flushes.

## Test Signals
The in-file unit tests cover races between destroy and trim, destroy of locked tablets after registry removal, duplicate/missing destroy paths, and timer retry behavior. Failpoint and integration tests in this subset add coverage for split resume, merge replay, delete-range persistence, data recovery after restart, and tablet-index/flushed-index invariants.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/tablet.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/mod.rs

## Purpose
This is the failpoint test crate root for raftstore-v2. It enables nightly custom test framework support, selects `test_util::run_failpoint_tests` as the test runner, imports the shared integration `cluster` harness, and declares the failpoint test modules.

## Important APIs, Types, and Functions
There are no runtime APIs. The important declarations are `#![feature(test)]`, `#![feature(custom_test_frameworks)]`, `#![test_runner(test_util::run_failpoint_tests)]`, the path import of `../integrations/cluster.rs`, and module declarations for failpoint suites.

## Control Flow
Cargo compiles this test target with failpoints enabled. The custom runner executes the module tests under TiKV's failpoint-test harness, so failpoint state setup and teardown semantics are controlled by `test_util`.

## State and Persistence Behavior
This file has no direct state or persistence behavior. It shapes test execution and ensures failpoint tests share the same cluster helper as normal integrations.

## Dependencies and Integration Points
It integrates failpoint tests with the `cluster` module used by normal integration tests. This matters because failpoint cases exercise the same real raftstore-v2 system startup, tablet registry, PD client, and transport behavior as non-failpoint tests.

## Risks and Edge Cases
- Sharing `cluster.rs` through a path import means helper changes affect both integration and failpoint targets.
- The custom test runner is required; running these modules under a plain harness could leave failpoints unmanaged.

## Test Signals
The module list shows the intended failpoint coverage areas: basic write/apply, bootstrap, bucket refresh, peer life, merge, PD heartbeat, split, and trace apply.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_basic_write.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_basic_write.rs

## Purpose
This failpoint test file validates raftstore-v2 write apply robustness under injected apply failures and delete-range persistence corner cases. It focuses on write-batch rollback/isolation and ensuring delete-range commands do not break recovery or flushed-index advancement.

## Important APIs, Types, and Functions
- `test_write_batch_rollback()` pauses `APPLY_COMMITTED_ENTRIES`, injects `APPLY_PUT` failures, and checks that failed and successful simple writes in the same apply batch remain isolated.
- `test_delete_range()` writes data to default/write CFs, applies a default-CF delete range while suppressing apply-trace persistence, restarts, and verifies delete-range replay.
- `test_delete_range_does_not_block_flushed_index()` verifies that a file-level delete range against default CF does not prevent later flushed-index advancement for writes in another CF.
- The tests use `SimpleWriteEncoder`, `PeerMsg::simple_write`, `router.stale_snapshot`, RocksDB flush/compaction helpers, and raft-engine flushed-index reads.

## Control Flow
The write-batch test queues two committed writes while apply is paused, injects one failing put, resumes apply, and asserts only the failing command returns an aborted error and only its key is absent. It repeats the sequence to confirm rollback after an initialized batch. The delete-range tests force data into SSTs, apply range deletion, manipulate apply-trace failpoints, close/remove tablets, restart the cluster, and inspect snapshots and raft-engine flushed indexes.

## State and Persistence Behavior
The tests intentionally exercise WAL-disabled tablet writes, write-batch rollback, CF-specific flush state, apply-trace persistence, and raft-engine flushed-index records. They simulate crash/restart windows by disabling apply-trace persistence and forcing tablet registry removal before restart.

## Dependencies and Integration Points
They depend on the integration `Cluster`, raftstore-v2 router subscriptions for proposed/committed/result phases, `engine_traits` CF operations, manual compaction, and raft-engine read-only APIs. The failpoints target apply code paths outside this file.

## Risks and Edge Cases
- A stale write batch can leak failed mutations into later successful commands; this file is specifically guarding that.
- Delete-range by file can produce no memtable writes for empty CFs; flushed-index logic must not wait forever for nonexistent flush work.
- Restart recovery must replay delete-range commands even when apply trace was not persisted.

## Test Signals
Strong assertions include aborted error messages, key absence/presence across snapshots, WAL/tablet restart behavior, and monotonically advancing raft-engine flushed indexes after cross-CF writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_basic_write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bootstrap.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bootstrap.rs

## Purpose
This file tests raftstore-v2 bootstrap idempotence and recovery when failpoints abort startup at key points between store bootstrap, prepare-bootstrap-region persistence, and cluster bootstrap completion.

## Important APIs, Types, and Functions
- `test_bootstrap_half_way_failure()` constructs a `test_pd` server/client, temp engines, and a closure that calls `Bootstrap::bootstrap_store()` followed by `bootstrap_first_region()`.
- Failpoints `node_after_bootstrap_store`, `node_after_prepare_bootstrap_cluster`, and `node_after_bootstrap_cluster` inject aborts at successive bootstrap stages.
- It reads `get_store_ident()` and `get_prepare_bootstrap_region()` from the raft engine to verify persisted metadata.

## Control Flow
The test first aborts after store bootstrap and expects no prepared bootstrap region but a nonzero store id. It then removes that failpoint, aborts after prepare-bootstrap-cluster, and checks that a prepared region exists. It aborts after bootstrap-cluster and still expects prepared metadata. Finally it runs bootstrap without failpoints, expecting recovery to finish and clear the prepared region, then verifies a second bootstrap is a no-op.

## State and Persistence Behavior
The test centers on raft-engine bootstrap metadata: store ident and prepared bootstrap region. It validates that partially persisted bootstrap state is either safely absent or resumable, and that successful completion clears the prepare marker.

## Dependencies and Integration Points
It integrates `raftstore_v2::Bootstrap`, `test_pd`, `engine_test::new_temp_engine`, raft-engine read-only bootstrap metadata APIs, and `kvproto::metapb::Store`.

## Risks and Edge Cases
- Bootstrap must be idempotent across process crashes after any single persisted marker.
- Prepared bootstrap-region metadata must not be left behind after successful cluster bootstrap.
- A store id persisted before first-region bootstrap must be reused rather than reallocated.

## Test Signals
The test checks error strings include failpoint names, metadata presence/absence at each phase, final successful bootstrap result, and second-run no-op behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bootstrap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bucket.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bucket.rs

## Purpose
This failpoint test validates bucket refresh behavior during a split race where the new split peer's apply scheduler is delayed. It ensures bucket metadata sent immediately after split can still be installed once the peer storage path becomes ready.

## Important APIs, Types, and Functions
- `test_refresh_bucket()` uses `split_region_and_refresh_bucket()` from the shared cluster helper.
- It reads `RegionLocalState.tablet_index` from the raft engine and expects the initial region at `RAFT_INIT_LOG_INDEX`.
- Failpoint `delay_set_apply_scheduler` sleeps during apply-scheduler setup to widen the race.

## Control Flow
The test starts a default one-node cluster, fetches region 2 and its peer, waits for current-term apply, enables the scheduler-delay failpoint, splits region 2 at `k22`, immediately refreshes buckets for the new region 1000, then polls debug info until bucket keys appear.

## State and Persistence Behavior
It checks persisted raft-engine region state only for the pre-split tablet index. The key behavior is in-memory bucket metadata propagation across the delayed apply-scheduler installation, eventually visible through `RegionMeta.bucket_keys`.

## Dependencies and Integration Points
The test integrates split admin commands, store-router bucket refresh, raftstore bucket metadata, raft-engine state reads, and the peer debug-info query path.

## Risks and Edge Cases
- Bucket refresh can arrive before the split peer's scheduler/storage is fully initialized.
- Losing the refresh would leave `bucket_keys` empty despite PD/autosplit updates.
- The test polls with a timeout because the failpoint uses real sleep and async scheduling.

## Test Signals
Success is `bucket_keys.len() == 4`, including region start/end keys plus the two refreshed bucket boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_life.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_life.rs

## Purpose
This failpoint test covers peer replacement while the old peer is stuck applying entries. It verifies that a larger peer id heartbeat can destroy the old peer, create the new peer, and survive restart even when apply progress was paused.

## Important APIs, Types, and Functions
- `test_destroy_by_larger_id_while_applying()` pauses `APPLY_COMMITTED_ENTRIES`, submits a simple write, constructs a `RaftMessage` heartbeat for the same region with a larger target peer id and higher term, and sends it through `send_raft_message`.
- It uses `assert_peer_not_exist()` and `must_query_debug_info()` to validate destruction/recreation.

## Control Flow
After the initial region applies to current term, the test pauses apply, sends a write and waits for commit, then sends a heartbeat addressed to `current_peer_id + 1` with incremented conf version and term 10. Removing the failpoint lets the system complete destruction. The test confirms the old peer disappears, debug info shows the new peer id and term, restarts the node, and checks the new peer remains.

## State and Persistence Behavior
The test validates raft peer life-cycle persistence in the raft engine while apply was interrupted. It expects the replacement peer's raft hard state term and peer id to persist across restart.

## Dependencies and Integration Points
It depends on the shared cluster harness, router write and raft-message paths, failpoint-injected apply pause, and life helper assertions.

## Risks and Edge Cases
- Larger-peer-id replacement must not be blocked forever by an applying old peer.
- Destruction must not lose the incoming higher term/hard state for the replacement peer.
- Restart must not resurrect the old peer or roll back the replacement.

## Test Signals
Assertions check old peer nonexistence, new peer `raft_status.id`, hard-state term 10, and same state after restart.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_life.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_merge.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_merge.rs

## Purpose
This file stress-tests raftstore-v2 merge recovery and conflict handling under failpoint-controlled crash/race windows. It covers source/target replay after restart, early source destruction, rollback when target ranges change, and conflicts with concurrent or already-finished target merges.

## Important APIs, Types, and Functions
- `test_source_and_target_both_replay()` injects `after_acquire_source_checkpoint` to abort after checkpoint acquisition, restarts, and waits for source data to appear in target.
- `test_source_destroy_before_target_apply()` combines `force_send_catch_up_logs` and `after_acquire_source_checkpoint` so the source is destroyed before target apply, then validates replay after restart.
- `test_rollback()` triggers a split from inside `start_commit_merge` and expects the source region to roll back and remain writable.
- `test_merge_conflict_0()` pauses `apply_commit_merge` for target merge 2+3, starts merge 1+2, and waits for `apply_rollback_merge`.
- `test_merge_conflict_1()` blocks ask-target for merge 1+2, merges 2+3 first, then forces check-merge and expects rollback.

## Control Flow
All tests use split helpers to create adjacent regions, write range-marker keys, then call `merge_region()` with specific failpoints active. Recovery tests restart the cluster and poll stale snapshots. Conflict tests coordinate with failpoint callbacks and channels, then attempt writes to the original source region until success proves rollback completed. The first conflict test also waits for the third region to apply current term to avoid nested future-pool leakage noted in comments.

## State and Persistence Behavior
The tests validate merge checkpoints, source destruction markers, target apply state, region epoch/range state, and data replay into the merged target. They intentionally cross restart boundaries to prove checkpoint/replay data is durable enough even when source and target have partial progress.

## Dependencies and Integration Points
They depend on cluster split/merge/life helpers, router stale snapshots, `PeerTick::CheckMerge`, failpoint callbacks, raftstore-v2 merge apply code, and tablet checkpoint handling.

## Risks and Edge Cases
- Source checkpoint acquisition followed by crash must be replayable by both source and target.
- Source destruction before target apply must not orphan data or prevent target replay.
- Merge commit must detect target range changes and roll back rather than corrupt overlapping regions.
- Concurrent merge conflicts can otherwise leave regions unwritable or merged into destroyed targets.

## Test Signals
Signals include source key visible in target after restart, old source peer nonexistence, rollback failpoint callback receipt, and successful writes to non-merged source regions after conflict resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_merge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_pd_heartbeat.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_pd_heartbeat.rs

## Purpose
This test validates fake store-heartbeat reporting when normal heartbeat scheduling is perceived as delayed or blocked by slowness. It specifically targets `worker/pd/store.rs` fake heartbeat behavior.

## Important APIs, Types, and Functions
- `test_fake_store_heartbeat()` builds a cluster with very short PD store-heartbeat and inspect intervals.
- Failpoint `mock_collect_tick_interval` makes collection interval immediate; `mock_slowness_last_tick_unfinished` simulates unfinished slowness inspection.
- It sends `StoreMsg::Tick(StoreTick::PdStoreHeartbeat)` and reads PD store stats through `PdClient::get_store_stats_async`.

## Control Flow
The test sends an explicit store heartbeat and records PD stats, then enables the slowness failpoint and waits long enough for fake heartbeat logic to run. It fetches store stats again and checks capacity/used size. If PD reports `start_time == 0`, the stats are interpreted as a fake heartbeat and must be marked busy; otherwise normal heartbeat stats must not be busy.

## State and Persistence Behavior
No raft data is persisted. The observable state is PD's in-memory/test-server store stats. The test confirms fake heartbeat contents reuse real disk stats but do not report writes.

## Dependencies and Integration Points
It integrates the store control router tick path, PD client/test server, heartbeat intervals in store config, and slowness failpoints used by the raftstore-v2 inspect path.

## Risks and Edge Cases
- Fake heartbeat must report enough store identity/capacity data for PD to mark the store busy, not missing.
- Normal heartbeats and fake heartbeats can race; the test handles both by checking `start_time`.
- Failpoints are removed explicitly to avoid contaminating other failpoint tests.

## Test Signals
Expected signals are nonzero capacity and used size, zero keys written, and `is_busy` true only for fake heartbeat stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_pd_heartbeat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_split.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_split.rs

## Purpose
This failpoint test verifies split recovery when metadata is persisted before the new tablet is physically installed. It ensures restart resumes tablet installation and both resulting regions can serve writes with the correct epoch.

## Important APIs, Types, and Functions
- `test_restart_resume()` uses failpoint `async_write_before_cb` to stop async metadata write before callback completion.
- It uses `split_region()` to create region 1000 from region 2, then submits a write to force split initialization.
- It reads raft-engine `RegionLocalState.tablet_index` and the expected tablet path from `TabletRegistry`.

## Control Flow
The test activates the failpoint, splits region 2, submits a write to region 2 to ensure split init begins, and verifies raft metadata for region 1000 exists while its tablet path does not. After restart, the path must exist. The failpoint is then removed because replaying the split would otherwise block writes. The test loops until region epochs match, then writes to both resulting regions.

## State and Persistence Behavior
It validates durable raft-engine split metadata and deferred tablet-directory creation. It also checks replay after restart installs the missing tablet and updates source-region epoch.

## Dependencies and Integration Points
It uses split helper admin commands, raft-engine state APIs, tablet registry path conventions, router request construction, and simple write routing.

## Risks and Edge Cases
- Persisted split metadata without a tablet directory must be recoverable.
- Source peer replay may lag after restart, so tests wait for epoch convergence.
- Leaving the failpoint enabled would deadlock replay writes, which the test explicitly avoids.

## Test Signals
Assertions cover initial `RAFT_INIT_LOG_INDEX`, missing tablet path before restart, existing path after restart, matching region epoch, and successful writes to both regions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_split.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_trace_apply.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_trace_apply.rs

## Purpose
This file is a placeholder failpoint test module for trace-apply recovery scenarios. It currently contains TODO comments only.

## Important APIs, Types, and Functions
There are no APIs or tests. The TODO list names planned coverage: recovery when split has not started, split has not finished, two pending splits where the second finishes before the first, and all splits finished.

## Control Flow
No executable control flow is present.

## State and Persistence Behavior
No state is modified. The comments indicate intended future coverage for trace-apply state and split progress persistence.

## Dependencies and Integration Points
None currently. Future tests would likely use the shared cluster split and failpoint helpers.

## Risks and Edge Cases
The absence of tests here means trace-apply split sequencing still relies on other failpoint and integration tests, especially `test_split.rs` and `tests/integrations/test_trace_apply.rs`.

## Test Signals
No direct test signals exist yet.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_trace_apply.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/cluster.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/cluster.rs

## Purpose
This file is the shared raftstore-v2 integration-test harness. It builds in-process test clusters with real raftstore-v2 batch systems, raft engines, tablet registries, PD clients, snapshot managers, coprocessor hosts, importers, resource controllers, and a channel-backed transport. It also provides high-level helpers for writing, querying, splitting, merging, dispatching raft messages, and asserting peer life-cycle state.

## Important APIs, Types, and Functions
- `check_skip_wal()` asserts RocksDB WAL files exist but are empty, validating WAL-skipping behavior.
- `TestRouter` wraps `RaftRouter<KvTestEngine, RaftTestEngine>` and adds `query`, `simple_write`, `admin_command`, `wait_flush`, `wait_applied_to_current_term`, `new_request_for`, `stale_snapshot`, `region_detail`, and `refresh_bucket`.
- `RunningState` owns live store components and shuts down the system/background worker on drop.
- `TestNode` owns PD client, temp path, optional running state, logger, and resource manager; it can start, stop, restart, expose registry/PD client/state/id.
- `TestTransport` implements raftstore-v2 `Transport` with a channel and flush counter.
- `v2_default_config()` sets test defaults, while `disable_all_auto_ticks()` disables automatic ticks so tests can drive behavior manually.
- `Cluster` owns nodes, routers, receivers, and PD server; it supports single/multi-node construction, restart, node/receiver access, and `dispatch()` to route all pending raft messages including snapshot file handoff.
- `split_helper`, `merge_helper`, and `life_helper` provide reusable admin-command and assertion utilities.

## Control Flow
`RunningState::new()` creates encrypted temp raft engine, bootstraps store and first region, creates the batch system, configures state storage, creates a tablet factory/registry and initial tablet, wraps the router, builds snapshot manager/coprocessor host/importer/background workers, and starts the raftstore-v2 system. `Cluster::with_configs()` disables ticks, creates each `TestNode`, starts it with a channel transport, and records routers/receivers. `Cluster::dispatch()` drains queued raft messages, finds target nodes by store id, simulates snapshot transfer by moving snapshot directories and encryption metadata, sends messages to routers, waits for flushes, and repeats until no messages remain.

## State and Persistence Behavior
The harness uses real temp directories for raft engines, tablet directories, tablet snapshots, and SST importer data. Restart drops `RunningState` and recreates it against the same temp path and PD client, preserving raft/tablet state. Snapshot transfer physically renames generated snapshot directories into receive paths and migrates encryption metadata. `stale_snapshot()` issues a stale-read snapshot request using write-batch flags.

## Dependencies and Integration Points
The file integrates `engine_test`, `engine_traits`, `raftstore_v2::{Bootstrap, StateStorage, StoreSystem, create_store_batch_system}`, raftstore store/coprocessor types, `test_pd`, `SstImporter`, encryption data-key management, resource control, concurrency manager, and TiKV worker utilities. It is imported by both normal integration and failpoint test targets.

## Risks and Edge Cases
- Automatic ticks are disabled, so tests must explicitly send ticks/dispatch messages; forgetting this can look like a product bug.
- `dispatch()` simulates snapshot transfer by filesystem rename and key import, so it must stay aligned with real snapshot manager paths.
- `wait_applied_to_current_term()` assumes commit/applied index and commit term are enough to prove current-term apply.
- Restart preserves temp path state but rebuilds runtime resources; tests relying on in-memory only state must account for loss.
- The shared path import into failpoint tests means helper behavior changes have broad blast radius.

## Test Signals
All integration/failpoint tests in this subset rely on this harness. It emits strong signals through debug info, stale snapshots, PD client reads, raft-engine direct reads, transport receiver messages, and tablet filesystem checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/mod.rs

## Purpose
This is the normal raftstore-v2 integration test crate root. It enables nightly custom test framework support, selects `test_util::run_tests`, and declares the integration modules.

## Important APIs, Types, and Functions
There are no runtime APIs. The file declares modules for the shared `cluster` harness and the test suites covering basic writes, conf changes, life cycle, merge, PD heartbeat, read, split, status, trace apply, and transfer leader.

## Control Flow
Cargo compiles this target and the custom test runner executes all declared module tests. The comment notes conflict-control tests are deferred until split support is ready.

## State and Persistence Behavior
This file has no direct persistence behavior. It controls which integration tests are compiled and run together.

## Dependencies and Integration Points
It integrates with `test_util::run_tests` and the module tree under `tests/integrations`.

## Risks and Edge Cases
- Excluding a module here silently removes its integration coverage.
- The custom test runner is required for TiKV test setup conventions.

## Test Signals
The module list is the high-level integration coverage map for raftstore-v2 in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_basic_write.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_basic_write.rs

## Purpose
This integration test file validates the basic raftstore-v2 simple-write path, request validation, follower rejection, put/delete behavior, stale snapshots, and WAL-skipping behavior for tablet writes.

## Important APIs, Types, and Functions
- `test_basic_write()` sends a valid simple write, then checks store mismatch, peer mismatch, epoch mismatch, stale term, entry-too-large rejection, and not-leader rejection after a higher-term heartbeat.
- `test_put_delete()` writes a key, reads it through stale snapshot, deletes it, reads absence, and checks WAL files are empty.
- The tests use `SimpleWriteEncoder`, `PeerMsg::simple_write`, router subscriptions, `new_peer`, epoch constants, and `check_skip_wal()`.

## Control Flow
The tests wait for region 2 to apply to current term, build request headers from debug info, and send simple-write messages through the router. Subscription futures verify proposed, committed, and final response phases. Invalid headers are cloned and mutated from a known-good header. The follower path is triggered by sending a crafted heartbeat from a higher-term peer to step down the local peer.

## State and Persistence Behavior
Successful writes mutate the tablet default CF and are visible through snapshots. Deletes remove data from the same CF. `check_skip_wal()` verifies the underlying tablet RocksDB uses empty WAL files for these raft-applied writes, implying durability comes from raft log/apply trace rather than RocksDB WAL.

## Dependencies and Integration Points
It depends on the shared cluster harness, raftstore store epoch constants, engine snapshot reads, raft messages, and raftstore-v2 router/simple-write APIs.

## Risks and Edge Cases
- Request validation must reject wrong store/peer/epoch/term before mutation.
- Large entries must be rejected before raft log append.
- A peer stepped down by a higher-term heartbeat must reject writes as not leader.
- WAL skipping is safe only if raft/apply recovery remains correct.

## Test Signals
Signals include successful proposed/committed/result futures, specific error fields (`store_not_match`, `epoch_not_match`, `stale_command`, `raft_entry_too_large`, `not_leader`), snapshot key presence/absence, and empty WAL file lengths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_basic_write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_conf_change.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_conf_change.rs

## Purpose
This file validates raftstore-v2 configuration-change behavior: adding learners, snapshot catch-up, removing peers, repeated peer recreation cleanup, removal with concurrent replicated writes, and responses to unknown peers.

## Important APIs, Types, and Functions
- `test_simple_change()` adds a learner, writes data after snapshot, verifies learner truncated/applied state and data, removes it, repeats add/remove cycles, and checks WAL skipping for admin commands.
- `test_remove_by_conf_change()` sends remove-peer and write messages together so the learner receives removal and later log entries, then verifies tombstone state and raft state cleanup.
- `add_learner()`, `write_kv()`, and `remove_peer()` are local helper functions for conf-change admin requests and replication dispatch.
- `test_unknown_peer()` sends a heartbeat from an unknown peer and expects a heartbeat response, proving peer cache/liveness behavior.

## Control Flow
Add learner uses `AdminCmdType::ChangePeer` with `AddLearnerNode`, validates leader metadata, dispatches heartbeat/snapshot messages to create the learner, and waits for snapshot generation. Removal sends `RemoveNode`, ticks raft on the removed peer, dispatches messages, sleeps for apply, and checks raft-engine tombstone state. Unknown-peer testing sends a fake heartbeat with matching target peer/epoch but unknown sender and reads the transport receiver for a heartbeat response.

## State and Persistence Behavior
The tests inspect raft-engine region state, tombstone state, raft state removal, applied/truncated indexes, tablet snapshots, and WAL files. They verify removed peers are persisted as tombstones and raft state is cleared.

## Dependencies and Integration Points
They use cluster dispatch/snapshot simulation, raft `ConfChangeType`, raft-engine read-only APIs, `PeerTick::Raft`, `SimpleWriteEncoder`, and life-cycle paths that create/destroy peers from raft messages.

## Risks and Edge Cases
- Learner snapshot apply must set truncated index equal to leader match index and preserve newly written data.
- Removing a peer must tolerate later replicated entries without resurrecting raft state.
- Repeated add/remove of peer ids must not leave stale registry or raft-engine state.
- Unknown peer responses are necessary for conf-change liveness.

## Test Signals
Signals include debug metadata peer lists/epochs, learner snapshot reads, `PeerState::Tombstone`, `get_raft_state == None`, heartbeat response messages, and empty WAL verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_conf_change.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_life.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_life.rs

## Purpose
This file tests raftstore-v2 peer life-cycle behavior driven by raft messages, tombstone messages, larger peer ids, GC peer requests/responses, and removed-peer record cleanup.

## Important APIs, Types, and Functions
- `test_life_by_message()` verifies valid raft messages create uninitialized peers, invalid messages do not, peers survive restart, and tombstone messages destroy/persist tombstones.
- `test_destroy_by_larger_id()` validates larger target peer id replacement, smaller peer id ignore/report behavior, and restart survival.
- `test_gc_peer_request()` ensures tombstone messages create-and-destroy unknown peers, prevent later normal recreation, and report on repeated tombstones.
- `test_gc_peer_response()` verifies leader-side tombstone messages for removed peers on vote/pre-vote and GC ticks, follower-side GC response reporting, and removed-record cleanup after a later write.

## Control Flow
The tests craft `RaftMessage` instances manually, mutate store id/epoch/tombstone flags/msg types, send them through routers, and observe debug info or transport receivers. Multi-node GC tests add and remove a learner, drain messages, send vote messages from the removed peer, forward tombstone messages to the removed node, then feed GC reports back to the leader and trigger record cleanup with a tick plus write.

## State and Persistence Behavior
They inspect raft state, apply state, region local state, tombstone markers, removed records, hard-state term, and restart survival. Tombstone persistence is validated with direct raft-engine debug helpers.

## Dependencies and Integration Points
The file uses cluster life helpers, raft message types, raft conf changes, router ticks, raft-engine read-only/debug APIs, and simple writes.

## Risks and Edge Cases
- Invalid peer creation messages must be ignored without partial persistent state.
- Tombstone messages must both destroy existing peers and prevent recreation by later stale normal messages.
- Larger peer id replacement must not lose term or leave old peer runnable.
- Removed-peer GC must avoid endless vote traffic while eventually pruning removed records.

## Test Signals
Signals include peer nonexistence, persisted tombstone state, heartbeat response/absence, GC peer response messages, tombstone outbound messages, removed-record length, and post-write cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_life.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_merge.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_merge.rs

## Purpose
This integration test validates normal raftstore-v2 region merge behavior after repeated splits. It checks tablet-index/version changes during splits, data preservation across left/right merges, chained merges, and restart recovery after the final merged region contains all keys.

## Important APIs, Types, and Functions
- `test_merge()` defines a `do_split` closure that checks tablet index increases for the source region, new regions start at `RAFT_INIT_LOG_INDEX`, and region version increments.
- It uses `split_region()` to create six adjacent regions and `merge_region()` to merge from both directions and then chain the remaining regions.
- Snapshot reads verify marker keys in each region before and after merge.

## Control Flow
Starting from region 2, the test repeatedly splits the right-hand side to create six regions. It validates each region's marker key is readable in the expected range. It merges region 1 into 2, region 6 into 5, then merges the middle chain until all data is in region 5. After restart, it reads all marker keys from the final region.

## State and Persistence Behavior
The test directly checks raft-engine region state at current and exact tablet indexes, flushed index relative to tablet index, region epoch version increments, and persisted data survival after restart. Merges must preserve data from destroyed source tablets in the target.

## Dependencies and Integration Points
It uses cluster split/merge helpers, raft-engine read-only APIs, tablet index constants, snapshots, and store id/peer constructors.

## Risks and Edge Cases
- Tablet indexes must advance for source splits and remain init for newly created tablets.
- Flushed indexes must cover the tablet index used by persisted region state.
- Merge direction must not matter; source data must appear in target for both left-to-right and right-to-left merges.
- Restart must reconstruct the final merged range with all data.

## Test Signals
Signals include tablet-index inequality/equality, version increments, flushed-index bounds, snapshot key presence before/after merge, and post-restart data presence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_merge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_pd_heartbeat.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_pd_heartbeat.rs

## Purpose
This integration file validates raftstore-v2 PD reporting for region leaders, store heartbeat statistics, and region bucket reporting/refreshing.

## Important APIs, Types, and Functions
- `test_region_heartbeat()` queries local region leader status and then polls PD for region leader by id.
- `test_store_heartbeat()` writes a key, sends a PD store-heartbeat tick, and validates PD store stats for capacity/used size, keys written, and bytes written.
- `test_report_buckets()` enables coprocessor region buckets, writes enough data, flushes, triggers split-region check and report-buckets ticks, validates bucket stats in PD, then refreshes bucket ranges and confirms merged bucket stats reset.

## Control Flow
Tests build request headers/status requests manually or through router helpers. Store heartbeat uses `StoreMsg::Tick(StoreTick::PdStoreHeartbeat)`. Bucket reporting writes repeated padded keys, flushes default CF to make split-key detection possible, sends `PeerTick::SplitRegionCheck` and `PeerTick::ReportBuckets`, then uses PD client bucket APIs. It also sends `PeerMsg::RefreshRegionBuckets` with bucket ranges to test local bucket merge before another report.

## State and Persistence Behavior
Store stats and bucket stats are observed in PD's test server. Bucket tests also mutate tablet data, flush it, update in-memory/local bucket metadata, and reset per-bucket write stats after reporting.

## Dependencies and Integration Points
The file integrates router status queries, PD client APIs, store control ticks, peer ticks, coprocessor bucket config, `ReadableSize`, `SimpleWriteEncoder`, and tablet registry flush.

## Risks and Edge Cases
- Store heartbeat byte counts must exceed encoded write payload size and key counts must reset per interval.
- Bucket stats must be reported once and then reset to zero on the next report.
- Refreshing same bucket ranges twice must merge bucket metadata into a single range without corrupting PD report shape.
- Tests account for initial PD stats possibly having `start_time == 0`.

## Test Signals
Signals include PD leader lookup, nonzero capacity/used, exact key count, bytes-written lower bound, bucket key count > 2, per-bucket write stats bounds, zeroed stats on second report, and single merged bucket stat vector after refresh.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_pd_heartbeat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_read.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_read.rs

## Purpose
This file validates raftstore-v2 read-query behavior: read-index execution and lease skipping, snap requests without explicit read index, rejection of write commands through query path, invalid snapshot request parameters, and local snapshot retry/lease behavior.

## Important APIs, Types, and Functions
- `test_read_index()` configures a short leader lease, issues snap+read-index queries, observes read-index value 6 after lease expiry and 0 while lease is valid or renewed by write.
- `test_snap_without_read_index()` confirms plain snap reads can use lease, while `read_quorum` forces read-index.
- `test_query_with_write_cmd()` sends write command types through query and expects error responses, not read results.
- `test_snap_with_invalid_parameter()` checks store id, peer id, stale term, stale-read flag, and invalid epoch rejection.
- `test_local_read()` uses `router.snapshot()` directly, then query returns read-index 0 because snapshot retry renewed the lease.

## Control Flow
The tests create `RaftCmdRequest` values with `CmdType::Snap`, optional `read_index`, and header flags. They sleep past configured lease durations to force read-index. Writes use `SimpleWriteEncoder` and `PeerMsg::simple_write` to renew leases. Invalid cases mutate a known-good request and inspect `QueryResult`.

## State and Persistence Behavior
The tests primarily observe raft read state and leader lease state, not persistent storage. The write in `test_read_index()` mutates tablet data only to renew the leader lease.

## Dependencies and Integration Points
They depend on cluster query/snapshot helpers, raft command protobufs, `WriteBatchFlags`, router read APIs, and raftstore-v2 lease/read-index code.

## Risks and Edge Cases
- Read-index should be skipped only under valid lease unless `read_quorum` is set.
- Write commands must never execute through query path.
- Stale-read flags are invalid for this snap query path.
- Direct local snapshot retries can renew lease, affecting later read-index expectations.

## Test Signals
Signals include exact read-index values (`6` or `0` in the single-node setup), missing read result for write commands, and response-header errors for invalid parameters.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_split.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_split.rs

## Purpose
This integration test validates normal raftstore-v2 split behavior, including repeated splits of existing and newly created regions, tablet-index evolution, region epoch version increments, flushed-index persistence, MVCC timestamp split-key truncation, and restart survival.

## Important APIs, Types, and Functions
- `test_split()` uses `split_region()` to split region 2 into 1000, split region 2 again into 1001, split region 1000 into 1002, and split 1002 into 1003.
- It reads raft-engine `RegionLocalState` at latest and exact tablet indexes, and raft-engine flushed indexes for `CF_RAFT`.
- It uses `txn_types::Key::append_ts`/`truncate_ts` to verify encoded MVCC split key handling.

## Control Flow
The test starts from region 2 at `RAFT_INIT_LOG_INDEX`, performs splits with key-range validation through helper writes, and after each split checks region state. For source regions, tablet index must change and version increments. For new regions, tablet index starts at `RAFT_INIT_LOG_INDEX`. It then restarts and verifies each final region can read a marker key in its range.

## State and Persistence Behavior
Splits persist new region metadata, tablet indexes, region versions, and flushed-index progress in the raft engine. They also create/install tablet state for new regions. Restart validates this persisted split graph.

## Dependencies and Integration Points
It uses cluster split helper, raft-engine APIs, tablet index constants, snapshots, store peer constructors, and transaction key encoding.

## Risks and Edge Cases
- Source tablet indexes must monotonically advance across repeated splits.
- Flushed index must be at least the new tablet index to support recovery.
- New split region tablets should start at init log index.
- Encoded keys with timestamps must split on the raw key boundary.

## Test Signals
Signals include tablet-index equality/inequality, version increments, exact region state lookup by tablet index, flushed-index lower bounds, and post-restart snapshot key presence in all split regions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_split.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_status.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_status.rs

## Purpose
This file validates basic raftstore-v2 status query behavior for region leader and region detail commands, including invalid store-id rejection.

## Important APIs, Types, and Functions
- `test_status()` builds `RaftCmdRequest` status requests with `StatusCmdType::RegionLeader` and `StatusCmdType::RegionDetail`.
- It uses `new_peer(1, 3)` as the initial single-node leader peer expectation.

## Control Flow
The test queries region 2 for leader, then region detail. It verifies leader, region id, empty range bounds, peer list, and initial epoch version/conf version. It mutates the header peer store id to 4 and expects a store-not-match error.

## State and Persistence Behavior
No persistent data is modified. The file observes bootstrapped region metadata and leader state.

## Dependencies and Integration Points
It uses the shared cluster query helper, raft command status protobufs, and raftstore-v2 status query path.

## Risks and Edge Cases
- Status queries still need header validation; wrong store id should not return local metadata.
- Initial region detail must match bootstrap constants for single-node raftstore-v2.

## Test Signals
Signals include exact leader peer, region id 2, empty start/end keys, single peer, epoch `(version=1, conf_ver=1)`, and `store_not_match` error.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_status.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_trace_apply.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_trace_apply.rs

## Purpose
This integration test validates trace-apply recovery for tablet data after restart, especially with RocksDB WAL disabled. It ensures unflushed raft-applied writes are replayed from raft/apply traces and that already flushed data does not cause redundant recovery writes.

## Important APIs, Types, and Functions
- `count_file()`, `count_sst()`, and `count_info_log()` inspect tablet directory files.
- `test_data_recovery()` writes 100 keys into each data CF with different flush patterns: default CF unflushed, write CF half flushed, lock CF fully flushed.
- It uses `avoid_flush_during_shutdown` to prevent shutdown flushes from masking recovery behavior.

## Control Flow
The test records initial LOG count, writes default/write/lock CF data, flushes selected CFs, verifies all data through a stale snapshot, disables shutdown flush, restarts, writes another key, and verifies all original data recovered. It checks LOG and SST counts, flushes all CFs, checks only expected recovery memtables created new SSTs, restarts again, verifies data is immediately readable, flushes again, and confirms no extra SSTs were produced.

## State and Persistence Behavior
This is a direct persistence test for tablet data, raft apply trace, RocksDB SST creation, WAL skipping, and recovery replay. Because WAL is disabled, unflushed data must come back through raftstore-v2 recovery logic rather than RocksDB WAL.

## Dependencies and Integration Points
It depends on tablet registry paths, RocksDB file layout, CF flush APIs, snapshots, `SimpleWriteEncoder`, router writes, `DATA_CFS`, and `RAFT_INIT_LOG_INDEX`.

## Risks and Edge Cases
- Unflushed applied writes must not be lost across restart.
- Recovery must be CF-aware and avoid rewriting already flushed ranges.
- Disabling shutdown flush is necessary to expose recovery rather than normal RocksDB persistence.
- File-count assertions are sensitive to RocksDB behavior changes.

## Test Signals
Signals include exact LOG counts after restarts, exact SST counts after controlled flushes, and full key/value verification across all data CFs before and after restarts.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_trace_apply.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_transfer_leader.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_transfer_leader.rs

## Purpose
This file validates leader transfer in a multi-node raftstore-v2 cluster with real replication dispatch. It ensures followers catch up before transfer, leadership is observed consistently on both source and target routers, and writes work before and after transfer in both directions.

## Important APIs, Types, and Functions
- `put_data()` writes a key through a specified leader node, dispatches messages in phases, verifies local visibility, verifies follower lag before heartbeat, then triggers raft ticks to commit on follower and verifies follower visibility.
- `must_transfer_leader()` sends `AdminCmdType::TransferLeader`, then loops dispatching messages and querying debug info until both routers report the target leader id.
- `test_transfer_leader()` creates a three-node cluster, adds node 1 as a voter, writes data, transfers leadership to node 1, writes again, and transfers back to node 0.

## Control Flow
The test first adds a peer with `ConfChangeType::AddNode`, dispatches to create it, and validates follower debug info. `put_data()` drives proposal/commit by sleeps plus `cluster.dispatch()` and explicit raft ticks. Transfer leader uses admin command plus repeated dispatch and debug polling with a final assert fallback.

## State and Persistence Behavior
The test mutates replicated tablet data and raft leadership state. It observes follower snapshots before and after commit heartbeats to ensure data application follows raft commit, not just message receipt.

## Dependencies and Integration Points
It integrates cluster multi-node setup, conf-change admin commands, transfer-leader admin commands, raft ticks, dispatch transport simulation, stale snapshots, and debug metadata.

## Risks and Edge Cases
- Transfer to a lagging follower should be preceded by data catch-up; the helper explicitly tests commit propagation.
- Leadership observations must converge on both old and new leader routers.
- Writes after transfer must use the new leader and still replicate back.

## Test Signals
Signals include successful add-node metadata, follower leader id, key visibility on leader and later follower, transfer command success, and both routers reporting the expected leader id in debug info.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_transfer_leader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/Cargo.toml -->
# sources/storage-engines/tikv/components/raftstore/Cargo.toml

## Purpose
This manifest defines the `raftstore` crate package metadata, feature flags, normal dependencies, and test dependencies. The crate provides raftstore v1/shared store and coprocessor components used by TiKV and also imported by raftstore-v2 tests and workers.

## Important APIs, Types, and Functions
As a `Cargo.toml`, it has no Rust APIs. Important configuration includes:
- Package name `raftstore`, version `0.0.1`, edition 2021, unpublished.
- Default features enabling `test-engine-kv-rocksdb`, `test-engine-raft-raft-engine`, and `engine_rocks`.
- Feature flags for failpoints, test exports, RocksDB/raft-engine test engines, and panic test engines.
- Dependencies on batch-system, engine traits/Rocks, raft, raft-proto, kvproto, pd_client, resource control/metering, service, sst_importer, tikv_util, yatp, tokio, and many TiKV shared crates.
- Dev-dependencies for encryption export, engine_panic, engine_test, file_system testexport, panic_hook, and test_sst_importer.

## Control Flow
Cargo uses this manifest to resolve conditional compilation and dependency graph construction. The default feature set makes raftstore usable in tests with RocksDB-backed KV and raft-engine-backed raft storage.

## State and Persistence Behavior
The manifest does not directly manage state. It selects persistence-related implementations by enabling engine crates and test engine features. Dependency selection affects whether RocksDB compaction events, raft log storage, encryption, and SST importer behavior are compiled.

## Dependencies and Integration Points
This manifest is the integration point for raftstore's shared dependencies. In this subset, raftstore-v2 code imports raftstore store types such as `Config`, `Bucket`, `TabletSnapManager`, `Transport`, `WriterContoller`, unsafe recovery syncers, and coprocessor config/host types.

## Risks and Edge Cases
- Default test-engine features couple normal crate builds to test engine implementations unless features are customized.
- Optional `engine_rocks` is required for compaction event sender code; disabling it may affect modules behind feature gates.
- Failpoint support is opt-in through the `failpoints` feature.
- Dependency drift here can affect both raftstore v1 and raftstore-v2 shared usage.

## Test Signals
No tests are defined in the manifest, but the selected dev-dependencies and features enable the integration and failpoint test suites researched in this work item.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/compacted_event_sender.rs -->
# sources/storage-engines/tikv/components/raftstore/src/compacted_event_sender.rs

## Purpose
This file adapts RocksDB compaction-finished events into raftstore store-control messages. It is the raftstore v1 implementation of `engine_rocks::CompactedEventSender`.

## Important APIs, Types, and Functions
- `RaftRouterCompactedEventSender<EK, ER>` holds a `Mutex<RaftRouter<EK, ER>>`.
- Its `CompactedEventSender::send()` implementation wraps a `RocksCompactedEvent` in `StoreMsg::CompactedEvent` and sends it to the raftstore control router.

## Control Flow
When RocksDB emits a compaction event, the sender locks the router mutex, constructs the store message, and calls `send_control`. Failures are logged as warnings and otherwise ignored.

## State and Persistence Behavior
The file does not persist data. It forwards compaction metadata from the storage engine into raftstore, where later handlers can update region size/statistics or trigger follow-up work.

## Dependencies and Integration Points
It depends on `engine_rocks::{CompactedEventSender, RocksCompactedEvent}`, `engine_traits::{KvEngine, RaftEngine}`, raftstore `StoreMsg`, and the v1 `RaftRouter`. The `KvEngine` implementation must use `RocksCompactedEvent` as its compaction event type.

## Risks and Edge Cases
- The router is protected by a standard mutex; compaction callback paths must not introduce deadlocks by re-entering with the same lock.
- Dropped `send_control` failures mean compaction events can be lost during shutdown or router failure.
- The implementation is specific to Rocks compaction events and not generic over other engine event types.

## Test Signals
No direct tests are present. Indirect signals would be raftstore components receiving `StoreMsg::CompactedEvent` after RocksDB compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/compacted_event_sender.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/config.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/config.rs

## Purpose
This file defines raftstore coprocessor configuration for split checking, region bucket behavior, consistency checking, and online config dispatch. It also validates derived split and bucket thresholds, with raftstore-v2-specific optimization for much larger split size defaults.

## Important APIs, Types, and Functions
- `Config` is serializable/deserializable and derives `OnlineConfig`. It includes split-on-table, batch split limit, optional split/max size and key thresholds, consistency check method, deprecated perf level, bucket enablement/size/approximation/merge settings, and approximate-bucket preference.
- `ConsistencyCheckMethod` selects raw or MVCC consistency checking.
- Constants include `SPLIT_SIZE` (256 MB), `RAFTSTORE_V2_SPLIT_SIZE` (10 GB), `BATCH_SPLIT_LIMIT`, `DEFAULT_BUCKET_SIZE` (50 MB), and `DEFAULT_REGION_BUCKET_MERGE_SIZE_RATIO`.
- `Config::region_split_size`, `region_max_keys`, `region_max_size`, `region_split_keys`, and `enable_region_bucket` expose defaulted values.
- `Config::optimize_for(raftstore_v2)` sets default split size to the v2 value when appropriate.
- `validate_bucket_size()` enforces bucket-size, approximate-threshold, nonzero, and merge-ratio constraints.
- `Config::validate(raft_kv_v2)` fills missing derived thresholds, validates max >= split values, and auto-enables region buckets for raftstore-v2 when useful.
- `SplitCheckConfigManager<EK>` dispatches online config changes to a `Scheduler<SplitCheckTask<EK>>`.

## Control Flow
Validation first fills `region_split_keys`, then validates or derives `region_max_size` and `region_max_keys`. It then validates bucket settings. If bucket validation succeeds and raft-kv-v2 is enabled with unspecified `enable_region_bucket`, it auto-enables buckets when split size is at least twice bucket size. If bucket validation fails but buckets are disabled, the invalid bucket settings are tolerated.

## State and Persistence Behavior
The config object is mutable during validation: missing optional thresholds are materialized into `Some` values, and `enable_region_bucket` can be set. Online changes are not applied directly here; they are scheduled as `SplitCheckTask::ChangeConfig`.

## Dependencies and Integration Points
It depends on `engine_traits::KvEngine`, online-config traits, serde, TiKV `ReadableSize`, worker `Scheduler`, raftstore `SplitCheckTask`, and consistency-check config types. Raftstore-v2 tests use this config for bucket behavior.

## Risks and Edge Cases
- Validation mutates the config, so callers comparing pre/post config should expect derived values to appear.
- Invalid bucket size is accepted if bucket feature is disabled; enabling later without revalidation could be risky if not routed through config manager.
- The comment says region max size default is split size times 3/2; code implements `split / 2 * 3`, which is integer-sized `ReadableSize` arithmetic.
- `optimize_for()` only changes split size when it was unspecified.

## Test Signals
The in-file `test_config_validate()` covers max-size and max-keys validation/derivation, disabled bucket tolerance, and split-key derivation. Integration bucket tests in raftstore-v2 validate runtime effects of enabling buckets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/consistency_check.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/consistency_check.rs

## Purpose
This file defines the raftstore coprocessor consistency-check observer interface and a raw-data implementation that computes CRC32 over all key/value pairs in a region plus the region state record. It supports consistency verification across replicas.

## Important APIs, Types, and Functions
- `ConsistencyCheckObserver<E>` extends `Coprocessor` with `update_context()` and `compute_hash()`. Observers append policy markers to a context and later compute hashes from snapshots.
- `Raw<E>` is a zero-sized observer using `PhantomData<E>`.
- `Raw::update_context()` appends `ConsistencyCheckMethod::Raw` to the context and returns `true`, indicating later observers should be skipped because raw checking is strongest/heaviest.
- `Raw::compute_hash()` consumes the raw-method marker from context and delegates to `compute_hash_on_raw()`.
- `compute_hash_on_raw()` scans all snapshot CFs over encoded region bounds, feeds keys and values into `crc32fast::Hasher`, then includes the `CF_RAFT` region-state key and value if present.

## Control Flow
During context construction, observers can append method identifiers and stop further observers. During hash computation, `Raw` checks that context is nonempty, asserts the first byte is the raw method marker, advances the context slice, and computes the digest from snapshot data and region state.

## State and Persistence Behavior
This file is read-only against snapshots. It does not persist data, but it includes persistent region-local state in the hash so metadata divergence is detected along with user data divergence.

## Dependencies and Integration Points
It depends on `engine_traits::{KvEngine, Snapshot, CF_RAFT}`, `kvproto::metapb::Region`, raftstore coprocessor traits, consistency-check config enum, `keys` region/data key encoding, and `crc32fast`.

## Risks and Edge Cases
- `compute_hash()` asserts the context marker; malformed context can panic rather than return an error.
- Raw consistency scan is heavy because it scans every CF over the full encoded region range.
- Snapshot `cf_names()` controls which CFs participate; engine implementations must expose the expected CF set.
- Region state inclusion reads from `CF_RAFT`, so missing region state is tolerated but divergent present values alter the hash.

## Test Signals
The in-file `test_update_context()` verifies that raw observer appends exactly one context byte with the raw method value and requests observer skipping.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/consistency_check.rs -->
