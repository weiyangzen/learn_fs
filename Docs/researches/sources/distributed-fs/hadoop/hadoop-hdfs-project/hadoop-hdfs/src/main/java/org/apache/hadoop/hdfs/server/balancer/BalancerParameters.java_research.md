# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/BalancerParameters.java

## Purpose
`BalancerParameters` is an immutable parameter bundle for the balancer CLI and run loop. It captures balancing policy, thresholds, host filters, block-pool filters, service-mode flags, and scheduling options.

## Important APIs and types
The class exposes getters for policy, threshold, max idle iteration, included/excluded nodes, source/target include/exclude sets, block pools, upgrade behavior, service mode, top-node sorting, over-utilized limit, and hot-block time interval. The nested `Builder` provides setters for each option and `build()`.

## Control flow
Defaults are defined in the builder: node-level policy, threshold 10.0, default max idle iterations from `NameNodeConnector`, empty filter sets, not running during upgrade, not service mode, no top sorting, unlimited over-utilized nodes, and zero hot-block interval meaning "use configuration". `Balancer.Cli.parse` mutates a builder according to command-line options and then builds an immutable instance.

## State and persistence
State is in-memory immutable after construction, except the sets themselves are stored by reference and are not defensively copied. There is no persistence.

## Dependencies and integration points
It integrates with `Balancer`, `BalancingPolicy`, `NameNodeConnector`, and CLI parser host/block-pool option handling.

## Risks and edge cases
Because sets are not copied or wrapped by the constructor, callers could mutate parameter contents after build. Defaults use `Collections.emptySet`, which is immutable, but parser-created sets are mutable. `limitOverUtilizedNum` default is `Integer.MAX_VALUE`, effectively no limit.

## Test signals
Tests should verify all defaults, each builder setter, `toString` coverage, parser-to-parameter mapping, and that mutable input sets can affect built parameters if changed.
