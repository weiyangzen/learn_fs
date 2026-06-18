# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ClusterConnector.java

Purpose: small abstraction hiding where diskbalancer cluster information comes from.

Important APIs/types/functions: `getNodes()` returns `List<DiskBalancerDataNode>` and may throw `Exception`; `getConnectorInfo()` returns a descriptive string for logs.

Control flow: implementations populate diskbalancer-native data model objects from a backing source, such as NameNode RPC storage reports or JSON files.

State and persistence behavior: the interface owns no state. Implementations may hold URIs, RPC clients, or parsed files.

Dependencies and integration points: consumed by `DiskBalancerCluster.readClusterInfo()` and constructed by `ConnectorFactory`. Implemented here by `DBNameNodeConnector` and `JsonNodeConnector`; tests also use in-memory/null connectors.

Risks: broad `throws Exception` simplifies implementations but pushes error classification to callers. Callers assume returned nodes already have volume density computed by `DiskBalancerDataNode.addVolume()`.

Test signals: diskbalancer command and data model tests use real, JSON, and test connectors to exercise this boundary.
