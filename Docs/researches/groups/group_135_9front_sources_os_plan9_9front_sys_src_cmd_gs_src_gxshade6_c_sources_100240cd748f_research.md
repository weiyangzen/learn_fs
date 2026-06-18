# Group Research: group_135_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxshade6_c_sources_100240cd748f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade6.c

Implements Ghostscript rendering for Coons patch and tensor-product patch shadings. It parses mesh patch streams, converts patch geometry into tensor control grids, recursively subdivides curved/color-varying patches, inserts wedge/padding fills to avoid dropouts, and ultimately paints trapezoids or triangles through device procedures.

Key behavior:
- `shade_next_patch` decodes patch flags and shared-edge continuation forms, reading coordinates, optional tensor interior points, and vertex colors.
- `gs_shading_Cp_fill_rectangle` and `gs_shading_Tpp_fill_rectangle` initialize mesh/patch fill state, iterate patch records, and call `patch_fill`.
- `Cp_transform` evaluates Coons patches; `Tpp_transform` evaluates tensor-product patches with Bernstein polynomials.
- `init_patch_fill_state` derives color domains, flatness, smoothness, linear-color flags, and optional lazy-wedge storage.
- `patch_fill` builds a normalized `tensor_patch`, optionally informs vector devices of shading coverage, computes sample counts from curve flatness/coordinate limits, fills boundary wedges, and recursively fills the patch body.
- Geometry is decomposed through stripes, quadrangles, triangles, wedges, and trapezoids; code handles axis swapping, semi-open raster intervals, self-intersection checks, monotonicity tests, and fixed-point overflow limits.
- Color handling supports direct vertex colors or function-evaluated parameter colors, monotonicity tests, linearity checks, device accelerated `fill_linear_color_triangle` / `fill_linear_color_trapezoid`, and fallback constant-color subdivision.
- `gx_shade_background` fills a background rectangle as one trapezoid expanded by interpatch padding.

Dependencies:
- Mesh and shading infrastructure from `gxshade.h` and `gxshade4.h`.
- Device painting hooks: `fill_trapezoid`, `fill_path`, `fill_linear_color_triangle`, `fill_linear_color_trapezoid`, and `pattern_manage`.
- Color-space remapping and function evaluation through Ghostscript color APIs.
- Fixed-point path/curve helpers from `gzpath.h`, `gxarith.h`, and curve sampling utilities.
- Debug visualization through `vdtrace.h`.

Research notes:
- This is numerically dense rendering code. It relies heavily on fixed-point arithmetic, selected `int64_t` products, and subdivision limits to keep intersection math bounded.
- The file documents known coverage tradeoffs around transposed trapezoids, self-overlap, wedges, and semi-open scan conversion.
- Several branches are guarded by compile-time feature macros such as `LAZY_WEDGES`, `QUADRANGLES`, `INTERPATCH_PADDING`, `USE_LINEAR_COLOR_PROCS`, and debug/test flags.
- Some repeated orientation checks in `is_x_bended` and `is_y_bended` look copy/pasted, but the surrounding logic is conservative and mainly detects possible bending/self-overlap.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstate.h

Internal Ghostscript graphics-state API used mainly by interpreter and state-management code.

Key declarations:
- Opaque `gs_state` forward declaration.
- Accessors for graphics-state memory, saved state, saved-state swapping, and allocator swapping.
- Client-data hooks: allocate, copy, free, and reason-aware `copy_for`.
- `gs_state_copy_reason_t` distinguishes `gsave`, `grestore`, `gstate`, `setgstate`, `copygstate`, and `currentgstate` copy contexts.
- `gs_state_set_client` installs client state and notes whether client data owns pattern streams.
- `gs_state_client_data` accessor is declared unless overridden by `gzstate.h`.
- `gx_get_clip_path_id` exposes the current clip path identifier.

Dependencies:
- Includes `gscspace.h` for graphics/color state context and common Ghostscript types.

Research notes:
- The comments explicitly mark this as unstable internal API, not a public embedding contract.
- The non-const `from` argument in `copy_for` is deliberate for clients that mutate or lazily normalize copied data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstdio.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstdio.h

Provides a stdio “back door” for Ghostscript code and contributed drivers.

Key behavior:
- Includes `gsio.h`.
- Undefines C library `stdin`, `stdout`, and `stderr`.
- Redefines them to Ghostscript-managed `gs_stdin`, `gs_stdout`, and `gs_stderr`.
- Undefines `fgetchar`.

Dependencies:
- Depends on Ghostscript I/O redirection definitions from `gsio.h`.

Research notes:
- The file exists for legacy/contributed code that still writes to stdio, even though the core library/interpreter avoid direct stdio use.
- This is preprocessor compatibility glue rather than runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstroke.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstroke.c

Implements Ghostscript path stroking: line-width expansion, cap/join construction, dash expansion, clipping, direct device fills, and strokepath outline generation.

Key behavior:
- `gx_stroke_path_expansion` computes conservative or exact bbox expansion for stroked paths, accounting for CTM, line width, caps, joins, miter limit, triangular joins, and curve joins.
- `gx_default_stroke_path` delegates to `gx_stroke_path_only`.
- `gx_stroke_path_only_aux` is the main engine. It computes orientation/reflection, expands and clips the path bbox, flattens curves, expands dashes, handles degenerate subpaths, computes segment widths, and emits either fills or path outlines.
- Optimized cases draw thin lines with `draw_thin_line` or fill bevel/miter bodies directly using `fill_triangle` and `fill_parallelogram`.
- General cases construct stroke outline paths through `stroke_add`, then fill them.
- Handles round, butt, square, and triangular caps, plus bevel, round, miter, triangle, and no-join behavior.
- `line_join_points` computes bevel/miter/triangle join points with miter-limit checks and optional inverse distance transforms for non-uniform CTMs.
- `add_round_cap` builds a full circular cap with four partial arcs.

Dependencies:
- Uses imager and line state from `gxistate.h` / `gzline.h`.
- Uses path internals from `gzpath.h`, clipping from `gzcpath.h`, and painting from `gxpaint.h`.
- Uses device procedures such as `draw_thin_line`, `fill_triangle`, `fill_parallelogram`, and clipping-device wrappers.
- Uses visual debug tracing through `vdtrace.h`.

Research notes:
- Degenerate subpaths are treated carefully: round caps can paint dots, while other caps generally do not, matching PostScript stroke behavior.
- The code has several performance-specialized branches for portrait/landscape/uniform transforms and idempotent raster operations.
- Comments acknowledge historical uncertainty around fill adjustment for strokes and orientation optimizations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxstroke.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.c

Implements Ghostscript wrappers over platform synchronization primitives.

Key behavior:
- `gx_semaphore_alloc` computes the actual platform semaphore storage size, chooses movable or immovable Ghostscript allocation based on `gp_semaphore_open(0)`, initializes the native semaphore, and records the allocator.
- `gx_semaphore_free` closes the native semaphore and frees the wrapper.
- `gx_monitor_alloc` does the same for platform monitor objects using `gp_monitor_sizeof` and `gp_monitor_open`.
- `gx_monitor_free` closes and frees monitor objects.
- Re-declares the wait/signal and enter/leave macros locally to keep implementation and header signatures consistent.

Dependencies:
- Platform primitives from `gpsync.h` via `gxsync.h`.
- Ghostscript allocation APIs from `gsmemory.h`.
- Error/type support from `gx.h` and `gserrors.h`.

Research notes:
- The wrapper structs place the native platform object last because its true size is platform-dependent.
- Allocation failure and platform-open failure return `NULL`; successful wrappers remember the allocator needed for cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.h

Defines Ghostscript’s synchronization abstraction for semaphores and monitors.

Key declarations:
- `gx_semaphore_t` stores an allocator pointer plus platform `gp_semaphore` storage.
- `gx_semaphore_alloc` / `gx_semaphore_free`.
- `gx_semaphore_wait` and `gx_semaphore_signal` macros delegate to platform primitives.
- `gx_monitor_t` stores an allocator pointer plus platform `gp_monitor` storage.
- `gx_monitor_alloc` / `gx_monitor_free`.
- `gx_monitor_enter` and `gx_monitor_leave` macros delegate to platform primitives.

Dependencies:
- Includes `gpsync.h` for native synchronization types and operations.
- Includes `gsmemory.h` for allocator types.

Research notes:
- Semaphores initialize with count 0; monitors initialize as available/entered count 1.
- Performance matters here, so wait/signal and enter/leave are macros rather than wrapper functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtext.h

Internal support header for Ghostscript device text enumeration.

Key contents:
- Defines `gs_text_returned_t` for client-visible current character, current glyph, and accumulated width.
- Defines composite-font stack structures, including modal and non-modal composite font levels up to `MAX_FONT_STACK`.
- Defines `gs_text_enum_common`, the shared layout embedded by all text enumerator implementations.
- Common enumerator state stores text parameters, target devices, imager state, original/current font, path/color/clip pointers, memory, refcount header, font stack, cached font/matrix pair, indices, CMap status, grid-fitting flags, and returned values.
- Documents the `imaging_dev` hack used by forwarding/bbox devices to account for low-level drawing done by another target.
- Declares GC structure descriptor macro `public_st_gs_text_enum`.
- Declares `gs_text_enum_init` and `gs_text_enum_copy_dynamic`.
- Provides `SHOW_IS_*` macros for text operation tests.
- Defines `gs_text_enum_procs_t` callbacks: `resync`, `process`, `is_width_only`, `current_width`, `set_cache`, `retry`, and `release`.
- Declares `gx_default_text_release`.

Dependencies:
- Includes public text definitions from `gstext.h`.
- Includes reference-count support from `gsrefct.h`.

Research notes:
- Text enumeration is refcounted; implementers must release referenced objects through the release callback path.
- The comments state that no fully generic default `process` implementation exists because text processing must handle path construction, intervention returns, width reporting, font restoration, and cache setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtmap.h

Defines Ghostscript transfer/mapping procedure types.

Key contents:
- Forward-declares abstract `gx_transfer_map`.
- Defines legacy `gs_mapping_proc`, which maps one float value with a transfer-map argument.
- Defines closure-style `gs_mapping_closure_proc_t`, which additionally receives caller-owned procedure data.
- Defines `gs_mapping_closure_t` holding a procedure pointer and data pointer.

Dependencies:
- Uses common Ghostscript scalar types such as `floatp`.

Research notes:
- The same mapping abstraction is used for transfer functions, black generation, and undercolor removal.
- Comments note that `gx_transfer_map` is broader than the name suggests and should probably be renamed to a mapping cache.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttf.h

Declares raw TrueType table layout structures and composite glyph flags.

Key contents:
- Composite glyph flags such as `TT_CG_ARGS_ARE_WORDS`, `TT_CG_HAVE_SCALE`, `TT_CG_MORE_COMPONENTS`, `TT_CG_HAVE_2X2`, and `TT_CG_USE_MY_METRICS`.
- Byte-array structs matching TrueType table layouts:
  - `ttf_head_t`
  - `ttf_hhea_t`
  - `longHorMetric_t`
  - `ttf_maxp_t`
  - `ttf_OS_2_t`
  - `ttf_vhea_t`
  - `longVerMetric_t`

Dependencies:
- Uses Ghostscript `byte` type supplied by the surrounding build headers.

Research notes:
- Fields remain encoded as raw big-endian byte arrays rather than host integers.
- This header is a structural table definition layer, not a parser or interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.c

Bridge between Ghostscript Type 42 font objects and the bundled TrueType interpreter/outliner.

Key behavior:
- Defines GC descriptor for `gx_ttfReader`, intentionally not enumerating `pfont` or `glyph_data` because they may point from global memory to local memory while the interpreter is active.
- Implements `ttfReader` callbacks: EOF, read, seek, tell, error, load glyph, release glyph.
- `gx_ttfReader__Read` reads from either a loaded glyph buffer or the Type 42 font `string_proc`; multi-part string reads are explicitly unimplemented.
- `gx_ttfReader__LoadGlyph` uses `pfont->data.get_outline` and keeps one extra glyph buffer at a time.
- `gx_ttfReader__create`, `destroy`, and `set_font` manage reader lifetime and font binding.
- Debug and warning helpers route TrueType interpreter messages and one-time bad-instruction/patent warnings.
- `gx_ttfMemory` adapts Ghostscript allocators to the TrueType interpreter memory interface.
- `ttfFont__create`, `ttfFont__destroy`, and `ttfFont__Open_aux` create/open interpreter font state, acquire/release shared interpreter and spot-analyzer resources, and map interpreter errors to Ghostscript errors.
- `decompose_matrix` separates glyph size, subpixel origin, post-transform, design-grid decisions, pixel alignment, and grid-fitting mode.
- `gx_ttfExport` adapts outliner callbacks to Ghostscript paths, optionally monotonizing curves for autohinting.
- `grid_fit` uses the Type 1 hinter and spot analyzer as an autohint fallback for Type 42 outlines.
- `gx_ttf_outline` runs the outliner, handles patented/bad-instruction fallback modes, optionally autohints, and appends the resulting outline to a `gx_path`.

Dependencies:
- Type 42 font internals from `gxfont42.h`.
- TrueType interpreter headers: `ttfoutl.h`, `ttfmemd.h`.
- Path, cache, matrix, paint, imager, and Type 1 hinting APIs.
- Spot analyzer from `gzspotan.h`.

Research notes:
- Grid fitting modes are controlled by `gs_currentgridfittt`: no fitting, TT interpreter, design-grid autohint, or TT with autohint fallback.
- `ttfFont__create` has early-return paths after allocating the memory adapter that do not visibly free it if interpreter/spot-analyzer acquisition fails.
- Reader destruction assumes no outstanding loaded glyph buffer; normal flows reset/release it, but `destroy` itself does not call reset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.h

Public bridge header for Ghostscript’s Type 42 / TrueType interpreter integration.

Key contents:
- Includes `ttfoutl.h`.
- Forward-declares `gx_ttfReader` and `gs_font_type42`.
- Defines `struct gx_ttfReader_s`, embedding `ttfReader` plus stream position, error flag, loaded extra glyph index, font pointer, allocator, and glyph-data buffer.
- Documents that `pfont` and `glyph_data` may temporarily point from global memory to local memory and must be null/reset during GC-sensitive periods.
- Declares reader lifecycle and binding functions.
- Declares `ttfFont__create`, `ttfFont__destroy`, `ttfFont__Open_aux`, and `gx_ttf_outline`.

Dependencies:
- TrueType outliner/interpreter types from `ttfoutl.h`.
- Ghostscript font, memory, glyph-data, matrix, scale, and path types from surrounding includes.

Research notes:
- This header defines the ownership boundary between Ghostscript memory management and the TrueType interpreter’s callback-oriented API.
- The GC warning in the struct comment is important: callers must avoid leaving local-memory pointers visible from globally allocated reader objects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.c

Shared support for Ghostscript Type 1 and Type 2 charstring interpreters.

Key behavior:
- Defines GC descriptors for Type 1 font/state objects, including enumeration and relocation of active charstring/subroutine glyph data in the interpreter stack.
- `gs_type1_interp_init` initializes interpreter state, oversampling scales, path/imager/font pointers, control stack, hint state, paint type, and grid-fitting flags.
- `gs_type1_finish_init` prepares fixed CTM coefficients, records character origin, initializes flex/hint offsets, computes character flatness, and marks initialization complete.
- `gs_type1_sbw`, `gs_type1_set_lsb`, and `gs_type1_set_width` set side bearing and width metrics.
- `gs_type1_blend` handles Multiple Master blend values using the font `WeightVector`.
- `gs_type1_seac` starts composite-accent handling by requesting the base character charstring.
- `gs_type1_endchar` either switches from base to accent charstring for `seac`, tolerates missing accent glyphs with a warning, or finalizes fill/flatness state.
- `type1_cis_get_metrics` exports left side bearing and width.
- `gs_type1_piece_codes` scans a Type 1 charstring looking for `seac`, following subroutines and selected othersubr patterns.
- `gs_type1_glyph_info` combines default glyph info, optional `seac` piece extraction, and width/vector extraction by partially interpreting the charstring.
- `gs_font_parent` returns a Type 9 parent font for encrypted Type 1/2 fonts when present.

Dependencies:
- Type 1 font internals from `gxfont1.h` and `gxtype1.h`.
- Charstring constants from `gsccode.h`.
- Matrix, imager, path, hinting, and fixed arithmetic helpers.

Research notes:
- `gs_type1_piece_codes` duplicates parsing logic rather than reusing the full interpreter; comments acknowledge this is unfortunate but simpler than refactoring.
- Some error paths in `gs_type1_glyph_info` return before freeing acquired glyph data, so callers should be cautious around malformed fonts or failed partial interpretation.
- `seac` accent-missing behavior intentionally follows Acrobat-like tolerance by skipping the missing accent without failing the whole glyph.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.h

Private definitions for the Adobe Type 1 / Type 2 charstring interpreter.

Key contents:
- Defines oversampling scale structures `pixel_scale` and `point_scale`, plus rounding helpers.
- Sets Type 2 total stem hint limit to 96.
- Defines `ip_state_t`, the interpreter control-stack frame containing instruction pointer, decryption state, and owning glyph data for GC.
- Defines encrypted/unencrypted charstring byte access macros.
- Forward-declares path and segment internals.
- Defines `gs_type1_state_s`, including:
  - Type 1 hinter state
  - font, imager state, output path, paint type, callback data
  - fixed CTM coefficients, flatness, origin, oversampling scale
  - operand stack and instruction stack
  - initialization, side-bearing, width, hint, `seac`, flex, and transient-array state
- Declares GC structure macro `public_st_gs_type1_state`.
- Defines operand-stack helper macros and number-decoding macros for 1-byte, 2-byte, and 4-byte charstring numbers.
- Declares shared interpreter utilities: finish init, side bearing/width, blend, `seac`, endchar, and metrics extraction.

Dependencies:
- Cryptography/decryption helpers from `gscrypt1.h`.
- Glyph data from `gsgdata.h`.
- Type 1 font definitions from `gstype1.h`.
- Type 1 hinting from `gxhintn.h`.

Research notes:
- The decode macros are low-level and assume the caller has valid charstring bounds/control flow.
- The state struct is shared by Type 1 and Type 2 interpreters, so it carries fields for both classic Type 1 operations and Type 2 transient/hint behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.c

Implements rendering support for Well Tempered Screening device colors.

Key behavior:
- Defines the WTS `gx_device_color_type_t` method table outside unit-test builds.
- `wts_get_samples` dispatches to Screen J or Screen H sample-location logic.
- Screen J sample lookup applies rational affine-like offsets from screen parameters and clamps the run length before screen discontinuities.
- Screen H sample lookup uses a linear search helper to map coordinates into unequal cell partitions.
- `wts_draw` generates a 1-bit halftone tile for a rectangle by comparing shade levels against screen samples.
- `gx_dc_wts_fill_rectangle_1` handles one-component WTS colors by drawing a mono tile and sending it through `copy_mono`.
- `wts_repack_tile_4` combines up to four 1-bit component tiles into chunky 4-bit/nibble color data.
- `gx_dc_wts_fill_rectangle_4` draws per-component tiles, repacks them, and sends them through `copy_color`.
- `gx_dc_wts_fill_rectangle` dispatches between one-component and up-to-four-component paths.
- `gx_dc_wts_equal` compares type, phase, component count, and levels.
- `gx_dc_wts_get_nonzero_comps` reports which WTS levels are nonzero.

Dependencies:
- Device color and halftone internals from `gxdcolor.h`, `gxdht.h`, and `gxwts.h`.
- Device-client APIs from `gxdevcli.h`.
- Imager state and halftone headers.
- Uses C `malloc`/`free` directly for temporary tile buffers.

Research notes:
- `gx_dc_wts_write` and `gx_dc_wts_read` are not implemented and return `unknownerror`.
- Temporary tile allocations are not checked for `NULL` before use, so large rectangles or allocation failure can lead to unsafe behavior.
- Only one-component and up-to-four-component WTS device colors are supported; larger component counts return `-1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.c -->