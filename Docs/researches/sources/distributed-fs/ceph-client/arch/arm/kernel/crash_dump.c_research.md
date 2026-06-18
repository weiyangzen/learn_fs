# sources/distributed-fs/ceph-client/arch/arm/kernel/crash_dump.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/crash_dump.c` copies pages from a crashed
kernel's old memory image. It is part of the vendored Linux ARM code under the Ceph client source
tree and has 35 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: copy_oldmem_page().
Visible dependencies include: `linux/errno.h`, `linux/crash_dump.h`, `linux/uaccess.h`,
`linux/io.h`, `linux/uio.h`.
C functions detected in this file include: `Copyright()`.

## Control Flow
the crash dump reader ioremaps the requested PFN, copies bytes to an iov_iter, and unmaps it.

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
Primary risk: ioremap failures or offset/size mistakes prevent vmcore extraction. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
