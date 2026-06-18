# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/AlwaysOnMetricsService.java

Purpose: metrics-sink lifecycle variant that starts metrics reporting immediately when the master service starts, including standby mode.

Important APIs/types/functions: overrides `start`, `promote`, `demote`, and `stop` from `MetricsService`.

Control flow: `start` logs and calls `startMetricsSystem`; `promote` and `demote` do nothing because sinks remain active across primary state changes; `stop` calls `stopMetricsSystem`.

State and persistence: no fields. Sink state lives in the global `MetricsSystem`.

Dependencies/integration: selected by `MetricsService.Factory` when `STANDBY_MASTER_METRICS_SINK_ENABLED` is true. Used by master process startup tests parameterized over standby metric behavior.

Risks: repeated start or stop behavior depends on `MetricsSystem` idempotency. Always-on standby reporting can duplicate cluster sink output if deployments expect only primary masters to emit metrics.

Test signals: verify sink start on service start, no sink changes on promote/demote, sink stop on stop, and factory selection.
