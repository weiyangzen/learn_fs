# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DataXceiverServer.java

Purpose: `DataXceiverServer` is the lightweight, non-IPC data-transfer listener for a DataNode. It accepts `Peer` connections from clients and other DataNodes, starts `DataXceiver` daemon threads, tracks active peers, enforces receiver limits, and owns shared transfer/balancer throttles.

Important APIs and types: `run()` is the accept loop; `kill`, `addPeer`, `closePeer`, `releasePeer`, `closeAllPeers`, `restartNotifyPeers`, `sendOOBToPeers`, and `stopWriters` manage connection lifecycle. `BlockBalanceThrottler` extends `DataTransferThrottler` and combines bandwidth throttling with a fair `Semaphore` for concurrent balancer moves. Reconfiguration methods include `updateBalancerMaxConcurrentMovers`, `setMaxXceiverCount`, and throttler setters/getters.

Control flow: the server loops while the DataNode should run and is not shutting down for upgrade. Each accepted peer is rejected if the current xceiver count exceeds `maxXceiverCount`; otherwise a daemon `DataXceiver` is started. Socket timeouts wake the loop for shutdown checks, asynchronous listener close is expected during shutdown, and OOM causes peer close plus a backoff sleep. At termination it closes the listener under lock, optionally interrupts peers for upgrade restart, waits briefly, then closes all peers and resets metrics.

State and persistence: in-memory state is guarded by `lock`: `peers`, `peersXceiver`, `closed`, and `noPeers`. Volatile state includes max receiver count and three transfer throttlers. It has no durable state; it mutates DataNode metrics and affects external socket state. `estimateBlockSize` supplies a fallback block length for older clients and downstream space checks.

Dependencies and integration points: it depends on `PeerServer`, `Peer`, `DataNode`, `Daemon`, `DataTransferThrottler`, and DFS config keys for xceiver count, block size, data-transfer bandwidth, read/write bandwidth, balance bandwidth, and concurrent mover limits. `DataXceiver` calls back into this server for peer registration, release, throttlers, and balancer permits.

Risks: active count enforcement checks `curXceiverCount > maxXceiverCount`, so boundary behavior allows the count to reach the configured maximum before rejecting later accepts. Reconfiguring balancer concurrency downward blocks while acquiring permits; interruption or timeout must preserve the old cap. Peer maps and metrics must stay paired across `releasePeer`, `closePeer`, and `closeAllPeers`, especially when domain sockets are handed to the short-circuit watcher.

Test signals: validate peer add/close metrics, shutdown-for-upgrade OOB and writer interruption, wait-for-no-peers behavior, listener close handling, max-xceiver rejection, independent read/write/transfer throttler configuration, and increasing/decreasing balancer mover limits under active permits.
