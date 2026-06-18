# Group Research: group_124_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gsovrc_h_sources_o_6352cf6a5612

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.h

Defines the Ghostscript overprint compositor interface. The extensive header comment documents how overprint/overprint mode interact with high-level devices, low-level rendering devices, forwarding devices, accumulating devices, transparency, pattern caches, and graphics-state lifetime.

Key structures:
- `gs_overprint_params_t`: holds retained/drawn component policy.
- `gs_overprint_t`: compositor object with `gs_composite_common` plus overprint parameters.

Public API:
- `gs_create_overprint(...)`: creates an overprint composite object.
- `gs_is_overprint_compositor(...)`: identifies overprint compositors.
- GC descriptors for overprint params/compositor.

Notable detail: `gs_overprint_clear_drawn_comp(drawn_comps, i)` clears `1 << 1` rather than `1 << i`, which looks suspicious and should be checked before relying on the macro.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspaint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspaint.c

Implements core Ghostscript painting operations: erase page, fill page, fill/eofill, stroke, and strokepath. It bridges graphics-state color/path state to device-level fill and stroke routines.

Main behavior:
- `gs_erasepage` saves state, sets gray to white, fills the full page, then restores state.
- `gs_fillpage` bypasses clipping and fills the whole device using high-level color if available, otherwise `gx_fill_rectangle`.
- `fill_with_rule`, `gs_fill`, and `gs_eofill` render current paths with winding or even/odd fill rules.
- `gs_stroke` handles charpath merging, null devices, alpha buffering, dash scaling, flatness scaling, and stroke-to-fill conversion when antialias buffering is needed.
- `gs_strokepath` replaces the current path with its stroked outline.

Important internals:
- Alpha-buffer setup scales path and clipping state with `scale_paths`.
- Dash patterns are scaled for antialias buffers and restored afterward.
- Null-device special cases avoid unnecessary color loading.

Dependencies are graphics state, path, clipping path, device color, memory devices, and low-level paint routines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspaint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspaint.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspaint.h

Declares the public painting procedures implemented by `gspaint.c`.

Exports:
- `gs_erasepage`
- `gs_fillpage`
- `gs_fill`
- `gs_eofill`
- `gs_stroke`
- `gs_imagepath`

It requires `gsstate.h` context for `gs_state`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspaint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.c

Implements generic support for Ghostscript parameter lists: typed values, value coercion, default scalar/array readers and writers, item-transfer helpers, and default request behavior.

Main behavior:
- Provides GC enumeration/relocation for `gs_param_typed_value`.
- Initializes `gs_param_list` common fields.
- Implements `gs_param_read_items` and `gs_param_write_items` for table-driven structure transfer.
- Implements `param_coerce_typed`, including int/long/float coercions, string/name interchange, and int-array to float-array conversion when memory is available.
- Provides fixed-type read/write wrappers for null, bool, int, long, float, strings, names, and arrays.

Notable detail:
- Missing params convention follows `1` for absent, `0` for present, negative for error.
- `param_read_name` requests `gs_param_type_string` while returning through the name union field; string/name share representation, but this is worth remembering when tracing type behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.h

Defines the client-facing parameter dictionary API used by Ghostscript objects and devices.

Key definitions:
- `gs_param_list`, `gs_param_name`, `gs_param_type`.
- Scalar, homogeneous collection, and heterogeneous collection value representations.
- `gs_param_value` union and `gs_param_typed_value`.
- Collection mode enum for normal dictionaries, integer-key dictionaries, and arrays.
- `gs_param_enumerator_t` and `gs_param_key_t`.
- `gs_param_list_procs`, the polymorphic operation table for typed transmission, collection begin/end, enumeration, request tracking, policies, error signaling, and commit.

Important design contract:
- The header documents two-phase commit requirements for device `put_params`: validate/signals first, call superclass/default handler, then install or roll back state.

Also declares:
- Typed read/write helpers.
- Table-driven item transfer API.
- `gs_c_param_list`, the concrete C parameter-list implementation with optional forwarding target.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam2.c

Implements a stream-oriented serializer/unserializer for `gs_param_list`, described as a redesigned future interface in `gsparams.h`.

Main behavior:
- `gs_param_list_puts` enumerates keys from a READ-mode list and writes compressed key lengths, types, keys, values, arrays, string arrays, and nested collections to a `stream`.
- `gs_param_list_gets` reads that stream format into a WRITE-mode parameter list, allocating aggregate data with the provided memory allocator.
- `sput_word`/`sget_word` encode variable-length 7-bit chunks.
- `sput_bytes`/`sget_bytes` bridge to Ghostscript stream byte APIs.

Important caveat:
- `gsparams.h` has this interface inside the disabled `#if 0` branch, so this file may not be part of the active build path.
- The local `sget_bytes` function has an apparent stray `};` before `return 0`, which would be syntactically invalid if compiled as shown.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.c

Implements the active buffer-based serializer/expander for Ghostscript parameter lists.

Main behavior:
- `gs_param_list_serialize` walks a READ-mode parameter list, writes compressed key lengths, types, C-string keys, value headers, aligned aggregate data, and recursively serialized dictionaries.
- `gs_param_list_unserialize` expands the buffer into a WRITE-mode parameter list, reconstructing pointers into the serialized buffer where possible.
- Uses `WriteBuffer` to count required bytes even when the destination buffer is null or too small.
- Aligns aggregate payloads for element size or pointer-size requirements.

Important properties:
- The format is memory-layout-oriented and not portable across architectures with different type sizes/endianness/alignment.
- Designed so expanded values can point directly into the serialized input buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.h

Declares serialization APIs for `gs_param_list`.

Active interface:
- `gs_param_list_serialize(gs_param_list *, byte *, int)`
- `gs_param_list_unserialize(gs_param_list *, const byte *)`

Disabled future interface:
- Stream-based `gs_param_list_puts`
- Stream-based `gs_param_list_gets`

The header currently selects the buffer serializer implemented in `gsparams.c`, while preserving declarations for the stream design behind `#if 0`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.c

Implements extended parameter-list utilities.

Main behavior:
- `gs_param_string_eq` compares `gs_param_string` with a C string.
- `param_put_enum` reads a name and maps it through a null-terminated enum-name table.
- `param_put_bool`, `param_put_int`, and `param_put_long` read typed values while accumulating and signaling errors.
- `param_list_copy` recursively copies one parameter list to another, including nested collections.

Important details:
- Preserves key persistence state while copying.
- Treats aggregate persistence carefully depending on whether source and destination use the same allocator.
- Handles dictionaries, integer-key dictionaries, and arrays recursively.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.h

Declares extended parameter dictionary helpers from `gsparamx.c`.

Exports:
- `gs_param_string_eq`
- `param_put_enum`
- `param_put_bool`
- `param_put_int`
- `param_put_long`
- `param_list_copy`

The helpers are convenience wrappers around `gs_param_list` operations, especially for device-style parameter ingestion with accumulated error handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparamx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.c

Implements basic Ghostscript path construction and clipping routines.

Main behavior:
- Path lifecycle: `gs_newpath`, `gs_closepath`, `gs_upmergepath`, `gx_current_path`.
- Point/line/curve construction: `gs_moveto`, `gs_rmoveto`, `gs_lineto`, `gs_rlineto`, `gs_curveto`, `gs_rcurveto`.
- Coordinate transformation from user space through CTM into fixed device coordinates.
- Coordinate clamping/limit checking through `clamp_point_aux`.
- Current point tracking and subpath start tracking.
- Clipping: `gx_effective_clip_path`, `gs_clippath`, `gs_initclip`, `gs_clip`, `gs_eoclip`, `gx_clip_to_rectangle`, `gx_clip_to_path`, `gx_default_clip_box`.

Important design:
- Effective clip path is cached by clip/view-clip IDs.
- View clipping is ignored for memory devices, primarily to support cache-device behavior.
- Default clipping box is derived from `ImagingBBox` if present, otherwise media size, hardware margins, and device initial matrix.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.h

Declares graphics-state path APIs.

Exports:
- Path constructors for move/line/curve/arc/closepath.
- Imager-level arc helpers.
- Path transformers/accessors: `gs_currentpoint`, `gs_upathbbox`, `gs_dashpath`, `gs_flattenpath`, `gs_reversepath`, `gs_strokepath`.
- Path enumeration allocation, initialization, iteration, and cleanup.
- Clipping operations: `gs_clippath`, `gs_initclip`, `gs_clip`, `gs_eoclip`.

Also defines `gs_pathbbox` as a wrapper around `gs_upathbbox(..., false)`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath1.c

Implements additional PostScript Level 1 path routines: arcs, arc tangents, path transformations, bounding boxes, and path enumeration.

Main behavior:
- `gs_arc`, `gs_arcn`, `gs_arc_add`, and `gs_imager_arc_add` approximate circular arcs with cubic Bezier curves.
- Optimizes exact quadrant arcs when CTM is scale/rotation-friendly.
- `gs_arcto` computes tangent points and adds an arc between two line segments.
- `make_quadrant_arc` computes four control points for quadrant arcs.
- `gs_dashpath`, `gs_flattenpath`, and `gs_reversepath` transform the current path.
- `gs_upathbbox` computes a user-space bounding box from the fixed device-space path.
- `gs_path_enum_copy_init`, `gs_path_enum_next`, and `gs_path_enum_cleanup` enumerate path elements back in user coordinates.

Important dependencies:
- Uses fixed-point geometry, CTM inverse transforms, path segment notes, dash expansion, curve flattening, and local path allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath2.h

Declares Level 2 graphics-state path procedures.

Exports:
- `gs_setbbox`
- `gs_rectappend`
- `gs_rectclip`
- `gs_rectfill`
- `gs_rectstroke`

This is a small interface header for rectangle and bounding-box operations implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspath2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.c

Implements generic Pattern color-space support for Ghostscript.

Main behavior:
- Defines `gs_color_space_type_Pattern`.
- Initializes generic pattern templates with `gs_pattern_common_init`.
- Dispatches generic `gs_make_pattern` to PatternType-specific constructors.
- `gs_make_pattern_common` allocates a pattern instance, copies/saves graphics state, concatenates the pattern matrix, clears the path, assigns a pattern id, and stores the instance in the client color.
- Frees pattern instances with saved graphics states.
- `gs_setpattern` and `gs_setpatternspace` install pattern color state.
- `gs_pattern_reference` adjusts pattern instance reference counts.
- `gs_get_pattern` returns the template for PaintProc use.

Pattern color-space methods:
- Number of components is negative for Pattern spaces.
- Base color space may be embedded for uncolored patterns.
- Remapping delegates to PatternType-specific `remap_color`.
- Overprint is deferred for patterns and handled at set-device-color/set-color time.
- Serialization writes pattern-space type plus optional base color space.

Notable caveat: comment notes base-space setting in `gs_setpatternspace` is wrong, reflecting known design debt.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.h

Defines the client interface and base structures for Ghostscript Pattern colors.

Key structures:
- `gs_pattern_template_t`: common Pattern template fields, including type, PatternType, uid, and client data.
- `gs_pattern_instance_t`: reference-counted instance with type, saved graphics state, and pattern id.

Exports:
- `gs_setpattern`
- `gs_setpatternspace`
- `gs_make_pattern`
- `gs_get_pattern`
- `gs_pattern_reference`

Also defines public GC descriptors for subclassing Pattern templates and instances.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspenum.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspenum.h

Defines common public path-enumeration constants.

Exports path element type values:
- `gs_pe_moveto`
- `gs_pe_lineto`
- `gs_pe_curveto`
- `gs_pe_closepath`

Also forward-declares the abstract `gs_path_enum` type.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspenum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspmdrv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspmdrv.c

Implements the OS/2 Presentation Manager display driver helper program for Ghostscript.

Main responsibilities:
- Runs as `gspmdrv -d id_string` to display a bitmap produced by Ghostscript through shared memory and semaphores.
- Runs as `gspmdrv -b filename.bmp` to display a BMP file for testing.
- Creates an OS/2 PM frame/client window, message queue, update thread, scroll bars, palette support, and system-menu additions.
- Reads and writes window position/size/maximized state to the OS/2 user profile.
- Uses named shared memory for bitmap data, named event semaphore for update notification, and named mutex semaphore for bitmap synchronization.
- Scans old `BITMAPINFO` and newer `BITMAPINFOHEADER2` layouts.
- Handles palette-manager setup for 8-bit bitmaps.
- Paints bitmap regions via `GpiDrawBits`, with fallback/double-buffer paths for known OS/2 display-driver bugs.
- Supports clipboard copy as `CF_BITMAP`.
- Handles scrolling, resizing, keyboard navigation, repaint, palette realization, and an About dialog.

Filesystem relevance is indirect: this is a platform UI/display helper within the vendored Ghostscript source tree, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspmdrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspmdrv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspmdrv.h

Defines resource IDs and version string shared by the OS/2 PM driver C source and resource file.

Exports:
- `GSPMDRV_VERSION`
- `IDM_ABOUT`
- `IDM_COPY`
- `IDD_ABOUT`
- `ID_GSPMDRV`
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gspmdrv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.c

Implements PatternType 1, the tiling-pattern implementation.

Main behavior:
- Defines PatternType 1 template/instance GC descriptors and type dispatch table.
- `gs_cspace_build_Pattern1` constructs Pattern color spaces with optional base spaces.
- `gs_pattern1_init` initializes PatternType 1 templates.
- `gs_makepattern`/`gs_pattern1_make_pattern` instantiate tiling patterns, save graphics state, compute tile stepping geometry, clip the tile, assign IDs, and account for colored versus uncolored PaintType behavior.
- `compute_inst_matrix` derives the stepping matrix and transformed bounding box.
- `clamp_pattern_bbox` limits huge pattern bounding boxes to the region that can actually affect the current page.
- `gs_pattern1_set_color` updates overprint behavior at set-color time; colored patterns conservatively mark all components as drawn.
- Implements bitmap/pixmap-derived pattern helpers used primarily by PCL.
- Defines device color types for colored patterns and masked uncolored variants: pure, binary halftone, and colored halftone.
- Implements pattern cache lookup and load methods.
- Pattern device colors cannot currently be serialized through the command list; write/read return errors.

Notable observations:
- `gs_cspace_build_Pattern1` appears to test `gs_color_space_num_components(pcspace)` while `pcspace` is still null; likely intended `pbase_cspace`.
- Pattern cache lookup accounts for internal pattern streams and dummy tiles.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.h

Defines the client interface for PatternType 1 tiling patterns.

Key structure:
- `gs_pattern1_template_t`, extending common pattern fields with `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, and `PaintProc`.

Exports:
- `gs_cspace_build_Pattern1`
- `gs_pattern1_init`
- `gs_makepattern`
- `gs_getpattern`
- `gs_makepixmappattern`
- `gs_makebitmappattern_xform`
- Backward-compatible aliases/macros for older client pattern API.

Documents mask versus colored pixmap conventions, indexed-color requirements, white-index transparency handling, and raw image-data lifetime expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.c

Implements PatternType 2 shading patterns.

Main behavior:
- Defines PatternType 2 template/instance GC descriptors and type dispatch table.
- `gs_pattern2_init` initializes templates.
- `gs_pattern2_make_pattern` uses common pattern allocation, stores the shading template, and initializes `shfill` state.
- `gs_pattern2_set_shfill` marks instances used by `shfill`.
- `gs_pattern2_remap_color` creates a PatternType 2 device color without concrete color mapping.
- `gs_pattern2_set_color` updates overprint using the shading color space while temporarily disabling overprint mode.
- `gx_dc_pattern2_fill_path` and rectangle fill path render through `gs_shading_fill_path_adjusted`.
- Provides equality, halftone lookup, save-device-color support, bbox transform/get helpers, overlap detection for shading types 3/6/7, and background detection.

PatternType 2 colors are not cache-loaded like Type 1; load is a no-op and drawing delegates to the shading renderer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.h

Defines the client interface for PatternType 2 shading patterns.

Key structures:
- `gs_pattern2_template_t`: common pattern fields plus `const gs_shading_t *Shading`.
- `gs_pattern2_instance_t`: common instance fields, embedded template, and `shfill` flag.

Exports:
- `gx_dc_pattern2`
- `gs_pattern2_init`
- `gx_dc_is_pattern2_color`
- `gx_dc_pattern2_fill_path`
- `gs_pattern2_set_shfill`
- `gx_dc_pattern2_shade_bbox_transform2fixed`
- `gx_dc_pattern2_get_bbox`
- `gx_dc_pattern2_can_overlap`
- `gx_dc_pattern2_has_background`

The header notes that a PatternType 2 color-space builder is not provided.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrect.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrect.h

Defines rectangle utility macros and declares integer-rectangle difference.

Exports:
- `rect_within`
- `rect_intersect`
- `rect_merge`
- `int_rect_difference`
- `PARALLELOGRAM_IS_RECT`
- `INT_RECT_FROM_PARALLELOGRAM`

The macros operate on rectangle structs with `p` and `q` corners and are used by clipping/painting geometry code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrefct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrefct.h

Defines Ghostscript’s reference-counting support macros and `rc_header`.

Key concepts:
- Reference-counted objects embed `rc_header rc`.
- `rc_header` stores count, allocator, and free procedure.
- Allocation macros initialize refcounts at 0 or 1.
- Increment/decrement/adjust macros handle zero-count free behavior.
- Assignment macros increment the new value before decrementing the old value to avoid premature free.

Important APIs/macros:
- `rc_free_struct_only`
- `rc_init`, `rc_init_free`
- `rc_alloc_struct_0`, `rc_alloc_struct_1`
- `rc_increment`, `rc_decrement`
- `rc_adjust`, `rc_adjust_only`
- `rc_assign`, `rc_pre_assign`
- Debug tracing hooks under `DEBUG`.

The header warns about interaction between reference counting and finalization: finalizing free procs must free the containing object before decrementing referenced objects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrefct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrop.c

Implements public RasterOp and transparency accessors for the graphics state.

Main behavior:
- `gs_setrasterop` updates the raster-op bits of `pgs->log_op`.
- `gs_currentrasterop` extracts the current RasterOp.
- `gs_setsourcetransparent` and `gs_settexturetransparent` toggle source/texture transparency bits.
- `gs_currentsourcetransparent` and `gs_currenttexturetransparent` read those bits.
- `gs_set_logical_op` and `gs_current_logical_op` set/get the entire combined logical operation for internal save/restore.

All setters reject changes while in `cachedevice`, returning `undefined`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrop.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrop.h

Declares RasterOp/transparency procedure interface.

Exports:
- `gs_setrasterop`
- `gs_currentrasterop`
- `gs_setsourcetransparent`
- `gs_currentsourcetransparent`
- `gs_settexturetransparent`
- `gs_currenttexturetransparent`
- `gs_current_logical_op`
- `gs_set_logical_op`

Depends on `gsropt.h` for RasterOp/logical-operation types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrop.h -->