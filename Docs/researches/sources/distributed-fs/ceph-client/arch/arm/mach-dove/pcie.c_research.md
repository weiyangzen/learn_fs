# sources/distributed-fs/ceph-client/arch/arm/mach-dove/pcie.c

Purpose: supplies legacy PCIe host-controller support for the two Marvell Dove PCIe ports.

Important APIs/types/functions: `struct pcie_port`, `dove_pcie_setup()`, config accessors `pcie_rd_conf()`/`pcie_wr_conf()`, root-complex fixup `rc_pci_fixup()`, `dove_pcie_scan_bus()`, `dove_pcie_map_irq()`, `add_pcie_port()`, and `dove_pcie_init()`.

Control flow: init checks each requested port's link status, enables its clock, records the base, and calls `pci_common_init()`. Setup assigns bus numbers, maps IO space, requests MEM windows, and adds resources. Config access is serialized per-port and rejects impossible local-bus device numbers.

State and persistence: `pcie_port[]`, `num_pcie_ports`, resource windows, enabled clocks, and `vga_base` persist for PCI core use.

Dependencies and integration: depends on Orion PCIe helpers, ARM legacy PCI APIs, Dove MBUS windows from `common.c`, clock lookup, and IRQ definitions.

Risks: panics if PCIe memory resource request fails. Link-down ports are ignored, changing controller numbering. Legacy PCI APIs and fixed windows complicate migration to DT PCIe.

Test signals: PCI enumeration on both ports, config-space read/write correctness, root-complex class fixup, IRQ routing, and link-down boot behavior.
