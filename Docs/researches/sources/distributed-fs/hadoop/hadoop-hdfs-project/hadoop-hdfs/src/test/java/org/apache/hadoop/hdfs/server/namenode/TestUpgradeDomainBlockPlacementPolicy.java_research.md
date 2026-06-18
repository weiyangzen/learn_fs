# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestUpgradeDomainBlockPlacementPolicy.java

## Purpose

`TestUpgradeDomainBlockPlacementPolicy` is an end-to-end test for `BlockPlacementPolicyWithUpgradeDomain` using combined host admin properties and decommission scenarios.

## Important APIs, Types, and Functions

The fixture configures six DataNodes across two racks with upgrade domains, uses `CombinedHostFileManager`, `HostsFileWriter`, `DatanodeAdminProperties`, and sets `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` to `BlockPlacementPolicyWithUpgradeDomain`. Helpers refresh admin properties, create files, wait for replication, and inspect `LocatedBlocks`.

## Control Flow

Setup starts six DataNodes with host/rack mapping, writes admin JSON-like include entries using resolvable DataNode IP/ports, assigns upgrade domains, marks selected nodes decommissioned, refreshes the DataNodeManager, and records expected normal nodes. `testPlacement` writes a replicated file and verifies every block includes required expected normal DataNodes. `testPlacementAfterDecommission` changes which nodes are decommissioned, waits until locations satisfy the new expected set, then calls placement-policy verification.

## State and Persistence Behavior

State lives in the MiniDFSCluster block map, host include file, DataNode admin state, upgrade-domain assignments, and replicated files. File block locations persist until decommission/re-replication changes them.

## Dependencies and Integration Points

It integrates host configuration loading, DataNodeManager refresh, rack awareness, upgrade-domain placement policy, decommissioning, replication, client block-location APIs, and block-placement verification.

## Risks and Edge Cases

Unresolved hostnames are rejected by `CombinedHostFileManager`, so the test uses IPs from actual DataNode IDs. The expected placement sets are based on exact upgrade-domain and rack combinations; changes to policy heuristics can affect assertions.

## Test Signals

Signals include all normal block locations containing required expected DataNode IDs after initial placement, eventual convergence after decommission changes, and `BlockPlacementStatus.isPlacementPolicySatisfied()` for every block.
