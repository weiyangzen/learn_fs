<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/core/usb.h

## Purpose
`usb.h` is the private header for `drivers/usb/core`. It declares cross-file USB core internals that are not part of the public USB driver API, including sysfs helpers, endpoint enable/disable helpers, authorization, descriptor/configuration routines, hub/devio/lpm/PM integration, bus/class/device type symbols, usbfs symbols, notification hooks, firmware location helpers, and ACPI glue.

## Important APIs, types, and functions
The header declares device and interface sysfs helpers, endpoint device creation/removal, `usb_enable_endpoint`, `usb_enable_interface`, endpoint/interface/device disable paths, interface cache release, authorization/deauthorization, quirk detection/release, ignored endpoint checks, descriptor/configuration APIs, generic driver probe/disconnect/suspend/resume hooks, hub workqueue and ownership helpers, hub/major/devio lifecycle functions, LPM helpers, PM suspend/resume/autosuspend functions, and ACPI registration/lookup functions. It defines `usb_get_max_power`, type predicates such as `is_usb_device`, and `usb_port_location_t`.

## Control flow
This file mainly shapes compile-time linkage. When `CONFIG_PM` is enabled, consumers call real suspend/resume/autosuspend/LPM functions; otherwise inline stubs return success or no-op. When `CONFIG_ACPI` is disabled, ACPI registration/unregistration become no-ops. Type predicates compare `struct device.type` to the USB core device/interface/endpoint/port type singletons, allowing bus walkers to filter mixed USB bus devices.

## State and persistence behavior
The header itself stores no state, but it exposes state-owning globals such as `usb_bus_type`, `usbmisc_class`, `usb_port_peer_mutex`, USB device types, `usb_generic_driver`, `usbfs_driver`, file operations, attribute group arrays, and `usbcore_name`. Its inline stubs intentionally preserve caller control flow when PM or ACPI is absent, which can hide feature differences behind successful no-ops.

## Dependencies and integration points
It depends on Linux PM and ACPI headers and public USB structures. It is included across USB core implementation files to share internal contracts among hub, config, driver, sysfs, devio, quirks, message, and ACPI code. External USB function or class drivers should generally use public headers instead.

## Risks
Because this is an internal contract header, prototype drift can create broad build failures. Stubbed PM/LPM/ACPI behavior can mask missing feature coverage if tests only check return values. The type predicates depend on device type pointer identity, so all USB device objects must be initialized with the correct singleton. `usb_get_max_power` encodes unit selection by speed and depends on current USB descriptor semantics.

## Test signals
Build matrices should cover PM on/off and ACPI on/off, host-only and gadget-related USB configurations, and sparse or CFI-style checks for prototype consistency. Runtime signals include correct sysfs and usbfs behavior, successful suspend/resume paths when PM is enabled, harmless no-op behavior when PM is disabled, and correct filtering in bus walkers using `is_usb_device` and related helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/usb.h -->
