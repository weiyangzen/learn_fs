# sources/distributed-fs/ceph/src/osd/OSD.cc - chunk subset-b-006937

Line range researched: `sources/distributed-fs/ceph/src/osd/OSD.cc` lines 8469-11888.

## Purpose

This chunk covers the middle-to-late OSD control plane for map commit and publication, placement group split/merge progression, peering event dispatch, recovery throttling, operation queue scheduling, dynamic configuration handling, performance-query reporting, OSD shard slot bookkeeping, mClock capacity benchmarking support, and a small heap-profiler admin command.

The code forms a bridge between persisted monitor state (`OSDMap`, superblock, pg_num history, purged snap records), in-memory OSD service state (`OSDService`, reservations, caches, heartbeat peers), per-PG state machines (`PG`, `PeeringState`, `PeeringCtx`), and the sharded operation work queue (`OSDShard`, `ShardedOpWQ`). The main operational pattern is: receive or commit a newer map, publish it through `OSDService`, prime PG split/merge slots, queue peering events, then let shard worker threads serialize operation and peering execution by `spg_t` ordering token.

## Important APIs, Types, and Functions

### OSDMap commit and PG-number history

- The opening block finalizes persisted OSD map state: updates `superblock.current_epoch`, `mounted`, and `clean_thru`; serializes `pg_num_history` into the meta collection; records purged snaps with `SnapMapper::record_purged_snaps()` when `superblock.purged_snaps_last == start - 1`; writes the superblock; registers `C_OnMapCommit`; queues the meta transaction; and publishes the superblock through `OSDService`.
- `OSD::track_pools_and_pg_num_changes()` walks newly added maps in order, comparing each map against the prior map and updating `pg_num_history.epoch`.
- `OSD::_track_pools_and_pg_num_changes()` records three map-derived events:
  - pool deletion via `pg_num_history.log_pool_delete()`, plus a final encoded `pg_pool_t`, pool name, and erasure-code profile written under `make_final_pool_info_oid(pool_id)`;
  - `pg_num` changes for existing pools via `log_pg_num_change()`;
  - pool creation by logging the new pool's initial `pg_num`.

### OSDMap advancement and publication

- `OSD::_committed_osd_maps()` is the on-commit callback path for new OSD maps. It locks `osd_lock`, then `map_lock`, advances from `first` through `last`, calls `service.pre_publish_map()`, handles OSD up/down transitions, updates boot/up epochs, and changes local OSD state from booting to active when the map matches the daemon's addresses.
- The same function checks whether the new map says this OSD no longer exists, is administratively stopped, is down, or has mismatched client, cluster, or heartbeat addresses. It may queue asynchronous shutdown, restart boot, mark itself dead to monitors on newer clusters, rebind the cluster messenger, mark heartbeat messengers down, and reset heartbeat peers.
- `OSD::check_osdmap_features()` adjusts messenger policy `features_required` masks for clients, monitors, and OSD peers based on the CRUSH/OSDMap feature sets; enables the on-disk `CEPH_OSD_FEATURE_INCOMPAT_SHARDS` incompat feature if missing; toggles heartbeat authorizer requirements around the Nautilus release boundary; and persists `require_osd_release` metadata.
- `OSD::consume_map()` publishes the current map to the service, primes pending splits and merges across shards, prunes ready-to-merge and pg-created state, advances each shard's map view, prunes pending creates that no longer map here, dispatches sessions waiting on maps, releases no-longer-needed reserved recovery pushes, queues `NullEvt` peering events for all PGs, and refreshes PG counters.
- `OSD::activate_map()` maps the `CEPH_OSDMAP_NORECOVER` flag into recovery pause/unpause state and calls `service.activate_map()`.

### Split and merge mechanics

- `C_FinishSplits` invokes `OSD::_finish_splits()` after a split transaction applies. `_finish_splits()` initializes split child PGs, queues a null event at their current map epoch, dispatches resulting peering context, unlocks, then registers and wakes each child on its target shard.
- `OSD::add_merge_waiter()` records merge source PG references in `merge_waiters[nextmap_epoch][target]` under `merge_lock` and returns whether all expected sources are present.
- `OSD::advance_pg()` advances a locked PG from its current map epoch to an OSD epoch. It detects PG merge sources and targets during `pg_num` decreases, handles merge source shutdown/detach and merge target readiness, calls `PG::handle_advance_map()`, detects `pg_num` increases, calls `split_pgs()`, and finally calls `PG::handle_activate_map()`.
- `OSD::split_pgs()` creates child PGs with `_make_pg()`, creates new collections, assigns collection commit queues, splits parent collections and PG memory state, initializes pool options, transfers per-child stats, and finalizes parent split stats in the provided transaction.
- `OSDShard::identify_splits_and_merges()`, `prime_splits()`, `_prime_splits()`, `prime_merges()`, `register_and_wake_split_child()`, and `unprime_split_children()` maintain shard-local `OSDShardPGSlot` state for split/merge participants that may not yet have an attached `PG`.

### Peering and message dispatch

- `OSD::dispatch_context()` sends queued peer messages from `PeeringCtx::message_map` only when the local OSD is up and active, shares maps before sends, and queues any non-empty peering transaction on the PG collection handle.
- Peer/source validation helpers `require_mon_peer()`, `require_mon_or_mgr_peer()`, and `require_osd_peer()` reject messages from inappropriate connection roles.
- Fast peering handlers convert messages into `PGPeeringEvent`s:
  - `handle_fast_pg_create()` accepts monitor-created PGs, validates supplemental history/past intervals, and queues `PgCreateEvt` with `PGCreateInfo`.
  - `handle_fast_pg_notify()` maps `MOSDPGNotify` records to `MNotifyRec` events and may carry `PGCreateInfo`.
  - `handle_fast_pg_info()` maps `MOSDPGInfo` entries to `MInfoRec`.
  - `handle_fast_pg_remove()` maps remove requests to `PeeringState::DeleteStart`.
  - `handle_fast_force_recovery()` maps monitor/manager force recovery or backfill commands to `Set/UnsetForceRecovery` and `Set/UnsetForceBackfill`.
- `OSD::handle_pg_query_nopg()` answers log/full-log or notify-style queries for PGs that do not exist locally, as long as the pool still exists.
- `OSDService::queue_check_readable()` either immediately queues `PeeringState::CheckReadable` or schedules it on `mono_timer`.

### Recovery throttle and operation dispatch

- `OSDService::_maybe_queue_recovery()` drains `awaiting_throttle` while `_recover_now()` permits work, reserves up to `osd_recovery_max_single_start` pushes, and queues PGs for recovery.
- `OSDService::_recover_now()` gates recovery on `defer_recovery_until`, `recovery_paused`, and the sum of active plus reserved recovery operations against `osd->get_recovery_max_active()`.
- `OSDService::get_target_pg_log_entries()` computes an even per-PG log target from `osd_target_pg_log_entries_per_osd`, clamped between `osd_min_pg_log_entries` and `osd_max_pg_log_entries`.
- `OSD::do_recovery()` enforces configurable recovery sleep, starts recovery ops through `PG::start_recovery_ops()`, optionally searches for unfound objects with `PG::find_unfound()`, dispatches any context, and releases reserved pushes.
- `OSDService::start_recovery_op()`, `finish_recovery_op()`, `is_recovery_active()`, and `release_reserved_pushes()` maintain active/reserved recovery counters and wake additional recovery work.
- `OSD::enqueue_op()` wraps client/recovery messages in `PGOpItem` or `PGRecoveryMsg`, records tracing and latency metrics, and enqueues into `op_shardedwq`.
- `OSD::enqueue_peering_evt()` wraps `PGPeeringItem` with peering priority.
- `OSD::dequeue_op()` shares maps, skips deleting PGs, marks the op as reached, and delegates to `PG::do_request()`.
- `OSD::dequeue_peering_evt()` handles PG-less queries, advances the PG to the shard map, runs the peering event, dispatches context, handles `need_up_thru`, and sends `pg_temp`.
- `OSD::dequeue_delete()` synthesizes a `DeleteSome` peering event.

### Dynamic configuration, QoS, and perf metrics

- `OSD::get_tracked_keys()` lists OSD config keys for runtime change handling, including recovery, backfill, op tracking, log routing, map cache, sleep knobs, heartbeat, scrub, and thread timeout keys.
- `OSD::handle_conf_change()` maps changed keys into subsystem updates: recovery/backfill reservations, mClock overrides, sleep overrides, scrub reservations and intervals, op tracker thresholds, map cache sizes, log config, FUSE toggling, recovery deferral, client throttler caps, clean-region limits, ASIO thread pool restart, and op work-queue timeouts.
- `OSD::maybe_override_max_osd_capacity_for_qos()` runs `OSDBenchTest` for mClock deployments unless skipped or a non-default configured capacity is present, validates the measured IOPS against HDD/SSD thresholds, and persists the result via monitor config when acceptable.
- `OSD::maybe_override_options_for_qos()` applies mClock defaults for recovery/backfill settings at boot, or rejects runtime recovery/backfill changes unless `osd_mclock_override_recovery_settings` is enabled. Rejections remove config keys from monitor config and emit cluster warnings.
- `OSD::maybe_override_sleep_options_for_qos()` disables recovery, degraded recovery, delete, snap trim, and scrub sleeps when mClock scheduling is active.
- `MonCmdSetConfigOnFinish` and `OSD::mon_cmd_set_config()` set OSD-specific monitor config and fall back to in-memory defaults on command failure.
- `OSD::osd_op_queue_type()` reads the scheduler type from shard 0.
- `OSD::update_log_config()` reparses clog options.
- `OSD::check_config()` emits warnings for insufficient map cache size and invalid clean-region interval config.
- `OSD::get_latest_osdmap()` blocks on `service.objecter->wait_for_latest_osdmap()`.
- `OSD::set_perf_queries()` stores supported dynamic perf stat queries and pushes them to all PGs.
- `OSD::get_perf_reports()` collects dynamic perf stats from all PGs, merges them, and returns an `OSDMetricPayload`.

### Shard and work-queue internals

- `OSDShard::_attach_pg()` and `_detach_pg()` bind or unbind a `PG` from an `OSDShardPGSlot`, update `PG::osd_shard`/`pg_slot`, maintain global PG count, and maintain the intrusive `pg_slots_by_epoch` index.
- `OSDShard::update_pg_epoch()`, `get_min_pg_epoch()`, `wait_min_pg_epoch()`, and `get_max_waiting_epoch()` expose per-shard epoch progress for map reservation and waiting logic.
- `OSDShard::consume_map()` swaps the shard map, wakes slots whose waiting map epochs are now available, drops stale or misdirected waiting operations, releases reserved pushes for dropped recovery work, and prunes empty slots.
- `OSDShard::_wake_pg_slot()` moves `to_process`, `waiting`, and `waiting_peering` items back to the scheduler front and increments `requeue_seq`.
- `OSDShard` construction creates a scheduler through `ceph::osd::scheduler::make_scheduler()`, owns a `context_queue` for on-commit callbacks, and initializes the EC extent cache.
- `OSD::ShardedOpWQ::_add_slot_waiter()` classifies blocked items into `waiting_peering` by map epoch or ordinary `waiting`.
- `OSD::ShardedOpWQ::_process()` is the central worker loop. It waits for scheduler/context work, drains on-commit callbacks from the smallest worker per shard, handles scheduled-future dequeue results, creates or finds the slot by ordering token, serializes on `slot->to_process`, locks the PG if present, handles races with slot requeue/removal, creates PGs from peering events when appropriate, waits or drops items based on map epoch and mapping, primes split children after PG creation, traces processing, runs the queued item, and then handles on-commits.
- `_enqueue()` and `_enqueue_front()` route items to shards by `spg_t` hash, enqueue into the scheduler, and notify waiting threads. `_enqueue_front()` preserves ordering when racing with a worker that has already moved a newer item into `to_process`.
- `stop_for_fast_shutdown()` prevents new enqueueing and drains each shard scheduler.

### OSDBenchTest and heap command

- `OSDBenchTest::precheck()` validates store/collection presence and benchmark input bounds, limiting block size and total count to prevent long OSD stalls.
- `OSDBenchTest::run_test()` flushes store cache, optionally prefills objects, performs writes, cleans up, and computes bandwidth/IOPS.
- `wait_for_flush_commit()`, `prefill_objects()`, `perform_write_test()`, and `cleanup()` implement the ObjectStore transaction flow for the benchmark.
- The constructor records benchmark parameters.
- `ceph::osd_cmds::heap()` validates tcmalloc availability, parses heap command arguments, and delegates to `ceph_heap_profiler_handle_command()`.

## Control Flow

The map path begins after map data is persisted. The superblock and auxiliary metadata are queued in a meta transaction, and `C_OnMapCommit` later invokes `_committed_osd_maps()`. That function updates in-memory map state epoch-by-epoch, handles identity/address/state transitions, and then calls `check_osdmap_features()`, `consume_map()`, and possibly `activate_map()`. `consume_map()` is the fan-out point: it publishes the map to service consumers, primes split/merge slots, advances every shard, wakes sessions waiting on maps, frees dropped push reservations, and queues a null peering event for every PG so PG-local map state catches up.

PG map advancement flows through worker threads. A peering item enters `ShardedOpWQ`, hashes to a shard, moves into the slot's `to_process`, locks the PG if present, and invokes `dequeue_peering_evt()`. That calls `advance_pg()` before dispatching the actual peering event. `advance_pg()` serially applies each missing map, handling merge source teardown, merge target completion or waiting, ordinary `PG::handle_advance_map()`, and split creation. Split children are finalized asynchronously through `C_FinishSplits` and then registered with the owning shard.

Client and recovery operations follow the same sharded ordering path but run through `dequeue_op()` instead of `dequeue_peering_evt()`. The worker loop decides whether a missing PG should be created, waited on, ignored, or treated as a stale/misdirected item. This means map availability, PG existence, split/merge blockers, and current up/acting mapping all participate in whether a queued item can execute.

Recovery is gated outside the main scheduler by `OSDService` counters and configuration. When pushes are released or recovery ops finish, `_maybe_queue_recovery()` can reserve more pushes and schedule more recovery. `do_recovery()` then starts PG recovery work, optionally sleeps according to configured recovery delay policy, and always releases unused reservations.

Runtime configuration flows from `handle_conf_change()` into the specific subsystem that owns the setting. Some changes are purely in-memory, such as op tracker thresholds or throttler caps. Some cause persistent monitor config writes or removals, especially mClock capacity and mClock recovery/backfill override enforcement.

## State and Persistence Behavior

Persistent state touched in this chunk includes:

- `superblock.current_epoch`, `mounted`, `clean_thru`, `purged_snaps_last`, and incompat features, persisted through `write_superblock()` and ObjectStore meta transactions.
- `pg_num_history`, encoded and written to the meta collection under `make_pg_num_history_oid()` after truncating any old contents.
- final deleted-pool metadata written under `make_final_pool_info_oid(pool_id)` so restart-time PG creation can recover pool information for zombie/deleted-pool PGs.
- purged snaps recorded through `SnapMapper::record_purged_snaps()`.
- `require_osd_release` written through `store->write_meta()`.
- mClock measured capacity persisted via `mon_cmd_set_config()` when benchmark results pass threshold checks.
- OSDBenchTest temporary objects created in the ObjectStore and removed through a cleanup transaction.

Important in-memory state includes:

- `osdmap`, map caches, and service-published map/superblock state.
- OSD boot/up/bind epochs stored through `OSDService::set_epochs()`.
- OSD lifecycle flags and transitions between booting, active, waiting-for-healthy, restart, and shutdown.
- heartbeat peer state, messenger bindings, and connection blocklisting through service/messenger calls.
- `merge_waiters`, guarded by `merge_lock`.
- `pending_creates_from_osd`, `pending_creates_from_mon`, and `last_pg_create_epoch`.
- recovery counters `recovery_ops_active`, `recovery_ops_reserved`, `awaiting_throttle`, and sleep scheduling flags/timers.
- per-shard `pg_slots`, `pg_slots_by_epoch`, `waiting`, `waiting_peering`, `to_process`, split wait sets, merge wait epoch, and `requeue_seq`.
- dynamic perf query state `m_perf_queries` and `m_perf_limits`.

## Dependencies and Integration Points

This chunk depends heavily on Ceph OSD internals:

- `OSDMap` and `OSDMapRef` for map epochs, pool metadata, pg-to-acting mapping, flags, addresses, release requirements, and feature masks.
- `ObjectStore`, `ObjectStore::Transaction`, collection handles, and context queues for durable map/PG/benchmark changes.
- `OSDService` for map publication, reservations, recovery state, scrub service, objecter access, heartbeat state, config-driven behavior, and cluster connections.
- `PG`, `PeeringCtx`, `PeeringState`, `PGPeeringEvent`, `PGCreateInfo`, and PG message records for the peering state machine.
- Messenger and connection APIs for peer-role validation, map sharing, policy changes, sending messages, rebinding, and heartbeat address handling.
- Monitor client APIs for marking self dead and updating/removing config keys.
- Scheduler abstractions under `ceph::osd::scheduler` for sharded operation ordering and mClock/classic queue behavior.
- Perf counters, tracepoints, op tracker, `clog`, and debug logging for observability.
- Timers (`mono_timer`, `sleep_timer`) for delayed readable checks and recovery sleep.
- tcmalloc heap profiler APIs for the heap admin command.

## Risks and Edge Cases

- Map gaps are expected in some boot/trim cases, but `track_pools_and_pg_num_changes()` aborts if the previous map cannot be found outside the explicit trim-lower-bound case.
- `_committed_osd_maps()` performs state transitions while juggling `osd_lock` and `map_lock`; incorrect lock ordering or early returns could stall map publication or shutdown/restart decisions.
- Address mismatch handling can restart or shut down an otherwise running OSD. The markdown log limits repeated restarts and can force shutdown when markdown frequency exceeds configured thresholds.
- `check_osdmap_features()` mutates messenger policies without coarse locking by relying on integer field updates and single-writer behavior; future policy changes must preserve that assumption.
- Merge handling in `advance_pg()` explicitly comments on rare races around merge PG instantiation in `consume_map()`. Source shutdown/detach also releases backoffs manually because shutdown teardown is aggressive.
- Split handling relies on transaction on-applied callbacks. If child registration is missed, waiting slots may retain operations indefinitely.
- `dispatch_context()` drops outgoing peering messages to down peers or null connections; callers must rely on later map/peering retries for progress.
- `handle_fast_pg_create()` logs impossible missing history/past-interval data after Octopus and ignores those entries, so compatibility with older/bad monitors depends on this defensive behavior.
- Recovery counters use assertions for underflow and active-count correctness; bugs in reservation release paths can abort the daemon.
- `ShardedOpWQ::_process()` has many race checks around slot removal, requeue, PG replacement, stopping, future scheduling, and map waiting. The `requeue_seq` guard is central to preserving ordering when map consumption wakes blocked items.
- Dropping a non-mapped operation shares the latest map with the client but otherwise discards it; correctness depends on clients resubmitting to the right OSD.
- mClock benchmark persistence trusts the ObjectStore benchmark and threshold configuration. A bad threshold can suppress useful capacity updates or accept misleading results.
- `OSDBenchTest` writes potentially large amounts of data through the real ObjectStore; precheck limits reduce but do not eliminate operational impact.
- Dynamic config changes restart `service.poolctx` for ASIO thread count and change work queue timeouts live; tests should cover active workload behavior during these transitions.

## Test Signals

Useful validation signals for this chunk include:

- OSD map advancement tests that verify superblock epoch/clean_thru updates, `pg_num_history` persistence, purged snap progression, and deleted-pool final metadata.
- Integration tests that boot an OSD through map gaps, NOUP changes, address mismatches, admin stop, and monitor down marking, checking restart/shutdown and `MOSDMarkMeDead` behavior.
- Split and merge tests for `pg_num` increases/decreases, including source teardown, target waiting, child slot priming, child registration, and recovery after restart.
- Peering-message tests that reject wrong peer types and translate create/notify/info/remove/force-recovery messages into the expected PG events.
- Recovery throttling tests for pause, defer, active/reserved limits, sleep scheduling, push release, and unfound-object search dispatch.
- Sharded work queue concurrency tests covering map waits, PG-less queries, stale/misdirected drops, scheduler future items, `_enqueue_front()` ordering, fast shutdown, slot removal races, and on-commit handling.
- Config-change tests for tracked keys: map cache resizing, scrub interval updates, throttler caps, op tracker settings, recovery/backfill reservations, mClock override enforcement, and ASIO/thread timeout changes.
- mClock capacity tests that mock `OSDBenchTest`, threshold acceptance/rejection, monitor config success/failure, and fallback in `MonCmdSetConfigOnFinish`.
- OSDBenchTest unit/integration tests for precheck bounds, prefill/no-prefill modes, cleanup after write failures, elapsed/bandwidth/IOPS calculation, and objectstore flush/commit behavior.
- Perf-query tests that set supported and unsupported query descriptors, propagate queries to all PGs, and merge reports under locking assumptions.
- Admin-command tests for `ceph::osd_cmds::heap()` with and without tcmalloc and with missing or supplied command arguments.
