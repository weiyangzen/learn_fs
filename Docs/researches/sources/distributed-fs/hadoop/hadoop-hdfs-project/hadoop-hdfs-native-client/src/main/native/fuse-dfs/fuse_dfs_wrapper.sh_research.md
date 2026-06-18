# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs_wrapper.sh

## Purpose
Convenience wrapper to launch `fuse_dfs` from a Hadoop source/build tree with classpath and native library paths set.

## Important APIs, Types, And Functions
Validates `HADOOP_HOME`, sets `FUSEDFS_PATH`, `LIBHDFS_PATH`, default `OS_ARCH` and `JAVA_HOME`, builds `CLASSPATH` by finding jars under `hadoop-client` and `hadoop-hdfs-project`, updates `PATH` and `LD_LIBRARY_PATH`, then execs `fuse_dfs "$@"`.

## Control Flow
The script exits if `HADOOP_HOME` is empty, applies defaults, iterates over jar files with null-delimited `find`, prepends configuration and library paths, and launches the binary.

## State, Persistence, And Dependencies
Environment variables are the primary state. It depends on bash, `find`, a source-tree layout, compiled native artifacts under target paths, and JVM server library layout.

## Integration Points
Used by developers or tests to run the built FUSE client without manually constructing JNI/libhdfs classpath and library paths.

## Risks
Hard-coded target paths and `$JAVA_HOME/jre/lib/$OS_ARCH/server` may not match modern JDK layouts. It overwrites `LD_LIBRARY_PATH` at the end rather than preserving all earlier content. Missing `HADOOP_CONF_DIR` produces an empty classpath component.

## Test Signals
Successful wrapper launch means jars are found, libhdfs and libjvm are loadable, and `fuse_dfs` is on `PATH`.
