<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/INodeCountVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/INodeCountVisitor.java

## Purpose

`INodeCountVisitor` traverses a namespace tree and counts how many times each inode id is visited, primarily for validating FSImage/snapshot graph structure.

## Important APIs and types

- Static `countTree(INode root)` returns `Counts`.
- `Counts.getCount(INode)` reports visit count by inode id.
- `INodeSet` stores `SetElement` keys in a `ConcurrentHashMap`.
- Default visitor increments count for every visited `INode`.

## Control flow

`countTree` creates a visitor and starts traversal at `Snapshot.CURRENT_STATE_ID`. Every inode accepted by the traversal hits the default visitor, which inserts or finds a `SetElement` keyed by inode id and atomically increments its count.

## State and persistence behavior

Counts are in-memory only. Snapshot ids are accepted by the visitor but not included in the key, so the count is per inode id across current and snapshot traversals.

## Dependencies and integration points

Depends on `NamespaceVisitor`, `INode`, and `Snapshot`. Used in FSImage validation/test contexts where references and snapshots may cause multiple visits.

## Risks and edge cases

Counting only by inode id intentionally collapses multiple Java object references to the same id. If ids are invalid or reused, counts become misleading. The concurrent map is safe but traversal itself depends on the namespace visitor implementation.

## Test signals

FSImage validation tests can assert expected counts for normal directories, snapshots, and references. Edge coverage should include referred inodes visited through `INodeReference`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/INodeCountVisitor.java -->
