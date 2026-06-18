<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/DecayRpcSchedulerDetailedMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/DecayRpcSchedulerDetailedMetrics.java

## Purpose
Publishes per-priority queue and processing time metrics for `DecayRpcScheduler`/FairCallQueue deployments.

## Important APIs, Types, And Functions
- Metrics source context `decayrpcschedulerdetailed`.
- `create(String ns)` registers the metrics source under `DecayRpcSchedulerDetailedMetrics.<ns>`.
- `init(int numLevels)` creates one queue metric and one processing metric name per priority level.
- `addQueueTime(int priority, long queueTime)` and `addProcessingTime(int priority, long processingTime)` add samples.
- `shutdown()` unregisters the metrics source.

## Control Flow
Creation builds a `MetricsRegistry` tagged by port/namespace and registers with `DefaultMetricsSystem`. `init` precomputes names and initializes `MutableRatesWithAggregation`. Add methods use the supplied priority as an array index into the precomputed names.

## State And Persistence
Holds metrics registry/name and arrays of metric names in memory. Exported metrics are runtime instrumentation only.

## Dependencies And Integration Points
Depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, and `MutableRatesWithAggregation`. Integrated with scheduler code that knows priority level indexes.

## Risks And Edge Cases
`init` must be called before adding samples. The add methods trust `priority` as a zero-based array index, while display names use `priority + 1`; incorrect caller indexing can throw or misattribute metrics. Sources should be unregistered on shutdown to avoid duplicate registrations in tests or restarts.

## Test Signals
Tests should verify source registration/unregistration, name generation, initialized rate names, priority indexing, and sample updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/metrics/DecayRpcSchedulerDetailedMetrics.java -->
