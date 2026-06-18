# sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_to_user.S

Purpose: UltraSPARC-I/II/IIi/IIe optimized raw copy-to-user wrapper.

Important APIs/functions: Defines `FUNC_NAME raw_copy_to_user`, guarded integer/FP stores, `STORE`, `STORE_BLK`, `EX_RETVAL(0)`, and ASI preamble before including `U1memcpy.S`.

Control flow: Validates `%asi`, falls back to `raw_copy_in_user` when needed, then executes U1 copy paths with store fault fixups.

State and persistence: No persistent data. It temporarily uses ASI and VIS/FPU state.

Dependencies/integration: Depends on `U1memcpy.S`, user ASI constants, and raw-copy callers.

Risks/test signals: Store exception residuals and FPU cleanup are key. Test protected destinations, unaligned copies, and KERNEL_DS-style ASI fallback.
