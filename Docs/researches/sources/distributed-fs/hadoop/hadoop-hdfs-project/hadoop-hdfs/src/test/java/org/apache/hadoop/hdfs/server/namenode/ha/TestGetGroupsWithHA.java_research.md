# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestGetGroupsWithHA.java

## Purpose
`TestGetGroupsWithHA` adapts the generic `GetGroupsTestBase` to an HA HDFS cluster, ensuring the `GetGroups` admin tool resolves and contacts NameNodes correctly through HA failover configuration.

## Important APIs, Types, And Functions
The class extends `GetGroupsTestBase`, overrides `getTool(PrintStream)` to return `new GetGroups(conf, o)`, and uses JUnit `setUpNameNode`/`tearDownNameNode` to manage a no-DataNode `MiniDFSCluster` with `MiniDFSNNTopology.simpleHATopology()`.

## Control Flow
Setup creates a fresh `HdfsConfiguration`, starts the HA cluster, and calls `HATestUtil.setFailoverConfigurations` so the inherited base tests run the tool against a logical nameservice rather than a single physical NameNode. Teardown shuts down the cluster.

## State And Persistence
There is no meaningful persistent HDFS data. Test state is the HA cluster configuration and the base class's group-mapping assertions/output capture.

## Dependencies And Integration Points
The test integrates `GetGroups`, `GetGroupsTestBase`, `MiniDFSCluster`, `MiniDFSNNTopology`, and `HATestUtil`. It covers the non-`ClientProtocol` group-mapping RPC path in an HA configuration.

## Risks
Failures point to HA logical URI/proxy configuration issues for tools outside normal filesystem operations. Because the actual assertions live in the base class, this class is mostly wiring and can miss HA transition scenarios.

## Test Signals
Inherited `GetGroupsTestBase` tests pass using the HA-configured `GetGroups` tool, and teardown completes without cluster leaks.
