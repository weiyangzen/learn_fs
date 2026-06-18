# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.h

## Purpose

`shmob_drm_kms.h` declares SH Mobile KMS format metadata and modeset initialization.

## Important APIs, Types, and Functions

`struct shmob_drm_format_info` maps DRM fourcc to LCD data format register bits, source-image format bits, data swap bits, and bpp. `shmob_drm_format_is_yuv()` tests the color-conversion bit. Public declarations are `shmob_drm_format_info()` and `shmob_drm_modeset_init()`.

## Control Flow

Plane and framebuffer code use `shmob_drm_format_info()` to validate and program LCDC formats. Probe calls `shmob_drm_modeset_init()`.

## State and Persistence Behavior

No state is owned by the header; it defines metadata shape for static tables.

## Dependencies and Integration Points

It forward-declares GEM DMA and driver state types and depends on LCDC register macros for `LDDFR_CC` in the YUV helper.

## Risks and Edge Cases

The inline YUV helper requires `shmob_drm_regs.h` to be included before or alongside this header in C files that use it.

## Test Signals

Compile coverage and format validation tests for RGB/YUV formats.
