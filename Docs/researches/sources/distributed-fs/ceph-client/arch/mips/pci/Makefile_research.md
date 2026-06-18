# sources/distributed-fs/ceph-client/arch/mips/pci/Makefile

## Purpose
Selects which MIPS PCI support objects are compiled for a kernel configuration. It is the integration manifest for generic PCI core glue, legacy controller glue, board-specific fixups, host-controller ops, MSI support, and SoC-specific drivers under `arch/mips/pci`.

## Important APIs, Types, And Functions
This file does not define C APIs. It uses Kbuild `obj-y` and `obj-$(CONFIG_...)` assignments to include objects such as `pci.o`, `pci-legacy.o`, `pci-generic.o`, `ops-bonito64.o`, `ops-gt64xxx_pci0.o`, `pci-bcm63xx.o`, `pci-alchemy.o`, `pci-ar2315.o`, `pci-ar71xx.o`, `pci-ar724x.o`, and matching fixup files.

## Control Flow
At build time, Kbuild evaluates the selected Kconfig symbols and appends matching objects. Several board symbols pull multiple files together, for example BCM63XX pulls controller, fixup, and ops files; Loongson boards pull fixup files plus `ops-loongson2.o`; SGI IP32 pulls fixup, ops, and platform PCI init files. Octeon MSI is gated by both `CONFIG_CAVIUM_OCTEON_SOC` and `CONFIG_PCI_MSI`.

## State And Persistence
No runtime state. Build outputs are determined by Kconfig state and object lists.

## Dependencies And Integration Points
Integrates MIPS platform Kconfig symbols with the Linux PCI subsystem. The object ordering matters because generic `pcibios_*` symbols and PCI fixup declarations are linked only for the active board family.

## Risks And Edge Cases
Wrong object selection can cause duplicate `pcibios_map_irq`/`pcibios_plat_dev_init` definitions or missing `pci_ops` symbols. Board combinations that accidentally enable incompatible legacy fixups are a build-time or link-time risk. MSI support for Octeon depends on nested `ifdef CONFIG_PCI_MSI`, so missing MSI objects are expected when MSI is disabled.

## Test Signals
Compile coverage across MIPS defconfigs is the primary signal. Link success for mutually exclusive board families and object presence checks in build logs validate this file.
