# sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm47xx.c

## Purpose
Provides BCM47xx PCI platform device initialization and IRQ mapping delegation for SSB and BCMA bus variants.

## Important APIs, Types, And Functions
Defines `pcibios_map_irq`, SSB/BCMA-specific `bcm47xx_pcibios_plat_dev_init_*` helpers under config guards, and `pcibios_plat_dev_init`.

## Control Flow
Generic IRQ mapping returns 0, while platform device init dispatches by `bcm47xx_bus_type`. SSB path calls SSB PCI init, reads the PCI interrupt pin, maps IRQ through SSB, validates IRQ >= 2, and writes `dev->irq`. BCMA path calls BCMA init and IRQ mapping similarly.

## State And Persistence
No persistent software state beyond assigning `dev->irq` during device init. Uses external `bcm47xx_bus_type`.

## Dependencies And Integration Points
Depends on SSB and/or BCMA core PCI helpers, BCM47xx platform bus type, and PCI core callbacks.

## Risks And Edge Cases
Returning 0 from `pcibios_map_irq` means the real mapping must happen in platform init. IRQ values below 2 are rejected because they are software interrupts. Builds without matching SSB/BCMA support leave devices unchanged.

## Test Signals
BCM47xx SSB and BCMA board boot, PCI device init logs, IRQ assignment, and failed-map error paths are useful signals.
