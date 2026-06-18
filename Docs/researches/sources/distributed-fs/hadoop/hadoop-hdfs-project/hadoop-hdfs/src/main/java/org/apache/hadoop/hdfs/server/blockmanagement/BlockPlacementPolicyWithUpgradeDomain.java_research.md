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
