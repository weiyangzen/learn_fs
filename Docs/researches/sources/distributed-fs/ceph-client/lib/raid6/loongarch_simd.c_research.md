# sources/distributed-fs/ceph-client/lib/raid6/loongarch_simd.c

Purpose: implements LoongArch LSX and LASX RAID6 syndrome generation and xor-syndrome update.

Important APIs and flow: LSX uses 16-byte vectors four at a time; LASX uses 32-byte vectors two at a time. `raid6_lsx_gen_syndrome()` and `raid6_lasx_gen_syndrome()` compute P and Q with vector XOR, byte shift, sign-mask, and `0x1d` reduction. `*_xor_syndrome()` updates a P/Q range and advances Q through left-side data positions. Published `raid6_lsx` and `raid6_lasx` have priority 0 so scalar algorithms remain competitive unless benchmarking chooses SIMD.

State and persistence: no persistence; mutates P/Q and temporarily owns LoongArch FPU/vector state.

Dependencies and integration: depends on `loongarch.h`, CPU feature flags, and `raid6_algos[]`.

Risks and test signals: risks include vector feature gating, priority policy, and GF recurrence correctness. Signals include boot selection logs, LoongArch RAID6 parity tests, and LSX/LASX userspace test builds.
