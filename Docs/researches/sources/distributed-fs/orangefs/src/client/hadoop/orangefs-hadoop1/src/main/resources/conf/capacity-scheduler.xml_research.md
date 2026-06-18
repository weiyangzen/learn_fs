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
