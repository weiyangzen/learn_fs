# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-bcm63xx.c

## Purpose
Provides simple BCM63xx PCI platform hooks for legacy PCI interrupt routing.

## Important APIs, Types, And Functions
Defines `pcibios_map_irq`, returning `bcm63xx_get_irq_number(IRQ_PCI)`, and no-op `pcibios_plat_dev_init`.

## Control Flow
Every enumerated PCI device is routed to the SoC's single PCI IRQ. Device init does no additional programming.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on BCM63xx CPU IRQ helpers and the BCM63XX object group.

## Risks And Edge Cases
All devices share one IRQ, so interrupt sharing must work. Incorrect CPU IRQ tables break every PCI device.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
