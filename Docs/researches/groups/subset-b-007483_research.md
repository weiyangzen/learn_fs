# subset-b-007483 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicy.java

## Purpose

`BlockPlacementPolicy` is the abstract contract for HDFS replica placement. It defines how the NameNode chooses target `DatanodeStorageInfo` instances for new blocks and reconstruction, validates whether existing replicas satisfy placement rules, chooses excess replicas for deletion, and decides whether balancer moves preserve placement policy.

## Important APIs and types

- `chooseTarget(...)` is the primary placement API, with overloads for chosen nodes, favored nodes, storage policy, add-block flags, and explicit storage-type counts.
- `verifyBlockPlacement(DatanodeInfo[], int)` returns a `BlockPlacementStatus` describing rack or extended failure-domain satisfaction.
- `chooseReplicasToDelete(...)` selects over-replicated storages after accounting for expected replica count, excess storage types, added-node and delete-node hints.
- `initialize(Configuration, FSClusterStats, NetworkTopology, Host2NodesMap)` injects NameNode configuration, cluster stats, topology, and host lookup dependencies.
- Shared helpers include `splitNodesWithRack`, `adjustSetsWithChosenReplica`, `getDatanodeInfo`, and `getRack`.
- `NotEnoughReplicasException` is the internal signal used by concrete policies when placement cannot satisfy the requested target count.

## Control flow

The base class delegates actual placement to subclasses, but it provides shared rack grouping used by deletion and move decisions. `splitNodesWithRack` first builds a rack-to-replica map from all available replicas, then classifies candidate replicas into `moreThanOne` or `exactlyOne` depending on whether their rack has multiple replicas. `adjustSetsWithChosenReplica` updates those structures after a deletion choice, moving a remaining rack peer from `moreThanOne` to `exactlyOne` if it becomes the last replica on its rack.

Favored-node and explicit-storage-type overloads intentionally fall back to the core abstract placement method unless a subclass adds stronger semantics. `getDatanodeInfo` lets shared code operate on either `DatanodeInfo` or `DatanodeStorageInfo`, while `getRack` is virtual so node-group policies can redefine the effective rack.

## State and persistence behavior

The class holds no persistent state. It is a stateless strategy base whose concrete implementations keep configuration-derived state. Its helper methods mutate caller-supplied collections only, especially during excess-replica selection.

## Dependencies and integration points

It sits between `BlockManager`, `DatanodeManager`, `NetworkTopology`, `FSClusterStats`, `BlockStoragePolicy`, storage-type accounting, balancer/mover decisions, and datanode host mappings. The runtime policy selected by NameNode configuration must implement this contract.

## Risks and edge cases

Rack classification assumes candidates are represented in the available set; a missing rack entry can produce null dereference. `getDatanodeInfo` rejects unsupported object types at runtime. Subclasses must keep overload semantics consistent, especially around favored nodes, storage policy fallback, and mutable `excludedNodes`.

## Test signals

Useful tests exercise rack split and adjustment behavior, delete-hint handling, storage-type overload routing, move validation, and subclass compatibility with both `DatanodeInfo` and `DatanodeStorageInfo` inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyDefault.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyDefault.java

## Purpose

`BlockPlacementPolicyDefault` is the standard HDFS block placement and excess-replica deletion policy. It prefers writer-local placement for the first replica, a remote rack for the second, a local rack relative to the second or writer for the third, and random placement afterward, while honoring storage policies, stale/load/slow-node filtering, rack limits, and client add-block flags.

## Important APIs and types

- Public `chooseTarget` overloads handle normal writes, favored-node writes, preselected replicas, `NO_LOCAL_WRITE` and `NO_LOCAL_RACK`, and explicit `EnumMap<StorageType,Integer>` requests.
- `chooseTargetInOrder`, `chooseLocalOrFavoredStorage`, `chooseLocalRack`, `chooseRemoteRack`, and `chooseRandom` implement the placement strategy.
- `isGoodDatanode` rejects nodes that are out of service, stale, overloaded, over rack limit, or slow.
- `chooseStorage4Block` asks each datanode for an eligible storage with enough remaining space and required storage type.
- `verifyBlockPlacement` enforces the default multi-rack rule.
- `chooseReplicasToDelete`, `chooseReplicaToDelete`, `useDelHint`, `pickupReplicaSet`, and `isMovable` preserve rack diversity during deletion and balancer moves.
- Tunables include `considerLoad`, load-by-storage-type, load-by-volume, local-node preference, peer slow-node exclusion, heartbeat tolerance, stale interval, and minimum blocks required for writes.

## Control flow

Initialization copies NameNode configuration and topology/stat references. Normal target selection first caps requested replicas by cluster size and computes `maxNodesPerRack`. Existing chosen storages are added to the exclusion set. If the caller requested `NO_LOCAL_RACK` or `NO_LOCAL_WRITE`, the method tries a modified exclusion set and only keeps the result if it can satisfy the count; otherwise it falls back to default placement.

The internal chooser derives required storage types from `BlockStoragePolicy`, then calls `chooseTargetInOrder`. If placement fails while stale nodes are being avoided, it retries without stale avoidance and preserves already chosen nodes. If storage types are unavailable, it marks remaining requested types unavailable and retries with policy fallbacks. `chooseRandom` repeatedly asks the topology for a candidate, validates the datanode, selects a matching storage, updates the storage-type counts, and records high-level rejection reasons for logging.

Deletion flow splits replicas by rack, optionally accepts a safe delete hint, otherwise chooses from a preferred set using oldest heartbeat first and least remaining storage as fallback. After each deletion choice it updates rack sets before selecting the next excess replica.

## State and persistence behavior

The policy stores only runtime configuration and references to NameNode-maintained cluster state. It persists nothing itself. Placement mutates provided result, exclusion, and storage-type maps; slow-node data comes from `DatanodeManager`, and load/staleness data comes from current heartbeat-derived state.

## Dependencies and integration points

This policy integrates with `NetworkTopology` and `DFSNetworkTopology`, `FSClusterStats`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `BlockStoragePolicy`, `StorageTypeStats`, `AddBlockFlag`, NameNode configuration keys, datanode slow-node peer stats, replication work scheduling, and balancer/mover safety checks.

## Risks and edge cases

Placement behavior is sensitive to mutable exclusion sets and partial results during retries. Load filtering can starve placement if cluster averages are low or storage-type stats are missing. The policy relies on `DatanodeDescriptor.chooseStorage4Block` to enforce per-storage capacity and minimum block requirements. Debug reason logging uses thread-local builders and maps, so tests should verify no stale diagnostic state leaks between calls. `NO_LOCAL_RACK` only applies when more than two racks exist, and both local-avoidance flags silently fall back if insufficient targets are available.

## Test signals

Strong tests cover replica ordering, rack caps, single-rack and multi-rack verification, storage-policy fallback, favored-node fallback, stale-node retry, overloaded and slow-node exclusion, `NO_LOCAL_WRITE` and `NO_LOCAL_RACK`, deletion hint safety, excess storage-type removal, and balancer `isMovable` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyDefault.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyRackFaultTolerant.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyRackFaultTolerant.java

## Purpose

`BlockPlacementPolicyRackFaultTolerant` extends the default placement policy to spread replicas as evenly as possible across racks. It is designed for deployments that want stronger rack-level fault tolerance than the default "at least two racks" policy.

## Important APIs and types

- `getMaxNodesPerRack` computes a stricter per-rack cap by rounding replica count across non-empty racks.
- `chooseTargetInOrder` overrides target placement to fill racks evenly and then distribute remainder replicas.
- `chooseEvenlyFromRemainingRacks` performs a best-effort fallback when some racks cannot satisfy the ideal distribution.
- `chooseOnce` keeps local preference for the first replica, then selects random replicas under the current rack cap.
- `verifyBlockPlacement` requires as many racks as requested replicas, bounded by available racks.
- `pickupReplicaSet` chooses over-replicated rack groups before singleton racks.

## Control flow

The policy first caps requested replicas by cluster size. When replicas are fewer than racks, it targets one per rack. When replicas exceed racks, it computes a rounded-up `maxNodesPerRack`. `chooseTargetInOrder` handles easy cases directly, then for uneven cases first fills every rack up to `maxNodesPerRack - 1`, excludes chosen nodes, and performs a second pass with `maxNodesPerRack` for the remainder. If that fails because racks lack eligible nodes, it raises the best-effort rack cap gradually while excluding already chosen nodes until the expected total is met or the previous exception is rethrown.

## State and persistence behavior

No additional persistent state is introduced beyond `BlockPlacementPolicyDefault`. All behavior derives from current topology, candidate eligibility, and the mutable placement result list.

## Dependencies and integration points

It reuses default storage, stale, load, and slow-node filtering and relies on `NetworkTopology` rack counts. It integrates with the same write, reconstruction, deletion, and balancer pathways as the default policy.

## Risks and edge cases

Clusters with zero or one rack fall back to default-like caps to avoid division errors. If rack metadata is misconfigured or racks have uneven datanode availability, the policy logs a warning and best-effort placement may not guarantee rack-level tolerance. The fallback loop depends on detecting progress to avoid repeatedly trying impossible caps.

## Test signals

Tests should cover fewer replicas than racks, replicas exactly divisible by racks, uneven replica-to-rack counts, racks with insufficient eligible nodes, single-rack and zero-rack topologies, verification against available rack count, and excess-replica deletion preference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyRackFaultTolerant.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyWithNodeGroup.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyWithNodeGroup.java

## Purpose

`BlockPlacementPolicyWithNodeGroup` adapts HDFS placement to topologies with a node-group layer below racks. It treats node groups as an additional failure domain so replicas avoid landing in the same node group when possible.

## Important APIs and types

- `initialize` requires `NetworkTopologyWithNodeGroup`.
- `chooseFavouredNodes` first tries favored nodes, then falls back to another node in each unchosen favored node's node group.
- `chooseLocalStorage` adds fallback from local node to local node group and then local rack.
- `chooseLocalRack`, `chooseRemoteRack`, and `chooseLocalNodeGroup` use first-half rack and last-half node-group topology helpers.
- `addToExcludedNodes` excludes every leaf in the selected node group plus dependent hostnames.
- `pickupReplicaSet`, `isMovable`, and `verifyBlockPlacement` enforce node-group diversity during deletion, move, and audit.

## Control flow

Initialization fails fast if the configured topology is not node-group aware. Placement first tries local storage, then a peer in the local node group, then local rack fallback. Remote-rack placement uses the rack portion of the writer path. When a node is chosen, the entire node group and dependent datanodes are excluded so later replicas do not duplicate the same lower-level failure domain. Verification temporarily strips node-group suffixes from `DatanodeInfo` network locations to reuse default rack verification, restores the original locations, then wraps the result with node-group status requiring one node group per replica.

For over-replication, the policy first uses the inherited rack split. If candidates already share a rack, it further partitions them by node group and prefers replicas from node groups with more than one copy.

## State and persistence behavior

The policy adds no durable state. It relies on `NetworkTopologyWithNodeGroup` and optional `Host2NodesMap` dependent-host metadata. `verifyBlockPlacement` temporarily mutates `DatanodeInfo` network locations and restores them in the normal path.

## Dependencies and integration points

It integrates with the node-group topology implementation, datanode dependent-host metadata, favored-node placement, replication deletion, balancer move validation, and `BlockPlacementStatusWithNodeGroup`.

## Risks and edge cases

Temporary mutation of datanode network locations during verification is fragile if exceptions are introduced before restoration. Dependent-host exclusion logs but otherwise tolerates missing host mappings. Node-group extraction assumes topology paths are well formed. Requiring `numberOfReplicas` node groups can report unsatisfied placement when the topology has fewer node groups than replicas.

## Test signals

Tests should cover topology type rejection, local node-group fallback, favored-node node-group fallback, dependent-host exclusion, delete-candidate node-group preference, `isMovable` with same-node-group target, and verification restoration of original network locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyWithNodeGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyWithUpgradeDomain.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyWithUpgradeDomain.java

## Purpose

`BlockPlacementPolicyWithUpgradeDomain` extends default rack placement with upgrade-domain diversity. It prevents early replicas from sharing upgrade domains and preserves upgrade-domain coverage during deletion and balancer moves.

## Important APIs and types

- `initialize` reads `DFS_UPGRADE_DOMAIN_FACTOR`.
- `isGoodDatanode` rejects a candidate whose upgrade domain is already represented while selected results are below the factor.
- `getUpgradeDomainWithDefaultValue` uses the datanode transfer address when no upgrade domain is configured.
- `verifyBlockPlacement` wraps default rack status in `BlockPlacementStatusWithUpgradeDomain`.
- `pickupReplicaSet` prefers excess replicas that share both rack and upgrade domain, then shared upgrade-domain replicas, then default rack logic.
- `useDelHint` and `isMovable` add upgrade-domain safety checks on top of default rack checks.

## Control flow

Placement delegates to the default algorithm but extends candidate validation. Once at least one replica is selected and fewer than `upgradeDomainFactor` replicas are selected, every new candidate must introduce a new upgrade domain. Verification computes the set of upgrade domains from current locations and asks the status object to require `min(numberOfReplicas, upgradeDomainFactor)` unique domains.

Deletion combines rack-based `moreThanOne` and `exactlyOne` sets, builds an upgrade-domain map, and identifies replicas sharing a domain. If every domain is unique, default deletion logic applies. Otherwise, replicas sharing both rack and upgrade domain are preferred; if none exist, replicas sharing only upgrade domain are preferred. Delete hints and mover decisions are accepted only if removing the source does not reduce upgrade-domain groups unless the existing domain count already exceeds the factor.

## State and persistence behavior

The only added state is the configured `upgradeDomainFactor`. Missing upgrade-domain metadata is not persisted; the fallback transfer address is used dynamically and logged.

## Dependencies and integration points

It depends on datanode upgrade-domain fields populated from host configuration or registration, default rack placement, `BlockPlacementStatusWithUpgradeDomain`, storage-type deletion logic, and balancer/mover validations.

## Risks and edge cases

Using transfer address as a fallback makes tests easier but can hide incomplete production upgrade-domain configuration. Placement only enforces uniqueness while results are below the factor; existing chosen nodes can already violate the policy. Deletion must balance rack and upgrade-domain safety, so regressions can reduce one failure-domain count while preserving the other.

## Test signals

Tests should cover unique-domain placement, null upgrade-domain fallback, verification for replica counts below and above the factor, deletion-set ordering, delete-hint rejection, mover rejection when domains collapse, and behavior when existing domains exceed the factor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementPolicyWithUpgradeDomain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatus.java

## Purpose

`BlockPlacementStatus` is the small result interface returned by block placement verification. It lets callers ask whether a block satisfies policy, obtain a human-readable failure description, and estimate how many additional replicas are needed to satisfy placement.

## Important APIs and types

- `isPlacementPolicySatisfied()` returns the boolean policy result.
- `getErrorDescription()` returns null on success and a diagnostic string on failure.
- `getAdditionalReplicasRequired()` returns zero on success or a required extra-replica count on failure.

## Control flow

The interface has no logic. Implementations compose policy-specific checks, commonly by wrapping a parent status and taking the maximum number of additional replicas required across policy dimensions.

## State and persistence behavior

No state or persistence exists in the interface. Implementations are immutable or simple value holders in normal use.

## Dependencies and integration points

`BlockPlacementPolicy.verifyBlockPlacement` returns this interface. `BlockManager`, fsck-style diagnostics, replication scheduling, decommission logic, and tests can consume it without knowing which placement policy is active.

## Risks and edge cases

The contract permits free-form error strings, so external callers should not parse them as stable APIs. Additional replica counts are advisory because actual placement can still fail due to topology, capacity, or storage-type constraints.

## Test signals

Tests should assert boolean, error-description, and additional-replica behavior for every implementation rather than only checking the boolean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusDefault.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusDefault.java

## Purpose

`BlockPlacementStatusDefault` is the rack-based placement status used by the default and rack-fault-tolerant policies. It records current rack count, required rack count, and total available racks.

## Important APIs and types

- Constructor arguments are `currentRacks`, `requiredRacks`, and `totalRacks`.
- `isPlacementPolicySatisfied` succeeds when the required rack count is met or the block already spans every rack in the cluster.
- `getErrorDescription` reports how many more racks are needed.
- `getAdditionalReplicasRequired` returns the rack deficit.

## Control flow

The status is a pure value calculation. The special `currentRacks >= totalRacks` branch prevents impossible requirements from being reported when the cluster has fewer racks than the ideal policy requires.

## State and persistence behavior

The class stores three integer fields and persists nothing. It is normally created per verification call.

## Dependencies and integration points

It is returned by `BlockPlacementPolicyDefault` and `BlockPlacementPolicyRackFaultTolerant`, and it is wrapped by node-group and upgrade-domain statuses.

## Risks and edge cases

If `totalRacks` is inaccurate or zero, the satisfaction branch can mislead callers. The class does not validate constructor arguments, so negative or inconsistent counts would produce nonsensical diagnostics.

## Test signals

Tests should cover satisfied, unsatisfied, one-rack cluster, required racks greater than total racks, and additional-replica counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusDefault.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusWithNodeGroup.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusWithNodeGroup.java

## Purpose

`BlockPlacementStatusWithNodeGroup` composes the parent rack status with node-group diversity requirements for `BlockPlacementPolicyWithNodeGroup`.

## Important APIs and types

- It stores a parent `BlockPlacementStatus`, a set of current node groups, and a required node-group count.
- `isPlacementPolicySatisfied` requires both parent status and node-group status to pass.
- `getErrorDescription` concatenates parent and node-group failure messages.
- `getAdditionalReplicasRequired` returns the maximum of parent and node-group deficits.

## Control flow

The node-group check is simply `requiredNodeGroups <= currentNodeGroups.size()`. Error generation first asks the parent status for its message, then adds a node-group-specific explanation if needed. Additional replica computation mirrors the composite logic by taking the maximum deficit rather than summing deficits.

## State and persistence behavior

The class is an in-memory value holder for one verification result. It keeps the provided set reference and does not persist anything.

## Dependencies and integration points

It is created by `BlockPlacementPolicyWithNodeGroup.verifyBlockPlacement` after default rack verification. Callers interact through the generic `BlockPlacementStatus` interface.

## Risks and edge cases

The required node-group count is usually the requested replica count, which can exceed the number of available node groups. The class does not cap by topology size. Because it keeps the input set, later external mutation could change the status result if a mutable set is reused.

## Test signals

Tests should cover parent-only failure, node-group-only failure, combined failure messages, additional-replica max behavior, and mutable-set isolation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusWithNodeGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusWithUpgradeDomain.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusWithUpgradeDomain.java

## Purpose

`BlockPlacementStatusWithUpgradeDomain` composes default rack placement with upgrade-domain diversity. It reports whether a block has enough unique upgrade domains for its replica count and configured domain factor.

## Important APIs and types

- Constructor inputs are parent status, upgrade-domain set, number of replicas, and `upgradeDomainFactor`.
- `isPlacementPolicySatisfied` requires parent and upgrade-domain checks.
- `getErrorDescription` combines parent and upgrade-domain failure details.
- `getAdditionalReplicasRequired` returns the maximum of parent and upgrade-domain deficits.

## Control flow

If the block's replica count is less than or equal to the factor, every replica must have a unique upgrade domain. If the replica count is greater than the factor, only `upgradeDomainFactor` unique domains are required. Failure descriptions include replica count, unique domain count, and the observed domain set.

## State and persistence behavior

This is a per-verification in-memory value object. It stores the provided set reference and does not persist state.

## Dependencies and integration points

It is created by `BlockPlacementPolicyWithUpgradeDomain` and consumed through `BlockPlacementStatus`. It relies on the policy to provide upgrade-domain values, including fallback values for missing metadata.

## Risks and edge cases

A factor of zero or negative values would make the child calculation nonsensical, so configuration validation matters upstream. Mutable input sets can affect subsequent results. Additional-replica counts are advisory and do not prove the cluster has domains available.

## Test signals

Tests should cover replica counts below, equal to, and above the factor; parent-only failures; domain-only failures; combined errors; and additional-replica max behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockPlacementStatusWithUpgradeDomain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReconstructionWork.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReconstructionWork.java

## Purpose

`BlockReconstructionWork` is the abstract task model used by `BlockManager.computeReconstructionWorkForBlocks` to represent replication or erasure-coding reconstruction. It bundles the block, source datanodes, containing nodes, live storages, target choices, priority, and placement deficiency flags.

## Important APIs and types

- Constructor captures `BlockInfo`, `BlockCollection`, source nodes, containing nodes, live replica storages, required additional replicas, and priority.
- Accessors expose block, source path, block size, storage policy ID, source nodes, live storages, target storages, priority, and required replication count.
- `setNotEnoughRack` and `hasNotEnoughRack` mark reconstruction driven by placement-policy deficiency rather than only replica count.
- Abstract `chooseTargets(BlockPlacementPolicy, BlockStoragePolicySuite, Set<Node>)` delegates target selection to concrete replicated or striped work.
- Abstract `addTaskToDatanode(NumberReplicas)` attaches the computed task to a source datanode.

## Control flow

The base constructor snapshots block collection details needed for later target choice. Concrete subclasses set `targets` after invoking block placement and then enqueue replication or erasure-coding work on a source datanode. The containing-node list is returned as unmodifiable so target selection can exclude existing holders without allowing callers to corrupt the task model.

## State and persistence behavior

The class is an in-memory scheduling object. It stores selected targets and a placement-deficiency flag, but nothing is persisted directly. Durable block state changes happen elsewhere when datanodes execute tasks and report blocks.

## Dependencies and integration points

It connects `BlockManager`, `BlockPlacementPolicy`, `BlockStoragePolicySuite`, `BlockInfo`, `BlockCollection`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `NumberReplicas`, and reconstruction queues.

## Risks and edge cases

The task snapshots `srcPath`, block size, and storage policy at construction; if metadata changes before scheduling, subclasses must tolerate stale context. Source-node arrays differ between replicated and erasure-coded tasks. Resetting targets allows retry paths but requires callers to avoid using stale target arrays.

## Test signals

Tests should verify constructor field capture, unmodifiable containing-node view, not-enough-rack flag behavior, subclass target selection with exclusions, and add-task behavior for both replicated and erasure-coded reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReconstructionWork.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReportLeaseManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReportLeaseManager.java

## Purpose

`BlockReportLeaseManager` rate-limits full block reports reaching the NameNode by granting a bounded number of leases to datanodes. Lease ID zero remains an intentional bypass for compatibility and manually triggered full block reports.

## Important APIs and types

- `NodeData` stores datanode UUID, lease ID, lease time, and doubly linked-list pointers.
- `register` and `unregister` manage datanode membership.
- `requestLease` grants a nonzero lease when pending leases are below `maxPending`.
- `checkLease` validates a report lease, accepts ID zero, rejects unknown, expired, missing, or mismatched leases.
- `removeLease` clears a lease after use.
- `pruneExpiredPending` and `pruneIfExpired` reclaim expired leases.

## Control flow

Two circular lists partition nodes: deferred nodes without leases and pending nodes with active leases. Registration inserts at the front of deferred. `requestLease` registers unknown datanodes on demand, removes any existing list entry, prunes expired pending leases from the oldest end, and returns zero if the pending cap is reached. Otherwise it issues a new nonzero monotonically advanced ID, records the monotonic timestamp, appends to pending, and increments `numPending`. Successful `removeLease` moves the node to the end of deferred so older reporters can be prioritized.

## State and persistence behavior

All state is in-memory and synchronized on the manager. Lease IDs are initialized from a random long and never use zero. State is lost on NameNode restart, and ID zero compatibility lets reports still be accepted outside the lease flow.

## Dependencies and integration points

It uses NameNode datanode descriptors, DFS full-block-report lease configuration, monotonic time, and heartbeat/block-report protocol fields. It protects `BlockManager` from bursts of expensive full block reports.

## Risks and edge cases

All methods are synchronized, so correctness is simple but latency-sensitive if logging or large pending lists grow. Expiration pruning stops at the first unexpired pending entry, relying on pending list order by lease time. Re-requesting a lease discards the previous lease, which is necessary for datanode restart but invalidates in-flight old reports.

## Test signals

Tests should cover max-pending enforcement, zero-ID bypass, unknown datanode registration, duplicate register/unregister behavior, lease expiry, ID mismatch rejection, nonzero ID generation across overflow, and deferred/pending order after remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReportLeaseManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockStatsMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockStatsMXBean.java

## Purpose

`BlockStatsMXBean` is the JMX-facing interface for block-management storage statistics. It exposes storage-type statistics to management clients.

## Important APIs and types

- `getStorageTypeStats()` returns a `Map<StorageType, StorageTypeStats>`.

## Control flow

The interface has no implementation logic. Implementing NameNode/block-management classes provide the current storage-type map when JMX queries arrive.

## State and persistence behavior

No state is stored by the interface. Implementations typically derive returned values from heartbeat-maintained `StorageTypeStats`.

## Dependencies and integration points

It is part of the NameNode management surface and depends on HDFS `StorageType` and block-management `StorageTypeStats`.

## Risks and edge cases

Returned maps should be safe for management consumers to inspect without mutating live internals. Since storage stats are dynamic, JMX clients must treat values as snapshots.

## Test signals

Tests should verify that implementing beans expose all relevant storage types, handle empty clusters, and do not leak mutable internal maps if that is a contract requirement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockStatsMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockStoragePolicySuite.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockStoragePolicySuite.java

## Purpose

`BlockStoragePolicySuite` is the NameNode-side registry of HDFS block storage policies. It defines built-in policies and helpers for storing policy IDs in system xattrs.

## Important APIs and types

- `createDefaultSuite(Configuration)` builds the built-in policy array.
- Policies include `LAZY_PERSIST`, `ALL_NVDIMM`, `ALL_SSD`, `ONE_SSD`, `HOT`, `WARM`, `COLD`, and `PROVIDED`.
- `getPolicy(byte)`, `getDefaultPolicy`, `getPolicy(String)`, and `getAllPolicies` provide lookup.
- `buildXAttrName`, `buildXAttr`, `getStoragePolicyXAttrPrefixedName`, and `isStoragePolicyXAttr` manage the system xattr representation.
- `ID_BIT_LENGTH` fixes the policy array size at 16 IDs.

## Control flow

Default suite creation allocates a fixed policy array and inserts policies by enum-provided byte ID. The configured default policy is resolved by case-insensitive name, falling back to the DFS default if absent or invalid. Lookup by byte treats ID zero as "unspecified" and returns the configured default policy. Lookup by name scans non-null policies case-insensitively.

## State and persistence behavior

The suite stores the default policy ID and immutable-by-convention policy array. The durable representation of a file policy is a system xattr containing one byte. The suite itself is rebuilt from configuration rather than persisted.

## Dependencies and integration points

It integrates storage policy semantics with `BlockStoragePolicy`, `StorageType`, `HdfsConstants.StoragePolicy`, `DFSConfigKeys`, `XAttr`, `XAttrHelper`, and placement code that asks policies for required and fallback storage types.

## Risks and edge cases

`getPolicy(byte)` indexes the array directly for nonzero IDs, so callers must pass valid IDs. Adding new policies is constrained by 4-bit IDs. Misconfigured default policy silently falls back rather than failing. Returned arrays and policy references should be treated as read-only.

## Test signals

Tests should cover all built-in policies, configured default resolution, ID zero behavior, invalid ID handling expectations, name lookup case-insensitivity, xattr name/value construction, and `isStoragePolicyXAttr` filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockStoragePolicySuite.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockToMarkCorrupt.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockToMarkCorrupt.java

## Purpose

`BlockToMarkCorrupt` is a small value object used while processing block reports to collect replicas that should be marked corrupt. It preserves both the datanode-reported corrupted block and the NameNode-stored block metadata.

## Important APIs and types

- Constructors require corrupted `Block`, stored `BlockInfo`, textual reason, and `CorruptReplicasMap.Reason`.
- The generation-stamp constructor mutates the corrupted block to a supplied generation stamp.
- `isCorruptedDuringWrite` compares stored and corrupted generation stamps.
- Accessors expose corrupted block, stored block, reason text, and reason code.
- `toString` shows whether corrupted and stored references are the same object.

## Control flow

Construction validates non-null block references. For generation-stamp mismatch scenarios, the second constructor delegates and then adjusts the corrupted block's generation stamp to represent the exact reported mismatch. Later block-report code can decide whether corruption happened during write and record the reason in `CorruptReplicasMap`.

## State and persistence behavior

The class is in-memory and short-lived. It mutates the supplied corrupted `Block` in one constructor, but persistent corruption state is stored later in `CorruptReplicasMap`.

## Dependencies and integration points

It is tied to block-report reconciliation, `BlockManager`, `BlockInfo`, `Block`, and corruption reason codes.

## Risks and edge cases

Mutating the corrupted block's generation stamp can surprise callers if the same `Block` instance is shared. `isCorruptedDuringWrite` only checks generation-stamp ordering and does not account for length or replica state mismatches.

## Test signals

Tests should cover null validation, generation-stamp mutation, corruption-during-write classification, reason propagation, and string output for same versus different stored block references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockToMarkCorrupt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockUnderConstructionFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockUnderConstructionFeature.java

## Purpose

`BlockUnderConstructionFeature` stores mutable state for a block that is still being written, appended, truncated, committed, or recovered. It is usually attached to the last block of an open file.

## Important APIs and types

- Constructor records `BlockUCState` and expected target storages.
- `setExpectedLocations`, `getExpectedStorageLocations`, iterator access, `getBlockIndices`, and `getBlockIndicesForSpecifiedStorages` manage expected replicas.
- `updateStorageScheduledSize` adjusts scheduled-block counts for partial striped blocks.
- State APIs include `getBlockUCState`, `setBlockUCState`, `commit`, `getBlockRecoveryId`, `getTruncateBlock`, and `setTruncateBlock`.
- `getStaleReplicas` identifies replicas with wrong generation stamps.
- `initializeBlockRecovery` selects a primary datanode and queues recovery work.
- `addReplicaIfNotPresent` incorporates reported replicas and storage moves.

## Control flow

Expected locations are built from non-null target storages. For striped blocks, each expected replica uses a block ID offset so internal block indices map to storages. Recovery sets state to `UNDER_RECOVERY`, records the recovery ID, optionally rotates primary selection, resets `chosenAsPrimary` once all live replicas have been tried, and chooses the live replica with the most recent heartbeat as primary. It then adds the block to that datanode's recovery queue.

Reported replicas update an existing expected storage by generation stamp, replace an entry if the same datanode reports the block on a different storage, or append a new replica entry. String helpers expose full or concise state for logs.

## State and persistence behavior

The class holds under-construction state in memory as part of `BlockInfo`. It includes state, expected replicas, primary index, recovery ID, and optional truncate block. Durable representation is handled by NameNode metadata serialization outside this class.

## Dependencies and integration points

It integrates with `BlockInfo`, `BlockInfoStriped`, `ReplicaUnderConstruction`, datanode storage scheduling, lease recovery, NameNode block state logs, block type handling, and replica states.

## Risks and edge cases

The constructor assertion checks `getBlockUCState()` before assigning the constructor state, so it relies on default null behavior and does not validate the passed state directly. Iterators are explicitly not thread-safe and require external FSNamesystem locking. Recovery with no replicas logs and sets primary index to -1. Partial striped block scheduled-size adjustments must match block index math.

## Test signals

Tests should cover replicated and striped expected-location creation, null targets, block index calculation, scheduled-size decrement for short stripes, recovery primary rotation, stale replica detection, reported storage replacement, append of unexpected replicas, and no-replica recovery behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockUnderConstructionFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlocksMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlocksMap.java

## Purpose

`BlocksMap` is the NameNode's block-to-metadata index. It maps block IDs to `BlockInfo`, tracks which block collection owns a block, and links block metadata to datanode storage locations.

## Important APIs and types

- `addBlockCollection` inserts or reuses a `BlockInfo` and sets its block collection ID.
- `removeBlock` removes a block from the map and all datanode storage lists.
- `getStoredBlock`, `getStorages`, `numNodes`, `removeNode`, `size`, `getBlocks`, and `getCapacity` expose lookup and iteration.
- `StorageIterator` iterates non-null storages from a `BlockInfo`, including striped blocks with sparse slots.
- `getReplicatedBlocks` and `getECBlockGroups` expose block-type counters.

## Control flow

The map is backed by a `LightWeightGSet` sized by constructor capacity. Its iterator disables modification tracking because the map is expected to be accessed under the FSNamesystem lock. Adding a block increments replicated or striped counters only when the block is newly inserted. Removing a block first removes it from the GSet, decrements counters, asserts it is no longer owned by an inode, then walks storage slots backwards removing the block from each datanode storage. Removing a node detaches that datanode's storage from the block and removes the block entirely if it is both deleted and has no storage.

## State and persistence behavior

`BlocksMap` is in-memory NameNode metadata. It can be cleared or closed, and counters are maintained with `LongAdder`. Persistent namespace state is stored elsewhere in fsimage/edit logs.

## Dependencies and integration points

It integrates `Block`, `BlockInfo`, `BlockCollection`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `INodeId`, `GSet`, and `LightWeightGSet`. It is central to block reports, replication, corruption handling, deletion, and cache management.

## Risks and edge cases

Iterator behavior intentionally tolerates concurrent modifications only because external locks are assumed; using it without locks can miss entries. Counter correctness depends on every insertion and removal path pairing increments/decrements. `removeBlock` asserts ownership is invalid before final removal, so callers must clear block collection ownership first.

## Test signals

Tests should cover add/reuse behavior, replicated versus striped counters, storage iteration with null striped slots, remove-node cleanup, block removal from datanode lists, clear/close behavior, and no-storage deleted block eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlocksMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CacheReplicationMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CacheReplicationMonitor.java

## Purpose

`CacheReplicationMonitor` is the NameNode background thread that scans cache directives and schedules DataNodes to cache or uncache block replicas. It turns namespace cache directives into per-block desired cache replication and per-datanode pending cache commands.

## Important APIs and types

- The class extends `SubjectInheritingThread` and implements `Closeable`.
- `work` is the monitor loop.
- `setNeedsRescan` and `waitForRescanIfNeeded` coordinate immediate rescans with callers through a CRM lock and conditions.
- `close` shuts the monitor down while the global FSNamesystem write lock is held.
- `rescan`, `resetStatistics`, `rescanCacheDirectives`, `rescanFile`, and `rescanCachedBlockMap` implement mark-and-sweep cache reconciliation.
- `addNewPendingCached`, `addNewPendingUncached`, `chooseDatanodesForCaching`, and `chooseRandomDatanodeByRemainingCapacity` select datanode cache actions.

## Control flow

The thread waits until a periodic interval expires or requested scan count exceeds completed count. Each scan flips a boolean mark, takes the global namesystem write lock, records the current scan count, resets cache statistics, applies directives, scans the cached-block map, and resets datanode caching directive send timestamps. Directive scanning skips expired directives, resolves paths without following invalid or unsupported entries, applies directory directives only to immediate child files, skips under-construction blocks, and updates per-directive needed/cached byte and file counts.

The cached-block scan first drops pending cache entries that no longer fit effective datanode cache capacity. It then removes completed pending-uncache entries, decides whether each cached block is still needed, trims pending cache entries when enough replicas are cached, trims pending uncache entries when replicas are under target, schedules new uncache work for over-cached blocks, or schedules new cache work for under-cached blocks. Blocks with no desired or pending cache state are removed from the global cached-block set.

## State and persistence behavior

The monitor maintains scan counters, shutdown flag, mark bit, previous scan statistics, and last lock-hold timestamp. It mutates in-memory `CachedBlock` entries and datanode pending cached/uncached lists. Cache directives are namespace state, but the monitor's pending decisions are runtime state derived by rescans.

## Dependencies and integration points

It integrates with `FSNamesystem`, `FSDirectory`, `BlockManager`, `CacheManager`, `CachePool`, `CacheDirective`, `CachedBlock`, `INodeFile`, datanode cache reports, block completeness and corruption state, stale-node detection, and NameNode locking modes.

## Risks and edge cases

The monitor holds the global write lock during scans but can drop/reacquire it when configured to limit lock time; correctness depends on rescanning and mark logic tolerating namespace changes. Directory directives scan only direct children, not recursively. Weighted random selection assumes positive total cache remaining percent; all-zero or inconsistent cache metrics would be risky. Pending capacity computation subtracts pending cached bytes and adds pending uncached bytes, so stale pending lists can affect scheduling.

## Test signals

Tests should cover periodic and forced rescan synchronization, directive expiry, file and directory directive application, under-construction block skipping, pool limit enforcement, cached-block mark cleanup, pending cache capacity pruning, corrupt/non-service datanode filtering, stale-node preference, weighted target selection, and safe shutdown with locks held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CacheReplicationMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CombinedHostFileManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CombinedHostFileManager.java

## Purpose

`CombinedHostFileManager` reads the JSON combined hosts file and answers include, exclude, upgrade-domain, and maintenance-expiration queries for datanodes. It replaces separate include/exclude files with one admin-state-aware source.

## Important APIs and types

- `refresh` reloads the configured hosts file using `CombinedHostsFileReader`.
- `HostProperties` stores a multimap from resolved `InetAddress` to `DatanodeAdminProperties`.
- `isIncluded`, `isExcluded`, `getUpgradeDomain`, and `getMaintenanceExpirationTimeInMS` answer datanode policy queries.
- `getIncludes` and `getExcludes` expose iterable socket addresses.
- `parseEntry` resolves hostnames and drops unresolved entries.

## Control flow

Refresh builds a new `HostProperties` instance, reads all JSON entries with optional timeout, resolves each hostname and port, adds valid entries, and atomically swaps the manager's current properties. Inclusion treats an empty set of normal in-service entries as "include everything"; otherwise a datanode is included if its resolved IP has a matching port or wildcard port zero entry. Exclusion checks for matching decommissioned entries. Maintenance expiration is returned only for matching `IN_MAINTENANCE` entries. Upgrade domain returns the first matching entry's upgrade domain.

## State and persistence behavior

The manager stores the current Hadoop `Configuration` and current in-memory `HostProperties`. The JSON file is the durable source. Refresh builds new state before swapping, avoiding partial update exposure.

## Dependencies and integration points

It integrates with `HostConfigManager`, `DatanodeAdminProperties`, `DatanodeID`, datanode admin states, `DFS_HOSTS` configuration, `CombinedHostsFileReader`, DNS resolution, decommission/maintenance management, and upgrade-domain placement policy.

## Risks and edge cases

DNS resolution happens only at refresh time; IP changes require refresh. Multiple entries for the same IP can make upgrade-domain selection depend on iteration order. Wildcard port zero intentionally matches all datanodes on a host. Unresolved entries are logged and ignored, which can admit or reject datanodes differently than intended.

## Test signals

Tests should cover empty include semantics, normal include entries, decommission excludes, maintenance expiration, wildcard ports, unresolved host drops, refresh atomicity, timeout reader path, and upgrade-domain matching with multiple entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CombinedHostFileManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CorruptReplicasMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CorruptReplicasMap.java

## Purpose

`CorruptReplicasMap` tracks datanodes that hold corrupt replicas for each block. It lets the NameNode hide corrupt replicas from normal placement accounting and clear corruption once enough good replicas exist or specific reasons are resolved.

## Important APIs and types

- `Reason` enumerates `NONE`, `ANY`, `GENSTAMP_MISMATCH`, `SIZE_MISMATCH`, `INVALID_STATE`, and `CORRUPTION_REPORTED`.
- `addToCorruptReplicasMap` adds or updates a datanode reason for a block.
- `removeFromCorruptReplicasMap` removes an entire block or one datanode entry, optionally matching a reason.
- `getNodes`, `isReplicaCorrupt`, `numCorruptReplicas`, `size`, `getCorruptBlocksSet`, and `getCorruptReason` expose contents.
- `getCorruptBlockIdsForTesting` returns sorted replicated or striped corrupt block IDs within a bounded page.
- `getCorruptBlocks` and `getCorruptECBlockGroups` expose counters.

## Control flow

Adding a corrupt replica creates the per-block datanode map if absent and increments replicated or EC block-group counters once per block key. Duplicate adds update the reason and log as duplicate. Removing a datanode entry optionally checks that the stored reason matches, deletes the per-block map when empty, and decrements the corresponding counter. Testing ID pagination filters block type through `BlockIdManager`, starts from the requested ID or beginning, sorts, limits to 100, and returns IDs.

## State and persistence behavior

The class is an in-memory map from `Block` to datanode-to-reason maps plus counters. Corruption knowledge is reconstructed or persisted by higher-level NameNode metadata mechanisms, not by this class directly.

## Dependencies and integration points

It integrates with `BlockManager`, block reports, client/datanode corruption reports, `NameNode.blockStateChangeLog`, IPC remote IP logging, `BlockIdManager`, and replicated versus striped block accounting.

## Risks and edge cases

The map is not internally synchronized and relies on NameNode locking. The key type is `Block`, so equality/generation-stamp semantics matter. Counters depend on correct `isStriped` values passed on add/remove. Reason-specific removal ignores mismatches and can leave stale corruption if reason classification changes.

## Test signals

Tests should cover add/update duplicates, per-node and whole-block removal, reason-specific removal, counter increments/decrements for replicated and striped blocks, corrupt ID pagination bounds, and get-reason behavior for missing entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CorruptReplicasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminBackoffMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminBackoffMonitor.java

## Purpose

`DatanodeAdminBackoffMonitor` is the backoff-oriented decommission and maintenance monitor. It tracks datanodes leaving service without flooding the global replication queue, feeding only a bounded number of blocks into pending replication and advancing nodes to decommissioned or maintenance states once their blocks are sufficiently covered.

## Important APIs and types

- `outOfServiceNodeBlocks` maps tracked datanodes to blocks still needing processing; null means the node has not been scanned yet.
- `pendingRep` maps datanodes to blocks already queued for reconstruction and waiting to become sufficiently replicated.
- `processConf` reads `pendingRepLimit` and `blocksPerLock`.
- `run` is the monitor tick entry point.
- `processPendingNodes`, `processCancelledNodes`, `check`, `processMaintenanceNodes`, `processPendingReplication`, `moveBlocksToPending`, `scanDatanodeStorage`, and `processCompletedNodes` implement the state machine.
- `isBlockReplicatedOk` verifies and optionally schedules reconstruction.
- `BlockStats` accumulates open-file and out-of-service-only block metrics for datanode leaving-service status.

## Control flow

Each tick skips work if the namesystem is stopped, resets checked-block counters, takes the block-management write lock, processes cancellations before new pending nodes, optionally requeues unhealthy tracked nodes if concurrency is over the configured limit, and moves new pending nodes into the tracked map. The later `check` phase scans newly tracked nodes under read locks, expires maintenance nodes under the global write lock, prunes pending replication blocks that now satisfy redundancy, moves more blocks into pending replication up to the limit, rescans apparently complete nodes, and finally transitions healthy completed nodes.

Initial scans add all decommissioning-node blocks to the to-process map but immediately filter maintenance or rescan blocks through sufficiency checks. `moveBlocksToPending` creates per-node iterators and cycles them round-robin, dropping and retaking the global write lock after `blocksPerLock` blocks. `nextBlockAddedToPending` removes each processed block from the unprocessed map and queues it only if `isBlockReplicatedOk` says it still needs work. Pending replication processing updates per-node leaving-service metrics and removes blocks once sufficient.

## State and persistence behavior

All tracking state is in-memory and rebuilt from datanode/block state as nodes enter decommission or maintenance. It mutates datanode admin state through `dnAdmin`, datanode leaving-service metrics, and the block reconstruction queue. Persistent admin intent comes from host configuration and datanode admin state maintained elsewhere.

## Dependencies and integration points

It extends `DatanodeAdminMonitorBase` and uses `DatanodeAdminMonitorInterface`, `BlockManager`, `DatanodeAdminManager`, `FSNamesystem` locks, `DatanodeDescriptor`, `DatanodeStorageInfo`, `BlockInfo`, `BlockCollection`, `NumberReplicas`, `INodeFile`, low-redundancy queues, and maintenance/decommission configuration keys.

## Risks and edge cases

The monitor deliberately drops and reacquires locks, so it must re-check storage existence and tolerate concurrent block state changes. `getYetToBeProcessedCount` assumes every tracked value is non-null; the code scans null entries before calling it in normal flow. Orphan blocks return false from `isBlockReplicatedOk`, keeping them pending until invalidation paths handle them. Requeueing unhealthy nodes trades fairness and completion latency against concurrency limits.

## Test signals

Tests should cover invalid config fallback, cancellation-before-pending ordering, max concurrent tracked-node requeue, initial scan differences for decommission and maintenance, lock-yield block batching, pending limit enforcement, round-robin scheduling across nodes, maintenance expiry, final state transitions, open-file/out-of-service metrics, and orphan or unknown block handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeAdminBackoffMonitor.java -->
