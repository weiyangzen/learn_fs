# sources/distributed-fs/ceph-client/drivers/edac/edac_pci.c

## Purpose
This file implements EDAC's PCI controller abstraction. It allocates `edac_pci_ctl_info` objects, tracks registered PCI EDAC controllers in a global ordered list, schedules polling checks, and provides a generic PCI parity polling controller.

## Important APIs and Functions
Exported APIs are `edac_pci_alloc_ctl_info()`, `edac_pci_free_ctl_info()`, `edac_pci_alloc_index()`, `edac_pci_add_device()`, `edac_pci_del_device()`, `edac_pci_create_generic_ctl()`, and `edac_pci_release_generic_ctl()`. Internal helpers include `find_edac_pci_by_dev()`, `add_edac_pci_to_global_list()`, `del_edac_pci_from_global_list()`, and `edac_pci_workq_function()`.

## Control Flow
A low-level driver allocates a controller, fills device/module/check fields, then calls `edac_pci_add_device()`. Add assigns an index, inserts the controller under `edac_pci_ctls_mutex`, creates sysfs, and either schedules delayed polling work or marks the controller interrupt-driven. The work function checks the current op state, calls `edac_check()` when global policy allows, and requeues itself using the sysfs-configured poll interval. Removal marks the controller offline, removes it from the RCU-protected list, stops polling work, and returns the object to the caller for final release.

## State and Persistence
Runtime state is the global `edac_pci_list`, `edac_pci_ctls_mutex`, atomic `pci_indexes`, per-controller counters, op state, delayed work, and private driver data. No state persists beyond kernel runtime.

## Dependencies and Integration
The file depends on `edac_pci.h`, `edac_module.h`, the EDAC workqueue, PCI parity sysfs helpers, and kernel list/RCU/mutex/workqueue APIs. The generic controller bridges old memory-controller drivers to EDAC PCI parity scanning.

## Risks
The list is protected by mutex for mutation and uses RCU deletion to tolerate asynchronous readers such as NMI paths. Allocation stores optional `pvt_info` separately; the visible free path delegates to sysfs/kobject release, so private-data lifetime should be reviewed when adding users. Add failure paths must keep list and sysfs creation balanced.

## Test Signals
Tests should register and remove both polling and interrupt-style controllers, verify `/sys/devices/system/edac/pci/pciN` creation/removal, confirm delayed work stops on removal, and validate duplicate device/index rejection.
