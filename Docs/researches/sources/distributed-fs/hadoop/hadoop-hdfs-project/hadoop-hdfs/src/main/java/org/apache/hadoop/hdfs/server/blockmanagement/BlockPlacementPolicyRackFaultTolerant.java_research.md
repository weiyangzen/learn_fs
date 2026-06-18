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
