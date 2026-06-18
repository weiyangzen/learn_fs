# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancingPolicy.java

## Purpose
`BalancingPolicy` defines how the balancer computes utilization. It supports node-level balancing across all block pools and block-pool-level balancing for each pool on each node.

## Important APIs and types
Shared counters are `totalCapacities`, `totalUsedSpaces`, and `avgUtilizations`, keyed by `StorageType`. Abstract methods are `getName`, `accumulateSpaces`, and `getUtilization`. Shared helpers are `reset`, `initAvgUtilization`, `getAvgUtilization`, and `parse`. Concrete singleton policies are `Node.INSTANCE` and `Pool.INSTANCE`.

## Control flow
The balancer calls `accumulateSpaces` for every `DatanodeStorageReport`, then `initAvgUtilization` computes average utilization per storage type. It later calls `getUtilization` for each node/storage type to classify storage groups. `parse` maps CLI names `datanode` and `blockpool` to singleton policies.

## State and persistence
Policy instances hold mutable counters and averages across one balancer iteration and are reset between iterations by `Balancer.resetData`. They persist nothing. Since the concrete policies are singletons, reset discipline is important.

## Dependencies and integration points
It depends on `StorageType`, `DatanodeStorageReport`, `StorageReport`, `EnumCounters`, and `EnumDoubles`. It directly drives `Balancer.init` classification and byte estimates.

## Risks and edge cases
The singleton policy objects are mutable, so concurrent balancer runs sharing the same JVM could interfere if they use the same policy instance. The pool policy uses `remaining + blockPoolUsed` as capacity to avoid targeting nodes with little free space; this intentionally differs from raw disk capacity and changes scheduling behavior. Zero-capacity storage types produce null utilization.

## Test signals
Tests should verify policy parsing, reset behavior, average utilization by storage type, node policy aggregation across storage reports, pool policy use of block-pool-used plus remaining, null utilization on absent storage types, and singleton mutation isolation across iterations.
