# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_helper.c

## Purpose
`drm_format_helper.c` implements generic framebuffer copy, byte-swap, and format-conversion helpers for simple display drivers. It focuses on clipped transfers from DRM framebuffers, usually XRGB8888 input, into device-native formats including RGB332, RGB565, RGB888/BGR888, 1555/5551, 8888 channel permutations, 2101010, grayscale, mono, gray2, and ARGB4444.

## Important APIs, Types, And Functions
State APIs are `drm_format_conv_state_init()`, `drm_format_conv_state_copy()`, `drm_format_conv_state_reserve()`, and `drm_format_conv_state_release()`. Copy/conversion APIs include `drm_fb_clip_offset()`, `drm_fb_memcpy()`, `drm_fb_swab()`, many `drm_fb_xrgb8888_to_*()` helpers, `drm_fb_argb8888_to_argb4444()`, `drm_fb_xrgb8888_to_mono()`, and `drm_fb_xrgb8888_to_gray2()`. Internals include `__drm_fb_xfrm()`, `__drm_fb_xfrm_toio()`, `drm_fb_xfrm()`, and vectorized line conversion helpers for 32-to-8/16/24/32 bit output.

## Control Flow
Generic transform helpers compute clipped line counts and source offsets, optionally allocate temporary storage when reading uncached or writing I/O memory, and process one line at a time. `drm_fb_memcpy()` walks all planes and copies clipped bytes with per-plane pitch handling. `drm_fb_swab()` selects 16-bit or 32-bit byte swapping based on bits per pixel. Most conversion wrappers set a destination pixel size and call `drm_fb_xfrm()` with a format-specific line function that uses inline pixel converters from `drm_format_internal.h`. Mono and gray2 conversions first copy one source line, convert XRGB8888 to BT.601 gray8, then pack one or two bits per pixel.

## State, Persistence, And Dependencies
Persistent state is optional temporary memory stored in caller-owned `struct drm_format_conv_state`; it can be reused across conversions and released explicitly. The helpers otherwise operate on caller-provided `iosys_map` arrays, framebuffer metadata, pitches, and clips. Dependencies include DRM rect helpers, DRM format metadata, iosys-map memory access, `memcpy_toio()`, endian conversion helpers, and `drm_format_internal.h` pixel conversion functions.

## Integration Points
Simple KMS drivers, fbdev emulation paths, panic paths, and manual-update drivers use these helpers when hardware scanout format differs from the framebuffer format or when copying from a shadow buffer to device memory. The helpers are deliberately generic and exported so drivers do not duplicate conversion loops.

## Risks
Several helpers are explicitly single-plane only in the transform path; multi-plane support is limited to raw `drm_fb_memcpy()`. Source I/O memory is not handled in `drm_fb_xfrm()`. Temporary allocation failures can drop conversions. Packed mono/gray2 bit ordering starts at the clip's first pixel rather than forcing byte-aligned x coordinates. Callers must supply clips and destination pitch consistent with the target hardware.

## Test Signals
Tests should cover clipped copies across pitch boundaries, destination I/O memory, uncached source hint behavior, temporary buffer reuse and release, every exported conversion with known pixel fixtures, endian byte-swap paths, mono and gray2 packing for non-multiple-of-8 or non-multiple-of-4 widths, invalid source format warnings, and multi-plane memcpy behavior.
