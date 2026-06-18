# sources/distributed-fs/ceph-client/drivers/usb/usbip/Makefile

## Purpose

`usbip/Makefile` maps USB/IP Kconfig symbols to kernel modules and object lists. It defines the build composition for the core, virtual host controller, host export driver, and virtual USB device controller.

## Important APIs, Types, and Functions

`ccflags-$(CONFIG_USBIP_DEBUG)` adds `-DDEBUG`. `usbip-core-y` contains `usbip_common.o` and `usbip_event.o`. `vhci-hcd-y` contains `vhci_sysfs.o`, `vhci_tx.o`, `vhci_rx.o`, and `vhci_hcd.o`. `usbip-host-y` contains `stub_dev.o`, `stub_main.o`, `stub_rx.o`, and `stub_tx.o`. `usbip-vudc-y` includes VUDC device, sysfs, tx, rx, transfer, and main objects.

## Control Flow

There is no runtime flow. The object order links shared logic with driver-specific entry points and controls which modules are emitted for selected configuration symbols.

## State and Persistence Behavior

Build artifacts reflect Kconfig state. No runtime state is defined here.

## Dependencies and Integration Points

It integrates Kbuild with the Kconfig symbols and keeps source files grouped by module boundary. It is the point where common USB/IP symbols become exported from `usbip-core` for `vhci-hcd`, `usbip-host`, and `usbip-vudc`.

## Risks and Test Signals

Risks include missing object files causing unresolved symbols, debug flag mismatch, or module composition drift when adding new files. Test signals are module build success for each symbol combination and `modinfo` showing expected module names.
