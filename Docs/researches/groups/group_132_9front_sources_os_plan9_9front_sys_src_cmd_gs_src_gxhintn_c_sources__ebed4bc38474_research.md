# Group Research: group_132_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxhintn_c_sources__ebed4bc38474

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.c

## Role

`gxhintn.c` implements Ghostscript's "new algorithm" Type 1 hinter. It collects Type 1/Type 2 glyph outlines, stem hints, hint masks, flex points, alignment zones, and stem snap data in an internal `t1_hinter` object, grid-fits the outline in device-oriented space, then exports the adjusted outline to a `gx_path`.

This is font rasterization and outline processing infrastructure, not filesystem code.

## Main Responsibilities

- Sets up fixed/fraction matrix transforms between glyph space, internal outliner space, and device space.
- Initializes and tears down dynamic arrays for poles, hints, zones, contours, hint ranges, and stem snap widths.
- Imports charstring operations through `t1_hinter__sbw`, `rmoveto`, `rlineto`, `rcurveto`, `closepath`, `setcurrentpoint`, and flex handlers.
- Records Type 1/Type 2 hint operations through hstem/vstem/hstem3/vstem3, dotsection, hint masks, and hint dropping.
- Converts BlueValues/OtherBlues/FamilyBlues and stem snap data from font dictionaries into internal zones and standard widths.
- Computes hint ranges, detects stem-applicable outline poles, aligns stem boundaries and alignment zones, adjusts opposite stem coordinates, processes dotsections, interpolates unaligned points, and exports a final path.

## Important Algorithms

- `mul_shift`, `mul_shift_round`, `fraction_matrix__set`, and `fraction_matrix__invert_to` keep transformation arithmetic in bounded integer/fixed precision, with 64-bit multiply when available and a 32-bit fallback.
- `t1_hinter__adjust_matrix_precision` drops matrix precision dynamically when imported coordinates would exceed the 24-bit internal coordinate budget.
- `t1_hinter__compute_aligned_coord` combines stem alignment with BlueScale/BlueShift/BlueFuzz overshoot logic and optional stem-middle alignment.
- `t1_hinter__align_stem_width` and `t1_hinter__align_stem_to_grid` try to preserve stem width while snapping boundaries to pixels/subpixels and optionally using standard stem widths.
- `t1_hinter__interpolate_other_poles` propagates fitted coordinates around contours, splitting interpolation ranges at extrema and using fixed-point ratio approximation to avoid broad integer division/multiply overflow.
- `t1_hinter__endglyph` is the orchestration point: add trailing moveto, simplify representation, compute ranges, align stem commands, align poles, dotsection process, interpolate, paint debug traces, export, and free arrays.

## Dependencies And Integration

- Uses Ghostscript path, font, matrix, fixed-point, Type 1 data, and memory APIs from headers such as `gxpath.h`, `gxfont1.h`, `gxtype1.h`, `gxhintn.h`, `gzpath.h`, and `gserrors.h`.
- Emits device-space geometry through `gx_path_add_point`, `gx_path_add_line`, `gx_path_add_curve`, and `gx_path_close_subpath`.
- Uses `vdtrace` hooks for optional debug visualization.
- Depends on compile-time switches declared in `gxhintn.h`, including `FINE_STEM_COMPLEXES`, `ALIGN_BY_STEM_MIDDLE`, and compatibility/bug-fix switches.

## Notable Edge Cases

- If hinting is disabled or there is no output memory, path operations are emitted directly without delayed grid fitting.
- Degenerate transforms, very small/large CTMs, and import coordinates beyond the precision budget disable or reduce hinting precision.
- Type 1 primary hints are expanded to whole-glyph ranges; secondary hints cover replacement ranges; Type 2 hint masks keep explicit active ranges.
- Flex rendering may become either two curves or one line depending on flex height in device-oriented space.
- Dotsection adjustment is skipped if both X and Y extremes were already aligned by stems.

## Notable Risks

- The file is large, stateful, and macro/flag sensitive; correctness depends on many cross-field invariants in `t1_hinter`.
- Several comments mark unfinished areas: diagonal stems are not hinted, Adobe compatibility is not fully verified, anomalous negative contours are not repaired, and some font metrics for overshoot compatibility are known unreliable.
- There are suspicious implementation details worth auditing before modifying: `fraction_matrix__set` computes `ayx`/`ayy` from `pmat->xx`/`pmat->xy` rather than `pmat->yx`/`pmat->yy`; `t1_hinter__is_conjugated` computes `sp` with the same formula as `vp`; and `t1_hinter__process_dotsections` sets `end_pole` from `contour[contour_index] - 2`, which appears inconsistent with other contour-end calculations.
- `t1_hinter__endglyph` returns `0` after the cleanup label even if an earlier operation put a negative `code` in scope, so some errors before export cleanup may be masked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.h

## Role

`gxhintn.h` declares the Type 1 hinter data model and public entry points implemented by `gxhintn.c`.

This is font rendering infrastructure, not filesystem code.

## Main Definitions

- Feature switches: `FINE_STEM_COMPLEXES`, `ALIGN_BY_STEM_MIDDLE`, `OPPOSITE_STEM_COORD_BUG_FIX`, and `TT_AUTOHINT_TOPZONE_BUG_FIX`.
- Capacity constants: `T1_MAX_STEM_SNAPS`, `T1_MAX_ALIGNMENT_ZONES`, `T1_MAX_CONTOURS`, `T1_MAX_POLES`, and `T1_MAX_HINTS`.
- Coordinate types: `t1_glyph_space_coord`, `t1_hinter_space_coord`, and `int19`.
- Enums for hint type, pole type, zone type, and alignment status.

## Data Structures

- `double_matrix` and `fraction_matrix` hold floating and fixed/fraction transform forms.
- `t1_pole` represents an outline point/control point with source and aligned coordinates, type, contour index, and per-axis alignment status.
- `t1_hint` represents one stem/dot hint with source/aligned boundaries, quality, active range link, stem3 index, and side mask.
- `t1_hint_range` links active ranges of hints to pole intervals.
- `t1_zone` represents a BlueValues-style top or bottom alignment zone.
- `t1_hinter` owns all persistent state for one glyph import/hint/export cycle, including matrices, origin, widths, contour arrays, hints, zones, stem snap arrays, flex state, font metrics, grid fitting state, output path, and allocator.

## Public Interface

- Lifecycle and setup: `t1_hinter__init`, `t1_hinter__set_mapping`, `t1_hinter__set_font_data`, `t1_hinter__set_font42_data`.
- Path import: `t1_hinter__sbw`, `sbw_seac`, `rmoveto`, `rlineto`, `rcurveto`, `setcurrentpoint`, `closepath`.
- Flex import: `flex_beg`, `flex_point`, `flex_end`.
- Hint import: `hint_mask`, `drop_hints`, `dotsection`, `hstem`, `vstem`, `overall_hstem`, `hstem3`, `vstem3`.
- Finalization/query: `endchar`, `endglyph`, and `is_x_fitting`.

## Notable Risks

- The struct exposes many internal fields directly; callers must follow the intended interpreter call sequence.
- Comments contain minor inaccuracies/typos, including `align_to_pixels` described as false meaning align to integral pixels.
- The `hstem3` prototype parameter names mix `x` and `y` names, although the types are all `fixed`; this is harmless to C compilation but confusing to readers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.c

## Role

`gxhldevc.c` implements helper procedures for high-level devices that need to save, compare, and recover color-space/client-color information associated with a Ghostscript `gx_device_color`.

This is graphics device/color infrastructure, not filesystem code.

## Main Functions

- `gx_hld_saved_color_init`: clears a saved color, sets color-space and pattern ids to `gs_no_id`, and saves a null device color.
- `gx_hld_get_gstate_ptr`: verifies that an imager state pointer is actually a `gs_state` object using Ghostscript structure type metadata.
- `gx_hld_save_color`: saves color space id, device color-specific state, client color paint values, and pattern id when available.
- `gx_hld_saved_color_equal`: compares complete saved-color structures with `memcmp`.
- `gx_hld_saved_color_same_cspace`: compares color-space id, pattern id, and `ccolor_valid`.
- `gx_hld_is_hl_color_available`: checks whether a graphics state and valid client color are available.
- `gx_hld_get_color_space_and_ccolor`: returns current color space and client color pointers plus pattern/non-pattern/process-color status.
- `gx_hld_get_number_color_components`: returns the component count for the current graphics state's color space, normalizing negative values.
- `gx_hld_get_color_component`: returns an individual high-level color component when valid.

## Dependencies And Integration

- Uses `gzstate.h`, `gscspace.h`, `gxcspace.h`, `gxdcolor`-related types from `gxhldevc.h`, pattern device color types, and Ghostscript structure descriptors.
- Integrates with `gx_device_color` polymorphic methods through `pdevc->type->save_dc`.
- Uses color-space ids and pattern ids rather than saving pointers that could become dangling.

## Notable Risks

- `gx_hld_save_color` clears `psc` and copies `pdevc->ccolor.paint.values`, but does not visibly assign `psc->ccolor_valid`; this may be intentional reliance on zeroed state or a missing field copy, and it affects `gx_hld_saved_color_same_cspace`.
- `gx_hld_saved_color_same_cspace` checks `color_space_id` twice.
- The implementation of `gx_hld_get_color_space_and_ccolor` returns `ppcc = &pdevc->ccolor` for non-pattern colors, while the header comment says the client color pointer will be `NULL` for the non-pattern case.
- Several public enum/status names have typos (`pattern_color_sapce`, comments such as "availavble"), which can leak into API use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.h

## Role

`gxhldevc.h` declares the high-level device color save/compare helper API used by Ghostscript devices that need color-space-aware output without changing the wider device interface.

This is graphics device/color infrastructure, not filesystem code.

## Design Intent

- Avoid broad changes to Ghostscript's long-standing device interface.
- Avoid saving pointers to graphics-state color space structures that may be temporary, stack-based, or freed outside the device.
- Save enough stable identifiers and value data to detect high-level color/color-space changes across device operations.

## Main Types

- `gx_hl_saved_color` stores:
  - `color_space_id`
  - `pattern_id`
  - `ccolor_valid`
  - `gs_client_color ccolor`
  - `gx_device_color_saved saved_dev_color`
- `gx_hld_get_color_space_and_ccolor_status` has statuses for non-pattern color space, pattern color space, and process-color fallback.
- `gx_hld_get_color_component_status` reports valid component, invalid color info, or invalid component request.

## Public Interface

- Initialization/comparison: `gx_hld_saved_color_init`, `gx_hld_saved_color_equal`, `gx_hld_saved_color_same_cspace`.
- Context lookup: `gx_hld_get_gstate_ptr`.
- Save/query helpers: `gx_hld_save_color`, `gx_hld_is_hl_color_available`, `gx_hld_get_color_space_and_ccolor`, `gx_hld_get_number_color_components`, `gx_hld_get_color_component`.

## Notable Risks

- The header contract for `gx_hld_get_color_space_and_ccolor` should be checked against implementation behavior before relying on `ppcc == NULL` for non-pattern colors.
- The status name `pattern_color_sapce` is misspelled and therefore part of the compiled API.
- `gx_hl_saved_color` comparison depends on unused fields being zeroed before use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.c

## Role

`gxht.c` implements Ghostscript binary halftone device color behavior and halftone tile cache management.

This is imaging/halftone rendering infrastructure, not filesystem code.

## Main Responsibilities

- Defines the public `gx_dc_type_ht_binary` device color type descriptor.
- Provides GC enumeration/relocation procedures for binary halftone device colors, tile arrays, and halftone caches.
- Allocates, initializes, clears, and frees halftone caches.
- Lazily renders halftone levels into cache tiles.
- Fills rectangles and masks with binary halftone textures.
- Serializes/deserializes binary halftone device colors for banding/high-level device workflows.
- Computes nonzero process components for binary halftone colors.

## Important Functions

- `gx_ht_cache_default_tiles` and `gx_ht_cache_default_bits`: choose small or large cache sizes based on memory/debug mode.
- `gx_ht_alloc_cache` and `gx_ht_free_cache`: allocate/free cache structure, bit storage, and tile array.
- `gx_ht_init_cache`: sizes tile replication, assigns cache ids, initializes per-tile strip bitmap metadata, and chooses a render dispatch path.
- `render_ht`: asks the order's render procedure to update a tile to a desired level and optionally replicates it horizontally/vertically.
- `gx_dc_ht_binary_load` and `gx_dc_ht_binary_load_cache`: bind a device color to the current halftone order and load the actual tile only at render time.
- `gx_dc_ht_binary_fill_rectangle` and `gx_dc_ht_binary_fill_masked`: render halftone fills through `strip_tile_rectangle`, `strip_copy_rop`, or the default masked-fill path.
- `gx_dc_ht_binary_write` and `gx_dc_ht_binary_read`: delta-serialize color0, color1, level, and component index.

## Data And Cache Semantics

- Cache capacity is limited by both tile count and bit-storage bytes.
- `levels_per_tile` maps multiple halftone levels to one cache tile when the cache cannot hold every level.
- Lazy tile loading avoids conflicts when multiple device colors share a small cache whose tiles can represent different levels at different times.
- The tile bitmap may be replicated horizontally and vertically to reduce tiling overhead when all renderings fit in cache.

## Notable Risks

- Several legacy helper routines (`gx_check_tile_cache_current`, `gx_check_tile_cache`, `gx_check_tile_size`) are stubs returning false or -1 and marked unused/not supported for DeviceN.
- `gx_dc_ht_binary_fill_rectangle` calls `gx_dc_ht_binary_load_cache` but ignores its return code, whereas the masked path checks it.
- Serialization omits the rendered tile and relies on the imager state's current device halftone during readback.
- Comments note a known wrong test around replicated tile raster/width in `render_ht`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.h

## Role

`gxht.h` defines client-facing Ghostscript halftone structures, including spot, threshold, extended threshold, client-order, component, multiple, and union halftone objects.

This is imaging/halftone infrastructure, not filesystem code.

## Main Types

- `gs_spot_halftone`: Type 1 halftone with screen parameters, AccurateScreens flag, and transfer closure.
- `gs_threshold_halftone_common`: shared width/height/transfer closure fields for threshold halftones.
- `gs_threshold_halftone`: Type 3 threshold halftone with byte thresholds.
- `gs_threshold2_halftone`: extended Type 3 threshold halftone with one/two-byte samples and one/two rectangles.
- `gs_client_order_halftone`: client-defined halftone that creates a `gx_ht_order`.
- `gs_halftone_component`: Type 5 component with component number/name, type, and per-type params.
- `gs_multiple_halftone`: Type 5 halftone with component array and color-name callback.
- `gs_halftone`: ref-counted graphics-state halftone union covering setscreen, setcolorscreen, Type 1, Type 3, extended Type 3, client order, and Type 5.

## Public Interface

- AccurateScreens globals: `gs_setaccuratescreens`, `gs_currentaccuratescreens`.
- UseWTS globals: `gs_setusewts`, `gs_currentusewts`.
- Screen sampling: `gs_screen_init_memory` and `gs_screen_init_accurate`.
- MinScreenLevels globals: `gs_setminscreenlevels`, `gs_currentminscreenlevels`.

## Important Notes

- The header explicitly states client halftone data may be relocated by GC but will not be freed on halftone release; clients own that memory.
- User-provided data is expected to be heap-allocated so Ghostscript GC can treat it as a structure pointer.
- Generalized halftone cache keys are difficult because device-specific halftone representation can depend on device transform and device color sense.

## Notable Risks

- Some fields are marked obsolete (`transfer`) but still present for compatibility.
- Lifetime rules for client data are subtle and easy to violate.
- Halftone objects intentionally lack stable ids suitable for generalized cache keys.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhtbit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhtbit.c

## Role

`gxhtbit.c` implements halftone order construction and tile bit updating for Ghostscript's imaging library.

This is imaging/halftone infrastructure, not filesystem code.

## Main Responsibilities

- Builds standard or short halftone order representations from threshold arrays.
- Maps order indices back to bit coordinates.
- Incrementally renders halftone tiles by XOR-ing changed bits between old and new levels.
- Exports `ht_order_procs_table`, the procedure table for the supported order-data representations.

## Important Functions

- `construct_ht_order_default`: stores threshold masks in `gx_ht_bit` records and completes the threshold order.
- `construct_ht_order_short`: counts threshold values, builds compact `ushort` bit indices adjusted for bitmap row padding, and replaces dynamically allocated data with predefined built-in halftone resources when an exact match is found.
- `ht_bit_index_default` and `ht_bit_index_short`: return `(x,y)` coordinates for an order entry.
- `render_ht_default` and `render_ht_short`: update an existing tile from `old_level` to `level` by XOR-ing each bit crossed by the level delta.

## Data Representations

- Default representation uses `gx_ht_bit` with byte offset and mask.
- Short representation stores one padded bit index per threshold bit as `ushort`.
- `ht_order_procs_table[2]` binds element size, construct, index, and render procedures for both representations.

## Notable Risks

- Rendering depends on incremental XOR from the tile's current level; callers must keep `pbt->level` accurate.
- `construct_ht_order_short` mutates ownership: it may free dynamic arrays and point the order at const built-in resources while setting `data_memory = 0`.
- The switch-based render loops intentionally use fall-through for small deltas and `goto` for larger deltas; edits require care.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhtbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttile.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttile.h

## Role

`gxhttile.h` defines the `gx_ht_tile` structure used by halftone caches and device colors.

This is imaging/halftone infrastructure, not filesystem code.

## Main Definition

- `gx_ht_tile` contains:
  - `gx_strip_bitmap tiles`: the currently rendered/repeated bitmap tile.
  - `int level`: cached gray level, described as number of spots whitened, or `-1` for empty.
  - `uint index`: tile index within the cache, used by GC relocation.

## Dependencies

- Requires `gxbitmap.h` to define `gx_strip_bitmap`.
- Forward declares `gx_ht_tile` under `gx_ht_tile_DEFINED`.

## Notable Risks

- Cache correctness depends on `level` matching the actual contents of `tiles.data`.
- `index` is part of pointer relocation for cached tile arrays; changing layout affects GC support in `gxht.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttype.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttype.h

## Role

`gxhttype.h` defines the `gs_halftone_type` enumeration used by Ghostscript client and graphics-state halftone structures.

This is imaging/halftone infrastructure, not filesystem code.

## Enumerated Types

- `ht_type_none`
- `ht_type_screen`
- `ht_type_colorscreen`
- `ht_type_spot`
- `ht_type_threshold`
- `ht_type_threshold2`
- `ht_type_multiple`
- `ht_type_multiple_colorscreen`
- `ht_type_client_order`

## Notes

- `ht_type_threshold2` is documented as extended Type 3 with 8- or 16-bit samples, bytestring thresholds, and one or two rectangles.
- `ht_type_multiple_colorscreen` represents Type 5 halftone dictionaries created from Type 2 or Type 4 halftone dictionaries.

## Notable Risks

- The enum is shared across halftone unions; adding or reordering values would require auditing all switch and serialization users.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi12bit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi12bit.c

## Role

`gxi12bit.c` implements 12-bit image sample unpacking and a high-depth image renderer that works on expanded Ghostscript `frac` samples.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `sample_unpack_12_proc`: exported unpack procedure for packed 12-bit source samples.
- `gs_image_class_2_fracs`: image-class selector that chooses `image_render_frac` for images with `bps > 8`.
- `image_render_frac`: renderer for expanded high-depth samples.

## Important Behavior

- `sample_unpack_12` unpacks two 12-bit samples from each three input bytes, handles odd `data_x`, partial trailing bytes, and writes identity-mapped `frac` values with caller-provided `spread`.
- `gs_image_class_2_fracs` converts mask color values to `frac` range values when mask color is in use.
- `image_render_frac` coalesces consecutive samples that map to the same device color, then fills one rectangle or parallelogram per run.
- Supports 1-component gray, 3-component RGB, 4-component CMYK, and default DeviceN/multi-component paths.
- Supports source color masking by testing high-depth samples against `penum->mask_color`.

## Dependencies And Integration

- Uses image enumerator state from `gximage.h`, color-space remapping, device color mapping, DDA fixed-point stepping, and device fill procedures.
- Uses `bits2frac`, `decode_frac`, RGB/CMYK color map procs, and `gx_fill_rectangle_device_rop`.

## Notable Risks

- The renderer assumes the high-depth samples have already been expanded into `frac` units.
- `bufend` is computed as `psrc + w`, where `w` is documented elsewhere as samples rather than pixels; correctness depends on callers passing a sample count compatible with `spp` stepping.
- The final run is always filled with `fill_parallelogram`, even when earlier portrait runs use rectangle filling; this mirrors the 16-bit file and may be intentional but is worth checking for performance/consistency.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi12bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi16bit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi16bit.c

## Role

`gxi16bit.c` implements 16-bit image sample unpacking and a high-depth image renderer that works on expanded Ghostscript `frac` samples.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `sample_unpack_16_proc`: exported unpack procedure for 16-bit big-endian source samples.
- `image_render_frac`: local renderer for expanded high-depth samples.

## Important Behavior

- `sample_unpack_16` reads two bytes per sample, converts to a `frac` with `(frac_1 * (sample + 1)) >> 16`, writes with caller-provided `spread`, and resets `pdata_x`.
- Rendering logic parallels `gxi12bit.c`: detect runs of identical samples/device colors, process mask colors, use concrete RGB/CMYK mapping when possible, otherwise decode and remap through the color space.
- Supports gray, RGB, CMYK, and DeviceN/multi-component paths.
- Saves `penum->used.x` on render error so interrupted image rendering can resume.

## Dependencies And Integration

- Uses Ghostscript fixed-point DDA image state, color remapping, device color mapping, and device fill APIs.
- Includes the same broad image/color/device headers as `gxi12bit.c`.

## Notable Risks

- The unpack loop condition is `while (left > 2)`, which skips exactly two remaining bytes; given two bytes are one complete 16-bit sample, this deserves scrutiny if the caller can pass exact sample-sized buffers.
- The file does not declare an image-class selector like `gs_image_class_2_fracs`; it relies on another compilation unit or class table to route 16-bit expanded data to this renderer/unpacker.
- Like `gxi12bit.c`, the final run uses `fill_parallelogram` even when portrait runs used rectangle filling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi16bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiclass.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiclass.h

## Role

`gxiclass.h` defines the image rendering class interfaces used to choose and call Ghostscript image renderers.

This is image rendering infrastructure, not filesystem code.

## Main Definitions

- Forward declares `gx_image_enum` and `gx_device`.
- `irender_proc(proc)`: macro signature for scan-line render procedures.
- `irender_proc_t`: function pointer type for render procedures.
- `iclass_proc(proc)`: macro signature for image-class selector procedures.
- `gx_image_class_t`: function pointer type for class selectors.

## Interface Semantics

- Render procedures receive expanded complete rows and return a negative error code or number of rows processed.
- `height == 0` is a flush/end-of-input signal for renderers.
- The `w` argument is the number of samples, not pixels and not bytes; this matters for multi-component and 12-bit-expanded images.
- Class selector procedures are called in alphabetical/priority order and may update the image enumerator before returning a renderer.

## Notable Risks

- The "w is samples" contract is easy to violate because many callers naturally think in pixels or bytes.
- The class selection priority is implicit in function names, so renaming can affect renderer choice.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiclass.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxicolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxicolor.c

## Role

`gxicolor.c` implements Ghostscript's general color image renderer for images with 8 or fewer bits per sample after unpacking.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `gs_image_class_4_color`: image-class selector for general color rendering.
- `image_render_color`: renderer for color image scan lines.

## Important Behavior

- Initializes optimized mask-color tests by scaling image mask ranges to byte sample space and storing bitmask/test shortcuts.
- Uses a `color_samples` union so up to four byte samples can be compared quickly as a 32-bit key.
- Maintains a small clue/cache table for low-bit-depth colors (`spp * bps <= 12`) to avoid repeated color remapping.
- Coalesces adjacent source samples/runs that produce equal device colors and emits one fill per run.
- Handles portrait, landscape, and skewed images with rectangle or parallelogram fills.
- Supports gray/RGB/CMYK-like component counts, alpha cases for gray+alpha and CMYK+alpha conversion to RGB+alpha, and default DeviceN handling.
- Uses concrete color remapping for device color spaces and general `remap_color` otherwise.

## Dependencies And Integration

- Uses image DDA state, color-space decode/remap procs, color-map procs, device colors, RasterOp logical operations, and device fill methods.
- Uses `gx_image_clue` cache entries from the image enumerator.

## Notable Risks

- The renderer has duplicated fill logic for per-run and final-run paths; changes must be mirrored carefully.
- Cache use is disabled inside the DeviceN path but the comment says this should happen during initialization.
- The alpha path explicitly says DeviceN color plus alpha is unsupported.
- Correctness depends on `mask_color.mask/test/exact` matching the unpacked byte sample representation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxicolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxidata.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxidata.c

## Role

`gxidata.c` implements generic ImageType 1 image row enumeration, unpack/repack dispatch, renderer invocation, flush handling, image-device setup, and cleanup.

This is image enumeration/rendering infrastructure, not filesystem code.

## Main Functions

- `gx_image1_plane_data`: processes incoming image planes row by row, unpacks or repacks source data, advances DDA state, applies clipping prechecks, and calls the selected renderer.
- `gx_image1_flush`: sends the renderer a `height == 0` flush call for buffered data.
- `update_strip`: translates strip DDAs to the current row origin and resets pixel DDA state.
- `repack_bit_planes`: combines 1 to 8 one-bit source planes into byte-wide samples using lookup tables and spread.
- `setup_image_device`: wraps the target device with clipping and RasterOp forwarding devices when present.
- `gx_image1_end_image`: optionally flushes, releases scaler state, frees clip/rop devices, buffers, line storage, and the image enumerator.

## Important Behavior

- Tracks partial progress with `penum->used.x` and `penum->used.y` so rendering can resume after an error/interruption.
- Handles bit-planar input separately from chunky/multi-component plane input.
- Uses direct source data when possible, but unpacks into `penum->buffer` when expansion or multiple planes are needed.
- Computes integer row/column coverage for portrait and landscape postures before invoking non-interpolated renderers.
- Null bit planes are represented by a zero block in the destination buffer to avoid per-bit conditional tests.

## Dependencies And Integration

- Uses `gx_image_enum`, `gx_image_plane_t`, sample unpack procedures, sample lookup tables, DDA helpers, clip/ROP forwarding devices, and image scaler release hooks.
- Calls `gx_image_flush`/`gx_image1_flush` and renderer procedure pointers selected by image classes.

## Notable Risks

- `BCOUNT` combines width, data offset, samples per pixel, bits per sample, and plane count; mistakes in plane metadata can under/over-read rows.
- `repack_bit_planes` writes in groups of eight output bytes and relies on caller-provided padding/alignment in the image buffer.
- Error recovery manipulates DDA state and `used` counters; small changes can break resumability.
- `gx_image1_end_image` frees the enumerator itself, so callers must not touch it afterward.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxidata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxifast.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxifast.c

## Role

`gxifast.c` implements fast rendering paths for simple 1-bit-per-sample monochrome images in portrait or landscape orientation.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `gs_image_class_1_simple`: class selector for fast monobit rendering.
- `image_render_skip`: skips completely transparent images.
- `image_render_simple`: fast portrait/no-rotation monobit renderer.
- `image_render_landscape`: fast 90-degree rotated monobit renderer.

## Important Algorithms

- `gs_image_class_1_simple` only selects this path when there is no RasterOp, `spp == 1`, `bps == 1`, and posture is portrait or landscape.
- It replaces unpacking with `sample_unpack_copy`, configures line buffers when scaling/rotation needs them, and handles mask-color transparency by making one image color transparent or by selecting the skip renderer.
- `image_simple_expand` scales one input monobit row into an output bitmap row using fixed-point DDAs, run scanning, byte run-length lookup tables, and byte/bit masks.
- `copy_portrait` chooses between direct `copy_mono` for pure colors and `fill_masked`/background fill for non-pure or transparent device colors.
- `image_render_simple` can directly expand into a memory device bitmap for the common pure-color, unclipped, positive-scale case; otherwise it expands into a buffer and copies each output row.
- `image_render_landscape` buffers 8 scan-line groups, flips them with `memflip8x8`, and then copies the rotated block through the portrait copy path.

## Dependencies And Integration

- Uses `gsbittab` lookup tables, bitmap alignment constants, Ghostscript DDA macros, image enumerator fields, memory device internals, device color loading, `copy_mono`, and masked-fill device color methods.
- Uses `gzht.h` indirectly through included image/device infrastructure.

## Notable Risks

- This path is highly optimized and depends on bitmap alignment, byte bit ordering, and DDA rounding details.
- There are compiler-workaround comments around DDA step computations, indicating sensitivity to generated code.
- The direct-memory-device path writes into scan-line storage and preserves edge bytes manually; clipping and bounds checks are intentionally strict before using it.
- Statistics code is enabled under DEBUG and changes macro behavior only for counters, not rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxifast.c -->