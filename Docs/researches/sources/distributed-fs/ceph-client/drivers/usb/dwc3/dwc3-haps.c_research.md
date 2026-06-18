# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-haps.c

## Purpose
`dwc3-haps.c` is a PCI glue driver for Synopsys HAPS DWC3/USB3 prototyping boards. It turns a PCI function into a child `dwc3` platform device with memory and IRQ resources plus software properties needed by the common core.

## Important APIs, Types, and Functions
`struct dwc3_haps` stores the child platform device and PCI device. `initial_properties` supplies `snps,usb3_lpm_capable`, `snps,has-lpm-erratum`, `snps,dis_enblslpm_quirk`, and `linux,sysdev_is_parent` through `dwc3_haps_swnode`. Main functions are `dwc3_haps_probe()` and `dwc3_haps_remove()`.

## Control Flow
Probe enables the PCI device with managed PCI helpers, sets bus master, allocates private state, allocates a `dwc3` platform device, builds two resources from PCI BAR0 and PCI IRQ, adds resources to the child, sets the PCI device as parent, attaches the software node, adds the platform device, and stores driver data. On failure it removes the software node and drops the platform device. Remove removes the software node and unregisters the child.

## State and Persistence Behavior
State is limited to the child platform device pointer and PCI pointer. The child DWC3 core owns controller runtime state after platform-device registration. No persistent storage exists.

## Dependencies and Integration Points
The driver integrates the PCI subsystem, platform device creation, software nodes/properties, and the common `dwc3` platform driver. PCI IDs cover Synopsys HAPS USB3, HAPS USB3 AXI, and HAPS USB31 devices, with a class mask on one ID to avoid binding unrelated i.MX PCIe controllers sharing VID/PID.

## Risks
Resource translation must be correct because BAR0 is passed directly to the common core. Software-node properties change core behavior globally for this child, especially LPM erratum and ENBLSLPM quirk. Incorrect PCI class matching could bind non-USB hardware. Cleanup must remove the software node before unregistering or dropping the child.

## Test Signals
Test PCI probe/remove on all IDs, child `dwc3` platform probe, BAR and IRQ visibility in the child, DMA through the PCI parent due to `linux,sysdev_is_parent`, class-mask non-match on known conflicting controllers, and no software-node leak across reprobe.
