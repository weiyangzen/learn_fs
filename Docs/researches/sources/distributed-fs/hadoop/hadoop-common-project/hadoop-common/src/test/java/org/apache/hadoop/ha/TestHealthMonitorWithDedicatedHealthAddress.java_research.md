# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitorWithDedicatedHealthAddress.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitorWithDedicatedHealthAddress.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitorWithDedicatedHealthAddress.java

Purpose: this subclass reuses all `TestHealthMonitor` cases with a `DummyHAService` that has a separate health-check RPC address, ensuring monitor behavior is identical when health probes are routed to a dedicated endpoint.

Important APIs and types: it overrides only `createDummyHAService()`, returning a `DummyHAService` with service address, health address, and auto-failover enabled.

Control flow: inherited setup and tests start the monitor, mutate service health/unreachability, and validate state transitions. The only control-flow difference is the target address chosen by `HealthMonitor` proxy creation.

State and persistence: all state comes from the inherited test: monitor thread state, dummy service flags, and proxy count. No durable state is introduced.

Dependencies and integration points: integrates dedicated health-address support in `HAServiceTarget`/`DummyHAService` with the generic `HealthMonitor` test suite.

Risks: because it inherits all tests, failures can be caused either by dedicated-address routing or base monitor behavior; debugging requires comparing against `TestHealthMonitor`.

Test signals: a pass confirms health monitoring, retries, failure-state propagation, and callback failure handling work when the HA service exposes a separate health RPC address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitorWithDedicatedHealthAddress.java -->
