# sources/distributed-fs/ceph-client/drivers/pci/search.c

## Purpose
`search.c` provides PCI core lookup and iteration helpers for buses and devices, plus DMA requester-ID alias iteration. It is a shared kernel API surface used by drivers, subsystems, and legacy interfaces that need to locate PCI devices by bus address, ID table, class code, or root-bus topology.

## Important APIs, types, and functions
The file defines `pci_bus_sem`, the read/write semaphore protecting global PCI bus and per-bus device lists. `pci_for_each_dma_alias()` walks a device's real DMA identity, explicit `dma_alias_mask`, and upstream bridge aliasing rules. Bus lookup is implemented by `pci_find_next_bus()`, `pci_find_bus()`, and recursive `pci_do_find_bus()`. Device lookup includes `pci_get_slot()`, `pci_get_domain_bus_and_slot()`, `pci_get_subsys()`, `pci_get_device()`, `pci_get_device_reverse()`, `pci_get_class()`, `pci_get_base_class()`, and `pci_dev_present()`. Public helpers export symbols and consistently return referenced `struct pci_dev *` values where the caller must call `pci_dev_put()`.

## Control flow and behavior
DMA alias iteration starts at `pci_real_dma_dev()`, calls the callback for the primary requester ID, then for any alias mask entries, then walks upstream until a root bus or a bridge marked `PCI_DEV_FLAGS_BRIDGE_XLATE_ROOT`. PCIe bridge type controls whether the alias remains the downstream device, becomes the bridge, or uses subordinate bus 0. Bus lookup walks `pci_root_buses` under `pci_bus_sem`, then searches child lists recursively. Device lookup uses either protected per-bus list traversal or `bus_find_device()`/`bus_find_device_reverse()` against `pci_bus_type`.

## State and persistence
The file does not persist state itself beyond the exported `pci_bus_sem`. It manipulates object lifetimes through `pci_dev_get()` and `pci_dev_put()`. `pci_dev_present()` intentionally returns only a momentary hint with no held reference after it exits.

## Dependencies and integration points
It depends on `linux/pci.h`, the driver core bus model, PCI device ID matching, `pci_root_buses`, bridge flags, and `pci_match_one_device()`. `pci_get_domain_bus_and_slot()` is used by the PCI config syscalls and TSM helpers in this subset.

## Risks
Callers must honor reference-count rules, especially continuation searches where the `from` argument is put by the search helper. `pci_dev_present()` can race hot removal by design. DMA alias rules are architecture and bridge-behavior sensitive, so regressions can break IOMMU grouping or DMA isolation.

## Test signals
Useful signals include hotplug add/remove lookup races, reference leak checks, reverse and forward ID iteration, class matching with wildcard IDs, IOMMU alias tests behind PCIe-to-PCI bridges, and boot logs for devices with `dma_alias_mask` or bridge alias flags.
