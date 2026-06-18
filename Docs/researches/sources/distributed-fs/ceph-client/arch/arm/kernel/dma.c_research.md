# sources/distributed-fs/ceph-client/arch/arm/kernel/dma.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/dma.c` implements the legacy ISA DMA API
frontend for ARM platforms. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 283 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: isa_dma_add(), request_dma(), free_dma(), set_dma_sg(),
__set_dma_addr(), set_dma_count(), set_dma_mode(), enable_dma(), disable_dma(),
dma_channel_active(), set_dma_speed(), get_dma_residue(), and proc_dma_show().
Visible dependencies include: `linux/module.h`, `linux/init.h`, `linux/spinlock.h`, `linux/errno.h`,
`linux/scatterlist.h`, `linux/seq_file.h`, `linux/proc_fs.h`, `asm/dma.h`, `asm/mach/dma.h`.
C functions detected in this file include: `isa_dma_add()`, `request_dma()`, `free_dma()`,
`set_dma_sg()`, `__set_dma_addr()`, `set_dma_count()`, `set_dma_mode()`, `enable_dma()`,
`disable_dma()`, `dma_channel_active()`, `set_dma_page()`, `set_dma_speed()`, `get_dma_residue()`,
`proc_dma_show()`, `proc_dma_init()`.

## Control Flow
registered platform dma_t channels are locked, configured, enabled/disabled through d_ops, and
optionally reported in /proc/dma.

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
Primary risk: the API has global channel state and BUG paths when callers enable or disable
unallocated DMA channels. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
