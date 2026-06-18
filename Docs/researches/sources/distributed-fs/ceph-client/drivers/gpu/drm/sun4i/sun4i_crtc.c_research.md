# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_crtc.c

## Purpose
`sun4i_crtc.c` implements the DRM CRTC glue tying a `sunxi_engine` to a TCON. It delegates atomic validation and mode programming to engine/TCON ops, manages vblank events, enables/disables TCON output, and creates planes from the engine.

## Important APIs, Types, and Functions
- `sun4i_crtc_init`: allocates `struct sun4i_crtc`, creates engine layers, initializes DRM CRTC with primary/cursor planes, adds helper funcs, sets `crtc.port`, and assigns overlay `possible_crtcs`.
- Atomic helpers: `sun4i_crtc_atomic_check`, begin, flush, enable, disable, and `mode_set_nofb`.
- Vblank funcs: `sun4i_crtc_enable_vblank` and disable call TCON vblank control.
- `sun4i_crtc_get_encoder`: finds the active encoder attached to the CRTC.

## Control Flow, State, and Persistence
Atomic check forwards to `engine->ops->atomic_check`. Begin captures pending events under the DRM event lock and calls engine atomic-begin. Flush commits engine registers and arms or sends vblank events. Enable/disable switch TCON status and vblank on/off. Mode set programs TCON mode and engine display size. `struct sun4i_crtc` persists as the DRM CRTC wrapper and stores engine, TCON, and a pending event pointer.

## Dependencies and Integration Points
The file depends on DRM CRTC atomic helpers, TCON APIs, `sunxi_engine`, backend/mixer layer initialization, and OF graph port lookup. It is created by TCON binding and participates in the master sun4i DRM device.

## Risks and Test Signals
Risks include assuming one active encoder per TCON, event handling split between begin and flush, NULL return in one error path of `sun4i_crtc_init`, and lifetime of `crtc.port`. Tests should cover atomic commits with events, enable/disable/shutdown, multiple encoder graph configurations, vblank on/off, and engine atomic-check failures.
