# `sources/distributed-fs/ceph-client/include/linux/usb/rzv2m_usb3drd.h`

## Purpose

`rzv2m_usb3drd.h` declares the reset helper for Renesas RZ/V2M USB3 dual-role-device glue. It lets USB3 DRD users reset the controller for host or device role.

## Important APIs, Types, and Constants

- `struct rzv2m_usb3drd` stores at least a `void __iomem *` register base for implementation users.
- `rzv2m_usb3drd_reset(struct device *dev, bool host)` resets the DRD block for host or non-host operation when `CONFIG_USB_RZV2M_USB3DRD` is enabled.
- Disabled builds provide an empty inline stub.

## Control Flow and Lifetimes

Role glue or controller code calls the reset helper during probe or role transition. The helper locates device-private DRD state and toggles reset/register state according to the `host` argument.

## State and Persistence Behavior

Hardware reset state is transient but affects controller role and register contents. The header itself stores no state beyond the implementation structure definition.

## Dependencies and Integration Points

It integrates Renesas RZ/V2M USB3 DRD glue with host/device controller drivers and device-model state. It uses `struct device`.

## Risks and Edge Cases

The disabled stub silently does nothing, so callers must ensure Kconfig matches hardware needs. Reset during active transfers can lose state. Host/device argument must match current role policy.

## Test Signals

Build with and without the DRD driver, call reset during host and device probe, test role switching, suspend/resume, and verify no active I/O is reset unexpectedly.
