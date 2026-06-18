# sources/distributed-fs/ceph-client/arch/arm/kernel/efi.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/efi.c` maps EFI runtime memory and validates ARM
EFI entry state. It is part of the vendored Linux ARM code under the Ceph client source tree and has
130 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: set_permissions(), efi_set_mapping_permissions(),
efi_create_mapping(), efi_arch_tables, load_cpu_state_table(), and arm_efi_init().
Visible dependencies include: `linux/efi.h`, `linux/memblock.h`, `linux/screen_info.h`, `asm/efi.h`,
`asm/mach/map.h`, `asm/mmu_context.h`.
C functions detected in this file include: `Copyright()`, `efi_set_mapping_permissions()`,
`efi_create_mapping()`, `load_cpu_state_table()`, `arm_efi_init()`.

## Control Flow
EFI memory descriptors become late mappings with cache/device types and optional RO/XN permissions,
then CPU state table diagnostics run.

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
Primary risk: section mappings may skip fine-grained permission changes, and buggy firmware state is
only warned about. Changes should preserve register layouts, numeric constants, early-boot calling
conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
