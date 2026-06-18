# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterClientMetrics.java

## Purpose
`RouterClientMetrics` publishes counters for router client protocol activity through Hadoop Metrics2. It tracks total invoked operations and a subset of concurrently invoked fan-out operations.

## Important APIs, Types, And Functions
- `create(Configuration)` registers a `RouterClientMetrics` instance with `DefaultMetricsSystem` and tags it with process/session metadata.
- `shutdown()` shuts down the default metrics system.
- `incInvokedMethod(Method)` increments a method-specific counter for many `ClientProtocol` methods, defaulting to `otherOps`.
- `incInvokedConcurrent(Method)` increments counters for methods invoked concurrently across remote locations, defaulting to `concurrentOtherOps`.
- Numerous `@Metric MutableCounterLong` fields define the published metric names.

## Control Flow
Both increment methods switch on `method.getName()`. Known operation names increment dedicated counters; unknown names increment the appropriate `other` counter. There is no reflection beyond reading the method name passed by caller code.

## State And Persistence
Metrics counters are in-memory Metrics2 mutable counters registered in the process metrics system. They are exposed to configured metrics sinks but not persisted by this class.

## Dependencies And Integration Points
It depends on `Configuration`, `DFSConfigKeys.DFS_METRICS_SESSION_ID_KEY`, `DefaultMetricsSystem`, `MetricsRegistry`, Metrics2 annotations, and Java reflection `Method`. `RouterMetricsService` creates and exposes this class; router RPC client/server paths call increment methods around proxied operations.

## Risks And Edge Cases
The switches are manually maintained and can miss new `ClientProtocol` methods, sending them to `otherOps`. Some counter names must match expected metrics consumers, so renaming fields is externally visible. `shutdown` calls `DefaultMetricsSystem.shutdown`, which can affect other metrics registered in the same process. Concurrent counters cover a subset of methods, not every method listed in total counters.

## Test Signals
`TestRouterClientMetrics` directly validates metric registration and operation counters. Broader router RPC tests indirectly exercise counter increments for client operations.
