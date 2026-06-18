# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 60536-68613

## Scope and Purpose

This chunk is a contiguous slice of the TiKV Details Grafana dashboard JSON. It starts inside the `GC scan write details` panel and continues through the rest of the visible GC/auto-compaction panels, the complete `Pessimistic Locking`, `Task`, `PD`, `Slow Trend Statistics`, and `Snapshot` rows, then enters the `Resolved TS` row and ends at the beginning of the `Max gap of resolved-ts in region leaders` panel. The file is declarative Grafana dashboard configuration, so the important interfaces are panel objects, row nesting, Prometheus expressions, Grafana dashboard variables, and TiKV metric names.

Operationally, this chunk covers observability for several TiKV subsystems:

- GC and auto compaction: GC scan keys by CF, auto-compaction latency, candidate counts, tombstone/discardable-version distributions, MVCC versions scanned, and compaction score.
- Pessimistic locking: lock-manager worker CPU, handled tasks, waiter lifetime, wait-table and wait-queue gauges, deadlock detection, detector leadership, pessimistic-lock memory, in-memory lock result rates, queue length heatmap, and MVCC scan-lock read duration.
- Generic task pools: worker and future-pool handled/pending task panels.
- PD client behavior: request counts, average request duration, heartbeats, peer validation, reconnects, forward status, and pending TSO requests.
- Slow-store trend signals: raftstore inspect duration, store slow score, disk probe duration, slow trend, QPS trend, sampling latency, and current QPS by instance.
- Snapshot path: snapshot message rate, state counts, generation/apply wait, handle duration, p99.99 size/KV count, snapshot actions, transport/generate speed, and pending applies.
- Resolved TS start: worker CPU and the first gap/region panels for resolved-ts and follower safe-ts.

## Dashboard Structure and Panels

The chunk uses the legacy Grafana `graph`, `heatmap`, and collapsed `row` schema. Most graphs use `${DS_TEST-CLUSTER}` as datasource, `renderer: "flot"`, `nullPointMode: "null as zero"`, right-side legend tables sorted by `max`, and `hideEmpty`/`hideZero` enabled. The dashboard variables repeated in nearly every PromQL target are `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$__rate_interval`, `$additional_groupby`, and, for selected percentile panels, `$optional_quantile`.

Panel coverage in this slice:

- GC tail and auto compaction:
  - `GC scan write details` and `GC scan default details` query `tikv_gcworker_gc_keys` for `cf="write"` and `cf="default"`, grouped by `key_mode`, `tag`, and `$additional_groupby`.
  - `Auto Compaction Duration` has p99.99, p99, average, and count targets over `tikv_auto_compaction_duration_seconds_*`, grouped by `type`.
  - `Auto Compaction Regions Status` directly sums `tikv_auto_compaction_regions_meet_threshold` and `tikv_auto_compaction_pending_candidates` by `instance`.
  - `Auto Compaction Num Tombstones`, `Auto Compaction Num Discardable`, `Auto Compaction MVCC Versions Scanned`, and `Auto Compaction Score` repeat the p99.99/p99/avg/count histogram pattern over their corresponding `_bucket`, `_sum`, and `_count` metrics.
- `Pessimistic Locking` row:
  - `Lock Manager Thread CPU` tracks `waiter_manager.*` and `deadlock_detect.*` thread CPU with `tikv_thread_cpu_seconds_total`.
  - `Lock Manager Handled tasks` uses `tikv_lock_manager_task_counter` by `type`.
  - `Waiter lifetime duration` and `Deadlock detect duration` use p99.99, p99, average, and count targets over lock-manager duration histograms.
  - `Lock Waiting Queue` compares `tikv_lock_manager_wait_table_status` and `tikv_lock_wait_queue_entries_gauge_vec` using `max_over_time(...[30s])`.
  - `Detect error`, `Deadlock detector leader`, `Total pessimistic locks memory size`, `In-memory pessimistic locking result`, and `Pessimistic lock activities` expose error counters, detector leadership heartbeat, memory gauge, result rates, and active key/waiter gauges.
  - `Lengths of lock wait queues when transaction enqueues` is the only heatmap in this chunk; it uses `sum(increase(tikv_lock_wait_queue_length_bucket[$__rate_interval])) by (le)`.
  - `In-memory scan lock read duration` uses histogram percentiles, average, and count over `tikv_storage_mvcc_scan_lock_read_duration_seconds_*`, grouped by `type`.
- `Task` row:
  - `Worker handled tasks` and `Worker pending tasks` expose `tikv_worker_handled_task_total` rates and `tikv_worker_pending_task_total` gauges by worker `name`.
  - `FuturePool handled tasks` and `FuturePool pending tasks` mirror the worker panels with `tikv_futurepool_handled_task_total` and `tikv_futurepool_pending_task_total`; pending future-pool tasks use `avg_over_time(...[1m])`.
- `PD` row:
  - `PD requests` and `PD request duration (average)` use `tikv_pd_request_duration_seconds_count` and `_sum/_count` average by request `type`.
  - `PD heartbeats` combines `tikv_pd_heartbeat_message_total` rates with direct pending heartbeat gauge `tikv_pd_pending_heartbeat_total`.
  - `PD validate peers`, `PD reconnection`, `PD forward status`, and `Pending TSO Requests` query peer validation counters, reconnect deltas, forwarding status, and TSO queue gauges.
- `Slow Trend Statistics` row:
  - `Inspected duration per server` and `Disk Probe Duration` use `$optional_quantile` over raftstore inspect and disk probe histograms.
  - `Store Slow Score`, `Slow Trend`, `QPS Changing Trend`, `AVG Sampling Latency`, and `QPS of each store` directly sum slow-score/trend gauge metrics by `instance`.
- `Snapshot` row:
  - `Rate snapshot message` uses a 1-minute `delta` of `tikv_raftstore_raft_sent_message_total{type="snapshot"}`.
  - `Snapshot state count` combines `tikv_raftstore_snapshot_traffic_total` and `tikv_pending_delete_ranges_of_stale_peer`.
  - `Snapshot generation/apply wait duration $optional_quantile` and `Handle snapshot duration $optional_quantile` use histogram quantiles over generation, apply, send, and snapshot duration buckets.
  - `99.99% Snapshot size` and `99.99% Snapshot KV count` use fixed p99.99 quantiles.
  - `Snapshot Actions` uses 1-minute deltas for `tikv_raftstore_snapshot_total`, `tikv_raftstore_clean_region_count`, and `tikv_server_snapshot_task_total`.
  - `Snapshot transport speed` measures `tikv_snapshot_limit_transport_bytes` for non-send transport types and `tikv_snapshot_limit_generate_bytes` for `type=~"io"`.
  - `Snapshot pending applies` directly displays `tikv_raftstore_snapshot_pending_applies`.
- `Resolved TS` row start:
  - `Resolved TS Worker CPU`, `Advance ts Worker CPU`, and `Scan lock Worker CPU` use `tikv_thread_cpu_seconds_total` filtered by thread-name regexes `resolved_ts.*`, `advance_ts.*`, and `inc_scan.*`.
  - `Max gap of resolved-ts`, `Min Resolved TS Region`, `Max gap of follower safe-ts`, and `Min Safe TS Follower Region` display resolved-ts/safe-ts lag and region gauges by `instance`.
  - The chunk ends just as `Max gap of resolved-ts in region leaders` begins, so only its title/description and opening object fields are visible in this work item.

## Important Query Patterns and Data Contracts

Histogram percentile panels use:

- `histogram_quantile(0.9999, sum(rate(<metric>_bucket{...}[$__rate_interval])) by (..., le, $additional_groupby))` for fixed p99.99 lines.
- `histogram_quantile(0.99, ...)` for p99 lines in auto-compaction and lock-manager panels.
- `histogram_quantile($optional_quantile, ...)` for operator-selected quantiles in slow-trend and snapshot panels.

Average panels use the conventional Prometheus histogram average formula:

- `sum(rate(<metric>_sum{...}[$__rate_interval])) by (...) / sum(rate(<metric>_count{...}[$__rate_interval])) by (...)`.

Counter-rate panels use `sum(rate(...[$__rate_interval])) by (...)`. Snapshot action and reconnect panels use `delta(...[1m])` or `delta(...[$__rate_interval])`; these are sensitive to counter reset behavior. Gauge panels usually use direct `sum((metric{...})) by (...)`, while queue status panels use `max_over_time(...[30s])` to smooth short-lived lock-manager state.

`$additional_groupby` is interpolated into many `by (...)` clauses and legend templates. It is an important integration contract: the variable must expand to a syntactically valid PromQL label list in contexts such as `by (type, $additional_groupby)`, `by ($additional_groupby)`, and `legendFormat` strings like `{{$additional_groupby}}`.

## Metrics Covered

Metrics referenced by this chunk include:

- GC and auto compaction: `tikv_gcworker_gc_keys`, `tikv_auto_compaction_duration_seconds_*`, `tikv_auto_compaction_regions_meet_threshold`, `tikv_auto_compaction_pending_candidates`, `tikv_auto_compaction_num_tombstones_*`, `tikv_auto_compaction_num_discardable_*`, `tikv_auto_compaction_mvcc_versions_scanned_*`, and `tikv_auto_compaction_score_*`.
- Lock manager and pessimistic locking: `tikv_thread_cpu_seconds_total`, `tikv_lock_manager_task_counter`, `tikv_lock_manager_waiter_lifetime_duration_*`, `tikv_lock_manager_wait_table_status`, `tikv_lock_wait_queue_entries_gauge_vec`, `tikv_lock_manager_detect_duration_*`, `tikv_lock_manager_error_counter`, `tikv_lock_manager_detector_leader_heartbeat`, `tikv_pessimistic_lock_memory_size`, `tikv_in_memory_pessimistic_locking`, `tikv_lock_wait_queue_length_bucket`, and `tikv_storage_mvcc_scan_lock_read_duration_seconds_*`.
- Generic workers: `tikv_worker_handled_task_total`, `tikv_worker_pending_task_total`, `tikv_futurepool_handled_task_total`, and `tikv_futurepool_pending_task_total`.
- PD client: `tikv_pd_request_duration_seconds_*`, `tikv_pd_heartbeat_message_total`, `tikv_pd_pending_heartbeat_total`, `tikv_pd_validate_peer_total`, `tikv_pd_reconnect_total`, `tikv_pd_request_forwarded`, and `tikv_pd_pending_tso_request_total`.
- Slow trend: `tikv_raftstore_inspect_duration_seconds_bucket`, `tikv_raftstore_slow_score`, `tikv_raftstore_disk_probe_duration_seconds_bucket`, `tikv_raftstore_slow_trend`, `tikv_raftstore_slow_trend_result`, `tikv_raftstore_slow_trend_l0`, and `tikv_raftstore_slow_trend_result_value`.
- Snapshot: `tikv_raftstore_raft_sent_message_total`, `tikv_raftstore_snapshot_traffic_total`, `tikv_pending_delete_ranges_of_stale_peer`, `tikv_raftstore_snapshot_generation_wait_duration_seconds_bucket`, `tikv_raftstore_snapshot_apply_wait_duration_seconds_bucket`, `tikv_server_send_snapshot_duration_seconds_bucket`, `tikv_raftstore_snapshot_duration_seconds_bucket`, `tikv_snapshot_size_bucket`, `tikv_snapshot_kv_count_bucket`, `tikv_raftstore_snapshot_total`, `tikv_raftstore_clean_region_count`, `tikv_server_snapshot_task_total`, `tikv_snapshot_limit_transport_bytes`, `tikv_snapshot_limit_generate_bytes`, and `tikv_raftstore_snapshot_pending_applies`.
- Resolved TS start: `tikv_resolved_ts_min_resolved_ts_gap_millis`, `tikv_resolved_ts_min_resolved_ts_region`, `tikv_resolved_ts_min_follower_safe_ts_gap_millis`, `tikv_resolved_ts_min_follower_safe_ts_region`, and the next chunk's visible continuation for `tikv_resolved_ts_min_leader_resolved_ts_gap_millis`.

## Control Flow and Observability Model

There is no executable control flow in this JSON. Grafana interprets the declarative object tree: collapsed row panels hold child `panels`, child panels run their `targets`, Prometheus evaluates the expressions after dashboard variable substitution, and Grafana renders the returned time series using graph or heatmap settings.

The implicit diagnostic flow in this chunk is:

1. Confirm GC scan and auto-compaction behavior. The GC panels separate `write` and `default` column families, while auto-compaction panels correlate duration with candidate volume, tombstone count, discardable versions, MVCC scan depth, and score.
2. Inspect pessimistic-locking pressure. CPU, task, queue, waiter-lifetime, deadlock-detection, memory, and in-memory-locking panels distinguish high lock contention from lock-manager scheduling, deadlock detector, or MVCC scan-lock read costs.
3. Check generic asynchronous task pressure. Worker and future-pool handled/pending panels indicate whether TiKV background pools are falling behind by worker/future-pool name.
4. Check PD client health. Request rate and average duration expose client-side PD latency; heartbeats, reconnects, forward status, validation, and pending TSO requests expose PD communication and TSO backpressure.
5. Identify slow-store trends. Slow score, disk probe duration, QPS trend, sampling latency, and QPS by instance provide a store-level signal that can explain Raftstore or PD-facing symptoms.
6. Investigate snapshot pressure. Snapshot state, wait, handling duration, size, KV count, action rates, transport/generate throughput, and pending applies identify whether snapshot generation, transfer, apply, or cleanup is contributing to lag.
7. Begin resolved-ts diagnosis. CPU and lag/region panels identify whether resolved-ts advancement is delayed and which regions/instances are responsible; this row continues in the next chunk.

The dashboard intentionally mixes high-percentile histograms, average/count overlays, direct gauges, and queue heatmaps. This gives operators a path from aggregate symptoms to per-instance attribution, but correctness depends on metric label stability and dashboard-variable expansion.

## State and Persistence Behavior

This chunk persists dashboard state only: panel IDs, row placement, row child membership, grid positions, descriptions, legends, tooltip behavior, axis units, datasource references, query strings, hidden/visible target flags, and variable placeholders. It does not persist TiKV runtime state. Runtime state is externalized through Prometheus time series scraped from TiKV.

The observed state includes both durable and transient operational state:

- Durable/persistent subsystem behavior is inferred from snapshot generation/apply, GC, compaction, and resolved-ts metrics.
- Transient queue and leadership state is inferred from lock waiting queues, detector heartbeat, worker/future-pool pending gauges, PD pending heartbeats, pending TSO requests, and snapshot pending applies.
- Counter-derived panels depend on Prometheus scrape history and monotonic counters; missing scrapes, restarts, or counter resets can create gaps or misleading `rate`, `increase`, or `delta` outputs.

Because many panels set `nullPointMode` to `null as zero` and hide empty/zero series, missing metrics can be visually quiet. That is helpful for sparse subsystems but risky when a missing exporter, renamed metric, or failed scrape should be visible as missing data rather than zero activity.

## Dependencies and Integration Points

- Grafana legacy dashboard schema: `row`, `graph`, `heatmap`, `gridPos`, `targets`, `legend`, `seriesOverrides`, `tooltip`, `xaxis`/`yaxes`, heatmap `dataFormat`, and datasource interpolation.
- Prometheus datasource `${DS_TEST-CLUSTER}` and PromQL functions `rate`, `increase`, `delta`, `avg_over_time`, `max_over_time`, `sum`, and `histogram_quantile`.
- Dashboard variables `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$additional_groupby`, `$optional_quantile`, and `$__rate_interval`.
- TiKV metrics exporters for GC worker, auto compaction, lock manager, in-memory pessimistic locking, worker/future pools, PD client, raftstore slow-trend detection, snapshot handling, and resolved-ts workers.
- Operational integration points include TiKV GC/compaction tuning, pessimistic transaction contention diagnosis, PD client and TSO troubleshooting, slow-store detection, snapshot backpressure analysis, and resolved-ts lag debugging.

## Risks and Edge Cases

- The chunk starts mid-panel. The opening `GC scan write details` panel is complete enough to recover its target, title, axes, and legend behavior, but final merged research should reconcile its object start from the previous chunk.
- The chunk ends inside panel 486. `Max gap of resolved-ts in region leaders` is only partially visible here; the next chunk must provide the target expression, legend, axes, and closing object.
- `$additional_groupby` appears inside `by ($additional_groupby)` and appended label lists. An empty or comma-prefixed/comma-suffixed expansion can make PromQL invalid unless the dashboard variable is configured carefully.
- High-cardinality labels can make several queries expensive: `type`, `result`, `status`, `disk`, `outcome`, `instance`, `name`, `key_mode`, `tag`, and arbitrary `$additional_groupby` values are used on histogram and rate aggregations.
- p99.99 and `$optional_quantile` histogram panels require complete `_bucket` series and correct `le` labels. Missing buckets or sparse scrape windows can produce unstable tails.
- Direct `delta` on counters, used for PD reconnects and snapshot action/message panels, can be noisy or negative across restarts. `rate`/`increase` may be safer if the metric is a standard monotonic counter.
- `null as zero` plus hidden empty/zero series can hide scrape failures, removed metrics, or dashboard-variable filters that match no series.
- Several panels combine different semantic units in one graph, for example snapshot state count with pending-delete ranges, or heartbeat rate with pending heartbeat gauge. Operators need the legend and axis context to avoid comparing unlike values directly.
- The heatmap for lock queue lengths groups only by `le`, not by instance or additional labels, so it gives cluster-level distribution shape but cannot directly identify the responsible TiKV instance.
- `PD forward status` uses legend `{{instance}}-{{host}}`, but the visible expression groups no labels and directly returns the raw series. If `host` is absent or labels differ across TiKV versions, legends may be confusing.

## Test Signals

Validation should focus on dashboard and PromQL correctness:

- Parse the full `tikv_details.json` as JSON after edits; this chunk alone is not a standalone JSON document because it starts and ends at arbitrary line boundaries.
- Import or provision the dashboard in Grafana to catch duplicate panel IDs, invalid legacy fields, broken collapsed-row nesting, bad heatmap configuration, and datasource variable issues.
- Substitute representative dashboard variable values and validate PromQL expressions with Prometheus query APIs, especially expressions containing `$additional_groupby`, `$optional_quantile`, `histogram_quantile`, and direct `delta`.
- Check TiKV `/metrics` or registry definitions for every referenced metric, including histogram sibling series (`_bucket`, `_sum`, `_count`) used for percentile and average panels.
- Exercise variable combinations with no additional grouping, grouping by `instance`, grouping by subsystem labels such as `type`/`status`, and an `$instance` regex matching one TiKV node and multiple TiKV nodes.
- Visual smoke-test the lock wait queue heatmap, auto-compaction histograms, snapshot percentiles, and resolved-ts gap panels on a live cluster to confirm units, legends, hidden series, and `null as zero` behavior are operationally clear.

## Cross-Chunk Notes

This is chunk 9 for `sources/storage-engines/tikv/metrics/grafana/tikv_details.json` in the chunk manifest. The final per-file research should merge it with adjacent chunks to recover the complete GC row before line 60536, the full panel 486 and remaining `Resolved TS` row after line 68613, and the dashboard-level templating/datasource definitions elsewhere in the JSON.
