# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerMXBean.java

## Purpose
`BalancerMXBean` defines the JMX management contract for balancer version and build metadata.

## Important APIs and types
It declares `getVersion()`, `getSoftwareVersion()`, and `getCompileInfo()`. `Balancer` implements these using `VersionInfo`.

## Control flow
There is no implementation flow in the interface. Runtime calls are made through JMX after `Balancer` registers itself with `MBeans.register("Balancer", "BalancerInfo", this)`.

## State and persistence
No state is held or persisted. Values reflect static Hadoop version/build metadata at runtime.

## Dependencies and integration points
It integrates with Hadoop metrics/JMX registration from `Balancer` and management tools that inspect balancer process metadata.

## Risks and edge cases
The contract is intentionally small, but external monitoring can depend on exact method availability. Implementations must avoid throwing from these simple metadata calls.

## Test signals
Tests should verify MBean registration exposes all three fields and that `Balancer.resetData` unregisters the MBean.
