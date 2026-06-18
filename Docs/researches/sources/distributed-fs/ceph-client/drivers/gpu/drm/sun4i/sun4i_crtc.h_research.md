# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_crtc.h

## Purpose
`sun4i_crtc.h` declares the Allwinner CRTC wrapper type and CRTC initialization API used by TCON/display-engine code.

## Important APIs, Types, and Functions
- `struct sun4i_crtc`: embeds `struct drm_crtc`, stores a pending vblank event pointer, and links the CRTC to a `sunxi_engine` and `sun4i_tcon`.
- `drm_crtc_to_sun4i_crtc`: container conversion helper.
- `sun4i_crtc_init`: creates the CRTC and its planes for a DRM device, engine, and TCON.

## Control Flow, State, and Persistence
The header owns no behavior directly. The wrapper state persists for the lifetime of the DRM CRTC and is accessed by atomic helpers in `sun4i_crtc.c`.

## Dependencies and Integration Points
It depends on DRM CRTC types and forward declarations from users. It connects TCON code, engine code, and CRTC helper implementation.

## Risks and Test Signals
The pending `event` field must remain synchronized with DRM event locking rules. Any changes to wrapper layout or initialization signature require compile coverage across TCON and engine users. Tests should validate container conversion and CRTC creation for backend and mixer engines.
