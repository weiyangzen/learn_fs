# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/QuotaCounts.java

## Purpose
`QuotaCounts` aggregates namespace, storage-space, and per-storage-type counters for quota usage and limits. It optimizes common zero and reset values by sharing immutable `ConstEnumCounters`.

## Important APIs, types, and functions
Static constants represent all-zero and all-`QUOTA_RESET` counters for quota and storage types. `modify` implements copy-on-write from const counters. `Builder` sets namespace, storage space, type-space counters/scalars, or copies another `QuotaCounts`. Instance methods add, subtract, negate, get/set/add namespace and storage values, get/set/add type spaces, threshold-check counters, and render/compare values.

## Control flow
Setters use `setQuotaCounter` to preserve shared default/reset counters when both quota dimensions match those common values. All mutation goes through `modify`, which deep-copies const counters before applying changes.

## State and persistence behavior
Instances are mutable in-memory accounting objects. They are computed from and written into inode quota features, namespace updates, snapshots, rename deltas, and fsimage/edit-log operations elsewhere. `getTypeSpaces` returns a defensive copy.

## Dependencies and integration points
Dependencies include `Quota`, `StorageType`, `EnumCounters`, `ConstEnumCounters`, `HdfsConstants.QUOTA_RESET`, and `Consumer`. It is heavily used by `FSDirectory`, `INode`, snapshots, quota verification, and storage-policy accounting.

## Risks and invariants
Mutating shared const counters would corrupt global defaults, so copy-on-write is mandatory. `hashCode` intentionally asserts false and returns a constant, so instances should not be hash keys. Threshold helpers must match full-counter semantics for shared zero/reset cases.

## Test signals
Relevant tests include `TestQuota`, `TestDiskspaceQuotaUpdate`, `TestCorrectnessOfQuotaAfterRenameOp`, EC quota tests, and snapshot quota tests. Focus on copy-on-write, default/reset sharing, defensive copies, add/subtract/negation, and threshold behavior.
