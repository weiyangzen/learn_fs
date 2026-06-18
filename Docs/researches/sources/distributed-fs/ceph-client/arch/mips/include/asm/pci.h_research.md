# sources/distributed-fs/ceph-client/arch/mips/include/asm/pci.h

Purpose: defines the MIPS architecture PCI interface between board-specific PCI host-controller code and common Linux PCI code.

Important APIs/types/functions: under `CONFIG_PCI_DRIVERS_LEGACY`, `struct pci_controller` holds the controller list node, root bus, OF node, `pci_ops`, memory/I/O resources and offsets, I/O map base, optional domain index/info, and optional bus-number get/set callbacks. Externs include `register_pci_controller`, `pcibios_map_irq`, `pcibios_plat_dev_init`, `pcibios_plat_setup`, `pci_load_of_ranges`, `PCIBIOS_MIN_IO`, and `PCIBIOS_MIN_MEM`. Inline helpers include `set_pci_need_domain_info`, `pcibios_assign_all_busses`, and `pci_proc_domain`; `pci_domain_nr` is defined for non-generic domains. Macros set CardBus minimum I/O and mmap support flags.

Control flow: board code registers controllers before scanning, optionally loads OF ranges, maps IRQs, and performs platform device initialization at enable time. Common PCI scanning asks `pcibios_assign_all_busses`, uses domain helpers, and maps PCI resources using architecture mmap support.

State and persistence: registered `pci_controller` instances are boot-lifetime kernel state in the PCI subsystem. Global minimum I/O/memory values guide resource allocation. Domain info affects procfs/sysfs representation.

Dependencies and integration points: includes Linux MM, ioport, list, OF, types, slab, scatterlist, string, and MIPS I/O helpers. It integrates with board PCI code, Open Firmware device trees, PCI resource allocation, DMA mapping, and arch-specific IRQ mapping.

Risks: legacy-controller definitions are conditional; callers must match `CONFIG_PCI_DRIVERS_LEGACY`. `pcibios_assign_all_busses` always returns 1, forcing bus renumbering and potentially differing from firmware assignments. Domain handling differs between generic and legacy domain configs. The extern `pcibios_plat_dev_init` is declared both inside and outside `__KERNEL__` blocks.

Test signals: PCI host-controller tests should verify controller registration, OF range parsing, bus numbering, domain numbers/proc-domain behavior, resource allocation above `PCIBIOS_MIN_*`, mmap support, IRQ mapping, and platform device init callbacks.
