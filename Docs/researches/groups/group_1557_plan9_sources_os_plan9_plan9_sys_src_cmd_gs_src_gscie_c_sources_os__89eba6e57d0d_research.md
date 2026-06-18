# Group Research: group_1557_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gscie_c_sources_os__89eba6e57d0d

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. All listed source files were read completely. These files are Ghostscript graphics/color/coordinate support code vendored in the Plan 9 tree, not Plan 9 filesystem code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.c

## Purpose
Core CIE color rendering cache management for Ghostscript. It samples CIE dictionary procedures, builds scalar/vector caches, prepares Color Rendering Dictionaries, and lazily completes joint caches that depend on both the current CIE color space and the current CRD.

## Key Behavior
- Defines default Decode/Encode/Transform/RenderTable procedures and cache-backed procedure variants.
- Initializes and restricts CIEA, CIEABC, CIEDEF, and CIEDEFG client colors.
- Loads DecodeA/ABC/DEF/DEFG/LMN caches when CIE spaces are installed.
- Detects identity and linear cached functions to simplify later mapping.
- Converts scalar caches into vector caches pre-multiplied by matrices.
- Computes interpolation ranges for numerically sensitive cache sections.
- Implements `gs_setcolorrendering`, `gs_currentcolorrendering`, and reference-counted joint-cache unsharing.
- Initializes, samples, and completes CRDs, including EncodeLMN/EncodeABC caches and optional RenderTable/T caches.
- Builds joint caches by folding CIE pipeline stages when identity procedures allow it.
- Provides a special CIE-to-XYZ imager state path used by high-level output code.

## Important Details
- The CIE mapping pipeline is optimized by folding steps backward when DecodeLMN, TransformPQR, or EncodeLMN are identity.
- Cache domain setup adjusts ranges crossing zero so zero maps exactly to a cache slot, avoiding common color default anomalies.
- `gs_cie_jc_complete` reuses completed joint caches by color-space ID and CRD ID where possible.
- `gx_cie_to_xyz_alloc` creates a reduced imager state whose finish procedure returns XYZ-like intermediate values rather than final device color.

## Dependencies
Uses CIE structures from `gscie.h`/`gxcie.h`, color-space and graphics-state internals, device color mapping, matrix math, GC/refcount helpers, and ICC integration hooks.

## Research Notes
This is the main preparation layer; actual hot-path color mapping is in `gsciemap.c`. Several comments mark historical limitations, including preloaded TransformPQR caches preventing range adjustment and XYZ remapping clamping values to `[0..1]`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.h

## Purpose
Defines Ghostscript’s CIE color structures, cache formats, transformation procedure types, CRD representation, joint-cache representation, defaults, constructors, and accessors.

## Key Contents
- Cache configuration:
  - `CIE_LOG2_CACHE_SIZE` defaulting to 9.
  - optional fixed-point cache values when FPU support is poor.
  - interpolation support and thresholds for CIE caches and RenderTables.
- Core math types: `gs_vector3`, column-major `gs_matrix3`, `gs_range3`, and `gs_range4`.
- Procedure types for DecodeA/ABC/DEF/DEFG, DecodeLMN, EncodeLMN/ABC, TransformPQR, and RenderTable.T.
- Scalar cache forms for floats, fracs, and ints; vector caches for matrix-premultiplied values.
- CIE color-space structures for CIEBasedA, ABC, DEF, and DEFG.
- `gs_cie_render`: Color Rendering Dictionary state, including original dictionary fields and derived/cached fields.
- `gx_cie_joint_caches`: shared cache state keyed by color-space ID and CRD ID.
- Sampling helper `SAMPLE_LOOP_VALUE`, cache initialization APIs, CRD state transition APIs, and CIE color-space constructors.

## Important Details
- Matrices are stored in column order and matrix composition is documented as `M2 * M1` for applying `M1` then `M2`.
- DEF and DEFG structures deliberately share the leading ABC/common layout, and the header notes accessors depend on these structure “puns.”
- Constructor comments warn that CIE color-space parameter structures are created with reference count 1, while `gs_setcolorspace` increments again; clients must decrement after setting if they do not want persistent allocation.

## Dependencies
Requires Ghostscript color-space, reference-counting, type, stream/table, and matrix-related headers.

## Research Notes
This header is the contract linking `gscie.c`, `gsciemap.c`, `gscscie.c`, `gscrd.c`, and `gscrdp.c`. It is performance-oriented and encodes many assumptions about cache size, interpolation precision, and shared structure layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsciemap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsciemap.c

## Purpose
Hot-path CIE color rendering. It maps CIEBasedA/ABC/DEF/DEFG client colors through the sampled caches prepared by `gscie.c` into concrete RGB, CMYK, separation, or XYZ-like output.

## Key Behavior
- Converts CIEDEFG and CIEDEF inputs through DecodeDEF[G], table interpolation, RangeABC scaling, DecodeABC/MatrixABC, and final CIE remapping.
- Implements `gx_remap_CIEABC` for efficient rendering into a `gx_device_color`.
- Implements concretization for CIEABC and CIEA.
- `gx_cie_real_remap_finish` performs shared finishing stages:
  - DecodeLMN/MatrixLMN/MatrixPQR,
  - TransformPQR/MatrixPQR inverse/MatrixLMN,
  - EncodeLMN/MatrixABC,
  - EncodeABC,
  - optional RenderTable lookup and RenderTable.T mapping.
- Supports RenderTable interpolation when enabled.
- `gx_cie_xyz_remap_finish` returns the intermediate XYZ path for high-level devices.
- `cie_lookup_mult3` performs cache lookup with optional interpolation and cached matrix contribution addition.

## Important Details
- The `LOOKUP_INDEX` macros are kept macro-based in non-debug builds because this path is extremely time-sensitive.
- DEF/DEFG table inputs are interpolated manually from decoded cached values and then passed to `gx_color_interpolate_linear`.
- Remap finish returns component count: 3 for RGB-like output, 4 for CMYK/4-component RenderTable output.
- ABC remap preserves original color-space values in `pdc->ccolor`.

## Dependencies
Uses CIE cache structures, Ghostscript color-space internals, imager state, device color remapping, arithmetic helpers, and lookup-table interpolation.

## Research Notes
This file assumes the CIE rendering caches are complete or can be completed by `CIE_CHECK_RENDERING`. Its correctness depends heavily on `skipDecodeABC`, `skipDecodeLMN`, `skipPQR`, and `skipEncodeLMN` flags built in the joint caches.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsciemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscindex.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscindex.h

## Purpose
Public client interface for Ghostscript Indexed color spaces.

## Key Contents
- Declares `gs_cspace_build_Indexed`.
- Declares palette/introspection helpers:
  - `gs_cspace_indexed_num_entries`,
  - `gs_cspace_indexed_value_array`,
  - `gs_cspace_indexed_set_proc`,
  - `gs_cspace_indexed_lookup`.

## Important Details
- Documents two modes:
  - byte string table supplied by client,
  - procedure-backed palette with cached float values.
- Notes that for byte-table mode, the client owns the table memory and the color space does not free it.
- Notes that procedure-backed Indexed spaces can use the default palette lookup procedures unless the client overrides them.

## Dependencies
Includes `gscspace.h`.

## Research Notes
The implementation is in `gscolor2.c`. The header describes `gs_cspace_indexed_value_array` as exposing the cached value array for procedure-backed Indexed spaces; the implementation appears to return `0` for `use_proc` spaces, which looks inconsistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscindex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.c

## Purpose
Implements Ghostscript `clipsave` and `cliprestore`.

## Key Behavior
- Defines the clip-stack GC/free descriptor.
- `gs_clipsave` allocates a shared copy of the current clip path and pushes it onto `pgs->clip_stack`.
- `gs_cliprestore` restores the top saved clip path or, if the explicit clip stack is empty, restores from the saved graphics-state clip path.
- Frees clip stack entries iteratively to avoid recursion through deep stack chains.

## Important Details
- If a clip stack entry is uniquely referenced, restore uses `gx_cpath_assign_free`; otherwise it preserves the path and decrements the stack reference count.
- Allocation failure during `clipsave` frees any partially allocated objects before returning `VMerror`.

## Dependencies
Uses graphics state internals, clip-stack internals, clip-path allocation/assignment, fixed/path headers, and Ghostscript reference-count helpers.

## Research Notes
This is graphics-state stack management only. It has no filesystem relevance.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.h

## Purpose
Small public interface for `clipsave` and `cliprestore`.

## Key Contents
- Declares `gs_clipsave(gs_state *)`.
- Declares `gs_cliprestore(gs_state *)`.

## Dependencies
Assumes `gs_state` is already declared by the including context.

## Research Notes
The implementation is entirely in `gsclipsr.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsclipsr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.c

## Purpose
Basic Ghostscript color and transfer-function operators.

## Key Behavior
- Defines GC descriptors for client colors and transfer maps.
- Provides paint initialization helpers for 1, 3, and 4 component spaces.
- Provides `[0..1]` restriction helpers for 1, 3, and 4 component paint values.
- Implements `gs_setgray`, `gs_setrgbcolor`, and `gs_setnullcolor`.
- Implements `gs_settransfer`, `gs_settransfer_remap`, and `gs_currenttransfer`.
- Implements `gx_set_device_color_1` for character-cache rendering.
- Exports `load_transfer_map`, which samples either old-style transfer procs or closure-based maps into `frac` tables.

## Important Details
- `setgray` and `setrgbcolor` temporarily initialize a local device color space and call `gs_setcolorspace`.
- `setnullcolor` is forbidden inside `cachedevice`.
- `gs_settransfer_remap` unshares only the gray map and clears red/green/blue maps, restoring reference counts on allocation failure.
- Transfer values are clamped to a caller-provided minimum and to `1.0`.

## Dependencies
Uses color-space internals, device-color conversion, transfer maps, graphics-state internals, and halftone transfer recalculation.

## Research Notes
This is the base color operator layer; CMYK and multi-channel transfer functions are in `gscolor1.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.h

## Purpose
Public client interface for basic color and transfer routines.

## Key Contents
- Declares gray/RGB/null color routines:
  - `gs_setgray`,
  - `gs_currentgray`,
  - `gs_setrgbcolor`,
  - `gs_currentrgbcolor`,
  - `gs_setnullcolor`.
- Declares transfer-function routines:
  - `gs_settransfer`,
  - `gs_settransfer_remap`,
  - `gs_currenttransfer`.

## Dependencies
Includes `gxtmap.h` for transfer mapping types.

## Research Notes
Some declared current-color routines are implemented elsewhere, not in `gscolor.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.c

## Purpose
Implements Level 1 extended color operators: CMYK color setting, black generation, undercolor removal, and color transfer functions.

## Key Behavior
- `gs_setcmykcolor` switches to DeviceCMYK, clamps component values, clears patterns, and invalidates device color.
- `gs_setblackgeneration_remap` unshares and updates the black-generation transfer map.
- `gs_setundercolorremoval_remap` unshares and updates the undercolor-removal transfer map, sampling with minimum `-1.0`.
- `gs_setcolortransfer_remap` unshares gray/red/green/blue transfer maps, assigns new IDs, updates color-component numbers, optionally samples all maps, and updates effective transfer.
- Provides current-value accessors for black generation, undercolor removal, and color transfer.

## Important Details
- `gs_setcolortransfer_remap` stores a full old transfer structure and restores partially changed references on allocation failure.
- Component names are resolved through `gs_color_name_component_number` for Red, Green, Blue, and Gray, which supports device/component-aware halftone behavior.
- Remap-disabled variants are used by the interpreter when delayed remapping is required.

## Dependencies
Uses `load_transfer_map` from `gscolor.c`, graphics-state internals, halftone types, transfer maps, color-space setup, and device component lookup.

## Research Notes
This file extends `gscolor.c`; it does not define current CMYK color retrieval despite the header declaration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.h

## Purpose
Public client interface for Level 1 extended color facilities.

## Key Contents
- Declares CMYK current/set routines.
- Declares black generation and undercolor removal setters, remap variants, and current accessors.
- Declares color transfer setter, remap variant, and current accessor.

## Dependencies
Requires the base color interface context, especially `gs_mapping_proc`.

## Research Notes
Implementation is primarily in `gscolor1.c`, with current CMYK retrieval implemented elsewhere in the Ghostscript library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.c

## Purpose
Level 2 color operators and Indexed color-space implementation.

## Key Behavior
- Implements `gs_setcolorspace`, `gs_currentcolorspace`, `gs_setcolor`, and `gs_currentcolor`.
- Handles color-space reference counts, install hooks, overprint refresh, color initialization, and device-color invalidation.
- Defines the `Indexed` color-space type descriptor.
- Implements Indexed base-space forwarding for install, overprint, concrete space, and reference adjustment.
- Allocates and frees indexed maps with cached float values.
- Provides default palette lookup functions for 1, 3, 4, and N component base spaces.
- Builds Indexed spaces from either a byte lookup table or an allocated procedure-backed palette.
- Implements Indexed color restriction, lookup, concretization, serialization, and high-level `gs_includecolorspace`.

## Important Details
- `gs_setcolorspace` restores the old color space if installation or overprint update fails.
- Indexed byte-table lookup scales table bytes to floats in `[0..1]`.
- Procedure-backed Indexed spaces use `gs_indexed_map` and can replace the lookup function.
- Serialization writes the base space, hival, `use_proc`, and either map values or raw table data.

## Dependencies
Uses color-space internals, parameter/stream serialization, pattern/high-level device hooks, and Indexed-map GC descriptors.

## Research Notes
`gs_cspace_indexed_value_array` appears inverted relative to its comment and `gscindex.h`: it returns `0` when `use_proc` is true, but then returns `lookup.map->values` in the non-procedure case where `lookup.table` is the active union member. That looks like a bug in this snapshot.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.h

## Purpose
Public client interface for Level 2 color facilities.

## Key Contents
- Includes Indexed color and pattern type declarations.
- Declares general color-space and color APIs:
  - `gs_currentcolorspace`,
  - `gs_setcolorspace`,
  - `gs_currentcolor`,
  - `gs_setcolor`.
- Declares CRD accessors:
  - `gs_currentcolorrendering`,
  - `gs_setcolorrendering`.
- Declares high-level device support API `gs_includecolorspace`.

## Dependencies
Requires `gscspace.h` and `gsmatrix.h`; includes `gscindex.h` and `gsptype1.h`.

## Research Notes
This is the main public bridge from normal color operators to CIE CRD handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor3.c

## Purpose
LanguageLevel 3 color operator support for smoothness and shaded fills.

## Key Behavior
- `gs_setsmoothness` clamps and stores smoothness in the graphics state.
- `gs_currentsmoothness` returns the stored value.
- `gs_shfill` constructs a shading pattern, marks it as an `shfill`, remaps it as a Pattern color, converts the current clipping path into a path, and fills that path.

## Important Details
- The comment explains that `shfill` is implemented through `gs_fill`-style path filling to preserve high-level output behavior.
- The generated pattern intentionally disregards shading Background for `shfill` semantics.
- Pattern references are released after the fill.

## Dependencies
Uses pattern type 2 support, shading structures, clip-path conversion, path filling, pattern remapping, and graphics-state internals.

## Research Notes
This is color/shading rendering glue, not device or filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor3.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor3.h

## Purpose
Public client interface for LanguageLevel 3 color facilities.

## Key Contents
- Forward-declares `gs_shading_t`.
- Declares `gs_setsmoothness`, `gs_currentsmoothness`, and `gs_shfill`.

## Dependencies
Assumes normal Ghostscript scalar and graphics-state types are available.

## Research Notes
The implementation is in `gscolor3.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscompt.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscompt.h

## Purpose
Abstract client interface for Ghostscript compositing objects.

## Key Contents
- Documents compositing as occurring after color correction and before halftoning.
- Forward-declares `gs_composite_t`.
- Declares `gs_composite_id`.

## Important Details
- Concrete compositing subclasses are expected to provide default implementations for devices without optimized compositing support.
- Compositing objects carry unique IDs for cache lookup and equality testing.

## Dependencies
Requires `gs_id` type from the surrounding Ghostscript type environment.

## Research Notes
This is an abstract contract header only; concrete RasterOp/alpha compositing code is elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscompt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.c

## Purpose
Implements Ghostscript coordinate-system and CTM operators.

## Key Behavior
- Maintains CTM, fixed CTM translation, CTM inverse validity, and character-matrix validity.
- Implements:
  - `gs_initmatrix`,
  - `gs_defaultmatrix`,
  - `gs_setdefaultmatrix`,
  - `gs_currentmatrix`,
  - `gs_setmatrix`,
  - `gs_translate`,
  - `gs_scale`,
  - `gs_rotate`,
  - `gs_concat`.
- Implements character matrix routines:
  - `gs_setcharmatrix`,
  - `gs_currentcharmatrix`,
  - `gs_settocharmatrix`.
- Implements forward and inverse point/distance transforms.
- Provides internal helpers:
  - `gx_translate_to_fixed`,
  - `gx_scale_char_matrix`,
  - `gx_matrix_to_fixed_coeff`,
  - `fixed_coeff_mult`.

## Important Details
- `ROUND_CTM_FIXED` adjusts floating translation to exactly match rounded fixed translation, avoiding anomalies such as `0 0 moveto currentpoint` not returning `0 0`.
- Inverse transforms use exact inverse formulas for non-skewed matrices rather than cached inverse matrices for better accuracy.
- `gx_translate_to_fixed` translates the current path when CTM fixed translation is valid; otherwise a nonempty path triggers `limitcheck`.
- `gx_matrix_to_fixed_coeff` chooses scaling to prevent overflow in fixed-point distance transforms.

## Dependencies
Uses matrix math, fixed arithmetic, path translation, graphics-state internals, font character matrices, devices for default matrix, and debug tracing.

## Research Notes
This is core rendering state machinery. Its main risk surface is numerical precision and invalidation correctness for CTM inverse and character matrices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.h

## Purpose
Public interface to graphics-state CTM and coordinate transformation procedures.

## Key Contents
- Declares CTM modification APIs: init/default/current/set matrix, translate, scale, rotate, concat.
- Declares extensions for default matrix and character matrix control.
- Declares point and distance transformation APIs.
- Forward-declares `gs_imager_state` and declares imager-state matrix helpers.

## Dependencies
Requires matrix and graphics-state types from `gsmatrix.h` and `gsstate.h`.

## Research Notes
Implementation is in `gscoord.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscoord.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscparam.c

## Purpose
Default in-memory implementation of Ghostscript parameter lists.

## Key Behavior
- Defines `gs_c_param` entries and `gs_c_param_list` GC descriptors.
- Supports writing typed parameters into a linked list.
- Supports nested dictionaries, integer-key dictionaries, and arrays via child `gs_c_param_list` objects.
- Deep-copies nonpersistent strings, names, int arrays, float arrays, string arrays, and name arrays.
- Tracks requested-but-unwritten parameters using `gs_param_type_any`.
- Supports delegated requested checks through an optional target parameter list.
- Switches lists from write mode to read mode through `gs_c_param_list_read`.
- Reads typed parameters, including nested collections and target fallback.
- Provides int-array to float-array alternate conversion storage for compatible reads.
- Enumerates keys and provides simple read policy/signal/commit hooks.

## Important Details
- `gs_c_param_list_release` recursively frees collection parameters and nonpersistent copied data.
- Nonpersistent string arrays allocate one combined block for array elements plus second-level string data.
- Request tracking distinguishes “requested but undefined” from actual written parameters.
- The implementation assumes parameter lists are transient enough that some allocated blocks do not need rich GC descriptors.

## Dependencies
Uses Ghostscript parameter-list APIs, memory allocation, string helpers, GC relocation/enumeration macros, and error codes.

## Research Notes
This is generic infrastructure heavily used by device parameter serialization, including CRD parameter read/write code in `gscrdp.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpixel.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpixel.c

## Purpose
Defines the internal `DevicePixel` color space, where the color value directly represents a device pixel.

## Key Behavior
- Defines the `DevicePixel` color-space type.
- `gs_cspace_init_DevicePixel` accepts depths 1, 2, 4, 8, 16, 24, and 32.
- Restricts pixel values to `[0, (1 << depth) - 1]`.
- Concretizes by storing the pixel value in `pconc[0]`.
- Remaps concrete pixel color directly with `color_set_pure`.
- Disables overprint for DevicePixel.
- Serializes the color-space type and depth.

## Important Details
- Comments warn there are not enough bits in `float` or `frac` for fully general DevicePixel values.
- Remapping masks the concrete value to the current device depth.

## Dependencies
Uses color-space internals, device color helpers, overprint state update, imager state, and stream serialization.

## Research Notes
This is a low-level escape hatch for direct device-pixel colors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpixel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpixel.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpixel.h

## Purpose
Public interface for initializing a DevicePixel color space.

## Key Contents
- Declares `gs_cspace_init_DevicePixel(gs_memory_t *mem, gs_color_space *pcs, int depth)`.

## Dependencies
Requires `gscspace.h` context for color-space types.

## Research Notes
Implementation is in `gscpixel.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpixel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpm.h

## Purpose
Defines charpath modes and cachedevice status values.

## Key Contents
- `gs_char_path_mode`:
  - normal show,
  - charwidth,
  - false/true charpath,
  - false/true charboxpath.
- `gs_in_cache_device_t`:
  - no cachedevice,
  - cachedevice not caching,
  - not caching with clip,
  - actively caching.

## Important Details
- Default values are explicitly required to be zero for both enums.

## Research Notes
This is a small shared state-definition header for text/path/cachedevice code elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.c

## Purpose
Creates and initializes Ghostscript CIE Color Rendering Dictionaries.

## Key Behavior
- Defines the GC descriptor for `gs_cie_render`.
- Provides default CRD procedures:
  - identity TransformPQR,
  - cache-marker TransformPQR,
  - identity Encode and RenderTable.T.
- Defines cache-backed EncodeLMN/EncodeABC and RenderTable.T procedures.
- Implements TransformPQR procedure-name lookup through device parameters:
  - copies a device prototype,
  - requests the named parameter,
  - reads back a procedure address stored as a string.
- Exposes default CRD procedure constants used by other files.
- `gs_cie_render1_build` allocates and minimally initializes a CRD.
- `gs_cie_render1_init_from` copies full CRD parameters and optionally copies already-sampled cached values from another CRD.
- `gs_cie_render1_initialize` is a convenience wrapper without cache copying.

## Important Details
- The CRD reference-count comment repeats the same API caveat as CIE color spaces: clients usually need to decrement after installing.
- `TransformPQR_from_cache` is a marker; it cannot perform actual lookup because the TransformPQR cache lives in joint caches, not in the CRD.
- Driver-specific TransformPQR lookup depends on matching `driver_name` against registered device names.

## Dependencies
Uses device list/device parameter APIs, C parameter lists, CIE structures, color rendering APIs, refcount/GC helpers, and matrix defaults.

## Research Notes
This file defines CRD object construction; cache sampling/completion is handled by `gscie.c`, and parameter dictionary serialization by `gscrdp.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.h

## Purpose
Public interface for CIE Color Rendering Dictionary creation.

## Key Contents
- Declares `gs_cie_render1_build`.
- Declares `gs_cie_render1_init_from`.
- Declares `gs_cie_render1_initialize`.
- Provides `gs_cie_render_client_data(pcrd)` l-value macro.

## Important Details
- Documents default handling for optional CRD parameter pointers.
- Documents that point/matrix/range/procedure values are copied, while RenderTable lookup table storage is only referenced.
- Documents optional cache copying when procedures are cache-backed and `pfrom_crd` is supplied.

## Dependencies
Includes `gscie.h`.

## Research Notes
Implementation is in `gscrd.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.c

## Purpose
Reads and writes device-specified CIE Color Rendering Dictionaries as parameter dictionaries.

## Key Behavior
- Writes vectors, matrices, ranges, and sampled procedure values into parameter lists.
- `param_write_cie_render1` writes a CRD as a named dictionary parameter.
- `param_put_cie_render1` writes the CRD body directly:
  - `ColorRenderingType`,
  - White/BlackPoint,
  - MatrixPQR/LMN/ABC,
  - RangePQR/LMN/ABC,
  - sampled EncodeLMN/EncodeABC values,
  - optional RenderTable size/table/T sampled values,
  - optional TransformPQR procedure name/data.
- Reads CRDs from named or direct parameter dictionaries.
- Converts sampled EncodeLMN/ABC and RenderTable.T arrays into temporary client-data callbacks.
- Completes CRD initialization/sampling, then replaces those callbacks with cache-backed procedures.

## Important Details
- Only serializable TransformPQR procedures are supported: identity or named device-provided procedure. Arbitrary procedures return `rangecheck`.
- Read path validates RenderTable dimensions and string sizes.
- Temporary `encode_data_t` lives on the stack while CRD caches are being populated; after completion, procedures are switched to `_from_cache`.
- Comments mark questionable persistence handling for TransformPQRData and incomplete RenderTableT writing abstraction.

## Dependencies
Uses CIE/CRD APIs, parameter-list APIs, device names, memory allocation, ranges/matrices, and cache completion from `gscie.c`.

## Research Notes
This file is central to device CRD interoperability. The stack-backed temporary callback scheme is safe only because the CRD is immediately initialized, sampled, and completed before `client_data` is cleared.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.h

## Purpose
Interface for device-specified CIE Color Rendering Dictionaries.

## Key Contents
- Declares CRD parameter write APIs:
  - `param_write_cie_render1`,
  - `param_put_cie_render1`.
- Declares CRD parameter read APIs:
  - `gs_cie_render1_param_initialize`,
  - `param_get_cie_render1`.
- Defines `GX_DEVICE_CRD1_TYPE` as 101.
- Documents the modified PostScript-style CRD dictionary representation used for device parameters.

## Important Details
- Documents `TransformPQRName`/`TransformPQRData` instead of raw TransformPQR procedures.
- Documents sampled array representations for EncodeLMN/ABC and RenderTable.T.
- Notes the representation is subject to change.

## Dependencies
Includes `gscie.h` and `gsparam.h`; forward-declares `gx_device`.

## Research Notes
Implementation is in `gscrdp.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.c

## Purpose
Implements Adobe Type 1 encryption and decryption loops.

## Key Behavior
- `gs_type1_encrypt` encrypts a byte string using `encrypt_next` and updates the caller’s crypt state.
- `gs_type1_decrypt` decrypts a byte string using `decrypt_next` and updates the caller’s crypt state.

## Important Details
- Decryption stores the input byte in a temporary before writing output, allowing in-place decryption when `src == dest`.
- The actual cipher step macros and constants are in `gscrypt1.h`.

## Dependencies
Uses Ghostscript byte/uint types and Type 1 crypt macros.

## Research Notes
This is small font-encryption support code, not general-purpose cryptography.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.h

## Purpose
Public interface and macro implementation for Adobe Type 1 encryption/decryption.

## Key Contents
- Defines `crypt_state` as `ushort`.
- Declares `gs_type1_encrypt` and `gs_type1_decrypt`.
- Defines Type 1 cipher constants:
  - `crypt_c1 = 52845`,
  - `crypt_c2 = 22719`,
  - `crypt_c1_inverse = 27493`.
- Defines encryption/decryption macros:
  - `encrypt_next`,
  - `decrypt_this`,
  - `decrypt_next`,
  - `decrypt_skip_next`,
  - `decrypt_skip_previous`.

## Important Details
- `decrypt_skip_previous` uses the modular inverse to rewind state.

## Research Notes
Implementation of bulk string processing is in `gscrypt1.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscscie.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscscie.c

## Purpose
Defines and constructs Ghostscript CIE color spaces.

## Key Behavior
- Defines GC descriptors for CIE common elements and CIEA/ABC/DEF/DEFG structures.
- Defines color-space type descriptors for:
  - CIEBasedA,
  - CIEBasedABC,
  - CIEBasedDEF,
  - CIEBasedDEFG.
- Implements `gx_concrete_space_CIE`, selecting DeviceRGB unless the current CRD RenderTable outputs 4 components.
- Provides `gx_install_CIE`, which dispatches through the color space’s `install_cspace` hook.
- Adjusts reference counts for each CIE parameter structure.
- Sets common and ABC default values.
- Builds CIE color spaces and parameter structures.
- Assigns lookup tables for CIEDEF/CIEDEFG.
- Serializes CIE common data and each CIE color-space variant.

## Important Details
- Common default WhitePoint is set to BlackPoint because there is no valid default; comments note using such a space gives poor results.
- CIEDEF and CIEDEFG default lookup tables are placeholders intended to fail predictably unless replaced.
- `gx_build_cie_space` is exported for ICC support.
- CIE spaces use `gx_spot_colors_set_overprint`.

## Dependencies
Uses CIE cache structures, color-space internals, device color mapping, graphics-state internals, stream serialization, and refcount/GC helpers.

## Research Notes
Two serialization details look suspicious in this snapshot:
- `gx_serialize_CIEDEFG` serializes only three `DecodeDEFG` caches despite DEFG having four decode components.
- `gx_serialize_lookup_table` writes from `&t->table->data` with `t->table->size`, which appears to write bytes from the pointer field rather than from the table data buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscscie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsel.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsel.h

## Purpose
Defines color operand selection for RasterOp/source-texture color mapping.

## Key Contents
- `gs_color_select_all = -1` for setting only.
- `gs_color_select_texture = 0`.
- `gs_color_select_source = 1`.
- `gs_color_select_count = 2`.

## Important Details
- Comments note source and texture currently mainly differ by halftone phase, but may diverge more in the future.
- Texture selection value `0` is aligned with `currenthtphase`.

## Research Notes
This is a small shared enum header used by remap/color APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.c

## Purpose
Implements Ghostscript Separation color spaces.

## Key Behavior
- Defines the Separation color-space type descriptor.
- Enumerates/relocates alternate color spaces and DeviceN maps for GC.
- Returns the alternate space only when `use_alt_cspace` is active.
- Installs Separation spaces by checking the separation component name against the current device and deciding whether to use the alternate space.
- Updates spot-equivalent colors on the device after installation.
- Sets overprint parameters for spot separations, `All`, and `None`.
- Adjusts reference counts for the tint map and alternate color space.
- Builds Separation spaces over an alternate color space.
- Sets or retrieves tint-transform Functions.
- Initializes Separation color to tint `1.0`.
- Remaps `None` separations to null color.
- Concretizes either through the alternate color space and tint transform or directly to a separation tint.
- Remaps concrete Separation colors directly for devices that support them or through the alternate space otherwise.
- Serializes separation name, alternate space, DeviceN map, and separation type.

## Important Details
- Devices with additive polarity always use the alternate color space for Separations.
- `check_Separation_component_name` populates `pgs->color_component_map` and maps named colorants to device component indexes.
- A colorant found in `SeparationNames` but absent from `SeparationOrder` maps to `-1`.
- `SEP_NONE` paints a null device color.
- The old multi-element separation cache path is removed; comments preserve design notes.

## Dependencies
Uses DeviceN map helpers, Function tint transforms, color-space internals, device colorant lookup, overprint state, device client procs, graphics-state internals, and stream serialization.

## Research Notes
Separation behavior is device-dependent: the same color space can become concrete spot output on a subtractive colorant-aware device or fall back to alternate-space rendering on additive or unsupported devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscsepr.c -->