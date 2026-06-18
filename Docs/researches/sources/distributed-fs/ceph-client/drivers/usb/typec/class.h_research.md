<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/class.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/class.h

## Purpose

`class.h` is the private state header for the USB Type-C class implementation. It defines the concrete device wrappers behind the public Type-C handles.

## Important APIs, Types, and Functions

It declares `struct typec_plug`, `struct typec_cable`, `struct typec_partner`, and `struct typec_port`, plus `to_typec_*()` container macros, device type externs, class externs, and ACPI port-link helpers. Fields include device objects, IDAs, PD identity/revision/SVDM state, USB mode/capability state, role state, mutexes, mux/switch/retimer handles, capabilities, operations, and linked USB2/USB3 devices.

## Control Flow

The header has no executable flow. It constrains registration, teardown, sysfs, and altmode-bus flow in `class.c`, `bus.c`, and mode-selection code by defining where state is cached and how device types are recognized.

## State and Persistence Behavior

All structures are runtime-only and released through device-type release callbacks. `struct typec_port` owns its duplicated capability block and mux/switch/retimer references; partner/cable/plug structures own mode IDAs and identity pointers supplied by controller drivers.

## Dependencies and Integration Points

It depends on Linux device core and public USB Type-C definitions. It is the private integration point among Type-C class, altmode bus, mux/retimer framework, ACPI helpers, and USB core connector links.

## Risks and Test Signals

Risks are broad because field layout changes affect many local files. Test signals are compile coverage for all Type-C class users, hotplug registration/unregistration, USB device attach/deattach callbacks, and ACPI/non-ACPI builds where `typec_link_ports()` becomes an inline no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/class.h -->
