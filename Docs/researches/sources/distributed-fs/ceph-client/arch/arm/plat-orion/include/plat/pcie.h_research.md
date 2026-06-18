# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/pcie.h

Purpose: Declares Orion PCIe controller helpers used by machine PCI setup code.

Important APIs: Register/query helpers include `orion_pcie_dev_id`, `orion_pcie_rev`, `orion_pcie_link_up`, `orion_pcie_x4_mode`, `orion_pcie_get_local_bus_nr`, `orion_pcie_set_local_bus_nr`, `orion_pcie_reset`, and `orion_pcie_setup`. PCI config accessors include normal, TLP workaround, memory-window workaround read paths, and write path.

Control flow/state: Callers map the PCIe controller and call setup/reset before host bridge enumeration. Config accessors operate directly on controller MMIO registers and the Linux `pci_bus`/`devfn` addressing model.

Dependencies/integration: Depends on `struct pci_bus`, Linux fixed-width types, and implementation in `pcie.c`. Integrates with ARM PCI host setup and MBus address-window code.

Risks/tests: Incorrect use of the three config read variants can produce broken enumeration on affected hardware. Tests should include link-up/down, local bus-number programming, x1/x4 mode detection, and config byte/word/dword reads and writes.
