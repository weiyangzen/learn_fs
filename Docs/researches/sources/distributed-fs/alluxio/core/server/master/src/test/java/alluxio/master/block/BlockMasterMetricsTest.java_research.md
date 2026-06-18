# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterMetricsTest.java

Purpose: unit tests for block master gauge registration and values exposed through `DefaultBlockMaster.Metrics`.

Important APIs/types/functions: setup clears metrics, mocks `DefaultBlockMaster`, supplies a `DefaultStorageTierAssoc`, and calls `Metrics.registerGauges`; tests capacity totals/free/used, tier capacity metrics, unique block count, and worker count.

Control flow: each test stubs block master methods, then reads gauges directly from `MetricsSystem.METRIC_REGISTRY` by metric key and tag suffix. Free capacity is validated as total minus used at both cluster and tier levels.

State and persistence: manipulates global metrics registry only; no master persistence.

Dependencies/integration: ties block master metric keys to `MetricsSystem` and storage tier association.

Risks: global registry requires clearing before tests to avoid stale gauges. Gauge names depend on tag string construction using `MetricInfo.TIER`.

Test signals: protects cluster capacity gauges, tier-tagged capacity gauges, unique block gauge, and worker count gauge.
