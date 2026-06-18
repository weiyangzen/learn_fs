# sources/storage-engines/tikv/components/raftstore/src/store/peer.rs lines 6536-7003

## Scope

This chunk covers the entire `#[cfg(test)] mod tests` at the end of TiKV raftstore's `store/peer.rs`. The selected lines are not production peer logic; they are unit tests for production helpers and local invariants defined earlier in the same file:

- synchronous-log and urgent-admin-command classification;
- one-byte `ProposalContext` raft-entry metadata encoding;
- `RequestInspector` policy selection for admin, read, write, stale-read, replica-read, read-quorum, and invalid request batches;
- `ProposalQueue` ordering, proposal lookup, stale-removal, propose-time lookup, and committed-callback behavior;
- `CmdEpochChecker` conflict tracking for proposed epoch-changing admin commands;
- `TransferLeaderContext` wire encoding and decoding.

Because this is a terminal file chunk, it also confirms that `peer.rs` ends at line 7003. The tests import `protobuf::ProtobufEnum`, `super::*`, `crate::store::msg::ExtCallback`, and `crate::store::util::u64_to_timespec`, then exercise private items through Rust's child-module visibility.

## Purpose

- Lock down which `AdminCmdType` values force raft log synchronization via `get_sync_log_from_request()`.
- Lock down which admin commands are considered urgent by `is_request_urgent()`, which affects follower lazy-commit behavior.
- Verify that `ProposalContext` flags round-trip through the compact byte-vector representation stored in raft entry context bytes.
- Verify `RequestInspector::inspect()` classifies requests into local read, stale read, read-index, normal proposal, transfer-leader proposal, and conf-change proposal paths, and rejects unsupported or mixed batches.
- Verify `ProposalQueue` can locate proposals by `(term, index)`, remove stale/front proposals as committed entries are processed, and preserve associated propose-time metadata.
- Verify uncommitted proposals from a previous term do not have their "committed" extension callback fired when later-term committed entries pass through the queue.
- Verify `CmdEpochChecker` serializes conflicting epoch-sensitive proposals, wakes waiters when conflicts apply, clears state on term advance, and reports stale callbacks on drop.
- Verify `TransferLeaderContext` remains backward-compatible for empty context, command-reply context, and custom coprocessor key/value context payloads.

## Important APIs, Types, And Functions

- `get_sync_log_from_request(&RaftCmdRequest) -> bool` returns true for admin commands that should synchronously persist raft logs before response. The test treats all admin types except `InvalidAdmin`, `CompactLog`, `TransferLeader`, `ComputeHash`, `VerifyHash`, `BatchSwitchWitness`, and `UpdateGcPeer` as sync-log commands.
- `is_request_urgent(&RaftCmdRequest) -> bool` is private and returns true for split, batch split, conf-change, conf-change-v2, compute/verify hash, prepare/commit/rollback merge, and batch switch witness admin commands. Non-admin requests are non-urgent.
- `ProposalContext` is a `bitflags` byte with `SYNC_LOG`, `SPLIT`, `PREPARE_MERGE`, `COMMIT_MERGE`, and `ROLLBACK_MERGE`. `to_vec()` emits either an empty vector or a single-byte bitset; `from_bytes()` accepts only empty or one-byte slices.
- `RequestPolicy` enumerates dispatch decisions: `ReadLocal`, `StaleRead`, `ReadIndex`, `ProposeNormal`, `ProposeTransferLeader`, `ProposeConfChange`, and `ReadIndexReplicaRead`.
- `RequestInspector` is a trait used by `Peer` and tests. It supplies `has_applied_to_current_term()` and `inspect_lease()`, while the default `inspect()` implementation performs request classification and lease/read-index decisions.
- `DummyInspector` in the test module is a minimal `RequestInspector` implementation with configurable applied-term and lease state. It isolates the policy logic from real peer state.
- `ProposalQueue<C>` stores ordered `Proposal<C>` values in a `VecDeque`. It supports `push()`, `find_propose_time()`, `pop()`, `find_proposal()`, `oldest()`, `back()`, and `gc()`.
- `Proposal<C>` comes from the raftstore FSM layer and carries `is_conf_change`, `index`, `term`, `cb`, optional `propose_time`, epoch-check metadata, and a `sent` marker.
- `Callback<S>` is the raft command callback type. These tests use write callbacks, extension callbacks, and panic/test snapshot types to assert callback invocation behavior without needing a live raftstore.
- `CmdEpochChecker<S>` tracks proposed admin commands whose application will change region epoch. It exposes local methods `propose_check_epoch()`, `post_propose()`, `last_cmd_index()`, `advance_apply()`, and `attach_to_conflict_cmd()`.
- `ProposedAdminCmd<S>` records a pending admin command's `AdminCmdType`, `AdminCmdEpochState`, raft index, and callbacks waiting on that conflict.
- `admin_cmd_epoch_lookup()` maps admin command types to whether they check or change region version/conf-version. The tests rely on its split and change-peer behavior.
- `TransferLeaderContext` is the raft message context for transfer-leader messages. It supports `None`, `CommandReply`, and `Custom(Vec<TransferLeaderCustomContext>)`.
- `TransferLeaderContext::to_bytes()`, `from_bytes()`, and `get_custom_ctx()` encode/decode context bytes using a leading tag and varint-length key/value pairs for custom coprocessor data.

## Control Flow

`test_sync_log()` iterates over every protobuf `AdminCmdType` value. For each type it builds a `RaftCmdRequest` with that admin command and asserts that `get_sync_log_from_request()` matches the hard-coded whitelist of non-sync-log admin commands. This guards against new admin command variants silently changing persistence semantics: a newly added protobuf enum value will be included by `AdminCmdType::values()` and will fail unless the helper classification and test expectation are updated consistently.

`test_urgent()` follows the same enum-wide pattern for `is_request_urgent()`. It marks split, conf-change, hash, merge, and witness-switch commands as urgent and asserts every other admin command is not urgent. It also checks a default non-admin `RaftCmdRequest` is not urgent. This covers the branch used by proposal handling to bypass follower lazy-commit delay for operations where prompt follower application matters.

`test_entry_context()` constructs several flag combinations containing a single structural context bit plus optional `SYNC_LOG`. It serializes each `ProposalContext` with `to_vec()`, parses it back with `from_bytes()`, and verifies all selected flags remain set. The test does not cover `ROLLBACK_MERGE`, empty context, unknown-bit truncation, or invalid multi-byte input, but it covers the context combinations produced by the `pre_propose()` match arms for split, prepare merge, and commit merge plus sync-log insertion.

`test_request_inspector()` builds a table of request/policy pairs, then runs it across all combinations of `applied_to_index_term` in `{true,false}` and `LeaseState` in `{Expired,Suspect,Valid}`. Admin requests are classified first: empty admin request is a normal proposal, change-peer and change-peer-v2 are conf changes, and transfer leader is a transfer-leader proposal. Non-admin writes become normal proposals. Read-only `Get` and `Snap` requests start as local reads but are downgraded to read-index unless the peer has applied the current term and the lease is valid. Stale-read flags override ordinary read handling and return `StaleRead`. Read-quorum forces `ReadIndex` even under a valid lease. Invalid command batches containing `Prewrite`, `Invalid`, or a mixture of read and write requests return errors.

`test_propose_queue_find_proposal()` fills a `ProposalQueue` with ordered proposals whose terms are derived from log index ranges. It then repeatedly appends one more proposal, checks that `find_propose_time()` returns the expected timestamp for every proposal not previously removed, calls `find_proposal()` for progressively increasing committed indexes, and verifies those proposals are removed from the queue. This exercises the core invariant that `find_proposal()` may discard all proposals in front of or at the searched `(term,index)` and that removed proposals are no longer visible through either `pop()` or `find_propose_time()`.

`test_uncommitted_proposals()` builds a queue with only term-1 proposals for entries `(1,1)` through `(5,1)`, while the simulated committed log sequence also includes later term-2 entries. It marks callbacks for committed term-1 entries as "must call" and callbacks for uncommitted term-1 entries as "must not call". Iterating through entries and invoking `find_proposal(term,index,0)` only finds matching term/index proposals. The term-1 proposals that were not committed before the term change must be notified stale by `find_proposal()` rather than having their committed extension callback invoked. The custom `DropPanic` helper makes missed or unexpected callback invocation fail the test.

`test_cmd_epoch_checker()` starts with an empty checker and a default region. It proposes a batch split at index 5 and verifies that ordinary requests and prepare-merge conflict with that version-changing command, while change-peer initially does not. It then proposes change-peer at index 6 and verifies conf-version-sensitive requests conflict with index 6, while ordinary version-sensitive requests still conflict with the earlier split at index 5. Applying through index 4 leaves both pending commands. Applying index 5 removes the split, wakes callbacks attached to it with an epoch-not-match response, and leaves the change-peer conflict. Advancing the term clears pending state and reports stale callbacks. The test also attaches multiple callbacks to one conflict index, verifies all are invoked on apply, verifies term advance invokes stale callbacks, and verifies `Drop` does the same outside shutdown.

`test_transfer_leader_context()` validates three encoding forms. `None` serializes to empty bytes and parses from empty bytes. `CommandReply` serializes to the singleton transfer-leader command-reply tag and parses back. `Custom` serializes a tagged sequence of varint-length-prefixed key/value entries, parses back to an equal value, and supports lookup by key with `get_custom_ctx()`.

## State And Persistence Behavior

- These tests do not directly write RocksDB, raft engine files, region metadata, or raft logs. Their persistence relevance is indirect: they pin helper decisions that determine raft entry context bytes, synchronous raft-log persistence, proposal lifecycle, and transfer-leader message context bytes.
- `get_sync_log_from_request()` influences whether proposed raft commands set `ProposalContext::SYNC_LOG` in `pre_propose()`. That context byte is persisted as raft entry context and later consumed when ready entries are applied or persisted.
- `ProposalContext::to_vec()` is the storage format for raft entry context metadata. The format is intentionally compact: empty for no flags, one byte for all currently supported flags. Any change from one-byte encoding affects raft-entry compatibility and should be treated as a wire/storage format change.
- `is_request_urgent()` affects in-memory scheduling/commit urgency. It does not persist state by itself, but a wrong classification can delay follower application for split/merge/conf-change style commands.
- `RequestInspector` reads applied-term and lease state but does not mutate persistent storage. In production `Peer` implementation, `has_applied_to_current_term()` compares peer storage applied term with raft term, and `inspect_lease()` can expire in-memory leader lease state if the lease is observed expired.
- `ProposalQueue` is in-memory leader-side state mapping raft log entries back to client callbacks and timing trackers. `find_proposal()` removes front proposals as entries are committed or proven stale; stale proposals are reported through `apply::notify_stale_req()`.
- `Callback::invoke_committed()` is used only when a matching proposal is known committed. The uncommitted proposal test guards against invoking committed extension callbacks for proposals superseded by later-term entries.
- `CmdEpochChecker` is in-memory gating state for proposals whose effects change region epoch. It holds callbacks for requests rejected behind a conflicting admin command, then reports `EpochNotMatch` when the conflicting command applies. It drains and reports stale callbacks on term changes or drop.
- `CmdEpochChecker::advance_apply()` builds an error response containing the current region epoch and binds the current term. This response is returned through callbacks rather than persisted.
- `TransferLeaderContext` bytes travel in raft messages, not region metadata. The custom context format is nevertheless a wire contract between transfer-leader observers/coprocessors and raftstore message handling.

## Dependencies And Integration Points

- The tests depend on protobuf enum iteration through `protobuf::ProtobufEnum`, which makes command-classification tests sensitive to new `AdminCmdType` variants.
- They depend on `kvproto::raft_cmdpb` request/response types: `RaftCmdRequest`, `Request`, admin subrequests, `AdminCmdType`, and `CmdType`.
- `RequestInspector` integrates with `WriteBatchFlags` from `txn_types`; the stale-read flag and transfer-leader proposal flag alter policy selection.
- Read policy decisions integrate with raft lease machinery through `LeaseState` and, in production, with `Peer::leader_lease`, `raft_group.raft.in_lease()`, and applied term from peer storage.
- `ProposalQueue` integrates with apply processing. Production paths call `find_propose_time()` and `find_proposal()` while handling committed entries, and waterfall metrics use proposal trackers for timing.
- `apply::notify_stale_req()` is the failure path for stale proposals and epoch-checker callbacks on term changes or checker drop.
- `CmdEpochChecker` integrates with `admin_cmd_epoch_lookup()`, `AdminCmdEpochState`, normal request epoch-check constants, and proposal paths that call `propose_check_epoch()` before raft proposal and `post_propose()` after successful admin proposal.
- `CmdEpochChecker::advance_apply()` integrates with apply advancement in the peer. Production calls remove pending epoch-changing commands once apply reaches their index, allowing later proposals that were blocked by those epoch changes to receive epoch mismatch feedback and retry.
- `Callback`, `ExtCallback`, and snapshot types integrate with raftstore's asynchronous command completion model. Tests use `engine_panic::PanicSnapshot` and `engine_test::kv::KvTestSnapshot` to avoid real storage snapshots.
- `TransferLeaderContext` depends on `bytes::Bytes`, `codec::NumberEncoder`/`NumberDecoder`, `BufferReader`, and `TransferLeaderCustomContext` from the coprocessor layer.
- `make_transfer_leader_response()` is adjacent to the transfer-leader context code and shares the same command-reply semantics, though the test chunk only validates context encoding.

## Risks And Edge Cases

- Admin command classification is brittle by design. If a new `AdminCmdType` is added, these enum-wide tests should fail until developers explicitly decide whether it requires sync-log and urgent handling.
- `get_sync_log_from_request()` and `ProposalContext::SYNC_LOG` are tied to raft-log durability behavior. Misclassifying an epoch-changing or topology-changing command as non-sync can expose durability or ordering bugs after crashes.
- `is_request_urgent()` gates follower lazy-commit behavior. Missing split/merge/conf-change style commands can increase availability windows where followers lag important region metadata changes.
- `ProposalContext::from_bytes()` truncates unknown bits for one-byte input but panics on multi-byte input. That is acceptable for current internal context bytes, but forward compatibility requires care if more than eight context flags are ever needed.
- The `test_entry_context()` combinations omit `ROLLBACK_MERGE` and empty context. Other tests or production coverage need to catch regressions in those branches.
- `RequestInspector::inspect()` allows only `Get`, `Snap`, and `ReadIndex` as read commands and a small set of write command types as write commands. New `CmdType` variants need explicit classification or they may be treated as errors.
- Mixed read/write batches are rejected. Any future batching feature that tries to mix reads and writes must alter this contract deliberately and update tests.
- Local reads require both current-term application and a valid lease. Weakening either condition can serve stale data after leader transfer or lease uncertainty.
- Stale-read flag precedence means stale reads bypass normal lease/read-index decisions. This is intentional but sensitive to header flag parsing with `WriteBatchFlags::from_bits_check()` and `from_bits_truncate()` in nearby transfer-leader handling.
- `ProposalQueue::push()` assumes strictly increasing `(term,index)` ordering. Tests cover ordered insertion only; production callers must never enqueue out-of-order proposals.
- `ProposalQueue::find_proposal()` panics if it finds a proposal in the searched term with a different index before the requested index. That panic protects an invariant but could take down a peer if proposal queue ordering or raft apply sequencing is corrupted.
- `test_uncommitted_proposals()` specifically guards committed-callback misuse across term changes. A regression here can cause client-visible success callbacks for commands that were never committed.
- `CmdEpochChecker` assumes its deque remains small because `admin_cmd_epoch_lookup()` groups epoch-changing command conflicts into version and conf-version dimensions. Adding a new epoch-changing admin class can alter this assumption.
- `CmdEpochChecker::maybe_update_term()` asserts terms never decrease. Any caller that invokes it with stale term data can panic.
- Attached callbacks must always be completed: on conflicting admin apply, term advance, or checker drop. Leaking them can hang clients waiting behind split/change-peer/merge proposals.
- `Drop` behavior differs during process shutdown: callbacks may be cleared without stale notification when `thread_group::is_shutdown(!cfg!(test))` reports shutdown. Tests run under `cfg(test)` and validate the non-shutdown path.
- `TransferLeaderContext::from_bytes()` treats an unknown tag as an error and parses custom payloads until input is exhausted. Malformed varint lengths or truncated key/value bytes propagate decode errors; tests cover only well-formed inputs.
- `TransferLeaderContext::get_custom_ctx()` returns the first matching key. Duplicate custom keys are not rejected, so coprocessor producers should avoid ambiguous duplicate entries.

## Test Signals

- The chunk itself is a set of unit test signals. Running the `raftstore` crate tests for `store::peer::tests` should exercise all functions in this range without requiring a multi-node TiKV cluster.
- Adding any `AdminCmdType` should cause `test_sync_log()` and `test_urgent()` to force an explicit classification update.
- Proposal context regressions should appear as failures in `test_entry_context()` when `to_vec()`/`from_bytes()` lose expected bits or change the single-byte representation.
- Request routing regressions should appear in `test_request_inspector()` for admin proposal type, stale read, read quorum, lease-valid local reads, applied-term gating, invalid command types, and mixed read/write batches.
- Proposal queue regressions should appear in `test_propose_queue_find_proposal()` as missing propose times, unexpected retained proposals after lookup, or failed removal of front proposals.
- Callback lifecycle regressions should appear in `test_uncommitted_proposals()` as panics from a committed callback not invoked when it should be, or from an uncommitted callback invoked incorrectly.
- Epoch conflict regressions should appear in `test_cmd_epoch_checker()` as wrong conflict indexes, stale pending commands after apply, failure to clear on term advance, or callbacks not delivered on apply/drop/term-change paths.
- Transfer-leader wire-format regressions should appear in `test_transfer_leader_context()` as failed round trips for empty, command-reply, or custom key/value contexts.
- Additional useful coverage would include `ProposalContext::ROLLBACK_MERGE`, invalid multi-byte proposal contexts, malformed `TransferLeaderContext` payloads, duplicate custom context keys, replica-read policy, and transfer-leader admin requests carrying `TRANSFER_LEADER_PROPOSAL`.
