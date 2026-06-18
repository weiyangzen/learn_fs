# Group Research: group_1559_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gsfemu_c_sources_os_82042271a5d2

Subset scope: `Docs/research_subset_a.md` includes `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfemu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfemu.c

## Role

GCC soft-float support implementation for Ghostscript platforms lacking usable hardware floating point. It supplies compiler helper symbols for single and double precision arithmetic, comparison, and conversion.

## Main Data

Defines IEEE float/double bit extraction macros, endian-aware double word indexing, sign/exponent/mantissa helpers, and bit-level aliases for float/double arguments and results.

## Control Flow

Implements negation, addition/subtraction, multiplication, division, comparisons, int/float conversions, double/float conversion, and int-to-float conversions. Double multiplication uses 14-bit chunk products; division generates quotient bits iteratively. Overflow and divide-by-zero raise `SIGFPE`; many underflows return signed zero.

## Dependencies

Uses `std.h`, `<signal.h>`, architecture endianness macros, and compiler/runtime expectations for `__adddf3`, `__mulsf3`, `__fixdfsi`, etc.

## Notes

This is explicitly not a complete IEEE implementation: only round-to-nearest is attempted, NaNs are not properly handled, and denormal support is absent for several operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfemu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.c

## Role

Converts planar image sample data, used for `MultipleDataSource`, into chunky interleaved pixel data.

## Main Data

Contains specialized converters for 3-plane and 4-plane input at 1, 2, 4, 8, and 12 bits per sample, plus generic N-plane paths for DeviceN-style color data. Uses bit tables, bit transpose macros, and Ghostscript sample-store macros.

## Control Flow

`image_flip_planes` validates bit depth and dispatches by plane count. Optimized routines pack RGB/CMYK-style planar bytes directly; generic N-plane routines extract each sample and write it into the output stream using sample-store helpers.

## Dependencies

Depends on `gx.h`, `gserrors.h`, `gsbitops.h`, `gsbittab.h`, and `gsflip.h`.

## Notes

Unsupported plane/depth combinations return `-1`. Twelve-bit paths assume the input represents an integral number of pixels and operate in 3-byte sample groups.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.h

## Role

Public interface for planar-to-chunky image data conversion.

## Main API

Declares `image_flip_planes`, which takes an output buffer, source plane array, byte offset, byte count, plane count, and bits per sample.

## Contract

Valid bits per sample are 1, 2, 4, 8, or 12. `num_planes` must be non-negative. The input must represent an integral number of pixels; for 12-bit samples, `nbytes` is rounded to a multiple of 3 by caller convention.

## Dependencies

Requires Ghostscript byte types from surrounding includes.

## Notes

Returns `0` on supported conversion and `-1` for invalid plane count or sample depth.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.c

## Role

Utility implementation for parsing Ghostscript file names into optional `%device%` and file-name components.

## Main Data

Operates on `gs_parsed_file_name_t`, storing allocator ownership, `gx_io_device`, pointer to file name bytes, and length.

## Control Flow

`gs_parse_file_name` identifies `%device`, `%device%`, or `%device%name` forms and resolves devices with `gs_findiodevice`; plain names use no explicit device. `gs_parse_real_file_name` rejects device-only names and terminates the file name. `gs_terminate_file_name` sets default IO device when needed and allocates a null-terminated copy. `gs_free_file_name` frees copied names.

## Dependencies

Uses Ghostscript memory, error, type, and IO-device interfaces: `gsmemory.h`, `gxiodev.h`, `gserrors.h`.

## Notes

Empty names and unknown devices return `undefinedfilename`; device-only real names return `invalidfileaccess`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.h

## Role

Declares parsed file-name representation and file-name parsing helpers.

## Main Data

`gs_parsed_file_name_t` records the allocator used for a copied C string, resolved IO device, file-name pointer, and length. The name may initially be unterminated.

## Main API

Declares `gs_parse_file_name`, `gs_parse_real_file_name`, `gs_terminate_file_name`, and `gs_free_file_name`.

## Contract

Callers must construct parsed names through the parser helpers rather than filling the structure manually. `gs_parse_real_file_name` also converts the result to a C string.

## Dependencies

Forward-declares `gx_io_device`; relies on Ghostscript memory and string types.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.c

## Role

Core Ghostscript font directory, font allocation, scaled-font cache, font state, cache-parameter, purge, and default font/glyph procedure implementation.

## Main Data

Defines default cache size constants for large and small memory systems, `gs_font_procs_default`, GC descriptors for font directories and fonts, original/scaled font lists, character cache integration, and font notification lifecycle.

## Control Flow

Font directories are allocated with character cache limits. Fonts are allocated and minimally initialized with IDs, notification lists, default outline-use policy, and procedure tables. `gs_definefont` registers base fonts. `gs_makefont` multiplies matrices, reuses cached scaled fonts when possible, clones font structures, invokes type-specific make hooks, and manages scaled cache eviction. State helpers set/current/root fonts. Cache parameter functions expose and mutate character cache limits. `gs_purge_font` unlinks fonts and purges related char caches. Default procedures implement basic font info, similarity, notdef detection, dummy glyph methods, and glyph info via outline path accumulation.

## Dependencies

Uses Ghostscript memory, GC, matrix, graphics state, device, font, char cache, path, UID, and notification infrastructure.

## Notes

Base-font list pointers are weak for GC marking but relocated during GC. Composite scaled fonts are deliberately not cached because their makefont hooks mutate descendant font vectors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.h

## Role

Public generic font and font-cache interface.

## Main API

Declares font directory allocation, `gs_definefont`, similar-font lookup, `gs_scalefont`, `gs_makefont`, font state accessors, font purge, font lookup by ID, and cache parameter getters/setters.

## Main Types

Forward-declares `gs_font_dir`, `gs_font`, and `gs_matrix`.

## Contract

`gs_definefont` is intended only for original unscaled fonts. `gs_scalefont` and `gs_makefont` return `0` when a cached scaled font is reused and `1` when a new font is created.

## Dependencies

Uses `gs_memory_t`, `gs_state`, `gs_id`, and matrix/font structures from Ghostscript core headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0.c

## Role

Composite FontType 0 support for defining and scaling composite fonts.

## Main Data

Provides the GC structure descriptor for `gs_font_type0`, including `Encoding`, `FDepVector`, and either `SubsVector` or `CMap` depending on `FMapType`.

## Control Flow

`gs_type0_adjust_matrix` scans descendant fonts for composites, copies `FDepVector`, and applies `gs_makefont` to composite descendants using the provided matrix. `gs_type0_define_font` applies this adjustment when a non-identity `FontMatrix` is used. `gs_type0_make_font` performs the same adjustment after scaling.

## Dependencies

Depends on composite font structures in `gxfont0.h`, font directory functions, matrix/device headers, and Ghostscript GC descriptor macros.

## Notes

The adjustment is skipped for identity matrices and for descendant vectors with no composite descendants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0c.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0c.c

## Role

Creates Type 0 composite font wrappers around CIDFonts and Type 42 fonts converted to CIDFontType 2.

## Main Data

Builds a single-entry `FDepVector`, one-entry dynamic `Encoding`, and either an identity CMap or a CMap derived from a TrueType cmap.

## Control Flow

`type0_from_cidfont_cmap` allocates a `gs_font_type0`, initializes FontMatrix, composite procs, name fields, `FMapType=fmap_CMap`, descendant vector, and CMap, then defines it in the font directory. `gs_font_type0_from_cidfont` creates an identity CMap and wraps a CIDFont. `gs_font_type0_from_type42` converts Type42 to CIDFontType2, optionally derives a CMap from the Type42 cmap, then wraps it.

## Dependencies

Uses CID font, CMap, Type42, and Type0 font internals.

## Notes

Error paths contain comments noting incomplete freeing of substructures.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0c.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.c

## Role

Generic support code shared by Ghostscript function implementations.

## Main Data

Defines GC descriptors for `gs_function_t`, function pointer arrays, and function pointer array elements.

## Control Flow

Provides allocation of initialized function arrays, common parameter freeing, common function freeing, validation of input/output counts plus Domain/Range order, default info population, common parameter writing, copying numeric arrays, range-scaling Domain/Range pairs, generic function scaling setup, and serialization of common function fields.

## Dependencies

Uses `gxfunc.h`, `gsparam.h`, Ghostscript memory/error APIs, and `stream`.

## Notes

`fn_common_serialize` writes a dummy zero Range when no Range exists, but only supports up to eight dummy values; larger no-Range functions return `unregistered`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.h

## Role

Generic abstraction for Ghostscript PDF/PostScript Functions.

## Main Data

Defines `gs_function_params_common`, `gs_function_params_t`, `gs_function_info_t`, `gs_function_head_t`, procedure-vector type `gs_function_procs_t`, and base `gs_function_t`.

## Main API

Declares allocation of function arrays and macros for evaluate, monotonicity test, info, parameter writing, scaled copy creation, parameter freeing, full freeing, and serialization.

## Contract

Function type is `int` rather than enum because specific function types are declared across separate headers. Specific function implementations provide their own parameter structs, init functions, free-param functions, and GC descriptors.

## Dependencies

Uses Ghostscript ranges, data source, parameter list, stream, memory, and bool types.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.c

## Role

Implementation of FunctionType 0 sampled functions.

## Main Data

Defines `gs_function_Sd_t`, sample extraction routines for 1/2/4/8/12/16/24/32 bits, interpolation helpers, and a pole cache for cubic interpolation. Supports up to 16 inputs and 16 outputs.

## Control Flow

Initialization validates dimensions, Domain/Range, sample size, order, bit depth, and sample-table sizes, then optionally allocates `array_step`, `stream_step`, and pole cache arrays. Evaluation clamps/encodes inputs into sample-space coordinates, fetches packed sample values from `DataSource`, interpolates linearly or cubically, decodes/clamps outputs, and returns floats. Cubic evaluation can use a cached tensor of Bezier poles. Monotonicity support maps requested subdomains into sample-index space and tests lattice/tensor monotonicity for shading decomposition. The file also implements parameter writing, scaled-copy creation, parameter freeing, and serialization including sample data.

## Dependencies

Uses `gsfunc0.h`, data source support, function common helpers, Ghostscript parameter lists, floating helpers, and streams.

## Notes

Pole-cache logic is marked as temporary development technology by compile-time flags. Higher-dimensional monotonic tests are limited by small fixed arrays.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.h

## Role

Type definitions and API for FunctionType 0 sampled functions.

## Main Data

Defines `function_type_Sampled` as `0` and `gs_function_Sd_params_t`, containing common function parameters plus order, data source, bits per sample, Encode/Decode arrays, Size array, and internal pole-cache metadata.

## Main API

Declares `gs_function_Sd_init` and `gs_function_Sd_free_params`.

## Dependencies

Includes `gsfunc.h` and `gsdsrc.h`.

## Notes

`BitsPerSample` supports 1, 2, 4, 8, 12, 16, 24, and 32. `Order` is optional and supports 1 or 3 after defaulting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.c

## Role

Implementation of LanguageLevel 3 function types: exponential interpolation, 1-input stitching, and internal arrayed-output functions.

## Main Data

Defines concrete function records for `ElIn`, `1ItSg`, and `AdOt`, helper routines to free and scale arrays of subsidiary functions, and GC descriptors from `gsfunc3.h`.

## Control Flow

Exponential functions clamp input, compute `arg^N`, interpolate between `C0` and `C1`, clamp to Range, and are always monotonic when valid. Stitching functions select a subfunction based on Bounds, encode the input into that subfunction’s domain, and evaluate it; monotonicity delegates to the selected segment when the tested interval does not cross a stitch. Arrayed-output functions evaluate multiple one-output subfunctions and assemble their outputs, handling overlapping input/output buffers for small input counts.

## Dependencies

Uses function common helpers, Ghostscript parameter lists, math wrappers, streams, and subsidiary function APIs.

## Notes

Arrayed-output Domain is computed as the intersection of subfunction domains; comments note this is tailored to shadings and similar dictionaries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.h

## Role

Declarations for LL3 function types.

## Main Data

Defines function type values for exponential interpolation (`2`), 1-input stitching (`3`), and internal arrayed output (`-1`). Declares parameter structs for `gs_function_ElIn_params_t`, `gs_function_1ItSg_params_t`, and `gs_function_AdOt_params_t`.

## Main API

Declares init and free-param functions for each type.

## Dependencies

Includes `gsfunc.h` and `gsdsrc.h`; uses Ghostscript memory and function pointer types.

## Notes

Arrayed-output functions intentionally ignore Domain and Range in their parameter description and are used to combine multiple one-output functions into one multi-output function.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.c

## Role

Implementation of FunctionType 4 PostScript Calculator functions.

## Main Data

Defines `gs_function_PtCr_t`, a calculator stack value type supporting bool/int/float, a maximum stack depth of 100, typed opcode variants, and an opcode dispatch table that maps explicit opcodes plus operand types to executable operations or coercions.

## Control Flow

Initialization validates generic parameters, stack limits, and bytecode structure through the terminating `PtCr_return`. Evaluation seeds the operand stack with inputs, interprets typed bytecode, performs arithmetic/comparison/stack/control operations, enforces stack bounds and type checks, and extracts numeric outputs. Symbolic reconstruction routines pretty-print bytecode as PostScript-like `{ ... }` text through a DataSource hack for PDF embedding. Scaled-copy creation appends multiply/add/roll operations to map outputs into requested ranges.

## Dependencies

Uses math wrappers, data-source support, Ghostscript function common helpers, streams, SubFileDecode filter, and pretty-printer streams.

## Notes

Monotonicity is intentionally unknown and returns a mask marking all dimensions uncertain. Calculator bytecode constants store native `int` and `float` representations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.h

## Role

Public definitions for FunctionType 4 PostScript Calculator functions.

## Main Data

Defines `function_type_PostScript_Calculator` as `4`, the calculator opcode enum, opcode count macros, and `gs_function_PtCr_params_t` with common function parameters plus an opcode byte string.

## Main API

Declares `gs_function_PtCr_init` and `gs_function_PtCr_free_params`.

## Dependencies

Includes `gsfunc.h`.

## Notes

Opcodes include arithmetic, comparison, stack operators, constants, and special control operators `if`, `else`, and `return`. The ops string is represented as `gs_const_string`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfunc4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgc.h

## Role

Library-level interface to Ghostscript garbage-collector VM spaces.

## Main Data

Defines `i_vm_space` with foreign, system, global, and local spaces. Defines `vm_spaces`, containing the GC reclaim procedure and allocator pointers accessible by indexed or named union fields.

## Main API

Defines `GS_RECLAIM` / `gs_reclaim` macros and convenience aliases such as `space_system`, `space_global`, and `spaces_indexed`.

## Dependencies

Forward-declares `gs_ref_memory_t`. Optionally checks that `r_space_bits` is 2 when visible.

## Notes

Foreign space must be index 0 because scalar PostScript refs do not need space bits for foreign/static objects. Higher-numbered VM spaces may point to lower-numbered spaces, but not vice versa.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.c

## Role

Glyph data cache implementation, currently specialized for Type 42 font glyph data read from files.

## Main Data

Defines `gs_glyph_cache_elem` with cached `gs_glyph_data_t`, glyph index, lock count, and list link. Defines `gs_glyph_cache` with total size, list head, stable memory allocator, Type42 font, stream, and read callback.

## Control Flow

`gs_glyph_cache__alloc` allocates cache state in stable memory and registers a font-free notification. `gs_glyph_cache__release` frees all cached glyph data, unregisters notification, and frees the cache. Lookup scans the list for matching glyphs or an unlocked recyclable element. `gs_get_glyph_data_cached` loads missing glyph data through the callback, recycles old unlocked entries after an arbitrary size threshold, moves hits to the head, and returns a locked client `gs_glyph_data_t` view.

## Dependencies

Uses Type42 font internals, glyph data API, stream, font notifications, and Ghostscript GC descriptors.

## Notes

Substring on cached glyph data is unsupported and returns `unregistered`; freeing a client view only decrements the cache element lock count.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.h

## Role

Public declaration for the glyph data cache.

## Main Data

Forward-declares Type42 font, glyph data, stream, and glyph cache types. Defines callback type `get_glyph_data_from_file`.

## Main API

Declares `gs_glyph_cache__alloc`, `gs_glyph_cache__release`, and `gs_get_glyph_data_cached`.

## Dependencies

Relies on Type42 font and stream abstractions.

## Notes

The interface is written for cached access to Type42 glyph outlines, with the cache object stored behind an opaque `gs_glyph_cache` pointer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.c

## Role

Implementation of glyph data ownership, substring, and freeing helpers.

## Main Data

Defines the GC descriptor for `gs_glyph_data_t`, permanent no-free procedures, and font-allocator-backed free/substring procedures.

## Control Flow

`gs_glyph_data_substring` range-checks and dispatches to the current glyph-data procs. `gs_glyph_data_free` dispatches free and resets the object to null. Permanent glyph data simply adjusts pointer/size. Font-owned string data may be memmoved and resized when substringed; object-backed bytes use permanent substring behavior. Constructors initialize glyph data from strings, byte objects, or null and select either no-free or font-backed procs.

## Dependencies

Uses Ghostscript bytestring helpers, font memory, GC descriptors, and error APIs.

## Notes

When initialized with a non-null font, callers transfer ownership of allocated glyph bytes to the glyph data object until `gs_glyph_data_free`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.h

## Role

Client and implementor interface for scalable glyph outline data access.

## Main Data

Defines `gs_glyph_data_t`, containing a constant bytestring, procedure table, procedure data, and memory allocator. Defines `gs_glyph_data_procs_t` with `free` and `substring` hooks.

## Main API

Declares `gs_glyph_data_substring`, `gs_glyph_data_free`, `gs_glyph_data_from_string`, `gs_glyph_data_from_bytes`, and `gs_glyph_data_from_null`.

## Contract

Clients receiving glyph data must call `gs_glyph_data_free` when finished. Implementors pass `NULL` as font for data retained elsewhere and the font pointer for data newly allocated for the client.

## Dependencies

Uses Ghostscript structure descriptors, bytestrings, memory, and font forward declarations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.c

## Role

HSB color operators for the Ghostscript library.

## Main Data

Uses fixed-point `frac` arithmetic for RGB/HSB conversion and clamps HSB input components into `[0,1]`.

## Control Flow

`gs_sethsbcolor` clamps hue/saturation/brightness, converts to RGB, and calls `gs_setrgbcolor`. `gs_currenthsbcolor` reads current RGB and converts back to HSB. Internal conversion follows Rogers’ procedural graphics algorithms: RGB-to-HSB finds max/min channels and hue sector; HSB-to-RGB computes sector and intermediate fixed-point values.

## Dependencies

Uses `gx.h`, `gscolor.h`, `gshsb.h`, and `gxfrac.h`.

## Notes

Hue for gray RGB values is arbitrary and returned as zero. Debug logging is available behind the `c` debug flag.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.h

## Role

Client interface for HSB color routines.

## Main API

Declares `gs_sethsbcolor(gs_state *, floatp, floatp, floatp)` and `gs_currenthsbcolor(const gs_state *, float[3])`.

## Dependencies

Requires Ghostscript graphics state and floating-point typedefs from surrounding includes.

## Notes

The implementation maps HSB through RGB; no independent HSB color space state is stored here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.h -->