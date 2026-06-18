# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableMetrics.java

## Purpose
JUnit coverage for mutable metrics primitives in `org.apache.hadoop.metrics2.lib`: counters, gauges, rates, aggregated rates, stats, quantiles, inverse quantiles, and float gauges. It verifies snapshot naming, interval-vs-total accounting, numerical accuracy, concurrent aggregation, rollover behavior, and handling of no-change/empty windows.

## Important APIs, Types, And Functions
Uses `MetricsRegistry`, `MutableStat`, `MutableRates`, `MutableRatesWithAggregation`, `MutableQuantiles`, `MutableInverseQuantiles`, `MutableGaugeFloat`, `Quantile`, and `MetricsRecordBuilder`. `testSnapshot()` validates registry-created metric emission. `testMutableRates*()` covers protocol/interface-based and string-array initialization. `snapshotMutableRatesWithAggregation()` reads mocked counters/gauges to accumulate expected totals. Quantile tests inspect `previousSnapshot` and verify percentile gauges against allowed error.

## Control Flow
Tests create registries or metric instances, mutate them, snapshot to mocked builders, and assert emitted names/values with `MetricsAsserts` and Mockito. The many-thread aggregation test coordinates worker lifetimes with latches, takes snapshots while additions are in flight, then verifies totals after all and half of the workers have completed. Quantile rollover tests insert controlled samples across timed windows, sleep past the configured five-second interval, then assert emitted gauges.

## State And Persistence Behavior
State is in in-memory mutable metrics and their rolling/interval buffers. Aggregated rates depend on thread-local state being collected before worker objects disappear; the test explicitly keeps threads alive through snapshots. Quantiles retain a previous published snapshot after scheduled rollover. The registry persists metrics by name for the duration of each test only.

## Dependencies And Integration Points
Depends on Hadoop metrics2 test helpers, Mockito, Guava `Stats`, `SubjectInheritingThread`, and JUnit timeout support. It exercises the public surface used by metrics sources before data reaches sinks.

## Risks
Timed quantile sleeps can be slow or flaky on heavily loaded systems. The random sleep interleaving in the concurrency test can expose race bugs but also makes failures harder to reproduce, though it logs the seed. Snapshot naming is case-sensitive and tied to metrics2 capitalization conventions.

## Test Signals
Strong signals are exact counter/gauge names (`FooNumOps`, `FooAvgTime`, percentile gauge names), correct interval reset to zero, stable large-number means/stdevs, successful concurrent totals, and no missing data after some aggregation threads terminate.
