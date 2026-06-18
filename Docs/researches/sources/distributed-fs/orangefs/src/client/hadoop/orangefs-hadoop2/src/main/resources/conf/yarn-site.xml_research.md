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
