# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NullStateStoreMetrics.java

Purpose: no-op `StateStoreMetrics` implementation used when state-store metrics are disabled, especially in tests.

Important APIs and types: extends `StateStoreMetrics` and overrides read/write/failure/remove metric update and getter methods, cache size, reset, and shutdown.

Control flow: update methods do nothing; operation count and average getters return `-1`; cache/reset/shutdown methods are no-ops.

State and persistence: no state and no metrics registration.

Dependencies and integration points: lets code depend on a `StateStoreMetrics` instance without checking for null when metrics collection is disabled.

Risks: returning `-1` is a sentinel and must not be treated as a real metric. Tests should verify callers tolerate disabled metrics and do not publish negative values as normal operational data.
