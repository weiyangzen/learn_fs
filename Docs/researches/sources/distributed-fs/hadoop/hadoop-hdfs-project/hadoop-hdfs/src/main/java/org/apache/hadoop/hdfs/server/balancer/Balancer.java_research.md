# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Balancer.java

## Purpose
`Balancer` is the command-line and service implementation that rebalances HDFS disk utilization by moving blocks from over-utilized DataNode storage groups to under-utilized ones. It implements `BalancerMXBean` for version metadata and coordinates NameNode connectors, dispatch scheduling, metrics, optional HTTP UI, and CLI parsing.

## Important APIs and types
Core instance methods include the constructor, `runOneIteration`, `init`, `chooseStorageGroups`, `matchSourceWithTargetToMove`, `resetData`, and MXBean getters. Static orchestration methods include `run`, `doBalance`, `stop`, `startBalancerHttpServer`, `checkKeytabAndInit`, and `time2Str`. Nested `Result` records per-iteration outcome and counters. Nested `Cli` parses options and invokes the balancer through `ToolRunner`.

## Control flow
Construction validates relevant config values, creates a `Dispatcher`, stores filter/policy parameters, creates metrics, and registers the MXBean. Each iteration asks the dispatcher for DataNode storage reports, uses the selected `BalancingPolicy` to compute average utilization per storage type, classifies storage groups into over-utilized, above-average, below-average, and under-utilized collections, optionally sorts or limits over-utilized sources, and computes bytes left to move. If the cluster is already balanced or upgrade state forbids movement, it exits early. Otherwise it matches sources and targets by node group, rack, then any other topology, schedules tasks on sources/targets, and asks the dispatcher to move blocks until no progress or completion.

## State and persistence
Instance state is iteration-local scheduler state plus references to `Dispatcher`, `NameNodeConnector`, policy, filters, threshold, movement limits, metrics, and MXBean name. The shared persistent coordination marker is `/system/balancer.id`, created through `NameNodeConnector` to prevent concurrent balancers. The class does not persist moved-block state; it relies on NameNode block maps and DataNode storage reports.

## Dependencies and integration points
It integrates with `Dispatcher`, `NameNodeConnector`, block placement policy validation, NameNode RPC URIs, DataNode storage reports, `StorageType`, Hadoop metrics, MBeans, optional `BalancerHttpServer`, Kerberos login, host-list parsing, DFS configuration keys, and command-line scripts. It requires `BlockPlacementPolicyDefault` for contiguous blocks.

## Risks and edge cases
Balancing decisions are based on periodically refreshed reports, so concurrent client writes/deletes can make target utilization drift. Running during an unfinalized upgrade is blocked by default because moved source blocks may not reclaim space. Include/exclude/source/target filters can make a cluster appear unbalanceable. The service mode uses a static `serviceRunning` flag and retry counters, so tests must reset global state. Limiting over-utilized nodes after computing overload bytes can change scheduled work without recalculating the earlier byte estimate.

## Test signals
Tests should cover CLI parsing and mutual exclusion of host filters, threshold bounds, block-pool filtering, policy compatibility failures, utilization classification, source/target matching by topology level, max bytes-to-move calculations, upgrade blocking, no-move and no-progress exits, metrics/MXBean registration cleanup, service-mode duplicate start prevention, keytab login, and HTTP server lifecycle.
