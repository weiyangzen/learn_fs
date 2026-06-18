# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInputStreamBlockLocations.java

Purpose: This parameterized test verifies DFSInputStream located-block cache refresh and deferred registration with the client-side located-block refresher, with expiration enabled and disabled.

Important APIs/types/functions: `DFSInputStream.refreshBlockLocations`, `getLastRefreshedBlocksAtForTesting`, `addToLocalDeadNodes`, `getLocalDeadNodes`, `chooseDataNode`, `DFSClient.getLocatedBlockRefresher`, and configuration keys for stale DataNodes, short-circuit reads, replication, prefetch size, and `DFS_CLIENT_REFRESH_READ_BLOCK_LOCATIONS_MS_KEY`.

Control flow: Each test initializes a seven-DataNode rack-aware cluster with four replicas, a 24-block file, and optional block-location expiration. `testRefreshBlockLocations` first proves no refresh occurs without a trigger, then fakes a local dead node and unresolved address cache to force refresh and validates changed located-block state. Deferred-registration tests open a stream, invoke a read/readFully/getAllBlocks before and after artificially aging `lastRefreshedBlocksAt`, and assert tracking only occurs when expiration is enabled. `testClearIgnoreListChooseDataNode` passes all replica locations in an ignore list and expects the list to be cleared so retry selection can proceed.

State and persistence behavior: The test creates large replicated files, mutates DFSInputStream internal dead-node and refresh timestamps through testing hooks, and checks registration state in the client refresher. Cleanup closes client/filesystem and deletes files on exit.

Dependencies and integration points: It connects NameNode stale-node avoidance, rack-aware block placement, client prefetching, located-block refresher registration, and hedged-read DataNode selection behavior.

Risks and test signals: Signals are object identity changes for `locatedBlocks`, timestamp advancement, dead-node clearing, refresher tracking state, and ignore-list size. Risks include heavy cluster/file setup and reliance on testing-only mutators and timing thresholds.
