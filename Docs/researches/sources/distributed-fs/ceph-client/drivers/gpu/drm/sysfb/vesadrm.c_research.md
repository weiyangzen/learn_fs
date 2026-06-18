# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/vesadrm.c

## Purpose

`vesadrm.c` implements a DRM driver for VESA BIOS Extension framebuffers described by `screen_info`. It maps the VESA linear framebuffer, creates a fixed-mode atomic pipeline, supports palette/gamma programming through VGA DAC or 32-bit PMI where available, and provides special C8/RGB332 emulation behavior.

## Important APIs, Types, and Functions

- `struct vesadrm_device`: embeds `drm_sysfb_device`, optional 32-bit PMI palette pointer, color-map write callback, and mode objects.
- `vesadrm_get_format_si()`: maps `screen_info` pixel masks to DRM formats, including `C8`.
- Palette/gamma writers: `vesadrm_vga_cmap_write()` and optional `vesadrm_pmi_cmap_write()`.
- Gamma/palette fill/load helpers for component and indexed formats.
- `vesadrm_primary_plane_helper_atomic_check()`: extends sysfb atomic check to switch C8 hardware to RGB332 emulation for XRGB8888 input.
- `vesadrm_crtc_helper_atomic_flush()`: reloads palette/gamma on color-management changes.
- `vesadrm_device_create()`: parses metadata, maps memory, initializes color management and fixed-mode pipeline.

## Control Flow

Device creation requires `VIDEO_TYPE_VLFB`, validates format/geometry/resource/stride/visible size through screen-info helpers, chooses a palette writer using VGA DAC for VGA-compatible modes or VESA PMI on 32-bit x86, stores optional EDID, maps the framebuffer write-combined, initializes mode config, creates the primary plane with custom atomic check, creates a CRTC with custom flush, enables gamma LUT support if a palette writer exists, attaches encoder/connector, and resets mode config. Probe registers the DRM device and starts clients.

## State and Persistence Behavior

The framebuffer and palette hardware are firmware-initialized and persist while bound. `cmap_write` determines whether color management can program hardware. For C8 hardware, CRTC format state can temporarily switch to RGB332 when emulating XRGB8888, and atomic flush reloads the corresponding palette. Remove unplugs the DRM device.

## Dependencies and Integration Points

It depends on x86/sysfb screen_info, VGA I/O ports, optional 32-bit VESA PMI, aperture helpers, DRM color management, DRM shmem/fbdev helpers, EDID, and `drm_sysfb_helper`. It binds to `vesa-framebuffer` platform devices.

## Risks and Edge Cases

- PMI palette writing uses inline assembly and is only available on 32-bit x86.
- If a color-indexed format lacks a writable palette, colors may be incorrect and only a warning is emitted.
- C8/XRGB8888 emulation relies on switching effective CRTC format to RGB332 and reloading palette state.
- VGA port access requires correct mode classification by screen_info helpers.
- As with other screen-info drivers, invalid firmware geometry can cause mapping or visible-size rejection.

## Test Signals

Boot tests should cover VGA-compatible and non-VGA VESA modes, C8 palette updates, RGB332 emulation for XRGB8888 clients, gamma LUT loads for 555/565/888 formats, EDID attachment, aperture handoff, and invalid screen_info rejection.
