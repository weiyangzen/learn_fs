# sources/distributed-fs/ceph/src/mds/MetricAggregator.cc

## Purpose

`MetricAggregator.cc` implements the rank-0 MDS-side aggregator for metrics reported by every active MDS rank. It receives `MMDSMetrics` messages from peer ranks, validates that those reports correspond to its rank-ping sequence, converts client, subvolume, and rank telemetry into Ceph `PerfCounters`, and serves manager perf-query reports through `MgrClient`.

## Important APIs, Types, and Functions

- Local counter id enums define three counter families: aggregate client count, per-client metrics, and subvolume metrics.
- `MetricAggregator::init()` registers the rank-0 client-count perf counter, starts the `mds-ping` thread, installs manager query/report callbacks, and reads `subv_metrics_window_interval`.
- `shutdown()` stops the pinger thread and removes all owned `PerfCounters`.
- `ms_dispatch2()` handles `MSG_MDS_METRICS` from MDS peers only.
- `notify_mdsmap()` maintains `active_rank_addrs`, initializes `clients_by_rank`, culls vanished ranks, and resets ping state.
- `handle_mds_metrics()` is the main ingestion path. It checks `mds_pinger.pong_received(rank, seq)`, applies client refresh/remove updates, refreshes subvolume counters, and updates rank perf counters.
- `refresh_metrics_for_rank()` creates per-client labeled counters on first sight and updates both perf counters and `query_metrics_map`.
- `refresh_subvolume_metrics_for_rank()` maintains `SlidingWindowTracker<SubvolumeMetric>` per subvolume path, publishes averaged IOPS/throughput/latency/quota/usage counters, and removes stale trackers and query entries.
- `set_perf_queries()` and `get_perf_reports()` implement the mgr-facing dynamic perf-query contract.

## Control Flow

At startup rank 0 registers a low-cardinality `mds_client_metrics` counter and launches a periodic pinger. The pinger holds the aggregator lock while iterating `active_rank_addrs`, sends pings through `MDSPinger`, then sleeps outside the lock. MDS map updates add new active ranks and remove old ones. Removing a rank culls its clients, deletes its rank perf counters, and resets pinger state.

On `MMDSMetrics`, the aggregator locks, rejects stale or unordered reports via `MDSPinger`, then handles every client update. Refresh updates create or update `(client, rank)` perf counters; remove updates delete the per-client counters and query entries. Subvolume samples are accumulated into sliding windows and converted to per-second rates. Rank CPU/open-request telemetry is written into `mds_rank_perf` counters.

Manager perf queries are stored as `MDSPerfMetricQuery -> key -> counters`. Client keys are built from rank/client regex subkeys; subvolume keys are built from subvolume path and current MDS rank subkeys. `get_perf_reports()` serializes the current counters and marks lagging ranks as delayed.

## State and Persistence Behavior

This file is runtime state only, but it publishes persistent process telemetry through the perf-counter collection and mgr reports. State includes `clients_by_rank`, `client_perf_counters`, `subvolume_aggregated_metrics`, `subvolume_perf_counters`, `rank_perf_counters`, `active_rank_addrs`, and `query_metrics_map`. The journal is not touched. Shutdown is responsible for deleting all counters it created.

## Dependencies and Integration Points

Major dependencies are `MDSRank`, `MDSMap`, `MDSPinger`, `MgrClient`, `PerfCountersBuilder`, `MDSPerfMetricTypes`, `MMDSMetrics`, and Ceph messenger dispatch. It integrates with `MetricsHandler.cc`, which sends the `MMDSMetrics` reports, and with the manager daemon through `MgrClient::set_perf_metric_query_cb`.

## Risks

- Counter lifetime is manual; missed remove paths can leak labeled `PerfCounters`.
- `clients_by_rank.at(rank)` assumes `notify_mdsmap()` established the rank before metrics arrive.
- `remove_metrics_for_rank()` decrements the aggregate client count even when called during rank culling with `remove=false`; this relies on culling being called once per known client.
- The per-client opened-inodes perf counter is set from `total_inodes` in one path, which looks easy to confuse with `opened_inodes` and should be covered by tests.
- Subvolume-cardinality is path based, so high churn in subvolume paths can create many labeled counters until the sliding window ages them out.
- All query-map updates occur under one mutex; complex regex queries and many subvolume paths can make the aggregator hot.

## Test Signals

Useful tests exercise rank add/remove through `notify_mdsmap()`, stale ping sequence rejection, client refresh/remove updates, dynamic perf-query regex matching, stale subvolume eviction, rank perf counter removal, and shutdown with non-empty client/subvolume/rank counter maps. Integration tests should include at least two MDS ranks plus client metrics to verify that rank 0 alone owns aggregated rank counters.
