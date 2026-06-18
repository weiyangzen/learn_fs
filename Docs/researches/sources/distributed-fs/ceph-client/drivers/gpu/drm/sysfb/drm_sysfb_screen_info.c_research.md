# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/drm_sysfb_screen_info.c

## Purpose

`drm_sysfb_screen_info.c` provides shared parsing helpers for firmware framebuffer metadata stored in Linux `struct screen_info`.

## Important APIs, Types, and Functions

- `drm_sysfb_get_width_si()` and `drm_sysfb_get_height_si()`: validate `lfb_width` and `lfb_height`.
- `drm_sysfb_get_memory_si()`: converts `screen_info` framebuffer resources into a `struct resource`.
- `drm_sysfb_get_stride_si()`: uses `lfb_linelength` or the format minimum pitch and validates against resource size divided by height.
- `drm_sysfb_get_visible_size_si()`: computes `PAGE_ALIGN(height * stride)` and validates against resource size.
- Internal `drm_sysfb_get_validated_size0()`: non-zero and max validation for 64-bit sizes.

## Control Flow

EFI and VESA drivers call these helpers after verifying the firmware video type. Width, height, memory, stride, and visible size are validated before any aperture acquisition or mapping. Missing stride falls back to minimum pitch for the detected format.

## State and Persistence Behavior

This file is stateless and only exports helper symbols when `CONFIG_SCREEN_INFO` includes it in the helper object.

## Dependencies and Integration Points

It depends on Linux screen-info resource helpers, DRM FourCC format helpers, and sysfb validation helpers. It integrates primarily with `efidrm.c` and `vesadrm.c`.

## Risks and Edge Cases

- `height * stride` is computed before `PAGE_ALIGN()` without an explicit overflow helper; validated inputs and resource limits reduce but do not fully document this assumption.
- Stride maximum is `size / height`, so height must already be non-zero.
- The helper returns NULL for missing memory rather than an error pointer.

## Test Signals

Tests should cover missing resources, zero width/height/stride, fallback pitch, resource-size-limited stride, visible-size page alignment, and oversized visible size rejection.
