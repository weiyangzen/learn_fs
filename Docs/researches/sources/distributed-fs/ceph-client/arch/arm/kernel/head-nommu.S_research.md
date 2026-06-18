# sources/distributed-fs/ceph-client/arch/arm/kernel/head-nommu.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head-nommu.S` implements ARM no-MMU and MPU
kernel startup. It is part of the vendored Linux ARM code under the Ceph client source tree and has
536 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: stext, secondary_startup, __after_proc_init, __setup_mpu,
__setup_pmsa_v7/v8, and secondary MPU setup helpers.
Visible dependencies include: `linux/linkage.h`, `linux/init.h`, `linux/errno.h`, `asm/assembler.h`,
`asm/ptrace.h`, `asm/asm-offsets.h`, `asm/page.h`, `asm/cp15.h`, `asm/thread_info.h`, `asm/v7m.h`,
`asm/mpu.h`, `head-common.S`.
Assembly entry points detected in this file include: `stext`, `secondary_startup`, `__setup_mpu`,
`__setup_pmsa_v7`, `__setup_pmsa_v8`, `__secondary_setup_mpu`, `__secondary_setup_pmsa_v7`,
`__secondary_setup_pmsa_v8`.

## Control Flow
startup identifies CPU type, optionally programs MPU regions, calls processor init, enables control
bits, and enters shared mmap-switched code.

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
Primary risk: MPU region sizing and PMSA version handling determine whether RAM, vectors, XIP ROM,
and background regions are accessible and protected. Changes should preserve register layouts,
numeric constants, early-boot calling conventions, and userspace/module ABI boundaries implied by
this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
