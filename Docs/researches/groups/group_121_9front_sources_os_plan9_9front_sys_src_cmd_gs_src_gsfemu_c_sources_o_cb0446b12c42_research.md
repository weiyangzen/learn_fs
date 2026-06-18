# Group Research: group_121_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gsfemu_c_sources_o_cb0446b12c42

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely. This group is Ghostscript graphics/font/function/color infrastructure imported into the 9front tree, not filesystem implementation code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfemu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfemu.c

## Role

`gsfemu.c` is a GCC-compatible software floating-point emulation layer for Ghostscript builds that lack hardware/libgcc floating point support.

This is numeric runtime support, not filesystem code.

## Main Interfaces

Implements GCC helper routines for double/single negation, arithmetic, comparisons, and conversions, including `__negdf2`, `__adddf3`, `__muldf3`, `__divdf3`, `__eqdf2`, `__fixdfsi`, `__floatsidf`, `__truncdfsf2`, and `__extendsfdf2`.

## Important Behavior

Works by inspecting IEEE-754 single and double bit layouts directly. Supports big- and little-endian double word ordering through `msw`/`lsw`. Raises `SIGFPE` for selected overflow/divide-by-zero cases. Returns zero rather than denormalized values in several underflow paths. Uses round-to-nearest only.

## Notable Risks

The file explicitly says it is not a complete IEEE implementation: NaNs and denormals are incomplete. It relies on type-punning through pointer casts. Division comments state quotient rounding is not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfemu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.c

## Role

`gsflip.c` converts planar image sample data from MultipleDataSource format into chunky/interleaved sample order.

This is image data layout support, not filesystem code.

## Main Interface

`image_flip_planes`

## Core Behavior

Specialized fast paths handle 3 and 4 planes at 1, 2, 4, 8, and 12 bits/sample. Generic slower paths handle DeviceN-style arbitrary plane counts for 1, 2, 4, 8, and 12 bits/sample.

The code uses static lookup tables, bit-transpose macros, and `sample_store_*` macros from `gsbitops.h`.

## Notable Risks

Bounds checking is delegated to callers. `bits_per_sample` must be 1, 2, 4, 8, or 12. Invalid plane count or unsupported sample depth returns `-1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.h

## Role

`gsflip.h` declares the planar-to-chunky image sample conversion API implemented by `gsflip.c`.

This is image layout infrastructure, not filesystem code.

## Public API

`image_flip_planes(byte *buffer, const byte **planes, int offset, int nbytes, int num_planes, int bits_per_sample)`

## Contract

Input starts at `planes[i] + offset`, output is written to `buffer`, input must contain an integral number of pixels, and valid sample depths are 1, 2, 4, 8, and 12 bits/sample. Returns `0` on success and `-1` for invalid arguments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.c

## Role

`gsfname.c` parses Ghostscript file names into optional `%IODevice%` prefixes and real file names, and can copy names into null-terminated C strings.

This is Ghostscript IO naming support, not filesystem implementation code.

## Main Interfaces

`gs_parse_file_name`, `gs_parse_real_file_name`, `gs_terminate_file_name`, `gs_free_file_name`

## Core Behavior

Empty names return `undefinedfilename`. Plain names without `%` use no explicit IODevice and retain the caller’s string pointer. `%device` and `%device%` both refer to a device-only name. `%device%name` resolves an IODevice and leaves `name` as the filename part. `gs_parse_real_file_name` rejects device-only names with `invalidfileaccess`.

## Notable Risks

`gs_free_file_name` must only be used on structures constructed through these helpers. Device prefix parsing treats `%device` and `%device%` equivalently.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.h

## Role

`gsfname.h` defines `gs_parsed_file_name_t` and declares file-name parsing/termination helpers.

This is Ghostscript IO naming API, not filesystem code.

## Main Type

`gs_parsed_file_name_t` stores allocator, resolved `gx_io_device *`, filename pointer, and filename length.

## Public API

`gs_parse_file_name`, `gs_parse_real_file_name`, `gs_terminate_file_name`, `gs_free_file_name`

## Important Contract

Callers must not allocate and fill `gs_parsed_file_name_t` manually; lifecycle depends on helper-initialized fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.c

## Role

`gsfont.c` implements generic Ghostscript font directory, font allocation, scaled-font caching, current font state, font cache parameters, font purging, default font procedure vectors, and default glyph metadata operations.

This is font/text rendering infrastructure, not filesystem code.

## Main Interfaces

Font directory and allocation: `gs_font_dir_alloc2`, `gs_font_dir_alloc2_limits`, `gs_font_alloc`, `gs_font_base_alloc`.

Font lifecycle/cache: `gs_definefont`, `gs_font_find_similar`, `gs_scalefont`, `gs_makefont`, `gs_purge_font`, `gs_find_font_by_id`.

Current font/cache parameters: `gs_setfont`, `gs_currentfont`, `gs_rootfont`, `gs_cachestatus`, `gs_setcachesize`, `gs_setcachelower`, `gs_setcacheupper`, `gs_setaligntopixels`, `gs_setgridfittt`.

## Core Behavior

The font directory owns original base fonts, scaled-font cache entries, and the rendered character cache. Large cache limits are attempted first unless running in small-memory mode, with fallback to smaller defaults. Scaled fonts are cached for non-composite fonts by base font and exact `FontMatrix`.

GC handling is specialized: base-font list pointers are weak during mark, base fonts unlink from the original-font list during finalization, scaled fonts unlink from the scaled-font cache, and character-cache font/matrix references are enumerated through the font directory descriptor.

## Notable Risks

Scaled-font cache eviction unlinks old fonts but cannot free them because outside references may exist. Exact matrix equality is used for cache hits. Some default glyph metadata depends on expensive outline path construction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.h

## Role

`gsfont.h` is the public generic font and font-cache interface for Ghostscript.

This is font API infrastructure, not filesystem code.

## Main Declarations

Opaque types include `gs_matrix`, `gs_font_dir`, and `gs_font`.

Public APIs cover font directory allocation, `definefont`, scaled font creation, current font state, purge/find-by-id, and cache parameter setters/getters.

## Important Contract

`gs_definefont` is for original unscaled fonts only. `gs_scalefont` and `gs_makefont` report whether a cached scaled font was reused or newly created.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0.c

## Role

`gsfont0.c` implements generic Type 0 composite font GC support and matrix-adjustment hooks for defining and scaling composite fonts.

This is composite font infrastructure, not filesystem code.

## Main Interfaces

`gs_type0_define_font`, `gs_type0_make_font`

## Core Behavior

The GC descriptor enumerates and relocates `data.Encoding`, `data.FDepVector`, and either `data.SubsVector` or `data.CMap`, depending on `FMapType`.

When a composite font has a non-identity `FontMatrix`, `gs_type0_adjust_matrix` copies `FDepVector` and applies `gs_makefont` to descendant composite fonts so descendant matrices incorporate the parent transform.

## Notable Risks

If descendant adjustment fails after allocating a copied dependency vector, the function returns the error without visible cleanup of the partially allocated vector.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0c.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0c.c

## Role

`gsfont0c.c` creates Type 0 wrapper fonts around CIDFont and Type 42 fonts, optionally using a TrueType cmap-derived CMap.

This is font wrapping/conversion support, not filesystem code.

## Main Interfaces

`gs_font_type0_from_cidfont`, `gs_font_type0_from_type42`

## Core Behavior

`type0_from_cidfont_cmap` allocates a Type 0 font, one-entry Encoding array, and one-entry FDepVector. It sets CMap-based mapping, wraps the descendant font, inherits key/font names, and installs Type 0 init/next-character procedures.

`gs_font_type0_from_cidfont` creates an identity CMap. `gs_font_type0_from_type42` first converts Type 42 to CIDFontType 2, then wraps it with either a TrueType cmap-derived CMap or an identity CMap.

## Notable Risks

Error paths contain explicit comments noting missing substructure cleanup. `font0->procs.make_font` is set to `0` because the wrapper path says it is not called.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0c.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.c

## Role

`gsfunc.c` implements generic Ghostscript Function support shared by PDF/PostScript function types.

This is rendering/function infrastructure, not filesystem code.

## Main Interfaces

`alloc_function_array`, `fn_common_free_params`, `fn_common_free`, `fn_check_mnDR`, `gs_function_get_info_default`, `fn_common_get_params`, `fn_copy_values`, `fn_scale_pairs`, `fn_common_scale`, `fn_common_serialize`

## Core Behavior

Provides allocation, validation, copying, scaling, parameter emission, and serialization helpers for concrete function types. Validation checks positive input/output counts and ordered `Domain`/`Range` pairs.

## Notable Risks

`fn_common_serialize` only supports missing `Range` with a small fixed dummy array; larger missing ranges return `unregistered`. Data sources are shared, not copied, by scaled functions according to the generic API contract.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.h

## Role

`gsfunc.h` defines the abstract Ghostscript Function type, common parameter layout, procedure vector, helper macros, and generic API used by all concrete function implementations.

This is rendering/function API infrastructure, not filesystem code.

## Main Types

`gs_function_type_t`, `gs_function_params_t`, `gs_function_info_t`, `gs_function_procs_t`, `gs_function_head_t`, `gs_function_t`

## Important Semantics

Concrete functions provide callbacks for evaluate, monotonicity testing, info query, parameter emission, scaled-copy creation, parameter free, object free, and serialization.

Function scaling maps outputs from `[0, 1]` into supplied target ranges and copies owned parameters/subfunctions so the new function can be freed independently. Data sources may be shared.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.c

## Role

`gsfunc0.c` implements FunctionType 0 Sampled functions, including sample extraction, linear and cubic interpolation, cached Bezier-pole interpolation, monotonicity analysis, scaling, serialization, and initialization.

This is PDF/PostScript function evaluation infrastructure, not filesystem code.

## Main Interface

`gs_function_Sd_init`, `gs_function_Sd_free_params`

## Core Behavior

Sampled functions map `m` inputs through a sample table to `n` outputs. Supported bits per sample are 1, 2, 4, 8, 12, 16, 24, and 32. Supported interpolation orders are 1, 3, and 0 as default-to-1.

The implementation includes bit-level sample readers, input domain clipping and encode mapping, output decode/range clipping, recursive linear/cubic interpolation, optimized cached cubic interpolation using a `pole` array, monotonicity checks, and serialized output of parameters and sampled data.

## Important Constraints

Maximum plausible inputs and outputs are both 16. Some monotonicity paths support only up to 4 dimensions, and tensor monotonicity for cubic paths is limited further to 3 dimensions.

## Notable Risks

Several allocation failure paths in `gs_function_Sd_init` return immediately after partial allocation without freeing prior allocations. The cached interpolation code is complex and explicitly marked as temporary development technology. `Range` is assumed present in cached cubic evaluation and clamping paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.h

## Role

`gsfunc0.h` defines FunctionType 0 Sampled function parameters and public constructor/free functions.

This is sampled-function API infrastructure, not filesystem code.

## Main Definitions

`function_type_Sampled`, `gs_function_Sd_params_t`, `private_st_function_Sd`, `gs_function_Sd_init`, `gs_function_Sd_free_params`

## Parameter Fields

The parameter struct includes common function fields plus `Order`, `DataSource`, `BitsPerSample`, `Encode`, `Decode`, `Size`, and internal cache fields `pole`, `array_step`, `stream_step`, and `array_size`.

## Important Contract

Although the struct exposes internal cache fields, callers are expected to provide external sampled-function parameters and let initialization manage internal cache setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.c

## Role

`gsfunc3.c` implements several LanguageLevel 3 function types: Exponential Interpolation, 1-Input Stitching, and an internal Arrayed Output composition function.

This is PDF/PostScript function infrastructure, not filesystem code.

## Main Interfaces

`gs_function_ElIn_init`, `gs_function_1ItSg_init`, `gs_function_AdOt_init`, and corresponding free-parameter functions.

## Function Types

Exponential Interpolation evaluates `C0 + x^N * (C1 - C0)` with optional range clipping.

1-Input Stitching selects one subfunction based on input bounds, maps the input through that interval’s Encode pair, and evaluates the selected subfunction.

Arrayed Output evaluates `n` subfunctions and assembles their scalar outputs into one `n`-component output, with special handling for overlapping input/output buffers.

## Notable Risks

`fn_1ItSg_make_scaled` scales `pfn->params.n` functions, but Stitching’s subfunction count is `k`; this is worth reviewing if `n != k`. Arrayed Output uses `fn_common_get_params` with a comment questioning parameter reporting. Arrayed Output computes its domain as the intersection of subfunction domains, with a comment noting this is not generally correct but fits shading usage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.h

## Role

`gsfunc3.h` defines LanguageLevel 3 Ghostscript function parameter structures and constructors for Exponential Interpolation, 1-Input Stitching, and Arrayed Output functions.

This is function API infrastructure, not filesystem code.

## Main Definitions

Function type constants: `function_type_ExponentialInterpolation = 2`, `function_type_1InputStitching = 3`, `function_type_ArrayedOutput = -1`.

Parameter structs: `gs_function_ElIn_params_t`, `gs_function_1ItSg_params_t`, `gs_function_AdOt_params_t`.

Public functions: init and free-parameter routines for all three types.

## Important Notes

Arrayed Output is internal-only and explicitly ignores Domain and Range fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.c

## Role

`gsfunc4.c` implements FunctionType 4 PostScript Calculator functions as a compact bytecode interpreter.

This is PDF/PostScript function evaluation infrastructure, not filesystem code.

## Main Interface

`gs_function_PtCr_init`, `gs_function_PtCr_free_params`

## Core Behavior

The evaluator uses a typed stack with bool, int, and float values. It interprets bytecode opcodes for arithmetic, trig/math, integer bit operations, comparisons, stack manipulation, constants, conditional `if`/`else`, and `return`.

A dispatch table maps opcode plus operand types to typed opcodes, coercion opcodes, no-ops, or typecheck.

## Additional Support

`calc_put_ops` reconstructs a symbolic PostScript-like function body. `calc_access` exposes that symbolic body through a fabricated `DataSource`. `fn_PtCr_make_scaled` appends scaling bytecode to transform outputs into target ranges.

## Notable Risks

Monotonicity is not analyzed. Stack depth is limited to 100. `calc_access` is intentionally inefficient. The header notes the GC descriptor needs to include the bogus `data_source`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.h

## Role

`gsfunc4.h` defines FunctionType 4 PostScript Calculator function opcodes, parameters, constructor, and free routine.

This is function bytecode API infrastructure, not filesystem code.

## Main Definitions

`function_type_PostScript_Calculator`, `gs_PtCr_opcode_t`, `PtCr_NUM_OPS`, `PtCr_NUM_OPCODES`, `gs_function_PtCr_params_t`

## Opcode Groups

Arithmetic, comparison, stack, constants, and special control-flow operators: `PtCr_if`, `PtCr_else`, `PtCr_return`.

## Notable Detail

The private GC descriptor macro contains a comment that it needs to include `data_source`, matching the implementation’s fabricated DataSource for symbolic output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfunc4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgc.h

## Role

`gsgc.h` declares the library-level interface to Ghostscript VM spaces and garbage collection.

This is memory-management infrastructure, not filesystem code.

## Main Definitions

`i_vm_space`, `vm_spaces`, `vm_reclaim_proc`, convenience aliases for VM spaces, `GS_RECLAIM`, and backward-compatible `gs_reclaim`.

## Important Semantics

VM spaces are ordered by dynamism. Pointers from more dynamic spaces to equal or less dynamic spaces are allowed, but not the reverse. Foreign space is index 0 so scalar refs need no space bits.

## Notable Risks

The header leaks interpreter-level concepts such as `gs_ref_memory_t` and the four PostScript memory spaces into the library layer, which it acknowledges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.c

## Role

`gsgcache.c` implements a small glyph data cache for Type 42 fonts, primarily when emulating CIDFontType 2 using TrueType data.

This is glyph/font cache infrastructure, not filesystem code.

## Main Interfaces

`gs_glyph_cache__alloc`, `gs_glyph_cache__release`, `gs_get_glyph_data_cached`

## Core Behavior

The cache stores linked `gs_glyph_cache_elem` entries containing glyph data, glyph index, lock count, and next pointer. It uses the font’s stable memory, records a stream and read callback, and registers a font-free notification callback.

Lookup returns cached data if present, otherwise reuses an unlocked element when cache size is above a threshold or allocates a new head element. Returned glyph data uses custom free/substring procs.

## Notable Risks

If `read_data` fails after allocating or reusing an element, the function returns without clearly removing or resetting the partially prepared element. The cache size threshold `32767` is arbitrary. Substring support for cached glyph data returns `unregistered`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.h

## Role

`gsgcache.h` declares the glyph data cache API used by Type 42 glyph loading.

This is font cache API infrastructure, not filesystem code.

## Main Types

Forward declarations for `gs_font_type42`, `gs_glyph_data_t`, `stream`, and `gs_glyph_cache`, plus callback type `get_glyph_data_from_file`.

## Public API

`gs_glyph_cache__alloc`, `gs_glyph_cache__release`, `gs_get_glyph_data_cached`

## Important Contract

The cache is constructed with a Type 42 font, a stream, and a callback that can load glyph data from that stream.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.c

## Role

`gsgdata.c` implements `gs_glyph_data_t` lifecycle and substring support for glyph outline/bitmap data returned by font procedures.

This is glyph data management infrastructure, not filesystem code.

## Main Interfaces

`gs_glyph_data_substring`, `gs_glyph_data_free`, `gs_glyph_data_from_string`, `gs_glyph_data_from_bytes`, `gs_glyph_data_from_null`

## Core Behavior

Glyph data can be backed by permanent font-owned data, dynamically allocated string data owned by a font allocator, or byte-string object data. `gs_glyph_data_free` calls the selected free proc and then resets the glyph data to null, making repeated frees harmless.

## Notable Risks

`glyph_data_substring_by_font` breaks constness to resize/memmove allocated string data. Correct ownership depends on implementors passing a non-null font only for request-allocated data safe to free later.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.h

## Role

`gsgdata.h` defines the glyph data return structure and lifecycle API for outline/bitmap data requested from fonts.

This is glyph data API infrastructure, not filesystem code.

## Main Types

`gs_glyph_data_t` and `gs_glyph_data_procs_t`.

`gs_glyph_data_t` stores `gs_const_bytestring bits`, a procedure table, procedure-private data, and optional memory allocator.

## Public API

`gs_glyph_data_substring`, `gs_glyph_data_free`, `gs_glyph_data_from_string`, `gs_glyph_data_from_bytes`, `gs_glyph_data_from_null`

## Important Contract

Clients receiving glyph data must call `gs_glyph_data_free` when finished. Implementors should pass a font pointer only when the returned data was newly allocated and should be freed by the client.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsgdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.c

## Role

`gshsb.c` implements Ghostscript HSB color setters/getters by converting between HSB and RGB.

This is color conversion infrastructure, not filesystem code.

## Main Interfaces

`gs_sethsbcolor`, `gs_currenthsbcolor`

## Core Behavior

`gs_sethsbcolor` clamps hue, saturation, and brightness into `[0, 1]`, converts HSB to RGB, and calls `gs_setrgbcolor`.

`gs_currenthsbcolor` fetches current RGB color with `gs_currentrgbcolor` and converts it to HSB.

Internal conversion uses algorithms attributed to Rogers, “Procedural Elements for Computer Graphics,” and Ghostscript fixed `frac` arithmetic.

## Notable Details

Gray RGB values map to hue 0, saturation 0, brightness equal to any RGB component. HSB hue is multiplied by 6 and dispatched by sector.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.h

## Role

`gshsb.h` declares the client-facing HSB color API.

This is color API infrastructure, not filesystem code.

## Public API

`gs_sethsbcolor(gs_state *, floatp, floatp, floatp)` and `gs_currenthsbcolor(const gs_state *, float[3])`.

The implementation converts through RGB rather than defining an independent device color space.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.h -->