# Group Research: group_1572_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxpageq_h_sources_o_af4ec57310f5

This group covers Ghostscript graphics-library internals under the Plan 9 source tree. The files are not filesystem implementations; they define page-queue coordination, fixed-point path construction and transformation, pattern caching, sample unpacking, RasterOp/plane helpers, and shading renderers.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpageq.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpageq.h

`gxpageq.h` declares Ghostscript's page queue interface for coordinating interpreter-produced command-list pages with renderer threads. It depends on `gsmemory.h`, `gxband.h`, and `gxsync.h`.

The central type is `gx_page_queue_action_t`, which encodes `PARTIAL_PAGE`, `FULL_PAGE`, `COPY_PAGE`, and `TERMINATE`. The long header comment is the key contract: page descriptions may be split into partial entries, copied pages must preserve rendered state for PostScript `copypage`, full pages complete or cancel page sequences, and terminate entries end rendering after prior required output.

The file forward-declares `gx_page_queue_t` and defines `gx_page_queue_entry_t`, which stores `gx_band_page_info_t page_info`, action, copy count, and queue/next links. `private_st_gx_page_queue_entry()` supplies GC metadata for `next` and `queue`.

Public operations allocate queues and entries, initialize/destroy queues, free page-info resources separately from entry objects, enqueue pages, add pages using a reserve entry under memory pressure, block until one/all pages finish rendering, and dequeue/finish entries. The implementation lives elsewhere, but this header defines the threading and ownership protocol. A notable risk is that callers must explicitly call `gx_page_queue_entry_free_page_info` before freeing entries unless `gx_page_queue_finish_dequeue` is used; otherwise command-list memory leaks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpageq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.c

`gxpaint.c` implements graphics-state-aware fill/stroke wrappers. It includes state, device, halftone tile, path, paint, and font headers.

The helper `caching_an_outline_font` detects when the graphics state is inside cache-device processing for non-user-defined outline fonts. In that case fill/stroke flattening uses flatness `0.0`, which preserves better outline fidelity for cached glyphs.

`gx_fill_path` obtains the current device, resolves the effective clip path, builds `gx_fill_params`, and dispatches the device `fill_path` procedure. It passes the fill rule, pixel adjustment values, flatness, and whether zero-width/height rectangles should still render.

`gx_stroke_fill` similarly resolves device and clip path, builds `gx_stroke_params`, and calls the device `stroke_path` procedure with the current device color. `gx_stroke_add` and `gx_imager_stroke_add` convert strokes into another path through `gx_stroke_path_only`; the former uses a full `gs_state`, the latter only an imager state plus device.

This file is a thin adapter layer. Its main integration point is the device procedure table. Errors are propagated from clip resolution and device calls.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.h

`gxpaint.h` declares Ghostscript's internal fill/stroke interface. It forward-declares `gs_imager_state`, `gs_state`, `gx_device`, and `gx_device_color`, avoiding heavier includes.

The graphics-state-aware API consists of `gx_fill_path`, `gx_stroke_fill`, `gx_stroke_add`, and `gx_imager_stroke_add`. These are implemented in `gxpaint.c` and bridge high-level graphics state to lower-level device path operations.

The imager-level API includes `gx_adjust_if_empty` and `gx_stroke_path_expansion`, plus the compatibility macro `gx_stroke_expansion`. `gx_stroke_path_expansion` computes a conservative/exact fixed-point bbox expansion for stroke width, caps, and joins, returning errors when the expansion cannot fit.

The header defines `gx_fill_params` with rule, adjustment, flatness, and zero-width-fill behavior, plus `gx_fill_path_only` as a direct device-proc macro. It also defines `gx_stroke_params` and declares `gx_stroke_path_only`, which can either draw a stroke or construct a stroked outline path.

The file is purely contractual; implementation is split across `gxpaint.c`, `gxfill.c`, and `gxstroke.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpaint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.c

`gxpath.c` implements mutable fixed-point path construction and path memory ownership. It uses Ghostscript's GC descriptors, fixed-point arithmetic, and internal `gzpath.h` segment definitions.

Paths own or share a reference-counted `gx_path_segments` object. Allocation supports heap paths, contained heap paths, stack-local paths, and a special bbox-accumulator pseudo-path. `gx_path_unshare` performs copy-on-write through `path_alloc_copy`. `gx_path_assign_preserve` and `gx_path_assign_free` carefully transfer segment ownership while preserving destination allocation class.

The incremental builder uses virtual `gx_path_procs`. Normal paths allocate concrete segments; bbox accumulator paths only update bbox/current-point state. Constructors include moveto, rmoveto, lineto, multi-line append, rectangle, curveto, partial arc approximation, path append, charpath append, closepath, and pop-closepath.

Segment allocation macros enforce unsharing, open subpaths when necessary, link new segments, and update state flags. `gx_path_add_partial_arc_notes` converts a small arc into one cubic Bezier using caller-supplied tangent fraction. `gx_path_add_char_path` implements charpath modes by appending actual outlines, bbox rectangles, bbox diagonals, or current points.

Debug-only routines dump path state and segment chains. Key risks are manual segment ownership, reliance on state flags, and partial additions in `gx_path_add_lines_notes` not being rolled back on mid-loop allocation failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.h

`gxpath.h` is the public fixed-point path and clipping-path interface for Ghostscript internals. It operates in device coordinates using fixed-point values, not user-space floating-point coordinates.

It declares `gx_path`, insideness rules, segment-note flags, memory-management functions, path constructors, state-flag accessors, path accessors, path transformers, enumerators, and clipping-path APIs. Memory management mirrors the implementation in `gxpath.c`: paths may be heap, contained, or stack objects, and segment storage may be shared until a constructor unshares it.

Constructor declarations include `gx_path_new`, point/line/rectangle/curve/arc/path append operations, charpath handling, and closepath variants. Compatibility macros provide note-less versions. `gx_path_copy_options` controls flattening/monotonizing behavior used by `gx_path_copy_reducing`.

Accessors expose current point, bbox, subpath start, curve presence, null/void checks, rectangular detection, and curve suitability checks. Transformers include reducing copy, reverse copy, translation, power-of-two scaling, dash expansion, and merge-contacting-contours optimization.

The clipping-path section declares analogous allocation/assignment APIs plus constructors, intersection, rectangle tests, and enumeration. This header is a major integration contract for fill, stroke, clip, font, and shading code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath2.c

`gxpath2.c` implements path access, bbox maintenance, rectangle recognition, transforms, reversal, and enumeration.

`gx_path_current_point` and `gx_path_subpath_start_point` return fixed-point positions or `nocurrentpoint`. `gx_path_bbox` lazily updates the stored bbox by scanning segments after `box_last`; curve control points are included. If the path has only a current point, that point is used. `gx_path_bbox_set` honors explicit `setbbox`.

Rectangle detection is handled by `gx_subpath_is_rectangular`, recognizing open rectangles, closepath rectangles, lineto-closed rectangles, and paths containing both lineto-to-start and closepath. `gx_path_is_rectangular` only succeeds for single-subpath paths.

`gx_path_translate` mutates bbox, current point, segment endpoints, and curve controls. `gx_point_scale_exp2`, `gx_rect_scale_exp2`, and `gx_path_scale_exp2_shared` scale points/paths by powers of two, optionally skipping shared segment mutation.

`gx_path_copy_reversed` emits reversed subpaths with Adobe-compatible closepath behavior. It preserves segment notes and handles trailing moveto semantics.

The enumerator functions initialize direct path iteration, return moveto/lineto/curveto/closepath events, expose last segment notes, and support one-or-more-element backup. Invalid segment types are treated as fatal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpath2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcache.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcache.h

`gxpcache.h` defines the rendered Pattern cache object. It forward-declares `gx_pattern_cache` and `gx_color_tile`.

`gx_pattern_cache_s` stores the allocator, tile array, tile count, used tile count, next round-robin replacement index, used bit budget, maximum bit budget, and a `free_all` callback. The header comment describes the design as an open hash table with single probing and round-robin replacement.

`private_st_pattern_cache()` supplies GC metadata for the `tiles` pointer; implementation and cache operations live in `gxpcmap.c`.

The structure is intentionally simple and low-level. Cache keys and values are in `gx_color_tile_s` from `gxpcolor.h`. The main limitation is direct id modulo indexing with no reprobing, so collisions evict existing entries aggressively.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcmap.c

`gxpcmap.c` implements PatternType 1 color mapping, rendered-pattern accumulation, and pattern-cache management.

The file defines default cache sizes, smaller under `arch_small_memory` or debug. It registers GC descriptors for color tiles, tile arrays, pattern cache, and pattern accumulator devices.

Pattern rendering uses `gx_device_pattern_accum`, a forwarding device that optionally owns a color memory device and a mono mask device. `pattern_accum_open` configures dimensions/resolution from the target device, allocates mask when `uses_mask`, and allocates color bits for colored patterns. Drawing procs forward fill/copy operations into the color target and update the mask. Close releases the mask and unretains the accumulator.

`gx_pattern_alloc_cache` creates a direct-mapped tile table. `gx_pattern_cache_add_entry` strips fully opaque masks, computes bitmap memory usage, evicts by id slot and round-robin budget pressure, then stores tile metadata and steals bitmap buffers from accumulator memory devices. `gx_pattern_cache_add_dummy_entry` creates high-level-device placeholder tiles.

`gx_pattern_load` renders the pattern PaintProc into an accumulator, inserts it, then verifies lookup. `gs_pattern1_remap_color` handles null patterns, uncolored pattern base-color remapping, masked device-color type substitution, and cache loading.

Risks are manual bitmap ownership transfer, direct cache collisions, and fatal behavior if accumulator bit readback is requested for uncolored-only paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcolor.h

`gxpcolor.h` declares internal Pattern color, tile, cache, and accumulator APIs. It includes pattern, color-space, device, memory-device, and cache headers.

`gs_pattern_type_s` is a dispatch table for pattern behavior: whether base color space is used, making an instance, retrieving a template, remapping color, and setcolor-time actions. The header declares common template/instance helpers and the Pattern color-space type.

The file declares Pattern device-color types for colored and uncolored masked variants, plus shared device-color serialization and nonzero-component methods.

`gx_color_tile_s` is the cache entry format. Its key fields are generated bitmap id, depth, and copied template UID; value fields include tiling type, step matrix, bbox, color bits, mask bits, simple/dummy flags, and index. Nonzero bitmap shifts are explicitly unsupported.

The header also declares default cache sizing, cache allocation, gstate cache accessors, accumulator allocation, cache insertion/dummy insertion, lookup, and selective winnowing. `gx_device_pattern_accum` wraps forward-device common fields with bitmap memory, pattern instance, color bits, and mask devices.

This is the main contract between pattern interpretation, rendering, and device-color use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcopy.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcopy.c

`gxpcopy.c` implements path copying with optional flattening, curve monotonizing, stroke-aware flatness adjustment, and fill-time contour merging.

`gx_path_copy_reducing` iterates source segments and emits corresponding destination segments. With `max_fixed` flatness it copies curves directly or monotonizes them. Otherwise it estimates subdivision count with `gx_curve_log2_samples` and emits flattened line segments through `gx_subdivide_curve`. For stroke flattening, it adjusts flatness based on estimated bbox expansion from line width and CTM. With `pco_accurate`, it inserts tangent-preserving endpoint lines and adjusts them using `adjust_point_to_tangent`.

`gx_path__check_curves` tests whether curves already satisfy requested monotonic/small-curve constraints. `gx_curve_monotonize` finds X/Y derivative roots, orders and merges split parameters, then emits cubic pieces. `gx_curve_monotonic_points` performs fixed-point prefilters before solving derivative roots.

The optimization section searches nearby subpaths for quasi-colinear vertical contacting segments and merges contours by rotating one subpath into another. This is explicitly heuristic, bounded by short search windows, and intended to help the filling algorithm.

Risks include complex fixed/double rounding, manual segment rewiring in contour merging, and comments noting simplified/incomplete behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcopy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpdash.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpdash.c

`gxpdash.c` expands dashed paths into explicit path segments. It assumes the input path has no curves.

`gx_path_add_dash_expansion` reads current dash parameters from the imager state's line params. If no dash pattern is active, it copies the path unchanged. Otherwise it walks each subpath and calls `subpath_expand_dashes`.

`subpath_expand_dashes` starts with a moveto, then walks line and close segments while consuming dash pattern elements. It transforms device-space segment deltas back through `gs_imager_idtransform` to compute user-space dash lengths. When dash adaptation is enabled, it rescales the pattern to fit an integral number of repetitions along the segment.

Ink-on sections emit lines; ink-off sections emit movetos. Closed subpaths with initial ink-on dashes use a two-pass wraparound scheme so the initial skipped section can be emitted at the end. Degenerate segments are skipped unless round caps are active. Near-zero trailing off elements may be stretched to produce a dot.

The function preserves segment notes where possible and propagates path-construction errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpdash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpflat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpflat.c

`gxpflat.c` provides Bezier curve flattening utilities for path copying and rasterization.

`gx_curve_log2_samples` estimates the power-of-two subdivision count needed to meet flatness, using a DEC PRL formula based on second differences. It handles very short curves and zero flatness specially for character outlines.

`split_curve_midpoint` bisects a cubic using overflow-conscious midpoint arithmetic. `curve_coeffs_ranged` converts control points to polynomial coefficients and rejects cases too large for the fast fixed-point iterator.

`gx_flattened_iterator__init` initializes a finite-difference iterator for monotonic nonzero curves, computing first/second/third differences with remainder masks. `gx_flattened_iterator__init_line` handles lines and splits very long lines to avoid coordinate-difference overflow in later algorithms. `gx_flattened_iterator__next` and `__prev` step forward/backward through flattened segments, with a compact special path for small `k`. `__switch_to_backscan` adjusts accumulator state before reverse scanning.

`gx_subdivide_curve_rec` emits line segments in bounded batches. If coefficient ranges are too large, it recursively midpoint-splits the curve. `gx_subdivide_curve` is the public wrapper.

This file is numerically sensitive: it mixes fixed-point overflow guards, recursive fallback, debug tracing, and finite-difference state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpflat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxropc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxropc.h

`gxropc.h` defines internal RasterOp compositing objects. It includes `gsropc.h` for RasterOp parameters and `gxcomp.h` for composite common fields.

`gs_composite_rop_t` embeds `gs_composite_common` and stores `gs_composite_rop_params_t params`. `private_st_composite_rop()` supplies GC metadata, especially for `params.texture`.

The only declared procedure is `gx_init_composite_rop`, which initializes a stack- or heap-allocated RasterOp compositing object from parameter data. The comment explains why this initializer is exposed: clients can allocate `gs_composite_rop_t` on the stack to avoid memory-manager overhead.

Implementation is in `gsropc.c`. This header is small but important for compositing paths that need RasterOp state without dynamic allocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxropc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxrplane.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxrplane.h

`gxrplane.h` declares planar rendering support. It forward-declares `gx_device`.

`gx_render_plane_t` describes extraction of one plane from chunky pixels. It contains `depth`, bit `shift` of the least significant bit from the low end, and an `index` within a multi-screen halftone. The comment says callers should treat this structure as opaque and initialize it only through the provided procedure.

`gx_render_plane_init` initializes a plane specification for a device and plane index. The device decides which bits constitute the plane; the comment notes this is currently fixed-procedure behavior but may eventually be moved into device properties or `color_info`.

The file is a compact interface layer for code that renders or separates individual planes from packed device pixels.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxrplane.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsample.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsample.c

`gxsample.c` implements image sample unpacking entry points and lookup tables.

The file defines `lookup4x1to32_identity` and `lookup4x1to32_inverted`, endian-dependent 1-bit expansion tables that map four 1-bit samples to packed 32-bit expanded output. Constants are shaped to avoid compiler warnings on different long sizes and C modes.

`sample_unpack_copy` returns the original data pointer and original bit offset when no unpacking/copying is needed.

The rest of the implementation is generated by including `gxsamplp.h` twice. The first include sets `MULTIPLE_MAPS` to `0` and creates `sample_unpack_1`, `_2`, `_4`, and `_8`. The second sets `MULTIPLE_MAPS` to `1` and creates interleaved variants where components use different sample maps.

This file is intentionally template-driven. Its integration point is `gximage` sample processing, which selects an unpack procedure based on bits per sample and component layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsample.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsample.h

`gxsample.h` declares lookup data and sample-unpack procedures for image decoding.

`sample_lookup_t` is a union of lookup-table layouts: 4x1-to-32-bit expansion for 1-bit samples without spreading, 2x2-to-16-bit expansion for 2-bit samples without spreading, and byte lookup for spread or higher-bit cases. The header declares identity and inverted 1-bit expansion tables.

`sample_map` is forward-declared. The `SAMPLE_UNPACK_PROC` macro defines the common unpacker signature. Unpackers receive an output buffer, output sample offset pointer, source data and bit/sample offset, source data size, sample map, spread factor, and number of components per plane. They return either the provided buffer or the original data pointer.

Declared unpackers include `sample_unpack_copy`, 1/2/4/8-bit unpackers, and interleaved 1/2/4/8-bit variants. This API supports efficient image data preparation before rendering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsample.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsamplp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsamplp.h

`gxsamplp.h` is a multi-include template used by `gxsample.c` to generate sample unpacking functions. Callers must define `MULTIPLE_MAPS` and function-name macros for 1/2/4/8-bit variants before inclusion.

For `MULTIPLE_MAPS`, the template advances through per-component sample maps modulo `num_components_per_plane`; otherwise it uses one map. It generates functions for 1-bit, 2-bit, 4-bit, and 8-bit samples.

The 1-bit unpacker either expands nibbles through `lookup4x1to32` when `spread == 1`, or writes each bit-expanded byte at `spread` intervals through `lookup8`. The 2-bit unpacker similarly uses `lookup2x2to16` for packed spread-1 output or byte lookups for spread output. The 4-bit unpacker maps high/low nibbles. The 8-bit unpacker can return the original source pointer when spread is 1 and the map is identity, avoiding copying.

Each generated function updates `*pdata_x` to the residual bit/sample offset and returns the buffer or source pointer. Risk areas are alignment casts to `bits32`/`bits16`, reliance on caller-provided buffer size, and template macro hygiene.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsamplp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.c

`gxshade.c` implements shared shading support: decoding mesh data streams and initializing fill state.

`shade_next_init` prepares a `shade_coord_stream_t` from a shading mesh data source. It supports reusable streams, strings wrapped in a local stream, and array sources. It selects packed or array value/decoded readers and initializes EOF/bit-buffer state.

Packed reads use `cs_next_packed_value`, which consumes arbitrary bit widths from a byte stream and reports rangecheck on EOF. Array reads use floats and validate integer range when reading flags or packed integer-like values. Decoded reads map packed integers through Decode ranges; array decoded values are used directly.

`shade_next_flag`, `shade_next_coords`, `shade_next_color`, and `shade_next_vertex` decode flags, transformed fixed-point coordinates, color components, Indexed color lookups, and full mesh vertices.

`shade_init_fill_state` computes common recursive fill tolerances from smoothness, device color capacity, halftone levels, shading type, and CIE/ICC ranges. It resolves Indexed spaces to direct base spaces. `shade_fill_path` fills one generated path through the device `fill_path` proc with shading-specific params.

This file is the common substrate for mesh, axial, radial, and patch shading renderers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.h

`gxshade.h` declares internal shading-rendering types and APIs. It documents the parameter-space mappings for PDF/PostScript shading types 1 through 7 and the general recursive subdivision strategy.

The header defines concrete shading structs for function-based, axial, radial, free-form Gouraud triangle, lattice-form Gouraud triangle, Coons patch, and tensor-product patch shadings, each with a fill-rectangle procedure declaration.

`shade_coord_stream_t` stores a stream wrapper, bit buffer, EOF flag, mesh params, CTM, and function pointers for reading values and decoded floats. It is used by mesh renderers to consume packed, string, stream, or array data sources.

`mesh_vertex_t` stores fixed position plus float color components, while `shading_vertex_t` is forward-declared for the triangle/patch header to define.

The common fill state macro stores device, imager state, direct color space, component count, and per-component maximum color error. Public helpers initialize stream/fill state, decode flags/coordinates/colors/vertices, and fill generated shading paths.

This header is the bridge between generic shading setup and specialized renderer implementations in `gxshade1.c`, `gxshade4.c`, and related patch files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade1.c

`gxshade1.c` renders non-mesh shadings: function-based, axial, and radial. It builds patch/triangle representations and delegates actual subdivision/filling to patch helpers from `gxshade4.h` and related files.

For function-based shading, `gs_shading_Fb_fill_rectangle` transforms the target rectangle into the shading domain, evaluates the function at region corners, builds a four-sided patch with straight control poles, and calls `patch_fill`.

For axial shading, `gs_shading_A_fill_rectangle` maps the fill rectangle into a coordinate system where the shading axis is the parameter dimension. It computes the clipped parameter range, creates a parallelogram strip patch with endpoint parameter colors, and handles `Extend[0]`/`Extend[1]` by filling constant-color extension strips.

Radial shading is more complex. It represents interpolation between circles as annular tensor patches. Helpers construct quadrant arcs, outer extension circles, apex/cone fills, obtuse-cone triangles, and nested-circle extensions. `gs_shading_R_fill_rectangle` initializes patch state, paints optional start extension, the core annulus, and optional end extension.

The code uses visual-debug tracing hooks and has several comments marking approximations, especially for radial extension clipping. Risk areas include geometric degeneracy, radius/cone edge cases, and the apparent typo in `make_other_poles` where `control[1].x` is assigned but `control[1].y` is divided before being set.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.c

`gxshade4.c` renders Gouraud triangle mesh shadings.

`mesh_init_fill_state` initializes common shading fill state, stores the mesh shading pointer, and records the fixed clipping rectangle.

`Gt_next_vertex` decodes the next vertex through `shade_next_vertex`; if the mesh has a Function, it treats the decoded color as a function parameter and evaluates the Function into actual color components.

`Gt_fill_triangle` creates a temporary `patch_fill_state_t`, initializes it, optionally paints interpatch padding along the triangle edges, then calls `mesh_triangle`. It terminates patch state afterward.

`gs_shading_FfGt_fill_rectangle` handles free-form triangle meshes. It reads flags from the coordinate stream: flag 0 starts a fresh triangle, flag 1 reuses the previous second/third vertices in one pattern, and flag 2 reuses them in another. Each completed triangle is filled.

`gs_shading_LfGt_fill_rectangle` handles lattice-form meshes. It reads the first row into an allocated vertex array, then streams subsequent vertices to form pairs of triangles between adjacent rows. The vertex array is freed on exit.

Errors propagate from decoding, allocation, function evaluation, and triangle fill. EOF handling differs by mode: free-form checks stream EOD after flag read failure, lattice loops on stream EOF.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.h

`gxshade4.h` defines internal triangle and patch shading rendering state.

Development flags control linear color procedures, triangle vs quadrangle decomposition, interpatch padding, color-contiguity subdivision, lazy wedge generation, and visual-debug/testing modes. Production-relevant defaults include triangle decomposition, half-pixel interpatch padding, and lazy wedges.

`mesh_frame_t` stores recursion vertices and clipping state. `mesh_fill_state_t` extends common shading fill state with mesh shading pointer, clip rect, recursion depth, and a fixed-size recursion frame stack.

Lazy wedge support uses linked `wedge_vertex_list_elem_t` nodes and lists to defer boundary wedge creation until neighboring areas are known. This reduces redundant wedge fills along shared subdivision boundaries.

`patch_fill_state_t` extends mesh fill state with Function pointer, vectorization flags, color argument count, coordinate/flatness/smoothness controls, self-intersection and color-linearity flags, wedge-buffer ownership, and color domain data.

`patch_color_t`, `shading_vertex_t`, and `patch_curve_t` represent parametric colors, mesh/patch vertices, and Bezier patch boundaries. The header declares fill-state lifecycle, triangle fill, padding, patch fill, wedge-buffer allocation/free, color resolution, and shade-background helper.

This is a shared private contract for `gxshade4.c`, `gxshade1.c`, and patch-rendering implementation files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.h -->