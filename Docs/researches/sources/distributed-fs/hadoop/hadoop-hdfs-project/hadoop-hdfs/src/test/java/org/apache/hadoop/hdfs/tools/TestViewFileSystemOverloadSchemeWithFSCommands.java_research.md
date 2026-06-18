# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestViewFileSystemOverloadSchemeWithFSCommands.java

## Purpose
`TestViewFileSystemOverloadSchemeWithFSCommands` verifies FsShell behavior for `-df` when the `hdfs` scheme is backed by `ViewFileSystemOverloadScheme`.

## Important APIs, Types, And Functions
It uses `ViewFileSystemOverloadScheme`, `ViewFsTestSetup.addMountLinksToConf`, `FsShell`, `ToolRunner`, `MiniDFSCluster`, and stream scanning helpers.

## Control Flow
Setup mirrors the DFSAdmin overload test: configure `fs.hdfs.impl`, target HDFS implementation, start a cluster, and capture the default HDFS URI. The test adds two mounts, one HDFS and one local, runs `FsShell -df -h` against the overloaded root, parses stdout lines, and removes observed mount paths from an expected list.

## State, Persistence, And Dependencies
State is the configured mount table, local target directory, MiniDFSCluster, and captured stdout/stderr. The `FsShell` is closed in a finally block.

## Integration Points
This validates FsShell filesystem resolution and per-mount disk-usage listing through ViewFS overload, including mixed HDFS/local targets.

## Risks
The test expects exactly three output lines and assumes the final whitespace-separated token is the mount path. Formatting changes in `-df -h` can break it without a semantic regression. It only covers `-df`, not other FsShell commands.

## Test Signals
Signals are zero return code, output line count, and both configured mounts appearing in the `df` result.
