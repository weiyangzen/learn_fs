## sources/distributed-fs/ceph-client/lib/raid6/sse2.c

Purpose: provides SSE2 RAID-6 syndrome generation and xor-syndrome update implementations for x86. It registers plain, unrolled-by-2, and on x86_64 unrolled-by-4 algorithms.

Important APIs/functions: `raid6_have_sse2()` checks MMX, FXSR, XMM, and XMM2. Public `raid6_calls` are `raid6_sse2x1`, `raid6_sse2x2`, and `raid6_sse2x4` on 64-bit. Each variant provides both `gen_syndrome` and `xor_syndrome`.

Control flow: syndrome generation loops by 16, 32, or 64 bytes. It initializes P/Q accumulators and applies GF multiply-by-two with `pcmpgtb`, `paddb`, mask `0x1d`, and XOR. Xor-syndrome uses the `start`/`stop` range to update parity for read-modify-write flows: it XORs affected data into P, computes Q contribution through the affected range, advances Q over unaffected lower disks, then XORs with existing Q. Non-temporal stores are used where appropriate, with comments avoiding them for small read/write areas in some variants.

State and persistence: no persistent state; parity buffers are overwritten or updated in place. SIMD state is protected with `kernel_fpu_begin/end()`.

Dependencies/integration: depends on `linux/raid/pq.h`, `x86.h`, inline SSE2 assembly, and the generic RAID-6 algorithm registry. `raid6_sse_constants.x1d` is the aligned GF reduction constant.

Risks/test signals: the code is register-heavy and architecture-specific, so risks include clobber omissions, alignment assumptions, and parity update divergence between unroll variants. `raid6/test/test.c` stresses generation, recovery, and xor-syndrome read-modify-write simulations.
