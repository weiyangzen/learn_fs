# sources/distributed-fs/ceph/src/mds/MetricsHandler.h

## Purpose

`MetricsHandler.h` declares the per-rank metrics dispatcher for CephFS MDS. It is responsible for receiving client metrics, periodically forwarding aggregated updates to rank 0, tracking rank0 sequencing, and exposing quota and rank telemetry helpers.

## Important APIs, Types, and Members

- `class MetricsHandler : public Dispatcher` accepts client and MDS ping messages.
- Public methods are lifecycle (`init()`, `shutdown()`), session hooks (`add_session()`, `remove_session()`), MDS map hook (`notify_mdsmap()`), and `maybe_update_subvolume_quota()`.
- `HandlePayloadVisitor` dispatches boost/static-visitor style payload handling but intentionally aborts for `SubvolumeMetricsPayload`, because subvolume handling needs an unlock/relock pattern.
- `create_subv_perf_counter()` is declared for subvolume perf-counter creation.
- `lock` protects sequence state, client metric maps, subvolume buffers, quota cache, rank0 address, stopping flag, and rank telemetry.
- `next_seq` is assigned by rank0 pings; `last_updated_seq` tracks local update rounds.
- `client_metrics_map` maps client entity instance to `(last_update_seq, Metrics)`.
- `subvolume_metrics_map` maps subvolume path to client-reported aggregated IO metrics.
- `SubvolumeQuotaInfo` caches quota, used bytes, and activity time by subvolume inode number.
- `UnlockGuard` is an RAII helper for temporarily dropping the metrics lock during MDS operations.
- `RankTelemetry` holds `RankPerfMetrics` plus CPU sampling state.

## Control Flow

The header defines a collector with two inbound paths: `MClientMetrics` from clients and `MMDSPing` from rank 0. The periodic updater thread is private and feeds rank0 through `update_rank0()`. MDS map changes control `addr_rank0`; sequence reset is part of the public map-notification contract.

## State and Persistence Behavior

State is transient and process-local. The class publishes rank perf counters, but does not journal metadata or persist metrics. Its cached quota data is intentionally evicted when inactive. The sequence fields are local coordination state with rank 0 and are reset when rank0 disappears or changes address.

## Dependencies and Integration Points

The header depends on Ceph messenger dispatch, mutexes, `MDSPerfMetricTypes`, CephFS metric payload types, boost variant visitation, and MDS/session forward declarations. It integrates with session lifecycle code, client message dispatch, MDS map notifications, quota broadcast code in `MDCache`, and rank0 aggregation.

## Risks

- The explicit unlock guard is necessary but risky if callers assume the lock remains held across helper calls.
- The comment near `addr_rank0` contains a stray non-ASCII character, which is harmless for build behavior but can trip strict text tooling.
- `rank_perf_counters` is a raw pointer with lifecycle split between `init()` and `shutdown()`.
- The visitor pattern has a hard abort for subvolume payloads; future payload additions must choose the correct dispatch path.

## Test Signals

Contract tests should assert accepted message types, sequence reset on rank0 address changes, session lifecycle transitions, thread shutdown cleanup, and quota cache behavior. Concurrency-oriented tests should focus on paths that temporarily unlock around MDS calls.
