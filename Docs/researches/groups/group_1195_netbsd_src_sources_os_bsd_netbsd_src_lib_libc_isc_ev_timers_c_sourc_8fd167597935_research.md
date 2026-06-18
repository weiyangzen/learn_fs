# Group Research: group_1195_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_isc_ev_timers_c_sourc_8fd167597935

Scope checked against `Docs/research_subset_a.md`; all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/ev_timers.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/ev_timers.c

Read completely: 519 lines.

This file implements eventlib time helpers and, outside `_LIBC`, timer management for ISC eventlib. The always-built helpers construct, add, subtract, compare, and convert `timespec`/`timeval` values, and obtain current time using `clock_gettime` with optional monotonic time support or `gettimeofday` fallback.

The non-libc timer implementation stores `evTimer` objects in a heap ordered by due time. Public operations create, clear, reconfigure, reset, and touch ordinary or idle timers. Idle timers wrap user callbacks in an `idle_timer` object that tracks last activity and reschedules or fires based on `ctx->lastEventTime`.

Important interactions: depends on `eventlib_p.h` for `evContext_p`, allocation macros, timer structures, heap wrappers, debug printing, and `__evOptMonoTime`. Timer deletion while currently executing is deferred by setting interval to zero so event dispatch cleanup can safely drop it.

Security/reliability notes: input validation rejects negative or out-of-range nanoseconds, except HP-UX compatibility assumes unsigned fields. Timer IDs are raw internal pointers; stale or forged IDs are checked only by comparing heap slots against the pointer. Idle timer cleanup is delicate because it frees wrapper state and mutates interval from callback paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/ev_timers.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/eventlib_p.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/eventlib_p.h

Read completely: 283 lines.

This is eventlib's private header. It defines common error/allocation macros, debug memory fill behavior, private structures for connections, accepts, files, streams, timers, waits, and queued event records, plus the central `evContext_p` implementation structure.

The context aggregates current event state, debug output, connection/file lists, fd sets or poll arrays, stream queues, timer heap, last event time, and wait lists. When `USE_POLL` is enabled, it replaces fd-set macros with poll-backed emulation helpers.

Important interactions: `ev_timers.c`, stream/wait/file code, and event loop internals share these struct layouts. It remaps internal symbols such as `evPrintf`, `evCreateTimers`, `evDestroyTimers`, and `evFreeWait` onto `__ev*` names.

Security/reliability notes: this header exposes broad internal mutable state and raw linked-list/heap ownership. The `OKNEW`/`FREE` macros assume memcluster allocation sizes match exact object types. Poll/fd-set abstraction changes the semantics of `FD_*` macros in files that include this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/isc/eventlib_p.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/libcincludes.mk -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/libcincludes.mk

Read completely: 20 lines.

This makefile fragment selects the libc architecture include directory. It derives `LIBC_MACHINE_ARCH` and `LIBC_MACHINE_CPU`, checks for an architecture `SYS.h`, sets `ARCHSUBDIR`, and then defines `ARCHDIR`.

Important interactions: included by build pieces that need libc's architecture-specific include tree. It prefers `${MACHINE_ARCH}` over `${MACHINE_CPU}` when both have a `SYS.h`.

Security/reliability notes: no runtime behavior. Build failure is explicit through a `.BEGIN` target if no matching architecture directory exists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/libcincludes.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/Makefile.inc

Read completely: 75 lines.

This makefile fragment adds libc locale sources, man pages, and man-page links. It covers locale management, multibyte conversion, Unicode `uchar.h` conversion APIs, wide-character classification/translation, rune tables, and wide string numeric/collation/time functions.

It sets `.PATH` to architecture and generic locale directories, adds Citrus include paths for rune and UTF-32 conversion files, defines `WITH_RUNE`, and disables nonliteral format warnings for `wcsftime.c`.

Security/reliability notes: no runtime behavior. Build composition is important because several generated/template source files depend on compile-time include ordering and Citrus headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/__mb_cur_max.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/__mb_cur_max.c

Read completely: 41 lines.

This file defines two libc-wide multibyte length globals: `__mb_cur_max`, initialized to 1 for the C locale, and `__mb_len_max_runtime`, initialized to compile-time `MB_LEN_MAX`.

Important interactions: locale setup and multibyte conversion code use these values to expose or bound runtime multibyte lengths. `setlocale.c` resets `__mb_len_max_runtime` before locale changes.

Security/reliability notes: global mutable locale state can affect conversions process-wide. The file itself contains no logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/__mb_cur_max.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/__wctoint.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/__wctoint.h

Read completely: 79 lines.

This header defines inline `__wctoint`, mapping wide characters `0-9`, `A-Z`, and `a-z` to digit values `0..35`, returning `-1` for non-digits.

Important interactions: included by the `_wcstol.h` and `_wcstoul.h` templates and their concrete integer conversion wrappers. It deliberately avoids locale-dependent classification.

Security/reliability notes: no allocation or I/O. The conversion is ASCII-style only, which matches base conversion expectations for these libc functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/__wctoint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstod.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstod.h

Read completely: 146 lines.

This template implements `wcstof`, `wcstod`, and `wcstold` families. It skips wide whitespace, converts the remaining wide string to multibyte with `wcstombs_l`, calls the configured `strto*_l` function, and maps the resulting multibyte end pointer back to a wide-character end pointer.

Important interactions: concrete files define `_FUNCNAME`, `_RETURN_TYPE`, and `_STRTOD_FUNC` before including this template. It uses `_current_locale()` for non-`_l` wrappers and `setlocale_local.h` for locale access.

Security/reliability notes: handles conversion and allocation failure by returning zero and setting `endptr` to the original input. The end-pointer mapping has an explicit `XXX` assumption that each wide character is one byte in the converted portion, which can be wrong for multibyte encodings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstod.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstol.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstol.h

Read completely: 161 lines.

This template implements signed wide-string integer conversion for `wcstol`, `wcstoll`, and `wcstoimax`. It validates base, skips locale-aware whitespace, accepts optional sign and `0x` prefixes, auto-detects octal/decimal/hex when base is zero, and accumulates with cutoff/cutlim overflow checks.

Important interactions: concrete wrappers provide return type and min/max macros, and include `__wctoint.h` for digit mapping. The template emits both current-locale and explicit-locale entry points.

Security/reliability notes: overflow sets `errno = ERANGE` and saturates to min/max. Invalid base sets `EINVAL`. The parser is ASCII digit/letter based, not locale-specific for digits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstoul.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstoul.h

Read completely: 137 lines.

This template implements unsigned wide-string integer conversion for `wcstoul`, `wcstoull`, and `wcstoumax`. It validates base, skips whitespace, accepts optional sign and prefixes, accumulates unsigned values with overflow checks, and applies negation after parsing if a leading minus was present.

Important interactions: concrete wrappers define `_FUNCNAME`, `__UINT`, and `__UINT_MAX`. It shares digit conversion via `__wctoint.h` and locale retrieval via `setlocale_local.h`.

Security/reliability notes: overflow saturates to `__UINT_MAX` and sets `ERANGE`; invalid base sets `EINVAL`. Negative inputs are accepted by unsigned conversion semantics and wrapped after successful parse.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstoul.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans.c

Read completely: 106 lines.

This file implements `_towctrans_ext`, the extended-range wide-character translation helper. It returns `WEOF` unchanged, then binary-searches a `_WCTransEntry` extended map to translate non-cached runes.

Important interactions: `_wctrans_local.h` uses this as the slow path after cached translations. Case conversion APIs in `iswctype_mb.c` ultimately route through `_towctrans_priv`.

Security/reliability notes: assumes the `_WCTransEntry` and its range table are valid and sorted. The code comments note it assumes `wchar_t = int` when casting to `__nbrune_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans_local.h

Read completely: 60 lines.

This header declares `_towctrans_ext` and defines inline helpers for wide-character translation. `_towctrans_priv` uses the cached translation table for small runes and falls back to `_towctrans_ext`; `_wctrans_lower` and `_wctrans_upper` return the locale's lower/upper translation entries.

Important interactions: used by `_wctype.c`, `iswctype_mb.c`, and `rune.c` to share translation lookup logic.

Security/reliability notes: relies on diagnostic assertions that translation entries are initialized. No standalone runtime behavior beyond inline table access.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype.c

Read completely: 112 lines.

This file implements rune type lookup. `_runetype_priv` returns cached classification bits for small runes or binary-searches extended ranges for larger runes, supporting either per-rune type arrays or a uniform range map. `_iswctype_priv` masks the resulting bits with a `_WCTypeEntry`.

Important interactions: all `isw*` and width functions in `iswctype_mb.c` depend on these helpers. `rune.c` uses `_runetype_priv` while building byte-oriented ctype compatibility tables.

Security/reliability notes: assumes sorted and valid `_RuneRange` data loaded from locale files or default tables. Returns zero for `WEOF` and unknown ranges.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype_local.h

Read completely: 37 lines.

This header declares `_runetype_priv` and `_iswctype_priv`, the internal wide-character classification helpers.

Important interactions: included by classification, multibyte, and rune loading code that needs to query `_RuneLocale` classification data.

Security/reliability notes: declaration-only header with no direct runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/aliasname_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/aliasname_local.h

Read completely: 74 lines.

This header declares `__unaliasname` and defines inline `__isforcemapping`, which recognizes the case-insensitive literal `/FORCE` without using locale-sensitive string comparison.

Important interactions: `nb_lc_template.h` uses these helpers while resolving locale aliases from `locale.alias`, distinguishing force mappings from ordinary alias fallback behavior.

Security/reliability notes: `__isforcemapping` indexes fixed positions in `name` and assumes a valid NUL-terminated string. It intentionally avoids `strcasecmp` because locale lookup must not depend on the current locale.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/aliasname_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c16rtomb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c16rtomb.c

Read completely: 212 lines.

This file implements `c16rtomb` and `c16rtomb_l`, converting UTF-16 code units to the current locale's multibyte encoding. It stores pending high surrogates in a private state embedded in `mbstate_t`, combines valid surrogate pairs into a UTF-32 scalar, and delegates scalar output to `c32rtomb_l`.

Important interactions: uses `c32rtomb.h` to assert state-size compatibility and `setlocale_local.h` for `_current_locale()`. Null `ps` uses a static state as required by the C API, and null `s` emits a reset/null conversion into a local buffer.

Security/reliability notes: invalid surrogate ordering sets `errno = EILSEQ`. A null code unit discards any pending high surrogate and resets through `c32rtomb_l`. Static state for null `ps` is not thread-safe by standard allowance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c16rtomb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.c

Read completely: 229 lines.

This file implements `c32rtomb` and `c32rtomb_l`, converting a UTF-32 scalar value to the current locale's multibyte encoding. It rejects surrogate code points, opens a Citrus iconv converter from `utf-32le` to the locale `CODESET`, converts into a temporary buffer, decodes that as one wide character, then emits it with `wcrtomb_l` using the caller's conversion state.

Important interactions: depends on Citrus iconv internals and `nl_langinfo_l(CODESET, loc)`. It uses `le32enc`, `mbrtowc_l`, and `wcrtomb_l` as the bridge between Unicode scalar values and NetBSD's locale/wide-character machinery.

Security/reliability notes: iconv open failures are mapped to `EIO`; conversion errors propagate through `errno`. The file preserves `errno` on success. The comments flag unresolved questions about relying on iconv for surrogate rejection and combining-character behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.h

Read completely: 40 lines.

This header defines `struct c32rtombstate`, currently a one-byte dummy placeholder, with a comment that it must match the maximum conversion state actually used by `wcrtomb_l`.

Important interactions: `c16rtomb.c` and `c8rtomb.c` use this type only for compile-time assertions about how much private state can fit inside `mbstate_t`.

Security/reliability notes: the placeholder makes state sizing dependent on the current `wcrtomb_l` implementation. If `wcrtomb_l` grows private state, this header must be updated.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c32rtomb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c8rtomb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c8rtomb.c

Read completely: 228 lines.

This file implements `c8rtomb` and `c8rtomb_l`, converting UTF-8 code units to the current locale's multibyte encoding. It maintains a compact UTF-8 DFA state and partial scalar buffer inside `mbstate_t`; incomplete byte sequences produce no output until a complete scalar is accepted, then output is delegated to `c32rtomb_l`.

Important interactions: uses a locally defined class/state table inspired by Hoehrmann's UTF-8 decoder, plus `c32rtomb.h` for state-size assertions. Null `s` resets through a null code unit conversion.

Security/reliability notes: invalid UTF-8 transitions return `(size_t)-1` with `EILSEQ`. A null byte discards buffered UTF-8 input and emits a null scalar. Static state for null `ps` is allowed but not race-free.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/c8rtomb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/ctype_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/ctype_local.h

Read completely: 54 lines.

This header defines byte-oriented ctype cache sizes, compatibility classification bit masks, and declarations for the C locale ctype/toupper/tolower tables. Under `__BUILD_LEGACY`, it also declares legacy BSD ctype globals.

Important interactions: included by rune file/local headers and setlocale internals to connect wide/rune classification to traditional `ctype` table APIs.

Security/reliability notes: no executable logic. The fixed `_CTYPE_CACHE_SIZE` of 256 shapes cached rune and byte table behavior throughout the locale implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/ctype_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_collate.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_collate.c

Read completely: 53 lines.

This file instantiates the dummy locale-category template for `LC_COLLATE`. It defines `_PREFIX`, `_CATEGORY_ID`, and `_CATEGORY_NAME`, then includes `dummy_lc_template.h`.

Important interactions: `setlocale.c` registers `_dummy_LC_COLLATE_setlocale` for `LC_COLLATE`. Since real collation is not implemented here, wide collation functions also fall back to simple string behavior.

Security/reliability notes: only accepts C/POSIX or environment-resolved values through the template. No file loading or dynamic allocation beyond template behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_collate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_template.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_template.h

Read completely: 54 lines.

This template implements a simple `setlocale` function for categories that do not load external locale data. It resolves an empty name through environment variables, accepts only `C` or `POSIX`, updates the locale's `part_name`, and returns the active category name.

Important interactions: instantiated by `dummy_lc_collate.c`. It includes `generic_lc_template_decl.h` for the generated prototype form.

Security/reliability notes: rejects arbitrary locale names for dummy categories. It stores pointers to stable string literals rather than allocating new category data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_template.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/duplocale.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/duplocale.c

Read completely: 52 lines.

This file implements `duplocale` by allocating a new `struct _locale` and shallow-copying the source locale.

Important interactions: shares category implementation pointers and cache pointers with the source. `freelocale` later frees only the locale struct, not the pointed-to shared category data.

Security/reliability notes: there is no explicit NULL or special-locale validation here; callers must pass a valid `locale_t`. Shallow copying is consistent with the cache model but makes ownership shared.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/duplocale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.c

Read completely: 109 lines.

This file implements `__fix_locale_grouping_str`, converting textual locale grouping strings such as `3;3;-1` into POSIX grouping byte sequences. It edits the supplied string in place, skips semicolons, handles `-1` as `CHAR_MAX`, parses one- or two-digit group sizes, and returns a static no-grouping sequence for empty or invalid input.

Important interactions: used by locale category loaders to normalize numeric and monetary grouping fields from locale data files.

Security/reliability notes: the function casts away const and mutates the input buffer, so callers must pass writable storage unless they expect the static fallback. It assumes values are at most two decimal digits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.h

Read completely: 36 lines.

This header declares `__fix_locale_grouping_str`.

Important interactions: included by locale loaders that need to normalize grouping strings.

Security/reliability notes: declaration-only header. The mutating behavior is only visible from the implementation, not encoded in the prototype.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/freelocale.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/freelocale.c

Read completely: 51 lines.

This file implements `freelocale` by asserting the argument is not `LC_GLOBAL_LOCALE`, not `LC_C_LOCALE`, and not NULL, then freeing the locale object.

Important interactions: matches the shallow-allocation model of `newlocale`/`duplocale`; category implementations and caches are shared and not freed here.

Security/reliability notes: misuse is caught only by diagnostic assertions, which may be disabled. Passing special locale objects in release builds would be unsafe.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/freelocale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/generic_lc_all.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/generic_lc_all.c

Read completely: 117 lines.

This file implements `_generic_LC_ALL_setlocale`. It parses either a single locale name applied to all categories or a slash-separated per-category locale query string, calls each category's setlocale handler, and builds the composite `locale->query` string.

Important interactions: registered for `LC_ALL` by `setlocale.c`. It drives all category-specific handlers from `_find_category`, including dummy collate and Citrus-backed categories.

Security/reliability notes: it copies input into a fixed-size `head` buffer with `strlcpy` but does not explicitly check truncation. Slash parsing rejects malformed category counts. It returns NULL if no category load succeeds for a non-NULL request.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/generic_lc_all.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/generic_lc_template_decl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/generic_lc_template_decl.h

Read completely: 35 lines.

This header declares a template-generated `_PREFIX(setlocale)` function taking a locale name and `struct _locale *`.

Important interactions: included by generic and dummy locale templates to provide consistent prototypes.

Security/reliability notes: declaration-only header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/generic_lc_template_decl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/global_locale.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/global_locale.c

Read completely: 202 lines.

This file defines default C-locale category data, the shared `_C_cache`, the mutable global locale `_lc_global_locale`, and immutable `_lc_C_locale`. Defaults cover messages, monetary, numeric, time, rune/ctype, and `struct lconv` cache fields.

Important interactions: `_current_locale()` returns `_lc_global_locale`; `newlocale`, `setlocale`, `localeconv`, `nl_langinfo`, and category templates all rely on these baseline objects. The C cache also points at system error-list storage for locale-sensitive error message support.

Security/reliability notes: most fields point to static string literals or default locale objects. `_lc_global_locale` is mutable process-wide state and is not inherently synchronized.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/global_locale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/iswctype_mb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/iswctype_mb.c

Read completely: 235 lines.

This file implements locale-aware wide classification, translation, and width APIs. Macros generate `iswalnum_l` through `iswxdigit_l`, plus non-`_l` wrappers. Similar macros generate `towupper_l`/`towlower_l`. It also implements `wctype`, `wctrans`, `iswctype`, `towctrans`, `wcwidth`, and `wcswidth`.

Important interactions: uses `_RuneLocale` from `loc->part_impl[LC_CTYPE]`, `_iswctype_priv` for classification, `_towctrans_priv` for translations, and `_runetype_priv` for width data.

Security/reliability notes: null `wctype_t`/`wctrans_t` set `EINVAL`. `wctrans_l` appears to return `&rl->rl_wctype[i]` rather than `&rl->rl_wctrans[i]`, which is a notable type/logic risk for charmaps. Width accumulation uses `int` and does not check overflow.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/iswctype_mb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/localeconv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/localeconv.c

Read completely: 51 lines.

This file implements `localeconv` and `localeconv_l`. The current-locale wrapper delegates to `localeconv_l`, which returns a non-const pointer to the `struct lconv` cached inside `loc->cache`.

Important interactions: cache contents are built by `_setlocale_cache` in `setlocale.c` from monetary and numeric category implementations.

Security/reliability notes: returns internal cache storage with const cast, matching libc API expectations but exposing mutable-looking data backed by shared locale cache.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/localeconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/localeio.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/localeio.h

Read completely: 36 lines.

This header declares locale file I/O helpers: `_localeio_map_file`, `_localeio_unmap_file`, and `__loadlocale`.

Important interactions: category loaders and rune loading paths use these helpers to map and load external locale files.

Security/reliability notes: declaration-only header. The interface passes raw mapped memory and sizes, so callers must validate file formats.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/localeio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc16.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc16.c

Read completely: 213 lines.

This file implements `mbrtoc16` and `mbrtoc16_l`, decoding locale multibyte input into UTF-16 code units. It delegates scalar decoding to `mbrtoc32_l`; BMP scalars are returned directly, while non-BMP scalars are split into a high surrogate returned immediately and a saved low surrogate returned on the next call with `(size_t)-3`.

Important interactions: embeds a `mbrtoc32` state inside `mbstate_t` after a pending-surrogate field, with compile-time layout assertions.

Security/reliability notes: null `s` follows the standard reset behavior. Pending low surrogate delivery consumes no input. Static state for null `ps` is permitted but not race-free.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.c

Read completely: 257 lines.

This file implements `mbrtoc32` and `mbrtoc32_l`, decoding locale multibyte input to a UTF-32 scalar value. It opens a Citrus iconv converter from the locale `CODESET` to `utf-32le`, consumes one wide character with `mbrtowc_l`, re-encodes it to multibyte from an initial state, converts that to UTF-32LE, decodes the scalar, and rejects surrogate code points.

Important interactions: bridges NetBSD's wide-character conversion with Citrus iconv and `nl_langinfo_l(CODESET)`. The private state sizing is asserted against `mbrtoc32.h`.

Security/reliability notes: `n == 0` returns incomplete without invoking iconv. Iconv open failure maps to `EIO`; conversion errors propagate. The code preserves `errno` on success. A comment says “UTF-16LE” in one conversion comment, but the code uses UTF-32LE.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.h

Read completely: 40 lines.

This header defines `struct mbrtoc32state`, currently a one-byte dummy placeholder, with a note that it must match the maximum state actually used by `mbrtowc_l`.

Important interactions: `mbrtoc16.c` and `mbrtoc8.c` use it for compile-time `mbstate_t` layout assertions.

Security/reliability notes: if `mbrtowc_l` starts using more private state, this placeholder must be updated or the assertions may become misleading.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc8.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc8.c

Read completely: 226 lines.

This file implements `mbrtoc8` and `mbrtoc8_l`, decoding locale multibyte input into UTF-8 code units. It delegates scalar decoding to `mbrtoc32_l`, returns the first UTF-8 byte immediately, and buffers up to three trailing bytes for later `(size_t)-3` returns without consuming input.

Important interactions: embeds `mbrtoc32` state after UTF-8 output buffering in `mbstate_t`, with compile-time size/alignment assertions.

Security/reliability notes: rejects scalar values outside Unicode's UTF-8 range with `EILSEQ`. Pending trailing bytes are cleared as they are emitted. Static state for null `ps` is not race-free by standard allowance.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte.h

Read completely: 132 lines.

This header defines the private layout used to store `_RuneLocale *` and Citrus ctype state inside `mbstate_t`. It provides helpers to reinterpret `mbstate_t` as `_RuneState`, extract the rune locale, ctype object, and private state, initialize state, and lazily fix up state for a locale.

Important interactions: `multibyte_amd1.c` and `multibyte_c90.c` use these helpers for restartable and legacy multibyte APIs. The `_PRIVSIZE` value is passed to Citrus ctype open in `rune.c`.

Security/reliability notes: correctness depends on `mbstate_t` being large and aligned enough for the private state. `_fixup_ps` initializes state when the stored runelocale is NULL or forced.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_amd1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_amd1.c

Read completely: 258 lines.

This file implements restartable C95/C99-style multibyte APIs and related helpers: `mbrlen`, `mbsinit`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `wcrtomb`, `wcsrtombs`, `btowc`, `wctob`, and `_mb_cur_max_l`, with locale-aware `_l` variants.

Important interactions: wrappers mostly call Citrus ctype methods after `_fixup_ps` ensures `mbstate_t` is bound to the active rune locale. Byte/wide single-character conversion uses the locale's `rl_citrus_ctype` directly.

Security/reliability notes: Citrus errors are copied to `errno`, but return values come from the backend. State lifetime and locale binding depend on callers not reusing `mbstate_t` across incompatible locales without reset.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_amd1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_c90.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_c90.c

Read completely: 167 lines.

This file implements legacy C90 multibyte APIs and `wcsnrtombs`: `mblen`, `mbstowcs`, `mbtowc`, `wcstombs`, `wcsnrtombs`, and `wctomb`, with locale-aware variants.

Important interactions: non-restartable APIs call the locale's Citrus ctype directly. `wcsnrtombs_l` uses the restartable state helpers from `multibyte.h`.

Security/reliability notes: errors are surfaced through `errno` from Citrus. As with other wrappers, behavior relies on the ctype backend honoring libc conversion contracts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/multibyte_c90.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_messages_misc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_messages_misc.h

Read completely: 49 lines.

This header supplies template macros for the NetBSD `LC_MESSAGES` category: `_CATEGORY_TYPE` as `_MessagesLocale`, `_CATEGORY_ID` as `LC_MESSAGES`, and `_CATEGORY_NAME` as `"LC_MESSAGES"`. It also defines an empty `_PREFIX(update_global)` hook.

Important interactions: included before `nb_lc_template_decl.h` and `nb_lc_template.h` by the concrete messages category source.

Security/reliability notes: no standalone logic. The empty global update hook means category data is reflected through locale structures/cache rather than category-specific globals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_messages_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_monetary_misc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_monetary_misc.h

Read completely: 49 lines.

This header supplies template macros for the `LC_MONETARY` category: `_CATEGORY_TYPE` as `_MonetaryLocale`, `_CATEGORY_ID` as `LC_MONETARY`, and `_CATEGORY_NAME` as `"LC_MONETARY"`. It defines an empty update hook.

Important interactions: used to instantiate the generic NetBSD locale category loader for monetary data.

Security/reliability notes: no runtime code beyond an inline no-op. The closing comment names a different guard prefix, but the actual include guard is correct.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_monetary_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_numeric_misc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_numeric_misc.h

Read completely: 49 lines.

This header supplies template macros for the `LC_NUMERIC` category: `_CATEGORY_TYPE` as `_NumericLocale`, `_CATEGORY_ID` as `LC_NUMERIC`, and `_CATEGORY_NAME` as `"LC_NUMERIC"`. It defines an empty update hook.

Important interactions: used by concrete numeric locale category code with `nb_lc_template.h`.

Security/reliability notes: no standalone runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_numeric_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template.h

Read completely: 244 lines.

This template implements caching and loading for NetBSD locale categories. It defines a per-category cache of loaded parts, optionally guarded by a mutex, loads C/POSIX directly from `_lc_C_locale`, loads other names via `_PREFIX(create_impl)`, handles force mappings, resolves aliases through `locale.alias`, and provides a generated category `setlocale`.

Important interactions: category-specific files define `_PREFIX`, `_CATEGORY_TYPE`, `_CATEGORY_ID`, and `_CATEGORY_NAME` before including it. It depends on `aliasname_local.h`, `_PathLocale`, `_lc_C_locale`, and category-specific `create_impl` functions.

Security/reliability notes: cache entries are intentionally process-lifetime allocations. Alias resolution and file loading are mutex-protected when `_REENTRANT`. The alias macro's force logic is subtle and depends on `/FORCE` semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template_decl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template_decl.h

Read completely: 41 lines.

This header declares template-generated category helpers: `_PREFIX(create_impl)` and `_PREFIX(update_global)`, and includes the generic setlocale declaration template.

Important interactions: used by concrete NetBSD locale category files before including `nb_lc_template.h`.

Security/reliability notes: declaration-only template support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_template_decl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_time_misc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_time_misc.h

Read completely: 55 lines.

This header supplies template macros for `LC_TIME`: `_CATEGORY_TYPE` as `_TimeLocale`, `_CATEGORY_ID` as `LC_TIME`, and `_CATEGORY_NAME` as `"LC_TIME"`. It also defines index conversion macros for day, month, and AM/PM `nl_langinfo` item ranges.

Important interactions: used by time locale category implementation and related table lookups.

Security/reliability notes: no standalone runtime behavior. Index macros assume valid `nl_item` values from the corresponding ranges.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nb_lc_time_misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/newlocale.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/newlocale.c

Read completely: 110 lines.

This file implements `newlocale`. It allocates a new locale object, copies either the source locale or current locale, applies a single locale name or slash-separated names to the categories selected by `mask`, then builds/attaches a locale cache.

Important interactions: uses `_find_category` to call each category's setlocale handler and `_setlocale_cache` to populate `struct lconv` cache data.

Security/reliability notes: if a category handler fails, this implementation does not check each handler return in the single-name path before continuing. It frees the destination on malformed slash strings or cache failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/newlocale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nl_langinfo.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/nl_langinfo.c

Read completely: 196 lines.

This file implements `nl_langinfo` and `nl_langinfo_l`. Static tables map supported `nl_item` values to locale categories and byte offsets within category structs. The function returns an empty string for out-of-range or unused items, otherwise copies the pointer stored at the computed offset.

Important interactions: reads `_TimeLocale`, `_NumericLocale`, `_MessagesLocale`, and `_RuneLocale` data from `loc->part_impl`. `CODESET` is served from `_RuneLocale.rl_codeset`.

Security/reliability notes: table offsets are stored as `uint16_t`, so struct offsets must fit. It assumes each mapped offset refers to a `char *` field. Unsupported ERA/ALT_DIGITS/CRNCYSTR entries intentionally return empty strings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/nl_langinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/rune.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/rune.c

Read completely: 430 lines.

This file loads binary rune locale data into an in-memory `_RuneLocale`. It validates the `RuneCT10` file format, converts big-endian cached tables and extended ranges, copies variable data, extracts `CODESET=`, opens the matching Citrus ctype, and builds byte-oriented ctype/toupper/tolower compatibility tables.

Important interactions: consumes structures from `runetype_file.h`, produces `_RuneLocale` from `runetype_local.h`, calls `_citrus_ctype_open`, and uses `_runetype_priv`/`_towctrans_priv` to derive byte tables. On signed-char platforms it allocates guarded ctype tables to catch negative-index ctype abuse unless compatibility mode permits it.

Security/reliability notes: validates many file-size bounds before copying range payloads, but the range arithmetic and total allocation depend on trusted counts not overflowing earlier calculations. Error paths free guarded tables and the locale object. `__mb_len_max_runtime` bounds the loaded encoding's `MB_CUR_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/rune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/runetable.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/runetable.c

Read completely: 353 lines.

This file defines `_DefaultRuneLocale`, the built-in C/POSIX rune classification and mapping table. It includes cached runetype bits for byte values, lower/upper mapping arrays, empty extended ranges, codeset `"646"`, the default Citrus ctype, translation entries, classification entries, and byte ctype/toupper/tolower table pointers.

Important interactions: global C locale objects in `global_locale.c` point to this default rune locale. `rune.c` copies pieces of this table when initializing dynamically loaded rune locales.

Security/reliability notes: static data only. Correctness is foundational for all C-locale ctype and wide classification behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/runetable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_file.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_file.h

Read completely: 136 lines.

This header defines the serialized rune locale file format and runetype bit masks. It declares packed file entries/ranges/locales, magic string `RuneCT10`, the `CODESET=` variable tag, cached table sizes, rune scalar types, and screen-width/type flags.

Important interactions: `rune.c` reads these packed structures from mapped locale files and converts them to host-endian `_RuneLocale` structures. Tools that generate locale files must match this layout.

Security/reliability notes: serialized fields are network-endian and packed. Consumers must validate lengths carefully before accessing trailing variable-size data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_local.h

Read completely: 145 lines.

This header defines the in-memory rune locale representation: `_RuneEntry`, `_RuneRange`, `_WCTransEntry`, `_WCTypeEntry`, indexes for standard classification/translation names, and `_RuneLocale` containing cached type/mapping arrays, extended ranges, variable data, Citrus ctype pointer, wctype/wctrans tables, and byte ctype tables.

Important interactions: central shared header for `rune.c`, `_wctype.c`, `_wctrans.c`, `iswctype_mb.c`, `multibyte.h`, and default rune table definitions.

Security/reliability notes: no executable code, but the structure layout is a private ABI within libc locale code. Range arrays must remain sorted for binary-search helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/runetype_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale.c

Read completely: 203 lines.

This file implements libc locale dispatch and cache construction. It registers category handlers, initializes `_PathLocale`, resolves environment defaults, implements `_setlocale_cache`, `_find_category`, `_get_locale_env`, `__setlocale`, and public `setlocale`.

Important interactions: category handlers include generic `LC_ALL`, dummy `LC_COLLATE`, and Citrus category loaders. `_setlocale_cache` deduplicates caches by monetary/numeric/message category names and fills `struct lconv` fields from category implementations.

Security/reliability notes: the cache list is explicitly noted as not locked, leaking memory on races. `__setlocale` calls `_setlocale_cache` even if the category handler returned NULL, and does not free the allocated cache if an existing cache is reused inside `_setlocale_cache` only after the call succeeds. Environment lookup rejects names containing `/`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale_local.h

Read completely: 103 lines.

This header defines libc's private locale state: locale name constants, `_locale_cache_t`, `struct _locale`, category setter function type, declarations for category setlocale functions, cache helpers, and `_current_locale()` in libc builds.

Important interactions: included by most locale implementation files. It exposes `_PathLocale`, `_C_cache`, and `__mb_len_max_runtime`.

Security/reliability notes: no standalone logic beyond `_current_locale`, which returns the mutable global locale in `_LIBC` builds. The fixed `_LOCALENAME_LEN_MAX` shapes storage for category names and composite queries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/setlocale_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcscoll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcscoll.c

Read completely: 56 lines.

This file implements `wcscoll` and `wcscoll_l` as simple `wcscmp` wrappers. A comment notes that `LC_COLLATE` should be implemented.

Important interactions: uses `_current_locale()` for the non-`_l` wrapper but ignores the locale argument.

Security/reliability notes: no locale collation support; sorting behavior is code-point/wide-character order rather than locale collation order.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcscoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcsftime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcsftime.c

Read completely: 116 lines.

This file implements `wcsftime` and `wcsftime_l`. It converts the wide format string to multibyte, calls `strftime_l`, then converts the result back to wide characters.

Important interactions: uses `wcstombs_l`, `strftime_l`, `mbstowcs_l`, `_current_locale()`, and `MB_CUR_MAX_L(loc)`.

Security/reliability notes: checks for multiplication overflow before allocating the multibyte output buffer. Stateful encodings are explicitly called out as a limitation because conversion state may be lost across format specifications.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcsftime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstod.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstod.c

Read completely: 51 lines.

This file instantiates `_wcstod.h` for `wcstod` and `wcstod_l`, with return type `double` and backend `strtod_l`.

Important interactions: provides weak aliases and includes the shared floating conversion template.

Security/reliability notes: inherits the template's multibyte conversion behavior and end-pointer limitations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstof.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstof.c

Read completely: 51 lines.

This file instantiates `_wcstod.h` for `wcstof` and `wcstof_l`, with return type `float` and backend `strtof_l`.

Important interactions: provides weak aliases and delegates all parsing logic to the shared template.

Security/reliability notes: inherits template behavior, including conversion allocation and approximate wide end-pointer mapping.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoimax.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoimax.c

Read completely: 49 lines.

This file instantiates `_wcstol.h` for `wcstoimax`, using `intmax_t`, `INTMAX_MIN`, and `INTMAX_MAX`.

Important interactions: includes `__wctoint.h` and the signed integer conversion template.

Security/reliability notes: inherits base validation and overflow saturation from `_wcstol.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoimax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstol.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstol.c

Read completely: 48 lines.

This file instantiates `_wcstol.h` for `wcstol`, using `long`, `LONG_MIN`, and `LONG_MAX`.

Important interactions: includes `__wctoint.h` and emits both `wcstol` and `wcstol_l` through the template.

Security/reliability notes: inherits signed conversion overflow and invalid-base behavior from the template.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstold.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstold.c

Read completely: 51 lines.

This file instantiates `_wcstod.h` for `wcstold` and `wcstold_l`, with return type `long double` and backend `strtold_l`.

Important interactions: provides weak aliases and reuses the floating wide-string conversion template.

Security/reliability notes: inherits template limitations around multibyte conversion and end-pointer mapping.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstold.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoll.c

Read completely: 48 lines.

This file instantiates `_wcstol.h` for `wcstoll`, using `long long int`, `LLONG_MIN`, and `LLONG_MAX`.

Important interactions: includes `__wctoint.h` and the signed conversion template.

Security/reliability notes: inherits overflow checks and ASCII digit mapping from `_wcstol.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoul.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoul.c

Read completely: 47 lines.

This file instantiates `_wcstoul.h` for `wcstoul`, using `unsigned long` and `ULONG_MAX`.

Important interactions: includes `__wctoint.h` and the unsigned conversion template.

Security/reliability notes: inherits unsigned overflow saturation and negative-input wrapping from `_wcstoul.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoull.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoull.c

Read completely: 47 lines.

This file instantiates `_wcstoul.h` for `wcstoull`, using `unsigned long long int` and `ULLONG_MAX`.

Important interactions: includes `__wctoint.h` and the unsigned conversion template.

Security/reliability notes: inherits base validation and overflow behavior from `_wcstoul.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoull.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoumax.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoumax.c

Read completely: 48 lines.

This file instantiates `_wcstoul.h` for `wcstoumax`, using `uintmax_t` and `UINTMAX_MAX`.

Important interactions: includes `__wctoint.h` and the unsigned conversion template.

Security/reliability notes: inherits unsigned conversion semantics from `_wcstoul.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcstoumax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcsxfrm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcsxfrm.c

Read completely: 71 lines.

This file implements `wcsxfrm` and `wcsxfrm_l` as a simple copy/length transform. It returns `wcslen(s2)` and copies `s2` to `s1` only if it fits within `n`.

Important interactions: locale argument is ignored because `LC_COLLATE` is not implemented.

Security/reliability notes: if the transformed length is `n` or more, it leaves the destination unspecified by doing nothing, matching the cited SUSv3 behavior. No locale collation transform is performed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/locale/wcsxfrm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/md/Makefile.inc

Read completely: 27 lines.

This makefile fragment adds MD4/MD5 libc sources and manual pages. It includes `md4c.c`, `md5c.c`, `md4hl.c`, and `md5hl.c`, registers man pages and links for init/update/final/end/file/data APIs, and generates `md4.3`/`md5.3` from `mdX.3` plus algorithm-specific copyright text.

Important interactions: `md4hl.c` and `md5hl.c` are generated-style instantiations of `mdXhl.c`.

Security/reliability notes: no runtime behavior. MD4 and MD5 are legacy hash algorithms and should not be treated as collision-resistant for new security uses.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/md2hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/md/md2hl.c

Read completely: 24 lines.

This file instantiates the generic MD high-level helper implementation for MD2 when the platform lacks `<md2.h>`. It defines `MDALGORITHM` as `MD2`, includes namespace handling and `<md2.h>`, and conditionally includes `mdXhl.c`.

Important interactions: intended for tool/compatibility builds controlled by `HAVE_NBTOOL_CONFIG_H` and `HAVE_MD2_H`.

Security/reliability notes: MD2 is cryptographically obsolete. This file contains no algorithm logic itself.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/md2hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/md4hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/md/md4hl.c

Read completely: 16 lines.

This file instantiates `mdXhl.c` for MD4 by defining `MDALGORITHM` as `MD4` and `MDINCLUDE` as `<md4.h>`.

Important interactions: produces high-level `MD4End`, `MD4File`, and `MD4Data` functions from the generic template.

Security/reliability notes: MD4 is obsolete and collision-prone. This wrapper contains no independent logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/md4hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/md5hl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/md/md5hl.c

Read completely: 16 lines.

This file instantiates `mdXhl.c` for MD5 by defining `MDALGORITHM` as `MD5` and `MDINCLUDE` as `<md5.h>`.

Important interactions: produces high-level `MD5End`, `MD5File`, and `MD5Data` helpers.

Security/reliability notes: MD5 is obsolete for collision-resistant security use. This file is a thin template wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/md5hl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/mdXhl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/md/mdXhl.c

Read completely: 109 lines.

This generic template implements high-level digest helpers for an `MDALGORITHM`: `End` finalizes a context and formats the 16-byte digest as lowercase hex, `File` hashes a named file by reading `BUFSIZ` chunks, and `Data` hashes an in-memory buffer.

Important interactions: included by `md4hl.c`, `md5hl.c`, and conditionally `md2hl.c`. Macro concatenation builds algorithm-specific function and context names. Weak aliases are emitted for libc builds.

Security/reliability notes: `End` allocates 33 bytes if caller passes NULL. `File` preserves `errno` across `close`, but if `close` itself fails after successful reads that failure is ignored. Digest size is fixed at 16 bytes, matching MD2/MD4/MD5 only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/md/mdXhl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/misc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/misc/Makefile.inc

Read completely: 15 lines.

This makefile fragment adds miscellaneous libc sources. It optionally includes `ubsan.c` when `MKLIBCSANITIZER=yes`, and always includes constructor startup support `initfini.c` and stack protector support `stack_protector.c`.

Important interactions: uses architecture and generic misc paths through `.PATH`.

Security/reliability notes: no runtime behavior. The selected files affect process initialization and compiler-inserted stack/bounds failure handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/misc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/misc/initfini.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/misc/initfini.c

Read completely: 131 lines.

This file implements libc startup initialization in `_libc_init`. It ensures one-time initialization, sets up a static-binary `_dlauxinfo` substitute when possible, initializes stack protector guard, atomic operations, static TLS, threading, and atexit mutexes.

Important interactions: called both from crt0 and global constructor handling, so `libc_initialised` prevents duplicate work. It defines common symbols for `__ps_strings`, `__progname`, and `environ` for compatibility with older binaries.

Security/reliability notes: comments document an ASLR/Emacs undump hazard around `__ps_strings`. Initialization order is security-critical because stack protector setup happens early. `_dlauxinfo` weak-reference behavior differs between static and dynamic binaries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/misc/initfini.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/misc/stack_protector.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/misc/stack_protector.c

Read completely: 124 lines.

This file provides stack protector guard setup and failure handlers. `__guard_setup` fills `__stack_chk_guard` from `sysctl(KERN_ARND)` and falls back to a terminator canary if random retrieval fails. Failure paths log or print an error, block most signals, restore default `SIGABRT`, raise it, and exit with 127 if still running.

Important interactions: `_libc_init` calls `__guard_setup`; compiler-inserted stack protector checks call `__stack_chk_fail` or local aliases. `__chk_fail` handles fortified buffer check failures.

Security/reliability notes: fallback canary is weaker than random canary but avoids leaving guard zero. Failure handling tries to minimize reentrancy by blocking signals before logging and aborting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/misc/stack_protector.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/Makefile.inc

Read completely: 13 lines.

This makefile fragment adds DNS nameserver helper sources: `ns_name.c`, `ns_netint.c`, `ns_parse.c`, `ns_print.c`, `ns_samedomain.c`, and `ns_ttl.c`.

Important interactions: sets `.PATH` to `${.CURDIR}/nameser` and applies a lint suppression to `ns_name.c` for a table initialized with `-1` in `char` storage.

Security/reliability notes: no runtime behavior in this fragment. The lint note documents intentional unsigned char conversion behavior in DNS name parsing tables.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/nameser/Makefile.inc -->