# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NullGroupsMapping.java


Purpose: `NullGroupsMapping` is a test or special-purpose `GroupMappingServiceProvider` that resolves every user to no groups.

Important APIs and types: It implements list and set lookup methods returning empty collections and no-op cache refresh/add methods.

Control flow and state: There is no mutable state. Every lookup returns empty, which the outer `Groups` service may convert into a no-groups IOException and negative-cache entry.

Dependencies and integration: It integrates with `Groups` through the provider interface and is useful for configurations that intentionally disable group mapping or tests that need deterministic misses.

Risks and test signals: Tests should account for the distinction between this provider returning empty and `Groups` throwing for empty results. It should not be used accidentally in authorization-sensitive deployments.
