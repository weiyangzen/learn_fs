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
