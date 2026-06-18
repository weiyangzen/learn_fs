# subset-b-008954 Research

Grouped research for WiredTiger Workgen runner files. Each section preserves the source path in the title and is bounded by the exact reconciliation markers for downstream splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_update_trigger.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_update_trigger.py

Purpose: executable Workgen workload derived from `read_write_heavy.wtperf` to drive cache-update pressure. It creates 10 file-backed tables plus a logging table, populates 1,000,000 rows, then runs an 85 percent read / 15 percent update mix intended to hit the WiredTiger cache update trigger.

Important APIs and functions: imports `Context`, `latency`, `get_cache_eviction_stats`, and helpers from `runner`, plus `wiredtiger` and `workgen`. It uses `Context.wiredtiger_open`, `Session.create`, `Table`, `Operation`, `Thread`, `Workload`, `op_multi_table`, `op_log_like`, `txn`, `Key.KEYGEN_PARETO`, and `ParetoOptions`. There are no local functions or classes.

Control flow: initialize a 10 GB cache connection with logging, statistics logging, session cap, eviction threads, and I/O capacity; create and populate 10 tables; create `table:log`; construct throttled log-update and log-read threads; construct a checkpoint thread; construct bursty transaction-wrapped update and search threads that do 10,000 operations then sleep; compute thread counts from `read_ops=85` and `total_thread_num=128`; run the workload for 200 seconds.

State and persistence: writes data to WiredTiger home, persists normal and log-like tables, advances commit timestamps through Workgen transaction options, and emits `cache_eviction.stat` and `latency.stat` under `context.args.home`. Checkpoints are scheduled every 30 seconds for 10 iterations.

Dependencies and integration: relies on the Workgen Python extension, WiredTiger Python bindings, and the `runner` package. The script is meant for benchmark/perf automation rather than import use.

Risks: a likely typo sets `thread_upd10k_sleep10.options.name = "Search"` instead of naming `thread_read10k_sleep10`; comments mention `eviction_updates_trigger=30` but the connection config does not set it. The workload is resource-heavy and assumes enough disk, cache, and sessions. `op_log_like` doubles write-like operations, so throttle values are approximate.

Test signals: successful `assert ret == 0`, periodic stats log JSON, `cache_eviction.stat` trigger counters, and latency buckets in `latency.stat`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_update_trigger.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/compress_ratio.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/compress_ratio.py

Purpose: compares update-heavy behavior across several WiredTiger block compressors and zlib page-image configurations. It creates one table per compression option, populates each with compressible values, then runs inserts and updates so statistics logs can reveal compression ratio and performance differences.

Important APIs and functions: defines local `op_append`, `make_op`, and `operations` helpers. `operations` builds an operation list across tables, optionally adding log-table operations and wrapping groups in transactions. It uses `Context`, `Table`, `Key`, `Value`, `Operation`, `Thread`, `Workload`, and Workgen throttling/name options.

Control flow: open a 2 GB cache connection with checkpoint/statistics logging and disabled WT logging; define compressor configs for none, lz4, snappy, zlib, zlib with one-page or ten-page `memory_page_image_max`, and zstd; create a table per compressor; set `value_compressibility=70`; populate 500,000 append-key rows per operation sequence; run two insert threads and ten update threads for 60 seconds with per-thread throttle 1000 and 1-second reporting.

State and persistence: creates persistent table files in the Workgen home. Checkpoints run every 20 seconds from connection config. No explicit latency file is written; the primary persistence artifacts are WiredTiger tables and statistics logs.

Dependencies and integration: requires the configured WiredTiger library to support the listed compressors. The comments note `extensions_config` can be used for externally built compressors, though this script leaves it commented.

Risks: compressor availability is build-dependent and unsupported compressor names fail during `create`. Local helper code duplicates `runner.core` concepts. Workload sizes and throttles are machine-tuned and can overwhelm smaller hosts. No cleanup or final close is present, relying on process exit.

Test signals: `assert ret == 0` after populate and workload, plus WiredTiger JSON statistics log for file sizes/compression counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/compress_ratio.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_insert_heavy.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_insert_heavy.py

Purpose: disaggregated-storage cache workload with an insert-heavy operation mix. It targets layered/disagg table behavior under frequent checkpoints, timestamped writes, and lagged readers.

Important APIs and functions: top-level Workgen script using `Context`, `Table`, `Operation`, `Thread`, `Workload`, `txn`, `latency.workload_latency`, and `Connection.set_timestamp`. It also reads `WT_BUILDDIR` to load the palite page-log extension.

Control flow: open a leader disaggregated connection with `precise_checkpoint=true`, 8 GB cache, palite page log, and extended `cache_stuck_timeout_ms`; set stable timestamp to 1; create `table:test` as `type=layered,block_manager=disagg`; populate 500,000 rows with 8 threads; create snapshot update and insert transaction operations using commit timestamps; create 10 reader threads with read timestamp lags from 60 to 195 seconds; checkpoint every 10 seconds; run a 15-minute workload with 90 insert threads, 5 update threads, one reader per lag, and checkpointing.

State and persistence: persists layered/disagg data and page-log state in the WT home, advances oldest/stable timestamps every second using Workgen options, and writes `latency.out`.

Dependencies and integration: requires `WT_BUILDDIR/ext/page_log/palite/libwiredtiger_palite.so` and a WiredTiger build supporting disaggregated storage. Integrates with benchmark automation through output latency and statistics.

Risks: `WT_BUILDDIR` missing produces an invalid extension path. Comments say 600 seconds for checkpoint count while `run_time` is 900 seconds. The script prints the workload return value but does not assert it after run, unlike populate. Resource cost is high.

Test signals: populate assertion, workload return print, timestamped stats, checkpoint progress, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_insert_heavy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_heavy.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_heavy.py

Purpose: read-heavy variant of the disaggregated cache benchmark. It stresses timestamped reads close to stable timestamp while maintaining a small amount of timestamped insert/update churn and frequent checkpoints.

Important APIs and functions: uses `Context.wiredtiger_open`, `Connection.set_timestamp`, `Session.create`, `Table`, `Operation`, `txn`, `Thread`, `Workload`, and `latency.workload_latency`. No local helpers are defined.

Control flow: open a palite-backed disaggregated leader with 8 GB cache and precise checkpointing; create a layered/disagg table; populate 500,000 rows with 8 insertion threads; create 5 update threads and 5 insert threads, each using snapshot transactions with commit timestamps; create readers at ten timestamp lags, each multiplied by 9 threads; checkpoint every 10 seconds for 90 cycles; run for 900 seconds with report interval 10 and timestamp advancement every second.

State and persistence: uses WT home data files and disaggregated page-log artifacts, with stable timestamp initialized to 1 and oldest/stable timestamps advanced by Workgen. Outputs `latency.out`.

Dependencies and integration: requires the palite shared library under `WT_BUILDDIR`, the Workgen extension, and WiredTiger disaggregated storage features. Intended as part of a family of disagg cache workloads for comparative runs.

Risks: no assertion is made on final workload return. Missing `WT_BUILDDIR` or incompatible build breaks open. Running many timestamped readers can expose old-history retention costs and disk pressure. Checkpoint comments and run-time comments should be checked if changing durations.

Test signals: populate assert, printed workload return, periodic report/stats, timestamp behavior, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_heavy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_write.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_write.py

Purpose: balanced read/write disaggregated cache benchmark. It mixes timestamped inserts, updates, lagged reads, and checkpoints against one layered/disagg table to study cache behavior under roughly equal read/write pressure.

Important APIs and functions: uses the same Workgen and runner APIs as the other disagg cache scripts: `Context`, `Table`, `Operation`, `txn`, `Thread`, `Workload`, timestamp lag options, and `latency.workload_latency`.

Control flow: open a palite disaggregated leader connection; initialize stable timestamp; create a small-page layered table; populate 500,000 rows; build commit-timestamp snapshot update and insert operations; build 10 reader operation templates with read timestamp lags; assemble 50 update threads, 50 insert threads, and 5 copies of each lagged reader template; add a 10-second checkpoint loop; run for 900 seconds.

State and persistence: persistent state includes layered table pages, disaggregated page-log data, checkpoint metadata, and history needed for lagged reads. Writes `latency.out` in the configured home.

Dependencies and integration: depends on `WT_BUILDDIR` for `libwiredtiger_palite.so`. It is structurally aligned with insert/read/update-heavy variants, making it suitable for comparative performance dashboards.

Risks: comment says populate 1M rows but `icount` is 500,000. The run return is printed rather than asserted. `threads = 50 * tupdate + 50 * tinsert` yields 100,000 writes before reader multiplication, so comments about exact percentages should be verified against Workgen repetition semantics.

Test signals: populate assertion, workload return print, WiredTiger stats log, checkpoint cadence, timestamp advancement, and latency buckets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_read_write.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_update_heavy.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_update_heavy.py

Purpose: update-heavy disaggregated cache workload. It emphasizes update chains and history/cache pressure on layered disaggregated storage, with small insert/read side traffic and frequent checkpoints.

Important APIs and functions: top-level Workgen use of `Context`, `Operation.OP_UPDATE`, `Operation.OP_INSERT`, `Operation.OP_SEARCH`, `txn`, `Thread`, `Workload`, timestamp lag options, `Connection.set_timestamp`, and latency output.

Control flow: open a palite-backed disaggregated leader; create one layered/disagg table with 4 KB internal/leaf pages; populate 500,000 rows; wrap update and insert operations in snapshot transactions with commit timestamps; build read timestamp operations for lags 60-195 seconds; schedule checkpoints every 10 seconds; run 90 update thread copies, 5 insert thread copies, 10 reader threads, and checkpoint thread for 900 seconds.

State and persistence: creates persistent disaggregated table state and page-log state, maintains history for timestamped reads, advances oldest/stable timestamps, and writes `latency.out`.

Dependencies and integration: requires a WiredTiger build with disaggregated storage and the palite extension. It integrates with the disagg benchmark family through identical connection/table setup and varied thread mix.

Risks: missing `WT_BUILDDIR` breaks extension loading. The run result is not asserted. Heavy updates can grow history store/page-log state and disk usage. Comments again mention 600 seconds for checkpoint count despite 900-second run.

Test signals: populate assertion, printed workload return, checkpoint and statistics logs, timestamp advancement, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/disagg_cache_update_heavy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/evict-btree-hs.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/evict-btree-hs.py

Purpose: stresses disk access to the WiredTiger history store and eviction by combining a low cache, large values, skewed Pareto access, log-like writes, and long-running transactions.

Important APIs and functions: uses `op_multi_table`, `op_log_like`, `txn`, `sleep`, `Key.KEYGEN_PARETO`, `ParetoOptions`, `Operation.OP_LOG_FLUSH`, `Workload`, and `latency.workload_latency`. No local functions.

Control flow: open a 1 GB cache connection with logging, 12 eviction threads, statistics log, and session cap 800; create one large-value file table; populate 500,000 rows using 40 threads; create a log table; define Pareto search, insert, throttled update, and long transaction threads; define a log flush thread; run 400 search threads, 100 insert threads, 10 update threads, 100 long-transaction threads, and logging thread for 400 seconds.

State and persistence: persistent file table and log table are created. Long transactions keep versions pinned and cause history-store/cache pressure. Logging is enabled for the connection and log table, and latency is written to `latency.out`.

Dependencies and integration: generated from a wtperf configuration and integrates with Workgen runner helpers to emulate wtperf options.

Risks: comments document much larger original wtperf settings; this script is reduced but still resource-heavy. Long transaction expression `txn(((search_op + update_op) * 1000 + sleep(0.1)) * 10000)` can create large operation structures and long pinned histories. Disk usage is explicitly constrained by shortening runtime.

Test signals: populate and workload assertions, statistics log, latency output, and max latency threshold of 50 seconds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/evict-btree-hs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_dynamic_tables.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_dynamic_tables.py

Purpose: demonstrates Workgen dynamic table creation and deletion while workload operations target random tables.

Important APIs and functions: uses `Context`, `Key`, `Value`, `Operation`, `Thread`, and `Workload`. The key distinction is constructing operations without an explicit `Table`, letting Workgen select random dynamic tables. Workload options `create_prefix`, `create_interval`, `create_count`, `create_trigger`, `create_target`, `max_num_files`, `drop_interval`, `drop_count`, `drop_trigger`, and `drop_target` drive dynamic DDL.

Control flow: open a default WT home, build random-table insert/update/search threads, create a workload running for 300 seconds, configure creation when database size falls below 100 MB until 200 MB, configure drops when size exceeds 250 MB until 75 MB, then run.

State and persistence: dynamically creates and drops tables with prefix `dynamic_` in the WiredTiger home. The workload state is driven by database size thresholds and maximum file count.

Dependencies and integration: validates Workgen dynamic table features rather than a specific WT storage algorithm. It can pair with `validate_mirror_tables.py` when dynamic mirroring is enabled elsewhere, though this file does not enable mirrors directly.

Risks: operations on random tables depend on Workgen's dynamic-table state; empty table sets during startup/shutdown could expose edge cases. Size thresholds are workload-environment dependent.

Test signals: single `assert ret == 0`, successful dynamic DDL over 300 seconds, and absence of Workgen errors while tables are changing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_dynamic_tables.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare.py

Purpose: small prepared-transaction example combining inserts prepared with stable timestamp, updates with commit timestamps, and lagged timestamp reads.

Important APIs and functions: uses `txn`, Workgen transaction attributes `read_timestamp_lag`, `use_prepare_timestamp`, and `use_commit_timestamp`, plus workload timestamp options `oldest_timestamp_lag`, `stable_timestamp_lag`, and `timestamp_advance`.

Control flow: open a 500 MB cache connection; create one string table; populate 5,000 rows; build a read transaction at read timestamp lag 30; build snapshot insert transaction using prepare timestamp; build snapshot update transaction using commit timestamp; run 30 copies of each operation type for 50 seconds; write latency output.

State and persistence: table data persists in WT home for the process. Workgen advances timestamps every second with oldest lag 40 and stable lag 20, supporting prepared/commit timestamp semantics. `latency.out` records operation latency.

Dependencies and integration: simple benchmark/example for Workgen timestamp transaction options; imports `time` only for elapsed time printing.

Risks: small table and high thread count can amplify conflicts or not-found behavior depending on Workgen key generation. Report interval is 500 seconds, longer than run time, so periodic reports are effectively suppressed.

Test signals: populate/workload assertions, elapsed-time print, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare_evict_reconcile.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare_evict_reconcile.py

Purpose: prepared transaction workload tuned to force eviction/reconciliation pressure. It uses large keys/values, small leaf pages, low cache target, and timestamped prepared writes.

Important APIs and functions: Workgen APIs for `Operation.OP_SEARCH`, `OP_INSERT`, `OP_UPDATE`, `txn`, transaction timestamp flags, and latency output. It uses direct WT table configuration for page size and allocation.

Control flow: open a 500 MB cache connection with `eviction_target=60`; create one table with 4 KB leaves and 7 KB values; populate 5,000 rows; build read timestamp lag 300 readers, prepared insert writers, and commit timestamp updaters, each repeated 5,000 times; run 30 copies of each for 300 seconds with oldest lag 400 and stable lag 20.

State and persistence: writes large page images and history to a file table, advances timestamps, and writes `latency.out`. No explicit checkpoint thread is configured; normal WT behavior applies.

Dependencies and integration: extends `example_prepare.py` toward cache/eviction behavior. Useful as a smaller reproducer for prepared reconciliation paths.

Risks: final workload return is not asserted. Large values with small leaf pages can create intense cache pressure. Report interval exceeds runtime, limiting progress visibility.

Test signals: populate console messages, successful workload completion, timestamp behavior, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_prepare_evict_reconcile.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_simple.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_simple.py

Purpose: minimal Workgen example showing context setup, table creation, insert operations, repeated operation multiplication, workload execution, and optional verbose table display.

Important APIs and functions: defines `show(tname, s, args)` to print table contents when `--verbose` is set. Uses `Context.wiredtiger_open`, `Session.create`, `Table`, `Key.KEYGEN_APPEND`, `Value`, `Operation.OP_INSERT`, `Thread`, and `Workload`.

Control flow: open a 1 GB cache WT home through `Context`; create `table:simple`; run one insert workload; optionally print contents; run another workload with five repeated inserts; print again.

State and persistence: data persists in the temporary/default Workgen home for the script. `Context` handles home cleanup unless command-line options override it. No latency file is generated.

Dependencies and integration: demonstrates runner initialization and Workgen basics; intended as a direct example rather than perf workload.

Risks: verbose output can be noisy if repetition is increased. Uses `from runner import *` and Workgen globals for simplicity.

Test signals: two `assert ret == 0` checks and visible inserted records under `--verbose`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_simple.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_txn.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_txn.py

Purpose: simple transactional write example. It populates a table and then mixes readers with transaction-wrapped two-operation insert writers.

Important APIs and functions: uses `txn(opwrite * 2)` to wrap repeated insert operations in a Workgen transaction. Other APIs are `Context`, `Table`, `Operation`, `Thread`, `Workload`.

Control flow: open a 500 MB cache database; create one string table; populate 500,000 rows; create one search thread and one transaction-wrapped double-insert writer; run eight readers and two writers for 10 seconds with 5-second reports.

State and persistence: table content persists in the WT home and grows during the write workload. No explicit timestamps, checkpoints, or latency files are used.

Dependencies and integration: demonstrates `runner.core.txn` and Workgen transaction grouping. Useful as a smoke test for transaction support.

Risks: append inserts after a large populate can be resource-sensitive. Without timestamp or isolation config, semantics are default transaction behavior.

Test signals: populate and workload assertions plus periodic report output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_txn.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/insert_stress.py

Purpose: stresses insert paths with very large values, mixed key generators, and concurrent transactional reads.

Important APIs and functions: uses direct `Operation.OP_INSERT` variants with uniform and append keys, `Value` sizes 130 KB and 100 bytes, `op_group_transaction` for grouped read transactions, and `Workload`.

Control flow: open a 4 GB cache connection with checkpoint every 10 seconds, snappy compression, disabled logging, and statistics logging; create `file:test.wt` with `leaf_value_max=64MB`; populate 500 rows; define a thread that does a large uniform insert, ten small uniform inserts, and a large append insert; define a read transaction made from 100 search operations; run eight insert threads plus one read thread for 240 seconds.

State and persistence: creates a compressed file table with large values and frequent checkpointing. The table key range is 100 million. No explicit latency output is written.

Dependencies and integration: relies on snappy compressor support and Workgen's large-value generation. Part of stress workload suite.

Risks: large value sizes drive disk and cache pressure. Insert operations with uniform keys may hit duplicate-key or update-like behavior depending on Workgen semantics. No latency file despite benchmark nature.

Test signals: populate and workload assertions, WiredTiger stats log, and checkpoint behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_stress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_test.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/insert_test.py

Purpose: functional example/test for operation addition, multiplication, append key generation, truncate effects, error handling, and workload options help.

Important APIs and functions: local `tablename`, `show`, and `expectException`; Workgen `Operation`, `Key`, `Value`, `Table`, `Thread`, `Workload`; direct `Session.truncate`.

Control flow: create two tables; run and display a single insert workload; truncate behind Workgen's context; build multiplied operation groups across two tables and run; truncate both; mutate operation lists with `+=` and `*=` and run; print workload/thread representations; validate expected exceptions for missing value and invalid key sizing; print workload options help.

State and persistence: table contents are repeatedly inserted and truncated. The script intentionally lets WiredTiger state and Workgen's internal key memory diverge to demonstrate insert-only tolerance.

Dependencies and integration: a developer-facing Workgen sanity/example script rather than a perf run. Uses assertions and expected exceptions as test signals.

Risks: broad `except BaseException` in `expectException` catches more than ordinary failures. Some exception behavior is deferred to `Workload.run`, so invalid setup may not fail where a reader expects.

Test signals: successful RUN1-3 assertions, expected exceptions in RUN4, printed data, and options help.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/insert_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/maintain_low_dirty_cache.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/maintain_low_dirty_cache.py

Purpose: machine-tuned workload intended to maintain dirty cache around WiredTiger's 5 percent eviction target on AWS perf hosts while driving mixed multi-table reads, inserts, and updates.

Important APIs and functions: local `op_append`, `make_op`, and `operations` create multi-table operation sequences with optional log table and transaction grouping. Uses Workgen throttles, thread names, `latency.workload_latency`, and connection statistics.

Control flow: open a 2 GB cache connection with checkpoint every 8 seconds, snappy compression, disabled logging, and stats logging; create 8 data tables and a log table; populate 1,000,000 append rows; build log-like insert/update operations and grouped read transactions; run 4 insert threads, 9 update threads, and 90 read threads for 1,200 seconds with 1-second reporting and 5-second samples.

State and persistence: writes 8 data tables, a log-like table, checkpoints frequently, and writes `latency.out` under the connection home.

Dependencies and integration: comparator/variant of `multi_btree_heavy_stress.py` with production perf-host tuning. Requires snappy support.

Risks: comments warn tuning is machine-dependent. Long 20-minute runtime and large populate can consume disk. Log-like table additions multiply write volume.

Test signals: populate/workload assertions, statistics log, per-thread throughput names, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/maintain_low_dirty_cache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/many-dhandle-stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/many-dhandle-stress.py

Purpose: stresses WiredTiger dhandle/file-manager behavior with 15,000 tables, idle-close cycling, checkpoints, and access spread across many handles.

Important APIs and functions: uses `op_populate_with_range` for range-partitioned population, `op_multi_table` for multi-table access, Pareto key generation, workload option `max_idle_table_cycle`, and latency output. It also appends a hard-coded legacy path to `sys.path`.

Control flow: open a 10 GB cache connection with file manager idle close time 30, session max 1000, all/clear statistics, and JSON stats on close; create 15,000 tables; populate 15,000,000 rows using range partitioning with random range 1,500,000,000; create throttled Pareto insert threads, Pareto read threads, and a checkpoint thread; run for 900 seconds with 10 insert threads and 10 read threads.

State and persistence: creates tens of thousands of table files and statistics output. Workload tracks idle-table cycle warning threshold at 2 seconds. Writes `latency.out`.

Dependencies and integration: generated from `many-dhandle-stress.wtperf`; tests file handle and dhandle scaling. The hard-coded `sys.path` is unnecessary when run from the runner directory and may be stale.

Risks: very high file count can exceed OS limits or disk inode budgets. `max_latency=60` is much lower than comments from wtperf and may flag warnings on slower hosts. The shebang is malformed as `#/usr/bin/env python`.

Test signals: assertions, idle-table cycle warnings/fatal option, statistics log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/many-dhandle-stress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_base.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_base.py

Purpose: shared base class for prefetch verification microbenchmarks. It centralizes database setup, population, and prefetch-related statistics collection.

Important APIs and functions: class `microbenchmark_prefetch` with `__init__`, `populate`, and `print_prefetch_stats`. It uses `wiredtiger.stat.conn.block_read` and `cache_read_app_count`, `Context`, `Table`, `Operation.OP_INSERT`, `Thread`, and `Workload`.

Control flow: constructor opens a 1 GB cache connection with 12 eviction threads, statistics for all/file sources, and `prefetch=(available=true,default=false)`; creates one `table:test_prefetch0` file table with key size 12 and value size 138; `populate` inserts 12,000,000 rows; `print_prefetch_stats` opens a statistics cursor, prints block/cache-read counters, and writes `prefetch_stats.out`.

State and persistence: creates a large single table and statistics artifacts in the WT home. The class stores `context`, `conn_config`, `conn`, `session`, `nrows`, `table`, and optional `workload`.

Dependencies and integration: imported by `microbenchmark_prefetch_off_verify.py` and `microbenchmark_prefetch_on_verify.py`. Depends on WiredTiger prefetch configuration and stats IDs.

Risks: 12 million rows can be slow/heavy. `print_prefetch_stats` writes only blocks read to file while printing both counters, so downstream tools may miss `cache_read_app_count`. File handle is manually closed but would benefit from context manager.

Test signals: populate assertion, printed statistics, and `prefetch_stats.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_off_verify.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_off_verify.py

Purpose: measures verify workload behavior when prefetch is explicitly disabled.

Important APIs and functions: imports `microbenchmark_prefetch`, constructs `Operation.OP_VERIFY` with config `prefetch=(enabled=false)`, and uses `Workload`.

Control flow: instantiate base, populate data, close and reopen the connection to flush cache, reopen a session, define and call `run_workload`, run verify for 300 seconds, print/write prefetch stats, close resources.

State and persistence: data table persists across connection reopen. Reopen clears cache to make verify reads meaningful. Statistics are collected after the verify run and written to `prefetch_stats.out`.

Dependencies and integration: paired with `microbenchmark_prefetch_on_verify.py`; comparison expects fewer blocks read when prefetch is off.

Risks: full 12-million-row populate plus 5-minute verify is expensive. The table object is reused across reopen, relying on Workgen table URI state rather than live cursor/session state.

Test signals: verify `assert ret == 0`, printed "Start/Finished verifying", and lower blocks-read stats relative to the prefetch-on variant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_off_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_on_verify.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_on_verify.py

Purpose: measures verify workload behavior when prefetch is explicitly enabled.

Important APIs and functions: uses `microbenchmark_prefetch` from the base module and constructs `Operation.OP_VERIFY` with `prefetch=(enabled=true)`.

Control flow: create and populate the benchmark database, close/reopen the connection to flush cache, run a 300-second verify workload with prefetch enabled, print prefetch stats, and close session/connection.

State and persistence: persistent populated table is reused after reopen. Statistics cursor samples connection counters after verify and writes `prefetch_stats.out`.

Dependencies and integration: intended to be compared with the off variant; expected outcome is more blocks read or different throughput when prefetch is on.

Risks: comments say reopen turns prefetch on, but prefetch is actually selected in the verify operation config while the connection default remains false. Runtime and data volume are high.

Test signals: workload assertion and prefetch stats, especially `blocks_read` relative to the off run.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_on_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_fast_truncate.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_fast_truncate.py

Purpose: rollback-to-stable microbenchmark for fast truncate. It creates stable data, evicts it, checkpoints, truncates all rows at an unstable timestamp, then measures checkpoint plus RTS latency.

Important APIs and functions: imports `timestamp_str` and `show` from `microbenchmark_rts_unstable_content`; uses direct WiredTiger sessions/cursors, `debug=(release_evict)`, `Session.truncate`, `Operation.OP_CHECKPOINT`, `Operation.OP_RTS`, and latency output.

Control flow: create 1,000,000 rows at commit timestamp 10 after setting stable timestamp 5; evict rows with a debug cursor; checkpoint; open a second session and truncate the full key range at timestamp 15; run a Workgen workload containing checkpoint then RTS; emit `rts_fast_truncate.out`.

State and persistence: table contains data, then a timestamped truncate newer than stable. RTS should roll back unstable truncate effects. Eviction forces disk/read behavior.

Dependencies and integration: depends on RTS operation support in Workgen and helper display functions from the unstable-content module.

Risks: large explicit Python loops over 1M rows can be slow. Uses `show(uri, session, context.args)` after operations with an older session; fine for verbose display but can be expensive. Output filename is relative, not under `context.args.home`.

Test signals: workload assertion, latency file, optional verbose table contents, and no eviction search errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_fast_truncate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_large_hs.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_large_hs.py

Purpose: rollback-to-stable microbenchmark for a large history store. It writes stable and unstable content, then updates all rows to push versions into the history store before measuring RTS.

Important APIs and functions: local `large_updates(session, uri, value, start, end, timestamp)`, direct timestamped transactions, `Connection.rollback_to_stable`, `Operation.OP_RTS`, and `latency.workload_latency`.

Control flow: create table; write 1,000,001 stable-ish rows at timestamp 5 for the upper tenth and unstable rows at timestamp 10 for lower tenth; checkpoint; update every row to `"bbbb"` at timestamp 15 to create history; checkpoint; set stable timestamp 5; call direct `rollback_to_stable`; then run a Workgen RTS operation and write `rts_large_hs.out`.

State and persistence: intentionally creates large history-store content and unstable versions. Direct RTS before Workgen RTS changes database state before measurement, so the Workgen RTS may measure a second/no-op path.

Dependencies and integration: uses helper functions from `microbenchmark_rts_unstable_content`.

Risks: very high row count and one transaction per row are extremely expensive. Opens a cursor inside each loop iteration for the second update phase but closes only the last cursor, creating possible resource pressure. Calls `show(uri, session, context.args)` after `session.close()`, which is a likely bug.

Test signals: workload assertion and `rts_large_hs.out`; direct `rollback_to_stable` should not fail.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_large_hs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_many_files.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_many_files.py

Purpose: RTS/checkpoint microbenchmark for a very large number of files/tables.

Important APIs and functions: direct `Session.create`, cursors, debug eviction cursor `release_evict`, `Operation.OP_CHECKPOINT`, `Operation.OP_RTS`, and latency output.

Control flow: create 100,000 tables named `table:rts_many_filesN`; insert one row into each; evict each row through a debug cursor; run a Workgen workload containing checkpoint then RTS; write `rts_many_files.out`; optionally display data using imported `show`.

State and persistence: creates many WiredTiger table files and associated metadata. Eviction tries to remove pages from cache before checkpoint/RTS measurement.

Dependencies and integration: imports helpers from `microbenchmark_rts_unstable_content`, though timestamps are not used. Stresses metadata/file traversal rather than value volume.

Risks: 100,000 tables can exceed filesystem, metadata, open cursor, or time budgets. The transaction commit condition checks `if i % 56 == 0` inside the row loop, using table index instead of row index; with `nrows=1` this is harmless but odd. `show(uri, session, ...)` targets base URI without suffix, likely not an existing table.

Test signals: workload assertion, no eviction search exceptions, and `rts_many_files.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_many_files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_overflow_pages.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_overflow_pages.py

Purpose: RTS microbenchmark focused on overflow pages by using tiny page sizes and values large enough to overflow.

Important APIs and functions: direct timestamped writes, `debug=(release_evict)`, `Operation.OP_RTS`, and latency output.

Control flow: open database and set stable timestamp 5; create table with 512-byte allocation and leaf pages; insert 550,000 rows at timestamp 10 with repeated string values; evict rows; checkpoint; run a Workgen RTS operation and write `rts_overflow_pages.out`.

State and persistence: creates overflow-page-heavy on-disk state and unstable timestamped data relative to stable timestamp. RTS should process these unstable updates.

Dependencies and integration: imports `timestamp_str` and `show` helpers. Integrates with other RTS microbenchmarks as a latency-output comparator.

Risks: row-by-row eviction and small pages are expensive. Stable timestamp remains 5 while writes are at 10, so all content is unstable; any semantic expectation should account for full rollback potential. Output file is relative.

Test signals: workload assertion, no eviction failure exceptions, latency file, and optional verbose display.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_overflow_pages.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_unstable_content.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_unstable_content.py

Purpose: base/simple RTS microbenchmark and helper provider for other RTS scripts. It creates unstable timestamped content and measures checkpoint plus RTS latency.

Important APIs and functions: defines `show(uri, s, args)` for verbose cursor printing and `timestamp_str(t)` for timestamp formatting. In main, uses `Context`, direct WT transactions, `Operation.OP_CHECKPOINT`, `Operation.OP_RTS`, `Workload`, and `latency.workload_latency`.

Control flow: when run as a script, open database, set stable timestamp 5, create `table:rts_unstable_content`, insert 10 rows at timestamp 10, run checkpoint then RTS as Workgen operations, write `rts_unstable_content.out`, and optionally show rows.

State and persistence: table content is newer than stable timestamp and therefore subject to rollback. It also acts as a utility module for other RTS benchmarks.

Dependencies and integration: imported by fast truncate, large history store, many files, and overflow pages modules. The helper functions are intentionally lightweight.

Risks: timestamp formatting is a trivial decimal string and may not cover hex timestamp formats if needed elsewhere. The module mixes helper definitions with executable benchmark guarded by `__main__`, which is acceptable but makes imports depend on no top-level side effects.

Test signals: workload assertion, latency file, optional verbose table output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_rts_unstable_content.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_base.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_base.py

Purpose: shared base class for tiered-storage checkpoint microbenchmarks.

Important APIs and functions: class `microbenchmark_tiered` with `__init__`, `populate`, `create_bucket`, `set_checkpoint_thread`, `print_stats`, and `run_workload`. It uses `op_multi_table`, `op_group_transaction`, Workgen thread composition, `wiredtiger.stat.conn.flush_tier`, and latency output.

Control flow: constructor opens a `dir_store` tiered-storage connection with a bucket directory, log/statistics enabled, and early-loaded dir_store extension; creates four file tables; prepares read, update, and insert thread templates across all tables. `populate` inserts 50,000 rows with grouped transactions. `run_workload` runs 8 readers, 2 updaters, 2 inserters, and a caller-provided checkpoint thread for 300 seconds. `print_stats` asserts more than two `flush_tier` calls.

State and persistence: creates WT home, local bucket directory, four tiered tables, logs, statistics, and `latency.out`. `create_bucket` ensures local object-store directory exists before open.

Dependencies and integration: imported by with-flush and without-flush scripts. Requires `./ext/storage_sources/dir_store/libwiredtiger_dir_store.so` relative to run directory/build.

Risks: constructor parameter `extension` is stored but not used to vary config; config always names `dir_store`. Missing extension or wrong working directory fails open. `print_stats` is meaningful only for workloads that force flush tier.

Test signals: populate/run assertions, `flush_tier > 2` assertion for flush variant, statistics log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_with_flush.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_with_flush.py

Purpose: tiered-storage benchmark measuring checkpoints when alternating normal checkpoints with forced `flush_tier`.

Important APIs and functions: imports `microbenchmark_tiered`, builds a checkpoint thread using `Operation.OP_SLEEP`, `Operation.OP_CHECKPOINT`, and checkpoint config `flush_tier=(enabled,force)`.

Control flow: create base tiered benchmark, populate tables, set a checkpoint operation sequence of sleep 30, checkpoint, sleep 30, forced flush-tier checkpoint, then run the standard mixed workload and assert flush-tier stats.

State and persistence: writes table data to WT home and tiered bucket, triggers object flushes, and writes latency/statistics artifacts.

Dependencies and integration: direct pair with `microbenchmark_tiered_checkpoint_without_flush.py`; comparison isolates forced flush-tier overhead.

Risks: depends on base class dir_store extension path. `print_stats` expects at least three flushes during 300-second run; slow flushes or altered timing may fail despite correct behavior.

Test signals: base assertions, `flush_tier > 2`, statistics logs, and latency file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_with_flush.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_without_flush.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_without_flush.py

Purpose: tiered-storage benchmark measuring normal checkpoint latency without explicit flush-tier calls.

Important APIs and functions: uses `microbenchmark_tiered` and a simple checkpoint thread `sleep(30) + checkpoint`.

Control flow: instantiate base benchmark, populate four tables, set the checkpoint thread, and run the base mixed workload. It does not call `print_stats` because no forced flush-tier count is expected.

State and persistence: creates tiered tables and local bucket state through the base class, emits latency/statistics artifacts, and checkpoints every 30 seconds.

Dependencies and integration: control workload for the with-flush variant.

Risks: same extension/working-directory risks as the base. Without a flush assertion, success only means workload completion, not that no tiered flush occurred due to other mechanisms.

Test signals: populate and workload assertions plus latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_tiered_checkpoint_without_flush.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multi_btree_heavy_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/multi_btree_heavy_stress.py

Purpose: compact Workgen proof-of-concept matching a multi-btree read-heavy wtperf workload, scaled down for testing.

Important APIs and functions: local `op_append`, `make_op`, and `operations` helpers; uses optional log table, `Key.KEYGEN_APPEND`, `KEYGEN_UNIFORM`, `Value`, throttled/named threads, and latency output.

Control flow: open a 1 GB cache connection with snappy compression, checkpointing, and stats logging; create 8 tables plus a log table; populate 20,000 append-operation groups; build insert, update, and grouped read operations across tables; throttle inserts/updates at 250 and reads at 1000; run 1 insert, 1 update, and 2 read threads for 30 seconds.

State and persistence: creates compressed data and log-like tables, checkpoints, and writes `latency.out`.

Dependencies and integration: benchmark precursor for heavier variants such as `maintain_low_dirty_cache.py`. Requires snappy support.

Risks: helper code duplicates runner functionality and may diverge. Comments preserve much larger wtperf settings, so readers must use actual constants. TODO questions log table config.

Test signals: populate/workload assertions, printed latency path, stats log, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multi_btree_heavy_stress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multiversion.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/multiversion.py

Purpose: simple Workgen insert example with optional WiredTiger compatibility configuration for older release testing.

Important APIs and functions: local `show(tname, s)` and `create_compat_config(args)`. Adds `--release` argument with choices `4.2` and `4.4`, calls `context.initialize()` before opening, and uses `Operation.OP_INSERT`.

Control flow: parse release argument; open a 1 GB cache WT home with compatibility suffix based on release; create `table:simple`; run one append insert workload, show contents; run five more inserts and show contents.

State and persistence: creates data under a compatibility-mode WT home when requested. No latency output.

Dependencies and integration: helps test multiversion/compatibility behavior in Workgen runner scripts.

Risks: `create_compat_config` returns strings with compatibility releases that may be invalid for newer WiredTiger builds. The open config concatenates `"create,cache_size=1G,"` and the helper string that begins with a comma, producing a double comma for release cases; WT config parsing may tolerate this but it is untidy.

Test signals: workload assertions and printed records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multiversion.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/prepare_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/prepare_stress.py

Purpose: prepared-transaction stress workload derived from `evict-btree-hs.py`, aimed at cache/eviction behavior around prepared updates, timestamped reads, and long-running snapshot transactions.

Important APIs and functions: uses `txn`, `op_multi_table`, `op_log_like`, `sleep`, Workgen transaction flags `use_prepare_timestamp`, `use_commit_timestamp`, `read_timestamp_lag`, workload timestamp lag/advance options, and latency output.

Control flow: open 1 GB cache connection with logging and eviction threads; create one large-value table with table logging disabled; populate 500,000 rows in snapshot transactions; create a logging table; define read timestamp Pareto operations, prepared insert operations, commit-timestamp update operations, long-running search/update snapshot operations, and log flushes; run 50 readers, 50 prepared inserters, 10 updaters, 100 long-running threads, and logging for 400 seconds.

State and persistence: creates data and log tables, uses prepared and commit timestamps, advances oldest/stable timestamps every second, pins history with lagged reads/long transactions, and writes `latency.out`.

Dependencies and integration: stress variant of history-store eviction script for prepared transactions.

Risks: high thread count and timestamped prepared operations can be resource-intensive. Comments call update operations "Insert operations" in one place. Log-like operations double write-like activity.

Test signals: populate/workload assertions, elapsed time print, statistics log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/prepare_stress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_storms.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_storms.py

Purpose: creates alternating bursts of read and write activity over many tables to study latency/throughput storms.

Important APIs and functions: uses `op_multi_table`, `op_log_like`, `Operation.OP_SLEEP`, `OP_CHECKPOINT`, `OP_LOG_FLUSH`, `Thread`, `Workload`, and latency output.

Control flow: open 2 GB cache connection with logging, stats, and I/O capacity; create 100 snappy-compressed tables; populate 4,000,000 rows across tables; create a log table; build throttled update/read background threads, checkpoint/log-flush threads, and four burst threads that perform 10,000 or 80,000 operations followed by sleeps; run 80 background writers, 80 background readers, 40 burst threads, checkpoint, and logging for 900 seconds.

State and persistence: stores 100 data tables and log table; connection logging/statistics are enabled; latency output is written.

Dependencies and integration: derived from wtperf read/write-heavy config and adapted to Workgen helper functions.

Risks: actual operation volume is inflated by `op_log_like`; high table count and large values need significant disk/cache. Burst synchronization is initially high but expected to drift.

Test signals: populate/workload assertions, `latency.out`, statistics log, and visible storm patterns in sample output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_storms.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_long.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_long.py

Purpose: long synchronized read/write workload that alternates phases of readers, writers, both, and idle periods against a background load.

Important APIs and functions: uses `timed(seconds, ops)` and `sleep(seconds)` runner helpers, `Thread.synchronized = True`, multi-table/log-like helpers, and latency output.

Control flow: create/populate 100 snappy tables and a log table; build throttled background update/read threads, checkpoint and log-flush threads; build synchronized writer thread active for 240 seconds then idle 240 seconds; build synchronized reader thread active in a 120/240/120-second pattern; run 20 background writers, 20 background readers, 50 synchronized writers, 50 synchronized readers, checkpoint, and logging for 1,800 seconds.

State and persistence: persistent multi-table data/log state, periodic checkpoints/log flushes, statistics and latency artifacts.

Dependencies and integration: demonstrates Workgen synchronization and timed operation helpers.

Risks: long 30-minute runtime and high thread count. Imported `sys` is unused. Thread synchronization behavior depends on Workgen scheduler semantics; modifications can easily change phase alignment.

Test signals: workload assertions, phase patterns in reports, statistics log, and `latency.out`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_long.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_short.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_short.py

Purpose: shorter synchronized read/write storm workload with periodic collective alignment across read and write groups.

Important APIs and functions: uses `timed`, `sleep`, `Thread.synchronized`, `op_multi_table`, `op_log_like`, checkpoint/log flush operations, and latency output.

Control flow: setup mirrors the long sync workload: 100 tables, 4,000,000 populate rows, log table, throttled background update/read threads. It then creates synchronized write groups on 10- and 20-second cycles and read groups on 8- and 16-second cycles. Runs background, synchronized, checkpoint, and logging threads for 900 seconds.

State and persistence: persistent tables, log table, logging/statistics, and `latency.out`.

Dependencies and integration: compact synchronization demo for Workgen scheduling and phase-driven workload behavior.

Risks: high operation count and log-like amplification. Imported `sys` is unused. Because all synchronized threads start aligned, early samples can show stronger synchronization than later samples.

Test signals: assertions, report samples showing 80-second collective cycles, stats log, and latency output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/read_write_sync_short.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/__init__.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/__init__.py

Purpose: package initializer for Workgen runner scripts. It discovers a usable WiredTiger build, sets Python/library paths when necessary, imports `wiredtiger` and `workgen`, and re-exports runner helper APIs.

Important APIs and functions: `_prepend_env_path(pathvar, s)` prepends library directories. Module-level logic computes `thisdir`, `workgen_src`, `wt_dir`, `curdir`, and `wt_builddir`; may re-exec Python with `_workgen_init` set to refresh dynamic library search paths. Exports `txn`, `extensions_config`, `op_append`, `op_group_transaction`, `op_log_like`, `op_multi_table`, `op_populate_with_range`, `sleep`, `timed`, `workload_latency`, and `get_cache_eviction_stats`.

Control flow: prefer `WT_BUILDDIR`; else current directory containing `wt`; else warn. Try importing `wiredtiger`; on failure add source/build Python paths; on continued failure set `LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH` and `os.execv` the interpreter once. Then similarly import `workgen` after adding source/build paths if needed.

State and persistence: mutates `os.environ`, `sys.path`, and potentially replaces the running process. No disk writes except downstream imports.

Dependencies and integration: every runner script imports this package first, allowing direct execution without manual environment setup.

Risks: re-exec can surprise debuggers and wrappers. Path detection can choose the wrong build in multi-build trees. Bare `except` blocks hide import details. If re-exec fails, the user gets guidance but execution exits.

Test signals: successful import of `runner`, `wiredtiger`, and `workgen`; warning messages when build discovery fails.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/core.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/core.py

Purpose: core helper library that lets Workgen Python runner scripts emulate common wtperf features: transactions, timed phases, extension config, multi-table expansion, log-like operations, grouped transactions, and range-partitioned populate.

Important APIs and functions: public helpers include `txn`, `sleep`, `timed`, `extensions_config`, `op_copy`, `op_append`, `op_multi_table`, `op_log_like`, `op_group_transaction`, and `op_populate_with_range`. Internal helpers include `_wiredtiger_builddir`, `_choose_pareto`, `_op_get_group_list`, `_op_copy_mod`, `_op_multi_table_as_list`, `_check_pareto`, `_op_log_op`, `_optype_is_write`, and `_op_transaction_list`.

Control flow: `txn` attaches a `Transaction` object to an operation. `timed` wraps operations in an `OpList` if needed and sets `_timed`. `extensions_config` finds exactly one matching shared library per extension and builds a WT config string. `op_multi_table` deep-copies operations across tables, with special Pareto/range-partition logic. `op_log_like` injects secondary log-table inserts for write-like operations. `op_group_transaction` restructures operation lists into transaction groups. `op_populate_with_range` maps initial inserts across fully and partially filled tables.

State and persistence: mutates Workgen operation objects, including private SWIG-backed fields. It does not write persistent storage directly.

Dependencies and integration: imports `Key`, `Operation`, `OpList`, `Table`, `Transaction`, and `Value` from Workgen. Used by most runner scripts.

Risks: relies on Workgen private attributes like `_group`, `_table`, `_key`, and `_repeatgroup`; SWIG/API changes can break it. `op_group_transaction` compares `ops_arg != Operation.OP_NONE`, which appears suspicious because `ops_arg` is an object, not an optype. Transaction plus Pareto range partition is explicitly unsupported. Random prime selection makes some expanded operation order nondeterministic.

Test signals: behavior is indirectly tested by all runner workloads; failures appear as operation construction exceptions, Workgen run errors, or distribution anomalies.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/core.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/latency.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/latency.py

Purpose: formats Workgen workload latency statistics into human-readable text files or stdout, with optional ASCII plots.

Important APIs and functions: public `workload_latency(workload, outfilename=None, plot=False)`. Private helpers `_show_buckets`, `_latency_buckets`, `_latency_preprocess`, `_latency_plot`, `_latency_op_plot`, and `_latency_optype`.

Control flow: `workload_latency` opens an output file if requested, then processes workload stats for insert, checkpoint, read, remove, update, truncate, RTS, and not-found operations. `_latency_optype` skips empty operation types, prints totals/average/min/max, prints bucket totals, and optionally plots microsecond/millisecond/second histograms. Plotting preprocesses SWIG arrays by merging buckets and scaling into an 80-column by 20-row ASCII chart.

State and persistence: writes to the requested latency file or stdout. It reads `workload.stats` and does not mutate workload state except assigning `arr.height` in preprocessing.

Dependencies and integration: imported by `runner.__init__` and used across benchmark scripts to write `latency.out` or named RTS files.

Risks: output file is opened without explicit close when `outfilename` is used; process exit normally closes it, but long-lived import usage could leak. Assigning `height` to SWIG arrays may depend on permissive wrapper behavior. Bucket summaries print total counts rather than detailed bucket contents unless plot mode is true.

Test signals: existence/non-empty latency files and expected operation sections for nonzero stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/latency.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/wtcache.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/wtcache.py

Purpose: emits a focused snapshot of WiredTiger cache and eviction statistics for Workgen cache workloads.

Important APIs and functions: public `get_cache_eviction_stats(session, cache_eviction_file)`. It reads `wiredtiger.stat.conn` counters for cache bytes, history store bytes, eviction trigger hits, app reads/writes, app eviction attempts/failures, forced eviction, and eviction worker attempts/failures.

Control flow: open append file or use stdout; open a `statistics:` cursor; print a start marker; compute percentages relative to `cache_bytes_max`; print cache occupancy, history store occupancy, trigger counters, app page counters, app eviction counters, forced eviction counters, worker eviction counters; close cursor.

State and persistence: appends to the given stats file, commonly `cache_eviction.stat`, or writes stdout. It does not mutate database state.

Dependencies and integration: imported by `runner.__init__`; used by `cache_workload_update_trigger.py` and likely similar cache workloads.

Risks: divides by `cache_total`, so a zero/unavailable cache max would fail. File handle is not explicitly closed. Imports `json` but does not use it. Some counters depend on WiredTiger stat names and may break across versions.

Test signals: cache stats file with start/end markers and populated counter values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/wtcache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/skiplist_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/skiplist_stress.py

Purpose: stress workload for skiplist-related insertion paths with small cache and debug stress enabled.

Important APIs and functions: uses `debug_mode=(stress_skiplist=1)`, `split_deepen_min_child`, Workgen inserts, thread multiplication, and latency output.

Control flow: open a 100 MB cache connection with logging disabled, fast statistics, JSON stats log, and skiplist debug stress; create `file:test`; set key size 64, value size 10, and range 100 million; run 50 insert threads for 360 seconds.

State and persistence: creates one file table and appends/inserts random-range keys under heavy concurrency. Writes `latency.out`.

Dependencies and integration: tests WiredTiger debug mode behavior and split/skiplist concurrency.

Risks: debug mode option requires a compatible build. Small cache with many threads may trigger stalls or non-representative performance. No populate phase means table growth happens only during run.

Test signals: workload assertion, statistics log, latency file, and absence of split/skiplist failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/skiplist_stress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree.py

Purpose: basic small btree read workload.

Important APIs and functions: uses `Context`, `Session.create`, `Table`, insert/search `Operation`, `Thread`, and `Workload`.

Control flow: open 500 MB cache; create `file:test.wt`; populate 500,000 rows; run 8 search threads for 120 seconds with 5-second reports.

State and persistence: creates one file table in the WT home. No explicit latency or close call.

Dependencies and integration: simple benchmark/smoke workload for read performance over a small table.

Risks: no latency output, so observability is limited to Workgen reports. Table remains in the home until context cleanup.

Test signals: populate and workload assertions plus read throughput report.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree_reopen.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree_reopen.py

Purpose: small btree read workload that forces reopen behavior on each search operation.

Important APIs and functions: same as `small_btree.py`, with direct private assignment `op._config = 'reopen'`.

Control flow: create/populate one table with 500,000 rows; create search operation, set config to `reopen`, run 8 copies for 120 seconds.

State and persistence: persistent table data is repeatedly searched with reopen behavior, likely exercising handle open/close paths.

Dependencies and integration: relies on Workgen interpreting `_config='reopen'`. Used to compare normal read path versus reopen overhead.

Risks: direct mutation of private `_config` is fragile. No latency file. Reopen behavior can be much slower and file-manager sensitive.

Test signals: assertions and workload reports.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_btree_reopen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_update_reopen.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/small_update_reopen.py

Purpose: small update workload using reopen operation config, with raw byte key/value formats.

Important APIs and functions: uses `key_format=u,value_format=u`, insert/update operations, `op._config='reopen'`, and Workgen thread multiplication.

Control flow: open 500 MB cache; create `file:test.wt`; populate 500,000 rows with 200-byte values; run 8 update threads with reopen config for 120 seconds.

State and persistence: updates a persistent table while reopening handles/cursors per operation according to Workgen config.

Dependencies and integration: companion to small btree reopen read benchmark.

Risks: private `_config` mutation, no latency output, and update conflicts/overwrites may vary with key generator behavior.

Test signals: populate/workload assertions and Workgen report output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/small_update_reopen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/split_stress.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/split_stress.py

Purpose: stresses page split paths and split races with small cache, small pages, fast split deepening, and concurrent random-order inserts.

Important APIs and functions: uses `op_multi_table`, insert operations, Workgen thread multiplication, table range settings, and latency output.

Control flow: open a 100 MB cache connection with statistics logging; create three file tables with 8 KB leaf/internal pages, key/value max 1433, memory page max 1 MB, and `split_deepen_min_child=100`; populate 50,000 rows across tables; run 20 insert threads across all tables for 300 seconds.

State and persistence: creates three file tables and grows them through concurrent inserts. Writes `latency.out`.

Dependencies and integration: split stress benchmark for WiredTiger btree concurrency.

Risks: small cache and aggressive split config are intentionally stressful and can expose races. Operation distribution depends on Workgen range/key behavior.

Test signals: populate/workload assertions, latency output, statistics log, and absence of split failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/split_stress.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/workgen_stat.sh -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/workgen_stat.sh

Purpose: shell utility that combines WiredTiger JSON statistics time-series files and Workgen `sample.json` into a sorted output file, optionally opening/running an analyzer.

Important APIs and functions: shell functions `Usage` and `Filter`. `Filter` removes `"version"` fields using `sed`, which helps normalize JSON lines before sorting.

Control flow: parse `-h` home, `-o` output, and `-e` analyzer; verify home directory and `WiredTiger.wt`; choose a temporary output if analyzer is requested without output; run `(cd $wthome; Filter WiredTigerStat.* sample.json) | sort > $outfile`; if analyzer is set, use `open -a` on Darwin or execute analyzer on other systems.

State and persistence: reads stats files from a WT home and writes the combined output file, defaulting to `$wthome/stat_tmp.json` when needed.

Dependencies and integration: POSIX shell, `sed`, `sort`, `uname`, macOS `open` optionally, and analyzer executable. Used after Workgen benchmark runs.

Risks: usage text says at least one of `-t2` or `-o`, but `-t2` is not parsed; likely stale help. Unquoted `$wthome` in `cd $wthome` and `$outfile` redirection can fail for spaces. Glob with no `WiredTigerStat.*` may pass literal depending shell settings.

Test signals: non-empty combined JSON output and analyzer launch/exit status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/workgen_stat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/validate_mirror_tables.py -->
# sources/storage-engines/wiredtiger/bench/workgen/validate_mirror_tables.py

Purpose: validates Workgen mirror table pairs in a WiredTiger home by comparing each base table with its mirror. Returns success only when all discovered mirror pairs match.

Important APIs and functions: `usage_exit`, `get_wiredtiger_db_files(connection)`, `get_mirrors(connection, db_dir, db_files)`, `get_mirror_file(metadata_cursor, filename)`, and `main(sysargs)`. It uses `py_common.wiredtiger_util.wiredtiger_open` and `wt_cmp_uri.wiredtiger_compare_uri`.

Control flow: parse one database directory argument; open WT readonly; enumerate metadata `file:` entries excluding WiredTiger internal files; for each file, inspect metadata for `app_metadata` keys `workgen_dynamic_table=true` and `workgen_table_mirror`; pair base and mirror files if both exist; close connection; compare each URI pair while redirecting comparator stdout to `/dev/null`; report success/failure count and exit accordingly.

State and persistence: readonly database access only. It opens `/dev/null` for suppressed comparator output and prints a summary.

Dependencies and integration: requires WiredTiger tools modules on `PYTHONPATH`. Integrates with Workgen dynamic table mirror testing and snapshot validation workflows.

Risks: `get_mirror_file` catches only `KeyError` by class name and may leave `metadata` undefined for other exceptions. App metadata parsing assumes comma-separated `key=value` entries without embedded commas/equal signs. `stdout` variable receives return value from `wiredtiger_compare_uri`, not captured output, because stdout is redirected. The URI strings include `db_dir/table:name`, matching comparator expectations but worth verifying if comparator API changes.

Test signals: process exit 0 on all mirror matches, exit 1 on usage or mismatches, and printed count of validated pairs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/validate_mirror_tables.py -->
