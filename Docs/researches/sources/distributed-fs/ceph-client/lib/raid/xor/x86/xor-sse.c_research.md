# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-sse.c

Purpose: implements SSE and prefetch64-SSE XOR templates for x86.

Important APIs and flow: `xor_sse_{2,3,4,5}` and `xor_sse_{2,3,4,5}_pf64` process 256-byte chunks using `movaps`, `xorps`, and `prefetchnta`, with macro-expanded schedules for each source count. `DO_XOR_BLOCKS()` creates `xor_gen_sse_inner()` and `xor_gen_sse_pf64_inner()`, wrapped with `kernel_fpu_begin/end` and exported as `xor_block_sse` and `xor_block_sse_pf64`.

State and persistence: no persistence; in-place destination mutation and temporary FPU/SSE state ownership.

Dependencies and integration: registered by x86 selection on x86-64 or XMM-capable 32-bit CPUs when AVX is not forced.

Risks and test signals: risks include alignment assumptions for `movaps`, prefetch behavior, and register constraints across 32/64-bit modes. Signals include KUnit XOR tests, boot calibration comparing SSE variants, and RAID parity workloads.
