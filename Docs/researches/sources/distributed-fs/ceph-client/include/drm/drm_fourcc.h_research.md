# sources/distributed-fs/ceph-client/include/drm/drm_fourcc.h

Purpose: Defines DRM pixel-format metadata and helper APIs for interpreting FourCC formats, host-endian aliases, plane counts, bytes-per-block, block geometry, chroma subsampling, alpha/YUV/indexed flags, bpp, pitch, and legacy format mapping.

Important APIs, types, and functions: Defines `DRM_FORMAT_MAX_PLANES`, host-endian aliases for common formats, `struct drm_format_info`, inline predicates for YUV packed/semiplanar/planar layouts and 4:1:0, 4:1:1, 4:2:0, 4:2:2, and 4:4:4 sampling, plane width/height helpers, and APIs `__drm_format_info()`, `drm_format_info()`, `drm_get_format_info()`, `drm_mode_legacy_fb_format()`, `drm_driver_legacy_fb_format()`, `drm_driver_color_mode_format()`, `drm_format_info_block_width()`, `drm_format_info_block_height()`, `drm_format_info_bpp()`, and `drm_format_info_min_pitch()`.

Control flow: Framebuffer creation and plane validation look up a format through static tables or the driver's `get_format_info` hook, then use plane/block/subsampling helpers to validate dimensions, pitches, offsets, and minimum memory requirements. Legacy bpp/depth and driver color modes are translated to FourCC values for old IOCTLs and fbdev paths.

State and persistence: Format info is static metadata and has no mutable state. It defines userspace ABI interpretation of FourCC/modifier combinations and must remain stable.

Dependencies and integration points: Depends on UAPI `drm_fourcc.h`, DRM devices, and kernel math helpers. Integrated by framebuffer creation, planes, format conversion helpers, dumb-buffer sizing, modifiers, fbdev, and display drivers.

Risks and test signals: Risks include wrong block dimensions for packed or tiled formats, pitch underestimation, YUV subsampling dimension rounding errors, endian alias mistakes, legacy bpp/depth mismatches, and driver hook divergence from core format tables. Test RGB/YUV/indexed formats, multi-plane pitches, odd chroma dimensions, modifier-specific format info, legacy fb format mapping, and minimum-pitch calculations.
