# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/QuotaExceededException.java

## Purpose
`QuotaExceededException` is the base public/evolving HDFS quota exception for namespace and disk/storage-space quota violations. It extends `ClusterStorageCapacityExceededException`.

## APIs and Behavior
Protected constructors support no-arg, explicit message, and `(quota, count)` creation for subclasses. `setPathName(String)` sets the path included by subclass-generated messages. `getMessage()` delegates to the superclass; specialized subclasses generate detailed text when no explicit message is present.

## State, Dependencies, and Integration
It stores mutable `pathName`, `quota`, and `count` for subclasses. It integrates with NameNode quota enforcement and client RPC exception propagation.

## Risks and Test Signals
The base class itself does not generate details, so using it directly with quota/count yields an empty superclass message. Tests should cover subclass message behavior, path mutation after construction, serialization across RPC, and callers catching the base type for all quota failures.
