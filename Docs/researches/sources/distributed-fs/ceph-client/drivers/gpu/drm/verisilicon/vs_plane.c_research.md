<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.c

## Purpose
`vs_plane.c` provides shared VeriSilicon plane helpers for translating DRM formats into DC color/swizzle fields and computing DMA start addresses for a framebuffer source rectangle.

## Important APIs, Types, and Functions
The public functions are `drm_format_to_vs_format(u32 drm_format, struct vs_format *vs_format)` and `vs_fb_get_dma_addr(struct drm_framebuffer *fb, const struct drm_rect *src_rect)`. It maps common 16/32-bit RGB/XRGB/ARGB/BGR/RGBA formats to `enum vs_color_format` and `enum vs_swizzle`.

## Control Flow
Format translation selects a hardware color format first, then a channel swizzle based on fourcc ordering, defaults to ARGB swizzle for formats where swizzle is not meaningful, and clears UV swizzle. DMA address calculation gets plane 0's DMA GEM object, starts from `dma_addr + fb->offsets[0]`, then adds x offset using `drm_format_info_min_pitch()` and y offset using framebuffer pitch.

## State and Persistence Behavior
The helpers do not persist state. Their outputs are immediately used by plane register programming. DMA addresses refer to persistent DMA GEM backing memory while the framebuffer is alive.

## Dependencies and Integration Points
The file depends on DRM framebuffer DMA helpers, GEM DMA objects, fourcc metadata, and `vs_plane.h`. `vs_primary_plane.c` consumes both helpers during atomic update.

## Risks
Unexpected formats only warn and leave `color` potentially unchanged if caller provided uninitialized storage. Only plane 0 is handled. Source coordinates are 16.16 fixed-point and are shifted before address calculation; scaling is disallowed elsewhere, so this is safe only with matching atomic checks.

## Test Signals
Unit tests should cover every advertised fourcc, swizzle mapping, DMA address calculation for nonzero offsets/src x/y, and rejection prevention for unadvertised formats in plane init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.c -->
