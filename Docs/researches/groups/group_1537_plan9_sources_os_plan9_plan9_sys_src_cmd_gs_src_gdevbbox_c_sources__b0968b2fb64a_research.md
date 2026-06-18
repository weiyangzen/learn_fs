# Group Research: group_1537_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevbbox_c_sources__b0968b2fb64a

Scope checked against `Docs/research_subset_a.md`: all listed files are under `sources/os/plan9/plan9`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.c

Ghostscript bounding-box accumulator device. It can run as a standalone `bbox` device that prints page bounding boxes at page output, or as a forwarding wrapper around another target device while tracking the painted extent.

Key behavior:
- Defines `gs_bbox_device` as an 8-bit gray, high-resolution pseudo-device sized near the fixed-point coordinate limit.
- Maintains a `gs_fixed_rect bbox`, mapped black/white/transparent colors, and pluggable box procedures for init/get/add/in-rect.
- `gx_device_bbox_init` clones the bbox prototype, optionally attaches a target, fills forwarding procedures, and redirects color/page-device operations to the target.
- `bbox_open_device` initializes the box and optionally opens the target; `bbox_close_device` optionally closes the target and frees compositor-created wrappers.
- `bbox_output_page` prints `%%BoundingBox` and `%%HiResBoundingBox` for standalone use, then forwards page output.
- Low-level drawing hooks update the accumulated box for rectangles, mono/color/alpha copies, strip tiles, ROP copies, trapezoids, parallelograms, triangles, and thin lines.
- High-level path hooks try to use path/stroke extents directly when unclipped, but fall back through default rendering with `target = NULL` when clipping means the exact bbox must be derived from generated pieces.
- Image handling wraps the target image enumerator, forwards image data, computes transformed source-row bounds, and handles clipping by drawing two triangles through a clip device.
- `bbox_create_compositor` creates a target compositor and wraps it in another bbox device that forwards bbox updates into the original accumulator.
- `bbox_text_begin` uses default text handling and adjusts the text enumerator imaging device when forwarding.

Notable dependencies:
- Core Ghostscript device and forwarding infrastructure: `gxdevice.h`, `gsdevice.h`, `gdevbbox.h`.
- Drawing/color/path/image internals: `gxdcolor.h`, `gxiparam.h`, `gxistate.h`, `gxpaint.h`, `gxpath.h`, `gxcpath.h`.

Research notes:
- This file is a central utility wrapper, not a printer/file-format backend like many neighboring `gdev*` files.
- White can be treated as transparent or opaque through `WhiteIsOpaque`; page-sized erases reinitialize the bbox unless white is opaque.
- The file exposes `PageBoundingBox` through device parameters and accepts a written bbox back through `put_params`.
- There is a likely typo in `bbox_draw_thin_line`: the forwarded target call passes `(fx0, fy0, fx1, fy0, ...)`, using `fy0` for both endpoints instead of `fy1`. Bounding-box accumulation still uses `fy1`, so forwarding and measured output can diverge.
- The image-row bbox logic advances by the submitted `height`, relying on the target enumerator's row consumption behavior. If partial consumption differs from `height`, this may over-accumulate, though overestimation is safer than underestimation for bbox use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.h

Public interface and structure definition for Ghostscript's bounding-box accumulator device.

Key contents:
- Documents two usage modes: standalone `bbox` output device and embedded C component in a device pipeline.
- Declares `gx_device_bbox_procs_t`, a virtual procedure table for bbox initialization, retrieval, rectangle addition, and containment tests.
- Declares default implementations: `bbox_default_init_box`, `bbox_default_get_box`, `bbox_default_add_rect`, and `bbox_default_in_rect`.
- Defines `gx_device_bbox_common`, embedding forwarding-device state plus bbox-specific fields: standalone/forward-open-close flags, box procedures, box procedure data, white-opacity mode, current bbox, mapped black/white, and transparent color.
- Declares GC descriptor support through `public_st_device_bbox`.
- Exposes lifecycle/configuration APIs:
  - `gx_device_bbox_init`
  - `gx_device_bbox_fwd_open_close`
  - `gx_device_bbox_set_white_opaque`
  - `gx_device_bbox_bbox`
  - `gx_device_bbox_release`

Notable dependencies:
- Requires Ghostscript core device definitions from `gxdevice.h` before inclusion.
- Uses Ghostscript fixed-point geometry and memory/device types.

Research notes:
- The header explicitly notes that bbox devices unusually may propagate `open_device` and `close_device` to their target.
- `gx_device_bbox_bbox` reports in 1/72 inch user units, not raw fixed device pixels.
- The virtual bbox procedure table supports subclass/compositor sharing, which is used by `gdevbbox.c` for composited forwarding devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbit.c

Ghostscript "plain bits" printer devices used mostly to measure rendering time or dump raw rendered pixels without a real output format.

Key behavior:
- Defines three devices:
  - `bit`: 1-bit monochrome raw bits.
  - `bitrgb`: RGB raw bits.
  - `bitcmyk`: CMYK raw bits.
- Device procedures use normal printer open/output/close, custom color mapping, parameter handling, and a simple `bit_print_page`.
- `bit_print_page` copies each rendered scanline and writes the raw raster bytes directly to `OutputFile`; if the filename is `nul`, it skips writes to measure rendering without I/O.
- `bit_get_params` temporarily restores the real component count, delegates printer parameters, publishes a sample default CRD, and exposes `ForceMono`.
- `bit_put_params` accepts `GrayValues`/`RedValues`/`GreenValues`/`BlueValues` to derive bits per component, supports `ForceMono`, updates `color_info`, closes the device on depth/component changes, and resets CMYK mapping hooks.
- `bit_mono_map_color`, `bit_map_color_rgb`, and `bit_map_cmyk_color` encode/decode gray/RGB/CMYK values across supported depths.

Notable dependencies:
- Ghostscript printer APIs: `gdevprn.h`.
- Parameter/color rendering helpers: `gsparam.h`, `gscrd.h`, `gscrdp.h`, `gdevdcrd.h`, `gxlum.h`.

Research notes:
- The `REAL_NUM_COMPONENTS` macro derives intended component count from the device name character after `bit`, so adding new bit devices requires updating that macro.
- The raw output has no file header, dimensions, or byte-order metadata; it is a diagnostic/rendering benchmark backend rather than an interchange format.
- The depth selection table permits high component depths such as 12 and 16 bits where supported by the color model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbj10.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbj10.c

Ghostscript Canon Bubble Jet BJ-10e/BJ-200/BJ-300 family printer driver.

Key behavior:
- Defines `gs_bj200_device` and `gs_bj10e_device`, both monochrome 360 DPI printer devices sharing `bj10e_print_page`.
- `bj200_open` and `bj10e_open` set margins based on A4 vs letter width and model-specific top/bottom constraints, then open the printer.
- `bj10e_print_page`:
  - Allocates input scanline and transposed output buffers.
  - Sends BJ initialization commands, disables automatic carriage return, sets vertical spacing, and sets printable page length.
  - Scans for blank lines and emits vertical skip commands.
  - Transposes raster data in 8-line blocks into printer head-column format using `gdev_prn_transpose_8x8`.
  - Aligns the last pass so the print head does not move below the bottom printable margin.
  - Coalesces blank and non-blank horizontal column groups, emits horizontal skip/data commands, and sends form feed at page end.

Notable dependencies:
- Uses only the Ghostscript printer device API from `gdevprn.h`.

Research notes:
- The long comments document hardware DIP-switch behavior, paper-size assumptions, and BJ-300 Proprinter-mode use.
- `USE_FACTORY_DEFAULTS` changes reset behavior for letter vs A4 paper, but is disabled by default because factory defaults may differ by market/model.
- The code carefully models physical head constraints: 64 jets exist but only 48 are used per strip, which affects effective bottom margin.
- Memory cleanup is centralized through `fin`, so allocation and scanline errors release buffers before returning.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbj10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjc.h

Configuration header for older Canon BJC printer drivers, especially BJC-600 and BJC-800 style devices.

Key contents:
- Defines driver names and version strings for `bjc600` and `bjc800`.
- Defines print-limit and margin constants, including optional recommended/tight margin modes.
- Defines BJC head-row count and media-weight thresholds.
- Provides margin macros for letter, A4, and A3.
- Defines public parameter names such as `ManualFeed`, `DitheringType`, `MediaType`, `MediaWeight`, `PrintQuality`, `ColorComponents`, `PrintColors`, and `MonochromePrint`.
- Enumerates media types, dithering modes, quality modes, printable color bitmasks, and base resolutions.
- Supplies generic defaults and per-model defaults for media, quality, dithering, manual feed, monochrome mode, resolution, bits per pixel, component count, print colors, and media weight.

Notable dependencies:
- This is a macro-only header and does not include other headers directly.

Research notes:
- There is a typo/inconsistency in the inner include guard: `#ifndef _GDEV_BJC_H` is followed by `#define _GDEV_CDJ_H`, so `_GDEV_BJC_H` is never actually defined. The outer `gdevbjc_INCLUDED` guard prevents repeat inclusion in normal use, but the inner guard is ineffective.
- The defaults intentionally allow compile-time override by defining `BJC_DEFAULT_*` or model-specific `BJC600_DEFAULT_*`/`BJC800_DEFAULT_*` macros before inclusion.
- The file distinguishes `ColorComponents` from `BitsPerPixel`, warning that changing one requires a compatible change to the other.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.c

Implementation of a small Canon BJC command-generation library. It serializes BJC escape commands to a Ghostscript `stream`.

Key behavior:
- Utility helpers write bytes, high/low and low/high 16-bit fields, and generic ESC-command envelopes.
- Emits single-character commands: LF, FF, CR.
- Emits session commands: initialize/reset, set initial condition, compression, print method, short print method, media supply, and cartridge identification.
- Emits page commands: page margins, extended margins, and page ID.
- Emits image commands: raster resolution, raster skip, CMYK image data, move lines, move-line unit, image format, continue image, and indexed image.

Notable dependencies:
- Includes `std.h` and the public BJC command interface `gdevbjcl.h`.
- Uses Ghostscript stream output APIs: `spputc` and `sputs`.

Research notes:
- The implementation is deliberately thin and generally trusts callers to pass valid values/ranges documented in the header.
- Several implementation names do not match prototypes in `gdevbjcl.h`: the source defines `bjc_put_set_initial` and `bjc_put_set_compression`, while the header declares `bjc_put_initial_condition` and `bjc_put_compression`. Unless macros elsewhere bridge these names, this is an API mismatch.
- The header declares `bjc_put_photo_image`, but this file does not implement it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.h

Public interface for the Canon BJC command-generation library.

Key contents:
- Defines capability bits for BJC model command support, including single-character, session, page, resolution, and image capabilities.
- Defines capability masks for known models: 50, 70, 80, 210, 250, 610, 620, 4000, 4100, 4200, 4300, 4550, 4650, 5500, and 7000.
- Provides `BJC_ENUMERATE_OPTIONS(m)` to generate model/capability tables.
- Declares command emitters for CR/FF/LF, initial condition, initialize, print method, media supply, cartridge identification, page margins, raster compression/resolution/skip, CMYK image data, movement, image format, photo image, continuation image, and indexed image.
- Defines enums for print color, media, quality, black density, short print methods, media supply, media type, cartridge commands, raster compression, CMYK image component, image format, and ink system.

Notable dependencies:
- Includes `<stdio.h>` as a patch for `stream.h`, then includes Ghostscript `stream.h`.

Research notes:
- The header documents that the library is preliminary and not every printer supports every command.
- It includes many model-specific notes where numeric enum values mean different things for different printer families.
- The header/source pair is inconsistent for at least initial-condition and compression function names, and the header declares a photo-image function not present in the implementation read in this group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.c

Ghostscript synchronous BMP file output devices.

Key behavior:
- Defines BMP devices:
  - `bmpmono`: 1-bit monochrome.
  - `bmpgray`: 8-bit grayscale with fixed 256-gray palette.
  - `bmpsep1`: separated CMYK, 1 bit per plane.
  - `bmpsep8`: separated CMYK, 8 bits per plane.
  - `bmp16`: 4-bit EGA/VGA-style color.
  - `bmp256`: 8-bit 3-3-2 palette color.
  - `bmp16m`: 24-bit color using BGR byte order.
  - `bmp32b`: 32-bit CMYK-like output outside the BMP specification.
- `bmp_print_page` writes a BMP header, then writes rows bottom-to-top with 32-bit row padding.
- `bmp_cmyk_print_page` writes four separate BMP images, one per CMYK plane, each bottom-to-top, using render-plane extraction.

Notable dependencies:
- Ghostscript printer APIs: `gdevprn.h`.
- PC color mapping helpers: `gdevpccm.h`.
- Shared BMP helpers from `gdevbmp.h` / `gdevbmpc.c`.

Research notes:
- Multi-plane separated CMYK output concatenates multiple BMP image streams into one output file; many ordinary BMP readers will only display the first.
- The synchronous path allocates only one padded row buffer and streams output directly.
- BMP row padding bytes are zeroed once after allocation; the image copy fills only active raster bytes for each row.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.h

Shared BMP output declarations for Ghostscript BMP devices.

Key contents:
- Defines default BMP device resolution as 72 DPI in both axes.
- Declares `write_bmp_header` for standard BMP output.
- Declares `write_bmp_separated_header` for separated CMYK plane BMP output.
- Declares 24-bit color mapping procedures:
  - `bmp_map_16m_rgb_color`
  - `bmp_map_16m_color_rgb`

Notable dependencies:
- Assumes Ghostscript printer and device procedure types are already visible to the including compilation unit.

Research notes:
- This header contains only shared definitions; device descriptors live in `gdevbmp.c` and async variants in `gdevbmpa.c`.
- The 24-bit mapper explicitly supports BMP's BGR byte ordering through its implementation in `gdevbmpc.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpa.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpa.c

Async-rendering demonstration version of the BMP output drivers. It mirrors the synchronous BMP devices but uses Ghostscript's async printer/clist machinery to overlap interpretation and rendering.

Key behavior:
- Defines `gx_device_async`, extending printer device state with `UsePlanarBuffer`, `buffered_page_exists`, and per-plane file offsets.
- Defines async BMP devices for mono, separated CMYK 1/8-bit, 4-bit, 8-bit, 24-bit, and 32-bit CMYK-like output.
- `bmpa_open_writer` installs async render procedures, parameter hooks, hardware-param hook, output-page hook, space-parameter hook, and optional planar buffering, then opens with `gdev_prn_async_write_open`.
- `bmpa_reader_start_render_thread` launches the render thread through `gp_create_thread`.
- `bmpa_reader_output_page` opens the output as positionable so the renderer can seek back and update already written BMP data.
- `bmpa_reader_print_planes` writes headers, records the data offset, and writes rendered rows bottom-to-top for either normal or separated-plane output.
- `bmpa_reader_buffer_planes` reopens existing BMP raster data, reads bands back into a buffer device, renders additional clist content over it, and writes updated bands back in place.
- `bmpa_get_space_params` computes band buffer sizes for async writer/reader compatibility, then forces buffer and band-buffer space to match.
- `bmpa_get_params`/`bmpa_put_params` expose planar-buffer behavior through printer parameter helpers.
- `bmpa_get_hardware_params` returns a test-only `TestValue`.

Notable dependencies:
- Async printer/clist APIs: `gdevprna.h`, `gdevppla.h`, `gpsync.h`.
- BMP helpers: `gdevbmp.h`.
- PC color mapping helpers: `gdevpccm.h`.

Research notes:
- The file is explicitly a demo of async rendering, not just another BMP writer.
- Positionable output is required; non-seekable streams would not support the buffered-page overlay path.
- The comments explain Ghostscript clist memory sizing in unusual detail and are a useful reference for async printer driver construction.
- `SINGLE_PAGE` can be enabled to discard all but the first page, but is disabled because Ghostscript may write multiple BMP streams even though many viewers only process the first.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpc.c

Shared BMP file-format utility implementation for Ghostscript BMP devices.

Key behavior:
- Defines local BMP file header, info header, and RGB quad structures, with explicit little-endian assignment macros for big-endian hosts.
- `write_bmp_depth_header` writes the `BM` signature, file header, info header, optional palette, image dimensions, row stride, pixel depth, and resolution in pixels per meter.
- `write_bmp_header` builds a palette for depths up to 8 bits by calling the device's color decode routine, then delegates to `write_bmp_depth_header`.
- `write_bmp_separated_header` builds a grayscale inverted palette for a single CMYK separation plane.
- `bmp_map_16m_rgb_color` and `bmp_map_16m_color_rgb` encode/decode 24-bit BMP color indexes in Windows BGR byte order.

Notable dependencies:
- Ghostscript printer/device APIs through `gdevprn.h`.
- Declarations from `gdevbmp.h`.

Research notes:
- The file explicitly avoids including the `BM` bytes inside `bmp_file_header` because compiler padding could shift the following 32-bit field.
- Palette writing uses `fwrite` but does not check its return value, unlike the fixed headers.
- 32-bit CMYK-like output is supported by callers but is outside standard BMP semantics; this utility only writes an uncompressed BMP-style header for the given depth.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevccr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevccr.c

Ghostscript CalComp Raster Format output driver.

Key behavior:
- Defines one `ccr` device, defaulting to 300 DPI A3-sized output with 0.2 inch margins and 3 one-bit CMY components.
- Custom RGB-to-color mapping converts RGB to a 3-bit CMY bitmap.
- `ccr_print_page` allocates a row buffer for every page row plus per-row C/M/Y buffers, converts each rendered input byte group into packed C, M, and Y pass data, then writes the output as three passes: Y, M, C.
- CalComp output commands include file start/end, new pass, empty line, and line-start-with-length markers.
- Helper routines allocate/free row buffers, append packed CMY bytes while tracking effective nonzero length, and write each color pass.

Notable dependencies:
- Uses Ghostscript printer APIs from `gdevprn.h`.

Research notes:
- The implementation stores all page rows before writing passes, so memory usage scales with page height and width rather than streaming one row at a time.
- `alloc_line` allocates each plane buffer with `cols` bytes even though packed output advances one byte per 8 pixels, overallocating by roughly 8x but simplifying allocation.
- The color decode routine appears to place red/blue values in reversed indexes relative to the usual `rgb[0]`, `rgb[1]`, `rgb[2]` convention; this may be harmless if rarely used, but it is suspicious.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevccr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcd8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcd8.c

Large Ghostscript HP Color DeskJet driver for `cdj670`, `cdj850`, `cdj890`, and `cdj1600` devices. It handles printer-specific setup, color calibration, CMYK/CMY mapping, gray component replacement, Floyd-Steinberg dithering, resolution scaling, and PCL raster compression.

Key behavior:
- Defines calibration/config data:
  - `hp850_cmyk_init` raster configuration bytes.
  - Gamma/calibration tables for HP 850-style and 890-style behavior.
  - Black-correction lookup generation.
- Defines `gx_device_cdj850`, which extends printer state with CMYK capability, default depth, quality, paper type, intensity count, scaling flags, printer type, compression mode, gamma values, black correction, and function pointers for printer-specific start/print/terminate routines.
- Exports devices:
  - `gs_cdj670_device`: 600 DPI CMYK-style device.
  - `gs_cdj850_device`: 600 DPI CMYK-style device.
  - `gs_cdj890_device`: 600 DPI CMYK-style device.
  - `gs_cdj1600_device`: 300 DPI CMY/PCL-style device.
- `hp_colour_open` sets color parameters if needed, chooses effective resolution/scaling/intensity based on printer type, paper type, and quality, sets paper margins, then opens the printer.
- `cdj850_get_params`/`cdj850_put_params` expose `Quality`, `Papertype`, `MasterGamma`, per-channel gamma values, `BlackCorrect`, and `BitsPerPixel`.
- `cdj850_print_page` copies gamma tables locally, optionally applies gamma transforms, computes black correction, calculates a single large work buffer, initializes internal pointer slices, starts raster mode, sends scanlines, terminates the page, and frees storage.
- `send_scan_lines` skips blank lines, handles y-scaling and two-pass color timing, and dispatches nonblank rows to the device-specific line printer.
- `cdj850_print_non_blank_lines` performs gray component replacement, black-plane dithering, mode-9 compressed black output, color-plane rescaling, color dithering, and compressed C/M/Y plane output.
- `cdj1600_print_non_blank_lines` copies 24-bit color input into the color buffer, dithers CMY planes, and outputs mode-3 compressed planes.
- `do_gcr` performs gray component replacement and applies C/M/Y/K calibration lookup tables.
- `FSDlinebw`, `FSDlinec2`, `FSDlinec3`, and `FSDlinec4` implement bidirectional Floyd-Steinberg dithering for black and color planes with two, three, or four intensity levels.
- Rescale functions average color data for 1x/2x in X and Y so black and color planes can run at different resolutions.
- `cdj_set_bpp` and `cdj_put_param_bpp` manage accepted bit depths, process color model changes, color component counts, mapping procedure changes, and device close/reopen needs.
- PCL setup differs between the DeskJet 850-style path and the `cdj1600` path, including PJL/PCL entry for `cdj1600`.

Notable dependencies:
- Ghostscript printer and PCL APIs: `gdevprn.h`, `gdevpcl.h`.
- Parameter API: `gsparam.h`.
- Luminance helpers: `gxlum.h`.
- PCL compression helpers: `gdev_pcl_mode9compress` and `gdev_pcl_mode3compress`.

Research notes:
- This is printer/raster code, not filesystem logic, but it is in the included Plan 9 Ghostscript source tree.
- The driver keeps extensive legacy comments about printer model support, quality/paper switches, gamma usage, and performance costs of 600 DPI color rendering.
- Work memory is manually partitioned from a single allocation; correctness depends on `calculate_memory_size` matching every pointer slice in `init_data_structure`.
- The code uses the `scan` variable both for bidirectional dithering direction and alternating compression buffers; comments call out this overload explicitly.
- `cdj850_get_params` writes `MasterGamma` from `cdj850->gammavalc` rather than `cdj850->mastergamma`, which looks like a parameter reporting bug.
- `cdj850_put_params` documents `Quality` as `-1,0,1`, but validates it with minimum `0`, so `DRAFT = -1` cannot be set through this path despite comments.
- `gdev_cmyk_map_cmyk_color` assigns `yellow = cmyk[3]` and `black = cmyk[4]`, which is suspicious for a four-component CMYK array and may be an out-of-bounds/indexing bug unless this old Ghostscript calling convention supplies a different layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcd8.c -->