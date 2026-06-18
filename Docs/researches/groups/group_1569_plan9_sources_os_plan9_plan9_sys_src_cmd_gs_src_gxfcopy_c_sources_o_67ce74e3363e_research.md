# Group Research: group_1569_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxfcopy_c_sources_o_67ce74e3363e

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.c

## Purpose
Implements Ghostscript high-level output font copying and incremental glyph subsetting. It creates copied font objects that preserve enough structural, metric, subroutine, and glyph-outline data to query/render/write subsets for Type 1/2, Type 42 TrueType, CIDFontType 0, and CIDFontType 2 fonts.

## Main Concepts
- Defines `gs_copied_font_data_t`, attached through `gs_font.client_data`, as the central copied-font state.
- Stores copied glyph vector data in `gs_copied_glyph_t` arrays indexed by glyph name hash slot, CID, or TrueType GID depending on font type.
- Maintains optional glyph-name tables, extra-name lists, Type 1/2 Subrs/GlobalSubrs, TrueType stripped font data, Type 42 fake metrics, Type 1/2 encodings, and CID maps.
- Supplies copied-font procedure vectors so copied fonts can answer `font_info`, `encode_char`, `enumerate_glyph`, `glyph_info`, `glyph_outline`, `glyph_name`, and `build_char`.

## Public API Implemented
- `gs_copy_font`: copies the non-glyph font shell and initializes font-type-specific copied data.
- `gs_copy_glyph`: copies one glyph plus dependent subglyph pieces.
- `gs_copy_glyph_options`: copy with `COPY_GLYPH_NO_OLD`, `COPY_GLYPH_NO_NEW`, and `COPY_GLYPH_BY_INDEX`.
- `gs_copied_font_add_encoding`: adds encoding entries for copied Type 1/2/42 fonts.
- `gs_copy_font_complete`: copies all glyphs and relevant encoding entries.
- `gs_copied_can_copy_glyphs`: compatibility check for merging/copying glyphs between fonts.
- `copied_drop_extension_glyphs`: removes extension glyph aliases before embedded font output.

## Font-Type Paths
- Type 1/Type 2:
  - Copies local and global subroutines.
  - Uses hashed glyph-name slots.
  - Copies CharString bytes and names.
  - Implements copied Type 1 glyph data, subr data, `seac` lookup, and outline interpretation.
- Type 42:
  - Writes stripped TrueType/CID2 data into memory via `psf_write_truetype_stripped` or `psf_write_cid2_stripped`.
  - Stores glyph outlines separately and patches fake hmtx/vmtx metrics.
  - Uses GID-indexed glyph slots and name-to-GID mapping.
- CIDFontType 0:
  - Copies CIDSystemInfo and Type 1/2 FDArray subfonts.
  - Shares parent glyph storage/global subrs with copied subfonts.
  - Stores FD index bytes as a prefix before charstring data.
- CIDFontType 2:
  - Extends Type 42 copying with a copied `CIDMap`.
  - Maps CIDs to GIDs and supports copying by CID or by GID.

## Important Internal Routines
- `copy_string` / `uncopy_string`: explicit GC-managed string duplication/freeing.
- `copy_subrs`: scans then copies Type 1/2 Subrs or GlobalSubrs into packed data plus start offsets.
- `copied_glyph_slot`, `named_glyph_slot_hashed`, `named_glyph_slot_linear`: glyph lookup and insertion-slot resolution.
- `copy_glyph_data`: detects duplicate/conflicting glyph definitions and owns copied vector bytes.
- `copy_glyph_name`: fills primary and extra glyph-name tables.
- `compare_glyphs`: compares widths, composite pieces, and outline bytes for compatibility.
- `same_type1_hinting`, `same_type42_hinting`, `same_cid0_hinting`, `same_cid2_hinting`: hinting compatibility checks.

## Dependencies
Uses core Ghostscript font, glyph, Type 1, Type 42, CID, path, text, stream, memory, and PostScript font writer internals, including `gxfont.h`, `gxfont1.h`, `gxfont42.h`, `gxfcid.h`, `gxfcopy.h`, `gxfcache.h`, `gxtype1.h`, `gxtext.h`, `gzstate.h`, and `gdevpsf.h`.

## Notable Risks / Edge Cases
- Compatibility logic is subtle because it compares both font identity/hinting and subset glyph outlines.
- `compare_glyphs` contains a suspicious self-comparison: `memcmp(gdata0.bits.data, gdata0.bits.data, gdata0.bits.size)`, which cannot detect differences against `gdata1`.
- `expand_CIDMap` allocates a replacement map but does not visibly free the previous map before overwriting `cfdata->CIDMap`.
- `copied_drop_extension_glyphs` has suspicious pointer use in one separator comparison: it passes `name + j` rather than the glyph-name byte buffer.
- Copied fonts intentionally do not preserve all PostScript dictionary data such as Metrics arrays, CDevProc, OtherSubrs, and full FontInfo.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.h

## Purpose
Declares the font-copying API used by high-level output devices and font-subsetting code.

## Public Interface
- `gs_copy_font`: copies a font shell without glyph data.
- `gs_copy_glyph`: copies a glyph and dependent subglyphs into a copied font.
- `gs_copy_glyph_options`: copies with stricter duplicate/new-glyph controls.
- `gs_copied_font_add_encoding`: adds a character-to-glyph encoding entry.
- `gs_copy_font_complete`: copies all glyphs and encoding data.
- `gs_copied_can_copy_glyphs`: checks whether another compatible font can provide glyphs.
- `copied_drop_extension_glyphs`: removes synthetic extension glyphs before embedding.

## Option Flags
- `COPY_GLYPH_NO_OLD`: error if top-level glyph was already copied.
- `COPY_GLYPH_NO_NEW`: error if top-level glyph was not already copied.
- `COPY_GLYPH_BY_INDEX`: interpret glyph as an index/GID where relevant.

## Documented Font Coverage
- Supports Type 1/2, Type 42, CIDFontType 0, and CIDFontType 2.
- Type 1/2 copying preserves Subrs and GlobalSubrs but not OtherSubrs.
- Type 42 copying strips/copies non-glyph TrueType data and copies outlines separately.
- CIDFontType 0 copies Type 1/2 subfonts and subroutines.
- CIDFontType 2 copies glyph data and CIDMap entries incrementally.

## Important Constraints
The header states copied fonts support querying and rendering but not `make_font`. It also warns that compatibility is the caller's responsibility for `gs_copy_glyph`, while `gs_copied_can_copy_glyphs` exists for explicit checking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.c

## Purpose
Implements dropout prevention for character rasterization in the path fill algorithm. It tracks thin quasi-horizontal stems during pseudo-rasterization and paints one-pixel repairs where normal trapezoid filling would leave visual gaps.

## Main Data Flow
- Maintains two active `margin_set` windows, each corresponding to a half-integer pixel-row sampling window.
- Each margin set has an ordered linked list of horizontal intervals (`margin`) and an array of per-X `section` samples.
- Filling code calls into this file while trapezoid bands are generated.
- When a margin window closes, `fill_margin` decides which pixels to paint and emits rectangles through the device fill path.

## Key Functions
- `init_section`: resets section state over an interval.
- `free_all_margins`: frees dynamically allocated margin records and clears the reusable list.
- `store_margin`: inserts/merges margin intervals in ordered form.
- `margin_boundary`: samples boundary intersections at half-integer X positions.
- `continue_margin_common`: records both sides of an active filled region into a margin set.
- `margin_interior`: marks fully painted interior pixels so dropout repair does not overpaint them.
- `process_h_lists`: handles horizontal path segments that form margin boundaries.
- `close_margins`: fills all pending margin intervals and releases their list.
- `start_margin_set`: advances the rolling pair of margin windows.

## Algorithms / Heuristics
- Uses `ADJUST_SERIF` and `CHECK_SPOT_CONTIGUITY` to reduce bad serif widening in small poorly hinted fonts.
- Computes padding from section `y0`/`y1` to decide whether to paint the lower or upper pixel in the row window.
- Treats interior coverage as `-2` sentinel values to suppress repair pixels where normal trapezoids already cover the spot.
- Reuses local margin storage first and falls back to GC allocation only when active margins exceed `MAX_LOCAL_ACTIVE`.

## Dependencies
Works tightly with `gxfill.c` and `gxfill.h` structures (`line_list`, `active_line`, `fill_options`), fixed-point math from `gxfixed.h`, devices/colors, and optional `vdtrace` debugging visualization.

## Notable Risks / Edge Cases
The code is intentionally heuristic and contains comments noting imperfect handling for bold characters and contacting serifs. It assumes no garbage collection while transient margins are active and uses simple GC descriptors accordingly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.h

## Purpose
Declares the dropout-prevention data structures and entry points shared between the fill algorithm and `gxfdrop.c`.

## Main Types
- `margin`: linked-list interval `[ibeg, iend)` of pixels to consider for repair.
- `section`: per-X sampling record containing fractional `y0`/`y1` boundary intersections, plus optional `x0`/`x1` coverage when serif/contiguity adjustment is enabled.
- `margin_set`: one row-window state with sampling Y coordinate, margin list, touched margin cache, and section array.

## Configuration
- `ADJUST_SERIF` is enabled.
- `CHECK_SPOT_CONTIGUITY` is enabled.
These control extra logic for small serif and stem repair choices.

## Public Functions
- `init_section`
- `free_all_margins`
- `close_margins`
- `process_h_lists`
- `margin_interior`
- `start_margin_set`
- `continue_margin_common`

## Integration
This header forward-declares `active_line` and `line_list`, showing it is intentionally coupled to the fill loop internals rather than being a standalone raster module.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfdrop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.c

## Purpose
Implements Ghostscript's core path filling algorithm: a topological spot decomposition with trapezoid and scanline backends, clipping integration, fill adjustment, shading optimization, spot analyzer support, and character dropout prevention.

## Public Entry Points
- `gx_adjust_if_empty`: expands nearly empty boxes so zero-width/epsilon-width fills can still mark pixels.
- `gx_default_fill_path`: default device `fill_path` implementation, with a special path for pattern/shading fills.
- Internal main routine `gx_general_fill_path`: orchestrates bounding, clipping, flattening, active-line construction, backend selection, and cleanup.

## Fill Pipeline
1. Compute path bounding box before flattening.
2. Decide whether pseudo-rasterization is needed for small character fills.
3. Check inner/outer clipping boxes and optionally wrap the target with a clip device.
4. Normalize fill adjustment fields for center-of-pixel and any-part-of-pixel behavior.
5. Flatten/copy/reduce path when needed, optionally merging contacting contours for large paths.
6. Build a Y-sorted active-line list from subpaths/segments/curves.
7. Select trapezoid or scanline filling backend.
8. Run the backend with banding constraints.
9. Release temporary path, active-line, margin, and section storage.

## Active-Line System
- `active_line` records a monotonic line/flattened curve piece, its current/next X, direction, iterator state, and linked-list position.
- `x_order`, `insert_y_line`, `insert_x_new`, `move_al_by_y`, `resort_x_line`, and `intersect_al` maintain Y and X ordering and handle segment crossings.
- Non-monotonic curves are split through `gx_flattened_iterator` and contour scanning logic.

## Backend Selection
- Trapezoid backend is preferred for pseudo-rasterization, non-curved paths, flat paths, and spot analyzer devices.
- Scanline backend is used where avoiding double writes matters, especially with non-idempotent RasterOps and fill adjustment.
- Rectangular non-idempotent fills can bypass the general algorithm and call rectangle ROP fill directly.
- Pattern 2 shading fills invert subdivision order: clip first, then let shading fill use the path intersection.

## Generated Template Use
Includes:
- `gxfillts.h` twice for direct/non-direct slanted trapezoid adjustment helpers.
- `gxfilltr.h` seven times for spot analyzer, pseudo-rasterization direct/non-direct, adjusted direct/non-direct, and unadjusted direct/non-direct trapezoid loops.
- `gxfillsl.h` twice for direct/non-direct scanline loops.

## Range List Support
The scanline backend uses `coord_range_list_t` to merge integer X ranges within a sampled Y pixel band, minimizing overdraw while preserving fill/eofill behavior.

## Dependencies
Depends on path, clipping, device, color, halftone tile, imager state, pattern, spot analyzer, dropout prevention, and fixed-point math headers.

## Notable Risks / Edge Cases
The implementation is arithmetic-heavy and has many comments about numerical corner cases: line intersections, triple intersections, non-monotonic curves, horizontal curve pieces, band boundaries, and fixed-point overflow. The pseudo-rasterization path is deliberately specialized for character sizes below a fixed threshold.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.h

## Purpose
Defines common internal data structures, macros, and statistics for the path filling algorithm and dropout-prevention integration.

## Main Types
- `active_line`: state for a segment/flattened curve active in the scan conversion process.
- `fill_options`: immutable options passed through fill loops, including device/color state, fill rule, adjustment, clipping box, direct-fill capability, and backend flags.
- `line_list`: per-fill transient state containing active-line pools, Y/X lists, horizontal lists, margin sets, local storage, and bbox dimensions.

## Important Macros
- `AL_X_AT_Y`: computes an active line's X coordinate at a fixed Y, with a fast integer path and a slower quotient path.
- `SET_NUM_ADJUST` / `ADD_NUM_ADJUST`: compensate for architecture-specific negative division behavior.
- `LOOP_FILL_RECTANGLE_DIRECT`: selects direct device rectangle fill versus ROP-aware rectangle fill based on template-time `FILL_DIRECT`.

## Local Storage Strategy
Provides stack/local arrays for common small fills:
- `MAX_LOCAL_ACTIVE`
- `MAX_LOCAL_SECTION`
- `local_active`
- `local_margins`
- `local_section0`
- `local_section1`

Dynamic allocation is reserved for unusually complex fills.

## Debug Support
When `DEBUG` is enabled, defines `stats_fill_t` counters and `INCR` macros used throughout `gxfill.c` and template headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfill.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillsl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillsl.h

## Purpose
Template header for generating scanline-based path fill loops. It is included multiple times by `gxfill.c` with different macro parameters.

## Template Inputs
- `FILL_DIRECT`: selects direct device rectangle writes or ROP-aware rectangle writes.
- `TEMPLATE_spot_into_scanlines`: generated function name.

## Algorithm
- Maintains active lines in X order.
- Computes Y sampling bands using adjustment-derived fractional limits.
- Uses fill rule accumulation (`INSIDE_PATH_P`) to determine filled X intervals.
- Merges ranges into `coord_range_list_t`.
- Emits one-pixel-high rectangles for each completed scanline range.
- Calls `merge_ranges` to include path portions spanning the current sample band.

## Integration
Relies on support routines and types defined in `gxfill.c` before inclusion: active-line management, range lists, fill options, and rectangle fill macros.

## Notable Characteristics
Unlike the trapezoid backend, this backend is designed to avoid repeated writes to the same pixel row when fill adjustment or non-idempotent RasterOps make overdraw unsafe.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillsl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfilltr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfilltr.h

## Purpose
Template header for generating trapezoid decomposition fill loops. `gxfill.c` includes it repeatedly to create specialized functions for spot analysis, pseudo-rasterization, fill adjustment, and direct/non-direct color writes.

## Template Inputs
- `IS_SPOTAN`: output trapezoids to spot analyzer instead of normal device fill.
- `PSEUDO_RASTERIZATION`: enable dropout-prevention margin tracking.
- `FILL_ADJUST`: include fill adjustment in geometry and raster decisions.
- `FILL_DIRECT`: choose direct rectangle fills or ROP-aware fills.
- `TEMPLATE_spot_into_trapezoids`: generated function name.

## Algorithm
- Pulls pending lines from `y_list` into X-sorted active state at each Y.
- Handles isolated horizontal lines specially.
- Computes next band top from segment ends, new segment starts, band limits, and intersections.
- Uses winding/even-odd accumulation to pair left/right boundaries.
- Emits rectangles for vertical-sided regions and trapezoids for slanted regions.
- Calls slanted-adjust helpers when fill adjustment needs more precise decomposition.
- In pseudo-rasterization mode, calls margin/dropout helpers around every filled or skipped band.

## Spot Analyzer Path
When `IS_SPOTAN` is enabled, stores trapezoid topology through `gx_san_trap_store` rather than painting directly, preserving segment pointers and boundary directions.

## Dropout Path
When `PSEUDO_RASTERIZATION` is enabled, invokes:
- `start_margin_set`
- `complete_margin`
- `margin_interior`
- `add_margin`
- `process_h_lists`
- `close_margins`

## Notable Characteristics
The generated loops are highly optimized by compile-time macros and avoid runtime conditionals for common fill modes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfilltr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillts.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillts.h

## Purpose
Template header for generating slanted-trapezoid fill-adjustment helpers. It is included by `gxfill.c` for direct and non-direct rectangle fill variants.

## Template Inputs
- `FILL_DIRECT`: direct device fill versus ROP-aware fill.
- `TEMPLATE_slant_into_trapezoids`: generated helper name.

## Algorithm
Handles the geometry produced by dragging an adjustment square along trapezoid borders. It distinguishes:
- top wider than bottom,
- bottom wider than top,
- genuinely slanted trapezoids requiring `fill_slant_adjust`.

## Key Details
- Uses adjusted left/right edges and `adjust_below`/`adjust_above`.
- Adds single-row rectangle repairs where adjusted top or bottom spans an additional pixel.
- Uses `loop_fill_trap_np` for clipped trapezoid fills that do not require pseudo-rasterization.

## Integration
Called from adjusted trapezoid loops in `gxfilltr.h` when a filled region has slanted boundaries and vertical fill adjustment is active.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfillts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfixed.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfixed.h

## Purpose
Defines Ghostscript's internal fixed-point coordinate representation and conversion/rounding macros.

## Representation
- `fixed` is `long`.
- `ufixed` is `ulong`.
- Uses 8 fractional bits via `_fixed_shift`.
- `fixed_scale` is 256, so `fixed_1` is one device/user coordinate unit in fixed representation.
- Provides `gs_fixed_point` and `gs_fixed_rect`.

## Conversion Macros
Includes conversions between fixed and int/long/float:
- `int2fixed`
- `fixed2int`, `fixed2int_rounded`, `fixed2int_ceiling`, `fixed2int_pixround`
- variable optimized forms such as `fixed2int_var`
- `float2fixed`, `float2fixed_rounded`, `fixed2float`

## Rounding Model
Defines special pixel rounding for Ghostscript's center-of-pixel fill rule:
- `_fixed_pixround_v`
- `fixed_pixround`
- `fixed2int_pixround`

## Arithmetic / Overflow
- `CHECK_SET_FIXED_SUM` detects fixed addition overflow and clamps result.
- Declares `fixed_mult_quo` for high-precision `A * B / C`.
- Provides optional FPU-free helpers for float/double to fixed conversion under `USE_FPU_FIXED`.

## Integration
This header is foundational for path geometry, fill scan conversion, glyph outlines, and rasterization decisions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfixed.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfmap.h

## Purpose
Defines cached fraction-to-fraction transfer maps used in Ghostscript color processing.

## Main Type
`gx_transfer_map` contains:
- reference-count header,
- legacy `proc`,
- newer `closure`,
- changing `id`,
- cached `frac values[transfer_map_size]`.

## Constants
- `log2_transfer_map_size` is 8.
- `transfer_map_size` is 256.
- Interpolation is enabled when `log2_transfer_map_size <= 8`.

## Public/Declared Operations
- `gx_set_identity_transfer`: initializes identity map.
- `gx_color_frac_map`: interpolating map helper when enabled.
- `gx_map_color_frac`: maps a `frac` through a transfer map.
- `gx_map_color_float`: maps a float by table lookup.
- `gs_mapped_transfer`: closure-style lookup function.
- `gs_identity_transfer`: identity transfer procedure.

## Integration
Used by color transfer, black generation, and undercolor removal paths. It depends on `gxfrac.h`, transfer-map closure definitions, reference counting, and GC descriptors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont.h

## Purpose
Defines Ghostscript's core font object model, font information records, glyph information records, and font procedure vector.

## Main Types
- `gs_font_info_t`: font-level metrics and descriptor-like fields, including PDF FontDescriptor-compatible values plus names/copyright strings.
- `gs_glyph_info_t`: glyph-level width, bbox, composite-piece, vertical-vector, and outline-width information.
- `gs_font_procs`: virtual procedure table for font definition, scaling, encoding, glyph enumeration, glyph metrics, outlines, glyph names, and text rendering.
- `gs_font`: base generic font object with memory, directory, notify list, matrix, type, bitmap behavior, WMode, PaintType, StrokeWidth, names, and procedures.
- `gs_font_base`: non-composite base font with FontBBox, UID, FAPI hooks, and encoding indexes.

## Key Procedure Groups
- Font-level: `define_font`, `make_font`, `font_info`, `same_font`.
- Glyph-level: `encode_char`, `decode_glyph`, `enumerate_glyph`, `glyph_info`, `glyph_outline`, `glyph_name`.
- Rendering-level: `init_fstack`, `next_char_glyph`, `build_char`.

## Important Contracts
- `glyph_info` implementers must derive WMode from requested flags, not from `font->WMode`, because descendant fonts can inherit WMode.
- `glyph_outline` similarly receives explicit WMode.
- Subclasses of `gs_font` must use `gs_font_finalize`.
- Font names are fixed-size `gs_font_name` records used for font directory and high-level output lookup.

## Declared Helpers
- Font allocation and notification helpers.
- Default/no-op procedure declarations.
- `gs_font_glyph_is_notdef`.
- `gs_font_parent`.
- `gx_extendeg_glyph_name_separator`, used by PDF width/metrics glyph-name conflict logic and copied-font cleanup.

## Integration
This is the central dependency for `gxfcopy.c`, Type 0/1/42 font headers, text rendering, font cache, and high-level output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0.h

## Purpose
Defines Ghostscript Type 0 composite font data and procedure declarations.

## Mapping Types
Defines `fmap_type` values matching PostScript `FMapType` dictionary values:
- `fmap_8_8`
- `fmap_escape`
- `fmap_1_7`
- `fmap_9_7`
- `fmap_SubsVector`
- `fmap_double_escape`
- `fmap_shift`
- `fmap_CMap`

## Main Type
`gs_type0_data` stores:
- mapping mode and escape/shift bytes,
- `SubsVector` metadata,
- `Encoding`,
- `FDepVector`,
- optional `CMap`.

## Font Type
`gs_font_type0` embeds `gs_font_common` plus `gs_type0_data`.

## Declared Procedures
- `gs_type0_define_font`
- `gs_type0_make_font`
- `gs_type0_init_fstack`
- `gs_type0_next_char_glyph`

## Integration
Used for composite font dispatch and CID-wrapped fonts. It supplies the structures consumed by `gxfont0c.h` wrapper constructors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0c.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0c.h

## Purpose
Declares helper constructors for Type 0 composite font wrappers around CIDFont and Type 42/TrueType font data.

## Declared Constructors
- `gs_font_type0_from_cidfont`: creates a Type 0 wrapper for a CIDFont, with optional matrix.
- `gs_font_type0_from_type42`: creates a Type 0 wrapper for a Type 42 font converted to Type 2 CIDFont, optionally using the TrueType cmap as the CMap.
- `gs_font_cid2_from_type42`: creates a CIDFontType 2 object from Type 42.
- `gs_cmap_from_type42_cmap`: creates a Unicode-marked CMap from a TrueType cmap, limited to Platform 3, Encoding 1, Format 4.

## Dependencies
Includes `gxfont0.h` and `gxfcid.h`, tying composite-font wrapping to CID font internals and Type 42 support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0c.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont1.h

## Purpose
Defines Ghostscript Type 1 and Type 2 font data structures and procedure interfaces.

## Main Types
- `gs_type1_data_procs_t`: callback table for glyph data, Subr data, `seac` data, and OtherSubr stack interaction.
- `gs_type1_data`: Type 1/2 interpreter data, callback data, parent Type 9 font pointer, encryption length, subroutine biases, width defaults, random seed, and hinting parameters.
- `gs_font_type1`: `gs_font_base_common` plus `gs_type1_data`.

## Hinting Data
Stores Type 1 hint tables and parameters:
- Blue values/family blues/other blues,
- standard stem widths,
- stem snap arrays,
- weight vector,
- force bold, language group, expansion and rounding fields.

## Declared Procedures
- `gs_type1_glyph_info`
- `gs_type1_piece_codes`

## Integration With Font Copying
`gxfcopy.c` uses this header to:
- copy glyph CharString bytes,
- copy Subrs/GlobalSubrs,
- invoke Type 1 glyph info,
- interpret copied outlines,
- detect `seac` pieces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont42.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont42.h

## Purpose
Defines Ghostscript Type 42 / TrueType font data structures and procedure declarations.

## Main Types
- `gs_type42_mtx_t`: metrics table descriptor with count, offset, and length.
- `gs_type42_data`: TrueType access callbacks, outline/metric procedures, cached table offsets, unitsPerEm, loca format, metrics tables, glyph counts, glyph lengths, glyph cache, and warning flags.
- `gs_font_type42`: `gs_font_base_common` plus `gs_type42_data`.

## Key Callbacks
- `string_proc`: retrieves bytes from the TrueType data source.
- `get_glyph_index`: maps Ghostscript glyph to TrueType GID.
- `get_outline`: retrieves glyph outline bytes.
- `get_metrics`: retrieves glyph metrics for WMode.

## Declared Procedures
- `gs_type42_font_init`
- `gs_type42_append`
- `gs_type42_get_metrics`
- `gs_type42_wmode_metrics`
- `gs_type42_default_get_metrics`
- `gs_type42_get_outline_from_TT_file`
- `gs_type42_enumerate_glyph`
- `gs_type42_glyph_info`
- `gs_type42_glyph_outline`
- `gs_type42_glyph_info_by_gid`

## Integration With Font Copying
`gxfcopy.c` creates copied Type 42 fonts by storing stripped TrueType data, overriding callbacks, copying selected glyph outlines, and filling fake hmtx/vmtx data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont42.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfrac.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfrac.h

## Purpose
Defines Ghostscript's compact fractional color representation and conversion helpers.

## Representation
- `frac` and `signed_frac` are `short`.
- Uses 15 effective bits.
- `frac_1` is `0x7ff8`, deliberately chosen so common fractions can be represented more exactly than with a full `32767` scale.

## Conversion Helpers
- `frac2float`
- `float2frac`
- `frac2bits`
- `bits2frac`
- `frac2byte`
- `byte2frac`
- `frac2bits_floor`
- `frac2ushort`
- `ushort2frac`

## Arithmetic Helpers
- `frac_1_quo`: quotient for product divided by `frac_1`.
- `frac_1_rem`: remainder after that quotient.

## Integration
Used by transfer maps, color mapping, halftoning, and other internal color calculations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfrac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxftype.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxftype.h

## Purpose
Defines Ghostscript font type identifiers and bitmap font behavior values.

## Font Types
`font_type` values mirror PostScript `FontType` values:
- composite Type 0,
- Type 1 encrypted,
- Type 2 encrypted,
- user-defined,
- disk-based,
- CIDFontType 0,
- CIDFontType 1,
- CIDFontType 2,
- Chameleon,
- CID bitmap,
- TrueType Type 42.

## Bitmap Behavior
`fbit_type` values mirror `ExactSize`, `InBetweenSize`, and `TransformedChar` dictionary entries:
- use outlines,
- use bitmaps,
- transform bitmaps.

## Integration
Included by `gxfont.h` and indirectly used by all font implementation and font-copying paths for type dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxftype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfunc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfunc.h

## Purpose
Declares internal helpers for Ghostscript Function objects.

## Main GC Definition
Declares `st_function` and `public_st_function`, marking the generic function type with two pointer fields:
- `params.Domain`
- `params.Range`

## Declared Helpers
- `fn_common_free_params`
- `fn_common_free`
- `fn_check_mnDR`
- `gs_function_get_info_default`
- `fn_common_get_params`
- `fn_copy_values`
- `fn_scale_pairs`
- `fn_common_scale`
- `fn_common_serialize`

## Responsibilities
The helpers cover common Function lifecycle, validation, parameter export, value copying, range/decode scaling, and serialization behavior.

## Integration
Used by concrete PostScript/PDF function implementations. Depends on `gsfunc.h` and Ghostscript structure/GC macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfunc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxgetbit.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxgetbit.h

## Purpose
Defines the parameter interface and helper declarations for the device `get_bits_rectangle` procedure.

## Main Types
- `gs_get_bits_options_t`: alias of `gx_bitmap_format_t`.
- `gs_get_bits_params_t`: options, up to 32 data plane pointers, returned X offset, and raster.

## Contract
- Devices update `options` to the actual chosen bitmap format.
- If input options are zero, the device must report supported options and return an error.
- All devices must support at least one option in each bitmap-format group and `GB_COLORS_NATIVE`.
- Default implementation only supports a limited set: 8-bit depth, chunky packing, return-copy behavior, and requires chunky packing support.

## Declared Helpers
- `gx_get_bits_return_pointer`: tries to satisfy the request by returning a pointer into stored data.
- `gx_get_bits_copy`: satisfies the request by copying from source bytes into caller-requested output form.

## Integration
Used by device implementors and clients needing bitmap extraction without depending on the full driver-client header surface.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxgetbit.h -->