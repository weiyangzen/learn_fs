# sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.cc

## Purpose
`PrometheusExporter.cc` implements the EOS MGM Prometheus HTTP metrics endpoint. It adapts in-memory MGM traffic-shaping state into `prometheus::MetricFamily` objects, gates collection to the active master, wraps high-cardinality collectors in a cache, and registers the resulting collectors with a `prometheus::Exposer`.

## Important APIs, Types, And Functions
The public implementation is `PrometheusExporter::PrometheusExporter(...)` plus the default destructor. Internal helpers include `MasterOnlyCollectable`, `MonitoringCollector`, `TrafficShapingCollector`, `EntityTotals`, `StandardKey`, `AllKey`, `LabelOrUnknown()`, metric-family builders, `AddGauge()`, `AddCounter()`, `AddReadWriteCounters()`, `AddLoopStats()`, and `AddPolicyMetrics()`.

`TrafficShapingCollector::Collect()` is the main exporter path. It creates metric families for cumulative IO bytes and operations, per-filesystem IO, all-tag IO, loop latency, report processing rate, map cardinality, policy bytes, reservation pressure, traffic-shaping configuration, and the `eos ns stat` compatible enabled flag. The collector delegates population to `AddCounterFamilies()`, `AddSystemFamilies()`, `AddPolicyFamilies()`, `AddPressureFamilies()`, and `AddConfigFamilies()`.

## Control Flow
The constructor creates a `prometheus::Exposer` on the supplied bind address with 8 worker threads, then registers two master-gated collectables: a lightweight `MonitoringCollector` exposing cache TTL and a cached `TrafficShapingCollector` exposing traffic-shaping data. `MasterOnlyCollectable::Collect()` returns an empty vector unless the supplied `should_collect` predicate exists and returns true.

At scrape time, `TrafficShapingCollector` asks `TrafficShapingEngine` for its manager. If no manager is available, no traffic-shaping metrics are emitted. Otherwise it constructs all families, fills them from manager snapshots, and returns the vector. All-tag metrics are emitted only when the current detail-level cardinality is at or below `kMaxAllTagsMetricEntries` (50,000); otherwise the exporter emits limit status and suppresses those high-cardinality series.

## State And Persistence Behavior
The exporter owns no persistent EOS state. Runtime state is limited to the exposer, collector objects, cluster label string, cache TTL, and references into `TrafficShapingEngine`. Counters are derived from traffic-shaping cumulative snapshots; gauges are derived from current engine and manager configuration. The only retention/caching behavior comes from `CachedCollectable`, configured by the constructor TTL.

## Dependencies And Integration Points
This file integrates `prometheus-cpp` (`Collectable`, `Exposer`, `MetricFamily`, `ClientMetric`) with EOS traffic shaping (`TrafficShapingEngine`, `TrafficShapingManager`, `TrafficShapingPolicy`, snapshot types) and EOS label helpers (`UidLabel`, `GidLabel`, `NodeLabel`, `kUnknownId`). It is started and stopped by `XrdMgmOfs::ApplyMonitoringConfig()` and uses the MGM instance name as the `cluster` label.

## Risks And Edge Cases
Metric cardinality is the central risk: all-tag metrics include node, fsid, app, uid, gid, and compatibility labels, so the hard 50,000-entry cap prevents scrape overload but can hide detail. Label compatibility also duplicates uid/gid fields (`uid`, `uid_id`, `uid_name`, `gid`, `gid_id`, `gid_name`, `groups`), so label changes could break dashboards. The collector assumes manager snapshot methods are safe during concurrent scrapes. Disabled user policies export zero for user limit/reservation gauges while controller limits still export raw values, which consumers must interpret correctly.

## Test Signals
Useful tests include master versus non-master collection, cache TTL metric presence, manager-null behavior, all-tag export below/equal/above 50,000 entries, aggregate/detail-level projections, policy enabled/disabled values, reserved-app pressure with missing pressure samples, config gauge values, and scrape output label compatibility for existing dashboards.
