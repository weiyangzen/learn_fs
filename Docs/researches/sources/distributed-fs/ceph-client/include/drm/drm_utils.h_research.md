# sources/distributed-fs/ceph-client/include/drm/drm_utils.h

## Purpose
`drm_utils.h` declares miscellaneous DRM utility functions intended for use both inside DRM and by adjacent code such as fbdev drivers.

## Important APIs, types, and functions
APIs are `drm_get_panel_orientation_quirk`, `drm_get_panel_backlight_quirk`, and `drm_timeout_abs_to_jiffies`. `struct drm_panel_backlight_quirk` carries `min_brightness` and `brightness_mask`. `drm_get_panel_backlight_quirk` consumes a `struct drm_edid`.

## Control flow
Display code can query panel orientation quirks by physical width/height, query EDID-based panel backlight quirks, or convert absolute nanosecond timeouts to signed jiffies for wait APIs.

## State and persistence
The header owns no state. Quirk state is implemented elsewhere, likely as static tables, and timeout conversion is derived from current time/jiffies.

## Dependencies and integration points
It depends on basic Linux types and forward-declared DRM EDID data. It integrates with panel orientation handling, backlight drivers/helpers, EDID parsing, and timeout-based synchronization paths.

## Risks and test signals
Risks include overmatching physical-size quirks, stale EDID quirk tables, brightness masks that hide valid levels, timeout overflow or negative conversion errors, and external users depending on DRM internals. Test signals include known quirky panels, EDID-based backlight quirk lookup, timeout conversion for past/present/future deadlines, and fbdev/DRM cross-subsystem builds.
