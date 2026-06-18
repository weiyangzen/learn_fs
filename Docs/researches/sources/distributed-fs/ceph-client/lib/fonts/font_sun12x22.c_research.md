# sources/distributed-fs/ceph-client/lib/fonts/font_sun12x22.c

## Purpose

`font_sun12x22.c` defines the compiled-in Sun 12x22 console bitmap font. It provides a large fixed-width monochrome font intended for high-resolution console use and Sun/SPARC-style visual compatibility. Like other generated font files in this directory, it contributes static data plus a `struct font_desc` descriptor for the common font registry.

The file is data-focused: it contains 256 glyphs, each 12 pixels wide and 22 scanlines tall, encoded as packed bytes. Because 12 pixels require two bytes per scanline, every glyph consumes 44 bytes.

## Important APIs, Types, and Objects

- `#include "font.h"` supplies `struct font_data`, `struct font_desc`, and `SUN12x22_IDX`.
- `#define FONTDATAMAX 11264` is the raw glyph-table size. This matches `256 glyphs * 22 rows * 2 bytes per row`.
- `static const struct font_data fontdata_sun12x22` contains four zeroed `extra` words followed by the glyph table.
- `const struct font_desc font_sun_12x22` publishes the descriptor:
  - `.idx = SUN12x22_IDX`
  - `.name = "SUN12x22"`
  - `.width = 12`
  - `.height = 22`
  - `.charcount = 256`
  - `.data = fontdata_sun12x22.data`
  - `.pref = 5` on `__sparc__`
  - `.pref = -1` otherwise

The bitmap comments show 12 visible bits per row. The second byte carries four visible high-order bits plus four padding bits, consistent with the generic glyph pitch calculation.

## Control Flow and Data Layout

There is no executable control flow in this file beyond static object initialization. The compiler emits read-only bitmap data and one descriptor. Runtime font selection and rendering happen through shared font infrastructure.

The glyph table is ordered by character code:

- Each glyph begins with a comment such as `/* 65 0x41 'A' */`.
- Each of the 22 scanlines uses two bytes.
- The visible width is 12 bits; padding bits in the low nibble of the second byte are not part of the glyph.
- The final descriptor follows the closing `fontdata_sun12x22` initializer.

Direct source checks for this research found 256 glyph labels and 11264 byte literals, matching `FONTDATAMAX` and the descriptor geometry.

## State and Persistence Behavior

The file defines immutable compiled-in data. It performs no allocation, mutation, locking, reference counting, or I/O. Its only state-like behavior is architecture-dependent descriptor preference: `.pref` is set at compile time based on whether `__sparc__` is defined.

The `font_desc.data` pointer targets `fontdata_sun12x22.data`, so consumers must treat the data as read-only and rely on static lifetime. Dynamic font import/export metadata from `font_data_t` is not managed here.

## Dependencies and Integration Points

- Build integration is controlled by `lib/fonts/Makefile`: `font-$(CONFIG_FONT_SUN12x22) += font_sun12x22.o`.
- Configuration is controlled by `lib/fonts/Kconfig`: `CONFIG_FONT_SUN12x22` depends on `FRAMEBUFFER_CONSOLE || DRM_PANIC` and on `!SPARC && FONTS` in the inspected tree, with help text describing it as a high-resolution Sun font.
- Registration happens in `lib/fonts/fonts.c` under `#ifdef CONFIG_FONT_SUN12x22`, where `&font_sun_12x22` is added to the `fonts[]` table.
- Public declarations are in `include/linux/font.h` as `extern const struct font_desc font_sun_12x22`.
- Consumers use `find_font("SUN12x22")` or `get_default_font()`, then render via generic bitmap paths. The descriptor participates in default-font scoring, including the architecture-specific `.pref` value.
- The 12-pixel width is a relevant integration case for `font_rotate.c` because it is not byte-aligned and requires correct padding-bit handling during rotated console rendering.

## Risks and Edge Cases

- Table geometry consistency is the main risk. The data must remain exactly 11264 bytes for 256 12x22 glyphs; any mismatch can corrupt glyph indexing.
- The low four bits of each second scanline byte are padding. If generated data sets padding bits or a consumer treats pitch bits as visible width, rendering or rotation may show artifacts.
- The `#ifdef __sparc__` preference split means the same source file can influence default font selection differently across architectures.
- Kconfig/build logic must stay aligned with the exported descriptor. Enabling `CONFIG_FONT_SUN12x22` without compiling this object would break the registry; compiling it without registration wastes image space.
- Large static font data increases built image size by more than small fonts. This is expected for optional compiled-in fonts but is still relevant for tiny systems.
- There are no local assertions binding `FONTDATAMAX`, `.charcount`, `.width`, and `.height`, so source review or generated checks are important.

## Test Signals

- Compile with `CONFIG_FONT_SUPPORT=y` and `CONFIG_FONT_SUN12x22=y`; `fonts.c` should register the descriptor without unresolved symbols.
- `find_font("SUN12x22")` should return width 12, height 22, charcount 256, and non-NULL data when the config is enabled.
- Source-level invariants checked for this research: 256 glyph labels and 11264 byte literals.
- Rendering smoke tests should include ASCII and high-half glyphs on framebuffer console or DRM panic/log paths.
- Rotation tests should include this font or a 12x22 sample because its width is not byte-aligned, making padding handling observable.
- Architecture-sensitive default-font tests should confirm `.pref = 5` when compiling for `__sparc__` and `.pref = -1` otherwise.
