# subset-b-008644 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/options.h -->
# sources/storage-engines/rocksdb/include/rocksdb/options.h

Purpose: This header is the central public configuration contract for RocksDB. It declares the option structs passed into DB open, column-family open, reads, writes, flushes, compactions, external file ingestion, tracing, size estimation, remote compaction, live-file export, and wait-for-compaction APIs. Most behavior is expressed as defaults and documented constraints rather than executable control flow, but those fields drive nearly every storage-engine path: WAL recovery, MANIFEST handling, memtable flush, compaction selection, table format, cache tiering, rate limiting, file placement, checksumming, snapshots, and iterator semantics.

Important APIs and types: `ColumnFamilyOptions` extends `AdvancedColumnFamilyOptions` with user-visible per-CF knobs such as `comparator`, `merge_operator`, compaction filters/factories, `write_buffer_size`, compression settings, `prefix_extractor`, level sizing, auto-compaction disable, `table_factory`, `cf_paths`, `compaction_thread_limiter`, `sst_partitioner_factory`, `memtable_max_range_deletions`, and `uncache_aggressiveness`. `DBOptions` defines process/DB-wide behavior: creation flags, paranoid verification, WAL tracking, Env and FileSystem integrations, rate limiter, SST file manager, logging, file-open policy, WAL size policy, background jobs, MANIFEST rotation/reuse/recovery optimization, WAL archive retention, mmap/direct IO, stats persistence, write-buffer manager, sync pacing, listeners, write concurrency, WAL recovery, two-phase commit, row cache, WAL filter, recovery/shutdown flush policy, ingestion defaults, manual WAL flushing, WAL compression, atomic flush, identity/DB id recording, best-efforts recovery, background error resume, compaction service, cache tier selection, off-peak compaction, follower catch-up, filesystem temperatures, and fast SST open. `Options` combines `DBOptions` and `ColumnFamilyOptions` for single-CF open and convenience tuning methods.

Other exported option types include `WALRecoveryMode`, `DbPath`, `CompactionServiceJobInfo`, `CompactionServiceScheduleResponse`, `CompactionService`, `ReadTier`, `Range`, `RangeOpt`, `ScanOptions`, `MultiScanArgs`, `ReadOptions`, `WriteOptions`, `FlushOptions`, `FlushWALOptions`, `CompactionOptions`, `BottommostLevelCompaction`, `BlobGarbageCollectionPolicy`, `CompactRangeOptions`, `IngestExternalFileOptions`, `IngestExternalFileArg`, `TraceOptions`, `ImportColumnFamilyOptions`, `SizeApproximationOptions`, `CompactionServiceOptionsOverride`, `OpenAndCompactOptions`, `LiveFilesStorageInfoOptions`, and `WaitForCompactOptions`. `CreateLoggerFromOptions()` is the file's direct helper function declaration.

Control flow: There is little executable flow in the header, but several small classes encode API behavior. `Options` constructors compose DB and CF options and expose `OldDefaults()`, `PrepareForBulkLoad()`, `OptimizeForSmallDb()`, and `DisableExtraChecks()` for chained tuning. `MultiScanArgs` stores a comparator and an ordered vector of `ScanOptions`, supports copy/move, inserts bounded or unbounded scan ranges with optional property bags, tests whether all scans are bounded, exposes implicit vector-pointer conversions for compatibility, and copies non-range IO settings from another instance. `CompactionService` defaults `Schedule()` and `Wait()` to `kUseLocal`, so unimplemented services fall back to local compaction. `FlushOptions`, `FlushWALOptions`, and `CompactionOptions` establish constructor defaults inline.

State and persistence behavior: The fields determine what RocksDB writes, validates, retains, and replays. WAL-related options control durability and recovery: `sync`, `disableWAL`, WAL recovery modes, WAL tracking in MANIFEST or predecessor WALs, WAL archive TTL/size, WAL compression, manual flushing, `avoid_flush_during_recovery`, write-buffer-manager enforcement during recovery, and `track_and_verify_wals`. MANIFEST behavior is shaped by max size, space amplification, close-time verification, reuse-on-open, recovery optimization, DB id storage, and best-efforts recovery. SST/blob persistence is shaped by table factory, compression, file checksums, SST unique-id verification, DB paths/CF paths, filesystem temperatures, direct IO, file preallocation, SstFileManager space limits, external file ingestion, atomic replace ranges, compaction outputs, and OpenAndCompact resumption. Stats can be in memory or persisted to a hidden column family. Snapshot and iterator correctness can be weakened by settings like `unordered_write`, `ignore_range_deletions`, or unsafe prefix options, so defaults generally favor correctness.

Dependencies and integration points: The header pulls in `advanced_options.h`, comparator, compression, customizable configuration, Env, checksum, event listeners, SST partitioning, universal compaction, version/types, and write-buffer management. It forward-declares many public and internal integration objects: `Cache`, `CompactionFilter`, `Comparator`, `ConcurrentTaskLimiter`, `Env`, `SstFileManager`, `Logger`, `MergeOperator`, `Snapshot`, `RateLimiter`, `Statistics`, `WalFilter`, `FileSystem`, `UserDefinedIndexFactory`, `IODispatcher`, and table/cache-related helpers. Public APIs across `DB`, `ColumnFamilyHandle`, `Iterator`, `SstFileWriter`, compaction services, backup/checkpoint flows, and tools consume these structs.

Important API contracts: Comparators and merge operators must keep the same name and semantics across opens. Prefix extractors must produce comparator-contiguous prefixes for safe prefix filtering. Exceptions must not escape from `CompactionService`. Direct compaction reads reject mmap reads and can fail later when SST paths lack O_DIRECT support. Ingestion options interact strongly: `move_files` and `link_files` are exclusive; DB-generated files preserve original sequence numbers and must obey strict overlap/order constraints; global sequence numbers are required for overlapping writer-generated files; `ingest_behind` requires compatible CF history. `ReadOptions::snapshot` must belong to the DB and be unreleased; `ReadOptions` timestamp fields require a timestamp-aware comparator. `CompactRangeOptions::canceled` can be overwritten by disabling manual compaction, whereas `CompactionOptions::canceled` is not.

Risks and edge cases: This header is a broad ABI/API surface, so field order, defaults, and option names are compatibility-sensitive. Several settings are explicitly deprecated, experimental, or temporary kill switches. Many options can silently trade correctness for performance, including `unordered_write`, `ignore_range_deletions`, `avoid_flush_during_shutdown`, weak ingestion ordering, and old single-delete contract migration. Prefix seek optimization has documented bugs around short keys and immediate-successor bounds. `best_efforts_recovery` is designed for missing/truncated files and incomplete physical copies, not arbitrary corruption. Remote compaction and compaction service options depend on external implementations that must not throw. Several defaults are mutable via `SetOptions()`/`SetDBOptions()`, so code must distinguish immutable open-time behavior from dynamic behavior.

Test signals: Good tests cover option sanitization, default dumps, string parsing/configuration, incompatible option rejection, WAL recovery modes, MANIFEST verification/reuse/rotation, direct IO open and compaction failure modes, best-efforts recovery from missing/truncated files, prefix seek equivalence, ingestion overlap and checksum paths, external file atomic replace, compaction cancellation, trace filtering, MultiScan bounded-range behavior, stats persistence, rate-limiter priorities, and remote compaction fallback to local execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/perf_context.h -->
# sources/storage-engines/rocksdb/include/rocksdb/perf_context.h

Purpose: This header defines RocksDB's per-thread performance counter surface. It exposes aggregate and per-level counters that storage-engine code updates when `PerfLevel` enables the relevant metric classes. The counters let callers diagnose read, write, cache, iterator, WAL, memtable, Env, encryption, blob, ingestion, and internal-lock costs without changing individual API signatures.

Important APIs and types: `PerfContextByLevelBase` holds per-level point-read counters: Bloom useful/positive/true-positive stats, returned user keys, SST table-read time, and block-cache hits/misses. `PerfContextByLevel` adds `Reset()`. `PerfContextBase` is the large flat counter struct. It tracks user key comparisons, block/cache read counts and bytes, secondary-cache activity, checksum/decompression time, bytes returned by Get/MultiGet/iterators, blob-cache and blob-file IO, internal iterator skips/deletes/recent keys/merge operands/range-deletion reseeks, Get and iterator phase timings, write phase timings, write-thread waits, DB mutex/condition waits, table-reader/index/filter/block construction timings, memtable/SST bloom counts, transaction key-lock waits, TimedEnv filesystem operation timings, CPU nanos for reads/iterator operations, iterator call counts, encryption/decryption time, async seeks, file ingestion latency, and block-category read-byte breakdown. `PerfContext` provides construction, copy/move, `Reset()`, `ToString()`, per-level allocation toggles, `copyMetrics()`, and ownership of `level_to_perf_context`. `get_perf_context()` returns the active context.

Control flow: Callers set the current thread's perf level through `perf_level.h`, then RocksDB internals increment fields directly or through macros in implementation files. `PerfContext::Reset()` clears the counters, `ToString()` formats them, and `EnablePerLevelPerfContext()` allocates `std::map<uint32_t, PerfContextByLevel>` storage and flips the enable flag. `DisablePerLevelPerfContext()` temporarily stops per-level accounting without freeing the map; `ClearPerLevelPerfContext()` releases it. `get_perf_context()` returns a thread-local context when perf context is compiled in, or a global no-op context when `NPERF_CONTEXT` disables instrumentation.

State and persistence behavior: The state is transient diagnostic state only. Counters are per thread in normal builds and are resettable by the application. They do not persist to DB files and do not change storage behavior except for the runtime cost of instrumentation. The per-level map is heap-owned by `PerfContext` and must be explicitly enabled before level breakdowns are collected.

Dependencies and integration points: It depends on `rocksdb/perf_level.h` for collection levels and standard `map`/`string`. It integrates with DB read/write paths, table cache, block cache, secondary cache, blob DB, transaction lock manager, Env wrappers, encryption Env, external file ingestion, and tests that assert or print performance counters. The file comments require any field changes to be mirrored in `DEF_PERF_CONTEXT_METRICS()` or `DEF_PERF_CONTEXT_LEVEL_METRICS()` in `perf_context.cc`.

Risks and edge cases: Field order is intentionally locked; reordering or adding fields without macro updates breaks builds and can corrupt metric reporting. Some timing groups are documented as potentially inaccurate when 2PC, two write queues, or pipelined writes are enabled. Disabled perf context returns a non-null no-op object, so tests must account for build flags. Per-level collection adds dynamic allocation and map lookup overhead. Metrics have different minimum `PerfLevel`s, so zero values can mean either no activity or instrumentation not enabled.

Test signals: Tests should verify `Reset()` zeroes all counters, `ToString(true)` omits zero counters, per-level contexts allocate/disable/clear correctly, copy/move retain metric values, `get_perf_context()` is thread-local in normal builds, and counters appear only at the expected `PerfLevel`. Regression tests should catch macro/header drift when fields are added.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/perf_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/perf_level.h -->
# sources/storage-engines/rocksdb/include/rocksdb/perf_level.h

Purpose: This small public header defines the instrumentation level used by RocksDB performance counters. It controls how much data `perf_context` and `iostats_context` collect for the current thread.

Important APIs and types: `enum PerfLevel : unsigned char` defines `kUninitialized`, `kDisable`, `kEnableCount`, `kEnableWait`, `kEnableTimeExceptForMutex`, `kEnableTimeAndCPUTimeExceptForMutex`, `kEnableTime`, and sentinel `kOutOfBounds`. `SetPerfLevel(PerfLevel level)` sets the current thread's collection level. `GetPerfLevel()` returns it.

Control flow: Levels are incremental: enabling a higher level includes metrics from lower levels plus additional categories. Count/byte metrics start at `kEnableCount`; RocksDB-internal wait/delay metrics start at `kEnableWait`; operation timing starts at `kEnableTimeExceptForMutex`; CPU time starts at `kEnableTimeAndCPUTimeExceptForMutex`; mutex/condition timing starts at `kEnableTime`.

State and persistence behavior: The setting is runtime-only and thread-local. It does not persist in DB state and does not affect logical results, but higher levels add measurement overhead.

Dependencies and integration points: The header depends only on `rocksdb_namespace.h` plus standard types. `perf_context.h`, iostats collection, DB tests, benchmarking tools, and applications that need diagnostics call these APIs.

Risks and edge cases: `kOutOfBounds` must remain the last value. Metric names generally imply their enabling level, but comments in metric declarations are the source of truth for exceptions. Tests must avoid assuming metrics are populated when the level is too low.

Test signals: Unit tests should verify set/get behavior per thread, incremental metric enabling, disabled mode preserving zero/no-op counters, and boundary validation around `kOutOfBounds`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/perf_level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/persistent_cache.h -->
# sources/storage-engines/rocksdb/include/rocksdb/persistent_cache.h

Purpose: This header declares the legacy persistent read-cache interface for caching IO pages or blocks on persistent media. It gives RocksDB an abstract cache tier that survives process restarts and is optimized for read caching.

Important APIs and types: `PersistentCache` defines `StatsType` as `std::vector<std::map<std::string, double>>` for per-tier stats. Its virtual API includes `Insert(const Slice& key, const char* data, size_t size)`, `Lookup(const Slice& key, std::unique_ptr<char[]>* data, size_t* size)`, `IsCompressed()`, `Stats()`, `GetPrintableOptions()`, and `NewId()`. `NewPersistentCache()` constructs an implementation from `Env`, path, capacity, logger, NVM optimization flag, and output shared pointer.

Control flow: Callers insert page data under a stable key, then later look it up into an owned buffer. `IsCompressed()` tells RocksDB whether cached bytes are serialized/compressed blocks with trailers or uncompressed blocks. `NewId()` lets multiple clients allocate numeric prefixes for cache-key sharding at startup.

State and persistence behavior: Unlike in-memory block cache, implementation state is intended to live on a persistent medium under the configured path and size. The interface copies inserted data, returns lookup data through owned buffers, and exposes tier stats. The header itself does not define eviction, crash consistency, or key namespace format; implementations own those choices.

Dependencies and integration points: It depends on `Env`, `Slice`, `Statistics`, `Status`, and `Logger`. It integrates with RocksDB block/table read paths that can use persistent cache as a read cache, and with applications configuring a cache through `NewPersistentCache()`.

Risks and edge cases: Cache keys must be unique across restarts and clients; misuse can produce stale or cross-DB cache hits. `IsCompressed()` must match the stored bytes or readers can decompress/interpret blocks incorrectly. Implementations must define how they handle partial writes, corruption, eviction, and capacity pressure. The comments contain a minor typo in "tier", but the API intent is clear.

Test signals: Tests should exercise insert/lookup round trips, misses, compressed versus uncompressed mode, persistence across reopen when supported, `NewId()` uniqueness, capacity/eviction behavior in the concrete implementation, and stats/reporting content.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/persistent_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/point_lock_bench_tool.h -->
# sources/storage-engines/rocksdb/include/rocksdb/point_lock_bench_tool.h

Purpose: This header declares the entry point for a point-lock benchmark tool under the RocksDB namespace. It is a public-ish tool hook rather than a storage-engine data structure.

Important APIs and types: `int point_lock_bench_tool(int argc, char** argv);` is the only declaration. It mirrors a `main()`-style signature and returns a process-style status code.

Control flow: The implementation is elsewhere. Callers pass command-line arguments through to the tool entry point, which presumably parses options and runs point-lock benchmark scenarios.

State and persistence behavior: The header defines no persistent state. Any benchmark-created DBs, logs, or temporary files are implementation details outside this file.

Dependencies and integration points: It includes only `rocksdb_namespace.h`. It integrates with RocksDB's tool binaries or test/benchmark launchers that want to call the tool from a shared entry point.

Risks and edge cases: The raw `char**` API inherits normal command-line lifetime and mutability assumptions. The declaration provides no options schema, so integration tests must rely on the implementation or binary help output.

Test signals: Build/link tests should ensure the symbol is defined. Tool tests should invoke it with representative valid and invalid argument lists and validate exit codes and benchmark output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/point_lock_bench_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/port_defs.h -->
# sources/storage-engines/rocksdb/include/rocksdb/port_defs.h

Purpose: This header holds small common definitions shared by RocksDB porting code, public API headers, and internal directories.

Important APIs and types: It forward-declares `port::CondVar` and defines `enum class CpuPriority` with `kIdle`, `kLow`, `kNormal`, and `kHigh`.

Control flow: There is no executable control flow. The enum is consumed by scheduling or thread/CPU-priority integration code elsewhere.

State and persistence behavior: It defines no state and has no persistence effect. CPU priority is a runtime scheduling hint when used by implementations.

Dependencies and integration points: It depends only on `rocksdb_namespace.h`. Port implementations, Env/threading code, and public APIs can include it without pulling in heavier platform headers.

Risks and edge cases: The enum's numeric values are part of cross-component assumptions if serialized, logged, or mapped to OS priorities. Platform-specific code must handle unsupported priority changes gracefully.

Test signals: Compile tests should verify low dependency weight. Port tests should validate mappings from `CpuPriority` to actual platform priority behavior where implemented.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/port_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/rate_limiter.h -->
# sources/storage-engines/rocksdb/include/rocksdb/rate_limiter.h

Purpose: This header defines RocksDB's IO rate-limiting interface and the factory for the generic token-bucket limiter. It lets DB-wide options throttle reads, writes, or all IO, primarily background flush/compaction but also selected user reads/writes when request options opt in.

Important APIs and types: `RateLimiter` defines `OpType::{kRead,kWrite}` and `Mode::{kReadsOnly,kWritesOnly,kAllIo}`. The constructor defaults to write-only limiting for API compatibility. Virtual APIs include `SetBytesPerSecond()`, optional `SetSingleBurstBytes()`, older `Request(bytes, pri)`, stats-aware `Request(bytes, pri, stats)`, operation-aware `Request(bytes, pri, stats, op_type)`, `RequestToken(bytes, alignment, io_priority, stats, op_type)`, `GetSingleBurstBytes()`, `GetTotalBytesThrough()`, `GetTotalRequests()`, optional `GetTotalPendingRequests()`, `GetBytesPerSecond()`, and `IsRateLimited()`. `NewGenericRateLimiter()` constructs a shareable implementation with rate, refill period, fairness, mode, auto-tuning, and burst size.

Control flow: Callers ask for tokens before IO. The operation-aware `Request()` checks `IsRateLimited(op_type)` and bypasses the limiter for disabled operation types. `RequestToken()` may request a smaller aligned grant than the original byte count, which supports direct IO alignment and burst limits. Implementations block when tokens are unavailable and update statistics when supported.

State and persistence behavior: The limiter holds runtime counters, pending queues, configured rate, burst size, and mode in the implementation. It is not persisted. Sharing one limiter across DB instances coordinates aggregate IO pressure.

Dependencies and integration points: It depends on `Env` for `IOPriority`, `Statistics`, and `Status`. `DBOptions::rate_limiter`, `ReadOptions::rate_limiter_priority`, `WriteOptions::rate_limiter_priority`, flush, compaction, WAL flush, and file readers/writers can use it. Generic limiter fairness distinguishes high- and low-priority requests, commonly flush versus compaction.

Risks and edge cases: Derived classes must not throw exceptions into RocksDB. New implementations should override newer overloads; the deprecated base `Request(bytes, pri)` asserts false. Callers must respect `bytes >= 0` and `bytes <= GetSingleBurstBytes()`. A mode mismatch can unintentionally leave reads or writes unthrottled. Large refill periods can cause bursty stalls; small periods add CPU overhead. `GetTotalPendingRequests()` is optional.

Test signals: Tests should verify mode filtering, dynamic rate changes, burst-size validation, fairness starvation avoidance, stats counters, alignment-aware `RequestToken()`, pending request reporting for the generic limiter, and behavior under concurrent high/low priority load.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/rate_limiter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/rocksdb_namespace.h -->
# sources/storage-engines/rocksdb/include/rocksdb/rocksdb_namespace.h

Purpose: This header centralizes the namespace macro used by RocksDB public headers. It allows builds to override `ROCKSDB_NAMESPACE` while defaulting to `rocksdb`.

Important APIs and types: It defines no C++ types. Preprocessor logic undefines `ROCKSDB_NAMESPACE` when it equals `42` for testing, then defines it to `rocksdb` if still unset.

Control flow: The only control flow is preprocessor conditionals. Public headers use `namespace ROCKSDB_NAMESPACE { ... }`, so this macro controls symbol namespace at compile time.

State and persistence behavior: There is no runtime state or persistence behavior.

Dependencies and integration points: It has no includes and is pulled into most public headers. It supports namespace customization for embedded builds, ABI isolation, or tests that deliberately exercise macro override handling.

Risks and edge cases: All translation units in a linked RocksDB build must agree on the namespace macro or symbols will not link. The special `42` testing case is surprising but documented by the comment. Macro collisions before including this file can alter the public ABI.

Test signals: Compile/link tests should build with the default namespace and with a custom namespace, and should verify the test sentinel path resets `42` to the default.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/rocksdb_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/secondary_cache.h -->
# sources/storage-engines/rocksdb/include/rocksdb/secondary_cache.h

Purpose: This header defines the modern secondary-cache interface for a lower cache tier such as non-volatile media or compressed block storage. It is used beneath the primary block cache and integrates with RocksDB's `Customizable` configuration system.

Important APIs and types: `SecondaryCacheResultHandle` represents a lookup result that may be pending, ready-miss/error, or ready-hit. It exposes `IsReady()`, `Wait()`, `Value()`, and `Size()`. `SecondaryCache` extends `Customizable`, declares `Type()`, `CreateFromString()`, and virtual methods `Insert()`, `InsertSaved()`, `Lookup()`, `SupportForceErase()`, `Erase()`, `WaitAll()`, optional `SetCapacity()`, `GetCapacity()`, `Deflate()`, and `Inflate()`. `SecondaryCacheWrapper` forwards all calls to a target shared cache and is intended for decorators. `kSliceCacheItemHelper` is an external helper for cache entries that can be copied as slices.

Control flow: A primary cache can suggest insertion through `Insert()`, passing the object and `CacheItemHelper` callbacks to serialize persistable bytes. `InsertSaved()` warms the cache from already saved bytes, optionally marked with compression type and source tier. `Lookup()` can block when `wait=true` or return a pending handle when `wait=false`; callers must wait before using `Value()`/`Size()`, and must take ownership of a hit value to avoid leaks. `advise_erase` lets the primary cache tell a supporting secondary cache to drop an entry after promoting it.

State and persistence behavior: Implementations own the secondary tier state and capacity. Entries may be stored on persistent media, compressed memory, or another cache mechanism. Admission control can decline an insert while returning OK. Capacity-changing APIs are optional; `Deflate()`/`Inflate()` are temporary RAM-capacity adjustments intended to be lighter than a full `SetCapacity()`.

Dependencies and integration points: It depends on `advanced_cache.h`, `customizable.h`, `options.h`, `Slice`, `Statistics`, and `Status`. It integrates with block cache entries through `Cache::ObjectPtr`, `CacheItemHelper`, and `CreateContext`; with `DBOptions::lowest_used_cache_tier`; and with configuration parsing via `CreateFromString()`.

Risks and edge cases: The handle state comment has a typo saying ready-hit has `IsReady() == false`; the intended behavior is ready plus non-null value. Pending handles must not be destroyed. Some implementations might never report ready through polling without `Wait()` or `WaitAll()`. `Value()` transfers/returns ownership semantics through `ObjectPtr`; failing to consume a hit leaks memory. Exceptions must not propagate. `advise_erase` is only a hint and requires `SupportForceErase()` for force behavior.

Test signals: Tests should cover synchronous and asynchronous lookup, `WaitAll()`, hit/miss/error handles, insert admission, saved-data warming with compression metadata, erase/advised erase, wrapper forwarding, capacity changes or NotSupported fallback, stats updates, and leak checks when handles produce values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/secondary_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/slice.h -->
# sources/storage-engines/rocksdb/include/rocksdb/slice.h

Purpose: This header defines `Slice`, RocksDB's core non-owning byte-string view, plus optional and pinnable variants. It is foundational across all public APIs for keys, values, ranges, cache keys, and encoded table data.

Important APIs and types: `Slice` stores `const char* data_` and `size_t size_`, with constructors from pointer/length, `std::string`, `std::string_view`, C string, and `SliceParts` plus scratch buffer. It exposes `data()`, `size()`, `empty()`, indexing, `clear()`, prefix/suffix removal, `ToString()`, `ToStringView()`, `DecodeHex()`, `compare()`, `starts_with()`, `ends_with()`, and `difference_offset()`. `OptSlice` is a compact optional slice using `SIZE_MAX` as the no-value sentinel and exposes `has_value()`, bool conversion, dereference, `AsPtr()`, and `CopyFromPtr()`. `PinnableSlice` inherits `Slice` and `Cleanable`, can either copy into self storage or pin external storage with cleanup callbacks, and supports move-only ownership, `PinSlice()`, `PinSelf()`, prefix/suffix removal, `Reset()`, `GetSelf()`, and `IsPinned()`. `SliceParts` represents virtual concatenation of an array of slices. Equality/inequality operators and inline compare helpers are defined.

Control flow: `Slice` methods operate directly on the pointer and size. `remove_prefix()` advances `data_`; `remove_suffix()` shrinks size. `compare()` uses `memcmp()` over the common prefix then length ordering. `difference_offset()` scans to the first differing byte. `OptSlice` differentiates no-value from empty slice, including the caution that `OptSlice{nullptr}` means absent while `Slice{nullptr}` means empty. `PinnableSlice::PinSlice()` records external data and cleanup ownership; `PinSelf()` copies or reuses owned string storage; `Reset()` runs cleanups and clears pinned state.

State and persistence behavior: `Slice` does not own memory and persists nothing. Correctness depends on the referenced storage outliving the slice. `PinnableSlice` can own copied data in `self_space_` or delegate cleanup for pinned external resources, making it useful for zero-copy reads where buffers must be released when the result object resets.

Dependencies and integration points: It depends on `cleanable.h` and standard string/memory utilities. Virtually every RocksDB API uses `Slice` for keys, values, timestamps, range bounds, cache keys, table entries, and file-writer/reader operations. `PinnableSlice` integrates with block cache and table readers that can return pinned values.

Risks and edge cases: Dangling slices are the dominant risk. `Slice` is intentionally copyable, and public `data_`/`size_` exist for RocksJNI compatibility, so callers can mutate view metadata directly. `compare()` asserts both data pointers are non-null, so default empty slices use `""` rather than null. `OptSlice` copies the pointed-to slice metadata, not future changes to a pointed object. `PinnableSlice` is not copyable, requires reset/destruction to release cleanups, and its prefix/suffix removal changes owned storage when not pinned but only adjusts metadata when pinned.

Test signals: Tests should cover string/view/C-string/null construction, lexicographic comparison, prefix/suffix removal, hex encode/decode, optional empty versus absent semantics, `SliceParts` concatenation constructor, `PinnableSlice` cleanup invocation, pin versus self-copy behavior, move construction/assignment, and zero-copy read lifetime interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/slice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/slice_transform.h -->
# sources/storage-engines/rocksdb/include/rocksdb/slice_transform.h

Purpose: This header defines the pluggable prefix/key transformation interface used most commonly for prefix Bloom filters and prefix seek optimization. It lets a column family map keys to comparable prefixes under documented safety constraints.

Important APIs and types: `SliceTransform` extends `Customizable`. It declares `Name()`, static `Type()`, static `CreateFromString()`, `AsString()`, pure virtual `Transform(const Slice&)`, pure virtual `InDomain(const Slice&)`, optional `FullLengthEnabled(size_t*)`, and optional `SameResultWhenAppended(const Slice&)`. Factories `NewFixedPrefixTransform(size_t)`, `NewCappedPrefixTransform(size_t)`, and `NewNoopTransform()` create common extractors.

Control flow: RocksDB checks `InDomain()` before adding/querying prefix Bloom entries. If true, it calls `Transform()` to derive the prefix. `FullLengthEnabled()` gives auto-prefix-mode code a maximum prefix length for recognizing upper-bound successor cases. `SameResultWhenAppended()` is mostly a user-facing safety check for seeking to a raw prefix without total-order seek.

State and persistence behavior: Transform objects are runtime configuration. Their names and semantics matter across DB reopen because existing SST filter/index data was built using prior extractor behavior. The header itself persists nothing, but changing extractor semantics can make persisted filters unsafe or ineffective.

Dependencies and integration points: It depends on `Customizable`, `rocksdb_namespace.h`, and `Slice`. `ColumnFamilyOptions::prefix_extractor`, block-based table filters, memtable prefix bloom, iterators, Gets, MultiGets, and option-string parsing use this interface.

Risks and edge cases: Implementations must not throw. Prefix extractors must satisfy the comparator-contiguity requirements documented in `options.h`; otherwise range scans with prefix filters can hide existing keys. `FullLengthEnabled()` and `auto_prefix_mode` have documented limitations around short keys. Returning true from `SameResultWhenAppended()` when not guaranteed can lead users to issue unsafe prefix seeks.

Test signals: Tests should verify transform/domain behavior for fixed, capped, and noop extractors; option-string creation and `AsString()` output; prefix Bloom correctness for in-domain/out-of-domain keys; total-order versus prefix seek equivalence; and unsafe extractor cases being rejected or documented by integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/slice_transform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/snapshot.h -->
# sources/storage-engines/rocksdb/include/rocksdb/snapshot.h

Purpose: This header declares RocksDB's immutable snapshot handle and a small RAII wrapper for acquiring/releasing snapshots. Snapshots provide stable point-in-time read views for `ReadOptions::snapshot`.

Important APIs and types: `Snapshot` is an abstract class with `GetSequenceNumber()`, `GetUnixTime()`, and `GetTimestamp()`. Its destructor is protected so users release snapshots through DB APIs. `ManagedSnapshot` constructs by acquiring `DB::GetSnapshot()` or by taking ownership of an existing snapshot pointer, releases it in the destructor, and exposes `snapshot()`.

Control flow: Applications call `DB::GetSnapshot()` and pass the pointer into read options. `ManagedSnapshot` wraps that lifecycle: constructor stores the DB and snapshot, destructor calls release, and `snapshot()` returns the managed pointer.

State and persistence behavior: A snapshot pins an in-memory version/sequence view and can keep old memtable/SST resources alive until release. It is immutable and thread-safe to read. Snapshot handles are not persisted across process restarts; sequence number and timestamps reflect DB state at creation.

Dependencies and integration points: It depends on `rocksdb/types.h` for `SequenceNumber` and forward-declares `DB`. Read paths, iterators, transactions, compaction garbage collection, and resource cleanup all integrate with snapshot lifetime.

Risks and edge cases: Failing to release snapshots can retain obsolete files and block cleanup/compaction. A snapshot must be released to the same DB that created it. `ReadOptions::snapshot` must not outlive the snapshot. `ManagedSnapshot` is simple ownership; users should avoid double-release when passing an already-owned snapshot.

Test signals: Tests should cover sequence/timestamp visibility, RAII release, multi-threaded reads through one snapshot, resource pinning until release, and invalid/double ownership misuse in debug or sanitizer builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_dump_tool.h -->
# sources/storage-engines/rocksdb/include/rocksdb/sst_dump_tool.h

Purpose: This header declares the object-oriented entry point for the SST dump tool. The tool inspects or verifies SST files using RocksDB options.

Important APIs and types: `class SSTDumpTool` exposes `int Run(int argc, char const* const* argv, Options options = Options());`.

Control flow: Callers instantiate `SSTDumpTool` and pass command-line arguments plus optional `Options`. The implementation parses arguments and operates on SST files. The default argument constructs default RocksDB options when the caller does not supply custom comparator/table settings.

State and persistence behavior: The header defines no persistent state. The tool can read SST files and may produce output or verification statuses depending on implementation arguments; it should not be assumed to mutate DB state from this declaration alone.

Dependencies and integration points: It includes `rocksdb/options.h`, which lets the tool share comparator, Env, table factory, and checksum behavior with the DB or caller. It integrates with command-line binaries, tests, and support tooling.

Risks and edge cases: Running the dump tool with options that do not match the SST's comparator/table format can misinterpret keys or fail. The `Options` default construction pulls in a heavy option surface for a small tool declaration.

Test signals: Tests should invoke `Run()` against valid, corrupt, and option-mismatched SST files, validate exit codes, and verify checksum/table-property reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_dump_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_file_manager.h -->
# sources/storage-engines/rocksdb/include/rocksdb/sst_file_manager.h

Purpose: This header defines the public `SstFileManager` interface and factories. The manager tracks SST and blob file sizes, enforces optional space caps, and rate-limits deletion of SST/blob/WAL files through the delete scheduler used by DB instances.

Important APIs and types: `SstFileManager` is a thread-safe public interface whose concrete derived classes are RocksDB-internal. It exposes `SetMaxAllowedSpaceUsage()`, `SetCompactionBufferSize()`, `IsMaxAllowedSpaceReached()`, `IsMaxAllowedSpaceReachedIncludingCompactions()`, `GetTotalSize()`, `GetTrackedFiles()`, `GetDeleteRateBytesPerSecond()`, `SetDeleteRateBytesPerSecond()`, `GetMaxTrashDBRatio()`, `SetMaxTrashDBRatio()`, `GetTotalTrashSize()`, and `SetStatisticsPtr()`. `NewSstFileManager()` has a modern overload taking `Env*` plus `std::shared_ptr<FileSystem>` and a legacy `Env*` overload.

Control flow: DB instances register and unregister tracked SST/blob files through the implementation. Callers can update the max allowed space; when tracked bytes exceed it, RocksDB writes fail through background error behavior. Delete scheduling throttles file deletion based on configured bytes per second and can chunk large file truncation. Trash ratio controls whether new files bypass trash and delete immediately.

State and persistence behavior: Runtime state includes tracked filenames/sizes, total tracked size, trash size, delete-rate settings, max-space settings, compaction buffer size, and optional statistics pointer. It does not track WAL file sizes for space accounting, but its delete scheduler affects WAL deletion rate. It can be shared by multiple DBs, coordinating space and deletion behavior across them.

Dependencies and integration points: It depends on `file_system.h`, `statistics.h`, `status.h`, `Env`, and `Logger`. `DBOptions::sst_file_manager` uses it; compaction, flush, obsolete-file cleanup, delete scheduling, and DB write admission integrate with it.

Risks and edge cases: The manager only tracks SST/blob files in the first DB path according to `DBOptions` comments, which can surprise multi-path users. Setting max allowed space too low can stop writes. Deletion throttling can build trash backlog; high trash ratio triggers immediate deletion. Chunked deletion can leave partial trash files that should not be manually recovered without checking. Deprecated trash-dir arguments mostly have no effect but still influence cleanup of provided directories.

Test signals: Tests should verify tracked-file maps and total size, max-space admission failures, inclusion of ongoing compaction estimates, deletion-rate throttling and runtime changes, trash-size accounting, shared manager behavior across DBs, statistics updates, and both factory overloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_file_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_file_reader.h -->
# sources/storage-engines/rocksdb/include/rocksdb/sst_file_reader.h

Purpose: This header declares `SstFileReader`, a public utility for reading and verifying standalone SST files generated by a DB or `SstFileWriter`.

Important APIs and types: `SstFileReader` constructs from `Options`, owns an opaque `Rep`, and exposes `Open(file_path)`, `NewIterator(ReadOptions)`, `MultiGet()` overloads returning `std::string` or `PinnableSlice` values, `Get()` overloads, `NewTableIterator()`, `ParseTableIteratorKey()`, `GetTableProperties()`, `VerifyChecksum(ReadOptions)`, default `VerifyChecksum()`, and `VerifyNumEntries(ReadOptions)`.

Control flow: A caller creates the reader with options matching the SST, calls `Open()`, then uses DB-style logical reads or raw table iteration. `NewIterator()` returns a DB iterator that hides logically invisible entries such as deletes. `NewTableIterator()` returns a raw table iterator over all point data entries, including deletes, for tooling. `ParseTableIteratorKey()` decodes raw internal keys into `ParsedEntryInfo`. Verification methods scan table data or properties to detect checksum corruption or entry-count mismatches.

State and persistence behavior: The reader is read-only and stores open-file/table-reader state in `rep_`. It does not mutate SST files. Read options can control checksum verification, cache filling, snapshots for logical visibility, and IO behavior where supported.

Dependencies and integration points: It depends on iterator, options, slice, table properties, and types. It integrates with SST dump/repair tools, tests, external ingestion validation, offline inspection, and block/table reader implementations selected by `Options::table_factory`.

Risks and edge cases: Options must match the SST's comparator and table format. A logical DB iterator can hide tombstones and older versions, while raw table iteration exposes them; tooling must choose the correct API. `ParseTableIteratorKey()` returns slices pointing into the raw key argument, so lifetimes are short. Cache/readahead options may be ignored for raw iteration. Corruption verification coverage depends on table format.

Test signals: Tests should open writer-generated and DB-generated SSTs, compare logical versus raw iteration, exercise string and pinnable `Get`/`MultiGet`, parse raw keys, validate table properties, detect checksum corruption, detect entry-count mismatch, and fail cleanly on wrong options or corrupt files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_file_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_file_writer.h -->
# sources/storage-engines/rocksdb/include/rocksdb/sst_file_writer.h

Purpose: This header declares the public offline SST writer used to create external SST files for later ingestion into RocksDB. All generated keys have sequence number zero unless timestamp APIs encode user-defined timestamps.

Important APIs and types: `ExternalSstFileInfo` records file path, smallest/largest point keys, smallest/largest range-deletion keys, checksum and checksum function name, sequence number, file size, entry counts, range-deletion count, and file version. `SstFileWriter` is a non-thread-safe class with constructors from `EnvOptions`, `Options`, optional comparator/column family, page-cache invalidation flag, and IO priority. It exposes `Open(file_path, Temperature)`, `Put()` overloads with and without timestamp, `PutEntity()` for wide columns, `Merge()`, `Delete()` overloads, `DeleteRange()` overloads, `Finish(ExternalSstFileInfo*)`, `FileSize()`, and static `CreatedBySstFileWriter()`.

Control flow: Users construct a writer with DB-compatible options, call `Open()`, add sorted point entries through `Put`/`Merge`/`Delete`, optionally add range tombstones in any order, and call `Finish()` to close and optionally fill metadata. Point keys must be strictly after previous point keys according to the comparator. Timestamp overloads require timestamp size matching the comparator and respect `persist_user_defined_timestamps`; when persistence is disabled, only the minimum timestamp is accepted and not stored.

State and persistence behavior: The writer creates a real SST file at the target path, with optional filesystem temperature and page-cache invalidation while writing. It owns opaque writer state in `rep_`, tracks file size, writes table properties including creation identity, and returns metadata useful for ingestion. Range tombstones in the same file do not delete point keys in that same file.

Dependencies and integration points: It depends on advanced options, Env, options, table properties, types, and wide columns. It integrates with external file ingestion (`IngestExternalFileOptions`), offline sorting/bulk-load pipelines, tests, file checksums, compression/table factories, column-family metadata, and `SstFileReader`.

Risks and edge cases: The class is not thread-safe. Incorrect key ordering causes errors. Comparator/table options must match the target DB/CF or ingestion/read behavior is unsafe. Timestamp-aware comparators reject non-timestamp point APIs. Range tombstone ordering differs from point ordering and does not affect same-file point entries, which can surprise callers. Failing to call `Finish()` leaves an incomplete file. Page-cache invalidation and IO priority depend on Env/FileSystem support.

Test signals: Tests should cover sorted-key enforcement, timestamp persistence rules, wide-column writes, merge/delete/range-delete entries, file-info population, checksum metadata, `CreatedBySstFileWriter()`, ingestion into compatible and incompatible CFs, page-cache invalidation hooks, file size reporting, and incomplete/open/finish lifecycle errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_file_writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_partitioner.h -->
# sources/storage-engines/rocksdb/include/rocksdb/sst_partitioner.h

Purpose: This header defines the pluggable SST partitioner interface used by compaction to split output SST files on application-significant key boundaries, reducing future write amplification when files are promoted or compacted.

Important APIs and types: `PartitionerResult` has `kNotRequired` and `kRequired`. `PartitionerRequest` carries pointers to previous and current user keys plus current output file size. `SstPartitioner` declares `Name()`, `ShouldPartition()`, `CanDoTrivialMove()`, and nested `Context` containing full/manual compaction flags, output level, and smallest/largest compaction keys. `SstPartitionerFactory` extends `Customizable`, provides `Type()`, `CreateFromString()`, `CreatePartitioner(context)`, and `Name()`. `SstPartitionerFixedPrefix` splits on fixed-prefix changes, and `SstPartitionerFixedPrefixFactory` creates those partitioners. `NewSstPartitionerFixedPrefixFactory()` is the public factory helper.

Control flow: For each key during compaction, RocksDB builds a `PartitionerRequest` and asks `ShouldPartition()`. Returning `kRequired` finishes the current SST with the previous key and starts a new SST with the current key. When compaction could trivially move an existing file, RocksDB calls `CanDoTrivialMove()` with the file's smallest/largest user keys; the partitioner can reject trivial movement if it would violate partition boundaries. The factory creates a fresh partitioner per compaction context.

State and persistence behavior: The partitioner affects persisted SST file boundaries and therefore future compaction overlap/write amplification. It does not persist its own state, but the selected factory and partitioning semantics must remain compatible with the workload and key format. Fixed-prefix partitioning stores only `len_` in the factory/partitioner object.

Dependencies and integration points: It depends on `Customizable`, `rocksdb_namespace.h`, and `Slice`. `ColumnFamilyOptions::sst_partitioner_factory` wires it into compaction. Option-string parsing can instantiate factories through `CreateFromString()`.

Risks and edge cases: Partitioners must not throw exceptions. `PartitionerRequest` holds pointers to caller-owned slices, so implementations must not retain them beyond the call. A bad partitioner can generate too many small files, harm compaction, or reject beneficial trivial moves. Fixed-prefix logic must handle keys shorter than the configured prefix. Since the feature is experimental in `options.h`, compatibility can change.

Test signals: Tests should cover split decisions on prefix changes, no split within a prefix, short-key behavior, current-output-file-size awareness in custom partitioners, `CanDoTrivialMove()` acceptance/rejection, factory creation from string, per-compaction context propagation, and resulting SST boundary/file-count effects after compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/sst_partitioner.h -->
