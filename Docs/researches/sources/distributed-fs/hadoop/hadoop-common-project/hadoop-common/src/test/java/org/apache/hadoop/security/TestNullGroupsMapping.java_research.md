# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNullGroupsMapping.java

Purpose: Ensures `NullGroupsMapping` always returns no groups and ignores cache mutation hooks.

Important APIs/types/functions: `NullGroupsMapping`, `getGroups`, `cacheGroupsAdd`, `cacheGroupsRefresh`, and JUnit setup.

Control flow: creates a new mapper, checks `getGroups("user")` returns an empty list, calls `cacheGroupsAdd` with two groups and checks still empty, calls `cacheGroupsRefresh` and checks still empty.

State and persistence: mapper instance only; no persistent cache state.

Dependencies/integration points: `GroupMappingServiceProvider` no-op implementation for deployments/tests that disable group lookup.

Risks: only validates list path, not `getGroupsSet` if implemented separately.

Test signals: confirms the null provider remains side-effect-free for add/refresh operations.
