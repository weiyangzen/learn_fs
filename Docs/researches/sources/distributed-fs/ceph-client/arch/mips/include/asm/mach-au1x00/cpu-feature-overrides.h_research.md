# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/cpu-feature-overrides.h

**Purpose:** Provides compile-time MIPS CPU feature constants for Alchemy Au1x00 platforms.

**Important APIs/types/functions:** Defines many `cpu_has_*` values: TLB and 4K exception/cache present, no FPU, no MIPS16/microMIPS/MIPS64/DSP/MT/virtualization features, counter/watch/divec/prefetch/mcheck/EJTAG/LLSC present, no D-cache aliases, I-cache fills from D-cache, MIPS32r1 yes and r2/r6 no, and no secondary cache line size. It has no functions or storage.

**Control flow:** Generic MIPS code compiles feature-dependent paths based on these constants, affecting cache ops, exception handling, atomics, watchpoints, and instruction selection.

**State and persistence behavior:** No mutable state. It is a compile-time hardware contract for all Au1x00 variants selected by this machine.

**Dependencies and integration points:** Integrated by generic MIPS CPU feature logic and must agree with CP0 PRID handling in `au1000.h` and Kconfig support.

**Risks:** Any incorrect feature bit can emit unsupported instructions or skip required cache handling. The uniform values must remain true for every Au1x00 variant, including Au1300.

**Test signals:** Build all Alchemy defconfigs, boot on representative SoCs, run atomics/LLSC tests, cache coherency tests, watchpoint smoke tests, and verify no FPU/DSP/MIPS32r2-only code is selected.
