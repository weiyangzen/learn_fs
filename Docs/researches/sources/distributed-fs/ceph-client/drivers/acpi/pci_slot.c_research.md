<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_slot.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_slot.c

## Purpose
`pci_slot.c` creates Linux `pci_slot` objects from ACPI slot metadata below a PCI bus bridge. It finds ACPI device children with `_ADR` and `_SUN`, names slots by the slot user number, and removes those slot objects when the bus is removed.

## Important APIs, Types, and Functions
`struct acpi_pci_slot` links a `struct pci_slot` into the module-global slot list. Public functions are `acpi_pci_slot_enumerate()`, `acpi_pci_slot_remove()`, and `acpi_pci_slot_init()`. Internal helpers are `check_slot()`, `register_slot()`, and the DMI callback `do_sta_before_sun()`.

## Control Flow and State
Enumeration obtains the ACPI handle for `bus->bridge`, locks `slot_list_lock`, and walks one ACPI namespace level below the bridge. `check_slot()` optionally evaluates `_STA` first on quirked systems, reads `_ADR` to obtain the PCI device number, and requires `_SUN` to identify a real slot. `register_slot()` skips duplicate bus/device slots, allocates wrapper state, calls `pci_create_slot()`, appends it to `slot_list`, and holds a reference on the PCI bus device. Removal walks the global list, destroys slots for the removed bus, drops bus references, and frees wrappers.

## State and Persistence
Persistent state is the global `slot_list`, each created `pci_slot`, and the `check_sta_before_sun` DMI quirk flag. There is no stored firmware state; slot objects reflect current ACPI namespace and PCI bus lifetime.

## Dependencies and Integration Points
The file depends on ACPI namespace walking, `_ADR`, `_SUN`, optional `_STA`, PCI slot core APIs, DMI matching, and PCI bus bridge ACPI handles. It is called by PCI/ACPI bus setup and teardown.

## Risks and Test Signals
Risks include ignoring allocation failure during namespace walk, duplicate suppression only by bus/device, `_SUN` side effects on absent Fujitsu PRIMEQUEST slots unless the DMI quirk fires, and slot names limited to numeric strings. Test signals are `/sys/bus/pci/slots` entries with expected names, no duplicate slots for multifunction devices, correct behavior on Fujitsu PRIMEQUEST firmware, and slot cleanup when a hot-added root bus is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_slot.c -->
