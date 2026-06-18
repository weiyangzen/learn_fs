# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 8023-15657

## Scope

This chunk covers a middle segment of the TiKV details Grafana dashboard JSON. It starts at the tail of the preceding `gRPC` row, then defines the collapsed `Storage`, `Local Reader`, `Thread CPU`, and `IO Breakdown` rows. The range ends inside panel `113` in the following `Raft Waterfall` row's first latency panels, so the last panel is visible enough to identify its purpose and queries but continues past the chunk boundary.

The content is dashboard configuration rather than executable code. Its "APIs" are Grafana panel schemas, Prometheus datasource targets, dashboard template variables, and PromQL expressions tied to TiKV metric names.

## Purpose

The chunk builds operational observability for TiKV storage-path latency, local read routing, thread-level CPU attribution, disk IO throughput, IO rate limiting, and early raft waterfall latency. It lets operators answer questions such as:

- how many storage commands TiKV is receiving by `type`;
- whether async engine requests are failing;
- how write, snapshot, local-read snapshot, read-index propose, and read-index confirm latency distributions behave;
- whether full compaction is consuming or pausing storage work;
- whether local reads are accepted, rejected, stale, or follower reads;
- which TiKV thread pools are consuming CPU;
- whether read/write IO volume or rate limiter wait time is high;
- where raft request latency is accumulating between async write, store, apply, propose wait, and batch wait phases.

## Important Dashboard Objects

- Row `61`, title `Storage`, collapsed with 17 child panels. It groups storage command rates, async request errors, heatmaps and percentile graphs for async request durations, process CPU, full compaction timings, and concurrency manager timestamps.
- Row `79`, title `Local Reader`, collapsed with 2 child panels. It tracks local read rejection reasons and received/executed local read request rates.
- Row `82`, title `Thread CPU`, collapsed with 20 child panels. It groups `tikv_thread_cpu_seconds_total` by regex-matched TiKV thread names and exposes busy non-RocksDB threads over 80 percent CPU.
- Row `103`, title `IO Breakdown`, collapsed with 4 child panels. It tracks write/read IO bytes, IO rate limiter thresholds, and rate limiter request wait duration.
- Row `108`, title `Raft Waterfall`, is visible from the full JSON structure and begins in this chunk with panels `109` through `113`. This chunk includes async write, store, apply, store propose wait, and store batch wait latency panels; panel `113` continues past line 15657.

All panels use the Prometheus datasource template `${DS_TEST-CLUSTER}` except row containers, which have null datasources. Most queries are filtered by dashboard variables `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, `instance=~"$instance"`, and many aggregate by `$additional_groupby`. Latency and rate panels use Grafana's `$__rate_interval`; the IO rate limiter quantile panel uses `$optional_quantile`.

## Metrics And Query Patterns

The `Storage` row uses these main metrics:

- `tikv_storage_command_total`: command receive rate, grouped by `type` and `$additional_groupby`.
- `tikv_storage_engine_async_request_total`: async engine request error rate, filtering `status!~"all|success"`.
- `tikv_storage_engine_async_request_duration_seconds_bucket/_sum/_count`: async request histograms for `type="write"`, `type="snapshot"`, `type="snapshot_local_read"`, `type="snapshot_read_index_propose_wait"`, and `type="snapshot_read_index_confirm"`.
- `tikv_storage_process_stat_cpu_usage`: storage process CPU usage over the panel-described 30 second window.
- `tikv_storage_full_compact_duration_seconds_*`, `tikv_storage_full_compact_pause_duration_seconds_*`, and `tikv_storage_full_compact_increment_duration_seconds_*`: full compaction latency, pause latency, and per-increment latency.
- `tikv_concurrency_manager_max_ts_limit` and `tikv_concurrency_manager_max_ts`: concurrency manager timestamp progress and limit.

The latency graph pattern is repeated throughout this chunk: each graph overlays 99.99th percentile, 99th percentile, average, and count series. Percentiles are computed with `histogram_quantile(...)` over `sum(rate(<metric>_bucket[$__rate_interval])) by (le, $additional_groupby)`. Averages divide the rate of `_sum` by the rate of `_count`, and counts use the rate of `_count`. Heatmap companions use `sum(increase(<metric>_bucket[$__rate_interval])) by (le)`.

The `Local Reader` row uses:

- `tikv_raftstore_local_read_reject_total`, grouped by `instance` and `reason`;
- `tikv_raftstore_local_read_executed_requests`, `_executed_stale_read_requests`, `_executed_follower_read_requests`, `_received_requests`, `_received_stale_read_requests`, and `_received_follower_read_requests`, each rendered as rates grouped by `$additional_groupby`.

The `Thread CPU` row uses `tikv_thread_cpu_seconds_total` and regex filters on `name`:

- raftstore: `(raftstore|rs)_.*`;
- async apply: `apply_[0-9]+`;
- store writer: `store_write.*`;
- gRPC: `grpc.*`;
- scheduler: `sched_.*`;
- unified read pool: `unified_read_po.*`;
- RocksDB: `rocksdb.*`;
- GC, region, snapshot, background, raftlog fetch, import, backup, CDC, TSO, storage read pool, coprocessor read pool, and IME each have dedicated regexes.

The busy-thread panel uses `topk(20, sum(rate(tikv_thread_cpu_seconds_total{name!~"rocksdb.*"}[$__rate_interval])) by (instance, name) > 0.8)`, so it is an exception panel that surfaces only non-RocksDB threads above the 80 percent threshold.

The `IO Breakdown` row uses:

- `tikv_io_bytes{op="write"}` and `tikv_io_bytes{op="read"}` for per-type and total throughput;
- `tikv_rate_limiter_max_bytes_per_sec` for IO threshold by priority/type;
- `tikv_rate_limiter_request_wait_duration_seconds_*` for configurable quantile and average wait duration.

The visible part of `Raft Waterfall` uses:

- `tikv_storage_engine_async_request_duration_seconds_*{type="write"}`;
- `tikv_raftstore_store_duration_secs_*`;
- `tikv_raftstore_apply_duration_secs_*`;
- `tikv_raftstore_request_wait_time_duration_secs_*`;
- `tikv_raftstore_store_wf_batch_wait_duration_seconds_*`.

## Control Flow

Runtime flow is declarative and driven by Grafana:

1. Grafana loads the dashboard JSON and renders row panels.
2. Dashboard variables supply datasource, cluster, instance, grouping, rate interval, and optional quantile values.
3. Each panel sends its `targets[].expr` PromQL query to the selected Prometheus-compatible datasource.
4. Prometheus evaluates rate, increase, sum, avg, histogram, and top-k expressions against TiKV's exported metric series.
5. Grafana renders graph or heatmap panels, applies legend formatting, axis units, null handling, and series overrides.

There are no local functions, classes, or imperative branches in this JSON. The main control-flow-like behavior is the repeated composition of histogram bucket, sum/count, and count queries into a single graph panel and the use of collapsed rows to defer visual expansion in Grafana.

## State And Persistence Behavior

The chunk contributes persistent dashboard configuration. It does not mutate TiKV state, Prometheus state, or Grafana runtime state directly. Its persistence effects are through stored dashboard JSON: panel IDs, titles, grid positions, query text, legend formats, axis formats, and row membership remain stable until edited or regenerated.

Important persistent identifiers in this chunk include panel IDs `61` through `113`. These IDs are used by Grafana for panel references, links, snapshots, and dashboard diffs. Most panels set `nullPointMode` to `null as zero`, hide empty/zero legend series, and sort legends by maximum descending; this affects incident interpretation because missing series may be visually suppressed or flattened to zero.

## Dependencies And Integration Points

- Grafana dashboard schema: row, graph, heatmap, `gridPos`, `fieldConfig`, `legend`, `tooltip`, `xaxis`, `yaxes`, and series override fields.
- Prometheus query language: `rate`, `increase`, `sum`, `avg`, `histogram_quantile`, `topk`, regex label filters, and grouping clauses.
- TiKV metric exporters: all metric names in this chunk must remain emitted with expected labels such as `k8s_cluster`, `tidb_cluster`, `instance`, `type`, `status`, `reason`, `name`, `op`, and histogram `le`.
- Dashboard templating: `${DS_TEST-CLUSTER}`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$__rate_interval`, and `$optional_quantile`.
- Operational runbooks and alerts may depend on panel titles and metric semantics even if no alert rules are embedded in this chunk.

## Risks

- Query drift risk: if TiKV renames metrics or thread names, panels silently go empty. This is especially likely for regex-based thread panels such as `unified_read_po.*`, `(backup-worker|bkwkr|backup_endpoint).*`, and CDC/TSO naming variants.
- Label-cardinality risk: `$additional_groupby` can expand every latency and IO panel by arbitrary grouping labels. High-cardinality groupings can make Grafana slow and Prometheus queries expensive.
- Histogram correctness risk: `histogram_quantile` requires preserving `le` in the aggregation. This chunk does so, but any future edit that removes `le` would make percentiles invalid.
- Average correctness risk: averages divide `_sum` rate by `_count` rate. If count is zero or missing for a grouping, Prometheus can produce empty or invalid-looking series.
- Visual interpretation risk: `null as zero`, hidden empty/zero legends, and negative-Y transforms for count series can make absence of data look like zero work or hide instrumentation failures.
- Boundary risk: the chunk ends in panel `113`; later chunks must reconcile the rest of `Store batch wait duration` and any subsequent `Raft Waterfall` panels before producing the final per-file research.
- Duplicate semantics risk: `Storage async write duration` appears both in the `Storage` row and in the beginning of `Raft Waterfall`. This is likely intentional for different diagnostic contexts, but dashboard maintenance must keep the duplicated queries consistent.

## Test Signals

Useful validation signals include:

- Parse the file with `jq` to confirm valid JSON and stable panel nesting for rows `61`, `79`, `82`, `103`, and `108`.
- Use a Grafana dashboard linter or provisioning dry-run to ensure graph and heatmap panel fields are accepted by the target Grafana version.
- Run Prometheus API query checks for representative expressions from each row against a TiKV test cluster: `tikv_storage_command_total`, `tikv_storage_engine_async_request_duration_seconds_bucket`, `tikv_raftstore_local_read_reject_total`, `tikv_thread_cpu_seconds_total`, `tikv_io_bytes`, and `tikv_rate_limiter_request_wait_duration_seconds_bucket`.
- Verify every histogram quantile query groups by `le` plus any intended label dimensions.
- Verify dashboard variables expand safely when `$additional_groupby` is empty or contains one or more labels.
- Compare rendered panels before and after any dashboard edit with a cluster that has storage traffic, local reads, raftstore activity, compaction, and IO rate limiter activity.
