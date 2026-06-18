# sources/distributed-fs/ceph-client/arch/sh/lib/Makefile

Purpose: selects architecture runtime library objects for SuperH, including memory primitives, delay routines, I/O helpers, compiler helper routines, and optional MMU/ftrace variants.

Important variables: `lib-y`, `obj-y`, `memcpy-y`, `memset-y`, `udivsi3-y`, `CONFIG_CPU_SH4`, `CONFIG_CC_OPTIMIZE_FOR_SIZE`, `CONFIG_MMU`, and `CONFIG_MCOUNT`.

Control flow: Kbuild includes baseline helpers and conditionally swaps SH4-optimized memcpy/memset, division variants, copy/clear-user routines, and ftrace mcount code.

State and persistence: build-time object selection only; it determines which global symbols satisfy kernel/runtime references.

Dependencies and integration: consumed by arch Kbuild and compiler-generated helper calls such as shifts/divides plus generic kernel memory APIs.

Risks: wrong object selection can cause missing symbols or slower/incorrect low-level memory and arithmetic behavior on a CPU family.

Test signals: successful SH link, boot tests, memory primitive selftests, ftrace tests, and compiler helper symbol resolution.
