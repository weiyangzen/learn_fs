# subset-b-008703 research

Grouped research report for RocksDB utility sources. Each marked section is source-tree aligned for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c.cc -->
# sources/storage-engines/rocksdb/util/crc32c.cc

Purpose: implements RocksDB's CRC-32C engine behind `util/crc32c.h`, including a portable table-driven fallback, platform-specific fast dispatch, x86 SSE4.2/PCLMUL three-way acceleration, Power8 and Arm64 integration, support probing text, and logarithmic CRC concatenation through `Crc32cCombine`.

Important APIs and functions: `Extend()` is the exported entry point and delegates to static `ChosenExtend`, initialized by `Choose_Extend()`. `ExtendImpl<CRC32>()` is the common byte/alignment loop, using `DefaultCRC32()` for either table or SSE instruction chunks. `ExtendPPCImpl()` and `ExtendARMImpl()` wrap platform implementations. `IsFastCrc32Supported()` reports the compiled/runtime-selected fast path. The x86-only `crc32c_3way()` parallelizes long inputs through three CRC lanes and `_mm_clmulepi64_si128()`. `Crc32cCombine()` converts RocksDB's inverted CRC values to pure CRC space, advances the first CRC over virtual zeroes, cancels the second initializer, and combines with the second CRC.

Control flow: the file starts with lookup tables and low-level chunk helpers, then platform probes, then dispatch. `ExtendImpl()` aligns the pointer, consumes 16-byte and 8-byte chunks, and finishes bytewise. On x86 with SSE4.2 and PCLMUL, `Choose_Extend()` prefers `crc32c_3way()` unless disabled. On Arm/PPC it requires runtime feature checks before using hardware paths. Combine logic uses constexpr GF(2) multiplication tables and `CountTrailingZeroBits()` to advance by powers of zero blocks.

State and persistence: `ChosenExtend` is a process-static function pointer selected at load time. On Arm, global `pmull_runtime_flag` records PMULL availability. On PPC, `arch_ppc_crc32` caches probe result. CRC values are deterministic file-format/state values, so table constants, inversion semantics, masking compatibility, and combine math are persistence-critical.

Dependencies and integration: depends on `util/coding.h`, `util/math.h`, `util/crc32c_arm64.h`, and, on PPC, `crc32c_ppc.*` plus constants. Callers include file checksums, block/data verification, WAL/SST checksum paths, and tests. The code is heavily gated by compiler macros and CPU feature macros.

Risks: static dispatch on x86 assumes binaries are only run where compiled CPU features are valid; runtime detection is explicitly removed there. Unaligned casts are intentionally used in fast paths and need sanitizer suppression. Any change to polynomial constants, inversion, endian handling, or mask semantics breaks stored checksums. Static initialization depends on runtime probe functions being safe during load.

Test signals: `crc32c_test.cc` covers RFC vectors, small/unaligned/large inputs, incremental `Extend()`, masking round trips, and `Crc32cCombine()` over many sizes including a large second input.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c.h -->
# sources/storage-engines/rocksdb/util/crc32c.h

Purpose: public declaration header for RocksDB CRC-32C helpers in `ROCKSDB_NAMESPACE::crc32c`.

Important APIs and types: `IsFastCrc32Supported()` returns a descriptive runtime support string. `Extend(init_crc, data, n)` computes CRC over data appended after an existing CRC. `Crc32cCombine(crc1, crc2, crc2len)` combines two unmasked CRCs without rereading the first string. `Value(data, n)` is the zero-initialized convenience wrapper. `Mask()` and `Unmask()` apply the LevelDB/RocksDB storage masking transform using `kMaskDelta`.

Control flow: this header is mostly inline wrappers. `Value()` calls `Extend(0, ...)`. `Mask()` rotates right 15 bits and adds a fixed delta; `Unmask()` subtracts the delta and rotates back.

State and persistence: no mutable state. The mask transform is persisted anywhere embedded CRCs are stored, so `kMaskDelta` and rotate widths are compatibility-sensitive.

Dependencies and integration: includes standard size/integer headers, `std::string`, and the RocksDB namespace header. It is consumed widely by checksum generation, file readers/writers, block formats, tests, and utility code.

Risks: callers must pass unmasked CRCs to `Crc32cCombine()`. Mixing masked and unmasked values silently produces wrong results. The API accepts raw `char*` and length with no ownership or null protection except implementation-specific behavior.

Test signals: direct coverage appears in `crc32c_test.cc` for values, incremental extension, masking, and combine behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_arm64.cc -->
# sources/storage-engines/rocksdb/util/crc32c_arm64.cc

Purpose: Arm64 CRC-32C hardware implementation and runtime feature probes for CRC32 and PMULL acceleration.

Important APIs/functions: `crc32c_runtime_check()` probes CRC32 instruction support using Linux/FreeBSD auxv, Apple `sysctlbyname`, or OpenBSD CPU ID sysctl. `crc32c_pmull_runtime_check()` similarly checks PMULL/crypto support. `crc32c_arm64(crc, data, len)` computes CRC using Arm CRC intrinsics and optionally a PMULL-assisted 1024-byte parallel path.

Control flow: the file is compiled only under `HAVE_ARM64_CRC`. `crc32c_arm64()` inverts the input CRC, optionally loops over 1024-byte blocks with three parallel lanes and PMULL constants when `pmull_runtime_flag` and `HAVE_ARM64_CRYPTO` are true, then falls back to sequential 8/4/2/1-byte CRC instructions for the tail or for systems without PMULL.

State and persistence: reads external global `pmull_runtime_flag` from `crc32c.cc`, which is set during support checks and dispatch. No persistent storage is written; output must match the generic CRC contract.

Dependencies and integration: depends on `crc32c_arm64.h` for intrinsics/macros, OS feature-probe headers, and Arm NEON/ACLE when enabled. `crc32c.cc` calls this through `ExtendARMImpl()` after `crc32c_runtime_check()`.

Risks: PMULL and CRC32 are separate capabilities; Raspberry Pi-like systems can have CRC32 without PMULL, which this code explicitly handles. It uses unaligned typed pointer loads with sanitizer suppression. Feature probing varies by OS and can return false where support exists but the probing path is unavailable.

Test signals: generic CRC tests exercise this implementation when compiled/run on supported Arm64 hardware; there is no Arm-only unit test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_arm64.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_arm64.h -->
# sources/storage-engines/rocksdb/util/crc32c_arm64.h

Purpose: compile-time Arm64 CRC/crypto capability header exposing intrinsics wrappers, prefetch helpers, and Arm CRC function declarations.

Important APIs/macros: defines `HAVE_ARM64_CRC` when building for AArch64 with `__ARM_FEATURE_CRC32`. Maps `crc32c_u8/u16/u32/u64` to ACLE intrinsics. Defines `PREF4X64L1` and `PREF1KL1` assembly prefetch macros. Declares `crc32c_arm64()`, `crc32c_runtime_check()`, and `crc32c_pmull_runtime_check()`. Defines `HAVE_ARM64_CRYPTO` and includes NEON when `__ARM_FEATURE_CRYPTO` is available.

Control flow: the header gates all declarations behind architecture and feature macros, so non-Arm or non-CRC builds see no functions. The prefetch macros expand to `PRFM PLDL1KEEP` assembly.

State and persistence: no state. Its macro decisions control which code paths are compiled and therefore whether stored CRC-compatible values are produced by hardware or fallback code.

Dependencies and integration: included by `crc32c.cc` and `crc32c_arm64.cc`; depends on `<arm_acle.h>` and `<arm_neon.h>` only when relevant.

Risks: compile-time macro detection must match compiler support. Inline assembly constraints are Arm64-specific. Consumers must not call declarations unless the header exposed them under `HAVE_ARM64_CRC`.

Test signals: indirectly covered by `crc32c_test.cc` on Arm64 builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc.c -->
# sources/storage-engines/rocksdb/util/crc32c_ppc.c

Purpose: C wrapper around the Power8 VPMSUM assembly CRC implementation, with scalar alignment/tail handling and a no-op stub for unsupported builds.

Important APIs/functions: `crc32c_ppc(crc, data, len)` is the exported C ABI. Under `HAVE_POWER8`, `crc32_vpmsum()` handles CRC inversion, 16-byte alignment, assembly call to `__crc32_vpmsum()`, and tail bytes using `crc32_align()`. Under non-Power8 builds, `crc32c_ppc()` exists but returns zero and is not expected to be called.

Control flow: short or unaligned prefixes are processed by table-driven `crc32_align()`. Aligned bulk data is passed to assembly in 16-byte multiples. Tail bytes are processed after assembly. A `NULL` data pointer triggers temporary zero-filled allocation before calculating CRC, a compatibility workaround for assembly behavior.

State and persistence: no retained state. Results must match standard CRC-32C with configured `CRC_XOR` and reflected constants from `crc32c_ppc_constants.h`.

Dependencies and integration: includes `crc32c_ppc_constants.h` with `CRC_TABLE` for scalar fallback constants. Called from `crc32c.cc` through `ExtendPPCImpl()` when Power8/AltiVec feature probing succeeds.

Risks: the unsupported stub returns an invalid checksum if accidentally called. The `NULL` workaround allocates `len` bytes and can be expensive or fail for large lengths. Correctness depends on pointer alignment, endian/reflection macros, and the assembly symbol matching the C declaration.

Test signals: generic CRC tests cover it on Power8 builds. No explicit allocation-failure or null-input test is present in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc.h -->
# sources/storage-engines/rocksdb/util/crc32c_ppc.h

Purpose: C/C++ ABI declaration for the PowerPC CRC-32C implementation.

Important API: declares `uint32_t crc32c_ppc(uint32_t crc, unsigned char const* buffer, size_t len)`, wrapped in `extern "C"` for C++ callers.

Control flow: none; this is a declaration-only header.

State and persistence: no state. The function's output participates in persistent checksum compatibility through `crc32c.cc` dispatch.

Dependencies and integration: includes `<cstddef>` and `<cstdint>`. Used by `crc32c.cc` and implemented by `crc32c_ppc.c`.

Risks: callers rely on build-time/runtime gates to avoid calling the stub implementation on unsupported targets.

Test signals: indirectly covered by CRC tests on PPC-capable builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc_asm.S -->
# sources/storage-engines/rocksdb/util/crc32c_ppc_asm.S

Purpose: PowerPC/Power8 vector assembly implementation of bulk CRC-32C using VPMSUM instructions and Barrett reduction.

Important symbol: exports `__crc32_vpmsum(unsigned int crc, void* p, unsigned long len)`, consumed by `crc32c_ppc.c`. Internal labels handle bulk, short, zero-length, cooldown, and final reduction paths.

Control flow: the function saves GPR and VMX registers, prepares masks/constants, incorporates the initial CRC into vector state, and chooses `.Lshort` for inputs below 256 bytes. Large inputs are processed in MAX_SIZE-bounded blocks using eight parallel 16-byte vector lanes, warm-up/main/cool-down scheduling, tail reduction for 0-112 remaining bytes, and final Barrett reduction. Conditional `BYTESWAP_DATA` selects `vperm` byte swapping based on endianness and reflection.

State and persistence: no persistent state; it preserves nonvolatile registers before returning the CRC in `r3`. Correctness is entirely encoded in constant tables and polynomial/reflection macros.

Dependencies and integration: includes platform assembly helpers (`ppc-asm.h`, `ppc-opcode.h`) and includes `crc32c_ppc_constants.h` in assembly mode. It is linked with the C wrapper only for relevant PowerPC builds.

Risks: high platform sensitivity: ABI register preservation, TOC addressing, endian/reflection modes, and assembler macro compatibility are all critical. The code assumes callers provide aligned bulk ranges after C wrapper preprocessing. Debugging failures can be difficult because most logic is in vector assembly.

Test signals: covered only indirectly by CRC vector tests on Power8 hardware/builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc_constants.h -->
# sources/storage-engines/rocksdb/util/crc32c_ppc_constants.h

Purpose: shared CRC-32C polynomial definitions and lookup/reduction constants for PPC C and assembly paths.

Important definitions: sets `CRC` to `0x1edc6f41`, enables `REFLECT` and `CRC_XOR`, provides `crc_table[]` when `CRC_TABLE` is defined for scalar alignment/tail work, and otherwise emits assembly labels `.constants`, `.short_constants`, and `.barrett_constants`.

Control flow: under non-assembly C usage it provides only the 256-entry table. Under `__ASSEMBLY__` it emits MAX_SIZE and long constant tables for reducing 262144 kbits to 1024 bits, final short reductions, and reflected Barrett constants.

State and persistence: no mutable state. Constants are algorithmic state: any change alters CRC results and breaks compatibility.

Dependencies and integration: included by `crc32c_ppc.c` with `CRC_TABLE` and by `crc32c_ppc_asm.S` with `__ASSEMBLY__`.

Risks: dual C/assembly behavior makes accidental macro changes dangerous. The tables are hard to audit manually; endian/reflection assumptions must stay in sync with assembly.

Test signals: generic CRC vectors and PPC execution are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_ppc_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_test.cc -->
# sources/storage-engines/rocksdb/util/crc32c_test.cc

Purpose: unit test executable for CRC-32C correctness across portable and accelerated implementations.

Important tests: `StandardResults` checks RFC 3720 vectors, deterministic buffer expected results for small aligned/unaligned and large inputs, and verifies incremental `Extend()` matches single-pass `Value()`. `Values`, `Extend`, `Mask`, `Crc32cCombineBasicTest`, `Crc32cCombineOrderMattersTest`, `Crc32cCombineFullCoverTest`, and `Crc32cCombineBigSizeTest` cover API properties and combine math.

Control flow: `main()` initializes GoogleTest and fills a large global buffer with deterministic FNV-derived 64-bit words before running tests. The expected table stores bitwise-inverted values for the three-way implementation checks, so tests compare `~expected.crc32c`.

State and persistence: uses global `buffer` and `expectedResults`. The tests assert stable persisted CRC behavior, mask transform behavior, and combine equivalence.

Dependencies and integration: includes `testharness`, `coding`, and `random`. It validates the implementation selected by build/runtime dispatch rather than directly selecting each backend.

Risks: architecture-specific code is only covered when the test binary runs on that architecture with those compile flags. Expected values are magic constants; failures need interpretation against CRC inversion conventions.

Test signals: this file itself is the strongest signal for CRC implementation correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/crc32c_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/data_structure.cc -->
# sources/storage-engines/rocksdb/util/data_structure.cc

Purpose: out-of-line helpers for RocksDB public/internal data-structure support, specifically small enum-set bit operations.

Important APIs: `detail::CountTrailingZeroBitsForSmallEnumSet(uint64_t)` delegates to `CountTrailingZeroBits()`. `detail::BitsSetToOneForSmallEnumSet(uint64_t)` delegates to `BitsSetToOne()`.

Control flow: both functions are single-call wrappers around `util/math.h` functions.

State and persistence: no state or persistence. Behavior depends only on input bit patterns.

Dependencies and integration: includes `rocksdb/data_structure.h` and `util/math.h`. These wrappers keep some implementation details out of headers while exposing stable functions for small enum set internals.

Risks: minimal. Semantics must remain aligned with the public `data_structure.h` expectations, especially for zero inputs if callers depend on math helper behavior.

Test signals: no direct test in this subset; coverage is likely through users of small enum sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/data_structure.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/defer.h -->
# sources/storage-engines/rocksdb/util/defer.h

Purpose: RAII utilities for deferred scope cleanup and temporary value restoration.

Important types: `Defer` stores a `std::function<void()>` and invokes it in the destructor. `SaveAndRestore<T>` stores a pointer and saved value, optionally assigns a temporary new value, and restores the saved value in the destructor.

Control flow: construction captures cleanup/restoration state; destruction performs the action. Copying is deleted for both types to avoid duplicate cleanup or restoration.

State and persistence: state is process-local RAII state (`fn_`, `obj_`, `saved_`). There is no persistence. `SaveAndRestore` uses move semantics for saved values and restore assignment.

Dependencies and integration: includes `<functional>`, namespace header, and is used wherever RocksDB wants centralized cleanup around early returns or temporary overrides.

Risks: `Defer` destructor invokes user code and is not marked `noexcept`; throwing during stack unwinding would terminate. `SaveAndRestore` requires the pointed object to outlive the guard and be assignable. It is not thread-safe by itself.

Test signals: `defer_test.cc` covers block/function scope execution and basic save/restore.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/defer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/defer_test.cc -->
# sources/storage-engines/rocksdb/util/defer_test.cc

Purpose: unit tests for `Defer` and `SaveAndRestore`.

Important tests: `DeferTest.BlockScope` verifies destructor execution at block exit. `DeferTest.FunctionScope` verifies deferred cleanup runs after lambda body changes state. `SaveAndRestoreTest.BlockScope` verifies original value restoration after mutation inside the guard scope.

Control flow: each test mutates an integer before and after entering a nested scope, relying on RAII destruction at scope exit.

State and persistence: local integer state only; no persistence.

Dependencies and integration: includes `util/defer.h`, port stack trace setup, and GoogleTest harness.

Risks: tests do not cover exception paths, moved/nontrivial types, null pointers, or destructor-throw behavior.

Test signals: confirms the primary RAII semantics used by production callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/defer_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dirty_tracked.h -->
# sources/storage-engines/rocksdb/util/dirty_tracked.h

Purpose: template wrapper that tracks whether an owned value has been mutated so expensive `Reset()` calls can be skipped when clean.

Important type/API: `DirtyTracked<T>` forwards constructor args to `T`, exposes const read access through `operator->` and `operator*`, exposes mutable access through `mut()` which marks dirty, and `Reset()` calls `value_.Reset()` only when dirty.

Control flow: reads never affect dirty state. Mutations must go through `mut()`. `Reset()` short-circuits unless `dirty_` is true, then clears the flag after resetting the value.

State and persistence: stores `T value_` and `bool dirty_`; no persistence. Dirty state is an optimization hint inside the owning object.

Dependencies and integration: includes `<utility>` and RocksDB namespace. Intended for hot paths where rarely populated helper objects would otherwise allocate or clear unnecessarily.

Risks: correctness depends on all mutations using `mut()`. The wrapper is explicitly not thread-safe. `T` must provide `void Reset()`.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dirty_tracked.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/distributed_mutex.h -->
# sources/storage-engines/rocksdb/util/distributed_mutex.h

Purpose: optional abstraction over folly `DistributedMutex`, falling back to RocksDB's port mutex when folly is unavailable.

Important APIs/types: with `USE_FOLLY`, defines `DMutex` as a subclass of `folly::DistributedMutex` with `kName()` and no-op `AssertHeld()`, plus `DMutexLock = std::lock_guard<folly::DistributedMutex>`. Without folly, aliases `DMutex = port::Mutex` and `DMutexLock = std::lock_guard<DMutex>`.

Control flow: entirely compile-time through `USE_FOLLY`.

State and persistence: mutex state is in-memory synchronization only; no persistence.

Dependencies and integration: includes folly synchronization when available, otherwise `<mutex>` and `port/port.h`. Integration point is code wanting scoped locking while allowing deployments to choose a lower-contention mutex.

Risks: only scoped locking is supported because lock/unlock APIs differ. `AssertHeld()` is a no-op in the folly path, so code must not rely on it for diagnostics. Behavioral/performance differences between fallback and folly can hide concurrency issues.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/distributed_mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/duplicate_detector.h -->
# sources/storage-engines/rocksdb/util/duplicate_detector.h

Purpose: recovery-time helper that emulates memtable duplicate key/sequence detection when a memtable flush prevents normal insertion-based duplicate detection.

Important type/API: `DuplicateDetector` owns a `DBImpl*`, current `batch_seq_`, and a map from column family id to `std::set<Slice, SetComparator>`. `IsDuplicateKeySeq(cf, key, seq)` returns true when the same key appears twice for the same sequence batch.

Control flow: asserts `seq >= batch_seq_`; a new sequence clears all tracked keys. For each column family, it lazily initializes the set comparator from the DB column family handle. On duplicate insertion, it clears/reinitializes tracking for that CF, reinserts the key, and reports true.

State and persistence: in-memory per-recovery-batch state only. It stores `Slice` objects, so key memory lifetime must exceed tracking use.

Dependencies and integration: depends on `DBImpl`, logging, `SetComparator`, column family handles, sequence numbers, and RocksDB logging/status conventions. It is intended for WAL recovery logic.

Risks: dropped column family during recovery logs fatal and throws. Slice lifetime is critical. The class is not thread-safe. Clearing all keys on new batch assumes sequence changes exactly delimit duplicate-detection windows.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/duplicate_detector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dynamic_bloom.cc -->
# sources/storage-engines/rocksdb/util/dynamic_bloom.cc

Purpose: constructor implementation for `DynamicBloom`, allocating and aligning the in-memory Bloom bit array.

Important functions: local `roundUpToPow2()` supports layout sizing. `DynamicBloom::DynamicBloom()` validates probe count, computes block size/bit rounding so XOR-offset double probes stay in range, allocates aligned memory through an `Allocator`, zeroes it, then adjusts `data_` to a block boundary.

Control flow: `num_probes` must be even and at most 10. Total bits are rounded up to whole probe-safe blocks. Allocation includes padding for alignment correction. Debug builds assert last-word XOR probes remain in range.

State and persistence: initializes immutable `kLen`, `kNumDoubleProbes`, and zeroed `RelaxedAtomic<uint64_t>* data_`. The filter is explicitly in-memory only and not schema/persistence stable.

Dependencies and integration: uses `memory/allocator.h`, `port/port.h`, `rocksdb/slice.h`, and hash utilities. Called by table/plain-table and memory-resident filter code.

Risks: requires non-null allocator and enough memory. Constructor uses asserts rather than runtime errors for invalid probe counts. Alignment math is integral to preventing out-of-bounds XOR probe offsets.

Test signals: `dynamic_bloom_test.cc` covers empty/small filters, false-positive behavior, and concurrent add/query behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dynamic_bloom.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dynamic_bloom.h -->
# sources/storage-engines/rocksdb/util/dynamic_bloom.h

Purpose: high-speed in-memory Bloom filter with optional lock-free concurrent insertion and batch lookup support.

Important APIs/types: `DynamicBloom` supports `Add`, `AddConcurrently`, `AddHash`, `AddHashConcurrently`, `MayContain`, batch `MayContain`, `MayContainHash`, and `Prefetch`. Internally, `DoubleProbe()` and templated `AddHash()` implement two bit probes per 64-bit word.

Control flow: keys are hashed with `BloomHash()`. `FastRange32()` maps the 32-bit hash to a base word, then `a ^ i` addresses subsequent double-probe words. A 64-bit golden-ratio multiply expands the hash; each iteration tests or sets two bits and rotates by 12 bits for the next pair. Batch lookup precomputes hashes and prefetches words before checking.

State and persistence: stores `kLen`, `kNumDoubleProbes`, and relaxed atomic word array. It is explicitly not serialized for compatibility. Concurrent adds use relaxed fetch-or to avoid races and lost bits but require external happens-before for visibility semantics.

Dependencies and integration: depends on `Slice`, `MultiGetContext`, `RelaxedAtomic`, `BloomHash`, `FastRange32`, and prefetch macros. It integrates with in-memory filters and multi-get lookup paths.

Risks: false-positive rate trades accuracy for speed; requires even `num_probes <= 10`. A poor or mismatched 32-bit hash would degrade distribution. Single-threaded `AddHash()` is not race-safe. Batch arrays assume `num_keys <= MultiGetContext::MAX_BATCH_SIZE`.

Test signals: `dynamic_bloom_test.cc` exercises correctness, false-positive thresholds, perf modes, and concurrent operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dynamic_bloom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dynamic_bloom_test.cc -->
# sources/storage-engines/rocksdb/util/dynamic_bloom_test.cc

Purpose: GoogleTest/gflags-based validation and optional performance testing for `DynamicBloom`.

Important tests: `EmptyFilter`, `Small`, and `SmallConcurrentAdd` validate basic membership behavior. `VaryingLengths` inserts up to hundreds of thousands or perf-mode tens of millions of sequential/non-sequential keys and checks false positive rates. `perf` measures add/query latency when enabled. `concurrent_with_perf` uses four threads for concurrent adds, hits, and miss/false-positive measurement.

Control flow: if `GFLAGS` is unavailable, the executable prints a skip message and returns success. With gflags, command-line flags control bits per key, probes, and perf scale. `KeyMaker` creates sequential and non-sequential key slices backed by object fields.

State and persistence: tests use arena-backed in-memory filters and local counters/timers; no persistence.

Dependencies and integration: includes `dynamic_bloom.h`, arena, port threads, system clock, gflags compatibility, test harness, and stopwatch utilities.

Risks: probabilistic false-positive checks can be sensitive to hash/filter changes. Perf mode can allocate/process very large filters. Sequential-key cases can hide 32-bit hash weaknesses, which comments explicitly note.

Test signals: strong direct signal for DynamicBloom correctness and approximate FP-rate expectations, conditional on gflags availability.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/dynamic_bloom_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/fastrange.h -->
# sources/storage-engines/rocksdb/util/fastrange.h

Purpose: fast alternative to modulo for mapping uniformly distributed 32-bit or 64-bit hashes into a range.

Important APIs/types: `FastRangeGeneric<Hash, Range>()` delegates to specialized `FastRangeGenericImpl`. `FastRange32(uint32_t, uint32_t)` and `FastRange64(uint64_t, size_t)` are the recommended wrappers.

Control flow: 32-bit mapping multiplies `range * hash` into 64 bits and returns the high 32 bits. 64-bit mapping uses `__uint128_t` when available or a decomposed 64x64-to-high64 multiplication fallback.

State and persistence: no state. Results are deterministic but depend on input hash width; this matters for in-memory layout and probabilistic structures, not persisted formats here.

Dependencies and integration: includes type traits and namespace. Used by DynamicBloom, filter benchmarks, hash helpers, and any code mapping hash values to buckets.

Risks: using `FastRange64` on a 32-bit-quality hash can produce very poor distribution, often near zero; comments warn the templated form can hide this mistake. Range type must be unsigned and no wider than hash type.

Test signals: no direct test in this subset, but DynamicBloom/filter benchmark exercise practical use.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/fastrange.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/file_checksum_helper.cc -->
# sources/storage-engines/rocksdb/util/file_checksum_helper.cc

Purpose: implementation of default file checksum list storage and checksum generator factory registration/loading.

Important APIs/functions: `FileChecksumListImpl::{reset,size,GetAllFileChecksums,SearchOneFileChecksum,InsertOneFileChecksum,RemoveOneFileChecksum}` manage an in-memory map. `NewFileChecksumList()` returns a new implementation. `GetFileChecksumGenCrc32cFactory()` returns a static shared default factory. `FileChecksumGenFactory::CreateFromString()` registers built-ins once and loads either the default CRC32C factory or a shared-object factory.

Control flow: list methods validate output pointers where relevant, use unordered_map lookup/insert/erase, and return `Status::NotFound()` for missing files. Factory creation uses `std::call_once()` to register `FileChecksumGenCrc32cFactory` in `ObjectLibrary`.

State and persistence: `FileChecksumListImpl` keeps in-memory file-number to checksum/name pairs. `GetFileChecksumGenCrc32cFactory()` and factory registration use process-static state. Actual checksum bytes are persisted by callers.

Dependencies and integration: depends on `file_checksum_helper.h`, `customizable_util.h`, `ObjectLibrary`, and `LoadSharedObject`. Integrated with options/config parsing and SST file checksum generation.

Risks: `GetAllFileChecksums()` iteration order is unordered. Pointer validation prevents null writes but insert accepts any checksum/name content. Shared object loading can fail based on config/environment.

Test signals: no direct test in this subset; `file_reader_writer_test.cc` exercises checksum handoff at writer level.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/file_checksum_helper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/file_checksum_helper.h -->
# sources/storage-engines/rocksdb/util/file_checksum_helper.h

Purpose: declares default CRC32C file checksum generator and in-memory file checksum list implementation.

Important types/APIs: `FileChecksumGenCrc32c` implements `FileChecksumGenerator` with `Update()`, `Finalize()`, `GetChecksum()`, and `Name()`. `FileChecksumGenCrc32cFactory` creates the generator when no checksum name or `"FileChecksumCrc32c"` is requested. `FileChecksumListImpl` implements CRUD/list APIs over file-number checksums.

Control flow: `Update()` extends running CRC32C. `Finalize()` stores the checksum as big-endian raw bytes via `PutFixed32(EndianSwapValue(checksum_))`. `GetChecksum()` asserts finalization occurred.

State and persistence: generator stores `uint32_t checksum_` and finalized string. The byte order and algorithm name are persisted/externally visible through file checksum metadata. List implementation stores map entries in memory.

Dependencies and integration: depends on public `rocksdb/file_checksum.h`, coding, CRC32C, and math endian helpers. Used by DB/file writing options as the default SST file checksum method.

Risks: calling `GetChecksum()` before `Finalize()` or `Finalize()` twice triggers assertions. Changing endian storage would break compatibility with existing checksum consumers. Factory matching is string-based.

Test signals: writer checksum handoff in `file_reader_writer_test.cc`; direct generator tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/file_checksum_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/file_reader_writer_test.cc -->
# sources/storage-engines/rocksdb/util/file_reader_writer_test.cc

Purpose: broad file reader/writer behavior test suite covering `WritableFileWriter`, readahead readers, line reader, checksum handoff, error notification, and I/O priority propagation.

Important tests: `RangeSync` validates bytes-per-sync aligned range sync scheduling. `IncrementalBuffer`, `AlignedBufferedWrites`, and `BufferWithZeroCapacityDirectIO` cover buffering/direct I/O constraints. `AppendWithChecksum`, `AppendVerifyNoChecksum`, and `AppendWithChecksumRateLimiter` exercise CRC32C append verification/handoff with fault-injection FS and rate limiting. `AppendStatusReturn` checks append error propagation. Readahead random/sequential parameterized tests validate empty, short, long, and over-readahead reads. `LineFileReaderTest` validates line counting and injected read errors. `IOErrorNotification` checks listener callbacks. `WritableFileWriterIOPriorityTest` checks priority propagation across operations.

Control flow: many tests define local fake `FSWritableFile` implementations to assert calls and simulate errors. DB-backed tests use `DBTestBase`, `FaultInjectionTestFS`, and `WritableFileWriter`. Parameterized tests instantiate multiple readahead sizes.

State and persistence: uses temporary DB/test files, memory strings, injected FS state, and listener counters. It verifies behavior that affects persisted file contents and checksums but does not define new storage formats.

Dependencies and integration: integrates file system abstractions, DB options, CRC32C, rate limiter, event listeners, mock env, string test sources/sinks, and sync point fault injection.

Risks: fake file implementations may not capture all filesystem behavior. Some tests depend on random data but fixed seeds. Fork/process lock behavior is not here; that is in `filelock_test.cc`.

Test signals: strong regression signal for file I/O wrappers, buffering, read-ahead, checksum handoff, and listener semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/file_reader_writer_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/filelock_test.cc -->
# sources/storage-engines/rocksdb/util/filelock_test.cc

Purpose: verifies RocksDB environment file lock behavior, especially same-thread re-lock failure and OS-level lock visibility.

Important APIs/tests: `LockTest` wraps `Env::LockFile()` and `Env::UnlockFile()`. `CheckFileLock()` forks a child on non-Windows systems, attempts an `fcntl(F_SETLK)` write lock, and interprets success/failure according to expected lock state. `LockBySameThread` acquires a lock, verifies contention, attempts duplicate lock, checks error status/message, then unlocks and verifies release.

Control flow: child process opens the lock file and attempts an advisory whole-file write lock. Parent waits for child exit status. Windows path currently returns true as a TODO stub.

State and persistence: uses a per-thread test path and OS file lock state. No durable data beyond the lock file.

Dependencies and integration: includes Env/Status, POSIX `fcntl`, wait headers for BSD variants, coding/string utilities, and test harness.

Risks: fork-based checks are POSIX-specific; Windows does not validate actual lock behavior. Advisory lock semantics differ by filesystem. Same-process file descriptor behavior motivates using a child process.

Test signals: direct signal that Env lock implementation prevents duplicate locks and exposes thread ID in non-Windows error messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/filelock_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/filter_bench.cc -->
# sources/storage-engines/rocksdb/util/filter_bench.cc

Purpose: gflags-driven benchmark and validation tool for RocksDB Bloom-like filter implementations, full-filter readers, and plain-table Bloom filters.

Important types/functions: `KeyMaker` generates varied keys with optional alignment/size variation. `FilterInfo` stores built filter data/readers and FP counters. `FilterBench` extends `MockBlockBasedTableTester`; `Go()` builds filters, verifies no false negatives and acceptable FP rate, then runs query workloads. `RandomQueryTest()` measures gross/dry-run query time for single, batched, random, and skewed filter selection modes.

Control flow: if gflags is unavailable, executable returns an error. Flags choose implementation, memory/key limits, bits per key, batch size, reader interface, cache charging, quick/best-case modes, and runs. Build phase repeatedly creates filters until memory/key target. Verification checks inside keys and outside FP rate. Query phase compares real filter time to dry-run hashing/testing overhead.

State and persistence: benchmark-only in-memory state: arenas, filter buffers, readers, random seed, FP reports, optional block cache. No persistence.

Dependencies and integration: includes table filter internals, mock block table tester, plain-table Bloom, cache, arena, hash/fastrange, random, stopwatch, gflags compatibility, and stderr logger.

Risks: benchmark results are sensitive to compiler optimization, assertions, CPU cache, malloc usable size, and flag combinations. Some flag combinations throw runtime errors. FP assertions are probabilistic unless `allow_bad_fp_rate` is set.

Test signals: not a unit test by default but useful performance/FP-rate signal for filter implementation changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/filter_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/gflags_compat.h -->
# sources/storage-engines/rocksdb/util/gflags_compat.h

Purpose: compatibility shim for differences across gflags versions.

Important definitions: includes `<gflags/gflags.h>`, defines `GFLAGS_NAMESPACE` as `google` if older gflags did not define it, and defines fallback `DEFINE_uint32`/`DECLARE_uint32` in terms of `DEFINE_int32` plus a `uint32_t&` alias.

Control flow: compile-time macro fallback only.

State and persistence: gflags globals are process state only. The fallback creates an internal int32 flag and exposes a reinterpret-cast uint32 reference.

Dependencies and integration: used by tests/benchmarks needing portable gflags APIs, including `dynamic_bloom_test.cc` and `filter_bench.cc`.

Risks: the fallback `uint32_t&` alias relies on representation-compatible reinterpretation of an int32 flag, which is pragmatic but not type-safe. Negative command-line values could map unexpectedly through unsigned access.

Test signals: indirectly exercised by gflags-dependent tests/benchmarks when built with older gflags.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/gflags_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash.cc -->
# sources/storage-engines/rocksdb/util/hash.cc

Purpose: implementation of RocksDB common non-cryptographic hash functions, including legacy 32-bit MurmurHash1, XXH3-based 64/128-bit hashes, slice-part hashing, and bijective 128-bit mixing/unmixing helpers.

Important APIs/functions: `Hash()` implements persistent 32-bit MurmurHash1-compatible hashing. `Hash64()` delegates to `XXPH3_64bits(_withSeed)`. `GetSlicePartsNPHash64()` concatenates slice parts and hashes them. `Hash128()` wraps XXH3 128-bit output into `Unsigned128`. `Hash2x64()` returns high/low 64-bit halves. `BijectiveHash2x64()` and `BijectiveUnhash2x64()` implement invertible 128-bit transformations adapted from XXH3 small-input mixing. `kGetSliceNPHash64UnseededFnPtr` is initialized to `GetSliceHash64`.

Control flow: `Hash()` processes 4-byte little-endian chunks, then a switch over 0-3 trailing bytes using `int8_t` casts to preserve legacy sign-extension behavior without UB. 64/128-bit functions call xxhash variants. Bijective hash/unhash uses fixed secrets, multiplication to/from 128-bit, endian swaps, avalanche/unavalanche, and modular inverse constants.

State and persistence: persistent hash functions define stable values used in formats/data structures; comments distinguish stable `Hash64`/`Hash` from non-persistent wrappers in the header. Global function pointer is process state.

Dependencies and integration: depends on `coding`, `hash128.h`, `math128.h`, `xxhash`, `xxph3`, and `port/lang.h`. Used by Bloom filters, cache/hash containers, partitioning, and benchmarks.

Risks: legacy 32-bit behavior intentionally preserves signed-char quirks; changing it would break persistent compatibility. `GetSlicePartsNPHash64()` copies all parts and can allocate. Seed sequences differing by one may not be independent.

Test signals: no direct hash test in this subset; dynamic Bloom and filter benchmark exercise hash use indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash.h -->
# sources/storage-engines/rocksdb/util/hash.h

Purpose: public/internal convenience declarations and wrappers for RocksDB hash functions.

Important APIs/types: declares stable `Hash64`, `Hash`, `Hash2x64`, `BijectiveHash2x64`, inverse helpers, `GetSlicePartsNPHash64`, and slice convenience wrappers. Inline `NPHash64` variants currently delegate to `Hash64` unless `ROCKSDB_MODIFY_NPHASH` is defined. `BloomHash()` is the legacy 32-bit Bloom hash. Provides `SliceHasher32` and `SliceNPHasher64` functors plus `Upper32of64`/`Lower32of64`.

Control flow: mostly inline dispatch to out-of-line implementations. `ROCKSDB_MODIFY_NPHASH` intentionally perturbs non-persistent hash output for tests. `GetSliceRangedNPHash()` uses `FastRange64()`.

State and persistence: no owned state except declaration of global function pointer. Comments define persistence contracts: `Hash`/`Hash64` stable, `NPHash64` not for persisted data.

Dependencies and integration: includes `rocksdb/slice.h` and `fastrange.h`. Used broadly by filters, hash containers, memtables, caches, and benchmarks.

Risks: confusing persistent vs non-persistent hash APIs can lead to stored data depending on changeable hashes. `BloomHash()` uses a fixed seed and legacy 32-bit quality. FastRange wrapper requires quality 64-bit hashes.

Test signals: indirect through Bloom/filter tests; no direct test in subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash128.h -->
# sources/storage-engines/rocksdb/util/hash128.h

Purpose: lightweight 128-bit hash declaration header separated from `hash.h` to avoid pulling `math128.h` into the common hash header.

Important APIs: declares `Unsigned128 Hash128(const char*, size_t, uint64_t seed)` and unseeded overload; provides `GetSliceHash128(const Slice&)`.

Control flow: `GetSliceHash128()` directly calls `Hash128()` with slice data/size.

State and persistence: no state. The declared hash is stable/persistent for non-cryptographic use.

Dependencies and integration: includes `rocksdb/slice.h` and `util/math128.h`; implemented in `hash.cc`.

Risks: consumers must treat it as non-cryptographic despite 128-bit width. Changes to implementation would affect persistent users.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash128.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash_containers.h -->
# sources/storage-engines/rocksdb/util/hash_containers.h

Purpose: compile-time abstraction for unordered map/set implementations, allowing folly F14 containers when available and standard containers otherwise.

Important aliases: under `USE_FOLLY`, `UnorderedMap`, `UnorderedMapH`, and `UnorderedSet` alias `folly::F14FastMap/F14FastSet`. Otherwise they alias `std::unordered_map` and `std::unordered_set`.

Control flow: compile-time macro selection only.

State and persistence: no state. Container choice affects in-memory performance and iteration/order characteristics, not persistent format.

Dependencies and integration: includes RocksDB namespace and either folly F14 headers or standard unordered containers. Used by code wanting a centralized hash-container choice.

Risks: folly and std containers differ in performance, memory layout, iterator invalidation details, and possibly iteration order. Code should not depend on container-specific behavior beyond unordered associative semantics.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash_containers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash_map.h -->
# sources/storage-engines/rocksdb/util/hash_map.h

Purpose: small fixed-bucket hash map optimized to reduce allocations by storing collision chains in `autovector` rather than node-based lists.

Important type/API: template `HashMap<K, V, size=128>` provides `Contains(K)`, `Insert(K, const V&)`, `Delete(K)`, and `Get(K)` over an array of `autovector<std::pair<K,V>,1>` buckets.

Control flow: all operations compute `key % size` to pick a bucket and linearly scan with `std::find_if`. `Delete()` replaces the removed element with the last element in the bucket before popping. `Get()` returns `it->second` without checking for missing keys.

State and persistence: in-memory fixed bucket array only. No resizing, hashing object, or persistence.

Dependencies and integration: includes `<algorithm>`, `<array>`, `<utility>`, and `util/autovector.h`. Suitable for small integer-key maps where allocation avoidance matters.

Risks: requires `K` to support `% size` and equality. `Insert()` does not check duplicates, so repeated keys can coexist and `Get/Delete` affect the first found. `Get()` is unsafe for absent keys. Fixed bucket count can degrade badly with poor key distribution.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/util/hash_map.h -->
