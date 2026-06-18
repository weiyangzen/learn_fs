# sources/distributed-fs/ceph-client/lib/crc/arm64/crc64.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc64.h` dispatches arm64 CRC64 support, accelerating CRC64-NVME with PMULL while leaving big-endian ECMA CRC64 on the generic path.

## Important APIs, Types, and Functions

It declares `crc64_nvme_arm64_c`, defines `crc64_be_arch` as `crc64_be_generic`, and provides inline `crc64_nvme_arch`.

## Control Flow

For CRC64-NVME, the wrapper checks for length at least 128 bytes, PMULL feature, and allowed SIMD. It processes the 16-byte-aligned prefix with `crc64_nvme_arm64_c()` under `scoped_ksimd()`, advances the pointer, leaves a 0..15 byte tail, and finishes the tail with `crc64_nvme_generic()`. Big-endian CRC64 always uses generic.

## State and Persistence Behavior

No persistent state is defined. Feature state comes from arm64 cpufeature.

## Dependencies and Integration Points

Dependencies include arm64 cpufeature, SIMD helpers, min/max and size headers, the NEON inner C function, and generic CRC64 functions in `crc64-main.c`.

## Risks and Edge Cases

Only the NVME variant is accelerated; callers must not expect ECMA CRC64 acceleration. The wrapper must preserve the generic complementing convention from `crc64-main.c`. SIMD must not be used in disallowed contexts.

## Test Signals

Signals include CRC64-NVME vectors around the 128-byte threshold, tails 1..15, PMULL absent fallback, `may_use_simd()` false fallback, and ECMA CRC64 generic behavior.

## Read Coverage

Source read size: 28 lines, 612 bytes.
