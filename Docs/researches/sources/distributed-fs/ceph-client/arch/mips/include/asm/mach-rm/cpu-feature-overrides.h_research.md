# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rm/cpu-feature-overrides.h

Purpose: Compile-time CPU feature overrides for SNI RM200 C systems, known to ship with R4600 V2.0 and R5000 processors. It lets generic MIPS code constant-fold feature checks.

Important APIs/types/functions: Defines `cpu_has_tlb`, `cpu_has_4kex`, `cpu_has_4k_cache`, `cpu_has_32fpr`, `cpu_has_counter`, `cpu_has_llsc`, and `cpu_has_64bits` as present. It disables watchpoints, MIPS16, DSP, MIPS MT, userlocal, EJTAG, machine check, prefetch, and MIPS32/64 release-level flags. `cpu_has_dc_aliases` depends on `PAGE_SIZE < 0x4000`.

Control flow, state, and persistence: No runtime state is stored. The macros alter compile-time branches and static keys in architecture code.

Dependencies and integration: Consumers are generic MIPS CPU feature logic, cache/TLB code, signal/FPU setup, and exception paths. It requires `PAGE_SIZE` from page configuration.

Risks and test signals: A wrong override silently compiles in invalid instructions or omits required workarounds. Test with RM200 defconfig builds, FPU and cache-alias stress, and runtime `/proc/cpuinfo` or boot logs matching expected R4x00/R5000 behavior.
