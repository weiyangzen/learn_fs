# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 68614-76906

## Scope

This chunk is a middle slice of TiKV's `tikv_details.json` Grafana dashboard. It starts inside the collapsed `Resolved TS` row, includes the complete collapsed `Point In Time Restore` and `Backup & Import` rows, and ends inside the next collapsed row after the `Total Flushed Size (Last 30m)` log-backup stat panel begins. The file is JSON dashboard configuration rather than executable code, so the important "APIs" are Grafana panel schema fields and Prometheus query expressions that bind TiKV metrics to dashboard views.

## Purpose

- Define operational dashboard panels for TiKV resolved-ts health, PITR/import/backup workloads, external storage setup, checksum/analyze coprocessor work, disk IO, cloud requests, and the first log-backup status/flush panels.
- Provide Prometheus expressions scoped by Grafana variables: `${DS_TEST-CLUSTER}`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$optional_quantile`, and `$additional_groupby`.
- Use collapsed row panels to group related troubleshooting surfaces without making all charts visible by default.
- Standardize graph, heatmap, and stat panels with repeated legend behavior, `null as zero` graph handling, heatmap buckets, and units such as seconds, bytes, bytes/sec, operations/sec, counts/sec, and percent units.

## Important Panels And Query Interfaces

- `Resolved TS` tail panels:
  - `Max gap of resolved-ts in region leaders` uses `tikv_resolved_ts_min_leader_resolved_ts_gap_millis` grouped by `instance`.
  - `Min Leader Resolved TS Region` exposes `tikv_resolved_ts_min_leader_resolved_ts_region`.
  - `Check leader duration` heatmaps `tikv_resolved_ts_check_leader_duration_seconds_bucket`.
  - `CheckLeader request region count` and `CheckLeader request size` calculate `histogram_quantile($optional_quantile, ...)` over check-leader item-count and request-size buckets.
  - `Fail advance ts count` combines `tikv_resolved_ts_fail_advance_count` by `instance, reason` with `tikv_raftstore_check_stale_peer`.
  - `Lock heap size`, `Observe region status`, and `Pending command size` use `tikv_resolved_ts_lock_heap_bytes`, `tikv_resolved_ts_region_resolve_status`, and `tikv_resolved_ts_channel_pending_cmd_bytes_total`.
- `Point In Time Restore` row panels:
  - Import CPU/thread pressure is shown via `tikv_thread_cpu_seconds_total{name=~"sst_.*"}` and `count(rate(...))`.
  - Import RPC latency/ops/count panels use `tikv_import_rpc_duration_bucket`, `_sum`, `_count`, and `tikv_import_rpc_count`, split by request and optional grouping.
  - Apply and engine stages use `tikv_import_apply_duration_bucket`, `tikv_import_engine_request_bucket`, `tikv_import_applier_event`, `tikv_import_apply_bytes_*`, and `tikv_import_apply_cached_bytes`.
  - Memory visibility includes `tikv_server_mem_trace_sum{name=~"raftstore-.*"}`.
- `Backup & Import` row panels:
  - Backup CPU and thread panels use backup worker thread names, `backup_io`, `tikv_backup_softlimit`, and `tikv_backup_thread_pool_size`.
  - Backup error and SST generation panels use `tikv_backup_error_counter`, `tikv_backup_range_size_bytes_bucket`, and `tikv_backup_range_size_bytes_sum`.
  - Backup duration heatmaps and quantile charts use `tikv_backup_range_duration_seconds_bucket`, `_sum`, and `_count` for `snapshot`, `scan`, `save.*`, and all types.
  - External storage creation is represented as both heatmap and percentile/average/count graph over `tikv_external_storage_create_seconds_*`.
  - Checksum/analyze request duration uses `tikv_coprocessor_request_duration_seconds_*{req=~"analyze.*|checksum.*"}`.
  - Disk IO, import CPU/thread/error/RPC/download/read/rewrite/ingest/local-write, raw TTL expiration, and cloud request rate are represented with `node_disk_io_time_seconds_total`, `tikv_import_*`, `tikv_backup_raw_expired_count`, and `tikv_cloud_request_duration_seconds_count`.
- The next row begins with stat panels:
  - `Endpoint Status` maps `tikv_log_backup_enabled` values `0/1` to disabled/enabled text.
  - `Task Status` maps `tikv_log_backup_task_status` values `0/1/2` to running/paused/error text.
  - `Advancer Owner` checks `tidb_log_backup_advancer_owner > 0`.
  - `Average Flush Size`, `Flushed Files (Last 30m) Per Host`, `Flush Times (Last 30m)`, and the beginning of `Total Flushed Size (Last 30m)` use 30-minute `increase` or `delta` windows over `tikv_log_backup_flush_*` metrics.

## Control Flow

Grafana loads this JSON as a dashboard model. Each collapsed row owns a nested `panels` array; when the row is expanded, Grafana evaluates each target expression against the configured Prometheus datasource. Variable interpolation happens before query execution, so cluster and instance filters are injected into every metric selector.

The runtime query pattern is consistent:

- Raw gauges use `sum(...)`, `avg(...)`, or `min(...)` with label grouping.
- Counters use `rate(...)`, `increase(...)`, or `delta(...)` over `$__rate_interval` or fixed `[30m]` windows.
- Histogram charts use either heatmap expressions such as `sum(increase(metric_bucket[$__rate_interval])) by (le)` or quantile expressions using `histogram_quantile(...)` over `sum(rate(metric_bucket[$__rate_interval])) by (..., le)`.
- Stat panels reduce series with `lastNotNull`, while graph panels show time-series legends with current/max values and heatmaps use upper bucket bounds.

## State And Persistence Behavior

This chunk does not persist application data. It persists dashboard configuration: panel IDs, titles, descriptions, row grouping, visual types, units, legends, field mappings, and PromQL expressions. Operational state comes from Prometheus samples emitted by TiKV, TiDB log-backup advancer metrics, and node exporter disk metrics.

The queries themselves imply state semantics:

- Gauge-style metrics such as resolved-ts gap, lock heap bytes, pending command bytes, cached import bytes, backup thread pool size, log-backup enabled/task status, and advancer ownership report current sampled state.
- Counter and histogram metrics are transformed into rates, deltas, increases, quantiles, and heatmap buckets, so restarts and counter resets can affect short-window panels.
- The log-backup stat panels intentionally use fixed `[30m]` windows, while most other panels use Grafana's `$__rate_interval`.
- Several descriptions warn that cumulative flushed sizes or counts may decrease when TiKV nodes reboot; the panel expressions use `delta` over 30 minutes to make recent activity visible despite that reset risk.

## Dependencies And Integration Points

- Grafana dashboard schema: `row`, `graph`, `heatmap`, and `stat` panel types; `fieldConfig`, `options`, `legend`, `tooltip`, `gridPos`, and axis/unit fields.
- Prometheus datasource `${DS_TEST-CLUSTER}` and Grafana variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$optional_quantile`, `$additional_groupby`, and `$__rate_interval`.
- TiKV metrics families for resolved-ts, import/PITR, backup, external storage, raw backup TTL, cloud requests, log backup flushes, and server memory tracing.
- TiDB metric `tidb_log_backup_advancer_owner` for advancer ownership, integrated into a TiKV dashboard row.
- Node exporter `node_disk_io_time_seconds_total` for IO utilization correlation during backup/import workloads.
- Visual consumers include on-call debugging, performance analysis, backup/import throughput tracking, and regression detection during TiKV, BR, PITR, or log-backup operations.

## Risks And Edge Cases

- The chunk starts and ends mid-row. Any chunk-local parser must preserve context from neighboring chunks; final dashboard interpretation requires merge/reconciliation with adjacent line ranges.
- Some expressions compare or combine different semantic units in one panel. For example `CheckLeader request size` overlays bytes and item count, and backup CPU overlays CPU utilization with `tikv_backup_softlimit`; legends are required to avoid misreading axes.
- `delta(...)` on counters or reset-prone cumulative values can go negative around process restarts. Some stat panels also use boolean comparisons such as `> 0`, so they show activity presence rather than exact counts.
- Histogram quantiles depend on complete bucket series and correct `le` grouping. Dropped buckets or inconsistent labels will produce misleading quantiles or blank heatmaps.
- Several panels group by `$additional_groupby`. If that variable is empty, malformed, or too high-cardinality, the dashboard can either fail queries or generate excessive series.
- `null as zero` can hide scrape gaps by rendering missing data as zero, especially risky for error counters and status panels.
- The PromQL selectors consistently filter `k8s_cluster`, `tidb_cluster`, and `instance`, but `tidb_log_backup_advancer_owner > 0` does not include those filters in this chunk; depending on datasource scope, it may show advancer owners outside the selected TiKV instance filter.
- The `Import Ingest SST Bytes` heatmap uses `tikv_import_ingest_byte_bucket` but formats the Y axis as seconds in this chunk, which appears inconsistent with the title and metric name.
- The external storage and checksum panels hard-code high percentiles (`0.9999`, `0.99`) alongside average/count series. Sparse workloads can make those percentile lines noisy.
- Stat value mappings use fixed numeric meanings for log-backup enabled/task status. Producer-side enum changes would silently mislabel state unless the dashboard is updated.

## Test Signals

- JSON/dashboard validation should confirm this line range remains syntactically valid when merged with adjacent chunks and that panel IDs `486` through `554` stay unique in the full dashboard.
- PromQL validation should parse every `expr` and `query` field, including expressions with `$optional_quantile` and `$additional_groupby` after variable substitution.
- Dashboard smoke tests should expand `Resolved TS`, `Point In Time Restore`, `Backup & Import`, and the following log-backup row to verify all graph, heatmap, and stat panels render against a representative Prometheus datasource.
- Metric coverage tests should check that TiKV still exports every referenced metric family: `tikv_resolved_ts_*`, `tikv_check_leader_*`, `tikv_import_*`, `tikv_backup_*`, `tikv_external_storage_create_seconds_*`, `tikv_coprocessor_request_duration_seconds_*`, `tikv_cloud_request_duration_seconds_count`, and `tikv_log_backup_*`.
- Unit/axis review should specifically verify `tikv_import_ingest_byte_bucket` formatting and mixed-unit panels.
- Restart/reset scenarios should be tested for panels using `delta` and `increase`, especially backup/log-backup flush counts and sizes.
- Variable tests should exercise empty and non-empty `$additional_groupby`, multiple `$instance` matches, and common `$optional_quantile` values.
