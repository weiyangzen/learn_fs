# sources/distributed-fs/ceph/src/osd/PeeringState.h

## Purpose

`PeeringState.h` declares Ceph OSD placement-group peering state: the state machine, state data, listener interface, event types, and public API used by `PG`, `PrimaryLogPG`, recovery backends, and OSD control paths to move a PG from map changes through peering, activation, recovery, backfill, clean state, deletion, split, and merge. It is the header boundary for durable PG metadata (`pg_info_t`, `PastIntervals`, `PGLog`), transient interval state, peer information, lease/readability tracking, missing-object location, recovery reservations, and Boost.Statechart event dispatch.

The file is declaration-heavy; most behavior is implemented in `sources/distributed-fs/ceph/src/osd/PeeringState.cc`, while callers and integration surfaces are spread across `PG.cc`, `PG.h`, `PrimaryLogPG.cc`, `OSD.cc`, EC backend code, and scheduler code.

## Important Types and APIs

### `PGPool`

`PGPool` caches pool identity and `pg_pool_t` state for the current OSDMap epoch. It stores `cached_epoch`, pool `id`, pool `name`, pool `info`, and the pool default `SnapContext`. `update(OSDMapRef)` refreshes this cached view. `get_readable_interval(ConfigProxy&)` returns the pool read lease interval from `pool_opts_t::READ_LEASE_INTERVAL` or derives it from `osd_heartbeat_grace * osd_pool_default_read_lease_ratio`.

The `fmt::formatter<PGPool>` specialization formats pool id, name, and `pg_pool_t` info for logging.

### Message and Transaction Contexts

`BufferedRecoveryMessages` owns a `std::map<int, std::vector<MessageRef>>` or `MessageURef` under Crimson and buffers per-target OSD messages. It can merge another buffer with `accept_buffered_messages()` and exposes `send_osd_message()`, `send_notify()`, `send_query()`, and `send_info()` helpers.

`PeeringCtx` inherits `BufferedRecoveryMessages` and adds the `ObjectStore::Transaction` that accumulates on-disk peering mutations plus an optional heartbeat handle. It is non-copyable but movable.

`PeeringCtxWrapper` hides whether outgoing recovery messages should be written to the live `PeeringCtx` or a temporary buffer while a flush is pending. State-machine code uses the wrapper to send messages and append to the transaction without knowing whether message delivery is delayed.

### `HeartbeatStamps`

`HeartbeatStamps` is a refcounted, mutex-protected record of heartbeat clock skew bounds for a peer OSD. It tracks:

- `peer_clock_delta_lb` and `peer_clock_delta_ub`, lower and upper bounds for peer clock minus local clock.
- `up_from`, the highest peer `up_from` epoch observed.
- `sent_ping()`, `got_ping()`, and `got_ping_reply()` to exchange and update bound information.

The lease/readability logic depends on these clock bounds to translate remote readable deadlines into local time safely.

### `PeeringState::PeeringListener`

`PeeringListener` is the large callback interface implemented by `PG` (`PG.h` inherits it). It separates the pure peering state machine from side effects supplied by the owning PG/OSD:

- persistence preparation: `prepare_write()`, `rebuild_missing_set_with_deletes()`
- cluster messaging: `send_cluster_message()`, `send_pg_created()`
- lease and heartbeat scheduling: `get_mnow()`, `get_hb_stamps()`, `schedule_renew_lease()`, `queue_check_readable()`, `update_heartbeat_peers()`
- flush lifecycle: `try_flush_or_schedule_async()`, `start_flush_on_transaction()`, `on_flushed()`
- recovery reservations: local background IO and remote recovery reservation request/cancel/update callbacks
- activation and role notifications: `on_pool_change()`, `on_role_change()`, `on_change()`, `on_activate()`, `on_replica_activate()`, `on_activate_complete()`, `on_clean()`, `on_active_exit()`
- deletion and merge callbacks: `on_removal()`, `do_delete_work()`, merge readiness setters
- logging, perf counters, stats publishing, recovery-space accounting, and blocklist/watcher checks

This interface is the principal integration point and a major risk surface: many PeeringState transitions are only correct if listener callbacks have precise ordering and transaction semantics.

### Events

The header declares Boost.Statechart events for map changes, activation, querying, scrub requests, reservation outcomes, deletion, leases, recovery, backfill, and control flags. Explicit event structs include `QueryState`, `QueryUnfound`, `AdvMap`, `ActMap`, `Activate`, `ActivateCommitted`, `UnfoundBackfill`, `UnfoundRecovery`, and `RequestScrub`. Numerous `TrivialEvent(...)` declarations cover common state-machine signals such as `Initialize`, `GotInfo`, `NeedUpThru`, `Backfilled`, `MakePrimary`, `MakeStray`, `NeedActingChange`, `AllReplicasRecovered`, `DoRecovery`, `GoClean`, `IntervalFlush`, force recovery/backfill toggles, deletion reservation events, and `CheckReadable`.

Public event entrypoints are `handle_event(const boost::statechart::event_base&, PeeringCtx*)` and `handle_event(PGPeeringEventRef, PeeringCtx*)`; both call `start_handle()`, process the event through the Boost state machine, then call `end_handle()`.

### State Machine

`PeeringMachine` is `boost::statechart::state_machine<PeeringMachine, Initial>`. It carries pointers back to `PeeringState`, `PGStateHistory`, `CephContext`, the PG id, logging prefix provider, and listener. It also provides state methods access to the current transaction and recovery context.

The declared hierarchy is:

- `Initial`
- `Reset`
- `Started`
- `Start`
- primary side: `Primary`, `WaitActingChange`, `Peering`, `GetInfo`, `GetLog`, `GetMissing`, `WaitUpThru`, `Down`, `Incomplete`, `Active`, `Activating`, `Clean`, `Recovered`, `Backfilling`, `WaitRemoteBackfillReserved`, `WaitLocalBackfillReserved`, `NotBackfilling`, `NotRecovering`, `Recovering`, `WaitRemoteRecoveryReserved`, `WaitLocalRecoveryReserved`
- replica side: `ReplicaActive`, `RepNotRecovering`, `RepRecovering`, `RepWaitBackfillReserved`, `RepWaitRecoveryReserved`
- stray/delete side: `Stray`, `ToDelete`, `WaitDeleteReserved`, `Deleting`
- terminal failure: `Crashed`

Each nested state declares its accepted reactions and transitions. Examples: `GetInfo` requests peer info then transitions to `GetLog` on `GotInfo`; `GetLog` may transition to `WaitActingChange`, `Incomplete`, or repeat itself; `Peering` transitions to `Active` on `Activate`; `Active` handles map and message traffic while child states handle activation, recovery, backfill, and clean progression; `ReplicaActive` handles primary queries, lease messages, and remote reservation events; `ToDelete` and children drive incremental PG removal.

## Core State and Persistence Behavior

The class stores both durable PG state and transient interval state.

Durable or persisted-through-listener fields include:

- `info` and `last_written_info` (`pg_info_t`)
- `past_intervals`
- `pg_log`
- dirty flags `dirty_info` and `dirty_big_info`
- `last_persisted_osdmap`
- history embedded in `info.history`, including prior readable upper bound state

`write_if_dirty(ObjectStore::Transaction&)` asks the listener to prepare writes when dirty state exists. `force_write_state()` marks both info forms dirty and writes them. `reset_last_persisted()` resets persisted map tracking and marks both dirty. `init_from_disk_state()` hydrates `info`, `last_written_info`, `past_intervals`, and `PGLog` from disk and then logs suspicious conditions.

Transient peering fields include current role, `state` bits (`PG_STATE_*`), current and up primary, `up`, `acting`, set forms, `acting_recovery_backfill`, `stray_set`, `peer_info`, `peer_missing`, peer feature intersections, target sets for backfill and async recovery, missing-object location, reservation flags, delete flags, and flush/message-buffering state.

Flush behavior is explicit: `start_flush()` increments `flushes_in_progress` and registers transaction commit callbacks through the listener; `needs_flush()` blocks activation-sensitive behavior until `complete_flush()` drains the counter; `begin_block_outgoing()`, `end_block_outgoing()`, and `messages_pending_flush` allow recovery messages to be buffered until durable state is flushed.

Version pointers are central to correctness:

- `pg_committed_to` marks versions committed on all replicas during active primary service.
- `last_complete_ondisk` is the committed local `last_complete`.
- `last_update_applied` is the last locally readable update.
- `last_rollback_info_trimmed_to_applied` tracks rollback-info trim application.
- `min_last_complete_ondisk` and `pg_trim_to` bound log trimming.

APIs such as `complete_write()`, `local_write_applied()`, `update_last_complete_ondisk()`, `recovery_committed_to()`, `append_log_entries_update_missing()`, `append_log()`, and `merge_new_log_entries()` update these invariants with `PGLog` and missing-set changes.

## Control Flow

Map updates enter via `advance_map()`, which processes an `AdvMap` event with the new OSDMap, previous map, up/acting vectors, and primary ids. `activate_map()` processes `ActMap`. The state machine may restart peering based on `should_restart_peering()`, initialize interval data through `start_peering_interval()`, and notify listener hooks via `on_new_interval()`.

Primary peering generally flows as:

1. `Initial` receives `Initialize` and enters `Reset`.
2. `Reset` handles map activation and role calculation.
3. `Started/Start` transitions to `Primary` or `Stray`.
4. `Primary/Peering/GetInfo` gathers peer `pg_info_t` via notify/query traffic.
5. `GetLog` chooses an authoritative log shard, requests/merges logs, and may request an acting-set change or mark the PG incomplete.
6. `GetMissing` obtains peer missing sets.
7. `WaitUpThru` waits for an OSDMap that proves the primary is up-through the needed epoch.
8. `Activate` enters `Active`, where `Activating` either reaches `Recovered`, starts recovery, or requests backfill.
9. Recovery/backfill reservation states coordinate local and remote reservations before `Recovering` or `Backfilling`.
10. `Recovered` transitions to `Clean` when all replicas are activated and clean conditions hold.

Replica flow enters `ReplicaActive`, responds to `MQuery`, `MInfoRec`, `MLogRec`, trims, activation events, and lease messages, and uses `RepWaitRecoveryReserved`/`RepWaitBackfillReserved` to serve primary-driven reservations.

Stray flow handles queries/log/info until it is told to delete. `ToDelete` requests deletion reservation, `Deleting` repeatedly calls listener deletion work through `DeleteSome`, and may be interrupted back to `WaitDeleteReserved`.

## Acting-Set, Recovery, and Missing-Object Algorithms

The header declares the algorithmic helpers used by the implementation:

- `build_prior()` constructs the prior set from past intervals.
- `calculate_maxles_and_minlua()` and `find_best_info()` choose the best authoritative history/log candidate.
- `calc_ec_acting()`, `select_replicated_primary()`, `calc_replicated_acting()`, and `calc_replicated_acting_stretch()` compute desired acting/backfill sets for EC, replicated, and stretch pools.
- `choose_acting()` coordinates acting-set selection and may request pg_temp changes through `want_acting`.
- `choose_async_recovery_ec()` and `choose_async_recovery_replicated()` identify async recovery targets.
- `recoverable()` tests whether the desired set can proceed.
- `search_for_missing()`, `discover_all_missing()`, `build_might_have_unfound()`, and `all_unfound_are_queried_or_lost()` manage unfound-object discovery.

Missing-object state is bridged through inheritance from `MissingLoc::MappingInfo`, `missing_loc`, local `PGLog::get_missing()`, and per-peer `peer_missing`. Public accessors expose missing counts, unfound state, and missing-location maps to recovery and user-facing query paths.

## Leases and Readability

The file includes detailed read-lease state:

- `readable_interval`
- `readable_until`
- `readable_until_ub`
- `prior_readable_until_ub`
- `prior_readable_down_osds`
- replica-side `readable_until_ub_from_primary`
- primary-side `readable_until_ub_sent`
- per-acting `acting_readable_until_ub`

`renew_lease()`, `send_lease()`, `schedule_renew_lease()`, `get_lease()`, `proc_lease()`, `proc_lease_ack()`, `proc_renew_lease()`, `get_lease_ack()`, and `recalc_readable_until()` maintain primary/replica lease propagation. `can_serve_read()` combines object missing state and readability predicates. `clear_prior_readable_until_ub()` resets inherited prior-interval readability once it expires or is no longer relevant.

This code path relies on `HeartbeatStamps` skew bounds and OSDMap liveness; errors here risk stale reads across peering intervals.

## Split, Merge, Stats, and Maintenance APIs

`start_split_stats()`, `finish_split_stats()`, and `split_into()` support PG splitting. `merge_from()` merges source PG state into a target and integrates with merge readiness callbacks in the listener.

Stats APIs include `update_stats()`, `update_stats_wo_resched()`, `prepare_stats_for_publish()`, `apply_op_stats()`, backfill stats updates, snap trimming state via `adjust_purged_snaps()`, hit-set updates, blocked-by accounting, and stat invalidation tracking.

Recovery and backfill maintenance APIs include `recover_got()`, `on_peer_recover()`, `begin_peer_recover()`, `object_recovered()`, `update_backfill_progress()`, `update_complete_backfill_object_stats()`, `update_peer_last_backfill()`, `force_object_missing()`, `prepare_backfill_for_missing()`, and `set_revert_with_targets()`.

## Dependencies and Integration Points

Direct dependencies include Boost.Statechart, Ceph context/config types, `PGLog`, `PGStateUtils`, `PGPeeringEvent`, OSD types, `ObjectStore`, `OSDMap`, `MissingLoc`, message refs, mutex/refcount helpers, and snap types.

Important integration points observed from cross-references:

- `PeeringState.cc` implements the declared state machine and algorithms.
- `PG.h` implements `PeeringListener` and owns a `PeeringState recovery_state`.
- `PG.cc` drives initialization, query state, map activation, interval flush, heartbeat stamps, and unfound events.
- `PrimaryLogPG.cc` posts recovery/backfill/clean events and queries unfound state.
- `OSD.cc` posts admin/control events such as scrub, delete, forced recovery/backfill, and check-readable events.
- `ECBackend.cc`, `ECBackendL.cc`, `ECCommon.h`, and `ECCommonL.h` coordinate with `pg_committed_to` and log submission behavior.
- `scheduler/OpSchedulerItem.h` interprets `recovery_msg_priority_t` values for recovery message scheduling.
- `OSDService::get_hb_stamps()` creates `HeartbeatStamps` instances shared by sessions and PG peering.

## Risks and Edge Cases

- The state machine has many nested transitions and catch-all crash transitions; adding events without understanding parent-state reactions can silently discard, defer, or crash unexpected traffic.
- `PeeringListener` side effects must be transactionally aligned with state changes. Incorrect `prepare_write()`, flush, or commit callback behavior can expose messages before durable state is safe.
- Lease/readability logic depends on conservative clock-skew bounds. Incorrect heartbeat stamp updates or prior interval handling can produce stale reads.
- Acting-set selection has separate replicated, EC, and stretch-pool paths. A change in one path can violate min_size, locality, or backfill-target assumptions in another.
- `peer_info`, `peer_missing`, `peer_purged`, `peer_activated`, and stray deletion state defend against races with old maps and old replicas; cleanup changes can reintroduce stale peer data.
- `pg_committed_to`, `last_complete_ondisk`, `last_update_applied`, and trim boundaries are tightly coupled to PGLog mutation. Advancing any pointer too early risks data loss or divergent reads; advancing too late can stall trim/recovery.
- Message buffering during flush is easy to break because `PeeringCtxWrapper` intentionally hides whether messages are immediate or pending.
- Crimson/classic build differences affect message reference types; helpers must remain templated or conditional where the header already abstracts them.
- `deleting` and atomic `deleted` are queried by peering reset logic; races with shutdown/deletion events can make a PG appear reset to older events.

## Test Signals

Useful validation signals for changes touching this header or its contracts:

- Unit or integration tests that drive PG map changes through `PG::handle_advance_map()`, initialization, `Initialize`, `AdvMap`, and `ActMap` paths.
- Peering tests that cover primary election, `GetInfo`, `GetLog`, incomplete PGs, acting-set changes, and `NeedUpThru`.
- Recovery/backfill tests that observe transitions through local/remote reservation states, too-full rejections, preemption, and completion events.
- Read lease tests or simulations that validate `send_lease()`, `proc_lease()`, `proc_lease_ack()`, `CheckReadable`, and prior-readable interval expiry under skewed heartbeat timestamps.
- Log divergence and missing-object tests covering `proc_master_log()`, `proc_replica_log()`, `append_log_entries_update_missing()`, `discover_all_missing()`, and unfound queries.
- Split/merge tests that validate `split_into()`, `merge_from()`, stats transfer, and merge readiness callbacks.
- Delete-path tests that drive `DeleteStart`, reservation, repeated `DeleteSome`, interruption, and final removal transaction behavior.
- Scheduler or recovery-message priority checks for both mclock and weighted-priority queue configurations, especially forced recovery/backfill, degraded, undersized, and best-effort cases.

## Research Notes

This research read the complete `PeeringState.h` source file and cross-referenced implementation/call sites with repository search. The final artifact is source-tree-aligned at `Docs/researches/sources/distributed-fs/ceph/src/osd/PeeringState.h_research.md`.
