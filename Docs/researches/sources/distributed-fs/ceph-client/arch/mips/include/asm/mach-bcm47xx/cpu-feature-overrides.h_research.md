# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/cpu-feature-overrides.h

**Purpose:** Provides BCM47xx compile-time CPU feature constants, with different assumptions for BCMA-only versus SSB-only builds.

**Important APIs/types/functions:** Defines MIPS feature macros for TLB, 4K cache/exception, no FPU/32FPR, counter, divec, prefetch, mcheck, EJTAG, LL/SC, no 64-bit, no MT/VZ, and cache-line sizes. Conditional blocks set `cpu_has_watch`, `cpu_has_mips32r2`, `cpu_has_dsp`, `cpu_has_dsp2`, `cpu_has_vint`, line sizes, and perf counter interrupt bit differently for BCMA-only and SSB-only builds. Some features such as `cpu_has_mips16` and `cpu_has_dc_aliases` are intentionally left to generic detection/comments.

**Control flow:** Generic MIPS code compiles feature-dependent paths based on these constants. Kconfig selection of SSB or BCMA materially changes emitted code and runtime expectations.

**State and persistence behavior:** No mutable state. The file is a compile-time CPU capability contract.

**Dependencies and integration points:** Integrated by BCM47xx Kconfig, generic MIPS CPU feature handling, exception/cache/perf/watchpoint code, and SSB/BCMA platform selection.

**Risks:** Combined SSB+BCMA builds leave some conditional features undefined here and must rely on generic fallback. Wrong line size or MIPS32r2/DSP/watch assumptions can produce invalid instructions or broken cache maintenance on older cores.

**Test signals:** Build SSB-only, BCMA-only, and combined configs; boot representative cores; run cache tests, perf counter/watchpoint tests, and scan generated config for expected feature macro values.
