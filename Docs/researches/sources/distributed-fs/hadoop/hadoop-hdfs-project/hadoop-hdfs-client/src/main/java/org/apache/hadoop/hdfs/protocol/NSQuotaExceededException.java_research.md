# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NSQuotaExceededException.java

## Purpose
`NSQuotaExceededException` specializes `QuotaExceededException` for namespace quota violations, i.e. file and directory count limits.

## APIs and Behavior
It offers default, message, and `(quota, count)` constructors. `getMessage()` preserves explicit superclass messages; otherwise it builds a namespace quota message using inherited path/quota/count and optional prefix set by `setMessagePrefix()`.

## State, Dependencies, and Integration
State is inherited plus a mutable `prefix`. The class is public/evolving and propagates through NameNode RPCs for create, mkdir, rename, and other namespace mutations.

## Risks and Test Signals
The prefix is mutable and only affects generated messages. Tests should cover explicit-message bypass, prefix rendering, null path handling, and RPC propagation from operations that exceed directory namespace quotas.
