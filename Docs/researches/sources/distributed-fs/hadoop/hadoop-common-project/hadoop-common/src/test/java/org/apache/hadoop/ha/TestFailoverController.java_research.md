# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestFailoverController.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestFailoverController.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestFailoverController.java

Purpose: this unit test covers `FailoverController.failover()` using `DummyHAService` targets. It validates manual failover, forced fencing, readiness and health checks, rollback/failback behavior, unreachable services, permission failures, and self-failover rejection.

Important APIs and types: `doFailover()` creates a `FailoverController` with `RequestSource.REQUEST_BY_USER`. Tests use `DummyHAService`, `HAServiceProtocol`, `HAServiceStatus`, `AlwaysSucceedFencer`, `AlwaysFailFencer`, and Mockito stubs for `transitionToStandby`, `transitionToActive`, `monitorHealth`, `getServiceStatus`, and proxy acquisition.

Control flow: successful cases transition source to standby and target to active without fencing when graceful transitions work. Failure cases inject access denial, not-ready status, failed health checks, transition failures, dead source proxies, dead target proxies, and fencer failures. The controller either aborts, fences the source, proceeds to target activation, or tries to fail back depending on whether the source cooperated or was fenced.

State and persistence: state is in-memory HA service state and fencer counters. There is no durable persistence. The tests check final `HAServiceState`, fencer call counts, and which service object was fenced.

Dependencies and integration points: integrates failover controller logic with HA RPC protocol semantics, fencer configuration from `NodeFencer`, Hadoop configuration defaults, and service readiness/health checks.

Risks: some assertions depend on dummy fencer static state and `DummyHAService` side effects, so setup isolation matters. The test name `NonExistant` mirrors existing spelling but covers real behavior: proxy calls may fail after proxy creation, not during creation.

Test signals: covers active-to-standby, standby-to-active, active-to-active refusal, access-control failure propagation, force-active bypass of readiness, graceful fencing timeout use, no failback after forced fencing, fencing during failed failback, and zero fencing on self-failover rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestFailoverController.java -->
