# Group Research: group_1574_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxwts_h_sources_os__7e59309d738a

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.h

Defines Ghostscript well-tempered screening data structures. It introduces 16-bit screen samples, the base `wts_screen_t` shape, and three screen types: rational, J, and H screens.

Key structures:
- `wts_screen_s`: common screen type, cell dimensions, shift, and sample buffer.
- `wts_screen_j_t`: probability/jump-based screen variant with A/B horizontal and C/D vertical jumps.
- `wts_screen_h_t`: H-screen variant storing exact `px`/`py` targets and integer split positions.
- `wts_get_samples(...)`: exported accessor for sample runs at a given coordinate.

This is a small rendering/halftone support header; it has no filesystem or OS-facing behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxxfont.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxxfont.h

Defines Ghostscript’s external font, or xfont, interface. The design comments establish that devices supply xfonts, xfonts are transformation-specific bitmap providers, and allocation/release is mediated through object procedures.

Core API:
- `gx_xfont_common` and `gx_xfont_s`: generic xfont object with a procedure table.
- `gx_xfont_procs_s`: factory lookup, glyph mapping, metrics, render, and release methods.
- `xfont_proc_*` macros: stable prototypes for implementation tables.
- `gs_private_st_dev_ptrs1`: GC descriptor helper for xfonts that reference one device pointer.

The file is part of rendering/device integration. The main portability concern is ABI stability of callback signatures and GC relocation for device-backed font objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxxfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzacpath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzacpath.h

Declares the clipping path accumulator device. `gx_device_cpath_accum` is a Ghostscript device that accumulates a rectangle list while optionally clipping to a band boundary rectangle.

Exports:
- `gx_cpath_accum_begin`
- `gx_cpath_accum_set_cbox`
- `gx_cpath_accum_end`
- `gx_cpath_accum_discard`
- `gx_cpath_intersect_path_slow`

This supports banded rendering and clipping path construction. Its role is internal graphics geometry, not OS file handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzacpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzcpath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzcpath.h

Defines internal clipping path structures. A `gx_clip_path` subclasses `gx_path`, adds a local/reference-counted rectangle list, fill rule, inner/outer bounds, path validity, high-level path list, and a change id.

Key types:
- `gx_clip_rect_list`: ref-counted rectangle list.
- `gx_cpath_path_list`: retained source paths for high-level devices.
- `gx_clip_path_s`: concrete clip path.
- `gs_cpath_enum_s`: iterator state for enumerating a clipping path as path or rectangles.

The file is tightly coupled to `gzpath.h` and Ghostscript GC descriptors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzcpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzht.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzht.h

Declares internal halftone construction, installation, and cache APIs. It covers sampled/threshold/client orders, screen enumeration, halftone cache sizing, fractional color helpers, and colorant-name resolution.

Important elements:
- `gs_screen_enum_s`: holds sampled halftone, order, transform matrices, position, and graphics state.
- `gx_ht_cache_s`: stores cached tiles, backing bits, copied order, cache level geometry, and render callback.
- Cache limits distinguish small and large memory builds.
- `gx_ht_install`, `gx_imager_dev_ht_install`, and transfer reset routines install effective halftones into graphics state/imager state.

This is central to raster output quality and memory use. It is not filesystem code, but it includes architecture-sensitive cache sizing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzht.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzline.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzline.h

Small internal header for line parameters. It exposes the GC descriptor macro for `gx_line_params`, noting that the pattern pointer must only be followed when the pattern size is nonzero.

Exports:
- `private_st_line_params()`
- `st_line_params_num_ptrs`
- `gs_currentlineparams(const gs_imager_state *)`

This is graphics-state support for stroke parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzline.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzpath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzpath.h

Defines Ghostscript’s internal path representation. Paths are linked lists of start, line, close-line, and Bezier curve segments, with subpaths holding closure state and curve counts.

Key structures and mechanics:
- `segment`, `line_segment`, `line_close_segment`, `curve_segment`, `subpath`.
- Curve point/coefficient conversion macros and monotonic/flattening procedure declarations.
- `gx_path_state_flags`: tracks current point validity, open subpath, drawing state, and out-of-range coordinates.
- `gx_path_segments`: ref-counted shared segment ownership.
- `gx_path_s`: full path object with allocator, bounding box, segment ownership, state flags, counts, current position, and virtual path procs.
- `gs_path_enum_s` and `gx_flattened_iterator_s`: enumeration/flattening state.

This is a core geometry header. The main invariants are path state flags, segment reference ownership, and GC descriptors for shared path structures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzpath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.c

Implements the spot analyzer device used for glyph topology analysis and stem recognition, primarily for TrueType grid fitting and antialiased rendering support.

Main flow:
- Defines a mostly-null device procedure table, using `gx_default_fill_path` and a custom unlimited clipping box.
- Allocates reusable linked buffers for trapezoids and trapezoid contacts, with hard caps around 10000 entries.
- `gx_san__obtain` / `gx_san__release` manage a ref-counted analyzer device.
- `gx_san_begin` resets active band/contact state while reusing allocated buffers.
- `gx_san_trap_store` consumes trapezoids in increasing Y-band and X order, reconstructs upper/lower contacts, merges prolongations, and tracks glyph x extents.
- Stem generation walks the reconstructed topology, recognizes vertical-ish boundaries, computes area/axis-derived average width, and emits `gx_san_sect` hints through a caller handler.

Notable implementation details:
- Cyclic lists model bands and contact sets.
- Visual tracing hooks (`vd_*`) draw traps, contacts, stems, and hints under tracing.
- The algorithm assumes ordered trapezoid input from the fill pipeline.
- `gx_san_end` is currently empty.

This is graphics/glyph analysis code. It is memory-management sensitive because GC descriptors only consider buffer links valid during GC.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.h

Declares the spot analyzer device interface and data structures. The header states the analyzer consumes trapezoid fill output for glyph grid fitting and antialiased rendering, with current implementation focused on vertical stem recognition.

Key types:
- `gx_san_trap`: trapezoid geometry, outline segment pointers, band topology, side flags, and recognizer state.
- `gx_san_trap_contact`: cyclic neighbor relationship between lower and upper trapezoids.
- `gx_san_sect`: emitted stem section with left/right coordinates, outline segment pointers, and side mask.
- `gx_device_spot_analyzer`: Ghostscript device plus trap/contact buffers and current topology state.

Exports analyzer lifecycle, trapezoid storage, and stem generation functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzstate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzstate.h

Defines Ghostscript’s private `gs_state_s` graphics state. The imager state common prefix must be first, followed by saved-state linkage, CTM caches, paths, clipping paths, color state, font state, device state, transparency state, and client procs.

Important fields:
- `path`, `clip_path`, `clip_stack`, `view_clip`, and effective clip cache.
- `color_space`, `ccolor`, and `dev_color`.
- `font`, `root_font`, `char_tm`, cachedevice/charpath state.
- `device`, device filter stack, transparency group stack.
- `gs_state_do_ptrs` enumerates GC-managed pointers outside imager state and device.

This is a central object definition; correctness depends on GC enumeration order and the “imager state first” layout contract.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.c

Implements the interpreter allocator over Ghostscript reference memory spaces. `ialloc_init` creates local, stable-local, system, and optionally distinct global/stable-global memories; Level 1 aliases global to local.

Main services:
- Select current VM space with `ialloc_set_space`.
- Expose memory space, new mask, and save level.
- Reset GC request flags across VM spaces.
- Register ref roots.
- Allocate, shrink, and free ref arrays with special handling for GC terminator refs, LIFO allocation, large chunks, packed arrays, and dangling-reference nulling.
- Allocate string refs.

Key invariant: every run of refs has an extra terminator ref used by the garbage collector. Ref-array free paths either reclaim LIFO/whole-chunk storage or null out contents and account lost bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.h

Public/internal interface for interpreter allocation. It maps current interpreter context memory to shorthand macros:
- `gs_imemory`, `iimemory`, `imemory`
- local/global/system allocator aliases
- byte, struct, array, string allocation/free wrappers
- ref-array and string-ref wrappers when `ref` types are visible

Declares allocator initialization, GC request reset, validation, VM space selection, new mask, save level, and `make_i*struct` helpers that tag refs with the current VM space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.c

Implements the public Ghostscript interpreter API used by DLL/static clients. It wraps `gs_main_*` interpreter entry points around an opaque library context.

Key behavior:
- `gsapi_revision` returns product/copyright/revision metadata.
- `gsapi_new_instance` allocates memory and a main instance, but gates process-wide instance count to one.
- `gsapi_delete_instance` clears callbacks/display pointer and decrements the counter; comments note no real deletion occurs.
- `gsapi_set_stdio`, `gsapi_set_poll`, and `gsapi_set_display_callback` install callbacks.
- `gsapi_init_with_args`, `gsapi_run_string*`, `gsapi_run_file`, and `gsapi_exit` delegate to `gs_main_*`.
- `gsapi_set_visual_tracer` installs visual tracing interface.

Notable issue: `gsapi_run_string` passes `get_minst_from_memory(ctx->memory)` as the first argument to `gsapi_run_string_with_length`, whose first parameter is expected to be the API instance pointer. This vintage code relies on surrounding context assumptions and is worth scrutiny.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.h

Declares the public Ghostscript API and platform export/calling-convention macros. It supports Windows, OS/2, classic Mac export pragmas, and default empty macros for static/non-Windows builds.

API surface:
- revision query
- single-instance create/delete
- stdio, polling, display callbacks
- interpreter initialization
- run string/file helpers
- interpreter exit
- visual tracer debug hook
- function pointer typedefs for dynamic binding

The header explicitly warns that this implementation supports only one Ghostscript instance per process due to global state and `gsapi_instance_counter`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iastate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iastate.h

Convenience include wrapper for interpreter allocator state. It includes `gxalloc.h`, `istruct.h`, and `ialloc.h`.

No declarations beyond include guarding. Its purpose is to collect allocator-state dependencies in the correct order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iastate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iastruct.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iastruct.h

Small include wrapper for interpreter memory-manager implementation structures. It includes `gxobj.h` and `ialloc.h`.

It contains no types or functions itself; it is a dependency coordination header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iastruct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.c

Implements Level 2 encoded number reading utilities for PostScript binary object sequences and homogeneous number arrays.

Main functions:
- `num_array_format`: validates encoded number strings or accepts array forms.
- `num_array_size`: computes element count.
- `num_array_get`: retrieves numeric refs from arrays or encoded byte strings.
- `sdecode_number`: decodes 16/32-bit fixed-point integer formats or float formats.
- `sdecodeushort`, `sdecodeshort`, `sdecodelong`, `sdecodefloat`: endian-aware primitive decoders.

Portability details:
- Handles MSB/LSB encoded formats.
- Sign-extends 32-bit longs on platforms where `long` is larger than 4 bytes.
- Converts IEEE floats to native floats if the architecture does not use IEEE native floats.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.h

Defines encoded number constants and decoder prototypes. It documents an Adobe interpreter compatibility bug around byte-swapping native IEEE reals and enables emulation with `BYTE_SWAP_IEEE_NATIVE_REALS`.

Important constants:
- `bt_num_array_value`
- `num_int32`, `num_int16`, `num_float`, `num_float_native`
- `num_msb`, `num_lsb`, `num_array`
- `enc_num_bytes_values` and `encoded_number_bytes`

Exports array-format helpers and primitive number decoders.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccfont.c

Provides initialization support for compiled fonts. It converts compact C font tables into interpreter refs, dictionaries, arrays, names, strings, and parsed objects.

Main components:
- `str_enum` and `key_enum`: walk compact string/key arrays.
- `cfont_next_string`: decodes inline string encodings, null markers, and parsed-object strings.
- `cfont_put_next`: resolves encoded or string keys to names and stores dictionary entries.
- `cfont_*_create`: create dictionaries and arrays with ref/string/number/name/scalar contents.
- `cfont_ref_from_string`: uses the scanner to parse an object from a string.
- `ccfont_procs`: procedure vector passed to compiled-font initializers.
- `.getccfont` operator: returns compiled font count or builds a requested font object.

This file bridges generated C font assets into PostScript VM objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccinit0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccinit0.c

Defines an empty Ghostscript initialization string for non-compiled initialization:
- `gs_init_string[] = { 0 }`
- `gs_init_string_sizeof = 0`

The comment notes `gsmain.c` recognizes an empty init string specially.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iccinit0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icclib.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icclib.mak

Partial makefile for building Graeme W. Gill’s `icclib` inside Ghostscript. It expects variables such as `GLSRCDIR`, `ICCSRCDIR`, `ICCGENDIR`, and `ICCOBJDIR`.

Key build rules:
- Sets `ICCPROFVER=9809`.
- Builds `icc.$(OBJ)` from `icc.c` and ICC headers.
- Creates generated `icclib.dev` module metadata.
- Provides clean/config-clean targets for ICC generated/object files.

The makefile includes platform syntax accommodations for OpenVMS include flags.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icfontab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icfontab.c

Defines the compiled-font procedure table. It includes generated `gconfigf.h` twice:
- First to declare extern compiled font procedures.
- Second to populate `fprocs[]`.

Exports `ccfont_fprocs`, returning the procedure count, table pointer, and `ccfont_version` for compatibility checking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icfontab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar.h

Defines execution-stack layout and helpers for character rendering operators. The `snumpush` frame stores the text enumerator, procedure slots, saved stack depths, saved gstate level, saved font/root font, completion proc, and mark.

Exports support functions from `zchar.c`, including show setup/continuation/free, glyph refs, stringwidth finish, cachedevice operators, and width-only inspection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar1.h

Declares Type 1/Type 2 character rendering support.

Exports:
- `charstring_execchar`: implementation entry for `.type1/2execchar`.
- `zchar1_glyph_outline`: glyph outline procedure.
- `zcharstring_outline`: build outline from a CharString for Type 1/2 and CIDFontType 0 usage.
- glyph info helpers.
- `z1_set_cache`: cache setup for rendered glyphs.

This header connects interpreter font operators to Type 1/2 charstring execution and glyph cache setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icharout.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icharout.h

Interface to character outline and cache setup helpers in `zcharout.c`.

Key declarations:
- `zchar_exec_char_proc`
- `zchar_get_metrics` and `zchar_get_metrics2`
- `zchar_get_CDevProc`
- `zchar_set_cache`
- `zchar_charstring_data`
- `zchar_enumerate_glyph`

It defines `metrics_present` to distinguish no metrics, width-only metrics, and side-bearing-plus-width metrics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icharout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icid.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icid.h

CID font interface header for `zcid.c` and `zfcid0.c`.

Exports:
- `cid_system_info_param`
- `cid_to_TT_charcode`
- `cid_fill_CIDMap`
- `ztype9mapcid`

It supports CIDSystemInfo parsing and CID-to-TrueType charcode/glyph mapping using Decoding, TT cmap, and SubstNWP data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icie.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icie.h

Internal CIE color handling interface. It mostly exports parameter acquisition helpers from `zcie.c` to `zcrd.c`, plus cache coordination in the other direction.

Capabilities:
- Read range arrays, 3-ranges, 3x3 matrices, procedure arrays, WhitePoint/BlackPoint, and lookup tables from dictionaries.
- Finish CIE color space setup.
- Prepare sampled procedure caches for 1/3/4 component CIE transforms.
- Join CIE render caches with graphics state.

This is color-management support for interpreter-level CIE color spaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icolor.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icolor.h

Declares interpreter color remapping procedures for transfer functions and related caches.

Exports:
- stack slot counts for `zcolor_remap_one`
- `zcolor_remap_one`
- unsigned and signed remap finish routines
- `zcolor_reset_transfer`
- `zcolor_remap_color`

The comments note that special-form procedures may avoid scheduling work but still return `o_push_estack`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icolor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconf.c

Builds configuration-dependent interpreter tables from generated `gconf.h`.

Defines:
- `gs_main_instance_init_values`
- `gs_init_file_array`
- `gs_emulator_name_array`
- function type table and count
- `op_defs_all` and `op_def_count`
- plugin instantiation table

This is generated-configuration glue. It binds configured initialization files, emulators, function builders, operators, and plugins into the interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconf.h

Collected imports for interpreter configuration:
- `gs_init_string`
- `gs_init_string_sizeof`
- `gs_init_file_array`
- `gs_emulator_name_array`

It links initialization-string data from `iccinit[01].c` and table data from `iconf.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconfig.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconfig.c

Duplicate configuration table source with the same content and `$Id` label as `iconf.c`. It defines interpreter init values, init file array, emulator array, function type table, operator table, and plugin table from `gconf.h`.

Its presence likely supports alternate build naming or generated build rules. Behaviorally it is equivalent to `iconf.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icontext.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icontext.c

Implements interpreter context state lifecycle and GC support.

Main responsibilities:
- GC descriptor enumerates/relocates graphics state, stdio refs, userparams, dual memory, and dictionary/execution/operand stacks.
- `context_state_alloc` allocates stacks, initializes `system_dict`, allocates graphics state, copies dual memory, creates `userparams`, initializes scanner/security flags and invalid stdio refs, and increments VM context counts.
- `context_state_load` copies context-local dictionary entries into `systemdict`, installs saved `userparams`, resets user parameters, restores save checking, clears estack caches, and refreshes dictionary-stack top cache.
- `context_state_store` cleans ref stacks and saves `systemdict.userparams`.
- `context_state_free` decrements VM context counts, returns a freed-space mask if any VM is last-owned, otherwise tears down graphics state and stacks.

This file is important for multi-context Display PostScript support, though the broader API still limits instances.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icontext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icontext.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icontext.h

Externally visible context-state interface.

Declares:
- `st_context_state`
- `set_user_params`
- `context_state_alloc`
- `context_state_load`
- `context_state_store`
- `context_state_free`

It includes `icstate.h` for the concrete state layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icontext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icremap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icremap.h

Defines `int_remap_color_info_t`, used to communicate color remapping procedure and tint values back to the interpreter.

Fields:
- `op_proc_t proc`
- `float tint[GS_CLIENT_COLOR_MAX_COMPONENTS]`

The comment distinguishes pattern remapping, which ignores tints, from DeviceN remapping, which uses them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icremap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icsmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icsmap.h

Interface for loading cached color-space maps for Indexed or substituted Separation spaces.

Defines execution-stack layout constants for map loading and declares:
- `zcs_begin_map(...)`

The note clarifies that the underlying color space is a direct space, not just a base space, because Indexed spaces may map into Separation or DeviceN spaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icstate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icstate.h

Defines externally visible interpreter context state.

`gs_context_state_s` contains:
- graphics state pointer
- dual VM memory
- language level and interpreter mode refs
- random/usertime/superexec state
- userparams and scanner/security flags
- library path and stdio refs
- dictionary, execution, and operand stacks
- plugin list

Also defines the public GC descriptor macro for context states. The stacks are deliberately placed at the end to minimize offsets elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/icstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddict.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddict.h

Thin dictionary API wrapper that supplies the current interpreter dictionary stack implicitly via `i_ctx_p->dict_stack`.

Defines macros:
- `idict_put`
- `idict_put_string`
- `idict_undef`
- `idict_copy`
- `idict_copy_new`
- `idict_resize`
- `idict_grow`
- `idict_unpack`

Used by operator code that already has `i_ctx_p`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddict.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddstack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddstack.h

Minimal dictionary-stack API subset needed by dictionary code.

Declares:
- `dstack_set_top`: refresh cached top dictionary data after stack/dictionary changes.
- `dstack_dict_is_permanent`: checks whether a dictionary is one of the permanent stack dictionaries.

This header breaks a coupling loop between dictionary implementation and dictionary stack internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddstack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idebug.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idebug.c

Interpreter debug support, forcibly compiled with `DEBUG`. It prints names, refs, packed refs, ref memory regions, stacks, and arrays.

Capabilities:
- `debug_print_name` / `debug_print_name_index`
- Full ref printing for arrays, dictionaries, files, fonts, names, operators, packed arrays, strings, structs, etc.
- Packed-ref decoding for packed operators, ints, literal/executable names.
- `debug_dump_one_ref`, `debug_dump_refs`, `debug_dump_stack`, `debug_dump_array`

It depends on type-name and attribute-print macro tables from ref definitions. This file is diagnostic-only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idebug.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idebug.h

Prototypes for interpreter debugging helpers in `idebug.c`.

Exports individual value printers and dump functions for refs, arrays, memory regions, and ref stacks. It forward-declares `ref_stack_t` when needed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.c

Implements Ghostscript dictionaries. Dictionaries have separate key and value arrays, packed or unpacked key representation, open-addressing lookup, deleted-entry markers, save/restore integration, and dictionary-stack cache updates.

Core behavior:
- `dict_alloc` creates dictionary object and contents.
- `dict_create_contents` allocates value array and packed/unpacked key array with wraparound/deleted sentinel.
- `dict_find` hashes names, strings converted to names, integers, reals, and fallback object types; packed dictionaries use macro-generated probing.
- `dict_put` performs store checks, auto-expands if configured, converts string keys to names, unpacks if packed representation cannot hold key, updates count and name single-definition cache.
- `dict_undef` removes entries, marks deleted/empty slots, clears name cache, and nulls value.
- `dict_copy_entries`, `dict_resize`, and `dict_grow` preserve name-cache and save/restore invariants.
- Enumeration APIs: `dict_first`, `dict_next`, `dict_value_index`, `dict_index_entry`.

Design coupling is explicit: dictionaries must update dictionary-stack cached top values and name cached-value pointers, so they depend on `iddstack.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.h

Dictionary package interface. It exposes first-level dictionary layout for performance:
- `values`
- `keys`
- `count`
- `maxlength`
- `memory`

Declares dictionary allocation, find, put, undef, length/capacity, copy, resize, grow, unpack, and enumeration APIs. It also defines access-check macros and hash/rounding algorithms.

Performance notes:
- On larger-memory systems dictionary sizes round to powers of two where possible.
- Huge dictionaries fall back to slower modulo logic.
- Fast clients use internal hash macros and dictionary layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idict.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idictdef.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idictdef.h

Internal dictionary representation details. It documents dictionary capacity semantics, packed vs unpacked key arrays, deleted/empty markers, and the wraparound sentinel entry.

Defines:
- `dict_is_packed`
- packed key constants
- `packed_name_key`
- length/capacity/slot macros
- `packed_search_1` and `packed_search_2` probing macros

This file is implementation-private but shared with high-performance dictionary stack lookup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idictdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.c

Implements display-device callback installation. `display_set_callback` runs a small PostScript snippet to check whether `devicedict /display` exists and retrieves the display device if present.

If the device exists:
- verifies stack result types
- closes the device if already open
- sets `gx_device_display.callback`
- reopens the device if it was open
- cleans stack entries

Harmless when the display device is not compiled in. This bridges the public API display callback into the actual display device instance.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.h

Header for display callback installation. It forward-declares `display_callback` and declares:
- `display_set_callback(gs_main_instance *minst, display_callback *callback)`

Called from the interpreter main path after API callback setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idosave.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idosave.h

Declares support functions for save/restore change recording:
- `alloc_save_change`
- `alloc_save_change_in`

The comment explains why the containing object ref is required: the allocator must choose the correct VM save chain and must know whether the container is a ref array/dictionary or struct for GC tracing and relocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idosave.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.c

Implements typed dictionary parameter extraction helpers.

Supported parameter forms:
- booleans
- signed/unsigned integers, including null-aware signed ints
- floats
- integer arrays, fixed-size integer arrays
- float arrays with optional defaults
- procedures with invalid/empty defaults
- matrices
- UniqueID/XUID
- UID equality checks

Notable compatibility choices:
- Integral reals are accepted for integer parameters and integer arrays because some Fontographer output violates Adobe specs.
- `dict_uid_param` prefers XUID in Level 2, allocates XUID storage, treats UniqueID 0 as invalid/no UID, and validates UniqueID range `0..0xffffff`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.h

Interface for dictionary parameter helpers. It documents common return conventions:
- `0`: valid parameter found
- `1`: defaulted/missing parameter
- `<0`: error
- routines with `null` may return `2` for null

It declares scalar, array, procedure, matrix, UID, and UID-check helpers. It intentionally takes C string keys rather than static name refs to simplify GC handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idsdata.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idsdata.h

Defines `dict_stack_t`, the dictionary stack state.

Fields:
- underlying `ref_stack_t`
- `min_size`
- `userdict_index`
- `def_space` cache for fast `def` legality
- `top_keys`, `top_npairs`, `top_values` cache for fast top-dictionary lookup
- cached `system_dict`

It documents Level 1/Level 2 handling of `globaldict` by replacing it with a systemdict copy rather than physically changing minimum stack size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idsdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.c

Implements dictionary-stack lookup and cache maintenance.

Main functions:
- `dstack_dict_is_permanent`: checks permanent stack dictionaries.
- `dstack_find_name_by_index`: searches from top dictionary down using packed/unpacked dictionary probing, then slower extension-block search if needed.
- `dstack_set_top`: refreshes fast top-dictionary lookup cache and `def_space`.
- `dstack_gc_cleanup`: after GC, scans permanent dictionaries and updates cached value pointers stored in names.

The fast inline path in `idstack.h` is supported by `top_keys/top_npairs/top_values`, and debug builds gather lookup/probe/depth statistics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.h

Generic dictionary stack API. It defines `ds_ptr` and `const_ds_ptr`, declares GC cleanup and full-stack name lookup, and provides fast macros for name lookup.

Key macros:
- `dstack_find_name_by_index_inline`: one-probe top-dictionary fast path, otherwise calls full search.
- `if_dstack_find_name_by_index_top`: checks only the top dictionary.

The comment notes the top-dictionary fast path hits over 90% of name lookups excluding operators.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/idstack.h -->