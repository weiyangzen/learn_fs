<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/init.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/init.c

Purpose: performs early per-CPU SH processor initialization.

Important APIs/types/functions: `cpu_init()`, `cache_init()`, `detect_cache_shape()`, `fpu_init()`, `dsp_init()`, weak `l2_cache_init()`, setup handlers for `nofpu`/`nodsp`.

Control flow: probes CPU, computes cache geometry, purges/enables caches, initializes FPU/DSP feature flags, sets ASID cache and physical address bits, programs speculative/expmask registers, initializes VBR and xstate on boot CPU.

State and persistence: persistent kernel state includes `current_cpu_data`, cache shape auxv globals, ASID cache, feature flags, and thread xstate metadata.

Dependencies/integration: depends on CPU probe, cacheflush, SMP, SH BIOS, trap setup, MMU context, and command-line setup.

Risks: early raw cache/register operations are fragile; wrong geometry can corrupt boot data or user ABI cache shapes.

Test signals: boot representative subtypes with nofpu/nodsp, cache modes, SMP, and verify `/proc/cpuinfo`, auxv, and trap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/init.c -->
