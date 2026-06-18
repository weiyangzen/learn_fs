# Research: subset-b-009536

Grouped source research for the requested xfstests-bld/popt work item. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.c

Purpose: core implementation of the popt option parser. It creates and owns `poptContext`, walks option tables, handles long/short options, alias expansion, exec expansion, leftover arguments, stripped arguments, callbacks, typed argument storage, and experimental Bloom-filter style `poptBits`.

Important APIs/functions: `poptGetContext`, `poptResetContext`, `poptGetNextOpt`, `poptGetOptArg`, `poptGetArg`, `poptPeekArg`, `poptGetArgs`, `poptFreeContext`, `poptAddAlias`, `poptAddItem`, `poptBadOption`, `poptStrerror`, `poptStuffArgs`, `poptStrippedArgv`, numeric save helpers, string/argv/bitset helpers, and `poptSetExecPath`. Private helpers include callback walkers, `handleAlias`, `handleExec`, `findOption`, `expandNextArg`, and `execCommand`.

Control flow: callers allocate a context with the original argv and option table, then repeatedly call `poptGetNextOpt`. The parser pops exhausted alias/stuffed frames, identifies leftovers and `--`, parses long options including `--opt=arg`, falls back to short-option clusters, expands aliases by pushing a new `optionStackEntry`, records an exec item for post-parse `execvp`, locates table entries recursively, fetches required/optional arguments, saves typed values, invokes callbacks, and returns option `val` when appropriate. End of input triggers POST callbacks, optional `maincall`, or an exec command.

State/persistence: `poptContext_s` persists argv stack frames, leftovers, aliases, execs, final argv, app name, exec path, optional help text, and strip bitmaps until reset/free. Alias/stuffed argv are duplicated into heap storage; `finalArgv` is rebuilt across parsing. `poptBits` uses global tunables `_poptBitsN/M/K` and hashes from `poptJlu32lpair`. Random numeric options use a static seed.

Dependencies/integration: depends on `system.h`, `poptint.h`, libc allocation/string/process APIs, `execvp`, `PATH`, `POSIXLY_CORRECT`/`POSIX_ME_HARDER`, and option/config records created by `poptconfig.c`. Help output and tests consume the public API declared in `popt.h`.

Risks: many allocation failures are commented as impossible; several realloc assignments overwrite original pointers. `execCommand` deliberately executes configured commands after dropping privileges when possible, so config-file trust matters. Type punning and alignment checks are architecture-sensitive. `poptBitsDel` clears Bloom-filter bits and can create false negatives. Alias recursion is bounded by `POPT_OPTION_DEPTH`, but complex alias/argument substitution still has subtle side effects.

Test signals: `test1.c` and `testit.sh` exercise option parsing, aliases, execs, optional arguments, callbacks, POSIX mode, numeric conversions, bit operations, `POPT_ARG_ARGV`, `POPT_ARG_BITSET`, help/usage, and leftovers. `tdict.c` exercises `poptBits`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.h -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.h

Purpose: public API and ABI contract for the popt library. It defines option table syntax, argument types, modifier flags, error codes, context flags, alias/item structures, callback signatures, helper macros, and all exported parsing/config/help functions.

Important APIs/types: `struct poptOption`, `struct poptAlias`, `poptItem`, abstract `poptContext`, `poptCallbackType`, and `enum poptCallbackReason`. Key macros include `POPT_ARG_*`, `POPT_ARGFLAG_*`, `POPT_CBFLAG_*`, `POPT_ERROR_*`, `POPT_CONTEXT_*`, `POPT_AUTOHELP`, `POPT_AUTOALIAS`, and `POPT_TABLEEND`. Public functions include context lifecycle, parsing, config readers, argv parsing/duplication, help/usage, exec path, stripping, typed value savers, and `poptBits` operations.

Control flow: applications declare one or more `struct poptOption` arrays ending in `POPT_TABLEEND`, obtain a `poptContext`, then loop on `poptGetNextOpt`. Options with nonzero `val` can return control to the caller; options with `arg` pointers can be saved automatically. Included tables and callback rows affect recursive parsing and event handling.

State/persistence: the header exposes opaque context ownership rules and documents which arrays/strings are duplicated or retained. `poptItem` stores alias/exec metadata and argv arrays. `poptBits` is an allocated bitset whose storage is application-owned after use.

Dependencies/integration: includes `stdio.h` for `FILE *` and is consumed by all popt C files plus downstream programs. It carries Splint annotations, indicating long-standing ABI and static-analysis compatibility concerns.

Risks: flag values share bit fields, so callers must combine argument types and modifiers carefully. Some APIs return owned memory (`poptGetOptArg`, parse/dup helpers), while option-table strings are often borrowed; ownership mistakes can leak or double-free. Experimental flags such as `POPT_ARG_MAINCALL`, `POPT_ARG_BITSET`, `POPT_ARGFLAG_RANDOM`, and toggle/logical modifiers need targeted tests.

Test signals: `test1.c`, `test2.c`, `tdict.c`, and `testit.sh` collectively exercise most declared parser, config, help, numeric, argv, and bitset surfaces.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.pc.in -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.pc.in

Purpose: pkg-config template for installed popt consumers. It records install prefixes, library path, include path, package name, version, description, link flags, and C preprocessor include flags.

Important fields: `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Version`, `Description`, `Libs`, and `Cflags`. `@VERSION@`, `@POPT_PKGCONFIG_LIBS@`, and directory variables are substituted by the build system.

Control flow/state: no runtime control flow. The generated `popt.pc` is persistent install metadata used by `pkg-config --libs popt` and `pkg-config --cflags popt`.

Dependencies/integration: integrates autotools/configure substitution with downstream build systems. `Libs` is intentionally template-driven so platform-specific library requirements can be injected.

Risks: incorrect substitution of `libdir`, `includedir`, or `POPT_PKGCONFIG_LIBS` breaks consumers at compile/link time. The file does not include `Requires`, so transitive dependencies must be encoded in `Libs` if needed.

Test signals: package installation tests or downstream compile tests should validate that generated `popt.pc` points to installed `popt.h` and libpopt.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.spec.in -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.spec.in

Purpose: RPM spec template for building and packaging popt. It describes metadata, build requirements, source location, configure/make/install phases, language file handling, package file list, release tracking, and changelog.

Important sections: `%description`, `%prep`, `%build`, `%install`, `%check`, `%track`, `%clean`, `%files`, and `%changelog`. It installs libpopt, `popt.h`, man pages, and `popt.pc`.

Control flow/state: RPM expands macros, unpacks the source, runs `%configure`, builds, stages into `$RPM_BUILD_ROOT`, runs `make check || :`, and packages installed artifacts with generated `popt.lang`. Persistent outputs are RPM binaries/source packages and installed filesystem entries.

Dependencies/integration: depends on RPM macro environment, gettext, autotools install targets, and pkgconfig directory macros. The `%track` stanza appears RPM5-specific and monitors upstream tarball versions.

Risks: `%check` ignores failures, which prevents test failures from blocking packaging. The `License: X Consortium` and old source URL may need validation in modern packaging. Macro overrides for `_libdir` and `_pkgconfigdir` may conflict with distro policies.

Test signals: RPM build logs should confirm `%find_lang`, installed file ownership, and downstream `rpm -ql` paths; `make check` output still matters even though failure is tolerated.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popt.spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptconfig.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/poptconfig.c

Purpose: implements popt config-file support and convenience initialization. It reads config files, parses application-specific alias/exec declarations, expands globbed config paths, checks file sanity, and wires config-defined items into a `poptContext`.

Important functions: `poptSaneFile`, `poptReadFile`, `poptReadConfigFile`, `poptReadConfigFiles`, `poptReadDefaultConfig`, `poptInit`, and `poptFini`. Private helpers include `poptGlob`, `configAppMatch`, and `poptConfigLine`.

Control flow: `poptReadConfigFiles` splits colon-delimited path lists, optionally applies `@` sanity checks, expands globs, and calls `poptReadConfigFile`. File reading can trim escaped newlines. `poptReadConfigFile` builds logical lines, skips comments/blank lines, and sends each line to `poptConfigLine`. A config line must match the current app name, specify `alias` or `exec`, identify an option or file-backed option, parse replacement argv with `poptParseArgvString`, strip `--POPTdesc`/`--POPTargs` metadata, then call `poptAddItem`.

State/persistence: aliases and exec entries are persisted inside `con->aliases`/`con->execs`. File buffers and glob arrays are temporary. Default config reads from configured sysconfdir, `/etc/popt`, `/etc/popt.d/*`, and `$HOME/.popt`.

Dependencies/integration: uses `glob`, `fnmatch`, `stat`, `open/read/lseek`, environment `HOME`, `POPT_SYSCONFDIR`, parser APIs in `poptparse.c`, and item insertion in `popt.c`.

Risks: `poptSaneFile` appears inverted or at least surprising: it returns `1` for stat failure and for regular owner-owned files that are not group/world writable, while several comments say `0 on OK`. `poptConfigLine` forcibly returns success even after parse failures, hiding invalid lines. Config files can define exec aliases, so trust boundaries are important. Globs and `@` sanity behavior are subtle and should be tested with real permissions.

Test signals: `test-poptrc.in`, `test1.c`, and `testit.sh` verify aliases, execs, `--POPTdesc`, `--POPTargs`, default config via `HOME`, and alias argument substitution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popthelp.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/popthelp.c

Purpose: implements automatic help and usage output for popt option tables, including built-in `--help`/`--usage`, nested tables, aliases/execs, default values, i18n domains, wrapping, terminal-width detection, and multibyte display width.

Important APIs/functions: exported globals `poptAliasOptions`, `poptHelpOptions`, `poptHelpOptionsI18N`, and functions `poptPrintHelp`, `poptPrintUsage`, `poptSetOtherOptionHelp`. Private helpers include `displayArgs`, `maxColumnWidth`, `stringDisplayWidth`, `getTableTranslationDomain`, `getArgDescrip`, `singleOptionDefaultValue`, `singleOptionHelp`, `singleTableHelp`, `singleOptionUsage`, `singleTableUsage`, `showShortOptions`, and alias/exec item printers.

Control flow: applications include `POPT_AUTOHELP` in option tables. When help/usage options are parsed, `displayArgs` prints and exits. `poptPrintHelp` emits a usage intro, optional other-help text, computes left-column width, then recursively prints visible options and included tables. `poptPrintUsage` emits a compact one-line/multi-line synopsis with deduplication of included tables and appended alias/exec usage.

State/persistence: reads context state such as `con->options`, aliases, execs, flags, argv0, and `otherHelp`; writes only to `FILE *`. It allocates temporary column/dedup/default strings and frees them.

Dependencies/integration: uses `system.h`, `poptint.h`, gettext macros, `POPT_fprintf`, terminal `TIOCGWINSZ`, `mbsrtowcs`, and parser-internal context fields. Help tables are part of the public API via `popt.h`.

Risks: help formatting is sensitive to terminal width, locale, multibyte conversion, and exact option-table layout. `displayArgs` exits the process, so embedding applications need to expect that behavior. Some buffer sizing relies on estimates; default string truncation and wide-character display padding need regression tests.

Test signals: `testit.sh` contains exact expected `--usage` and `--help` output for `test1`, covering wrapping, defaults, hidden options, aliases/execs, included tables, and callback headings.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/popthelp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.c

Purpose: internal support routines for popt: UTF-8 character stepping, gettext domain handling in UTF-8, locale conversion for formatted help output, and inclusion of the Jenkins lookup3 pair hash used by `poptBits`.

Important functions: `POPT_prev_char`, `POPT_next_char`, optional `POPT_dgettext`, optional `strdup_locale_from_utf8`, and `POPT_fprintf`. The file also maps `lookup3.c` into `poptJlu32lpair`.

Control flow: help/wrapping code calls character stepping to avoid splitting UTF-8 continuation bytes. `POPT_fprintf` formats into a dynamically allocated UTF-8 buffer, optionally converts to the current locale using iconv, then writes to the stream. `POPT_dgettext` temporarily binds a translation domain to UTF-8.

State/persistence: mostly stateless, but gettext domain codeset binding is temporarily mutated and restored. Formatted buffers and converted strings are temporary allocations.

Dependencies/integration: depends on `system.h`, `poptint.h`, `stdarg`, optional gettext/libintl, iconv, langinfo, and bundled `lookup3.c`. `popt.c` uses the hash for Bloom filters; `popthelp.c` uses formatting and character navigation.

Risks: `POPT_prev_char` assumes the caller is not at the beginning of a string and scans backward until a non-continuation byte. Locale conversion has complex error/realloc paths and may lose text on invalid input. The static `utf8_skip_data` table is present but not used by the stepping helpers.

Test signals: help wrapping under non-ASCII locales and `tdict.c`/bitset usage are the main indirect tests. Exact ASCII help tests do not fully cover iconv or multibyte behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.h -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.h

Purpose: private header shared by popt implementation files. It exposes internal memory helpers, bitmask helpers, argument pointer union, context layout, option-stack state, i18n macros, and internal function declarations.

Important types/macros: `_free`, `pbm_set`, PBM allocation/set/clear/test macros, `poptArg`, `_poptArgMask`, `_poptGroupMask`, `poptArgType`, `poptGroup`, `F_ISSET`, `LF_ISSET`, `CBF_ISSET`, `poptSubstituteHelpI18N`, `struct optionStackEntry`, and `struct poptContext_s`.

Control flow/state: `optionStackEntry` is the parser frame used for original argv, aliases, and stuffed args. `poptContext_s` stores parser stack, leftovers, option table, aliases/execs, final argv, maincall, deferred exec, exec search path, help text, and stripped-argument bitmap. Macros drive flag decoding throughout `popt.c` and `popthelp.c`.

Dependencies/integration: includes `stdint.h`, optional iconv/langinfo/libintl headers, and depends on public types from `popt.h` via `system.h`. It declares `POPT_fprintf`, `POPT_dgettext`, `POPT_prev_char`, and `POPT_next_char` for use across files.

Risks: because this header exposes private structure layout to all implementation files, accidental field changes affect ABI assumptions inside the library. PBM macros assume correctly sized allocations and valid indices. `poptSubstituteHelpI18N` mutates option table pointers as a compatibility hack.

Test signals: parser, help, config, and bitset tests exercise this indirectly; structural issues usually show as parse failures, memory leaks, or crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptparse.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/poptparse.c

Purpose: argv utility layer for popt. It duplicates argv arrays into compact heap storage, parses shell-like strings into argv arrays, and converts simple config files into command-line option strings.

Important functions: `poptDupArgv`, `poptParseArgvString`, and `poptConfigFileToString`.

Control flow: `poptDupArgv` validates argc/argv, computes one allocation containing pointer table plus string data, copies each argument, and returns argc/argv to caller. `poptParseArgvString` tokenizes input using whitespace, single/double quotes, and backslash escaping, grows a temporary argv pointer array, then delegates to `poptDupArgv`. `poptConfigFileToString` reads `name` or `name=value` lines, ignores comments/invalid/missing-value lines, and emits a space-prefixed string of `--name` or `--name="value"` options.

State/persistence: returned argv arrays are heap-owned by the caller and freed as a single block. Temporary parse buffers are freed before return.

Dependencies/integration: used by config parsing and tests. Relies on `_isspaceptr`, `stpcpy`, and popt error codes from `system.h`/`popt.h`.

Risks: `poptParseArgvString` calls `strlen(s)` without NULL guarding. Realloc failure of `argv` loses the old pointer. `poptConfigFileToString` is documented as development-stage, has fixed line buffer length, silently ignores invalid lines, and preserves embedded newlines in quoted values unless stripped by earlier logic.

Test signals: `test-poptrc` alias parsing, `testit.sh` alias/exec tests, and any config-file conversion tests validate quote/escape behavior and single-allocation ownership.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/poptparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/system.h -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/system.h

Purpose: portability and common include header for popt sources. It centralizes config includes, libc headers, whitespace macro, allocation wrappers, `stpcpy` fallback, secure getenv mapping, unused attribute, and inclusion of `popt.h`.

Important APIs/macros: `_isspaceptr`, `xmalloc`, `xcalloc`, `xrealloc`, `xstrdup`, fallback `stpcpy`, optional mcheck-backed allocation macros, secure `getenv` remap to `__secure_getenv`, and `UNUSED`.

Control flow/state: no runtime control flow beyond inline `stpcpy` and macro-expanded allocation calls. Allocation wrappers either call libc directly or exit on failure when mcheck/GCC macros are enabled.

Dependencies/integration: consumed by all popt C files and tests. Pulls in `config.h` when available, standard headers, optional `unistd.h`, and public `popt.h`.

Risks: macro replacement of allocation functions changes failure semantics across build configurations. `xstrdup` maps to `strdup` and can return NULL unless the mcheck macro branch is used. The secure getenv remap changes environment behavior for setuid-like contexts.

Test signals: portability builds across platforms and memory-check builds are the relevant coverage; normal parser tests exercise the macros indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/tdict.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/tdict.c

Purpose: sample/test program for `poptBits` Bloom-filter functionality using a dictionary file. It loads `/usr/share/dict/words`, builds a bitset, converts leftover command arguments into another bitset, intersects them, and reports membership hits/misses.

Important functions/state: `loadDict` reads words, strips whitespace/comments, and calls `poptSaveBits`. Global options expose `--debug` and toggleable `--verbose`. Globals track dictionary filename, `dictbits`, and hit/miss counters.

Control flow: main first counts dictionary lines to scale `_poptBitsN/M/K`, parses command options, reloads dictionary into `dictbits`, builds `avbits` from remaining args with `poptBitsArgs`, intersects a copy with dictionary bits, then checks each leftover word with `poptBitsChk`.

State/persistence: bitsets are heap allocations and freed at exit. Global `poptBits` sizing values are modified before bitset creation, affecting subsequent poptBits allocations in this process.

Dependencies/integration: depends on popt parser, `poptBits` API, libc file I/O, and a system dictionary path. It includes `system.h`, `stdio.h`, and `popt.h`.

Risks: Bloom filters can false-positive; this test cannot prove exact dictionary membership. Missing dictionary file makes the program fail. `poptBitsDel` semantics are not tested here.

Test signals: useful as a smoke test for `poptSaveBits`, `poptBitsArgs`, union/intersection, and toggle options; output includes bitset sizing and hit/miss totals.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/tdict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/test-poptrc.in -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/test-poptrc.in

Purpose: popt configuration fixture for `test1`. It defines aliases and exec entries used by the shell test harness to validate config-file parsing, alias expansion, argument substitution, and help metadata.

Important entries: aliases for `--simple`, `--two`, `--takerest`, `-T`, `-O`, `--grab`, `--grabbar`, and `-e`; exec entries for `--echo-args` and `-a` mapped to `/bin/echo`; `--POPTdesc` and `--POPTargs` metadata make `--simple` visible in help.

Control flow/state: when read by `poptReadConfigFile`, matching lines for app `test1` become `con->aliases` or `con->execs`. Aliases are later expanded by `handleAlias`; execs are deferred until parser completion by `handleExec`/`execCommand`.

Dependencies/integration: consumed by `test1.c` and `testit.sh`; requires parser support for quote handling and `!#:+` next-argument substitution.

Risks: because exec entries can run external commands, production config files require trusted locations and sane permissions. The fixture uses shell-style quoted strings that depend on `poptParseArgvString` behavior.

Test signals: most alias and exec cases in `testit.sh` depend on this file, including `--simple`, `--two`, `--takerest`, `--grab`, and `--echo-args`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/test-poptrc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/test1.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/test1.c

Purpose: comprehensive popt test program used by `testit.sh`. It declares a large option table covering flags, typed arguments, callbacks, included tables, aliases/execs, help, optional args, bit operations, argv accumulation, and bitsets, then prints a normalized summary for comparison.

Important functions/state: `option_callback` prints callback events on the second parse pass; `resetVars` resets all globals and frees accumulated argv/bitset state; `main` reads config/defaults, parses once, resets context and variables, parses again, and prints changed values plus leftovers.

Control flow: the deliberate two-pass parse tests `poptResetContext`. The option table includes callback tables before/after normal options, `POPT_AUTOALIAS`, and `POPT_AUTOHELP`. Main handles errors with `poptBadOption`/`poptStrerror`, then emits deterministic output based on globals modified by parsing.

State/persistence: many globals hold option targets. `aArgv` strings are caller-owned and freed in `resetVars`; `aBits` is cleared but not freed until process exit. The context stores aliases from `test-poptrc` and default config.

Dependencies/integration: depends on the popt library, `test-poptrc`, `$HOME/.popt` behavior via default config, and the shell harness's expected output.

Risks: exact output is sensitive to help wrapping width and program name (`lt-test1` under libtool). Floating comparisons use direct inequality for test reporting. Memory ownership of string options intentionally leaks or is process-lifetime in the library design.

Test signals: `testit.sh` has nearly sixty cases against this program, making it the strongest regression signal for parser behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/test1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/test2.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/test2.c

Purpose: "real world" popt test program modeling a create-user style command with grouped option tables for transaction, database, and user fields. It checks nested include tables and config-file defaults.

Important state/APIs: global string and integer fields represent command options. `userOptionsTable`, `transactOptionsTable`, and `databaseOptionsTable` are included into `optionsTable`, which also includes `POPT_AUTOHELP`. Main calls `poptGetContext`, `poptReadConfigFile(rcfile)`, one `poptGetNextOpt`, and `poptFreeContext`.

Control flow: before parsing, include table `arg` pointers are filled at runtime. The rcfile defaults are read before parsing command-line options. The program calls `poptGetNextOpt` primarily to service `--help`, then prints all collected config/option values.

State/persistence: option values are global pointers updated by popt string parsing or config defaults. The parser context owns only its internal allocations; target strings assigned by `POPT_ARG_STRING` are duplicated and not explicitly freed by this program.

Dependencies/integration: depends on `system.h`/popt APIs and a `createuser-defaults` config file if used.

Risks: parsing only one option means it is not a general complete parser for all command-line options; it is intended as a bug reproducer/help/config test. Printed `%s` with NULL pointers may emit `(null)` on glibc but is not fully portable.

Test signals: useful for include-table help/config regressions, but it is not wired into the visible `testit.sh` active cases.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/test2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/testit.sh -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/testit.sh

Purpose: shell regression harness for popt test binaries. It runs `test1` with fixed argument combinations and compares full stdout to expected strings.

Important functions: `run` executes a program under `HOME=$builddir`, compares output exactly, and exits with code 2 on mismatch. `run_diff` exists for file-output tests but active `test3` calls are commented out.

Control flow: establishes `builddir`, changes to `srcdir`, then runs numbered test cases for basic options, aliases, rest handling, short options, POSIX modes, callbacks, exec aliases, one-dash long options, optional args, typed numeric conversions, `POPT_ARG_ARGV`, bit operations, bitsets, and exact `--usage`/`--help` text. Prints `Passed.` at the end.

State/persistence: temporary environment variables `POSIX_ME_HARDER` and `POSIXLY_CORRECT` are set/unset for specific cases. Temporary files from `run_diff` are removed if used. No persistent state except any logs from invoked programs.

Dependencies/integration: depends on compiled `test1`, `test-poptrc` in builddir/HOME, standard shell tools, `diff`, and deterministic terminal/help formatting.

Risks: exact string comparisons make tests fragile across locale, terminal width, binary prefix naming, and formatting changes. `run` uses backtick command substitution, which strips trailing newlines.

Test signals: high-value parser regression suite; failures identify specific numbered behaviors in popt core, config, help, and exec handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/testit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/update-all -->
# sources/test-tools/xfstests-bld/fstests-bld/update-all

Purpose: top-level build/update script for the fstests appliance userland components. It builds and installs dependency projects into a local `bld` destination, then records git version metadata for key repositories.

Important steps: source `config.custom` or `config`, compute parallelism from CPU count, set `DESTDIR`, build/install `e2fsprogs-libs`, `attr`, `acl`, `libaio`, `xfsprogs-dev`, `fio`, `xfstests-dev`, `quota`, and `misc`, remove `.la` files, and write `xfsprogs.ver`, `fio.ver`, `xfstests.ver`, and `quota.ver`.

Control flow/state: the script is run with `bash -vx`, so commands are echoed. Each component build runs in a subshell. Installed artifacts persist under `$(pwd)/bld`; version files persist in the fstests-bld directory.

Dependencies/integration: depends on repository checkout layout, make/libtool, config variables such as `EXEC_LLDFLAGS`, and git metadata. Outputs feed test appliance/release artifacts.

Risks: no `set -e`, so failures may not stop subsequent component builds. Hard-coded static linking/libtool flags can be host-sensitive. Parallel builds can expose race issues. Removing all `.la` files is broad but intentional.

Test signals: successful end-to-end appliance builds and version-file freshness in release scripts are the primary validation.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/update-all -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/install-kconfig -->
# sources/test-tools/xfstests-bld/kernel-build/install-kconfig

Purpose: installs a suitable kernel `.config` into the external kbuild directory, selecting a baseline config by architecture and kernel version and layering optional debug/test fragments.

Important options: `--perf`, `--blktests`, `--i386`, `--arm64`, `--arch`, `--dept`, `--kasan`, `--kcsan`, `--lockdep`, `--ubsan`, `--full-debug-info`, `--extra-debug`, `--generic`, `--get-config-fn`, and `--no-action`.

Control flow: sources `arch-funcs`, canonicalizes architecture, verifies kernel source root, gets build dir from `kbuild --get-build-dir`, reads `make kernelversion`, searches backward for the newest matching config fragment, appends architecture and optional fragments, backs up existing `.config`, writes the new config, appends tag-derived `CONFIG_LOCALVERSION`, and runs `make olddefconfig`.

State/persistence: writes `$BLD_DIR/.config`, may create `$BLD_DIR/.config.bak`, and modifies local version based on `# TAG:` lines. Does not modify git-tracked kernel sources directly.

Dependencies/integration: integrated with `kbuild`, `kernel-configs`, Linux kernel `Makefile`, `MAINTAINERS`, make, awk/sed, and cross-compile helpers.

Risks: config search stops at version 2 and assumes numeric minor versions. `tags` are read from the generated config even in no-action mode, where the file may not exist. Fragment ordering controls final Kconfig values and should be deliberate.

Test signals: `--get-config-fn`, no-action dry runs, and a successful `make olddefconfig` for each supported architecture validate behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/install-kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/install-kconfig.sh.in -->
# sources/test-tools/xfstests-bld/kernel-build/install-kconfig.sh.in

Purpose: install-time wrapper template for `install-kconfig`. It substitutes `@DIR@`, exports `KBUILD_DIR`, and execs the real script under `$DIR/kernel-build`.

Important control flow: fixed `DIR=@DIR@`, sets `KBUILD_DIR=$DIR/kernel-build`, exports it, and `exec`s `$KBUILD_DIR/install-kconfig "$@"`.

State/persistence: no persistent state; passes all arguments unchanged.

Dependencies/integration: generated by install tooling so users can run a stable command from `bin` while scripts live under `lib`.

Risks: incorrect `@DIR@` substitution breaks all wrapper invocations. Uses `/bin/sh`, so wrapper must remain POSIX shell.

Test signals: installed wrapper should resolve the real script and preserve arguments such as `--get-config-fn`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/install-kconfig.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/kbuild -->
# sources/test-tools/xfstests-bld/kernel-build/kbuild

Purpose: convenience kernel build driver for external object directories. It reads per-repository kbuild configuration, canonicalizes architecture, optionally installs configs, builds kernels or Debian packages, generates modules tarballs, and persists build config/cert material.

Important options: `--arch`, `--arm64`, `--i386`/`-32`, `--dpkg`, `--no-dpkg`, `--install-kconfig`, `--install-kconfig-opts`, `--oldconfig`, `--get-build-dir`, `--get-kbuild-config`, `--get-kbuild-dir`, `--no-action`, `--kunit`/`--test`, and `-j`.

Control flow: discovers git dir/common dir, ensures kernel source root, loads `.git/kbuild/config`, sets architecture/build dir overrides, builds `MAKE_ARGS` with `ARCH`, `O`, `CROSS_COMPILE`, and optional `CC=clang`, optionally runs install-kconfig/olddefconfig/KUnit, removes stale `.deb` symlinks, then either runs `make bindeb-pkg` and normalizes generated `.deb` names or runs ordinary `make`. On successful full builds it writes `.git_version`, installs modules into a temp dir, creates `modules.tar.xz`, and copies `.config` plus signing keys back to `.git/kbuild`.

State/persistence: creates/uses `$GITDIR/kbuild`, `$BLD_DIR`, `$BLD_DIR/.config`, `$BLD_DIR/modules.tar.xz`, normalized Debian package files, `.git_version`, and cached cert/key files.

Dependencies/integration: depends on git, Linux kernel make targets, dpkg tools for package mode, `arch-funcs`, install-kconfig, tar/xz, and optional clang/cross-compile settings. Outputs are consumed by kvm/gce xfstests.

Risks: build-directory selection depends on shell-sourced config. Debian version-number handling has kernel-version-specific logic. No-action mode still evaluates many shell tests. Module archive generation uses temp directories and must clean up on errors.

Test signals: `--get-build-dir`, no-action builds, package builds, successful `modules.tar.xz`, and subsequent kvm/gce boot tests validate this script.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/kbuild.sh.in -->
# sources/test-tools/xfstests-bld/kernel-build/kbuild.sh.in

Purpose: install-time wrapper template for the `kbuild` script. It resolves the installed library directory via `@DIR@`, exports `KBUILD_DIR`, and execs the real kernel build driver.

Important control flow: assigns `DIR=@DIR@`, `KBUILD_DIR=$DIR/kernel-build`, exports `KBUILD_DIR`, and `exec`s `$KBUILD_DIR/kbuild "$@"`.

State/persistence: none directly; all persistent behavior belongs to `kbuild`.

Dependencies/integration: generated into a user-facing bin path by install rules.

Risks: bad substitution of `@DIR@` or missing executable target breaks installed command.

Test signals: invoking installed `kbuild --get-kbuild-dir` should return the expected library tree.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/kbuild.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/kbuild32.sh.in -->
# sources/test-tools/xfstests-bld/kernel-build/kbuild32.sh.in

Purpose: install-time wrapper for 32-bit kernel builds. It is the same as `kbuild.sh.in` but appends `--32` before user arguments.

Important control flow: substitutes `@DIR@`, exports `KBUILD_DIR`, and `exec`s `$KBUILD_DIR/kbuild --32 "$@"`.

State/persistence: none directly.

Dependencies/integration: intended to provide a stable 32-bit build command, but the current `kbuild` parser recognizes `-32` and `--i386`, not `--32`.

Risks: likely option mismatch: this wrapper passes `--32`, while `kbuild` handles `--i386|-32)`. Unless another compatibility layer rewrites it, installed `kbuild32` will hit `unknown option: --32`.

Test signals: an installed-wrapper smoke test should invoke `kbuild32 --get-build-dir`; failure would confirm the option mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/kernel-build/kbuild32.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/README.in -->
# sources/test-tools/xfstests-bld/release/README.in

Purpose: release README template for KVM test appliance image bundles. It explains what the images are, where xfstests-bld lives, architecture guidance, quick-start documentation, GPL corresponding-source information, Debian distro source mirror, git repository versions, and image creation scripts.

Important placeholders: `@DISTRO@`, `@MIRROR@`, and `@VERFILE@` are replaced by `gen-README`.

Control flow/state: no executable logic. Generated README persists in `release/out_dir/README`.

Dependencies/integration: consumed by `release/gen-README`, which injects Debian mirror/distro and git version file content.

Risks: stale quick-start URL, distro name, mirror, or git-version data can make release compliance information inaccurate.

Test signals: release generation should verify placeholders are fully replaced and `@VERFILE@` content is present.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/README.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/gen-README -->
# sources/test-tools/xfstests-bld/release/gen-README

Purpose: generates `release/out_dir/README` from `README.in` by substituting Debian mirror/distro and inserting git-version metadata, with optional notes for tagged xfstests/blktests local changes.

Important variables: derives `DIR`, `BUILD_DIR`, `REL_DIR`, `OUT_DIR`, `APPLIANCE_DIR`, `MIRROR`, `distro`, `xfstests_rel`, and `blktests_rel`.

Control flow: resolves repository root based on script location, sources appliance `config.custom` if present, reads `xfstests/build-distro` when available, detects release tags pointing at current xfstests/blktests heads, creates output dir, runs `sed` with a read command to include `git-versions.amd64`, then appends local-change URLs for release tags.

State/persistence: writes `release/out_dir/README`.

Dependencies/integration: depends on git repos under `fstests-bld`, release output from snapshot steps, sed, realpath, and appliance config.

Risks: hard-coded `git-versions.amd64` means README version content depends on that architecture file. Unquoted paths in several subshells assume no spaces. Tag detection may produce multiple lines if multiple matching tags exist.

Test signals: generated README should have no placeholders and should include current git-version lines and optional release tag notes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/gen-README -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/snapshot-release -->
# sources/test-tools/xfstests-bld/release/snapshot-release

Purpose: assembles release output for all supported appliance architectures. It verifies required artifacts exist and are not newer than their git-version files, checks version consistency across architectures, copies artifacts into `release/out_dir`, and regenerates README.

Important functions: `check_file_exists` aborts on missing required files; `check_file_out_of_date` aborts if an artifact is newer than the version file.

Control flow: for `arm64 i386 amd64`, it checks `selftests/git-versions.$arch`, `fstests-bld/xfstests-$arch.tar.gz`, `test-appliance/root_fs.img.$arch`, and `test-appliance/root_fs.$arch.tar.gz`; compares version files against the first architecture; copies all files to output; runs `gen-README`.

State/persistence: creates/updates files under `release/out_dir`.

Dependencies/integration: depends on completed selftests/build artifacts for all architectures, `cmp`, `cp -p`, and `gen-README`.

Risks: bug in mismatch reporting uses `$f` when setting `b="$(basename $f)"`, but `$f` is not set in that scope. Freshness check direction assumes version files should be newer than artifacts. Missing one architecture blocks release.

Test signals: a dry release with intentionally stale/missing artifacts should abort; successful release should populate all expected out_dir files plus README.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/snapshot-release -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/upload-to-korg -->
# sources/test-tools/xfstests-bld/release/upload-to-korg

Purpose: signs and uploads release artifacts from `release/out_dir` to kernel.org using `kup`, with an optional testing destination.

Important functions: `usage`, `sign_file`, and `upload_file`. `FILES` lists README, root filesystem images/tarballs, and xfstests tarballs for amd64, i386, and arm64.

Control flow: resolves repo root, changes to `release`, processes `--testing`, lists output dir, validates all required files exist, signs each file, then uploads each file and its detached signature. For `.tar.gz`, it signs the uncompressed tar data by gunzipping to `/tmp`.

State/persistence: creates `.sig` files beside artifacts in `out_dir`; uses temporary uncompressed tar files under `/tmp`; uploads or removes remote files under `DEST`.

Dependencies/integration: requires `gpg2`, `kup`, `gunzip`, release output artifacts, and kernel.org upload credentials.

Risks: temporary `/tmp/$tar_fn` names can collide. `upload_file` uses `$i` in destination path instead of local `$1`, relying on loop-global state. No checksum verification after upload. Signing uncompressed tarballs is intentional but different from signing the distributed `.tar.gz` bytes.

Test signals: `--testing` upload, presence of `.sig` files, and kernel.org staging listings validate behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/release/upload-to-korg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/Makefile -->
# sources/test-tools/xfstests-bld/run-fstests/Makefile

Purpose: install helper for run-fstests assets. It installs the run-fstests tree under `$(prefix)/lib/kvm-xfstests`, installs wrapper scripts under `$(prefix)/bin`, and ensures a root filesystem image is available.

Important targets: `all` prints a message; `install` creates install dirs, archives/extracts the tree with optional `.gitignore` exclusions, removes `config.custom`, copies or downloads `root_fs.img`, and generates `kvm-xfstests`/`gce-xfstests` wrappers from `.in` templates.

Control flow/state: `TEST` probes whether tar supports `--exclude-ignore-recursive`. Persistent outputs are installed library tree, rootfs image, and executable wrappers.

Dependencies/integration: depends on tar, curl, shell, rootfs prebuilt URL, and wrapper templates.

Risks: downloading during install can be surprising or fail offline. Only kvm/gce wrappers are installed here, not android. The tar feature probe is command-output based and may vary by tar implementation.

Test signals: `make install DESTDIR=...` should install scripts, omit `config.custom`, and produce executable wrappers with substituted paths.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/android-xfstests -->
# sources/test-tools/xfstests-bld/run-fstests/android-xfstests

Purpose: Android runner for xfstests. It boots an optional kernel through fastboot, deploys an xfstests chroot/rootfs onto a rooted Android device, prepares partitions, runs tests or interactive shell commands, and captures logs.

Important functions: `die`, `ask_yesno`, `adb_ready`, `fastboot_ready`, `wait_for_device`, `reboot_into_fastboot_mode`, `query_kernel_version`, `extract_kernel_version`, `boot_kernel`, `chroot_prepare`, `chroot_wipe`, `chroot_run`, `chroot_interactive_shell`, `setup_chroot`, `try_shrink_userdata`, `setup_partitions`, `xfstests_running`, and `stop_existing_tests`.

Control flow: handles `install-kconfig`/`kbuild` passthrough commands, sources config and CLI parsing, sets log file, verifies adb/fastboot, stops existing tests unless shell-like command, loops through kernel boot, chroot deployment, and partition setup, optionally reformats userdata smaller, then either enters shell or pushes a generated `/run-xfstests` script and runs it through chroot with tee logging.

State/persistence: modifies the attached device: `/data/xfstests-chroot`, `/data/xfstests-results`, bind mounts, loop device nodes, chroot md5 marker, test partitions, and potentially userdata formatting. Host logs persist under `$DIR/logs` unless `SKIP_LOG`.

Dependencies/integration: depends on adb, fastboot, root adbd, permissive SELinux, rootfs tarball, android test appliance scripts, shared util config/CLI/arch functions, and optional kernel image.

Risks: destructive path can reformat userdata after confirmation. Root shell commands interpolate variables into adb shell heredocs, so paths must be trusted. Kernel-version extraction by grepping image banners is heuristic. Device state/mount cleanup failures can affect later runs.

Test signals: successful chroot md5 reuse, partition setup result files, kernel version verification, log output, and xfstests result summaries validate behavior; manual device tests are required.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/android-xfstests -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/android-xfstests.sh.in -->
# sources/test-tools/xfstests-bld/run-fstests/android-xfstests.sh.in

Purpose: install-time wrapper template for `android-xfstests`. It substitutes `@DIR@`, exports `ANDROID_XFSTESTS_DIR`, and execs the real runner.

Important control flow: `DIR=@DIR@`, `ANDROID_XFSTESTS_DIR=$DIR/run-fstests`, `export`, then `exec $ANDROID_XFSTESTS_DIR/android-xfstests "$@"`.

State/persistence: none directly.

Dependencies/integration: generated wrapper allows user-facing binary location to point at installed library tree.

Risks: the run-fstests Makefile in this subset installs kvm/gce wrappers, not this one; packaging must include it elsewhere if Android support is intended.

Test signals: installed wrapper should find `util/get-config` through the exported directory.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/android-xfstests.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/compress-rootfs -->
# sources/test-tools/xfstests-bld/run-fstests/compress-rootfs

Purpose: recompresses the default KVM root filesystem qcow2 image by converting to raw, running filesystem discard, then converting back to compressed qcow2.

Important commands: `qemu-img convert -f qcow2 -O raw`, `e2fsck -fy -E discard`, `qemu-img convert -f raw -O qcow2 -o compat=0.10 -c`, and cleanup of the raw image.

Control flow/state: uses fixed paths under `./test-appliance`, creates `root_fs.raw`, rewrites `root_fs.img`, then removes the raw file.

Dependencies/integration: depends on qemu-img and e2fsck. Intended as maintenance utility for the test appliance image.

Risks: destructive overwrite of `root_fs.img`; no `set -e`, so a failed command may allow later commands to run. Fixed `DIR=.` means it must be run from repository/run-fstests context.

Test signals: final qcow2 should pass `qemu-img check` and boot under kvm-xfstests.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/compress-rootfs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/dashboard/Dockerfile -->
# sources/test-tools/xfstests-bld/run-fstests/dashboard/Dockerfile

Purpose: container image definition for the GCE xfstests dashboard Flask app, suitable for Cloud Run-style deployment.

Important steps: base image `google/cloud-sdk`, sets `PYTHONUNBUFFERED`, copies app code to `/app`, installs Python packages `Flask`, `gunicorn`, `junit-xml`, and `junitparser`, then runs gunicorn bound to `$PORT`.

Control flow/state: image build bakes source into `/app`; runtime starts one gunicorn worker with eight threads and no timeout.

Dependencies/integration: needs Google Cloud SDK for `gcloud storage rsync`, Python/pip, dashboard.py, and environment variables consumed by the app.

Risks: unpinned pip dependencies can change behavior. `MAINTAINER` is deprecated. Running from a broad cloud-sdk base increases image size. One worker may limit CPU utilization.

Test signals: container should start with a dummy `$PORT`, import `dashboard:app`, and successfully execute `/sync` when credentials and `RESULTS_GS_PATH` are configured.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/dashboard/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/dashboard/dashboard.py -->
# sources/test-tools/xfstests-bld/run-fstests/dashboard/dashboard.py

Purpose: Flask dashboard for GCE xfstests results. It mirrors result tarballs from GCS, extracts them, parses JUnit XML, groups results by category/date/config, and provides a simple file browser.

Important functions/classes: `results_header`, `result_summary`, `get_results`, `get_property`, `run_shell_command`, `gs_rsync`, `extract_tarballs`, `setup_dirs`, Flask handlers `/favicon.ico`, `/sync`, `/`, `/files/<path>`, `/files/`, and `testresult`.

Control flow: root handler validates `RESULTS_GS_PATH`, ensures local dirs, triggers sync/extraction, walks extracted results, reads `results.xml`, optionally categorizes LTM watch jobs from nearby `ltm-info/report`, builds an HTML table by category/date/TESTCFG, and links each cell into the file browser. `/sync` runs `gcloud storage rsync` and extraction only when rsync output indicates changes.

State/persistence: local mirror path defaults to `/tmp/mirror`, extracted results to `/tmp/extracted/`; these persist for the container instance lifetime. No database is used.

Dependencies/integration: depends on Flask, junitparser, gcloud CLI, tar, mkdir/rm commands, result tarball layout, JUnit properties including `TESTCFG`, and Cloud credentials.

Risks: command construction uses string concatenation and `split(' ')`, so paths with spaces break. File browser concatenates requested paths under `extracted_dir` without normalization, creating path traversal risk. HTML is unescaped for file contents and metadata. `extract_tarballs` has a likely path check bug by joining `extract_path` twice.

Test signals: unit tests can cover parsing/grouping; integration tests should sync a fixture bucket/local tree, parse known results.xml, and validate file browser containment.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/dashboard/dashboard.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/gce-xfstests -->
# sources/test-tools/xfstests-bld/run-fstests/gce-xfstests

Purpose: primary Google Compute Engine runner and administration CLI for xfstests. It manages GCS artifacts/config, instance/disk/image/result commands, kernel uploads, LTM/KCS delegation, machine-type selection, and test VM creation.

Important functions: `get_local_hash`, `get_remote_hash`, `verify_single_uri`, `do_get_results_uri`, `do_get_results`, `get_gce_zone`, `get_gce_zone_disk`, `get_machtype_file`, `get_machtype_stats`, `fit_machtype_resources`, and `launch_vm`. It also exposes many subcommands through a large `case`: list/remove/start/stop instances, disks, images, results, ssh/scp/console/serial/describe, setup, image import/export/copy, kbuild/install-kconfig, upload-kernel, LTM/KCS launch/control, dashboard launch, and normal test launch.

Control flow: validates core config, handles early administrative subcommands, ensures bucket config exists, syncs selected config variables to `gs://$GS_BUCKET/gce_xfstests.config`, parses CLI for a test launch, computes test run id/instance name, resolves kernel/modules/hooks/test files to GCS URIs with hash-based upload avoidance, appends metadata arguments, chooses or validates a machine type, delegates to LTM/KCS if requested, ensures cert freshness, then creates a Compute Engine VM with metadata containing the xfstests command payload and retries selected resource/image-family failures.

State/persistence: persists GCS config/artifacts/results, local cache files under `$GCE_CACHE_DIR`, local config cache in `/tmp`, optional `.ltm_instance_$GCE_PROJECT`/`.kcs_instance_$GCE_PROJECT`, VM metadata, created instances/disks, and result tarballs under `/tmp` when fetched.

Dependencies/integration: depends heavily on shared util scripts (`get-config`, `parse_opt_funcs`, `arch-funcs`, `parse_cli`, LTM/KCS funcs), gcloud wrappers, GCS bucket/project/zone config, jq, openssl, sed/awk/tar/xz, kernel artifact introspection, and GCE image families.

Risks: very large shell script with many global variables and side-effectful subcommands. Metadata argument construction relies on shell quoting and `--metadata "^ ^$ARG"`. Hard-coded machine pricing can go stale. There is a syntax-looking bug in the cert check: `if test -f "$cert_file" ! openssl ...` is missing a command separator/operator. Remote deletion/upload commands are powerful and need careful project/bucket targeting.

Test signals: no-action launch output, `get-results` fixture tarballs, machine-type cache refresh, upload-kernel hash checks, and GCE integration tests for VM creation/deletion are needed. LTM/KCS paths require separate service tests.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/gce-xfstests -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/gce-xfstests.sh.in -->
# sources/test-tools/xfstests-bld/run-fstests/gce-xfstests.sh.in

Purpose: install-time wrapper template for `gce-xfstests`. It exports `GCE_XFSTESTS_DIR` and execs the installed runner.

Important control flow: substitutes `@DIR@`, sets `GCE_XFSTESTS_DIR=$DIR/run-fstests`, exports it, and execs `$GCE_XFSTESTS_DIR/gce-xfstests "$@"`.

State/persistence: none directly.

Dependencies/integration: generated by install Makefile for user-facing `gce-xfstests`.

Risks: path substitution must match the installed lib layout; otherwise the runner cannot find `util/get-config`.

Test signals: installed `gce-xfstests get-bucket` or `--no-action` commands should resolve the real script.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/gce-xfstests.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/get-results -->
# sources/test-tools/xfstests-bld/run-fstests/get-results

Purpose: summarizes xfstests log files by grepping high-signal lines, with an optional failures-only mode that detects a missing `END` marker.

Important behavior: default regexp captures kernel version, command line, FSTEST/MNTOPTS/CPU/MEM metadata, BEGIN/END, mount/mkfs options, ext4 errors, warnings, run/failure/pass lines, inconsistent output, and shutdown reason. `--failures` narrows the regexp and enables missing-END detection.

Control flow: parses `--summary` or `--failures`, selects input files from arguments or latest `logs/log.*`, runs `grep -E`, and in failures mode compares counts of `BEGIN` and `END` lines.

State/persistence: read-only except stdout. No temp files.

Dependencies/integration: used by `gce-xfstests get-results --summary/--failures` and manually against local logs.

Risks: grep-based parsing is format-fragile. Missing-END detection only reports the last BEGIN if counts differ and does not pair tests structurally.

Test signals: fixture logs with pass/fail/incomplete cases should validate summary and failures mode.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/get-results -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/kvm-xfstests -->
# sources/test-tools/xfstests-bld/run-fstests/kvm-xfstests

Purpose: local QEMU/KVM runner for xfstests. It prepares rootfs/test disks, stages updated test artifacts/modules, configures networking/virtfs, launches QEMU with the selected kernel, captures logs, and extracts result archives.

Important flow/options: handles `install-kconfig`, `kbuild`, and `setup` passthroughs; sources config and CLI parsing; downloads rootfs if missing; optionally builds kernel; validates kernel and test disks; configures networking, logs/results filenames, virtiofs/9p shares, modules and update tarballs, architecture-specific QEMU machine/console, and then runs `qemu-system-*`.

Control flow: creates a temporary VDH tar image as a communication disk, optionally appends xfstests/extra/files/modules tarballs, truncates it to 256M, starts QEMU with rootfs plus many virtio disks and metadata kernel args, tees serial output to log, extracts `exit_code` and `results.tar.xz` from VDH after VM exit, trims log summary, restores terminal line wrap, and exits with guest-provided status.

State/persistence: may download rootfs into `test-appliance`, create/update test disks via setup utility, create logs under `$DIR/logs`, results tarballs, temp VDH and extraction dirs, virtfs dirs under `/tmp`, and virtiofsd sockets/logs.

Dependencies/integration: depends on QEMU/KVM, kvm-do-setup, parse_cli config, kernel/modules artifacts from kbuild, rootfs image, tar, xz, wget, virtiofsd, and host network/tap setup.

Risks: powerful local VM command with many unquoted variable expansions from config. Virtiofsd background processes are started without explicit cleanup in this script. Rootfs download URL and qemu feature flags are host-sensitive. There is a typo in the scratch path default branch assigning `VIRTFS_SCRATCH_PATH` when checking `VIRTFS_SCRATCHTEST_PATH`.

Test signals: no-action command inspection, setup-created disks, successful boot/log/result extraction, and virtfs/9p specific configs are key validations.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/kvm-xfstests -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/kvm-xfstests.sh.in -->
# sources/test-tools/xfstests-bld/run-fstests/kvm-xfstests.sh.in

Purpose: install-time wrapper template for `kvm-xfstests`. It exports `KVM_XFSTESTS_DIR` and execs the installed local VM runner.

Important control flow: `DIR=@DIR@`, `KVM_XFSTESTS_DIR=$DIR/run-fstests`, export, then `exec $KVM_XFSTESTS_DIR/kvm-xfstests "$@"`.

State/persistence: none directly.

Dependencies/integration: generated by install Makefile for user-facing `kvm-xfstests`.

Risks: bad `@DIR@` substitution or missing run-fstests tree breaks the wrapper.

Test signals: installed wrapper should run `kvm-xfstests setup --help` or a no-action command and locate util scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/kvm-xfstests.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/qemu-xfstests.sh.in -->
# sources/test-tools/xfstests-bld/run-fstests/qemu-xfstests.sh.in

Purpose: compatibility wrapper template that points `qemu-xfstests` style invocations at the same implementation as `kvm-xfstests`.

Important control flow: substitutes `@DIR@`, exports `KVM_XFSTESTS_DIR=$DIR/run-fstests`, and execs `$KVM_XFSTESTS_DIR/kvm-xfstests "$@"`.

State/persistence: none directly.

Dependencies/integration: provides alternate installed command name while reusing kvm runner implementation.

Risks: name may imply non-KVM behavior, but it does not alter acceleration or options; users must configure `kvm-xfstests` options.

Test signals: wrapper smoke test should produce identical behavior to kvm wrapper for no-action commands.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/qemu-xfstests.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-Dashboard.yaml -->
# sources/test-tools/xfstests-bld/run-fstests/roles-Dashboard.yaml

Purpose: custom Google Cloud IAM role definition for dashboard-related deployment/runtime. It grants a broad set of Compute, IAM, Logging, Recommender, Resource Manager, Cloud Run, and Storage permissions.

Important fields: `stage: ALPHA`, title/description, and `includedPermissions`. Notable capabilities include compute instance/disk/image/network inspection and mutation, service account listing/actAs, extensive logging access, Cloud Run service/revision/route reads, and storage object create/delete/get/list/update.

Control flow/state: declarative YAML; applied by gcloud/IAM tooling to create or update a custom role. Persistent state lives in GCP IAM.

Dependencies/integration: supports the xfstests dashboard and related launch utilities that need Cloud Run, storage, logging, and compute visibility.

Risks: permission set is very broad for a dashboard role, including many mutating Compute and Logging operations plus storage delete. Principle-of-least-privilege review is warranted before production use.

Test signals: deployment should verify the dashboard can sync/read results and serve without requiring unused mutation permissions; IAM policy simulator can reduce scope.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-Dashboard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-ImgCreate.yaml -->
# sources/test-tools/xfstests-bld/run-fstests/roles-ImgCreate.yaml

Purpose: custom Google Cloud IAM role for VMs that create/export/import/copy xfstests images.

Important permissions: compute disk create/delete/snapshot/use, image create/delete/deprecate/get/list/setLabels/update/useReadOnly, instance attach/detach/stop/update/use, network/subnetwork use, serviceAccount actAs, logging operations, resource manager project get, and storage object create/get/list/update.

Control flow/state: declarative role file applied to GCP IAM. Persistent effect is a custom role with ALPHA stage.

Dependencies/integration: used by image creation/export tooling referenced by `gce-xfstests create-image`, `export-image`, `import-image`, and `copy-image`.

Risks: broad compute and logging permissions, though more image-focused than LTM/KCS. It lacks `storage.objects.delete`, which may be intentional for image creator safety. ALPHA stage signals role instability.

Test signals: image creation pipeline should validate the exact role can create disks/images, upload objects, and complete without owner/editor privileges.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-ImgCreate.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-LTMKCS.yaml -->
# sources/test-tools/xfstests-bld/run-fstests/roles-LTMKCS.yaml

Purpose: custom Google Cloud IAM role for long-term monitoring (LTM) and kernel compile server (KCS) VMs. It grants permissions needed to manage compute resources, read images, manipulate instances/disks/networks, write logs, and interact with storage.

Important permissions: broad compute instance lifecycle operations, disk create/delete/resize/snapshot/update/use, image get/list/useReadOnly, network/subnetwork use and update, service account actAs/list/get, extensive logging permissions, project get, and storage object create/delete/get/list/update.

Control flow/state: declarative YAML for GCP custom role creation/update. Its effect persists in IAM and is consumed by service accounts used by LTM/KCS instances.

Dependencies/integration: supports `gce-xfstests launch-ltm`, `launch-kcs`, LTM batch submission, KCS build delegation, and VM self-management workflows.

Risks: very high privilege role, including instance create/delete/update, network mutation, storage delete, and service account actAs. A compromised LTM/KCS VM would have wide project impact. Scope should be isolated to a dedicated project where possible.

Test signals: LTM/KCS integration tests should verify required operations under this role; IAM recommender/policy analysis can identify unused permissions for reduction.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-LTMKCS.yaml -->
