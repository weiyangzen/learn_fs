# Group Research: group_103_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevl256_c_sources_9cb2b6f26079

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl256.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl256.c

Implements the `lvga256` Ghostscript display device for Linux `vgalib` 256-color VGA modes. It registers `gs_lvga256_device` with custom open/close, RGB palette mapping, fill, tile, mono/color copy, and line drawing procedures.

Key behavior:
- `lvga256_open` initializes vgalib, selects the default VGA mode or `G320x200x256`, sets device dimensions from VGA mode, and initializes the first 64 palette entries as a coarse RGB cube.
- Dynamic colors start at palette index 64. `lvga256_map_rgb_color` maps exact coarse cube colors directly and otherwise hashes 5-bit RGB triples into `dynamic_colors`, assigning palette entries until index 255.
- If the dynamic palette is exhausted, color mapping returns `gx_no_color_index`.
- Drawing operations are direct vgalib calls: `gl_fillbox`, `gl_setpixel`, `gl_putbox`, and `gl_line`.
- `lvga256_copy_mono` handles transparent `zero`/`one` colors and pre-clears opaque rectangles before setting foreground pixels.
- `lvga256_tile_rectangle` optimizes opaque tiles by filling with `czero` and delegating the rest to `gx_default_tile_rectangle`.

Dependencies and notes:
- Requires `<vga.h>` and `<vgagl.h>`, so this is host/display-specific rather than Plan 9-specific code.
- `lvga256_map_color_rgb` is effectively a stub returning white for any color; it does not query the VGA palette.
- The dynamic color table uses linear probing with a sentinel-sized extra slot.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl256.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl31s.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl31s.c

Implements the `lj3100sw` printer device for HP LaserJet 3100 Software. It emits the proprietary stream expected by installed LaserJet 3100 software, with media selection support from `gdevmeds.c`.

Key behavior:
- Defines supported media names and printer dimensions for 300 dpi and high-resolution modes.
- Registers `gs_lj3100sw_device` via a printer device descriptor with custom `lj3100sw_print_page_copies` and `lj3100sw_close`.
- Uses `select_medium(pdev, media, LARGEST_MEDIUM)` to choose a medium that fits the rendered image.
- Encodes raster lines using two static variable-length code tables for white and black run lengths from 0 to 64 pixels.
- Buffers output in `BUFFERSIZE` chunks, emitting section headers with little-endian 16-bit fields.
- On a new printer file, writes job setup records including resolution, selected medium, printer width, and control fields.
- Centers page data horizontally inside the selected printer width.
- Handles all-white lines through compact empty-line byte sequences that differ by resolution.
- On close, writes termination sections and then delegates to `gdev_prn_close`.

Dependencies and notes:
- Relies on `gdevprn.h` and `gdevmeds.h`.
- `num_copies` argument is ignored; the driver uses `ppdev->NumCopies`.
- The run-length codec is local to this driver and tightly coupled to the LaserJet 3100 software protocol.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevl31s.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlbp8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlbp8.c

Implements Canon `lbp8` and `lips3` monochrome printer devices for Canon LBP-8II and LIPS III printers at 300 dpi.

Key behavior:
- Registers `gs_lbp8_device` and `gs_lips3_device`, each with device-specific paper size, margins, init string, and end string.
- `can_print_page` is the shared print routine.
- It writes printer initialization bytes, scans each Ghostscript raster line, masks unused bits at the right edge, strips trailing zero bytes, and skips empty lines.
- For non-empty rows, it emits vertical motion, horizontal motion, and raster graphics transfer commands.
- Long zero runs inside a row are skipped by splitting the output into shorter non-zero spans.
- Ends the page with an eject command and optional device-specific termination sequence.

Dependencies and notes:
- Uses `gdev_prn_copy_scan_lines` and `gdev_mem_bytes_per_scan_line`.
- The LBP init sequence uses ESC `[` CSI-style sequences; LIPS III uses DCS/ST job control sequences.
- `lbp8_end` is `NULL`, so `sizeof(lbp8_end)` is passed but ignored because the pointer is null.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlbp8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlj56.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlj56.c

Implements HP LaserJet 5/6 PCL XL printer devices: `lj5mono` and `lj5gray`.

Key behavior:
- Registers `gs_lj5mono_device` as 1-bit monochrome and `gs_lj5gray_device` as 8-bit grayscale.
- `ljet5_open` opens the Ghostscript printer and writes a PCL XL file header through stream helpers.
- `ljet5_close` writes the PCL XL trailer and closes the printer.
- `ljet5_print_page` writes a PCL XL page header, media selection, color-space setup, image header, and then one compressed image block per scan line.
- Monochrome output uses an indexed 1-bit palette; grayscale output uses direct 8-bit gray pixels.
- Each line is compressed with `gdev_pcl_mode2compress_padded`.
- Uses PCL XL token helpers from `gdevpx*.h`.

Dependencies and notes:
- Includes `stream.h`, `gdevpcl.h`, and PCL XL attribute/operator headers.
- `MIN_SKIP_LINES` is defined but not used; this implementation sends the whole image one line at a time.
- Allocates a padded word buffer for scanning and a separate output compression buffer.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlj56.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlp8k.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlp8k.c

Implements the `lp8000` Epson LP-8000 ESC/Page monochrome laser printer driver at 300 dpi.

Key behavior:
- Registers `gs_lp8000_device` with fixed margins and `lp8000_print_page`.
- Writes a large ESC/Page/EJL initialization sequence before raster output.
- Computes printer coordinates with a 60-pixel offset, then aligns the left margin to a byte boundary.
- Scans from top margin to bottom margin, skipping consecutive blank lines.
- For nonblank lines, trims leading and trailing zero bytes.
- Compresses remaining bytes using the LP-8000 repeated-byte format: two repeated bytes followed by an insertion count, splitting runs longer than 257 bytes.
- Emits X coordinate updates only when the trimmed left edge changes.
- Emits Y coordinate, compressed byte count, point count, bitmap mode command, and compressed data for each line.
- Writes a termination and reinitialization sequence at end of page.

Dependencies and notes:
- Uses `gdev_prn_get_bits` for blank-line detection and `gdev_prn_copy_scan_lines` for actual line copy.
- The long file comment documents the reverse-engineered LP-8000 protocol and its compressed data format.
- Handles only the 300x300 dpi mode described by the constants and init strings.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlp8k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlxm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlxm.c

Implements the `lxm5700m` Lexmark 5700 monochrome inkjet printer driver.

Key behavior:
- Defines `lxm_device`, a `gx_device_printer` subclass carrying `headSeparation`.
- Registers `gs_lxm5700m_device` at 600x600 dpi with default `HeadSeparation = 16`.
- Exposes `HeadSeparation` through `lxm_get_params` and validates it in `lxm_put_params` as 1 through 32.
- Emits printer initialization macros `init1`, `init2`, and `init3`.
- Prints in overlapping 208-pixel-high swipes with `overLap = 104`.
- Skips blank regions but backs up by the overlap distance so later swipes can reinforce earlier dots.
- Computes left/right byte bounds for each swipe.
- Encodes each output column using a 13-word directory that identifies which 16-bit vertical sectors have data.
- Alternates `RIGHTWARD` and `LEFTWARD` direction, changing how even/odd columns map to the two printhead columns and `headSeparation`.
- Dynamically grows `swipeBuf` if the compressed swipe exceeds the current allocation.
- Writes swipe headers containing vertical delta, byte size, horizontal extent, and encoded column data, then ejects with `fin()`.

Dependencies and notes:
- Uses `gsparams.h` for parameter handling.
- The driver is intentionally monochrome and cartridge-calibration-oriented.
- The buffer-growth macro jumps to an allocation cleanup label on failure.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlxm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm1.c

Implements the 1-bit `image1` monobit memory device and, on little-endian hosts, the `image1w` word-oriented variant.

Key behavior:
- Registers `mem_mono_device` with custom RGB mapping, mono copy, fill, strip-tile, strip-copy ROP, and get-bits support.
- Color mapping accounts for possible inverted palette data in `mdev->palette.data[0]`.
- `mem_mono_fill_rectangle` uses `bits_fill_rectangle`, unless `USE_COPY_ROP` is enabled for test coverage through ROP code.
- `mem_mono_copy_mono` is a performance-heavy implementation with architecture-dependent chunk fetch macros.
- Handles transparent, zero, and one color combinations via a `copy_modes` lookup table mapping to OR, STORE, AND, or fallback behavior.
- Optimizes single-chunk, one-source-to-two-destination chunks, aligned multi-chunk, and unaligned multi-chunk copies separately.
- `mem_mono_strip_tile_rectangle` reimplements monochrome halftone strip tiling for performance when colors are complements and tile shift is zero; otherwise delegates to `gx_default_strip_tile_rectangle`.
- Little-endian `mem_mono_word_device` wraps fills and copies with `mem_swap_byte_rect` and uses `mem_word_get_bits_rectangle`.

Dependencies and notes:
- Core dependency is `gdevmem.h` for scan-line, fit, chunk, mask, and swap helpers.
- The file contains a comment noting `mem_mono_map_color_rgb` is unusual because map-color procedures normally return an error code.
- The code is highly sensitive to bit order, chunk alignment, and host endian configuration.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm16.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm16.c

Implements the 16-bit `image16` true-color memory device using RGB565 layout.

Key behavior:
- Registers `mem_true16_device` with custom RGB map/unmap, mono copy, color copy, fill, and default strip-copy ROP.
- `mem_true16_map_rgb_color` packs color values as 5 red bits, 6 green bits, and 5 blue bits.
- `mem_true16_map_color_rgb` expands 5/6-bit components back into Ghostscript color values.
- Pixels are stored in big-endian byte order; little-endian hosts byte-swap the 16-bit color for memory writes.
- `mem_true16_fill_rectangle` optimizes single-pixel, repeated-byte colors, and wider nonuniform fills.
- `mem_true16_copy_mono` applies transparent or explicit zero/one colors pixel by pixel.
- `mem_true16_copy_color` delegates rectangular byte copying to `mem_copy_byte_rect`.

Dependencies and notes:
- Uses `mem_device("image16", 16, 0, ...)`.
- Unlike many neighboring files, it does not define a separate `image16w` word-oriented variant.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm2.c

Implements the 2-bit `image2` mapped-color memory device and little-endian `image2w` variant.

Key behavior:
- Registers `mem_mapped2_device` with mapped-color RGB map/unmap, copy, fill, and gray strip-copy ROP.
- Uses four precomputed 2-bit fill patterns for color values 0 through 3.
- `mem_mapped2_fill_rectangle` fills bit ranges with `bits_fill_rectangle`, scaling x/w by 2 bits per pixel.
- `mem_mapped2_copy_mono` handles opaque bitmaps, stencils, and reverse stencils using nibble/bit masks.
- `mem_mapped2_copy_color` temporarily doubles `dev->width` and reuses `mem_mono_device.copy_mono` over expanded bit coordinates.
- Little-endian `mem_mapped2_word_device` wraps fill/copy operations with `mem_swap_byte_rect` and uses `mem_word_get_bits_rectangle`.

Dependencies and notes:
- Relies on `mem_mapped_map_rgb_color` and `mem_mapped_map_color_rgb`, defined elsewhere in the memory-device layer.
- The temporary `dev->width` mutation is local and restored immediately after delegation.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm24.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm24.c

Implements the 24-bit RGB `image24` memory device and little-endian `image24w` variant.

Key behavior:
- Registers `mem_true24_device` with RGB map/unmap, mono/color copy, optimized fill, alpha copy, strip tiling, strip-copy ROP, and get-bits support.
- Stores pixels as three bytes per pixel, with `x_to_byte(x) = x * 3`.
- `mem_true24_fill_rectangle` has separate paths for wide fills, grayscale-byte fills, cached color fills, and narrow fills of width 1 through 4.
- Maintains a per-device 24-bit color cache (`mdev->color24`) with endian-specific packed word patterns.
- `mem_true24_copy_mono` optimizes the common stencil case where `zero` is transparent and `one` is a real color, processing full source bytes with unrolled bit checks.
- `mem_true24_copy_color` delegates to `mem_copy_byte_rect`.
- `mem_true24_copy_alpha` blends a source alpha map at depth 2 or 4 into existing RGB destination pixels.
- Little-endian `mem_true24_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- `mem_true24_strip_copy_rop` aliases `mem_gray8_rgb24_strip_copy_rop`.
- Optional `USE_MEMSET` and `USE_MEMCPY` paths are present but disabled.
- Debug statistics are compiled only under `DEBUG`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm24.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm32.c

Implements the 32-bit `image32` memory device and little-endian `image32w` variant.

Key behavior:
- Registers `mem_true32_device` as a 32-bit storage format with 24 color bits and 8 alpha/extra bits.
- Uses endian-aware `arrange_bytes` and `color_swap_bytes` to store 32-bit pixel words in the expected byte order.
- `mem_true32_fill_rectangle` optimizes widths 1 through 4, zero fills via `memset`, and wider repeated 32-bit stores.
- `mem_true32_copy_mono` has a fast stencil path for transparent `zero` and real `one`, unrolling full source bytes into up to eight destination pixels.
- The nontransparent-zero path handles explicit zero/one colors pixel by pixel.
- `mem_true32_copy_color` uses `mem_copy_byte_rect`.
- Little-endian `mem_true32_word_device` wraps color values with byte swapping and swaps copied color rectangles for word-oriented output.

Dependencies and notes:
- Uses `gx_default_map_rgb_color`, `gx_default_map_color_rgb`, and `gx_default_cmyk_map_cmyk_color`.
- The word variant’s `copy_color` copies raw bytes and then calls `mem_swap_byte_rect`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm4.c

Implements the 4-bit `image4` mapped-color memory device and little-endian `image4w` variant.

Key behavior:
- Registers `mem_mapped4_device` with mapped RGB map/unmap, copy, fill, and gray strip-copy ROP.
- Defines 16 precomputed fill patterns where each nibble repeats the color value.
- `mem_mapped4_fill_rectangle` fills bit ranges with `bits_fill_rectangle`, scaling x/w by 4 bits per pixel.
- `mem_mapped4_copy_mono` handles transparent-noop, masked, reverse-masked, and opaque cases.
- Opaque bitmap copy builds a four-entry table for all two-source-bit combinations and processes aligned destination nibbles in pairs.
- Masked copy toggles high/low nibble masks as it walks pixels.
- `mem_mapped4_copy_color` temporarily quadruples `dev->width` and delegates to monobit copy logic.
- Little-endian `mem_mapped4_word_device` wraps operations with `mem_swap_byte_rect`.

Dependencies and notes:
- Like `gdevm2.c`, this file reuses `mem_mono_device` or `mem_mono_word_device` for color bitmap copies by widening coordinate space.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm40.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm40.c

Implements the 40-bit `image40` true-color memory device and little-endian `image40w` variant.

Key behavior:
- Registers `mem_true40_device` with 5-byte pixels, RGB map/unmap, copy, fill, default alpha copy, and get-bits support.
- Unpacks 64-bit `gx_color_index` values into five bytes.
- Uses `mdev->color40` to cache endian-specific 32-bit word rotations for repeated 5-byte color patterns.
- `mem_true40_fill_rectangle` optimizes grayscale repeated-byte fills with `memset`, cached wide color fills, and narrow fills of width 1 through 4.
- `mem_true40_copy_mono` mirrors the 24-bit stencil structure but writes five bytes per destination pixel.
- `mem_true40_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true40_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- Uses `uint64_t` color extraction.
- The cache stores five rotated 32-bit words (`abcd`, `bcde`, `cdea`, `deab`, `eabc`) to make 5-byte pixels efficient despite unaligned word boundaries.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm40.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm48.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm48.c

Implements the 48-bit `image48` true-color memory device and little-endian `image48w` variant.

Key behavior:
- Registers `mem_true48_device` with 6-byte pixels, RGB map/unmap, copy, fill, default alpha copy, strip-copy ROP, and get-bits support.
- Unpacks `gx_color_index` into six component bytes.
- Maintains a three-word color cache for repeated 48-bit color patterns (`abcd`, `cdef`, `efab`) with endian-specific layouts.
- `mem_true48_fill_rectangle` handles repeated-byte grayscale fills, cached wide color fills, and narrow fills.
- Since two 6-byte pixels make three 32-bit words, the wide fill path writes two pixels per loop.
- `mem_true48_copy_mono` provides explicit-color and stencil paths.
- `mem_true48_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true48_word_device` swaps byte rectangles around all write paths.

Dependencies and notes:
- Similar to `gdevm40.c`, but its pixel size naturally groups as two pixels per 12-byte block.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm48.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm56.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm56.c

Implements the 56-bit `image56` true-color memory device and little-endian `image56w` variant.

Key behavior:
- Registers `mem_true56_device` with 7-byte pixels, RGB map/unmap, copy, fill, default alpha copy, and get-bits support.
- Unpacks `gx_color_index` into seven component bytes.
- Maintains a seven-word color cache for repeated 56-bit color patterns with endian-specific rotations.
- `mem_true56_fill_rectangle` optimizes repeated-byte grayscale fills, wide cached fills, and narrow widths.
- The wide fill path writes four 7-byte pixels as seven 32-bit words.
- `mem_true56_copy_mono` has explicit zero/one and stencil-only paths, writing seven bytes per selected pixel.
- `mem_true56_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true56_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- Debug statistic hooks match the neighboring high-bit-depth files.
- Uses `uint64_t` shifts for the high three component bytes.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm56.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm64.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm64.c

Implements the 64-bit `image64` true-color memory device and little-endian `image64w` variant.

Key behavior:
- Registers `mem_true64_device` with 8-byte pixels, RGB map/unmap, copy, fill, default alpha copy, and get-bits support.
- Uses two 32-bit words per pixel; `PIXEL_SIZE` is defined as `2` in 32-bit-word units, while byte offset is `x << 3`.
- `declare_unpack_color` produces two 32-bit words, with explicit byte rearrangement on little-endian hosts.
- `mem_true64_fill_rectangle` writes repeated two-word pixels, with paths for wide and narrow fills.
- `mem_true64_copy_mono` handles explicit zero/one colors and the common transparent-zero stencil case.
- `mem_true64_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true64_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- The standard device’s byte offsets are correct through `x_to_byte(x) = x << 3`.
- In the word variant, `mem64_word_copy_color` uses `PIXEL_SIZE` in byte-pointer arithmetic even though `PIXEL_SIZE` is 32-bit-word count in this file; this is a notable sharp edge if maintaining this code.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm8.c

Implements the 8-bit `image8` mapped-color memory device and little-endian `image8w` variant.

Key behavior:
- Registers `mem_mapped8_device` with mapped RGB map/unmap, copy, fill, and gray/RGB24 strip-copy ROP.
- `mem_mapped8_fill_rectangle` uses `bytes_fill_rectangle` directly because each pixel is one byte.
- `mem_mapped8_copy_mono` dispatches to three helper routines:
  - `mapped8_copy01` for opaque zero/one coloring.
  - `mapped8_copyN1` for stencil writes where zero is transparent.
  - `mapped8_copy0N` for reverse stencil writes where one is transparent.
- The helper split exists because of bcc32 compiler limitations.
- `mem_mapped8_copy_color` copies source bytes directly with `mem_copy_byte_rect`.
- Little-endian `mem_mapped8_word_device` wraps fill, mono copy, and color copy with `mem_swap_byte_rect`.

Dependencies and notes:
- `mem_gray8_strip_copy_rop` aliases `mem_gray8_rgb24_strip_copy_rop`.
- This is the simplest packed mapped-color memory device because no bit/nibble packing is needed.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.c

Implements the legacy Classic MacOS `macos` Ghostscript PICT output device. The file itself notes this device is superseded by the newer `gsapi_*` interface and DISPLAY device.

Key behavior:
- Defines `gs_mac_procs`, wiring core device operations to Mac-specific open, close, sync, output-page, fill, copy-mono, draw-line, copy-alpha, params, and xfont hooks.
- Defines public `gs_macos_device` with default 72 dpi letter dimensions, PICT handle state, output filename/file state, xfont flags, and font cache state.
- `mac_open` allocates a `PicHandle`, writes a PICT header, fills in page/media dimensions and resolutions, and reports device-open callback events through `pgsdll_callback`.
- `mac_get_initial_matrix` maps Ghostscript coordinates into Mac-style page coordinates with negative y scale.
- `mac_sync_output` writes an end-picture opcode in place and sends a sync callback.
- `mac_output_page` optionally saves a PICT file, sends page callback, and finishes the Ghostscript output page.
- `mac_save_pict` writes the 512-byte PICT file header followed by the generated PICT data.
- `mac_close` unlocks/resizes/disposes the PICT handle depending on output mode and sends the close callback.
- Drawing operations serialize PICT opcodes:
  - `mac_fill_rectangle` writes RGB foreground and `fillRect`.
  - `mac_draw_line` writes RGB foreground and line opcode.
  - `mac_copy_mono` writes a bitmap/PackBits rectangle with foreground/background colors and QuickDraw transfer mode.
  - `mac_copy_alpha` simulates alpha on white background by building a color table that shifts saturation/value toward white.
- `mac_convert_rgb_hsv` and `mac_convert_hsv_rgb` support alpha color-table generation.
- `mac_set_colordepth` supports depths 1, 4, 7, 8, and 24, updating `color_info` and RGB mapping procs.
- `mac_put_params` handles `UseExternalFonts`, `BitsPerPixel`, and `OutputFile`, respecting `LockSafetyParams`.
- `mac_get_params` publishes the same parameters.
- Exports `gsdll_get_pict` to return the generated `PicHandle`.

Dependencies and notes:
- Depends on `gdevmac.h`, `gdevmacpictop.h`, QuickDraw/Classic Mac APIs, and Ghostscript DLL callbacks.
- `copy_color` and strip tiling are present only in disabled experimental `#if 0` blocks.
- PICT memory is managed through `CheckMem` and `ResetPage` macros from `gdevmac.h`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.h

Header for the legacy Classic MacOS PICT device and xfont integration.

Key contents:
- Includes Classic MacOS headers: `Fonts.h`, `FixMath.h`, `Resources.h`, plus Ghostscript device, xfont, struct, DLL, and utility headers.
- Defines default page/device dimensions and dpi values for the `macos` device.
- Defines `gx_device_macos`, extending Ghostscript device/printer-style state with:
  - Output filename and `FILE *`.
  - PICT handle and current PICT pointer.
  - `outputPage` reset state.
  - `useXFonts`.
  - Last-used font face/size/family and a list of used font family IDs.
- Declares all Mac device procs: open, matrix, sync, output, params, close, fill, strip-tile, mono/color copy, line, alpha, and xfont procs.
- Defines `mac_xfont`, carrying Ghostscript xfont common state plus Mac font name, family, face, size, encoding, and metrics.
- Defines `CheckMem` to grow the PICT handle while preserving `currPicPos`.
- Defines `ResetPage` to reset PICT drawing after page output and clear font caches.
- Defines RGB/HSV helper structs and private helper prototypes.
- Exports `gsdll_get_pict` under `#pragma export`.

Dependencies and notes:
- `gdevmac.c` and `gdevmacxf.c` share this header.
- The header assumes Classic/Carbon Mac type names and resource APIs are available.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacpictop.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacpictop.h

Macro library for serializing Classic MacOS QuickDraw PICT opcodes and data structures into a memory buffer.

Key contents:
- Low-level write macros for bytes, 16-bit ints, 32-bit longs, fill bytes, and opcodes.
- QuickDraw structure writers for points, rectangles, regions, patterns, RGB colors, color specs, color tables, and PixMaps.
- `PICTWriteDataPackBits` writes raw bitmap data for small rasters or calls QuickDraw `PackBits` per row for larger rasters, including per-row byte counts and even-byte padding.
- Text writer macros handle Pascal strings and padding.
- Defines many PICT opcode macros:
  - Clipping, patterns, text state, colors, highlight/op colors.
  - Lines and text drawing.
  - Font names.
  - Rectangles, rounded rectangles, ovals, arcs, and same-shape variants.
  - BitsRect and PackBitsRect bitmap/pixmap forms.
  - End-picture opcodes.
- Provides Ghostscript-to-PICT color helpers:
  - `GSSetStdCol`
  - `GSSetFgCol`
  - `GSSetBkCol`

Dependencies and notes:
- Includes `<QDOffscreen.h>`.
- This is macro-only code and mutates the supplied pointer argument extensively.
- Several macros depend on ambient variable names, notably `raster` inside `PICTWriteDataPackBits`; callers must match those assumptions.
- Some rarely used macros appear fragile, for example `PICTWriteRegion` parameter naming and `PICT_PnSize` argument forwarding.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacpictop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacttf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacttf.h

Defines small TrueType font table structs used by the Mac xfont implementation.

Key contents:
- `TTFontDirComponent`: TrueType table directory entry with tag, checksum, offset, and length.
- `TTFontDir`: TrueType font directory header with version, table count, search metadata, and a flexible first component.
- `TTF_FONT_NAMING_TABLE` tag defined as `'name'`.
- `TTFontNamingTable`: initial fields for reading a TrueType naming table record, including platform, language, name ID, string length, and offset.

Dependencies and notes:
- Uses Mac integer types such as `UInt32` and `UInt16`.
- Only supports the limited table access needed by `mac_get_font_encoding` in `gdevmacxf.c`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacttf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacxf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacxf.c

Implements Classic/Carbon MacOS external font (`xfont`) support for the `macos` device.

Key behavior:
- Defines encoding conversion tables for Standard-to-Mac and ISO-Latin-1-to-Mac.
- Declares but leaves `gs_map_mac_to_std` and `gs_map_mac_to_iso` as zero-initialized arrays.
- Defines `mac_xfont_procs` with lookup, char-to-xglyph, metrics, render, and release functions.
- Registers `mac_xfont` with Ghostscript GC metadata via `gs_private_st_dev_ptrs1`.
- `mac_get_xfont_procs` returns the static xfont procedure table.
- `mac_lookup_font`:
  - Requires `UseExternalFonts` to be enabled.
  - Accepts only MacRoman, ISO Latin-1, or Standard encodings.
  - Rejects tiny fonts and transformed matrices.
  - Allocates `mac_xfont`, finds a Mac font family/style, gets font name, size, encoding, and metrics.
  - Saves and restores current GrafPort text state while measuring.
- `mac_char_xglyph` maps input character codes through the encoding tables depending on the native font encoding.
- `mac_char_metrics` returns broad metrics from `FMetricRec`, with no per-glyph width lookup.
- `mac_render_char` emits PICT font-name/font/size/face opcodes when needed, then writes a `LongText` opcode for the single character.
- `mac_release` frees the xfont object.
- `mac_find_font_family` tries exact names, dash-to-space names, and then extracts style tokens like Italic, Bold, Narrow, and Condensed.
- `mac_get_font_encoding` loads the font resource, walks the TrueType directory, finds the naming table, and maps platform IDs to MacRoman or ISO Latin-1.
- `mac_get_font_resource` uses `FMSwapFont` and `GetResInfo`.
- Provides compatibility wrappers for older Font Manager APIs when `USE_RECOMMENDED_CARBON_FONTMANAGER_CALLS` is disabled.

Dependencies and notes:
- Depends on `gdevmac.h`, `gdevmacttf.h`, Classic/Carbon Font Manager APIs, QuickDraw GrafPort state, and Ghostscript xfont types.
- Some failure paths in `mac_lookup_font` return `NULL` after allocation without freeing `macxf`.
- Reverse encoding maps are empty, which limits MacRoman-to-ISO/Standard conversions.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.c

Implements shared media selection support for printer drivers.

Key behavior:
- Defines a static table of known media sizes in meters, including ISO A/B series, architectural sizes, US paper sizes, and envelopes.
- Each media table entry includes a priority of `1 / (width * height)`, so smaller matching media have higher priority.
- `select_medium(gx_device_printer *pdev, const char **available, int default_index)`:
  - Converts current device width and height from pixels/dpi to meters.
  - Iterates through the caller-provided null-terminated media-name list.
  - Finds matching known media whose width and height exceed the image dimensions plus a 0.1 cm tolerance.
  - Chooses the smallest suitable available medium by priority.
  - Falls back to `default_index` if no medium matches.

Dependencies and notes:
- Included by printer drivers such as `gdevl31s.c`.
- The function is orientation-sensitive: it compares width-to-width and height-to-height without trying rotated media.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.c -->