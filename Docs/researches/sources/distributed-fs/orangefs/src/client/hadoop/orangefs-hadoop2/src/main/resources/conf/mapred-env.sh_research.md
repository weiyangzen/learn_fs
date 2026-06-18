<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/mapred-env.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/mapred-env.sh

## Purpose

This shell environment template initializes daemon/client environment variables for the OrangeFS Hadoop example. It contributes Java settings, log locations, Hadoop classpath entries, JNI library paths, and OrangeFS-specific variables.

## Important APIs, Types, and Functions

Key environment contracts are `JAVA_HOME`, `ORANGEFS_VERSION`, `ORANGEFS_PREFIX`, `LD_LIBRARY_PATH`, `JNI_LIBRARY_PATH`, `HADOOP_CLASSPATH`, `PVFS2TAB_FILE`, `ORANGEFS_STRIP_SIZE_AS_BLKSIZE`, and service-specific log/heap options.

Active directives observed:

- `export JAVA_HOME=${JAVA_HOME}`
- `export HADOOP_MAPRED_LOG_DIR="/tmp/hadoop-${USER}/hadoop2logs"`
- `export HADOOP_JOB_HISTORYSERVER_HEAPSIZE=1000`
- `export HADOOP_MAPRED_ROOT_LOGGER=INFO,RFA`

## Control Flow

Hadoop startup scripts source this file before launching daemons or clients. Autoconf substitutes the OrangeFS version placeholders, then the classpath entries make the `orangefs-hadoop*` and `orangefs-jni` jars visible to Hadoop.

## State, Persistence, and Concurrency

The file does not persist application data. It controls process environment and log placement; changes require restarting the affected daemon or rerunning the client command.

## Dependencies and Integration Points

It depends on a valid Java installation, Hadoop's shell launcher conventions, OrangeFS libraries under `/opt/orangefs` by default, and the generated JNI/Hadoop jars in `ORANGEFS_PREFIX/lib`.

## Risks and Test Signals

Hard-coded Java 7 paths, mutable `/tmp` log locations, and missing JNI library paths are common failure points. Test signals are successful daemon startup, no `UnsatisfiedLinkError`, and OrangeFS classes visible in `hadoop classpath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/mapred-env.sh -->
