# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/JsonNodeConnector.java

Purpose: file-backed connector that reads a serialized `DiskBalancerCluster` JSON model and returns its nodes.

Important APIs/types/functions: constructor stores a `URL`. `getNodes()` reads `clusterURI.getPath()` with Jackson `ObjectReader` for `DiskBalancerCluster`, logs the node count, and returns `cluster.getNodes()`. `getConnectorInfo()` describes the JSON cluster source.

Control flow: there is no transformation beyond Jackson deserialization. The JSON model must already contain the diskbalancer data model shape.

State and persistence behavior: holds only the source URL. It performs read-only local file access and returns in-memory model objects.

Dependencies and integration points: selected by `ConnectorFactory` for file URIs. Used for offline planning/reporting tests and hand-crafted cluster models under test resources.

Risks: deserialized nodes may not have lookup maps populated until `DiskBalancerCluster.readClusterInfo()` iterates them. Bad/missing JSON file errors propagate. The connector returns the model's existing nodes without recomputing density unless volume-set/node constructors and JSON data preserve needed state.

Test signals: `TestDiskBalancerCommand` uses JSON connector scenarios; package docs mention test resource JSON cluster samples.
