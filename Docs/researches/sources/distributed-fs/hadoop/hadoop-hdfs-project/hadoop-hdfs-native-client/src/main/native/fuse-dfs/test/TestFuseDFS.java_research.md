# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/test/TestFuseDFS.java

## Purpose
JUnit integration tests for a `fuse_dfs` mount backed by a Java `MiniDFSCluster`.

## Important APIs, Types, And Functions
Class state includes `MiniDFSCluster`, `FileSystem`, `Process fuseProcess`, runtime, and mount point. Helpers execute shell commands, create/check files, redirect process output, establish and tear down FUSE mount. Tests cover directories, create/read/delete, touch, unsupported random writes, recursive copy, and concurrent threads.

## Control Flow
`startUp` builds a MiniDFSCluster with permissions disabled, establishes the mount by launching `fuse_dfs` with classpath/native env, and waits. Each test uses local file APIs and shell commands against the mount. `tearDown` unmounts before shutting down HDFS.

## State, Persistence, And Dependencies
State includes real FUSE mount, external `fusermount`, native binary paths relative to `build.test`, JVM/libhdfs library paths, and MiniDFS files. Tests mutate the mounted HDFS namespace and host mount table.

## Integration Points
Exercises Java build output, native `fuse_dfs`, libhdfs JNI, MiniDFSCluster, and common POSIX tools (`mkdir`, `ls`, `rm`, `cp`, `find`, `cat`, `stat`).

## Risks
Very environment-sensitive: requires FUSE privileges/config (`user_allow_other`), Linux utilities, correct native library paths, and long sleeps. Shell command strings are not escaped. Fixed 50-second mount wait slows tests and may still be flaky.

## Test Signals
Passes indicate end-to-end mount functionality for basic metadata, data I/O, deletion, copy, and concurrency. Failures often point to environment setup rather than pure code regressions.
