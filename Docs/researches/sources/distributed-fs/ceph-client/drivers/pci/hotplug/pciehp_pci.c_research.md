# sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_pci.c

## Purpose
Provides PCI enumeration and removal helpers for pciehp once the hardware controller has determined that a slot should be added or removed.

## Important APIs, Types, and Functions
The file exports `pciehp_configure_device()` and `pciehp_unconfigure_device()`. Both operate on a pciehp `struct controller`, its PCIe port bridge, and the bridge subordinate bus.

## Control Flow
Hot-add locks PCI rescan/remove, rejects already-enumerated function 0, scans slot `00.0`, adds hotplug bridge metadata below any newly found bridges, assigns unassigned bridge resources, configures PCIe bus settings, temporarily drops `reset_lock` while binding drivers through `pci_bus_add_devices()`, then caches the downstream device serial number. Hot-remove optionally marks devices disconnected for surprise removal, locks rescan/remove, iterates the subordinate device list in reverse so VFs are removed before PFs, temporarily drops `reset_lock` around driver unbind/removal, and for safe removals disables bus mastering/SERR and masks INTx on each removed device.

## State and Persistence Behavior
The code mutates the PCI device tree under the hotplug bridge and updates `ctrl->dsn`. It relies on core PCI resource assignment to persist BAR/window programming and on `pci_dev_set_disconnected()` to prevent config accesses after surprise removal.

## Dependencies and Integration Points
Depends on the PCI core scanning, bridge resource assignment, bus settings, driver binding, and removal APIs. It is invoked by the pciehp state machine after `pciehp_hpc.c` has validated link/presence and controlled slot power.

## Risks
Dropping and reacquiring `reset_lock` around device bind/unbind is required to avoid AB-BA deadlocks; changing this ordering is risky. Reverse removal protects SR-IOV list iteration. Function-0-only scanning follows PCIe hotplug's one-device-per-slot model and is not suitable for arbitrary conventional PCI slots.

## Test Signals
Validate hot-add of endpoints and downstream bridges, resource assignment, driver autoload, SR-IOV PF/VF hot-remove, surprise removal disconnect marking, safe removal command-bit masking, and repeated add/remove under concurrent reset or driver probe activity.
