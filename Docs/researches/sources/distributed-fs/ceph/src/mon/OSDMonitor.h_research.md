# sources/distributed-fs/ceph/src/mon/OSDMonitor.h

## Purpose

`OSDMonitor.h` declares the monitor-side service responsible for maintaining and publishing the cluster OSD map. It is a `PaxosService` whose committed state is the authoritative OSDMap history, and it also observes config changes through `md_config_obs_t`. The header defines the service state, failure-report bookkeeping, OSD map manifest support, background PG mapping jobs, command/daemon message entry points, pool and CRUSH mutation helpers, PG creation tracking, and stretch-mode controls.

The file is intentionally broad because the OSD monitor owns several high-value coordination surfaces: OSD lifecycle, OSD failure detection, pool creation/deletion, CRUSH rule and erasure-code validation, map delivery to clients/OSDs, PG split/merge/create notifications, purged snapshot metadata, blocklist mutations, and stretch cluster transitions.

## Important APIs, Types, and State

`failure_reporter_t` stores one reporter's view of a target OSD failure, including the `failed_since` timestamp and the original `MonOpRequestRef`. `failure_info_t` aggregates reporters by reporting OSD, lazily recomputes `max_failed_since`, can move report messages into a list for completion, and supports cancellation per reporter. These types back monitor-side OSD down decisions and are sensitive to stale reports and reporter churn.

`LastEpochClean` tracks per-pool `last_epoch_clean` reports. Its nested `Lec` records epochs by PG, the next missing PG shard, and a floor value. The public API records PG reports, removes pools, returns a lower bound over the cluster, and dumps formatter state. This is used by OSDMonitor to derive safe trimming and health signals from OSD beacons.

`osdmap_manifest_t` records pinned full OSD map epochs. It exposes first/last pinned helpers, membership, insertion, nearest-lower pinned lookup, versioned encode/decode, and formatter dump output. The manifest exists because OSDMonitor manages full OSD map persistence and pruning itself instead of delegating full-version stashing to `PaxosService`.

`OSDMonitor` derives from `PaxosService` and `md_config_obs_t`. Its central committed object is public `OSDMap osdmap`; leader-side pending state includes `OSDMap::Incremental pending_inc`, pending OSD metadata writes/removals, `failure_info`, `down_pending_out`, OSD weights, map caches, pruning manifest, priority-cache controls, and background mapping structures. Important public APIs include `tick`, command preprocessing/preparation, `get_version`, `get_version_full`, `get_inc`, `send_latest`, `send_incremental`, `blocklist`, metadata dumps, subscription checks, application enablement, pool option updates, OSD create/purge/destroy helpers, and stretch-mode transitions.

The `CleanUpmapJob` and `PrimeTempJob` nested classes are `ParallelPGMapper::Job` implementations. `CleanUpmapJob` scans PG upmap state, uses `OSDMap::check_pg_upmaps`, and under a mutex updates `pending_inc` through `clean_pg_upmaps`. `PrimeTempJob` iterates PG ranges and calls `prime_pg_temp`. The surrounding `ParallelPGMapper`, `OSDMapMapping`, and `mapping_job` members show that expensive PG-to-OSD calculations can be offloaded while preserving monitor state consistency.

The callback contexts `C_Booted`, `C_ReplyMap`, and `C_PoolOp` convert Paxos-service completion results into monitor replies. They dispatch the success path, ignore `-ECANCELED`, redispatch on `-EAGAIN`, and abort on unexpected return codes. That pattern is important because many OSDMonitor operations are prepared during one Paxos round and only reply after the proposal commits.

## Control Flow and Integration

The service lifecycle is inherited from `PaxosService`: `create_initial`, `update_from_paxos`, `create_pending`, `encode_pending`, `on_active`, `on_restart`, `on_shutdown`, `get_store_prefixes`, and `get_trim_to` integrate the OSD map service with monitor Paxos. OSDMonitor deliberately overrides `encode_full` as empty and `should_stash_full` as false because full OSD map persistence is locally managed. `encode_trim_extra` participates in trims so old full maps remain available as needed for peers rebuilding state.

Message handling is split into read-only preprocessing and update preparation. `preprocess_query`, `prepare_update`, `should_propose`, and specialized helpers handle OSD map fetches, boot/alive/full beacons, failure reports, mark-down/dead flows, PG temp updates, PG created/merge notifications, pool operations, purged snap operations, and monitor CLI commands. The `send_full`, `send_incremental`, `build_latest_full`, and `build_incremental` methods are the map distribution path for OSDs, clients, and monitor subscriptions.

Pool and CRUSH command helpers validate invariants before mutating `pending_inc`: pool remove/rename, tiering, erasure-code profile normalization, CRUSH rule creation, pool size/min_size, stripe width, PG count sizing, autoscale/bulk/crimson flags, application metadata, stretch mode, and OSD/CRUSH removal. This front-loads safety checks into monitor command preparation rather than allowing invalid OSDMap increments to commit.

Failure detection flows through `check_failures`, `check_failure`, `get_grace_time`, `is_failure_stale`, `force_failure`, `process_failures`, and `take_all_failures`. These functions combine reporter records, grace intervals, laggy thresholds, and mark-down eligibility (`can_mark_down/up/out/in`) before composing `pending_inc`. Timeout processing also connects to `handle_osd_timeouts` and beacon tracking in `last_osd_report`, `osd_epochs`, and `last_epoch_clean`.

PG creation tracking keeps `creating_pgs_by_osd_epoch`, `pending_created_pgs`, `creating_pgs_epoch`, and `creating_pgs` under `creating_pgs_lock`. Helpers scan pool changes, update pending PGs from an OSDMap incremental, compute parent PGs, update subscriptions, and send PG create messages to OSDs. This makes pool creation and PG split/merge state visible to the OSDs that must instantiate PGs.

## State and Persistence Behavior

Committed state is encoded via the PaxosService path into monitor store versions; the pending delta is `pending_inc`. OSD metadata has separate pending add/remove containers. Full OSD maps and incrementals are cached in `SimpleLRU` keyed by `(version, features)`, so callers can request feature-specific encodings without reencoding each time.

Full OSD map pruning is explicit. `load_osdmap_manifest`, `should_prune`, `_prune_update_trimmed`, `prune_init`, `_prune_sanitize_options`, `is_prune_enabled`, `is_prune_supported`, and `do_prune` coordinate the manifest and monitor store transactions. The manifest pins full epochs that must survive outside normal trim intervals. The comments around `should_stash_full` and `encode_trim_extra` are strong signals that OSDMonitor persistence cannot be treated like a generic PaxosService log.

Purged snapshot metadata is stored with generated keys from `make_purged_snap_epoch_key`, `make_purged_snap_key`, and `make_purged_snap_key_value`. `insert_purged_snap_update`, `lookup_purged_snap`, `try_prune_purged_snaps`, and remove-snaps command handlers integrate snapshot purge ranges with OSDMap epochs.

Priority cache state is local monitor process state, not Paxos state. The cache sizing fields and helpers register OSD map caches and RocksDB binned KV cache with `PriorityCache::Manager`, tune cache ratios, and react to config changes.

## Dependencies and Integration Points

The header depends on Ceph monitor infrastructure (`Monitor`, `PaxosService`, `MonOpRequest`, `Subscription`), OSD map types (`OSDMap`, `OSDMapMapping`, CRUSH wrappers), erasure-code interfaces, encoding/buffer helpers, `SimpleLRU`, `PriorityCache`, `ParallelPGMapper`, and monitor DB transactions. It also has direct command integration through `cmdmap_t`-based methods and daemon integration through OSD boot, beacon, alive, failure, and map request messages.

OSDMonitor is a hub for other monitor services. Stretch-mode helpers coordinate with monmap stretch logic; `notify_new_pg_digest` hints at manager/OSD recovery integration; application metadata affects clients such as RBD, CephFS, and RGW; feature validation blocks CRUSH or pool changes when daemons do not support them.

## Risks and Edge Cases

The biggest risk is committing an invalid `pending_inc`, because OSDMap changes are cluster-wide control-plane state. Pool removal, CRUSH mutations, stretch mode, and OSD purge paths need strict validation and clear error propagation. The separate full-map pruning path is another high-risk area: trimming too aggressively can prevent lagged monitors or OSDs from reconstructing needed maps.

Failure detection is timing-sensitive. Stale reports, clock skew, laggy OSDs, and repeated reporter cancellation can cause false down/out decisions if grace logic or `max_failed_since` maintenance is wrong. Background mapper jobs mutate pending state from parallel scans and therefore rely on locking and on avoiding stale OSDMap views.

Feature-specific map encodings and messenger feature checks can create compatibility regressions. The reencoding helpers, map caches, and `validate_crush_against_features` should be treated as compatibility-critical, especially around mixed-version clusters.

## Test Signals

Relevant tests should exercise OSDMap lifecycle commands, OSD boot/alive/failure handling, map fetches with different feature masks, pool create/delete/rename, CRUSH rule and erasure-code validation, PG create notifications, purged snap key behavior, pruning with pinned maps, and stretch-mode transitions. The public `CleanUpmapJob` comment references `TestTestOSDMap.cc`, suggesting unit coverage around upmap cleanup. Integration tests should also validate monitor quorum behavior through Paxos commit/reply callbacks and confirm that final map histories remain readable after trim/prune.
