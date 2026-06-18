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
