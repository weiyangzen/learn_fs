<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshottableDir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshottableDir.java

## Purpose
`LsSnapshottableDir` implements the `hdfs lsSnapshottableDir` CLI to list snapshottable directories visible to the current user, or all of them for a superuser.

## APIs and Types
It extends `Configured`, implements `Tool`, and exposes `run(String[] argv)` plus `main`.

## Control Flow
`run` requires zero arguments, obtains the default `FileSystem`, checks that it is a `DistributedFileSystem`, invokes `getSnapshottableDirListing`, and prints via `SnapshottableDirectoryStatus.print`. `IOException` is caught, shortened to the first localized-message line, printed, and returned as failure.

## State and Persistence
It keeps no state and performs no writes except stdout/stderr. Data comes from NameNode RPC through the DFS client.

## Dependencies and Integration
It depends on `FileSystem`, `DistributedFileSystem`, `SnapshottableDirectoryStatus`, and `ToolRunner`. It is part of the HDFS snapshot admin tool set.

## Risks
The tool rejects non-DFS filesystems at runtime. Like related snapshot tools, it assumes exception messages are non-null. It does not expose filters or machine-readable output.

## Test Signals
Tests should validate zero-argument usage, non-DFS rejection, successful listing print path, IOException formatting, and `ToolRunner` integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshottableDir.java -->
