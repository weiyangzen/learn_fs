# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DSQuotaExceededException.java

## Purpose
`DSQuotaExceededException` specializes `QuotaExceededException` for disk-space quota violations. It is part of the public/evolving HDFS exception surface and is thrown by namespace operations such as create, append, replication changes, and rename when storage-space quota would be exceeded.

## APIs and Behavior
The class provides default, message, and `(quota, count)` constructors. `getMessage()` delegates to the superclass when an explicit message exists; otherwise it builds a detailed disk-space message using inherited `pathName`, `quota`, and `count`, including both raw bytes and human-readable binary-prefix strings via `long2String`.

## State, Dependencies, and Integration
State is inherited from `QuotaExceededException`. The exception is serialized across RPC as part of NameNode error propagation and is expected by client-side code that distinguishes namespace quota from disk-space quota. No persistence happens in this class.

## Risks and Test Signals
Formatting is user-visible and should remain stable enough for diagnostics, though callers should not parse it. Tests should cover explicit-message preservation, null and non-null `pathName`, large byte values, and correct propagation through create/append/setReplication RPC failure paths.
