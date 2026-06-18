# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/DefaultMetricsMaster.java

## Purpose
`DefaultMetricsMaster` is the core master responsible for receiving client/worker metrics, maintaining cluster metrics, exposing the metrics master gRPC service, and registering derived throughput and multi-value aggregate gauges.

## Important APIs and Types
- Extends `CoreMaster`; implements `MetricsMaster` and `NoopJournaled`.
- Holds `Map<String, MultiValueMetricsAggregator> mAggregatorRegistry`.
- Holds `MetricsStore mMetricsStore`.
- Constructors set clock/executor and register aggregators.
- `registerThroughputGauge` creates bytes-per-minute gauges from counters and last clear time.
- `getServices` exposes `METRICS_MASTER_CLIENT_SERVICE`.
- `start(Boolean isLeader)` initializes metrics and starts cluster metric updater heartbeat only on leader.
- `clientHeartbeat` and `workerHeartbeat` asynchronously submit metrics to `MetricsStore`.
- `clearMetrics` clears store; `getMetrics` returns all metrics from `MetricsSystem`.
- Inner `ClusterMetricsUpdater` periodically calls `updateMultiValueMasterMetrics`.

## Control Flow
At construction, the master registers throughput gauges for read/write counters and creates a `SingleTagValueAggregator` per UFS operation. On start, it initializes metric keys, clears existing metrics, and, if leader, schedules a fixed-interval heartbeat. The updater fetches master metrics matching registered filters, lets each aggregator compute output values, and registers gauges for newly produced aggregate metric names. Heartbeat RPC handlers enqueue writes into the master executor instead of synchronously updating the store.

## State and Persistence
Metrics are in-memory and this master is `NoopJournaled`; metrics are cleared on start and via `clearMetrics`. Derived gauges live in the global `MetricsSystem` registry.

## Dependencies and Integration Points
Integrates with `CoreMaster`, `MetricsMasterClientServiceHandler`, `MetricsStore`, `MetricsSystem`, Dropwizard gauges, heartbeat framework, authentication interceptor, and Alluxio configuration for service thread count and update interval.

## Risks and Edge Cases
- Metrics updates are asynchronous; immediate reads after heartbeat may not include submitted metrics.
- Throughput gauge divides by uptime in minutes since last clear; for uptime <= 0 it returns the raw counter value.
- Gauges capture aggregator instances and read current aggregate values at scrape time.
- Non-leader masters do not start the cluster metrics updater.

## Test Signals
Tests should cover service registration with interceptor, leader-only heartbeat scheduling, client/worker heartbeat asynchronous storage, clear semantics, throughput gauge arithmetic, aggregate gauge creation, and no-op journaling expectations.
