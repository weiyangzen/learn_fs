# sources/distributed-fs/ceph-client/arch/arm/kernel/head-common.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head-common.S` contains shared ARM early boot
code after MMU/MPU transition. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 239 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __vet_atags, __mmap_switched, lookup_processor_type,
__lookup_processor_type, __error_lpae, __error_p, and __error.
Visible dependencies include: `asm/assembler.h`.
Important macros/constants include: `ATAG_CORE`, `ATAG_CORE_SIZE`, `ATAG_CORE_SIZE_EMPTY`,
`OF_DT_MAGIC`.
Assembly entry points detected in this file include: `lookup_processor_type`.

## Control Flow
boot validates ATAG/DTB pointers, clears BSS, copies/decompresses XIP data, stores
processor/machine/ATAG state, and jumps to start_kernel.

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
Primary risk: early code runs before allocators and normal mappings, so address assumptions and
register contracts are strict. Changes should preserve register layouts, numeric constants, early-
boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
