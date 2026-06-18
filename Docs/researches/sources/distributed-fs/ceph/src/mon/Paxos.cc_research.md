# sources/distributed-fs/ceph/src/mon/Paxos.cc

## Purpose

`Paxos.cc` implements the Ceph monitor Paxos state machine used by monitor services to commit ordered versions of control-plane state. It handles leader recovery, proposal numbering, collect/last exchange, begin/accept/commit, state sharing to lagging peers, leases for readable/writeable service state, trimming, shutdown/restart, and service-facing read/write APIs.

This is not a generic library implementation: it is tightly integrated with `Monitor`, `MonitorDBStore`, `MMonPaxos`, monitor elections, timer events, perf counters, and service transactions. Each committed version stores an encoded monitor DB transaction that can be replayed into the local store.

## Important APIs and Functions

Initialization APIs are `init`, which loads `last_pn`, `accepted_pn`, `last_committed`, and `first_committed` from stable storage, and `init_logger`, which registers Paxos perf counters for leader/peon starts, refreshes, begin/commit/collect latencies, timeouts, state sharing, and proposal number allocation. `dump_info` emits the core persistent counters.

Phase 1 is `collect` on the leader and `handle_collect` on peons. The leader enters recovering state, discovers any local uncommitted value at `last_committed + 1`, chooses a new globally unique proposal number via `get_new_proposal_number`, sends `OP_COLLECT` to quorum peers, and sets a collect timeout. Peons accept higher proposal numbers by persisting `accepted_pn`, reply with `OP_LAST`, share committed state if the leader is behind, and include any accepted-but-uncommitted value and its pending proposal number.

State catch-up is handled by `share_state` and `store_state`. `share_state` reads committed version bufferlists from the monitor store into an outgoing message. `store_state` takes received version bufferlists, filters them to the contiguous range after local `last_committed`, writes each version, decodes each embedded transaction into the same store transaction, advances `last_committed`, refreshes `first_committed`, and clears obsolete uncommitted tracking.

The leader handles `OP_LAST` in `handle_last`: it records peer committed ranges, bootstraps if version ranges are incompatible, stores any shared committed state, sends commits to lagging peers, retries collection if a peer reports a higher accepted proposal number, learns the highest-numbered uncommitted value, and either reproposes that value or becomes active and extends leases after all quorum members respond.

Phase 2 starts with `begin`. The leader asserts it has enough collected responses, records local acceptance, wraps the initial base case if `last_committed == 0`, persists the pending value under the next version plus `pending_v`/`pending_pn`, sends `OP_BEGIN` to peers, and sets an accept timeout. Peons handle `OP_BEGIN` by rejecting stale proposal numbers, persisting the pending value and pending proposal metadata, entering updating state, cancelling the lease, and replying with `OP_ACCEPT`.

Commit flow is `handle_accept`, `commit_start`, `commit_finish`, and `handle_commit`. The leader waits for every quorum member, not just a bare majority, before committing, because peers may still be sharing stale state. `commit_start` writes `last_committed + 1`, decodes and appends the proposed transaction to the local store transaction, queues it asynchronously, and moves to writing state. `commit_finish` runs after store completion, advances in-memory `last_committed`, refreshes `first_committed`, sends `OP_COMMIT` with the committed value to peers, clears `new_value`, refreshes services, runs commit finishers, extends leases, finishes the round, and triggers trim or pending proposals. Peons process `OP_COMMIT` by `store_state` and refresh.

Lease APIs are `extend_lease`, `handle_lease`, `handle_lease_ack`, `lease_ack_timeout`, `reset_lease_timeout`, `lease_timeout`, and `lease_renew_timeout`. Leaders broadcast lease expirations tied to `last_committed`, collect ACKs and feature maps from all quorum members, and renew before expiration. Peons accept leases only if they are peons and `last_committed` matches, update `lease_expire`, enter active state, ACK with feature maps, reset timeout, and release active/readable waiters.

Service-facing APIs include `is_readable`, `read`, `read_current`, `is_lease_valid`, `is_writeable`, `get_pending_transaction`, `queue_pending_finisher`, `trigger_propose`, and `propose_pending`. Services build one pending monitor DB transaction, queue finishers, and ask Paxos to propose when active and unplugged. `propose_pending` encodes the transaction, swaps pending finishers into committing finishers, enters updating state, and starts `begin`.

Lifecycle APIs include `trim`, `cancel_events`, `shutdown`, `leader_init`, `peon_init`, `restart`, `reset_pending_committing_finishers`, `dispatch`, and `is_consistent`. `dispatch` verifies monitor role/source sanity and routes `MMonPaxos` opcodes to handlers.

## State and Persistence Behavior

Stable keys include `last_pn`, `accepted_pn`, `last_committed`, `first_committed`, numeric committed-version keys under the Paxos service name, and pending proposal metadata `pending_v`/`pending_pn`. Accepted but uncommitted values are intentionally persisted before peer acknowledgement so a later leader can learn and repropose them.

Committed version values are encoded `MonitorDBStore::Transaction` bufferlists. Applying a commit writes the version bufferlist and decodes/appends its transaction operations atomically, so local service state and the Paxos log advance together. The initial commit additionally sets `first_committed` to 1 in the wrapped transaction.

Timers are part of the correctness model. Collect, accept, lease ACK, lease, and renew timers cause fresh elections or lease extension. `restart` flushes the store if the state was writing to avoid losing async commit completion under a state transition. `shutdown` waits for in-progress queued commits before cancelling contexts and removing perf counters.

Trimming removes old committed version keys from `first_committed` up to a bounded end based on `paxos_min` and `paxos_trim_max`, updates `first_committed`, optionally compacts the store range, and queues a finisher to clear the `trimming` flag. Trimming is only triggered after rounds finish and `should_trim` is true.

## Dependencies and Integration Points

The implementation depends on `Paxos.h`, `Monitor`, `MonMap`, `MMonPaxos`, monitor DB transactions, monitor timers, monitor elections/bootstrap, session feature maps, perf counters, Ceph clocks, and formatter/debug infrastructure. It calls `mon.refresh_from_paxos` after committing or storing state so each PaxosService can update from the committed store.

Monitor role state is central. Leaders call `collect`, `begin`, `commit_start`, and `extend_lease`; peons handle collect/begin/commit/lease messages. Bootstrap/election is the recovery answer for incompatible trim ranges, proposal conflicts, collect/accept timeouts, and lease failures.

## Risks and Edge Cases

The highest-risk behavior is persistence ordering. Proposal numbers and accepted values must hit stable storage before replies, and committed transactions must atomically update both Paxos metadata and service state. Any change that weakens this can violate Paxos safety after crashes or leader changes.

Version range compatibility is another critical edge. If a peer's `first_committed` is beyond the local `last_committed + 1`, or if a peon is too far behind the leader's trim floor, the code bootstraps rather than trying to fill an impossible gap. Trimming policies must preserve enough history for normal catch-up.

The leader waits for all quorum members to accept before commit, even though the log message says "got majority"; this is a deliberate stale-state avoidance tradeoff. Changing this behavior requires an explicit lease revocation/catch-up design. Lease handling is also sensitive to clock skew, lag, and message timestamps; `warn_on_future_time` only warns and does not correct time.

Async store commits interact with locks and shutdown. `C_Committed` reacquires `mon.lock`, aborts if shutdown, and otherwise calls `commit_finish`. The shutdown path adopts the already-held lock and waits for `commits_started` to drain, so lock ownership assumptions are important.

## Test Signals

Tests should cover proposal number monotonicity and rank uniqueness, local recovery of pending uncommitted values, peon rejection of stale proposal numbers, leader retry after higher peer proposal number, state sharing to lagging peers, bootstrap on trimmed gaps, initial commit behavior, async commit completion, lease ACK/timeout/renew paths, read/write gating by active state and lease validity, trimming boundaries, restart while writing, and shutdown with queued commits. Fault-injection hooks using `paxos_kill_at` are explicit test signals for crash points through collect, begin, accept, commit, and refresh.
