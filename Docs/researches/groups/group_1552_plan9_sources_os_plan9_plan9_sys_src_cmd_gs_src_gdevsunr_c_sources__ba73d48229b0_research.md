# Group Research: group_1552_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevsunr_c_sources__ba73d48229b0

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsunr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsunr.c

Implements the Ghostscript `sunhmono` printer device, a narrow Sun raster output driver for Harlequin-style 1-bit `SUN_RAS` files.

Key behavior:
- Defines the Sun raster file header fields, magic value, standard/raw raster type, and no-colormap map type used by this driver.
- Registers `gs_sunhmono_device` as a 1-bit printer device at the configured/default 72 DPI with zero margins.
- `sunhmono_print_page` computes Ghostscript scan-line bytes, pads output scan lines to an even byte count, and writes a header followed by all image rows.
- Uses `gdev_prn_get_bits` to fetch each raster row, writes the Ghostscript row bytes, writes a zero pad byte for odd-width rows, then appends the unusual `};\n` terminator expected by the target format variant.
- Allocates one row buffer with Ghostscript memory APIs and returns `VMerror` if allocation fails.

Dependencies:
- Depends on `gdevprn.h`, printer-device macros, `gdev_mem_bytes_per_scan_line`, `gdev_prn_get_bits`, and Ghostscript allocation/error helpers.

Research notes:
- The file explicitly supports only the Harlequin 1-bit no-colormap variant, not the broader Sun raster family.
- Header output is a direct struct write, so portability depends on the build environment matching the expected integer layout/byte order for this Ghostscript port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsunr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.c

Implements legacy DOS SuperVGA display devices for Ghostscript, including shared 256-color frame-buffer operations and chipset-specific mode/page switching.

Key behavior:
- Maintains an 8-bit palette model with a fixed 64-entry color cube plus dynamically assigned DAC entries from index 64 upward unless the device uses fixed colors.
- `svga_find_mode` selects the smallest mode table entry that satisfies the requested width/height, adjusts device resolution, and records the frame-buffer raster.
- `svga_open` saves the prior display mode, switches to the selected graphics mode, initializes DAC colors, and resets the current 64K page window; `svga_close` restores the saved mode.
- `svga_map_rgb_color` maps RGB to fixed PC palette entries or dynamically hashes 5-bit RGB values into assignable DAC entries; it returns `gx_no_color_index` if the dynamic table is exhausted.
- `svga_fill_rectangle`, `svga_copy_mono`, `svga_copy_color`, `svga_get_bits`, and `svga_copy_alpha` draw directly into banked video memory at segment `0xa000`, changing pages as offsets cross 64K windows.
- `svga_copy_alpha` approximates alpha as saturation toward white and lazily allocates palette shades for intermediate alpha levels.
- Defines a VESA device that queries BIOS mode info, validates bank-window geometry, supports one or two read/write windows, and uses either a BIOS page function pointer or interrupt `0x10` bank switching.
- Defines ATI Wonder, Trident, Tseng ET3000/ET4000, Cirrus CL-GD54XX, and Avance Logic devices with chipset-specific mode tables and page-select register programming.

Dependencies:
- Uses Ghostscript device/color/parameter APIs from `gxdevice.h`, `gdevpccm.h`, `gdevpcfb.h`, and `gdevsvga.h`.
- Uses DOS-era BIOS/register, segment pointer, I/O port, interrupt, and optional assembly helpers such as `int86`, `int86x`, `outportb`, `inportb`, `MK_PTR`, `disable`, and `enable`.

Research notes:
- This is hardware-facing display code, not a Plan 9 OS subsystem despite its location in the vendored Plan 9 Ghostscript tree.
- Correctness is tightly coupled to banked VGA assumptions: 64K windows, byte-per-pixel 8-bit modes, and chipset register semantics.
- The shared dynamic color table is file-global, so multiple open SVGA devices would not have independent dynamic palette state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.h

Declares the shared interface and device structure for the SuperVGA display drivers implemented in `gdevsvga.c`.

Key behavior:
- Declares common device procedures for open/close-adjacent behavior, palette mapping, rectangle fill, mono/color copy, parameter handling, scan-line readback, and alpha copy.
- Defines `mode_info`, a width/height-to-BIOS-mode lookup entry.
- Defines `gx_device_svga`, extending `gx_device_common` with mode getter/setter callbacks, bank-page callback, palette policy, selected mode, raster size, active page, read/write window numbers, and chipset-specific union state.
- Provides `svga_color_device` and `svga_device` macros for constructing 8-bit SVGA devices with initial 640x480 page geometry and resolution derived from page height.
- Declares utility functions for color initialization, mode lookup, and common open handling.

Dependencies:
- Requires `gdevpcfb.h` and the Ghostscript device procedure macro conventions from `gxdevice.h`.

Research notes:
- The structure deliberately separates common banked-frame-buffer logic from chipset-specific page selection.
- The default device macro maps a screen-sized display into a full-page coordinate space rather than exposing physical monitor DPI.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.c

Implements TIFF/Fax and monochrome compressed TIFF printer devices: `tiffcrle`, `tiffg3`, `tiffg32d`, `tiffg4`, `tifflzw`, and `tiffpack`.

Key behavior:
- Defines `gx_device_tfax`, combining printer state, fax state, TIFF writer state, `MaxStripSize`, and TIFF `FillOrder`.
- Exposes `MaxStripSize` and `FillOrder` through get/put parameters; rejects negative strip sizes and fill-order values other than TIFF values 1 and 2.
- Splits page output into strips with `gdev_stream_print_page_strips`, calling a stream filter per strip and then `gdev_tiff_end_strip`.
- Exports `gdev_fax_print_page_stripped` for other fax-style drivers to write CCITT/Fax streams in TIFF strips.
- Builds a sorted monochrome TIFF directory template with bits-per-sample, compression, photometric interpretation, fill order, samples-per-pixel, and T4/T6 options.
- `tifff_print_page` writes the TIFF page directory, configures `FirstBitLowOrder` from `FillOrder`, streams fax rows, and finalizes the TIFF page.
- Configures CCITT RLE, Group 3 1D, Group 3 2D, and Group 4 variants by setting stream state fields such as `EndOfLine`, `EncodedByteAlign`, and `K`, plus the proper TIFF compression/options tags.
- Implements LZW and PackBits TIFF output through Ghostscript stream templates `s_LZWE_template` and `s_RLE_template`.
- `tfax_begin_page` temporarily patches the device width when fax encoding columns differ from the current device width.

Dependencies:
- Uses `gdevprn.h`, `gdevtifs.h`, `strimpl.h`, `scfx.h`, `gdevfax.h`, `gdevtfax.h`, `slzwx.h`, and `srlx.h`.
- Relies on the shared TIFF directory/strip writer in `gdevtifs.c` and fax-stream helpers from the Ghostscript fax subsystem.

Research notes:
- `MaxStripSize` is based on uncompressed byte count and falls back to one row per strip if the requested maximum is smaller than a scan line.
- The code intentionally avoids the `CleanFaxData` TIFF tag because many TIFF readers do not recognize it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.h

Declares the shared TIFF/Fax page writer entry point used by fax-capable Ghostscript drivers.

Key behavior:
- Provides the prototype for `gdev_fax_print_page_stripped`, which writes a fax-encoded printer page using a `stream_CFE_state` and a requested rows-per-strip value.

Dependencies:
- Assumes callers have visible definitions for `gx_device_printer`, `FILE`, and `stream_CFE_state` from the surrounding Ghostscript headers.

Research notes:
- This is a minimal interface header; the behavior and validation live in `gdevtfax.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfnx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfnx.c

Implements uncompressed RGB TIFF printer devices `tiff12nc` and `tiff24nc`.

Key behavior:
- Defines a printer-backed TIFF device carrying `gdev_tiff_state`.
- Registers `tiff12nc` and `tiff24nc` as 24-bit Ghostscript RGB devices using the default RGB color mapping procedures.
- Builds a sorted RGB TIFF directory with indirect `BitsPerSample`, no compression, RGB photometric interpretation, MSB fill order, and three samples per pixel.
- Provides separate indirect bits-per-sample values for 4/4/4 RGB (`tiff12nc`) and 8/8/8 RGB (`tiff24nc`).
- `tiff12_print_page` fetches 24-bit rows, packs high nibbles from six source bytes into three 12-bit RGB output bytes, and writes `(width * 3 + 1) >> 1` bytes per row.
- `tiff24_print_page` writes fetched printer rows directly as 24-bit RGB data.
- Both print paths open the TIFF page directory, write all rows as one strip, patch strip metadata, finalize the page, and free the row buffer.

Dependencies:
- Uses `gdevprn.h`, `gdevtifs.h`, Ghostscript printer raster access, and the shared TIFF page writer.

Research notes:
- The 12-bit device still renders internally through a 24-bit printer device and reduces precision only at file output.
- Error handling returns early on allocation or row fetch failure, but the allocated row buffer is only freed along the normal block path after allocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfnx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.c

Implements the shared TIFF page/directory/strip writer used by multiple Ghostscript TIFF output devices.

Key behavior:
- Defines standard TIFF directory entries for page identity, dimensions, strip offsets/counts, orientation, rows per strip, X/Y resolution, planar config, resolution unit, page number, software, and timestamp.
- Defines indirect standard values for next-directory offset, rational resolutions, software string, and TIFF date/time string.
- On big-endian builds, adjusts packed SHORT/BYTE immediate tag values before writing them.
- `gdev_tiff_begin_page` writes the TIFF header for a new file or patches the previous directory pointer for multi-page output.
- Merges sorted standard entries with sorted client entries, replacing standard tags when client tags use the same tag number.
- Computes strip count from `max_strip_size`; uses one strip when no maximum is supplied, otherwise calculates rows per strip with a minimum of one row.
- Allocates paired `StripOffsets` and `StripByteCounts` arrays, writes placeholder strip metadata, records the first strip start, and writes indirect values after directory entries.
- `gdev_tiff_end_strip` records each strip byte count, pads odd file offsets to word alignment, and records the next strip start.
- `gdev_tiff_end_page` records where the next directory pointer lives, patches strip offsets and byte counts back into the file, and frees the strip metadata array.

Dependencies:
- Uses `stdio_.h`, `time_.h`, `gstypes.h`, `gscdefs.h`, `gdevprn.h`, and `gdevtifs.h`.
- Depends on Ghostscript printer helpers for page/file state and scan-line sizing.

Research notes:
- This file provides the core multi-page TIFF chaining and strip-offset patching that higher-level TIFF devices rely on.
- Client-provided TIFF entries must be sorted by tag, as the merge algorithm assumes sorted inputs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.h

Defines the TIFF types, tag constants, directory-entry representation, TIFF writer state, and public TIFF page/strip writer functions.

Key behavior:
- Defines fixed-size TIFF integer typedefs from architecture size macros rather than assuming C `short`/`long` widths.
- Defines the TIFF header and directory-entry structures, including magic values for big/little endian and TIFF version 42.
- Enumerates TIFF field data types and the internal `TIFF_INDIRECT` flag used to mark values that should be written out-of-line.
- Enumerates the subset of TIFF tags used by these Ghostscript devices, including image dimensions, compression, photometric interpretation, fill order, strip metadata, resolution, T4/T6 fax options, page number, software, date/time, and `CleanFaxData`.
- Defines compression, photometric, orientation, planar configuration, T4/T6 option, resolution-unit, and clean-fax-data constants.
- Defines stack-only `gdev_tiff_state`, tracking memory, directory offsets, tag counts, current strip index/count/rows, patch offsets, and strip offset/count arrays.
- Declares `gdev_tiff_begin_page`, `gdev_tiff_end_strip`, and `gdev_tiff_end_page`.

Dependencies:
- Requires Ghostscript architecture macros, memory type `gs_memory_t`, printer type `gx_device_printer`, and byte/FILE definitions from including source context.

Research notes:
- The header explicitly warns that `gdev_tiff_state` has no GC descriptor and must not live in GC-managed allocated storage.
- The tag list is intentionally partial and grows only as supported devices need more TIFF fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtifs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtknk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtknk.c

Implements the `tek4696` printer device for Tektronix 4696/4695 ink-jet plotters.

Key behavior:
- Registers a 4-bit, 120 DPI printer device with a roll-media page size chosen to approximate an A-series aspect ratio.
- Defines a subtractive Tektronix palette using bit planes for black, magenta, yellow, and cyan, with only eight meaningful RGB-derived palette values.
- `tekink_map_rgb_color` thresholds each RGB channel at half intensity and maps the resulting 3-bit RGB code into the printer’s 4-bit ink code.
- `tekink_map_color_rgb` maps valid printer colors back to RGB and rejects unused 4-bit values.
- `tekink_print_page` allocates one input row plus four separated one-bit output planes, one per ink channel.
- For each raster row, separates input 4-bit pixels into black/magenta/yellow/cyan bit planes, trims trailing zero bytes from each plane, and emits Tektronix escape-command line records for nonblank color planes.
- Tracks blank lines for roll-paper devices to skip leading whitespace and compact runs of blank rows into micro-line-feed commands.
- Emits final micro-line-feed/page separation commands and frees the temporary buffer.

Dependencies:
- Uses `gdevprn.h`, `malloc_.h`, Ghostscript printer scan-line copying, and standard C memory/string/file routines.

Research notes:
- The code uses `malloc`/`free` rather than Ghostscript memory allocation.
- It is specific to the Tektronix printer command stream and would need new descriptors/geometric settings for related models.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtknk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtrac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtrac.c

Implements diagnostic Ghostscript tracing devices that print low-level and selected high-level drawing operations instead of rendering output.

Key behavior:
- Provides internal printers for `gx_drawing_color`, logical operation values, paths, and nontrivial clipping paths.
- Low-level procedures log `fill_rectangle`, `copy_mono`, `copy_color`, `copy_alpha`, `fill_mask`, parallelogram/triangle fills, thin lines, strip tile rectangles, and placeholder messages for unsupported paths such as trapezoid and ROP tracing.
- High-level `trace_fill_path` and `trace_stroke_path` print path segments, drawing color, fill/stroke parameters, and clip information.
- Defines a minimal `trace_image_enum_t` image enumerator that logs plane data calls, tracks rows remaining, and frees itself at image end.
- `trace_begin_typed_image` logs image type and image matrix, handles image types 1/3/4 enough to compute component/plane metadata, returns immediately for type 2 images with no data, and otherwise falls back to Ghostscript’s default typed-image handling.
- `trace_text_begin` logs text operation flags, font name, text/glyph data, widths/deltas, and drawing color; for simple width-return cases it can compute total width and update the current path, otherwise it falls back to the default text path.
- Defines three concrete devices: `tr_mono` (1-bit monochrome), `tr_rgb` (24-bit RGB), and `tr_cmyk` (4-bit CMYK).

Dependencies:
- Uses Ghostscript graphics, path, clipping, image, font, text, imager-state, halftone, and device headers.
- Relies on Ghostscript debug output macros (`dputs`, `dprintf*`) and default fallback device procedures.

Research notes:
- This is a debugging/instrumentation device and intentionally leaves many operations as logged no-ops or default fallbacks.
- Text width computation is explicitly marked as copied from `pdfwrite` and wrong for Type 0 fonts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtrac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtsep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtsep.c

Implements uncompressed TIFF grayscale, CMYK, and separation-output devices: `tiffgray`, `tiff32nc`, and `tiffsep`.

Key behavior:
- `tiffgray` is an 8-bit grayscale printer device that writes uncompressed min-is-black TIFF data through the shared TIFF writer.
- `tiff32nc` is a 32-bit CMYK printer device using separated 8-bit-per-plane CMYK color mapping and uncompressed TIFF output with `Photometric_separated`.
- Defines sorted TIFF directory templates and bits-per-sample indirect values for grayscale and CMYK output.
- Defines `tiffsep_device`, a DeviceN-capable printer with TIFF state for one composite CMYK output plus per-separation TIFF states/files, `gs_devn_params`, and equivalent CMYK color parameters for spot colors.
- Provides GC enumeration/relocation for dynamically stored separation-name data.
- Builds an extended device-procedure table supporting DeviceN component lookup, encode/decode, color mapping procs, and spot equivalent-color updates.
- Maps gray/RGB/CMYK source color spaces into DeviceN component arrays using separation-order maps.
- Encodes color components into `gx_color_index` with configurable bits per component and decodes them back in reverse component order.
- Gets/puts DeviceN printer parameters through the shared `devn_*` helpers, allowing separation names/order and spot equivalent data.
- Creates output separation file names by appending the standard colorant name or generated `sN` spot name plus `.tif` to the base output name; raw separation-name escaping is noted but disabled.
- Determines how many separations to output from device component limits, standard CMYK components, requested `SeparationOrder`, and spot-color count.
- Builds component-to-separation maps and CMYK-equivalent maps for process and spot colors.
- `tiffsep_print_page` writes a composite CMYK TIFF page, opens/reuses per-separation grayscale TIFF files, writes one grayscale separation file per selected component, builds a CMYK-equivalent raster line, then finalizes all strip/page metadata.
- `tiffsep_prn_close` closes any separation files left open across pages.

Dependencies:
- Uses `gdevprn.h`, `gdevtifs.h`, `gdevdevn.h`, and `gsequivc.h`.
- Depends on DeviceN/separation helpers, equivalent CMYK color updates, Ghostscript printer raster access, and the shared TIFF writer.

Research notes:
- `tiffsep` can accept more spot colors than it can image in one pass; users can use `SeparationOrder` across multiple passes to emit more than the component limit.
- Separation file naming deliberately avoids raw spot names by default because operating systems restrict filename characters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtsep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.c

Implements shared utility code and default Ghostscript device procedures for high-level “vector” output devices.

Key behavior:
- Publishes GC structure descriptors for vector devices and vector image enumerators.
- Provides default `setflat`, path writing, and rectangle writing implementations for vector-device procedure tables.
- `gdev_vector_dopath` enumerates Ghostscript paths, optimizes rectangular paths through `dorect` when possible, optionally merges collinear line segments, avoids isolated `moveto` fills that trigger Acrobat Reader artifacts, and emits begin/move/line/curve/close/end callbacks.
- `gdev_vector_init` and `gdev_vector_reset` initialize cached graphics state, saved high-level fill/stroke colors, clipping IDs, scale, page state, and cached black/white colors.
- `gdev_vector_open_file_options` opens OutputFile as seekable or sequential, allocates stream buffer/stream state, optionally opens a bbox tracking device, and makes stream close flush rather than close the underlying file.
- `gdev_vector_stream` lazily calls the device `beginpage` callback on first page output.
- Updates cached logical operation, fill color, stroke color, flatness, dash, linewidth, line cap/join, and miter limit only when changed.
- `gdev_vector_stroke_scaling` computes a scalar stroke scale for uniform CTMs or a normalized matrix for anisotropic CTMs.
- Provides helpers for writing polygons, rectangles, clip paths, and clip-path updates from either path-valid clips or rectangular clip lists.
- `gdev_vector_close_file` frees bbox/stream resources and closes the underlying Ghostscript output file, reporting I/O errors.
- `gdev_vector_begin_image` initializes shared image-enumerator state, updates log-op/clip/fill color as needed, and forwards image bounds to the optional bbox device.
- `gdev_vector_end_image` can pad missing image rows, forwards image end to the bbox device, and frees the image enumerator.
- `gdev_vector_get_params`/`put_params` expose `OutputFile`, reject unsafe filename changes after output has begun, and reopen output when allowed.
- Default fill/stroke/trapezoid/parallelogram/triangle device procedures translate raster-ish operations into vector path callbacks where possible, otherwise fall back to Ghostscript defaults.

Dependencies:
- Uses Ghostscript math, memory, platform file, parameter, path, clipping, imager-state, color, stream, and bbox-device APIs.
- Implements the interface declared in `gdevvec.h`.

Research notes:
- This is a framework file: concrete vector formats supply `gx_device_vector_procs`, while this file handles state caching and common geometry conversion.
- In `gdev_vector_stroke_path`, anisotropic scaling is detected, but the default `dopath` call still passes `NULL` for the matrix, making fallback behavior important for cases requiring CTM rewriting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.h

Declares the shared Ghostscript framework for devices that emit high-level/vector drawing commands rather than pure raster output.

Key behavior:
- Documents the intent of “vector” devices: output command streams such as PDF, PostScript, PCL XL, HP-GL/2, CGM, Windows Metafile, or PICT, while still possibly handling text and raster images.
- Defines output filename and dash-pattern limits.
- Defines `gx_path_type_t` flags for fill/stroke/clip, winding/even-odd rule, path optimization, and always-close behavior.
- Defines `gx_rect_direction_t` for rectangle path ordering.
- Defines `gx_device_vector_procs`, the callback table for page begin, graphics-state changes, color changes, path emission, and rectangle/path default hooks.
- Declares default callback implementations `gdev_vector_setflat`, `gdev_vector_dopath`, and `gdev_vector_dorect`.
- Defines `gx_device_vector_common`, extending a device with memory, vector callbacks, output file/stream state, cached imager state, dash cache, saved high-level colors, clipping IDs, fill/stroke options, coordinate scale, page state, optional bbox device, and cached black/white colors.
- Provides initial values and GC descriptor macros for vector devices.
- Declares file/stream opening options for ASCII, sequential output, sequential fallback, and bbox tracking.
- Declares state update helpers for log-op, fill color, fill preparation, stroke preparation, stroke scaling, path writing, polygon/rectangle writing, clip-path writing/updating, and file close.
- Defines common image-enumerator fields and declares begin/end image helpers.
- Declares default device procedures for `OutputFile` parameters and common fill/stroke geometry operations.

Dependencies:
- Includes `gp.h`, `gsropt.h`, `gxdevice.h`, `gdevbbox.h`, `gxiparam.h`, `gxistate.h`, `gxhldevc.h`, and `stream.h`.

Research notes:
- The header is the contract concrete vector devices implement; procedure comments specify which callbacks each helper may invoke.
- The embedded state cache is central to avoiding redundant commands in generated vector output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvglb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvglb.c

Implements the `vgalib` console display device for 386 PC systems using Linux/SVGAlib-style VGA access.

Key behavior:
- Defines a simple display device with a configurable `DisplayMode` parameter and 16-color focus.
- `vgalib_open` selects the configured/default VGA mode, clears the screen, infers width/height and approximate DPI when unset, and installs 16-color PC palette entries when color is available.
- `vgalib_close` restores text mode.
- RGB/color-index mapping delegates to the PC 4-bit palette helpers.
- `vgalib_fill_rectangle` clips the target and draws larger rectangles as horizontal or vertical lines, using point drawing only for very small rectangles.
- `vgalib_tile_rectangle` pre-clears fully opaque tiles before delegating to the default tiler.
- `vgalib_copy_mono` handles transparent/opaque zero/one colors, optional inversion, and bit-by-bit pixel drawing.
- `vgalib_copy_color` handles 4-bit color pixel maps nibble-by-nibble, or delegates to mono copy on monochrome devices.
- `vgalib_get_bits` reads pixels back with `vga_getpixel` and packs them according to device depth.
- `vgalib_get_params`/`put_params` expose `DisplayMode`; changing the mode closes the open device so it can be reopened with the new mode.

Dependencies:
- Uses Ghostscript device/color/parameter APIs plus `<vga.h>` SVGAlib functions such as `vga_setmode`, `vga_clear`, `vga_getcolors`, `vga_setpalette`, `vga_drawline`, `vga_drawpixel`, and `vga_getpixel`.

Research notes:
- The file states it only supports 16-color modes.
- This is another hardware/display backend inside the Ghostscript source tree, not Plan 9 filesystem or kernel logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevvglb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwddb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwddb.c

Implements the `mswin` Microsoft Windows 3.x display device using a device-dependent bitmap (DDB) backing store.

Key behavior:
- Defines a Windows display device with bitmap/DC handles, dynamic pens/brushes, a palette, and a small monochrome staging bitmap/DC used for `copy_mono`.
- `win_ddb_open` delegates common window setup to `win_open`, rejects depths above 8 bits per pixel, allocates the backing bitmap, creates the mono staging bitmap, builds the palette, creates pens/brushes, and routes text drawing to the bitmap DC.
- `win_ddb_close` destroys tools, DCs, bitmaps, palette resources, palette memory, and then closes the common window device.
- `win_ddb_map_rgb_color` delegates to common Windows palette mapping and mirrors newly added colors into the DDB palette and tool set.
- `win_ddb_fill_rectangle` uses `PatBlt`, special-casing black and otherwise selecting a cached brush.
- `win_ddb_tile_rectangle` pre-clears fully opaque tiles and has a fast path for small 1-bit tiles that fit the staging bitmap with zero phase.
- `win_ddb_copy_mono` clips, chunks transfers to the 32x32 staging bitmap, handles transparent/opaque colors through Windows raster ops, caches bitmap IDs, packs source rows, and blits to the backing DC.
- `win_ddb_copy_color` draws 8-bit or 4-bit indexed pixels with `SetPixel`, or delegates monochrome color maps to `copy_mono`.
- `win_ddb_copy_to_clipboard` copies the backing bitmap and palette to the Windows clipboard.
- `win_ddb_repaint` blits from the backing DC to the requested screen DC.
- `win_ddb_alloc_bitmap` creates a compatible bitmap/DC, halving resolution up to four times if bitmap allocation fails.
- Internal helpers create/delete per-palette pens and brushes.

Dependencies:
- Uses `gdevmswn.h`, Ghostscript Windows common device helpers, Windows GDI handles/APIs, palette helpers, and Ghostscript memory allocation.

Research notes:
- This driver is limited to 8-bit-and-below indexed/palette display modes.
- The resolution-halving fallback changes device dimensions when the backing bitmap cannot be allocated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwddb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwdib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwdib.c

Implements the `mswindll` Microsoft Windows Ghostscript DLL display device using a DIB-style memory device backing store.

Key behavior:
- Defines a Windows DIB device that wraps a Ghostscript memory device, global-memory backing allocation, optional Win32 mutex, lock count, and 16-bit Windows segment bookkeeping when needed.
- `win_dib_open` performs common window setup, creates a mutex on non-Win32s Win32 systems, validates memory-device support for the selected depth, allocates the backing bitmap, and notifies the DLL callback of device creation and size.
- `win_dib_get_initial_matrix` uses a lower-left origin with positive Y scaling, unlike most display devices.
- `win_dib_close` locks the device during close notification, frees the bitmap, closes the mutex, and delegates common window close.
- Drawing operations forward fill, mono copy, and color copy into the wrapped memory device, splitting operations at 64K segment boundaries for 16-bit builds.
- `win_dib_get_bits` delegates scan-line readback to the memory device; `win_dib_put_params` locks the device while common Windows parameters are updated.
- Exports DLL APIs to copy the full DIB (`gsdll_copy_dib`), copy the palette (`gsdll_copy_palette`), draw a source rectangle to a caller-supplied HDC (`gsdll_draw`), lock/unlock the device (`gsdll_lock_device`), and expose bitmap header/palette/row pointers (`gsdll_get_bitmap_row`).
- `win_dib_repaint` builds a `BITMAPINFO` header and uses `SetDIBitsToDevice`, including 15-bit and 16-bit bitfield masks and chunking transfers above roughly 2 MB.
- `win_dib_make_dib` constructs a global-memory DIB copy for a requested rectangle, including bitmap header, RGB palette or bitfield masks, and padded scan-line data.
- `win_dib_alloc_bitmap` sizes the memory-device width to avoid segment crossings on 16-bit builds, allocates global memory for raster data and line pointers, aligns the base, initializes the memory device, and sends size notifications.
- `win_dib_free_bitmap` unlocks and frees the global backing allocation.
- `win_dib_lock_device` uses a mutex on modern Win32 or a counter on Win16/Win32s to prevent resizing while callers inspect bitmap memory.

Dependencies:
- Uses `gdevmswn.h`, `gxdevmem.h`, `gsdll.h`, `gsdllwin.h`, Windows global memory/GDI APIs, Ghostscript memory devices, and common Windows Ghostscript callback/palette helpers.

Research notes:
- The file supports both Win32 and segmented 16-bit Windows memory constraints, which explains much of the block-splitting and alignment logic.
- The DLL row-access API intentionally avoids making a second full bitmap copy when callers only need structured access to rows.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwdib.c -->