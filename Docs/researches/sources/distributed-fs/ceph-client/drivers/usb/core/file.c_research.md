# sources/distributed-fs/ceph-client/drivers/usb/core/file.c

## Purpose

`file.c` implements the USB major-number dispatch layer and `usbmisc` class-device support for USB interface drivers that expose character devices. It maps minor numbers to driver-provided `file_operations`, swaps the opened file to the real operations table, and creates/destroys the corresponding class device.

## Important APIs, Types, and Functions

- `usb_minors[MAX_USB_MINORS]` maps USB minor numbers to registered `struct file_operations`.
- `minor_rwsem` protects the minor table across open/register/deregister.
- `usb_open()` looks up the minor, gets a module-safe fops reference with `fops_get()`, calls `replace_fops()`, and then invokes the real `open()` if present.
- `usb_fops` is the registered major-level dispatch fops for `USB_MAJOR`.
- `usb_devnode()` delegates devnode naming/mode to an optional `usb_class_driver::devnode`.
- `usbmisc_class` is the class used for created USB miscellaneous devices.
- `usb_major_init()` and `usb_major_cleanup()` register/unregister the USB major.
- `usb_register_dev()` allocates a minor, stores driver fops, sets `intf->minor`, and calls `device_create()`.
- `usb_deregister_dev()` destroys the class device, clears the minor-table entry, and resets interface minor state.

## Control Flow

USB core initialization calls `usb_major_init()` to register `USB_MAJOR` with `usb_fops`. A USB interface driver that wants a character device calls `usb_register_dev()`. The function validates `class_driver->fops`, rejects interfaces already assigned a minor, chooses either the requested `minor_base` or zero under `CONFIG_USB_DYNAMIC_MINORS`, scans for a free table entry while holding `minor_rwsem` for write, stores fops, assigns `intf->minor`, formats a class-device name, and creates the `usbmisc` class device. If `device_create()` fails it rolls back the table entry and minor assignment.

When user space opens the char device, VFS enters `usb_open()` through the common USB major. The function takes `minor_rwsem` for read, obtains the real fops from the minor table, atomically replaces the file fops with `replace_fops()`, and invokes the real `open()`. Deregistration destroys the class device first, clears the fops table under the write semaphore, and resets `intf->usb_dev`/`intf->minor`.

## State and Persistence Behavior

The minor table and `intf->minor`/`intf->usb_dev` are live kernel state. Device nodes may be created by devtmpfs/udev from the `usbmisc` class device, but this file itself stores no durable state. `fops_get()` provides module lifetime protection for an open; table updates are serialized by `minor_rwsem`.

## Dependencies and Integration Points

This layer integrates with VFS character devices, Linux device classes, devtmpfs/udev, USB interface driver probe/disconnect paths, and the `struct usb_class_driver` contract. Drivers must explicitly call `usb_register_dev()` after `usb_register_driver()` and must call `usb_deregister_dev()` during disconnect or teardown.

## Risks and Edge Cases

- Minor allocation can fail with `-EXFULL` if all 256 slots are used or static minor ranges collide.
- `usb_open()` returns `-ENODEV` when a device is gone or the fops table entry has already been cleared.
- Deregistration must be ordered with driver disconnect so new opens stop seeing the fops while existing opens remain protected by fops references.
- `snprintf(name, sizeof(name), class_driver->name, minor - minor_base)` assumes driver-provided names fit the 20-byte buffer and are intended as printf-style patterns.
- Drivers that forget to deregister leak minor slots and class devices.

## Test Signals

Useful tests include registering multiple USB class devices, dynamic-minor allocation, static minor collision handling, open after disconnect, module unload with open file references, `device_create()` failure injection, custom `devnode()` behavior, and verification that `/dev` nodes and sysfs `usbmisc` entries appear/disappear with interface bind/unbind.
