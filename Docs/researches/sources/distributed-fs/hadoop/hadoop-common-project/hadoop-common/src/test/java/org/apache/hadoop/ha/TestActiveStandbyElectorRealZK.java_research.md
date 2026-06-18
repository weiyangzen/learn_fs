# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElectorRealZK.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElectorRealZK.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElectorRealZK.java

Purpose: this integration test validates `ActiveStandbyElector` behavior against a real ZooKeeper server from `ClientBaseWithFixes`, complementing the mocked unit coverage with actual sessions, ephemeral nodes, watches, and ACL updates.

Important APIs and types: creates two `ActiveStandbyElector` instances with mocked `ActiveStandbyElectorCallback`s, unique `PARENT_DIR`, byte-array app data, and real `ZooKeeperServer`. Helpers include `checkFatalsAndReset()`, `ActiveStandbyElectorTestUtil.waitForActiveLockData()`, and `waitForElectorState()`.

Control flow: `setUp()` starts ZooKeeper and initializes electors. `testActiveStandbyTransition()` walks through parent creation, first active, second standby, quit-based takeover, rejoin as standby, session expiration of each elector, fencing callbacks, and eventual standby recovery. Additional tests expire active and standby sessions, verify `quitElection(false)` suppresses accidental rejoin after an expired event, and ensure reconnect without prior election participation does not start an election.

State and persistence: real persistent parent znodes and ephemeral lock znodes are used. Session IDs are invalidated through `ZooKeeperServer.closeSession()`, and active lock data is inspected from ZooKeeper. ACL state is tested by precreating a parent znode, mutating its data/version, and calling `ensureParentZNode()` with read-only ACLs.

Dependencies and integration points: depends on ZooKeeper server internals, Mockito timeout verification, Hadoop elector utilities, Guava `Ints`, and JUnit timeouts to bound asynchronous behavior.

Risks: timing-sensitive waits and `Thread.sleep()` make this more integration-flaky than pure unit tests. Shared static `PARENT_DIR` is UUID-based, reducing collision risk but tying all methods in the class to one path.

Test signals: verifies no fatal callbacks, correct active/standby role callbacks, fencing of old active data after session loss, safe no-rejoin behavior after explicit quit, and parent ACL update compatibility with existing znodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElectorRealZK.java -->
