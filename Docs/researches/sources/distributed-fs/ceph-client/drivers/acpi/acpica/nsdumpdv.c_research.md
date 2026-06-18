<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdumpdv.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdumpdv.c

## Purpose
Contains obsolete, compile-gated debug helpers for dumping root devices and selected device identity data from the namespace.

## Important APIs, Types, And Functions
Under `ACPI_OBSOLETE_FUNCTIONS` and debug gates, defines `acpi_ns_dump_one_device` and `acpi_ns_dump_root_devices`. It uses `acpi_ns_dump_one_object`, `acpi_get_object_info`, `struct acpi_device_info`, and namespace walking for `ACPI_TYPE_DEVICE`.

## Control Flow
`acpi_ns_dump_root_devices` checks table-debug level, obtains the `\_SB_` handle, prints a heading, and walks all device objects below it. The per-device callback delegates generic object dumping, asks ACPICA for object info, then prints HID and ADR with indentation.

## State And Persistence
No persistent state is modified. It allocates and frees the temporary object-info buffer returned by `acpi_get_object_info`.

## Dependencies And Integration Points
Only compiled for obsolete debug configurations. Integrates with namespace dump support and object-info evaluation helpers that may evaluate device identification methods.

## Risks And Edge Cases
The module is explicitly marked obsolete. Because object info may depend on firmware methods, debug dumping can have side effects or fail on malformed devices. It silently returns if debug level is disabled or `\_SB_` is absent.

## Test Signals
Build with obsolete/debug options, enable table debug level, verify device listings under `\_SB_`, include devices with and without HID/ADR data, and confirm buffers from `acpi_get_object_info` are freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdumpdv.c -->
