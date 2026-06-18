# sources/distributed-fs/ceph-client/drivers/usb/mtu3/Makefile

## Purpose

`drivers/usb/mtu3/Makefile` assembles the MTU3 composite driver object according to Kconfig-selected role, tracing, debugfs, and debug-message options.

## Important APIs, Types, and Functions

`obj-$(CONFIG_USB_MTU3) += mtu3.o` creates the composite object. `mtu3-y` always includes `mtu3_plat.o`; optional additions include `mtu3_trace.o`, `mtu3_host.o`, gadget objects `mtu3_core.o`, `mtu3_gadget_ep0.o`, `mtu3_gadget.o`, `mtu3_qmu.o`, dual-role `mtu3_dr.o`, and debugfs `mtu3_debugfs.o`. `ccflags-$(CONFIG_USB_MTU3_DEBUG)` adds `-DDEBUG`.

## Control Flow

There is no runtime control flow. Kbuild conditionals select source objects based on `CONFIG_TRACING`, `CONFIG_USB_MTU3_HOST`, `CONFIG_USB_MTU3_GADGET`, `CONFIG_USB_MTU3_DUAL_ROLE`, and `CONFIG_DEBUG_FS`.

## State and Persistence Behavior

The file has no runtime state. It preserves the build-time contract that platform probe is always present, with host/gadget/DRD functionality linked only when configured.

## Dependencies and Integration Points

It integrates with Kbuild, trace header include paths, and the local role abstraction in `mtu3_dr.h`, where missing role objects are replaced by inline stubs.

## Risks and Test Signals

Risks include missing objects for dual-role combinations, stale trace include path behavior, or linking debugfs callers without debugfs implementation. Test signals include building host-only, gadget-only, dual-role, tracing-enabled, debugfs-disabled, and debug-message-enabled configurations.
