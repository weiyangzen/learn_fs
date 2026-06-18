# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/MetricsService.java

Purpose: abstract base for master metrics sink lifecycle services.

Important APIs/types/functions: protected `startMetricsSystem`, protected `stopMetricsSystem`, and nested `Factory.create`.

Control flow: subclasses decide when to call the helpers. The start helper reads `METRICS_CONF_FILE` and calls `MetricsSystem.startSinks`; the stop helper calls `MetricsSystem.stopSinks`. Factory selects always-on or primary-only mode from `STANDBY_MASTER_METRICS_SINK_ENABLED`.

State and persistence: no local state. Metrics sinks, reporters, and exported metrics are global `MetricsSystem` concerns and are not journaled here.

Dependencies/integration: implements `SimpleService`; integrated into `AlluxioMasterProcess` registered service list and tested through master start/stop readiness checks.

Risks: factory returns concrete package-private subclasses, so external tests usually observe via lifecycle effects. Misordered lifecycle calls can double-start or double-stop sinks unless `MetricsSystem` tolerates it.

Test signals: `MetricsServiceTest` should cover factory selection, config-file path forwarding, and primary/standby lifecycle behavior through the two subclasses.
