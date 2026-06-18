# Group Research: group_1538_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevcdj_c_sources_o_7155dd6ba600

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcdj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcdj.c

Large Ghostscript printer-driver collection for HP/Canon color printers. It defines multiple device descriptors and a shared print pipeline for HP DeskJet/PaintJet/DesignJet/LaserJet variants, Epson ESC/P output, and Canon BJC raster-mode printers.

Key responsibilities:
- Defines Ghostscript devices including `cdjmono`, `cdeskjet`, `cdjcolor`, `cdj500`, `cdj550`, optional `cdj550cmyk`, `declj250`, `dnj650c`, `lj4dith`, `pj`, `pjxl`, `pjxl300`, `escp`, `escpc`, `bjc600`, and `bjc800`.
- Implements open routines that choose paper-size-specific hardware margins and initialize printer color depth/component metadata.
- Implements device parameter get/put paths for DeskJet shingling/depletion/black correction, PaintJet XL print quality/render type, BJC media/manual feed/quality/dithering/process color model/media weight/version metadata, and bits-per-pixel changes.
- Provides `hp_colour_print_page`, the central rasterization/output loop for all HP-like, ESC/P, and BJC-like devices.
- Converts Ghostscript rendered scanlines into printer color planes, handles blank-line skipping, shingled/head-row behavior, and emits device-specific PCL, HP-RTL, ESC/P, or Canon raster commands.
- Implements compression helpers: HP PaintJet mode 1 run-length compression, BJC PackBits-style compression, and selection between PCL mode 2 and mode 3 where supported.
- Implements RGB/CMYK color mapping and reverse mapping for PCL and BJC/CMYK-capable devices.
- Implements scanline expansion between packed 3/8/16/24-bit representations and 24/32-bit CMY/CMYK working formats.
- Implements Floyd-Steinberg dithering macros for gray/RGB/CMY/CMYK and a specialized BJC CMYK error-diffusion algorithm.

Important behavior:
- `hp_colour_open` mutates margins based on printer type and paper size, then calls `gdev_prn_open`.
- CMYK-capable devices use `cprn_device->cmyk` as a tri-state: positive for CMYK printing, negative for CMYK-capable but RGB/PCL mapping, zero for non-CMYK.
- `cdj_set_bpp` can change device color procedures and close an already-open device when color model/depth changes.
- DeskJet 500/550 use PCL mode 9 compression; DesignJet uses HPGL/2 plus HP-RTL and mode 1; PaintJet XL can select mode 2 or mode 3 per row; BJC uses Canon raster commands and PackBits-style compression.
- For some printer modes, rendered RGB/CMY data is inverted or decomposed into K/CMY planes before output.
- ESC/P output buffers head-height groups, transposes raster data into vertical nozzle order, optimizes horizontal skips, and flushes in bands.
- BJC page initialization emits Canon command sequences for page mode, margins, compression, paper loading, printing method, resolution, raster transfer, vertical skips, and page finish.
- `bjc_fscmyk` initializes and maintains a private CMYK error buffer, scans alternate directions, generates K-only output for gray cases, and clips CMY error in K-only regions.

Dependencies:
- Ghostscript printer/device APIs: `gdevprn.h`, `gdevpcl.h`, `gsparam.h`, `gsstate.h`, color value helpers, and Canon BJC constants from `gdevbjc.h`.
- Uses PCL compression helpers from other Ghostscript modules: `gdev_pcl_mode2compress`, `gdev_pcl_mode3compress`, `gdev_pcl_mode9compress`.
- Relies on Ghostscript memory allocation, scanline copying, device params, and device color procedure conventions.

Notable risks:
- The file is explicitly marked as hard to maintain and no longer accepting changes; its logic is dense, macro-heavy, and tightly coupled across printer families.
- Many paths share global/static ESC/P state (`ep_storage`, `ep_raster_buf`, `ep_print_buf`, `img_rows`), making reentrancy and concurrent use unsafe.
- Several calculations depend on exact buffer sizing across packed/expanded depths; mistakes can corrupt adjacent working regions.
- BJC and ESC/P code uses many empirically derived limits and hard-coded hardware command bytes.
- `cdj_put_param_bpp` temporarily mutates `pdev->color_info.depth` to pass Ghostscript parameter validation, then resets it, which is fragile.
- `bg_and_ucr` macro appears suspect: the black component calculation uses `kv = (yv > k ? k : y)`, mixing original variable names rather than the temporary `yv`.
- `gdev_cmyk_map_color_cmyk` has a parameter name `prgb[3]` but may write four CMYK values in the default path.
- Several functions return generic `0` or `rangecheck` and do not preserve detailed printer/protocol failure context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcdj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcfax.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcfax.c

Ghostscript `cfax` output device that writes SFF format for CAPI fax devices.

Key responsibilities:
- Defines the `gs_cfax_device` fax printer device.
- Emits SFF document header, per-page header, encoded line records, page data, and document-end signature.
- Uses Ghostscript fax parameters via `gdev_fax_get_params` and `gdev_fax_put_params`.
- Encodes each scanline through a stream template, specifically CCITT fax encoding through `s_CFE_template`.
- Overrides close handling so multi-page SFF documents receive the required final document-end marker.

Important behavior:
- `cfax_print_page` initializes CCITT fax encoder state with byte alignment, low-order first bit order, no EOL/EOB, and `K = 0`.
- `cfax_begin_page` temporarily patches `pdev->width` to the fax-adjusted width when writing the SFF page header.
- `cfax_stream_print_page_width` encodes one line at a time, writing short or extended SFF block lengths depending on encoded byte count.
- If the output filename is `"nul"`, encoded data is computed but not written.

Dependencies:
- Ghostscript printer and fax infrastructure: `gdevprn.h`, `gdevfax.h`.
- Stream encoder infrastructure: `strimpl.h`, `scfx.h`.
- Uses `gdev_fax_init_fax_state`, `gdev_prn_copy_scan_lines`, stream template init/process/release callbacks, and Ghostscript memory allocators.

Notable risks:
- On encoder init failure inside the line loop, the function returns immediately without freeing allocated buffers.
- Output block buffer size is fixed at 1000 bytes; correctness depends on CCITT output for one row fitting this working model.
- Only SFF/CAPI-specific line block conventions are implemented; it is not a generic fax writer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcfax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgm.c

Ghostscript CGM device wrapper that maps Ghostscript drawing operations into the local CGM-writing library.

Key responsibilities:
- Defines `cgmmono`, `cgm8`, and `cgm24` devices.
- Manages output file name, `FILE *`, CGM writer state, and picture-open state.
- Opens CGM files, initializes the CGM metafile, and declares metafile capabilities.
- Starts pictures lazily on first non-white drawing operation.
- Implements fill rectangle, monochrome bitmap copy, and color bitmap copy through CGM `RECTANGLE` and `CELL_ARRAY` elements.
- Provides `OutputFile` get/put support, including safety checks under `LockSafetyParams`.

Important behavior:
- `cgm_open` writes `BEGIN_METAFILE` and metafile attributes such as version, VDC type, integer/index/color precision, maximum color index, and element list.
- `cgm_begin_picture` sets abstract scaling, direct vs indexed color selection, VDC extent, edge width, optional color table, and begins the picture body.
- Indexed devices emit a CGM color table by asking the Ghostscript device to decode every color index.
- `cgm_output_page` closes the current picture if one is active.
- `cgm_close` closes any open picture, writes `END_METAFILE`, terminates the CGM state, and closes the output file.

Dependencies:
- Uses `gdevcgml.h` for CGM API calls and `gdevpccm.h` for 8-bit PC color mapping.
- Relies on Ghostscript device procs, file APIs, parameter lists, memory manager, and `fit_fill`/`fit_copy`.

Notable risks:
- If `cgm_initialize` fails after opening the file, the already-open file is not closed before returning VMerror.
- `cgm_copy_mono` slow path creates `fill_color` for each pixel but never calls `cgm_FILL_COLOR`, and it uses `cgm_set_rect(points, x, y, 1, 1)` instead of offsetting by `ix/iy`; transparent/nontrivial mono copies can therefore emit wrong rectangles/colors.
- The implementation intentionally lacks efficient tile/pattern support.
- `OutputFile` put handling may open the new file before the device open lifecycle expects the metafile header to be written.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.c

Implementation of the local CGM-writing library used by the CGM Ghostscript device.

Key responsibilities:
- Allocates and initializes `cgm_state`, including metafile defaults, picture defaults, control attributes, graphics attributes, and command buffer state.
- Implements public CGM API calls for metafile, picture, control, graphical primitive, and attribute elements.
- Serializes CGM binary command headers and command continuation chunks.
- Serializes CGM data types: integers, fixed reals, VDCs, points, strings, indexed/direct colors, RGB triples, and cell arrays.
- Tracks selected CGM state values in `cgm_state` after writing corresponding commands.

Important behavior:
- Commands are accumulated in a fixed 400-byte buffer and flushed with short or extended CGM command headers.
- `write_command` pads writes to an even byte count as required by CGM binary encoding.
- `cgm_CELL_ARRAY` always emits packed cell arrays, ignoring the caller's requested representation mode.
- `cgm_CELL_ARRAY` handles bit-aligned source offsets by combining adjacent bytes.
- Fixed real serialization floors negative values before writing whole/fraction parts.
- State-setting calls generally both write the CGM element and update `st`.
- Termination only frees the state object; metafile/picture closure is the caller's responsibility.

Dependencies:
- Internal definitions from `gdevcgmx.h` and public types from `gdevcgml.h`.
- Uses caller-provided allocator and output `FILE *`.

Notable risks:
- `cgm_set_metafile_elements` handles `cgm_set_COLOR_PRECISION` by writing `meta->color_precision` but assigns `st->metafile.color_index_precision` instead of `st->metafile.color_precision`.
- `cgm_POLYGON_SET` starts `OP(POLYGON)` instead of `OP(POLYGON_SET)`, so it may emit the wrong CGM primitive opcode.
- `put_string` uses `put_int(st, 65535, 2)` for extended string chunk length; `put_int` only handles 8/16/24/32 precision, so very long strings are likely malformed.
- Floating real representation is unimplemented in `put_real`.
- Most public functions do little range/state validation and rely on callers to maintain valid CGM sequencing.
- `cgm_CELL_ARRAY` reads `row[i + 1]` when shifting misaligned data, so callers must provide an accessible extra byte past each row's logical packed length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.h

Public interface for the local CGM-writing library.

Key contents:
- Declares opaque `cgm_state` and allocator callback structure.
- Defines coordinate, VDC, point, RGB, color, string, precision, and other CGM data types.
- Defines enum types for CGM VDC type, scaling, color selection, line/marker/edge specification modes, transparency, clipping, line/marker/text/fill/edge styles, arc closure, cell representation, and aspect source flags.
- Defines result codes: OK, wrong state, out of range, I/O error, and out of memory.
- Defines metafile element, picture element, and update-mask structures/constants.
- Declares API functions for initialization/termination, metafile lifecycle, picture lifecycle, control elements, graphical primitives, and attribute elements.

Important behavior:
- Names mostly mirror CGM standard element names, with American spellings for color/center.
- The API supports direct and indexed color, integer and real VDCs, packed cell arrays, primitive geometry, text, color tables, and aspect source flags.
- Some CGM features are acknowledged but not represented, such as character set list, character coding announcer, and pattern table.

Dependencies:
- Requires Ghostscript base types such as `byte`, `uint`, `bool`, and `FILE`.
- Implemented by `gdevcgml.c` with internal state from `gdevcgmx.h`.

Notable risks:
- The public API exposes many CGM concepts but the implementation only partially validates/implements them.
- Several fields are raw pointers into caller-owned memory, such as font lists, element lists, and strings; lifetime must outlive use by the writer state where stored.
- Function naming includes `cgm_ALT_CHARACTER_SET_INDEX` because older VAX DEC C had a 31-character name limit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgmx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgmx.h

Internal header for the CGM-writing library.

Key contents:
- Defines packed internal CGM opcode indices grouped by CGM class.
- Defines shifts used to encode command class and element id.
- Defines `struct cgm_state_s`, including output file, allocator, current metafile/picture/control/attribute state, aspect source flags, command buffer, command count, continuation state, and last result.
- Sets `command_max_count` to 400 bytes and requires it to be even.

Important behavior:
- The opcode enum is the internal bridge between symbolic API calls and CGM binary command headers.
- `cgm_state_s` stores both durable CGM settings and transient command serialization state.
- Some state areas are placeholders or comments, such as text alignment, pattern table, and color table.

Dependencies:
- Includes `gdevcgml.h` for public CGM types.

Notable risks:
- The state struct stores many fields that may be uninitialized unless the relevant API call was made.
- `source_flags` is hard-coded to 18 entries, matching the current aspect source enum count.
- Command serialization depends on enum values and bit shifts remaining consistent with CGM binary encoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgmx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcif.c

Ghostscript output driver that converts a monochrome page into CIF layout commands.

Key responsibilities:
- Defines the `cif` printer device at configurable `X_DPI`/`Y_DPI`, defaulting to 72 dpi.
- Derives a CIF cell/name from the output filename before the first dot.
- Scans rendered monochrome bits and writes CIF `B` box commands for set pixels or runs of set pixels.
- Emits CIF prologue and epilogue commands around the generated geometry.

Important behavior:
- Default path performs horizontal run coalescing: consecutive set bits in a scanline become one wider CIF box.
- `TILE` compile-time option switches to a simpler per-pixel box emission path.
- Coordinates are scaled by 4 and y is emitted as `pdev->height - lnum`.

Dependencies:
- Ghostscript printer API and scanline copying from `gdevprn.h`.

Notable risks:
- The non-`TILE` path does not flush a run if the scanline ends while `length != 0`, so runs reaching the final bit of the line can be dropped.
- The string allocation uses `length = strlen(fname) + 1`, then writes `s[length] = '\0'`; this allocates one byte too few in the no-dot case.
- The generated CIF naming and geometry are very simple and assume one-bit input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevclj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevclj.c

Ghostscript H-P Color LaserJet 5/5M driver using a 3-plane bi-level color model.

Key responsibilities:
- Defines `cljet5` and `cljet5pr` devices.
- Validates supported paper sizes and resolutions.
- Supplies supported `InputAttributes` page sizes.
- Computes default matrices for normal and rotated page output.
- Packs byte-per-pixel 3-bit color data into separate C/M/Y bit planes.
- Compresses each plane with PCL mode 2 compression.
- Emits PCL setup, raster dimensions, blank-line skips, compressed plane data, raster end, and form feed.
- Provides a special `cljet5pr` variant that performs driver-level page rotation for PCL interpreters that cannot use `setpagedevice`.

Important behavior:
- Only executive, letter, and A4 color page sizes are listed.
- Supported resolutions are 75, 100, 150, and 300 dpi, and X/Y resolution must match.
- `USE_FAST_MODE` selects the faster fixed/simple color-space path; alternate direct color mode is present in comments/conditional command emission.
- `clj_put_params` rejects unknown media sizes and rotated media for the standard driver.
- `clj_pr_put_params` can synthesize a rotated `.MediaSize` parameter list and mark the device rotated, explicitly violating the usual device invariant as documented in the comments.
- `pack_and_compress_scanline` trims trailing zero longwords from each plane before compression.

Dependencies:
- Ghostscript printer and PCL support: `gdevprn.h`, `gdevpcl.h`, parameter APIs, C parameter lists, and PCL color mappers.
- Uses `fabs` from `math_.h`.

Notable risks:
- The driver-level rotation variant mutates page size/width/height during get/put parameter paths and is intended only for specific PCL interpreter contexts.
- `clj_media_size` can use `fres.data` while only `HWSize` was supplied; if `HWResolution` was not read successfully in that path, the resolution source is fragile.
- Buffer sizing depends on `CLJ_MAX_SCANLINE` and the supported media/resolution assumptions.
- Only a narrow set of page sizes is accepted for color output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevclj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcljc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcljc.c

Ghostscript H-P Color LaserJet 5/5M contone driver, based on the CLJ driver but hardwired for 24-bit direct RGB output.

Key responsibilities:
- Defines the `cljet5c` printer device at 300 dpi, 24-bit RGB.
- Allocates raw scanline, compressed scanline, and previous-row buffers.
- Emits PCL reset, paper definition, transparency controls, render mode, resolution, direct-by-pixel RGB color model, raster start, and compression mode 3 setup.
- Copies each rendered scanline, compresses it with PCL mode 3 against the previous row, and writes it to the printer.
- Ends raster graphics and ejects the page.

Important behavior:
- Color parameters, render mode, and bits per component are hardwired.
- Uses direct RGB with 8 bits per component through `\033*v6W`.
- Compression seed row starts as zeroed `prow`.

Dependencies:
- Ghostscript printer and PCL support: `gdevprn.h`, `gdevpcl.h`.
- Uses default RGB color mapping procs.

Notable risks:
- The previous-row buffer passed to `gdev_pcl_mode3compress` is initialized but not visibly updated in this function; correctness depends on that compression helper updating or interpreting it as seed state.
- Several PCL positioning and margin constants are hard-coded.
- The device is simpler than `gdevclj.c` and lacks the paper/resolution validation logic found there.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcljc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.c

Special Ghostscript forwarding device that applies PCL5-style color mapping algorithms before passing colors to a target device.

Key responsibilities:
- Defines a forwarding `gx_device_cmap` prototype and GC descriptor.
- Initializes a cmap device over a target device with a selected mapping method.
- Exposes `ColorMappingMethod` through get/put device parameters.
- Adjusts device color model metadata depending on mapping mode.
- Supplies custom color mapping procs for gray, RGB, and CMYK color spaces.
- For non-identity mapping, forces images through the default image renderer so color mapping is applied through the cmap device.

Important behavior:
- Identity mapping forwards the target's color model and color procedures.
- Monochrome mapping converts RGB/CMYK input to gray brightness.
- Snap-to-primaries thresholds gray/RGB/CMY components to full off/on values.
- Color-to-black-over-white maps black to white and other RGB colors to black; CMYK behavior is present but explicitly noted as untested.
- `cmap_begin_typed_image` forwards high-level image handling only for identity mapping; other mappings use `gx_default_begin_typed_image`.

Dependencies:
- Ghostscript device forwarding, color conversion, fraction, image, and parameter APIs.
- Header interface from `gdevcmap.h`.

Notable risks:
- `cmap_put_params` calls `gx_forward_put_params` before reading `ColorMappingMethod`; if target parameter updates fail, behavior depends on `ecode`/`code` handling.
- The CMYK mapping path is marked untested and may not be exercised.
- Non-identity modes intentionally disable target high-level image optimizations.
- Mapping procs call the target's `get_color_mapping_procs` and assume the target implements the relevant callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.h

Public interface for the special color mapping forwarding device.

Key contents:
- Defines `gx_device_color_mapping_method_t`.
- Enumerates mapping methods: identity, snap-to-primaries, color-to-black-over-white, and monochrome.
- Defines `device_cmap_max_method`.
- Defines `gx_device_cmap` as a forwarding device plus mapping method.
- Declares GC structure support macro `public_st_device_cmap`.
- Declares `gdev_cmap_init`.

Important behavior:
- Clients may change `ColorMappingMethod` at runtime via device parameters.
- Header comments require callers to call `gs_setdevice_no_init(pgs, dev)` for every graphics state that may reference the device after changing the mapping method.

Dependencies:
- Requires Ghostscript device-forwarding types and GC macro infrastructure through includers.

Notable risks:
- The runtime-change contract is easy to miss; updating the parameter alone is not enough for existing graphics states.
- The enum order is part of the externally settable integer parameter behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcp50.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcp50.c

Ghostscript driver for the Mitsubishi CP50 color printer.

Key responsibilities:
- Defines the `cp50` 24-bit color printer device with empirically derived pixel dimensions, DPI, margins, and clipping constants.
- Implements printer output page handling to pass the requested copy count to the print-page routine.
- Copies rendered scanlines from a fixed source window into R, G, and B plane buffers.
- Rotates each plane into printer order and writes red, green, then blue plane data.
- Emits CP50-specific initialization, mode, copy-count, and image-download command sequences.
- Provides 24-bit RGB color mapping and reverse mapping.

Important behavior:
- Fixed constants define usable image region: `X_PIXEL = 474`, `Y_PIXEL = 800`, `FIRST_LINE = 140`, `LAST_LINE = 933`, `FIRST_COLUMN = 180`.
- Plane buffers are initialized to white before image data is copied.
- `cp50_output_page` opens the printer, stores `num_copies` in a global, calls the print-page proc, closes the printer, then reinitializes clist output if needed.
- The device maps RGB color indices as `R << 16 | G << 8 | B`.

Dependencies:
- Ghostscript printer API from `gdevprn.h`.

Notable risks:
- Uses a global `int copies`, making concurrent device use unsafe.
- `LAST_LINE - FIRST_LINE + 1` is 794, while `Y_PIXEL` is 800; comments say it should be close, not exact.
- Copying uses fixed pixel offsets and assumes the rendered line is large enough for `i * 3 + FIRST_COLUMN + 2`.
- Allocation failure returns `-1` rather than a specific Ghostscript VMerror.
- `cp50_output_page` repeatedly checks `code < 0` after setting `outcode` and `closecode`, so those intermediate errors are only handled later.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcp50.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcslw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcslw.c

Ghostscript driver for CoStar LabelWriter II/II Plus style label printers.

Key responsibilities:
- Defines `coslw2p` and `coslwxl` monochrome devices.
- Copies rendered monochrome scanlines, trims trailing zero words, and skips blank lines.
- Emits LabelWriter spacing, line-width, raster data, and eject commands.
- Caps output line width to 56 bytes for the 2-inch model.

Important behavior:
- `coslw2p` is 2 inches wide at 128 dpi; `coslwxl` uses 204 dpi.
- Blank lines are emitted through repeated `ESC f 1 <count>` spacing commands, chunked at 255 lines.
- If the byte width changes, the driver emits `ESC D <out_count>`.
- Raster data is introduced with `0x16`, followed by raw row bytes.
- Page eject uses `ESC E`.

Dependencies:
- Ghostscript printer API from `gdevprn.h`.

Notable risks:
- No compression is implemented; comment says it may be added later.
- The driver keeps zero initialization and unused storage beyond the active scanline, but only uses the first line-sized region.
- Width is hard-capped to 56 bytes regardless of the higher-resolution model's potential geometry.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcslw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdbit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdbit.c

Default Ghostscript device bitmap-copying implementation.

Key responsibilities:
- Implements fallback bitmap operations for devices that do not provide optimized methods.
- Implements `gx_default_tile_rectangle` through `strip_tile_rectangle`.
- Implements `gx_default_copy_mono` using fill/background plus masked fill.
- Implements `gx_default_copy_color` by grouping same-color runs into filled rectangles.
- Implements `gx_default_copy_alpha` by reading destination pixels, blending with a source color, re-encoding pixels, and copying accumulated scanlines back.
- Implements default `fill_mask` handling with optional clipping and alpha delegation.
- Implements `gx_default_strip_tile_rectangle`, which breaks tiled fills into copy operations across tile repetitions and phase/shift.
- Provides no-op/error implementations for unsupported alpha/ROP operations.
- Provides unaligned copy wrappers for mono, color, and alpha bitmap data.

Important behavior:
- `gx_default_copy_mono` uses `gx_dc_default_fill_masked`; if both zero and one colors are present, it fills the background first.
- `gx_default_copy_color` supports depths below 8 and byte-multiple depths up to 64 via fall-through byte assembly.
- `gx_default_copy_alpha` supports 1-bit via `copy_mono`; 2-bit and 4-bit alpha are blended on a 0-15 scale.
- If a blended color cannot be represented, alpha is moved toward 0 or 1 and blending retried.
- `gx_default_strip_tile_rectangle` temporarily patches `tile_rectangle` to avoid recursion when delegating to a device-specific implementation.
- Tile copying preserves bitmap ids only when a complete tile is copied; partial copies use `gs_no_bitmap_id`.
- Unaligned wrappers adjust data origin and, if raster alignment is incompatible, split the operation line by line.

Dependencies:
- Core Ghostscript graphics/device headers: device procs, memory devices, clipping devices, drawing colors, raster ops, bitmap ids, interrupt checks, and line accumulation macros.

Notable risks:
- These implementations are intentionally slow fallback paths.
- `gx_default_copy_color` relies on fall-through switch behavior for packed byte assembly.
- `gx_default_copy_alpha` can allocate full input/output scanline buffers and requires working `get_bits`, `decode_color`, and `encode_color` device procs.
- The 24-bit unaligned color adjustment has special modular arithmetic that is easy to break.
- Temporarily mutating a device procedure in `gx_default_strip_tile_rectangle` is fragile if device procs are shared or used concurrently.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.c

Sample helper for devices that expose a PostScript CIE Color Rendering Dictionary through device parameters.

Key responsibilities:
- Defines sample CRD constants: white point, PQR/LMN ranges, MatrixABC, encode/transform procedures, and a simple render table.
- Implements `sample_device_crd_get_params`.
- Writes a constant `CRDName` parameter when requested.
- Builds and initializes a `gs_cie_render` structure when the named CRD parameter is requested.
- Writes the CRD through `param_write_cie_render1`.
- Optionally exposes the address of the sample `TransformPQR` procedure as a string parameter.

Important behavior:
- The sample CRD mostly uses default PostScript values with optional "dented" transform/encode procedures.
- `DENT` is currently neutral because `dent_PQR` and `dent_LMN` are `1.0`.
- `bit_EncodeABC_proc` applies `pow(max(in, 0), 0.45)`.
- Render table data is a no-op 2x2x2 RGB cube.
- Built CRDs are reference-counted and released after writing to the parameter list.

Dependencies:
- Ghostscript CIE/color rendering internals: `gscspace.h`, `gscrd.h`, `gscrdp.h`, parameter APIs, client device APIs, memory/string helpers.

Notable risks:
- Comments explicitly call out that storing/exporting a procedure address through an allocated string is a shortcut and not recommended.
- This is sample code, not a full device-specific CRD management framework.
- The optional procedure-address parameter is process/address-space specific and not portable as serialized data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.h

Header interface for the sample device CRD helper.

Key contents:
- Include guard `gdevdcrd_INCLUDED`.
- Declares `sample_device_crd_get_params(gx_device *pdev, gs_param_list *plist, const char *crd_param_name)`.

Role:
- Lets device implementations expose the sample CRD-building helper from `gdevdcrd.c` in their get-params path.

Dependencies:
- Requires `gx_device` and `gs_param_list` types to be visible to includers.

Notable risks:
- The header exposes only the helper declaration; all CRD behavior and limitations live in the C file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.h -->