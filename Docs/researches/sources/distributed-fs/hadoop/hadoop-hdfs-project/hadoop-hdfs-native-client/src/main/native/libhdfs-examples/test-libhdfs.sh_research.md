# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/test-libhdfs.sh

## Purpose
Legacy shell integration harness for running libhdfs tests against a MiniDFSCluster launched from Hadoop jars.

## Important APIs, Types, And Functions
Requires `HADOOP_HOME`; optional env vars include `HDFS_TEST_CONF_DIR`, `LIBHDFS_BUILD_DIR`, `OS_NAME`, and `CLOVER_JAR`. Function `findlibjvm` locates JVM library directories. It launches `MiniDFSClusterManager` and runs `hdfs_test` with `LD_PRELOAD`.

## Control Flow
Validate environment, find HDFS test jar, assemble classpath from Hadoop jars, locate libjvm, remove old core-site, start a background MiniDFSClusterManager that writes config, wait up to 30 seconds, run native test with preloaded libjvm/libhdfs, kill cluster, exit with test status.

## State, Persistence, And Dependencies
Writes/removes `core-site.xml` in test conf dir, writes `/tmp/libhdfs-test-cluster.out`, starts/kills a background JVM, and uses native libraries from Hadoop install paths.

## Integration Points
Connects installed Hadoop layout, Java MiniDFSCluster manager, and native libhdfs test executable.

## Risks
Uses `kill -9` for cleanup, unquoted paths in places, fixed NameNode port 20300, and `LD_PRELOAD` assumptions. `rm core-site.xml` can fail or remove caller-provided config. Modern JVM layouts may break `tools.jar` or libjvm assumptions.

## Test Signals
Cluster config file creation, native test exit status, and cluster cleanup messages are the main signals.
