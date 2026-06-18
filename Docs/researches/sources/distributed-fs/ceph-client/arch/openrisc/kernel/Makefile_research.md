<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/Makefile

## Purpose
Selects OpenRISC kernel objects and linker script generation.

## Important APIs, Types, And Functions
Builds `vmlinux.lds` for builtin kernels. Core objects include `head.o`, `setup.o`, `or32_ksyms.o`, `process.o`, `dma.o`, `traps.o`, `time.o`, `irq.o`, `entry.o`, `ptrace.o`, `signal.o`, `sys_call_table.o`, `unwinder.o`, and `cacheinfo.o`. Optional objects include jump labels, SMP, stacktrace, modules, OF prom support, and always `patching.o`.

## Control Flow
Kbuild uses these assignments to compile boot, exception, process, syscall, and MMU support into the architecture kernel.

## State And Persistence
No runtime state; controls linked code availability.

## Dependencies And Integration Points
Must align with Kconfig options and references from assembly/C code.

## Risks
Omitting an object causes link failures or missing runtime hooks. Including feature objects without Kconfig dependencies can break minimal builds.

## Test Signals
Build matrix with `SMP`, `MODULES`, `STACKTRACE`, `JUMP_LABEL`, and `OF` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/Makefile -->
