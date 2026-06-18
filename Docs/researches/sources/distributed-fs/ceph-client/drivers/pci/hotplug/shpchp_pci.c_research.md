# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_pci.c

## Purpose
Provides SHPC PCI device enumeration and removal for a specific conventional PCI slot device number below an SHPC-managed bridge.

## Important APIs, Types, and Functions
Public functions are `shpchp_configure_device()` and `shpchp_unconfigure_device()`, both operating on `struct slot` and its controller bridge/subordinate bus.

## Control Flow
Configure locks PCI rescan/remove, rejects an already existing device at the slot devfn, scans that slot, adds hotplug bridge metadata only for bridges in the target slot, assigns unassigned bridge resources, configures PCIe bus settings, and adds devices. Unconfigure locks rescan/remove, iterates subordinate devices, removes those whose PCI slot matches `p_slot->device`, and unlocks.

## State and Persistence Behavior
The code mutates the PCI device tree under the SHPC bridge and causes resource assignment/device binding through PCI core calls. It does not manage SHPC hardware state directly.

## Dependencies and Integration Points
Depends on PCI scanning/removal/resource assignment and is called by `board_added()` and `remove_board()` in `shpchp_ctrl.c`.

## Risks
It scans/removes by PCI slot number, which matches SHPC conventional PCI semantics but differs from pciehp's fixed function-0 model. It does not explicitly mark devices disconnected for surprise removal; higher-level SHPC handling must decide when removal is safe. Resource assignment affects the whole bridge.

## Test Signals
Hot-add endpoints and bridges at SHPC slot device numbers, duplicate device detection, no-device scan failure, resource assignment, driver binding, and removal of only devices in the target slot.
