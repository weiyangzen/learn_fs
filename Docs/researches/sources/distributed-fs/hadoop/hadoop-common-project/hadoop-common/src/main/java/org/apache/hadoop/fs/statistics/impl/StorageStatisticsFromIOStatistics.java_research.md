# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/impl/StorageStatisticsFromIOStatistics.java

Purpose: adapter that publishes IOStatistics counters through Hadoop's older `StorageStatistics` API.

Important APIs, types, and functions: constructor with name, scheme, and IOStatistics; overrides for `getScheme()`, `getLong()`, `isTracked()`, `reset()`, and `getLongStatistics()`.

Control flow: `getLong()` reads from the source counter map. Iteration over long statistics converts current IOStatistics counter entries into `StorageStatistics.LongStatistic` objects. Reset is a no-op because the adapter does not own mutable state.

State and persistence: stores name/scheme via superclass and a source IOStatistics reference. It is a live adapter, not a snapshot.

Dependencies and integration points: depends on `StorageStatistics` and `IOStatistics`; created by `IOStatisticsBinding.publishAsStorageStatistics()`. It bridges newer IOStatistics into existing Hadoop metrics consumers.

Risks and test signals: only counters are published, not gauges/min/max/means. Tests should cover missing keys, live counter updates, iterator contents, scheme propagation, and reset no-op behavior.
