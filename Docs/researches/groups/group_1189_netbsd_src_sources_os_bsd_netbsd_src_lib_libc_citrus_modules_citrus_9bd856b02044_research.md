# Group Research: group_1189_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_citrus_modules_citrus_9bd856b02044

Scope: subset A from `Docs/research_subset_a.md`, covering the listed NetBSD libc citrus and compatibility files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.c

## Scope

Implements the Citrus `mapper_zone` mapper module. It maps integer code indices only when they fall inside configured row/column zones, optionally applying row and column offsets.

## APIs And Behavior

- Exports mapper operations through `_citrus_mapper_zone_mapper_getops()`.
- Parses mapper variables in either single-column form or `rowzone/colzone/bits` form.
- Accepts offset specifications after `:`, with signed row/column offsets.
- `_citrus_mapper_zone_mapper_convert()` splits source indices by `mz_col_bits`, validates row/column membership, applies offsets, and returns either success or `_CITRUS_MAPPER_CONVERT_NONIDENTICAL`.
- Declares itself stateless with one source and one destination index per conversion.

## Dependencies

Uses Citrus mapper/module interfaces, `_memstream`, `_region`, basic character helpers, and mapper traits.

## Risks And Invariants

- Zone ranges and offsets are bounds-checked so offset application does not cross the configured row/column bit width.
- `mz_col_bits` controls both source splitting and destination packing, so bit-width parsing errors would corrupt mappings.
- The module allocates `cm->cm_closure`; uninit is empty, so lifetime depends on the surrounding mapper framework behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.h

## Scope

Public header for the Citrus `mapper_zone` module.

## APIs

- Defines include guard `_CITRUS_MAPPER_ZONE_H_`.
- Declares the mapper getops entry point through `_CITRUS_MAPPER_GETOPS_FUNC(mapper_zone)` inside `__BEGIN_DECLS` / `__END_DECLS`.

## Dependencies And Invariants

- Requires Citrus mapper macro definitions from including context.
- Contains no data structures or inline behavior; ABI exposure is limited to the getops symbol.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_zone.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.c

## Scope

Implements the Citrus ctype/stdenc module for Microsoft Kanji / Shift-JIS style encodings, including optional JIS X 0213:2004 behavior.

## APIs And Behavior

- Provides Citrus ctype and stdenc operations via `citrus_ctype_template.h` and `citrus_stdenc_template.h`.
- Maintains `_MSKanjiState` with up to two buffered bytes.
- `_citrus_MSKanji_mbrtowc_priv()` decodes single-byte ASCII/Kana or two-byte MS Kanji sequences, returning restart on incomplete byte pairs.
- `_citrus_MSKanji_wcrtomb_priv()` validates and emits one- or two-byte sequences.
- Stdenc conversion maps wide characters into csid/index classes for ISO-646, Kana, Kanji/Gaiji, and JIS2004 plane behavior.
- Module init parses variables, including JIS2004 mode.

## Dependencies

Uses Citrus ctype/stdenc templates, `_bcs` helpers, `wchar_t`, and standard errno semantics.

## Risks And Invariants

- Lead-byte and trail-byte validation is central: accepted lead ranges are `0x81-0x9f` and `0xe0-0xfc`; accepted trailing ranges are `0x40-0x7e` and `0x80-0xfc`.
- Incomplete state must preserve buffered bytes and report `(size_t)-2`.
- Stdenc row/column arithmetic differs under JIS2004 mode and must match Shift-JIS plane layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.h

## Scope

Public header for the Citrus MSKanji encoding module.

## APIs

- Defines include guard `_CITRUS_MSKANJI_H_`.
- Declares ctype and stdenc getops functions through `_CITRUS_CTYPE_GETOPS_FUNC(MSKanji)` and `_CITRUS_STDENC_GETOPS_FUNC(MSKanji)`.

## Dependencies And Invariants

- Provides only module entry declarations; implementation details stay private in the `.c` file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_ues.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_ues.c

## Scope

Implements the Citrus ctype/stdenc module for Unicode escape sequences, supporting Java-style `\uXXXX` behavior and optional C99 `\UXXXXXXXX` behavior.

## APIs And Behavior

- State buffers up to 12 bytes, enough for surrogate-pair escape output.
- `_citrus_UES_mbrtowc_priv()` decodes raw/basic characters and escape sequences, handles incomplete escape state, and combines surrogate pairs in non-C99 mode.
- `_citrus_UES_wcrtomb_priv()` emits raw characters, `\uXXXX`, surrogate-pair `\uXXXX\uXXXX`, or C99 `\UXXXXXXXX` forms depending on mode and code point.
- Stdenc maps all valid characters into csid `0`.
- Module init parses `C99` from the variable string and sets `mb_cur_max` to 10 or 12.

## Dependencies

Uses Citrus ctype/stdenc templates, `_bcs` case-insensitive parsing, `wchar_t`, and errno conventions.

## Risks And Invariants

- C99 mode changes both accepted escape syntax and what counts as a basic unescaped character.
- Surrogates are rejected as standalone scalar values in C99 mode but are used internally for non-C99 surrogate-pair decoding.
- Restart handling depends on preserving partially-read escape bytes in `_UESState`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_ues.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_ues.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_ues.h

## Scope

Public header for the Citrus UES encoding module.

## APIs

- Defines include guard `_CITRUS_UES_H_`.
- Declares ctype and stdenc getops functions for `UES`.

## Dependencies And Invariants

- No implementation state is exposed; consumers only use module getops entry points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_ues.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf1632.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf1632.c

## Scope

Implements the Citrus stdenc module for UTF-16 and UTF-32, including BOM detection/emission, preferred endian selection, forced-endian mode, and surrogate-pair handling.

## APIs And Behavior

- `_citrus_UTF1632_mbrtowc_priv()` reads 2 or 4 bytes depending on UTF-16/UTF-32 mode, detects BOM unless forced, and decodes UTF-16 surrogate pairs.
- `_citrus_UTF1632_wcrtomb_priv()` emits an initial BOM unless forced-endian mode is active, then writes UTF-16 code units or UTF-32 words in current endian.
- `parse_variable()` recognizes `big`, `little`, `force`, and `utf32`.
- Module init sets maximum byte length to 6 for UTF-16 or 8 for UTF-32, accounting for initial BOM plus character bytes.
- Stdenc maps characters to csid `0`.

## Dependencies

Uses Citrus stdenc templates, `_bcs` parsing helpers, `machine/endian.h`, and standard wide-character types.

## Risks And Invariants

- `current_endian` is per-state and transitions from unknown to BOM-detected or preferred endian.
- UTF-16 low-surrogate validation is required after a high surrogate.
- UTF-32 rejects surrogate code points but does not otherwise deeply validate Unicode scalar upper bounds beyond code representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf1632.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf1632.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf1632.h

## Scope

Public header for the Citrus UTF1632 stdenc module.

## APIs

- Defines include guard `_CITRUS_UTF1632_H_`.
- Declares `_CITRUS_STDENC_GETOPS_FUNC(UTF1632)`.

## Dependencies And Invariants

- Header exposes only the stdenc module entry point; UTF-16/UTF-32 options are parsed privately by the implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf1632.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.c

## Scope

Implements the Citrus ctype/stdenc module for UTF-7, including direct characters, base64 shifted sequences, UTF-16 unit conversion, and state reset output.

## APIs And Behavior

- Maintains shift/base64 state in `_UTF7State`.
- `_citrus_UTF7_mbrtowc_priv()` decodes direct bytes and shifted base64 sequences, using UTF-16 intermediate units and surrogate-pair handling.
- `_citrus_UTF7_wcrtomb_priv()` emits direct characters when permitted, `+-` for literal plus, or shifted base64 sequences for encoded characters.
- `_citrus_UTF7_put_state_reset()` terminates an open shifted sequence when necessary.
- Stdenc maps all decoded characters into csid `0` and reports incomplete character/shift state.

## Dependencies

Uses Citrus ctype/stdenc templates, base64 helper logic internal to the file, and wide-character/errno APIs.

## Risks And Invariants

- UTF-7 is state-dependent; reset output is required to close shifted mode.
- Base64 bit-buffer accounting must preserve partial bits across calls.
- Surrogate handling must reject malformed high/low pairs while still supporting restart on incomplete input.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.h

## Scope

Public header for the Citrus UTF7 encoding module.

## APIs

- Defines include guard `_CITRUS_UTF7_H_`.
- Declares ctype and stdenc getops functions for `UTF7`.

## Dependencies And Invariants

- Exposes no conversion state or constants; all UTF-7 behavior is template-backed implementation detail.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf8.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf8.c

## Scope

Implements the Citrus ctype/stdenc module for UTF-8, including restartable multibyte decoding and wide-character encoding.

## APIs And Behavior

- Builds a byte-class/count table for UTF-8 sequence lengths.
- `_citrus_UTF8_mbrtowc_priv()` buffers partial sequences, determines expected length from the leading byte, validates continuation bytes, and produces a wide character.
- `_citrus_UTF8_wcrtomb_priv()` emits UTF-8 for wide characters up to the module’s supported range.
- Stdenc maps wide characters to csid `0`.
- State descriptor reports initial state when no bytes are buffered, otherwise incomplete character.

## Dependencies

Uses Citrus ctype/stdenc templates and standard wide-character/errno support.

## Risks And Invariants

- Correct restart behavior depends on retaining `chlen`, expected length, and accumulated bytes.
- Continuation-byte validation and overlong/invalid sequence handling are correctness-sensitive.
- `MB_CUR_MAX` is fixed at 6 for historical UTF-8 coverage, wider than modern Unicode scalar UTF-8.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf8.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf8.h

## Scope

Public header for the Citrus UTF8 encoding module.

## APIs

- Defines include guard `_CITRUS_UTF8_H_`.
- Declares ctype and stdenc getops functions for `UTF8`.

## Dependencies And Invariants

- Header is declaration-only; conversion tables and state handling are private to the implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf8.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_viqr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_viqr.c

## Scope

Implements the Citrus ctype/stdenc module for VIQR Vietnamese mnemonic encoding.

## APIs And Behavior

- Builds a mnemonic tree from RFC 1456 mappings and extension mappings at module initialization.
- `_citrus_VIQR_mbrtowc_priv()` walks mnemonic trie state, handles escape characters, and returns the longest valid mnemonic mapping.
- `_citrus_VIQR_wcrtomb_priv()` emits mnemonic strings for mapped characters and uses escape disambiguation for ambiguous literal bytes.
- `_citrus_VIQR_put_state_reset()` clears pending mnemonic/disambiguation state.
- Stdenc maps characters through csid `0`.

## Dependencies

Uses `TAILQ` for mnemonic child lists, dynamic allocation for mnemonic trie nodes, Citrus ctype/stdenc templates, and standard string/wide-character APIs.

## Risks And Invariants

- The mnemonic trie must be destroyed on module uninit to avoid leaks.
- Longest-prefix matching and escape disambiguation are central to reversible VIQR conversion.
- `mb_cur_max` is derived from the longest configured mnemonic and must stay within `MB_LEN_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_viqr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_viqr.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_viqr.h

## Scope

Public header for the Citrus VIQR encoding module.

## APIs

- Defines include guard `_CITRUS_VIQR_H_`.
- Declares ctype and stdenc getops functions for `VIQR`.

## Dependencies And Invariants

- All VIQR mnemonic data and trie structures remain private to the `.c` implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_viqr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_zw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_zw.c

## Scope

Implements the Citrus ctype/stdenc module for the ZW encoding, a stateful ASCII/GB2312-style encoding using `zW` shift sequences.

## APIs And Behavior

- Maintains `_ZWState` with charset state: `NONE`, `AMBIGIOUS`, `ASCII`, or `GB2312`.
- `_citrus_ZW_mbrtowc_priv()` decodes ASCII, recognizes `zW` entry into GB2312 mode, handles newline/NUL reset behavior, and decodes two-byte GB2312 indexes.
- `_citrus_ZW_wcrtomb_priv()` emits `zW` when entering GB2312 mode, encodes ASCII escapes inside GB2312 mode, and emits GB2312 pairs for non-ASCII values.
- `_citrus_ZW_put_state_reset()` emits newline to leave GB2312 mode when needed.
- Stdenc uses csid `0` for ASCII-range values and `1` for others.

## Dependencies

Uses Citrus ctype/stdenc templates and standard wide-character/errno APIs.

## Risks And Invariants

- State transitions around `z`, `zW`, newline, and NUL are subtle and affect stream synchronization.
- All encoded bytes are constrained to 7-bit values; bytes above `0x7f` are rejected.
- Reset output is required for stateful GB2312 mode.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_zw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_zw.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_zw.h

## Scope

Public header for the Citrus ZW encoding module.

## APIs

- Defines include guard `_CITRUS_ZW_H_`.
- Declares ctype and stdenc getops functions for `ZW`.

## Dependencies And Invariants

- Only module entry points are public; charset state is private to the implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_zw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/Makefile.inc

## Scope

Build fragment for libc 4.3BSD compatibility sources.

## Behavior

- Adds `compat-43` source search paths for architecture-specific and common compatibility code.
- Adds `creat.c`, `getdtablesize.c`, `gethostid.c`, `killpg.c`, `sethostid.c`, `setpgrp.c`, `setrgid.c`, `setruid.c`, and `sigcompat.c`.
- Adds `getwd.c` unless `AUDIT` is defined.
- Adds include path for `<compat/sys/signal.h>` when compiling `sigcompat.c`.
- Registers manual pages and mlinks for related compatibility APIs.

## Dependencies And Invariants

- Depends on NetBSD make variables such as `ARCHDIR`, `.CURDIR`, `NETBSDSRCDIR`, `SRCS`, `MAN`, and `MLINKS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/creat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/creat.c

## Scope

Compatibility implementation of `creat()`.

## Behavior

- Validates `path` with `_DIAGASSERT`.
- Calls `open(path, O_WRONLY | O_CREAT | O_TRUNC, mode)` and returns its result.

## Dependencies And Invariants

- Depends on `<fcntl.h>` `open()` flags.
- Preserves historical `creat()` semantics as a thin `open()` wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/creat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/getdtablesize.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/getdtablesize.c

## Scope

Compatibility implementation of `getdtablesize()`.

## Behavior

- Returns `(int)sysconf(_SC_OPEN_MAX)`.

## Dependencies And Invariants

- Uses libc namespace setup and `<unistd.h>`.
- Mirrors the old descriptor-table-size API through the modern `sysconf` query.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/getdtablesize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/gethostid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/gethostid.c

## Scope

Compatibility implementation of `gethostid()`.

## Behavior

- Reads `CTL_KERN.KERN_HOSTID` through `sysctl`.
- Returns `-1` if `sysctl` fails; otherwise returns the integer host ID as `long`.

## Dependencies And Invariants

- Depends on `<sys/sysctl.h>` and kernel `KERN_HOSTID`.
- Host ID is treated as a 32-bit integer despite the `long` return type.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/gethostid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/getwd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/getwd.c

## Scope

Compatibility implementation of unsafe historical `getwd()`.

## Behavior

- Emits a link-time warning recommending `getcwd()`.
- Calls `getcwd(buf, MAXPATHLEN)`.
- On failure, copies `strerror(errno)` into `buf` and returns `NULL`.

## Dependencies And Invariants

- Requires caller-provided `MAXPATHLEN` buffer.
- Preserves historical behavior of placing the error string in the supplied buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/getwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/killpg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/killpg.c

## Scope

Compatibility implementation of `killpg()`.

## Behavior

- Rejects process group `1` and values `<= INT_MIN` with `errno = ESRCH`.
- Sends signals by calling `kill(-pgid, sig)`.

## Dependencies And Invariants

- Uses negative PID semantics of `kill()` for process-group signaling.
- Guards against invalid negation and special process group behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/killpg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/sethostid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/sethostid.c

## Scope

Compatibility implementation of `sethostid()`.

## Behavior

- Casts the provided `long hostid` to `int`.
- Writes `CTL_KERN.KERN_HOSTID` through `sysctl`.
- Returns `-1` on failure, `0` on success.

## Dependencies And Invariants

- Depends on `<sys/sysctl.h>` and kernel permission checks for setting host ID.
- Truncates to the historical 32-bit host ID representation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/sethostid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/setpgrp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/setpgrp.c

## Scope

Compatibility implementation of two-argument `setpgrp()`.

## Behavior

- Calls `setpgid(pid, pgid)` and returns its result.

## Dependencies And Invariants

- Preserves old BSD API shape while delegating to POSIX process-group control.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/setpgrp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/setrgid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/setrgid.c

## Scope

Compatibility implementation of deprecated `setrgid()`.

## Behavior

- Emits a link-time deprecation warning.
- Calls `setregid(rgid, (gid_t)-1)` to change only the real group ID.

## Dependencies And Invariants

- Effective GID is intentionally left unchanged with `(gid_t)-1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/setrgid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/setruid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/setruid.c

## Scope

Compatibility implementation of deprecated `setruid()`.

## Behavior

- Emits a link-time deprecation warning.
- Calls `setreuid(ruid, (uid_t)-1)` to change only the real user ID.

## Dependencies And Invariants

- Effective UID is intentionally left unchanged with `(uid_t)-1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/setruid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/sigcompat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/sigcompat.c

## Scope

Implements 4.3BSD signal compatibility functions on top of modern `sigaction`, `sigprocmask`, and `sigsuspend`.

## APIs And Behavior

- Converts between `struct sigvec` and `struct sigaction` with `sv2sa()` and `sa2sv()`.
- `sigvec()` delegates to `sigaction()`, preserving old mask/flag layout.
- `sigsetmask()` sets the signal mask and returns the previous low-word mask.
- `sigblock()` blocks requested signal bits and returns the previous low-word mask.
- `sigpause()` builds a signal set from an integer mask and calls `sigsuspend()`.

## Dependencies And Invariants

- Includes `<compat/sys/signal.h>` for old `sigvec` definitions.
- Uses only `sa_mask.__bits[0]`, so this is intentionally limited to the old integer signal-mask ABI.
- Flips `SV_INTERRUPT` with modern restart semantics using xor conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat-43/sigcompat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile

## Scope

Standalone makefile for building the libc compatibility library component.

## Behavior

- Includes the parent libc `Makefile.inc`.
- Sets `LIB=cold`.
- Adds libc include and architecture include paths.
- Includes common compatibility subdirectory fragments for db, gen, locale, net, rpc, stdio, stdlib, and sys.
- Sets `COMPATARCHDIR` and `.PATH` for architecture-specific gen/sys sources.
- Finishes with `<bsd.lib.mk>`.

## Dependencies And Invariants

- Depends on NetBSD make variables `.CURDIR`, `ARCHSUBDIR`, `COMPATDIR`, and the compatibility subdirectory layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile.inc

## Scope

Main compatibility build fragment included by libc builds.

## Behavior

- Adds the kernel source include path for compatibility headers.
- Defines `COMPATARCHDIR`.
- Adds architecture-specific gen/sys paths.
- Includes compatibility fragments for db, locale, gen, net, rpc, stdio, stdlib, sys, time, and the selected architecture.

## Dependencies And Invariants

- The selected architecture fragment is loaded through `${COMPATARCHDIR}/Makefile.inc`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/Makefile.inc

## Scope

AArch64 compatibility architecture build fragment.

## Behavior

- Includes `${COMPATARCHDIR}/sys/Makefile.inc`.

## Dependencies And Invariants

- No gen or locale compatibility sources are added here; AArch64 compatibility work in this group is under `sys`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/Makefile.inc

## Scope

AArch64 compatibility syscall wrapper build fragment.

## Behavior

- Adds compatibility assembly sources for old `vfork`, SysV IPC controls, signal action/mask/pending/return/suspend, and quota control.
- Leaves `compat___sigtramp1.S` commented out.

## Dependencies And Invariants

- Source list must match kernel compatibility syscall names and AArch64 `SYS.h` wrapper macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_Ovfork.S

## Scope

AArch64 compatibility wrapper for old `vfork`.

## Behavior

- Emits a warning reference for compatibility `vfork()`.
- Defines `PSEUDO(vfork,__vfork14)`.

## Dependencies And Invariants

- Relies on `SYS.h` AArch64 syscall wrapper macros.
- Preserves old symbol while routing to `__vfork14`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___semctl.S

## Scope

AArch64 compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes the public libc symbol to the NetBSD 1.4-compatible semaphore control syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___sigreturn14.S

## Scope

AArch64 compatibility wrapper for `__sigreturn14`.

## Behavior

- Notes that register state must be preserved.
- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Signal return wrappers must not disturb user register state before entering the compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_msgctl.S

## Scope

AArch64 compatibility wrapper for `msgctl`.

## Behavior

- Emits a warning reference recommending `<sys/msg.h>`.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves old SysV message-control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_quotactl.S

## Scope

AArch64 compatibility wrapper for `quotactl`.

## Behavior

- Emits a warning reference recommending `<sys/quota.h>`.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes legacy libc symbol to the NetBSD 5.0-compatible quota syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_shmctl.S

## Scope

AArch64 compatibility wrapper for `shmctl`.

## Behavior

- Emits a warning reference recommending `<sys/shm.h>`.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves old SysV shared-memory control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigaction.S

## Scope

AArch64 compatibility wrapper for old `sigaction`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Routes to the NetBSD 1.3 signal action ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigpending.S

## Scope

AArch64 compatibility wrapper for old `sigpending`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigpending,compat_13_sigpending13)`.

## Dependencies And Invariants

- Uses the old integer signal-set ABI through the compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigprocmask.S

## Scope

AArch64 compatibility wrapper for old `sigprocmask`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigprocmask,compat_13_sigprocmask13)`.

## Dependencies And Invariants

- Bridges libc `sigprocmask` symbol to old signal-mask syscall ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigreturn.S

## Scope

AArch64 compatibility wrapper for old `sigreturn`.

## Behavior

- Defines compatibility signal-return syscall wrapper for `sigreturn`.
- Routes to `compat_13_sigreturn13`.

## Dependencies And Invariants

- Must preserve register state across the signal-return syscall boundary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigsuspend.S

## Scope

AArch64 compatibility wrapper for old `sigsuspend`.

## Behavior

- Emits a warning reference recommending `<signal.h>`.
- Defines `PSEUDO(sigsuspend,compat_13_sigsuspend13)`.

## Dependencies And Invariants

- Uses old signal mask representation through the NetBSD 1.3 compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/Makefile.inc

## Scope

Alpha compatibility architecture build fragment.

## Behavior

- Includes the Alpha compatibility syscall make fragment.

## Dependencies And Invariants

- The active source list for this group comes from `arch/alpha/sys/Makefile.inc`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/Makefile.inc

## Scope

Alpha compatibility syscall wrapper build fragment.

## Behavior

- Adds compatibility wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on Alpha assembly syscall conventions and `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_Ovfork.S

## Scope

Alpha compatibility wrapper for `vfork`.

## Behavior

- Defines `SYSCALL(vfork)` for the compatibility vfork symbol.

## Dependencies And Invariants

- Uses Alpha syscall wrapper macros; unlike newer arches, this file names the syscall directly as `vfork`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___semctl.S

## Scope

Alpha compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to the NetBSD 1.4 SysV semaphore compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigreturn14.S

## Scope

Alpha compatibility wrapper for `__sigreturn14`.

## Behavior

- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Preserves compatibility signal-return entry naming for old binaries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigtramp1.S

## Scope

Alpha old signal trampoline compatibility code.

## Behavior

- Provides the legacy signal trampoline entry used to return from old signal handlers.
- Bridges the user signal frame back into the kernel’s compatibility signal-return mechanism.

## Dependencies And Invariants

- Highly ABI-sensitive: stack/register layout must match old Alpha signal frame expectations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_msgctl.S

## Scope

Alpha compatibility wrapper for `msgctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves NetBSD 1.4 message-control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_quotactl.S

## Scope

Alpha compatibility wrapper for `quotactl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes to NetBSD 5.0 quota compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_shmctl.S

## Scope

Alpha compatibility wrapper for `shmctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves NetBSD 1.4 shared-memory control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigaction.S

## Scope

Alpha compatibility wrapper for old `sigaction`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Uses old NetBSD 1.3 signal-action ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigpending.S

## Scope

Alpha compatibility implementation of old `sigpending`.

## Behavior

- Implements architecture-specific handling rather than a simple `PSEUDO` line.
- Calls the compatibility `sigpending13` syscall and stores/returns the old signal mask as required by Alpha ABI.

## Dependencies And Invariants

- Must match Alpha calling convention for pointer arguments and return values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigprocmask.S

## Scope

Alpha compatibility implementation of old `sigprocmask`.

## Behavior

- Performs architecture-specific argument adaptation for old integer signal masks.
- Calls `compat_13_sigprocmask13` and stores the old mask when requested.

## Dependencies And Invariants

- Pointer-versus-value mask conversion must match old libc ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigreturn.S

## Scope

Alpha compatibility wrapper for old `sigreturn`.

## Behavior

- Defines `PSEUDO(sigreturn,compat_13_sigreturn13)`.

## Dependencies And Invariants

- Preserves the old signal-return syscall ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigsuspend.S

## Scope

Alpha compatibility implementation of old `sigsuspend`.

## Behavior

- Performs architecture-specific mask indirection for old signal-set ABI.
- Calls `compat_13_sigsuspend13`.

## Dependencies And Invariants

- Must pass the old integer mask value in the form expected by the compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/alpha/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/Makefile.inc

## Scope

ARM compatibility architecture build fragment.

## Behavior

- Includes the ARM compatibility syscall make fragment.

## Dependencies And Invariants

- All listed ARM compatibility files are selected through `arch/arm/sys/Makefile.inc`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/Makefile.inc

## Scope

ARM compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on ARM `SYS.h` and ARM EABI/APCS syscall conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_Ovfork.S

## Scope

ARM compatibility wrapper for `vfork`.

## Behavior

- Provides an explicit `ENTRY(vfork)`.
- Performs ARM-specific syscall sequence for old vfork compatibility.

## Dependencies And Invariants

- Must preserve the ABI expectations around parent/child return values from `vfork`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___semctl.S

## Scope

ARM compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to NetBSD 1.4 semaphore compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigreturn14.S

## Scope

ARM compatibility wrapper for `__sigreturn14`.

## Behavior

- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Signal return entry must preserve user register state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigtramp1.S

## Scope

ARM legacy signal trampoline.

## Behavior

- Defines `ENTRY(__sigtramp_sigcontext_1)`.
- Adapts the old signal frame and invokes the compatibility signal-return path.

## Dependencies And Invariants

- Stack frame layout and saved register locations must match old ARM signal delivery ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_msgctl.S

## Scope

ARM compatibility wrapper for `msgctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves old SysV message-control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_quotactl.S

## Scope

ARM compatibility wrapper for `quotactl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes to NetBSD 5.0 quota compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_shmctl.S

## Scope

ARM compatibility wrapper for `shmctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves old SysV shared-memory control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigaction.S

## Scope

ARM compatibility wrapper for old `sigaction`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Uses old NetBSD 1.3 signal action ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigpending.S

## Scope

ARM compatibility implementation of old `sigpending`.

## Behavior

- Defines explicit `ENTRY(sigpending)`.
- Calls the compatibility syscall and writes the returned integer mask through the user-provided pointer.

## Dependencies And Invariants

- Must adapt between old integer signal-mask ABI and pointer-based libc function shape.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigprocmask.S

## Scope

ARM compatibility implementation of old `sigprocmask`.

## Behavior

- Defines explicit `ENTRY(sigprocmask)`.
- Converts a signal-set pointer argument to the old integer mask value.
- Calls `compat_13_sigprocmask13` and stores the old mask if requested.

## Dependencies And Invariants

- Handles null new-mask pointer by using the old ABI’s equivalent no-change/block-empty behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigreturn.S

## Scope

ARM compatibility wrapper for old `sigreturn`.

## Behavior

- Defines `PSEUDO(sigreturn,compat_13_sigreturn13)`.

## Dependencies And Invariants

- Signal return must preserve restored user context semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigsuspend.S

## Scope

ARM compatibility implementation of old `sigsuspend`.

## Behavior

- Defines explicit `ENTRY(sigsuspend)`.
- Dereferences the old signal mask pointer and calls `compat_13_sigsuspend13`.

## Dependencies And Invariants

- Must pass the integer signal mask expected by the compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/arm/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/Makefile.inc

## Scope

HPPA compatibility architecture build fragment.

## Behavior

- Includes HPPA compatibility syscall build rules.

## Dependencies And Invariants

- HPPA additionally has a locale compatibility source in this group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/locale/compat_setlocale32.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/locale/compat_setlocale32.c

## Scope

HPPA 32-bit compatibility wrapper for `setlocale`.

## Behavior

- Provides compatibility glue for older HPPA locale ABI.
- Delegates locale selection to the modern libc locale implementation while preserving the old exported symbol/ABI surface.

## Dependencies And Invariants

- Exists because HPPA compatibility needs architecture-specific locale handling in addition to syscall wrappers.
- Correctness depends on matching old pointer/return ABI expectations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/locale/compat_setlocale32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/Makefile.inc

## Scope

HPPA compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on HPPA-specific syscall entry conventions in `SYS.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_Ovfork.S

## Scope

HPPA compatibility wrapper for `vfork`.

## Behavior

- Defines an HPPA `ENTRY(vfork,0)` and uses syscall wrapper machinery for vfork.
- Includes compatibility warning/reference behavior.

## Dependencies And Invariants

- Must follow HPPA return-value and branch conventions for fork-like syscalls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___semctl.S

## Scope

HPPA compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to old SysV semaphore control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigreturn14.S

## Scope

HPPA compatibility wrapper for `__sigreturn14`.

## Behavior

- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Preserves signal-return ABI and register state assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigtramp1.S

## Scope

HPPA legacy signal trampoline.

## Behavior

- Defines `ENTRY_NOPROFILE(__sigtramp_sigcontext_1,0)`.
- Reconstructs/uses the old signal frame and enters the signal-return path.
- Contains HPPA-specific instruction sequencing for trampoline execution.

## Dependencies And Invariants

- Stack layout, register preservation, and trampoline entry alignment are ABI-critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_msgctl.S

## Scope

HPPA compatibility wrapper for `msgctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves old SysV message-control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_quotactl.S

## Scope

HPPA compatibility wrapper for `quotactl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes to NetBSD 5.0 quota compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_shmctl.S

## Scope

HPPA compatibility wrapper for `shmctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves old SysV shared-memory control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigaction.S

## Scope

HPPA compatibility wrapper for old `sigaction`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Routes to NetBSD 1.3 signal action ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigpending.S

## Scope

HPPA compatibility implementation of old `sigpending`.

## Behavior

- Defines explicit `ENTRY(sigpending, 0)`.
- Calls compatibility syscall and stores the returned old mask through the caller pointer.

## Dependencies And Invariants

- Must obey HPPA register and return-value convention while adapting old signal mask ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigprocmask.S

## Scope

HPPA compatibility implementation of old `sigprocmask`.

## Behavior

- Defines explicit `ENTRY(sigprocmask, 0)`.
- Converts pointer-based mask arguments to old integer mask syscall arguments.
- Stores the previous mask when requested.

## Dependencies And Invariants

- Null mask behavior and old integer mask storage must match historical libc ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigreturn.S

## Scope

HPPA compatibility implementation of old `sigreturn`.

## Behavior

- Defines explicit `ENTRY(sigreturn, 0)`.
- Invokes compatibility signal-return syscall with HPPA-specific sequence.

## Dependencies And Invariants

- Must preserve user context restoration semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigsuspend.S

## Scope

HPPA compatibility implementation of old `sigsuspend`.

## Behavior

- Defines explicit `ENTRY(sigsuspend, 0)`.
- Adapts the caller’s mask pointer to the old integer-mask syscall ABI.

## Dependencies And Invariants

- Signal mask value passing must match `compat_13_sigsuspend13`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/Makefile.inc

## Scope

i386 compatibility architecture build fragment.

## Behavior

- Includes i386 compatibility syscall sources.
- Also participates in i386-specific compatibility source selection for old runtime ABI support.

## Dependencies And Invariants

- Depends on i386 `SYS.h`, assembly ABI, and selected compatibility gen/sys fragments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/Makefile.inc

## Scope

i386 compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Source list must align with i386 old syscall ABI and stack argument layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_Ovfork.S

## Scope

i386 compatibility implementation of old `vfork`.

## Behavior

- Defines explicit `ENTRY(vfork)`.
- Performs i386-specific syscall entry and parent/child return handling.
- Includes compatibility warning reference behavior.

## Dependencies And Invariants

- Fork-like return register conventions are ABI-sensitive on i386.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___semctl.S

## Scope

i386 compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to old SysV semaphore control syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigreturn14.S

## Scope

i386 compatibility wrapper for `__sigreturn14`.

## Behavior

- Customizes `ENTRY` profiling behavior to preserve register state.
- Defines `PSEUDO(__sigreturn14,compat_16___sigreturn14)`.

## Dependencies And Invariants

- Signal-return path must avoid clobbering restored register context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigtramp1.S

## Scope

i386 legacy signal trampoline.

## Behavior

- Provides old signal trampoline code for returning from sigcontext-based signal handlers.
- Arranges stack arguments for compatibility signal return.

## Dependencies And Invariants

- The trampoline’s stack layout must match old i386 signal frame construction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_msgctl.S

## Scope

i386 compatibility wrapper for `msgctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(msgctl,compat_14_msgctl)`.

## Dependencies And Invariants

- Preserves old SysV message-control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_quotactl.S

## Scope

i386 compatibility wrapper for `quotactl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes to NetBSD 5.0 quota compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_shmctl.S

## Scope

i386 compatibility wrapper for `shmctl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(shmctl,compat_14_shmctl)`.

## Dependencies And Invariants

- Preserves old SysV shared-memory control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigaction.S

## Scope

i386 compatibility wrapper for old `sigaction`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(sigaction,compat_13_sigaction13)`.

## Dependencies And Invariants

- Routes to NetBSD 1.3 signal action ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigpending.S

## Scope

i386 compatibility implementation of old `sigpending`.

## Behavior

- Uses `_SYSCALL(sigpending,compat_13_sigpending13)`.
- Stores returned old integer mask through the caller-provided pointer.
- Clears return register for success.

## Dependencies And Invariants

- Adapts old integer mask syscall result to modern pointer-return function shape.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigprocmask.S

## Scope

i386 compatibility implementation of old `sigprocmask`.

## Behavior

- Defines explicit `ENTRY(sigprocmask)`.
- Converts new-mask pointer into old integer mask argument.
- Calls `compat_13_sigprocmask13`.
- Stores old mask through `oset` when provided.

## Dependencies And Invariants

- Stack argument rewriting must match i386 calling convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigreturn.S

## Scope

i386 compatibility wrapper for old `sigreturn`.

## Behavior

- Customizes profiling entry behavior to preserve registers.
- Defines `PSEUDO(sigreturn,compat_13_sigreturn13)`.

## Dependencies And Invariants

- The signal-return path must not disturb user register state while entering the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigsuspend.S

## Scope

i386 compatibility implementation of old `sigsuspend`.

## Behavior

- Defines explicit `ENTRY(sigsuspend)`.
- Dereferences the signal mask pointer into the old integer argument slot.
- Calls `compat_13_sigsuspend13`.

## Dependencies And Invariants

- Stack mutation before `SYSTRAP` is required for the old syscall ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/i386/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/Makefile.inc

## Scope

IA64 compatibility architecture build fragment.

## Behavior

- Includes IA64 compatibility syscall build rules.

## Dependencies And Invariants

- IA64 has a smaller compatibility syscall source list than the other architectures in this group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/Makefile.inc

## Scope

IA64 compatibility syscall wrapper build fragment.

## Behavior

- Adds `compat_Ovfork.S`, `compat___semctl.S`, `compat_sigprocmask.S`, `compat_sigsuspend.S`, and `compat_quotactl.S`.

## Dependencies And Invariants

- Does not list the full signal/sysv-ipc compatibility set used by several other architectures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_Ovfork.S

## Scope

IA64 compatibility wrapper for `vfork`.

## Behavior

- Minimal wrapper defining `SYSCALL(vfork)`.

## Dependencies And Invariants

- Uses IA64 `SYS.h` syscall macro conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat___semctl.S

## Scope

IA64 compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to old SysV semaphore control compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_quotactl.S

## Scope

IA64 compatibility wrapper for `quotactl`.

## Behavior

- Emits compatibility warning reference.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes to NetBSD 5.0 quota compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigprocmask.S

## Scope

IA64 compatibility wrapper for old `sigprocmask`.

## Behavior

- Defines `PSEUDO(sigprocmask,compat_13_sigprocmask13)`.

## Dependencies And Invariants

- Uses the old NetBSD 1.3 signal-mask compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigsuspend.S

## Scope

IA64 compatibility wrapper for old `sigsuspend`.

## Behavior

- Defines `PSEUDO(sigsuspend,compat_13_sigsuspend13)`.

## Dependencies And Invariants

- Routes to old signal-mask suspend ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/ia64/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/Makefile.inc

## Scope

m68k compatibility architecture build fragment.

## Behavior

- Includes m68k compatibility syscall build rules.

## Dependencies And Invariants

- The active listed files are selected through the m68k syscall make fragment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/Makefile.inc

## Scope

m68k compatibility syscall wrapper build fragment.

## Behavior

- Adds wrappers for old vfork, SysV IPC controls, signal operations, signal trampoline, and quota control.

## Dependencies And Invariants

- Depends on m68k `SYS.h`, trap conventions, and stack-based syscall argument layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_Ovfork.S

## Scope

m68k compatibility implementation of old `vfork`.

## Behavior

- Defines explicit `ENTRY(vfork)`.
- Uses m68k-specific syscall/trap sequence for vfork.
- Handles fork-like return conventions for parent and child.

## Dependencies And Invariants

- Return register handling and stack preservation are ABI-sensitive for vfork.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___semctl.S

## Scope

m68k compatibility wrapper for `__semctl`.

## Behavior

- Defines `PSEUDO(__semctl,compat_14___semctl)`.

## Dependencies And Invariants

- Routes to the NetBSD 1.4 semaphore compatibility syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigreturn14.S

## Scope

m68k compatibility implementation of `__sigreturn14`.

## Behavior

- Defines explicit `ENTRY(__sigreturn14)`.
- Uses m68k trap-based signal-return path for `compat_16___sigreturn14`.

## Dependencies And Invariants

- Must preserve the user register image being restored by signal return.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigreturn14.S -->