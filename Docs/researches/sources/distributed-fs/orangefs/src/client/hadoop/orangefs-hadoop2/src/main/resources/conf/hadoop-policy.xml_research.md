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
