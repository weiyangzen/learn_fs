# sources/distributed-fs/ceph-client/lib/crc/arm64/crc32-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc32-core.S` implements AArch64 hardware CRC32, CRC32C, big-endian CRC32, and four-way PMULL-combined long-buffer variants.

## Important APIs, Types, and Functions

Exported symbols are `crc32_le_arm64`, `crc32c_le_arm64`, `crc32_be_arm64`, `crc32c_le_arm64_4way`, `crc32_le_arm64_4way`, and `crc32_be_arm64_4way`. Macros include byte/bit order conversion helpers, `__crc32`, and `crc4way`. Constant tables `.L0` and `.L1` hold folding coefficients.

## Control Flow

`__crc32` handles normal hardware CRC processing: it applies bit/byte order transforms for BE mode, handles sub-16 byte tails, processes 32-byte chunks with `crc32x`/`crc32cx`, and returns with order restored. `crc4way` processes long inputs as groups of up to 64 64-byte blocks, splits each group into four contiguous lanes, computes partial CRCs in parallel with hardware CRC instructions, combines them with PMULL coefficients, and loops until all 64-byte blocks are consumed.

## State and Persistence Behavior

State is local to registers and read-only coefficient tables. No mutable global state is stored.

## Dependencies and Integration Points

The file depends on AArch64 CRC and crypto instruction support, assembler macros, and dispatch from `arm64/crc32.h`. The wrapper decides whether CRC and PMULL features are available and handles remaining tails after four-way processing.

## Risks and Edge Cases

The four-way path assumes length in full 64-byte blocks and relies on the caller to process remainders. BE transforms must correctly reverse both bit and byte order. PMULL coefficient table indexing is sensitive to block counts.

## Test Signals

Signals include CRC32 LE, CRC32C, and CRC32 BE vectors, lengths below and above the four-way threshold, non-multiple-of-64 tails via wrapper, PMULL/no-PMULL feature combinations, and comparison to generic tables.

## Read Coverage

Source read size: 357 lines, 9848 bytes.
