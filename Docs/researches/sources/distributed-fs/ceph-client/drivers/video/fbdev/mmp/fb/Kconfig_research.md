# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Kconfig

## Purpose
Defines the fbdev frontend option for the Marvell MMP display subsystem.

## Important APIs, Types, and Functions
- `config MMP_FB` is a tristate option depending on `FB`.
- It selects `FB_IOMEM_HELPERS` and defaults to `y`.

## Control Flow
Kconfig exposes the MMP framebuffer driver when the enclosing MMP display menu is active and fbdev core is available.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Builds the framebuffer driver that consumes MMP paths and overlays from the core/hardware layer.

## Risks
Defaulting to `y` can build the fb frontend even when no platform data creates a usable path; probe still fails gracefully if platform data is missing.

## Test Signals
Kconfig/build validation with `FB` enabled/disabled and `MMP_DISP` enabled.
