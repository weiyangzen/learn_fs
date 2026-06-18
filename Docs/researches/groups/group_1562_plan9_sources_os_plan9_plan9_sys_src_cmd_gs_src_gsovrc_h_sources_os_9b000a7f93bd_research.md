# Group Research: group_1562_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gsovrc_h_sources_os_9b000a7f93bd

Scope: `Docs/research_subset_a.md`. All listed source files were read completely. This report is organized for splitter consumption with one marked block per source file.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.h

Defines the public/internal interface for Ghostscript’s overprint compositor. The long file comment explains when overprint compositing is relevant for high-level devices, low-level devices, forwarding devices, accumulating devices, transparency devices, and pattern rendering.

Key definitions:
- `gs_overprint_params_t` / `struct gs_overprint_params_s`: tracks whether retained components exist, whether spot components are retained, and `drawn_comps` bitmask.
- `gs_overprint_t`: compositor object containing `gs_composite_common` plus overprint parameters.
- Structure descriptors: `private_st_gs_overprint_t`, `public_st_overprint_params_t`.
- Public functions: `gs_create_overprint`, `gs_is_overprint_compositor`.

Integration:
- Includes `gsstype.h` and `gxcomp.h`.
- Used by pattern/color state code to update overprint behavior, notably Type 1/2 pattern set-color paths.
- The compositor is intended to wrap and follow the lifetime/open-close state of the underlying device.

Risk notes:
- `gs_overprint_clear_drawn_comp(drawn_comps, i)` clears `1 << 1` rather than `1 << i`; this looks like a historical typo with component-mask consequences.
- The model depends on device process-color mappings and assumes compositor installation/removal discipline elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.c

Implements Ghostscript library painting operations: erase page, fill page, path fill, even-odd fill, stroke, and strokepath.

Key functions:
- `gs_erasepage`: saves state, sets gray to white, calls `gs_fillpage`, restores state.
- `gs_fillpage`: fills the full device using high-level color if available, otherwise `gx_fill_rectangle`, temporarily resetting RasterOp.
- `alpha_buffer_bits`, `alpha_buffer_init`, `alpha_buffer_release`: anti-alias buffer setup for fill/stroke paths.
- `scale_paths`, `scale_dash_pattern`: adjust current path, clipping paths, view clip, effective clip, and dash parameters for alpha-buffer supersampling.
- `fill_with_rule`, `gs_fill`, `gs_eofill`: load device color, optionally alpha-buffer, call `gx_fill_path`, then `gs_newpath`.
- `gs_stroke`: handles charpath merging, null-device fast path, alpha-buffered stroke conversion, or direct `gx_stroke_fill`.
- `gs_strokepath`: replaces current path with stroked outline via `gx_stroke_add`.

Integration:
- Uses path, clipping, device, high-level color, memory-device, and graphics-state internals (`gzstate.h`, `gzpath.h`, `gzcpath.h`, `gxpaint.h`, `gxdevmem.h`).
- Alpha buffering relies on device `get_alpha_bits` and memory alpha-buffer devices.

Risk notes:
- Alpha-buffer scaling must preserve aliasing among `path`, `clip_path`, `view_clip`, and `effective_clip_path`; errors here can corrupt clipping.
- Stroke alpha-buffer path temporarily mutates line width, dash pattern, and flatness and must restore them exactly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.h

Declares the public painting API for Ghostscript graphics state users.

Exports:
- `gs_erasepage`
- `gs_fillpage`
- `gs_fill`
- `gs_eofill`
- `gs_stroke`
- `gs_imagepath`

Integration:
- Requires `gsstate.h` types to be visible before inclusion.
- Implemented mainly in `gspaint.c`; `gs_imagepath` is declared here but implemented elsewhere.

Risk notes:
- This is a thin API header with no ownership logic; correctness depends on caller-supplied valid `gs_state *`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.c

Implements core parameter-list helpers for Ghostscript’s typed key/value parameter dictionaries.

Key functions:
- GC relocation/enumeration for `gs_param_typed_value`.
- `gs_param_list_init`: initializes common list procedure table, allocator, and persistent-key default.
- `gs_param_list_set_persistent_keys`: toggles key lifetime contract.
- `param_init_enumerator`: zeroes enumerator state.
- `gs_param_read_items` / `gs_param_write_items`: transfer structured fields based on `gs_param_item_t` descriptors.
- `param_coerce_typed`: supports selected coercions among int/long/float, string/name, string/name arrays, int array to float array, and empty array to typed arrays.
- `param_read_requested_typed`, fixed-type readers, and fixed-type writers.
- Defaults: `gs_param_request_default`, `gs_param_requested_default`.

Integration:
- Implements interfaces declared in `gsparam.h`.
- Used broadly by device `get_params` / `put_params` and incremental parameter list construction.

Risk notes:
- `param_coerce_typed`’s int-to-float case assigns from `value.l` after actual type `int`; this looks suspicious because `value.l` may not be initialized as a long.
- `param_read_name` requests `gs_param_type_string` while returning union member `n`; this may be deliberate compatibility or a typo.
- Error accumulation in item reads/writes keeps scanning after failures, matching device parameter policy but requiring callers to inspect final code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.h

Defines Ghostscript’s generic parameter dictionary abstraction.

Key definitions:
- `gs_param_type`: scalar, homogeneous collection, and heterogeneous collection type IDs.
- Homogeneous array/string structs: `gs_param_int_array`, `gs_param_float_array`, `gs_param_string_array`.
- `gs_param_collection`, `gs_param_dict`, `gs_param_array`.
- `gs_param_value`, `gs_param_typed_value`, and GC procedures for typed values.
- `gs_param_collection_type_t`: general dict, int-key dict, or array.
- `gs_param_list_procs`: virtual table for typed transmission, begin/end collection, key enumeration, requests, policies, error signaling, and commit.
- Helper macros for reading/writing, begin/end dict, request/query, policy, signal, and commit.
- `gs_param_list` common base with proc table, allocator, and persistent-key flag.
- `gs_param_item_t` descriptor-based transfer API.
- `gs_c_param_list`: C-side default/incremental parameter list with optional forwarding target.

Integration:
- Core contract for device parameter exchange and PostScript-like dictionaries.
- The header embeds detailed two-phase `put_params` policy guidance for device implementers.

Risk notes:
- The API deliberately reuses one procedure table for “reading” and “writing” from opposite client/device perspectives, which is powerful but easy to misuse.
- Persistent vs transient key/value ownership is central; callers must set flags consistently.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam2.c

Implements a stream-based serializer/deserializer for `gs_param_list`. The header file currently disables this interface behind `#if 0`, marking it as a future interface.

Key functions:
- `gs_param_list_puts`: serializes a read-mode list to a stream using variable-length words, key strings, type IDs, scalar bytes, arrays, string arrays, and recursive collections.
- `sput_word`, `sput_bytes`: write compressed integer and raw bytes to stream.
- `gs_param_list_gets`: deserializes from a stream into a write-mode list, allocating aggregate data as needed.
- `sget_word`, `sget_bytes`: read compressed integer and raw bytes from stream.

Integration:
- Includes `gsparams.h`, `stream` support indirectly, and parameter-list APIs.
- Intended replacement for the buffer serializer in `gsparams.c`.

Risk notes:
- Scalar serialization/deserialization uses intentional-looking fall-through from bool/int/long/float into null handling; this is fragile and comment-free.
- `gs_param_list_gets` indexes `gs_param_type_sizes[type]` before validating `type`.
- The `sget_bytes` function contains an apparent stray `};` before `return 0`, which would be a compile risk if this disabled future interface were enabled.
- String/name array deserialization allocates element strings but the visible code does not assign `sa->data` after reading each string, suggesting incomplete or stale implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparam2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.c

Implements the active buffer-based serializer and expander for parameter lists.

Key functions:
- `gs_param_list_serialize`: writes a parameter list into an aligned byte buffer, returning the required size even when the buffer is null or too small.
- `gs_param_list_unserialize`: expands a buffer back into a write-mode parameter list.
- `ptr_align_to`, `wb_put_alignment`: alignment helpers for direct buffer references.
- `wb_put_word`, `buf_get_word`: variable-length integer encoding/decoding.
- `wb_put_bytes`: size-counting and bounded copy helper.

Serialization model:
- Each entry stores compressed key length, type, null-terminated key, then type-specific payload.
- Scalar and homogeneous structs are stored as memory images.
- Aggregate payloads are aligned so the unserialized list can point into the source buffer.
- Dictionaries recurse and write an end marker.

Integration:
- Public interface declared in `gsparams.h`.
- Used where compact in-memory parameter-list transport is required.

Risk notes:
- This format is architecture-sensitive because it stores unpacked C memory images for numeric/scalar structures.
- `gs_param_list_unserialize` trusts source buffer structure and type IDs; malformed buffers can walk memory.
- String array unserialization mutates string descriptors in the input buffer by assigning `sa->data` and `persistent`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.h

Declares parameter-list serialization APIs.

Key behavior:
- Includes `stream.h` and `gsparam.h`.
- Contains a disabled future stream interface (`gs_param_list_puts`, `gs_param_list_gets`) implemented in `gsparam2.c`.
- Exposes the active buffer interface:
  - `gs_param_list_serialize`
  - `gs_param_list_unserialize`

Integration:
- The active path maps to `gsparams.c`.
- The stream path is present but disabled with `#if 0`.

Risk notes:
- Consumers using the active interface must provide a void-pointer-aligned buffer for unserialization.
- Header comments make clear that success for serialization requires returned size to be positive and not exceed supplied buffer size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.c

Provides extended utilities for parameter dictionaries.

Key functions:
- `gs_param_string_eq`: compares `gs_param_string` to a C string by size and bytes.
- `param_put_enum`: reads a name parameter, matches against a null-terminated name table, stores enum index, and signals range/type errors.
- `param_put_bool`, `param_put_int`, `param_put_long`: convenience readers that propagate prior accumulated error code.
- `param_list_copy`: recursively copies all keys and values from one parameter list to another, including dictionaries/arrays.

Integration:
- Uses `gsparam.h` APIs and `gsparamx.h` declarations.
- Useful for device `put_params` implementations that collect multiple parameter validation errors.

Risk notes:
- `param_list_copy` uses fixed `char string_key[256]`; longer keys return rangecheck.
- `copy_persists` is set from allocator equality; the name suggests the condition may deserve careful review because persistence is modified based on allocator relationship.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.h

Declares extended parameter dictionary utilities.

Exports:
- `gs_param_string_eq`
- `param_put_enum`
- `param_put_bool`
- `param_put_int`
- `param_put_long`
- `param_list_copy`

Integration:
- Requires parameter-list types from `gsparam.h` to be visible.
- Designed as convenience support for robust `put_params` parsing and list duplication.

Risk notes:
- Thin declarations only; error accumulation semantics are defined by implementations in `gsparamx.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparamx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.c

Implements basic Ghostscript path construction, current point handling, clipping, and default clip box computation.

Key functions:
- `gs_newpath`, `gs_closepath`, `gs_upmergepath`, `gx_current_path`.
- `gs_currentpoint`: inverse-transforms device current point to user space.
- `gs_moveto`, `gs_rmoveto`, `gs_lineto`, `gs_rlineto`, `gs_curveto`, `gs_rcurveto`.
- Internal transform compatibility and coordinate clamping helpers.
- `gx_effective_clip_path`: caches effective intersection of clip path and view clip path, with memory-device exception.
- `gs_clippath`, `gs_initclip`, `gs_clip`, `gs_eoclip`.
- `gx_clip_to_rectangle`, `gx_clip_to_path`, `gx_default_clip_box`.

Integration:
- Uses graphics state internals, fixed-point path API, matrix transforms, clipping path APIs, and device geometry.
- `gx_default_clip_box` respects `ImagingBBox` when set, otherwise derives from media size, hardware margins, and device initial matrix.

Risk notes:
- Relative path operators include comments noting range checks are still “fixme”.
- `gx_effective_clip_path` has complex ownership/shared-state handling; stale IDs or alias mistakes could leak or corrupt clipping.
- Coordinate clamping can mask extreme user-space inputs depending on `clamp_coordinates`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.h

Declares graphics-state path procedures.

Exports:
- Path constructors: newpath, move/line/curve, arc/arcn/arc_add/arcto, closepath.
- Imager-level arc support: `gs_imager_arc_add`, `make_quadrant_arc`.
- Path transforms/accessors: currentpoint, pathbbox/upathbbox, dashpath, flattenpath, reversepath, strokepath.
- Path enumeration: `gs_path_enum_alloc`, init/copy init, next, cleanup.
- Clipping: clippath, initclip, clip, eoclip.

Integration:
- Includes `gspenum.h`.
- Forward-declares `gs_imager_state`, `gx_path`, and `gs_matrix_fixed`.
- `gs_pathbbox` macro maps to `gs_upathbbox(..., false)`.

Risk notes:
- Function prototype ordering includes an old compiler workaround for bool argument placement in `gs_arc_add`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath1.c

Implements additional PostScript Level 1 path operations: arcs, arcto, path transformations, bounding boxes, and path enumeration.

Key functions:
- Arc support: `gs_arc`, `gs_arcn`, `gs_arc_add`, `gs_imager_arc_add`, `next_arc_curve`, `next_arc_quadrant`, `arc_add`.
- `gs_arcto`: computes tangent points and arc curve between two segments.
- `make_quadrant_arc`: computes Bezier control points for quadrant arcs.
- `gs_dashpath`: expands dash pattern into path.
- `gs_flattenpath`: converts curves to line segments.
- `gs_reversepath`: reverses subpath order and updates current/subpath start points.
- `gs_upathbbox`: returns path bbox in user coordinates.
- `gs_path_enum_copy_init`, `gs_path_enum_next`, `gs_path_enum_cleanup`.

Integration:
- Uses low-level `gx_path` operations and matrix transforms.
- Arc code transforms from user to fixed device coordinates and tags arc-generated curve segments.
- Path enumeration transforms fixed device points back into user space.

Risk notes:
- Arc approximation is numerically sensitive, with special fast paths for orthogonal quadrant arcs.
- `gs_arcto` handles collinearity by falling back to `lineto`.
- Enumeration may allocate a path copy, so cleanup is mandatory when `copy` is true.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath2.h

Declares Level 2 graphics-state path procedures.

Exports:
- `gs_setbbox`
- Rectangle operators: `gs_rectappend`, `gs_rectclip`, `gs_rectfill`, `gs_rectstroke`

Integration:
- Requires `gsmatrix.h` types and `gs_state`.
- Complements `gspath.h` with rectangle-oriented Level 2 operations implemented elsewhere.

Risk notes:
- Header only; rectangle count and matrix handling contracts are enforced by implementations outside this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.c

Implements generic Pattern color space support shared by PatternType 1 and 2.

Key functions and objects:
- GC descriptors for pattern templates/instances and Pattern color space.
- `gs_color_space_type_Pattern`: Pattern color space type vtable.
- `gs_pattern_common_init`: initializes pattern template common fields.
- `gs_make_pattern`: dispatches to pattern type’s `make_pattern`.
- `gs_make_pattern_common`: allocates pattern instance, copies graphics state, concatenates pattern matrix, clears path, assigns pattern ID.
- `rc_free_pattern_instance`: frees saved graphics state then instance.
- `gs_setpattern`, `gs_setpatternspace`.
- `gs_pattern_reference`, `gs_get_pattern`.
- Pattern color space procs: component count, base space, remap, init, restrict, install, overprint handling, refcount adjustment, serialization.

Integration:
- Includes color space, device color, path, image, stream, and state internals.
- Pattern color spaces may include a base paint color space for uncolored patterns.
- Pattern overprint setup is deferred to set-device-color for patterns.

Risk notes:
- Comment in `gs_setpatternspace` says base-space setting is wrong, indicating known design debt.
- `gx_adjust_color_Pattern` adjusts `pcc->pattern` without a null check in the visible code path.
- Pattern color spaces report negative component counts for backward compatibility, which downstream code must understand.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.h

Defines the client interface for Pattern colors.

Key definitions:
- `gs_pattern_type_t` forward declaration.
- `gs_pattern_template_common` and `gs_pattern_template_t`.
- Pattern template GC descriptor macros.
- `gs_pattern_instance_t` with `rc_header`, pattern type, saved graphics state, and pattern ID.
- Pattern instance GC descriptor macros.

Exports:
- `gs_setpattern`
- `gs_setpatternspace`
- `gs_make_pattern`
- `gs_get_pattern`
- `gs_pattern_reference`

Integration:
- Includes `gsccolor.h`, `gsrefct.h`, and `gsuid.h`.
- Provides common base for `gsptype1.h` and `gsptype2.h`.

Risk notes:
- Pattern instances are reference-counted and retain saved graphics state; clients holding colors outside the graphics state must call `gs_pattern_reference` correctly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspenum.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspenum.h

Defines common client-facing path enumeration symbols.

Key definitions:
- Path element IDs: `gs_pe_moveto`, `gs_pe_lineto`, `gs_pe_curveto`, `gs_pe_closepath`.
- Opaque `gs_path_enum` type.

Integration:
- Included by `gspath.h`.
- Used by path enumeration APIs implemented in `gspath1.c`.

Risk notes:
- Simple constant header; consumers must match the point-count contract for each path element type.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspenum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.c

Implements an OS/2 Presentation Manager display driver/helper for Ghostscript, despite residing in this Plan 9 source tree copy. It can display live shared-memory output from `gsos2.exe` or load a BMP file for display testing.

Key data:
- Global semaphores: `update_event_sem`, `bmp_mutex_sem`.
- `BMAP`: bitmap metadata, palette and old-state tracking.
- `DISPLAY`: display planes, bitcount, palette-manager state.
- `OPTIONS`: saved window origin/size/maximized state.
- Global OS/2 handles: anchor block, frame/client windows, source GS window, update thread.

Key functions:
- `main`: initializes PM, parses `-d id_string` or `-b filename.bmp`, starts update thread, creates window, enters message loop.
- `update_func`: waits on event semaphore and posts `WM_GSUPDATE`.
- `exit_func`: writes profile, closes semaphores, frees shared bitmap memory.
- `find_hwnd_gs`: finds originating CMD/GS window by process ID embedded in ID string.
- `init_window`, `fix_sysmenu`, `restore_window_position`, `read_profile`, `write_profile`.
- `init_display`: opens shared memory, event semaphore, and mutex by generated names.
- `init_bitmap`: loads BMP file into memory and points bitmap info into it.
- `scan_bitmap`: parses `BITMAPINFO`/`BITMAPINFO2`, palette size, dimensions, depth, and data pointer.
- `make_palette`, `make_bitmap`, `paint_bitmap`, `copy_clipboard`.
- `ClientWndProc`: handles paint/update, scrollbars, palette realization, move/size persistence, keyboard navigation, copy/about commands.
- `AboutDlgProc`: handles about dialog dismissal.

Integration:
- Uses OS/2 APIs (`Dos*`, `Win*`, `Gpi*`) plus `gdevpm.h` shared names.
- Synchronizes bitmap access with a mutex while GS may update shared memory.
- Handles OS/2 display-driver quirks with slow/fast bitmap painting paths.

Risk notes:
- Many fixed `char[256]` buffers and `sprintf`/`strcpy` calls predate modern bounds practices.
- `find_hwnd_gs` allocates switch-list memory with `malloc` and does not visibly free it.
- Error strings in `init_display` use `argv[0]`/`argv[1]` in places where generated semaphore/shared-memory names might be more useful.
- Platform-specific and unlikely to build outside OS/2 tooling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.h

Defines constants shared by the OS/2 Presentation Manager driver source and resource file.

Key definitions:
- `GSPMDRV_VERSION`
- Menu/dialog command IDs: `IDM_ABOUT`, `IDM_COPY`, `IDD_ABOUT`
- Resource ID: `ID_GSPMDRV`

Integration:
- Included by `gspmdrv.c` and referenced by the OS/2 resource script.

Risk notes:
- Header is platform/resource-specific and has no logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspmdrv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.c

Implements PatternType 1 tiling patterns, including pattern instance creation, bitmap/pixmap pattern helpers, device color types, and pattern cache lookup.

Key areas:
- Pattern type vtable: `gs_pattern1_type` with base-space, make, get, remap, and set-color procedures.
- `gs_cspace_build_Pattern1`: builds Pattern color space with optional base color space.
- `gs_pattern1_init`, `gs_makepattern`, `gs_pattern1_make_pattern`.
- `compute_inst_matrix`, `clamp_pattern_bbox`: compute step matrix, device bbox, tile size, and clamp huge pattern bboxes to page intersection.
- `gs_pattern1_set_color`: updates overprint behavior for colored vs uncolored patterns.
- `gs_getpattern`: returns Type 1 template from client color.
- Bitmap/pixmap pattern support:
  - bitmap structure descriptors
  - `pixmap_info`
  - `free_pixmap_pattern`
  - `mask_PaintProc`, `image_PaintProc`, `bitmap_paint`
  - `gs_makepixmappattern`
  - `gs_makebitmappattern_xform`
- Device color types:
  - `gx_dc_pattern`
  - `gx_dc_pure_masked`
  - `gx_dc_binary_masked`
  - `gx_dc_colored_masked`
- Pattern cache:
  - `gx_pattern_cache_lookup`
  - load procs for colored and masked patterns.
- Save/equality/nonzero-components/write/read support for device colors.

Integration:
- Depends on generic pattern support in `gspcolor.c`, overprint parameters in `gsovrc.h`, image machinery, color spaces, device color vtables, and pattern cache internals.
- Fill rectangle procedures are declared here but implemented via `gxp1fill.h` inclusion pattern elsewhere.
- Exported device color type is referenced by other pattern/color modules.

Risk notes:
- `gs_cspace_build_Pattern1` checks `gs_color_space_num_components(pcspace)` before `pcspace` is allocated; source context suggests this likely meant `pbase_cspace`.
- Pattern scaling has compatibility switches and Adobe/traditional adjustments, making rendering sensitive to small numeric changes.
- Command-list serialization of patterns intentionally returns `unknownerror`; vector devices get only minimal save support.
- Bitmap/pixmap pattern helpers do not own original bitmap data; client lifetime must exceed pattern use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.h

Defines the client interface for PatternType 1 tiling patterns.

Key definitions:
- `gs_pattern1_template_t`: common pattern template plus `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, and `PaintProc`.
- `gs_client_pattern` backward-compatible typedef.
- PatternType 1 GC descriptor macro.

Exports:
- `gs_cspace_build_Pattern1`
- `gs_pattern1_init`
- `gs_makepattern`
- `gs_getpattern`
- `gs_makepixmappattern`
- `gs_makebitmappattern_xform`
- `gs_makebitmappattern` compatibility macro.

Integration:
- Includes `gspcolor.h` and `gxbitmap.h`.
- Used by clients that create colored/uncolored tiling patterns or PCL-style bitmap/pixmap patterns.

Risk notes:
- Header comments make bitmap-data lifetime explicit: raw image data must outlive the pattern.
- Mask patterns require 1-bit depth; colored pixmap patterns require Indexed color space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.c

Implements PatternType 2 shading patterns.

Key functions and objects:
- GC descriptors for Type 2 template/instance.
- `gs_pattern2_type` vtable.
- `gs_pattern2_init`: initializes template.
- `gs_pattern2_make_pattern`: creates instance via generic pattern common helper and stores `Shading`.
- `gs_pattern2_get_pattern`.
- `gs_pattern2_set_shfill`: marks instance as direct `shfill`.
- Device color type `gx_dc_pattern2`.
- `gx_dc_is_pattern2_color`.
- `gx_dc_pattern2_get_dev_halftone`: returns halftone from saved state.
- `gx_dc_pattern2_load`: no-op.
- `gs_pattern2_remap_color`: sets device color as PatternType 2 without concrete mapping.
- `gs_pattern2_set_color`: updates overprint using shading color space while temporarily disabling overprint mode.
- `gx_dc_pattern2_fill_path` / fill rectangle: delegates to `gs_shading_fill_path_adjusted`.
- Equality/save helpers.
- BBox/overlap/background helpers: `gx_dc_pattern2_shade_bbox_transform2fixed`, `gx_dc_pattern2_get_bbox`, `gx_dc_pattern2_can_overlap`, `gx_dc_pattern2_has_background`.

Integration:
- Depends on shading (`gsshade.h`), generic pattern color, device color, graphics state, and path internals.
- Shares pattern command-list write/read stubs with Type 1 (`gx_dc_pattern_write`, `gx_dc_pattern_read`).

Risk notes:
- PatternType 2 does not use a base space; shading’s own color space controls color/overprint.
- Direct fill delegates to shading code and uses saved imager state from pattern creation time.
- Self-overlap detection is type-number based for shading types 3, 6, and 7.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.h

Defines the client/internal interface for PatternType 2 shading patterns.

Key definitions:
- `gs_shading_t` forward declaration.
- `gs_pattern2_template_t`: pattern common fields plus `const gs_shading_t *Shading`.
- `gs_pattern2_instance_t`: pattern instance common fields, copied template, and `shfill` flag.
- GC descriptor macros for template and instance.
- Public device color type: `gx_dc_pattern2`, `gx_dc_type_pattern2`.

Exports:
- `gs_pattern2_init`
- `gx_dc_is_pattern2_color`
- `gx_dc_pattern2_fill_path`
- `gs_pattern2_set_shfill`
- `gx_dc_pattern2_shade_bbox_transform2fixed`
- `gx_dc_pattern2_get_bbox`
- `gx_dc_pattern2_can_overlap`
- `gx_dc_pattern2_has_background`

Integration:
- Includes `gspcolor.h`, `gsdcolor.h`, and `gxfixed.h`.
- Used by shading fill and pattern device-color handling.

Risk notes:
- Header notes that there is no `gs_cspace_build_Pattern2` helper even though it “should” exist.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrect.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrect.h

Provides rectangle utility macros and one rectangle-difference declaration.

Key definitions:
- `rect_within`: tests containment.
- `rect_intersect`: in-place rectangle intersection, possibly anomalous if empty.
- `rect_merge`: in-place rectangle union/merge.
- `int_rect_difference`: computes outer-minus-inner into up to four rectangles.
- `PARALLELOGRAM_IS_RECT`: tests whether a parallelogram is axis-aligned rectangle.
- `INT_RECT_FROM_PARALLELOGRAM`: converts a rectangular parallelogram to integer rectangle using center-of-pixel rounding.

Integration:
- Includes `gxfixed.h`.
- Used by clipping, fill, and device geometry code.

Risk notes:
- Macros evaluate arguments multiple times and mutate targets; callers must avoid side-effect expressions.
- Empty/anomalous rectangle behavior is explicit and must be handled by callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrefct.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrefct.h

Defines Ghostscript’s manual reference-counting helper macros.

Key definitions:
- `rc_header`: `ref_count`, owning `gs_memory_t *`, and free procedure.
- `rc_free_proc` signature macro.
- Debug trace hooks for init/free/increment/adjust.
- Initialization/allocation macros: `rc_init_free`, `rc_init`, `rc_alloc_struct_0`, `rc_alloc_struct_1`.
- Free macro: `rc_free_struct`.
- Count adjustment macros: `rc_increment`, `rc_allocate_struct`, `rc_unshare_struct`, `rc_adjust`, `rc_adjust_only`, `rc_decrement`, `rc_decrement_only`.
- Assignment helpers: `rc_assign`, `rc_pre_assign`.

Integration:
- Used by pattern instances in `gspcolor.h`/`gspcolor.c` and other shared objects.
- Relies on Ghostscript memory allocator and structure descriptors.

Risk notes:
- Macros mutate pointer arguments and can free objects; caller ordering matters.
- `rc_assign` increments source before decrementing destination to handle alias/last-reference cases.
- No thread-safety is provided.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrefct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.c

Implements RasterOp and transparency state accessors for Ghostscript graphics state.

Key functions:
- `gs_setrasterop`: updates RasterOp bits in `pgs->log_op`, rejected inside cachedevice.
- `gs_currentrasterop`: extracts current ROP3 value.
- `gs_setsourcetransparent` / `gs_currentsourcetransparent`.
- `gs_settexturetransparent` / `gs_currenttexturetransparent`.
- `gs_set_logical_op` / `gs_current_logical_op`: internal save/restore of combined logical operation.

Integration:
- Uses `gzstate.h` graphics-state internals and `gsropt.h` bit definitions via `gsrop.h`.
- `gspaint.c` temporarily resets logical op for full-page fill.

Risk notes:
- Mutating RasterOp/transparency is disallowed during cachedevice, returning `undefined`.
- `gs_set_logical_op` is unrestricted internal API and can overwrite all logical-op bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.h

Declares RasterOp and transparency procedures.

Exports:
- `gs_setrasterop`
- `gs_currentrasterop`
- `gs_setsourcetransparent`
- `gs_currentsourcetransparent`
- `gs_settexturetransparent`
- `gs_currenttexturetransparent`
- `gs_current_logical_op`
- `gs_set_logical_op`

Integration:
- Includes `gsropt.h` for `gs_rop3_t` and `gs_logical_operation_t`.
- Implemented by `gsrop.c`.

Risk notes:
- Thin header; semantics depend on `gsrop.c` and graphics-state invariants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrop.h -->