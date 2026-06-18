# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestExportsTable.java

## Purpose
`TestExportsTable` verifies NFS export-point discovery and validation for HDFS and ViewFs-backed configurations.

## Important APIs, Types, And Functions
The tests use `MiniDFSCluster`, federated `MiniDFSNNTopology`, ViewFs `ConfigUtil.addLink`, `Nfs3`, `Mountd`, and `RpcProgramMountd.getExports`. Cases cover root HDFS export, multiple ViewFs export links, internal ViewFs export, invalid ViewFs root export, internal HDFS export, and invalid local filesystem export.

## Control Flow
Each test configures ephemeral NFS/mount/http ports, starts a MiniDFSCluster, optionally builds ViewFs links to federated HDFS namespaces, starts NFS, and asserts the mount daemon's export list. Invalid configurations assert `FileSystemException` messages indicating unsupported underlying schemes.

## State And Persistence
Tests create temporary MiniDFSCluster state and HDFS directories such as `/user1`, `/user2`, `/myexport1`, and ViewFs links in configuration. Clusters are shut down in `finally` blocks.

## Dependencies And Integration Points
This suite covers integration among export configuration, mount daemon export reporting, NFS startup validation, HDFS filesystems, and ViewFs resolution.

## Risks
Assertions use `assertTrue` equality checks and message substrings rather than stronger typed status objects. Startup of full MiniDFS clusters makes tests relatively heavy. Export ordering is assumed for the multiple-export case.

## Test Signals
Passing indicates NFS exports are advertised correctly for valid HDFS/ViewFs internal paths and fail fast for unsupported root ViewFs or local filesystem configurations.
