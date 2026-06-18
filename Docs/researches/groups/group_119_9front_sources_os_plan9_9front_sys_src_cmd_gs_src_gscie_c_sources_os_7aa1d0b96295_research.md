# Group Research: group_119_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gscie_c_sources_os_7aa1d0b96295

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely. This group is Ghostscript graphics/color infrastructure inside the 9front source import, not filesystem implementation code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.c

## Role

`gscie.c` implements CIE color rendering cache management for Ghostscript. It builds, samples, completes, and optimizes CIE color space and Color Rendering Dictionary (CRD) caches, then prepares joint caches used by CIE color remapping.

This is rendering/color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_cie_cached_value`
- `gx_init_CIE`
- `gx_restrict_CIEDEFG`
- `gx_restrict_CIEDEF`
- `gx_restrict_CIEABC`
- `gx_restrict_CIEA`
- `gx_install_CIEDEFG`
- `gx_install_CIEDEF`
- `gx_install_CIEABC`
- `gx_install_CIEA`
- `gx_cie_load_common_cache`
- `gx_cie_common_complete`
- `gs_cie_defg_complete`
- `gs_cie_def_complete`
- `gs_cie_abc_complete`
- `gs_cie_a_complete`
- `gs_setcolorrendering`
- `gs_currentcolorrendering`
- `gx_currentciecaches`
- `gs_cie_cache_init`
- `gs_cie_render_init`
- `gs_cie_render_sample`
- `gs_cie_render_complete`
- `gs_cie_cache_to_fracs`
- `gs_cie_cs_common`
- `gs_cie_cs_complete`
- `gs_cie_jc_complete`
- `gs_cie_compute_points_sd`
- `gx_cie_to_xyz_alloc`
- `gx_cie_to_xyz_free`

## Core Behavior

The file defines default CIE decode/encode functions, default ranges, default matrices, and cache-backed substitutes for DecodeA, DecodeABC, DecodeDEF, DecodeDEFG, and DecodeLMN.

Cache loading is driven by `CIE_LOAD_CACHE_BODY`, which samples client procedures over computed sample domains and records whether a function is identity. Linear-cache detection then marks caches that can be folded into matrix operations.

CIE color installation loads Decode caches, initializes common LMN caches, completes derived vector caches, and invalidates or rebuilds joint caches as needed. DEF and DEFG spaces additionally scale DecodeDEF/DecodeDEFG values into lookup-table dimensions.

CRD handling progresses through explicit statuses:

- `gs_cie_render_init`: initializes matrices, inverse mappings, derived domains, and source/destination white/black points.
- `gs_cie_render_sample`: samples EncodeLMN, EncodeABC, and RenderTable.T functions.
- `gs_cie_render_complete`: restricts sampled values, converts final caches to fracs or table indices, and folds EncodeABC cache scaling into `MatrixABCEncode`.

Joint caches combine the current CIE color space and CRD. `cie_joint_caches_complete` works backward through the mapping pipeline and folds identity steps where possible when `OPTIMIZE_CIE_MAPPING` is enabled.

`gx_cie_to_xyz_alloc` builds a minimal imager state and joint cache for CIE-to-XYZ conversion, used by PDF writing paths.

## Dependencies

Includes Ghostscript color, CIE, matrix, device, imager state, serialization, and arithmetic internals: `gxcspace.h`, `gxcie.h`, `gxcmap.h`, `gzstate.h`, `gsicc.h`, and related math/memory support.

## Notable Risks

- `cie_invert3` divides by determinant without a visible zero/singularity guard.
- Several cache completion routines are explicitly “not idempotent”; callers must honor status ordering.
- Optimized folding depends on exact identity/linearity detection and may alter numerical behavior near interpolation thresholds.
- `gx_cie_to_xyz_alloc` sets `pis->cie_render` to a non-null sentinel pointer only to satisfy checks; the sentinel must never be dereferenced.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.h

## Role

`gscie.h` defines the core data structures, cache layout, procedure types, defaults, constructors, and accessors for Ghostscript CIE color algorithms.

This is rendering/color-management infrastructure, not filesystem code.

## Main Definitions

- CIE cache sizing:
  - `CIE_LOG2_CACHE_SIZE`
  - `gx_cie_cache_size`
  - interpolation macros
  - fixed-vs-float cache value selection
- Vector and matrix types:
  - `gs_vector3`
  - `gs_matrix3`
  - `gs_range3`
  - `gs_range4`
- CIE procedure types:
  - `gs_cie_a_proc`
  - `gs_cie_abc_proc`
  - `gs_cie_def_proc`
  - `gs_cie_defg_proc`
  - `gs_cie_common_proc`
  - `gs_cie_render_proc`
  - `gs_cie_transform_proc`
  - `gs_cie_render_table_proc`
- Cache structures:
  - `cie_cache_floats`
  - `cie_cache_fracs`
  - `cie_cache_ints`
  - `gx_cie_vector_cache`
  - `gx_cie_vector_cache3_t`
- CIE color structures:
  - `gs_cie_common`
  - `gs_cie_a`
  - `gs_cie_abc`
  - `gs_cie_def`
  - `gs_cie_defg`
- CRD structures:
  - `gs_cie_render`
  - `gs_cie_render_table_t`
  - `gx_cie_joint_caches`

## Public API Surface

Declares constructors for CIEBasedA, CIEBasedABC, CIEBasedDEF, and CIEBasedDEFG color spaces, plus lookup-table setup and CRD/cache completion functions.

It also declares CIE cache utilities, joint-cache completion, sampled-loop helpers, and `gx_serialize_cie_common_elements`.

## Important Design Notes

Matrices are stored in column order and multiplied as column-vector transforms. The header explicitly notes that composing M1 followed by M2 requires computing `M2 * M1`.

The cache system assumes monotonic client functions with known domains so procedure callbacks can be sampled up front and avoided in rendering hot paths.

The constructor comment warns that CIE parameter structures are created with reference count 1, while `gs_setcolorspace` increments again; clients are expected to adjust counts afterward. The comment labels this as an API bug.

## Notable Risks

- Heavy reliance on structural “puns” between CIEA/ABC/DEF/DEFG parameter layouts makes field ordering critical.
- `gs_cie_a_RangeA` is defined twice.
- Several comments describe status preconditions, but implementation in `gscie.c` mostly treats completion calls as idempotent rather than rejecting out-of-order states.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsciemap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsciemap.c

## Role

`gsciemap.c` is the runtime CIE color rendering hot path. It maps CIEBasedA/ABC/DEF/DEFG client colors through precomputed caches, CRD transforms, render tables, and final concrete RGB/CMYK remapping.

This is rendering/color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `gx_concretize_CIEDEFG`
- `gx_concretize_CIEDEF`
- `gx_remap_CIEABC`
- `gx_concretize_CIEABC`
- `gx_concretize_CIEA`
- `gx_cie_remap_finish`
- `gx_cie_real_remap_finish`
- `gx_cie_xyz_remap_finish`

## Core Behavior

For CIEBasedDEF and CIEBasedDEFG, input components are decoded through cached DecodeDEF/DecodeDEFG values, clamped and scaled into lookup-table coordinates, interpolated through `gx_color_interpolate_linear`, converted into ABC values, optionally passed through DecodeABC/MatrixABC, then finished through the joint CIE pipeline.

For CIEBasedABC and CIEBasedA, the code maps input values directly into cached vector forms before invoking the remap finish procedure.

`gx_cie_real_remap_finish` applies the remaining joint-cache pipeline:

- DecodeLMN / MatrixLMN / MatrixPQR
- TransformPQR / inverse PQR / MatrixLMN
- EncodeLMN / MatrixABC
- EncodeABC
- optional RenderTable lookup and RenderTable.T mapping

It returns 3 for RGB output or 4 for CMYK output.

`gx_cie_xyz_remap_finish` is a special endpoint for CIE-to-XYZ export; it clamps XYZ values into fracs.

## Performance Design

The file uses cache-index macros to avoid function-call overhead in non-debug builds. `cie_lookup_mult3` supports interpolation only inside precomputed interpolation ranges and otherwise performs direct lookup and cached vector summation.

## Dependencies

Uses CIE definitions from `gxcie.h`, color remapping from `gxcmap.h`, device color operations, imager state, and fixed/fraction arithmetic.

## Notable Risks

- The code assumes `CIE_CHECK_RENDERING` establishes valid CIE rendering state before cache use.
- Index arithmetic is performance-oriented and depends on cache base/factor/limit correctness from `gscie.c`.
- The non-interpolating render-table path is compiled out when `CIE_RENDER_TABLE_INTERPOLATE` is defined, so both variants must be maintained carefully.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsciemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscindex.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscindex.h

## Role

`gscindex.h` declares the client API for Ghostscript Indexed color spaces.

This is rendering/color-space infrastructure, not filesystem code.

## Public API

- `gs_cspace_build_Indexed`
- `gs_cspace_indexed_num_entries`
- `gs_cspace_indexed_value_array`
- `gs_cspace_indexed_set_proc`
- `gs_cspace_indexed_lookup`

## Behavior Contract

The header documents two Indexed color modes:

- byte-string lookup table supplied by the client
- procedure-backed palette/cache where clients can fill values directly and optionally replace the lookup procedure

The table memory is owned by the client for string-table color spaces; the color space does not free it.

## Dependencies

Includes `gscspace.h` for color-space definitions and `gs_indexed_params`.

## Notable Risks

- API ownership is mixed: byte lookup tables are external, while procedure-backed maps are allocated by the color-space implementation.
- The corresponding implementation’s `gs_cspace_indexed_value_array` condition appears inconsistent with this header’s procedure-backed palette-accessor description.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscindex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.c

## Role

`gsclipsr.c` implements Ghostscript `clipsave` and `cliprestore` operations by maintaining a reference-counted stack of saved clipping paths.

This is graphics-state clipping infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_clipsave`
- `gs_cliprestore`

## Core Behavior

`gs_clipsave` creates a shared copy of the current clip path, allocates a `gx_clip_stack_t`, initializes reference counting with `rc_free_clip_stack`, and pushes it onto `pgs->clip_stack`.

`gs_cliprestore` pops from `pgs->clip_stack` when present and restores the saved clip path. If the stack node is uniquely referenced, it frees the stack node and assigns the clip path with transfer of ownership; otherwise it preserves the shared clip path and decrements the stack reference count.

If no clip stack is present, `cliprestore` falls back to restoring the clip path from the saved graphics state.

## Memory Management

`rc_free_clip_stack` frees stack nodes iteratively and frees each associated clip path, avoiding recursion through long clip-stack chains.

## Dependencies

Uses graphics state, clip path, path, fixed-coordinate, and Ghostscript GC/refcount support.

## Notable Risks

- `gs_clipsave` must handle partially failed allocation for either the clip-path copy or stack node; it does free both possible allocations on failure.
- `gs_cliprestore` assumes `pgs->saved` is valid when no explicit clip stack exists.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.h

## Role

`gsclipsr.h` declares the client interface for Ghostscript clipping save/restore operations.

This is graphics-state infrastructure, not filesystem code.

## Public API

- `gs_clipsave(gs_state *)`
- `gs_cliprestore(gs_state *)`

## Dependencies

Requires `gs_state` to be visible to callers through the surrounding Ghostscript headers.

## Notable Risks

No internal state is defined here; correctness is in `gsclipsr.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsclipsr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.c

## Role

`gscolor.c` implements core Ghostscript color and transfer-function operators for grayscale and RGB color, null color, transfer maps, and character-cache device color setup.

This is rendering/color graphics-state infrastructure, not filesystem code.

## Main Public Interfaces

- `gx_init_paint_1`
- `gx_init_paint_3`
- `gx_init_paint_4`
- `gx_restrict01_paint_1`
- `gx_restrict01_paint_3`
- `gx_restrict01_paint_4`
- `gx_no_adjust_color_count`
- `gs_setgray`
- `gs_setrgbcolor`
- `gs_setnullcolor`
- `gs_settransfer`
- `gs_settransfer_remap`
- `gs_currenttransfer`
- `gx_set_device_color_1`
- `load_transfer_map`

## Core Behavior

The file initializes paint component arrays for 1-, 3-, and 4-component spaces and clamps paint values into `[0,1]`.

`gs_setgray` and `gs_setrgbcolor` switch the graphics state to DeviceGray or DeviceRGB, set clamped paint values, clear pattern state, and invalidate cached device color.

`gs_setnullcolor` is disallowed inside `cachedevice`, otherwise it switches to harmless gray and marks device color null.

Transfer handling uses `gx_transfer_map` reference counting. `gs_settransfer_remap` unshares the gray transfer map, drops color transfer maps, assigns a new procedure, reloads the transfer cache if requested, updates effective transfer, and invalidates device color.

`load_transfer_map` samples either old-style function pointers or closure-style transfer callbacks into a fixed-size frac table.

## Dependencies

Uses Ghostscript color-space, device color, device, transfer-map, graphics state, and GC/refcount support.

## Notable Risks

- Transfer-map mutation relies on `rc_unshare_struct`; failure paths must restore reference counts.
- `gx_set_device_color_1` changes overprint and color-space state for character-cache rendering, so callers must use it only in the intended cache context.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.h

## Role

`gscolor.h` declares the base Ghostscript client color API for gray/RGB/null color and transfer functions.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_setgray`
- `gs_currentgray`
- `gs_setrgbcolor`
- `gs_currentrgbcolor`
- `gs_setnullcolor`
- `gs_settransfer`
- `gs_settransfer_remap`
- `gs_currenttransfer`

## Dependencies

Includes `gxtmap.h` for transfer-map procedure types.

## Notable Risks

This header only declares APIs; current-color query implementations are elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.c

## Role

`gscolor1.c` implements Ghostscript Level 1 extended color operators: CMYK color, black generation, undercolor removal, and color transfer functions.

This is rendering/color graphics-state infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_setcmykcolor`
- `gs_setblackgeneration`
- `gs_setblackgeneration_remap`
- `gs_currentblackgeneration`
- `gs_setundercolorremoval`
- `gs_setundercolorremoval_remap`
- `gs_currentundercolorremoval`
- `gs_setcolortransfer`
- `gs_setcolortransfer_remap`
- `gs_currentcolortransfer`

## Core Behavior

`gs_setcmykcolor` switches the current color space to DeviceCMYK, clamps all four components, clears pattern state, and invalidates device color.

Black generation and undercolor removal setters unshare the corresponding transfer map, assign the new procedure, stamp a new ID, optionally sample it into the cached transfer map, and invalidate device color.

`gs_setcolortransfer_remap` unshares gray/red/green/blue transfer maps, assigns new transfer procedures and IDs, records device component numbers for Red/Green/Blue/Gray halftone transfer lookup, reloads maps if requested, updates effective transfer, and invalidates device color.

## Dependencies

Uses `load_transfer_map` from `gscolor.c`, effective transfer setup from halftone code, color-space/device-color internals, and halftone component-name lookup.

## Notable Risks

- The `setcolortransfer` failure path restores some old map pointers by `rc_assign`, but the sequence is delicate because multiple unshare operations can fail at different points.
- Device component-name lookup occurs at setter time and depends on the current device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.h

## Role

`gscolor1.h` declares the client interface for Ghostscript Level 1 extended color facilities.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_setcmykcolor`
- `gs_currentcmykcolor`
- `gs_setblackgeneration`
- `gs_setblackgeneration_remap`
- `gs_currentblackgeneration`
- `gs_setundercolorremoval`
- `gs_setundercolorremoval_remap`
- `gs_currentundercolorremoval`
- `gs_setcolortransfer`
- `gs_setcolortransfer_remap`
- `gs_currentcolortransfer`

## Dependencies

Requires `gscolor.h` context and Ghostscript mapping-procedure types.

## Notable Risks

Header-only declarations; behavior and reference-count safety are in `gscolor1.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.c

## Role

`gscolor2.c` implements Ghostscript Level 2 color operations: general `setcolorspace`/`setcolor`, Indexed color spaces, Indexed color lookup/remapping, serialization, and high-level device color-space inclusion.

This is rendering/color-space infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_setcolorspace`
- `gs_currentcolorspace`
- `gs_setcolor`
- `gs_currentcolor`
- `lookup_indexed_map`
- `free_indexed_map`
- `alloc_indexed_map`
- `gs_cspace_build_Indexed`
- `gs_cspace_indexed_num_entries`
- `gs_cspace_indexed_value_array`
- `gs_cspace_indexed_set_proc`
- `gs_cspace_indexed_lookup`
- `gs_includecolorspace`

## Core Behavior

`gs_setcolorspace` rejects changes inside `cachedevice`, adjusts reference counts, installs the new color space, updates overprint if active, initializes the current color, releases the old current color and old color space, and invalidates device color.

`gs_setcolor` copies client color into graphics state, adjusts old/new color references, restricts values through the color-space type, and invalidates device color.

Indexed color-space support can use either:

- a byte string table owned externally
- an allocated `gs_indexed_map` palette/procedure object with reference-counted storage

The Indexed color type delegates installation, overprint, and concrete-space selection to its base space. Concretization looks up a palette entry into a `gs_client_color`, then concretizes in the base color space.

Serialization writes the base color space, high index, mode flag, and either mapped float values or byte table data.

`gs_includecolorspace` calls the current device’s `include_color_space` procedure for high-level output devices such as PDF.

## Dependencies

Uses color-space internals, pattern/color remapping, stream serialization, memory/refcount helpers, and device procedures.

## Notable Risks

- `gs_cspace_indexed_value_array` returns null when `use_proc` is true, which appears inconsistent with the header comment saying the function returns the cached-value array for procedure-based Indexed color spaces. Since the non-procedure path stores a byte table rather than a map, the implementation condition is suspect.
- The byte-table mode stores a caller-owned pointer; lifetime is external.
- `gs_cspace_build_Indexed` sets `hival = num_entries - 1`; a zero `num_entries` value would underflow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.h

## Role

`gscolor2.h` declares the Ghostscript Level 2 color API for general color spaces, current color, CIE color rendering, and device color-space inclusion.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_currentcolorspace`
- `gs_setcolorspace`
- `gs_currentcolor`
- `gs_setcolor`
- `gs_currentcolorrendering`
- `gs_setcolorrendering`
- `gs_includecolorspace`

## Dependencies

Includes `gscindex.h` and `gsptype1.h`; requires `gscspace.h` and `gsmatrix.h` context.

## Important Contract

The header notes that `setcolorspace` and `setcolor` copy only the top level of their structure arguments, so heap-allocated caller structures may be freed after setting them, but referenced subobjects must obey the color-space reference-counting rules.

## Notable Risks

CRD type is forward-declared here for public use; concrete CRD layout is in `gscie.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.c

## Role

`gscolor3.c` implements Ghostscript LanguageLevel 3 color operations for smoothness and shading fill.

This is rendering/shading infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_setsmoothness`
- `gs_currentsmoothness`
- `gs_shfill`

## Core Behavior

`gs_setsmoothness` clamps the graphics-state smoothness value to `[0,1]`.

`gs_shfill` constructs a shading pattern from the supplied shading object, marks it as a `shfill` pattern, remaps it through a Pattern color space without a base space, converts the current clipping path into a path, and fills that path with winding rule. It then releases the pattern reference.

The implementation deliberately uses `gx_fill_path` rather than direct shading fill so high-level output devices can observe the fill operation.

## Dependencies

Uses Pattern Type 2 support, shading support, clip-path-to-path conversion, device color remapping, and graphics state/path operations.

## Notable Risks

- `gs_shfill` allocates and remaps a pattern before converting/filling the clip path; each failure path must preserve pattern reference cleanup.
- Background handling is described in comments, but this function does not visibly clone and remove `Background`; that behavior likely occurs through `gs_pattern2_set_shfill`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.h

## Role

`gscolor3.h` declares the client interface for LanguageLevel 3 smooth shading operations.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_setsmoothness`
- `gs_currentsmoothness`
- `gs_shfill`

## Dependencies

Forward-declares `gs_shading_t` when needed.

## Notable Risks

Header-only; implementation is in `gscolor3.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscompt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscompt.h

## Role

`gscompt.h` defines the abstract compositing-object type used near the end of the Ghostscript rendering pipeline.

This is rendering pipeline infrastructure, not filesystem code.

## Public API

- `typedef struct gs_composite_s gs_composite_t`
- `gs_composite_id`

## Design Notes

The comments define compositing as occurring after color correction and before halftoning. Concrete compositing implementations are expected to provide default device implementations when target devices lack optimized support.

Compositing objects carry unique IDs for cache lookup and equality testing, similar to halftones and transfer functions.

## Dependencies

Uses `gs_id` from Ghostscript base types.

## Notable Risks

This header is intentionally abstract; concrete behavior is defined by subclasses elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscompt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.c

## Role

`gscoord.c` implements Ghostscript coordinate-system and current transformation matrix (CTM) operations, including default matrix handling, text character matrices, transforms, inverse transforms, and fixed-point transform helpers.

This is graphics-state geometry infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_initmatrix`
- `gs_defaultmatrix`
- `gs_setdefaultmatrix`
- `gs_currentmatrix`
- `gs_setcharmatrix`
- `gs_currentcharmatrix`
- `gs_setmatrix`
- `gs_imager_setmatrix`
- `gs_settocharmatrix`
- `gs_translate`
- `gs_scale`
- `gs_rotate`
- `gs_concat`
- `gs_transform`
- `gs_dtransform`
- `gs_itransform`
- `gs_idtransform`
- `gs_imager_idtransform`
- `gx_translate_to_fixed`
- `gx_scale_char_matrix`
- `gx_matrix_to_fixed_coeff`
- `fixed_coeff_mult`

## Core Behavior

The file updates CTM state and invalidates cached inverse CTM and cached character matrix whenever transforms change.

`gs_defaultmatrix` uses the current device’s initial matrix, then applies device margins scaled by hardware resolution, unless an explicit default matrix has been set.

`gs_setcharmatrix` composes a font matrix with the CTM and caches a fixed-point-capable character matrix.

Inverse transform functions prefer exact inverse operations for non-skewed matrices and use cached inverse matrices only for skewed cases.

`gx_translate_to_fixed` adjusts CTM translation to exact fixed coordinates and translates the current path by the corresponding fixed delta when possible.

`gx_matrix_to_fixed_coeff` and `fixed_coeff_mult` prepare and use fixed-point coefficients for fast distance transformations while avoiding overflow.

## Precision Design

`ROUND_CTM_FIXED` aligns floating CTM translation values with rounded fixed translations to avoid anomalies such as `0 0 moveto currentpoint` not returning exactly `0 0`.

## Dependencies

Uses matrix, fixed-point arithmetic, path translation, device initial matrix, font matrix, and graphics/imager state internals.

## Notable Risks

- Large or fractional path translations fail with `limitcheck` when fixed CTM translation is invalid and the path is non-null.
- Cached inverse and character matrices depend on consistent invalidation.
- Fixed coefficient scaling uses bit-width assumptions and must avoid overflow across supported architectures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.h

## Role

`gscoord.h` declares the Ghostscript graphics-state CTM and coordinate transformation API.

This is graphics geometry API infrastructure, not filesystem code.

## Public API

- CTM modification:
  - `gs_initmatrix`
  - `gs_defaultmatrix`
  - `gs_currentmatrix`
  - `gs_setmatrix`
  - `gs_translate`
  - `gs_scale`
  - `gs_rotate`
  - `gs_concat`
- Extensions:
  - `gs_setdefaultmatrix`
  - `gs_currentcharmatrix`
  - `gs_setcharmatrix`
  - `gs_settocharmatrix`
- Transform operations:
  - `gs_transform`
  - `gs_dtransform`
  - `gs_itransform`
  - `gs_idtransform`
- Imager-state operations:
  - `gs_imager_setmatrix`
  - `gs_imager_idtransform`

## Dependencies

Requires `gsmatrix.h` and `gsstate.h` context; forward-declares `gs_imager_state` if needed.

## Notable Risks

Header only; behavior and cache invalidation are in `gscoord.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscparam.c

## Role

`gscparam.c` implements Ghostscript’s default C in-memory parameter-list implementation for reading, writing, requesting, enumerating, and forwarding typed device/interpreter parameters.

This is parameter plumbing infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_c_param_list_alloc`
- `gs_c_param_list_write`
- `gs_c_param_list_set_target`
- `gs_c_param_list_write_more`
- `gs_c_param_list_release`
- `gs_c_param_list_read`

The public procedure table methods are installed into `gs_param_list` and used through generic parameter APIs.

## Core Data Model

Each parameter is stored as a linked `gs_c_param` node with:

- key and key ownership flag
- typed value union
- `gs_param_type`
- optional alternate typed data
- next pointer

`gs_param_type_any` marks requested-but-not-written parameters.

## Write Behavior

Writes allocate parameter nodes, copy typed values, and deep-copy non-persistent string/name/array storage. String and name arrays also copy second-level string data when needed.

Collections are represented as nested `gs_c_param_list` instances and stored as dict, int-key dict, or array values.

## Read Behavior

Reads search the local list first, optionally fall back to a target parameter list, and then coerce values to requested types. A special int-array-to-float-array conversion path allocates alternate typed data and caches it in the parameter node.

Enumeration walks the linked list. Error policy defaults to ignore, and commit is a no-op.

## GC Support

Defines composite GC descriptors for parameter nodes and lists. Aggregate parameters recurse into nested lists; other typed values delegate to `gs_param_typed_value` GC helpers.

## Notable Risks

- List insertion is head-first, so enumeration returns reverse write order.
- `alternate_typed_data` lifetime is tied to list release; callers must not retain converted arrays afterward.
- `persistent_keys = true` by default means key strings are usually not copied, so caller key storage must remain valid unless persistence is disabled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.c

## Role

`gscpixel.c` implements Ghostscript’s DevicePixel color space, which treats the color value as a raw device pixel index.

This is rendering/device color infrastructure, not filesystem code.

## Main Public Interface

- `gs_cspace_init_DevicePixel`

## Core Behavior

The DevicePixel color space is a one-component, base color space. Initialization accepts only depths 1, 2, 4, 8, 16, 24, or 32.

Restriction clamps the pixel value to `[0, (1 << depth) - 1]`.

Concretization casts the paint value to a `frac` carrying the raw pixel value. Remapping masks the value to the current device color depth and stores it as a pure device color.

DevicePixel disables overprint by resetting effective overprint mode and updating state with `retain_any_comps = false`.

Serialization writes the color-space type and pixel depth.

## Dependencies

Uses color-space internals, device color, overprint state, imager/graphics state, and stream serialization.

## Notable Risks

- Comments note “NOT ENOUGH BITS IN float OR frac” for raw pixel values, especially at larger depths.
- `(1L << depth)` is used for max-value calculation; depth 32 may be architecture-sensitive if `long` width or signed shifting assumptions differ.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.h

## Role

`gscpixel.h` declares the DevicePixel color-space initialization API.

This is rendering/device color API infrastructure, not filesystem code.

## Public API

- `gs_cspace_init_DevicePixel(gs_memory_t *mem, gs_color_space *pcs, int depth)`

## Dependencies

Requires `gscspace.h` context for `gs_color_space` and memory types.

## Notable Risks

Header only; accepted depth validation and raw-pixel limitations are in `gscpixel.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpm.h

## Role

`gscpm.h` defines enum values for charpath mode and cache-device status in Ghostscript.

This is text/rendering state infrastructure, not filesystem code.

## Main Definitions

`gs_char_path_mode` values:

- `cpm_show`
- `cpm_charwidth`
- `cpm_false_charpath`
- `cpm_true_charpath`
- `cpm_false_charboxpath`
- `cpm_true_charboxpath`

`gs_in_cache_device_t` values:

- `CACHE_DEVICE_NONE`
- `CACHE_DEVICE_NOT_CACHING`
- `CACHE_DEVICE_NONE_AND_CLIP`
- `CACHE_DEVICE_CACHING`

## Important Contracts

Both default enum values are explicitly required to remain zero.

## Dependencies

No substantial dependencies beyond standard Ghostscript type context.

## Notable Risks

Enums are used as shared state markers; changing numeric order would break callers relying on zero/default semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.c

## Role

`gscrd.c` creates and initializes Ghostscript CIE Color Rendering Dictionaries (CRDs), defines default CRD procedures, cache-backed procedure wrappers, and TransformPQR procedure lookup through device parameters.

This is color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `TransformPQR_default`
- `TransformPQR_from_cache`
- `TransformPQR_lookup_proc_name`
- `Encode_default`
- `EncodeLMN_from_cache`
- `EncodeABC_from_cache`
- `RenderTableT_default`
- `RenderTableT_from_cache`
- `gs_cie_render1_build`
- `gs_cie_render1_init_from`
- `gs_cie_render1_initialize`

## Core Behavior

`gs_cie_render1_build` allocates a reference-counted CRD, assigns an ID, initializes GC-visible pointers, marks status built, and returns it.

`gs_cie_render1_init_from` copies all CRD parameters into a CRD, applying defaults for optional values. If `pfrom_crd` is supplied and procedure fields indicate cache-backed procedures, it copies cached EncodeLMN, EncodeABC, or RenderTable.T cache data from the source CRD.

`gs_cie_render1_initialize` is a convenience wrapper with no source-CRD cache copy.

Default procedures are identity transforms. Cache-backed procedures call `gs_cie_cached_value` against existing CRD caches.

TransformPQR procedure-name lookup searches the Ghostscript library device list for the named driver, copies the prototype device, requests the named parameter, reads a procedure pointer from a string parameter, and then calls the resolved procedure.

## GC Support

Defines `st_cie_render1` with GC enumeration/relocation for `client_data`, render-table string table, and TransformPQR procedure data when a render table exists.

## Notable Risks

- TransformPQR device-parameter lookup deserializes a function pointer from string data; this is tightly coupled to trusted in-process device parameters.
- `TransformPQR.proc_data` relocation is conditioned on `RenderTable.lookup.table`, which looks suspicious because TransformPQR data can conceptually exist without a render table.
- The CRD build API has the same reference-count convention noted elsewhere: callers may need to decrement after setting it in graphics state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.h

## Role

`gscrd.h` declares the public interface for creating and initializing Ghostscript CIE Color Rendering Dictionaries.

This is color-management API infrastructure, not filesystem code.

## Public API

- `gs_cie_render1_build`
- `gs_cie_render1_init_from`
- `gs_cie_render1_initialize`
- `gs_cie_render_client_data`

## Important Contracts

The header documents that `gs_cie_render1_build` returns a CRD with reference count 1, while `gs_setcolorrendering` increments it again. Clients should decrement their reference after setting the CRD if they do not intend to keep it.

`gs_cie_render1_init_from` copies scalar/matrix/range/procedure values but only copies the render-table pointer, not the render-table data.

## Dependencies

Includes `gscie.h`.

## Notable Risks

Render-table data lifetime remains caller-owned or externally managed; the initializer does not deep-copy it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.c

## Role

`gscrdp.c` serializes and deserializes device-specified CIE CRDs through Ghostscript parameter lists.

This is device parameter/color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `param_write_cie_render1`
- `param_put_cie_render1`
- `gs_cie_render1_param_initialize`
- `param_get_cie_render1`

## Write Behavior

The writer emits a modified PostScript-style CRD dictionary containing:

- `ColorRenderingType`
- `WhitePoint`
- optional `BlackPoint`
- matrices and ranges when non-default
- sampled `EncodeLMNValues` and `EncodeABCValues`
- optional TransformPQR name/data
- optional render table size/table
- optional sampled `RenderTableTValues`

Sampling is performed from CRD procedures into float arrays sized by `gx_cie_cache_size`.

If TransformPQR is neither default nor name-addressable, writing fails with `rangecheck`.

## Read Behavior

The reader validates `ColorRenderingType`, reads vectors/matrices/ranges, reads optional sampled procedure arrays, reconstructs temporary procedure callbacks backed by stack-local `encode_data_t`, initializes/samples/completes the CRD, then replaces procedure pointers with cache-backed forms where sampled arrays were supplied.

Render tables are validated for dimensions and string sizes, then copied into newly allocated `gs_const_string` arrays referencing parameter-list string data.

## Dependencies

Uses Ghostscript parameter-list APIs, CIE cache/render routines, device names, memory allocation, and render-table interpolation support.

## Notable Risks

- `param_get_cie_render1` temporarily stores `pcrd->client_data = &data` where `data` is stack-local; it resets `client_data` before return, relying on all cache completion happening synchronously.
- Render table string data is referenced from the parameter list data; the allocated table copies string descriptors, not underlying bytes.
- Writer comments mark `pd.persistent = true` for TransformPQRData as “WRONG,” indicating an acknowledged lifetime/ownership issue.
- Error cleanup for partially allocated render-table structures is limited and depends on downstream ownership conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.h

## Role

`gscrdp.h` declares the interface and encoded dictionary format for device-specified Ghostscript CIE CRDs.

This is device parameter/color-management API infrastructure, not filesystem code.

## Public API

- `param_write_cie_render1`
- `param_put_cie_render1`
- `gs_cie_render1_param_initialize`
- `param_get_cie_render1`

## Encoded Format

Defines `GX_DEVICE_CRD1_TYPE` as `101` and documents a modified ColorRenderingType 1 dictionary format:

- `TransformPQRName`
- `TransformPQRData`
- `EncodeLMNValues`
- `EncodeABCValues`
- `RenderTableSize`
- `RenderTableTable`
- `RenderTableTValues`

## Dependencies

Includes `gscie.h` and `gsparam.h`; forward-declares `gx_device`.

## Notable Risks

The header explicitly says the representation is subject to change without notice, so external clients should treat it as internal device-parameter protocol rather than a stable file format.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.c

## Role

`gscrypt1.c` implements Adobe Type 1 font encryption and decryption loops.

This is font data encoding infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_type1_encrypt`
- `gs_type1_decrypt`

## Core Behavior

Both functions copy the caller-provided crypt state locally, process `len` bytes, update output bytes using macros from `gscrypt1.h`, then write the final state back to `*pstate`.

Encryption processes each source byte through `encrypt_next`.

Decryption handles in-place source/destination overlap by first copying the input byte into a local `ch`, then applying `decrypt_next`.

## Dependencies

Uses basic Ghostscript types from `gstypes.h` and encryption macros from `gscrypt1.h`.

## Notable Risks

This is legacy Type 1 charstring/eexec-style obfuscation, not modern cryptography. It should not be used for security beyond compatibility with Adobe Type 1 formats.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.h

## Role

`gscrypt1.h` declares Adobe Type 1 encryption/decryption APIs and defines the state-update macros/constants.

This is font data encoding API infrastructure, not filesystem code.

## Public API

- `typedef ushort crypt_state`
- `gs_type1_encrypt`
- `gs_type1_decrypt`

## Main Macros And Constants

- `crypt_c1`
- `crypt_c2`
- `crypt_c1_inverse`
- `encrypt_next`
- `decrypt_this`
- `decrypt_next`
- `decrypt_skip_next`
- `decrypt_skip_previous`

## Core Behavior

Encryption and decryption use the standard 16-bit rolling Type 1 cipher state. The inverse constant supports stepping state backward with `decrypt_skip_previous`.

## Notable Risks

Macro arguments have side effects through state mutation; callers must avoid expressions with unintended repeated side effects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscscie.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscscie.c

## Role

`gscscie.c` defines Ghostscript CIE color-space types, constructors, defaults, reference counting, concrete-space selection, lookup-table setup, and serialization.

This is color-management/color-space infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_color_space_type_CIEDEFG`
- `gs_color_space_type_CIEDEF`
- `gs_color_space_type_CIEABC`
- `gs_color_space_type_CIEA`
- `gx_concrete_space_CIE`
- `gx_install_CIE`
- `gx_set_common_cie_defaults`
- `gx_build_cie_space`
- `gs_cspace_build_CIEA`
- `gs_cspace_build_CIEABC`
- `gs_cspace_build_CIEDEF`
- `gs_cspace_build_CIEDEFG`
- `gs_cie_defx_set_lookup_table`
- `gx_serialize_cie_common_elements`

## Core Behavior

The file declares GC descriptors and four CIE color-space types for CIEBasedA, CIEBasedABC, CIEBasedDEF, and CIEBasedDEFG. Each type installs CIE initialization, restriction, concretization, overprint, reference-count adjustment, and serialization handlers.

`gx_concrete_space_CIE` chooses DeviceRGB unless the current CRD has a render table with four output components, in which case it chooses DeviceCMYK.

Constructors allocate both a color-space object and the large reference-counted parameter object, then apply default ranges, matrices, decode functions, install hooks, and lookup-table placeholders.

DEF/DEFG lookup-table setup stores dimensions and a pointer to the table but does not deep-copy table data.

Serialization emits color-space type, common CIE elements, cached decode values where needed, ranges, matrices, and lookup-table metadata/data.

## Dependencies

Uses CIE definitions, color-space internals, device color mapping, stream serialization, refcount/GC support, and CIE map/concretization routines.

## Notable Risks

- `gx_concrete_space_CIE` uses static `rgb_cs` and `cmyk_cs` objects initialized idempotently; shared mutable statics can be risky in concurrent contexts.
- `gx_serialize_lookup_table` writes `&t->table->data` rather than `t->table->data`, which appears suspicious because it serializes bytes from the address of the pointer field, not from the pointed-to table data.
- `gx_serialize_CIEDEFG` loops `k < 3` over `DecodeDEFG` caches even though DEFG has four components; this appears to omit the fourth cache.
- Lookup-table setters store caller-provided table pointers without ownership transfer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscscie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsel.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsel.h

## Role

`gscsel.h` defines color operand selection values used to distinguish source and texture colors for RasterOp and related graphics-state operations.

This is rendering state infrastructure, not filesystem code.

## Main Definitions

`gs_color_select_t` values:

- `gs_color_select_all = -1`
- `gs_color_select_texture = 0`
- `gs_color_select_source = 1`

Also defines `gs_color_select_count` as `2`.

## Important Contract

`gs_color_select_texture` is explicitly zero because it is used for `currenthtphase`.

## Notable Risks

Changing numeric values would break callers that rely on the documented zero and count semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.c

## Role

`gscsepr.c` implements Ghostscript Separation color spaces: construction, tint-transform function binding, device colorant matching, alternate color-space fallback, concretization/remapping, overprint behavior, and serialization.

This is color-management/color-space infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_color_space_type_Separation`
- `gs_build_Separation`
- `gs_cspace_build_Separation`
- `gs_cspace_set_sepr_function`
- `gs_cspace_get_sepr_function`

The disabled `gs_cspace_set_sepr_proc` exists under `#if 0`.

## Core Behavior

A Separation color space has one tint component, a separation name, an alternate color space, and a `gs_device_n_map` tint transform.

Construction validates that the alternate color space can be an alternate space, allocates the DeviceN-style map, stores the separation name, and initializes the alternate space copy.

Installation calls `check_Separation_component_name`, stores whether alternate color space should be used, optionally installs the alternate color space, and lets the device update spot equivalent colors.

Component-name checking:

- treats `SEP_NONE` and `SEP_ALL` as special and avoids alternate space
- forces alternate space on additive devices
- converts the separation name to a byte string using the color-name callback
- asks the device for a colorant index
- maps absent or out-of-order colorants to alternate-space use or `-1`

Concretization either applies the tint transform and concretizes in the alternate color space or returns the tint as a unit frac for direct separation output.

Overprint retains spot components when overprint is enabled and the separation is not `/All`, with special handling for `/None`.

Serialization writes the separation name, alternate color space, DeviceN map, and separation type; `use_alt_cspace` is intentionally not serialized as intrinsic color-space state.

## Dependencies

Uses function objects, DeviceN map helpers from `gscdevn.h`/`gxcdevn.h`, color-space internals, device colorant callbacks, overprint state, and stream serialization.

## Notable Risks

- `gs_build_Separation` allocates the map but does not itself initialize the alternate space or separation name; callers must complete setup.
- `gx_concretize_Separation` checks a one-element map cache and copies cached concrete values, but the visible path does not update that cache after a miss.
- The raw procedure-based tint transform setter is disabled because serialization only supports function-backed maps.
- Name-string storage returned by `get_colorname_string` is assumed valid for immediate device comparison.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.c -->