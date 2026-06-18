# sources/distributed-fs/ceph-client/drivers/usb/core/usb-acpi.c

## Purpose
Provides USB-to-ACPI glue for port power resources, port LPM capability quirks, USB4 tunneled-device PM links, firmware-derived port connect type/location, and ACPI companion discovery for USB devices and port devices.

## Important APIs, Types, And Functions
Exported APIs are `usb_acpi_power_manageable()`, `usb_acpi_port_lpm_incapable()`, and `usb_acpi_set_power_state()`. Bus registration APIs are `usb_acpi_register()` and `usb_acpi_unregister()`. Internal helpers include `usb_acpi_add_usb4_devlink()`, `usb_acpi_get_connect_type()`, `usb_acpi_get_companion_for_port()`, `usb_acpi_find_companion_for_port()`, `usb_acpi_find_companion_for_device()`, `usb_acpi_find_companion()`, and `usb_acpi_bus_match()`.

## Control Flow
Power-manageability and power-state setters find a hub port ACPI handle and call ACPI power-resource APIs. `usb_acpi_port_lpm_incapable()` parses the USB controller DSM UUID, checks function 5 availability on the port, evaluates it as an integer, and returns `1` when U1/U2 should be disabled. USB4 devlink setup applies only to tunneled SuperSpeed devices connected to a root hub; it reads the port fwnode `usb4-host-interface` reference and creates a runtime-PM device link from the USB child to the NHI device. Companion discovery maps root hubs via the HCD firmware device, maps ports by raw root port or parent port ACPI handle, derives connect type and location from `_UPC` and `_PLD`, and maps embedded devices to their port companion.

## State And Persistence
The file mutates `port_dev->connect_type`, `port_dev->location`, and `udev->usb4_link`. ACPI power state is external firmware/platform state. There is no local persistent storage.

## Dependencies And Integration Points
Depends on ACPI core, PCI/HCD raw port numbering, USB hub/port structures, firmware node references, device links, runtime PM flags, and USB link tunnel mode. It integrates with port creation, hub power control, LPM policy, and driver-core companion matching through `struct acpi_bus_type`.

## Risks And Test Signals
Risks include incorrect root-port numbering, missing or malformed `_UPC`/`_PLD`, DSM return type/value ambiguity, USB4 device-link lifetime, hard-wired device companion sharing, and unhandled per-interface ACPI function companions. Test signals include ACPI platforms with visible/connectable, hidden/connectable, and unused ports; ports with power resources; DSM LPM-disable cases; USB4 tunneled device suspend/resume ordering; root hub and nested hub companion lookup; and device removal with `udev->usb4_link`.
