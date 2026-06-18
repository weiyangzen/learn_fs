# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterFactory.java

Purpose: master factory responsible for constructing and registering the metrics master in core master startup.

Important APIs/types/functions: implements `MasterFactory<CoreMasterContext>`; `isEnabled()` always returns true; `getName()` returns `Constants.METRICS_MASTER_NAME`; `create` builds a `DefaultMetricsMaster`, registers it under `MetricsMaster.class`, and returns it.

Control flow: during master boot, the factory logs creation, constructs `DefaultMetricsMaster` with the shared `CoreMasterContext`, adds it to `MasterRegistry`, and exposes the typed master for later dependencies such as block master and throttle master.

State and persistence: the factory itself is stateless and thread-safe. Metrics persistence and in-memory state belong to `DefaultMetricsMaster`, `MetricsStore`, and the global metrics system.

Dependencies/integration: participates in Alluxio's `MasterFactory` discovery/registration path and provides `MetricsMaster` dependency resolution to other masters.

Risks: because `isEnabled` is unconditional, tests and deployments must account for metrics master creation even when metric collection features are disabled. Duplicate registration behavior depends on `MasterRegistry` semantics and is not guarded here.

Test signals: verify name, unconditional enablement, returned implementation type, and registry lookup after `create`. Existing block/backup tests instantiate it to satisfy block-master dependencies.
