# Group Research: group_1589_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_zstack_c_sources_os_ccd85a29bc4a

Read all listed files completely. Scope confirmed under `sources/os/plan9/plan9`, which is included by `Docs/research_subset_a.md`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstack.c

## Purpose
Implements Ghostscript operand-stack PostScript operators: stack manipulation, marks, counts, and roll/index behavior.

## Public Surface
- `zpop`, `zexch`, `zdup`, `zindex`, `zroll`, `zcleartomark`.
- Private operators: `zclear_stack`, `zcount`, `zmark`, `zcounttomark`.
- Registered through `zstack_op_defs`.

## Implementation Notes
- Uses `check_op`, `push`, `pop`, `ref_assign_inline`, and `ref_stack_*` helpers.
- `zindex` supports references that may live in older stack blocks via `ref_stack_index`.
- `zroll` has optimized contiguous-stack paths for `mod == 1` and `mod == -1`, plus multi-block fallback using cycle rotation.
- `clear`, `count`, `mark`, `cleartomark`, and `counttomark` delegate to ref-stack primitives.

## Dependencies
Depends on Ghostscript interpreter stack machinery in `istack.h`, refs/storage helpers in `store.h`, allocator headers, and operator registration in `oper.h`.

## Risks and Notes
- `zroll` is stack-boundary-sensitive and manually handles non-contiguous stack blocks.
- Overflow handling uses `o_stack.requested` before returning `e_stackoverflow`.
- Filesystem relevance: none directly; this is interpreter stack infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstring.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstring.c

## Purpose
Implements Ghostscript string-specific operators that are not handled by generic composite operators.

## Public Surface
- `zstring`: allocates a zeroed PostScript string.
- Private operators: `.bytestring`, `.namestring`, `anchorsearch`, `search`, `.stringbreak`, `.stringmatch`.
- Registered through `zstring_op_defs`.

## Implementation Notes
- `.bytestring` allocates raw bytes and returns an array-structure ref.
- `string` allocates with `ialloc_string`, enforces `max_string_size`, and zero-fills.
- `.namestring` exposes the bytes backing a name.
- `anchorsearch` checks prefix match and returns post/match/boolean according to PostScript convention.
- `search` scans for a pattern and returns post/match/pre/boolean.
- `.stringbreak` searches for any byte from a character-set string without C string APIs, so embedded NULs work.
- `.stringmatch` compares strings or names against wildcard-style patterns via `string_match`.

## Dependencies
Uses Ghostscript allocation, names, VM-space attributes, ref attributes, and utility string matching.

## Risks and Notes
- Several operators adjust `value.bytes` and sizes in-place to create substring views.
- `.stringmatch` treats non-string/name objects as matching only a single `*` pattern.
- Filesystem relevance: none directly; this is interpreter string handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zstring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zsysvm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zsysvm.c

## Purpose
Implements non-standard Ghostscript operators for allocating arrays, dictionaries, packed arrays, and strings in explicit VM spaces: local, global, or system.

## Public Surface
Registered operators include:
- `.globalvmarray`, `.globalvmdict`, `.globalvmpackedarray`, `.globalvmstring`.
- `.localvmarray`, `.localvmdict`, `.localvmpackedarray`, `.localvmstring`.
- `.systemvmarray`, `.systemvmdict`, `.systemvmpackedarray`, `.systemvmstring`.
- `.systemvmcheck`.

## Implementation Notes
- `specific_vm_op` temporarily changes `icurrent_space`, calls the normal creation operator, then restores the old space.
- Wrappers reuse existing `zarray`, `zdict`, `zpackedarray`, and `zstring`.
- `.systemvmcheck` returns whether an object lives in `avm_system`.

## Dependencies
Uses Ghostscript interpreter allocation space controls from `ialloc.h` and `ivmspace.h`.

## Risks and Notes
- Correct restoration of allocation space is critical after delegated operator failure or success.
- System VM is outside normal save/restore semantics and should only contain simple or system-VM composite references.
- Filesystem relevance: none directly; VM allocation policy only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zsysvm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztoken.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztoken.c

## Purpose
Implements token-reading operators and scanner continuation support for files, strings, executable token streams, and comment callbacks.

## Public Surface
- `ztoken`: implements `token` for files and strings.
- `ztokenexec`: reads a token from a file and executes/interprets it like the interpreter, with literal procedures preserved.
- `ztokenexec_continue`: exported continuation used by interpreter refill handling.
- `ztoken_handle_comment`: handles `%ProcessComment` and `%ProcessDSCComment` callouts.
- `ztoken_scanner_options`: updates cached scanner option bits from user parameters.
- Registered through `ztoken_op_defs`.

## Implementation Notes
- File tokenization initializes `scanner_state` and uses `scan_token`.
- String tokenization uses `scan_string_token`; on error it restores the operand stack to its original depth.
- Refill handling stores scanner state and continuation on the execution stack.
- `token_continue` temporarily removes the source file from the operand stack while scanning procedures.
- `tokenexec_continue` places scanned executable objects on the execution stack, except procedures are treated as literals.
- Comment handling dynamically looks up `%ProcessComment` or `%ProcessDSCComment`, pushes file/comment operands when available, and schedules continuation.
- Scanner options map `ProcessComment`, `ProcessDSCComment`, `PDFScanRules`, and `PDFScanInvNum`.

## Dependencies
Depends on scanner/token APIs (`iscan.h`, `itoken.h`), streams/files, dictionary lookup, operand and execution stacks, filters, and name lookup.

## Risks and Notes
- Stack cleanup around scanner errors is important because procedure scanning may leave partial operands.
- Continuation memory ownership differs for saved vs reused scanner states.
- Comment callbacks mutate both operand and execution stacks and are sensitive during initialization.
- Filesystem relevance: indirect only; tokenization can read from file streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztoken.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrans.c

## Purpose
Implements PostScript/PDF transparency operators for blend mode, alpha, text knockout, transparency groups, soft masks, ImageType 3x masks, and pdf14 device-filter management.

## Public Surface
Registered in split tables:
- `ztrans1_op_defs`: `.setblendmode`, `.currentblendmode`, `.setopacityalpha`, `.currentopacityalpha`, `.setshapealpha`, `.currentshapealpha`, `.settextknockout`, `.currenttextknockout`.
- `ztrans2_op_defs`: `.begintransparencygroup`, `.discardtransparencygroup`, `.endtransparencygroup`, `.begintransparencymaskgroup`, `.begintransparencymaskimage`, `.discardtransparencymask`, `.endtransparencymask`, `.inittransparencymask`, `.image3x`, `.pushpdf14devicefilter`, `.poppdf14devicefilter`.

## Implementation Notes
- Float getter/setter helpers abstract alpha accessors.
- `enum_param` maps name refs to blend/mask subtype indexes.
- Transparency group setup reads `Isolated`, `Knockout`, current color space, and bounding box coordinates.
- Mask group setup reads subtype, background/gray background, optional transfer function, and bbox.
- `tf_using_function` bridges Ghostscript functions to mask transfer functions.
- `.image3x` reads `DataDict` and optional `ShapeMaskDict`/`OpacityMaskDict`, validates interleave/data-source rules, and inserts mask data sources before image data as needed.
- pdf14 filter push/pop operators delegate to `gs_push_pdf14trans_device` and `gs_pop_pdf14trans_device`.

## Dependencies
Touches graphics state, color spaces, image parameter parsing, dictionaries, functions, transparency graphics library, and pdf14 device support.

## Risks and Notes
- Mask dictionary validation is subtle: interleave type must agree with available data sources.
- Transfer functions must be single-input/single-output functions.
- `.discard*` operators require current transparency layer type checks.
- Filesystem relevance: none directly; rendering/transparency pipeline only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrap.c

## Purpose
Provides minimal trapping-parameter operator support for LanguageLevel 3 trapping features.

## Public Surface
- `.settrapparams`: reads a dictionary and applies it to `i_trap_params`.
- `settrapzone`: registered but not implemented, returns `undefined`.
- Registered through `ztrap_op_defs`.

## Implementation Notes
- Defines global `gs_trap_params_t i_trap_params` with a source comment marking the design as questionable.
- `.settrapparams` wraps a dictionary as a `dict_param_list`, calls `gs_settrapparams`, releases the parameter list, and pops on success.

## Dependencies
Uses dictionary parameter-list parsing and graphics trapping APIs from `gstrap.h`.

## Risks and Notes
- `settrapzone` is explicitly NYI.
- Global trap parameter storage is called out as bogus by the source.
- Filesystem relevance: none.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztype.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztype.c

## Purpose
Implements type inspection, executable/literal conversion, access restriction/check operators, and numeric/string/name conversions.

## Public Surface
- Exported for other interpreter components: `zcvx`, `zreadonly`, `zcvi`, `zcvr`.
- Registered operators: `cvi`, `cvlit`, `cvn`, `cvr`, `cvrs`, `cvs`, `cvx`, `executeonly`, `noaccess`, `rcheck`, `readonly`, `.type`, `.typenames`, `wcheck`, `xcheck`.

## Implementation Notes
- `.type` indexes type-name array by base type; structure refs derive names from registered structure type metadata.
- `.typenames` pushes executable name refs for known ref types and nulls for missing entries.
- `cvlit` clears executable; `cvx` sets executable but rejects internal operators outside the execution stack.
- Access checks use dictionary access refs when needed and apply `ref_save` before mutating dictionary access.
- `noaccess` rejects permanent dictionaries and read-only dictionaries.
- `cvi`/`cvr` accept numbers or strings tokenized by `scan_string_token`.
- `cvrs` supports radix 2..36 with custom integer conversion; radix 10 uses the shared object-to-string path.
- `cvs` uses `obj_cvs` and has a compatibility fallback that truncates selected operator names on rangecheck.

## Dependencies
Uses scanner utilities, dictionary stack checks, names, object conversion helpers, memory/ref root interfaces, and stream/filter headers required by scanner code.

## Risks and Notes
- Access mutation is security-sensitive and must preserve PostScript invalidaccess behavior.
- `cvx` deliberately protects internal operators from executable exposure.
- Real-to-int conversion uses conservative min/max real bounds.
- Filesystem relevance: none directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zupath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zupath.c

## Purpose
Implements LanguageLevel 2 user-path operators and insideness tests for current paths or user paths.

## Public Surface
- Insideness: `ineofill`, `infill`, `instroke`, `inueofill`, `inufill`, `inustroke`.
- User path operations: `uappend`, `ucache`, `ueofill`, `ufill`, `upath`, `ustroke`, `ustrokepath`.
- Exported helper `make_upath`.
- Registered through `zupath_l2_op_defs`.

## Implementation Notes
- Insideness tests create a temporary clipping aperture and install `gs_hit_device` to detect whether painting hits.
- Coordinate tests use a one-pixel fixed rectangle; user-path tests preserve current path while clipping to an appended path.
- `inustroke` handles optional matrix operands and concatenates or returns identity as needed.
- User path opcode arrays support compact two-element form: operands array plus opcode string with repeat encoding.
- Ordinary executable user-path arrays are validated against a whitelist of path operators.
- `make_upath` enumerates a Ghostscript path, allocates an executable array, writes optional `ucache`, `setbbox`, and path construction operators.
- `upath_append` resets the current path, interprets compact or executable path arrays, and updates `current_point`.
- `ustrokepath` preserves and frees path storage carefully while replacing path with stroked outline.

## Dependencies
Depends on path, graphics-state, matrix, painting, fixed-point, dictionary, name, numeric-array, and device/hit-detection APIs.

## Risks and Notes
- User-path parsing executes only recognized operators and enforces exact argument counts.
- Temporary gsave/grestore and path preservation are critical to avoid changing current graphics state during tests.
- Compact user-path operand decoding depends on numeric-array format helpers.
- Filesystem relevance: none; graphics/path subsystem only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zupath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zusparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zusparam.c

## Purpose
Implements Ghostscript user and system parameter operators, including password checks, VM/font/cache limits, scanner option updates, and parameter retrieval.

## Public Surface
- `set_user_params`: exported for context switching.
- Registered operators: `.currentsystemparams`, `.currentuserparams`, `.getsystemparam`, `.getuserparam`, `.setsystemparams`, `.setuserparams`, and Level 2 `.checkpassword`.

## Implementation Notes
- Parameter definitions are described by small structs for long, bool, and string parameters.
- System long params include `BuildTime`, `MaxFontCache`, `CurFontCache`, `Revision`, `MaxGlobalVM`.
- System bool/string params include `ByteOrder` and `RealFormat`.
- User long params include `JobTimeout`, font cache controls, stack maxima, `MaxLocalVM`, `VMReclaim`, `VMThreshold`, `WaitTimeout`, `MinScreenLevels`, `AlignToPixels`, and `GridFitTT`.
- User bool params include `AccurateScreens`, `UseWTS`, and `LockFilePermissions`.
- `.checkpassword` compares supplied password against `StartJobPassword` and `SystemParamsPassword`.
- `.setsystemparams` validates `SystemParamsPassword`, can update start/system passwords subject to `LockFilePermissions`, then applies writable system params.
- `.setuserparams` applies user params and refreshes cached scanner options with `ztoken_scanner_options`.
- `current_param_list` writes matching parameter name/value pairs onto the operand stack; `currentparam1` filters by name and returns one value or `undefined`.

## Dependencies
Uses font directory/cache APIs, GC/VM status APIs, parameter-list readers/writers, dictionaries, token scanner options, stack maxima, halftone/user rendering options, and VM control helpers from `ivmem2.h`.

## Risks and Notes
- `setparams` does not roll back partial changes if a later parameter fails.
- `LockFilePermissions` can only be enabled once; disabling while locked returns `invalidaccess`.
- String/string-array parameter setting is explicitly not implemented.
- Filesystem relevance: indirect only through `LockFilePermissions`, which affects later file permission behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zusparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem.c

## Purpose
Implements PostScript save/restore virtual-memory operators and related VM status/forget-save extension.

## Public Surface
- `zsave`, `zrestore`.
- Private operators: `vmstatus`, `.forgetsave`.
- Registered through `zvmem_op_defs`.

## Implementation Notes
- `vm_save_t` stores the graphics-state save boundary associated with a VM save.
- `zsave` optionally validates memory, allocates a local save record, creates allocator save state, performs `gs_gsave_for_save` and `gs_gsave`, and returns a `t_save` ref.
- `zrestore` validates the save object, checks all operand/execution/dictionary stack refs are older than the target save, fixes stack refs, iteratively restores allocator state, restores graphics state at each save level, refreshes dictionary cache, and temporarily clears `LockFilePermissions`.
- `restore_check_stack` rejects stack refs to objects allocated since the save, with special exceptions for executable/closed e-stack files and empty executable strings.
- `restore_fix_stack` clears `l_new` and canonicalizes newer empty executable strings or closed executable files on the e-stack.
- `vmstatus` reports local save level, used VM, and available allocation accounting.
- `.forgetsave` removes a save without restoring VM, while splicing graphics-state save chains and forgetting allocator state.

## Dependencies
Uses allocator save/restore internals, graphics state save/restore, stacks, files/streams, dictionaries, memory validation, and matrix/graphics-state headers.

## Risks and Notes
- Save/restore is memory-ownership-sensitive; invalid stack references must be detected before allocator rollback.
- Graphics-state restoration and VM restoration are coupled through `vm_save_t`.
- `.forgetsave` is non-standard and manipulates graphics-state save chains directly.
- Filesystem relevance: indirect through file refs on the execution stack during restore validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem2.c

## Purpose
Implements Level 2 local/global VM controls and garbage-collector control hooks.

## Public Surface
- Exported setters: `set_vm_threshold`, `set_vm_reclaim`.
- Registered operators: `.currentglobal`, `.gcheck`, `.setglobal`, and Level 2 `.vmreclaim`.

## Implementation Notes
- `.setglobal` switches allocation between global and local VM.
- `.currentglobal` reports whether current allocation space is not local.
- `gcheck`/`scheck` reports whether an object is not local.
- `set_vm_threshold` clamps threshold values, with `-1` choosing debug-dependent defaults, then applies to global and local spaces.
- `set_vm_reclaim` toggles GC reclamation across system/global/local spaces based on values `-2..0`.
- `.vmreclaim` supports only immediate GC requests by returning `e_VMreclaim` for values 1 or 2.

## Dependencies
Uses Ghostscript dual-memory spaces, VM-space attributes, and interpreter error signaling.

## Risks and Notes
- Operators are registered even for initial Level 1 because initialization needs them.
- `.vmreclaim` does not itself collect; it exits to the interpreter caller.
- Filesystem relevance: none.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/Makefile

## Purpose
Builds vendored zlib 1.2.2 static/shared libraries plus `example` and `minigzip` test programs.

## Public Surface
Targets include `all`, `check`, `test`, `libz.a`, shared library target, `example`, `minigzip`, `install`, `uninstall`, `clean`, `distclean`, `tags`, and `depend`.

## Implementation Notes
- Defaults to `CC=cc`, `CFLAGS=-O`, `LIBS=libz.a`, and shared names `libz.so.1.2.2`, `libz.so.1`, `libz.so`.
- `OBJS` lists core zlib objects: checksums, deflate/inflate, trees, gz I/O, utilities.
- Optional assembler match code uses `match.S` through preprocessing.
- `test` pipes `hello world` through `minigzip` and runs `example`.
- `install` copies headers, libraries, symlinks shared names if present, and installs `zlib.3`.
- `distclean` restores `Makefile` from `Makefile.in` and `zconf.h` from `zconf.in.h`.

## Dependencies
Uses POSIX make tools, shell, `ar`, `ranlib`, optional `ldconfig`, compiler, and zlib source files.

## Risks and Notes
- Byte-identical to `Makefile.in` in this tree.
- Install/uninstall paths default to `/usr/local`.
- Filesystem relevance: build/install script only; not runtime filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/Makefile.in -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/Makefile.in

## Purpose
Template Makefile for zlib builds; in this repository it is byte-identical to the checked-in `Makefile`.

## Public Surface
Same targets as `Makefile`: `all`, `test`, `libz.a`, shared library, test executables, install/uninstall, cleanup, tags, and dependency generation.

## Implementation Notes
- `configure` rewrites variable assignments from this file into `Makefile`.
- Contains default compiler, flags, library names, install directories, object lists, test rules, and dependencies.
- Supports optional assembler match object through `OBJA=match.o`.

## Dependencies
Same as `Makefile`: make, shell, compiler toolchain, archive tools, zlib source files.

## Risks and Notes
- Since this template and `Makefile` are identical before configuration, configuration state is not pre-applied.
- Filesystem relevance: build/install metadata only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/adler32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/adler32.c

## Purpose
Implements zlib’s Adler-32 checksum function.

## Public Surface
- `uLong ZEXPORT adler32(uLong adler, const Bytef *buf, uInt len)`.

## Implementation Notes
- Splits checksum into `s1` and `s2` modulo 65521.
- Returns initial checksum `1L` when `buf == Z_NULL`.
- Processes input in `NMAX` chunks to avoid 32-bit overflow.
- Uses unrolled macros `DO1` through `DO16` for speed.
- Supports `NO_DIVIDE` builds with repeated subtraction instead of `% BASE`.

## Dependencies
Includes `zlib.h` with `ZLIB_INTERNAL`.

## Risks and Notes
- Correct chunk size is tied to overflow math in the source comment.
- Filesystem relevance: none; checksum primitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/adler32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/compress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/compress.c

## Purpose
Provides simple one-shot memory-buffer compression wrappers around the streaming deflate API.

## Public Surface
- `compress2(dest, destLen, source, sourceLen, level)`.
- `compress(dest, destLen, source, sourceLen)`.
- `compressBound(sourceLen)`.

## Implementation Notes
- Initializes a `z_stream` with default allocators, input/output buffers, and requested level.
- Calls `deflateInit`, then `deflate(..., Z_FINISH)`, then `deflateEnd`.
- Converts unfinished `Z_OK` from `deflate` into `Z_BUF_ERROR` when output space is insufficient.
- `compress` delegates to `compress2` with `Z_DEFAULT_COMPRESSION`.
- `compressBound` returns the zlib 1.2.2 bound formula for default deflate settings.

## Dependencies
Depends on public zlib API declarations in `zlib.h` and deflate implementation.

## Risks and Notes
- Caller must provide enough output buffer; no dynamic allocation for destination occurs here.
- `compressBound` must stay in sync with default deflate window/memory settings.
- Filesystem relevance: none.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/configure -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/configure

## Purpose
Portable shell configuration script for zlib compiler flags, shared/static library selection, feature detection, and Makefile generation.

## Public Surface
Command-line options include `--shared`, `--prefix`, `--exec_prefix`, `--libdir`, `--includedir`, and help.

## Implementation Notes
- Extracts zlib version pieces from `zlib.h`.
- Defaults archive tools, install prefixes, shared extension, and static build mode.
- Detects gcc and platform-specific shared-library flags for Linux/GNU, Cygwin/OS2, QNX, HP-UX, Darwin, IRIX, OSF1, SCO, SunOS, AIX, and generic Unix.
- Tests shared-library support by compiling and linking a temporary test.
- Detects `unistd.h` and rewrites `zconf.h` from `zconf.in.h`.
- Probes `vsnprintf`/`snprintf` availability and return-value behavior, adding fallback macros and printing security warnings for unsafe fallbacks.
- Detects `errno.h`, `mmap`, and assembler symbol underscore behavior.
- Cleans temporary test files and rewrites `Makefile` from `Makefile.in` with selected variables.

## Dependencies
Requires POSIX shell, compiler, `sed`, `uname`, optional `nm`, source headers, and writable build directory.

## Risks and Notes
- Uses compile/link probes with generated temporary files in the source directory.
- Falling back to `sprintf`/`vsprintf` is explicitly warned as a string-format security risk.
- Filesystem relevance: build-time file generation and installation configuration only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/configure -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/crc32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/crc32.c

## Purpose
Implements zlib’s CRC-32 checksum calculation, including optional dynamic table generation and optimized word-at-a-time paths.

## Public Surface
- `get_crc_table()`.
- `crc32(crc, buf, len)`.

## Implementation Notes
- Uses polynomial table generation under `DYNAMIC_CRC_TABLE`; otherwise includes generated `crc32.h`.
- Optional `MAKECRCH` mode writes generated CRC tables to `crc32.h`.
- `BYFOUR` enables endian-specific 32-bit processing when a four-byte integer type is available.
- `crc32` initializes with `crc ^ 0xffffffff`, processes bytewise or dispatches to little/big-endian routines, then complements result.
- `crc32_little` and `crc32_big` align input, process 32-byte chunks, then remaining words/bytes.

## Dependencies
Includes `zutil.h`; generated table data is in `crc32.h`.

## Risks and Notes
- Source comments warn `DYNAMIC_CRC_TABLE` is not mutex-protected; callers should initialize before multithreaded use.
- Word-at-a-time paths depend on pointer alignment and endian detection.
- Filesystem relevance: none; checksum primitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/crc32.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/crc32.h

## Purpose
Provides generated static CRC-32 lookup tables for rapid checksum calculation when `DYNAMIC_CRC_TABLE` is not enabled.

## Public Surface
- Defines `local const unsigned long FAR crc_table[TBLS][256]`.

## Implementation Notes
- Contains the base 256-entry CRC table.
- Under `BYFOUR`, includes additional tables for fast big-endian and little-endian word-at-a-time CRC updates.
- The header is generated by `crc32.c` in `MAKECRCH` mode and included directly by `crc32.c`.

## Dependencies
Requires surrounding definitions for `local`, `FAR`, `TBLS`, and optional `BYFOUR` from `crc32.c`.

## Risks and Notes
- This is generated data; manual edits risk desynchronizing from the polynomial generation logic.
- Table shape depends on `TBLS`; `BYFOUR` changes required initializer count.
- Filesystem relevance: none.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.c

## Purpose
Implements zlib 1.2.2 deflate compression: stream initialization, parameter changes, dictionary setup, block generation, sliding-window matching, flushing, trailers, copying, and teardown.

## Public Surface
- `deflateInit_`, `deflateInit2_`.
- `deflateSetDictionary`.
- `deflateReset`.
- `deflatePrime`.
- `deflateParams`.
- `deflateBound`.
- `deflate`.
- `deflateEnd`.
- `deflateCopy`.

## Implementation Notes
- Configuration table maps compression levels to match parameters and compressor functions: stored, fast, or slow.
- `deflateInit2_` validates zlib version/stream size, selects zlib/raw/gzip wrapper from `windowBits`, allocates window, hash chains, hash heads, and pending/literal/distance buffers.
- `deflateSetDictionary` seeds the window and hash chains and updates Adler state unless raw/gzip rules reject it.
- `deflateReset` resets counters, wrapper state, checksum, Huffman tree state, and LZ77 match state.
- `deflateParams` can switch compression level/strategy midstream and flushes if compressor function changes.
- `deflate` writes zlib or gzip headers, drains pending bytes, handles duplicate flush semantics, invokes the selected block compressor, writes empty flush blocks, handles `Z_FULL_FLUSH` history clearing, and emits zlib/gzip trailers on finish.
- `deflateEnd` frees pending buffer, hash heads, previous links, window, and state.
- `deflateCopy` deep-copies a stream state except on 16-bit `MAXSEG_64K`.
- `fill_window` maintains the 2x window, slides the upper half down, adjusts hash chains, reads input, and initializes rolling hash.
- `deflate_stored` emits uncompressed stored blocks for level 0.
- `deflate_fast` performs greedy matching without lazy evaluation.
- `deflate_slow` performs lazy match evaluation for better compression.
- `longest_match` and `longest_match_fast` implement hash-chain match searches with careful lookahead and optimization assumptions.

## Dependencies
Depends on `deflate.h`, zlib utility allocators/memory helpers/checksums, Huffman tree functions from `trees.c`, and optional asm match support.

## Risks and Notes
- Window sliding and hash-chain updates are correctness-critical.
- Wrapper state uses sign changes to prevent duplicate trailers.
- Strategy-specific match suppression affects compression ratio and deterministic output.
- `deflateEnd` returns `Z_DATA_ERROR` if ending while busy.
- Filesystem relevance: none directly; compression library used by Ghostscript streams/builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.h

## Purpose
Defines internal data structures, constants, macros, and tree-function interfaces used by zlib deflate compression.

## Public Surface
Internal-only header, not for applications. Key definitions:
- Compression code constants: `LENGTH_CODES`, `LITERALS`, `L_CODES`, `D_CODES`, `BL_CODES`, `MAX_BITS`.
- Stream statuses: `INIT_STATE`, `BUSY_STATE`, `FINISH_STATE`.
- Types: `ct_data`, `tree_desc`, `Pos`, `IPos`, `deflate_state`.
- Macros: `put_byte`, `MIN_LOOKAHEAD`, `MAX_DIST`, `d_code`, `_tr_tally_lit`, `_tr_tally_dist`.
- Tree-function declarations: `_tr_init`, `_tr_tally`, `_tr_flush_block`, `_tr_align`, `_tr_stored_block`.

## Implementation Notes
- Enables gzip support unless `NO_GZIP` is defined.
- `deflate_state` contains stream backlink, pending output, wrapper state, LZ77 window/hash state, match parameters, Huffman trees, buffers, and bit output state.
- `pending_buf` is shared with literal/distance buffer layout by `deflate.c`.
- Inline tally macros update literal/distance buffers and dynamic tree frequencies unless `DEBUG` is enabled.

## Dependencies
Includes `zutil.h` and assumes tree code provides length/distance code tables.

## Risks and Notes
- State layout is tightly coupled to `deflate.c` and `trees.c`.
- Buffer sizing assumptions are documented and affect compression correctness/performance.
- Filesystem relevance: none.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/deflate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/example.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/example.c

## Purpose
Provides a standalone zlib usage and regression example covering compression, decompression, gzip file I/O, flushing, sync recovery, large streams, dynamic parameter changes, and preset dictionaries.

## Public Surface
Test functions:
- `test_compress`, `test_gzio`, `test_deflate`, `test_inflate`.
- `test_large_deflate`, `test_large_inflate`.
- `test_flush`, `test_sync`.
- `test_dict_deflate`, `test_dict_inflate`.
- `main`.

## Implementation Notes
- Uses repeated `hello` data and a `hello` preset dictionary.
- `CHECK_ERR` exits on non-`Z_OK` return codes.
- `test_gzio` writes/reads `foo.gz` or platform-specific name, exercising `gzopen`, `gzputc`, `gzputs`, `gzprintf`, `gzseek`, `gztell`, `gzgetc`, `gzungetc`, and `gzgets`.
- Small-buffer deflate/inflate tests force one-byte input/output availability.
- Large tests exercise greedy compression, already compressed input, `deflateParams`, and output discard loops.
- Flush/sync tests intentionally corrupt a compressed block, then use `inflateSync`.
- Dictionary tests verify `Z_NEED_DICT`, Adler dictionary ID matching, and `inflateSetDictionary`.
- `main` checks zlib version compatibility, prints compile flags, allocates buffers, runs all tests, and frees memory.

## Dependencies
Uses public `zlib.h`, C stdio/string/stdlib, gzip file APIs, and allocation/free from libc.

## Risks and Notes
- Creates a gzip test file in the current directory.
- Exits process on first failure; not a library component.
- Filesystem relevance: limited to gzip file I/O test coverage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/example.c -->