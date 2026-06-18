# Research: sources/distributed-fs/ceph/src/osd/PeeringState.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006942`: lines 1-8193, `Docs/researches/chunks/subset-b-006942_research.md`
- `subset-b-006943`: lines 8194-8385, `Docs/researches/chunks/subset-b-006943_research.md`

## Chunk Research

### subset-b-006942: lines 1-8193

# sources/distributed-fs/ceph/src/osd/PeeringState.cc lines 1-8193

## Scope

This chunk covers almost all of Ceph OSD PG peering state implementation in `PepheringState.cc`, from includes through the `GetMissing` state `QueryState` handler. It excludes only the tail that starts at line 8194, including `GetMissing::react(QueryUnfound)`, `WaitUpThru`, `PeeringMachine` logging, stream output, and replica recovery ordering helpers.

The code implements the durable and in-memory state transitions that let a placement group notice OSDMap changes, exchange PG info/logs with peers, choose an acting set, activate primary or replica roles, drive recovery/backfill reservations, track unfound objects, publish stats, split/merge PG metadata, and delete local PG contents. The central abstractions are `PeeringState`, `PeeringListener`, `PeeringCtx`, `PeeringCtxWrapper`, `PGLog`, `pg_info_t`, `pg_missing_t`, `PastIntervals`, OSDMap-derived acting/up sets, and a Boost Statechart machine rooted in `PeeringMachine`.

## Purpose

`PeeringState` is the OSD-side state engine for one PG shard. It owns the local view of `pg_info_t`, `PGLog`, past intervals, peer info, missing sets, recovery sources, acting/backfill targets, and PG state bits. Its job is to determine whether the PG can safely become peered or active for a given OSDMap interval, and if so to establish which OSDs/shards form the writeable acting set and what each peer must recover or backfill.

The implementation handles both replicated and erasure-coded pools, including EC optimization behavior where non-primary shards may have sparse logs and partial-write last-complete metadata. It also has special handling for stretch pools, temporary acting-set changes through `pg_temp`, async recovery target selection, leases for replica reads, and PG split/merge operations.

Persistent state changes flow through `ObjectStore::Transaction` via `PeeringListener::prepare_write()` and `PGLog` log handlers. Network-visible side effects are buffered through peering contexts and sent as `MOSDPGNotify2`, `MOSDPGQuery2`, `MOSDPGInfo2`, `MOSDPGLog`, `MOSDPGTrim`, `MOSDPGLease`, reserve messages, and delete/remove messages.

## Important APIs, Types, and Functions

`BufferedRecoveryMessages` wraps a `PeeringCtx` message map while outgoing recovery messages are blocked across peering resets. It provides `send_notify()`, `send_query()`, and `send_info()` helpers that enqueue typed OSD messages instead of sending immediately.

`PGPool::update()` refreshes cached pool metadata from an `OSDMapRef`, including pool name and snapshot context. It skips missing pools because pool deletion can race PG-side work.

`PeeringState::PeeringState()` initializes the PG state object, stores listener/context/map references, initializes local `pg_info_t`, `PGLog`, feature masks, `MissingLoc`, and starts the state machine.

`start_handle()`, `begin_block_outgoing()`, `clear_blocked_outgoing()`, `end_block_outgoing()`, and `end_handle()` manage per-event peering context lifetimes and event latency accounting. Blocking replaces the active context with a `BufferedRecoveryMessages` instance so recovery-related messages can be delayed until the local store flush completes.

`check_recovery_sources()`, `purge_strays()`, `remove_down_peer_info()`, and `update_heartbeat_peers()` keep peer tracking consistent with OSD liveness. Strays receive `MOSDPGRemove` unless premerge or debug-no-purge is active; down OSDs are removed from info/missing/request maps.

`update_history()` merges incoming `pg_history_t`, refreshes lease/readability upper bounds, marks `dirty_info`, and clears `past_intervals` if the PG became clean after the interval history covered by those intervals.

`apply_pwlc()`, `update_peer_info()`, `consider_adjusting_pwlc()`, and `consider_rollback_pwlc()` implement partial-write last-complete handling for EC optimized pools. They propagate newer partial-write ranges, advance peer `last_update`/`last_complete` when safe, and roll pwlc state forward or backward when divergent log processing changes the authoritative head.

`proc_replica_notify()`, `proc_primary_info()`, `proc_master_log()`, and `proc_replica_log()` are the main peer data ingestion points. They validate stale/down senders, merge history, update `peer_info`, collect feature masks, process authoritative or replica logs, update `peer_missing`, and add peers to `might_have_unfound`.

`advance_map()`, `activate_map()`, `should_restart_peering()`, `start_peering_interval()`, and `on_new_interval()` respond to OSDMap changes. They update pool/map references, recalculate `up`, `acting`, primary identities, PG state bits, past intervals, feature masks, heartbeat stamps, lease bounds, and dirty flags. They decide whether to reset peering when the interval changes or the local OSD transitions up.

`init_primary_up_acting()` maps raw OSD vectors into `pg_shard_t` sets. For EC pools it derives shard ids from vector positions and handles `pg_temp` primary-first ordering so the chosen primary shard matches OSDMap semantics even when an OSD appears in multiple positions.

`check_past_interval_bounds()` validates that persisted `past_intervals` cover exactly the required range from last clean or pool creation through `same_interval_since`, bounded by the cluster OSDMap trim floor. It logs cluster errors and aborts on mismatches unless disabled by config.

`get_recovery_priority()`, `get_backfill_priority()`, `get_delete_priority()`, `set_force_recovery()`, and `set_force_backfill()` derive queue priorities and update forced recovery/backfill PG state bits. Priorities are clamped through pool `RECOVERY_PRIORITY` options and legacy bounds.

`schedule_renew_lease()`, `send_lease()`, `proc_lease()`, `proc_lease_ack()`, `proc_renew_lease()`, `recalc_readable_until()`, and `check_prior_readable_down_osds()` maintain Octopus-era read leases. Primary lease state is bounded by replica acknowledgements and prior readable intervals; replicas translate primary lease times through heartbeat clock-delta bounds.

`build_prior()` asks `PastIntervals` for the prior set of OSDs that may need probing. It supplies OSD liveness/lost-at status, sets `PG_STATE_DOWN` when required, updates `need_up_thru`, and tells the listener which OSDs are probe targets.

`find_best_info()`, `calculate_maxles_and_minlua()`, `select_replicated_primary()`, `calc_replicated_acting()`, `calc_replicated_acting_stretch()`, `calc_ec_acting()`, `recoverable()`, `choose_async_recovery_ec()`, `choose_async_recovery_replicated()`, and `choose_acting()` form the acting-set selection engine. They choose an authoritative log, primary, target acting set, backfill targets, acting-recovery-backfill set, and async recovery exclusions while respecting min_size, missing-loc recoverability, stretch bucket limits, EC shard rules, and `pg_temp` needs.

`search_for_missing()`, `discover_all_missing()`, and `build_might_have_unfound()` drive unfound-object discovery. They identify peers that might contain missing objects, send full-log queries where needed, update `MissingLoc`, and publish stats when the unfound count changes.

`activate()` is the central transition into peered/active work. It updates `last_epoch_started`, writes an `ActivateCommitted` callback into the transaction, initializes `last_complete`, recovery pointers, snap trimming, peer activation messages, missing maps, `MissingLoc`, `might_have_unfound`, and PG state bits. On primary it sends `MOSDPGInfo2` or `MOSDPGLog` to peers; on replica it calls listener activation hooks.

`share_pg_info()`, `fulfill_info()`, `fulfill_log()`, and `fulfill_query()` publish PG info/log state to peers in response to state changes or `MQuery` requests.

`merge_log()` and `rewind_divergent_log()` are thin wrappers around `PGLog` with a transaction-backed log handler. `append_log_entries_update_missing()`, `merge_new_log_entries()`, `add_log_entry()`, `append_log()`, `recover_got()`, `force_object_missing()`, and `pre_submit_op()` mutate logs and missing sets during normal writes, recovery, async recovery, repair, or divergence handling.

`try_mark_clean()` marks the PG clean only when the acting set is full-size, updates clean epochs, clears past intervals, handles pending merge readiness, shares PG info, publishes stats, and clears recovery state.

`split_into()` and `merge_from()` implement PG split/merge metadata transformation. They split/merge logs, pwlc, stats, histories, past intervals, backfill pointers, and dirty flags, while using OSDMap placement to initialize child up/acting state.

`update_calc_stats()` synthesizes degraded, misplaced, missing, unfound, copy count, availability, object-location, and scrub-related stats from local/peer missing sets, recovery/backfill state, and EC shard topology. `prepare_stats_for_publish()` applies state timestamps, unstable stats, stale/inconsistent flags, and returns an optional changed `pg_stat_t`.

`dump_peering_state()`, `query_unfound()`, and `QueryState` handlers produce JSON diagnostic output for `ceph pg query`-style introspection, including current state, probes, blocked-by OSDs, requested info/log/missing sets, unfound discovery, and recovery progress.

## State Machine Coverage

The file uses Boost Statechart with nested states and per-state latency counters. The covered states include:

- `Crashed`: aborts on invalid events.
- `Initial`: receives the first notify/info/log and branches to primary or stray handling.
- `Started`: common outer state; handles interval flush completion, OSDMap advancement, and basic queries.
- `Reset`: resets peering for a new interval, sends notify to primary if this shard is not primary, and transitions back into `Started`.
- `Start`: branches by role to `Primary` or `Stray`.
- `Primary`: common primary parent; handles replica notifies, forced recovery/backfill flags, scrub requests, and primary cleanup on exit.
- `Peering`: primary peering parent; tracks prior set, peering blocked details, map effects, and `need_up_thru`.
- `GetInfo`: probes prior-set OSDs for `pg_info_t`; rebuilds prior set when incoming history advances `last_epoch_started`.
- `GetLog`: runs `choose_acting()`, requests the authoritative log if not local, processes the master log, and repeats selection for EC sparse-log cases.
- `GetMissing`: requests logs/missing maps from acting-recovery-backfill peers and posts `Activate` or `NeedUpThru` when done.
- `Down`: marks the PG down when the prior set requires unavailable OSDs, and retries if new notify history can advance peering.
- `Incomplete`: marks the PG incomplete when no complete authoritative info/log can be found, and retries on new notify or min_size decrease.
- `WaitActingChange`: waits for monitor-applied `pg_temp` changes and resets if a wanted target goes down.
- `Active`: primary active parent; calls `activate()`, waits for all replicas to commit activation, renews leases, processes new map events, notifies, leases, trims, logs, and queries.
- `Activating`, `Recovered`, and `Clean`: represent activation completion, post-recovery/backfill rechecks, and fully clean state.
- `NotRecovering`, `WaitLocalRecoveryReserved`, `WaitRemoteRecoveryReserved`, and `Recovering`: manage primary-side recovery reservations, full checks, cancellation, unfound handling, and transition to backfill or recovered state.
- `NotBackfilling`, `WaitLocalBackfillReserved`, `WaitRemoteBackfillReserved`, and `Backfilling`: manage local and remote backfill reservations, retry delays, too-full handling, and completion.
- `ReplicaActive`, `RepNotRecovering`, `RepWaitRecoveryReserved`, `RepWaitBackfillReserved`, and `RepRecovering`: manage replica activation, lease acknowledgement, remote reservation grants/revokes, and incoming primary info/log updates.
- `Stray`: handles a non-acting/non-primary local shard, accepts info/log from the real primary, restarts backfill if instructed, or transitions to deletion if the pool is gone.
- `ToDelete`, `WaitDeleteReserved`, and `Deleting`: reserve local background I/O for deletion, roll forward/reset log state, mark deletion, and call listener removal work until complete.

## Control Flow

Normal map-driven peering begins when `advance_map()` receives a new `OSDMapRef` and constructs an `AdvMap` event. `Started` or `Reset` checks whether the interval changed through `PastIntervals::is_new_interval()` or a local down-to-up transition. A new interval runs `start_peering_interval()`, which records past intervals, resets PG state bits, clears primary state, recalculates role/up/acting, notifies the listener, and decides whether this shard should notify a primary.

On activation of the map, `Reset::react(ActMap)` sends a `pg_notify_t` to the primary if necessary and transitions to `Started`. `Start` then moves into `Primary` when this shard is primary, or `Stray` otherwise.

Primary peering proceeds through `GetInfo`, `GetLog`, and `GetMissing`. `GetInfo` builds a prior set from `past_intervals` and probes OSDs that might have relevant PG state. `GetLog` combines local and peer `pg_info_t` into `all_info`, selects an authoritative log, calculates a desired acting set, and may request `pg_temp` changes or mark the PG incomplete. If a remote log is authoritative, the primary asks for it, merges it, and may repeat selection for EC optimized non-primary sparse-log cases. `GetMissing` requests each relevant peer's missing map unless it can infer the peer is empty, non-contiguous and needs backfill, fully backfilled, or already up to date.

Acting-set selection prefers recoverability and data safety before preserving current mapping. For replicated pools, it selects a primary based on up primary eligibility and an approximate missing-object threshold; then it prefers up OSDs, current acting OSDs, and strays with sufficient log contiguity. Stretch pools use ancestor buckets and per-bucket caps to maximize barrier-bucket representation and include a mandatory member if configured. EC pools fill each shard position from up, acting, or stray shards that are complete enough for the authoritative log. After initial selection, async recovery can temporarily remove costly up shards from `want` if the remaining set is still above min_size and recoverable.

When all required logs/missing maps are available and `need_up_thru` is clear, `Activate` transitions into `Active` for primaries or `ReplicaActive` for replicas. `activate()` updates durable PG info/log state, queues a transaction commit callback, sends activation log/info messages to replicas, updates local views of peer missing maps, initializes `MissingLoc`, builds unfound probes if needed, and marks the PG activating. The primary waits until every member in `acting_recovery_backfill` has committed activation, including itself via `ActivateCommitted` and replicas via `MInfoRec`; then `all_activated_and_committed()` renews leases, calculates degraded state, and posts `AllReplicasActivated`.

Once active, recovery and backfill run through separate reservation submachines. Recovery first reserves local background I/O, then remote recovery slots through `MRecoveryReserve::REQUEST`, then enters `Recovering`. Backfill similarly reserves local and remote backfill slots with `MBackfillReserve`. Too-full, preemption, cancellation, unfound, and retry-delay events clear state bits, release reservations, schedule later events, and move back to non-recovering/non-backfilling states. Completion moves to `Recovered`, which may request a new acting change, re-add async recovery targets, or post `GoClean`.

Replica flow is mostly reactive. A replica or stray accepts `MOSDPGLog`/`MOSDPGInfo2` from the primary, merges/rewinds local log state, processes leases, activates with the primary's activation epoch, and sends an info acknowledgement containing lease ack and updated history after its activation transaction commits.

Deletion flow is entered from `Stray` when the pool is gone or external delete events. It reserves background I/O, rolls the log forward, clears pwlc, resets backfill state, marks local deletion, calls `on_removal()`, and repeatedly calls `do_delete_work()` until termination.

## State and Persistence Behavior

Durable PG metadata is stored through `info`, `past_intervals`, and `pg_log`. `write_if_dirty()` delegates persistence to `PeeringListener::prepare_write()` with dirty flags for normal and "big" info. It also records the last persisted OSDMap epoch and clears dirty markers after preparing the transaction.

`dirty_info` is set for changes to `pg_info_t` fields such as `history`, `last_update`, `last_complete`, `last_epoch_started`, `last_interval_started`, `last_backfill`, `purged_snaps`, stats, hit-set, pwlc, and state-dependent metadata. `dirty_big_info` is set for heavier metadata such as `past_intervals`, purged snaps, and history changes that affect persisted big info.

`past_intervals` persist the mapping history required to know which OSDs may have acknowledged writes. They are updated on new intervals, cleared when the PG becomes clean, validated against map trim lower bounds, and sometimes adopted or adjusted during PG merge.

`PGLog` persists the authoritative mutation log and missing map. This chunk calls into `PGLog` to merge remote logs, append new entries, rewind divergent entries, roll forward committed entries, trim safe entries, reset backfill/recovery pointers, split/merge logs, and update missing sets. Log trimming is bounded by `min_last_complete_ondisk`, `can_rollback_to`, and `pg_committed_to`, with special EC optimization clamps.

Peer state is mostly in-memory: `peer_info`, `peer_missing`, `peer_last_complete_ondisk`, `peer_activated`, request sets, `missing_loc`, `might_have_unfound`, `stray_set`, `peer_purged`, `blocked_by`, and reserve target sets. These are rebuilt on peering resets, map changes, and incoming peer messages, but they influence durable transitions such as activation, clean marking, and log trimming.

OSDMap-derived state includes `up`, `acting`, `upset`, `actingset`, `primary`, `up_primary`, role, feature masks, `last_require_osd_release`, and pool metadata. These values are recalculated on interval changes and used to set PG state flags such as `REMAPPED`, `ACTIVE`, `PEERED`, `CLEAN`, `DEGRADED`, `UNDERSIZED`, `DOWN`, `INCOMPLETE`, `PEERING`, `WAIT`, `LAGGY`, forced recovery/backfill, recovery/backfill wait/toofull/unfound, `PREMERGE`, `CREATING`, and `INCONSISTENT`.

Lease state is in-memory but fed by persisted history fields. `readable_until`, `readable_until_ub`, `prior_readable_until_ub`, `acting_readable_until_ub`, and `prior_readable_down_osds` prevent reads from being served across intervals until prior readable windows are safe or OSDs are dead.

Split/merge mutates both source and target PG state. Splits partition logs, reset complete pointers, copy history/purged snaps, initialize child up/acting, invalidate stats, and dirty both parent and child. Merges roll source and target logs forward, trim to heads, combine stats, merge logs, adjust histories and past-interval bounds, reset pwlc, and mark incomplete when any source/target was incomplete.

## Dependencies and Integration Points

The code depends directly on Ceph OSD domain types from `PeeringState.h`, `PGPeeringEvent.h`, `PGLog`, `OSDMap`, `pg_pool_t`, `pg_info_t`, `pg_history_t`, `PastIntervals`, `MissingLoc`, `pg_missing_t`, `pg_stat_t`, `object_stat_sum_t`, `pg_query_t`, and `pg_notify_t`.

`PeeringListener` is the main integration boundary to the owning PG/OSD implementation. This chunk calls listener methods to send cluster messages, update heartbeat peers, prepare writes, obtain log handlers, clear primary state, request/cancel background I/O reservations, publish stats, schedule events, flush or schedule async work, report cluster log messages, handle pool changes, mark merge readiness, notify PG creation, start recovery/backfill/removal hooks, check blocklisted watchers, and query store/recovery state.

Network integration uses OSD message classes: `MOSDPGRemove`, `MBackfillReserve`, `MRecoveryReserve`, `MOSDPGInfo2`, `MOSDPGTrim`, `MOSDPGLog`, `MOSDPGNotify2`, `MOSDPGQuery2`, `MOSDPGLease`, and `MOSDPGLeaseAck`. Query/notify/log/info messages carry PG history, past intervals, logs, missing maps, leases, and feature vectors between OSDs.

OSDMap and pool integration is pervasive. The code reads PG size/min_size, pool type, EC optimization flags, stretch settings, pending merge settings, removed snaps, OSD features, `up_thru`, OSD liveness/lost state, `pg_temp`, CRUSH ancestors, OSD full flags, and pool existence. It also requests `pg_temp` changes through listener queues when the desired acting set differs from the current acting set.

Store integration is through `ObjectStore::Transaction`, `PGLog::LogEntryHandler`, activation commit callbacks, and listener removal work. The peering machine queues `PGPeeringEvent` callbacks on commit so state transitions happen only after durable writes complete.

Monitoring and diagnostics integrate through `Formatter`, cluster logs, perf counters such as `rs_*_latency` and stats invalidation counters, `pg_stat_t` publishing, and state dumps used by PG query operations. Comments note that tests rely on specific degraded/misplaced debug messages in `update_calc_stats()`.

## Risks and Edge Cases

Past interval correctness is critical. `check_past_interval_bounds()` aborts on mismatched persisted bounds because missing a prior interval can lose knowledge of an OSD that may contain acknowledged writes. OSDMap trimming can force interval clearing/faking, which is explicitly handled but risky.

Authoritative-log selection is subtle, especially for EC optimized pools. Non-primary shards may have sparse logs, partial writes can advance `last_update` without all shards observing every entry, and `repeat_getlog` exists to avoid rolling back based on an incomplete sparse log. Bugs here can choose an unsafe master log or incorrectly discard valid partial writes.

`choose_acting()` has several paths where it requests `pg_temp` and returns false. Callers sometimes have comments noting unchecked return values. A failed re-selection while active, after async recovery, or during notify handling could leave `want_acting` or recovery target state stale until a later map/event.

Stretch acting selection balances primary/up preferences, mandatory buckets, bucket caps, and CRUSH ancestors. Incorrect ancestor lookup or heap ordering can leave a PG undersized even when alternatives exist, or violate stretch constraints after failures.

Lease handling depends on heartbeat clock-delta bounds and prior readable intervals. If prior readable down OSD tracking or lease ack minima are wrong, replicas could serve reads past a safe interval or primaries could resume reads too early.

Recovery and backfill reservations span local and remote state machines. Preemption, too-full revocation, cancellation, and feature-gated `RECOVERY_RESERVATION_2` behavior must release both local and remote reservations exactly once. Missing releases can starve recovery; premature releases can allow overcommit.

Stats calculation is complex and mixes exact and estimated data. It has special paths for recovery, backfill, undersized replicated pools, EC missing shards, object location counts, and negative object correction. Incorrect stats can mislead health, recovery scheduling, autoscaling, and stuck/inconsistent checks.

Activation has many side effects in one function: durable history updates, peer log messages, missing-map mutation, snap trim initialization, lease renewal, missing-loc setup, and state flags. Any partially ordered callback or transaction issue can cause peers to believe activation has happened before the primary has durable state.

Stray purging and deletion must not race premerge, pool deletion, or acting-set changes. The code avoids purging during premerge and clears request maps after purging, but stale peer info can still trigger additional peering or remove messages.

PG split/merge has many invariants around histories, past intervals, stats invalidation, backfill pointers, and pwlc. Merge has explicit fallback logic for placeholder histories and adjusted interval starts, indicating previous edge cases around missing or inconsistent histories.

Several assertions encode deep invariants: non-empty `acting_recovery_backfill`, matching log heads and info last_update, valid primary shard derivation, available peer info/missing entries, and proper interval bounds. These are valuable but mean malformed peering inputs can abort the OSD rather than return a recoverable error.

The covered chunk stops before `GetMissing::react(QueryUnfound)` and `WaitUpThru`, so any complete analysis of peering blocked on monitor `up_thru` updates must include the next chunk.

## Test Signals

Map interval tests should cover primary changes, acting/up changes, local down-to-up transitions, pool full flag transitions, OSDMap trim gaps, pool deletion, and PG split changes. Assertions should inspect PG state bits, `same_interval_since`, `past_intervals`, `send_notify`, role, and dirty flags.

Past interval tests should exercise empty required bounds, non-empty bounds, start/end mismatches, oldest-map trimming, last clean clearing, and cluster error/abort behavior.

Peer-info tests should cover duplicate notify suppression, stale notify from an OSD not up since send epoch, stray detection and purge, down peer removal, feature-mask intersection, history merging, and pwlc propagation from primary and non-primary shards.

Acting selection tests should cover replicated primary preference, forced authoritative primary due to approximate missing objects, incomplete up primary, backfill target selection, stray inclusion when unrestricted, `restrict_to_up_acting`, `pg_temp` clear/request behavior, unrecoverable missing-loc cases, async recovery removal, and oversized want eviction.

EC tests should cover shard-position selection, non-primary shard exclusion from authoritative log selection, sparse-log `repeat_getlog`, pwlc roll-forward/rollback, stats invalidation after partial writes, and trim clamps to `can_rollback_to`.

Stretch tests should cover bucket cap computation, mandatory member inclusion, ancestor heap ordering, too few buckets, more candidate OSDs than pool size, up-set sufficiency, and interaction with async recovery.

Activation tests should verify primary and replica activation separately: transaction commit callback, `last_epoch_started`, `pg_committed_to`, `last_complete`, missing stats, peer `MOSDPGInfo2` versus `MOSDPGLog` selection, backfill initialization, snap trim queue setup, lease send/ack, `peer_activated`, `blocked_by`, and transition to `ACTIVE` or `PEERED`.

Recovery/backfill reservation tests should cover local reservation defer, remote grant/reject/revoke, too-full retry, preemption with and without `RECOVERY_RESERVATION_2`, release ordering, forced priority changes, and transitions among wait/recovering/backfilling/not states.

Unfound tests should cover building `might_have_unfound` from past intervals and strays, skipping down/purged/empty peers, duplicate query suppression, adding source info, all-queried-or-lost detection, and immediate recovery kick when an active PG receives useful missing data.

Log tests should cover authoritative log merge, replica log processing, divergent rewind, append on primary and replica, async/backfill transaction-not-applied handling, repair `recover_got`, trim-to calculation, aggressive trim, duplicate op log sizing, and missing-loc rebuild after stats invalidating log entries.

Stats tests should cover clean, degraded, undersized, remapped, recovering, backfilling, EC missing shard, negative object count, scrub error inconsistent marking, publish timestamp updates, unstable stats combination, and no-change suppression in `prepare_stats_for_publish()`.

Split/merge tests should cover parent and child log partitioning, pwlc split, backfill restart, stats invalidation counters, child acting initialization, merge with missing sources, placeholder target histories, last merge metadata validation, past-interval start adjustment, and combined stats/log output.

Deletion tests should cover deleted pool transition from `Stray`, delete priority changes across full/nearfull OSD states, reservation acquisition, log roll-forward before removal, pwlc clearing, `on_removal()` transaction side effects, repeated `DeleteSome`, and perf counter decrement on interrupted deletion.

### subset-b-006943: lines 8194-8385

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
