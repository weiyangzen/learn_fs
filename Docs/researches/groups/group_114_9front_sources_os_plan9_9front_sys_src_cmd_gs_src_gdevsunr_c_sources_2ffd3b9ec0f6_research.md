# Group Research: group_114_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevsunr_c_sources_2ffd3b9ec0f6

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsunr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsunr.c

## Purpose
Ghostscript printer device for Harlequin-style 1-bit Sun raster output, exposed as `sunhmono`.

## Main Concepts
- Defines the Sun raster header layout and constants for magic, raw pixrect image type, and no colormap.
- Registers `gs_sunhmono_device` as a 1-bit printer device at 72 DPI by default.
- `sunhmono_print_page` writes a binary Sun raster header, page scanlines, 16-bit row padding, and the unusual trailing `"};\n"` terminator.

## Key Behavior
- Computes Ghostscript scanline bytes and rounds output row length up to an even byte count.
- Pulls each raster row with `gdev_prn_get_bits`.
- Writes raw 1-bit data with an extra zero byte when the Ghostscript row size is odd.
- Does not byte-swap the header fields; it writes the host representation of `int` fields.

## Dependencies
Uses Ghostscript printer memory and raster APIs from `gdevprn.h`.

## Notable Risks
- Return values from `fwrite`, `fputc`, and `gdev_prn_get_bits` are not checked after allocation succeeds.
- Header byte order is implicit in native `int` layout, which may not match the Sun raster format on all hosts.
- The output format is intentionally narrow: 1-bit, no colormap, with a nonstandard terminator.

## Filesystem Relevance
Writes an image stream through Ghostscript printer output. It is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsunr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.c

## Purpose
Common Ghostscript SuperVGA display driver implementation for VESA and several 256-color PC SVGA chipsets. It handles banked framebuffer drawing, palette management, mode selection, and chipset-specific page switching.

## Main Concepts
- Shared SVGA procedures: open/close, color mapping, fill, copy mono/color, get bits, alpha copy, and parameter put.
- `gx_device_svga` instances are declared for `vesa`, `atiw`, `tvga`, `tseng`, `cirr`, and `ali`.
- Uses banked VGA memory at segment `0xa000`, with 64K page switching through BIOS or hardware registers.
- Maintains a dynamic palette table starting at color index 64 unless the device uses a fixed palette.

## Key Functions
- `svga_find_mode`, `vesa_find_mode`: choose a mode that fits the requested dimensions and adjust resolution.
- `svga_open`, `svga_close`: save/restore display mode, load DAC colors, initialize page state.
- `svga_map_rgb_color`, `svga_map_color_rgb`: map RGB to fixed cube or dynamic DAC entries and read DAC values back.
- `svga_fill_rectangle`: writes directly into banked framebuffer memory, including boundary-crossing handling.
- `svga_copy_mono`, `svga_copy_color`: raster copy paths for 1-bit and 8-bit source data.
- `svga_get_bits`: reads a scanline back from banked framebuffer memory.
- `svga_copy_alpha`: approximates alpha as saturation toward white and caches shade mappings.
- Chipset page setters: `vesa_set_page`, `atiw_set_page`, `tvga_set_page`, `tseng_set_page`, `cirr_set_page`, `ali_set_page`.

## Dependencies
Uses Ghostscript device internals, PC framebuffer helpers, PC color mapping, BIOS interrupt helpers, port I/O, and chipset register access.

## Notable Risks
- Requires direct BIOS, VGA DAC, and hardware port access; unsuitable for protected modern systems unless emulated.
- Global saved mode and dynamic palette state are process-wide.
- Many hardware operations have no timeout or error confirmation.
- `tseng_open` returns success if `svga_open` fails after mode selection because it returns `0` when `code < 0`.
- Pointer/page arithmetic is tuned for 16-bit segmented/banked VGA memory and is fragile outside that environment.

## Filesystem Relevance
No filesystem logic. This is hardware display output code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.h

## Purpose
Shared declarations for Ghostscript SuperVGA display drivers.

## Main Contents
- Declares common SVGA device procedures such as `svga_close`, color mapping, fill/copy, get/put params, `svga_get_bits`, and `svga_copy_alpha`.
- Defines `mode_info`, mapping width/height pairs to BIOS or chipset mode IDs.
- Defines `gx_device_svga`, extending a Ghostscript device with mode callbacks, page callbacks, palette behavior, raster size, bank/window state, and chipset-specific union fields.
- Provides `svga_color_device` and `svga_device` initialization macros.
- Declares utility functions `svga_init_colors`, `svga_find_mode`, and `svga_open`.

## Dependencies
Requires `gdevpcfb.h` and Ghostscript core device declarations.

## Notable Risks
The structure exposes low-level hardware callbacks and chipset state directly. Correct behavior depends on matching the struct fields to the platform-specific implementation in `gdevsvga.c`.

## Filesystem Relevance
No filesystem logic. This is display-driver support infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.c

## Purpose
Implements Ghostscript TIFF fax and monochrome compressed TIFF devices: `tiffcrle`, `tiffg3`, `tiffg32d`, `tiffg4`, `tifflzw`, and `tiffpack`.

## Main Concepts
- Defines `gx_device_tfax`, combining printer state, fax parameters, TIFF writer state, `MaxStripSize`, and `FillOrder`.
- Uses shared TIFF directory writing from `gdevtifs.c`.
- Uses Ghostscript stream encoders for CCITT Fax, LZW, and PackBits/RLE output.
- Supports stripped TIFF output when `MaxStripSize` limits uncompressed strip size.

## Key Functions
- `tfax_get_params`, `tfax_put_params`: expose and validate `MaxStripSize` and `FillOrder`, delegating fax parameters to `gdevfax`.
- `gdev_stream_print_page_strips`: sends row ranges through a stream encoder and finalizes each TIFF strip.
- `gdev_fax_print_page_stripped`: exported helper for other fax drivers.
- `tifff_print_page`: common fax TIFF page writer.
- `tiffcrle_print_page`, `tiffg3_print_page`, `tiffg32d_print_page`, `tiffg4_print_page`: configure CCITT variants.
- `tifflzw_print_page`, `tiffpack_print_page`: configure LZW and PackBits output.
- `tfax_begin_page`: temporarily patches width for fax-adjusted page width while writing the TIFF directory.

## Dependencies
Uses `gdevprn.h`, `gdevtifs.h`, Ghostscript stream internals, CCITT Fax (`scfx.h`), fax device helpers (`gdevfax.h`), LZW, and RLE stream templates.

## Notable Risks
- Several calls to `gdev_tiff_end_strip` and `gdev_tiff_end_page` ignore return values.
- `tfax_begin_page` return value is ignored in common page paths.
- TIFF strip state assumes the encoder writes exactly the intended row ranges.
- The code mutates device width briefly to write adjusted TIFF metadata.

## Filesystem Relevance
Writes TIFF output files/streams and seeks within them for directory patching. It is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.h

## Purpose
Small public header for the TIFF/Fax writer helper used by fax-capable Ghostscript devices.

## Main Contents
- Declares `gdev_fax_print_page_stripped`, which writes a fax page through a CCITT Fax encoder with a caller-specified rows-per-strip value.

## Dependencies
The declaration depends on `gx_device_printer`, `FILE`, and `stream_CFE_state` types provided by including code.

## Filesystem Relevance
No filesystem logic. It declares an image-output helper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfnx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfnx.c

## Purpose
Implements uncompressed RGB TIFF output devices `tiff12nc` and `tiff24nc`.

## Main Concepts
- Defines a simple `gx_device_tiff` printer wrapper with `gdev_tiff_state`.
- Registers 24-bit RGB printer devices for both output modes.
- Uses TIFF tags for RGB photometric interpretation, no compression, MSB fill order, and three samples per pixel.
- `tiff12nc` stores three 4-bit RGB samples packed into 12 bits per pixel; `tiff24nc` stores 8-bit RGB samples.

## Key Functions
- `tiff12_print_page`: writes a TIFF directory using 4/4/4 bits per sample, converts 24-bit RGB scanlines into packed 12-bit RGB data, and emits rows.
- `tiff24_print_page`: writes a TIFF directory using 8/8/8 bits per sample and copies RGB scanlines directly.

## Dependencies
Uses Ghostscript printer APIs and the shared TIFF writer declarations in `gdevtifs.h`.

## Notable Risks
- If line allocation fails after `gdev_tiff_begin_page`, the page directory has already been written and is not closed/patched.
- `tiff12_print_page` loops over `raster` in 6-byte input chunks, which relies on the 24-bit scanline layout matching that conversion.
- Write errors are not checked.

## Filesystem Relevance
Writes TIFF image streams. It is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfnx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.c

## Purpose
Shared TIFF-writing substructure for Ghostscript printer devices. It writes TIFF headers/directories, manages strip offset/count arrays, records strip sizes, and patches directory fields after image data is written.

## Main Concepts
- Defines standard TIFF directory entries for page type, dimensions, strip offsets, orientation, rows per strip, byte counts, resolution, planar config, page number, software, and timestamp.
- Merges caller-supplied sorted TIFF entries with standard entries, allowing caller entries to replace standard tags.
- Stores strip offsets and byte counts in allocated arrays until page finalization.
- Supports multi-page output by patching the previous directory’s next-directory pointer.

## Key Functions
- `gdev_tiff_begin_page`: writes TIFF header for a new file, writes merged directory entries and indirect values, allocates strip arrays, computes rows per strip, and records first strip start.
- `gdev_tiff_end_strip`: records current strip byte count, pads the file to word alignment, and records the next strip offset.
- `gdev_tiff_end_page`: seeks back to patch strip offsets and byte counts, frees strip arrays, and remembers the next directory pointer location.

## Dependencies
Uses Ghostscript types, printer helpers, product/revision metadata, and standard C file/time APIs.

## Notable Risks
- Heavy use of `ftell`, `fseek`, and native integer layout makes portability dependent on classic TIFF assumptions and platform type sizes.
- Allocation failure after writing part of a directory leaves a partially written output.
- The initial placeholder write uses uninitialized strip arrays before they are filled, though those bytes are later patched.
- Local time generation uses `localtime` without null checking.
- Return values from file I/O are mostly ignored.

## Filesystem Relevance
Directly performs seekable file writes for TIFF output. It is output-format infrastructure, not filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.h

## Purpose
Defines TIFF data structures, constants, tags, and the shared state/API for Ghostscript TIFF writers.

## Main Contents
- Defines fixed-size TIFF integer aliases using Ghostscript architecture-size macros.
- Defines `TIFF_header`, endian magic constants, version value, and `TIFF_dir_entry`.
- Enumerates TIFF field types, including internal `TIFF_INDIRECT`.
- Enumerates the subset of TIFF tags used by Ghostscript output devices, including image dimensions, compression, photometric interpretation, fill order, strips, resolution, planar config, fax options, page number, software, and timestamp.
- Defines compression, photometric, fill-order, orientation, planar-config, fax-option, and resolution-unit constants.
- Defines `gdev_tiff_state`, holding memory, directory offsets, strip counts, rows per strip, and strip offset/count arrays.
- Declares `gdev_tiff_begin_page`, `gdev_tiff_end_strip`, and `gdev_tiff_end_page`.

## Dependencies
Relies on Ghostscript architecture macros and printer/file types supplied by including modules.

## Notable Risks
The TIFF state is documented as stack-only because it has no GC descriptor. Allocating it in GC-managed storage would make pointer tracing unsafe.

## Filesystem Relevance
Defines structures for seekable TIFF output files. It is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtifs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtknk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtknk.c

## Purpose
Ghostscript printer driver for Tektronix 4696/4695 inkjet plotters, exposed here as `tek4696`.

## Main Concepts
- Defines a 4-bit subtractive color index model for black, magenta, yellow, cyan, and their simple combinations.
- Maps RGB thresholded colors to Tektronix ink bit combinations.
- Converts Ghostscript raster rows into four 1-bit color planes and emits Tektronix escape-command output.

## Key Functions
- `tekink_map_rgb_color`: threshold maps RGB to one of eight valid ink combinations.
- `tekink_map_color_rgb`: maps valid device indexes back to RGB and rejects unused indexes.
- `tekink_print_page`: allocates a row buffer, splits each scanline into B/M/Y/C bit planes, suppresses trailing blank bytes, emits color-plane commands, handles micro-line feeds, skips leading blank lines on roll paper, and separates plots with feeds or form feed.

## Dependencies
Uses Ghostscript printer APIs and C heap allocation through `malloc_.h`.

## Notable Risks
- Uses raw `malloc`/`free` instead of Ghostscript memory APIs.
- Returns `-1` directly on allocation failure instead of a Ghostscript error code.
- Write errors are not checked.
- File naming/model behavior depends on `pdev->dname` string comparison to detect roll paper.

## Filesystem Relevance
Writes printer command streams only. It is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtknk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtrac.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtrac.c

## Purpose
Diagnostic Ghostscript tracing devices that print drawing operations rather than rendering them. It provides sample high-level device implementations for monochrome, RGB, and CMYK tracing.

## Main Concepts
- Devices: `tr_mono`, `tr_rgb`, and `tr_cmyk`.
- Implements low-level callbacks for rectangles, mono/color/alpha copy, masks, tiles, and shape fills.
- Implements high-level path, image, and text tracing.
- Uses Ghostscript debug output macros such as `dprintf`/`dputs`.

## Key Functions
- `trace_drawing_color`, `trace_lop`, `trace_path`, `trace_clip`: formatting helpers for colors, logical ops, paths, and clipping.
- Low-level trace callbacks: `trace_fill_rectangle`, `trace_copy_mono`, `trace_copy_color`, `trace_copy_alpha`, `trace_fill_mask`, shape/tile callbacks.
- `trace_fill_path`, `trace_stroke_path`: dump path contents and state.
- `trace_begin_typed_image`, `trace_plane_data`, `trace_end_image`: trace image setup and incoming image planes.
- `trace_text_begin`: dumps text operation flags, font name, text/glyph data, width adjustments, and optionally creates a text enumerator for supported cases.

## Dependencies
Uses Ghostscript core device, path, clip path, color, image, font, text, and imager-state internals.

## Notable Risks
- Designed for diagnostics, not production rendering; many operations return success without drawing.
- Several callbacks print placeholders such as `**fill_trapezoid**` or default to generic handling.
- Text width handling is explicitly marked wrong for Type 0 fonts.
- Debug output can expose document text and drawing details.

## Filesystem Relevance
No filesystem logic. Output is diagnostic logging through Ghostscript debug facilities.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtrac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtsep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtsep.c

## Purpose
Implements uncompressed TIFF output devices for grayscale, CMYK, and separations: `tiffgray`, `tiff32nc`, and `tiffsep`.

## Main Concepts
- `tiffgray` writes 8-bit grayscale TIFF.
- `tiff32nc` writes 32-bit uncompressed CMYK TIFF.
- `tiffsep` writes a composite CMYK-equivalent TIFF plus separate 8-bit grayscale TIFF files for each selected process/spot separation.
- `tiffsep_device` embeds DeviceN parameters, equivalent CMYK spot-color metadata, one TIFF state for the composite file, TIFF states for each separation, and sidecar `FILE *` handles.

## Key Functions
- `tiffgray_print_page`, `tiff32nc_print_page`: shared pattern of writing a TIFF directory, streaming rows, ending strip/page, and freeing line buffers.
- DeviceN mapping:
  - `tiffsep_get_color_mapping_procs`
  - `tiffsep_get_color_comp_index`
  - `tiffsep_encode_color`
  - `tiffsep_decode_color`
  - `tiffsep_update_spot_equivalent_colors`
- Parameter handling:
  - `tiffsep_get_params`
  - `tiffsep_put_params`
- Separation file handling:
  - `create_separation_file_name`
  - `copy_separation_name`
  - `tiffsep_prn_open`
  - `tiffsep_prn_close`
- Raster composition:
  - `number_output_separations`
  - `build_comp_to_sep_map`
  - `build_cmyk_map`
  - `build_cmyk_raster_line`
  - `tiffsep_print_page`

## Behavior
- Supports more spot colors than can be imaged in one pass, relying on `SeparationOrder` for multi-pass output.
- Separation filenames are derived from the main output filename plus `.Cyan.tif`, `.Magenta.tif`, `.Yellow.tif`, `.Black.tif`, or `.sN.tif` for spot color indexes.
- Individual separation files store inverted component values because TIFF grayscale is additive while separations are subtractive.
- Composite CMYK data is built from process colors and equivalent CMYK values for spots.

## Notable Risks
- Separation-name escaping is explicitly not implemented; the safer numeric spot suffix path is used.
- `map_comp_to_sep` is not initialized before selective assignment, so unexpected component maps could read stale stack values.
- `gx_parse_output_file_name` return code is overwritten/ignored except for its format pointer effect.
- Several output and TIFF-finalization errors are not checked.
- Sidecar files can remain open across pages unless page-number formatting requires per-page files.

## Filesystem Relevance
Creates and writes multiple TIFF output files derived from the output filename. It is image/printer output code, not filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtsep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.c

## Purpose
Shared utility implementation for Ghostscript vector-style devices such as PDF, PostScript, PCL XL, CGM, metafile, and similar high-level output formats.

## Main Concepts
- Provides default vector procedure implementations for paths, rectangles, polygons, clipping, output files, image enumeration, and common shape fills.
- Caches device graphics state so concrete vector devices only emit changes.
- Supports optional bounding-box tracking through a `gx_device_bbox`.
- Manages output file opening as seekable or sequential, plus stream buffering.

## Key Functions
- Path output:
  - `gdev_vector_dopath`
  - `gdev_vector_dorect`
  - `gdev_vector_dopath_init`
  - `gdev_vector_dopath_segment`
  - `gdev_vector_write_polygon`
  - `gdev_vector_write_rectangle`
- State management:
  - `gdev_vector_init`
  - `gdev_vector_reset`
  - `gdev_vector_update_log_op`
  - `gdev_vector_update_fill_color`
  - `gdev_vector_prepare_fill`
  - `gdev_vector_prepare_stroke`
  - `gdev_vector_stroke_scaling`
- File/stream management:
  - `gdev_vector_open_file_options`
  - `gdev_vector_stream`
  - `gdev_vector_close_file`
  - `gdev_vector_get_params`
  - `gdev_vector_put_params`
- Clipping:
  - `gdev_vector_write_clip_path`
  - `gdev_vector_update_clip_path`
- Image enumeration:
  - `gdev_vector_begin_image`
  - `gdev_vector_end_image`
- Default device procs:
  - `gdev_vector_fill_rectangle`
  - `gdev_vector_fill_path`
  - `gdev_vector_stroke_path`
  - `gdev_vector_fill_trapezoid`
  - `gdev_vector_fill_parallelogram`
  - `gdev_vector_fill_triangle`

## Notable Behavior
- Optimizes rectangular paths and can merge collinear line segments.
- Defers fill-only isolated `moveto` operations to avoid an Acrobat Reader 4 artifact.
- Prevents changing `OutputFile` after output has begun unless safety and stream-position checks allow it.
- Uses a stream whose close procedure is changed to flush only, leaving final file closure to Ghostscript output-file handling.

## Notable Risks
- Some comments mark incomplete or wrong behavior, including fill padding value and initial saved color comments.
- `gdev_vector_stroke_path` computes a matrix for anisotropic stroke scaling but passes `NULL` to `dopath`, so the intended inverse path transform is not applied in that call.
- Many default operations fall back to raster/default behavior on errors, which may surprise concrete vector devices expecting purely high-level output.
- Output-file changes require careful state handling because vector formats typically write headers early.

## Filesystem Relevance
Manages output files and buffered streams for vector devices. It is output infrastructure, not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.h

## Purpose
Central shared header for Ghostscript vector-style output devices.

## Main Contents
- Documents vector devices as high-level command streams rather than raster-only devices.
- Defines `gx_path_type_t` flags for fill, stroke, clip, winding/even-odd rules, path optimization, and forced closepath emission.
- Defines `gx_device_vector_procs`, the callback table concrete vector devices implement for page start, graphics-state changes, high-level colors, paths, rectangles, and path segments.
- Defines `gx_device_vector_common`, extending a Ghostscript device with:
  - output file and stream fields,
  - cached imager state and dash pattern,
  - saved fill/stroke high-level colors,
  - clipping path IDs,
  - fill/stroke options,
  - coordinate scale,
  - page mark state,
  - optional bbox device,
  - cached black/white color indexes.
- Declares GC descriptor macros for vector devices and image enumerators.
- Defines output-file option flags for ASCII, sequential, sequential fallback, and bbox tracking.
- Declares utility APIs implemented in `gdevvec.c`.
- Declares default vector device procedures for fills, strokes, and geometric fills.

## Dependencies
Includes Ghostscript platform, RasterOp, device, bbox, image parameter, imager-state, high-level color, and stream headers.

## Notable Risks
The header is a private subsystem contract; concrete vector devices depend on field layout and callback semantics. Several callbacks are optional but utility functions call specific callbacks when advertised behavior requires them.

## Filesystem Relevance
Declares output-file/stream support for vector formats. It is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvglb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvglb.c

## Purpose
Ghostscript display driver for Linux/386 console graphics through `vgalib`, limited to 16-color modes.

## Main Concepts
- Defines `gx_device_vgalib` with a `DisplayMode` parameter.
- Registers the `vgalib` device.
- Uses svgalib calls for mode setting, palette setup, pixel drawing, line drawing, and pixel readback.

## Key Functions
- `vgalib_open`: chooses requested/default mode, clears screen, sets dimensions and resolution, initializes a 16-color palette.
- `vgalib_close`: restores text mode.
- `vgalib_map_rgb_color`, `vgalib_map_color_rgb`: delegate to PC 4-bit color mapping.
- `vgalib_fill_rectangle`: fills via lines for larger rectangles and pixels for small rectangles.
- `vgalib_tile_rectangle`: pre-fills when both tile colors are opaque, then delegates to default tiling.
- `vgalib_copy_mono`, `vgalib_copy_color`: draw source bits/nibbles pixel by pixel.
- `vgalib_get_bits`: reads pixels from the screen and packs them into Ghostscript scanline format.
- `vgalib_get_params`, `vgalib_put_params`: expose and update `DisplayMode`, closing the device before a mode change if open.

## Dependencies
Uses Ghostscript device/color/parameter APIs and external `<vga.h>` svgalib functions.

## Notable Risks
- Requires console graphics permissions and svgalib support.
- Pixel-by-pixel paths are slow.
- `vgalib_get_bits` does not range-check `y`.
- Mode switching directly affects the console and restores `TEXT` on close.

## Filesystem Relevance
No filesystem logic. This is a console display backend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvglb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwddb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwddb.c

## Purpose
Microsoft Windows Ghostscript display driver using a device-dependent bitmap (DDB) backing store.

## Main Concepts
- Defines `gx_device_win_ddb`, extending Windows common device state with a backing bitmap/DC, palette, pens, brushes, and a small monochrome staging bitmap.
- Registers the `mswin` device.
- Uses Windows GDI operations for fills, blits, palette management, repainting, and clipboard export.

## Key Functions
- `win_ddb_open`: opens the common Windows device, rejects >8 bpp, allocates backing bitmap, creates mono staging DC/bitmap, creates palette/tools, and routes text drawing to the bitmap DC.
- `win_ddb_close`: deletes tools, DCs, bitmap, palette, and palette memory, then closes common Windows state.
- `win_ddb_map_rgb_color`: extends the bitmap palette when the window palette gets a new color.
- `win_ddb_fill_rectangle`: fills with `PatBlt`.
- `win_ddb_tile_rectangle`: optimizes small monochrome tile blits through the staging bitmap.
- `win_ddb_copy_mono`: chunks mono copies into the staging bitmap and `BitBlt`s with appropriate raster ops.
- `win_ddb_copy_color`: draws 8-bit or 4-bit color pixel maps with `SetPixel`, or delegates mono cases to `copy_mono`.
- `win_ddb_copy_to_clipboard`: copies the backing bitmap and palette to the Windows clipboard.
- `win_ddb_repaint`: blits from backing DC to the window DC.
- `win_ddb_alloc_bitmap`, `win_ddb_free_bitmap`: allocate/free backing bitmap/DC, halving resolution after repeated allocation failures.
- `win_maketools`, `win_destroytools`, `win_addtool`: manage palette-indexed pens and brushes.

## Notable Risks
- `win_maketools` allocation failure is not propagated to `win_ddb_open`; later code assumes tool arrays exist.
- Some GDI calls are unchecked.
- `win_ddb_alloc_bitmap` silently halves resolution on allocation failure, changing output dimensions.
- DDB output is palette/device dependent and limited to <=8 bpp.

## Filesystem Relevance
No filesystem logic. This is a Windows display/clipboard backend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwddb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwdib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwdib.c

## Purpose
Microsoft Windows Ghostscript display/DLL driver using a device-independent bitmap (DIB) memory backing store.

## Main Concepts
- Defines `gx_device_win_dib`, extending Windows common device state with DIB memory, optional Win32 mutex, lock count, and an embedded Ghostscript memory device.
- Registers the `mswindll` device.
- Exposes DLL APIs for copying the DIB, copying the palette, drawing the bitmap to a caller HDC, locking the device, and retrieving bitmap rows.

## Key Functions
- `win_dib_open`: opens common Windows state, creates a mutex on non-Win32s, validates memory-device support, allocates bitmap memory, and notifies DLL callbacks.
- `win_dib_get_initial_matrix`: uses a lower-left origin suitable for DIB memory.
- `win_dib_close`: locks, notifies callback shutdown, frees bitmap memory, closes mutex, and closes common Windows state.
- Drawing wrappers: `win_dib_fill_rectangle`, `win_dib_copy_mono`, `win_dib_copy_color`, `win_dib_get_bits`; these delegate to the embedded memory device and split transfers around 64K segment boundaries on 16-bit Windows.
- `win_dib_put_params`: locks around Windows parameter updates.
- DLL exports:
  - `gsdll_copy_dib`
  - `gsdll_copy_palette`
  - `gsdll_draw`
  - `gsdll_lock_device`
  - `gsdll_get_bitmap_row`
- `win_dib_repaint`: pushes DIB rows to a Windows DC with `SetDIBitsToDevice`, chunking large transfers.
- `win_dib_make_dib`: allocates a standalone DIB copy with header, palette/bitfields, and pixel data.
- `win_dib_alloc_bitmap`, `win_dib_free_bitmap`: allocate global memory for raster data and line pointers.
- `win_dib_lock_device`: mutex/lock-count helper for external access.

## Notable Risks
- 16-bit segment splitting code is delicate; one copy-color split branch advances the source by `by * raster` rather than `bh * raster`.
- Several allocation/lock paths beep or return null without detailed error propagation.
- `gsdll_get_bitmap_row` assumes a valid device pointer and accesses fields before full validation.
- External callers can receive row pointers valid only while locked; misuse can race with Ghostscript drawing or resizing.

## Filesystem Relevance
No filesystem implementation logic. The DLL row-copy API can support saving bitmaps externally, but this file only manages in-memory DIB output and Windows drawing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwdib.c -->