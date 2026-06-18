# Research: subset-b-008918

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/tikv_fast_tune.json -->
# sources/storage-engines/tikv/metrics/grafana/tikv_fast_tune.json

## Purpose

`tikv_fast_tune.json` is a Grafana dashboard export named `Test-Cluster-TiKV-FastTune` with UID `TiKVFastTune`. It is a TiKV operational tuning and incident-triage dashboard focused on quickly identifying whether TiDB-visible write or read latency is caused by TiKV RPC imbalance, scheduler queues, raftstore/apply waiting, RocksDB write/read behavior, compaction backlog, PD scheduling activity, CPU jitter, or coprocessor pressure. The default time range is the last six hours, refreshes every five minutes, and uses browser timezone with Grafana dark styling.

The dashboard is organized as a sequence of row separators and graph panels. The first row, `Summary`, correlates write/read RPC rates and latency with write stalls, pending compaction bytes, PD scheduling, CPU, and other high-level causes. The `TiKV-Write affected TiDB-Write ?` row drills into write-path bottlenecks. The `TiKV-Read affected TiDB-Write ?` row covers read/coprocessor pressure that can interfere with write latency by consuming shared TiKV and RocksDB resources.

## Important APIs, Types, and Functions

This file has no executable functions, but it depends on Grafana's JSON dashboard schema and Prometheus query API:

- Dashboard schema fields include `__inputs`, `__requires`, `annotations`, `templating`, `panels`, `time`, `timepicker`, `refresh`, `uid`, and `version`.
- The datasource input is `DS_TEST-CLUSTER`, a Prometheus datasource reference substituted as `${DS_TEST-CLUSTER}` throughout templating and panel targets.
- The required Grafana components are Grafana `6.0.1`, Graph panel `5.0.0`, and Prometheus datasource `5.0.0`; the dashboard schema version is `18`.
- Template variables are hidden `k8s_cluster` and `tidb_cluster` selectors plus a visible multi-select `instance` selector. `instance` uses `includeAll` with `allValue: ".*"`, making it suitable for regex label filters.
- Panel targets use PromQL functions such as `rate`, `irate`, `delta`, `avg_over_time`, `sum`, `avg`, `max`, and `histogram_quantile` over one-minute windows.
- Graph panel behavior is mostly time-series driven, with legend formats such as `{{instance}}-write`, `write-rpc`, `duration-999%`, `pending-bytes-kv`, `rocksdb-cpu-{{instance}}`, and `{{type}}-max`.

The dashboard reads metrics from these major metric families: `tikv_grpc_msg_duration_seconds_*`, `tikv_engine_write_stall`, `tikv_engine_pending_compaction_bytes`, `pd_schedule_operators_count`, `pd_scheduler_store_status`, `tikv_worker_pending_task_total`, `node_cpu_seconds_total`, `tikv_futurepool_pending_task_total`, `tikv_raftstore_request_wait_time_duration_secs_bucket`, `tikv_raftstore_apply_wait_time_duration_secs_bucket`, `tikv_engine_write_micro_seconds`, `tikv_engine_flow_bytes`, `tikv_engine_compaction_flow_bytes`, `tikv_thread_cpu_seconds_total`, `tikv_engine_bytes_per_write`, `tikv_raftstore_store_perf_context_time_duration_secs_bucket`, `tikv_raftstore_apply_perf_context_time_duration_secs_bucket`, `tikv_engine_wal_file_sync_micro_seconds`, `tikv_coprocessor_request_*`, `tikv_coprocessor_scan_details`, `tikv_engine_get_micro_seconds`, `tikv_coprocessor_rocksdb_perf`, `tikv_engine_sst_read_micros`, `tikv_raftstore_proposal_total`, `tikv_engine_cache_efficiency`, `tikv_engine_locate`, `tikv_engine_seek_micro_seconds`, and `tikv_engine_get_served`.

## Control Flow

Grafana loads the dashboard, asks the configured Prometheus datasource to resolve template variables, then renders the graph panels using the selected label values. The variable flow is hierarchical: `k8s_cluster` is discovered from `tikv_engine_block_cache_size_bytes`, `tidb_cluster` is filtered by the selected Kubernetes cluster, and `instance` is filtered by both cluster labels through `tikv_engine_size_bytes`. Every panel query then injects these variables as `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, and usually `instance=~"$instance"`.

At render time, the dashboard compares baseline traffic with suspected causes. Many panels include `write-rpc` as a reference series using `tikv_grpc_msg_duration_seconds_count` for `kv_prewrite`, `kv_commit`, and `kv_pessimistic_lock`. The summary row first checks imbalance and RPC latency across write, get/batch-get/scan, and coprocessor calls. It then checks write stalls, compaction pending bytes, PD scheduling operators, PD pending tasks, region balancing reasons, and CPU jitter. The write-impact row moves down the pipeline through scheduler future-pool queues, scheduler wait histograms, raftstore and apply wait histograms, RaftDB/KVDB write latency, compaction/frontend IO flows, RocksDB thread CPU, write batch sizes, mutex/write-thread wait, and RaftDB WAL sync latency. The read-impact row covers coprocessor QPS and handling latency, coprocessor wait queues, scan amplification, KVDB get/seek/SST/cache behavior, delete-skipped counts, and read-index/local-read fallback to raftstore.

The dashboard has 54 top-level panel entries, including three row separators and 51 graph panels, with 142 Prometheus target expressions. Rows are not collapsed, so all panels are visible in the exported layout.

## State and Persistence Behavior

The only persistent state in this source file is dashboard configuration. It does not store metric values, alerts, or user data. Grafana persists dashboard identity through `uid: "TiKVFastTune"`, `version: 7`, `iteration: 1606814402924`, and `editable: true`; `id` and `gnetId` are `null`, which makes the export portable across Grafana instances. Timepicker options and refresh intervals are embedded in the file, while actual time-series state remains in Prometheus.

Runtime state is provided by Grafana URL/template variable selections. The visible `instance` variable supports multi-select and all-instances regex selection; hidden `k8s_cluster` and `tidb_cluster` variables are still required for the datasource queries. Because all panels use short one-minute PromQL ranges, the dashboard emphasizes recent spikes and jitter rather than long-term smoothing.

## Dependencies and Integration Points

The dashboard integrates with a TiKV/TiDB deployment whose Prometheus labels include `k8s_cluster`, `tidb_cluster`, `instance`, and metric-specific labels such as `type`, `db`, `req`, `cf`, `name`, `store`, `event`, `mode`, and `metric`. It also integrates with PD metrics for scheduling-operator and store-capacity context, and node exporter CPU metrics through `node_cpu_seconds_total`.

Operationally, this dashboard is a companion to TiDB/TiKV incident response. It assumes Prometheus scrapes TiKV, PD, and node metrics with consistent cluster labels. It also assumes TiKV exposes legacy metric names used by the dashboard, including RocksDB-engine percentile gauge families such as `tikv_engine_write_micro_seconds`, `tikv_engine_seek_micro_seconds`, and `tikv_engine_sst_read_micros`.

## Risks and Edge Cases

- Metric-name drift is the primary maintenance risk. If TiKV renames or removes legacy metric families, panels silently show no data.
- Some query filters are hard-coded to specific operation labels, for example write RPCs as `kv_prewrite|kv_commit|kv_pessimistic_lock` and read RPCs as `kv_get|kv_scan|kv_batch_get|kv_batch_get_command|coprocessor`. New RPC names will be absent until the regexes are updated.
- Many queries aggregate across instances with `sum` or `avg`, which is useful for cluster-level diagnosis but can hide one bad instance unless paired with the per-instance panels.
- Histogram quantiles are computed after summing buckets. This is appropriate for aggregate latency, but it differs from taking per-instance quantiles and can obscure skew.
- Several panels correlate write RPCs with non-write causes; correlation is visual rather than causal. Operators still need to confirm causality with logs, deployment events, and workload changes.
- Panel titles contain question marks and one note that scheduler wait duration is incorrectly included. Those labels are useful for triage but should not be treated as formal alert definitions.
- Short one-minute `rate` windows make the dashboard sensitive to scrape gaps and low-volume workloads.

## Test Signals

Validation should start with JSON parsing and Grafana import. A useful static check is `jq` parsing plus a traversal that counts panels and target expressions, verifies every PromQL target has a datasource, and confirms the three template variables resolve against Prometheus. Runtime validation should open the dashboard against a representative TiKV cluster and verify that high-level Summary panels, write-path panels, and read/coprocessor panels all return data.

Prometheus query checks should cover representative expressions for RPC histograms, RocksDB gauges, future-pool queues, raftstore/apply wait buckets, PD schedule operator counts, node CPU, and coprocessor metrics. For regression testing, compare panel counts, target counts, UID, required datasource input, and variable names after any dashboard edit.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/tikv_fast_tune.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/tikv_raw.json -->
# sources/storage-engines/tikv/metrics/grafana/tikv_raw.json

## Purpose

`tikv_raw.json` is a Grafana dashboard export named `Test-Cluster-TiKV-Raw` with UID `K0D2tEZZz`. It focuses on TiKV raw read commands and causal timestamp provider behavior. The dashboard is intentionally narrower than the fast-tune board: it helps operators inspect latency for raw read command classes and diagnose TSO/causal timestamp request volume, renewal latency, batch-list behavior, and current batch size.

The default time range is the last five minutes and `refresh` is disabled in the export. The dashboard uses Grafana dark style, schema version `16`, and has two collapsed top-level rows: `Read - $command` and `Causal timestamp`. Those collapsed rows contain all graph panels, so a viewer must expand them to see the charts.

## Important APIs, Types, and Functions

This file is dashboard configuration rather than executable code, but its operational interface is the combination of Grafana dashboard schema, template variables, and PromQL:

- Dashboard fields include `__inputs`, `__requires`, `annotations`, `templating`, `panels`, `time`, `timepicker`, `refresh`, `uid`, and `version`.
- The datasource input is `DS_TEST-CLUSTER`, labeled `test-cluster`, with Prometheus plugin metadata.
- Required components are Grafana `5.4.3`, Graph panel `5.0.0`, and Prometheus datasource `5.0.0`.
- Template variables include hidden `k8s_cluster` and `tidb_cluster`, visible multi-select `command`, and visible multi-select `instance`.
- The `command` variable is populated from `tikv_storage_command_total` and regex-filtered to `raw_get|raw_scan|raw_batch_get|raw_batch_scan`.
- The `instance` variable is populated from `tikv_engine_size_bytes` for the selected cluster labels.
- PromQL target expressions use `rate`, `sum`, and `histogram_quantile` over one-minute windows.

The dashboard reads scheduler command and read-processing histograms for raw commands: `tikv_scheduler_command_duration_seconds_bucket`, `_sum`, `_count`, and `tikv_scheduler_processing_read_duration_seconds_bucket`, `_sum`, `_count`. It also reads causal timestamp provider metrics: `tikv_causal_ts_provider_get_ts_duration_seconds_bucket/count`, `tikv_causal_ts_provider_tso_batch_renew_duration_seconds_bucket/count`, `tikv_causal_ts_provider_tso_batch_list_counting_bucket/count`, and `tikv_causal_ts_provider_tso_batch_size`.

## Control Flow

Grafana first resolves the hidden cluster selectors from Prometheus. `k8s_cluster` is discovered from `tikv_engine_block_cache_size_bytes`; `tidb_cluster` is discovered from the same metric family constrained by the selected Kubernetes cluster. The visible `command` selector is then built from `tikv_storage_command_total` and restricted to raw read commands. The visible `instance` selector is built from `tikv_engine_size_bytes` for the chosen cluster.

When the `Read - $command` row is expanded, the dashboard renders `Command Duration` and `Read Processing Duration`. Each panel shows P99, P95, and average latency for the selected raw command regex and selected instances. The P99/P95 series are derived from histogram buckets, while average latency divides one-minute `_sum` rate by one-minute `_count` rate.

When the `Causal timestamp` row is expanded, the dashboard renders causal timestamp request rate by result, P99/P999/MAX get-ts duration by result, TSO batch renew request rate by result and reason, P99 renew duration by result and reason, P99/P50 TSO batch-list counting by type, batch-list counting frequency by type, and current summed TSO batch size.

The source contains two top-level row panels, nine graph panels nested under those rows, and sixteen Prometheus target expressions.

## State and Persistence Behavior

The file persists dashboard structure and identity, not metric data. The export has `uid: "K0D2tEZZz"`, `version: 1`, `iteration: 1560225374091`, `editable: true`, `id: null`, and `gnetId: null`. Both top-level rows have `collapsed: true`, so the nested panels are stored under each row's `panels` field rather than as visible top-level graph panels. Runtime state comes from Grafana variable selections and the active time range.

Because the default time range is only five minutes and every rate uses a one-minute window, the dashboard is optimized for immediate inspection. It is less useful for long-term trend analysis unless the viewer manually expands the range and verifies that the one-minute rates remain appropriate.

## Dependencies and Integration Points

This dashboard depends on a Prometheus datasource scraping TiKV metrics with consistent `k8s_cluster`, `tidb_cluster`, `instance`, `type`, `result`, and `reason` labels. It integrates specifically with TiKV raw key-value APIs exposed through scheduler command metrics and with the causal timestamp provider metrics exposed by TiKV.

The dashboard can be used beside broader TiKV and PD dashboards. It narrows investigation to raw command latency and timestamp provider activity, which is useful when raw KV workloads or causal timestamp delays are suspected rather than transaction, raftstore, or coprocessor behavior.

## Risks and Edge Cases

- The row panels are collapsed in the export. Users may think the dashboard is empty unless they expand `Read - $command` or `Causal timestamp`.
- `refresh: false` means the dashboard will not auto-refresh unless the user changes the Grafana setting after import.
- The `command` variable regex only includes four raw read command labels. New raw command labels or write-oriented raw commands will be excluded.
- Average latency queries divide `_sum` rate by `_count` rate. If the selected command has no traffic, the expression can return no series or Prometheus special values depending on the datasource behavior.
- Histogram quantiles are aggregated across selected instances, which gives a cluster-level view but can hide per-instance skew.
- The dashboard assumes causal timestamp metric families are present. TiKV builds or versions without these metrics will leave the causal timestamp row empty.
- Short one-minute windows are sensitive to scrape interval, scrape failures, and low traffic.

## Test Signals

Static validation should parse the JSON, verify the two row panels and nine nested graph panels, and check that all sixteen PromQL targets reference `${DS_TEST-CLUSTER}` either directly or through inherited panel configuration. Variable tests should confirm `k8s_cluster`, `tidb_cluster`, `command`, and `instance` all resolve in Prometheus, and that `command` only returns the intended raw command labels.

Runtime validation should expand both rows in Grafana, select a known TiKV instance and raw command, and verify non-empty scheduler command duration, read processing duration, get-ts request, TSO renewal, batch-list counting, and batch-size panels. A regression check should preserve the dashboard UID, variable names, collapsed-row nesting, and the sixteen target expressions unless an intentional dashboard migration changes them.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/metrics/grafana/tikv_raw.json -->
