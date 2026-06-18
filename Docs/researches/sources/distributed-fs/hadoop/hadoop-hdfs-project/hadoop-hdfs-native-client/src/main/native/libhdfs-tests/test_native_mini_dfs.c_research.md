# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_native_mini_dfs.c

## Purpose
`test_native_mini_dfs.c` is the smallest lifecycle test for the native MiniDFSCluster wrapper. It verifies that the JNI bridge can create a formatted cluster, wait for it to become active, shut it down, and free native resources.

## Important APIs and types
The file defines a static `NativeMiniDfsConf` with `doFormat=1` and uses `nmdCreate`, `nmdWaitClusterUp`, `nmdShutdown`, and `nmdFree`.

## Control flow
`main` creates the cluster, expects a non-NULL pointer, waits for startup, shuts down, frees the wrapper, and returns zero. Failures are handled by `EXPECT_*` macros from `expect.h`.

## State and persistence
The only state is the formatted MiniDFSCluster created for the test process. No files are created through libhdfs in this test.

## Dependencies
It depends on `native_mini_dfs.h`, `expect.h`, JNI and Hadoop classes loaded by the implementation, and errno only through included support.

## Risks
This test does not cover NameNode port lookup, WebHDFS, short-circuit setup, datanode count, or libhdfs connections. It is a fast sentinel for JVM/classpath/MiniDFS lifecycle breakage rather than functional HDFS behavior.

## Test signals
Passing this test confirms that native tests can start the embedded Java MiniDFSCluster and tear it down cleanly. Failure usually indicates classpath, JNI initialization, MiniDFS construction, or shutdown invocation problems.
