# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-header.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-header.S` provides shared ARM exception
entry/exit assembly macros. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 467 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: zero_fp, alignment_trap, v7m_exception_entry,
v7m_exception_slow_exit, store/load_user_sp_lr, svc_exit, restore_user_regs, ct_user_enter/exit,
invoke_syscall, and do_overflow_check.
Visible dependencies include: `linux/init.h`, `linux/linkage.h`, `asm/assembler.h`, `asm/asm-
offsets.h`, `asm/errno.h`, `asm/thread_info.h`, `asm/uaccess-asm.h`, `asm/v7m.h`.
Important macros/constants include: `BAD_PREFETCH`, `BAD_DATA`, `BAD_ADDREXCPTN`, `BAD_IRQ`,
`BAD_UNDEFINSTR`, `S_OFF`, `ATRAP(x...)`.

## Control Flow
included entry files use these macros to build frames, switch context tracking, invoke syscalls, and
restore user mode.

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
Primary risk: macro changes affect several entry files simultaneously and can break stack overflow
checks, uaccess state, or register restore order. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
