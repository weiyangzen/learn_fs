# Research: subset-b-007831

This grouped report covers the OrangeFS Hadoop 1/Hadoop 2 adapter configuration, scripts, Java filesystem bridge, HCFS tests, and JNI user-interface bindings listed for `subset-b-007831`. Each source section is bounded with reconciliation markers so it can be split into the mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java

## Purpose

`OrangeFileSystemFSInputStream` adapts the OrangeFS JNI `OrangeFileSystemInputStream` to Hadoop's `Seekable` and `PositionedReadable` contracts while updating Hadoop `FileSystem.Statistics` counters.

## Important APIs, Types, and Functions

The class extends `org.orangefs.usrint.OrangeFileSystemInputStream` and implements `Closeable`, `Seekable`, and `PositionedReadable`. Important methods are the constructor, `getPos`, synchronized `read()` variants, positional `read(long, byte[], int, int)`, `readFully` variants, `seek`, and `seekToNewSource`.

## Control Flow

Construction opens the underlying OrangeFS stream and increments read operations. Normal reads delegate to the parent stream, then increment bytes-read when positive bytes are returned. Positional reads save the current offset, seek to the requested position, read, and seek back. `readFully` performs a single read and throws if it returns fewer bytes than requested. `seekToNewSource` always returns false because OrangeFS does not expose alternate block sources to this adapter.

## State, Persistence, and Concurrency

The only adapter-local state is the Hadoop statistics reference; file position and buffering live in the parent OrangeFS input stream. Read and seek methods are synchronized, but positional methods combine multiple synchronized calls and are not atomic with respect to other thread operations between calls.

## Dependencies and Integration Points

It depends on Hadoop `FileSystem.Statistics`, `Seekable`, `PositionedReadable`, commons-logging, and the OrangeFS JNI input stream. It is constructed by `OrangeFileSystem.open` and returned inside `FSDataInputStream`.

## Risks and Test Signals

`readFully` does not loop until the buffer is full, so short reads can cause false failures even before EOF. It also increments statistics before null checks in some methods, so a null statistics object would fail before warning. Tests should cover EOF, short reads, positional reads preserving file position, seek/read interleavings, and byte counter accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/capacity-scheduler.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/capacity-scheduler.xml

## Purpose

This scheduler template configures the single default queue for the `Hadoop 1 MapReduce` example cluster. It is not OrangeFS code itself, but it controls MapReduce/YARN admission while jobs use `ofs://` storage.

## Important APIs, Types, and Functions

The file exposes queue capacity, user-limit, maximum-active-task/application, priority, and locality-delay settings consumed by Hadoop scheduler services.

Active properties observed:

- `mapred.capacity-scheduler.maximum-system-jobs` = `3000`
- `mapred.capacity-scheduler.queue.default.capacity` = `100`
- `mapred.capacity-scheduler.queue.default.maximum-capacity` = `-1`
- `mapred.capacity-scheduler.queue.default.supports-priority` = `false`
- `mapred.capacity-scheduler.queue.default.minimum-user-limit-percent` = `100`
- `mapred.capacity-scheduler.queue.default.user-limit-factor` = `1`
- `mapred.capacity-scheduler.queue.default.maximum-initialized-active-tasks` = `200000`
- `mapred.capacity-scheduler.queue.default.maximum-initialized-active-tasks-per-user` = `100000`
- `mapred.capacity-scheduler.queue.default.init-accept-jobs-factor` = `10`
- `mapred.capacity-scheduler.default-supports-priority` = `false`
- `mapred.capacity-scheduler.default-minimum-user-limit-percent` = `100`
- `mapred.capacity-scheduler.default-user-limit-factor` = `1`
- `mapred.capacity-scheduler.default-maximum-active-tasks-per-queue` = `200000`
- `mapred.capacity-scheduler.default-maximum-active-tasks-per-user` = `100000`
- `mapred.capacity-scheduler.default-init-accept-jobs-factor` = `10`
- `mapred.capacity-scheduler.init-poll-interval` = `5000`
- `mapred.capacity-scheduler.init-worker-threads` = `5`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/capacity-scheduler.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/core-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/core-site.xml

## Purpose

This `Hadoop 1 MapReduce` core-site file binds Hadoop's default filesystem to OrangeFS. It registers the `ofs` implementation class, maps the logical OrangeFS authority to a mounted OrangeFS path, and sets OrangeFS client buffer, block-size, and layout defaults used by the Java adapter.

## Important APIs, Types, and Functions

Important configuration keys are `fs.default.name`/`fs.defaultFS`, `fs.ofs.impl`, `fs.AbstractFileSystem.ofs.impl` for Hadoop 2, `fs.ofs.systems`, `fs.ofs.mntLocations`, `fs.ofs.file.buffer.size`, `fs.ofs.block.size`, and `fs.ofs.file.layout`.

Active properties observed:

- `fs.default.name` = `ofs://localhost-orangefs:3334`
- `fs.ofs.impl` = `org.apache.hadoop.fs.ofs.OrangeFileSystem`
- `hadoop.tmp.dir` = `/tmp/hadoop-${user.name}`
- `fs.ofs.systems` = `localhost-orangefs:3334`
- `fs.ofs.mntLocations` = `/mnt/orangefs`
- `fs.ofs.file.buffer.size` = `4194304`
- `fs.ofs.block.size` = `134217728`
- `fs.ofs.file.layout` = `PVFS_SYS_LAYOUT_ROUND_ROBIN`
- `io.compression.codecs` = `org.apache.hadoop.io.compress.GzipCodec, org.apache.hadoop.io.compress.DefaultCodec, org.apache.hadoop.io.compress.BZip2Codec, org.apache.hadoop.io.compress.SnappyCodec`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/core-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/fair-scheduler.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/fair-scheduler.xml

## Purpose

This Hadoop 1 fair-scheduler allocation template is effectively empty. It preserves the expected config-file slot while the example cluster uses default scheduler behavior or the capacity scheduler instead.

## Important APIs, Types, and Functions

There are no pool definitions, weights, minimum shares, ACLs, or preemption rules in the file.

Active properties observed:

- No concrete `<property>` entries are present.

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/fair-scheduler.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hadoop-env.sh.in -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hadoop-env.sh.in

## Purpose

This shell environment template initializes daemon/client environment variables for the OrangeFS Hadoop example. It contributes Java settings, log locations, Hadoop classpath entries, JNI library paths, and OrangeFS-specific variables.

## Important APIs, Types, and Functions

Key environment contracts are `JAVA_HOME`, `ORANGEFS_VERSION`, `ORANGEFS_PREFIX`, `LD_LIBRARY_PATH`, `JNI_LIBRARY_PATH`, `HADOOP_CLASSPATH`, `PVFS2TAB_FILE`, `ORANGEFS_STRIP_SIZE_AS_BLKSIZE`, and service-specific log/heap options.

Active directives observed:

- `export HADOOP_NAMENODE_OPTS="-Dcom.sun.management.jmxremote $HADOOP_NAMENODE_OPTS"`
- `export HADOOP_SECONDARYNAMENODE_OPTS="-Dcom.sun.management.jmxremote $HADOOP_SECONDARYNAMENODE_OPTS"`
- `export HADOOP_DATANODE_OPTS="-Dcom.sun.management.jmxremote $HADOOP_DATANODE_OPTS"`
- `export HADOOP_BALANCER_OPTS="-Dcom.sun.management.jmxremote $HADOOP_BALANCER_OPTS"`
- `export HADOOP_JOBTRACKER_OPTS="-Dcom.sun.management.jmxremote $HADOOP_JOBTRACKER_OPTS"`
- `export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-amd64"`
- `export ORANGEFS_VERSION="@PVFS2_VERSION_MAJOR@.@PVFS2_VERSION_MINOR@.@PVFS2_VERSION_SUB@"`
- `export ORANGEFS_PREFIX="/opt/orangefs"`
- `export LD_LIBRARY_PATH="$ORANGEFS_PREFIX/lib"`
- `export JNI_LIBRARY_PATH="$ORANGEFS_PREFIX/lib"`
- `export HADOOP_CLASSPATH="$JNI_LIBRARY_PATH/orangefs-jni-${ORANGEFS_VERSION}.jar:$JNI_LIBRARY_PATH/orangefs-hadoop1-${ORANGEFS_VERSION}.jar"`
- `export PVFS2TAB_FILE="/tmp/orangefs_hadoop_storage/pvfs2tab"`
- `export ORANGEFS_STRIP_SIZE_AS_BLKSIZE=true`
- `export HADOOP_LOG_DIR=/tmp/hadoop-${USER}/hadoop1logs`

## Control Flow

Hadoop startup scripts source this file before launching daemons or clients. Autoconf substitutes the OrangeFS version placeholders, then the classpath entries make the `orangefs-hadoop*` and `orangefs-jni` jars visible to Hadoop.

## State, Persistence, and Concurrency

The file does not persist application data. It controls process environment and log placement; changes require restarting the affected daemon or rerunning the client command.

## Dependencies and Integration Points

It depends on a valid Java installation, Hadoop's shell launcher conventions, OrangeFS libraries under `/opt/orangefs` by default, and the generated JNI/Hadoop jars in `ORANGEFS_PREFIX/lib`.

## Risks and Test Signals

Hard-coded Java 7 paths, mutable `/tmp` log locations, and missing JNI library paths are common failure points. Test signals are successful daemon startup, no `UnsatisfiedLinkError`, and OrangeFS classes visible in `hadoop classpath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hadoop-env.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hadoop-policy.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hadoop-policy.xml

## Purpose

This policy template opens Hadoop service RPC ACLs for the local OrangeFS example cluster. It allows client, admin, NameNode/DataNode or YARN/MapReduce protocols to run without per-user ACL setup.

## Important APIs, Types, and Functions

Each `security.*.acl` property is an RPC service authorization list. The template sets the listed ACLs to `*`, allowing all users.

Active properties observed:

- `security.client.protocol.acl` = `*`
- `security.client.datanode.protocol.acl` = `*`
- `security.datanode.protocol.acl` = `*`
- `security.inter.datanode.protocol.acl` = `*`
- `security.namenode.protocol.acl` = `*`
- `security.inter.tracker.protocol.acl` = `*`
- `security.job.submission.protocol.acl` = `*`
- `security.task.umbilical.protocol.acl` = `*`
- `security.refresh.policy.protocol.acl` = `*`
- `security.admin.operations.protocol.acl` = `*`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hadoop-policy.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hdfs-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hdfs-site.xml

## Purpose

This `Hadoop 1 MapReduce` HDFS-site template is intentionally almost empty because the example stack uses OrangeFS as the filesystem rather than a real HDFS namespace.

## Important APIs, Types, and Functions

There are no active HDFS service properties in this file; Hadoop still loads it as part of the conventional configuration directory.

Active properties observed:

- No concrete `<property>` entries are present.

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/mapred-queue-acls.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/mapred-queue-acls.xml

## Purpose

This Hadoop 1 queue ACL template defines submit and administer ACL properties for the default MapReduce queue. The values are blank, leaving access behavior to Hadoop's interpretation and the surrounding security configuration.

## Important APIs, Types, and Functions

The active keys are `mapred.queue.default.acl-submit-job` and `mapred.queue.default.acl-administer-jobs`.

Active properties observed:

- `mapred.queue.default.acl-submit-job` = ``
- `mapred.queue.default.acl-administer-jobs` = ``

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/mapred-queue-acls.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/mapred-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/mapred-site.xml

## Purpose

This MapReduce configuration directs jobs to run against the OrangeFS-backed Hadoop deployment. In Hadoop 2 it selects YARN and places staging, history, system, and health paths under `ofs://localhost-orangefs:3334`; in Hadoop 1 it configures the job tracker and task counts.

## Important APIs, Types, and Functions

Important properties cover framework selection, job tracker or YARN staging, local/system/temp directories, map/reduce resource sizing, speculative execution, compression, and task retry policy.

Active properties observed:

- `mapred.job.tracker` = `localhost:8021`
- `mapred.child.java.opts` = `-Xmx400m`
- `mapred.map.tasks` = `2`
- `mapred.reduce.tasks` = `1`
- `mapred.tasktracker.map.tasks.maximum` = `2`
- `mapred.tasktracker.reduce.tasks.maximum` = `1`
- `mapred.job.reuse.jvm.num.tasks` = `-1`
- `mapred.local.dir` = `/pvfs/data/mapred/local`
- `mapred.system.dir` = `/mapred/system`
- `mapreduce.jobtracker.staging.root.dir` = `/user`
- `mapred.temp.dir` = `/mapred/temp`
- `mapred.map.tasks.speculative.execution` = `false`
- `mapred.reduce.tasks.speculative.execution` = `false`
- `mapred.reduce.slowstart.completed.maps` = `0.95`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/mapred-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/orangefs-server.conf -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/orangefs-server.conf

## Purpose

This OrangeFS server configuration defines the single-node filesystem used by the Hadoop examples. It sets defaults, the `localhost` BMI/TCP alias, filesystem identity, root handle, metadata/data handle ranges, storage directories, log file, and storage hints.

## Important APIs, Types, and Functions

Important directives are `Alias localhost tcp://localhost:3334`, filesystem `Name orangefs`, `RootHandle`, `DataStorageSpace`, `MetadataStorageSpace`, handle ranges, `FileStuffing`, distributed-directory parameters, and Trove storage hints.

Active directives observed:

- `<Defaults>`
- `UnexpectedRequests 50`
- `EventLogging none`
- `EnableTracing no`
- `LogStamp datetime`
- `BMIModules bmi_tcp`
- `FlowModules flowproto_multiqueue`
- `PerfUpdateInterval 1000`
- `ServerJobBMITimeoutSecs 30`
- `ServerJobFlowTimeoutSecs 30`
- `ClientJobBMITimeoutSecs 300`
- `ClientJobFlowTimeoutSecs 300`
- `ClientRetryLimit 5`
- `ClientRetryDelayMilliSecs 2000`
- `PrecreateBatchSize 0,32,512,32,32,32,0`
- `PrecreateLowThreshold 0,16,256,16,16,16,0`
- `DataStorageSpace /tmp/orangefs_hadoop_storage/data`
- `MetadataStorageSpace /tmp/orangefs_hadoop_storage/meta`
- `LogFile /tmp/orangefs_hadoop_storage/orangefs-server.log`
- `</Defaults>`

## Control Flow

`pvfs2-server` reads the file during format (`-f`) and normal startup. The example scripts format, copy `pvfs2tab`, start the server, and ping the mounted filesystem; Hadoop clients then connect through the configured `ofs://localhost-orangefs:3334` authority.

## State, Persistence, and Concurrency

The config itself is static, while the data and metadata directories under `/tmp/orangefs_hadoop_storage` hold the persistent test filesystem state. Cleanup scripts remove those directories, effectively destroying the example volume.

## Dependencies and Integration Points

It must agree with `core-site.xml`, `pvfs2tab`, `/mnt/orangefs`, and OrangeFS binaries under `ORANGEFS_PREFIX`.

## Risks and Test Signals

Using `/tmp` makes the example volatile. Handle ranges and root handles are hard-coded for one server, so copying this into a multi-server deployment without regeneration is unsafe. Tests should format, start, `pvfs2-ping`, create a file through Hadoop, restart, and verify visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/orangefs-server.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/taskcontroller.cfg -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/taskcontroller.cfg

## Purpose

This executor/task-controller configuration is a placeholder for privileged Hadoop task execution settings in the example cluster.

## Important APIs, Types, and Functions

The active keys describe local directories, log directories, task kill grace periods, Linux container-executor group, banned users, minimum uid, and allowed system users depending on Hadoop generation.

Active directives observed:

- `mapred.local.dir=#configured value of mapred.local.dir. It can be a list of comma separated paths.`
- `hadoop.log.dir=#configured value of hadoop.log.dir.`
- `mapred.tasktracker.tasks.sleeptime-before-sigkill=#sleep time before sig kill is to be sent to process group after sigterm is sent. Should be in seconds`
- `mapreduce.tasktracker.group=#configured value of mapreduce.tasktracker.group.`

## Control Flow

Hadoop task controller or NodeManager container-executor reads the file when secure/local container launch support is enabled. The example leaves values as comments/placeholders, so normal non-secure examples do not depend on it.

## State, Persistence, and Concurrency

No data is persisted by this file. It gates process launch permissions when enabled.

## Dependencies and Integration Points

It depends on Hadoop native/container-executor installation, filesystem permissions, and matching groups/users on all worker nodes.

## Risks and Test Signals

Leaving placeholders in a secure deployment can block task launch or accidentally permit/deny the wrong users. Test by running a small YARN/MapReduce job under the intended user and checking NodeManager/task-controller logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/src/main/resources/conf/taskcontroller.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/build-and-install.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/build-and-install.sh

## Purpose

Builds the Hadoop 2 OrangeFS adapter jar with Maven using Java 7 source/target settings, skips tests, and installs the versioned jar into `ORANGEFS_PREFIX/lib`.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `sudo cp target/orangefs-hadoop2-?.?.?.jar "${ORANGEFS_PREFIX}/lib/"`

## Control Flow

The script changes to its own directory, runs `mvn ... clean package`, and only copies the jar if Maven succeeds because the commands are chained with `&&`.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires Maven, a compatible JDK, generated `pom.xml`, `ORANGEFS_PREFIX`, sudo rights, and the OrangeFS JNI artifact available to Maven.

## Risks and Test Signals

Skipping tests can install a broken adapter. The wildcard jar copy assumes exactly one matching target jar. Test by running Maven with tests separately and verifying Hadoop can load `org.apache.hadoop.fs.ofs.OrangeFileSystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/build-and-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/pom.xml.in -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/pom.xml.in

## Purpose

This Maven POM template builds the `orangefs-hadoop2` jar that registers OrangeFS as a Hadoop 2 `FileSystem` and `AbstractFileSystem` implementation. Autoconf substitutes the OrangeFS version into the project and JNI dependency versions.

## Important APIs, Types, and Functions

Important coordinates are `org.apache.hadoop.fs.ofs:orangefs-hadoop2`, dependency `org.apache.hadoop:hadoop-common:2.7.2`, dependency `org.orangefs.usrint:orangefs-jni`, and test dependencies on JUnit plus Hadoop test APIs.

## Control Flow

Maven reads the substituted POM during package builds, compiles Java sources under `src/main/java`, resolves declared dependencies, and emits a versioned jar consumed by the OrangeFS installation or Hadoop classpath.

## State, Persistence, and Concurrency

The POM is build metadata only. It produces jar artifacts under `target/` and does not persist runtime filesystem state.

## Dependencies and Integration Points

Maven resolution must find the matching `orangefs-jni` version and Hadoop 2.7.2 artifacts. The build script supplies Java 7 source/target compiler flags externally.

## Risks and Test Signals

The test dependency `hadoop-test:1.0.0` is from an older Hadoop line and may be fragile with Hadoop 2.7.2. Test by building with and without skipped tests and by loading the jar in Hadoop's classpath.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/pom.xml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/relaunch.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/relaunch.sh

## Purpose

Restarts the complete local OrangeFS plus Hadoop 2 example stack in a fixed order for iterative testing.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `./scripts/examples/orangefs/stop_orangefs.sh`
- `./scripts/examples/hadoop/stop_hadoop.sh`
- `./scripts/examples/hadoop/cleanup_hadoop.sh`
- `./scripts/examples/orangefs/reset_orangefs.sh`
- `./scripts/examples/hadoop/start_hadoop.sh`

## Control Flow

It stops OrangeFS, stops Hadoop, cleans Hadoop local state, resets OrangeFS storage, then starts Hadoop. A TODO notes it does not fail fast when intermediate scripts fail.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Depends on all example scripts, `setenv` files, kill/ssh access, OrangeFS binaries, and Hadoop scripts.

## Risks and Test Signals

Because it ignores failures, later startup may hide an earlier stop/cleanup/reset problem. It also destroys OrangeFS example storage through reset. Verify by checking process state and running `hadoop fs` after relaunch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/relaunch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_clean.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_clean.sh

## Purpose

Runs Hadoop's `org.apache.hadoop.fs.TestDFSIO` benchmark in `clean` mode against the configured OrangeFS-backed Hadoop filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `org.apache.hadoop.fs.TestDFSIO \`

## Control Flow

The script enters its directory and invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} org.apache.hadoop.fs.TestDFSIO -clean` with two 64 MB files for read/write modes.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, Hadoop test classes on the classpath, and a running OrangeFS-backed Hadoop environment.

## Risks and Test Signals

Benchmark results are sensitive to `fs.ofs.file.buffer.size`, file layout, and leftover TestDFSIO data. Clean before and after runs; verify byte counts and task success in YARN logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_clean.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_read.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_read.sh

## Purpose

Runs Hadoop's `org.apache.hadoop.fs.TestDFSIO` benchmark in `read` mode against the configured OrangeFS-backed Hadoop filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `org.apache.hadoop.fs.TestDFSIO \`

## Control Flow

The script enters its directory and invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} org.apache.hadoop.fs.TestDFSIO -read` with two 64 MB files for read/write modes.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, Hadoop test classes on the classpath, and a running OrangeFS-backed Hadoop environment.

## Risks and Test Signals

Benchmark results are sensitive to `fs.ofs.file.buffer.size`, file layout, and leftover TestDFSIO data. Clean before and after runs; verify byte counts and task success in YARN logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_write.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_write.sh

## Purpose

Runs Hadoop's `org.apache.hadoop.fs.TestDFSIO` benchmark in `write` mode against the configured OrangeFS-backed Hadoop filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `org.apache.hadoop.fs.TestDFSIO \`

## Control Flow

The script enters its directory and invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} org.apache.hadoop.fs.TestDFSIO -write` with two 64 MB files for read/write modes.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, Hadoop test classes on the classpath, and a running OrangeFS-backed Hadoop environment.

## Risks and Test Signals

Benchmark results are sensitive to `fs.ofs.file.buffer.size`, file layout, and leftover TestDFSIO data. Clean before and after runs; verify byte counts and task success in YARN logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/cleanup_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/cleanup_hadoop.sh

## Purpose

Cleans or resets local Hadoop example runtime state. Cleanup removes `/tmp/hadoop-$USER` and `HADOOP_LOCAL_DIR` on each slave; reset stops daemons, cleans, and starts them again.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `for slave in $(cat $HADOOP_CONF_DIR/slaves); do`
- `ssh $slave "rm -rf /tmp/hadoop-$USER $HADOOP_LOCAL_DIR"`
- `done`

## Control Flow

The cleanup script sources `setenv` and loops over configured slaves with SSH. The reset wrapper sequences stop, sleep, cleanup, and start.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires `setenv`, `HADOOP_CONF_DIR/slaves`, SSH, and correct local-dir settings.

## Risks and Test Signals

It recursively removes paths from environment variables, so wrong variables can delete unintended data. Test in disposable environments and inspect expanded commands under `set -x`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/cleanup_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/hadoop_prog.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/hadoop_prog.sh

## Purpose

Manages the local OrangeFS example server lifecycle.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `${HADOOP_PREFIX}/bin/hadoop \`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/hadoop_prog.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/reset_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/reset_hadoop.sh

## Purpose

Cleans or resets local Hadoop example runtime state. Cleanup removes `/tmp/hadoop-$USER` and `HADOOP_LOCAL_DIR` on each slave; reset stops daemons, cleans, and starts them again.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `./stop_hadoop.sh`
- `sleep 3`
- `./cleanup_hadoop.sh`
- `./start_hadoop.sh`

## Control Flow

The cleanup script sources `setenv` and loops over configured slaves with SSH. The reset wrapper sequences stop, sleep, cleanup, and start.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires `setenv`, `HADOOP_CONF_DIR/slaves`, SSH, and correct local-dir settings.

## Risks and Test Signals

It recursively removes paths from environment variables, so wrong variables can delete unintended data. Test in disposable environments and inspect expanded commands under `set -x`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/reset_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_app_logs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_app_logs.sh

## Purpose

Summarizes Hadoop application or daemon logs by locating log files, counting ERROR/WARN/line totals, and optionally printing full contents.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `LOG_NAME=${1:-syslog}`
- `SHOW_LOGS=${2:-false}`
- `. setenv`
- `ALL_LOGS=$(find ${HADOOP_LOG_DIR} -name "${LOG_NAME}" | sort)`
- `WIDTH=-20`
- `echo`
- `printf "Found the following log files in HADOOP_LOG_DIR=%s\n" "${HADOOP_LOG_DIR}"`
- `printf "================================================================================\n"`
- `printf "%s\n" "${ALL_LOGS}"`
- `echo`
- `printf "Some log statistics:\n"`
- `printf "================================================================================\n"`
- `printf "%${WIDTH}s %${WIDTH}s %${WIDTH}s %s\n" "ERROR" "WARN" "LINES" "LOG_PATH"`
- `for logfile in ${ALL_LOGS}; do`
- `printf "%${WIDTH}s %${WIDTH}s %${WIDTH}s %${WIDTH}s\n" \`
- `"$(cat ${logfile} | grep ERROR | wc -l)" \`
- `"$(cat ${logfile} | grep WARN | wc -l)" \`

## Control Flow

The script sources `setenv`, finds matching log files under `HADOOP_LOG_DIR`, prints a table, and conditionally cats each log when requested.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires readable logs and standard shell tools `find`, `sort`, `grep`, `wc`, and `cat`.

## Risks and Test Signals

Unquoted iteration over log paths can break on spaces, and full log printing can be large. Test signal is accurate counts matching manual grep on representative logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_app_logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_daemon_logs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_daemon_logs.sh

## Purpose

Summarizes Hadoop application or daemon logs by locating log files, counting ERROR/WARN/line totals, and optionally printing full contents.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `SHOW_LOGS=${1:-false}`
- `. setenv`
- `ALL_LOGS=$(find ${HADOOP_LOG_DIR} -iname "*.log")`
- `WIDTH=-20`
- `echo`
- `printf "Found the following log files in HADOOP_LOG_DIR=%s\n" "${HADOOP_LOG_DIR}"`
- `printf "================================================================================\n"`
- `printf "%s\n" "${ALL_LOGS}"`
- `echo`
- `printf "Some log statistics:\n"`
- `printf "================================================================================\n"`
- `printf "%${WIDTH}s %${WIDTH}s %${WIDTH}s %s\n" "ERROR" "WARN" "LINES" "LOG_PATH"`
- `for logfile in ${ALL_LOGS}; do`
- `printf "%${WIDTH}s %${WIDTH}s %${WIDTH}s %${WIDTH}s\n" \`
- `"$(cat ${logfile} | grep ERROR | wc -l)" \`
- `"$(cat ${logfile} | grep WARN | wc -l)" \`
- `"$(cat ${logfile} | wc -l)" \`

## Control Flow

The script sources `setenv`, finds matching log files under `HADOOP_LOG_DIR`, prints a table, and conditionally cats each log when requested.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires readable logs and standard shell tools `find`, `sort`, `grep`, `wc`, and `cat`.

## Risks and Test Signals

Unquoted iteration over log paths can break on spaces, and full log printing can be large. Test signal is accurate counts matching manual grep on representative logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_daemon_logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/start_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/start_hadoop.sh

## Purpose

Starts the Hadoop 2 example daemons: ResourceManager locally and NodeManager, proxyserver, and historyserver through SSH for each configured slave.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} start resourcemanager`
- `for slave in $(cat $HADOOP_CONF_DIR/slaves); do`
- `ssh $slave "$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} start nodemanager"`
- `ssh $slave "$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} start proxyserver"`
- `ssh $slave "$HADOOP_PREFIX/sbin/mr-jobhistory-daemon.sh --config ${HADOOP_CONF_DIR} start historyserver"`
- `done`
- `echo "Visit http://localhost:8088"`

## Control Flow

It reads `$HADOOP_CONF_DIR/slaves`, runs Hadoop daemon scripts with `--config`, and uses SSH for worker-side services.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires passwordless SSH, valid `slaves`, Hadoop daemon scripts under `HADOOP_PREFIX`, and matching configuration on all nodes.

## Risks and Test Signals

No error aggregation is performed, so one failed SSH command can leave a partial cluster. Check daemon logs, ports, and the ResourceManager UI after execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/start_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/stop_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/stop_hadoop.sh

## Purpose

Stops the Hadoop 2 example daemons: ResourceManager locally and NodeManager, proxyserver, and historyserver through SSH for each configured slave.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} stop resourcemanager`
- `for slave in $(cat $HADOOP_CONF_DIR/slaves); do`
- `ssh $slave "$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} stop nodemanager"`
- `ssh $slave "$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} stop proxyserver"`
- `ssh $slave "$HADOOP_PREFIX/sbin/mr-jobhistory-daemon.sh --config ${HADOOP_CONF_DIR} stop historyserver"`
- `done`

## Control Flow

It reads `$HADOOP_CONF_DIR/slaves`, runs Hadoop daemon scripts with `--config`, and uses SSH for worker-side services.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires passwordless SSH, valid `slaves`, Hadoop daemon scripts under `HADOOP_PREFIX`, and matching configuration on all nodes.

## Risks and Test Signals

No error aggregation is performed, so one failed SSH command can leave a partial cluster. Check daemon logs, ports, and the ResourceManager UI after execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/stop_hadoop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/teragen.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/teragen.sh

## Purpose

Runs the Hadoop MapReduce examples jar command for `teragen` against the configured OrangeFS-backed filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `jar ${HADOOP_PREFIX}/share/hadoop/mapreduce/hadoop-mapreduce-examples-?.?.?.jar \`

## Control Flow

The script changes to its directory, optionally sources `setenv`, then runs `hadoop --config` with the examples jar and fixed/default input-output paths.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires Hadoop example jars matching the wildcard, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and a working YARN/MapReduce cluster using `ofs://` storage.

## Risks and Test Signals

Wildcard jar matching and hard-coded data directories can fail or collide with previous runs. Test by listing generated paths, checking job history, and validating output with `teravalidate` or `hadoop fs -cat` for wordcount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/teragen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/terasort.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/terasort.sh

## Purpose

Runs the Hadoop MapReduce examples jar command for `terasort` against the configured OrangeFS-backed filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `jar ${HADOOP_PREFIX}/share/hadoop/mapreduce/hadoop-mapreduce-examples-?.?.?.jar \`

## Control Flow

The script changes to its directory, optionally sources `setenv`, then runs `hadoop --config` with the examples jar and fixed/default input-output paths.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires Hadoop example jars matching the wildcard, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and a working YARN/MapReduce cluster using `ofs://` storage.

## Risks and Test Signals

Wildcard jar matching and hard-coded data directories can fail or collide with previous runs. Test by listing generated paths, checking job history, and validating output with `teravalidate` or `hadoop fs -cat` for wordcount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/terasort.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/teravalidate.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/teravalidate.sh

## Purpose

Runs the Hadoop MapReduce examples jar command for `teravalidate` against the configured OrangeFS-backed filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `jar ${HADOOP_PREFIX}/share/hadoop/mapreduce/hadoop-mapreduce-examples-?.?.?.jar \`

## Control Flow

The script changes to its directory, optionally sources `setenv`, then runs `hadoop --config` with the examples jar and fixed/default input-output paths.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires Hadoop example jars matching the wildcard, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and a working YARN/MapReduce cluster using `ofs://` storage.

## Risks and Test Signals

Wildcard jar matching and hard-coded data directories can fail or collide with previous runs. Test by listing generated paths, checking job history, and validating output with `teravalidate` or `hadoop fs -cat` for wordcount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/teravalidate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/wordcount.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/wordcount.sh

## Purpose

Runs the Hadoop MapReduce examples jar command for `wordcount` against the configured OrangeFS-backed filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `jar ${HADOOP_PREFIX}/share/hadoop/mapreduce/hadoop-mapreduce-examples-?.?.?.jar \`

## Control Flow

The script changes to its directory, optionally sources `setenv`, then runs `hadoop --config` with the examples jar and fixed/default input-output paths.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires Hadoop example jars matching the wildcard, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and a working YARN/MapReduce cluster using `ofs://` storage.

## Risks and Test Signals

Wildcard jar matching and hard-coded data directories can fail or collide with previous runs. Test by listing generated paths, checking job history, and validating output with `teravalidate` or `hadoop fs -cat` for wordcount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/wordcount.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/cleanup_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/cleanup_orangefs.sh

## Purpose

Deletes all files under the configured OrangeFS example storage directory.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `rm -rf ${ORANGEFS_STORAGE_DIR}/*`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/cleanup_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/init_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/init_orangefs.sh

## Purpose

Formats/initializes the OrangeFS server storage using `pvfs2-server -f` and the example config.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `${ORANGEFS_PREFIX}/sbin/pvfs2-server -a localhost ${ORANGEFS_CONF_FILE} -f`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/init_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/reset_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/reset_orangefs.sh

## Purpose

Stops, cleans, initializes, and starts the local OrangeFS example server.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `./stop_orangefs.sh`
- `sleep 1`
- `./cleanup_orangefs.sh`
- `sleep 1`
- `./init_orangefs.sh`
- `sleep 1`
- `./start_orangefs.sh`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/reset_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/start_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/start_orangefs.sh

## Purpose

Copies the pvfs2tab file, starts `pvfs2-server`, waits, and pings `/mnt/orangefs`.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `cp $PVFS2TAB_FILE /tmp/orangefs_hadoop_storage/pvfs2tab`
- `${ORANGEFS_PREFIX}/sbin/pvfs2-server -a localhost ${ORANGEFS_CONF_FILE}`
- `sleep 3`
- `${ORANGEFS_PREFIX}/bin/pvfs2-ping -m /mnt/orangefs`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/start_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/stop_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/stop_orangefs.sh

## Purpose

Stops all `pvfs2-server` processes with `killall`.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `killall pvfs2-server`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/stop_orangefs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/install_protoc.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/install_protoc.sh

## Purpose

Manages the local OrangeFS example server lifecycle.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `VERSION=2.5.0`
- `if [[ $EUID -ne 0 ]]; then`
- `echo "This script must be run as root" 1>&2`
- `fi`
- `TMP_DIR=/tmp/install_protoc`
- `trap 'rm -rf ${TMP_DIR}' EXIT && \`
- `cd ${TMP_DIR} && \`
- `wget http://protobuf.googlecode.com/files/protobuf-${VERSION}.tar.gz && \`
- `tar xzf protobuf-${VERSION}.tar.gz && \`
- `cd protobuf-${VERSION} && \`
- `./configure && \`
- `make && \`
- `sudo make install && \`
- `sudo ldconfig`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/install_protoc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/toggle_container_debug.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/toggle_container_debug.sh

## Purpose

Manages the local OrangeFS example server lifecycle.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `WHICH=${1:-on} # on or off`
- `UPDATE_USING_SUDO=true # set to false to update jar under your user account (not root)`
- `LINE1="log4j.logger.org.apache.hadoop.fs.ofs.OrangeFileSystem=DEBUG"`
- `LINE2="log4j.logger.org.apache.hadoop.fs.ofs.OrangeFS=DEBUG"`
- `TMP_DIR="/tmp"`
- `TARGET_FILE="container-log4j.properties"`
- `TARGET_JAR_PATH="$(find "${HADOOP_PREFIX}" -iname "hadoop-yarn-server-nodemanager-?.?.?.jar")"`
- `trap 'rm "${TMP_DIR}/${TARGET_FILE}"' EXIT`
- `cd "${TMP_DIR}"`
- `jar xf "${TARGET_JAR_PATH}" ${TARGET_FILE}`
- `if [ "$WHICH" = "off" ]; then`
- `printf "off\n"`
- `sed -i "/\b\(${LINE1}\|${LINE2}\)\b/d" "${TARGET_FILE}"`
- `fi`
- `if [ "$WHICH" = "on" ]; then`
- `printf "on\n"`
- `sed -i "/\b\(${LINE1}\|${LINE2}\)\b/d" "${TARGET_FILE}"`
- `printf "${LINE1}\n" >> "${TARGET_FILE}"`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/toggle_container_debug.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java

## Purpose

`OrangeFileSystem` is the primary Hadoop 2 `FileSystem` adapter for OrangeFS. It translates Hadoop `Path`, stream, permission, status, mkdir, delete, rename, and local-copy operations into OrangeFS JNI calls through the singleton `org.orangefs.usrint.Orange` facade.

## Important APIs, Types, and Functions

Important overridden APIs include `initialize`, `create`, deprecated `createNonRecursive`, `append`, `open`, `delete`, `exists`, `getFileStatus`, `listStatus`, `mkdirs`, `rename`, `setPermission`, local-copy hooks, `getUri`, `getWorkingDirectory`, and `setWorkingDirectory`. Internal helpers `getOFSPathName`, `getParentPaths`, `makeAbsolute`, and `isDirectory` handle Hadoop-to-mounted-path translation and directory walking. The class uses `PVFS2POSIXJNIFlags`, `PVFS2STDIOJNIFlags`, `OrangeFileSystemInputStream`, `OrangeFileSystemOutputStream`, `Stat`, and `OrangeFileSystemLayout`.

## Control Flow

Construction grabs the Orange singleton and flag objects but leaves the instance uninitialized. `initialize` validates URI authority, reads `fs.ofs.file.buffer.size`, `fs.ofs.block.size`, `fs.ofs.file.layout`, `fs.ofs.systems`, and `fs.ofs.mntLocations`, matches the URI authority to a mount path, initializes Hadoop statistics/local FS, and sets the working directory. File creation optionally deletes existing files, creates missing parents, opens an OrangeFS output stream with configured buffer/block/layout overrides, then applies Hadoop permissions. Reads construct `OrangeFileSystemFSInputStream`; metadata calls use POSIX `stat`; directory listing uses stdio directory enumeration and per-entry status calls.

## State, Persistence, and Concurrency

The class keeps per-instance configuration state: URI, mount prefix, working directory, local filesystem, buffer size, block size, layout, Hadoop statistics, and initialization flag. Persistent data is in OrangeFS via POSIX calls; Hadoop metadata is reconstructed from `stat` results on demand. Methods are mostly unsynchronized except stream reads/seeks, so callers rely on Hadoop `FileSystem` usage patterns and OrangeFS/POSIX semantics for concurrent mutation.

## Dependencies and Integration Points

It depends on Hadoop Common 2.x APIs, the OrangeFS JNI jar/native library, mounted OrangeFS paths, `core-site.xml` authority-to-mount configuration, and OrangeFS server/client processes. It integrates with MapReduce/YARN through `fs.ofs.impl` and with Hadoop statistics by incrementing read/write operation counters.

## Risks and Test Signals

Important risks are authority/mount mismatches, null-return-to-`null` behavior in `listStatus` where Hadoop often expects exceptions, `createNonRecursive` parent handling, hard-coded replication value `0`, sticky-bit removal in `setPermission`, and path translation through a local mount rather than pure URI access. Tests should cover initialization errors, multiple authorities, mkdir parent creation, overwrite behavior, permissions/umask, delete recursion, listStatus on files/directories/missing paths, working-directory relative paths, and live read/write through a mounted OrangeFS server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java

## Purpose

`OrangeFileSystemFSInputStream` adapts the OrangeFS JNI `OrangeFileSystemInputStream` to Hadoop's `Seekable` and `PositionedReadable` contracts while updating Hadoop `FileSystem.Statistics` counters.

## Important APIs, Types, and Functions

The class extends `org.orangefs.usrint.OrangeFileSystemInputStream` and implements `Closeable`, `Seekable`, and `PositionedReadable`. Important methods are the constructor, `getPos`, synchronized `read()` variants, positional `read(long, byte[], int, int)`, `readFully` variants, `seek`, and `seekToNewSource`.

## Control Flow

Construction opens the underlying OrangeFS stream and increments read operations. Normal reads delegate to the parent stream, then increment bytes-read when positive bytes are returned. Positional reads save the current offset, seek to the requested position, read, and seek back. `readFully` performs a single read and throws if it returns fewer bytes than requested. `seekToNewSource` always returns false because OrangeFS does not expose alternate block sources to this adapter.

## State, Persistence, and Concurrency

The only adapter-local state is the Hadoop statistics reference; file position and buffering live in the parent OrangeFS input stream. Read and seek methods are synchronized, but positional methods combine multiple synchronized calls and are not atomic with respect to other thread operations between calls.

## Dependencies and Integration Points

It depends on Hadoop `FileSystem.Statistics`, `Seekable`, `PositionedReadable`, commons-logging, and the OrangeFS JNI input stream. It is constructed by `OrangeFileSystem.open` and returned inside `FSDataInputStream`.

## Risks and Test Signals

`readFully` does not loop until the buffer is full, so short reads can cause false failures even before EOF. It also increments statistics before null checks in some methods, so a null statistics object would fail before warning. Tests should cover EOF, short reads, positional reads preserving file position, seek/read interleavings, and byte counter accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemUnderlying.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemUnderlying.java

## Purpose

`OrangeFileSystemUnderlying` is a close sibling of `OrangeFileSystem` that exposes the same OrangeFS-backed Hadoop `FileSystem` behavior plus a constructor accepting `Configuration` and `URI`, and a `getFsStatus` method backed by POSIX `fstatfs`. It appears intended for lower-level or test access to the underlying filesystem implementation.

## Important APIs, Types, and Functions

It implements the same major operations as `OrangeFileSystem`: `initialize`, `create`, `append`, `open`, `delete`, `exists`, `getFileStatus`, `listStatus`, `mkdirs`, `rename`, `setPermission`, `copyFromLocalFile`, `copyToLocalFile`, and working-directory accessors. Additional notable APIs are `OrangeFileSystemUnderlying(Configuration, URI)` and `getFsStatus(Path)`. It uses `Orange`, `PVFS2POSIXJNIFlags`, `PVFS2STDIOJNIFlags`, `Stat`, `Statfs`, and OrangeFS stream classes.

## Control Flow

The parameterized constructor initializes immediately. `initialize` mirrors the primary adapter's authority-to-mount matching. File operations map Hadoop paths through `getOFSPathName` into the configured mount path, then call OrangeFS POSIX/stdio JNI methods. `getFsStatus` opens the path with `O_RDONLY`, calls `fstatfs`, and returns Hadoop `FsStatus` from capacity/used/remaining fields.

## State, Persistence, and Concurrency

State is per instance and equivalent to the main adapter: OrangeFS mount mapping, URI, layout, buffer/block settings, working directory, local filesystem, and statistics. Persistent state is entirely OrangeFS-side. The `getFsStatus` implementation opens a file descriptor but does not close it in the inspected code, so repeated calls can leak descriptors.

## Dependencies and Integration Points

It integrates the Hadoop filesystem API with the OrangeFS JNI layer and the same configuration files as the primary adapter. Tests or components that need `FsStatus` may use this class where `OrangeFileSystem` does not expose that override.

## Risks and Test Signals

In addition to the primary adapter risks, `getFsStatus` should be tested for descriptor cleanup and behavior on directories, missing paths, and permission errors. The simplified `create` path does not perform the same overwrite/parent validation as `OrangeFileSystem`, so compatibility tests should compare behavior between the two classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemUnderlying.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFs.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFs.java

## Purpose

`OrangeFs` registers OrangeFS with Hadoop 2's newer `AbstractFileSystem` layer by delegating all operations to an `OrangeFileSystem` instance under the `ofs` scheme.

## Important APIs, Types, and Functions

The only constructor `OrangeFs(URI, Configuration)` calls `DelegateToFileSystem` with a new `OrangeFileSystem`, the scheme string `ofs`, and authority handling disabled via the final boolean argument.

## Control Flow

Hadoop loads this class through `fs.AbstractFileSystem.ofs.impl` in `core-site.xml`. Construction wires the `AbstractFileSystem` facade to the existing `FileSystem` implementation, so all real work flows into `OrangeFileSystem.initialize` and its operation overrides.

## State, Persistence, and Concurrency

This class owns no additional state beyond the delegate created by the superclass. Persistence and concurrency behavior are inherited from `OrangeFileSystem` and OrangeFS.

## Dependencies and Integration Points

It depends on Hadoop `DelegateToFileSystem`, `Configuration`, URI parsing, and the `OrangeFileSystem` class. It is the bridge needed by APIs that use `AbstractFileSystem` rather than `FileSystem.get` directly.

## Risks and Test Signals

The constructor has package visibility, matching Hadoop's reflective construction expectations for this era. Test by resolving `ofs://` paths through both `FileSystem` and `AbstractFileSystem` APIs and confirming operations route to the same OrangeFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/capacity-scheduler.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/capacity-scheduler.xml

## Purpose

This scheduler template configures the single default queue for the `Hadoop 2/YARN` example cluster. It is not OrangeFS code itself, but it controls MapReduce/YARN admission while jobs use `ofs://` storage.

## Important APIs, Types, and Functions

The file exposes queue capacity, user-limit, maximum-active-task/application, priority, and locality-delay settings consumed by Hadoop scheduler services.

Active properties observed:

- `yarn.scheduler.capacity.maximum-applications` = `10000`
- `yarn.scheduler.capacity.maximum-am-resource-percent` = `0.3`
- `yarn.scheduler.capacity.resource-calculator` = `org.apache.hadoop.yarn.util.resource.DefaultResourceCalculator`
- `yarn.scheduler.capacity.root.queues` = `default`
- `yarn.scheduler.capacity.root.default.capacity` = `100`
- `yarn.scheduler.capacity.root.default.user-limit-factor` = `1`
- `yarn.scheduler.capacity.root.default.maximum-capacity` = `100`
- `yarn.scheduler.capacity.root.default.state` = `RUNNING`
- `yarn.scheduler.capacity.root.default.acl_submit_applications` = `*`
- `yarn.scheduler.capacity.root.default.acl_administer_queue` = `*`
- `yarn.scheduler.capacity.node-locality-delay` = `-1`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/capacity-scheduler.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/container-executor.cfg -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/container-executor.cfg

## Purpose

This executor/task-controller configuration is a placeholder for privileged Hadoop task execution settings in the example cluster.

## Important APIs, Types, and Functions

The active keys describe local directories, log directories, task kill grace periods, Linux container-executor group, banned users, minimum uid, and allowed system users depending on Hadoop generation.

Active directives observed:

- `yarn.nodemanager.linux-container-executor.group=#configured value of yarn.nodemanager.linux-container-executor.group`
- `banned.users=#comma separated list of users who can not run applications`
- `min.user.id=1000#Prevent other super-users`
- `allowed.system.users=##comma separated list of system users who CAN run applications`

## Control Flow

Hadoop task controller or NodeManager container-executor reads the file when secure/local container launch support is enabled. The example leaves values as comments/placeholders, so normal non-secure examples do not depend on it.

## State, Persistence, and Concurrency

No data is persisted by this file. It gates process launch permissions when enabled.

## Dependencies and Integration Points

It depends on Hadoop native/container-executor installation, filesystem permissions, and matching groups/users on all worker nodes.

## Risks and Test Signals

Leaving placeholders in a secure deployment can block task launch or accidentally permit/deny the wrong users. Test by running a small YARN/MapReduce job under the intended user and checking NodeManager/task-controller logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/container-executor.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/core-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/core-site.xml

## Purpose

This `Hadoop 2/YARN` core-site file binds Hadoop's default filesystem to OrangeFS. It registers the `ofs` implementation class, maps the logical OrangeFS authority to a mounted OrangeFS path, and sets OrangeFS client buffer, block-size, and layout defaults used by the Java adapter.

## Important APIs, Types, and Functions

Important configuration keys are `fs.default.name`/`fs.defaultFS`, `fs.ofs.impl`, `fs.AbstractFileSystem.ofs.impl` for Hadoop 2, `fs.ofs.systems`, `fs.ofs.mntLocations`, `fs.ofs.file.buffer.size`, `fs.ofs.block.size`, and `fs.ofs.file.layout`.

Active properties observed:

- `fs.default.name` = `ofs://localhost-orangefs:3334`
- `fs.ofs.impl` = `org.apache.hadoop.fs.ofs.OrangeFileSystem`
- `hadoop.tmp.dir` = `/tmp/hadoop-${user.name}`
- `fs.defaultFS` = `ofs://localhost-orangefs:3334`
- `fs.AbstractFileSystem.ofs.impl` = `org.apache.hadoop.fs.ofs.OrangeFs`
- `fs.ofs.systems` = `localhost-orangefs:3334`
- `fs.ofs.mntLocations` = `/mnt/orangefs`
- `fs.ofs.file.buffer.size` = `4194304`
- `fs.ofs.block.size` = `134217728`
- `fs.ofs.file.layout` = `PVFS_SYS_LAYOUT_ROUND_ROBIN`
- `io.compression.codecs` = `org.apache.hadoop.io.compress.GzipCodec, org.apache.hadoop.io.compress.DefaultCodec, org.apache.hadoop.io.compress.BZip2Codec, org.apache.hadoop.io.compress.SnappyCodec`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/core-site.xml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hadoop-policy.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hadoop-policy.xml

## Purpose

This policy template opens Hadoop service RPC ACLs for the local OrangeFS example cluster. It allows client, admin, NameNode/DataNode or YARN/MapReduce protocols to run without per-user ACL setup.

## Important APIs, Types, and Functions

Each `security.*.acl` property is an RPC service authorization list. The template sets the listed ACLs to `*`, allowing all users.

Active properties observed:

- `security.client.protocol.acl` = `*`
- `security.client.datanode.protocol.acl` = `*`
- `security.datanode.protocol.acl` = `*`
- `security.inter.datanode.protocol.acl` = `*`
- `security.namenode.protocol.acl` = `*`
- `security.admin.operations.protocol.acl` = `*`
- `security.refresh.usertogroups.mappings.protocol.acl` = `*`
- `security.refresh.policy.protocol.acl` = `*`
- `security.ha.service.protocol.acl` = `*`
- `security.zkfc.protocol.acl` = `*`
- `security.qjournal.service.protocol.acl` = `*`
- `security.mrhs.client.protocol.acl` = `*`
- `security.resourcetracker.protocol.acl` = `*`
- `security.resourcemanager-administration.protocol.acl` = `*`
- `security.applicationclient.protocol.acl` = `*`
- `security.applicationmaster.protocol.acl` = `*`
- `security.containermanagement.protocol.acl` = `*`
- `security.resourcelocalizer.protocol.acl` = `*`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hadoop-policy.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hdfs-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hdfs-site.xml

## Purpose

This `Hadoop 2/YARN` HDFS-site template is intentionally almost empty because the example stack uses OrangeFS as the filesystem rather than a real HDFS namespace.

## Important APIs, Types, and Functions

There are no active HDFS service properties in this file; Hadoop still loads it as part of the conventional configuration directory.

Active properties observed:

- No concrete `<property>` entries are present.

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/httpfs-env.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/httpfs-env.sh

## Purpose

This shell environment template initializes daemon/client environment variables for the OrangeFS Hadoop example. It contributes Java settings, log locations, Hadoop classpath entries, JNI library paths, and OrangeFS-specific variables.

## Important APIs, Types, and Functions

Key environment contracts are `JAVA_HOME`, `ORANGEFS_VERSION`, `ORANGEFS_PREFIX`, `LD_LIBRARY_PATH`, `JNI_LIBRARY_PATH`, `HADOOP_CLASSPATH`, `PVFS2TAB_FILE`, `ORANGEFS_STRIP_SIZE_AS_BLKSIZE`, and service-specific log/heap options.

Active directives observed:

- No active non-comment directives are present.

## Control Flow

Hadoop startup scripts source this file before launching daemons or clients. Autoconf substitutes the OrangeFS version placeholders, then the classpath entries make the `orangefs-hadoop*` and `orangefs-jni` jars visible to Hadoop.

## State, Persistence, and Concurrency

The file does not persist application data. It controls process environment and log placement; changes require restarting the affected daemon or rerunning the client command.

## Dependencies and Integration Points

It depends on a valid Java installation, Hadoop's shell launcher conventions, OrangeFS libraries under `/opt/orangefs` by default, and the generated JNI/Hadoop jars in `ORANGEFS_PREFIX/lib`.

## Risks and Test Signals

Hard-coded Java 7 paths, mutable `/tmp` log locations, and missing JNI library paths are common failure points. Test signals are successful daemon startup, no `UnsatisfiedLinkError`, and OrangeFS classes visible in `hadoop classpath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/httpfs-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/httpfs-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/httpfs-site.xml

## Purpose

This Hadoop 2 HttpFS site template is present as part of the stock config set but contains no active service overrides. It does not participate directly in OrangeFS filesystem binding unless HttpFS is separately enabled.

## Important APIs, Types, and Functions

No active HttpFS properties are defined.

Active properties observed:

- No concrete `<property>` entries are present.

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/httpfs-site.xml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/mapred-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/mapred-site.xml

## Purpose

This MapReduce configuration directs jobs to run against the OrangeFS-backed Hadoop deployment. In Hadoop 2 it selects YARN and places staging, history, system, and health paths under `ofs://localhost-orangefs:3334`; in Hadoop 1 it configures the job tracker and task counts.

## Important APIs, Types, and Functions

Important properties cover framework selection, job tracker or YARN staging, local/system/temp directories, map/reduce resource sizing, speculative execution, compression, and task retry policy.

Active properties observed:

- `mapreduce.framework.name` = `yarn`
- `yarn.app.mapreduce.am.staging-dir` = `ofs://localhost-orangefs:3334/tmp/hadoop-yarn/staging`
- `mapred.healthChecker.script.path` = `ofs://localhost-orangefs:3334/mapred/jobstatus`
- `mapred.job.tracker.history.completed.location` = `ofs://localhost-orangefs:3334/mapred/history/done`
- `mapred.system.dir` = `ofs://localhost-orangefs:3334/mapred/system`
- `mapreduce.jobhistory.done-dir` = `ofs://localhost-orangefs:3334/job-history/done`
- `mapreduce.jobhistory.intermediate-done-dir` = `ofs://localhost-orangefs:3334/job-history/intermediate-done`
- `mapreduce.jobtracker.staging.root.dir` = `ofs://localhost-orangefs:3334/user`
- `mapreduce.map.cpu.vcores` = `1`
- `mapreduce.reduce.cpu.vcores` = `1`
- `mapreduce.map.memory.mb` = `640`
- `mapreduce.map.java.opts` = `-Xmx512m`
- `mapreduce.reduce.memory.mb` = `1280`
- `mapreduce.reduce.java.opts` = `-Xmx1024m`
- `yarn.app.mapreduce.am.resource.mb` = `640`
- `yarn.app.mapreduce.am.command-opts` = `-Xmx512m`
- `mapreduce.task.io.sort.mb` = `256`
- `mapreduce.input.fileinputformat.split.minsize` = `67108864`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/mapred-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/orangefs-server.conf -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/orangefs-server.conf

## Purpose

This OrangeFS server configuration defines the single-node filesystem used by the Hadoop examples. It sets defaults, the `localhost` BMI/TCP alias, filesystem identity, root handle, metadata/data handle ranges, storage directories, log file, and storage hints.

## Important APIs, Types, and Functions

Important directives are `Alias localhost tcp://localhost:3334`, filesystem `Name orangefs`, `RootHandle`, `DataStorageSpace`, `MetadataStorageSpace`, handle ranges, `FileStuffing`, distributed-directory parameters, and Trove storage hints.

Active directives observed:

- `<Defaults>`
- `UnexpectedRequests 50`
- `EventLogging none`
- `EnableTracing no`
- `LogStamp datetime`
- `BMIModules bmi_tcp`
- `FlowModules flowproto_multiqueue`
- `PerfUpdateInterval 1000`
- `ServerJobBMITimeoutSecs 30`
- `ServerJobFlowTimeoutSecs 30`
- `ClientJobBMITimeoutSecs 300`
- `ClientJobFlowTimeoutSecs 300`
- `ClientRetryLimit 5`
- `ClientRetryDelayMilliSecs 2000`
- `PrecreateBatchSize 0,32,512,32,32,32,0`
- `PrecreateLowThreshold 0,16,256,16,16,16,0`
- `DataStorageSpace /tmp/orangefs_hadoop_storage/data`
- `MetadataStorageSpace /tmp/orangefs_hadoop_storage/meta`
- `LogFile /tmp/orangefs_hadoop_storage/orangefs-server.log`
- `</Defaults>`

## Control Flow

`pvfs2-server` reads the file during format (`-f`) and normal startup. The example scripts format, copy `pvfs2tab`, start the server, and ping the mounted filesystem; Hadoop clients then connect through the configured `ofs://localhost-orangefs:3334` authority.

## State, Persistence, and Concurrency

The config itself is static, while the data and metadata directories under `/tmp/orangefs_hadoop_storage` hold the persistent test filesystem state. Cleanup scripts remove those directories, effectively destroying the example volume.

## Dependencies and Integration Points

It must agree with `core-site.xml`, `pvfs2tab`, `/mnt/orangefs`, and OrangeFS binaries under `ORANGEFS_PREFIX`.

## Risks and Test Signals

Using `/tmp` makes the example volatile. Handle ranges and root handles are hard-coded for one server, so copying this into a multi-server deployment without regeneration is unsafe. Tests should format, start, `pvfs2-ping`, create a file through Hadoop, restart, and verify visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/orangefs-server.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/yarn-env.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/yarn-env.sh

## Purpose

This shell environment template initializes daemon/client environment variables for the OrangeFS Hadoop example. It contributes Java settings, log locations, Hadoop classpath entries, JNI library paths, and OrangeFS-specific variables.

## Important APIs, Types, and Functions

Key environment contracts are `JAVA_HOME`, `ORANGEFS_VERSION`, `ORANGEFS_PREFIX`, `LD_LIBRARY_PATH`, `JNI_LIBRARY_PATH`, `HADOOP_CLASSPATH`, `PVFS2TAB_FILE`, `ORANGEFS_STRIP_SIZE_AS_BLKSIZE`, and service-specific log/heap options.

Active directives observed:

- `export HADOOP_YARN_USER=${USER}`
- `export JAVA_HOME=${JAVA_HOME}`
- `if [ "$JAVA_HOME" = "" ]; then`
- `echo "Error: JAVA_HOME is not set."`
- `exit 1`
- `fi`
- `JAVA=$JAVA_HOME/bin/java`
- `JAVA_HEAP_MAX=-Xmx1000m`
- `if [ "$YARN_HEAPSIZE" != "" ]; then`
- `JAVA_HEAP_MAX="-Xmx""$YARN_HEAPSIZE""m"`
- `fi`
- `IFS=`
- `export YARN_LOG_DIR=/tmp/hadoop-${USER}/hadoop2logs`
- `if [ "$YARN_LOGFILE" = "" ]; then`
- `YARN_LOGFILE='yarn.log'`
- `fi`
- `if [ "$YARN_POLICYFILE" = "" ]; then`
- `YARN_POLICYFILE="hadoop-policy.xml"`
- `fi`
- `unset IFS`

## Control Flow

Hadoop startup scripts source this file before launching daemons or clients. Autoconf substitutes the OrangeFS version placeholders, then the classpath entries make the `orangefs-hadoop*` and `orangefs-jni` jars visible to Hadoop.

## State, Persistence, and Concurrency

The file does not persist application data. It controls process environment and log placement; changes require restarting the affected daemon or rerunning the client command.

## Dependencies and Integration Points

It depends on a valid Java installation, Hadoop's shell launcher conventions, OrangeFS libraries under `/opt/orangefs` by default, and the generated JNI/Hadoop jars in `ORANGEFS_PREFIX/lib`.

## Risks and Test Signals

Hard-coded Java 7 paths, mutable `/tmp` log locations, and missing JNI library paths are common failure points. Test signals are successful daemon startup, no `UnsatisfiedLinkError`, and OrangeFS classes visible in `hadoop classpath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/yarn-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/yarn-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/yarn-site.xml

## Purpose

This YARN site template describes a single-host ResourceManager/NodeManager setup used with the OrangeFS Hadoop 2 examples. It fixes service ports, NodeManager resources, shuffle service registration, classpath, and log aggregation.

## Important APIs, Types, and Functions

Important keys include ResourceManager addresses, `yarn.nodemanager.aux-services`, memory/vcore limits, `yarn.application.classpath`, and `yarn.log-aggregation-enable`.

Active properties observed:

- `yarn.resourcemanager.scheduler.address` = `localhost:8030`
- `yarn.resourcemanager.resource-tracker.address` = `localhost:8031`
- `yarn.resourcemanager.address` = `localhost:8032`
- `yarn.resourcemanager.admin.address` = `localhost:8033`
- `yarn.web-proxy.address` = `localhost:8034`
- `yarn.resourcemanager.webapp.address` = `localhost:8088`
- `yarn.nodemanager.hostname` = `localhost`
- `yarn.nodemanager.aux-services` = `mapreduce_shuffle`
- `yarn.nodemanager.aux-services.mapreduce_shuffle.class` = `org.apache.hadoop.mapred.ShuffleHandler`
- `yarn.nodemanager.vmem-check-enabled` = `false`
- `yarn.nodemanager.resource.cpu-vcores` = `1`
- `yarn.scheduler.minimum-allocation-mb` = `640`
- `yarn.scheduler.maximum-allocation-mb` = `1920`
- `yarn.nodemanager.resource.memory-mb` = `1920`
- `yarn.nodemanager.localizer.fetch.thread-count` = `3`
- `yarn.log-aggregation-enable` = `true`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/yarn-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/fs/ofs/OrangeFileSystemTest.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/fs/ofs/OrangeFileSystemTest.java

## Purpose

This JUnit class is a scaffold for direct `OrangeFileSystem` method testing. Its setup builds a configuration from `confPath` and initializes `ofs://localhost-orangefs:3334`, but most test methods are placeholders except constructor, initialization, and selected existence checks.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testOrangeFileSystem`
- `testAppendPathIntProgressable`
- `testCompleteLocalOutputPathPath`
- `testCopyFromLocalFileBooleanPathPath`
- `testCopyToLocalFileBooleanPathPath`
- `testCreatePathFsPermissionBooleanIntShortLongProgressable`
- `testDeletePathBoolean`
- `testExistsPath`
- `testGetFileStatusPath`
- `testGetHomeDirectory`
- `testGetParentPaths`
- `testGetUri`
- `testGetWorkingDirectory`
- `testInitializeURIConfiguration`
- `testIsDir`
- `testListStatusPath`
- `testMakeAbsolute`
- `testMkdirsPathFsPermission`
- `testOpenPathInt`
- `testRenamePathPath`
- `testSetPermissionPathFsPermission`
- `testSetWorkingDirectoryPath`
- `testStartLocalOutputPathPath`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

Coverage is sparse and many tests are empty, so it mainly signals intended API surface rather than real regression protection. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/fs/ofs/OrangeFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnector.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnector.java

## Purpose

This connector source provides factory/interface glue for creating OrangeFS-backed Hadoop `FileSystem` instances in generic HCFS tests.

## Important APIs, Types, and Functions

Relevant test/API surface:

- No local `test*` methods; behavior is inherited from a Hadoop test base.

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

Mis-set `HCFS_TEST_CONNECTOR` environment/class property can make the test suite instantiate the wrong connector or fail reflectively. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorFactory.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorFactory.java

## Purpose

This connector source provides factory/interface glue for creating OrangeFS-backed Hadoop `FileSystem` instances in generic HCFS tests.

## Important APIs, Types, and Functions

Relevant test/API surface:

- No local `test*` methods; behavior is inherited from a Hadoop test base.

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

Mis-set `HCFS_TEST_CONNECTOR` environment/class property can make the test suite instantiate the wrong connector or fail reflectively. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorInterface.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorInterface.java

## Purpose

This connector source provides factory/interface glue for creating OrangeFS-backed Hadoop `FileSystem` instances in generic HCFS tests.

## Important APIs, Types, and Functions

Relevant test/API surface:

- No local `test*` methods; behavior is inherited from a Hadoop test base.

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

Mis-set `HCFS_TEST_CONNECTOR` environment/class property can make the test suite instantiate the wrong connector or fail reflectively. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorInterface.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSPerformanceIOTests.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSPerformanceIOTests.java

## Purpose

This class tests OrangeFS stream buffering behavior by writing around `DEFAULT_OFS_FILE_BUFFER_SIZE` and checking when data spills to the filesystem.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testBufferSpill`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

The assertions depend on buffer-size defaults and a live filesystem's length visibility. It is a useful signal for output-stream flush/spill behavior. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSPerformanceIOTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSTestWorkingDir.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSTestWorkingDir.java

## Purpose

This test verifies relative-path writes through a changed working directory. It creates a local temp file, copies it to a relative OrangeFS path, and checks existence.

## Important APIs, Types, and Functions

Relevant test/API surface:

- No local `test*` methods; behavior is inherited from a Hadoop test base.

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

It depends on correct `setWorkingDirectory`, local temp-file handling, and cleanup of the working test directory. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSTestWorkingDir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsFileSystemTest.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsFileSystemTest.java

## Purpose

This is the main live HCFS behavior test suite for the OrangeFS Hadoop adapter. It exercises encoded paths, tolerant recursive mkdirs, owner lookup, text IO, permission changes, directory listing/deletion, file IO, seek/available reads, and permission mutation.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testEncodedPaths`
- `testTolerantMkdirs`
- `testOwner`
- `testTextWriteAndRead`
- `testPermissions`
- `testZDirs`
- `testFiles`
- `testFileIO`
- `testPermissionsChanging`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

It requires a live configured OrangeFS filesystem and can leave state unless teardown succeeds. It provides the strongest functional signal for filesystem compatibility. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsMainOperationsBaseTest.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsMainOperationsBaseTest.java

## Purpose

This class adapts Hadoop's `FSMainOperationsBaseTest` to OrangeFS and adds tests for mkdir failure below existing files, absolute working directory behavior, glob behavior for missing files, and deleting missing paths.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testMkdirsFailsForSubdirectoryOfExistingFile`
- `testWDAbsolute`
- `testGlobStatusThrowsExceptionForNonExistentFile`
- `testDeleteNonExistentFile`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

Inherited Hadoop tests can expose semantic mismatches in exceptions, working directory handling, and path qualification. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsMainOperationsBaseTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsTestGetFileBlockLocations.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsTestGetFileBlockLocations.java

## Purpose

This class extends Hadoop's `TestGetFileBlockLocations` to run block-location contract checks against the OrangeFS-backed filesystem.

## Important APIs, Types, and Functions

Relevant test/API surface:

- No local `test*` methods; behavior is inherited from a Hadoop test base.

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

OrangeFS may not provide HDFS-style block locations, so inherited assertions are the key compatibility signal. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsTestGetFileBlockLocations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsUmaskTest.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsUmaskTest.java

## Purpose

This JUnit test checks directory creation under a configured umask, expecting `mkdirs` to produce a directory with permission `0755`.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testMkdirsWithUmask`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

It validates Hadoop permission and umask translation through OrangeFS `mkdir`/`chmod`; failures can indicate permission masking drift. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsUmaskTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/OrangeFSMultipleVolumeTest.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/OrangeFSMultipleVolumeTest.java

## Purpose

This test validates multiple OrangeFS authority mappings. It asks Hadoop for filesystems for `ofs://localhost-orangefs:3334` and `ofs://localhost-orangefs:3335`, checks existence on each configured volume, and verifies a missing path on one volume.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testDefaultPath`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

It depends on multiple configured OrangeFS systems/mounts; it is the main signal for `fs.ofs.systems` and `fs.ofs.mntLocations` matching logic. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/OrangeFSMultipleVolumeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2JNI_common.h -->
# sources/distributed-fs/orangefs/src/client/jni/libPVFS2JNI_common.h

## Purpose

`libPVFS2JNI_common.h` centralizes common native JNI support macros for the OrangeFS Java user interface. It normalizes `_GNU_SOURCE`, disables `_FORTIFY_SOURCE` for this native layer, includes `errno`/`stdio`, defines a default Java `ArrayList` size, and provides optional debug/error-printing macros.

## Important APIs, Types, and Functions

Important macros are `JNI_INITIAL_ARRAY_LIST_SIZE`, `NULL_JOBJECT`, `JNI_PFI`, `JNI_PRINT`, `JNI_ERROR`, and `JNI_PERROR`. `ENABLE_JNI_ERROR` and `ENABLE_JNI_PERROR` are enabled by default; function-entry and generic print tracing are disabled unless the macros are uncommented.

## Control Flow

C JNI implementation files include this header and call the macros around native operations. `JNI_PERROR` checks `errno` and prints line/function information plus `perror` output when native calls fail.

## State, Persistence, and Concurrency

The header owns no persistent state. Its macros write to stdout/stderr and read global `errno`, so output from concurrent JNI calls may interleave.

## Dependencies and Integration Points

It is shared by `libPVFS2POSIXJNI.c` and `libPVFS2STDIOJNI.c`, and indirectly supports the Java classes in `org.orangefs.usrint`.

## Risks and Test Signals

Default stderr error printing can be noisy in Hadoop containers. Disabling `_FORTIFY_SOURCE` may hide buffer misuse diagnostics. Test by compiling the JNI library with expected flags and exercising failure paths to ensure Java callers receive null/error returns while native diagnostics remain interpretable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2JNI_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2POSIXJNI.c -->
# sources/distributed-fs/orangefs/src/client/jni/libPVFS2POSIXJNI.c

## Purpose

`libPVFS2POSIXJNI.c` implements the native methods for `PVFS2POSIXJNI`, exposing a broad POSIX-like API to Java. It is the low-level bridge used by the Hadoop OrangeFS adapter for metadata, permissions, open/read/write/seek, directory creation, rename/delete, stat/statfs, xattrs, links, and time operations.

## Important APIs, Types, and Functions

The file exports JNI wrappers for `access`, `chmod`, `chown`, `close`, `creat`, `dup`, `faccessat`, `fallocate`, `fchmod*`, `fchown*`, `fdatasync`, `fsync`, `ftruncate`, `open`, `openWithHints`, `openat`, `pread`, `pwrite`, `read`, `write`, `lseek`, `mkdir`, `mkdirTolerateExisting`, `rename`, `rmdir`, `stat`, `lstat`, `fstat`, `statfs`, `fstatfs`, `statvfs`, `unlink`, `utime`, `utimes`, symlink/link APIs, and xattr list/remove APIs. Helpers `fill_stat`, `fill_statfs`, and related object construction translate native structs into Java `Stat`, `Statfs`, and `Statvfs` objects. `fillPVFS2POSIXJNIFlags` publishes native constants into Java.

## Control Flow

Each JNI function converts Java strings or byte arrays into native pointers, calls the corresponding libc/POSIX or OrangeFS-interposed function, checks failures with common macros, releases Java resources, and returns primitive values or Java wrapper objects. `openWithHints` adds OrangeFS-specific layout/striping hints before opening a file. `mkdirTolerateExisting` treats an existing directory as success to support recursive Hadoop `mkdirs` races.

## State, Persistence, and Concurrency

The file itself stores no global filesystem state, but it mutates OrangeFS/POSIX persistent state through file descriptors, paths, metadata, xattrs, and timestamps. File descriptor lifetime is controlled by Java callers. Native `errno` is process/thread-local but diagnostics are printed to stderr. Concurrent Java calls can operate on shared file descriptors if the caller shares them.

## Dependencies and Integration Points

It depends on JNI headers, POSIX headers, OrangeFS client interception/libraries available at runtime, and Java classes matching the native method names and signatures. Hadoop `OrangeFileSystem` uses this layer for `stat`, `mkdirTolerateExisting`, `chmod`, `rename`, `unlink`, `isDir`, and stream/file operations.

## Risks and Test Signals

Risks include Java/native signature drift, resource leaks on missing `ReleaseStringUTFChars`/descriptor close paths, partial read/write handling, platform differences in struct fields, `errno` reuse, and unsupported operations on OrangeFS. Tests should call every wrapper with success and failure cases, verify `Stat`/`Statfs` field mapping, exercise large reads/writes and xattrs, run under leak sanitizers where possible, and validate Hadoop operations that depend on `mkdirTolerateExisting` and `openWithHints`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2POSIXJNI.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2STDIOJNI.c -->
# sources/distributed-fs/orangefs/src/client/jni/libPVFS2STDIOJNI.c

## Purpose

`libPVFS2STDIOJNI.c` implements native methods for `PVFS2STDIOJNI`, exposing C stdio and directory/user/group helpers to Java. The Hadoop adapter relies on this file for directory listing, recursive directory deletion, and translating uid/gid values into names.

## Important APIs, Types, and Functions

Private helpers resolve users and groups: `get_groupname_by_gid`, `get_username_by_uid`, `get_gid_by_groupname`, and `get_uid_by_username`. JNI exports wrap `FILE*` operations such as `fopen`, `fdopen`, `fclose`, `fflush`, `fread`, `fwrite`, `fseek`, `ftell`, `fgets`, `fputs`, unlocked variants, `tmpfile`, and buffer controls; directory APIs such as `opendir`, `fdopendir`, `readdir`, `closedir`, `rewinddir`, `seekdir`, `telldir`, and `dirfd`; helper APIs `getEntriesInDir`, `recursiveDeleteDir`, `getUsername`, `getGroupname`, `getUid`, and `getGid`; and `fillPVFS2STDIOJNIFlags` for constants.

## Control Flow

Wrappers convert Java strings/arrays to native buffers, call stdio or directory routines, convert results back to Java primitives, strings, byte arrays, or `ArrayList` objects, and print diagnostics through common JNI macros. `getEntriesInDir` opens a directory, skips `.`/`..`, appends entry names to a Java `ArrayList`, and closes the directory. `recursiveDeleteDir` walks a directory tree and removes children before the parent.

## State, Persistence, and Concurrency

The file mutates persistent filesystem state through remove/recursive delete and writes through `FILE*`. Java stores native `FILE*`/`DIR*` pointers as `jlong`, so caller discipline controls lifetime and thread safety. User/group lookups consult system account databases and are not OrangeFS-specific.

## Dependencies and Integration Points

It depends on libc stdio/dirent/pwd/group APIs, JNI, the common JNI header, and matching Java native declarations. `OrangeFileSystem.getFileStatus` uses user/group lookup; `listStatus` uses `getEntriesInDir`; recursive delete uses `recursiveDeleteDir`.

## Risks and Test Signals

Risks include pointer-as-long misuse, recursive deletion of unintended paths, fixed 32-byte user/group buffers, directory iteration races, unlocked stdio variants, and Java/native signature drift. Tests should list directories with many entries, unusual names, and permission errors; verify recursive delete on nested trees; resolve uid/gid failures; and run file read/write wrappers through EOF and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/libPVFS2STDIOJNI.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/module.mk.in -->
# sources/distributed-fs/orangefs/src/client/jni/module.mk.in

## Purpose

`module.mk.in` wires the OrangeFS JNI component into the broader OrangeFS build when `BUILD_JNI` is enabled. It identifies native C sources and Java sources that belong to the JNI/user-interface library.

## Important APIs, Types, and Functions

Important variables are `JNI_DIR`, `JNI_JAVA_DIR`, `ORGDIR`, `USRC`, `JNIJAVA`, and `ULIBSRC`. `USRC` includes `libPVFS2POSIXJNI.c` and `libPVFS2STDIOJNI.c`; `JNIJAVA` lists POSIX/stdio wrappers, flags, stat classes, `Orange`, stream/channel classes, and layout enum support.

## Control Flow

The surrounding make system includes this fragment, checks `BUILD_JNI`, appends native sources to `ULIBSRC`, and uses the Java source list when packaging or installing the JNI Java interface.

## State, Persistence, and Concurrency

This is build metadata only. It produces native and Java artifacts but stores no runtime state.

## Dependencies and Integration Points

It integrates the JNI directory with OrangeFS's top-level build and must stay synchronized with Maven packaging and Java native declarations.

## Risks and Test Signals

Missing a Java class or C file here can make autotools builds differ from Maven/manual builds. Test by building with `BUILD_JNI` enabled and verifying the resulting jar/native library contain the same API surface expected by Hadoop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/pom.xml.in -->
# sources/distributed-fs/orangefs/src/client/jni/pom.xml.in

## Purpose

This Maven POM template builds the `orangefs-jni` Java jar that exposes OrangeFS/POSIX/stdio JNI classes to the Hadoop adapter and other Java clients.

## Important APIs, Types, and Functions

Important coordinates are `org.orangefs.usrint:orangefs-jni`; dependencies are commons-logging, log4j, and JUnit for tests. The compiler plugin is pinned to Java 5 source/target for older compatibility.

## Control Flow

Maven reads the substituted POM during package builds, compiles Java sources under `src/main/java`, resolves declared dependencies, and emits a versioned jar consumed by the OrangeFS installation or Hadoop classpath.

## State, Persistence, and Concurrency

The POM is build metadata only. It produces jar artifacts under `target/` and does not persist runtime filesystem state.

## Dependencies and Integration Points

The jar must match the native JNI shared library built from `libPVFS2POSIXJNI.c` and `libPVFS2STDIOJNI.c`, and its version is substituted from OrangeFS build variables.

## Risks and Test Signals

Java/native signature drift is the key risk: Maven can build Java while native methods fail at runtime. Test by running JNI smoke tests that load the native library and call stat/open/read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/pom.xml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Orange.java -->
# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Orange.java

## Purpose

`Orange` is the Java singleton facade for the OrangeFS direct-client JNI layer. It centralizes construction of `PVFS2POSIXJNI` and `PVFS2STDIOJNI` wrappers so higher-level code can access POSIX-style and stdio-style native operations through one object.

## Important APIs, Types, and Functions

The public API is `Orange.getInstance()`, returning the holder-based singleton. Public fields `posix` and `stdio` expose initialized `PVFS2POSIXJNI` and `PVFS2STDIOJNI` instances. The constructor is private.

## Control Flow

The nested `OrangeHolder` lazily initializes the singleton when `getInstance` is first called. The constructor creates both JNI wrapper objects, which are then reused by Hadoop adapters and Java stream classes.

## State, Persistence, and Concurrency

The singleton stores two mutable public wrapper references. It does not persist filesystem state itself; all persistence is through native calls. Holder-based initialization is thread-safe in Java, but the public fields can be reassigned by any code with access.

## Dependencies and Integration Points

It depends on the generated/manual JNI Java classes in `org.orangefs.usrint` and their native library bindings. `OrangeFileSystem` and `OrangeFileSystemUnderlying` call it during construction.

## Risks and Test Signals

Public mutable fields weaken singleton invariants. Tests should verify native library loading, flag initialization, and basic `posix.stat`/`stdio.getEntriesInDir` calls through `Orange.getInstance()` from multiple callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/Orange.java -->
