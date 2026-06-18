# sources/distributed-fs/ceph-client/lib/fonts/font_rotate.c

## Purpose

`font_rotate.c` implements bitmap rotation helpers for the Linux font subsystem. It can rotate a single glyph by 90, 180, or 270 degrees clockwise, and can rotate an entire font-data buffer in 90-degree steps. The file is built when framebuffer console rotation is enabled and is used by fbcon clockwise, counter-clockwise, upside-down, and shared rotation paths.

Unlike the adjacent generated font tables, this file contains all runtime behavior for bit-level remapping, allocation/reuse of rotated font buffers, and exported GPL-only symbols.

## Important APIs, Types, and Functions

Public exported functions:

- `void font_glyph_rotate_90(const unsigned char *glyph, unsigned int width, unsigned int height, unsigned char *out)`
- `void font_glyph_rotate_180(const unsigned char *glyph, unsigned int width, unsigned int height, unsigned char *out)`
- `void font_glyph_rotate_270(const unsigned char *glyph, unsigned int width, unsigned int height, unsigned char *out)`
- `unsigned char *font_data_rotate(font_data_t *fd, unsigned int width, unsigned int height, unsigned int charcount, unsigned int steps, unsigned char *buf, size_t *bufsize)`

Private helpers:

- `font_glyph_bit_pitch(width)` returns a bit pitch rounded up to a byte boundary with `round_up(width, 8)`.
- `__font_glyph_pos(x, y, bit_pitch, bit)` maps logical pixel coordinates to a byte offset and mask. Bit position 0 is the most significant bit (`0x80`), matching the font bitmap convention.
- `font_glyph_test_bit()` reads one source pixel.
- `font_glyph_set_bit()` writes one destination pixel.
- `__font_glyph_rotate_90()`, `__font_glyph_rotate_180()`, and `__font_glyph_rotate_270()` perform the inner pixel-remapping loops without clearing the destination buffer.

External dependencies include `font_data_buf()` and `font_glyph_size()` from `include/linux/font.h`, kernel allocation helpers (`kmalloc_array`, `kfree`), `check_mul_overflow()`, `ERR_PTR()`, and standard `memset()`/`memcpy()`.

## Control Flow

Single-glyph rotation follows this pattern:

1. The public wrapper clears the output buffer with the exact destination glyph size. For 90 and 270 degrees, width and height are flipped in the `font_glyph_size()` call.
2. The wrapper calls the corresponding private `__font_glyph_rotate_*()` helper.
3. The private helper iterates over all input `y` rows and `x` columns.
4. For every set source bit, it computes the rotated destination coordinate and sets the output bit.

The rotation helpers account for packed scanline padding:

- Source and destination bit pitches are rounded to byte boundaries.
- `shift = (8 - (dimension % 8)) & 7` adjusts coordinate formulas when width or height is not a multiple of 8, preventing padding bits from being treated as visible pixels.
- 90-degree rotation uses output X coordinate `out_bit_pitch - 1 - y - shift` and output Y coordinate `x`.
- 180-degree rotation uses destination X `bit_pitch - 1 - x - shift` and destination Y `height - 1 - y`.
- 270-degree rotation uses destination X `y` and destination Y `bit_pitch - 1 - x - shift`.

Whole-font rotation in `font_data_rotate()` works as follows:

1. It reads the source glyph buffer using `font_data_buf(fd)`.
2. It computes source cell size with `font_glyph_size(width, height)`.
3. It normalizes `steps` with `steps %= 4`.
4. It chooses destination cell size: same size for steps 0 and 2, flipped geometry for steps 1 and 3.
5. It checks `charcount * d_cellsize` with `check_mul_overflow()`.
6. It either reuses the caller-provided buffer when large enough, or allocates a new buffer with `kmalloc_array()` and frees the old one.
7. It copies unchanged data for step 0, or clears and rotates each glyph for steps 1, 2, or 3.
8. It returns the usable buffer pointer, or an error pointer on allocation/size failure.

## State and Persistence Behavior

The file has no global mutable state. State is entirely caller-owned:

- Public single-glyph helpers mutate only the caller-provided `out` buffer.
- `font_data_rotate()` may allocate a new buffer, free the old `buf`, update `*bufsize`, and return the active buffer.
- The returned whole-font buffer contains raw glyph bytes only; it is explicitly not a full `font_data_t` object with metadata/refcount header.

There is no persistence I/O. The allocation semantics mirror `krealloc()` style reuse but are implemented as allocate-new/free-old when the current buffer is absent or too small.

## Dependencies and Integration Points

- Build integration: `lib/fonts/Makefile` adds `font_rotate.o` through `font-$(CONFIG_FRAMEBUFFER_CONSOLE_ROTATION)`.
- API declarations live in `include/linux/font.h`.
- Exported symbols use `EXPORT_SYMBOL_GPL`, so consumers must be GPL-compatible kernel code.
- Direct callers visible in this tree include:
  - `drivers/video/fbdev/core/fbcon_cw.c`, which uses `font_glyph_rotate_90()`.
  - `drivers/video/fbdev/core/fbcon_ud.c`, which uses `font_glyph_rotate_180()`.
  - `drivers/video/fbdev/core/fbcon_ccw.c`, which uses `font_glyph_rotate_270()`.
  - `drivers/video/fbdev/core/fbcon_rotate.c`, which uses `font_data_rotate()` to maintain rotated font data for console rendering.
- It depends on the generic font bitmap contract from `include/linux/font.h`: pitch is `DIV_ROUND_UP(width, 8)`, and glyph size is pitch times vertical pitch/height.

## Risks and Edge Cases

- Callers must provide correctly sized `out` buffers for single-glyph helpers. The functions clear the assumed destination size but do not validate the pointer or allocation length.
- Non-byte-aligned dimensions are sensitive to the `shift` adjustment. Off-by-one errors here would produce mirrored or shifted glyphs and may set bits in padding columns.
- `font_data_rotate()` returns error pointers (`ERR_PTR(-EINVAL)` or `ERR_PTR(-ENOMEM)`), not NULL; callers must use kernel error-pointer checks.
- If `bufsize` is NULL and a new buffer is allocated, the function cannot report the new size to the caller. The buffer is still returned, but future reuse by size requires the caller to track size separately.
- On allocation growth, the old `buf` is freed after successful allocation. On allocation failure, the old buffer is left untouched because `kfree(buf)` happens only after `kmalloc_array()` succeeds.
- `steps` values above 3 are accepted and normalized. Negative values are impossible because the type is unsigned.
- CPU cost is `O(charcount * width * height)` because every visible bit position is scanned.

## Test Signals

- Unit-style bitmap tests should cover 90, 180, and 270 degree rotations for byte-aligned and non-byte-aligned dimensions, especially widths/heights such as 8, 12, 14, and 22.
- A round-trip test rotating by 90 degrees four times should reproduce the original visible bitmap.
- `font_data_rotate(..., steps=0, ...)` should byte-copy the original data and use the destination size for the unrotated geometry.
- Buffer reuse tests should verify that a sufficiently large caller buffer is reused, while a too-small buffer is replaced and `*bufsize` is updated.
- Overflow tests should force `charcount * d_cellsize` to fail and confirm `ERR_PTR(-EINVAL)`.
- Integration smoke tests should exercise fbcon rotation modes and compare text placement/readability for fonts whose dimensions are not multiples of eight, such as SUN12x22.
