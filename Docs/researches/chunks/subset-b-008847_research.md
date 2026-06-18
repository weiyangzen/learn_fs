# sources/storage-engines/tikv/components/raftstore/src/store/fsm/apply.rs lines 7125-8262

## Scope

This chunk covers the tail of the `apply.rs` unit-test module for the raftstore apply finite-state machine. It does not define production apply logic directly; instead it exercises high-risk behavior implemented earlier in the file, especially apply batching, observer hooks, command observation, SST ingestion validation, region splitting, peer removal persistence, pending command safety, flashback command gating, and batch-split validation.

The surrounding test helpers used by this range are defined earlier in the same module: `fetch_apply_res` receives `PeerMsg::ApplyRes` notifications, `apply` builds an `Apply<Callback<_>>` from committed entries and proposals, `cb`/`cb_conf_change` wrap write callbacks, `EntryBuilder` serializes `RaftCmdRequest` entries, `ApplyObserver` implements query/admin/region/cmd observer hooks, and `validate` schedules an in-worker delegate inspection.

## Purpose

The tests in this chunk validate that apply FSM externally visible results stay consistent with durable raftstore state and coprocessor side effects. They focus on cases where apply progress can diverge from command execution:

- bucket metadata can change across batched apply tasks;
- observer hooks can suppress execution or persistence;
- command observers must see applied command batches at the correct observation level;
- split and conf-change admin commands mutate region metadata and apply state;
- SST ingestion has strict metadata and cleanup requirements;
- flashback state blocks ordinary commands but allows flashback-marked commands;
- validation routines reject malformed split and ingest metadata before state mutation.

## Important APIs, Types, and Helpers

`test_bucket_version_change_in_try_batch` creates an apply batch system with a single apply worker and no low-priority worker, registers a region, submits two `Apply` tasks with `BucketMeta` versions 1 and 2, and asserts that both the returned `ApplyRes.bucket_stat.meta.version` and the delegate's cached `buckets.meta.version` settle at 2. This is a regression signal for `try_batch` and bucket-stat propagation when multiple apply messages for one region are coalesced.

`test_exec_observer` uses `ApplyObserver` as a query, admin, and region-change observer. The observer's important controls are `skip_persist_when_pre_commit`, `filter_compact_log`, `filter_consistency_check`, and `delay_remove_ssts`. The test verifies that:

- `pre_persist` can delay persistence of `RaftApplyState`, so the in-memory `ApplyRes.apply_state.applied_index` can be one ahead of the CF_RAFT persisted state.
- `pre_exec_admin` can filter `CompactLog`, `ComputeHash`, and `VerifyHash`; filtered admin commands still advance `applied_index` and `applied_term`, but do not emit `ExecResult`.
- unfiltered `CompactLog` updates `RaftApplyState.truncated_state` and emits an execution result.
- `post_exec_admin` observes region-modifying admin commands such as `BatchSplit` and merge commands.
- `PrepareMerge` triggers apply-state persistence.
- `post_exec_query` can move ingested SSTs from `pending_handle_ssts` either to immediate `delete_ssts` or delayed `pending_delete_ssts`.

`test_cmd_observer` registers `ApplyObserver` as a `CmdObserver` and validates `on_flush_applied_cmd_batch`. It checks that command batches are emitted after normal puts, that registering a CDC observer during a blocked apply worker sees a snapshot including the just-applied write, that later command batches carry the registered CDC observe ID, and that stopping observation or targeting an absent region produces the expected non-observed batch or `RegionNotFound` response.

`test_check_sst_for_ingestion` directly covers `check_sst_for_ingestion`. The routine requires a valid UUID, CF name equal to `CF_DEFAULT` or `CF_WRITE`, matching region id, matching region epoch conf/version, and a range whose start/end are in the target region. The test covers invalid UUID/CF/id/epoch/range and the valid cases.

`new_split_req`, `SplitResultChecker`, and `error_msg` are local test helpers for split coverage. `SplitResultChecker::check` reads `RegionLocalState` and `RaftApplyState` from CF_RAFT to confirm split outputs: peer state is `Normal`, region id/range/peers/epoch are correct, merge state is absent, and newly created regions have initial raft apply state and truncated state at `RAFT_INIT_LOG_INDEX`.

`test_split` drives `AdminCmdType::BatchSplit` through the apply FSM. It tests rejected split requests for missing peer IDs, empty request lists, out-of-range keys, empty split keys, descending or duplicate keys, and per-request peer-id count validation. It then verifies successful single and multi-split cases for both `right_derive = true` and `right_derive = false`, including derived region selection, region epoch version increments, persisted region boundaries, cloned peer store IDs with new peer IDs, and CDC observer epoch mismatch after the region epoch changes.

`test_conf_change_remove_node_update_apply_state` applies a normal put and then a `ChangePeerV2` remove-self command. It asserts that the persisted `RaftApplyState` matches the `ApplyRes.apply_state` both before and after removal, and that the removal advances the applied index. The comment explains the safety requirement: a removed peer may be taking a snapshot, so stale apply state would break the coprocessor cache assumption that snapshot data matches apply state and could return stale cached reads.

`pending_cmd_leak` and `pending_cmd_leak_dtor_not_abort` intentionally construct a `PendingCmd` with `Callback::None` inside `panic_hook::recover_safe`. They assert the leak guard panics, but that a destructor running during an existing panic does not double-panic and abort the process.

`flashback_need_to_be_applied` registers a region marked `is_in_flashback`, then writes a persisted `RegionLocalState` with `is_in_flashback = false` to simulate disk/cache disagreement. It verifies that an ordinary admin command (`TransferLeader`) is rejected with `flashback_in_progress`, while a `PrepareFlashback` request with `WriteBatchFlags::FLASHBACK` is allowed and produces an apply result.

`new_batch_split_request` and `test_validate_batch_split` directly test `validate_batch_split`: empty `splits.requests` is rejected, legacy `AdminCmdType::Split` without batch requests is rejected, every split key must be non-empty and strictly increasing, every request must supply one new peer id per existing peer, and the final split key must be inside the region's exclusive end range.

## Control Flow

Most tests follow the same apply-system pattern:

1. Create temporary KV engine/importer, notification channel, scheduler, `Config`, `ApplyRouter`, and apply batch system.
2. Build `super::Builder<KvTestEngine>` with coprocessor host, router, engine, importer, store id, pending-create-peer map, and sync timestamp.
3. Spawn the apply system and send `Msg::Registration` for the target region.
4. Construct raft log entries with `EntryBuilder`, send `Msg::apply(apply(...))`, receive callback responses or `ApplyRes`, and assert on in-memory delegate state and persisted CF_RAFT state.
5. Shut down the batch system.

The observer tests add additional control edges. `Msg::Validate` is used as an in-worker barrier in `test_cmd_observer`, blocking the apply worker while another apply and a `Msg::Change` observer-registration task queue behind it. Once unblocked, the snapshot callback must observe the write from the same serialized apply stream. `test_exec_observer` toggles observer atomics between apply tasks so each phase isolates one hook behavior.

The split tests layer validation and persistence checks over the same flow. The `exec_split` closure submits one split command at the current epoch, waits for its proposal callback, and increments the log index. The test manually tracks expected epoch versions after successful splits, then `SplitResultChecker` reads persisted metadata to ensure the apply path wrote exactly the region layout implied by the split request and `right_derive` flag.

## State and Persistence Behavior

The chunk repeatedly checks `RaftApplyState` stored under `keys::apply_state_key(region_id)` in `CF_RAFT`. Important persistence contracts covered here include:

- applied indexes advance for filtered admin commands even when no `ExecResult` is produced;
- disabling `pre_persist` can make returned apply state newer than persisted state until a later persist point;
- enabling normal persistence writes the apply state by `finish_for`;
- `PrepareMerge` forces a durable apply-state update;
- remove-self conf changes must persist the new apply state before notifying raftstore;
- split-created regions persist initial apply state and normal `RegionLocalState`;
- flashback and split admin paths persist modified `RegionLocalState` through `write_peer_state`.

KV data state is also checked indirectly. Puts are verified through proposal callbacks, command-observer snapshots, and engine reads in adjacent tests. SST ingest state is exercised by writing a generated SST into the importer save path, applying `IngestSst`, and asserting cleanup queues in `ApplyCtxInfo`: delayed removal moves files to `pending_delete_ssts`, while normal removal moves them to `delete_ssts`.

Region metadata persistence is central to `test_split` and `test_conf_change_remove_node_update_apply_state`. Splits rewrite the original region and create new region-local states with updated ranges, peers, and epoch version. Remove-self conf change persists a higher applied index so snapshots taken concurrently by the removed peer cannot expose stale coprocessor cache state.

## Dependencies and Integration Points

The tests integrate the apply FSM with:

- `create_apply_batch_system`, `ApplyRouter`, `Msg::Registration`, `Msg::apply`, `Msg::Change`, `Msg::Validate`, and `Msg::destroy` from the apply batch system API.
- `CoprocessorHost` observer registries for query, admin, region-change, and command observers.
- `CmdObserver::on_flush_applied_cmd_batch` and `CmdBatch` observe IDs for CDC/RTS/PITR command observation.
- `RaftCmdRequest`, `AdminRequest`, `Request`, `Entry`, `Proposal`, `Callback`, `WriteResponse`, and `ReadResponse` protobuf/control types.
- TiKV engine traits and CF names, especially `KvEngine`, `KvTestEngine`, `CF_RAFT`, `CF_DEFAULT`, `CF_WRITE`, and `CF_LOCK`.
- importer/SST types such as `SstMeta`, generated SST files, and pending SST cleanup lists.
- region metadata types `Region`, `RegionEpoch`, `RegionLocalState`, `PeerState`, `ChangePeerRequest`, and `ConfChangeType`.
- flashback flags via `WriteBatchFlags::FLASHBACK` and region `is_in_flashback` state.

The direct production routines covered by this chunk are `validate_batch_split` and `check_sst_for_ingestion`; the rest of the range is integration-style coverage for earlier `ApplyDelegate` and `ApplyFsm` behavior.

## Risks and Edge Cases

Persistence ordering is the main risk surfaced by these tests. Observer hooks can intentionally defer persistence, but apply results, snapshots, and coprocessor cache assumptions still require precise boundaries for when state is durable. The remove-self test documents a linearizability hazard if a concurrently generated snapshot contains data newer than its apply state.

Observer filtering is another risk. Filtered admin commands still advance the raft applied index. That is correct for observer-driven suppression, but any change to filtering semantics could accidentally skip index advancement or emit side effects for filtered commands.

SST ingestion combines durable KV changes with external file lifecycle management. The chunk highlights risks around stale pending SST handles, delayed file deletion, invalid CF names, wrong region epochs, and range validation.

Split validation is intentionally strict. Empty keys, non-ascending keys, duplicate keys, out-of-range keys, missing batch requests, legacy split requests, and mismatched peer-id counts all have explicit coverage because accepting any of them can corrupt persisted region layout or create peers with inconsistent membership.

Command observation depends on serialized apply ordering. Registering an observer while the apply worker is blocked must not observe a stale snapshot, and stopped observers must not receive later command batches. Epoch mismatch handling after splits is part of this same integration surface.

Flashback handling has a subtle cache-vs-disk state risk. The test demonstrates that the in-memory region flashback flag can block normal commands even if persisted `RegionLocalState` was manually set otherwise, while explicit flashback commands with the required flag remain applicable.

## Test Signals

This chunk is itself test code. High-value signals are:

- bucket version propagation: `test_bucket_version_change_in_try_batch`;
- observer hook behavior and SST cleanup: `test_exec_observer`;
- command observer flushing and observer registration ordering: `test_cmd_observer`;
- SST metadata validation: `test_check_sst_for_ingestion`;
- batch split execution and persisted region/apply-state checks: `test_split`;
- remove-self conf-change apply-state persistence: `test_conf_change_remove_node_update_apply_state`;
- pending command leak guard panic behavior: `pending_cmd_leak` and `pending_cmd_leak_dtor_not_abort`;
- flashback command gating: `flashback_need_to_be_applied`;
- standalone batch split validation: `test_validate_batch_split`.

These tests rely on timeout-based channels (`recv_timeout`) and temporary engines/importers, so failures usually indicate either a real apply/control-flow regression or a worker scheduling/deadlock issue in the apply batch system.
