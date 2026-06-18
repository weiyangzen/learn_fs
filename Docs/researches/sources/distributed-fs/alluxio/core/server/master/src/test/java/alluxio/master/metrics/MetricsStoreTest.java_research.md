# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsStoreTest.java

## Purpose
`MetricsStoreTest` validates `MetricsStore`, the component that accepts worker and client metric reports and updates cluster-level counters. It covers worker metrics, client metrics, UFS-tagged worker metrics, and clearing/reset time behavior.

## Important APIs, Types, and Functions
The test fixture uses `MetricsStore.initMetricKeys`, `putWorkerMetrics`, `putClientMetrics`, `clear`, and `getLastClearTime`. It builds `Metric` objects through `Metric.from`, uses `MetricKey` constants for worker/client/cluster metrics, and derives tagged metric names through `Metric.getMetricNameWithTags` plus `MetricInfo.TAG_UFS`.

## Control Flow, State, and Persistence
`before` resets the global `MetricsSystem`, creates a `MetricsStore` with `SystemClock`, and initializes metric keys. Each test submits synthetic metric batches for hosts or clients, then reads the corresponding cluster counter. UFS metrics are grouped by escaped UFS URI and also update all-UFS aggregate counters. `clearAndGetClearTime` records the previous clear time, writes metrics, sleeps briefly to avoid same-millisecond timestamps, clears the store, and asserts counters reset and clear time advances.

## Dependencies and Integration Points
The store integrates with Alluxio metric naming, Dropwizard counters via `MetricsSystem`, gRPC `MetricType`, and URI escaping for tagged UFS metrics.

## Risks
The tests rely on global in-memory metric state and real clock progression. `Thread.sleep(10)` reduces but does not eliminate timing sensitivity on extremely coarse or overloaded environments. Metric-name parsing is implicit in the store under test, so renamed metric keys can invalidate expectations.

## Test Signals
Passing tests show that metrics from multiple workers and clients are accumulated correctly, UFS metrics are split by UFS tag and summed globally, and `clear` resets cluster counters while updating the clear timestamp.
