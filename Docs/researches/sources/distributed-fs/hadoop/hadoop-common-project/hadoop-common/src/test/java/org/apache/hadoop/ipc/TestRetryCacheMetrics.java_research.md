# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCacheMetrics.java

Purpose: verifies retry cache metrics names and live counter updates.

Important APIs/types/functions: `RetryCache`, `RetryCacheMetrics`, `MetricsRecordBuilder`, `MetricsAsserts.getMetrics()`, and counters `CacheHit`, `CacheCleared`, `CacheUpdated`.

Control flow: creates a retry cache named `TestRetryCacheMetrics`, checks the metrics record name is `RetryCache.TestRetryCacheMetrics`, then verifies initial counters are zero. It calls `incrCacheHit()`, `incrCacheCleared()`, and `incrCacheUpdated()` on the metrics object and checks expected counter values after each update.

State and persistence behavior: metrics state is in-memory in Hadoop metrics2. The retry cache object owns a metrics source. No persistent state.

Dependencies and integration points: covers the metric naming contract and counter exposure consumed by monitoring systems.

Risks and test signals: focused signal for metrics regressions. Because metric sources can be global, duplicate names or leaked sources in nearby tests could affect this if lifecycle behavior changes.
