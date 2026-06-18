# sources/distributed-fs/ceph-client/arch/arm/kernel/entry-v7m.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/entry-v7m.S` implements ARMv7-M exception entry
and context switching. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 160 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __invalid_entry, __irq_entry, __pendsv_entry, __switch_to,
vector_table, and exc_ret.
Visible dependencies include: `asm/page.h`, `asm/glue.h`, `asm/thread_notify.h`, `asm/v7m.h`,
`entry-header.S`.
Assembly entry points detected in this file include: `__switch_to`, `vector_table`.

## Control Flow
M-profile exceptions enter through a vector table, construct frames via shared macros, dispatch
IRQ/PendSV, and switch thread state.

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
Primary risk: V7M has different PSR/mode semantics, so classic ARM assumptions in entry code are
unsafe here. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
