# sources/distributed-fs/ceph-client/lib/crypto/x86/nh-sse2.S

Purpose: SSE2 accelerated NH hash implementation for x86_64.

Important APIs/types/functions: exports `nh_sse2(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`. Macro `_nh_stride` processes one 16-byte stride for four NH passes.

Control flow: initializes pass accumulators and preloads the first key vectors. The main loop handles four 16-byte strides per 64-byte chunk, rotating key registers through `_nh_stride`. Each stride loads message and key words, adds them, shuffles 32-bit values into multiply pairs, uses `pmuludq` for 32x32-to-64 products, and accumulates pass sums. Tail handling processes one to three remaining 16-byte strides. Final reduction packs and adds low/high accumulator lanes into four 64-bit outputs.

State and persistence: no global state; writes caller hash buffer only. Uses XMM registers under FPU context managed by the caller.

Dependencies: SSE2, x86_64 ABI, NH generic contract that `message_len % 16 == 0`, and dispatch in `nh.h`.

Integration points: baseline x86 SIMD path when SSE2 is present and AVX2 is unavailable.

Risks: assumes message/key buffers are valid for the guaranteed multiple-of-16 length. Register-rotation macro is dense; ordering mistakes produce pass-specific mismatches. No `vzeroupper` is needed for SSE-only code.

Test signals: generic-vs-SSE2 differential tests over boundary lengths and randomized keys/messages.
