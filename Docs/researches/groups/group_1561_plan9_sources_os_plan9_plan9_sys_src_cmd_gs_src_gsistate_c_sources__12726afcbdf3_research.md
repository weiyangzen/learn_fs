# Group Research: group_1561_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gsistate_c_sources__12726afcbdf3

Scope confirmed in `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsistate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsistate.c

Implements Ghostscript imager-state housekeeping. It defines GC pointer enumeration and relocation for `gx_line_params` dash patterns and `gs_imager_state`, including client data, opacity/shape masks, transparency stack, color rendering pointers, and effective transfer maps.

`gs_imager_state_initialize` seeds a new imager state with memory ownership, null color rendering and transparency references, default screen phases, a newly allocated identity gray transfer map, default color-map procedures, and pattern-cache defaults. `gs_imager_state_copy` performs a shallow temporary copy and clears the transparency stack in the copy.

Reference-count lifecycle is explicit: `gs_imager_state_copied` increments referenced masks, halftones, transfer maps, CIE state, and caches; `gs_imager_state_pre_assign` uses `rc_pre_assign` before assignment; `gs_imager_state_release` decrements the same references and specially releases dependent device-halftone structures when the last reference is about to go away.

Key dependencies: `gxistate.h`, `gzline.h`, transfer maps, CIE rendering structures, device halftone release, and Ghostscript reference-count macros. This file is central to safe copying and teardown of graphics/imager state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsistate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjconf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjconf.h

Ghostscript’s `jconfig.h` configuration wrapper for Independent JPEG Group code. It is intended to be combined with `stdpre.h` externally because of the IJG build directory layout, then includes `arch.h` for platform characteristics.

Defines IJG feature/configuration macros such as `HAVE_PROTOTYPES`, unsigned char/short support, optional standard headers under `__STDC__`, and disables BSD strings, sys/types, far pointers, short external names, and broken incomplete types.

Also adjusts `MAX_ALLOC_CHUNK` on small-int architectures and, for JPEG internals, sets `RIGHT_SHIFT_IS_UNSIGNED` based on `ARCH_ARITH_RSHIFT`. The file is a build-portability bridge rather than runtime logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjmorec.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjmorec.h

Wrapper around IJG `jmorecfg.h` via `jmcorig.h`, pruning JPEG encoder/decoder features not needed by this Ghostscript build. It disables fast integer DCT, optional floating DCT when no FPU is available, multiscanning/progressive encoding, entropy optimization, input smoothing, block smoothing, IDCT scaling, upsample scaling/merging, and quantization passes.

Progressive and multiscanning decode support is intentionally retained because progressive JPEG is required for PDF 1.3. It raises `D_MAX_BLOCKS_IN_MCU` to 64 for Adobe compatibility on unusual JPEG files.

This file is compile-time feature selection for embedded IJG code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsjmorec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.c

Standalone Ghostscript library test program. `main` captures real stdio before Ghostscript redefines it, initializes platform and library state, allocates interpreter memory, initializes IO devices, selects/copies the first device, wraps it in a bounding-box device, creates a graphics state, installs a screen halftone, ensures a minimum graphics-state stack, erases the page, dispatches a selected test, outputs the page, prints the bounding box, and finalizes the library.

The file contains test cases covering major public graphics APIs:
- `test1`: randomized kaleidoscope path/color/fill exercise.
- `test2`: bitmap pattern fill over paths.
- `test3`: RasterOp calls on monobit-style devices.
- `test4`: dynamic device resolution through parameter lists.
- `test5`: unmasked, explicit-mask, and chroma-key image APIs.
- `test6`: CIE color rendering, CIEABC color space, and color-mapping wrapper behavior.
- `test7`: non-monotonic Type 5 halftone masks.
- `test8`: partially transparent pixmap patterns.
- optional `test10`: captured printer-output replay under `CAPTURE`.

It also provides local stubs for GC relocation procedures, `gs_to_exit`, `gs_abort`, `copysign`, an ordered-dither spot function, rectangle-fill helper, and deterministic random number generation.

This is not production rendering code; it is a broad integration harness for validating Ghostscript library/device/color/path/image APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.h

Declares the Ghostscript library initialization/finalization API. `gs_lib_init` performs full initialization using the C heap by default, while `gs_lib_init0` and `gs_lib_init1` split initialization so clients can substitute a different allocator after phase 0.

`gs_lib_finit` performs cleanup after execution and accepts exit status, error code, and memory pointer. The header requires stdio and Ghostscript memory definitions from its includer context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.c

Implements the Ghostscript library context stored on `gs_memory_t`. `gs_lib_ctx_init` allocates a `gs_lib_ctx_t`, captures real process stdio, initializes stdout/stderr redirection state, DLL callback hooks, polling hook, per-context `gs_next_id`, and dictionary auto-expand policy.

`outwrite`, `errwrite`, `outflush`, and `errflush` centralize output routing. Output can go to redirected files, stderr, callback functions, or captured real stdout/stderr. Diagnostics use a file-static `mem_err_print`, so stderr handling is effectively process-global even though most context data is per-memory.

`gs_lib_ctx_get_non_gc_memory_t` exposes the non-GC allocator associated with the diagnostic memory context. The file is important for shared-library embedding and callback-based IO.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.h

Defines `gs_lib_ctx_t`, the per-library/per-memory context used by Ghostscript embedding code. It stores stdio streams, redirected stdout stream, redirection flags, interactive-stdin flag, caller handle, stdin/stdout/stderr/poll callbacks, next-id counter, interpreter/system hooks, PostScript name table pointer, and dictionary auto-expand policy.

Declares `gs_lib_ctx_init`, `gs_lib_ctx_get_interp_instance`, and `gs_lib_ctx_get_non_gc_memory_t`. The comments note some fields are legacy or interpreter-specific hacks rather than clean library-context state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.c

Implements Ghostscript line-parameter operators. Device-independent setters/getters cover line width, cap, join, miter limit, dash pattern, dash adaptation, curve join, and dot length. Device-dependent quality/state controls cover flatness, stroke adjustment, accurate curves, and dot orientation.

Important validation behavior:
- cap/join values are range-checked against `gs_line_cap_max`/`gs_line_join_max`;
- miter limit must be at least 1 and stores a derived `miter_check`;
- dash elements must be non-negative and non-empty patterns must have nonzero total length;
- flatness is clamped to `[0.2, 100]`;
- dot length cannot be negative;
- dot orientation only accepts simple axis-aligned or swapped CTMs.

`gx_set_dash` owns dash pattern memory using the graphics state's allocator, resizing/freeing as needed, and precomputes initial dash index, ink state, and remaining distance from the offset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.h

Public header for line parameters and rendering-quality controls. It includes `gslparam.h` for line cap/join enums and declares all setter/getter functions implemented by `gsline.c`.

It separates standard PostScript-style parameters from Ghostscript extensions and also exposes imager-level accessors for flatness, dash adaptation, and accurate-curve settings through the opaque `gs_imager_state`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslparam.h

Defines line cap and line join enumerations. Standard PostScript values are present, plus Ghostscript extensions: triangle cap, no join, triangle join, and unknown sentinels.

`gs_line_cap_max` is 3, so `gs_cap_unknown` is not accepted by normal setters. `gs_line_join_max` is 4, so triangle join is accepted while unknown is not.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.c

Implements a `gs_memory_t` allocator backed directly by C `malloc`/`free`. Each allocation is prefixed with `gs_malloc_block_t`, linked into an allocation list, and records size, type descriptor, and client name. This allows status reporting and bulk cleanup via `free_all`.

Allocation paths support raw bytes, structures, byte arrays, struct arrays, strings, resize, object-size/type lookup, finalization on free, optional debug fill patterns, and enable/disable of free operations. It detects size overflow for byte arrays and logs missing blocks when freeing unknown pointers.

`heap_available` probes the heap with up to 20 temporary 64 KB allocations to estimate available memory for status reporting. `gs_malloc_wrap` layers a monitor-locked wrapper and retrying wrapper around the raw heap allocator; `gs_malloc_unwrap` reverses this. `gs_malloc_init` creates the default wrapped allocator and initializes or inherits the library context.

This is the default non-GC allocator foundation used by Ghostscript in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.h

Declares the C-heap allocator interface. `gs_malloc_memory_t` embeds `gs_memory_common` and tracks the allocation list, configured limit, current used bytes, and max used bytes.

Exports initialization/release routines, default allocator creation/release, wrappers for non-GC `gs_malloc`/`gs_free`, and functions to wrap/unwrap a heap allocator with locking/retry layers. This header is the public entry point for Ghostscript's malloc-backed memory manager.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.c

Implements matrix creation, arithmetic, coordinate transforms, fixed-point transforms, bounding-box transforms, and compact stream serialization.

Core APIs create identity, translation, scaling, and rotation matrices; multiply/invert/translate/scale/rotate matrices; transform points and distances forward or inverse; and transform bounding boxes by evaluating all four corners. Fast paths handle axis-aligned `xx/yy` and swapped `xy/yx` matrices.

Fixed-point support converts `gs_matrix` to `gs_matrix_fixed`, validates translation range, transforms points/distances into `gs_fixed_point`, and optionally provides rounded current-point transforms. Error paths return `undefinedresult` for non-invertible matrices and `limitcheck` for fixed overflow.

`sput_matrix` and `sget_matrix` serialize matrices with a compact control byte describing repeated/zero coefficients and optional float payloads, used by band-list/stream code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.h

Defines `gs_matrix` as six floats: `xx`, `xy`, `yx`, `yy`, `tx`, `ty`, matching PostScript transformation matrix semantics. Provides constant-initializer macros, identity body, and fast-path predicates `is_xxyy` and `is_xyyx`.

Declares matrix construction, arithmetic, point/distance/bbox transforms, and stream serialization functions. It forward-declares `stream` so callers do not need full stream internals for prototypes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmdebug.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmdebug.h

Allocator-debugging header. Declares fill-pattern bytes for allocated, local block, collected, deleted, and freed memory states. Aliases allocator debug enablement to `gs_debug['@']`.

Defines `gs_alloc_fill`, which conditionally calls `gs_alloc_memset` under `DEBUG`; in non-debug builds it compiles to no-op. This is used by allocator implementations to make memory misuse easier to diagnose.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmdebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.c

Implements `gs_memory_locked_t`, a monitor-locked wrapper around another `gs_memory_t`. Initialization installs a full procedure table and allocates a `gx_monitor_t`; release frees wrapper structures without freeing the target allocator.

Most methods enter the monitor, forward the allocation/free/status/root operation to the target, then leave the monitor. `free_all` frees only wrapper structures/allocator, not target data. `stable` lazily wraps the target’s stable allocator in another locked allocator when needed.

The wrapper serializes allocator access for multithreaded use while preserving the same memory-manager API.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.h

Declares `gs_memory_locked_t`, which embeds `gs_memory_common` and stores a target allocator plus `gx_monitor_t`. The header documents that this wrapper does not track acquired memory itself, so `free_all` with `FREE_ALL_DATA` is effectively a no-op at the wrapper level.

Exports init, release, and target-accessor functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemlok.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.c

Generic allocator support for Ghostscript. Defines debug fill-byte constants, structure descriptors for free blocks, byte blocks, GC roots, and const strings, plus bytestring enumeration/relocation helpers that distinguish object-backed bytes from raw string-backed data.

Provides utility functions for debug filling large blocks, resize-or-allocate struct arrays, raw immovable struct allocation, no-op free/consolidation handlers, const-depunting free helpers, bytestring free helpers, structure type accessors, and root registration.

Under `DEBUG`, it traces reference-count operations and attempts to name referenced objects. It also defines `rc_free_struct_only`, and generic GC pointer enumeration/relocation for basic structures using descriptor metadata and optional supertype traversal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.h

Primary Ghostscript memory-manager interface. It defines opaque structure descriptors, allocator type, pointer type, GC root type, memory status reporting, raw allocator procedures, object/string allocation procedures, root registration, free enabling, stable allocator access, consolidation, and `free_all` flags.

The API distinguishes objects from strings: objects are aligned and cannot have interior references, while strings may be unaligned and may be referenced internally. It also supports movable versus immovable allocations for GC-capable allocators.

`gs_memory_common` embeds stable allocator, procedure table, library context, a PCL/PXL memory tracking head, and non-GC parent allocator pointer. The header provides the macros used throughout the Ghostscript codebase for allocation, resize, free, type/size lookup, and root management.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemraw.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemraw.h

Legacy raw-memory allocator interface retained entirely inside `#if 0`. The comments explain that `gsmemraw` used to be an abstract base class but is no longer used; `gs_memory_t` is now the concrete base interface because the full interface is needed across the system.

The disabled content documents raw allocation semantics, alignment caveats, status reporting, stable allocators, `free_all`, consolidation, raw procedure tables, and `gs_raw_memory_s`. The active header only provides include guards, so it is documentation/compatibility residue rather than compiled API.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemraw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.c

Implements `gs_memory_retrying_t`, a wrapper allocator that retries allocation failures after invoking a recovery closure. Initialization installs a forwarding/retrying procedure table, sets the target allocator, inherits the library context, points `non_gc_memory` at itself, and installs a default no-retry recovery procedure.

Allocation, resize, string allocation, struct allocation, array allocation, and root registration use the `RETURN_RETRYING` loop: call the target, and if it returns null while recovery says retry is allowed, call the recovery procedure and retry. Free, status, object type/size, unregister, enable-free, and consolidation simply forward to the target.

`stable` lazily wraps the target stable allocator in a retrying allocator if the stable target differs. This wrapper provides a generic low-memory recovery hook without changing allocator clients.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.h

Declares the retrying allocator wrapper. Defines `gs_memory_recover_status_t` with `RECOVER_STATUS_NO_RETRY` and `RECOVER_STATUS_RETRY_OK`, plus the recovery callback signature.

`gs_memory_retrying_t` embeds `gs_memory_common`, target allocator, recovery procedure, and recovery data. Exports init/release, recovery-closure setter, and target accessor. Like the locked wrapper, it does not track target data itself.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmisc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmisc.c

Large utility implementation for Ghostscript. It includes redirected printf helpers (`outprintf`, `errprintf`) that route through library-context output functions, global debug state (`gs_debug`, `gs_debug_out`), debug flag checking, debug file/line logging, program identification printing, error logging, and interrupt-aware return handling.

It supplies compatibility replacements for missing or broken C library functions: `memmove`, `memcpy`, `memchr`, `memset`, and `realloc` depending on platform macros. Debug helpers dump bytes/bitmaps and print strings normally or as hex.

Arithmetic utilities include positive modulo, integer GCD, modular division, integer log2, fixed-point multiply/divide, float/double-to-fixed and fixed-to-float conversions for FPU-limited builds, traced `sqrt`, degree-based sin/cos/sincos with exact quadrantal handling, optional lookup-table trigonometry, and PostScript-style `atan2` degrees.

This file is a portability and diagnostics hub used by many Ghostscript subsystems.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnogc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnogc.c

Implements a non-tracing “ersatz GC” for environments that do not need full garbage collection or save/restore. It focuses on string freelists and free-space consolidation.

`sf_alloc_string` searches the current chunk’s large-string freelist for exact-size matches. `sf_free_string` returns strings either by moving `ctop` when freeing the top string, by inserting large strings into an address-ordered freelist, or by adding tiny strings to 1-byte freelists per 256-byte block. Debug checks detect overlapping frees.

`sf_consolidate_free` closes the current chunk, merges free strings at the bottom of string storage, can recover string-marking-table space when no string space is used, reopens the chunk, and then consolidates object free space. `gs_nogc_reclaim` installs these string-freelist procedures on all VM spaces and stable memories, then consolidates.

This is reclamation without tracing: it coalesces allocator-managed free regions but does not discover unreachable live objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnogc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnogc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnogc.h

Small interface header for the non-tracing GC/reclaim implementation. Includes `gsgc.h` for `vm_reclaim_proc` and declares `gs_nogc_reclaim` with that signature.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnogc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnorop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnorop.c

Provides stubs for builds without implemented RasterOp support. `gs_current_logical_op` always returns `lop_default`; `gs_set_logical_op` accepts only `lop_default` and returns `rangecheck` for other logical operations.

Memory-device and default `copy_rop`/`strip_copy_rop` implementations return errors (`rangecheck` or `unknownerror`) to signal unsupported operations. ROP texture-device allocation also returns `rangecheck`, and the maker function is a never-called no-op.

This file satisfies link dependencies while intentionally disabling RasterOp behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnorop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.c

Implements a simple notification-list mechanism. `gs_notify_init` stores allocator and empty head. `gs_notify_register` allocates a registration node and prepends it. `gs_notify_unregister_calling` removes matching registrations, optionally all entries for a procedure when `proc_data` is null, invokes a caller-provided unregistration callback, and frees nodes. `gs_notify_unregister` uses a no-op callback.

`gs_notify_all` walks the list while caching `next` before callback invocation, calls every client even if errors occur, and returns the first negative error. `gs_notify_release` frees all registrations.

GC descriptors are defined for registration nodes and lists, so notification lists can be embedded in GC-managed structures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.h

Declares Ghostscript notification machinery. A `gs_notify_registration_t` stores callback, callback data, and next pointer. `gs_notify_list_t` stores allocator and first registration.

The header documents that duplicate registrations are not detected, clients must unregister before finalization, and providers should notify clients on provider finalization with `event_data == NULL`. It also declares private/public GC descriptor macros and the full registration, unregistration, notification, and release API.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.c

Implements the overprint/overprint-mode compositor. It defines serialization for potentially 64-bit `gx_color_index` values using base-128 variable-length bytes, compositor equality, string write/read for command-list use, the public `gs_composite_overprint_type`, `gs_create_overprint`, and `gs_is_overprint_compositor`.

The file defines `overprint_device_t`, a forwarding device with overprint state: `drawn_comps` for non-separable targets and `retain_mask` for separable/linear targets. Three procedure tables represent no-overprint forwarding, generic overprint, and separable overprint. Procedure tables are lazily completed with `gx_device_forward_fill_in_procs`.

Overprint parameter updates choose the correct procedure table, compute process/spot drawn components via color-mapping procedures when retaining spot components, disable overprint for degenerate “all components drawn” cases, and build a byte-order-aware retain mask for separable/linear devices. Little-endian depth > 8 color indexes are byte-swapped for bitmap order.

Device methods open the target and copy parameters, forward `put_params` while syncing open state, forward page-device lookup, and intercept overprint compositor creation by updating the existing overprint device. Rectangle fill methods dispatch to generic or separable overprint helpers, selecting the optimized separable path when depth divides the fill chunk width.

`c_overprint_create_default_compositor` suppresses overprint when no components are retained or when the target has only one component, allocates an overprint forwarding device, copies target parameters, sets the target, and applies overprint parameters. Several comments describe remaining stub/performance areas for additional overprint-specific drawing methods.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsovrc.c -->