# sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci_32.c

Purpose: this is the 32-bit PowerPC PCI initialization and compatibility layer. It supplies 32-bit globals, Open Firmware bus-number mapping for platforms that renumber PCI buses, 32-bit PHB IO resource adjustment, the 32-bit PCI initialization pass, and the `pciconfig_iobase` syscall implementation.

Important APIs and state: exported globals are `isa_io_base`, `pci_dram_offset`, and `isa_bridge_pcidev`. `pcibios_assign_bus_offset` controls spacing after scanned hose bus ranges. `pci_assign_all_buses` tracks reassignment mode. Under `CONFIG_PPC_PCI_OF_BUS_MAP`, `pci_to_OF_bus_map` and `pci_bus_count` maintain a kernel-to-firmware bus map. `pci_device_from_OF_node()` translates OF nodes to bus/devfn, optionally remapping through that table. `pci_create_OF_bus_map()` creates the root DT property used by `/proc` device tree consumers. `pcibios_setup_phb_io_space()` adjusts resource windows by the virtual IO offset. `pcibios_init()` scans all registered hoses and invokes common resource survey and machine fixups.

Control flow: after PHBs are discovered into `hose_list`, `subsys_initcall(pcibios_init)` probes all controllers. It may force bus reassignment based on PCI flags, sets first and last bus numbers, calls `pcibios_scan_phb()`, adds devices, updates the next bus number, optionally builds OF bus maps for PMAC/CHRP, runs `pcibios_resource_survey()`, and then calls machine `pcibios_fixup` and `pcibios_after_init`. The syscall finds a hose for a bus and returns bridge number, memory offset, IO base, ISA IO base, or ISA memory base.

State and persistence: persistent 32-bit PCI state is split between exported legacy base variables, the optional OF bus map, per-hose bus number ranges, and mutated IO resources. The root DT property for the OF bus map is allocated from memblock and persists for proc-device-tree consumers.

Dependencies and integration points: this file relies on `hose_list` and common scan/resource logic from `pci-common.c`, platform callbacks from `ppc_md`, Open Firmware node properties, generic PCI device lookup, memblock allocation for early properties, and compatibility with old users of `pciconfig_iobase`.

Risks: bus-map support assumes OF bridge nodes have usable `bus-range`, `class-code`, and `reg` properties. If buses are reassigned, OF-to-kernel translation can be ambiguous when several kernel buses match one OF bus. The syscall is legacy and domain-limited. The 32-bit IO resource adjustment mutates `hose->io_resource` in place and depends on common code having a valid virtual mapping.

Test signals: 32-bit PMAC/CHRP/PReP boots should show PCI probing, stable device discovery, and correct OF bus maps when bus reassignment is active. Regression checks include `pci_device_from_OF_node()` users, `pciconfig_iobase` return values for old X/server tooling, resource survey warnings, and machine fixup ordering.
