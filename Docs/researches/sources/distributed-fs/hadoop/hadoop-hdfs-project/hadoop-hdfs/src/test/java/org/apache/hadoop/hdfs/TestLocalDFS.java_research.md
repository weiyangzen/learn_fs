# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLocalDFS.java

## Purpose
Tests basic `FileSystem` working directory and home directory behavior against a local `MiniDFSCluster`.

## APIs and Control Flow
`writeFile`, `readFile`, and `cleanupFile` create, verify, and delete simple files. `getUserName` extracts the DFS client's short username for `DistributedFileSystem`. `testWorkingDirectory` verifies the original working directory is absolute, writes relative paths, changes working directory with absolute and relative paths, reads content, cleans up, and checks home directory uses the default `/user/<user>` prefix. `testHomeDirectory` loops over custom home prefixes `/home` and `/home/user` and checks `getHomeDirectory`.

## State, Dependencies, Integration
State is per-client working directory, namespace paths, and home-prefix configuration. Dependencies include `MiniDFSCluster`, `FileSystem`, `HdfsClientConfigKeys`, and simple data streams. It integrates HDFS `FileSystem` path resolution with user identity and configuration.

## Risks and Test Signals
Signals are content equality, existence/deletion checks, and exact home path equality. Risks are user-name derivation differences for non-DFS wrappers and repeated cluster creation inside a loop with shared `Configuration`.
