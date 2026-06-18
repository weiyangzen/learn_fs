# sources/distributed-fs/ceph-client/arch/sparc/lib/U3memcpy.S

Purpose: UltraSPARC-III/Cheetah optimized memcpy engine and template for U3 user-copy routines.

Important APIs/functions: Emits `U3memcpy` by default. Defines `__restore_fp`, many `U3_retl_*` residual helpers, and macro hooks for `LOAD`, `STORE`, `STORE_BLK`, `PREAMBLE`, and `FUNC_NAME`.

Control flow: Validates length, aligns destination, uses VIS and prefetch for large copies, handles less-than-192-byte and less-than-16-byte paths separately, and returns through helper labels on exceptions. Wrappers override memory access and exception behavior.

State and persistence: Stateless; transiently uses VIS/FPU state and ASI.

Dependencies/integration: Includes `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; patched by `U3patch.S`.

Risks/test signals: Cheetah-specific prefetch/VIS loops and exception helpers can miscount residuals. Test random aligned/unaligned copies, lengths around 16 and 192, user faults, and comparison with generic memcpy.
