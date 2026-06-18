<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RetryCacheMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RetryCacheMetrics.java

## Purpose
`RetryCacheMetrics` publishes counters for Hadoop IPC retry-cache activity.

## Important APIs, Types, And Functions
- `create(RetryCache cache)` registers a source named `RetryCache.<cacheName>`.
- Counters: `cacheHit`, `cacheCleared`, `cacheUpdated`.
- Incrementers and getters expose current counter values.

## Control Flow
Construction initializes a registry name from the retry cache. The static factory registers the instance. Callers increment counters on retry-cache events.

## State And Persistence
Metrics counters live in memory and are exported through metrics2; no durable persistence.

## Dependencies And Integration Points
Depends on `RetryCache`, metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, and `MutableCounterLong`.

## Risks And Edge Cases
There is no local `shutdown`; lifecycle must be handled elsewhere or source names can collide in repeated tests. Counter fields are injected/initialized by metrics2 registration.

## Test Signals
Retry-cache tests should verify counter increments and registered source naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/RetryCacheMetrics.java -->
