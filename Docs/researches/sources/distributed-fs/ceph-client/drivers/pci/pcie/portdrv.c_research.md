<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.c

## Purpose
`portdrv.c` is the PCIe port bus driver. It binds to PCIe Root/Upstream/Downstream Ports and RCECs, discovers native services, allocates service IRQs, creates child `pcie_device` instances on the `pci_express` bus, registers service drivers, fans out PM callbacks, and integrates port devices with PCI error recovery and runtime PM.

## Important APIs, Types, and Functions
Important types include `struct portdrv_service_data`, `struct pcie_device`, and `struct pcie_port_service_driver`. Exported APIs are `pcie_port_find_device()`, `pcie_port_service_register()`, and `pcie_port_service_unregister()`. Key internals include `pcie_message_numbers()`, `pcie_port_enable_irq_vec()`, `pcie_init_service_irqs()`, `get_port_device_capability()`, `pcie_device_init()`, `pcie_port_device_register()`, `pcie_port_device_remove()`, `pcie_port_bus_match()`, `pcie_port_bus_probe()`, `pcie_port_bus_remove()`, and `pcie_portdrv_probe()`.

## Control Flow and State
At device init, `pcie_portdrv_init()` registers service drivers for AER, PME, DPC, bandwidth control, and hotplug, applies DMI PME MSI quirks, then registers the PCI driver. Probe validates PCIe port/RCEC type, links RCECs, enables the PCI device, discovers service capability based on port type, native ownership, AER availability, DPC capability, hotplug, PME, and bandwidth notification support, allocates MSI-X/MSI or INTx vectors, creates child service devices, saves port state, and enables runtime PM if bridge D3 is possible. Remove/shutdown unregister children, frees vectors, and disables the port device.

## Dependencies and Integration Points
The driver depends on host bridge `_OSC` ownership flags, boot parameters `pcie_ports=compat/native/dpc-native`, PCI IRQ vector allocation, DMI, runtime PM, RCEC support, AER/PME/DPC/bwctrl/hotplug init functions, and PCI core error handlers. Service files under `pcie/` register against `pcie_port_bus_type` and receive their synthetic device plus IRQ from this driver.

## Risks and Test Signals
Risks include incorrect service discovery when firmware retains ownership, bad MSI message number handling, shared-vector interactions among PME/hotplug/bwctrl, leaking child devices or IRQ vectors on partial failure, and runtime D3 breaking config accesses. Tests should cover native and firmware-owned ACPI systems, `pcie_ports` boot options, MSI/MSI-X/INTx fallback, RCEC service creation, runtime suspend/resume, service probe failure paths, and PCI error recovery callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/portdrv.c -->
