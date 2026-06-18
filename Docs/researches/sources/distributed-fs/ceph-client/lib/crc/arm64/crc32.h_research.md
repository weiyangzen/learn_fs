# sources/distributed-fs/ceph-client/lib/crc/arm64/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc32.h` dispatches arm64 CRC32, CRC32C, and big-endian CRC32 between generic table implementations, single-stream CRC instructions, and four-way PMULL-combined long-buffer routines.

## Important APIs, Types, and Functions

It declares six assembly functions for single-stream and four-way CRC paths, defines `min_len = 1024`, and provides inline `crc32_le_arch`, `crc32c_arch`, `crc32_be_arch`, and `crc32_optimizations_arch`.

## Control Flow

Each arch wrapper first checks `ARM64_HAS_CRC32`; if absent it calls the generic base function. For buffers at least 1024 bytes, PMULL feature present, and SIMD allowed, it enters `scoped_ksimd()`, processes the rounded-down 64-byte multiple with the four-way routine, advances the pointer, and returns early if no tail remains. Tails and smaller buffers use the single-stream hardware CRC function.

## State and Persistence Behavior

No global mutable state is defined here; runtime feature state is supplied by arm64 alternatives/cpufeature.

## Dependencies and Integration Points

Dependencies include arm64 alternatives, cpufeature, SIMD helpers, generic CRC base functions, and assembly functions in `arm64/crc32-core.S`.

## Risks and Edge Cases

The wrapper must not enter SIMD code when `may_use_simd()` is false. The four-way path must process only full 64-byte chunks and then correctly handle tail bytes. Optimization flags report CRC32 support even when PMULL is absent because single-stream acceleration still exists.

## Test Signals

Signals include generic fallback when CRC32 is absent, hardware CRC path for short buffers, four-way path for >=1024 bytes, tail processing after four-way calls, BE CRC vectors, and `crc32_optimizations()` output.

## Read Coverage

Source read size: 85 lines, 2168 bytes.
