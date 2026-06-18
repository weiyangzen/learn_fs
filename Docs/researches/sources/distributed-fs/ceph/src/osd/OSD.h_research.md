# sources/distributed-fs/ceph/src/osd/OSD.h

## Purpose
`OSD.h` declares the core classic Ceph OSD daemon surface: `OSD`, its `OSDService` helper, per-shard scheduling state, PG-slot ordering state, and the object-store benchmark helper. The header is the coordination contract between OSD message dispatch, OSDMap publication, PG lifecycle, recovery/backfill, scrub scheduling, heartbeat health, monitor reporting, admin-socket commands, and ObjectStore persistence.

## Important APIs, Types, and Functions
`OSDService` exposes service functions used by PGs and OSD internals: scheduler enqueueing, map publication and pre-publication, map sharing to peers, cluster and heartbeat connection lookup, op error replies, misdirected-op handling, scrub service access, PG locking, snap trim totals, tiering objecter finishers, watcher notification IDs, recovery and scrub queues, PG temp/create reporting, map cache access, OSD stats/fullness checks, boot/up/bind epoch accessors, heartbeat stamp lookup, readable lease renewal, stopping state, and PG timers.

The `OSDService` state model is broad: `superblock`, published and next OSDMaps, map reservation counts, agent queues for cache tiering/promotion/flush, promotion throttling counters, objecter and finisher shards, watch and recovery timers, backfill/snap/scrub reservers, PG merge readiness maps, `pg_temp` desired/pending maps, created-PG reports, recovery throttling lists, OSDMap LRU caches, stat/fullness state, epoch state, heartbeat stamps, lease timer, and stop state.

`OSDShardPGSlot` describes ordering and wait state for one PG slot inside a shard. It holds the PG ref, `to_process` queue, running count, client wait queue, epoch-keyed peering wait queues, requeue generation, split wait epochs, current slot epoch, intrusive epoch-order hook, and merge wait epoch.

`OSDShard` declares per-shard queueing and map consumption machinery: shard locks, `pg_slots`, intrusive `pg_slots_by_epoch`, min-PG-epoch waiters, the per-shard `OpScheduler`, `ContextQueue`, erasure-code extent-cache LRU, PG attach/detach, epoch update, map consumption, PG-slot waking, split/merge identification and priming, and op queue type lookup.

`OSDBenchTest` encapsulates local ObjectStore write benchmarks. It declares precheck, optional object prefill, write test execution, flush/commit wait, cleanup transaction, elapsed/prefill/bandwidth/iops accessors, and error-string reporting.

`OSD` itself derives from `Dispatcher` and `md_config_obs_t`. Major APIs include config observers, startup/shutdown (`pre_init`, `init`, `final_init`, `shutdown`, `fast_shutdown` via service, signal handling), static metadata and mkfs helpers, map object naming helpers, object-store metadata peek/write helpers, ObjectStore benchmark runner, NUMA/FUSE helpers, op queue and shard sizing helpers, message fast-dispatch gates, PG creation/removal and peering handlers, recovery dispatch, scrub rescheduling, command handling, status collection, session waiting-on-map handling, heartbeat dispatch/reset, admin-socket routing, and performance-query plumbing.

## Control Flow
The header documents a layered dispatch path. Messenger fast dispatch accepts client ops, peering, recovery, scrub, heartbeat, command, and lease messages. OSD dispatch turns messages into scheduler items keyed by PG/shard. `ShardedOpWQ` enqueues items into each shard scheduler, moves dequeued work into `OSDShardPGSlot::to_process`, waits when PGs or maps are unavailable, preserves per-client and per-peer ordering, and requeues waiters when a PG materializes, a split completes, or a map advances.

Map flow is split between globally visible and pre-published state. `OSDService::publish_map` and `get_osdmap` expose the active map under `publish_lock`; `pre_publish_map`, `get_nextmap_reserved`, `release_map`, and `await_reserved_maps` coordinate a next map that helpers may use only while respecting map reservations. `OSD::handle_osd_map`, `track_pools_and_pg_num_changes`, `consume_map`, `activate_map`, and `advance_pg` are declared as the path that persists maps, tracks PG split/merge history, updates shards, and advances PGs through peering state.

PG lifecycle flow runs through `_make_pg`, `register_pg`, `load_pgs`, `handle_pg_create_info`, fast PG create/notify/info/remove handlers, split/merge helpers, pending create throttles, and deletion queueing. The shard comments define how missing PGs, future epochs, split children, and merge waiters are held without violating client or peer ordering.

Recovery, scrub, and snap trim are queued through `OSDService` methods that create scheduler items or scrub event messages with costs and priorities. Recovery uses `awaiting_throttle`, active/reserved push counters, pause/defer state, and scheduler-specific sleep paths. Scrub uses explicit queues for primary and replica state transitions such as resched, pushes update, applied update, chunk free/busy, unblocking, digest update, replica maps, finish, and next chunk.

Heartbeat flow is isolated from the main op path. `HeartbeatDispatcher` fast-dispatches pings, and `T_Heartbeat` runs `heartbeat_entry`, which maintains peer connections, ping history, health classification, peer update needs, and monitor failure reporting.

## State and Persistence Behavior
Persistent ObjectStore state surfaced here includes the OSD superblock, meta collection handle, osdmap and incremental-osdmap objects (`osdmap.<epoch>` and `inc_osdmap.<epoch>`), snapmapper, purged snapshots, final pool info, PG num history, PG collections, and mkfs/write-meta artifacts. `write_superblock`, `read_superblock`, `trim_maps`, `trim_stale_maps`, `write_meta`, `peek_meta`, and `recursive_remove_collection` are the persistence-facing declarations.

Long-lived in-memory state includes atomic OSD daemon state, atomic/current OSDMap refs, PG count, pending creates, sessions waiting for newer maps, heartbeat peer state, failure queues, monitor report timestamps, full/nearfull/failsafe state, map caches, stat counters, op tracker, perf query limits, timers, worker queues, and Objecter/tiering state. Most shared state is guarded by explicit Ceph locks; the header also calls out lock ordering for PG map interactions: `PG::lock`, then `ShardData::lock`, then `OSD::pg_map_lock`.

## Dependencies and Integration Points
This header integrates with `PG.h`, `OpRequest.h`, `Session.h`, `ObjectStore`, `OSDMap`, `Messenger`, monitor and manager clients, `LogClient`, `OpScheduler`, `AsyncReserver`, scrubber services, timers, finishers, shared/simple LRUs, perf counters, admin socket hooks, and many OSD message types. `OSDService` is intentionally friend-accessible to `OSD`, `PG`, `PrimaryLogPG`, and scrub classes, making it the common service layer for placement-group code.

Monitor integration appears through OSDMap subscriptions, boot/preboot, metadata collection, alive/up-through beacons, failure reports, PG temp/create reports, full-status updates, and purged-snap replies. Client and peer integration appears through session wait queues, op error replies, backoff/reset cleanup, objecter tiering, heartbeat peers, and direct cluster/client messenger send helpers.

## Risks
The main risks are concurrency and ordering regressions. PG-slot queues must preserve client ordering and peer peering ordering while allowing map waits, PG creation, split waits, and merge waits. OSDMap pre-publication and reservation handling must avoid using stale maps to reopen connections to OSD instances that are about to go down. Recovery and scrub queues share scheduler resources and must keep cost/priority semantics consistent across weighted-priority and mclock paths.

State risks include stale OSDMap persistence leaks, incorrect PG num history for split/merge detection, full-status misclassification, missed heartbeat failures or false positives, leaked session/message/connection reference cycles, lingering PG temp/create reports, and ObjectStore cleanup errors in mkfs, benchmarks, or PG deletion.

Security and availability risks include fast-dispatch accepting a broad set of message types, peer identity gates in `require_mon_peer`, `require_mon_or_mgr_peer`, and `require_osd_peer`, admin-socket command routing to PGs, and `filter_xattrs` preserving only underscore-prefixed internal xattrs.

## Test Signals
Useful tests include OSDMap publication/reservation races, map trimming and stale-map cleanup, PG creation under max-PG throttles, split and merge wait/requeue behavior, ordered client ops across map waits, peering message ordering by peer, session reset cleanup, recovery pause/defer/sleep throttling, scrub event queue transitions, heartbeat peer add/remove and stale/unhealthy detection, full/backfillfull/nearfull/failsafe thresholds including injected full states, mkfs/read-superblock/peek-meta paths, benchmark cleanup after failures, and messenger fast-dispatch authentication/refusal/reset handling.
