# subset-b-008840 Research

Grouped research report for TiKV raftstore-v2 operation lifecycle, PD, query, and ready handling sources. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/life.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/life.rs

## Purpose
Implements raftstore-v2 peer creation, peer destruction, tombstone handling, stale peer garbage collection, merge-source destruction coordination, availability probes, and disk-full proposal gating. The module explains the v2 lifecycle model: peers are created only by bootstrap, store-level raft messages, or split-init via a store-created uninitialized FSM; peers are destroyed only after removal/merge/tombstone/larger-peer-id paths persist a tombstone record.

## Important APIs, Types, And Functions
`DestroyProgress` tracks destroy state from `None` to `WaitReady`, `Destroying`, and `Destroyed`, optionally carrying the triggering raft message used to recreate a newer peer after destruction. `AbnormalPeerContext` stores pending peers, down peers, disk-full peers, and whether a dangerous majority set exists. `GcPeerContext` stores peer ids confirmed as destroyed. Store-level entry points include `Store::on_split_init`, `Store::on_ask_commit_merge`, and `Store::on_raft_message`. Peer-level entry points include `maybe_schedule_gc_peer_tick`, `maybe_gc_sender`, `on_tombstone_message`, `on_gc_peer_request`, `on_gc_peer_response`, `on_gc_peer_tick`, `check_proposal_with_disk_full_opt`, `refill_disk_full_peers`, `mark_for_destroy`, `postponed_destroy`, `start_destroy`, and `finish_destroy`.

## Control Flow
Store-level raft messages are first attempted against an existing peer mailbox. If the mailbox is disconnected, the store validates store id, epoch, tombstone state, merge target state, and disk-full constraints before creating an uninitialized `Storage` and `PeerFsm`, registering it with the router, and forwarding the original message when it has a valid sender. Split initialization creates the recipient peer through an empty split message, then sends `PeerMsg::SplitInit`. Tombstone and larger-peer-id messages mark an existing peer for asynchronous destruction. GC ticks are leader-only: removed peers receive direct tombstone messages, while merged source peers are checked through target peers before source destruction is forwarded.

## State And Persistence Behavior
Destroy is deliberately asynchronous. `mark_for_destroy` only moves the peer into `WaitReady` and forces a ready round. `start_destroy` waits until pending apply and tombstone-tablet work are safe, cleans raft-engine state through the extra write batch, writes `PeerState::Tombstone` at the applied index, records tombstone tablet cleanup, and moves to `Destroying`. `finish_destroy` runs only after the destroy write is persisted; it removes store metadata, reader delegates, read progress, tablet registry entries, closes the router mailbox, clears pending reads and proposals, and dispatches any saved triggering message. Removed and merged peer records remain in region state until an `UpdateGcPeer` admin proposal removes confirmed ids.

## Dependencies And Integration Points
The module depends on raft engine region state reads, `Storage::uninit`, `PeerFsm::new`, router registration, raftstore transport, split and merge command helpers, tablet registry cleanup, disk usage state from the store context, proposal control, apply proposal callbacks, and PD heartbeat side effects. It integrates tightly with `ready/mod.rs` because ready handling is where destroy writes are built and finalized.

## Risks And Edge Cases
The main risks are lifecycle races: split-init racing with initial raft messages, recreating a peer after a larger id tombstones the old peer, forwarding merge-source GC only after target merge completion, and preventing tablet path races during destroy. Disk-full logic is also safety-sensitive because it can suppress proposals, transfer leadership, reduce raft inflight messages to disk-full peers, and keep a potential quorum alive. `check_if_to_peer_destroyed` can panic if the raft engine reports a non-tombstone state for a peer that does not exist in memory.

## Test Signals
No local test module appears in this file. Observable signals are failpoint coverage around split-init races, raft metrics for dropped messages, tombstone and GC logs, disk-full proposal errors, `UpdateGcPeer` admin proposals, and integration tests that exercise split, merge, peer removal, unsafe recovery destroy, and disk-full behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/life.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/misc.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/misc.rs

## Purpose
Handles miscellaneous store-level maintenance, currently snapshot garbage collection for tablet snapshots.

## Important APIs, Types, And Functions
`StoreFsmDelegate::on_snapshot_gc` is the tick handler. `Store::on_snapshot_gc` lists snapshot paths from `snap_mgr`, parses them into `TabletSnapKey`, groups keys by region id, and routes `PeerMsg::SnapGc` to the owning peer.

## Control Flow
The store FSM tick calls the store helper, logs any cleanup-listing error, and reschedules `StoreTick::SnapGc` using `snap_mgr_gc_tick_interval`. For each region group, the store router attempts to send the cleanup message. If the peer mailbox is disconnected and the store is not shutting down, the keys are scheduled directly to the tablet worker as `tablet::Task::SnapGc`.

## State And Persistence Behavior
The file does not mutate raft metadata directly. Snapshot files are external filesystem artifacts owned by the snapshot manager or tablet worker. Persistence behavior is cleanup-oriented: stale snapshot files are discovered and later deleted by peer or tablet-worker handling.

## Dependencies And Integration Points
Depends on `TabletSnapKey::from_path`, `snap_mgr.list_snapshot`, the peer router, `PeerMsg::SnapGc`, and the tablet worker scheduler. It integrates with peer snapshot lifecycle and store tick scheduling.

## Risks And Edge Cases
Malformed snapshot paths propagate as errors from `TabletSnapKey::from_path`. Router disconnection is ambiguous between a removed peer and shutdown; shutdown suppresses fallback work, while non-shutdown routes cleanup to the tablet worker. Grouping by region is important to avoid sending unrelated snapshot keys to one peer.

## Test Signals
There are no direct tests in this file. Signals are snapshot manager directory contents after GC ticks, warnings for cleanup failures, and tablet worker `SnapGc` task scheduling when a peer is absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/mod.rs

## Purpose
Defines the operation module boundary for raftstore-v2 and re-exports the command, lifecycle, ready, query, transaction extension, disk snapshot backup, and unsafe recovery pieces used by the rest of the crate.

## Important APIs, Types, And Functions
Top-level submodules include `bucket`, `command`, `disk_snapshot_backup`, `life`, `misc`, `pd`, `query`, `ready`, `txn_ext`, and `unsafe_recovery`. Public re-exports expose command structures such as `CommittedEntries`, `CompactLogContext`, split and merge helpers, `DestroyProgress`, `AbnormalPeerContext`, `GcPeerContext`, and ready types such as `ApplyTrace`, `AsyncWriter`, `ReplayWatch`, `SnapState`, and `StateStorage`. Crate-visible exports expose `SplitInit`, `LocalReader`, `ReadDelegatePair`, `SharedReadTablet`, and `TxnContext`.

## Control Flow
The file has no runtime control flow outside test utilities. It establishes import paths and module ownership so peer/store FSM code can refer to operation helpers through a stable facade.

## State And Persistence Behavior
The module root does not persist state. Its re-exports expose persistence-sensitive helpers, especially command apply state, lifecycle tombstone state, and ready apply-trace state.

## Dependencies And Integration Points
It is the integration point for raftstore-v2 operation code. Test utilities provide `create_tmp_importer`, `MockReporter`, `new_put_entry`, and `new_delete_range_entry`, which support apply/query tests by building encoded raft log entries and receiving apply results.

## Risks And Edge Cases
The main risk is API surface drift: moving or renaming re-exports can break consumers outside this directory. The test utilities encode requests using `SimpleWriteEncoder` and region headers, so they must stay aligned with command decoding.

## Test Signals
No tests are defined directly here, but `test_util` is used by operation submodule tests such as capture/apply-trace tests. Compilation is the primary signal for export correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/pd.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/pd.rs

## Purpose
Implements raftstore-v2 interactions with PD: store heartbeats, region heartbeats, pending/down peer reporting, split id allocation requests, split reporting, and peer-destroy notifications.

## Important APIs, Types, And Functions
`StoreFsmDelegate::on_pd_store_heartbeat` schedules periodic store heartbeats. `Store::store_heartbeat_pd` builds `pdpb::StoreStats`. `PeerFsmDelegate::on_pd_heartbeat` updates peer statistics and sends region heartbeats from leaders. `Peer::region_heartbeat_pd`, `collect_pending_peers`, `destroy_peer_pd`, `ask_batch_split_pd`, and `report_batch_split_pd` are the peer-facing PD APIs.

## Control Flow
Store heartbeat collection locks store metadata to count reader delegates, reads snapshot manager sending/receiving counts and traffic stats, swaps global written bytes/keys counters to zero, and schedules `pd::Task::StoreHeartbeat`. Region heartbeat runs on leaders after peer statistics refresh. It sends region metadata, leader peer, down peers, pending peers, write flow, approximate size/keys, and wait-data peers through `pd::Task::RegionHeartbeat`.

## State And Persistence Behavior
This file does not directly persist raft or tablet state. It derives report state from in-memory store metadata, snapshot manager counters, raft progress, apply truncated index, split-flow estimates, and peer stats. The global write counters are consumed through atomic `swap(0)`, making heartbeat reporting destructive for that interval.

## Dependencies And Integration Points
Depends on PD worker tasks, raft progress status, snapshot manager stats, `STORE_SNAPSHOT_TRAFFIC_GAUGE_VEC`, split-flow control, abnormal peer context, and global store stats. PD responses to split requests and heartbeats influence scheduling and membership outside this file.

## Risks And Edge Cases
Pending-peer detection treats progress matched below truncated index as pending, including matched zero, because merge safety requires all target peers to exist. If peer cache lookup fails under `dev_assert`, it panics; otherwise it logs. Scheduler failures only log errors, so missed heartbeats are retried by future ticks. Store heartbeat start time is cast to `u32`.

## Test Signals
No direct tests are present. Signals include PD task scheduling, store snapshot gauges, pending peer logs/metrics, the `schedule_check_split` failpoint after region heartbeat, and integration tests around split, merge, and PD heartbeat reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/pd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/capture.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/capture.rs

## Purpose
Implements capture-change support for applied command observation, used by CDC, resolved-ts, and PITR observers to obtain a consistent snapshot and then receive subsequent applied command batches.

## Important APIs, Types, And Functions
`PeerFsmDelegate::on_leader_callback` builds a read-index request for the current leader and routes it through query handling. `PeerFsmDelegate::on_capture_change` waits for the leader read callback and then schedules `ApplyTask::CaptureApply`. `Apply::on_capture_apply` validates observer freshness and region epoch, flushes prior writes, creates a `RegionSnapshot`, updates observe ids and observe level, and returns the snapshot. `Apply::observe_apply` records applied commands when observation is enabled. `Apply::flush_observed_apply` emits a `CmdBatch` to the coprocessor host.

## Control Flow
Capture starts on the peer FSM by issuing a leader read callback so the capture point is sequenced with raft/query state. The callback reports query errors immediately. On success it sends the capture change to the apply scheduler. Apply-side handling rejects stale observer ids, verifies the requested epoch against the current region, flushes current apply writes so the snapshot includes all prior modifications, builds the region snapshot at the current applied index, updates the requested observer id, recomputes observe level, and returns the snapshot through the callback. Later apply operations are recorded and flushed in batches to observers.

## State And Persistence Behavior
`on_capture_apply` forces an apply writebatch flush before snapshot creation. It mutates in-memory observe metadata (`cdc_id`, `rts_id`, or `pitr_id`) and observe level, but does not add raft log entries. Observed commands are buffered in memory and drained on flush; large buffers shrink back to `SHRINK_PENDING_CMD_QUEUE_CAP`.

## Dependencies And Integration Points
Depends on query read-index sequencing, apply scheduler, `ChangeObserver`, `ObserveHandle`, `ObserverType`, `RegionSnapshot`, epoch comparison, coprocessor command observation, `WriteBatchFlags::FLASHBACK`, and the router `CaptureChange` message.

## Risks And Edge Cases
Stale capture commands must be rejected or old clients could rewind observer ids. Epoch mismatch returns an error instead of a snapshot. Missing apply scheduler is converted to `RegionNotFound`. Flashback regions require a special query flag to allow capture. The snapshot must be taken after flushing prior writes, otherwise the observer could miss data before the capture point.

## Test Signals
The local `test_capture_apply` builds an apply instance, applies a put, captures, applies another put, and verifies the snapshot sees only the first put while the observer receives the second command. The `raft_on_capture_change` failpoint gives additional integration-test control.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/capture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/lease.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/lease.rs

## Purpose
Implements leader lease and leader-side read-index behavior for raftstore-v2 queries. It decides when reads can be answered under lease, when quorum read-index is required, and how lease state is propagated to local read delegates.

## Important APIs, Types, And Functions
`Peer::on_step_read_index` handles incoming read-index messages when a leader has a valid lease. `pre_read_index` blocks unsafe read-index during split or merge. `read_index_leader` proposes or amends leader read-index requests. `respond_read_index` returns read responses after read-index completion. `maybe_renew_leader_lease`, `expire_lease_on_became_follower`, `maybe_update_read_progress`, `inspect_lease`, `try_renew_leader_lease`, and `need_renew_lease_at` maintain lease state. `PeerFsmDelegate::on_check_leader_lease_tick` periodically renews the lease.

## Control Flow
For a leader read, the peer first checks whether the latest pending read can be amended under the current lease. If so, it batches the command with that read and records the local committed index. Otherwise it calls raft `propose_read_index`, stores a `ReadIndexRequest`, and marks ready. If the lease is suspect, it proposes a no-op write to refresh the lease. Completed read-index requests bind tracker timing, recheck region epoch, merge locally recorded committed index with the batch read index, and return `QueryResult::Read`.

## State And Persistence Behavior
Lease state is in memory but published into `StoreMeta.readers` as `ReadProgress` so `LocalReader` can make local-read decisions. Leadership changes expire or renew lease state and update read delegates. Read-index requests are in-memory pending-read queue entries; they do not persist by themselves, although no-op writes used for lease renewal enter the raft log.

## Dependencies And Integration Points
Depends on raft-rs read-index APIs, `ReadIndexRequest`, `ReadProgress`, `ReadDelegate`, store metadata, proposal control, leader lease utilities, `SimpleWriteEncoder` for no-op writes, query channels, tracker metrics, and `PeerTick::CheckLeaderLease`.

## Risks And Edge Cases
The code deliberately uses peer-storage commit index rather than raft-rs committed index to avoid exposing reads beyond persisted/applied state. Split and merge states reject read-index to avoid stale range ownership. Epoch is checked again at response time because the region may split or merge while read-index is pending. A leader transfer marks lease suspect on `MsgTimeoutNow`, requiring explicit renewal. The `before_propose_readindex` failpoint can inject read-index failure.

## Test Signals
No local unit tests are in this file. Signals include read-index pending metrics, leader lease ticks, failpoint injection, local-reader tests that observe lease renewal effects, and integration tests for leader transfer, split/merge read safety, and read quorum behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/lease.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/local.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/local.rs

## Purpose
Implements the v2 local snapshot reader. It serves snapshot reads directly from a cached tablet when region validation, applied term, lease, and stale-read safe-ts checks allow; otherwise it redirects through the peer FSM to perform read-index and then retries.

## Important APIs, Types, And Functions
`MsgRouter` abstracts sending `PeerMsg` to a peer. `SharedReadTablet` owns a shareable tablet handle whose cached clone is deliberately short-lived. `LocalReader::snapshot` is the public async entry point. Internals include `pre_propose_raft_command`, `try_get_snapshot`, `try_to_renew_lease`, and `maybe_renew_lease_in_advance`. `CachedReadDelegate` pairs a `ReadDelegate` with a `SharedReadTablet`. `StoreMetaDelegate` implements `ReadExecutorProvider` for `LocalReaderCore`. `SnapRequestInspector` selects `ReadLocal`, `ReadIndex`, or `StaleRead`.

## Control Flow
`snapshot` first attempts local execution synchronously. Request validation fetches a cached delegate from store metadata, fills the tablet cache, verifies the request is exactly one `Snap`, and inspects policy. For local reads it snapshots the tablet before reading time, fences ordering, checks the remote leader lease, fills v2 snapshot metadata, and optionally sends an advance-renewal query. For stale reads it decodes the read timestamp from header flag data, checks safe-ts before and after snapshot acquisition, and returns the snapshot only if safe. For read-index policy or expired lease, it sends a read-quorum `PeerMsg::RaftQuery`, waits for a `QueryResult::Read`, clears `read_quorum`, and retries local snapshot acquisition.

## State And Persistence Behavior
The reader does not write persistent state. It reads from store metadata and tablet snapshots, attaches transaction extension state, term, txn extra op, bucket metadata, and v2 marker to the returned `RegionSnapshot`. `SharedReadTablet` drops the underlying optional tablet when the source wrapper is dropped, allowing stale tablets to be released even if clones exist. Safe-ts and leader lease are read from `ReadDelegate`/`RegionReadProgress`.

## Dependencies And Integration Points
Depends on `LocalReaderCore`, `ReadDelegate`, `RegionSnapshot`, store metadata readers, router query channels, `ReadProgress`, `TxnExt`, bucket metadata, `WriteBatchFlags::STALE_READ`, local read metrics, and tracker metrics. It is paired with lease handling in `query/lease.rs` and read progress updates in `query/mod.rs`.

## Risks And Edge Cases
The snapshot path must avoid reading from a stale tablet after epoch changes; failure to fill the tablet cache causes retry. Local reads require applied term equal to current term and a valid remote leader lease. Stale reads must check safe-ts both before and after snapshot acquisition. The retry limit of ten protects against infinite stale delegate loops but turns persistent churn into an internal error. Router full and disconnected errors are converted to server-busy or region-not-found responses.

## Test Signals
`test_read` covers unregistered regions, applied-term mismatch requiring read-index retry, lease expiration and renewal, tablet cache misses, read-quorum routing, and stale-read safe-ts failures/success. `test_read_delegate` checks that delegate tablet handles match expected tablet paths and are released after reader removal. Failpoints `perform_read_index` and `perform_read_local` force policy selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/local.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/mod.rs

## Purpose
Coordinates all raftstore-v2 query handling. It separates KV reads from status queries, chooses local read versus read-index policy, validates query requests, applies read states from raft ready, and updates read progress after apply.

## Important APIs, Types, And Functions
`PeerFsmDelegate::on_query` is the main peer-FSM entry point. `inspect_read` chooses `ReadLocal` or `ReadIndex`. `Peer::validate_query_msg`, `read_index`, `apply_reads`, `post_pending_read_index_on_replica`, `ready_to_handle_unsafe_replica_read`, `ready_to_handle_read`, `send_read_command`, `on_query_status`, `query_status`, `on_query_debug_info`, and `handle_read_on_apply` implement query behavior. The module also declares `capture`, `lease`, `local`, and `replica` submodules.

## Control Flow
Non-status queries are validated for allowed command types, store id, stale-read exclusion, leadership or replica-read permission, peer id, force-leader state, initialization, term, and region epoch. Leaders can answer locally if applied to current term and lease is valid; otherwise they use read-index. Followers use read-index for explicit read-index or replica reads. `apply_reads` consumes raft ready read states, advances leader or replica pending-read queues, renews leader lease after successful read state, and clears stale reads after role changes. After apply, leaders or followers reattempt pending reads that were blocked by apply progress.

## State And Persistence Behavior
Query state is in-memory: pending reads, read progress, leader lease, role state, and debug metadata. No query path writes durable state directly, but read-index and no-op lease renewal interact with raft ready and may produce persisted raft entries. `on_query_debug_info` synthesizes v2 commit index and term from in-memory/persisted raft log state because v2 does not persist them in the same shape as v1.

## Dependencies And Integration Points
Depends on raft ready read states, `ReadIndexContext`, `ReadProgress`, `RequestPolicy`, proposal control, raft metrics, local reader delegates, lease and replica modules, coprocessor host notifications, `RegionMeta`, and query/debug channels.

## Risks And Edge Cases
Read safety is guarded by multiple conditions: applied term must match current term, split and merge states suppress unsafe reads, prepare-merge prevents replica read, and follower replica reads must wait until applied index reaches read index. Read-index responses can be lost on followers, so addition requests are re-proposed. Region epoch is checked before serving read-index responses. Role changes silently drop uncommitted reads and update read progress.

## Test Signals
Direct tests are in submodules, especially `query/local.rs`. Additional signals include failpoint `on_applied_current_term`, read-index pending counts, invalid proposal metrics, status query responses, debug info contents, and integration tests for leader transfer, follower reads, split/merge, and region epoch validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/replica.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/replica.rs

## Purpose
Implements follower/replica read-index support for raftstore-v2, including retrying lost read-index requests and responding to replica reads once follower apply progress is safe.

## Important APIs, Types, And Functions
`Peer::retry_pending_reads` periodically retries pending follower read-index requests. `read_index_follower` proposes a follower read-index through raft. `respond_replica_read` returns successful replica-read or read-index responses. `respond_replica_read_error` reports the same error to every command batched in a pending read.

## Control Flow
Follower read-index first checks that a leader is known. It extracts any embedded read-index request payload, calls `propose_read_index`, stores a `ReadIndexRequest` in the pending queue, and marks ready. Retry logic checks that the peer is still a follower, pending reads need retry, and `pre_read_index` still permits reads; it then reissues raft `read_index` with the existing request context. Responses are emitted only after `query/mod.rs` determines that the follower has applied through the returned read index.

## State And Persistence Behavior
The file manages in-memory pending-read state only. Read-index itself is a raft protocol operation and does not persist local durable state directly. Tracker metrics record wait time from proposal to confirmation.

## Dependencies And Integration Points
Depends on raft leader id, `ReadIndexContext`, pending read queue, `propose_read_index`, `ReadResponse`, query channels, stale request notification, and configuration retry thresholds. It is called from query tick/ready handling in `ready/mod.rs` and `query/mod.rs`.

## Risks And Edge Cases
If no leader is known, reads fail with `NotLeader`. Read-index responses can be lost, so retry is required to avoid permanently queued follower reads. Lock information returned by the leader is converted into a read-index response error. Requests that were proposed while the peer was leader but complete after it becomes follower are notified stale unless they explicitly allow replica read.

## Test Signals
No local unit tests are present. Signals include read-index pending metrics, retry logs, `read_index_no_leader` metric, lock-response handling, and integration tests for follower reads under lost responses or apply lag.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/replica.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/apply_trace.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/apply_trace.rs

## Purpose
Tracks apply persistence for raftstore-v2 tablets, where tablet WAL is disabled. It records data-CF flush progress and a virtual raft-CF admin progress so restart recovery can replay only the necessary raft logs without losing unflushed data or violating admin-operation barriers.

## Important APIs, Types, And Functions
`write_initial_states` writes bootstrap raft, apply, region, and flushed-index states. `StateStorage` adapts engine flush progress into raft-engine records and peer messages. `ApplyTrace` tracks per-CF `Progress`, admin progress, persisted apply index, explicit flush triggers, and ready-number flush tasks. Key methods include `recover`, `on_flush`, `on_modify`, `on_admin_flush`, `on_admin_modify`, `on_sst_ingested`, `should_flush`, `maybe_advance_admin_flushed`, `advance_flushed_index_for_ingest`, `log_recovery`, `restore_snapshot`, `on_applied_snapshot`, `should_persist`, `register_flush_task`, and `take_flush_index`. `Storage::new`, `recover_tablet`, `init_apply_trace`, and `record_apply_trace` connect trace state to storage lifecycle. Peer hooks include `on_data_flushed`, `on_data_modified`, `cleanup_stale_ssts`, and `flush_before_close`.

## Control Flow
Recovery reads persisted flushed indexes for all data CFs and the virtual raft CF, then loads region/apply state at the recovered admin index. During runtime, apply reports data modifications, engine flush callbacks report flushed indexes, and admin operations mark virtual raft-CF modifications/flushes. `maybe_advance_admin_flushed` advances the global safe replay point only when admin barriers are satisfied and unflushed data CFs permit it. Ingested SST ranges can bridge gaps beyond flush records. When `should_persist` is true, ready handling writes the raft-CF flushed index through the raft engine and records the ready number so stale SST cleanup can run after persistence completes.

## State And Persistence Behavior
Durable records include region state, apply state, raft state, and flushed indexes keyed by region, CF, tablet index, and apply index in the raft engine. In-memory `ApplyTrace` mirrors progress and decides when to persist. Snapshot restore resets modification markers without pretending data is flushed; applied snapshot marks all data/admin flushed. `flush_before_close` may force up to three oldest-CF flushes and synchronously persist the admin flushed index to reduce replay on shutdown.

## Dependencies And Integration Points
Depends on `KvEngine`/`RaftEngine` flushed-index APIs, tablet registry paths, encryption key manager, snapshot install paths, tablet worker cleanup tasks, flush state atomics, SST apply state, `PeerMsg::DataFlushed`, `WriteTask.extra_write`, and ready persistence callbacks.

## Risks And Edge Cases
Incorrect advancement of admin flushed index can cause data loss after restart or unnecessary replay. The code handles flush racing ahead of modification tracking by aligning impossible progress, treats SST ingests as pending inclusive ranges, and uses apply index rather than raw flushed index in `flush_before_close` to avoid advancing beyond seen modifications. Tablet recovery panics on missing tablet data after trying split and snapshot paths. Failpoints can force apply-trace persistence or reset apply index during restart.

## Test Signals
`test_write_initial_states` verifies bootstrap raft/apply/region/flushed records. `test_apply_trace` exercises data flush, admin barriers, and SST-ingest range advancement. `test_advance_admin_flushed` covers advancement edge cases, races, and non-regression. Failpoints include `should_persist_apply_trace`, `RESET_APPLY_INDEX_WHEN_RESTART`, and `flush_before_close_threshold`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/apply_trace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/async_writer.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/async_writer.rs

## Purpose
Wraps asynchronous raft ready persistence for a peer. It tracks which ready numbers are not yet persisted, merges ready tasks that have no durable data into preceding writes, and releases persisted raft messages only after their durability dependency is satisfied.

## Important APIs, Types, And Functions
`UnpersistedReady` records ready number, maximum following empty ready number, persisted-message batches, snapshot presence, and flushed epoch. `AsyncWriter::new`, `write`, `known_largest_number`, `send`, `merge`, `on_persisted`, `persisted_number`, and `all_ready_persisted` implement the writer. Test-export methods `subscribe_flush` and `notify_flush` support waiting for flush. The file also implements `WriteRouterContext` for `StoreContext` and `PersistedNotifier` for `StoreRouter`.

## Control Flow
`write` sends tasks with durable data to the write router and records an `UnpersistedReady`. Empty tasks are either returned immediately when no prior ready is pending, or merged into the last unpersisted ready by extending `max_empty_number` and buffering any messages. `on_persisted` pops unpersisted readies up to the completed ready number, accumulates deferred raft messages, captures the last flushed epoch and snapshot flag, advances `persisted_number` to include merged empty readies, and asks the write router to check newly persisted work.

## State And Persistence Behavior
The durable writes are executed by the write router and write workers outside this file. `AsyncWriter` maintains only in-memory ordering state, but it is safety-critical because persisted messages must not be sent before the entries or state they depend on are durable. Snapshot and flushed-epoch flags are carried forward to ready completion handling.

## Dependencies And Integration Points
Depends on `WriteRouter`, `WriteTask`, write senders, store config/metrics, persisted notifier callbacks, `PeerMsg::Persisted`, raft messages, and ready handling in `ready/mod.rs`.

## Risks And Edge Cases
Ready numbers must be monotonic and persisted callbacks must match queued readies; otherwise the code panics through `slog_panic`. Empty ready merging must preserve deferred message ordering and include snapshots/flushed epochs from prior persisted work. Persisted notifications are best effort through router `force_send`; failures are logged.

## Test Signals
No local unit tests are present in this file. Signals include ready-number panic paths, persisted message ordering in integration tests, test-export flush channels, and ready persistence metrics from the write router.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/async_writer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/mod.rs

## Purpose
Drives raft ready processing for raftstore-v2. It batches raft side effects, sends asynchronous persistence tasks, applies committed entries, sends raft messages, manages snapshots, handles role changes, updates leases/read progress, reports durability/commit metrics, and finalizes peer destroy after persistence.

## Important APIs, Types, And Functions
Exports `ApplyTrace`, `DataTrace`, `StateStorage`, `AsyncWriter`, `GenSnapTask`, `SnapState`, and `write_initial_states`. `ReplayWatch` records startup replay pause statistics. Store APIs include `on_store_unreachable` and test-only `on_wait_flush`. Peer FSM tick APIs include `on_raft_tick` and `on_check_long_uncommitted`. Major peer methods include `maybe_pause_for_replay`, `tick`, `on_raft_message`, `on_raft_log_fetched`, `build_raft_message`, `send_raft_message`, `handle_raft_committed_entries`, `handle_raft_ready`, `on_persisted`, `on_role_changed`, `on_leader_commit_index_changed`, `check_long_uncommitted_proposals`, and `handle_reported_disk_usage`. `Storage::handle_raft_ready` folds ready state into write tasks.

## Control Flow
Ticks retry pending reads, check force leader state, and tick raft unless the peer is snapshot-handling or not serving. Incoming raft messages pass replay pause, tombstone, extra-message, epoch, peer-id, split-initialization, read-index fast path, and raft `step` handling before marking ready. `handle_raft_ready` resets ready flags, takes raft ready, handles role changes, sends volatile leader messages, applies read states, schedules committed entries to apply, builds a `WriteTask`, merges storage state changes and apply-trace writes, attaches persisted messages, starts destroy if the peer stopped serving, and either advances immediately for empty writes or advances asynchronously through `AsyncWriter`.

## State And Persistence Behavior
Ready persistence includes raft entries, hard state, raft state, apply trace records, snapshot application metadata, flushed epoch, and destroy tombstone writes. `AsyncWriter` delays `advance_append` completion until persistence returns. `on_persisted` sends deferred persisted messages, calls raft `on_persist_ready`, reports persisted/commit metrics, finalizes applied snapshot state, updates flushed epoch and entry cache persistence, cleans stale SSTs after persisted flushed-index records, optionally forwards force-leader commit index, and finishes destroy when all ready work is persisted.

## Dependencies And Integration Points
Depends on raft-rs `Ready`, raftstore transport, apply scheduling, snapshot module, async writer, apply trace, lifecycle destroy methods, query pending-read handling, PD heartbeat on role changes, coprocessor role/region-change notifications, tablet worker trim/flush tasks, disk usage tracking, transaction context, transfer-leader cache warmup, and raftstore metrics.

## Risks And Edge Cases
The file is concurrency-sensitive because ready handling and write completion can overlap. Persisted messages must wait for durable state, destroy must be the final ready, and snapshots must update apply state only after async loading completes. Read safety requires role-change cleanup, lease renewal/expiration, split and merge gating, and prepare-merge lease suspicion. Replay pause prevents startup from spending too long reading missing logs but must still schedule apply. Disk usage messages can change inflight limits and proposal availability. Failpoints cover snapshot-ready and long-uncommitted paths.

## Test Signals
No local test module appears here, but many integration tests exercise this path. Signals include ready metrics, persisted/commit waterfall metrics, snapshot counters, role-change coprocessor callbacks, long-uncommitted warnings, failpoints `before_handle_snapshot_ready_3` and `on_check_long_uncommitted_proposals_1`, test-export flush waits, and lifecycle tests that verify destroy completion after async persistence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/mod.rs -->
