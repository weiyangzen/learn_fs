# sources/distributed-fs/ceph-client/drivers/usb/core/phy.h

## Purpose
Declares the USB root-hub generic PHY wrapper interface implemented by `phy.c` for use by USB host-controller/core code.

## Important APIs, Types, And Functions
Forward-declares `struct device` and opaque `struct usb_phy_roothub`. Prototypes cover allocation for all/root USB2 PHYs and separate USB3 PHYs, lifecycle (`init`, `exit`), mode and calibration, port connect/disconnect notifications, power on/off, and controller-aware suspend/resume. The header uses `enum phy_mode` in a prototype but relies on included context for the enum declaration.

## Control Flow
This header has no runtime control flow. It establishes the callable contract: users allocate a roothub wrapper, initialize it, set mode/calibrate as needed, power it on, notify connect/disconnect events, and pair suspend/resume and exit/power-off operations according to HCD lifecycle.

## State And Persistence
The header exposes only an opaque pointer, intentionally hiding list layout and per-PHY state. Persistence and ownership are controlled by the implementation's devm allocation and generic PHY providers.

## Dependencies And Integration Points
Integrated by host-controller code and `phy.c`. It forms the compile-time boundary between USB core users and the generic PHY subsystem fan-out implementation.

## Risks And Test Signals
Risks are ABI/API drift with `phy.c`, missing enum visibility if included without generic PHY declarations, and misuse of lifecycle ordering by callers. Test signals are compile coverage across configurations with and without `CONFIG_GENERIC_PHY`, and HCD suspend/resume paths that exercise every declared method.
