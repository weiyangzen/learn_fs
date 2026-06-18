# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ZKFCTestUtil.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ZKFCTestUtil.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ZKFCTestUtil.java

Purpose: `ZKFCTestUtil` provides a small wait helper for ZK failover controller tests.

Important APIs and types: `waitForHealthState(ZKFailoverController zkfc, HealthMonitor.State state, MultithreadedTestUtil.TestContext ctx)` polls `zkfc.getLastHealthState()` until it equals the expected state.

Control flow: the method loops, optionally calls `ctx.checkException()` to surface background-thread failures, then sleeps 50 ms between checks. It has no internal timeout and relies on the caller's test timeout or surrounding harness.

State and persistence: no state is mutated except thread sleep timing. The observed state is the ZKFC's last health monitor state.

Dependencies and integration points: used by `MiniZKFCCluster.waitForHealthState()` and tests that need background ZKFC exceptions propagated while waiting.

Risks: lack of timeout can hang if callers omit a JUnit timeout or context cancellation. It intentionally favors simple polling over richer synchronization.

Test signals: enables deterministic-ish waits for health state transitions while preserving failure visibility from `MultithreadedTestUtil.TestContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ZKFCTestUtil.java -->
