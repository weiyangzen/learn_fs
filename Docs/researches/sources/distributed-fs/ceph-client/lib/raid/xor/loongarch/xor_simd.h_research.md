# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.h

Purpose: declares the raw LoongArch SIMD XOR functions implemented by `xor_simd.c`.

Important APIs and flow: under `CONFIG_CPU_HAS_LSX` it declares `__xor_lsx_{2,3,4,5}`; under `CONFIG_CPU_HAS_LASX` it declares `__xor_lasx_{2,3,4,5}`. Each function accepts byte count, destination pointer, and up to four source pointers.

State and persistence: no state; interface-only header.

Dependencies and integration: used by `xor_simd_glue.c` to wrap raw SIMD routines with `DO_XOR_BLOCKS()` and FPU state handling.

Risks and test signals: wrong prototypes would corrupt calling convention. Compiler diagnostics plus KUnit XOR runs on LSX/LASX systems are the main signals.
