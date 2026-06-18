# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/jvmmonitor/JvmMonitorServiceTest.java

## Purpose
`JvmMonitorServiceTest` verifies the simple-service wrapper around the JVM pause monitor. It checks factory selection, metric registration on start, lifecycle stability across primary/standby transitions, and protection against double start.

## Important APIs, Types, and Functions
The tests use `JvmMonitorService.Factory.create`, `SimpleService.start`, `promote`, `demote`, and `stop`, plus `MetricsSystem.startSinks`, `clearAllMetrics`, `stopSinks`, and `allMetrics`. `checkMetrics` counts registered metric names containing `Server.`.

## Control Flow, State, and Persistence
`before` starts metrics sinks from the configured metrics file; `after` clears metrics and stops sinks. With `MASTER_JVM_MONITOR_ENABLED=false`, the factory must return `NoopService`. With it enabled, start registers three JVM monitor metrics, promote/demote leave them present, and stop does not unregister them. `doubleStart` asserts a second `start` throws `IllegalStateException`.

## Dependencies and Integration Points
The file integrates master simple-service lifecycle code with `JvmMonitorService`, `NoopService`, Alluxio configuration, and the global metrics system.

## Risks
Metric counting by substring is broad and can become fragile if other `Server.` metrics are registered in the same global registry. The test starts metrics sinks, so environmental metrics configuration problems can affect it.

## Test Signals
Passing tests show the factory respects configuration, startup registers the expected JVM monitor gauges, role transitions are idempotent for metrics, and duplicate start is rejected.
