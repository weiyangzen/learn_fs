# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyExcludeSlowNodes.java

## Purpose
`TestReplicationPolicyExcludeSlowNodes` verifies that slow-peer telemetry can be converted into a slow-node exclusion set and honored by multiple block placement policies. It also verifies that disabling peer statistics through reconfiguration clears the global slow-node set.

## Important APIs, types, and functions
The parameterized class runs with `BlockPlacementPolicyDefault`, `BlockPlacementPolicyWithUpgradeDomain`, `AvailableSpaceBlockPlacementPolicy`, `BlockPlacementPolicyRackFaultTolerant`, and `AvailableSpaceRackFaultTolerantBlockPlacementPolicy`. It enables `DFS_DATANODE_PEER_STATS_ENABLED_KEY`, sets a one-second slow-peer collection interval, and enables `DFS_NAMENODE_BLOCKPLACEMENTPOLICY_EXCLUDE_SLOW_NODES_ENABLED_KEY`. It uses `SlowPeerTracker.addReport`, `OutlierMetrics`, `DatanodeManager.getSlowPeersUuidSet`, `DatanodeManager.getSlowNodesUuidSet`, and NameNode `reconfigureProperty`.

## Control flow
`testChooseTargetExcludeSlowNodes` registers all test DataNodes, adds peer reports so the first three DataNodes are reported slow by the last three, sleeps for the collector, then obtains the slow-peer UUID set. Choosing three targets from a slow writer must return only DataNodes not in the slow set. `testSlowPeerTrackerEnabledClearSlowNodes` adds reports, waits until the static slow-node set is populated, reconfigures peer statistics off, and asserts the set is cleared.

## State and persistence behavior
The state under test is the in-memory `SlowPeerTracker`, DatanodeManager collector initialization, static slow-node UUID set, and placement-time exclusion behavior. Reconfiguration changes runtime NameNode configuration but no persistence is checked.

## Dependencies and integration points
This file integrates slow peer telemetry with block placement. It covers both direct tracker ingestion and the collector path that translates reports into DataNode UUID exclusions. The test intentionally runs across several policies to protect the shared exclusion hook.

## Risks and test signals
Signals include exact slow set size, membership by DataNode UUID, target count, and absence of slow UUIDs in chosen targets. The tests are timing-sensitive because collector execution is observed with sleep or `GenericTestUtils.waitFor`. Regressions include ignoring slow-node exclusions, not clearing slow state on disable, or policy-specific bypass of the shared slow-node filter.
