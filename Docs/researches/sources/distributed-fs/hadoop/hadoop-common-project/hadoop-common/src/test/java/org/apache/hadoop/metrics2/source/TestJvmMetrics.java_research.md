# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/source/TestJvmMetrics.java

## Purpose
Tests JVM metrics collection and monitor integration: pause monitor metrics, GC time monitor metrics/alerts, monitor lifecycle edge cases, singleton semantics, and thread-count collection performance.

## Important APIs, Types, And Functions
Uses `JvmMetrics`, `JvmPauseMonitor`, `GcTimeMonitor`, `MetricsCollectorImpl`, `ServiceOperations.stop()`, and `SubjectInheritingThread`. `teardown()` stops monitors. `updateThreadsAndWait()` scales helper thread population for performance runs.

## Control Flow
Presence tests start monitors, attach them to `JvmMetrics`, collect metrics via mocked builders, and verify tags/gauge families. Lifecycle tests double-start/stop or stop before init/start and expect service-state behavior. GC tests allocate garbage and call `System.gc()` until monitor data and alerts appear. Singleton tests call `initSingleton()` with same/different names. Performance test creates 100-3000 sleeping threads and times two collection modes.

## State And Persistence Behavior
Monitor threads and helper test threads are the main state. `@AfterEach` stops monitors, and performance cleanup reduces helper threads to zero. `JvmMetrics.initSingleton()` is process-global, so tests rely on singleton persistence.

## Dependencies And Integration Points
Integrates metrics2 source collection with Hadoop service lifecycle, JVM MXBeans/thread groups, GC monitoring, pause monitoring, and test metrics assertions.

## Risks
GC alert tests are environment-sensitive because JVM GC behavior is nondeterministic. Performance test prints timings but has no hard performance assertion. Singleton global state can leak process name expectations across tests.

## Test Signals
Signals include `JvmMetrics` records tagged with process/session, memory/thread gauges, `GcTimePercentage`, expected `ServiceStateException` text for invalid lifecycle transitions, positive GC count/percentage/alerts, and singleton object identity.
