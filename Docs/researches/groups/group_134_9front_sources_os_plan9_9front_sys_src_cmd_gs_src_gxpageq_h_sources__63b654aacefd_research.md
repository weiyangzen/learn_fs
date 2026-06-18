# Group Research: group_134_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxpageq_h_sources__63b654aacefd

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.h

Ghostscript page queue interface for producer/renderer coordination around band-list pages. It declares the queue entry type, action enum, memory descriptors, and public lifecycle/synchronization routines used by the page writer and renderer threads.

Key contents:
- `gx_page_queue_action_t` defines `PARTIAL_PAGE`, `FULL_PAGE`, `COPY_PAGE`, and `TERMINATE` actions, with detailed ordering semantics for partial band-list fragments, `copypage`, `showpage`, cancelled pages, and shutdown.
- `gx_page_queue_entry_s` stores `gx_band_page_info_t`, action, copy count, FIFO link, and back-pointer to its queue.
- Queue APIs cover allocation, initialization/destruction, enqueue/add-page, blocking dequeue, finish-dequeue cleanup, and waiting for one or all queued pages to finish rendering.
- The comments explicitly separate freeing a queue entry from freeing its large page/band-list resources.

Notable dependencies:
- `gsmemory.h` for Ghostscript allocation.
- `gxband.h` for band-list page metadata.
- `gxsync.h` for monitor/thread synchronization primitives used by the implementation.

Research notes:
- This header is concurrency-facing but implementation details are intentionally hidden in `gxpageq.c`.
- The action comments are the most important contract: a renderer must preserve preceding partial and copy-page state until the corresponding full/copy page semantics are satisfied.
- There is a spelling typo in the comment/prototype area (`Declaraions`, `deqeueue`), but the API contract is clear.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.c

Small graphics-state-aware wrapper layer for path fill and stroke operations. It converts the full `gs_state` into device fill/stroke calls using the current device, clip path, flatness, and color.

Key behavior:
- `caching_an_outline_font` detects outline font cache-device rendering and suppresses normal flatness by using `0.0`, preserving higher quality cached glyph outlines.
- `gx_fill_path` resolves the effective clipping path, fills `gx_fill_params`, and dispatches to the current device `fill_path` procedure.
- `gx_stroke_fill` resolves clipping and dispatches to device `stroke_path` with current device color.
- `gx_stroke_add` and `gx_imager_stroke_add` call `gx_stroke_path_only` to append stroked outlines to another path, using graphics-state or imager flatness.

Notable dependencies:
- Graphics state internals: `gzstate.h`.
- Device and color dispatch: `gxdevice.h`, `gxhttile.h`.
- Path and stroke declarations: `gxpaint.h`, `gxpath.h`.
- Font state: `gxfont.h`.

Research notes:
- This file does not implement rasterization itself; it packages state for lower-level fill/stroke implementations and device procedures.
- The clip path is resolved before dispatch, so failures in clipping state prevent device calls.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.h

Internal fill/stroke interface tying Ghostscript graphics state paths to imager/device procedures.

Key contents:
- Forward declarations for `gs_imager_state`, `gs_state`, `gx_device`, and `gx_device_color`.
- Graphics-state-aware procedures implemented in `gxpaint.c`: `gx_fill_path`, `gx_stroke_fill`, `gx_stroke_add`, and `gx_imager_stroke_add`.
- `gx_fill_params` carries fill rule, subpixel adjustment, flatness, and the `fill_zero_width` flag for making nearly empty rectangles visible.
- `gx_stroke_params` currently carries flatness.
- Declares `gx_adjust_if_empty`, `gx_stroke_path_expansion`, and `gx_stroke_path_only`.
- Provides compatibility macro `gx_stroke_expansion` and direct `gx_fill_path_only` dispatch macro.

Notable dependencies:
- Requires fixed-point, path, and raster-op related types from surrounding includes.
- The lower-level implementations live mostly in fill/stroke modules outside this group.

Research notes:
- The API distinguishes high-level graphics-state-aware wrappers from imager-level procedures that can be called without a full `gs_state`.
- `gx_imager_stroke_add` still requires a device for absolute-length dots.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpaint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.c

Core Ghostscript fixed-point path construction and memory-management implementation. It owns path allocation modes, shared segment reference-counting, subpath/segment creation, incremental path mutation, charpath transfer behavior, closepath handling, and debug printing.

Key behavior:
- Defines structure descriptors for path objects and segment types, plus default path procedure tables and a bbox-accumulator procedure table.
- Supports heap-allocated, contained, and stack/local paths, with separate reference-counted segment storage.
- Prevents sharing of local segment storage; attempts to share local segments are treated as fatal.
- `gx_path_unshare` and `path_alloc_copy` implement copy-on-write before mutation.
- Constructors add moveto, rmoveto, lines, multiple lines, rectangles, curves, partial arcs, whole paths, and charpath-specific variants.
- `gx_path_add_path` physically splices subpath segment chains from one path into another, then resets the source path.
- Closepath allocates `line_close_segment`, links it to the current subpath, and records the source subpath.
- `gx_path_pop_close_notes` removes the final line and replaces it with closepath for Type 1 font hinting workflows.
- Debug builds can dump complete segment chains with coordinates and notes.

Notable dependencies:
- `gzpath.h` for concrete path/segment internals.
- `gsstruct.h` for GC descriptors and reference-counting macros.
- `gxfixed.h` for fixed-point coordinates.
- `vdtrace.h` for optional visual tracing.

Research notes:
- Memory ownership is subtle: path objects and segment containers have separate allocation modes and lifetimes.
- `gx_path_add_lines_notes` intentionally does not roll back partial additions on allocation/range failure, matching repeated single-line calls.
- Bounding-box enforcement via `bbox_set` rejects points outside a preset bbox during construction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.h

Public/internal fixed-point path and clipping-path API for Ghostscript imager code. The interface operates in device coordinates and uses fixed-point values rather than user-space floating-point values.

Key contents:
- Defines path insideness rules, segment notes, path copy options, and rectangle-classification enum.
- Declares path allocation/initialization/free/assignment functions for heap, contained, and local paths, including shared segment variants.
- Declares constructors for points, relative points, lines, rectangles, curves, partial arcs, path append, charpath append, closepath, and pop-close.
- Exposes state flags, current point, bbox queries, curve/void/null tests, rectangle detection, path reduction/copy/reversal/translation/scaling, dash expansion, and contour merging.
- Declares path enumeration functions that do not copy the path and expose segment notes/backtracking.
- Declares clipping path allocation, assignment, construction, intersection, conversion to path, rectangle inclusion, and enumeration APIs.

Notable dependencies:
- `gscpm.h`, `gslparam.h`, `gspenum.h`, and `gsrect.h`.
- Concrete structures are opaque here and defined in `gzpath.h`.

Research notes:
- The comments are an important ownership guide: path objects may be stack, heap, or embedded, while segment data are shared reference-counted objects.
- The copy options show the path subsystem supports flattening, monotonization, stroke-aware flattening, accurate tangents, and small-curve constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath2.c

Read-side and transformation support for Ghostscript fixed-point paths. It implements current-point queries, bbox maintenance, rectangular path recognition, translation/scaling, path reversal, and path enumeration.

Key behavior:
- `gx_path_current_point` and `gx_path_subpath_start_point` return current/start points or `nocurrentpoint`.
- `gx_path_bbox` lazily updates the cached bbox by scanning only segments after `box_last`; empty paths fall back to current point if present.
- `gx_path_bbox_set` honors explicit bboxes used by `patbbox`.
- `gx_subpath_is_rectangular` recognizes open, closed, fake-closed, and redundantly closed rectangles.
- `gx_path_translate` updates cached bbox, current point, segment endpoints, and curve controls.
- `gx_path_scale_exp2_shared` scales path metadata and, when segments are not shared, segment coordinates by powers of two.
- `gx_path_copy_reversed` reproduces Adobe reversepath behavior, including treatment of closepath and trailing moveto.
- Path enumeration returns moveto/lineto/curveto/closepath records, supports notes, and can back up one or more elements.

Notable dependencies:
- `gspath.h` for enumerator allocation prototype.
- `gxarith.h` and `gxfixed.h` for fixed-point arithmetic.
- `gzpath.h` for concrete segment traversal.

Research notes:
- Rectangle detection is intentionally tolerant of common bad PostScript that closes with both lineto and closepath.
- `gx_path_scale_exp2_shared` always scales bbox/current position but skips segment mutation when segments are shared; callers must pass the sharing flag correctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpath2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcache.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcache.h

Definition of the Ghostscript Pattern cache object.

Key contents:
- Forward declarations for `gx_pattern_cache` and `gx_color_tile`.
- `gx_pattern_cache_s` stores allocator, tile array, tile counts, round-robin index, current/max bitmap bit usage, and a `free_all` callback.
- Declares the private GC descriptor macro implemented in `gxpcmap.c`.

Notable dependencies:
- Uses Ghostscript memory and scalar types supplied by including context.

Research notes:
- The file documents the cache as an open hash table with single probing and round-robin replacement, with a note that both strategies could be improved.
- The cache data model is intentionally small and simple: no chaining, no reprobing, and fixed tile storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcmap.c

Pattern color mapping, rendering, accumulation, and caching implementation for PatternType 1 colors.

Key behavior:
- Provides default Pattern cache sizing, with smaller defaults for small-memory/debug configurations.
- Defines GC descriptors for color tiles, cache entries, pattern accumulators, and related device structures.
- Implements a pattern accumulator forwarding device that renders colored pattern bits and/or a 1-bit mask into memory devices.
- Accumulator drawing procs update color bits when present and update mask coverage for fills, mono copies, and color copies.
- `gx_pattern_alloc_cache` creates a fixed-size tile table and initializes tile keys/data pointers.
- `gx_pattern_cache_free_entry` releases cached tile bitmaps and updates `bits_used`/`tiles_used`.
- `gx_pattern_cache_add_entry` strips all-ones masks, evicts by hash slot and round-robin size pressure, transfers bitmap ownership from accumulator devices into cache tiles, and records pattern metadata.
- `gx_pattern_cache_add_dummy_entry` records a device-managed high-level pattern placeholder.
- `gx_pattern_load` checks cache, renders the pattern PaintProc into an accumulator device, adds it to the cache, then closes/free states.
- `gs_pattern1_remap_color` handles colored and uncolored PatternType 1 remapping and loads the pattern tile/mask.

Notable dependencies:
- Pattern/color internals: `gxpcolor.h`, `gxp1impl.h`, `gxcolor2.h`, `gxdcolor.h`.
- Device/memory devices: `gxdevice.h`, `gxdevmem.h`.
- Graphics state: `gzstate.h`.

Research notes:
- `pattern_accum_get_bits_rectangle` notes that unread areas should use the mask but currently do not.
- The cache indexes by `id % num_tiles`; collisions evict the existing slot.
- `gx_pattern_load` has multiple ownership transitions: accumulator close normally frees bookkeeping, but cached bitmap buffers are preserved by clearing memory pointers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcolor.h

Pattern color and rendered-tile structure declarations for Ghostscript.

Key contents:
- Defines `gs_pattern_type_t`, including callbacks for base-space use, pattern instantiation, template lookup, color remapping, and setcolor-time handling.
- Declares common pattern initialization/instantiation helpers and pattern instance freeing.
- Declares Pattern color space type and Pattern device color types for colored and masked uncolored patterns.
- Declares shared Pattern device-color serialization and nonzero-component methods.
- Defines `gx_color_tile`, the cache value/key for rendered PatternType 1 tiles: generated id, depth, template uid, tiling type, step matrix, bbox, color bits, mask, simplicity flag, dummy flag, and cache index.
- Defines `gx_device_pattern_accum`, a forwarding device wrapping memory devices for rendered pattern image and mask.
- Declares cache allocation, gstate cache access, accumulator allocation, cache insertion/dummy insertion, lookup, and selective purge functions.

Notable dependencies:
- `gspcolor.h`, `gxcspace.h`, `gxdevice.h`, `gxdevmem.h`, and `gxpcache.h`.

Research notes:
- The header notes that color depth alone is not enough to prove a cached tile matches a target device, because there is no full color-representation object.
- Non-zero bitmap shifts for tiles are explicitly unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcopy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcopy.c

Path copying, curve flattening orchestration, curve monotonization, and contour-merge optimization code.

Key behavior:
- `gx_path_copy_reducing` copies a path while optionally preserving curves, flattening curves, monotonizing curves, applying accurate tangent endpoints, or adjusting flatness for stroking.
- Stroke-aware flattening reduces flatness according to a conservative expansion estimate based on CTM and line half-width.
- Accurate flattening inserts extra tangent line segments and adjusts endpoints to align better with curve tangents.
- `adjust_point_to_tangent` handles vertical, horizontal, and general tangent projection cases.
- `gx_path__check_curves` tests whether curves already satisfy monotonic/small-curve constraints.
- `gx_curve_monotonize` splits a Bezier at derivative roots in X and Y so resulting curve spans are monotonic.
- `gx_curve_monotonic_points` computes valid derivative-zero parameters with several cheap rejection cases before using square roots.
- `gx_path_merge_contacting_contours` searches nearby subpaths for quasi-vertical contacting line segments and splices contours together for fill optimization.

Notable dependencies:
- `gconfigv.h` for FPU configuration.
- `gxistate.h` for line parameters.
- `gzpath.h` for segment internals.
- Fixed arithmetic helpers from `gxfixed.h`/`gxfarith.h`.

Research notes:
- On copy error, the destination path is reset with `gx_path_new`, avoiding partially reduced output.
- The contour merge is explicitly simplified and heuristic: it searches limited windows and only quasi-vertical contacts.
- In `gx_curve_monotonize`, the statements assigning `ry = -qy` in two sign-noise branches look suspicious because they mirror `rx = -rx` but use `qy` rather than `ry`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcopy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpdash.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpdash.c

Dash expansion for flattened paths. It converts dashed stroke input into explicit path segments before stroking/filling.

Key behavior:
- `gx_path_add_dash_expansion` copies the path unchanged when no dash pattern is active; otherwise it expands each subpath.
- `subpath_expand_dashes` walks line-only subpaths, tracks dash index, remaining element length, and ink-on state.
- Segment lengths are measured in user space by inverse distance-transforming device-space fixed deltas.
- Dash-adapt mode rescales the dash pattern to fit an integer number of repetitions on a segment.
- Closed paths with initial ink require wraparound handling: the initial region may be skipped and emitted after the rest of the subpath.
- Degenerate segments are skipped unless round line caps are active.
- Near-end off dashes are stretched by epsilon to produce a dot when required.

Notable dependencies:
- Line state from `gsline.h`/`gzline.h`.
- Coordinate transforms from `gsmatrix.h` and `gscoord.h`.
- Concrete paths from `gzpath.h`.

Research notes:
- The implementation assumes the input path contains no curves.
- The `drawing` state is compact but subtle: `-1` skips initial closed-path segments, `0` draws normally, and `1` emits the delayed wraparound portion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpdash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpflat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpflat.c

Bezier curve flattening algorithms and iterator support for converting curves into line segments.

Key behavior:
- `gx_curve_log2_samples` estimates `log2` sample count from DEC PRL flatness bounds, with special handling for short curves and flatness zero.
- `split_curve_midpoint` bisects a cubic Bezier using overflow-aware fixed-point midpoints.
- `curve_coeffs_ranged` checks whether polynomial coefficients and sample count fit the fast fixed-point iterator range.
- `gx_flattened_iterator__init` precomputes finite differences for a monotonic curve and stores current/end state.
- `gx_flattened_iterator__init_line` represents long lines as two segments when endpoint subtraction may overflow.
- `gx_flattened_iterator__next` and `gx_flattened_iterator__prev` scan flattened segments forward/backward using accumulated fixed-point deltas and remainders.
- `gx_flattened_iterator__switch_to_backscan` adjusts iterator state when changing scan direction.
- `gx_subdivide_curve_rec` falls back to recursive midpoint subdivision when the fast iterator cannot represent a curve safely, batching generated points into line additions.
- `gx_subdivide_curve` is the public wrapper around recursive subdivision.

Notable dependencies:
- `gxarith.h`, `gxfixed.h`, and concrete path internals in `gzpath.h`.
- `vdtrace.h` for optional visual debugging.

Research notes:
- The file favors fast fixed-point iteration but recursively subdivides to avoid coefficient overflow.
- `max_points` limits batched line generation, reducing stack/local buffer size while still streaming long flattened output.
- Comments include several old spelling mistakes, but the algorithmic intent is well documented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpflat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxropc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxropc.h

Internal RasterOp compositing object declaration.

Key contents:
- Includes public RasterOp compositing parameters from `gsropc.h` and base compositor declarations from `gxcomp.h`.
- Defines `gs_composite_rop_t` as `gs_composite_common` plus `gs_composite_rop_params_t`.
- Declares the GC descriptor macro for `params.texture`.
- Declares `gx_init_composite_rop`, allowing callers to initialize stack-allocated RasterOp compositors.

Notable dependencies:
- `gsropc.h` for RasterOp parameters.
- `gxcomp.h` for compositor common fields.

Research notes:
- The comments explicitly justify exposing initialization so clients can avoid memory-manager overhead by stack-allocating compositor objects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxropc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxrplane.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxrplane.h

Planar rendering helper declarations for extracting one plane from chunky pixels.

Key contents:
- Forward-declares `gx_device`.
- Defines `gx_render_plane_t` with bit depth, least-significant-bit shift, and plane/screen index.
- Declares `gx_render_plane_init`, which initializes a plane specification for a given device and plane index.

Notable dependencies:
- Device-specific color layout is supplied by the implementation/device, not by this header.

Research notes:
- The header says the structure should be treated as opaque by callers despite its fields being visible.
- Comments note that plane selection is currently fixed-procedure based but should eventually become a device/color-info property.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxrplane.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.c

Sample unpacking entry module. It defines endian-dependent lookup tables for 1-bit expansion and instantiates unpacking templates for shared-map and interleaved multi-map cases.

Key behavior:
- Builds `lookup4x1to32_identity` and `lookup4x1to32_inverted` differently for big-endian and little-endian CPUs.
- Handles compiler constant quirks for 32-bit and 64-bit long expressions.
- `sample_unpack_copy` returns the original data pointer when no unpacking/copying is needed and updates `pdata_x`.
- Includes `gxsamplp.h` twice:
  - once for single lookup map functions `sample_unpack_1/2/4/8`,
  - once for interleaved component maps `sample_unpack_1/2/4/8_interleaved`.

Notable dependencies:
- `gxsample.h` for public declarations and sample lookup types.
- `gximage.h` and `gxfixed.h` for image context.
- Template implementation in `gxsamplp.h`.

Research notes:
- The lookup tables are deliberately typed as aligned integer arrays rather than byte arrays.
- This module is compile-time template instantiation rather than hand-written separate functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.h

Sample lookup and expansion interface for image sample unpacking.

Key contents:
- Defines `sample_lookup_t`, a union containing lookup tables for 1-bit-to-32-bit, 2-bit-to-16-bit, and 8-bit byte expansion cases.
- Declares identity and inverted standard 1-bit expansion lookup arrays.
- Defines the `SAMPLE_UNPACK_PROC` macro and `sample_unpack_proc_t` function pointer type.
- Declares no-copy unpacking plus 1-, 2-, 4-, and 8-bit unpackers, including interleaved multi-map variants.

Notable dependencies:
- Expects `bits32`, `bits16`, `byte`, `uint`, and `sample_map` context from surrounding Ghostscript headers.

Research notes:
- Unpacking routines may return either the caller buffer or the original input data, so callers must use the returned pointer rather than assuming `bptr`.
- `spread` and `num_components_per_plane` allow both contiguous expansion and interleaved component layouts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsample.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsamplp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsamplp.h

Multi-include template header that generates sample unpacking functions for 1-, 2-, 4-, and 8-bit samples, with optional per-component lookup-map rotation.

Key behavior:
- Requires callers to define `MULTIPLE_MAPS` and the four `TEMPLATE_sample_unpack_*` function names before inclusion.
- For `MULTIPLE_MAPS`, `NEXT_MAP`/`NEXT_MAP8` advance through per-component `sample_map` tables modulo `num_components_per_plane`.
- 1-bit unpacking expands either by 4-bit chunks into `bits32` values when `spread == 1`, or by individual bits into byte output when spreading.
- 2-bit unpacking expands nibbles into `bits16` values for contiguous output or individual 2-bit samples into byte output.
- 4-bit unpacking maps high/low nibbles into byte output.
- 8-bit unpacking can avoid copying entirely when output is contiguous and the map is identity; otherwise it maps bytes into the destination buffer.
- Each routine updates `*pdata_x` to the residual sample offset appropriate for the bit depth.

Notable dependencies:
- Included by `gxsample.c`; depends on `sample_lookup_t`, `sample_map`, `byte`, `bits16`, and `bits32`.

Research notes:
- This is intentionally not guarded by a normal include guard because it is included multiple times in one translation unit.
- `dsize` is treated as source byte count; routines compute `left` after applying the sample offset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsamplp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.c

Common shading rendering support: packed mesh data decoding, shading fill-state initialization, and path fill helper.

Key behavior:
- `shade_next_init` initializes a `shade_coord_stream_t` over a reusable stream, string, or array data source, selecting packed or array value decoders.
- `cs_next_packed_value` reads arbitrary-width packed unsigned integers across byte boundaries and marks EOF on short reads.
- `cs_next_array_value` reads float values from unpacked arrays and validates integer range when flags/packed values are requested.
- Decoding functions convert packed integers through Decode ranges or pass array floats through directly.
- `shade_next_flag` byte-aligns packed input before reading a flag.
- `shade_next_coords` reads coordinate pairs, decodes them, and transforms them through the current CTM to fixed device points.
- `shade_next_color` handles Indexed color lookup, direct component decode, or single function argument input.
- `shade_next_vertex` reads one mesh vertex and initializes a second color argument defensively.
- `shade_init_fill_state` chooses direct/base color space, computes per-component smoothness/error tolerances, and accounts for device color/halftone capacity.
- `shade_fill_path` fills a path using the target device with shading-specific fill params.

Notable dependencies:
- Color spaces and indexed/CIE/ICC support: `gxcspace.h`, `gscindex.h`, `gscie.h`, `gsicc.h`.
- Device/client and halftone state: `gxdevcli.h`, `gxistate.h`, `gxdht.h`.
- Fill and shading internals: `gxpaint.h`, `gxshade.h`, `gxshade4.h`.

Research notes:
- `MAX_SMOOTHNESS` clamps overly high smoothness to avoid blocky output.
- Function-based shadings with non-monotonic functions are noted in `gxshade.h` as not fully handled by the smoothness test.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.h

Internal declarations and algorithm notes for Ghostscript shading rendering.

Key contents:
- Documents parameter-space, color, and user-space mappings for shading types 1 through 7.
- Declares concrete shading wrapper structs for function-based, axial, radial, free-form Gouraud, lattice Gouraud, Coons patch, and tensor-product patch shadings.
- Declares fill-rectangle procedures for each shading type.
- Defines `shade_coord_stream_t`, which abstracts packed/array mesh data reading, decode, CTM conversion, and EOF state.
- Defines `mesh_vertex_t` and forward-declares `shading_vertex_t`.
- Declares stream helpers for flags, coordinates, colors, and vertices.
- Defines `shading_fill_state_common` and `shading_fill_state_t`, including device, imager state, direct color space, component count, and max color errors.
- Declares common fill-state initialization and `shade_fill_path`.

Notable dependencies:
- Public shading params from `gsshade.h`.
- Fixed and matrix types from `gxfixed.h`/`gxmatrix.h`.
- Ghostscript stream API.

Research notes:
- The header is unusually explanatory: it lays out the recursive subdivision strategy used by shading renderers.
- It notes that type 3 circle mappings are not closed under general CTM linear transforms in the same way as other shadings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade1.c

Rendering for non-mesh shadings: function-based type 1, axial type 2, and radial type 3. It converts these shading forms into patch/triangle fill operations shared with mesh shading code.

Key behavior:
- Function-based shading computes the inverse parameter range for the target rectangle, evaluates the function at the four parameter-space corners, builds a synthetic patch, and calls `patch_fill`.
- Axial shading builds a coordinate frame where the axial line is the parameter direction, clips the requested fill rectangle to `[0,1]`, fills the main band, and optionally fills extension bands at constant endpoint colors.
- Radial shading represents the interpolation between two circles using annular tensor patches and handles extension regions for nested, obtuse-cone, acute-cone, cylinder, and apex cases.
- `R_tensor_annulus` decomposes circle annulus portions into four patch quadrants using Bezier quadrant arcs.
- `R_outer_circle`, `R_rect_radius`, `R_obtuse_cone`, `R_tensor_cone_apex`, and `R_extensions` compute geometry needed for radial extension regions.
- Visual debug tracing hooks exist for axial, radial, and function-based patch rendering.

Notable dependencies:
- Function/pattern and color support: `gsptype2.h`, `gxcspace.h`, `gxdcolor.h`.
- Path and shading internals: `gxpath.h`, `gxshade.h`, `gxshade4.h`.
- Device client and imager state: `gxdevcli.h`, `gxistate.h`.

Research notes:
- `make_other_poles` appears to contain a real assignment-order typo: `curve[i].control[1].y /= 3;` is executed before `control[1].y` is assigned from vertex coordinates.
- `gs_shading_R_fill_rectangle` releases visual tracing with `VD_TRACE_FUNCTIONAL_PATCH` rather than `VD_TRACE_RADIAL_PATCH`, which looks like a copy/paste inconsistency.
- The radial extension logic is geometry-heavy and contains comments acknowledging approximations, such as not cutting invisible annulus parts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.c

Rendering front-end for Gouraud triangle mesh shadings, including free-form and lattice forms. It decodes vertices and delegates actual triangle/padding rendering to patch/mesh helpers.

Key behavior:
- `mesh_init_fill_state` initializes common shading fill state and stores the clipping rectangle.
- `Gt_next_vertex` reads a shading vertex and, if a Function is present, treats the decoded component as a function input and evaluates it into actual color components.
- `Gt_fill_triangle` creates a `patch_fill_state_t`, optionally emits interpatch padding on all triangle edges, then calls `mesh_triangle`.
- `gs_shading_FfGt_fill_rectangle` reads free-form Gouraud mesh flags. Flag `0` reads a fresh triangle; flags `1` and `2` reuse prior vertices according to PostScript mesh semantics.
- `gs_shading_LfGt_fill_rectangle` allocates one row of vertices, then consumes subsequent rows to generate two triangles per lattice cell.
- Visual trace hooks wrap triangle patch rendering when enabled.

Notable dependencies:
- Mesh stream decoding from `gxshade.c`/`gxshade.h`.
- Patch/mesh fill helpers from `gxshade4.h`.
- Color/function support: `gsptype2.h`, `gxcspace.h`, `gxdcolor.h`.

Research notes:
- Free-form mesh parsing returns `rangecheck` for invalid flags and verifies that loop termination was actual end-of-data.
- Lattice mesh rendering frees its row buffer through a single `out` path.
- This file does not define `mesh_triangle`, `mesh_padding`, or patch fill internals; it is the type-4/type-5 decoder/front-end.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.h

Internal declarations and compile-time tuning flags for triangle and patch shading rendering.

Key contents:
- Development/tuning flags for linear color procedures, quadrangle mode, interpatch padding, color contiguity, lazy wedges, visual trace, and no-fill/skip tests.
- Defines `mesh_frame_t`, `mesh_fill_state_t`, and common mesh fill-state macro with recursion frames.
- Defines wedge vertex list structures and lazy-wedge buffer sizing.
- Defines `patch_fill_state_t`, which extends mesh state with Function, vectorization, color-domain, flatness, smoothness, color linearity, self-intersection, and wedge allocation fields.
- Defines `patch_color_t`, `shading_vertex_s`, and `patch_curve_t`.
- Declares mesh/patch initialization, teardown, triangle fill, edge padding, patch fill, wedge-buffer allocation/free, color resolution, and background shading helper.

Notable dependencies:
- Consumes common shading types from `gxshade.h`.

Research notes:
- Comments describe interpatch padding as an Adobe-style trapping emulation using half-pixel expansion.
- `QUADRANGLES` support is retained mainly as historical/useful reference code but disabled because triangle decomposition looked better and faster.
- Several structures note missing GC descriptors, indicating this is internal transient rendering state rather than fully managed object state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.h -->