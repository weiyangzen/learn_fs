# sources/distributed-fs/ceph-client/arch/arm/kernel/fiqasm.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/fiqasm.S` implements banked FIQ register get/set
helpers. It is part of the vendored Linux ARM code under the Ceph client source tree and has 49
source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __set_fiq_regs and __get_fiq_regs.
Visible dependencies include: `linux/linkage.h`, `asm/assembler.h`.
Assembly entry points detected in this file include: `__set_fiq_regs`, `__get_fiq_regs`.

## Control Flow
the helpers switch CPSR to FIQ mode with IRQ/FIQ masked, load or store r8-r12/sp/lr, then restore
the prior CPSR.

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
Primary risk: interrupts in FIQ mode are fatal, so mode switching and hazard nops must remain exact.
Changes should preserve register layouts, numeric constants, early-boot calling conventions, and
userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
