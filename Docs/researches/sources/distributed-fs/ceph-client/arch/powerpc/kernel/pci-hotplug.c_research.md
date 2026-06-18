# sources/distributed-fs/ceph-client/arch/powerpc/kernel/pci-hotplug.c

Purpose: this file provides PowerPC-specific PCI hotplug helpers for finding buses by device-tree node, releasing `pci_dn` firmware data when a PCI device goes away, recursively removing devices below a bus, and adding newly visible devices to an existing bus.

Important APIs and functions: `pci_find_bus_by_node()` walks the PHB root bus children to find the `struct pci_bus` matching a DT node. `pcibios_release_device()` invokes optional PHB release callbacks and frees a deferred dead `pci_dn`. `pci_hp_remove_devices()` recursively descends child buses and calls `pci_stop_and_remove_bus_device()` in reverse device order. `pci_hp_add_devices()` chooses OF-rescan or normal probing based on `controller_ops.probe_mode`, scans slots and bridges, then calls `pcibios_finish_adding_to_bus()`. The helper `traverse_siblings_and_scan_slot()` maps DT children to slots for partial hotplug rescans.

Control flow: a hotplug add operation starts with a bus whose DT node still exists. In `PCI_PROBE_DEVTREE` mode the bus is rescanned by `of_rescan_bus()`. In normal mode, the code scans endpoint or bridge slots described by DT children, then performs two bridge scans: one for already configured bridges and one allowing reconfiguration. It finishes through common PCI code to claim or assign resources and register devices. Removal is bottom-up: child buses are processed first, then devices on the current bus are stopped and removed.

State and persistence: hotplug state is mostly held elsewhere, in `struct pci_bus`, `struct pci_dev`, DT nodes, PHB `controller_ops`, EEH state, and `pci_dn` objects. This file is responsible for final deferred freeing of `PCI_DN_FLAG_DEAD` objects during device release, which ties dynamic DT node removal to PCI core object lifetime.

Dependencies and integration points: it integrates with `pci_dn.c` for `PCI_DN()`/`pci_get_pdn()`, `pci_of_scan.c` for OF rescans, `pci-common.c` for final resource registration, generic PCI bridge/slot scanning, EEH, and platform-specific release hooks.

Risks: partial hotplug relies on DT child class codes and `PCI_DN(devfn)` data being accurate. The sibling scan has a subtle dependency on `start->child` while iterating children, so malformed or stale nodes can lead to skipped or repeated scans. Resource assignment is delegated after probing, so failures show up later. Removing devices while firmware data is still referenced requires the deferred `pci_dn` lifetime to be correct.

Test signals: hot-add should create only missing devices and then expose them in sysfs/proc. Hot-remove should remove child buses before parents and free dead `pci_dn` objects without use-after-free reports. Run with OF probe mode and normal probe mode, partial bridge removal, EEH-enabled kernels, and platform `release_device` callbacks.
