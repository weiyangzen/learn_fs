## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableRatesWithAggregation.java

Purpose: High-concurrency rate collection using per-thread local stats aggregated into global mutable rates at snapshot time.

Important APIs/types/functions: `init(Class)` and `init(String[])` pre-create metrics, `add(name,elapsed)` records thread-local samples, `snapshot` aggregates live thread maps and snapshots globals, `collectThreadLocalStates` forces current thread aggregation, and `init(protocol,prefix)` adds a metric-name prefix.

Control flow: Each thread lazily creates a local map stored in `ThreadLocal` and tracked by weak reference. Snapshot removes dead-thread maps, drains local `ThreadSafeSampleStat` values into `MutableRate` instances, then snapshots global metrics.

State and persistence: Concurrent global metrics map, protocol cache, weak-reference queue of thread maps, thread-local map, and prefix. In-memory only.

Dependencies/integration: Created by `MetricsRegistry.newRatesWithAggregation` and annotation factory.

Risks/test signals: Samples from dead threads can be lost if not snapshotted before GC, as documented. Tests should cover multi-thread aggregation, weak reference cleanup, prefixing, and protocol cache behavior.
