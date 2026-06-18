# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRpcServer.java

Purpose: Tests NameNode RPC server binding, client IP proxying through caller context for block locality, HA failback with proxy users, and Observer NameNode handling of stale `addBlock` requests.

Important APIs and functions: `testNamenodeRpcBindAny` inspects `NameNodeRpcServer` listener host. `getPreferredLocation` uses `DistributedFileSystem.getClient().getLocatedBlocks`. Proxy tests use `CallerContext.CLIENT_IP_STR`, `DFS_NAMENODE_IP_PROXY_USERS`, and `UserGroupInformation.doAs`. Observer handling calls `NameNodeRpcServer.addBlock` directly and expects `ObserverRetryOnActiveException`.

Control flow: The bind test starts a cluster with `dfs.namenode.rpc-bind-host` set to `0.0.0.0`. Client IP proxy tests create clusters with known racks/hosts or QJM HA, set caller context, compare unauthorized random placement with authorized proxied placement, and verify failover/failback access. The observer test creates a three-NameNode QJM HA cluster, transitions one NameNode to observer, stops its edit log tailer, creates a file on active, confirms observer is stale, then asserts `addBlock` asks the client to retry on active.

State and persistence behavior: File creation persists blocks for placement and stale observer checks. Caller context is thread-local and restored in finally blocks. HA state transitions mutate NameNode roles.

Dependencies and integration points: Integrates MiniDFSCluster, MiniQJMHACluster, NameNode RPC protocols, block placement locality, caller context, UGI, observer reads, edit log tailing, and HDFS client located-block APIs.

Risks: Locality tests use randomness and repeat 20 trials, so they are probabilistic. CallerContext must be restored to avoid leaking into later tests. Observer behavior depends on stopping the edit log tailer to create a controlled stale namespace.

Test signals: Expected signals include wildcard RPC host binding, authorized proxy user consistently receiving the requested preferred host, HA failover preserving file status access, and stale observer `addBlock` throwing `ObserverRetryOnActiveException`.
