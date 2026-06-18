# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/IncrementalBlockReportManager.java

Purpose: `IncrementalBlockReportManager` batches and sends incremental block reports (IBRs) from a DataNode actor to a NameNode between full block reports. It tracks per-storage received, receiving, and deleted block changes.

Important APIs and types: `notifyNamenodeBlock` queues a `ReceivedDeletedBlockInfo`; `triggerIBR` marks reports ready and optionally forces immediate timing; `sendImmediately`, `waitTillNextIBR`, and `sendIBRs` coordinate actor heartbeat timing. `PerStorageIBR` stores one pending entry per `Block`, supports remove/removeAll/put/putMissing, and increments pending-block metrics by status.

Control flow: adding an RDBI first removes older entries for the same block across all storages, then inserts it for the target storage. `RECEIVING_BLOCK` sets `readyToSend` for the next heartbeat; `RECEIVED_BLOCK` triggers immediate reporting, forced for transient storage. `sendIBRs` snapshots and clears pending reports under synchronization, performs the NameNode RPC outside the lock, records metrics and `lastIBR` on success, or requeues missing reports and logs on failure.

State and persistence: state is in-memory per BP service actor: `pendingIBRs`, `readyToSend`, `ibrInterval`, `lastIBR`, and metrics. Persistence is externalized by the NameNode RPC `blockReceivedAndDeleted`; failed RPCs are requeued so events are not lost unless process state is lost.

Dependencies and integration points: it depends on `DatanodeProtocol`, `DatanodeRegistration`, `DatanodeStorage`, `StorageReceivedDeletedBlocks`, `ReceivedDeletedBlockInfo`, `BlockStatus`, `DataNodeMetrics`, and `Time.monotonicNow`. It is driven by DataNode block lifecycle events and BP service actor heartbeat loops.

Risks: metrics for pending blocks increment on `put`, but `generateIBRs` resets only aggregate pending counts after removal; tests should ensure status-specific counters are interpreted correctly. `putMissing` assumes a `PerStorageIBR` already exists for each storage in failed reports. Process crash loses pending in-memory reports, relying on later full block reports for convergence. Synchronization protects maps but RPC occurs outside locks, so newer entries can coexist while old reports are in flight.

Test signals: verify duplicate block replacement across storages, timing gates for `sendImmediately`, forced transient reports, success metrics and `lastIBR`, failure requeue without overwriting newer entries, deletion report test trigger wait, empty report no-op, and `clearIBRs` behavior.
