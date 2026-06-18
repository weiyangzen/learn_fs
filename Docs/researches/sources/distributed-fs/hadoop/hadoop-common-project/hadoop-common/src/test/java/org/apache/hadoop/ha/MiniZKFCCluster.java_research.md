# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/MiniZKFCCluster.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/MiniZKFCCluster.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/MiniZKFCCluster.java

Purpose: `MiniZKFCCluster` is a test harness for running multiple dummy `ZKFailoverController` instances against a real in-process ZooKeeper server. It models HA services, ZKFC threads, shared-resource ownership, health changes, transition failures, fencing failures, and ZooKeeper session loss.

Important APIs and types: the public harness API includes `start()`, `start(int)`, `stop()`, `getService()`, `getElector()`, `getZkfc()`, health and failure setters, `waitForHAState()`, `waitForHealthState()`, `waitForElectorState()`, `expireActiveLockHolder()`, `waitForActiveLockHolder()`, and `expireAndVerifyFailover()`. The nested `DummyZKFCThread` runs a controller under `MultithreadedTestUtil.TestContext`; nested `DummyZKFC` adapts `ZKFailoverController` to `DummyHAService`, serializing targets as four-byte indexes via Guava `Ints`.

Control flow: construction configures fast health-monitor intervals, clears `DummyHAService.instances`, and creates two services. `start(int)` formats the scoped ZK parent through service 0, starts its ZKFC, waits for it to become active, then starts the rest and waits for standby. Failover tests mutate `DummyHAService` flags and use polling waits that also surface thread exceptions through `ctx.checkException()`.

State and persistence: persistent state lives in ZooKeeper under `ZKFailoverController.ZK_PARENT_ZNODE_DEFAULT/dummy-cluster`, with lock and breadcrumb znodes managed by the elector. Local state is held in `svcs`, `thrs`, `sharedResource`, and mutable dummy-service flags. `stop()` interrupts all ZKFC threads, stops the context, and asserts no shared-resource split-brain violation.

Dependencies and integration points: integrates HA service protocol stubs, `ActiveStandbyElector`, `HealthMonitor`, ZooKeeper server internals, RPC server setup, and `DummySharedResource`. It intentionally bypasses login and admin access checks for tests.

Risks: polling loops rely on external test timeouts; stale `DummyHAService.instances` would corrupt target decoding, so the constructor clears it. Session-expiration tests read ZK internals directly and assume lock data equals service index bytes.

Test signals: downstream tests use this harness to verify automatic failover, graceful failover, observer handling, fencing, session re-establishment, and stress conditions while enforcing single ownership of the shared resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/MiniZKFCCluster.java -->
