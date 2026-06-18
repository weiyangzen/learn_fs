# sources/distributed-fs/ceph-client/lib/raid6/Makefile

Purpose: builds the RAID6 P/Q library and generates architecture-specific unrolled sources and lookup tables.

Important APIs and flow: `raid6_pq-y` includes algorithm selection, recovery, generated tables, and integer unrolls. Conditional object lists add x86, AltiVec, NEON, s390, LoongArch, and RISC-V implementations. `mktables` is a host program that emits `tables.c`; `unroll.awk` turns `.uc` templates into `intN`, `altivecN`, `vpermxorN`, `neonN`, and `s390vxN` sources. It also manages required compiler flags for AltiVec and NEON/FPU objects.

State and persistence: build-system state only; generated C files are build artifacts.

Dependencies and integration: Kbuild, host tools, architecture configs, and compiler feature flags.

Risks and test signals: risks include wrong FPU flags causing SIMD instructions outside wrappers or failed generated-source dependencies. Signals are all-architecture build coverage and RAID6 test programs/KUnit equivalents where present.
