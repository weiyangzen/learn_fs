# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rc32434.c

## Purpose
Provides IDT RC32434/RB532 PCI IRQ mapping and an early bridge fixup.

## Important APIs, Types, And Functions
Defines `irq_map`, `pcibios_map_irq`, `rc32434_pci_early_fixup`, and no-op `pcibios_plat_dev_init`.

## Control Flow
Devices on bus 0 or 1 and slots below 12 map through `irq_map` plus `GROUP4_IRQ_BASE + 4`. Header fixup for slot 6 bus 0 disables prefetch memory range and sets cache line size.

## State And Persistence
No software persistence except static table. Config writes persist until reset.

## Dependencies And Integration Points
Depends on RC32434 board IRQ definitions and PCI fixup infrastructure.

## Risks And Edge Cases
The fixup is registered for `PCI_ANY_ID`, so guard conditions must remain correct. Table lookup lacks pin use and assumes two buses/twelve slots.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
