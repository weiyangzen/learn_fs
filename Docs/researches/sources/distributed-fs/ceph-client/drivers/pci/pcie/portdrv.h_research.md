<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.h -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.h

## Purpose
`portdrv.h` defines the private PCIe port-service bus ABI shared by `portdrv.c` and service drivers. It identifies service bits, declares service initialization hooks, defines synthetic service device/driver structures, and provides optional-feature stubs.

## Important APIs, Types, and Functions
Service bit definitions are `PCIE_PORT_SERVICE_PME`, `AER`, `HP`, `DPC`, and `BWCTRL`, with `PCIE_PORT_DEVICE_MAXSERVICES` set to five. `struct pcie_device` contains the service IRQ, parent PCI port, service bit, private service data, and embedded `struct device`. `struct pcie_port_service_driver` contains probe/remove/PM/reset callbacks, port type match, service bit, and embedded `device_driver`. Helper APIs include `set_service_data()`, `get_service_data()`, `pcie_port_service_register()`, `pcie_port_service_unregister()`, `pcie_port_find_device()`, PME MSI controls, and CXL RCH AER hooks.

## Control Flow and State
`portdrv.c` allocates one `pcie_device` per detected service and matches it with a `pcie_port_service_driver` by service bit and port type. Each service stores private state through `priv_data`. Configuration stubs make absent services return no-op success or harmless defaults, allowing initialization fan-out in `portdrv.c` to remain unconditional.

## Dependencies and Integration Points
The header is included by AER, AER injection, CXL RCH handling, bandwidth control, DPC, EDR, PME, and port driver code. It also bridges hotplug via `pcie_hp_init()` and provides global policy state `pcie_ports_dpc_native`.

## Risks and Test Signals
Risks include adding a new service without updating `PCIE_PORT_DEVICE_MAXSERVICES`, mismatched shift/bit ordering with IRQ arrays, lifetime mistakes with service `priv_data`, and stub behavior diverging from enabled implementations. Tests should build all service combinations, verify service device names and matching, shared IRQ assignment, and lookup through `pcie_port_find_device()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.h -->
