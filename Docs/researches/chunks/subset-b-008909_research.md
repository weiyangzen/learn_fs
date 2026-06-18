# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 22525-30293

## Scope and Purpose

This chunk is a contiguous slice of the TiKV Details Grafana dashboard JSON. It contains the tail of a Raft IO/apply-log panel, then complete collapsed rows for Raft IO, Raft Propose, Raft Process, Raft Message, and most of Raft Admin before ending inside the first Raft log GC panel. The file is declarative dashboard configuration rather than executable code, so the important "APIs" are Grafana panel fields, Prometheus query expressions, dashboard variables, and the TiKV metric names those expressions depend on.

The slice focuses on diagnosing TiKV Raftstore behavior: Raft client wait-ready latency, store write blocking, proposal rates and wait times, apply/store FSM scheduling and polling, unpersisted-apply state, Raft message throughput/drop/latency, admin command activity, split/load-base-split behavior, flashback-state peers, and the start of raft-log-GC write latency.

## Dashboard Structure and Panels

- The chunk starts mid-panel with `99% Apply log duration per server`, using `tikv_raftstore_apply_log_duration_seconds_*` to show p99, hidden average, and hidden count by `instance` plus `$additional_groupby`.
- `Raft IO` row includes `Raft Client Wait Connection Ready Duration`, `99% Raft Client Wait Connection Ready Duration`, `Store io task reschedule`, and `Write task block duration per server $optional_quantile`.
- `Raft Propose` row includes proposal count and latency panels: `Raft proposals per ready`, `Raft read/write proposals`, read/write proposals per server, propose wait heatmap and p99/p99.99 graph, store write wait heatmap and percentile graph, apply wait heatmap and percentile graph, store-write handle duration, write trigger size, propose-log throughput, and perf-context duration.
- `Raft Process` row includes ready handling, max raftstore event duration, replica-read lock-check duration, FSM reschedules, store/apply FSM schedule wait, store/apply FSM poll duration, store/apply FSM poll rounds, store/apply FSM count per poll, peer/apply message length distributions, unpersisted-apply region count, and apply-ahead-of-persistence log count.
- `Raft Message` row includes sent, flushed, received, accepted-by-type, vote, and dropped-message panels, plus send-wait and receive-delay heatmaps and p99/p99.99 graphs.
- `Raft Admin` row includes admin proposals, admin apply, split-check count and duration, load-base split event/duration, observed CPU/QPS/read bytes for load-base split decisions, peer flashback-state count, and begins `Raft log GC write duration`.

Panel layout is Grafana's legacy graph/heatmap schema. Repeated fields include `gridPos`, `id`, `legend`, `seriesOverrides`, `tooltip`, `xaxis`/`yaxes` or heatmap `xAxis`/`yAxis`, `nullPointMode: "null as zero"`, and `${DS_TEST-CLUSTER}` datasource binding. Most graph legends are configured as right-side tables sorted by `max` descending with empty and zero series hidden.

## Important Query Patterns

- Histogram heatmaps use `sum(increase(<metric>_bucket{...}[$__rate_interval])) by (le)` and set `format: "heatmap"` with `dataFormat: "tsbuckets"` in heatmap panels.
- Percentile graphs use `histogram_quantile(...)` over `sum(rate(<metric>_bucket{...}[$__rate_interval])) by (..., le, $additional_groupby)`. Fixed quantiles include `0.99`, `0.9999`, `0.999999`, `1`, and `0.8`; several panels use `$optional_quantile`.
- Average overlays divide rate of `_sum` by rate of `_count`, usually hidden or styled with a filled line. Count overlays use `_count` and are frequently hidden or transformed to negative Y on the second axis.
- Counter/rate panels use `sum(rate(...[$__rate_interval])) by (...)`. Gauge-like panels use direct `sum((metric{...})) by (...)`, and load-base split events use `sum(delta(tikv_load_base_split_event[1m]))`.
- Every query filters by `k8s_cluster="$k8s_cluster"`, `tidb_cluster="$tidb_cluster"`, and usually `instance=~"$instance"`. Several panels add label filters such as `type="ready"`, `type="send_wait"`, `type="receive_delay"`, `type=~"local_read|normal|read_index"`, `type!=="compact"` is not used; the actual PromQL filter is `type!="compact"`.
- `$additional_groupby` is injected into many `by (...)` clauses and legend templates. This is the main integration knob for drilling into extra labels, but it must expand to a syntactically valid group-by list for every affected PromQL expression.

## Metrics Covered

The chunk references these TiKV metrics:

- Raft IO and apply/write path: `tikv_raftstore_apply_log_duration_seconds_*`, `tikv_server_raft_client_wait_ready_duration_*`, `tikv_raftstore_io_reschedule_region_total`, `tikv_raftstore_io_reschedule_pending_tasks_total`, `tikv_raftstore_store_write_msg_block_wait_duration_seconds_bucket`.
- Proposal path: `tikv_raftstore_apply_proposal_bucket`, `tikv_raftstore_proposal_total`, `tikv_raftstore_request_wait_time_duration_secs_*`, `tikv_raftstore_store_write_task_wait_duration_secs_*`, `tikv_raftstore_apply_wait_time_duration_secs_*`, `tikv_raftstore_store_write_handle_msg_duration_secs_bucket`, `tikv_raftstore_store_write_trigger_wb_bytes_bucket`, `tikv_raftstore_propose_log_size_sum`, `tikv_raftstore_apply_perf_context_time_duration_secs_bucket`, `tikv_raftstore_store_perf_context_time_duration_secs_bucket`.
- Raft process/FSM path: `tikv_raftstore_raft_ready_handled_total`, `tikv_raftstore_raft_process_duration_secs_count`, `tikv_raftstore_event_duration_bucket`, `tikv_broadcast_normal_duration_seconds_bucket`, `tikv_replica_read_lock_check_duration_seconds_bucket`, `tikv_batch_system_fsm_reschedule_total`, `tikv_batch_system_fsm_schedule_wait_seconds_bucket`, `tikv_batch_system_fsm_poll_seconds_bucket`, `tikv_batch_system_fsm_poll_rounds_bucket`, `tikv_batch_system_fsm_count_per_poll_bucket`, `tikv_raftstore_peer_msg_len_bucket`, `tikv_raftstore_apply_msg_len_bucket`, `tikv_raft_enable_unpersisted_apply_regions`, `tikv_raft_apply_ahead_of_persist_bucket`.
- Raft messaging: `tikv_raftstore_raft_sent_message_total`, `tikv_server_raft_message_flush_total`, `tikv_server_raft_message_recv_total`, `tikv_raftstore_raft_dropped_message_total`, `tikv_server_raft_message_duration_seconds_*`.
- Admin/split/flashback/log-GC path: `tikv_raftstore_admin_cmd_total`, `tikv_raftstore_check_split_total`, `tikv_raftstore_check_split_duration_seconds_bucket`, `tikv_load_base_split_event`, `tikv_load_base_split_duration_seconds_*`, `tikv_load_base_split_region_load_*`, `tikv_raftstore_peer_in_flashback_state`, and `tikv_raftstore_raft_log_gc_write_duration_secs_*`.

## Control Flow and Observability Model

Grafana evaluates this JSON by row and panel. Collapsed row panels are stored inside the row object's `panels` array; when a row is expanded in Grafana, each child panel runs its PromQL targets against the selected Prometheus datasource and dashboard variables. There is no application control flow in the JSON itself, but there is an implicit diagnostic flow:

1. Raft IO panels surface whether raft log application, raft-client connection readiness, IO rescheduling, or store-write blocking are introducing latency.
2. Raft Propose panels break client-facing Raft work into proposal volume, read/write mix, request wait time, store write wait, apply wait, write message handling, write batch trigger size, proposed log throughput, and RocksDB perf-context latency.
3. Raft Process panels distinguish ready processing, batch-system scheduling, poll duration, poll rounds, message batch sizes, and unpersisted-apply lag. These panels help identify scheduler saturation versus Raftstore execution cost.
4. Raft Message panels isolate network/transport behavior: send/flush/receive rate, message type mix, vote churn, explicit dropped messages, local send wait, and receiver-reported receive delay.
5. Raft Admin panels track control-plane actions that can explain workload shifts: conf-change/transfer-leader proposals, admin apply commands, split checks, load-base split events and decision inputs, flashback-state peers, and raft-log-GC write latency.

The panels intentionally combine heatmaps for distribution shape with percentile/average/count graphs for per-instance attribution. This makes the dashboard useful for first seeing a cluster-wide tail and then drilling down to the responsible TiKV instance or label group.

## State and Persistence Behavior

The JSON persists dashboard state only: panel IDs, grid placement, row collapse state, legend preferences, axis units, datasource references, query strings, and variable placeholders. It does not persist TiKV runtime state. The observed state is pulled from Prometheus time series produced by TiKV and selected through dashboard variables.

Several panels encode persistence-related semantics indirectly:

- `tikv_raft_enable_unpersisted_apply_regions` reports regions applying unpersisted raft logs.
- `tikv_raft_apply_ahead_of_persist_bucket` reports the raft-log gap between applied and persisted indexes.
- `tikv_raftstore_raft_log_gc_write_duration_secs_*`, visible at the end of the chunk, monitors write latency for raft log GC state changes.
- Proposal, store-write, apply-wait, and raft-ready panels together expose where durable Raft progress is delayed.

Because Prometheus queries use `rate`, `increase`, and `delta`, the dashboard depends on scrape continuity and monotonically increasing counter semantics. Counter resets, missing scrapes, or label cardinality changes will directly affect panel continuity.

## Dependencies and Integration Points

- Grafana legacy panel model: `graph`, `heatmap`, collapsed `row`, `seriesOverrides`, `legend`, and axis/tooltip fields.
- Prometheus datasource `${DS_TEST-CLUSTER}` and Grafana interval variable `$__rate_interval`.
- Dashboard variables: `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, and `$optional_quantile`.
- TiKV metric exporters for raftstore, server raft messaging, batch system, replica read, broadcast, and load-base split metrics.
- TiKV operational workflows: Raft proposal/read-index debugging, apply/write path latency analysis, batch system/FSM scheduling, raft transport diagnosis, admin/split diagnosis, flashback monitoring, and raft log GC diagnosis.

## Risks and Edge Cases

- Query syntax is sensitive to `$additional_groupby`. If it expands to an empty value or includes a leading/trailing comma in the wrong context, PromQL `by (...)` clauses can fail or produce unexpected grouping.
- High-cardinality groupings on `instance`, `to`, `type`, `reason`, and `$additional_groupby` can make histogram quantiles expensive, especially p99.99/p99.9999-style panels over bucket metrics.
- Some panel descriptions are inaccurate or typo-prone. `Store io task reschedule` says "throughput of disk write per IO type" but queries reschedule counters; `Apply fsm schedule wait duration` has a trailing `e`; `Perf Context duration` repeats a proposal-rate description; and `Store io task reschedule` legend uses `rechedule`.
- Several graphs set `nullPointMode` to `null as zero`. Missing series can look like true zeros, which is useful for quiet panels but risky during scrape gaps.
- `histogram_quantile(1, ...)` for apply-ahead-of-persistence approximates the top bucket boundary, not an exact maximum. Operators should not treat it as a precise per-region max.
- `sum(delta(tikv_load_base_split_event[1m]))` can show negative or confusing values around counter resets if the metric behaves like a counter rather than an event gauge.
- Unit handling is mixed: CPU millicores are divided by `1000`, read bytes are described as KiB, proposal speed uses bytes/sec, and many count overlays are hidden or on a secondary axis. Incorrect axis units can lead to false comparisons between panels.
- The file chunk ends inside the `Raft log GC write duration` panel, so any following targets or panels must be reconciled from the next chunk before producing the final per-file report.

## Test Signals

Since this is dashboard JSON, useful validation is configuration and query validation rather than unit testing:

- Parse the full `tikv_details.json` as JSON and ensure this chunk remains structurally nested under the intended row/panel objects after edits.
- Use Grafana dashboard import or provisioning validation to catch invalid legacy panel fields, duplicate panel IDs, bad row nesting, and datasource variable issues.
- Run Prometheus `api/v1/query` or `promtool`-style checks against representative expressions after variable substitution, especially expressions containing `$additional_groupby` and `$optional_quantile`.
- Verify all referenced metric names still exist in TiKV's metrics registry/exported `/metrics` output; missing `_bucket`, `_sum`, or `_count` siblings will break percentile or average panels.
- Exercise dashboard variable combinations: no extra group-by, grouping by `instance`, grouping by message/admin `type`, and a filtered `$instance` regex.
- Visually smoke-test the heatmaps and graph legends in Grafana with a live cluster to ensure bucket formats, axis units, hidden average/count overlays, and negative-Y count transforms render as intended.

## Cross-Chunk Notes

This work item starts in the middle of the preceding Raft IO/apply-log panel and ends in the middle of the Raft Admin `Raft log GC write duration` panel. The final merged per-file research should combine this analysis with adjacent chunks to recover the complete row context, preceding panel IDs, the remainder of the log-GC panel, later Raft Admin panels, dashboard templating definitions, and top-level dashboard metadata.
