# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/PrimaryOnlyMetricsService.java

Purpose: metrics-sink lifecycle variant that reports only while the master is primary.

Important APIs/types/functions: overrides `start`, `promote`, `demote`, and `stop`.

Control flow: `start` only logs, leaving sinks stopped in standby. `promote` starts sinks. `demote` stops sinks. `stop` also stops sinks to clean up if the service is currently primary or if shutdown follows an unusual state path.

State and persistence: stateless wrapper over global `MetricsSystem`.

Dependencies/integration: default selection by `MetricsService.Factory` when standby sink reporting is disabled. Master process tests assert metric sinks are not serving for standby masters under this configuration.

Risks: double `demote` or `stop` after `demote` relies on sink stop idempotency. If promotion fails after sinks start, cleanup must occur through master process error handling.

Test signals: verify no start-on-standby, start-on-promote, stop-on-demote, stop-on-shutdown, and behavior across promote/demote/promote cycles.
