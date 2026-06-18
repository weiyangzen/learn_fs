# Group Research: group_150_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_zfunc3_c_sources_o_11faa4d9eb22

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc3.c

## Purpose
Builds Ghostscript LanguageLevel 3 FunctionType 2 and FunctionType 3 PostScript functions from dictionaries.

## Key Functions
- `gs_build_function_2()` builds exponential interpolation functions from `N`, optional `C0`, optional `C1`, and inherited Domain/Range parameters.
- `gs_build_function_3()` builds one-input stitching functions from `Functions`, `Bounds`, and `Encode`.

## Important Behavior
- FunctionType 2 defaults `C0` and `C1` to one-element arrays when absent and verifies output dimensions match Range.
- FunctionType 3 recursively builds subfunctions and requires `Bounds` length `k - 1` and `Encode` length `2 * k`.
- Both builders clean up allocated parameter storage on failure.

## Research Notes
Interpreter glue around the Ghostscript function library; no direct filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc4.c

## Purpose
Builds PDF/PostScript FunctionType 4 calculator functions by validating a restricted PostScript procedure and encoding it into Ghostscript calculator bytecode.

## Key Functions
- `check_psc_function()` walks a procedure, validates literals/operators/control forms, and optionally emits opcodes.
- `psc_fixup()` patches branch offsets for `if` and `ifelse`.
- `gs_build_function_4()` validates, allocates, encodes, terminates, and initializes a calculator function.

## Important Behavior
- Accepts only numeric, boolean, procedure constants in control positions, `true`/`false`, and a fixed whitelist of operators.
- Name operands must resolve to executable systemdict operators and match the calculator opcode table.
- Recursion is capped at 10 nested procedures.
- The builder does a sizing pass before allocating the encoded operation string.

## Research Notes
This file is a compiler from a constrained PostScript subset to an internal function VM used by PDF shading/functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfunc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfzlib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfzlib.c

## Purpose
Registers zlib and Flate encode/decode filters for the PostScript interpreter.

## Key Functions
- `filter_zlib()` initializes `stream_zlib_state` and reads optional `Effort`.
- `zzlibE()` and `zzlibD()` create raw `zlibEncode`/`zlibDecode` filters.
- `zFlateE()` and `zFlateD()` create `FlateEncode`/`FlateDecode`, with predictor chaining.

## Important Behavior
- `Effort` is accepted from filter dictionaries in the range `-1..9`.
- Flate filters route through predictor-aware helper paths, unlike raw zlib filters.
- Registers four filter operators in `zfzlib_op_defs`.

## Research Notes
Thin interpreter wrapper over stream templates from Ghostscript’s zlib integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zfzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zgeneric.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zgeneric.c

## Purpose
Implements generic PostScript operators shared by arrays, strings, dictionaries, packed arrays, and byte structures: `copy`, `get`, `put`, `length`, intervals, and `forall`.

## Key Functions
- `zcopy()`, `zcopy_integer()`, and `zcopy_interval()` implement stack, array, string, and dictionary copy dispatch.
- `zlength()`, `zget()`, and `zput()` implement common composite object access.
- `zforceput()` bypasses normal access checks for selected internal use.
- `zgetinterval()` and `zputinterval()` handle subsequence extraction and replacement.
- `zforall()` schedules iteration continuations for arrays, dictionaries, strings, and packed arrays.
- `copy_interval()` performs the shared array/string/packed-array copy logic.

## Important Behavior
- Stack copy has a fast contiguous-stack path and a general multi-block path.
- Dictionary `put` honors superexec bypass and otherwise enforces write permissions.
- Packed arrays are read-only for mutation.
- `forall` uses the execution stack to preserve iteration state and call user procedures.
- Array copies use old-generation-aware ref assignment; strings use `memmove` for aliasing.

## Research Notes
Core interpreter object plumbing; heavily tied to VM, stacks, packed arrays, and dictionary internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zgeneric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zgstate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zgstate.c

## Purpose
Implements PostScript graphics-state allocation and operators for save/restore, line attributes, dash state, curve behavior, fill adjustment, limit clamping, and text rendering mode.

## Key Functions
- `int_gstate_alloc()` allocates and initializes Ghostscript’s interpreter graphics-state extension.
- `zgsave()`, `zgrestore()`, `zgrestoreall()`, and `zinitgraphics()` wrap whole-state operations.
- `zsetlinewidth()`, `zsetlinecap()`, `zsetlinejoin()`, `zsetmiterlimit()`, and current-state variants expose stroke parameters.
- `zsetdash()` and `zcurrentdash()` manage dash patterns.
- Extension operators manage accurate curves, curve joins, fill adjustment, dash adaptation, dot length/orientation, limit clamp, and text rendering mode.
- `gs_istate_alloc()`, `gs_istate_copy()`, and `gs_istate_free()` are client lifecycle callbacks.

## Important Behavior
- `setlinewidth` stores the absolute width to match Adobe behavior.
- Dash arrays are unpacked into temporary floats for validation, while the original array is retained in interpreter state.
- Initial black-generation and undercolor-removal procedures are executable arrays containing `pop 0.0`.
- Remap-color state is allocated in global VM so copied graphics states can live in global VM.

## Research Notes
Central bridge between PostScript operator semantics and Ghostscript graphics-state structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zgstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zhsb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zhsb.c

## Purpose
Implements HSB color operators.

## Key Functions
- `zcurrenthsbcolor()` pushes current hue, saturation, and brightness.
- `zsethsbcolor()` validates three numeric parameters and sets the graphics-state color.

## Important Behavior
- `sethsbcolor` clears the interpreter cached color-space array after setting an HSB color.
- Operators are registered as `currenthsbcolor` and `sethsbcolor`.

## Research Notes
Small color-space operator wrapper around `gshsb.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zhsb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht.c

## Purpose
Implements basic halftone and screen operators, including `.currenthalftone`, `.currentscreenlevels`, and `setscreen`.

## Key Functions
- `zcurrenthalftone()` returns screen, colorscreen, or dictionary halftone state.
- `zcurrentscreenlevels()` exposes the current screen level count.
- `zsetscreen()` initializes a screen order and starts spot-function sampling.
- `zscreen_enum_init()` sets up execution-stack state for sampling screen cells.
- `screen_sample()` and `set_screen_continue()` drive repeated calls to the PostScript spot function.
- `setscreen_finish()` installs the completed screen.

## Important Behavior
- `setscreen` samples each cell of a halftone pattern by calling user PostScript code.
- The screen enumerator is allocated in the same VM space as the supplied procedure.
- Completion stores the sampled procedure for all color components and clears explicit halftone dictionary state.

## Research Notes
Core continuation-driven halftone sampling path shared by other halftone files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht1.c

## Purpose
Implements `setcolorscreen`, the Level 1 color halftone screen operator.

## Key Functions
- `zsetcolorscreen()` parses four screen definitions, prepares a color halftone, and schedules sampling for each component.
- `setcolorscreen_finish()` installs the completed color screen and records component procedures.
- `setcolorscreen_cleanup()` frees temporary halftone structures.

## Important Behavior
- Four component screens are parsed from red, green, blue, and gray frequency/angle/procedure triples.
- Uses a dummy C spot function until the PostScript spot procedures are sampled.
- Component indices are shuffled to match device component order.
- Temporary `gs_halftone` and `gx_device_halftone` allocations are cleaned up after installation.

## Research Notes
Layered on the sampling helper from `zht.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.c

## Purpose
Implements Level 2 `.sethalftone5` support for multi-component halftone dictionaries, including spot, threshold, and threshold2 components.

## Key Functions
- `gs_get_colorname_string()` converts a separation/colorant name index to string data.
- `zsethalftone5()` parses the primary and component halftone dictionaries, prepares device halftones, schedules sampling, and installs the result.
- `sethalftone_finish()` installs the prepared halftone.
- `dict_spot_params()` parses Type 1 spot halftone parameters.
- `dict_spot_results()` writes actual frequency/angle results back to dictionaries.
- `dict_threshold_params()` and `dict_threshold2_params()` parse threshold halftone data.

## Important Behavior
- Counts only component dictionaries matching usable device colorants; ignores unrelated dictionary entries.
- Type 2 and Type 4 halftones are marked as multiple colorscreens so they adapt to the device color space.
- Supports component HalftoneTypes 1, 3, and 7.
- Schedules both spot-function sampling and transfer-function remapping on the execution stack.
- Threshold2 supports string or byte-structure threshold storage and validates size against dimensions and bits per sample.

## Research Notes
This is the most complex halftone interpreter bridge in the group, coordinating dictionaries, colorant names, VM spaces, graphics state, and deferred execution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.h

## Purpose
Declares shared Level 2 halftone support used by `zht2.c`.

## Key Functions
- `gs_get_colorname_string()` maps a `gs_separation_name` to a byte string and length.

## Important Behavior
- Includes `gscspace.h` for `gs_separation_name`.
- Guarded by `zht2_INCLUDED`.

## Research Notes
Small cross-file declaration for colorant-name lookup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zht2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zicc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zicc.c

## Purpose
Implements the LanguageLevel 3 `.seticcspace` operator for ICCBased color spaces.

## Key Functions
- `zseticcspace()` validates an ICC color-space dictionary, creates a `CIEICC` color space, loads the profile, caches CIE conversion data, and installs the space.

## Important Behavior
- Requires dictionary key `N` and readable `DataSource` file.
- The current color space becomes the ICC alternate space and must be allowed as an alternate.
- Rejects an ICCBased current alternate to avoid nested ICC spaces.
- Optional `Range` is validated for monotonic min/max pairs and stored in ICC info.
- Uses stream read/write IDs as the profile file identifier.

## Research Notes
File/stream use is for ICC profile data sources, not OS filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zicc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage.c

## Purpose
Implements Level 1/2 image and imagemask operator setup plus common image data-source processing.

## Key Functions
- `data_image_params()` parses common image dictionary fields and DataSource operands.
- `pixel_image_params()` adds current color-space handling and pixel-image options.
- `zimage_setup()` starts a typed image and delegates source handling.
- `image1_setup()`, `zimage1()`, and `zimagemask1()` create standard image and mask image paths.
- `zimage_data_setup()` stores data sources and initializes an image enumerator.
- `image_proc_process()` / `image_proc_continue()` handle procedure data sources.
- `image_file_continue()` handles file data sources and stream read exceptions.
- `image_string_continue()` handles string data sources.
- `image_cleanup()` releases image enumerators.

## Important Behavior
- Supports procedure, string, and Level 2 file data sources, with all sources required to be the same type.
- Tracks identical file-source aliasing so shared stream buffers are consumed correctly.
- Procedure sources support `e_RemapColor` callbacks and resume through execution-stack continuations.
- Image enumerators are allocated in local memory to avoid global/local VM ownership problems.
- Empty images clean up immediately and pop operands.

## Research Notes
Critical image interpreter machinery coordinating PostScript data sources, streams, VM, graphics state, and image rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage2.c

## Purpose
Provides a helper for processing image descriptions that have no explicit source data.

## Key Functions
- `process_non_source_image()` starts a typed image with `gs_image_begin_typed()` and returns the result.

## Important Behavior
- Intended for use by DPS-related code.
- Does not allocate or clean up data-source state because no data is supplied.
- Contains an inline comment noting the hard-coded `uses_color` argument is questionable.

## Research Notes
Small shared helper, not an operator table itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage3.c

## Purpose
Implements LanguageLevel 3 masked image operators `.image3` and `.image4`.

## Key Functions
- `zimage3()` parses ImageType 3 data/mask dictionaries and interleave rules.
- `zimage4()` parses ImageType 4 color-key mask data.
- Both route completed image structures through `zimage_setup()`.

## Important Behavior
- ImageType 3 requires `DataDict`, `MaskDict`, and `InterleaveType` 1..3.
- `MaskDict` DataSource presence must match `InterleaveType == 3`.
- Multiple data sources are only allowed for ImageType 3 when interleaved type 3 is used.
- ImageType 4 accepts `MaskColor` as component values or component ranges and clamps impossible matches.

## Research Notes
Extends the common image machinery in `zimage.c` for LL3 masked-image forms.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zimage3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev.c

## Purpose
Implements standard IODevice support and the `%lineedit%` / `%statementedit%` line-buffering helper.

## Key Functions
- `zgetiodevice()` returns IODevice names by numeric index.
- `zfilelineedit()` reads from stdin, builds an editable line or statement string, and returns a string-backed file stream.

## Important Behavior
- `%lineedit%` and `%statementedit%` are declared as special devices but actual opening is handled by interpreter code.
- `zfilelineedit()` grows a PostScript string buffer up to `max_string_size`.
- Statement mode scans tokens and continues reading until a complete statement is present.
- Handles stdin callouts via `s_handle_read_exception()`.
- Returned streams read from the completed line buffer and disable normal close freeing.

## Research Notes
This is interpreter-side IODevice/file-stream glue, relevant to file abstractions but not Plan 9 VFS internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev2.c

## Purpose
Implements Level 2 IODevice parameter operators and the `%null%` device.

## Key Functions
- `null_open()` opens the platform null file for write-only access.
- `zgetdevparams()` serializes IODevice parameters onto the operand stack.
- `zputdevparams()` reads stack parameters, verifies the system-params password, and applies IODevice parameters.

## Important Behavior
- `%null%` accepts only write access.
- Device lookup uses `gs_findiodevice()` on a string operand.
- `.putdevparams` requires `SystemParamsPassword` validation before changing device parameters.
- Parameter lists are managed with stack-param helper APIs.

## Research Notes
IODevice configuration interface for PostScript Level 2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevs.c

## Purpose
Implements `%stdin%`, `%stdout%`, and `%stderr%` IODevices using direct C stdio/file streams.

## Key Functions
- `stdin_init()` marks stdin as interactive by default.
- `stdin_open()`, `stdout_open()`, and `stderr_open()` create or reopen standard streams.
- `s_stdin_read_process()` fills stdin buffers through `gp_stdin_read()`.
- `zget_stdin()`, `zget_stdout()`, and `zget_stderr()` expose standard streams to other interpreter code.
- `zis_stdin()` identifies stdin streams.

## Important Behavior
- Standard files may be closed and reopened, receiving new stream IDs.
- Stdin has a custom read process that reads one character at a time when interactive.
- Streams and buffers are allocated in system memory.
- IODevice state is temporarily used to carry the current interpreter context during open.

## Research Notes
Direct host-stdio implementation of Ghostscript standard IODevices.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevsc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevsc.c

## Purpose
Alternative implementation of `%stdin%`, `%stdout%`, and `%stderr%` IODevices using procedure-backed streams and callouts.

## Key Functions
- `stdio_close()` closes and invalidates standard stream IDs.
- `stdin_open()`, `stdout_open()`, and `stderr_open()` create proc streams tagged by integer procedure refs.
- `zget_stdin()`, `zget_stdout()`, and `zget_stderr()` retrieve or create the streams.
- `zis_stdin()` recognizes the special stdin proc stream.

## Important Behavior
- Literal integer refs identify standard streams: `0` stdin, `1` stdout, `2` stderr.
- Allocates buffers manually when the proc stream has none.
- Stdin proc stream sets `min_left` to zero.
- Closing increments IDs to block stale file object access.

## Research Notes
Designed for environments where stdio is mediated through interpreter callouts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevsc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevst.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevst.c

## Purpose
Implements the `%static%` IODevice for opening embedded static resources from `gs_init_string`.

## Key Functions
- `iostatic_init()` allocates IODevice state containing the static-resource dictionary.
- `iostatic_open_file()` resolves `%static%/category/instance` paths to offsets and returns a string-backed stream.
- `zsetup_io_static()` installs the resource dictionary into `%static%` device state.

## Important Behavior
- `%static%` paths must begin with `/category/instance`.
- Category and instance names are bounded by a local 30-byte buffer.
- Expects resource dictionaries to contain integer `StaticFilePos` and `StaticFileEnd`.
- Device state is GC-scannable because it stores a PostScript `ref`.

## Research Notes
Provides embedded-resource file access for startup/static resources, not host filesystem access.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodevst.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zlib.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zlib.mak

## Purpose
Partial makefile for compiling or linking zlib as part of Ghostscript.

## Key Targets
- `zlibc.dev` builds common zlib support from `zutil`.
- `zlibe.dev` selects shared or compiled encode/compression support.
- `zlibd.dev` selects shared or compiled decode/decompression support.
- `crc32.dev` handles crc32 as its own module because libpng needs it.

## Important Behavior
- Controlled by `SHARE_ZLIB`: `1` links against `ZLIB_NAME`, `0` compiles bundled zlib sources.
- Documents expected zlib source version 1.2.1 and warns about older zlib issues.
- Uses generated `.dev` module descriptions with `SETMOD` and `ADDMOD`.
- Compiles `crc32.c` with warnings disabled because of 32-bit constants under `-Wtraditional`.

## Research Notes
Build-system integration only; no runtime interpreter code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zlib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmath.c

## Purpose
Implements mathematical PostScript operators and the interpreter random-number generator.

## Key Functions
- `zsqrt()`, `zarccos()`, `zarcsin()`, `zatan()`, `zcos()`, `zsin()`, `zexp()`, `zln()`, and `zlog()` implement numeric functions.
- `zrand()`, `zsrand()`, and `zrrand()` implement Adobe-compatible random state operations.

## Important Behavior
- Public operator functions are also used by FunctionType 4 calculator support.
- Trig functions use degrees for PostScript semantics.
- `exp` rejects `0 0 exp` and negative bases with non-integer exponents.
- Random generation uses the Park-Miller `16807 mod (2^31 - 1)` algorithm.
- Random state is stored in interpreter context so context switching can preserve it.

## Research Notes
Pure arithmetic interpreter support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmatrix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmatrix.c

## Purpose
Implements PostScript matrix and coordinate transformation operators.

## Key Functions
- `zinitmatrix()`, `zdefaultmatrix()`, `zcurrentmatrix()`, `zsetmatrix()`, and `zsetdefaultmatrix()` expose CTM/default matrix operations.
- `ztranslate()`, `zscale()`, and `zrotate()` operate either on the graphics state or produce a matrix when a matrix operand is supplied.
- `zconcat()`, `zconcatmatrix()`, and `zinvertmatrix()` perform matrix composition/inversion.
- `ztransform()`, `zdtransform()`, `zitransform()`, and `zidtransform()` share `common_transform()`.

## Important Behavior
- Transform operators optimize the common no-matrix case.
- Matrix-producing forms overwrite operands to match PostScript stack results.
- `common_transform()` accepts normal arrays and packed arrays as possible matrix operands.
- Default matrix can be reset with `null`.

## Research Notes
Bridge from PostScript matrix syntax to Ghostscript `gsmatrix` and coordinate APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmatrix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmedia2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmedia2.c

## Purpose
Implements Level 2 media matching helpers for `setpagedevice`, including `.matchmedia` and `.matchpagesize`.

## Key Functions
- `zmatchmedia()` selects a medium from input attributes based on requested attributes, policies, priority, orientation, and media position.
- `zmatchpagesize()` exposes page-size matching directly.
- `zmatch_page_size()` converts PostScript arrays to geometric values.
- `match_page_size()` matches requested size against fixed or ranged media.
- `make_adjustment_matrix()` computes rotation, scaling, and centering adjustment matrices.

## Important Behavior
- Null input attributes short-circuit to `null true`.
- PageSize matching tolerates differences within 5 units and can rotate dimensions.
- Policy values control exact, nearest, next-larger, scaling, and forced-request behavior.
- Media-position mismatch adds a small penalty.
- Priority arrays break ties among otherwise matching media.

## Research Notes
Page-device/media selection logic, not file or storage logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmedia2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc.c

## Purpose
Implements miscellaneous interpreter operators: `bind`, serial/time queries, environment lookup, dynamic operator creation, OS error helpers, debug flags, and optional persistent-cache debug hooks.

## Key Functions
- `zbind()` recursively binds executable names in procedures to operator refs.
- `zserialnumber()`, `zrealtime()`, and `zusertime()` expose serial and timing values.
- `zgetenv()` reads host environment variables.
- `zmakeoperator()` creates operator-array entries from names and procedures.
- `zoserrno()`, `zsetoserrno()`, and `zoserrorstring()` expose host errno state.
- `zsetdebug()` toggles Ghostscript debug channels.

## Important Behavior
- `bind` handles arrays, packed arrays, and op arrays, making nested executable arrays read-only.
- Packed executable names can be replaced with packed executable-operator tags.
- `realtime` is initialized relative to process startup for FTS compatibility.
- Dynamic operator tables account for restore removing table entries without resetting counts.
- Persistent-cache operators are compiled only under `DEBUG_CACHE`.

## Research Notes
Mixed interpreter/runtime utility surface with some host OS interaction through platform wrappers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc1.c

## Purpose
Implements Type 1 font encryption/decryption helpers and eexec filters.

## Key Functions
- `ztype1encrypt()` and `ztype1decrypt()` call shared `type1crypt()`.
- `type1crypt()` encrypts/decrypts a source string into a target string and returns the updated state.
- `eexec_param()` parses eexec seed operands.
- `zexE()` creates `eexecEncode`.
- `zexD()` creates `eexecDecode`.

## Important Behavior
- Type 1 crypt state is range-checked against truncation to `crypt_state`.
- Output string must be at least as large as input.
- eexec decode supports dictionary parameters `seed`, `lenIV`, and `eexec`.
- If decoding a PFB stream, the filter captures PFB state and can avoid binary-to-hex roundtripping.

## Research Notes
Font/filter-specific interpreter glue around stream templates and Type 1 crypto helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc2.c

## Purpose
Implements language-level query/change operators and the internal dictionary swapping needed to move between PostScript levels.

## Key Functions
- `zlanguagelevel()` returns current language level.
- `zsetlanguagelevel()` validates and switches language level.
- `set_language_level()` coordinates transitions among levels 1, 2, and 3.
- `swap_level_dict()` swaps level-specific dictionaries with systemdict entries.
- `swap_entry()` exchanges individual dictionary entries.

## Important Behavior
- Level-setting operators are available even in Level 1 mode.
- Level 1 hides globaldict by replacing its dictionary-stack slot with systemdict.
- Entering Level 2 enables dictionary auto-expansion; returning to Level 1 disables it.
- Level 3 availability depends on `ll3dict` being present.
- Name caches for globaldict entries are invalidated when dropping to Level 1.

## Research Notes
Interpreter mode-management code with careful VM-space bypasses for system dictionaries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc3.c

## Purpose
Implements miscellaneous LanguageLevel 3 operators: clip save/restore and procedure equality testing.

## Key Functions
- `zclipsave()` and `zcliprestore()` wrap graphics-state clipping save/restore.
- `zeqproc()` compares two procedures recursively to depth 10.

## Important Behavior
- `.eqproc` requires array/procedure operands and descends only when both nested arrays have equal sizes.
- Executable attributes intentionally do not need to match, matching Adobe behavior used for idiom recognition.
- Names and strings are not considered equal even if their object comparison would otherwise pass.

## Research Notes
Small LL3 support file used by clipping and `bind` idiom recognition behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpacked.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpacked.c

## Purpose
Implements PostScript packed-array operators and the packed-array construction routine.

## Key Functions
- `zcurrentpacking()` returns current array-packing mode.
- `zpackedarray()` builds a packed array from stack operands.
- `zsetpacking()` changes packing mode.
- `make_packed_array()` packs names, small integers, and executable operators into compact storage.

## Important Behavior
- `packedarray` validates count against operand-stack depth and pops source elements on success.
- Packing checks local-into-global store constraints.
- Mixed arrays use full refs for un-packable elements while preserving packed refs around them.
- Alignment padding uses legal packed refs so the garbage collector can scan storage.
- Result arrays are read-only and created as shortarray or mixedarray depending on contents.

## Research Notes
Low-level memory/representation code for compact PostScript procedure storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpacked.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpaint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpaint.c

## Purpose
Implements basic painting operators and small nonstandard painting helpers.

## Key Functions
- `zfill()`, `zeofill()`, and `zstroke()` wrap standard path painting.
- `zfillpage()` fills the entire page.
- `zimagepath()` converts bitmap data into a path.

## Important Behavior
- `.imagepath` validates integer width/height and readable string data.
- Bitmap data length must cover `ceil(width / 8) * height`.
- Painting itself is delegated to Ghostscript graphics APIs.

## Research Notes
Thin painting operator layer over `gspaint.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpaint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath.c

## Purpose
Implements basic PostScript path construction and clipping operators.

## Key Functions
- `znewpath()`, `zcurrentpoint()`, `zmoveto()`, `zrmoveto()`, `zlineto()`, and `zrlineto()` manage simple path segments.
- `zcurveto()` and `zrcurveto()` add Bezier segments.
- `zclosepath()`, `zinitclip()`, `zclip()`, and `zeoclip()` handle path closure and clipping.
- `common_to()` and `common_curve()` parse numeric operands and dispatch to graphics APIs.

## Important Behavior
- Numeric path operands are parsed as doubles and passed to graphics state path APIs.
- Successful path construction pops consumed operands.
- `currentpoint` pushes two reals.

## Research Notes
Core interpreter path API glue.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath1.c

## Purpose
Implements additional PostScript Level 1 path operators: arcs, arcto, path transformations, path bounding boxes, and `pathforall`.

## Key Functions
- `zarc()`, `zarcn()`, `zarct()`, and `zarcto()` implement circular/tangent path operations.
- `zdashpath()`, `zflattenpath()`, `zreversepath()`, `zstrokepath()`, and `zclippath()` transform or replace paths.
- `zpathbbox()` computes path bounding boxes.
- `zpathforall()` enumerates path elements through four user procedures.
- `path_continue()` drives path enumeration on the execution stack.
- `path_cleanup()` releases the path enumerator.

## Important Behavior
- `arcto` returns tangent points while `arct` consumes operands and returns no points.
- `pathforall` pushes a mark, four procedures, and an enumerator, then schedules continuations.
- Path enumeration checks operand-stack capacity before fetching the next path element.
- Curve elements push three points before invoking the curve procedure.

## Research Notes
Continuation-driven path iteration mirrors other interpreter `forall`-style operators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpcolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpcolor.c

## Purpose
Implements Level 2 Pattern color-space support, tiling pattern construction, pattern cache initialization, and deferred pattern painting.

## Key Functions
- `zpcolor_init()` creates the graphics-state pattern cache.
- `int_pattern_alloc()` creates interpreter pattern client data.
- `zbuildpattern1()` builds tiling pattern instances from pattern dictionaries and matrices.
- `zsetpatternspace()` installs Pattern color spaces with optional base color space.
- `zPaintProc()` triggers deferred PaintProc execution through `e_RemapColor`.
- `pattern_paint_prepare()`, `pattern_paint_finish()`, and `pattern_paint_cleanup()` manage rendering a pattern tile and caching it.

## Important Behavior
- `zbuildpattern1` validates `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, `PaintProc`, and optional UID.
- Uncolored Pattern space captures the current non-pattern color space as its base.
- Pattern painting saves/restores graphics state and may use an internal accumulator device or device-managed accumulation.
- PaintProc stack leftovers are cleaned up after rendering.
- Pattern cache entries are added after successful tile rendering.

## Research Notes
Complex rendering callback path bridging PostScript PaintProc execution to Ghostscript pattern caching.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zpcolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zrelbit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zrelbit.c

## Purpose
Implements relational, boolean, and bitwise PostScript operators.

## Key Functions
- `zeq()`, `zne()`, `zge()`, `zgt()`, `zle()`, and `zlt()` implement equality and ordering.
- `zmax()` and `zmin()` implement nonstandard extrema operators.
- `zand()`, `znot()`, `zor()`, `zxor()`, and `zbitshift()` implement boolean/integer bit operations.
- `zidenteq()` and `zidentne()` test object identity.
- `obj_le()` compares numeric or string operands.

## Important Behavior
- String comparisons require read access.
- Ordering supports numbers and strings only.
- Boolean operators require both operands to be boolean; integer operators require both operands to be integer.
- Oversized bit shifts yield zero.
- Several functions are public so FunctionType 4 calculator support can reuse them.

## Research Notes
Core scalar operator implementation used both directly by PostScript and internally by calculator functions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zrelbit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zrop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zrop.c

## Purpose
Implements RasterOp and transparency control operators.

## Key Functions
- `zsetrasterop()` and `zcurrentrasterop()` set/query the current 8-bit raster operation.
- `zsetsourcetransparent()` and `zcurrentsourcetransparent()` set/query source transparency.
- `zsettexturetransparent()` and `zcurrenttexturetransparent()` set/query texture transparency.

## Important Behavior
- RasterOp is validated as an integer up to `0xff`.
- Transparency operators require boolean operands.
- All state changes are delegated to `gsrop` graphics-state APIs.

## Research Notes
Small extension surface for raster operation state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zrop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zshade.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zshade.c

## Purpose
Implements LanguageLevel 3 shading operators, shading dictionary builders for ShadingTypes 1 through 7, and shading-pattern construction.

## Key Functions
- `zcurrentsmoothness()` and `zsetsmoothness()` expose smoothness state.
- `zshfill()` fills with an already built shading object.
- `zbuildshadingpattern()` builds PatternType 2 shading patterns.
- `build_shading()` collects common shading parameters and delegates type-specific construction.
- `build_shading_function()` builds single functions or array-composed functions.
- `build_shading_1()` through `build_shading_7()` build function-based, axial, radial, triangle mesh, lattice mesh, Coons patch, and tensor patch shadings.
- `build_directional_shading()` parses shared axial/radial parameters.
- `build_mesh_shading()` parses mesh data sources, decode arrays, and optional functions.
- `flag_bits_param()` parses mesh flag bits where relevant.

## Important Behavior
- Shading color space is copied from the current graphics color space; Pattern space is rejected.
- Optional `Background`, `BBox`, and `AntiAlias` are common to all shading types.
- Indexed color spaces are rejected when a shading has a `Function`, matching PLRM/Adobe behavior.
- Mesh data sources may be arrays of floats, files, or strings.
- Stream/string mesh data requires `BitsPerCoordinate`, `BitsPerComponent`, and `Decode`; free-form, Coons, and tensor meshes also require `BitsPerFlag`.
- On failure, allocated functions, decode arrays, backgrounds, and color spaces are released.

## Research Notes
Large LL3 rendering front end that converts PostScript shading dictionaries into Ghostscript shading structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/zshade.c -->