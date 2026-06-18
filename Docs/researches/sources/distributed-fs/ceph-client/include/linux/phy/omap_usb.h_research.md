# sources/distributed-fs/ceph-client/include/linux/phy/omap_usb.h

## Purpose
OMAP USB2 PHY companion header. It declares the comparator binding hook used by OMAP USB2 PHY support.

## Important APIs, Types, and Functions
Defines `phy_to_omapusb(x)` for converting a generic USB PHY member to its containing `struct omap_usb`. Declares `omap_usb2_set_comparator()` when OMAP USB2 support is built, with an `-ENODEV` stub otherwise.

## Control Flow
Consumers install a `struct phy_companion` comparator through `omap_usb2_set_comparator()`. Disabled builds return immediately with `-ENODEV`.

## State and Persistence
The header itself has no state. Comparator registration persists in the OMAP USB2 implementation.

## Dependencies and Integration Points
Depends on `linux/usb/phy_companion.h` and integrates OMAP USB2 PHY code with USB comparator/companion logic.

## Risks
The container macro assumes the embedded member is named `phy`. Missing OMAP USB2 config produces an explicit error stub that callers must handle.

## Test Signals
Build tests for OMAP USB2 modular/built-in/disabled configs and USB2 comparator registration tests on supported OMAP platforms.
