# sources/distributed-fs/ceph/src/mon/MgrStatMonitor.cc

## Purpose

`MgrStatMonitor.cc` implements the monitor Paxos service that persists manager-reported cluster statistics: `PGMapDigest`, service map, progress events, health checks, and pool availability tracking. It also serves statfs and pool-stat client requests from the latest committed digest.

## Important APIs, Types, and Functions

Key functions are the constructor/destructor config observer registration, `get_tracked_keys()`, `handle_conf_change()`, `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `preprocess_report()`, `prepare_report()`, `preprocess_getpoolstats()`, `preprocess_statfs()`, `check_subs()`, `send_digests()`, `calc_pool_availability()`, `clear_pool_availability()`, `should_calc_pool_availability()`, and `update_logger()`.

## Control Flow and State

Only reports from the current active mgr gid are accepted; non-active mgr reports are ignored in preprocessing. `prepare_report()` decodes a pending PG digest from `MMonMgrReport`, swaps in report health checks, service map data, and progress events, then the Paxos commit path encodes digest, service map, progress events, pool availability, and health checks. `update_from_paxos()` decodes optional fields defensively, notifies subscribers, updates cluster log counters, notifies OSDMonitor about new PG digest data, and leader-side calculates pool availability when the configured interval has elapsed.

Pool availability state is guarded by `lock`. The calculation adds pools from `digest.pool_pg_unavailable_map`, removes pools missing from the digest or OSDMap, updates uptime/downtime/failure counters based on availability transitions, and copies live availability into `pending_pool_availability`.

## Dependencies and Integration Points

The service depends on `PaxosService`, `PGMapDigest`, `ServiceMap`, progress events, health check maps, `OSDMonitor`, `MgrMonitor`, `MMonMgrReport`, `MGetPoolStats`, `MStatfs`, `MServiceMap`, config observation, and cluster logger counters. Service-map subscriptions use the `"servicemap"` subscription type.

## Risks and Test Signals

Risks include accepting stale/non-active mgr reports, decoding older Paxos records missing progress or availability fields, racing config changes with availability updates, and incorrect uptime/downtime transitions. Tests should verify active gid filtering, statfs and pool-stats capability checks, fsid mismatch drops, removed-pool statfs drops, service-map subscriptions, optional decode compatibility, config toggle reset behavior, and cluster logger counter updates from digest state.
