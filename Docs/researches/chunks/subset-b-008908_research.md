# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 15658-22524

## Scope

This chunk covers a middle slice of the TiKV details Grafana dashboard JSON. The range begins inside the final target of the `Store batch wait duration` graph and ends inside the first target of `99% Apply log duration per server`, so both boundary panels are partial in this chunk. The complete material visible here includes:

- The tail of the collapsed `Raft Waterfall` row: store writer waterfall latency panels from `Store batch wait duration` through `Store commit and persist duration`.
- The complete collapsed `Raftstore IO` row: paired heatmap and percentile graph panels for raftstore IO reasons such as peer destroy, peer creation, stale merge checks, snapshot reads, v2 learner compatibility, raft term lookup, and raft log fetch.
- The beginning of the collapsed `Raft IO` row: process-ready, store-write-loop, append-log, commit-log, and apply-log latency panels.

The file is dashboard configuration, not executable code. Its effective APIs are Grafana panel schemas, Prometheus expressions, dashboard variables, metric names, labels, and row/panel layout contracts.

## Purpose

This section defines operational visibility for Raftstore write-path and IO latency in TiKV. It turns TiKV Prometheus histogram metrics into Grafana rows that let an operator diagnose where raft work is waiting: request batching, proposal send, store writer queueing, KV DB state writes, Raft Engine writes, leader persistence, commit/persist timing, peer creation/destruction IO, raft log reads, raft append/commit/apply phases, and store write-loop behavior.

The chunk uses two visual idioms repeatedly:

- Heatmap panels show bucket distribution over time with `sum(increase(<histogram>_bucket[$__rate_interval])) by (le)`.
- Graph panels show high percentiles, mean latency, and event rate with `histogram_quantile(0.9999, ...)`, `histogram_quantile(0.99, ...)`, `<sum>/<count>`, and `sum(rate(<count>[$__rate_interval]))`.

Most graph panels set the latency y-axis to seconds and put count series on the second y-axis with a negative transform through the `alias` `/^count/` override. This lets latency and throughput be inspected together without the count line hiding the latency curves.

## Important Dashboard Objects

### Raft Waterfall Tail

The chunk starts in panel `113`, `Store batch wait duration`, with only its final count query and panel footer visible. It then contains complete graph panels `114` through `121`:

- `Store send to write queue duration` uses `tikv_raftstore_store_wf_send_to_queue_duration_seconds`.
- `Store send proposal duration` uses `tikv_raftstore_store_wf_send_proposal_duration_seconds`.
- `Store write kv db end duration` uses `tikv_raftstore_store_wf_write_kvdb_end_duration_seconds`.
- `Store before write duration` uses `tikv_raftstore_store_wf_before_write_duration_seconds`.
- `Store write end duration` uses `tikv_raftstore_store_wf_write_end_duration_seconds`.
- `Store persist duration` uses `tikv_raftstore_store_wf_persist_duration_seconds`.
- `Store commit but not persist duration` uses `tikv_raftstore_store_wf_commit_not_persist_log_duration_seconds`.
- `Store commit and persist duration` uses `tikv_raftstore_store_wf_commit_log_duration_seconds`.

These panels all follow the same four-target pattern: 99.99th percentile, 99th percentile, average from histogram sum/count, and count rate. They group by `$additional_groupby`; unlike the later per-server panels, these waterfall graphs do not add `instance` to the aggregation key in this chunk.

The collapsed row object is titled `Raft Waterfall` and contains the panels as nested `panels` entries. The row itself has no query targets.

### Raftstore IO Row

Collapsed row `122`, `Raftstore IO`, is complete in this chunk. It contains twelve IO reason pairs. Each reason has a heatmap panel using `tikv_raftstore_io_duration_seconds_bucket` and a graph panel using the corresponding bucket/sum/count series filtered by the same `reason` label:

- `peer_destroy_kv_write`: RocksDB write when destroying a peer.
- `peer_destroy_raft_write`: RaftEngine write when destroying a peer.
- `init_raft_state`: raft-state initialization when creating a peer.
- `init_apply_state`: apply-state initialization when creating a peer.
- `entry_storage_create`: RaftEngine read operation when creating a peer.
- `store_check_msg`: checking region state for a message to a non-existent region.
- `peer_check_merge_target_stale`: checking stale merged regions.
- `peer_maybe_create`: RocksDB and RaftEngine reads while creating a peer.
- `peer_snapshot_read`: read requests for peer snapshot work.
- `v2_compatible_learner`: raftstore v2 compatibility checking.
- `raft_term`: reading terms of raft logs from RaftEngine.
- `raft_fetch_log`: fetching raft logs from RaftEngine.

The heatmap side of each pair has one target, `format: "heatmap"`, `legendFormat: "{{le}}"`, `maxDataPoints: 512`, `dataFormat: "tsbuckets"`, hidden zero buckets, and a seconds y-axis. The graph side has four targets: 99.99%, 99%, average, and count. These graph targets group by `instance`, `le` where needed, and `$additional_groupby`, so they preserve per-TiKV-server latency differences.

### Raft IO Row Beginning

Collapsed row `147`, `Raft IO`, begins at line 21053 and is partially included. Complete pairs visible in this chunk are:

- `Process ready duration` and `99% Process ready duration per server`, using `tikv_raftstore_raft_process_duration_secs` filtered by `type="ready"`.
- `Store write loop duration` and `99% Store write loop duration per server`, using `tikv_raftstore_store_write_loop_duration_seconds`.
- `Append log duration` and `99% Append log duration per server`, using `tikv_raftstore_append_log_duration_seconds`.
- `Commit log duration` and `99% Commit log duration per server`, using `tikv_raftstore_commit_log_duration_seconds`.
- `Apply log duration`, a complete heatmap using `tikv_raftstore_apply_log_duration_seconds_bucket`.

Panel `157`, `99% Apply log duration per server`, starts in this chunk but is not complete here. The visible target is the 99.99th percentile query over `tikv_raftstore_apply_log_duration_seconds_bucket` grouped by `instance`, `le`, and `$additional_groupby`; the remaining targets continue after the chunk boundary.

## Query and Control Flow

There is no application control flow, but there is a consistent dashboard data flow:

1. Grafana variables such as `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, and `$__rate_interval` are substituted into PromQL.
2. Prometheus filters TiKV series by Kubernetes cluster, TiDB cluster, and instance regex.
3. Histogram bucket panels either aggregate bucket increases by `le` for heatmaps or aggregate bucket rates by `le` plus grouping labels for `histogram_quantile`.
4. Average lines divide rate of `_sum` by rate of `_count`.
5. Count lines use rate of `_count`, grouped consistently with the panel.
6. Grafana renders nested row panels as collapsed sections, preserving the row-local `gridPos` layout.

The panel order expresses troubleshooting flow more than execution flow. The waterfall panels follow raftstore write progress from scheduling through queueing, proposal, local write, persistence, and commit. The IO row then breaks down specific peer and raftstore maintenance IO reasons. The Raft IO row begins lower-level raft processing timings for ready processing, write-loop work, log append, log commit, and log apply.

## State and Persistence Behavior

The JSON persists dashboard state: panel IDs, row collapse state, layout, legends, query strings, y-axis units, color/heatmap settings, data source references, and target visibility. It does not persist TiKV runtime state.

Runtime state is external:

- TiKV exposes histogram metrics through Prometheus scrape endpoints.
- Prometheus stores bucket, sum, and count time series for the configured retention period.
- Grafana computes rates, increases, quantiles, averages, and visual transformations at query/render time.

Because row objects are `collapsed: true`, their nested panels are persisted inside the row's `panels` array. Tools that flatten or migrate Grafana JSON must preserve nested row panels or the dashboard will lose these views.

## Dependencies and Integration Points

The chunk depends on:

- Grafana's legacy graph and heatmap panel schemas (`type: "graph"` and `type: "heatmap"`), including flot rendering options, row nesting, series overrides, and axis configuration.
- The dashboard data source variable `${DS_TEST-CLUSTER}`.
- Prometheus-compatible PromQL functions: `rate`, `increase`, `sum by`, and `histogram_quantile`.
- TiKV metric names emitted by raftstore instrumentation, including `tikv_raftstore_store_wf_*`, `tikv_raftstore_io_duration_seconds`, `tikv_raftstore_raft_process_duration_secs`, `tikv_raftstore_store_write_loop_duration_seconds`, `tikv_raftstore_append_log_duration_seconds`, `tikv_raftstore_commit_log_duration_seconds`, and `tikv_raftstore_apply_log_duration_seconds`.
- Label contracts for `k8s_cluster`, `tidb_cluster`, `instance`, `reason`, `type`, `le`, and whatever labels are supplied through `$additional_groupby`.

Operationally, this section integrates TiKV raftstore metrics with cluster dashboards used for diagnosing raft latency, peer lifecycle IO, Raft Engine read/write cost, and store-io-pool behavior.

## Risks

- The chunk has partial panels at both boundaries. `Store batch wait duration` and `99% Apply log duration per server` must be reconciled with adjacent chunks before producing the final per-file research document.
- The dashboard uses legacy Grafana panel types and nested collapsed rows. Grafana migrations can change field names or handling of row-contained panels.
- `histogram_quantile` requires preserving `le` in the aggregation key. Dropping `le` would make percentile panels invalid; adding or removing `instance` changes whether a graph is cluster-wide or per-server.
- The average expression divides rate of `_sum` by rate of `_count`; panels do not guard against zero count denominators beyond hiding empty or zero legend values.
- `$additional_groupby` is interpolated directly into `by (...)` clauses. If it is empty or malformed for the deployed Grafana/Prometheus version, queries can fail or group differently than expected.
- Heatmaps aggregate only by `le`, while corresponding graph panels often group by `instance` and `$additional_groupby`. This is intentional for distribution overview versus server-specific percentile detail, but it can surprise operators comparing the two views.
- Metric name or label drift in TiKV instrumentation will silently break affected panels unless dashboard validation or runtime query checks catch it.
- Count series are transformed to negative values on a second y-axis; consumers reading screenshots must understand that downward count curves do not mean negative events.

## Test and Validation Signals

Useful validation for this chunk is dashboard and metric oriented:

- Run JSON validation with `jq` over `tikv_details.json` to confirm the file remains syntactically valid after edits.
- Import the dashboard into a Grafana version supported by the project and verify that collapsed rows `Raft Waterfall`, `Raftstore IO`, and `Raft IO` render nested panels.
- Query a TiKV Prometheus target for each metric family named in this chunk and confirm bucket, sum, and count series exist with the expected labels.
- Validate representative PromQL expressions for each pattern: a waterfall graph, a raftstore IO heatmap, a raftstore IO per-server graph, a raft-process `type="ready"` graph, and an apply-log graph.
- Check that percentile graph legends show 99.99%, 99%, avg, and count series and that count series are assigned to the secondary y-axis.
- Exercise Grafana variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, and `$additional_groupby` with both broad and narrow selections to catch empty result sets and invalid grouping expansions.
