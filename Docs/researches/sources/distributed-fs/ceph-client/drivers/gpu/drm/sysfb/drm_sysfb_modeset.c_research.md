# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_modeset.c

## Purpose

`drm_sysfb_modeset.c` implements the shared fixed-mode atomic modesetting helpers for system framebuffer DRM drivers. It builds supported format lists, selects blitters, validates shadow-plane updates, copies damage clips into the firmware scanout buffer, clears disabled planes, handles fixed CRTC/connector behavior, and manages custom plane/CRTC state.

## Important APIs, Types, and Functions

- `drm_sysfb_mode()`: creates a 60 Hz fixed mode and derives physical size from 96 dpi when absent.
- `drm_sysfb_build_fourcc_list()`: normalizes native alpha formats to non-alpha equivalents and appends emulated `XRGB8888`.
- `drm_sysfb_get_blit_func()`: maps source/destination format pairs to memcpy or DRM conversion helpers.
- `drm_sysfb_plane_helper_begin_fb_access()`: starts shadow FB access and stores the blit function for the transaction.
- `drm_sysfb_plane_helper_atomic_check()`: enforces no scaling, sets CRTC format, and reserves conversion buffer when needed.
- `drm_sysfb_plane_helper_atomic_update()`: iterates damage and blits to the scanout buffer.
- `drm_sysfb_plane_helper_atomic_disable()`: clears the disabled region to black.
- State helpers for plane and CRTC reset/duplicate/destroy.
- `drm_sysfb_crtc_helper_mode_valid()` and `atomic_check()`: fixed-mode and primary-plane/gamma validation.
- `drm_sysfb_connector_helper_get_modes()`: applies optional one-block EDID and always returns the fixed mode.

## Control Flow

Concrete drivers initialize one native format and fixed mode. During atomic check, the helper rejects scaling, records the hardware framebuffer format in CRTC state, and reserves a conversion buffer if the userspace framebuffer format differs. Begin-access selects a concrete blitter from the userspace format to the current CRTC format. Atomic update obtains CPU access to the GEM framebuffer, enters the DRM device, iterates damage clips, offsets the destination scanout map, and invokes the blitter. Connector probing reads optional EDID through a custom block reader that suppresses extensions, then reports the fixed firmware mode.

## State and Persistence Behavior

Per-plane state stores the blit function and DRM shadow state, including conversion buffer state. Per-CRTC state stores the effective scanout format, which can differ from native format in VESA palette emulation. The physical firmware framebuffer contents persist in `sysfb->fb_addr`; updates modify it directly. Disable clears only the current source-sized region.

## Dependencies and Integration Points

It depends on DRM atomic, damage, EDID, framebuffer conversion, GEM shadow framebuffer, panic scanout, and probe helpers. It integrates with all sysfb drivers through the callback macro bundles in `drm_sysfb_helper.h`.

## Risks and Edge Cases

- Blit support is intentionally limited: native memcpy or XRGB8888-to-native conversions. Unsupported pairs fail begin access.
- EDID helper only exposes the base block and clears extension count, which is safe for limited firmware EDID but loses extension modes.
- `atomic_disable()` uses `dst.vaddr_iomem` directly and notes a TODO for mapping abstraction; normal-memory mappings may need care.
- Damage handling assumes no scaling and primary plane alignment.
- Clearing disabled planes writes zeros, which may not represent ideal black for every exotic format.

## Test Signals

Tests should cover native format ordering, alpha-to-X format normalization, XRGB8888 emulation, unsupported conversion rejection, damage clip blits, disable clears, fixed-mode validation, gamma LUT length checks, EDID with extension count, and panic scanout buffer reporting.
