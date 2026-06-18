# sources/distributed-fs/ceph-client/lib/raid6/avx2.c

Purpose: implements x86 AVX2 RAID6 syndrome generation and read-modify-write syndrome update.

Important APIs and flow: `raid6_have_avx2()` checks AVX2 and AVX. `raid6_avx21_*`, `raid6_avx22_*`, and x86-64 `raid6_avx24_*` process 32, 64, or 128 bytes per outer iteration. Generation computes P as XOR of data and Q as GF(2^8) multiply-by-2 recurrence using `0x1d` reduction. `xor_syndrome` updates P/Q over a data subrange with left-side Q advancement. Published `raid6_avx2x1/x2/x4` structures have priority 2.

State and persistence: no durable state; it mutates P and Q buffers and temporarily owns FPU/AVX state.

Dependencies and integration: depends on `x86.h`, boot CPU feature checks, `kernel_fpu_begin/end`, and `raid6_algos[]`.

Risks and test signals: risks include alignment, byte-count multiples, AVX state handling, and GF recurrence errors. Signals are RAID6 boot selection logs, parity-generation tests, recovery tests using AVX2-generated syndromes, and x86-64 versus 32-bit coverage.
