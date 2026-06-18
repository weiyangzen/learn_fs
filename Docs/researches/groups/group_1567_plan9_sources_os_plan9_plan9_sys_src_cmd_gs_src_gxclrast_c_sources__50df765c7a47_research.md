# Group Research: group_1567_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxclrast_c_sources__50df765c7a47

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`.

This grouped report covers Ghostscript command-list rasterization, command-list rectangle writing, color mapping, clipping path, and color-space support files under the Plan 9 source import. Every listed source file was read completely and is reported in its own finalizer-delimited block.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrast.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrast.c

## Purpose
Implements the Ghostscript command-list interpreter/rasterizer. It reads compact command streams for selected bands or saved pages, reconstructs graphics state, color state, paths, clipping, images, halftones, compositors, and bitmap operands, then dispatches equivalent drawing operations to a target device.

## Public Surface
- `clist_playback_band(...)`: main playback engine used by command-list readers to render or set up from a filtered band stream.

## Implementation
- Maintains an aligned command buffer with refill helpers, variable-length integer decoding, and direct stream reads for payloads larger than the current buffer contents.
- Decodes compact rectangle, tile, color, delta-color, copy-mono/color/alpha, RasterOp, path segment, path paint, image, clipping, color-space, halftone, compositor, and parameter commands.
- Reconstructs per-band `gx_clist_state`, tile cache references, tile phases, drawing colors, logical operations, image enumerators, and a local `gs_imager_state`.
- Decompresses bitmap/tile data using RunLength or CCITTFax decode helpers and expands short scanlines into device raster alignment when needed.
- Handles clipping commands by accumulating clipping marks into `gx_device_cpath_accum`, then re-enabling clipping only when the resulting clip does not contain the whole target box.
- Supports command-list compositors by deserializing a compositor id/payload, creating a compositor device over the current target, and invoking compositor read-update hooks.

## Dependencies
Uses most of the Ghostscript graphics core: command-list structures from `gxcldev.h`, paths and clip paths, imager state, device colors, color spaces, images, halftones, serialization, stream filters, compositors, and device drawing procedures.

## Risks and Notes
- Bad or inconsistent command bytes become fatal errors after dumping buffer context.
- Several paths trust command-list invariants established by writer-side code, such as decompressed bitmap payloads fitting the command buffer.
- Indexed color-space data and large image data may allocate transient heap buffers; cleanup is centralized at the `out` label.
- Alpha copy explicitly cannot combine with RasterOp in this implementation.
- The `read_create_compositor` format has no independent total length field and relies on the design assumption that compositor command payloads fit in the command buffer.

Filesystem relevance: this is band-list playback for Ghostscript rendering. It reads command-list streams, including band files through callers, but does not implement filesystem semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclread.c

## Purpose
Implements command-list reading and band rasterization orchestration. It filters command-list files by band range, initializes reader state, renders requested bands into a buffer device, and serves `get_bits_rectangle` requests from rasterized bands.

## Public Surface
- `clist_setup_params(gx_device *dev)`: plays the initial parameter command for async rendering setup.
- `clist_get_bits_rectangle(...)`: rasterizes enough command-list content to return requested pixels.
- `clist_render_rectangle(...)`: renders an arbitrary rectangle of the command list into a caller-supplied device.

## Implementation
- Defines `stream_band_read_state` and `s_band_read_process`, a stream filter that walks the band index file and only emits command runs whose band ranges overlap the requested band range.
- `clist_select_render_plane` chooses a single render plane when possible, but falls back to full-pixel rendering for slow RasterOps.
- `clist_rasterize_lines` lazily renders a band into the command-list reader memory buffer and then rebinds the buffer device to the requested line subset.
- `clist_get_bits_rectangle` supports chunky, planar, bit-planar, selected-plane, pointer, and copy output modes; if a rectangle spans bands, it returns pieces or punts to the default implementation when the request cannot be satisfied incrementally.
- `clist_playback_file_bands` opens saved page command and band files when needed, wraps them in the band-filter stream, calls `clist_playback_band`, and closes only the files it opened.

## Dependencies
Uses Ghostscript clist file APIs, stream APIs, printer buffer-device helpers, rendering planes, memory devices, and `clist_playback_band` from `gxclrast.c`.

## Risks and Notes
- The file comments acknowledge an architectural leak: it includes `gdevprn.h` because some command-list reader services are still printer-device-specific.
- Band filtering depends on consistent `cmd_block` positions in the band index file and command file.
- Multiple selected planes fall back to the default `get_bits_rectangle` path rather than partial clist optimization.

Filesystem relevance: this file opens and reads command-list band files through Ghostscript's clist file abstraction, but its role is rendering-band I/O rather than filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrect.c

## Purpose
Implements rectangle-oriented command-list writing for fills, tiles, mono/color/alpha copies, and RasterOp strip copies. It converts device drawing calls into compact command opcodes and payloads.

## Public Surface
- `cmd_write_rect_cmd(...)`: emits a rectangle command using compact full, short, tiny, or delta encodings.
- Device procedures: `clist_fill_rectangle`, `clist_strip_tile_rectangle`, `clist_copy_mono`, `clist_copy_color`, `clist_copy_alpha`, and `clist_strip_copy_rop`.

## Implementation
- Tracks prior rectangle state and writes small deltas when possible, falling back to full variable-length rectangle coordinates.
- Fill and tile rectangle procedures update color/tile state, disable incompatible logical operations when needed, and emit rectangle commands per affected band.
- Mono/color/alpha copy procedures compress bitmap payloads with allowed compression modes and split transfers by height or row width when a single command would exceed limits.
- Tile and RasterOp handling caches tile ids, writes tile color and phase changes, and may synthesize ids for anonymous texture tiles.
- `clist_strip_copy_rop` estimates colors used, marks slow RasterOps for render-plane decisions, writes texture tile state, enables the logical operation, then delegates to fill/copy commands while suppressing their normal RasterOp disabling.

## Dependencies
Uses clist command/state macros, bitmap compression helpers from other clist files, RasterOp tables/macros, tile cache helpers, and Ghostscript device procedures.

## Risks and Notes
- Some oversized tile cases are handled by scanline subdivision; shifted multi-line tile fallback is explicitly not handled.
- The CMYK RasterOp path includes a hack that treats 4-component devices as subtractive and flags slow ROPs for full-pixel rendering.
- `copy_alpha` returns an unknown error when the target disables non-1-bit alpha copy support.

Filesystem relevance: none directly. This is command serialization for banded rendering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclutil.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclutil.c

## Purpose
Provides shared command-list writing utilities: buffered command output, band-list flushing, variable-length integer encoding, compact color encoding, logical-operation/clipping state commands, serialized parameter commands, and filter initializers.

## Public Surface
- `cmd_write_buffer(...)`: writes all pending band and band-range command lists to command and band files.
- `cmd_put_list_op(...)` and `cmd_put_range_op(...)`: reserve command payload space in per-band or range command lists.
- `cmd_size_w` / `cmd_put_w`: variable-length positive integer encoding.
- Color/state helpers: `cmd_put_color`, `cmd_set_tile_colors`, `cmd_set_tile_phase`, `cmd_put_enable_lop`, `cmd_put_enable_clip`, `cmd_set_lop`, `cmd_update_lop`.
- `cmd_put_params(...)`: serializes device parameter lists into an extended command.
- Filter setup helpers: `clist_cfe_init`, `clist_cfd_init`, `clist_rle_init`, `clist_rld_init`.

## Implementation
- Buffers commands in memory as linked `cmd_prefix` chunks grouped by band or band range, flushing to the clist command file plus band index file when the buffer fills.
- Converts low-memory warnings into retryable VM errors unless the writer is configured to ignore such warnings.
- Encodes colors either as full values with trailing zero-byte suppression or as packed byte deltas from the previous color value.
- Handles the special `gx_no_color_index` value as a distinct compact command case.
- Serializes parameter lists into a local buffer when small, otherwise writes directly into reserved command-list space and backs out by shortening the command if serialization fails.

## Dependencies
Uses clist file APIs, command-list state definitions, Ghostscript parameter serialization, RunLength and CCITTFax stream filters, and memory/error helpers.

## Risks and Notes
- Color delta encoding has format-specific packing for odd byte counts; reader and writer must remain exactly synchronized.
- `cmd_put_params` requires the serialized parameter list to fit in the command buffer once reserved.
- Hard file I/O errors make the current clist writer non-retryable; low-memory warnings are deliberately promoted for recovery behavior.

Filesystem relevance: this file writes command-list and band-index data through Ghostscript clist files. It is renderer serialization infrastructure, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclzlib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclzlib.c

## Purpose
Initializes zlib compressor/decompressor prototype states for RAM-based command-list band lists.

## Public Surface
- `gs_cl_zlib_init(gs_memory_t *mem)`: initializes global zlib encode/decode stream states with raw deflate mode.
- `clist_compressor_state(void *client_data)`: returns the compressor prototype.
- `clist_decompressor_state(void *client_data)`: returns the decompressor prototype.

## Implementation
- Stores two static `stream_zlib_state` objects.
- Sets zlib defaults, sets `no_wrapper = true`, and assigns encode/decode templates.
- The `mem` and `client_data` arguments are not used by the current implementation.

## Dependencies
Requires Ghostscript zlib stream support via `szlibx.h` and clist memory interfaces.

## Risks and Notes
- Static state means callers receive prototypes to copy or reference; mutation after initialization would be global.
- The file must be compiled with zlib include paths, as noted by the source comment.

Filesystem relevance: none directly. It configures compression for in-memory band-list data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.c

## Purpose
Implements Ghostscript color mapping: device color encode/decode defaults, color-space-to-device-color-model conversions, component name lookup, color remapping into direct or halftoned device colors, transfer-map support, and legacy map_rgb/map_color helpers.

## Public Surface
- Device color packing: `gx_default_encode_color`, `gx_default_decode_color`, error encode/decode procedures, gray encode helpers, and backward-compatible gray encoding.
- Color-model mapping procedure providers for DeviceGray, DeviceRGB, DeviceCMYK, and DeviceRGBK.
- Component lookup procedures for Gray/RGB/CMYK/RGBK devices.
- Cmap procedure selection: `gx_get_cmap_procs`, `gx_default_get_cmap_procs`, `gx_set_cmap_procs`.
- Standard color-space remappers/concretizers for DeviceGray, DeviceRGB, and DeviceCMYK.
- Transfer helpers: `gs_identity_transfer`, `gs_mapped_transfer`, `gx_set_identity_transfer`, optional interpolation map function.
- Legacy/default device color mappers for monochrome, grayscale, RGB, CMYK, and RGB-alpha APIs.

## Implementation
- For separable linear devices, encodes color indexes by shifting each component into the device-specified bit fields and decodes by scaling bit-field values back to `gx_color_value`.
- Provides default conversions among Gray, RGB, CMYK, and RGBK color models, including RGB to CMYK through black generation and undercolor removal when imager state is available.
- Chooses halftoned or direct color mapping procedures depending on `gx_device_must_halftone`.
- Direct mapping applies color model conversion, transfer functions, polarity handling, conversion to `gx_color_value`, then device `encode_color`; if direct encoding fails, it falls back to halftoned rendering.
- Halftoned mapping converts to device colorants, applies transfer/polarity handling, then calls `gx_render_device_DeviceN` and loads the resulting device color.
- DeviceN and Separation mapping use `gs_devicen_color_map` to place source components into device colorant order, with special handling for Separation All and additive-device inversion.
- DeviceGray/RGB alpha remappers use `map_rgb_alpha` only where applicable; CMYK alpha is explicitly ignored.

## Dependencies
Uses device color, imager state, transfer maps, halftone rendering, DeviceN colorant mapping, color conversion helpers from `gxdcconv.c`, luminance weights, and Ghostscript device procedure vectors.

## Risks and Notes
- Debug checks require separable-linear devices for the default encode/decode routines, but release behavior still assumes correct device metadata.
- `gx_error_decode_color` loops from `num_components` down to zero, which writes one past the usual last component index if the buffer is only `num_components` elements.
- CMYK alpha handling is marked ignored.
- RGB-to-CMYK fallback without imager state contains a suspicious `min(m, g)` term where yellow would be expected; the surrounding comment says this mode supports PCL RasterOp behavior.

Filesystem relevance: none. This is rendering color infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.h

## Purpose
Declares the color mapping interfaces that connect Ghostscript color spaces and imager state to device color models and device color indexes.

## Public Surface
- Function-signature macros for concrete gray/RGB/CMYK/RGBA/Separation/DeviceN remapping.
- `gx_cm_color_map_procs`: maps standard color spaces into a device colorant vector.
- `gx_color_map_procs`: maps concrete color values into a `gx_device_color` and reports whether the mapping is halftoned.
- Procedure selection APIs: `gx_get_cmap_procs`, `gx_default_get_cmap_procs`, `gx_set_cmap_procs`.
- Remap macros: `gx_remap_concrete_gray`, `gx_remap_concrete_rgb`, `gx_remap_concrete_cmyk`, `gx_remap_concrete_rgb_alpha`, `gx_remap_concrete_separation`, `gx_remap_concrete_devicen`.
- Device procedure typedefs for color component lookup, color-model mapping procs, color encoding, and color decoding.
- Default procedure declarations for Gray/RGB/CMYK/RGBK devices and error handlers.

## Semantics
- Devices may provide custom color-space-to-color-model conversion procedures; otherwise standard conversions are used.
- Component name lookup distinguishes ordinary names from separations via `component_type`.
- The header includes `gxcindex.h` and `gxcvalue.h`, tying color mapping to both packed device color indexes and driver-interface component values.

## Dependencies
Requires Ghostscript device color structures, imager state, fractional color maps, color selection ids, and device procedure conventions.

## Risks and Notes
- Many macros dispatch through procedure pointers and assume `pis->cmap_procs` has been refreshed after device changes.
- The duplicated CMYK default declarations are harmless but redundant.

Filesystem relevance: none. This is a rendering interface header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcolor2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcolor2.h

## Purpose
Defines internal Level 2 color support structures for cached Indexed/Separation color transforms and uncolored tiling pattern instances.

## Public Surface
- `gs_indexed_map`: reference-counted cache for indexed lookup or separation tint-transform results, including procedure union, `proc_data`, value count, and float values.
- `lookup_indexed_map(...)`: lookup procedure that returns cached map values.
- `alloc_indexed_map(...)`: allocates a map and its value storage.
- `free_indexed_map(...)`: reference-count free procedure.
- `gs_pattern1_instance_t`: internal representation of a Type 1 pattern instance with template, step matrix, tiling bbox, simplicity flag, mask flag, device size, and bitmap id.

## Dependencies
Includes Level 2 color public declarations, matrices, reference counting, and bitmap ids. Structure descriptors are implemented in related color/pattern source files.

## Risks and Notes
- `gs_indexed_map.values` is described as a flexible logical array but is stored as a pointer, so allocation and reference-count management must stay paired.
- Pattern instance comments document adjusted tiling-space semantics used to simplify repeated tile coverage calculations.

Filesystem relevance: none. This is color/pattern rendering metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcolor2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcomp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcomp.h

## Purpose
Defines the internal compositor type model used by Ghostscript devices and command lists.

## Public Surface
- Compositor ids: `GX_COMPOSITOR_ALPHA`, `GX_COMPOSITOR_OVERPRINT`, `GX_COMPOSITOR_PDF14_TRANS`.
- `gs_composite_type_procs_t`: method table for default compositor creation, equality, command-list serialization/deserialization, clist writer update, and clist reader update.
- `gs_composite_type_t`: compositor type descriptor with one-byte command-list id and procedure table.
- Default clist update hooks: `gx_default_composite_clist_write_update`, `gx_default_composite_clist_read_update`.
- `gs_composite_s`: reference-counted abstract compositor object with type, id, and rc header.
- `gs_composite_id(pcte)`: id accessor macro.

## Semantics
- Command lists cannot serialize raw type-table addresses, so each compositor type needs a stable one-byte id.
- `write` and `read` procedures are responsible for compact command-list representation of compositor instances.
- Clist update hooks allow compositors to adjust writer/reader devices when a compositor is pushed through banded rendering.

## Dependencies
Uses public compositor definitions from `gscompt.h`, Ghostscript reference counting, bit-format definitions, imager state, devices, and memory APIs.

## Risks and Notes
- The one-byte id space allows 255 compositor types, which the comment treats as sufficient.
- Compositor serialization correctness is critical for async/banded rendering because writer and reader may live in separate address spaces.

Filesystem relevance: none. It is compositing/rendering infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcomp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcoord.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcoord.h

## Purpose
Declares internal graphics-state coordinate transformation helpers.

## Public Surface
- `gx_translate_to_fixed(gs_state *, fixed, fixed)`: sets translation to a fixed-point value and translates any current path.
- `gx_scale_char_matrix(gs_state *, int, int)`: scales CTM and character matrix for oversampling.
- `gx_matrix_to_fixed_coeff(const gs_matrix *, fixed_coeff *, int)`: computes fixed-point distance transformation coefficients from a matrix.

## Dependencies
Requires public coordinate APIs plus internal matrix/state definitions supplied by including context.

## Risks and Notes
- This is declaration-only; behavior is implemented elsewhere.
- Callers use these helpers where fixed-point precision and character oversampling matter.

Filesystem relevance: none. It is graphics coordinate infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcoord.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.c

## Purpose
Implements clipping path storage, sharing, assignment, rectangle-list representation, path synthesis, clipping intersection, scaling, enumeration, and debug printing. It deliberately excludes the lower-level actual clipping algorithms implemented in adjacent files.

## Public Surface
- Allocation/init/free: `gx_cpath_init_contained_shared`, `gx_cpath_alloc_shared`, `gx_cpath_init_local_shared`, `gx_cpath_free`.
- Sharing/assignment: `gx_cpath_unshare`, `gx_cpath_assign_preserve`, `gx_cpath_assign_free`.
- Accessors: `gx_cpath_to_path`, `gx_cpath_inner_box`, `gx_cpath_outer_box`, `gx_cpath_includes_rectangle`, `gx_cpath_set_outer_box`, `gx_cpath_list`.
- Setting/intersection/scaling: `gx_cpath_from_rectangle`, `gx_cpath_reset`, `cpath_is_rectangle`, `gx_cpath_clip`, `gx_cpath_intersect`, `gx_cpath_scale_exp2_shared`.
- Clip-list operations: `gx_clip_list_init`, `gx_clip_list_free`.
- Enumeration: `gx_cpath_enum_init`, `gx_cpath_enum_next`, `gx_cpath_enum_notes`.

## Implementation
- Represents clips either as a valid path or as a rectangle list with correct bounding boxes; paths are synthesized lazily from rectangle lists for `clippath`-style consumers.
- Uses reference-counted rectangle lists, path segment storage, and path-list nodes to share clip state across graphics states without unnecessary copying.
- Fast-paths rectangle clipping by intersecting boxes and preserving a valid path when the new clip is a rectangle and unchanged or simply represented.
- For nontrivial path intersections, flattens curves if needed, calls `gx_cpath_intersect_path_slow`, and stores original path history in a path-list when the rectangle list alone cannot preserve source path identity.
- Enumerates rectangle-list clipping paths by tracing rectangle edges and emitting path operations.
- Maintains `inner_box` for quick containment tests and `outer_box` expanded to pixel boundaries.

## Dependencies
Uses Ghostscript path, fixed-point, graphics state, imager state, clipping accumulator/list types, memory descriptors, and reference-count helpers.

## Risks and Notes
- `gx_cpath_unshare` has an explicit `NYI` comment where copying a shared rectangle list should occur.
- Several error returns in assignment helpers convert negative codes to `0`, matching old code style but obscuring failure propagation.
- Sharing local path segments is treated as fatal because stack-local segment storage cannot safely be reference-counted across clip paths.
- Rectangle-list enumeration can produce many small line segments for complex clips.

Filesystem relevance: none. This is graphics clipping-path infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.h

## Purpose
Exposes clipping list and clipping device implementation details needed by stack-allocated clipping clients and lower-level clipping code.

## Public Surface
- `gx_clip_rect`: linked rectangle with integer bounds and `to_visit` enumeration bookkeeping.
- `gx_clip_list`: either a single rectangle or a linked list with dummy head/tail entries, aggregate x bounds, and rectangle count.
- `gx_device_clip`: forwarding clipping device containing a clip list, current rectangle cursor, translation, cached clipping box, and target forwarding state.
- Device constructors: `gx_make_clip_translate_device`, `gx_make_clip_device`, `gx_make_clip_path_device`.
- Clip-list helpers exported from `gxcpath.c`: `gx_clip_list_init`, `gx_clip_list_free`, `gx_cpath_set_outer_box`, `gx_cpath_list`.

## Semantics
- Clip lists are ordered by Y ranges; consecutive rectangles either share Y bounds or start at/after the previous rectangle's bottom.
- A list with `count <= 1` is considered rectangular.
- Clipping devices cache their clipping box, so their target clipping box and clip list must remain unchanged after open.

## Dependencies
Requires Ghostscript device forwarding structures and clipping path declarations from included context.

## Risks and Notes
- The header intentionally exposes implementation structures, so external users must honor invariants usually hidden behind higher-level APIs.
- Translation-aware clipping devices are documented as late additions used mainly for split transfers.

Filesystem relevance: none. This is clipping device metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcspace.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcspace.h

## Purpose
Defines the internal color-space type/class interface for Ghostscript color-space implementations.

## Public Surface
- `gs_color_space_type_s`: color-space vtable with index, base/alternate eligibility flags, structure type, component count, base-space lookup, color initialization/restriction, concrete-space lookup, concretization, concrete remap, direct remap, install, overprint setup, reference-count adjustment, serialization, and linearity checking.
- Macros for invoking color-space procedures, including `cs_num_components`, `cs_base_space`, `cs_init_color`, `cs_restrict_color`, `cs_concrete_space`, `cs_concretize_color`, `cs_adjust_counts`, and `cs_serialize`.
- Standard procedure declarations for 1/3/4-component spaces, no-base/no-concrete/default-remap helpers, reference-count no-ops, serialization, linearity checks, and overprint.
- Device color-space remap/concretize declarations implemented in `gxcmap.c`.
- Allocation/init API: `gs_cspace_init` and `gs_cspace_alloc`.

## Semantics
- Concrete colors are values the device can handle directly, possibly after halftoning.
- Pattern spaces have component counts encoded specially: `-1` for colored patterns and `-N-1` for uncolored patterns.
- Reference counting is split between indirect color-space components and indirect color values.
- Serialization excludes the type pointer because it is assumed to be handled separately as a static constant.

## Dependencies
Uses public color-space/client-color definitions, concrete fraction types, color selection, streams, devices, imager state, and Ghostscript memory descriptors.

## Risks and Notes
- Many procedures are not defined for Pattern spaces or non-concrete spaces; callers must dispatch through the correct color-space type.
- The `adjust_color_count` procedure explicitly accepts a NULL color-space argument for a documented application hack around Pattern color release.

Filesystem relevance: none. This is color-space implementation infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcspace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.c

## Purpose
Implements lookup and interpolation for 3-D and 4-D color lookup tables.

## Public Surface
- `gx_color_interpolate_nearest(...)`: returns nearest table entries without interpolation.
- `gx_color_interpolate_linear(...)`: returns linearly interpolated output values.

## Implementation
- Nearest lookup rounds fixed-point input indices and copies `m` byte table values as `frac` outputs.
- Linear interpolation delegates to `interpolate_accum`.
- For 4-D tables, interpolation performs two 3-D interpolations and interpolates between them on the first coordinate.
- For 3-D tables, it gathers the eight neighboring samples, interpolates along c, then b, then a, using fixed-point fractional parts.
- Boundary coordinates use zero deltas at the high edge to avoid reading past the last table entry.

## Dependencies
Uses fixed-point helpers, fraction conversion macros, and the `gx_color_lookup_table` structure from `gxctable.h`.

## Risks and Notes
- The code assumes caller-supplied indices are already in table range as promised by the header.
- Table layout must match the header's 3-D/4-D string-array convention exactly.

Filesystem relevance: none. This is color interpolation math.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.h

## Purpose
Declares the color lookup table data model and interpolation APIs.

## Public Surface
- `gx_color_lookup_table`: describes a 3-D or 4-D table with dimension count, dimensions, output component count, and array of constant strings.
- `gx_color_interpolate_nearest(...)`: nearest-sample lookup.
- `gx_color_interpolate_linear(...)`: trilinear/4-D interpolated lookup.

## Semantics
- For 3-D tables, `table[i]` points to data of length `dims[1] * dims[2] * m`.
- For 4-D tables, `table[i]` spans the first two dimensions as `dims[0] * dims[1]` strings of length `dims[2] * dims[3] * m`.
- Input fixed-point indices are guaranteed by callers to be within `[0, dims[n]-1]`.

## Dependencies
Includes fixed-point and fraction types.

## Risks and Notes
- String sizes are retained mostly to simplify garbage collection even though table slices are uniform.

Filesystem relevance: none. This is a rendering math interface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxctable.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcvalue.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcvalue.h

## Purpose
Defines the driver-interface type and conversion macros for device gray/RGB/colorant component values.

## Public Surface
- `gx_color_value`: unsigned short component value type.
- `gx_color_value_bits`, `gx_max_color_value`: component precision and maximum.
- Byte conversion macros: `gx_color_value_to_byte`, `gx_color_value_from_byte`.
- Fraction conversion macros: `frac2cv`, `cv2frac`.

## Semantics
- Component precision is tied to `sizeof(unsigned short)`, typically 16 bits.
- Byte expansion repeats high bits into low bits so 8-bit values scale across the full component range.

## Dependencies
Requires architecture size macros and fraction conversion macros from included Ghostscript base headers.

## Risks and Notes
- The comment says supported component precision must be between 8 and 16 bits; code assumes that range.

Filesystem relevance: none. This is a color component type definition.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcvalue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.c

## Purpose
Implements color conversion between Ghostscript device color spaces, specifically RGB-to-gray, RGB-to-CMYK, CMYK-to-gray, and CMYK-to-RGB.

## Public Surface
- `color_rgb_to_gray(frac r, frac g, frac b, const gs_imager_state *pis)`.
- `color_rgb_to_cmyk(frac r, frac g, frac b, const gs_imager_state *pis, frac cmyk[4])`.
- `color_cmyk_to_gray(frac c, frac m, frac y, frac k, const gs_imager_state *pis)`.
- `color_cmyk_to_rgb(frac c, frac m, frac y, frac k, const gs_imager_state *pis, frac rgb[3])`.

## Implementation
- RGB to gray uses luminance weights.
- RGB to CMYK computes subtractive complements, derives black from the minimum of C/M/Y, applies black-generation and undercolor-removal transfer maps from the imager state when available, and otherwise uses fallback defaults.
- CMYK to gray maps CMY to weighted non-gray plus black, clamping to black when the sum exceeds full scale.
- CMYK to RGB uses Adobe-compatible formulas controlled by `USE_ADOBE_CMYK_RGB`, with fast cases for no black and full black.

## Dependencies
Uses fractional arithmetic, luminance constants, imager transfer maps, and debug tracing.

## Risks and Notes
- The source explicitly notes alternate non-Adobe formulas that produced better display results, but this build selects Adobe-compatible behavior.
- RGB to CMYK depends on black-generation and undercolor-removal maps matching PostScript initialization behavior when an imager state is present.

Filesystem relevance: none. This is color conversion math.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcconv.c -->