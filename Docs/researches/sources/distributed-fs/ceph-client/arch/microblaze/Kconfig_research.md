# sources/distributed-fs/ceph-client/arch/microblaze/Kconfig

## Purpose

declares the MicroBlaze architecture configuration surface, CPU feature dependencies, platform
choices, endian mode, MMU, cache, PCI, and generic kernel capability selections

## Important APIs, Types, and Functions

Source read size: 218 lines, 5809 bytes. Kconfig symbols: `MICROBLAZE`, `CPU_BIG_ENDIAN`,
`CPU_LITTLE_ENDIAN`, `ARCH_HAS_ILOG2_U32`, `ARCH_HAS_ILOG2_U64`, `GENERIC_HWEIGHT`,
`GENERIC_CALIBRATE_DELAY`, `GENERIC_CSUM`, `STACKTRACE_SUPPORT`, `LOCKDEP_SUPPORT`, `MMU`,
`CMDLINE_BOOL`, `CMDLINE`, `CMDLINE_FORCE`, `NR_CPUS`, `ADVANCED_OPTIONS`, `HIGHMEM`,
`LOWMEM_SIZE_BOOL`, `LOWMEM_SIZE`, `MANUAL_RESET_VECTOR`, `KERNEL_START_BOOL`, `KERNEL_START`,
`TASK_SIZE_BOOL`, `TASK_SIZE`; plus 1 more.

## Control Flow and Behavior

config entries select architecture feature symbols and source other MicroBlaze Kconfig fragments so
Kbuild can choose matching objects and compiler flags

## State and Persistence

persistent state is the generated .config/autoconf.h that shapes every compiled MicroBlaze object

## Dependencies and Integration Points

integrates with init/Kconfig, generic MM/IRQ/time/ftrace/perf options, platform Kconfig, and the
MicroBlaze Makefile

## Risks and Test Signals

bad dependencies produce unbootable or uncompilable kernels for a soft CPU configuration;
mmu_defconfig, randconfig, and QEMU/FPGA boots are signals
