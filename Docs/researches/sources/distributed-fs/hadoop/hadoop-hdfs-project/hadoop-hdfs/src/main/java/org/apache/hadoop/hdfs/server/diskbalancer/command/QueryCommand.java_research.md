# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/QueryCommand.java

Purpose: implements `hdfs diskbalancer -query <node[,node...]>`, reporting the current diskbalancer plan status from one or more DataNodes.

Important APIs/types/functions: constructor registers `-query` and `-verbose`. `execute()` validates node input, deduplicates/sorts node strings through `TreeSet`, fills a default DataNode IPC port when no `host:port` is supplied, gets a `ClientDatanodeProtocol`, calls `queryDiskBalancerPlan()`, and prints `Plan File`, `Plan ID`, and result. With `-verbose`, it appends `DiskBalancerWorkStatus.currentStateString()`.

Control flow: the command performs no NameNode cluster discovery; it connects directly to each requested DataNode. On the first `DiskBalancerException`, it logs and rethrows rather than continuing to later nodes.

State and persistence behavior: no durable state. It emits status text to the command print stream and logs progress.

Dependencies and integration points: depends on `DFS_DATANODE_IPC_ADDRESS_KEY` default port, `NetUtils`, `ClientDatanodeProtocol`, and DataNode `DiskBalancerWorkStatus`. It is the operational counterpart to `ExecuteCommand`.

Risks: the host:port regex requires two to five digits and treats anything else as a bare host, so unusual address formats may get the default port appended. Partial failures abort the whole multi-node query. It does not use `Command.getNodes()` cluster resolution, so UUIDs are not resolved unless usable as network names.

Test signals: `TestDiskBalancerCommand` includes query without submit and multiple-node query cases.
