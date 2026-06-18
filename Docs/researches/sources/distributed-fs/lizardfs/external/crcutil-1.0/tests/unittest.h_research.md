<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.h

## Purpose
Core crcutil unittest framework. It wraps generic CRC implementations, verifies algebraic and algorithmic invariants, benchmarks algorithm variants, sorts performance results, and manages aligned placement for verifier instances.

## Important APIs, Types, and Functions
Important types are `GenericCrcTest`, `CrcVerifierInterface`, `AlgSorter`, `PerfTestState`, `RollingCrcTest`, `CrcTest`, `CrcVerifierFactoryInterface`, `CrcVerifier`, and `CrcVerifierFactory`. Key methods include `InitWithCrc32c`, `VerifyPow`, `VerifyCrcZeroes`, `VerifyChangeStartValue`, `VerifyConcatenate`, `VerifyCb`, `VerifyLCD`, `VerifyCrcOfCrc`, `VerifyDistribution`, `VerifyRollingCrc`, `TestFunctionality`, `PerfTestMeasure`, `PerfTestVariants`, `PerfTestRun`, and `TestPerformance`. `CreateTest` registers paired canonical/raw and stride variants.

## Control Flow, State, and Persistence
`CrcVerifier` stores factories, allocates one maximum-sized aligned scratch block, placement-news each test into that memory, runs all functionality tests first, then benchmarks factories marked for performance. `CrcTest::TestFunctionality` validates byte, word, blockword, multiword, SSE4 CRC32C fast path, rolling CRC, start-value transforms, concatenation, CRC-of-CRC, and distribution behavior against slower reference paths. Performance uses a 64 MiB random buffer, sizes from 4 bytes to 64 MiB, `Rdtsc::Get`, repeated trials, and `PerfTestState` to print CSV rows plus best-method summaries. State is in heap-allocated factory objects, aligned scratch memory, temporary performance buffers, and in-memory performance aggregation maps.

## Dependencies and Integration Points
Depends on crcutil `aligned_alloc.h`, `bob_jenkins_rng.h`, `crc32c_sse4.h`, `generic_crc.h`, `rdtsc.h`, `rolling_crc.h`, and `unittest_helper.h`. It bridges generic CRC templates and optional hardware CRC32C acceleration by creating a placement-new `Crc32cSSE4_Test` when degree, polynomial, stride, word size, and CPU support match.

## Risks and Test Signals
Risks include very high memory/time cost, reliance on non-serialized cycle counters, possible undefined behavior if placement-new objects require destructors that are not called, raw `new` ownership in factory arrays, platform-specific compiler workarounds, and a likely `delete[] buf` bug after the pointer has been alignment-adjusted away from `buf0` in `TestPerformance`. Test signals are `--noperf` functional success, deterministic CHECK failures on any CRC mismatch, performance CSV rows with nonzero timings on x86, ASan/UBSan around aligned allocation and buffer deletion, and conditional SSE4/int128 execution only on supported builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.h -->
