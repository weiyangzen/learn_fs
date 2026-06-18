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
