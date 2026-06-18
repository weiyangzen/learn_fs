# sources/distributed-fs/ceph-client/drivers/mcb/mcb-pci.c

## Purpose
`mcb-pci.c` implements the PCI carrier for MEN Chameleon Bus FPGA devices.

## Important APIs, Types, and Functions
Core elements are `struct priv`, `mcb_pci_get_irq()`, `mcb_pci_probe()`, `mcb_pci_remove()`, the PCI ID table for MEN and Altera vendor IDs with Chameleon device ID, and `mcb_pci_driver`.

## Control Flow, State, and Persistence
Probe enables the PCI device, sets bus mastering, rejects IO-mapped BAR0, maps an initial Chameleon header window, allocates an MCB bus, installs a carrier-specific IRQ callback that returns the PCI IRQ, parses Chameleon cells, optionally remaps to the exact table size, and attaches devices. Remove releases the bus and disables the PCI device. Runtime state is held in PCI drvdata and MCB bus/device structures. Persistent input is PCI configuration/resource state and FPGA descriptor memory.

## Dependencies and Integration Points
The file integrates PCI core probing, IO memory resource management, `chameleon_parse_cells()`, and MCB bus exports. It imports the `MCB` namespace.

## Risks and Test Signals
Risks include assuming descriptors live in BAR0, unsupported IO BARs, cleanup ordering after parse failures, and using one PCI IRQ for all child devices. Tests should cover probe failure at each step, table remapping, device remove with bound children, both vendor IDs, and PCI resource edge cases.
