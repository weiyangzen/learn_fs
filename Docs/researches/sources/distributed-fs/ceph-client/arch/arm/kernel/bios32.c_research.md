# sources/distributed-fs/ceph-client/arch/arm/kernel/bios32.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/kernel/bios32.c` implements ARM PCI BIOS-style host
bridge setup and fixups. It is part of the vendored Linux ARM code under the Ceph client source tree
and has 596 source lines in this checkout.

## Important APIs, Types, and Functions
Primary API or contract surface: pcibios_report_status(), PCI fixups, pcibios_fixup_bus(),
pcibios_swizzle(), pcibios_map_irq(), pcibios_init_hw(), pci_common_init_dev(),
pcibios_align_resource(), and pci_map_io_early().
Visible dependencies include: `linux/export.h`, `linux/kernel.h`, `linux/pci.h`, `linux/slab.h`,
`linux/string_choices.h`, `linux/init.h`, `linux/io.h`, `asm/mach-types.h`, `asm/mach/map.h`,
`asm/mach/pci.h`.
C functions detected in this file include: `pcibios_bus_report_status()`, `list_for_each_entry()`,
`pcibios_report_status()`, `pci_fixup_83c553()`, `pci_fixup_unassign()`, `layer()`,
`pci_dev_for_each_resource()`, `pci_fixup_ide_bases()`, `pci_fixup_dec21142()`,
`pci_fixup_cy82c693()`, `pdev_bad_for_parity()`, `pcibios_fixup_bus()`, `pcibios_swizzle()`,
`pcibios_map_irq()`, `pcibios_init_resource()`, `pcibios_init_hw()`, `pci_common_init_dev()`,
`pci_bus_claim_resources()`, ... (22 total).

## Control Flow
platform hw_pci callbacks set up bridges, resources are claimed or assigned, interrupts are
swizzled/mapped, and devices are added.

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
Primary risk: resource alignment, legacy bridge fixups, and IRQ mapping are platform-sensitive and
can break PCI enumeration. Changes should preserve register layouts, numeric constants, early-boot
calling conventions, and userspace/module ABI boundaries implied by this file.

## Test Signals
Use ARM defconfig and targeted config builds covering the relevant `CONFIG_*` option, run objdump or
boot smoke tests under QEMU/hardware where possible, and exercise subsystem tests for PCI, DMA,
ftrace, FIQ, EFI, cpuidle, hibernation, syscall, or DT/ATAG boot paths as applicable.
