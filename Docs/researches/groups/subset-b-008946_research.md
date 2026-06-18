# subset-b-008946 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_replica_stale_read.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_replica_stale_read.rs

## Purpose
This failpoint suite validates TiKV replica stale-read correctness when follower/learner replicas answer reads from local state using resolved-ts and replica read-state metadata. It stresses the conditions under which a replica can serve an old timestamp without issuing ReadIndex, and when it must reject with `data_is_not_ready` or fall back to normal leader snapshot reads.

## Important APIs, Types, And Functions
`prepare_for_stale_read` and `prepare_for_stale_read_before_run` build a three-node `ServerCluster`, enable `resolved_ts`, transfer leadership, construct a `PeerClient`, and install `propose_readindex_from_follower=panic` to prove follower stale reads do not go through ReadIndex. Test code uses `PeerClient` helpers such as `must_kv_write`, `must_kv_read_equal`, `must_kv_prewrite`, `must_kv_commit`, `must_kv_prewrite_one_pc`, `must_kv_prewrite_async_commit`, `must_kv_pessimistic_lock`, and low-level `kv_read`. PD and raftstore control is via `TestPdClient`, `must_split`, `must_merge`, `must_transfer_leader`, `RegionPacketFilter`, `IsolationFilterFactory`, and failpoints including `before_sync_replica_read_state`, `on_apply_res`, `raft_before_applying_snap_finished`, `apply_before_prepare_merge_2_3`, and `on_schedule_merge`.

## Control Flow
The basic replication tests write data on the leader, block `MsgAppend` to a follower, and assert that reads at timestamps already applied succeed while reads at newer commit timestamps are rejected. The lock tests leave unresolved MVCC locks and verify safe-ts is bounded by the minimum lock start timestamp, then advances after locks commit. Apply-index tests arrange ordering races where resolved-ts, apply-index, and synchronized `(apply_index, safe_ts)` tuples are updated in different orders, proving followers cannot be advertised a safe timestamp for data they have not applied.

Snapshot and merge tests move the same stale-read invariant across region lifecycle events. While a follower is applying a snapshot, stale reads should return `data_is_not_ready` with safe-ts zero, then resume after the snapshot is applied. Merge tests assert that target-region safe-ts becomes the minimum of source and target state, source leaders stop advancing safe-ts during merge, rollback resumes advancement, and reading a source range after target merge does not expose writes hidden behind a source lock.

## State And Persistence Behavior
The observable state is MVCC data and locks, per-peer apply index, resolved-ts/safe-ts, replica read-state broadcast state, region epoch and peer topology, snapshot application state, and concurrency-manager max-ts. Tests deliberately persist data through raft replication, snapshots, merges, and peer replacement. `test_stale_read_future_ts_not_update_max_ts` confirms a future-timestamp stale read does not raise the leader concurrency manager's max-ts, preserving later async-commit and 1PC transactions with smaller timestamps.

## Dependencies And Integration Points
The file integrates TiKV storage RPC behavior through `PeerClient`, PD region scheduling through `TestPdClient`, raftstore message filtering, failpoint injection, resolved-ts advancement, snapshot apply, merge scheduling, and learner peer creation. It is a cross-layer test for MVCC, concurrency manager, raftstore replica state, and PD-driven region membership.

## Risks And Edge Cases
The main risks are serving stale or future data when a follower has safe-ts but lacks the corresponding apply index, failing to reset safe-ts during snapshot apply, incorrectly merging lock resolver state, updating source safe-ts after merge, treating pessimistic locks from old leaders as blockers, serving stale reads from learners before they are ready, or allowing stale reads to perturb max-ts.

## Test Signals
Success is signaled by exact value reads at allowed timestamps, `data_is_not_ready` region errors at unsafe timestamps, safe-ts zero while snapshot apply is paused, absence of follower ReadIndex proposals, successful post-snapshot/post-merge reads, and successful async-commit/1PC writes after future-timestamp stale reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_replica_stale_read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_server.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_server.rs

## Purpose
This file tests TiKV server-side raft transport and health behavior under failpoint-induced failures: store-id/address mismatch, full raft send channels, health-service status transitions, and raft message observer rejection. It verifies server behavior around connection recovery and status reporting rather than storage semantics.

## Important APIs, Types, And Functions
The tests use `new_server_cluster`, `cluster.run_node`, `cluster.stop_node`, PD `get_store`, `must_put`, `async_put`, and engine assertions. Raft transport is exercised with `RegionPacketFilter`, `CloneFilterFactory`, and `MessageType` filters. Health checks build a grpc health service from `health_controller.get_grpc_health_service()` using `grpcio::ServerBuilder`, `HealthClient`, and `HealthCheckRequest`. Failpoints include `mock_store_refresh_interval_secs`, `send_raft_message_full`, `on_batch_raft_stream_drop_by_err`, `pause_on_peer_collect_message`, `force_reject_raft_append_message`, and `force_reject_raft_snapshot_message`.

## Control Flow
`test_mismatch_store_node` swaps node addresses by stopping nodes, restarting node 2 on node 3's address and node 3 on node 2's address, and blocking prevote traffic. With store refresh forced to zero interval, a write should trigger address refresh and recover replication despite the original mismatch. `test_send_raft_channel_full` injects a full send channel and asserts this condition should not drop the batch raft stream, then removes the failpoint and confirms replication resumes.

`test_serving_status` starts a standalone grpc health server around TiKV's health controller. It observes normal `Serving`, explicit `NotServing`, `ServiceUnknown` while peer collection is paused long enough to make raftstore progress unobservable, and recovery back to `Serving` after the failpoint is removed. `test_raft_message_observer` rejects append and snapshot messages while adding peers, validates peers do not receive data while rejection is active, then removes failpoints and verifies both existing and newly added peers catch up.

## State And Persistence Behavior
Persistent state is ordinary replicated KV data in the engines. Transient server state includes PD store address metadata, raft client connection/cache state, bounded raft send queues, health controller serving flags, and raftstore progress collection. The tests check that transient transport failures do not corrupt durable data and that recovery leads to replicated KV state on all expected stores.

## Dependencies And Integration Points
The suite connects test raftstore cluster orchestration, PD store metadata, grpc transport, batch raft streams, health checking, raft message observers, and TiKV failpoints. It also depends on `tikv_util::HandyRwLock` to access simulator internals for health controllers.

## Risks And Edge Cases
Risks covered include a raft client keeping a stale address after a store-id mismatch, treating send-channel backpressure as a stream-breaking error, health status remaining `Serving` while peer collection is stuck, health status ignoring manual serving toggles, and raft observer rejection leaving peers permanently unable to catch up.

## Test Signals
Assertions check address metadata after refresh, replicated values on affected engines, no panic on stream-drop failpoint while the send channel is full, grpc health status transitions, absent data while append/snapshot rejection is active, and successful replication after failpoints are removed.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_snap.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_snap.rs

## Purpose
This suite validates raft snapshot generation, sending, receiving, application, retry, GC, recovery, and shutdown behavior. It targets failure windows where snapshots overlap split ranges, network/resolve errors interrupt transfer, peers are destroyed during pending snapshot application, raft writes fail after KV snapshot writes, and receiver concurrency limits serialize ingestion.

## Important APIs, Types, And Functions
Helpers `must_empty_dir` and `assert_snapshot` poll snapshot directories. The tests use `configure_for_snapshot`, `configure_for_request_snapshot`, `new_node_cluster`, `new_server_cluster`, `test_raftstore_v2` variants, `MessageTypeNotifier`, `RegionPacketFilter`, `DropSnapshotFilter`, `IsolationFilterFactory`, `get_snap_mgr`, raft-engine debug APIs, and snapshot manager stats. Key failpoints include `region_gen_snap`, `transport_on_send_snapshot`, `snapshot_delete_after_send`, `snapshot_enter_do_build`, `apply_pending_snapshot`, `destroy_peer_after_pending_move`, `skip_schedule_applying_snapshot`, `peer_2_handle_snap_mgr_gc`, `before_no_ready_gen_snap_task`, `before_region_gen_snap`, `get_snapshot_for_gc`, `receiving_snapshot_net_error`, `worker_gc_raft_log`, `raft_before_save_on_store_1`, `APPLY_COMMITTED_ENTRIES`, `RESET_APPLY_INDEX_WHEN_RESTART`, `snap_send_duration_timeout`, `snap_send_timer_delay`, `snap_send_error`, `receiving_snapshot_callback`, `snap_gen_precheck_failed`, and `post_recv_snap_complete*`.

## Control Flow
Early tests verify snapshot file lifecycle: overlapped snapshots from pre-split ranges are cleaned, snapshot sending retries after address resolution failure, in-flight generation tasks are canceled or replaced when deleted after send, and snapshot directories empty after send completion. Pending-snapshot destruction tests isolate a peer, force it into applying state, remove and recreate peers, pause destroy/apply paths, restart nodes, and assert the correct peer eventually applies data and snapshot files are GCed.

Several tests inject old or failed snapshots. `test_receive_old_snapshot` captures an old snapshot, lets the peer catch up with newer data, replays the old snapshot, then removes/re-adds peers across a split to ensure pending snapshot metadata is not left behind. Recovery tests corrupt ordering between KV snapshot application and raftdb state persistence, stop/restart nodes, and assert the snapshot is re-applied cleanly and stale raft logs are removed. Other cases validate snapshot generation from no-new-commit ready, cancellation when log GC advances the truncated index, cleanup after GC failures, send timeouts, corrupted SST retry, and send-error cleanup.

The receiver-busy tests configure `concurrent_recv_snap_limit = 1` and orchestrate two regions sending snapshots to the same store. They assert snapshot generation pauses or precheck fails while the receiver is busy, then both regions complete when the first receive finishes.

## State And Persistence Behavior
Persistent artifacts include `.meta` and SST snapshot files, raft logs, `RaftLocalState`, region local state, and KV data in RocksDB. Transient state includes snapshot manager sending/receiving counters, pending snapshot regions, peer `Applying` state, raft progress in `Snapshot`, and receiver precheck reservations. The tests emphasize cleanup: stale snapshot files, stale raft logs before first index, pending metadata, and leader-side generated snapshots must not survive after failure recovery.

## Dependencies And Integration Points
These tests connect raftstore peer FSMs, apply FSMs, snapshot manager, server transport, raft engine, RocksDB snapshot ingestion, PD membership changes, failpoint scheduling, and both raftstore v1/v2 clusters through `test_case`.

## Risks And Edge Cases
Risks include peers stuck in snapshot progress after send failure, panics when destroying peers with pending apply tasks, old snapshots resurrecting stale metadata, snapshot generation using a truncated index, leaked receiving counters, incomplete raftdb recovery, corrupted snapshot retry failure, send-timeout leaks, and busy receivers allowing duplicate or unbounded snapshot generation.

## Test Signals
Signals are engine value presence/absence, snapshot directory emptiness or expected files, snapshot manager counters, raft log emptiness after recovery, peer state transitions, received snapshot notifications, PD peer membership checks, no panic during shutdown, and successful writes after snapshot recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_snap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_split_region.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_split_region.rs

## Purpose
This large failpoint suite validates region split correctness across raftstore metadata, peer creation, snapshot interaction, split-check scheduling, pessimistic locks, leader election, raftstore-v2 split initialization, and PD heartbeat reporting. Its focus is preventing stale or duplicate peers, corrupted store metadata, wrong leader/read behavior, and lost split progress in race-heavy code paths.

## Important APIs, Types, And Functions
Important helper types are `PrevoteRangeFilter`, which records vote message ranges around split, `CollectSnapshotFilter`, which piles snapshot messages by source peer, and `TeeFilter`, which records outgoing raft messages. `gen_split_region` creates size-driven split scenarios. The suite uses `new_node_cluster`, `new_server_cluster`, `test_raftstore_v2`, `configure_for_merge`, `configure_for_snapshot`, `configure_for_request_snapshot`, PD `must_add_peer`/`must_remove_peer`/`must_merge`/`split_region`, `cluster.split_region`, `must_split`, `read_on_peer`, `TikvClient`, `PessimisticLockRequest`, `PrewriteRequest`, `SnapshotExt`, and raw access to store metas and local states. It uses many split failpoints, notably `before_set_region_on_peer_3`, `before_destroy_peer_on_peer_1003`, `apply_before_split_*`, `apply_after_split_*`, `is_generating_snapshot`, `region_split_skip_max_count`, `on_split_region_check_tick`, `on_handle_apply_*`, `before_check_snapshot_*`, `on_snap_msg_*`, `on_vote_msg_*`, `on_append_msg_*`, `on_heartbeat_msg_*`, `on_handle_apply_split_2_after_mem_check`, `on_split`, `after_split`, `txn_before_process_write`, `on_split_invalidate_locks`, `worker_gc_raft_log_flush`, `before_nofity_apply_res`, `begin_raft_poller`, `on_apply_batch_split`, `on_store_2_split_init_race_with_initial_message`, `tablet_trimmed_finished`, `fail_pre_propose_split`, and `test_pd_client::finish_region_heartbeat`.

## Control Flow
The opening tests create deliberately inconsistent timing: a peer is applying snapshot while a split inserts new region metadata, stale heartbeat triggers destroy, and a later split verifies meta remains consistent. Vote tests pause follower split apply and assert prevote/request-vote messages carry the new split range and are cached/responded after split completion. Snapshot-generation tests verify split checks pause when snapshot generation is in progress unless max skip count is reached.

The middle of the file focuses on duplicate or stale peer creation. It tests initialized peers with the same region ID, tombstoned peers, stale peers continuing to process snapshot/vote/append/heartbeat messages, uninitialized peers with same or different peer IDs, and destroy-after-memory-check ordering. These scenarios combine split, merge, peer remove/add, snapshot pauses, message isolation, and tombstone cleanup to ensure a split-created peer neither overwrites valid metadata nor resurrects removed data.

Other tests cover batching and statistics. `test_split_duplicated_batch` piles overlapping snapshots so an uninitialized peer and split peer can be fetched in one batch, ensuring ready results are mapped to the correct peer. Approximate size/key reporting tests assert split-check refreshes PD stats even when no split occurs. Split-check retry tests inject one failed pre-propose split and expect later size/key checks to complete.

The transaction section validates pessimistic lock safety during split. Concurrent lock/prewrite requests paused before processing must return `EpochNotMatch` when split invalidates in-memory locks or changes epoch, rather than writing locks to the wrong region or returning misleading `PessimisticLockNotFound`.

The final raftstore-v2 and election tests cover split during shutdown, split racing with conf change, split-init racing with initial messages without sending to store 0, slow split with tablet trim and dirty-data reset, new-region leadership after parent leader transfer, and pending peer reporting in PD heartbeats while a split peer has not applied yet.

## State And Persistence Behavior
The suite observes store metadata maps, region local states (`Normal`, tombstone/cleared), peer IDs and epochs, raft logs and log-GC responses, snapshot files/messages, in-memory pessimistic locks, approximate region size/keys, tablet dirty-data flags, PD heartbeat pending peers, and actual KV data by key range. Persistent behavior is validated by engine reads after split/merge/remove/readd operations and by ensuring destroyed regions are cleared while surviving ranges keep their data.

## Dependencies And Integration Points
This is a deep integration suite for raftstore peer FSM, apply FSM, split checker, PD scheduler, transaction lock manager, snapshot manager, raft transport filters, grpc `TikvClient`, tablet storage in raftstore-v2, and test macros that run selected cases against both raftstore implementations.

## Risks And Edge Cases
Covered risks include metadata corruption from concurrent destroy and split insert, dropped or misranged vote messages during slow split, duplicate initialized peers, stale uninitialized peers becoming valid after tombstone, split ready mapped to the wrong peer in a batch, epoch-unsafe pessimistic writes, async log-GC callbacks mutating a replacement peer, channel-full split result loss, shutdown races, messages to store 0 during split init, dirty-data never reset after tablet trim index mismatch, split retry starvation, and PD heartbeats missing pending peers.

## Test Signals
Signals include successful `must_put`/`must_get_equal` after each race, `must_get_none` for cleared stale ranges, expected `EpochNotMatch` errors, PD approximate stat changes, explicit leader identity assertions, pending peer checks in heartbeat callbacks, absence of messages to store 0, channel notifications from filters/failpoints, and no panic in previously corrupting races.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_split_region.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_sst_ingest.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_sst_ingest.rs

## Purpose
This file validates range-latch coordination between SST ingestion paths and the MVCC compaction filter, plus ordering between peer destruction, snapshot application, and foreground writes. It ensures snapshot/clean-overlap ingestion and compaction GC serialize only when their key ranges overlap, while non-overlapping regions proceed independently.

## Important APIs, Types, And Functions
`prepare_data_used_by_compaction_filter` writes multiple MVCC versions with `TikvClient`, splits the keyspace into three regions (`a`, `b`, `c`), and flushes default/write CFs. `setup_cluster` returns a prepared `ServerCluster`, target `Region`, selected `Peer`, and `TestPdClient`. `start_region_migrate` removes and re-adds a peer while forcing SST ingestion via `apply_cf_without_ingest_false` and skipping stale-range cleanup. `start_compaction_filter` runs `TestGcRunner::gc`. Synchronization helpers `verify_pending` and `verify_completed` assert channel progress. Main scenario helpers are `blocked_by_ingest_test` and `blocks_ingest_test`.

## Control Flow
The first matrix starts apply-snapshot or clean-overlap ingestion, pauses after the ingest latch is acquired, then starts compaction-filter GC. For regions `a` and `b`, the GC callback should not fire until the ingestion failpoint is released because their ranges overlap compaction-filter data. For region `c`, the callback should complete immediately because the region does not overlap the relevant GC range. The second matrix reverses the order: compaction GC acquires and pauses on the latch first, then peer migration tries to ingest; overlapping regions block until GC resumes, while region `c` completes without waiting.

`test_apply_snapshot_must_wait_destroy_peer` starts a remove-peer path paused in stale-range cleanup, then re-adds the peer and asserts apply-snapshot completion is blocked until destroy-peer cleanup resumes. `test_destroy_peer_must_wait_ongoing_foreground_writes` pauses a foreground apply write, starts peer destroy, and asserts destroy completion waits for the foreground write failpoint to clear.

## State And Persistence Behavior
The test data has multiple committed versions so compaction filtering has real obsolete MVCC versions to scan. Region boundaries define whether range latches overlap. Persistent writes are flushed to RocksDB default/write CFs. Peer removal/re-addition drives snapshot SST ingestion and stale-range cleanup, while foreground writes and destroy-peer tasks contend through per-region serialization.

## Dependencies And Integration Points
The suite integrates the TiKV transactional KV RPC path, RocksDB CF flushing, region split, PD peer migration, snapshot apply SST ingestion, clean-overlap ingestion, the GC worker's compaction filter, range latch failpoints, and raftstore region-worker ordering.

## Risks And Edge Cases
Risks include deadlocks or missing synchronization between compaction filter and ingestion, over-blocking non-overlapping ranges, boundary overlap mistakes at region start/end keys, concurrent destroy and apply-snapshot with `allow_write` SST ingestion, and destroy-peer racing with in-flight foreground apply writes.

## Test Signals
Blocking is detected by `RecvTimeoutError::Timeout`; successful progress is a channel `Ok(true)`. Thread joins assert no panic. The destroy/apply tests use `apply_snapshot_finished` and `raft_store_after_destroy_peer` callbacks to prove ordering, and failpoint removal should unblock the waiting operation within the expected timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_sst_ingest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_sst_recovery.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_sst_recovery.rs

## Purpose
This suite tests TiKV's damaged SST recovery worker. It creates a cluster whose first store has a corrupted RocksDB SST spanning selected region ranges, then verifies recovery deletes damaged files only after affected peers are safely removed, preserves unrelated data, and serializes with adding peers back to the damaged store.

## Important APIs, Types, And Functions
`assert_corruption` checks engine errors contain `Corruption`. `disturb_sst_file` overwrites an SST file with invalid bytes. `compact_files_to_target_level` uses `RocksEngine::compact_files_cf` to force selected live SSTs into a target level and surface corruption. `create_tikv_cluster_with_one_node_damaged` builds a three-store `ServerCluster`, starts `RecoveryRunner` workers using each store's `store_meta`, writes three SST ranges, splits regions at `2`, `4`, and `7`, corrupts the middle `[3,5]` SST, and returns the cluster, PD client, and damaged engine.

## Control Flow
`test_sst_recovery_basic` pauses before file deletion, waits for `store_meta.get_all_damaged_region_ids()` to report two damaged regions, removes corresponding peers from store 1, proves other stores can serve the affected key, and checks the corrupted read still fails while deletion is paused. After releasing the failpoint, the corrupted key becomes absent, damaged ranges clear, live file count drops, and cluster reads still work from remaining replicas.

`test_sst_recovery_overlap_range_sst_exist` creates an additional overlapping L0 SST with updated values before removing damaged-region peers. After recovery, compaction reduces files to one while preserving non-damaged overlapping data on store 1; because store 1 no longer hosts the affected peer, cluster reads for key `4` return the newer value from other stores. `test_sst_recovery_atomic_when_adding_peer` pauses deletion, removes affected peers, attempts to add a peer back on store 1, and expects the conf change not to finish until recovery releases the store metadata lock and deletes the damaged file.

## State And Persistence Behavior
Persistent state includes RocksDB SST files, live file metadata, region replicas, and KV values across stores. In-memory state includes `store_meta.damaged_ranges` and damaged region IDs tracked by the recovery worker. Recovery must delete entire damaged SST files only after affected replicas are removed from the damaged store, and must preserve non-overlapping keys in adjacent SSTs.

## Dependencies And Integration Points
The file integrates `engine_rocks_helper::sst_recovery::RecoveryRunner`, RocksDB compaction/live-file APIs, raftstore peer membership, PD conf changes, store metadata locking, failpoints around recovery deletion, and engine `Peekable` reads.

## Risks And Edge Cases
Risks include deleting corrupted SSTs before replicas are removed, losing unaffected overlapping data, allowing conf changes to add a peer while damaged-file deletion is in progress, failing to clear damaged range metadata, or leaving RocksDB background corruption after compaction.

## Test Signals
Signals include corruption errors before recovery, `None` for corrupted keys after deletion, exact live-file counts, empty `damaged_ranges`, successful reads from healthy replicas, preserved overlapping values in store-local reads, and `must_region_not_exist`/`must_region_exist` around atomic add-peer recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_sst_recovery.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_stale_peer.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_stale_peer.rs

## Purpose
This failpoint suite validates stale-peer detection, cleanup, destruction, restart recovery, and raft-log cleanup. It covers peers removed from PD membership, peers stuck applying snapshots, stale learners, uninitialized peers, delayed async destroy, and local-reader updates after removal.

## Important APIs, Types, And Functions
The tests use `new_node_cluster`/`new_server_cluster`, `configure_for_snapshot`, PD peer operations, `must_gc_peer`, `must_region_cleared`, raft-engine debug APIs, `RaftLocalState`, `PeerState`, `RaftMessage`, and `block_on(pd_client.get_region_by_id)`. They run selected cases against raftstore v1 and v2 using `test_case`. Failpoints include `peer_check_stale_state`, `manually_set_store_offline`, `raftstore_set_region_after_change_peer`, `apply_on_add_node_1_2`, `on_handle_apply_1003`, `region_apply_snap`, `worker_gc_raft_log`, and `destroy_peer_after_pending_move`.

## Control Flow
`test_one_node_leader_missing` configures a single-node cluster with carefully ordered stale-state intervals and asserts stale-state checking should not run in a valid single-node leadership case. `test_clean_stale_peer` marks a store offline, removes a peer, and verifies offlined stores retain data files; after the store returns to serving, adding a new peer resyncs data and removing it later clears data. `test_node_update_localreader_after_removed` pauses an apply path, isolates and removes a peer, waits for stale GC, then resumes apply and asserts the removed peer does not reinsert stale local-reader state.

Restart and snapshot tests cover learners and applying peers. A stale learner paused in apply must catch up after restart. A peer applying a snapshot can be removed via tombstone message; once snapshot apply resumes, it should destroy itself without needing another message trigger. Uninitialized peer tests ensure destroying a new learner does not let an older isolated peer on the same store revive after partitions change.

The log cleanup tests simulate lost raft-log GC tasks, ensure stale logs exist below first index, then destroy or snapshot-recover the peer and assert old logs are deleted. `test_async_destroy_peer_delayed` pauses peer destroy, adds a replacement peer on the same store, resumes destroy, removes the replacement, and confirms the region data is cleared.

## State And Persistence Behavior
State under test includes raft local state, hard-state commit/last-index, peer local state (`Applying`, cleared/tombstone), local-reader delegates, engine data files, region data in all CFs, pending destroy tasks, and stale raft logs. Persistent cleanup must distinguish offlined stores, removed serving peers, uninitialized peers, and replacement peers sharing a store.

## Dependencies And Integration Points
The suite integrates PD membership, raftstore stale-state checking, snapshot apply cancellation, async destroy, SnapManager offlined state, local reader delegate updates, raft log GC worker, raft engine read/debug APIs, and simulator message filters.

## Risks And Edge Cases
Risks include unnecessary stale-state panic in a one-node cluster, deleting data for an offlined store too early, stale apply callbacks updating local readers after removal, learners losing committed-but-unapplied logs across restart, snapshot-apply peers surviving tombstone removal, old isolated peers reviving after a newer uninitialized peer is destroyed, stale raft logs left after destroy, and delayed destroy deleting data for a replacement peer incorrectly.

## Test Signals
Signals include engine file presence, value presence/absence after peer removal/addition, `must_region_not_exist`, `must_region_cleared`, local state reaching `Applying`, raft entries becoming empty, callbacks firing at failpoints, and successful reads after restart catch-up.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_stale_peer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_stale_read.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_stale_read.rs

## Purpose
This file validates node-level stale-read prevention for local lease reads and ReadIndex during split, merge, leader transfer, and peer destruction. It ensures old-region leaders cannot return stale values once another region or leader owns the key range, and that queued reads fail with explicit errors rather than timing out or returning obsolete data.

## Important APIs, Types, And Functions
`stale_read_during_splitting` drives both left-derive and right-derive split modes. `must_not_stale_read` writes a newer value through the new region, compares old/new leader local reads and ReadIndex reads, pauses `before_propose_readindex`, then releases the split/merge failpoint and expects an error. `must_not_eq_on_key` performs the read comparison. Other tests use `configure_for_lease_read`, `configure_for_merge`, `configure_for_request_snapshot`, PD split/merge, `Callback`, `read_on_peer`, `make_cb_rocks`, and raftstore message filters.

## Control Flow
Split tests pause apply on the old leader's store after initiating split, wait for another store to lead the new split region, write through the new region, and verify both local read and ReadIndex against the old region return errors, not stale values. The merge test creates two regions with different leaders, triggers merge, pauses commit-merge on all but one peer, manually adjusts source epoch to the prepare-merge epoch, and applies the same stale-read denial pattern to a key now covered by the target region.

`test_read_index_when_transfer_leader_2` delays raft messages to the old leader, queues read-index requests before and after leader transfer, then delivers heartbeat/append messages in one batch so role change and read completion race; both queued reads must return `stale_command`. `test_read_after_peer_destroyed` pauses destroy, queues a read on the removed peer, resumes destroy, waits for async raft-GC progress, and expects `region_not_found`. `test_stale_read_during_merging_2` pauses at `leader_commit_prepare_merge` after prepare-merge commit and confirms the leader lease is suspected early enough that local reads time out rather than returning an obsolete value.

## State And Persistence Behavior
The tested state is region epoch/range ownership, leader leases, pending read queues, ReadIndex proposals, peer destroy state, and merge prepare/commit progress. Persistent KV values establish the stale-versus-current answers, while transient raftstore state decides whether reads are served locally, queued, rejected, or timed out.

## Dependencies And Integration Points
The file integrates raftstore local read, ReadIndex, PD split/merge scheduling, leader transfer, message filtering, async command callbacks, destroy-peer flow, and failpoints in split/merge/read-index paths.

## Risks And Edge Cases
Risks include old leaders serving stale local reads during slow split, ReadIndex requests queued before role change succeeding after leadership is lost, prepare-merge not suspecting leader lease early enough, removed peers answering reads before destroy completes, and split derive mode differences hiding a stale key under old and new ranges.

## Test Signals
Signals include the new region returning the latest value, old region reads carrying header errors, queued reads returning `stale_command`, destroyed-peer reads returning `region_not_found`, expected timeout while merge leader is paused, and no stale value equality from the old owner.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_stale_read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_stats.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_stats.rs

## Purpose
This small failpoint test validates region bucket statistics reporting for read and write traffic. It confirms bucket metadata and per-bucket read/write counters are collected and reported to PD when region buckets are enabled.

## Important APIs, Types, And Functions
The test uses `must_new_and_configure_cluster_and_kv_client` to build a cluster and raw KV client while enabling `coprocessor.enable_region_bucket`, setting long split-check interval, short `report_region_buckets_tick_interval`, and disabling hibernate regions. It issues writes through `cluster.must_put`, point reads through `cluster.must_get`, and a `RawBatchGetRequest` through the KV client. `cluster.must_get_buckets(1)` retrieves reported bucket data. The failpoint `mock_tick_interval` forces tick scheduling to return immediately.

## Control Flow
After cluster startup and failpoint installation, the test writes 50 keys shaped as `[b'k', i]` with 4-byte values, reads them individually, then sends one raw batch-get over the same key set. It waits for bucket reporting, fetches buckets for region 1, and asserts bucket metadata contains the expected two boundary keys and one stats bucket.

## State And Persistence Behavior
Persistent state is the 50 raw KV entries. Transient/statistical state is bucket metadata and bucket read/write counters accumulated by raftstore/coprocessor reporting. Hibernate is disabled to keep the region active long enough for bucket stats to be reported.

## Dependencies And Integration Points
The test integrates raw KV RPCs, raftstore bucket reporting, PD test-client bucket retrieval, coprocessor bucket configuration, and failpoint-controlled tick intervals.

## Risks And Edge Cases
Risks include bucket reports being skipped while a region hibernates, read/write byte accounting excluding key bytes or value bytes incorrectly, batch reads not contributing to read stats, and bucket metadata not being initialized when split checks are effectively disabled.

## Test Signals
Expected signals are `buckets.meta.keys.len() == 2`, `write_keys == [50]`, `write_bytes == [50 * (4 + 2)]`, `read_keys == [50]`, and `read_bytes == [50 * (4 + 2)]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_stats.rs -->
