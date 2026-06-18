# sources/storage-engines/tikv/metrics/grafana/tikv_details.json lines 37417-45105

## Chunk Scope

This chunk covers the TiKV details Grafana dashboard from the tail of the RocksDB row through the full Titan row and the beginning of the In Memory Engine row. It is dashboard configuration rather than executable application code, but it defines an operational API between TiKV Prometheus metrics and Grafana panels. The chunk uses the dashboard-level Prometheus datasource `${DS_TEST-CLUSTER}` and the templated labels `$k8s_cluster`, `$tidb_cluster`, `$instance`, `$db`, `$titan_db`, `$additional_groupby`, and Grafana's `$__rate_interval`.

The visible panels are:

- RocksDB `$db` metrics: compaction flow, bytes per write, read amplification, pending compaction bytes, snapshots, compression ratio, SST file levels, oldest snapshot duration, external SST ingestion, RocksDB block-read counters, write stall signals, stall-condition changes, and memtable size.
- Titan `$titan_db` metrics: blob file count and size, blob cache size and hit ratio, blob key/value size distributions, blob get and iterator operations, blob read/write/sync/GC durations, blob flow rates, discardable ratio distribution, and GC input/output/file counters.
- In Memory Engine start: KV operations, read throughput comparison with RocksDB, coprocessor handle duration, region cache hit and hit-rate, region cache miss reasons, and memory usage. The next panel starts at the end of the chunk but is incomplete here.

## Purpose

The chunk's purpose is to expose low-level TiKV storage engine health in one dashboard area. Operators can use these panels to correlate:

- RocksDB write amplification, compaction pressure, memtable growth, stalled writes, snapshot retention, and ingestion behavior.
- Titan blob-file lifecycle, cache effectiveness, blob I/O latency, iterator behavior, discardable data accumulation, and GC throughput.
- In-memory engine usage, hit rate, request latency, and read throughput contribution relative to RocksDB.

This dashboard is a read-only observability artifact. It does not persist TiKV state, mutate cluster configuration, or run application control flow. Its behavioral contract is the set of PromQL expressions, units, labels, legend templates, row layout, and Grafana panel options encoded in JSON.

## Important Dashboard Objects and APIs

The primary "types" in this chunk are Grafana dashboard schema objects:

- `row` panels: `RocksDB - $db`, `Titan - $titan_db`, and `In Memory Engine` organize nested panels and are collapsed by default in surrounding dashboard style.
- `graph` panels: most panels use the legacy `flot` graph renderer, line rendering, table legends, `hideEmpty: true`, `hideZero: true`, `sort: "max"`, and `nullPointMode: "null as zero"`.
- `heatmap` panel: `Ingestion picked level` uses bucketed `tikv_engine_ingestion_picked_level_bucket` data with `sum(increase(...[$__rate_interval])) by (le)`.
- Prometheus query APIs: `rate`, `increase`, `sum`, `avg`, `max`, `topk`, and `histogram_quantile`.
- Prometheus histogram convention: duration panels use `_bucket`, `_sum`, and `_count` series for percentile, average, and request-rate views.

Important metrics referenced by family:

- RocksDB engine flow and state: `tikv_engine_compaction_flow_bytes`, `tikv_engine_flow_bytes`, `tikv_engine_bytes_per_write`, `tikv_engine_read_amp_flow_bytes`, `tikv_engine_pending_compaction_bytes`, `tikv_engine_num_snapshots`, `tikv_engine_compression_ratio`, `tikv_engine_num_files_at_level`, `tikv_engine_oldest_snapshot_duration`, `tikv_engine_memory_bytes`.
- Ingestion and RocksDB perf: `tikv_engine_ingestion_picked_level_bucket`, `tikv_storage_ingest_external_file_duration_secs_bucket`, `_sum`, `_count`, `tikv_storage_ingest_external_file_allow_write_counter`, `tikv_storage_rocksdb_perf`, `tikv_coprocessor_rocksdb_perf`.
- Write stall: `tikv_engine_write_stall_reason`, `tikv_engine_write_stall`, `tikv_engine_stall_conditions_changed`.
- Titan file and cache state: `tikv_engine_titandb_num_live_blob_file`, `tikv_engine_titandb_num_obsolete_blob_file`, `tikv_engine_titandb_live_blob_file_size`, `tikv_engine_titandb_obsolete_blob_file_size`, `tikv_engine_blob_cache_size_bytes`, `tikv_engine_blob_cache_efficiency`.
- Titan operation and latency families: `tikv_engine_blob_iter_touch_blob_file_count`, `tikv_engine_blob_key_size`, `tikv_engine_blob_value_size`, `tikv_engine_blob_locate`, `tikv_engine_blob_get_micros_seconds`, `tikv_engine_blob_seek_micros_seconds`, `tikv_engine_blob_next_micros_seconds`, `tikv_engine_blob_prev_micros_seconds`, `tikv_engine_blob_file_read_micros_seconds`, `tikv_engine_blob_file_write_micros_seconds`, `tikv_engine_blob_file_sync_micros_seconds`, `tikv_engine_blob_gc_micros_seconds`.
- Titan flow and GC: `tikv_engine_blob_flow_bytes`, `tikv_engine_titandb_blob_file_discardable_ratio`, `tikv_engine_blob_file_synced`, `tikv_engine_blob_gc_action_count`, `tikv_engine_blob_gc_flow_bytes`, `tikv_engine_blob_gc_input_file`, `tikv_engine_blob_gc_output_file`, `tikv_engine_blob_gc_file_count`.
- In-memory engine: `tikv_in_memory_engine_kv_operations`, `tikv_in_memory_engine_flow`, `tikv_in_memory_engine_memory_usage_bytes`, `tikv_snapshot_type_count`, `tikv_in_memory_engine_snapshot_acquire_failed_reason_count`, `tikv_coprocessor_request_handle_seconds_bucket`, `_sum`, `_count`.

## Query and Control Flow

Grafana drives control flow by evaluating each panel target over the selected time range and template variable values:

1. The dashboard variables resolve cluster and instance filters from Prometheus labels. In this chunk, all query targets filter by `k8s_cluster="$k8s_cluster"` and `tidb_cluster="$tidb_cluster"`, most filter by `instance=~"$instance"`, and storage-engine panels further filter by either `db="$db"` or `db="$titan_db"`.
2. Rate panels compute per-second changes over `$__rate_interval` using `rate(counter[$__rate_interval])` and then aggregate with `sum ... by (...)`.
3. Gauge-style panels read the current series and aggregate with `avg`, `max`, or `sum`.
4. Histogram panels calculate high-percentile latency with `histogram_quantile` over `sum(rate(bucket[$__rate_interval])) by (le, ...)`, and average latency with `sum(rate(_sum)) / sum(rate(_count))`.
5. Legends derive series identity from labels such as `instance`, `cf`, `level`, `type`, `req`, `ratio`, and `$additional_groupby`.

RocksDB flow:

- `Compaction flow` compares compaction bytes read, compaction bytes written, and flush-write bytes. It is the first correlation point for compaction I/O pressure.
- `Bytes / Write` reads precomputed summary-like series split by type labels `bytes_per_write_max`, `bytes_per_write_percentile99`, `bytes_per_write_percentile95`, and `bytes_per_write_average`.
- `Read amplification` divides total read bytes by estimated useful bytes per instance.
- Compaction backlog, snapshot counts/duration, compression ratio, SST file count, ingestion level, and ingest duration then provide cause signals for stalls and space amplification.
- `Write Stall Reason`, `Write stall duration`, and `Stall conditions changed of each CF` expose RocksDB throttle state and frequency.
- `Memtable size` tracks `type="mem-tables-all"` memory by column family.

Titan flow:

- File count and size panels compare live versus obsolete blob files.
- Cache panels show top 20 blob cache sizes by instance/CF and compute hit ratio as hit / (hit + miss).
- Size-distribution panels expose average, p95, p99, and max key/value/blob-iterator touch counts from `type` labels.
- Operation panels use `tikv_engine_blob_locate` counters for get, seek, prev, and next operations.
- Latency panels use pre-aggregated type labels ending in `_average`, `_percentile95`, `_percentile99`, and `_max`, grouped by either `$additional_groupby` or `type, $additional_groupby`.
- Flow panels split key and byte flows with `type=~"keys.*"` and `type=~"bytes.*"`.
- GC panels expose action counts, GC duration, input/output file sizes, key/byte flows, and file count rates.

In-memory engine flow:

- `OPS` sums `tikv_in_memory_engine_kv_operations` by `instance`, `type`, and `$additional_groupby`.
- `Read MBps` compares RocksDB `tikv_engine_flow_bytes` against `tikv_in_memory_engine_flow` for read and iterator read byte types.
- `Coprocessor Handle duration` shows 99.99%, 99%, average, and count for `tikv_coprocessor_request_handle_seconds` by request type.
- `Region Cache Hit` and `Region Cache Hit Rate` derive in-memory snapshot usage from `tikv_snapshot_type_count`.
- `Region Cache Miss Reason` breaks snapshot acquisition failures down by `type`.
- `Memory Usage` averages `tikv_in_memory_engine_memory_usage_bytes` by instance.

## State and Persistence Behavior

The chunk does not define durable application state. Persistence-related behavior is indirect:

- RocksDB panels reflect persisted LSM state: SST levels, compaction debt, snapshots, memtables, write stalls, and ingestion.
- Titan panels reflect persisted blob-file state: live/obsolete blob files, discardable ratios, blob GC input/output, and sync/write/read latencies.
- In-memory engine panels reflect volatile cache state and memory usage, with hit-rate calculations derived from snapshot acquisition counters.

Grafana state consists of dashboard JSON fields: panel `id`, `gridPos`, row nesting, datasource references, target expressions, legend display options, axis units, and rendering settings. This state is versionable configuration in the repository, not runtime state in TiKV.

## Dependencies and Integration Points

Runtime dependencies:

- Prometheus datasource `${DS_TEST-CLUSTER}`.
- TiKV metric exporters exposing the named `tikv_*` series and expected labels.
- Grafana support for legacy `graph`/`heatmap` panel JSON, `flot` rendering, table legends, and template variables.
- Dashboard-level variables from the full file, especially `k8s_cluster`, `tidb_cluster`, `db`, `instance`, `titan_db`, `additional_groupby`, and Grafana's `$__rate_interval`.

Integration points:

- The `$db` variable is sourced from RocksDB block-cache metrics and is reused across RocksDB panels.
- The `$titan_db` variable is sourced from Titan blob-file metrics and gates all Titan panels.
- `$additional_groupby` is injected directly into `by (...)` clauses, so it controls whether panels aggregate at cluster, instance, store, or other label dimensions.
- In-memory engine panels integrate with coprocessor request metrics and RocksDB read-flow metrics to compare cache behavior against regular engine reads.
- The row/panel IDs in this chunk (`263` through `314`) are part of the larger `tikv_details.json` dashboard and must stay unique within the full dashboard.

## Risks and Edge Cases

- Several panels use `nullPointMode: "null as zero"`. Missing series can appear as zero, which is convenient for sparse metrics but can hide exporter regressions or metric name drift.
- Ratio panels do not guard against zero denominators. `Read amplification`, `Blob cache hit`, and `Region Cache Hit Rate` may produce `NaN`, `Inf`, or missing series when useful bytes, hit+miss totals, or snapshot counts are zero.
- `$additional_groupby` appears inside `by (...)` clauses. If the variable is empty or malformed, PromQL can become syntactically invalid; if it expands to labels absent from a metric family, aggregation cardinality and legends can differ across panels.
- Several Titan duration panels have label/selector mismatches visible in this chunk: `Blob file read duration` labels the `percentile99` selector as `95%` and the `percentile95` selector as `99%`; `Blob file write duration` shows the same inversion. This can mislead latency diagnosis even if the underlying metrics are correct.
- Some panels group by `type` even while selecting a single exact `type` value. This is harmless but can make legends verbose and may retain stale type labels if metric naming changes.
- `topk(20)` on blob cache size hides lower-ranked instances/CFs. It is useful for dashboards but not complete enough for fleet-wide capacity accounting.
- `sum(increase(...[$__rate_interval])) by (le)` in the ingestion heatmap depends on bucket monotonicity and scrape continuity; resets or sparse ingestion can make the heatmap noisy.
- The chunk ends inside the next In Memory Engine panel (`The count of different types of region`), so this report cannot fully characterize that panel's target expressions.

## Test and Validation Signals

Useful checks for this dashboard chunk:

- JSON validity: the whole `tikv_details.json` should parse with `jq`; this was confirmed while extracting panel metadata.
- Panel coverage: expected visible IDs in this range are `263` through `314`, with rows `279` (`Titan - $titan_db`) and `307` (`In Memory Engine`).
- PromQL syntax validation: load the dashboard in Grafana against a Prometheus datasource and verify each target parses after variable expansion, especially expressions containing `$additional_groupby`.
- Metric availability: query Prometheus for every metric family listed above in a TiKV cluster with RocksDB, Titan, and in-memory engine features enabled.
- Semantic validation: compare `Blob file read duration` and `Blob file write duration` legend labels against their `type` selectors to fix the p95/p99 inversion if confirmed as unintended.
- Rendering validation: verify units match series semantics (`binBps` for byte flows, `bytes` for sizes, `ops` for operation rates, `s` for histogram seconds, and `microseconds` display for precomputed Titan micros metrics).
- Sparse-data validation: inspect ratio panels during no-traffic windows to ensure zero denominators do not create misleading alerts or unreadable legends.

## Chunk Boundaries and Merge Notes

This chunk starts in the middle of the RocksDB dashboard section after a preceding panel's axis configuration, then covers complete RocksDB panels `263` through `278`, the full Titan row `279` through `306`, and the start of In Memory Engine row `307` through panel `314`. The final per-file merge should combine this with adjacent chunks to recover the preceding RocksDB panels and the remaining In Memory Engine panel(s) after line `45105`.
