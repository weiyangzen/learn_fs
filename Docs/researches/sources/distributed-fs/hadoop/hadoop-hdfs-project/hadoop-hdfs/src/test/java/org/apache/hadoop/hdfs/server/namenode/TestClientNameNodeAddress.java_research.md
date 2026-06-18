# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestClientNameNodeAddress.java

Purpose: Verifies `NameNodeUtils.getClientNamenodeAddress` chooses the correct client-visible NameNode address for WebHDFS redirects across simple, missing, federated, and HA configurations.

Important APIs/types/functions: Uses `HdfsConfiguration`, `FS_DEFAULT_NAME_KEY`, `DFS_NAMESERVICES`, `DFS_HA_NAMENODES_KEY_PREFIX`, `DFS_NAMENODE_RPC_ADDRESS_KEY`, and `NameNodeUtils.getClientNamenodeAddress(Configuration, String)`.

Control flow: Each test builds an in-memory configuration and asserts either an address string or null. Simple cases cover `hdfs://host:port`, no port, no default FS, and no host. Federation tests distinguish HA logical nameservice results from non-HA physical RPC addresses.

State and persistence behavior: No persistent state is created; the tested state is configuration-derived address resolution.

Dependencies and integration points: Guards WebHDFS redirect address publication and behavior where the current nameservice ID influences the result in federated deployments.

Risks: Callers must handle null for incomplete default FS settings. In HA, the result is a logical nameservice ID rather than host:port.

Test signals: AssertJ equality and JUnit null assertions; no cluster startup is required.
