# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank_helper.c

## Purpose
Provides small helper implementations for drivers that need generic vblank behavior, especially timer-backed vblank support for hardware without real vblank interrupts.

## Important APIs, Types, and Functions
Exports `drm_crtc_vblank_atomic_flush`, `drm_crtc_vblank_atomic_enable`, `drm_crtc_vblank_atomic_disable`, `drm_crtc_vblank_helper_enable_vblank_timer`, `drm_crtc_vblank_helper_disable_vblank_timer`, and `drm_crtc_vblank_helper_get_vblank_timestamp_from_timer`. These functions are intended for `drm_crtc_helper_funcs` and `drm_crtc_funcs` wiring, often through helper macros.

## Control Flow
`atomic_flush` consumes `crtc_state->event` under `event_lock`, tries to acquire a vblank ref, arms the event for the next vblank on success, or sends immediately on failure. Enable/disable call `drm_crtc_vblank_on/off`. Timer helpers simply start/cancel the vblank timer and source timestamps from the timer timeout helper.

## State and Persistence
The file owns no persistent state. It mutates CRTC state event pointers and delegates all vblank state to `drm_vblank.c`.

## Dependencies and Integration Points
Depends on DRM atomic state, event locking, `drm_crtc_arm_vblank_event`, `drm_crtc_send_vblank_event`, and vblank timer APIs. Integrates with drivers that choose generic helper funcs instead of bespoke vblank IRQ handling.

## Risks
Drivers using `atomic_flush` must ensure event arming matches hardware commit timing; otherwise events may be one frame late or early. Timer-backed timestamps are synthetic and depend on correct mode-derived frame duration.

## Test Signals
Atomic commit tests should verify event delivery with and without available vblank refs. Timer-backed drivers need checks for stable event cadence, correct disable behavior, and absence of leaked `crtc_state->event` pointers.
