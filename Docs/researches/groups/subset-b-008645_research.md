# Group Research: subset-b-008645

Work item `subset-b-008645` covers 24 RocksDB public API headers under `sources/storage-engines/rocksdb/include/rocksdb`. Each file section is wrapped for reconciliation and split into the source-tree-aligned per-file output path.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/statistics.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/statistics.h

- **Purpose:** Defines RocksDB's public statistics surface: ticker counters, latency/value histograms, stats collection levels, and the `Statistics` customizable interface used by DB options and monitoring integrations.
- **Important APIs/types/functions:** `enum Tickers` catalogs counters for block/secondary/persistent caches, Bloom filters, memtable/table reads, compaction and flush bytes, WAL activity, compression/decompression, BlobDB, transaction overhead, backup bytes, tiered storage, async reads, prefetching, MultiScan, UDI load failures, file-open metadata, and manifest validation. `enum Histograms` catalogs timing and distribution metrics such as `DB_GET`, `DB_WRITE`, file read/write histograms, flush/compaction timings, MultiGet/MultiScan distributions, compression timings, and ingest external file phases. `HistogramData` is the aggregate output shape. `StatsLevel` gates overhead. `Statistics` exports `getTickerCount`, `recordTick`, `setTickerCount`, `getAndResetTickerCount`, `histogramData`, `recordInHistogram`, `reportTimeToHistogram`, `Reset`, `ToString`, and `getTickerMap`. `CreateDBStatistics()` creates the default implementation; `TickersNameMap` and `HistogramsNameMap` bind enum values to names.
- **Control flow:** This header is declarative, but it shapes runtime paths where RocksDB calls `recordTick()` for cheap counters and `reportTimeToHistogram()` for timer samples. `reportTimeToHistogram()` checks `stats_level_` and skips work at `kExceptTimers` or lower before forwarding to `recordInHistogram()`. Backward compatibility routes `recordInHistogram()` to deprecated `measureTime()` when custom implementations only override the older method.
- **State and persistence:** Statistics state is in the concrete implementation, usually in memory and resettable through `Reset()`. `stats_level_` is an atomic member of the abstract base so callers can adjust collection overhead concurrently. Enum ordering is API-sensitive for C++/Java binding coordination, but comments warn C++ values are not guaranteed stable.
- **Dependencies:** Depends on `Customizable` for options/config integration and `Status` for factory/reset results. Metrics are consumed throughout DB, table, cache, compaction, WAL, backup, transaction, and trace paths.
- **Integration points:** `Options::statistics` stores a shared `Statistics`; JNI and Java bindings must update matching conversion code when new values are added. Monitoring systems read ticker maps, histograms, `ToString()`, and stats history snapshots built from these names.
- **Risks:** Adding enum values requires updating name maps and Java bindings or metrics become invisible/mis-mapped. Custom `Statistics` implementations must not throw exceptions into RocksDB. High stats levels can add timer and mutex-time overhead on hot paths.
- **Test signals:** Unit tests should validate enum/name-map coverage, stats-level filtering, `Reset()`, histogram output fields, custom implementation compatibility with `measureTime()`, and expected counter deltas from cache, compaction, backup, and read/write operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/statistics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/stats_history.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/stats_history.h

- **Purpose:** Exposes `StatsHistoryIterator`, the user-facing iterator for snapshots of statistics automatically recorded by RocksDB.
- **Important APIs/types/functions:** `StatsHistoryIterator::Valid()`, `Next()`, `GetStatsTime()`, `GetStatsMap()`, and `status()` define the read contract. `GetFormatVersion()` remains as a deprecated stub returning `-1`.
- **Control flow:** Callers obtain an iterator from `DB::GetStatsHistory(start, end, &iter)`, then loop while `Valid()`, read the timestamp and stat map, call `Next()`, and check `status()` for terminal errors.
- **State and persistence:** The history source can be in memory or on disk depending on DB options. Returned maps are only valid until the iterator is modified. Timestamps are documented as seconds, even though users often choose time ranges using environment clock values.
- **Dependencies:** Depends on `statistics.h` names, `Status`, and DB internals that materialize snapshots. The forward declaration of `DBImpl` signals implementation ownership outside the public header.
- **Integration points:** Used by monitoring and diagnostics code that wants historical stat snapshots rather than current cumulative counters.
- **Risks:** Lifetime of the returned map is easy to misuse. Time-unit confusion can produce empty ranges. Deprecated format-version plumbing should not be used for feature detection.
- **Test signals:** Tests should cover empty history, bounded time ranges, iterator advancement, map lifetime assumptions, and error reporting via `status()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/stats_history.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/status.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/status.h

- **Purpose:** Defines `Status`, RocksDB's lightweight operation-result object, including success/error codes, subcodes, severities, message storage, and debug enforcement that returned statuses are inspected.
- **Important APIs/types/functions:** `Status::Code` covers `kOk`, `kNotFound`, `kCorruption`, `kNotSupported`, `kInvalidArgument`, `kIOError`, `kMergeInProgress`, `kIncomplete`, `kShutdownInProgress`, `kTimedOut`, `kAborted`, `kBusy`, `kExpired`, `kTryAgain`, `kCompactionTooLarge`, and `kColumnFamilyDropped`. `SubCode` refines errors such as `kNoSpace`, `kMemoryLimit`, `kPathNotFound`, `kManualCompactionPaused`, `kTxnNotPrepared`, `kIOFenced`, and `kPrefetchLimitReached`. Static factories create common statuses. Predicates such as `ok()`, `IsNotFound()`, `IsNoSpace()`, `IsTryAgain()`, and `IsCompactionAborted()` classify results. `UpdateIfOk()` preserves the first non-OK failure.
- **Control flow:** RocksDB APIs return `Status` by value. Callers branch on `ok()` or specific predicates. In builds with `ROCKSDB_ASSERT_STATUS_CHECKED`, reading code/subcode/severity or explicitly calling `PermitUncheckedError()` marks the object checked; destruction of an unchecked status aborts with a stack trace.
- **State and persistence:** The object stores code, subcode, severity, retryability/data-loss flags, scope, and optional heap-owned message text. It is copyable and movable; moving resets the source to OK. It is not persistent data itself, but it is the common error carrier across filesystem, DB, backup, trace, and config paths.
- **Dependencies:** Uses `Slice` for message construction and optionally `port/stack_trace.h` for checked-status builds. Many other public headers depend on it.
- **Integration points:** Every public API in this batch returns or embeds `Status`/`IOStatus`. Subcode combinations let higher layers distinguish retry, storage-full, path-missing, memory-limit, transaction, and compaction-control cases without string parsing.
- **Risks:** `operator==` compares only `code_`, not subcode/message/severity, so equality is coarse. Ignoring statuses in checked builds aborts. `AssertOK()` is debug-only. Thread safety is const-only; non-const access requires external synchronization.
- **Test signals:** Tests should exercise factory/predicate mappings, message rendering, copy/move behavior, `UpdateIfOk()` precedence, checked-status enforcement, and subcode-specific branches like NoSpace, MemoryLimit, and IOFenced.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/system_clock.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/system_clock.h

- **Purpose:** Declares the customizable `SystemClock` abstraction used by RocksDB for wall-clock time, monotonic deltas, CPU-time accounting, sleeps, and timed condition-variable waits.
- **Important APIs/types/functions:** `SystemClock::Default()`, `NowMicros()`, `NowNanos()`, `CPUMicros()`, `CPUNanos()`, `SleepForMicroseconds()`, `TimedWait()`, `GetCurrentTime()`, and `TimeToString()` are the core operations. `SystemClock::CreateFromString()` and `Type()` integrate with options customization. `SystemClockWrapper` forwards calls to an inner clock and exposes `Inner()`, `PrepareOptions()`, and `SerializeOptions()`.
- **Control flow:** Internal timing code calls the configured clock. Default `NowNanos()` and `CPUNanos()` derive from microsecond methods; platform implementations can override monotonic nanosecond timing. `TimedWait()` waits until a deadline and reports timeout versus wakeup.
- **State and persistence:** The clock interface usually has no durable state. `GetCurrentTime()` returns epoch seconds and only overwrites the output on success. `SystemClockWrapper` owns a shared target clock.
- **Dependencies:** Depends on `Customizable`, `Status`, `port::CondVar`, and chrono types. Used by rate limiting, statistics, backup timestamps, cache dump deadlines, and other time-sensitive paths.
- **Integration points:** Test clocks and wrappers can be installed through configurable objects. The `kDefaultName()` identifier lets code detect the platform default.
- **Risks:** `NowMicros()` is described as system time in some paths, while `NowNanos()` should be monotonic; substituting a non-monotonic custom clock can break timeout and latency logic. `CPUMicros()` returning zero means unsupported and must be handled by callers.
- **Test signals:** Tests should validate default clock availability, wrapper forwarding, timeout behavior, serialization/config creation, and custom clock edge cases such as unsupported CPU time.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/system_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/table.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/table.h

- **Purpose:** Defines public table-format APIs and options for block-based, plain, cuckoo, and adaptive SST table factories, including cache behavior, checksum/format version choices, index/filter configuration, readahead, UDI integration, and table factory construction.
- **Important APIs/types/functions:** `ReadScopedBlockBufferProvider` leases provider-owned data-block memory. `ChecksumType`, `PinningTier`, `MetadataCacheOptions`, `CacheUsageOptions`, and `BlockBasedTableOptions` control block-based SST behavior. Key nested enums include `IndexType`, `BlockSearchType`, `DataBlockIndexType`, `IndexShorteningMode`, and `PrepopulateBlockCache`. Factory functions include `NewBlockBasedTableFactory()`, `NewPlainTableFactory()`, `NewCuckooTableFactory()`, and `NewAdaptiveTableFactory()`. `PlainTableOptions`, `CuckooTableOptions`, property-name structs, and `TableFactory::{CreateFromString,NewTableReader,NewTableBuilder,Clone,IsDeleteRangeSupported}` define the extension points.
- **Control flow:** Flush, compaction, recovery, repair, and ingestion call `TableFactory::NewTableBuilder()` to write SSTs. Table cache misses, SST dump, and ingestion validation call `NewTableReader()` to open SSTs. Block-based options split into write-time format decisions, such as `format_version`, checksum, block sizing, index kind, filter construction, and read-time behavior, such as cache pinning, readahead, block cache, UDI primary routing, and search strategy.
- **State and persistence:** Many fields are persisted into SST data, footer, or property blocks: checksum type, format version, block layout, index/filter settings, compression-related format metadata, and UDI presence. Cache pointers, pinning, readahead, and `ReadScopedBlockBufferProvider` leases are in-memory runtime state. Format-version comments document cross-version readability boundaries.
- **Dependencies:** Depends on caches, `Cleanable`, `Customizable`, `Env`, options, `Status`, table reader/builder internals, file readers/writers, filters, persistent cache, and `UserDefinedIndexFactory`.
- **Integration points:** `ColumnFamilyOptions::table_factory` selects these factories. Block cache tracing, secondary cache, direct I/O, tiered storage, compaction warming, prefix extraction, filters, compression, and UDI all meet at this configuration surface.
- **Risks:** Misclassifying read-time versus write-time options can produce confusing operational changes because existing readers may not pick up changes until file reopen. Deprecated pinning flags interact with `MetadataCacheOptions`. Excessive pinning can exhaust block cache. UDI primary mode requires all SSTs to have UDI blocks and disables partitioned index/filter combinations. Format-version upgrades can affect downgrade compatibility.
- **Test signals:** Tests should cover factory config parsing, mutable option updates, SST compatibility by format version, cache pinning/memory charging, filter construction and corruption checks, readahead counters, UDI primary/fallback behavior, and table reader/builder open paths used by flush, compaction, repair, and ingestion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/table_properties.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/table_properties.h

- **Purpose:** Defines SST table property names, user-collected property callbacks, property collector factories, and the `TableProperties` structure used to describe persisted SST metadata.
- **Important APIs/types/functions:** `UserCollectedProperties` is a string-to-string map. `TablePropertiesNames` lists property-block keys for DB identity, sizes, indexes, UDI, filters, key/value counts, timestamps, compression, sequence ranges, restart intervals, and separated key/value layout. `TablePropertiesCollector` provides `AddUserKey()`, `BlockAdd()`, `Finish()`, `GetReadableProperties()`, `NeedCompact()`, and `Name()`. `TablePropertiesCollectorFactory::Context` carries CF/level/tiering context and `CreateTablePropertiesCollector()` creates per-file collectors. `TableProperties` contains numeric and string fields plus `ToString()`, `Add()`, `GetAggregatablePropertiesAsMap()`, `ApproximateMemoryUsage()`, `Serialize()`, `Parse()`, and `AreEqual()`. `ParseCompressionNameForDisplay()` decodes stored compression metadata.
- **Control flow:** During table building, RocksDB creates one collector per output file, calls `AddUserKey()` sequentially for entries, calls `BlockAdd()` when blocks are cut, then calls `Finish()` before writing the property block. On read/open, RocksDB parses `TableProperties`, exposes them through DB/table APIs, and may use them for diagnostics, backup IDs, compression display, and validation.
- **State and persistence:** `TableProperties` is persisted in SST property blocks. It records durable properties such as original file number, DB/session/host IDs, data/index/filter sizes, key counts, compression schema, sequence-number time mapping, UDI primary marker, and sequence bounds. User-collected properties are raw bytes and require user interpretation.
- **Dependencies:** Depends on `Customizable`, `Status`, `types.h`, `CompressionManager`, and table internals. The unique-ID helper depends on these fields.
- **Integration points:** Used by compaction, flush, ingestion, backup/open-as-read-only, SST dump, custom collectors, and monitoring. Compression display can consult globally registered or supplied `CompressionManager` instances.
- **Risks:** Collector callback failures are logged and otherwise ignored, so property loss may not fail writes. Exceptions must not escape custom collectors. Raw string properties can be misinterpreted. Compression-name parsing has compatibility branches for pre/post format version 7 and returns generic/unknown values for malformed metadata.
- **Test signals:** Tests should verify collector lifecycle, persisted property round trips, aggregation maps, memory estimates, compression-name parsing, UDI property markers, sequence-bound presence helpers, and behavior when collectors return non-OK.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/table_properties.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/table_reader_caller.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/table_reader_caller.h

- **Purpose:** Defines `TableReaderCaller`, a compact enum tagging who requested table-reader/block-cache access for tracing and analysis.
- **Important APIs/types/functions:** Values include user operations (`kUserGet`, `kUserMultiGet`, `kUserIterator`, `kUserApproximateSize`, `kUserVerifyChecksum`), tools and internal paths (`kSSTDumpTool`, `kExternalSSTIngestion`, `kRepair`, `kPrefetch`, `kCompaction`, `kCompactionRefill`, `kFlush`, `kSSTFileReader`), `kUncategorized`, and `kMaxBlockCacheLookupCaller`.
- **Control flow:** Callers pass one of these tags into table-reader/cache lookup paths; tracing and analysis aggregate hits/misses or block activity by caller.
- **State and persistence:** The enum has no state and is not a durable file format, but trace records/logs may store or interpret its values.
- **Dependencies:** Only depends on the RocksDB namespace header.
- **Integration points:** Used by block cache tracing, table reader benchmarks/tests, compaction refill, flush verification, SST dump, ingestion, and user read paths.
- **Risks:** New table-reader call paths that use `kUncategorized` lose attribution. Consumers must keep arrays sized to `kMaxBlockCacheLookupCaller`.
- **Test signals:** Block cache trace tests should assert expected caller tags for Get, MultiGet, iterator, compaction, flush, ingestion, and SST dump paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/table_reader_caller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/thread_status.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/thread_status.h

- **Purpose:** Exposes runtime status snapshots for RocksDB-related threads returned by `GetThreadList()`.
- **Important APIs/types/functions:** `ThreadStatus` includes `ThreadType`, `OperationType`, `OperationStage`, compaction/flush property enums, `StateType`, immutable fields such as thread id, DB/CF names, operation, elapsed micros, stage, state, and `op_properties`. Utility methods translate enum values and elapsed times to human-readable strings.
- **Control flow:** Instrumented RocksDB threads update internal status tracking while running operations such as compaction, flush, DB open, Get/MultiGet, iterator, checksum verification, and manifest file checksum retrieval. `GetThreadList()` copies those states into public `ThreadStatus` objects.
- **State and persistence:** Status is transient diagnostic state. `kEnabled` tells callers whether RocksDB was built with thread-status support. Operation properties are positional and change meaning by operation type.
- **Dependencies:** Depends on standard containers and the RocksDB namespace. DB APIs populate the structure from internal thread-local/global tracking.
- **Integration points:** Admin tools, logs, and tests use the translation helpers to display currently running compactions, flushes, and read operations.
- **Risks:** The header still documents the feature as under development, so enum and class definitions can change. Misinterpreting `op_properties` without operation-specific names yields incorrect diagnostics.
- **Test signals:** Tests should cover build-enabled/disabled behavior, enum-name mapping, stage transitions during flush/compaction, elapsed-time formatting, and property-name lookup bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/thread_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/threadpool.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/threadpool.h

- **Purpose:** Defines the public `ThreadPool` abstraction for background job execution with adjustable thread count, joining, queue inspection, fire-and-forget submission, and optional reservation.
- **Important APIs/types/functions:** `ThreadPool::JoinAllThreads()`, `SetBackgroundThreads()`, `GetBackgroundThreads()`, `GetQueueLen()`, `WaitForJobsAndJoinAllThreads()`, `SubmitJob()` overloads, `ReserveThreads()`, `ReleaseThreads()`, and `NewThreadPool(int)`.
- **Control flow:** Users create a pool, submit `std::function<void()>` jobs, optionally change background-thread count, wait for completion, or join. Reservation methods default to no-op and can be overridden by implementations that coordinate thread capacity.
- **State and persistence:** Thread count, queue length, job state, and reservations are in-memory runtime state. No durable persistence.
- **Dependencies:** Depends on `<functional>` and the RocksDB namespace. Implementations live outside the header.
- **Integration points:** Useful for utilities or embedders needing a RocksDB-compatible background execution surface separate from `Env` thread pools.
- **Risks:** Jobs are fire-and-forget, so exceptions escaping jobs or lifetime captures are implementation-sensitive. `JoinAllThreads()` discards unstarted threads, while `WaitForJobsAndJoinAllThreads()` promises queued jobs run, so callers must choose deliberately.
- **Test signals:** Tests should validate queue length, job execution, thread-count changes, wait/join semantics, moved functor submission, and reservation overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/threadpool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/tool_hooks.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/tool_hooks.h

- **Purpose:** Provides a work-in-progress hook interface allowing `db_bench_tool` and similar tools to override how DB variants are opened and how the tool exits.
- **Important APIs/types/functions:** `ToolHooks` declares virtual `Open()` overloads for `DB`, column families, read-only DBs, `TransactionDB`, `OptimisticTransactionDB`, secondary/follower opens, and `blob_db::BlobDB`, plus `Exit(int)`. `DefaultHooks` implements the interface using normal RocksDB open calls and `exit(status)`. `defaultHooks` is the global default instance.
- **Control flow:** Tools call through a `ToolHooks` object instead of invoking static DB open methods directly. Custom subclasses can redirect opens to alternate implementations while preserving benchmark/tool call sites.
- **State and persistence:** The hooks do not own durable state by default, but open calls create DB handles and may create/read DB directories, WALs, blob files, and metadata.
- **Dependencies:** Depends on `rocksdb/db.h`, transaction DB forward declarations, and BlobDB types.
- **Integration points:** Primarily integrated with `db_bench_tool`; it bridges benchmarks to DB, transaction, secondary, follower, and BlobDB open paths.
- **Risks:** Marked work in progress and subject to change. Hooks must exactly mirror default semantics for options, CF handle ownership, error propagation, and process exit or benchmark behavior changes.
- **Test signals:** Tool tests should use custom hooks to assert the intended open overload is called, errors propagate, handles are returned/owned correctly, and `Exit()` is interceptable.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/tool_hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/trace_reader_writer.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/trace_reader_writer.h

- **Purpose:** Defines abstract trace I/O endpoints for exporting and replaying RocksDB traces one operation at a time, plus file-backed factories.
- **Important APIs/types/functions:** `TraceWriter::Write()`, `Close()`, and `GetFileSize()`; `TraceReader::Read()`, `Close()`, and `Reset()`; `NewFileTraceWriter()` and `NewFileTraceReader()`.
- **Control flow:** Trace capture writes serialized records through a `TraceWriter`. Replayers read records through a `TraceReader`, optionally call `Reset()` to return to the trace header, and close the endpoint when done.
- **State and persistence:** File-backed implementations persist trace data to `trace_filename` using `Env` and `EnvOptions`. Custom implementations may stream to external systems. The implementation may not be thread-safe.
- **Dependencies:** Depends on `Env`, `EnvOptions`, `Slice`, `Status`, and filesystem abstractions.
- **Integration points:** Used by query, block-cache, and I/O tracing/replay infrastructure. Custom endpoints let users export traces to non-file destinations.
- **Risks:** Reader/writer thread safety is not guaranteed. `Reset()` can fail after close or on non-seekable implementations. Trace size reporting depends on implementation accuracy.
- **Test signals:** Tests should cover file writer/reader round trips, close/error behavior, reset semantics, EOF handling, and custom endpoint substitution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/trace_reader_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/trace_record.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/trace_record.h

- **Purpose:** Declares typed trace records for replayable RocksDB operations and a visitor-style handler interface for executing or processing them.
- **Important APIs/types/functions:** `TraceType` identifies begin/end, write/get/iterator/MultiGet query traces, block-cache trace block kinds, and I/O traces. `TraceRecord` stores a timestamp and defines `GetTraceType()`, `GetTimestamp()`, `Accept()`, and `NewExecutionHandler(DB*, handles)`. Query subclasses include `WriteQueryTraceRecord`, `GetQueryTraceRecord`, `IteratorSeekQueryTraceRecord`, and `MultiGetQueryTraceRecord`; each exposes column-family IDs, keys, bounds, seek type, or write-batch representation.
- **Control flow:** Trace decoding constructs a concrete record, then calls `Accept(handler, &result)`. The handler dispatches by concrete type and can execute against a DB using the provided execution handler, producing a `TraceRecordResult`.
- **State and persistence:** Records hold timestamps and payloads in `PinnableSlice` or vectors. Serialized traces persist the operation inputs; execution results are separate. Iterator records can carry lower/upper bounds to recreate read options.
- **Dependencies:** Depends on `Slice`, `PinnableSlice`, `Status`, DB/ColumnFamilyHandle forward declarations, and `trace_record_result.h` consumers.
- **Integration points:** Used by trace readers, replayers, benchmarking, and diagnostics that need to capture and replay writes, Gets, MultiGets, and iterator seeks.
- **Risks:** Column-family ID vectors must match available handles during replay. WriteBatch representations must remain compatible. Visitor handlers need to distinguish API-level handler success from the underlying operation's returned status.
- **Test signals:** Tests should validate type dispatch, timestamp preservation, payload access, iterator bound replay, MultiGet CF/key vector handling, and execution handler behavior against a DB with multiple column families.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/trace_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/trace_record_result.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/trace_record_result.h

- **Purpose:** Defines result objects returned by trace-record handlers, separating trace dispatch success from the status and values produced by replayed DB operations.
- **Important APIs/types/functions:** `TraceRecordResult` stores the corresponding `TraceType` and has a result `Handler`. `TraceExecutionResult` adds start/end timestamps and `GetLatency()`. Concrete classes are `StatusOnlyTraceExecutionResult`, `SingleValueTraceExecutionResult`, `MultiValuesTraceExecutionResult`, and `IteratorTraceExecutionResult`, with accessors for statuses, values, iterator validity, keys, and values.
- **Control flow:** After a trace record is handled, callers inspect or visit the concrete result through `Accept(handler)`. Execution results preserve the underlying DB status even when `TraceRecord::Accept()` itself returns OK.
- **State and persistence:** Results are transient replay outputs. Values can be owned strings or `PinnableSlice` data copied/moved into the result. Latency is computed from stored timestamps.
- **Dependencies:** Depends on `Status`, `Slice`, `PinnableSlice`, and `TraceType`.
- **Integration points:** Replayers, analyzers, and benchmark harnesses use these results to compare replayed operation behavior or measure latency.
- **Risks:** Consumers can mistakenly treat `Accept()` OK as operation success and ignore embedded `Status`. Vector lengths in MultiGet results must correspond to traced keys. Iterator results carry empty key/value when invalid.
- **Test signals:** Tests should cover visitor dispatch, status/value preservation for NotFound and errors, MultiGet vector round trips, iterator valid/invalid states, and latency calculations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/trace_record_result.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/transaction_log.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/transaction_log.h

- **Purpose:** Exposes WAL metadata and transaction-log iteration APIs for reading write batches from RocksDB logs.
- **Important APIs/types/functions:** `WalFileType` distinguishes archived and live logs. `WalFile` exposes `PathName()`, `LogNumber()`, `Type()`, `StartSequence()`, and `SizeFileBytes()`. `BatchResult` carries a starting `SequenceNumber` and move-only `WriteBatch`. `TransactionLogIterator` exposes `Valid()`, `Next()`, `status()`, `GetBatch()`, and nested `ReadOptions` with checksum verification.
- **Control flow:** Callers enumerate WAL files through DB APIs or call `GetUpdatesSince()` to obtain a `TransactionLogIterator`. A valid iterator returns batches in sequence until a gap or error; callers use `Next()` only while valid and inspect `status()`.
- **State and persistence:** WAL files are durable DB log files, either live in the DB directory or archived under the archive directory. `StartSequence()` and `BatchResult::sequence` define replay ordering. `SizeFileBytes()` is the flushed extent and matters for recycled WAL files.
- **Dependencies:** Depends on `Status`, `types.h`, and `WriteBatch`.
- **Integration points:** Used by replication, backup, change-data-capture, recovery tooling, and transaction log diagnostics.
- **Risks:** Iteration stops at sequence gaps. Disabling checksum verification trades safety for speed. `BatchResult` is move-only, so API users must not copy it. WAL archival/cleanup options can remove needed history.
- **Test signals:** Tests should cover live/archived file metadata, iterator continuity, gap behavior, checksum verification failures, recycled WAL sizes, and move-only batch ownership.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/transaction_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/types.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/types.h

- **Purpose:** Centralizes public lightweight RocksDB type aliases and enums shared across headers.
- **Important APIs/types/functions:** Defines `ColumnFamilyId`, `SequenceNumber`, `TablePropertiesCollection`, `kMinUnCommittedSeq`, `TableFileCreationReason`, `BlobFileCreationReason`, `FileType`, `EntryType`, `ParsedEntryInfo`, `WriteStallCause`, `WriteStallCondition`, and file `Temperature`.
- **Control flow:** These are consumed as classification and identity values across APIs. `ParsedEntryInfo` provides user key, optional timestamp, sequence number, and entry type when exposing internal entries.
- **State and persistence:** Several values correspond to durable concepts: WAL sequence numbers, file types in DB directories, table/blob creation reasons, internal key entry types, and tiered-storage temperatures. Comments warn enum ordering for `EntryType` should not change.
- **Dependencies:** Depends on `Slice` and forward-declared `TableProperties`.
- **Integration points:** Used by table properties, transaction logs, compaction/tiering, file-system placement, write-stall reporting, and public metadata APIs.
- **Risks:** Changing enum values can break API compatibility or persisted/diagnostic interpretation. `Temperature::kLastTemperature` is explicitly misnamed as an invalid sentinel, so code should not treat it as a real tier.
- **Test signals:** Tests should validate enum conversion/display code elsewhere, sequence-number edge cases, timestamp parsing with and without user-defined timestamps, and write-stall/temperature mapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/unique_id.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/unique_id.h

- **Purpose:** Declares helpers for deriving stable binary unique IDs for SST files from `TableProperties`.
- **Important APIs/types/functions:** `GetUniqueIdFromTableProperties()` returns a 128-bit binary ID, `GetExtendedUniqueIdFromTableProperties()` returns a 192-bit binary ID, and `UniqueIdToHumanString()` formats binary IDs as uppercase hex groups separated by dashes.
- **Control flow:** Callers pass parsed table properties; helpers return `NotSupported` when required properties are missing, typically for older SSTs. Successful IDs can be stored, compared, shortened as prefixes, or displayed using the formatter.
- **State and persistence:** The ID is derived from persisted SST properties such as DB/session/file identity. The binary string may contain NUL bytes and must not be handled with C-string APIs.
- **Dependencies:** Depends on `table_properties.h` and `Status`.
- **Integration points:** Backup systems, file catalogs, and diagnostics use these IDs to distinguish SST files beyond file number/name.
- **Risks:** Older files do not support IDs. Misusing `.c_str()` loses entropy at embedded NUL bytes. 128-bit IDs are sufficient for most deployments, but globally shared backup namespaces may need the 192-bit extended form.
- **Test signals:** Tests should cover supported and unsupported property sets, binary length, non-zero 128-bit prefix, human formatting of full and prefix IDs, and collision assumptions using DB/session/file changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/unique_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/universal_compaction.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/universal_compaction.h

- **Purpose:** Defines public configuration for universal compaction picking and limits.
- **Important APIs/types/functions:** `CompactionStopStyle` selects similar-size or total-size file picking. `CompactionOptionsUniversal` fields include `size_ratio`, `min_merge_width`, `max_merge_width`, `max_size_amplification_percent`, `compression_size_percent`, `max_read_amp`, `stop_style`, `allow_trivial_move`, `incremental`, and `reduce_file_locking`, with a default constructor and defaulted equality operator.
- **Control flow:** Universal compaction logic reads these options to decide when files are compacted, how many sorted runs to tolerate, whether output should be compressed, whether trivial moves are allowed, and whether to adjust file picking when bottom-priority compactions wait.
- **State and persistence:** Options are runtime configuration and can affect future compaction outputs; they are not direct persisted metadata. Some choices influence file layout and compression of new SSTs.
- **Dependencies:** Uses basic integer/vector headers and the RocksDB namespace.
- **Integration points:** Consumed by column-family compaction options and dynamic `SetOptions()` for `reduce_file_locking`.
- **Risks:** Invalid `max_read_amp` values can cause `Status::NotSupported()` at DB open. Aggressive `max_size_amplification_percent`, `incremental`, or file-locking reduction can trade read amplification, write amplification, and compaction load. Some automatic behavior only applies with total-size stop style.
- **Test signals:** Tests should cover default values, option equality, DB-open validation, compaction-picking boundaries, compression-size thresholds, trivial-move behavior, and dynamic `reduce_file_locking` updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/universal_compaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/user_defined_index.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/user_defined_index.h

- **Purpose:** Declares the experimental public API for user-defined SST indexes, including builders, readers, iterators, and factories.
- **Important APIs/types/functions:** `kUserDefinedIndexPrefix` prefixes UDI block names. `UserDefinedIndexBuilder` defines `ValueType`, `BlockHandle`, `IndexEntryContext`, `AddIndexEntry()`, `OnKeyAdded()`, `Finish()`, and `EstimatedSize()`. `UserDefinedIndexIterator` defines scan preparation, `SeekToFirstAndGetResult()`, `SeekToLastAndGetResult()`, `SeekAndGetResult()`, `NextAndGetResult()`, `PrevAndGetResult()`, `value()`, and sequence-aware `SeekContext`. `UserDefinedIndexReader` creates iterators and reports memory usage. `UserDefinedIndexOption` supplies a comparator. `UserDefinedIndexFactory` creates builders/readers and is `Customizable`.
- **Control flow:** During table building, RocksDB calls `OnKeyAdded()` for entries and `AddIndexEntry()` at block boundaries, then `Finish()` to get serialized index contents. During reads/scans, RocksDB creates a reader from the index block, allocates iterators, calls `Prepare()` for scan batches, and seeks/steps through UDI entries to obtain block handles.
- **State and persistence:** Serialized UDI contents are persisted in SST meta blocks. Builders own serialized buffers until destruction. Readers own parsed index structures and report memory usage. Sequence tags in contexts are needed when the same user key spans block boundaries.
- **Dependencies:** Depends on advanced iterator result types, `Customizable`, options, comparator, slices, `Status`, and `types.h`.
- **Integration points:** Wired through `BlockBasedTableOptions::user_defined_index_factory`, `use_udi_as_primary_index`, and `ReadOptions::table_index_factory`. UDI primary mode changes all read paths, including compaction and checksum verification.
- **Risks:** The API is experimental. Only monolithic index blocks are supported. Reverse iteration requires overriding default NotSupported methods. Incorrect separators or sequence-tag handling can route reads to wrong data blocks. Primary mode requires migration discipline and is incompatible with partitioned indexes/filters.
- **Test signals:** Tests should validate builder callback ordering, duplicate user-key/sequence-boundary cases, serialized reader round trips, forward and reverse iteration, bound-check results, comparator customization, primary/fallback read routing, and missing-UDI open failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/user_defined_index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/user_write_callback.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/user_write_callback.h

- **Purpose:** Exposes `UserWriteCallback`, a small interface for user-defined validation or side effects around writes.
- **Important APIs/types/functions:** `UserWriteCallback::Callback(DB*)` is the only operation and returns `Status`.
- **Control flow:** Internal write paths that accept a callback invoke `Callback()` with the target DB; the returned status can allow or abort the write flow depending on the caller.
- **State and persistence:** The interface has no state. Implementations may inspect DB state or maintain external state, but persistence semantics depend on the write path invoking it.
- **Dependencies:** Depends on `Status` and forward-declared `DB`.
- **Integration points:** Used by advanced write APIs or transaction paths that need user logic during a write.
- **Risks:** Callback implementations run in sensitive write-path context and must avoid deadlocks, expensive operations, and exceptions. The header does not define ownership or threading policy beyond the virtual contract.
- **Test signals:** Tests should cover callback success/failure propagation, DB pointer validity, write abort semantics, and callback behavior under concurrent writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/user_write_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/agg_merge.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/agg_merge.h

- **Purpose:** Declares an experimental aggregation merge-operator utility that multiplexes merge operands to registered aggregation functions by function name.
- **Important APIs/types/functions:** `Aggregator::Aggregate()` combines values in reverse insertion order and `DoPartialAggregate()` controls partial aggregation. `AddAggregator()` registers a named plugin. `GetAggMergeOperator()` returns the singleton merge operator. `EncodeAggFuncAndPayload()`, `ExtractAggFuncAndValue()`, and `ExtractList()` encode/decode operands and error lists. `kUnnamedFuncName` and `kErrorFuncName` are reserved function names.
- **Control flow:** Users register aggregators, install the singleton merge operator, encode Put/Merge payloads with function names, and Reads trigger aggregation. Changing function names for a key causes prior operands to be aggregated and used as the first payload for the new function.
- **State and persistence:** Encoded function/payload data is stored as DB values and merge operands. Aggregator registry is process-global and not thread-safe to mutate concurrently with merge operation use.
- **Dependencies:** Depends on `MergeOperator`, `Slice`, `Status`, strings, and vectors.
- **Integration points:** Bridges RocksDB merge semantics to reusable aggregation functions, including functions inspired by SQL engines or third-party aggregation libraries.
- **Risks:** Encoding format is explicitly subject to change. Missing aggregators or aggregation errors encode an error function with operand lists rather than necessarily failing the DB operation. Registry mutation races can affect active DBs.
- **Test signals:** Tests should cover encoding/decoding, unnamed-to-named transitions, function switching, partial aggregation, missing/error aggregators, singleton reuse, and registry initialization before DB open.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/agg_merge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/backup_engine.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/backup_engine.h

- **Purpose:** Defines the BackupEngine public API for creating, verifying, restoring, opening, purging, and deleting RocksDB backups, including shared-file naming, metadata, restore modes, concurrency guarantees, and read-only access.
- **Important APIs/types/functions:** `BackupEngineOptions` configures `backup_dir`, backup env, shared table/blob files, sync, log backup, rate limiting, background operations, naming scheme, schema version, and temperature metadata behavior. `CreateBackupOptions` controls flushing, callbacks, file exclusion, background CPU priority, and atomic flush. `RestoreOptions` controls log retention, alternate directories, and restore mode. `BackupInfo`, `BackupFileInfo`, `BackupExcludedFileInfo`, `MaybeExcludeBackupFile`, `BackupStatistics`, `BackupEngineReadOnlyBase`, `BackupEngineAppendOnlyBase`, `BackupEngine`, and `BackupEngineReadOnly` define the operational API.
- **Control flow:** Writable engines open a backup directory, clean incomplete work as needed, create backups by optionally flushing a DB and copying/linking live files plus WALs, record metadata, verify backups by size/checksum, restore selected or latest backups, and purge/delete old backups. Read-only engines expose info, verification, and restore without mutating the backup directory.
- **State and persistence:** Backup directories persist shared files, per-backup metadata, application metadata, checksum/naming information, optional file temperature metadata, and excluded-file references. `share_files_with_checksum_naming` can mix schemes in one directory. `StopBackup()` is one-way for that engine instance and leaves cleanup to later backup/GC.
- **Dependencies:** Depends on `Env`, `IOStatus`, metadata/file storage info, DB options, rate limiter, logger, filesystem behavior, and `Status`.
- **Integration points:** Used by backup/restore utilities, read-only backup DB opens, incremental restore workflows, file-exclusion systems, and monitoring through `BACKUP_READ_BYTES`/`BACKUP_WRITE_BYTES` statistics.
- **Risks:** `share_files_with_checksum=false` is deprecated and can lose data with divergent histories. Cross-engine interleavings on the same backup directory are mostly unspecified for write operations. Excluding shared files makes restore depend on `alternate_dirs`. Schema-version choices affect temperature metadata readability. Unsynced backups sacrifice crash consistency for speed.
- **Test signals:** Tests should cover create/restore/verify, checksum and size mismatch detection, shared-file naming schemes, excluded-file restore with alternates, read-only open limits, stop/GC cleanup behavior, purge/delete crash recovery, rate limiting, atomic flush, and documented concurrency behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/backup_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/cache_dump_load.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/cache_dump_load.h

- **Purpose:** Declares experimental APIs for dumping block-cache entries from one host and loading them into a destination secondary cache for cache warmup.
- **Important APIs/types/functions:** Format constants `kCacheDumpMajorVersion` and `kCacheDumpMinorVersion`. `CacheDumpWriter` writes metadata and packets. `CacheDumpReader` reads metadata and packets. `CacheDumpOptions` carries a `SystemClock`, deadline, and max byte budget. `CacheDumper` supports `SetDumpFilter()` and `DumpCacheEntriesToWriter()`. `CacheDumpedLoader` restores entries to secondary cache. Factory functions create file readers/writers, the default dumper, and the default loader.
- **Control flow:** A source process creates a writer and default dumper, optionally filters by DB list, writes metadata once, then writes cache-entry packets. A destination process creates a reader and loader, reads metadata once, then loads packets into a secondary cache before DB reopen.
- **State and persistence:** The dump format stores metadata and packetized block contents including type, dump time, cache key, block length, checksum, and block data. File-backed readers/writers persist the stream; loaders populate secondary cache, not the primary block cache.
- **Dependencies:** Depends on cache, Env, FileSystem, `IOStatus`, secondary cache, table options, `SystemClock`, and block-based table options.
- **Integration points:** Intended for DB migration/warmup workflows where copied SST files arrive on another host and the secondary cache can be prefilled.
- **Risks:** API and data format are experimental. Deadline and size limits can produce partial dumps. Cache keys must remain meaningful on the destination. Only secondary-cache loading is supported. Default methods return NotSupported unless concrete factories are used.
- **Test signals:** Tests should cover metadata-before-packets ordering, EOF as empty packet, checksum/version validation, DB filtering, deadline/size cutoff, file round trips, and restored secondary-cache hit behavior after DB open.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/cache_dump_load.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/checkpoint.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/checkpoint.h

- **Purpose:** Declares `Checkpoint`, an API for creating openable point-in-time snapshots and exporting live SST files for a column family.
- **Important APIs/types/functions:** `Checkpoint::Create(DB*, Checkpoint**)`, `CreateCheckpoint(checkpoint_dir, log_size_for_flush, sequence_number_ptr)`, `ExportColumnFamily(handle, export_dir, metadata)`, and destructor.
- **Control flow:** Users create a `Checkpoint` bound to a DB, then call `CreateCheckpoint()` with a non-existing absolute destination. RocksDB flushes depending on WAL size and 2PC rules, hard-links SST/blob files when possible, copies files otherwise, and always copies required metadata such as MANIFEST. `ExportColumnFamily()` flushes and exports live SSTs for a CF with metadata.
- **State and persistence:** Checkpoints are durable directory snapshots that can be opened as DBs. Exported CF directories contain hard links or copies plus export/import metadata. Optional sequence-number output identifies a sequence guaranteed to be included.
- **Dependencies:** Depends on `DB`, column-family handles, live-file metadata, export/import metadata, and `Status`.
- **Integration points:** Used by backup workflows, snapshot export/import, testing, and operational cloning.
- **Risks:** If WAL writing is disabled and flush is not forced appropriately, the checkpoint may miss recent memtable data. Multi-directory DB paths are not supported for checkpoint/export. Destination directories must not already exist.
- **Test signals:** Tests should cover hard-link versus copy fallback, flush threshold behavior, sequence-number output, 2PC flush behavior, unsupported multi-path DBs, export metadata validity, and opening a created checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/checkpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/convenience.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/convenience.h

- **Purpose:** Compatibility forwarding header for code that still includes `rocksdb/utilities/convenience.h` after the real header moved to `rocksdb/convenience.h`.
- **Important APIs/types/functions:** No local APIs are declared; it includes `rocksdb/convenience.h`.
- **Control flow:** Preprocessor inclusion redirects callers to the new header location.
- **State and persistence:** No runtime state or persisted data.
- **Dependencies:** Depends on `rocksdb/convenience.h`.
- **Integration points:** Preserves source compatibility for existing applications and utilities using the old include path.
- **Risks:** Any symbols, dependencies, or warnings come from the forwarded header. Removing this shim would break old includes.
- **Test signals:** Compile tests should include both old and new header paths and verify the expected convenience APIs remain available.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/utilities/convenience.h -->
