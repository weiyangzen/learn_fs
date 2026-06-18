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
