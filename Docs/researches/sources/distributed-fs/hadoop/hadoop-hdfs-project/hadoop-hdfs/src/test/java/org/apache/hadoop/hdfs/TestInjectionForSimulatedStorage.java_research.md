# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestInjectionForSimulatedStorage.java

## Purpose
Tests simulated-storage block injection and replication recovery: after simulated DNs lose block contents across restart, injected blocks on one DN should seed replication back to the configured factor.

## APIs and Control Flow
`waitForBlockReplication` polls `ClientProtocol.getBlockLocations` until each expected block has the requested number of locations. `testInjection` configures `SimulatedFSDataset`, creates a four-block file with replication 4, records all block reports, shuts down the cluster, restarts without formatting with twice as many simulated DNs and safemode threshold 0, extracts unique blocks from old reports, injects them into DN0 via `cluster.injectBlocks`, and waits for replication back to four replicas.

## State, Dependencies, Integration
State includes Namenode namespace persistence, simulated DN block reports, injected block lists, and replication queues. Dependencies include `SimulatedFSDataset`, `BlockListAsLongs`, `DatanodeStorage`, `DFSClient`, `MiniDFSCluster`, and `Time`. It integrates test-only simulated storage with block-manager replication scheduling.

## Risks and Test Signals
Signals are block count and per-block replica count convergence. Risks include unbounded wait when `maxWaitSec` is negative, simulated storage diverging from real disk behavior, and restart-without-format relying on preserved test storage dirs.
