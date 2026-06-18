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
