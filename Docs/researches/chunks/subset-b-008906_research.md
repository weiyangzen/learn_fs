# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 1-8022

## Scope

This chunk covers the opening 8,022 lines of the TiKV detailed Grafana dashboard JSON. It starts with dashboard-level metadata and the Prometheus datasource input `DS_TEST-CLUSTER`, then defines the `Duration`, `Cluster`, `Errors`, and `Server` row panels through the beginning of the final `gRPC resource group QPS` panel. The slice ends mid-object at the `xaxis.name` field for that panel, so the full JSON document continues in later chunks.

The content is declarative dashboard configuration rather than executable TiKV code. Its effective behavior is the set of Grafana panels, legends, axes, thresholds, and Prometheus expressions used to observe TiKV write/read latency, cluster resources, error signals, storage/raft internals, scheduler/thread-pool behavior, RocksDB perf counters, and gRPC server traffic.

## Purpose

- Provide the first major monitoring surface for TiKV details in Grafana, backed by a Prometheus datasource selected through `${DS_TEST-CLUSTER}`.
- Organize TiKV health into collapsed Grafana rows: `Duration`, `Cluster`, `Errors`, and `Server`.
- Expose latency distributions with `histogram_quantile()` over Prometheus histogram buckets and expose average values with `rate(_sum) / rate(_count)`.
- Track per-instance capacity, CPU, memory, disk utilization, RocksDB flow, QPS, error rates, leader/region counts, and uptime.
- Surface failure and saturation conditions such as critical errors, scheduler busy, channel full, coprocessor full, write stall, raftstore process busy, report-failure messages, leader missing, damaged RocksDB files, and raft append rejects.
- Break down server-side request paths by gRPC type, priority, source, resource group, batch sizes, batch wait latency, and raft message batch size.

## Important Dashboard Objects And Queries

- Dashboard metadata declares one Prometheus input named `DS_TEST-CLUSTER` and uses old-style Grafana graph panels with `renderer: "flot"`, `type: "graph"`, `type: "row"`, `gridPos`, `legend`, `tooltip`, `xaxis`, and `yaxes` fields.
- The `Duration` row contains:
  - `Write Pipeline Duration`, a stacked bar graph with quantiles for `tikv_raftstore_append_log_duration_seconds_bucket`, `tikv_raftstore_request_wait_time_duration_secs_bucket`, `tikv_raftstore_apply_wait_time_duration_secs_bucket`, `tikv_raftstore_commit_log_duration_seconds_bucket`, and `tikv_raftstore_apply_log_duration_seconds_bucket`.
  - `Cop Read Duration`, a stacked bar graph with `tikv_storage_engine_async_request_duration_seconds_bucket{type="snapshot"}`, `tikv_coprocessor_request_wait_seconds_bucket{type="all"}`, and `tikv_coprocessor_request_handle_seconds_bucket`.
- The `Cluster` row includes store capacity panels from `tikv_store_size_bytes{type="used|available|capacity"}`, CPU from `process_cpu_seconds_total` with hidden `tikv_server_cpu_cores_quota`, memory from `process_resident_memory_bytes` with hidden `tikv_server_memory_quota_bytes`, disk utilization from `node_disk_io_time_seconds_total`, MBps from `tikv_engine_flow_bytes` and `tikv_in_memory_engine_flow`, QPS from `tikv_grpc_msg_duration_seconds_count`, error rate from `tikv_grpc_msg_fail_total`, missing PD heartbeat detection via `tikv_pd_heartbeat_message_total{type="noop"} < 1`, critical errors from `tikv_critical_error_total`, leader/region counts from `tikv_raftstore_region_count`, and uptime from `time() - process_start_time_seconds`.
- The `Errors` row begins with `Critical error`, which adds a Grafana threshold at values greater than zero, then aggregates operational failure signals in `Server is busy`: `tikv_scheduler_too_busy_total`, `tikv_channel_full_total`, `tikv_coprocessor_request_error{type="full"}`, `tikv_engine_write_stall{type="write_stall_percentile99",db=~"$db"}`, `tikv_raftstore_store_write_msg_block_wait_duration_seconds_count`, and `tikv_raftstore_process_busy`.
- Additional `Errors` panels include server report failures through `tikv_server_report_failure_msg_total`, RocksDB/engine size via `tikv_engine_size_bytes`, channel full by type, active written leaders and write distributions from `tikv_region_written_keys_*` and `tikv_region_written_bytes_*`, approximate region size from `tikv_raftstore_region_size_*`, clear-overlap-region duration from `tikv_raftstore_clear_overlap_region_duration_seconds_*`, apply key/value size buckets, hibernated peer state, raftstore memory trace through `tikv_server_mem_trace_sum{name=~"raftstore-.*"}` plus `raft_engine_memory_usage`, raft entry cache evictions through `tikv_raft_entries_evict_bytes`, address-resolution latency through `tikv_server_address_resolve_duration_secs_bucket`, and raft append rejects through `tikv_server_raft_append_rejects`.
- The `Server` row starts at the end of the chunk and covers gRPC/server panels:
  - `gRPC message count`, `gRPC message failed`, quantile `gRPC message duration$optional_quantile`, and `Average gRPC message duration` using `tikv_grpc_msg_duration_seconds_*` and `tikv_grpc_msg_fail_total`, with variants grouped by `type`, `priority`, and `$additional_groupby`.
  - `gRPC batch commands wait duration` from `tikv_grpc_batch_commands_wait_duration_seconds_bucket`.
  - `gRPC batch size` from request/response batch histograms and averages: `tikv_server_grpc_req_batch_size_*`, `tikv_server_grpc_resp_batch_size_*`, and `tikv_server_request_batch_size_*`.
  - `raft message batch size` from `tikv_server_raft_message_batch_size_*`.
  - `gRPC request sources QPS` and `gRPC request sources duration` from `tikv_grpc_request_source_counter_vec` and `tikv_grpc_request_source_duration_vec`.
  - `gRPC resource group QPS` from `tikv_grpc_resource_group_total`; this panel continues past line 8022.

## Control Flow And Data Flow

Grafana loads the dashboard JSON, resolves the `DS_TEST-CLUSTER` input to a Prometheus datasource, and renders each collapsed row when expanded. Each graph panel executes its `targets` against Prometheus using dashboard variables such as `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$db`, `$optional_quantile`, `$additional_groupby`, and Grafana's `$__rate_interval`.

Most panels follow one of four PromQL patterns. Counter and histogram streams use `rate(metric[$__rate_interval])` for per-second behavior. Histogram quantiles wrap `histogram_quantile(q, sum(rate(bucket[$__rate_interval])) by (le, ...))`. Average latencies or sizes divide `sum(rate(metric_sum))` by `sum(rate(metric_count))`. Gauges and current state use direct `sum(metric) by (...)`, `avg(metric) by (...)`, or expressions such as `time() - process_start_time_seconds`.

The row layout is declarative. Parent row panels have `collapsed: true`, `type: "row"`, and nested `panels`. Child panels carry the actual Prometheus targets and presentation settings. Legends commonly sort by max or current value, hide empty and zero series, and render on the right as a table.

## State And Persistence Behavior

This chunk has no runtime state inside TiKV and does not persist user data. It is persisted as repository configuration for Grafana. At deployment/import time it becomes Grafana dashboard state: panel IDs, row collapse state, grid positions, datasource binding, PromQL expressions, units, thresholds, hidden targets, and legend rules.

The dashboard reads TiKV, process, node, and raft-engine metrics from Prometheus. It does not write to TiKV, Prometheus, or Grafana datasources during normal viewing. Its persistence impact is indirect: changing a query, label selector, unit, or threshold changes what operators see and can therefore affect alert triage, capacity decisions, and incident diagnosis.

## Dependencies And Integration Points

- Grafana dashboard import/runtime must support this JSON schema and legacy graph panel options such as `aliasColors`, `bars`, `lines`, `renderer: "flot"`, `seriesOverrides`, `thresholds`, `tooltip`, `xaxis`, and `yaxes`.
- Prometheus is the only datasource declared in this slice. Every target uses `${DS_TEST-CLUSTER}`.
- Query selectors depend on TiDB Operator or deployment labels `k8s_cluster`, `tidb_cluster`, and `instance`. Some panels also depend on `job=~".*tikv"`, `db=~"$db"`, `type`, `priority`, `source`, `name`, `req`, `store_id`, `state`, and `$additional_groupby`.
- TiKV metric integration spans raftstore, storage engine, coprocessor, scheduler, server, gRPC, YATP thread pool, RocksDB perf, memory trace, and in-memory engine metrics.
- Non-TiKV metric integration includes `process_cpu_seconds_total`, `process_resident_memory_bytes`, `process_start_time_seconds`, `node_disk_io_time_seconds_total`, and `raft_engine_memory_usage`.
- Panel units integrate with Grafana formatting: seconds (`s`), bytes (`bytes`), operations (`ops`), percent unit (`percentunit`), and untyped counts (`none`/`short`).

## Risks And Edge Cases

- The assigned chunk ends inside a panel object, so validating only lines 1-8022 as standalone JSON will fail. Validation must use the full `tikv_details.json` or merge all chunks first.
- Several expressions include `$additional_groupby` directly inside `by (...)`. If that variable expands to an empty or malformed value, PromQL can become invalid or produce unexpected grouping.
- Hidden quota series for CPU and memory are present but hidden. Operators may miss quota context unless they intentionally enable those series or a later dashboard version surfaces them.
- `IO utilization` groups by `instance` but its legend includes `{{device}}`; without grouping by `device`, the legend can show an empty or misleading device label.
- Error panels often use `null as zero` and `hideZero`. That keeps dashboards quiet, but it can hide missing series, scrape gaps, or label mismatches unless Prometheus/Grafana missing-data behavior is tested separately.
- Critical-error thresholding is present on the `Critical error` panel, but most other error/saturation panels are visual only in this chunk. Operational alerting must exist elsewhere if non-zero values should page.
- Histogram quantiles depend on correct `_bucket` series and complete `le` labels. Dropped buckets, aggregation across incompatible label sets, or low traffic can make quantiles noisy.
- Average expressions divide `_sum` rates by `_count` rates without explicit zero guards. For sparse traffic windows, panels can show `NaN`, `Inf`, or disappear depending on Prometheus/Grafana behavior.
- Regex filters such as `job=~".*tikv"` and `db=~"$db"` can over-match if label conventions drift.
- The chunk mixes TiKV metrics with process/node metrics; dashboard correctness depends on consistent relabeling so `instance` refers to comparable entities across all jobs.
- Metric renames or label changes in TiKV, raft-engine, or deployment exporters will silently break panels until dashboard tests or visual review catch missing series.

## Test Signals

- Parse the full `tikv_details.json` with a JSON parser and Grafana dashboard linter after all chunks are reconciled; do not parse this chunk alone as JSON.
- Run PromQL syntax checks for every `expr` in this chunk with representative variable expansions for `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$db`, `$optional_quantile`, `$additional_groupby`, and `$__rate_interval`.
- In a TiKV test cluster, verify that each panel returns at least one series when the relevant workload runs: writes for write-pipeline panels, coprocessor reads for read panels, raft traffic for raft panels, and gRPC traffic for server panels.
- Check histogram panels with both high and low traffic to confirm quantiles and average divisions render acceptably when `_count` rates are zero or sparse.
- Verify label grouping and legends, especially `IO utilization`, gRPC priority/type groupings, resource group names, request sources, raftstore memory names, and report-failure `store_id`.
- Confirm the `Critical error` threshold renders when `tikv_critical_error_total` is non-zero and that zero/missing series behavior is understood for panels using `hideZero` and `null as zero`.
- Compare all metric names in this slice against TiKV's exported metrics after a version upgrade, with special attention to older names ending in `_duration_secs_bucket`, vector-style names such as `tikv_grpc_request_source_counter_vec`, and raft-engine memory metrics.
- Import the dashboard into a supported Grafana version and expand the `Duration`, `Cluster`, `Errors`, and `Server` rows to verify panel layout, units, hidden series, and row collapse behavior.
