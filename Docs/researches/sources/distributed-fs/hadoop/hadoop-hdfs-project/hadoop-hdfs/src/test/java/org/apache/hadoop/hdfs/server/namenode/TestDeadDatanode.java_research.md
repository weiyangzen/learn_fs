# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeadDatanode.java

Purpose: Ensures NameNode behavior is correct for DataNodes that have transitioned to dead: protocol requests are rejected or redirected appropriately, dead nodes are excluded from placement, and capacity/non-DFS metrics are restored after re-registration.

Important APIs/types/functions: Uses `MiniDFSCluster`, `InternalDataNodeTestUtils.getDNRegistrationForBP`, `DFSTestUtil.waitForDatanodeState`, `DatanodeProtocol.blockReceivedAndDeleted`, `blockReport`, `sendHeartbeat`, `BlockManager.chooseTarget4NewBlock`, `DatanodeManager`, and `RegisterCommand`.

Control flow: One test shuts down a DataNode, waits until it is dead, submits IBRs/block reports/heartbeats using the old registration, and checks the response. Another verifies placement excludes the dead local client node. The re-registration test disables heartbeats, marks a node dead, checks aggregate accounting, reenables heartbeats, and waits for live re-registration.

State and persistence behavior: Targets in-memory DataNode descriptor liveness, registration state, aggregate capacity, and non-DFS-used counters. No durable restart is tested.

Dependencies and integration points: Covers DataNode protocol RPCs, asynchronous incremental block report processing, heartbeat commands, block placement policy, and NameNode capacity accounting.

Risks: Timing-sensitive liveness waits depend on heartbeat intervals. IBR processing is asynchronous, so the test flushes block operations.

Test signals: Dead IBRs do not re-register the node, block report throws, heartbeat returns a register command, placement excludes the dead descriptor, and aggregate counters match live descriptors before and after re-registration.
