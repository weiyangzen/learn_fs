# sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_64.c

Purpose: this file supplies 64-bit PowerPC PCI initialization, PHB IO-space mapping/unmapping, the 64-bit `pciconfig_iobase` syscall compatibility path, NUMA lookup for PCI buses, and PMAC OF-node device translation.

Important APIs and functions: `pci_io_base` is exported as the base for IO BAR offsets. `pcibios_init()` is a synchronous subsys initcall that sets `ppc_md.phys_mem_access_prot`, enables PCI domains, scans each PHB, runs common resource survey, adds devices, and runs machine fixups. `pcibios_unmap_io_space()` handles PHB and bridge hot-unmap cases. `ioremap_phb()` allocates virtual space between `PHB_IO_BASE` and `PHB_IO_END` and maps physical IO pages. `pcibios_map_io_space()` and `pcibios_setup_phb_io_space()` map PHB IO resources. `pcibus_to_node()` returns PHB NUMA node when enabled. `pci_device_from_OF_node()` reads `PCI_DN` bus/devfn for PMAC.

Control flow: the 64-bit path scans PHBs before adding devices, unlike the 32-bit path that adds devices per hose before the resource survey. IO mapping aligns the physical base and size to pages, records `io_base_alloc`, computes `io_base_virt`, and adjusts `io_resource` by `pcibios_io_space_offset()`. Unmapping a bridge flushes hash-table entries for the bridge IO range on Book3S; unmapping a PHB iounmaps the stored allocation.

State and persistence: PHB IO mapping state lives in `io_base_phys`, `pci_io_size`, `io_base_alloc`, `io_base_virt`, and adjusted `io_resource`. Domain/proc visibility is controlled with PCI flags. The syscall uses `pci_root_buses` and DT-backed `PCI_DN(hose_node)->phb` to recover the controller.

Dependencies and integration points: depends on VM area allocation, page-range ioremap, hash MMU flushing, OF compatibility checks for MacRISC4 AGP routing, generic PCI root bus lists, `pci-common.c` scanning/resource code, and platform callbacks.

Risks: IO mapping requires page-aligned inputs and enough virtual address space in the PHB IO region. Hot-unmap for bridges only flushes hash entries and assumes page tables remain valid, which is architecture-specific. `pciconfig_iobase` is not domain-correct and returns the first matching root bus. The MacRISC4 AGP special case is intentionally compatibility-driven and fragile.

Test signals: 64-bit boot should show PCI probing done, devices added after resource survey, and valid `/proc` domain behavior. Hotplug tests should exercise PHB unmap and bridge hash flush. NUMA tests should confirm PCI devices inherit the PHB node. Legacy users of `pciconfig_iobase` should receive stable IO and memory bases.
