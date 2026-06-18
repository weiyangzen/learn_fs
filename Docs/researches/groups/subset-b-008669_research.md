# subset-b-008669 RocksDB microbench and monitoring research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/microbench/db_basic_bench.cc -->
# sources/storage-engines/rocksdb/microbench/db_basic_bench.cc

Purpose: Defines a Google Benchmark binary for RocksDB basic DB-path microbenchmarks. It measures DB open/close, Put, manual compaction, manual flush, Get, GetMergeOperands, block seek, iterator seek/next/prev, prefix seek, and RandomAccessFileReader reads under combinations of compaction style, data volume, value size, statistics, WAL, filters, mmap, compression, checksum, and block-cache settings.

Important APIs/types/functions: `KeyGenerator` creates fixed-size encoded random/sequential keys, prefixes, non-existing keys, and min/max range keys. `SetupDB`/`TeardownDB` create a process-scoped test DB, gather approximate size, close, and destroy it. Benchmark entry points include `DBOpen`, `DBClose`, `DBPut`, `ManualCompaction`, `ManualFlush`, `DBGet`, `SimpleGetWithPerfContext`, `DBGetMergeOperandsInMemtable`, `DBGetMergeOperandsInSstFile`, `DataBlockSeek`, iterator benchmarks, `PrefixSeek`, and `RandomAccessFileReaderRead`.

Control flow: Most benchmarks build options from `state.range()` arguments, create/load a static DB on thread 0, run timed Google Benchmark loops, expose counters through `state.counters`, then wait for compaction and tear the DB down. Read benchmarks prepopulate data and compact/flush to stabilize file shape. Perf-context benchmarks enable `kEnableTime`, reset `get_perf_context()` per operation, and aggregate counters per iteration.

State and persistence behavior: The benchmark persists temporary RocksDB instances under `Env::GetTestDirectory()` with names using benchmark labels and `getpid()`, then destroys them. Write-heavy benchmarks may disable WAL, disable auto compaction, tune write buffers, or use snapshots to preserve merge operands. The file-reader benchmark creates temporary files and deletes them at the end.

Dependencies/integration: Integrates public `rocksdb::DB`, options, statistics, filters, merge operators, internal `DBImpl`, block builders/readers, perf context, table factories, and Google Benchmark. It exercises both public APIs and internal APIs such as `BlockBuilder`, `Block`, `DataBlockIter`, and `RandomAccessFileReader`.

Risks/test signals: This is benchmark code rather than correctness-test code. Static `std::unique_ptr<DB>` variables are shared across threaded benchmark instances, relying on Google Benchmark setup timing and thread 0 conventions. `ManualCompaction` uses `if (i + 1 % flush_mod == 0)`, which parses as `i + (1 % flush_mod)` and likely never does the intended periodic flush except final flush. Several loops ignore some intermediate statuses until later, and large argument matrices can be expensive.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/microbench/db_basic_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/microbench/ribbon_bench.cc -->
# sources/storage-engines/rocksdb/microbench/ribbon_bench.cc

Purpose: Provides a focused Google Benchmark binary comparing fixed Bloom-like filter implementations, including Ribbon-related implementations, for build speed, positive query speed, negative query speed, filter size, and false positive percentage.

Important APIs/types/functions: `KeyMaker` generates unique-ish variable-length keys from `(filter_num, val_num)` using a reusable aligned buffer. `CustomArguments` enumerates every fixed filter implementation from `BloomLikeFilterPolicy::GetAllFixedImpls()` with bits-per-key, average key length, and entry-count combinations. `FilterBuild`, `FilterQueryPositive`, and `FilterQueryNegative` are registered benchmarks.

Control flow: Each benchmark constructs a `BloomLikeFilterPolicy`, wraps it in `mock::MockBlockBasedTableTester`, generates entries through `FilterBitsBuilder`, and then either times builder `AddKey`/`Finish` or times reader `MayMatch` calls. Negative queries use a different `filter_num` to avoid intentionally inserted keys and track false positives as a benchmark counter.

State and dependencies: State is in benchmark-local builders, readers, key buffers, and returned filter ownership (`owner`). It depends on internal block-based filter APIs and mock table helpers, not the full DB stack.

Risks/test signals: This is performance-only coverage. `KeyMaker::Get` invalidates previous slices because it reuses one buffer, which is safe for immediate builder/reader calls but unsafe if retained. The negative benchmark increments `i` without modulo; key generation still varies through encoded data but can wrap at `uint32_t`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/microbench/ribbon_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/file_read_sample.h -->
# sources/storage-engines/rocksdb/monitoring/file_read_sample.h

Purpose: Defines lightweight sampling helpers for file-read accounting so RocksDB can estimate read counts without instrumenting every read path at full cost.

Important APIs/types/functions: `kFileReadSampleRate` is 1024. `kFileReadNextSampleRate` is 64 times larger and must remain a power of two. `should_sample_file_read()` uses the thread-local random generator and a fixed hit value; `should_sample_file_read_next()` uses a thread-local counter and bitmask. `sample_file_read_inc()` and `sample_collapsible_entry_file_read_inc()` scale sampled reads into `FileMetaData::stats` atomics.

Control flow: Callers ask whether to sample a read or iterator-next read, with sync-point callbacks able to override the boolean for tests. If sampled, callers increment sampled counters by the base sample rate using relaxed atomics.

State and dependencies: The only local mutable state is the thread-local next-read counter. It depends on `db/version_edit.h` for `FileMetaData`, `util/random.h`, and `test_util/sync_point.h`.

Risks/test signals: Sampling is approximate and intentionally relaxed. `sample_collapsible_entry_file_read_inc()` also adds `kFileReadSampleRate` even though next-read sampling is rarer, so callers must understand the intended estimate semantics. Sync points provide deterministic test hooks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/file_read_sample.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram.cc -->
# sources/storage-engines/rocksdb/monitoring/histogram.cc

Purpose: Implements RocksDB histogram buckets and statistical summaries used by `StatisticsImpl` histograms and other monitoring paths.

Important APIs/types/functions: `HistogramBucketMapper` constructs 109 human-readable bucket upper bounds by repeatedly multiplying by 1.5 and rounding to two significant digits. `HistogramStat` implements `Clear`, `Add`, `Merge`, percentile, average, standard deviation, `Data`, and `ToString`. `HistogramImpl` wraps `HistogramStat` behind the abstract `Histogram` interface and a mutex for clear/merge.

Control flow: `Add` locates a bucket, updates bucket count, min, max, count, sum, and sum-of-squares using relaxed atomics. `Merge` compares min/max with CAS loops and fetch-adds aggregate fields. Percentiles scan cumulative bucket counts, linearly interpolate inside the selected bucket, and clamp to current min/max.

State and dependencies: State is atomic counters in `HistogramStat`; `HistogramImpl` adds a mutex for operations that need multi-field coordination. It depends on `port/port.h`, `util/cast_util.h`, `<cmath>`, and `rocksdb/statistics.h`.

Risks/test signals: `Add` intentionally uses load/store increments instead of `fetch_add`, so racing increments can be lost; tests explicitly tolerate this for standard deviation but guard against negative/NaN variance. Min/max updates are relaxed and approximate under races. The fixed bucket array size in the header must match the mapper bucket count.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram.h -->
# sources/storage-engines/rocksdb/monitoring/histogram.h

Purpose: Declares the histogram abstraction and concrete statistical storage used by RocksDB monitoring and statistics reporting.

Important APIs/types/functions: `HistogramBucketMapper` maps values to bucket indexes and exposes limits/counts. `HistogramStat` stores min, max, count, sum, sum squares, and a fixed atomic bucket array. `Histogram` is the abstract interface for clearing, adding, merging, querying percentiles, formatting, and exporting `HistogramData`. `HistogramImpl` is the standard implementation with `TEST_GetStats()`.

Control flow/integration: The header separates lock-free hot-path `HistogramStat::Add` from higher-level `HistogramImpl` API calls. `StatisticsImpl` embeds one `HistogramImpl` per histogram type per core, merges them for reads, and calls `Data`/`ToString`.

State and persistence behavior: Histograms are in-memory only. No persistence is performed here, but exported `HistogramData` and `ToString` can be consumed by stats dumps and persistent stats logic elsewhere.

Dependencies: Uses `<atomic>` transitively through atomics, `<mutex>`, `<vector>`, `<string>`, and `rocksdb/statistics.h`.

Risks/test signals: The comments and fixed `buckets_[109]` are a maintenance contract with `HistogramBucketMapper`. Copy/assignment are deleted to avoid unsafe duplication of atomic state. Tests in `histogram_test.cc` cover basic distribution math, empty/clear behavior, merge, boundary values, and race-tolerant standard deviation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram_test.cc -->
# sources/storage-engines/rocksdb/monitoring/histogram_test.cc

Purpose: Unit tests for `HistogramImpl` and `HistogramWindowingImpl` statistics behavior, including percentile math, merging, clearing, expiration, and standard deviation edge cases.

Important APIs/types/functions: `PopulateHistogram` inserts ranges into a histogram while advancing a `MockSystemClock`. Helper assertions `BasicOperation`, `MergeHistogram`, `EmptyHistogram`, and `ClearHistogram` are reused against both plain and windowed histograms. Tests include `HistogramWindowingExpire`, `HistogramWindowingMerge`, `LargeStandardDeviation`, and `LostUpdateStandardDeviation`.

Control flow: Tests populate deterministic distributions, call `Data`, and assert median, p95, p99, average, min/max, and counts with small tolerances. Windowing tests configure three one-second windows, inject a mock clock, and verify old windows are dropped as time advances.

State/dependencies: Uses `MockSystemClock`, RocksDB test harness, and `Random` to simulate microsecond passage. The global mock clock is injected into windowed histograms through `TEST_UpdateClock`.

Risks/test signals: The suite documents tolerated lock-free races: `LostUpdateStandardDeviation` manually corrupts sum-of-squares to ensure standard deviation never goes negative or NaN. It does not stress multi-threaded races directly, but it covers the expected mathematical outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram_windowing.cc -->
# sources/storage-engines/rocksdb/monitoring/histogram_windowing.cc

Purpose: Implements a time-windowed histogram that keeps aggregate statistics for the most recent N windows and expires older buckets lazily from the Add hot path.

Important APIs/types/functions: Constructors allocate `window_stats_` and set default or configured window counts/durations. `Add` calls `TimerTick`, updates aggregate `stats_`, and updates the current window. `Merge` combines compatible windowed histograms. `SwapHistoryBucket` expires the next circular bucket and advances `current_window_`.

Control flow: `TimerTick` compares `clock_->NowMicros()` with `last_swap_time_` and requires the current window to have at least `min_num_per_window_` samples. `SwapHistoryBucket` uses `try_lock` so only one racing writer rotates windows. It subtracts dropped bucket counts and aggregate sums, recomputes min/max if the dropped bucket owned them, clears the expired bucket, and stores the next index.

State and dependencies: Maintains an aggregate `HistogramStat`, a circular array of `HistogramStat`, clock pointer, mutex, and relaxed atomic current-window/last-swap state. It depends on `SystemClock`, base histogram code, and cast utilities.

Risks/test signals: Add can land samples in the older bucket during rotation, explicitly tolerated by comments. Merge first merges total stats even if window configuration is incompatible, then returns before aligning window buckets, so callers can observe aggregate merge without window compatibility. Tests cover expiration and merge behavior under mock time.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram_windowing.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram_windowing.h -->
# sources/storage-engines/rocksdb/monitoring/histogram_windowing.h

Purpose: Declares `HistogramWindowingImpl`, a `Histogram` implementation that reports only a sliding time-window of samples.

Important APIs/types/functions: The class implements the full `Histogram` interface, exposes constructors for default and custom `(num_windows, micros_per_window, min_num_per_window)`, and provides debug-only `TEST_UpdateClock` for deterministic time tests.

Control flow/integration: Public read APIs proxy to the aggregate `stats_`. Writes go through `Add`, which may rotate windows. `Merge` supports combining another `HistogramWindowingImpl`. It is intended as a drop-in histogram where recent-window behavior is preferable to all-time aggregation.

State and persistence behavior: State is in-memory: a shared `SystemClock`, mutex, aggregate `HistogramStat`, circular `window_stats_`, atomic `current_window_`, and atomic `last_swap_time_`. No data is persisted directly.

Dependencies: Depends on `monitoring/histogram.h` and forward-declares `SystemClock`.

Risks/test signals: The class deletes copy/assignment because it owns mutable atomic/statistical arrays. Configuration comments contain a typo (`configuable`) but the contract is clear. `histogram_test.cc` validates expiration, merge, clear, empty, and standard operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/histogram_windowing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.cc -->
# sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.cc

Purpose: Implements an iterator over DB statistics snapshots retained in `DBImpl` memory.

Important APIs/types/functions: `InMemoryStatsHistoryIterator::~InMemoryStatsHistoryIterator`, `Valid`, `status`, `Next`, `GetStatsTime`, `GetStatsMap`, and private `AdvanceIteratorByTime`.

Control flow: Construction calls `AdvanceIteratorByTime(start_time_, end_time_)`. `Next` calls `AdvanceIteratorByTime(GetStatsTime() + 1, end_time_)` to avoid returning the same timestamp repeatedly. `AdvanceIteratorByTime` delegates to `DBImpl::FindStatsByTime`, which fills the next timestamp and copied stats map; a null DB pointer invalidates the iterator.

State and persistence behavior: The iterator stores a copy of the current stats map, making the current result stable even if DBImpl garbage-collects old in-memory snapshots. It does not persist data; it reflects the in-memory history buffer only.

Dependencies/integration: Depends on `db/db_impl/db_impl.h` and the public `StatsHistoryIterator` interface. Created by DB stats-history APIs when persistent stats are not used.

Risks/test signals: Long gaps between `Next` calls may skip purged snapshots, as documented in the header. `stats_history_test.cc` covers in-memory retrieval and buffer-size purging behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.h -->
# sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.h

Purpose: Declares `InMemoryStatsHistoryIterator`, the `StatsHistoryIterator` implementation for DBImpl's in-memory stats-history map.

Important APIs/types/functions: Constructor accepts `[start_time, end_time)` and `DBImpl*`, then positions the iterator. Public API implements `Valid`, `status`, `Next`, `GetStatsTime`, and `GetStatsMap`. Copy and move operations are deleted.

Control flow/integration: The iterator advances by timestamp range and copies the pointed snapshot into `stats_map_`. This copy is the key integration contract with `DBImpl::stats_history_` garbage collection: the current snapshot survives after the DB's backing map has purged it.

State and persistence behavior: Fields track current `time_`, requested time bounds, copied `stats_map_`, `status_`, `valid_`, and raw `DBImpl*`. It has no ownership of the DB and no disk persistence.

Dependencies: Depends on `rocksdb/stats_history.h` and forward knowledge of `DBImpl`.

Risks/test signals: The raw DB pointer must outlive the iterator. Comments note possible fragmented segments when callers wait too long between `Next()` calls and GC interleaves. DB tests validate snapshot access and purging.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/instrumented_mutex.cc -->
# sources/storage-engines/rocksdb/monitoring/instrumented_mutex.cc

Purpose: Implements mutex and condition-variable wrappers that record perf-context and statistics timing for DB mutex waits and condition waits.

Important APIs/types/functions: `stats_for_report` enables statistics reporting only when a clock and statistics object exist and the stats level includes mutex timing. `InstrumentedMutex::Lock` wraps `LockInternal` with `PERF_CONDITIONAL_TIMER_FOR_MUTEX_GUARD`. `InstrumentedCondVar::Wait` and `TimedWait` do the same for condition waits.

Control flow: Lock/wait methods create a scoped `PerfStepTimer`, optionally start it when the stats code is `DB_MUTEX_WAIT_MICROS`, call internal wait/lock functions, and stop on scope exit. Debug builds call `ThreadStatusUtil::TEST_StateDelay` before blocking. `TimedWaitInternal` exposes a sync-point callback to alter absolute wait time for tests.

State/dependencies: Uses the wrapped `port::Mutex`/`port::CondVar`, optional `Statistics`, optional `SystemClock`, and stats code. Depends on perf-context macros, thread-status debug hooks, `SystemClock`, and sync points.

Risks/test signals: Instrumentation is gated by compile-time perf flags and runtime stats level. `COERCE_CONTEXT_SWITCH` can deliberately yield/sleep around DB mutex waits for stress. Timing overhead is minimized but still present when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/instrumented_mutex.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/instrumented_mutex.h -->
# sources/storage-engines/rocksdb/monitoring/instrumented_mutex.h

Purpose: Declares instrumented wrappers around RocksDB port mutexes and condition variables, plus RAII lock/unlock helpers.

Important APIs/types/functions: `InstrumentedMutex` wraps `Lock`, `Unlock`, and `AssertHeld` while retaining optional statistics/clock/ticker metadata. `CacheAlignedInstrumentedMutex` enforces cache-line alignment. `InstrumentedMutexLock` locks/unlocks by RAII. `InstrumentedMutexUnlock` temporarily releases and reacquires. `InstrumentedCondVar` exposes `Wait`, `TimedWait`, `Signal`, and `SignalAll`.

Control flow/integration: DB internals can use these wrappers in place of `port::Mutex` to get monitoring data through `StatisticsImpl` and perf context without changing lock call sites much.

State and dependencies: State is the underlying mutex/condvar plus monitoring pointers and stats code. The condition variable shares the mutex's monitoring metadata. Depends on `monitoring/statistics_impl.h`, `rocksdb/system_clock.h`, `rocksdb/thread_status.h`, and `util/stop_watch.h`.

Risks/test signals: Statistics pointers are non-owning and must outlive the instrumented object. RAII helpers are non-copyable. The cache-aligned class has a static assertion guarding alignment-size consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/instrumented_mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/iostats_context.cc -->
# sources/storage-engines/rocksdb/monitoring/iostats_context.cc

Purpose: Implements thread-local IO statistics context access, reset behavior, and string formatting.

Important APIs/types/functions: Defines `thread_local IOStatsContext iostats_context` unless `NIOSTATS_CONTEXT` is set, `get_iostats_context()`, `IOStatsContext::Reset`, and `IOStatsContext::ToString`.

Control flow: `Reset` zeroes byte counters, IO timing counters, CPU timing counters, resets temperature-specific file IO stats, and sets `thread_pool_id` to `Env::Priority::TOTAL`. `ToString` uses a macro to emit all counters or only non-zero counters, then trims trailing comma/space.

State and persistence behavior: IO stats are thread-local and in-memory. With `NIOSTATS_CONTEXT`, a dummy static context exists only to keep API shape simple; reset/string operations become no-ops or empty output.

Dependencies/integration: Depends on `monitoring/iostats_context_imp.h`, `rocksdb/env.h`, and public `rocksdb/iostats_context.h`. Instrumented Env/file code updates these counters through macros in the imp header.

Risks/test signals: Counters are not thread-safe by design because each thread has its own context. Formatting relies on trimming `find_last_not_of(", ")`; tests cover zero-included and zero-excluded strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/iostats_context.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/iostats_context_imp.h -->
# sources/storage-engines/rocksdb/monitoring/iostats_context_imp.h

Purpose: Provides internal macros for cheap updates to the thread-local `IOStatsContext`.

Important APIs/types/functions: Declares `extern thread_local IOStatsContext iostats_context` and defines macros `IOSTATS_ADD`, `IOSTATS_RESET`, `IOSTATS_RESET_ALL`, `IOSTATS_SET_THREAD_POOL_ID`, `IOSTATS_THREAD_POOL_ID`, `IOSTATS`, timer guard macros, and `IOSTATS_SET_DISABLE`. In `NIOSTATS_CONTEXT` builds the macros compile away.

Control flow: Update macros directly mutate context fields when `disable_iostats` is false. Timer macros construct `PerfStepTimer` instances on stack, start them, and accumulate elapsed wall or CPU time into IO stats fields.

State/dependencies: The state is the external thread-local context. It depends on `monitoring/perf_step_timer.h` and `rocksdb/iostats_context.h`.

Risks/test signals: Macro expansion assumes a valid field name and can evaluate provided values directly. `IOSTATS_ADD_IF_POSITIVE` is defined only in the disabled branch here, so call sites should not rely on it unless defined elsewhere. `iostats_context_test.cc` validates visible formatting after updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/iostats_context_imp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/iostats_context_test.cc -->
# sources/storage-engines/rocksdb/monitoring/iostats_context_test.cc

Purpose: Unit test for `IOStatsContext::ToString` zero filtering behavior.

Important APIs/types/functions: Test `IOStatsContextTest.ToString` calls `get_iostats_context()->Reset()`, sets `bytes_read`, then compares formatted strings with and without `exclude_zero_counters`.

Control flow: The test asserts the default string contains both zero-valued counters and the non-zero `12345` value. It then asserts the zero-excluding string omits `"= 0"` while still containing the non-zero value.

State/dependencies: Uses the thread-local IO stats context and RocksDB test harness. The main function installs stack traces and runs Google Test.

Risks/test signals: Coverage is narrow: it does not validate every counter, timer macro, disabled build, or temperature sub-counters. It gives a direct regression signal for formatting and zero filtering.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/iostats_context_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_context.cc -->
# sources/storage-engines/rocksdb/monitoring/perf_context.cc

Purpose: Implements RocksDB's per-thread performance context storage, reset/copy/string formatting, and optional per-level read metrics.

Important APIs/types/functions: Large macros `DEF_PERF_CONTEXT_METRICS` and `DEF_PERF_CONTEXT_LEVEL_METRICS` enumerate all fields that must match public `PerfContextBase` and `PerfContextByLevelBase`. `get_perf_context()` returns the thread-local/global context and performs static layout/offset validation. `PerfContext::Reset`, `copyMetrics`, `ToString`, `EnablePerLevelPerfContext`, `DisablePerLevelPerfContext`, and `ClearPerLevelPerfContext` manage metrics.

Control flow: On access, compile-time static assertions ensure internal macro-generated structs have the same size and offsets as public headers. Reset zeros all declared metrics and optionally per-level maps. ToString emits counters, optionally skipping zeros, and appends per-level values as `value@levelN`.

State and dependencies: Normally `thread_local PerfContext perf_context` holds per-thread counters; `NPERF_CONTEXT` builds use a dummy global. Per-level data is heap-allocated as `std::map<uint32_t, PerfContextByLevel>`. Depends on `monitoring/perf_context_imp.h`.

Risks/test signals: Adding a public perf metric requires updating the macros or static assertions fail. Copying can allocate a per-level map; destructor clears it outside Solaris/non-disabled builds. Formatting trims trailing separators. Benchmarks in `db_basic_bench.cc` exercise selected counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_context.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_context_imp.h -->
# sources/storage-engines/rocksdb/monitoring/perf_context_imp.h

Purpose: Internal header defining perf-context globals and instrumentation macros used throughout RocksDB hot paths.

Important APIs/types/functions: Declares the current `PerfContext` object, with Solaris indirection and `NPERF_CONTEXT` disabled mode. Macros include timer start/stop/guard variants, CPU timer guards, conditional mutex timer guards, wait timer guards, measurement, and counter increment macros including per-level increments.

Control flow: In enabled builds, timer macros create `PerfStepTimer` stack objects and start them immediately or conditionally. Counter macros check `perf_level >= kEnableCount` before mutating fields. Per-level increments lazily create a `PerfContextByLevel` entry for the supplied level when per-level tracking is enabled.

State/dependencies: Mutates thread-local `perf_context` and reads thread-local `perf_level`. Depends on `perf_step_timer.h`, public `rocksdb/perf_context.h`, and stop-watch utilities.

Risks/test signals: Macro-based instrumentation has scope/name constraints and assumes the metric field exists. Disabled builds compile macros to no-ops, so code must not depend on side effects inside macro arguments except for the explicit clock cast in CPU guards.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_context_imp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_level.cc -->
# sources/storage-engines/rocksdb/monitoring/perf_level.cc

Purpose: Implements the thread-local perf instrumentation level API.

Important APIs/types/functions: Defines `thread_local PerfLevel perf_level = kEnableCount`, `SetPerfLevel(PerfLevel level)`, and `GetPerfLevel()`.

Control flow: `SetPerfLevel` asserts the supplied enum is between `kUninitialized` and `kOutOfBounds`, then stores it in thread-local state. Instrumentation macros and `PerfStepTimer` consult this level to decide whether to record counts, wall time, wait time, mutex time, or CPU time.

State and dependencies: State is per-thread and not persisted. Depends on `monitoring/perf_level_imp.h` and `<cassert>`.

Risks/test signals: Invalid levels are debug-asserted rather than returned as errors. Because the default is `kEnableCount`, timing metrics require callers to explicitly raise the level. Benchmarks do this before collecting detailed perf counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_level.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_level_imp.h -->
# sources/storage-engines/rocksdb/monitoring/perf_level_imp.h

Purpose: Declares the internal thread-local `perf_level` variable used by perf-context macros.

Important APIs/types/functions: `extern thread_local PerfLevel perf_level`.

Control flow/integration: Included by `perf_step_timer.h`, `perf_context_imp.h`, and `perf_level.cc`; consumers compare the current value with required enable levels before recording measurements.

State and dependencies: No implementation state in this header beyond the external declaration. Depends on `port/port.h` and public `rocksdb/perf_level.h`.

Risks/test signals: It is a narrow glue header; correctness depends on exactly one definition in `perf_level.cc` and consistent thread-local support on the target platform.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_level_imp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_step_timer.h -->
# sources/storage-engines/rocksdb/monitoring/perf_step_timer.h

Purpose: Provides the scoped timer primitive used by perf-context and IO-stats macros to accumulate elapsed wall or CPU time and optionally report tickers to `Statistics`.

Important APIs/types/functions: `PerfStepTimer` constructor captures metric pointer, optional clock, CPU-time flag, required `PerfLevel`, optional statistics object, and ticker type. Public methods are `Start`, `Measure`, and `Stop`; destructor calls `Stop`.

Control flow: The constructor precomputes whether perf counters are enabled and only resolves a clock when either perf or statistics reporting is needed. `Start` stores current time. `Measure` adds elapsed duration to the metric and resets the start time. `Stop` adds elapsed duration to the metric when enabled and calls `RecordTick` on optional statistics.

State and dependencies: Stores booleans, ticker type, clock pointer, start timestamp, metric pointer, and statistics pointer. Depends on `perf_level_imp.h`, `statistics_impl.h`, and `rocksdb/system_clock.h`.

Risks/test signals: `metric_` must remain valid for the timer lifetime. Statistics reporting can run even when perf-level recording is disabled. Destructor-based stop makes the macro guards exception-safe in C++ terms, but double-stop is avoided only through `start_ = 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/perf_step_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/persistent_stats_history.cc -->
# sources/storage-engines/rocksdb/monitoring/persistent_stats_history.cc

Purpose: Implements persistent stats-history key/version helpers and an iterator over the persistent stats column family.

Important APIs/types/functions: Defines version-key strings and current/compatible versions. `DecodePersistentStatsVersionNumber` reads version metadata from the persistent stats CF. `EncodePersistentStatsKey` formats keys as zero-padded seconds timestamp plus `#` plus stats key. `OptimizeForPersistentStats` tunes CF options. `PersistentStatsHistoryIterator` implements `Valid`, `status`, `Next`, `GetStatsTime`, `GetStatsMap`, and `AdvanceIteratorByTime`. Local `parseKey` decodes persisted keys.

Control flow: The iterator seeks the persistent stats CF to the starting timestamp string, parses the first timestamp at or after the requested start, invalidates if beyond end time, then scans all entries with the same timestamp into a map while skipping format-version keys.

State and persistence behavior: Persistent history lives in a RocksDB column family. Iterator state stores current timestamp, bounds, stats map, status, valid flag, and raw `DBImpl*`. Key format sorts by time because timestamps are fixed width.

Dependencies/integration: Depends on `DBImpl`, persistent stats CF accessors, `ReadOptions`, iterators, and `ParseUint64`.

Risks/test signals: `EncodePersistentStatsKey` casts timestamps to `int` for `%010d`, limiting useful range despite `uint64_t` API. `parseKey` returns max timestamp for malformed/too-old keys; iterator logic can then invalidate. Tests cover disk retrieval, reopen recovery, values, read-only, and CF interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/persistent_stats_history.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/persistent_stats_history.h -->
# sources/storage-engines/rocksdb/monitoring/persistent_stats_history.h

Purpose: Declares persistent stats-history metadata helpers and the `StatsHistoryIterator` implementation for the persistent stats column family.

Important APIs/types/functions: Extern strings/version constants name format and compatibility keys. `StatsVersionKeyType` selects version key type. Declares `DecodePersistentStatsVersionNumber`, `EncodePersistentStatsKey`, `OptimizeForPersistentStats`, and `PersistentStatsHistoryIterator`.

Control flow/integration: DB open/persist paths use the helpers to configure and validate the persistent stats CF. DB stats-history APIs can return `PersistentStatsHistoryIterator` to scan time-bounded persisted snapshots.

State and persistence behavior: The iterator stores current time, requested bounds, copied stats map, status, valid flag, and non-owning `DBImpl*`. Actual stats are persisted as key/value pairs in a dedicated column family.

Dependencies: Includes `db/db_impl/db_impl.h` and `rocksdb/stats_history.h`.

Risks/test signals: Copy/move are deleted to prevent accidental duplication of iterator state and raw DB pointer. Header comments contain a typo (`persitent`) but document the version-read contract. `stats_history_test.cc` provides integration coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/persistent_stats_history.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/statistics.cc -->
# sources/storage-engines/rocksdb/monitoring/statistics.cc

Purpose: Implements RocksDB statistics names, construction/registration, option integration, and `StatisticsImpl` aggregation behavior.

Important APIs/types/functions: Defines `TickersNameMap` and `HistogramsNameMap` mapping public enum order to string names. `CreateDBStatistics` constructs `StatisticsImpl`. `Statistics::CreateFromString` registers and loads built-in or custom stats. `StatisticsImpl` implements ticker reads/sets/resets, histogram reads, tick/histogram recording, full reset, `ToString`, `getTickerMap`, and `HistEnabledForType`.

Control flow: Hot-path updates record into `per_core_stats_.Access()` with relaxed atomics and optional forwarding to wrapped `stats_`. Aggregate operations lock `aggregate_lock_`, iterate all core-local slots, and merge ticker/histogram values. `setTickerCount` assigns the requested count to core 0 and zeroes other cores. `Reset` clears all tickers and histograms.

State and dependencies: Maintains optional inner `Statistics`, an aggregate mutex, and cache-line-aligned `CoreLocalArray<StatisticsData>` containing ticker atomics and histogram arrays. It depends on custom object loading/options, convenience APIs, histogram implementation, and string utilities.

Risks/test signals: The name maps must stay in enum order; tests assert this. Aggregation can be expensive because it scans all core-local slots and merges histograms. Stats-level gates skip tickers or histograms based on configured `StatsLevel`. ToString uses fixed temp buffers and asserts on truncation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/statistics.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/statistics_impl.h -->
# sources/storage-engines/rocksdb/monitoring/statistics_impl.h

Purpose: Declares `StatisticsImpl`, the built-in RocksDB implementation of the public `Statistics` interface, along with helper functions for recording stats.

Important APIs/types/functions: Internal enum sentinels extend public ticker/histogram maxima. `StatisticsImpl` overrides ticker, histogram, reset, map, string, and option-related APIs. Nested `StatisticsData` stores cache-line-aligned per-core tickers and histograms with custom aligned allocation. Inline helpers `RecordInHistogram`, `RecordTimeToHistogram`, `RecordTick`, and `SetTickerCount` null-check before dispatch.

Control flow/integration: Writers use per-core storage for low contention; readers and reset operations use `aggregate_lock_`. The class can wrap an inner `Statistics` object for forwarding and is registered as `"BasicStatistics"`.

State and dependencies: Depends on `HistogramImpl`, `CoreLocalArray`, RocksDB statistics APIs, port alignment, likely macros, and mutex utilities.

Risks/test signals: The `StatisticsData` size/alignment static assertion is disabled under `TEST_CACHE_LINE_SIZE`. If public enum maxima change, arrays and map tests catch mismatches. Optional inner stats can duplicate work and must tolerate forwarding.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/statistics_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/statistics_test.cc -->
# sources/storage-engines/rocksdb/monitoring/statistics_test.cc

Purpose: Unit tests for statistics enum/name-map consistency and configurable statistics objects with empty names.

Important APIs/types/functions: `SanityTickers` asserts `TickersNameMap` length and enum order. `SanityHistograms` does the same for `HistogramsNameMap`. `NoNameStats` defines a minimal `DefaultNameStatistics` with `Name() == ""` and an `inner` customizable shared pointer option.

Control flow: Map sanity tests iterate enum values and compare the stored enum in each pair. The no-name test verifies `ToString(ConfigOptions)` for a nameless stats object omits options even before and after configuring `inner=`.

State/dependencies: Uses RocksDB test harness, options type info, convenience/customizable infrastructure, and stack trace setup in main.

Risks/test signals: The suite is a strong guard against enum/name-map drift but does not test hot-path per-core aggregation. The no-name test covers a configuration edge case for wrapped stats objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/statistics_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/stats_history_test.cc -->
# sources/storage-engines/rocksdb/monitoring/stats_history_test.cc

Purpose: Integration tests for stats dump scheduling, stats persist scheduling, in-memory stats history, persistent stats history, persistent stats CF behavior, read-only reopen, and stats-CF flush ordering.

Important APIs/types/functions: `StatsHistoryTest` extends `DBTestBase`, installs a `MockSystemClock`, wraps the Env with `CompositeEnvWrapper`, and overrides periodic-task scheduler timers through a sync point. Tests include `RunStatsDumpPeriodSec`, `StatsPersistScheduling`, `PersistentStatsFreshInstall`, `GetStatsHistoryInMemory`, `InMemoryStatsHistoryPurging`, `GetStatsHistoryFromDisk`, `PersitentStatsVerifyValue`, `PersistentStatsCreateColumnFamilies`, `PersistentStatsReadOnly`, and `ForceManualFlushStatsCF`.

Control flow: Tests reopen DBs with stats options, advance mock time through `TEST_WaitForPeriodicTaskRun`, inspect callbacks/counters, call `GetStatsHistory`, iterate maps, and check persistent stats CF contents using iterators. Several tests create extra column families and verify stats survive reopen.

State and persistence behavior: Exercises both `DBImpl::stats_history_` memory snapshots and the persistent stats column family. Disk tests verify monotonic key growth, preserved non-zero counters after reopen, reserved CF name behavior, and read-only compatibility.

Dependencies/integration: Uses DB internals, column-family handles, periodic scheduler, sync points, cache/rate-limiter includes, persistent stats helpers, mock time, and test utilities.

Risks/test signals: Tests are time-sensitive but controlled by mock clock and scheduler wait hooks. `PersitentStatsVerifyValue` has a misspelled test name. Coverage is broad and gives the strongest integration signal for stats-history behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/stats_history_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_impl.cc -->
# sources/storage-engines/rocksdb/monitoring/thread_status_impl.cc

Purpose: Implements public `ThreadStatus` formatting and operation-property interpretation helpers, with disabled stubs under `NROCKSDB_THREAD_STATUS`.

Important APIs/types/functions: Defines `ThreadStatus::kEnabled`, `GetThreadTypeName`, `GetOperationName`, `GetOperationStageName`, `GetStateName`, `MicrosToString`, `GetOperationPropertyName`, and `InterpretOperationProperties`.

Control flow: Name helpers range-check enum values and return entries from global operation/stage/state tables or unknown names. `MicrosToString` returns empty for zero and otherwise delegates to `AppendHumanMicros`. `InterpretOperationProperties` emits maps for compaction and flush properties, splitting compaction input/output level and flag bitfields into named values.

State and dependencies: No mutable state here; it reads global metadata from `util/thread_operation.h`. Depends on `rocksdb/env.h`, `rocksdb/thread_status.h`, and string utilities.

Risks/test signals: Disabled builds return empty strings/maps and `kEnabled=false`, so callers must tolerate missing status names. Property interpretation is operation-specific; unknown operations intentionally produce no properties.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_updater.cc -->
# sources/storage-engines/rocksdb/monitoring/thread_status_updater.cc

Purpose: Implements the low-level thread-local status tracker used to collect active thread information for `GetThreadList`.

Important APIs/types/functions: `RegisterThread`, `UnregisterThread`, `ResetThreadStatus`, `SetEnableTracking`, `SetColumnFamilyInfoKey`, operation/state setters, operation property setters, `SetOperationStartTime`, `GetThreadList`, `GetLocalThreadStatus`, `NewColumnFamilyInfo`, `EraseColumnFamilyInfo`, and `EraseDatabaseInfo`.

Control flow: Register lazily allocates thread-local `ThreadStatusData`, initializes type/id, and inserts it into the global active set under `thread_list_mutex_`. Setters mutate thread-local atomics only when tracking is enabled. `GetThreadList` locks the global maps, loads high-level fields first, then lower-level operation/state fields only if higher-level CF and operation information are valid, preserving consistency under lock-free updates.

State and dependencies: State includes thread-local `ThreadStatusData*`, global active thread set, CF info map, DB-to-CF key map, and a mutex. Disabled builds provide no-op setters and `GetThreadList` returns `NotSupported`.

Risks/test signals: Thread registration owns a raw heap allocation that must be released by `UnregisterThread`. Operation property indexes are not range-checked here. Comments define the high-to-low consistency contract. Debug verification exists in `thread_status_updater_debug.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_updater.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_updater.h -->
# sources/storage-engines/rocksdb/monitoring/thread_status_updater.h

Purpose: Declares the internal structures and updater class that hold per-thread RocksDB status and global column-family metadata.

Important APIs/types/functions: `ConstantColumnFamilyInfo` stores DB key/name and CF name. `ThreadStatusData` stores atomics for enable flag, thread id/type, CF key, operation type, operation start time/stage/properties, and state. `ThreadStatusUpdater` exposes registration, status setters, `GetThreadList`, CF metadata map updates, and debug verification.

Control flow/integration: Most DB code should call `ThreadStatusUtil` rather than this class directly. The header documents the consistency rule: resets clear low-level fields first, sets update high-level fields first, and readers fetch high-to-low so partial results remain coherent.

State and dependencies: In enabled builds, `thread_status_data_` is thread-local; global maps and active data set are protected by `thread_list_mutex_`. Depends on `rocksdb/thread_status.h`, `rocksdb/status.h`, and `util/thread_operation.h`.

Risks/test signals: Raw pointers are used as DB/CF identity keys, so lifecycle map erasure is important. `enable_tracking` gates most updates. Disabled builds remove all real fields and behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_updater.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_updater_debug.cc -->
# sources/storage-engines/rocksdb/monitoring/thread_status_updater_debug.cc

Purpose: Provides debug-only validation for the `ThreadStatusUpdater` column-family info map.

Important APIs/types/functions: `ThreadStatusUpdater::TEST_VerifyColumnFamilyInfoMap` checks whether supplied `ColumnFamilyHandle*` entries exist or do not exist in `cf_info_map_` and match CF names.

Control flow: In debug and thread-status-enabled builds, the function locks `thread_list_mutex_`, optionally asserts map size equals handle count, converts handles to `ColumnFamilyHandleImpl`, reads each `ColumnFamilyData`, and asserts map presence/name expectations. Disabled thread-status builds provide an empty body.

State/dependencies: Reads `cf_info_map_` under the updater mutex. Depends on `db/column_family.h`, `util/cast_util.h`, and updater declarations.

Risks/test signals: This is assertion-only debug code and has no runtime behavior in release. It directly supports tests that need lifecycle assurance for CF tracking metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_updater_debug.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_util.cc -->
# sources/storage-engines/rocksdb/monitoring/thread_status_util.cc

Purpose: Implements static convenience wrappers for thread-status tracking, caching the current Env's `ThreadStatusUpdater` in thread-local state.

Important APIs/types/functions: Implements `RegisterThread`, `UnregisterThread`, `SetEnableTracking`, `SetColumnFamily`, `SetThreadOperation`, `GetThreadOperation`, `SetThreadOperationStage`, operation property setters, `SetThreadState`, `ResetThreadStatus`, CF metadata creation/erasure, `MaybeInitThreadLocalUpdater`, and `AutoThreadOperationStageUpdater`.

Control flow: The first non-unregister call can initialize the thread-local updater from an Env. Registration records thread type and Env thread ID. Operation setting records start time for non-unknown operations and clears it for unknown. The RAII stage updater stores the previous stage in its constructor and restores it in the destructor.

State and dependencies: Uses thread-local `thread_updater_initialized_` and `thread_updater_local_cache_`; disabled builds use static no-op variables/functions. Depends on Env, SystemClock, and `ThreadStatusUpdater`.

Risks/test signals: The first Env used by a thread wins until `UnregisterThread`, so mixed-Env threads must unregister to switch updater caches. Some methods require prior initialization and silently no-op otherwise. Debug hooks are declared elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_util.h -->
# sources/storage-engines/rocksdb/monitoring/thread_status_util.h

Purpose: Declares the public internal utility class for updating current-thread RocksDB status without exposing direct updater management at every call site.

Important APIs/types/functions: `ThreadStatusUtil` static methods cover thread registration, CF info lifecycle, tracking enablement, current CF, operation, operation stage/properties, state, reset, debug delays, and expected IO-activity mapping. `AutoThreadOperationStageUpdater` is an RAII helper for temporary stage changes.

Control flow/integration: DB, compaction, flush, Env, and iterator code can call these methods to update thread status. The utility lazily caches an Env-provided `ThreadStatusUpdater` per thread and no-ops when tracking is disabled or unavailable.

State and dependencies: Declares thread-local updater cache and initialization flag in enabled builds; disabled builds use static globals. Depends on DB, Env, thread-status public API, and updater declarations.

Risks/test signals: Static thread-local cache makes lifecycle order important. API comments require CF map updates without holding `db_mutex`. Debug-only methods support deterministic mutex/state-delay tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_util_debug.cc -->
# sources/storage-engines/rocksdb/monitoring/thread_status_util_debug.cc

Purpose: Implements debug-only helpers for thread-status tests and IO-activity expectations.

Important APIs/types/functions: `TEST_SetStateDelay` sets a per-state artificial delay. `TEST_StateDelay` sleeps when the configured delay is positive. `TEST_GetExpectedIOActivity` maps thread operation types to `Env::IOActivity` values.

Control flow: Delay functions use an atomic array indexed by `ThreadStatus::StateType`. Expected-activity mapping switches over known DB operations such as flush, compaction, DB open, get, multiget, iterator, checksum verification, entity gets, and manifest checksum retrieval; unknown operations map to `kUnknown`.

State and dependencies: Debug-only state is `static std::atomic<int> states_delay[NUM_STATE_TYPES]`. Depends on updater/util headers and `SystemClock`.

Risks/test signals: Only compiled under `!NDEBUG`. State index validity relies on valid `StateType` inputs. The operation-to-IO mapping is a test oracle for instrumentation paths and must be updated when new status operations imply new IO activities.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/monitoring/thread_status_util_debug.cc -->
