# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/libata-portmap.h

Purpose: maps legacy ATA primary and secondary IRQ lookups to PowerPC PCI legacy IDE IRQ helpers.

Important APIs/types/functions: `ATA_PRIMARY_IRQ(dev)` expands to `pci_get_legacy_ide_irq(dev, 0)` and `ATA_SECONDARY_IRQ(dev)` expands to `pci_get_legacy_ide_irq(dev, 1)`.

Control flow: libata PCI drivers call the macros while probing legacy IDE compatibility channels.

State and persistence: no state; IRQ routing is queried from PCI/platform firmware.

Dependencies and integration points: depends on PCI legacy IRQ infrastructure and integrates libata with PowerPC PCI host bridges.

Risks: firmware or host bridge bugs in legacy IRQ routing propagate directly to ATA probe. The macro assumes channel indexes 0 and 1 match primary/secondary IDE.

Test signals: boot PowerPC platforms with legacy IDE, verify libata detects both channels and receives interrupts, and test with PCI host bridges that provide nonstandard legacy routing.
