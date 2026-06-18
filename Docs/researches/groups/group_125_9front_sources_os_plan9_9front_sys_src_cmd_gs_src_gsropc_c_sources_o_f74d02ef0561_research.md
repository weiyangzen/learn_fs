# Group Research: group_125_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gsropc_c_sources_o_f74d02ef0561

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.c

Implements the Ghostscript RasterOp compositor object and a forwarding compositor device used to apply logical RasterOp operations during rendering.

Key behavior:
- Defines the `gs_composite_rop_type` compositor vtable and allocates `gs_composite_rop_t` objects in `gs_create_composite_rop`.
- Compares RasterOp compositors by operation code and optional texture device color.
- Creates a `gx_device_composite_rop` wrapper device around a target device in `c_rop_create_default_compositor`.
- Overrides fill/copy procs for the wrapper; most image/copy paths temporarily fall back to default implementations.
- `dcr_fill_rectangle` maps flat fills to `strip_copy_rop`, selecting memory-device helpers for selected depths and handling pure or binary-halftone textures.

Dependencies:
- Uses compositor, device, device-color, memory-device, and RasterOp support from `gxcomp`, `gxdevice`, `gxdcolor`, `gxdevmem`, and `gxropc`.
- Uses `gs_next_ids` for compositor identity.

Research notes:
- Serialization hooks `c_rop_write` and `c_rop_read` are explicitly `NYI` and contain no return path in this source.
- Several rendering paths are also marked incomplete: memory device selection, 16/32-bit implementations, colored halftones, patterns, and identity-operation bypass.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.h

Declares the public RasterOp-compositing interface.

Key definitions:
- `gs_composite_rop_params_t` holds a packed logical operation and optional `gx_device_color` texture.
- The comments define two operating modes: no texture means input data are treated as texture with implicit black source; non-null texture means input data are source and the caller promises the texture is stable.
- `gs_create_composite_rop` constructs a compositor object from those parameters.

Dependencies:
- Includes `gscompt.h` for compositor types and `gsropt.h` for logical RasterOp definitions.
- Forward-declares `gx_device_color` when needed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropt.h

Defines RasterOp, transparency, and logical-operation bit encodings shared by PCL/PostScript extensions.

Key definitions:
- `gs_rop2_t` and `gs_rop3_t` encode 2-input and 3-input Boolean RasterOps, with source, destination, and texture bit positions chosen so Boolean algebra on opcodes mirrors Boolean algebra on pixels.
- Macros transform ROP3 operations by inverting operands, pinning operands to 0 or 1, swapping source/texture, applying source or texture transparency, negating results, and testing operand use.
- `gs_logical_operation_t` packs low-byte ROP3, source/pattern transparency flags, render algorithm bits, and `lop_pdf14`.
- `lop_uses_S`, `lop_uses_T`, `lop_no_T_is_S`, `lop_no_S_is_T`, and `lop_is_idempotent` support renderer optimizations and transparency behavior.
- Declares `rop_proc_table[256]` and `rop_usage_table[256]`.

Research notes:
- `TRANSPARENCY_PER_H_P` intentionally preserves HP manual semantics, including the unusual definition where transparency flags can force source use.
- `lop_pdf14` forces logical operations to be treated as non-idempotent even though it does not directly change rendering bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsroptab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsroptab.c

Provides the concrete table of 256 RasterOp procedures plus the operand-usage table.

Key behavior:
- Defines one `ropN(D,S,T)` function for each 8-bit ROP3 opcode, using expressions derived from HP/Microsoft reverse Polish notation names.
- Exports `rop_proc_table[256]`, mapping opcode values directly to implementation functions.
- Exports `rop_usage_table[256]`, whose entries encode whether each operation uses D, S, T, or combinations of them.
- Includes the small generator program, in a comment, that produced the usage table from `rop3_uses_D/S/T`.

Dependencies:
- Includes only `stdpre.h` and `gsropt.h`; this is a pure Boolean helper table.

Research notes:
- This file is data-heavy but mechanically straightforward: correctness depends on the per-op expressions and direct opcode-to-index table alignment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsroptab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.c

Implements utility routines for compact variable-length integer serialization.

Key behavior:
- `enc_u_size_uint` and `enc_s_size_int` compute encoded sizes for unsigned and signed integers.
- `enc_u_put_uint` and `enc_s_put_int` write little-endian base-128 encodings with a continuation bit.
- `enc_u_get_uint`, `enc_u_get_uint_nc`, `enc_s_get_int`, and `enc_s_get_int_nc` decode const and non-const byte-pointer streams.
- Signed encoding stores sign in the next-to-high bit of the first byte and handles `enc_s_min_int` specially.
- A `UNIT_TEST` block round-trips unsigned and signed values around powers of two and checks encoded lengths.

Dependencies:
- Uses `gstypes.h` and constants/macros from `gsserial.h`.

Research notes:
- This is a low-level format helper originally split out from command-list code.
- The non-const wrappers delegate to the const decoders and advance by pointer difference.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.h

Declares and macro-expands compact unsigned and signed integer encoders used by serialization code.

Key definitions:
- Unsigned values use base-128 little-endian bytes with bit 7 as the continuation flag.
- `enc_u_sizew`, `enc_u_size2w`, and point helpers provide fast size calculations.
- `enc_u_putw`, `enc_u_put2w`, `enc_u_getw`, and related macros inline one- and two-byte fast paths.
- Signed values use bit 6 of the first byte as the sign bit and bit 7 as continuation.
- `enc_s_putw`, `enc_s_getw`, and point helpers encode/decode signed integers with special handling for minimum int.

Dependencies:
- Requires Ghostscript base types and byte/point-compatible structures from included context.

Research notes:
- The header is intentionally macro-heavy for fast command-list style encoding.
- Comments contain minor typos, but the code path is clear and paired with the `UNIT_TEST` in `gsserial.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsserial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.c

Implements constructors, validation, GC descriptors, and common rendering setup for PDF/PostScript shading objects.

Key behavior:
- Defines GC descriptors for generic shadings and mesh shadings, including data sources, functions, and decode arrays.
- Initializes common shading parameters and mesh-specific defaults.
- Validates color spaces, BBoxes, function input/output arity, mesh bit depths, and BitsPerFlag values.
- Provides parameter init and object allocation for Function-based, Axial, Radial, Free-form Gouraud triangle, Lattice Gouraud triangle, Coons patch, and Tensor product patch shadings.
- Rendering entry `gs_shading_fill_path_adjusted` delegates to `gs_shading_fill_path`, which builds clipping from the current device box, optional rectangle, optional shading BBox, and optional input path.
- Uses a temporary clip device when the target device requests shading-area clipping through `pattern_manage`.
- Fills the shading background when requested, remapping the background color through the shading color space.
- Calls the shading-type `fill_rectangle` procedure after converting the clipped device box back to user-space bounds.

Dependencies:
- Uses color spaces, functions, data sources, clip paths, path construction, device color remapping, and shading renderers from `gxshade*`.

Research notes:
- Function domain superset checking is intentionally not enforced to match Adobe behavior.
- Background fill has an in-source warning that it is wrong for non-idempotent RasterOps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.h

Defines public shading parameter structures, type tags, GC descriptor macros, constructors, and the rendering entry point.

Key definitions:
- `gs_shading_type_t` enumerates shading types 1 through 7.
- `gs_shading_params_common` contains color space, optional background, optional BBox, and AntiAlias.
- `gs_shading_procs_t` currently contains the type-specific `fill_rectangle` procedure.
- Type-specific parameter structs cover Function-based, Axial, Radial, and four mesh shading families.
- Mesh common parameters include data source, coordinate/component bit depths, Decode, and optional Function.
- Descriptor macros define how each shading type participates in Ghostscript GC traversal.

Public API:
- Parameter initializers for each shading type.
- `gs_shading_*_init` constructors.
- `gs_shading_fill_path_adjusted`, the external path/rectangle shading renderer.

Research notes:
- The header keeps implementation layout partially visible because GC descriptors and clients need concrete parameter structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsshade.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.c

Implements Ghostscript graphics-state allocation, lifetime management, save/restore, copy/current/setgstate, overprint updates, and miscellaneous state operators.

Key behavior:
- The large opening comment classifies all state-owned storage: embedded state, GC-owned references, ref-counted shared members, stack-associated objects, per-state heap objects, and client data.
- Defines `gs_state` GC enumeration/relocation, including special handling for devices and device-filter stacks.
- `gs_state_alloc` allocates an initial state, initializes imager state, paths, clip paths, view clip, color space/color, null device, alpha/transfer/line defaults, font placeholders, and a bottom save.
- `gs_gsave`, `gs_grestore_only`, `gs_grestore`, `gs_gsave_for_save`, `gs_grestoreall_for_restore`, and `gs_grestoreall` implement graphics-state stack manipulation and save-level view-clip behavior.
- `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, and `gs_setgstate` clone or copy states with distinct semantics for saved pointers, view clips, client data, and show-state pointers.
- `gstate_alloc_parts`, `gstate_clone`, `gstate_free_contents`, and `gstate_copy` handle per-state path/clip/color/device-color allocations, shared path segments, dash patterns, refcounts, and color-space counts.
- Overprint APIs update overprint flags/mode and install or refresh an overprint compositor through device `create_compositor`.
- `gs_initgraphics` resets matrix, path, clipping, line parameters, dash state, dot settings, miter limit, and RasterOp defaults without resetting current color/color space.
- Includes fill adjust, coordinate clamp, and text rendering mode accessors.

Dependencies:
- Ties together imager state, devices, paths, clip paths, color spaces, pattern caches, halftones, line state, overprint compositor, and client callbacks.

Research notes:
- This file is the central ownership boundary for graphics-state mutation.
- State copy operations are deliberately subtle: `gsave` switches old/new private parts, while off-stack clones keep their own parts.
- Overprint compositor refresh is required after state restoration and `setgstate` when overprint state may change.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.h

Declares the public graphics-state API.

Key declarations:
- Opaque `gs_state` and overprint parameter forward declaration.
- Allocation/free and save/restore/copy APIs: `gs_state_alloc`, `gs_state_free`, `gs_gsave`, `gs_grestore`, `gs_grestoreall`, `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, and `gs_setgstate`.
- Save/restore helpers used by interpreter `save`/`restore`.
- Overprint controls and `gs_do_set_overprint`.
- `gs_initgraphics`.
- Includes public device, line, color, halftone, and color-selection headers.
- Screen/halftone phase APIs and miscellaneous fill-adjust, limit-clamp, text-rendering-mode, and cache-device accessors.

Research notes:
- This header is a broad facade: including it also brings in major public graphics-state sub-APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstruct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstruct.h

Defines the macro framework Ghostscript modules use to describe GC-visible structures.

Key behavior:
- Documents naming conventions for structure types, typedefs, public/private descriptors, embedded structures, and array element descriptors.
- Defines pointer processing procedure tables for unmark/mark/relocate operations and standard pointer types for structs and strings.
- Defines GC roots and `public_st_gc_root_t`.
- Defines GC relocation procedure accessors used by structure-specific relocation routines.
- Provides stock no-pointer and basic table-driven enumeration/relocation declarations.
- Defines `BASIC_PTRS`, `GC_OBJ_ELT`, string element descriptors, and descriptor builders for simple, basic, composite, complex, finalizable, element-array, pointer-only, suffix-subclass, and general-subclass structures.
- Provides enumeration/relocation helper macros such as `ENUM_PTR`, `ENUM_STRING`, `RELOC_PTR`, `RELOC_STRING_VAR`, `ENUM_USING`, and `RELOC_USING`.
- Includes convenience descriptor macros for structures with fixed numbers of object/string pointers.

Dependencies:
- Includes `gsstype.h` for the underlying descriptor types and proc signatures.

Research notes:
- This is infrastructure rather than runtime policy, but many files in this group instantiate descriptors through these macros.
- The suffix/general subclass macros encode superclass offsets and additional pointer tables, so descriptor correctness depends on accurate member order and offsets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstruct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstype.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstype.h

Defines the core structure descriptor types used by Ghostscript's allocator and garbage collector.

Key definitions:
- Opaque `gc_state_t`.
- `enum_ptr_t`, the return carrier for enumerated object or string pointers.
- Proc signatures for clear-marks, enumerate-pointers, relocate-pointers, and finalize callbacks.
- `gs_memory_struct_type_s`, containing object size, structure name, optional shared procs, per-type callbacks, and callback data.
- `extern_st(st)` macro for structure descriptor declarations.

Research notes:
- Comments constrain finalizers: they must not allocate or resize allocator-managed objects and cannot assume referenced managed objects still exist.
- `EV_CONST` preserves historical enum callback constness while minimizing compiler warnings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.c

Implements the generic text-processing interface between graphics state, devices, fonts, and clients.

Key behavior:
- Defines GC descriptors for `gs_text_params_t` and `gs_text_enum_t`, including string/array inputs, replacement-width arrays, devices, paths, colors, clip paths, fonts, font stacks, and cached font-matrix pairs.
- `gx_device_text_begin` validates text params, selects path/clip arguments based on operation flags, and dispatches to the device `text_begin` proc.
- `gs_text_enum_init` initializes common enumerator fields, dynamic font-stack state, current font, indexes, scale, and device refcount.
- `gs_text_enum_copy_dynamic` copies mutable enumeration state for delegated/subsidiary text processing.
- `gs_text_begin` derives the effective clip path when drawing, loads the current device color even for width-only operations, and calls the device text entry point.
- Provides begin helpers for PostScript-style operators: `show`, `ashow`, `widthshow`, `awidthshow`, `kshow`, `xyshow`, `glyphshow`, `cshow`, `stringwidth`, `charpath`, `charboxpath`, `glyphpath`, and `glyphwidth`.
- `gs_text_restart`, `gs_text_resync`, and `gs_text_process` delegate to enumerator procs.
- Accessors expose current font, current/next char, current glyph, total width, replaced widths, current width, width-only status, and cache-device setup.
- Release functions decrement device/enumerator references and call implementation-specific release hooks.
- Default font routines initialize an empty font stack, map the next input item to a char/glyph, and provide a failing `gs_no_build_char`.

Dependencies:
- Uses device text procs, font/cache structures, paths, clip paths, device colors, graphics state, and Ghostscript GC/refcount machinery.

Research notes:
- Color is loaded unconditionally because high-level devices may accumulate Type 3 charstrings even for `stringwidth`.
- `setup_FontBBox_as_Metrics2` handles CID glyph-direct cases where normal char-to-glyph setup is bypassed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.h

Declares the public/device text interface and text operation encoding.

Key definitions:
- Operation flags describe the input source, width modification mode, requested output action, client intervention, and width return.
- Validation macros reject missing or multiple input/output modes, invalid single-item sizes, and simultaneous add/replace width modes.
- `gs_text_params_t` carries input bytes/chars/glyphs/single char/single glyph, optional deltas, space char/glyph, replacement width arrays, and width count.
- `dev_proc_text_begin` defines the device-side text begin procedure.
- Return codes from `gs_text_process` request rendering, client intervention, or CDevProc execution.
- `gs_text_cache_control_t` selects char width, cache device, or cache device 2 metrics.

Public API:
- Generic text begin/update/restart/resync/process/release functions.
- PostScript-equivalent begin helpers.
- Current font/char/glyph/width accessors and cache setup helpers.

Research notes:
- The interface is explicitly state-machine based: clients call begin, repeatedly process until completion/error, and respond to positive return codes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstparam.h

Defines transparency parameter types shared by graphics state and PDF 1.4 compositor code.

Key definitions:
- `gs_blend_mode_t` enumerates supported blend modes from Compatible/Normal through Color, with `GS_BLEND_MODE_NAMES`.
- `gs_transparency_state_t` is the common stack-node header for transparency groups and masks.
- `gs_transparency_mask_t` is a refcounted cached mask header.
- `gs_transparency_group_params_t` carries optional blending color space plus Isolated and Knockout flags.
- `gs_transparency_mask_params_t` carries mask subtype, background components, gray background, transfer callback, and transfer function data.
- `gx_transparency_mask_params_t` is the post-command-list mask parameter form with sampled 256-byte transfer function.
- `gs_transparency_channel_selector_t` selects opacity or shape channel.

Research notes:
- Comments require `gs_trans_group_params_init` and `gs_trans_mask_params_init` to stay in sync with the parameter structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.c

Implements transparency graphics-state accessors and non-rendering PDF 1.4 transparency compositor dispatch.

Key behavior:
- Sets/gets blend mode, opacity alpha, shape alpha, and text knockout, clamping alpha to `[0,1]` and validating blend modes.
- Exposes current transparency stack type.
- Defines a dummy transparency-stack descriptor and pop helper; actual push helper is disabled by `PUSH_TS 0`.
- `gs_state_update_pdf14trans` sends `gs_pdf14trans_params_t` operations to `send_pdf14trans` and installs a new compositor device if one is returned.
- Initializes and begins/ends transparency groups by filling PDF14 compositor params with isolation, knockout, alpha, shape, blend mode, and bbox.
- Imager-level `gx_begin/end_transparency_group` call device transparency procs when present.
- Initializes mask params with identity transfer by default.
- Begins transparency masks by copying background data, sampling the transfer function into 256 byte values, and forwarding PDF14 params.
- Imager-level mask begin/end/init functions call device procs or clear opacity/shape masks.
- Provides PDF14 push/pop device operations.

Dependencies:
- Uses graphics state internals, device compositor support, PDF 1.4 device interface (`gdevp14.h`), and transparency parameter definitions.

Research notes:
- Group color space is logged but not used; blending color space is currently based on the process color model of the output device.
- `gs_discard_transparency_layer` is marked dummy/NYI and operates on the disabled local stack mechanism.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.h

Declares PDF 1.4 transparency compositor operations, parameter structures, graphics-state accessors, and imager-level device hooks.

Key definitions:
- `pdf14_compositor_operations` covers push/pop device, begin/end group, init/begin/end mask, and set blend params.
- Serialization change bits identify blend mode, text knockout, shape alpha, and opacity alpha changes.
- `gs_transparency_source_t` pairs constant alpha with an optional transparency mask.
- `gs_pdf14trans_params_t` carries all operation-specific PDF14 compositor data.
- `gs_pdf14trans_t` embeds `gs_composite_common` plus PDF14 params.
- Estimated buffer-space macros approximate PDF14 transparency row memory using three buffers, one alpha channel, four color channels, and 8 bits per channel.

Public API:
- Blend/alpha/text-knockout accessors.
- PDF14 device push/pop.
- Transparency group and mask begin/end/init/discard calls.
- Imager-level group/mask calls and compositor identification.

Research notes:
- The row-space estimate is explicitly a hack and may underpredict real transparency buffer needs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.c

Implements ingestion and validation of trapping parameters from a Ghostscript parameter list.

Key behavior:
- `trap_put_float_param` reads a float parameter, applies a supplied validation predicate, signals parameter errors, and accumulates the current error code.
- `gs_settrapparams` copies the current trap parameter struct, reads known keys, validates unit-range and positive fields, reads booleans and integer fields, maps `ImageTrapPlacement` through enum names, and commits only if no error occurred.
- Validates `ImageResolution > 0`.

Dependencies:
- Uses `gs_param_list` helpers from `gsparamx.h` and trapping definitions from `gstrap.h`.

Research notes:
- The update is transactional at the struct level: the original parameters are replaced only after all reads and checks succeed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.h

Defines trapping parameter and zone structures.

Key definitions:
- `gs_trap_placement_t` enumerates Center, Choke, Spread, and Normal placement with matching name macro.
- `gs_trap_params_t` contains black/color limits, widths, enabled flags, image trapping flags, image resolution, image trap placement, sliding/step/color-scaling limits, and trap width.
- `gs_trap_zone_t` pairs trapping params with a path pointer and is marked subject to change.

Public API:
- `gs_settrapparams` reads/validates parameters from a `gs_param_list`.

Research notes:
- Several possible parameters are commented out, including colorant zone details and halftone name.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.c

Implements the Adobe Type 1 charstring interpreter.

Key behavior:
- `gs_type1_interpret` continues or starts interpretation for a `gs_type1_state`, optional glyph data, and othersubr callback index.
- Initializes the Type 1 hinter, maps font/CTM/subpixel data, and passes Type 1 font data into hinting before interpretation.
- Maintains operand and instruction stacks, decryption state, call depth, and current fixed-point origin.
- Decodes Type 1 charstring numbers in one-, two-, and four-byte forms, including a special large-number division workaround.
- Handles subroutine calls/returns through font `subr_data` callbacks and frees returned glyph data.
- Dispatches Type 1/Type 2-shared drawing commands to the hinter: stems, moves, lines, curves, closepath, endchar, and current point update.
- Implements `hsbw` and `sbw`, returning `type1_result_sbw` to allow client intervention after sidebearing/width setup.
- Handles `seac`, including accent recursion and sidebearing adjustment for a documented Fontographer workaround.
- Handles Type 1 escaped commands including dotsection, stem3, div, callothersubr, pop, and setcurrentpoint.
- Implements known Flex and Multiple Master blend othersubrs internally; unknown othersubrs are passed to client callbacks with copied operand values and return `type1_result_callothersubr`.

Dependencies:
- Uses Type 1 font data, glyph data, path/imager state, fixed arithmetic, font matrix mapping, Type 1 hinting (`gxhintn.h`), and callback procedures from the font data.

Research notes:
- The interpreter is resumable: it stores instruction pointer, decryption state, operand stack count, and call stack count when returning for client intervention.
- Many invalid or unsupported opcodes return `invalidfont`, matching PostScript font error semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.h

Declares the Type 1/Type 2 charstring interpreter interface and opcode definitions.

Key definitions:
- `crypt_charstring_seed` for Type 1 charstring decryption.
- Opaque `gs_type1_state` and Type 1 font/path forward declarations.
- Initialization and state customization APIs: `gs_type1_interp_init`, callback data setter, left sidebearing setter, and width setter.
- Return codes `type1_result_sbw` and `type1_result_callothersubr`.
- Generic `charstring_interpret_proc_t`, with declarations for `gs_type1_interpret` and `gs_type2_interpret`.
- Shared Type 1/Type 2 number encoding opcodes and helpers for small, positive two-byte, and negative two-byte values.
- `char_command` enum for shared, Type 1-only, and Type 2-only charstring commands.
- Debug name tables for Type 1 and Type 2 commands.
- `char1_extended_command` and `char2_extended_command` enums plus debug-name tables for escaped commands.

Research notes:
- The header intentionally co-locates Type 1 and Type 2 opcode definitions because the encodings overlap heavily.
- The backward-compatibility `gs_type1_init` macro adapts older text enumerator usage to the newer interpreter init function.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype1.h -->