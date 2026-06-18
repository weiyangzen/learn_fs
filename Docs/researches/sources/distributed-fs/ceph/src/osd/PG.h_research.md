# sources/distributed-fs/ceph/src/osd/PG.h

## Purpose
`PG.h` declares the abstract base class for Ceph OSD placement groups. It defines the contract between concrete PG implementations, `PeeringState`, scrubber code, OSD services, PG backends, recovery scheduling, request queues, snap trimming, collection split/merge, and admin/stat reporting. Concrete classes such as primary-log PGs provide object-operation specifics while this base class centralizes shared peering, lifecycle, state, and callback plumbing.

## Important APIs, Types, and Members
`PGRecoveryStats` records per-state enter/exit/event/time totals and can dump plain or formatted recovery-state statistics. `PG` derives from `DoutPrefixProvider`, `PeeringState::PeeringListener`, and `Scrub::PgScrubBeListener`. Key identity members are `pg_whoami`, `pg_id`, `coll`, `ch`, `pgmeta_oid`, and references to `pool` and `info` owned by `recovery_state`.

Public state/query APIs expose current state, OSDMap epoch/ref, pool, history, acting/up sets, role, primary, past intervals, EC metadata, scrub state, snap-trim counters, stats counters, heartbeat peers, and recovery/backfill flags. Initialization and persistence APIs include `init()`, `read_state()`, `peek_map_epoch()`, `read_info()`, `_has_removal_flag()`, `prepare_write()`, and `write_if_dirty()`.

The abstract surface for concrete PGs includes `split_colls()`, `plpg_on_role_change()`, `plpg_on_pool_change()`, `start_recovery_ops()`, `get_watchers()`, `do_request()`, `clear_cache()`, `get_cache_obj_count()`, `snap_trimmer()`, `do_command()`, cache-agent methods, `check_local()`, `_clear_recovery_state()`, `_split_into()`, `kick_snap_trim()`, `snap_trimmer_scrub_complete()`, `get_pgbackend()`, and `_range_available_for_scrub()`.

Protected members define wait queues for map, peered, readable, active, flush, scrub, cache-full, clean-to-primary-repair, unreadable/degraded/blocked objects, degraded callbacks, and on-disk waits. Recovery state includes `recovery_queued`, `recovery_ops_active`, `waiting_on_backfill`, backfill intervals, reservations, projected log, projected last update, and recovery-state machine. Backoff state, heartbeat peers/probes, snap trim queues, unstable stats, and publish stats are also declared here.

## Control Flow
The class lifecycle starts with construction, collection setup, and either new-PG `init()` or disk `read_state()`. OSD map changes enter through `handle_advance_map()` and `handle_activate_map()`, while state-machine events enter through `queue_peering_event()` and `do_peering_event()`. Activation callbacks (`on_activate`, `on_replica_activate`, `on_activate_committed`, `on_active_actmap`, `on_clean`, `on_active_exit`) coordinate waiters, recovery, snap trim, scrub, and backend state.

Requests enter concrete `do_request()` but are managed by shared discard, capability, wait, and requeue helpers. Recovery scheduling calls `queue_recovery()`, concrete `start_recovery_ops()`, `start_recovery_op()`, `finish_recovery_op()`, and `find_unfound()`. Scrub scheduling wraps `ScrubPgIF` calls and protects active-state transitions. Split and merge paths update `PeeringState`, snap mapper bits, collection state, and source PG metadata.

## State and Persistence
The header defines both durable and volatile PG state. Durable state is mediated through `PeeringState`, `PGLog`, `pg_info_t`, `PastIntervals`, the PG metadata object, collection layout, and snap mapper. Volatile state includes locks/refcounts, wait queues, projected log state, active recovery counts, backoffs, reservations, heartbeat peers, scrubber state, unpublished stat deltas, and agent/cache state. The class comments explicitly describe wait-list ordering because it is part of the correctness contract for request ordering.

## Dependencies and Integration Points
`PG.h` depends on Ceph mempool/intrusive pointer utilities, admin finishers, OSD and PG types, `SnapMapper`, sessions/backoffs, timers, `PGLog`, `OSDMap`, `PGBackend`, peering events/state, recovery and missing-location types, scrub interfaces, and manager perf metric types. It integrates with `OSDService`, `OSDShard`, `ObjectStore`, `PGBackend`, scrub backends, monitor/OSD messaging, op scheduling, and dynamic perf stats.

## Risks
This header exposes a large callback contract; concrete PGs must maintain invariants expected by `PeeringState`, scrubber, backend, and OSDService simultaneously. Many helpers require the PG lock, but the type system does not enforce it. Wait queue ordering is documented but easy to break when adding a new blocking condition. Public inline stats mutators clamp negative byte counts, which protects counters but can hide upstream accounting bugs. Abstract hooks make it possible for concrete implementations to forget to clear cache/recovery/scrub state on interval changes.

## Test Signals
Tests should verify concrete PG implementations satisfy all abstract hooks, lock assertions, peering listener callbacks, scrub listener callbacks, wait queue ordering, recovery counters, split/merge contracts, snap trim accounting, stats publication, byte reservation accounting for EC and replicated pools, and PGBackend delegation through `PGLogEntryHandler`. Compile-time coverage across feature flags (`PG_DEBUG_REFS`, `CEPH_DEBUG_MUTEX`, Crimson) is also important.
