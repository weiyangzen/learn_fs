# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_core.c

## Purpose
Implements pSeries RPA DLPAR add/remove orchestration for PCI slots, PHBs, and VIO slots. It maps a user-provided DRC name to a device-tree node and then creates or removes kernel PCI/VIO/hotplug representations.

## Important APIs, Types, and Functions
Public functions are `dlpar_add_slot()` and `dlpar_remove_slot()`. Internal helpers include `find_dlpar_node()`, `find_php_slot()`, `dlpar_pci_add_bus()`, `dlpar_add_pci_slot()`, `dlpar_remove_pci_slot()`, `dlpar_add_phb()`, `dlpar_remove_phb()`, `dlpar_add_vio_slot()`, `dlpar_remove_vio_slot()`, and `is_dlpar_capable()`. `rpadlpar_mutex` serializes all DLPAR operations.

## Control Flow
Add/remove first acquire `rpadlpar_mutex`, find a VIO, PCI slot, or PHB node by DRC properties, dispatch by node type, put the OF node reference, and release the mutex. PCI slot add creates the PCI bus/device for the EADS bridge, scans below bridges, maps IO space, finishes PCI bus addition, confirms the bridge, and registers an rpaphp hotplug slot. PCI slot removal deregisters the hotplug slot, removes devices below the bus, unmaps IO space, and removes the bridge device. PHB add/remove use dynamic PHB platform helpers, while VIO add/remove register or unregister VIO device nodes. Module init rejects partitions lacking the RTAS `ibm,configure-connector` token and creates the sysfs control group.

## State and Persistence Behavior
The file mutates the live OF-derived PCI/VIO topology, PCI buses/devices, dynamic PHB state, rpaphp slot list, and VIO device registration. It calls `vm_unmap_aliases()` after removal to flush stale vmalloc mappings. No on-disk persistence exists; partition firmware remains authoritative for DRC topology.

## Dependencies and Integration Points
Depends on RTAS token discovery, Open Firmware node traversal, pSeries PCI bridge APIs (`init_phb_dynamic`, `remove_phb_dynamic`, `of_create_pci_dev`, `of_scan_pci_bridge`), EEH initialization, VIO registration, rpaphp DRC property parsing/slot registration, and PCI rescan/remove locking.

## Risks
DLPAR add/remove is topology-sensitive: built-in DLPAR-capable nodes may not be hotpluggable, and `find_php_slot()` only sees rpaphp-registered slots. PCI removal assumes the located bus has a bridge device and uses `BUG_ON` in that path. Failure after creating a dynamic PHB or bus can leave partial topology if not unwound by callers. The mutex serializes user operations but does not by itself protect against all firmware or hotplug event races.

## Test Signals
Exercise sysfs DRC add/remove for VIO slots, PCI slots, and PHBs; duplicate add/remove; missing DRC names; EEH initialization; IO-space map/unmap failures; hotplug slot deregistration failures; dynamic PHB creation/removal; and concurrent add/remove attempts interrupted by signals.
