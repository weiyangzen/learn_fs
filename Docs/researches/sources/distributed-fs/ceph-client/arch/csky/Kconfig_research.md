# sources/distributed-fs/ceph-client/arch/csky/Kconfig

## Purpose

declares the C-SKY architecture configuration surface, CPU variants, MMU/cache/FPU/SMP/highmem/TCM
options, and generic kernel feature selections

## Important APIs, Types, and Functions

Source read size: 355 lines, 8599 bytes. Kconfig symbols: `CSKY`, `LOCKDEP_SUPPORT`,
`ARCH_SUPPORTS_UPROBES`, `CPU_HAS_CACHEV2`, `CPU_HAS_FPUV2`, `CPU_HAS_HILO`, `CPU_HAS_TLBI`,
`CPU_HAS_LDSTEX`, `CPU_NEED_TLBSYNC`, `CPU_NEED_SOFTALIGN`, `CPU_NO_USER_BKPT`,
`GENERIC_CALIBRATE_DELAY`, `GENERIC_CSUM`, `GENERIC_HWEIGHT`, `MMU`, `STACKTRACE_SUPPORT`,
`TIME_LOW_RES`, `CPU_ASID_BITS`; plus 32 more.

## Control Flow and Behavior

menu/config entries choose ABI, page offset, CPU features, PMU, power management, TCM, SMP, highmem,
and architecture capability defaults

## State and Persistence

persistent effects are compile-time configuration symbols that shape the built kernel

## Dependencies and Integration Points

integrates with the top-level Kconfig, generic MM/IRQ/time/ftrace/perf options, and C-SKY Makefile
object selection

## Risks and Test Signals

bad defaults can build incompatible kernels for a CPU; defconfig, randconfig, and boot tests across
CK610/CK807/CK810/CK860 are the signals
