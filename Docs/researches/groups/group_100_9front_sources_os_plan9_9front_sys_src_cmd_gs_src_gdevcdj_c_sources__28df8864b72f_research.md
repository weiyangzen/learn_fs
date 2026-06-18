# Group Research: group_100_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gdevcdj_c_sources__28df8864b72f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcdj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcdj.c

Ghostscript HP/Canon color printer backend containing many device definitions in one legacy file: DeskJet/PaintJet/DesignJet/LaserJet dithering, Epson ESC/P, and Canon BJC variants. It defines device structs for HP-style RGB/CMY devices and BJC CMYK-capable devices, device procedure tables, exported `gs_*_device` descriptors, open/parameter/print routines, raster packing, PCL/ESC/P/BJC command output, compression, and color mapping.

Key behavior:
- `hp_colour_open` selects margins by printer type and paper size, initializes color depth via `cdj_set_bpp`, and opens the printer device.
- `cdj_get_params`, `cdj_put_params`, `pjxl_*`, `pj_put_params`, and `bjc_*_params` expose device options such as `BitsPerPixel`, `BlackCorrect`, `Shingling`, `Depletion`, `PrintQuality`, `RenderType`, `ProcessColorModel`, media type, media weight, manual feed, dithering type, and print colors.
- `hp_colour_print_page` is the central raster pipeline. It allocates working buffers, copies rendered scanlines, handles blank-line skipping, expands packed pixel formats, dithers RGB/CMYK data, separates planes, chooses printer-specific compression, writes printer control streams, and ejects/finalizes pages.
- Compression support includes local PCL mode 1, imported/used PCL mode 2/3/9 paths, BJC PackBits-like compression, and ESC/P transposition buffers.
- Color functions map RGB/CMY/CMYK across 1/3/8/16/24/32-bit modes, with optional black correction and CMYK-specific encode/decode behavior.

Notable dependencies:
- Ghostscript printer/device APIs: `gdevprn.h`, `gdevpcl.h`, `gsparam.h`, `gsstate.h`.
- Color/luminance helpers: `gxlum.h`.
- Canon BJC constants/options from `gdevbjc.h`.

Research notes:
- This is vendor/legacy Ghostscript printer output code, not filesystem logic, but it is part of the in-scope 9front Ghostscript source tree.
- The file itself warns that no further changes were accepted historically and that the drivers were planned for rewrite; the implementation reflects that: many compile-time flags, global ESC/P buffers, macro-heavy dithering, and printer-specific command knowledge are tightly coupled.
- Memory ownership in `hp_colour_print_page` is manual; allocation failure returns VM errors, but there are paths where one allocation may have succeeded before another fails.
- `bjc_fscmyk` embeds an adapted Floyd-Steinberg CMYK algorithm with persistent error buffer layout packed into caller-provided storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcdj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcfax.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcfax.c

Ghostscript CAPI fax SFF writer. It defines the `cfax` fax device using fax printer parameters, CCITT fax encoding, and custom SFF document/page framing.

Key behavior:
- `gs_cfax_device` is declared through `FAX_DEVICE_BODY` with `cfax_print_page`.
- `cfax_doc_hdr`, `cfax_page_hdr`, and `cfax_doc_end` emit SFF container markers and little-endian numeric fields.
- `cfax_print_page` initializes a `stream_CFE_state` for 1-D Group 3-style encoding with byte alignment and low-order first bit order.
- `cfax_stream_print_page_width` copies every scanline, pads width-adjusted rows, runs the stream encoder per line, and writes SFF line records using short or long length forms.
- `cfax_prn_close` appends the SFF end-of-document marker before normal printer close.

Notable dependencies:
- Ghostscript printer/fax APIs: `gdevprn.h`, `gdevfax.h`.
- Stream compression interfaces: `strimpl.h`, `scfx.h`.

Research notes:
- The code supports multipage SFF output by detecting new files for the document header and using a special close hook for document termination.
- A narrow resource risk exists in `cfax_stream_print_page_width`: if encoder init fails inside the line loop, the function returns immediately rather than going through the cleanup label, so temporary buffers may leak on that error path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcfax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgm.c

Ghostscript Computer Graphics Metafile output device. It wraps the local CGM writer library and exposes three devices: `cgmmono`, `cgm8`, and `cgm24`.

Key behavior:
- Defines `gx_device_cgm`, storing output filename, file handle, `cgm_state`, and picture state.
- `cgm_open` opens `OutputFile`, initializes the CGM writer with Ghostscript memory callbacks, begins the metafile, and writes core metafile properties.
- `cgm_begin_picture` starts a picture lazily on first drawing operation, sets scaling, color selection mode, VDC extent, VDC precision, edge width, and indexed color table for <=8-bit devices.
- `cgm_output_page` ends an active picture and finishes the Ghostscript page.
- `cgm_close` ends any active picture, writes `END_METAFILE`, terminates the CGM writer, and closes the file.
- Drawing support covers rectangle fills, monochrome bitmap copy, and color bitmap copy, primarily via CGM rectangles and cell arrays.

Notable dependencies:
- CGM API from `gdevcgml.h`.
- Ghostscript device, parameter, and platform file APIs.
- `gdevpccm.h` for 8-bit palette color mapping.

Research notes:
- `OutputFile` is a device parameter and respects `LockSafetyParams`.
- The bitmap fallback paths are intentionally inefficient.
- In `cgm_copy_mono`, the slow per-pixel rectangle path appears suspicious: it computes each pixel color but uses `cgm_set_rect(points, x, y, 1, 1)` rather than offsetting by `ix`/`iy`, and it does not visibly emit `cgm_FILL_COLOR` for each chosen color before the rectangle. That path likely does not render arbitrary transparent/two-color masks correctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.c

Implementation of the CGM-writing library used by `gdevcgm.c`. It serializes CGM binary commands, tracks metafile/picture/attribute state, and provides public functions for CGM elements.

Key behavior:
- `cgm_initialize` allocates and initializes `cgm_state` defaults for metafile, picture, control, and attribute elements.
- Public APIs emit CGM elements for metafile control, picture control, primitives, cell arrays, geometry, and drawing attributes.
- `begin_command`, `put_*`, `write_command`, and `end_command` implement binary command buffering with short and extended-length CGM command encoding.
- Integer, real, VDC, point, string, color, RGB, and byte-array encoders honor the current precision and color selection state.
- `cgm_CELL_ARRAY` writes packed cell data row by row, including source-bit shifting and even-byte padding.

Notable dependencies:
- Internal definitions from `gdevcgmx.h`.
- Standard memory/string/file wrappers.

Research notes:
- The implementation mostly trusts callers; invalid state/range handling is minimal despite result codes existing for such errors.
- Floating real representation is stubbed: `put_real` only implements fixed representation.
- In `cgm_set_metafile_elements`, the `cgm_set_COLOR_PRECISION` branch writes `meta->color_precision` but assigns `st->metafile.color_index_precision = meta->color_index_precision`; this looks like a copy/paste bug because it does not update `st->metafile.color_precision`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.h

Public interface for the CGM-writing library.

Key contents:
- Abstract `cgm_state` and allocator callback types.
- CGM scalar, coordinate, point, color, precision, and string types.
- Enumerations for VDC type, scaling, color selection, line/marker/edge modes, transparency, clipping, text settings, fill styles, hatch indexes, arc closure, polygon edge visibility, cell representation, and aspect source flags.
- `cgm_result` error/result enum.
- Metafile and picture element structs plus bitmask flags for selective emission.
- Public prototypes for initialization, termination, metafile elements, picture elements, control elements, graphical primitives, and attribute elements.

Notable dependencies:
- Uses Ghostscript-style `uint`, `byte`, and `bool` types supplied by included compilation context rather than declaring them locally.

Research notes:
- The header names API functions after CGM standard elements, with shortened alternate-character-set naming for legacy VAX DEC C symbol length limits.
- It is a serialization API, not a rendering or parsing API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgml.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgmx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgmx.h

Internal header for the CGM-writing library.

Key contents:
- Defines CGM binary opcode numbering with class/id shifts and the `cgm_op_index` enum.
- Defines the concrete `struct cgm_state_s`, including file handle, allocator, current metafile/picture/control/attribute state, aspect source flags, and command buffer.
- Sets `command_max_count` to 400 bytes and stores dynamic command state: `command_count`, `command_first`, and `result`.

Notable dependencies:
- Includes `gdevcgml.h`, making public CGM types available to the private implementation.

Research notes:
- This file is tightly paired with `gdevcgml.c`; external users should consume only `gdevcgml.h`.
- `command_max_count` must remain even because command writes pad to even byte counts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgmx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcif.c

Ghostscript CIF output driver for generating Caltech Intermediate Form-style chip layout output from rendered monochrome pages.

Key behavior:
- Defines `gs_cif_device` as a 1-bit printer device, defaulting to 72 DPI unless `X_DPI`/`Y_DPI` are overridden.
- `cif_print_page` derives a CIF structure name from the output filename prefix before the first dot, writes CIF prologue records, scans each rendered line, and emits box records for set bits.
- With `TILE` defined, every set bit becomes a `B4 4 ...` box.
- Without `TILE`, consecutive set bits on a scanline are coalesced into wider box records.

Notable dependencies:
- Only uses `gdevprn.h` plus standard string routines available through the Ghostscript environment.

Research notes:
- This is an output conversion device, not storage/filesystem code.
- There is a likely allocation bug: `s` is allocated with `length` bytes and then writes `s[length] = '\0'`; the allocation should allow one extra byte. In the no-dot case, `length` is already `strlen + 1`, then the code writes one byte beyond that.
- The non-`TILE` run coalescing does not flush a run that reaches the end of a scanline, so trailing black runs at line end can be omitted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevclj.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevclj.c

Ghostscript HP Color LaserJet 5/5M PCL driver, plus a page-rotation variant.

Key behavior:
- Defines `gx_device_clj` with standard printer state and a `rotated` flag.
- Supports 75, 100, 150, and 300 DPI square resolutions.
- Supports specific color-capable media sizes via `clj_paper_sizes`, with logical long-edge-feed orientation metadata and offsets.
- `clj_get_initial_matrix` builds the page matrix according to media orientation and rotation.
- `clj_get_params` publishes supported input media sizes.
- `clj_put_params` validates requested page size and resolution, rejecting unsupported or rotated media in the standard device.
- `pack_and_compress_scanline` converts 3-bit-per-pixel YMC byte data into C/M/Y bit planes and compresses each plane using PCL mode 2.
- `clj_print_page` emits PCL setup, scans imageable rows, skips blank lines, writes C/M/Y compressed planes, and ends the raster/page.
- `cljet5pr` variant fakes rotation by rewriting `.MediaSize` before delegating to printer parameters.

Notable dependencies:
- Ghostscript printer and PCL APIs: `gdevprn.h`, `gdevpcl.h`.
- Parameter APIs for synthesized page-size lists.

Research notes:
- The file documents a hardware tradeoff between fast fixed color modes and more accurate direct color mode; `USE_FAST_MODE` is enabled.
- The rotation variant explicitly breaks a usual Ghostscript device invariant by modifying parameters, and the comments restrict its intended use to PCL interpreter contexts lacking proper `setpagedevice`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevclj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcljc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcljc.c

Ghostscript contone HP Color LaserJet 5/5M driver based on `gdevclj.c`, but with hardwired 24-bit direct RGB output.

Key behavior:
- Defines `gs_cljet5c_device` as a 300 DPI, 24-bit RGB printer device.
- `cljc_print_page` allocates raw, compressed, and previous-row buffers.
- Emits PCL reset, paper definition, color render mode, direct RGB pixel format, raster setup, and mode 3 compression selection.
- For each scanline, copies rendered data and sends PCL mode 3 delta-compressed raster data against the previous row.
- Ends raster graphics and ejects the page.

Notable dependencies:
- Ghostscript printer and PCL compression APIs.

Research notes:
- Color encoding and render mode are intentionally hardwired.
- Compared with `gdevclj.c`, this is smaller and simpler but sends full contone raster data rather than bitplane-packed YMC.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcljc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.c

Special forwarding color-mapping device used to implement PCL5 color mapping behavior.

Key behavior:
- Defines a private prototype `gs_cmap_device` with forwarding drawing operations and custom parameter/color-mapping hooks.
- `gdev_cmap_init` initializes a `gx_device_cmap`, attaches a target device, copies target parameters, fills forwarding procs, and selects a mapping method.
- `gdev_cmap_set_method` switches among identity, monochrome, snap-to-primaries, and color-to-black-over-white modes, updating color model metadata and mapping procs.
- `cmap_get_params`/`cmap_put_params` expose `ColorMappingMethod`.
- `cmap_begin_typed_image` forwards high-level images only for identity mapping; otherwise it forces default image rendering so colors pass through the mapper.
- Gray/RGB/CMYK mapping procedures transform source color values and then delegate to the target device’s color mapping procs.

Notable dependencies:
- Ghostscript forwarding-device infrastructure, color conversion helpers, and `gdevcmap.h`.

Research notes:
- This is a device wrapper rather than a physical output device.
- CMYK mapping is explicitly noted as untested/not apparently called.
- Identity mode preserves the target color model; non-identity modes deliberately present altered color model metadata to avoid unwanted halftoning behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.h

Public interface for the special color mapping forwarding device.

Key contents:
- `gx_device_color_mapping_method_t` enum:
  - `device_cmap_identity`
  - `device_cmap_snap_to_primaries`
  - `device_cmap_color_to_black_over_white`
  - `device_cmap_monochrome`
- `gx_device_cmap` struct extending `gx_device_forward_common` with a `mapping_method`.
- GC structure declaration macro `public_st_device_cmap`.
- Prototype for `gdev_cmap_init`.

Research notes:
- Comments state that clients may change `ColorMappingMethod` at runtime but must then call `gs_setdevice_no_init` for graphics states referencing the device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcp50.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcp50.c

Ghostscript Mitsubishi CP50 color printer driver.

Key behavior:
- Defines fixed experimental printer geometry: 474 x 800 pixels, scanline cropping bounds, first column offset, and 154 x 187 DPI.
- `gs_cp50_device` is a 24-bit RGB printer device with custom output page and RGB mappers.
- `cp50_print_page` allocates RGB planes and a temporary plane, initializes them white, emits CP50 control sequences, copies/crops rendered scanlines from `FIRST_LINE` through `LAST_LINE`, splits RGB bytes into separate planes, rotates each plane, and writes R/G/B plane data.
- `cp50_output_page` opens the printer, stores `num_copies` in a global, invokes the print-page routine, closes the printer, reinitializes clist output if needed, and finishes the page.
- `cp50_rgb_color`/`cp50_color_rgb` map 24-bit RGB color indexes.

Notable dependencies:
- Ghostscript printer APIs only.

Research notes:
- Uses a global `int copies` to pass copy count into `cp50_print_page`, so it is not reentrant/thread-safe.
- Allocation failure returns `-1` rather than a Ghostscript VM error code.
- Several geometry constants are empirical and hardcoded, making the driver highly device-specific.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcp50.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcslw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcslw.c

Ghostscript CoStar LabelWriter II/II Plus driver.

Key behavior:
- Defines two monochrome printer devices:
  - `coslw2p` at 128 DPI.
  - `coslwxl` at 204 DPI.
- `coslw_print_page` allocates word-aligned scanline storage, clears temporary storage, scans rendered rows, masks bits beyond page width, skips blank rows with `ESC f` spacing commands, caps output width at 56 bytes for the 2-inch model, changes bytes-per-line with `ESC D`, writes raster lines with `0x16`, and ejects with `ESC E`.

Notable dependencies:
- Ghostscript printer APIs.

Research notes:
- Compression is explicitly left as a possible future improvement.
- The driver is simple monochrome raster output with printer command framing and blank-line optimization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcslw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdbit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdbit.c

Default Ghostscript bitmap-copying implementation for devices that do not provide optimized operations.

Key behavior:
- `gx_default_tile_rectangle` maps tile requests to `strip_tile_rectangle`.
- `gx_default_copy_mono` fills monochrome masks via device colors and `gx_dc_default_fill_masked`.
- `gx_default_copy_color` implements slow row-run rectangle filling for packed color bitmaps, delegating 1-bit depth to `copy_mono`.
- `gx_default_copy_alpha` simulates alpha by reading destination pixels, decoding colors, blending component values, re-encoding, and writing accumulated lines.
- `gx_default_fill_mask` handles optional clipping and alpha/mask dispatch.
- `gx_default_strip_tile_rectangle` tiles a strip bitmap over a rectangle, handling shallow, narrow, and full tiling cases, and avoids recursion if a device’s tile proc conditionally calls the default strip implementation.
- `gx_copy_*_unaligned` wrappers adjust misaligned source pointers/raster strides and fall back to line-by-line copying where needed.
- `gx_no_copy_alpha`, `gx_no_copy_rop`, and `gx_no_strip_copy_rop` are negative stubs returning unknown-error.

Notable dependencies:
- Core Ghostscript graphics/device headers: clipping, rops, device colors, memory devices, bitmap tables, and alignment helpers.

Research notes:
- This is shared rendering fallback infrastructure and is more central than most other files in this group.
- The implementations favor correctness and portability over speed, and comments repeatedly describe them as inefficient defaults.
- The alpha path relies on target device `get_bits`, `decode_color`, and `encode_color`; if a device cannot represent a blended color it adjusts alpha toward representable endpoints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.c

Sample implementation for exposing a device Color Rendering Dictionary through Ghostscript device parameters.

Key behavior:
- Defines default-ish CIE rendering data: white point, PQR/LMN ranges, transform/encode procedures, ABC matrix, gamma-like ABC encoding, and dummy render tables.
- `sample_device_crd_get_params` conditionally writes:
  - `CRDName`
  - a built CIE Render1 object under the requested CRD parameter name
  - a serialized pointer-sized procedure address string for the sample PQR transform proc name.
- Builds and initializes a `gs_cie_render` object with `gs_cie_render1_build` and `gs_cie_render1_initialize`, writes it with `param_write_cie_render1`, and decrements the reference.

Notable dependencies:
- Ghostscript CIE color/rendering internals: `gscspace.h`, `gscrd.h`, `gscrdp.h`, `gxdevcli.h`.
- Header `gdevdcrd.h`.

Research notes:
- Comments identify it as sample code; a settable `CRDName` is left as an exercise.
- The static procedure-address export is explicitly discouraged in comments and is a shortcut for sample behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.h

Small public header for the sample device CRD helper.

Key contents:
- Include guard `gdevdcrd_INCLUDED`.
- Prototype:
  `int sample_device_crd_get_params(gx_device *pdev, gs_param_list *plist, const char *crd_param_name);`

Research notes:
- Depends on the including compilation unit already having declarations for `gx_device` and `gs_param_list`.
- This header is only an interface shim for `gdevdcrd.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.h -->