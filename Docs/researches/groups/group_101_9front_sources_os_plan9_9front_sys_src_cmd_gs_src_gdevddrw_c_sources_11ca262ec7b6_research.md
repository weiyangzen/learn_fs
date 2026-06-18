# Group Research: group_101_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevddrw_c_sources_11ca262ec7b6

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.c

Ghostscript default polygon, line, trapezoid, gradient-fill, and image-dispatch device procedures. This is shared rendering infrastructure used when a device does not provide specialized drawing implementations.

Key behavior:
- Defines fixed-point trapezoid edge state (`trap_line`) and gradient state (`trap_gradient`) helpers for exact scan conversion.
- Includes `gxdtfill.h` repeatedly under different macro configurations to generate trapezoid fill variants: axis-swapped/non-swapped, direct/non-direct color writes, contiguous fills, and linear-color fills.
- `gx_default_fill_trapezoid` selects a generated fill routine based on axis orientation and whether the drawing color can be written directly.
- Linear-color routines fill shaded trapezoids and triangles by deriving per-edge and per-scanline color gradients, with overflow checks that return `0` when callers must subdivide.
- `gx_default_fill_parallelogram` and `gx_default_fill_triangle` decompose non-rectangular shapes into trapezoids while preserving Ghostscript’s center-of-pixel rules.
- `gx_default_draw_thin_line` handles horizontal/vertical one-pixel lines as rectangles and general lines as thin trapezoids.
- Image entry points bridge legacy `begin_image` to `begin_typed_image`, avoiding recursive device-procedure calls, and keep obsolete `image_data`/`end_image` compatibility wrappers.

Notable dependencies:
- Ghostscript fixed-point geometry, device, color, image, and clipping APIs: `gxfixed.h`, `gxdevice.h`, `gxdcolor.h`, `gxiparam.h`, `gxistate.h`.
- Macro-generated trapezoid implementation from `gxdtfill.h`.
- Visual debug tracing via `vdtrace.h`.

Research notes:
- This file is core Ghostscript rendering machinery, not filesystem code.
- The implementation is deliberately macro-heavy: actual trapezoid bodies come from `gxdtfill.h` with local macro settings, so behavior depends on compile-time inclusion context.
- Linear shading has explicit overflow avoidance and returns non-error `0` to request decomposition by higher-level callers.
- The obsolete `gx_default_draw_line` intentionally returns `-1`; newer thin-line and shape fill procedures are the meaningful paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.h

Small Ghostscript header exposing selected polygon/trapezoid drawing declarations from `gdevddrw.c`.

Key contents:
- Defines `enum fill_trap_flags` with `ftf_peak0`, `ftf_peak1`, and `ftf_pseudo_rasterization`.
- Declares the contiguous-fill trapezoid entry points `gx_fill_trapezoid_cf_fd` and `gx_fill_trapezoid_cf_nd`.
- Uses Ghostscript geometry/color types supplied by surrounding headers: `gx_device`, `gs_fixed_edge`, `fixed`, `gx_device_color`, and `gs_logical_operation_t`.

Research notes:
- This is not a standalone public API header; it assumes inclusion in Ghostscript device/rendering compilation context.
- The two declared functions are generated in `gdevddrw.c` by including `gxdtfill.h` with `CONTIGUOUS_FILL` enabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevddrw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.c

Ghostscript example DeviceN and spot-color process-model device implementation. It provides utility routines for DeviceN parameter handling, colorant-name lookup, component mapping, packed raster repacking, and example `spotcmyk`/`devicen` printer devices that write raw component files and PCX previews.

Key behavior:
- Converts Gray/RGB/CMYK source color spaces into DeviceN component arrays using the current separation-order map.
- `bpc_to_depth` computes packed device depth for component count and bits per component.
- `check_pcm_and_separation_names` and `devn_get_color_comp_index` resolve process colorants and spot separations, optionally auto-adding new spot colorants.
- `devn_get_params`, `devn_put_params`, and `devn_printer_put_params` manage `SeparationColorNames`, `SeparationOrder`, `Separations`, and `MaxSeparations`, including rollback for standard printer parameter failures.
- Defines two devices:
  - `spotcmyk`: 1-bit CMYK plus optional spot colors.
  - `devicen`: 8-bit component DeviceN-style example device.
- `spotcmyk_encode_color` and `spotcmyk_decode_color` pack/unpack component values into `gx_color_index`.
- `repack_data` extracts selected bit fields from packed pixels into process-color or spot-color output streams.
- `spotcmyk_print_page` writes process color data to the main output, writes each spot color to sibling files named with `sN`, then converts those raw files to `.pcx`.
- Embedded PCX writer builds headers, palettes, planar/chunky layouts, and RLE-compressed image rows for a limited set of bit-depth/component combinations.

Notable dependencies:
- Ghostscript printer, parameter, color-rendering, and equivalent-color APIs: `gdevprn.h`, `gsparam.h`, `gscrd.h`, `gdevdcrd.h`, `gxdcconv.h`, `gsequivc.h`.
- Shared declarations from `gdevdevn.h`.

Research notes:
- The file labels these as example devices; output behavior is demonstrative rather than a polished production image format pipeline.
- `devn_put_params` allocates new separation-name buffers when `SeparationColorNames` changes; ownership is tracked for GC relocation, but old names are not visibly freed during replacement.
- In `spotcmyk_print_page`, early returns after PCX conversion failures bypass the common cleanup label, leaking temporary buffers.
- `pcx_write_rle` compares `data != *from || from == end`; because C evaluates left-to-right, it may dereference `from` when `from == end`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.h

Header for common Ghostscript DeviceN process-color model support.

Key contents:
- Sets DeviceN limits: `GX_DEVICE_MAX_SEPARATIONS` at 16 and `MAX_DEVICE_PROCESS_COLORS` at 6.
- Defines colorant-name, separation-name, separation-list, separation-map, and `gs_devn_params` structures.
- Declares `DeviceCMYKComponents`.
- Includes `gsequivc.h` for equivalent CMYK spot-color metadata.
- Declares conversion helpers for Gray/RGB/CMYK to DeviceN component arrays.
- Defines automatic spot-color modes: `NO_AUTO_SPOT_COLORS`, `ENABLE_AUTO_SPOT_COLORS`, and `ALLOW_EXTRA_SPOT_COLORS`.
- Declares DeviceN parameter helpers, color-component lookup helpers, `repack_data`, and `bpc_to_depth`.

Research notes:
- The header documents that some routines mutate device color info and DeviceN parameters and do not always restore on error; callers must use the printer wrapper if rollback is needed.
- It is a shared support header for Ghostscript devices with spot-color or DeviceN behavior, not storage/filesystem functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdfax.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdfax.c

Ghostscript DigiBoard DigiFAX output device.

Key behavior:
- Defines `dfaxlow` and `dfaxhigh` devices at 204 DPI horizontal resolution and low/high vertical fax resolutions.
- Extends the printer device with a page counter and image-width field.
- `dfax_prn_open` resets the page counter and delegates to fax-device open logic.
- `dfax_print_page` configures CCITT fax encoding state with EOL markers and byte alignment.
- Writes a fixed DigiFAX page header, updates page number and resolution bits, appends encoded fax page data via `gdev_fax_print_page`, then seeks back to update the total page count.

Notable dependencies:
- Ghostscript printer/fax APIs: `gdevprn.h`, `gdevfax.h`, `gdevtfax.h`.
- Stream compression interfaces: `strimpl.h`, `scfx.h`.

Research notes:
- The driver is marked as user-maintained legacy code.
- It uses `fseek` to patch the page count after page output, so output streams must be seekable for correct headers.
- Header bytes are stored in a static buffer and modified per page.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdfax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdflt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdflt.c

Ghostscript default device implementation. It fills missing device procedure slots, infers color encoding/decoding behavior, determines separable color layouts, and supplies no-op/default implementations for common device lifecycle and page operations.

Key behavior:
- `get_encode_color` derives an encoding procedure from explicit `encode_color`, legacy RGB/CMYK mapping procedures, monochrome defaults, or separable-linear color info.
- `is_like_DeviceRGB` and `is_like_DeviceCMYK` probe color mapping procedures with sample values to identify compatible standard color models.
- Default decode functions handle additive/subtractive one-component devices, separable devices, 1-bit CMYK, and approximate CMYK decode through RGB when necessary.
- `set_linear_color_bits_mask_shift` and `check_device_separable` populate component shift/mask/bit metadata for separable packed color indices.
- `gx_device_fill_in_procs` installs default procedure pointers for lifecycle, raster operations, paths, trapezoids, images, color mapping, compositor creation, clipping, patterns, shading, and spot equivalent colors.
- Default lifecycle/page functions mostly no-op or delegate: open initializes separability, output syncs then finishes page, close returns success.
- Default matrix functions provide inverted-Y and upright-Y device coordinate transforms.
- Default compositor, clipping-box, xfont, alpha-bit, pattern, and page callbacks provide baseline behavior.

Notable dependencies:
- Core Ghostscript device/color/compositor APIs: `gxdevice.h`, `gxcomp.h`, `gsropt.h`.

Research notes:
- This is central compatibility glue for old and new Ghostscript device APIs.
- Several defaults are intentionally conservative or approximate, especially CMYK decode through RGB and automatic separability probing.
- `gx_device_fill_in_procs` forcibly replaces obsolete `image_data` and `end_image` hooks with current wrappers and can warn in debug builds.
- The comments note known limitations: default initial matrices have wrong translation assumptions for devices with arbitrary initial matrices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdflt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdgbr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdgbr.c

Ghostscript default implementation of `get_bits` and `get_bits_rectangle`, including conversion between native device pixels and requested standard bitmap formats.

Key behavior:
- `gx_default_get_bits` delegates single-scanline reads to `get_bits_rectangle` while temporarily disabling itself to avoid recursion.
- `requested_includes_stored` checks whether stored bitmap options satisfy a caller’s requested packing/color/depth/alpha format.
- `gx_get_bits_return_pointer` attempts zero-copy pointer returns when alignment, raster, packing, and plane-selection constraints allow it.
- `gx_get_bits_copy` copies or transforms bitmap regions into requested chunky/planar destination buffers.
- Supports direct bit-copy, unaligned bit-copy through memory-device `copy_mono`, chunky-to-planar extraction, native-to-standard conversion, and standard-to-native conversion.
- Special-cases 1-bit-per-component CMYK to 24-bit RGB conversion.
- `gx_default_get_bits_rectangle` bridges devices that only implement `get_bits`, handles partial-row extraction, and otherwise processes rectangles row by row through `gx_get_bits_copy`.

Notable dependencies:
- Ghostscript bitmap option and sample-load/store macros: `gxgetbit.h`.
- Memory devices and bitmap helpers: `gxdevmem.h`, `gdevmem.h`.
- Luminance weights from `gxlum.h`.

Research notes:
- This file is device raster plumbing, not filesystem code.
- Much of the complexity comes from honoring many combinations of return mode, packing mode, offset, raster, color space, depth, alpha, and plane selection.
- The implementation intentionally uses temporary recursion guards by swapping device procedure pointers during fallback calls.
- Some paths only support `GB_DEPTH_8` for native-to-standard conversion and return rangecheck for unsupported format combinations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdgbr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjet.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjet.c

Ghostscript HP DeskJet/LaserJet monochrome PCL device definitions and printer-specific wrappers around the generic mono PCL raster pipeline in `gdevdljm.c`.

Key behavior:
- Defines devices for `deskjet`, `djet500`, `fs600`, `laserjet`, `ljetplus`, `ljet2p`, `ljet3`, `ljet3d`, `ljet4`, `ljet4d`, `lp2563`, and `oce9050`.
- `hpjet_open` chooses paper-size-specific margins, handles DeskJet vs LaserJet origin movement, and enables duplex defaults for duplex device variants.
- `hpjet_close` emits duplex odd-page handling and printer reset when pages were printed.
- `hpjet_make_init` augments printer initialization strings with manual-feed or media-source tray selection.
- Per-device `*_print_page_copies` functions choose resolution, PCL initialization commands, and feature masks before calling `dljet_mono_print_page_copies`.
- `oce9050_print_page_copies` enters HPGL/2/RTL mode before printing and advances/resets the plotter afterward.
- `hpjet_get_params` and `hpjet_put_params` expose `ManualFeed` and `%MediaSource` in addition to normal printer parameters.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- Generic mono PCL feature definitions and print routine from `gdevdljm.h`.

Research notes:
- The file contains many model-specific PCL command strings and margins, reflecting practical printer compatibility rather than a uniform PCL abstraction.
- Fixed-size init buffers are sized for local strings; future longer command strings would need care.
- Media source support maps a small `%MediaSource` range through a two-entry table and ignores null `%MediaSource`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjtc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjtc.c

Ghostscript HP DeskJet 500C color PCL driver.

Key behavior:
- Defines `djet500c` as a 300x300 DPI, 3-bit RGB-style printer device with PCL 3-bit color mapping.
- Uses compile-time `SHINGLING` and `DEPLETION` settings for DeskJet color print quality behavior.
- `djet500c_print_page` resets/configures the printer, selects RGB raster mode, depletion, shingling, mode-2 compression, and raster start.
- For each scanline, reads packed 3-bit pixel data, skips blank lines, pads line data, transposes R/G/B bits into separate planes, complements plane bits for printer semantics, compresses each plane, and emits PCL raster-transfer commands.
- `mode2compress` implements HP mode 2 run/literal compression for arbitrary line lengths.

Notable dependencies:
- Ghostscript printer and PCL APIs: `gdevprn.h`, `gdevpcl.h`.
- Uses C library `malloc`/`free` rather than Ghostscript memory allocators for its work buffers.

Research notes:
- This is contributed legacy driver code.
- Allocation failures are not checked after `malloc` for `bitData` or plane buffers; null dereferences are possible under memory pressure.
- The compressor reads `*exam` in loop tests where `exam` may have reached `end_row`, so edge-case out-of-bounds reads are plausible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.c

Generic monochrome HP DeskJet/LaserJet PCL raster output engine shared by multiple printer-specific wrappers.

Key behavior:
- `dljet_mono_print_page` delegates to `dljet_mono_print_page_copies` with one copy.
- Allocates a shared work buffer for current input row, compressed output row, alternate compressed row, and previous seed row.
- Initializes printer state, paper size, duplex mode, per-page setup, copies, raster end/start, and resolution.
- Scans rendered rows, masks bits beyond page width, skips trailing zero words, tracks blank lines, and chooses whether to output blank rows or vertical-positioning commands.
- Supports PCL no-compression, mode 2 compression, and adaptive mode 2/mode 3 compression, including mode-switch penalty accounting.
- Maintains/clears the seed row required by mode 3 compression.
- Ends raster graphics, ejects the page, frees temporary storage, and returns the last copy/print error.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- PCL helpers and feature flags from `gdevdljm.h`, including `gdev_pcl_mode2compress`, `gdev_pcl_mode3compress`, and paper-size helpers.

Research notes:
- This is the central implementation behind several printer devices in `gdevdjet.c`.
- It has many printer-behavior workarounds encoded through feature flags, especially around vertical spacing, seed-row clearing, duplex, copies, and paper-size commands.
- Temporary storage is manually partitioned in word-sized chunks for faster scanning and compression.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.h

Interface and feature-flag header for the generic monochrome HP DeskJet/LaserJet PCL driver.

Key contents:
- Defines vertical-spacing capability flags: `PCL_NO_SPACING`, `PCL3_SPACING`, `PCL4_SPACING`, `PCL5_SPACING`, and `PCL_ANY_SPACING`.
- Defines printer capabilities: mode 2/mode 3 compression, raster-end reset behavior, duplex, paper-size selection, and copy-count commands.
- Provides shorthand feature combinations such as `PCL_MODE0`, `PCL_MODE2`, `PCL_MODE3`, and no-spacing variants.
- Defines known feature masks for DeskJet, DeskJet 500, FS-600, LaserJet variants, LP2563B, and OCE9050.
- Declares `dljet_mono_print_page` and `dljet_mono_print_page_copies`.

Notable dependencies:
- Includes `gdevpcl.h` for PCL-related constants and helper declarations.

Research notes:
- The header explicitly warns that “PCL printer” is an approximation; feature flags encode model-specific command subsets.
- It is tightly paired with `gdevdljm.c` and consumed by model wrappers in `gdevdjet.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdljm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdm24.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdm24.c

Ghostscript high-resolution 24-pin dot-matrix printer driver for NEC P6-compatible and Epson LQ850-compatible devices.

Key behavior:
- Defines `necp6` and `lq850` 360x360 DPI monochrome printer devices.
- `dot24_print_page` handles the common raster pipeline for both devices, parameterized by model-specific initialization strings.
- Reads 24 or 48 scanline blocks depending on vertical resolution, interleaves odd/even passes for 360 DPI, and transposes row-major bitmap data into 24-pin column bytes via `memflip8x8`.
- Skips blank rows with vertical movement commands and skips long horizontal zero runs with tab stops where worthwhile.
- Emits ESC/P-style 24-pin graphics runs through `dot24_output_run`.
- `dot24_improve_bitmap` clears selected adjacent pixels at 360 DPI to account for printers that cannot print adjacent dots reliably.
- Model entry points only choose the NEC P6 or LQ850 initialization sequence.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- Memory bit-transposition helper `memflip8x8`.

Research notes:
- The file is pure printer-output conversion code.
- Allocation failures are handled for both input and output buffers.
- The driver mutates the generated bitmap in `dot24_improve_bitmap` for device-physics compatibility, trading exact raster fidelity for printable output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdm24.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdrop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdrop.c

Ghostscript default and device-independent RasterOp implementation.

Key behavior:
- Provides debug tracing for copy-rop inputs and optional bitmap dumps.
- `gx_default_strip_copy_rop` implements RasterOp for non-memory devices by reading destination pixels with `get_bits_rectangle`, running the operation in an intermediate memory device, then writing results back with `copy_color`.
- Converts source and texture colors into standard RGB/gray forms when needed.
- Special-cases conversion back into 1-bit CMYK devices.
- `mem_default_strip_copy_rop` implements RasterOp for memory devices through an 8-bit gray or 24-bit RGB intermediate memory device, expanding source/texture/destination operands as required.
- Uses stack-sized fallback buffers where possible and heap buffers for larger row blocks.
- `gx_default_copy_rop` adapts tiled texture input into strip texture input.
- `gx_copy_rop_unaligned` and `gx_strip_copy_rop_unaligned` adjust unaligned source pointers and rasters or process one scanline at a time.
- `gs_transparent_rop` computes effective ROP3 logic under source/pattern transparency rules.

Notable dependencies:
- Ghostscript ROP, memory-device, bitmap, and color APIs: `gsropt.h`, `gxdevrop.h`, `gxdevmem.h`, `gxgetbit.h`, `gdevmrop.h`.

Research notes:
- This is rendering/raster operation infrastructure, not filesystem code.
- The code carefully handles whether a ROP uses source, texture, or destination operands to avoid unnecessary reads/conversions.
- There is a likely leak/error-path issue in `gx_default_strip_copy_rop`: after copying destination data into the intermediate device, a `copy_color` failure returns immediately instead of going through the cleanup label.
- `max_rop_bitmap` intentionally limits multi-row temporary allocation, falling back to at least one row.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdsha.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdsha.c

Ghostscript default shading scanline fill implementation.

Key behavior:
- Implements `gx_default_fill_linear_color_scanline`.
- Decomposes a horizontally varying linear-color scanline into runs of constant device color index.
- Builds initial packed color index from component fractions and device component shifts/bits.
- Steps each component by numerator/denominator gradient arithmetic, preserving fractional remainders.
- Clips each run against the fill clip rectangle.
- Emits each run through `fill_rectangle`, swapping axes when requested by the fill attributes.
- Emits visual debug rectangles via `vd_rect`.

Notable dependencies:
- Ghostscript device/color index APIs: `gxdevice.h`, `gxcindex.h`.
- Visual debug tracing via `vdtrace.h`.

Research notes:
- This is the fallback scanline shading path; devices can override it with a direct raster implementation.
- The file comments note this default is simple but not optimal because it enumerates color changes and emits rectangles rather than writing scanline pixels directly.
- The clip tests intentionally mirror broader fill clipping behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdsha.c -->