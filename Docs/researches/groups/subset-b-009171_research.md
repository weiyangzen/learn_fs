# Research Report: subset-b-009171

This grouped report covers the subset B source files requested for rsync and its bundled popt/test/web helper files. Each file section is bounded by reconciliation markers so the final per-file research documents can be split into source-tree-aligned paths.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/popt.h -->
# sources/sync-backup/rsync/popt/popt.h

Purpose: Public API header for the bundled popt option parser. It defines option table syntax, argument type constants, flag bits, error codes, context flags, alias/exec item records, callback contracts, and exported parser/config/help functions used by popt consumers.

Important APIs, types, and functions: `struct poptOption` is the core option descriptor with long/short names, `argInfo`, storage pointer, return value, help text, and argument description. `struct poptAlias`, `poptItem`, `poptContext`, `poptCallbackType`, and `enum poptCallbackReason` define alias/exec and callback contracts. Public functions include `poptGetContext()`, `poptGetNextOpt()`, `poptGetOptArg()`, `poptReadConfigFiles()`, `poptPrintHelp()`, `poptPrintUsage()`, `poptSaveInt()` and related typed save helpers, plus experimental `poptBits*()` helpers.

Control flow and state: This header is declarative, but it encodes parser behavior through bit masks. `POPT_ARG_*` selects conversion/storage behavior, `POPT_ARGFLAG_*` modifies parsing and help output, callback flags drive pre/post/option callback invocation, and `POPT_CONTEXT_*` controls argv treatment. `POPT_AUTOHELP`, `POPT_AUTOALIAS`, and `POPT_TABLEEND` are table construction macros that integrate with `popthelp.c`.

State and persistence behavior: The opaque `poptContext` owns argv copies, aliases, exec entries, leftover args, final argv, and help text in `poptint.h`. Config reading APIs persist aliases and exec items into the context. Callers own context lifetime via `poptFreeContext()`/`poptFini()`, while some returned strings/argv arrays are malloc-backed.

Dependencies and integration points: Included by popt implementation files and consumers. It depends only on `stdio.h` publicly, but its declarations tie into `poptconfig.c`, `poptparse.c`, `popthelp.c`, and internal context definitions in `poptint.h`. In rsync, this bundled library supports command-line/config parsing.

Risks and test signals: ABI stability is important because flags and struct layouts are public. Risk areas include ambiguous flag combinations, callback type safety via `void *`, ownership of allocated argv data, and experimental bitset APIs. Good tests cover option conversion, optional args, aliases, config files, help output, and error-code reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/popt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptconfig.c -->
# sources/sync-backup/rsync/popt/poptconfig.c

Purpose: Implements popt configuration file loading and alias/exec registration. It reads files, expands optional glob path lists, validates config file sanity, parses individual config lines, and initializes a context with user-specified config paths.

Important APIs, types, and functions: `poptSaneFile()` rejects null names, rpm backup/new files, non-regular files, and executable files. `poptReadFile()` reads an entire file into a NUL-terminated buffer and can trim escaped newlines. `poptReadConfigFile()`, `poptReadConfigFiles()`, and `poptReadDefaultConfig()` are the main loaders. `poptInit()` wraps `poptGetContext()` plus `poptReadConfigFiles()`. Internal helpers include `glob_pattern_p()`, `poptGlob()`, `configAppMatch()`, and `poptConfigLine()`.

Control flow: `poptReadConfigFiles()` splits colon-separated paths, expands globs, sanity-checks each match, and calls `poptReadConfigFile()`. `poptReadConfigFile()` reads and line-normalizes the file, skipping comments and blank lines before passing entries to `poptConfigLine()`. A line supplies app name, `alias` or `exec`, option token, and argv text. File-backed option text can be interpolated, parsed by `poptParseArgvString()`, stripped of `--POPTdesc=`/`--POPTargs=` metadata, and added through `poptAddItem()`.

State and persistence behavior: Successful config entries mutate `con->aliases` or `con->execs`. Default config checks `/etc/popt`, `/etc/popt.d/*`, and `$HOME/.popt` when present. The implementation intentionally returns success for each config line at exit, which makes malformed lines non-fatal after local cleanup.

Dependencies and integration points: Uses `system.h`, `poptint.h`, POSIX file APIs, optional `glob.h`/`fnmatch.h`, and `poptparse.c`. Config aliases later appear in help via `popthelp.c` and are used by the parser core.

Risks and test signals: Risks include whole-file memory use, silent bad-line acceptance, glob/platform differences, path sanity policy gaps, and `errno = -EOVERFLOW` oddness on oversized files. Tests should cover config comments, escaped newlines, app-name glob matching, metadata stripping, missing files, unsafe files, and default config discovery.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/popthelp.c -->
# sources/sync-backup/rsync/popt/popthelp.c

Purpose: Generates popt `--help` and `--usage` output and defines the built-in help/usage option table. It formats option names, argument descriptions, translated help text, alias/exec entries, and terminal-width-aware wrapping.

Important APIs, types, and functions: Exported symbols are `poptAliasOptions`, `poptHelpOptions`, `poptHelpOptionsI18N`, `poptPrintHelp()`, `poptPrintUsage()`, and `poptSetOtherOptionHelp()`. Internal helpers include `displayArgs()`, `maxColumnWidth()`, `stringDisplayWidth()`, `getTableTranslationDomain()`, `getArgDescrip()`, `singleOptionDefaultValue()`, `singleOptionHelp()`, `maxArgWidth()`, `singleTableHelp()`, `singleOptionUsage()`, `singleTableUsage()`, and `showShortOptions()`.

Control flow: `displayArgs()` is registered as a callback and exits after printing help or usage. `poptPrintHelp()` prints a usage intro, optional custom help tail, computes column widths, and recursively traverses included option tables and alias/exec tables. `poptPrintUsage()` builds a compact one-line form, tracks already-seen option tables to avoid recursion duplicates, emits grouped short options, then walks tables and context items.

State and persistence behavior: `poptSetOtherOptionHelp()` replaces `con->otherHelp`. Help generation reads context state but does not mutate parser progress. Static `poptHelpOptionsI18N` points at an i18n-aware table. Formatting uses heap buffers for wrapped text and default-value strings.

Dependencies and integration points: Depends on `system.h`, `poptint.h`, optional terminal `ioctl(TIOCGWINSZ)`, optional multibyte support via `mbsrtowcs`, and translation macros from `poptint.h`. It integrates with the public `POPT_AUTOHELP` and `POPT_AUTOALIAS` macros from `popt.h`.

Risks and test signals: Risks include formatting regressions, multibyte width miscalculation, recursive include-table loops, hidden option leakage, and default-value display reading mis-typed `opt->arg` pointers. Tests should compare help/usage output for long/short/toggle/options, included tables, aliases, terminal width changes, i18n domains, and custom `otherHelp`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/popthelp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptint.c -->
# sources/sync-backup/rsync/popt/poptint.c

Purpose: Internal popt utility implementation for UTF-8 character stepping, localized formatted output, and lookup3 hash pair generation. It supports help/output code and bitset/hash users without exposing these helpers as the primary public API.

Important APIs, types, and functions: `POPT_prev_char()` and `POPT_next_char()` move over UTF-8 continuation bytes. `POPT_dgettext()` temporarily binds a text domain to UTF-8 before calling `dgettext()` when NLS support is enabled. `POPT_fprintf()` formats into a heap buffer, optionally converts from UTF-8 to the current locale, and writes to a stream. `strdup_locale_from_utf8()` is the iconv conversion helper when available. `lookup3.c` is included with `poptJlu32lpair` symbol remapping.

Control flow: `POPT_fprintf()` uses `vasprintf()` when available or a reallocating `vsnprintf()` loop otherwise. It then either calls `strdup_locale_from_utf8()` and writes converted text, or writes the formatted buffer directly. The iconv helper handles `E2BIG` by growing output, treats invalid/incomplete sequences as failure, and resets conversion state before processing.

State and persistence behavior: No long-lived mutable state is stored here. Temporary changes to `bind_textdomain_codeset()` are restored after lookup. All format/conversion buffers are heap-allocated and freed per call.

Dependencies and integration points: Depends on `system.h`, `poptint.h`, optional `langinfo.h`, `iconv`, gettext/libintl, and the bundled `lookup3.c`. `popthelp.c` relies on `POPT_fprintf()` and UTF-8 stepping for display formatting.

Risks and test signals: Risks include pointer underflow if `POPT_prev_char()` is called at the start of a string, locale conversion failures, non-C99 `vsnprintf()` behavior, and temporary gettext codeset changes in threaded contexts. Tests should exercise UTF-8 help text, non-UTF-8 locales, long formatted lines, and builds with/without iconv/NLS.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptint.h -->
# sources/sync-backup/rsync/popt/poptint.h

Purpose: Internal popt header that exposes parser context layout, option stack state, internal macros, union casts for option storage, bitmap helpers, and localization wrappers to the implementation files.

Important APIs, types, and functions: `_free()` safely frees possibly const pointers and returns NULL. `pbm_set` and `PBM_*` macros manage parse-position bitmaps. `poptArg` is a union for type-specific access to `opt->arg`. `struct optionStackEntry` stores active argv stack frames, next argument state, current alias, and stuffed-argument markers. `struct poptContext_s` stores option stack, leftovers, options, aliases, execs, final argv, maincall, exec path, help text, and stripped-arg bitmap.

Control flow: Macros `poptArgType()`, `poptGroup()`, `F_ISSET()`, `LF_ISSET()`, and `CBF_ISSET()` centralize flag decoding. `poptSubstituteHelpI18N()` swaps built-in help tables for translated variants. The header also declares `POPT_fprintf()`, `POPT_prev_char()`, and `POPT_next_char()`, plus translation macros `D_`, `POPT_`, and `N_`.

State and persistence behavior: Defines all mutable context state used by parser, config, and help modules. Context fields persist across parse calls until reset/free, while bitmaps track consumed/stripped args.

Dependencies and integration points: Includes `stdint.h`, depends on public `popt.h`, and is included by the implementation files. It bridges public ABI-compatible types to private implementation details.

Risks and test signals: Since it exposes private struct layout across bundled source files, layout changes must be synchronized. Risks include bitmap allocation sizing, macro side effects, flag mask drift with `popt.h`, and translation macro build matrix issues. Tests should compile all feature combinations and exercise alias stacking, stripped argv, leftovers, and translated help.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptparse.c -->
# sources/sync-backup/rsync/popt/poptparse.c

Purpose: Provides argv duplication and string/config-file-to-command-line parsing helpers for popt.

Important APIs, types, and functions: `poptDupArgv()` packs an argv pointer array and copied strings into one malloc block. `poptParseArgvString()` tokenizes a shell-like string into argc/argv with single-quote, double-quote, backslash, and whitespace handling. `poptConfigFileToString()` converts simple key/value config files into a command-line string such as `--name="value"`.

Control flow: `poptParseArgvString()` first builds a temporary argv into a mutable buffer, respecting quote state and escaped characters. It grows the temporary pointer array by `POPT_ARGV_ARRAY_GROW_DELTA`, then normalizes ownership by calling `poptDupArgv()`. `poptConfigFileToString()` reads lines with `fgets()`, skips comments/blanks, parses `name` or `name=value`, trims whitespace, grows the command string, and appends quoted options.

State and persistence behavior: No global state. Returned argv arrays and config strings are heap-owned by the caller. Temporary parsing buffers are freed on exit.

Dependencies and integration points: Uses `system.h` for allocation/string helpers and `_isspaceptr()`. Called by `poptconfig.c` to parse alias/exec replacement argv text and by consumers that accept config-file input.

Risks and test signals: This is intentionally simpler than a full shell parser. Risks include bad quote handling, no escaping of embedded quotes in config values, line length overflow, silently ignored malformed config lines, and integer/memory growth errors. Tests should cover empty input, spaces, quotes, trailing backslashes, long lines, malformed key/value lines, and ownership/freeing of returned argv arrays.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/poptparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/system.h -->
# sources/sync-backup/rsync/popt/system.h

Purpose: Portability and utility include for the bundled popt code. It pulls in generated config, standard headers, allocation helper declarations/macros, `stpcpy()` fallback, secure `getenv()` mapping, and compiler attribute macros.

Important APIs, types, and functions: Defines `_isspaceptr()` for unsigned-char-safe whitespace checks. Declares or macro-defines `xmalloc()`, `xcalloc()`, `xrealloc()`, and `xstrdup()`. Supplies an inline `stpcpy()` when missing. Defines `UNUSED`, `FORMAT`, and `NORETURN`. Includes `popt.h` after preparing the environment.

Control flow: Mostly preprocessor logic. When `HAVE_MCHECK_H` and GCC are present, allocation macros call libc allocation and abort via `vmefail()` on failure, improving mtrace locations. Otherwise they map directly to libc allocation functions. `getenv()` may be remapped to `secure_getenv()` or `__secure_getenv()`.

State and persistence behavior: No runtime state beyond process-wide allocation and environment access behavior. The secure getenv remapping affects any popt source that includes this header.

Dependencies and integration points: Depends on `config.h`, libc headers, optional `mcheck.h`, and `popt.h`. Included by all bundled popt implementation files.

Risks and test signals: Risks include GNU statement-expression allocation macros reducing portability, `xstrdup()` assuming non-null strings, and build differences when secure getenv is unavailable. Tests are mainly compile-time/build-matrix checks plus config parsing under privileged/sanitized environment assumptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/prepare-source -->
# sources/sync-backup/rsync/prepare-source

Purpose: Maintainer helper script that either builds generated autoconf files locally or fetches generated/source files from the rsync upstream distribution area.

Important APIs, types, and functions: Shell actions are `build`/`make`, `fetch`, `fetchgen`, and `fetchSRC`. It invokes `packaging/prep-auto-dir`, `make -f prepare-source.mak`, `rsync-ssl`, and filesystem operations to symlink/copy configure inputs.

Control flow: The script determines its directory, optionally switches into a prepared `build` dir, creates symlinks for `configure.ac` and `m4`, copies existing generated files if needed, defaults to `build` when no action is supplied, then tries requested actions in order until one succeeds. Unknown actions fail immediately.

State and persistence behavior: Mutates the working tree or build directory by creating symlinks, copying generated files, touching `configure.sh`/`config.h.in`, and fetching content over rsync. It does not maintain a separate state file.

Dependencies and integration points: Integrates with `prepare-source.mak`, `rsync-ssl`, upstream rsync servers, and the autoconf toolchain. Used by maintainers before releases or source preparation.

Risks and test signals: Risks include destructive replacement of local files/symlinks, reliance on network/upstream layout, and action fall-through semantics that stop at first success. Test signals are running `prepare-source build` in a clean checkout, verifying generated timestamps, and dry-running fetch paths in isolated build directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/prepare-source -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/prepare-source.mak -->
# sources/sync-backup/rsync/prepare-source.mak

Purpose: Minimal makefile for regenerating rsync autoconf artifacts used by `prepare-source`.

Important APIs, types, and functions: Targets are `conf`, `aclocal.m4`, `configure.sh`, and `config.h.in`. Commands call `aclocal -I m4`, `autoconf -o configure.sh`, and `autoheader && touch config.h.in`.

Control flow: `conf` depends on `configure.sh` and `config.h.in`. `aclocal.m4` is regenerated from `m4/*.m4`; both generated outputs depend on `configure.ac` and `aclocal.m4`.

State and persistence behavior: Writes generated autoconf files in the current directory. Uses standard make timestamp logic and does not store custom state.

Dependencies and integration points: Invoked by `prepare-source`; requires `make`, `aclocal`, `autoconf`, `autoheader`, `configure.ac`, and `m4` macros.

Risks and test signals: Risks are mostly tool-version drift and generated-file churn. Test by invoking `make -f prepare-source.mak conf` in a prepared tree and comparing generated files expected by build scripts.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/prepare-source.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/progress.c -->
# sources/sync-backup/rsync/progress.c

Purpose: Implements rsync transfer progress display for per-file and aggregate progress modes.

Important APIs, types, and functions: Exports `want_progress_now`, `progress_init()`, `set_current_file_index()`, `instant_progress()`, `end_progress()`, and `show_progress()`. Internal `struct progress_history`, `msdiff()`, and `rprint_progress()` maintain recent throughput samples and format output.

Control flow: `progress_init()` seeds start time for non-server clients. `show_progress()` samples current time, optionally converts per-file offsets to aggregate offsets for `--info=progress2`, initializes or rotates a five-second history ring, suppresses output when stdout is not in the foreground process group, and calls `rprint_progress()`. `end_progress()` prints final progress, newline, and resets per-file state. `instant_progress()` emits a filename when needed before ending progress.

State and persistence behavior: Static state tracks start sample, rolling history, ring indexes, and current file index. It updates global `output_needs_newline` and reads global `stats`, `cur_flist`, and verbosity flags. State is process-local and resets at file boundaries.

Dependencies and integration points: Depends on `rsync.h`, `inums.h`, terminal process group APIs when available, logging via `rprintf()`, and file-list lookups via `flist_find()`.

Risks and test signals: Risks include division by zero, incorrect aggregate index math with incremental recursion, terminal carriage-return padding regressions, and foreground detection differences. Tests should validate `--progress`, `--info=progress2`, quiet mode, incremental recursion, and terminal/non-terminal output.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/progress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/receiver.c -->
# sources/sync-backup/rsync/receiver.c

Purpose: Receiver-side transfer engine. It opens basis/output files, receives delta tokens, reconstructs destination files, validates whole-file checksums, handles partial/delayed/inplace updates, and coordinates redo/success messages.

Important APIs, types, and functions: Exports `get_tmpname()`, `open_tmpfile()`, and `recv_files()`. Key internal helpers are `secure_basis_open()`, `receive_data()`, `discard_receive_data()`, `handle_delayed_updates()`, `no_batched_update()`, `we_want_redo()`, and `gen_wants_ndx()`.

Control flow: `recv_files()` loops over file indexes and item flags from `read_ndx_and_attrs()`, handles non-transfer item logging/xattrs, rejects transfer requests in phase 2, toggles checksum/append/backup settings for redo phase, selects a basis file based on protocol and `fnamecmp_type`, opens an output path either inplace or temporary, calls `receive_data()`, closes fds, finalizes with `finish_transfer()` or partial-dir retention, and sends success/redo/no-send messages. `receive_data()` reads the checksum header, maps the basis file, processes literal and matched-block tokens, writes data or skips matched inplace ranges, updates transfer checksums, handles sparse/preallocated/truncated files, fsyncs if requested, and compares against the sender checksum.

State and persistence behavior: Static `phase`, `redoing`, `batch_redo_list`, `delayed_bits`, and `updating_basis_or_equiv` drive multi-phase and redo behavior. Persistent filesystem effects include temp files, partial-dir files, delayed-update renames, backups, chmod/chown/mtime/xattr updates via `finish_transfer()`, and optional source-removal success messages.

Dependencies and integration points: Deeply integrated with rsync protocol, file lists, generator pipe, checksum/mapping/token code, logging, filters, xattrs, ACLs through shared helpers, secure path functions, and global options from `options.c`/main state.

Risks and test signals: High-risk areas are symlink race hardening, absolute partial/backup basis handling, no-basis match tokens, sparse/inplace truncation, redo checksum length toggles, delayed update atomicity, daemon filters, and batch mode ordering. Tests should include partial-dir absolute paths, non-chroot daemon secure symlink races, inplace redo, append/append-verify, sparse files, vanished/basis-dir cases, and checksum verification failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/receiver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rounding.c -->
# sources/sync-backup/rsync/rounding.c

Purpose: Compile-time helper used to validate structure padding assumptions for `rounding.h` generation/build correctness.

Important APIs, types, and functions: Defines `struct test` containing `union file_extras extras[EXTRA_ROUNDING+1]` followed by `int64 test`. `main()` declares a static array sized to fail compilation if `ACTUAL_SIZE != EXPECTED_SIZE`.

Control flow: There is no runtime logic beyond returning success. The important behavior is compile-time array size validation.

State and persistence behavior: No persistent state. It validates compiler layout behavior for rsync's packed file-extra allocation model.

Dependencies and integration points: Includes `rsync.h` for `EXTRA_ROUNDING`, `union file_extras`, and `int64`. Used by the build system as a pre-compilation/helper check.

Risks and test signals: Risk is silent ABI/layout mismatch in file-list extras if this check is bypassed. The test signal is successful compilation; failure indicates padding/alignment assumptions need adjustment.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rounding.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-ssl -->
# sources/sync-backup/rsync/rsync-ssl

Purpose: Bash wrapper that secures daemon-style rsync connections using `openssl`, `gnutls-cli`, or `stunnel` by acting as rsync's `--rsh` helper.

Important APIs, types, and functions: `rsync_ssl_run()` validates daemon-style arguments and execs `rsync --rsh="$0 --HELPER"`. `rsync_ssl_helper()` selects and configures TLS backend, parses rsync helper args, derives host/port/cert/key/CA options from environment, and execs the chosen client. `path_search()` locates helper binaries on `PATH`.

Control flow: User mode handles `--help`, `--type=...`, and ordinary rsync args. Helper mode expects `HOSTNAME rsync --server --daemon .`, ignores optional `-l USER`, chooses backend, builds verification options, defaults port to `RSYNC_PORT` or `RSYNC_SSL_PORT` or 874, then replaces the process with the TLS command connected to host:port.

State and persistence behavior: No files are persisted except stunnel's inherited here-doc config stream. Environment variables (`RSYNC_SSL_TYPE`, backend paths, cert/key/CA, ports) control behavior and are exported for recursive helper use.

Dependencies and integration points: Depends on bash, rsync, and one TLS backend. Used by `prepare-source` and users wanting daemon TLS without native rsync TLS support.

Risks and test signals: Risks include shell word splitting in exec command construction, weaker verification with stunnel defaults, backend option divergence, and hostname/port parsing limitations. Tests should run openssl/gnutls/stunnel modes, unset/empty/custom CA behavior, helper argument validation, and daemon URL rejection for non-daemon args.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-ssl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/bin/badge-update -->
# sources/sync-backup/rsync/rsync-web/bin/badge-update

Purpose: Small deployment helper that refreshes the GitHub Actions build badge on the rsync website.

Important APIs, types, and functions: Shell commands remove `badge.svg`, fetch a fresh badge with `wget`, and upload it with `rsync -aiic --inplace --remove-source-files` to `$SAMBA_HOST:/home/httpd/html/rsync/`.

Control flow: Linear script with no argument parsing or error handling beyond shell command exit behavior.

State and persistence behavior: Deletes and recreates local `badge.svg`, then removes it after successful rsync upload because `--remove-source-files` is used.

Dependencies and integration points: Depends on `wget`, `rsync`, network access to GitHub, and `$SAMBA_HOST` credentials/path. Integrates with rsync-web publishing workflow.

Risks and test signals: Risks include unvalidated `$SAMBA_HOST`, failed/partial download uploaded as badge, and no `set -e`. Test by running in a staging directory with a staging host and verifying uploaded SVG content.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/bin/badge-update -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/bin/upload -->
# sources/sync-backup/rsync/rsync-web/bin/upload

Purpose: Website upload helper for the rsync HTML hierarchy.

Important APIs, types, and functions: Checks for an `rsync-and-debian` directory as a root marker, then runs `rsync -aviOHFFc --del -f._filt . $SAMBA_HOST:/home/httpd/html/rsync/ "$@"`.

Control flow: Single guard: if run from the expected web root, upload; otherwise print an error and exit 1. Extra script arguments are appended to the rsync command.

State and persistence behavior: Mutates the remote web tree and deletes remote files not present locally due to `--del`. No local persistent state.

Dependencies and integration points: Depends on rsync, filter file `_filt`, `$SAMBA_HOST`, and the local website checkout layout.

Risks and test signals: Risks are destructive remote deletion, unvalidated destination, and accidental extra args. Test in staging with `--dry-run`, validate filter behavior, and verify root marker prevents accidental uploads from wrong directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/bin/upload -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/convert-gpl -->
# sources/sync-backup/rsync/rsync-web/convert-gpl

Purpose: Perl filter that converts GPL/plain text snippets into simple HTML-safe output for the website.

Important APIs, types, and functions: Reads stdin line by line, escapes `&`, `<`, and `>`, converts a form-feed character to `<hr>`, hyperlinkifies bracketed `http`/`https` URLs, and prints transformed lines.

Control flow: Linear streaming transformation in a `while (<>)` loop.

State and persistence behavior: Stateless filter; output is written to stdout and no files are changed directly.

Dependencies and integration points: Depends on Perl. Intended for rsync-web content generation.

Risks and test signals: Risks include incomplete HTML sanitization for URLs inserted into `href`, regex greediness, and limited markup semantics. Tests should feed text with special characters, form feeds, multiple URLs, and already-escaped content.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/convert-gpl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/rsync-debug -->
# sources/sync-backup/rsync/rsync-web/rsync-debug

Purpose: Debug wrapper that runs rsync under `strace` with core dumps enabled.

Important APIs, types, and functions: Runs `ulimit -c unlimited`, then invokes `strace -f -t -s 1024 -o /tmp/rsync-$$.out rsync "$@"`.

Control flow: Linear wrapper with no option parsing. All user arguments are forwarded to rsync.

State and persistence behavior: Writes an strace log to `/tmp/rsync-<pid>.out` and may allow core files depending on system configuration.

Dependencies and integration points: Depends on shell, `strace`, and rsync. Comments note some systems use `truss` or `tusc`, but the script hard-codes `strace`.

Risks and test signals: Risks include leaking sensitive paths/args/data into `/tmp`, overwriting predictable-ish files if pid reuse and permissions align, and absence of `strace` on non-Linux systems. Test by invoking with harmless rsync args and verifying trace output.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/rsync-debug -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/rsync_wrapper.pl -->
# sources/sync-backup/rsync/rsync-web/rsync_wrapper.pl

Purpose: Legacy Perl module `Rsync` that wraps the external rsync binary with object-oriented option storage, execution, and accessors for stdout/stderr/status.

Important APIs, types, and functions: `new()` creates an object with default path `/usr/local/bin/rsync`, recognized boolean/scalar option hashes, ordered exclude/include data, source/destination data, debug flag, output arrays, and status fields. `defopts()` parses short/long/default options into the object. `exec()` builds the command, runs it via `IPC::Open3::open3`, captures stdout/stderr, waits, and stores shifted and raw statuses. Accessors are `status()`, `realstatus()`, `err()`, and `out()`.

Control flow: Options passed to `new()` or `defopts()` are normalized from short to long form, with special handling for scalar short options `-B`, `-e`, `-T`, `--exclude`, `--include`, reset marker `!`, and `--path-to-rsync`. `exec()` sorts flag/scalar option keys, appends excludes, stored data, and per-call args, then launches rsync.

State and persistence behavior: Object state persists defaults and last-run outputs/status. Per-call args are not saved. The wrapper does not persist files itself, but rsync side effects are whatever command arguments request.

Dependencies and integration points: Depends on Perl 5.004, `FileHandle`, `IPC::Open3`, and `Carp`. Integrates as a convenience API for website/legacy automation around rsync.

Risks and test signals: Risks include deadlock potential from reading stderr fully before stdout if a child writes enough stdout, sorted option ordering changing semantic order for some options, stale option list relative to modern rsync, and shell-free but user-controlled binary path execution. Tests should cover option parsing, include/exclude ordering, failure to exec, large stdout/stderr, status accessors, and custom rsync path.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/rsync_wrapper.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/tech_report/images.pl -->
# sources/sync-backup/rsync/rsync-web/tech_report/images.pl

Purpose: LaTeX2HTML support data mapping image keys to generated image files and metadata for the rsync technical report.

Important APIs, types, and functions: Defines Perl hashes such as `%cached_env_img`, `%cached_env_img_width`, `%cached_env_img_height`, `%cached_env_img_align`, `%cached_env_img_alt`, and `%cached_env_img_map`. Entries map symbolic labels like `displaymath62` to image filenames, dimensions, alignment, alt text, and image-map flags.

Control flow: No executable flow beyond Perl assignment and final `1;` module truth value.

State and persistence behavior: Provides static metadata to a consuming Perl/LaTeX2HTML pipeline. It does not write files.

Dependencies and integration points: Loaded by generated technical-report HTML tooling. Depends on the corresponding image files being present.

Risks and test signals: Risks are stale image dimensions, missing image files, or broken alt text after report regeneration. Test by loading the file in Perl and rendering the technical report to ensure every referenced image resolves.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/tech_report/images.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/tech_report/labels.pl -->
# sources/sync-backup/rsync/rsync-web/tech_report/labels.pl

Purpose: LaTeX2HTML support data for labels in the rsync technical report.

Important APIs, types, and functions: Defines `%external_labels`, `%noresave`, `%ref_files`, and `%noresave` entries for labels such as `fig:pipeline`, then returns true with `1;`.

Control flow: Static Perl assignments only.

State and persistence behavior: No mutation beyond populating package-global hashes at load time. It serves generated documentation navigation/reference state.

Dependencies and integration points: Consumed by the technical report HTML generation output. Must remain in sync with generated HTML files.

Risks and test signals: Risk is stale or missing labels after documentation regeneration. Test by loading the generated report and checking internal references.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync-web/tech_report/labels.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync.c -->
# sources/sync-backup/rsync/rsync.c

Purpose: Shared rsync runtime routines used by multiple processes: charset setup/conversion, protected-arg transfer, index/attribute reading, file attribute application, signal handling, transfer finalization, file-list lookup, and role naming.

Important APIs, types, and functions: Exports `setup_iconv()`, `iconvbufs()`, `send_protected_args()`, `read_ndx_and_attrs()`, `free_sums()`, `dest_mode()`, `set_file_attrs()`, `sig_int()`, `finish_transfer()`, `flist_for_ndx()`, and `who_am_i()`. Internal `same_mtime()` compares file-list and stat mtimes with optional nanosecond accuracy.

Control flow: `setup_iconv()` initializes message checking and optional send/receive converters. `iconvbufs()` converts xbufs with support for expansion, circular output, and inclusion of bad/incomplete bytes. `read_ndx_and_attrs()` reads protocol indexes, handles incremental-recursion flist markers and delete stats, updates `cur_flist`, reads item flags/basis types/xnames, and validates transfer requests. `set_file_attrs()` stat/xattr/ACL-loads as needed, computes ownership/group/time/create-time/mode changes, applies them, and reports itemized names. `finish_transfer()` handles backups, pre-rename attrs, robust rename/copy fallback, and final attrs.

State and persistence behavior: Mutates global iconv descriptors, `cur_flist`, stats-related state indirectly, file flags such as `FLAG_TIME_FAILED`, and filesystem metadata. `sig_int()` sets `got_kill_signal` for controlled shutdown or exits.

Dependencies and integration points: Central integration point for rsync protocol, file-list management, logging, ACL/xattr modules, backup/rename helpers, charset libraries, and process-role globals.

Risks and test signals: Risks include protocol desynchronization in `read_ndx_and_attrs()`, metadata privilege edge cases, symlink time/chown portability, iconv buffer wrap errors, and robust rename fallback with partial dirs. Tests should cover protocol versions, incremental recursion, ACL/xattr preservation, fake-super, symlink metadata, iconv protected args, and signal cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/rsync.h -->
# sources/sync-backup/rsync/rsync.h

Purpose: Primary shared rsync header. It defines protocol constants, feature flags, cross-platform types, core structs, file-list layout macros, logging/debug categories, message codes, buffer helpers, and portability wrappers used across the C codebase.

Important APIs, types, and functions: Major definitions include protocol bounds/version, `XMIT_*`, `FLAG_*`, itemize flags, message/log enums, file type/delete enums, `struct file_struct`, `union file_extras`, `struct file_list`, `struct sum_struct`, `struct map_struct`, `filter_rule`, `struct stats`, `flist_ndx_list`, `item_list`, `xbuf`, `stat_x`, and `name_num_item`. Macros such as `F_LENGTH()`, `F_OWNER()`, `F_GROUP()`, `F_XATTR()`, `sum2_at()`, `INFO_GTE()`, and `DEBUG_GTE()` encode central access patterns.

Control flow: As a header it has no runtime flow, but it controls compilation via feature probes from `config.h`, fallback typedefs, optional iconv/ACL/xattr/support macros, and replacement libc declarations. It also includes `proto.h`, making project-wide function prototypes available to C files.

State and persistence behavior: Defines the in-memory shape of file-list entries and stats. File extras are stored before `struct file_struct`, so layout macros directly govern persistent transfer state in memory and wire-derived metadata interpretation.

Dependencies and integration points: Includes a broad set of platform headers plus rsync internal libraries (`byteorder.h`, digest, wildmatch, permstring, addrinfo, pool allocator). All major C files depend on it.

Risks and test signals: High-risk areas are protocol constant changes, file-extra alignment/layout, wire-value caps, platform fallback definitions, and macro side effects. Test signals include full build matrix, protocol compatibility tests, large-file and xattr/ACL tests, `rounding.c` compile check, and sanitizer/valgrind runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/rsync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/runtests.py -->
# sources/sync-backup/rsync/runtests.py

Purpose: Python test runner replacing deprecated `runtests.sh`. It discovers rsync tests, prepares per-test scratch directories, configures environment, runs tests sequentially or in parallel, supports version-mixing/expected-result manifests, and summarizes outcomes.

Important APIs, types, and functions: `parse_args()` defines CLI flags. Helpers include `find_setfacl_nodef()`, `get_tls_args()`, `read_shconfig()`, `get_testuser()`, `prep_scratch()`, `collect_tests()`, `parse_expect_result()`, `outcome_of()`, and `build_rsync_cmd()`. `TestResult` stores result data. `run_one_test()` executes a single test. `main()` orchestrates environment setup, test collection, parallel execution, valgrind log checking, and exit code calculation.

Control flow: `main()` merges CLI and legacy env variables, resolves tool/source dirs and rsync binaries, validates helper programs, builds base env (`RSYNC`, `RSYNC_PEER`, `TLS_ARGS`, `scratchbase`, `PYTHONPATH`, etc.), filters collected `_test.py` files, optionally restricts to expected-result manifest entries, runs tests via `ThreadPoolExecutor` or sequential loop, processes outputs under a print lock, removes scratch dirs for successful/skipped/xfail tests unless preserved, checks valgrind logs, compares skipped/expected outcomes, and exits with a count-like status.

State and persistence behavior: Creates `testtmp` scratch directories, symlinks `src`, writes `test.log`, optional `rsyncd.log`, and valgrind logs. It may delete scratch directories after tests. Runtime state is kept in counters and `outcomes`.

Dependencies and integration points: Depends on Python 3 stdlib, `testsuite/exitcodes.py`, built rsync binaries, helper programs, `shconfig`, `config.h`, and test scripts under `testsuite`.

Risks and test signals: Risks include shell-string `RSYNC` env construction for complex paths, parallel tests sharing external resources, missing helper validation drift, expected-result semantics hiding failures if manifests are wrong, and scratch cleanup permissions. Test by running single, full, parallel, valgrind, expected-result, excluded, and mixed-version suites.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/runtests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/sender.c -->
# sources/sync-backup/rsync/sender.c

Purpose: Sender-side transfer engine. It receives checksum sets from the generator, opens source files securely, maps file data, computes deltas, sends matched/literal data to the receiver, logs progress, and optionally removes source files after successful transfer.

Important APIs, types, and functions: Exports `extra_flist_sending_enabled`, `successful_send()`, and `send_files()`. Internal helpers are `receive_sums()` and `write_ndx_and_attrs()`.

Control flow: `send_files()` loops over indexes from `read_ndx_and_attrs()`, sends extra flists during incremental recursion, handles `NDX_DONE` phases, resolves file paths, logs non-transfer items, toggles redo/checksum/append/backup state based on `FLAG_FILE_SENT`, reads receiver checksums via `receive_sums()`, opens the source path using `secure_relative_open()` in secure daemon mode or `do_open_checklinks()` otherwise, maps the file, writes index/attrs and checksum header, runs `match_sums()`, emits progress/logging, unmaps/closes, frees sums, and marks the file sent. `successful_send()` re-stats and removes source files only if unchanged and not the destination in a local-server transfer.

State and persistence behavior: Mutates `file->flags`, stats counters, `io_error`, `make_backups`, `append_mode`, `csum_length`, `updating_basis_file`, and `extra_flist_sending_enabled`. It may delete source files when `--remove-source-files` is active.

Dependencies and integration points: Integrates with generator requests, receiver protocol, file-list APIs, checksum/match code, secure path resolver, xattr request exchange, batch mode, compression selection, progress, and logging.

Risks and test signals: Risks include secure daemon TOCTOU path handling, source deletion safety, append diminished-file behavior, device reads, batch output routing, phase synchronization, and redo state toggles. Tests should cover daemon secure symlink races, remove-source-files unchanged checks, append/inplace, device copy policy, batch mode, incremental recursion, and vanished files.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/sender.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/shconfig.in -->
# sources/sync-backup/rsync/shconfig.in

Purpose: Autoconf template for shell variables consumed by rsync test scripts and `runtests.py`.

Important APIs, types, and functions: Defines `ECHO_T`, `ECHO_N`, `ECHO_C`, `HOST_OS`, `SHELL_PATH`, and `FAKEROOT_PATH` placeholders and exports them.

Control flow: No branches. `config.status` substitutes `@...@` values to create `shconfig`, and scripts source/read it.

State and persistence behavior: Generated `shconfig` persists build-environment facts for later test execution. The template itself has no runtime state.

Dependencies and integration points: Depends on autoconf substitution from configure. `runtests.py` reads the generated file and injects non-empty values into test environments.

Risks and test signals: Risks include missing substitutions, shell quoting issues, and stale generated `shconfig` after configure changes. Test by running configure, inspecting `shconfig`, and executing tests that depend on fakeroot/shell/echo behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/shconfig.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/simd-checksum-avx2.S -->
# sources/sync-backup/rsync/simd-checksum-avx2.S

Purpose: Optional AVX2 assembly implementation of rsync's rolling checksum inner loop when `USE_ROLL_ASM` is enabled.

Important APIs, types, and functions: Exports `get_checksum1_avx2_asm` (with leading underscore on Apple). The function receives `buf`, `len`, current index `i`, and pointers to `ps1`/`ps2`, processes 64-byte chunks after a 128-byte threshold check, updates sums, and returns the updated index. `.mul_T2` stores byte weights 64 down to 1.

Control flow: The routine exits immediately when too little data remains. Otherwise it loads constants and the first two cache lines, loops over 64-byte blocks using AVX2 operations (`vpmaddubsw`, `vpaddw`, `vpaddd`, `vpsrldq`, prefetch), accumulates partial s1/s2 values, performs horizontal reductions, writes back `*ps1` and `*ps2`, calls `vzeroupper`, and returns.

State and persistence behavior: Mutates only caller-provided checksum pointers and uses read-only constant data. No global writable state.

Dependencies and integration points: Includes `config.h`, must match `CHAR_OFFSET` in `rsync.h`, requires assembler/CPU support for AVX2 and non-temporal aligned load instructions used here. Integrated with checksum dispatch/build configuration.

Risks and test signals: Risks include ABI/register convention mismatches, CPU feature dispatch errors, checksum divergence from C implementation, unaligned/short-buffer handling, and `CHAR_OFFSET` drift. Tests should compare checksums against the C path across lengths/alignment, run on AVX2 and non-AVX2 hosts, and include sanitizer-style fallback coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/simd-checksum-avx2.S -->
