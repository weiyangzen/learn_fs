# Group Research: group_99_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevbbox_c_sources__1b48f959a214

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.c

## Purpose
Implements Ghostscript’s `bbox` device, a forwarding or stand-alone device that accumulates the drawn page bounding box. In stand-alone mode it prints `%%BoundingBox` and `%%HiResBoundingBox`; in pipeline mode it forwards rendering to a target while tracking drawing extents.

## Main Interfaces
- Defines the public `gs_bbox_device` prototype.
- Implements default bbox proc set: `bbox_default_init_box`, `bbox_default_get_box`, `bbox_default_add_rect`, `bbox_default_in_rect`.
- Implements exported helpers declared in `gdevbbox.h`: `gx_device_bbox_init`, `gx_device_bbox_fwd_open_close`, `gx_device_bbox_set_white_opaque`, `gx_device_bbox_bbox`, `gx_device_bbox_release`.
- Overrides many device drawing procedures: rectangle fill, mono/color/alpha copy, path fill/stroke, masks, trapezoids, parallelograms, triangles, thin lines, strip tiling/ROP, typed images, compositors, and text.

## Behavior
- Stores accumulated extents in fixed device coordinates, then converts them back to 1/72 inch user-style coordinates in `gx_device_bbox_bbox`.
- Treats white as transparent unless `WhiteIsOpaque` is set, using `transparent` to suppress bbox growth for transparent/white fills.
- Full-page rectangle or strip-tile operations call `BBOX_INIT_BOX`; this can reset the bbox on page erases depending on transparency/white behavior.
- If a target exists, most operations first forward to the target, then update the bbox.
- For clipped high-level operations, it temporarily sets `bdev->target = NULL` and asks default Ghostscript drawing routines to decompose the drawing through the clipping path so the bbox is accurate.
- For unclipped paths/images, it often uses path/image transformed bounding boxes directly for speed.
- Typed image handling wraps a target image enumerator and accumulates the transformed bbox for each image data chunk.
- Compositor creation wraps target compositor devices with a new bbox forwarding device that shares the original bbox accumulator.
- `bbox_text_begin` uses the default text path but points the text enumerator’s imaging device back at the bbox device when forwarding.

## Parameters
- `get_params` reports `PageBoundingBox` and `WhiteIsOpaque`.
- `put_params` accepts `PageBoundingBox` to seed/reset the accumulator and `WhiteIsOpaque` to change transparency semantics, then forwards other parameters.

## Dependencies
Uses Ghostscript core device, path, clip, image, imager, and drawing-color APIs: `gxdevice.h`, `gsdevice.h`, `gxdcolor.h`, `gxiparam.h`, `gxistate.h`, `gxpaint.h`, `gxpath.h`, `gxcpath.h`.

## Notes
- The bbox device uses a very high default resolution and huge page coordinate range to avoid limiting real-device jobs.
- There is a suspicious call in `bbox_draw_thin_line`: the target call passes `fx0, fy0, fx1, fy0` rather than `fx0, fy0, fx1, fy1`; this may be intentional legacy behavior or a typo worth verifying before modifying.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.h

## Purpose
Declares the bbox device interface and common structure fields for Ghostscript’s bounding-box accumulator/forwarding device.

## Main Interfaces
- Defines `gx_device_bbox_procs_t`, a virtual proc table for bbox accumulator operations:
  - `init_box`
  - `get_box`
  - `add_rect`
  - `in_rect`
- Declares default implementations for those procs.
- Defines `gx_device_bbox_common`, including forwarding-device fields, bbox procs/data, `white_is_opaque`, current `bbox`, and cached black/white/transparent colors.
- Defines `gx_device_bbox` and its GC descriptor macro `public_st_device_bbox`.

## Exported API
- `gx_device_bbox_init(gx_device_bbox *dev, gx_device *target, gs_memory_t *mem)`
- `gx_device_bbox_fwd_open_close(gx_device_bbox *dev, bool forward_open_close)`
- `gx_device_bbox_set_white_opaque(gx_device_bbox *dev, bool white_is_opaque)`
- `gx_device_bbox_bbox(gx_device_bbox *dev, gs_rect *pbbox)`
- `gx_device_bbox_release(gx_device_bbox *dev)`

## Behavior Contract
- Can be used as a free-standing `bbox` output device or as a component in a forwarding device pipeline.
- Forwarding bbox devices normally propagate open/close to their target, but this can be disabled.
- Non-target bbox devices have an effectively infinite page size; target-backed devices mirror target parameters.
- Custom bbox procs allow subclasses and compositor wrappers to redirect accumulation to shared state.

## Dependencies
Requires `gxdevice.h` and Ghostscript fixed-point/rectangle/device-forwarding types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbit.c

## Purpose
Implements “plain bits” printer devices used to measure rendering/output time by dumping raw rendered raster data.

## Devices
- `gs_bit_device`: monochrome `bit`
- `gs_bitrgb_device`: RGB `bitrgb`
- `gs_bitcmyk_device`: CMYK `bitcmyk`

## Main Behavior
- Uses printer-device infrastructure but does not implement drawing operations directly; rendering happens through the standard printer/memory path.
- `bit_print_page` writes each scan line’s raw bytes to the output file, unless the output filename is `nul`, in which case it skips writes after rendering.
- Supports variable bits per component through parameters like `GrayValues`, `RedValues`, `GreenValues`, and `BlueValues`.
- Supports `ForceMono`, which can force RGB/CMYK devices to behave as 1-component monochrome devices while preserving the real component count internally.

## Color Mapping
- `bit_mono_map_color` maps gray to packed gray/mono output, with inverted 1-bit mono semantics.
- `bit_map_color_rgb` decodes gray, RGB, or CMYK packed color indices back to RGB.
- `bit_map_cmyk_color` packs CMYK component bits into a color index and avoids `gx_no_color_index`.

## Parameters
- `bit_get_params` temporarily restores the real component count before delegating to printer params and exposing `CRDDefault` plus `ForceMono`.
- `bit_put_params` validates component value counts, updates depth/dither info, applies `ForceMono`, closes the device when color layout changes, and resets CMYK mapping procs.

## Dependencies
Uses `gdevprn.h`, `gsparam.h`, CRD helpers, luminance helpers, and device color-rendering defaults.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbj10.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbj10.c

## Purpose
Implements Canon Bubble Jet BJ-10e/BJ-200/BJ-300-style monochrome printer drivers.

## Devices
- `gs_bj200_device`: 360 dpi `bj200`
- `gs_bj10e_device`: 360 dpi `bj10e`

## Main Behavior
- `bj200_open` and `bj10e_open` choose margins based on paper width, distinguishing A4-like and letter-like pages.
- `bj10e_print_page` initializes the printer, disables automatic carriage return, sets vertical spacing and printable page length, then sends raster data in print-head-height strips.
- Output is transposed from scan-line order into column/jet order using `gdev_prn_transpose_8x8`.
- Blank scan lines are skipped with vertical tab commands.
- Blank horizontal column groups are skipped with printer horizontal skip commands.
- The final print pass is aligned so the bottom of the print head reaches the desired bottom margin.

## Printer Protocol
- Uses ESC/P-style BJ commands:
  - reset/set initial conditions
  - disable automatic CR
  - vertical spacing
  - page length
  - vertical/horizontal skips
  - raster graphics transfer
  - form feed

## Notes
- The large comments document BJ200 factory defaults, DIP switch implications, BJ300 compatibility, and margin behavior.
- `USE_FACTORY_DEFAULTS` can change reset behavior for letter/A4 handling.
- Memory use is limited to one input line buffer and one transposed output strip buffer.

## Dependencies
Uses Ghostscript printer device helpers from `gdevprn.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbj10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjc.h

## Purpose
Defines constants and defaults for older Canon BJC printer drivers, especially BJC-600 and BJC-800 style devices.

## Contents
- Driver names and version strings:
  - `BJC_BJC600`
  - `BJC_BJC800`
- Hardware margin/limit constants, including lower-limit modes controlled by `USE_RECOMMENDED_MARGINS` and `USE_TIGHT_MARGINS`.
- Media weight thresholds.
- Print-head row count.
- Letter/A4/A3 margin macros.
- Public option names such as `ManualFeed`, `DitheringType`, `MediaType`, `PrintQuality`, `ColorComponents`, `PrintColors`, and `MonochromePrint`.
- Enumerated integer values for media types, dithering modes, quality modes, and color component masks.
- Resolution constants based on 90 dpi increments.
- Generic defaults and BJC600/BJC800-specific default overrides.

## Integration Role
This is a configuration header, not an implementation file. It centralizes compile-time defaults for Canon BJC drivers that include it.

## Notes
- Header guard has an apparent typo/inconsistency: `#ifndef _GDEV_BJC_H` followed by `#define _GDEV_CDJ_H`, while the closing comment says `_GDEVBJC_H`.
- Defaults are designed to be overridden by preprocessor defines at build time.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.c

## Purpose
Implements a small command-generation library for Canon BJC-family printer command streams.

## Main Helpers
- `bjc_put_bytes`
- `bjc_put_hi_lo`
- `bjc_put_lo_hi`
- `bjc_put_command`

These write command bytes to Ghostscript `stream` objects with the expected byte ordering.

## Commands Implemented
- Single-byte controls: LF, FF, CR.
- Initialization: return to initial condition and set initial condition.
- Data compression selection.
- Print method selection, short and extended.
- Raster resolution.
- Raster skip.
- Page margins and extended margins.
- Media supply.
- Ink cartridge identification.
- CMYK raster image data.
- Move by raster lines and set movement unit.
- Image format.
- Page ID.
- Continue raster image.
- BJ indexed image.

## Behavior
Each public function emits a concrete BJC escape sequence and payload. The implementation does not validate model capabilities; callers are expected to know which commands a target printer supports.

## Dependencies
Uses `std.h`, `gdevbjcl.h`, and Ghostscript `stream` write helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.h

## Purpose
Declares the Canon BJC command-generation library and printer capability masks.

## Capability Model
- Defines bit flags for optional command support:
  - single-character commands
  - session commands
  - page commands
  - resolution modes
  - image commands
- Defines model capability masks for BJC 50, 70, 80, 210, 250, 610, 620, 4000, 4100, 4200, 4300, 4550, 4650, 5500, and 7000.
- Provides `BJC_ENUMERATE_OPTIONS(m)` to build tables over known models.

## Command API
Declares command emitters for:
- CR, FF, LF
- initialize / initial condition
- print method
- media supply
- identify cartridge
- page margins and extended margins
- page ID
- raster compression
- raster resolution and skips
- CMYK raster image
- move lines and movement unit
- image format and photo image
- continue image
- indexed image

## Types
Defines enums for print color, media, quality, black density, short print modes, media supply/type, cartridge commands, compression, CMYK components, image format, and ink system.

## Notes
- Several comments mark commands as model-specific or “different for 7000”.
- Header declares `bjc_put_initial_condition` and `bjc_put_compression`, while `gdevbjcl.c` implements `bjc_put_set_initial` and `bjc_put_set_compression`; this mismatch is important if these APIs are compiled/linked directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.c

## Purpose
Implements BMP output devices that render Ghostscript pages into BMP-format files.

## Devices
- `bmpmono`: 1-bit mono
- `bmpgray`: 8-bit grayscale
- `bmpsep1`: separated CMYK, 1 bit per plane
- `bmpsep8`: separated CMYK, 8 bits per plane
- `bmp16`: 4-bit EGA/VGA-style color
- `bmp256`: 8-bit 3-3-2 palette color
- `bmp16m`: 24-bit color
- `bmp32b`: 32-bit CMYK, outside standard BMP

## Main Behavior
- `bmp_print_page` writes a normal BMP header, then emits scan lines bottom-to-top as required by BMP.
- Scan lines are padded to 32-bit boundaries.
- `bmp_cmyk_print_page` writes four separate BMP images, one per CMYK plane, using Ghostscript render-plane support.
- Row buffers are allocated per page and freed after output.

## Dependencies
Uses `gdevprn.h`, PC color mappers from `gdevpccm.h`, and shared BMP helpers from `gdevbmp.h` / `gdevbmpc.c`.

## Notes
- Separated CMYK output is represented as multiple grayscale BMP sections in one output stream, which may not be accepted by ordinary BMP viewers as a single conventional image.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.h

## Purpose
Declares shared definitions and helper interfaces for BMP output devices.

## Contents
- Default BMP device resolution: `X_DPI 72`, `Y_DPI 72`.
- `write_bmp_header(gx_device_printer *pdev, FILE *file)`
- `write_bmp_separated_header(gx_device_printer *pdev, FILE *file)`
- 24-bit color mappers:
  - `bmp_map_16m_rgb_color`
  - `bmp_map_16m_color_rgb`

## Integration Role
Included by BMP device implementations to share header writing and 24-bit BGR color packing behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpa.c

## Purpose
Implements asynchronous BMP output devices as a demonstration of Ghostscript async rendering and command-list rendering.

## Devices
- `bmpamono`
- `bmpasep1`
- `bmpasep8`
- `bmpa16`
- `bmpa256`
- `bmpa16m`
- `bmpa32b`

## Device Structure
Defines `gx_device_async`, extending printer-device fields with:
- `UsePlanarBuffer`
- `buffered_page_exists`
- `file_offset_to_data[4]`

## Main Behavior
- Writer open procedures configure async render procs and start the async writer/render setup with `gdev_prn_async_write_open`.
- Render thread entry calls `gdev_prn_async_render_thread`.
- Output opens the printer stream as positionable so the renderer can seek and update partial pages.
- `bmpa_reader_print_planes` writes BMP headers and bottom-to-top raster data, saving data offsets for later overlays.
- `bmpa_reader_buffer_planes` can seek back into an existing BMP data area, read bands into a buffer device, continue rendering over them, and write updated bands back.
- Supports both ordinary BMP output and separated CMYK plane output.

## Parameters
- `bmpa_get_params` and `bmpa_put_params` delegate to planar printer parameter helpers and expose/control `UsePlanarBuffer`.
- `bmpa_get_hardware_params` publishes a test-only `TestValue`.

## Memory/Banding
- `bmpa_get_space_params` computes band dimensions and buffer sizes for async command-list rendering.
- The comments provide an extensive explanation of writer/render buffer partitioning, tile cache size, command buffer sizing, and async reader/writer matching.

## Dependencies
Uses async printer infrastructure from `gdevprna.h`, BMP helpers, PCL/planar printer helpers, synchronization/thread support, and command-list rendering APIs.

## Notes
- The source explicitly warns that multi-page BMP output is technically possible but most BMP consumers display only the first page.
- This file is both a functional driver and a tutorial-style example of async rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpc.c

## Purpose
Provides shared BMP file-format utilities and 24-bit BMP color mappers.

## Main Structures
Defines local BMP-compatible structures:
- `bmp_file_header`
- `bmp_info_header`
- `bmp_quad`

Includes endian-conversion macros so multi-byte BMP fields are written little-endian on both little- and big-endian hosts.

## Header Writing
- `write_bmp_depth_header` writes the `BM` signature, file header, info header, resolution in pixels per meter, and optional palette.
- `write_bmp_header` builds a palette for depths <= 8 by asking the device’s `map_color_rgb` proc, then delegates to `write_bmp_depth_header`.
- `write_bmp_separated_header` builds a grayscale palette for a single separated CMYK plane and writes a BMP header for that plane depth.

## Color Mapping
- `bmp_map_16m_rgb_color` packs RGB as BMP BGR byte order in a color index.
- `bmp_map_16m_color_rgb` decodes that packed value back to RGB.

## Dependencies
Uses Ghostscript printer-device APIs and declarations from `gdevbmp.h`.

## Notes
- BMP scan-line padding is handled by callers and included in header size calculations.
- The header intentionally omits the leading `BM` bytes from `bmp_file_header` to avoid compiler padding issues.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevccr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevccr.c

## Purpose
Implements a CalComp Raster Format printer/output driver named `ccr`.

## Device
- `gs_ccr_device`: A3-sized, 300 dpi, 3-component, 8-bit-depth printer device with 0.2 inch margins.

## Color Mapping
- `ccr_map_rgb_color` reduces RGB to 1-bit-per-component CMY by thresholding the top bit and inverting RGB to CMY.
- `ccr_map_color_rgb` converts packed CMY bits back to full-intensity RGB.

## Output Behavior
- `ccr_print_page` reads every rendered scan line, unpacks pixels into C/M/Y bit bytes, stores all rows in memory, and then writes separate Y, M, and C passes.
- The output stream is wrapped with CalComp control bytes:
  - file start
  - new pass separators
  - line start records
  - empty-line records
  - file end

## Internal Data
`cmyrow` stores per-row buffers and effective lengths for each color pass. Helper routines allocate row buffers, append packed CMY bytes, write each pass, and free allocated memory.

## Dependencies
Uses Ghostscript printer helpers from `gdevprn.h`.

## Notes
- The driver buffers the entire page in memory before writing passes, so memory cost scales with page height and width.
- Allocation failure paths free already allocated line buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevccr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcd8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcd8.c

## Purpose
Implements Ghostscript printer drivers for HP color DeskJet-style devices: `cdj670`, `cdj850`, `cdj890`, and `cdj1600`.

## Devices
- `gs_cdj670_device`: 600 dpi CMYK-capable path, default 32 bpp.
- `gs_cdj850_device`: 600 dpi CMYK-capable path, default 32 bpp.
- `gs_cdj890_device`: 600 dpi CMYK-capable path, default 32 bpp.
- `gs_cdj1600_device`: 300 dpi CMY/PCL-style path, default 24 bpp.

## Major Components
- Gamma lookup tables for 850-family and 890-family behavior.
- Device structs that extend printer devices with CMYK state, default depth, correction flags, quality, paper type, intensity count, scaling flags, printer type, compression mode, gamma values, black correction, and printer-command function pointers.
- Parameter handlers for quality, paper type, gamma, black correction, and bits per pixel.
- Print-page pipeline with buffer allocation, gamma/GCR preparation, raster-mode setup, scan-line processing, compression, and page termination.
- Floyd-Steinberg dithering for black and color planes, including 2-, 3-, and 4-intensity color output.
- HP PCL mode 9 compression for cdj850-style output and mode 3 compression for cdj1600-style output.

## Open/Configuration Behavior
- `hp_colour_open` chooses resolution and scaling based on printer type, quality, and media type.
- Margins are set for A4/letter DeskJet devices or fixed CDJ1600 margins.
- `cdj850_start_raster_mode` emits HP raster setup including page size, quality, media type, top offset, CMYK raster configuration, and compression.
- `cdj1600_start_raster_mode` enters PCL mode, sets resolution/page/media/quality/raster width/plane count, then starts raster graphics.

## Rendering Pipeline
- `cdj850_print_page` copies gamma tables, optionally recomputes gamma curves, computes black correction, allocates one large working buffer, initializes pointer slices, starts raster mode, sends scan lines, terminates the page, and frees memory.
- `send_scan_lines` skips blank lines, preserves plane buffers across compression, and dispatches nonblank rows to the device-specific output function.
- `cdj850_print_non_blank_lines` performs grey component replacement, dithers the black plane, emits black, rescales color planes as needed, dithers C/M/Y, and emits lower/upper color planes depending on intensity count.
- `cdj1600_print_non_blank_lines` copies color data to the color buffer, dithers color planes, and emits PCL mode 3 compressed planes.

## Color Processing
- `do_gcr` performs grey component replacement / undercolor handling and applies gamma lookup tables.
- `do_gamma` builds gamma-adjusted lookup tables.
- `do_black_correction` builds a correction table used during GCR.
- `rescale_byte_wise1x1`, `1x2`, `2x1`, and `2x2` adapt color-plane resolution relative to black-plane resolution.

## Color Mapping
- `gdev_cmyk_map_cmyk_color` packs CMYK-like values into the driver’s K,C,M,Y internal order.
- `gdev_cmyk_map_rgb_color` supports mono/gray mapping for CMYK devices.
- `gdev_cmyk_map_color_rgb` decodes packed CMYK values to RGB.
- `gdev_pcl_map_rgb_color` and `gdev_pcl_map_color_rgb` handle PCL-style gray/CMY/RGB packed depths from 1 to 32 bpp.
- `cdj_set_bpp` switches among mono, RGB/CMY, and CMYK modes and updates device color metadata/procs.

## Parameters
- `cdj850_get_params` reports `Quality`, `Papertype`, `MasterGamma`, individual gamma values, and `BlackCorrect`.
- `cdj850_put_params` validates and stores those parameters, then routes bits-per-pixel changes through `cdj_put_param_bpp` / `cdj_set_bpp`.
- Quality accepted by `put_params` is checked as 0..2 even though the enum uses `DRAFT = -1`; that mismatch is worth preserving/understanding before changing behavior.

## Memory Layout
- `calculate_memory_size` computes scan-line, plane, error, output, and total storage sizes.
- `init_data_structure` slices one allocation into alternating input buffers, error buffers, plane buffers, color buffers, upper/lower intensity buffers, and output compression storage.

## Notes
- The file is self-contained and old-style C, with `P1`..`P12` compatibility macros.
- Dithering intentionally random-seeds error buffers for high-bit-depth modes to avoid uniform first rows.
- There is a notable indexing concern in `gdev_cmyk_map_cmyk_color`: it assigns `yellow = cmyk[3]` and `black = cmyk[4]`, which is atypical for a four-element CMYK array and should be verified before relying on or modifying that mapper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcd8.c -->