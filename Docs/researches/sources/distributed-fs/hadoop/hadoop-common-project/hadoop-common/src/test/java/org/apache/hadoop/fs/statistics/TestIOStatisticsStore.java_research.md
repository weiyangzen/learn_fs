# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/statistics/TestIOStatisticsStore.java

Purpose: Tests `IOStatisticsStore` mutable operations for gauges, min/max samples, mean samples, counters, JSON snapshot round trips, and evaluated map iteration.

Important APIs/types/functions: `iostatisticsStore`, `IOStatisticsStore`, `setGauge`, `incrementGauge`, `getGaugeReference`, `setMinimum`, `addMinimumSample`, `setMaximum`, `addMaximumSample`, `setMeanStatistic`, `addMeanStatisticSample`, `incrementCounter`, `snapshotIOStatistics`, `IOStatisticsSnapshot.serializer`, and assertion helpers.

Control flow: `setup` builds a store with one counter, gauge, min, max, and mean. Gauge tests cover positive/negative increments, direct reference reads, and unknown gauge no-op return. Minimum/maximum tests assert sample aggregation keeps lower/higher values and unknown samples do not fail. Mean tests set an initial mean and add a sample to produce two samples with sum ten. Round-trip test populates all stats, serializes a snapshot to JSON, deserializes, and verifies values. Counter tests cover unknown counter and ignored negative increments. `testForeach` creates a store with three counters and validates `forEach`, `keySet`, `values`, and `entrySet` evaluation.

State/persistence: Per-test in-memory statistics store; teardown logs state. JSON is in-memory only.

Dependencies/integration: Integrates mutable store implementation, lazy/evaluating maps, JSON snapshot serialization, and assertion utilities.

Risks: Unknown statistic operations are mostly asserted as no-throw/no-change, not exact internal state for every type. `testForeach` resets counters for entry iteration but does not assert the final entry iteration count/sum after reset.

Test signals: Exact values for gauges/min/max/mean/counters, ignored negative counter increments, JSON round-trip values, and evaluated-map key/value/entry collection behavior.
