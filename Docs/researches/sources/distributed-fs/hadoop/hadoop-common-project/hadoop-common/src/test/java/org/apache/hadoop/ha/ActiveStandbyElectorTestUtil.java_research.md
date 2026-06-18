# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ActiveStandbyElectorTestUtil.java

Purpose: polling utility for HA elector tests. It waits for ZooKeeper lock data or elector state transitions while surfacing background test-thread exceptions.

Important APIs and types: `MultithreadedTestUtil.TestContext`, `ZooKeeperServer`, `ActiveStandbyElector`, `ActiveStandbyElector.State`, `ActiveStandbyElector.LOCK_FILENAME`, `Stat`, `NoNodeException`, `Time.now`, and `StringUtils.byteToHexString`.

Control flow: `waitForActiveLockData` loops until the active lock znode data matches expected bytes, or until the node is absent when expected data is `null`. It calls `ctx.checkException()` if a context is supplied, logs current data or missing node every 500 ms, and sleeps 50 ms between checks. `waitForElectorState` loops until `elector.getStateForTests()` equals the expected state, also checking context exceptions and sleeping.

State and persistence: reads ZooKeeper in-memory database state through the test server; it does not mutate state.

Dependencies and integration: used by failover/election tests to coordinate asynchronous ZooKeeper and elector behavior.

Risks and test signals: loops have no internal timeout, so callers must provide external timeout/context handling. Incorrect znode paths or state visibility can cause hangs; context checks are the main safety mechanism.
