## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EmptyStorageStatistics.java

Purpose: `EmptyStorageStatistics` is a package-private no-op `StorageStatistics` implementation for filesystems or components that need a statistics object but have no counters to report.

Important APIs and types: the constructor passes a name to `StorageStatistics`. `getLongStatistics()` returns an empty iterator, `getLong(String)` returns null, `isTracked(String)` returns false, and `reset()` is a no-op.

Control flow, state, and persistence: after construction, behavior is fixed and stateless apart from the inherited name. No counters are allocated, reset does nothing, and no data is persisted.

Dependencies and integration: it depends on `StorageStatistics` and `Collections.emptyIterator()`. It is useful as a null-object implementation in filesystem statistics wiring, avoiding null checks for statistics containers.

Risks and test signals: risks are mostly caller assumptions. Code expecting non-null `Long` values or a tracked key can misinterpret this empty implementation. Tests should verify empty iteration, null value lookup, false tracking for arbitrary keys, idempotent reset, and inherited name behavior.
