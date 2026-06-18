# sources/distributed-fs/ceph/src/mon/MgrStatMonitor.h

## Purpose

`MgrStatMonitor.h` declares the monitor service that stores and serves mgr-reported PG, service, progress, health, and pool availability statistics. It also exposes lightweight accessors used by monitor status, statfs, and dump paths.

## Important APIs, Types, and Functions

Live state includes `version`, `PGMapDigest digest`, `ServiceMap service_map`, progress events, and pool availability. Pending Paxos state mirrors those fields as `pending_digest`, `pending_health_checks`, `pending_progress_events`, `pending_service_map_bl`, and `pending_pool_availability`. Public APIs include report preprocessing/preparation, statfs and poolstats preprocessing, subscription checks, digest sending, logger updating, pool availability calculation/clear/update gating, digest/statfs/pool-stat accessors, and config observer methods.

## Control Flow and State

The class is both a `PaxosService` and an `md_config_obs_t`. The mutex protects availability tracking and config-derived fields. `enable_availability_tracking`, `pool_availability_update_interval`, and `pool_availability_last_updated` determine whether availability scores are updated from the current digest. `get_trim_to()` keeps only a small history because old mgrstat states are not normally needed.

## Dependencies and Integration Points

Dependencies include `ceph_mutex`, `Context`, `PaxosService`, `PGMap`, `ServiceMap`, monitor subscriptions, config proxy callbacks, and statfs structures. Consumers use `get_service_map()`, `get_progress_events()`, `get_pool_stat()`, `get_digest()`, `get_pool_availability()`, `get_statfs()`, `dump_info()`, `dump_cluster_stats()`, and `dump_pool_stats()`.

## Risks and Test Signals

The header exposes references to live maps, so callers must respect monitor threading assumptions. Availability defaults are read from global config at construction and then updated by observer callbacks. Tests should cover construction/destruction observer registration, pending/live state separation, accessors on missing pools, availability config changes, and formatting helpers.
