# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-armv.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-armv.S` implements classic ARM exception
vectors, SVC/IRQ/abort/undefined/FIQ entry, context switching, and kuser helpers. It is part of the
vendored Linux ARM code under the Ceph client source tree and has 1127 source lines in this
checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: irq_handler, pabt_helper, dabt_helper, svc_entry, usr_entry,
__switch_to, ret_from_exception, vector_stub variants, vector_swi references, and kuser helper area.
Visible dependencies include: `linux/init.h`, `asm/assembler.h`, `asm/page.h`, `asm/glue-df.h`,
`asm/glue-pf.h`, `asm/vfpmacros.h`, `asm/thread_notify.h`, `asm/unwind.h`, `asm/unistd.h`,
`asm/tls.h`, `asm/system_info.h`, `asm/uaccess-asm.h`, `asm/kasan_def.h`, `entry-header.S`, ... (15
total).
Important macros/constants include: `RELOC_TEXT_NONE`, `SPFIX(code...)`.
Assembly entry points detected in this file include: `ret_from_exception`, `__switch_to`.

## Control Flow
exceptions save pt_regs-compatible frames, dispatch C handlers or syscall logic, restore user/kernel
state, and preserve ABI-visible helper code.

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
Primary risk: tiny ordering changes can corrupt register frames, preemption state, syscall restart,
BHB mitigations, or user ABI helpers. Changes should preserve register layouts, numeric constants,
early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
