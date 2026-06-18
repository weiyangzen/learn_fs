# Group Research: group_144_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_stat_h_sources_os__dfa6dd213909

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. I read all 29 listed files completely.

This group covers Ghostscript portability headers, core `ref` store macros, the generic stream package, zlib stream filters, and FreeType-derived TrueType outline/interpreter adapter code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stat_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stat_.h

Generic substitute for Unix `sys/stat.h`.

Key points:
- Includes `std.h` before any header that may include `sys/types.h`.
- Includes `<stat.h>` for Metrowerks, otherwise `<sys/stat.h>`.
- Defines `stat_blocks(psbuf)` with a Plan 9-inclusive fallback based on file size when `st_blocks` is unavailable.
- Maps Microsoft `_stat` to `stat`.
- Provides `stat_is_dir(stbuf)` across systems with or without `S_ISDIR`.
- Patches `S_ISCHR`, `S_ISREG`, `S_IRUSR`, and `S_IWUSR` when missing.

Dependencies and interactions:
- Used by Ghostscript platform/file code needing portable stat metadata.
- Plan 9 is explicitly handled in the no-`st_blocks` platform list.

Research relevance:
- This is portability glue that normalizes filesystem metadata tests across Unix, Plan 9, Windows, VMS, and older compilers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stat_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/std.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/std.h

Main standard definitions header for Ghostscript code.

Key points:
- Includes `stdpre.h` and generated `arch.h`.
- Defines lower-case compatibility aliases for architecture macros.
- Computes memory alignment requirements and type sizes.
- Defines `bits16`, `bits32`, signed/unsigned min/max constants, pointer min/max, and reliable arithmetic right shift macros.
- Declares Ghostscript output routing functions: `outwrite`, `errwrite`, `outflush`, `errflush`, `outprintf`, and `errprintf`.
- Defines `dprintf*`, `dlprintf*`, `eprintf*`, and `lprintf*` debugging/error-printing macro families.
- Declares program identification helpers and module init-proc macro.

Dependencies and interactions:
- Depends on `arch.h` for target layout/endian/compiler behavior.
- Exposes `gs_memory_t` as a forward type because output routing is memory-context aware.
- Used broadly across Ghostscript source before platform and system headers.

Research relevance:
- This is the central Ghostscript portability and diagnostics contract.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/std.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdint_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdint_.h

Generic substitute for C99 `stdint.h`.

Key points:
- Includes `std.h`.
- Uses real `<stdint.h>` when `HAVE_STDINT_H` is set, with a MacOS shortcut.
- Accepts stdint-like types from `sys/types.h` when `SYS_TYPES_HAS_STDINT_TYPES` is set.
- Provides platform-specific definitions for Win32/MSVC, OpenVMS, and Cygwin.
- Falls back to `arch.h`-derived typedefs for 8-, 16-, 32-, and 64-bit signed/unsigned integer types.

Dependencies and interactions:
- Used by jbig2dec headers, TrueType bytecode/interpreter code, and other code requiring exact-size integers.
- Relies on `ARCH_SIZEOF_*` from `arch.h`.

Research relevance:
- This protects bundled older code from missing C99 integer headers on legacy or non-Unix platforms.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdint_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdio_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdio_.h

Generic substitute for `stdio.h`.

Key points:
- Includes `std.h` before `<stdio.h>`.
- On old VMS, maps `unlink` to `delete`.
- Declares `unlink(const char *)` for systems where stdio may not provide it.
- On Plan 9, renames system `sclose` out of the way by mapping `sclose(s)` to `Sclose(s)` before Ghostscript’s stream `sclose`.
- Defines missing `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`.
- Maps MSVC `fdopen` and `fileno` to underscored variants.

Dependencies and interactions:
- Important for `stream.h`/`stream.c`, where Ghostscript defines its own `sclose`.
- Used throughout code that needs stdio plus Ghostscript’s portability setup.

Research relevance:
- Contains a direct Plan 9 compatibility fix for a stream API name collision.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdio_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpn.h

Deprecated pre-ANSI prototype macro header.

Key points:
- Defines `P0()` through `P16(...)`.
- Comments explain these formerly supported traditional C compilers by hiding argument lists.
- Current definitions preserve typed parameter lists because pre-ANSI compilers are no longer supported.
- Marked deprecated and not intended for new code.

Dependencies and interactions:
- Included by `stdpre.h` for legacy source compatibility.

Research relevance:
- Small historical compatibility layer that keeps older Ghostscript declarations buildable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpre.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpre.h

Standard definitions that do not require `arch.h`.

Key points:
- Normalizes compiler/platform feature macros such as `__MSDOS__`, `__OSF__`, `SYSV`, `__SVR3`, and `__PROTOTYPES__`.
- Provides fallbacks for `__FILE__`, `__LINE__`, `const`, `volatile`, and `inline`.
- Defines `extern_inline` policy, `DISCARD`, `size_of`, `far_data`, `countof`, `offset_of`, and `ALIGNMENT_MOD`.
- Defines Ghostscript short unsigned aliases: `byte`, `uchar`, `ushort`, `uint`, and `ulong`.
- Includes `<sys/types.h>` behind temporary macro renames to avoid type-name clashes.
- Defines portable `bool`, `true`, `false`, pointer comparison macros, `min`, `max`, `ROUND_UP`, `ROUND_DOWN`, `floatp`, `BEGIN`/`END`, `DO_NOTHING`, and `client_name_t`.
- Defines `public`/`private` conventions and includes `stdpn.h`.
- Defines portable `exit_OK` and `exit_FAILED`, with VMS special handling.

Dependencies and interactions:
- Included before most Ghostscript headers.
- Its requirement to include `std.h` before headers using `sys/types.h` drives wrappers like `stat_.h`, `stdio_.h`, `string_.h`, and `time_.h`.

Research relevance:
- Foundational portability layer for old C compilers, system headers, pointer ordering, basic types, and Ghostscript coding conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stdpre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/store.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/store.h

Assignment and constructor macros for Ghostscript interpreter `ref` objects.

Key points:
- Includes `ialloc.h` and `idosave.h`.
- Defines `ref_assign` and `ref_assign_inline`, with old compiler-specific tuning.
- Implements save/restore-aware assignment:
  - `ref_must_save*`
  - `ref_do_save*`
  - `ref_save*`
  - `ref_mark_new*`
  - `ref_assign_new*`
  - `ref_assign_old*`
- Provides debug fill patterns for partially initialized refs under `DEBUG`.
- Defines generic constructors:
  - `make_t`, `make_ta`
  - `make_tv`
  - `make_tav`
  - `make_tasv`
- Defines type-specific constructors for booleans, integers, marks, nulls, operators, reals, arrays, strings, structs, and array-structs.
- Distinguishes stack stores, new-object stores, and old-object stores that require save tracking.

Dependencies and interactions:
- Relies on interpreter memory masks from `idmemory`/`gs_ref_memory_t`.
- Used throughout interpreter code when writing refs into VM-managed composite objects.

Research relevance:
- Central correctness layer for PostScript VM save/restore and local/global allocation tracking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/store.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.c

Implements Ghostscript’s generic stream package core.

Key behavior:
- Defines GC descriptors and relocation for `stream`, including buffer/string pointers, filter links, interpreter file-list links, state, and file name.
- Finalizer closes only valid non-temporary file streams to avoid freeing non-file stream storage during GC finalization.
- Implements allocation and initialization:
  - `s_init`
  - `s_alloc`
  - `s_init_state`
  - `s_alloc_state`
  - `s_std_init`
- Manages stream file names with copied, null-terminated storage through `ssetfilename` and `sfilename`.
- Provides standard no-op/reset/flush/close/switch helpers.
- `s_disable` invalidates a stream, clears GC-visible links, resets state, and frees the copied filename.
- Implements filter flushing/closing, including `CloseTarget` propagation via `close_strm`.
- Provides generic API functions: `savailable`, `stell`, `spseek`, `sswitch`, `sclose`, `spgetcc`, `spputc`, `sungetc`, `sgets`, `sputs`, `spskip`, and `sreadline`.
- `spgetcc` preserves filter read-ahead by honoring `min_left` and can close at EOD.
- `sgets` can bypass the stream buffer for large reads when template guarantees permit.
- `sreadline` handles CR/LF variants, optional prompts, fixed or growable buffers, and stdin-specific EOL behavior.
- `sreadbuf` and `swritebuf` traverse filter pipelines by temporarily reversing `strm` links, updating `end_status` while unwinding.
- `stream_compact` moves unread data to the bottom of the buffer and advances logical position.
- Implements string read/write streams, reusable string streams, and a position-only write stream.
- Implements filter construction and teardown:
  - `s_init_filter`
  - `s_add_filter`
  - `s_close_filters`
- Defines NullEncode/NullDecode templates using `stream_move`.

Dependencies and interactions:
- Includes `stdio_.h`, `memory_.h`, `gdebug.h`, `gpcheck.h`, `stream.h`, and `strimpl.h`.
- File stream constructors declared in `stream.h` are implemented elsewhere (`sfxstdio.c`/`sfxfd.c`), not in this file.
- Used by interpreter filters, file objects, image data sources, compression filters, and output devices.

Research relevance:
- Core buffering and filter-pipeline engine. Correct EOD/read-ahead behavior here affects all PostScript/PDF stream consumers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.h

Public definition of Ghostscript streams.

Key points:
- Defines `stream_procs`, the virtual procedure table for availability, seek, reset, flush, close, process, and mode switching.
- Exposes `struct stream_s` for performance-sensitive clients.
- Stream state includes:
  - common stream state
  - read/write cursors
  - buffer pointer/size metadata
  - `end_status`
  - access modes
  - optional `cbuf_string`
  - logical position
  - stream procedure table
  - underlying stream for filters
  - temporary-stream flags
  - interpreter read/write IDs
  - file-list links
  - `CloseSource`/`CloseTarget` behavior
  - embedded stdio file state and subfile limits
- Defines mode and validity macros: `s_is_valid`, `s_is_reading`, `s_is_writing`, `s_can_seek`.
- Defines fast byte read/write macros `sgetc` and `sputc`.
- Declares buffer APIs, skip/seek APIs, inline read macros, allocation/init routines, string/file stream constructors, filename helpers, standard procedures, filter helpers, and NullEncode/Decode templates.
- `sbuf_min_left` encodes the filter read-ahead contract.

Dependencies and interactions:
- Includes `scommon.h` and `srdline.h`.
- Requires stdio setup through `stdio_.h` in implementation/users.
- Consumed by filters, file objects, devices, and data decoders.

Research relevance:
- This header is the stream ABI for the Ghostscript interpreter/library.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/stream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/strimpl.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/strimpl.h

Definitions for stream implementors.

Key points:
- Documents the `process` procedure contract in detail.
- Process return values:
  - `EOFC`: end of data
  - `ERRC`: syntax/error
  - `0`: need more input
  - `1`: need more output space
- Explains special `last = 1` handling for encoders when no more input will arrive.
- Documents stricter EOD/read-ahead behavior required for decoding filters.
- Notes that decoders requiring explicit EOD should set `min_left = 1`.
- Defines `stream_template_s` fields:
  - state descriptor
  - init procedure
  - process procedure
  - minimum input/output sizes
  - release procedure
  - parameter/default pointer initializer
  - reinit procedure
- Declares `stream_move`.
- Declares `s_hex_process` and `hex_syntax`.

Dependencies and interactions:
- Includes `scommon.h`, `gstypes.h`, and `gsstruct.h`.
- Used by all concrete stream filters and by `stream.c`.

Research relevance:
- This is the implementor-facing contract that keeps all filters compatible with Ghostscript’s pipeline engine.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/strimpl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/string_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/string_.h

Generic substitute for Unix `string.h`.

Key points:
- Includes `std.h` before system headers.
- Uses `<strings.h>` and maps `strchr` to `index` for `BSD4_2`.
- Otherwise includes `<string.h>`.
- Supports `MEMORY__NEED_MEMMOVE` by mapping `memmove` to `gs_memmove`.
- Patches Think C `strlen` return handling.

Dependencies and interactions:
- Used by code needing string/memory functions while respecting Ghostscript header ordering rules.

Research relevance:
- Small portability wrapper around system string APIs and Ghostscript’s fallback `memmove`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/string_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibc.c

Common code for zlib encode/decode stream filters.

Key behavior:
- Defines structure descriptors for zlib block tracking, dynamic state, and public zlib stream state.
- `s_zlib_set_defaults` sets zlib parameters:
  - `windowBits = MAX_WBITS`
  - wrapper enabled
  - default compression level/method/strategy
  - `memLevel = min(MAX_MEM_LEVEL, 8)`
  - clears dynamic pointer
- `s_zlib_alloc_dynamic_state` allocates immovable zlib dynamic state, installs `s_zlib_alloc`/`s_zlib_free` callbacks into `z_stream`, and links the Ghostscript allocator.
- `s_zlib_free_dynamic_state` frees the dynamic state object.
- `s_zlib_alloc` allocates zlib data from `stable_memory`, records each block in a doubly linked list, and returns zlib-compatible pointers.
- `s_zlib_free` frees data, finds/removes the recorded block, and logs if zlib frees unrecorded data.

Dependencies and interactions:
- Includes Ghostscript memory/GC headers, `strimpl.h`, `szlibxx.h`, and `zconf.h`.
- Shared by `szlibd.c` and `szlibe.c`.

Research relevance:
- Bridges zlib’s allocator model into Ghostscript’s movable/GC-aware memory world by keeping immovable and traceable allocations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibd.c

zlib decoding/decompression filter stream.

Key behavior:
- `s_zlibD_init` allocates dynamic state and calls `inflateInit2`, using negative `windowBits` when `no_wrapper` is set.
- Sets `st->min_left = 1` for decoding read-ahead.
- `s_zlibD_reset` calls `inflateReset`.
- `s_zlibD_process` maps stream cursors into `z_stream`, avoids `Z_BUF_ERROR` on empty input/full output, and calls `inflate(Z_PARTIAL_FLUSH)`.
- Special-cases a known JAWS PDF generator empty-stream byte sequence and returns `EOFC`.
- Returns stream statuses from zlib results: `Z_OK`, `Z_STREAM_END`, or error.
- `s_zlibD_release` calls `inflateEnd` and frees dynamic state.
- Exports `s_zlibD_template`.

Dependencies and interactions:
- Uses `szlibxx.h` and Ghostscript stream template conventions.
- Consumed as the Flate/zlib decode filter implementation.

Research relevance:
- Decompression filter with Ghostscript stream status mapping and PDF compatibility workaround.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibe.c

zlib encoding/compression filter stream.

Key behavior:
- `s_zlibE_init` allocates dynamic state and calls `deflateInit2` with configured level, method, wrapper, memory level, and strategy.
- `s_zlibE_reset` calls `deflateReset`.
- `s_zlibE_process` maps stream cursors into `z_stream`, avoids `Z_BUF_ERROR`, and calls `deflate` with `Z_FINISH` on final flush or `Z_NO_FLUSH` otherwise.
- Maps `Z_OK` to need-input/need-output stream statuses and `Z_STREAM_END` to successful final completion only when input is consumed.
- `s_zlibE_release` calls `deflateEnd` and frees dynamic state.
- Exports `s_zlibE_template`.

Dependencies and interactions:
- Uses `szlibxx.h` and the common allocator/defaults from `szlibc.c`.

Research relevance:
- Compression filter implementation that adapts zlib’s streaming API to Ghostscript’s process-procedure contract.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibx.h

Public zlib stream state definition.

Key points:
- Forward-declares `zlib_dynamic_state_t`.
- Defines `stream_zlib_state` with common stream state plus:
  - `windowBits`
  - `no_wrapper`
  - compression `level`
  - `method`
  - `memLevel`
  - `strategy`
  - dynamic state pointer
- Defines the public GC descriptor macro for zlib stream state.
- Declares `s_zlibD_template` and `s_zlibE_template`.
- Declares shared `s_zlib_set_defaults`.

Dependencies and interactions:
- Included by zlib encoder/decoder users and `szlibxx.h`.

Research relevance:
- Public state contract for Ghostscript zlib filters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibxx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibxx.h

Private implementation definitions for the zlib interface.

Key points:
- Includes `szlibx.h` and zlib’s `zlib.h`.
- Documents why zlib internal allocations must be immovable and GC-traceable.
- Defines `zlib_block_t`, a linked-list node recording each zlib allocation.
- Defines `zlib_dynamic_state_t` with:
  - Ghostscript memory pointer
  - block list
  - embedded `z_stream`
- Provides GC descriptor macros for block and dynamic state structures.
- Declares zlib allocation/free callbacks and dynamic-state allocation/free helpers.

Dependencies and interactions:
- Must be compiled with zlib include path.
- Used only by common/encode/decode zlib filter implementation.

Research relevance:
- Internal memory-safety layer for using zlib inside Ghostscript’s allocator/GC constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibxx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/time_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/time_.h

Generic substitute for Unix `sys/time.h`.

Key points:
- Includes `std.h` and build-generated `gconfig_.h`.
- Includes `<sys/time.h>` when `HAVE_SYS_TIME_H` is set.
- For Plan 9, SCO, AIX, Sequent DYNIX/ptx, GCC/glibc, and Intel compiler cases, also includes `<time.h>`.
- Without `sys/time.h`, includes `<time.h>` and defines fallback `struct timeval` and `struct timezone` where needed.
- Defines `gettimeofday_no_timezone` for SVR4.0.
- Includes `<sys/times.h>` when available and defines `use_times_for_usertime`.
- Supplies fallback `CLK_TCK = 100` when missing.

Dependencies and interactions:
- Used by platform timing code such as user-time and wall-clock helpers.
- Plan 9 is explicitly listed in the dual `sys/time.h` + `time.h` inclusion path.

Research relevance:
- Portability wrapper for time APIs across Unix-like, Plan 9, and legacy environments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/time_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.c

FreeType-derived arithmetic routines for TrueType processing.

Key behavior:
- Provides a root-estimate lookup table used by square-root calculations.
- With native `LONG64`, implements:
  - `MulDiv`
  - `MulDiv_Round`
  - `Order64`
  - `Sqrt64`
- Without native 64-bit integers, implements manual 64-bit arithmetic:
  - `Neg64__`
  - `Add64`
  - `Sub64`
  - `MulTo64`
  - `Div64by32`
  - `Order64`
  - `Sqrt64`
- Handles signs explicitly and clamps divide overflow to signed 32-bit extrema.
- Contains unused `Order32`/`Sqrt32` under `#if 0`.

Dependencies and interactions:
- Includes `ttmisc.h` and `ttcalc.h`.
- Used by TrueType scaling, transforms, fixed-point multiplication/division, and outline construction.

Research relevance:
- Critical numeric substrate for fixed-point glyph transforms on platforms with or without native 64-bit arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.h

Header for TrueType arithmetic computations.

Key points:
- Includes `ttcommon.h` and `tttypes.h`.
- Defines exact 16-bit and 32-bit integer aliases from `SIZEOF_INT`/`SIZEOF_LONG`.
- Detects native 64-bit support through 8-byte `long`, optional GCC `long long`, or MSVC `__int64`.
- In `LONG64` mode, maps 64-bit operations to native expressions.
- Otherwise defines `Int64` as `{ lo, hi }` and maps macros to helper functions.
- Declares multiplication/division, 64-bit add/sub/mul/div/order/sqrt helpers as appropriate.
- Defines fixed-point conversion macros:
  - `MUL_FIXED`
  - `INT_TO_F26DOT6`
  - `INT_TO_F2DOT14`
  - `INT_TO_FIXED`
  - `F2DOT14_TO_FIXED`
  - `FLOAT_TO_FIXED`
  - `ROUND_F26DOT6`

Dependencies and interactions:
- Used by `ttfmain.c` and FreeType-derived TrueType internals.

Research relevance:
- Public arithmetic interface for TrueType fixed-point math.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcommon.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcommon.h

FreeType internal symbol-renaming header.

Key points:
- When `TT_PREFIX_ALL_NAMES` is defined, maps many internal names to `FT*`-prefixed equivalents.
- Covers modules such as:
  - `ttcalc`
  - lists/cache/error/mutex
  - raster
  - cmap
  - object/context/instance/face/glyph handling
  - TrueType table loading
  - glyph loading
  - interpreter
  - extensions
  - kerning
- Does not rename external `TT_` API functions.

Dependencies and interactions:
- Helps avoid link-time collisions when multiple FreeType-derived components or libraries are present.

Research relevance:
- Namespacing compatibility layer for embedded FreeType-derived code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconf.h

Configuration header for Ghostscript’s TrueType interpreter.

Key points:
- Modified from FreeType configuration.
- Defines `WORDS_BIGENDIAN` from `ARCH_IS_BIG_ENDIAN`.
- Defines `HAVE_MEMCPY`.
- Leaves many platform features undefined: `mmap`, ANSI headers, `getpagesize`, `valloc`, `fcntl.h`, `unistd.h`, `getopt.h`, `conio.h`, and `basename`.
- Defines `SIZEOF_INT` and `SIZEOF_LONG` from Ghostscript `ARCH_LOG2_SIZEOF_*`.

Dependencies and interactions:
- Included by `ttconfig.h`.
- Ties FreeType-derived code to Ghostscript’s generated architecture configuration.

Research relevance:
- Build-configuration adapter between Ghostscript portability macros and imported FreeType code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconfig.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconfig.h

TrueType configuration settings, modified from FreeType.

Key points:
- Includes `ttconf.h`.
- Comments state Ghostscript cut out the TrueType instruction interpreter, though this tree still contains interpreter-related interfaces/adapters.
- Leaves debugging and optional GCC 64-bit mode disabled by default.
- Defines `ALIGNMENT 8`.
- Enables `SECURE_COMPUTATIONS`.
- Enables `IGNORE_FILL_FLOW` so invalid contour orientation is still handled.
- Defines `Print(format, ap)` to `vfprintf(stderr, ...)` unless supplied externally.
- Computes FreeType byte-order constants from `WORDS_BIGENDIAN`.
- Enables `LOOSE_ACCESS` for big-endian non-bus-error systems.
- Leaves thread-safe/reentrant/static interpreter/static raster options undefined.
- Defines `TT_EXTEND_ENGINE`.

Dependencies and interactions:
- Used by FreeType-derived TrueType internals.
- Pulls architecture data through `ttconf.h`.

Research relevance:
- Controls numeric, raster, byte-order, threading, and extension behavior for embedded TrueType support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.c

TrueType font input helper routines.

Key behavior:
- Implements big-endian scalar reads through abstract `ttfReader` callbacks:
  - `ttfReader__Byte`
  - `ttfReader__SignedByte`
  - `ttfReader__Short`
  - `ttfReader__UShort`
  - `ttfReader__UInt`
  - `ttfReader__Int`
- Reads raw bytes through `r->Read`.
- Converts 2- and 4-byte values from TrueType big-endian order into host integers.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttfsfnt.h`, and `ttfinp.h`.
- Used heavily by `ttfmain.c` table and glyph parsing.

Research relevance:
- Small but central endian-safe input layer for SFNT/TrueType parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.h

Declarations for TrueType input helpers.

Key points:
- Declares byte, signed-byte, unsigned-short, unsigned-int, signed-short, and signed-int reader helpers.
- Assumes `ttfReader` is already declared by `ttfoutl.h`.

Dependencies and interactions:
- Used by TrueType parser code needing typed big-endian reads.

Research relevance:
- Thin header for the TrueType reader convenience API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmain.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmain.c

FreeType interface adapter for Ghostscript TrueType outline extraction.

Key behavior:
- Defines fixed/floating transform helpers for F26.6 and 16.16 values.
- Maps SFNT table names to `ttfFont` table pointer fields.
- Implements `TT_Set_Instance_CharSizes`, setting instance scale, ppem, point size, integer scaling, and resetting the instance.
- `ttfInterpreter__obtain` creates or refcounts a shared interpreter capsule and allocates execution context.
- `ttfInterpreter__release` decrements lock, frees usage buffer, execution context, interpreter object, and memory wrapper.
- `ttfFont__init`/`ttfFont__finit` initialize and release font face/instance/context resources.
- `ttfFont__Open`:
  - handles TTC collections and plain TrueType headers
  - scans table directory
  - loads core table metadata from `head`, `maxp`, `hhea`, optional `vhea`
  - allocates compound-glyph usage storage
  - creates FreeType-derived face/context/instance structures
  - initializes CVT and instance metrics
  - maps FreeType errors to `FontError` values
- Glyph setup/teardown uses `Context_Load`/`Context_Save` and instruction-control logic.
- Provides helpers for mounting glyph zones, initializing subglyph records, and copying current/original glyph coordinates.
- `ttfOutliner__init` stores reader/export/font/orientation state.
- `ttfOutliner__BuildGlyphOutlineAux`:
  - reads horizontal or vertical metrics
  - supports metrics-only queries when outlines are disabled
  - loads glyph data through `ttfReader::LoadGlyph`
  - parses simple and compound glyphs
  - enforces point/contour limits
  - expands repeat flags and decodes relative X/Y coordinates
  - recursively builds compound subglyph outlines with bounded nesting storage
  - handles component transforms, anchor/offset placement, and `USE_MY_METRICS`
  - optionally runs glyph instructions through `Context_Run`
  - adds phantom points for hinting and width adjustment
  - reports malformed fonts, patented instructions, memory failures, and bad instructions
- `ttfOutliner__DrawGlyphOutline`:
  - exports width first
  - optionally exports raw points
  - converts TrueType quadratic curves to cubic Bezier callbacks
  - emits move/line/curve/close callbacks
  - skips 1- and 2-point contours
  - contains an `AVECTOR_BUG` workaround for outlier points beyond expanded bbox bounds
- `ttfOutliner__Outline` wraps glyph start/build/stop, applies design-grid post-transform scaling, and returns outline status without drawing directly.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttfmemd.h`, `ttfinp.h`, `ttfsfnt.h`, `ttobjs.h`, `ttinterp.h`, and `ttcalc.h`.
- Consumes abstract `ttfReader` and `ttfExport` APIs declared in `ttfoutl.h`.
- Uses FreeType-derived context/instance/face APIs and Ghostscript GC descriptors from `ttfmemd.c`.

Research relevance:
- Main bridge between TrueType/SFNT data and Ghostscript outline callbacks. It is the highest-level TrueType file in this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.c

GC memory structure descriptors for TrueType interpreter objects.

Key behavior:
- Defines public structure descriptors for:
  - `TFace`
  - `TInstance`
  - `TExecution_Context`
  - `ttfFont`
  - `ttfInterpreter`
- `TFace` descriptor traces reader, font, font program, CVT program, and CVT pointers.
- `TInstance` custom enum/reloc traces face, function/instruction definitions, code range bases, CVT, and storage.
- `TExecution_Context` custom enum/reloc traces current face, definitions, call stack, code ranges, storage, stack, glyph point arrays, twilight point arrays, and CVT.
- Comments mark some fields as local or never used and intentionally not GC-traced.
- `ttfFont` descriptor traces face, instance, execution context, and interpreter pointer.
- `ttfInterpreter` descriptor traces execution context, subglyph usage buffer, and memory wrapper.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttobjs.h`, `ttfmemd.h`, and `gsstruct.h`.
- Used by `ttfmain.c` allocations through `ttfMemory`.

Research relevance:
- Essential for keeping FreeType-derived TrueType data safe under Ghostscript’s moving GC.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.h

Header declaring TrueType GC structure descriptors.

Key points:
- Includes `gsstype.h`.
- Declares external structure descriptors:
  - `st_TFace`
  - `st_TInstance`
  - `st_TExecution_Context`
  - `st_ttfFont`
  - `st_ttfInterpreter`

Dependencies and interactions:
- Included by code that allocates these structures with Ghostscript’s typed allocator.

Research relevance:
- Descriptor declaration header for GC-aware TrueType object allocation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmemd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfoutl.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfoutl.h

TrueType instruction interpreter and outline extraction interface.

Key declarations:
- Forward-declares `TFace`, `TInstance`, `TExecution_Context`, and `ttfInterpreter`.
- Defines `FloatMatrix`, `FloatPoint`, `F26Dot6`, and `F26Dot6Point`.
- Defines abstract `ttfMemory` allocator API with byte allocation, structured allocation, and free callbacks.
- Defines `ttfInterpreter` capsule with execution context, subglyph usage stack, lock, and memory pointer.
- Defines `FontError` values covering missing tables/names, memory failure, unimplemented data, cmap/glyph absence, bad font data, patented code, and bad instructions.
- Defines abstract `ttfReader` callbacks:
  - EOF/read/seek/tell/error
  - glyph load/release
- Defines `ttfFont` table-pointer metadata, units/flags/counts/metric table info, interpreter objects, and debug callbacks.
- Declares `ttfFont__init`, `ttfFont__finit`, and `ttfFont__Open`.
- Defines `ttfExport` callbacks for moves, lines, curves, close, points, width, and debug paint.
- Declares interpreter obtain/release routines.
- Defines `ttfGlyphOutline` and `ttfOutliner`.
- Declares `ttfOutliner__init`, `ttfOutliner__Outline`, and `ttfOutliner__DrawGlyphOutline`.

Dependencies and interactions:
- Included by TrueType parser/adapter code and Ghostscript consumers that provide reader/export adapters.

Research relevance:
- Primary public interface for TrueType outline extraction in this Ghostscript source subset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfoutl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfsfnt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfsfnt.h

SFNT/TrueType table structure definitions.

Key points:
- Based on Apple `sfnt.h`, modified to use ISO C exact-size integer types via `stdint_.h`.
- Defines `uint8/int8`, `uint16/int16`, and `uint32/int32` aliases.
- Uses packing pragmas around table structures.
- Defines SFNT offset table and directory entry structures.
- Defines core TrueType table structures:
  - `sfnt_FontHeader`
  - horizontal/vertical metrics headers
  - `sfnt_maxProfileTable`
  - glyph metrics
  - cmap directory/platform/name/mapping structures
  - naming table records
  - device metrics
  - PostScript table info
- Defines glyph flag enums for simple outlines and component glyph packing.
- Defines cmap platform enum.
- Defines reversed-endian four-character table tags such as `head`, `hhea`, `loca`, `maxp`, `cvt `, `prep`, `glyf`, `hmtx`, `vmtx`, `cmap`, `fpgm`, `kern`, `hdmx`, `name`, and `post`.
- Defines `FontTableInfo` and `RAW_TRUE_TYPE_SIZE`.

Dependencies and interactions:
- Used by `ttfinp.c` and `ttfmain.c` for table offsets, field offsets, tags, and glyph flag decoding.

Research relevance:
- Structural map of the SFNT/TrueType binary format used by Ghostscript’s TrueType adapter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfsfnt.h -->