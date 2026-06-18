# Group Research: group_123_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gsistate_c_sources_41cc52eb071a

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsistate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsistate.c

Implements Ghostscript imager-state housekeeping: GC descriptors, initialization, shallow copying, reference-count adjustment, pre-assignment, and release.

Key behavior:
- Defines GC enumeration/relocation for `gx_line_params`, including dash pattern relocation.
- Defines `public_st_imager_state()` traversal for client data, opacity/shape masks, transparency stack, CR state pointers, and effective transfer maps.
- `gs_imager_state_initialize` initializes memory, rendering/color fields, transfer maps, screen phases, pattern state, and default color-map procedures.
- Allocates one identity gray transfer map and shares it through all `effective_transfer` entries.
- `gs_imager_state_copy` performs a shallow struct copy but clears `transparency_stack`, explicitly noting incomplete reference-count handling.
- `gs_imager_state_copied`, `gs_imager_state_pre_assign`, and `gs_imager_state_release` manage reference-counted members such as masks, halftones, CIE rendering, transfer maps, and joint caches.
- Release has special handling for `dev_ht`: if the device halftone refcount is about to drop to zero, dependent halftone structures are released first.

Dependencies:
- Uses Ghostscript GC/reference-count macros from `gsstruct.h` and related imager/color headers.
- Imports `cmap_procs_default`.
- Uses `gs_next_ids` for transfer-map identity allocation.

Research notes:
- This file is central to safe state lifetime management for imaging operations.
- The shallow-copy API is intentionally limited and should not be treated as a fully independent clone without later `gs_imager_state_copied`/assignment handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsistate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjconf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjconf.h

Ghostscript-specific `jconfig.h` configuration wrapper for Independent JPEG Group code.

Key behavior:
- Includes `arch.h`; notes that `stdpre.h` is concatenated externally during IJG build setup rather than directly included here.
- Enables prototype, unsigned char, and unsigned short support where available.
- Enables `HAVE_STDDEF_H` and `HAVE_STDLIB_H` under `__STDC__`.
- Disables BSD strings, sys/types, far pointers, short external names, and incomplete-type workaround flags.
- On very small `int` platforms, caps `MAX_ALLOC_CHUNK` at `0xfff0`.
- Under `JPEG_INTERNALS`, defines `RIGHT_SHIFT_IS_UNSIGNED` based on `ARCH_ARITH_RSHIFT`.

Dependencies:
- Depends on Ghostscript architecture feature macros, especially `ARCH_SIZEOF_INT` and `ARCH_ARITH_RSHIFT`.

Research notes:
- This is build-configuration glue, not runtime code.
- It narrows IJG feature assumptions to match Ghostscript’s portability layer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjmorec.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjmorec.h

Wrapper over IJG `jmorecfg.h` for Ghostscript JPEG feature selection.

Key behavior:
- Includes `jmcorig.h`, then disables optional or unwanted JPEG encoder/decoder features.
- Disables fast integer DCT and disables floating DCT when `FPU_TYPE <= 0`.
- Disables compressor multiscan/progressive support and entropy optimization.
- Keeps decoder multiscan/progressive support because progressive JPEG is required for PDF 1.3.
- Disables smoothing, IDCT scaling, upsample scaling/merging, and quantization passes.
- Sets `D_MAX_BLOCKS_IN_MCU` to `64` for Adobe compatibility.

Dependencies:
- Depends on IJG configuration symbols and Ghostscript `FPU_TYPE`.

Research notes:
- This header trades optional JPEG features for a smaller, controlled build while preserving PDF-required progressive decoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsjmorec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.c

Standalone Ghostscript library test program, despite the nearby initialization header name. It exercises core drawing, device, color, image, halftone, and compositor APIs.

Key behavior:
- Captures real stdio before Ghostscript I/O redirection and initializes platform/library state.
- Allocates interpreter/reference memory, initializes I/O devices, selects a device, wraps it in a bbox device, and creates a `gs_state`.
- Prints device name through the parameter-list API and optionally sets `OutputFile` to `-`.
- Installs a screen halftone using an ordered dither spot function.
- Runs one of several test routines selected by command-line argument, outputs the page, and prints the bounding box.
- Provides GC stubs for relocation and pointer procs because this test harness is not a full interpreter GC environment.
- Provides `gs_to_exit` and `gs_abort` cleanup/exit stubs.

Test routines:
- `test1`: random colored kaleidoscope drawing with transformations and fills.
- `test2`: bitmap pattern fill over a polygon, including colored and uncolored pattern usage.
- `test3`: limited RasterOp exercise against monobit devices.
- `test4`: dynamic device resolution/page parameter update through `gs_putdeviceparams`.
- `test5`: ImageType 1, 3, and 4 image paths, including explicit masks and chroma-key masks.
- `test6`: CIE color rendering, CIEABC color space setup, and color-mapping device modes.
- `test7`: non-monotonic halftone mask construction.
- `test8`: partially transparent indexed pixmap pattern.
- Optional `test10` under `CAPTURE`: replays captured printer output after setting page/device parameters.

Dependencies:
- Pulls in many graphics-library subsystems: state, color spaces, CIE, image parameters, path/paint, RasterOp, devices, bbox device, cmap device, and halftones.

Research notes:
- This file is best understood as a broad integration smoke-test harness for Ghostscript’s C API.
- It is not implementing the `gslib.h` init/fini functions; it calls them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.h

Public library initialization/finalization interface.

Key declarations:
- `int gs_lib_init(FILE *debug_out);`
- `gs_memory_t *gs_lib_init0(FILE *debug_out);`
- `int gs_lib_init1(gs_memory_t *);`
- `void gs_lib_finit(int exit_status, int code, gs_memory_t *);`

Behavior contract:
- `gs_lib_init` performs complete initialization using the C heap.
- Clients needing a custom default allocator can call `gs_lib_init0`, adjust allocator setup, then call `gs_lib_init1`.
- `gs_lib_finit` performs cleanup after execution.

Research notes:
- Requires stdio and Ghostscript memory types.
- This header defines the lifecycle boundary used by the test harness and embedders.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.c

Implements Ghostscript library context initialization and central stdout/stderr routing.

Key behavior:
- Captures real `stdin`, `stdout`, and `stderr` before Ghostscript headers may redefine them.
- Keeps a static `mem_err_print` memory pointer used for stderr context lookup.
- `gs_lib_ctx_get_non_gc_memory_t` returns the non-GC allocator from `mem_err_print`, if available.
- `gs_lib_ctx_init` creates one `gs_lib_ctx_t` per memory root, stores it in `mem->gs_lib_ctx`, initializes stdio fields, callback slots, poll hook, ID counter, and dictionary auto-expand flag.
- `outwrite` routes stdout to redirected file, stderr, callback, or real stdout, then flushes.
- `errwrite` routes stderr to callback or real stderr, then flushes.
- `outflush` and `errflush` flush only when output is not callback-managed.

Dependencies:
- Uses `gslibctx.h` and `gsmemory.h`.
- Uses allocator-provided `gs_alloc_bytes_immovable` during context setup.

Research notes:
- `mem_err_print` is global/static, so stderr routing depends on the most recent initialized memory context.
- This file is API-embedding glue for DLL/shared-object style callers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.h

Declares Ghostscript’s per-library memory context structure and initialization/accessor API.

Key structure:
- `gs_lib_ctx_t` holds:
  - owning `gs_memory_t *memory`
  - real/redirected stdio file pointers
  - stdout redirection flags
  - DLL/shared-library caller handle
  - stdin/stdout/stderr/poll callbacks
  - `gs_next_id` counter
  - `top_of_system`
  - interpreter name table pointer
  - `dict_auto_expand`

Key declarations:
- `int gs_lib_ctx_init(gs_memory_t *mem);`
- `void *gs_lib_ctx_get_interp_instance(gs_memory_t *mem);`
- `const gs_memory_t *gs_lib_ctx_get_non_gc_memory_t(void);`

Research notes:
- The comments acknowledge interpreter-specific fields living here as a hack.
- Context propagation depends on memory objects copying `gs_lib_ctx` into derived allocators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.c

Implements line parameter operators for Ghostscript graphics state.

Key behavior:
- `gs_setlinewidth`/`gs_currentlinewidth` delegate through `gx_line_params`.
- Validates and sets line cap and join values, returning `rangecheck` for unsupported enum values.
- `gx_set_miter_limit` validates limit >= 1 and precomputes `miter_check` using half-angle formulas, with a near-2 special case.
- `gx_set_dash` validates dash arrays, handles empty patterns, rejects negative/zero-total patterns, allocates/resizes dash pattern storage, and computes initial dash index/ink/distance from offset.
- Current dash accessors return length, pattern pointer, and offset.
- Flatness is clamped to `[0.2, 100]`.
- Stroke adjust, dash adaptation, curve join, accurate curves, dot length, and dot orientation extension operators are implemented.
- `gs_setdotorientation` only accepts CTMs with axis-aligned or swapped-axis forms.

Dependencies:
- Uses graphics state internals from `gzstate.h`, line internals from `gzline.h`, matrix helpers, and memory allocation.

Research notes:
- Dash setup is the densest stateful logic in this file.
- Error handling follows Ghostscript conventions via `return_error`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.h

Public declarations for line parameters and quality controls.

Key declarations:
- Standard PostScript line operators: linewidth, linecap, linejoin, miterlimit, dash, flatness, stroke adjust.
- Ghostscript extensions: dash adaptation, curve join, accurate curves, dot length, dot orientation.
- Imager-level accessors for flatness, dash adaptation, and accurate curves.

Dependencies:
- Includes `gslparam.h` for cap/join enum definitions.
- Forward-declares `gs_imager_state`.

Research notes:
- This header separates public graphics-state API from internal `gx_line_params` implementation details.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslparam.h

Defines line cap and line join enum values.

Key definitions:
- `gs_line_cap`: butt, round, square, triangle, unknown.
- `gs_line_cap_max` is `3`, so `gs_cap_unknown` is not settable.
- `gs_line_join`: miter, round, bevel, none, triangle, unknown.
- `gs_line_join_max` is `4`, so `gs_join_unknown` is not settable.

Research notes:
- Some enum values are explicitly marked as not supported by PostScript but still available to Ghostscript extensions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gslparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.c

Implements Ghostscript’s default C heap allocator and wrapper construction.

Key behavior:
- Defines `gs_malloc_memory_procs`, a full `gs_memory_t` procedure table backed by `malloc`, `free`, and `gs_realloc`.
- Each allocation receives a `gs_malloc_block_t` header containing linked-list pointers, size, structure type, and client name.
- Allocated blocks are tracked in a doubly linked list so `free_all` can release remaining allocations.
- `gs_heap_alloc_bytes` enforces allocator limit accounting, attaches headers, fills debug patterns, and updates current/max used bytes.
- Struct and array allocators record the appropriate Ghostscript type descriptor.
- `gs_heap_resize_object` uses `gs_realloc`, preserves list links, updates size/accounting, and fills newly allocated space under debug fill settings.
- `gs_heap_free_object` finalizes typed objects before unlink/free, reports missing blocks, and tolerates null pointers.
- Root registration APIs are no-ops for this non-GC heap allocator.
- `gs_heap_status` estimates available memory by probing with temporary mallocs.
- `gs_heap_enable_free` can swap real free functions for no-op frees.
- `gs_malloc_wrap` builds a locked wrapper, then a retrying wrapper, around the heap allocator.
- `gs_malloc_init` creates the default allocator, initializes or inherits library context, wraps it, and marks stable memory.
- `gs_malloc_release` unwraps and frees all heap allocator data.

Dependencies:
- Uses `gsmemory.h`, `gsmdebug.h`, `gsstruct.h`, `gsmemlok.h`, and `gsmemret.h`.

Research notes:
- This allocator is both a raw allocator and object allocator.
- The wrapper stack is important: normal clients receive retrying-over-locked-over-malloc memory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.h

Client interface for the default C heap allocator.

Key declarations:
- `gs_malloc_memory_t` embeds `gs_memory_common` and tracks allocated list, limit, used bytes, and max used bytes.
- `gs_malloc_memory_init`
- `gs_malloc_memory_release` macro using `gs_memory_free_all(... FREE_ALL_EVERYTHING ...)`
- `gs_malloc_init`
- `gs_malloc_release`
- `gs_malloc` and `gs_free` macros allocate through `mem->non_gc_memory`.
- Wrapper helpers: `gs_malloc_wrap`, `gs_malloc_wrapped_contents`, and `gs_malloc_unwrap`.

Research notes:
- Requires `gsmemory.h`.
- Public API exposes both raw heap memory manager construction and the wrapped allocator used by clients.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.c

Implements matrix creation, arithmetic, coordinate transforms, fixed-point transforms, and compact stream serialization.

Key behavior:
- Provides identity, translation, scaling, and degree-based rotation matrix constructors.
- `gs_matrix_multiply` optimizes for matrices with zero off-diagonal entries.
- `gs_matrix_invert` handles diagonal and general matrices, returning `undefinedresult` for singular matrices.
- Translate/scale/rotate support in-place operation.
- Point and distance transforms have fast paths for diagonal and swapped-axis matrices.
- Bounding-box transforms convert all four corners and recompute min/max to handle rotations and rounding consistency.
- `gs_matrix_fixed_from_matrix` copies a float matrix into fixed-matrix form and caches fixed translation when in range.
- Fixed-point point/distance transform functions use checked fixed multiply/sum helpers and return `limitcheck` on overflow.
- Optional precise currentpoint path uses rounded fixed conversion.
- `sput_matrix` serializes matrices compactly with a control byte and only nonzero/nonredundant float coefficients.
- `sget_matrix` decodes that representation from a stream.

Dependencies:
- Uses `gxmatrix.h`, `gxfixed.h`, `gxfarith.h`, and `stream.h`.
- Uses trig helpers from `gsmisc.c` via `gs_sincos_degrees`.

Research notes:
- The matrix stream representation is private to this file.
- Fixed-point conversion is performance-sensitive and heavily guarded for overflow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.h

Public matrix type and matrix API declarations.

Key definitions:
- `gs_matrix` has six PostScript matrix coefficients: `xx`, `xy`, `yx`, `yy`, `tx`, `ty`.
- `constant_matrix_body` and `identity_matrix_body` support static initialization.
- `is_xxyy` and `is_xyyx` detect diagonal or swapped-axis simple matrices for fast paths.

Key declarations:
- Matrix creation, multiply/invert/translate/scale/rotate.
- Point, distance, and bbox transforms, including inverse variants.
- Stream serialization: `sget_matrix`, `sput_matrix`.

Research notes:
- This header is the public client interface; fixed-matrix details live in internal headers and `gsmatrix.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmatrix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmdebug.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmdebug.h

Allocator debugging definitions.

Key behavior:
- Declares debug fill pattern bytes:
  - allocated-but-uninitialized
  - locally allocated block
  - garbage collected
  - locally deleted block
  - freed
- Defines `gs_alloc_debug` as `gs_debug['@']`.
- Declares `gs_alloc_memset`.
- Defines `gs_alloc_fill`; under `DEBUG`, it fills memory only when allocator debug flag is set, otherwise it is a no-op.

Dependencies:
- Requires `gdebug.h` for `gs_debug`.

Research notes:
- Fill constants are defined in `gsmemory.c`.
- Used by allocators and no-GC string free lists to catch use-after-free/uninitialized memory during debug runs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmdebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.c

Implements a monitor-locked wrapper around another Ghostscript memory allocator.

Key behavior:
- Builds a full `gs_memory_procs_t` table where each operation enters a `gx_monitor_t`, calls the target allocator, then leaves the monitor.
- `gs_memory_locked_init` sets procedure table, target, inherited library context, and allocates the monitor from the target.
- `gs_memory_locked_release` frees wrapper-owned structures, not target allocations.
- `gs_memory_locked_target` exposes the wrapped allocator.
- `gs_locked_free_all` only releases wrapper structures/allocator and cached stable wrapper; it does not free target data.
- `gs_locked_stable` lazily wraps the target’s stable allocator unless the target is already stable.
- All alloc/free/status/root/enable-free procedures delegate under the monitor.

Dependencies:
- Uses `gxsync.h` monitor APIs through `gsmemlok.h`.
- Delegates to the target allocator’s procedure table.

Research notes:
- This wrapper does not track allocations itself.
- It is used by `gsmalloc.c` as the first wrapper around the heap allocator before retrying behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.h

Interface for monitor-locked memory allocator wrapper.

Key structure:
- `gs_memory_locked_t` embeds `gs_memory_common`, target allocator pointer, and monitor pointer.

Key declarations:
- `gs_memory_locked_init`
- `gs_memory_locked_release`
- `gs_memory_locked_target`

Research notes:
- The header states that `free_all` with `FREE_ALL_DATA` is a no-op because the wrapper does not own or track target allocations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.c

Generic allocator support shared by Ghostscript memory implementations.

Key behavior:
- Defines allocator debug fill bytes and structure descriptors for free blocks, byte blocks, GC roots, and const strings.
- Implements bytestring and const-bytestring GC enumerate/relocate procedures, preserving substring offset when backing bytes object moves.
- `gs_alloc_memset` fills arbitrarily large regions in `max_int` chunks.
- `gs_resize_struct_array` allocates or resizes typed struct arrays and checks type in DEBUG builds.
- `gs_raw_alloc_struct_immovable` aliases raw struct allocation to immutable byte allocation sized from the type descriptor.
- Provides no-op free and consolidate functions used when freeing is disabled.
- Provides const-pointer freeing helpers by deconstifying before dispatch.
- Frees `gs_bytestring`/`gs_const_bytestring` through object or string paths depending on representation.
- Exposes type descriptor size/name accessors.
- `gs_register_struct_root` wraps `gs_register_root` with `ptr_struct_type`.
- DEBUG reference-count tracing prints type names and refcount transitions.
- `rc_free_struct_only` frees a reference-counted object through its memory.
- `basic_enum_ptrs` and `basic_reloc_ptrs` implement generic descriptor-driven GC traversal and relocation, including supertype traversal.

Dependencies:
- Uses `gsmemory.h`, `gsmdebug.h`, `gsrefct.h`, and `gsstruct.h`.

Research notes:
- This file is infrastructure for both GC and non-GC allocators.
- The descriptor-driven pointer traversal is the main generic GC support in this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.h

Primary Ghostscript memory allocation API.

Key concepts:
- Distinguishes aligned objects from unaligned strings.
- Supports movable and immovable allocations for GC-aware allocators.
- Defines allocator status, type descriptors, pointer types, GC roots, and the complete `gs_memory_procs_t` interface.
- Raw procedures include immovable byte allocation, resize, free, stable allocator, status, free_all, and consolidate_free.
- Object-level procedures include movable bytes, structs, byte arrays, struct arrays, object size/type, strings, string resize/free, root registration, root unregistration, and enable_free.
- Defines convenience macros such as `gs_alloc_bytes`, `gs_alloc_struct`, `gs_alloc_string`, `gs_free_object`, `gs_memory_status`, and `gs_consolidate_free`.
- Defines `FREE_ALL_DATA`, `FREE_ALL_STRUCTURES`, `FREE_ALL_ALLOCATOR`, and `FREE_ALL_EVERYTHING`.
- Declares const-free helpers, bytestring free helpers, struct-array resize helper, root helper, no-op free/consolidate procedures, and raw immutable struct allocation.
- Defines `gs_memory_common`, including stable allocator, procedure table, library context, optional PCL/PXL memory head, and non-GC parent allocator.
- Defines concrete `struct gs_memory_s`.

Research notes:
- This is a foundational API; most allocator implementations in this group are concrete wrappers around this contract.
- Comments explicitly warn that allocator alignment is not guaranteed beyond hardware requirements.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemraw.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemraw.h

Historical raw-memory allocator interface, currently disabled with `#if 0`.

Key contents:
- Explains that `gsmemraw` used to be an abstract base class.
- States it is no longer in use; `gs_memory_t` is now the concrete base class because the full allocator interface must be available throughout the system.
- The disabled block contains older raw allocator status/types/procedure macros and comments about alignment requirements.
- Ends with only include guards active.

Research notes:
- No active API is exported beyond the include guard.
- Useful for understanding allocator design history and why raw allocation was folded into `gs_memory_t`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemraw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.c

Implements a retrying allocator wrapper around another allocator.

Key behavior:
- Builds `retrying_procs`, a full `gs_memory_procs_t` table.
- Allocation-like operations call the target allocator; if the result is null, they invoke a recovery closure and retry while it returns `RECOVER_STATUS_RETRY_OK`.
- Default recovery closure is `no_recover_proc`, which never retries.
- Free, status, object-size/type, unregister-root, enable-free, and consolidate-free directly forward to the target without retry loops.
- `gs_memory_retrying_init` sets procs, target, inherited library context, `non_gc_memory`, and default recovery closure.
- `gs_memory_retrying_set_recover` installs custom recovery callback/data.
- `gs_memory_retrying_release` releases wrapper structures only.
- `gs_retrying_stable` lazily wraps target stable allocator unless target stable allocator is the same target.

Dependencies:
- Implements interface declared in `gsmemret.h`.
- Assumes target allocator supplies complete `gs_memory_t` procs.

Research notes:
- This wrapper is designed to give clients a hook to free memory or trigger collection after failed allocation.
- It does not own allocations and does not free target data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.h

Interface for retrying memory allocator wrapper.

Key definitions:
- `gs_memory_retrying_t` embeds `gs_memory_common`, target allocator, recovery proc, and recovery proc data.
- `gs_memory_recover_status_t`: `RECOVER_STATUS_NO_RETRY` or `RECOVER_STATUS_RETRY_OK`.
- `gs_memory_recover_proc_t` callback signature.

Key declarations:
- `gs_memory_retrying_init`
- `gs_memory_retrying_release`
- `gs_memory_retrying_set_recover`
- `gs_memory_retrying_target`

Research notes:
- Comments clarify that this wrapper does not track acquired memory, so `free_all` with `FREE_ALL_DATA` is a no-op at wrapper level.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmisc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmisc.c

Miscellaneous Ghostscript utilities: redirected output, debug support, libc fallbacks, arithmetic helpers, fixed-point conversions, and trig helpers.

Key behavior:
- Captures original `sqrt` before Ghostscript math macro wrapping.
- `outprintf` and `errprintf` route formatted output through `outwrite`/`errwrite`; both use a fixed 1024-byte buffer and emit a panic message if exceeded.
- Defines global `gs_debug[128]` and `gs_debug_out`.
- `gs_debug_c` supports uppercase debug flags implying lowercase.
- Debug print helpers include file/line prefixes, program identifiers, error logging, byte/bitmap dumps, and string/hex string printing.
- `gs_return_check_interrupt` maps platform interrupt checks into Ghostscript error returns.
- Provides fallback `memmove`, `memcpy`, `memchr`, `memset`, and `realloc` implementations under portability macros.
- Arithmetic helpers include positive modulo, gcd, modular division, integer log2, fixed multiply/divide quotient, and optional IEEE fixed/floating conversion helpers.
- `gs_sqrt` can trace sqrt calls under debug flag `~`.
- `gs_sin_degrees`, `gs_cos_degrees`, and `gs_sincos_degrees` optimize exact quadrant angles and have no-FPU table-based alternatives.
- `gs_atan2_degrees` returns PostScript-style degree angles and reports `undefinedresult` for `(0,0)`.

Dependencies:
- Uses Ghostscript portability headers for math, memory, fixed-point arithmetic, platform interrupt checks, and errors.
- Output functions depend on `gslibctx.c` routing.

Research notes:
- This file is a portability and diagnostics hub.
- The formatted output functions use `vsprintf`, so callers rely on the fixed buffer guard happening after formatting, not before.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.c

Implements non-tracing reclamation and string freelists for non-GC Ghostscript environments.

Key behavior:
- Provides unaligned 32-bit get/put helpers matching `SFREE_NB`.
- `sf_alloc_string` scans current chunk string freelist for exact-size reusable blocks for requests >= 40 bytes and below large-object threshold; otherwise delegates to reference memory allocator.
- `sf_free_string` returns strings to chunk storage:
  - immediately moves `ctop` for top-of-string-area frees
  - inserts larger strings into address-ordered freelists
  - inserts tiny strings into per-256-byte one-byte freelists
  - updates lost string accounting and debug-fill patterns
- DEBUG overlap checks detect suspicious freelist insertions.
- `sf_enable_free` delegates enable-free and reinstalls string free hook when enabled.
- `sf_merge_strings` coalesces free strings at the bottom/top boundary of chunk string storage.
- `sf_consolidate_free` closes chunks, merges string space, recovers unused string-marking space, reinitializes freelists, reopens chunks, and consolidates object free space.
- `gs_nogc_reclaim` walks VM spaces, installs string freelist behavior on each distinct reference memory and stable memory allocator, then consolidates.
- `use_string_freelists` rewires allocator string and consolidate procs to no-GC versions.

Dependencies:
- Uses `gxalloc.h` reference-memory internals: chunks, chunk locators, lost accounting, and consolidation helpers.
- Declared through `gsnogc.h` as a VM reclaim procedure.

Research notes:
- This is not a tracing collector; it only coalesces free memory and installs freelist reuse.
- It assumes environments without save/restore and without real garbage collection needs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.h

Interface for the non-tracing GC/reclaim procedure.

Key declaration:
- `extern vm_reclaim_proc(gs_nogc_reclaim);`

Dependencies:
- Includes `gsgc.h` for `vm_reclaim_proc`.

Research notes:
- This header exposes `gs_nogc_reclaim` to VM/allocator code that expects a reclaim callback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnorop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnorop.c

Stubs for builds without implemented RasterOp support.

Key behavior:
- `gs_current_logical_op` always returns `lop_default`.
- `gs_set_logical_op` accepts only `lop_default`; all other values return `rangecheck`.
- Memory-device RasterOp entry points return `rangecheck`.
- Default device `copy_rop` and `strip_copy_rop` implementations return `unknownerror`.
- `gx_alloc_rop_texture_device` returns `rangecheck`.
- `gx_make_rop_texture_device` is an empty never-called stub.

Dependencies:
- Provides symbols expected by RasterOp-capable interfaces while intentionally disabling behavior.

Research notes:
- This file is a compatibility stub layer, useful for configurations that compile RasterOp APIs but do not support the feature.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnorop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.c

Implements simple notification registration lists.

Key behavior:
- Defines GC descriptors for registrations and notification lists.
- `gs_notify_init` initializes list head and memory allocator.
- `gs_notify_register` allocates a registration node, stores callback/data, and pushes it at the list head.
- `gs_notify_unregister_calling` removes matching registrations by callback and optional data, calls a user-supplied unregister hook per removal, frees nodes, and returns whether anything was found.
- `gs_notify_unregister` is the same without a hook.
- `gs_notify_all` calls all registered callbacks, preserves the first negative error code, and continues notifying remaining callbacks.
- `gs_notify_release` frees all remaining registration nodes.

Dependencies:
- Uses allocator from `gs_notify_list_t`.
- Uses structures declared in `gsnotify.h`.

Research notes:
- Duplicate registrations are allowed.
- Notification iteration stores `next` before invoking callbacks, so callbacks can unregister current entries safely in common cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.h

Public notification-list interface.

Key definitions:
- `gs_notify_proc_t`: callback receiving `proc_data` and `event_data`.
- `gs_notify_registration_t`: callback, callback data, next pointer.
- `gs_notify_list_t`: allocator pointer and first registration.
- GC descriptor macros for registration and list structures.

Key declarations:
- `gs_notify_init`
- `gs_notify_register`
- `gs_notify_unregister`
- `gs_notify_unregister_calling`
- `gs_notify_all`
- `gs_notify_release`

Research notes:
- Comments specify that clients must unregister when finalized, and notifying object finalization uses `event_data = NULL`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.c

Implements Ghostscript overprint/overprint-mode compositor support and forwarding device behavior.

Key behavior:
- Defines GC descriptor for `gs_overprint_t`.
- Implements variable-length little-endian base-128 encoding/decoding for `gx_color_index`, supporting potentially 64-bit color indices.
- `c_overprint_equal` compares compositor type and overprint parameters.
- `c_overprint_write` serializes overprint flags and, when needed, drawn component bits.
- `c_overprint_read` decodes serialized overprint parameters and constructs a compositor.
- Defines `gs_composite_overprint_type` with create/equal/write/read/clist update procs.
- `gs_create_overprint` allocates a reference-counted compositor, assigns ID, type, and params.
- `gs_is_overprint_compositor` checks compositor type.
- Defines `overprint_device_t`, a forwarding device with `drawn_comps` and `retain_mask`.
- Provides three proc tables:
  - no-overprint forwarding procs
  - generic overprint procs for non-separable/non-linear color encodings
  - separable overprint procs for separable linear encodings
- `swap_color_index` handles byte order for multi-byte color indices on little-endian hosts.
- `set_retain_mask` builds a per-bit retain mask from non-drawn components and device component masks.
- `check_drawn_comps` builds a component mask from nonzero mapped component values.
- `update_overprint_params` switches proc tables based on overprint parameters and target color model, computes process/spot drawn components, handles degenerate all-components-drawn case, and updates retain masks.
- `overprint_open_device` opens target and copies parameters.
- `overprint_put_params` forwards target parameter updates, decaches colors, and closes itself if target closes.
- `overprint_get_page_device` forwards page-device lookup to target.
- `overprint_create_compositor` updates existing overprint device params when given an overprint compositor; otherwise delegates to default compositor creation.
- `overprint_generic_fill_rectangle` delegates to `gx_overprint_generic_fill_rectangle`.
- `overprint_sep_fill_rectangle` swaps color index as needed and chooses optimized masked fill path based on depth.
- `fill_in_procs` completes proc tables once using a temporary forward device.
- `c_overprint_create_default_compositor` suppresses no-op overprint, initializes proc tables lazily, allocates an overprint forwarding device, copies target params, sets target, and applies overprint params.

Dependencies:
- Uses device/compositor infrastructure: `gxcomp.h`, `gxdevice.h`, `gsdevice.h`, `gxoprect.h`, `gxdcolor.h`, and `gxistate.h`.
- Uses `gs_next_ids` for compositor identity.
- Relies on lower-level overprint rectangle helpers from `gxoprect`.

Research notes:
- The comments describe some fill routines as stubs historically, but current functions delegate to `gx_overprint_*` helpers.
- The compositor is suppressed for no-op overprint and for degenerate cases where all components are drawn, avoiding unnecessary forwarding devices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsovrc.c -->