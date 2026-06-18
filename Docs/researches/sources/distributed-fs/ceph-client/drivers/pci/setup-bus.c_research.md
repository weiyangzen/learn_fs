# sources/distributed-fs/ceph-client/drivers/pci/setup-bus.c

## Purpose
`setup-bus.c` is the PCI core bridge-window sizing and resource assignment engine. It sizes downstream I/O, MMIO, and prefetchable MMIO windows, assigns device and bridge resources, retries allocation by releasing bridge windows when needed, distributes hotplug headroom, and supports resizing/reassigning resources after enumeration.

## Important APIs, types, and functions
The key local type is `struct pci_dev_resource`, which snapshots a device resource, requested add-on size, minimum alignment, and original flags for retry/restore lists. Important exported or externally used APIs include `pci_flags`, `pci_dev_res_add_to_list()`, `pbus_select_window()`, `pci_resource_is_optional()`, `pci_bus_size_bridges()`, `pci_claim_bridge_resource()`, `pci_bus_assign_resources()`, `pci_bus_claim_resources()`, `pci_realloc_get_opt()`, `pci_assign_unassigned_root_bus_resources()`, `pci_assign_unassigned_resources()`, `pci_assign_unassigned_bridge_resources()`, `pci_do_resource_release_and_resize()`, and `pci_assign_unassigned_bus_resources()`. Weak hooks `pcibios_setup_bridge()` and `pcibios_window_alignment()` let architectures participate.

## Control flow and behavior
Sizing is depth-first. `__pci_bus_size_bridges()` first sizes subordinate buses, handles CardBus separately, checks bridge range support, accounts hotplug reserves, and calls `pbus_size_io()` and `pbus_size_mem()` for appropriate windows. Memory sizing buckets child BAR alignments, computes compact head alignment, treats SR-IOV, ROM, and empty bridge windows as optional, and can record optional growth in a realloc list.

Assignment is sorted by decreasing alignment. `pdev_sort_resources()` collects unassigned movable resources; `__assign_resources_sorted()` first tries required plus optional growth, then falls back to required resources, releasing same-type allocations when required resources fail. Bridge setup writes base/limit registers via `pci_setup_bridge_io()`, `pci_setup_bridge_mmio()`, and `pci_setup_bridge_mmio_pref()` after resources are assigned. Root assignment can perform multiple tries depending on `pci=realloc` policy and bus depth, releasing leaf or whole-subtree bridge windows before retrying.

Hotplug distribution starts with spare space in a hotplug bridge, subtracts already-needed device resources, and recursively splits surplus among hotplug bridges or normal bridges. Resizable BAR support releases affected BARs and upstream bridge windows, changes the BAR size, reassigns the hierarchy, and restores the old state if any required resource fails.

## State and persistence
The persistent state is the kernel resource tree (`struct resource` parent/child links), `struct pci_dev.resource[]`, bridge config-space windows, `pci_flags`, and the boot-time `pci_realloc_enable` policy. Temporary linked lists store snapshots for retries and are freed after each pass.

## Dependencies and integration points
This file integrates with `setup-res.c` for `pci_assign_resource()`, `pci_release_resource()`, and `pci_update_resource()`, with `setup-cardbus.c` for CardBus sizing/setup, with ACPI for `acpi_ioapic_add()`, with SR-IOV and resizable BAR helpers, and with architecture hooks for resource alignment and bridge programming.

## Risks
Resource sizing has high blast radius: bad alignment or optional-size accounting can leave devices unassigned, overlap bridge windows, or program invalid hardware ranges. Retry paths depend on faithfully restoring saved resource state. Locking matters around subtree resize because bridge reassignment walks global PCI topology under `pci_bus_sem`.

## Test signals
Relevant tests include multi-level bridge enumeration, hotplug bridges with spare capacity, SR-IOV BAR allocation with and without `pci=realloc`, 64-bit prefetchable windows, disabled/empty bridge windows, CardBus bridges, resizable BAR grow/shrink failure recovery, and boot logs containing assignment, release, restore, and "failed to assign" messages.
