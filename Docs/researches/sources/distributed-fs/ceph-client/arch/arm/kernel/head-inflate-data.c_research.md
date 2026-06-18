# sources/distributed-fs/ceph-client/arch/arm/kernel/head-inflate-data.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head-inflate-data.c` inflates XIP compressed
kernel data during earliest boot. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 56 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: __inflate_kernel_data().
Visible dependencies include: `linux/init.h`, `linux/zutil.h`, `head.h`,
`../../../lib/zlib_inflate/inftrees.h`, `../../../lib/zlib_inflate/inflate.h`,
`../../../lib/zlib_inflate/infutil.h`.
C functions detected in this file include: `__inflate_kernel_data()`.

## Control Flow
a stack-allocated zlib stream inflates data from __data_loc into _sdata before BSS clearing and
start_kernel.

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
Primary risk: the code runs with a temporary stack and no allocator, so frame size and zlib
workspace assumptions are boot-critical. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
