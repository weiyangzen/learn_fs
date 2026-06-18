# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/IOStatisticsStoreBuilder.java

Purpose: builder interface for constructing an `IOStatisticsStore` with declared statistic keys.

Important APIs, types, and functions: fluent `withCounters()`, `withGauges()`, `withMinimums()`, `withMaximums()`, `withMeanStatistics()`, duration convenience declarations, and `build()`.

Control flow: callers declare the keys a store should track, then call `build()` to receive a mutable store implementation.

State and persistence: no state in the interface. Implementations hold declaration lists until build time.

Dependencies and integration points: implemented by `IOStatisticsStoreBuilderImpl`; obtained through `IOStatisticsBinding.iostatisticsStore()`.

Risks and test signals: if callers forget to register a key, later updates become no-ops or reference lookups fail. Tests should cover all declaration methods and duplicate/null key handling.
