# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.h

## Purpose

`rcar_lvds.h` declares the public helper interface for the R-Car LVDS bridge, mainly for DU code that needs to control LVDS-provided pixel clocks or query link/connection state.

## Important APIs, Types, and Functions

The exported functions are `rcar_lvds_pclk_enable()`, `rcar_lvds_pclk_disable()`, `rcar_lvds_dual_link()`, and `rcar_lvds_is_connected()`. Build-time stubs return `-ENOSYS` or `false` when `CONFIG_DRM_RCAR_LVDS` is disabled.

## Control Flow

DU clock/output code calls the pclk helpers around modeset on extended-PLL platforms. Encoder-routing code can query whether the bridge is dual-link or connected.

## State and Persistence Behavior

The header has no state. The bridge implementation owns clock and connection state.

## Dependencies and Integration Points

It only forward-declares `struct drm_bridge`. It is included by R-Car DU code without forcing the LVDS implementation to be built in.

## Risks and Edge Cases

Callers must handle `-ENOSYS` on disabled builds and must not assume a disconnected LVDS bridge can provide a valid output, except for D3/E3 dot-clock-only cases handled by the implementation.

## Test Signals

Build matrix coverage with LVDS enabled/disabled and modesets that use LVDS as both an output bridge and a clock provider.
