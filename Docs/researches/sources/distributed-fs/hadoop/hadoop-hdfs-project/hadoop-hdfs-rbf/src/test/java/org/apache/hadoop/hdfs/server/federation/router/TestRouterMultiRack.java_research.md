# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterMultiRack.java

## Purpose

`TestRouterMultiRack.java` verifies erasure-coding topology support results through a Router when two nameservices have independent datanodes spread across multiple racks. The source was read as a complete 129-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `DistributedFileSystem`, `ECTopologyVerifierResult`, router quota/RPC configuration, independent datanodes, and per-namespace `DistributedFileSystem` handles. The single test method is `testGetECTopologyResultForPolicies`.

## Control Flow

Setup starts a two-namespace cluster with nine datanodes per nameservice and an explicit rack list covering six racks. The test enables `RS-6-3-1024k` through the router, checks default enabled-policy support, queries unsupported and supported policy combinations, enables an unsupported `RS-10-4-1024k` policy through the router, and then toggles that policy on individual namespace filesystems to prove the federated result is unsupported if any namespace has an unsupported enabled policy.

## State and Persistence Behavior

EC policy state is mutated on the router filesystem and underlying namespace filesystems during the class-level mini-cluster lifetime. Cluster state is torn down after all tests.

## Dependencies and Integration Points

This test integrates Router EC policy RPC forwarding, topology aggregation across namespaces, rack placement metadata, and `ECTopologyVerifierResult` semantics.

## Risks and Edge Cases

The test assumes specific EC policy names and datanode/rack counts. It checks support booleans but not detailed error messages. Because policy state is changed multiple times, cleanup by cluster shutdown is important.

## Test Signals

Signals are `isSupported()` true for policies satisfiable by the configured topology and false for policies requiring more datanodes than any subcluster can provide or when one namespace has an unsupported enabled policy.
