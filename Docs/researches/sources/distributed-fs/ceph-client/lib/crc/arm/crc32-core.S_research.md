# sources/distributed-fs/ceph-client/lib/crc/arm/crc32-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc32-core.S` provides ARM accelerated CRC32 and CRC32C routines using ARMv8 CRC instructions and PMULL folding.

## Important APIs, Types, and Functions

Exported entry points are `crc32_pmull_le`, `crc32c_pmull_le`, `crc32_armv8_le`, and `crc32c_armv8_le`. The file defines CRC32 and CRC32C PMULL constants and a `__crc32` macro for scalar hardware CRC loops.

## Control Flow

The PMULL routines align the length down to 16-byte multiples, load four vectors, xor the initial CRC into the stream, process 64-byte chunks with carry-less multiplication constants, fold four vectors to one, fold to 64 and then 32 bits, and perform Barrett reduction. The scalar ARMv8 CRC macro handles aligned and unaligned pointers, processes 8-byte pairs through `crc32w`/`crc32cw`, and handles 4/2/1 byte tails with endian fixes under BE8.

## State and Persistence Behavior

The file stores only read-only constants. Per-call state is in general-purpose and NEON registers.

## Dependencies and Integration Points

It depends on ARM assembler support for `.arch_extension crc`, crypto NEON, `linux/linkage.h`, and dispatch from `arm/crc32.h`. The C header handles feature checks, alignment, and SIMD context.

## Risks and Edge Cases

PMULL paths require 16-byte multiple lengths and SIMD permission; scalar paths assume CRC extension availability. Unaligned head and tail handling must match generic CRC32/CRC32C semantics. BE8 byte reversal paths are easy to regress.

## Test Signals

Signals include CRC32 and CRC32C vectors over small tails, unaligned buffers, PMULL threshold lengths, big-endian ARM, generic fallback equivalence, and static-key dispatch coverage.

## Read Coverage

Source read size: 306 lines, 6910 bytes.
