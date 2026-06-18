# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSetters.java

Purpose: small public interface that adds direct setter methods to the read-only `IOStatistics` contract so mutable stores and snapshots can share a common mutation surface.

Important APIs, types, and functions: declares `setCounter()`, `setGauge()`, `setMaximum()`, `setMinimum()`, and `setMeanStatistic()`.

Control flow: implementations decide whether unknown keys are no-ops or create entries. `IOStatisticsSnapshot` inserts values into maps; `IOStatisticsStoreImpl` only updates predeclared atomic entries.

State and persistence: no state. It defines write access to runtime or snapshot statistics state.

Dependencies and integration points: depends on `IOStatistics` and `MeanStatistic`. It is implemented by `IOStatisticsSnapshot` and `IOStatisticsStore`.

Risks and test signals: callers must understand the implementation-specific unknown-key policy. Tests should cover snapshot insertion, store no-op behavior for missing keys, mean statistic copy/reference expectations, and compatibility with JSON/serialized snapshots.
