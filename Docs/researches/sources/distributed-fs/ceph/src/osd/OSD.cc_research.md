# Research: sources/distributed-fs/ceph/src/osd/OSD.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006936`: lines 1-8468, `Docs/researches/chunks/subset-b-006936_research.md`
- `subset-b-006937`: lines 8469-11888, `Docs/researches/chunks/subset-b-006937_research.md`

## Chunk Research

### subset-b-006936: lines 1-8468

# sources/distributed-fs/ceph/src/osd/OSD.cc lines 1-8468

## Scope

This chunk covers the first 8,468 lines of Ceph's OSD daemon implementation. It starts with includes, compatibility feature definitions, and `OSDService`, then covers OSD formatting, metadata handling, construction, initialization, admin-socket commands, shutdown, PG loading/creation, heartbeat/failure detection, boot/preboot, monitor reporting, dispatch setup, PG statistics, health metrics, and the beginning of OSDMap ingestion. The chunk ends inside `OSD::handle_osd_map()` after adding received maps to transactions/caches and updating superblock map intervals; the later map commit, activation, PG scan, and consume logic continues in the next chunk.

## Purpose

`OSD.cc` is the central runtime coordinator for a Ceph object storage daemon. In this range it ties together durable local state in the `ObjectStore`, current and historical `OSDMap` state, PG lifecycle management, monitor and manager protocols, heartbeat/failure detection, op queueing, and admin/debug surfaces.

The covered code does not implement object IO itself; that is largely delegated to PG classes such as `PrimaryLogPG`. Instead, this layer provides the daemon envelope around PGs: startup and boot sequencing, map persistence, PG discovery and creation, service helpers used by PGs, heartbeat networking, monitor updates, and routing of fast-dispatch messages into per-PG work queues.

## Important APIs, Types, And Functions

### Compatibility And Service Setup

- `OSD::get_osd_initial_compat_set()` and `OSD::get_osd_compat_set()` define supported on-disk OSD feature bits. The initial set includes long-lived incompat features such as `PGINFO`, `OLOC`, `HOBJECTPOOL`, `SNAPMAPPER`, `PGMETA`, `FASTINFO`, `RECOVERY_DELETES`, and `SNAPMAPPER2`; the runtime supported set additionally includes `SHARDS`.
- `OSDService::OSDService()` wires the service facade to the owning `OSD`, `ObjectStore`, messengers, `MonClient`, loggers, scrub services, reservers, timers, map caches, and an internal `Objecter`.
- `OSDService::init()`, `final_init()`, `start_shutdown()`, `shutdown_reserver()`, `shutdown()`, and `fast_shutdown()` manage service-level timers, finishers, the tiering agent thread, the objecter, map publication, and reservation teardown.
- `OSDService::activate_map()` enables or disables the tiering agent according to OSDMap `NOTIERAGENT` and OSD activity state.

### OSDMap Management Helpers

- `OSDService::identify_splits_and_merges()` walks pool `pg_num` history between two maps to find split children and merge participants for a PG. It uses a queue so fabricated merge parents and later split descendants can be discovered recursively.
- `OSDService::get_nextmap_reserved()`, `release_map()`, and `await_reserved_maps()` coordinate access to `next_osdmap` while dispatchers may still reference older pre-published maps.
- `OSDService::build_incremental_map_msg()`, `send_incremental_map()`, `_get_map_bl()`, `get_inc_map_bl()`, `_add_map_bl()`, `_add_map_inc_bl()`, `_add_map()`, and `try_get_map()` implement map sharing and map cache/persistence reads. They prefer incremental maps where possible, fall back to full maps across gaps, page-align buffers, and maintain separate caches for decoded maps, full map blobs, and incremental map blobs.
- `OSDService::maybe_share_map()` updates a peer session's projected map epoch and sends the missing `(projected_epoch, current_epoch]` map range over the existing connection.
- `OSD::osdmap_subscribe()`, `request_full_map()`, `got_full_map()`, `trim_maps()`, `trim_stale_maps()`, and `handle_osd_map()` coordinate monitor subscriptions, explicit full-map fetches, on-disk map trimming, stale map cleanup, and ingestion of `MOSDMap` messages.

### Fullness, Stats, And Reporting

- `OSDService::recalc_full_state()` computes `NONE`, `NEARFULL`, `BACKFILLFULL`, `FULL`, or `FAILSAFE` from logical and physical ratios, OSDMap thresholds, the failsafe ratio, and test injection state.
- `check_full_status()`, `need_fullness_update()`, `check_*full()`, `tentative_backfill_full()`, `is_*full()`, and `set_injectfull()` provide runtime fullness checks for write/backfill admission, monitor reporting, and admin-test injection.
- `set_statfs()`, `set_osd_stat()`, `compute_adjusted_ratio()`, `inc_osd_stat_repaired()`, and `set_osd_stat_repaired()` maintain `osd_stat_t`, heartbeat ping metrics, op queue age histograms, fake-statfs test behavior, backfill-adjusted capacity ratios, and repaired-shard health counters.
- `OSD::collect_pg_stats()` builds `MPGStats` for the manager by gathering OSD stats, object-store perf stats, primary PG stats, per-pool statfs where supported, and `min_last_epoch_clean` beacon state.
- `OSD::get_health_metrics()` reports slow ops and pending PG creation counts to the manager health channel. It can emit aggregated slow-op cluster log messages grouped by op state and most affected pool.

### Op, Recovery, Scrub, And PG Queueing

- `OSDService::reply_op_error()` constructs `MOSDOpReply` for early op failure paths.
- `handle_misdirected_op()` warns or drops certain misdirected ops, with special EC handling for primary shard changes across map epochs.
- `enqueue_back()`, `enqueue_front()`, `queue_recovery_context()`, `queue_for_snap_trim()`, `_queue_for_recovery()`, `queue_for_pg_delete()`, and the scrub queue helpers wrap PG work as `OpSchedulerItem`s and feed `op_shardedwq`.
- Scrub queue helpers include `queue_for_scrub()`, `queue_for_rep_scrub()`, `queue_for_rep_scrub_resched()`, `queue_for_scrub_resched()`, `queue_scrub_pushes_update()`, `queue_scrub_chunk_free()`, `queue_scrub_chunk_busy()`, `queue_scrub_applied_update()`, `queue_scrub_unblocking()`, `queue_scrub_digest_update()`, `queue_scrub_got_repl_maps()`, `queue_scrub_replica_pushes()`, `queue_scrub_is_finished()`, and `queue_scrub_next_chunk()`.
- Cost accounting adapts to the selected op queue. mClock uses cost estimates such as object counts or reserved pushes; the legacy weighted priority queue uses configured fixed costs.

### PG Lifecycle

- `OSD::_make_pg()` creates a `PrimaryLogPG` from a live pool in the map or from final pool-info tombstones for deleted pools.
- `_get_pgs()`, `_get_pgids()`, `register_pg()`, `_lookup_pg()`, `_lookup_lock_pg()`, and `lookup_lock_pg()` provide shard-indexed PG inventory operations.
- `load_pgs()` reads `pg_num_history`, lists collections, removes temporary or removal-flagged PG collections, peeks each PG's map epoch, reconstructs PGs, opens collections, reads PG state, assigns commit queues, and registers live PGs.
- `handle_pg_create_info()` handles monitor or peer PG creation info: applies max-PG throttling, validates pool creation flags, creates collections and initial on-disk PG metadata, initializes PG role/history/past intervals, runs initialize/activate events, and dispatches resulting transactions.
- `maybe_wait_for_max_pg()` and `resume_creating_pg()` enforce the hard PG-per-OSD limit. Delayed monitor creates resubscribe to `osd_pg_creates`; delayed OSD-origin creates send forced `pg_temp` twiddles to retrigger peering.
- `try_finish_pg_delete()` detaches a PG from its shard slot after delete completion, unprimes split children, and decrements PG role counters.
- Merge readiness helpers (`set_ready_to_merge_source()`, `set_ready_to_merge_target()`, `set_not_ready_to_merge_source()`, `set_not_ready_to_merge_target()`, `send_ready_to_merge()`, `_send_ready_to_merge()`, `clear_ready_to_merge()`, `clear_sent_ready_to_merge()`, `prune_sent_ready_to_merge()`) batch `MOSDPGReadyToMerge` monitor notifications and avoid duplicate source reports.

### OSD Formatting, Metadata, Construction, Init, And Shutdown

- `OSD::write_superblock()` persists `OSDSuperblock` both as object data and in an omap key on `OSD_SUPERBLOCK_GOBJECT`.
- `OSD::mkfs()` initializes an `ObjectStore`, creates or validates the meta collection and superblock, and writes store metadata.
- `OSD::write_meta()` writes `magic`, `whoami`, `ceph_fsid`, key material, osdspec affinity, creation version, creation time, and `ready`.
- `OSD::peek_meta()` reads enough metadata to identify an existing OSD without fully booting it.
- `OSD::OSD()` constructs daemon subsystems: messengers, `MgrClient`, loggers, `LogClient`, `OpTracker`, op threadpool, sharded op queue, boot finisher, `OSDService`, shard objects, GSS keytab env, trace endpoint, and scheduler type/cutoff.
- `pre_init()` checks mount-in-use and registers config observation. `set_numa_affinity()` derives CPU affinity from store and network NUMA locality, with `osd_numa_node` overriding auto-detection.
- `OSD::init()` is the main slow startup path: initialize timers, mount store, open meta collection, validate object name limits, read/upgrade superblock, load current OSDMap, check deleted-pool safety, create snapmapper/purged-snaps objects, load object classes, set bind epoch, clear temp objects, load PGs, initialize statfs, wire auth clients/servers and dispatchers, initialize monitor and manager clients, publish maps/superblock, prime split/merge slots, start op and heartbeat threads, authenticate and wait for rotating keys, update CRUSH class/location, optionally compact, start objecter, consume prior maps, subscribe to PG creates/mgrmap, start boot, and apply QoS overrides.
- `OSD::shutdown()` has fast and slow paths. Fast shutdown stops accepting queue work, shuts timers/admin hooks, drains and stops the op threadpool, stops the agent, prepares the store, fast-shuts service timers, unmounts, and exits. Slow shutdown marks stopping, shuts down PGs, drains queues, stops heartbeat and messengers, writes clean unmount state to the superblock, tears down reservers and PG references, unregisters config observation, closes meta collection, flushes journal if configured, shuts down monitor/service/objectstore/messengers, and removes op tracking state.

### Admin Socket And Test Commands

- `OSDSocketHook` routes admin-socket commands to `OSD::asok_command()` asynchronously.
- `OSD::asok_command()` handles status, op tracker dumps, queue state, blocklist, watchers, recovery/scrub reservations, latest-map fetch, heap properties, object-store KV stats, scrub dump, DB histogram, cache flush/drop/status, stored-key rotation, PG state history, compaction, mapped-pool listing, SMART data, device listing, beacon send, cluster log, OSD benchmark, PG stats flush, heap/cpu profiling, missing-object dump, recovery kick, recovery stats, stale OSDMap trimming, purged-snap scrub/reset, shard repair count reset, network ping reports, pool statfs, and OSD PG stats.
- PG-targeting admin commands are routed to `PG::do_command()` only when the local PG is primary, except `scrubdebug`, which can route to non-primary PGs.
- `TestOpsSocketHook::test_ops()` implements direct test/debug mutations and injections: omap set/remove/header/get, truncate, data/metadata error injection, EC read/write/parity injection controls, recovery delay changes, and fullness injection.

### Heartbeat, Failure Detection, Boot, And Monitor Reports

- `_add_heartbeat_peer()`, `_remove_heartbeat_peer()`, `need_heartbeat_peer_update()`, `maybe_update_heartbeat_peers()`, and `reset_heartbeat_peers()` maintain heartbeat peer sets from active PG peers, neighbor OSDs, random up OSDs by subtree, and stale-peer cleanup.
- `handle_osd_ping()` processes `PING`, `PING_REPLY`, and `YOU_DIED`. It validates fsid, updates `HeartbeatStamps`, replies on heartbeat channels, shares maps over cluster connections, records front/back ping averages and min/max windows, cancels queued or pending failure reports when a peer recovers, and subscribes for maps when another OSD says this OSD is down.
- `heartbeat_entry()`, `heartbeat_check()`, `heartbeat()`, and `heartbeat_reset()` run the heartbeat loop, send front/back pings, maintain deadline history, compute full status from current stats, queue failure reports, reopen heartbeat connections after resets, and request newer maps when isolated.
- `tick()` runs under `osd_lock` and handles markdown-log expiry, heartbeat peer updates, retrying boot while waiting for health, monitor map polling during boot, and periodic purged-snap scrub scheduling.
- `tick_without_osd_lock()` updates buffer CRC counters and statfs, performs heartbeat checks and monitor reports, sends full/failure updates, requests maps for waiting shards, initiates scrubs, recalibrates promote throttles, resumes delayed PG creates, sends beacons, updates daemon health, and kicks the recovery queue.
- `start_boot()`, `_got_mon_epochs()`, `_preboot()`, `_get_purged_snaps()`, `handle_get_purged_snaps_reply()`, `_is_healthy()`, `start_waiting_for_healthy()`, `_send_boot()`, and `_collect_metadata()` implement the preboot state machine. The OSD waits for internal/peer heartbeat health, enough recent maps, fullness updates, purged-snap records, and PG peering catch-up before sending `MOSDBoot` with addresses, superblock, boot epoch, features, and metadata.
- `send_full_update()`, `queue_want_up_thru()`, `send_alive()`, `requeue_failures()`, `send_failures()`, `send_still_alive()`, `cancel_pending_failures()`, `send_beacon()`, and `maybe_send_beacon()` are the monitor-reporting paths for fullness, `up_thru`, failure/alive reports, and Luminous+ OSD beacons.

### Messaging And Dispatch

- `ms_handle_connect()` resends boot or monitor reports on monitor reconnect and rerequests pending full maps.
- `ms_handle_fast_connect()` and `ms_handle_fast_accept()` ensure OSD peer sessions exist for outgoing/incoming non-monitor, non-manager connections.
- `ms_handle_reset()` breaks connection/session ref cycles and runs session reset cleanup. `ms_handle_refused()` can immediately report refused OSD connections as failures when configured.
- `ms_dispatch()` handles non-fast messages under `osd_lock`; in this chunk it recognizes mark-me-down acks, `MOSDMap`, purged-snap replies, and admin `MCommand`.
- `ms_fast_dispatch()` handles fast-path messages without taking `osd_lock` unless needed by target handlers. It directly handles force recovery, scrub requests, PG creation/notify/info/remove, and single-PG peering ops. Other fast-dispatch ops become tracked `OpRequest`s and are enqueued to the shard queue. Legacy clients without split-resend or Tentacle shard encoding support are ordered through `Session::waiting_on_map` until the right map can translate them.
- `ms_handle_fast_authentication()` initializes session caps from connection auth caps and rejects undecodable or unparsable caps.

## Control Flow

The normal startup flow is:

1. `pre_init()` verifies the store is not already mounted and registers config observation.
2. `init()` mounts the store, opens metadata, reads/upgrades the superblock, loads the current OSDMap, creates metadata helper objects, clears temporary objects, loads existing PGs, initializes auth/monitor/manager/messenger/service infrastructure, starts threads, authenticates, updates CRUSH metadata, starts the objecter, consumes prior maps, subscribes to monitor channels, and calls `start_boot()`.
3. `start_boot()` either waits for heartbeat health or moves to preboot and asks the monitor for OSDMap epochs.
4. `_preboot()` checks map recency, destroyed/noup/sortbitwise/fullness state, purged-snap catch-up, and PG map consumption before `_send_boot()`.
5. `_send_boot()` resolves local addresses, sets NUMA affinity, collects metadata, sends `MOSDBoot`, and enters `STATE_BOOTING`.
6. Later OSDMap handling, not fully contained in this chunk, marks the OSD active once the monitor maps it up and PGs consume the necessary maps.

The steady-state loop is split between timers and message dispatch:

- `heartbeat_entry()` periodically calls `heartbeat()` under `heartbeat_lock`.
- `tick()` handles OSD-lock-protected periodic tasks.
- `tick_without_osd_lock()` handles statfs, monitor reports, scrub/recovery triggers, beacons, health updates, and recovery queue kicks without holding `osd_lock`.
- `ms_fast_dispatch()` routes most OSD/PG protocol messages to per-shard queues; `ms_dispatch()` handles map and command messages under `osd_lock`.

Shutdown first prevents new work, then drains queues and threads, then tears down PGs, service timers, monitor/client state, map references, object-store state, and messengers. The fast shutdown branch deliberately skips most persistent clean-unmount work and exits after draining enough to unmount safely.

## State And Persistence Behavior

The key durable state in this chunk is stored in the `ObjectStore` meta collection:

- `OSDSuperblock` is written both as object data and as an omap key. `read_superblock()` reads both replicas and chooses the newer `current_epoch` if they disagree.
- Full maps are stored under `get_osdmap_pobject_name(epoch)` and incremental maps under `get_inc_osdmap_pobject_name(epoch)`.
- `pg_num_history`, snapmapper, purged-snap records, final deleted-pool info, and PG collections are read or updated during startup, PG creation, map handling, purged-snap scrub, and map trimming.
- Store metadata keys record identity and bootstrap facts: `magic`, `whoami`, `ceph_fsid`, `osd_key`, `osdspec_affinity`, `ceph_version_when_created`, `created_at`, and `ready`.

Important in-memory state includes:

- Current OSD state (`STATE_PREBOOT`, `STATE_BOOTING`, active/waiting/stopping variants), boot/up/bind epochs, `up_thru_wanted`, full-map request ranges, pending PG creates, `last_pg_create_epoch`, and `osd_markdown_log`.
- `OSDService` published map/superblock references, decoded map caches, map blob caches, pre-publish reservations, stat state, full status state, heartbeat stamps, pg_temp queues, PG-created queues, merge-readiness queues, recovery/scrub/snap reservers, tiering agent state, objecter finishers, and timers.
- Per-shard PG slots, per-shard map references, op queues, waiting-map session queues, and EC extent cache LRUs.
- Heartbeat peer state with front/back connections, sent ping history, deadlines, last RX/TX times, ping average rings, failure queues, and failure reports pending monitor acknowledgement.

Persistence ordering is central. Startup persists feature upgrades before proceeding. Map handling writes full/incremental map objects and updates the superblock before later activation. Shutdown writes clean unmount epoch and `clean_thru` in the superblock on the slow path. `trim_maps()` never trims below the map-cache lower bound because PGs may still reference older epochs.

## Dependencies And Integration Points

This code integrates with most of the OSD subsystem:

- `ObjectStore` for mkfs/mount/unmount, collections, transactions, statfs, metadata, cache, compaction, pool stats, SMART/device metadata, and debug error injection.
- `OSDMap` and monitor messages (`MOSDMap`, `MMonGetOSDMap`, `MOSDBoot`, `MOSDFull`, `MOSDFailure`, `MOSDAlive`, `MOSDBeacon`, `MOSDPGTemp`, `MOSDPGCreated`, `MOSDPGReadyToMerge`, purged-snap messages) for cluster membership and map/state reporting.
- `Messenger`, `Connection`, and `Session` for client, cluster, heartbeat, objecter, monitor, and manager channels.
- `PG`, `PrimaryLogPG`, peering event classes, scrub-machine messages, snap trimming, recovery, and PG deletion queueables for per-PG behavior.
- `MgrClient` for PG stats, perf metric queries/reports, and daemon health metrics.
- `MonClient`, auth handlers, rotating keys, and `LogClient` for bootstrapping and monitor interaction.
- `AdminSocket` for operator/debug control and PG command routing.
- `HeartbeatMap`, NUMA helpers, block-device helpers, class handler, CPU/heap profilers, LTTng tracepoints, op tracker, perf counters, and QoS/mClock configuration.

## Risks And Edge Cases

- Startup ordering is brittle. The OSD must not accept maps too early, start the objecter before authentication, trim maps before PGs are done with them, or boot before fullness, purged-snap, health, and PG map-consumption prerequisites are satisfied.
- Superblock and map persistence are correctness-critical. Corrupt or mismatched superblock replicas are tolerated only to the extent that one valid replica exists; missing maps for existing pools can abort startup.
- Incremental map CRC mismatch handling is safety-critical. The OSD requests full maps and truncates the current message's usable range when reconstructed full-map CRCs do not match.
- Map sharing and reservation logic must avoid use-after-publication races. `get_nextmap_reserved()` and `release_map()` protect peers using pre-published maps while newer maps are being published.
- Fullness logic controls write and backfill admission. Miscomputing logical versus physical ratios, backfill adjustments, or injected state can either drop valid writes or allow unsafe writes past full thresholds.
- Heartbeat state has several race-prone paths: connection reset/reopen, stale-peer cleanup, monitor failure report cancellation, dual front/back connection accounting, and `YOU_DIED` handling.
- PG creation throttling depends on monitor subscriptions and forced `pg_temp` twiddles. Bugs here can leave PGs withheld indefinitely or overrun `mon_max_pg_per_osd` hard ratios.
- Admin/test commands intentionally mutate objectstore state and inject errors. They are powerful and guarded mainly by admin-socket access and session caps.
- Fast shutdown skips clean-unmount superblock updates and exits the process. It must only be used when the store path can tolerate that behavior.
- The chunk ends mid-`handle_osd_map()`. The later commit callback, map activation, PG peering updates, and cleanup must be reviewed with the next chunk before drawing conclusions about full map-application semantics.

## Test And Validation Signals

Useful validation for this chunk includes:

- OSD mkfs/start/stop/restart tests covering existing superblocks, mismatched identities, feature upgrades, missing/corrupt superblock replicas, and clean versus fast shutdown.
- OSDMap ingestion tests with full maps, incremental maps, map gaps, duplicate maps, monitor trim lower bounds, CRC mismatch fallback, explicit full-map rerequests, stale map trimming, and peers receiving shared map ranges.
- PG lifecycle tests for startup `load_pgs()`, deleted-pool tombstones, temporary/removal collections, PG creation from monitor and OSD peers, max-PG throttling/resume, split/merge priming, PG delete completion, and merge-ready monitor notifications.
- Heartbeat/failure tests with front/back ping success, dropped pings, stale peers, connection resets, refused connections, false failure cancellation, `YOU_DIED` handling, and monitor failure/alive messages.
- Boot sequencing tests for unhealthy heartbeat map, peer health ratio, `noup`, destroyed OSD, missing `SORTBITWISE`, fullness update required before boot, purged-snap catch-up, and PG peering drain before `MOSDBoot`.
- Admin-socket tests for command registration/routing, PG primary-only behavior, non-primary `scrubdebug`, op tracker dumps, cache and compaction commands, pool statfs, SMART/device listing, recovery stats, and guarded test injections.
- Fullness/stat tests for fake statfs, backfill-adjusted ratios, injected full states, nearfull/backfillfull/full/failsafe transitions, monitor `MOSDFull` emission, heartbeat ping metric export, and manager daemon health metrics.
- Dispatch tests for monitor map handling under `osd_lock`, fast peering messages, legacy client PG remapping through `waiting_on_map`, session auth cap parsing, command authorization, and operation tracking/tracing.

### subset-b-006937: lines 8469-11888

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
