# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElector.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElector.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElector.java

Purpose: this unit test exercises `ActiveStandbyElector` against a mocked `ZooKeeper` client, focusing on election state transitions, asynchronous callback handling, retry behavior, ACL setup, parent znode creation, active-data lookup, and optional SSL ZooKeeper client configuration.

Important APIs and types: `ActiveStandbyElectorTester` overrides `connectToZooKeeper()` to return `mockZK` and `sleepFor()` to accumulate retry delay without blocking. Tests drive `joinElection()`, `processResult()` for create/stat callbacks, `processWatchEvent()`, `quitElection()`, `getActiveData()`, `ensureParentZNode()`, `createZooKeeper()`, and callback methods on `ActiveStandbyElectorCallback`.

Control flow: setup builds an elector rooted at `/parent/node`. Tests manually inject ZooKeeper result codes such as `OK`, `NODEEXISTS`, `CONNECTIONLOSS`, `NONODE`, `SESSIONEXPIRED`, and fatal codes. Create success fences prior breadcrumb data before `becomeActive`; node-exists causes standby and monitor watch setup; deletion causes re-election; disconnect moves to neutral and reconnect monitors; expiration creates a new session and rejoins only if app data is known.

State and persistence: the tested state is elector role, pending monitor flag, retry count, session identity, lock znode data, breadcrumb znode data, and parent znode ACL/version behavior. Persistence is simulated through `ZooKeeper.create`, `exists`, `getData`, `setData`, `delete`, `getACL`, and `setACL` verification.

Dependencies and integration points: uses Mockito, JUnit 5, ZooKeeper watcher and callback APIs, Hadoop `CommonConfigurationKeys`, `SecurityUtil.TruststoreKeystore`, and ZooKeeper `ZKClientConfig`/`ClientX509Util`.

Risks: tests assert exact fatal-error strings and exact retry thresholds, so production changes to diagnostics or default retry policy can break them. Because callbacks are driven manually, they validate elector logic more than real ZooKeeper ordering.

Test signals: covers null app data validation, duplicate standby suppression, breadcrumb deletion on quit, parent ACL updates when nodes already exist, `ActiveNotFoundException`, no-election-before-health, and SSL vs non-SSL ZK client property propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestActiveStandbyElector.java -->
