# sources/distributed-fs/ceph/src/mds/MetricAggregator.h

## Purpose

`MetricAggregator.h` declares the rank-0 dispatcher and state container used to aggregate CephFS MDS metrics. The class receives MDS-to-MDS metric messages, pings active ranks to drive sequence validation, owns perf counters for client/subvolume/rank metrics, and exposes manager perf reports.

## Important APIs, Types, and Members

- `class MetricAggregator : public Dispatcher` makes the aggregator a messenger dispatcher.
- Public lifecycle methods are `MetricAggregator(CephContext*, MDSRank*, MgrClient*)`, `init()`, and `shutdown()`.
- `notify_mdsmap(const MDSMap&)` updates the active-rank membership tracked by the pinger and culls removed ranks.
- `ms_dispatch2()` is the only dispatch hook with behavior; connection reset/refusal hooks are no-ops.
- `lock` protects all maps and the `stopping` flag. The header explicitly warns not to hold it while calling `send_message_mds()`.
- `clients_by_rank` maps rank to client instances so rank removal can delete all client metrics for that rank.
- `query_metrics_map` stores manager-configured `MDSPerfMetricQuery` data.
- `mds_pinger` plus `pinger` thread manages rank pings and delayed-rank detection.
- Perf-counter ownership is split across `m_perf_counters`, `client_perf_counters`, `subvolume_perf_counters`, and `rank_perf_counters`.
- Private helpers cover message handling, client refresh/remove, subvolume refresh, rank perf updates, rank culling, pings, query setup, and report generation.

## Control Flow

The header exposes a compact external contract: construct with MDS and manager dependencies, call `init()`, feed MDS map updates, dispatch messenger messages, then call `shutdown()`. All detailed behavior is private, making callers interact only through Ceph dispatcher and MDS map hooks.

## State and Persistence Behavior

All stored state is process-local and mutex-protected. The class owns raw `PerfCounters*` pointers and must remove/delete them. No metadata journal, object store, or on-disk state is modified by the class itself. Query state persists only until the manager sends a new config payload or the MDS shuts down.

## Dependencies and Integration Points

The declaration depends on Ceph messenger types, `Dispatcher`, `ceph::mutex`, perf counters, mgr metric types, `MDSPerfMetricTypes`, `mdstypes`, and `MDSPinger`. It is tightly coupled to `MetricAggregator.cc`, `MetricsHandler.cc`, manager perf queries, and MDS map change notification from `MDSRank`.

## Risks

- The class has mixed ownership styles: `MDSPinger` by value, `std::thread` by value, and several raw perf-counter pointers.
- The lock-order warning is important because rank-to-rank sends can re-enter MDS code that may need MDS locks.
- `stopping` is protected by `lock`; any future helper that reads it lockless would need care.
- The public no-op connection handlers mean connection resets do not directly clear rank state; rank cleanup depends on MDS map updates and pinger/report logic.

## Test Signals

Header-level contract tests should verify lifecycle idempotence expectations, dispatcher message acceptance only for `MSG_MDS_METRICS` from MDS peers, and that MDS map changes are the supported source of active-rank membership. Static analysis should flag raw perf-counter ownership and thread shutdown paths.
