# sources/distributed-fs/ceph/src/osd/PeeringState.cc lines 8194-8385

## Scope

This chunk covers the end of the primary peering state-machine path in `PeeringState.cc`. It includes:

- `GetMissing::react(const QueryUnfound&)` and `GetMissing::exit()`.
- The complete `WaitUpThru` state implementation.
- `PeeringState::PeeringMachine::log_enter()` and `log_exit()`.
- `operator<<(ostream&, const PeeringState&)`, the compact diagnostic formatter for PG peering state.
- `PeeringState::get_replica_recovery_order()`, which chooses an ordered list of non-primary shards needing recovery.

The declarations for these states and helpers live in `PeeringState.h`: `GetMissing` transitions to `WaitUpThru` on `NeedUpThru`; `WaitUpThru` handles `ActMap`, `MLogRec`, `QueryState`, and `QueryUnfound`; `get_replica_recovery_order()` is exposed as a public helper for recovery scheduling.

## Purpose

The peering purpose of this chunk is to bridge the final gap between collecting missing sets and activation. `GetMissing` has already requested or synthesized peer missing information. If the primary still needs a newer OSDMap that records its `up_thru` epoch, peering enters `WaitUpThru`; otherwise earlier code posts `Activate`. `WaitUpThru` waits until map advancement clears `ps->need_up_thru`, then posts `Activate(ps->get_osdmap_epoch())`.

The remaining helpers support observability and recovery behavior:

- State entry and exit helpers feed the PG listener's peering history and record per-state event counts and time.
- The stream operator prints enough state to diagnose peering mismatches, deletion, past intervals, rollback bounds, commit/application lag, notify requirements, and prior-readable timing.
- `get_replica_recovery_order()` prioritizes shards with fewer missing objects first, while scheduling normal acting replicas before async recovery targets.

## Important APIs, Types, and Fields

- `PeeringState::GetMissing` is a Boost.Statechart state under `Peering`. In this chunk it reports no unfound availability for `QueryUnfound`, records `rs_getmissing_latency` on exit, and clears `ps->blocked_by`.
- `PeeringState::WaitUpThru` is another `Peering` substate. It is entered when `need_up_thru` prevents activation after missing-set collection.
- `ActMap` is the event indicating an OSDMap activation/advance. `WaitUpThru::react(const ActMap&)` checks the already-updated `ps->need_up_thru` flag and posts `Activate` once the map has the required `up_thru`.
- `MLogRec` carries `MOSDPGLog` data from another shard. During `WaitUpThru`, the state still accepts missing/log information from peers and folds it into `peer_missing` and `peer_info`.
- `pg_missing_t::claim()` moves a received missing set into `ps->peer_missing[logevt.from]`.
- `pg_info_t` from `logevt.msg->info` is stored in `ps->peer_info` and passed through `ps->update_peer_info()`, keeping the peer-info map and derived peering state synchronized.
- `QueryState` and `QueryUnfound` dump admin-facing state. This chunk reports `WaitUpThru` with a human-readable comment and marks unfound availability as false.
- `PeeringMachine::log_enter()` and `log_exit()` delegate to the `PeeringListener` interface through `pl->log_state_enter()` and `pl->log_state_exit()`.
- `PGStateHistory state_history` backs `NamedState` and listener history dumps.
- `PeeringState` diagnostic formatting uses core fields including `info`, `up`, `acting`, `async_recovery_targets`, `backfill_targets`, `role`, `last_peering_reset`, `deleting`, `past_intervals`, `pg_committed_to`, `last_update_applied`, `pg_log`, `last_complete_ondisk`, `min_last_complete_ondisk`, `state`, `send_notify`, and `prior_readable_until_ub`.
- `get_replica_recovery_order()` depends on `get_acting_recovery_backfill()`, `get_primary()`, `get_peer_missing()`, `pg_missing_t::num_missing()`, and `is_async_recovery_target()`.

## Control Flow

`GetMissing::react(const QueryUnfound&)` simply emits `state = "GetMising"` and `available_might_have_unfound = false`, then consumes the query. The spelling of `"GetMising"` is present in the source string. `GetMissing::exit()` logs state exit through `PeeringMachine`, increments `rs_getmissing_latency` by the time spent in the state, and clears `blocked_by` because the missing-set wait is over.

`WaitUpThru` construction registers the named state `"Started/Primary/Peering/WaitUpThru"` and logs entry. On `ActMap`, it inspects `ps->need_up_thru`; if the flag has been cleared by map processing, it posts an `Activate` event for the current OSDMap epoch. It then forwards the `ActMap`, allowing outer states or other reactions to observe the map event as well.

If a peer log arrives while waiting for `up_thru`, `WaitUpThru::react(const MLogRec&)` does not transition. It records the sender's missing set and peer info, updates the peer-info bookkeeping, and discards the message event. This preserves useful peer state gathered during the wait instead of dropping it until peering restarts.

`WaitUpThru::react(const QueryState&)` emits a state object with `name`, `enter_time`, and the comment `"waiting for osdmap to reflect a new up_thru for this osd"`, then forwards the query. `WaitUpThru::react(const QueryUnfound&)` reports no unfound availability and discards the query. `WaitUpThru::exit()` logs the exit and increments `rs_waitupthru_latency`.

The state-machine logging helpers are called by `NamedState`-using state constructors and exits throughout `PeeringState.cc`. `log_exit()` computes wall-clock duration from `enter_time`, logs debug details including `event_count` and `event_time`, forwards those values to the listener, then resets the counters for the next state interval.

The stream operator builds a single `pg[...]` summary. It prints `up`, optionally separate `acting`, EC primary marker, async/backfill target sets, role and last-peering-reset, deletion state, past interval bounds, peered lag indicators, log/info mismatch warnings, log-bound mismatch warnings, rollback bound, on-disk completion lag, primary-only minimum completion, PG state string, pending notify marker, and prior-readable-until upper-bound details.

`get_replica_recovery_order()` walks `get_acting_recovery_backfill()`, skips the primary, asserts that every remaining shard has a `peer_missing` entry, and ignores shards with zero missing objects. Shards with missing objects are partitioned into normal replicas and async recovery targets. Each partition is sorted ascending by missing count, normal replicas are kept before async targets, and the returned vector contains only `pg_shard_t` values.

## State and Persistence Behavior

This chunk does not directly write object-store metadata, mutate PG info on disk, or append to the PG log. Its state changes are in-memory peering state-machine updates plus listener/performance accounting.

`GetMissing::exit()` clears `blocked_by`, which affects subsequent peering diagnostics and blocked-state reporting. It also updates peering perf counters through `pl->get_peering_perf().tinc(rs_getmissing_latency, dur)`.

`WaitUpThru::react(const MLogRec&)` mutates `peer_missing` and `peer_info` while waiting for the map. These fields are central to later activation and recovery calculations; they are not persisted by this function directly, but they influence activation decisions, missing-location tracking, and recovery scheduling once peering proceeds.

The `need_up_thru` flag is not cleared in this chunk. It is adjusted during map processing elsewhere, via `adjust_need_up_thru()`, after the OSDMap records a sufficient `up_thru` for this OSD. `WaitUpThru` only observes the flag and posts activation once it is false.

`PeeringMachine::log_enter()` and `log_exit()` update listener-owned state history and performance/trace records. In the concrete PG listener implementation, those records back PG peering diagnostics rather than PG durable object state.

`operator<<` is read-only but encodes several consistency expectations: `pg_log` head and tail should match `info.last_update` and `info.log_tail`; the in-memory log's first entry should be strictly beyond the log tail; `last_complete_ondisk` should normally match `info.last_complete`; and a primary has a tracked `min_last_complete_ondisk`.

`get_replica_recovery_order()` is read-only. Its ordering affects later recovery work selection but does not itself modify missing sets or recovery reservations.

## Dependencies and Integration Points

- Boost.Statechart drives state transitions and event reactions. This chunk uses `post_event()`, `forward_event()`, and `discard_event()`.
- `DECLARE_LOCALS`, `psdout`, and `dout_prefix` connect the code to Ceph's PG-specific debug logging infrastructure.
- `PeeringListener` is the abstraction behind `pl`; this chunk calls `log_state_enter()`, `log_state_exit()`, `get_peering_perf()`, and state-update methods used through `ps`.
- `osd_perf_counters` defines `rs_getmissing_latency` and `rs_waitupthru_latency`, making these state durations visible in OSD recovery-state performance counters.
- OSD map advancement is the external trigger for `WaitUpThru`: OSD code notices `get_need_up_thru()` and sends/report updates so a later map can satisfy the primary's `up_thru` requirement.
- `PrimaryLogPG` and backend recovery code consume `get_peer_missing()` and the result of `get_replica_recovery_order()` to decide which replicas need recovery and in what order.
- The stream operator is used anywhere `PeeringState` is printed to logs, admin dumps, or assertions, so its mismatch markers are a major integration point for debugging peering failures.
- `prior_readable_until_ub` links this formatter to the prior-readable logic maintained in `pg_history_t` and consumed by read-serving paths before activation clears or expires the bound.

## Risks

- `WaitUpThru::react(const ActMap&)` assumes map handling has already correctly updated `need_up_thru`. If that flag is stale, activation can be delayed indefinitely or posted too early.
- `WaitUpThru::react(const MLogRec&)` trusts the message sender key and overwrites `peer_missing[logevt.from]` and `peer_info[logevt.from]`. Incorrect filtering before this point could pollute peering state with irrelevant or stale peer data.
- `get_replica_recovery_order()` asserts that every non-primary shard in `acting_recovery_backfill` has a `peer_missing` entry. Missing setup of `peer_missing` turns into an assertion failure instead of graceful recovery ordering.
- The sort comparator only compares missing counts. Equal-count shards have no explicit deterministic tie-breaker; `std::sort` may reorder equal elements in an implementation-dependent way.
- The explicit partitioning means async recovery targets are always ordered after normal replicas, even if an async target has fewer missing objects. That matches the comment, but it can delay quick async repairs.
- Diagnostic output in `operator<<` dereferences the first and last PG log entries when the log is non-empty. The surrounding empty check protects normal cases, but malformed log containers would make this path sensitive.
- `QueryUnfound` for `GetMissing` emits `"GetMising"` with a typo. Any external consumer matching exact state strings may need to account for the existing misspelling.

## Test and Validation Signals

Focused validation should cover both state-machine behavior and diagnostic/recovery-order side effects:

- A peering-state unit test should enter `WaitUpThru` with `need_up_thru = true`, deliver an `ActMap`, and verify no activation is posted until map processing clears `need_up_thru`.
- A companion test should clear `need_up_thru`, deliver `ActMap`, and verify `Activate` is posted with the current OSDMap epoch.
- `MLogRec` handling in `WaitUpThru` should be tested by sending peer missing/info data and asserting that `peer_missing`, `peer_info`, and derived peer-info updates reflect the sender.
- Query tests should verify `WaitUpThru` dumps its state name, enter time, explanatory comment, and `available_might_have_unfound = false`.
- Perf-counter tests or log-history assertions should verify `GetMissing::exit()` increments `rs_getmissing_latency`, clears `blocked_by`, and that `WaitUpThru::exit()` increments `rs_waitupthru_latency`.
- Formatter tests should construct `PeeringState` values with mismatched `pg_log` head/tail, non-empty past intervals, deletion, notify, prior-readable bounds, and primary completion lag to ensure the expected diagnostic tokens appear.
- Recovery-order tests should cover normal replicas versus async recovery targets, zero-missing exclusion, ascending missing-count ordering within each partition, and assertion behavior when `peer_missing` lacks an acting recovery/backfill shard.
