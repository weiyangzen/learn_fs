# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsMasterTest.java

## Purpose
`MetricsMasterTest` verifies `DefaultMetricsMaster` behavior around throughput gauges and cluster metric aggregation. It checks that master-local counters and timers are translated into cluster-visible metrics on the manually scheduled metrics heartbeat.

## Important APIs, Types, and Functions
The fixture creates `DefaultMetricsMaster` with `MasterTestUtils.testMasterContext`, a `ManualClock`, and a constant executor-service factory. Tests use `registerThroughputGauge`, `addAggregator`, `MetricsSystem.counter`, `MetricsSystem.timer`, `MetricsSystem.getMetricValue`, `Metric.getMetricNameWithTags`, `SingleTagValueAggregator`, and `HeartbeatScheduler.execute`.

## Control Flow, State, and Persistence
`before` clears all metrics, builds a `MasterRegistry`, registers the metrics master, and starts it as leader. `testThroughputGauge` increments a master counter and advances the manual clock to assert per-minute throughput calculation. `testRegisteredAggregator` creates UFS-tagged master counters/timers and manually triggers `MASTER_CLUSTER_METRICS_UPDATER`. `testMultiValueAggregator` creates per-UFS counters and verifies distinct cluster metrics are created after heartbeat execution. State is in the global in-memory `MetricsSystem` registry.

## Dependencies and Integration Points
This test touches the master registry lifecycle, heartbeat scheduler, Alluxio metric naming/tag escaping, Dropwizard `Counter` and `Gauge`, and cluster aggregator implementations. It relies on `ManuallyScheduleHeartbeat` to make background aggregation deterministic.

## Risks
Global metric state can leak if setup/teardown is bypassed. Throughput values depend on the manual clock and cumulative counter deltas, so changes to gauge semantics can break expectations. The UFS operation test selects the first `MetricInfo.UfsOps` enum value, which keeps the test generic but ties it to enum stability.

## Test Signals
Passing tests show that throughput gauges are registered and compute expected rates, UFS operation aggregators merge counter and timer counts, and multi-value aggregation keeps separate values by tag. These are strong unit signals for master cluster metric publication.
