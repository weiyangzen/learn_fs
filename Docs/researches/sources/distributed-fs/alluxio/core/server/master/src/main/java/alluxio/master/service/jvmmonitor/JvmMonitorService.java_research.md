# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/jvmmonitor/JvmMonitorService.java

Purpose: optional `SimpleService` that starts a JVM pause monitor for the master and registers gauges for pause statistics.

Important APIs/types/functions: synchronized `start`, `promote`, `demote`, `stop`, and nested `Factory.create`. The service owns nullable `JvmPauseMonitor mJvmPauseMonitor`.

Control flow: factory returns `NoopService` when `MASTER_JVM_MONITOR_ENABLED` is false. `start` checks the monitor is absent, constructs `JvmPauseMonitor` from sleep/warn/info threshold configuration, starts it, and registers total/info/warn pause gauges if absent. `promote` and `demote` are no-ops. `stop` stops and clears the monitor if present.

State and persistence: monitor reference is guarded by the service instance lock. Metrics are registered in the global metrics system; there is no journaled state.

Dependencies/integration: depends on `Configuration`, `PropertyKey`, `MetricKey`, `MetricsSystem`, and `JvmPauseMonitor`. `ServerIndicator` later reads the total pause metric when throttling is enabled.

Risks: `start` is intentionally single-use until `stop` clears the monitor. Registered gauges capture the monitor instance; after stop/start, `registerGaugeIfAbsent` may keep an older supplier depending on metrics registry behavior.

Test signals: `JvmMonitorServiceTest` should cover disabled factory, start/stop lifecycle, duplicate start rejection, metric registration, and no-op promotion/demotion.
