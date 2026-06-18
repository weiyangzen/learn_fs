# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerRPCDelay.java

## Purpose
`TestBalancerRPCDelay` isolates balancer NameNode RPC throttling behavior. It verifies that balancer `getBlocks` calls are dispersed so the NameNode RPC queue is not saturated.

## Important APIs, Types, and Functions
The file delegates to `TestBalancer.testBalancerRPCDelay`. It uses `DFSConfigKeys.DFS_NAMENODE_GETBLOCKS_MAX_QPS_DEFAULT`, JUnit lifecycle methods, and class-level `@Timeout(100)`.

## Control Flow
`setup` constructs a `TestBalancer` instance and calls its setup method to initialize counters. `testBalancerRPCDelayQps3` runs the shared balancer RPC delay scenario with QPS 3. `testBalancerRPCDelayQpsDefault` runs the same scenario with the default configured QPS. `teardown` calls `TestBalancer.shutdown` to stop any cluster created by the delegated scenario.

## State and Persistence Behavior
All substantive state lives in the delegated `TestBalancer`: MiniDFSCluster, spied `FSNamesystem`, atomic counters for `getBlocks` count and timing, and balancer configuration. This wrapper owns lifecycle boundaries so the delegated cluster does not leak.

## Dependencies and Integration Points
The class integrates with `TestBalancer` rather than directly with HDFS internals. The underlying delegated path spies on NameNode `getBlocks` and verifies calls per second relative to configured QPS.

## Risks and Test Signals
Risks are inherited timing sensitivity: elapsed wall-clock duration is rounded to seconds and can vary under load. Signals are the underlying assertions that the number of `getBlocks` calls reaches the target and that calculated calls per second do not exceed the configured maximum.
