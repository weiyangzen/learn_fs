<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.h

## Purpose

`phy-generic.h` declares the private state and helper APIs for the generic NOP USB PHY.

## Important APIs, Types, and Functions

`struct usb_phy_generic` embeds `struct usb_phy` and stores device, clock, VCC regulator, reset GPIO, VBUS-detect GPIO, VBUS regulator, VBUS regulator enabled flag, current draw, and VBUS state. Declared helper APIs are `usb_gen_phy_init()`, `usb_gen_phy_shutdown()`, and `usb_phy_gen_create_phy()`.

## Control Flow

The header has no execution path. `phy-generic.c`, `phy-am335x.c`, and `phy-keystone.c` populate this structure and install optional platform-specific init/shutdown callbacks.

## State and Persistence Behavior

The structure is per-device runtime state. Its fields mirror hardware controls that persist only while the PHY device is active.

## Dependencies and Integration Points

It depends on `linux/usb/usb_phy_generic.h`, GPIO descriptors, and regulators. It is a local helper boundary for legacy USB PHY implementations.

## Risks and Test Signals

Risks are lifecycle misuse by derived drivers, especially overriding callbacks without preserving generic resources. Compile coverage and probe/remove tests for generic, AM335x, and Keystone PHYs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.h -->
