# sources/distributed-fs/ceph-client/drivers/xen/acpi.c

## Purpose
`acpi.c` contains Xen Dom0 ACPI integration helpers for sleep notification and interrupt routing information.

## Important APIs, types, and functions
Key functions are `xen_acpi_notify_hypervisor_sleep`, `xen_acpi_notify_hypervisor_extended_sleep`, internal `xen_acpi_notify_hypervisor_state`, `xen_acpi_get_gsi_info`, `xen_acpi_register_get_gsi_func`, and `xen_acpi_get_gsi_from_sbdf`. It defines a local ACPI PRT entry shape matching the fields used from ACPI PCI IRQ lookup.

## Control flow
Sleep helpers package PM control values into `XENPF_enter_acpi_sleep` platform ops, validating 16-bit or 8-bit fields depending on extended mode, then notify Xen. GSI lookup reads a PCI device interrupt pin, uses ACPI PCI IRQ lookup, allocates link interrupts when needed, defaults polarity based on ACPI IRQ model, and returns GSI/trigger/polarity. SBDF lookup is an externally registered callback protected by an rwlock.

## State and persistence
Only the registered SBDF-to-GSI callback pointer is persistent runtime state. ACPI and Xen platform state are external.

## Dependencies and integration points
It depends on PCI, ACPI PCI IRQ routing, Xen platform hypercalls, and exported Xen ACPI helper symbols used by other Xen PCI/ACPI code.

## Risks and test signals
Risks include truncating sleep control values, ignoring hypercall return from sleep notification, ACPI PRT assumptions, callback unregister absence, and rwlock use around arbitrary callback execution. Test signals include S-state transitions, extended sleep values, PCI devices with direct and link-based PRT entries, GIC and non-GIC polarity defaults, invalid inputs, and SBDF callback registration.
