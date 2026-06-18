# sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Makefile

## Purpose
This Makefile builds the RainShadow CEC adapter driver.

## Important APIs, Types, and Functions
It maps `CONFIG_USB_RAINSHADOW_CEC` to `rainshadow-cec.o`.

## Control Flow
Kbuild includes the driver object when configured.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The implementation binds to a serio protocol and registers a CEC adapter.

## Risks and Test Signals
Build tests should verify object inclusion for `CONFIG_USB_RAINSHADOW_CEC`.
