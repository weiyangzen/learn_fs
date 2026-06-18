# Group Research: group_142_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_openvms_mak_source_7b90aee6b388

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/openvms.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/openvms.mak

OpenVMS platform makefile for the Ghostscript tree. It configures VAX/Alpha OpenVMS builds, output/source/object directories, runtime search paths, third-party library source locations, compiler/linker commands, selected devices/features, and generated build metadata.

The makefile includes the generic Ghostscript make fragments (`gs.mak`, `lib.mak`, `int.mak`, `jpeg.mak`, `zlib.mak`, `libpng.mak`, `jbig2.mak`, `icclib.mak`, `devs.mak`, `contrib.mak`) and adapts their variables to OpenVMS syntax. It builds helper programs such as `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`, creates `openvms.com`/`openvms.opt`, and emits `gconfig_.h`/`gconfigv.h`.

Dependencies are OpenVMS DCL commands, DEC C, OpenVMS linker option files, DECwindows/X11 libraries, bundled JPEG/libpng/zlib/jbig2/icclib sources, and Ghostscript platform files such as `gp_vms.c` and `gp_stdia.c`.

Filesystem relevance is indirect. This is userland build orchestration for a vendored Ghostscript copy in 9front, not Plan 9 filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/openvms.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/oper.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/oper.h

Central Ghostscript interpreter operator header. It defines the operator procedure convention, pulls in operand stack, operator definition, external operator declaration, operand checking, and utility headers, and supplies common checking macros used by `z*` operator implementations.

The key logic is type-check error handling: bottom operand-stack guard slots use invalid refs, so failed type checks call `check_type_failed` to distinguish `typecheck` from `stackunderflow`. The header also defines access/type check macros and positive operator return codes for execution-stack push/pop and Display PostScript rescheduling.

Dependencies include `ierrors.h`, `ostack.h`, `opdef.h`, `opextern.h`, `opcheck.h`, `iutil.h`, and the interpreter context model.

This file is core Ghostscript interpreter infrastructure and has no direct filesystem role.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/oper.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/opextern.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/opextern.h

Declares Ghostscript PostScript operator procedures that are intentionally referenced outside their defining source files and are available in all interpreter configurations.

The declarations cover fast/special operators used by `interp.c`, server-loop operators, save/restore hooks, Level 2 graphics state/page device helpers, VM-specific constructors, path construction operators, FunctionType 4 arithmetic/math/relational operators, CIE cache support, and miscellaneous shared operator entry points such as `ztoken`, `zwrite`, and `zclosefile`.

Dependencies are the interpreter context type `i_ctx_t` and `ref`, normally provided before or through surrounding operator headers.

This is cross-module interpreter API glue, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/opextern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/os2.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/os2.mak

OS/2 and MS-DOS GCC/EMX or IBM C++ Ghostscript makefile. It sets directory layout, install paths, compiler mode, DLL/executable selection, X11 option, third-party library locations, large color index configuration, processor/FPU flags, assembler use, selected devices, and language features.

The makefile includes the generic Ghostscript make fragments plus `pcwin.mak`, then defines OS/2 platform modules (`gp_os2`, `gp_stdia`), an OS/2 printer IO device feature, auxiliary build programs, generated configuration headers, main `gsos2`/`gsdll2` targets, resources/icons, Presentation Manager helper driver, and ZIP packaging rules.

Dependencies include EMX GCC or IBM C++, OS/2 `LINK386`, `rc`, `emxbind`, bundled JPEG/libpng/zlib/jbig2/icclib, Windows/OS2 device fragments, and platform sources such as `gp_os2.c`, `gp_os2pr.c`, `gdevpm.c`, `gdevos2p.c`, and `gspmdrv.c`.

Filesystem relevance is indirect. The file configures userland Ghostscript builds and printer/file IO choices, but it is not an OS filesystem component.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/os2.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ostack.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ostack.h

Defines macros for Ghostscript’s operand stack as seen by operator implementations. It maps the current interpreter context to `o_stack`, `osp`, `osbot`, and `ostop`, and provides push/pop/overflow/underflow helpers.

The important design note is that the interpreter does not pre-check underflow before invoking an operator. Guard refs below the operand stack allow normal type checks to detect underflow later; operators that do not type-check or that have variable arity must call `check_op`.

Dependencies include `iostack.h` and `icstate.h`. The stack itself is a linked block stack, so whole-stack operators must account for non-contiguous storage.

This is interpreter runtime support, unrelated to Plan 9 filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ostack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/pcwin.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/pcwin.mak

Makefile fragment for PC window-system-specific Ghostscript devices shared by MS Windows and OS/2 builds. It is separated because Windows code needs special compile switches and include paths.

It defines rules for deprecated MS Windows DLL/display devices, Windows DDB/DIB printer devices, OS/2 Presentation Manager devices, and OS/2 printer devices. Targets assemble `.dev` modules from objects such as `gdevmswn`, `gdevmsxf`, `gdevwdib`, `gdevwprn`, `gdevwpr2`, `gdevpm`, and `gdevos2p`.

Dependencies include Windows headers, OS/2/Windows Ghostscript DLL headers, device memory/color helpers, printer device headers, and make variables from platform makefiles.

Filesystem relevance is indirect and limited to userland printer/display build integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/pcwin.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/pipe_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/pipe_.h

Portable declaration wrapper for `popen` and `pclose`. It includes Ghostscript’s `stdio_.h` wrapper and normalizes Windows versus non-Windows handling.

On Win32 it redirects `popen` to Ghostscript’s `mswin_popen` implementation because historical MSVC `_popen` versions were considered broken for Ghostscript’s needs, while `pclose` maps to `_pclose`. On non-Windows platforms it declares `popen` without a prototype argument list because old platform headers were inconsistent.

Dependencies are C stdio and platform macros such as `__WIN32__`.

Filesystem relevance is indirect: this supports process pipe IO for userland Ghostscript streams, not kernel pipes or VFS.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/pipe_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/plan9-aux.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/plan9-aux.mak

Plan 9-adapted auxiliary makefile fragment, derived from Ghostscript’s Unix auxiliary make rules. It builds Unix-like platform modules and helper programs for the Plan 9/APE environment.

It defines `unix_.dev` from `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, and `gp_unix_cache`, plus a `sysv_.dev` variant. It builds helper executables (`echogs`, `genarch`, `genconf`, `gendev`, `genht`, `geninit`) and generates `gconfig_.h` by probing `/sys/include/ape` for headers such as `dirent.h`, `sys/time.h`, and `sys/times.h`.

Dependencies include APE headers, Unix compatibility platform code, MD5 cache support, and the generic Ghostscript build variables.

Filesystem relevance is modest but real for 9front userland: it probes Plan 9 APE include files and selects Unix-style file/path support modules for Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/plan9-aux.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/png_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/png_.h

Small include wrapper for libpng. It selects `<png.h>` when `SHARE_LIBPNG` is true and the local `"png.h"` otherwise.

The wrapper lets Ghostscript source depend on `png_.h` without knowing whether the build is linked to a shared system libpng or the bundled libpng source tree.

Filesystem relevance is none directly; this is image codec include plumbing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/png_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.c

Implements the `ASCII85Decode` stream filter. It decodes groups of five ASCII85 digits into four binary bytes, recognizes `z` as a compressed zero group, ignores scanner-classified whitespace, and terminates on `~>`.

The filter is resumable across stream buffer boundaries through `stream_A85D_state.odd` and `word`. It checks for output-buffer capacity, detects ASCII85 overflow, handles odd final groups, and accepts CR/LF between `~` and `>` for Acrobat compatibility despite stricter PostScript language wording.

Dependencies include `strimpl.h`, `sa85d.h`, and `scanchar.h`. It exports `s_A85D_template`.

Risk notes: malformed streams return `ERRC`; finalization with a single dangling digit is invalid. This is stream codec logic, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.h

Declares the ASCII85Decode filter state and stream template. The state embeds common stream state plus the number of accumulated odd digits and the partial 32-bit word.

It provides the GC descriptor macro, an inline initialization macro used by scanner code to avoid an extra function call, and `s_A85D_template`.

Dependencies are Ghostscript stream common definitions, and `strimpl.h` when templates are referenced.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85x.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85x.h

Declares the ASCII85Encode filter state and stream template. It includes `sa85d.h` and defines encoder state fields for output line digit count and last character written.

The inline initialization sets line count to zero and last character to newline. The actual encoder implementation is elsewhere, while this header supplies the shared state layout and `s_A85E_template`.

Dependencies are Ghostscript stream common definitions and ASCII85Decode declarations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85x.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.c

Implements an AES stream filter wrapper around Plan 9 libsec AES CBC routines. It stores key material in the stream state, delays AES setup until processing begins, reads the first 16 input bytes as the CBC initialization vector, and decrypts full 16-byte blocks.

The process routine supports optional RFC 1423-style padding removal on the final block. It is symmetric at the stream-template level but this implementation calls `aesCBCdecrypt`, so its operational behavior here is decryption. It returns stream suspension when more input or output space is needed.

Dependencies include `saes.h`, `strimpl.h`, Ghostscript error headers, and Plan 9 `<libsec.h>` via the header.

Risk notes: invalid key lengths and missing keys fail; invalid padding is tolerated by treating padding length as zero, matching a bug-compatibility comment. It is cryptographic stream support for PDF/PostScript, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.h

Declares Ghostscript’s AES stream state for this 9front tree. It includes `scommon.h`, enables `_PLAN9_SOURCE`, and includes Plan 9 `<libsec.h>`.

The state stores key bytes, key length, CBC IV, initialization flag, padding mode, and an embedded `AESstate`. It exposes key setup, padding setup, the AES stream template, and a buffer processing declaration.

Dependencies include Ghostscript stream state conventions and Plan 9 libsec. This is a 9front-specific adaptation compared with heap-context AES implementations in some Ghostscript versions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/saes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.c

Implements the Arcfour/RC4-compatible stream cipher filter. `s_arcfour_set_key` initializes the 256-byte S-box with the key scheduling algorithm, and `s_arcfour_process` generates the keystream while XORing input to output.

The same processing path encrypts and decrypts because Arcfour is XOR-stream based. State consists of the S-box and two indices, saved after each buffer chunk for resumable stream processing. `s_arcfour_process_buffer` provides an in-place buffer helper around the stream cursor API.

Dependencies include Ghostscript stream implementation headers and error conventions. It exports `s_arcfour_template`.

Security note: Arcfour/RC4 is legacy cryptography retained for PDF compatibility. This file is not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.h

Declares Arcfour stream cipher state, key setup, stream template, and buffer helper. The state embeds stream common fields plus RC4 indices `x`/`y` and a 256-byte permutation table.

Dependencies are `scommon.h` and `strimpl.h` for template use. The header frames the algorithm as functionally equivalent to PDF-specified RC4 while avoiding the trademarked name in code comments.

This is PDF encryption filter support, not filesystem infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sarc4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.c

Implements BCP and TBCP encode/decode filters. Encoding escapes selected control characters by emitting Ctrl-A and XORing the control byte with `0x40`; TBCP escapes a slightly different set.

Decoding recognizes escaped control sequences, end-of-file Ctrl-D, interrupt Ctrl-C, status Ctrl-T, flow-control bytes, and tagged mode additions. Interrupt and status handling are callback hooks stored in the decode state. The code is stream-resumable through `escaped`, `copy_count`, and related fields, although copy-string support is effectively dormant here.

Dependencies include `strimpl.h` and `sbcp.h`. It exports templates for `BCPEncode`, `TBCPEncode`, `BCPDecode`, and `TBCPDecode`.

Filesystem relevance is indirect: BCP/TBCP is printer/job transport encoding for userland Ghostscript streams.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.h

Declares BCP/TBCP stream templates and decode state. Encoding has no custom state, while decode state includes callback pointers for interrupt/status requests and dynamic fields for escape handling and tagged copy behavior.

Dependencies are Ghostscript stream common definitions and `strimpl.h` when templates are referenced.

This is printer protocol stream plumbing, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.c

Implements BoundedHuffman encode and decode filters. These extend the common Huffman stream machinery with zero-run encoding and optional end-of-data markers.

The encoder allocates an encoding table from the supplied Huffman definition, accumulates runs of zero values, emits zero-run codes where possible, writes optional EOD, and flushes pending bits. The decoder allocates a decoding table, decodes variable-length codes, expands zero runs, and recognizes EOD.

Dependencies include `sbhc.h`, `shcgen.h`, Ghostscript memory allocation, and the Huffman encoder/decoder state macros from `shc.h`.

Risk notes: the file contains historical `WRONG` and `NOT IMPLEMENTED YET` comments around table generation assumptions and incomplete partial-code handling. This is compression stream code, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.h

Declares BoundedHuffman filter states and templates. The common state embeds Huffman state, an `hc_definition`, client-set `EndOfData` and `EncodeZeroRuns`, and a dynamic `zeros` counter.

Separate encode/decode states add `hce_table` or `hcd_table` storage and GC descriptors for allocated definition/table arrays. The header also provides inline init and decode state load/store macros.

Dependencies include `shc.h` and `strimpl.h`. This is stream compression infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbtx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbtx.h

Declares ByteTranslate encode/decode filter state. The state is simply stream common fields plus a 256-byte translation table, with encode and decode using the same structure type aliases.

It exposes `s_BTE_template` and `s_BTD_template`; implementation lives in `sfilter1.c`.

This is byte mapping stream support, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbtx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.c

Implements Burrows-Wheeler block sort encode/decode filters and a shared buffered-block stream helper. The common helper allocates a block buffer, fills it from input, flips between filling and draining modes, and frees storage on release.

Encoding reverses the buffered block, sorts all cyclic rotations using an initial radix bucket pass plus `qsort`, writes block length and original index, and emits the transformed last-column bytes. Decoding reads length/index, fills the transformed block, builds inverse permutation offset tables, then reconstructs output bytes through LF-mapping.

The decoder uses `SHORT_OFFSETS` tables to reduce memory: 64K-level full offsets, 4K-level 16-bit offsets, and packed 12-bit per-entry residual offsets. It falls back to an int offset table if that macro is disabled.

Dependencies include Ghostscript memory/stream code, `qsort`, and `sbwbs.h`.

Risk notes: the encoder uses a static global pointer to pass stream state into the comparison callback, so concurrent sorting in multiple streams would not be reentrant. This is compression filter code, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.h

Declares buffered stream state and BWBlockSort encode/decode state. The shared state contains `BlockSize`, allocated buffer, filling flag, current block size, and position.

The BWBlockSort state adds an `offsets` allocation and encode/decode fields for block length, original index, and current decode index. It exposes encode/decode templates and GC descriptors.

Dependencies are `scommon.h` and `strimpl.h`. This is block compression stream support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sbwbs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scanchar.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scanchar.h

Defines the scanner character classification interface for Ghostscript token scanning. It declares `scan_char_array`, defines `scan_char_decoder` with an exception offset, and assigns classification constants for digits, names, binary tokens, whitespace, exceptions, and other characters.

It also defines scanner-level special characters such as NULL, EOT, vertical tab, DOS EOF, CR, and abstract EOL handling for platforms where newline and carriage return differ unusually.

Dependencies include `scommon.h` for stream exception counts. The table implementation is in `scantab.c`.

This is PostScript/PDF tokenization support, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scanchar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scantab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scantab.c

Defines `scan_char_array`, the token scanner lookup table described by `scanchar.h`. The table classifies stream exceptions, ASCII control characters, printable ASCII, binary token bytes 128-159, and high bytes 160-255.

Digits map to radix values, letters map to radix values through base 36 where appropriate, PostScript delimiters map to `ctype_other`, whitespace maps to `ctype_space`, and binary token marker bytes map to `ctype_btoken`.

Dependencies include `stdpre.h`, `scommon.h`, and `scanchar.h`.

This is scanner data for Ghostscript language parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scantab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scf.h

Common CCITTFax encode/decode definitions. It documents Group 3/Group 4 fax run-length Huffman coding, declares encoding tables, decoding tables, EOL and 2-D code constants, exceptional decode values, and run-detection macros.

The macros `skip_white_pixels` and `skip_black_pixels` are performance-sensitive scanners over packed bitmap rows. They account for `BlackIs1` polarity and use byte bit-run tables to skip long same-color runs efficiently.

Dependencies include `shc.h`, architecture sizing macros, and bit-run helper tables declared elsewhere.

This is image compression support for fax/PDF streams, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfd.c

Implements the `CCITTFaxDecode` stream filter. Initialization allocates current and optional previous line buffers, sets raster size and polarity, initializes Huffman decode state, and prepares row/EOL tracking.

The process routine manages row completion, output copying, EOL detection, optional damaged-row skipping, Group 3 1-D, Group 3 mixed 1-D/2-D, and Group 4 2-D modes. It decodes Huffman runs into packed output rows using macros for bit buffering, white/black run decoding, vertical/pass/horizontal 2-D modes, and black-bit inversion.

EOL scanning recognizes RTC/EOFB-style termination counts. 1-D decoding alternates white and black runs. 2-D decoding compares the current row with the previous reference row and handles pass, vertical, and horizontal modes.

Dependencies include `scf.h`, `scfx.h`, `strimpl.h`, `gdebug.h`, and generated decode tables from `scfdtab.c`.

Risk notes: uncompressed mode returns `ERRC` in the active code path, and comments mark some damaged-row and partial-code cases as not implemented. This is stream/image decompression code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdgen.c

Generator program for `scfdtab.c`, the CCITTFaxDecode lookup tables. It writes C source containing white, black, 2-D, and uncompressed decode tables.

The generator enumerates codes from the encoder tables in `scfetab.c`/`scf.h`, builds first-level and optional second-level decode nodes, fills replicated leaves for short codes, and emits extension nodes for longer codes. It also emits a dummy function for compilers requiring executable code in every source file.

Dependencies include `scf.h`, C stdio, malloc, and the CCITTFax encoding table definitions.

This is build-time table generation for stream decoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdtab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdtab.c

Generated CCITTFaxDecode table source. It defines `cf_white_decode`, `cf_black_decode`, `cf_2d_decode`, and `cf_uncompressed_decode` arrays of `cfd_node` entries consumed by `scfd.c`.

The arrays encode run lengths, exceptional values such as EOL/invalid/uncompressed/pass/horizontal, and code lengths. They are generated from the encoder-side canonical tables and the generator logic in `scfdgen.c`.

Dependencies include `scommon.h` and `scf.h`. The dummy `scfdtab_dummy` exists for old compilers.

This is generated compression metadata, not executable algorithm logic beyond table storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfdtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfe.c

Implements the `CCITTFaxEncode` stream filter. Initialization allocates current row, optional previous row, and encoded-line buffers; computes raster and worst-case encoded byte size; initializes Huffman encoder state; and prepares mixed 1-D/2-D row cadence.

The process routine collects full input scan lines, normalizes row-end sentinel bits for run scanners, writes optional EOL/byte alignment, encodes the row directly to the caller buffer or internal line buffer, swaps current/reference rows in 2-D modes, and emits final end-of-block EOL sequences.

`cf_encode_1d` alternates white and black run detection and emits run Huffman codes. `cf_encode_2d` compares current and previous rows and chooses pass, vertical, or horizontal coding. Long runs are split into make-up and termination codes.

Dependencies include `scf.h`, `scfx.h`, `strimpl.h`, generated/static tables from `scfetab.c`, and bit-run macros.

This is fax image compression stream logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfetab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfetab.c

Defines canonical CCITTFaxEncode run tables. It includes EOL codes, 1-D and 2-D uncompressed markers, pass/vertical/horizontal 2-D codes, Group 3 mixed-mode EOL variants, white termination/make-up tables, black termination/make-up tables, and uncompressed exit codes.

These tables are consumed directly by `scfe.c` and indirectly by `scfdgen.c` to generate decoder tables.

Dependencies include `scommon.h` and `scf.h`.

This is static CCITT fax Huffman metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfetab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfparam.c

Implements parameter get/put support for CCITTFax filters. It defines the mapping between PostScript/PDF parameter names and `stream_CF_state` fields.

` s_CF_get_params` writes all or only non-default parameters. `s_CF_put_params` reads a parameter list into a copy of the state, validates ranges for `K`, `Columns`, `Rows`, `DamagedRowsBeforeError`, and power-of-two `DecodedByteAlign`, then commits the copy on success.

Dependencies include Ghostscript parameter APIs, `scf.h` for maximum width, and `scfx.h` for state layout.

This is stream parameter validation, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfx.h

Defines CCITTFax stream state structures for encode and decode filters. The common state stores fax parameters such as `Uncompressed`, `K`, EOL/byte-alignment flags, dimensions, block termination, polarity, damaged-row tolerance, bit order, decoded alignment, row buffers, raster size, and mixed-mode row counter.

Encode state adds encoded-line buffer fields and copy counters. Decode state adds bit position, rows/row counters, input/output row positions, EOL count, polarity inversion, 2-D run state, damaged-row tracking, and placeholders for uncompressed runs.

Dependencies include `shc.h`, `strimpl.h`, and the templates implemented in `scfe.c`/`scfd.c`.

This header is the contract between CCITTFax parameter handling and filter implementations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scfx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scommon.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scommon.h

Defines core Ghostscript stream types shared by stream clients and implementations. It introduces opaque `stream`, `stream_state`, and `stream_template`, stream exception return codes, read/write cursor layouts, stream procedure typedef macros, and generic parameter get/put procedure forms.

The generic `stream_state` contains the template pointer, memory allocator, error reporter, minimum lookahead, and an error string buffer. Comments explain stream exceptional-condition behavior and byte-oriented access conventions.

Dependencies include `gsmemory.h`, `gstypes.h`, and `gsstype.h`.

This is foundational userland stream infrastructure used by filters and file-like IO in Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/scommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.c

Implements common DCT/JPEG filter parameter get/put logic. It handles scalar DCT parameters (`ColorTransform`, `QFactor`) and JPEG stream data flags (`Picky`, `Relax`), plus quantization and Huffman table serialization/deserialization.

Quantization handling converts between Adobe zigzag order and IJG natural order for newer JPEG versions, supports byte strings and float arrays, applies `QFactor`, detects duplicate tables, assigns component table numbers, and allocates missing IJG quant tables through Ghostscript JPEG allocation helpers.

Huffman handling packs/unpacks the 16 count bytes plus values, supports byte string or float-array input via `s_DCT_byte_params`, detects duplicate DC/AC tables, assigns component table numbers, and enforces baseline or relaxed table-count limits.

Dependencies include `jpeglib_.h`, `sdct.h`, `sdcparam.h`, `sjpeg.h`, Ghostscript parameter APIs, and memory/error utilities.

Risk notes: comments mark some deallocation paths and byte-array handling as historically imperfect. This is JPEG stream parameter plumbing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.h

Declares internal common DCT parameter routines used by DCT encode/decode parameter files. It exposes scalar get/put, quantization table get/put, Huffman table get/put, and byte-parameter extraction.

The header explicitly says these procedures are internal and not documented for general clients.

Dependencies include DCT stream state and Ghostscript parameter types supplied by including files.

This is JPEG parameter API glue.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdct.h

Defines common DCT/JPEG stream state. It models IJG libjpeg allocations through immovable Ghostscript memory blocks tracked by `jpeg_block_t`, wraps common JPEG error/longjmp/memory/parameter fields, and defines separate compression and decompression data records.

`stream_DCT_state` stores common stream state, marker data, `QFactor`, `ColorTransform`, `NoMarker`, JPEG allocation memory, a union pointer to compress/decompress/common data, scan line size, and phase. It declares DCT encode/decode templates and the shared defaults function.

Dependencies include `setjmp.h`, libjpeg public structs, Ghostscript stream implementation headers, and memory/GC descriptor macros.

This is the central type contract for Ghostscript DCT filters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctc.c

Common DCT encode/decode support. It declares the public GC descriptor for `stream_DCT_state` and implements `s_DCT_set_defaults`.

Defaults set JPEG allocation memory to Ghostscript’s non-GC memory, clear the libjpeg data pointer, set `ColorTransform` to unspecified, `QFactor` to `1.0`, and clear marker data.

Dependencies include `jpeglib_.h`, Ghostscript memory allocation headers, `strimpl.h`, and `sdct.h`.

This is shared JPEG stream initialization support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctd.c

Implements the `DCTDecode` stream filter around IJG libjpeg. It provides a JPEG source manager that suspends when more input is needed, skips pending bytes across stream chunks, and inserts a fake EOI when input ends prematurely.

The process routine is phase-driven: skip leading garbage until a marker, read headers, apply `ColorTransform` if no Adobe marker overrides it, start decompression, stream scanlines to output, optionally buffer oversized scanlines, finish decompression, and return EOFC.

Dependencies include `jpeglib_.h`, `jerror_.h`, `sdct.h`, `sjpeg.h`, Ghostscript memory/debug headers, and IJG decompression APIs via Ghostscript wrappers.

Risk notes: fake EOI tolerance is compatibility behavior. Release destroys JPEG state and frees scanline/decompress allocations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdctd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcte.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcte.c

Implements the `DCTEncode` stream filter around IJG libjpeg. It provides a JPEG destination manager that suspends when the output buffer fills, initializes compression, writes optional marker bytes, optionally writes an Adobe APP14 marker, streams scanlines, finishes compression into a fixed internal buffer, and drains final bytes.

The process routine is phase-driven from initialization through final EOFC. It checks that complete scanlines are available unless input is marked final, and returns output-full or input-needed statuses as required by Ghostscript stream conventions.

Dependencies include `jpeglib_.h`, `jerror_.h`, `sdct.h`, `sjpeg.h`, and Ghostscript memory/debug headers.

This is JPEG encoding stream glue, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcte.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sddparam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sddparam.c

Implements `DCTDecode` parameter get/put wrappers. `s_DCTD_get_params` creates default DCT state and delegates common scalar parameter writing to `s_DCT_get_params`; a comment marks fuller decode parameter reporting as not yet implemented.

`s_DCTD_put_params` applies common DCT scalar parameters, then accepts Huffman and quantization tables for decode streams so missing tables can be supplied externally.

Dependencies include `jpeglib_.h`, `sdct.h`, `sdcparam.h`, `sjpeg.h`, and Ghostscript parameter/error APIs.

This is JPEG decode parameter handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/sddparam.c -->