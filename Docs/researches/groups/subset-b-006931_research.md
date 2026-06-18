# Research: subset-b-006931

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/OSDMonitor.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/OSDMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PGMap.cc -->
# sources/distributed-fs/ceph/src/mon/PGMap.cc

## Purpose

`PGMap.cc` implements monitor-side aggregation, serialization, formatting, command handling, health reporting, and maintenance logic for placement group and OSD statistics. It turns raw `pg_stat_t`, `osd_stat_t`, and per-pool statfs reports into cluster summaries, per-pool statistics, monitor health checks, PG query responses, and reweight-by-utilization recommendations.

The file has two closely related layers. `PGMapDigest` is the compact aggregate representation used for summaries and encoded digests. `PGMap` owns full per-PG/per-OSD maps and derives the digest fields. This split lets monitor consumers get lightweight summary data without always carrying the full PG map.

## Important APIs and Functions

Encoding APIs include `PGMapDigest::encode/decode`, `PGMap::encode/decode`, and `PGMap::encode_digest`. Digest encoding requires `SERVER_NAUTILUS` features and writes aggregate PG counts, pool sums, OSD sums, state counts, OSD PG counts, last OSD stat sequence numbers, moving deltas, available space by CRUSH rule, purged snaps, OSD class sums, and unavailable PG maps. Full PGMap encoding writes version, raw `pg_stat`, raw `osd_stat`, last OSDMap/PG scan epochs, timestamp, and per-OSD pool statfs before recalculating aggregates on decode.

Mutation APIs center on `PGMap::apply_incremental`. It asserts monotonic versioning, updates or removes PG stats, applies per-pool statfs updates, updates/removes OSD stats, maintains derived counters through `stat_pg_add`, `stat_pg_sub`, `stat_osd_add`, and `stat_osd_sub`, rolls global and per-pool deltas, deletes removed-pool aggregate state, and updates `last_osdmap_epoch`/`last_pg_scan`.

Aggregate rebuild helpers include `calc_stats`, `calc_purged_snaps`, `calc_osd_sum_by_class`, `get_unavailable_pg_in_pool_map`, `get_rule_avail`, and `get_rules_avail`. Query and dump helpers include formatter and stream variants for full PG maps, basic summaries, PG progress, pool stats, OSD stats, ping times, stuck PGs, filtered PG stats, OSD perf stats, and blocked-by summaries.

`process_pg_map_command` is the monitor command dispatcher for PGMap-related read commands. It normalizes legacy aliases such as `pg dump_json`, `pg dump_pools_json`, `pg ls-by-primary`, `pg ls-by-osd`, and `pg ls-by-pool`, then handles `pg stat`, `pg getmap`, `pg dump`, `pg ls`, `pg dump_stuck`, `pg debug`, `osd perf`, and `osd blocked-by`.

`PGMapUpdater::check_osd_map` reconciles PGMap state after OSDMap changes. It removes stats for deleted OSDs, zeroes stats for out OSDs, clears op queue age histograms for down/up transitions, removes PGs from deleted pools, creates placeholder stats for new PGs after pool expansion, removes merged PGs after PG count shrink, and drops pending updates for old PGs. `PGMapUpdater::check_down_pgs` marks PGs stale when their acting primary is down, either by scanning all PGs or by consulting `pg_by_osd` for selected OSDs.

`reweight::by_utilization` calculates proposed OSD reweights based on either raw storage utilization or PG distribution. It validates thresholds and minimum data volume/PG count, computes average and overload utilization, sorts OSDs by absolute deviation from average, caps changes by `max_changef` and `max_osds`, optionally avoids increasing weights, applies the proposed weights to a temporary OSDMap, and summarizes the expected mapping change.

## Control Flow

The normal update path is incremental. OSDs and monitor services build `PGMap::Incremental` objects, then `apply_incremental` mutates the full map and updates soft aggregate state in the same pass. Existing PG stats are subtracted before replacement and added after replacement, preserving global state counters, pool sums, PG-by-OSD indices, creating-PG indices, blocked-by counters, active/unknown counts, and state histograms. OSD stat updates follow the same subtract/replace/add pattern.

Delta calculations are smoothing windows. `apply_incremental` computes global deltas only after an existing timestamp and non-zero old sum are available. `update_delta`, `update_one_pool_delta`, and `update_pool_deltas` store timestamped deltas in bounded lists controlled by `mon_stat_smooth_intervals`, clamp very long gaps using `mon_delta_reset_interval`, and maintain aggregate rate numerators plus timestamp denominators for later summary output.

Digest generation performs late derived work: available bytes by CRUSH rule are calculated from current OSDMap weights and OSD free space, OSD class sums are rebuilt from CRUSH device class names, purged snap ranges are intersected across known PGs per pool, and unavailable PGs are determined using stuck thresholds and unfound-object checks.

Health reporting first converts PG state bits into consequence categories such as availability, degraded redundancy, backfill full, damage, and recovery full. It optimizes by using `num_pg_by_state` before scanning all PGs, applies stuck thresholds for delayed states, records limited details, then emits Ceph health checks. It then layers in scrub errors, large omap objects, cache pool size warnings, too few/many PGs, too few OSDs, slow heartbeat pings, OSD repair counts, PG sizing skew, pool quota warnings, misplaced/unfound objects, legacy slow/stuck request warnings, BlueStore/object-store alerts, missed scrub/deep-scrub deadlines, missing pool application metadata, and slow snap trimming.

## State and Persistence Behavior

`PGMap` is persistable through Ceph buffer encoding. The encoded full state is raw enough to reconstruct all derived fields via `calc_stats`, while digest encoding is optimized for summaries and external consumers. Versioning is explicit: `apply_incremental` requires `inc.version == version + 1`, and `PGMap::Incremental` carries its own version, OSDMap epoch, PG scan epoch, timestamp, PG updates/removals, OSD stat updates/removals, and per-OSD pool statfs updates.

Most aggregate members are soft state: `pg_pool_sum`, `pg_sum`, `osd_sum`, `num_pg_by_state`, `num_pg_by_osd`, `pg_by_osd`, `blocked_by_sum`, `creating_pgs`, moving deltas, and unavailable maps are derived from raw reports and config/OSDMap context. The code nevertheless maintains them incrementally for performance, so subtract/add symmetry and erase-on-zero behavior are correctness-critical.

Per-pool statfs is stored separately from PG stats and folded into `pg_pool_sum`. OSD removal also removes related `(pool, osd)` statfs entries and subtracts them from pool aggregates. Pool deletion calls `deleted_pool` to purge pool statfs, pool sums, state counters, and per-pool deltas.

## Dependencies and Integration Points

The implementation depends on monitor health types, Ceph config, clocks, formatters, text tables, feature bits, health constants, OSD map and CRUSH wrappers, mempool containers, and PG/OSD stat encoders from `osd_types.h`. It is called by monitor command handlers, manager/status paths, OSDMonitor PGMap update logic, and tools that need `ceph df`, `ceph pg dump`, `ceph osd perf`, stuck PG lists, or reweight calculations.

The code integrates tightly with `OSDMap`. Pool names, CRUSH rules, full ratios, raw-used rates, device classes, OSD up/down/out state, pool existence, PG counts, quota settings, application metadata, and release requirements all alter PGMap output or health behavior.

## Risks and Edge Cases

The incremental aggregate maintenance is the most fragile part. A missing subtract, double add, or missed erase can corrupt monitor health, `ceph df`, reweight decisions, or PG query results until a full decode/recalc path runs. Edge cases include unknown PG state (`state == 0`), pools disappearing while PG updates are pending, per-pool statfs for deleted OSDs, and acting/up sets that overlap.

Several rate computations divide by `utime_t` deltas. The code mitigates negative counters by flooring deltas to zero and skips unsynchronized first samples, but zero or tiny deltas, stale OSD reports, and counter resets remain important test cases.

Health checks depend on config thresholds and limited detail counts. Regressions can be subtle because changes affect user-visible health codes and severities, not just internal state. Slow ping handling also has a likely typo-risk pattern where front-side `improving` compares the third front sample to `back_pingtime[2]`, so tests around heartbeat detail ordering are valuable.

`reweight::by_utilization` must avoid unsafe recommendations when there are too few PGs or too little byte data. It also needs robust behavior for zero CRUSH weights, out OSDs, missing acting OSDs, and `util == 0` when considering weight increases.

## Test Signals

Useful tests include encode/decode round trips for `PGMapDigest`, `PGMap`, and `Incremental`; apply-incremental replacement/removal paths; pool deletion cleanup; per-pool statfs aggregation; OSD out/down stat handling; stale PG marking after acting primary down; digest available-space calculations for CRUSH rules; stuck PG filtering; command output for formatter and plaintext modes; health checks for every emitted health code; and reweight refusal/recommendation cases. Existing `generate_test_instances` methods provide seed objects for encoder tests, but behavioral tests need constructed OSDMap and PG stat scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PGMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PGMap.h -->
# sources/distributed-fs/ceph/src/mon/PGMap.h

## Purpose

`PGMap.h` declares the monitor data model for placement group and OSD statistics. It separates compact aggregate state (`PGMapDigest`) from the full mutable PG map (`PGMap`) and declares the command, updater, and reweight interfaces implemented in `PGMap.cc`.

The model is used by monitors to answer status and admin commands, produce health checks, track PG creation/stuckness, compute pool and cluster storage summaries, and reconcile PG/OSD stats after OSDMap changes.

## Important APIs, Types, and Members

`PGMapDigest` contains aggregate state: OSD stat sequence numbers, available space by CRUSH rule, PG/OSD counts, active and unknown PG counts, per-pool sums, global PG and OSD sums, OSD class sums, PG counts by state/pool/OSD, unavailable PGs by pool, purged snap intervals, and moving delta state for global and per-pool rates. It provides summary printers, recovery/client/cache IO rate helpers, pool free-space calculation, `ceph df`-style dump helpers, statfs conversion, encode/decode/dump, and test instances.

`PGMapDigest::pg_count` stores acting, up-not-acting, and primary PG counts for one OSD. It has inline encode/decode/dump and test instance support, and is encoded through `WRITE_CLASS_ENCODER`.

`PGMap` extends `PGMapDigest` with full state: `version`, `last_osdmap_epoch`, `last_pg_scan`, `osd_stat`, `pg_stat`, and `pool_statfs`. It also owns derived soft indexes such as `pg_by_osd`, `blocked_by_sum`, `pg_sum_deltas`, `num_pg_by_pool_state`, creating-PG sets, and creating-PG-by-OSD epoch maps.

`PGMap::Incremental` is the update carrier. It holds the target version, PG stat updates/removals, OSDMap and PG scan epochs, timestamp, per-OSD pool statfs updates, private OSD stat updates/removals, and helpers to update, zero, clear, or remove OSD stats. `stat_osd_down_up` is specialized to clear `op_queue_age_hist` for OSD down/up transitions while preserving other known stats.

The public PGMap API includes accessors, `apply_incremental`, full aggregate recalculation, PG/OSD add/sub helpers, purged snap and OSD class calculations, full and digest encoding, JSON/plain dump methods, stuck PG filtering, OSD perf and blocked-by output, filtered PG listing, parentage lookup, health check generation, and summary printing.

`process_pg_map_command` exposes PGMap read commands to monitor command handling. `PGMapUpdater` declares static reconciliation helpers for OSDMap changes and down PG marking. The `reweight` namespace declares `by_utilization`, the admin helper for generating OSD reweight proposals.

## Control Flow and State Behavior

The design expects callers to maintain raw `pg_stat`, `osd_stat`, and `pool_statfs` through ordered incrementals. `apply_incremental` updates the raw maps and keeps the inherited digest aggregates current. Full decode reconstructs derived state with `calc_stats`, which is the recovery path if incremental soft state is absent.

The digest APIs treat some data as context-dependent. Available space by rule requires the current OSDMap; OSD class sums require CRUSH class lookup; purged snap intersections depend on all known PGs for a pool; unavailable PG maps depend on current stuck thresholds and PG states. That is why `PGMap::encode_digest` exists separately from plain `PGMapDigest::encode`.

Dump and summary methods are dual-mode: most accept either a `Formatter` for structured output or an `ostream`/`stringstream` for CLI text. This is important for Ceph commands that share computation but expose JSON and human-readable modes.

## Dependencies and Integration Points

The header depends on Ceph buffer encoding, `ceph_statfs`, command parsing, formatter interfaces, OSD stat types, mempool containers, monitor types, and `health_check_map_t`. It references `OSDMap` without including all monitor service machinery, keeping the PGMap model reusable by monitor command and health paths.

Integration is primarily with `OSDMonitor` and monitor command dispatch, but also with the manager/status surface, health reporting, CRUSH/OSDMap storage calculations, and admin reweight flows. The `WRITE_CLASS_ENCODER_FEATURES` macros make the types part of Ceph's versioned wire/store encoding contract.

## Risks and Edge Cases

Because `PGMap` inherits mutable aggregate fields from `PGMapDigest`, callers must understand which fields are raw state and which are derived. Direct mutation of `pg_stat`, `osd_stat`, or aggregate containers outside the declared add/sub/apply paths can break invariants. The private OSD update fields in `Incremental` reduce this risk for OSD stat removals and replacements.

Pool and OSD IDs are signed in several maps, while counts and states are often unsigned or bitmasks. Tests should cover negative/system pool filtering, unknown PG state zero, high OSD IDs that resize `osd_last_seq`, and erase-on-zero behavior for state maps. Feature-gated encoding is another compatibility-sensitive area.

## Test Signals

The header exposes `generate_test_instances` for digest, PG count, incremental, and full PGMap types, which are intended for encoder tests. Additional compile/API tests should validate command dispatcher linkage, health check construction, `PGMapUpdater` use with OSDMap changes, and reweight output contracts. Behavioral tests should verify that public accessors such as `get_num_pg_by_osd`, `get_pool_free_space`, `get_statfs`, and `definitely_converted_snapsets` remain consistent after incrementals and decode/recalc.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/PGMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Paxos.cc -->
# sources/distributed-fs/ceph/src/mon/Paxos.cc

## Purpose

`Paxos.cc` implements the Ceph monitor Paxos state machine used by monitor services to commit ordered versions of control-plane state. It handles leader recovery, proposal numbering, collect/last exchange, begin/accept/commit, state sharing to lagging peers, leases for readable/writeable service state, trimming, shutdown/restart, and service-facing read/write APIs.

This is not a generic library implementation: it is tightly integrated with `Monitor`, `MonitorDBStore`, `MMonPaxos`, monitor elections, timer events, perf counters, and service transactions. Each committed version stores an encoded monitor DB transaction that can be replayed into the local store.

## Important APIs and Functions

Initialization APIs are `init`, which loads `last_pn`, `accepted_pn`, `last_committed`, and `first_committed` from stable storage, and `init_logger`, which registers Paxos perf counters for leader/peon starts, refreshes, begin/commit/collect latencies, timeouts, state sharing, and proposal number allocation. `dump_info` emits the core persistent counters.

Phase 1 is `collect` on the leader and `handle_collect` on peons. The leader enters recovering state, discovers any local uncommitted value at `last_committed + 1`, chooses a new globally unique proposal number via `get_new_proposal_number`, sends `OP_COLLECT` to quorum peers, and sets a collect timeout. Peons accept higher proposal numbers by persisting `accepted_pn`, reply with `OP_LAST`, share committed state if the leader is behind, and include any accepted-but-uncommitted value and its pending proposal number.

State catch-up is handled by `share_state` and `store_state`. `share_state` reads committed version bufferlists from the monitor store into an outgoing message. `store_state` takes received version bufferlists, filters them to the contiguous range after local `last_committed`, writes each version, decodes each embedded transaction into the same store transaction, advances `last_committed`, refreshes `first_committed`, and clears obsolete uncommitted tracking.

The leader handles `OP_LAST` in `handle_last`: it records peer committed ranges, bootstraps if version ranges are incompatible, stores any shared committed state, sends commits to lagging peers, retries collection if a peer reports a higher accepted proposal number, learns the highest-numbered uncommitted value, and either reproposes that value or becomes active and extends leases after all quorum members respond.

Phase 2 starts with `begin`. The leader asserts it has enough collected responses, records local acceptance, wraps the initial base case if `last_committed == 0`, persists the pending value under the next version plus `pending_v`/`pending_pn`, sends `OP_BEGIN` to peers, and sets an accept timeout. Peons handle `OP_BEGIN` by rejecting stale proposal numbers, persisting the pending value and pending proposal metadata, entering updating state, cancelling the lease, and replying with `OP_ACCEPT`.

Commit flow is `handle_accept`, `commit_start`, `commit_finish`, and `handle_commit`. The leader waits for every quorum member, not just a bare majority, before committing, because peers may still be sharing stale state. `commit_start` writes `last_committed + 1`, decodes and appends the proposed transaction to the local store transaction, queues it asynchronously, and moves to writing state. `commit_finish` runs after store completion, advances in-memory `last_committed`, refreshes `first_committed`, sends `OP_COMMIT` with the committed value to peers, clears `new_value`, refreshes services, runs commit finishers, extends leases, finishes the round, and triggers trim or pending proposals. Peons process `OP_COMMIT` by `store_state` and refresh.

Lease APIs are `extend_lease`, `handle_lease`, `handle_lease_ack`, `lease_ack_timeout`, `reset_lease_timeout`, `lease_timeout`, and `lease_renew_timeout`. Leaders broadcast lease expirations tied to `last_committed`, collect ACKs and feature maps from all quorum members, and renew before expiration. Peons accept leases only if they are peons and `last_committed` matches, update `lease_expire`, enter active state, ACK with feature maps, reset timeout, and release active/readable waiters.

Service-facing APIs include `is_readable`, `read`, `read_current`, `is_lease_valid`, `is_writeable`, `get_pending_transaction`, `queue_pending_finisher`, `trigger_propose`, and `propose_pending`. Services build one pending monitor DB transaction, queue finishers, and ask Paxos to propose when active and unplugged. `propose_pending` encodes the transaction, swaps pending finishers into committing finishers, enters updating state, and starts `begin`.

Lifecycle APIs include `trim`, `cancel_events`, `shutdown`, `leader_init`, `peon_init`, `restart`, `reset_pending_committing_finishers`, `dispatch`, and `is_consistent`. `dispatch` verifies monitor role/source sanity and routes `MMonPaxos` opcodes to handlers.

## State and Persistence Behavior

Stable keys include `last_pn`, `accepted_pn`, `last_committed`, `first_committed`, numeric committed-version keys under the Paxos service name, and pending proposal metadata `pending_v`/`pending_pn`. Accepted but uncommitted values are intentionally persisted before peer acknowledgement so a later leader can learn and repropose them.

Committed version values are encoded `MonitorDBStore::Transaction` bufferlists. Applying a commit writes the version bufferlist and decodes/appends its transaction operations atomically, so local service state and the Paxos log advance together. The initial commit additionally sets `first_committed` to 1 in the wrapped transaction.

Timers are part of the correctness model. Collect, accept, lease ACK, lease, and renew timers cause fresh elections or lease extension. `restart` flushes the store if the state was writing to avoid losing async commit completion under a state transition. `shutdown` waits for in-progress queued commits before cancelling contexts and removing perf counters.

Trimming removes old committed version keys from `first_committed` up to a bounded end based on `paxos_min` and `paxos_trim_max`, updates `first_committed`, optionally compacts the store range, and queues a finisher to clear the `trimming` flag. Trimming is only triggered after rounds finish and `should_trim` is true.

## Dependencies and Integration Points

The implementation depends on `Paxos.h`, `Monitor`, `MonMap`, `MMonPaxos`, monitor DB transactions, monitor timers, monitor elections/bootstrap, session feature maps, perf counters, Ceph clocks, and formatter/debug infrastructure. It calls `mon.refresh_from_paxos` after committing or storing state so each PaxosService can update from the committed store.

Monitor role state is central. Leaders call `collect`, `begin`, `commit_start`, and `extend_lease`; peons handle collect/begin/commit/lease messages. Bootstrap/election is the recovery answer for incompatible trim ranges, proposal conflicts, collect/accept timeouts, and lease failures.

## Risks and Edge Cases

The highest-risk behavior is persistence ordering. Proposal numbers and accepted values must hit stable storage before replies, and committed transactions must atomically update both Paxos metadata and service state. Any change that weakens this can violate Paxos safety after crashes or leader changes.

Version range compatibility is another critical edge. If a peer's `first_committed` is beyond the local `last_committed + 1`, or if a peon is too far behind the leader's trim floor, the code bootstraps rather than trying to fill an impossible gap. Trimming policies must preserve enough history for normal catch-up.

The leader waits for all quorum members to accept before commit, even though the log message says "got majority"; this is a deliberate stale-state avoidance tradeoff. Changing this behavior requires an explicit lease revocation/catch-up design. Lease handling is also sensitive to clock skew, lag, and message timestamps; `warn_on_future_time` only warns and does not correct time.

Async store commits interact with locks and shutdown. `C_Committed` reacquires `mon.lock`, aborts if shutdown, and otherwise calls `commit_finish`. The shutdown path adopts the already-held lock and waits for `commits_started` to drain, so lock ownership assumptions are important.

## Test Signals

Tests should cover proposal number monotonicity and rank uniqueness, local recovery of pending uncommitted values, peon rejection of stale proposal numbers, leader retry after higher peer proposal number, state sharing to lagging peers, bootstrap on trimmed gaps, initial commit behavior, async commit completion, lease ACK/timeout/renew paths, read/write gating by active state and lease validity, trimming boundaries, restart while writing, and shutdown with queued commits. Fault-injection hooks using `paxos_kill_at` are explicit test signals for crash points through collect, begin, accept, commit, and refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Paxos.cc -->
