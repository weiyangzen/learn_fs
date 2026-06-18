# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips_mt.h

Purpose: Public MIPS MT configuration and sysfs-class declarations.

Important APIs/types/functions: Exposes `tclimit`, `vpelimit`, `mt_fpu_cpumask`, `mt_fpemul_threshold`, `mips_mt_set_cpuoptions()`, and `mt_class` when relevant. If `CONFIG_MIPS_MT` is absent, `mips_mt_set_cpuoptions()` compiles to a no-op.

Control flow, state, and persistence: The header itself has no implementation. Global state controls thread-context and VPE limits, FPU CPU mask, and FPU emulation threshold for MIPS MT systems.

Dependencies and integration: Depends on Linux `cpumask_t` and class declarations. It integrates with MIPS MT boot setup, sysfs exposure, FPU policy, and scheduler/CPU option initialization.

Risks and test signals: Misconfigured TC/VPE limits can expose nonexistent hardware contexts or underuse available ones. Test MIPS MT boot, sysfs class registration, FPU affinity/emulation behavior, and non-MT build stubs.
