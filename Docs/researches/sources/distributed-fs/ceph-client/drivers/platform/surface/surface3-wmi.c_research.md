# sources/distributed-fs/ceph-client/drivers/platform/surface/surface3-wmi.c

## Purpose
Implements a Surface 3-specific WMI/platform driver that replaces the default ACPI lid handling with a WMI-backed lid switch tied to touchscreen hotplug behavior. It reports lid state via the input subsystem.

## Important APIs, Types, And Functions
`struct surface3_wmi` stores touchscreen and PNP0C0D ACPI devices, an ACPI hotplug context, and an input device. `s3_wmi_query_block()` serializes WMI queries with a global mutex and expects integer results. `s3_wmi_send_lid_state()` reports `SW_LID`. Discovery helpers scan platform devices for the lid ACPI node and SPI touchscreen child `NTRG`. Probe/remove are `s3_wmi_probe()` and `s3_wmi_remove()`, registered through a manually allocated platform device in module init.

## Control Flow
Module init creates a platform device and probes only on DMI-matched Microsoft Surface 3 systems. Probe scans platform devices, finds the SPI touchscreen and lid ACPI devices, trims the original ACPI lid device, registers an input lid switch, installs a hotplug notify callback on the touchscreen ACPI device, and sends the initial lid state. Hotplug notifications and resume both query WMI GUID `F7CC25EC-D20B-404C-8903-0ED4359C18AE` instance 0 and report the result.

## State And Persistence Behavior
Driver state is global singleton state (`s3_wmi` and `s3_wmi_pdev`) with one mutex around WMI query operations. It persists no state across unload or reboot. Remove clears the hotplug context and rescans the original ACPI lid device handle to restore default lid handling.

## Dependencies And Integration Points
Depends on ACPI, WMI, DMI, input, platform bus enumeration, SPI ACPI naming, and ACPI hotplug internals. Integrates with userspace through a normal input `SW_LID` device named `Lid Switch`.

## Risks
The driver assumes one Surface 3 platform and uses global mutable state. `s3_wmi_probe()` calls `acpi_bus_trim(s3_wmi.pnp0c0d_adev)` without explicitly validating that the lid ACPI device was found, so discovery failures could lead to a null dereference. The WMI query parser accepts only integer objects and logs buffer length conditionally. ACPI hotplug context manipulation is fragile across ACPI core changes.

## Test Signals
Test on Surface 3 DMI only, verify no binding elsewhere, check lid input events across attach/detach/resume, simulate missing SPI touchscreen or lid ACPI node, unload/reload and confirm PNP0C0D restoration, and validate WMI error handling.
