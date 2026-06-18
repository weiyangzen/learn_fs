<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Kconfig

## Purpose
Defines `CONFIG_USB_RENESAS_USBHS`, the tristate Renesas USBHS controller driver option.

## Important APIs, Types, And Functions
No runtime APIs. The symbol depends on `USB_GADGET`, `ARCH_RENESAS || SUPERH || COMPILE_TEST`, and `EXTCON || !EXTCON`.

## Control Flow
Build selection produces a built-in driver or a `renesas_usbhs` module. Help text documents a full/high-speed USB 2.0 controller with endpoint zero and multiple configurable endpoints.

## State And Persistence
State is build configuration only.

## Dependencies And Integration Points
Controls Makefile inclusion and interacts with frontend symbols for HCD/UDC. The extcon dependency prevents built-in USBHS from depending on modular extcon.

## Risks
The top-level symbol requires gadget support even for host-capable builds. Build matrix mistakes can hide unresolved frontend dependencies.

## Test Signals
Build `y`, `m`, disabled, COMPILE_TEST, and extcon built-in/module combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Kconfig -->
