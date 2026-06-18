<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h` declares compile-time MIPS CPU capability overrides for `mach-ip28`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 31 macros including `__ASM_MACH_IP28_CPU_FEATURE_OVERRIDES_H`, `cpu_has_watch`, `cpu_has_mips16`, `cpu_has_mips16e2`, `cpu_has_divec`, `cpu_has_vce`, `cpu_has_cache_cdex_p`, `cpu_has_cache_cdex_s`, `cpu_has_prefetch`, `cpu_has_mcheck`, `cpu_has_ejtag`, `cpu_has_llsc`, `cpu_has_vtag_icache`, `cpu_has_dc_aliases`, `cpu_has_ic_fills_f_dc`, `cpu_has_dsp`, `cpu_has_dsp2`, `cpu_icache_snoops_remote_store`, `cpu_has_mipsmt`, `cpu_has_userlocal`, `cpu_has_nofpuex`, `cpu_has_64bits`, `cpu_has_4kex`, `cpu_has_4k_cache`, and 7 more; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
There is no runtime branch logic. The MIPS headers include this file at compile time and convert the `cpu_has_*` and cache-line macros into constant feature tests, so later code paths are compiled, optimized, or omitted based on these definitions.

## State and Persistence Behavior
It stores no mutable state. Its constants persist as build-time architecture assumptions that affect generated code for cache, exception, FPU, DSP, LL/SC, and ISA-level paths.

## Dependencies and Integration Points
Direct includes are `asm/cpu.h`. Major macro families are `cpu_has (27)`, `cpu_icache (2)`, `_ (1)`, `cpu_dcache (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is the generic MIPS CPU feature probes, cache/TLB setup, alternatives, FPU/DSP/MT code paths, and architecture Kconfig selection.

## Risks
wrong feature constants can compile in instructions or cache behavior the selected CPU cannot execute; feature lies can cause illegal instructions, missing FPU emulation assumptions, wrong cache operations, or broken atomic primitives.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot-test on representative hardware or QEMU where available and inspect CPU feature logs, cache line sizes, and illegal-instruction traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip28/cpu-feature-overrides.h -->
