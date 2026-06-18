<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hadoop-env.sh.in -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hadoop-env.sh.in

## Purpose

This shell environment template initializes daemon/client environment variables for the OrangeFS Hadoop example. It contributes Java settings, log locations, Hadoop classpath entries, JNI library paths, and OrangeFS-specific variables.

## Important APIs, Types, and Functions

Key environment contracts are `JAVA_HOME`, `ORANGEFS_VERSION`, `ORANGEFS_PREFIX`, `LD_LIBRARY_PATH`, `JNI_LIBRARY_PATH`, `HADOOP_CLASSPATH`, `PVFS2TAB_FILE`, `ORANGEFS_STRIP_SIZE_AS_BLKSIZE`, and service-specific log/heap options.

Active directives observed:

- `export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64`
- `export MALLOC_ARENA_MAX=4`
- `export HADOOP_CONF_DIR=${HADOOP_CONF_DIR:-"/etc/hadoop"}`
- `export ORANGEFS_VERSION="@PVFS2_VERSION_MAJOR@.@PVFS2_VERSION_MINOR@.@PVFS2_VERSION_SUB@"`
- `export ORANGEFS_PREFIX=/opt/orangefs`
- `export LD_LIBRARY_PATH=$ORANGEFS_PREFIX/lib`
- `export JNI_LIBRARY_PATH=$ORANGEFS_PREFIX/lib`
- `export PVFS2TAB_FILE=/tmp/orangefs_hadoop_storage/pvfs2tab`
- `if [ "$HADOOP_CLASSPATH" ]; then`
- `export HADOOP_CLASSPATH="$HADOOP_CLASSPATH:$JNI_LIBRARY_PATH/orangefs-hadoop2-${ORANGEFS_VERSION}.jar:$JNI_LIBRARY_PATH/orangefs-jni-${ORANGEFS_VERSION}.jar"`
- `else`
- `export HADOOP_CLASSPATH="$JNI_LIBRARY_PATH/orangefs-hadoop2-${ORANGEFS_VERSION}.jar:$JNI_LIBRARY_PATH/orangefs-jni-${ORANGEFS_VERSION}.jar"`
- `fi`
- `export ORANGEFS_STRIP_SIZE_AS_BLKSIZE=true`
- `for f in $HADOOP_HOME/contrib/capacity-scheduler/*.jar; do`
- `if [ "$HADOOP_CLASSPATH" ]; then`
- `export HADOOP_CLASSPATH=$HADOOP_CLASSPATH:$f`
- `else`
- `export HADOOP_CLASSPATH=$f`
- `fi`

## Control Flow

Hadoop startup scripts source this file before launching daemons or clients. Autoconf substitutes the OrangeFS version placeholders, then the classpath entries make the `orangefs-hadoop*` and `orangefs-jni` jars visible to Hadoop.

## State, Persistence, and Concurrency

The file does not persist application data. It controls process environment and log placement; changes require restarting the affected daemon or rerunning the client command.

## Dependencies and Integration Points

It depends on a valid Java installation, Hadoop's shell launcher conventions, OrangeFS libraries under `/opt/orangefs` by default, and the generated JNI/Hadoop jars in `ORANGEFS_PREFIX/lib`.

## Risks and Test Signals

Hard-coded Java 7 paths, mutable `/tmp` log locations, and missing JNI library paths are common failure points. Test signals are successful daemon startup, no `UnsatisfiedLinkError`, and OrangeFS classes visible in `hadoop classpath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hadoop-env.sh.in -->
