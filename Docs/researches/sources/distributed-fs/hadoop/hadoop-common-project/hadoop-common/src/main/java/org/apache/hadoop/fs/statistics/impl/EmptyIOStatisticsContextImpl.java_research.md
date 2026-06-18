# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/EmptyIOStatisticsContextImpl.java

Purpose: singleton disabled-mode IOStatisticsContext used when thread-level IO statistics are not enabled.

Important APIs, types, and functions: `snapshot()`, `getAggregator()`, `getIOStatistics()`, `reset()`, `getID()`, and package-private `getInstance()`.

Control flow: snapshot returns an empty snapshot, aggregator/statistics return empty no-op objects, reset does nothing, and the ID is fixed for the disabled context.

State and persistence: no mutable state beyond shared singleton identity. It avoids creating per-thread state when collection is disabled.

Dependencies and integration points: depends on `IOStatisticsContext`, `IOStatisticsSnapshot`, and `IOStatisticsBinding` empty objects. Returned by `IOStatisticsContextIntegration` in disabled mode.

Risks and test signals: callers should not assume IDs identify real thread contexts when disabled. Tests should cover disabled mode no-op aggregation, non-null returns, reset behavior, and stable singleton access.
