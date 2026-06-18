# Group Research: group_1580_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_openvms_mak_sources_51905e7b2802

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/openvms.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/openvms.mak

Legacy Ghostscript makefile for OpenVMS VAX and Alpha builds.

It defines OpenVMS-specific build directories, runtime library paths, compiler/linker command syntax, DEC C flags, X11 include handling, bundled third-party library locations, device lists, language features, file I/O choices, and generated header rules. It includes Ghostscript core make fragments such as `gs.mak`, `lib.mak`, `int.mak`, JPEG, zlib, libpng, JBIG2, ICC, device, and contrib makefiles.

Important behavior:

- Sets default runtime paths such as `GS_DOCDIR`, `GS_LIB_DEFAULT`, and `GS_INIT`.
- Configures OpenVMS compiler/linker commands including `/DECC`, `/PREFIX=ALL`, shortened names, include syntax, `.obj`/`.exe` suffixes, and DCL command helpers.
- Selects many display, printer, image, TIFF, PNG, JPEG, and PDF/PS output devices.
- Builds helper programs such as `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Generates OpenVMS command and option files, including DECwindows shared library references.
- Generates `gconfig_.h` and `gconfigv.h` through `echogs`.

This file is build infrastructure for the bundled Ghostscript command tree. It has no filesystem implementation logic beyond build-time directory creation and generated-file rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/openvms.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/oper.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/oper.h

Ghostscript interpreter header for PostScript operator definitions and common operator checks.

It includes operand stack, operator declaration, operator definition, error, check, and utility headers. The file documents the operator procedure contract: operators receive an `i_ctx_t *` and return `0`, a negative Ghostscript error code, or one of several positive interpreter-control codes.

Key contents:

- Declares `check_type_failed(const ref *)`, used to convert failed type checks on operand-stack guard entries into `stackunderflow`.
- Defines macros for type/access checking: `check_type`, `check_stype`, `check_array`, `check_type_access`, `check_read_type`, and `check_write_type`.
- Defines `return_op_typecheck` and `NYI`.
- Defines special positive return values `o_push_estack`, `o_pop_estack`, and `o_reschedule`.

The file is central to interpreter operator implementation discipline. It is not filesystem-related.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/oper.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/opextern.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/opextern.h

Header declaring PostScript operator procedures that are referenced outside their defining translation units and are present in all Ghostscript interpreter configurations.

It groups exported `z*` and `zop_*` procedures by use:

- Special operator encoding in `interp.c`: arithmetic, stack, conditional, and dictionary primitives such as `zadd`, `zdef`, `zdup`, `zexch`, `zif`, `zifelse`, `zindex`, `zpop`, `zroll`, and `zsub`.
- Internal entry points: `zop_add`, `zop_def`, and `zop_sub`.
- Server loop, save/restore, graphics state, pagedevice, wrapper, specific-VM, user path, FunctionType 4, CIE cache, and miscellaneous support operators.
- Customer/special-use exports such as `zcurrentdevice`, `ztoken`, `ztokenexec`, and `zwrite`.

This is a cross-module interpreter declaration file, not OS or filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/opextern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/os2.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/os2.mak

Legacy Ghostscript makefile for MS-DOS or OS/2 builds using GCC/EMX or IBM C++.

It configures build directories, installation roots, runtime search paths, compiler/linker options, DLL vs EXE mode, X11 optional support, bundled JPEG/PNG/zlib/JBIG2/ICC paths, device lists, feature lists, auxiliary tools, OS/2 Presentation Manager targets, resources, icons, and packaging.

Important behavior:

- Defaults to `MAKEDLL=1`, `EMX=1`, and `USE_LARGE_COLOR_INDEX=1`.
- Configures compiler flags for GCC/EMX or IBM C++, optional debug symbols, DLL flags, CPU/FPU options, and OS/2-specific defines.
- Selects Ghostscript features such as PostScript level 3, PDF, DPS, TrueType, EPSF, and `os2print`.
- Includes generic Ghostscript build fragments plus `pcwin.mak` for Windows/OS2 device rules.
- Builds platform modules including `gp_os2`, `gp_stdia`, and OS/2 printer I/O.
- Builds auxiliary tools through EMX bind steps or IBM C++ commands.
- Supports OS/2 PM driver resources/icons and a `zip` packaging target.

This is build/platform integration for Ghostscript’s OS/2 target. It does not implement filesystem behavior, though it references OS/2 printer I/O and packaging filesystem paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/os2.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ostack.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ostack.h

Ghostscript operand stack helper header.

It maps the current interpreter context’s operand stack into short names and defines stack manipulation macros:

- `iop_stack`, `o_stack`, `osbot`, `osp`, and `ostop`.
- `check_ostack(n)` for overflow preflight.
- `push(n)` for pushing and updating `osp`.
- `pop(n)` for decrementing `osp`.
- `check_op(nargs)` for explicit stack-underflow checks.

The comments describe Ghostscript’s operand stack guard-entry scheme: the interpreter does not precheck underflow for every operator, so invalid guard refs below the stack bottom let type checks later report `stackunderflow`. It also notes that the operand stack is a linked list of blocks, so whole-stack operations must account for block boundaries.

This is interpreter stack infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ostack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/pcwin.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/pcwin.mak

Partial Ghostscript makefile for PC window-system-specific device drivers shared by MS Windows and OS/2 builds.

It isolates devices needing special platform compilation switches:

- Deprecated MS Windows 3.x DLL display device objects: `gdevmswn`, `gdevmsxf`, `gdevwdib`, plus color mapping helpers.
- MS Windows DDB and DIB printer device targets: `mswinprn.dev` and `mswinpr2.dev`.
- OS/2 Presentation Manager devices: `os2pm.dev` and `os2dll.dev`.
- OS/2 printer device: `os2prn.dev`.

It defines per-object dependencies and uses `GLCCWIN` or `GLCC` as appropriate.

This is device build wiring for Ghostscript, not runtime filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/pcwin.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/pipe_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/pipe_.h

Small portability wrapper for `popen` and `pclose`.

Behavior:

- Includes `stdio_.h`.
- On `__WIN32__`, maps `popen` to Ghostscript’s `mswin_popen`, because old MSVC `_popen` implementations are noted as broken for Ghostscript’s needs. `pclose` maps to `_pclose`.
- On non-Windows platforms, declares `popen` without a prototype argument list due to inconsistent system headers, and declares `pclose(FILE *)`.

This is portability support for process pipes. It is adjacent to OS integration but contains no filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/pipe_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/plan9-aux.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/plan9-aux.mak

Auxiliary makefile for Ghostscript’s Unix-style platform and helper-program rules, adapted in this Plan 9 source tree.

Although the internal identifier is `unix-aux.mak`, this file appears as `plan9-aux.mak` in the Plan 9 Ghostscript source directory. It defines:

- `unix_.dev` and `sysv_.dev` platform modules from `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, optional cache code, and `nosync`.
- Build rules for platform support objects such as `gp_unix`, `gp_unix_cache`, `gp_stdia`, and `gp_sysv`.
- Auxiliary program build rules for `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- `gconfig_.h` generation by probing headers under `INCLUDE=/sys/include/ape`, including `dirent.h`, `sys/time.h`, `sys/times.h`, and JPEG memory-system availability.

This is build support for Ghostscript in a Unix/APE-like environment. It touches filesystem paths only to test for headers and generate build artifacts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/plan9-aux.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/png_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/png_.h

Minimal wrapper for including libpng headers.

If `SHARE_LIBPNG` is true, it includes system `<png.h>`; otherwise it includes the bundled `"png.h"`. This lets the Ghostscript build switch between external and bundled libpng.

No filesystem logic is present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/png_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.c

Implementation of Ghostscript’s `ASCII85Decode` stream filter.

Core behavior:

- Defines `s_A85D_init`, which delegates to the inline initializer from `sa85d.h`.
- Implements `s_A85D_process`, reading ASCII85 input digits and writing decoded binary bytes.
- Handles ordinary base-85 groups, the `z` shorthand for four zero bytes, whitespace via `scan_char_decoder`, and end marker `~>`.
- Allows CR/LF between `~` and `>` for Adobe Acrobat compatibility, while treating other intervening characters as errors.
- Checks for 32-bit overflow in final group assembly.
- Supports partial final groups through `a85d_finish`.
- Emits stream statuses `0`, `1`, `EOFC`, or `ERRC` using Ghostscript stream conventions.
- Exposes `s_A85D_template` with min input/output sizes `2` and `4`.

This is byte-stream decoding code. It has no filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.h

Interface and state definition for Ghostscript’s `ASCII85Decode` filter.

It defines `stream_A85D_state` with common stream state plus:

- `odd`: count of accumulated partial ASCII85 digits.
- `word`: accumulated base-85 word.

It also declares:

- GC descriptor macro `private_st_A85D_state`.
- Inline initializer `s_A85D_init_inline`, which sets `min_left`, clears `word`, and resets `odd`.
- External stream template `s_A85D_template`.

This header belongs to Ghostscript stream filtering, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85d.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85x.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85x.h

Interface header for ASCII85 stream filters, adding `ASCII85Encode` state on top of `sa85d.h`.

It defines `stream_A85E_state` with common stream state plus:

- `count`: number of emitted digits since the last line break.
- `last_char`: last written character.

It declares the GC descriptor macro `private_st_A85E_state`, inline initializer `s_A85E_init_inline`, and external `s_A85E_template`.

The actual encode implementation is elsewhere. This is stream filter interface code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sa85x.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.c

Arcfour stream cipher implementation used by Ghostscript filters.

The file implements an RC4-compatible symmetric byte stream, described as based on Schneier’s presentation and functionally equivalent to RC4 as referenced by PDF.

Important routines:

- `s_arcfour_set_key` initializes the 256-byte S-box from a supplied key and rejects empty keys.
- `s_arcfour_process` generates keystream bytes, XORs them with input, and preserves the `x`/`y` indices and S-box between calls.
- `s_arcfour_process_buffer` applies the same transform in-place to a buffer using stream cursors.
- `s_arcfour_template` exposes the filter with byte-sized input/output units.

The same operation encrypts and decrypts. This is cryptographic stream-filter code for document/PDF handling, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.h

Header for the Arcfour stream cipher filter.

It defines `stream_arcfour_state` with common stream state, two permutation indices `x` and `y`, and the 256-byte S-box. It declares:

- `s_arcfour_set_key`.
- GC descriptor macro `private_st_arcfour_state`.
- External `s_arcfour_template`.
- `s_arcfour_process_buffer` for in-place buffer transformation.

This is a Ghostscript/PDF stream cipher interface, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sarc4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.c

Implementation of Ghostscript BCP and TBCP stream filters.

The encode side escapes selected control characters by writing `CtrlA` and XORing the character with `0x40`. Two escape tables distinguish BCP from TBCP; TBCP additionally escapes ESC.

The decode side tracks escape state and handles protocol control characters:

- `CtrlA`: starts an escaped control byte.
- `CtrlC`: calls the client `signal_interrupt` callback.
- `CtrlD`: signals end of data unless escaped.
- `CtrlT`: calls the client `request_status` callback.
- `CtrlE`, `CtrlQ`, `CtrlS`, and `Ctrl-\`: ignored protocol controls.
- TBCP-specific escaped `[` and `M` handling.

It defines stream templates for `BCPEncode`, `TBCPEncode`, `BCPDecode`, and `TBCPDecode`.

This is printer/job transport encoding support for Ghostscript streams. It is not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.h

Interface for BCP and TBCP stream filters.

It declares encode templates `s_BCPE_template` and `s_TBCPE_template`. For decode, it defines `stream_BCPD_state` with:

- Client callbacks `signal_interrupt` and `request_status`.
- Dynamic state fields `escaped`, `matched`, `copy_count`, and `copy_ptr`.

It declares `private_st_BCPD_state`, `s_BCPD_template`, and `s_TBCPD_template`.

This is Ghostscript stream protocol state, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.c

Implementation of bounded Huffman encode/decode stream filters.

The bounded Huffman filters extend generic Huffman coding with optional zero-run encoding and an optional end-of-data marker.

Important encode behavior:

- `s_BHCE_init` allocates an encoding table from the provided Huffman definition and calls `hc_make_encoding`.
- `s_BHCE_process` encodes byte values, accumulates runs of zero when configured, emits run-length symbols, and optionally emits an EOD code at finalization.
- `s_BHCE_release` frees the allocated encoding table.

Important decode behavior:

- `s_BHCD_init` allocates a decoding table sized by `hc_sizeof_decoding` and calls `hc_make_decoding`.
- `s_BHCD_process` decodes variable-length codes, expands zero runs, and recognizes the configured EOD code.
- Some comments flag incomplete or questionable paths, including “WRONG” allocation comments and a not-yet-implemented partial-code case.

The stream templates are `s_BHCE_template` and `s_BHCD_template`.

This is compression filter code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.h

Header for bounded Huffman stream filters.

It defines shared state containing generic Huffman state, an `hc_definition`, client-set `EndOfData` and `EncodeZeroRuns`, and dynamic `zeros` count. It defines:

- `max_zero_run`.
- `stream_BHCE_state` with an encode table.
- `stream_BHCD_state` with a decode table.
- GC descriptor macros for both states.
- Inline initialization macros `s_bhce_init_inline` and `s_bhcd_init_inline`.
- Decode state load/store macros for bit-reader state plus zero-run state.

This is compression-stream infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbhc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbtx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbtx.h

Header for ByteTranslate encode/decode filters.

It defines `stream_BT_state`, used for both encode and decode, with common stream state and a 256-byte translation table. It declares the GC descriptor macro and external templates `s_BTE_template` and `s_BTD_template`.

The implementation is elsewhere. This is a simple byte-mapping filter interface, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.c

Implementation of Burrows-Wheeler block-sorting compression filters.

The file first defines common buffered-block stream support:

- `s_buffered_set_defaults`, `s_buffered_no_block_init`, and `s_buffered_block_init`.
- `s_buffered_process`, which fills a block buffer from stream input.
- `s_buffered_release`.

For `BWBlockSortEncode`:

- Allocates a block buffer and rotation index array.
- Reverses the input block before encoding so the decoder emits the original order.
- Sorts rotations using an initial radix pass and `qsort` with `bwbs_compare_rotations`.
- Writes the block length `N` and primary index `I` as big-endian `int` values.
- Emits the Burrows-Wheeler transformed last-column bytes.

For `BWBlockSortDecode`:

- Reads `N` and `I`, validates them, fills the encoded block, and constructs inverse mapping tables.
- Uses `SHORT_OFFSETS` by default, storing inverse-order data in 64K, 4K, and 12-bit packed tiers to save memory.
- Iterates from index `I` through the inverse transform to reconstruct output bytes.

Risk notes: the encoder uses a static `bwbs_compare_ss` to pass state to `qsort`, so the sort comparison is not reentrant. Several allocation comments are marked “WRONG” in the legacy source.

This is compression transform code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.h

Header for BWBlockSort Burrows-Wheeler filters and their block-buffering base state.

It defines `stream_buffered_state_common` with:

- Client-set `BlockSize`.
- Allocated `buffer`.
- Dynamic `filling`, `bsize`, and `bpos`.

It defines `stream_BWBS_state` with inherited buffered state, an `offsets` pointer, current block length `N`, primary index `I`, and current decode index `i`. It aliases this for encode and decode states and declares `s_BWBSE_template` and `s_BWBSD_template`.

This is compression stream state, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sbwbs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scanchar.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scanchar.h

Header defining Ghostscript token-scanner character classification.

It declares `scan_char_array`, biased by `max_stream_exception`, and `scan_char_decoder`, which maps byte values and stream exceptions to scanner categories.

Categories include:

- Numeric digit values `0` through `max_radix - 1`.
- `ctype_name`.
- `ctype_btoken`.
- `ctype_space`.
- `ctype_other`.
- `ctype_exception`.

It also defines special control character constants such as `char_NULL`, `char_EOT`, `char_VT`, `char_DOS_EOF`, and portable `char_CR`/`char_EOL` handling for OS-9 newline peculiarities.

This supports PostScript/PDF lexical scanning, not filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scanchar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scantab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scantab.c

Definition of the scanner character-class table declared by `scanchar.h`.

The table maps stream exceptions and all 256 byte values to Ghostscript scanner categories:

- Whitespace for NUL, tab, LF, FF, CR, and space.
- `ctype_other` for token delimiters such as `%`, parentheses, slash, angle brackets, brackets, and braces.
- Numeric digit values for `0-9`, `A-Z`, and `a-z` where applicable.
- `ctype_btoken` for bytes 128-159.
- `ctype_name` for most remaining bytes, including high bytes 160-255.

This table is used for fast token scanning in PostScript/PDF parsing. It is not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scantab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scf.h

Shared definitions for Ghostscript CCITTFax encoding and decoding filters.

It documents the CCITT Group 3 and Group 4 run-length Huffman scheme and declares the encoding and decoding tables used by the encoder/decoder.

Major contents:

- Maximum safe line width calculation `cfe_max_width` and output-code byte sizing macro.
- Encoding table types and extern declarations for white/black run tables, EOL, uncompressed, 2-D pass/vertical/horizontal, and Group 3 2-D EOL codes.
- Decode node type aliases and negative exceptional values: `run_error`, `run_zeros`, `run_uncompressed`, `run2_pass`, and `run2_horizontal`.
- Initial/minimum decode bit counts for white, black, 2-D, and uncompressed decoding tables.
- Optimized pixel-run detection macros `skip_white_pixels` and `skip_black_pixels`, using byte-run tables and handling `BlackIs1`.

This is image compression support for CCITT fax filters, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfd.c

Implementation of Ghostscript’s `CCITTFaxDecode` stream filter.

Core behavior:

- Initializes raster size, line buffers, optional previous-line buffer for 2-D modes, row counters, EOL counters, bit-reader state, and polarity.
- Copies completed decoded rows from internal line buffers to the caller.
- Handles Group 3/4 EOL detection, RTC/EOFB end conditions, optional byte alignment, mixed 1-D/2-D `K` handling, row limits, and damage-skipping scaffolding.
- Implements `cf_decode_1d` for white/black Huffman run decoding and scan-line bit filling.
- Implements `cf_decode_2d` for pass, vertical, and horizontal coding against a previous reference line.
- Uses generated decode tables from `scfdtab.c` and run-scan macros from `scf.h`.
- Keeps intermediate state so decoding can suspend and resume across input/output buffer boundaries.
- `cf_decode_uncompressed` currently returns `ERRC`; an alternative untested implementation is compiled out.

Risk notes: some source comments mark incomplete or questionable areas, including damaged row substitution and uncompressed mode handling. Allocation-failure comments are legacy “WRONG” markers but the code does return stream errors.

This is CCITT fax image decompression, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdgen.c

Generator program for `scfdtab.c`, the CCITTFax decode lookup tables.

The program opens `scfdtab.c` for writing and emits:

- Header/license comments.
- Includes for `std.h`, `scommon.h`, and `scf.h`.
- `cf_white_decode`, `cf_black_decode`, `cf_2d_decode`, and `cf_uncompressed_decode` tables.
- A dummy function for compilers requiring executable code.

The generator builds first-level and second-level decode trees by enumerating the encode tables from `scfetab.c`/`scf.h`:

- White and black termination/makeup codes.
- 1-D uncompressed and EOL-related codes.
- 2-D pass, horizontal, vertical, uncompressed, and EOL-related codes.
- Uncompressed mode and exit codes.

It uses `malloc` for second-level nodes while generating output.

This is build-time table generation for CCITT fax decoding, not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdtab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdtab.c

Generated static lookup tables for the `CCITTFaxDecode` filter.

The file contains four `const cfd_node` arrays:

- `cf_white_decode`.
- `cf_black_decode`.
- `cf_2d_decode`.
- `cf_uncompressed_decode`.

Each entry stores a decoded run/exception value and code length. Positive values are run lengths or table offsets depending on context; negative values use the exceptional codes defined in `scf.h`, such as run errors, EOL/zero runs, uncompressed mode, pass mode, and horizontal mode.

The file also includes `scfdtab_dummy` to satisfy compilers that require executable code in each translation unit.

This is generated compression-table data, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfdtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfe.c

Implementation of Ghostscript’s `CCITTFaxEncode` stream filter.

Core behavior:

- Initializes raster size, input line buffer, encoded output buffer, optional previous-line buffer, and 1-D/2-D scheduling state.
- Buffers raw raster rows from the caller, pads/terminates each row with polarity changes for run detection, then emits encoded line data.
- Supports pure 1-D (`K == 0`), pure 2-D (`K < 0`), and mixed Group 3 1-D/2-D (`K > 0`) modes.
- Handles optional EOL emission, encoded byte alignment, and end-of-block EOL sequence generation.
- `cf_encode_1d` emits white/black run codes using CCITT Huffman tables.
- `cf_encode_2d` selects pass, vertical, or horizontal mode by comparing the current line against the previous reference line.
- `cf_put_long_run` emits makeup codes for long runs before termination codes.

Debug builds can count and print white/black run-code usage. This is CCITT fax image compression, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfetab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfetab.c

Static encoding tables for Ghostscript’s `CCITTFaxEncode` filter, also used by `scfdgen.c` to generate decode tables.

It defines:

- EOL code `cf_run_eol`.
- 1-D uncompressed marker `cf1_run_uncompressed`.
- 2-D pass, vertical, horizontal, and uncompressed codes.
- Group 3 2-D EOL codes distinguishing 1-D and 2-D rows.
- White run termination and makeup tables.
- Black run termination and makeup tables.
- Uncompressed run and exit code tables.
- Dummy `scfetab_dummy`.

This file is table data for CCITT fax image compression. It is not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfetab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfparam.c

Parameter read/write support for CCITTFax filters.

It defines the parameter table for shared CCITT fax stream state, including:

- `Uncompressed`, `K`, `EndOfLine`, `EncodedByteAlign`, `Columns`, `Rows`, `EndOfBlock`, `BlackIs1`, `DamagedRowsBeforeError`, `FirstBitLowOrder`, and `DecodedByteAlign`.

Important routines:

- `s_CF_get_params` writes all or non-default parameter values.
- `s_CF_put_params` reads parameters into a copy, validates ranges, and commits on success.

Validation includes limits for `K`, `Columns`, `Rows`, damaged-row tolerance, and `DecodedByteAlign`, with `DecodedByteAlign` required to be a power of two between 1 and 16.

This is image-filter parameter plumbing, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfx.h

State definitions for Ghostscript CCITTFax encode/decode filters.

It defines common CCITT fax state fields:

- Client parameters such as `Uncompressed`, `K`, `EndOfLine`, `EncodedByteAlign`, `Columns`, `Rows`, `EndOfBlock`, `BlackIs1`, `DamagedRowsBeforeError`, `FirstBitLowOrder`, and `DecodedByteAlign`.
- Derived state such as `raster`, current line buffer `lbuf`, previous line buffer `lprev`, and mixed-mode `k_left`.

It defines encoder state `stream_CFE_state` with max output sizing, encoded-line buffer, and read/write counters.

It defines decoder state `stream_CFD_state` with bit/row positions, EOL counts, current polarity, 2-D run-color state, damaged-row tracking, and uncompressed-mode placeholders.

The header declares GC descriptor macros and templates `s_CFE_template` and `s_CFD_template`.

This is compression filter state, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scommon.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scommon.h

Common Ghostscript stream infrastructure definitions shared by stream clients and implementors.

It forward-declares `stream`, `stream_state`, and `stream_template`, then defines:

- Stream exceptional return codes: `EOFC`, `ERRC`, `INTC`, `CALLC`, and `max_stream_exception`.
- Read/write cursor structures used by stream processing procedures.
- Procedure signature macros for init, process, release, defaults, reinit, report-error, and parameter get/put functions.
- Generic `stream_state_common`, including template pointer, memory allocator, error reporter, `min_left`, and fixed-size error string.
- Base `stream_state` and GC descriptor declaration.

The file documents Ghostscript’s byte-oriented stream model and sticky exceptional conditions.

This is core stream framework code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/scommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.c

Shared DCT/JPEG filter parameter handling for Ghostscript’s `DCTEncode` and `DCTDecode`.

Major responsibilities:

- Defines common DCT scalar parameters `ColorTransform` and `QFactor`, plus IJG wrapper flags `Picky` and `Relax`.
- Converts Adobe zigzag-order quantization parameters to IJG natural order for newer JPEG library versions, and back when reporting parameters.
- Reads/writes quantization tables as strings or float arrays under `QuantTables`.
- Packs and writes Huffman tables under `HuffTables`.
- Reads byte-sized parameters from strings or float arrays through `s_DCT_byte_params`.
- Validates common scalar ranges, including `Picky`, `Relax`, `ColorTransform`, and `QFactor`.
- Deduplicates identical quantization and Huffman tables and assigns component table indexes.
- Allocates IJG quantization/Huffman tables through Ghostscript JPEG allocation helpers.

Risk notes: several comments note incomplete deallocation on intermediate errors and a “byte_array IS WRONG” legacy concern. The code assumes valid IJG table pointers in some get paths.

This is JPEG/DCT stream parameter plumbing, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.h

Internal header for DCT filter parameter helpers implemented in `sdcparam.c`.

It declares routines for:

- Common DCT parameter get/put.
- Quantization table get/put.
- Huffman table get/put.
- Byte-sized parameter extraction from strings or arrays.

The comments state these are internal helpers used by `sddparam.c` and `sdeparam.c`, not public API.

This is DCT/JPEG stream parameter interface code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdct.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdct.h

Header defining Ghostscript DCT/JPEG stream filter state.

Major contents:

- `jpeg_block_t`, used to track immovable allocations made for IJG JPEG library data.
- Common JPEG stream data containing a copied stream template, IJG error manager, `jmp_buf`, allocator, allocation block list, and `Picky`/`Relax` flags.
- `jpeg_compress_data`, wrapping `jpeg_compress_struct`, destination manager, and final-output buffer.
- `jpeg_decompress_data`, wrapping `jpeg_decompress_struct`, source manager, skip state, fake-EOI state, optional scanline buffer, and scanline byte count.
- `stream_DCT_state`, the GC-managed Ghostscript stream state containing marker data, `QFactor`, `ColorTransform`, `NoMarker`, JPEG memory, compress/decompress data pointer, scanline size, and processing phase.
- Public GC descriptor macros and declarations for `s_DCTD_template`, `s_DCTE_template`, and `s_DCT_set_defaults`.

This is JPEG/DCT stream state infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctc.c

Small common implementation file for DCT encode/decode streams.

It defines the public GC descriptor for `stream_DCT_state` and implements `s_DCT_set_defaults`.

Defaults set:

- `jpeg_memory` to Ghostscript’s non-GC library memory.
- `data.common` to null.
- `ColorTransform` to `-1` meaning unspecified.
- `QFactor` to `1.0`.
- `Markers` to an empty string.

This is shared DCT/JPEG filter initialization support, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctd.c

Implementation of Ghostscript’s `DCTDecode` JPEG stream filter.

Core behavior:

- Installs IJG source-manager callbacks for initialization, buffer refill, skipping input data, resync, and termination.
- `dctd_fill_input_buffer` suspends when more input is needed, or injects a fake EOI marker at final input EOF.
- `dctd_skip_input_data` tracks skipped bytes across caller buffers.
- `s_DCTD_process` runs a phase machine:
  - Skip leading garbage before the JPEG marker.
  - Read JPEG headers.
  - Apply `ColorTransform` if supplied and not overridden by an Adobe marker.
  - Start decompression.
  - Allocate an oversized scanline buffer if output scanlines exceed template output size.
  - Read scanlines into caller output or the intermediate buffer.
  - Finish decompression and return `EOFC`.
- `s_DCTD_release` destroys JPEG state, frees scanline buffer and decompression data, and restores the stream template pointer.

This is JPEG decompression stream code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcte.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcte.c

Implementation of Ghostscript’s `DCTEncode` JPEG stream filter.

Core behavior:

- Defines IJG destination-manager callbacks; `empty_output_buffer` returns false to suspend when output is full.
- Defaults include empty markers and `NoMarker=true`.
- `s_DCTE_process` runs a phase machine:
  - Start JPEG compression.
  - Write supplied custom marker bytes.
  - Optionally write a manual Adobe APP14 marker carrying `ColorTransform`.
  - Feed scanlines from input to IJG compression.
  - Finish compression into a fixed internal buffer.
  - Copy final bytes to caller output and return `EOFC`.
- It validates premature input EOF during scanline consumption.
- `s_DCTE_release` destroys JPEG state, frees compression data, and restores the template pointer.

This is JPEG compression stream code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcte.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sddparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sddparam.c

Parameter get/put support for `DCTDecode`.

It provides:

- `s_DCTD_get_params`, which writes common DCT parameters. The code has an `NYI` comment and uses a default state for comparison.
- `s_DCTD_put_params`, which reads common DCT parameters and then accepts `HuffTables` and `QuantTables` for JPEG streams that omit those tables.

This file delegates most work to shared helpers in `sdcparam.c`.

It is JPEG/DCT filter parameter code, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sddparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdeparam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdeparam.c

Parameter get/put support for `DCTEncode`.

It defines encode-specific scalar parameters:

- `Columns`, `Rows`, `Colors`, `Marker`, `NoMarker`, `Resync`, and `Blend`.

Get path:

- Reports common DCT parameters, encode scalars, horizontal/vertical sampling factors, quantization tables, and Huffman tables.
- Builds a temporary default compression state when only non-default values are requested.
- Notes unresolved `NYI`/`Blend` handling in comments.

Put path:

- Requires valid image dimensions and component count; rejects two-component JPEG and invalid ranges.
- Reads common DCT parameters, initializes IJG defaults, optional Huffman and quantization tables, and applies `QFactor` when no explicit quant tables are supplied.
- Selects IJG color spaces and Adobe marker `ColorTransform` behavior for grayscale, RGB, and CMYK/YCCK.
- Reads `HSamples` and `VSamples`, validates factors 1 through 4, disables JFIF/Adobe automatic markers, sets restart interval, and enforces sample-count limits unless `Relax` is enabled.

This is JPEG encoder parameter handling, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdeparam.c -->