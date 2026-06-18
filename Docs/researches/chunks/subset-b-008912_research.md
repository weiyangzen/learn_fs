# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 45106-52917

## Scope and Purpose

This chunk is a line-bounded slice of the TiKV Details Grafana dashboard JSON. It starts in the middle of panel `315` in the collapsed `In Memory Engine` row and ends inside panel `372` in the collapsed `Scheduler - $command` row. The file is declarative dashboard configuration, not executable source code, so the important "APIs" are Grafana panel schema fields, Prometheus/PromQL expressions, dashboard variables, and the TiKV metric series those expressions depend on.

The slice covers three operational areas:

- The tail of the `In Memory Engine` row, focused on cached region counts, cache GC/load/eviction/warmup, in-memory engine write and prepare-for-write latency, iterator seek/next/prev activity, per-region GC safe points, and auto-load/auto-evict decision distributions.
- Complete collapsed rows for `Flow Control`, `Scheduler`, and `Scheduler Worker Pool`, covering scheduler write/throttle flow, compaction pressure inputs, command queues, memory quota, YATP scheduler worker wait/execute latency, multilevel scheduling, and worker-pool task timing.
- The beginning of the `Scheduler - $command` row, covering command-specific stage totals, command duration, latch wait duration, key-read/key-write distributions, and the all-CF scan-detail panel for the selected `$command`.

Because the requested line range begins and ends inside panel objects, the final per-file report should reconcile this chunk with adjacent chunks before treating row boundaries as complete.

## Dashboard Structure

The chunk uses Grafana's legacy dashboard model:

- Rows are `type: "row"` panels with `collapsed: true` and a nested `panels` array.
- Graph panels use `type: "graph"`, legacy `xaxis`/`yaxes`, `renderer: "flot"`, right-side legend tables, and `nullPointMode: "null as zero"`.
- Heatmap panels use `type: "heatmap"`, `dataFormat: "tsbuckets"`, `format: "heatmap"` targets, hidden zero buckets, and bucket-axis units such as seconds or generic counts.
- Datasource references are `${DS_TEST-CLUSTER}` on child panels. Row containers have `datasource: null`.
- Most queries filter on `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, and usually `instance=~"$instance"`.
- Many panels include `$additional_groupby` inside PromQL `by (...)` clauses and in legend templates; command-specific panels also use `$command`.

Panel groups in this chunk:

- `In Memory Engine` row `307`, panel IDs `315-336` within this slice.
- `Flow Control` row `337`, panel IDs `338-347`.
- `Scheduler` row `348`, panel IDs `349-356`.
- `Scheduler Worker Pool` row `357`, panel IDs `358-365`.
- `Scheduler - $command` row `366`, panel IDs `367-372` within this slice. The full row continues beyond this chunk in the source file.

## Important APIs, Types, and Query Functions

There are no application functions or Rust/Go types in this JSON. The operative interfaces are:

- Grafana panel fields: `id`, `title`, `description`, `type`, `datasource`, `targets`, `legend`, `seriesOverrides`, `gridPos`, `tooltip`, `fieldConfig`, `yaxes`, and heatmap `xAxis`/`yAxis`.
- PromQL range functions: `rate`, `increase`, `delta`, and `avg_over_time`.
- PromQL aggregations: `sum`, `avg`, and `max` with `by (...)` groupings.
- PromQL histogram handling: `histogram_quantile` over bucket rates, and `_sum / _count` average overlays.
- Grafana variables: `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$command`.

Common query idioms:

- Heatmaps: `sum(increase(<metric>_bucket{...}[$__rate_interval])) by (le)`.
- Tail latency graphs: `histogram_quantile(0.9999, sum(rate(<metric>_bucket{...}[$__rate_interval])) by (le, ...))` and a matching `0.99` query.
- Average overlays: `sum(rate(<metric>_sum[...])) by (...) / sum(rate(<metric>_count[...])) by (...)`.
- Count overlays: `sum(rate(<metric>_count[...])) by (...)`, often hidden or transformed to the negative secondary axis.
- Gauges: direct `sum((metric{...})) by (...)`, `max((metric{...})) by (...)`, or booleanized gauges such as `!= 0`.

## In Memory Engine Metrics and Behavior

The in-memory engine panels expose the lifecycle of regions cached in TiKV's in-memory engine:

- `Region Count` uses `tikv_in_memory_engine_cache_count` averaged by `instance` and `type` to show the number and type mix of cached regions.
- `GC Filter` uses `tikv_in_memory_engine_gc_filtered` rates by filter `type` and `$additional_groupby` to show cache-GC filtering activity.
- `Region GC Duration`, `Region Load Duration`, and `Region Eviction Duration` are heatmaps from `*_duration_secs_bucket` metrics, tracking latency distributions for GC, load, and eviction work.
- `Region Load Count` and `Region Eviction Count` use `delta(..._count[$__rate_interval])`, which treats histogram counts as interval deltas rather than per-second rates. This makes the panels event-count oriented over the current range interval.
- `Region Warmup Count` uses `tikv_in_memory_engine_transfer_leader_warmup_total` to observe warmup activity after leader transfer or related cache warmup triggers.
- `Write duration` and `99% In-memory engine write duration per server` use `tikv_in_memory_engine_write_duration_seconds_*` to provide both cluster heatmap distribution and per-instance p99.99/p99/average/count overlays.
- `Prepare for write duration` and its per-server percentile graph mirror the write-duration panels for `tikv_in_memory_engine_prepare_for_write_duration_seconds_*`.
- `Iterator operations` breaks `tikv_in_memory_engine_locate` into `number_db_seek`, `number_db_seek_found`, `number_db_next`, `number_db_next_found`, `number_db_prev`, and `number_db_prev_found`.
- `Seek duration` uses `tikv_in_memory_engine_seek_duration_*` with `histogram_quantile(1)`, `$optional_quantile`, `0.95`, and average overlays. The `1` quantile is a bucket-bound approximation, not an exact maximum.
- `Oldest Auto GC SafePoint`, `Newest Auto GC SafePoint`, `Auto GC SafePoint Gap`, and `Auto GC SafePoint Gap With TiKV` expose per-region in-memory-engine GC safe point age and gap by dividing timestamp-or-TSO-like values by `2^18`.
- `Cached Region Coprocessor Requests`, `Cached Region MVCC Amplification`, `Top Region Coprocessor Requests`, and `Top Region MVCC Amplification` are heatmaps used to understand auto-load/auto-evict inputs for cached versus top regions.

These panels integrate TiKV's in-memory engine with Prometheus and Grafana as an operational feedback loop: operators can see whether regions are being loaded, evicted, or GCed too often; whether in-memory writes or prepare steps have long tails; whether iterator activity is dominated by misses; and whether GC safe point gaps are growing enough to retain MVCC history.

## Flow Control Metrics and Behavior

The `Flow Control` row describes TiKV scheduler flow-control pressure:

- `Scheduler flow` compares `tikv_scheduler_write_flow` with nonzero `tikv_scheduler_throttle_flow`, grouped by `instance`, to show actual write flow and active throttling.
- `Scheduler discard ratio` divides `tikv_scheduler_discard_ratio` by `10000000`, then renders it as a percent-unit graph by `type`.
- `Throttle duration` is a heatmap over `tikv_scheduler_throttle_duration_seconds_bucket`.
- `Scheduler throttled CF` booleanizes `tikv_scheduler_throttle_cf != 0` and labels series by `instance` and `cf`, making column-family throttling visible.
- `Flow controller actions` rates `tikv_scheduler_throttle_action_total` by action `type`, column family `cf`, and `$additional_groupby`.
- `Flush/L0 flow` compares `tikv_scheduler_l0_flow` and `tikv_scheduler_flush_flow` by `instance` and `cf`, plus total-by-instance overlays.
- `Flow controller factors` graphs `tikv_scheduler_l0`, `tikv_scheduler_memtable`, and `tikv_scheduler_l0_avg`, all maxed by `instance`.
- `Compaction pending bytes` shows RocksDB `tikv_engine_pending_compaction_bytes{db="kv"}` by `cf`, with a hidden scheduler-specific pending-compaction query divided by `10000000`.
- `Txn command throttled duration` and `Non-txn command throttled duration` rate `tikv_txn_command_throttle_time_total` and `tikv_non_txn_command_throttle_time_total` by `type`.

This row is an integration point between RocksDB storage pressure, TiKV scheduler flow-control policy, and user-visible command throttling. It lets operators correlate write flow, L0/memtable factors, pending compaction bytes, and throttle actions before moving to command-level scheduler panels.

## Scheduler Metrics and Behavior

The `Scheduler` row focuses on the transaction scheduler as a queueing and memory-governed subsystem:

- `Scheduler stage total` overlays `tikv_scheduler_too_busy_total` and `tikv_scheduler_stage_total` rates by `stage`, showing both normal command-stage throughput and too-busy rejections.
- `Scheduler priority commands` rates `tikv_scheduler_commands_pri_total` by command `priority`.
- `Scheduler pending commands` graphs `tikv_scheduler_contex_total` by `instance`. The metric name appears to be spelled `contex`, so renaming it would break this dashboard unless queries are migrated.
- `Scheduler running commands` graphs `tikv_scheduler_running_commands` by `instance`.
- `Scheduler writing bytes` graphs `tikv_scheduler_writing_bytes` by `instance`.
- `Scheduler memory quota` overlays `tikv_scheduler_memory_quota_size{type="in_use"}` and `{type="capacity"}` by `instance`.
- `Txn Scheduler Pool Wait Duration` and `Txn Scheduler Pool Exec Duration` are heatmaps over YATP scheduler-worker pool wait and exec bucket metrics filtered by `name=~"sched-worker.*"`.

These panels model the scheduler as a flow from queued command contexts, through running commands, to write bytes and memory quota. The YATP pool heatmaps connect scheduler symptoms to worker-pool saturation.

## Scheduler Worker Pool Metrics and Behavior

The `Scheduler Worker Pool` row tracks multilevel YATP scheduling behavior for `sched-worker.*` pools:

- `Time used by level` rates `tikv_multilevel_level_elapsed` by `level`, with level 0 described as small queries.
- `Level 0 chance` graphs `tikv_multilevel_level0_chance` per instance, indicating how often small tasks are selected.
- `Running tasks` uses `avg_over_time(tikv_scheduler_running_commands[1m])` by `instance` and `$additional_groupby`.
- `Wait Duration` duplicates the scheduler wait-duration heatmap for `tikv_yatp_pool_schedule_wait_duration_bucket`.
- `Running threads` uses `avg_over_time(tikv_unified_read_pool_thread_count[1m])`; despite the row being scheduler-worker oriented, this metric name references the unified read pool, so the panel should be checked for intentional reuse versus copy/paste drift.
- `Duration of One Time Slice` uses `tikv_yatp_task_poll_duration_*` p99.99, p99, average, and count overlays.
- `Task Execute Duration` uses `tikv_yatp_task_exec_duration_*`.
- `Task Schedule Times` uses `tikv_yatp_task_execute_times_*`.

This row is important when scheduler latency could come from worker-pool scheduling rather than storage or command semantics. The multilevel panels expose fairness and small-task preference, while poll/exec/schedule-times histograms expose per-task runtime and rescheduling behavior.

## Command-Specific Scheduler Metrics

The `Scheduler - $command` row starts at panel ID `366` and is parameterized by `$command`. Within this chunk it includes:

- `Scheduler stage total`, filtering `tikv_scheduler_too_busy_total` and `tikv_scheduler_stage_total` with `type="$command"`.
- `Scheduler command duration`, using `tikv_scheduler_command_duration_seconds_*` to show p99.99, p99, average, and hidden count for the selected command.
- `Scheduler latch wait duration`, using `tikv_scheduler_latch_wait_duration_seconds_*` to isolate latch contention within the selected command path.
- `Scheduler keys read`, using `tikv_scheduler_kv_command_key_read_*` to show key-read distribution and count.
- `Scheduler keys written`, using `tikv_scheduler_kv_command_key_write_*` to show key-write distribution and count.
- `Scheduler scan details`, using `tikv_scheduler_kv_scan_details{req="$command"}` by scan `tag` and `$additional_groupby`.

The chunk ends inside the `Scheduler scan details` panel after the `xaxis` block begins. Later panels in the same row, such as CF-specific scan details and command process/block-read duration, are outside this requested line range and must be handled by following chunks.

## State and Persistence Behavior

The JSON persists Grafana dashboard state only: row collapse state, panel IDs, panel layout, titles/descriptions, datasource variables, query strings, legend display state, axis units, heatmap options, and series overrides. It does not persist TiKV runtime state.

The persisted dashboard state does, however, encode assumptions about TiKV runtime state:

- In-memory engine state is observed through cached region counts, load/eviction/GC counters, safe point gauges, write/prepare histograms, and auto-load/auto-evict input distributions.
- Scheduler state is observed through command queues, running commands, memory quota in-use/capacity gauges, write bytes, flow-controller throttle status, and worker-pool histograms.
- Storage pressure state is observed indirectly through L0 flow, flush flow, memtable factors, and pending compaction bytes.
- Command-specific state is observed through `$command`-filtered stage counters, duration histograms, latch wait histograms, key read/write histograms, and scan-detail counters.

PromQL functions imply stateful metric semantics. `rate` and `increase` assume counter-like monotonicity; `delta` assumes meaningful changes over the selected range; `avg_over_time` depends on scrape continuity; histogram quantiles assume bucket label `le` and complete bucket series. Counter resets, missing scrapes, or metric-label churn can therefore look like real TiKV behavior in these panels.

## Dependencies and Integration Points

Primary dependencies:

- Grafana legacy graph, heatmap, and row panel schema.
- Prometheus datasource `${DS_TEST-CLUSTER}`.
- Grafana runtime variables `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$command`.
- TiKV Prometheus exporters for in-memory engine, scheduler, flow control, RocksDB engine, YATP, multilevel scheduler, and unified read/scheduler pool metrics.

Operational integration points:

- In-memory-engine panels support debugging cache churn, region warmup, safe point lag, write-path overhead, and auto-load/auto-evict decisions.
- Flow-control panels support debugging throttling from L0, memtable, flush, and compaction pressure.
- Scheduler panels support transaction scheduler queue, memory, write-size, too-busy, and worker-pool diagnosis.
- Command-specific panels support isolating latency, latch waits, and read/write/scan amplification for a selected command such as commit.

## Risks and Edge Cases

- The chunk starts mid-panel and ends mid-panel. Any automated reader of this line range alone does not see complete JSON objects for the first and last panels.
- `$additional_groupby` appears inside many `by (...)` clauses. If it expands to an empty string or an invalid comma-separated fragment, PromQL syntax can break or grouping can change unexpectedly.
- `$command` is embedded as an exact label match in some panels with `type="$command"` and as `req="$command"` in scan details. Dashboard variable values must match TiKV label values exactly.
- `nullPointMode: "null as zero"` can hide missing data, scrape gaps, or removed metric series by rendering them as zeros.
- High-cardinality labels such as `instance`, `cf`, `type`, `tag`, `priority`, `level`, and arbitrary `$additional_groupby` values can make histogram quantile and heatmap queries expensive.
- Several panels use p99.99 histograms. These are sensitive to sparse bucket data and scrape interval selection.
- `histogram_quantile(1, ...)` in `Seek duration` should be interpreted as the highest observed bucket boundary estimate, not a precise maximum.
- The in-memory load and eviction count panels use `delta` on histogram count series instead of `rate` or `increase`; this may behave poorly around counter resets.
- Some axis scaling is manual: safe points divide by `2^18`, discard ratio divides by `10000000`, and one hidden pending-compaction query divides by `10000000`. These constants should be verified against the metric units before changing.
- `Scheduler pending commands` references `tikv_scheduler_contex_total`; this likely preserves an existing exported metric spelling. Correcting the spelling in only the dashboard would break the panel.
- `Running threads` in the scheduler worker row uses `tikv_unified_read_pool_thread_count` while the rest of the row filters `sched-worker.*`. This may be intentional cross-pool context or a dashboard drift risk.

## Test Signals

Useful validation is dashboard and query validation rather than unit testing:

- Parse the complete `tikv_details.json` with `jq` to ensure the source file is still valid JSON after any dashboard edits.
- Import or provision the dashboard into Grafana to catch legacy panel schema issues, duplicate panel IDs, broken row nesting, invalid datasource references, and bad heatmap/graph rendering.
- Substitute representative values for `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$command`, then validate the resulting PromQL expressions against Prometheus.
- Check that all referenced metric families exist in TiKV `/metrics`, including `_bucket`, `_sum`, and `_count` siblings for histogram panels.
- Smoke-test both empty and non-empty `$additional_groupby` configurations because it is used in many group-by clauses.
- Verify heatmap panels render bucket distributions with the expected units and that graph legends hide or show average/count overlays as intended.
- Compare scheduler worker panels against live worker-pool metrics to confirm `sched-worker.*` filters and the `tikv_unified_read_pool_thread_count` panel are intentional.

## Cross-Chunk Notes

This chunk should be merged with adjacent chunks for complete panel context:

- The beginning of panel `315` and earlier `In Memory Engine` panels are before line `45106`.
- The `Scheduler scan details` panel `372` continues after line `52917`.
- The remainder of the `Scheduler - $command` row, including CF-specific scan details and later command-processing panels, is outside this work item.
