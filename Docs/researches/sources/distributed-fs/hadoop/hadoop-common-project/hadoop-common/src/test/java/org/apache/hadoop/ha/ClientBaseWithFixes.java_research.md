# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/ClientBaseWithFixes.java

Purpose: Hadoop-local copy of ZooKeeper `ClientBase` with JMX verification removed to avoid spurious test failures. It provides per-test ZooKeeper server lifecycle, client creation, and wait helpers for HA tests.

Important APIs and types: `ZKTestCase`, `TestableZooKeeper`, `ZooKeeper`, `Watcher`, `CountDownLatch`, `ServerCnxnFactory`, `ZooKeeperServer`, `ZKDatabase`, `FileTxnLog`, `ServerSocketUtil`, `GenericTestUtils`, and JUnit `BeforeEach`/`AfterEach`.

Control flow: static initialization enables ZooKeeper four-letter commands. `setUp` creates the base test dir, sets low log preallocation, initializes client tracking, creates a temp data dir, and starts a server. `createClient` variants create a `TestableZooKeeper`, wait for a `CountdownWatcher` to connect, and track clients for teardown. `send4LetterWord`, `waitForServerUp`, and `waitForServerDown` use socket diagnostics. `createNewServerInstance` starts a `ZooKeeperServer`; `shutdownServerInstance` shuts it down and closes the database. `tearDown` closes clients, stops the server, recursively deletes temp dirs, and resets factory state.

State and persistence: creates temporary ZooKeeper data/log directories under `GenericTestUtils.getTestDir()`, tracks live clients in `allClients`, and uses selected localhost ports.

Dependencies and integration: foundational fixture for HA tests that need embedded ZooKeeper without upstream JMX checks.

Risks and test signals: resource leaks, stuck ports, client list misuse before setup, and unbounded waits around server up/down are primary risks. Four-letter command enablement is test-only and security-sensitive outside tests.
