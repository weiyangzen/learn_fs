# Group Research: group_1570_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxhintn_c_sources_o_3b2ed5d815f8

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.c

Purpose: implements Ghostscript's newer Type 1/Type 2 font hinter. It imports charstring outline operations into internal pole/hint arrays, aligns stems and blue-zone features to device/subpixel grids, interpolates unaligned points, and exports the adjusted outline into a `gx_path`.

Key responsibilities:
- Fixed-point transform support: `double_matrix`/`fraction_matrix` setup, inversion, precision reduction, glyph-to-outliner/device conversions.
- Font setup: `t1_hinter__set_mapping`, `t1_hinter__set_font_data`, and `t1_hinter__set_font42_data` configure CTM, pixel/subpixel scale, blue zones, stem snaps, ForceBold, autohint defaults, and disabled-hinting behavior.
- Outline capture: `sbw`, `rmoveto`, `rlineto`, `rcurveto`, `closepath`, flex handlers, and `setcurrentpoint` accumulate poles and contours unless hinting is disabled, in which case they directly emit transformed path segments.
- Hint capture: `hstem`, `vstem`, `hstem3`, `vstem3`, `hint_mask`, `drop_hints`, `dotsection`, and range bookkeeping store stem commands and activation ranges.
- End-of-glyph processing: `t1_hinter__endglyph` adds trailing moveto, computes spans, simplifies representation, computes hint ranges, aligns stems, adjusts opposite boundaries, processes dotsections, interpolates remaining poles, exports the path, and frees dynamic arrays.

Important data flow:
- Glyph-space coordinates are stored in `t1_pole.gx/gy`; aligned glyph-space coordinates are stored in `ax/ay`.
- Hints store original stem boundaries `g0/g1`, aligned boundaries `ag0/ag1`, range lists, side masks, and alignment strength.
- Dynamic arrays start with embedded fixed-size buffers from `gxhintn.h` and grow via `gs_alloc_bytes` when limits are exceeded.

Alignment behavior:
- Horizontal stems use Y coordinates; vertical stems use X coordinates.
- Blue zones can force top/bottom alignment and overshoot suppression.
- Standard stem widths are consulted when preserving stem width.
- Dotsections are shifted toward nearby vertical stem centers or half-pixel alignment when not already aligned by stem hints.
- Remaining points are interpolated between aligned poles, with extra handling around extrema.

Dependencies:
- Uses Ghostscript path, font, matrix, fixed-point, memory, error, and optional `vdtrace` debugging APIs.
- Public entry points are declared in `gxhintn.h`.

Research notes:
- This is graphics/font rendering code, not filesystem code, but it is part of the Plan 9 Ghostscript source tree included in subset A.
- Several comments identify compatibility workarounds and known limitations: diagonal stems are not hinted, some font-size/resolution calculations are known imperfect, and some glyph-validity assumptions are heuristic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.h

Purpose: public/internal header for the Type 1 hinter implemented in `gxhintn.c`.

Key definitions:
- Compile-time feature flags for fine stem complexes, stem-middle alignment, opposite-coordinate bug fix, and TrueType autohint top-zone fix.
- Capacity constants: stem snaps, alignment zones, contours, poles, and hints.
- Coordinate types: `t1_glyph_space_coord`, `t1_hinter_space_coord`, and `int19`.
- Enums for hint type (`hstem`, `vstem`, `dot`), pole type, zone type, and alignment strength.
- Matrix structs: `double_matrix` and `fraction_matrix`.
- Core records: `t1_pole`, `t1_hint`, `t1_hint_range`, `t1_zone`, and `t1_hinter`.

`t1_hinter` contents:
- Transform state, glyph origin/width/current-point state, grid-fit flags, blue-zone/stem data, pole/hint/contour arrays, font metrics, ForceBold/seac flags, and output path/memory pointers.
- Embedded arrays provide common-case storage, with pointers allowing growth.

Public API:
- Initialization and configuration: `t1_hinter__init`, `t1_hinter__set_mapping`, `t1_hinter__set_font_data`, `t1_hinter__set_font42_data`.
- Charstring drawing commands: `sbw`, `rmoveto`, `rlineto`, `rcurveto`, `setcurrentpoint`, `closepath`.
- Flex, hint, and stem commands.
- Completion/accessors: `endchar`, `endglyph`, `is_x_fitting`.

Dependencies:
- Requires Ghostscript fixed/matrix/memory types from included surrounding headers; directly includes `stdint_.h`.

Research notes:
- This header exposes a stateful, procedural interface intended to be called by Type 1/Type 2 charstring interpreters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.c

Purpose: implements helper routines for high-level devices to save, compare, and query color-space-aware device colors without storing unsafe pointers into transient graphics-state objects.

Main functions:
- `gx_hld_saved_color_init`: clears a saved-color record, marks ids as `gs_no_id`, and saves a null device color.
- `gx_hld_get_gstate_ptr`: verifies an imager state is actually a `gs_state` via Ghostscript object type metadata.
- `gx_hld_save_color`: saves color space id, pattern id when applicable, client color component values, and device-color-specific saved data.
- `gx_hld_saved_color_equal`: compares two full saved-color structs with `memcmp`.
- `gx_hld_saved_color_same_cspace`: compares ids and validity metadata for color-space sameness.
- `gx_hld_is_hl_color_available`: checks for graphics state, device color, and valid client color.
- `gx_hld_get_color_space_and_ccolor`: returns current color space and client color pointers when valid, distinguishing pattern and non-pattern color-space cases.
- `gx_hld_get_number_color_components`: returns component count from the current graphics-state color space.
- `gx_hld_get_color_component`: returns a requested high-level color component.

Dependencies:
- Uses graphics state, color space, device color, pattern color, and Type 2 pattern headers.
- Relies on `gx_device_color.type->save_dc` for polymorphic device color saving.

Research notes:
- `pattern_color_sapce` is misspelled in the enum and implementation, so callers must use the existing spelling.
- `gx_hld_saved_color_same_cspace` repeats a color_space_id check; harmless but redundant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.h

Purpose: declares helper structures and APIs for high-level device color preservation and comparison.

Key design constraints documented:
- Avoid changing the broad Ghostscript device interface.
- Avoid storing pointers to temporary or externally owned color-space/client-color objects.
- Preserve enough information to detect color-space and color changes in high-level devices.

Key type:
- `gx_hl_saved_color` stores `color_space_id`, `pattern_id`, `ccolor_valid`, a copied `gs_client_color`, and `gx_device_color_saved`.

APIs:
- Save/init/compare saved color records.
- Retrieve graphics-state pointer from imager state when possible.
- Query high-level color availability.
- Retrieve current color space and client color status.
- Query component counts and individual high-level component values.

Enums:
- `gx_hld_get_color_space_and_ccolor_status`: `non_pattern_color_space`, `pattern_color_sapce`, `use_process_color`.
- `gx_hld_get_color_component_status`: valid result or invalid color/component status.

Research notes:
- Header comments are important: they define the lifetime and pointer-safety model expected by high-level devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.c

Purpose: implements binary halftone device color behavior and halftone tile-cache management for Ghostscript's imaging library.

Main components:
- Defines public device color type `gx_dc_type_ht_binary`.
- Provides GC pointer enumeration/relocation for binary halftone colors, tile arrays, and caches.
- Defines default cache sizing for small and large-memory builds.
- Allocates/frees `gx_ht_cache` with tile storage and bit buffers.
- Initializes tile cache layouts in `gx_ht_init_cache`.
- Renders halftone levels into cache tiles incrementally via `render_ht`.

Binary halftone color operations:
- `save_dc`: stores colors, level, component index, and phase.
- `get_dev_halftone`: returns the associated `gx_device_halftone`.
- `load`: switches cache order when needed, but defers tile rendering.
- `load_cache`: renders the needed level into the appropriate tile lazily.
- `fill_rectangle`: uses strip tiling or RasterOp copying depending on colors/source/lop.
- `fill_masked`: ensures cache loading, then delegates to default masked fill.
- `equal`: compares type, phase, colors, and halftone level.
- `write`/`read`: serializes/deserializes changed fields using flag bits and process color encoding.
- `get_nonzero_comps`: decodes both binary colors to identify components that can be nonzero.

Cache behavior:
- Cache levels are grouped into available tile slots.
- If all levels fit cheaply, tiles may be replicated horizontally and vertically to reduce repeated tiling overhead.
- Tile ids are generated from `gs_next_ids`.

Research notes:
- Several old tile-cache query functions are retained but return false/-1 with comments saying they are no longer used in DeviceN code.
- Read reconstruction always takes the halftone from `pis->dev_ht`; serialized data does not contain the tile or halftone object.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.h

Purpose: declares client-side halftone structures and public halftone control APIs.

Halftone types modeled:
- Type 1 spot halftones: `gs_spot_halftone`.
- Type 3 threshold halftones: `gs_threshold_halftone`.
- Extended Type 3 threshold halftones: `gs_threshold2_halftone`.
- Client-defined order halftones: `gs_client_order_halftone`.
- Type 5 multi-component halftones: `gs_multiple_halftone`.
- Unified graphics-state halftone union: `gs_halftone`.

Important design comments:
- Halftones are not globally identified/cache-keyed objects in this library design.
- Client-provided data can be relocated by GC, but clients remain responsible for freeing it.
- General halftone caching is device-dependent because spot halftone representation depends on device transformation and additive/subtractive sense.

Memory/GC support:
- Declares structure descriptors and max pointer counts for halftone components and whole halftones.

Procedural APIs:
- `gs_setaccuratescreens` / `gs_currentaccuratescreens`.
- `gs_setusewts` / `gs_currentusewts`.
- `gs_screen_init_memory` and `gs_screen_init_accurate`.
- `gs_setminscreenlevels` / `gs_currentminscreenlevels`.

Research notes:
- This header is the main structural contract for halftone objects used by PostScript graphics state and device setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhtbit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhtbit.c

Purpose: builds and updates halftone order bit representations from threshold arrays.

Order construction:
- `construct_ht_order_default`: fills `gx_ht_bit.mask` values from thresholds and calls `gx_ht_complete_threshold_order`.
- `construct_ht_order_short`: builds compact ushort bit-index arrays and level offsets from threshold values.
- Short construction also checks registered predefined halftone resources; if a match is found, it frees allocated arrays and points the order at built-in constant data.

Coordinate lookup:
- `ht_bit_index_default`: converts a default `gx_ht_bit` entry to x/y bit coordinates by locating the mask bit.
- `ht_bit_index_short`: converts compact ushort bit index to x/y coordinates using raster width.

Rendering:
- `render_ht_default`: toggles bits between old and new levels using `gx_ht_bit.offset/mask`.
- `render_ht_short`: toggles bits between old and new levels using compact bit indexes.
- Both renderers handle level movement up or down with unrolled switch logic and XOR bit inversion.

Exported table:
- `ht_order_procs_table[2]` maps order representation to element size, construction, index lookup, and render functions.

Dependencies:
- Uses bitmap raster math, halftone tile definitions, transfer maps, and device halftone resource lists.

Research notes:
- Threshold values are clamped to at least 1 before use.
- Compact representation accounts for bitmap row padding when computing stored bit indexes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhtbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttile.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttile.h

Purpose: defines the cacheable halftone tile record used by device colors and halftone caches.

Main type:
- `gx_ht_tile` wraps a `gx_strip_bitmap` plus cache metadata.

Fields:
- `tiles`: rendered strip bitmap for the current halftone tile.
- `level`: cached gray/halftone level, or `-1` when cache is empty by convention.
- `index`: tile index inside the cache, used for relocation/GC logic.

Dependencies:
- Requires `gxbitmap.h` definitions before inclusion.

Research notes:
- This header is deliberately small so clients of `gx_device_color` can see halftone tile layout without pulling in the full halftone cache internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttype.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttype.h

Purpose: defines the client-visible halftone type enumeration.

Enum values:
- `ht_type_none`.
- `ht_type_screen` for `setscreen`.
- `ht_type_colorscreen` for `setcolorscreen`.
- `ht_type_spot` for Type 1 halftone dictionaries.
- `ht_type_threshold` for Type 3 threshold dictionaries.
- `ht_type_threshold2` for extended threshold dictionaries with byte strings and 8/16-bit samples.
- `ht_type_multiple` for Type 5 halftone dictionaries.
- `ht_type_multiple_colorscreen` for Type 5 objects derived from Type 2/4 dictionaries.
- `ht_type_client_order` for client-defined `gx_ht_order` creation.

Research notes:
- Used by `gxht.h` and other halftone setup code as the discriminator for halftone parameter unions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi12bit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi12bit.c

Purpose: provides unpacking and rendering support for image data with 12-bit samples, expanded into Ghostscript `frac` values.

Unpacking:
- `sample_unpack_12` reads packed 12-bit samples from 3-byte pairs.
- Handles odd `data_x`, full 3-byte groups, and trailing 1- or 2-byte partial data.
- Writes expanded `frac` samples into the destination buffer using `spread`.
- Exposes `sample_unpack_12_proc`.

Strategy:
- `gs_image_class_2_fracs` selects the frac renderer for `bps > 8`.
- Converts mask color ranges from sample values into `frac` values when image masking is active.

Rendering:
- `image_render_frac` handles 1-, 3-, 4-, and arbitrary-component images.
- Reuses runs of identical samples to reduce color remapping and fill calls.
- Checks mask-color transparency.
- Uses fast device color mapping for gray/RGB/CMYK device-color cases, otherwise decodes into `gs_client_color` and calls color-space remap.
- Emits rectangles for portrait images and parallelograms for transformed images.
- Saves `penum->used.x/y` on errors so rendering can resume.

Dependencies:
- Uses image enumerator state, color space remapping, device color mapping, DDA geometry, and fill APIs.

Research notes:
- The file is closely parallel to `gxi16bit.c`, differing mainly in packed 12-bit unpacking and mask conversion assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi12bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi16bit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi16bit.c

Purpose: provides unpacking and rendering support for image data with 16-bit samples expanded into `frac` values.

Unpacking:
- `sample_unpack_16` reads big-endian 16-bit samples, converts them to `frac`, and stores them with configured `spread`.
- Exposes `sample_unpack_16_proc`.

Rendering:
- `image_render_frac` is structurally the same high-bit-depth renderer used for 12-bit images.
- Handles gray, RGB, CMYK, and DeviceN-like arbitrary sample counts.
- Performs run detection on expanded sample values.
- Supports mask-color transparency.
- Uses direct device color mapping when available, or color-space decode/remap otherwise.
- Fills portrait rectangles or transformed parallelograms.
- Records partial progress in `penum->used` on errors.

Dependencies:
- Uses Ghostscript image, color, device, DDA, and path/clipping infrastructure.

Research notes:
- Unlike `gxi12bit.c`, this file does not define a separate strategy procedure; it supplies the 16-bit unpacker and renderer implementation in the same style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi16bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiclass.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiclass.h

Purpose: defines the abstract image rendering class callback interface.

Key declarations:
- Forward declares `gx_image_enum` and `gx_device`.
- Defines `irender_proc_t`: renders expanded complete source rows for an image enumerator.
- Defines `gx_image_class_t`: selects a renderer for an image class and may update the enumerator.

Contract details:
- Render procedures receive a buffer, data x offset, sample count width, height, and target device.
- `w` is sample count, not pixel count or byte count.
- `h == 0` signals end-of-input flushing.
- Render procedures return a negative error code or the number of rows processed.

Research notes:
- This header underpins files such as `gxifast.c`, `gxicolor.c`, and `gxi12bit.c`, whose strategy functions compete in priority order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxiclass.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxicolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxicolor.c

Purpose: renders color images with 8 or fewer bits per sample after samples have been expanded to byte-wide values.

Strategy:
- `gs_image_class_4_color` always returns `image_render_color`.
- When mask color is active, it scales mask ranges to byte values and precomputes fast mask/test bits for quick rejection.

Rendering:
- `image_render_color` handles RGB, CMYK/RGBA, gray+alpha, CMYK+alpha conversion, and arbitrary DeviceN-like sample counts.
- Uses a small 256-entry clue/cache table for low-bit sample combinations (`spp * bps <= 12`) to avoid repeated color remapping.
- Checks transparency via precomputed mask/test and full range matching when necessary.
- Maps concrete device colors directly when possible; otherwise decodes samples into `gs_client_color` and remaps through the color space.
- Coalesces adjacent identical/equivalent device colors into runs.
- Emits portrait rectangles, landscape rotated rectangles, or parallelograms depending on image posture.
- Updates `penum_orig->used` on errors for resumable rendering.

Dependencies:
- Uses color-space remap APIs, concrete color remap, color map procs, image DDA state, device fill operations, and ROP-aware rectangle fills.

Research notes:
- Alpha handling is limited to specific cases; comments state DeviceN color plus alpha is unsupported.
- Duplicated fill logic appears for normal and final run paths to avoid passing many locals to a helper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxicolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxidata.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxidata.c

Purpose: implements generic ImageType 1 image enumeration, row unpacking/repacking, rendering dispatch, flushing, and cleanup.

Main flow:
- `gx_image1_plane_data` processes incoming image planes row by row.
- Computes row byte counts, handles resumed partial progress, sets up clipping/ROP forwarding devices, unpacks or repacks source data, updates DDA row/pixel state, applies clipping checks, and invokes the selected render procedure.
- `gx_image1_flush` invokes the renderer with `h == 0` to flush buffered image data at end-of-input.
- `gx_image1_end_image` optionally flushes, releases scaler state, and frees image buffers/devices/enumerator.

Bit-planar support:
- `repack_bit_planes` combines 1 to 8 individual bit planes into byte-wide samples.
- Handles null planes by substituting zero buffers.
- Supports nonzero `data_x`, direct identity output, and lookup-table mapped output.

Device setup:
- `setup_image_device` wraps the target with clip and ROP forwarding devices when present.

State/error behavior:
- `penum->used.x/y` track partially consumed pixels/rows after render errors.
- DDA row/strip state is restored on interrupted rendering so callers can resume.
- Caller remains responsible for ending the image after normal or error returns.

Research notes:
- This is the central glue between image decoders/unpackers and specialized renderers in the other `gxi*` files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxidata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxifast.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxifast.c

Purpose: provides fast rendering paths for simple 1-bit monochrome images.

Strategy:
- `gs_image_class_1_simple` selects this path only for non-ROP, single-component, 1-bit images.
- Supports portrait and 90-degree landscape postures.
- Allocates line buffers when scaling or landscape rotation requires intermediate storage.
- Sets `sample_unpack_copy` and adjusts unpack state so raw bits can be consumed directly.
- Converts mask-color ranges into transparent `gx_no_color_index` device colors, or skips completely transparent images.

Core rendering:
- `image_render_skip`: consumes transparent image data without drawing.
- `image_simple_expand`: scales and optionally reverses one monobit scan line using fixed-point DDA state and run scanning.
- `copy_portrait`: copies expanded bits to the target, using `copy_mono` for pure colors or masked fills when one color is non-pure/transparent.
- `image_render_simple`: optimized portrait renderer, including direct memory-device bitmap expansion when conditions are safe.
- `image_render_landscape`: buffers groups of 8 scan lines for 90-degree rotated images.
- `copy_landscape`: flips 8x8 blocks with `memflip8x8` and copies them through the portrait path.

Dependencies:
- Uses bit tables, fixed-point DDA math, device color loading, memory-device internals, clipping constraints, and halftone/device color fill hooks.

Research notes:
- The direct memory-device fast path carefully saves/restores edge bytes outside the image bounds.
- Landscape rendering flushes buffered data on discontinuities, end-of-input, or explicit flush calls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxifast.c -->