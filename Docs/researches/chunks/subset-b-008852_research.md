# sources/storage-engines/tikv/components/raftstore/src/store/peer.rs lines 1-6535

## Scope and Purpose

This chunk contains the main Raftstore `Peer<EK, ER>` implementation for a TiKV region replica. It defines the peer's proposal queues, read-index queue integration, leader lease handling, Raft ready append/advance flow, snapshot persistence/application handoff, destroy lifecycle, split/merge gates, disk-full quorum handling, transfer-leader protocol, PD heartbeat payloads, and request inspection policy. The final lines enter the local test module, but the actual test bodies are outside this requested line range.

`Peer` is the stateful bridge between raft-rs `RawNode<PeerStorage<EK, ER>>`, TiKV's apply FSM, async/sync write IO, transport, PD reporting, coprocessor hooks, region read progress, transaction extensions, and region-worker tasks. Most functions in this chunk are about preserving the exact order between Raft state changes, durable persistence, apply scheduling, message sending, and externally visible reads.

## Important Types and State

- `ProposalQueue<C>` tracks pending proposals in `(term, index)` order. It supports tracker lookup, proposal-time lookup, stale-proposal notification, callback extraction when entries commit, and capacity shrinking after drains. It panics if committed entries disagree with queued proposal ordering, which is a strong consistency invariant.
- `ProposalContext` serializes raft entry flags into one byte: sync-log, split, prepare-merge, commit-merge, and rollback-merge. It is attached to `Entry.context` and later used in commit handling and failpoints.
- `CmdEpochChecker<S>` records at most a small deque of proposed epoch-changing admin commands. It prevents conflicting epoch checks before apply catches up, attaches callbacks to rejected commands, advances callbacks after apply, and reports stale callbacks on term changes or drop.
- `ApplySnapshotContext`, `PersistSnapshotResult`, `UnpersistedReady`, and `ReadyResult` describe the ready/snapshot persistence pipeline: ready number, messages to send after snapshot apply, persisted snapshot metadata, pending async ready numbers, and whether append processing produced IO.
- `SplitCheckTrigger` accumulates approximate size/key state, compaction-declined bytes, ingest effects, and skip flags for split checks.
- `Peer<EK, ER>` holds the core replica state: region and peer metadata, `RawNode`, proposal/read queues, leader lease, pending snapshot/apply state, merge/split markers, replication mode and group commit state, disk-full peers, transaction extension state, read-progress tracker, write router, unpersisted ready queues, leader-transfer state, recovery state, and operational counters.
- `DiskFullPeers` tracks peers on almost-full/already-full stores and whether each can still contribute to quorum; `majority` marks when disk-full peers affect the quorum set.
- `RequestPolicy` and `RequestInspector` decide whether a command is handled as local read, stale read, read index, normal proposal, transfer leader, or conf change.
- `TransferLeaderContext` serializes pre-transfer metadata: empty context, command-reply marker, or coprocessor-provided key/value context. `TransferLeaderState` tracks current transferee, pending pre-transfer message deadline, and entry-cache warmup state.

## Core Control Flow

Peer construction (`Peer::new`) validates the peer id, builds `PeerStorage`, initializes raft-rs `RawNode` with TiKV config, seeds applied and last-index derived fields, initializes read progress and transaction extensions, optionally campaigns for a single-peer region, and syncs the persisted index cache. `activate` registers the peer with apply scheduling and emits a coprocessor region-create event.

Raft message flow starts with `step`, which updates heartbeat/leader-missing observations, short-circuits read-index requests when a valid leader lease can answer them, drops unsafe early vote messages, calls `RawNode::step`, reports commit timing, and flags balance-related snapshot generation. Outbound messages are wrapped by `build_raft_message`/`prepare_raft_message`, enriched with region epoch, peer metadata, disk usage, and initial-message range keys, then sent through `send_raft_messages`, which reports unreachable peers and snapshot failures back to raft-rs.

Ready append flow is centered on `handle_raft_ready_append`. It refuses work while pending destroy or snapshot application blocks readiness, checks pending snapshot prerequisites, waits for overlapping atomic snapshot source destruction, obtains `RawNode::ready`, updates metrics, applies role/leader-commit side effects before external messages, sends leader messages, advances read-index requests, schedules committed entries to apply, handles generate-snapshot tasks, persists ready data through `PeerStorage::handle_raft_ready`, and either dispatches a write task or advances non-IO ready state immediately.

Ready advance flow has separate async and sync paths. `on_persist_ready` consumes `unpersisted_readies`, sends persisted messages only after durability, calls `RawNode::on_persist_ready`, updates persisted caches, forwards forced-leader commit indexes, and schedules snapshot application once the snapshot ready is fully persisted. `handle_raft_ready_advance` performs the same ordering for sync write worker mode using `advance_append`/`advance_append_async`, handles light ready commit/messages/committed entries, and updates storage commit state when the light ready changes commit index.

Committed entry handling (`handle_raft_committed_entries`) asserts that no snapshot is being applied, updates raft log size hints and term cache per entry, renews leader lease based on the proposal time of a committed current-term command, extracts proposal callbacks, invokes "committed" callbacks only when epoch safety was guaranteed, builds an `Apply` task with commit index bounded by persisted index, traces/evicts entry cache as needed, and schedules apply through `apply_router`.

Apply completion (`post_apply`) advances raft-rs applied index, advances the epoch checker, compacts follower entry cache, persists apply state and applied term into `PeerStorage`, updates hot-write and split-check hints, unblocks pending snapshots/read-index requests, updates `RegionReadProgress`, and notifies coprocessors/read delegates when a leader applies the current term.

## Reads, Leases, and Read Progress

`RequestInspector::inspect` rejects mixed read/write batches and invalid command types, routes stale reads directly, replica reads through follower read-index policy, read-quorum requests through read index, and ordinary reads through local lease only when the peer has applied the current term and the lease is valid.

Local reads call `handle_read` directly with the peer storage commit index. `handle_read` optionally checks region epoch, enforces stale-read `safe_ts`, asks `RegionReadProgress` to advance resolved-ts when stale read lag is material, executes the read through a `PollContextReader` snapshot, attaches `txn_ext` and bucket metadata to returned snapshots, includes `txn_extra_op`, and binds the current raft term to the response.

Read-index flow (`read_index`, `apply_reads`, `response_read`, and `post_pending_read_index_on_replica`) is careful about leader and follower semantics. Leaders can amend compatible reads into the last pending read while the prior lease window covers them. Followers reject replica reads when local disk is not normal, wake hibernated leaders and ask PD for leader info when no leader is known, retry lost read-index requests, and only serve unsafe replica reads after applying to the read index, with no pending merge and no snapshot handling. Leader reads wait for `ready_to_handle_read`, which blocks during split, merge, or before the current term is applied.

Lease renewal is centralized in `maybe_renew_leader_lease`, guarded by `should_renew_lease`. Leaders do not renew while splitting, merging, in force-leader mode, or in flashback state. Lease updates propagate to read delegates through `ReadProgress`, and `need_renew_lease_at` avoids redundant renewals when pending reads or writes already cover the next heartbeat window.

## Snapshot, Destroy, Split, and Merge Behavior

Snapshot handling is deliberately serialized. `check_snap_status` blocks new ready processing until a persisted snapshot is scheduled and applied; on success it sends delayed messages, advances apply index to the truncated index, advances the epoch checker, finishes recovery wait states, resumes read progress, updates applied progress, and clears `wait_data` peers by notifying the leader and scheduling apply recovery.

`handle_raft_ready_append` records snapshot results in `apply_snap_ctx`, pauses read progress, resets raft-log size hints, schedules best-effort raftlog GC for stale logs, and handles witness snapshot notifications. `on_persist_snapshot` validates ready number ordering, marks the snapshot scheduled, persists snapshot metadata into storage, refreshes peer metadata that may have changed from learner/witness transitions, adjusts raft priority, and activates the peer.

Destroy flow starts with `maybe_destroy`, which defers destruction while atomic snapshot or snapshot apply/persist work is in flight, cancels applying snapshots where possible, marks `pending_remove`, and returns a `DestroyPeerJob`. `destroy` schedules background peer metadata/data cleanup through storage, falling back to synchronous `clear_meta_in_kv_and_raft` if the worker is unavailable. `ready_to_destroy` records cleanup metrics, schedules data clearing when needed, clears pending reads, and reports all pending proposals as region removed.

Merge safety is spread across proposal and read logic. `pre_propose_prepare_merge` checks follower progress, rejects pending snapshots, bounds log and entry-size gaps, rejects conf/admin commands in the merge gap, gates in-memory pessimistic locks behind `prepare_merge_fence`, and proposes those locks before PrepareMerge. `on_leader_commit_idx_changed` records committed split/prepare-merge indexes before commit index is externally observable; PrepareMerge suspects the lease and discards read progress to avoid stale local reads. `maybe_append_merge_entries` appends source entries directly during commit-merge handling and adjusts term/commit metadata if needed.

## Proposals, Conf Changes, and Transfer Leader

`propose` is the public command entry point. It inspects the request, dispatches reads immediately, routes transfer-leader/admin/conf-change/normal proposals, checks disk-full policy, handles epoch conflicts by attaching callbacks to conflicting admin commands, invokes proposed callbacks only after current-term apply safety, marks urgent proposals to disable lazy commit, records proposal metadata, and disables unpersisted apply for PrepareMerge.

`propose_normal` rejects inappropriate force-leader and merging states, requires current-term apply for admin commands, runs `CmdEpochChecker`, invokes coprocessor `pre_propose`, serializes and size-checks the request, calls raft-rs `propose`, handles silent drops as NotLeader, and relaxes max-inflight limits for merge proposals when disk-full peers must receive logs.

`propose_conf_change` requires no pending merge/conf change and current-term apply, runs coprocessor checks and epoch checks, serializes the admin command, and delegates to `propose_conf_change_internal`. The internal path uses `util::check_conf_change` for health/removal constraints and calls raft-rs `propose_conf_change` with sync-log context.

Transfer leader uses a pre-transfer protocol. The leader sends `MsgTransferLeader` with last-log term, cache low index, and serialized `TransferLeaderContext`; the transferee rejects if it is learner/witness/wait-data, applying snapshot, contacted by a nonleader, or less disk-healthy than the source. It may warm entry cache asynchronously, then acks with applied index/log term. The leader validates voter status, snapshot state, pending conf index, and max log lag before calling raft-rs `transfer_leader`. TransferLeader admin commands may choose the best matched transferee and return an immediate admin response because the actual leadership move is advisory.

## Replication, Disk-Full, PD, and Extra Messages

Replication mode support initializes and switches group commit based on `GlobalReplicationState` and DR auto-sync status. `region_replication_status` checks group commit consistency, enables group commit after SyncRecover catch-up, and reports `IntegrityOverLabel`, `SimpleMajority`, or `Unknown` to PD. `check_group_commit_consistent` temporarily enables group commit to query maximal committed index, then restores the original setting.

Leader heartbeat support includes `check_peers`, `collect_down_peers`, `collect_pending_peers`, `any_new_peer_catch_up`, `check_stale_state`, `heartbeat_pd`, and stale-peer extra messages. PD heartbeats carry term, region, down/pending peers, write stats, approximate size/keys, replication status, and wait-data peers.

Disk-full handling refills `DiskFullPeers` from store disk usage and raft progress, adjusts per-peer max inflight to zero/one/full depending on quorum contribution and merge needs, marks dangerous majority sets containing already-full peers, rejects proposals when the leader or quorum cannot accept them, and may pre-transfer leadership to a normal peer to preserve write availability.

Extra-message integration covers wake-up broadcasts for hibernated regions, stale-peer checks, snapshot-generation precheck request/response, availability notification after wait-data snapshot apply, want-rollback-merge messages, and max-ts update scheduling on leadership acquisition.

## Persistence and Ordering Guarantees

The central persistence invariant is that messages depending on durable state are sent only after the corresponding ready has been persisted. Async write mode stores ready numbers in `unpersisted_readies`; no-IO ready instances are attached to the prior IO ready where possible. Sync write mode holds `unpersisted_ready` until `handle_raft_ready_advance`.

Committed apply tasks use a commit index capped at the persisted index so apply forwarding cannot advertise unpersisted logs. Snapshot ready application is delayed until the snapshot's ready number is persisted and all earlier unpersisted readies are consumed. Read progress is paused during snapshot apply and resumed only after apply completion advances storage and raft-rs state.

Unpersisted apply is disabled on term change and PrepareMerge by setting a minimum safe index, then re-enabled only after applying beyond that index and only when configured. Metrics track whether raft-rs currently has unpersisted apply enabled to keep gauges balanced even if raft-rs resets the limit on demotion.

## Dependencies and Integration Points

- raft-rs: `RawNode`, `Ready`, `LightReady`, `Entry`, `Message`, progress state, conf voters, read index, leader transfer, group commit, persisted/committed/applied indexes.
- Storage: `PeerStorage`, `Engines`, `KvEngine`, `RaftEngine`, snapshots, term cache, apply state, raft state, entry cache, snapshot persistence, destroy scheduling, log GC, and async entry-cache warmup.
- FSM and workers: `PollContext`, `ApplyTask`, `Apply`, `WriteRouter`, `WriteMsg`, region worker tasks, split-check tasks, raftlog GC tasks, and read tasks.
- Transport and routing: `Transport`, `RaftMessage`, `ExtraMessage`, `RaftStoreRouter`, `PeerMsg`, `CasualMessage`, read command forwarding, and apply router scheduling.
- PD/coprocessor: PD heartbeat/update-max-ts/query-leader tasks, replication state, coprocessor region-change/role-change/pre-propose/pre-transfer hooks, and read-progress callbacks.
- Transaction/read support: `TxnExt`, in-memory pessimistic locks, `LocksStatus`, `TxnExtraOp`, `ReadDelegate`, `RegionReadProgress`, stale-read safe timestamps, bucket metadata.
- Operational controls: failpoints, metrics, memory tracing, disk usage, feature gate for snapshot-generation precheck, hibernation group state, unsafe recovery, and snapshot backup recovery.

## Risks and Edge Cases

- Ready ordering is fragile: sending messages before persistence, advancing ready numbers out of order, or handling new ready while a snapshot is applying can violate raft durability or create stale reads. The code uses assertions, panics, and queues to enforce this.
- Lease correctness depends on split/merge ordering. Split and PrepareMerge commit indexes must be recorded before the new commit index leaks through heartbeat/read-index responses; otherwise local reads can serve stale ranges.
- Proposal callback correctness depends on monotonic `(term, index)` ordering in `ProposalQueue` and accurate `CmdEpochChecker` state. Term changes intentionally stale outstanding callbacks.
- Direct merge-entry append bypasses normal raft replication paths; term and commit metadata are manually adjusted to keep raft state coherent.
- Disk-full handling trades availability and safety by throttling peers, selectively allowing quorum contributors, and special-casing merge proposals. Incorrect quorum classification can either halt writes unnecessarily or send logs to stores that cannot persist them.
- Transfer leader is multi-stage and advisory. Stale cache-warmup state, pending conf changes, pending snapshots, learner/witness targets, disk-health skew, and version-skewed missing low indexes are all handled explicitly.
- Follower read-index requests can be lost and must be retried; unsafe replica reads are blocked by apply lag, pending merge, and snapshot handling. A long gap returns `ReadIndexNotReady`.
- Destroy during snapshot work is deferred via flags. Incorrectly clearing data while snapshot apply or atomic snapshot overlap is active could delete live region data.
- Several paths panic rather than recover after storage/ready invariant failures, because continuing could resurrect stale peers or corrupt Raft state.

## Test Signals

The chunk begins the local test module at line 6533, so test bodies are outside this work item's range. The visible production code has many failpoints and metrics that indicate intended test coverage:

- Proposal queue tests should verify monotonic push, stale callback notification, exact term/index matching, queue shrinking, and panic on unexpected callback index.
- Epoch checker tests should cover conflicting split/merge/change-peer commands, term changes, callback attachment to conflict commands, apply advancement, and drop-time stale notification.
- Read policy tests should cover local lease reads, read quorum, replica reads, stale reads, mixed read/write rejection, invalid command rejection, and current-term apply gating.
- Ready pipeline tests should exercise async and sync persistence, no-IO ready attachment, persisted message sending after durability, light ready commit handling, and panic cases for out-of-order ready numbers.
- Snapshot tests should cover pending snapshot gating, `apply_snap_ctx` scheduling, read-progress pause/resume, wait-data recovery, witness snapshot notification, stale-log GC scheduling, and destroy deferral during snapshot work.
- Lease/split/merge tests should verify no lease renewal during split/merge/force-leader/flashback, lease suspicion after PrepareMerge, safe-ts discard, prepare-merge fence behavior, pessimistic-lock proposal before merge, and log-gap/admin-command rejection.
- Disk-full tests should cover leader full rejection, follower full quorum classification, dangerous majority sets, max-inflight adjustments, merge proposal exceptions, and leader-transfer attempts away from full leaders.
- Transfer-leader tests should cover pre-transfer context serialization, rejection predicates, cache warmup timeout/staleness, command-reply ACK context, pending-conf/log-gap checks, and immediate command response behavior.
- PD/extra-message tests should cover down/pending peer reporting, stale-peer message peer-list caching, wake-up throttling, snapshot-generation precheck feature gating, availability response after wait-data snapshot, and replication status transitions.

## Cross-Chunk Notes

Lines after 6535 contain the test bodies for helpers and peer behaviors introduced here. The final reconciled per-file document should merge those tests with this production-code analysis, and should also account for any later `peer.rs` code beyond the requested line range.
