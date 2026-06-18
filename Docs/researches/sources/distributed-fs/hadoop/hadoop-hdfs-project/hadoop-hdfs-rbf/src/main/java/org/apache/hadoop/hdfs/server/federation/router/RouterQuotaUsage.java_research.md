<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUsage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUsage.java

## Purpose
`RouterQuotaUsage` is the router-specific `QuotaUsage` subclass used to represent aggregated quota usage and limits for federation mount points. It adds fluent builder methods, quota violation checks, and a compact string representation.

## Important APIs, Types, and Functions
`RouterQuotaUsage.Builder` extends `QuotaUsage.Builder` and overrides setters to return the router builder type. `verifyNamespaceQuota`, `verifyStoragespaceQuota`, and `verifyQuotaByStorageType` throw HDFS quota exceptions when usage exceeds configured limits. `toString` renders namespace and storage-space quota/usage pairs, using `-` for reset quotas and byte descriptions for space values.

## Control Flow
Violation checks read the relevant quota and consumed values, skip reset storage-type quotas, and use NameNode `Quota.isViolated`. Storage-type verification iterates only over types supporting quota.

## State and Persistence Behavior
Instances are immutable through the inherited `QuotaUsage` builder pattern. No persistence occurs here; values are held in router quota cache and mount-table records.

## Dependencies and Integration Points
Dependencies include `QuotaUsage`, `StorageType`, `HdfsConstants`, `NSQuotaExceededException`, `DSQuotaExceededException`, NameNode `Quota`, `DirectoryWithQuotaFeature` semantics, and `StringUtils.byteDesc`. `RouterQuotaManager` and `RouterQuotaUpdateService` build and consume this type.

## Risks
Quota checks must be called by enforcement paths; this class does not enforce automatically. The builder supports array setters inherited from `QuotaUsage`, so callers must provide arrays aligned with `StorageType.values()`. `toString` omits per-storage-type quotas, which is fine for compact logs but not full diagnostics.

## Test Signals
Tests should cover fluent builder chaining, namespace violation and reset behavior, storage-space violation and reset behavior, per-storage-type iteration and exception, default counts, inherited getter values, and `toString` formatting for set and unset quotas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterQuotaUsage.java -->
