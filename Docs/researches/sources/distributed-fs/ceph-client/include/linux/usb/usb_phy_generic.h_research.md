# sources/distributed-fs/ceph-client/include/linux/usb/usb_phy_generic.h

## Purpose
This header declares helpers for registering the generic no-op USB PHY platform device used by controllers that need a simple PHY object.

## Important APIs, types, and functions
The exported APIs are `usb_phy_generic_register()` and `usb_phy_generic_unregister()`. When `CONFIG_NOP_USB_XCEIV` is disabled, registration returns `NULL` and unregister is a no-op.

## Control flow, state, and persistence
Callers register a generic PHY during platform setup and unregister it during teardown. Runtime state belongs to the created platform device and USB PHY framework; no persistent data is represented.

## Dependencies and integration points
It depends on USB OTG PHY declarations and platform-device infrastructure. It integrates with controller drivers expecting an OTG/PHY provider even when hardware has no programmable transceiver.

## Risks and test signals
Risks are mishandling a `NULL` return from disabled stubs and unregistering an invalid pointer. Tests should cover enabled probe/remove and disabled-config behavior.
