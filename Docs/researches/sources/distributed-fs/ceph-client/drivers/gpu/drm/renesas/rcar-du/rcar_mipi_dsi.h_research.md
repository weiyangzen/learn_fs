# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.h

## Purpose

`rcar_mipi_dsi.h` declares the DU-facing pixel-clock control hooks for the R-Car MIPI DSI bridge.

## Important APIs, Types, and Functions

It exposes `rcar_mipi_dsi_pclk_enable(struct drm_bridge *, struct drm_atomic_state *)` and `rcar_mipi_dsi_pclk_disable(struct drm_bridge *)`, with no-op stubs when `CONFIG_DRM_RCAR_MIPI_DSI` is disabled.

## Control Flow

DU modeset code calls enable before video output is started so the DSI block can configure clocks, PHY, and timings from the atomic state. Disable tears down the DSI block after video is stopped.

## State and Persistence Behavior

No state is owned by the header. The bridge implementation stores lane/format/mode information gathered during host attach.

## Dependencies and Integration Points

The header forward-declares DRM atomic state and bridge types and is included by R-Car DU output code.

## Risks and Edge Cases

No-op stubs can hide missing DSI support if callers do not gate output availability on bridge presence. The enable hook returns void, so startup failures are logged but not propagated to atomic commit.

## Test Signals

Build with DSI enabled/disabled and modeset a DSI panel while checking that failures in clock/PHY startup are visible in logs.
