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
