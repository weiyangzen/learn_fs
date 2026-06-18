# sources/distributed-fs/ceph-client/arch/arm/kernel/head.S

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/head.S` implements MMU-enabled ARM kernel
startup and initial page tables. It is part of the vendored Linux ARM code under the Ceph client
source tree and has 602 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: stext, __create_page_tables, secondary_startup,
__secondary_switched, __enable_mmu, __turn_mmu_on, __fixup_smp, __do_fixup_smp_on_up, and fixup_smp.
Visible dependencies include: `linux/linkage.h`, `linux/init.h`, `linux/pgtable.h`,
`asm/assembler.h`, `asm/cp15.h`, `asm/domain.h`, `asm/ptrace.h`, `asm/asm-offsets.h`, `asm/page.h`,
`asm/thread_info.h`, `head-common.S`.
Important macros/constants include: `KERNEL_RAM_VADDR`, `PG_DIR_SIZE`, `PMD_ENTRY_ORDER`,
`XIP_START`.
Assembly entry points detected in this file include: `stext`, `secondary_startup_arm`,
`secondary_startup`, `__secondary_switched`, `__turn_mmu_on`, `fixup_smp`.

## Control Flow
primary boot validates CPU/LPAE/ATAGs, builds identity and kernel mappings, maps debug UART and boot
params, enables the MMU, then jumps to __mmap_switched; secondary CPUs use supplied page tables.

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
Primary risk: page-table layout, physical/virtual patching, and SMP-on-UP fixups are extremely
sensitive to alignment and CPU capability bits. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
