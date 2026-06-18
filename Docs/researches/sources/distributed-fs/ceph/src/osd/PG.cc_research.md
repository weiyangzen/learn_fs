# sources/distributed-fs/ceph/src/osd/PG.cc

## Purpose
`PG.cc` implements the common placement-group base behavior shared by concrete PG types. It manages PG locking and intrusive lifetime, logging prefixes, snap mapping, primary-state cleanup, capability checks, recovery queueing/completion, split/merge bookkeeping, client backoff messages, heartbeat peer sets, persistent PG metadata reads/writes/upgrades, snap trim queues, op requeue ordering, scrub event forwarding, backfill space reservation, stale-message discard rules, peering-event dispatch, deletion work, stats publishing, and small OSD-service callbacks.

## Important APIs and Functions
Lifetime and locking are implemented by `get()`, `put()`, debug ref helpers, `lock()`, `unlock()`, `is_locked()`, the constructor/destructor, and `PGLockWrapper`. `gen_prefix()`, `get_peering_perf()`, `get_perf_logger()`, and recovery-state logging integrate with diagnostics.

Snap and object metadata helpers are `remove_snap_mapped_object()`, `clear_object_snap_mapping()`, `update_object_snap_mapping()`, `update_snap_map()`, and `filter_snapc()`. Primary and recovery state helpers include `clear_primary_state()`, `queue_recovery()`, `finish_recovery()`, `_finish_recovery()`, `start_recovery_op()`, `finish_recovery_op()`, `clear_recovery_state()`, `cancel_recovery()`, `on_new_interval()`, `on_clean()`, `on_active_exit()`, and reservation callbacks.

Split/merge and deletion helpers include `split_into()`, `start_split_stats()`, `finish_split_stats()`, `merge_from()`, `do_delete_work()`, and `C_DeleteMore::complete()`. Backoff management is handled by `add_backoff()`, `release_backoffs()`, `clear_backoffs()`, and `rm_backoff()`. Persistent state code includes `init()`, `read_state()`, `read_info()`, `peek_map_epoch()`, `_has_removal_flag()`, `upgrade()`, and `prepare_write()`.

Request control includes `op_has_sufficient_caps()`, `requeue_op()`, `requeue_ops()`, `requeue_map_waiters()`, `can_discard_op()`, `can_discard_replica_op()`, `can_discard_scan()`, `can_discard_backfill()`, and `can_discard_request()`. Peering and map transitions are handled by `do_peering_event()`, `queue_peering_event()`, `queue_null()`, `find_unfound()`, `handle_advance_map()`, `handle_activate_map()`, `handle_initialize()`, and `handle_query_state()`.

Scrub methods include `start_scrubbing()`, `on_scrub_schedule_input_change()`, `scrub_requested()`, `replica_scrub()` overloads, `forward_scrub_event()` overloads, priority helpers, and scrub-state wait checks. Stats and heartbeat helpers include `publish_stats_to_osd()`, `with_pg_stats()`, `dump_pgstate_history()`, `dump_missing()`, `pg_stat_adjust()`, `with_heartbeat_peers()`, and heartbeat peer/probe updates.

## Control Flow
PGs are constructed with an OSD service, current map, pool, and `spg_t`, then initialized either from new placement data (`init()`) or from disk (`read_state()`). Disk load reads omap keys, decodes `pg_info_t`, `PastIntervals`, purged snaps, fast info, and the PG log/missing set, upgrades if needed, initializes current up/acting/role from the OSDMap, sets collection options, injects an initialize peering event, and persists any dirty state.

Map changes flow through `handle_advance_map()` and `handle_activate_map()`, delegating state-machine work to `PeeringState`, updating the OSD shard epoch, requeueing map waiters, and refreshing scrub schedules if pool settings changed. Peering events are filtered by `old_peering_evt()` and then passed to `recovery_state.handle_event()`, followed by `write_if_dirty()` so state changes are captured.

Client and replica requests may block on ordered wait queues. `requeue_ops()` preserves request ordering by pushing waitlists back in reverse order, and it may divert ops to `waiting_for_readable` if readability is still blocked. `can_discard_request()` rejects stale messages based on same-primary/same-interval epochs, force-op-resend epochs, split epochs, down OSDs in the next map, and peering reset epochs.

Recovery control queues primary PGs only when primary and peered. Recovery completion clears recovery state, waits for sync, purges strays, publishes stats, and notifies the scrubber. Backfill reservation estimates required bytes, adjusts EC pools by data chunk count and stripe size, checks full/backfill-full policy under `OSDService::stat_lock`, and records primary/local byte reservations for stats adjustment.

Deletion scans collection objects in bounded batches, removes snap mapper entries and objects, schedules more delete work on commit, and finally clears PG info/log, removes the collection, flushes, and asks the OSD to finish deletion or reinstantiates if racing with merge.

## State and Persistence
Runtime state includes the lock/refcount, OSD pointers, collection handle, `PeeringState`, snap mapper, scrubber, wait queues, backoffs, recovery counters, heartbeat peers/probes, backfill reservation bytes, projected log/update state, unstable/publish stats, snap trim queues, and deletion sleep flag. Persistent PG state is stored in the PG metadata object omap: info version, info, big info/past intervals/purged snaps, fast info, PG log, and missing set. Object snap mappings are persisted through `SnapMapper` in the object store transaction. Collection operations persist split, merge, delete, and rollback cleanup effects.

## Dependencies and Integration Points
`PG.cc` depends on `OSD`, `OSDService`, `PeeringState`, `PGLog`, `PGBackend`, `SnapMapper`, `ObjectStore`, `ScrubPgIF`, session/capability objects, many OSD message classes, timers/reservers, op scheduler items, and perf counters. It is the glue between map advancement, peering, backend IO/recovery, scrub scheduling, client request gating, monitor/OSD service callbacks, and durable object-store metadata.

## Risks
The class relies heavily on holding `_lock`; several methods assert lock ownership or assume serialized PG event execution. Request ordering is fragile because many wait queues interact. Backoff release races with session reset and new backoffs, requiring lock ordering between `backoff_lock` and `Backoff::lock`. Recovery counters must stay balanced, especially when clearing recovery or suspending backfill. Persistent writes combine info, log, missing, and snap mapper updates; missed dirty writes can corrupt peering state. Deletion must handle objects appearing during removal and races with merge. In debug-ref code, the shown `put_with_id()` deletes when `newref` is nonzero, which is suspicious and should be verified against build configuration and tests.

## Test Signals
Tests should cover read/write of PG state, prepare-write omap keys, map advancement and peering event filtering, request discard decisions across map epochs/features, wait-queue requeue order, snap mapper updates/removals, split/merge state transfer, backoff add/release/session reset, recovery queue and completion, backfill reservation/full checks, scrub event forwarding on active/inactive PGs, deletion batches, stats publishing, and heartbeat peer updates.
