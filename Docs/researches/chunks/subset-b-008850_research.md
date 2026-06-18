# sources/storage-engines/tikv/components/raftstore/src/store/fsm/peer.rs lines 6334-7955

## Scope

This chunk covers the tail of `peer.rs`, starting inside the Raft log garbage-collection tick at the point where entry-cache eviction may be scheduled, and continuing through periodic peer maintenance, split and bucket refresh handling, stale-peer checks, consistency hash handling, witness/flashback transitions, public helper constructors, status command execution, memory tracing, and the local unit tests at the end of the file.

The chunk is a partial view of a very large peer FSM implementation. It does not include the definitions of `PeerFsm`, `PeerFsmDelegate`, `Peer`, `BatchRaftCmdRequestBuilder`, or the main message dispatch loop, but it shows many of the callbacks and tick handlers that connect the peer FSM to Raft, PD, split checking, coprocessor region metadata, unsafe recovery, consistency checking, and test-only instrumentation.

## Purpose

- Finish Raft log GC decision-making by computing a safe compaction index, respecting replicated/applied/persisted indexes, cache liveness, snapshot generation, and witness voter replication metadata.
- Maintain peer-local periodic work through `PeerTick` scheduling for entry-cache eviction, long-uncommitted proposal checks, request-snapshot retry, leader lease renewal, split checks, PD heartbeats, stale-peer validation, bucket reporting, memory-lock reactivation, and voter replicated-index polling.
- Coordinate region split workflows by reacting to approximate size/key updates, asking PD for batch split operators, and scheduling split-check worker tasks for full-region or key-range scans.
- Maintain region bucket metadata, push bucket updates into read progress, notify followers through extra messages, and report bucket statistics to PD.
- Handle special raftstore states that affect availability and correctness: witness switching, non-witness snapshot catch-up, unsafe recovery timeouts, force-leader cleanup, hibernation transitions, stale-peer validation, flashback lock gating, and busy-apply tracking.
- Schedule and verify consistency hash checks by coordinating async hash computation with a Raft `VerifyHash` admin command.
- Provide helper constructors for Raft command requests used by status, read-index, hash verification, and log compaction paths.
- Execute status commands locally without proposing them through Raft.
- Expose memory accounting helpers for Raft read-index and progress state.
- Test request batching behavior, especially which request kinds can be batched, size limits, callback fan-out, and duplicate lock-CF key detection.

## Important APIs, Types, And Functions

- `register_entry_cache_evict_tick()` and `on_entry_cache_evict_tick()` schedule and execute entry-cache eviction when `needs_evict_entry_cache(self.ctx.cfg.evict_cache_on_memory_ratio)` indicates memory pressure. They use `PeerTick::EntryCacheEvict` and repeat until the store entry cache becomes empty.
- `on_check_long_uncommitted_tick()` is leader-only and inactive for hibernated idle groups. It calls `peer.check_long_uncommitted_proposals(self.ctx)` and reschedules `PeerTick::CheckLongUncommitted`.
- `on_request_snapshot_tick()` handles the retry loop for a peer that has switched from witness to non-witness and is waiting for data. It rejects append messages while requesting a snapshot only after the local last log term matches the current term.
- `on_request_voter_replicated_index()` is witness-specific. When a compact-log command is pending and enough time has elapsed since last compaction, it sends `ExtraMessageType::MsgVoterReplicatedIndexRequest` to the leader and reschedules `PeerTick::RequestVoterReplicatedIndex`.
- `on_check_leader_lease_tick()` renews the leader lease from a periodic tick for active leaders and then schedules the next `PeerTick::CheckLeaderLease`.
- `on_split_region_check_tick()` is the main automatic split-check trigger. It gates on leadership, pending removal, split trigger skip state, split-check scheduler load, current split state, import mode, and in-progress snapshot generation before scheduling `SplitCheckTask::split_check`.
- `on_prepare_split_region()` validates a split request on the current leader and asks PD for a batch split through `PdTask::AskBatchSplit`. It classifies the split as size, load, or admin based on the source string.
- `on_approximate_region_size()` and `on_approximate_region_keys()` update `split_check_trigger`, schedule a new split check, and schedule a PD heartbeat so updated approximate metrics become visible.
- `on_refresh_region_buckets()` validates epoch freshness, updates `RegionBucketsInfo`, notifies the coprocessor host of `RegionChangeEvent::UpdateBuckets`, updates `ReadProgress` in `StoreMeta`, and sends `MsgRefreshBuckets` extra messages from leaders to non-witness followers.
- `on_msg_refresh_buckets()` is the follower-side bucket refresh handler. It ignores messages on leaders and updates the region reader's `ReadProgress` with a `BucketMeta` constructed from the extra message.
- `on_compaction_declined_bytes()` accumulates compaction-declined bytes into `split_check_trigger`, increments `UPDATE_REGION_SIZE_BY_COMPACTION_COUNTER` once the configured split-check diff is exceeded, and schedules split checking.
- `gen_bucket_range_for_update()` bridges bucket metadata into split checking. It returns bucket ranges only when region buckets are enabled, using twice the configured bucket size as the update threshold.
- `on_schedule_half_split_region()` schedules a key-range or bucket-oriented split check. It rejects non-leaders and stale epochs, optionally returns test-only `PeerInternalStat`, treats source `"bucket"` as bucket checking only, and otherwise schedules `SplitCheckTask::split_check_key_range`.
- `on_pd_heartbeat_tick()` checks peers on every tick, sends PD heartbeat only from leaders, and has special hibernate behavior: non-hibernate regions always reschedule; hibernate regions reschedule only when replication mode still needs catch-up.
- `on_check_peers_availability()` sends `MsgAvailabilityRequest` extra messages to peers listed in `wait_data_peers` and removes peer ids that no longer resolve in the local peer cache.
- `on_check_peer_stale_state_tick()` is the central stale and hibernation maintenance tick. It handles unsafe recovery timeout, force-leader timeout, hibernate state transitions, stale leader detection, peer stale-check broadcasts, and PD peer validation.
- `on_reactivate_memory_lock_tick()` restores in-memory pessimistic lock status after a failed or completed leader transfer when the peer is still leader and has waited enough configured ticks.
- `on_report_region_buckets_tick()` reports leader bucket statistics to PD with `PdTask::ReportBuckets` and reschedules `PeerTick::ReportBuckets`.
- `try_to_fetch_committed_index()` issues a local Raft read-index request to fetch the current leader commit index when a follower needs `last_leader_committed_idx`.
- `on_check_peer_complete_apply_logs()` updates `busy_on_apply`, `StoreMeta::busy_apply_peers`, and `completed_apply_peers_count` based on applied index lag versus `last_leader_committed_idx` and `leader_transfer_max_log_lag`.
- `on_ready_compute_hash()`, `on_ready_verify_hash()`, `on_hash_computed()`, and `verify_and_store_hash()` implement the consistency-check handshake: schedule async hash computation, store or compare computed hashes, propose a verify-hash admin request, and panic on mismatched hashes.
- `on_ingest_sst_result()` feeds ingested SST size/key metrics into split-check and bucket state, then triggers PD heartbeat and split checking if this peer is leader.
- `on_transfer_leader()` acknowledges a transfer-leader message only if the execution term still matches the peer term, then marks the FSM as having ready work.
- `on_set_flashback_state()` updates region metadata, expires leader lease, and sets pessimistic lock status to `IsInFlashback`, `Normal`, or `NotLeader` depending on the new region flag and leadership.
- `on_ready_batch_switch_witness()` applies a witness switch region update to `StoreMeta`, changes local witness state, clears local data or delays cleanup when switching to witness, requests a snapshot when switching back to non-witness, tracks other peers waiting for data, and reports changed peer state to PD from leaders.
- `maybe_destroy_source()` is a public merge helper. It checks `StoreMeta::pending_merge_targets` and tells callers whether an isolated source peer can be destroyed after observing a target-region epoch newer than the stored merge target.
- `new_read_index_request()`, `new_admin_request()`, `new_verify_hash_request()`, and `new_compact_log_request()` construct `RaftCmdRequest` values for local/read/admin workflows.
- `execute_status_command()`, `execute_region_leader()`, and `execute_region_detail()` serve status requests locally, binding the peer term into the response without going through the Raft proposal path.
- `memtrace::PeerMemoryTrace`, `PeerFsm::raft_read_size()`, and `PeerFsm::raft_progress_size()` expose approximate heap sizing for Raft read-only/read-index state and replication progress/inflight buffers.
- The `tests` module validates `BatchRaftCmdRequestBuilder` behavior against admin/status/snapshot requests, max entry size, callback invocation, and duplicate lock-CF writes.

## Control Flow

The chunk starts in the second half of Raft log GC. The handler has already computed applied, truncated, first, last, replicated, voter-replicated, and alive-cache indexes. It first compacts/evicts in-memory entry cache based on alive replicated indexes and memory pressure, then computes a Raft log compact index. Forced compaction uses `replicated_idx` when possible. Otherwise, count and size limits compact to at least halfway between first and last, but never below the replicated index. Small log spans, replicated indexes before first, threshold limits, and the reserve tick budget all skip compaction with metrics.

Before proposing compaction, the compact index is capped at Raft's persisted log index so unpersisted entries are not compacted. The code subtracts one from the chosen index for historical compatibility, rejects an index that falls below `first_idx`, cancels any snapshot generation that would now be obsolete, builds a `CompactLog` admin request with compact term and voter replicated index, proposes it with `DiskFullOpt::AllowedOnAlmostFull`, resets skipped-GC ticks, reschedules the GC tick, and increments the GC counter.

The following tick handlers are mostly guard-and-reschedule loops. Entry-cache eviction repeats while memory pressure remains and the cache is non-empty. Long-uncommitted proposal checks and leader lease renewal are leader-only and skip idle hibernated groups. Snapshot requests are retried for non-leader, non-removing peers waiting for data; the handler avoids duplicate snapshot work and only switches `should_reject_msgappend` on once the local last log term catches up to the current term. Witness peers with pending compact commands periodically ask their leader for voter replicated index information.

Split checking starts from approximate size/key changes, compaction-declined bytes, manual half-split scheduling, and periodic split ticks. The periodic split tick filters out non-leaders, pending removals, skip-trigger windows, busy split-check scheduler, in-progress split, import mode, and short-lived snapshot generation. If it passes all gates, it schedules a scanning split-check task with optional bucket ranges from `gen_bucket_range_for_update()` and records the trigger as handled.

Preparing a split is a PD-mediated workflow. The peer must still be leader, the caller's region epoch and split keys must validate against the current region, and the split reason is derived from the source. The handler schedules `PdTask::AskBatchSplit` with current region metadata, the local peer, right-derive config, source-size sharing, callback, and reason. If the PD scheduler is stopped, it extracts the callback from the returned task and invokes it with an error response.

Bucket refresh flow is epoch-protected. A stale refresh request logs and, under test builds, returns the current bucket state through a test callback. A fresh request generates the next bucket version from the current term and bucket version, updates `RegionBucketsInfo`, and exits early if no bucket-key range changed. On real change, it notifies the coprocessor host, updates the region reader's read progress under `StoreMeta`, and, if leader, sends refresh extra messages containing version and keys to all non-witness followers. Followers receiving `MsgRefreshBuckets` update only read-progress bucket metadata; they do not mutate the leader-owned bucket statistics.

PD heartbeat and peer availability maintenance operate around leadership and witness catch-up. The PD heartbeat tick always calls `check_peers()`, then only leaders heartbeat PD. For hibernated regions it does not blindly reschedule unless replication mode needs catch-up. Witness switching uses `wait_data` and `wait_data_peers`: local non-witness switches request snapshots, leaders track other peers needing data and later send availability probes to them, while invalid peer ids are pruned before they can affect pending-peer reporting.

Stale-state checking is a larger state machine. The tick is skipped for pending removal, rescheduled early, and ignored during snapshot handling. It first aborts timed-out unsafe recovery state and exits stale force-leader mode after the same timeout. When hibernate regions are enabled, idle followers may transition to `PreChaos` if the Raft base tick is no longer registered, leaders mark ready work and schedule PD heartbeat, `PreChaos` advances to `Chaos`, and `Chaos` registers a Raft base tick so followers can elect if leader ping is absent. After that, `peer.check_stale_state()` drives either no action, a leader-missing warning plus stale-peer broadcasts, or PD validation through `PdTask::ValidatePeer`.

Memory-lock reactivation is scoped to a leader transfer failure path. The handler takes the pessimistic-lock write guard, exits unless this peer is still leader and the status is `TransferringLeader`, increments a tick counter, and restores `LocksStatus::Normal` only after no active Raft lead transferee is present and the configured timeout has elapsed. Otherwise it drops the lock guard and schedules another reactivation tick.

Busy-apply tracking first exits if no tracking is active. If the peer has become leader, or if it is newly initialized with only the init log index, it clears `busy_on_apply`, removes the peer from `StoreMeta::busy_apply_peers`, and bumps `completed_apply_peers_count` if present. Otherwise it compares `last_leader_committed_idx` to the applied index. A missing commit index is treated as `u64::MAX` so restarted peers remain busy until the leader-commit index is fetched. Peers over the configured lag threshold are inserted into the busy set; peers below it are removed and counted complete.

Consistency checking has two arrival orders. A computed hash or expected verify hash can arrive first. `verify_and_store_hash()` rejects older indexes, treats same-index empty hash as duplicate, compares same-index non-empty hashes and panics on mismatch, clears the stored hash on match, and stores newer hash material for later comparison. When local hash computation stores a new hash successfully, `on_hash_computed()` proposes a `VerifyHash` admin command so other peers can compare.

Flashback and witness state changes directly alter serving behavior. Flashback region updates expire the remote leader lease to block local reads and set pessimistic locks to a mode that prevents new lock insertion while clearing existing locks. Witness switching updates shared region metadata, lowers Raft priority and clears data when becoming a witness, defers data cleanup if the leader is scanning snapshots, and requests a snapshot plus read-progress wait state when becoming a non-witness.

After helper request constructors, status command execution branches on `StatusCmdType`. Region leader responses return the cached leader if known. Region detail requires the local store to be initialized before returning the current region and leader. The response is wrapped in `RaftCmdResponse` and term-bound with the current peer term.

The file ends with memory tracing helpers and tests. The memory helpers estimate transient heap in Raft read-index queues, pending read-index messages, progress records, and inflight buffers. Tests build representative `RaftCmdRequest` values and validate batchability, request-size boundaries, callback fan-out for batched commands, and a panic path for duplicate writes to the same lock-CF key in a batch.

## State And Persistence Behavior

- Raft log GC state spans durable Raft log state and transient FSM counters. It reads persisted/applied/truncated/first/last indexes from the peer store and Raft log, proposes a durable `CompactLog` admin command, resets `skip_gc_raft_log_ticks`, and may cancel in-flight snapshot generation tied to soon-to-be-compacted logs.
- Entry-cache eviction affects in-memory Raft entry cache only. It is repeated through ticks and is also invoked from the log-GC path when memory ratio policy requires eviction.
- Split-check state is mostly transient scheduling and approximate metadata. `split_check_trigger` records approximate size/key and compaction-declined-byte signals; scheduled `SplitCheckTask` work can later lead to PD split requests and region metadata changes outside this chunk.
- Bucket state is persistent in peer memory and shared read metadata, not directly in storage here. `RegionBucketsInfo` is updated, `StoreMeta::readers` receive `ReadProgress::region_buckets`, coprocessor region-change callbacks run, and followers get extra messages that refresh their local read-progress bucket metadata.
- PD heartbeat, peer availability, and stale-peer validation update shared raftstore metadata indirectly through schedulers and peer fields. This chunk schedules `PdTask::AskBatchSplit`, `PdTask::ValidatePeer`, and `PdTask::ReportBuckets`, and calls `peer.heartbeat_pd(self.ctx)`.
- Hibernation state is persisted only in the peer FSM state machine. The code mutates `GroupState` through `reset_hibernate_state`, registers Raft ticks, sets `has_ready`, and sends pings to detect leader reachability.
- Unsafe recovery and force-leader state are time-bounded. The tick aborts recovery state or exits force-leader mode when `UNSAFE_RECOVERY_STATE_TIMEOUT` elapses, preventing abandoned PD recovery processes from leaving long-lived local overrides.
- In-memory pessimistic lock state changes are guarded by a write lock. Flashback clears lock contents and prevents new locks; leader-transfer reactivation restores normal lock insertion after timeout; witness/non-leader paths can leave locks unavailable.
- Witness switching updates `StoreMeta` region metadata through `meta.set_region`, mutates local `peer.is_witness`, may clear the local store's data, may set `delay_clean_data`, and may set read progress to `WaitData(true)` until a snapshot catches up the data-bearing peer.
- Consistency-check state lives in `peer.consistency_state`, including index, hash, context, and last check time. A successful local hash computation becomes a Raft admin proposal; a mismatch intentionally panics the process to surface data inconsistency.
- `StoreMeta::busy_apply_peers` and `completed_apply_peers_count` are updated under mutex to expose leader-transfer readiness and apply backlog state across peers.
- Status command responses are generated from current in-memory peer/store state. They do not append Raft entries and do not write storage.
- Memory tracing computes sizes from live Raft internal collections and does not mutate state.
- The tests mutate only local request builders, callbacks, and atomic flags. The duplicate lock-CF test expects a panic during batch construction.

## Dependencies And Integration Points

- The chunk depends on the surrounding `PeerFsmDelegate` implementation for `schedule_tick`, `register_raft_gc_log_tick`, `register_raft_base_tick`, `register_pd_heartbeat_tick`, `propose_raft_command_internal`, `region`, `region_id`, `peer`, `update_region`, `on_exit_force_leader`, and other methods defined outside this line range.
- It integrates with Raft through `raft_group`, progress matched indexes, `raft_log.persisted`, `read_index`, `request_snapshot`, `lead_transferee`, local term checks, and admin proposals.
- It integrates with raftstore storage through peer-store methods such as `applied_index`, `truncated_index`, `first_index`, `last_index`, `on_compact_raftlog_cache`, `evict_entry_cache`, `cancel_generating_snap`, `is_generating_snapshot`, `is_initialized`, and `clear_data`.
- It integrates with TiKV configuration via `self.ctx.cfg`: log GC count/size/threshold/reserve limits, entry-cache memory ratio, request-voter-replicated-index interval, split-check diff, right-derive split behavior, hibernate regions, leader-missing durations, reactive memory-lock timeout, and leader-transfer max log lag.
- It uses PD scheduling for split, stale-peer validation, and bucket reporting through `self.ctx.pd_scheduler` and `PdTask`.
- It uses the split-check worker scheduler through `self.ctx.split_check_scheduler` and task constructors from `SplitCheckTask`.
- It integrates with import-mode control through `self.ctx.importer`, avoiding automatic split checks while Lightning or BR import mode could make ingest requests fail with epoch mismatch.
- It integrates with coprocessor and read systems through `self.ctx.coprocessor_host`, `RegionChangeEvent::UpdateBuckets`, `StoreMeta::readers`, and `ReadProgress`.
- It sends inter-peer side-channel messages through `ExtraMessage`, `ExtraMessageType`, `RefreshBuckets`, and `peer.send_extra_message` over `self.ctx.trans`.
- It depends on region and peer metadata helpers such as `util::validate_split_region`, `util::is_epoch_stale`, `util::gen_bucket_version`, `find_peer`, `find_peer_by_id`, `is_learner`, and peer cache lookup.
- It integrates with transaction pessimistic-lock state through `self.fsm.peer.txn_ext.pessimistic_locks` and `LocksStatus`.
- It integrates with consistency-check workers through `self.ctx.consistency_check_scheduler` and `ConsistencyCheckTask::compute_hash`.
- It depends on failpoint infrastructure for testing and fault injection in log eviction, long-uncommitted checks, request snapshot, split skip counts, stale recovery timeout, and flashback state handling.
- The tests depend on `engine_test::kv::KvTestEngine`, `kvproto::raft_cmdpb` request/response types, protobuf `compute_size`, `ReadableSize`, `RaftMetrics`, `Callback`, `ExtCallback`, and `RaftCommand`.

## Risks And Edge Cases

- Log compaction is constrained by several indexes with different durability meanings. Compacting beyond `raft_log.persisted`, below `first_idx` after the historical subtract-one step, or ahead of a needed snapshot index can lose data or invalidate snapshot generation. This chunk explicitly caps and cancels, but future changes to the compact-index formula are high risk.
- The comment around `compact_idx -= 1` says the reason is unknown and inherited from original code. That makes this arithmetic a fragile compatibility point, especially near `first_idx`.
- Log GC skips based on `raft_log_gc_threshold` only up to `raft_log_reserve_max_ticks`; changing the tick cadence or reserve limit changes how long stale logs are retained even when below threshold.
- Entry-cache eviction can be scheduled from both log GC and entry-cache ticks. Eviction policy must avoid tight rescheduling loops under sustained memory pressure.
- Snapshot request retry for witness-to-non-witness peers depends on `last_term == term` before rejecting `MsgAppend`. If this condition is wrong during leader changes, a recovering peer could either reject useful appends too early or delay snapshot request too long.
- Split checks are intentionally disabled during import mode and temporarily delayed during snapshot generation. Removing those guards can cause ingest epoch failures or stale snapshots; delaying too long can leave oversized regions unsplit.
- Bucket refresh uses `region_buckets_info().bucket_stat().unwrap()` after update paths. If bucket stat is absent under an unexpected configuration or stale path, this can panic. Current callers appear to rely on bucket refresh only when bucket metadata exists.
- `on_msg_refresh_buckets()` updates follower read progress without checking epoch staleness against the current region beyond using the message epoch in `BucketMeta`. If stale messages can arrive out of order, later read behavior depends on upstream message filtering and version semantics.
- `on_check_peers_availability()` only sends probes and prunes invalid cached peers; it does not reschedule itself directly in this function. Continued probing depends on callers registering the tick when `wait_data_peers` is non-empty.
- Hibernation stale-state transitions are subtle. The code intentionally waits through `Idle`, `PreChaos`, and `Chaos` before enabling Raft ticks; changing this sequence can create unnecessary elections or delay elections after one-way leader communication failure.
- Unsafe recovery and force-leader cleanup depend on monotonic elapsed time and the shared timeout constant. Too short a timeout can abort legitimate recovery; too long leaves unsafe state active.
- Busy-apply tracking treats missing `last_leader_committed_idx` as `u64::MAX`, which intentionally keeps a restarted follower marked busy. This requires `try_to_fetch_committed_index()` to make progress; otherwise peers may remain busy indefinitely.
- Consistency hash mismatch panics, which is appropriate for data corruption detection but makes failpoint and test coverage important. Race handling around older, duplicate, or dropped hash computations is managed through index/hash state and miss counters.
- `verify_and_store_hash()` currently ignores the `context` argument except when constructing a verify request from stored state. The TODO notes context handling; if two hash computations share an index but differ in context, correctness relies on surrounding scheduling preventing ambiguity.
- `on_set_flashback_state()` expires the leader lease and clears pessimistic locks while holding the lock state. Any future local-read or lock path that bypasses these fields could violate flashback restrictions.
- Witness switching as leader sets `delay_clean_data` instead of immediately clearing data to avoid snapshot-scan races. That delayed cleanup must be consumed elsewhere; otherwise witness peers may retain unnecessary data.
- `maybe_destroy_source()` unwraps `meta.store_id` and the target peer lookup. It assumes callers provide `StoreMeta` with store id and a target region containing the local store's peer. Violating that invariant would panic.
- `new_read_index_request()` creates a `Request` and sets its type to `ReadIndex`, but this chunk does not push that command into the returned request. The later merge pass should check callers and earlier code to determine whether this is intentional dead setup, an incomplete helper, or covered by another convention.
- Status commands bypass Raft. That is intended for observational state, but region detail can be stale relative to concurrent region changes and rejects uninitialized stores.
- Memory size estimates use fixed-size approximations for UUIDs, messages, `Progress`, and inflight buffers. They are useful for tracing but should not be treated as exact allocator usage.
- The duplicate lock-CF batching test expects a panic after adding duplicate lock keys. This is a strong correctness assertion for batching, but the builder implementation lies outside this chunk.

## Test Signals

- Raft log GC tests should cover forced compaction, count-limit compaction, size-limit compaction, threshold skip and max-reserve behavior, replicated index before first index, persisted index behind applied index, compact index equal to first index before subtraction, snapshot-generation cancellation, and generated `CompactLog` request fields including voter replicated index.
- Entry-cache tests should simulate memory-pressure and non-empty cache states to confirm eviction repeats only while needed and stops when empty.
- Snapshot request tests should cover witness-to-non-witness recovery, pending removal, leader peer, handling snapshot, pending snapshot, last-term mismatch after leader change, request failure logging, and `should_reject_msgappend` transitions.
- Split-check tests should cover non-leader and pending-remove skips, split-trigger `should_skip`, busy scheduler, in-progress split, import mode, region-in-import-mode, snapshot-generation skip count, bucket range generation, and scheduler errors.
- Split preparation tests should cover not-leader callback errors, stale or invalid epochs, invalid split keys, source-to-`SplitReason` mapping, successful `PdTask::AskBatchSplit`, and stopped PD scheduler callback behavior.
- Bucket refresh tests should cover stale epoch, unchanged bucket ranges, changed bucket version, coprocessor `UpdateBuckets` notification, read-progress update, leader broadcast to non-witness followers, follower-side `MsgRefreshBuckets`, and test-only callbacks.
- PD heartbeat and peer availability tests should cover hibernate versus non-hibernate rescheduling, leader-only heartbeat, replication-mode catch-up, invalid `wait_data_peers` pruning, and extra-message availability probes.
- Stale-state tests should exercise unsafe recovery timeout, force-leader timeout, hibernation `Idle -> PreChaos -> Chaos` transitions, leader-missing metrics, stale-peer broadcasts, and PD `ValidatePeer` scheduling failures.
- Memory-lock reactivation tests should cover non-leader skip, non-transferring status skip, active `lead_transferee`, timeout tick threshold, and final `LocksStatus::Normal` restoration.
- Busy-apply tests should cover becoming leader while tracked, newly initialized peers, missing leader commit index, lag above and below `leader_transfer_max_log_lag`, busy set insertion/removal, and completed count increments.
- Consistency-check tests should cover compute task scheduling errors, older hash miss, duplicate same-index empty-hash case, same-index mismatch panic, same-index match clearing, newer hash replacement, dropped slow computation miss counts, and verify-hash proposal disk-full behavior.
- Flashback tests should assert region metadata update, remote lease expiration, lock clearing on flashback entry, `Normal` lock status for leader exit, and `NotLeader` status for follower exit.
- Witness switch tests should cover switching local peer to witness as follower and leader, delayed data cleanup, switching back to non-witness, immediate snapshot request, `wait_data_peers` tracking for other peers, PD heartbeat, and availability tick registration.
- Merge helper tests should cover no pending target, source not in target map, region epoch not newer, newer epoch with target peer matching local store, and malformed metadata invariants if defensive checks are added.
- Status command tests should cover `RegionLeader`, initialized and uninitialized `RegionDetail`, invalid status command, unknown cached leader, and term binding in responses.
- Memory tracing tests should validate monotonic size changes as read states, pending read-index entries, peer counts, and inflight buffers grow.
- Existing local unit tests in this chunk already signal request batching behavior: admin/status/snapshot requests are not batchable, normal puts below entry max are batchable, oversized puts are not, batched proposed/committed/final callbacks all fan out, size-limit accumulation prevents a second large request, and duplicate lock-CF keys panic.

## Unresolved Cross-Chunk References

- The dispatch paths that call each tick handler are outside this chunk. The merge report should connect these handlers back to the `PeerTick` registration and FSM message handling code.
- `BatchRaftCmdRequestBuilder` is tested here but defined earlier. The merge report should combine these tests with the builder implementation to explain batching invariants completely.
- The delayed witness data cleanup path (`delay_clean_data`) and request-snapshot completion path are not visible here.
- The consistency-check lifecycle starts before `on_ready_compute_hash()` and continues when `VerifyHash` admin commands apply; those proposal/apply paths are outside this chunk.
- The source and validation semantics of bucket refresh messages are partially outside this chunk, especially ordering/version guarantees for follower `MsgRefreshBuckets`.
