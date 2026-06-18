# sources/distributed-fs/ceph-client/arch/sparc/lib/U1memcpy.S

Purpose: UltraSPARC-I/II-family optimized memcpy and template for U1 raw user-copy functions.

Important APIs/functions: Emits `memcpy` by default, exports `FUNC_NAME`, and defines many U1 residual helpers (`U1_g1_1_fp`, `U1_gs_80_fp`, `U1_o2_0`, etc.) plus macros for VIS alignment and block loops.

Control flow: Checks length, handles tiny and medium copies, aligns the destination, enters VIS mode for large copies, runs one of eight unrolled alignment-specific block loops, completes residual VIS chunks, then handles tails. User-copy wrappers replace loads/stores and exception handling.

State and persistence: Stateless, but manipulates VIS/FPU state and uses memory barriers before/after block operations.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; used by U1 copy wrappers.

Risks/test signals: VIS alignment dispatch and fault helpers are complex. Test all source alignment classes, boundary sizes around 16 and 320 bytes, randomized data comparisons, and user-copy faults inside VIS loops.
