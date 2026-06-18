# sources/distributed-fs/ceph-client/lib/crc/arm64/crc64-neon-inner.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc64-neon-inner.c` implements the inner arm64 NEON/PMULL routine for accelerated CRC64-NVME over 16-byte chunks.

## Important APIs, Types, and Functions

The visible function is `crc64_nvme_arm64_c(u64 crc, const u8 *p, size_t len)`. Helpers are `pmull64`, `pmull64_high`, and `pmull64_hi_lo`. Constants `fold_consts_val` and `bconsts_val` hold polynomial reduction values.

## Control Flow

The function loads fold constants and initializes a 128-bit vector with the incoming CRC. It xors each 16-byte block into the accumulator, folds the previous accumulator with carry-less multiplication while more blocks remain, then multiplies the final 128-bit value by `x^64`, reduces it back to 128 bits, performs Barrett reduction using `bconsts`, and returns the high lane as the reflected CRC state.

## State and Persistence Behavior

Only read-only constants are stored. All CRC state is local vector state. The caller owns complementing and tail processing.

## Dependencies and Integration Points

The file depends on arm64 NEON intrinsics and is compiled with FPU/crypto flags by the CRC Makefile. It integrates with `arm64/crc64.h`, which checks PMULL and SIMD availability and handles generic tails.

## Risks and Edge Cases

The function assumes the length is a nonzero 16-byte multiple selected by the wrapper. It uses kernel-mode SIMD, so wrong compile flags or missing SIMD guards would be unsafe. Constants are specific to the NVME reflected CRC64 polynomial, not ECMA big-endian CRC64.

## Test Signals

Signals include CRC64-NVME known vectors, lengths 16, 32, 128, and non-multiple tails through the wrapper, generic equivalence, PMULL feature gating, and build verification that FPU flags are applied only to this object.

## Read Coverage

Source read size: 65 lines, 1714 bytes.
