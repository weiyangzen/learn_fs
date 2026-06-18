# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_fourcc.c

## Purpose
`drm_fourcc.c` centralizes DRM pixel-format metadata and legacy fb format translation. It maps bpp/depth or command-line color modes to FourCC formats, returns `drm_format_info` records, allows drivers to override format info for modifiers, and computes block dimensions, bits per pixel, and minimum pitch.

## Important APIs, Types, And Functions
Important exports are `drm_mode_legacy_fb_format()`, `drm_driver_legacy_fb_format()`, `drm_driver_color_mode_format()`, `drm_format_info()`, `drm_get_format_info()`, `drm_format_info_block_width()`, `drm_format_info_block_height()`, `drm_format_info_bpp()`, and `drm_format_info_min_pitch()`. Internal `__drm_format_info()` searches a static table of `struct drm_format_info` covering indexed, RGB, alpha, high-depth, YUV, packed, planar, and block-coded formats.

## Control Flow
Legacy format selection first maps bpp/depth to a canonical FourCC, then `drm_driver_legacy_fb_format()` applies device quirks for host byte order and XBGR 30 bpp preference. `drm_driver_color_mode_format()` interprets color-mode values for fbdev use. Format lookup linearly scans the static table and warns through `drm_format_info()` for unsupported formats. Block width/height helpers return explicit block dimensions or one-pixel defaults, and bpp/min-pitch derive byte and block geometry.

## State, Persistence, And Dependencies
There is no mutable state. The persistent data is the compiled static format table, whose fields include `format`, `depth`, `num_planes`, `cpp` or `char_per_block`, `block_w`, `block_h`, subsampling, alpha, indexed, and YUV flags. Dependencies include DRM device mode_config quirks and optional driver `get_format_info` callbacks.

## Integration Points
Framebuffer creation, plane validation, fbdev emulation, DMA address helpers, and format conversion helpers all rely on this metadata. Drivers can customize modifier-specific descriptions through `dev->mode_config.funcs->get_format_info()`, while core validation still uses `__drm_format_info()` to reject unknown FourCCs.

## Risks
The static table is a central contract; incorrect block sizes, plane counts, subsampling, or alpha/YUV flags can break framebuffer validation, pitch calculation, DMA addressing, and userspace-visible format behavior. Big-endian compatibility relies on driver quirks. `drm_format_info_bpp()` divides by block dimensions and assumes populated `char_per_block` for formats where bpp is meaningful.

## Test Signals
Tests should cover legacy bpp/depth mappings, device byte-order quirks, color-mode mappings, lookup for representative RGB/YUV/indexed/block formats, bpp and minimum pitch for packed and block-coded formats, unsupported format warnings, and driver-specific `get_format_info` override behavior.
