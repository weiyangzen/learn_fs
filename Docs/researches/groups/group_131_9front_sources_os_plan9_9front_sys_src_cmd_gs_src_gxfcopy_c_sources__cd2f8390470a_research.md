# Group Research: group_131_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxfcopy_c_sources__cd2f8390470a

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.c

Implements Ghostscript font copying/subsetting for high-level output devices.

Key behavior:
- Defines copied-font private data for glyph byte strings, glyph names, extra glyph aliases, copied font metadata, Type 1/CFF subrs, TrueType/CID backing data, encodings, and CID maps.
- Provides GC descriptors for copied glyph arrays, name arrays, extra-name lists, and copied-font data.
- `gs_copy_font` creates a copied font shell for Type 1/2, Type 42 TrueType, CIDFontType 0, and CIDFontType 2 fonts without copying all glyphs up front.
- `gs_copy_glyph_options` copies one glyph and recursively copies component glyphs discovered through `psf_add_subset_pieces`.
- Type 1/2 path copies local/global subrs, charstrings, glyph names, `.notdef`, and provides glyph-data/subr/seac accessors for the copied font.
- Type 42 path writes stripped TrueType/CID2 font data to memory, stores glyph outlines separately, fakes hmtx/vmtx metrics space, and maps names to GIDs.
- CIDFontType 0 path copies FDArray subfonts and shares parent glyph/subr storage with copied subfonts.
- CIDFontType 2 path maintains an expandable `CIDMap` from copied CIDs to TrueType GIDs.
- `gs_copy_font_complete` enumerates all glyphs and copies Encoding entries where relevant.
- `gs_copied_can_copy_glyphs` checks whether glyph subsets can be merged by comparing font type/name/WMode, optional hinting data, and glyph outlines/metrics.
- `copied_drop_extension_glyphs` removes synthetic extension glyphs used to resolve PDF Widths-to-Metrics name conflicts before embedding.

Dependencies:
- Uses core font structures from `gxfont.h`, `gxfont1.h`, `gxfont42.h`, and CID support from `gxfcid.h`.
- Uses glyph cache marking through `gs_font_dir`.
- Uses Type 1 interpreter support for outlining copied Type 1 glyphs.
- Uses `gdevpsf.h` subset/piece discovery and stripped TrueType/CID writing helpers.
- Uses Ghostscript memory, GC, string, matrix, path, and graphics-state APIs.

Research notes:
- Copied fonts deliberately do not support `make_font`; they support querying, glyph outlining, and BuildChar-style rendering for already copied glyphs.
- Type 1 glyph-name lookup uses hashed storage sized to prime values to guarantee reprobe termination.
- TrueType copied glyph storage is indexed by GID; CIDFontType 2 adds a CID-to-GID layer.
- The compatibility check is important for high-level output font merging and prevents mixing same-named but structurally different fonts.
- Potential risk: `compare_glyphs` contains a suspicious `memcmp(gdata0.bits.data, gdata0.bits.data, ...)`, which compares a buffer with itself rather than with `gdata1`.
- Potential risk: `copied_drop_extension_glyphs` has fragile pointer/string arithmetic in the extension-name separator checks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.h

Declares the public API for high-level-output font copying and glyph subsetting.

Key declarations:
- `gs_copy_font` copies a font shell, excluding most glyph definitions.
- `gs_copy_glyph` copies one glyph and any sub-glyphs into a copied font.
- `gs_copy_glyph_options` adds `COPY_GLYPH_NO_OLD`, `COPY_GLYPH_NO_NEW`, and `COPY_GLYPH_BY_INDEX`.
- `gs_copied_font_add_encoding` adds character-to-glyph encoding entries for copied character-indexed fonts.
- `gs_copy_font_complete` copies all glyphs and relevant encoding entries.
- `gs_copied_can_copy_glyphs` checks whether glyphs from another font are compatible with an existing copied font.
- `copied_drop_extension_glyphs` removes synthetic extension glyphs before embedding.

Behavior contract:
- Supports Type 1/2, Type 42, CIDFontType 0, and CIDFontType 2.
- Does not copy PostScript-only data such as Metrics arrays, CDevProc, and full FontInfo beyond `font_info`.
- Destination fonts must come from `gs_copy_font`.
- `gs_copy_glyph` does not itself verify source/destination compatibility.

Dependencies:
- Includes `gsccode.h` and forward-declares `gs_font` and `gs_matrix`.

Research notes:
- The header is the contract for font subsetting used by high-level output devices such as PDF/PS writers.
- The comments are unusually detailed and define the per-FontType limitations that callers must respect.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcopy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.c

Implements dropout prevention for character rasterization during path filling.

Key behavior:
- Manages `margin` interval lists and `section` arrays used by pseudo-rasterization.
- Uses two moving `margin_set` windows centered on half-pixel Y positions to track thin painted regions around pixel rows.
- `store_margin` inserts and merges touching margin intervals while maintaining ordered linked lists.
- `margin_boundary` records intersections of path boundaries with half-pixel X probes.
- `continue_margin_common`, `margin_interior`, and horizontal-list processing mark candidate dropout areas as fills, boundaries, or interiors.
- `fill_margin` chooses whether to paint an extra pixel row based on recorded upper/lower section contact and serif-adjustment heuristics.
- `close_margins` flushes pending margin intervals to device rectangles.
- `start_margin_set` rotates the two margin sets when the fill loop advances across a pixel-center window.
- Allocates most margins from local `line_list` storage and falls back to GC-managed allocation only if needed.

Dependencies:
- Depends on `gxfill.h` line-list/active-line state and `gxfdrop.h` margin structures.
- Uses `gxdevice.h`, `gxdcolor.h`, and fill rectangle macros to emit corrective pixels.
- Uses `gxfixed.h` fixed-point math and `vdtrace.h` debugging visualization.

Research notes:
- This code only runs for pseudo-rasterized character fills, not normal fills with nonzero adjustment.
- The algorithm targets thin quasi-horizontal stems generated from flattened paths, where normal trapezoid filling may miss a visible pixel.
- `ADJUST_SERIF` and `CHECK_SPOT_CONTIGUITY` are enabled, so serif and spot-contiguity heuristics are active.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.h

Defines data structures and interfaces for glyph-fill dropout prevention.

Key definitions:
- `ADJUST_SERIF` and `CHECK_SPOT_CONTIGUITY` enable serif adjustment and local spot-contiguity checks.
- `margin` describes a pixel-index interval to paint.
- `section` stores fractional Y intersections for a half-integer X probe and, when enabled, X coverage bounds.
- `margin_set` groups one half-pixel Y window, its interval list, touched-cache pointer, and section array.
- Debug visualization macros define scale and colors for trapezoids and margins.

Key declarations:
- `init_section`
- `free_all_margins`
- `close_margins`
- `process_h_lists`
- `margin_interior`
- `start_margin_set`
- `continue_margin_common`

Dependencies:
- Forward-declares `active_line` and `line_list`.
- Uses `fixed`, `gx_device`, and Ghostscript GC struct declarations.

Research notes:
- The long header comment is the clearest overview of pseudo-rasterization: two moving `1xN` pixel windows track painted margins and decide whether to add fallback pixels.
- This header is tightly coupled to `gxfill.c` internals rather than a general public API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfill.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfill.c

Implements Ghostscript’s main topological path-fill algorithm with scanline, trapezoid, dropout-prevention, and spot-analysis paths.

Key behavior:
- Builds a Y-sorted list of active path edges from subpaths, adding temporary close segments when needed.
- Handles line and curve segments, using flattened iterators for non-monotonic curves and preserving enough topology for TrueType grid fitting/spot analysis.
- Chooses between trapezoid decomposition and scanline filling based on character status, curves, flatness, RasterOp idempotence, rectangle fast paths, shading, and spot-analyzer devices.
- `gx_general_fill_path` computes path/clip bounding boxes, fill adjustment, pseudo-rasterization eligibility, clipping-device setup, flattening/reduction, and fill-loop dispatch.
- `gx_default_fill_path` routes shading PatternType 2 fills through a path/clip intersection optimization before falling back to the general fill engine.
- Active-line code orders edges by current X and slope, detects segment endings, moves lines across Y bands, and re-sorts after crossings.
- Intersection handling splits bands at edge crossings and normalizes `x_next` values to preserve monotonic X ordering, including triple-intersection mitigation.
- Trapezoid variants are generated by repeated inclusion of `gxfilltr.h`; scanline variants by `gxfillsl.h`; slanted adjusted trapezoid variants by `gxfillts.h`.
- Range-list code merges scanline X intervals before painting, avoiding duplicate writes for non-idempotent RasterOps.
- Pseudo-rasterization hooks call `gxfdrop.c` margin tracking to add dropout-prevention pixels for small character fills.

Dependencies:
- Uses path/clip internals from `gzpath.h` and `gzcpath.h`.
- Uses device color, halftone tile, imager state, pattern shading, spot analyzer, and device drawing helpers.
- Includes template headers `gxfilltr.h`, `gxfillsl.h`, and `gxfillts.h` multiple times with different macro configurations.
- Uses `gxfdrop.h` for character dropout prevention and `gxfill.h` for active-line/fill-option structures.

Research notes:
- This is one of the central rasterization files: it bridges vector path topology to device rectangle/trapezoid calls.
- Pseudo-rasterization is limited to character fills under roughly 500 pixels in width/height and skipped for spot-analyzer devices.
- The code has many numerical guardrails around fixed-point overflow, curve extrema, crossings, vertical stems, and band boundaries.
- Rectangle fills with non-idempotent RasterOps get special handling to avoid double-writing pixels.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfill.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfill.h

Defines shared structures and macros for the fill algorithm and dropout prevention.

Key definitions:
- `active_line` stores segment endpoints, deltas, current/next X, direction, curve iterator, monotonicity flags, and list links.
- `AL_X_AT_Y` computes edge X at a given Y with a fast fixed-point path and slower quotient fallback.
- `fill_options` packages device color, RasterOp, clipping box, fill rule, adjustment values, flatness, device callbacks, and algorithm flags.
- `line_list` owns pending Y list, active X list, horizontal-line lists, margin sets, local allocation pools, bbox fields, and fill options.
- `LOOP_FILL_RECTANGLE_DIRECT` switches between pure-color device fill and RasterOp-aware rectangle fill.
- Debug-only `stats_fill_t` tracks counters for allocation, sorting, banding, crossings, and fill operations.

Dependencies:
- Requires `active_line` users to know `segment`, `gx_flattened_iterator`, `gx_device`, `gx_device_color`, and `margin_set`.
- Consumed by `gxfill.c`, `gxfdrop.c`, and the fill template headers.

Research notes:
- This header exposes internal fill-engine state, not a stable public graphics API.
- The local arrays avoid allocator churn for common small fills; large/complex fills fall back to dynamic allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfill.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillsl.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillsl.h

Template header that generates scanline fill-loop variants.

Key behavior:
- Defines `TEMPLATE_spot_into_scanlines(line_list *, fixed band_mask)` under caller-supplied macro names.
- Supports direct pure-color rectangle fills or RasterOp-aware fills through `FILL_DIRECT`.
- Maintains a `coord_range_list_t` of X ranges for each output scanline.
- Advances active lines by sampling Y bands derived from fill adjustment values.
- Inserts newly active non-horizontal edges into the X list.
- Uses winding or even-odd fill logic through `INSIDE_PATH_P`.
- Calls `merge_ranges` to include regions contributed by active segments across the same pixel band.
- Flushes merged ranges as one-pixel-high rectangles.

Template parameters:
- `FILL_DIRECT`
- `TEMPLATE_spot_into_scanlines`

Dependencies:
- Must be included from `gxfill.c`, where helper types/functions and range-list machinery are defined.

Research notes:
- This file is intentionally not include-guarded as a normal header because it is included multiple times with different macro definitions.
- The scanline path is important when non-idempotent RasterOps or fill adjustment make trapezoid double-writing unsafe.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillsl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfilltr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfilltr.h

Template header that generates trapezoid decomposition fill-loop variants.

Key behavior:
- Defines `TEMPLATE_spot_into_trapezoids(line_list *, fixed band_mask)` under macro control.
- Moves edges from Y-sorted pending list into X-sorted active list as the sweep advances.
- Handles isolated horizontal segments directly or records them for pseudo-rasterization.
- Computes next Y band from pending starts, edge ends, band masks, and intersections.
- Uses `intersect_al` to split bands at crossings.
- Generates fill regions using winding/even-odd inside transitions.
- Emits rectangles for vertical-sided regions, trapezoids for slanted regions, and spot-analyzer trap records for spot-analysis devices.
- Calls slanted-adjust helpers when fill adjustment requires expanded trapezoid geometry.
- Integrates pseudo-rasterization by starting/closing margin sets, processing horizontal lists, and recording margins/interiors around filled trapezoids.

Template parameters:
- `IS_SPOTAN`
- `PSEUDO_RASTERIZATION`
- `FILL_ADJUST`
- `FILL_DIRECT`
- `TEMPLATE_spot_into_trapezoids`

Dependencies:
- Included repeatedly by `gxfill.c`.
- Relies on `gxfill.c` helpers such as `insert_x_new`, `move_al_by_y`, `process_h_segments`, `intersect_al`, `complete_margin`, and `process_h_lists`.

Research notes:
- This is the hot path for most non-scanline fills.
- The macro specializations remove runtime branches for the common combinations of spot analysis, pseudo-rasterization, fill adjustment, and direct color writes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfilltr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillts.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillts.h

Template header that generates adjusted slanted-trapezoid filling helpers.

Key behavior:
- Defines `TEMPLATE_slant_into_trapezoids(const line_list *, const active_line *, const active_line *, fixed, fixed)`.
- Models fill adjustment as dragging a square around the trapezoid boundary, not simply expanding corners.
- Distinguishes top-wider, bottom-wider, and generally slanted cases.
- Uses direct rectangle fills for one-pixel adjustment caps where possible.
- Delegates complex slanted cases to `fill_slant_adjust`.
- Uses `loop_fill_trap_np` for clipped trapezoid emission.

Template parameters:
- `FILL_DIRECT`
- `TEMPLATE_slant_into_trapezoids`

Dependencies:
- Included by `gxfill.c` after `fill_slant_adjust` and `loop_fill_trap_np` are defined.

Research notes:
- This is a geometry-correctness helper for fill-adjusted paths.
- It avoids over-simplified expansion that would distort slanted trapezoid edges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfillts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfixed.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfixed.h

Defines Ghostscript’s fixed-point coordinate representation and conversion/arithmetic helpers.

Key definitions:
- `fixed` is a signed long; `ufixed` is an unsigned long.
- Fixed coordinates use 8 fractional bits (`fixed_scale == 256`).
- Provides constants such as `fixed_0`, `fixed_epsilon`, `fixed_1`, `fixed_half`, `max_fixed`, and `min_fixed`.
- Provides integer/float conversions, rounding, ceiling, floor, pixel rounding, fraction extraction, and truncation macros.
- Defines `CHECK_SET_FIXED_SUM` for overflow-detecting fixed addition.
- Declares `fixed_mult_quo` for safe `A * B / C` when products may exceed a long.
- Provides optional FPU-less IEEE helpers for float/double to fixed conversion.
- Defines `gs_fixed_point` and `gs_fixed_rect`.

Dependencies:
- Uses architecture macros such as `ARCH_SIZEOF_LONG`, `arch_ints_are_short`, `arch_is_big_endian`, and FPU-related feature flags.
- Uses Ghostscript error codes for limitcheck handling.

Research notes:
- Pixel rounding is central to the fill code’s center-of-pixel rule.
- The 8-bit fractional choice balances coordinate range with enough precision for rasterization.
- Many fill algorithms depend on the exact semantics of `fixed_pixround`, `fixed2int_pixround`, and `fixed_mult_quo`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfixed.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfmap.h

Defines cached color transfer-map representation and lookup helpers.

Key definitions:
- `gx_transfer_map` stores a reference-count header, legacy mapping proc, closure, changing ID, and `frac` lookup table.
- Transfer maps use `transfer_map_size == 256`.
- `public_st_transfer_map` declares GC traversal over the mapping closure/proc state.
- `gx_set_identity_transfer` initializes identity maps.
- `gx_map_color_frac` maps fractional color components through the cache, interpolating when the table is small enough.
- `gx_map_color_float` maps float inputs through the cache.
- Declares `gs_mapped_transfer` and `gs_identity_transfer`.

Dependencies:
- Includes `gsrefct.h`, `gsstype.h`, `gxfrac.h`, and `gxtmap.h`.
- `gx_color_frac_map` implementation is in `gxcmap.c`.

Research notes:
- This is used by imager/color state for transfer functions, black generation, and undercolor removal.
- The comments note an intermediate migration from `proc` to `closure`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont.h

Defines the core Ghostscript font object model, font information structures, glyph information structures, and font procedure vectors.

Key definitions:
- `gs_font_info_t` reports font-level descriptor data such as ascent, bbox, flags, widths, names, copyright, and metrics.
- `gs_glyph_info_t` reports glyph widths, vertical origin, bbox, composite pieces, outline-width distinction, vertical vectors, and CDevProc allowance.
- `gs_font_procs` defines font-level, glyph-level, and glyph-rendering virtual methods.
- Declares default/no-op font procs and `gs_font_procs_default`.
- `gs_font_name` stores short font/key names.
- `gs_font_common` defines base font object fields: links, memory, directory, IDs, base font, matrix, type, bitmap policy, WMode, PaintType, StrokeWidth, procedure vector, key/font names.
- `gs_font` is the generic font object.
- `gs_font_base_common` extends generic fonts with FontBBox, UID, FAPI hooks, and encoding indexes.
- `gs_font_base` is the common base for non-composite fonts.

Key declarations:
- `gs_font_alloc`
- `gs_font_notify_init`
- `gs_font_notify_register`
- `gs_font_notify_unregister`
- `gs_font_base_alloc`
- `gx_extendeg_glyph_name_separator`
- `gs_font_glyph_is_notdef`
- `gs_font_parent`

Dependencies:
- Includes character code, public font, glyph data, matrix, notify, UID, GC struct, and font-type headers.

Research notes:
- This is the central internal font ABI used by copied fonts, Type 1, Type 42, composite fonts, text rendering, and high-level output.
- Comments emphasize that `glyph_info`/`glyph_outline` implementations must derive WMode from arguments rather than reading `font->WMode` for descendant fonts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0.h

Defines Type 0 composite font data structures and procedures.

Key definitions:
- `fmap_type` enumerates Type 0 `FMapType` values: `8/8`, escape, `1/7`, `9/7`, SubsVector, double escape, shift, and CMap.
- `fmap_type_is_modal` identifies escape/double-escape/shift mapping modes.
- `gs_type0_data` stores mapping controls, SubsVector metadata, Encoding, FDepVector, and optional CMap.
- `gs_font_type0` extends `gs_font_common` with `gs_type0_data`.
- Declares GC structure metadata for Type 0 fonts.

Key declarations:
- `gs_type0_define_font`
- `gs_type0_make_font`
- `gs_type0_init_fstack`
- `gs_type0_next_char_glyph`

Dependencies:
- Forward-declares `gs_cmap_t`.
- Uses `gs_font_common` and font proc macros from `gxfont.h`.

Research notes:
- Type 0 fonts are dispatch/wrapper fonts that map input character codes into descendant fonts.
- This header provides the data layout consumed by composite-font show enumeration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0c.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0c.h

Declares helper APIs for creating Type 0 wrappers and CID/CMap conversions.

Key declarations:
- `gs_font_type0_from_cidfont` creates a Type 0 wrapper for a CIDFont, with optional matrix and WMode.
- `gs_font_type0_from_type42` creates a Type 0 wrapper around a Type 42 font converted to a Type 2 CIDFont, optionally using the TrueType cmap.
- `gs_font_cid2_from_type42` converts a Type 42 font into a Type 2 CIDFont.
- `gs_cmap_from_type42_cmap` creates a Unicode-based CMap from a TrueType Platform 3, Encoding 1, Format 4 cmap.

Dependencies:
- Includes `gxfont0.h` and `gxfcid.h`.

Research notes:
- This is glue between simple TrueType/CID font representations and composite Type 0 font machinery.
- The CMap helper is intentionally limited to a specific TrueType cmap format.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0c.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont1.h

Defines Type 1 and Type 2 font internal data structures and callbacks.

Key definitions:
- `zone_table`, `float_array`, and `stem_table` macros define compact hint-parameter arrays.
- `gs_type1_data_procs_t` provides callbacks for glyph data, local/global subr data, seac data, and OtherSubrs push/pop stack interaction.
- `gs_type1_data` stores charstring interpreter callback, procedure data, parent Type 9 font, encryption length, Type 2 subr biases/random seed/default width/nominal width, and Type 1 hinting parameters.
- Hinting fields include Blue values, family zones, OtherBlues, StdHW/StdVW, StemSnapH/V, ForceBold, LanguageGroup, and WeightVector.
- `gs_font_type1` extends `gs_font_base_common` with `gs_type1_data`.
- Declares GC metadata for Type 1 fonts.

Key declarations:
- `gs_type1_glyph_info`
- `gs_type1_piece_codes`

Dependencies:
- Includes `gstype1.h` for the charstring interpreter proc and `gxfixed.h` for fixed widths.

Research notes:
- Type 1 and CFF Type 2 share this data structure because their runtime state is similar enough.
- `gs_type1_piece_codes` exists mainly for font copying of `seac` composite glyphs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont42.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont42.h

Defines Type 42 TrueType font internal data structures and public helpers.

Key definitions:
- `gs_type42_mtx_t` describes hmtx/vmtx table count, offset, and length.
- `gs_type42_data` stores client-provided string access/proc data, initialized glyph index/outline/metrics callbacks, cached table offsets, unitsPerEm, indexToLocFormat, metrics tables, glyph counts, loca-derived lengths, glyph cache, and warning flags.
- `gs_font_type42_common` extends base font fields with Type 42 data.
- `gs_font_type42` is the concrete Type 42 font object.
- Declares GC metadata for Type 42 fonts.

Key declarations:
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

Dependencies:
- Forward-declares glyph cache and cached font/matrix pair types.
- Uses base font structures from `gxfont.h`.

Research notes:
- The file documents a historical mismatch between `numGlyphs` from `loca` and `trueNumGlyphs` from `maxp`, preserving both for compatibility.
- Type 42 code is a major dependency of font copying and CIDFontType 2 handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont42.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfrac.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfrac.h

Defines Ghostscript’s compact fractional color/value representation.

Key definitions:
- `frac` and `signed_frac` are signed shorts.
- Uses 15 effective bits with endpoint `frac_1 == 0x7ff8`.
- Chooses a range that exactly represents many common fractions better than a full signed-short range.
- Provides conversions between fracs and floats, bytes, arbitrary bit widths, unsigned shorts, and products/quotients by `frac_1`.
- Defines `frac_1_quo` and `frac_1_rem` helpers for scaled integer math.

Dependencies:
- Relies on architecture short-size macros.

Research notes:
- This representation is used in color transfer maps and raster color math.
- The non-maximal endpoint value is intentional to reduce common rounding errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfrac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxftype.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxftype.h

Defines Ghostscript font-type and bitmap-behavior enums.

Key definitions:
- `font_type` values mirror PostScript/PDF FontType and CIDFontType dictionary values.
- Includes composite, Type 1, Type 2, user-defined, disk-based, CIDFontType 0/1/2/4, Chameleon, and TrueType Type 42.
- `fbit_type` defines bitmap behavior for ExactSize, InBetweenSize, and TransformedChar: use outlines, use bitmaps, or transform bitmaps.

Dependencies:
- None beyond base typedef/macros.

Research notes:
- These enum values are ABI-significant because they must match font dictionary values.
- Used throughout font allocation, copying, rendering, and interpretation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxftype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfunc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfunc.h

Declares internal support for Ghostscript Function objects.

Key definitions:
- Declares abstract GC structure type `st_function`.
- `public_st_function` defines GC traversal over generic function `Domain` and `Range` arrays.

Key declarations:
- `fn_common_free_params`
- `fn_common_free`
- `fn_check_mnDR`
- `gs_function_get_info_default`
- `fn_common_get_params`
- `fn_copy_values`
- `fn_scale_pairs`
- `fn_common_scale`
- `fn_common_serialize`

Dependencies:
- Includes public function API `gsfunc.h` and GC struct helpers `gsstruct.h`.

Research notes:
- Provides shared implementation helpers for concrete PostScript/PDF function types.
- Handles validation, parameter copying/scaling, serialization, and common cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfunc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxgetbit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxgetbit.h

Defines the parameter interface and helpers for the `get_bits_rectangle` device procedure.

Key definitions:
- `gs_get_bits_options_t` aliases `gx_bitmap_format_t`.
- `gs_get_bits_params_t` carries accepted/chosen format options, up to 32 data plane pointers, returned X offset, and raster.
- Documents that devices update `options` with the actual chosen format, one option per group.
- Documents that `options == 0` is a capability query and should return supported options with an error.

Key declarations:
- `gx_get_bits_return_pointer` tries to implement `get_bits_rectangle` by returning a pointer into stored device data.
- `gx_get_bits_copy` implements `get_bits_rectangle` by copying from stored device data.

Dependencies:
- Includes `gxbitfmt.h`.
- Uses `gx_device` and byte/raster types from Ghostscript core headers.

Research notes:
- This header isolates bitmap retrieval option details so most device users do not need recompilation when options change.
- Default support assumes 8-bit depth, chunky packing, and copy return unless devices override more formats.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxgetbit.h -->