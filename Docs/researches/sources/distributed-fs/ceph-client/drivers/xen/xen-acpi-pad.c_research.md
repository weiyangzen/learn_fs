# sources/distributed-fs/ceph-client/drivers/xen/xen-acpi-pad.c

## Purpose
`xen-acpi-pad.c` handles ACPI processor aggregator notifications in Xen dom0 and translates requested idle CPU counts into Xen core-parking platform operations.

## Important APIs, types, and functions
Important functions are `xen_acpi_pad_idle_cpus`, `xen_acpi_pad_idle_cpus_num`, `acpi_pad_pur`, `acpi_pad_handle_notify`, `acpi_pad_notify`, `acpi_pad_probe`, and `acpi_pad_remove`. The driver matches ACPI HID `ACPI000C` and registers a platform driver named `acpi_processor_aggregator`.

## Control flow
Initialization runs only in the Xen initial domain and only on Xen 4.2 or newer. Probe installs an ACPI notify handler. On notification `0x80`, the driver evaluates `_PUR` to get the requested number of idle CPUs, calls `XENPF_core_parking` to set the count, queries the result, and reports status with `_OST`. Remove unparks CPUs and removes the notify handler.

## State and persistence
State is minimal: `xen_cpu_lock` serializes platform operations and ACPI notification handling. Xen core-parking state changes live in the hypervisor until changed again; the driver itself stores no durable state.

## Dependencies and integration points
It depends on ACPI platform devices, `_PUR`/`_OST`, Xen platform hypercalls, Xen version detection, and dom0-only initialization. It integrates firmware power-management events with Xen CPU core parking.

## Risks and test signals
Risks include malformed `_PUR` packages, unsupported Xen versions, concurrent notifications, failure to unpark on remove, and mismatched ACPI status reporting. Test signals include ACPI000C probe, notification injection, `_PUR` failure cases, Xen platform-op errors, remove/unpark behavior, and domU/non-Xen refusal.
