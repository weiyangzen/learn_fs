# sources/control-plane/longhorn/scalability/dev/data-plane-grafana_dashboard.json

## Purpose
Grafana dashboard JSON for "Reference Setup, Scalability, Performance, and Sizing" (`uid` `2fqV-mhSz`). It visualizes Longhorn data-plane benchmark output from `kbench_metric_exporter_*` Prometheus metrics across access mode, test mode, rate-limit mode, IO pattern, and IO type. It refreshes every five seconds in UTC.

## Important APIs, Types, and Queries
The dashboard uses Grafana schema v37, built-in annotations, and custom template variables: `volume_access_mode` (`rwo`, `rwx`), `test_mode` (`read-only`, `write-only`, `read-write`), and `rate_limit_type` (`no-rate-limit`, `rate-limit`). The read panels are stored under a collapsed `Read Performance` row; write panels are expanded under `Write Performance`.

Metrics are organized around `kbench_metric_exporter_iops`, `kbench_metric_exporter_bandwidth`, and `kbench_metric_exporter_latency`. Each metric is filtered by the three variables plus `io_pattern` (`random` or `sequential`) and `io_type` (`read` or `write`). Panels show raw series, `sum by(volume_name)`, `sum by(pod)`, `avg(...)`, and `count(...)` variants for IOPS, bandwidth, and latency.

## Control Flow
Grafana resolves the three custom variables, evaluates hidden panels inside the collapsed read row and visible write panels, then renders time series and text separators. There is no imperative logic; dashboard behavior is driven by templated PromQL labels. The collapsed row preserves read panels while keeping the default view focused on write performance.

## State and Persistence
All dashboard state is in JSON: variable defaults (`rwx`, `write-only`, `rate-limit`), panel IDs/layout, row collapsed state, datasource references, and visualization options. Benchmark data is persisted in Prometheus; the dashboard writes no state.

## Dependencies and Integration Points
Requires Grafana, Prometheus datasource `uid: prometheus`, and a kbench metric exporter that emits the exact label set used by the queries: `volume_access_mode`, `test_mode`, `rate_limit_type`, `io_pattern`, `io_type`, `volume_name`, and `pod`. It integrates with Longhorn scalability/performance test workflows that label metrics consistently.

## Risks
Every panel depends on exact label names and values; missing or renamed labels produce empty graphs. Defaults bias the initial view to RWX, write-only, rate-limited tests. The dashboard does not template namespace, cluster, or datasource. Some count panels are labeled "Pods" while counting metric series/containers, so interpretation depends on exporter cardinality. Collapsed read panels can hide failures in read-test telemetry unless explicitly expanded.

## Test Signals
Validation signals are JSON parse/import success, all template variables selectable, and non-empty PromQL results for both read and write panels after a kbench run. Cross-check average, sum-by-PVC, sum-by-pod, and count panels against raw exporter series to catch label-cardinality drift.
