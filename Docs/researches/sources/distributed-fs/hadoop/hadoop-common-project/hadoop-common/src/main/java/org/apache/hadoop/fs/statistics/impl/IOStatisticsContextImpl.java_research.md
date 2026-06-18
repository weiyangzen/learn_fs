# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsContextImpl.java

Purpose: concrete per-thread IOStatisticsContext that aggregates into a mutable `IOStatisticsSnapshot`.

Important APIs, types, and functions: constructor taking thread ID and unique ID; `getAggregator()`, `snapshot()`, `reset()`, `getIOStatistics()`, `getID()`, and `toString()`.

Control flow: producers aggregate into the internal snapshot via `getAggregator()`. `snapshot()` returns a new snapshot copy; `reset()` clears internal maps for the next interval.

State and persistence: stores `threadId`, unique `id`, and a live mutable `IOStatisticsSnapshot`. Snapshot copies are serializable; the context itself is runtime state.

Dependencies and integration points: implements `IOStatisticsContext`; created by `IOStatisticsContextIntegration` for threads tracked in the weak thread map.

Risks and test signals: reset clears the shared internal aggregator, so callers must snapshot before reset. Tests should cover aggregate/snapshot isolation, reset, logging output, unique ID assignment, and concurrent access through snapshot synchronization.
