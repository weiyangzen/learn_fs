# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-common.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-common.S` implements ARM syscall return
paths and syscall tables. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 464 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: ret_fast_syscall, ret_to_user, ret_from_fork, vector_swi,
__sys_trace, syscall_table_start/end, sys_syscall, sigreturn wrappers, mmap2, and OABI wrappers.
Visible dependencies include: `asm/assembler.h`, `asm/unistd.h`, `asm/ftrace.h`, `asm/unwind.h`,
`asm/page.h`, `asm/unistd-oabi.h`, `entry-header.S`, `calls-eabi.S`, `calls-oabi.S`.
Important macros/constants include: `TRACE(x...)`, `__SYSCALL_WITH_COMPAT(nr, native, compat)`,
`__SYSCALL(nr, func)`.
Assembly entry points detected in this file include: `ret_to_user`, `ret_to_user_from_irq`,
`ret_from_fork`, `vector_bhb_loop8_swi`, `vector_bhb_bpiall_swi`, `vector_swi`, `\sym`.

## Control Flow
SVC decode selects EABI/OABI syscall numbers, handles tracing/seccomp/restarts, invokes syscall
tables, and returns through work-pending checks.

## State and Persistence Behavior
State is kernel-resident and mostly early-boot or per-CPU: machine type, ATAG/DT pointers, page
tables, processor IDs, cache/idle metadata, FIQ ownership, DMA channel locks, ftrace patched text,
EFI mappings, or hibernation image state. Persistence is limited to kernel memory, exported
proc/sysfs/debug state, or stable ABI effects visible to modules and userspace.

## Dependencies and Integration Points
This file integrates with the ARM architecture boot, exception, tracing, firmware, PCI, DMA, or
power management path selected by `arch/arm/kernel/Makefile`. It is tied to adjacent ARM headers,
linker tables, generated `asm-offsets.h`, machine descriptors, and generic Linux subsystems named by
its includes.

## Risks
Primary risk: syscall table ordering and ABI wrapper behavior are hard userspace ABI contracts.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
