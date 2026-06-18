# sources/storage-engines/tikv/metrics/grafana/tikv_details.dashboard.py lines 1-6725

## Chunk Scope

This chunk covers the imports, dashboard template variables, and the first large run of row-builder functions in `tikv_details.dashboard.py`. It starts with the `common.py`/`grafanalib` dependency setup, defines `Templates()`, and then defines dashboard rows from `Duration()` through most of `RocksDB()`.

The line boundary cuts inside `RocksDB()`: lines through 6722 finish the block-cache-operations row, and line 6725 is the opening `graph_panel(` for the following `Read flow` row. The rest of `RocksDB()` and all later TiKV detail rows belong to later chunks.

## Purpose

This file is a Python generator for the TiKV Details Grafana dashboard. The functions in this chunk return `grafanalib.core.RowPanel` objects populated with Prometheus targets for TiKV health, latency, throughput, scheduler, Raft, GC, coprocessor, in-memory engine, thread, and RocksDB diagnostics.

The code is mostly declarative: each row function constructs a `Layout`, adds rows of `graph_panel`, `heatmap_panel`, `stat_panel`, or histogram helper outputs, then returns `layout.row_panel`. The operational contract is the generated dashboard JSON, not runtime TiKV behavior. Correctness depends on accurate Prometheus metric names, label selectors, legends, units, repeat variables, and row ordering.

## Important APIs, Types, and Functions

- `Templates() -> Templating` defines Grafana variables for `k8s_cluster`, `tidb_cluster`, `db`, `command`, `instance`, `titan_db`, `additional_groupby`, and `optional_quantile`. These variables drive every generated query that uses the default selectors or `$db`/`$command` repeats.
- `Layout` from `common.py` owns Grafana row placement. `layout.row([...])` assigns 24-column grid positions and appends panels to the row; `layout.half_row([...])` creates half-width rows used in GC.
- `target()` from `common.py` converts `Expr`, `OpExpr`, or raw PromQL strings into Grafana `Target` objects. If `additional_groupby=True`, it appends `$additional_groupby` to the PromQL `by (...)` clause and legend.
- `expr_sum`, `expr_avg`, `expr_max`, `expr_sum_rate`, `expr_sum_delta`, `expr_sum_aggr_over_time`, `expr_histogram_quantile`, `expr_histogram_avg`, `expr_operator`, and `expr_topk` build PromQL with default cluster filters: `k8s_cluster`, `tidb_cluster`, and `instance=~"$instance"` unless explicitly skipped.
- `graph_panel_histogram_quantiles()` and `heatmap_panel_graph_panel_histogram_quantile_pairs()` provide common histogram views: heatmap buckets plus quantile/count/avg graph panels.
- `YatpPool()` is the only reusable row-builder defined in this chunk. `UnifiedReadPool()` and `SchedulerWorkerPool()` call it with different pool prefixes and running-task metrics.
- `SchedulerCommands()` and `RocksDB()` use Grafana row repeat behavior: `repeat="command"` and `repeat="db"` respectively.

## Row Builders Covered

- `Duration()` summarizes write-pipeline and coprocessor read latency with optional quantiles.
- `Cluster()` gives top-level storage capacity, CPU, memory, disk I/O, QPS/error rate, leader/region counts, buckets, and uptime.
- `Errors()` groups critical errors, busy signals, raftstore/scheduler/coprocessor/gRPC errors, leader drop/missing, damaged files, and append rejects.
- `Server()` covers CF size, channel full, active written leaders, region size/write distributions, hibernated peers, raftstore memory trace, raft entry cache eviction, address resolution, YATP wait latency, and RocksDB perf read I/O.
- `gRPC()` covers message counts, failures, message duration, batch wait and batch size, request sources, and resource-group QPS.
- `ThreadCPU()` groups thread CPU usage by TiKV subsystem and includes top busy non-RocksDB threads.
- `TTL()` covers TTL expiration, checker progress/actions, compact duration, and poll interval.
- `PD()` covers PD requests, request durations, heartbeats, validation, reconnects, forwarding, and pending TSO requests.
- `IOBreakdown()` covers `tikv_io_bytes`, rate limiter thresholds, and wait duration.
- `RaftWaterfall()`, `RaftstoreIO()`, `RaftIO()`, `RaftPropose()`, `RaftProcess()`, `RaftMessage()`, `RaftAdmin()`, `RaftLog()`, and `LocalReader()` cover Raft write-path timing, IO reasons, proposal/read/write rates, FSM scheduling/polling, message transport, split/admin events, log GC/fetch behavior, and local-reader request counters.
- `Storage()`, `FlowControl()`, `SchedulerCommands()`, `Scheduler()`, `SchedulerWorkerPool()`, and `GC()` cover storage async request timing/errors, full compaction, concurrency manager timestamps, write throttling, scheduler command stages, per-command scheduler details, scheduler memory/pending/running state, YATP scheduler pool behavior, TiDB/TiKV GC, safe points, compaction filter GC, and auto compaction candidate metrics.
- `Snapshot()` and `Task()` cover raft snapshot traffic/actions/durations/sizes/pending applies and worker/future-pool task throughput/backlog.
- `CoprocessorOverview()` and `CoprocessorDetail()` cover coprocessor request duration, errors, scan keys, RocksDB perf, response bytes, memory quota, DAG executor/request counts, scan details by CF, memory-lock checks, semaphore waits, and waiting task counts.
- `InMemoryEngine()` covers in-memory engine operations, RocksDB-vs-IME read throughput, cache hit/miss behavior, memory/region counts, GC/load/eviction/warmup, write/prepare/seek durations, safe point range, and auto load/evict histograms.
- `Threads()` covers OS thread state, thread I/O, and voluntary/nonvoluntary context switch top-k panels.
- `RocksDB()` starts a repeated per-`db` row group and, in this chunk, covers get/seek/write/WAL operations, latency summaries, compaction operations/durations/job file counts, SST read duration, compaction reasons, block cache size, memtable hit rate, block cache byte flow, block cache hit rates, key flow, and block cache operation counts. Subsequent RocksDB rows are outside the chunk.

## Control Flow

There is no conditional runtime flow tied to TiKV state. Each builder follows the same static construction pattern:

1. Create a `Layout(title=...)`, sometimes with `repeat=...`.
2. Call `layout.row()` or `layout.half_row()` with a list of panel objects.
3. Each panel embeds one or more `target()` calls.
4. Each target embeds a PromQL expression built from `common.py` helpers or, rarely, a raw string.
5. Return `layout.row_panel` for later assembly into the full `Dashboard`.

The main dynamic behavior is delegated to Grafana and Prometheus. Grafana resolves template variables such as `$db`, `$command`, `$instance`, `$additional_groupby`, and `$optional_quantile`; Prometheus evaluates the generated expressions over `$__rate_interval` or explicit ranges like `1m` and `30s`.

## State and Persistence Behavior

This chunk has no mutable application state, no persistence, no network I/O, and no direct filesystem writes. Its state is the generated Grafana dashboard schema. The durable output is produced later when the script is rendered to JSON, which is expected to align with `tikv_details.json` and its checksum file.

Template variables act as dashboard-level state from a user perspective: changing `db`, `command`, `instance`, `additional_groupby`, or `optional_quantile` changes query shape and panel cardinality. `repeat="db"` and `repeat="command"` create multiple row instances based on variable values.

## Dependencies

- Local `common.py` supplies the DSL for PromQL expression construction, Grafana target creation, panel creation, units, layout, legends, series overrides, and templating.
- `grafanalib.formatunits` supplies display units such as seconds, bytes IEC, bytes/sec IEC, percent, ops/sec, requests/sec, microseconds, nanoseconds, and ISO timestamps.
- `grafanalib.core` supplies dashboard object types and constants, including `Templating`, `RowPanel`, `GraphThreshold`, `StatValueMappings`, `StatValueMappingItem`, `Dashboard`, `NULL_AS_NULL`, and tooltip/hide constants.
- Prometheus metrics are emitted by TiKV, TiDB clients, PD interactions, node exporters, RocksDB/raft-engine instrumentation, and subsystem-specific workers. The dashboard assumes those metric and label contracts exist.

## Integration Points

- The default selectors in `common.Expr` integrate every generated query with TiDB Cloud/TiKV label dimensions: `k8s_cluster`, `tidb_cluster`, and `instance`.
- `Templates()` provides the variable names used by the generated PromQL, including `$db` for `RocksDB()` and `$command` for `SchedulerCommands()`.
- `additional_groupby=True` is an integration mechanism for optional per-instance drilldown without duplicating panels. It appends `none` or `instance` depending on the template variable value.
- Histogram helpers depend on Prometheus histogram naming conventions: callers pass the base metric without `_bucket`, `_sum`, or `_count`; helpers synthesize those suffixes.
- `skip_default_instance_selector()` is used for TiDB-side GC/config metrics and some safe-point panels where the TiKV `instance` selector would be wrong or too restrictive.
- Series overrides are used where panels combine different scales, for example running compactions/flushes on the right axis and pending raft log fetch tasks on a secondary axis.

## Risks and Edge Cases

- Metric rename or label drift breaks panels silently at dashboard runtime. The highest-risk areas are regex label selectors for thread names, `db="$db"`, `type="$command"`, and detailed RocksDB `type` labels such as percentile names.
- `target(additional_groupby=True)` mutates the expression by appending `$additional_groupby`. Reusing the same `Expr` object across targets would duplicate labels, though this chunk generally creates fresh expressions inline.
- `target()` assumes an `Expr` with `additional_groupby=True` has or receives a non-`None` legend. Expressions with empty `by_labels` rely on explicit legends in this file; missing one can fail string concatenation or produce poor legends.
- Several ratio panels divide by sums that can be zero, including cache hit rates, bloom prefix rate, TTL progress, and in-memory engine hit rate. Prometheus will produce `NaN`/`Inf` rather than a guarded zero.
- Optional quantile panels use `$optional_quantile` in both query and legend. Invalid custom variable values would generate invalid PromQL.
- The chunk contains raw strings and manually assembled label selectors; typos are not caught until rendering or dashboard use. One visible example is `by_labels=["cf", " type"]` in the RocksDB compaction guard panel, where `" type"` includes a leading space.
- Line 6725 opens a row whose contents are outside this chunk. Any analysis of `RocksDB()` must be reconciled with following chunks before a final per-file report.

## Test Signals

- Run the dashboard generation path that produces `tikv_details.json` and compare it with the checked-in JSON/checksum to catch layout, query, and schema drift.
- Import or render the generated `Dashboard` with `grafanalib` to catch Python syntax errors, invalid object fields, missing legend formats for `OpExpr`, and invalid unit constants.
- Snapshot-test representative PromQL strings for default selectors, `skip_default_instance_selector()`, `additional_groupby=True`, optional quantiles, repeated `$db`/`$command` rows, and histogram helper suffix generation.
- Validate that every base histogram metric passed to `expr_histogram_quantile()` or `expr_histogram_avg()` omits `_bucket`, `_sum`, and `_count`, matching the helper assertions.
- Lint or query-check label names in `by_labels`, especially the RocksDB `["cf", " type"]` case and high-cardinality additions from `$additional_groupby`.
- Runtime dashboard smoke tests should exercise template combinations: all instances, a single instance, all DBs, one DB, all commands, one command, and `additional_groupby=instance`.
- Prometheus-side tests should verify key panels return data for a sample TiKV deployment: cluster capacity, gRPC duration, scheduler command repeat rows, GC safe points, in-memory engine panels when enabled, and RocksDB repeated rows.
