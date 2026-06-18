# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsDataLocality.java

## Purpose
`TestWebHdfsDataLocality` verifies WebHDFS DataNode selection for HTTP redirects. It ensures create operations prefer a local DataNode, read/checksum/append operations choose a block replica, excluded DataNodes are avoided, invalid exclusions are harmless, and a not-yet-initialized NameNode fails with a clear error.

## Important APIs, Types, and Functions
The file uses `NamenodeWebHdfsMethods.chooseDatanode`, `MiniDFSCluster` with racks/hosts, `DistributedFileSystem`, `DatanodeManager`, `NameNodeAdapter.getBlockLocations`, `LocatedBlocks`, `LocatedBlock`, `HdfsFileStatus`, `PutOpParam.Op.CREATE`, `GetOpParam.Op.GETFILECHECKSUM/OPEN`, `PostOpParam.Op.APPEND`, and Mockito for an uninitialized `NameNode`.

## Control Flow
`testDataLocality` starts six DataNodes across three racks, verifies CREATE chooses the DataNode matching the client address, creates a one-replica file, finds its block location, and asserts GETFILECHECKSUM, OPEN, and APPEND choose that replica. `testExcludeDataNodes` creates a three-replica file with named hosts, builds an exclusion string from one then two replica transfer addresses, and checks each read-like operation avoids excluded hosts. `testExcludeWrongDataNode` excludes a non-existent host and expects no failure. `testChooseDatanodeBeforeNamesystemInit` uses a mocked NameNode with null namesystem and expects `IOException`.

## State and Persistence Behavior
State is live cluster block placement and DataNode topology. There is no persistence or restart behavior.

## Dependencies and Integration Points
This is a WebHDFS/NameNode placement integration test covering network topology, block manager DataNode lookup, file status lookup, operation-specific redirect logic, and exclusion parsing.

## Risks and Edge Cases
Risks include redirecting clients away from local or replica DataNodes, ignoring exclude lists and causing retry loops, failing when exclusions reference unknown hosts, and null-pointer failures before namesystem initialization. The first CREATE loop computes each DataNode IP but passes loopback as client host, so it depends on MiniDFSCluster/DataNodeManager local-address behavior.

## Test Signals
Signals are equality with expected DataNode IP or replica `DatanodeInfo`, inequality against excluded hosts, absence of failure for unknown exclusions, and a specific initialization error substring.
