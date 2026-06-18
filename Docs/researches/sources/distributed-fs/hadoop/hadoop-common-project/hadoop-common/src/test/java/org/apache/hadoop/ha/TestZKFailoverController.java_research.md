# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverController.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverController.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverController.java

Purpose: this integration suite validates `ZKFailoverController` end-to-end with `MiniZKFCCluster` and a real ZooKeeper server. It covers formatting, ACL/auth, fencer requirements, automatic failover, graceful failover, observer handling, ZooKeeper outages, RPC security policy, and multi-node election.

Important APIs and types: setup configures digest auth/ACL, `ZKFailoverController.ZK_QUORUM_KEY`, and `MiniZKFCCluster`. Tests use `DummyZKFC`, `DummyHAService`, `ActiveStandbyElector`, `ZKFCProtocol`, `ZKFCRpcServer`, `PolicyProvider`, `RefreshAuthorizationPolicyProtocol`, and `LambdaTestUtils`.

Control flow: command-line tests run `DummyZKFC.run()` with `-formatZK`, `-force`, and `-nonInteractive`. Runtime tests start two or three ZKFCs, mutate health/state/failure flags, expire sessions, stop and restart ZooKeeper, invoke `cedeActive()` and `gracefulFailover()`, and wait for lock-holder or HA/elector states. Graceful failover cases validate success, unhealthy target rejection, observer rejection, active transition failure rollback, standby transition failure fencing, and fence failure propagation.

State and persistence: persistent state is ZooKeeper parent, lock, breadcrumb, ACLs, and auth. Runtime state includes HA service state, health monitor state, elector state, fencer counts, transition counts, and ZK sessions. ACL formatting is verified by unauthenticated ZooKeeper read failure.

Dependencies and integration points: integrates ZooKeeper, ZKFC command parsing, automatic failover enablement, fencer checks, HA RPC, service authorization policy, digest ACLs, and the mini harness.

Risks: heavy asynchronous coverage is bounded by a class-level timeout but can be sensitive to scheduling. ACL tests depend on digest auth correctness. Some cases rely on exact exception text fragments.

Test signals: verifies expected error codes for no parent, no ZK, denied format, disabled auto-failover, and missing fencer; correct failover on bad health/state/lost sessions; no failover during ZK outage; cede-active delay semantics; no fencing on clean graceful failover; fencing when graceful standby fails; and three-ZKFC transition counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestZKFailoverController.java -->
