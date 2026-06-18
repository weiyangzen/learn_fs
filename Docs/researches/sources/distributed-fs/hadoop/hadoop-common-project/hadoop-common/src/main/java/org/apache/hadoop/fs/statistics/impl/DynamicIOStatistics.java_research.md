# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/DynamicIOStatistics.java

Purpose: package-private IOStatistics implementation whose map values are evaluated lazily through registered functions.

Important APIs, types, and functions: map accessors return unmodifiable maps for counters, gauges, minimums, maximums, and means. Package methods add evaluator functions for each category.

Control flow: builder registers key-to-function mappings. When callers access or iterate the returned maps, `EvaluatingStatisticsMap` invokes the functions and returns current values; mean values are copied to avoid exposing mutable internals.

State and persistence: stores evaluator functions rather than fixed values. It is live and non-serializable; snapshots are needed to persist point-in-time values.

Dependencies and integration points: depends on `AbstractIOStatisticsImpl`, `EvaluatingStatisticsMap`, and `MeanStatistic`. Built by `DynamicIOStatisticsBuilder`, used by stores and adapters over Hadoop `StorageStatistics`.

Risks and test signals: evaluator failures happen during map reads and can surprise logging/snapshot callers. Tests should cover lazy evaluation, unmodifiable maps, mean copy isolation, duplicate key replacement behavior, and snapshot consistency.
