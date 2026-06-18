# sources/distributed-fs/ceph-client/drivers/pci/slot.c

## Purpose
`slot.c` implements sysfs-visible physical PCI slot objects under `/sys/bus/pci/slots`, including naming, default attributes, device-to-slot association, reference management, and hotplug-driver integration.

## Important APIs, types, and functions
It exports `pci_slots_kset`, `pci_create_slot()`, and `pci_destroy_slot()`. It defines the `pci_slot_ktype`, sysfs ops for `struct pci_slot_attribute`, default attributes `address`, `max_bus_speed`, and `cur_bus_speed`, and helpers `make_slot_name()`, `rename_slot()`, `pci_dev_assign_slot()`, and `get_slot()`.

## Control flow and behavior
Initialization creates the global `slots` kset under the PCI bus kset. `pci_create_slot()` serializes on `pci_slot_mutex`, reuses existing `(bus, slot_nr)` slots except placeholder `-1` slots, optionally lets hotplug drivers rename unclaimed slots, allocates and names new slots while avoiding duplicate sysfs names by suffixing `-N`, attaches the kobject, and assigns matching existing devices' `dev->slot` pointers under `pci_bus_sem`. `pci_destroy_slot()` simply drops the kobject reference; `pci_slot_release()` clears matching devices' slot pointers, removes the slot from the bus list, drops the bus reference, and frees memory.

## State and persistence
Persistent kernel state includes `pci_slots_kset`, each bus's `slots` list, kobject references, `slot->hotplug`, `slot->number`, and each device's `dev->slot` pointer. Sysfs files expose derived address and bus speed data.

## Dependencies and integration points
It integrates with the PCI bus kset, hotplug drivers, `pci_bus_sem`, `pci_slot_mutex`, kobject/sysfs infrastructure, and optional `ARCH_PCI_SLOT_GROUPS`.

## Risks
Incorrect reference balancing can leak slots or free objects while devices still point at them. Slot name collisions are expected on broken firmware and must remain ABI-compatible. Bus-wide slots using `PCI_SLOT_ALL_DEVICES` must correctly match ARI or multi-device slot semantics.

## Test signals
Use hotplug driver create/destroy cycles, duplicate firmware slot names, placeholder slots, bus-wide PCIe slots, sysfs attribute reads, and device insertion after slot creation to verify `pci_dev_assign_slot()`.
