# Group Research: group_1542_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevmeds_h_sources__02a963055baa

Scope checked against `Docs/research_subset_a`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.h

Small interface header for Ghostscript medium-selection support.

- Defines include guard `gdevmeds_INCLUDED`.
- Includes `gdevprn.h`, so the interface is printer-device-specific.
- Declares `select_medium(gx_device_printer *pdev, const char **available, int default_index)`.
- No implementation, data structures, or macros beyond the public prototype.
- Integration role: lets printer drivers ask shared `gdevmeds.c` logic to choose a medium from an available-medium list with a default fallback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.c

Generic Ghostscript bitmap-backed memory device implementation.

- Defines GC descriptors and relocation for `gx_device_memory`, including owned/foreign bitmap storage, line-pointer tables, and palette strings.
- Provides standard monobit palettes: black-white and white-black variants for inverted 1-bit memory devices.
- Maps bit depths to memory-device prototypes via `gdev_mem_device_for_bits` and word-oriented prototypes via `gdev_mem_word_device_for_bits`; supported depths include 1, 2, 4, 8, 16, 24, 32, 40, 48, 56, and 64.
- Uses `draw_thin_line == mem_draw_thin_line` as the marker for `gs_device_is_memory`.
- `gs_make_mem_device` and `gs_make_mem_mono_device` initialize memory devices, optionally forwarding color mapping to a target device and handling 1-bit inversion.
- Size helpers compute bitmap storage, line pointer storage, total data size, and maximum height, including a special PDF 1.4 transparency estimate path.
- `mem_open` rejects planar devices and delegates to `gdev_mem_open_scan_lines`; scan-line setup supports contiguous bitmap-plus-pointer storage or separately allocated line pointers.
- `mem_get_bits_rectangle` returns native chunky pixels by pointer when possible or copies through Ghostscript get-bits helpers.
- Little-endian word-oriented devices use `mem_swap_byte_rect` and `mem_word_get_bits_rectangle` to swap word byte order around get-bits calls.
- Palette-mapped devices implement nearest-palette RGB/gray lookup in `mem_mapped_map_rgb_color` and decode indices in `mem_mapped_map_color_rgb`.
- Risk notes: relocation logic adjusts line pointers relative to moved base storage; incorrect ownership flags would corrupt GC relocation/free behavior. `gdev_mem_max_height` is exact only outside the PDF transparency estimate path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.h

Private definitions and device-construction macros for Ghostscript memory devices.

- Documents the contiguous bitmap representation: scan lines in PostScript-like order, padded to `bitmap_align_mod`, plus a line-pointer table for faster row access.
- Defines scan-line setup/access macros such as `declare_scan_ptr`, `setup_rect`, and `SETUP_RECT_VARS`.
- Declares generic memory-device procs: open, close, initial matrix, get-bits rectangle, word get-bits rectangle, mapped color encode/decode, default RasterOp, and `mem_draw_thin_line`.
- Provides `mem_full_alpha_device`, `mem_full_device`, and `mem_device` macros for generating full `gx_device_memory` descriptors and procedure tables.
- Defines max-value macros for supported RGB/gray depths, working around compiler shift-expression issues.
- Declares byte-rectangle utilities: `mem_swap_byte_rect` and `mem_copy_byte_rect`.
- Exposes memory-device prototypes for mono, mapped 2/4/8-bit, true-color 16 through 64-bit, planar, and word-oriented variants.
- Declares shared RasterOp entry points for mono, gray, and gray8/rgb24 memory devices.
- Exposes the two standard 1-bit palettes used by `gdevmem.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.c

MGR bitmap output driver for Ghostscript printer devices.

- Defines `gx_device_mgr`, extending `gx_device_printer` with `mgr_depth`.
- Registers devices: `mgrmono`, `mgrgray2`, `mgrgray4`, `mgrgray8`, `mgr4`, and `mgr8`.
- Uses standard printer open/output/close procs, with custom print-page functions for monochrome, gray, and color MGR output.
- `mgr_begin_page` writes an MGR bitmap header using `B_PUTHDR8`, allocates a row buffer, and initializes a cursor.
- `mgr_print_page` outputs 1-bit rows padded to byte boundaries.
- `mgrN_print_page` repacks Ghostscript 8-bit gray scan lines into 2-, 4-, or 8-bit MGR gray formats, builds gray CLUT entries, and byte-swaps CLUT words on little-endian hosts.
- `cmgrN_print_page` handles 4-bit PC color and 8-bit MGR color; the 8-bit path remaps a 7x7x4 cube plus reserved colors into an MGR CLUT.
- `mgr_8bit_map_rgb_color` and `mgr_8bit_map_color_rgb` implement the fixed MGR 8-bit color mapping with extra gray shades.
- Risk notes: page routines allocate temporary buffers and return immediately on some write errors, so cleanup is not always symmetrical. Static CLUT and mapping tables make the driver non-reentrant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.h

Shared MGR device definitions.

- Declares MGR 8-bit color mapping procs used by `gdevmgr.c`.
- Defines MGR bitmap header encoding macro `B_PUTHDR8` and `struct b_header`.
- Defines `struct nclut` for color lookup table entries.
- Provides constants for MGR LUT types, RGB channels, and 16-entry palette ramps.
- Contains static `mgrlut[LUT][RGB][LUTENTRIES]` with built-in black/white, gray, biased gray, VGA, BCT, and user palettes.
- Integration role: shared header for MGR output format structure and palette definitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmiff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmiff.c

ImageMagick MIFF direct-color output driver.

- Defines the `miff24` printer device at 72 dpi, 24-bit RGB, using standard RGB map/decode procs.
- `miff24_print_page` writes a simple MIFF header: `id=ImageMagick`, `DirectClass`, columns, rows, and run-length compression.
- Allocates one raster line and reads rows with `gdev_prn_get_bits`.
- Encodes each run as RGB bytes followed by a repeat count byte, with a maximum run count of 255.
- Frees the line buffer after processing and returns the last Ghostscript row-read status.
- Risk notes: file write errors from `putc`/`fputs` are not checked; only source scan-line errors affect the returned code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmiff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.c

Any-depth planar memory-device implementation.

- Public entry point `gdev_mem_set_planar` validates plane count, per-plane depth, shift overlap, supported memory depth, and total depth before replacing chunky drawing procs with planar-aware ones.
- `mem_planar_open` rejects non-planar devices and uses normal memory scan-line allocation.
- Drawing operations temporarily patch `gx_device_memory` fields to expose one plane at a time to the appropriate standard memory-device prototype.
- Implements planar `fill_rectangle`, `copy_mono`, `copy_color`, `strip_tile_rectangle`, and `get_bits_rectangle`.
- `copy_color` extracts each plane from chunky input into a fixed stack buffer, chunking wide transfers as needed, then calls the plane-depth copy routine.
- `strip_tile_rectangle` can split monochrome colored tiles by plane but punts colored tiles to the default implementation.
- `planar_to_chunky` repacks planar storage back into native chunky pixels, with optimized direct byte-per-component cases for 3- and 4-plane 8-bit components.
- `mem_planar_get_bits_rectangle` can return a single requested plane directly, otherwise falls back to chunky format and may copy through an intermediate buffer for unsupported get-bits options.
- Risk notes: procedure patching relies on careful save/restore of depth, base, raster, line pointers, and `copy_mono`; errors in intermediate routines could leave device state inconsistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.h

Public interface for planar memory devices.

- Documents planar storage: bits are stored by planes, least-significant color-index plane first.
- Each plane may have a distinct supported memory-device depth, currently capped at 16 bits per plane.
- Total plane depth must fit within `gx_color_index` and within the memory device color depth.
- Planes are stored contiguously as separate device images, with one line-pointer table per plane.
- Declares `gdev_mem_set_planar(gx_device_memory *mdev, int num_planes, const gx_render_plane_t *planes)`.
- Must be called after `gs_make_mem_device` and before opening the device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr1.c

RasterOp implementation for monobit memory devices.

- Main entry point is `mem_mono_strip_copy_rop`.
- Converts Ghostscript logical operations to effective 1-bit ROP3 with transparency handling through `gs_transparent_rop`.
- Lazily initializes the mono palette if needed, then adjusts ROP semantics when device bit polarity is inverted.
- Simplifies operations based on source and texture palettes, including known-0, known-1, inverted-source, and inverted-texture cases.
- Fast-paths constant fills, no-ops, copy-mono-compatible source operations, and strip-tile-compatible texture operations.
- General path walks destination rows and tiled texture spans, fetches skewed source/texture bytes, applies `rop_proc_table[rop]`, and masks edge bytes.
- Includes debug tracing/dump hooks under `DEBUG`.
- Risk notes: this is bit-level code with multiple skew/mask calculations; correctness depends on prior clipping via `fit_fill`/`fit_copy` and valid texture repetition metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr2n.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr2n.c

RasterOp adapter for 2- and 4-bit gray memory devices.

- Main entry point is `mem_gray_strip_copy_rop`.
- Attempts to fake 2-/4-bit gray ROPs by expanding pixel coordinates into equivalent 1-bit spans and reusing `mem_mono_strip_copy_rop`.
- Falls back to `mem_default_strip_copy_rop` for color devices, transparency, unsupported source palettes, or incompatible texture colors.
- Adjusts source colors, texture geometry, phase, width, and device width by `log2_depth`.
- Fabricates a tiny texture for constant non-black/non-white texture colors.
- Temporarily replaces `fill_rectangle`, `copy_mono`, and `strip_tile_rectangle` with stub routines that force fallback if mono ROP special cases are used.
- Restores device procedures and width after the mono call.
- Risk notes: temporary mutation of `dev->width` and procedure slots is fragile; the stub routines intentionally return errors to trigger the slow general path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr2n.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr8n.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr8n.c

RasterOp implementation for 8-bit gray and 24-bit RGB memory devices.

- Main entry point is `mem_gray8_rgb24_strip_copy_rop`.
- Handles 8-bit gray and 24-bit RGB destinations; comments note 16- and 32-bit cases fall back to the default implementation elsewhere.
- Detects constant source and texture, simplifies ROPs when constants equal device black or white, and records transparency sentinel values.
- For non-gray 8-bit devices, only simple cases are handled directly; complex cases fall back to `mem_default_strip_copy_rop`.
- Clips either as a copy or fill depending on whether source is constant.
- Uses macro-generated loops for 8-bit and 24-bit pixels, with cases split across constant/data source and constant/data texture.
- Supports 1-bit source/texture palettes and multi-bit source/texture data, including repeated strip textures with phase/shift.
- Risk notes: nested macro control flow is dense; transparency is implemented by skipping destination writes when source or texture equals the transparent sentinel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr8n.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrop.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrop.h

Shared RasterOp definitions for memory-device implementations.

- Declares `gs_transparent_rop` for deriving an effective 1-bit ROP with transparency.
- Under `DEBUG`, declares `trace_copy_rop` for tracing copy/strip-copy ROP calls.
- Defines forward declarations for `gx_device_color` and `gx_device_rop_texture`.
- `gx_device_rop_texture` is a forwarding device containing a logical operation and a texture color.
- Provides the structure descriptor macro `private_st_device_rop_texture`.
- Declares allocation and initialization helpers: `gx_alloc_rop_texture_device` and `gx_make_rop_texture_device`.
- Role: supports using image data as RasterOp source while treating a specified `gx_device_color` as texture.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.c

Experimental run-length encoded memory-device wrapper.

- File explicitly warns that the code has not been tested.
- Represents each scan line as a doubly linked list of runs stored inside the memory device scan-line storage.
- Uses dummy start/end runs, bounded run indices, and bounded run lengths; caps the number of runs per line to avoid stack expansion costs and low compression value.
- `gdev_run_from_mem` copies a memory device into `gx_device_run`, checks whether enough run slots fit per scan line, initializes uninitialized lines to device white, and replaces drawing/get-bits procs.
- Non-fill operations standardize affected lines to normal bitmap form, then call the saved original memory-device procedure.
- `run_expand` converts one run-encoded line to bitmap form using saved `fill_rectangle`.
- `run_standardize` manages the range of lines already converted to standard form.
- `run_line_initialize` builds initial runs and a free list for a line that is first written with a non-white color.
- `run_fill_interval` performs the core run-list edit: finds affected runs, splits preserved prefixes/suffixes, deletes overwritten runs, and inserts/merges new runs.
- `run_fill_rectangle` keeps all-white uninitialized regions cheap, delegates overlapping standardized regions, and converts a line to standard form if it runs out of run slots.
- Risk notes: untested, mutates scan-line storage between two representations, and uses stack arrays sized by `MAX_RUNS`; safest interpretation is an experimental optimization layer for fill-heavy pages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.h

Definition of the run-length encoded memory-device wrapper.

- Includes `gxdevmem.h` and defines `gx_device_run`.
- `gx_device_run` embeds `gx_device_memory md` as its first field for device compatibility.
- Tracks run capacity per line, an uninitialized line range, and a standard/uncompressed line range.
- Stores saved memory-device procs for copy mono/color, fill rectangle, copy alpha, strip tile, strip copy ROP, and get-bits rectangle.
- Declares `gdev_run_from_mem(gx_device_run *rdev, gx_device_memory *mdev)`.
- Intended behavior: use RLE storage when useful and fall back to standard bitmap representation as needed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmrun.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.c

Shared Microsoft Windows 3.x display-driver support.

- `win_open` determines output size from resolution defaults, probes desktop bit depth, normalizes to 1/4/8/16/24 bpp, sets color info, and creates palettes for indexed modes.
- `win_sync_output` and `win_output_page` notify the Ghostscript DLL callback with sync/page events.
- `win_close` frees palette resources and the 8-bit mapped-color bitset.
- `win_map_rgb_color` encodes colors for 24-bit BGR, 16-bit 5:6:5, 15-bit 5:5:5, 8-bit palette mode, 4-bit PC color, or default monochrome mapping.
- 8-bit mode starts with a 64-color cube and dynamically appends up to 220 palette entries, using `mapped_color_flags` to avoid unnecessary palette scans.
- `win_map_color_rgb` decodes color indices according to the active bpp mode.
- `win_put_params` supports changing `BitsPerPixel` before open, suppresses default close/reopen during size/resolution changes, and asks the concrete implementation to reallocate its bitmap when needed.
- `win_makepalette` creates palettes for 64-, 16-, and 2-color modes.
- `win_set_bits_per_pixel` updates `color_info`, allocates or frees 8-bit mapped-color flags, installs encode/decode procs, and preserves anti-alias settings.
- Risk notes: comments admit an error-recovery path after bitmap reallocation failure is “WRONG”; code is legacy Windows API and resource-management heavy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.h

Shared declarations and common structure fields for Microsoft Windows 3.x Ghostscript drivers.

- Pulls in Ghostscript core headers plus Windows compatibility headers and shell API.
- Forward-declares `gx_device_win`.
- Declares shared utility functions: `win_makepalette`, `win_nomemory`, and `win_update`.
- Declares common device procs for open, sync, output, close, RGB mapping, params, xfont, and alpha bits.
- Defines callback-style procedure typedef macros for clipboard, repaint, bitmap allocation, and bitmap freeing.
- `gx_device_win_common` adds bpp, palette state, mapped-color flags, implementation hooks, and Windows palette handles.
- Defines `gx_device_win_s` as `gx_device_common` plus Windows common fields.
- Provides initial size/resolution constants and Windows ROP constants used by rendering and xfont code.
- Defines `win_color_value` for compressing Ghostscript color values into 8-bit Windows palette components.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmswn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmsxf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmsxf.c

Microsoft Windows external-font implementation for Ghostscript.

- Exposes `win_get_xfont_procs`, returning lookup, glyph mapping, metrics, render, and release callbacks.
- Defines `win_xfont`, holding Ghostscript xfont state, Windows `LOGFONT`, `TEXTMETRIC`, `HFONT`, owning Windows device, y inversion, and y offset.
- Contains Standard/Symbol/ISO-to-OEM mapping tables for Windows character sets.
- Maps common PostScript font families to Windows face names: Courier, Helvetica/Arial/Helv, and Times/Times New Roman/Tms Rmn.
- `win_lookup_font` accepts only simple non-skewed, uniform-scale matrices and small sizes, builds `LOGFONT`, matches logical fonts against Windows faces, records metrics, and allocates a `win_xfont`.
- `win_char_xglyph` maps Ghostscript characters to Windows glyph codes based on encoding and selected font charset.
- `win_char_metrics` selects the font into a desktop DC and returns width plus a bbox derived from ascent/descent and y inversion.
- `win_render_char` renders required glyphs into a temporary 1-bit Windows bitmap, extracts bits, and copies them to the target device with `copy_mono`; optional direct-window rendering is disabled.
- `win_release` deletes the Windows font and frees the Ghostscript xfont object.
- Risk notes: uses desktop DCs because the driver has no owned window; rendering uses legacy `GetBitmapBits` and temporary GDI objects that must be carefully released.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmsxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevn533.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevn533.c

Sony NWP-533 laser printer driver.

- User-contributed driver targeting NEWS printer interfaces via `<newsiop/lbp.h>` and printer ioctls.
- Defines the `nwp533` 1-bit printer device using paper constants from the platform header, defaulting to A4.
- `nwp533_open` defaults the output file to `/dev/lbp` when none is supplied.
- `analyze_error` resets and queries printer status, waits for recoverable conditions such as no cartridge, no paper, jam, door open, or test printing, and aborts for severe hardware/toner conditions.
- `nwp533_print_page` stops the printer, seeks to start, writes each padded scan line to the printer file, then starts printing via ioctl.
- `nwp533_close` stops the printer before normal printer-device close.
- Risk notes: platform-specific ioctl paths, blocking sleep/retry loop, typo-laden diagnostics, and several error returns before freeing the scan-line buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevn533.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevnfwd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevnfwd.c

Null-device and forwarding-device implementation.

- Provides target management for `gx_device_forward`, including reference-count assignment and finalization that decrements the target.
- `gx_device_forward_fill_in_procs` installs forwarding defaults for most higher-level device procedures while leaving open/close and low-level drawing operations to concrete devices.
- `gx_device_forward_color_procs` makes a forwarding device delegate color mapping and encode/decode to its target.
- Implements many `gx_forward_*` wrappers for close, matrix, sync, output page, color mapping, drawing, path fills/strokes, images, get-bits, text, hardware params, patterns, and color-space hooks.
- Fallback behavior varies: some wrappers call Ghostscript defaults when no target exists, while low-level mandatory operations may return fatal/rangecheck errors.
- Color mapping wrappers return forwarding color-map procs so the target device pointer is used correctly inside target mapping functions.
- `gx_forward_decode_color` clears component values if no target exists.
- Defines `gs_null_device` and `gs_nullpage_device`; both discard rendering operations, with `nullpage` behaving as a page device.
- Null procs return success for fills, copies, paths, trapezoids, triangles, thin lines, and strip-copy ROP; `null_put_params` prevents non-page null devices from keeping a reset size.
- Risk notes: `gx_forward_copy_alpha` delegates to `copy_mono` with alpha parameters, reflecting older Ghostscript proc compatibility assumptions; forwarding devices rely on target proc tables being correctly initialized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevnfwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevo182.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevo182.c

Okidata Microline 182 dot-matrix printer driver.

- Defines `oki182`, a 1-bit printer device defaulting to 8x11 inches at 72 dpi.
- Supports 72x72 and 144x144 modes, with comments describing required printer DIP switch setup and 8-bit graphics mode assumptions.
- `oki_transpose` converts 7 scan lines into vertical 7-bit column bytes with the high bit set to avoid command-byte confusion.
- `oki_compress` trims trailing blank graphics bytes and converts long leading blank runs into spaces; high-resolution mode doubles columns per space.
- `oki_print_page` initializes printer mode, skips blank rows using fine line feed commands, gathers 7 or 14 scan lines, transposes them, compresses output, and emits printer command/data sequences.
- High-resolution mode splits even/odd scan lines into two graphics passes with a one-bit line feed between them.
- Always emits a form feed and flushes before freeing buffers.
- Risk notes: printer command protocol is tightly coupled to hardware behavior; write calls mostly ignore short-write/error status.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevo182.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevokii.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevokii.c

Okidata IBM-compatible 9-pin dot-matrix printer driver.

- Defines `okiibm`, a 1-bit printer device with configurable compile-time defaults for X dpi 60/120/240 and Y dpi 72/144.
- Documents Okidata’s unusual 1/216-inch feed scaling to 1/144-inch physical movement and tracks this with `y_step`.
- `okiibm_print_page1` handles the main rendering loop: skips blank scan lines, emits vertical feed commands, copies 8 or 16 source lines, optionally shuffles high-resolution lines, transposes 8x8 blocks, trims trailing zero columns, and outputs graphics runs.
- Uses `gdev_prn_transpose_8x8` to convert row-major raster data into printer column format.
- `okiibm_output_run` emits ESC graphics commands and supports all columns, even columns, or odd columns for high horizontal resolution passes.
- `okiibm_print_page` builds init/end command strings and enables unidirectional printing for higher resolutions.
- Risk notes: vertical positioning depends on the printer starting in a power-on state; output assumes valid X dpi table indexing through `x_dpi / 60`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevokii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevos2p.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevos2p.c

OS/2 Presentation Manager printer device.

- Defines `os2prn`, a printer device intended for Ghostscript as a DLL loaded by a PM application, not text-mode Ghostscript.
- Device state includes OS/2 anchor block, printer DC, presentation spaces, queue name/list, clipping box, and memory DC/PS.
- `os2prn_open` verifies PM process type, discovers printer queues, selects queue from `OS2QUEUE` or filename/default queue, opens a queued printer DC, reads printer resolution and hardcopy caps, sets Ghostscript margins/clipbox, chooses bpp, creates memory DC/PS, starts a print document, and opens a scratch printer file for Ghostscript’s printer framework.
- `os2prn_close` ends the document, destroys presentation spaces/DCs, closes the printer device, and unlinks the scratch file.
- `os2prn_get_params` and `os2prn_put_params` expose `OS2QUEUE` and pre-open `BitsPerPixel`.
- `os2prn_print_page` builds OS/2 `BITMAPINFOHEADER2`/palette data, slices the page into chunks bounded by 64K-ish memory limits, copies Ghostscript scan lines into a DIB buffer, draws bits into a memory bitmap, then bit-blits clipped slices to the printer PS.
- Color mapping supports 24-bit RGB packed as OS/2-expected byte order and black/white fallback; `os2prn_set_bpp` installs color-info and proc table changes while preserving anti-alias data.
- Queue helpers enumerate and free OS/2 print queues via `SplEnumQueue`.
- Risk notes: several OS/2 resource acquisition failures return without unwinding earlier resources; this is legacy platform code with device-context lifetime and clipping correctness as the main maintenance hazards.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevos2p.c -->