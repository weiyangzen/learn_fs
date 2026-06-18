<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolManager.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolManager.java

Purpose: `BlockPoolManager` owns all `BPOfferService` instances in a DataNode, keyed by nameservice and block-pool id, and handles dynamic NameNode/nameservice refresh.

Important APIs and functions: `addBlockPool` adds a registered BPOS to the block-pool map. `getAllNamenodeThreads`, `get`, `remove`, `startAll`, `shutDownAll`, and `joinAll` control BPOS lifecycle. `refreshNamenodes` loads NameNode service and lifeline RPC addresses from configuration and delegates to `doRefreshNamenodes`. `createBPOS` is extracted for tests. `isSlownodeByBlockPoolId` and `isSlownode` aggregate slow-node state from BPOS instances.

Control flow and state: maps and the offer-service list are synchronized for structural changes, while the list itself is a `CopyOnWriteArrayList` for safe iteration. `doRefreshNamenodes` computes nameservices to add, remove, and refresh. It creates BPOS objects for added services under the manager lock, starts all services as the login user, stops removed services outside the manager lock so actor callbacks can call `remove`, and refreshes NN lists for existing services as the login user.

Persistence and dependencies: no direct persistence. It drives runtime connections to NameNodes and delegates storage registration to BPOS/DataNode. Dependencies include `DFSUtil` address parsing, `DFSConfigKeys`, `UserGroupInformation`, Guava-like collection helpers, and DataNode logging.

Integration points: DataNode uses this manager during startup and `refreshNamenodes`. BPOfferService calls back to `remove` when the last actor shuts down and to `addBlockPool` after successful block-pool registration elsewhere in the DataNode flow.

Risks and test signals: refresh sequencing is sensitive: newly added services are started while holding the manager lock, removed services are stopped later, and existing services refresh their actor lists. Null lifeline maps are tolerated. Tests should cover adding/removing nameservices, refreshing NN addresses inside a nameservice, map cleanup for never-registered BPOS, login-user `doAs` failures, and slow-node aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolManager.java -->
