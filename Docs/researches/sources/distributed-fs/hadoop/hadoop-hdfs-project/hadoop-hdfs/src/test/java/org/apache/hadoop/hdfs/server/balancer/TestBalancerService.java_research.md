# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerService.java

## Purpose
`TestBalancerService` tests the balancer's long-running service mode (`-asService`). It verifies repeated balancing without process exit, retry behavior after NameNode outages, and service metrics/MBean exposure.

## Important APIs, Types, and Functions
Key APIs include `Balancer.Cli`, `Balancer.stop`, `Balancer.getExceptionsSinceLastBalance`, `MiniDFSCluster` HA topology, `HATestUtil`, `NameNodeProxies`, `SubjectInheritingThread`, `DefaultMetricsSystem`, `MetricsAsserts`, `ManagementFactory`, and `VersionInfo`. Helpers are `setupCluster`, `addOneDataNode`, and `newBalancerService`.

## Control Flow
`setupCluster` starts an HA MiniDFSCluster, transitions NameNode 0 active, creates a failover-aware `ClientProtocol`, and writes a replicated file to fill two DataNodes to 30 percent. `testBalancerServiceBalanceTwice` starts service mode, waits for metrics initialization and nonzero bytes-left-to-move, waits for balance, adds another node, waits for balance again, then stops the service. `testBalancerServiceOnError` shuts down the active NameNode, waits for exception accounting, restarts it, rebalances, and verifies the exception count resets. `testBalancerServiceMetrics` verifies the BalancerInfo MBean version/revision and metrics tag block pool ID.

## State and Persistence Behavior
State includes an HA MiniDFSCluster, a long-lived balancer service thread, service interval configuration, balancer global stop flag, exception counters, Hadoop metrics sources, and JMX MBeans. Each test stops the balancer and shuts down the cluster in `finally`.

## Dependencies and Integration Points
Integration points are service-mode CLI parsing, failover proxy configuration, HA NameNode active/standby transitions, DataNode heartbeats, balancer metrics source naming by block pool ID, JMX BalancerInfo, and `TestBalancer` utility methods.

## Risks and Test Signals
Risks include thread lifecycle leaks if `Balancer.stop()` is not reached, metrics source timing, HA retry timing, and MBean registration races. Signals include successful repeated utilization convergence, `BytesLeftToMove` and `BytesMovedInCurrentRun` gauges, nonzero then reset exception counter, BalancerInfo version/revision content, and block-pool metrics tag assertions.
