# Group Research: subset-b-009527

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localename.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localename.c

Purpose: determines the active gettext locale name in XPG syntax for message lookup. On POSIX-like builds `_nl_locale_name(category, categoryname)` returns `setlocale(category, NULL)` when reliable, otherwise follows the environment precedence `LC_ALL`, category-specific variable, then `LANG`, defaulting to `"C"`.

Important APIs and control flow: the only exported routine is `_nl_locale_name`. Non-Win32 control flow is intentionally small and returns pointers owned by libc/environment/static storage. The large Win32 branch first honors POSIX-style environment overrides, then reads `GetThreadLocale()`, strips sort rules with `LANGIDFROMLCID`, splits `PRIMARYLANGID` and `SUBLANGID`, and maps many Windows language/sublanguage constants to gettext locale strings such as `en_US`, `pt_BR`, or modifiers like `az_AZ@cyrillic`.

State and dependencies: no persistent state is stored. Dependencies are `stdlib.h`, `locale.h`, optional `windows.h`, configure macros, and platform locale constants, with fallback definitions for older MinGW headers.

Integration points: called by gettext lookup code to choose catalog directories. It integrates with `LC_MESSAGES` category naming and Win32 process/thread locale APIs.

Risks and test signals: risks are stale or ambiguous Win32 mappings, environment lifetime assumptions, and codeset omission. Test by overriding `LC_ALL`, category variables, and `LANG`; on Windows test representative LCIDs and fallback `"C"`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/log.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/log.c

Purpose: appends gettext-style untranslated-message entries to a log file. It is used when translation lookup fails and logging is enabled elsewhere in libintl.

Important APIs and control flow: `_nl_log_untranslated(logfilename, domainname, msgid1, msgid2, plural)` caches the last opened filename and `FILE *`, reopening only when the target changes. It emits `domain`, `msgid`, optional `msgid_plural`, and an empty `msgstr`/`msgstr[0]` block. `print_escaped()` quotes ASCII strings, escaping backslash and double quote, and splits embedded newlines into PO-style continued strings.

State and persistence: static `last_logfilename` and `last_logfile` persist across calls; file contents are appended with `fopen(..., "a")`. There is no explicit flush after each entry and no lock protection.

Dependencies and integration: depends on stdio/stdlib/string and is called from gettext failure paths. Output format is intended to be consumable as PO fragments.

Risks and test signals: not thread-safe, silently drops entries on allocation/open failure, and keeps descriptors open until another filename is used or process exit. Test escaped quotes, backslashes, trailing and non-trailing newlines, plural entries, filename switches, and open failure behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/ngettext.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/ngettext.c

Purpose: implements the public plural gettext entry point for the current default domain.

Important APIs and control flow: `NGETTEXT(msgid1, msgid2, n)` is name-mapped to `__ngettext` for glibc or `libintl_ngettext` for standalone libintl. The function delegates all real lookup and plural selection to `DCNGETTEXT(NULL, msgid1, msgid2, n, LC_MESSAGES)`. A glibc weak alias exposes `ngettext`.

State and persistence: this file stores no state. It relies on global gettext domain, locale, catalog cache, and plural-expression state managed by other libintl files.

Dependencies and integration: includes `gettextP.h`, either system `libintl.h` or local `libgnuintl.h`, and `locale.h`. It is a thin integration wrapper connecting the standard API to `dcngettext`.

Risks and test signals: risks live in downstream lookup logic, but this wrapper must preserve ABI names and category selection. Test that `ngettext` honors the current `textdomain`, `LC_MESSAGES`, and plural `n`, and that default fallback returns `msgid1`/`msgid2` when no catalog exists.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/ngettext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.c

Purpose: supplies OS/2 EMX runtime compatibility for libintl directory and environment handling.

Important APIs and control flow: `_nl_getenv(name)` calls `DosScanEnv` so DLL builds can read environment variables reliably. The constructor `nlos2_initialize()` reads `UNIXROOT` and `GNULOCALEDIR`, then initializes `_nlos2_libdir`, `_nlos2_localealiaspath`, and `_nlos2_localedir` to either `GNULOCALEDIR`, `UNIXROOT`-prefixed configure paths, or hardwired defaults. If the computed locale directory fits in `MAXPATHLEN`, it copies it to `libintl_nl_default_dirname`.

State and persistence: global path pointers and a fixed-size default dirname buffer persist for process lifetime. Allocated prefixed paths are intentionally not freed.

Dependencies and integration: included by `osdep.c` on `__EMX__`; paired with `os2compat.h`, which rewrites `LIBDIR`, `LOCALEDIR`, `LOCALE_ALIAS_PATH`, `getenv`, and case-insensitive string APIs.

Risks and test signals: constructor allocation failures are not checked before later `strlen`, and path concatenation assumes configured paths begin suitably. Test with and without `UNIXROOT`/`GNULOCALEDIR`, long paths, and DLL environment visibility.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.h

Purpose: centralizes OS/2 compile-time compatibility macros for gettext.

Important APIs/types/functions: when not included from the OS/2 implementation itself, it remaps `LIBDIR`, `LOCALEDIR`, and `LOCALE_ALIAS_PATH` to runtime globals `_nlos2_libdir`, `_nlos2_localedir`, and `_nlos2_localealiaspath`. It declares those globals, maps `strcasecmp`/`strncasecmp` to `stricmp`/`strnicmp`, forces `HAVE_STRCASECMP`, remaps `getenv` to `_nl_getenv`, and defines legacy `LC_MESSAGES_COMPAT`.

State and persistence: the header declares external path globals owned by `os2compat.c`; it stores no state itself.

Dependencies and integration: intended for inclusion from `config.h` or OS/2-aware gettext compilation units. It changes names globally, so include order matters.

Risks and test signals: broad macro replacement can affect unrelated code included afterward. Test OS/2 builds for correct path macros, case-insensitive alias lookup, and compatibility with older gettext `LC_MESSAGES == -1` assumptions.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/osdep.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/osdep.c

Purpose: selects OS-dependent libintl glue at compile time.

Important APIs and control flow: if `__EMX__` is defined, the file includes `os2compat.c` directly so OS/2 support is compiled into this translation unit. Otherwise it declares `typedef int dummy;` only to keep compilers from warning about an empty translation unit.

State and persistence: no state outside what `os2compat.c` contributes on OS/2.

Dependencies and integration: this file is part of the libintl build list and provides a stable platform hook without requiring every makefile to conditionally add OS/2 sources.

Risks and test signals: including a `.c` file is intentional here but can surprise tooling. Test that non-OS/2 builds compile without symbols, and OS/2 builds include exactly one copy of the compatibility globals and constructor.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/osdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.c

Purpose: extracts and initializes plural-form expressions from gettext catalog header entries.

Important APIs and control flow: `EXTRACT_PLURAL_EXPRESSION(nullentry, pluralp, npluralsp)` searches the header for `nplurals=` and `plural=`, parses `nplurals` with `strtoul` or a fallback loop, then invokes `PLURAL_PARSE` on the plural expression string. On any missing field or parse failure it falls back to `GERMANIC_PLURAL`, representing `n != 1` with two plural forms. `GERMANIC_PLURAL` is either statically initialized using C99 designated initializers or lazily initialized by `init_germanic_plural()`.

State and persistence: the fallback expression is global static process state. Successfully parsed expressions are heap-owned by the caller and freed through `FREE_EXPRESSION`.

Dependencies and integration: depends on `plural-exp.h`, `plural.c`/`plural.y` parser symbols, ctype/string/stdlib, and name remapping for glibc, libintl, or gettext tools.

Risks and test signals: it uses substring search rather than structured header parsing and does not validate `nplurals` bounds against expression results here. Test malformed headers, whitespace, very large numbers, missing semicolons, parse errors, and default English/Germanic fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.h

Purpose: defines the AST and parser interface for gettext plural-form selection.

Important APIs/types/functions: `struct expression` stores an operator, arity, and either numeric value or up to three child expressions. Operators cover variable `n`, constants, logical not, arithmetic, comparisons, logical and/or, and ternary `?:`. `struct parse_args` passes the input cursor and parse result through the Bison interface. Macros rename `FREE_EXPRESSION`, `PLURAL_PARSE`, `GERMANIC_PLURAL`, and `EXTRACT_PLURAL_EXPRESSION` for glibc, standalone libintl, or gettext-tool builds. Non-libintl/tool builds also expose `plural_eval`.

State and persistence: declares the global fallback expression and heap-expression ownership contract but stores no state itself.

Dependencies and integration: consumed by `plural-exp.c`, generated `plural.c`, grammar `plural.y`, and catalog loading code that evaluates plural forms.

Risks and test signals: ABI/name remapping is sensitive because `struct expression` is explicitly considered binary-incompatible across contexts. Test compile modes `_LIBC`, `IN_LIBINTL`, and tool builds; verify recursive free and parser result ownership.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.c

Purpose: generated GNU Bison 1.35 parser for gettext plural expressions, built from `plural.y`.

Important APIs and control flow: the generated `yyparse` is renamed to `PLURAL_PARSE` outside glibc. It consumes a `struct parse_args *`, uses a pure-parser interface, and builds `struct expression` AST nodes through embedded `new_exp_*` helpers. The included scanner `yylex()` tokenizes numbers, variable `n`, `||`, `&&`, comparison, arithmetic, unary `!`, parentheses, and ternary `?:`, stopping safely at semicolon, newline, or NUL. `FREE_EXPRESSION()` recursively releases AST nodes.

State and persistence: parser state is stack/local; AST nodes are heap-allocated. No persistent state except generated parser tables. The caller owns the returned AST.

Dependencies and integration: includes `plural-exp.h`; used by `plural-exp.c` during catalog header parsing. It mirrors `plural.y`, so regeneration must use a compatible Bison skeleton.

Risks and test signals: generated code uses alloca/stack growth paths and old Bison conventions. Numeric token parsing can overflow `unsigned long` silently. Test representative plural expressions, invalid single `&`/`|`, malformed ternaries, allocation failures, and equivalence with regenerated output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.y -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.y

Purpose: authoritative Bison grammar for gettext plural expressions.

Important APIs and control flow: it declares a pure parser with `YYLEX_PARAM` and `YYPARSE_PARAM` wired to `struct parse_args`. Grammar precedence follows C-like expression precedence for ternary, logical OR/AND, equality, comparison, additive, multiplicative, and unary not. Semantic actions allocate AST nodes with `new_exp_0` through `new_exp_3`; if allocation fails, children are freed and parsing aborts. The scanner recognizes decimal numbers, `n`, operators, parentheses, and end delimiters; `yyerror()` intentionally emits nothing.

State and persistence: no persistent state. It produces heap-owned `struct expression` trees and defines recursive `FREE_EXPRESSION`.

Dependencies and integration: generates `plural.c`; consumed by `plural-exp.c` via `PLURAL_PARSE`. Name mapping avoids symbol clashes across glibc/libintl/tool builds.

Risks and test signals: `%expect 7` documents known parser conflicts, so parser changes require careful conflict review. Test grammar associativity, malformed expressions, memory cleanup on partial failures, and compatibility between `.y` and checked-in generated `.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.y -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.c

Purpose: fetches a parsed printf argument list from a `va_list` into typed storage for later positional formatting.

Important APIs and control flow: `printf_fetchargs(va_list args, arguments *a)` iterates over `a->arg[0..count)` and dispatches on each `arg_type`. It uses default argument promotions for small integer and char types, handles optional long long, long double, wide char/string, pointer, string, and `%n` count-pointer variants, and returns `-1` for `TYPE_NONE` or unknown types.

State and persistence: no global state. It mutates caller-provided `arguments` by filling each union field.

Dependencies and integration: depends on `printf-args.h`. `vasnprintf.c` calls it after `printf_parse()` has registered all required argument types.

Risks and test signals: correctness depends on the parser assigning exactly the ABI type expected by `va_arg`; a mismatch is undefined behavior. Test every length modifier, positional reuse, `*` width/precision arguments, `%n`, disabled `HAVE_LONG_LONG`/wide-type configurations, and unknown-type rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.h

Purpose: declares typed storage used to replay parsed printf format directives, especially for positional arguments.

Important APIs/types/functions: `arg_type` enumerates scalar, string, pointer, wide, floating, and `%n` pointer categories. `argument` stores the selected type plus a union holding the fetched value. `arguments` groups a count and dynamic `argument *` array. It declares `printf_fetchargs`.

State and persistence: no state; it defines ownership expectations for arrays allocated by `printf-parse.c` and filled by `printf-args.c`.

Dependencies and integration: includes `stddef.h`, optional `wchar.h`, and `stdarg.h`. Used by both narrow and wide printf parsers and `vasnprintf.c`.

Risks and test signals: compile-time feature macros change enum layout and union fields, so all including translation units must share the same configuration. Test ABI consistency in standalone and statically included builds, and all optional type configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-args.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.c

Purpose: parses narrow or wide printf format strings into directive metadata and a typed argument table.

Important APIs and control flow: `PRINTF_PARSE(format, d, a)` is macro-renamed to `printf_parse` or `wprintf_parse`. It scans for `%`, records directive bounds, flags, width/precision spans, positional indices, conversion, and argument index. `REGISTER_ARG` grows `a->arg` using `xsum`/`xtimes`, initializes missing entries to `TYPE_NONE`, and rejects positional reuse with incompatible types. It supports XSI positional syntax (`n$`, `*n$`), C99 `j`, `z`/`Z`, `t`, `hh`, `h`, `l`, `ll`, `L`, and normal conversions.

State and persistence: allocates `d->dir` and `a->arg`; caller frees them. On error it frees partial allocations and returns `-1`.

Dependencies and integration: used by `vasnprintf.c` and included by `printf.c` for fallback implementations. Depends on `xsize.h` for overflow detection and `printf-args.h` for type registration.

Risks and test signals: malformed format strings, huge positional indices, and incompatible positional reuse are the key risks. Test all flags, `%`, `%n`, wide aliases `C`/`S`, width/precision positions, overflow paths, and cleanup on parse failure.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.h

Purpose: defines narrow-character printf directive metadata and parser API.

Important APIs/types/functions: flag macros represent grouping, left alignment, sign, space, alternate form, and zero padding. `ARG_NONE` is the sentinel for no consumed argument. `char_directive` records the source span, width/precision spans, width/precision argument indices, conversion character, and main argument index. `char_directives` holds the directive array and maximum width/precision literal lengths. It declares `printf_parse`.

State and persistence: no global state. The parser allocates `char_directives.dir`, which callers own.

Dependencies and integration: includes `printf-args.h`; consumed by `printf-parse.c`, `vasnprintf.c`, and `printf.c` fallback code.

Risks and test signals: the structure stores pointers into the original format string, so callers must keep the format alive while formatting. Test sentinel handling, literal max-length tracking, and conversion normalization for `C`/`S` in platforms that support those extensions.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf-parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf.c

Purpose: provides libintl printf-family wrappers that support POSIX/XSI positional parameters on systems whose native printf does not.

Important APIs and control flow: when `HAVE_POSIX_PRINTF` is false, it statically includes `printf-args.c`, `printf-parse.c`, and `vasnprintf.c`, then exports `libintl_vfprintf`, `libintl_fprintf`, `libintl_vprintf`, `libintl_printf`, `libintl_vsprintf`, `libintl_sprintf`, optional snprintf/asprintf variants, and optional wide-character variants. Each wrapper delegates directly to the system function if the format lacks `$`; otherwise it formats through `libintl_vasnprintf` or `libintl_vasnwprintf`, then writes/copies the result.

State and persistence: no global state. Temporary formatted strings are heap-allocated and freed by wrappers, except returned asprintf buffers.

Dependencies and integration: depends on platform printf feature macros, stdio/string/stdlib, optional wchar support, and DLL export attributes.

Risks and test signals: fallback `vsprintf`/`vsnprintf` behavior around truncation, `%n`, and return counts is delicate. Test both `$` and non-`$` formats, truncation copies, wide output, stream write failures, and platforms with/without `snprintf`/`asprintf`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/printf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.c

Purpose: implements optional relocatable installation-prefix rewriting for gettext/libintl packages.

Important APIs and control flow: under `ENABLE_RELOCATABLE`, `set_relocation_prefix()` stores original/current prefixes and notifies dependent charset/iconv/intl libraries. `compute_curr_prefix()` derives a current prefix from an original prefix, original install directory, and current pathname by stripping matching relative path components. For PIC shared libraries, platform-specific code locates the loaded library path using Win32 `DllMain` or Linux `/proc/self/maps`. `relocate(pathname)` lazily initializes shared-library prefixes when needed and rewrites paths beginning with `orig_prefix` to `curr_prefix`.

State and persistence: static `orig_prefix`, `curr_prefix`, lengths, optional `shared_library_fullname`, and initialization flags persist. Returned relocated strings may be newly allocated and intentionally leaked unless callers cache them.

Dependencies and integration: used by path-building code for catalogs and dependent libraries. Handles Unix, Win32, OS/2, and DOS path rules.

Risks and test signals: prefix memory is not freed, `/proc/self/maps` parsing is Linux/glibc-specific, and path comparison assumptions can fail for unusual installs. Test equal prefixes, moved trees, root prefixes, Windows drive paths, PIC library detection, and disabled relocation.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.h

Purpose: declares or disables the relocatable path API.

Important APIs/types/functions: when `ENABLE_RELOCATABLE` is enabled, it declares exported `set_relocation_prefix(orig_prefix, curr_prefix)`, `relocate(pathname)`, and `compute_curr_prefix(orig_installprefix, orig_installdir, curr_pathname)`. It defines `RELOCATABLE_DLL_EXPORTED` for MSVC DLL builds. When relocation is disabled, `relocate(pathname)` is a macro identity function.

State and persistence: no state in the header; implementation state lives in `relocatable.c`.

Dependencies and integration: included by code that wants installation paths to survive tree moves without conditionalizing call sites.

Risks and test signals: callers must handle the dual nature of `relocate`: identity macro when disabled, possibly allocated/leaking pointer when enabled. Test both configure modes and C++ inclusion.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/relocatable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/textdomain.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/textdomain.c

Purpose: implements `textdomain(3)`, selecting the default message catalog domain.

Important APIs and control flow: `TEXTDOMAIN(domainname)` is name-mapped for glibc or standalone libintl. A `NULL` argument returns the current domain. Empty string or the built-in default resets `_nl_current_default_domain` to `_nl_default_default_domain`. A new non-default domain is duplicated with `strdup`/`malloc`, installed under `_nl_state_lock`, `_nl_msg_cat_cntr` is incremented on success, and the previous non-default domain is freed.

State and persistence: mutates global `_nl_current_default_domain` and `_nl_msg_cat_cntr`; locking is real in glibc and dummy in standalone builds.

Dependencies and integration: depends on `gettextP.h`, libintl headers, string allocation, and the catalog invalidation counter consumed by lookup/cache code.

Risks and test signals: standalone builds lack real thread synchronization; allocation failure leaves the old domain intact but returns `NULL`. Test reset, same-domain no-op, repeated changes, allocation failure behavior, and catalog reload notification.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/textdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.c

Purpose: implements dynamically sized `vasnprintf`/`vasnwprintf` with support for parsed positional printf directives.

Important APIs and control flow: `VASNPRINTF(resultbuf, lengthp, format, args)` macro-expands to narrow or wide implementation. It parses the format, fetches typed arguments, allocates a temporary directive buffer, then iterates literal spans and directives. `%%` appends a literal percent; `%n` writes the current output length; other conversions reconstruct a single-directive format string, supply optional width/precision prefixes, and call `snprintf`/`swprintf` when available or a sized `sprintf` fallback otherwise. `ENSURE_ALLOCATION` grows result storage using checked `xsize.h` arithmetic.

State and persistence: no globals. The returned buffer is either caller-provided `resultbuf` or malloc-allocated. On errors it frees internal allocations, sets `errno` to `EINVAL` or `ENOMEM`, and returns `NULL`.

Dependencies and integration: used by `printf.c` fallback wrappers and as public `vasnprintf` declarations. Depends on `printf-parse.c`, `printf-args.c`, wide-character feature macros, `snprintf`, and platform float limits.

Risks and test signals: portability logic for non-C99 `snprintf`, `%n`, wide conversions, MB_CUR_MAX sizing, and no-snprintf fallbacks is complex. Test truncation, huge widths/precisions, every conversion class, `%n`, NULL/resultbuf reuse, ENOMEM paths, and wide/narrow builds.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.h

Purpose: declares dynamically allocated narrow formatted-string helpers.

Important APIs/types/functions: `asnprintf(resultbuf, lengthp, format, ...)` and `vasnprintf(resultbuf, lengthp, format, va_list)` return a pointer to a NUL-terminated formatted string, either reusing `resultbuf` or allocating with `malloc`. On success `*lengthp` receives the byte count excluding the trailing NUL. GCC printf-format attributes are provided when available.

State and persistence: no state. Ownership is returned to the caller when the returned pointer differs from `resultbuf`.

Dependencies and integration: includes `stdarg.h` and `stddef.h`; consumed by `vasnprintf.c`, `printf.c`, and callers needing XSI positional formatting support.

Risks and test signals: callers must pass a valid `lengthp` and free allocated results. Test compiler attribute compatibility, C++ linkage, result buffer reuse, and error returns.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnprintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnwprintf.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnwprintf.h

Purpose: declares dynamically allocated wide-character formatted-string helpers.

Important APIs/types/functions: `asnwprintf(resultbuf, lengthp, format, ...)` and `vasnwprintf(resultbuf, lengthp, format, va_list)` mirror the narrow API but operate on `wchar_t` strings. Success returns either the caller buffer or a malloc-allocated buffer and stores the resulting wide-character count excluding the NUL in `*lengthp`.

State and persistence: no state; caller owns any allocated result.

Dependencies and integration: includes `stdarg.h` and `stddef.h` for `wchar_t`/`size_t`. Used by `vasnprintf.c` when `WIDE_CHAR_VERSION` is set and by wide printf wrappers in `printf.c`.

Risks and test signals: return length semantics must stay in wide characters, not bytes. Test wide literals, wide strings/chars, buffer reuse, C++ linkage, and platform differences in `swprintf`/`_snwprintf`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/vasnwprintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/wprintf-parse.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/wprintf-parse.h

Purpose: defines wide-character printf directive metadata and parser API.

Important APIs/types/functions: it duplicates the narrow parser contract using `wchar_t` pointers and conversion fields. `wchar_t_directive` records directive, width, precision, argument indices, flags, and conversion. `wchar_t_directives` holds the directive array and max width/precision lengths. It declares `wprintf_parse`.

State and persistence: no state. Parsed directive pointers refer into the original wide format string and must not outlive it.

Dependencies and integration: includes `printf-args.h`; implemented by compiling `printf-parse.c` with `WIDE_CHAR_VERSION`. Used by wide `vasnprintf.c` and `printf.c` fallback wrappers.

Risks and test signals: duplicated constants must remain compatible with narrow parsing, and wide conversion aliases must match platform support. Test positional wide formats, width/precision `*`, `%lc`/`%ls`, `C`/`S`, and memory cleanup on parse errors.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/wprintf-parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/xsize.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/xsize.h

Purpose: provides checked `size_t` arithmetic helpers for allocation-size calculations.

Important APIs/types/functions: `xcast_size_t`, `xsum`, `xsum3`, `xsum4`, `xmax`, and `xtimes` return `SIZE_MAX` as an overflow sentinel. `size_overflow_p` and `size_in_bounds_p` test that sentinel. Inline helpers carry GCC pure attributes where available.

State and persistence: no state.

Dependencies and integration: includes `stddef.h`, `limits.h`, and optionally `stdint.h`. Used by `printf-parse.c` and `vasnprintf.c` to avoid allocating undersized buffers after overflow.

Risks and test signals: callers must check `SIZE_MAX` before `malloc`; `xtimes` assumes positive element size and is a macro to handle wider integer inputs. Test boundary arithmetic near `SIZE_MAX`, multiplication overflow, and callers that propagate the sentinel into allocation failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/xsize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/Makefile.in

Purpose: autoconf make template for building, testing, installing, and cleaning e2fsprogs `libblkid`.

Important build APIs and control flow: defines object/source lists for cache, device, probe, read, resolve, save, topology, tag, version, size, and seek units. Includes generated e2fsprogs make fragments for static, ELF, BSD, profile, and checker libraries. Builds generated headers `blkid_types.h` via `config.status` and copies `blkid.h.in` to `blkid.h`. Produces `libblkid.3`, `blkid.pc`, optional test executables, and a standalone `blkid` utility linked with `libuuid`.

State and persistence: generated artifacts include headers, man page, pkg-config file, libraries, object directories, and test scripts. Install targets write headers under `$(includedir)/blkid`, library under `$(libdir)`, and pkg-config metadata.

Dependencies and integration: depends on top-level `MCONFIG`, uuid library, substitution tools, and e2fsprogs build macros.

Risks and test signals: generated header/config substitutions must match compiler ABI. Test `make all`, `make check`, install/uninstall, clean/distclean, shared/static variants, and dependency regeneration.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid.h.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid.h.in

Purpose: public libblkid API template installed as `blkid/blkid.h`.

Important APIs/types/functions: exposes opaque handles `blkid_dev`, `blkid_cache`, iterators, `blkid_probe`, and `blkid_topology`; defines `blkid_loff_t` as `__s64`; declares version constants and flags for `blkid_get_dev`. Public APIs cover cache lifetime, device iteration/search, device number resolution, full probing, size detection, verification, tag lookup/iteration/parsing, topology probing, and version parsing.

State and persistence: public callers receive handles to internal cache/device state. Cache persistence is controlled by `blkid_get_cache`/`blkid_put_cache`, with on-disk cache behavior implemented elsewhere.

Dependencies and integration: includes `sys/types.h` and generated `blkid_types.h`. Used by applications, `blkidP.h`, and e2fsprogs utilities.

Risks and test signals: ABI stability depends on keeping structs opaque and type widths correct. Test C/C++ inclusion, all public prototypes, flag semantics, and interaction with generated `blkid_types.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid.pc.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid.pc.in

Purpose: pkg-config template for consumers of libblkid.

Important fields and control flow: configure substitutes `prefix`, `exec_prefix`, `libdir`, `includedir`, and `@E2FSPROGS_VERSION@`. The package advertises name `blkid`, description, private dependency `uuid`, include flag `-I${includedir}/blkid`, and link flag `-L${libdir} -lblkid`.

State and persistence: installed as `$(libdir)/pkgconfig/blkid.pc` by the makefile. It persists build-time installation paths for downstream compile/link discovery.

Dependencies and integration: generated by `config.status`; used by `pkg-config` and downstream build systems.

Risks and test signals: `Requires.private: uuid` matters for static linking; include path must match installed header layout. Test `pkg-config --cflags --libs blkid`, static flags, DESTDIR installs, and version substitution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkidP.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkidP.h

Purpose: private libblkid header defining internal structures, flags, debug controls, and cross-file prototypes.

Important APIs/types/functions: `struct blkid_struct_dev` stores cache linkage, tag list, name, type, priority, device number, timestamp, flags, label, and UUID shortcut. `struct blkid_struct_tag` links tags by device and by tag name. `struct blkid_struct_cache` stores device/tag list heads, probe/cache-file times, flags, and filename. Defines verification/cache flags, probe timing constants, default cache path `/etc/blkid.tab`, error codes, device priority constants, debug masks, `DBG`, `dir_list`, and private prototypes for scanning, llseek, cache read/save, tags, and device allocation.

State and persistence: describes in-memory cache graph and on-disk cache filename; no state itself.

Dependencies and integration: includes public `blkid.h` and private `list.h`. All libblkid implementation files depend on this shared contract.

Risks and test signals: intrusive list ownership is manual and easy to corrupt; private layout changes affect all objects. Test device/tag add/free, cache flush/read, debug builds, and stale cache cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkidP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid_types.h.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid_types.h.in

Purpose: configure-generated fixed-width integer type header for libblkid.

Important APIs/types/functions: conditionally defines `__u8`, `__s8`, `__u16`, `__s16`, `__u32`, `__s32`, `__u64`, and `__s64` unless Linux/ext2/blkid types are already present. It can use assembler/kernel typedef macros supplied by `@ASM_TYPES_HEADER@` or choose C primitive types based on substituted `@SIZEOF_*@` values. Invalid configurations deliberately emit `?==error` tokens.

State and persistence: no runtime state. Generated output persists ABI type choices.

Dependencies and integration: generated by `config.status`; included by public `blkid.h` and downstream applications.

Risks and test signals: wrong size substitutions break ABI and `blkid_loff_t`. Test generated header on target compilers, existing type-header coexistence, 64-bit availability, and `tst_types`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/blkid_types.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/cache.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/cache.c

Purpose: owns allocation, initialization, cleanup, and garbage collection for libblkid caches.

Important APIs and control flow: `blkid_get_cache(ret_cache, filename)` allocates `struct blkid_struct_cache`, initializes device/tag list heads, chooses a cache filename from explicit argument, safe `BLKID_FILE`, or `/etc/blkid.tab`, duplicates it, then calls `blkid_read_cache`. `safe_getenv()` ignores environment variables for setuid/setgid or non-dumpable processes and uses `__secure_getenv` when available. `blkid_put_cache(cache)` flushes cache changes, frees devices, tag heads and dangling tags, filename, and cache. `blkid_gc_cache(cache)` stats each device path and removes missing devices.

State and persistence: owns in-memory cache lists and the cache filename; `blkid_flush_cache` persists changes on put or explicit flush.

Dependencies and integration: depends on `read.c`, `save.c`, `dev.c`, `tag.c`, safe environment behavior, and debug masks.

Risks and test signals: `blkid_get_cache` does not handle `blkid_strdup` failure explicitly, and cache operations are not synchronized. Test secure env suppression, missing cache files, GC deletion, flush-on-put, debug init, and memory cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/dev.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/dev.c

Purpose: manages blkid device object allocation/freeing and public device iteration.

Important APIs and control flow: `blkid_new_dev()` calloc-allocates a device and initializes its list heads. `blkid_free_dev(dev)` removes it from the cache device list, frees all attached tags through `blkid_free_tag`, frees the name, and releases the struct. `blkid_dev_devname(dev)` returns `bid_name`. Iterator APIs allocate a magic-checked iterator, optionally install copied tag search criteria, walk `cache->bic_devs`, filter through `blkid_dev_has_tag`, and free iterator state at end.

State and persistence: device objects are intrusive-list members owned by a cache. Iterators hold traversal position and optional copied search strings.

Dependencies and integration: depends on `blkidP.h`, `list.h`, and tag APIs. Test program exercises iteration and search.

Risks and test signals: `blkid_dev_iterate_end` leaks `search_type` and `search_value`; iteration is invalid if cache mutates concurrently. Test allocation/free, filtered iteration, iterator misuse magic checks, and debug dumps.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devname.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devname.c

Purpose: resolves device names, probes block devices, and populates the blkid cache from system enumeration sources.

Important APIs and control flow: `blkid_get_dev(cache, devname, flags)` finds or creates a cache entry and optionally verifies it with `blkid_verify`; verified entries trigger stale duplicate cleanup by matching type/label/UUID. `probe_one()` resolves a `/proc/partitions` name and `dev_t` to a path using `/dev`, `/devfs`, `/devices`, `/dev/mapper`, sysfs DM names, or exhaustive `blkid_devno_to_devname`, then probes with `BLKID_DEV_NORMAL` and assigns priority. `probe_all()` rate-limits using `BLKID_PROBE_INTERVAL`, reads cache, scans EVMS and old LVM `/proc` hierarchies, parses `/proc/partitions`, skips extended partitions, removes whole-disk cache entries when partitions exist, probes remaining devices, and flushes the cache. `blkid_probe_all` and `blkid_probe_all_new` expose full and new-only scans.

State and persistence: mutates device entries, priorities, verification flags, cache probed time, and on-disk cache via flush.

Dependencies and integration: integrates with `probe.c`, `devno.c`, `cache.c`, `/proc`, `/sys`, and device nodes.

Risks and test signals: old kernel/proc heuristics, real-device side effects, fixed path buffers, and stale duplicate removal are risky. Test with loop devices, DM leaf/non-leaf maps, LVM/EVMS absence, partitioned disks, new-only scans, and unreadable devices.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devno.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devno.c

Purpose: maps a block device number (`dev_t`) back to a pathname by scanning device directories.

Important APIs and control flow: `blkid_strndup` and `blkid_strdup` provide local string duplication helpers. `blkid__scan_dir(dirname, devno, list, devname)` scans one directory, skipping dot entries and overlong paths, stats children, returns the first block device whose `st_rdev` matches, and optionally queues real subdirectories for breadth-first traversal. `blkid_devno_to_devname(devno)` seeds `/devices`, `/devfs`, and `/dev`, then performs breadth-first directory scanning until a matching path is found or all lists are exhausted.

State and persistence: uses transient `dir_list` queues and returns an allocated pathname owned by the caller. No persistent state.

Dependencies and integration: used by `devname.c` fallback resolution and DM mapper scanning. Depends on `stat`, `lstat`, directory APIs, and `makedev` configuration.

Risks and test signals: recursive scan can be expensive, follows `stat` for device checks, and uses fixed 1024-byte path buffer. Test matching device numbers, symlink directories, permission-denied directories, no-match behavior, and breadth-first preference.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/devno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/getsize.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/getsize.c

Purpose: determines the byte size of an open block device or regular file.

Important APIs and control flow: `blkid_get_dev_size(fd)` tries platform-specific ioctls in preferred order: Darwin block count, Linux `BLKGETSIZE64` except old 2.5 kernels, legacy `BLKGETSIZE`, BSD `DIOCGMEDIASIZE`, floppy `FDGETPRM`, and disklabel partitions. For regular files it returns `st_size`. If all specialized methods fail, it performs exponential then binary search using `valid_offset()`, which seeks and reads one byte to find the last valid offset.

State and persistence: no persistent state; it changes the file descriptor offset during probing.

Dependencies and integration: used by probing code to bound reads. Depends on `blkid_llseek`, ioctl headers, `uname`, `fstat`, and platform disk headers.

Risks and test signals: binary search fallback can be slow or disruptive for unusual devices, and old-kernel checks are heuristic. Test block devices, regular files, zero-length files, old ioctl failures, large devices beyond 32-bit offsets, and final fd offset expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/getsize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/libblkid.3.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/libblkid.3.in

Purpose: generated manual page source describing libblkid’s role and cache model.

Important content and control flow: documents inclusion of `<blkid/blkid.h>` and linking with `-lblkid`; explains that libblkid identifies block-device content, labels, UUIDs, and serial-like identifiers. It emphasizes the `/etc/blkid.tab` cache, verification of cached data when raw-device access is available, the `BLKID_FILE` override, and why cache use matters for multi-device scans and modular-kernel visibility.

State and persistence: describes persisted cache state in `/etc/blkid.tab`; generated substitutions fill e2fsprogs version/date.

Dependencies and integration: installed by `Makefile.in` as section 3 man page; references `blkid(8)`.

Risks and test signals: documentation can drift from implementation, especially cache path, privilege behavior, and licensing text. Test generated man rendering, substitution values, and consistency with `blkid_get_cache` safe environment handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/libblkid.3.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/list.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/list.h

Purpose: provides a small Linux-kernel-style intrusive doubly linked list implementation for libblkid internals.

Important APIs/types/functions: `struct list_head` stores `next`/`prev`. Macros/functions include `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `__list_add`, `list_add`, `list_add_tail`, `__list_del`, `list_del`, `list_del_init`, `list_empty`, `list_splice`, `list_entry`, `list_for_each`, and `list_for_each_safe`.

State and persistence: no global state. List membership is embedded in owning structs such as devices and tags.

Dependencies and integration: included by `blkidP.h`; guarded to avoid conflict if a system `LIST_HEAD` already exists. Supports C++ linkage wrappers.

Risks and test signals: no runtime validation, type safety, or poisoning after delete; misuse can corrupt cache graphs. Test add/delete/splice ordering, safe iteration while freeing, empty-list behavior, and `list_entry` offsets on supported compilers.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/llseek.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/llseek.c

Purpose: abstracts large-file seek support for libblkid across old Linux and non-Linux systems.

Important APIs and control flow: `blkid_llseek(fd, offset, whence)` uses normal `lseek` when `off_t` can represent the requested offset. On Linux it prefers `lseek64`, then `llseek`, then the `_llseek` syscall wrapper where needed. If an old kernel lacks `_llseek`, a static `do_compat` flag suppresses future attempts and returns `EOVERFLOW`. Non-Linux builds use `lseek64` when available or reject unrepresentable offsets with `EOVERFLOW` before falling back to `lseek`.

State and persistence: Linux fallback stores `do_compat` process-wide after `ENOSYS`. It mutates the fd offset.

Dependencies and integration: used by `getsize.c` and block probing reads. Depends on large-file feature macros, syscall headers, errno, and configured type sizes.

Risks and test signals: old syscall declarations and 32-bit boundary logic are platform-sensitive. Test offsets below/above 2 GiB, ENOSYS fallback, non-Linux `lseek64`, `EOVERFLOW`, and preservation of errno semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/llseek.c -->
