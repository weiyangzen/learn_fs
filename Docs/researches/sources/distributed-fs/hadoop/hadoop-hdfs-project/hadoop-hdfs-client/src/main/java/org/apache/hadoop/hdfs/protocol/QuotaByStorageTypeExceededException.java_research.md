# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaByStorageTypeExceededException.java

## Purpose
`QuotaByStorageTypeExceededException` specializes quota failures for storage-type-specific space quotas.

## APIs and Behavior
It provides default, message, and `(quota, count, StorageType)` constructors. `getMessage()` preserves explicit messages or builds a storage-type quota message with path, quota, and consumed space formatted via `long2String`.

## State, Dependencies, and Integration
It extends `QuotaExceededException` and adds `StorageType type`. It is thrown by storage policy/quota enforcement when a path exceeds quota for a specific storage media type.

## Risks and Test Signals
Generated-message path calls `type.toString()`, so a null type will throw. Tests should cover explicit messages, all relevant storage types, null path behavior, null type behavior, and propagation through storage-type quota RPCs.
