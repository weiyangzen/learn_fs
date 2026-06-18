# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/Content.java

## Purpose
`Content` is an enum of namespace content counters used while computing HDFS content summaries.

## Important APIs and Types
The enum values are `FILE`, `DIRECTORY`, `SYMLINK`, `LENGTH`, `DISKSPACE`, `SNAPSHOT`, and `SNAPSHOTTABLE_DIRECTORY`.

## Control Flow
There is no executable logic; values are consumed by `EnumCounters<Content>` in `ContentCounts` and namespace summary traversal code.

## State and Persistence
The enum has no mutable state and is not directly persisted. Its ordinal/name stability matters for in-memory counters and APIs that map these counters to content summary fields.

## Dependencies and Integration
Primary integration is `ContentCounts`, `ContentSummaryComputationContext`, and INode content summary computation.

## Risks and Test Signals
Adding or reordering enum values could affect counter array layout if any code assumes ordinal positions. Tests should verify that content summary fields map to the intended enum values and that snapshots/snapshottable directories are counted separately from normal directories.
