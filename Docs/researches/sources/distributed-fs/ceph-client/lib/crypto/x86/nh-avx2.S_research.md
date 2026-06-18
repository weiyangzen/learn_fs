# sources/distributed-fs/ceph-client/lib/crypto/x86/nh-avx2.S

Purpose: AVX2 accelerated NH ε-almost-universal hash function for x86_64.

Important APIs/types/functions: exports `nh_avx2(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. Internal macro `_nh_2xstride` processes two NH strides in parallel.

Control flow: the function initializes four pass accumulators, preloads key vectors, and processes 64-byte chunks in a loop. Each stride adds message words to keyed words, shuffles 32-bit pairs, performs unsigned 32x32-to-64 multiplies with `vpmuludq`, and accumulates 64-bit sums for four passes. Remainders of 16, 32, or 48 bytes are handled with partial vector paths; the final single stride zeroes high lanes to avoid incorporating garbage. Horizontal reductions combine vector lanes into four `__le64` pass outputs.

State and persistence: no persistent state; writes only the output hash array. Uses YMM registers and calls `vzeroupper`.

Dependencies: AVX2, x86_64 ABI, key/message alignment tolerance through unaligned loads, and caller-side FPU bracketing.

Integration points: selected by `nh.h` when message length is at least 64 bytes and AVX2 is available.

Risks: message length is guaranteed by caller to be a multiple of 16; violating that would read beyond the valid message. Remainder handling and horizontal sum ordering must match generic NH exactly.

Test signals: NH known-answer/differential tests against generic, especially lengths 16, 32, 48, 64, and non-multiple-of-64 multiples of 16.
