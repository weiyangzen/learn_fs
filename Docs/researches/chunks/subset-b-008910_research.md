# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 30294-37416

## Scope and Purpose

This chunk is a mid-dashboard section of the TiKV Grafana details dashboard. It closes the collapsed `Raft Log` row, defines the full collapsed `Raft Engine` row, and begins the collapsed `RocksDB - $db` row. The file is declarative Grafana JSON, so its operational surface is the panel schema plus the embedded PromQL query contracts against TiKV, raft-engine, Prometheus, and Grafana dashboard variables.

The chunk gives operators drill-down visibility into three storage paths:

- Raft log GC and asynchronous raft log fetching, including GC write/seek rates, skipped/failed GC, raft log lag, fetch counts, and fetch worker queue depth.
- Raft Engine write/read/rewrite/WAL behavior, including operation rates, high-percentile write duration, write-size distribution, WAL sub-phase latency, log file and entry counts, and compression ratio.
- RocksDB engine behavior for the selected `$db`, including get/seek/write/WAL/compaction/cache/key/read/write panels through `Bytes / Read` at panel id 262.

## Dashboard Structure

The chunk contains these row/panel groups:

- `Raft Log` row ending at panel id 225. Visible panels in this chunk are ids 218-225.
- `Raft Engine` collapsed row id 226. Nested panels are ids 227-236.
- `RocksDB - $db` collapsed row id 237. Nested panels in this chunk are ids 238-262; the row continues after the chunk.

All panels use the old Grafana graph panel shape: `"type": "graph"`, `renderer: "flot"`, `xaxis.mode: "time"`, `targets` arrays containing Prometheus `expr`/`query`, and `legend` tables configured with current/max values, max sorting, and hidden empty/zero series. Most panels use `${DS_TEST-CLUSTER}` as the datasource and cluster selectors `{k8s_cluster="$k8s_cluster", tidb_cluster="$tidb_cluster", instance=~"$instance"}`. RocksDB panels also add `db="$db"` and often group by `$additional_groupby`.

## Important APIs, Types, and Query Contracts

There are no code-defined functions or classes in this JSON. The important "APIs" are the Grafana dashboard schema fields, the PromQL functions, and the metric names this dashboard assumes are exported.

Grafana-facing contracts:

- Row panels use `collapsed: true` and hold their child graphs in a `panels` array. This keeps the detailed storage sections folded until an operator expands them.
- Graph panels rely on `gridPos` to lay out mostly 12-wide, 7-high paired panels, with some 24-wide panels such as `Raft log async fetch task duration`.
- `targets[].expr` and `targets[].query` duplicate the same PromQL, a compatibility pattern for older Grafana/Prometheus datasource JSON.
- `legendFormat` depends on labels such as `instance`, `type`, `reason`, `cf`, and the template-expanded `$additional_groupby`.
- Units are set through `yaxes[].format`: `s`, `ops`, `binBps`, `bytes`, `percentunit`, `µs`, `short`, or `none`. Several latency panels use logarithmic axes.

PromQL contracts:

- Counter-like metrics are converted with `sum(rate(metric{...}[$__rate_interval])) by (...)`.
- Histogram metrics use `histogram_quantile(...)` over `sum(rate(..._bucket[$__rate_interval])) by (le, ...)`, with average lines computed as `sum(rate(..._sum)) / sum(rate(..._count))`.
- Gauge-like metrics use `avg((metric{...}))`, `sum((metric{...}))`, `max((metric{...}))`, or `topk(20, avg(...))` without `rate`.
- Dashboard variables used directly in PromQL include `$__rate_interval`, `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$db`.

Key metric families in this chunk:

- Raft log GC/fetch: `tikv_raftstore_raft_log_kv_sync_duration_secs_*`, `tikv_raftstore_raft_log_gc_write_duration_secs_count`, `tikv_raftstore_raft_log_gc_seek_operations_count`, `tikv_raftstore_log_lag_sum`, `tikv_raftstore_raft_log_gc_skipped`, `tikv_raftstore_raft_log_gc_failed`, `tikv_raftstore_entry_fetches`, `tikv_raftstore_entry_fetches_task_duration_seconds_*`, and `tikv_worker_pending_task_total{name=~"raftlog-fetch-worker"}`.
- Raft Engine: `raft_engine_write_apply_duration_seconds_*`, `raft_engine_read_entry_duration_seconds_*`, `raft_engine_read_message_duration_seconds_*`, `raft_engine_write_duration_seconds_*`, `raft_engine_write_size_*`, `raft_engine_background_rewrite_bytes_sum`, `raft_engine_write_preprocess_duration_seconds_bucket`, `raft_engine_write_leader_duration_seconds_bucket`, `raft_engine_sync_log_duration_seconds_bucket`, `raft_engine_allocate_log_duration_seconds_bucket`, `raft_engine_rotate_log_duration_seconds_bucket`, `raft_engine_log_file_count`, `raft_engine_swap_file_count`, `raft_engine_recycled_file_count`, `raft_engine_purge_duration_seconds_bucket`, `raft_engine_log_entry_count`, and `raft_engine_write_compression_ratio_*`.
- RocksDB engine: `tikv_engine_memtable_efficiency`, `tikv_engine_cache_efficiency`, `tikv_engine_get_served`, `tikv_engine_get_micro_seconds`, `tikv_engine_locate`, `tikv_engine_seek_micro_seconds`, `tikv_engine_write_served`, `tikv_engine_write_micro_seconds`, `tikv_engine_wal_file_synced`, `tikv_engine_write_wal_time_micro_seconds`, `tikv_engine_event_total`, `tikv_engine_num_running_compactions`, `tikv_engine_num_running_flushes`, `tikv_raftstore_compaction_guard_action_total`, `tikv_engine_compaction_time`, `tikv_engine_num_files_in_single_compaction`, `tikv_engine_sst_read_micros`, `tikv_engine_compaction_reason`, `tikv_engine_block_cache_size_bytes`, `tikv_engine_bloom_efficiency`, `tikv_engine_flow_bytes`, `tikv_engine_compaction_num_corrupt_keys`, `tikv_engine_estimate_num_keys`, and `tikv_engine_bytes_per_read`.

## Panel-Level Behavior

Raft log panels:

- `Raft log GC kv sync duration` id 218 plots 99.99th percentile and average KV sync latency by instance.
- `Raft log GC write operations` id 219 and `Raft log GC seek operations` id 220 show per-instance GC write and seek operation rates.
- `Raft log lag` id 221 charts raft log lag by instance from `tikv_raftstore_log_lag_sum`.
- `Raft log gc skipped` id 222 groups skipped GC by `instance, reason`; `Raft log GC failed` id 223 tracks failure rate.
- `Raft log fetch` id 224 groups fetch rates by `type` and `$additional_groupby`.
- `Raft log async fetch task duration` id 225 combines a 99.99th percentile fetch-task histogram, an average fetch-task latency line, and a pending-task gauge for `raftlog-fetch-worker`. The pending-task series is overridden onto the right axis and transformed as negative Y, which makes queue buildup visually distinct from duration.

Raft Engine panels:

- `Operation` id 227 compares write-apply, read-entry, and read-message operation rates.
- `Write Duration` id 228 overlays 99.99th percentile, 99th percentile, average, and hidden count for `raft_engine_write_duration_seconds`. Count is configured as a dashed negative right-axis series; average stays on the left axis.
- `Flow` id 229 shows raft-engine write bytes plus background rewrite bytes by rewrite `type`.
- `Write Duration Breakdown $optional_quantile` id 230 splits write latency into preprocess/wait, leader/WAL, and apply stages at the selected quantile.
- `Bytes / Written` id 231 mirrors the write-duration pattern for write size histograms, with percentile, average, and count series.
- `WAL Duration Breakdown (999%)` id 232 breaks WAL write latency into total, sync, allocate, and rotate at 0.999 quantile.
- `File Count` id 233 and `Entry Count` id 235 monitor log/swap/recycled files and log entries.
- `Other Durations $optional_quantile` id 234 covers read-entry, read-message, and purge histogram latencies.
- `Write Compression Ratio` id 236 shows high-percentile, average, and count series from raft-engine compression-ratio histograms.

RocksDB panels in this chunk:

- `Get operations` id 238 compares memtable hits, block cache hits, and L0/L1/L2-and-up get serving rates.
- `Get duration` id 239 and `Seek duration` id 241 use already-exported max/percentile/average gauge series in microseconds rather than deriving quantiles from buckets.
- `Seek operations` id 240 tracks seek/next/prev and found variants through `tikv_engine_locate`.
- `Write operations` id 242 distinguishes successful writes, timeouts, and WAL writes.
- `Write duration` id 243, `Write WAL duration` id 245, `WAL sync duration` id 247, `Compaction duration` id 249, `Compaction Job Size(files)` id 250, `SST read duration` id 251, and `Bytes / Read` id 262 all follow the same max/99/95/avg gauge-series pattern.
- `WAL sync operations` id 244 tracks sync rate.
- `Compaction operations` id 246 combines completed compaction/flush event rates on the left axis with running compaction/flush gauges on the right axis.
- `Compaction guard actions` id 248 groups raftstore compaction guard action rates by `cf`, `type`, and `$additional_groupby`, limited to `default|write` column families.
- `Compaction reason` id 252 groups compaction rates by `cf` and `reason`.
- `Block cache size` id 253 uses `topk(20, avg(tikv_engine_block_cache_size_bytes) by (cf, instance))`, so it intentionally caps displayed cache-size series.
- `Memtable hit` id 254, `Block cache hit` id 256, and bloom-prefix efficiency use ratio expressions of hit-like counters over hit-plus-miss or filtered-plus-match counters.
- `Block cache flow` id 255 covers read/write byte flow and data/filter/index insert/evict byte rates.
- `Keys flow` id 257 adds read/written key rates and corrupt-key compaction rate.
- `Block cache operations` id 258 counts cache add/add-failure operations by cache component.
- `Read flow` id 259, `Total keys` id 260, and `Write flow` id 261 show bytes read, estimated keys, WAL bytes, and write bytes.

## Control Flow and Data Flow

Grafana evaluates this chunk from dashboard variables to PromQL queries to panel rendering:

1. The user selects datasource, cluster, instance regex, `$additional_groupby`, optional quantile, and RocksDB `$db`.
2. Expanding a collapsed row materializes its nested graph panels.
3. For each visible panel, Grafana sends each target expression to the Prometheus datasource over the dashboard time range.
4. Prometheus filters TiKV/raft-engine metrics by the dashboard labels, applies `rate`, `sum`, `avg`, `max`, `topk`, or `histogram_quantile`, and groups by the requested labels.
5. Grafana renders each returned series using the panel title, legend format, unit, axis, and optional series override.

There is no local mutation or branching logic in the JSON. The effective behavior is controlled by metric availability, template variable expansion, Prometheus aggregation semantics, and Grafana rendering options.

## State and Persistence Behavior

This chunk persists dashboard state only as JSON configuration:

- Panel identity and layout are stored in stable numeric `id` and `gridPos` fields.
- Query state is embedded in each target's `expr`/`query`; no runtime query results are persisted in the repository.
- Collapsed rows persist their child panels under `panels`, so the dashboard starts compact while retaining detailed storage diagnostics.
- Visibility/interpretation state is encoded through `hide`, `seriesOverrides`, axis units, log bases, `nullPointMode: "null as zero"`, and legend sorting.

Runtime metric state lives outside this file in Prometheus. The dashboard assumes TiKV and raft-engine exporters provide compatible metric names and labels.

## Dependencies and Integration Points

Primary dependencies:

- Grafana graph panel JSON compatible with legacy/flot graph panels.
- Grafana Prometheus datasource `${DS_TEST-CLUSTER}`.
- Prometheus with TiKV and raft-engine metrics scraped under labels `k8s_cluster`, `tidb_cluster`, `instance`, and for RocksDB panels `db`.
- Dashboard templating variables `$instance`, `$additional_groupby`, `$optional_quantile`, `$db`, `$k8s_cluster`, `$tidb_cluster`, and `$__rate_interval`.

Integration points:

- Operators use these panels to correlate raftstore log GC/fetch symptoms with raft-engine WAL/write behavior and RocksDB compaction/cache behavior.
- Raft Engine panels depend on the raft-engine metric prefix rather than the older RocksDB/TiKV `tikv_engine_*` prefix.
- RocksDB panels integrate column-family labels (`cf`) and reason/type labels, making them sensitive to label cardinality and exporter naming.
- The `Compaction guard actions` panel bridges raftstore metrics into the RocksDB row, showing that storage layout and raftstore region compaction guard behavior are intentionally observed together.

## Risks and Edge Cases

- `$additional_groupby` is interpolated inside `by (...)` clauses. If it expands to an empty or malformed label list, PromQL can become invalid or produce unexpected grouping.
- Several average expressions divide rate sums by count rates. When counts are zero, Prometheus can return `NaN`/`Inf`; Grafana's `null as zero` may mask missing traffic as zero.
- `nullPointMode: "null as zero"` can make scrape gaps or missing metric series look like real zero values.
- High-cardinality grouping by `instance`, `cf`, `reason`, `type`, and arbitrary `$additional_groupby` values can create heavy Prometheus queries, especially histogram quantiles across bucket series.
- The dashboard mixes histogram-derived quantiles for raft-engine with exporter-provided percentile gauges for RocksDB. The two forms have different statistical meaning and aggregation behavior.
- Panel id 253 uses `topk(20)`, intentionally hiding all but the largest 20 block-cache size series.
- Some panel titles and labels contain cosmetic inconsistencies, such as trailing spaces, `999%` wording for 0.999 quantile, and `{{ type}}` with an extra space in the legend template. These do not necessarily break Grafana but can reduce polish or make legend matching brittle.
- Series overrides that transform count/pending-task series to negative Y are visually useful but can be misread as negative metric values if operators do not know the convention.
- The chunk assumes metric families such as `raft_engine_*` and `tikv_engine_*` retain exact names and label values. Exporter renames, TiKV version drift, or raft-engine feature-gating would silently empty panels.

## Test and Validation Signals

Useful validation checks for this chunk:

- Parse the dashboard with `jq` to ensure JSON syntax remains valid and panel ids 218-262 are present with expected titles.
- Load the dashboard in Grafana and expand `Raft Log`, `Raft Engine`, and `RocksDB - $db` rows to confirm nested panels render and do not show datasource/query syntax errors.
- Run representative PromQL queries from each family in Prometheus: one histogram quantile, one average `_sum/_count` expression, one `$optional_quantile` query, one RocksDB percentile gauge, one ratio expression, and one `topk` expression.
- Test dashboard variables with normal and edge selections: all instances, a single instance, each `$db` value, and each `$additional_groupby` option.
- Verify metric availability for the expected exporters by checking that panels for raft log GC, raft-engine write/WAL, RocksDB compaction, and block cache all return non-empty series on an active TiKV cluster.
- Inspect rendered units and axes: seconds for histogram latencies, microseconds for RocksDB gauge latencies, bytes/binBps for flow/size panels, percentunit for hit ratios, and right-axis overrides for pending/running/count series.
