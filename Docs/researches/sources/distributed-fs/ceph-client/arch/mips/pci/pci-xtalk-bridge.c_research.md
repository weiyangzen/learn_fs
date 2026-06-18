## sources/distributed-fs/ceph-client/arch/mips/pci/pci-xtalk-bridge.c

### Purpose
This file implements SGI Xtalk Bridge PCI host support. It provides DMA address translation, config-space access including IOC3 emulation, bridge interrupt domains, board-specific IOC3 subsystem/interrupt setup from NVMEM, host bridge probing/removal, and platform-driver registration.

### Important APIs, Types, And Functions
Exports include `phys_to_dma()` and `dma_to_phys()`. Config helpers are `ioc3_cfg_rd/wr()`, `pci_conf0/1_read_config()`, `pci_conf0/1_write_config()`, and `bridge_pci_ops`. IRQ support uses `bridge_irq_chip_data`, `bridge_irq_chip`, `bridge_domain_ops`, `bridge_map_irq()`, and affinity/activate/deactivate callbacks. Board setup helpers populate `ioc3_sid` and `int_mapping`. `bridge_get_partnum()` reads and CRC-validates NVMEM PROM contents. `bridge_probe()` and `bridge_remove()` manage the host bridge.

### Control Flow
Probe defers until bridge NVMEM is available, creates a child IRQ domain under the default domain, allocates a `pci_host_bridge` with private `bridge_controller`, adds memory/I/O/bus resources with offsets, requests resources, initializes bridge registers and interrupt routing defaults, disables or enables swapping/page-size bits, applies board setup based on part number, sets PCI ops/map_irq/swizzle, scans the root bus, claims firmware resources, and adds devices. Removal tears down IRQ domain and root bus under PCI rescan locks.

### State, Persistence, And Dependencies
State spans bridge MMIO registers, per-slot IOC3 subsystem IDs, cached PCI interrupt virqs, IRQ domain/fwnode, DMA base address, resource windows, and platform driver data. Dependencies include SGI Bridge register definitions, DBE-safe accessors, NVMEM, CRC16, irqdomain hierarchy, PCI host-bridge APIs, and Xtalk platform data.

### Integration Points
It drives `xtalk-bridge` platform devices and supports SGI IOC3 quirks used by IP27/IP29/IP30/IP34 systems. `pci-ip27.c` consumes the resulting bridge controller for NUMA node mapping and IOC3 fixups.

### Risks
IOC3 emulation is deliberately partial; unmodeled config registers return zero or ignore writes. `bridge_domain_free()` returns early when `nr_irqs` is nonzero, which is unusual and worth reviewing. Part-number matching depends on PROM CRC and NVMEM device naming. Type 1 access is acknowledged as poorly documented.

### Test Signals
Validate NVMEM deferral, PROM part matching, IOC3 subsystem IDs, PCI config reads behind root and subordinate buses, IRQ allocation/affinity on NUMA systems, DMA address round trips, and clean platform removal.
