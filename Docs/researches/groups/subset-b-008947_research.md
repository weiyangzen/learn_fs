# Research Group subset-b-008947

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_storage.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_storage.rs

## Purpose
`test_storage.rs` is a large failpoint-driven storage test suite for TiKV's transactional and raw storage layers. It exercises scheduler behavior, RaftKV early errors, deadline propagation, asynchronous writes, pessimistic lock memory state, async-commit and 1PC prewrite paths, shared/exclusive lock semantics, raw compare-and-swap latching, and behavior during leader change and shutdown. The file is test-only, but it documents several critical ordering contracts between storage commands, the concurrency manager, lock manager, Raft proposal/apply, and read paths.

## Important APIs, Types, and Functions
The suite uses `TestStorageBuilderApiV1`, generic `TestStorageBuilder<_, _, F>`, `MockLockManager`, `Storage::sched_txn_command`, raw APIs such as `raw_compare_and_swap_atomic`, `raw_get`, `raw_put`, and command constructors from `tikv::storage::txn::commands`. It constructs `Prewrite`, `PrewritePessimistic`, `Commit`, `Rollback`, `AcquirePessimisticLock`, `ResolveLockReadPhase`, and `ResolveLock` commands with explicit `Context`, timestamps, mutation sets, assertion levels, and async-commit/1PC flags.

Important helper functions include `test_pessimistic_lock_resumable_blocked_twice_impl`, `test_async_commit_prewrite_with_stale_max_ts_impl`, `expect_locked`, `test_async_apply_prewrite_impl`, and `test_async_apply_prewrite_1pc_impl`. The suite also uses helpers from `test_raftstore` and storage test utilities, such as `must_get_equal`, `must_get_none`, `must_have_locks`, `expect_ok_callback`, `expect_fail_callback`, `expect_pessimistic_lock_res_callback`, `delete_pessimistic_lock`, and `extract_region_error`/`extract_key_error`.

## Control Flow
The tests usually create either an in-memory test storage or a one-to-three-node Raftstore cluster, prepare a region `Context`, inject one or more failpoints, schedule a storage command, and then assert on callback timing, region/key errors, persisted values, lock table contents, or leader state. Many cases deliberately block at a narrow failpoint such as `scheduler_async_snapshot_finish`, `scheduler_start_execute`, `scheduler_async_write_finish`, `on_handle_apply`, `txn_before_process_write`, `after-snapshot`, `cleanup`, or `pause_on_peer_collect_message`, then mutate cluster state before unblocking.

Scheduler tests validate that stale snapshots after double leader transfer return `StaleCommand`, that `raftkv_early_error_report` is surfaced as `RegionNotFound` before data is written, and that dynamic scheduler pool resizing can free a blocked worker. Resource-control tests switch the scheduler between single-queue and priority-queue pools as resource groups are added or removed.

Transactional tests cover pipelined pessimistic lock responses when the engine write succeeds, fails, or is still finishing; delayed resumable lock wakeups; async-commit rejection while max timestamp is unsynced after leader transfer; async-apply prewrite returning before apply while preserving memory locks; fallback when async-apply completion fails; 1PC async-apply visibility; and raw CAS latch serialization. Deadline tests assert that blocking before async write, snapshot acquisition, proposal, or multi-batch resolve-lock produces `DeadlineExceeded` or request errors rather than hidden writes.

The shared-lock block models a mixed shared/exclusive lock lifecycle: shared pessimistic locks merge, an exclusive lock turns them shrink-only and blocks on retry, committed shared locks release the exclusive waiter with conflicts, exclusive locks then block future shared locks, and `scan_lock` filters shared-lock details by max timestamp.

## State and Persistence Behavior
The tests observe both memory-only state and persisted Rocks/Raft state. Pessimistic lock tests inspect the concurrency manager and `MockLockManager` tokens, while shared-lock tests open MVCC snapshots and read lock entries from the lock CF through `MvccReader`. Async prewrite tests deliberately rely on memory locks staying visible while apply is paused, then becoming persisted after apply is released. Raw and transactional writes are verified through `must_get_equal`, `raw_get`, storage `get`, `batch_get`, and scan-lock results.

Leader-transfer and shutdown tests are especially stateful: pending storage callbacks may cross leader term changes, async apply may return before raft apply finishes, and queued commit/rollback commands during shutdown must preserve latch correctness so the first committed operation remains the durable outcome after a new leader is elected.

## Dependencies and Integration Points
The file integrates `api_version` formats (`ApiV1`, `ApiV2`), `kvproto::kvrpcpb` request/response types, gRPC `TikvClient`, `test_raftstore` cluster simulators, storage command internals, resource control, the storage config manager, lock manager, MVCC reader, flow controller, and failpoints. It runs many cases against both raftstore implementations via `#[test_case(test_raftstore::new_server_cluster)]` and `#[test_case(test_raftstore_v2::new_server_cluster)]`.

## Risks and Edge Cases
The main risks under test are stale commands after leadership churn, early errors mutating data, leaked latches or memory locks, async responses racing apply, missing max-ts synchronization on a new leader, deadline checks after work has already begun, and shared-lock waiters re-entering the wait queue incorrectly. Several tests rely on sleeps and timeout windows, so changes to scheduler timing, failpoint names, or cluster heartbeat timing can make failures look flaky even when the underlying invariant is valid.

## Test Signals
Passing signals include explicit stale-command or max-timestamp-not-synced region errors, absence of unintended writes, expected pool size and queue failpoint hits, successful callbacks only after failpoint release, no leaked locks after failure paths, lock entries with exact timestamps and lock types, final committed values after leader shutdown, and correct `KeyIsLocked` details for shared-lock conflicts.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_table_properties.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_table_properties.rs

## Purpose
`test_table_properties.rs` validates the raw-key-mode GC compaction-filter decision logic that uses RocksDB table properties. It focuses on whether TiKV should run the raw GC compaction filter for SST files based on safepoint, bottommost-level status, and the ratio between stored versions and logical rows.

## Important APIs, Types, and Functions
The public local helper `make_key` encodes an API v2 raw key with timestamp and wraps it in TiKV's data-key prefix. `do_write` and `make_data` generate test rows by writing encoded `RawValue` records into `CF_DEFAULT` through `Engine::write` and `WriteData::from_modifies`. `do_gc` locates a flushed L0 file via `rocksdb_level_files`, sets `TestGcRunner::target_level`, and runs `gc_on_files`.

The tests use `TestEngineBuilder` with `ApiVersion::V2`, `DbConfig` knobs that disable auto compactions and dynamic level bytes, `TestGcRunner`, `GC_COMPACTION_FILTER_PERFORM`, `GC_COMPACTION_FILTER_SKIP`, and `STAT_RAW_KEYMODE` metrics.

## Control Flow
`test_check_need_gc` resets metrics, builds a temp Rocks engine, writes raw values, then runs GC with a max safepoint to force filtering. It then flushes additional files and drives a file-specific GC at target levels. With `ratio_threshold = Some(0.0)`, a non-bottommost file still triggers filtering because the version/row ratio exceeds the threshold.

`test_skip_gc_by_check` writes and flushes data, then runs raw GC with a safepoint earlier than all encoded MVCC timestamps. The filter is entered but table-property checks skip actual filtering. A second phase moves data through level 2, sets `ratio_threshold = f64::MAX`, and verifies that a non-bottommost file whose version ratio is below threshold increments the skip metric.

## State and Persistence Behavior
The file persists real RocksDB SST files in a temp directory, flushes them, and invokes compaction-filter GC against raw files. It does not use Raft or a cluster. The observable state is primarily RocksDB table layout and Prometheus-style test counters, not client-visible values.

## Dependencies and Integration Points
This suite touches `engine_rocks::RocksEngine`, `engine_traits::MiscExt`, raw API v2 key/value encoding, the server GC worker's compaction filter, RocksDB file-level metadata helpers, and TiKV's `DbConfig`. It tests a lower-level prerequisite for raw TTL/GC efficiency rather than a user-facing storage command.

## Risks and Edge Cases
The fragile points are RocksDB level placement, file naming, and metric expectations. The tests disable automatic compaction to make table layout deterministic. Any change in raw table-property statistics, level selection, or compaction-filter metric accounting can change the expected perform/skip counts.

## Test Signals
The test signal is exact metric movement: perform counts increase whenever the raw compaction filter is invoked, while skip counts increase when `check_need_gc` rejects filtering because the safepoint is too low or the version/row ratio does not justify non-bottommost filtering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_table_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_titan.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_titan.rs

## Purpose
`test_titan.rs` verifies that a node can disable Titan after blob-index records remain in SST files because peer-removal cleanup was interrupted. It models a dangerous storage-engine transition: data has older RocksDB versions that still refer to Titan blob files, but TiKV later runs with Titan disabled and should not crash or evaluate obsolete blob references incorrectly.

## Important APIs, Types, and Functions
The test uses a `new_node_cluster`, RocksDB/Titan configuration fields, `BlobRunMode::Fallback`, manual compaction APIs (`flush_cf`, `compact_range_cf`, `compact_files_in_range_cf`), RocksDB properties such as `rocksdb.num-files-at-level6`, `rocksdb.num-files-at-level5`, and `rocksdb.titandb.num-live-blob-file`, and PD peer removal/addition helpers.

## Control Flow
The cluster starts with Titan enabled, auto compactions disabled, large default-CF values routed to blob files, and smaller values kept in SST files. The test splits the initial region, writes a large `k1` value and smaller `k3`, flushes and compacts store 3 so level 6 contains both a blob reference and a normal value, then restarts store 3 in Titan fallback mode to force blob GC to reclaim the live blob file.

After fallback GC writes a replacement value into a higher level, the test restarts store 3 with Titan disabled. It injects `after_delete_files_in_range` while removing the peer to simulate cleanup deleting a fully covered SST file but leaving an older lower-level SST containing the obsolete blob reference. The peer is added back after the failpoint is removed, leadership moves to that peer, and large-value reads/writes are verified.

## State and Persistence Behavior
This test intentionally manipulates persistent RocksDB/Titan layout. It checks file counts in level 5 and level 6, blob-file live counts, region data cleanup, and restart behavior across Titan enabled, fallback, and disabled modes. The key persistence invariant is that obsolete blob references in older SST files must remain harmless after Titan is turned off.

## Dependencies and Integration Points
The suite integrates raftstore peer lifecycle, RocksDB manual compaction, Titan blob storage properties, region split/remove/add flows through PD, and failpoint-driven partial cleanup. It is a narrow regression test for the interaction between peer data cleanup and storage-engine configuration migration.

## Risks and Edge Cases
The critical risk is resurrecting or reading an obsolete blob-index key after delete-range/delete-file cleanup has removed a newer deletion or replacement record. Because the test depends on RocksDB levels and Titan GC timing, it loops while waiting for blob-file reclamation and disables auto compactions to keep layout stable.

## Test Signals
Passing requires the expected file/blob properties at each phase, successful peer re-addition, successful read of the original large `k1` value, successful write/read of another large value after Titan is disabled, and no TiKV crash while obsolete blob references remain in SST files.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_titan.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_transaction.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_transaction.rs

## Purpose
`test_transaction.rs` exercises failpoint-sensitive MVCC transaction invariants below and around the storage scheduler. It concentrates on async-commit max-ts ordering, memory-lock visibility, prewrite lock lifetime, pessimistic lock epoch validation, read-index behavior with max timestamp, proposal/leadership races, GC/last-change reads, and preventing forwarded proposals from applying twice.

## Important APIs, Types, and Functions
The suite uses `TestEngineBuilder`, `TestStorageBuilderApiV1`, `MockLockManager`, storage commands from `storage::txn::commands`, MVCC test helpers (`must_prewrite_put`, `must_commit`, `must_rollback`, `must_locked`), `ConcurrencyManager` checks, `TikvClient` RPCs, and raftstore cluster helpers. `lock_release_test!` generates two tests for lock lifetime on prewrite success/failure. Local helpers `must_put` and `must_delete` call the lower-level `Engine` async write API.

Important failpoints include `prewrite`, `commit`, `pessimistic_prewrite`, `before-set-lock-in-memory`, `after-snapshot`, `before-storage-check-memory-locks`, `rockskv_async_write`, `after_prewrite_one_key`, `acquire_pessimistic_lock`, `invalidate_locks_before_transfer_leader`, `on_apply_write_cmd`, `after_propose_pending_writes`, `before_get_write_in_next_last_change_info`, and `on_peer_collect_message_2`.

## Control Flow
The early tests inject simple transaction failpoints into prewrite, commit, and pessimistic prewrite to verify errors do not poison later successful writes. The max-ts tests deliberately pause between snapshot acquisition, max-ts update, memory-lock insertion, and memory-lock scans to ensure readers either see a lock or force `min_commit_ts` above the read timestamp. The generated lock-lifetime tests verify that memory locks appear only while a prewrite is in progress and are dropped both on success and write failure.

Async-commit fallback tests update the concurrency manager's max timestamp in the middle of a multi-key prewrite and assert that only safe locks keep async-commit metadata. Pessimistic-lock tests pause RPC processing while leaders transfer or while in-memory lock tables transition to `TransferringLeader`, asserting either stale-command errors or no writes to an unavailable memory table. The read-index test blocks apply on the leader, reads from another replica with max timestamp, and expects a lock error sourced from the memory lock that has not yet been dropped.

The proposal tests construct joint configuration changes and network filters so prewrite proposals race transfer leader and conf changes. The final `test_forbid_forward_propose` creates a higher-term raft message between validation and proposal, then verifies the failed forwarded proposal does not reapply after a retry.

## State and Persistence Behavior
The suite inspects memory locks through the concurrency manager, persisted lock CF records through `must_locked` and `scan_lock`, Raftstore in-memory lock tables via snapshot extensions, and final persisted key values through cluster reads. It relies on the rule that max-ts updates, memory-lock insertion, and storage snapshots must be ordered so async commit never returns a commit timestamp that can be missed by a concurrent reader.

## Dependencies and Integration Points
Dependencies include storage MVCC internals, gRPC KV RPC types, raftstore v1/v2 clusters, raft message filtering, GC-by-compact, `LocksStatus`, `WriteData`/`WriteEvent` async writes, and PD conf-change helpers. The test file bridges storage-layer transaction logic and raft proposal semantics.

## Risks and Edge Cases
The highest-risk areas are reader/write races around max timestamp, memory lock leaks after failed writes, duplicate prewrite idempotency after falling back from async commit, stale command detection for pipelined pessimistic locks, proposal forwarding under term changes, and GC removing rollback metadata while last-change information is being computed.

## Test Signals
Expected signals include exact `min_commit_ts` values such as `41` and `101`, absence of leaked memory locks, persisted locks with async-commit metadata only where safe, stale-command errors after epoch/term changes, `KeyIsLocked` from read-index max-ts reads, successful demotion/leader transfer in concurrent conf-change scenarios, GC-preserved last-change value return, and final absence of a key after the double-proposal guard.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_transaction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_transfer_leader.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_transfer_leader.rs

## Purpose
`test_transfer_leader.rs` validates leader-transfer correctness under slow apply, unsynced max timestamp, pending lock cleanup, entry-cache warmup, long-uncommitted proposal checking, and metadata changes that have applied on a transferee before they apply on the current leader. It is a failpoint-heavy Raftstore integration suite for safe leadership movement.

## Important APIs, Types, and Functions
The suite uses node and server clusters, `TikvClient` RPCs, `PdClient`, `RegionPacketFilter`, `Callback`, raft `MessageType::MsgTransferLeader` and `MsgAppend`, configuration helpers like `configure_for_lease_read`, and storage snapshots with transaction extensions. It constructs `PessimisticLock` records directly in a region's in-memory lock table and uses `CF_LOCK` reads to verify cleanup.

Macros provide reusable scenarios: `test_delete_lock_proposed_after_proposing_locks_impl!` drives cleanup commands across transfer attempts, `run_cluster_for_test_warmup_entry_cache!` creates a lagging follower and compacted leader entry cache, and `run_cluster_and_warm_up_cache_for_store2!` verifies cache warmup and transfer ack timing. `prevent_from_gc_raft_log` configures raft log retention for warmup tests.

## Control Flow
The opening tests reject transfer to a slow-applying peer, reject async-commit prewrites until a new leader synchronizes max timestamp, and ensure lock cleanup still completes when transfer-leader messages arrive before or after the cleanup command is proposed. `test_read_lock_after_become_follower` verifies that a prewrite that read an in-memory pessimistic lock before becoming follower returns stale-command rather than a misleading lock-not-found error.

The entry-cache tests create a follower that has missed many entries, then transfer leadership and inspect transfer messages, warmup failpoints, ack callbacks, and cache retention. They cover correct transfer message index, warmup start beyond last index, compacted warmup ranges, disabled warmup, timeout too long/short, successful warmup with and without becoming leader, single ack behavior, and leader-only long-uncommitted proposal ticks.

The final block uses paused apply failpoints to test transfer eligibility when the transferee has applied conf change, learner demotion, split, merge, or witness switch metadata ahead of the current leader. It ensures transfers are rejected to removed/learner/witness or unapplied peers and allowed to peers whose local metadata is safe.

## State and Persistence Behavior
The suite observes raft apply progress, raft local state indexes, truncated indexes, entry-cache state, in-memory pessimistic locks, lock CF deletion, PD region metadata, peer roles, witness flags, and persisted values on new leaders. The warmup tests are stateful around raft log retention and compaction, while metadata tests depend on PD heartbeats and region epoch/peer role state.

## Dependencies and Integration Points
It integrates raftstore leadership transfer, PD operators, raft log GC, entry-cache warmup worker, pessimistic lock proposal paths, storage snapshot extensions, region split/merge/conf-change machinery, and witness switching. Many tests are parameterized over raftstore v1 and v2 clusters.

## Risks and Edge Cases
The key risks are transferring to a lagging peer that cannot serve promptly, losing lock cleanup during leadership movement, accepting writes before max-ts sync, acking transfer before cache warmup is valid, stale warmup state retaining cache incorrectly, and using current-leader stale metadata instead of transferee-applied metadata for transfer safety decisions.

## Test Signals
Signals include unchanged leader when transfer is unsafe, successful writes on the current or new leader, absence of lock CF entries after cleanup, receipt of warmup failpoint callbacks and transfer ack messages, exact replicated/truncated index comparisons, missing long-uncommitted ticks on followers, PD leader checks for accepted/rejected transferees, and final peer role/witness metadata in PD.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_transfer_leader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_ttl.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_ttl.rs

## Purpose
`test_ttl.rs` validates raw-key TTL behavior for API v1 TTL mode and API v2. It covers file-level TTL checking, compaction-filter deletion, snapshot reads, iterator filtering, and raw batch put/get-TTL storage APIs under a controlled logical current timestamp.

## Important APIs, Types, and Functions
The suite uses `test_kv_format_impl!` to run implementations over `ApiV1Ttl` and `ApiV2`, `RawValue` encoding, `RawEncodeSnapshot`, storage raw APIs, `TestGcRunner`, `check_ttl_and_compact_files`, `GcTask::RawGcKeys`, RocksDB compaction APIs, `Iterator`, `Peekable`, and `SyncMutable`. `make_raw_key<F>` encodes a raw key and optional timestamp into TiKV data-key form.

## Control Flow
Every test fixes `ttl_current_ts` at `100`. `test_ttl_checker_impl` writes multiple flushed SST batches with expired, unexpired, and no-TTL records at commit timestamp `100`, then calls `check_ttl_and_compact_files` over selected key ranges. In API v2 it consumes emitted `RawGcKeys` tasks and deletes the encoded keys to model the real raw GC worker.

`test_ttl_compaction_filter_impl` writes expired and unexpired raw values, triggers manual compaction, and verifies only expired values are removed. `test_ttl_snapshot_impl` writes duplicate raw values and checks that snapshot `get` returns only the latest non-expired visible value and that `get_key_ttl_cf` returns remaining TTL, `None` for expired, and `Some(0)` for no TTL. `test_ttl_iterator_impl` validates forward, backward, seek, and seek-for-prev iteration skip expired keys and expired latest versions. `test_stoarge_raw_batch_put_ttl_impl` writes key/value/TTL arrays through `raw_batch_put` and reads both value and TTL back.

## State and Persistence Behavior
The tests use real RocksDB temp engines for compaction and snapshot cases, plus in-memory test storage for raw batch APIs. Persisted raw values encode user value, optional expire timestamp, and delete marker. The visible state is filtered at compaction time, snapshot point-read time, and iterator traversal time.

## Dependencies and Integration Points
This file integrates API-version-specific key/value encoding, RocksDB default CF, TiKV raw storage encoding, server GC worker TTL scanning, raw storage commands, and the raw snapshot wrapper. It is adjacent to raw GC/table-property tests but focuses on TTL visibility and deletion semantics.

## Risks and Edge Cases
Important edge cases are duplicate raw versions where the newest version is expired or not expired, no-TTL records that must remain visible, API v2 timestamp-suffixed raw keys, bounded compaction ranges, and iterator seeks that land on expired records and must advance to the next valid key.

## Test Signals
Passing signals are precise presence/absence of RocksDB keys after compaction, expected snapshot values and TTLs, iterator order `key1` then `key3` with expired keys skipped, seek behavior around hidden keys, and `raw_get_key_ttl` returning the same TTLs supplied to `raw_batch_put`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_ttl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_unsafe_recovery.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_unsafe_recovery.rs

## Purpose
`test_unsafe_recovery.rs` validates TiKV unsafe recovery behavior when quorum is lost, peers have unapplied entries or snapshots, recovery plans are resent, merges must be rolled back, and apply-before-persist has created divergent persisted raft state. The suite ensures stores do not report or execute recovery plans until local state is safe and that demotion/create results are reported accurately.

## Important APIs, Types, and Functions
The file uses raftstore clusters, PD recovery plan APIs (`pdpb::RecoveryPlan`, `DemoteFailedVoters`, created `metapb::Region`s), `must_enter_force_leader`, store heartbeat triggers, raft/apply state reads from `CF_RAFT`, `find_peer`, region split/merge helpers, and failpoints such as `on_handle_apply_store_1`, `unsafe_recovery_state_timeout`, `region_apply_snap`, `on_schedule_merge`, and `raft_before_persist_on_store_1`.

## Control Flow
The reporting tests block raft apply or snapshot apply, stop enough nodes to lose quorum, set an unsafe recovery plan, and verify PD receives no store report until apply catches up. The timeout test forces state timeout, unblocks apply, verifies the first plan is aborted, then resends the plan and observes a report.

`test_unsafe_recovery_execution_result_report` splits a region, removes a local peer from one side, constructs a plan that both demotes failed voters and creates a replacement region, blocks apply during execution, and then checks the returned peer reports. `test_unsafe_recovery_wait_for_snapshot_apply` compacts logs, restarts a lagging peer so it applies a snapshot, and ensures reporting waits until snapshot apply completes.

The demotion and merge tests enter force-leader mode after quorum loss, apply or resend demotion plans, and verify failed voters become learners. The rollback-merge test blocks merge commit, removes one right-region peer, loses quorum, enters force leader on the left region, allows rollback merge, and then applies demotion. The apply-before-persist test skips raft log persistence on store 1 while entries are applied, isolates store 2 for part of the log, restarts nodes, triggers reporting, force-leads store 1, demotes failed voters, and verifies store 2 eventually contains all data.

## State and Persistence Behavior
The suite heavily inspects durable raft and apply state. It reads `RaftApplyState` from KV `CF_RAFT`, `RaftLocalState` from the raft engine, compares applied and committed indexes across stores, checks PD region peer roles, and verifies data after recovery. It explicitly tests windows where apply progress is ahead of persist progress and where snapshots or unapplied entries make reporting unsafe.

## Dependencies and Integration Points
It integrates raftstore unsafe recovery state machines, PD recovery plan delivery/reporting, force-leader mode, snapshot apply, raft log GC, merge rollback, region creation, learner demotion, store heartbeats, and v1/v2 raftstore variants. The final apply-before-persist case is limited to classic raftstore because the feature is not supported by raftstore v2 in that test.

## Risks and Edge Cases
The key risks are reporting stale state before unapplied entries are applied, executing the same demotion plan twice, losing merge rollback state during quorum loss, demoting peers before force-leader state is valid, and reconciling applied-but-not-persisted entries after restart. Timeouts and resend behavior are also critical because PD may redeliver plans.

## Test Signals
Signals include no PD store report while apply/snapshot apply is paused, reports appearing after release, aborted plans not reporting until resent, peer reports containing created region 101 and demoted failed voters, PD regions showing failed voters as learners, applied/commit index relationships across stores, and final data visibility such as store 2 reading `k29 = v3`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_unsafe_recovery.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_witness.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_witness.rs

## Purpose
`test_witness.rs` validates witness-peer behavior in raftstore: local reader errors, raft log GC with witness peers, witness-to-non-witness snapshot recovery, non-witness availability notification, replica reads during conversion, witness leaders transferring out, and snapshot generation invalidation when a leader becomes witness.

## Important APIs, Types, and Functions
The suite uses `new_server_cluster`, PD witness switching helpers (`must_switch_witnesses`, `switch_witnesses`), `find_peer`, raft apply state reads from `keys::apply_state_key`, replica read requests, raft command constructors, and cluster filters such as isolation and snapshot-generation failpoints. `test_non_witness_availability` parameterizes pull and push availability flows, and `must_get_error_is_witness` asserts raft command responses contain `errorpb::IsWitness`.

## Control Flow
The first two tests remove a peer while a region update is paused and issue replica reads against the stale peer. If the peer had been switched to witness, the local reader returns `IsWitness`; without witness mode it returns a normal error without `is_witness`.

The raft-log GC tests switch one peer to witness, stop another follower, write enough data to exceed GC limits, and verify the witness truncated index does not advance until the voter replicated index can be pulled after the follower returns. A reboot variant restarts the witness before checking GC advancement.

Snapshot recovery tests switch a witness back to non-witness while blocking request/generate snapshot, verify the peer remains pending and lacks data, then unblock through restart or term change and check data arrives. Availability tests block either leader polling or follower notification and still require the non-witness to become available after snapshot. The replica-read test confirms reads against a converting non-witness still return `IsWitness` until snapshot apply completes.

The final leader tests force a future witness to become raft leader before applying the witness switch, then verify it rejects reads/writes/read-index with `IsWitness` and transfers leadership to a real voter. The snapshot-generation test makes a leader generate a snapshot for an isolated peer, switches that leader to witness, invalidates generation, rejects unsafe transfer to the lagging peer, then transfers to an eligible peer.

## State and Persistence Behavior
The suite inspects persisted raft apply truncated indexes across all stores, PD pending peers, region witness flags, local RocksDB data presence on witness/non-witness stores, and current region leader. Witness peers intentionally do not hold replicated user data, so `must_get_none` before snapshot and `must_get_equal` after non-witness recovery are central state checks.

## Dependencies and Integration Points
It integrates PD witness role changes, local reader/replica read handling, raft log GC and voter replicated-index exchange, snapshot request/generation, pending-peer tracking, raft leadership transfer, and command rejection paths. Failpoints such as `change_peer_after_update_region_store_3`, `on_raft_gc_log_tick`, `ignore request snapshot`, `ignore generate snapshot`, `before_exec_batch_switch_witness`, `before_region_gen_snap`, and `ignore_forbid_leader_to_be_witness` drive the edge cases.

## Risks and Edge Cases
The main risks are serving stale reads from witness peers, truncating raft logs before all voters can catch up, failing to request snapshots after witness conversion, leaving non-witness peers pending forever, allowing a witness leader to serve commands, and repeatedly generating invalid snapshots after a leader becomes witness.

## Test Signals
Passing signals include explicit `IsWitness` errors where expected, absence of `IsWitness` when witness mode was not enabled, truncated index movement only after voter catch-up, pending-peer count dropping to zero after snapshot, successful reads from recovered non-witness peers, command rejection while leader is witness, safe transfer to non-witness voters, and retained data such as `k9` after leadership transfer.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_witness.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/mod.rs -->
# sources/storage-engines/tikv/tests/failpoints/mod.rs

## Purpose
`mod.rs` is the crate root for TiKV failpoint tests. It enables nightly features needed by the test suite, installs the custom failpoint test runner, imports global logging macros, and exposes the `cases` module containing the actual failpoint test files.

## Important APIs, Types, and Functions
The file uses crate attributes `#![feature(box_patterns)]`, `#![feature(test)]`, `#![feature(custom_test_frameworks)]`, `#![test_runner(test_util::run_failpoint_tests)]`, and `#![recursion_limit = "100"]`. It declares `#[macro_use] extern crate slog_global;` and `mod cases;`.

## Control Flow
There is no runtime business logic in this file. Cargo/rustc compile it as the failpoints integration-test crate. The custom test framework routes test execution through `test_util::run_failpoint_tests`, which is important because failpoint tests often need special setup/teardown and logging.

## State and Persistence Behavior
This module owns no persistent state. Its state impact is test harness configuration: all nested failpoint cases run under the configured custom runner and with logging macros available.

## Dependencies and Integration Points
It integrates the failpoint test crate with `test_util`, `slog_global`, and the `cases` module tree. The `box_patterns` feature is required by many tests that pattern-match nested storage errors using boxed error enums.

## Risks and Edge Cases
Changing feature gates or the test runner can break many failpoint suites at compile time. Removing `slog_global` macro import may break tests that log through macros. Lowering the recursion limit could affect macro-heavy parameterized test cases.

## Test Signals
The signal is compile/test discovery rather than assertions in this file: all failpoint case modules should build, and the custom runner should execute them with failpoints correctly configured.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/backup/disk_snap.rs -->
# sources/storage-engines/tikv/tests/integrations/backup/disk_snap.rs

## Purpose
`disk_snap.rs` tests disk snapshot backup's coprocessor guard. While a disk snapshot backup prepare call is active, region operations that would invalidate or conflict with the backup, such as split, conf change, transfer leader, and merge, must be rejected or suspended. It also tests wait-apply behavior so backup preparation only proceeds after relevant writes are applied.

## Important APIs, Types, and Functions
The suite uses `test_backup::disk_snap::Suite`, prepare/finalize call handles, assertions `assert_success`, `assert_failure`, `assert_failure_because`, and `must_wait_apply_success`, plus raftstore `RegionPacketFilter`, `Simulator`, `Callback::write_ext`, and `must_contains_error`. It manually builds simple `RaftCmdRequest` put commands for wait-apply coverage.

## Control Flow
`test_basic` starts a prepare call and confirms split returns a suspended backup error. `test_conf_change` first removes a peer before backup, then prepares backup calls on all stores and verifies another peer removal is rejected by the coprocessor until all calls finalize. `test_transfer_leader` similarly rejects transfer while prepare calls are active and allows it after finalize. `test_prepare_merge` rejects merge during a prepared backup. `test_abort_last_one` starts a second prepare on the same store and verifies the first stream is aborted while the second can finalize.

`test_wait_apply` splits the keyspace into many regions, isolates one region's append messages, asynchronously proposes a write to every region, starts backup prepare on the leader store, and sends a wait-apply request for all regions. It expects every non-isolated region to report success only after the write is observable, then clears filters and expects the isolated region to complete.

## State and Persistence Behavior
The suite observes cluster metadata changes, leader transfer results, prepared backup call state, pending apply progress, and user data visibility after wait-apply. It does not inspect backup files; it focuses on the control plane suspension and apply barrier that protect snapshot consistency.

## Dependencies and Integration Points
It integrates BR/disk snapshot backup test helpers with raftstore admin operations, raft command callbacks, network filters, region split/merge/conf-change APIs, and coprocessor rejection messages. It is an integration test rather than a failpoint test.

## Risks and Edge Cases
The main risks are allowing region topology or leadership changes during backup prepare, failing to abort superseded prepare streams, and reporting wait-apply success before writes are locally applied and readable. The wait-apply test is sensitive to all split-region leaders being on the same store and asserts that precondition.

## Test Signals
Passing signals include suspended/rejected error strings while backup prepare is active, successful operations after finalize, aborted first prepare stream when a second starts, wait-apply region ids matching expected regions, immediate data visibility for completed regions, and eventual completion for the previously isolated region after network filters are cleared.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/backup/disk_snap.rs -->
