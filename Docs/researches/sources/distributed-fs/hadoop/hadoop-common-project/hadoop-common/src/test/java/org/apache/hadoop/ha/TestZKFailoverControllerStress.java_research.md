# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverControllerStress.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverControllerStress.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverControllerStress.java

Purpose: this stress test repeatedly perturbs `ZKFailoverController` clusters to catch race conditions, fatal thread exceptions, and shared-resource split-brain during rapid automatic failovers.

Important APIs and types: uses `MiniZKFCCluster`, real ZooKeeper server from `ClientBaseWithFixes`, `ActiveStandbyElector`, `ServerCnxn.DisconnectReason`, Mockito `Answer`, and `RandomlyThrow` to inject intermittent health failures.

Control flow: setup creates a cluster with `ZK_QUORUM_KEY`. `testExpireBackAndForth()` repeatedly expires active sessions in alternating directions and verifies failover. `testRandomExpirations()` randomly expires any current elector session and checks the test context for exceptions. `testRandomHealthAndDisconnects()` configures high elector retry count, randomly fails health checks, starts the cluster after mocking, then closes all ZooKeeper server connections every 50 ms.

State and persistence: state includes ZK sessions, health monitor results, random health-check exceptions, HA roles, and shared-resource ownership checked during cluster stop. ZooKeeper lock state is continuously recreated through elections.

Dependencies and integration points: depends on real ZooKeeper connection management, HA health monitor callbacks, `MiniZKFCCluster` wait/exception propagation, and Mockito partial real-method invocation.

Risks: intentionally nondeterministic random behavior can expose races but may be flaky under slow CI. Runtime is fixed at 30 seconds plus timeout cushion, making this expensive relative to unit tests.

Test signals: no uncaught exceptions, successful repeated failovers, and no shared-resource violations on teardown indicate the ZKFC system tolerates repeated session expiration, health instability, and disconnect storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverControllerStress.java -->
