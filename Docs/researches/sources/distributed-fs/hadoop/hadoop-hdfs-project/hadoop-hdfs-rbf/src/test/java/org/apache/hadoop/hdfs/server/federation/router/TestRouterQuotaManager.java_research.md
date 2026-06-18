## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterQuotaManager.java

Purpose: unit-level coverage for `RouterQuotaManager`, focused on in-memory path lookup behavior rather than full Router integration. The test constructs a fresh manager per test and clears it afterward.

Important APIs and types are `RouterQuotaManager`, `RouterQuotaUsage`, `RouterQuotaUsage.Builder`, `HdfsConstants.QUOTA_RESET`, and `Set<String>`. `testGetChildrenPaths()` stores quota entries at sibling and nested paths and verifies `getPaths(parent)` returns the parent plus true descendants while excluding prefix-only paths such as `/path3-subdir`. `testGetQuotaUsage()` verifies null behavior for missing entries and no-quota entries, then confirms lookup of the nearest ancestor with an actual namespace or space quota.

Control flow is simple: populate the manager map with synthetic paths, call the lookup method under test, and assert returned values. The second test mutates a reusable builder through unset quota, quota set on a parent, no-quota child, and quota-set child to exercise ancestor precedence.

State and persistence behavior is in-memory only. There is no state store, cluster, or filesystem. The manager cache is reset in `@AfterEach`, so tests guard against path lookup regressions without persistence side effects.

Dependencies and integration points are minimal but important because the full Router quota service depends on these semantics when evaluating quotas for child operations and mount-table descendants. Risks covered include accidental prefix matching, returning unset quota definitions as active quota, and choosing a farther ancestor over the closest quota-bearing path. Test signals are exact set size/content checks and quota field assertions.
