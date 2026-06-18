# sources/distributed-fs/ceph-client/include/drm/drm_vblank_helper.h

## Purpose
`drm_vblank_helper.h` declares helper callbacks for atomic vblank handling and hrtimer-backed vblank emulation.

## Important APIs, types, and functions
Atomic helper APIs are `drm_crtc_vblank_atomic_flush`, `drm_crtc_vblank_atomic_enable`, and `drm_crtc_vblank_atomic_disable`. `DRM_CRTC_HELPER_VBLANK_FUNCS` initializes helper function table entries for atomic flush/enable/disable. Timer APIs are `drm_crtc_vblank_helper_enable_vblank_timer`, `drm_crtc_vblank_helper_disable_vblank_timer`, and `drm_crtc_vblank_helper_get_vblank_timestamp_from_timer`; `DRM_CRTC_VBLANK_TIMER_FUNCS` maps them to CRTC funcs.

## Control flow
Atomic drivers can use the macro so atomic enable/disable/flush paths maintain vblank state. Drivers without hardware vblank IRQs or counters can use timer funcs to synthesize vblank timing and timestamps.

## State and persistence
The header stores no state. It manipulates `drm_vblank_crtc` state declared in `drm_vblank.h` and CRTC atomic state at runtime.

## Dependencies and integration points
It depends on hrtimer types, DRM atomic state, and CRTC objects. It integrates with `struct drm_crtc_helper_funcs`, `struct drm_crtc_funcs`, and vblank core state.

## Risks and test signals
Risks include enabling timer vblank on hardware that also generates IRQs, atomic disable ordering that drops pending events, timestamp inaccuracy from timer-only mode, and macro misuse in drivers with custom vblank sequencing. Test signals include atomic enable/disable, page flip event delivery through flush, timer-only vblank intervals, suspend/resume, and CRTC helper function table audits.
