# sources/distributed-fs/ceph-client/arch/arm/kernel/bugs.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/bugs.c` runs ARM CPU bug checks during final
architecture CPU init. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 19 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: check_other_bugs() and arch_cpu_finalize_init().
Visible dependencies include: `linux/init.h`, `linux/cpu.h`, `asm/bugs.h`, `asm/proc-fns.h`.
C functions detected in this file include: `check_other_bugs()`, `arch_cpu_finalize_init()`.

## Control Flow
write-buffer bug checks and optional processor-specific cpu_check_bugs run after CPU setup.

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
Primary risk: skipping checks may leave required CPU erratum workarounds disabled. Changes should
preserve register layouts, numeric constants, early-boot calling conventions, and userspace/module
ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
