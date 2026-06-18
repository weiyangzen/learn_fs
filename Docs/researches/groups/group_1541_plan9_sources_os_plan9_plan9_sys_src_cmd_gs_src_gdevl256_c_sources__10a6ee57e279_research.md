# Group Research: group_1541_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevl256_c_sources__10a6ee57e279

Scope confirmed against `Docs/research_subset_a.md`: these files are under `sources/os/plan9/plan9`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl256.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl256.c

Implements the `lvga256` Ghostscript display device for Linux VGA/vgalib 256-color modes. It opens vgalib, selects the default VGA mode or `G320x200x256`, sets device dimensions from the actual mode, initializes the first 64 palette entries as a compatibility color cube, and manages remaining palette slots dynamically.

Main entry points are `lvga256_open`, `lvga256_close`, `lvga256_map_rgb_color`, `lvga256_map_color_rgb`, `lvga256_fill_rectangle`, `lvga256_tile_rectangle`, `lvga256_copy_mono`, `lvga256_copy_color`, and `lvga256_draw_line`. The device descriptor is `gs_lvga256_device`.

The dynamic color allocator stores 5-bit RGB triples in a fixed open-addressed hash table and assigns VGA palette indices from 64 through 255. When the palette is exhausted, RGB mapping returns `gx_no_color_index`.

Rendering is direct vgalib/`vgagl`: `gl_fillbox`, `gl_putbox`, `gl_setpixel`, and `gl_line`. This makes the file platform-specific and unsuitable for non-Linux/non-vgalib builds without conditional exclusion.

Notable limitation: `lvga256_map_color_rgb` is effectively a stub that always returns white, so reverse color mapping is not faithful.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl256.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl31s.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl31s.c

Implements the `lj3100sw` printer device for HP LaserJet 3100 Software output. It targets workflows where Ghostscript emits a spool format consumed by installed HP LaserJet 3100 software, including SMB printing through a Windows host.

The device uses `gdev_prn` printer infrastructure, media selection from `gdevmeds`, and custom section records. Main routines are `lj3100sw_print_page_copies`, `lj3100sw_close`, and helpers for section headers, buffered data emission, newline markers, and empty-line markers.

Raster output is monochrome run-length-like bit coding. The `code[2][65]` tables encode white and black pixel runs of up to 64 pixels, with special handling for all-white lines. High resolution is inferred from `x_pixels_per_inch > 300`; media dimensions and printer width/height come from fixed tables.

`select_medium` chooses among supported names (`a4`, `letter`, `legal`, envelopes, etc.), and the selected index drives the device-specific job header. Page data is horizontally centered by comparing printer width and Ghostscript page width.

Copies are represented in closing trailer records, not by re-rendering page data. Risks are mostly protocol brittleness: constants and section types are hard-coded to the HP software format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevl31s.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlbp8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlbp8.c

Provides Canon LBP-8II (`lbp8`) and Canon LIPS III (`lips3`) monochrome printer devices at 300 DPI. Both devices share `can_print_page`, differing mainly in initialization and termination command strings.

The code emits printer control sequences directly, then sends non-empty scanline segments. It trims trailing zero bytes, skips leading zero bytes by updating the horizontal column position, and splits output around long zero runs to reduce data sent to the printer.

Important constants include `LINE_SIZE`, 300 DPI defaults, and static init/end byte sequences for LBP-8 and LIPS III. Device descriptors are `gs_lbp8_device` and `gs_lips3_device`.

The raster path uses `gdev_prn_copy_scan_lines`, masks unused bits past page width with `rmask`, and sends graphics transfer commands via `fprintf` plus binary `fwrite`.

The file is narrow and device-protocol-specific. It assumes one-bit raster data and depends on exact ESC/CSI/DCS behavior for these Canon printers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlbp8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlj56.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlj56.c

Implements Ghostscript devices for HP LaserJet 5/6 PCL XL output: `lj5mono` and `lj5gray`. The mono device is 1-bit; the gray device is 8-bit grayscale with default gray mapping procedures.

The device writes a PCL XL file header in `ljet5_open`, a trailer in `ljet5_close`, and page/image records in `ljet5_print_page`. It relies on PCL XL helper headers (`gdevpx*`) plus stream output wrappers.

`ljet5_print_page` writes page setup, media selection, color space setup, image attributes, then emits every scanline with `eRLECompression`. Compression uses `gdev_pcl_mode2compress_padded`.

The implementation allocates a word-aligned scanline buffer and a worst-case compressed output buffer. It writes every raster line rather than doing sparse image segmentation, despite defining `MIN_SKIP_LINES`.

Main dependencies are Ghostscript printer memory access, PCL XL attribute/opcode helpers, and stream buffering. Failures are mostly allocation or scanline-copy errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlj56.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlp8k.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlp8k.c

Implements the Epson LP-8000 `lp8000` printer device using ESC/PAGE-style control sequences at 300 DPI. The long file comment documents the reverse-engineered printer data format, including simple and compressed modes.

The actual implementation only supports compressed data. `lp8000_print_page` allocates two scanline-sized buffers, writes a long fixed initialization sequence, skips blank lines, trims leading/trailing zero bytes, compresses repeated bytes, and emits each non-empty line with X/Y coordinate commands and compressed raster payload.

Compression rule: a repeated byte sequence is encoded as byte, byte, count-minus-two, split into chunks when the run exceeds 257 bytes. Non-repeated bytes are copied literally.

The driver applies fixed margins and a printer coordinate offset of 60 pixels. It recalculates X only when leading zero trimming changes the starting coordinate.

The file is very protocol-specific and hard-codes A4-oriented initialization and clipping values. It returns VM errors on buffer allocation failure and flushes/frees buffers on normal completion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlp8k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlxm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlxm.c

Implements `lxm5700m`, a monochrome Lexmark 5700 inkjet printer device. It is designed around the printer’s dual black printhead columns and supports a tunable `HeadSeparation` parameter.

The device subclass `lxm_device` extends `gx_device_printer` with `headSeparation`. Parameters are exposed through `lxm_get_params` and `lxm_put_params`, with accepted separation range 1 to 32 and default 16.

`lxm5700m_print_page` emits initialization commands, scans for non-blank swipes, copies 208-line swipe bands, computes horizontal extents, and builds compressed column data. Output alternates `RIGHTWARD`/`LEFTWARD` direction to account for which physical printhead handles even/odd columns.

Compression uses a per-column directory of 13 16-bit sectors for a 208-pixel column. Only non-empty sector bitmaps are emitted after the directory. Swipe overlap is fixed at 104 lines.

The code dynamically grows the swipe output buffer when needed. It is tightly bound to reverse-engineered Lexmark protocol details and includes comments noting uncertainty about mechanical behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlxm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm1.c

Implements the 1-bit memory bitmap devices `image1` and, on little-endian builds, `image1w`. These are core Ghostscript stored-bitmap devices for monochrome rendering.

The public device descriptor `mem_mono_device` uses custom RGB mapping, fill, copy-mono, strip-tile, and strip-copy-rop procedures. Color mapping supports inverted palettes by XORing with `mdev->palette.data[0]`.

`mem_mono_copy_mono` is heavily optimized for bit-aligned and unaligned transfers. It chooses copy modes from color0/color1 transparency and value combinations, then uses chunk fetch/write macros for OR, STORE, and AND operations.

`mem_mono_strip_tile_rectangle` reimplements monochrome strip tiling for performance, optimized for non-shifted two-color halftone tiles. It falls back to `gx_default_strip_tile_rectangle` for unsupported strip/phase combinations.

The little-endian word-oriented variant wraps fill/copy operations with `mem_swap_byte_rect` and uses `mem_word_get_bits_rectangle`. The file is central to bitmap performance and has substantial endian-specific logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm16.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm16.c

Implements the 16-bit true-color memory device `image16`. Pixel format is RGB 5:6:5, stored in big-endian byte order regardless of host endianness.

Color mapping packs red, green, and blue Ghostscript color values into a 16-bit 5/6/5 index. Reverse mapping expands those bit fields back to full `gx_color_value` ranges with bit replication.

Rendering hooks are `mem_true16_fill_rectangle`, `mem_true16_copy_mono`, and `mem_true16_copy_color`. Fill handles one-pixel, repeated-byte, and general 16-bit store cases, swapping byte order on little-endian hosts.

`copy_mono` writes 16-bit pixels for set/unset source bits while respecting transparent `gx_no_color_index` values. `copy_color` delegates to `mem_copy_byte_rect`.

The file is compact but important as the canonical 16-bit packed RGB memory implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm2.c

Implements 2-bit mapped-color memory devices `image2` and, on little-endian systems, `image2w`. The standard device stores four 2-bit pixels per byte.

`mem_mapped2_fill_rectangle` uses `bits_fill_rectangle` with precomputed fill patterns for color indices 0 to 3. `mem_mapped2_copy_mono` handles opaque and transparent monochrome source copies into 2-bit destinations with nibble-pair masks.

`mem_mapped2_copy_color` temporarily scales `dev->width` and delegates to the monobit memory device’s `copy_mono`, treating 2-bit pixels as paired bits for bulk copying.

The word-oriented variant wraps standard operations with byte swapping through `mem_swap_byte_rect`, then uses `mem_mono_word_device` for color copies.

This file depends on shared mapped-color mapping procedures (`mem_mapped_map_rgb_color`, `mem_mapped_map_color_rgb`) and low-level bit rectangle helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm24.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm24.c

Implements 24-bit RGB memory devices `image24` and little-endian `image24w`. Pixels are three bytes, with RGB mapping delegated to Ghostscript’s default RGB mapping procedures.

`mem_true24_fill_rectangle` is highly optimized. It has separate paths for wide fills, grayscale byte-identical colors, cached repeated RGB word patterns, narrow widths, and optional debug statistics. A per-device `color24` cache avoids recomputing rotated RGB word patterns.

`mem_true24_copy_mono` supports opaque halftone/inverted-mask cases and optimized stencil cases where only the one color is written. The stencil path processes first partial byte, full source bytes, and final residual bits.

`mem_true24_copy_alpha` blends a 2-bit or 4-bit alpha mask over existing RGB pixels by interpolating each channel toward the source color. `copy_color` delegates to byte-rectangle copying.

The word-oriented variant byte-swaps affected rectangles before/after calling the standard implementation or copying bytes. The file is a performance-sensitive true-color memory backend.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm24.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm32.c

Implements 32-bit memory devices `image32` and little-endian `image32w`. The device reports 24 color bits plus 8 alpha/extra bits and uses default RGB/CMYK mapping.

`mem_true32_fill_rectangle` arranges color bytes for host endian order, then fills 32-bit pixels. It has specialized paths for widths 1 to 4, zero-color `memset`, and wider repeated 32-bit stores.

`mem_true32_copy_mono` has an optimized transparent-zero case for character masks, writing only one-colored set bits. The opaque path writes zero/one colors per source bit, respecting transparent `one`.

`mem_true32_copy_color` delegates to `mem_copy_byte_rect`. The word-oriented variant swaps colors for fill/copy-mono and byte-swaps copied color rectangles.

The file is simpler than 24-bit because 32-bit pixels align naturally to word boundaries, reducing pattern-rotation complexity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm4.c

Implements 4-bit mapped-color memory devices `image4` and little-endian `image4w`. Standard storage packs two 4-bit pixels per byte.

`mem_mapped4_fill_rectangle` fills with precomputed byte patterns from color index 0 to 15. `mem_mapped4_copy_mono` separates transparent/masked and opaque cases, with the opaque path processing destination nibbles and source bits in pairs for speed.

`mem_mapped4_copy_color` temporarily scales the device width and delegates to monobit `copy_mono`, treating each 4-bit pixel as four bits.

The word-oriented variant wraps operations in `mem_swap_byte_rect` and delegates color-copy work to `mem_mono_word_device`.

This file is the 4-bit counterpart to `gdevm2.c`, with more complex nibble alignment handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm40.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm40.c

Implements 40-bit memory devices `image40` and little-endian `image40w`. Pixels are five bytes, using default RGB mapping and alpha-capable memory device setup.

The implementation follows the high-depth memory-device template: unpack color bytes, cache rotated 32-bit word patterns in `mdev->color40`, optimize grayscale fills with `memset`, handle narrow widths directly, and fill wide non-gray rectangles with repeated cached words.

`mem_true40_copy_mono` supports full opaque and stencil-style mono copies into 5-byte pixels. `mem_true40_copy_color` delegates to `mem_copy_byte_rect`.

The word-oriented variant swaps bit ranges with `mem_swap_byte_rect` before and after fill/copy and uses direct byte-copy for color data.

The unusual 5-byte stride creates more rotated-cache state than 24/48-bit devices; correctness depends on endian-specific cache macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm40.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm48.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm48.c

Implements 48-bit memory devices `image48` and little-endian `image48w`. Pixels are six bytes.

The fill path uses a three-word rotated color cache (`abcd`, `cdef`, `efab`) and has separate handling for gray byte-identical colors, wide non-gray fills, and narrow widths. The stride allows efficient two-pixel repeated stores.

`mem_true48_copy_mono` mirrors the other high-depth devices: unpack zero/one colors, process source bitmap bits, and optimize stencil cases by skipping zero source spans.

`mem_true48_copy_color` delegates to `mem_copy_byte_rect`; `image48w` wraps operations in byte swapping and direct byte rectangle copies.

This is a high-precision RGB memory backend with no custom alpha blending beyond default copy-alpha setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm56.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm56.c

Implements 56-bit memory devices `image56` and little-endian `image56w`. Pixels are seven bytes, requiring a seven-word rotated cache for efficient wide fills.

`mem_true56_fill_rectangle` handles gray colors via `memset`, non-gray wide fills via cached 32-bit word rotations, and narrow widths with direct byte assignments. The fill loops are stride-specialized for 7-byte pixels.

`mem_true56_copy_mono` writes unpacked 7-byte colors for opaque and stencil mono copies. It processes first partial source byte, full bytes, and final residual bits similarly to the 24/40/48-bit devices.

`mem_true56_copy_color` delegates to byte rectangle copying. The word-oriented device swaps affected bit ranges around standard operations.

The file is largely generated-pattern-like relative to the other high-depth memory devices, but the 7-byte stride makes cache and alignment cases especially error-prone.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm56.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm64.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm64.c

Implements 64-bit memory devices `image64` and little-endian `image64w`. Pixels are represented as two 32-bit chunks after endian-aware unpacking.

`mem_true64_fill_rectangle` fills direct 64-bit pixels using repeated pairs of 32-bit stores. Unlike 40/48/56-bit files, there is no rotated byte cache because the pixel size aligns cleanly to 8 bytes.

`mem_true64_copy_mono` supports opaque and stencil mono copies by writing two-word pixels for set or unset source bits. `mem_true64_copy_color` delegates to `mem_copy_byte_rect`.

The word-oriented variant swaps 64-bit pixel bit ranges before/after standard operations and copies color bytes with `bytes_copy_rectangle`.

This is the simplest high-depth backend structurally because the stride is word-aligned, though it still uses endian-specific color unpacking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm8.c

Implements 8-bit mapped-color memory devices `image8` and little-endian `image8w`. Each pixel is one byte.

`mem_mapped8_fill_rectangle` uses `bytes_fill_rectangle`. `mem_mapped8_copy_mono` dispatches to three helper loops for opaque (`mapped8_copy01`), stencil (`mapped8_copyN1`), and reverse-stencil (`mapped8_copy0N`) cases.

`mem_mapped8_copy_color` delegates to `mem_copy_byte_rect`. The strip-copy-rop implementation aliases `mem_gray8_rgb24_strip_copy_rop`.

The word-oriented device wraps fill and mono/color copies with `mem_swap_byte_rect` on little-endian systems, then uses either byte filling or the standard mapped8 copy routine.

This is the straightforward byte-per-pixel mapped memory backend and acts as a common grayscale/palette target.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.c

Implements the legacy Classic MacOS `macos` Ghostscript output device, producing QuickDraw PICT data. The file notes this device is superseded by the newer API/DISPLAY device.

The device descriptor `gs_macos_device` uses `gs_mac_procs`, including open/close/sync/output-page, rectangle fill, mono copy, line drawing, alpha copy, parameter get/put, and xfont support. Color depth can be 1, 4, 7, 8, or 24 bits.

`mac_open` allocates and initializes a PICT handle with a fixed header, then patches dimensions and resolution. `mac_sync_output` and `mac_output_page` finalize the current PICT with `OpEndPic` while allowing more drawing. `mac_save_pict` writes a 512-byte PICT file header plus PICT data when `OutputFile` is set.

Drawing operations emit QuickDraw PICT opcodes through macros from `gdevmacpictop.h`. `mac_copy_mono` writes BitsRect/PackBitsRect-style data with foreground/background colors and dither copy modes. `mac_copy_alpha` simulates alpha on white backgrounds by creating a shaded color table.

`mac_put_params` handles `UseExternalFonts`, `BitsPerPixel`, and `OutputFile`, including LockSafetyParams checks. `gsdll_get_pict` exposes the `PicHandle` to callers.

The implementation is platform-specific and depends on Mac Toolbox handles, QuickDraw, and Ghostscript DLL callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.h

Defines the shared declarations and data structures for the legacy MacOS PICT device. It includes Mac Toolbox headers, Ghostscript device/font headers, and `gdevmacpictop.h`.

The central type is `gx_device_macos`, extending `gx_device_common` with output filename/file state, `PicHandle`, current PICT write pointer, page-reset state, external font flag, and cached font state.

It declares all Mac device procedures used by `gdevmac.c`, including drawing, page handling, parameter handling, alpha copy, and xfont lookup support. It also defines the `mac_xfont` structure used by `gdevmacxf.c`.

The `CheckMem` macro grows the PICT handle while preserving the current write offset. `ResetPage` clears page-output state and resets PICT position/font cache before further drawing after an output page.

The header also defines default 8.5x11 page/device geometry at 72 DPI and exports `gsdll_get_pict` for external callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacpictop.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacpictop.h

Provides macro helpers for writing Classic MacOS QuickDraw PICT structures and opcodes. It is included by `gdevmac.h` and used heavily by `gdevmac.c` and `gdevmacxf.c`.

The first macro layer writes primitive byte/int/long values, QuickDraw `Point`, `Rect`, `Region`, `Pattern`, RGB colors, color tables, pixmaps, PackBits image data, and Pascal strings.

The opcode layer covers many PICT operations: clipping, patterns, text font/face/mode/size, colors, lines, text, rectangles, rounded rectangles, ovals, arcs, bitmap/pixmap image transfer, and end-picture handling.

`PICTWriteDataPackBits` either copies raw data for small rasters or calls QuickDraw `PackBits` per row and writes row lengths with correct byte padding. It allocates a temporary compression buffer.

The Ghostscript helper macros `GSSetStdCol`, `GSSetFgCol`, and `GSSetBkCol` convert Ghostscript color indices through the device’s `map_color_rgb` procedure and emit PICT RGB color opcodes.

This header is macro-heavy and assumes pointer expressions are mutable lvalues; it is tightly coupled to Classic MacOS data layout and QuickDraw APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacpictop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacttf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacttf.h

Defines small C structures for reading TrueType font directory and naming-table data from Mac font resources.

Types include `TTFontDirComponent`, `TTFontDir`, and `TTFontNamingTable`. The structures model the TrueType table directory and the beginning of the `name` table.

The only tag macro is `TTF_FONT_NAMING_TABLE`, defined as `'name'`. `gdevmacxf.c` uses it to locate the naming table while determining a Mac xfont’s platform encoding.

The file has no functions and no Ghostscript device hooks. It exists solely as a low-level parsing aid for the Classic/Carbon Mac xfont bridge.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacttf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacxf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacxf.c

Implements external font (`xfont`) support for the legacy Classic/Carbon MacOS device. It lets Ghostscript render eligible text through local Mac fonts and PICT text opcodes instead of bitmap glyphs.

The file defines MacRoman/ISO/Standard encoding translation tables, the `mac_xfont_procs` procedure record, and the GC structure descriptor `st_mac_xfont`.

`mac_lookup_font` checks `UseExternalFonts`, accepted encodings, font size, and transformation simplicity. It finds a Mac font family/style from the requested name, determines encoding from font resources, measures metrics through QuickDraw font APIs, and returns a `mac_xfont`.

`mac_char_xglyph` maps Ghostscript characters between Standard, ISO Latin-1, and MacRoman encodings. `mac_char_metrics` returns simple metrics from `FMetricRec`. `mac_render_char` emits PICT font-name/font/size/face changes as needed and writes a one-character `LongText` opcode.

`mac_find_font_family` tries full names, dash-normalized names, and basic style suffix extraction. `mac_get_font_encoding` inspects `sfnt` TrueType resources and their naming table platform ID. Optional compatibility wrappers are provided for older FontManager calls when the Carbon macro is disabled.

Limitations: glyph-name lookup is unsupported, transformations are rejected, and some reverse mapping tables are empty.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmacxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.c

Implements shared media selection support for printer drivers. The exported function is `select_medium`.

The file contains a static table of known media names with physical width, height, and priority. Priority is inverse area, so among acceptable media the smallest matching sheet/envelope is preferred.

`select_medium(gx_device_printer *pdev, const char **available, int default_index)` computes current page size in meters from device pixels and DPI, then scans the caller’s NULL-terminated available-media list. It returns the index of the smallest available medium whose dimensions exceed the page size within a 0.1 cm tolerance.

Supported names include ISO A/B sizes, ARCH sizes, letter/legal/ledger/executive/note, envelopes such as com10/dl/c5/monarch, and variants like flsa/flse.

This helper is used by printer drivers such as `gdevl31s.c` to map Ghostscript page size to device-specific media index tables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.c -->