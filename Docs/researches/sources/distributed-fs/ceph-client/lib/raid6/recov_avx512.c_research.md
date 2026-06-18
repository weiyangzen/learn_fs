# sources/distributed-fs/ceph-client/lib/raid6/recov_avx512.c

Purpose: implements AVX512-accelerated RAID6 recovery with widest x86 vector path.

Important APIs and flow: `raid6_has_avx512()` checks AVX2, AVX, and AVX512F/BW/VL/DQ. Recovery setup mirrors scalar code, then ZMM code uses `vpshufb` against nibble GF tables to compute reconstructed blocks in 64-byte or 128-byte chunks. `raid6_recov_avx512` has priority 3, above AVX2.

State and persistence: temporary `ptrs` mutation is restored; failed data/P buffers are updated; vector state is bracketed with `kernel_fpu_begin/end`.

Dependencies and integration: depends on `raid6_call.gen_syndrome`, vector GF tables, x86 feature checks, and the recovery selector.

Risks and test signals: wide-vector state, alignment, feature gating, and table math are key risks. Signals include recovery tests on AVX512 systems, boot logs selecting `avx512x2/x1`, and fallback when features are missing.
