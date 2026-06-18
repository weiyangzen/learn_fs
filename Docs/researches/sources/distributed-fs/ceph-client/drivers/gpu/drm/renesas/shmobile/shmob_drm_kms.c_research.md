# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.c

## Purpose

`shmob_drm_kms.c` implements mode-setting initialization and framebuffer format validation for the legacy SH Mobile DRM driver.

## Important APIs, Types, and Functions

`shmob_drm_format_infos[]` maps DRM formats to LCDC data format, swap, bus source, and bpp register values. Public functions are `shmob_drm_format_info()` and `shmob_drm_modeset_init()`. `shmob_drm_fb_create()` validates formats and pitch constraints before creating GEM framebuffers.

## Control Flow

Modeset init initializes mode config, creates CRTC, encoder, and connector, resets mode config, starts polling, and sets min/max size and mode config funcs. Framebuffer creation rejects unsupported formats, primary pitches not 8-byte aligned or >=65536, and YUV chroma pitches that do not match the required relationship to luma pitch.

## State and Persistence Behavior

Format metadata is static. DRM mode_config persists in the DRM device. Framebuffer objects are managed by DRM GEM helpers.

## Dependencies and Integration Points

It depends on DRM atomic/GEM framebuffer helpers, local CRTC/plane/register definitions, and `shmob_drm_device`.

## Risks and Edge Cases

- Mode config funcs are assigned after `drm_mode_config_reset()`, which is unusual; users should confirm no reset path needs funcs earlier.
- YUV pitch validation assumes specific chroma layout rules from the LCDC hardware.
- Max mode size is 4095x4095, but timing register fields and external panels may impose smaller limits.

## Test Signals

Framebuffer creation tests for every supported format, pitch alignment, pitch upper bound, YUV chroma pitch mismatch, CRTC/encoder/connector init failures, and connector polling startup are important.
