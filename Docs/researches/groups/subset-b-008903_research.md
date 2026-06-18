# Research: subset-b-008903

Grouped research for two TiKV Grafana performance dashboard JSON files. Each section preserves the source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/performance_read.json -->
# sources/storage-engines/tikv/metrics/grafana/performance_read.json

## Purpose

`sources/storage-engines/tikv/metrics/grafana/performance_read.json` is a Grafana dashboard definition titled `Test-Cluster-Performance-Read` with UID `4aVOvxcWk`. It is a read-workload performance dashboard for TiDB/TiKV test clusters. The file is declarative JSON, not executable application code: its behavioral surface is Grafana's dashboard schema, nested row panels, graph panels, templating variables, and Prometheus queries.

The dashboard is optimized for diagnosing read-path latency and saturation across TiDB SQL handling, TiDB transaction and TiKV client activity, PD TSO latency, TiKV gRPC work, TiKV storage read pools, coprocessor wait/handle behavior, RocksDB KV read efficiency, and node-level read disk I/O. The default time range is `now-6h` to `now`; `refresh` is `false`, so the dashboard does not auto-refresh unless a viewer changes the setting.

## Important APIs, Types, and Data Contracts

The primary API contract is Grafana dashboard schema version `18`, requiring Grafana `6.1.6`, the legacy `graph` panel plugin, and a Prometheus datasource input named `DS_TEST-CLUSTER` with label `test-cluster`. Every graph panel uses the datasource `${DS_TEST-CLUSTER}`.

The dashboard exposes two query template variables:

- `k8s_cluster`: Prometheus `label_values(tikv_engine_block_cache_size_bytes, k8s_cluster)`.
- `tidb_cluster`: Prometheus `label_values(tikv_engine_block_cache_size_bytes{k8s_cluster="$k8s_cluster"}, tidb_cluster)`.

Both variables are single-select (`multi=false`, `includeAll=false`) and are injected into almost every PromQL selector. This makes the dashboard strongly dependent on TiKV metrics that carry both `k8s_cluster` and `tidb_cluster` labels.

The file uses collapsed row panels as section containers. The top-level rows are:

- `TiDB-Server` with 4 graph children.
- `Parse` with 1 graph child.
- `Compile` with 1 graph child.
- `Transaction` with 3 graph children.
- `KV` with 5 graph children.
- `PD Client` with 2 graph children.
- `gRPC` with 2 graph children.
- `Storage` with 1 graph child.
- `Coprocessor` with 3 graph children.
- `RocksDB-KV` with 5 graph children.
- `Disk` with 4 graph children.

Important Prometheus metrics referenced by this dashboard include:

- TiDB server/session metrics: `tidb_server_handle_query_duration_seconds_bucket`, `tidb_server_get_token_duration_seconds_bucket`, `tidb_server_connections`, `go_memstats_heap_inuse_bytes`, `tidb_session_parse_duration_seconds_bucket`, `tidb_session_compile_duration_seconds_bucket`, `tidb_session_transaction_duration_seconds_bucket`, `tidb_session_transaction_statement_num_bucket`, and `tidb_session_retry_num_bucket`.
- TiDB TiKV client metrics: `tidb_tikvclient_txn_cmd_duration_seconds_bucket`, `tidb_tikvclient_lock_resolver_actions_total`, `tidb_tikvclient_backoff_seconds_bucket`, and `tidb_tikvclient_backoff_seconds_count`.
- PD client metrics: `pd_client_cmd_handle_cmds_duration_seconds_bucket` and `pd_client_request_handle_requests_duration_seconds_bucket` filtered to `type="tso"`.
- TiKV runtime and gRPC metrics: `tikv_grpc_msg_duration_seconds_bucket` and `tikv_thread_cpu_seconds_total`.
- TiKV coprocessor metrics: `tikv_coprocessor_request_wait_seconds_bucket` and `tikv_coprocessor_request_handle_seconds_bucket`.
- RocksDB/TiKV read metrics: `tikv_engine_get_micro_seconds`, `tikv_engine_memtable_efficiency`, `tikv_engine_cache_efficiency`, `tikv_engine_get_served`, `tikv_engine_seek_micro_seconds`, `tikv_engine_locate`, and `tikv_engine_bloom_efficiency`.
- Node exporter disk read metrics: `node_disk_read_time_seconds_total`, `node_disk_reads_completed_total`, and `node_disk_read_bytes_total`.

The graph panel contract uses Grafana fields such as `targets`, `legendFormat`, `xaxis`, `yaxes`, `tooltip`, `lines`, `linewidth`, `fill`, `nullPointMode`, and `gridPos`. Units include seconds (`s`), microseconds (`µs`), operations (`ops`), percent unit (`percentunit`), IOPS (`iops`), bytes, and bytes per second (`Bps`).

## Control Flow and Dashboard Layout

At load time, Grafana resolves the datasource input, evaluates the template variables, then renders only row headers initially because every top-level row has `collapsed=true`. When a row is expanded, Grafana renders the row's nested graph panels and executes their PromQL targets against `${DS_TEST-CLUSTER}`.

The read-path control flow is organized from front-end SQL service latency toward lower storage layers:

1. `TiDB-Server` panels show query duration quantiles (`0.999`, `0.99`, `0.95`, `0.80`), token acquisition latency, connection counts, and TiDB heap memory.
2. `Parse` and `Compile` show 99th percentile SQL parse and compile durations by `sql_type`.
3. `Transaction` shows transaction duration quantiles by `sql_type`, statement count quantiles, and retry count quantiles.
4. `KV` focuses on read commands by filtering `tidb_tikvclient_txn_cmd_duration_seconds_bucket` to `type=~"get|batch_get|seek|seek_reverse"`, plus lock resolver and backoff activity.
5. `PD Client` isolates TSO wait and RPC latency.
6. `gRPC` filters TiKV message duration to `type=~"kv_get|kv_batch_get|coprocessor"` and shows gRPC thread CPU.
7. `Storage` shows `store_read.*` thread CPU as a read-pool pressure signal.
8. `Coprocessor` shows request wait and handle quantiles plus `cop_.*` thread CPU.
9. `RocksDB-KV` shows get/seek microsecond summaries, operation distributions by level or cache path, cache hit ratios, and bloom-prefix efficiency.
10. `Disk` shows node-level read latency, operations, bandwidth, and load.

Most latency panels use `histogram_quantile()` over `sum(rate(..._bucket[1m])) by (le, ...)`; selected TiKV backoff and scheduler-style panels use a longer `[5m]` window to smooth sparse events. RocksDB get/seek duration panels use gauge-like summary metrics with `max(...)` across instances.

## State and Persistence Behavior

The file persists dashboard state as static JSON. Grafana stores the dashboard UID, title, panel IDs, collapsed row state, time picker options, default time window, and variable definitions. There is no runtime mutation in the repository source file; any changes made through the Grafana UI would need to be exported back to JSON to persist in source control.

The dashboard intentionally starts with all rows collapsed. This reduces initial query load but means users must expand sections to execute graph queries. Annotation support is enabled through the built-in `Annotations & Alerts` dashboard annotation with the same datasource, but the dashboard defines no custom links and no embedded alert rules in these graph panels.

Variable values are not persisted with concrete defaults: both variable `current` values are `null`. On import, Grafana must evaluate the Prometheus label queries before the dashboard becomes useful.

## Dependencies and Integration Points

The direct runtime dependencies are Grafana, the legacy graph panel, a Prometheus datasource, TiDB/TiKV metric exporters, PD client metrics, Go runtime metrics, and node exporter disk metrics. The dashboard also assumes a label taxonomy where TiDB, TiKV, PD-client, and node-exporter series all share `k8s_cluster` and `tidb_cluster`.

Integration points include:

- Grafana import/provisioning: the datasource input `DS_TEST-CLUSTER` must be mapped to a real Prometheus datasource.
- TiKV/TiDB monitoring stack: all referenced metrics must exist with compatible names and labels.
- Kubernetes labeling: `k8s_cluster` and `tidb_cluster` must be consistently populated across TiDB, TiKV, PD-client, and node-exporter series.
- Dashboard reconciliation tooling: top-level panels are rows with nested `panels`, so tooling that only scans `.panels[]` will miss all graph targets unless it traverses recursively.

## Risks and Edge Cases

The strongest correctness risk is in the `Block cache hit` panel's `all` target. It references `instance=~"$instance"` and `db="$db"`, but this dashboard defines only `k8s_cluster` and `tidb_cluster` variables. Unless Grafana receives `instance` and `db` from another provisioning layer, that query can evaluate with unresolved or empty template variables. The other block-cache targets hard-code `db="kv"` and do not depend on those missing variables.

The dashboard is versioned for Grafana `6.1.6` and legacy `graph` panels. Newer Grafana deployments may migrate graph panels to time-series panels, but migrations can change rendering defaults, legend behavior, and axis handling.

Because all rows are collapsed, health checks that only look at initial dashboard load may not exercise PromQL queries. Conversely, expanding many rows can generate a burst of Prometheus queries, especially histogram quantile panels over 1-minute windows.

The template variables are derived from `tikv_engine_block_cache_size_bytes`; if that metric is absent or missing labels, both selectors can fail even though many dashboard panels depend on unrelated TiDB or node metrics. This creates a hidden coupling between dashboard usability and block-cache metric availability.

Several panels use `max(...)` over TiKV microsecond metrics rather than grouping by instance. This highlights worst observed values but can hide which node contributed unless legend or query grouping is adjusted.

Disk panels filter only by cluster labels and not by device class. Environments with virtual, loop, or irrelevant devices can make disk latency/load graphs noisy unless Prometheus relabeling filters those devices upstream.

## Test Signals and Validation

Useful static validation signals:

- `jq` should parse the file successfully and confirm required top-level keys such as `__inputs`, `__requires`, `templating`, `panels`, `time`, `title`, and `uid`.
- Recursive panel traversal should find 11 collapsed top-level rows and 31 nested graph panels with Prometheus targets.
- Every graph panel should use `${DS_TEST-CLUSTER}` as datasource.
- Template variables should include exactly `k8s_cluster` and `tidb_cluster`; this also exposes the missing `$instance` and `$db` references in the block-cache `all` query.
- PromQL linting or Grafana query inspection should validate all metric names and label selectors against a representative TiDB/TiKV Prometheus.

Runtime validation should import the dashboard into a Grafana instance with a TiDB/TiKV Prometheus datasource, select a known test cluster, expand every row, and verify that each panel returns non-empty data during a read workload. The most important behavioral checks are read KV command duration, gRPC message duration for `kv_get`, coprocessor wait/handle latency, RocksDB get/seek duration, cache hit ratios, and node read disk I/O.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/performance_read.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/performance_write.json -->
# sources/storage-engines/tikv/metrics/grafana/performance_write.json

## Purpose

`sources/storage-engines/tikv/metrics/grafana/performance_write.json` is a Grafana dashboard definition titled `Test-Cluster-Performance-Write` with UID `Fcw5wqcWk`. It is a write-workload performance dashboard for TiDB/TiKV test clusters. Like the companion read dashboard, this file is declarative Grafana JSON rather than executable code; its meaningful interfaces are dashboard schema objects, row and graph panels, template variables, and Prometheus queries.

The dashboard is tuned for write-path diagnosis from TiDB SQL handling through TiDB transaction commit, TiKV gRPC prewrite/commit traffic, scheduler latch and command latency, raftstore proposal/apply latency, RocksDB raft and KV write duration, async apply CPU, and node-level write disk I/O. Its default time range is `now-1h` to `now`, and `refresh` is `5s`, making it much more live-update oriented than the read dashboard.

## Important APIs, Types, and Data Contracts

The dashboard uses Grafana dashboard schema version `18`, requires Grafana `6.1.6`, uses legacy `graph` panels, and declares one Prometheus datasource input named `DS_TEST-CLUSTER` with label `test-cluster`. Every graph panel points to `${DS_TEST-CLUSTER}`.

It defines the same two single-select Prometheus query variables as the read dashboard:

- `k8s_cluster`: `label_values(tikv_engine_block_cache_size_bytes, k8s_cluster)`.
- `tidb_cluster`: `label_values(tikv_engine_block_cache_size_bytes{k8s_cluster="$k8s_cluster"}, tidb_cluster)`.

Top-level layout is a set of collapsed row panels:

- `TiDB-Server` with 4 graph children.
- `Parse` with 1 graph child.
- `Compile` with 1 graph child.
- `Transaction` with 3 graph children.
- `KV` with 5 graph children.
- `PD Client` with 2 graph children.
- `gRPC` with 2 graph children.
- `Scheduler` with 3 graph children.
- `raftstore` with 3 graph children.
- `RocksDB-Raft` with 2 graph children.
- `RocksDB-KV` with 4 graph children.
- `Disk` with 4 graph children.

Important Prometheus metrics referenced by this dashboard include:

- TiDB server/session metrics: `tidb_server_handle_query_duration_seconds_bucket`, `tidb_server_get_token_duration_seconds_bucket`, `tidb_server_connections`, `go_memstats_heap_inuse_bytes`, `tidb_session_parse_duration_seconds_bucket`, `tidb_session_compile_duration_seconds_bucket`, `tidb_session_transaction_duration_seconds_bucket`, `tidb_session_transaction_statement_num_bucket`, and `tidb_session_retry_num_bucket`.
- TiDB TiKV client commit metrics: `tidb_tikvclient_txn_cmd_duration_seconds_bucket` filtered to `type=~"commit"`, `tidb_tikvclient_lock_resolver_actions_total`, `tidb_tikvclient_backoff_seconds_bucket`, and `tidb_tikvclient_backoff_seconds_count`.
- PD TSO metrics: `pd_client_cmd_handle_cmds_duration_seconds_bucket` and `pd_client_request_handle_requests_duration_seconds_bucket` filtered to `type="tso"`.
- TiKV gRPC and thread metrics: `tikv_grpc_msg_duration_seconds_bucket` filtered to `kv_prewrite|kv_commit`, and `tikv_thread_cpu_seconds_total` for `grpc.*`, `sched_.*`, `(raftstore|rs)_.*`, and `apply_[0-9]+`.
- Scheduler metrics: `tikv_scheduler_latch_wait_duration_seconds_bucket`, `tikv_scheduler_latch_wait_duration_seconds_sum`, `tikv_scheduler_latch_wait_duration_seconds_count`, and `tikv_scheduler_command_duration_seconds_bucket`.
- Storage and raftstore write metrics: `tikv_storage_engine_async_request_duration_seconds_bucket`, `_sum`, `_count`, `tikv_raftstore_request_wait_time_duration_secs_bucket`, `tikv_raftstore_append_log_duration_seconds_bucket`, `tikv_raftstore_apply_wait_time_duration_secs_bucket`, `tikv_raftstore_apply_log_duration_seconds_bucket`, `_sum`, and `_count`.
- RocksDB write metrics: `tikv_engine_write_micro_seconds` for `db="raft"` and `db="kv"`.
- Node exporter disk write metrics: `node_disk_write_time_seconds_total`, `node_disk_writes_completed_total`, and `node_disk_written_bytes_total`.

The panels use the legacy graph panel schema: `targets`, `legendFormat`, axes, tooltip configuration, `nullPointMode`, `lines`, `fill`, `linewidth`, and layout positions. Units include seconds, microseconds, short counts, percent units, IOPS, bytes, and bytes per second.

## Control Flow and Dashboard Layout

Grafana loads the dashboard, resolves the Prometheus datasource input, evaluates `k8s_cluster` and `tidb_cluster`, and renders collapsed row headers. Expanding a row triggers the nested graph panels and their PromQL target evaluations.

The write-path diagnostic flow is layered as follows:

1. `TiDB-Server`, `Parse`, `Compile`, and `Transaction` mirror the SQL-facing panels used in the read dashboard, showing request latency, token latency, connection count, heap memory, parse/compile latency, transaction duration, statement count, and retry count.
2. `KV` switches the TiDB client focus to write commits by querying `tidb_tikvclient_txn_cmd_duration_seconds_bucket` with `type=~"commit"`. It also includes lock resolver and backoff panels.
3. `PD Client` shows TSO wait and RPC duration quantiles for timestamp acquisition pressure.
4. `gRPC` focuses on write request traffic with `tikv_grpc_msg_duration_seconds_bucket` filtered to `kv_prewrite|kv_commit`, plus top-5 gRPC thread CPU via `topk(5, sum(rate(...)) by (instance, name))`.
5. `Scheduler` tracks latch wait quantiles, scheduler worker CPU, and 99th percentile scheduler command duration by command type.
6. `raftstore` shows proposal wait latency by instance, raftstore CPU, and storage async write duration using 99th, 95th, and average targets.
7. `RocksDB-Raft` shows append-log 99th percentile latency by instance and raft DB write microsecond summaries.
8. `RocksDB-KV` shows apply wait latency, apply log duration, KV DB write microsecond summaries, and async apply CPU.
9. `Disk` shows node-level write latency, operations, bandwidth, and write time/load.

Histogram panels generally use `histogram_quantile()` over `sum(rate(..._bucket[1m])) by (le, ...)` for near-real-time views. Some scheduler and storage async write panels use `[5m]` windows for smoother write-path signals, especially latch waits and storage engine async write duration. Average latency panels divide rate of `_sum` by rate of `_count`.

## State and Persistence Behavior

The dashboard's state is persisted entirely as JSON: UID, title, schema version, row collapse state, panel IDs, graph options, default time range, 5-second refresh, time picker options, and variables. There is no local runtime state beyond what Grafana stores after import.

All top-level rows are collapsed in source. This keeps the initial view compact and limits initial query load, but it requires users or validation automation to expand rows to exercise the write-path queries.

The dashboard has built-in dashboard annotations enabled through the datasource, but it contains no custom dashboard links and no panel alert definitions. Template variable current values are `null`, so Grafana must evaluate label queries after import.

## Dependencies and Integration Points

The dashboard depends on Grafana's legacy graph panel, a Prometheus datasource, TiDB/TiKV/PD client metrics, TiKV scheduler and raftstore metrics, Go runtime metrics, and node exporter disk write metrics. The write dashboard has more TiKV-internal dependencies than the read dashboard because it covers scheduler, raftstore, raft RocksDB, KV RocksDB, and apply workers.

Integration points include:

- Grafana provisioning or import that maps `DS_TEST-CLUSTER` to an actual Prometheus datasource.
- TiDB/TiKV monitoring deployments that expose all referenced metric families with `k8s_cluster` and `tidb_cluster` labels.
- Prometheus scrape configuration for node exporter disk write metrics with matching cluster labels.
- Tooling that recursively walks row panels; non-recursive `.panels[]` consumers will only see the 12 collapsed row headers and miss the 34 graph panels.
- Performance-test workflows that rely on a 5-second auto-refresh and a 1-hour default time window for active write benchmarks.

## Risks and Edge Cases

The dashboard is tied to Grafana `6.1.6` and the legacy graph panel. Modern Grafana versions can import it, but panel migration may alter rendering or require compatibility handling.

The 5-second refresh interval can generate significant Prometheus load if many rows are expanded, because the dashboard contains many histogram quantile queries and per-instance groupings. This is especially relevant during write benchmarks where Prometheus and TiKV are already under load.

Template variables are discovered from `tikv_engine_block_cache_size_bytes`, even though the dashboard is write-focused and many panels do not depend on block-cache metrics. Missing block-cache series can break cluster selection for the entire dashboard.

The dashboard assumes consistent `k8s_cluster` and `tidb_cluster` labels across TiDB, TiKV, PD-client, and node-exporter metrics. Node exporter metrics often require explicit relabeling to add TiDB/TiKV cluster labels; if that relabeling is absent, disk panels return empty results.

Some write duration panels use `max(tikv_engine_write_micro_seconds{...})` without grouping by instance. This is useful for worst-case visibility but can obscure which instance contributed the value.

The gRPC CPU panel uses `topk(5, ...)`, which intentionally hides lower CPU consumers. That is good for dashboard readability but can miss broad low-level CPU growth across many threads.

Several average panels divide rates of `_sum` by `_count`; if the count rate is zero for a selected window, Prometheus can return empty or non-finite results. This is most likely during idle periods or narrow test windows.

## Test Signals and Validation

Useful static checks:

- `jq` should parse the file and confirm dashboard title `Test-Cluster-Performance-Write`, UID `Fcw5wqcWk`, schema version `18`, and `refresh` value `5s`.
- Recursive traversal should find 12 collapsed row panels and 34 graph panels with targets.
- All graph panels should use datasource `${DS_TEST-CLUSTER}`.
- Template variables should be exactly `k8s_cluster` and `tidb_cluster`.
- PromQL linting should validate metric names and labels against a representative TiDB/TiKV Prometheus, with special attention to scheduler, raftstore, and node disk metrics.

Runtime validation should import the dashboard into Grafana with a real TiDB/TiKV Prometheus datasource, run or replay a write-heavy workload, select a known test cluster, expand every row, and verify data for commit latency, prewrite/commit gRPC duration, scheduler latch waits, raft proposal/apply latency, RocksDB raft and KV write duration, async apply CPU, and node write disk I/O. Because the dashboard auto-refreshes every 5 seconds, validation should also watch Prometheus query latency and dashboard responsiveness when multiple rows are expanded.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/performance_write.json -->
