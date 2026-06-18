# Group Research: group_1588_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_zfunc3_c_sources_os_d8bb2ea57669

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc3.c

PostScript interface for LanguageLevel 3 FunctionType 2 and FunctionType 3 functions. It plugs into Ghostscript’s shared function-builder path by implementing `gs_build_function_2` and `gs_build_function_3`.

`gs_build_function_2` builds Exponential Interpolation functions. It copies common Domain/Range parameters, reads required `N`, optional/defaulted `C0` and `C1`, checks output vector lengths against each other and against `Range`, then calls `gs_function_ElIn_init`. Failure paths free partially allocated function parameter arrays with `gs_function_ElIn_free_params`.

`gs_build_function_3` builds one-input stitching functions. It reads the `Functions` array, recursively builds each subfunction through `fn_build_sub_function`, requires `Bounds` length `k - 1` and `Encode` length `2 * k`, derives output count from the first subfunction when `Range` is absent, and initializes with `gs_function_1ItSg_init`. It is ownership-sensitive because the function arrays are allocated before validation completes and are released by `gs_function_1ItSg_free_params` on error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc4.c

PostScript/PDF support for FunctionType 4 calculator functions. PDF calculator functions use a restricted PostScript procedure language, and this file validates that subset and compiles it into Ghostscript’s `gs_PtCr_opcode_t` bytecode.

The static `calc_ops` table maps allowed arithmetic, comparison, and stack operator procedures to calculator opcodes. `check_psc_function` walks a procedure completely, accepting integer, real, boolean constants, executable `true`/`false` names, allowed executable operators, and nested procedures only when used as literal operands to `if` or `ifelse`. It enforces a maximum nesting depth of 10 and rejects unbound/unknown names or unsupported operators.

`psc_fixup` patches forward branches for `if` and `else`. `gs_build_function_4` reads the dictionary `Function` procedure, runs the validator once to compute bytecode size, allocates an opcode buffer, runs validation again to emit opcodes, appends `PtCr_return`, and calls `gs_function_PtCr_init`. Failure frees the opcode string through `gs_function_PtCr_free_params`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfunc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfzlib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfzlib.c

Creates zlib and Flate stream filters for the interpreter. It registers `zlibEncode`, `zlibDecode`, `FlateEncode`, and `FlateDecode`.

`filter_zlib` initializes a zlib encoder state from `s_zlibE_template` defaults and optionally reads an `Effort` dictionary parameter in the range `-1..9`. `zzlibE` creates a raw zlib write filter, while `zzlibD` creates the matching read filter. `zFlateE` and `zFlateD` wrap the same zlib templates with predictor-aware helpers, connecting PNG/PDF predictor handling through `ifwpred.h` and `ifrpred.h`.

The file is narrow glue around Ghostscript’s stream filter templates; its main validation surface is the optional compression effort parameter and the generic filter open helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgeneric.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgeneric.c

Generic PostScript operators for arrays, strings, dictionaries, and packed arrays. It implements `copy`, `forall`, `.forceput`, `get`, `getinterval`, `length`, `put`, and `putinterval`, plus continuation operators used by `forall`.

`zcopy` dispatches either to stack copying for integer operands or object copying for composite operands. `copy_interval` performs overlap-aware copying for array/string/packed-array intervals and uses `ref_assign_old` where write barriers are needed. `zget`, `zput`, `zgetinterval`, and `zputinterval` handle type-specific access rules for dictionaries, strings, arrays, and packed arrays, including read/write checks and range checks.

`zforall` schedules iteration on the execution stack. Separate continuations handle arrays, dictionaries, packed arrays, and strings, pushing the next value/key-value pair and re-scheduling the procedure until complete. `forall_cleanup` removes execution-stack state if an iteration aborts. The file is central interpreter collection logic and relies heavily on stack discipline, access attributes, VM-space checks, and packed-array decoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgeneric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgstate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgstate.c

PostScript graphics-state operator layer. It exposes `gsave`, `grestore`, `grestoreall`, `initgraphics`, line parameter controls, dash controls, flatness, fill adjustment, curve/dot tuning, limit clamp, and text rendering mode.

The top of the file provides small adapter helpers for real, boolean, and unsigned integer state setters/getters. `int_gstate_alloc` allocates interpreter graphics state storage and initializes internal references used by the interpreter side of `gs_state`. The save/restore operators delegate to core `gs_state` routines and maintain the interpreter-side `istate` object.

`setdash` validates a dash array, converts numeric elements into a C array, rejects negative entries and all-zero patterns, then calls `gs_setdash`. Current-state operators push numbers, booleans, or arrays back to the operand stack. Non-standard controls such as accurate curves, curve join, dash adaptation, dot length/orientation, fill adjustment, and limit clamp expose Ghostscript-specific graphics controls not present in basic PostScript.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zgstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zhsb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zhsb.c

HSB color operator glue. `currenthsbcolor` calls `gs_currenthsbcolor` and pushes hue, saturation, and brightness. `sethsbcolor` reads three numeric operands, calls `gs_sethsbcolor`, clears the interpreter cached color-space array reference, and pops the operands.

The file registers only `currenthsbcolor` and `sethsbcolor`. It is a thin bridge from PostScript operands to the graphics library’s HSB conversion/state routines.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zhsb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht.c

Basic halftone/screen operators. It implements `currenthalftone`, `currentscreenlevels`, `setscreen`, and internal continuations for sampling a spot function into a halftone order.

`currenthalftone` reconstructs a PostScript dictionary for the current halftone, while `currentscreenlevels` reports the number of gray levels in the current screen. `zscreen_params` extracts `Frequency`, `Angle`, and `SpotFunction` operands into a `gs_screen_halftone`.

`zsetscreen` prepares screen sampling and calls `zscreen_enum_init`, which pushes a screen-enumeration state on the execution stack. `screen_sample` repeatedly calls the PostScript spot function at coordinates supplied by `gs_screen_currentpoint`; `set_screen_continue` feeds sampled values back into the screen enumerator; `setscreen_finish` installs the final halftone; and `screen_cleanup` tears down aborted enumeration. The file is continuation-heavy because screen sampling calls user PostScript code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht1.c

Implements `setcolorscreen`, the four-component color-screen operator. It reads four screen triples from the operand stack, one per indexed color-screen component, storing frequency, angle, and spot procedure refs.

A dummy spot function is installed before actual sampling, because real spot functions are sampled through interpreter continuations. `zsetcolorscreen` builds a `gs_halftone` with `ht_type_multiple_colorscreen`, allocates a matching `gx_device_halftone`, prepares it with `gs_sethalftone_prepare`, then schedules screen sampling for the components through `zscreen_enum_init`.

`setcolorscreen_finish` installs the prepared color halftone after all sampled screens complete. `setcolorscreen_cleanup` frees the prepared halftone/device-halftone allocations on completion or error. The implementation mirrors the single-screen flow in `zht.c` but expands it to four component dictionaries/screens.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.c

LanguageLevel 2 `.sethalftone5` implementation for dictionary-based, multi-component halftones. It supports Type 1 spot, Type 3 threshold, and Type 7 threshold2 component dictionaries inside a Type 5 halftone dictionary.

`zsethalftone5` enumerates the component dictionary, maps colorant names to device component numbers with `gs_cname_to_colorant_number`, ignores unusable components, enforces the component limit, allocates a `gs_halftone`, component array, and `gx_device_halftone`, and fills component parameters. It distinguishes Type 2/4 color-screen semantics by using `ht_type_multiple_colorscreen`; otherwise it uses `ht_type_multiple`.

After `gs_sethalftone_prepare`, it writes `ActualFrequency` and `ActualAngle` back into writable spot-function dictionaries when those keys exist. It then schedules Type 1 spot-function sampling and optional transfer-function remapping on the execution stack. `sethalftone_finish` installs the prepared halftone with `gx_ht_install`, and `sethalftone_cleanup` frees temporary prepared structures.

Helper routines parse spot parameters, threshold common parameters, threshold string/byte storage, threshold2 `Width2`/`Height2`/`BitsPerSample`, and convert Ghostscript separation-name indices back to strings for DeviceN/colorant matching.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.h

Small shared header for Level 2 halftone support. It includes `gscspace.h` for `gs_separation_name` and declares `gs_get_colorname_string`, which converts a separation/colorant name index into string data and length.

The function is implemented in `zht2.c` and is stored in multiple halftone structures so lower-level halftone code can resolve component names without depending directly on interpreter `ref` objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zht2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zicc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zicc.c

LanguageLevel 3 ICCBased color-space operator implementation. It registers `.seticcspace`, which receives the ICCBased dictionary after surrounding PostScript code has selected or implied the alternate color space.

`zseticcspace` reads `/N`, validates `/DataSource` as a readable file stream, rejects unsuitable alternate spaces and nested ICCBased alternate spaces, then reads the optional `Range` array with defaults of `[0 1]` per component. It verifies every range has `min <= max`.

The operator builds a CIEICC color-space object, stores the ICC stream, stream file id, component count, and ranges, copies the current color space as the alternate space, increments its color-space reference count, loads the ICC profile with `gx_load_icc_profile`, prepares CIE caches with `cie_cache_joint`, and finishes installation through `cie_set_finish`. The file is the interpreter bridge between ICC profile streams and Ghostscript’s CIE/ICC color machinery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zicc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage.c

Core image operator implementation for `.image1`, `.imagemask1`, and shared image data feeding. It parses image dictionaries, starts graphics-library image enumerators, and drives those enumerators from procedure, string, or file data sources.

`data_image_params` validates common image dictionary keys: `Width`, `Height`, `ImageMatrix`, `MultipleDataSources`, `BitsPerComponent`, `Decode`, `Interpolate`, and `DataSource`. `pixel_image_params` adds current color-space component count, rejects Pattern color space, sets chunky vs component-planar format, and reads `CombineWithColor`.

`zimage_setup` starts a typed image with `gs_image_begin_typed`, then `zimage_data_setup` allocates a local image enumerator and pushes execution-stack control records. The control records store source refs, aliasing info for repeated file sources, current plane index, plane count, and the enumerator.

There are three continuation paths. Procedure sources call the source procedure for each wanted plane and accept returned strings. File sources buffer and skip stream data, handle EOF and stream exceptions, and account for aliasing when the same file appears multiple times. String sources feed complete strings and may still return for `e_RemapColor` callbacks. `image_cleanup` releases the enumerator. This file is a key state-machine boundary between PostScript execution and incremental image rendering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage2.c

Small helper for Level 2/DPS image extensions that have no explicit source data. It exports `process_non_source_image`, used by other modules such as `zdps.c` and `zdpnext.c`.

The function calls `gs_image_begin_typed` on the supplied image descriptor and current graphics state, but does not allocate interpreter data-source continuations because no data is passed. The source comment notes the `uses_color` argument is currently hard-coded false and marked wrong, so callers depend on the narrow non-source-image use case.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage3.c

LanguageLevel 3 ImageType 3 and ImageType 4 support for masked images. It registers `.image3` and `.image4`.

`zimage3` reads an image dictionary with `InterleaveType`, `DataDict`, and `MaskDict`. It parses the data image with `pixel_image_params`, parses the mask image with `data_image_params`, verifies both nested dictionaries declare `ImageType 1`, and enforces the InterleaveType/DataSource rules: mask data source is required exactly for InterleaveType 3, data multiple sources are only allowed with InterleaveType 3, and mask multiple sources are rejected. For InterleaveType 3 it inserts the mask source before data sources before calling `zimage_setup`.

`zimage4` handles color-key masking. It parses a normal pixel image, reads `MaskColor`, supports either exact component values or component ranges, clamps negative values into unsigned/no-match conventions, and then delegates to `zimage_setup`. Both operators reuse the incremental image engine from `zimage.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev.c

Standard IODevice support and line-edit/statement-edit stream construction. It defines `%lineedit%` and `%statementedit%` device descriptors as special devices and registers `.getiodevice`.

`zgetiodevice` maps an integer IODevice index to its device name string or `null`, returning range errors for invalid indexes. The larger `zfilelineedit` routine is the implementation/continuation for `.filelineedit`: it reads from `%stdin` into a PostScript string buffer, grows the buffer up to `max_string_size`, handles read callouts, EOF, and I/O errors, and returns a string-backed file stream.

For statement editing, it appends an EOL and scans the accumulated buffer to decide whether a complete token/statement has been read; if the scanner needs refill, reading continues. The final stream disables close freeing of the backing string buffer and sets its filename to `%lineedit%` or `%statementedit%`. This file is interpreter-facing terminal input handling rather than OS filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev2.c

LanguageLevel 2 IODevice operators and `%null%` device definition. `%null%` accepts only write access and opens the platform null file through `file_open_stream`.

`.getdevparams` looks up an IODevice by string name, writes its parameters to the operand stack using `stack_param_list_write`, and prefixes the result with a mark. `.putdevparams` reads marked key/value parameters from the stack, checks the `SystemParamsPassword`, calls `gs_putdevparams`, releases parameter-list storage, and removes consumed operands.

The file is the PostScript parameter interface to `gx_io_device` implementations. It relies on the generic `gs_getdevparams`/`gs_putdevparams` hooks exposed by each device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevs.c

Direct stdio-backed `%stdin%`, `%stdout%`, and `%stderr%` IODevice implementation for the PostScript interpreter. It defines special IODevice descriptors using the `Special` dtype.

`stdin_init` marks stdin interactive in the library context. `stdin_open` allocates a file stream over `gs_stdin`, installs a custom process function that reads through `gp_stdin_read`, and returns a cached `ref_stdin` file object. The custom read process reads one character at a time in interactive mode but still uses a larger buffer for filters that need progress.

`stdout_open` and `stderr_open` allocate write streams over `gs_stdout` and `gs_stderr`, each with 128-byte buffers, cached file refs, and close behavior that flushes/closes the underlying file stream. `zget_stdin`, `zget_stdout`, and `zget_stderr` reopen cached standard streams through the IODevice table when necessary; `zis_stdin` recognizes this implementation by its custom process function.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevsc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevsc.c

Alternative `%stdin%`, `%stdout%`, and `%stderr%` IODevice implementation using procedure-stream callouts rather than direct C stdio file streams. It defines the same special devices and public `zget_*` helpers as `ziodevs.c`.

`stdin_open` creates a read procedure stream with literal integer `0` as a marker, allocates a buffer, sets `min_left` to zero, and caches it in `ref_stdin`. `stdout_open` and `stderr_open` create write procedure streams marked by literal integers `1` and `2`. `stdio_close` invokes the saved close/flush procedure, then bumps stream IDs so old file objects become invalid after close.

`zis_stdin` recognizes stdin by checking for a valid reading procedure stream whose procedure marker is literal integer `0`. This variant is used where standard streams are mediated by interpreter callouts instead of direct platform handles.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevsc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevst.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevst.c

`%static%` IODevice implementation for serving embedded initialization/resource data from `gs_init_string`. It defines a GC-managed `iostatic_state` holding a PostScript dictionary of static file metadata.

`iostatic_init` allocates and installs the state object. `iostatic_open_file` expects file names of the form `/category/instance`, looks up that category and instance in the configured dictionary, reads `StaticFilePos` and `StaticFileEnd`, and returns a read stream over the corresponding byte range in `gs_init_string`. Missing or malformed metadata returns `undefinedfilename` or `unregistered` depending on the failure.

`.setup_io_static` installs the dictionary into the `%static%` IODevice state with a write barrier. The GC mark/enumerate/relocate procedures ensure the stored dictionary reference is traced and relocated correctly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodevst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zlib.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zlib.mak

Partial Ghostscript makefile for building or linking zlib. It expects the including make system to define source, generated, object, and zlib-sharing variables such as `GSSRCDIR`, `ZSRCDIR`, `ZGENDIR`, `ZOBJDIR`, `SHARE_ZLIB`, and `ZLIB_NAME`.

The makefile defines zlib source/object path macros, zlib-specific compile flags, clean targets, and generated `.dev` module targets. When `SHARE_ZLIB=1`, encoder/decoder/crc modules are emitted as library dependencies on `ZLIB_NAME`. When `SHARE_ZLIB=0`, it compiles bundled zlib sources and creates `zlibc.dev`, `zlibe_0.dev`, `zlibd_0.dev`, and `crc32_0.dev`.

It covers common code (`zutil`), compression (`adler32`, `deflate`, `compress`, `trees`, `crc32`), and decompression (`inffast`, `inflate`, `inftrees`, `uncompr`, with older zlib 1.1.x source lists retained). The comments document supported zlib versions and warn about older zlib bugs/security issues.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zlib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmath.c

PostScript math and random-number operators. It registers trigonometric/logarithmic functions, square root, exponentiation, and `rand`/`srand`/`rrand`.

Each numeric operator validates real/integer operands through `real_param` or `num_params`, calls the C math library or Ghostscript fixed helpers as appropriate, and writes back integer or real results. Trigonometric functions use PostScript degrees rather than C radians. `atan` handles the two-argument PostScript form and normalizes results.

The random operators expose Ghostscript’s internal random state: `rand` pushes the next pseudo-random integer, `srand` seeds from an integer operand, and `rrand` returns the current seed/state. The file is straightforward operand conversion and range/error mapping around math helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmatrix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmatrix.c

PostScript matrix and coordinate-transform operators. It handles CTM manipulation (`concat`, `initmatrix`, `setmatrix`, `.setdefaultmatrix`) and matrix-valued operations (`currentmatrix`, `defaultmatrix`, `concatmatrix`, `invertmatrix`, `rotate`, `scale`, `translate`).

`read_matrix`/`write_matrix` are used to convert PostScript six-element arrays into `gs_matrix` values and back. `zconcat`, `zsetmatrix`, and `zsetdefaultmatrix` update graphics-state matrices. `zrotate`, `zscale`, and `ztranslate` construct transformation matrices and write them to the supplied matrix operand.

`common_transform` supports `transform`, `dtransform`, `itransform`, and `idtransform`, dispatching either through the graphics state CTM or directly through a matrix operand depending on operand count/type. The file is the interpreter binding for `gsmatrix.h` and `gscoord.h` matrix arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmatrix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmedia2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmedia2.c

LanguageLevel 2 media matching support for `setpagedevice`. It implements `.matchmedia` and `.matchpagesize`, matching requested page/device attributes against an `InputAttributes`-style dictionary and policy dictionary.

`.matchmedia` validates request, attributes, policies, and key array; handles null attribute dictionaries; extracts requested `MediaPosition`, `Orientation`, and `RollFedMedia`; applies `PolicyNotFound`; and scans candidate media dictionaries. Non-`PageSize` keys require object equality. `PageSize` uses `zmatch_page_size`, which supports exact/ranged media arrays, orientation, roll media, and policy-based nearest/next-larger matching.

`match_page_size` uses a tolerance of 5 units, computes mismatch penalties, prefers better size fits and priority ordering, and can generate an adjustment matrix for scaling/rotation. `make_adjustment_matrix` centers, rotates, optionally scales, and translates the page according to the selected medium. The code notes a limitation for variable-size media when the match is not exact.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmedia2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc.c

Miscellaneous interpreter operators. It includes `bind`, environment and OS error helpers, timing, serial number access, operator construction, debug flag updates, and a small path-cache interface.

`zbind` recursively walks procedures/arrays and replaces executable names with executable operators found in dictionaries, preserving packed-array behavior and avoiding rebinding already executable operators. `zmakeoperator` creates an operator object from an index and procedure-like ref. `zserialnumber` compares a password-like operand against the built-in serial number access policy.

`zrealtime` and `zusertime` expose elapsed real/user time; initialization records a baseline. `zgetenv`, `.oserrno`, `.setoserrno`, and `.oserrorstring` bridge to platform environment/error state. `.setdebug` toggles Ghostscript debug characters. `.pcacheinsert` and `.pcachequery` expose a persistent cache API through `gp_cache_*`, with allocation callback support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc1.c

Miscellaneous Type 1 font encryption operators and eexec filters. It registers `.type1encrypt`, `.type1decrypt`, `eexecEncode`, and `eexecDecode`.

`type1crypt` is the shared implementation for `.type1encrypt` and `.type1decrypt`: it takes input string, seed, and output string, checks output capacity, applies the supplied Type 1 crypt routine, updates the seed, and returns the output substring and new seed. `ztype1encrypt` and `ztype1decrypt` select encrypt/decrypt callbacks from `gscrypt1.h`.

`eexec_param` extracts optional `seed` from a parameter dictionary or defaults it. `zexE` and `zexD` create eexec encode/decode filters through the stream filter framework. The file is small but important for Type 1 font program handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc2.c

LanguageLevel management operators. It implements `languagelevel` and `.setlanguagelevel`, including dictionary swapping needed when changing visible language level.

`zlanguagelevel` pushes the current interpreter level. `zsetlanguagelevel` validates the requested level and calls `set_language_level`. The setter updates global level state and swaps entries between `systemdict` and level-specific dictionaries so operators/resources appear or disappear according to the selected level.

`swap_level_dict` and `swap_entry` traverse dictionaries and exchange entries, including nested subdictionaries. The logic must preserve dictionary access and VM-space constraints while mutating system-level operator dictionaries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc3.c

Miscellaneous LanguageLevel 3 operators. It registers `clipsave`, `cliprestore`, and `.eqproc`.

`clipsave` saves clipping state through the graphics state, and `cliprestore` restores it. These are thin wrappers around the clipping save/restore support in `gsclipsr.h`.

`.eqproc` compares two procedure objects structurally. It checks procedure-like operands and delegates to the interpreter’s procedure comparison logic, returning a boolean result. The file is a narrow LL3 extension binding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpacked.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpacked.c

Packed-array operators and packed-array construction. It implements `currentpacking`, `packedarray`, and `setpacking`, plus exported helper `make_packed_array`.

`currentpacking` returns the current global packing flag. `setpacking` stores a new boolean into the packing container with the correct old-reference write barrier. `zpackedarray` validates the requested element count, temporarily removes the count operand, and calls `make_packed_array`.

`make_packed_array` performs a two-pass conversion from stack refs to packed storage. The first pass computes required packed/full-ref storage and checks local-into-global stores. The second pass encodes packable names, small integers, and executable operators into short packed refs, expands runs when a full ref must be aligned, pads with legal packed integer refs for GC scanning, pops source operands, and returns either a `t_shortarray` or `t_mixedarray`. Alignment and GC safety are the main invariants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpacked.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpaint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpaint.c

Painting operator glue. It maps `fill`, `eofill`, and `stroke` directly to `gs_fill`, `gs_eofill`, and `gs_stroke`.

It also exposes non-standard `.fillpage` and `.imagepath`. `.fillpage` fills the current page through `gs_fillpage`. `.imagepath` accepts width, height, and a readable bitmap string, checks that enough data is present for one bit per pixel, and passes the mask data to `gs_imagepath` to append an image-derived path.

The file is intentionally thin; validation is limited to operand types, data length, and graphics-library return codes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpaint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath.c

Basic path construction and clipping operators. It registers `moveto`, `lineto`, `curveto`, relative variants, `closepath`, `newpath`, `currentpoint`, `clip`, `eoclip`, and `initclip`.

`common_to` reads two numeric operands and dispatches to absolute or relative move/line functions. `common_curve` does the same for six curve operands. `currentpoint` calls `gs_currentpoint` and pushes the current coordinates.

The clipping operators call `gs_clip`, `gs_eoclip`, and `gs_initclip`; path construction calls the corresponding `gspath.h` routines. This file is the basic PostScript path-to-graphics-state binding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath1.c

Additional path operators: arcs, arct/arcto, clipping/path conversion, flattening, reverse, stroke-to-path, dashpath, path bounding boxes, and `pathforall`.

`common_arc` parses five numeric operands and dispatches to `gs_arc` or `gs_arcn`. `common_arct` supports both `arct` and `arcto`, returning tangent points for `arcto`. Other single-step operators call `gs_clippath`, `gs_dashpath`, `gs_flattenpath`, `gs_reversepath`, `gs_strokepath`, or `gs_pathbbox`.

`pathforall` uses a graphics-library path enumerator and execution-stack continuation. It stores four procedure operands, enumerates path segments, pushes segment coordinates, and invokes the matching procedure for moveto/lineto/curveto/closepath. `path_cleanup` releases the enumerator if execution aborts. The pathforall implementation is a controlled callback loop into PostScript code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpath1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpcolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpcolor.c

LanguageLevel 2 Pattern color support for tiling patterns. It registers `.buildpattern1`, `.setpatternspace`, and internal pattern-paint continuations.

`zpcolor_init` allocates the pattern cache in system memory and attaches it to the graphics state. `zbuildpattern1` reads a pattern dictionary and matrix, validates `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, `PaintProc`, and optional UID, allocates an `int_pattern` carrying the original dictionary, and creates a pattern instance through `gs_makepattern`.

`zsetpatternspace` installs a Pattern color space, optionally using the current non-Pattern color space as the base space for uncolored patterns, and resets the interpreter’s current pattern object to null.

Pattern rendering is asynchronous. `zPaintProc` requests an `e_RemapColor` callback. `pattern_paint_prepare` creates or delegates pattern accumulation, saves/restores graphics state around the pattern’s saved state, switches to the accumulator or external accumulation path, pushes cleanup state, and schedules the user `PaintProc`. `pattern_paint_finish` adds the rendered tile to the pattern cache and removes PaintProc stack junk. `pattern_paint_cleanup` closes the accumulator, grestores, and notifies devices when external accumulation completes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrelbit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrelbit.c

Relational, boolean, and bitwise PostScript operators. It implements `and`, `or`, `xor`, `not`, `bitshift`, `eq`, `ne`, `lt`, `le`, `gt`, `ge`, `.min`, `.max`, `.identeq`, and `.identne`.

Boolean/bitwise operators dispatch based on operand types, supporting booleans and integers where PostScript allows them. `bitshift` handles positive and negative shifts with range-aware behavior. Relational operators compare numbers numerically and strings lexicographically; `obj_le` provides the shared less/equal ordering helper. `eq`/`ne` delegate to generic object equality, while identity equality uses stricter object identity semantics.

The file is low-level interpreter semantics: most complexity is exact PostScript type compatibility and correct boolean result replacement on the operand stack.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrelbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrop.c

RasterOp and transparency flag operators. It registers current/set forms for raster operation, source transparency, and texture transparency.

`setrasterop` reads an integer in `0..0xff` and calls `gs_setrasterop`. `currentrasterop` pushes the current logical operation. The source/texture transparent setters read booleans and update graphics-state RasterOp transparency flags; current operators push the current booleans.

This is a small PostScript wrapper over `gsrop.h` state. It is relevant to painting/compositing behavior but contains no raster implementation itself.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zshade.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zshade.c

LanguageLevel 3 shading and shading-pattern interface. It implements `currentsmoothness`, `setsmoothness`, `.shfill`, `.buildshading1` through `.buildshading7`, and `.buildshadingpattern`.

`zshfill` validates a non-executable shading structure and calls `gs_shfill`. `zbuildshadingpattern` combines a pattern dictionary, matrix, and shading object into a PatternType 2 pattern instance, using `int_pattern_alloc` for interpreter client data.

`build_shading` is the common dictionary framework. It copies the current non-Pattern color space into allocated shading parameters, reads optional `Background`, `BBox`, and `AntiAlias`, then calls a type-specific builder. `build_shading_function` builds either a single function or an array of functions combined with an Arrayed Output function; it enforces input-count compatibility. Indexed color spaces are rejected when a shading uses a function, matching the PLRM rule.

Type-specific builders cover Function-based, Axial, Radial, Free-form Gouraud triangle mesh, Lattice Gouraud triangle mesh, Coons patch mesh, and Tensor patch mesh shadings. Mesh support accepts array, file, or string `DataSource`, parses bit depths, decode arrays, optional functions, `BitsPerFlag`, and `VerticesPerRow` where relevant. Error paths release allocated functions, decode arrays, background colors, and copied color spaces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zshade.c -->