# sources/distributed-fs/ceph-client/arch/m68k/coldfire/pci.c

Purpose: ColdFire PCI host-bridge setup, configuration-space access, IRQ mapping, and root-bus scan.

Important APIs and data: globals `rootbus` and `iospace`; host slot/SID table `mcf_host_slot2sid[]`; IRQ table `mcf_host_irq[]`; `mcf_mk_pcicar()`, `mcf_pci_readconfig()`, `mcf_pci_writeconfig()`, `mcf_pci_ops`, PCI memory/IO/bus resources, `mcf_pci_map_irq()`, and `mcf_pci_init()` as `subsys_initcall()`.

Control flow and state: init allocates a host bridge, resets the external PCI bus, requests memory/IO resources, configures arbiter, pinmux, local host controller config, initiator and target windows, maps IO/config space with `ioremap()`, releases reset after a delay, scans the root bus, sizes/assigns resources, and adds devices. Config reads/writes enable `PCICAR`, access the IO window at `where & 3`, then disable config mode.

Dependencies and integration: Linux PCI core, ColdFire M54xx PCI registers, MMIO resource tree, IRQ swizzling, and memory map constants.

Risks and test signals: bus 0 probing is filtered by a fixed slot table; unsupported slots read as all-ones. No `ioremap` cleanup is done on scan failure after mapping. Test PCI enumeration, config read/write sizes/endian conversion, BAR assignment, DMA to RAM target window, and IRQ mapping for each populated slot.
