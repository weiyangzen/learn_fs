# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_helper.h

## Purpose

`drm_sysfb_helper.h` is the shared interface for DRM system framebuffer drivers. It declares metadata parsing helpers, the common `drm_sysfb_device` state, shadow-plane state extensions, fixed-mode CRTC/connector helpers, and macro bundles for plane/CRTC/connector/mode-config callbacks.

## Important APIs, Types, and Definitions

- `struct drm_sysfb_format`: maps a generic `pixel_format` to a DRM FourCC.
- Validation and screen-info helper declarations.
- `drm_sysfb_mode()`: fixed display mode constructor.
- `struct drm_sysfb_device`: embeds `drm_device`, optional EDID, fixed mode, native format, pitch, gamma LUT size, and framebuffer address.
- `struct drm_sysfb_plane_state`: extends DRM shadow plane state with a selected blit function.
- Plane helpers: fourcc-list builder, begin access, atomic check/update/disable, scanout-buffer support, reset/duplicate/destroy.
- `struct drm_sysfb_crtc_state`: extends CRTC state with current CRTC input format.
- CRTC and connector helper declarations plus callback macro bundles.

## Control Flow and State

Concrete drivers embed `drm_sysfb_device`, initialize fixed hardware metadata, then wire helper macro bundles into their plane, CRTC, connector, and mode-config function tables. The helpers keep per-plane blit state and per-CRTC format state across atomic transactions.

## Dependencies and Integration Points

It depends on DRM core, GEM shadow framebuffer, modes, iosys-map, and video pixel-format types. It integrates every sysfb concrete driver with DRM atomic helpers, fbdev/shmem helpers, fixed connector probing, and framebuffer conversion routines.

## Risks and Edge Cases

- Macro bundles hide many function-table entries; concrete drivers must add `.destroy` methods and any custom overrides correctly.
- `drm_sysfb_device` assumes one fixed scanout buffer and one fixed mode.
- `fb_gamma_lut_size` is optional; color management only works when concrete drivers also provide palette/gamma write hooks.
- The scanout address can be I/O memory or normal memory; helpers must respect `iosys_map` semantics.

## Test Signals

Build all concrete drivers after helper signature changes. Atomic tests should cover state duplication/destruction, format conversion setup, connector mode probing with and without EDID, scanout-buffer export, and gamma LUT length validation.
