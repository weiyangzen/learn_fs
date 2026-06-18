# sources/storage-engines/rocksdb/tools/db_bench_tool.cc lines 1-6629

## Scope

This chunk covers the first 6,629 lines of RocksDB's `db_bench` implementation. It includes the command-line flag surface, helper conversions and validators, value/key/statistics utilities, DB/column-family handle ownership wrappers, benchmark orchestration, option construction, DB open paths, `OpenAndCompact`, key generation, the general write path, and most of deterministic-compaction setup. The chunk stops inside `Benchmark::DoDeterministicCompact()`, so read workloads, merge/update workloads, transaction verification, backup/restore, checksum verification, and `main()` are mostly outside this chunk except where they are registered by benchmark dispatch.

## Purpose

- Provide the configuration and execution core for the `db_bench` command-line tool.
- Map a very large `gflags` surface into RocksDB `Options`, `ReadOptions`, `WriteOptions`, table options, cache objects, rate limiters, compaction settings, BlobDB settings, transaction settings, trace settings, and environment/filesystem selection.
- Open the target database in one of several modes: regular DB, read-only DB, multi-DB, multi-column-family DB, `OptimisticTransactionDB`, `TransactionDB`, stacked BlobDB, secondary DB, or follower DB.
- Dispatch comma-separated benchmark names to member functions, handling fresh-DB setup, benchmark-specific parameter rewrites, warmups, repeated runs, optional tracing, block-cache tracing, statistics aggregation, and post-processing hooks.
- Supply shared benchmark infrastructure: random value/key generation, per-thread state, duration-based loop control, progress reporting, histograms, confidence intervals, CSV reporting, background error recovery waits, and DB lifetime protection.
- Exercise persistent RocksDB behaviors such as WAL/sync settings, flush and compaction layout, cache and persistent-cache modes, blob files, user-defined timestamps, range tombstones, secondary catch-up, and remote-compaction-style `OpenAndCompact()`.

## Important APIs, Types, And Functions

- The flag block starts with `FLAGS_benchmarks` and exposes workload names and options for writes, reads, scans, compaction, tracing, backup/restore, verification, compression, cache setup, table format, memtable format, WAL behavior, BlobDB, transactions, secondary/follower DBs, user timestamps, range tombstones, and `OpenAndCompact` cancellation/resumption tests.
- `db_bench_exit()` routes exits through `ToolHooks` when installed, allowing test harnesses or embedding code to intercept process termination.
- `StringToCompressionType()` and `StringToAdmissionPolicy()` translate CLI strings to RocksDB enums and exit on unknown values.
- `CreateMemTableRepFactory()` builds the configured memtable factory from built-in names (`skip_list`, `prefix_hash`, `vector`, `hash_linkedlist`) or object-registry strings.
- `BaseDistribution`, `FixedDistribution`, `UniformDistribution`, `NormalDistribution`, and `RandomGenerator` generate compressible benchmark values with fixed or randomized lengths.
- `DBWithColumnFamilies` owns column-family handles and the DB owner pointer, tracks how many CFs have been created, selects hot CFs by uniform or configured probability distribution, and can create a new hot CF batch during staged writes.
- `ReporterAgent` writes periodic CSV rows of elapsed seconds and interval operations to `FLAGS_report_file` from a background thread.
- `Stats` records per-thread operation counts, bytes, histograms, progress reports, RocksDB property snapshots, thread status, file-operation counters, and final throughput output.
- `CombinedStats` computes average, median, and approximate 95% confidence intervals for repeated benchmark runs.
- `TimestampEmulator` produces 8-byte user timestamps for writes and either latest or random-past timestamps for reads.
- `SharedState`, `ThreadState`, and `Duration` coordinate benchmark workers, per-thread RNGs, global start/done barriers, rate limiters, and fixed-operation vs time-limited workloads.
- `Benchmark` is the central type. It owns caches, DB handles, open options, benchmark counters, generated existing keys, lifecycle locks, error listener, optional timestamp emulator, and optional secondary update thread.
- `Benchmark::Run()` initializes the DB, prints the environment/header, parses the benchmark list and `[Xn-Wn]` repeat/warmup suffixes, maps names to methods, recreates fresh DBs when required, starts traces, invokes `RunBenchmark()`, reports repeated-run statistics, runs post-processing hooks, stops secondary update, ends traces, and prints final statistics.
- `DbUseGuard` and `DbStateMutationGuard` protect DB handle use and mutation. Worker benchmark bodies run under `DbUseGuard`; fresh-DB reopen and destruction paths run under `DbStateMutationGuard`, which also stops the secondary update thread.
- `ThreadBody()` waits on the shared start barrier, enables perf context, runs the selected benchmark method under DB-use protection, records perf-context text when enabled, and signals completion.
- `RunBenchmark()` allocates worker arguments, optional benchmark-level read/write rate limiters, optional `ReporterAgent`, starts `FLAGS_env` threads, waits for all workers, merges `Stats`, reports results, and frees per-thread state.
- `InitializeOptionsFromFlags()` is the main flag-to-`Options` mapper. In this chunk it configures environment and filesystem wrappers, cache/table format, compression manager, WAL and write-thread settings, compaction options, memtable options, blob file options, checksums, protection bytes, statistics, logging, direct IO, rate limiting, FIFO/universal compaction, timestamps, and many other RocksDB options.
- `InitializeOptionsGeneral()` applies only the settings that should still be forced when an OPTIONS file was used, including create flags, statistics, block cache, filter policy, row cache, env, background priority lowering, rate limiter, listener, file checksum factory, opening single or multi DBs, optional no-op compaction filter, and loading `--use_existing_keys`.
- `Open()` chooses options-file loading first and falls back to flag-derived options, then calls `InitializeOptionsGeneral()`.
- `OpenDb()` handles actual DB open variants, including multi-CF descriptors, hot CF counts, CF probability validation, read-only open, optimistic/transaction DB open, stacked BlobDB open, secondary DB open with periodic `TryCatchUpWithPrimary()`, follower open, normal open, and optional open timing.
- `OpenAndCompact()` constructs a `CompactionServiceInput` from current SST metadata and latest OPTIONS file, writes output to a secondary directory, optionally deletes prior output, runs `DB::OpenAndCompact()`, supports cancellation on odd repeated runs, parses `CompactionServiceResult`, and reports output file counts and average size.
- `KeyGenerator` supports sequential, random, and unique-random key ids; unique-random pre-shuffles all ids with `seed_base`.
- `GenerateKeyFromInt()` and `GenerateKeyFromIntForSeek()` encode numeric keys into fixed-width byte keys, optionally adding a generated prefix and optionally forcing a missing seek prefix.
- `DoWrite()` implements `fillseq`, `fillrandom`, `filluniquerandom`, overwrite, stacked BlobDB puts, write batches, user timestamp updates, hot-CF stage creation, multi-DB sequential balancing, range tombstones or expanded point tombstones, disposable/persistent-entry simulation, write rate limiting, sine-rate changes, error-recovery waits, and byte accounting.
- `DoDeterministicCompact()` disables auto compactions, repeatedly writes and flushes to collect L0 sorted runs, then manually compacts files into a deterministic LSM shape for level, universal, or FIFO compaction. The debug-only verification continues past the chunk boundary.

## Control Flow

Startup flow in this chunk begins with parsed flags and `Benchmark` construction. The constructor creates primary and compressed caches, optional simcache, optional counted filesystem wrapper, validates prefix sizing, removes heap-profile leftovers, destroys the DB and WAL directory unless `--use_existing_db` is set, recreates the multi-DB parent directories when needed, registers an error listener, and creates a mock user-timestamp clock when requested.

`Benchmark::Run()` opens the DB through `Open()`, prints environment and option summary, then iterates over comma-separated benchmark names. For each benchmark it resets mutable per-run fields from flags, rebuilds read/write options, parses optional warmup/repeat syntax, chooses a member-function pointer, and marks whether a fresh DB is required. Fresh DB benchmarks take the mutation guard, skip if `--use_existing_db` is true, otherwise close current DB handles, destroy DB directories, clear multi-DB state, and reopen.

When a benchmark method is selected, `Run()` starts optional RocksDB operation tracing and optional block-cache tracing, executes warmup runs, then executes the requested repeat count. Each run uses `RunBenchmark()`, which creates worker state, starts all threads through `Env::StartThread()`, waits for them to initialize, releases the start barrier, waits for completion, merges stats, reports the benchmark line, and returns merged stats for repeated-run aggregation. After the benchmark list finishes, `Run()` stops secondary updates, ends traces, and prints RocksDB statistics and simcache statistics if enabled.

Worker flow is synchronized by `SharedState`: each `ThreadBody()` increments `num_initialized`, waits until `start` becomes true, enables perf context, starts its `Stats`, enters a `DbUseGuard`, executes the selected member function, stops stats, and increments `num_done`. The DB-use guard means DB handles cannot be concurrently destroyed by the mutation guard while workers are using them.

Option flow is split intentionally. `InitializeOptionsFromFlags()` builds the full option set from flags when no OPTIONS file is used. `InitializeOptionsGeneral()` applies the smaller set of dynamic/shared/runtime settings needed in both flag and OPTIONS-file modes, then opens DB handles. This split reduces accidental overwrites of settings loaded from an OPTIONS file while still installing benchmark-owned objects such as statistics, caches, listeners, and rate limiters.

Write workload flow in `DoWrite()` is nested by duration, DB/key-generator selection, batch creation, and entries per batch. It advances staged hot column-family creation when duration stages change, chooses a target DB for multi-DB runs, builds a `WriteBatch` or direct BlobDB writes, optionally schedules disposable-entry deletes, optionally emits overwrite keys from a recent-key window, optionally inserts range tombstones, optionally updates user timestamps, rate-limits by batch bytes, writes the batch, waits for background error recovery once, and records finished operations and bytes.

`OpenAndCompact()` is a meta-benchmark rather than a normal workload. It runs only on thread 0, gathers current SST files from `GetColumnFamilyMetaData()`, finds and parses the latest OPTIONS file number, serializes `CompactionServiceInput`, creates an output directory under `FLAGS_secondary_path`, optionally runs the compaction in a cancellable thread for odd repeated runs, and parses `CompactionServiceResult` when the API succeeds.

## State And Persistence Behavior

Persistent state touched directly by this chunk includes DB directories, WAL directories, backup/restore paths printed for later methods, secondary directories, `OpenAndCompact` output directories, read cache directories, LOG/read-cache logger files, report CSV files, trace files, block-cache trace files, SST files generated by writes/flushes/compactions, blob files, MANIFEST/OPTIONS metadata, and optional file checksums.

The write path can persist data through normal `DB::Write()` batches, stacked BlobDB `Put()` or `PutWithTTL()`, point deletes, `DeleteRange()`, and expanded range-tombstone point deletes. WAL durability is controlled by `WriteOptions.sync`, `disableWAL`, `manual_wal_flush`, WAL compression, WAL directory, fsync/fdatasync choice, WAL TTL/size settings, and WAL tracking flags. Direct IO, mmap, bytes-per-sync, writable-file buffering, and filesystem/env URI settings affect how those files are written.

Column-family state is dynamic. `OpenDb()` initially opens or creates only the hot CF set when `num_hot_column_families` is smaller than `num_column_families`; `DoWrite()` creates later hot CF batches as the workload stage advances. `DBWithColumnFamilies::num_created` is an atomic release/acquire synchronization point for threads selecting CF handles.

Cache state is shared across the benchmark. `NewCache()` can create LRU or HyperClock block caches, attach a compressed secondary cache or registry-created secondary cache, build tiered caches, or use a simcache wrapper. Block-based table options then reference this cache; blob cache can either share it or create a standalone LRU cache. Cache contents and cache statistics survive across benchmark methods until the `Benchmark` object is destroyed or the DB is reopened.

Secondary/follower behavior is persistent-integration sensitive. A secondary DB open can spawn a background thread that periodically calls `TryCatchUpWithPrimary()` against the captured `DBWithColumnFamilies`. Mutation guard construction stops and joins this thread before DB handles are mutated, preventing the secondary updater from using stale DB pointers.

Statistics and traces are external observability state. `Stats` prints throughput and histograms to stdout/stderr; `ReporterAgent` persists interval rows; RocksDB statistics are held in `dbstats`; operation and block-cache traces are started/stopped on the DB and written through file trace writers.

## Dependencies And Integration Points

- This file requires `GFLAGS`; the entire implementation is under `#ifdef GFLAGS`.
- Platform integrations include NUMA binding, POSIX/Windows file APIs, Linux `/proc/cpuinfo`, Apple/FreeBSD sysctl paths, and optional memkind cache allocation.
- Core RocksDB dependencies include `DB`, `Options`, `ColumnFamilyOptions`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `Iterator`, `Cache`, `RateLimiter`, `Statistics`, `Env`, `FileSystem`, `TableFactory`, `MergeOperator`, `CompactionFilter`, `EventListener`, `PerfContext`, `ThreadStatus`, `BackupEngine`, transaction DB APIs, BlobDB APIs, persistent cache APIs, object registry APIs, and compaction service structs.
- Tool-hook integration routes open calls through `ToolHooks`, allowing tests or tools to override `Open`, `OpenForReadOnly`, `OpenTransactionDB`, `OpenOptimisticTransactionDB`, `OpenAsSecondary`, `OpenAsFollower`, BlobDB open, and exit behavior.
- Table and cache integration includes block-based, plain, and cuckoo table factories; Bloom/Ribbon filters; partitioned filters/indexes; trie user-defined index factory; persistent read cache; secondary/tiered/compressed caches; block and blob prepopulation.
- Environment/filesystem integration includes `--env_uri`, `--fs_uri`, simulated hybrid filesystem, simulated HDD behavior, counted filesystem wrapping, direct IO flags, IO priority lowering, CPU priority lowering, and IO dispatcher prefetch limits for later MultiScan paths.
- Benchmark dispatch references many member functions whose bodies continue after this chunk, so later research chunks should connect those methods back to the dispatch and shared state documented here.

## Risks And Edge Cases

- The flag surface is broad and many flags interact. Some invalid combinations are checked locally, but many combinations can produce subtle RocksDB behavior rather than immediate errors.
- `OperationTypeString` maps both `kCompress` and `kUncompress` entries using `kCompress` as the key for the second entry, so the uncompress label is not represented as intended.
- `DBWithColumnFamilies::GetCfh()` assumes probability vectors are non-empty and sum to 100; validation happens at open time, but the selection loop uses `rand_num % 100` and can walk off if future changes bypass validation.
- `CreateNewCf()` relies on external sizing of `cfh` and atomic `num_created`; misuse outside staged hot-CF creation could leave null handles.
- `ReporterAgent` captures `[&]` for its reporting thread and depends on destructor signaling and joining before referenced members go away. The current lifetime is controlled by `RunBenchmark()`, but refactors should avoid detaching or moving it.
- `Stats::Merge()` inserts shared histogram pointers from other `Stats` instances rather than deep-copying when a histogram key is new. This is safe for current post-run reporting before thread states are deleted because the histograms are heap-owned by shared pointers, but it is easy to misread as value ownership.
- `Duration::GetStage()` computes with `max_ops_ - 1`; unusual zero-operation settings can be fragile despite `DoWrite()` guarding with `num_per_key_gen != 0`.
- `DbUseGuard` enforcement is strict only at `SelectDBWithCfh()` and by convention elsewhere. Direct `db_` accesses inside worker methods rely on `ThreadBody()` having installed a guard.
- `ErrorExit()` uses `std::_Exit(1)` from a DB-use or secondary-update context to avoid self-deadlock/self-join. That avoids hangs but skips normal cleanup and may leave temporary DB, WAL, trace, or output files.
- Fresh-DB reopen directly calls `db_.DeleteDBs()` and `multi_dbs_[i].DeleteDBs()` inside the mutation-guard scope rather than the wrapper that asserts guard ownership; comments document this but it is not mechanically enforced.
- `OpenDb()` changes `FLAGS_num_hot_column_families` when the user does not provide a valid smaller hot set, which makes the flag value mutable runtime state.
- The secondary update lambda sets `is_secondary_update_thread_ = true` and never resets it. The thread exits afterward, so this is currently harmless, but thread reuse or future pooling assumptions would be unsafe.
- `OpenAndCompact()` manually deletes only files directly under the output directory before `DeleteDir()`. Nested directories or non-file children would not be removed.
- `OpenAndCompact()` uses `FLAGS_secondary_path` for output staging; if not configured for non-secondary runs, directory semantics may surprise users.
- `KeyGenerator` in unique-random mode allocates one `uint64_t` per key and shuffles all values, which can be very memory-heavy for large `--num`.
- `DoWrite()` direct stacked BlobDB writes happen inside the per-entry loop and skip the later batch write path. Mixed assumptions around `Status s` and batch bytes need care when changing BlobDB behavior.
- `DoWrite()` uses `rand()` for BlobDB TTL, unlike most of the benchmark which uses seeded RocksDB RNGs. That can reduce reproducibility.
- Disposable/persistent entry simulation, overwrite windows, range tombstones, and unique-random mode are deliberately constrained. The code exits on some incompatible combinations but future flags could accidentally bypass those assumptions.
- User timestamp support in this chunk only supports 8-byte timestamps and asserts that assumption in `TimestampEmulator`.
- `DoDeterministicCompact()` mutates DB options to disable auto compactions and records `options_list`, but restoration is outside this chunk or absent in the visible part; later chunks should verify option restoration.

## Test Signals

- CLI/dispatch tests should cover benchmark name parsing, empty names, unknown names, `[Xn-Wn]` repeat/warmup syntax, fresh-DB skip with `--use_existing_db`, and benchmark-specific thread-count rewrites.
- Option tests should run db_bench with both flags and an OPTIONS file, verifying that `InitializeOptionsGeneral()` still installs statistics, caches, listeners, filters, env, row cache, and rate limiters without overwriting unrelated OPTIONS-file settings.
- DB open tests should cover normal, read-only, multi-DB, multi-CF, hot-CF staged creation, configured CF probability distribution, optimistic transaction DB, transaction DB with unordered writes, stacked BlobDB, secondary DB catch-up, and follower DB.
- Lifecycle tests should stress fresh-DB reopen while workers and the secondary update thread are active, validating `DbUseGuard`, `DbStateMutationGuard`, `StopSecondaryUpdateThread()`, and `ErrorExit()` behavior.
- Write workload tests should cover sequential/random/unique-random writes, batch sizes, sync/disable-WAL/manual-WAL options, overwrite probability/window behavior, disposable/persistent deletes, range tombstones vs expanded tombstones, user timestamps, multi-DB sequential balancing, and write-rate limiting.
- Cache/table tests should exercise LRU and HyperClock caches, simcache, compressed secondary cache, tiered cache, registry-created cache/secondary cache, blob cache sharing vs standalone cache, persistent read cache, partitioned filters/indexes, hash search, trie index, block-cache prepopulation, and cache charge options.
- Compaction tests should cover deterministic level/universal/FIFO setup, disabled-auto-compaction precondition, small `--num` failure messages, `CompactFiles()` output-level choices, FIFO size trimming, and debug verification of sorted-run key/seqno metadata.
- `OpenAndCompact` tests should cover missing OPTIONS file, malformed OPTIONS filename, no input files, cleanup/resume behavior, cancellation on odd repeated runs, result parsing, output directory conflicts, and average output-size reporting.
- Observability tests should verify progress reports, histograms by operation type, repeated-run average/median/CI output, CSV interval reports, `rocksdb.stats`/CF stats printing, thread-status snapshots, counted filesystem counters, operation traces, block-cache traces, and final statistics printing.
- Error-path tests should cover unsupported compression/cache/table settings, invalid admission policy, unavailable NUMA/memkind/jemalloc features, invalid CF distribution sums/counts, invalid BlobDB/cache sizes, failed cache/read-cache/logger creation, failed DB opens, failed writes with and without background error recovery, and secondary catch-up failure.
