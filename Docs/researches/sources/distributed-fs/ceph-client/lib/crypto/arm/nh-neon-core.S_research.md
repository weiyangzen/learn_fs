# sources/distributed-fs/ceph-client/lib/crypto/arm/nh-neon-core.S

## Purpose
This file implements the NH epsilon-almost-universal hash for ARM32 NEON. NH is used by higher-level keyed hashing constructions that process messages in 64-byte strides.

## Important APIs, Types, And Functions
The exported symbol is `nh_neon(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. The `_nh_stride` macro loads four vectors of key material and message words, performs pairwise additions, multiplies widened 32-bit pairs, and accumulates four pass sums.

## Control Flow
`nh_neon` initializes four 128-bit sum accumulators to zero, loops over 64-byte message strides in `.Lloop4`, and handles a final smaller multiple of the required chunk shape before `.Ldone`. The loop advances key and message pointers together, accumulating low/high halves into four 64-bit sums, then stores four little-endian 64-bit results.

## State And Persistence
State is limited to vector accumulators and caller-provided output. No persistent key schedule or global state is stored.

## Dependencies And Integration Points
It depends on `<linux/linkage.h>` and NEON. `arm/nh.h` calls it only for messages at least 64 bytes and when `may_use_simd()` succeeds; otherwise the generic NH path remains responsible.

## Risks And Edge Cases
Message length assumptions matter: the header filters very short inputs, while the common NH caller must provide lengths aligned to the algorithm contract. Endianness of `__le64` outputs and message word loading must match the generic implementation. Kernel SIMD context protection is required.

## Test Signals
NH vectors, Adiantum or other users of NH, randomized generic-vs-NEON comparisons across boundary lengths near 64 bytes, and ARM32 NEON build/runtime tests are the best signals.
