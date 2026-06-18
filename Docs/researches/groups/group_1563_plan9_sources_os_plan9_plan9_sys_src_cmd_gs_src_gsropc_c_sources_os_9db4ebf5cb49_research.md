# Group Research: group_1563_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gsropc_c_sources_os_9db4ebf5cb49

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`.

This grouped report covers Ghostscript graphics-library files under `sys/src/cmd/gs/src` in the Plan 9 source import. Each file was read completely and is reported in its own finalizer-delimited block.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.c

## Purpose
Implements creation and partial execution of Ghostscript RasterOp compositing objects. It defines `gs_composite_rop_t` object behavior, creates a forwarding compositor device named `"RasterOp compositor"`, and routes fill/copy operations toward RasterOp-capable strip copy routines.

## Public Surface
- `gs_create_composite_rop(gs_composite_t **ppcte, const gs_composite_rop_params_t *params, gs_memory_t *mem)`: allocates a reference-counted RasterOp compositor object, assigns a new id via `gs_next_ids`, stores the logical operation and optional texture, and returns it as `gs_composite_t`.
- `c_rop_create_default_compositor(...)`: composite type hook that creates the default forwarding compositor device around a target device.

## Internal Structure
- `gs_composite_rop_type` supplies composite callbacks: create default compositor, equality, write, read, and default clist update hooks.
- `gx_device_composite_rop` extends a forwarding device with `gs_composite_rop_params_t`.
- `gs_composite_rop_device` is a device descriptor that mostly forwards device operations, while overriding close, rectangle fill, mono/color/alpha copy, and compositor creation.

## Control Flow and Behavior
- Equality compares type, `log_op`, and optional texture equality with `gx_device_color_equal`.
- Serialization callbacks `c_rop_write` and `c_rop_read` are explicitly `NYI`; callers requiring compositor serialization cannot rely on this implementation.
- `c_rop_create_default_compositor` allocates an immovable forwarding device, copies target parameters, installs the target, and stores RasterOp parameters. The code comments say memory-device specialization is intended but not implemented at compositor creation time.
- `dcr_fill_rectangle` is the main implemented imaging path. It chooses `gx_default_strip_copy_rop` by default, switches to memory RasterOp implementations for selected memory-device depths, constructs source/texture color arrays, and calls the strip-copy RasterOp procedure.
- If no texture is supplied, fill color is treated as the texture and source is implicitly absent/black. If a pure or binary-halftone texture is supplied, it is passed as the texture operand. Colored halftones and patterns are not implemented and lead to range errors or comments.
- `dcr_copy_mono`, `dcr_copy_color`, and `dcr_copy_alpha` are temporary pass-throughs to default implementations, so RasterOp composition is not fully applied for those operations here.

## Dependencies
Uses Ghostscript device, memory-device, device-color, and RasterOp internals: `gxdevice.h`, `gxdevmem.h`, `gxdcolor.h`, `gxropc.h`, and memory/type macros from the graphics library. It relies on external `mem_*_strip_copy_rop` procedures imported through `gxropc.h`/memory-device infrastructure.

## Risks and Notes
- `c_rop_write` and `c_rop_read` have no return statements in the source body shown, because they are marked `NYI`; this is a real incomplete implementation risk.
- Memory-device optimized dispatch only handles some depths; 16-bit and 32-bit paths are explicitly not implemented.
- The device under test in `dcr_fill_rectangle` is the compositor device itself, so depth/color checks rely on forwarding-device classification behavior.
- Non-pure/non-binary texture cases are incomplete, especially colored halftones and patterns.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.h

## Purpose
Declares the RasterOp compositing interface used by Ghostscript clients that want to create a logical-operation compositor with an optional texture operand.

## Public Surface
- `gs_composite_rop_params_t`: packs `gs_logical_operation_t log_op` and `const gx_device_color *texture`.
- `gs_create_composite_rop(...)`: factory for `gs_composite_t` RasterOp compositor objects.

## Semantics
- If `texture == 0`, input data are used as the texture and source is implicitly black/zero.
- If `texture != 0`, the texture pointer supplies the texture operand and input data are the source.
- The caller promises the pointed-to texture will not change while used by the compositor.

## Dependencies
Includes `gscompt.h` for generic compositors and `gsropt.h` for logical operation/RasterOp definitions. It forward-declares `gx_device_color` when needed.

## Risks and Notes
- The texture pointer is borrowed and immutable by contract, not owned or copied by the interface. Lifetime violations would affect rendering correctness and equality checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropt.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropt.h

## Purpose
Defines Ghostscript RasterOp and logical-operation types, constants, and Boolean transformation macros. It covers PCL/PostScript-facing 2-input and 3-input RasterOps, transparency flags, render-algorithm packing, and exported RasterOp execution/usage tables.

## Public Surface
- `gs_rop2_t`: 2-input RasterOp enum with source, destination, zero, one, and default source operation.
- `gs_rop3_t`: 3-input RasterOp enum using D, S, and T truth-table encodings.
- `gs_logical_operation_t`: packed integer containing low 8-bit ROP3 code, source/pattern transparency flags, render algorithm bits, and the `lop_pdf14` marker.
- `rop_operand`, `rop_proc`, `rop_usage_t`: operand word type, function-pointer type, and operand usage enum.
- `extern const rop_proc rop_proc_table[256]` and `extern const byte rop_usage_table[256]`.

## Macro Behavior
- ROP truth-table constants are arranged so Boolean C operators on constants produce corresponding ROP codes, provided results are masked appropriately.
- `rop3_invert_*`, `rop3_know_*`, `rop3_swap_S_T`, and `rop3_not` transform ROP truth tables.
- `rop3_use_D_when_*` folds source/texture transparency into a ROP by forcing destination preservation for transparent pixels.
- `rop3_uses_*` and `rop3_is_idempotent` provide compile-time/test macros for usage and idempotence.
- `lop_*` macros extract ROP bits, check S/T use, account for transparency, and handle PDF 1.4 transparency as non-idempotent through `lop_pdf14`.

## Dependencies
Requires Ghostscript base integer and byte typedefs from surrounding includes. It exports data implemented in `gsroptab.c`.

## Risks and Notes
- `TRANSPARENCY_PER_H_P` selects the HP-compatible interpretation where transparency flags can make `lop_uses_S` true even if the raw ROP does not use source. This is intentionally described as bizarre but necessary.
- The packed `gs_logical_operation_t` representation is performance-driven and depends on bit layout stability.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsropt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsroptab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsroptab.c

## Purpose
Defines the complete table of 256 RasterOp procedures and a matching operand-usage table. Each procedure evaluates one 3-input ROP truth table over word-sized operands `D`, `S`, and `T`.

## Public Surface
- `const rop_proc rop_proc_table[256]`: index by low 8-bit ROP code to execute that logical operation.
- `const byte rop_usage_table[256]`: index by ROP code to identify whether D/S/T operands affect the result.

## Implementation
- `ROP_PROC(name, expr)` creates a private `rop_operand` function returning the Boolean expression.
- Helper macros `a`, `o`, and `x` abbreviate AND, OR, and XOR for the more complex RPN-derived expressions.
- Procedures `rop0` through `rop255` cover every possible 3-input Boolean function.
- The procedure table lists the 256 functions in numeric ROP order.
- The usage table was generated by a small included C program using `rop3_uses_D/S/T` macros.

## Dependencies
Includes `stdpre.h` and `gsropt.h`. The formulas rely on `rop_operand` being an unsigned word-sized type so bitwise complement and combination operate on many pixels/bits at once.

## Risks and Notes
- This is a table-driven low-level primitive. Any mismatch between a `ropN` expression and its table index would corrupt rendering for that ROP code.
- The comments note HP/Microsoft RPN names for many operations, but execution relies on the C expressions and table order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsroptab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.c

## Purpose
Implements variable-length little-endian integer serialization utilities used for compact command-list/object encodings.

## Public Surface
- `enc_u_size_uint(uint uval)`: returns byte count for unsigned base-128 encoding.
- `enc_s_size_int(int ival)`: returns byte count for signed encoding, handling minimum integer specially.
- `enc_u_put_uint(uint uval, byte *ptr)`: writes unsigned encoding and returns pointer after it.
- `enc_s_put_int(int ival, byte *ptr)`: writes signed encoding and returns pointer after it.
- `enc_u_get_uint(uint *pval, const byte *ptr)` / `enc_u_get_uint_nc(...)`: decode unsigned from const or non-const byte pointers.
- `enc_s_get_int(int *pval, const byte *ptr)` / `enc_s_get_int_nc(...)`: decode signed from const or non-const byte pointers.

## Encoding Model
- Unsigned values are base-128 little-endian digits with high bit `0x80` as continuation.
- Signed values use bit `0x40` in the first byte as the sign bit and reserve the high bit for continuation.
- Signed minimum integer cannot be negated normally, so size and encode/decode logic treat it as a special boundary case.

## Unit Test Block
Under `UNIT_TEST`, the file contains round-trip tests around powers of two for unsigned and signed values, checking encoded length and decoded equality for const and non-const decoding APIs.

## Dependencies
Includes `stdpre.h`, `gstypes.h`, and `gsserial.h`. Most fast paths are macro-defined in the header; this file supplies fallback/large-value routines.

## Risks and Notes
- Decode routines trust that the input buffer contains a terminating byte; malformed unbounded input could overrun the available buffer because no length parameter is accepted.
- Signed encoding depends on two's-complement-like boundary assumptions embodied by `enc_s_min_int`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.h

## Purpose
Declares and macro-optimizes compact serialization of unsigned and signed integers, including point pairs, for Ghostscript command-list and object serialization code.

## Public Surface
- Unsigned constants: `enc_u_shift`, `enc_u_lim_1b`, `enc_u_lim_2b`, `enc_u_sizew_max`.
- Unsigned sizing macros: `enc_u_sizew`, `enc_u_size2w`, `enc_u_sizexy`.
- Unsigned put/get macros: `enc_u_putw`, `enc_u_put2w`, `enc_u_putxy`, `enc_u_getw`, `enc_u_getw_nc`, `enc_u_get2w`, `enc_u_get2w_nc`, `enc_u_getxy`, `enc_u_getxy_nc`.
- Signed constants: `enc_s_shift0`, `enc_s_shift1`, one-byte/min/max limits, `enc_s_min_int`, `enc_s_sizew_max`.
- Signed sizing and put/get macros: `enc_s_sizew`, `enc_s_sizexy`, `enc_s_putw`, `enc_s_putxy`, `enc_s_getw`, `enc_s_getw_nc`, `enc_s_getxy`, `enc_s_getxy_nc`.
- Function prototypes for slow-path size, encode, and decode routines implemented in `gsserial.c`.

## Implementation Pattern
- Fast macros handle one- and two-byte unsigned cases inline before dispatching to functions for larger values.
- Signed macros inline the single-byte range and use functions for larger values.
- Separate `_nc` decode variants exist because many call sites use const byte pointers but some mutate pointer variables of non-const type.

## Dependencies
Requires Ghostscript `byte`, `uint`, `int`, point-like `.x/.y` structs, and `BEGIN`/`END` macro conventions from included base headers.

## Risks and Notes
- The signed-format documentation has obvious typos (`x >- 0`, multiplication where shift is intended), but the macros and implementation define the actual behavior.
- These macros evaluate pointer arguments mutably and should only be used with lvalue pointer variables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.c

## Purpose
Constructs and validates PDF/PostScript shading objects and provides the shared path/clip/background wrapper used to render shadings through type-specific rectangle fill callbacks.

## Public Surface
- Parameter initializers: `gs_shading_Fb_params_init`, `gs_shading_A_params_init`, `gs_shading_R_params_init`, `gs_shading_FfGt_params_init`, `gs_shading_LfGt_params_init`, `gs_shading_Cp_params_init`, `gs_shading_Tpp_params_init`.
- Constructors: `gs_shading_Fb_init`, `gs_shading_A_init`, `gs_shading_R_init`, `gs_shading_FfGt_init`, `gs_shading_LfGt_init`, `gs_shading_Cp_init`, `gs_shading_Tpp_init`.
- Rendering entry: `gs_shading_fill_path_adjusted(...)`.

## Validation and Initialization
- `check_CBFD` validates color-space component count, BBox ordering, and optional function arity against expected domain dimension and color components.
- `check_mesh` validates mesh data sources. Stream/bit-data sources require accepted coordinate/component bit widths; array data sources bypass bit-depth validation.
- `check_BPF` normalizes array data sources to 2-bit flags and validates stream flag widths of 2, 4, or 8 bits.
- Function-based shading requires an invertible matrix.
- Radial shading rejects equal domain bounds and negative radii.
- Free-form mesh rejects equal coordinate decode bounds when decode is present.
- Lattice mesh requires `VerticesPerRow >= 2`.

## Allocation and GC
- Uses `ALLOC_SHADING` to allocate the concrete shading, set type/procs, copy params, and return a generic `gs_shading_t`.
- Defines GC descriptors for generic and mesh shadings. Mesh GC enumeration relocates `DataSource`, `Function`, and `Decode` in addition to base shading pointers.

## Rendering Control Flow
- `gs_shading_fill_path` allocates a clipping path when the target device's `pattern_manage(..., pattern_manage__shading_area)` indicates clipping should be managed.
- It intersects the device clipping box, optional caller rectangle, shading BBox, and optional path.
- Axis-aligned BBoxes can be folded into the fixed clipping rectangle; otherwise a temporary path is built and intersected.
- If `Background` is set and requested, it remaps background color into a device color and fills the clip box before rendering the shading.
- It converts device fixed clip bounds back to user-space rectangle and calls `gs_shading_fill_rectangle(psh, ...)`, dispatching through the shading's procedure table.

## Dependencies
Uses color spaces, functions, data sources, device clipping, paths, pattern/shading helpers, and rendering callbacks from `gxshade*` modules. Type-specific fill implementations are external (`gxshade1.c`, `gxshade4.c`, `gxshade6.c`, etc.).

## Risks and Notes
- The background fill comment warns it is wrong for non-idempotent RasterOps.
- Actual shading algorithms are not in this file; this file only constructs objects and prepares clipping/background for dispatch.
- Domain-superset checking for functions is intentionally not enforced to match Adobe behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.h

## Purpose
Defines the public shading parameter structures, generic shading type/procedure model, per-shading constructors, and the single public path-fill rendering entry point.

## Public Surface
- `gs_shading_type_t`: shading types 1 through 7: function-based, axial, radial, free-form Gouraud triangle, lattice-form Gouraud triangle, Coons patch, tensor-product patch.
- `gs_shading_params_t`: common `ColorSpace`, optional `Background`, optional `BBox`, and `AntiAlias`.
- `gs_shading_procs_t` and `SHADING_FILL_RECTANGLE_PROC`: per-type rectangle rendering callback contract.
- Concrete parameter structs for each shading type.
- Parameter initialization and constructor prototypes for all seven types.
- `gs_shading_fill_path_adjusted(...)`: fill path/rectangle with a shading.

## Data Model
- `gs_shading_t` is a generic header plus common params; concrete public structs are represented by type-specific parameter structs and private implementation structs declared in internal headers.
- Mesh shadings share `gs_shading_mesh_params_common`: `DataSource`, coordinate/component bit depths, `Decode`, and optional `Function`.
- GC descriptor macros are provided for generic, function, axial/radial, mesh, and concrete mesh shading structs.

## Dependencies
Includes client color, color space, data source, function, matrix, and fixed-point headers. It forward-declares `gx_device`, `gx_path`, `gs_imager_state`, and `gs_shading_t` as needed.

## Risks and Notes
- Clients are responsible for setting required fields marked by comments before calling constructors.
- `gs_shading_fill_rectangle` may paint outside the requested user-space rectangle unless the caller has prepared clipping; the public path-fill routine handles this for external callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsshade.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.c

## Purpose
Implements Ghostscript graphics-state lifecycle, save/restore stack behavior, copying, overprint updates, initialization, and miscellaneous state controls.

## Public Surface
- Allocation/free: `gs_state_alloc`, `gs_state_free`.
- Save/restore: `gs_gsave`, `gs_grestore`, `gs_grestore_only`, `gs_gsave_for_save`, `gs_grestoreall_for_restore`, `gs_grestoreall`.
- Copying: `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, `gs_setgstate`.
- Accessors/swaps: `gs_state_memory`, `gs_state_saved`, `gs_state_swap_saved`, `gs_state_swap_memory`, `gx_get_clip_path_id`.
- Overprint: `gs_state_update_overprint`, `gs_do_set_overprint`, `gs_setoverprint`, `gs_currentoverprint`, `gs_setoverprintmode`, `gs_currentoverprintmode`.
- Initialization and misc: `gs_initgraphics`, `gs_setfilladjust`, `gs_currentfilladjust`, `gs_setlimitclamp`, `gs_currentlimitclamp`, `gs_settextrenderingmode`, `gs_currenttextrenderingmode`.

## Storage Model
The file documents graphics-state storage ownership in detail:
- The `gs_state` object itself is stack-owned.
- Some pointers are GC-managed and not reference-counted, such as fonts/devices in some contexts.
- Shared objects such as halftones, color rendering, transfer functions, clip stacks, and masks are reference-counted.
- Per-state private objects include path, clip paths, color space, client color, device color, and dash pattern.
- Path/clip/color sub-objects require custom reference or count adjustment when copied.

## Allocation and Initialization
- `gs_state_alloc` creates a state, initializes the imager state, halftone, path, clip/view/effective clip paths, default DeviceGray color space, null device, alpha, transfer, flatness, fill adjust, line settings, font placeholders, and transparency stack fields.
- Paths use stable memory through `gstate_path_memory` to survive `save ... restore` patterns involving Type 3 `setcachedevice`.
- `gs_initgraphics` resets matrix, path, clipping, line parameters, dash/dot settings, miter limit, and RasterOp state, but intentionally does not reset color or color space.

## Save/Restore Control Flow
- `gs_gsave` clones the current state, clears the cloned clip stack, increments the device-filter stack, links it as `pgs->saved`, and increments level.
- `gs_gsave_for_save` additionally clones view clipping, then cuts the stack so `grestore` cannot cross a PostScript `save` boundary.
- `gs_grestore_only` restores the saved state by swapping client data, copying client data for grestore, freeing current contents, assigning from saved, preserving transparency stack, freeing the saved shell, and updating overprint when needed.
- `gs_grestore` maintains the invariant that at least one saved state remains on the stack by doing a new `gsave` after bottom restore.
- `gs_grestoreall_for_restore` unwinds to the save boundary, frees pattern cache contents to avoid dangling references, splices the old stack, drops view clip, and restores twice.

## Copy/Clone Internals
- `gstate_alloc_parts` allocates or shared-allocates path and clipping structures, private color space, client color, and device color.
- `gstate_clone` copies the full state, duplicates dash patterns, copies client data through client callbacks, increments device refs, swaps private parts for `gsave`, and adjusts color-space reference counts.
- `gstate_copy` copies one allocated state into another while preserving destination allocator, saved pointer, pattern cache fallback, dash storage, and client data.
- `gstate_free_contents` decrements ref-counted device/clip/filter stacks, adjusts color-space counts, frees client data, dash pattern, private parts, and releases imager-state contents.

## Overprint
- `gs_state_update_overprint` creates an overprint compositor and asks the current device to create/update a compositor device; if a new device is returned it becomes current.
- `gs_do_set_overprint` delegates to pattern color handling or color-space `set_overprint`, depending on current color space and pattern state.
- Overprint mode is range-checked to 0 or 1 and triggers recomputation only when active and changed.

## Dependencies
This file is central to Ghostscript graphics state and depends on imager state, paths, clip paths, devices, halftones, color spaces, pattern cache, overprint compositors, line state, and memory/reference-count utilities.

## Risks and Notes
- The save/restore logic is ownership-sensitive; incorrect changes can double-free paths, lose client data, or leave dangling clip/pattern references.
- `gs_setgstate` temporarily nulls view clip to prevent refcount decrementing, then restores saved state metadata.
- The file carries historical compatibility decisions, including color not being reset by `initgraphics`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.h

## Purpose
Declares the public Ghostscript graphics-state API for allocation, save/restore, copy/setgstate, overprint, graphics initialization, device/color/halftone/line controls, and miscellaneous state fields.

## Public Surface
- Opaque `gs_state`.
- Opaque `gs_overprint_params_t`.
- Lifecycle: `gs_state_alloc`, `gs_state_free`.
- Save/restore/copy: `gs_gsave`, `gs_grestore`, `gs_grestoreall`, `gs_grestore_only`, `gs_gsave_for_save`, `gs_grestoreall_for_restore`, `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, `gs_setgstate`.
- Overprint: `gs_state_update_overprint`, `gs_currentoverprint`, `gs_setoverprint`, `gs_currentoverprintmode`, `gs_setoverprintmode`, `gs_do_set_overprint`.
- Initialization: `gs_initgraphics`.
- Halftone phase: `gs_setscreenphase`, `gs_currentscreenphase`, `gx_imager_setscreenphase`, plus `gs_sethalftonephase` and `gs_currenthalftonephase` macros.
- Misc: fill adjust, limit clamp, text rendering mode, cache-device status.

## Dependencies
Includes downstream public headers for devices, lines, colors, halftone screens, color selection, color pattern/mask support, and cache-device mode.

## Risks and Notes
- This header intentionally exposes a broad graphics-state surface while keeping the structure opaque. Internal code requiring fields uses `gzstate.h` instead.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstruct.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstruct.h

## Purpose
Defines Ghostscript's structure descriptor and GC pointer-enumeration macro system. Modules use these macros to declare how allocated C structs are traced, relocated, finalized, and composed from super/substructures.

## Public Surface
- Pointer procedure model: `gs_ptr_procs_s`, `ptr_struct_type`, `ptr_string_type`, `ptr_const_string_type`.
- GC root struct: `gs_gc_root_s` and `public_st_gc_root_t`.
- GC relocation procedure-vector model: `gc_procs_common_t` and `gc_proc`.
- Standard descriptors: `extern_st(st_free)`, `st_bytes`, `st_gc_root_t`, const string element descriptors.
- Descriptor declaration scopes: `public_st`, `private_st`.
- Basic GC table representation: `gc_ptr_type_index_t`, `gc_ptr_element_t`, `gc_struct_data_t`.
- Large macro families for descriptor creation, enum/reloc procedure writing, simple structures, complex structures, composites, element arrays, pointer wrappers, fixed pointer-count structures, suffix subclasses, and general subclasses.

## Descriptor Model
- Every GC-visible structure has a `gs_memory_struct_type_t` descriptor containing size, name, optional shared procedures, clear/enum/reloc/finalize procedures, and procedure data.
- Basic table-driven descriptors list pointer/string fields by offset and use shared `basic_enum_ptrs` / `basic_reloc_ptrs`.
- Composite descriptors can provide hand-written enum/reloc procedures.
- Subclass macros support two layouts: suffix subclasses where the superclass is at offset 0, and general subclasses where the superclass is a named member at a nonzero offset.

## Enumeration and Relocation Macros
- `ENUM_PTRS_BEGIN`, `ENUM_PTRS_WITH`, `ENUM_PTR`, `ENUM_STRING_PTR`, and related macros build switch-based pointer enumerators.
- `RELOC_PTRS_BEGIN`, `RELOC_PTRS_WITH`, `RELOC_PTR`, `RELOC_STRING_PTR`, and related macros build relocation procedures.
- `ENUM_USING` / `RELOC_USING` delegate enumeration/relocation to another structure descriptor, supporting embedded structures.
- Offset relocation macros handle pointers into the middle of relocatable objects.

## Structure Definition Macros
- `gs_public_st_simple` / `gs_private_st_simple`: no internal pointers.
- `gs_*_st_basic*`: table-defined pointer/string fields, optional superclass and finalization.
- `gs_*_st_composite*`: hand-written enum/reloc, optional finalization.
- `gs_*_st_element`: arrays of structures whose base descriptor has a fixed pointer count.
- `gs_*_st_ptr`: object that is itself just a pointer.
- `gs_*_st_ptrsN`, `gs_*_st_const_stringsN`, and mixed macros cover common fixed pointer/string counts.
- `gs_*_st_suffix_addN` and `gs_*_st_ptrs_addN` cover subclass descriptors with extra traceable fields.

## Dependencies
Requires `gsstype.h` and Ghostscript base memory/string typedefs. It assumes supporting functions/macros from the memory manager, GC, and compiler-compatibility layers.

## Risks and Notes
- This is macro infrastructure used across the Ghostscript library. Small changes can affect garbage collection correctness globally.
- The file documents conventions for placing structure definition, descriptor externs, and descriptor macros together; violating those conventions can hide GC descriptors or make allocation unsafe.
- Some finalization inheritance comments describe hacks and historical constraints in the descriptor format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstruct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstype.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstype.h

## Purpose
Defines the core `gs_memory_struct_type_t` descriptor type and procedure signatures used by Ghostscript's garbage-collected allocator to clear marks, enumerate pointers, relocate pointers, and finalize structures.

## Public Surface
- Opaque `gc_state_t`.
- `enum_ptr_t`: returned pointer plus optional size for string pointers.
- `EV_CONST`: compatibility macro currently defined as `const`.
- Procedure signature macros: `struct_proc_clear_marks`, `struct_proc_enum_ptrs`, `struct_proc_reloc_ptrs`, `struct_proc_finalize`.
- `gs_memory_struct_type_s`: structure descriptor containing object size, name, optional shared procedures, clear/enum/reloc/finalize callbacks, and procedure data.
- `extern_st(st)`: descriptor extern declaration macro.

## Dependencies
Uses Ghostscript typedefs for memory, structure names, pointer types, and unsigned sizes from surrounding base headers.

## Risks and Notes
- Finalizers are constrained: they must not allocate or resize managed objects and must not assume managed referents still exist.
- The descriptor definition is placed here because some compilers mishandled undefined structure types when using `extern_st`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.c

## Purpose
Implements Ghostscript's generic driver text interface support. It validates text parameters, initializes and manages text enumerators, wraps PostScript-equivalent text operators, updates device color, forwards text processing through enumerator procedure tables, and supplies default font callbacks.

## Public Surface
- Text begin APIs: `gx_device_text_begin`, `gs_text_begin`.
- Enumerator initialization/copy: `gs_text_enum_init`, `gs_text_enum_copy_dynamic`.
- PostScript-equivalent begin wrappers: `gs_show_begin`, `gs_ashow_begin`, `gs_widthshow_begin`, `gs_awidthshow_begin`, `gs_kshow_begin`, `gs_xyshow_begin`, `gs_glyphshow_begin`, `gs_cshow_begin`, `gs_stringwidth_begin`, `gs_charpath_begin`, `gs_charboxpath_begin`, `gs_glyphpath_begin`, `gs_glyphwidth_begin`.
- Processing APIs: `gs_text_restart`, `gs_text_resync`, `gs_text_process`, `gs_text_update_dev_color`.
- Accessors: current font/char/glyph, next char, total width, replaced width, width-only test, current width.
- Cache APIs: `gs_text_set_cache`, `gs_text_setcharwidth`, `gs_text_setcachedevice`, `gs_text_setcachedevice2`, `gs_text_retry`.
- Release/defaults: `gx_default_text_release`, `rc_free_text_enum`, `gs_text_release`, `gs_default_init_fstack`, `gs_default_next_char_glyph`, `gs_no_build_char`.

## GC Support
- `public_st_gs_text_params` enumerates the active input pointer based on `TEXT_FROM_*` flags and width arrays when `TEXT_REPLACE_WIDTHS` is set.
- `public_st_gs_text_enum` enumerates device pointers, imager state, fonts, path, device color, clip path, font-cache pair base, font stack entries, and embedded text parameters.
- Relocation handles device pointer relocation, embedded parameter relocation, font stack entries, and cached pair pointers that may point into an array element.

## Control Flow
- `gx_device_text_begin` rejects invalid operation masks, strips path/clip arguments when not needed, and calls the device's `text_begin` procedure.
- `gs_text_begin` computes effective clip path for drawing, loads the current device color even for width-only operations because high-level devices may accumulate Type 3 charstrings, and calls `gx_device_text_begin`.
- `gs_text_enum_init` copies immutable text parameters and common context into the enumerator, initializes dynamic state through the font's `init_fstack`, and increments the device reference.
- `gs_text_enum_copy_dynamic` copies current font, indices, font stack, metrics hints, cached pair pointer, and optional returned data for subsidiary enumerators.
- Operator wrappers build a `gs_text_params_t` with appropriate source, width adjustment, draw/path/width flags, and pass it to `gs_text_begin`.
- `text_do_draw` maps text rendering mode 3 to `TEXT_DO_NONE`, otherwise drawing.
- Restart/resync/processing/cache operations dispatch through `pte->procs`.

## Character Handling
- `gs_default_next_char_glyph` reads the next item from string/bytes/chars/glyphs/single-char/single-glyph sources, increments `pte->index`, and returns 2 at end.
- Glyph-based operations set `FontBBox_as_Metrics2` for CID encrypted/TrueType fonts to support metrics fallback.

## Dependencies
Depends on devices, fonts, font cache, paths, device colors, graphics state internals, and text enumerator definitions in `gxtext.h`.

## Risks and Notes
- Text rendering itself is not implemented here; device/font-specific enumerator procedures do the actual processing.
- The code intentionally loads device color for stringwidth-like operations because high-level Type 3 accumulation can need color despite no visible drawing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.h

## Purpose
Declares the driver-facing text interface: text source/operation flags, parameter structure, text begin/process/release APIs, return codes for client intervention, and glyph cache metric APIs.

## Public Surface
- Validation macros: `TEXT_HAS_MORE_THAN_ONE_`, `TEXT_OPERATION_IS_INVALID`, `TEXT_PARAMS_ARE_INVALID`.
- Source flags: `TEXT_FROM_STRING`, `TEXT_FROM_BYTES`, `TEXT_FROM_CHARS`, `TEXT_FROM_GLYPHS`, `TEXT_FROM_SINGLE_CHAR`, `TEXT_FROM_SINGLE_GLYPH`.
- Width flags: `TEXT_ADD_TO_ALL_WIDTHS`, `TEXT_ADD_TO_SPACE_WIDTH`, `TEXT_REPLACE_WIDTHS`.
- Result/action flags: `TEXT_DO_NONE`, `TEXT_DO_DRAW`, `TEXT_DO_CHARWIDTH`, false/true charpath and charboxpath flags.
- Other flags: `TEXT_INTERVENE`, `TEXT_RETURN_WIDTH`.
- `gs_text_params_t`: immutable input descriptor with source union, size, width adjustment fields, space char/glyph, replacement width arrays, and width array size.
- `dev_proc_text_begin` / `gx_device_text_begin`: device text-begin contract.
- Begin wrappers for PostScript text operators and generic `gs_text_begin`.
- Processing return codes: `TEXT_PROCESS_RENDER`, `TEXT_PROCESS_INTERVENE`, `TEXT_PROCESS_CDEVPROC`.
- Accessors, width queries, cache-control APIs, retry, and release.

## Semantics
- Exactly one `TEXT_FROM_*` and one `TEXT_DO_*` family member must be present.
- Single char/glyph sources must have `size == 1`.
- Additive width adjustment and replacement widths are mutually exclusive.
- `TEXT_PROCESS_RENDER` requires the client to render the current char/glyph and resume.
- `TEXT_PROCESS_INTERVENE` supports `kshow`/`cshow`-style between-character callbacks.
- `TEXT_PROCESS_CDEVPROC` asks the caller to execute CDevProc and feed results back through enumerator fields.

## Dependencies
Includes character-code and cache-device headers and forward-declares graphics state, device, imager, font, path, clip path, and device color types.

## Risks and Notes
- `widths_size` is marked probably unnecessary, suggesting historical API uncertainty.
- The operation mask is flexible, but only a constrained subset is valid; callers must use validation before relying on fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstparam.h

## Purpose
Defines shared transparency parameter types: blend modes, transparency stack state headers, cached mask headers, group parameters, mask parameters, serialized mask parameters, and opacity/shape channel selection.

## Public Surface
- `gs_blend_mode_t`: PDF-style blend modes from Compatible/Normal through Color, with `MAX_BLEND_MODE`.
- `GS_BLEND_MODE_NAMES`: string names matching the enum.
- `gs_transparency_state_type_t`: group or mask state.
- `gs_transparency_state_t`: common saved/type stack node.
- `gs_transparency_mask_t`: reference-counted cached mask common header.
- `gs_transparency_group_params_t`: group `ColorSpace`, `Isolated`, and `Knockout`.
- `gs_transparency_mask_subtype_t`: Alpha or Luminosity.
- `gs_transparency_mask_params_t`: mask subtype, background components/colors, gray background, transfer function callback, and transfer function data.
- `gx_transparency_mask_params_t`: post-command-list representation with sampled 256-entry transfer function.
- `gs_transparency_channel_selector_t`: opacity or shape.

## Dependencies
Includes client color max component definitions and reference-count headers. Forward-declares color space and function types.

## Risks and Notes
- Comments require updating initialization routines if group or mask parameter structures change.
- `MASK_TRANSFER_FUNCTION_SIZE` fixes transfer-function sampling at 256 entries for command-list/post-clist mask parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.c

## Purpose
Implements non-rendering transparency state management and PDF 1.4 compositor request packaging. It updates graphics-state transparency fields, begins/ends groups and masks, samples transfer functions, and forwards imager-level transparency operations to device procedures.

## Public Surface
- State setters/getters: `gs_setblendmode`, `gs_currentblendmode`, `gs_setopacityalpha`, `gs_currentopacityalpha`, `gs_setshapealpha`, `gs_currentshapealpha`, `gs_settextknockout`, `gs_currenttextknockout`.
- Stack query: `gs_current_transparency_type`.
- Group APIs: `gs_trans_group_params_init`, `gs_begin_transparency_group`, `gx_begin_transparency_group`, `gs_end_transparency_group`, `gx_end_transparency_group`.
- Mask APIs: `gs_trans_mask_params_init`, `gs_begin_transparency_mask`, `gx_begin_transparency_mask`, `gs_end_transparency_mask`, `gx_end_transparency_mask`, `gs_init_transparency_mask`, `gx_init_transparency_mask`.
- Device push/pop: `gs_push_pdf14trans_device`, `gs_pop_pdf14trans_device`.
- Layer discard stub: `gs_discard_transparency_layer`.

## Control Flow
- Setters clamp alpha values to `[0,1]`, range-check blend mode, and update fields in `gs_state`.
- `gs_state_update_pdf14trans` calls `send_pdf14trans` with `gs_pdf14trans_params_t`; if a new compositor device is returned, it installs it in the graphics state.
- `gs_begin_transparency_group` fills PDF14 params with group isolation/knockout, current opacity/shape/blend mode, and BBox, then sends `PDF14_BEGIN_TRANS_GROUP`.
- `gx_begin_transparency_group` is the imager-side counterpart; it validates background component count, copies opacity/shape/blend mode into `pis`, and calls the device `begin_transparency_group` proc if present.
- Mask begin initializes PDF14 params, copies background arrays, detects identity transfer function, samples the transfer function into 256 bytes, and sends `PDF14_BEGIN_TRANS_MASK`.
- `gx_begin_transparency_mask` converts PDF14 params into `gx_transparency_mask_params_t` and calls the device proc if available.
- Mask init clears the selected opacity/shape mask reference in the imager state.
- Push/pop device APIs send PDF14 push/pop opcodes without other parameters.

## Internal Stack Code
- A simple `gs_transparency_state_t` descriptor is defined.
- `PUSH_TS` is `0`, so `push_transparency_stack` is compiled out.
- `pop_transparency_stack` frees the current transparency stack node. `gs_discard_transparency_layer` calls this but is marked `NYI, DUMMY`; without stack pushes in this file, it only works if another path populated `pgs->transparency_stack`.

## Dependencies
Uses `gstrans.h`, graphics state internals, devices, and PDF14 compositor support from `gdevp14.h`.

## Risks and Notes
- Group color space is currently not used for blending; comments say blending color space is based on the process color model of the output device.
- Transfer-function sampling ignores callback return codes; the code calls `TransferFunction` and converts `out` directly.
- `gs_discard_transparency_layer` is explicitly incomplete/dummy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.h

## Purpose
Declares Ghostscript transparency compositor operations, PDF14 compositor parameter structure, transparency source state, graphics-state APIs, imager-level device hooks, and buffer-size estimation macros.

## Public Surface
- `pdf14_compositor_operations`: push/pop device, begin/end group, init/begin/end mask, set blend params.
- `PDF14_OPCODE_NAMES`: debug/display names for opcodes.
- Serialization change bits: `PDF14_SET_BLEND_MODE`, `PDF14_SET_TEXT_KNOCKOUT`, `PDF14_SET_SHAPE_ALPHA`, `PDF14_SET_OPACITY_ALPHA`.
- `gs_transparency_source_t`: constant alpha plus optional mask pointer.
- `gs_pdf14trans_params_t`: all fields needed to transmit a PDF 1.4 transparency operation through a compositor.
- `gs_pdf14trans_t`: compositor object with `gs_composite_common` and PDF14 params.
- Graphics-state transparency APIs and imager-level group/mask APIs.
- `gs_is_pdf14trans_compositor`.
- Buffer estimate macros: `NUM_PDF14_BUFFERS`, `NUM_ALPHA_CHANNELS`, `NUM_COLOR_CHANNELS`, `BITS_PER_CHANNEL`, `ESTIMATED_PDF14_ROW_SIZE`, `ESTIMATED_PDF14_ROW_SPACE`.

## Data Model
- PDF14 params combine operation selector, changed flags, group flags/BBox, channel selector, mask subtype/background/transfer function, blend parameters, opacity/shape sources, and `mask_is_image`.
- The row-space estimate assumes three buffers, one alpha channel, four color channels, and 8 bits per channel.

## Dependencies
Includes `gstparam.h` and `gxcomp.h`, and relies on `gs_state`, `gs_imager_state`, `gx_device`, `gs_rect`, and color/function types from included/forward-declared headers.

## Risks and Notes
- The buffer estimate is explicitly a hack and may underestimate real PDF transparency working space.
- Typo comments (`trasnparency`, `numbe`, `chanels`) do not affect behavior but reflect the vintage/source state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.c

## Purpose
Reads and validates trapping parameters from a Ghostscript parameter list into a `gs_trap_params_t` structure.

## Public Surface
- `gs_settrapparams(gs_trap_params_t *pparams, gs_param_list *plist)`: copies current params, applies any supplied parameter-list updates, validates ranges, and commits changes only if no error remains.

## Implementation
- `check_unit` accepts floats in `[0,1]`.
- `check_positive` accepts floats greater than zero.
- `trap_put_float_param` reads a float parameter, applies a validation callback, signals parameter errors, and preserves an accumulated error code.
- `gs_settrapparams` updates BlackColorLimit, BlackDensityLimit, BlackWidth, Enabled, ImageInternalTrapping, ImagemaskTrapping, ImageResolution, ImageToObjectTrapping, ImageTrapPlacement, SlidingTrapLimit, StepLimit, TrapColorScaling, and TrapWidth.
- Enum parsing for `ImageTrapPlacement` uses names from `gs_trap_placement_names`.
- `ImageResolution` is separately range-checked to be positive.

## Dependencies
Uses `gsparamx.h` parameter helpers, `gstrap.h` parameter definitions, and Ghostscript error codes.

## Risks and Notes
- This file sets parameters only; it does not implement trapping-zone rendering.
- Commit-on-success behavior avoids partially updating the caller's trap params when validation fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.h

## Purpose
Defines trapping placement enums, trapping parameter structures, trapping zones, and the API for setting trap parameters from a parameter list.

## Public Surface
- `gs_trap_placement_t`: Center, Choke, Spread, Normal.
- `gs_trap_placement_names`: string names for enum parameter parsing.
- `gs_trap_params_t`: trapping parameters including black limits/width, enable flags, image trapping behavior, resolution, placement, sliding/step/color scaling limits, and trap width.
- `gs_trap_zone_t`: parameter set plus path pointer for a zone, marked subject to change.
- `gs_settrapparams(gs_trap_params_t *params, gs_param_list *list)`.

## Dependencies
Includes `gsparam.h` and forward-declares `gx_path`.

## Risks and Notes
- Several fields are commented out rather than represented (`ColorantZoneDetails`, `HalftoneName`), so this is a partial trapping model.
- `gs_trap_zone_t` is explicitly unstable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.c

## Purpose
Implements the Adobe Type 1 charstring interpreter. It decodes encrypted or plain Type 1 charstrings, handles subroutines and escape operators, delegates hint/path operations to the Type 1 hinter, and returns positive intervention codes for caller-managed behavior such as side-bearing width and unknown OtherSubrs.

## Public Surface
- `gs_type1_interpret(gs_type1_state *pcis, const gs_glyph_data_t *pgd, int *pindex)`: continue interpreting a Type 1 charstring. Returns 0 for completion, negative Ghostscript errors, or positive Type 1 result codes.

## Initialization and State
- Uses `pcis->init_done` to initialize the hinter and finish Type 1 state setup on first/continued calls.
- Sets hinter mapping from imager CTM and font matrices, scale/subpixel values, origin, and alignment-to-pixels setting.
- Loads Type 1 font data into the hinter with grid-fitting control.
- Maintains operand stack `cstack`, charstring instruction stack `ipstack`, decryption state, current instruction pointer, and origin.

## Number Decoding
- Decodes Type 1 one-byte, two-byte positive/negative, and four-byte numeric encodings.
- Handles rare oversized four-byte values by recognizing an immediate denominator followed by `escape div` and pushing a fixed-point quotient.
- Pushes decoded fixed-point values to the charstring operand stack with stack overflow checks via macros from Type 1 internals.

## Main Operators
- `callsubr`: applies `subroutineNumberBias`, obtains subroutine data via `pdata->procs.subr_data`, saves current IP/decryption state, and enters the subroutine.
- `return`: frees current glyph data and resumes previous instruction stack frame.
- Stem/path ops (`hstem`, `vstem`, `rmoveto`, `rlineto`, `rrcurveto`, `vhcurveto`, `hvcurveto`, `closepath`) call `t1_hinter__*`.
- `endchar`: ends hinting, optionally handles `seac` accent flow, sets current point from path, and calls `gs_type1_endchar`.
- `hsbw` and escaped `sbw`: set side bearing/width via hinter and `gs_type1_sbw`, save interpreter continuation state, and return `type1_result_sbw` so the client may intervene.

## Escape Operators
- `dotsection`, `vstem3`, `hstem3`: delegate to hinter.
- `seac`: calls `gs_type1_seac`; may return to caller with accent index or restart with composed glyph data.
- `div`: divides top operands.
- `callothersubr`: implements recognized OtherSubrs internally:
  - 0, 1, 2: Flex begin/points/end.
  - 3: drop hints.
  - 12, 13: counter control ignored.
  - 14-18: Multiple Master blend with 1, 2, 3, 4, or 6 results.
  - Unrecognized OtherSubrs copy arguments to the caller through `push_values`, save interpreter state/operand stack, store the OtherSubr number in `*pindex`, and return `type1_result_callothersubr`.
- `pop`: either consumes ignored pops after known OtherSubrs or obtains a value from caller callback `pop_value`.
- `setcurrentpoint`: updates hinter current point and applies accent displacement.

## Dependencies
Depends on Type 1 font data (`gxfont1.h`, `gxtype1.h`), Type 1 encryption macros, glyph data management, fixed-point arithmetic, imager/path state, and the Type 1 hinter API in `gxhintn.h`.

## Risks and Notes
- The interpreter trusts many helper macros and callback contracts for stack bounds, data lifetime, and glyph/subroutine lookup.
- Some historical font compatibility hacks are explicit: `undoc15`, Flex handling, Fontographer side-bearing adjustment during `seac`.
- Counter control OtherSubrs are not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.h

## Purpose
Declares the client interface and shared opcode definitions for Type 1 and Type 2 charstring interpreters.

## Public Surface
- `crypt_charstring_seed`: Type 1 charstring decryption seed.
- Opaque `gs_type1_state`, `gx_path`, `gs_font_type1`, and `gs_type1_data_s` declarations.
- Initialization/configuration APIs: `gs_type1_interp_init`, `gs_type1_set_callback_data`, `gs_type1_set_lsb`, `gs_type1_set_width`.
- Backward-compatible `gs_type1_init` macro.
- Interpreter result codes: `type1_result_sbw`, `type1_result_callothersubr`.
- `charstring_interpret_proc` and function-pointer typedef.
- Interpreter prototypes: `gs_type1_interpret`, `gs_type2_interpret`.

## Charstring Encoding Definitions
- `char_num_command` defines numeric opcode ranges for one-byte numbers, two-byte positive/negative numbers, and related value macros.
- `char_command` defines shared Type 1/Type 2 opcodes, Type 1-only commands, Type 2-only commands, and undefined-case macros for each interpreter.
- `char1_command_names` and `char2_command_names` provide debug names.
- `char1_extended_command` enumerates Type 1 escape commands such as `dotsection`, `vstem3`, `hstem3`, `seac`, `sbw`, `div`, `callothersubr`, `pop`, and `setcurrentpoint`.
- `char2_extended_command` enumerates Type 2 escape commands including logical/math/stack ops and flex variants.

## Dependencies
Uses Ghostscript glyph data, imager state, log2 scaling, path, font, fixed data, and charstring internals through surrounding includes in implementation files.

## Risks and Notes
- The header intentionally combines Type 1 and Type 2 opcode definitions because the command sets overlap heavily.
- The backward-compatible `gs_type1_init` macro appears mismatched with the newer `gs_type1_interp_init` signature in this source snapshot; active callers use the direct initializer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.h -->