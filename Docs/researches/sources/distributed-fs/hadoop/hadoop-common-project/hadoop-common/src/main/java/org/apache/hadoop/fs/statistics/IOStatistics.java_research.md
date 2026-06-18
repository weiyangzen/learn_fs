# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatistics.java

Purpose: public unstable interface exposing low-cost per-instance IO statistics.

Important APIs and types: map accessors `counters()`, `gauges()`, `minimums()`, `maximums()`, `meanStatistics()`, and unset sentinels `MIN_UNSET_VALUE`/`MAX_UNSET_VALUE` equal to -1.

Control flow: implementations return current statistic maps; consumers read maps by agreed string keys. No methods mutate statistics directly.

State and persistence: interface state is implementation-defined. Returned maps may be live snapshots or immutable copies depending on implementation, which consumers must account for via specification.

Dependencies and integration: uses `MeanStatistic` and Java `Map`; consumed by logging, aggregation, duration summaries, stream wrappers, and filesystem/store metrics.

Risks: map mutability and concurrency guarantees are not specified in this interface. Missing minimum/maximum values use -1 sentinel, which can overlap valid values for some theoretical metrics. Key names are stringly typed.

Test signals: implementation tests should cover all map categories, empty maps, unset sentinels, snapshot/live behavior, thread-safety expectations, and mean statistic cloning where applicable.
