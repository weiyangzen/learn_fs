<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.cc -->
# sources/distributed-fs/lizardfs/src/common/block_xor.cc

## Purpose

This file implements in-place XOR of one byte buffer with another, optimized to let the compiler generate vectorized aligned loops when possible.

## Important APIs, Types, and Functions

Public function is `blockXor(uint8_t* dest, const uint8_t* source, size_t size)`. Internal helpers are `blockXorAligned()` and `blockXorUnaligned()`, with `ALIGNMENT` set to 16 and optional `__builtin_assume_aligned`.

## Control Flow

`blockXor()` compares source and destination pointer alignment modulo 16. If they can become jointly aligned, it XORs an unaligned prefix and then calls the aligned loop for the remainder. Otherwise it uses the byte loop for all data.

## State and Persistence Behavior

The function mutates `dest` in-place and has no other state.

## Dependencies and Integration Points

It depends on `massert` for debug assertions. XOR/EC read plans and parity calculations can use this helper.

## Risks and Edge Cases

The test currently passes `v2.data() + i` while varying `j`, so it does not fully exercise differing source/destination alignments. Overlapping buffers are not documented; byte-wise XOR is deterministic for exact same pointer but arbitrary overlaps can produce unintended results.

## Test Signals

`block_xor_unittest.cc` verifies no exceptions/crashes over some offsets and sizes. Stronger tests should compare bytes against a scalar reference across all offset pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.cc -->
