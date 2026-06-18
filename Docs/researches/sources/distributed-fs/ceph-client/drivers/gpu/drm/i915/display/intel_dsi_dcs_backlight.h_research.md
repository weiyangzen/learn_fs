<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.h

## Purpose
This header exposes the DSI DCS backlight initialization hook.

## Important APIs, Types, and Functions
It forward declares `struct intel_connector` and declares `intel_dsi_dcs_init_backlight_funcs()`.

## Control Flow
There is no local flow. Panel/backlight initialization calls this helper to install DCS callbacks when VBT selects the DSI DCS backlight type.

## State and Persistence Behavior
No state is stored here. The implementation persists its effect by setting `panel->backlight.funcs`.

## Dependencies and Integration Points
It is included by panel/DSI setup code that needs to try DCS backlight support without depending on implementation details.

## Risks
The function can return `-ENODEV` or `-EINVAL`; callers must continue to other backlight methods or fail appropriately.

## Test Signals
Compile coverage and panel initialization paths that either install DCS callbacks or cleanly fall back to other backlight implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.h -->
