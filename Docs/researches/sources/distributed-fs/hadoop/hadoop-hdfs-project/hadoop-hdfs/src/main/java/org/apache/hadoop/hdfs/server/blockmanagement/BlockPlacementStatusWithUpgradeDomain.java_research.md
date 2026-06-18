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
