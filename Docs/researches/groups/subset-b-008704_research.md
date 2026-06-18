# subset-b-008704 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash_test.cc -->
# sources/storage-engines/rocksdb/util/hash_test.cc

Purpose: provides regression tests for RocksDB hash and small math primitives whose outputs are format-sensitive. It locks down legacy 32-bit `Hash`, XXH-derived `Hash64`/`Hash128`, range-reduction helpers, 128-bit coding helpers, and bit-manipulation utilities used by Bloom filters, table indexes, hash tables, and other persisted or performance-sensitive paths.

Important APIs/types/functions: tests call `Hash`, `Hash64`, `Hash128`, `Hash2x64`, `GetSliceHash64`, `GetSliceHash128`, `BijectiveHash2x64`, `BijectiveUnhash2x64`, `FastRange32`, `FastRange64`, `FastRangeGeneric`, `BottomNBits`, `FloorLog2`, `ConstexprFloorLog2`, `CountTrailingZeroBits`, `BitsSetToOne`, `BitParity`, `EndianSwapValue`, `ReverseBits`, `DownwardInvolution`, `BitwiseAnd`, `Multiply64to128`, `EncodeFixed128`, `DecodeFixed128`, `EncodeFixedGeneric`, and `DecodeFixedGeneric`.

Control flow: fixed-value tests first verify stable hash outputs for many short byte strings. Miscellaneous loops then compare seeded and unseeded hash entry points, check upper/lower reconstruction, assert seed and length sensitivity, and validate bijective 16-byte transformations. Descriptor helpers compress hash results for all lengths up to 430 bytes to guard against algorithm changes across XXH size classes. The math section runs templated bit-operation checks over many integral types and `Unsigned128`, then checks multiplication and fixed-width coding.

State and persistence behavior: the test itself persists nothing, but many expected values are contract tests for persisted file-format behavior, especially Bloom hash compatibility and encoded table metadata compatibility. The `main` function prints the `GetSliceNPHash64("RocksDB")` id for diagnostic visibility before running GoogleTest.

Dependencies/integration points: depends on `util/hash.h`, `util/hash128.h`, `util/math.h`, `util/math128.h`, `util/coding.h`, `util/coding_lean.h`, and RocksDB's test harness. It is the local test signal for both hash and math utility headers because math has no separate dedicated test binary in this subset.

Risks: expected hash descriptors are intentionally brittle; legitimate algorithm upgrades require coordinated format-compatibility review. Some negative uniqueness checks are probabilistic and could theoretically collide, though the chosen inputs make that unlikely. The templated math tests avoid undefined inputs such as full-width `BottomNBits` and zero `FloorLog2`, so callers still need to respect those preconditions.

Test signals: this file is itself the primary test. It covers stable hash schemas, `FastRange` boundary values, 32/64/128-bit bit operations, endian swap/reverse behavior, downward involution properties, 64x64-to-128 multiplication, and fixed-width generic encoding/decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/heap.h -->
# sources/storage-engines/rocksdb/util/heap.h

Purpose: implements `BinaryHeap`, a small max-heap optimized for RocksDB multi-way merge workloads where replacing the current top is common and consecutive winners often come from the same input stream.

Important APIs/types/functions: `BinaryHeap<T, Compare>` exposes `push`, `top`, `replace_top`, `pop`, `swap`, `clear`, `empty`, `size`, and `reset_root_cmp_cache`. Private helpers compute parent/child indexes and implement `upheap` and `downheap`. The container stores entries in `autovector<T>` and follows `std::priority_queue` ordering: `Compare` is a less-than relation and `top()` returns the maximum.

Control flow: `push` appends and bubbles a moved value up. `replace_top` overwrites the root and calls `downheap`, avoiding the pop-plus-push comparison cost. `pop` moves the last value to the root, removes the tail, then downheaps unless the heap is empty. `downheap` chooses the larger child and caches the root child comparison when only the root value changed, allowing repeated `replace_top` calls to skip one comparison pattern.

State and persistence behavior: all state is in memory: comparator, vector storage, and `root_cmp_cache_`. It does not persist data and does not own external resources. Cache validity is reset on `push`, `clear`, many downheap paths, and swap transfers it with the heap.

Dependencies/integration points: used by merge-like RocksDB internals that need faster replace-top behavior than `std::priority_queue`. It depends on `util/autovector.h`, standard comparison utilities, and `port/port.h` for assertions/platform setup.

Risks: methods assert on invalid use such as `top`, `pop`, or `replace_top` on an empty heap. Correctness relies on `Compare` remaining stable and compatible with the stored values. The root comparison cache is a performance optimization with subtle invalidation rules, so future mutation APIs must reset it carefully.

Test signals: `heap_test.cc` compares random operation sequences against `std::priority_queue`, including duplicates, small heaps, one-element/two-element heaps, growing and draining behavior, `replace_top`, `pop`, and `clear`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/heap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/heap_test.cc -->
# sources/storage-engines/rocksdb/util/heap_test.cc

Purpose: verifies `BinaryHeap` behaves like `std::priority_queue` over long pseudo-random operation streams while exercising RocksDB's replace-top optimization surface.

Important APIs/types/functions: defines `HeapTestValue`, parameter tuple `(MAX_HEAP_SIZE, MAX_VALUE, RNG_SEED)`, parameterized fixture `HeapTest`, and `TEST_P(HeapTest, Test)`. The test calls `BinaryHeap::push`, `replace_top`, `pop`, `top`, `empty`, and `clear`, comparing against `std::priority_queue`.

Control flow: each parameterized run chooses insert, replace-top, or pop by deterministic random distributions. Insertion is slightly more frequent until `MAX_HEAP_SIZE` is reached, then the test drains without inserting until empty. After every operation, it checks empty state and top value against the reference priority queue.

State and persistence behavior: all state is local to the test: random generator, `BinaryHeap`, reference heap, drain flag, and operation counters. It writes no persistent files and uses the `FLAGS_iters` gflag only to scale runtime.

Dependencies/integration points: depends on `util/heap.h`, GoogleTest, optional gflags, `port/stack_trace.h`, and standard random/queue utilities. It is the direct regression suite for the custom heap used by merge code elsewhere.

Risks: the test checks externally visible behavior, not exact comparison counts or root-cache behavior. It uses `assert` for some internal test invariants, so those checks depend on assertion configuration. Random streams are deterministic by seed but do not exhaustively cover every comparator or move-only type scenario.

Test signals: parameter sets cover a large heap with occasional duplicates, many duplicates, no-duplicate small heaps, two-element heaps, and one-element heaps. The test also verifies at least one max-size drain happens and that `clear` leaves the heap empty.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/heap_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/interval_test.cc -->
# sources/storage-engines/rocksdb/util/interval_test.cc

Purpose: tests `IntervalSet` behavior for integer intervals and comparator-based `Slice` intervals, including merge, containment, open-ended intervals, and propagation mode return semantics.

Important APIs/types/functions: uses `IntervalSet<int>`, `Interval<int>`, `IntervalSet<Slice, Comparator>`, `BytewiseComparator`, `insert(start, end)`, `insert(start)`, iterators, `size`, `start`, `end`, and `has_end`.

Control flow: `BasicTest` inserts overlapping and adjacent integer intervals and checks canonical merged ranges. `SliceTest` inserts bounded and open-ended key ranges under the bytewise comparator and verifies contained inserts do not create new ranges. `PropModeTest` constructs the set with propagation mode enabled and verifies `insert` returns `false` when the inserted interval is already covered.

State and persistence behavior: interval state is purely in-memory and local to each test. No DB state is opened despite using `db_test_util` for the harness and stack trace setup.

Dependencies/integration points: validates `rocksdb/data_structure.h` interval utilities with both native ordering and RocksDB comparator ordering. Slice tests model key-range tracking behavior used by higher-level DB components that reason about key intervals.

Risks: coverage is focused on simple merge and containment cases. It does not stress randomized intervals, custom comparators beyond bytewise, reverse iteration, deletion, or very large interval sets. The final `SliceTest` leaves a trailing comment marker but no functional gap.

Test signals: confirms overlapping intervals collapse, disjoint intervals remain ordered, point/open-ended intervals are represented correctly, and propagation mode distinguishes new coverage from already-covered inserts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/interval_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/io_dispatcher_imp.cc -->
# sources/storage-engines/rocksdb/util/io_dispatcher_imp.cc

Purpose: implements RocksDB's `IODispatcher` for block-based table reads. It builds `ReadSet` objects that prefetch data blocks, coalesce nearby reads, honor cache and read-scoped buffer policies, optionally submit async I/O, enforce a prefetch memory budget, and provide on-demand `ReadIndex`/`ReadOffset` access.

Important APIs/types/functions: key implementation pieces are `IODispatcherImpl::Impl`, `SubmitJob`, `PrepareIORequests`, `PreCoalesceBlocks`, `DispatchPrefetch`, `ExecuteAsyncIO`, `ExecuteSyncIO`, `TryAcquireMemory`, `ReleaseMemory`, `TryDispatchPendingPrefetches`, `CreateAndPinBlockFromBuffer`, `GetReadScopedIOConfig`, `AsyncIOState`, `PendingPrefetchRequest`, and `ReadSet` methods including destructor, `ReadIndex`, `ReadOffset`, `ReleaseBlock`, `ReleasePrefetchMemory`, `ReleaseAsyncIOForBlock`, `PollAndProcessAsyncIO`, and `SyncRead`.

Control flow: `SubmitJob` creates a `ReadSet`, records the target filesystem, initializes pinned-block and size arrays, sorts block indexes by offset unless the job says they are sorted, checks the data block cache when applicable, computes uncached block sizes, coalesces uncached blocks by offset gap and memory budget, dispatches groups whose memory can be acquired, and queues the rest. `ReadIndex` first returns already pinned blocks, then polls async state if present, otherwise removes the block from pending and performs synchronous fallback. `ReadOffset` maps an offset to a block with binary search over sorted indexes. Memory release can trigger queued groups to dispatch.

State and persistence behavior: persistent database files are read but not mutated. In-memory dispatcher state includes global prefetch memory accounting, pending prefetch queue, statistics pointer, and shared `Impl` lifetime. Each `ReadSet` owns pinned cache entries, pending flags, block size accounting, async state map, sorted index, and weak dispatcher callback. Async states own scratch buffers, aligned/direct-I/O buffers, read-scoped leases, filesystem handles, request status, coalesced block handles, and cleanup functions.

Dependencies/integration points: integrates with `BlockBasedTable`, `RandomAccessFileReader`, `FileSystem::Poll`/`AbortIO`, `FSReadRequest`, `CachableEntry<Block>`, block cache lookup and insertion, decompression dictionaries, `ReadScopedBlockBufferProvider`, direct-I/O aligned buffers, RocksDB statistics tickers, sync points, and `IODispatcher` factory functions `NewIODispatcher`.

Risks: ownership and cleanup are subtle. The destructor must abort async I/O before deleting handles. Coalesced async states can be shared by many block indexes, so releasing one block must not abort the whole request unless it was the final remaining block. Prefetch memory must be released exactly once even after `ReadIndex` moves pinned entries out. Provider-backed uncompressed blocks require a cleanup object; otherwise pinning memory would be unsafe. Async `NotSupported` is expected to fall back to sync, while real async setup errors must surface. Sorting assumptions affect coalescing and `ReadOffset` correctness.

Test signals: `io_dispatcher_test.cc` covers basic reads, cache hits and cache bypass, fill-cache behavior, no-block-cache paths, read-scoped provider lifetime, direct I/O alignment, compressed block decompression into provider memory, mmap ignoring providers, coalescing, sorted-handle optimization, memory-limit queuing and release, oversized fallback, sync and async modes, async abort behavior, controlled stray completions, and async-not-supported fallback.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/io_dispatcher_imp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/io_dispatcher_imp.h -->
# sources/storage-engines/rocksdb/util/io_dispatcher_imp.h

Purpose: declares the concrete `IODispatcherImpl` class that implements the public `IODispatcher` interface by delegating implementation details to an internal shared `Impl`.

Important APIs/types/functions: `IODispatcherImpl` has a default constructor, an options constructor taking `IODispatcherOptions`, a virtual destructor, and `SubmitJob(const std::shared_ptr<IOJob>&, std::shared_ptr<ReadSet>*)`. The private `struct Impl` is hidden behind `std::shared_ptr<Impl> impl_`.

Control flow: callers construct the dispatcher directly or through `NewIODispatcher` factories in the `.cc` file, then submit an `IOJob`. All real work is delegated to `impl_->SubmitJob`, keeping the header stable and small while allowing the implementation to use private helper types.

State and persistence behavior: the header exposes only the shared implementation pointer. It persists no on-disk state. Shared ownership lets `ReadSet` callbacks safely hold weak/shared references to dispatcher memory accounting state after public dispatcher objects move through normal lifetimes.

Dependencies/integration points: depends on `rocksdb/io_dispatcher.h` for the public interface, `IOJob`, `ReadSet`, `IODispatcherOptions`, and `Status`. It is the bridge between public RocksDB I/O dispatcher APIs and the block-based table implementation in `io_dispatcher_imp.cc`.

Risks: the PIMPL design hides invariants from the header, so API users must rely on the public `IODispatcher` contract. Lifetime is intentionally shared; changing `impl_` ownership could break `ReadSet` memory-release callbacks.

Test signals: all behavior is exercised through `io_dispatcher_test.cc` and through block-based iterator paths that call `NewIODispatcher`/`SubmitJob`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/io_dispatcher_imp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/io_dispatcher_test.cc -->
# sources/storage-engines/rocksdb/util/io_dispatcher_test.cc

Purpose: provides an extensive regression suite for `IODispatcher`, `ReadSet`, block prefetching, cache interaction, read-scoped block buffers, direct I/O, async I/O fallback, coalescing, and prefetch memory accounting.

Important APIs/types/functions: defines `ReadTrackingFS`, `ReadTrackingRandomAccessFile`, `ControlledAsyncFS`, `ControlledAsyncRandomAccessFile`, `ControlledAsyncHandle`, fixture `IODispatcherTest`, `TestReadScopedBlockBufferProvider`, `InvalidReadScopedBlockBufferProvider`, `CreateAndOpenSST`, `CollectBlockHandles`, `NewFileWriter`, and `NewFileReader`. Tests drive `NewIODispatcher`, `SubmitJob`, `ReadSet::ReadIndex`, `ReadSet::ReadOffset` indirectly through block handles, `ReleaseBlock`, and block-based table iterators.

Control flow: the fixture creates real SST files with many data blocks, reopens them through tracking filesystems, collects data block handles from the table index, submits dispatcher jobs, and verifies returned `Block` objects or iterator values. Tracking filesystems record `MultiRead` and `ReadAsync` calls. Controlled async tests defer completion until `Poll` or `AbortIO` to model io_uring ordering and released-handle races.

State and persistence behavior: tests write temporary per-thread SST files and destroy the directory in teardown. Fixture vectors intentionally retain options, comparators, env options, statistics, and table readers so returned `BlockBasedTable` objects do not reference destroyed dependencies. Provider tests track live allocations and outstanding bytes to verify cleanup after block/reset/readset lifetimes.

Dependencies/integration points: integrates the dispatcher with block-based table builder/reader, cache, direct reads, mmap reads, compression, `ReadScopedBlockBufferProvider`, `RandomAccessFileReader`, `FileSystemWrapper`, sync points, DB test utilities, and RocksDB statistics tickers. It also exposes `RocksDbIOUringEnable` for async test enablement when compiled with io_uring.

Risks: some async tests are skipped when io_uring is unavailable, so platform coverage differs. Tests create large random-value SSTs and can be relatively heavy. Several assertions depend on exact cache and coalescing behavior, making them sensitive to table format or block sizing changes. The fixture's lifetime retention is required because block table readers store references to options.

Test signals: coverage includes basic and multi-file reads, statistics accounting, sync versus async reads, block content validation, cache pin cleanup on `ReadSet` destruction, coalescing thresholds, sorted-handle sort skipping, request offset validation, memory limit queuing, release-triggered dispatch, zero memory limit, partial prefetch, oversized block fallback, memory release after moved-out blocks, read-scoped cache bypass and provider ownership, invalid provider failure, direct I/O alignment, regular iterator and MultiScan provider propagation, async abort on release, stray completion safety, range remainder release, and async `NotSupported` sync fallback.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/io_dispatcher_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/kv_map.h -->
# sources/storage-engines/rocksdb/util/kv_map.h

Purpose: defines a comparator-aware STL map alias for key/value strings, useful in tests and utilities that need RocksDB comparator ordering rather than `std::string` byte ordering hardcoded by `std::less`.

Important APIs/types/functions: `stl_wrappers::LessOfComparator` stores a `const Comparator*` defaulting to `BytewiseComparator()` and overloads `operator()` for `std::string` and `Slice`. `stl_wrappers::KVMap` is `std::map<std::string, std::string, LessOfComparator>`.

Control flow: map comparisons wrap both inputs in `Slice` where needed and call `Comparator::Compare`, returning true when the result is negative. Construction of the comparator captures the comparator pointer once.

State and persistence behavior: no persistence. Runtime state is only the comparator pointer stored inside the map comparator and the key/value strings stored by `std::map`.

Dependencies/integration points: depends on `rocksdb/comparator.h`, `rocksdb/slice.h`, and standard map/string. It supports code paths that need STL containers to mimic DB key ordering, especially tests with custom comparators.

Risks: the comparator pointer is non-owning and must outlive the map. Changing the comparator object after keys have been inserted would violate `std::map` ordering assumptions. The include of `util/coding.h` is not used directly in this header.

Test signals: no local test file in this subset directly targets `KVMap`; its confidence comes from consumers that instantiate comparator-aware maps in RocksDB tests and utilities.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/kv_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/log_write_bench.cc -->
# sources/storage-engines/rocksdb/util/log_write_bench.cc

Purpose: implements a small gflags-based benchmark that simulates transactional log writes by repeatedly appending fixed-size records, flushing, optionally syncing, pacing writes, and reporting append-plus-flush latency distribution.

Important APIs/types/functions: command-line flags are `num_records`, `record_size`, `record_interval`, `bytes_per_sync`, and `enable_sync`. `RunBenchmark` creates a per-thread log path, configures `EnvOptions` through `Env::OptimizeForLogWrite`, constructs `WritableFileWriter`, appends records, calls `Flush` and optional `Sync`, records `HistogramImpl` latency, and sleeps to maintain the requested interval. Without gflags, `main` prints an install message and exits with code 1.

Control flow: the benchmark parses flags, calls `RunBenchmark`, opens a writable log file, builds a record filled with `X`, then loops `num_records` times. Each iteration measures append/flush/sync latency, periodically prints progress, computes schedule drift from the original start time, and sleeps if ahead of schedule. At the end it prints histogram text to stderr.

State and persistence behavior: writes a temporary benchmark log file under `test::PerThreadDBPath("log_write_benchmark.log")`. It does not delete the file in this source. Runtime state includes writer buffers, histogram buckets, timing values, and configured `bytes_per_sync`.

Dependencies/integration points: depends on gflags compatibility, `WritableFileWriter`, RocksDB `Env`, system clock, `DBOptions`, histogram implementation, and test utilities for per-thread paths. It exercises the same writable-file abstraction used by WAL/log writing paths, but as a standalone tool.

Risks: several I/O statuses are ignored, including file creation, append, flush, and sync results, so benchmark output can be misleading on failures. Pacing uses a simple cumulative schedule and can skip sleeps when writes fall behind. The no-gflags build is only a stub. The benchmark is not a correctness test and may leave files behind.

Test signals: no automated assertions. Useful signals are runtime stderr progress and the final latency histogram when invoked manually with gflags.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/log_write_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/math.h -->
# sources/storage-engines/rocksdb/util/math.h

Purpose: provides inline low-level integer math and bit-manipulation helpers used across RocksDB for hashing, range reduction, bit layouts, encoding support, and fast portable operations.

Important APIs/types/functions: defines `BottomNBits`, `FloorLog2`, `ConstexprFloorLog2`, `CountTrailingZeroBits`, `BitsSetToOne`, `BitParity`, `EndianSwapValue`, `ReverseBits`, `DownwardInvolution`, and typed `BitwiseAnd`. It uses BMI2 intrinsics for `BottomNBits` when available, MSVC intrinsics on Windows, and GCC/Clang builtins elsewhere.

Control flow: most functions select an implementation at compile time based on type size and compiler macros. Builtins handle common 16/32/64-bit cases; fallback code handles byte-swapping and MSVC popcount when required. `DownwardInvolution` applies staged xor shifts/masks from high bits to low bits and is documented as an involutive GF(2) transformation with useful bijection properties.

State and persistence behavior: stateless inline utilities with no memory ownership or persistence. Their outputs may become part of persisted formats when used by hashing, filters, or encoding code, so semantic stability matters even though this header writes nothing itself.

Dependencies/integration points: depends on `port/lang.h`, RocksDB namespace setup, compiler intrinsic headers, and standard type traits. `math128.h` specializes several templates for `Unsigned128`, and `hash_test.cc` is the local regression suite.

Risks: several functions have explicit undefined input domains: `BottomNBits` requires `nbits` smaller than the full width, `FloorLog2` requires positive values, and `CountTrailingZeroBits` requires nonzero values. Signed small types need careful casting to avoid sign-extension surprises; the implementation masks where needed. Platform-specific intrinsic branches must stay semantically aligned.

Test signals: `hash_test.cc` exercises these helpers over many signed and unsigned integral types plus `Unsigned128` specializations, checking bit masks, logs, trailing zeros, popcount, parity, endian swaps, reverse bits, downward involution properties, and typed `BitwiseAnd`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/math.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/math128.h -->
# sources/storage-engines/rocksdb/util/math128.h

Purpose: supplies RocksDB's `Unsigned128` abstraction and 128-bit extensions for math/coding helpers on platforms with or without native `__uint128_t`.

Important APIs/types/functions: defines `Unsigned128` as `__uint128_t` when available or a `{lo, hi}` struct otherwise. The fallback implements shifts, bitwise operators, comparisons, and conversion to <=64-bit integral types. Helper APIs include `Lower64of128`, `Upper64of128`, `Multiply64to128`, specializations of math helpers for `Unsigned128`, `IsUnsignedUpTo128`, `EncodeFixed128`, `DecodeFixed128`, and `EncodeFixedGeneric`/`DecodeFixedGeneric` specializations for 16/32/64/128-bit values.

Control flow: compile-time macros choose native or fallback representation. Fallback shifts split operations across lower and upper halves. `Multiply64to128` uses native multiplication when possible or manual 32-bit limb decomposition otherwise. Specialized bit helpers dispatch to the 64-bit helpers for each half and recombine. Fixed encoding writes lower 64 bits first, then upper 64 bits, matching little-endian fixed coding.

State and persistence behavior: no mutable global state. The fixed 128-bit encode/decode functions define an in-memory and persisted byte layout for callers that store 128-bit values. The fallback struct asserts it has exactly two `uint64_t` words of storage.

Dependencies/integration points: depends on `util/coding_lean.h` and `util/math.h`. Hashing, tests, and generic algorithms use it when they need 128-bit hash values, wide multiplication, or fixed-width 128-bit serialization.

Risks: `TEST_UINT128_COMPAT` can force the fallback path, so both native and fallback semantics must stay aligned. Shift operators mask shift counts by 127, which is intentional behavior but differs from undefined native oversized shifts. Generic encode/decode intentionally static-assert for unsupported sizes. `BitwiseAnd` overloads rely on casts to the smaller participating type.

Test signals: `hash_test.cc` tests `Unsigned128` bitwise operations, comparisons, shifts, popcount/parity helpers, reverse/endian behavior, `DownwardInvolution`, `Multiply64to128`, and fixed/generic encoding and decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/math128.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/murmurhash.cc -->
# sources/storage-engines/rocksdb/util/murmurhash.cc

Purpose: contains RocksDB's copy of MurmurHash2-family implementations selected by architecture: 64-bit MurmurHash64A on x86_64, 32-bit MurmurHash2 on i386, and endian/alignment-neutral MurmurHashNeutral2 elsewhere.

Important APIs/types/functions: implements `MurmurHash64A(const void*, int, unsigned int)`, `MurmurHash2(const void*, int, unsigned int)`, or `MurmurHashNeutral2(const void*, int, unsigned int)` depending on compile target. All use Murmur constants, tail-byte switch statements with intentional fallthrough, and final avalanche mixes.

Control flow: each function initializes the hash from seed and length, processes full machine words or manually assembled 32-bit words, handles remaining tail bytes with a fallthrough switch, and applies final xor/multiply/xor mixing before returning the hash.

State and persistence behavior: stateless pure hash functions. Output width and exact values are architecture-dependent by design through the header macro selection, so persisted users must account for the selected build target if values cross platforms.

Dependencies/integration points: includes `murmurhash.h` and `port/lang.h` for fallthrough annotations. The header exposes `MurmurHash`, `MURMUR_HASH`, `murmur_t`, and a `Slice` hasher, making this implementation available to hash containers and utility code.

Risks: x86_64 and i386 paths perform unaligned word loads and are endian-sensitive, matching original MurmurHash caveats. UBSAN alignment suppression is applied for x86_64 in sanitizer builds. `len` is `int`, so callers must avoid sizes outside that range. The neutral path is slower but safer for strict-alignment or non-little-endian platforms.

Test signals: no dedicated MurmurHash test in this subset. Broader hash stability is covered in `hash_test.cc` for other hash APIs, while Murmur-specific confidence depends on consumers and the original algorithm contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/murmurhash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/murmurhash.h -->
# sources/storage-engines/rocksdb/util/murmurhash.h

Purpose: declares the architecture-selected MurmurHash API and provides a RocksDB `Slice` functor for using MurmurHash in hash-based containers.

Important APIs/types/functions: compile-time branches define `MURMUR_HASH`, `MurmurHash`, and `murmur_t`. On x86_64 they map to `uint64_t MurmurHash64A`; on i386 to `unsigned int MurmurHash2`; otherwise to `unsigned int MurmurHashNeutral2`. `ROCKSDB_NAMESPACE::murmur_hash::operator()` hashes a `Slice` with seed zero and returns `size_t`.

Control flow: inclusion selects declarations and aliases through preprocessor architecture checks. The functor simply passes `slice.data()`, `static_cast<int>(slice.size())`, and seed `0` to the selected implementation.

State and persistence behavior: no state. Hash width varies by target architecture through `murmur_t`, and the functor truncates or widens to `size_t` as the platform dictates.

Dependencies/integration points: includes `<stdint.h>` and `rocksdb/slice.h`. The implementation is in `murmurhash.cc`; consumers include STL or custom hash tables needing `Slice` keys.

Risks: macro aliases can obscure which function is compiled on a given platform. `Slice::size()` is cast to `int`, so very large slices would overflow the API contract. Because algorithms differ by architecture, this should not be used for portable persisted hashes unless the platform is fixed.

Test signals: no direct test in this subset. Any behavior validation comes from consumers using `murmur_hash` plus architecture-specific build coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/murmurhash.h -->
