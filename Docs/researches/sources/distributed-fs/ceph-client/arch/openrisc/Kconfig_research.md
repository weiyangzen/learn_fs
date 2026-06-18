# sources/distributed-fs/ceph-client/arch/openrisc/Kconfig

Purpose: declares the OpenRISC architecture Kconfig feature set, CPU class options, optional instruction
availability, SMP/FPU switches, and debugging knobs.

Important APIs/types/functions: Kconfig symbols: `OPENRISC`, `CPU_BIG_ENDIAN`, `MMU`, `GENERIC_HWEIGHT`, `NO_IOPORT_MAP`,
`GENERIC_CSUM`, `STACKTRACE_SUPPORT`, `LOCKDEP_SUPPORT`, `FIX_EARLYCON_MEM`, `OR1K_1200`,
`DCACHE_WRITETHROUGH`, `BUILTIN_DTB_NAME`, `OPENRISC_HAVE_INST_FF1`, `OPENRISC_HAVE_INST_FL1`,
`OPENRISC_HAVE_INST_MUL`, `OPENRISC_HAVE_INST_DIV`, `OPENRISC_HAVE_INST_CMOV`,
`OPENRISC_HAVE_INST_ROR`, `OPENRISC_HAVE_INST_RORI`, `OPENRISC_HAVE_INST_SEXT`, `NR_CPUS`, `SMP`,
`FPU`, `OPENRISC_NO_SPR_SR_DSX`, and 4 more.

Control flow: Kconfig evaluates the architecture menu from top to bottom, enabling baseline OpenRISC capabilities
and exposing CPU feature, instruction, SMP, FPU, command-line, and debug choices to defconfig and
menuconfig users.

State and persistence: Persistent state is the chosen kernel configuration, which changes compiled instruction assumptions,
cache policy, SMP/FPU support, built-in DTB selection, and debug behavior.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are selecting instruction features unsupported by the target CPU, inconsistent SMP/FPU/cache
policy, or debug options that change exception behavior.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
