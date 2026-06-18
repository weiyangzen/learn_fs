# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 85425-86952

## Chunk Scope

This chunk is the end of the `Test-Cluster-TiKV-Details` Grafana dashboard JSON. It starts inside the `TTL expire count` graph panel, then defines the remaining TTL panels, a collapsed `Config` row, dashboard templating variables, default time range, refresh intervals, and final dashboard identity metadata.

The researched source span is `sources/storage-engines/tikv/metrics/grafana/tikv_details.json:85425-86952`. Because this is a generated/configuration dashboard document rather than executable code, the important "APIs" are Grafana dashboard schema objects, Prometheus query expressions, variable definitions, and panel transformations.

## Purpose

The chunk adds observability for TiKV TTL activity and exposes live TiKV runtime configuration tables. The TTL panels track expiry throughput, checker coverage, checker action rates, compact-task latency, and poll interval. The Config row gives operators instant table views over exported TiKV configuration metrics for RocksDB DB options, RocksDB CF options, flow control, and raftstore options.

The bottom of the file defines the cross-dashboard filter model used by the entire dashboard: Kubernetes cluster, TiDB cluster, database, storage command, instance, Titan database, extra grouping mode, and optional quantile. These variables are substituted into PromQL selectors throughout the dashboard, including the TTL and Config panels in this chunk.

## Important Dashboard Objects and Query Interfaces

### TTL graph/stat panels

- `TTL expire count` is already in progress when the chunk begins. The visible tail shows it is a graph panel with a time x-axis and `none` unit on the primary y-axis. The preceding query context immediately before the chunk uses `tikv_ttl_expire_kv_count_total` as a per-instance rate.
- `TTL expire size` (`id: 624`) is a graph panel at `gridPos x=12,y=0,w=12,h=7`. Its target computes `sum(rate(tikv_ttl_expire_kv_size_total{...}[$__rate_interval])) by (instance)` and displays bytes per second grouped by TiKV instance.
- `TTL check progress` (`id: 625`) computes `sum(rate(tikv_ttl_checker_processed_regions{...}[$__rate_interval])) by (instance) / sum(rate(tikv_raftstore_region_count{type="region",...}[$__rate_interval])) by (instance)`. It is formatted as `percentunit`, implying a progress ratio rather than a raw count.
- `TTL checker actions` (`id: 626`) graphs `sum(rate(tikv_ttl_checker_actions{...}[$__rate_interval])) by (type, $additional_groupby)` with legend `{{type}} {{$additional_groupby}}`. It exposes action throughput by action type and optionally by instance.
- `TTL checker compact duration` (`id: 627`) is a latency/count graph for `tikv_ttl_checker_compact_duration_*`. It renders `histogram_quantile(0.9999, ...)`, `histogram_quantile(0.99, ...)`, average duration from `_sum / _count`, and operation count from `_count`. Series overrides put `count` on y-axis 2 with negative-Y transform and draw `avg` on y-axis 1.
- `TTL checker poll interval` (`id: 628`) is a stat panel using `max(tikv_ttl_checker_poll_interval{type="tikv_gc_run_interval",...})`. It reduces with `lastNotNull`, uses unit `ms`, and shows a current scalar rather than a time-series graph.

All TTL panels use datasource `${DS_TEST-CLUSTER}`, cluster filters `{k8s_cluster="$k8s_cluster", tidb_cluster="$tidb_cluster", instance=~"$instance"}`, and either `$__rate_interval` for rates/histograms or an instant-ish current query for the stat panel.

### Config row and table panels

The collapsed `Config` row (`id: 629`, `type: row`, `collapsed: true`) contains four table panels:

- `RocksDB DB Config` (`id: 630`) queries `tikv_config_rocksdb_db{...}` as an instant table.
- `RocksDB CF Config` (`id: 631`) queries `tikv_config_rocksdb_cf{...} or (tikv_config_rocksdb unless tikv_config_rocksdb_cf)`. The fallback preserves compatibility with exporters that still publish the older `tikv_config_rocksdb` metric instead of the CF-specific metric.
- `Flow Control Config` (`id: 632`) queries `tikv_config_flow_control{...}` as an instant table.
- `Raftstore Config` (`id: 633`) queries `tikv_config_raftstore{...}` as an instant table.

Each table panel uses the same `organize` transformation: hide `Time`, `__name__`, and `job`; rename `name` to `Option`; and rename `Value #A` to `Value`. Field overrides also display the field column as `Option` and the last non-null value as `Value`.

### Dashboard variables and metadata

The chunk closes the panel list and defines the dashboard-wide templating list:

- `k8s_cluster`: hidden query variable from `label_values(tikv_engine_block_cache_size_bytes, k8s_cluster)`.
- `tidb_cluster`: hidden query variable from `label_values(tikv_engine_block_cache_size_bytes{k8s_cluster ="$k8s_cluster"}, tidb_cluster)`.
- `db`: visible multi-select with all enabled, sourced from `label_values(tikv_engine_block_cache_size_bytes{...}, db)`.
- `command`: visible multi-select with all enabled, sourced from non-zero `tikv_storage_command_total` series and regex-extracting the `type` label.
- `instance`: visible multi-select with `allValue: ".*"`, sourced from `label_values(tikv_engine_size_bytes{...}, instance)`. TTL and Config queries rely on this being regex-compatible because selectors use `instance=~"$instance"`.
- `titan_db`: hidden multi-select with all enabled, sourced from `label_values(tikv_engine_titandb_num_live_blob_file{...}, db)`.
- `additional_groupby`: custom variable with `none` and `instance`. TTL action and compact-duration panels include it in `by (...)` clauses and legend text.
- `optional_quantile`: custom variable with `0.99`, `0.999`, `0.9999`, `0.99999`, and `1`. This variable is not consumed by the panels visible in this chunk, but other dashboard chunks may use it for parameterized quantile queries.

Dashboard-level metadata sets `refresh: "1m"`, default time range `now-1h` to `now`, browser timezone, dark style, schema version 14, UID `RDVQiEzZz`, title `Test-Cluster-TiKV-Details`, and version `0`.

## Control Flow and Data Flow

There is no imperative control flow in this JSON. Runtime behavior is driven by Grafana:

1. Grafana loads the dashboard and resolves `${DS_TEST-CLUSTER}` to a Prometheus-compatible datasource.
2. Hidden variables `k8s_cluster` and `tidb_cluster` are populated first from block-cache metrics.
3. Visible variables such as `db`, `command`, and `instance` are populated from label queries constrained by the selected cluster variables.
4. TTL graph panels substitute variables into PromQL selectors and evaluate rates over `$__rate_interval`.
5. Grafana renders time-series panels with shared tooltips, table legends, max/current display, hidden empty/zero series, and nulls rendered as zero for the TTL graphs.
6. The Config row remains collapsed until an operator expands it. Its table panels run instant queries and then apply field transformations to show option/value rows.

The query data path is Prometheus metric export from TiKV to Grafana. The dashboard itself persists only panel definitions, variable definitions, layout, and rendering configuration.

## State and Persistence Behavior

The persisted state is this dashboard JSON, including panel IDs, layout coordinates, variable defaults, refresh policy, and timepicker options. Runtime selections for variables are not meaningfully initialized in this chunk: most `current` entries have `text` and `value` set to `null`, and the custom variables have empty `current` objects. Grafana will resolve these on load or during import.

The `Config` row is persisted with `collapsed: true`, so its four table panels are embedded under the row's `panels` array instead of the top-level visible layout. This matters for dashboard editing and import/export because collapsed-row child panels carry their own `gridPos` relative to the row.

Panel-level state is intentionally minimal. Alerts are not defined; `thresholds` are empty; `links` and `dataLinks` are empty. The dashboard is therefore a read-only observability surface, not an alerting or action surface.

## Dependencies and Integration Points

This chunk depends on these external contracts:

- Grafana dashboard JSON schema version 14 and legacy panel types `graph`, `table`, and `stat`.
- The Prometheus datasource variable `${DS_TEST-CLUSTER}`.
- TiKV metric names: `tikv_ttl_expire_kv_size_total`, `tikv_ttl_checker_processed_regions`, `tikv_raftstore_region_count`, `tikv_ttl_checker_actions`, `tikv_ttl_checker_compact_duration_bucket`, `_sum`, `_count`, `tikv_ttl_checker_poll_interval`, `tikv_config_rocksdb_db`, `tikv_config_rocksdb_cf`, `tikv_config_rocksdb`, `tikv_config_flow_control`, `tikv_config_raftstore`, `tikv_engine_block_cache_size_bytes`, `tikv_storage_command_total`, `tikv_engine_size_bytes`, and `tikv_engine_titandb_num_live_blob_file`.
- Required labels include `k8s_cluster`, `tidb_cluster`, `instance`, `type`, `db`, `name`, and histogram bucket label `le`.
- Grafana variable substitution semantics for `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, and `$additional_groupby`.

Integration-wise, the TTL panels tie TiKV's TTL subsystem to raftstore region count and compaction-duration histograms. The Config row integrates TiKV's exported configuration metrics with Grafana table transformations so operational configuration can be inspected without shelling into TiKV nodes.

## Risks and Edge Cases

- `TTL check progress` divides a rate of processed regions by a rate of region count. Region count is typically a gauge-like count; using `rate()` on it can produce zero, negative, or noisy denominators when region count changes slowly. That can make the progress ratio unstable or empty.
- `$additional_groupby` includes `none`, and this chunk interpolates it directly into `by (type, $additional_groupby)` and `by ($additional_groupby)`. PromQL support for a literal `none` label only works as a grouping label with no matching label values; it does not mean "group by nothing". This may create confusing empty legend segments or unintended grouping unless upstream dashboard generation intentionally uses a synthetic `none` label pattern.
- Several graph panels use `nullPointMode: "null as zero"`. Missing exporter data, scrape failures, or label mismatch can look like real zero throughput.
- Config panels use instant table queries with `maxDataPoints: 100`. Clusters with many options, instances, or label combinations may truncate or crowd table output.
- The RocksDB CF config fallback `tikv_config_rocksdb unless tikv_config_rocksdb_cf` is useful for compatibility but can mix legacy and current metric shapes if both are partially present.
- Template variables are bootstrapped from block-cache and engine-size metrics. If those metrics are missing while TTL or config metrics exist, variables may fail to populate and downstream panels will appear empty.
- Grafana schema version 14 and old `graph`/`table` panel settings may need migration in newer Grafana versions; field config and transformation fields are a mix of old and newer panel APIs.

## Test and Validation Signals

Useful validation for this chunk should include:

- Import `tikv_details.json` into a supported Grafana version and verify the dashboard parses with UID `RDVQiEzZz` and title `Test-Cluster-TiKV-Details`.
- In a Prometheus test environment with TiKV metrics, check that all variable queries populate in this order: `k8s_cluster`, `tidb_cluster`, `instance`, `db`, `command`, and `titan_db`.
- Run the TTL PromQL expressions directly in Prometheus for selected clusters and verify no parse errors occur, especially queries using `$additional_groupby`.
- Compare `TTL expire count` and `TTL expire size` with known TTL expiry workloads to confirm the counters are monotonic and the byte panel uses the expected `bytes` unit.
- Validate `TTL checker compact duration` by checking that `_bucket`, `_sum`, and `_count` series share compatible labels and that histogram quantiles produce non-empty series.
- Expand the collapsed Config row and verify each table shows `Option` and `Value` columns after the `organize` transformation, with `Time`, `__name__`, and `job` hidden.
- Exercise the `instance=All` path and confirm `allValue: ".*"` produces valid regex selection in every TTL and Config query in this chunk.

## Chunk Handoff Notes

For final per-file reconciliation, this chunk should be merged with earlier `tikv_details.json` chunks as the dashboard footer. Its main cross-chunk dependencies are the start of the `TTL expire count` panel before line 85425 and any earlier panels that consume `optional_quantile`, `db`, `command`, or `titan_db`. This chunk supplies the final dashboard-level variable definitions and therefore helps explain variable references appearing throughout the full file.
