# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitor.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitor.java

Purpose: this test verifies `HealthMonitor` state transitions and failure handling against a `DummyHAService`.

Important APIs and types: setup constructs a `HealthMonitor` with short intervals, overrides `createProxy()` to count attempts and optionally throw `OutOfMemoryError`, starts the monitor, and waits for `SERVICE_HEALTHY`. Tests drive `DummyHAService.isHealthy` and `actUnreachable`, add `HealthMonitor.Callback`, and use `shutdown()`/`join()`.

Control flow: `testMonitor()` moves from healthy to unhealthy, back to healthy, then to not responding via simulated unreachable RPC, verifies repeated proxy recreation, and finally recovers. `testHealthMonitorDies()` injects an uncaught error in proxy creation and waits for `HEALTH_MONITOR_FAILED`. `testCallbackThrowsRTE()` proves a throwing callback terminates the monitor into failed state.

State and persistence: state is thread-local/in-memory: monitor thread liveness, `HealthMonitor.State`, dummy service flags, `createProxyCount`, and `throwOOMEOnCreate`. No external persistence exists.

Dependencies and integration points: integrates HA service protocol proxy creation, Hadoop IPC retry configuration, monitor interval configuration, and JUnit timeouts.

Risks: waits poll for up to two seconds and assume short configured intervals are enough on loaded machines. The intentional `OutOfMemoryError` path tests broad failure capture and should not be confused with real heap exhaustion.

Test signals: verifies healthy/unhealthy/not-responding/recovered transitions, retry behavior on disconnection, clean shutdown, monitor failure on uncaught thread errors, and callback exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestHealthMonitor.java -->
