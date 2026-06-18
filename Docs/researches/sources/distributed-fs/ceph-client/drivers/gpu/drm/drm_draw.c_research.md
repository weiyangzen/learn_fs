# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw.c

Purpose: Provides low-level DRM drawing helpers for converting XRGB8888 colors and drawing monochrome bitmap glyphs or solid fills into mapped framebuffer memory for common 16-, 24-, and 32-bit pixel layouts.

Important APIs/types/functions: Exports `drm_draw_can_convert_from_xrgb8888`, `drm_draw_color_from_xrgb8888`, `drm_draw_blit16`, `drm_draw_blit24`, `drm_draw_blit32`, `drm_draw_fill16`, `drm_draw_fill24`, and `drm_draw_fill32`. It uses conversion helpers from `drm_format_internal.h`, pixel formats from `drm_fourcc.h`, foreground-bit helpers from `drm_draw_internal.h`, and `iosys_map_wr` for memory or I/O mapped destinations.

Control flow: Format support is a switch over specific RGB565, RGB/X/ARGB 1555, RGB888, X/ARGB/XBGR/ABGR8888, and 2101010 variants. Color conversion dispatches to per-format helpers and warns once for unsupported formats. Blit helpers iterate destination pixels, sample a monochrome source bitmap at `x / scale, y / scale`, and write only foreground pixels in the requested output width. The 24-bit path writes three bytes explicitly in little-endian blue/green/red order. Fill helpers iterate every destination pixel and write the supplied converted color, also using explicit byte writes for 24-bit pixels.

State and persistence behavior: No state is retained. All writes go directly to the caller-provided `struct iosys_map` at offsets computed from pitch, coordinates, and bytes per pixel. Source bitmap data is read-only and caller-owned.

Dependencies and integration points: Used by DRM panic/console or simple drawing paths that need to render glyphs or fills into framebuffers without a full acceleration stack. Integrates with Linux `iosys-map`, DRM fourcc formats, and internal pixel conversion helpers.

Risks: Callers must ensure destination dimensions, pitch, scale, and mapping are valid; the helpers do no bounds checking. Unsupported formats return false/0 and conversion emits a WARN_ONCE. The 24-bit write order assumes the expected little-endian byte layout. Blit only paints foreground pixels and leaves background untouched, so callers must pre-fill if they need a background color.

Test signals: Color conversion tests for every supported format, unsupported format warning/zero return, 16/24/32 blit output for representative glyph bitmaps and scale factors, fill output and pitch handling, 24-bit byte order verification, iosys_map I/O and system-memory destinations, and bounds tests in callers that clip draw rectangles before invoking these helpers.
