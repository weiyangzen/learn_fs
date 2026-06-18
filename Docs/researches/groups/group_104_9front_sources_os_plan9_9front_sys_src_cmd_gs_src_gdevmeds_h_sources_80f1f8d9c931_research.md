# Group Research: group_104_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevmeds_h_sources_80f1f8d9c931

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.h

Small Ghostscript printer-device interface header for medium selection support.

It includes `gdevprn.h` and exposes one function:

- `select_medium(gx_device_printer *pdev, const char **available, int default_index)`

The function is implemented elsewhere and is meant to choose an output medium for a `gx_device_printer` from a null-terminated or otherwise externally defined list of available media, with a default index fallback.

This file has no filesystem or OS kernel logic. Within the 9front source tree it belongs to the bundled Ghostscript command sources and participates in printer/output-device configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.c

Core implementation of Ghostscript’s generic in-memory bitmap device.

The file defines the GC structure descriptor for `gx_device_memory`, relocation/enumeration of owned bitmap storage, standard mono palettes, memory-device prototype lookup by bit depth, and device construction helpers. It supports chunky memory devices for 1, 2, 4, 8, 16, 24, 32, 40, 48, 56, and 64 bpp, plus word-oriented variants on little-endian targets.

Important routines:

- `gdev_mem_device_for_bits` and `gdev_mem_word_device_for_bits` choose device prototypes by depth.
- `gs_device_is_memory` detects memory devices by the distinguished `draw_thin_line` proc.
- `gs_make_mem_device` and `gs_make_mem_mono_device` initialize memory devices and optional forwarding target behavior.
- `gdev_mem_bits_size`, `gdev_mem_line_ptrs_size`, `gdev_mem_data_size`, and `gdev_mem_max_height` calculate bitmap and scan-line table storage.
- `mem_open`, `gdev_mem_open_scan_lines`, and `gdev_mem_set_line_ptrs` allocate or bind storage and set scan-line pointers.
- `mem_get_bits_rectangle` exports rectangular bitmap data through Ghostscript get-bits options.
- `mem_swap_byte_rect` and `mem_word_get_bits_rectangle` handle little-endian word-oriented export.
- `mem_mapped_map_rgb_color` and `mem_mapped_map_color_rgb` implement palette lookup for mapped color devices.

Risk notes: the code relies heavily on device invariants around `base`, `line_ptrs`, ownership flags, raster alignment, and plane count. Relocation logic mutates line pointers relative to relocated bitmap storage. Color palette matching uses simple absolute RGB component difference, not perceptual distance.

No filesystem logic is present; this is rendering-device memory management inside Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.h

Private header for Ghostscript memory devices.

It documents the memory-device representation: contiguous scan lines padded to `bitmap_align_mod`, plus a line pointer table for faster access. It also explains historical 16-bit PC storage constraints and why bitmap contents must be read in pieces.

Major contents:

- Scan-line access macros such as `declare_scan_ptr`, `setup_rect`, and `SETUP_RECT_VARS`.
- Declarations for common memory-device procedures: `mem_open`, `mem_close`, `mem_get_bits_rectangle`, `mem_word_get_bits_rectangle`, `mem_draw_thin_line`, mapped color procs, and default RasterOp support.
- Descriptor-building macros: `mem_full_alpha_device`, `mem_full_device`, and `mem_device`.
- Utility declarations such as `mem_swap_byte_rect` and `mem_copy_byte_rect`.
- External device prototypes for mono, mapped, true-color, planar, and word-oriented memory devices.
- External RasterOp procs for mono, gray, and gray8/rgb24 devices.
- Standard mono palettes for black/white polarity.

This header is central to the Ghostscript memory-device subsystem and is tightly coupled to `gxdevmem.h`, rendering procs, scan-line layout, and bit-depth-specific implementations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.c

Ghostscript MGR bitmap format output driver.

The file defines `gx_device_mgr`, extending the generic printer device with an `mgr_depth`, and exports device descriptors for:

- `mgrmono`
- `mgrgray2`
- `mgrgray4`
- `mgrgray8`
- `mgr4`
- `mgr8`

It writes MGR bitmap headers, iterates page scan lines with a `mgr_cursor`, and emits monochrome, grayscale, or color data. Grayscale output repacks Ghostscript 8-bit scan-line data into 2-, 4-, or 8-bit MGR representations and appends a color lookup table. Color output handles 4-bit PC palette data or 8-bit MGR’s 7x7x4 color cube plus extra grays, reserving the first 16 colors.

Important routines:

- `mgr_begin_page` writes the MGR header and allocates a row buffer.
- `mgr_next_row` copies printer scan lines.
- `mgr_print_page`, `mgrN_print_page`, and `cmgrN_print_page` serialize mono, gray, and color pages.
- `mgr_8bit_map_rgb_color` and `mgr_8bit_map_color_rgb` map Ghostscript colors to the MGR fixed palette.
- `clut2mgr` and `swap_bwords` convert palette entries and handle endianness.

Risk notes: some paths allocate row buffers without consistently checking every allocation result. Static CLUT tables make this old-style non-reentrant driver code. This is image/printer output logic, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.h

Shared header for Ghostscript MGR devices.

It declares the MGR 8-bit color mapping procedures and embeds definitions derived from MGR `dump.h` and `color.h`:

- `MGR_RESERVEDCOLORS`
- `B_PUTHDR8` macro for writing MGR bitmap headers
- `struct b_header`
- `struct nclut`
- MGR LUT constants for black/white, gray, bit-gray, VGA, BCT, user, and 8-bit LUT modes
- RGB component indexes
- Static `mgrlut[LUT][RGB][LUTENTRIES]` table with predefined 16-entry component ramps

The static lookup table is defined in the header, so every translation unit including it receives its own internal copy. In this group it is used by `gdevmgr.c`.

No filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmiff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmiff.c

Ghostscript MIFF file format driver for 24-bit direct-color output.

It defines the `miff24` printer device at 72 DPI using standard printer open/output/close procs and RGB color mapping. The main implementation is `miff24_print_page`, which:

- Allocates one raster line buffer.
- Writes a MIFF header with ImageMagick identifier, direct class, dimensions, and run-length compression.
- Iterates page rows via `gdev_prn_get_bits`.
- Emits RGB triples followed by a repeat count byte for adjacent identical pixels, capped at 255.
- Frees the line buffer and returns the final Ghostscript status code.

Risk notes: the RLE encoding is simple and assumes 24-bit RGB row layout of `width * 3` bytes. Allocation failure returns `VMerror`; scan-line fetch errors break the loop and are returned.

This is file-format serialization for rendered pages, not OS filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmiff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.c

Implementation of any-depth planar Ghostscript memory devices.

The public entry point is `gdev_mem_set_planar`, which validates a plane list, records plane depth/shift layout, detects uniform plane depth, and replaces normal chunky memory-device drawing procedures with planar-aware versions.

Core behavior:

- `mem_planar_open` requires `num_planes != 0` and then uses the generic memory scan-line setup.
- Drawing operations save and temporarily patch `gx_device_memory` fields so each plane can be treated as a separate normal memory device.
- `mem_planar_fill_rectangle`, `mem_planar_copy_mono`, and `mem_planar_strip_tile_rectangle` split colors into per-plane values.
- `mem_planar_copy_color` extracts bit fields from chunky source pixels into per-plane temporary buffers, then delegates to the appropriate plane-depth memory device.
- `planar_to_chunky` repacks planar storage back into chunky pixels, with optimized direct cases for 8-bit components.
- `mem_planar_get_bits_rectangle` supports querying a single selected plane when possible, otherwise converts to chunky output and uses Ghostscript get-bits copy helpers.

Risk notes: this file relies on temporary mutation of device fields (`color_info.depth`, `base`, `line_ptrs`, `raster`) and careful restoration. Errors from delegated procs are often ignored in drawing paths. The implementation prioritizes compatibility with Ghostscript memory devices over simplicity.

No filesystem logic is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.h

Interface header for planar Ghostscript memory devices.

It documents planar storage semantics:

- Color-index bits are stored by plane rather than by chunky pixel.
- The plane for least-significant color-index bits is stored first.
- Each plane may have a different allowed memory-device depth, currently documented as 1, 2, 4, 8, or 16.
- Each plane’s data is contiguous as if it were its own device.
- There is one line-pointer array per plane.

It declares:

- `gdev_mem_set_planar(gx_device_memory *mdev, int num_planes, const gx_render_plane_t *planes)`

The caller must first create a memory device, then configure planar layout before opening it. The existing device supplies color mapping but planar drawing procs are installed by the implementation.

No filesystem relevance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmpla.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr1.c

RasterOp implementation for 1-bit Ghostscript memory devices.

The central routine, `mem_mono_strip_copy_rop`, applies a logical RasterOp over destination, source, and texture bitmaps. It handles Ghostscript’s RGB-space RasterOp semantics while accounting for monobit device polarity, where many devices use black = 1 and white = 0.

Key behavior:

- Ensures mono palette polarity is initialized.
- Converts transparent logical operations with `gs_transparent_rop`.
- Adjusts the ROP if the device uses inverted mono polarity.
- Special-cases operations that reduce to fill, no-op, source copy, destination/source combinations, texture tiling, or destination/texture combinations.
- Falls back to byte-level scan-line loops for general D/S/T RasterOp evaluation using `rop_proc_table`.
- Handles source and texture bit skew, tile repetition, masks for partial bytes, and debug bitmap dumping.

Risk notes: the implementation is performance-sensitive bit manipulation with many coordinate and skew assumptions. It may call device procs for special cases, so callers must ensure those procs are valid for the current memory device.

This is rendering logic only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr2n.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr2n.c

RasterOp support for 2- and 4-bit Ghostscript memory devices.

The main routine, `mem_gray_strip_copy_rop`, tries to reuse the 1-bit RasterOp implementation by expanding pixel coordinates according to depth. It only takes the fast fake-mono route when conditions are compatible:

- Device is grayscale, not color.
- Source and texture transparency are not requested.
- Source colors are both all-zero or all-max.
- Texture colors, when present, are equal.

If the operation cannot be safely represented as a monobit operation, it calls `mem_default_strip_copy_rop`.

When using the fake-mono route, the code scales texture dimensions and x coordinates by `log2_depth`, maps solid colors down to 0/1, temporarily patches `fill_rectangle`, `copy_mono`, and `strip_tile_rectangle` to local stubs that return failure, and calls `mem_mono_strip_copy_rop`. If that returns an error, it falls back to the default general implementation.

Risk notes: this is explicitly a limited compatibility path. The local patched procs intentionally punt unsupported special cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr2n.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr8n.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr8n.c

RasterOp implementation for 8-bit gray and 24-bit RGB memory devices.

The file notes that 16- and 32-bit cases are not implemented here and fall back to the default slow implementation elsewhere. The main function is `mem_gray8_rgb24_strip_copy_rop`.

Behavior:

- Computes the ROP from `lop` and detects constant source or texture cases.
- Converts known black/white constant source or texture values into simplified ROPs.
- For non-gray 8-bit devices, only a few simple cases are handled directly; other cases call `mem_default_strip_copy_rop`.
- Clips/fits coordinates via `fit_copy` or `fit_fill`.
- Handles 8-bit and 24-bit destinations with macros for source/texture bit extraction, 24-bit get/put, and transparency checks.
- Covers combinations of constant source, constant texture, bitmap source, bitmap texture, 1-bit source/texture palettes, and repeated strip textures.

Risk notes: the implementation prioritizes avoiding code explosion over maximum performance and uses many macro-generated inner loops. Transparency is implemented by skipping destination writes when source or texture equals the transparent sentinel.

Rendering-only, no filesystem role.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr8n.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrop.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrop.h

Header for Ghostscript device RasterOp implementations.

It declares:

- `gs_transparent_rop(gs_logical_operation_t lop)` to compute effective 1-bit RasterOp behavior with transparency.
- Debug-only `trace_copy_rop` for copy/strip-copy RasterOp tracing.

It also defines the `gx_device_rop_texture` forwarding device type. This device applies RasterOp with a specified texture to drawing operations, treating the drawing color as the source rather than the texture. The texture is a `gx_device_color`, so it may represent solid colors or patterns.

Public construction/setup APIs:

- `gx_alloc_rop_texture_device`
- `gx_make_rop_texture_device`

This header is part of Ghostscript compositing/RasterOp infrastructure and depends on device forwarding and color structs. No filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.c

Experimental run-length encoded Ghostscript memory device.

The file explicitly warns that the code has not been tested. It builds a run-length representation over an existing `gx_device_memory`, using each scan line’s storage to hold `run_line` plus an array of doubly linked `run` records.

Key design:

- Run 0 is dummy end-of-line; run 1 is dummy start-of-line.
- Runs have bounded index and length bitfields.
- Lines can remain uninitialized if they are still entirely white.
- If a line becomes too fragmented or an operation is complex, it is expanded to standard memory form.
- `gdev_run_from_mem` copies an existing memory device, checks whether enough runs fit per line, initializes state ranges, and replaces drawing procs with run-aware wrappers.
- Non-fill operations such as copy, alpha copy, tiling, RasterOp, and get-bits standardize affected lines first and then delegate to saved normal memory-device procs.
- `run_fill_rectangle` is the main optimized operation and modifies run intervals directly.
- `run_fill_interval` performs split, delete, merge, and insertion logic for intervals.

Risk notes: the untested warning is significant. The code uses stack arrays sized by `MAX_RUNS`, bitfield packing, recursive standardization in some ranges, and subtle linked-list invariants. It is a memory optimization experiment, not production-looking filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.h

Header defining the run-length encoded memory device wrapper.

It describes a memory device that stores full-size pixels with run-length encoding when possible, switching to standard uncompressed representation as necessary.

It defines `gx_device_run`:

- First field is `gx_device_memory md`, allowing device-style casting.
- `runs_per_line` stores available run capacity.
- `umin/umax1` track an uninitialized-line range.
- `smin/smax1` track a range already converted to standard representation.
- `save_procs` stores original memory-device procs replaced by run-oriented implementations.

It declares:

- `gdev_run_from_mem(gx_device_run *rdev, gx_device_memory *mdev)`

No filesystem content; this is Ghostscript bitmap memory representation infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.c

Shared Microsoft Windows 3.x Ghostscript display-driver implementation.

It provides common device procedures for Windows display devices:

- `win_open`
- `win_sync_output`
- `win_output_page`
- `win_close`
- `win_map_rgb_color`
- `win_map_color_rgb`
- `win_get_params`
- `win_put_params`
- `win_makepalette`
- `win_nomemory`

On open, it derives default page dimensions, detects desktop bit depth if `BitsPerPixel` is unset, configures Ghostscript color info, and creates a Windows palette for indexed devices. Color mapping handles 24-bit BGR-style packed values, 16/15-bit packed values with endian adjustment, dynamic 8-bit palette allocation, 4-bit PC colors, and fallback mono/default behavior.

`win_put_params` supports changing `BitsPerPixel` before opening or resizing/reallocating the implementation bitmap while open. It contains an explicit comment that one recovery path after failed bitmap allocation is wrong because other device parameters may already have changed.

Risk notes: old Windows GDI resource management is manual. Dynamic 8-bit palette state uses a 4096-byte bitset. Error handling is mostly Ghostscript-style integer status codes.

No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.h

Shared header for Microsoft Windows 3.x Ghostscript drivers.

It imports Ghostscript device/memory/error headers plus Windows wrappers and Shell API headers. It defines `gx_device_win`, declares shared Windows device procedures, and provides common fields/macros for Windows device descriptors.

Important contents:

- Utility declarations: `win_makepalette`, `win_nomemory`, `win_update`.
- Device proc declarations for open, sync, output page, close, color mapping, params, xfont support, and alpha bits.
- Procedure typedef macros for implementation-specific bitmap allocation/free, repaint, and clipboard copy.
- `gx_device_win_common` fields: bit depth, color count, mapped color flags, bitmap procs, palette handles.
- `INITIAL_RESOLUTION`, `INITIAL_WIDTH`, `INITIAL_HEIGHT`.
- `wdev` cast macro.
- Windows RasterOp constants used by drawing/font code.
- `win_color_value` helper to compress Ghostscript color values to Windows 8-bit values using high-order bits.

This is platform display-driver infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmswn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmsxf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmsxf.c

External font (`xfont`) implementation for Ghostscript’s Microsoft Windows device.

The file defines `win_xfont` wrapping Ghostscript xfont state around Windows `LOGFONT`, `TEXTMETRIC`, and `HFONT`. It exposes `win_get_xfont_procs`, returning a `gx_xfont_procs` table with lookup, glyph conversion, metrics, rendering, and release functions.

Key behavior:

- Contains PostScript-to-OEM and ISO-to-OEM mapping tables.
- Maps common PostScript font names to Windows faces such as Courier New, Arial, Helv, Times New Roman, and Tms Rmn.
- `win_lookup_font` accepts only simple upright or inverted-y scaling matrices with no shear/rotation and size in a constrained range.
- `map_logical_font` verifies Windows actually selected the requested face prefix.
- `win_char_xglyph` maps StandardEncoding, ISOLatin1, and Symbol depending on Windows charset support.
- `win_char_metrics` queries Windows text extents and constructs a Ghostscript bbox.
- `win_render_char` renders required glyphs into a temporary 1-bit Windows bitmap, extracts bits, and copies them into the target Ghostscript device via `copy_mono`.
- `win_release` deletes the `HFONT` and optionally frees the xfont object.

Risk notes: direct window text rendering is disabled under `NOTUSED`; rendering relies on intermediate bitmaps. The code uses desktop DCs because it does not own a window. Encoding support is limited and name-based glyph lookup is not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmsxf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevn533.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevn533.c

Ghostscript driver for the Sony NWP-533 printer.

It depends on platform-specific headers `<sys/ioctl.h>` and `<newsiop/lbp.h>`, defaulting output to `/dev/lbp` if no filename is supplied. The device descriptor `gs_nwp533_device` uses printer dimensions and DPI constants from the LBP header and renders 1-bit output.

Important routines:

- `analyze_error` resets/queries printer status using LBP ioctls, reports recoverable states such as no paper, jam, door open, test printing, and non-recoverable hardware/toner conditions, then indicates whether to retry.
- `nwp533_open` supplies the default device path and calls `gdev_prn_open`.
- `nwp533_close` sends `LBIOCSTOP` with retry-on-recoverable-error handling before closing.
- `nwp533_print_page` allocates a scan-line buffer, stops the printer, seeks to start, writes all scan lines padded to 4 bytes, starts printing, and frees the buffer.

Risk notes: allocation failure for `in` is not checked before use. Some error paths return without freeing the buffer. Messages contain historical typos. This is direct printer-device I/O, not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevn533.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevnfwd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevnfwd.c

Ghostscript null and forwarding device implementation.

The first half implements forwarding-device infrastructure. A `gx_device_forward` delegates most device procedures to its `target`, with fallback defaults when no target exists. It also manages target reference counting through `gx_device_set_target` and a custom finalizer.

Covered forwarding procedures include initial matrix, sync/output page, color mapping, fill/copy operations, get/put params, CMYK/RGB-alpha mapping, xfont access, page device lookup, banding, RasterOp, path filling/stroking, masks, trapezoids, parallelograms, triangles, thin lines, images, strip tiling, get-bits rectangle, hardware params, text begin, color mapping procs, encode/decode color, pattern management, high-level color fills, color-space inclusion, linear color fills, and spot-equivalent updates.

The color-mapping section returns wrapper procs instead of the target’s raw procs so the target device pointer is passed correctly.

The second half defines `null` and `nullpage` devices. Their drawing procedures accept operations and return success without rendering. `nullpage` behaves as a page device; `null` preserves zero width/height for non-page-device parameter changes. Null decode maps one gray component from the low bit.

Risk notes: many forwarding procs fatal-error when a target is required but absent, while others use default fallbacks. Comments note clist target self-reference special cases.

This is Ghostscript device plumbing, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevnfwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevo182.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevo182.c

Ghostscript Okidata Microline 182 printer driver.

The file defines `gs_oki182_device`, a 1-bit printer device with default 72 DPI and 8x11 inch dimensions. It supports 72x72 and 144x144 output.

Main components:

- `oki_transpose` converts groups of 7 horizontal scan lines into printer column bytes. The high bit is set on every graphics byte so data cannot be mistaken for Okidata commands.
- `oki_compress` trims trailing empty columns and converts runs of leading empty columns into spaces.
- `oki_print_page` allocates input and output buffers, initializes the printer, optionally enters high-resolution mode, skips blank scan lines using fine line feeds, transposes scan-line groups into printer format, compresses output, emits graphics bytes and control sequences, form-feeds, flushes, and frees buffers.

Risk notes: the code uses old K&R-style implicit `int` in one local register declaration. It assumes particular printer command semantics and 8-bit mode. Buffer allocation errors are handled with cleanup.

No filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevo182.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevokii.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevokii.c

Ghostscript Okidata IBM-compatible 9-pin dot-matrix printer driver.

It defines `gs_okiibm_device`, supporting 60/120/240 horizontal DPI and 72/144 vertical DPI. The code is derived from Epson-style 9-pin logic but accounts for Okidata’s unusual handling of nominal 1/216-inch vertical feed commands as 1/144-inch movement on a repeating pattern.

Important routines:

- `okiibm_print_page1` handles core page output, scan-line buffering, blank-line skipping, vertical feed accounting, optional high-vertical-resolution line shuffling, 8x8 transposition via `gdev_prn_transpose_8x8`, and multi-pass graphics output for 240 DPI.
- `okiibm_output_run` emits a single ESC graphics command and optionally writes only even or odd columns for multi-pass output.
- `okiibm_print_page` prepares initialization/end strings and enables unidirectional printing at higher resolutions.

Risk notes: printer timing/positioning depends on the assumed power-on vertical feed state. The graphics mode lookup assumes `x_dpi / 60` indexes the table. This is device-specific output code, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevokii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevos2p.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevos2p.c

Ghostscript OS/2 printer device.

The file implements `os2prn`, intended only when Ghostscript runs as a DLL loaded by a Presentation Manager application, not as a text-mode executable. It ignores user `-g` and `-r` size/resolution for printer geometry, instead querying the OS/2 printer device context.

Key behavior:

- `os2prn_open` verifies PM process type, gets the anchor block, enumerates print queues, selects the requested/default queue, opens a queued printer DC, queries printer resolution and hardcopy caps, sets device size/margins/clipbox, creates printer and memory presentation spaces, determines 1-bit or 24-bit depth, starts the document, and opens a scratch printer file for Ghostscript compatibility.
- `os2prn_close` ends the document, destroys presentation spaces/DCs, closes Ghostscript printer state, and unlinks the scratch file.
- `os2prn_get_params` and `os2prn_put_params` expose `OS2QUEUE` and `BitsPerPixel`.
- `os2prn_print_page` renders slices into an OS/2 bitmap info structure and uses `GpiDrawBits` plus `GpiBitBlt` to transfer clipped bands to the printer.
- `os2prn_map_rgb_color`, `os2prn_map_color_rgb`, and `os2prn_set_bpp` handle 24-bit BGR-ordered output or mono defaults.
- `os2prn_get_queue_list` wraps `SplEnumQueue`; `os2prn_free_queue_list` releases queue buffers.

Risk notes: resource cleanup on open failures is partial. `pBuf` is passed uninitialized in the first `SplEnumQueue` size probe, matching old API style but fragile-looking in modern C. This is printer/platform integration, not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevos2p.c -->