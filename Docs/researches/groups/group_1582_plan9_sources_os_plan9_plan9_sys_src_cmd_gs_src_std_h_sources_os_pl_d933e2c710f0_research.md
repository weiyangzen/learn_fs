# Group Research: group_1582_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_std_h_sources_os_pl_d933e2c710f0

Scope confirmed against `Docs/research_subset_a.md`. All listed files were read completely. This batch covers Ghostscript portability headers, stream infrastructure, zlib stream adapters, and a trimmed FreeType-derived TrueType outline/hinting adapter inside the Plan 9 source tree.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/std.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/std.h

Purpose: central Ghostscript standard header that layers architecture-dependent constants from `arch.h` on top of compiler portability definitions from `stdpre.h`.

Key contents:
- Maps upper-case `ARCH_*` values to older lower-case compatibility names.
- Defines memory alignment, integer sizes, small-memory detection, `bits16`/`bits32`, signed min/max values, unsigned max aliases, and pointer min/max values.
- Provides portable arithmetic right-shift macros based on `arch_arith_rshift`.
- Declares Ghostscript output/error functions: `outwrite`, `errwrite`, `outflush`, `errflush`, `outprintf`, `errprintf`.
- Defines extensive debug/error printing macro families: `dprintf*`, `dlprintf*`, `eprintf*`, `lprintf*`.
- Declares program identity helpers and repeats `gs_memory_t`/`init_proc` compatibility definitions.

Dependencies: includes `stdpre.h`, `arch.h`, and `<stdio.h>`.

Integration notes: almost every C file in this group depends indirectly on this header for `byte`, `uint`, `bool`, `private`, `public`, architecture constants, and diagnostic output.

Risks: heavy macro use makes side effects possible in printf-like wrappers; duplicated `gs_memory_t`/`init_proc` definitions are guarded but reflect legacy layering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/std.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdint_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdint_.h

Purpose: Ghostscript substitute for C99 `stdint.h`.

Key contents:
- Includes `std.h` first to establish Ghostscript architecture and base typedefs.
- Uses native `<stdint.h>` when `HAVE_STDINT_H` is available, with a MacOS fallback.
- Accepts environments where `sys/types.h` already supplied fixed-width types.
- Provides platform-specific typedefs for Win32, VMS, and Cygwin.
- Falls back to `ARCH_SIZEOF_*` checks for 8-, 16-, 32-, and 64-bit signed/unsigned integer types.

Dependencies: `std.h`, optional `<stdint.h>`/`<inttypes.h>`.

Integration notes: `ttfsfnt.h` includes this header to define TrueType exact-size aliases (`uint8`, `int16`, `uint32`, etc.).

Risks: fallback branches assume exactly matching architecture sizes; if `ARCH_SIZEOF_LONG_LONG` is unavailable on a 32-bit compiler without 64-bit support, `int64_t`/`uint64_t` may not be defined.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdint_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdio_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdio_.h

Purpose: Ghostscript wrapper around standard I/O headers.

Key contents:
- Includes `std.h` before `<stdio.h>` to avoid `sys/types.h` ordering conflicts.
- Supplies or remaps `unlink` on older VMS and non-VMS systems.
- Contains Plan 9-specific protection against a system `sclose` name collision by redefining `sclose(s)` to `Sclose(s)` when `Plan9` is set.
- Defines missing `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`.
- Maps MSVC `fdopen`/`fileno` to underscored CRT names.

Dependencies: `std.h`, `<stdio.h>`, optional VMS `<unixio.h>`.

Integration notes: `stream.c` includes this file before the stream package, so the Plan 9 `sclose` collision handling is directly relevant.

Risks: macro remapping of `sclose` changes symbol visibility and must match how the Plan 9 port compiles system headers versus Ghostscript stream APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdio_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdpn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdpn.h

Purpose: deprecated pre-ANSI function-prototype compatibility macros.

Key contents:
- Defines `P0()` through `P16(...)`.
- Modern behavior simply expands argument type lists directly, with `P0()` as `void`.

Dependencies: none.

Integration notes: included from `stdpre.h`; exists to keep older declarations compiling.

Risks: new code should not use these macros; retained for source compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdpn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdpre.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdpre.h

Purpose: compiler and platform portability foundation used before architecture-specific setup.

Key contents:
- Normalizes platform symbols such as `__MSDOS__`, `SYSV`, `__SVR3`, and `__OSF__`.
- Detects prototype support and conditionally disables `const`, `volatile`, and `inline`.
- Defines inline support conventions through `extern_inline` and `HAVE_EXTERN_INLINE`.
- Provides `DISCARD`, `size_of`, `countof`, `offset_of`, `ALIGNMENT_MOD`, `ROUND_UP`, and `ROUND_DOWN`.
- Defines Ghostscript short unsigned aliases (`byte`, `uchar`, `ushort`, `uint`, `ulong`) and carefully avoids `sys/types.h` conflicts.
- Defines non-C++ `bool`, `true`, `false`, pointer comparison macros, `floatp`, `BEGIN`/`END`, `DO_NOTHING`, `client_name_t`, `public`, `private`, and process exit constants.
- Includes `stdpn.h`.

Dependencies: `<sys/types.h>`, `stdpn.h`.

Integration notes: this is the base for most files in the batch via `std.h`.

Risks: macro definitions such as `private`, `public`, and boolean aliases can conflict with external headers if include ordering is wrong.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stdpre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/store.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/store.h

Purpose: macro layer for assigning Ghostscript `ref` objects while preserving save/restore and local/global VM invariants.

Key contents:
- Defines fast `ref_assign` variants and save checks using `idmemory` masks.
- Provides `ref_save`, `ref_mark_new`, `ref_assign_new`, `ref_assign_old`, and related `_in` variants for explicit memory contexts.
- Adds debug fill patterns for unused ref fields under `DEBUG`.
- Defines constructors for scalar refs: booleans, integers, marks, nulls, operators, reals.
- Defines constructors for composite refs: arrays, strings, structs, and associative structs.

Dependencies: `ialloc.h`, `idosave.h`, ref/type macros from the interpreter object system.

Integration notes: used by the PostScript interpreter to make all object-slot writes visible to Ghostscript’s memory manager.

Risks: macro parameters are evaluated in assignment contexts; callers must avoid expressions with unintended side effects. Correct use of `_new` versus `_old` variants is critical for VM save/restore correctness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/store.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.c

Purpose: implementation of Ghostscript’s stream abstraction, including allocation, GC descriptors, buffering, filters, string streams, and null filters.

Key contents:
- Defines stream and stream-state structure descriptors plus GC enumeration, relocation, and finalization.
- Implements `s_init`, `s_alloc`, `s_init_state`, `s_alloc_state`, `s_std_init`, `ssetfilename`, and `sfilename`.
- Implements generic reset/flush/close/disable behavior and filter close/flush propagation.
- Provides core APIs: `savailable`, `stell`, `spseek`, `sswitch`, `sclose`, `spgetcc`, `spputc`, `sungetc`, `sgets`, `sputs`, `spskip`, and `sreadline`.
- Implements buffer processing through `s_process_read_buf`, `s_process_write_buf`, private `sreadbuf`, private `swritebuf`, `stream_move`, and private `stream_compact`.
- Implements string streams: `sread_string`, `sread_string_reusable`, `swrite_string`, string seek/process helpers.
- Implements `swrite_position_only`.
- Implements filter setup/teardown: `s_init_filter`, `s_add_filter`, and `s_close_filters`.
- Defines `s_NullE_template` and `s_NullD_template`.

Dependencies: `stdio_.h`, `memory_.h`, `gdebug.h`, `gpcheck.h`, `stream.h`, `strimpl.h`.

Integration notes: this is the central runtime substrate for all stream filters, including the zlib filters in this batch. It also participates in Ghostscript GC relocation by updating buffer cursors after buffer movement.

Risks: stream pipeline traversal mutates `strm` links temporarily using reversible pointer walking; errors there could corrupt pipeline topology. Close/finalize behavior is deliberately conservative for file streams because non-file streams may free storage during close.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.h

Purpose: public stream API and exposed `stream` structure for performance-sensitive clients.

Key contents:
- Defines `stream_procs` virtual methods: `available`, `seek`, `reset`, `flush`, `close`, `process`, and `switch_mode`.
- Defines `struct stream_s`, including common stream state, buffer cursors, mode flags, position, procedures, filter link, interpreter bookkeeping, C `FILE *`, and file subrange state.
- Provides mode and validity macros (`s_mode_read`, `s_mode_write`, `s_can_seek`, etc.).
- Declares fast I/O macros and functions: `sgetc`, `spgetc`, `sputs`, `sputc`, `sgets`, `spskip`, inline cursor helpers, and buffer availability helpers.
- Declares allocation, initialization, string/file stream setup, subfile setup, filename access, filter setup, filter close, and null filter templates.

Dependencies: `scommon.h`, `srdline.h`, and `<stdio.h>` via users.

Integration notes: the struct is intentionally public so hot byte-level stream operations can be macros rather than procedure calls.

Risks: clients can directly touch internal fields; misuse can break cursor invariants documented in the header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/strimpl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/strimpl.h

Purpose: implementation-facing stream filter contract.

Key contents:
- Documents the `process` procedure semantics for input/output cursors and `last`.
- Defines the required return statuses: `EOFC`, `ERRC`, `0`, and `1`.
- Documents EOD lookahead behavior needed by decoding filters.
- Defines `struct stream_template_s`, including state type, init, process, min buffer sizes, release, set-defaults, and reinit hooks.
- Declares `stream_move` and hex decoding helper `s_hex_process`.
- Defines `hex_syntax` options.

Dependencies: `scommon.h`, `gstypes.h`, `gsstruct.h`.

Integration notes: zlib templates and null stream templates implement this contract.

Risks: filters must honor subtle buffer-boundary/EOD semantics or behavior changes depending on buffer size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/strimpl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/string_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/string_.h

Purpose: Ghostscript wrapper around string/memory headers.

Key contents:
- Includes `std.h` first.
- Uses `<strings.h>` and maps `strchr` to `index` for `BSD4_2`.
- Otherwise includes `<string.h>`.
- Optionally replaces `memmove` with `gs_memmove` when `MEMORY__NEED_MEMMOVE` is set.
- Adjusts `strlen` for THINK C.

Dependencies: `std.h`, system string headers.

Integration notes: centralizes portability behavior for memory/string functions.

Risks: macro replacement of `memmove` must be consistent with memory subsystem configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/string_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibc.c

Purpose: shared zlib stream support for Ghostscript compression and decompression filters.

Key contents:
- Defines GC descriptors for zlib block tracking, dynamic state, and public zlib stream state.
- Implements `s_zlib_set_defaults`.
- Implements `s_zlib_alloc_dynamic_state` to allocate immovable `zlib_dynamic_state_t`, configure `zalloc`, `zfree`, and `opaque`.
- Implements `s_zlib_free_dynamic_state`.
- Implements zlib-compatible `s_zlib_alloc` and `s_zlib_free`, tracking every zlib allocation in a linked list of `zlib_block_t`.

Dependencies: Ghostscript memory/structure headers, `strimpl.h`, `szlibxx.h`, `zconf.h`.

Integration notes: bridges zlib’s allocator callbacks into Ghostscript’s stable/immovable allocation model so GC can track allocations.

Risks: freeing unrecorded data is logged rather than fatal; allocation tracking correctness is essential because zlib private memory is external to normal movable stream state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibd.c

Purpose: zlib decompression stream filter.

Key contents:
- `s_zlibD_init` allocates dynamic state and calls `inflateInit2`, honoring `no_wrapper`.
- `s_zlibD_reset` calls `inflateReset`.
- `s_zlibD_process` maps Ghostscript stream cursors to `z_stream`, handles empty input/full output, detects a known empty-stream encoding from JAWS PDF output, and converts zlib statuses to stream statuses.
- `s_zlibD_release` calls `inflateEnd` and frees dynamic state.
- Exports `s_zlibD_template`.

Dependencies: `memory_.h`, `std.h`, `gsmemory.h`, `gsmalloc.h`, `strimpl.h`, `szlibxx.h`, zlib.

Integration notes: used as a decoding filter template in the stream framework.

Risks: several initialization/reset failures collapse to `ERRC` with comments noting this is imprecise; malformed input status reporting is therefore coarse.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibe.c

Purpose: zlib compression stream filter.

Key contents:
- `s_zlibE_init` allocates dynamic state and calls `deflateInit2` with level, method, wrapper, memory level, and strategy.
- `s_zlibE_reset` calls `deflateReset`.
- `s_zlibE_process` maps stream cursors to zlib input/output buffers and uses `Z_FINISH` on final input, otherwise `Z_NO_FLUSH`.
- `s_zlibE_release` calls `deflateEnd` and frees dynamic state.
- Exports `s_zlibE_template`.

Dependencies: `std.h`, `gsmemory.h`, `gsmalloc.h`, `strimpl.h`, `szlibxx.h`, zlib.

Integration notes: used as an encoding filter template in the stream pipeline.

Risks: like the decoder, setup/reset errors return generic `ERRC`; init failure after `deflateInit2` does not explicitly free dynamic state in that branch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibx.h

Purpose: public zlib stream state definition.

Key contents:
- Forward-declares `zlib_dynamic_state_t`.
- Defines `stream_zlib_state` with `stream_state_common`, decompression/compression parameters, and dynamic zlib state pointer.
- Declares public GC descriptor macro `public_st_zlib_state`.
- Declares `s_zlibD_template`, `s_zlibE_template`, and `s_zlib_set_defaults`.

Dependencies: stream state types from the stream subsystem.

Integration notes: included by clients that need to configure zlib filter parameters before initialization.

Risks: dynamic state is opaque; callers must use stream-template lifecycle hooks rather than managing it directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibxx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibxx.h

Purpose: private zlib implementation definitions.

Key contents:
- Includes `szlibx.h` and `zlib.h`.
- Defines `zlib_block_t` linked-list nodes for GC-visible zlib allocation tracking.
- Defines `zlib_dynamic_state_t` with Ghostscript memory pointer, allocation list, and `z_stream`.
- Declares private structure descriptor macros for block and dynamic state.
- Declares allocator/free callbacks and dynamic-state allocation/free helpers.

Dependencies: zlib headers and Ghostscript memory descriptor macros.

Integration notes: shared by `szlibc.c`, `szlibd.c`, and `szlibe.c`.

Risks: header requires compile include path for zlib source/include directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibxx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/time_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/time_.h

Purpose: Ghostscript wrapper for time-related system headers.

Key contents:
- Includes `std.h` and `gconfig_.h`.
- Includes `<sys/time.h>` when available.
- For Plan 9, SCO, AIX, DYNIX/ptx, GCC/glibc, and Intel compiler cases, includes both `<sys/time.h>` and `<time.h>`.
- Defines fallback `timeval` and `timezone` structs when no `<sys/time.h>` is available.
- Defines `gettimeofday_no_timezone` for SVR4.0.
- Includes `<sys/times.h>` when configured and defines `use_times_for_usertime`; supplies default `CLK_TCK` if missing.

Dependencies: `std.h`, `gconfig_.h`, system time headers.

Integration notes: Plan 9 is explicitly called out as needing both time headers.

Risks: fallback struct definitions assume no system definitions are already present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/time_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.c

Purpose: FreeType-derived arithmetic helpers for TrueType fixed-point computations, with the instruction interpreter removed.

Key contents:
- Defines `Roots`, a lookup table used to seed square-root iteration.
- Implements `MulDiv` and `MulDiv_Round` using native 64-bit arithmetic when `LONG64` is available.
- Implements `Order64` and `Sqrt64` for native 64-bit mode.
- Provides software 64-bit implementation when native 64-bit is unavailable: `Neg64__`, `Add64`, `Sub64`, `MulTo64`, `Div64by32`, `Order64`, and `Sqrt64`.
- Keeps `Order32` and `Sqrt32` in disabled `#if 0` code.

Dependencies: `ttmisc.h`, `ttcalc.h`.

Integration notes: used by `ttfmain.c` for fixed-point transforms and scaling.

Risks: division by zero in software `Div64by32` saturates to signed limits; callers need to avoid invalid scale denominators where precise errors matter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.h

Purpose: arithmetic API and type setup for TrueType calculations.

Key contents:
- Defines `Int16`, `Word16`, `Int32`, and `Word32` from configured integer sizes.
- Detects native 64-bit support through `long`, GCC `long long`, or MSVC `__int64`.
- In native mode defines `Int64` plus fast macros for multiply/divide, add, subtract, multiply, divide, and square roots.
- In fallback mode defines struct-based `Int64` and declares helper functions.
- Provides fixed-point conversion macros such as `MUL_FIXED`, `INT_TO_F26DOT6`, `INT_TO_FIXED`, `F2DOT14_TO_FIXED`, `FLOAT_TO_FIXED`, and `ROUND_F26DOT6`.

Dependencies: `ttcommon.h`, `tttypes.h`, and size macros from TrueType config.

Integration notes: shared between TrueType parsing and outline code.

Risks: relies on `SIZEOF_INT`/`SIZEOF_LONG` being correctly defined by `ttconf.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcommon.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcommon.h

Purpose: optional FreeType internal symbol-renaming header.

Key contents:
- When `TT_PREFIX_ALL_NAMES` is defined, maps many internal FreeType-style names to `FT*`-prefixed names.
- Covers arithmetic, list/cache/error/mutex/raster/cmap/object/loading/glyph/interpreter/debug/extension/kerning functions.
- Does not rename external `TT_` APIs.

Dependencies: none.

Integration notes: prevents link-time conflicts if multiple FreeType-derived components are linked together.

Risks: only active under `TT_PREFIX_ALL_NAMES`; mixed builds must use consistent macro settings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconf.h

Purpose: Ghostscript-adapted configuration header for the TrueType interpreter.

Key contents:
- Undefines autoconf-style feature macros not used here.
- Defines `WORDS_BIGENDIAN` from `ARCH_IS_BIG_ENDIAN`.
- Defines `HAVE_MEMCPY`.
- Defines `SIZEOF_INT` and `SIZEOF_LONG` from Ghostscript `ARCH_LOG2_SIZEOF_*`.
- Leaves other platform features such as `mmap`, `valloc`, `fcntl.h`, `unistd.h`, and `basename` disabled.

Dependencies: architecture macros from Ghostscript standard headers.

Integration notes: included by `ttconfig.h` to feed FreeType-derived compile-time decisions.

Risks: intentionally static configuration may need adjustment if ported outside Ghostscript’s architecture setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconfig.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconfig.h

Purpose: FreeType-derived TrueType configuration settings adapted for Ghostscript.

Key contents:
- Includes `ttconf.h`.
- Leaves debug and one’s-complement support disabled.
- Leaves `_GNUC_LONG64_` disabled by default.
- Defines `ALIGNMENT 8`.
- Enables `SECURE_COMPUTATIONS`.
- Enables `IGNORE_FILL_FLOW`.
- Defines `Print` through `vfprintf` unless an external print function is configured.
- Defines endian constants and `FT_BYTE_ORDER`; enables `LOOSE_ACCESS` for suitable big-endian unaligned-access environments.
- Disables thread-safe/reentrant flags and static interpreter/raster flags.
- Enables `TT_EXTEND_ENGINE`.

Dependencies: `ttconf.h`, standard `vfprintf` availability through surrounding includes.

Integration notes: controls TrueType arithmetic, raster, and table-management compilation choices.

Risks: non-thread-safe default is explicit; shared interpreter use must be serialized externally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.c

Purpose: byte-order input helpers for `ttfReader`.

Key contents:
- Implements `ttfReader__Byte`, `ttfReader__SignedByte`, `ttfReader__Short`, `ttfReader__UShort`, `ttfReader__UInt`, and `ttfReader__Int`.
- Reads big-endian TrueType values from the abstract reader callback interface.

Dependencies: `ttmisc.h`, `ttfoutl.h`, `ttfsfnt.h`, `ttfinp.h`.

Integration notes: used by `ttfmain.c` to parse sfnt directories, metrics, glyph flags, coordinates, and instruction lengths.

Risks: functions assume `Read` succeeds; callers must check `r->Error(r)` separately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.h

Purpose: declarations for TrueType reader input helpers.

Key contents:
- Declares byte, signed byte, unsigned/signed short, unsigned int, and signed int reader helpers.

Dependencies: requires `ttfReader` type from `ttfoutl.h`.

Integration notes: small API boundary between abstract font data access and parser code.

Risks: must be included after `ttfReader` is declared.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmain.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmain.c

Purpose: Ghostscript adapter around FreeType-derived TrueType face setup, hinting context, glyph loading, compound glyph expansion, and outline export.

Key contents:
- Defines fixed and floating transform helpers, `FixMatrix`, and `ttfSubGlyphUsage`.
- Implements `TT_Set_Instance_CharSizes` to set instance metrics and reset the TrueType instance.
- Implements interpreter reference management through `ttfInterpreter__obtain` and `ttfInterpreter__release`.
- Implements `ttfFont__init`, `ttfFont__finit`, and `ttfFont__Open`.
- `ttfFont__Open` handles TTC collections, sfnt version checks, table directory parsing, key table offsets, units-per-em, glyph counts, component limits, metrics counts, interpreter usage allocation, face/context/instance creation, CVT scaling, preprogram execution, and size setup.
- Implements glyph lifecycle helpers `ttfFont__StartGlyph` and `ttfFont__StopGlyph`.
- Implements FreeType-style glyph-zone helpers: `mount_zone`, `Init_Glyph_Component`, `cur_to_org`, and `org_to_cur`.
- Implements `ttfOutliner__init`, private glyph transform/move helpers, recursive `ttfOutliner__BuildGlyphOutlineAux`, wrapper `ttfOutliner__BuildGlyphOutline`, `ttfOutliner__DrawGlyphOutline`, and public `ttfOutliner__Outline`.
- Handles simple glyphs, compound glyphs, horizontal/vertical metrics, phantom points, glyph instruction execution through `Context_Run`, and conversion of quadratic TrueType curves into exported cubic curves or lines.
- Includes explicit handling for patented instruction failures (`fPatented`) and malformed font data.

Dependencies: `ttmisc.h`, `ttfoutl.h`, `ttfmemd.h`, `ttfinp.h`, `ttfsfnt.h`, `ttobjs.h`, `ttinterp.h`, `ttcalc.h`.

Integration notes: core external API is declared in `ttfoutl.h`; consumers provide `ttfReader` for data and `ttfExport` for outline emission.

Risks: recursive compound glyph processing is capped through `MAX_SUBGLYPH_NESTING` and usage array sizing. Reader callbacks must manage glyph buffer lifetime around `LoadGlyph`/`ReleaseGlyph`. Error handling often maps low-level TrueType errors into broad `FontError` categories.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.c

Purpose: Ghostscript GC structure descriptors for TrueType interpreter objects.

Key contents:
- Defines public descriptors for `TFace`, `TInstance`, `TExecution_Context`, `ttfFont`, and `ttfInterpreter`.
- Enumerates and relocates managed pointers in `TInstance`: face, definitions, code ranges, CVT, and storage.
- Enumerates and relocates many `TExecution_Context` pointers: current face, definitions, call stack, code ranges, storage, stack, glyph zones, twilight zones, and CVT.
- Enumerates and relocates `ttfFont` pointers: face, instance, execution context, interpreter.
- Defines pointer descriptor for `ttfInterpreter`: execution context, usage array, and memory object.

Dependencies: `ttmisc.h`, `ttfoutl.h`, `ttobjs.h`, `ttfmemd.h`, `gsstruct.h`.

Integration notes: required for Ghostscript’s garbage collector to trace and relocate FreeType-derived structures safely.

Risks: any pointer added to TrueType structs must be reflected here or GC relocation/tracing can become invalid.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.h

Purpose: declarations for TrueType GC structure descriptors.

Key contents:
- Includes `gsstype.h`.
- Declares external structure descriptors: `st_TFace`, `st_TInstance`, `st_TExecution_Context`, `st_ttfFont`, and `st_ttfInterpreter`.

Dependencies: Ghostscript structure descriptor system.

Integration notes: used by allocation sites in `ttfmain.c`.

Risks: descriptor declarations must match definitions in `ttfmemd.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfmemd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfoutl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfoutl.h

Purpose: public interface for Ghostscript’s TrueType instruction/outlining adapter.

Key contents:
- Forward-declares `TFace`, `TInstance`, `TExecution_Context`, and `ttfInterpreter`.
- Defines `FloatMatrix`, `FloatPoint`, `F26Dot6`, and `F26Dot6Point`.
- Defines abstract `ttfMemory` allocator interface.
- Defines `ttfInterpreter` capsule with execution context, compound-glyph usage stack, lock count, and memory interface.
- Defines `FontError` enum.
- Defines abstract `ttfReader` interface for EOF/read/seek/tell/error/glyph load/release.
- Defines `ttfFont` with sfnt table pointers, metrics/config fields, face/instance/context/interpreter pointers, and debug callbacks.
- Declares font and interpreter lifecycle functions.
- Defines abstract `ttfExport` outline sink callbacks.
- Defines `ttfGlyphOutline` and `ttfOutliner`, plus outliner init/outline/draw APIs.

Dependencies: Ghostscript base types and TrueType implementation structs declared elsewhere.

Integration notes: this is the main boundary between Ghostscript font code and the TrueType parser/hinter.

Risks: the memory and reader interfaces are callback-driven; implementers must honor allocation ownership and glyph buffer release contracts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfoutl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfsfnt.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfsfnt.h

Purpose: sfnt/TrueType table structure and constant definitions.

Key contents:
- Includes `stdint_.h` and defines exact-size TrueType aliases (`uint8`, `int16`, `uint32`, etc.).
- Defines `BigDate`, `sfnt_DirectoryEntry`, `sfnt_OffsetTable`, header flags, and sfnt constants.
- Defines structures for font header, horizontal/vertical metrics headers, max profile, glyph metrics, cmap directory/platform entries, name records, naming table, device metrics, PostScript info, subheaders, and font table info.
- Defines outline flag bits (`ONCURVE`, `XSHORT`, `YSHORT`, `REPEAT_FLAGS`, coordinate flags).
- Defines component glyph flags (`ARG_1_AND_2_ARE_WORDS`, `ARGS_ARE_XY_VALUES`, scaling flags, `MORE_COMPONENTS`, `WE_HAVE_INSTRUCTIONS`, `USE_MY_METRICS`).
- Defines platform enums and reversed four-character table tags for this code’s integer representation.
- Defines `RAW_TRUE_TYPE_SIZE`.

Dependencies: `stdint_.h`.

Integration notes: parsed by `ttfmain.c` and helper code through offsets and flag constants.

Risks: several structs describe on-disk layouts but parsing in this code uses explicit big-endian reader functions rather than direct struct casts; direct casting would be unsafe across alignment/endian differences.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfsfnt.h -->