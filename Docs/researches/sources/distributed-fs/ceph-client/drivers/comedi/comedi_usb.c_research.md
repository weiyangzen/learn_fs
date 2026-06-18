# sources/distributed-fs/ceph-client/drivers/comedi/comedi_usb.c

## Purpose

This file is the USB bus helper layer for COMEDI drivers. It provides conversion helpers from a COMEDI device back to its USB interface or device, wrappers for auto-configuration and auto-unconfiguration, and paired registration of a COMEDI low-level driver with a `struct usb_driver`.

## Important APIs, types, and functions

The GPL-exported APIs are `comedi_to_usb_interface()`, `comedi_to_usb_dev()`, `comedi_usb_auto_config()`, `comedi_usb_auto_unconfig()`, `comedi_usb_driver_register()`, and `comedi_usb_driver_unregister()`. They bridge `struct comedi_device`, `struct usb_interface`, `struct usb_device`, `struct comedi_driver`, and `struct usb_driver`.

## Control Flow

USB driver probe calls `comedi_usb_auto_config(intf, driver, context)`, which passes `&intf->dev` and the context value into `comedi_auto_config()`. The COMEDI core allocates a device and invokes the low-level driver's `auto_attach`; that driver can recover the interface or USB device via the conversion helpers. USB disconnect calls `comedi_usb_auto_unconfig()`, delegating teardown to `comedi_auto_unconfig()`. Module registration first registers the COMEDI driver, then calls `usb_register()`, with COMEDI rollback on USB registration failure. Unregistration runs in the reverse order: USB first, COMEDI second.

## State and Persistence

This file has no private persistent state. State exists as kernel object references and registrations: `dev->hw_dev` links the COMEDI device to the USB interface's embedded device, the USB core tracks binding, and COMEDI tracks the allocated device and subdevices until unconfigured.

## Dependencies and Integration Points

It depends on `linux/comedi/comedi_usb.h`, the USB core, and COMEDI auto-configuration. It is the common integration point for USB COMEDI modules such as `dt9812`, `ni_usb6501`, `usbdux*`, and `vmk80xx`.

## Risks

The conversion helpers assume that `dev->hw_dev` is a USB interface device; using them from a non-USB auto-attach path would produce invalid container conversion. Driver-registration rollback is critical because a partially registered bus driver can otherwise leave COMEDI-visible board names without a matching USB probe path. Disconnect paths must tolerate devices already unconfigured through COMEDI user ioctls.

## Test Signals

Expected validation includes successful probe/disconnect cycles, `comedi_to_usb_dev()` returning the parent USB device in `auto_attach`, clean rollback when `usb_register()` fails, and no use-after-free or stale COMEDI device after cable disconnect while the device node is open.
