# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ContentCounts.java

## Purpose
`ContentCounts` is the mutable counter bundle used by content summary computation. It tracks logical namespace contents and storage-space consumption by storage type.

## Important APIs and Types
The nested `Builder` initializes `EnumCounters<Content>` and `EnumCounters<StorageType>` and provides fluent setters for files, directories, symlinks, length, diskspace, snapshots, and snapshottable directories. The main object exposes getters, `addContent`, `addContents`, `addTypeSpace`, and `addTypeSpaces`.

## Control Flow
Builders create zeroed counters and set requested values. Traversal code mutates `ContentCounts` in place while visiting INodes and snapshots. `addContents` merges both content and storage-type counters from another `ContentCounts`.

## State and Persistence
State is purely in-memory and mutable. It is usually scoped to a content-summary request, not durable metadata.

## Dependencies and Integration
It depends on `Content`, `StorageType`, and HDFS `EnumCounters`. It is owned by `ContentSummaryComputationContext` and used by INode implementations.

## Risks and Test Signals
The builder passes counter instances into `ContentCounts` without cloning, so builders should not be reused after `build` if caller expects immutability. Tests should cover aggregation across content and type-space counters, empty builder defaults, and storage-type quota summary calculations.
