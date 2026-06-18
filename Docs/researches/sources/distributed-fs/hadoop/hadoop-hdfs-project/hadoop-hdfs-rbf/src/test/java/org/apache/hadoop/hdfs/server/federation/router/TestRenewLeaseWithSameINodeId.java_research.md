# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRenewLeaseWithSameINodeId.java

## Purpose

`TestRenewLeaseWithSameINodeId` verifies that a single Router-facing `DFSClient` can renew leases for multiple files in different namespaces even when the namespace-local inode ids are the same.

## Important APIs, types, and functions

The suite uses `MiniRouterDFSCluster`, `RouterContext`, `RouterConfigBuilder`, `MockResolver`, `DistributedFileSystem`, `FSDataOutputStream`, `HdfsFileStatus`, and `DFSClient` writer tracking. `globalSetUp()` starts a non-HA two-namespace cluster with three datanodes per nameservice, metrics, RPC, and quota enabled.

## Control flow

The test adds mock resolver locations `/ns0` and `/ns1` to different nameservices. It opens two output streams through the same `DistributedFileSystem`, one under each namespace, fetches file status from the underlying client, asserts the two `fileId` values match, and then asserts `getNumOfFilesBeingWritten()` is `2`. Closing both streams should reduce that count to `0`.

## State and persistence behavior

The test creates real files in the mini-cluster and tracks client-side lease-renewer state. The important state key is not just inode id, but the federated file identity that must distinguish namespace plus inode for active writes.

## Dependencies and integration points

This is an integration test for Router path resolution, DFSClient lease renewal, file creation, and open-file accounting across subclusters. It protects behavior where two namespaces can legitimately allocate identical inode ids.

## Risks and test signals

A failure indicates the client is conflating files by inode id alone or leaking writer state after stream close. The test focuses on two files and two namespaces; it does not stress long-running renewer threads beyond checking the in-memory writer count.
