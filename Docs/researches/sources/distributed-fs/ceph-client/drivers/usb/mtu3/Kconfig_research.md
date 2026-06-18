# sources/distributed-fs/ceph-client/drivers/usb/mtu3/Kconfig

## Purpose

`drivers/usb/mtu3/Kconfig` defines configuration symbols for the MediaTek USB3 Dual Role controller driver and its host, gadget, dual-role, and debug build variants.

## Important APIs, Types, and Functions

The main symbol is `USB_MTU3`, a tristate depending on USB or USB_GADGET, MediaTek architecture or compile testing, and extcon availability. The mode choice defines `USB_MTU3_HOST`, `USB_MTU3_GADGET`, and `USB_MTU3_DUAL_ROLE`; dual-role selects `USB_ROLE_SWITCH`. `USB_MTU3_DEBUG` enables debug messages.

## Control Flow

Configuration chooses exactly one operating mode when `USB_MTU3` is enabled. Defaults prefer dual-role when both host and gadget stacks are available, host when only USB host is available, and gadget when only gadget is available.

## State and Persistence Behavior

The selected symbols persist in the kernel build config and control which source files are compiled. Runtime role and hardware state live in the MTU3 driver, not this Kconfig file.

## Dependencies and Integration Points

The symbols drive the MTU3 Makefile and the stub/full declarations in `mtu3_dr.h`. They integrate with xHCI MTK host support, USB gadget core, extcon, and USB role switch infrastructure.

## Risks and Test Signals

Risks include invalid dependency combinations, built-in versus module constraints for host/gadget dependencies, and accidentally excluding needed source objects for a chosen role. Test signals include all three mode builds, compile-test builds on non-MediaTek architectures, and debug builds adding `-DDEBUG`.
