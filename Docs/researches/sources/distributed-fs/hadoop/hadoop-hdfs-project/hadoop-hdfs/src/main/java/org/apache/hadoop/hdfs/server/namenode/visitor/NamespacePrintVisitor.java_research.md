<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespacePrintVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespacePrintVisitor.java

## Purpose

`NamespacePrintVisitor` renders the in-memory namespace tree as a text tree for tests and diagnostics, including files, symlinks, references, snapshots, quotas, and directory snapshot features.

## Important APIs and types

- Static `print2Sting(FSNamesystem)` and `print2Sting(INode)` return a string rendering.
- Implements specialized visitor methods for files, symlinks, references, directories, snapshottable directories, referred inodes, and child prefix hooks.
- Uses constants `"+-"` and `"\\-"` for branch rendering.

## Control flow

The private `print` starts traversal at current state. Each node-specific visit method writes inode details to a `PrintWriter`. Prefix hooks adjust a shared `StringBuilder` before and after children/referred inodes. Snapshottable directories print quota and snapshot count, validating that snapshot-root diffs match the feature's count.

## State and persistence behavior

State is limited to the output writer and mutable prefix builder for one traversal. It does not persist or mutate namespace state.

## Dependencies and integration points

Depends on `NamespaceVisitor`, `FSNamesystem`, inode subclasses, quota and snapshot feature classes, and inode dump methods. It is test-oriented.

## Risks and edge cases

Prefix manipulation assumes two-character branch markers; mismatched pre/post calls can corrupt output. `print2Sting` is misspelled but likely compatibility-sensitive for tests. Snapshot count mismatch throws through `Preconditions.checkState`.

## Test signals

Tests should compare output for normal trees, symlinks, snapshots, references, quotas, and empty/root directories. Snapshot feature invariant failures are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespacePrintVisitor.java -->
