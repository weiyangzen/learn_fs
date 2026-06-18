# sources/distributed-fs/ceph-client/lib/raid/xor/Makefile

## Purpose
Builds the generic and architecture-optimized XOR block implementations used by RAID/parity code, and descends into XOR tests.

## APIs, Control Flow, and State
Adds the local include path, builds `xor.o` when `CONFIG_XOR_BLOCKS` is enabled, composes it from generic core and register/prefetch implementations, and conditionally appends architecture-specific objects for Alpha, ARM/ARM64 NEON, LoongArch LSX, PowerPC Altivec, RISC-V vector, SPARC, S390, and x86 AVX/SSE/MMX. If `CONFIG_XOR_BLOCKS_ARCH` is enabled, `xor-core.o` receives an architecture include path. ARM/ARM64/PowerPC rules adjust FPU/vector compiler flags. `obj-y += tests/` always descends into tests. There is no runtime state in the Makefile.

## Dependencies, Integration, Risks, and Tests
Depends on Kbuild, architecture feature symbols, compiler support for vector flags, and source files under architecture subdirectories. Risks include wrong FPU flags causing build failures or unsafe kernel-mode vector use, duplicate/missing optimized objects for an architecture, and generic fallback performance regressions. Test signals include per-architecture builds, XOR KUnit tests, boot-time XOR speed/selection logs, and RAID parity correctness tests.
