# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-sibyte/cpu-feature-overrides.h

Purpose: Compile-time feature profile for SiByte MIPS64 processors with a fixed platform configuration.

Important APIs/types/functions: It marks watch registers, vectored interrupts (`cpu_has_divec`), prefetch, machine check, EJTAG, LL/SC, virtual-tag I-cache, 64-bit support, MIPS32r1, and MIPS64r1 as present. It disables MIPS16, VCE, cache CDEX, aliases, DSP, MIPS MT, userlocal, no-FPU-exception mode, and later release flags. It fixes D/I/S-cache line sizes to 32 bytes and marks primary caches non-inclusive.

Control flow, state, and persistence: Feature macros have no runtime state but steer generic branches for cache management, exception vectors, and instruction availability.

Dependencies and integration: Used by the MIPS CPU feature framework, cache code, TLB setup, and SiByte platform builds.

Risks and test signals: Since many paths become constants, any mismatch between SoC revision and macro values can become a boot-time or data-corruption fault. Test by building SiByte kernels, exercising cache flushes and LL/SC atomics, and verifying machine-check/EJTAG paths are not incorrectly assumed absent.
