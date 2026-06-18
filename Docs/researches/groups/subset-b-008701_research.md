# subset-b-008701 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/aligned_buffer.h -->
## sources/storage-engines/rocksdb/util/aligned_buffer.h

Purpose: defines alignment-aware buffer utilities used mainly by direct I/O paths. `TruncateToPageBoundary`, `Roundup`, and `Rounddown` provide page and multiple alignment arithmetic. `AlignedBuffer` owns an aligned byte buffer through `FSAllocationPtr`, tracks aligned capacity, current size, and buffer start, and supports either internal heap allocation or file-system supplied allocation. `GrowableBuffer` is a lighter malloc-backed growable byte buffer for overwrite-oriented workflows that want to avoid `std::string` zeroing behavior.

Important APIs and types: `AlignedBuffer::ExternalAllocation` and `Allocator` describe externally allocated aligned memory. `Alignment()` validates power-of-two alignment. `AllocateNewBuffer(size_t,bool,uint64_t,size_t)` rounds requested capacity, allocates `new char[new_capacity + alignment_]`, aligns `bufstart_`, and optionally copies old contents. The status-returning `AllocateNewBuffer(size_t,const Allocator*)` validates allocator output for null, short, misaligned data, misaligned size, and null owner. `SetBuffer` adopts a `Slice` result plus owner without copying. `Append`, `Read`, `PadToAlignmentWith`, `PadWith`, `RefitTail`, `Destination`, `Size`, and `Release` are the main mutation and ownership controls. `GrowableBuffer::ResetForSize` reallocates with doubling and minimum 64 bytes, uses `malloc_usable_size` when available, and warms cache lines.

Control flow and state: callers must set `alignment_` before allocation. `AllocateNewBuffer` resets `cursize_` unless copying, while `Release` clears all visible state and returns ownership. `Append` clamps to remaining capacity; `Read` asserts offset validity and copies only available bytes. There is no persistence layer; state is in-memory ownership of temporary I/O or compression buffers.

Dependencies and integration: depends on `rocksdb/file_system.h` for `FSAllocationPtr`, `rocksdb/status.h`, port allocation helpers, and cache-line constants. Integration search shows use by `RandomAccessFileReader`, `WritableFileWriter`, `FilePrefetchBuffer`, `BlockFetcher`, encryption env code, and blob building through `GrowableBuffer`.

Risks and test signals: API safety relies heavily on assertions for alignment and bounds. `Destination()` and `Size()` expose manual mutation and can overrun if callers miscompute capacity. Move assignment does not clear the moved-from raw `bufstart_`, though ownership moves through `FSAllocationPtr`; moved-from use would be unsafe. External allocators are validated, which is a strong signal for direct-I/O correctness. Nearby tests in `random_access_file_reader_test.cc` exercise direct I/O buffer allocation contexts; this file has no dedicated test in the subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/aligned_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/aligned_storage.h -->
## sources/storage-engines/rocksdb/util/aligned_storage.h

Purpose: provides a minimal replacement for aligned storage by declaring `aligned_storage<T, Align>::type`, a raw byte array of `sizeof(T)` with `alignas(Align)`. It is used when RocksDB needs reserve storage for a type without constructing it immediately.

Important APIs and types: the only API is the class template `aligned_storage<T, std::size_t Align = alignof(T)>` with nested `type { alignas(Align) unsigned char data[sizeof(T)]; }`. It does not provide constructors, destructors, placement-new helpers, or typed accessors.

Control flow, state, and persistence: there is no runtime control flow and no persistent state. The type exists at compile time to enforce size and alignment for later placement construction by callers.

Dependencies and integration: depends only on `<cstddef>` and `rocksdb/rocksdb_namespace.h`. Integration search shows `db/write_thread.h` using it for `std::mutex` and `std::condition_variable` storage in write-thread state, where delayed construction and controlled lifetime matter.

Risks and test signals: callers are responsible for object lifetime, placement new, destruction, and type aliasing rules. The template allows custom `Align`, so an underspecified alignment could create undefined behavior if callers override the default incorrectly. There is no direct test in this subset; coverage is indirect through write-thread behavior and compilation on supported toolchains.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/aligned_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/async_file_reader.cc -->
## sources/storage-engines/rocksdb/util/async_file_reader.cc

Purpose: implements coroutine-gated asynchronous multi-read batching for RocksDB file reads when `USE_COROUTINES` is enabled. It queues suspended read awaiters, issues `RandomAccessFileReader::ReadAsync` calls for each `FSReadRequest`, polls the `FileSystem`, cleans I/O handles, records stats, and resumes suspended coroutines.

Important APIs and functions: `AsyncFileReader::MultiReadAsyncImpl(ReadAwaiter*)` appends an awaiter to an intrusive queue, increases `num_reqs_`, resizes per-request `io_handle_` and deleter vectors, and invokes `ReadAsync` with a callback that copies `status`, `result`, and `fs_scratch` back to the original `FSReadRequest`. `AsyncFileReader::Wait()` gathers non-null I/O handles from all queued awaiters, calls `fs_->Poll`, releases handles with per-request deleters, overwrites request statuses with poll errors when the request itself succeeded, resumes each coroutine, records `MULTIGET_IO_BATCH_SIZE`, and clears queue state.

Control flow and state: every `co_await` call suspends because `await_ready` is false and `MultiReadAsyncImpl` returns true. The reader owns a transient queue via `head_` and `tail_`, plus aggregate `num_reqs_`. The queue is drained in FIFO order by `Wait()`. There is no locking in this implementation; the friend `SingleThreadExecutor` integration implies single-threaded ownership.

Dependencies and integration: depends on `util/async_file_reader.h`, `FileSystem::Poll`, `RandomAccessFileReader::ReadAsync`, `StopWatch`, histograms, and `autovector`. Integration search shows `table/multiget_context.h` exposing an `AsyncFileReader` for MultiGet style table reads.

Risks and test signals: correctness depends on `Wait()` being called after scheduling; otherwise coroutines remain suspended and handles remain pending. If `ReadAsync` returns non-OK, the callback will not run and the code stores the error directly, but no handle may be present. Poll errors are broadcast to requests that have not already failed. The compile-time `USE_COROUTINES` guard means builds without coroutine support do not test this code. No direct test appears in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/async_file_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/async_file_reader.h -->
## sources/storage-engines/rocksdb/util/async_file_reader.h

Purpose: declares `AsyncFileReader`, an awaitable facade for batching asynchronous `RandomAccessFileReader` reads under coroutine builds. It lets callers request a multi-read operation and later run it through `folly::coro::co_viaIfAsync`.

Important APIs and types: `AsyncFileReader(FileSystem*, Statistics*)` stores non-owning pointers. `MultiReadAsync(RandomAccessFileReader*, const IOOptions&, FSReadRequest*, size_t, IODebugContext*)` returns `ReadOperation<ReadAwaiter>`. `ReadAwaiter` implements `await_ready`, `await_suspend`, and `await_resume`, captures read parameters, keeps `autovector<void*,32>` handles and `autovector<IOHandleDeleter,32>` deleters, stores the awaiting coroutine handle, and has an intrusive `next_` pointer. `ReadOperation::viaIfAsync` wraps the awaiter in Folly's executor-aware coroutine scheduling.

Control flow and state: callers receive a deferred `ReadOperation`. When awaited, `ReadAwaiter::await_suspend` caches the coroutine handle and calls `MultiReadAsyncImpl`; the implementation queues it and returns true, so the coroutine suspends. `Wait()` later polls and resumes. `head_`, `tail_`, and `num_reqs_` track pending operations.

Dependencies and integration: includes `file/random_access_file_reader.h`, Folly coroutine support, RocksDB file-system and statistics APIs, `autovector`, and `stop_watch`. `SingleThreadExecutor` is a friend and is expected to drive `Wait()`. `MultiGetContext` is a visible consumer.

Risks and test signals: the header has a malformed comment/pragma line (`LICENSE.Apache file in the root directory).#pragma once`) followed by a second `#pragma once`; compilers tolerate this as comment text plus the real pragma, but it is untidy. Lifetimes of `file`, `opts`, `read_reqs`, and `dbg` must outlive suspension. There is no synchronization, so multi-threaded use would race on queue state. No direct tests are included here; coverage depends on coroutine-enabled read paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/async_file_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/atomic.h -->
## sources/storage-engines/rocksdb/util/atomic.h

Purpose: wraps `std::atomic` so RocksDB call sites make memory ordering explicit and avoid accidental sequential consistency or invalid memory-order combinations. It also centralizes deprecated pre-C++20 atomic `shared_ptr` free-function usage behind compiler warning suppression.

Important APIs and types: `RelaxedAtomic<T>` exposes only relaxed operations: `StoreRelaxed`, `LoadRelaxed`, weak/strong CAS, exchange, and fetch arithmetic/bitwise operations. `Atomic<T>` derives from it and adds acquire/release/acq_rel versions: release stores, acquire loads, acq_rel CAS/exchange/fetch operations. `AtomicSharedPtrLoad` and `AtomicSharedPtrStore` call `std::atomic_load_explicit` and `std::atomic_store_explicit` with pragma guards for Clang and GCC deprecation warnings.

Control flow and state: wrappers are thin inline calls around an internal `std::atomic<T> v_`. They do not add persistence, logging, or locking. The type distinction forces callers to choose relaxed-only vs acquire-release capable state.

Dependencies and integration: depends on `<atomic>`, `<memory>`, and namespace headers. It is a shared utility for performance-sensitive concurrent code, and conceptually pairs with `bit_fields.h` for packed atomic state.

Risks and test signals: the wrappers deliberately omit seq_cst variants; callers with rare seq_cst requirements must not misuse acquire-release operations. `RelaxedAtomic` is only correct when not synchronizing other data. `compare_exchange_*` uses a single memory order, so failure ordering follows standard rules for that overload. There is no dedicated test in the subset; confidence comes from simple mapping to standard atomics and compile-time use across the codebase.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/auto_tune_compressor.cc -->
## sources/storage-engines/rocksdb/util/auto_tune_compressor.cc

Purpose: implements two experimental compression manager wrappers. `AutoSkipCompressorWrapper` learns when compression is likely to be rejected and can bypass compression. `CostAwareCompressor` constructs multiple built-in compressors at selected levels and records CPU and output-size costs, though selection is currently hard-coded.

Important APIs and functions: `CompressionRejectionProbabilityPredictor::Record` counts `kNoCompression` rejections versus successful compression in a fixed window and updates predicted rejection percentage. `AutoSkipCompressorWrapper::CompressBlock` bypasses auto-skip unless it owns the working area; otherwise it explores 10 percent of the time, or exploits the predictor by bypassing when predicted rejection exceeds 50 percent. `ObtainWorkingArea` wraps the underlying compressor's working area with an `AutoSkipWorkingArea`. `CostAwareCompressor` builds compressors for Snappy, LZ4, LZ4HC, and ZSTD level sets when supported, returns ZSTD as preferred, delegates dictionary APIs to the last configured compressor, and records elapsed micros and compressed output size into per-level predictors. Factory functions create manager wrappers around either a supplied manager or `GetBuiltinV2CompressionManager()`.

Control flow and state: auto-skip state lives in the working area's shared predictor, not the compressor object, so it is scoped to the managed working area. Cost-aware state includes `allcompressors_`, `allcompressors_index_`, and dynamically allocated `IOCPUCostPredictor` objects owned by `CostAwareWorkingArea`. There is no persistence beyond in-memory predictor windows.

Dependencies and integration: depends on RocksDB advanced compression interfaces, built-in manager support, options helpers, `Random`, `StopWatchNano`, and sync points. It plugs into SST compression through `CompressionManagerWrapper::GetCompressorForSST`.

Risks and test signals: `CostAwareCompressor::CompressBlock` hard-codes ZSTD index `(6,2)` for highest level, which assumes ZSTD support and vector layout even if unsupported; constructor may leave empty slots. `MaybeCloneSpecialized` explicitly TODOs full dictionary compression support. Manager `Name()` returns the wrapped name due to a noted error, which can obscure configuration identity. Predictor windows are simple and not thread-safe. Sync points provide test hooks, but this subset does not include direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/auto_tune_compressor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/auto_tune_compressor.h -->
## sources/storage-engines/rocksdb/util/auto_tune_compressor.h

Purpose: declares auto-tuning compression components: a rejection-probability predictor for skipping unproductive compression and a cost-aware compressor scaffold for comparing CPU and I/O costs of compression levels.

Important APIs and types: `CompressionRejectionProbabilityPredictor` has `Predict`, `Record`, and `attempted_compression_count`. `AutoSkipWorkingArea` owns the wrapped compressor working area plus a shared predictor. `AutoSkipCompressorWrapper` derives from `CompressorWrapper` and overrides `Name`, clone/specialization, `CompressBlock`, `ObtainWorkingArea`, and `ReleaseWorkingArea`. `AutoSkipCompressorManager` derives from `CompressionManagerWrapper`. `WindowAveragePredictor<T>` records window averages, with aliases `IOCostPredictor` and `CPUUtilPredictor`; `IOCPUCostPredictor` combines them. `CostAwareWorkingArea` owns a wrapped working area and a two-dimensional predictor pointer table. `CostAwareCompressor` derives directly from `Compressor`, holds compressor matrices and level indexes, and exposes dictionary, preferred type, working-area, specialization, and compression APIs. `CostAwareCompressorManager` wraps manager creation.

Control flow and state: predictor state is mutable and windowed. Working-area ownership is manual: auto-skip uses `shared_ptr` for the predictor, cost-aware uses raw `IOCPUCostPredictor*` entries that the implementation deletes in `ReleaseWorkingArea`.

Dependencies and integration: depends on `rocksdb/advanced_compression.h`. The manager classes integrate with RocksDB compression option plumbing and SST creation.

Risks and test signals: the header exposes low-level ownership expectations but does not use RAII containers for cost predictors, increasing leak risk if ownership conventions change. `CostAwareCompressor` constants for exploration and cutoff are declared but the current implementation does not use them for actual choice. There are sync points in the implementation, but no local test file in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/auto_tune_compressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/autovector.h -->
## sources/storage-engines/rocksdb/util/autovector.h

Purpose: implements `autovector<T,kSize>`, a small-vector-like container that stores up to `kSize` elements in inline stack storage and overflows into `std::vector<T>`. It targets RocksDB hot paths where most vectors are small and heap allocation should be avoided.

Important APIs and types: public container aliases mirror STL vector types. The nested `iterator_impl` provides random-access iterator operations over logical indices. Main methods include `only_in_stack`, `size`, `resize`, `empty`, `capacity`, `reserve`, `operator[]`, `at`, `front`, `back`, `push_back`, `emplace_back`, `pop_back`, `clear`, copy/move constructors, assignment, and forward/reverse iterators. Inline storage is `alignas(alignof(value_type)) char buf_[kSize * sizeof(value_type)]`, with `values_` pointing at it.

Control flow and state: elements below `kSize` are placement-new constructed in `buf_`; additional elements live in `vect_`. `resize` constructs or destroys inline elements and resizes/clears overflow storage. `clear` destroys inline elements and clears the vector. Copy assignment assigns overflow first and placement-constructs inline elements. Move assignment moves `vect_`, then placement-constructs and moves inline elements from the source while setting source `num_stack_items_` to zero.

Dependencies and integration: depends on standard algorithms/iterators/vector and RocksDB `port/lang.h`. Integration search shows use in async file reader handles and many small-list RocksDB internals.

Risks and test signals: this is manual lifetime code. `push_back(T&&)` uses default construction plus move assignment for inline storage, so `T` must be default constructible in that path, unlike a perfect placement construction. Iterator dereference asserts `size() >= index_` rather than `index_ < size()`, so dereferencing `end()` would not be caught by that assert before `operator[]` asserts. Move assignment does not destroy existing inline elements before overwriting if the target already held inline values, which is a potential leak or lifetime bug for non-trivial `T`. `autovector_test.cc` covers push/pop, emplace, resize, copy, iterators, and performance smoke paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/autovector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/autovector_test.cc -->
## sources/storage-engines/rocksdb/util/autovector_test.cc

Purpose: verifies functional behavior and provides ad hoc performance comparisons for `autovector`. It focuses on stack versus heap transition, construction APIs, copy semantics, iterator behavior, and relative cost against `std::vector`.

Important tests and helpers: `AssertAutoVectorOnlyInStack` checks whether overflow storage has been allocated. `PushBackAndPopBack` inserts `1000 * kSize` integers, verifies size and indexing, then pops all elements. `EmplaceBack` builds pairs of integer and string values. `Resize` grows from stack-only to overflow and shrinks. `CopyAndAssignment` checks copy construction and assignment for stack and heap-sized vectors using `AssertEqual`. `Iterators` exercises forward, reverse, const, arithmetic, dereference, and arrow operations. `PerfBench` prints creation/insertion and sequence access timings for string and integer vectors.

Control flow and state: tests create fresh containers and validate visible state after each mutation. The benchmark test is still a `TEST_F`, so it runs with normal tests and prints to stdout, but has no assertions on performance.

Dependencies and integration: includes `util/autovector.h`, RocksDB test harness, `Env` timing, and `string_util`. It installs the RocksDB stack trace handler in `main`.

Risks and test signals: coverage is useful for ordinary operations but misses move construction/assignment, self-assignment behavior, non-default-constructible types, exception safety, and destructor-counting lifetime checks. Because `PerfBench` is assertion-light and potentially expensive, it is a smoke/performance diagnostic rather than a correctness gate. The test does validate stack-to-heap transitions and iterator arithmetic across both storage regions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/autovector_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/bit_fields.h -->
## sources/storage-engines/rocksdb/util/bit_fields.h

Purpose: defines a template system for tightly packing named fields into an unsigned underlying integer and updating those fields atomically. It is intended for concurrent state machines where a single lock-free atomic word is easier to reason about than multiple atomics or locks.

Important APIs and types: `BitFields<UnderlyingT,DerivedT>` stores `underlying`, exposes `Set`, `With`, `Get`, and `Ref` for field operations, and defines `kBitCount`. `NoPrevBitField` anchors field layout. `BoolBitField<Parent,Prev>` declares a one-bit bool field with get/set and OR/AND transforms. `UnsignedBitField<Parent,kBitCount,Prev>` declares an unsigned field with inferred value type, mask, get/set, clear, AND, OR, plus and minus transforms. `OrTransformer`, `AndTransformer`, and `AddTransformer` compose atomic fetch operations. `RelaxedBitFieldsAtomic` and `BitFieldsAtomic` wrap `std::atomic<U>` and provide load/store/CAS/exchange plus transform application with relaxed or acquire-release order.

Control flow and state: field operations are static template computations over bit offsets. Atomic `Apply` functions perform fetch-or, fetch-and, or fetch-add and optionally return before/after states. Debug builds track additive transform preconditions to catch inter-field overflow or underflow, except for top-bit fields where overflow can be intentionally ignored.

Dependencies and integration: depends on `<atomic>`, `<vector>`, `test_util/sync_point.h` for `testable_assert`, and `util/math.h` for `BitwiseAnd`. Integration search shows packed atomics in `cache/clock_cache.h`, including slot metadata and chain state.

Risks and test signals: layout correctness is compile-time but overlapping fields are permitted by design, so misuse can silently alias state. Additive transforms rely on unsigned overflow and debug-only preconditions; release builds will not catch bad underflow/overflow between fields. The comment has a typo in "aquire-release" but behavior is clear. No direct test in this subset; confidence is mostly compile-time static assertions and downstream cache tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/bit_fields.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/bloom_impl.h -->
## sources/storage-engines/rocksdb/util/bloom_impl.h

Purpose: contains implementation details for RocksDB Bloom-like filters. It provides false-positive-rate math, a current cache-local Bloom implementation optimized for 64-byte cache lines and AVX2 queries, and legacy Bloom implementations kept for reading/building compatible formats.

Important APIs and types: `BloomMath` exposes `StandardFpRate`, `CacheLocalFpRate`, `FingerprintFpRate`, and `IndependentProbabilitySum`. `FastLocalBloomImpl` exposes `EstimatedFpRate`, `ChooseNumProbes`, `AddHash`, `AddHashPrepared`, `PrepareHash`, `HashMayMatch`, and `HashMayMatchPrepared`. `LegacyNoLocalityBloomImpl` provides traditional double-hashing Bloom add/query. `LegacyLocalityBloomImpl<ExtraRotates>` provides cache-line-local legacy add/query and read preparation with configurable cache-line byte size.

Control flow and state: all implementations are stateless static helpers over caller-owned filter bytes. Fast-local add selects a cache line with `FastRange32(h1, len_bytes >> 6)` and sets probe bits within that 512-bit line using repeated multiplication by the 32-bit golden-ratio constant. Query either loops scalar or, under `__AVX2__`, evaluates up to eight probes per vector batch using loads, permutes, blends, masks, and `_mm256_testc_si256`.

Dependencies and integration: depends on `port/port.h` for `PREFETCH`, `rocksdb/slice.h`, `util/hash.h`, and `<immintrin.h>` when AVX2 is available. It integrates below block-based filter policies and is tested through `bloom_test.cc`.

Risks and test signals: fast-local assumes 64-byte cache-line buckets and uses 32-bit fast-range indexing, with comments noting huge-filter accuracy limits and abrupt breakdown at 256GB of cache lines. AVX2 code assumes little-endian layout equivalence. Legacy variants are explicitly marked "DO NOT REUSE" because of speed and accuracy deficiencies. `bloom_test.cc` provides strong schema, FP-rate, corrupt-filter, and Ribbon fallback coverage, but AVX2-specific behavior only runs on AVX2 builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/bloom_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/bloom_test.cc -->
## sources/storage-engines/rocksdb/util/bloom_test.cc

Purpose: tests full-filter behavior for legacy Bloom, fast local Bloom, and Standard128 Ribbon policies. It verifies sizing, membership, false positive rates, memory optimization, binary schema compatibility, corrupt-filter behavior, filter construction cache charging, and Ribbon level-threshold behavior.

Important tests and helpers: `FullBloomTest` owns `BlockBasedTableOptions`, policy, builder, reader, buffer, and filter size. Helpers generate fixed-width integer keys, open raw filter bytes, build filters, inspect metadata, compute packed match fingerprints, first false positives, and measured false-positive rate. `FilterSize` validates millibits-per-key rounding, builder space calculation, approximate entry inversion, and overflow capping. `FullEmptyFilter`, `FullSmall`, and `FullVaryingLengths` validate basic semantics and FP bounds. `OptimizeForMemory` checks fragmentation/storage behavior with and without allocator usable-size support. `ChargeFilterConstructionTest.RibbonFilterFallBackOnLargeBanding` verifies Ribbon fallback under strict cache capacity. `Schema` locks down hashes, metadata, and first false positives for multiple bit rates and key ranges. `RawSchema` and `CorruptFilters` verify readers for hand-built metadata, including fail-open behavior on bad filters. `RibbonTestLevelThreshold` verifies Bloom-before-level policy across compaction styles and creation reasons.

Control flow and state: the parameterized suite runs across `LegacyBloom`, `FastLocalBloom`, and `Standard128Ribbon`. GFlags provide `bits_per_key`; without GFlags the test exits successfully after printing a skip message.

Dependencies and integration: includes block-based filter internals, cache reservation manager, jemalloc helper, convenience APIs, test harness, hash utilities, and gflags compatibility. It exercises public `FilterPolicy` construction plus internal `FilterBitsBuilder` and `FilterBitsReader`.

Risks and test signals: schema fingerprints are intentionally brittle to catch incompatible filter changes. FP-rate checks are probabilistic but deterministic over generated keys. Some allocator expectations are conditional on jemalloc and `malloc_usable_size`. The GFlags skip path can hide coverage in builds lacking GFlags. Overall this is a high-signal regression suite for filter behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/bloom_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/build_version.cc.in -->
## sources/storage-engines/rocksdb/util/build_version.cc.in

Purpose: CMake/configure-style template that becomes a C++ source file containing RocksDB build metadata, plugin registry built-ins, and version-string helpers.

Important APIs and functions: template variables define `rocksdb_build_git_sha`, `rocksdb_build_git_tag`, `HAS_GIT_CHANGES`, and `rocksdb_build_date`, choosing Git date for clean trees and build date for modified trees. Plugin externs and built-in registry entries are injected into `ObjectRegistry::builtins_`. `AddProperty` parses `name:value` strings and skips failed substitutions. `LoadPropertiesSet` creates a heap map of build properties. `GetRocksBuildProperties` returns a static unique-owned map. `GetRocksVersionAsString` formats major/minor or major/minor/patch. `GetRocksBuildInfoAsString` formats program/version and optional verbose properties.

Control flow and state: initialization is lazy through function-local static `unique_ptr`. Build properties are immutable after initialization. The generated registry map is a namespace-level static.

Dependencies and integration: includes `rocksdb/version.h`, `rocksdb/utilities/object_registry.h`, and `util/string_util.h`. It integrates with build scripts that substitute `@GIT_SHA@`, `@GIT_TAG@`, `@GIT_MOD@`, `@GIT_DATE@`, `@BUILD_DATE@`, `@ROCKSDB_PLUGIN_EXTERNS@`, and `@ROCKSDB_PLUGIN_BUILTINS@`.

Risks and test signals: correctness depends on substitution tooling. `AddProperty` silently skips unresolved placeholders after the colon, which avoids exposing template artifacts but can hide build metadata failures. Static initialization of `ObjectRegistry::builtins_` is global and must match registry expectations. No direct test appears in this subset; coverage is from generated builds and version-reporting tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/build_version.cc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/cast_util.h -->
## sources/storage-engines/rocksdb/util/cast_util.h

Purpose: collects small casting and pointer helpers used to make potentially unsafe conversions explicit. It supports checked static casts for legacy downcasts, lossless integral casts, initializer-list disambiguation, and non-owning optional references.

Important APIs and types: `static_cast_with_check<DestClass>(SrcClass*)` performs `static_cast` and, when RTTI is enabled, asserts equality with `dynamic_cast`. The shared-pointer overload uses `std::static_pointer_cast` and debug RTTI validation. `lossless_cast<To>(From)` supports integral or enum value casts when the destination is at least as large, and pointer reinterpret casts between integral/enum pointee types with equal size. `List<T>` returns a homogeneous `initializer_list` reference. `UnownedPtr<T>` wraps a raw pointer with `get`, `operator->`, `operator*`, and bool conversion without ownership semantics.

Control flow and state: most checks are compile-time `static_assert`s. Runtime validation exists only for RTTI-enabled checked casts. `UnownedPtr` stores a nullable raw pointer and does not manage lifetime.

Dependencies and integration: depends on `<initializer_list>`, `<memory>`, `<type_traits>`, and RocksDB namespace headers. `coding.h` uses `lossless_cast` for byte pointer conversions in varint code.

Risks and test signals: `static_cast_with_check` can still be unsafe in non-RTTI builds if the caller's type assumption is wrong. `lossless_cast` checks type size, not signed range of runtime values, so signed-to-unsigned semantic surprises remain possible. The pointer branch has a likely typo checking `std::is_enum_v<To>` instead of the destination dereferenced type, though integral destination pointers satisfy the other condition. `UnownedPtr` can dangle. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/cast_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/channel.h -->
## sources/storage-engines/rocksdb/util/channel.h

Purpose: implements a simple blocking FIFO channel template for moving `T` values between producer and consumer threads, with explicit EOF signaling.

Important APIs and types: `channel<T>` owns a `std::queue<T>`, `std::mutex`, `std::condition_variable`, and `eof_` flag. `write(T&&)` pushes an element and wakes one waiter. `read(T&)` blocks until EOF or data, moves the front value into the output parameter, pops it, and returns false only when EOF is reached and the queue is empty. `sendEof()` sets EOF and wakes all waiters. `eof()` reports true only when the buffer is empty and EOF was sent. `size()` returns the buffered count.

Control flow and state: all public state access locks `lock_`. Reads drain queued data even after EOF is signaled, then return false once empty. The second `notify_one` in `read` can wake another waiter after a pop, though there is no bounded capacity in this implementation.

Dependencies and integration: depends only on standard condition-variable, mutex, queue, and utility headers plus RocksDB namespace. It is a generic utility; no direct integration from the required subset was needed for interpretation.

Risks and test signals: `write` after `sendEof` is not rejected, so caller protocol must prevent post-EOF writes or consumers can observe surprising behavior. The channel is unbounded and can grow under producer pressure. `write` only accepts rvalues. No direct tests appear in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/channel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/cleanable.cc -->
## sources/storage-engines/rocksdb/util/cleanable.cc

Purpose: implements `Cleanable` cleanup callback chains and `SharedCleanablePtr`, a reference-counted wrapper around a `Cleanable` used to share cleanup ownership among objects and transfer cleanup responsibilities.

Important APIs and functions: `Cleanable` initializes an embedded head cleanup node, runs `DoCleanup` in its destructor, supports move construction/assignment by transferring the head/list, and disables source cleanup after move. `DelegateCleanupsTo` registers each cleanup with another `Cleanable`, preserving ownership by transferring heap nodes where possible. `RegisterCleanup(Cleanup*)` installs a heap node or fills the embedded head. `RegisterCleanup(CleanupFunction, void*, void*)` either fills the embedded head or allocates a new cleanup node. `SharedCleanablePtr::Impl` extends `Cleanable` with relaxed atomic ref counting. `SharedCleanablePtr` supports allocate/reset/copy/move/destruction, dereference, registering a copy with a target cleanable, and moving its reference as a cleanup to a target.

Control flow and state: `Cleanable` stores one cleanup inline to avoid allocation for the common single-callback case and a linked list for extras. `SharedCleanablePtr` starts `Impl::ref_count` at one, increments on copies or registered virtual copies, and deletes the impl on the final `Unref`, triggering `Cleanable` cleanup.

Dependencies and integration: includes `rocksdb/cleanable.h`, atomics, assertions, and utility moves. Integration search shows cache handles, DB iterator/read paths, and shared cleanup pinning using `Cleanable` and `SharedCleanablePtr`.

Risks and test signals: move assignment asserts no self-move and would be unsafe if violated in release builds. `DelegateCleanupsTo` can reorder callbacks because `RegisterCleanup` inserts heap nodes near the head. Ref counting uses relaxed atomics, which is adequate only if object lifetime is otherwise synchronized around cleanup data. No direct test in this subset; behavior is heavily exercised indirectly by cache and iterator pinning tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/cleanable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding.cc -->
## sources/storage-engines/rocksdb/util/coding.cc

Purpose: provides out-of-line implementations for selected varint encoding and decoding functions declared in `coding.h`, keeping hot inline helpers in headers while centralizing fallback loops.

Important APIs and functions: `EncodeVarint32(char*, uint32_t)` emits one to five bytes using continuation bit `128`, with specialized branches for value ranges under 2^7, 2^14, 2^21, 2^28, and larger. `GetVarint32PtrFallback(const char*, const char*, uint32_t*)` decodes up to five bytes, returning nullptr on truncation or malformed overflow. `GetVarint64Ptr` decodes up to ten bytes by shifting seven bits at a time and returns nullptr on truncation or malformed data.

Control flow and state: all functions are stateless and operate on caller-provided byte ranges. Encode returns the first byte after the encoded value. Decode functions advance local pointers and only write output on successful termination.

Dependencies and integration: includes `util/coding.h` and RocksDB slice headers. `coding.h` inline functions call these from string append, slice parse, and pointer parse APIs.

Risks and test signals: callers must provide sufficient output space for encoders and correct input bounds for decoders. The 64-bit loop condition uses `shift <= 63` with increments of 7, allowing ten bytes while avoiding shifts beyond 63. `coding_test.cc` covers fixed encodings, varint round trips, overflow, truncation, length-prefixed strings, and prefix-varint helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding.h -->
## sources/storage-engines/rocksdb/util/coding.h

Purpose: declares and implements RocksDB's canonical byte-order-independent serialization helpers for fixed-width integers, varints, signed zigzag varints, length-prefixed slices, delimiter slicing, and unaligned memory access.

Important APIs and types: fixed writers `PutFixed16/32/64` append little-endian values to strings, while `EncodeFixed*` and `DecodeFixed*` come from `coding_lean.h`. Varint APIs include variadic `PutVarint32`, `PutVarint64`, combined append helpers, `EncodeVarint32/64`, `GetVarint32/64`, pointer decoders, and `VarintLength`. Signed values use `i64ToZigzag`, `zigzagToI64`, `PutVarsignedint64`, and `GetVarsignedint64`. Slice helpers include `PutLengthPrefixedSlice`, `PutLengthPrefixedSliceParts`, padding variants, `GetLengthPrefixedSlice`, and `GetSliceUntil`. `PutUnaligned` and `GetUnaligned` abstract platforms that disallow unaligned access.

Control flow and state: functions are stateless transformations on strings, slices, and byte pointers. `Get*` functions advance `Slice` inputs only on success. The unchecked `GetLengthPrefixedSlice(const char*)` assumes well-formed data and limits varint parsing to five bytes.

Dependencies and integration: includes `port/port.h`, `rocksdb/slice.h`, `util/cast_util.h`, and `util/coding_lean.h`. This file is broadly integrated across table formats, keys, options, metadata, and filter tests.

Risks and test signals: many lower-level APIs require callers to allocate enough output space and provide valid data. Length-prefixed slice sizes are cast to `uint32_t`, so callers must not encode slices larger than that contract. Unaligned helpers depend on compile-time platform detection. `coding_test.cc` gives strong boundary coverage for fixed encodings, varints, truncation, overflow, strings, and prefix-varint behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding_lean.h -->
## sources/storage-engines/rocksdb/util/coding_lean.h

Purpose: supplies a small, dependency-light subset of fixed-width little-endian encode/decode helpers. It is separated from `coding.h` for users that only need fixed integer serialization without slice and varint machinery.

Important APIs and functions: `EncodeFixed16`, `EncodeFixed32`, and `EncodeFixed64` write little-endian bytes into caller-provided buffers, using `memcpy` on little-endian platforms and manual byte extraction otherwise. `DecodeFixed16`, `DecodeFixed32`, and `DecodeFixed64` read little-endian bytes, using `memcpy` on little-endian platforms and manual reconstruction otherwise.

Control flow and state: all functions are inline, stateless, and perform no bounds checks. The caller must supply buffers of at least 2, 4, or 8 bytes as appropriate.

Dependencies and integration: depends on `<cstdint>`, `<cstring>`, and `port/port.h` for `port::kLittleEndian`. `coding.h`, comparator timestamp helpers, and Bloom tests use these primitives through fixed encoding APIs.

Risks and test signals: absence of bounds checks is intentional but places responsibility on callers. Endianness correctness is central to on-disk compatibility. `coding_test.cc` validates little-endian output and fixed integer round trips over broad value ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding_lean.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding_test.cc -->
## sources/storage-engines/rocksdb/util/coding_test.cc

Purpose: tests fixed integer encoding, legacy varint encoding, length-prefixed string parsing, and prefix-varint helpers. It is the main regression suite for serialization primitives used throughout RocksDB formats.

Important tests and helpers: `Fixed16`, `Fixed32`, and `Fixed64` perform round trips over large value sets and powers-of-two boundaries. `EncodingOutput` asserts little-endian byte order. `Varint32` and `Varint64` round-trip many boundary values and verify encoded length. Overflow and truncation tests verify malformed varints return nullptr. `Strings` checks length-prefixed slices. Prefix-varint helper traits abstract over 32- and 64-bit APIs, while tests validate exact byte strings, split disk-read decode APIs, invalid additional-byte counts, overflow, truncation, and `EncodePrefixVarint64<kMinimumBytes>` improper/minimum-width encodings.

Control flow and state: tests build encoded strings, decode by pointer and `Slice`, and assert input exhaustion. Prefix-varint tests keep helper cases close to expected byte strings, creating a schema-style compatibility lock.

Dependencies and integration: includes `util/coding.h`, RocksDB test harness, and `util/prefix_varint.h`. `main` installs stack traces and runs GoogleTest.

Risks and test signals: this suite is high-signal for serialization compatibility and malformed-input handling. It does not directly test `PutUnaligned/GetUnaligned`, `GetSliceUntil`, or oversized length-prefix caller contracts. Prefix-varint coverage in this file means changes to `prefix_varint.h` can break this coding test even though that header is outside the work item.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/coding_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compaction_job_stats_impl.cc -->
## sources/storage-engines/rocksdb/util/compaction_job_stats_impl.cc

Purpose: implements reset and aggregation behavior for `CompactionJobStats`, the struct RocksDB uses to report compaction metrics such as timing, record counts, byte counts, file counts, deletion handling, corruption count, write timing, and single-delete anomalies.

Important APIs and functions: `CompactionJobStats::Reset()` sets numeric counters to zero, restores booleans to defaults, sets `has_accurate_num_input_records` true, clears smallest/largest output key prefixes, and resets compaction flags. `CompactionJobStats::Add(const CompactionJobStats&)` accumulates counters, ANDs `has_accurate_num_input_records`, ORs `is_remote_compaction`, and adds file/write timing and single-delete counters.

Control flow and state: state is stored directly in the public stats object. `Reset` is a full reinitialization. `Add` is additive aggregation except for booleans with explicit semantics. Notably `Add` does not aggregate `is_full_compaction`, `is_manual_compaction`, or key prefix strings.

Dependencies and integration: includes `rocksdb/compaction_job_stats.h`. It integrates with compaction job reporting, event listeners, and external stats consumers.

Risks and test signals: aggregation omissions may be intentional for job-level flags, but consumers should not assume all fields are merged. Arithmetic can overflow on long-running or aggregated workloads because fields are plain counters. No direct tests in this subset; coverage is likely indirect through compaction tests and API consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/compaction_job_stats_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/comparator.cc -->
## sources/storage-engines/rocksdb/util/comparator.cc

Purpose: implements RocksDB's built-in user-key comparators: bytewise, reverse bytewise, and variants that append 64-bit timestamps. It also registers these comparators with the object library and supports configuration-string creation.

Important APIs and types: `BytewiseComparatorImpl` implements lexicographic `Compare`, `Equal`, separator shortening, short successor generation, same-length immediate successor detection, timestamp-agnostic comparison, and equality. `ReverseBytewiseComparatorImpl` reverses comparison order, supplies conservative separator behavior, disables short successor, and returns false for immediate successor to avoid auto-prefix-mode design issues. `ComparatorWithU64TsImpl<TComparator>` wraps a root comparator with `timestamp_size()==8`, compares user keys without timestamps first, orders larger timestamps first for equal user keys, exposes max/min timestamp slices, and formats timestamps. Public factories return static singleton comparators. `DecodeU64Ts`, `EncodeU64Ts`, `MaxU64Ts`, and `MinU64Ts` provide timestamp utilities. `Comparator::CreateFromString` parses custom options, registers built-ins once, handles known IDs, empty reset, registry lookup, and object configuration.

Control flow and state: singleton comparators use `STATIC_AVOID_DESTRUCTION`. Built-in registration is protected by `std::once_flag`. Timestamp comparison strips or extracts the final eight bytes when `a_has_ts` or `b_has_ts` says timestamps are present. Configuration creation may return static objects or registry-created static objects.

Dependencies and integration: depends on `db/dbformat.h` for timestamp slice helpers, `util/coding.h` for fixed64 encoding, customizable and object registry APIs, and `rocksdb/comparator.h`. Integration search shows these comparators throughout DB, table, transaction, options, and lock tests.

Risks and test signals: comparator semantics are on-disk compatibility critical. Separator algorithms must preserve ordering; bytewise asserts the shortened key remains below the limit, while reverse comparator intentionally handles fewer cases. Timestamp comparator assumes timestamp suffix size and fixed64 encoding. `CreateFromString` behavior depends on registry availability and ignore-unsupported settings. Tests are mostly outside this subset, but integration search shows extensive use in options, table, transaction, iterator, and timestamp tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/comparator.cc -->
