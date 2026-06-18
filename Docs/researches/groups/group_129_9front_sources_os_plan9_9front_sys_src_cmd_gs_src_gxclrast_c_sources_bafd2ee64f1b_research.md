# Group Research: 9front Ghostscript command-list, color, and clipping sources

This group covers Ghostscript rendering internals under `sources/os/plan9/9front/sys/src/cmd/gs/src`. The files are in Subset A because the `sources/os/plan9/9front` source tree is included, but these particular files are graphics command-list/color/clipping code rather than filesystem code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrast.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrast.c

Command-list interpreter and rasterizer for Ghostscript band playback.

Key behavior:
- Defines `clist_playback_band`, the main interpreter loop for command-list stream opcodes.
- Maintains a refilled command buffer, current clist drawing state, tile state/cache entries, path state, clipping path, imager state, current device color, image state, halftone buffer, and optional compositor target device.
- Decodes command families for misc state, colors and delta colors, rectangles, tile/copy bitmap operations, extended graphics state, image setup/data, serialized params, compositors, serialized halftones, drawing colors, path segments, and path painting.
- Dispatches decoded drawing operations to target device procs such as `fill_rectangle`, `strip_tile_rectangle`, `copy_mono`, `copy_color`, `copy_alpha`, `fill_mask`, `strip_copy_rop`, `begin_typed_image`, `gx_fill_path_only`, and `gx_stroke_path_only`.
- Handles compressed bitmap/tile payloads using RunLength and CCITTFax decode helpers; unpacks short rasters into aligned buffers.
- Reconstructs compact path segment encodings through `clist_decode_segment`, including relative lines, compact curves, closepath, and polyfill shapes.
- Reads serialized color spaces, including temporary DeviceGray/RGB/CMYK and Indexed spaces with table or proc-backed lookup maps.
- Reads `put_params` command payloads into a `gs_c_param_list` and applies them to the clist reader device.
- Reads compositor commands by looking up compositor IDs, deserializing compositor payloads, creating compositor devices, and invoking clist read-update hooks.
- Reads serialized halftones in one or more segments and installs them with `gx_ht_read_and_install`.

Notable dependencies:
- Command encoding definitions and clist structures from `gxcldev.h`/`gxclpath.h`.
- Color-space, color-map, halftone, image, path, compositor, stream, and device-proc infrastructure.
- Compression helpers initialized in `gxclutil.c` and zlib/CCITT/RLE stream templates elsewhere.

Research notes:
- The file is the read-side counterpart to clist writing utilities and rectangle/path command emitters.
- Bad opcodes are treated as fatal and dump command-buffer context for debugging.
- Some behavior is intentionally limited: only DeviceGray/RGB/CMYK color-space indices are accepted in `read_set_color_space`; others return rangecheck/NYI.
- Alpha is routed through RGB-alpha mapping/copy-alpha paths, but CMYK remapping comments elsewhere note alpha is ignored for CMYK.
- The interpreter owns multiple temporary allocations and carefully frees indexed tables/maps, clip paths, paths, imager state, data buffers, halftone buffers, and compositor devices on exit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclread.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclread.c

Command-list band reader and rendering bridge.

Key behavior:
- Defines a `stream_band_read_state` stream filter that scans a band index file and reads only command runs overlapping the requested band range.
- `s_band_read_process` alternates between reading command bytes from the command file and scanning `cmd_block` records from the band file.
- `clist_setup_params` replays initial clist parameters for async rendering setup.
- `clist_get_bits_rectangle` rasterizes requested lines into a buffer device and then copies the requested rectangle to caller-provided `get_bits` buffers.
- Selects plane-specific rendering when possible, but falls back to full-pixel rendering if multiple planes are requested or RasterOp requires slow full-color handling.
- `clist_rasterize_lines` renders one band at a time, sets up the memory/buffer device over the reader’s scratch storage, and caches current rasterized band bounds.
- `clist_render_rectangle` renders one rectangle across one or more bands, including saved/placed pages, and clears the destination buffer when requested.
- `clist_playback_file_bands` opens saved page band/command files if needed, wraps the band-read filter in a stream, and calls `clist_playback_band`.

Notable dependencies:
- `gxclrast.c` for actual command playback.
- Printer/buffer-device helpers such as `gdev_prn_colors_used` and `gdev_create_buf_device`.
- Clist file abstraction and band-page metadata.

Research notes:
- This file separates band selection and buffering from opcode interpretation.
- It supports incremental `get_bits_rectangle` delivery when requested lines cross band boundaries.
- It includes a design note that printer-device dependencies are undesirable but currently required for colors-used and buffer-device creation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrect.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrect.c

Rectangle-oriented command-list writer operations.

Key behavior:
- Encodes rectangles compactly with full, short-delta, tiny-delta, and special adjacent rectangle forms through `cmd_write_rect_cmd`.
- Implements clist writer device procedures for `fill_rectangle`, `strip_tile_rectangle`, `copy_mono`, `copy_color`, `copy_alpha`, and `strip_copy_rop`.
- Tracks colors used per band and updates clist state for current colors, tile colors, tile phase, logical operation state, and clip state.
- Emits bitmap payloads with `cmd_put_bits`, choosing compression and splitting large transfers by height or row width when a payload cannot fit.
- Handles tile caching and tile ID lookup/change commands before tiled fills and ROP texture operations.
- Converts high-level RasterOp calls into clist state updates plus nested simpler fill/copy operations, while marking slow ROP cases for later render-plane selection.

Notable dependencies:
- Writer-side macros and state from `gxcldev.h`.
- Tile, bitmap, RasterOp, and color-command helpers from the clist infrastructure.
- Default device fallback procedures for cases too large or unsupported by the command buffer.

Research notes:
- The file is focused on producing compact command streams; much complexity is about command buffer limits and avoiding repeated state emission.
- Very large bitmaps or tiles are recursively split; some tile limit cases only split by scan line and punt if a single scan line cannot fit.
- CMYK RasterOps are conservatively marked slow when destination involvement makes plane-wise rendering unsafe.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclutil.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclutil.c

Shared command-list writing utilities.

Key behavior:
- Provides debug opcode name tables, per-op statistics, and `cmd_print_stats` under `DEBUG`.
- Writes buffered command lists to command and band files via `cmd_write_band` and `cmd_write_buffer`.
- Manages command buffer allocation/alignment and per-band/range command list linkage in `cmd_put_list_op` and `cmd_put_range_op`.
- Encodes variable-length integers with `cmd_size_w`/`cmd_put_w`.
- Defines color selector descriptors for color0, color1, tile color0, and tile color1.
- Encodes colors either as full values with omitted trailing zero bytes or as compact deltas, including special handling for `gx_no_color_index`.
- Emits commands for tile colors, tile phase, logical operation enable/disable, clipping enable/disable, logical operation value, and serialized parameter lists.
- Initializes CCITTFax encode/decode and RunLength encode/decode stream states for command-list compression.

Notable dependencies:
- Clist writer structures, command formats, stream filter templates, parameter serialization, and path-command statistics.

Research notes:
- This file is central write-side infrastructure used by rectangle/path/image command emitters.
- Low-memory warnings may be converted into retryable VM errors unless the writer is configured to ignore them.
- Color delta encoding is carefully tied to `gx_color_index` byte width and device depth; reader decoding in `gxclrast.c` mirrors it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclzlib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclzlib.c

zlib stream-state initialization for RAM-based command-list band lists.

Key behavior:
- Holds static prototype `stream_zlib_state` objects for compression and decompression.
- `gs_cl_zlib_init` initializes both states with zlib defaults, disables zlib wrapper bytes, and installs encode/decode stream templates.
- `clist_compressor_state` and `clist_decompressor_state` return the prepared prototype stream states.

Notable dependencies:
- Ghostscript stream/zlib integration from `szlibx.h`.
- RAM clist infrastructure from `gxclmem.h`.

Research notes:
- This file only supplies reusable stream prototypes; actual clist code copies/uses these states elsewhere.
- It must be compiled with access to the zlib source include directory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.c

Core Ghostscript device color mapping implementation.

Key behavior:
- Defines GC descriptors for `gx_device_color`.
- Implements default separable/linear `encode_color` and `decode_color` using device component shifts, masks, and bit widths.
- Provides error and grayscale fallback encoders, including compatibility with old devices that only implement `map_rgb_color`.
- Defines default color-space-to-device-model conversions for DeviceGray, DeviceRGB, DeviceCMYK, and DeviceRGBK.
- Supplies default color-component-name lookup for Gray/RGB/CMYK/RGBK devices.
- Selects direct vs halftoned color-map procedure tables based on `gx_device_must_halftone`.
- Implements remapping for DeviceGray, DeviceRGB, and DeviceCMYK client colors, preserving original client-color values in the device color.
- Maps gray/RGB/CMYK/RGB-alpha/Separation/DeviceN fractions through device color-model procs, transfer maps, device polarity, encode_color, and halftone fallback.
- Implements transfer-map helpers: identity transfer, mapped transfer, identity-map initialization, and optional interpolating fraction map.
- Provides default device color-index mappings for 1-bit monochrome, grayscale, 8-bit gray, RGB, CMYK, and RGB-alpha compatibility.

Notable dependencies:
- `gxcspace.h`, `gxcmap.h`, `gxdcconv.h`, `gxcdevn.h`, transfer-map and halftone rendering infrastructure.

Research notes:
- The central pipeline is: color space fractions -> device color model components -> transfer/polarity adjustment -> direct color index or halftoned DeviceN color.
- DeviceN and Separation support use `gs_devicen_color_map` to place input components into device colorant order.
- Direct mapping falls back to halftoning if `encode_color` returns `gx_no_color_index`.
- CMYK remapping explicitly ignores alpha.
- The RGB-to-CMYK default path contains a suspicious fallback expression using `min(m, g)` when deriving `k`; this may be intentional legacy code but deserves caution if touched.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.h

Internal interface for Ghostscript color mapping procedures.

Key contents:
- Defines procedure signatures for mapping gray, RGB, CMYK, RGB-alpha, Separation, and DeviceN concrete colors to `gx_device_color`.
- Defines device color-space-to-color-model mapping procs for gray/RGB/CMYK inputs.
- Defines `gx_cm_color_map_procs` for device-provided color-model conversion hooks.
- Defines `gx_color_map_procs` for imager-state color remapping hooks and halftone-status testing.
- Declares `gx_get_cmap_procs`, `gx_default_get_cmap_procs`, and `gx_set_cmap_procs`.
- Provides macros for invoking concrete color remappers through the current imager-state procedure table.
- Declares default conversions, color-component-index routines, color-mapping-proc routines, encode/decode routines, grayscale encoders, and the `unit_frac` clamp/convert macro.
- Defines component-name type constants, including ordinary names and separation names.

Notable dependencies:
- `gscsel.h`, `gxfmap.h`, `gxcindex.h`, and `gxcvalue.h`.

Research notes:
- This header separates two layers: color space to device color model, and final device color rendering/halftoning.
- Device methods can override color-model conversions while retaining generic rendering logic from `gxcmap.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcolor2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcolor2.h

Internal Level 2 color support definitions.

Key contents:
- Defines `gs_indexed_map`, a reference-counted cache for Indexed color procedure values or Separation tint-transform values.
- Declares `lookup_indexed_map`, `alloc_indexed_map`, and `free_indexed_map`.
- Defines `gs_pattern1_instance_t` for PatternType 1 instances.
- Pattern instance stores template data, tiling-to-device step matrix, tiling-space bounding box, simple/uses-mask flags, device size, and cached bitmap ID.
- Provides private structure descriptor macros for indexed maps and pattern instances.

Notable dependencies:
- Client color definitions, matrices, reference counting, and bitmap IDs.

Research notes:
- `gxclrast.c` uses the indexed map declarations when reconstructing Indexed color spaces during clist playback.
- The pattern portion documents Ghostscript’s adjusted “tiling space” model for efficient tile-copy coverage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcolor2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcomp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcomp.h

Compositor type and object definitions for Ghostscript compositing.

Key contents:
- Assigns one-byte command-list compositor IDs for alpha, overprint, and PDF 1.4 transparency compositors.
- Defines `gs_composite_type_procs_t` with hooks for default compositor creation, equality, command-list serialization/deserialization, clist write update, and clist read update.
- Defines `gs_composite_type_t` with compositor ID and proc table.
- Declares default clist write/read update implementations.
- Defines common reference-counted `gs_composite_t` object layout and `gs_composite_id`.

Notable dependencies:
- `gscompt.h`, reference counting, bit format definitions, `gx_device`, and `gs_imager_state`.

Research notes:
- The one-byte stable compositor ID exists because command lists may be replayed in a different address space where method-table pointers are meaningless.
- `gxclrast.c` uses this interface to deserialize and install compositors during clist playback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcomp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcoord.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcoord.h

Internal graphics-state coordinate transformation declarations.

Key contents:
- Declares `gx_translate_to_fixed` for fixed-point translation and existing path translation.
- Declares `gx_scale_char_matrix` for CTM and character matrix oversampling.
- Declares `gx_matrix_to_fixed_coeff` for deriving fast fixed-point distance-transform coefficients from a matrix.

Notable dependencies:
- Requires graphics coordinate/matrix state definitions through `gscoord.h`.

Research notes:
- This is a small internal API header; implementations live elsewhere.
- It is used by character/path rendering code that needs fixed-point CTM support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcoord.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.c

Implementation of Ghostscript clipping paths and clipping rectangle lists.

Key behavior:
- Defines structure descriptors and GC relocation/enumeration logic for clip paths, clip lists, clip rects, clip path-list nodes, clip enumerators, and clipping devices.
- Manages clipping path allocation, local/shared initialization, reference counting, assignment, unsharing, and freeing.
- Maintains both path-segment and rectangle-list representations, with validity flags and cached inner/outer boxes.
- Converts rectangle-list-only clipping paths back into path segments via `gx_cpath_to_path`.
- Implements fast rectangle clipping/intersection paths and falls back to slow path intersection for nontrivial clipping.
- Tracks previous clipping paths in `gx_cpath_path_list` when nontrivial intersections need clippath reconstruction history.
- Scales clipping paths and rectangle lists by powers of two.
- Initializes/free clip lists and converts fixed rectangles into integer clip rectangles.
- Enumerates rectangle-list clipping paths as path edges through `gx_cpath_enum_init` and `gx_cpath_enum_next`.
- Provides debug printing for clip paths and rectangle lists.

Notable dependencies:
- Path, clipping accumulator, fixed-point geometry, graphics state, and memory/reference-counting infrastructure.

Research notes:
- Rectangle clipping is optimized heavily; a clip path may be represented only as a rectangle list until a path representation is demanded.
- `gx_cpath_unshare` has an explicit NYI for copying shared rectangle lists; callers should be cautious around shared-list mutation.
- The rectangle-list enumerator traces left/right edges and may produce many small line segments for complex clip lists.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.h

Internal clipping list and clipping device definitions.

Key contents:
- Defines `gx_clip_rect`, a doubly linked rectangle with integer bounds and enumeration bookkeeping.
- Defines `gx_clip_list`, which is either a single rectangle or a linked list with dummy head/tail entries.
- Provides structure descriptor macros for clip rect/list GC support.
- Defines `clip_list_is_rectangle`.
- Defines `gx_device_clip`, a forwarding clipping device with clip list, current cursor, translation, cached clipping box, and target forwarding fields.
- Declares constructors for translated clip devices and clip-path devices.
- Declares clip-list initialization/freeing, outer-box setup, and rectangle-list access for clip paths.

Notable dependencies:
- Requires device-forwarding definitions from `gxdevice.h`.

Research notes:
- The header intentionally exposes implementation structs so clients can allocate clip lists/devices on the stack.
- Clip devices assume the target clipping box and clip list remain const after open because clipping box data is cached.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcspace.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcspace.h

Internal color-space type/class interface.

Key contents:
- Defines `gs_color_space_type_s`, the method table for all color-space implementations.
- Records color-space index, base/alternate-space eligibility, concrete structure type, and method pointers.
- Methods include component count, base-space access, initial color, restriction, concrete-space lookup, concretization, concrete remap, direct remap, install, overprint setup, cspace/color reference-count adjustment, serialization, and linearity testing.
- Provides macros for invoking each method.
- Declares standard structure descriptors and standard helper procedures for common component counts, init/restrict behavior, no-op/default behavior, serialization, and linearity.
- Declares DeviceGray/RGB/CMYK concretize/remap implementations from `gxcmap.c`.
- Declares `gs_cspace_init` and `gs_cspace_alloc`.

Notable dependencies:
- Client color-space API, client color values, color selection, and fraction types.

Research notes:
- This header is the core internal abstraction that lets `gxcmap.c`, `gxclrast.c`, and color-space implementations share a uniform color-space method table.
- Pattern spaces are special because component counts can depend on an underlying space.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcspace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.c

Color lookup-table interpolation implementation.

Key behavior:
- `gx_color_interpolate_nearest` selects nearest table entries for 3-D or 4-D color lookup tables and converts byte table values to `frac`.
- `interpolate_accum` performs trilinear interpolation for 3-D tables.
- For 4-D tables, interpolation is implemented as two 3-D interpolations blended along the first dimension.
- Handles boundary cells by reusing the last available sample when an index is at the maximum dimension.
- `gx_color_interpolate_linear` is the public entry point for linear interpolation.

Notable dependencies:
- Fixed-point helpers from `gxfixed.h`, fraction helpers from `gxfrac.h`, and table layout from `gxctable.h`.

Research notes:
- Table entries are byte-valued and promoted to Ghostscript fractions for output.
- The implementation assumes indices are already range-checked by the caller as documented in the header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.h

Interface for 3-D and 4-D color lookup tables.

Key contents:
- Defines `gx_color_lookup_table` with dimension count, dimensions, output component count, and table string array.
- Documents table layout for 3-D and 4-D tables.
- Declares `gx_color_interpolate_nearest` and `gx_color_interpolate_linear`.
- Inputs are fixed-point table indices; outputs are fraction color values.

Notable dependencies:
- Fixed-point and fraction definitions.

Research notes:
- 4-D tables are stored as an array indexed by the first two dimensions, each entry containing the remaining dimensions and output components.
- String sizes are retained largely to simplify garbage collection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxctable.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcvalue.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcvalue.h

Device color-value scalar definition and conversion macros.

Key contents:
- Defines `gx_color_value` as `unsigned short`.
- Defines size/bits/max constants for device color values.
- Provides byte conversion macros `gx_color_value_to_byte` and `gx_color_value_from_byte`.
- Provides fraction conversion macros `frac2cv` and `cv2frac`.

Notable dependencies:
- Assumes fraction conversion helpers such as `frac2ushort` and `ushort2frac` are already available to includers.

Research notes:
- Device color values are currently 16-bit, with comments allowing the possibility of fewer effective bits in the future.
- This type is used across device encode/decode and color mapping paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcvalue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.c

Device color-space conversion helpers.

Key behavior:
- Converts RGB fractions to gray using luminance weights.
- Converts RGB to CMYK, including black generation and undercolor removal from the imager state when available.
- Converts CMYK to gray through luminance of CMY plus black.
- Converts CMYK to RGB, using Adobe-compatible formulas when `USE_ADOBE_CMYK_RGB` is defined.
- Emits color-conversion debug traces under the `c` debug flag.

Notable dependencies:
- Fraction arithmetic, luminance weights, imager-state transfer maps, and color-map helpers.

Research notes:
- Gray-to-RGB and gray-to-CMYK are treated as trivial and implemented elsewhere.
- The file supports both Adobe-style CMYK/RGB conversion and an alternate multiplicative model behind preprocessor conditionals, but this build selects Adobe behavior.
- Passing a null imager state changes RGB-to-CMYK behavior to use default identity-like assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcconv.c -->