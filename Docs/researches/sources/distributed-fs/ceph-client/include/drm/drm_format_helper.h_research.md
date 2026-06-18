# sources/distributed-fs/ceph-client/include/drm/drm_format_helper.h

Purpose: Declares framebuffer memory-copy, byte-swap, and pixel-format conversion helpers plus reusable temporary conversion state for drivers that need CPU-side scanout conversion.

Important APIs, types, and functions: Defines `struct drm_format_conv_state`, initializers `DRM_FORMAT_CONV_STATE_INIT` and `DRM_FORMAT_CONV_STATE_INIT_PREALLOCATED()`, state management functions, `drm_fb_clip_offset()`, `drm_fb_memcpy()`, `drm_fb_swab()`, and many XRGB8888/ARGB8888 conversion routines to RGB332, RGB565, RGB565BE, XRGB1555, ARGB1555, RGBA5551, RGB888, BGR888, ARGB8888, ABGR8888, XBGR8888, BGRX8888, XRGB2101010, ARGB2101010, GRAY8, MONO, GRAY2, and ARGB4444.

Control flow: Drivers initialize or reuse a conversion state, reserve temporary storage as needed, compute source offsets from clips and format info, then copy or convert the clipped framebuffer region from `iosys_map` source maps to destination maps using destination pitches. Preallocated state lets callers avoid allocation in sensitive paths.

State and persistence: Conversion state only caches temporary memory and whether it is caller-owned. Converted pixels are written to destination backing storage; no other persistent state exists.

Dependencies and integration points: Depends on DRM framebuffers, format info, rectangles, `iosys_map`, and GFP allocation flags. Integrates with fbdev emulation, shadow-plane helpers, simple display pipes, and drivers whose hardware accepts fewer formats than userspace can provide.

Risks and test signals: Risks include incorrect clip offset for multi-plane/block formats, temporary buffer lifetime mistakes, endian/byte-swap errors, alpha handling differences, pitch overruns, allocation failures in commit paths, and cached versus non-cached memory handling. Test every conversion format, odd widths/heights, unaligned clips, large pitch padding, preallocated state reuse, allocation failure, and visual CRC comparisons.
