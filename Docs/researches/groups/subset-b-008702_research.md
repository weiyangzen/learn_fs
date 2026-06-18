# Research: subset-b-008702

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression.cc -->
# sources/storage-engines/rocksdb/util/compression.cc

Purpose: implements RocksDB's built-in compression manager version 2, including string conversion helpers, block compression and decompression for compiled-in codecs, ZSTD streaming WAL compression support, dictionary training/finalization, optimized decompressor selection, object-registry creation, and the legacy forced-compression helper.

Important APIs and functions: `CompressionTypeToString()` and `CompressionTypeFromString()` map enum values to the newer built-in strings, including custom and reserved byte ranges. `CompressionOptionsToString()` serializes file-affecting compression options and intentionally omits `parallel_threads`. `StreamingCompress::Create()` and `StreamingUncompress::Create()` currently instantiate only ZSTD stream implementations. `ZSTDStreamingCompress::Compress()` and `ZSTDStreamingUncompress::Uncompress()` keep ZSTD input-buffer state across repeated calls, return `-1` after reset on codec error, and return remaining input or remaining frame work for the caller loop. `DecompressorDict::Populate()` clones a dictionary-aware decompressor, installs a `FailureDecompressor` for empty or rejected dictionaries, and accounts approximate cache memory. `ZSTD_TrainDictionary()` and `ZSTD_FinalizeDictionary()` wrap ZDICT training/finalization where available.

Control flow: built-in block compression is organized around local `Compressor` subclasses. `StartCompressBlockV2()` writes the standard varint32 uncompressed-size prefix for version-2 block formats and rejects inputs over 4 GiB or output buffers too small to hold the prefix. Snappy and XPRESS use codec-native framing/length behavior and do not use this prefix. Zlib, BZip2, LZ4, LZ4HC, and ZSTD write after the prefix, update `compressed_output_size`, and set `out_compression_type` to the actual stored type only when compression is accepted. A declined attempt normally returns OK with `kNoCompression` and either size 0 for bypass or size 1 for attempted-but-rejected compression, preserving statistics semantics in table building.

Codec-specific behavior: zlib uses `deflateInit2()` with configured window bits, level, strategy, and optional dictionary. BZip2 ignores dictionaries for compatibility. LZ4 fast and LZ4HC share a wire format but are selected by level: default keeps the configured type's historical behavior, non-default `level <= 0` uses LZ4 fast acceleration, and `level >= 1` uses LZ4HC with clamping. ZSTD sanitizes level 0 to `-1`, uses working areas for `ZSTD_CCtx`, applies checksums when requested, and prefers digested `ZSTD_CDict` when present. Non-destination-size ZSTD compression errors are returned as corruption rather than silent fallback.

Decompression flow: `BuiltinDecompressorV2::ExtractUncompressedSize()` has codec exceptions for Snappy and XPRESS, then delegates to the base varint extractor. Decompression dispatch validates exact output sizes for all codecs. ZSTD decompression can use a caller-provided `UncompressionContext` working area, otherwise it obtains a temporary context from `CompressionContextCache`; dictionary variants can use raw dictionaries or `ZSTD_DDict` when static-linking APIs are available. `BuiltinDecompressorV2WithDict` stores the serialized dictionary even for codecs that historically ignore it, keeping old table semantics.

State and persistence: the file defines the process-wide `kBuiltinCompressionManagerV2` singleton and returns aliasing `shared_ptr`s to embedded decompressor instances so their lifetime is tied to the manager. Table persistence is affected by the `CompatibilityName()` `"BuiltinV2"`, per-block `CompressionType`, serialized dictionaries, and the compression name/options written elsewhere by table builders. WAL persistence uses the streaming factory via log writer/reader, but this file owns the stream implementation.

Dependencies and integration points: depends on optional codec libraries behind `SNAPPY`, `ZLIB`, `BZIP2`, `LZ4`, `XPRESS`, and `ZSTD` macros; on `CompressionManager`, `Compressor`, and `Decompressor` interfaces from `rocksdb/advanced_compression.h`; on `ObjectLibrary` registration for config parsing; and on table/block code through cache roles, dictionary blocks, block type metadata, and sync points. `GetBuiltinV2CompressionManager()` is the main entry used by options/table code and tests. Blob code uses `LegacyForceBuiltinCompression()`.

Risks: many error paths intentionally degrade compression to `kNoCompression`, so callers must distinguish bypass/rejection from corruption using the size/type conventions. Dictionary ownership is subtle: dictionary decompressors may reference bytes owned by `DecompressorDict`, so lifetimes must stay coupled. `CompressionDict::operator=` replaces `zstd_cdict_` without freeing an existing one, which is safe only if assignment is not used on an object already owning a CDict. ZSTD working-area reset and dictionary reference ordering are important because `ZSTD_CCtx_refCDict()` / `loadDictionary()` attach state to reusable contexts. LZ4 level mapping changes observable `out_compression_type`, so table properties record configured type separately in tests.

Test signals: `compression_test.cc` covers dictionary ratio/locality, dynamic per-level compression, injected compression/decompression failures, wrapper managers, custom compression schema compatibility, predefined dictionary correctness, parallel-thread recommendations, manager thread overrides, unified LZ4/LZ4HC level behavior, ZSTD level-zero mapping, and configured-type table properties. WAL streaming is tested outside this file in log tests that call `StreamingCompress::Create()` and `CompressionTypeRecord`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression.h -->
# sources/storage-engines/rocksdb/util/compression.h

Purpose: declares RocksDB's compression utility surface: build-time codec support probes, dictionary holder types, reusable compression/decompression working areas, built-in compression string helpers, WAL compression records, streaming compression interfaces, and the legacy forced-compression helper.

Important APIs and types: `SanitizeZSTDCompressionLevel()` maps the default sentinel to `ZSTD_CLEVEL_DEFAULT` and level 0 to `-1`. `ZSTDUncompressCachedData` wraps a `ZSTD_DCtx*` plus a cache index, distinguishing owned one-shot contexts (`cache_idx_ == -1`) from borrowed per-core cached contexts. `FailureDecompressor` is a `Decompressor` that consistently returns a stored non-OK status. `DecompressorDict` owns or references raw dictionary bytes and the dictionary-specialized decompressor that must be used with those bytes. `CompressionDict` owns raw dictionary bytes and, for ZSTD, an optional digested `ZSTD_CDict`.

Control flow and lifecycle: `CompressionContext` creates and owns a native ZSTD compression context when type is `kZSTD`, setting level and optional checksum at construction and freeing it at destruction. `UncompressionContext` borrows a cached ZSTD decompression context from `CompressionContextCache` on construction and returns it when destroyed if the context came from cache. Support-probe functions are inline compile-time checks, and `CompressionTypeSupported()`, `DictCompressionTypeSupported()`, and `StreamingCompressionTypeSupported()` centralize option validation by codec.

Streaming and WAL behavior: `CompressionTypeRecord` encodes the current WAL compression type as fixed32 and decodes only streaming-supported types, rejecting unsupported values as corruption. `StreamingCompress` and `StreamingUncompress` define stateful buffer-by-buffer interfaces where callers repeat calls until no remaining work is reported, and `ZSTDStreamingCompress` / `ZSTDStreamingUncompress` provide the concrete ZSTD implementations when compiled in.

State and persistence: dictionary holders are move-only to avoid duplicate ownership of native dictionaries and cached contexts. `DecompressorDict` exposes `ContentSlice()`, `kCacheEntryRole`, `kBlockType`, and `ApproximateMemoryUsage()` so compression dictionary blocks can be stored in the block cache with memory accounting. `CompressionTypeRecord` affects WAL replay state rather than table state.

Dependencies and integration points: includes memory allocator helpers, table block types, `aligned_buffer`, coding utilities, compression context cache, and public RocksDB options/advanced compression interfaces. It conditionally includes ZSTD, ZDICT, and XPRESS headers and defines feature macros such as `ROCKSDB_ZSTD_DDICT` and `ROCKSDB_ZDICT_FINALIZE`. It is used by table builders/readers, WAL log reader/writer, blob code, compression tests, and platform environment initialization.

Risks: the header has heavy conditional compilation, so unsupported-codec builds must continue compiling all inline stubs. Borrowed ZSTD contexts rely on `UncompressionContext` destruction to return cache entries. `DecompressorDict::own_bytes()` documents a caller-lifetime hazard when constructed from a `Slice` without an owning allocation. ZSTD static-linking features influence whether digested dictionary decompression is available.

Test signals: direct behavior is covered through `compression.cc` tests for level sanitization, dictionary handling, manager selection, and streaming WAL tests elsewhere. The decode path in `CompressionTypeRecord` is exercised by WAL/log tests that validate unsupported compression-type records.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression_context_cache.cc -->
# sources/storage-engines/rocksdb/util/compression_context_cache.cc

Purpose: implements a singleton per-core cache of reusable ZSTD decompression contexts to reduce random-read latency and allocation/initialization overhead.

Important APIs and types: `compression_cache::ZSTDCachedData` contains one `ZSTDUncompressCachedData` and an atomic sentinel pointer. `CompressionContextCache::Rep` owns a `CoreLocalArray<ZSTDCachedData>` and exposes indexed borrow/return methods. Public methods forward through `rep_`: `GetCachedZSTDUncompressData()` and `ReturnCachedZSTDUncompressData()`.

Control flow: `Rep::GetZSTDUncompressData()` asks `CoreLocalArray` for the current core's element and index. `ZSTDCachedData::GetUncompressData()` tries to atomically swap the sentinel from the cached-data address to `nullptr`; success means the caller borrowed the per-core context and receives the cache index, while failure means another thread is using it and a one-time owned context is created instead. `ReturnZSTDUncompressData()` looks up the original core index and swaps the sentinel back to the cached-data address.

State and persistence: all state is process-local and non-persistent. The singleton is function-local static storage. Cached native contexts can live for process lifetime; one-shot contexts are freed by `ZSTDUncompressCachedData` destructors. `CompressionContextCache::InitSingleton()` eagerly constructs the singleton for environments that want initialization before worker use.

Dependencies and integration points: depends on `util/compression.h` for `ZSTDUncompressCachedData` and `util/core_local.h` for core sharding. Environment startup calls `CompressionContextCache::InitSingleton()` in POSIX and Windows default environments. `UncompressionContext` in `compression.h` is the main client and returns cached entries during destruction.

Risks: correctness depends on callers returning only borrowed entries and exactly once; `ReturnUncompressData()` asserts if the sentinel was not acquired. The cached core index can become stale if a thread migrates, but returning to the original index is intended because the borrowed object records that index. The padding expression is designed to make the structure cache-line sized, but changes to member sizes or `CACHE_LINE_SIZE` can affect compile-time layout.

Test signals: behavior is indirectly tested by ZSTD decompression paths in DB compression tests and WAL/table read tests. There is no direct stress test in this file for concurrent borrow fallback or assert paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression_context_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression_context_cache.h -->
# sources/storage-engines/rocksdb/util/compression_context_cache.h

Purpose: declares the process singleton used to cache compression/uncompression contexts, currently only ZSTD decompression contexts, on a per-core basis.

Important APIs and types: `CompressionContextCache::Instance()` returns the singleton, `InitSingleton()` forces construction, `GetCachedZSTDUncompressData()` borrows a cached or one-shot ZSTD context, and `ReturnCachedZSTDUncompressData(int64_t idx)` returns a previously borrowed cached context. The private `Rep` hides the `CoreLocalArray` implementation from users.

Control flow and state: users do not manage native codec pointers directly; they receive and return `ZSTDUncompressCachedData` through higher-level wrappers. The cache uses an index-based return protocol because the borrowing thread may not still be on the same core when it releases the context.

Dependencies and integration points: forward-declares `ZSTDUncompressCachedData` and includes only namespace definitions in the header, keeping codec and core-local details in the `.cc`. `UncompressionContext` in `compression.h` is the key integration point.

Risks: the public return method trusts the provided index and asserts on invalid values in the implementation. Because the cache is a singleton, teardown ordering can matter if other static objects try to return contexts after destruction; normal use scopes contexts inside operations.

Test signals: tested indirectly through ZSTD decompression and environment initialization; no standalone unit test validates singleton lifecycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression_context_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression_test.cc -->
# sources/storage-engines/rocksdb/util/compression_test.cc

Purpose: provides DB-level and compressor-manager tests for RocksDB compression behavior, including dictionary generation, per-level compression choices, failure handling, custom compression managers, auto-skip/cost-aware wrappers, predefined dictionaries, parallel compression controls, and recent LZ4/ZSTD level semantics.

Important fixtures and helpers: `DBCompressionTest` derives from `DBTestBase`. `PresetCompressionDictTest` parameterizes supported dictionary compression types and bottommost-vs-normal options. `CompressionFailuresTest` injects compression and decompression failures across compression types, dictionary sizes, and parallel thread counts. `DBCompressionTestMaybeParallel` parameterizes compression manager wrapper tests by thread count, dictionary use, and separated key/value data blocks. `ValidateRocksBlock()` parses data or index block layouts to prove specialized compressors receive the expected block schema.

Major control-flow coverage: dictionary tests write flush and compaction workloads, observe block-cache dictionary insertion tickers, and verify readback. Dynamic-level tests use compactions, table metadata, and sync-point callbacks to assert the selected output compression at changing base levels. Failure tests use sync points to tamper with compression result type, decompression return status, decompressed bytes, or parallel finish status, then verify either safe uncompressed fallback or corruption propagation. Manager-wrapper tests intercept compression calls, simulate bypass/rejection by block contents, verify statistics, and check working-area propagation.

Custom manager and schema behavior: `CompressionManagerCustomCompression` defines a local manager supporting built-in and custom compression types, then validates format-version guardrails, compatibility names, table property compression names such as `Foo;8A;`, reopening with/without compatible managers, dynamic option changes, and object registry fallback for manager lookup. It also checks that managers claiming `"BuiltinV2"` cannot use custom compression types.

Dictionary and adaptive-wrapper behavior: `PreDefinedDictionaryCompression` creates a custom manager that supplies a predefined ZSTD dictionary, verifies dictionary cache insertion and successful reads, then reopens with a broken decompressor that stores but ignores the dictionary and expects corruption. `AutoSkipCompressionManager` and `CostAwareCompressorManager` use flush block policies and sync points to verify prediction/exploration decisions and CPU/IO cost prediction plumbing.

State and persistence signals: tests repeatedly close/reopen databases, inspect SST table properties, block-cache dictionary statistics, compression names, compression options, and compaction output events. The tests check both on-disk compatibility and runtime option changes. Random data and fixed seeds are used to make compression ratios predictable enough for assertions.

Dependencies and integration points: includes DB test utilities, block builders, data block footers, object registry, auto-tune and simple mixed compressor utilities, random/test helpers, and stack trace setup. Tests depend heavily on `SyncPoint` hooks from table building, compaction, and decompression code.

Risks and notable gaps: some branches skip when optional libraries are not compiled in, so build-matrix coverage is required. Dictionary-ratio assertions can be sensitive to codec behavior, although comments account for ZSTD trained/finalized variability. There appears to be a duplicated `else if (i == kWithZSTDTrainedDict)` in `PresetCompressionDict`, making the finalized-dictionary assertion branch unreachable as written. The context-cache implementation is only indirectly stressed.

Specific test signals: `GetRecommendedParallelThreads` validates fast-compressor overrides and ZSTD level-0 backdoor behavior; `CompressionManagerOverridesParallelThreads` proves manager-modified options activate parallel compression; `UnifiedLZ4LZ4HCLevels` confirms level-based algorithm selection, clamping, output identity, and round trips; `ZSTDLevelZeroMapsToMinusOne` verifies level 0 output equals level -1 and differs from level 3; `ConfiguredCompressionTypeRecordedInProperties` checks `_type=<decimal>` persistence in table properties.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compression_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.cc -->
# sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.cc

Purpose: implements RocksDB's internal `ConcurrentTaskLimiter` used to throttle outstanding tasks such as compaction work while allowing scoped token ownership.

Important APIs and functions: the constructor stores the limiter name, max outstanding task limit, and zero outstanding count. `SetMaxOutstandingTask()` updates the limit, `ResetMaxOutstandingTask()` sets it to `-1` for unlimited, `GetOutstandingTask()` returns the current count, `GetToken(bool force)` tries to reserve a task slot, and `NewConcurrentTaskLimiter()` is the public factory returning the interface pointer. `TaskLimiterToken::~TaskLimiterToken()` releases one outstanding slot.

Control flow: `GetToken()` loads the limit and current task count with relaxed ordering, then loops while forced, unlimited, or below limit. It uses `compare_exchange_weak(tasks, tasks + 1)` so competing threads update `tasks` on failure and retry against the latest value. If the limit is reached and `force` is false, it returns `nullptr`. A successful reservation returns a unique token whose destructor decrements the count.

State and persistence: all state is in atomics on the limiter object and is not persisted. The implementation asserts at destruction that no outstanding task remains, making token lifetime part of object lifetime correctness.

Dependencies and integration points: implements `include/rocksdb/concurrent_task_limiter.h` and is constructed by column-family options, compaction scheduling code, and JNI wrappers. The `force` flag supports bypass paths that must proceed even beyond the configured throttle.

Risks: relaxed atomics are adequate for a counter but provide no ordering for work protected by the limiter. The decrement in `TaskLimiterToken` assumes the limiter outlives all tokens; premature limiter destruction is caught only by debug assertions or undefined behavior. The CAS loop reloads `limit` only once per call, so concurrent limit changes might not affect an in-progress token request until the next call.

Test signals: integration references include DB compaction tests and Java `ConcurrentTaskLimiterTest`. This implementation file has no local unit tests in the subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.h -->
# sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.h

Purpose: declares the concrete internal implementation of RocksDB's `ConcurrentTaskLimiter` and the RAII token that releases task reservations.

Important APIs and types: `ConcurrentTaskLimiterImpl` overrides `GetName()`, `SetMaxOutstandingTask()`, `ResetMaxOutstandingTask()`, and `GetOutstandingTask()`, and exposes `GetToken(bool force)` for callers that need to reserve capacity. `TaskLimiterToken` is move-disabled/copy-disabled and holds a raw pointer back to its limiter for release on destruction.

State and lifecycle: the limiter stores `name_`, `max_outstanding_tasks_`, and `outstanding_tasks_`. Tokens increment the outstanding count when created by `GetToken()` and decrement it when destroyed. Copying the limiter is disabled to keep atomics and token back-pointers stable.

Dependencies and integration points: includes public `rocksdb/concurrent_task_limiter.h` and `rocksdb/env.h`. The public factory is declared in the interface header and implemented in the `.cc`, while Java bindings allocate it through JNI.

Risks: the raw pointer in `TaskLimiterToken` makes lifetime ordering explicit but unenforced; users must not destroy the limiter before all tokens. The header's `virtual std::unique_ptr<TaskLimiterToken> GetToken(bool force)` is not part of the public base interface, so code using it must know the concrete type.

Test signals: behavior is expected to be exercised by compaction limiter tests and Java option tests rather than by this header directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/concurrent_task_limiter_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/core_local.h -->
# sources/storage-engines/rocksdb/util/core_local.h

Purpose: provides `CoreLocalArray<T>`, a small utility for sharding frequently accessed state by physical CPU core to reduce contention and false sharing.

Important APIs and types: `CoreLocalArray<T>::Size()` reports the allocated shard count. `Access()` returns the element for the current core. `AccessElementAndIndex()` returns both pointer and index so callers can remember where an object came from. `AccessAtCore(size_t)` returns a specific shard and asserts bounds.

Control flow: construction reads `std::thread::hardware_concurrency()`, then chooses a power-of-two shard count at least eight. `AccessElementAndIndex()` calls `port::PhysicalCoreID()`. If the core id is unavailable, it chooses a random shard from the thread-local random generator. Otherwise it maps the core id with `BottomNBits(cpuid, size_shift_)`, which is a fast modulo for power-of-two sizes.

State and persistence: owns a `std::unique_ptr<T[]>` for process-local state only. The template does not enforce cache alignment, but comments tell users to make `T` cache aligned when false sharing matters.

Dependencies and integration points: depends on port core-id support, `Random::GetTLSInstance()`, and `BottomNBits()`. Used by compression context caching, statistics, concurrent arena sharding, and memtable range tombstone caches.

Risks: hardware concurrency can return zero on some platforms; because the minimum shift starts at 3, the array still has eight entries. Physical core ids can exceed the shard count and are folded by low bits, which can collide on some topology layouts. Cached indices can be inaccurate after thread migration, so callers should only cache them when documented tolerance exists.

Test signals: exercised indirectly by users such as compression context cache and statistics. There is no local direct test for CPU-id fallback distribution or alignment assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/core_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coro_utils.h -->
# sources/storage-engines/rocksdb/util/coro_utils.h

Purpose: supplies macros that let RocksDB declare and define paired synchronous and coroutine implementations from mostly shared code, while compiling cleanly when coroutine support is disabled.

Important APIs and macros: with `USE_COROUTINES`, `DECLARE_SYNC_AND_ASYNC`, `DECLARE_SYNC_AND_ASYNC_OVERRIDE`, and `DECLARE_SYNC_AND_ASYNC_CONST` declare both the regular function and a `folly::coro::Task<ret>` function with `Coroutine` suffix. Without coroutine support, they declare only the synchronous function. `using_coroutines()` is a constexpr feature probe. The second section undefines and redefines `DEFINE_SYNC_AND_ASYNC`, `CO_AWAIT`, and `CO_RETURN` based on whether the current inclusion is for `WITH_COROUTINES` or `WITHOUT_COROUTINES`.

Control flow and inclusion model: the file intentionally has a guarded declaration section and an unguarded idempotent macro-definition section. A source file can include it once normally, then include sync-and-async implementation headers twice with `WITH_COROUTINES` and `WITHOUT_COROUTINES` to generate both function bodies. In coroutine mode, `CO_AWAIT(foo)` expands to `co_await fooCoroutine`; in synchronous mode it expands to `foo`.

State and persistence: no runtime state or persistence. The behavior is entirely compile-time macro expansion.

Dependencies and integration points: conditionally includes Folly coroutine headers. Used by table cache, block based table reader, and version set sync/async implementation headers to keep MultiGet-style logic shared across sync and async variants.

Risks: macro hygiene is central; callers must define exactly the intended `WITH_COROUTINES` or `WITHOUT_COROUTINES` mode before including shared implementation fragments. Typos in the header comments do not affect behavior, but macro misuse can silently generate missing declarations or wrong call forms. The file lacks `#pragma once` around the whole file by design, so maintainers must preserve the two-section structure.

Test signals: indirect coverage comes from builds with and without `USE_COROUTINES` and tests exercising sync/async table read paths. There is no local runtime test because the utility is preprocessor-only.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coro_utils.h -->
