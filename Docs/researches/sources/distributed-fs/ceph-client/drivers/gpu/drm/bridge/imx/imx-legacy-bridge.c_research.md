# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-legacy-bridge.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-legacy-bridge.c

## Purpose

This file provides a small bridge for legacy i.MX device-tree display bindings that describe fixed `display-timings` instead of a proper panel driver.

## Important APIs, Types, And Functions

`struct imx_legacy_bridge` embeds a DRM bridge, fixed display mode, and bus flags. The exported factory `devm_imx_drm_legacy_bridge()` allocates and registers the bridge. `imx_legacy_bridge_get_modes()` exposes the fixed mode and bus flags.

## Control Flow

The factory reads a DRM display mode and bus flags from OF using `of_get_drm_display_mode()`, marks the mode as driver-provided, sets bridge OF node/type/ops, and registers the bridge with device-managed cleanup. Attach only allows `DRM_BRIDGE_ATTACH_NO_CONNECTOR`. Get-modes returns the fixed mode and copies bus flags to connector display info.

## State And Persistence Behavior

The fixed mode and bus flags are cached in the bridge object for the device lifetime. No hardware is programmed and no persistent storage exists.

## Dependencies And Integration Points

It depends on DRM bridge modes ops, OF display timing helpers, and exported GPL linkage through `<drm/bridge/imx.h>`. It is intended for older i.MX IPUv3 users.

## Risks And Test Signals

Risks include preserving obsolete bindings and rejecting connector-creating attach users. Test signals are successful fixed-mode enumeration, correct bus flags, and legacy DT displays working without a panel driver.
