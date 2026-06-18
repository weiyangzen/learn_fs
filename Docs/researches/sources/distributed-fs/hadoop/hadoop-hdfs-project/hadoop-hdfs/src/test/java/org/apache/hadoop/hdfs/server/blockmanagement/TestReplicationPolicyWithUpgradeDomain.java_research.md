# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestReplicationPolicyWithUpgradeDomain.java

## Purpose
`TestReplicationPolicyWithUpgradeDomain` validates `BlockPlacementPolicyWithUpgradeDomain`, which layers upgrade-domain diversity on top of rack-aware block placement. It covers target choice, exclusions, insufficient-domain fallback, placement verification, replica deletion, and move eligibility.

## Important APIs, types, and functions
The test extends `BaseReplicationPolicyTest` and sets `blockPlacementPolicy` to `BlockPlacementPolicyWithUpgradeDomain`. It builds nine DataNodes across three racks, assigning upgrade domains 1, 2, and 3 repeatedly within each rack. It uses `chooseTarget`, `verifyBlockPlacement`, `chooseReplicasToDelete`, `BlockStoragePolicySuite`, `StorageType`, and `isMovable`. Local helpers collect selected upgrade domains and racks from `DatanodeStorageInfo[]`.

## Control flow
`testChooseTarget1` checks target selection for replica counts 0 through 4. It verifies local preference, remote rack placement, same-rack grouping for later replicas, and that selected targets cover the expected number of upgrade domains. `testChooseTargetWithExcludeNodes` adds excluded DataNodes in combinations that constrain available upgrade domains and racks, then verifies the policy still prefers local and preserves diversity where possible. `testChooseTargetWithoutEnoughReplica` excludes enough nodes that only two targets can satisfy a request for three.

`testVerifyBlockPlacement` constructs located blocks with specific rack and upgrade-domain distributions and checks whether placement is satisfied, including whether error descriptions mention upgrade-domain deficiencies only when that is the limiting factor. `testChooseReplicasToDelete` checks delete hints, rejection of hints that would reduce upgrade-domain diversity, storage type excess deletion, and SSD-policy transition scenarios. `testIsMovable` simulates balancer moves and checks whether replacing a source with a target preserves or improves rack and upgrade-domain counts.

## State and persistence behavior
The state under test is in-memory DataNode topology, upgrade-domain labels, selected target lists, candidate replica collections, storage types, and move candidate sets. There is no cluster persistence; the source builds synthetic descriptors through the base harness.

## Dependencies and integration points
This file tests the upgrade-domain placement policy used by writes, re-replication, deletion, and balancer move validation. It integrates with storage policy excess calculations and the generic placement status/error mechanism.

## Risks and test signals
Signals include exact target counts, object identity for expected storages, rack set size, upgrade-domain set size, placement status, error description content, chosen deletion candidates, and `isMovable` booleans. It catches regressions where rack policy is satisfied but upgrade-domain diversity is lost, delete hints are accepted too aggressively, or balancer moves reduce fault-domain diversity.
