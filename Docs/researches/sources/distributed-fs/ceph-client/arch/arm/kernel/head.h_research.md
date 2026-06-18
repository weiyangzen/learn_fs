# sources/distributed-fs/ceph-client/arch/arm/kernel/head.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head.h` declares symbols shared by XIP data
inflation code and early boot assembly. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 7 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __data_loc, _edata_loc, _sdata, and __inflate_kernel_data().
No standalone symbols are declared beyond build-system or include-level directives.

## Control Flow
head-common.S and head-inflate-data.c agree on data source/destination symbols through this header.

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
Primary risk: symbol mismatch breaks XIP data copy or decompression before the kernel is fully
initialized. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
