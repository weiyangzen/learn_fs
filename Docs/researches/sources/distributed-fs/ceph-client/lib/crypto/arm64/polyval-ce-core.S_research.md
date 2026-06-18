# sources/distributed-fs/ceph-client/lib/crypto/arm64/polyval-ce-core.S

## Purpose
ARMv8 Crypto Extensions implementation of POLYVAL multiplication and block evaluation using PMULL.

## Important APIs, Types, And Functions
Exports `polyval_mul_pmull(struct polyval_elem *a, const struct polyval_elem *b)` and `polyval_blocks_pmull(struct polyval_elem *acc, const struct polyval_key *key, const u8 *data, size_t nblocks)`. Major macros are `karatsuba1`, `karatsuba1_store`, `karatsuba2`, `montgomery_reduction`, `full_stride`, and `partial_stride`.

## Control Flow
Single multiplication loads two 128-bit elements, performs Karatsuba polynomial multiplication, reduces modulo `x^128 + x^127 + x^126 + x^121 + 1`, and stores back to `a`. Block processing loads an accumulator and precomputed powers `h^8` through `h^1`, consumes full 8-block strides with interleaved multiplication and one reduction per stride, then handles remaining partial blocks before storing the accumulator.

## State, Persistence, And Dependencies
The accumulator is updated in caller memory. Key powers are read-only input supplied by the generic POLYVAL key setup. The code requires ARMv8 crypto/PMULL instructions and Linux linkage macros.

## Integration Points
This is the acceleration backend for POLYVAL users such as AES-GCM-SIV style authentication in the kernel crypto library.

## Risks
The finite-field representation is Montgomery-style and easy to misuse; key-power order, endian assumptions, and block-count tail handling are the high-risk areas. Register aliases are dense, so ABI clobbering or macro edits can silently corrupt authentication tags.

## Test Signals
POLYVAL known-answer tests should compare generic and PMULL paths for 0, 1, 7, 8, 9, and many-block inputs, with randomized key powers and accumulator seeds.
