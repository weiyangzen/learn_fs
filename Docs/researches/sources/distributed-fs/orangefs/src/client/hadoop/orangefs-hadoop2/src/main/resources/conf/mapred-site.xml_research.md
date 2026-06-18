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
