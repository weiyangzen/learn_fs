# Group Research: group_1573_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxshade6_c_sources__d553d7daac06

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade6.c

Ghostscript renderer for Coons patch and tensor-product patch shadings. It turns shading mesh patch streams into device trapezoids, triangles, wedges, and optionally device-native linear-color fills while preserving contiguous scan conversion as much as possible.

Key behavior:
- `gs_shading_Cp_fill_rectangle` and `gs_shading_Tpp_fill_rectangle` initialize mesh fill state, parse patch records with `shade_next_patch`, and call `patch_fill`.
- `shade_next_patch` handles patch flags 0-3, reuses prior patch edges where allowed by the PDF/PostScript mesh format, reads Bezier boundary control points, optional tensor interior points, and vertex colors.
- `Cp_transform` evaluates Coons patch coordinates from the four boundary curves; `Tpp_transform` evaluates tensor-product patches using Bernstein basis functions and a 4x4 control grid.
- `make_tensor_patch` normalizes both Coons and tensor patches into an internal `tensor_patch` with four corner colors; Coons interiors are synthesized from boundary control points.
- `patch_fill` computes subdivision counts from curve flatness, informs devices that support `pattern_manage__shading_area`, fills interpatch padding/wedges, and recursively decomposes patches.
- The decomposition path uses `fill_patch`, `fill_stripe`, `decompose_stripe`, `fill_quadrangle`, `mesh_triangle`, and triangle helpers to split geometry until it can be painted as constant-color trapezoids or linear-color primitives.
- Wedge logic tracks thin gaps introduced by different curve subdivision levels. With `LAZY_WEDGES`, wedge vertices are pooled and linked so gaps can be filled later without overfilling every subdivision immediately.
- Color handling supports direct interpolated component colors and function-based colors. It tests monotonicity, linearity, and smoothness with `gs_function_is_monotonic`, `cs_is_linear`, `function_linearity`, and `color_span`.
- When possible, it uses device procedures `fill_linear_color_triangle` and `fill_linear_color_trapezoid`; otherwise it recursively decomposes to constant-color trapezoids via `fill_trapezoid`.
- `gx_shade_background` paints a padded rectangular shading background using a trapezoid.

Notable dependencies:
- Mesh/shading infrastructure: `gxshade.h`, `gxshade4.h`.
- Color-space and device color remapping: `gxcspace.h`, `gxdcolor.h`.
- Device procedures: `gxdevcli.h`, especially `fill_trapezoid`, `fill_path`, `pattern_manage`, and linear-color fills.
- Path/fixed-point helpers: `gzpath.h`, `gxarith.h`, `stdint_.h`.

Research notes:
- The file is graphics/rendering code in the Plan 9 vendored Ghostscript tree, not filesystem logic.
- It is heavily fixed-point and `int64_t` oriented. Comments document deliberate limits for `intersection_of_small_bars` and curve subdivision to avoid overflow in self-intersection handling.
- Coverage correctness is central: comments describe semi-open device scan conversion, transposed trapezoids, interpatch padding, dropout prevention, and known double-paint tradeoffs.
- Recursion has safety guards such as `level > 100`, but many paths rely on subdivision heuristics and assertions around lazy wedge buffer sizing.
- There are repeated orientation checks in `is_x_bended` and `is_y_bended`, suggesting copy/paste duplication in a conservative self-overlap detector.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstate.h

Internal Ghostscript graphics-state API header. It forward-declares opaque `gs_state` and exposes internal state memory/save-stack/client-data hooks used primarily by the interpreter.

Key contents:
- Save/memory accessors: `gs_state_memory`, `gs_state_saved`, `gs_state_swap_saved`, `gs_state_swap_memory`.
- Client-data callback types for allocation, copying, freeing, and reason-aware copying.
- `gs_state_copy_reason_t` distinguishes `gsave`, `grestore`, `gstate`, `setgstate`, `copygstate`, and `currentgstate` copy contexts.
- `gs_state_client_procs` groups client callbacks.
- `gs_state_set_client` registers client state and notes whether pattern streams are involved.
- `gs_state_client_data` and `gx_get_clip_path_id` expose stored client data and clipping path identity.

Notable dependencies:
- Includes `gscspace.h` for color-space-related graphics-state types.
- Implementations are in graphics-state source files such as `gsstate.c`.

Research notes:
- The header explicitly says these interfaces are internal and unstable between releases.
- `copy_for` takes a non-const `from` pointer by design because some clients mutate or adjust state during copy operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstdio.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstdio.h

Small Ghostscript compatibility header providing a stdio back door for contributed drivers.

Key contents:
- Includes `gsio.h`.
- Undefines and remaps `stdin`, `stdout`, and `stderr` to Ghostscript-managed `gs_stdin`, `gs_stdout`, and `gs_stderr`.
- Undefines `fgetchar`.

Research notes:
- The comment says the core library and interpreter do not use standard streams directly, but some contributed drivers still write to stdout/stderr.
- This is a portability shim, not a full stdio wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstroke.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstroke.c

Ghostscript path stroking implementation. It converts paths and line parameters into filled stroke outlines or direct device drawing operations, handling line width, dash expansion, caps, joins, clipping, thin lines, and stroke adjustment.

Key behavior:
- `gx_stroke_path_expansion` computes conservative or exact bounding-box expansion for a stroked path based on CTM, line width, caps, joins, miter limit, and path shape.
- `gx_default_stroke_path` delegates to `gx_stroke_path_only`.
- `gx_stroke_path_only_aux` is the main pipeline: computes clipping bounds, flattens curves, expands dashes, detects CTM orientation/uniform scale, computes device-space stroke widths, handles degenerate subpaths, and emits each segment.
- When drawing, `stroke_fill` uses optimized device procedures for thin lines, parallelogram bodies, and bevel triangles where possible; otherwise it falls back to constructing a stroke path.
- When building paths, `stroke_add` appends cap/join outlines to `to_path`, including round caps and round joins.
- `line_join_points` implements bevel, miter, triangle, and no-join behavior, including miter-limit checks under non-uniform transforms.
- `adjust_stroke`, `width_is_thin`, and `set_thin_widths` implement pixel-aligned stroke adjustment and minimum-width handling.
- `compute_caps`, `add_round_cap`, and `cap_points` generate butt, square, round, and triangular cap geometry.

Notable dependencies:
- Path and line internals: `gzpath.h`, `gzline.h`, `gzcpath.h`.
- Device and paint procedures: `gxdevice.h`, `gsdevice.h`, `gxpaint.h`.
- Matrix/fixed arithmetic: `gxmatrix.h`, `gxfixed.h`, `gxfarith.h`.
- Debug visualization hooks: `vdtrace.h`.

Research notes:
- The code deliberately treats zero-width and very thin lines differently from normal fills, because fill adjustment can otherwise make strokes look too heavy or disappear.
- `gx_stroke_path_only` with a non-null output path may still clip against the clipping path, which the file notes is almost never what callers of `strokepath` want.
- The implementation is optimization-heavy and geometry-sensitive; changes can affect exact scan conversion, joins at transformed angles, dash behavior, and degenerate subpaths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxstroke.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.c

Implementation of Ghostscript synchronization primitive allocation wrappers.

Key behavior:
- `gx_semaphore_alloc` computes the real allocation size from `gp_semaphore_sizeof`, chooses movable or immovable allocation based on `gp_semaphore_open(0)`, stores the allocator, and initializes the native semaphore.
- `gx_semaphore_free` closes the native semaphore and frees the wrapper through its recorded allocator.
- `gx_monitor_alloc` does the same for monitor objects using `gp_monitor_sizeof` and `gp_monitor_open`.
- `gx_monitor_free` closes and frees a monitor.
- Wait/signal and enter/leave are macro wrappers in the header, redefined here to check consistency.

Notable dependencies:
- Platform synchronization API: `gpsync.h` via `gxsync.h`.
- Ghostscript allocator APIs: `gsmemory.h`, `memory_.h`.

Research notes:
- The native platform object has implementation-defined size, so the wrapper structs carry a placeholder native field and allocate adjusted byte counts.
- The allocation path handles platforms whose native synchronization objects cannot be moved by using immovable memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.h

Internal synchronization abstraction header for Ghostscript.

Key contents:
- Defines `gx_semaphore_t`, storing the allocator and a platform `gp_semaphore` native object. The comment notes the native field must be last because its actual size is platform-dependent.
- Declares `gx_semaphore_alloc` and `gx_semaphore_free`.
- Defines `gx_semaphore_wait` and `gx_semaphore_signal` as direct macros to platform operations.
- Defines `gx_monitor_t`, storing allocator and platform `gp_monitor`.
- Declares `gx_monitor_alloc` and `gx_monitor_free`.
- Defines `gx_monitor_enter` and `gx_monitor_leave` as macro wrappers.

Notable dependencies:
- `gpsync.h` for platform primitives.
- `gsmemory.h` for allocator types.

Research notes:
- Semaphores are documented as queued counting semaphores initialized with event count 0.
- Monitors are documented as initialized with event count 1, so the first enter succeeds immediately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtext.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtext.h

Internal support header for Ghostscript driver text enumeration and rendering.

Key contents:
- Defines `gs_text_returned_t`, carrying current character/glyph for intervention and accumulated width for width-returning operations.
- Defines composite font stack types `gx_font_stack_item_t` and `gx_font_stack_t`, with `MAX_FONT_STACK` set to 5.
- Defines `gs_text_enum_common`, the shared prefix for text enumerator implementations. It stores immutable text-begin arguments, device/imaging device, imager state, original/current fonts, path/color/clip data, memory, procedure table, reference count, scaling/cache information, composite font stack, CID/FMapType state, grid-fitting flag, and returned data.
- Defines concrete `struct gs_text_enum_s` as the common structure.
- Declares `gs_text_enum_init` and `gs_text_enum_copy_dynamic`.
- Provides `SHOW_IS*` macros for operation flag checks such as drawing, stringwidth, intervention, replacement widths, and slow show cases.
- Defines `gs_text_enum_procs_t`, the virtual method table for text enumeration: `resync`, `process`, `is_width_only`, `current_width`, `set_cache`, `retry`, and `release`.
- Declares default release procedure `gx_default_text_release`.

Notable dependencies:
- Public text parameters from `gstext.h`.
- Reference counting from `gsrefct.h`.

Research notes:
- The `imaging_dev` field is a documented workaround for forwarding devices such as bbox devices, allowing lower-level drawing operations to be redirected for bounding-box accounting.
- The comments spell out required behavior for text processing: charpath/width path appending, intervention after characters, current-font reset, and width reporting.
- Implementations must call `rc_free_text_enum` from their freeing procedure so device and other referenced structures are released correctly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtmap.h

Small shared header defining Ghostscript transfer/mapping function callback types.

Key contents:
- Forward-declares abstract `gx_transfer_map`.
- Defines legacy `gs_mapping_proc`, taking a value and transfer map.
- Defines closure-style `gs_mapping_closure_proc_t`, taking value, transfer map, and caller data.
- Defines `gs_mapping_closure_t` with a procedure pointer and opaque data pointer.

Research notes:
- The same mapping abstraction is used for transfer functions, black generation, and undercolor removal.
- The comment notes that `gx_transfer_map` should probably be renamed to a more general mapping cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttf.h

TrueType table layout header. It defines byte-accurate structures and flags used to parse TrueType font data.

Key contents:
- Composite glyph flags such as `TT_CG_ARGS_ARE_WORDS`, `TT_CG_ARGS_ARE_XY_VALUES`, `TT_CG_HAVE_SCALE`, `TT_CG_MORE_COMPONENTS`, `TT_CG_HAVE_XY_SCALE`, `TT_CG_HAVE_2X2`, `TT_CG_HAVE_INSTRUCTIONS`, and `TT_CG_USE_MY_METRICS`.
- Table structures for `head`, `hhea`, `hmtx` long horizontal metrics, `maxp`, `OS/2`, `vhea`, and `vmtx` long vertical metrics.
- Fields are stored as `byte` arrays matching the big-endian on-disk TrueType representation rather than native integers.

Research notes:
- This header is a data-layout contract, not a parser.
- Consumers must decode multi-byte fields explicitly; direct native integer access would be incorrect.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.c

Bridge between Ghostscript Type 42 fonts and the bundled TrueType interpreter/outliner. It adapts Ghostscript font data, memory management, and paths to the TrueType interpreter interfaces.

Key behavior:
- Defines GC behavior for `gx_ttfReader`; `pfont` and `glyph_data` are intentionally not enumerated because they may point from global memory to local memory and must be cleared before GC.
- Implements `ttfReader` methods: EOF, read, seek, tell, error, glyph loading, and glyph release.
- `gx_ttfReader__LoadGlyph` asks the Type 42 font for a glyph outline through `get_outline`, maintains one extra glyph buffer, and returns it to the TrueType outliner.
- `gx_ttfReader__Reset`, `create`, `destroy`, and `set_font` manage reader lifecycle.
- `ttfFont__create` adapts Ghostscript memory to `ttfMemory`, obtains a TrueType interpreter and spot analyzer from the font directory, allocates `ttfFont`, and initializes debug callbacks.
- `ttfFont__destroy` finalizes the TrueType font and releases interpreter/analyzer resources.
- `ttfFont__Open_aux` decomposes the character matrix, opens a TrueType font, maps interpreter errors to Ghostscript errors, and records warnings for bad instructions or patented interpreter needs.
- `gx_ttfExport` converts outliner callbacks into `gx_path` operations: move, line, curve, close, and set width.
- `gx_ttf_outline` builds a glyph outline, selecting TT grid fitting, design-grid rendering, autohinting fallback, or unhinted output based on `gs_currentgridfittt`.
- `grid_fit` is an unfinished autohinting path that uses the Type 1 hinter over a generated TrueType outline and spot analyzer stems.

Notable dependencies:
- Type 42 font internals: `gxfont42.h`.
- TrueType interpreter/outliner headers: `gxttfb.h`, `ttfmemd.h`, `ttfoutl.h`.
- Path and hinting: `gxpath.h`, `gzpath.h`, `gxhintn.h`, `gzspotan.h`.
- Ghostscript memory and font APIs: `gsstruct.h`, `gsfont.h`.

Research notes:
- `gx_ttfReader__Read` cannot handle positive continuation from `string_proc`; it returns `gs_error_unregistered` for that unimplemented loop case.
- `ttfFont__create` has early returns after allocating `gx_ttfMemory` if interpreter or spot analyzer acquisition fails, with no visible cleanup of `m`; callers should treat this legacy path carefully.
- Warnings for bad instructions and patented behavior are emitted once per base font.
- There is a typo in the warning string: “fhe glyph index”.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.h

Header for the Ghostscript-to-TrueType interpreter bridge.

Key contents:
- Includes `ttfoutl.h`.
- Forward-declares `gx_ttfReader` and `gs_font_type42`.
- Defines `struct gx_ttfReader_s` as a `ttfReader` subclass with stream position, error state, one extra glyph buffer index, Type 42 font pointer, allocator, and `gs_glyph_data_t`.
- Declares reader lifecycle and font binding functions.
- Declares `ttfFont__create`, `ttfFont__destroy`, `ttfFont__Open_aux`, and `gx_ttf_outline`.

Research notes:
- The struct comment documents a GC hazard: the reader may live in global memory while `pfont` and `glyph_data` point to local memory, so those fields must be null when GC runs and are reset when the TrueType interpreter exits.
- This header is tightly paired with `gxttfb.c` and the bundled TrueType interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.c

Shared Adobe Type 1 / Type 2 charstring interpreter support for Ghostscript fonts.

Key behavior:
- Defines GC enumeration/relocation for `gs_type1_state`, including relocation of saved charstring instruction pointers relative to relocated glyph data.
- Exports `gx_extendeg_glyph_name_separator`, used by PDF font logic to resolve glyph-name conflicts while converting widths to metrics.
- `gs_type1_interp_init` initializes interpreter state, operand/control stacks, font/imager/path pointers, callback data, paint type, hinting flags, oversampling scales, sidebearing/width state, and seac state.
- `gs_type1_finish_init` computes fixed CTM coefficients, records path origin, initializes hint/flex offsets, and derives character flatness.
- `gs_type1_sbw`, `gs_type1_set_lsb`, and `gs_type1_set_width` record side bearing and width metrics.
- `gs_type1_blend` blends Multiple Master font values using the font weight vector.
- `gs_type1_seac` begins composite accented-character handling by saving accent/base operands and loading the base CharString.
- `gs_type1_endchar` switches from base to accent CharString for `seac`, handles missing accent glyphs compatibly, adjusts fill state for PaintType 0, and sets flatness unless grid fitting is disabled.
- `type1_cis_get_metrics` returns lsb and width as doubles.
- `gs_type1_piece_codes` partially decodes a Type 1 CharString to detect `seac` piece character codes, including subroutine calls and selected OtherSubrs.
- `gs_type1_glyph_info` combines default glyph info with piece and width extraction by fetching glyph data and interpreting until `[h]sbw`.
- `gs_font_parent` returns a Type 1/Type 2 font’s parent Type 9 font when present.

Notable dependencies:
- Font internals: `gxfont.h`, `gxfont1.h`, `gxtype1.h`.
- Charstring constants and glyph data: `gsccode.h`, `gsgdata.h`.
- Hinting and path support: `gxhintn.h`, `gxchrout.h`, `gzpath.h`.

Research notes:
- `gs_type1_piece_codes` duplicates part of the charstring parser because factoring it out was considered too invasive.
- `gs_type1_glyph_info` returns `rangecheck` for unknown OtherSubr during width extraction because it cannot safely continue.
- The missing seac accent path prints a warning and skips the missing accent, matching Acrobat Reader behavior per the comment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.h

Private Type 1 / Type 2 charstring interpreter state and helper macro header.

Key contents:
- Defines oversampling scale structures `pixel_scale` and `point_scale`, plus `set_pixel_scale` and `scaled_rounded`.
- Sets `max_total_stem_hints` to 96 per Type 2 documentation.
- Defines `ip_state_t`, the saved instruction pointer/decryption/glyph-data state for charstring subroutine calls.
- Provides `charstring_this`, `charstring_next`, and `charstring_skip_next` macros for encrypted or plain CharString byte access.
- Defines `struct gs_type1_state_s`, including Type 1 hinter state, font/imager/path pointers, grid-fitting and paint state, fixed CTM coefficients, flatness, oversampling, operand stack, instruction stack, sidebearing/width metrics, Type 2 hint count, seac state, flex state, ignored pops, and transient array.
- Declares the public structure descriptor macro for GC integration.
- Defines operand-stack helper macros `CLEAR_CSTACK`, `INIT_CSTACK`, and `CS_CHECK_PUSH`.
- Defines number-decoding macros for 1-byte, 2-byte, and 4-byte charstring numbers.
- Declares shared interpreter utility functions: `gs_type1_finish_init`, `gs_type1_sbw`, `gs_type1_blend`, `gs_type1_seac`, `gs_type1_endchar`, and `type1_cis_get_metrics`.

Notable dependencies:
- Encryption: `gscrypt1.h`.
- Glyph data and Type 1 data structures: `gsgdata.h`, `gstype1.h`.
- Hinting: `gxhintn.h`.

Research notes:
- Operand and instruction stack sizes match Type 2 documentation: 48 operands and 10 call stack entries.
- The 4-byte decode path sign-extends only on platforms where `long` exceeds 4 bytes.
- This is a private interpreter header; it exposes many macros that assume local variables such as `csp`, `cstack`, `cip`, and decryption state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.c

Ghostscript Well Tempered Screening renderer and device color implementation.

Key behavior:
- Defines `gx_dc_type_wts`, a device color type with save, halftone lookup, load, fill-rectangle, equality, serialization, deserialization, and nonzero-component procedures.
- `mul_shr_16` performs fixed-style multiply/shift using `double`; the integer implementation is marked TODO.
- `wts_get_samples_j` maps device coordinates into Screen J threshold sample cells using fixed coefficients and determines how many contiguous samples remain valid.
- `wts_get_samples_h` maps coordinates for Screen H using `wts_screen_h_offset`, which currently uses a linear search.
- `wts_get_samples` dispatches by WTS screen type.
- `wts_draw` renders a 1-bit tile by comparing a shade level against WTS samples over a rectangle.
- `gx_dc_wts_fill_rectangle_1` draws a one-component WTS halftone by building a temporary mono tile and calling `copy_mono`.
- `gx_dc_wts_fill_rectangle_4` draws up to four components by building per-plane mono tiles, repacking them into chunky 4-bit pixels with `wts_repack_tile_4`, and calling `copy_color`.
- `gx_dc_wts_fill_rectangle` dispatches to one-component or <=4-component implementations.
- `gx_dc_wts_equal` compares type, phase, component count, and levels.
- `gx_dc_wts_get_nonzero_comps` reports which WTS component levels are nonzero.

Notable dependencies:
- Halftone and WTS types: `gsht.h`, `gxdht.h`, `gxwts.h`.
- Device color APIs: `gxdcolor.h`, `gxdevcli.h`.
- Graphics state API: `gxstate.h`.

Research notes:
- Serialization/deserialization (`gx_dc_wts_write` and `gx_dc_wts_read`) are not implemented and return `gs_error_unknownerror`.
- Temporary tile buffers are allocated with C `malloc`/`free`, not Ghostscript memory APIs.
- The code does not check `malloc` results before drawing into buffers, so allocation failure would lead to null dereference.
- More than four components are unsupported and return `-1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.c -->