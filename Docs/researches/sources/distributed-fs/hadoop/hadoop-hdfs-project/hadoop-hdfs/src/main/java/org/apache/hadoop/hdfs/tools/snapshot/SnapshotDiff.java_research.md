<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/SnapshotDiff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/SnapshotDiff.java

## Purpose
`SnapshotDiff` implements `hdfs snapshotDiff <snapshotDir> <from> <to>` to print differences between two snapshots or between a snapshot and the current directory tree.

## APIs and Types
It extends `Configured` and implements `Tool`. Constructors default to `HdfsConfiguration` or accept any `Configuration`. `getSnapshotName` normalizes `"."`, `.snapshot/name`, and `/.snapshot/name` forms. `run` and `main` provide CLI execution.

## Control Flow
`run` requires three arguments, resolves the filesystem from the snapshot root URI, enforces `DistributedFileSystem`, normalizes from/to names, invokes `dfs.getSnapshotDiffReport`, and prints the report string. `IOException` prints a short error line and the full stack trace to stderr before returning failure.

## State and Persistence
No persistent state. The command reads NameNode snapshot metadata through the DFS client and writes a textual diff report.

## Dependencies and Integration
It depends on `DistributedFileSystem`, `SnapshotDiffReport`, `HdfsConstants`, `Path`, and `ToolRunner`. It is a CLI wrapper over the DFS snapshot diff RPC.

## Risks
`getSnapshotName` uses string prefix slicing and must stay aligned with `.snapshot` constants. Stack traces on normal user-facing errors are noisy. Exception message splitting assumes non-null localized messages. It does not validate that from/to are distinct.

## Test Signals
Tests should cover normalization for `"."`, `.snapshot/foo`, `/.snapshot/foo`, raw snapshot names, argument count errors, non-DFS filesystem rejection, successful report printing, and IOException stderr format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/SnapshotDiff.java -->
