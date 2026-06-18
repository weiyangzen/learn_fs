<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/xxhash.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/xxhash.h

## Purpose
This header is a self-contained xxHash compatibility implementation for the linux-kernel zstd test harness. It provides one-shot and streaming `xxh32`/`xxh64` APIs under kernel-style names so the imported zstd code can compile outside the kernel.

## Important APIs, Types, And Functions
It defines `struct xxh32_state`, `struct xxh64_state`, `xxh32`, `xxh64`, `xxhash`, reset/update/digest routines, and copy-state helpers. Internal helpers implement little-endian reads, rotations, primes, avalanche rounds, and accumulator merge logic.

## Control Flow
One-shot hashes initialize accumulators from the seed, consume 16- or 32-byte stripes, process remaining 4/8/1-byte tails, then avalanche. Streaming update stores short tail bytes in `mem32`/`mem64`, updates large-stripe accumulators when enough bytes arrive, and digest mirrors one-shot finalization.

## State And Persistence
State is entirely caller-owned in the streaming structs: seed, total length, four accumulators, memory size, and a small buffered tail. There is no persistence or allocation.

## Dependencies And Integration Points
The file depends on kernel-style integer/unaligned headers in the test include tree. It supports zstd code paths that use xxHash checksums while running the linux-kernel port tests in user space.

## Risks
Risks are endian and unaligned-access correctness, integer overflow dependence, and divergence from upstream xxHash behavior. Because all functions are `static inline`, ODR/link conflicts are avoided but compiler warnings can hide unused coverage.

## Test Signals
Coverage is indirect through linux-kernel zstd tests and seekable/pzstd checksum users. Strong signals are successful round trips and checksum validation paths that exercise both one-shot and streaming hash usage.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/xxhash.h -->
