<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshot.java

## Purpose
`LsSnapshot` is a private HDFS CLI tool implementing `hdfs lsSnapshot <snapshotDir>` to list snapshots for one snapshottable directory.

## APIs and Types
It extends `Configured` and implements `Tool`. The public API is `run(String[] argv)` and `main`, which delegates through `ToolRunner`.

## Control Flow
`run` builds usage text, requires exactly one argument, constructs a `Path`, obtains a `DistributedFileSystem` through `AdminHelper.getDFS(getConf())`, calls `getSnapshotListing(snapshotRoot)`, and prints results with `SnapshotStatus.print`. On exception it prints only the first line of the localized message and returns 1.

## State and Persistence
The tool has no persistent state. It reads cluster state via the configured DFS client and writes to stdout/stderr.

## Dependencies and Integration
It depends on `DistributedFileSystem`, `SnapshotStatus`, `AdminHelper`, `Tool`, and Hadoop configuration injection. It integrates into HDFS command-line administration.

## Risks
Error handling assumes `getLocalizedMessage()` is non-null. It does not verify the filesystem type itself because `AdminHelper.getDFS` is responsible. Usage text comments mention snapshottable directories generally, while this command lists snapshots under a specific path.

## Test Signals
Tests should cover argument count validation, successful print delegation, DFS exception message trimming, null/empty exception messages, and `main` exit-code behavior through a tool harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/snapshot/LsSnapshot.java -->
