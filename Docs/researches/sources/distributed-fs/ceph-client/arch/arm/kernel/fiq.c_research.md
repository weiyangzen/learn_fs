# sources/distributed-fs/ceph-client/arch/arm/kernel/fiq.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/fiq.c` implements ARM FIQ ownership, handler
installation, and exported control API. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 166 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: fiq_handler ownership stack, set_fiq_handler(), claim_fiq(),
release_fiq(), enable_fiq(), disable_fiq(), show_fiq_list(), and init_FIQ().
Visible dependencies include: `linux/module.h`, `linux/kernel.h`, `linux/init.h`,
`linux/interrupt.h`, `linux/seq_file.h`, `asm/cacheflush.h`, `asm/cp15.h`, `asm/fiq.h`,
`asm/mach/irq.h`, `asm/irq.h`, `asm/traps.h`.
Important macros/constants include: `FIQ_OFFSET`.
C functions detected in this file include: `fiq_def_op()`, `show_fiq_list()`, `set_fiq_handler()`,
`claim_fiq()`, `release_fiq()`, `enable_fiq()`, `disable_fiq()`, `init_FIQ()`.

## Control Flow
drivers claim FIQ, install vector code and banked registers, and prior owners can
relinquish/reacquire control.

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
Primary risk: FIQ is not shareable, vector patching requires I-cache maintenance, and incorrect
release order is diagnosed but dangerous. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
