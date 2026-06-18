# subset-b-008693 Research: RocksDB block cache analyzer tools

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.py -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.py

## Purpose

`block_cache_pysim.py` is a standalone Python simulator for RocksDB block-cache trace CSVs. It evaluates replacement and admission behavior across trace-observed hits, LRU-style policies, Belady MIN, ARC, GreedyDualSize, and reinforcement-learning policy selectors. It also emits CSV fragments for miss-ratio curves, miss and miss-ratio timelines, byte-miss summaries, and policy-selection timelines consumed by the shell combiner and plotting script in this same directory.

## Important APIs, Types, And Functions

`TraceRecord` mirrors the fields of RocksDB `BlockCacheTraceRecord` as a CSV-friendly Python object. It normalizes boolean integer fields and computes the effective cached block size as `block_size + block_key_size`.

`CacheEntry`, `HashEntry`, and `HashTable` provide the storage primitives used by sampled policies. `HashTable` is a custom chained hash table with resize-on-growth/shrink and `random_sample()` for sampled eviction. This supports ML policy evaluation without materializing or sorting the whole cache on each eviction.

`MissRatioStats` and `PolicyStats` accumulate global and time-bucketed counters. `MissRatioStats` tracks accesses, misses, miss bytes, and per-time-unit maps; `PolicyStats` records the policy chosen by an ML cache per time bucket.

`Policy` and its implementations (`LRUPolicy`, `MRUPolicy`, `LFUPolicy`, `HyperbolicPolicy`, `CostClassPolicy`) rank sampled entries for eviction. `ThompsonSamplingCache` and `LinUCBCache` choose among these policies using bandit-style reward from whether a selected policy had evicted the missed key.

`Cache` is the abstract simulator base. `access()` handles block-vs-row-key behavior, calls `_lookup()`, `_evict()`, `_insert()`, and `_should_admit()`, and updates the common miss statistics. `MLCache`, `OPTCache`, `GDSizeCache`, `ARCCache`, `LRUCache`, and `TraceCache` implement the policy-specific mechanics.

`create_cache()` is the main factory. It parses `hybrid` and `hybridn` suffixes, scales capacity by downsample ratio, and maps strings such as `ts`, `linucb`, `pylru`, `pycctbbt`, `opt`, `trace`, `lru`, `arc`, and `gdsize` to concrete cache instances.

`run()` is the trace driver. It optionally pre-scans the whole trace for OPT next-access sequence numbers, streams each CSV line into a `TraceRecord`, filters by column family, handles warmup counter reset, updates trace-observed stats, and feeds the selected simulator. `report_stats()` writes the generated `data-ml-*` files. The `__main__` block parses eight CLI arguments and wires the factory, runner, and reporter together.

## Control Flow

The CLI expects cache type, cache size, downsample size, warmup seconds, trace path, result directory, max accesses, and target column family. It parses capacity suffixes with `parse_cache_size()`, creates a cache, streams the trace through `run()`, then writes summaries with `report_stats()`.

For normal policies, `run()` is single pass: split each comma-delimited line, skip non-target column families, create a `TraceRecord`, update observed trace stats, and call `cache.access()`. For `OPTCache`, `run()` first scans all target records into per-block `BlockAccessTimeline` instances so every later access can carry `next_access_seq_no` for Belady-style eviction.

`Cache.access()` either routes Get-like records through row-key hybrid handling or directly accesses the block key. `_access_kv()` performs the generic lookup/miss/admission sequence. Policy implementations only supply lookup/eviction/insertion details, keeping metric update centralized.

Hybrid row-key mode treats `caller == 1` records with nonzero `get_id` and `key_id` as Gets. It first attempts the row key, may short-circuit future block accesses for the same Get when a row hit completes the request, and can run in mode `2` where data blocks are not inserted on row misses.

## State And Persistence Behavior

Runtime state is in-memory and proportional to cache contents plus trace metadata. `HashTable` keeps cache entries for sampled policies; `PQTable` backs OPT and GreedyDualSize; ARC keeps T1/T2/B1/B2 deques and a value table; hybrid mode keeps a bounded `get_id_row_key_map` with `retain_get_id_range = 100000`.

OPT can be memory-heavy because it keeps an access timeline for every block before replay. The code periodically calls `gc.collect()` during large runs and after hash-table resize to reduce Python heap pressure.

Persistent output is a family of CSV fragment files under `result_dir`, mostly prefixed `data-ml-...` and `header-ml-...`. `report_stats()` writes miss-ratio curves, per-second/minute/hour byte-miss summaries, miss timelines, miss-ratio timelines, and policy timelines for ML caches. It overwrites existing fragment files with `w+`.

## Dependencies And Integration Points

The script depends on Python standard modules plus `numpy`. It integrates with `block_cache_pysim.sh`, which launches many instances and concatenates the generated `header-` and `data-` files into aggregate `ml_*` files. Its output naming is also consumed by `block_cache_trace_analyzer_plot.py`.

The trace input format is assumed to be the comma-separated, human-readable ordering of RocksDB block-cache trace fields: timestamp, block id, block type, block size, column family metadata, caller, no-insert, Get/key metadata, hit flags, table/sequence/key-size metadata, and block offset.

## Risks And Edge Cases

Several policy paths are not Python 3 compatible as written. The file has a Python 3 shebang but uses `sorted(..., cmp=...)`, and `heapq` entries only define `__cmp__`, not `__lt__`; these paths fail under modern Python 3 when exercised. This affects sampled policy ranking and OPT/GDSize priority queues.

Some capacity arithmetic uses `/`, producing floats in Python 3 (`cache_size / downsample_size`, ARC `self.c`), while several cache algorithms compare sizes and lengths as if integers. This can produce subtle boundary differences or type surprises.

`PolicyStats.write_policy_ratio_timeline()` takes a `file_path` parameter but references `result_dir`, which is not local or global in that scope. `report_stats()` calls it, so ML cache reporting can raise `NameError`.

The CSV parser is positional and unescaped; a malformed line, missing field, or unexpected comma in a text field will fail or corrupt interpretation. `max_accesses_to_process` uses `access_seq_no > max`, so it processes one more record than a strict inclusive/exclusive caller might expect.

Cost-class accounting has suspicious calculations: `CostClassEntry.avg_size()` returns an average last-access time instead of size, and `remove()` subtracts hits, which can make cost-class hit totals negative depending on eviction sequence.

## Test Signals

`block_cache_pysim_test.py` directly imports and exercises the major cache classes, hash table behavior, row-key hybrid behavior, trace-observed stats, and an end-to-end synthetic trace. The tests are useful signals for intended semantics, especially expected evictions for LRU/LFU/MRU/OPT and cache-size accounting. However, because several Python 3-incompatible constructs are in active paths, the test module itself is also likely to expose runtime failures when run with the shebang's interpreter.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.sh -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.sh

## Purpose

`block_cache_pysim.sh` is a batch runner and result combiner for `block_cache_pysim.py`. It launches many Python simulations across fixed cache sizes and cache policy names, limits concurrent jobs, waits for completion, and then merges per-run CSV fragments into consolidated `ml_*` result files under the requested result directory.

## Important APIs, Inputs, And Outputs

The script requires exactly five arguments: `trace_file_path`, `result_dir`, `downsample_size`, `warmup_seconds`, and `max_jobs`. It sets a fixed `max_num_accesses=100000000` and uses `result_dir/ml` as a temporary directory for per-run logs and CSV fragments.

The batch matrix is hard-coded to column family `all`, cache sizes `1G`, `2G`, `4G`, `8G`, and `16G`, and cache types `opt`, `lru`, `pylru`, `pycctbbt`, `pyhb`, `ts`, `trace`, and `lru_hybrid`. The `trace` pseudo-cache is only run for `16G` because it reports observed trace misses independent of simulated capacity.

Outputs are generated by Python into `result_dir/ml`, then concatenated into files such as `ml_<cf>_<capacity>_<time_unit>policy_timeline`, `ml_<cf>_<capacity>_<time_unit>miss_timeline`, `ml_<cf>_mrc`, `ml_<time_unit>_<cf>_avgmb`, and `ml_<time_unit>_<cf>_p95mb`. Final MRC and byte-miss files are sorted by cache type and capacity.

## Control Flow

The script validates argument count, disables core dumps with `ulimit -c 0`, removes and recreates the temporary ML result directory, and enters nested loops over column family, cache size, and cache type.

Before launching each simulation, it polls the number of running Python pysim processes using `ps aux | grep pysim | grep python | grep -cv grep`. If this count is at least `max_jobs`, it sleeps and rechecks. Each simulation is started with `nohup python block_cache_pysim.py ... >& "$ml_tmp_result_dir/$output" &`.

After launching the matrix, it waits until no `pysim` Python processes remain. It then scans every generated file twice, once for `header-` files and once for `data-` files, derives a consolidated output filename from filename fragments, appends the content, and sorts selected aggregate files.

## State And Persistence Behavior

The script destructively removes `result_dir/ml` at startup and removes any previous `result_dir/ml_*` aggregate files before combining. It does not preserve old simulation outputs.

Job state is inferred externally from process names, not from child PIDs captured at launch. The script does not record a manifest of launched commands or per-job exit status. Combined files are append-built from whatever files exist under the temporary directory after the wait loop.

## Dependencies And Integration Points

It depends on Bash, `ps`, `grep`, `sort`, `cat`, and a `python` executable in `PATH`. The script assumes it is run from a working directory where `block_cache_pysim.py` is directly addressable by relative path. Its combined output filenames are intended for `block_cache_trace_analyzer_plot.py`.

The comments mention package requirements for numpy/scipy/matplotlib/pandas-era tooling, but only the simulator execution itself is needed in this script.

## Risks And Edge Cases

The process-counting logic is broad: any unrelated Python command containing `pysim` can throttle or keep the script waiting. Conversely, child processes that do not match this grep pattern may be missed. Because `current_jobs` is initialized from a global process scan and then incremented manually, it can drift from the actual set of launched children.

The script uses `python`, not `python3`, despite the simulator's Python 3 shebang. On systems where `python` is Python 2 or absent, runs fail or use the wrong interpreter.

It removes result directories with `rm -rf` based on user-provided `result_dir`. Incorrect arguments can delete prior results. It also appends files without checking simulator exit statuses, so partial or failed runs can produce incomplete aggregate CSVs.

Filename parsing uses shell string splitting on `-` and relies on fixed positions. Cache names or paths containing unexpected dashes can produce wrong `time_unit`, `capacity`, or column-family extraction. The loop `for fn in $result_dir/*` is unquoted, so result paths containing spaces are unsafe.

## Test Signals

There is no dedicated shell test. Behavioral confidence is indirect: the Python simulator's tests validate some generated data paths, and the plotting script encodes expectations for the aggregate output names. Missing direct tests leave concurrency limiting, result cleanup, filename parsing, and failure handling unverified.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim_test.py -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim_test.py

## Purpose

`block_cache_pysim_test.py` is an executable test suite for the Python block-cache simulator. It uses assertions and synthetic traces rather than a test framework to validate hash-table operations, cache replacement behavior, hybrid row-key behavior, trace-observed hit accounting, and an end-to-end run across multiple cache factories.

## Important APIs, Types, And Functions

The test imports nearly every simulator-facing type from `block_cache_pysim.py`: cache implementations, policy implementations, `HashTable`, `CacheEntry`, `TraceRecord`, factory `create_cache()`, and driver `run()`.

`test_hash_table()` stress-tests insertion, replacement, deletion, lookup, `len()`, and uniqueness of `random_sample()` results. It maintains a Python dict as the oracle through one million random operations.

`assert_metrics()` is the core cache-state checker. It verifies `used_size`, access/miss counters, expected block keys, expected row keys, and entry sizes. It supports both the custom `HashTable` and normal dictionary-backed caches.

`test_cache()` builds a small sequence of repeated accesses to keys 1, 2, and 3, then inserts key 4 to check which key is evicted. `test_lru_cache()`, `test_mru_cache()`, and `test_lfu_cache()` specialize this shared sequence with expected outcomes.

`test_mix()` performs randomized access over a fixed key universe and validates high-level invariants: miss ratio is positive, trace cache mirrors trace hit bits, non-trace caches do not exceed capacity, and the sum of entry sizes equals `used_size`.

`test_end_to_end()` writes a synthetic `test_trace`, creates several cache types through `create_cache()`, calls `run()`, checks every cache processed `n` records, asserts OPT has no higher miss ratio than any other cache, and removes the generated trace file.

`test_hybrid()`, `test_opt_cache()`, and `test_trace_cache()` target row/block hybrid semantics, Belady MIN next-access eviction, and direct trace-observed hit behavior respectively.

## Control Flow

The file is designed for direct execution. Under `if __name__ == "__main__"`, it runs all test functions sequentially, then loops across many cache type strings and row-cache suffix modes to call `test_mix()`, and finally performs the synthetic end-to-end trace run.

Most tests mutate a shared `TraceRecord` object by changing selected fields between calls. This keeps setup compact and makes expected state transitions explicit. The randomized tests rely on Python's default random seed, so they cover many combinations but are not deterministic.

## State And Persistence Behavior

The only persistent artifact is the temporary `test_trace` file created by `test_end_to_end()`, which is removed on successful completion. If an assertion or runtime exception occurs before cleanup, the file may remain in the working directory.

Tests intentionally inspect internal cache state such as `used_size`, `table`, and policy data structures. This gives strong white-box coverage of simulator invariants but couples tests tightly to implementation details.

## Dependencies And Integration Points

The test depends on the importable sibling module `block_cache_pysim.py` and standard `os`, `random`, and `sys`. It does not use pytest/unittest discovery conventions. It can be run as `python3 block_cache_pysim_test.py` from the analyzer directory, assuming simulator dependencies such as numpy are installed.

It serves as the only direct validation signal for the simulator invoked by `block_cache_pysim.sh`; there is no direct integration test that runs the shell batch or plotting pipeline.

## Risks And Edge Cases

The test suite is expensive: `test_hash_table()` runs one million randomized operations, `test_mix()` runs 100k operations per cache/mode combination, and `test_end_to_end()` writes and processes 100k trace rows across multiple cache types. This is useful for stress but can be slow in lightweight CI.

Randomized tests are not seeded, so failures may be difficult to reproduce exactly. The tests also do not use `try/finally` around `test_trace` cleanup.

Because the simulator currently uses Python 2 comparison idioms in active cache paths, these tests may fail under Python 3 before reaching all intended assertions. The test file itself is therefore an important compatibility signal, not just a correctness signal.

The tests do not validate generated CSV file contents from `report_stats()`, policy timeline reporting, shell aggregation, plotting, malformed traces, target column-family filtering, or warmup reset behavior in detail.

## Test Signals

Positive signals include broad coverage of cache factory strings, row-key modes `0`, `1`, and `2`, exact expected evictions for small deterministic sequences, internal size accounting, and end-to-end trace replay. Gaps remain around output-file contracts and external orchestration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.cc -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.cc

## Purpose

`block_cache_trace_analyzer.cc` implements the RocksDB block-cache trace analyzer command when built with `GFLAGS`. It reads binary or human-readable block-cache traces, optionally simulates cache configurations, aggregates per-block/per-file/per-column-family statistics, and emits human-readable summaries plus CSV files for timelines, miss-ratio curves, reuse metrics, spatial locality, skew, access-count distributions, and correlation inputs.

## Important APIs, Types, And Functions

The file defines gflags for trace path, output path, cache simulator config, downsample/warmup, print options, grouping labels, bucket lists, reuse analysis, caller analysis, MRC-only mode, correlation limits, and human-readable trace conversion.

Helper functions convert block types and callers to strings, parse caller names, identify user accesses, compute percentages, parse bucket strings, parse cache simulator configuration files, and normalize timeline granularity.

`BlockCacheTraceAnalyzer::Analyze()` is the main reader loop. It creates either `BlockCacheHumanReadableTraceReader` or binary `BlockCacheTraceReader`, optionally opens a human-readable writer, streams records, records per-block state unless `mrc_only_`, updates miss-ratio stats, feeds `BlockCacheTraceSimulator`, and prints progress.

`RecordAccess()` updates the nested aggregate maps keyed by column family, SST file number, block type, and block key. It assigns stable internal block IDs, updates `BlockAccessInfo`, tracks Get key timelines, optionally computes reuse distance, and writes a human-readable record with block/get IDs.

Output writers include `WriteMissRatioCurves()`, `WriteMissRatioTimeline()`, `WriteMissTimeline()`, `WriteAccessTimeline()`, `WriteReuseDistance()`, `WriteReuseInterval()`, `WriteReuseLifetime()`, `WriteBlockReuseTimeline()`, `WritePercentAccessSummaryStats()`, `WriteDetailedPercentAccessSummaryStats()`, `WriteAccessCountSummaryStats()`, `WriteGetSpatialLocality()`, `WriteSkewness()`, `WriteCorrelationFeatures()`, and `WriteCorrelationFeaturesForGet()`.

Print-only methods include `PrintStatsSummary()`, `PrintBlockSizeStats()`, `PrintAccessCountStats()`, and `PrintDataBlockAccessStats()`.

`block_cache_trace_analyzer_tool()` is the command entry point. It parses flags, initializes optional cache simulators, constructs the analyzer, runs analysis, writes MRC/timelines, and dispatches all requested detailed analyses unless MRC-only mode is set.

## Control Flow

Startup validates `FLAGS_block_cache_trace_path`, parses cache simulator configs if provided, and constructs `BlockCacheTraceSimulator` with warmup and downsample settings. The analyzer then reads the trace until the reader returns an incomplete/end status or an error.

During each record, full-analysis mode calls `RecordAccess()` before updating global miss-ratio state. The simulator access path is independent of full-analysis state, which lets `--mrc_only` avoid keeping per-block aggregates while still producing cache simulation outputs.

After analysis, the entry point always writes miss-ratio curves and miss/miss-ratio timelines for 1 second, 1 minute, and 1 hour granularities if a simulator/output directory exists. It then prints summaries and conditionally writes optional outputs based on non-empty label/bucket flags.

Most CSV writers use `TraverseBlocks()` to iterate the nested aggregate tree and build label-keyed maps. `ParseLabelStr()` validates labels such as `cf`, `sst`, `level`, `bt`, `caller`, `block`, and `all`; `BuildLabel()` concatenates selected label values into stable output labels.

## State And Persistence Behavior

Persistent analyzer state lives in memory while processing a trace: `cf_aggregates_map_` owns block aggregate data, `block_info_map_` points into those owned block aggregates for quick lookup, `get_key_info_map_` stores Get-key timelines, `miss_ratio_stats_` and `caller_miss_ratio_stats_map_` store time-bucketed hit/miss data, and `cache_simulator_` stores simulated cache state.

Reuse distance mode is particularly expensive. On every access, `RecordAccess()` can add the current block key to every existing block's `unique_blocks_since_last_access` set, making CPU and memory scale poorly with unique block count.

Output files are written directly under `output_dir_` with names encoding labels, time units, cache capacity, and suffix constants. Human-readable trace conversion writes to `human_readable_trace_file_path_` when requested. Most writers silently return if an output file cannot be opened.

## Dependencies And Integration Points

The file is compiled only under `#ifdef GFLAGS`. It depends on RocksDB trace classes (`BlockCacheTraceReader`, `BlockCacheHumanReadableTraceReader`, `BlockCacheTraceRecord`), RocksDB cache simulator classes, `Env`/file APIs, `HistogramStat`, gflags compatibility, and RocksDB string parsing utilities.

`parse_cache_config_file()` consumes configuration lines matching `cache_name,num_shard_bits,ghost_capacity,cache_capacity_1,...`. These map into `BlockCacheTraceSimulator` and the output contract used by plotting.

CSV outputs use suffixes and layouts expected by `block_cache_trace_analyzer_plot.py`. The Python simulator produces parallel `ml_*` variants for some of the same graph families.

## Risks And Edge Cases

Many output writers silently return when a file cannot be opened, so a run can finish without producing requested files. Several bucketed analyses use `upper_bound(...)->second` and require the final max bucket appended by `parse_buckets()`; direct calls with incomplete buckets can dereference `end()`.

`TraverseBlocks()` returns immediately when grouping by table and a block lacks table ID, which can stop traversal of all remaining blocks rather than skipping only that block. This can under-report table-grouped analyses.

`Analyze()` returns the final reader status. The tool treats `Status::Incomplete()` as successful end-of-trace, but any other non-OK status exits. Consumers need to know that incomplete is normal here.

Reuse distance computation is explicitly high-cost and can become impractical for large traces. Timeline writers can also create wide CSVs from `start_time` to `end_time`, with sparse data expanded into zero-filled columns.

Some percentage calculations return `-1` on zero denominators; those values are written into CSVs and can surprise plotting or downstream consumers expecting non-negative percentages.

## Test Signals

This file exposes `TEST_cf_aggregates_map()` in the header, suggesting unit tests can inspect aggregation state. The code itself contains no tests in this subset. Practical validation signals are compile coverage under `GFLAGS`, analyzer invocation on representative traces, output-file existence/content checks, and plotting compatibility checks against generated CSVs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.h -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.h

## Purpose

`block_cache_trace_analyzer.h` declares the data model and public API for the RocksDB block-cache trace analyzer. It defines per-key, per-block, per-block-type, per-SST, and per-column-family aggregation structures, feature/prediction vectors for correlation analysis, and the `BlockCacheTraceAnalyzer` class used by the C++ command entry point.

## Important APIs, Types, And Functions

`GetKeyInfo` tracks a user key's assigned ID plus access sequence numbers and timestamps. `AddAccess()` appends the sequence number and microsecond timestamp for each Get access referencing that key.

`BlockAccessInfo` is the central per-block aggregate. It stores block identity, table and offset metadata, access counts, size, first/last access time, key cardinality, referenced-key maps, caller maps, per-caller timelines, unique blocks since last access, reuse-distance counts, sequence timelines, and timestamp timelines. `AddAccess()` enforces consistent block size/key count when known, updates caller and timeline data, records table/offset metadata, and gathers data-block Get/MultiGet spatial-locality fields.

`BlockTypeAccessInfoAggregate`, `SSTFileAccessInfoAggregate`, and `ColumnFamilyAccessInfoAggregate` form the nested aggregate tree used by the implementation: column family -> SST fd -> block type -> block key -> block info.

`Features` and `Predictions` store vectors for correlation analysis, pairing past features like elapsed time since last access and number of past accesses with future reuse intervals/access counts.

`BlockCacheTraceAnalyzer` exposes `Analyze()`, print methods, CSV writer methods, and `TEST_cf_aggregates_map()`. Private helpers parse label strings, build labels, compute reuse distance, record a single access, update reuse/correlation feature vectors, write generic bucket stats, and traverse blocks.

`block_cache_trace_analyzer_tool(int argc, char** argv)` declares the CLI entry point implemented in the `.cc` file.

## Control Flow

The header's contract centers on one call to `Analyze()` followed by zero or more print/write calls. `Analyze()` populates internal aggregate maps and simulator state. The writer methods then traverse this populated state to produce individual analyses.

`BlockAccessInfo::AddAccess()` is called once per full-analysis trace record. It updates basic metadata first, then caller/timeline maps, then data-block key-level fields when the access is a Get or MultiGet on a data block.

The private `TraverseBlocks()` callback pattern is the core extension point for output writers: it lets each writer supply a callback receiving column-family, file, level, block type, block key, block ID, and immutable block aggregate.

## State And Persistence Behavior

The analyzer owns all aggregation state. `cf_aggregates_map_` owns block records; `block_info_map_` stores pointers into that map and therefore depends on the map lifetime. `get_key_info_map_` accumulates key reuse features for Get accesses. Sequence and timestamp counters are monotonic across trace processing.

The header also declares output path fields (`output_dir_`, `human_readable_trace_file_path_`) and a `BlockCacheHumanReadableTraceWriter`. Actual file persistence is performed by implementation writers.

## Dependencies And Integration Points

The header depends on RocksDB internal and public headers: `db/dbformat.h` for key parsing support, `rocksdb/env.h`, `rocksdb/trace_record.h`, `rocksdb/utilities/sim_cache.h`, `trace_replay/block_cache_tracer.h`, and `utilities/simulator_cache/cache_simulator.h`.

Types such as `TraceType`, `TableReaderCaller`, `BlockCacheTraceRecord`, `BlockCacheTraceHelper`, `MissRatioStats`, and `BlockCacheTraceSimulator` are provided outside this header. This makes the analyzer tightly integrated with RocksDB's trace replay and simulator subsystems.

## Risks And Edge Cases

`BlockAccessInfo::AddAccess()` uses assertions for block-size/key-count consistency and referenced-data-size sanity. In release builds assertions may be disabled; in debug builds malformed traces can abort the process.

`CacheEntry`-like metadata in Python and C++ differ; this header's aggregation uses RocksDB-native fields and helper APIs, while the Python simulator consumes a positional CSV representation. Keeping those contracts synchronized is a cross-language maintenance risk.

`block_info_map_` contains raw pointers into nested `std::map` values. `std::map` node stability makes this workable for inserts, but future container changes would risk pointer invalidation.

Reuse-distance support stores `unique_blocks_since_last_access` per block, which can be very memory-intensive. The header's state shape makes that cost apparent even before reading the implementation.

## Test Signals

`TEST_cf_aggregates_map()` exposes the aggregation tree for tests. Key testable contracts include `BlockAccessInfo::AddAccess()` timeline updates, data-block key maps, column-family/SST/block-type nesting, and analyzer behavior with `mrc_only_` disabled vs enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_plot.py -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_plot.py

## Purpose

`block_cache_trace_analyzer_plot.py` converts CSV outputs from the C++ block-cache trace analyzer and Python simulator into PDF graphs. It handles miss-ratio curves, LRU-relative diffs, access timelines, stacked bucket summaries, reuse graphs, percentage access summaries, skew graphs, correlation heatmaps, and Python-simulator byte-miss statistics.

## Important APIs, Types, And Functions

`get_cmap()` initializes a large shuffled color palette. Global `bar_color_maps`, `colors`, and `color_index` keep label colors stable across graphs.

`num_to_gb()` formats numeric byte counts as GiB text, though it is not used in the visible code paths.

`plot_miss_stats_graphs()` and `plot_miss_stats_diff_lru_graphs()` read MRC-like CSVs with rows of `cache_name,num_shard_bits,ghost_capacity,capacity,value`. They generate capacity-vs-value plots and value differences relative to `lru-0-0`.

`sanitize()` strips leading underscores from labels and replaces the uint64 max sentinel with `max`.

`read_data_for_plot_vertical()` and `read_data_for_plot_horizontal()` parse two CSV orientations into `x`, `labels`, and `label_stats`. `read_data_for_plot()` selects between them.

`plot_line_charts()` writes multi-page PDF line charts. `plot_stacked_bar_charts()` writes stacked bar charts. `plot_heatmap()` writes seaborn heatmaps from correlation output.

Higher-level functions dispatch graph families: `plot_timeline()`, `plot_correlation()`, `plot_reuse_graphs()`, `plot_percentage_access_summary()`, `plot_access_count_summary()`, and `plot_miss_ratio_timeline()`.

The `__main__` block expects an input directory containing experiment subdirectories and an output graph directory. It iterates each experiment directory, creates a matching output subdirectory, and calls all graph-family functions.

## Control Flow

The script imports matplotlib with the `Agg` backend for headless PDF generation. On execution, it validates two CLI arguments, lists the input directory, and skips entries that are not directories.

For each experiment subdirectory, it processes analyzer CSVs by suffix/prefix. Some graph functions open a `PdfPages` object and add one page per matching CSV file. Correlation processing first scans `*_correlation_input` files, computes Spearman correlations with pandas, writes `*_correlation_output`, and then plots those outputs as heatmaps.

The plotting contract depends heavily on filename suffixes from `block_cache_trace_analyzer.cc`, `block_cache_pysim.py`, and `block_cache_pysim.sh`.

## State And Persistence Behavior

The script writes PDF files under the output graph directory, preserving experiment subdirectory names. It also writes derived `*_correlation_output` CSV files back into the input CSV directories.

Global color state persists across all plots in a process. This helps keep a label's color stable, but it also means color assignment depends on processing order and can eventually exhaust the fixed 360-color list if many unique labels are seen.

## Dependencies And Integration Points

Runtime dependencies include Python standard modules plus `matplotlib`, `numpy`, `pandas`, and `seaborn`. It uses `matplotlib.backends.backend_pdf.PdfPages` and explicitly selects the non-interactive `Agg` backend.

The script is the consumer for CSVs emitted by the C++ analyzer (`mrc`, access timelines, reuse summaries, percentage summaries, skewness, correlation inputs) and for Python simulator aggregates (`ml_*_avgmb`, `ml_*_p95mb`, `ml_*_mrc`, and ML timelines).

## Risks And Edge Cases

The script uses older matplotlib/pandas APIs in places. `plt.xscale("log", basex=2)` is incompatible with newer matplotlib versions that use `base=2`, and `DataFrame.pivot("label", "corr", "value")` is incompatible with newer pandas keyword-only signatures.

`plot_miss_ratio_timeline(csv_result_dir, output_result_dir)` is called from the experiment loop with the top-level directories rather than the current experiment subdirectory, unlike other plot functions. This can cause missed files or output in the wrong directory.

`plot_miss_ratio_timeline()` calls the same miss-timeline plot twice with identical parameters, overwriting or duplicating work.

Line plotting uses `[int(x[i]) for i in range(len(x) - 1)]` and `label_stats[label_index][:-1]`, dropping the last x and y value. This may be intentional to avoid an open-ended bucket, but for timeline data it can silently omit real data.

Input parsing assumes non-empty CSVs and numeric values in all data cells. Empty files, headers only, NaNs outside correlation paths, or labels exceeding the color list can fail.

## Test Signals

There are no direct tests in this subset. The strongest validation signals would be golden CSV fixtures from the analyzer and simulator, smoke tests that generate PDFs with current matplotlib/pandas versions, and checks that each expected PDF appears under the correct experiment output directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_plot.py -->
