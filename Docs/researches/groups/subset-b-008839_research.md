# subset-b-008839 Research

Grouped research report for TiKV raftstore-v2 command, admin split/merge, write, and disk snapshot backup sources. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/commit.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/commit.rs

## Purpose
Implements the commit half of raftstore-v2 region merge. Source peers that have applied `PrepareMerge` ask the target peer to propose `CommitMerge`; target apply merges the source checkpoint tablet and target tablet into a new target tablet, then the source peer is destroyed after catch-up and acknowledgement.

## Important APIs, Types, And Functions
`CommitMergeResult` carries target apply side effects back to the peer FSM: applied index, prepare-merge index, source checkpoint path, new region state, source region, source safe-ts, and the newly opened tablet. `CatchUpLogs` is the pause/response channel used when target apply must redirect source entries before it can finish. `MERGE_IN_PROGRESS_PREFIX` and `MergeInProgressGuard` create a marker directory that distinguishes recoverable partial merged tablets from completed ones. Main peer methods are `start_commit_merge`, `on_check_merge`, `ask_target_peer_to_commit_merge`, `on_ask_commit_merge`, `propose_commit_merge`, `on_redirect_catch_up_logs`, `on_catch_up_logs`, `finish_catch_up_logs`, `on_apply_res_commit_merge`, and `on_ack_commit_merge`.

## Control Flow
After source apply of `PrepareMerge`, `start_commit_merge` schedules/checks merge and builds an `AskCommitMerge` request for the local target peer. The request embeds source `RegionLocalState` plus source raft entries from the minimum replicated index through the prepare commit. The target rejects stale epochs, ignores lagging epochs, short-circuits already merged records, and otherwise proposes a `CommitMerge` admin log with `ProposalContext::COMMIT_MERGE`. During target apply, if the source checkpoint is not yet present, apply redirects `CatchUpLogs` to the source peer and waits on a oneshot. The source appends/commits missing merge entries if necessary, applies up to `PrepareMerge`, returns safe-ts, and marks itself for destroy. The target then extends its range, merges tablets, records a `MergedRecord`, and reports `CommitMergeResult`; peer-side handling installs metadata, safe-ts, read tablet, tombstones old tablets, forces split-stat refresh, and notifies PD if leader.

## State And Persistence Behavior
Persistence is tablet-oriented. The source checkpoint lives at `merge_source_path(source_id, prepare_index)` and is consumed by target apply. Target apply opens a new tablet at `tablet_path(target_id, commit_index)`, using `MergeInProgressGuard` to delete incomplete output after crashes and defuse the marker only after `tablet.merge` succeeds. `RegionLocalState` is updated to `Normal`, new tablet index, widened key range, and appended merged records. Peer-side `state_changes_mut().put_region_state` and `apply_trace_mut().on_admin_flush` make the new state durable through raftstore-v2 state change flushing.

## Dependencies And Integration Points
Depends on merge preparation state from `prepare.rs`, `merge_source_path` from `merge/mod.rs`, raft log storage and `maybe_append`, tablet registry/factory merge support, `StoreContext` routing/control messages, `SharedReadTablet`, transaction context safe-ts merge, PD heartbeat/GC peer ticks, and proposal contexts understood by raftstore.

## Risks And Edge Cases
Correctness relies on source and target regions being siblings on the same stores, source dirty data being trimmed before commit, no oversized embedded entry payload, and precise safe-ts transfer before source metadata disappears. Crash recovery depends on marker-directory semantics and idempotent reuse of existing merged tablets. Empty catch-up entries can still need a commit-index bump, and term advancement is handled manually when appending logs outside normal raft replication.

## Test Signals
The file contains many failpoints for scheduling, proposing, source checkpoint acquisition, merge execution, and apply result handling. There are no local unit tests in this file; coverage is integration-style through merge tests elsewhere plus invariants, panics, metrics counters, PD heartbeats, tombstone cleanup, and source peer destruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/commit.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/mod.rs

## Purpose
Defines shared merge module exports, source checkpoint path naming, and the source-region `MergeContext` state wrapper used by prepare, commit, rollback, and proposal control.

## Important APIs, Types, And Functions
The module exposes `commit`, `prepare`, and `rollback`. `MERGE_SOURCE_PREFIX` names source checkpoint tablets. `merge_source_path` derives the on-disk checkpoint path from a `TabletRegistry`, source region id, and prepare-merge commit index. `MergeContext` stores an optional `PrepareStatus` and provides `from_region_state`, `maybe_take_pending_prepare`, `max_compact_log_index`, and `prepare_merge_index`. Peer helpers include `update_merge_progress_on_became_follower`, `calculate_min_progress`, and `applied_merge_state`.

## Control Flow
When a peer is constructed from `RegionLocalState::Merging`, `from_region_state` recreates merge context as `PrepareStatus::Applied`, allowing restarted source peers to resume commit checks. Pending prepare proposals held behind a pessimistic-lock fence are released by `maybe_take_pending_prepare` once apply reaches the fence. Leaders use `calculate_min_progress` before prepare or commit scheduling to find the minimum matched and committed raft indexes across peers and to reject merge if any peer is snapshotting.

## State And Persistence Behavior
This file does not persist data directly, but it interprets persisted `RegionLocalState` and `MergeState` and maps them to in-memory `MergeContext`. The source checkpoint path is part of the persistent tablet layout and is later destroyed by commit or rollback cleanup. `prepare_merge_index` reflects the persisted merge state's commit index.

## Dependencies And Integration Points
Used by `prepare.rs` for fencing and source checkpoint creation, `commit.rs` for finding applied merge state and checkpoint paths, `rollback.rs` for cleanup, `control.rs` for merge proposal gating, and compact-log logic through `max_compact_log_index`.

## Risks And Edge Cases
`calculate_min_progress` rejects pending snapshots because merging a source peer with an invalid target snapshot state would be unsafe. It compensates for inaccurate raft progress when min matched is below min committed by raising matched to committed. Follower transitions clear transient trim/fence checks to avoid stale leader-only merge progress.

## Test Signals
There are no local tests. Signals are indirect through prepare/commit/rollback behavior, restart recovery from `PeerState::Merging`, assertions around merge status transitions, and logs warning when raft progress is inconsistent.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/prepare.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/prepare.rs

## Purpose
Implements `PrepareMerge`, the source-region phase that validates merge eligibility, fences in-memory pessimistic locks, persists `PeerState::Merging`, and creates the source checkpoint consumed by commit merge.

## Important APIs, Types, And Functions
`PreProposeContext` carries `min_matched` and remaining raft-entry size budget for transferred locks. `PrepareStatus` is the source merge FSM: `WaitForTrimStatus`, `WaitForFence`, `CatchUpLogs`, and `Applied`. `PrepareMergeResult` returns new region state and `MergeState`. Main peer methods are `propose_prepare_merge`, `validate_prepare_merge_command`, `check_logs_before_prepare_merge`, `start_check_trim_status`, `merge_on_availability_response`, `check_pessimistic_locks`, `retry_pending_prepare_merge`, `propose_locks_before_prepare_merge`, and `post_prepare_merge_fail`. Apply-side `apply_prepare_merge` mutates region state and checkpoints the tablet.

## Control Flow
Proposal first validates that source and target are sibling regions on the same stores and not in joint consensus. It then runs three ordered gates: availability/trim checks against source and target peers, raft-log gap and forbidden-admin scanning, and pessimistic-lock fencing. Trim checks send `MsgAvailabilityRequest` to all relevant peers and resume through a pre-flush callback with `PRE_FLUSH_FINISHED`. If locks exist and apply has not caught up to the last log, `WaitForFence` rejects new writes until apply reaches the fence, then the original request is retried. Locks are serialized as lock-CF puts before the actual `PrepareMerge` proposal. Apply increments both version and conf version, writes `MergeState`, flushes, and creates the merge-source checkpoint if missing. Peer apply result installs the new metadata, persists region state through state changes, enters prepare-merge mode, resolves any waiting catch-up logs, and starts commit merge.

## State And Persistence Behavior
Prepare merge persists `RegionLocalState` with `PeerState::Merging`, updated epoch, `MergeState { min_index, target, commit }`, and a source checkpoint at `merge_source_path(region_id, log_index)`. It also sets pessimistic lock status to `MergingRegion` while locks are transferred and resumes/cleans it on failure or rollback. In-memory state in `MergeContext` tracks async checks and is reconstructed from persisted state after restart only once apply has made the prepare durable.

## Dependencies And Integration Points
Depends on raft progress and log storage, `SimpleWriteReqDecoder` for scanning log payloads, lock CF serialization, tablet checkpointers, pre-flush infrastructure in admin/mod.rs, availability extra messages, `ProposalContext::PREPARE_MERGE`, `ProposalControl`, transaction lock tables, and commit merge startup.

## Risks And Edge Cases
Merge is rejected for dirty source tablets, missing/stale target metadata, non-sibling ranges, mismatched peer store sets, pending snapshots, excessive log gap, conf changes or epoch-changing admin logs in the gap, oversized embedded entries, and oversized pessimistic locks. The trim check has a timeout cleanup path because request ownership crosses callbacks. Failure after lock status changes must call `post_prepare_merge_fail` to return locks to normal.

## Test Signals
No local unit tests are defined here, but the file includes failpoints and extensive assertions. Integration signals include `prepare_merge` metrics, `PendingPrepareMerge` retry behavior, persisted `PeerState::Merging`, checkpoint creation, proposal rejection in merging mode, and subsequent `start_commit_merge`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/prepare.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/rollback.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/rollback.rs

## Purpose
Implements rollback for a prepared but uncommitted merge, returning the source region from `PeerState::Merging` to `Normal` and cleaning merge-mode in-memory state.

## Important APIs, Types, And Functions
`RollbackMergeResult` carries the prepare commit index and updated `RegionLocalState`. `Peer::on_reject_commit_merge` converts a target-side rejection into a local `RollbackMerge` admin proposal if the prepare index matches. `Apply::apply_rollback_merge` updates region state. `Peer::on_apply_res_rollback_merge` persists and installs the result. `Peer::rollback_merge` performs local cleanup and can also be called when a snapshot rolls back merge without a proposal.

## Control Flow
If a target peer rejects commit merge due to stale epoch, the source peer checks that its applied prepare index equals the rejection index, builds a rollback admin request, and passes it through normal admin proposal handling. Apply verifies the local state is `Merging` and the requested commit equals the persisted merge state, bumps region version to avoid duplicate rollback ambiguity, clears merge state, and returns a result. Peer result handling updates store metadata/readers, writes the new local state to the state-change batch, updates storage, and calls `rollback_merge` to leave merge mode.

## State And Persistence Behavior
Rollback persists the source region as `PeerState::Normal` with merge state removed and region version incremented. Cleanup records the source checkpoint path as a tombstone tablet path rather than deleting immediately, leaves `ProposalControl` prepare-merge mode, drops `MergeContext`, resumes read progress, and restores pessimistic lock status to normal on leaders.

## Dependencies And Integration Points
Uses `merge_source_path`, admin request construction, `ProposalContext::ROLLBACK_MERGE` via admin dispatch, `RegionChangeReason::RollbackMerge`, state-change persistence, read progress, lock status, PD heartbeat, and target rejection messages from `commit.rs`.

## Risks And Edge Cases
Index mismatches are ignored before proposing but panic during apply/result handling if persisted state does not match the rollback request. Cleanup assumes an applied prepare merge exists. The checkpoint is deliberately retained for tombstone cleanup so restarts can avoid rebuilding or leaking it.

## Test Signals
There are no local tests. Signals are rollback admin metrics, logs for ignored stale rejections, panics for inconsistent merge state, state-change writes, read-progress resume, lock status normalization, and PD heartbeat after leader rollback.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/merge/rollback.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/mod.rs

## Purpose
Central admin-command dispatcher for raftstore-v2 peers. It validates, routes, proposes, and post-processes admin commands such as split, compact log, conf change, transfer leader, merge, flashback, and GC peer updates.

## Important APIs, Types, And Functions
`AdminCmdResult` is the apply-to-peer side-effect enum consumed by `command/mod.rs`. `Peer::on_admin_command` is the main entry point. `on_prepare_merge` adjusts raft inflight behavior for merge under disk pressure. `start_pre_flush` schedules tablet flushes and sends `MsgFlushMemtable` extra messages to follower voters. The module re-exports merge and split helpers including `MergeContext`, `CatchUpLogs`, `SplitInit`, `SplitFlowControl`, and tablet path helpers.

## Control Flow
`on_admin_command` rejects non-serving peers and non-admin requests, invokes coprocessor pre-propose hooks, validates store/peer/term/epoch through `validate_command`, checks disk-full policy except for transfer-leader warmup and conf changes, and requires applied-to-current-term for most admin commands. It delays conflicting commands through `ProposalControl`, rejects most proposals during pending/applied prepare merge, triggers merge-specific disk-full handling, drains pending simple writes to preserve ordering, then dispatches by `AdminCmdType`. Batch split performs an asynchronous pre-flush phase before reproposing with `PRE_FLUSH_FINISHED`. Transfer leader either runs the warmup protocol or proposes a flagged transfer-leader log. Merge, flashback, compact log, conf change, and GC updates delegate to their submodules or raw `propose`.

## State And Persistence Behavior
This file mainly coordinates proposal state rather than applying persistence. Successful admin proposals are recorded in `ProposalControl` and may disable commit broadcast skipping until uncommitted admin work is resolved. `start_pre_flush` can cause tablet memtables to flush before split or merge proposals, reducing checkpoint cost and improving availability under disk pressure.

## Dependencies And Integration Points
Integrates with `StoreContext`, coprocessor host, raft metrics, `ProposalControl`, write batching, split/merge/flashback/conf-change submodules, disk-full peer context, router mailbox resubmission, tablet scheduler, and raft extra messages.

## Risks And Edge Cases
Admin ordering depends on draining pending writes before proposing admin logs. Merge mode rejects most commands to protect source-region invariants. Batch split and prepare/commit merge use callbacks through router mailboxes, so shutdown paths must tolerate missing mailboxes. Disk-full logic intentionally allows transfer leader, conf change, and merge-related flows under narrower rules.

## Test Signals
No tests are local to this file. Signals are covered by submodule tests and integration behavior: proposal metrics, delayed conflict callbacks, admin result handling, pre-flush resubmission, disk-full rejection paths, and fail-fast panics for unimplemented admin types.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/split.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/split.rs

## Purpose
Implements raftstore-v2 batch split: split checks, split request handling, apply-time physical tablet checkpointing, parent peer metadata updates, and initialization of new split peers.

## Important APIs, Types, And Functions
`SplitResult` returns the new regions, derived-region index, tablet index, size sharing flag, and new derived tablet. `SplitInit` carries a new region snapshot, inherited locks, metrics, and derived-leader hints. `RequestSplit`, `RequestHalfSplit`, `SplitFlowControl`, `SplitPendingAppend`, `temp_split_path`, and `report_split_init_finish` support scheduling and initialization. Main methods include `on_split_region_check`, `on_request_split`, `on_request_half_split`, `propose_split`, `apply_batch_split`, `on_apply_res_split`, `on_split_init`, `post_split_init`, `on_split_init_finish`, and `on_tablet_trimmed`.

## Control Flow
Leaders schedule split checks when approximate size/key updates or apply size deltas exceed thresholds, unless snapshot generation or busy split-check workers defer work. Manual split requests validate leadership, clean tablet state, disk-full policy, epoch, and key ordering before asking PD for split ids. Applying batch split validates requests, computes region boundaries and epochs, flushes existing writes, checkpoints the current tablet for all child regions and the derived parent tablet, opens the derived tablet, and updates apply-side region state. Peer apply result splits in-memory pessimistic locks, updates store metadata/read tablet under lock, tombstones the previous tablet, trims dirty data asynchronously, notifies PD, sends `SplitInit` to child peers or store control, and tracks child init completion before marking admin flush.

## State And Persistence Behavior
Split creates temporary child tablets under `SPLIT_PREFIX` and a derived tablet at `tablet_path(parent_id, split_log_index)`. Apply-side region state gets the derived region and tablet index but peer-side `state_changes_mut().put_region_state` and dirty mark persistence complete the durable metadata update. Dirty tablets are trimmed asynchronously; `on_tablet_trimmed` clears dirty marks and storage dirty-data state. Child peers initialize from synthetic snapshots with raft init index/term.

## Dependencies And Integration Points
Depends on split-check scheduler, PD split id/reporting paths, tablet checkpointers, raft snapshot metadata, `StoreMeta` readers, shared read tablets, transaction lock splitting, tablet trim worker, router/store control messages, `ApplyMetrics`, and admin validation from raftstore.

## Risks And Edge Cases
Splitting dirty tablets is rejected to avoid repeated trim compaction work. The first append message for a new split peer may be held while parent split initialization races. Shutdown during callback routing is tolerated. Derived-left versus derived-right changes peer id assignment and region boundaries. Approximate size/key sharing is heuristic. Crash/restart safety relies on atomic checkpoints and persisted dirty marks.

## Test Signals
`test_split` exercises invalid peer id counts, empty split requests, out-of-range and empty keys, non-ascending keys, right/left derive layouts, multi-split epoch updates, child peer ids, checkpoint paths, and forced flush of pending writes before split. Runtime signals include split metrics, PD batch split reports, split trace completion, dirty mark writes, and failpoints.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/split.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/transfer_leader.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/transfer_leader.rs

## Purpose
Implements raftstore-v2 transfer-leader handling, including a pre-transfer readiness protocol that warms entry cache and optionally drains pessimistic locks before raft leadership transfer.

## Important APIs, Types, And Functions
`transfer_leader_cmd` extracts `TransferLeaderRequest`. `Peer::propose_transfer_leader` selects a transferee and sends pre-transfer messages. `pre_transfer_leader`, `on_transfer_leader_msg`, `maybe_reject_transfer_leader_msg`, `set_pending_transfer_leader_msg`, `maybe_ack_transfer_leader_msg`, `maybe_transfer_leader_cache_warmup`, `ack_transfer_leader_msg`, and `ready_to_transfer_leader` implement the message lifecycle. `Apply::apply_transfer_leader` and `Peer::on_transfer_leader` handle the optional proposed transfer-leader command.

## Control Flow
The current leader picks the candidate with the highest matched index from requested peers, randomizing ties, and sends `MsgTransferLeader` with the leader's entry-cache first index and term. A follower rejects if it is snapshotting, the sender is not the current leader, or disk-full conditions would reduce availability; otherwise it stores the message and waits until cache warmup and coprocessor pre-ack hooks are ready or a deadline expires. It then ACKs with its applied index. When the leader receives the ACK, it checks voter membership, pending snapshots, pending conf changes, and log lag. If locks must be proposed first, it proposes a flagged `TransferLeader` admin command; after the target applies that command it ACKs with `CommandReply`. Otherwise the leader calls raft `transfer_leader`.

## State And Persistence Behavior
Most state is transient in transfer-leader state: pending message, deadline, and cache warmup range. The optional `TransferLeader` admin command is replicated but only returns `AdminCmdResult::TransferLeader` when the expected new leader is the local peer; it does not mutate region metadata. Cache warmup state is reset when stale and updated as async cache population progresses.

## Dependencies And Integration Points
Integrates with raft progress/status, entry cache warmup, coprocessor `pre_ack_transfer_leader`, transaction lock proposal before transfer, admin dispatch flags, disk usage, config timing, and raft message queues.

## Risks And Edge Cases
Transfer is refused for learners/non-voters, pending snapshots, pending conf changes, log gaps beyond `leader_transfer_max_log_lag`, wrong term, and unsafe disk-full combinations. Deadlines prevent indefinite cache warmup blocking. Rolling upgrade compatibility is handled by accepting index zero. Term mismatch during apply causes stale transfer commands to be ignored.

## Test Signals
No tests are local here. Signals include transfer-leader proposal metrics, logs for rejection reasons, cache warmup state transitions, ACK messages with applied indexes, and raft transferee refresh after `transfer_leader`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/transfer_leader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/control.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/control.rs

## Purpose
Provides proposal conflict control for raftstore-v2, replacing the older epoch checker by tracking proposed/admin-applied lifetimes and merge-mode gating.

## Important APIs, Types, And Functions
`ProposedAdminCmd` records admin type, committed flag, epoch-change state, raft index, and delayed response channels. `ProposalControl` stores a small ordered list of proposed admin commands, pending prepare-merge flag, applied prepare-merge index, and current term. Key methods are `maybe_update_term`, `check_conflict`, `record_proposed_admin`, `commit_to`, `advance_apply`, `set_pending_prepare_merge`, `enter_prepare_merge`, `leave_prepare_merge`, `is_splitting`, and `is_merging`.

## Control Flow
Before proposing normal or admin work, callers use `check_conflict` with either no admin type or an admin type. The method compares the candidate's epoch checks against already proposed admin commands and treats `PrepareMerge` as a universal conflict. Conflicting callbacks are delayed instead of immediately failed. Once raft commits indexes, `commit_to` marks proposed admins as committed and can trigger hooks. Once apply reaches indexes, `advance_apply` returns delayed channels with epoch-not-match responses based on the current region. Term increases stale all delayed work and clear the queue.

## State And Persistence Behavior
All state is in memory and rebuilt from peer/apply state after restart. The applied prepare-merge index mirrors durable merge state and makes `is_merging` true even after the proposal queue has advanced. Dropping `ProposalControl` notifies delayed callbacks with stale-command errors to avoid hanging clients.

## Dependencies And Integration Points
Uses raftstore admin epoch lookup, normal request epoch-check flags, `CmdResChannel`, apply notification helpers, and `AdminCmdType`. It is called by admin dispatch, simple-write handling, apply result advancement, merge prepare/rollback, and split status checks.

## Risks And Edge Cases
Correctness depends on recording only epoch-changing admin commands and maintaining increasing indexes. Term regression panics. Delayed callbacks intentionally receive epoch-not-match after the conflicting admin applies, encouraging clients to refresh region metadata instead of retrying with blind backoff.

## Test Signals
`test_proposal_control` covers conflict detection, commit/apply transitions, delayed callback delivery, term-change stale responses, and drop cleanup. `test_proposal_control_merge` covers prepare-merge committed state, applied merge mode, and leaving merge mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/control.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/mod.rs

## Purpose
Top-level replicated command pipeline for raftstore-v2. It validates proposals, appends raft entries, schedules committed entries to apply FSMs, applies normal/admin commands in order, flushes write batches, reports apply results, and drives peer-side state updates.

## Important APIs, Types, And Functions
`parse_at` decodes protobuf messages with panic-on-corruption diagnostics. `CommittedEntries` batches raft entries with proposal callbacks. `new_response` preserves request UUIDs. Peer methods include `schedule_apply_fsm`, `validate_command`, `propose`, `propose_with_ctx`, `post_propose_command`, `schedule_apply_committed_entries`, `on_apply_res`, and `post_propose_fail`. `ApplyFlowControl` and apply methods `apply_committed_entries`, `apply_entry`, `maybe_flush`, `flush`, and `apply_unsafe_write` form the apply worker core.

## Control Flow
Leaders validate store id, peer id, leadership, term, region epoch, force-leader state, and flashback state before proposing. Proposals are appended through raft and stored with callbacks and waterfall metrics. Committed raft entries are matched to proposal callbacks and sent to the apply FSM. Apply decodes simple-write batches first, otherwise decodes admin/conf-change requests, validates epochs and flashback state, dispatches to write/admin handlers, records admin results, and buffers callbacks. `flush` writes the tablet write batch with WAL disabled, updates flush state applied index in the write callback, reports `ApplyRes`, flushes observers, and then resolves client callbacks.

## State And Persistence Behavior
Raftstore-v2 relies on raft engine persistence before kv/tablet memtable flushes, so it does not persist commit index/term in kv apply state like v1. Data writes are staged in `write_batch` and flushed to tablet with applied index in `FlushState`. Apply results carry admin side effects, data CF modifications, metrics, bucket stats, and SST applied indexes back to peer FSM. Peer-side `on_apply_res` updates raft applied index/term, entry cache, proposal control, read progress, split flow control, storage stats, apply trace, and recovery state.

## Dependencies And Integration Points
Re-exports admin/write/control APIs and integrates with raft, raftstore proposal queues, apply pools, tablet registry/scheduler, read progress, coprocessor observers, PD bucket metadata, flashback checks, simple-write codec, conf-change modules, split/merge/flashback/admin handlers, and metrics.

## Risks And Edge Cases
Silent raft proposal drops are converted to `NotLeader`. Force-leader mode panics on ordinary proposals except rollback merge. Apply uses savepoints to roll back partial batch work on command errors. Corrupted entry payloads panic. Flow control yields by time or written bytes and can trigger manual flush when apply trace needs it. Callbacks are delayed until after apply results are reported so subsequent messages observe admin side effects.

## Test Signals
Local tests are in submodules, while this file exposes failpoints for apply handling and report skipping. Observable signals include proposal/apply histograms, write trackers, apply result side effects, admin result dispatch, callback ordering, and recovery/flush traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/ingest.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/ingest.rs

## Purpose
Handles raftstore-v2 ingest-SST write application and periodic cleanup of stale imported SST files.

## Important APIs, Types, And Functions
`StoreFsmDelegate::on_cleanup_import_sst` schedules periodic cleanup ticks. `Store::on_cleanup_import_sst` scans importer state and routes stale SSTs by region. `Peer::on_cleanup_import_sst` filters SSTs whose epochs are stale relative to the peer flushed epoch and schedules tablet cleanup. `Apply::apply_ingest` validates, ingests, tracks, and accounts SST files during apply.

## Control Flow
The store cleanup tick measures importer total size, lists API v2 SSTs, groups them by region id, and sends `PeerMsg::CleanupImportSst` to live peers. If a peer mailbox is disconnected and the router is not shutting down, it filters out SSTs overlapping current import ranges and schedules direct tablet cleanup. A peer receiving cleanup compares SST region epochs with its flushed epoch and deletes/schedules only stale files. During apply, each SST is checked against region bounds, validated by importer metadata, skipped if log recovery already applied that CF/index, flushed before ingest, ingested into the local tablet, registered in `SstApplyState`, bucket stats and metrics are updated, and per-CF SST applied indexes are recorded.

## State And Persistence Behavior
Ingest modifies tablet data by external SST ingestion after flushing pending writes. Applied SST metadata is registered in `SstApplyState` so later cleanup can reason about imported files. `push_sst_applied_index` records per-CF apply trace information. Cleanup removes stale importer files and updates importer-size metrics but does not alter raft region state.

## Dependencies And Integration Points
Depends on `sst_importer`, `check_sst_for_ingestion`, region epoch utilities, tablet cleanup scheduler, importer range overlap checks, store ticks, `ApplyRes` SST applied index propagation, bucket statistics, and PD store-size metrics.

## Risks And Edge Cases
Importer validation failure for a corrupt SST panics, while region-bound check failure deletes the offending SST and returns an apply error. Cleanup must not remove files still in an active import range. Ingest cannot batch across regions in v2, so apply flushes before ingest. Log recovery can skip already applied CF indexes.

## Test Signals
No local tests are defined here. Signals include `ingest_sst` counters, importer size gauge, logs for stale cleanup, `SstApplyState` registrations/deletions, bucket ingest stats, and failpoints around cleanup scheduling and apply ingest.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/ingest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/mod.rs

## Purpose
Implements simple write proposal batching and apply-side put, delete, delete-range, unsafe-write, and ingest integration for raftstore-v2.

## Important APIs, Types, And Functions
Re-exports `SimpleWrite`, `SimpleWriteBinary`, `SimpleWriteEncoder`, and `SimpleWriteReqDecoder`. Peer methods `on_simple_write`, `on_unsafe_write`, and `propose_pending_writes` coordinate proposal-side batching. Apply methods `apply_put`, `apply_delete`, and `apply_delete_range` modify tablets. The `ingest` submodule extends this with SST ingest.

## Control Flow
`on_simple_write` first amends an existing encoder if possible, otherwise validates command headers, deadline and disk-full options, drains pending writes to preserve order, delays behind conflicting admin proposals, rejects merge mode, and creates a new `SimpleWriteReqEncoder` bounded by raft entry size ratio. `propose_pending_writes` revalidates the encoder header, encodes batched data, proposes it, and posts callbacks. `on_unsafe_write` bypasses raft by sending an `ApplyTask::UnsafeWrite` to the local apply scheduler. Apply paths check log recovery skip state, validate keys against region bounds, update bucket write stats, prefix keys with data encoding, write/delete via default or named CF APIs, adjust size hints, and record per-CF modification indexes. Delete range validates bounds/CFs and schedules a tablet delete-range task unless `notify_only`.

## State And Persistence Behavior
Simple writes are persisted through raft, then applied into a tablet write batch that `command/mod.rs` flushes. Modification indexes track which data CFs changed at which raft index. Delete-range can perform asynchronous file/range deletion through the tablet worker and only records modifications when the worker reports data was written. Unsafe writes use `u64::MAX` indexes and force an apply flush need without raft durability.

## Dependencies And Integration Points
Depends on command validation/proposal logic, `ProposalControl`, disk-full policy, raftstore simple-write codec, tablet scheduler, engine CF helpers, bucket stats, apply flow control, and `ingest.rs` for SST writes.

## Risks And Edge Cases
Amending batched writes must keep a compatible header and size budget. Epoch-not-match proposals deliberately avoid calling proposed callbacks. Merge mode blocks normal writes. Delete-range must handle inclusive region end-key validation and invalid CF names. RocksDB/tablet APIs require prefixed data keys even though raftstore-v2 has isolated tablets.

## Test Signals
`test_delete_range` builds a test tablet, applies a put through committed entries, verifies the prefixed key exists, applies delete-range, and verifies removal. Additional signals are write command counters, failpoints after pending-write proposal and apply put, size-diff hints, and modification indexes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/disk_snapshot_backup.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/disk_snapshot_backup.rs

## Purpose
Provides a placeholder `SnapshotBrHandle` implementation for raftstore-v2, explicitly reporting that snapshot backup is unsupported.

## Important APIs, Types, And Functions
`UnimplementedHandle` is a clone/copy zero-sized type implementing `raftstore::store::snapshot_backup::SnapshotBrHandle`. The implemented methods are `send_wait_apply`, `broadcast_wait_apply`, and `broadcast_check_pending_admin`. All return `crate::Error::Other` with the shared reason string.

## Control Flow
There is no operational backup flow. Any snapshot-backup caller using this handle immediately receives an error that names the unsupported method and notes that raftstore-v2 does not support snapshot backup yet.

## State And Persistence Behavior
The type has no state and performs no persistence, message routing, or channel sends. The `broadcast_check_pending_admin` method accepts an `UnboundedSender<CheckAdminResponse>` but deliberately does not use it.

## Dependencies And Integration Points
Depends on the snapshot backup trait and request/response protobuf types from raftstore/kvproto. It is an integration shim that lets the broader store compile while making unsupported raftstore-v2 snapshot BR behavior explicit at runtime.

## Risks And Edge Cases
The main risk is operational: callers must surface this unsupported error clearly and avoid assuming snapshot backup works for raftstore-v2. Since every method fails synchronously, no partial state is created.

## Test Signals
There are no local tests. Expected signal is the exact error path from callers invoking snapshot backup APIs under raftstore-v2.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/disk_snapshot_backup.rs -->
