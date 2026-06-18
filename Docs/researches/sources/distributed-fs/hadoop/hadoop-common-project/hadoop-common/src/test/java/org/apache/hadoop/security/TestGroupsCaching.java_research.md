# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupsCaching.java

Purpose: Broad unit/concurrency coverage for the `Groups` cache: positive/negative caching, static overrides, request coalescing, expiration, background reload, counters, and exception handling.

Important APIs/types/functions: `Groups`, `FakeGroupMapping`, `ExceptionalGroupMapping`, `FakeTimer`, `CommonConfigurationKeys` group cache settings, `cacheGroupsAdd`, `refresh`, `getGroups`, `getNegativeCache`, background counter getters, `CountDownLatch`, and `SubjectInheritingThread`.

Control flow: setup resets fake mapping state and configures it as the group provider. Tests populate fake groups, blacklist users, advance fake time, run concurrent lookup threads, pause/resume mapping calls with a latch, and assert request counts/counter values. Background-refresh cases verify stale values are returned immediately when enabled, blocking reload happens when disabled, failures are counted, old values survive some failures, and entries eventually expire.

State and persistence: static fake provider state (`allGroups`, blacklist, request counters, delay, exception flag, latch), per-test `Configuration`, `Groups` caches, fake time, and background reload executor state.

Dependencies/integration points: Hadoop group mapping cache, shell mapping superclass, AssertJ/JUnit, and thread scheduling.

Risks: many static mutable fields require setup discipline; timing sleeps and background counters can be flaky; static override config bypasses provider calls; exceptions should not poison negative cache.

Test signals: strong signal for cache correctness under concurrency, cache expiry, negative-cache TTL, refresh clearing, stale-value policy, and background reload metrics.
