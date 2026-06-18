# sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480ht.c

## Purpose
Implements BCM1480/BCM1455 HyperTransport support exposed through the PCI subsystem.

## Important APIs, Types, And Functions
Defines `bcm1480ht_pci_ops`, `bcm1480ht_controller`, global `ht_eoi_space`, and `bcm1480ht_pcibios_init`.

## Control Flow
Init maps 16 MiB HT config space, marks the bus enabled, maps the 4 MiB HT EOI special region, maps HT I/O space, sets `io_map_base`, and registers a secondary PCI controller with `get_busno` returning 0. Config access mirrors the BCM1480 PCI path using the HT config mapping and access gating.

## State And Persistence
Global `ht_cfg_space`, `ht_eoi_space`, and `bcm1480ht_bus_status` persist for the boot lifetime. Hardware mappings remain active until reboot.

## Dependencies And Integration Points
Depends on SiByte BCM1480 HT register definitions, MIPS I/O mapping, and PCI controller registration.

## Risks And Edge Cases
Always scans because firmware may not initialize all HT paths, increasing reliance on absent-device behavior. Large config and EOI mappings consume kernel virtual space. Device-mode handling is minimal.

## Test Signals
BCM1480 HT devices, interrupt EOI users, config scanning, and secondary-controller registration are main validation signals.
