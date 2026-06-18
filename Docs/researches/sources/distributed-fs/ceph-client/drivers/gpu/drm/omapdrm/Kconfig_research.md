# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/Kconfig

## Purpose
Defines OMAP DRM and OMAP Display Subsystem feature options.

## Important APIs, Types, And Functions
`config DRM_OMAP` selects DRM/KMS helpers, bridge connector, display helpers, HDMI, videomode helpers, and optional fbdev DMA helpers. Nested options enable debug, debugfs, IRQ stats, DPI, VENC, OMAP4/OMAP5 HDMI, CEC, SDI, DSI, scaling FCK/PCK ratio, and VENC reset sleep behavior.

## Control Flow
When `DRM_OMAP` is enabled, dependent feature booleans choose which DSS outputs and helpers are compiled by the Makefile.

## State, Persistence, And Dependencies
No runtime state exists here; it controls build-time feature inclusion.

## Integration Points
Integrated by the DRM Kconfig hierarchy and the OMAP DRM Makefile conditional object lists.

## Risks
Platform dependency excludes most non-OMAP builds except compile tests with supported page size. Enabling outputs without matching hardware/device tree still needs runtime probing to succeed.

## Test Signals
Signals are valid Kconfig combinations, build coverage for selected outputs, and expected debug/debugfs features when enabled.
