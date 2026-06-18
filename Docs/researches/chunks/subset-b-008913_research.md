# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 52918-60535

## Scope and Purpose

This chunk is a contiguous slice of the TiKV Details Grafana dashboard JSON. It is declarative observability configuration, not executable TiKV code, so the relevant "APIs" are Grafana panel fields, PromQL expressions, dashboard variables, panel IDs, row layout, and the TiKV/TiDB metrics those expressions bind to.

The slice starts near the end of a collapsed Scheduler row, covers complete collapsed rows for Coprocessor Overview, Coprocessor Detail, and Unified Read Pool, then covers most of the beginning of the GC row before ending inside the next panel definition. Its purpose is to visualize read-path and GC behavior: scheduler scan details and scheduler latency for a selected `$command`, coprocessor request latency, request volume, scan-key and RocksDB perf detail, coprocessor memory/semaphore pressure, YATP unified-read-pool scheduling, GC worker throughput/failures/duration, TiDB GC progress/configuration, TiKV auto-GC progress/safepoint, and GC compaction-filter activity.

## Dashboard Structure and Panels

- Scheduler continuation: `Scheduler scan details [lock]`, `[write]`, and `[default]` query `tikv_scheduler_kv_scan_details` by `tag` for each CF with `req="$command"`; `Scheduler command process duration` and `Scheduler command block read duration` use p99.99, p99, average, and hidden count overlays from scheduler histogram families; `Check memory locks duration` is a heatmap over `tikv_storage_check_mem_lock_duration_seconds_bucket`.
- `Coprocessor Overview` row: starts at row id 379 and contains request-duration heatmap and percentile graph, total request rate, request errors, cursor/scan-key operations, RocksDB perf statistics, response bytes, and coprocessor memory quota. These panels use `tikv_coprocessor_request_duration_seconds_*`, `tikv_coprocessor_request_error`, `tikv_coprocessor_scan_keys_*`, `tikv_coprocessor_rocksdb_perf`, `tikv_coprocessor_response_bytes`, and `tikv_coprocessor_memory_quota`.
- `Coprocessor Detail` row: starts at row id 389 and breaks coprocessor work into handle duration, handle duration by store, wait duration, wait duration by store, DAG request/executor counters, table/index scan details with and without CF grouping, memory-lock-check heatmap and percentile graph, semaphore wait heatmap and percentile graph, and current semaphore waiting task count.
- `Unified Read Pool` row: starts at row id 405 and tracks the YATP/unified-read pool using `tikv_multilevel_level_elapsed`, `tikv_multilevel_level0_chance`, `tikv_unified_read_pool_running_tasks`, `tikv_yatp_pool_schedule_wait_duration_bucket`, `tikv_unified_read_pool_thread_count`, `tikv_yatp_task_poll_duration_*`, `tikv_yatp_task_exec_duration_*`, and `tikv_yatp_task_execute_times_*`.
- `GC` row: starts at row id 414 and includes complete panels for GC tasks, GC task duration, TiDB GC seconds, TiDB GC worker actions, ResolveLocks progress, TiKV auto-GC progress, GC speed, TiKV auto-GC safepoint, GC lifetime, GC interval, and GC in compaction filter. The chunk ends after the opening fields of panel id 426, `GC scan write details`, so that panel's targets and behavior are not fully present here.

Most panels use Grafana legacy `graph`, `heatmap`, `stat`, and collapsed `row` schemas. Graph panels generally set a right-side legend table, hide empty/zero series, sort by maximum descending, render with flot, and use `nullPointMode: "null as zero"`. Heatmap panels use `dataFormat: "tsbuckets"`, hide zero buckets, and plot bucket upper bounds on the Y axis. Stat panels use `lastNotNull` reduction for the GC lifetime and interval configuration values.

## Important Query Patterns

- Histogram heatmaps use `sum(increase(<metric>_bucket{...}[$__rate_interval])) by (le)` and `format: "heatmap"`. This appears in scheduler memory-lock checks, coprocessor request duration, coprocessor memory-lock checks, semaphore waiting duration, and unified-read-pool schedule wait.
- Percentile latency graphs use `histogram_quantile(0.9999, ...)` and `histogram_quantile(0.99, ...)` over `sum(rate(<metric>_bucket{...}[$__rate_interval])) by (..., le, $additional_groupby)`. The same panels usually add average overlays as `rate(_sum) / rate(_count)` and hidden count overlays from `_count`.
- Counter/rate panels use `sum(rate(metric{...}[$__rate_interval])) by (...)`, for example request totals, request errors, DAG requests/executors, scheduler scan details, GC task counters, TiDB GC worker actions, GC speed, and GC compaction filter counters.
- Gauge/config panels use direct aggregation without `rate`, such as `sum(tikv_coprocessor_memory_quota)`, `tikv_multilevel_level0_chance`, `avg_over_time` for running task/thread counts, `max(tidb_tikvclient_range_task_stats)`, and `max(tidb_tikvclient_gc_config)`.
- Nearly every query filters by `k8s_cluster="$k8s_cluster"` and `tidb_cluster="$tidb_cluster"`; most TiKV-side panels also filter `instance=~"$instance"`. Scheduler and GC-duration panels additionally depend on `$command`; many panels inject `$additional_groupby` into both `by (...)` clauses and legend templates.

## Metrics Covered

Scheduler metrics:

- `tikv_scheduler_kv_scan_details`
- `tikv_scheduler_processing_read_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_scheduler_block_read_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_storage_check_mem_lock_duration_seconds_bucket`

Coprocessor overview/detail metrics:

- `tikv_coprocessor_request_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_request_error`
- `tikv_coprocessor_scan_keys_bucket`, `_sum`, `_count`
- `tikv_coprocessor_rocksdb_perf`
- `tikv_coprocessor_response_bytes`
- `tikv_coprocessor_memory_quota`
- `tikv_coprocessor_request_handle_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_request_wait_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_dag_request_count`
- `tikv_coprocessor_executor_count`
- `tikv_coprocessor_scan_details`
- `tikv_coprocessor_mem_lock_check_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_semaphore_wait_time_duration_seconds_bucket`, `_sum`, `_count`
- `tikv_coprocessor_waiting_for_semaphore`

Unified read pool metrics:

- `tikv_multilevel_level_elapsed`
- `tikv_multilevel_level0_chance`
- `tikv_unified_read_pool_running_tasks`
- `tikv_yatp_pool_schedule_wait_duration_bucket`
- `tikv_unified_read_pool_thread_count`
- `tikv_yatp_task_poll_duration_bucket`, `_sum`, `_count`
- `tikv_yatp_task_exec_duration_bucket`, `_sum`, `_count`
- `tikv_yatp_task_execute_times_bucket`, `_sum`, `_count`

GC and TiDB/TiKV GC metrics:

- `tikv_gcworker_gc_tasks_vec`
- `tikv_storage_gc_skipped_counter`
- `tikv_gcworker_gc_task_fail_vec`
- `tikv_gc_worker_too_busy`
- `tikv_gcworker_gc_task_duration_vec_bucket`, `_sum`, `_count`
- `tidb_tikvclient_gc_seconds_bucket`
- `tidb_tikvclient_gc_worker_actions_total`
- `tidb_tikvclient_range_task_stats`
- `tikv_gcworker_autogc_processed_regions`
- `tikv_raftstore_region_count`
- `tikv_storage_mvcc_gc_delete_versions_sum`
- `tikv_gcworker_autogc_safe_point`
- `tidb_tikvclient_gc_config`
- `tikv_gc_compaction_filtered`
- `tikv_gc_compaction_filter_skip`
- `tikv_gc_compaction_mvcc_rollback`
- `tikv_gc_compaction_filter_orphan_versions`
- `tikv_gc_compaction_filter_perform`
- `tikv_gc_compaction_failure`
- `tikv_gc_compaction_filter_mvcc_deletion_met`
- `tikv_gc_compaction_filter_mvcc_deletion_handled`
- `tikv_gc_compaction_filter_mvcc_deletion_wasted`

## Control Flow and Observability Model

Grafana evaluates this JSON by row and panel. Collapsed rows keep their child panel definitions inside a row-level `panels` array; expanding a row causes the child panel targets to run against `${DS_TEST-CLUSTER}` with the current dashboard variable substitutions.

The implicit diagnostic flow is:

1. Scheduler panels show how the selected scheduler `$command` interacts with RocksDB CF scans, command processing latency, block-read latency, and memory-lock checks.
2. Coprocessor overview panels provide a broad read-path view: request duration distribution, request throughput, errors, scan-key/cursor volume, RocksDB internal delete-skip perf statistics, response size, and memory quota.
3. Coprocessor detail panels separate service time from queue/wait time. They distinguish total handle duration, per-store handle duration, request wait duration, per-store wait duration, DAG request/executor mix, table/index scan operations, memory-lock-check latency, semaphore wait latency, and currently waiting semaphore tasks.
4. Unified read pool panels correlate coprocessor/read workload with YATP scheduling: level elapsed time, level-0 scheduling chance for small tasks, running tasks, schedule wait heatmap, running threads, time-slice duration, total task execution duration, and number of scheduling slices per task.
5. GC panels move from worker throughput and duration to TiDB GC orchestration, ResolveLocks progress, TiKV auto-GC progress, safe point/configuration, GC speed, and compaction-filter behavior.

This chunk intentionally combines distribution panels with attribution panels. Heatmaps show bucket shape over time, while graph panels preserve `instance`, `req`, `task`, `type`, `key_mode`, `cf`, `tag`, `priority`, or `$additional_groupby` labels for drilldown.

## State and Persistence Behavior

The JSON persists Grafana dashboard state only: panel IDs, row collapse state, grid coordinates, datasource references, query strings, legend/axis/tooltip behavior, stat reductions, and variable placeholders. It does not persist TiKV state or mutate Prometheus data.

The observed runtime state is external and time-series based. Scheduler, coprocessor, unified-read-pool, and GC components emit metrics; Prometheus scrapes them; Grafana queries them with `rate`, `increase`, `avg_over_time`, and direct aggregation. Counter semantics and scrape continuity matter because most rate panels assume monotonic counters, while histogram panels assume complete `_bucket`, `_sum`, and `_count` families with stable bucket labels.

Persistence-related behavior is visible through GC and MVCC panels rather than through local storage writes in this JSON. `tikv_storage_mvcc_gc_delete_versions_sum`, GC compaction filter counters, `tikv_gcworker_autogc_safe_point`, `tidb_tikvclient_gc_config`, and TiDB GC worker metrics expose how MVCC versions are retained or removed and how GC safe-point/configuration state affects storage cleanup. The chunk also shows `tikv_raftstore_region_count` used as the denominator for TiKV auto-GC progress, tying GC progress to persisted region inventory.

## Dependencies and Integration Points

- Grafana legacy dashboard schema: collapsed `row` panels, `graph`, `heatmap`, `stat`, `targets`, `seriesOverrides`, `fieldConfig`, `gridPos`, legends, axes, and tooltips.
- Prometheus datasource variable `${DS_TEST-CLUSTER}` and Grafana interval variable `$__rate_interval`.
- Dashboard variables: `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$command`, and `$additional_groupby`.
- TiKV metrics exporters for scheduler, storage lock checks, coprocessor, YATP/unified read pool, raftstore region counts, GC worker, MVCC GC, and GC compaction filter metrics.
- TiDB metrics exporters for `tidb_tikvclient_gc_seconds_bucket`, `tidb_tikvclient_gc_worker_actions_total`, `tidb_tikvclient_range_task_stats`, and `tidb_tikvclient_gc_config`.
- Operational integration with TiKV/TiDB troubleshooting: read latency, read queuing, coprocessor executor mix, memory lock contention, semaphore throttling, thread-pool saturation, GC worker saturation, GC safe-point drift, and compaction-filter health.

## Risks and Edge Cases

- `$additional_groupby` is inserted directly into `by (...)` clauses. Empty, malformed, or comma-prefixed substitutions can break PromQL or silently alter aggregation semantics.
- Several high-cardinality dimensions can be combined: `instance`, `req`, `tag`, `cf`, `type`, `task`, `key_mode`, `priority`, and `$additional_groupby`. Histogram quantiles over these labels, especially p99.99, can be expensive on large clusters.
- Many graph panels use `nullPointMode: "null as zero"`. Missing scrapes or missing label series can look like real zeros.
- Average expressions divide `_sum` rates by `_count` rates. If the denominator is zero or absent, panels can show gaps, infinities, or misleading drops depending on Grafana/Prometheus behavior.
- The scheduler and GC-duration panels use `$command`, but the row titles around this chunk are mixed: scheduler panels are under `Scheduler - $command`, while the GC task duration panel also filters `type="$command"`. Variable values that make sense for scheduler commands may not make sense for GC task types.
- The `TiDB GC seconds` panel uses `histogram_quantile(1, ...)`, which estimates the upper histogram bucket boundary rather than an exact maximum duration.
- `TiKV Auto GC SafePoint` divides `tikv_gcworker_autogc_safe_point` by `2^18` and formats it as `dateTimeAsIso`; this assumes the metric encodes a TiDB/TiKV timestamp whose physical time is recovered by that conversion.
- `TiKV Auto GC Progress` divides auto-GC processed regions by raftstore region count per instance. If the numerator and denominator are scraped at different moments or labels differ, progress can spike or be absent.
- The chunk ends at line 60535 inside panel id 426, `GC scan write details`; the targets and final rendering options for that panel must be recovered from the next chunk before a complete per-file report is assembled.

## Test Signals

Because this is dashboard JSON, validation should focus on configuration and query behavior:

- Parse the full `tikv_details.json` as JSON after any edit to ensure row nesting and comma boundaries remain valid.
- Import or provision the dashboard in Grafana to catch duplicate panel IDs, invalid legacy graph/heatmap/stat fields, broken datasource variables, and malformed row collapse state.
- Substitute representative dashboard variables and validate PromQL expressions with Prometheus query APIs or a promtool-like checker, especially expressions containing `$additional_groupby` and `$command`.
- Verify the referenced metric families exist in TiKV and TiDB `/metrics` output, including histogram `_bucket`, `_sum`, and `_count` siblings.
- Smoke-test with several variable combinations: all instances, a single `$instance`, no extra group-by, grouping by `instance`, grouping by `req`, grouping by `task`, and grouping by `key_mode`.
- Visually inspect heatmaps and graph legends in Grafana to confirm bucket formats, date-time safepoint conversion, negative-Y count overlays, hidden count series, and stat `lastNotNull` reductions render as intended.

## Cross-Chunk Notes

This work item starts mid-dashboard after earlier scheduler panels and ends inside the opening of `GC scan write details` panel id 426. The final merged per-file research should combine this chunk with adjacent chunks to recover the full scheduler row before line 52918, the remainder of panel id 426 after line 60535, later GC panels, dashboard templating definitions, and top-level dashboard metadata.
