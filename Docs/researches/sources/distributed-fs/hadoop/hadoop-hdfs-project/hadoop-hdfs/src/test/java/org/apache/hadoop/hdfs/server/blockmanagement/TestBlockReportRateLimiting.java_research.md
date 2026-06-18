
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportRateLimiting.java

## Purpose
`TestBlockReportRateLimiting` verifies full block report lease rate limiting during DataNode startup and lease expiration recovery. It ensures only the configured number of full block report leases is active and that a failed/stopped datanode does not permanently block another datanode after lease expiry.

## Important APIs, Types, and Functions
The test configures `DFS_NAMENODE_MAX_FULL_BLOCK_REPORT_LEASES` and `DFS_NAMENODE_FULL_BLOCK_REPORT_LEASE_LENGTH_MS`. It overrides the static `BlockManagerFaultInjector.instance` to observe `incomingBlockReportRpc`, `requestBlockReportLease`, and `removeBlockReportLease`. Synchronization uses `Semaphore`, `AtomicReference`, `HashSet<DatanodeID>`, and `GenericTestUtils.waitFor`.

## Control Flow and State
`testRateLimitingDuringDataNodeStartup` sets the maximum leases to one, starts five datanodes, and uses the fault injector to block incoming full reports until the test releases a semaphore one datanode at a time. It tracks expected and actual datanode IDs and fails if a lease ID is zero or more than one lease is issued simultaneously. `testLeaseExpiration` starts a two-node cluster with a 100 ms lease, records the first node granted a lease, stops it, injects an IOException for its report, and waits for the other node to successfully send a leased full report after expiration.

## Dependencies and Integration Points
This file integrates the NameNode full block report lease manager, MiniDFSCluster datanode startup, fault injection hooks, and block report RPC contexts. `@AfterEach` restores a normal fault injector to avoid cross-test contamination.

## Risks and Test Signals
The tests are timing and concurrency sensitive. They mitigate this with semaphores, atomics, and bounded waits. Strong signals are the absence of zero-lease bypass reports, exact one-at-a-time lease issuance, and successful progress after the first lessee fails.
