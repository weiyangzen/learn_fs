# sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_to_user.S

Purpose: UltraSPARC-III/Cheetah optimized copy-to-user wrapper.

Important APIs/functions: Defines guarded stores, `FUNC_NAME U3copy_to_user`, `STORE`, `STORE_BLK`, `EX_RETVAL(0)`, and ASI preamble before including `U3memcpy.S`.

Control flow: Checks `%asi`, falls back to `raw_copy_in_user`, then uses U3 copy paths with exception-protected stores and block stores.

State and persistence: No persistent state; temporary VIS/FPU and ASI use.

Dependencies/integration: Depends on `U3memcpy.S`, ASI constants, and `U3patch.S`.

Risks/test signals: Store fault recovery and ASI fallback must match raw copy semantics. Test protected destinations, VIS/block paths, and patched Cheetah systems.
