# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStore.java

Purpose: mutable statistics store contract combining IOStatistics, setter, aggregation, and duration tracking capabilities.

Important APIs, types, and functions: counter/gauge/min/max increments, sample methods, `reset()`, atomic reference getters, `getMeanStatistic()`, timed operation helpers, and default `incrementCounter(key)` and `addSample()`.

Control flow: implementations update registered statistic entries, ignore unknown keys where documented, and provide `DurationTrackerFactory.trackDuration()` through the inherited factory interface. `addSample()` updates count, mean, max, and min for a single key.

State and persistence: no state in the interface. Implementations usually hold atomics and mean objects in memory; snapshots are needed for persistence.

Dependencies and integration points: extends `IOStatistics`, `IOStatisticsSetters`, `IOStatisticsAggregator`, and `DurationTrackerFactory`. Used by filesystem and stream implementations as their core mutable metrics sink.

Risks and test signals: updates across count/mean/min/max are explicitly not atomic as a group. Tests should cover unknown key policy, reference getter exceptions, duration tracker integration, reset, aggregation, and concurrent updates.
