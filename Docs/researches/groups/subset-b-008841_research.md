# subset-b-008841 research

This grouped report covers the raftstore-v2 snapshot, unsafe recovery, raft wrapper, routing, and PD worker files listed in work item `subset-b-008841`. Each section preserves the original source path for downstream reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/snapshot.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/snapshot.rs

Purpose: this file owns raftstore-v2 tablet snapshot generation, validation, application, and cleanup. It bridges raft's `Storage::snapshot` callback, apply-worker tablet snapshot generation, received tablet installation, raft metadata persistence, and post-apply peer recovery.

Important APIs/types/functions: `SnapState` tracks per-target-peer snapshot lifecycle: `Relax`, `Generating`, `Generated`, `Sending`. `GenSnapTask` carries region/to-peer plus cancellation/index atomics and a load-balance marker. `recv_snap_path` derives final received tablet paths. `install_tablet` atomically moves a generated/received tablet into the `TabletRegistry`, integrating encryption key-manager link/remove operations. Peer methods include `maybe_schedule_gen_snapshot`, `on_snapshot_generated`, `on_snapshot_sent`, `on_applied_snapshot`, and `on_snap_gc`. Apply exposes `schedule_gen_snapshot`. Storage exposes `snapshot`, `validate_snap`, cancellation helpers, `on_snapshot_generated`, `on_applied_snapshot`, and `apply_snapshot`.

Control flow: raft asks `Storage::snapshot(request_index, to)`. Existing generated/sending snapshots are validated and reused; generating snapshots return `SnapshotTemporarilyUnavailable`; dirty post-split tablets delay generation. A new request creates atomics, records `SnapState::Generating`, and stores `GenSnapTask`. The peer later sends that task to apply, apply flushes, records the latest applied index/term, and schedules `ReadTask::GenTabletSnapshot`. Completion returns to the peer, which updates storage state and pings raft. Applying a received snapshot decodes `RaftSnapshotData`, clears stale raft logs, rewrites apply/region/flushed-index state, records a persisted callback to install the tablet, and marks `task.has_snapshot`.

State and persistence: raft log state, apply state, region local state, tablet index, dirty marks, flushed indexes for all CFs, and removed/merged records are persisted through `WriteTask`/extra v2 log batches. Tablet directory installation is intentionally deferred to `persisted_cbs` so filesystem visibility follows raft-engine persistence. `on_applied_snapshot` reopens the tablet, resets flush/read progress, updates store metadata readers, handles implicit merge rollback, split init, tombstone tablet cleanup, and deferred split append messages.

Dependencies/integration: depends on `engine_traits` tablet registry/log batches, raft snapshots, `raftstore::store` read/write tasks and snap manager, encryption key manager, coprocessor region-change hooks, `ApplyResReporter`, and tablet worker GC. It integrates with split initialization via `temp_split_path` and `SplitInit`.

Risks: ordering is critical: installing a tablet before persisted metadata would expose inconsistent storage. Cancellation uses shared atomics and per-peer state; stale generated snapshots must be rejected by index/epoch. Dirty split tablets intentionally block snapshots, so incorrect dirty-mark handling could starve replication. `install_tablet` panics on rename/link failures, so abort recovery around temp tablet creation remains sensitive.

Test signals: `raft/storage.rs` contains tests for applying snapshots, generating snapshots, cancellation, and state transitions that exercise these APIs. Failpoints include `apply_snapshot_complete`, `post_split_init_complete`, and `region_apply_snap`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/txn_ext.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/txn_ext.rs

Purpose: this file manages transaction-side extensions tied to raftstore-v2 peer leadership: max timestamp synchronization, in-memory pessimistic lock lifecycle, lock movement during split, and lock persistence before leader transfer.

Important APIs/types/functions: `TxnContext` wraps `Arc<TxnExt>`, an atomic `ExtraOp`, and a tick counter for memory-lock reactivation. Key methods are `on_region_changed`, `on_became_leader`, `after_commit_merge`, `on_became_follower`, `split`, `init_with_lock`, and private `require_updating_max_ts`. Peer methods are `on_reactivate_memory_lock_tick` and `propose_locks_before_transfer_leader`.

Control flow: when a peer becomes leader or after merge, `require_updating_max_ts` encodes term and region version into `max_ts_sync_status`, then schedules `pd::Task::UpdateMaxTimestamp`; PD worker later advances the concurrency manager. Leadership changes update `PeerPessimisticLocks` status, term, and version. Before transfer-leader, the peer decodes `TransferLeaderContext`, disables in-memory locks by moving status to `TransferringLeader`, schedules a reactivation tick, encodes all non-deleted lock CF entries into a simple write, and proposes them before actual transfer if needed.

State and persistence: the in-memory pessimistic-lock map is guarded by `RwLock`; lock table version is deliberately advanced on split so concurrent readers fail with epoch mismatch instead of lock-not-found. Persistent lock materialization uses `SimpleWriteEncoder` against `CF_LOCK`, with `DiskFullOpt::AllowedOnAlmostFull` so transfer safety is not blocked by almost-full disk mode.

Dependencies/integration: depends on `raftstore::store::TxnExt`, `PeerPessimisticLocks`, transfer-leader context encoding, `SimpleWriteEncoder`, peer ticks, and PD worker timestamp update tasks. It ties into split admin handling through returned grouped locks.

Risks: the transfer path has a FIXME about raft command size limits when many locks are encoded. Status/tick ordering around `lead_transferee` is delicate; reactivation too early can reopen memory locks while transfer is still pending. Max-ts status uses packed low bits, so stale async PD responses are filtered only by exact atomic status.

Test signals: no direct unit tests in this file. Coverage is implied by leader transfer, pessimistic transaction, split, and merge integration tests elsewhere; failpoint `invalidate_locks_before_transfer_leader` targets the persistence window.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/txn_ext.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/create.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/create.rs

Purpose: this file creates missing peers during unsafe recovery by reusing raftstore-v2 split initialization, because v2 peers are normally initialized only through snapshots/tablets.

Important APIs/functions: `Store::on_unsafe_recovery_create_peer` performs store-level creation. `Peer::on_unsafe_recovery_wait_initialized` records a wait state, and `unsafe_recovery_maybe_finish_wait_initialized` clears it once storage is initialized or force-finished.

Control flow: the store first checks `StoreMeta.region_ranges` for overlap with the target region. Existing same-region creation becomes a no-op; overlapping different regions aborts. It then creates an empty tablet under `temp_split_path` with tablet index `RAFT_INIT_LOG_INDEX`, constructs a `SplitInit` with no derived region, and calls `on_split_init` with `skip_if_exists`. Finally it force-sends `PeerMsg::UnsafeRecoveryWaitInitialized` to the new region so the peer can hold the execution syncer until initialization finishes.

State and persistence: creation writes an empty temporary tablet through the tablet factory before split initialization. The subsequent split-init path is responsible for moving peer/region state toward initialized status. Peer state stores `UnsafeRecoveryState::WaitInitialize(syncer)` unless a non-aborted unsafe recovery state is already active.

Dependencies/integration: depends on `StoreMeta` range indexes, TiKV key encoding helpers for overlap checks, `TabletRegistry`, `SplitInit`, `PeerPessimisticLocks`, and router force-send. It integrates with unsafe recovery execution syncers from raftstore and with normal split-init peer creation machinery.

Risks: the source TODO notes recovery from abort after opening the temporary tablet is incomplete. The overlap check must be exact, or unsafe recovery could create overlapping peers. If a peer already exists, split-init is skipped because peer FSM cannot process concurrent split-init messages. Syncer lifetime depends on the peer receiving the wait message before being destroyed.

Test signals: no local tests in this file. Coverage should come from unsafe recovery create-peer and split-init integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/create.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/demote.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/demote.rs

Purpose: this file demotes failed voters during unsafe recovery after a peer has entered force-leader mode, restoring a valid quorum configuration.

Important APIs/functions: Peer methods are `on_unsafe_recovery_pre_demote_failed_voters`, `unsafe_recovery_demote_failed_voters`, and `unsafe_recovery_maybe_finish_demote_failed_voters`.

Control flow: pre-demotion rejects concurrent non-aborted recovery state and requires `is_in_force_leader`. If the region is already in joint state, it first proposes an `exit_joint_request`, then stores `UnsafeRecoveryState::DemoteFailedVoters` with `demote_after_exit=true` and target last index. Otherwise it constructs `demote_failed_voters_request`, proposes it as an admin command, and stores a demotion wait state with target last index. The check method waits until raft applied reaches the target. If it was only exiting residual joint state, it re-enters demotion; otherwise it may issue a final exit-joint command and clears state.

State and persistence: the actual configuration changes are raft admin commands. The unsafe recovery state records the syncer, failed voters, target index, and whether a second-stage demotion is needed after exiting joint state. Errors may set `UnsafeRecoveryState::Failed`.

Dependencies/integration: depends on raftstore helper constructors `demote_failed_voters_request` and `exit_joint_request`, `CmdResChannel` for immediate command response inspection, force-leader state from `force_leader.rs`, and periodic `check_unsafe_recovery_state` from `report.rs`.

Risks: losing force leadership between exit-joint and demotion aborts progress. Immediate `try_result` only observes synchronous command errors; later apply failures are represented by waiting/apply state. Joint-state transitions are multi-stage and must preserve target indexes to avoid clearing state before commands apply.

Test signals: no direct tests here. It should be covered by unsafe recovery and joint-consensus integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/demote.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/destroy.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/destroy.rs

Purpose: this small file initiates peer destruction as an unsafe recovery plan action.

Important API/function: `Peer::on_unsafe_recovery_destroy_peer(syncer)` validates unsafe recovery state and marks the peer for destruction.

Control flow: if another non-aborted unsafe recovery state exists, it logs a warning, aborts the incoming syncer, and returns. Otherwise it stores `UnsafeRecoveryState::Destroy(syncer)` and calls `mark_for_destroy(None)`. The syncer is intentionally retained in peer state until the normal destroy path completes and drops it.

State and persistence: this file does not directly write storage; it triggers existing peer destroy machinery. The state marker is important because the recovery coordinator is synchronized by the syncer lifetime.

Dependencies/integration: depends on `UnsafeRecoveryExecutePlanSyncer`, `UnsafeRecoveryState`, and peer lifecycle methods from other operation modules.

Risks: if destroy progress does not drop the state/syncer, unsafe recovery execution can hang. Concurrent plan handling is intentionally strict; only aborted states permit replacement.

Test signals: no local tests. Expected coverage is unsafe recovery destroy-plan integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/destroy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/force_leader.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/force_leader.rs

Purpose: this file implements the unsafe recovery force-leader state machine, allowing one surviving peer to temporarily become leader without normal quorum so it can commit recovery configuration changes.

Important APIs/functions: Peer methods include `on_enter_pre_force_leader`, `on_force_leader_fail`, `on_enter_force_leader`, `on_exit_force_leader`, `on_exit_force_leader_campaign`, `check_force_leader`, and `maybe_force_forward_commit_index`. Helper `get_force_leader_expected_alive_voter` filters voters by failed stores.

Control flow: entering pre-force-leader first handles existing force-leader state, rejects uninitialized peers, and may wait election ticks so leader lease/check-quorum can expire. It rejects if expected alive voters still form quorum. It disables prevote, campaigns, verifies self vote, and stores `ForceLeaderState::PreForceLeader`. `check_force_leader` later waits near election timeout, validates votes only from expected alive voters, and if all grant, synthesizes vote responses from failed-store voters to transition raft to leader. In force-leader state, it disables check quorum and may advance commit index to the minimum matched/persisted index among non-failed stores when the term matches. Exiting restores follower role, check quorum, prevote, and optionally schedules a fresh campaign.

State and persistence: force leadership is an in-memory `ForceLeaderState`; raft term/vote/role/check-quorum/prevote fields are mutated directly. Commit advancement changes raft log committed index and requires ready processing via `set_has_ready`.

Dependencies/integration: depends on raft `RawNode` internals, progress tracker votes, `LeaseState`, unsafe recovery state, peer router campaign message, and store config election ticks.

Risks: the code deliberately violates normal raft election rules; incorrect failed-store input can create split brain. Lease expiration checks guard stale leaders, but clock/tick assumptions matter. Commit forwarding refuses previous-term logs, reducing but not eliminating recovery hazards. `WaitForceCompact` is marked unreachable in v2 paths.

Test signals: no direct tests in this file. Coverage should be in unsafe recovery force-leader integration and failover tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/force_leader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/mod.rs

Purpose: this module file groups unsafe recovery operation extensions for raftstore-v2 peers and store FSMs.

Important APIs/types/functions: it declares private submodules `create`, `demote`, `destroy`, `force_leader`, and `report`. The public API is provided by inherent impl blocks in those files on `Store` and `Peer`.

Control flow: importing this module compiles all unsafe recovery handlers into the broader `operation` module. Dispatch occurs through router messages and peer/store handlers elsewhere; this file itself contains no runtime logic.

State and persistence: no direct state. State is owned by submodules via `ForceLeaderState`, `UnsafeRecoveryState`, raft admin proposals, split-init creation, and destroy progress.

Dependencies/integration: serves as the integration point tying unsafe recovery operations into raftstore-v2 operation compilation.

Risks: because all submodules are private and expose inherent methods, missing this module import would silently remove unsafe recovery behavior from operation builds.

Test signals: no tests here; testing is by submodule behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/report.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/report.rs

Purpose: this file handles unsafe recovery reporting and wait-for-apply/report-status peer operations.

Important APIs/functions: `Store::on_unsafe_recovery_report` sends a store heartbeat with an optional recovery report. Peer methods include `on_unsafe_recovery_wait_apply`, `unsafe_recovery_maybe_finish_wait_apply`, `on_unsafe_recovery_fill_out_report`, and `check_unsafe_recovery_state`.

Control flow: wait-apply rejects conflicting non-aborted states, chooses target index as last index in force-leader mode or committed index otherwise, and records `UnsafeRecoveryState::WaitApply` until applied catches up or serving is gone. Fill-out report gathers raft state and region state, marks force-leader status, scans uncommitted entries for `COMMIT_MERGE` proposal context, and reports through the syncer. The periodic checker advances wait-apply, wait-initialize, and demote states.

State and persistence: no writes are performed here except through state clearing. The report serializes current raft local state and region local state into PD protobufs, plus derived flags.

Dependencies/integration: depends on raft `Storage::entries`, `ProposalContext`, PD report protobufs, unsafe recovery syncers, and the demotion/create modules through checker calls.

Risks: scanning uncommitted entries panics on storage errors; recovery reporting assumes raft log access is reliable. Wait targets differ in force-leader mode because proposed logs are expected to become committed by force-forwarding.

Test signals: no local tests. Integration tests should verify reports include commit-merge and force-leader markers and that wait states clear only after apply.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/report.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/apply.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/raft/apply.rs

Purpose: this file defines the raftstore-v2 apply-side state object that applies committed raft commands to a tablet and reports apply results.

Important APIs/types/functions: `Observe` tracks coprocessor observation info. `Apply<EK, R>` contains peer identity, current tablet, write batch, region state, apply progress, data-modification trace, callback queue, apply flow control, flush/SST state, log recovery trace, schedulers, importer, coprocessor host, metrics, logger, and bucket stats. Methods are mostly accessors and state mutators: `new`, `ensure_write_buffer`, `set_apply_progress`, `apply_progress`, `set_tablet`, callback/admin-result handling, `release_memory`, trace and flow-control accessors, and scheduler/importer accessors.

Control flow: construction loads the latest tablet from `TabletRegistry`, derives current applied index from `FlushState`, initializes perf context, and rejects `use_delete_range` for v2. Applying command logic lives in other operation files, but those paths mutate this structure as the single apply FSM state. `set_apply_progress` also clears `log_recovery` once all CF replay targets are reached.

State and persistence: `Apply` buffers writes in an engine write batch and tracks modifications separately from `flush_state`; comments emphasize that apply progress is updated after each command, but flush state must not be advanced immediately because manual flushes from other threads could observe an incorrect index. `sst_apply_state` and `sst_applied_index` coordinate SST ingestion visibility.

Dependencies/integration: integrates with engine traits, `TabletRegistry`, raftstore apply metrics/config, coprocessor observation, SST importer, tablet worker, read scheduler, and result reporter. Snapshot generation in `snapshot.rs` uses `apply_progress`, `flush`, tablet clone, and read scheduler.

Risks: exposing a new tablet before pending write batch is empty would mismatch tablet content and epoch, so `set_tablet` asserts an empty batch. Incorrect modification tracing can let raft logs be deleted before CF data is flushed. Log recovery depends on per-CF indexes being accurate.

Test signals: direct tests are not in this file, but snapshot/storage tests construct `Apply::new` and exercise snapshot scheduling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/apply.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/raft/mod.rs

Purpose: this is the public module facade for raftstore-v2 raft wrapper types.

Important APIs/types/functions: it declares submodules `apply`, `peer`, and `storage`, then re-exports `Apply`, `Peer`, and `Storage`.

Control flow: no runtime control flow exists here. It defines the module boundary used by operation/router/FSM code.

State and persistence: none directly. The re-exported types own apply state, peer orchestration state, and raft storage persistence state.

Dependencies/integration: external code imports `crate::raft::{Apply, Peer, Storage}` through this module, avoiding direct submodule paths.

Risks: minimal; changing exports would ripple through many operation files.

Test signals: no tests needed beyond downstream compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/peer.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/raft/peer.rs

Purpose: this file defines `Peer`, the central raftstore-v2 object that wraps a raft `RawNode<Storage>`, current tablet cache, proposal/read queues, lifecycle state, split/merge/compact contexts, unsafe recovery state, transaction context, and readiness flags.

Important APIs/types/functions: `Peer::new` builds a peer from config, tablet registry, snap manager, and `Storage`. The remainder provides accessors and orchestration helpers for region/peer metadata, tablet replacement, read progress, leader lease, raft group, apply scheduler, proposal queue, pending ticks/messages, state changes, split/merge contexts, force-leader state, unsafe recovery state, and transfer-leader state.

Control flow: construction creates a raft config using applied index, recovers and loads a tablet if initialized, creates a cached tablet handle, initializes read progress and lease, restores merge proposal-control state if needed, and campaigns immediately for a single-peer initialized region. `set_region` updates region metadata, tablet index, read delegate/progress, leader lease, transaction context, and coprocessor region-change notifications. Ready helpers (`set_has_ready`, `set_has_extra_write`, pending messages/ticks) drive batch FSM processing.

State and persistence: peer-owned persistent deltas are accumulated in `state_changes` log batches and merged into `WriteTask` via `merge_state_changes_to`. `flush_state`, `sst_apply_state`, compact-log context, last sent snapshot index, and persistent tablet index interactions coordinate log GC and tablet durability. The peer stores only cached/live state for leadership, reads, proposals, and recovery, while `Storage` owns raft local/apply/region state.

Dependencies/integration: depends on raft `RawNode`, engine tablet cache/registry, coprocessor host, raftstore proposal/read queues, leases, region read progress, unsafe recovery states, transaction context, and many operation contexts. It is extended by numerous `operation/*` impl blocks.

Risks: `Peer` is a high-coupling object; subtle flag omissions can prevent ready handling, async writes, or ticks. Region updates must keep storage, read delegate, read progress, lease, and transaction context consistent. Force-leader and unsafe recovery states live here and bypass normal raft assumptions.

Test signals: no direct unit tests in this file. Behavior is covered through operation and raftstore-v2 integration tests that instantiate peers and exercise lifecycle transitions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/peer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/storage.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/raft/storage.rs

Purpose: this file implements raftstore-v2 storage, analogous to v1 `PeerStorage`, and provides the `raft::Storage` trait over TiKV raft-engine entry storage plus region/tablet metadata.

Important APIs/types/functions: `Storage<EK, ER>` owns `EntryStorage`, current peer, `RegionLocalState`, persistence flags, dirty-data flag, snapshot states/tasks, split-init state, apply trace, and flushed epoch. `Storage::create` constructs storage from local states. Methods expose entry/region/peer state, generation task management, dirty mark, flushed epoch, split-init, raft/apply state, initialization status, tablet index, region-state replacement, and replay-count estimate. The `raft::Storage` impl supplies `initial_state`, `entries`, `term`, `first_index`, `last_index`, and `snapshot`.

Control flow: creation finds the local peer in the region, reads dirty mark for the current tablet index, creates `EntryStorage`, and initializes snapshot/task containers. `initial_state` asserts hard-state commit matches initialization status; uninitialized peers return empty conf state even if hard state exists, while initialized peers return region-derived conf state. Snapshot calls delegate to the snapshot logic in `operation/ready/snapshot.rs`.

State and persistence: `ever_persisted` marks whether initial state must be persisted even if unchanged. `has_dirty_data` survives through raft engine dirty marks and suppresses snapshot generation after split until cleanup. `apply_trace` records flushed/applied indexes for replay/log GC. `flushed_epoch` advances only when a newer epoch is persisted.

Dependencies/integration: depends on `EntryStorage`, raft protobuf states, read scheduler, raft metrics, TiKV utility peer lookup, and operation types `ApplyTrace`, `GenSnapTask`, `SnapState`, and `SplitInit`.

Risks: the hard-state/initialized assertion protects a key v2 invariant; violating it means raft can start with wrong conf state. Dirty mark correctness affects snapshot availability and split recovery. Snapshot state is in `RefCell`, so runtime borrow discipline matters.

Test signals: local tests exercise snapshot apply, snapshot generation, cancellation, stale result handling, and storage creation with test engines/tablet registry.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/raft/storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/imp.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/router/imp.rs

Purpose: this file implements adapter traits and router wrappers for raftstore-v2, connecting internal `StoreRouter` to async read notifications, coprocessor split/bucket hooks, local reads, CDC, and unsafe recovery.

Important APIs/types/functions: `AsyncReadNotifier for StoreRouter` forwards fetched logs and generated snapshots to peers. `StoreHandle for StoreRouter` sends approximate-size/key updates, split requests, and bucket refreshes. `RaftRouter` wraps `StoreRouter` and `LocalReader`. `CdcHandle for RaftRouter` implements `capture_change` and `check_leadership`. `UnsafeRecoveryRouter` wraps a mutexed `StoreRouter` and implements `UnsafeRecoveryHandle`.

Control flow: async read callbacks force-send peer messages. StoreHandle methods convert coprocessor signals into `PeerMsg` variants. `RaftRouter::new` creates local store meta for `LocalReader`; `snapshot` delegates read-only snapshot execution to local reader. CDC capture builds an `AnyResChannel` callback that downcasts a region snapshot or forwards an error response. Unsafe recovery methods translate coordinator requests into peer/store messages, using broadcast for exit/wait/report and force/control sends for create/report.

State and persistence: routers do not persist data. They hold router handles, local reader metadata, and callback channels. Unsafe recovery router mutex serializes access to the underlying router object.

Dependencies/integration: depends on raftstore traits `AsyncReadNotifier`, `StoreHandle`, `CdcHandle`, and `UnsafeRecoveryHandle`; uses `PeerMsg`, `StoreMsg`, response channels, `LocalReader`, and `StoreMeta`.

Risks: force-send paths bypass normal backpressure; dropped messages are converted to region-not-found or generic errors inconsistently depending on operation. CDC downcast assumes snapshot type matches `EK::Snapshot`. `UnsafeRecoveryRouter::send_destroy_peer` treats missing region as success because peer may already be gone.

Test signals: no local tests. Coverage is by router trait integration, CDC tests, unsafe recovery tests, and local-read snapshot tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/imp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/internal_message.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/router/internal_message.rs

Purpose: this file defines messages and result structs exchanged between peer FSMs and apply FSMs.

Important APIs/types/functions: `ApplyTask` variants are committed entries, snapshot generation, unsafe write bytes, manual flush, bucket-stat refresh, and capture-apply. `ApplyRes` reports applied index/term, admin results, modification trace, apply metrics, bucket stats, and SST applied indexes. `SstApplyIndex` identifies a CF index and raft index for SST application tracking.

Control flow: peer FSM sends `ApplyTask` to apply workers; apply workers send `ApplyRes` back through router messages after applying committed entries or internal tasks. Snapshot generation tasks come from `snapshot.rs`, while capture tasks are CDC-related.

State and persistence: these are transport structs only. `ApplyRes.modifications` and `sst_applied_index` carry persistence/flush tracking signals to peer-side state.

Dependencies/integration: depends on PD bucket stat types, raftstore apply metrics, command/admin result types, committed entries, data trace, and `GenSnapTask`.

Risks: adding apply task variants requires peer and apply dispatch updates. Missing fields in `ApplyRes` can desynchronize log GC, flow control, or callbacks.

Test signals: no local tests; compile-time exhaustiveness and apply/peer integration tests cover message use.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/internal_message.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/message.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/router/message.rs

Purpose: this file defines the typed message vocabulary for raftstore-v2 peer and store routers, plus constructors for common raft requests.

Important APIs/types/functions: `PeerTick` and `StoreTick` enumerate periodic peer/store tasks and expose tag mappings. `RaftRequest<C>`, `SimpleWrite`, `UnsafeWrite`, and `CaptureChange` wrap routed work with timestamps/channels. `PeerMsg` covers raft messages, queries, writes, admin commands, ticks, apply results, snapshots, split/merge/GC/tablet operations, CDC capture, flush/test hooks, and unsafe recovery commands. `StoreMsg` covers store-level raft/control messages, latency inspection, and unsafe recovery report/create-peer. Helper constructors create query/admin/simple-write/split messages.

Control flow: routers enqueue these enums into peer or store FSMs. The batch FSM dispatches on variants and invokes operation modules. Constructors consistently allocate response channels and set send timestamps for latency tracking.

State and persistence: messages carry protobuf requests/responses, syncers, encoded simple writes, and metadata, but do not persist data themselves. Some variants such as `Persisted`, `DataFlushed`, and `SnapshotSent` communicate persistence completion back to peers.

Dependencies/integration: depends on kvproto raft/PD/import protobufs, raftstore fetched logs/snapshot results/simple-write binary, resource-control metering, health latency inspector, and response channel types.

Risks: `PeerMsg` is a central compatibility surface; missing dispatch for a new variant would drop behavior. Unsafe recovery variants carry syncers whose lifetime matters. `StoreMaybeTombstone` semantics are intentionally ambiguous because PD cannot distinguish tombstone from not-found stores.

Test signals: no local tests. Exhaustive matching in FSM dispatch and integration tests provide coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/message.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/router/mod.rs

Purpose: this module file defines the public router facade for raftstore-v2.

Important APIs/types/functions: it declares `imp`, `internal_message`, public `message`, and `response_channel` modules. It re-exports `RaftRouter`, `UnsafeRecoveryRouter`, `ApplyRes`, `SstApplyIndex`, `PeerMsg`, `PeerTick`, `RaftRequest`, `StoreMsg`, `StoreTick`, response-channel types, and `DiskSnapBackupHandle`. Test-only flush channel exports are gated by `testexport`.

Control flow: no runtime logic. It centralizes import paths for operation, FSM, and service layers.

State and persistence: none directly.

Dependencies/integration: consumers import router messages/channels through this facade rather than internal submodules.

Risks: export changes affect a broad compile surface. Keeping `ApplyTask` crate-private limits apply-worker internals.

Test signals: downstream compilation and module integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/response_channel.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/router/response_channel.rs

Purpose: this file implements reusable async response channels for raftstore-v2 read/write/debug commands, including optional proposed/committed events and cancellation semantics.

Important APIs/types/functions: `EventCore<Res>` stores a two-bit-per-event atomic state, optional result, optional before-set callback, waker, and tracker. `BaseChannel`/`BaseSubscriber` form generic result channels. `CmdResChannel`, `CmdResSubscriber`, `CmdResChannelBuilder`, `CmdResStream`, and `CmdResEvent` support raft write responses and proposed/committed notifications. `AnyResChannel`, `QueryResChannel`, `DebugInfoChannel`, `ReadResponse`, and `QueryResult` specialize payloads. Test-export `FlushChannel` exists behind a feature gate.

Control flow: producers call `notify_event` for proposed/committed milestones and `set_result` once for final payload; dropping a channel calls `cancel`. Subscribers poll `WaitEvent` or `WaitResult`, registering an `AtomicWaker` and setting subscribed bits via CAS. `CmdResStream` yields proposed, committed, then finished events according to the channel's event mask.

State and persistence: all state is in memory. The event atomic reserves event 0 for payload and 31 for cancellation. Trackers carry read or write latency metadata through callback trait implementations.

Dependencies/integration: implements raftstore callback traits `ErrorCallback`, `WriteCallback`, and `ReadCallback`; integrates with tracker TLS, raft command protobufs, transaction extra op, and region meta debug responses.

Risks: `UnsafeCell` plus atomics require strict single-result/single-consumer assumptions. The source includes a FIXME that `set_result` may need a stronger ordering barrier to prevent result write reordering before event publication. `take_result`/`result` cannot safely race each other despite `Sync` impl.

Test signals: local tests cover cancellation, channel result delivery, query responses, before-set callback mutation, and `CmdResStream` event sequencing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/router/response_channel.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/mod.rs

Purpose: this module file exposes raftstore-v2 worker submodules.

Important APIs/types/functions: public modules are `pd`, `refresh_config`, and `tablet`.

Control flow: no runtime logic here. Worker implementations are compiled through these module exports.

State and persistence: none directly.

Dependencies/integration: operation and batch code import PD/tablet worker tasks through this namespace.

Risks: minimal; removing an export breaks downstream module paths.

Test signals: downstream compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/misc.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/misc.rs

Purpose: this file contains miscellaneous PD worker async handlers, mainly max timestamp synchronization for transaction correctness and min-resolved-ts reporting.

Important APIs/functions: `Runner::handle_update_max_timestamp` and `Runner::handle_report_min_resolved_ts`.

Control flow: max-ts handling clones PD/concurrency/causal-ts/shutdown handles and spawns an async loop. While `txn_ext.max_ts_sync_status` still equals the initial status and shutdown is false, it either flushes the causal timestamp provider or obtains a TSO from PD, then updates `ConcurrencyManager::max_ts`. On success it atomically flips the low success bit; on repeated failure it logs at a throttled interval. A failpoint can delay the future by one second. Min-resolved-ts reporting sends an async PD request and logs failure.

State and persistence: no local persistence. Durable correctness is indirect: max-ts advancement prevents future reads/writes on a new leader from using timestamps older than prior leader reads. `max_ts_sync_status` filters stale async completions.

Dependencies/integration: used by `TxnContext::require_updating_max_ts`, depends on PD client TSO/min-resolved-ts APIs, `ConcurrencyManager`, optional RawKV API v2 `CausalTsProviderImpl`, global timer, and YATP remote spawning.

Risks: if PD/causal-ts calls fail indefinitely, leadership remains with stale status until another transition or shutdown; requests may be blocked by higher-level checks. The status compare-exchange means only the currently relevant transition can mark success.

Test signals: no local tests. Failpoint `delay_update_max_ts` supports timing tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/mod.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/mod.rs

Purpose: this file defines the raftstore-v2 PD worker task enum, runner state, runnable dispatch, reporter adapters, and admin-request helper constructors.

Important APIs/types/functions: `Task` covers store heartbeat/info updates, region heartbeat/stat updates, split operations, max timestamp update, bucket/min-resolved-ts reports, slowness inspection, and graceful shutdown state. `Runner<EK, ER, T>` owns PD client, raft engine, tablet registry, snap manager, store router, stats monitor, YATP remote, store/region stats, CPU records, concurrency manager, optional causal ts provider, slowness stats, gRPC service manager, config, and shutdown flags. `PdReporter` implements `FlowStatsReporter`, `Collector`, and `StoreStatsReporter`. `requests` builds and sends admin requests.

Control flow: `Runner::new` configures `PdStatsMonitor`, starts it with auto-split and resource collectors, and initializes state maps. `Runnable::run` schedules the heartbeat response receiver and dispatches every `Task` to specialized handlers in `store`, `region`, `split`, `misc`, or `slowness`. Reporter trait methods convert stats-monitor callbacks back into PD worker tasks.

State and persistence: PD worker stores accumulated store/region statistics, bucket deltas, CPU records, heartbeat timing, and slowness trends in memory. It does not directly persist raft data; admin requests are routed back to peers for raft proposal.

Dependencies/integration: integrates PD client, resource metering collector, auto split controller, gRPC service manager, config version track, store router, and raftstore store stats traits.

Risks: the runner is a hub; dropped scheduled tasks lose stats or management actions. `maybe_schedule_heartbeat_receiver` must run once to receive PD operators. Admin helper sends best-effort and logs failures rather than retrying locally.

Test signals: no direct tests in this file. Submodules include targeted tests; integration coverage should verify PD worker dispatch and heartbeat response handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/region.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/region.rs

Purpose: this file implements PD worker region-level heartbeat/stat handling, bucket reporting, CPU record accounting, and PD heartbeat response dispatch.

Important APIs/types/functions: `RegionHeartbeatTask` carries leader heartbeat data. `PeerStat` stores accumulated read/query/write snapshot baselines and approximate size/key data. `ReportBucket` tracks current and last-reported bucket stats and computes deltas. Runner methods include `handle_region_heartbeat`, `maybe_schedule_heartbeat_receiver`, `handle_report_region_buckets`, read/write stats updates, CPU record handling, `handle_destroy_peer`, `merge_buckets`, and `calculate_region_cpu_records`.

Control flow: region heartbeat converts approximate size 0 to 1 for compatibility, computes deltas since last region report, consumes region CPU records, builds `RegionStat`, updates store histograms, and sends async PD heartbeat. The heartbeat response receiver is installed once and translates PD operators into admin requests or peer messages: change peer, change peer v2, transfer leader, split by keys/half split, merge, or noop. Read/write stats accumulate per-region counters and feed `PdStatsMonitor`; bucket reports merge deltas then report PD deltas over elapsed seconds.

State and persistence: all stats maps are in memory: `region_peers`, `region_buckets`, and CPU records split by region-heartbeat and store-heartbeat windows. Destroy-peer removes stale stat records. Persistent changes from PD responses happen only after routed raft admin proposals apply.

Dependencies/integration: depends on PD client heartbeat APIs, `PdStatsMonitor`, resource metering raw records, router messages, admin request helper constructors, and request split/half-split operation types.

Risks: delta accounting assumes monotonic counters; resets can underflow because subtraction is direct. Heartbeat receiver panics on unexpected PD stream error. Bucket metadata changes require merge recalculation to align old stats to current bucket layout.

Test signals: local test `test_remove_peer_stat_from_maps` verifies destroy cleanup removes peer and CPU stats. Broader behavior needs PD heartbeat integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/region.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/slowness.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/slowness.rs

Purpose: this file implements store slowness trend detection and reporting for raftstore-v2 PD store stats.

Important APIs/types/functions: `SlownessStatistics` contains a cause `Trend`, result `Trend`, QPS recorder, and `last_tick_finished` flag. Runner methods include `handle_update_slowness_stats`, `handle_graceful_shutdown_state`, `handle_slowness_stats_tick`, `update_slowness_in_store_stats`, and private `flush_slowness_metrics`.

Control flow: periodic stats monitor creates latency inspectors; completed inspections call `handle_update_slowness_stats`, marking the tick finished and recording total raftstore duration as cause signal. On slowness tick, an unfinished previous tick records a large interval and may trigger a fake store heartbeat if real heartbeat is delayed; otherwise it records 100ms white noise. Store stats update computes slow trend cause/result values and rates, records QPS into result trend, sets PD protobuf `SlowTrend`, and flushes Prometheus gauges.

State and persistence: slowness state is in memory and exported through metrics and store heartbeat PD stats. Graceful shutdown state is stored in an atomic and triggers a store heartbeat tick message.

Dependencies/integration: depends on health-controller trend types, raftstore metrics, store heartbeat interval, PD store stats protobufs, and router control messages.

Risks: trend thresholds are heuristic and comments note compatibility-driven simplification of disk/network causes. If inspector ticks hang, fake heartbeat behavior prevents PD from missing slow state but can report synthetic data. Failpoint can force unfinished tick behavior.

Test signals: no local tests. Failpoint `mock_slowness_last_tick_unfinished` supports behavior testing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/slowness.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/split.rs -->
# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/split.rs

Purpose: this file handles PD-assisted region split requests and auto-split execution for raftstore-v2.

Important APIs/functions: `new_batch_split_region_request` builds a batch-split admin request. Runner methods are `handle_ask_batch_split`, private `ask_batch_split_imp`, `handle_report_batch_split`, and `handle_auto_split`.

Control flow: explicit ask-batch-split validates non-empty keys, asks PD for new region/peer IDs, then builds a `BatchSplit` admin request and sends it through `StoreRouter` with the optional response channel. Reporting split completion sends `report_batch_split` asynchronously. Auto-split iterates `SplitInfo` values, fetches current region metadata from PD, and either asks for a load-based single-key split or leaves half-split range handling as TODO.

State and persistence: this worker does not persist split state. PD allocates IDs; the actual split is persisted by the peer after the routed admin command is proposed and applied.

Dependencies/integration: depends on PD client `ask_batch_split`, `report_batch_split`, `get_region_by_id`, admin request helper `send_admin_request`, `StoreRouter`, and raftstore auto-split `SplitInfo`.

Risks: if PD ID allocation fails, split is only logged and not retried here. `zip(split_keys, ids)` assumes PD returns matching ID count. Auto half-split is not implemented, so range-only auto split info is ignored.

Test signals: no local tests. Split behavior is covered by raftstore split/admin integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/split.rs -->
