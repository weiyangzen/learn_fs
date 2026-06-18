# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-t10dif.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc-t10dif.h` dispatches CRC-T10DIF on PowerPC to VMX/VPMSUM acceleration when vector crypto is available.

## Important APIs, Types, and Functions

It defines `VMX_ALIGN`, `VMX_ALIGN_MASK`, `VECTOR_BREAKPOINT`, static key `have_vec_crypto`, assembly declaration `__crct10dif_vpmsum`, inline `crc_t10dif_arch`, and `crc_t10dif_mod_init_arch`.

## Control Flow

The wrapper falls back to generic if length is below threshold plus alignment, vector crypto is unavailable, or SIMD use is disallowed. Otherwise it processes a generic prealignment prefix to 16-byte alignment, disables preemption and page faults, enables kernel Altivec, calls `__crct10dif_vpmsum()` on the aligned multiple after shifting CRC placement, disables Altivec, then processes any tail generically.

## State and Persistence Behavior

Feature state is stored in a read-only-after-init static key. Per-call vector state is protected by explicit Altivec enable/disable and preemption/pagefault guards.

## Dependencies and Integration Points

Dependencies include PowerPC SIMD/Altivec context helpers, CPU feature flags `CPU_FTR_ARCH_207S` and `PPC_FEATURE2_VEC_CRYPTO`, generic T10DIF, and VPMSUM assembly.

## Risks and Edge Cases

Alignment and CRC bit placement (`crc <<= 16`/`>>= 16`) are critical. SIMD context must be protected exactly or kernel vector state can be corrupted. The wrapper must not pass unaligned or tail bytes to the assembly routine.

## Test Signals

Signals include generic equivalence over prealigned, unaligned, threshold, and tail lengths; vector-feature fallback; preemption/pagefault guard checks; and KUnit T10DIF vectors on PPC64 with vector crypto.

## Read Coverage

Source read size: 70 lines, 1740 bytes.
