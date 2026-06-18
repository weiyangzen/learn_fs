# sources/storage-engines/tikv/metrics/grafana/tikv_details.dashboard.py lines 6726-11011

## Scope

This chunk covers the final large segment of TiKV's generated Grafana details dashboard definition. It starts in the latter part of `RocksDB()` at the "Read flow" panel and continues through the remaining row-panel factory functions plus the final `Dashboard(...)` assembly.

Functions wholly or partially covered here:

- tail of `RocksDB()` from read/write flow panels through write-stall and memtable panels;
- `RaftEngine()`;
- `Titan()`;
- `PessimisticLocking()`;
- `PointInTimeRestore()`;
- `ResolvedTS()`;
- `Memory()`;
- `BackupImport()`;
- `Encryption()`;
- `BackupLog()`;
- `SlowTrendStatistics()`;
- `StatusServer()`;
- `ResourceControl()`;
- `LoadShedding()`;
- `TikvConfig()`;
- the final `dashboard = Dashboard(...).auto_panel_ids()` object.

The code is declarative dashboard construction rather than TiKV runtime logic. Each function creates a `Layout`, appends Grafana rows with panel helper calls, and returns `layout.row_panel`.

## Purpose

- Define the lower half of the `Test-Cluster-TiKV-Details` Grafana dashboard used to observe TiKV engine internals, transaction lock behavior, backup/import tools, log backup, resource control, status API, encryption, and config surfaces.
- Encode Prometheus queries, panel titles, legends, units, row grouping, stat value mappings, and final dashboard ordering in Python/grafanalib form.
- Keep the dashboard close to TiKV metric names so dashboard generation fails or produces visibly broken panels when metric contracts drift.
- Provide specialized views for operational diagnosis: RocksDB read/write/compaction flow and stalls, raft-engine WAL behavior, Titan blob storage, pessimistic-lock wait/deadlock behavior, PITR/import and backup throughput, resolved-ts health, allocator behavior, log backup checkpoint lag, load shedding, and static TiKV configuration gauges.

## Important APIs, Types, And Functions

- `Layout` is the local dashboard-row builder imported from `common`. Every function in this chunk instantiates `Layout(title=...)`, optionally with `repeat="titan_db"` in `Titan()`, then calls `layout.row([...])`.
- `graph_panel`, `graph_panel_histogram_quantiles`, `heatmap_panel`, `stat_panel`, and `table_panel` create Grafana panels. The chunk uses graph panels for time series, heatmaps for Prometheus histogram buckets, stat panels for current log-backup status, and table panels for config metrics.
- `target(...)` wraps Prometheus expressions and per-series metadata such as `legend_format`, `hide`, and `additional_groupby`.
- PromQL expression helpers include `expr_simple`, `expr_sum`, `expr_avg`, `expr_max`, `expr_min`, `expr_sum_rate`, `expr_count_rate`, `expr_sum_delta`, `expr_sum_increase`, `expr_sum_aggr_over_time`, `expr_histogram_quantile`, `expr_operator`, and `expr_topk`. They are the main abstraction that keeps label selectors and aggregate labels consistent across panels.
- `yaxes(...)` and `yaxis(...)` bind Grafana units from `grafanalib.formatunits` such as bytes, bytes/sec, seconds, microseconds, milliseconds, ops/sec, percent, date-time, and short numeric formats.
- `OPTIONAL_QUANTILE_INPUT` is interpolated into several titles and legends for panels whose histogram quantile can be chosen from the dashboard variable defined earlier in the file.
- `StatValueMappings` and `StatValueMappingItem` map log-backup status gauge values to readable states: endpoint disabled/enabled and task running/paused/error.
- `series_override(...)` is used in the log-backup checkpoint panel to render the synthetic current-time series as a dashed reference line.
- `Dashboard(...)` sets dashboard metadata and composition: title `Test-Cluster-TiKV-Details`, UID `RDVQiEzZz`, browser timezone, one-minute refresh, datasource input, `Templates()`, ordered panel list, schema version 14, and shared-crosshair graph tooltip.

## Panel Coverage

The `RocksDB()` tail covers engine read/write and storage health: `tikv_engine_flow_bytes`, `tikv_engine_estimate_num_keys`, `tikv_engine_compaction_flow_bytes`, `tikv_engine_bytes_per_read`, `tikv_engine_bytes_per_write`, `tikv_engine_read_amp_flow_bytes`, `tikv_engine_pending_compaction_bytes`, snapshot count and oldest snapshot duration, compression ratios, files per level, ingest-SST duration and picked level, RocksDB block-read perf counters, write-stall reasons/durations, stall condition changes, and memtable size.

`RaftEngine()` covers raft-engine operations, write/read/message rates, write duration and breakdowns, WAL sync/allocation/rotation duration, write size, rewrite flow, log/swap/recycle file counts, entry count, purge/read durations, and write compression ratio. It uses both fixed 0.999 quantiles and optional 0.99-style quantiles.

`Titan()` repeats per `$titan_db` and covers TitanDB blob-file count/size, blob cache size and hit ratio, iterator-touched blob-file count, blob key/value sizes, blob get/seek/next/prev durations, blob locate operation rates, discardable ratio distribution, blob key/byte flow, blob file read/write/sync durations, blob GC action/duration/input/output sizes, GC key/byte flow, and GC file count.

`PessimisticLocking()` covers lock-manager CPU, handled tasks, waiter lifetime, wait-table status, lock-wait queue entries, deadlock detection duration and errors, detector leader heartbeat, pessimistic lock memory, in-memory pessimistic-lock results, active keys/waiters, wait queue length heatmap, and in-memory scan-lock read duration.

`PointInTimeRestore()` focuses on PITR apply/import paths: SST worker CPU, apply RPC duration, download/apply engine breakdown, apply RPC ops/counts, cache events, RPC and apply heatmaps, queuing/concurrency/apply time, throughput, applier speed, cached bytes, unfinished engine requests, and raftstore memory usage during apply.

`ResolvedTS()` covers resolved-ts/advance-ts/scan-lock worker CPU, gaps between resolved/safe timestamps and wall-clock time, region IDs with minimal resolved/safe timestamps, check-leader duration/request size/item count, failed advancement reasons and stale-peer checks, lock heap bytes, initial scan backoff, observe-region status, and pending command bytes.

`Memory()` covers allocator statistics, net allocation rate per thread (`alloc - dealloc`), allocated/released rates, mapped allocation, and arena count.

`BackupImport()` combines backup, import, checksum, and cloud-request views: backup CPU/thread count/errors, SST size and duration histograms, SST generation throughput, external storage creation, checksum/analyze duration, node disk IO utilization, import CPU/thread/errors, import RPC duration/rates/counts, download/read/rewrite/ingest heatmaps, download throughput, local write keys/bytes, TTL expired count, and cloud request rate.

`Encryption()` covers encryption data keys, encrypted file count, initialization flag, meta file size, coprocessor RocksDB encryption/decryption nanos, and encryption metadata read/write duration.

`BackupLog()` is the largest single section. It covers endpoint/task/owner status, recent flush file/size stats, average flush size, log-backup CPU, handle event rate, initial scan throughput, checkpoint lag, event memory, observed regions, retryable/fatal errors, checkpoint TS versus current time, flush/initial-scan/convert/resolve durations, command batch sizes, temp-file save/write/syscall durations, internal actor message rates/durations, initial scan RocksDB throughput/operations, initial scan reason/status, temp buffer memory/file/swap metrics, advancer batch/tick durations, region checkpoint request failures/results, current last region/checkpoint/store state, active subscriptions, and advancer operation counts.

`SlowTrendStatistics()`, `StatusServer()`, `ResourceControl()`, `LoadShedding()`, and `TikvConfig()` provide smaller operational sections for slow-store detection, status API latency/rate, resource-control/analyze metrics, admission/load-shedding behavior, and table views of TiKV config gauges.

## Control Flow

The runtime flow of the Python script is straightforward:

1. Import grafanalib types, format units, and local `common` helpers.
2. Define row-panel factory functions. The functions are not executed until the final `Dashboard` object is built.
3. Inside each factory, instantiate a `Layout`.
4. Call `layout.row([...])` repeatedly with panel objects. Each panel contains one or more `target()` objects, and each target contains a PromQL string or an expression-builder object.
5. Return `layout.row_panel`.
6. Build `dashboard = Dashboard(...)` at module import/execution time. The `panels=[...]` list calls every row-panel factory in the intended dashboard order, including functions defined before this chunk and functions defined in this chunk.
7. Call `.auto_panel_ids()` to assign Grafana panel IDs after all row panels are assembled.

There are no loops in this chunk except implicit iteration inside helper calls and Grafana rendering. Branching is limited to PromQL expression composition through helpers such as `.extra(" > 0")`, `expr_operator(a, "/", b)`, and stat value mappings.

## State And Persistence Behavior

- The Python code itself stores no TiKV runtime state and writes no TiKV data. Its only stateful local objects are transient `Layout`, panel, target, and `Dashboard` Python objects created while generating the Grafana dashboard JSON.
- Persistence impact is indirect: this file defines the persisted dashboard artifact when the dashboard generator is run. Generated JSON panel IDs, row order, query strings, and template references become part of the operational monitoring surface.
- The panels observe persistent TiKV subsystems such as RocksDB, raft engine, Titan blob files, backup/import files, log backup checkpoints, and configuration gauges, but they do not mutate those systems.
- `Dashboard(...).auto_panel_ids()` makes panel identity generation dependent on the final ordered panel tree. Reordering, adding, or removing row panels changes generated IDs and may affect Grafana links/alerts if any external artifact depends on panel IDs.
- `TikvConfig()` table panels expose config metrics as Prometheus samples. They do not read TiKV config files directly; they depend on TiKV exporting config gauge labels.

## Dependencies And Integration Points

- Depends on `metrics/grafana/common.py` helper functions for PromQL generation, datasource input handling, panel construction, templating, grouping, and axes. The correctness of `additional_groupby=True`, label selectors, histogram helpers, and `.extra(...)` suffix behavior is delegated to this module.
- Depends on `grafanalib.core` for `Dashboard`, `RowPanel`, `Templating`, stat value mappings, tooltip mode, null-point handling, and visibility constants.
- Depends on `grafanalib.formatunits` for all Grafana unit strings. Incorrect units do not break Prometheus queries but make panels misleading.
- Depends on templates defined earlier in this file: `$db`, `$titan_db`, `$instance`, `$additional_groupby`, `$optional_quantile`, `$k8s_cluster`, and `$tidb_cluster`. Many expressions in this chunk interpolate `db="$db"` or `db="$titan_db"` directly.
- Integrates with Prometheus metric names exported by TiKV, TiDB log-backup advancer, and node exporter. Examples include `tikv_engine_*`, `raft_engine_*`, `tikv_lock_manager_*`, `tikv_import_*`, `tikv_resolved_ts_*`, `tikv_log_backup_*`, `tidb_log_backup_*`, `tikv_resource_control_*`, `tikv_status_server_*`, and `node_disk_io_time_seconds_total`.
- Integrates with Grafana dashboard consumers rather than TiKV production code. The final dashboard is usually rendered to JSON by the repository's dashboard tooling and then imported into Grafana.
- The final `panels=[...]` ordering integrates functions from the whole file: earlier overview/raftstore/scheduler/read-pool/GC/task sections plus the chunk-defined engine/tool/debug/infrequent/config sections.

## Risks And Edge Cases

- Metric rename or label drift is the primary risk. The code hard-codes many metric names and labels such as `db`, `type`, `cf`, `level`, `instance`, `request`, `stage`, `resource_group`, and `is_background`; any exporter change can silently produce empty panels.
- Template coupling is tight. `Titan()` requires the hidden `titan_db` variable, and RocksDB panels require `$db`. If template queries stop returning values, repeated rows or db-filtered panels disappear.
- `additional_groupby=True` relies on the `common` helper to merge an optional dashboard grouping label into PromQL. A helper regression can affect many panels at once.
- Some panels intentionally override default instance grouping with `by_labels=[]`. That gives cluster-wide totals/averages but can hide per-instance skew if copied into a diagnosis that needs instance-level detail.
- Several PromQL ratios can divide by zero or produce missing/NaN series: RocksDB read amplification, Titan blob-cache hit ratio, backup average flush size, and checkpoint lag expressions with post-filtered timestamps.
- Heatmap panels require `_bucket` metrics with stable bucket label semantics. Supplying a base histogram metric to `heatmap_panel` or changing buckets in exporters would break visual distributions.
- Histogram quantile panels depend on bucket cardinality and label grouping. Adding high-cardinality labels to metrics can make panels expensive, especially in Titan, backup/import, log backup, and resolved-ts sections.
- The chunk mixes fixed quantiles, optional quantiles, histogram averages, rates, deltas, and increases. Using `delta` on counters over short windows can show resets/reboot artifacts; some log-backup stat descriptions explicitly warn that values may reduce after TiKV reboot.
- There are a few text-quality issues that do not affect functionality but can reduce operator clarity, such as typos in panel titles/descriptions (`durtion`, `Subscrption`, "summered") and duplicate or swapped-looking labels in Titan blob file read/write duration panels where 99/95 selector labels are paired with 95/99 legends.
- `schemaVersion=14` is deliberately kept at or above the Grafana threshold for shared crosshair/tooltips. Lowering it can break the intended tooltip behavior.
- Panel ID stability depends on `auto_panel_ids()` and the ordered panel list. Merge conflicts or out-of-order insertion can produce a dashboard that renders but changes panel IDs unexpectedly.
- Table config panels use raw config gauges. Label cardinality or string-like labels can make tables wide, and the fallback expression for RocksDB CF config (`tikv_config_rocksdb unless tikv_config_rocksdb_cf`) assumes exporter compatibility behavior.

## Test Signals

- The most direct validation is running the repository's Grafana dashboard generation path for `tikv_details.dashboard.py` and confirming it imports without Python exceptions and emits valid Grafana JSON.
- Generated JSON should be checked for non-empty row panels for every function in this chunk, stable panel IDs after `.auto_panel_ids()`, and presence of the expected dashboard UID/title/schema/tooltips.
- Static checks can parse generated targets and verify that every PromQL expression is syntactically valid, especially expressions assembled with `expr_operator(...)`, `.extra(...)`, regex label selectors, and `time() * 1000` checkpoint computations.
- A Prometheus-backed smoke test should load the dashboard against a TiKV test cluster and verify representative panels return data for RocksDB, raft engine, backup/import, resolved-ts, log backup, resource-control, and config metrics.
- Metric-contract tests should spot-check important metric names in TiKV exporters against dashboard references: `tikv_engine_flow_bytes`, `raft_engine_write_duration_seconds`, `tikv_engine_titandb_num_live_blob_file`, `tikv_lock_manager_waiter_lifetime_duration`, `tikv_import_rpc_duration`, `tikv_resolved_ts_min_resolved_ts_gap_millis`, `tikv_log_backup_enabled`, `tidb_log_backup_last_checkpoint`, and `tikv_config_rocksdb_db`.
- Visual review should verify units and legends: bytes versus bytes/sec, seconds versus microseconds, ops/sec versus counts, date-time checkpoint panels, hidden import thread targets, stat value mappings, and dashed current-time series override.
- Regression tests for this chunk should compare generated dashboard JSON before/after changes while allowing intentional panel additions. Unintended changes to row order, repeated row variables, template references, or panel IDs are important review signals.
