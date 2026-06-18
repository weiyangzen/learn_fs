# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ConnectorFactory.java

Purpose: factory for selecting the diskbalancer cluster connector from a cluster URI.

Important APIs/types/functions: `getCluster(URI clusterURI, Configuration conf)` logs URI/scheme and returns `JsonNodeConnector` when `scheme.startsWith("file")`, otherwise `DBNameNodeConnector`. Constructor is private.

Control flow: binary dispatch on URI scheme. File URIs are treated as serialized cluster models; all other schemes are treated as live HDFS NameNode endpoints.

State and persistence behavior: stateless; returns new connector instances each call.

Dependencies and integration points: used by `Command.readClusterInfo()`. Depends on URI-to-URL conversion for file connectors and `DBNameNodeConnector` construction for live clusters.

Risks: `startsWith("file")` is permissive; unexpected schemes starting with that prefix would be treated as JSON. Non-file URIs must be acceptable to `NameNodeConnector`.

Test signals: command tests create JSON connectors and live mini-cluster connectors; connector selection is indirectly covered by plan/report tests.
