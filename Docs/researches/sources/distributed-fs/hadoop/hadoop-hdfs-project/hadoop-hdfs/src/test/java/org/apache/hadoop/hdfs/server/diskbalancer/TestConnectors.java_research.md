# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/diskbalancer/TestConnectors.java

## Purpose

`TestConnectors` validates disk balancer cluster connectors for live NameNode discovery and JSON serialization/parsing of discovered cluster topology.

## Important APIs and types

- `ConnectorFactory.getCluster(URI, Configuration)` creates a `ClusterConnector` from an HDFS filesystem URI.
- `DiskBalancerCluster.readClusterInfo` loads DataNode and volume topology.
- `DiskBalancerCluster.toJson` and `parseJson` round-trip cluster model data.
- `MiniDFSCluster` supplies a live three-DataNode test cluster with default two volumes per DataNode.

## Control flow

Setup starts a three-DataNode MiniDFSCluster. The NameNode connector test waits for active cluster state, gets a connector for the filesystem URI, reads cluster info, and asserts the discovered node count is three and the first node has two volumes. The JSON connector test reads the same live topology, serializes it to JSON, parses it back, and asserts the node count is preserved.

## State and persistence behavior

The only persistent state is MiniDFSCluster test storage, removed by cluster shutdown. The JSON string is in-memory and not written to disk.

## Dependencies and integration points

This file connects NameNode-reported DataNode storage topology to the disk balancer model layer and validates that JSON connector semantics can represent that topology.

## Risks and edge cases

- It checks counts only, not detailed volume fields after JSON parse.
- Default volume count assumptions depend on MiniDFSCluster defaults.
- It does not test file-based JSON connector loading directly.

## Test signals

Strong signals are live connector discovery from an HDFS URI, expected DataNode count, expected per-node volume count, and successful JSON round-trip at the cluster model level.
