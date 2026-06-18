# sources/storage-engines/tikv/components/raftstore/src/store/fsm/apply.rs lines 1-7124

## Scope

This chunk covers lines 1-7124 of `sources/storage-engines/tikv/components/raftstore/src/store/fsm/apply.rs`, from module imports through the apply FSM implementation and into the first part of the unit-test module. The full source file continues past this chunk; the mapped slice ends just as `test_bucket_version_change_in_try_batch` starts, so that test body and later tests are out of scope for this chunk.

The covered code is the core Raft apply path for TiKV raftstore. It receives committed Raft entries for a Region, decodes write/admin commands, mutates the local KV engine and region metadata, persists apply state with the same KV write batch as data changes, emits apply results back to raftstore, manages proposal callbacks, supports split/merge/conf-change/witness/flashback/log-compact operations, and wires this per-region delegate into TiKV's batch-system FSM runtime.

## Purpose

- Apply committed Raft log entries for each Region in log-index order and advance `RaftApplyState`.
- Execute normal write commands (`Put`, `Delete`, `DeleteRange`, `IngestSst`) against the KV engine with region-boundary and epoch checks.
- Execute admin commands that mutate raftstore metadata: legacy and v2 conf changes, batch split, prepare/commit/rollback merge, compact log, transfer leader, consistency hash, flashback state transitions, and batch witness switching.
- Keep proposal callbacks aligned with committed entries, returning stale-command or region-removed errors when callbacks can no longer be fulfilled.
- Batch writes across messages while preserving correctness boundaries around delete range, SST ingestion, consistency checks, merges, snapshots, and write-batch limits.
- Persist region local state and apply state in CF_RAFT, alongside KV data changes in a single KV write batch where required to avoid power-loss holes.
- Expose `ExecResult` and `ApplyRes` messages back to raftstore so the raftstore thread can perform side effects outside the apply worker, such as log GC, split peer activation, merge finalization, consistency checks, and peer destruction.
- Run per-region apply work in a `batch_system` FSM with normal/low-priority scheduling, dynamic configuration tracking, resource metering, latency inspection, memory tracing, and apply-result notification.

## Important APIs, Types, And Functions

- `PendingCmd<C>` stores a proposed command callback with its `(index, term)`. Its `Drop` panics if the callback was not consumed, making callback leaks visible.
- `PendingCmdQueue<C>` separates normal proposals, a single conf-change proposal, and compact-log callbacks. It handles stale callbacks by index/term and shrinks its normal queue when it becomes small again.
- `ChangePeer`, `Range`, `SwitchWitness`, and `NewSplitPeer` are data carriers embedded in `ExecResult` variants for metadata-affecting admin commands.
- `ExecResult<S>` is the apply-to-raftstore side-effect vocabulary. Covered variants include conf change, compact log, split, prepare/commit/rollback merge, compute/verify hash, delete range, SST ingest, transfer leader, flashback, batch witness switch, pending compact state, and unsafe force compact.
- `ApplyResult<S>` is the internal per-entry result: no special result, yield, an `ExecResult`, or a `WaitMergeSource` marker used to pause target-Region merge commit until the source Region catches up.
- `ApplyCallbackBatch<S>` batches `CmdBatch` observer data and write callbacks. It ensures coprocessor observation happens before callbacks are invoked after persistence.
- `Notifier<EK>` abstracts apply-worker notifications back to raftstore: `notify(Vec<ApplyRes<_>>)` and `notify_one(region_id, PeerMsg<_>)`.
- `ApplyContext<EK>` is the per-poller mutable execution context. It owns the KV write batch wrapper, pending apply results, callback batch, importer, coprocessor host, snapshot scheduler, router, notifier, performance context, latency inspectors, metrics histograms, SST cleanup lists, and write/yield configuration.
- `ApplyContext::prepare_for`, `commit`, `commit_opt`, `write_to_db`, `finish_for`, and `flush` implement the apply lifecycle. They prepare region-scoped write-batch state, persist pending KV/apply-state/SST ingest work, invoke observers and callbacks, accumulate `ApplyRes`, and notify raftstore at poller boundaries.
- `should_write_to_engine`, `has_high_latency_operation`, `should_sync_log`, and `can_witness_skip` are command classifiers. They decide when to flush before a command, whether to demote a Region to low-priority handling, whether WAL sync is required, and whether a witness peer can skip decoding a normal entry.
- `WaitSourceMergeState` and `YieldState<EK>` preserve paused apply state across batch-system polls, especially for target-side `CommitMerge` waiting on the source peer.
- `ApplyDelegate<EK>` is the per-Region apply state machine. It owns Region and peer metadata, `RaftApplyState`, applied term, pending callbacks, merge/witness/snapshot state, observer IDs, local apply metrics, raft-engine entry fetcher, bucket statistics, and memory trace state.
- `ApplyDelegate::handle_raft_committed_entries` is the top-level per-entry loop. It checks index continuity, dispatches normal/conf-change entries, handles yields and merge waits, and destroys the delegate after self-removal.
- `ApplyDelegate::handle_raft_entry_normal` decodes `RaftCmdRequest` or v2 simple-write entries, applies empty entries, clears stale callbacks on term change, handles witness skipping, flush/yield decisions, and calls `process_raft_cmd`.
- `ApplyDelegate::handle_raft_entry_conf_change` decodes `ConfChange` or `ConfChangeV2`, parses the embedded command context, and attaches the decoded conf-change record to the returned `ExecResult::ChangePeer`.
- `ApplyDelegate::process_raft_cmd`, `apply_raft_cmd`, and `exec_raft_cmd` are the core command execution path. They set sync hints, invoke coprocessor pre/post hooks, save/rollback write-batch savepoints on errors, advance apply index/term on deterministic outcomes, update in-memory Region state, and return whether apply state must be persisted immediately.
- `exec_write_cmd`, `handle_put`, `handle_delete`, `handle_delete_range`, and `handle_ingest_sst` implement normal write commands.
- `exec_admin_cmd` dispatches admin commands to specialized handlers.
- `exec_change_peer`, `exec_change_peer_v2`, `apply_conf_change`, and `apply_leave_joint` implement legacy and joint-consensus configuration changes, including learner/voter transitions, self-removal, epoch changes, and persistent `RegionLocalState` writes.
- `validate_batch_split` and `exec_batch_split` validate split keys/peer IDs, construct derived and new Regions, coordinate `pending_create_peers`, persist new peer state and initial apply state, and return `ExecResult::SplitRegion`.
- `exec_prepare_merge`, `exec_commit_merge`, and `exec_rollback_merge` implement Region merge state transitions. `exec_commit_merge` can return `WaitMergeSource` and later resume once source logs are caught up.
- `try_compact_log`, `exec_compact_log`, and `compact_raft_log` update only `RaftApplyState.truncated_state`; actual raft-log deletion is left to raftstore-side processing.
- `exec_flashback` toggles Region flashback fields and persists updated `RegionLocalState`.
- `exec_batch_switch_witness` updates peer witness flags, marks self as waiting for data when switching back from witness, and persists normal/unavailable/tombstone state.
- `is_conf_change_cmd` and `check_sst_for_ingestion` are exported helpers for command classification and SST metadata validation.
- `Apply<C>` is the scheduled apply task: peer/region IDs, term, commit index/term, cached entries, proposal callbacks, entry-size accounting, and optional bucket metadata. `try_batch` merges same-region tasks up to `MAX_APPLY_BATCH_SIZE`.
- `Registration`, `Proposal<C>`, `Destroy`, `CatchUpLogs`, `GenSnapTask`, `ObserverType`, and `ChangeObserver` are external message payloads sent into the apply FSM.
- `Msg<EK>` is the apply FSM message enum. It includes apply work, registration, merge catch-up, noop, destroy, snapshot, observer change, validation hooks for tests, recovery from witness wait, compact checks, unsafe force compaction, and in-memory-engine load callbacks.
- `ApplyMetrics`, `ApplyRes<S>`, and `TaskRes<S>` are the output data structures delivered to raftstore.
- `ApplyFsm<EK>` owns one `ApplyDelegate` and its mailbox/receiver. It implements per-message handling, batching, proposal append, destroy, merge resume, snapshot generation, observer changes, compact checks, and unsafe compaction.
- `ControlFsm` carries latency-inspection control messages into pollers.
- `ApplyPoller<EK>` implements `PollHandler`, tracking config changes, draining normal/control FSMs, flushing apply context at poll end, and updating memory traces.
- `Builder<EK>`, `ApplyRouter<EK>`, `ApplyBatchSystem<EK>`, and `create_apply_batch_system` connect this apply code to TiKV's `batch_system`.
- The `memtrace` submodule implements heap-size estimates for pending commands, yielded merge state, messages, and catch-up logs.

## Control Flow

Apply work begins outside this file when raftstore schedules `Msg::Apply` through `ApplyRouter::schedule_task`. If no mailbox exists for a `Registration`, `schedule_task` creates a new `ApplyFsm` from the registration and registers it. If an apply message targets a missing Region, callbacks are failed with `RegionNotFound` unless the process is shutting down.

Within a poll, `ApplyPoller::begin` picks up configuration changes, including `messages_per_tick` and apply-yield write size. `handle_control` drains latency-inspection messages. `handle_normal` resumes any yielded delegate first, then drains up to `messages_per_tick` messages from the Region receiver and passes them to `ApplyFsm::handle_tasks`.

`handle_tasks` coalesces consecutive `Msg::Apply` messages for the same Region through `Apply::try_batch` until the 64 MiB entry-size limit or a non-apply message is encountered. It records apply-wait metrics, updates global write trackers, handles registration/destroy/snapshot/change/compact/recovery messages, and preserves pending messages in `YieldState` if apply yields mid-batch.

For `Msg::Apply`, `ApplyFsm::handle_apply` materializes entries from `CachedEntries`, fetching from the raft engine when only a range is cached. It updates delegate term, bucket metadata, commit index and commit term, appends proposal callbacks, resets priority to normal, and calls `ApplyDelegate::handle_raft_committed_entries`.

`handle_raft_committed_entries` wraps the Region in `ApplyContext::prepare_for`, then iterates committed entries. It enforces `applied_index + 1 == entry.index`, dispatches by Raft entry type, collects `ExecResult`s, and calls `ApplyContext::finish_for` after all entries or before yielding. If self-removal was applied, it destroys the delegate after finishing current results.

For normal entries, empty data is treated as a term/leader-change/read-index marker: observers receive `on_empty_cmd`, stale normal callbacks from older terms are failed, and applied index/term advance. Non-empty entries are skipped by witnesses when `can_witness_skip` sees a normal non-admin request. Otherwise the entry is decoded as a normal `RaftCmdRequest` or as a v2 simple-write request when compatible learner support is enabled. High-latency commands demote the delegate to low priority, pending SST ingestion can force yield, and pre-command flushes occur before commands that need an up-to-date engine view or cannot be safely ordered behind pending writes.

`process_raft_cmd` marks WAL-sync requirements, calls coprocessor `pre_apply`, executes the command, binds the current term into the response, matches the corresponding pending callback by index/term/conf-change status, pushes observer and callback data into `ApplyCallbackBatch`, and optionally persists apply state immediately.

`apply_raft_cmd` is savepoint-protected. It runs coprocessor `pre_exec`; otherwise it sets execution index/term, establishes a write-batch savepoint, and calls `exec_raft_cmd`. Deterministic user-visible errors such as epoch mismatch or flashback-state mismatch roll back to the savepoint and become error responses while still advancing applied index. Successful admin commands capture the old epoch and later assert that expected epoch dimensions changed. If execution returns `WaitMergeSource`, the caller does not advance apply state yet.

Normal write execution loops through all requests in the Raft command. Puts and deletes check key-in-region against origin keys, then write prefixed data keys into the configured CF or default CF, updating size/key/lock-CF metrics and bucket stats. Delete-range validates ordering, bounds, and CF names; it may call engine range-deletion APIs immediately, then returns an `ExecResult::DeleteRange` for raftstore observation. SST ingestion validates metadata and importer state, pushes the validated SST into `ApplyContext.pending_ssts`, marks `has_pending_ssts`, and returns `ExecResult::IngestSst`.

Admin execution dispatches by `AdminCmdType`. Conf changes update peers and conf version, set tombstone state on self-removal, and persist `RegionLocalState`. Batch split constructs all post-split Regions and new peer IDs, updates pending-create-peer bookkeeping to resolve races with snapshot/raft-message peer creation, persists new Region state plus initial apply states, and updates the derived Region. Merge prepare persists `PeerState::Merging`; merge commit first sends `SignificantMsg::CatchUpLogs` to the source Region and yields, then after source readiness validates source local state, expands target key range, tombstones the source, and returns `ExecResult::CommitMerge`. Rollback checks persisted merge state and returns to normal. Flashback toggles Region flashback fields. Batch witness switching updates peer witness flags and may set `wait_data`, making subsequent apply work pause until a `Recover` message arrives.

When `ApplyContext::commit` or `flush` writes to the engine, pending SSTs are ingested first, then the KV write batch is written with `sync` set if any command requested WAL sync and WAL is enabled. A real synced KV write updates `last_kv_sync_success_at_millis`. Oversized write batches are replaced to release memory; smaller ones are cleared for reuse. Ingested SST files are deleted after the write that made the applied index durable. Coprocessor flush observers run before callbacks, then write callbacks are invoked and histograms are flushed.

`ApplyContext::finish_for` runs `pre_persist` hooks, optionally writes the latest apply state into the current write batch, then appends an `ApplyRes` containing Region ID, apply state, applied term, exec results, metrics, bucket stats, and outstanding write sequence numbers. If the current KV write batch has not yet been written, the result is counted so a later write sequence number can be attached after `write_to_db`.

`ApplyPoller::end` flushes any pending writes and apply results for the poll batch, updates delegates' `last_flush_applied_index`, clears `has_pending_ssts`, and emits memory traces. This is the main handoff point back to raftstore via the `Notifier`.

Merge waiting uses `YieldState` and `WaitSourceMergeState`. A target Region that cannot commit a merge stores the current entry, remaining entries, and pending messages, and asks the source Region to catch up. The source Region handles `LogsUpToDate` by destroying itself, setting the shared atomic to its Region ID, and sending `Noop` to the target. On a later poll, the target sees the atomic, sets `ready_source_region_id`, and resumes the stored entries/messages.

Snapshot messages first force a flush when a pending apply result for the same Region has not yet persisted the current apply index. Witness peers and peers waiting for data do not generate snapshots. Successful snapshot requests schedule `SnapGenTask::Gen` with a KV snapshot, applied term/state, cancellation token, and destination store.

Observer-change messages validate Region epoch, commit pending writes so the returned snapshot includes all previous writes, install CDC/RTS/PITR observe handles, and invoke the read callback with a `RegionSnapshot`. Stale observe IDs and epoch mismatches return errors.

Compact checks and unsafe force compaction are handled as apply-side state changes that create `ExecResult`s for raftstore. Witness compact-log behavior is special: compact requests can be queued until `voter_replicated_index` proves all voters have replicated enough logs, preventing a witness from deleting logs needed by a lagging voter.

## State And Persistence Behavior

- `RaftApplyState` is the central durable progress record. This code writes it under `keys::apply_state_key(region_id)` in `CF_RAFT`, deliberately through the KV engine so apply index and KV data changes share durability ordering.
- `RegionLocalState` is persisted with `write_peer_state` for conf changes, splits, merge state transitions, flashback toggles, witness transitions, and tombstones. New split Regions also get `write_initial_apply_state`.
- Normal KV mutations are written through `WriteBatchWrapper<EK::WriteBatch>`, which lets coprocessors wrap or observe the apply write batch.
- `ApplyContext::write_to_db` preserves operation order around SST ingestion: pending SSTs are ingested before writing later put/delete operations in the same apply context, preventing later writes from being reordered before ingested data.
- Ingested SST files are deleted only after the apply index that prevents replay is durably written. Coprocessors may move SSTs into `pending_delete_ssts` to delay deletion for custom engines.
- Write-batch savepoints isolate command execution. When a command returns a deterministic apply error, all writes from that command are rolled back before an error response is generated.
- `sync_log_hint` accumulates command-level WAL-sync requirements. Admin metadata changes and SST ingestion generally require sync; compact log, transfer leader, compute hash, and verify hash do not.
- `disable_wal` supports WAL-disabled writes and attaches synthetic sequence numbers through `SequenceNumber::pre_write/post_write`.
- `last_flush_applied_index` tracks what apply index has been persisted for a delegate. Snapshot generation and batching decisions use it to force flushes before taking snapshots or before commands that need an up-to-date engine snapshot.
- `ApplyRes.write_seqno` carries sequence numbers from committed writes so downstream raftstore logic can associate apply results with engine write order.
- `pending_cmds` is memory-only proposal callback state. It is cleared as stale on re-registration/drop, notified as region-removed on destroy, or silently cleared during global shutdown.
- `yield_state` and `wait_merge_state` are memory-only scheduling state. They preserve unprocessed entries/messages across poll rounds but are not durable.
- `pending_create_peers` is shared memory used by split handling to coordinate with peer creation from raft messages/snapshots. It is updated before split metadata is persisted and rolled back for already-existing split Regions.
- `wait_data` pauses apply for a peer switched from witness back to non-witness until a recovery message arrives, and `exec_batch_switch_witness` persists `PeerState::Unavailable` in that state.
- `buckets: Option<BucketStat>` tracks region bucket write statistics derived from `BucketMeta` carried in apply tasks.
- Memory accounting is maintained through `ApplyMemoryTrace`, `MEMTRACE_APPLYS`, `MEMTRACE_APPLY_ROUTER_ALIVE`, `MEMTRACE_APPLY_ROUTER_LEAK`, and entry-cache gauges.

## Dependencies And Integration Points

- The code is generic over `EK: KvEngine`, and depends on engine traits for snapshots, write batches, CF operations, range deletion, sequence numbers, performance context, and SST metadata.
- It depends on `RaftEngineReadOnly` to fetch cached-missing committed entries by `(region_id, start, end)` when `CachedEntries` only carries a range.
- It integrates with kvproto command and metadata types: `RaftCmdRequest/Response`, `AdminRequest/Response`, `Region`, `RegionEpoch`, `RaftApplyState`, `RaftTruncatedState`, `RegionLocalState`, `MergeState`, `SstMeta`, and Raft `Entry`/`ConfChange` messages.
- It integrates with raftstore peer state through `Peer`, `Registration::new`, `PeerMsg`, `SignificantMsg`, `TaskRes`, `ApplyRes`, `write_peer_state`, `write_initial_apply_state`, `entry_storage::first_index`, and utility epoch/key/flashback checks.
- It integrates with TiKV coprocessors through `CoprocessorHost`, `Cmd`, `CmdBatch`, `CmdObserveInfo`, `RegionState`, `ApplyCtxInfo`, `WriteBatchWrapper`, and observer hooks for pre-apply, pre-exec, post-exec, apply-state persistence, empty commands, and flush notification.
- It integrates with SST ingestion via `SstImporter<EK>`, `SstMetaInfo`, importer validation, ingest, and delete.
- It integrates with snapshot generation through `Scheduler<SnapGenTask<_>>` and `SnapGenTask::Gen`.
- It integrates with the batch runtime through `Fsm`, `PollHandler`, `HandlerBuilder`, `BatchRouter`, `BatchSystem`, `BasicMailbox`, `Priority`, control FSMs, and resource metering.
- It integrates with resource control by charging `Msg::Apply` entry sizes to the resource group name embedded in each entry header and returning the dominant group.
- It integrates with health/latency monitoring through `LatencyInspector`, apply-wait/apply-process recording, local Prometheus histograms, slow logs, and write trackers.
- It integrates with PD bucket statistics through `BucketMeta` and `BucketStat`.
- It integrates with TiKV failpoints throughout apply, split, merge, snapshot, conf change, and write paths for deterministic fault injection.
- It integrates with witness behavior: witness peers skip normal write entries when safe, defer compacting logs until voter replication is sufficient, skip consistency hash snapshots, and block snapshot generation.
- The test module in this chunk integrates with `engine_test`, `test_sst_importer`, `PanicEngine`, dummy schedulers, temporary directories, and custom coprocessor observers to validate behavior.

## Risks And Edge Cases

- Apply index continuity is critical. `handle_raft_committed_entries` panics on gaps because applying entries out of order would corrupt Region state.
- Apply state must be persisted with KV data, not in raft RocksDB. Moving it to a separate WAL would allow power loss to persist applied index without the corresponding KV mutations.
- Callback handling is fragile: callbacks must be consumed exactly once, stale proposals must be failed with the right term, and missing Region callbacks must release transaction latches without falsely acknowledging success.
- Savepoint rollback is required for command-level errors. A key-not-in-region or epoch-not-match error must not leave partial KV writes in the batch while still advancing applied index.
- `should_write_to_engine` and `should_sync_log` encode durability and ordering boundaries. Weakening these checks around `CommitMerge`, hash computation, rollback merge, delete range, or SST ingestion can expose stale snapshots or replay non-idempotent ingestion.
- SST ingestion has multiple correctness hazards: metadata must match Region ID/epoch/range/CF, pending writes must flush before ingestion, later writes must not be reordered before ingestion, and SST files must not be deleted before replay is impossible.
- Delete-range handling performs immediate engine range deletion before returning `ExecResult::DeleteRange`. CF validation, boundary checks, and notify-only behavior must remain precise to avoid deleting outside the Region.
- Conf-change logic must reject duplicate peers, mismatched peer IDs, illegal joint-state transitions, direct voter removal in enter-joint mode, and witness-role mismatches. Self-removal must stop later entries in the same Ready.
- The admin epoch invariant check after successful admin execution intentionally panics if an admin command did not change the epoch dimensions declared by `admin_cmd_epoch_lookup`.
- Split handling races with peers created by raft messages or snapshots. Incorrect `pending_create_peers` transitions can leave duplicate or missing split peer state.
- Merge commit is deliberately asynchronous. If target-side apply writes before source-side apply is stopped, both delegates could race on apply state and Region metadata.
- Witness compacting is conservative because a witness may be the only source of logs for a lagging voter after leader failure. Compacting by local compact index alone can harm recovery.
- `can_witness_skip` parses protobuf tags manually to avoid full decoding. Changes to `RaftCmdRequest` wire layout or malformed data handling need careful compatibility review.
- Low-priority yielding around delete-range and SST ingestion relies on `has_pending_ssts`, delegate priority, write-size thresholds, and duration thresholds. Bugs here can cause starvation, duplicated SST overlap, or excessive latency for normal Regions.
- `Apply::try_batch` must merge only same-region tasks and preserve monotonic term/commit index/commit term while carrying the newest bucket metadata.
- `ApplyRouter::schedule_task` creates a mailbox from `Registration` when a Region is absent, but drops many other messages. New message variants need explicit missing-mailbox semantics.
- `Drop for ApplyFsm` reports stale callbacks except during shutdown. If shutdown detection is wrong, callbacks may either leak or receive spurious errors.
- Snapshot generation must flush pending apply state first; otherwise the generated snapshot can contain KV data without matching durable apply state.
- Coprocessor hooks can filter execution, skip persistence, move SST cleanup responsibility, or observe command batches. Apply invariants must hold even when observers are installed.
- The chunk ends inside tests, so later test coverage for bucket batching, observers, SST checking, splits, conf-change removal, and batch-split validation is outside this chunk.

## Test Signals

The visible tests in this chunk are substantial and exercise both helper classifiers and end-to-end apply behavior:

- `test_can_witness_skip` checks witness skip classification for empty normal commands, admin commands, normal put commands, legacy conf changes, and v2 conf changes.
- `test_should_sync_log` verifies which admin commands require KV WAL sync and confirms SST ingestion sync behavior.
- `test_should_write_to_engine` verifies pre-command flush requirements for compute hash, delete range, and SST ingestion with/without pending writes.
- `test_has_high_latency_operation` verifies low-priority classification for `IngestSst` and `DeleteRange`, not normal put.
- `test_basic_flow` starts an apply batch system, registers a Region, verifies delegate registration state, checks missing-Region callback failure, stale proposal cleanup, empty-entry snapshot flush behavior, apply-result contents, destroy notifications, and post-destroy missing-Region behavior.
- `test_handle_raft_committed_entries` executes normal v1 Raft command entries through a real test engine. It validates puts, CF writes, epoch mismatch, key-not-in-region rollback atomicity, deletes, delete ranges, priority/yield behavior, SST ingestion ordering and epoch failure, write-batch key-limit flushing, observer pre/post query counts, metrics, and callbacks.
- `test_handle_raft_committed_entries_from_v2` repeats the same broad write-path coverage using the simple-write v2 command encoding with compatible learner support enabled.
- `test_apply_yield_with_msg_size` validates write-size based apply yielding and dynamic configuration changes to `apply_yield_write_size`.
- `test_handle_ingest_sst` validates ordering across a sequence of put, ingest, put, ingest, put entries, ensuring final engine values match the latest logical operation for each key combination.
- The helper test scaffolding includes `EntryBuilder`, `EntryBuilderUsingSimpleWrite`, `ApplyObserver`, `TestNotifier`, `validate`, `batch_messages`, `fetch_apply_res`, `proposal`, and callback constructors. These give useful patterns for future tests that need to inspect delegate state, batch messages into one poll, capture apply results, or simulate coprocessor behavior.
- `test_bucket_version_change_in_try_batch` begins at the chunk boundary, but its assertions are not included in lines 1-7124.

Additional high-value tests for changes touching this chunk should cover:

- Failpoint-driven interruption before/after split, prepare merge, commit merge, snapshot flush, and conf changes.
- Power-loss style durability scenarios where apply state, KV writes, and SST deletion ordering are inspected.
- Witness compact-log queuing with varying `voter_replicated_index` and pending compact queues.
- Merge target/source interleavings around `WaitMergeSource`, `LogsUpToDate`, and `Noop` wakeups.
- Observer combinations where `pre_exec` filters execution, `pre_persist` refuses persistence, and `post_exec` delays SST deletion.
- Missing-mailbox behavior for every `Msg` variant added in the future.
- Shutdown/drop paths to ensure callbacks are either consumed silently during shutdown or notified as stale/removed during normal operation.
