# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 76907-85424

## Purpose

This chunk defines a late section of the TiKV details Grafana dashboard. It is declarative dashboard JSON rather than executable code: the operational behavior comes from Grafana rendering panels and Prometheus evaluating the embedded PromQL. The covered lines finish most of the `Backup Log` observability row, then define collapsed rows for `Threads`, `Memory`, `Resource Control`, `Status Server`, `Encryption`, and the beginning of `TTL`.

The main purpose is production troubleshooting for TiKV log backup, advancer progress, process/thread health, allocator behavior, resource control/analyze work, HTTP status server latency, encryption health, and TTL expiration throughput. Every query is scoped through dashboard template variables such as `${DS_TEST-CLUSTER}`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$optional_quantile`, and `$additional_groupby`.

## Important Dashboard Objects and Metrics

The chunk continues the log backup panels with stat, graph, and heatmap objects. Key panels include:

- `Total Flushed Size (Last 30m)` and `Flush Files (Last 30m)`, both using `delta(...[30m])` on `tikv_log_backup_flush_file_size_sum` and `_count`.
- `CPU Usage`, based on `tikv_thread_cpu_seconds_total` for thread names matching `backup_stream|log-backup-scan(-[0-9]+)?`.
- Log backup throughput and progress: `tikv_log_backup_handle_kv_batch_sum`, `tikv_log_backup_incremental_scan_bytes_sum`, `tidb_log_backup_last_checkpoint`, `tikv_log_backup_heap_memory`, and `tikv_log_backup_observed_region`.
- Error panels over `tikv_log_backup_errors` and `tikv_log_backup_fatal_errors`, grouped by `type` and `instance`.
- Duration heatmaps over histogram buckets for flush, initial scan, raft event conversion, region TS resolve, command batch size, temp-file save/write/syscall-write, and advancer tick/batch operations.
- Internal actor panels over `tikv_log_backup_internal_actor_acting_duration_sec_count` and `_bucket`, grouped by message.
- Initial scan RocksDB operation panels using `tikv_log_backup_initial_scan_operations`, trigger reasons via `tikv_log_backup_initial_scan_reason`, pending stages via `tikv_log_backup_pending_initial_scan`, and temp-file cache/swap metrics.
- Advancer checkpoint panels using `tidb_log_backup_advancer_*`, `tidb_log_backup_region_request*`, `tidb_log_backup_current_last_region_id`, `tikv_log_backup_store_last_checkpoint_*`, and `tikv_log_backup_active_subscription_number`.

The collapsed `Threads` row contributes panels for `tikv_threads_state`, `tikv_threads_io_bytes_total`, `tikv_thread_voluntary_context_switches`, and `tikv_thread_nonvoluntary_context_switches`. The `Memory` row covers allocator state through `tikv_allocator_stats`, `tikv_allocator_thread_allocation`, `tikv_allocator_thread_stats`, and `tikv_allocator_arena_count`.

The `Resource Control` row mixes resource-control and analyze metrics: `tikv_resource_control_background_task_wait_duration`, `tikv_resource_control_priority_quota_limit`, `tikv_analyze_metrics_total`, and `tikv_coprocessor_rocksdb_perf` for analyze full sampling block reads. The `Status Server` row uses `tikv_status_server_request_duration_seconds_{bucket,sum,count}` to expose p99/p99.99, average, and operation-rate views by path. The `Encryption` row uses `tikv_encryption_data_key_storage_total`, `tikv_encryption_file_num`, `tikv_encryption_is_initialized`, `tikv_encryption_meta_file_size_bytes`, `tikv_coprocessor_rocksdb_perf` encryption/decryption nanos, and `tikv_encryption_write_read_file_duration_seconds_{bucket,sum,count}`. The chunk ends inside the first `TTL` panel, `tikv_ttl_expire_kv_count_total`; the panel is incomplete in this chunk and should be reconciled with the next chunk.

## Control Flow and Data Flow

Runtime control is Grafana-driven. The JSON creates row panels, most of them collapsed, with nested panels inside each row. When a user expands a row or views the dashboard, Grafana sends each `targets[*].expr` query to the selected Prometheus datasource and renders results according to the panel type.

PromQL data flow follows a few repeated patterns:

- Counter rates use `rate(metric[$__rate_interval])`, usually summed by `instance`, `type`, `reason`, `result`, `stage`, `path`, `message`, or `$additional_groupby`.
- Recent totals use `delta(metric[30m])` for stat panels that show last-30-minute flush size/count.
- Histogram heatmaps use `sum(increase(metric_bucket[$__rate_interval])) by (le)`.
- Quantile graphs use `histogram_quantile(...)` over `sum(rate(..._bucket[$__rate_interval])) by (..., le)`.
- Average latency series divide `sum(rate(..._sum))` by `sum(rate(..._count))`.
- Diagnostic top lists use `topk(20, ...)` with threshold filters for thread IO and context switches.

The dashboard has no local branching logic beyond Grafana options such as `hide`, collapsed rows, legends, axis units, graph overrides, and null handling.

## State and Persistence Behavior

Persistent state is the JSON dashboard definition itself. Operational state comes from Prometheus time series emitted by TiKV and TiDB log backup components. The dashboard reads but does not mutate TiKV state.

The visible state categories in this chunk are:

- Log backup persisted/progress state: checkpoint timestamps, current last region IDs, per-store checkpoint TS/region IDs, active subscriptions, observed region counts, pending initial scan stages, temp-file memory/count/swap size, and flushed files/bytes.
- Process state: thread states, IO bytes, voluntary/nonvoluntary context switches, allocator totals, per-thread allocations, mapped memory, and arena counts.
- Service state: status server request latency/rate by API path.
- Encryption state: key count, encrypted file count, initialization flag, meta file size, crypto nanos, and encryption metadata read/write duration.

Several metrics are counters or histograms that require monotonic series. The stat descriptions note that flush totals may drop after TiKV reboot, because the underlying per-process counters reset.

## Dependencies and Integration Points

This chunk depends on:

- Grafana dashboard JSON schema for row, graph, heatmap, and stat panels.
- The `${DS_TEST-CLUSTER}` datasource variable resolving to Prometheus or a Prometheus-compatible backend.
- Dashboard template variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$optional_quantile`, and `$additional_groupby`.
- TiKV metrics exporters for `tikv_*` series, plus TiDB/log-backup advancer metrics for `tidb_log_backup_*` series.
- Prometheus label contracts including `instance`, `k8s_cluster`, `tidb_cluster`, `name`, `type`, `stage`, `message`, `cf`, `op`, `reason`, `result`, `task`, `priority`, `metric`, `req`, `path`, and `le`.

The integration point with TiKV/TiDB code is metric naming and label stability. Any source-code change that renames log backup, allocator, status server, encryption, analyze, or TTL metrics must update this dashboard. Any change to thread naming also affects the log-backup CPU panel because it filters by thread-name regex.

## Risks and Observability Gaps

- Some panels use `delta` over counters that may reset on restart. The dashboard notes this for flush summaries, but the visual result can still mislead during incident triage.
- `Current Last Region Leader Store ID` appears to query `tikv_log_backup_store_last_checkpoint_ts / 262144`, which looks like a timestamp conversion despite the title saying leader store ID. This may be a dashboard bug or a misleading title.
- `Observed Region Count` repeats the same expression twice, once as `{{instance}}` and once as `{{instance}}-total`, so it may duplicate identical series rather than showing separate per-instance and total views.
- The `Status API Request Duration` panel hides p99.99, average, and count series, leaving p99 visible by default. That is intentional-looking but can hide important tail and traffic context unless users inspect panel settings.
- Several heatmaps aggregate only by `le`, losing `instance` and other labels. This is useful for fleet-level shape but can mask a single slow store.
- The `reason!="retryable-scan-region"` filter in the region checkpoint failure panel suppresses a known retryable category; this reduces noise but can hide a surge in retries.
- Many graph panels use `null as zero`, which can make missing metrics look like true zero values.
- The chunk boundary cuts the TTL row after the query target for `tikv_ttl_expire_kv_count_total`; title, axes, and any subsequent TTL panels are outside this chunk.

## Test and Validation Signals

Useful validation for this chunk is mostly dashboard and metric-contract oriented:

- Load the JSON into Grafana or run a dashboard linter to verify valid panel nesting, unique IDs in the covered range, valid row collapse structure, and supported legacy panel fields.
- Run Prometheus query validation for representative expressions, especially histogram queries, `$additional_groupby` interpolation, and the thread `topk` expressions.
- Verify Prometheus exposes all referenced metrics in a TiKV/TiDB cluster with log backup, encryption, resource control, analyze, and TTL enabled.
- During dashboard review, check that the suspicious leader-store panel and duplicated observed-region expressions match operator intent.
- Exercise restart scenarios to confirm flush stat descriptions and counter-reset behavior are acceptable.
- Compare units against metric semantics: bytes/binBps for size and throughput, seconds for duration, microseconds for resource control quota/wait panels, percentunit for CPU, ops for rates, and none for IDs/counts.

## Cross-Chunk Notes

This is a partial file chunk. It starts mid-panel just before the `Total Flushed Size (Last 30m)` stat title and ends mid-panel in the `TTL` row. The later merge lane should combine this report with adjacent chunks to recover the full `Backup Log` row start and the rest of the TTL dashboard section.
