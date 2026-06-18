# sources/distributed-fs/ceph-client/drivers/usb/typec/pd.h

## Purpose

`pd.h` is the private header for the USB Power Delivery class implementation. It defines the internal device wrappers that back `pd.c` and declares class lifecycle and lookup helpers.

## Important APIs, Types, and Functions

`struct usb_power_delivery` contains the class `struct device`, allocated ID, PD revision, and optional version. `struct usb_power_delivery_capabilities` contains the capabilities device, parent PD pointer, and source/sink role. Container macros convert devices to those wrappers. Prototypes expose `usb_power_delivery_find()`, `usb_power_delivery_init()`, and `usb_power_delivery_exit()`.

## Control Flow

The header has no executable control flow. It defines the device layout and local helper contract consumed by `pd.c` and the Type-C class initialization path.

## State and Persistence Behavior

The structures describe runtime-only device-model state. IDs, revision/version, and role are retained while the corresponding devices exist and are freed by device release callbacks.

## Dependencies and Integration Points

It includes `linux/device.h` and `linux/usb/typec.h`, tying the private PD class state to the Linux device core and Type-C role enums. It is intentionally narrower than the public `<linux/usb/pd.h>` API.

## Risks and Test Signals

Risks are local ABI coupling with `pd.c`: changing structure fields or macros affects every release path and sysfs callback. Test signals are compile coverage of PD class init, registration, sysfs attribute access, and lookup by class device name.
