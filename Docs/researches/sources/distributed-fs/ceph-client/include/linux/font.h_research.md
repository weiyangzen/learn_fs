# sources/distributed-fs/ceph-client/include/linux/font.h

## Purpose
This header defines kernel soft-font metadata, reference-counted font data helpers, glyph sizing helpers, rotation helpers, and declarations for built-in console fonts.

## APIs, types, and control flow
`font_glyph_pitch(width)` rounds bits per scanline to bytes, and `font_glyph_size(width, vpitch)` multiplies pitch by scanlines. `font_data_t` is an opaque raw glyph pointer with a hidden negative-offset header for optional CRC32, byte count, and refcount. Helpers import/export console fonts, get/put references, query size, compare data, and expose read-only raw bytes with `font_data_buf()`. Rotation helpers transform individual glyphs or full font data by 90/180/270 degrees. `struct font_desc` describes built-in fonts by id, name, geometry, character count, data, and preference. `find_font()` and `get_default_font()` select fonts.

## State and dependencies
Font data owns hidden metadata and refcount state. Built-in font descriptors are extern constants. Dependencies include console font structures, math helpers, CRC callback supplied by import, and video/console consumers.

## Integration, risks, and tests
Console, framebuffer, DRM console, and font loading paths use this interface. Risks include treating `font_data_t *` as a plain allocation, bad vertical pitch, refcount imbalance, CRC mismatch, rotation buffer sizing errors, and width/pitch confusion. Tests should cover glyph pitch for non-byte widths, import/export round trips, refcount put-to-zero behavior, equality checks, all rotations, default font selection, and malformed userspace font geometry.
