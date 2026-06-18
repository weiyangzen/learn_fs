# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-rbtx4927.c

## Purpose
Provides Toshiba RBTX4927 board-specific PCI interrupt rotation.

## Important APIs, Types, And Functions
Defines `rbtx4927_pci_map_irq`, using TXX9 option flags and RBTX4927 IOC IRQ constants.

## Control Flow
The function rotates INTA-D based on slot number, with separate handling for the card slot and backplane, then converts the logical pin to IOC PCIA-D IRQ numbers.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on TXX9 PCI option state and RBTX4927 board IRQ definitions. It is called by board PCI setup rather than generic `pcibios_map_irq` in this file.

## Risks And Edge Cases
PICMG option and slot arithmetic must match physical backplane wiring. Out-of-range pins would produce nonsensical rotations.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
