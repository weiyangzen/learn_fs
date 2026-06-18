<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ibm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ibm.c

## Purpose
Provides IBM-specific ACPI PCI hotplug extensions. It registers an acpiphp attention LED provider, parses IBM `APCI` ACPI table data, evaluates `APLS` to set LEDs, synthesizes ACPI netlink events, and exposes the raw aPCI table through sysfs.

## Important APIs, Types, and Functions
`union apci_descriptor` models IBM table descriptors. `ibm_slot_from_id()` locates a slot descriptor by hotplug slot user number. `ibm_set_attention_status()` evaluates `APLS`. `ibm_get_attention_status()` derives LED state from table fields. `ibm_handle_events()` combines IBM notification subevents into netlink events. `ibm_get_table_from_acpi()` reads and concatenates `APCI` buffers. `ibm_read_apci_table()` serves `/sys/bus/pci/slots/apci_table`. Init/exit install/remove ACPI notify handler, sysfs file, and attention callbacks.

## Control Flow
Init walks the ACPI namespace looking for present devices with hardware ID `IBM37D0` or `IBM37D4`, fetches its ACPI device, registers attention callbacks with acpiphp, installs an ACPI device notify handler, sizes the APCI table, and creates the sysfs binary attribute. Setting LED state reads the current APCI table, maps Linux slot `_SUN` to IBM slot ID, and evaluates `APLS(slot_id, status)`. Reading the table re-evaluates `APCI`, validates it as a package of buffers, concatenates the buffers, and copies them to userspace only from offset zero.

## State and Persistence
Global state includes the IBM ACPI handle, a notification accumulator, the sysfs bin attribute size, and registered attention callbacks. APCI table contents are read fresh from firmware and not cached beyond temporary allocations.

## Dependencies and Integration Points
Depends on ACPI namespace walking/evaluation/notifications, acpiphp attention registration, PCI slots kset, sysfs binary attributes, and ACPI netlink event generation.

## Risks and Edge Cases
APCI parsing trusts descriptor lengths from firmware while walking a flat buffer; malformed tables can break lookup. The sysfs table read only supports whole-table reads from position zero. Notification synthesis uses a single global `ibm_note`, relying on ACPI serialization assumptions. Attention registration can fail if another provider is active. Init assumes `pci_slots_kset` is ready.

## Test Signals
Load on systems with and without IBM IDs, set/get attention LEDs, read `apci_table`, inject or observe ACPI notifications, test malformed/missing APCI/APLS firmware responses, and unload to confirm sysfs and notify handler cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ibm.c -->
