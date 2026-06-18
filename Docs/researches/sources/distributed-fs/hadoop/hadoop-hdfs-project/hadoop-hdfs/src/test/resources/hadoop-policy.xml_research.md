# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hadoop-policy.xml

## Purpose

`hadoop-policy.xml` is the test security authorization policy for HDFS-related protocols. The complete 126-line file was read. It sets permissive ACLs for most service protocols while restricting refresh-policy operations to `${user.name}` so tests can exercise service-level authorization without blocking normal MiniDFSCluster protocol traffic.

## Important APIs, Types, and Functions

The file defines Hadoop service authorization ACL properties: `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.inter.datanode.protocol.acl`, `security.namenode.protocol.acl`, `security.inter.tracker.protocol.acl`, `security.job.submission.protocol.acl`, `security.task.umbilical.protocol.acl`, `security.refresh.policy.protocol.acl`, `security.ha.service.protocol.acl`, and `security.zkfc.protocol.acl`. Values are ACL strings parsed by Hadoop service authorization code, where `*` means all users and `${user.name}` resolves to the active test user.

## Control Flow

During secure or service-authorization-enabled tests, Hadoop loads this XML into `Configuration`, service authorization refresh logic maps protocol interfaces to these ACL properties, and RPC servers allow or deny callers based on the parsed user/group ACL. Most protocol checks short-circuit to allow because the value is `*`; refresh authorization remains user-specific.

## State and Persistence Behavior

The file is static test policy state. It persists no cluster data, but it affects the in-memory authorization tables used by NameNode, DataNode, HA service, ZKFC, and older MapReduce protocol tests if those services load this resource.

## Dependencies and Integration Points

It integrates with Hadoop `ServiceAuthorizationManager`, HDFS client/DataNode/NameNode RPC protocols, HA admin and ZKFC tests, and admin commands that refresh authorization policy. It shares the standard Hadoop policy XML schema used by production `hadoop-policy.xml` files.

## Risks and Edge Cases

The main risks are accidentally making tests too permissive for refresh-policy checks, breaking variable substitution for `${user.name}`, leaving obsolete MapReduce ACL keys that may still be expected by compatibility tests, or changing `*` ACLs in a way that causes unrelated protocol tests to fail under service authorization.

## Test Signals

Signals are MiniDFSCluster startup with service authorization enabled, successful DFSClient/DataNode/NameNode/HA/ZKFC RPCs for arbitrary test users, and targeted refresh-policy tests allowing only the configured current user.
