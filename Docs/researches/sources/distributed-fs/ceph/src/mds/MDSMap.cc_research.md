# sources/distributed-fs/ceph/src/mds/MDSMap.cc

## Purpose

`MDSMap.cc` implements the CephFS MDS map data model: daemon/rank state reporting, compatibility feature sets, health summaries, versioned encoding/decoding, cluster availability, state-transition validation, pool/rank helpers, required client feature derivation, and balancer rank-mask parsing.

## Important Functions And Control Flow

Compatibility helpers build all/default/base/pre-v16.2.5 `CompatSet` values. `mds_info_t::dump`, `dump(std::ostream&)`, and `human_name` render per-daemon state. `MDSMap::dump`, `print`, `print_summary`, `dump_flags_state`, and `print_flags` expose map contents: epoch, flags, features, timestamps, pools, ranks, failed/damaged/stopped sets, daemon info, balancer settings, standby counts, and quiesce DB membership.

Health APIs include legacy `get_health` and structured `get_health_checks`. They report damaged ranks, degraded filesystems, online MDS count below `max_mds`, all-down filesystems, multi-MDS with old snapshots, laggy daemons, and deprecated inline data.

Encoding is heavily versioned. `mds_info_t::encode_versioned` selects struct version based on peer features and encodes addrs, laggy state, export targets, MDS features, join fscid, flags, and compat. `MDSMap::encode` has legacy branches for peers without `CEPH_FEATURE_PGID64` or `CEPH_FEATURE_MDSENC`, then the modern `ENCODE_START(5,4)` form with extended version `ev=19`. `decode` mirrors these versions, provides defaults for older fields, converts old snap booleans to feature flags, derives required client features for older encodings, and bootstraps missing daemon compat from map compat.

Query helpers include `is_cluster_available`, `get_state_gid`, `get_state`, `get_gid`, `get_info`, `state_transition_valid`, `check_health`, `is_data_pool`, `find_mds_gid_by_name`, `get_num_mds`, `get_up_mds_set`, `add_data_pool`, `remove_data_pool`, `get_up_features`, `get_recovery_mds_set`, `get_mds_set_lower_bound`, `get_mds_set`, `get_standby_replay`, `is_followable`, `is_laggy_gid`, `is_degraded`, address/rank/incarnation helpers, `set_min_compat_client`, and rank-mask methods.

## State And Persistence Behavior

The encoded MDS map is persistent monitor-distributed cluster state. It records feature compatibility, filesystem enablement/name, pools, rank membership, daemon info by global id, failed/damaged/stopped ranks, required client features, balancer configuration, and qdb cluster fields. Decode sanitizes old layouts and inserts `MDS_FEATURE_INCOMPAT_INLINE` for compatibility during transition. `sanitize` removes data pools that no longer exist according to an external pool predicate.

## Dependencies And Integration Points

The file depends on `MDSMap.h`, CephFS feature helpers, `Formatter`, monitor health-check types, and Ceph encoding. `MDSDaemon` decodes maps from `MMDSMap` and validates compat before processing. Clients use availability and address/rank queries; monitors use health/check and state-transition logic.

## Risks And Test Signals

Risks include wire-compatibility regression, incorrect defaults for old maps, health false positives/negatives, invalid state transitions, and rank-mask parsing mistakes. Tests should round-trip every supported encoding branch, decode old map fixtures, validate transition tables, exercise availability with empty/damaged/laggy/active states, check health checks for each degraded condition, sanitize missing pools, compute up-feature intersections, and parse `bal_rank_mask` values including `all`, `-1`, `0`, `0x0`, valid hex, invalid hex, oversize masks, and all-zero masks.
