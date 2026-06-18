<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/host-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/pci/host-bridge.c

## Purpose
Provides small host-bridge helper routines for locating the root host bridge, managing host-bridge device references, installing release callbacks, and translating resources between CPU physical addresses and PCI bus address regions.

## Important APIs, Types, and Functions
Exports `pci_find_host_bridge()`, `pci_get_host_bridge_device()`, `pci_set_host_bridge_release()`, `pcibios_resource_to_bus()`, and `pcibios_bus_to_resource()`. Internal helpers are `find_pci_root_bus()` and `region_contains()`.

## Control Flow
Root-bus lookup walks `bus->parent` to the top and converts `root_bus->bridge` into `struct pci_host_bridge`. Resource-to-bus translation finds the host bridge window containing the resource and subtracts the window offset. Bus-to-resource translation searches windows of the same resource type, constructs the bus-visible region for each, chooses the one containing the requested bus region, and adds the offset to produce CPU resource coordinates.

## State and Persistence
This file owns no persistent state. It reads the host bridge `windows` list and manipulates references to existing bridge devices. Release callback data is stored in `struct pci_host_bridge`.

## Dependencies and Integration Points
Depends on core PCI bus/host bridge structures and resource window lists. It is used by ACPI hotplug helpers and other PCI code needing host-bridge lookup or address translation.

## Risks and Edge Cases
If no matching window is found, translations use offset zero; callers must ensure windows are populated for non-identity mappings. `pci_get_host_bridge_device()` manually increments the kobject reference and must be balanced by `pci_put_host_bridge_device()`. Resource type matching matters for bus-to-resource translation.

## Test Signals
Validate translations on systems with identity and non-identity host bridge windows, IO versus memory windows, nested PCI buses, host bridge reference get/put balancing, and callers using `pci_find_host_bridge()` on child buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/host-bridge.c -->
