# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_sysfs.c

## Purpose
Adds a controller-level SHPC sysfs attribute that reports free subordinate bus resources for debugging and management.

## Important APIs, Types, and Functions
Public functions are `shpchp_create_ctrl_files()` and `shpchp_remove_ctrl_files()`. The `ctrl` device attribute is read-only and implemented by `show_ctrl()`.

## Control Flow
`show_ctrl()` obtains the bridge subordinate bus, emits free non-prefetchable memory, prefetchable memory, I/O resources, and a simple free bus-number range by scanning for the first unused bus number.

## State and Persistence Behavior
No persistent state is stored beyond the device attribute registration. Output reflects current PCI bus resource lists at read time.

## Dependencies and Integration Points
Depends on PCI device/sysfs APIs and resource iteration. It is created after SHPC probe and removed before controller release.

## Risks
The bus-number reporting only shows the first contiguous gap discovered by `pci_find_bus()`. The output is diagnostic and not synchronized against concurrent resource changes beyond normal sysfs/device lifetime assumptions.

## Test Signals
Read the `ctrl` attribute on SHPC bridges with free memory, prefetchable memory, I/O, and bus-number resources; validate removal on driver unbind and behavior with no subordinate resources.
