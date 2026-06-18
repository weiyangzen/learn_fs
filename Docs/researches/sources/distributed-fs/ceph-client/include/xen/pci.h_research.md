# sources/distributed-fs/ceph-client/include/xen/pci.h

## Purpose
`pci.h` declares Linux Xen PCI helper functions for dom0 device reset and device-domain ownership tracking, with safe stubs when dom0 support is disabled.

## Important APIs, Types, and Functions
The exported helpers are `xen_reset_device()`, `xen_find_device_domain_owner()`, `xen_register_device_domain_owner()`, and `xen_unregister_device_domain_owner()`. Non-`CONFIG_XEN_DOM0` stubs return `-1`.

## Control Flow
Dom0 PCI code can reset a device through Xen-aware paths and register which domain owns a PCI device. In non-dom0 builds, callers receive failure immediately and should follow non-Xen or unsupported paths.

## State and Persistence Behavior
Real implementations maintain runtime ownership association between PCI devices and Xen domains and may trigger hypervisor reset bookkeeping. This header stores no state itself.

## Dependencies and Integration Points
It depends on `struct pci_dev` declarations from users. It integrates Linux PCI passthrough, dom0 device assignment, Xen physdev reset notification, and hotplug/remove paths.

## Risks and Test Signals
Risks include ownership leaks, reset without hypervisor notification, stubs being treated as success, and races during device removal. Test signals include dom0 passthrough attach/detach, reset paths, owner lookup consistency, and non-dom0 build coverage.
