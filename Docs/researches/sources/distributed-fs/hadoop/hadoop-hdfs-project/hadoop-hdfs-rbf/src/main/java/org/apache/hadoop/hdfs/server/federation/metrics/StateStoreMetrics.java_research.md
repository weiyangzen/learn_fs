# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/StateStoreMetrics.java

Purpose: `StateStoreMetrics` implements State Store Metrics2 and JMX metrics for transaction latency/count, per-record cache sizes, location cache counters, and cache loading durations.

Important APIs and state: `create(Configuration)` registers a Metrics2 source. `addRead`, `addWrite`, `addRemove`, and `addFailure` append latency samples to `MutableRate`s. Getter methods expose sample count and mean from the last stats interval. `setCacheSize` lazily creates `MutableGaugeInt`s keyed as `Cache<name>Size`; `setLocationCache` lazily creates `MutableGaugeLong`s; `setCacheLoading` lazily creates `MutableRate`s keyed as `Cache<name>Load`. `getCacheLoadMetrics` and `reset` are visible for testing.

Control flow and persistence: metrics are process-local, held in Metrics2 mutable objects and not persisted. `shutdown` shuts down `DefaultMetricsSystem` and resets rates. The protected no-arg constructor supports test/proxy creation but leaves fields dependent on Metrics2 injection.

Dependencies and integration points: State Store drivers call the add/set methods. `MountTableResolver.loadCache` writes location cache access/miss counters through this class. Metrics2 annotations and registry tags expose session/process metadata.

Risks: `shutdown` calls global `DefaultMetricsSystem.shutdown`, which can affect more than just this source in embedded tests. `reset` assumes `reads/writes/removes/failures` are non-null. Cache metric maps are not synchronized; expected use is metrics-thread friendly but concurrent lazy creation can race.

Test signals: cover operation sample counts/averages, dynamic gauge creation and updates, cache load rate creation, `reset`, and interactions from mount table cache metrics.
