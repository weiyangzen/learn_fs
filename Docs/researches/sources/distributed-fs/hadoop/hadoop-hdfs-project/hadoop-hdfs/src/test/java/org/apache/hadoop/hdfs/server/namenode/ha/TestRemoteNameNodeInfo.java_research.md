# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRemoteNameNodeInfo.java

Purpose: verifies parsing of remote NameNode metadata from HA configuration when a nameservice has more than two NameNodes.

Important APIs and types: `RemoteNameNodeInfo.getRemoteNameNodes`, `MiniDFSNNTopology`, `MiniDFSCluster.configureNameNodes`, `DFS_HA_NAMENODE_ID_KEY`, and `DFS_NAMENODE_RPC_ADDRESS_KEY`-derived topology configuration.

Control flow: the test builds an empty configuration, constructs a nameservice `ns1` with three NN IDs and IPC ports, asks `MiniDFSCluster.configureNameNodes` to materialize the HA keys, marks `nn1` as local, and calls `RemoteNameNodeInfo.getRemoteNameNodes(conf)` as well as `getRemoteNameNodes(conf, nameservice)`. It asserts both lists are equal.

State and persistence behavior: there is no cluster runtime or persistent namespace state. The only state is the configuration keyspace that maps nameservice and NN IDs to RPC addresses and local identity.

Dependencies and integration points: integrates with MiniDFS topology configuration helpers and production parsing logic for remote NameNode upload/checkpoint destinations.

Risks and test signals: the main risk is parsing only two peers or treating explicit nameservice and inferred nameservice paths differently. The equality assertion is a compact signal that both parsing entry points produce the same `RemoteNameNodeInfo` set for a three-NN HA topology.
