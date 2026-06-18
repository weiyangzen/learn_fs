# sources/distributed-fs/ceph-client/drivers/usb/usbip/Kconfig

## Purpose

`usbip/Kconfig` defines the selectable kernel configuration surface for USB/IP core, virtual host controller, host-side exported-device driver, virtual USB device controller, and optional debug output.

## Important APIs, Types, and Functions

The entries are `USBIP_CORE`, `USBIP_VHCI_HCD`, `USBIP_VHCI_HC_PORTS`, `USBIP_VHCI_NR_HCS`, `USBIP_HOST`, `USBIP_VUDC`, and `USBIP_DEBUG`. `USBIP_CORE` depends on `NET` and selects `USB_COMMON` and `SGL_ALLOC`. VHCI and host depend on `USBIP_CORE && USB`; VUDC depends on `USBIP_CORE && USB_GADGET`.

## Control Flow

There is no runtime flow. Build-time selection determines which modules and helper objects are compiled and whether debug macros expand with `-DDEBUG`.

## State and Persistence Behavior

Kconfig values persist in the kernel configuration. `USBIP_VHCI_HC_PORTS` and `USBIP_VHCI_NR_HCS` shape compiled-in port/controller counts and therefore the sysfs attach surface.

## Dependencies and Integration Points

This file integrates USB/IP with kernel networking, USB host, USB gadget, scatterlist allocation, and debug build infrastructure. Userspace USB/IP tools depend on the selected kernel pieces being present.

## Risks and Test Signals

Risks include invalid assumptions about high port/controller counts, missing core selection for dependent drivers, and debug builds exposing verbose logs. Test signals are allmodconfig/build coverage, module names matching help text, valid Kconfig ranges, and sysfs port count matching configured VHCI values.
