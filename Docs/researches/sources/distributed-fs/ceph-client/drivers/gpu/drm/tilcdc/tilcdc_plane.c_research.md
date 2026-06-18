# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_plane.c

## Purpose

`tilcdc_plane.c` implements the single primary plane for the tilcdc driver. It enforces full-screen, unscaled scanout matching the CRTC mode and forwards framebuffer changes to the CRTC scanout/page-flip path.

## Important APIs, Types, and Functions

- `tilcdc_plane_funcs` wires universal plane operations to DRM atomic helper reset/update/disable/state helpers.
- `tilcdc_plane_atomic_check()` validates CRTC attachment, framebuffer presence, zero CRTC x/y, plane size equal to mode size, pitch equal to mode width times bytes per pixel, and marks the CRTC mode changed if the framebuffer pixel format changes.
- `tilcdc_plane_atomic_update()` calls `tilcdc_crtc_update_fb()` and clears the CRTC event on success.
- `tilcdc_plane_init()` allocates the primary plane with the pixel formats selected by probe and installs helper funcs.

## Control Flow

Probe creates this plane from `tilcdc_crtc_create()`. During atomic check the plane rejects overlays, scaling, panning, and mismatched pitch. During atomic update the framebuffer is passed to the CRTC, which either updates scanout immediately or defers to vblank. The driver has no overlay planes.

## State and Persistence Behavior

The plane is DRM-managed and stores no state beyond the embedded DRM plane. Framebuffer changes are reflected through CRTC state and hardware DMA address registers.

## Dependencies and Integration Points

The file depends on DRM atomic helpers, framebuffer format metadata, selected format arrays in `tilcdc_drv.c`, and `tilcdc_crtc_update_fb()`.

## Risks and Edge Cases

- Strict pitch equality rejects framebuffers with padding, which is intentional for simple LCDC scanout but can surprise generic userspace.
- Pixel format changes force a modeset because raster format bits live in CRTC mode programming.
- `WARN_ON(!crtc_state)` returns success rather than a hard error, but such a missing state should not occur for an attached plane.

## Test Signals

Tests should cover full-screen valid scanout, nonzero position rejection, scaled-size rejection, padded pitch rejection, pixel-format change forcing modeset, page flip event delivery through CRTC update, and initialization with each selected format list.
