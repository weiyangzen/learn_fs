# sources/distributed-fs/ceph-client/arch/arm/kernel/devtree.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/devtree.c` handles ARM machine selection and CPU
map setup from flattened device tree. It is part of the vendored Linux ARM code under the Ceph
client source tree and has 238 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: arm_dt_init_cpu_maps(), arch_match_cpu_phys_id(),
arch_get_next_mach(), and setup_machine_fdt().
Visible dependencies include: `linux/init.h`, `linux/export.h`, `linux/errno.h`, `linux/types.h`,
`linux/memblock.h`, `linux/of.h`, `linux/of_fdt.h`, `linux/of_irq.h`, `linux/smp.h`,
`asm/cputype.h`, `asm/setup.h`, `asm/page.h`, `asm/prom.h`, `asm/smp_plat.h`, ... (16 total).
C functions detected in this file include: `set_smp_ops_by_method()`, `arm_dt_init_cpu_maps()`,
`for_each_of_cpu_node()`, `smp_setup_processor_id()`, `arch_match_cpu_phys_id()`,
`arch_get_next_mach()`, `setup_machine_fdt()`.

## Control Flow
DT verification, compatible matching, CPU MPIDR parsing, SMP enable-method lookup, DT fixups, and
early node scanning happen before normal platform setup.

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
Primary risk: bad CPU reg properties or compatible lists can cap CPUs, choose wrong smp_ops, or stop
boot with an unsupported machine table dump. Changes should preserve register layouts, numeric
constants, early-boot calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
