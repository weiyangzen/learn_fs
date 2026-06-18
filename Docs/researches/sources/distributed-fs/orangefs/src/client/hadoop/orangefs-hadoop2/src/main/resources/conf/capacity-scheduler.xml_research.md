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
