# Group Research: group_136_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxwts_h_sources_os_561c45010476

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.h

Defines weighted threshold screen data structures for Ghostscript halftoning.

Key points:
- Defines `wts_screen_sample_t` as `bits16`, plus opaque `wts_screen_t`.
- Supports screen types `WTS_SCREEN_RAT`, `WTS_SCREEN_J`, and `WTS_SCREEN_H`.
- Base `wts_screen_s` stores cell dimensions, shift, type, and sample buffer.
- `wts_screen_j_t` adds jump probabilities and coordinate deltas for J-style screens.
- `wts_screen_h_t` adds exact split proportions and integer split positions for H-style screens.
- Declares `wts_get_samples`, which maps an `(x,y)` location to sample data and count.

Research notes:
- This is a compact internal interface; implementation is elsewhere.
- The fields are layout/algorithm parameters for screen sample lookup, not general graphics state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxxfont.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxxfont.h

Defines Ghostscript’s external-font object interface.

Key points:
- Documents design assumptions: devices supply xfonts, xfonts are transformation-specific objects, and they provide bitmaps independent of a particular device.
- Defines `gx_xfont_common`, `gx_xfont`, and `gx_xfont_procs`.
- Procedure vector covers lookup, character/glyph mapping, metrics, rendering, and release.
- `lookup_font` is explicitly a factory callback taking a device, font name, encoding, UID, matrix, and allocator.
- `render_char` can target any Ghostscript device.
- Provides GC descriptor helper macros for xfonts that hold a single device pointer.

Research notes:
- This is a device-facing font acceleration/bitmap interface.
- The header preserves compatibility history around deprecated and later restored glyph mapping behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxxfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzacpath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzacpath.h

Declares the clipping-path accumulator device interface.

Key points:
- Defines `gx_device_cpath_accum`, a device that accumulates clip rectangles into a `gx_clip_list`.
- Stores allocator, clip box, bounding box, and accumulated list.
- Used to clip accumulated clipping paths to band boundaries during band-list rendering.
- Declares begin, set clipping box, end, discard, and slow path intersection APIs.
- `gx_cpath_accum_end` releases old clipping-path contents before installing the accumulated result.

Research notes:
- This is infrastructure for converting device output into clipping-region data.
- It depends on device and clipping-path internals rather than public PostScript APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzacpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzcpath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzcpath.h

Defines internal clipping-path structures.

Key points:
- `gx_clip_rect_list` wraps a reference-counted `gx_clip_list`.
- `gx_cpath_path_list` records full source paths and fill rules for high-level output of path intersections.
- `gx_clip_path` subclasses `gx_path`, adding local rectangle list, rule, inner/outer boxes, shared rectangle list, path validity flag, path-list chain, and change id.
- Includes GC descriptor macros for clip rectangle lists, path lists, clip paths, and clip-path enumerators.
- Defines `gs_cpath_enum_s`, which can enumerate either a path representation or a rectangle-list representation.
- `gx_cpath_is_shared` tests shared rectangle-list ownership through refcount.

Research notes:
- Clip paths maintain both geometric path and rectangle-list forms when needed.
- Lifetime is split between the path representation and the clip list, each with separate sharing concerns.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzcpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzht.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzht.h

Declares internal halftone construction, sampling, cache, and installation APIs.

Key points:
- Provides allocation and construction functions for spot, threshold, client, and bit-level halftone orders.
- Defines `gs_screen_enum_s` for screen sampling, including supplied halftone, generated order, matrices, strip/shift state, and graphics state.
- Declares screen-order initialization and full screen-plane processing helpers.
- Defines `gx_ht_cache`, which stores cached rendered halftone tiles, cache sizing metadata, copied order, and render callback.
- Defines cache sizing constants for small/large memory modes and tile cache byte limits.
- Provides fractional-color rounding helpers and a small lookup table for low denominators.
- Declares cache allocation/free/init/currentness checks, tile-size checks, tile rendering, order release, device-halftone installation, and transfer-function recomputation.
- Declares colorant-name mapping helpers for halftone dictionaries.

Research notes:
- This is a central internal header for halftone lifecycle and cache performance.
- The cache design deliberately stores only selected rendered levels, sliding cached tiles instead of storing all `P+1` possibilities.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzline.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzline.h

Declares internal line-parameter support.

Key points:
- Includes `gxline.h` for `gx_line_params`.
- Defines `private_st_line_params`, a complex GC descriptor for line parameters.
- The descriptor must avoid following the dash pattern pointer when dash pattern size is zero.
- Declares `gs_currentlineparams` for accessing line parameters from an imager state.

Research notes:
- The main behavior is in `gsline.c`/`gsistate.c`; this header isolates GC and accessor details.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzpath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzpath.h

Defines Ghostscript’s internal path representation and path helper APIs.

Key points:
- Paths are linked lists of `segment` objects: start, line, close-line, and Bezier curve.
- `segment_common` stores previous/next links, type, notes, and endpoint.
- `subpath` is a start segment that owns the current subpath’s last segment, curve count, temporary closer, and closed flag.
- Curve helpers convert between control points and cubic coefficients and support flattening, monotonic splitting, and subdivision.
- Path state flags track current point validity, open subpath state, drawing state, and out-of-range coordinates.
- `gx_path_segments` carries reference-counted shared segment ownership.
- `gx_path_s` stores allocator, allocation mode, segment ownership, bbox, current position, counts, state flags, and virtual path procedure table.
- Declares GC descriptors for path segments, paths, and path enumerators.
- Defines inline helpers for shared/void/curve checks and current-point retrieval.
- Defines `gx_flattened_iterator_s` and functions for forward/backward iteration over flattened curves or lines.

Research notes:
- This is one of the core geometry data structures in the graphics library.
- Segment sharing and stack-contained temporary paths are explicit design concerns.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.c

Implements the spot analyzer device used for spot topology analysis and TrueType-style vertical stem recognition.

Key behavior:
- Defines GC descriptors for the analyzer device, trapezoid records, and trapezoid contact records.
- Implements freelist/buffer management for trapezoids and contacts, with hard caps around 10000 allocations per buffer type.
- Provides cyclic-list helpers for Y-band trapezoid lists and contact lists.
- Defines a minimal Ghostscript device descriptor named `spot analyzer`; most device procs are null except open, close, clipping box, fill path, and copy finalization hooks.
- `san_open` initializes buffers and x-extents; `san_close` frees buffers.
- `gx_san__obtain` allocates/opens the device and uses a lock count; `gx_san__release` decrements and releases when no longer used.
- `gx_san_begin` resets current topology state and reuses existing buffers through freelists.
- `gx_san_trap_store` accepts trapezoids in increasing Y-band and X order, builds upper/lower contact topology, tracks leftmost/rightmost boundaries, and updates global x extents.
- `try_unite_last_trap` merges adjacent prolongation trapezoids when topology and outline boundaries match.
- Stem detection uses trapezoid area/axis length to estimate average width and rejects nearly horizontal boundaries using tangent/cosine checks.
- Hint generation has two modes internally: by selecting representative trapezoid width or by selecting outline tangents; the active path uses tangent-based hints.
- Overall hints identify leftmost/rightmost outer glyph boundaries when requested.
- Stem hints follow single-descendent/single-ancestor contiguous trapezoid chains and call a client handler with `gx_san_sect`.
- Visual tracing hooks draw trapezoids, contacts, stems, and hints when enabled.

Research notes:
- The implementation assumes the trapezoid fill algorithm emits trapezoids in a strict scanning order.
- GC comments note that only buffer links are valid during collection; topology work pointers are transient.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.h

Declares the spot analyzer device, trapezoid topology structures, and stem-generation API.

Key points:
- Describes the device as analyzing trapezoid-fill output for glyph grid fitting and antialiased rendering support.
- `gx_san_trap` stores geometry, outline boundary segment pointers, directions, topology contacts, band-list links, and stem-recognition flags.
- `gx_san_trap_contact` represents neighbor relationships across band boundaries as cyclic lists.
- `gx_san_sect` is the output stem/hint section with endpoints, outline segment pointers, and side mask.
- `gx_device_spot_analyzer` embeds a device plus lock count, trapezoid/contact buffers and freelists, topology reconstruction state, and global x extents.
- Provides GC descriptor macros with restricted pointer tracing assumptions.
- Declares obtain/release, begin, trapezoid storage, end, and stem generation functions.

Research notes:
- This is a private graphics helper rather than a display device.
- The API is callback-driven for extracted stem sections.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzstate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzstate.h

Defines the private Ghostscript graphics state structure.

Key points:
- `gs_state_s` starts with `gs_imager_state_common`, making imager state the base layout.
- Stores saved-state chain, CTM inverse/default state, current path, clip path, clip stack, view clip, and effective clip cache.
- Holds color space, client color, and cached device color.
- Tracks current font, root font, character matrix, cachedevice/charpath modes, and show-state linkage.
- Stores gsave level, current device, device filter stack, transparency group stack, and client callbacks.
- Defines `gs_device_filter_stack_s` here so gstate lifecycle code can access reference counts.
- Provides GC descriptor declaration and `gs_state_do_ptrs` pointer enumeration macro.
- Defines `gx_setcurrentpoint` development macro.

Research notes:
- This is the internal state object tying paths, clipping, color, font, device, and transparency together.
- Device pointer handling is called out as special in GC enumeration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gzstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.c

Implements the interpreter allocator interface over Ghostscript reference memory spaces.

Key behavior:
- `ialloc_init` creates local, stable-local, system, and optionally global/stable-global `gs_ref_memory_t` allocators.
- Level 1 mode aliases global VM to local VM; Level 2 mode creates distinct local/global spaces.
- Initializes VM space tags, optional pointer-stability IDs, GC reclaim hook, and current allocation space.
- Provides accessors for allocator space, new mask, and save level.
- `ialloc_set_space` selects current VM by indexed space.
- `ialloc_reset_requested` clears GC request causes across system/global/local spaces.
- `gs_register_ref_root` registers ref roots with the GC.
- `gs_alloc_ref_array` allocates arrays of `ref` with an extra terminating mark ref for GC relocation metadata; it can extend the current ref run when possible.
- `gs_resize_ref_array` only supports shrinking and handles LIFO shrink specially, otherwise records lost space.
- `gs_free_ref_array` frees only LIFO arrays or large arrays occupying a whole chunk; otherwise nulls references and records lost storage.
- `gs_alloc_string_ref` allocates a byte string and wraps it in a string ref with current space attributes.

Research notes:
- Ref arrays have interpreter-specific GC layout requirements beyond generic heap allocation.
- Much of the code is optimized for stack-like allocation patterns while preserving PostScript save/restore behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.h

Declares interpreter allocator access macros and APIs.

Key points:
- Defines current interpreter memory aliases through `i_ctx_p->memory`, including local/global/system spaces.
- Provides convenience wrappers for allocating/freeing bytes, structs, arrays, strings, and const objects through current interpreter memory.
- Declares `ialloc_init`, requested-GC reset, memory validation, VM-space accessors, and allocation-space selection.
- When refs are known, defines wrappers for ref-array allocation/resizing/freeing and string-ref allocation.
- Defines `make_istruct*` and `make_iastruct*` helpers that tag structures with the current VM space.

Research notes:
- This header is the main shorthand layer used by interpreter code.
- It hides the dual-memory structure but keeps VM-space semantics visible through attributes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ialloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.c

Implements the public Ghostscript interpreter embedding API.

Key behavior:
- Maintains a static instance counter with max 1; multiple instances are explicitly unsupported.
- `gsapi_revision` fills product/copyright/revision fields and supports size probing.
- `gsapi_new_instance` initializes malloc memory, allocates a main instance, stores it in `gs_lib_ctx`, installs caller handle, clears callbacks, and returns the library context.
- `gsapi_delete_instance` clears callbacks/display pointer and decrements the counter, but comments note real deletion is not occurring and thread readiness is doubtful.
- Provides setters for stdio callbacks, poll callback, and display callback.
- `gsapi_init_with_args` delegates to `gs_main_init_with_args`.
- Run-string APIs wrap `gs_main_run_string_*`, using the instance’s `error_object`.
- `gsapi_run_file` delegates to `gs_main_run_file`.
- `gsapi_exit` calls `gs_to_exit`.
- `gsapi_set_visual_tracer` installs a global visual tracer pointer.

Research notes:
- The implementation is an embedding facade over `gs_main_instance`.
- The single-instance limitation is enforced in both code and comments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.h

Declares the public Ghostscript interpreter API for DLL/static embedding.

Key points:
- Defines platform-specific export and calling-convention macros for Windows, OS/2, Mac, and generic builds.
- Declares `gsapi_revision_t`.
- Warns prominently that only one Ghostscript instance is supported.
- Declares instance lifecycle, stdio callbacks, poll callback, display callback, interpreter initialization, string/file execution, exit, and visual tracer APIs.
- Documents callback contracts and return-code behavior for initialization and run functions.
- Provides function pointer typedefs for dynamic loading.

Research notes:
- This is a public ABI header, so calling convention correctness is emphasized.
- The comments encode important lifecycle rules: call `gsapi_exit` after initialization and before deleting an instance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iastate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iastate.h

Collects interpreter allocator-state headers.

Key points:
- Includes `gxalloc.h`, `istruct.h`, and `ialloc.h`.
- Has no independent structs or functions.

Research notes:
- This is a compatibility/convenience aggregation header for allocator state users.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iastate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iastruct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iastruct.h

Collects interpreter memory-manager implementation structure headers.

Key points:
- Includes `gxobj.h` and `ialloc.h`.
- Defines no new declarations beyond the include guard.

Research notes:
- This is a thin aggregation header retained for source organization and dependency compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iastruct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.c

Implements Level 2 encoded-number array/string decoding.

Key behavior:
- Defines `enc_num_bytes` table from header constants.
- `num_array_format` validates encoded number strings or recognizes regular arrays/packed arrays.
- Encoded number strings must start with byte value 149, contain a valid format byte, and have a count matching payload length.
- `num_array_size` returns element count for encoded strings or ordinary arrays.
- `num_array_get` reads from either a normal array or encoded number string; only integer/real array elements are accepted.
- `sdecode_number` decodes fixed-point 16/32-bit integers or real floats according to format and binary scale.
- Short/ushort/long decoders honor big/little endian format bits.
- `sdecodefloat` handles native floats directly or converts IEEE float bits on non-IEEE platforms.

Research notes:
- It emulates Adobe behavior for binary object sequences through format handling in the companion header.
- The array path and encoded-string path converge on returning integer/real refs or errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.h

Defines encoded-number constants and decoder declarations.

Key points:
- Enables `BYTE_SWAP_IEEE_NATIVE_REALS` to emulate an Adobe interpreter byte-swapping bug for native IEEE reals.
- Defines encoded number array marker byte `149`.
- Defines PostScript number formats for int32, int16, IEEE/native float, and byte-order bits.
- Provides validity and byte-count helpers, including `num_array` as a special format for ordinary arrays.
- Declares format detection, size, element extraction, and low-level numeric decoders.

Research notes:
- Constants match PostScript Language Reference binary object formats.
- The header separates external format policy from decoder implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ibnum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iccfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iccfont.c

Implements initialization support for compiled fonts.

Key behavior:
- Defines string and key enumerators for compact compiled-font key/value arrays.
- `cfont_next_string` decodes compact string arrays, including null markers and object-from-string markers.
- `cfont_put_next` creates dictionary entries from encoded keys or string keys and stores supplied values.
- Provides helpers to create dictionaries with general refs, string/null values, or scalar/array number values.
- Provides helpers to create name arrays, string arrays, scalar arrays, names, and parsed refs from strings.
- Parsing uses scanner state and a string stream to convert compact text to a PostScript object.
- Builds a `cfont_procs` procedure vector passed to compiled-font initialization code.
- Defines `.getccfont`, returning font count for null input or constructing a selected compiled font object for an integer index.
- Validates compiled font procedure table version through `ccfont_fprocs`.
- Registers operator table `ccfonts_op_defs`.

Research notes:
- This file bridges generated compiled-font C data into live interpreter refs.
- It uses interpreter allocation and dictionary APIs, so save/VM attributes are part of object creation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iccfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iccinit0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iccinit0.c

Defines the non-compiled initialization string.

Key points:
- Includes `stdpre.h`.
- Exports `gs_init_string` as a single zero byte.
- Exports `gs_init_string_sizeof` as zero.
- Comment notes `gsmain.c` recognizes an empty init string specially.

Research notes:
- This is configuration data, not logic.
- It represents the build mode where initialization is not embedded as compiled PostScript content.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iccinit0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icclib.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icclib.mak

Partial makefile for building Graeme W. Gill’s icclib inside Ghostscript.

Key points:
- Requires build variables for Ghostscript source, icclib source, generated intermediate files, and object directory.
- Notes the tested icclib version is 2.0 and defines `ICCPROFVER=9809`.
- Builds path variables for source, generated, and object outputs.
- Defines ICC include and compiler flags through Ghostscript make variables.
- Provides clean targets for generated `.dev` files and ICC object files.
- Builds `icclib.dev` from `icc.$(OBJ)` using `SETMOD`.
- Defines ICC header dependencies and compile rule for `icc.c`.

Research notes:
- This is build integration for a third-party ICC profile library.
- Comments admit the clean rule is broad and should delete generated/object files more selectively.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icfontab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icfontab.c

Builds the compiled-font procedure table.

Key points:
- Includes `ccfont.h`.
- Uses `gconfigf.h` or `GCONFIGF_H` to declare compiled-font procedures via `font_` macros.
- Builds `fprocs[]`, a null-terminated array of compiled font initializer function pointers.
- `ccfont_fprocs` returns the number of procedures, the table pointer, and `ccfont_version`.

Research notes:
- This file is compiled and linked with compiled fonts, possibly in a shared library.
- Compatibility is checked by returning the font ABI version.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icfontab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar.h

Declares shared character rendering operator support.

Key points:
- Documents execution-stack layout used by character rendering operators.
- Defines `snumpush` as 9 and macros for retrieving text enumerator, procedure slot, saved stack depths, saved gstate level, saved font/root font, and completion procedure from the execution stack.
- Declares show setup, continuation, dispatch, cleanup, glyph ref creation, and `stringwidth` finish helpers.
- Declares cachedevice operators and width-only show query.

Research notes:
- Character rendering in the interpreter is continuation-based through the execution stack.
- The macros encode a fixed stack-frame ABI shared by `zchar*.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar1.h

Declares Type 1 / Type 2 character rendering interfaces.

Key points:
- Forward-declares `gs_font_type1`.
- Declares `charstring_execchar`, the implementation behind `.type1execchar` / `.type2execchar` style operators.
- Declares glyph-outline procedure for Type 1/2 fonts.
- Declares `zcharstring_outline` for extracting outlines from CharString data, including CIDFontType 0 use.
- Declares glyph info helpers, including a generic WMode-aware variant.
- Declares `z1_set_cache` for Type 1 glyph cache setup.

Research notes:
- This header connects interpreter font operators to Type 1/Type 2 charstring interpretation and cache setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icharout.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icharout.h

Declares outline character output helpers.

Key points:
- Declares execution of a character procedure-defined outline.
- Defines `metrics_present` enum for no metrics, width-only, and sidebearing-plus-width cases.
- Declares helpers to retrieve `Metrics`, `Metrics2`, and `CDevProc` entries from base fonts.
- Declares `zchar_set_cache`, which consults metrics/CDevProc and calls `setcachedevice`/`setcachedevice2`, possibly scheduling a continuation.
- Declares CharString data extraction for glyphs.
- Declares glyph enumeration over a dictionary through `dict_first`/`dict_next`.

Research notes:
- This is the shared boundary between font dictionaries, character cache setup, and outline execution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icharout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icid.h

Declares CID font support helpers.

Key points:
- Forward-declares `gs_cid_system_info_t`.
- Declares parsing of `CIDSystemInfo` dictionaries.
- Declares CID-to-TrueType character code or glyph index conversion using `Decoding`, `TT_cmap`, and `SubstNWP`.
- Declares CIDMap construction from TrueType cmap data, decoding, substitution, and `GDBytes`.
- Declares `.type9mapcid` operator entry point.

Research notes:
- This header supports CID-keyed font mapping, especially TrueType-backed CID handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icie.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icie.h

Declares internal interpreter helpers for CIE color spaces and rendering dictionaries.

Key points:
- Provides dictionary parameter readers for ranges, 3-range sets, 3x3 matrices, procedure arrays, 3-procedure arrays, WhitePoint/BlackPoint, and lookup tables.
- Declares `cie_set_finish` for completing color-space setup.
- Declares cache preparation helpers that sample PostScript procedures into CIE caches via continuations.
- Provides macros for 3- and 4-component cache preparation.
- Declares `cie_cache_joint`, used between CIE color space and color rendering dictionary setup.

Research notes:
- These APIs bridge PostScript dictionary/procedure data into graphics-library CIE color caches.
- Many functions are exported between `zcie.c` and `zcrd.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icolor.h

Declares transfer-function and color remapping cache helpers.

Key points:
- Exports required operand and execution stack slot counts for `zcolor_remap_one`.
- Declares `zcolor_remap_one`, which schedules sampling/reloading of a transfer map or recognizes special procedures.
- Declares finish routines for `[0..1]` and `[-1..1]` cache reloads.
- Declares helpers to recompute effective transfer functions and invalidate current color after remapping.

Research notes:
- This is interpreter glue for procedure-driven color cache construction.
- The scheduling contract always returns through continuation mechanics when remapping is handled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iconf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iconf.c

Builds configuration-dependent interpreter tables.

Key points:
- Defines `gs_main_instance_init_values` from default initializer macros.
- Uses `gconf.h` macro expansions to build init `.ps` filename refs and emulator-name refs.
- Declares and builds the function type table from configured function builders.
- Declares and builds the operator definition table, always including `interp_op_defs`.
- Declares and builds the plugin instantiation table from configured plugins.
- The string ref arrays use foreign readonly strings and are terminated by a null string entry.

Research notes:
- This is generated-configuration glue driven by `gconf.h`.
- `iconfig.c` in this group has the same content under a different filename.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iconf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iconf.h

Declares interpreter configuration imports.

Key points:
- Exports `gs_init_string` and `gs_init_string_sizeof` from `iccinit[01].c`.
- Exports `gs_init_file_array` and `gs_emulator_name_array` from `iconf.c`.

Research notes:
- This is a small aggregation header for configuration data used during initialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iconfig.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iconfig.c

Builds configuration-dependent interpreter tables.

Key points:
- Content matches `iconf.c`.
- Defines default main-instance values.
- Builds init-file and emulator-name ref arrays from `gconf.h`.
- Builds function type, operator definition, and plugin instantiation tables.
- Terminates generated arrays with sentinel entries.

Research notes:
- This appears to be a duplicate or alternate build-name variant of `iconf.c`.
- Its role is configuration-table generation, not runtime algorithm implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.c

Implements interpreter context state allocation, load, store, and free operations.

Key behavior:
- Defines GC clear-mark, enumerate, and relocate procedures for `gs_context_state_t`, including embedded dual memory and stack objects.
- `context_state_alloc` allocates the context in local VM if needed, allocates interpreter stacks, initializes dictionary stack systemdict, allocates graphics state, copies memory state, initializes language/user/runtime fields, creates `userparams`, initializes bogus stdio file refs, and increments VM context counts.
- `context_state_load` switches references from systemdict to context-local objects using `userdict.localdicts`, installs saved `userparams`, calls `set_user_params`, restores save-check state, clears execution-stack cache, and refreshes dictionary-stack top cache.
- `context_state_store` cleans dictionary/exec/operand stacks and saves `systemdict.userparams` into the context.
- `context_state_free` decrements VM context counts and either reports freed VM spaces or frees graphics state and interpreter stacks.
- Graphics state freeing uses `grestoreall`, pointer patching for the final restore, and `gs_state_free`.

Research notes:
- Context switching is tightly coupled to systemdict/userdict and local/global VM semantics.
- Some cleanup paths are marked with comments for freeing whole VM spaces or userparams, suggesting implementation gaps or higher-level ownership.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.h

Declares externally visible interpreter context-state operations.

Key points:
- Includes `icstate.h` and declares GC descriptor `st_context_state`.
- Declares `set_user_params`, supplied by user-parameter implementation variants.
- Declares context allocation, load, store, and free APIs.
- Context allocation is always in local VM and can either allocate the state object or fill an existing one.
- Context free returns a mask of VM spaces freed.

Research notes:
- This header exposes context operations used by interpreter lifecycle and Display PostScript-like context management.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icremap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icremap.h

Defines interpreter color-remapping callback state.

Key points:
- Defines `int_remap_color_info_t`.
- Stores an interpreter remapping procedure and tint values up to `GS_CLIENT_COLOR_MAX_COMPONENTS`.
- Comments note pattern remapping ignores tint values, while DeviceN remapping uses them.
- Provides a simple GC descriptor macro.

Research notes:
- This is small state passed between graphics color remapping and interpreter procedures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icremap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icsmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icsmap.h

Declares shared cached color-space map loading support.

Key points:
- Defines execution-stack frame layout for cached map loading: component count, map object, procedure, hival, and index.
- Declares `zcs_begin_map`, which sets up loading for Indexed or substituted Separation color spaces.
- Accepts an indexed map output pointer, mapping procedure, entry count, direct base color space, and continuation procedure.

Research notes:
- The base parameter is a direct color space because Indexed base spaces may themselves be Separation or DeviceN.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icstate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icstate.h

Defines externally visible interpreter context state.

Key points:
- `gs_context_state_s` stores current graphics state, dual memory, language level, array packing, binary object format, random state, usertime fields, superexec depth, userparams, scanner options, file-permission lock, startup argument-file flag, library path, stdio refs, dictionary/exec/operand stacks, and plugin list.
- The dictionary, execution, and operand stacks are embedded at the end to minimize offsets elsewhere.
- Declares `rand_state_initial`.
- Provides `public_st_context_state` descriptor macro implemented in `icontext.c`.

Research notes:
- This is the interpreter’s per-context state container.
- It combines VM, graphics, scanning, parameter, file, and stack state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/icstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iddict.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iddict.h

Provides dictionary API wrappers using the current interpreter dictionary stack.

Key points:
- Defines `idict_stack` as `i_ctx_p->dict_stack`.
- Wraps `dict_put`, `dict_put_string`, `dict_undef`, `dict_copy`, `dict_copy_new`, `dict_resize`, `dict_grow`, and `dict_unpack` with the current dictionary-stack pointer.
- Includes `idict.h` and `icstate.h`.

Research notes:
- This header removes repetitive `&idict_stack` arguments for operator code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iddict.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iddstack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iddstack.h

Declares the minimal dictionary-stack API needed by dictionary code.

Key points:
- Forward-declares `dict_stack_t`.
- Declares `dstack_set_top`, which refreshes cached top-dictionary lookup values.
- Declares `dstack_dict_is_permanent`, which tests whether a dictionary is one of the permanent stack dictionaries.

Research notes:
- This breaks a dependency cycle between dictionary implementation and dictionary-stack implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/iddstack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.c

Implements debug printing and dumping helpers for interpreter refs, arrays, and stacks.

Key behavior:
- Forces `DEBUG` for this compilation unit.
- Defines type-name string table and references `tx_next_index`.
- Prints names by converting name refs or indexes to string refs.
- `debug_print_full_ref` prints detailed ref type/attributes and payload for arrays, booleans, devices, dictionaries, files, integers, names, op arrays, operators, reals, saves, strings, structs, and unknown types.
- Packed refs are decoded as executable operators, packed integers, literal names, or executable names.
- `debug_dump_one_ref` prints type, access attributes, size, raw value bits, and printable object representation when available.
- `debug_dump_refs` dumps a contiguous ref region.
- `debug_dump_stack` walks a ref stack from top to bottom.
- `debug_dump_array` handles normal, mixed, short packed, and op arrays, expanding packed elements as needed.

Research notes:
- This file is developer diagnostics only and depends on many interpreter internals.
- Struct printing assumes `gsalloc.c` object headers for type discovery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.h

Declares interpreter debugging helpers.

Key points:
- Declares name/ref/packed-ref print functions.
- Declares single-ref, ref-region, array, and stack dump functions.
- Forward-declares `ref_stack_t` when needed.

Research notes:
- This header is only useful in debug-oriented code paths that can include interpreter ref types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.c

Implements Ghostscript’s interpreter dictionary hash table.

Key behavior:
- Defines maximum dictionary size from `max_array_size - 1` and defaults dictionaries to packed keys.
- Rounds dictionary storage size directly on small-memory systems and to powers of two on larger systems unless huge.
- `dict_alloc` creates the dictionary object as refs, stores allocator as foreign struct, and initializes contents.
- Dictionary contents use separate values and keys arrays; keys may be packed shortarray entries or full refs.
- Packed dictionaries use sentinel empty/deleted keys and a wraparound slot.
- `dict_unpack` converts packed keys to full refs when required by unsupported key forms or large name indexes.
- `dict_find` hashes names/strings/integers/reals/other refs, searches packed or unpacked tables with open addressing, returns existing value slot or insertion slot, and reports `dictfull`.
- Strings are converted to names for lookup/insert when readable.
- `dict_put` performs store checks, auto-grows when configured, inserts new keys, updates count, updates single-definition name caches when allowed, and stores values with save tracking.
- `dict_undef` removes entries, marks deleted/empty slots, decrements count, clears name caches, and nulls values.
- Provides length, maxlength, max-index, copy, resize, grow, enumeration, value-index, and index-entry operations.
- Resize rebuilds contents, copies entries, preserves/updates name caches, frees or save-records old arrays, and refreshes dictionary-stack top cache.

Research notes:
- The implementation is tightly coupled to save/restore, GC relocation, name cache optimization, and dictionary-stack caches.
- Packed-name keys are a major fast path, but arbitrary keys force unpacking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.h

Declares the dictionary package interface and exposes first-level dictionary layout.

Key points:
- `dict_s` stores `values`, `keys`, `count`, `maxlength`, and allocator `memory` refs.
- Exposes layout to support fast access checking and lookup.
- Declares `dict_max_size` and `dict_auto_expand`.
- Declares allocation, access-ref helpers, read/write checks, find, string-find, put, string-put, undef, length, capacity, max index, copy, resize, grow, unpack, enumeration, and index lookup functions.
- Documents error behavior for lookup, insertion, copy, resize, and enumeration.
- Defines hash and rounding helpers, with different small/large memory behavior.
- Defines `dict_max_non_huge` threshold and explains huge dictionary fallback.

Research notes:
- This public internal header intentionally leaks representation for speed.
- Hashing assumes name indexes are already sufficiently scattered.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idict.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idictdef.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idictdef.h

Defines dictionary implementation internals and packed-key search macros.

Key points:
- Documents dictionary structure: keys, values, count, maxlength, and memory refs.
- Explains distinction between client capacity `C` and allocated slots `M`, including power-of-two rounding.
- Defines packed and unpacked key marker conventions for empty and deleted entries.
- Notes the first entry is always deleted to reduce wraparound cost.
- Defines helpers for packed-state checks, packed key sentinels, packed name keys, length/capacity/slot counts.
- Provides split packed-search macros used by both dictionary and dictionary-stack lookup code.

Research notes:
- This is included by implementation and high-performance clients.
- The macros intentionally expose free variables, so callers must set up names exactly as expected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idictdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.c

Implements display-device callback installation for the interpreter API.

Key behavior:
- `display_set_callback` runs PostScript to test whether `devicedict /display` exists and retrieve the display device.
- If present, verifies stack types, gets the device, closes it if already open, installs the callback pointer in `gx_device_display`, and reopens it if needed.
- Pops the temporary device and boolean results from the operand stack.
- Returns success when display device is absent.

Research notes:
- This is only used when `gsapi_set_display_callback` is called and the display device is included.
- It bridges API-level display callbacks into the actual device instance after initialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.h

Declares display callback installation support.

Key points:
- Forward-declares `display_callback`.
- Declares `display_set_callback(gs_main_instance *, display_callback *)`.

Research notes:
- Called from main interpreter setup to push API display callbacks into the display device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idosave.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idosave.h

Declares low-level save-recording helpers for restore support.

Key points:
- `alloc_save_change` and `alloc_save_change_in` record changes that must be undone by `restore`.
- APIs take the containing object ref and the changed ref/packed-ref pointer.
- Comments explain the container is needed to choose the correct VM saved-change chain and to trace/relocate change records during GC.

Research notes:
- This is foundational for PostScript save/restore semantics over arrays, dictionaries, and structs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idosave.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.c

Implements utilities for extracting typed parameters from dictionaries.

Key behavior:
- Boolean, integer/null, integer, unsigned integer, and float getters apply defaults, type checks, range checks, and missing-key behavior.
- Integer getters accept integral real values for compatibility with Fontographer-generated output.
- Integer array helpers support exact-length, max-length, and custom under/over error variants.
- Float array helpers handle array-like refs, optional defaults, and exact/max length behavior.
- `dict_proc_param` validates procedures or supplies invalid/empty defaults.
- `dict_matrix_param` reads a matrix from a dictionary value.
- `dict_uid_param` extracts XUID in Level 2 mode or UniqueID otherwise, allocating XUID value arrays and treating UniqueID 0 as invalid for Fontographer compatibility.
- `dict_check_uid_param` verifies a dictionary UID matches an existing UID.

Research notes:
- These helpers centralize PostScript dictionary parameter validation and defaulting.
- Return conventions distinguish found, defaulted, null, and error cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.h

Declares dictionary parameter extraction helpers.

Key points:
- Forward-declares `gs_matrix` and `gs_uid`.
- Documents common return convention: 0 valid, 1 defaulted, negative error; null-aware routines return 2 for null.
- Notes dictionary keys are passed as C strings to avoid GC concerns over static name refs.
- Declares scalar, array, procedure, matrix, UID, and UID-checking functions.
- Documents array helper variants for custom under/over errors, max length, and exact length.

Research notes:
- This is a shared validation layer for font, color, device, and interpreter parameter dictionaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idsdata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idsdata.h

Defines the generic dictionary stack structure.

Key points:
- `dict_stack_t` embeds a `ref_stack_t` of dictionaries.
- Tracks `min_size`, the stack size after clearing.
- Tracks `userdict_index` because Level 1/Level 2 switching substitutes globaldict behavior without changing minimum stack size.
- Caches `def_space` to quickly decide whether `def` can store a value into the top dictionary.
- Caches packed top-dictionary keys, pair count, and values for fast lookup.
- Stores a cached copy of the bottom system dictionary.
- Provides GC descriptor macro as a suffix of `ref_stack_t`.

Research notes:
- The top-entry caches are recomputed after GC, so they are intentionally not declared as GC pointers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idsdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.c

Implements dictionary-stack lookup and cache maintenance.

Key behavior:
- In debug builds, gathers lookup/probe/depth statistics.
- `dstack_dict_is_permanent` checks whether a dictionary appears in the permanent bottom portion of the dictionary stack, handling single-block and extended stacks.
- `dstack_find_name_by_index` searches dictionaries from top to bottom for a name index.
- Packed dictionaries use the same packed-search macros as `idict.c`; unpacked dictionaries probe full ref keys.
- If the current stack block misses and extensions exist, slower `dict_find` searches remaining stack entries.
- `dstack_set_top` caches packed key/value pointers and pair count for readable packed top dictionaries, otherwise installs dummy packed keys; it also caches `def_space`.
- `dstack_gc_cleanup` scans permanent dictionaries after GC and relocates cached single-definition name value pointers.

Research notes:
- This file is a performance-critical companion to dictionary implementation.
- The inline fast path in the header is backed by this full-stack search.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.h

Declares generic dictionary-stack APIs and fast lookup macros.

Key points:
- Defines dictionary stack pointer aliases `ds_ptr` and `const_ds_ptr`.
- Declares GC cleanup and full name-index lookup.
- Defines `dstack_find_name_by_index_inline`, an optimized top-dictionary single-probe lookup that falls back to full search.
- Defines `if_dstack_find_name_by_index_top`, a macro that only checks the top dictionary.
- Includes dictionary-stack data and generic stack headers.

Research notes:
- The inline lookup is tuned for common interpreter name lookup, with comments claiming over 90 percent top-dictionary single-probe hits outside operator handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/idstack.h -->