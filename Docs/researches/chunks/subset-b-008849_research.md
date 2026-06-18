# sources/storage-engines/tikv/components/raftstore/src/store/fsm/peer.rs lines 1-6333

## Scope and Purpose

This chunk covers the first and largest part of TiKV raftstore v1 peer-FSM handling. It defines `PeerFsm`, the command batch builder, the `PeerFsmDelegate` message loop, and most of the peer-side control plane for Raft messages, ready/apply results, snapshots, peer destruction, membership changes, split/merge, unsafe recovery, proposal validation, and the beginning of Raft log GC.

The code is on the performance-critical raftstore path. Its job is to bridge the batch-system FSM runtime with the lower-level `Peer<EK, ER>` Raft state machine, the apply FSM, `StoreMeta`, PD scheduling, snapshot manager, cleanup/raftlog workers, coprocessor observers, and transport. It owns per-peer scheduling state (`tick_registry`, hibernation state, pending ready flags, delayed destroy state, command batching state) while delegating actual Raft storage/proposal mechanics to `Peer`.

This chunk starts at imports and type definitions and ends inside `on_raft_gc_log_tick`, after leader-side progress scanning and entry-cache compaction decisions. The remaining part of log-GC proposal construction and later tick/utility/test code is outside this mapped range.

## Major Types and Constants

- `DelayDestroy` and `DelayReason` track why physical peer destruction is deferred. Reasons are unpersisted ready data, unflushed Raft log GC, or shutdown.
- `DestroyPeerJob` carries the minimal information needed to destroy a peer, including whether the apply FSM exists.
- `PeerFsm<EK, ER>` wraps `Peer<EK, ER>` and the batch-system-facing state: scheduled tick registry, hibernation/missing tick accounting, stopped/ready flags, mailbox/receiver, split/log-GC skip counters, command batch builder, memory trace deltas, delayed destruction, and whether destroy-time log GC has flushed.
- `BatchRaftCmdRequestBuilder<E>` batches compatible write commands into one `RaftCmdRequest`. It tracks accumulated request size, callbacks, early proposed-callback state, and debug duplicate-key detection for `CF_LOCK` puts.
- `PeerFsmDelegate<'a, EK, ER, T>` is the active handler bound to a mutable `PeerFsm` plus a mutable `PollContext`. Almost all behavior in this chunk is implemented on this delegate.
- Important constants include `MAX_REGIONS_IN_ERROR`, `REGION_SPLIT_SKIP_MAX_COUNT`, `MAX_BATCH_SIZE_LIMIT`, `UNSAFE_RECOVERY_STATE_TIMEOUT`, and `MAX_PROPOSAL_SIZE_RATIO`.

## Construction, FSM Runtime, and Batching

`PeerFsm::create` constructs an initialized peer for bootstrap, split, or merge-derived regions by finding this store's peer in the provided region. `PeerFsm::replicate` constructs an uninitialized peer when a Raft message creates a local replica before its full region state is known. Both initialize hibernation metrics, a loose-bounded receiver, `Peer::new`, empty batching state, and no delayed destruction.

`Drop for PeerFsm` stops the peer, drains pending messages, invokes command and split callbacks with a region-not-found response, decrements hibernation gauges, and subtracts recorded memory trace sizes. This is a critical last-chance callback path: leaving callbacks pending would strand clients or panic higher layers.

The `Fsm` implementation exposes the batch-system contract: `PeerMsg<EK>` messages, store FSM type, `is_stopped`, mailbox install, and mailbox removal.

`BatchRaftCmdRequestBuilder` batches only simple non-empty `Put`/`Delete` requests with matching headers and bounded size. It rejects large individual requests, caps total batched request size, caps by `WRITE_BATCH_MAX_KEYS`, and limits the final proposal to a fraction of `raft_entry_max_size`. When building a batch, it combines proposed callbacks, committed callbacks, and write trackers into one `Callback::Write` while returning per-original-command responses with the shared response header.

Risk signal: batching deliberately reorders pending batched commands with direct `propose_raft_command_internal` calls in some paths. The code protects ordinary external proposals by flushing pending batches before proposing a non-batched command, but internal callers that bypass that helper rely on comments and local reasoning.

## Main Message Loop

`handle_msgs` drains a vector of `PeerMsg` values and dispatches by variant:

- `RaftMessage` passes through coprocessor filtering and `on_raft_message`.
- `RaftCommand` records wait time, enforces deadline, optionally checks duplicate lock-CF keys, then either batches or proposes immediately depending on config, request compatibility, disk-full policy, and majority disk-full state.
- `Tick` dispatches to `on_tick`.
- `ApplyRes`, `SignificantMsg`, `CasualMessage`, `Start`, `HeartbeatPd`, `Persisted`, replication-mode updates, and destroy messages map to their dedicated handlers.

Stopped peers skip most messages, but not `RaftCommand`, because client callbacks still need deterministic failure. After the loop, `on_loop_finished` decides whether to flush a pending batch. It delays batching when ready concurrency limits or uncommitted logs suggest waiting will improve batching, but may invoke proposed callbacks early if pre-propose checks and likely-propose checks succeed.

The loop integrates metrics heavily: message distribution, wait times, proposal delays, event time, slow logs, and waterfall trackers.

## Ticks, Hibernation, and Readiness

`schedule_tick` uses `tick_registry` to avoid duplicate scheduling and appends closures into `ctx.tick_batch`. `start` registers base Raft, log GC, PD heartbeat, split check, stale peer check, merge check, optional snapshot request, approximate bucket generation, and witness voter-index pulling.

`on_raft_base_tick` is the core periodic driver. It ignores pending-remove peers, checks apply completion state, may fetch committed index for lag detection, keeps ticking while snapshots are pending, retries pending reads, advances unsafe force-leader state, runs hibernation pre/post checks, replays skipped ticks after waking from idle, ticks raft-rs, flushes entry-cache metrics, and either reschedules ticks or transitions to `GroupState::Idle`.

Leader hibernation requires local `HibernateState` quorum votes. `quorum_agree_to_hibernate` may broadcast `MsgHibernateRequest`; followers respond only when hibernation is enabled, no uncommitted logs exist, they are not waiting for snapshot data, and the request comes from the current leader. Wake-up and stale-check extra messages reset hibernation to ordered or chaos states.

`collect_ready` consumes `fsm.has_ready`, asks `Peer` to append Raft ready data, reacts to role changes, registers GC/cache ticks for new entries, accounts ready metrics, and wakes a peer if the leader was marked unreachable.

## Casual and Significant Messages

`on_casual_msg` handles local side-channel events that are not direct Raft log entries: split preparation, hash results, approximate size/key updates, bucket refresh, snapshot GC, clearing region size, region-overlap wake-up, generated snapshot completion, forced log compaction, metadata access callbacks, leader query responses, lease renewal, rejecting append, snapshot-applied damage tracking, campaigns, and in-memory-engine load scheduling.

`on_significant_msg` handles higher-priority cross-component events: snapshot status/unreachable reports, merge results, catch-up logs, resolved stores for DR AutoSync commit groups, capture-change read-index proposals, leader callbacks, log-GC flush completion, async raftlog fetch completion, unsafe recovery commands, snapshot-backup wait-apply commands, pending-admin checks, and delayed async destroy completion.

These message families are the major integration surface between peer FSM, apply FSM, store FSM, region workers, snapshot manager, PD, and unsafe/snapshot recovery orchestration.

## Raft Message Validation and Handling

`on_raft_message` is the external Raft ingress path. It updates memory accounting through a deferred block, rejects messages for stopped/pending-remove peers, updates reported disk usage, drops unsafe `MsgTimeoutNow` under `AlreadyFull`, drops append messages for non-witness peers still waiting for snapshot data, validates store id and epoch presence, handles tombstone GC messages, handles merge-target stale-source discovery, and checks target peer id.

`check_msg` enforces that a message targets the current peer. Stale messages to smaller peer ids are dropped; messages to larger peer ids can trigger self-destruction if `Peer::maybe_destroy` says this local peer is stale. Epoch-stale messages from stores no longer in the region are forwarded to stale-message handling.

`check_snapshot` is the main snapshot safety gate. It verifies snapshot file presence for non-witness snapshots, rejects witness/non-witness mismatches for stale snapshot indices, verifies the snapshot contains the target peer, checks in-memory `StoreMeta` consistency, rejects overlap with atomic snapshots or pending snapshots, scans `region_ranges` for overlap, and determines whether overlapped source regions can be destroyed because the snapshot represents a merge target. It records accepted snapshot regions in `pending_snapshot_regions` and returns source regions that should be destroyed only after raft-rs accepts the snapshot.

`destroy_regions_for_snapshot` marks source regions in `atomic_snap_regions` and `destroyed_region_for_snap`, then sends merge-result messages to those source peers. This defers actual destruction until the target snapshot path is known to be applying.

Once a message passes checks, vote and timeout messages move the peer into chaos; leader messages reset ordered ticking. The peer cache is updated, transfer-leader messages take a special path, and all other Raft messages call `Peer::step`. Accepted snapshots may destroy overlapped regions. Successful handling can clear uncampaigned split records, heartbeat PD when new peers catch up, wake hibernated peers, and set `has_ready`.

Risk signal: many invariants are enforced by `panic!` or `assert!` because metadata corruption, impossible merge states, or contradictory peer ids would risk data loss. These paths are intentionally fail-fast.

## Unsafe Recovery and Snapshot Recovery

The unsafe recovery handlers coordinate forced leadership, voter demotion, peer destruction, wait-apply, and reporting:

- `on_enter_pre_force_leader` validates initialization, waits out active leader leases/election timeout when needed, forces apply/raft compatibility when applied index is ahead of last index, rejects force leader if expected alive voters still form quorum, disables prevote, campaigns, and enters `PreForceLeader`.
- `check_force_leader` waits for vote responses from expected live voters. If all expected voters grant, `on_enter_force_leader` injects positive vote responses for failed stores, disables check-quorum, and enters `ForceLeader`.
- `on_exit_force_leader` restores normal Raft behavior, expires forced leadership, becomes follower, reenables check-quorum/prevote, and optionally campaigns again.
- `on_unsafe_recovery_pre_demote_failed_voters` exits joint state first if needed, then proposes demotion through `demote_failed_voters_request`.
- `check_unsafe_recovery_state` completes wait-apply and demotion flows after target indexes are applied.
- `on_unsafe_recovery_fill_out_report` reports local raft/region state, applied index, force-leader status, and whether uncommitted entries include a commit-merge context.

Snapshot backup recovery uses `on_snapshot_br_wait_apply` to wait until followers or leaders apply through their current last index, with expected epoch validation, follower sanity checks, term-change abort support, and per-state syncer completion.

Risk signal: force leader deliberately bypasses normal quorum assumptions and temporarily disables Raft protections. The code narrows allowed proposals during force-leader state to change-peer/change-peer-v2/rollback-merge operations and returns `RecoveryInProgress` for ordinary requests.

## Apply Results and Ready Results

`on_apply_res` handles `ApplyTaskRes::Apply` by processing `ExecResult`s, ignoring results after stop/ready-to-destroy, updating bucket flow, checking apply completion, calling `Peer::post_apply`, and registering leader-side PD heartbeat, split check, pending-merge retry, and apply-unpersisted-log state updates. `ApplyTaskRes::Destroy` either destroys the peer or marks an atomic snapshot source as ready for target-side completion.

`on_ready_result` dispatches apply execution results:

- `ChangePeer` updates raft-rs conf state, region metadata, peer caches, pending peer tracking, leader demotion/removal handling, PD heartbeat, and self-destruction.
- `CompactLog` updates pending-compact state and schedules raftlog GC/cache compaction.
- `SplitRegion` updates StoreMeta ranges, creates/registers new `PeerFsm`s, moves pessimistic locks into derived regions, initializes replication mode and read delegates, handles pending first messages, and starts new peers.
- `PrepareMerge`, `CommitMerge`, and `RollbackMerge` coordinate merge state and metadata.
- Hash, ingest SST, transfer leader, flashback, witness switching, pending compact status, and unsafe force compact are delegated to later functions or direct local state updates.

`post_raft_ready_append` is the synchronous-ready counterpart to `on_persisted_msg`, handling persisted snapshots after ready advancement and rolling back pending merge when a snapshot implicitly supersedes it.

State/persistence signal: apply results are the bridge from durable Raft log application to in-memory `StoreMeta`. Correct ordering between apply state, region ranges, read delegates, safe-ts/read progress, and peer destruction is essential for serving reads safely.

## Peer Destruction

Destruction is deliberately staged:

1. `handle_destroy_peer` destroys the apply FSM first for initialized peers; uninitialized peers can destroy directly.
2. `destroy_peer` marks `pending_remove = ReadyToDestroy`, disables apply-unpersisted-log accounting, then calls `maybe_delay_destroy`.
3. `maybe_delay_destroy` defers if unpersisted readies exist, or schedules a flushed `RaftlogGcTask` so old log entries are removed before metadata destruction. Uninitialized peers skip log GC because they should not have leader-received logs.
4. Once safe, `destroy_peer` removes damaged-region state, busy apply tracking, pending snapshot ranges, read progress, read delegates, and notifies coprocessor/PD. It then calls `Peer::destroy`, which may complete synchronously or later via `ReadyToDestroyPeer`.
5. `on_ready_destroy_peer` finalizes callback cleanup, closes the router, stops the FSM, removes `regions` and `region_ranges`, and clears merge/atomic-snapshot bookkeeping.

The code explicitly protects against destroying a peer while applying an atomic snapshot or active snapshot. Merge-target snapshot destruction also tracks whether source data must be preserved because target already owns the key range.

Risk signal: destroy-time races are central. The delayed-destroy reasons prevent races between write worker persistence, raftlog GC, and new peers with the same region id. Duplicate delayed-destroy reasons panic to catch repeated inconsistent destruction attempts.

## Split and Merge Control Flow

Split handling in `on_ready_split_region` updates pessimistic-lock epoch/version, partitions locks among derived regions, estimates size/keys, updates the parent region in `StoreMeta`, reports batch split to PD, removes/reinserts range boundaries, creates new peer FSMs for new regions, initializes replication/peer caches/read delegates, registers mailboxes, starts peers, forwards pending first messages, and records uncampaigned new regions for later cleanup.

Merge handling has several phases:

- `validate_merge_peer` and `is_merge_target_region_stale` ensure the target region is present and at the expected epoch, or determine that local persisted target state is tombstoned/stale.
- `schedule_merge` builds a `CommitMerge` admin request for the target region, including source entries from the source peer when needed.
- `on_check_merge` periodically retries scheduling and coordinates rollback requests from followers or force-leader state.
- `on_ready_prepare_merge` records pending merge state, updates region metadata, and may hand catch-up logs back to apply.
- `on_catch_up_logs_for_merge` appends merge entries directly to the source raft log or stores catch-up logs until prepare-merge applies.
- `on_ready_commit_merge` updates region range boundaries, removes source metadata, marks source read delegate pending remove, merges safe-ts using source read progress, requires max-ts refresh, resets buckets, heartbeats PD, and sends a merge result to the source peer.
- `on_ready_rollback_merge` clears pending merge state, resumes read progress, optionally updates region metadata, restores pessimistic-lock status, and heartbeats PD.
- `on_merge_result` destroys the source peer from target log, target snapshot step 1/2, or stale merge paths.

Risk signal: region merge spans two peer FSMs and the apply FSM. The code depends on PD's guarantee that all target peers exist before merge, on no compact-log proposal in the protected merge interval, and on StoreMeta range maps matching durable region state.

## Proposal Validation and Command Submission

`pre_propose_raft_command` is the central proposal gate. It checks store id, handles status requests locally, checks peer id, restricts force-leader proposals, permits read-index/replica/stale reads on non-leaders only where valid, rejects writes on non-leaders with `NotLeader`, rejects witness or not-yet-non-witness peers, requires initialization, rejects active snapshot application, checks term, checks region epoch and augments epoch-not-match errors with sibling regions, and validates flashback state.

`check_merge_proposal` validates `PrepareMerge` and `CommitMerge`: no prepare merge in joint state, target/source region must exist as expected, regions must be siblings, and peer sets must match.

`propose_raft_command` flushes pending batches before submitting a command. `propose_raft_command_internal` handles pending-remove callback failure, waterfall timing, pre-propose errors, merge-proposal errors, response term binding, `Peer::propose`, waking hibernated peers, and PD heartbeat tick registration.

`collect_sibling_region` consults `StoreMeta.region_ranges` to attach a bounded number of split siblings to epoch-not-match errors, respecting right-derived split configuration.

## Transfer Leader and Pessimistic Locks

`on_transfer_leader_msg` handles both transfer-leader requests and replies. Leaders validate log term, readiness, and transferee cache status; followers may reject or store pending transfer messages until they can acknowledge. Leaders flush command batches before transfer and call `propose_locks_before_transfer_leader`.

`propose_locks_before_transfer_leader` changes in-memory pessimistic locks into transferring-leader mode, schedules reactivation, and proposes lock-CF `Put` entries for non-deleted locks before transfer. This reduces unavailability while the transferee catches up and preserves ordering between existing writes, lock persistence, and the transfer-leader admin command.

Risk signal: there is a FIXME noting that pessimistic-lock proposal can exceed Raft command size limits. Large lock maps need testing and eventual splitting or bounding.

## State and Persistence Behavior

Persistent state touched in this chunk includes Raft log entries, Raft hard state, apply state, `RegionLocalState`, snapshot files, compacted log metadata, and engine writes during unsafe force compact. Most normal persistence is delegated to `Peer`, apply FSM, Raft engine, and worker schedulers, but this chunk controls when those writes become visible to in-memory metadata.

`StoreMeta` is the authoritative in-memory region map. This code updates `regions`, `region_ranges`, `readers`, `region_read_progress`, `pending_snapshot_regions`, `atomic_snap_regions`, `destroyed_region_for_snap`, `targets_map`, `pending_merge_targets`, `busy_apply_peers`, `damaged_regions`, and pending message queues. Lock ordering is important: destroy drops `StoreMeta` before async clearing work, while some forced sends intentionally happen under the lock because the target peer is still guaranteed to exist.

Read safety is represented through `ReadProgress`, safe-ts pausing/resuming, merge-safe-ts merging, and removing read delegates/progress before stale peers can serve reads. Leader lease renewal uses a noop read-index request when needed and rejects unsafe renewals.

Snapshot state is split among snapshot files in `snap_mgr`, `pending_snapshot_regions` range reservations, `Peer` pending snapshot state, apply FSM snapshot application, and post-persist metadata replacement. Accepted snapshots can initialize previously uninitialized replicated peers, replace existing initialized regions, or atomically absorb source regions after merge.

## Dependencies and Integration Points

- `Peer<EK, ER>` provides Raft group access, store access, proposal, step, ready append/advance, apply post-processing, snapshot state, merge helpers, disk-full peers, read progress, and destruction.
- `PollContext` supplies config, router, apply router, store metadata, engines, schedulers, snapshot manager, transport, coprocessor host, PD scheduler, metrics, global replication state, and current disk usage.
- raft-rs types (`MessageType`, `StateRole`, progress sets, snapshots, conf changes) drive message and role behavior.
- `engine_traits` and Raft engine APIs are used for log GC, unsafe force compact, and local target-region stale checks through `CF_RAFT`.
- `kvproto` request/response/state messages define the network, Raft command, region, snapshot, merge, and PD/report contracts.
- Worker schedulers handle snapshot cleanup, raftlog GC, split checks, consistency checks, and region tasks.
- Failpoints are dense throughout this chunk and act as test-only interleaving controls for snapshot, split, merge, destroy, ready, and log-GC races.

## Risks and Edge Cases

- Stale peer and replacement-peer races are common. Peer id comparisons, epoch checks, and `pending_create_peers` assertions protect against old uninitialized peers handling new-region state.
- Snapshot overlap handling can cause data loss if it destroys a source peer before a target snapshot is truly accepted. The code therefore records regions to destroy and performs destruction only after snapshot acceptance/atomic bookkeeping.
- Async destroy must not race unpersisted ready writes or raftlog GC. `maybe_delay_destroy` is a high-risk gate.
- Force leader can violate normal quorum semantics if invoked incorrectly. The code restricts proposals and carefully restores Raft settings, but recovery orchestration must be correct.
- Merge depends on cross-region ordering and target existence guarantees. Incorrect PD guarantees, stale target metadata, or premature compaction can panic or require rollback.
- Pessimistic-lock transfer-leader proposals may be oversized.
- Many state-corruption detections are panics, not recoverable errors, because continuing could corrupt data.
- Disk-full logic affects both proposal batching and Raft messages; mixing commands with different disk-full options in a batch is explicitly avoided.

## Test Signals

- Message loop tests should cover callback completion when peers stop, batching size/header/type limits, proposed/committed callback fan-out, duplicate lock-CF debug detection, deadline failures, and disk-full batching exclusions.
- Raft message tests should cover mismatched store id, missing epoch, stale target peer ids, tombstone GC, merge-target stale GC, witness/non-witness snapshot mismatch, pending snapshot overlap, atomic snapshot overlap, and stale delegate detection.
- Hibernation tests should verify leader quorum hibernation votes, follower rejection conditions, wake-up extra messages, missing-tick replay, and raft-base tick rescheduling under pending reads/snapshots.
- Destroy tests should force unpersisted-ready delay, raftlog-GC-flush delay, async destroy completion, initialized versus uninitialized destruction, merge-by-target data preservation, router close behavior, and cleanup of `StoreMeta` merge/snapshot structures.
- Split tests should validate range-map updates, new peer registration, pending uninitialized peer replacement, lock partitioning, pending first-message forwarding, size/key sharing, and uncampaigned new-region cleanup.
- Merge tests should cover prepare/commit/rollback, catch-up logs before and after prepare applies, target missing/stale states from KV engine, rollback quorum messages, target snapshot step 1/2, safe-ts merge, and source read delegate pending removal.
- Unsafe recovery tests should exercise wait-tick force leader, pre-vote/check-quorum restoration, expected-live-voter rejection, demote-after-exit-joint-state, wait-apply completion, ordinary proposal rejection during recovery, and unsafe force compact when applied index exceeds last index.
- Proposal tests should cover status-command local execution, not-leader/replica-read/stale-read/read-index paths, witness rejection, wait-data rejection, applying-snapshot rejection, term/epoch/flashback failures, sibling-region collection, and merge proposal validation.
- Log-GC tests for this chunk should at least validate the covered prefix: leader-only execution, rescheduling while cache is non-empty or hibernation disabled, progress scanning across learners/voters, heartbeat-based alive-cache index, max-log-lag metrics, and cache compaction/eviction trigger behavior.

## Cross-Chunk Notes

- Lines after 6333 continue `on_raft_gc_log_tick`, including compact index selection, compact-log proposal construction, skip counters, and final metrics.
- Later code also covers entry-cache eviction, long-uncommitted checks, snapshot request ticks, leader lease checks, split-check scheduling, bucket refresh/reporting, PD heartbeat, stale-peer checks, hash/SST/transfer/flashback/witness handlers, helper request constructors, status command execution, and unit tests.
