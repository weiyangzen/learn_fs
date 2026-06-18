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
