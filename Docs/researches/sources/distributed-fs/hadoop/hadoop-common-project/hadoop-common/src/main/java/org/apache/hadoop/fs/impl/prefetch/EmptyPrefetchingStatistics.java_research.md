<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/EmptyPrefetchingStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/EmptyPrefetchingStatistics.java

## Purpose
Provides a singleton no-op implementation of `PrefetchingStatistics` for callers that do not want to publish IO statistics.

## Important APIs, Types, And Functions
`getInstance()` returns the singleton. All statistic methods are implemented as no-ops except `prefetchOperationStarted`, which returns a stub `DurationTracker`.

## Control Flow
There is no branching or mutable workflow. Callers receive a reusable object and can invoke every statistics callback without null checks.

## State And Persistence
Only a private static singleton exists. No counters are stored and no statistics persist.

## Dependencies And Integration Points
Used wherever prefetch components require a non-null `PrefetchingStatistics`. It depends on `IOStatisticsSupport.stubDurationTracker`.

## Risks
Using this in production disables visibility into prefetch latency, cache occupancy, eviction, executor wait time, and buffer memory accounting. That is acceptable only when statistics are intentionally unavailable.

## Test Signals
Verify singleton identity, no exceptions from all callback methods, and that returned duration trackers can be closed/failed safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/EmptyPrefetchingStatistics.java -->
