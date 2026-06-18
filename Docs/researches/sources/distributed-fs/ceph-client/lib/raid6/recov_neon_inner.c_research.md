# sources/distributed-fs/ceph-client/lib/raid6/recov_neon_inner.c

Purpose: contains the actual ARM NEON RAID6 recovery vector math.

Important APIs and flow: for AArch32, supplies `vqtbl1q_u8()` using two 64-bit table lookups. `__raid6_2data_recov_neon()` loads pbmul/qmul low and high nibble tables, computes `px = p ^ dp`, `qx = qmul[q ^ dq]`, `db = pbmul[px] ^ qx`, stores reconstructed B in `dq` and A in `dp`. `__raid6_datap_recov_neon()` computes `dq = qmul[q ^ dq]` and updates P. Both process 16 bytes per loop.

State and persistence: no durable state; mutates recovery buffers passed by the wrapper. SIMD ownership is handled by the caller.

Dependencies and integration: depends on `<arm_neon.h>` and declarations in `neon.h`.

Risks and test signals: table lookup portability between AArch32 and AArch64 and exact GF nibble math are risks. Signals include NEON recovery tests and build coverage for both ARM modes.
