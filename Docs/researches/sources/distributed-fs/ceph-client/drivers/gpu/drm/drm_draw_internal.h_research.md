# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_draw_internal.h

Purpose: Private DRM drawing header that declares color conversion, blit, and fill helpers and defines inline bitmap helpers for glyph drawing.

Important APIs/types/functions: Inline helpers are `drm_draw_is_pixel_fg`, which tests a bit in a 1-bpp source bitmap, and `drm_draw_get_char_bitmap`, which returns the bitmap start for a character in a `struct font_desc`. It declares all drawing functions implemented in `drm_draw.c`: format support, XRGB8888 color conversion, 16/24/32-bit blits, and 16/24/32-bit fills.

Control flow: The foreground test computes `sbuf8[(y * spitch) + x / 8] & (0x80 >> (x % 8))`, matching MSB-first glyph bitmap storage. Character lookup advances by `c * font->height * font_pitch`.

State and persistence behavior: No state is stored. The helpers operate on caller-owned font/bitmap memory and destination maps.

Dependencies and integration points: Includes Linux font and integer types and forward-declares `struct iosys_map`. It is consumed by DRM drawing users and `drm_draw.c`, providing a compact internal contract without exposing these helpers as public UAPI.

Risks: Callers must pass a character index valid for the font data and a pitch matching the font bitmap layout. Negative or out-of-range x/y values in `drm_draw_is_pixel_fg` would index invalid memory; callers and blit loops are responsible for sane coordinates.

Test signals: Unit-style checks for MSB-first bit extraction, glyph pointer offsets for known font dimensions and pitch, declarations matching `drm_draw.c`, and draw callers clipping source coordinates before invoking inline helpers.
