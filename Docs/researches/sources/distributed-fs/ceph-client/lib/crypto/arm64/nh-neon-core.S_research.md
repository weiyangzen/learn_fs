# sources/distributed-fs/ceph-client/lib/crypto/arm64/nh-neon-core.S

## Purpose
This ARM64 ASIMD assembly file implements the NH universal hash fast path.

## Important APIs, Types, And Functions
It exports `nh_neon(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. The `_nh_stride` macro loads message and key vectors, adds them as 32-bit words, widens products, and accumulates pass sums.

## Control Flow
The function initializes four vector accumulators, processes 64-byte strides in `.Lloop4`, handles the final stride path, and stores four 64-bit little-endian hash sums to the output. It advances key and message pointers consistently with the NH pass layout.

## State And Persistence
Only the output hash array is written persistently. Keys and message data are read-only caller inputs.

## Dependencies And Integration Points
It uses Linux linkage macros and ASIMD registers. `arm64/nh.h` gates calls with ASIMD feature detection, minimum message length, and `may_use_simd()`.

## Risks And Edge Cases
Length alignment and short-message handling are delegated to the header/generic caller. Endianness of output and message word interpretation must match generic NH. SIMD context safety is required.

## Test Signals
NH known-answer tests, randomized comparisons with generic NH across boundary lengths, ASIMD feature masking, and users such as Adiantum provide validation.
