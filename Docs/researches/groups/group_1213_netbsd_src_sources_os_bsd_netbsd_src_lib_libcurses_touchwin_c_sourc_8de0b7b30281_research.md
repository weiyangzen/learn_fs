# Group Research: group_1213_netbsd_src_sources_os_bsd_netbsd_src_lib_libcurses_touchwin_c_sourc_8de0b7b30281

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/touchwin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/touchwin.c

This libcurses file implements dirty-line tracking and synchronization helpers for `WINDOW` objects. It is responsible for marking windows or line ranges as changed, clearing dirty state, propagating touch state between parent/subwindows, and honoring `immedok`/`syncok` behavior.

Key entry points:
- `__sync(WINDOW *)` refreshes immediately when `__IMMEDOK` is set and propagates changes upward when `__SYNCOK` is set.
- `is_linetouched()` and `is_wintouched()` inspect `__ISDIRTY` line flags.
- `touchline()`, `wredrawln()`, `touchwin()`, `redrawwin()`, `untouchwin()`, and `wtouchln()` expose public touch/untouch operations.
- `__touchwin()` and `__touchline()` are internal helpers used by refresh/sync paths.
- `wsyncup()` marks ancestors dirty; `wsyncdown()` marks a child dirty if an ancestor is already touched.

Important state and control flow:
- The real work is in `_cursesi_touchline_force()`, which offsets columns by `win->ch_off`, sets `__ISDIRTY`, optionally sets `__ISFORCED`, and widens the shared `firstchp`/`lastchp` damage bounds.
- `wtouchln(..., changed = 0)` clears damage by resetting shared first/last changed-column pointers back to empty values and clearing `__ISDIRTY | __ISFORCED`.
- Parent and subwindow interaction matters because line damage pointers are shared; touching through one view affects refresh decisions for related windows.

Risks and notes:
- Several public wrappers call through to `wtouchln()` using `win->maxy` without an explicit NULL check in the wrapper itself; NULL safety depends on the callee, except `touchwin()`/`redrawwin()` dereference `win` before `wtouchln()`.
- `is_wintouched()` loops `y < maxy`, while `is_linetouched()` allows `line == maxy` to pass the `line > win->maxy` check; bounds conventions are worth checking against the rest of curses.
- This is display invalidation code, not filesystem code, but it is part of the NetBSD source tree covered by subset A.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/touchwin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/tscroll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/tscroll.c

This file formats terminal capability strings used for scrolling and cursor-control style sequences. It derives from termcap `tgoto`-style expansion and provides a small varargs formatter over `%` escapes.

Key entry points:
- `__tscroll(const char *cap, int n1, int n2)` forwards to `__parse_cap()`.
- `__parse_cap(char const *cap, ...)` expands termcap-style percent sequences into a static `MAXRETURNSIZE` result buffer.

Supported escape behavior:
- Numeric output: `%d`, `%2`, `%3`.
- Character output: `%.`, `%+x`.
- Value transformation: `%>xy`, `%i`, `%n`, `%B`, `%D`.
- Literal percent: `%%`.
- `%pN` is ignored as a limited System V terminfo compatibility concession.
- `%r` is documented as unsupported.

Important state and control flow:
- The parser lazily consumes one integer argument at a time into `n`, tracks whether a value is currently loaded with `have_input`, and clears that state after output-producing escapes.
- Errors, NULL capabilities, or unknown escapes return a static empty string.
- The output buffer is static, so callers must treat it as overwritten by later calls and not thread-safe.

Risks and notes:
- There is no explicit bounds checking on the static result buffer while appending output.
- Only a subset of terminfo expansion syntax is supported.
- Debug tracing uses `unctrl()` to display nonprinting capability bytes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/tscroll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/tstp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/tstp.c

This file handles curses suspension/resume behavior, `SIGTSTP`, `SIGWINCH`, and saving/restoring terminal modes around `endwin()` and job-control stops.

Key entry points:
- `__stop_signal_handler()` blocks `SIGALRM`/`SIGWINCH`, calls `__stopwin()`, unblocks and sends `SIGTSTP`, then resumes with `__restartwin()`.
- `__set_stophandler()` and `__restore_stophandler()` install/restore the curses `SIGTSTP` handler.
- `__set_winchhandler()`, `__restore_winchhandler()`, and `__winch_signal_handler()` manage resize handling and KEY_RESIZE signaling.
- `__stopwin()` tears down curses terminal state.
- `__restartwin()` restores curses mode, resizes standard screens, restores colors/meta/cursor state, and refreshes `curscr`.
- `def_prog_mode()`, `reset_prog_mode()`, `def_shell_mode()`, and `reset_shell_mode()` implement curses terminal-mode save/restore APIs.

Important state and control flow:
- `tstp_set`, `winch_set`, `otstpfn`, and `owsa` track installed handlers and previous handlers.
- `__stopwin()` saves current terminal state into `save_termios`, restores old signal handlers, emits terminal exit sequences, flushes output, marks `endwin`, and restores `orig_termios`.
- `__restartwin()` checks `TIOCGWINSZ`, updates `LINES`/`COLS`, resizes `curscr` and `stdscr`, saves the new shell baseline, restores saved program terminal state, and restarts screen rendering.
- The resize handler either chains to a prior non-default handler or marks `_cursesi_screen->resized`.

Risks and notes:
- Signal handlers interact with global `_cursesi_screen`; correctness depends on screen initialization and async-signal assumptions inherited by curses.
- `__restore_winchhandler()` only restores if the current handler still matches the saved curses handler; otherwise it assumes the application has taken over.
- `TCSASOFT` is defaulted to `0` if absent, so hardware-setting preservation is platform-dependent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/tstp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/tty.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/tty.c

This file implements libcurses terminal mode management: raw/cbreak/cooked modes, input timing behavior, echo/newline settings, typeahead, save/restore tty state, screen start/end sequences, and erase/kill character queries.

Key entry points:
- `baudrate()`, `gettmode()`, and `_cursesi_gettmode()` initialize and query terminal mode state.
- `raw()`, `noraw()`, `cbreak()`, `nocbreak()`, and `halfdelay()` switch input modes.
- `__delay()`, `__nodelay()`, `__timeout()`, and `__notimeout()` manipulate `VMIN`/`VTIME`.
- `__save_termios()` and `__restore_termios()` preserve timeout settings.
- `echo()`, `noecho()`, `nl()`, `nonl()`, `intrflush()`, `qiflush()`, and `noqiflush()` control curses terminal behavior flags.
- `__startwin()`, `endwin()`, `isendwin()`, and `flushinp()` manage active curses screen mode.
- `savetty()`, `resetty()`, `erasechar()`, `killchar()`, `erasewchar()`, `killwchar()`, and `typeahead()` provide compatibility APIs.

Important state and control flow:
- `_cursesi_gettmode()` reads terminal attributes from input first, then output, and marks `screen->notty` if neither is a tty.
- It builds three termios templates: `baset`, `cbreakt`, and `rawt`; `rawt` disables signal/extension processing and output post-processing, with hardware/parity handling dependent on `TCSASOFT`.
- Mode setters update global compatibility flags like `__rawmode`, `__pfast`, `__echoit`, and screen-local fields like `useraw`, `curt`, `nl`, and `pfast`.
- `__startwin()` emits alternate-screen/cursor/keypad sequences through terminfo wrappers and optionally installs a larger BSD stdio buffer.
- `endwin()` delegates to `__stopwin()` from `tstp.c`.

Risks and notes:
- Many routines assume `_cursesi_screen` and `stdscr` are valid.
- Timeout helpers change all three termios templates, so callers relying on original `VMIN`/`VTIME` must use the save/restore helpers correctly.
- Non-tty operation returns OK for many mode operations while disabling actual termios changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.c

This file defines lookup tables for rendering byte values as printable strings. It backs the `unctrl()` and `unctrllen()` macros declared in `unctrl.h`.

Key data:
- `__unctrl[256]` maps bytes to display strings:
  - ASCII control bytes become caret notation such as `^A`.
  - Printable ASCII maps to one-character strings.
  - DEL maps to `^?`.
  - High bytes map to lowercase hex strings like `0x80`.
- `__unctrllen[256]` stores the corresponding display lengths.
- Under `HAVE_WCHAR`, `__wunctrl[256]` provides wide-string equivalents.

Integration:
- Used by curses tracing and callers that need display-safe representations of control characters.
- Exported through macros rather than functions in `unctrl.h`.

Risks and notes:
- The tables are static mappings for 8-bit byte values, not locale-sensitive Unicode display conversion.
- High-byte values are rendered as hex byte strings rather than decoded multibyte characters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.h

This public header declares the control-character display tables and provides macros for converting byte values to printable forms.

Key declarations:
- `extern const char * const __unctrl[]`
- `extern const unsigned char __unctrllen[]`
- `extern const wchar_t * const __wunctrl[]` when `HAVE_WCHAR` is enabled.

Key macros:
- `unctrl(c)` indexes `__unctrl` with `(unsigned char)c & 0xff`.
- `unctrllen(c)` indexes `__unctrllen` the same way.
- `wunctrl(wc)` indexes `__wunctrl` using the first value field of a curses wide character object.

Integration:
- Included by code needing byte-to-display rendering.
- Pulls in `<wchar.h>` and `<curses.h>` only for wide-character support.

Risks and notes:
- `wunctrl(wc)` assumes a curses wide-character structure with `vals[0]`; it is not a generic `wchar_t` macro.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/unctrl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/underscore.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/underscore.c

This file implements old curses underscore/underline mode helpers.

Key entry points:
- `underscore()` and `underend()` operate on `stdscr` when `_CURSES_USE_MACROS` is not set.
- `wunderscore(WINDOW *)` enables `__UNDERSCORE` in `win->wattr` when the terminal can enter/exit underline mode or has an underline character capability.
- `wunderend(WINDOW *)` clears `__UNDERSCORE` when `exit_underline_mode` is available.

Integration:
- Uses termcap/terminfo globals such as `enter_underline_mode`, `exit_underline_mode`, and `underline_char`.
- Modifies window attribute state; later rendering code emits terminal capabilities.

Risks and notes:
- Returns `1` on success-like paths rather than the usual curses `OK` constant, matching legacy behavior in this file.
- `wunderend()` only clears when `exit_underline_mode` exists, so underline state may remain if only underline-character fallback is available.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/underscore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/version.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcurses/version.c

This file implements `curses_version()` for NetBSD curses.

Behavior:
- If `CURSES_VERSION` is not supplied at build time, it defaults to `"believe in unicorns"`.
- If a version string is present, it is wrapped in parentheses after `"NetBSD-Curses"`.
- `curses_version()` returns the compile-time static string.

Integration:
- Includes `curses.h`.
- Intended to provide a recognizable but deliberately non-standard NetBSD curses version identifier.

Risks and notes:
- The default string is intentionally not a semantic version.
- Packagers can override `CURSES_VERSION` with branding/version text via compiler flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcurses/version.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libdm/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libdm/Makefile

This NetBSD makefile builds the `libdm` device-mapper userland library.

Key build settings:
- `LIB= dm`
- `SRCS= libdm_ioctl.c`
- Installs `dm.h` to `/usr/include`.
- Installs manual page `dm.3`.
- Links against `libprop` through `LIBDPLIBS`.
- Sets `USE_SHLIBDIR=yes` and disables fortification by default with `USE_FORT?= no`.

Conditional behavior:
- If `RUMP_ACTION` is defined, adds `-DRUMP_ACTION` to `CPPFLAGS`, enabling rump syscall paths in `libdm_ioctl.c`.

Integration:
- This build file connects the proplib-backed ioctl wrapper to NetBSD's device-mapper driver interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libdm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libdm/dm.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libdm/dm.h

This public header declares NetBSD libdm's opaque handle API for constructing and running device-mapper ioctl tasks.

Key types:
- Opaque pointer typedefs: `libdm_task_t`, `libdm_cmd_t`, `libdm_target_t`, `libdm_table_t`, `libdm_dev_t`, and `libdm_iter_t`.
- `struct cmd_version` maps command strings to version triples.

Key API groups:
- Task lifecycle and execution: `libdm_task_create()`, `libdm_task_destroy()`, `libdm_task_run()`.
- Task metadata: name, uuid, minor, command string, command version, flags, open count, event count, target count.
- Flag helpers for suspend/status/exists/nocount-style protocol bits.
- Command arrays: create/destroy/iterate and attach tables.
- Table dictionaries: start, length, target type, params, status.
- Target dictionaries: name and version.
- Device dictionaries: name, minor, rename new-name.

Integration:
- `DM_DEVICE_PATH` is `/dev/mapper/control`.
- The implementation in `libdm_ioctl.c` translates these APIs to proplib dictionaries and NetBSD DM ioctl keys.

Risks and notes:
- Ownership semantics are not obvious from the header: several getters return pointers into property objects rather than caller-owned strings.
- The header has a comment typo around “dictonaries” but no functional issue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libdm/dm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libdm/libdm_ioctl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libdm/libdm_ioctl.c

This file implements the NetBSD libdm userspace API. It wraps device-mapper operations in proplib dictionaries/arrays and exchanges them with the kernel device-mapper driver through `NETBSD_DM_IOCTL` on `/dev/mapper/control`.

Key structures:
- `struct libdm_task` owns a top-level `prop_dictionary_t`.
- `struct libdm_cmd` owns a `prop_array_t` command-data array.
- `struct libdm_table`, `struct libdm_target`, and `struct libdm_dev` wrap proplib dictionaries.
- `struct libdm_iter` wraps a proplib object iterator.
- `cmd_ver[]` maps command names like `version`, `targets`, `create`, `info`, `remove`, `reload`, `status`, and `table` to version `{4,0,0}`.

Key control flow:
- `libdm_task_create()` allocates a dictionary, sets `DM_IOCTL_COMMAND`, and adds a version array when the command appears in `cmd_ver`.
- `libdm_task_run()` opens `DM_DEVICE_PATH`, sends the dictionary via `prop_dictionary_sendrecv_ioctl()` or rump plistref ioctl path, closes the fd, releases the old dictionary, and replaces it with the response dictionary.
- Setters store strings, integers, flags, tables, and command arrays under kernel protocol keys from `<dev/dm/netbsd-dm.h>`.
- Getters read values from response dictionaries and arrays.
- Iterators expose command arrays as target/table/dev/dependency sequences.

API coverage:
- Task name/uuid/minor/flags/open/event/target count accessors.
- Specific flag mutators for suspend, status-table, and exists flags.
- Command creation, destruction, table attachment, iteration.
- Table creation/destruction and field accessors for start, length, target type, params, and status.
- Target and device wrapper destruction/accessors.
- Rename support through `libdm_dev_set_newname()` storing a string at array index 0.

Risks and notes:
- Several allocation paths do not check every intermediate proplib allocation result.
- Some getters do not initialize local variables before `prop_dictionary_get_*` failure paths, so callers must avoid relying on values after malformed responses.
- `libdm_cmd_get_deps()` calls `prop_number_unsigned_value(obj)` before checking whether `obj` is NULL.
- Wrapper objects returned by iterator getters do not consistently retain underlying proplib objects, but destroy routines release them; this requires careful proplib ownership expectations.
- Error return conventions are mixed: some APIs return `ENOENT`, some return booleans from proplib setters, some return `EXIT_SUCCESS`, and ioctl errors are propagated differently under rump/non-rump paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libdm/libdm_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/Makefile

This makefile builds NetBSD `libedit`.

Key build settings:
- `LIB= edit`
- Depends on `libterminfo`.
- Installs `histedit.h` to `/usr/include`.
- Builds manpages `editline.3`, `editrc.5`, and `editline.7`.
- Installs `libedit.pc` under `/usr/lib/pkgconfig`.

Source list:
- Core sources include `chared.c`, `chartype.c`, `common.c`, `el.c`, `eln.c`, `emacs.c`, `filecomplete.c`, `hist.c`, `history.c`, `historyn.c`, `keymacro.c`, `literal.c`, `map.c`, `parse.c`, `prompt.c`, `read.c`, `readline.c`, `refresh.c`, `search.c`, `sig.c`, `terminal.c`, `tokenizer.c`, `tokenizern.c`, `tty.c`, and `vi.c`.

Generated headers:
- `vi.h`, `emacs.h`, and `common.h` are generated from source files using `makelist -h`.
- `fcns.h`, `func.h`, and `help.h` are generated from the editor command source set.
- The generated headers are prerequisites of `.depend`.

Test hook:
- Defines a build target for `tc1` from `TEST/tc1.c` linked against `libedit.a` and termlib.

Warnings and portability:
- Uses `WARNS?=5`, `-Wunused-parameter`, GCC conversion warnings, and selected per-file warning suppressions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/Makefile

This small makefile builds libedit test programs.

Key settings:
- `NOMAN=1`
- `PROG=wtc1 test_filecompletion`
- Adds `-I${.CURDIR}/..` so tests can include libedit internals.
- Links with `-ledit -ltermlib`.
- Adds `-DDEBUG` when `DEBUG` is defined.
- Includes `<bsd.prog.mk>`.

Integration:
- Builds interactive wide-character test coverage (`wtc1`) and file completion escaping tests (`test_filecompletion`).
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/fuzz1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/fuzz1.c

This is a libFuzzer harness for the readline-compatible history expansion interface.

Behavior:
- Initializes locale and stifles history to 7 entries once.
- Clears history for each fuzz input.
- Splits the fuzz buffer on newline boundaries.
- For each non-empty segment, NUL-terminates it, calls `history_expand()`, and adds successful expansions to history.
- Frees both the expansion and temporary segment.

Integration:
- Includes `<readline/readline.h>` and exercises libedit's readline compatibility layer.
- The file header documents sanitizer/fuzzer build and run commands.

Risks and notes:
- Inputs are byte-oriented and optionally run with `-only_ascii=1`.
- The harness deliberately ignores expansion errors and focuses on memory-safety coverage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/fuzz1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/rl1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/rl1.c

This is a minimal readline compatibility smoke test.

Behavior:
- Repeatedly calls `readline("hi$")`.
- Adds each returned line to history with `add_history()`.
- Prints `history_length` and the line content.

Integration:
- Includes `<readline/readline.h>`, exercising the compatibility API rather than native `histedit.h`.

Risks and notes:
- Returned lines from `readline()` are not freed in this test.
- `argc`/`argv` are unused.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/rl1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/tc1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/tc1.c

This is an interactive narrow-character libedit test shell.

Key behavior:
- Initializes locale, signal handlers, history, tokenizer, and an `EditLine` instance.
- Sets vi mode, enables libedit signal handling, installs an escaped prompt, attaches history, and binds tab to a custom directory completion function.
- Rebinds vi command-mode `j`/`k` to line movement rather than history movement.
- Sources user editrc settings with `el_source(el, NULL)`.
- Reads lines with `el_gets()`, tokenizes them with `tok_line()`, stores them in history, and either handles `history` subcommands, passes libedit commands to `el_parse()`, or forks/execs an external command.

Completion:
- `complete()` finds the current word by scanning backward to whitespace, opens `.`, scans directory entries, and inserts the unmatched suffix of the first matching entry.

Signal handling:
- A simple signal handler stores the signal number in `gotsig`; the main loop reports it and calls `el_reset()`.

Risks and notes:
- The test uses direct shell execution via `fork()`/`execvp()`.
- Completion assumes `opendir(".")` succeeds and does not guard against NULL `DIR *`.
- It is a demonstration/test driver, not library code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/tc1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/test_filecompletion.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/test_filecompletion.c

This test verifies libedit filename completion escaping behavior.

Test model:
- Defines many `test_input` cases with:
  - wide-character user-typed command text,
  - expected input seen by the completion function,
  - one or two generated completion matches,
  - expected escaped output in the edit buffer.
- Cases cover angle brackets, backslashes, braces, dollars, equals, newlines, spaces, quotes, parentheses, pipes, tabs, backticks, `@`, semicolons, ampersands, cursor-at-quote/backslash behavior, and multiple-match common-prefix completion.

Key functions:
- `mycomplet_func()` returns hardcoded matches based on the current completion text.
- `main()` initializes `EditLine`, writes each test input directly into `el->el_line`, calls `fn_complete()`, prints the expected/generated values, and asserts that the edited buffer matches.

Integration:
- Includes internal headers `filecomplete.h` and `el.h`, so it tests internals rather than only public API.
- Uses `FN_QUOTE_MATCH` behavior through `fn_complete()` when no attempted completion function is supplied.

Risks and notes:
- The test mutates `el->el_line` directly, bypassing normal editing setup.
- It allocates a fixed 64-wide-character buffer and uses a pointer limit larger than 64 wchar slots because it adds `64 * sizeof(*buffer)` to a `wchar_t *`; the test data remains small enough that this does not affect intended coverage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/test_filecompletion.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/wtc1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/wtc1.c

This is a wide-character version of the interactive libedit test shell.

Key behavior:
- Initializes locale, wide history (`history_winit()`), wide tokenizer (`tok_winit()`), and `EditLine`.
- Uses `el_wset()`, `el_wgets()`, `el_wline()`, `el_wparse()`, and wide prompt/history/tokenizer APIs.
- Loads history from `.whistory` on startup and saves it on exit.
- Provides a wide-character directory completion function bound to tab.
- Handles `history`, `history clear`, `history load`, and `history save`.
- For external commands, converts the wide input line to multibyte text, tokenizes with the narrow tokenizer, and `execvp()`s the result.

Completion:
- Finds the current wide word, converts it to multibyte with `wctomb()`, compares against directory entries, converts the remaining suffix back to wide characters, and inserts it with `el_winsertstr()`.

Risks and notes:
- `my_wcstombs()` uses a static growable buffer and does not handle `wcstombs()` failure.
- Completion assumes `opendir(".")` succeeds.
- The test mixes wide and narrow tokenizers for process execution.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/TEST/wtc1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chared.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/chared.c

This file implements libedit's low-level character editing utilities. It owns line-buffer mutation, vi undo/redo/yank bookkeeping, kill buffer handling, word movement helpers, buffer growth, and public insert/delete/replace cursor APIs.

Key state:
- `el->el_line` holds the editable wide-character line buffer, cursor, last character, and limit.
- `el_chared.c_undo` stores vi undo snapshots.
- `el_chared.c_redo` stores vi redo command metadata and buffer.
- `el_chared.c_kill` stores yanked/killed text and mark.
- `el_chared.c_vcmd` stores an active vi operator action and start position.

Key functions:
- `cv_undo()` snapshots the current line and redo metadata.
- `cv_yank()` copies a text range into the kill buffer.
- `c_insert()`, `c_delafter()`, `c_delafter1()`, `c_delbefore()`, and `c_delbefore1()` perform primitive buffer edits.
- `ce__isword()`, `cv__isword()`, and `cv__isWord()` classify word characters for emacs/vi movement.
- `c__prev_word()`, `c__next_word()`, `cv_next_word()`, `cv_prev_word()`, and `cv__endword()` implement word navigation.
- `cv_delfini()` finalizes a vi delete/yank/change operator.
- `ch_init()`, `ch_reset()`, `ch_enlargebufs()`, and `ch_end()` manage editor buffers.
- `el_winsertstr()`, `el_deletestr()`, `el_deletestr1()`, `el_wreplacestr()`, and `el_cursor()` are public editing helpers.
- `c_gets()` reads a small prompt response for extended commands.
- `c_hpos()` computes cursor horizontal position in a multiline buffer.
- `ch_resizefun()` and `ch_aliasfun()` store application callbacks.

Important control flow:
- Buffer expansion reallocates line, kill, undo, redo, and history buffers together, preserving pointer offsets.
- Vi delete/change operations use `c_vcmd.action` flags (`DELETE`, `INSERT`, `YANK`) and call `cv_delfini()` after motion commands.
- Deletion primitives update undo/yank state for non-emacs maps.

Risks and notes:
- `ch_init()` has multiple allocation steps; on failure it delegates to `ch_end()` for cleanup.
- Many operations assume internal buffers were initialized and sized consistently.
- `el_deletestr1()` bounds checks are conservative and does not delete if `end >= line_length`, so callers must understand its exact range semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chared.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chared.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/chared.h

This internal header declares libedit character editor state and helper APIs.

Key types:
- `c_undo_t`: saved line length, cursor, and buffer for vi undo.
- `c_redo_t`: redo insertion buffer, command, invoking character, count, and action.
- `c_vcmd_t`: active vi operator action and position.
- `c_kill_t`: kill/yank buffer, end pointer, and mark.
- `el_chared_t`: aggregates undo, kill, redo, vi command state, resize callback, and alias callback.

Important constants:
- `VI_MOVE` enables vi-like cursor movement on insert/command transitions.
- Action flags: `NOP`, `DELETE`, `INSERT`, `YANK`.
- Direction constants: `CHAR_FWD`, `CHAR_BACK`.
- Input modes: `MODE_INSERT`, `MODE_REPLACE`, `MODE_REPLACE_1`.

Declared helpers:
- Word classification and movement helpers.
- Character insertion/deletion primitives.
- Character editor lifecycle and buffer growth.
- Resize and alias callback installers.

Integration:
- Included by `el.h`, making character editing state part of the central `EditLine` object.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chared.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chartype.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/chartype.c

This file implements wide-character/multibyte conversion and display-width helpers for libedit.

Key functions:
- `ct_encode_string()` converts wide strings to multibyte strings using a growable `ct_buffer_t`.
- `ct_decode_string()` converts multibyte strings to wide strings.
- `ct_decode_argv()` decodes a narrow argv array into a wide argv array using shared conversion storage.
- `ct_enc_width()` returns the encoded byte width of one wide character.
- `ct_encode_char()` encodes one wide character to a provided byte buffer.
- `ct_visual_string()` converts a string to its printable visual representation.
- `ct_visual_width()` computes display width for control, tab, newline, printable, and nonprintable characters.
- `ct_visual_char()` renders one character as printable/wide display text.
- `ct_chr_class()` classifies a character as printable, ASCII control, tab, newline, or nonprintable.

Important behavior:
- Conversion buffers grow in `CT_BUFSIZ` increments.
- ASCII control characters render as caret notation.
- Nonprintable characters render as `\U+` hexadecimal forms.
- Printable width is delegated to `wcwidth()`.

Risks and notes:
- Conversion uses process locale functions such as `mbstowcs()`, `wctomb()`, and `wcrtomb()`.
- Conversion buffers are owned by `EditLine` scratch fields and reused; callers should not retain results after subsequent conversions using the same buffer.
- `ct_encode_string()` aborts if `ct_encode_char()` unexpectedly reports insufficient space after pre-growth.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chartype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chartype.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/chartype.h

This internal header defines libedit's character conversion buffer and wide-character display APIs.

Key declarations:
- `ct_buffer_t` holds reusable narrow and wide buffers plus their sizes.
- Encoding/decoding APIs for strings, argv arrays, and single characters.
- Visual-width and visual-rendering APIs.
- Character classification constants and `ct_chr_class()`.

Portability checks:
- Verifies, on many non-BSD platforms, that `wchar_t` stores ISO 10646 characters.
- Warns when `WCHAR_MAX < INT32_MAX`, indicating no non-BMP support.

Important constants:
- `VISUAL_WIDTH_MAX` is 8, enough for the widest `\U+nnnnn` representation used here.
- `MB_FILL_CHAR` marks terminal cells occupied by the extra width of a wide character.
- Character class constants distinguish printable, ASCII control, tab, newline, and nonprintable cases.

Integration:
- Included by `el.h`, so conversion/display helpers are core to all line editing and refresh paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/chartype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/common.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/common.c

This file implements editor-neutral libedit command functions shared by emacs and vi bindings.

Key command functions:
- Input and line completion: `ed_insert()`, `ed_newline()`, `ed_end_of_file()`, `ed_quoted_insert()`.
- Deletion: `ed_delete_prev_word()`, `ed_delete_next_char()`, `ed_kill_line()`, `ed_delete_prev_char()`.
- Movement: `ed_move_to_end()`, `ed_move_to_beg()`, `ed_next_char()`, `ed_prev_char()`, `ed_prev_word()`, `ed_prev_line()`, `ed_next_line()`.
- Arguments and ignored input: `ed_digit()`, `ed_argument_digit()`, `ed_unassigned()`, `ed_ignore()`, `ed_sequence_lead_in()`.
- Display: `ed_clear_screen()`, `ed_redisplay()`, `ed_start_over()`.
- History navigation/search: `ed_prev_history()`, `ed_next_history()`, `ed_search_prev_history()`, `ed_search_next_history()`.
- Extended command execution: `ed_command()`.

Important control flow:
- Insert mode honors `MODE_INSERT`, `MODE_REPLACE`, and `MODE_REPLACE_1`, using `c_insert()` and `re_fastaddc()`/`re_refresh()`.
- Vi operator-pending actions are completed by motion commands through `cv_delfini()`.
- History navigation saves the current line when leaving event 0, updates `eventno`, and uses `hist_get()` to load target history entries.
- History search uses `c_setpat()` and `c_hmatch()` from search helpers.
- `ed_command()` prompts with `"\n: "`, parses the resulting command with `parse_line()`, resets to key map, and refreshes.

Risks and notes:
- Many functions interpret `el_state.argument`; very large numeric arguments are capped indirectly in digit handlers.
- Behavior diverges for vi vs emacs maps, especially cursor bounds and EOF handling.
- Extended commands depend on generated command tables and parser integration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/config.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/config.h

This generated-style configuration header records platform feature availability for NetBSD libedit.

Defined features:
- `HAVE_CURSES_H`
- `HAVE_GETPW_R_POSIX`
- `HAVE_ISSETUGID`
- `HAVE_STRUCT_DIRENT_D_NAMLEN`
- `HAVE_SYS_CDEFS_H`
- `HAVE_TERMCAP_H`
- `HAVE_TERM_H`

Undefined/commented features:
- `HAVE_GETPW_R_DRAFT`
- `HAVE_NCURSES_H`

Integration:
- Includes `sys.h` after feature defines.
- Used by files like `filecomplete.c`, `el.c`, and tests to choose portable code paths.

Risks and notes:
- This is configuration glue, not runtime logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/el.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/el.c

This file implements the core wide-character `EditLine` lifecycle and configuration API.

Key entry points:
- `el_init()` and `el_init_fd()` create an `EditLine`.
- `el_init_internal()` allocates and initializes the full editor object.
- `el_end()` tears down all modules and conversion buffers.
- `el_reset()` resets tty mode and character editor state.
- `el_wset()` and `el_wget()` implement wide-character set/get operations for `EL_*` options.
- `el_wline()` exposes current line info.
- `el_source()` reads and parses editrc-style configuration files.
- `el_resize()` handles terminal resize updates.
- `el_beep()` emits terminal bell.
- `el_editmode()` implements the `edit on/off` command.

Initialization order:
- Stores input/output/error `FILE *` and fd values.
- Sets `el_getenv` to `getenv`.
- Decodes and stores program name as wide string.
- Initializes modules in order: terminal, keymacro, map, tty, chared, search, history, prompt, signal, literal, and read.

Configuration behavior:
- `el_wset()` handles prompts, terminal/editor settings, signal/edit/unbuffered/safe-read flags, bindings, termcap commands, tty settings, added functions, history backend, file streams, refresh, word characters, custom getenv, resize callbacks, and alias callbacks.
- `el_wget()` retrieves supported prompt/editor/signal/edit/terminal/input/clientdata/file/wordchars/getenv settings.

Security and config loading:
- `el_source(NULL)` refuses to source files when `issetugid()` reports a set-id context.
- It uses `EDITRC` if set, otherwise `$HOME/.editrc`, skips empty/comment lines, decodes to wide strings, and passes commands to `parse_line()`.

Risks and notes:
- Module initialization return values are not all checked; tty failure sets `NO_TTY`.
- `el_reset()` always calls `tty_cookedmode()` then `ch_reset()`.
- The varargs API requires exact argument types matching `histedit.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/el.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/el.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/el.h

This is libedit's central internal header. It defines the `EditLine` object and shared editor state structures.

Key definitions:
- Local defaults: `KSHVI`, `VIDEFAULT`, and `ANCHOR`.
- Buffer size: `EL_BUFSIZ` is 1024 wide characters.
- Flag bits: `HANDLE_SIGNALS`, `NO_TTY`, `EDIT_DISABLED`, `UNBUFFERED`, `NARROW_HISTORY`, `NO_RESET`, `FIXIO`, and `FROM_ELLINE`.
- `el_action_t`: command action index type.
- `coord_t`: screen coordinate pair.
- `el_line_t`: current editable line buffer/cursor/last/limit.
- `el_state_t`: input mode, numeric argument, meta-next state, and current/previous command metadata.

`struct editline` aggregates:
- Program name, stdio streams, fds, flags, cursor position.
- Real and virtual display buffers.
- Client data.
- Line and command state.
- Terminal, tty, refresh, prompt, literal, character editor, map, keymacro, history, search, signal, and read submodules.
- Conversion buffers for visual/scratch/legacy APIs.
- Legacy `LineInfo` storage.
- Custom getenv callback.

Integration:
- Includes nearly all internal module headers, making this the core dependency for libedit implementation files.
- Declares `el_editmode()` and `el_init_internal()`.

Risks and notes:
- Many internals are exposed to tests and implementation units through this header.
- Memory allocation macros directly map to libc allocation functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/el.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/eln.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/eln.c

This file implements narrow-character compatibility wrappers around libedit's wide-character core APIs.

Key entry points:
- `el_getc()` calls `el_wgetc()` and converts one wide character to a single byte with `wctob()`.
- `el_push()` decodes a narrow string and calls `el_wpush()`.
- `el_gets()` calls `el_wgets()`, converts the returned line to multibyte, and adjusts `nread` to byte length.
- `el_parse()` decodes argv and calls `el_wparse()`.
- `el_set()` maps narrow varargs options to wide/internal operations.
- `el_get()` maps wide/internal results back to narrow API types.
- `el_line()` converts `LineInfoW` to legacy byte-offset `LineInfo`.
- `el_insertstr()` and `el_replacestr()` decode narrow strings and call wide insertion/replacement.

Important behavior:
- `EL_BIND`, `EL_TELLTC`, `EL_SETTC`, `EL_ECHOTC`, and `EL_SETTY` decode up to 20 narrow strings and call the same underlying map/terminal/tty handlers as `el_wset()`.
- `EL_ADDFN` decodes name/help strings but leaves the function pointer unchanged.
- `EL_HIST` marks `NARROW_HISTORY`, causing history conversion through `hist_convert()`.
- `el_line()` computes byte offsets for cursor and lastchar by summing encoded widths.

Risks and notes:
- `el_getc()` fails with `ERANGE` when a wide character cannot be represented as one byte.
- Returned converted strings use `el_lgcyconv`, a reusable buffer that is overwritten by later conversions.
- Varargs type correctness is critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/eln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/emacs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/emacs.c

This file implements emacs-style editing commands for libedit.

Key command functions:
- `em_delete_or_list()` handles `^D`: EOF at empty line, delete under cursor otherwise, and currently errors at end-of-line nonempty.
- `em_delete_next_word()` kills from cursor to the end of the next word.
- `em_yank()` inserts the kill buffer.
- `em_kill_line()` kills the whole line.
- `em_kill_region()` and `em_copy_region()` operate on the mark/cursor region.
- `em_gosmacs_transpose()` and `em_delete_prev_char()` implement emacs variants of transpose/backspace.
- `em_next_word()`, `em_upper_case()`, `em_capitol_case()`, and `em_lower_case()` perform word movement/case changes.
- `em_set_mark()` and `em_exchange_mark()` manage the mark.
- `em_universal_argument()` multiplies the argument by 4.
- `em_meta_next()` marks the next input as meta.
- `em_toggle_overwrite()` toggles insert/overwrite mode.
- `em_copy_prev_word()` copies the previous word at the cursor.
- `em_inc_search_next()` and `em_inc_search_prev()` start incremental history search.

Important control flow:
- Most text manipulation uses shared helpers from `chared.c`.
- Word operations use emacs word classification `ce__isword`.
- Kill/yank operations manipulate `el_chared.c_kill`.
- Some commands are vi-aware when called in vi maps, completing operator-pending actions.

Risks and notes:
- `em_yank()` rejects insertion when the kill buffer would exceed the current line limit rather than attempting buffer growth.
- Mark-based commands require `c_kill.mark` to be set.
- The function name `em_capitol_case()` preserves historical spelling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/emacs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.c

This file implements libedit filename completion, tilde expansion, shell-style escaping, match collection, match display, and completion key wrappers.

Key functionality:
- `fn_tilde_expand()` expands `~` and `~user` using `getpwuid_r()`/`getpwnam_r()` when available.
- `fn_filename_completion_function()` iterates directory entries and returns matches for a prefix, preserving directory prefixes and supporting tilde-expanded directory paths.
- `completion_matches()` repeatedly calls a generator function, builds a match list, and computes the common prefix in `matches[0]`.
- `fn_display_match_list()` sorts and displays matches in columns.
- `fn_complete2()` is the main completion engine.
- `fn_complete()` is a compatibility wrapper that enables quote matching unless an attempted completion function is supplied.
- `_el_fn_complete()` and `_el_fn_sh_complete()` are bindable libedit command wrappers.

Escaping logic:
- `needs_escaping()` identifies shell-special wide characters.
- `needs_dquote_escaping()` restricts escaping inside double quotes to `"`, `\`, `` ` ``, and `$`.
- `unescape_string()` removes backslashes for matching.
- `escape_filename()` applies shell escaping according to current quote context and appends a space or `/` for single matches.
- `find_word_to_complete()` scans backward from the cursor to find the completion word, respecting escaped break characters and optional special prefixes.

Completion flow:
- Determine whether the previous command was also completion; repeated completion lists matches.
- Find and optionally unescape the current word.
- Call an attempted completion function if provided; otherwise call `completion_matches()` with the filename generator.
- Replace the current word with the common match prefix.
- For a single match, optionally append a suffix from `app_func()` and close quotes.
- For multiple matches on list request, prompt when above `query_items`, then display columns.
- Free all match strings and temporary buffers.

Risks and notes:
- `fn_filename_completion_function()` uses static directory/name state, so it is not reentrant or thread-safe.
- Escaping is shell-oriented and carefully quote-context dependent; tests cover many special characters.
- User confirmation for large match lists reads from `stdin` directly.
- Some allocation failure paths free top-level arrays but not necessarily already collected individual strings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.h

This header declares libedit file completion APIs.

Key declarations:
- `fn_complete()` and `fn_complete2()` perform completion with generator callbacks, attempted-completion callbacks, break characters, optional suffix function, query threshold, and optional readline-style result fields.
- `FN_QUOTE_MATCH` requests quote-aware matching/escaping.
- `fn_display_match_list()` prints matches in columns.
- `fn_tilde_expand()` expands `~` paths.
- `fn_filename_completion_function()` generates filename matches.
- `completion_matches()` provides readline-compatible match collection.

Integration:
- Included by `filecomplete.c`, tests, and code binding completion commands.
- Uses `EditLine *` from `histedit.h`/internal headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/filecomplete.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/hist.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/hist.c

This file connects `EditLine` to a history backend.

Key functions:
- `hist_init()` allocates the current-line history scratch buffer.
- `hist_end()` frees it.
- `hist_set()` installs the history function pointer and reference pointer.
- `hist_get()` loads either the saved current line or a selected history event into `el_line`.
- `hist_command()` implements editline `history` subcommands.
- `hist_enlargebuf()` grows the internal history scratch buffer.
- `hist_convert()` adapts narrow-history responses to wide strings.

Important behavior:
- `hist_get()` treats `eventno == 0` as the current editable line and restores from `el_history.buf`.
- For nonzero history events, it starts at `HIST_FIRST()` and walks forward `eventno - 1` entries.
- Loaded history lines have trailing newline and trailing space trimmed.
- Cursor placement differs for vi vs non-vi maps.
- `hist_command()` supports listing history and setting `size` or `unique`.

Integration:
- Uses macros from `hist.h` to call the installed history backend.
- Uses `ct_encode_string()`, `ct_decode_string()`, and `strvis()` for display/conversion.

Risks and notes:
- If no history backend is installed, history operations return errors.
- History listing dynamically grows a temporary escaped-output buffer.
- `hist_convert()` relies on `NARROW_HISTORY` callers passing narrow strings through a wide-event typed interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/hist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/hist.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/hist.h

This internal header defines libedit's history adapter state and helper macros.

Key types:
- `hist_fun_t`: callback type for history operations.
- `el_history_t`: current-line scratch buffer, buffer size, last pointer, selected event number, backend reference, backend function, and event cookie.

Key macros:
- `HIST_FUN_INTERNAL()` calls the installed history function and returns `ev.str` or NULL.
- `HIST_FUN()` routes through `hist_convert()` when `NARROW_HISTORY` is set.
- Convenience macros wrap common operations: `HIST_NEXT`, `HIST_FIRST`, `HIST_LAST`, `HIST_PREV`, `HIST_SET`, `HIST_LOAD`, `HIST_SAVE`, `HIST_SAVE_FP`, and `HIST_NSAVE_FP`.

Declared functions:
- History lifecycle, event loading, backend installation, command handling, buffer growth, and narrow-to-wide conversion.

Integration:
- Included by `el.h`; command files use these macros for history navigation/search.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/hist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/histedit.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libedit/histedit.h

This is the public libedit API header for editing, history, and tokenization.

Public editing API:
- Opaque `EditLine`.
- Narrow `LineInfo`.
- Command return codes `CC_NORM` through `CC_REFRESH_BEEP`.
- Lifecycle: `el_init()`, `el_init_fd()`, `el_end()`, `el_reset()`.
- Input: `el_gets()`, `el_getc()`, `el_push()`.
- Configuration and commands: `el_set()`, `el_get()`, `el_parse()`, `el_source()`, `el_resize()`.
- Editing helpers: `el_line()`, `el_insertstr()`, `el_deletestr()`, `el_replacestr()`, `el_deletestr1()`.
- Completion helpers: `_el_fn_complete()` and `_el_fn_sh_complete()`.

Configuration constants:
- `EL_PROMPT`, `EL_TERMINAL`, `EL_EDITOR`, `EL_SIGNAL`, `EL_BIND`, `EL_TELLTC`, `EL_SETTC`, `EL_ECHOTC`, `EL_SETTY`, `EL_ADDFN`, `EL_HIST`, `EL_EDITMODE`, `EL_RPROMPT`, `EL_GETCFN`, `EL_CLIENTDATA`, `EL_UNBUFFERED`, `EL_PREP_TERM`, `EL_GETTC`, `EL_GETFP`, `EL_SETFP`, `EL_REFRESH`, `EL_PROMPT_ESC`, `EL_RPROMPT_ESC`, `EL_RESIZE`, `EL_ALIAS_TEXT`, `EL_SAFEREAD`, `EL_WORDCHARS`, and `EL_GETENV`.

Public history API:
- Opaque `History`.
- `HistEvent` with event number and string.
- `history_init()`, `history_end()`, and `history()`.
- Operation constants from `H_FUNC` through `H_NSAVE_FP`, covering navigation, add/enter/append, load/save, clear, uniqueness, deletion, data events, replacement, and file-pointer save.

Public tokenizer API:
- Opaque `Tokenizer`.
- `tok_init()`, `tok_end()`, `tok_reset()`, `tok_line()`, and `tok_str()`.

Wide-character API:
- `LineInfoW`, `HistEventW`, `HistoryW`, and `TokenizerW`.
- Wide versions of get/push/parse/set/get/line/insert/replace/history/tokenizer functions.
- `el_cursor()` for cursor movement.

Integration:
- Defines `LIBEDIT_MAJOR 2` and `LIBEDIT_MINOR 11`.
- Provides C++ linkage guards.

Risks and notes:
- The `el_set()`/`el_get()` API is varargs-heavy; callers must match the documented argument types exactly.
- Narrow and wide APIs share the same `EditLine` object, with conversion wrappers in `eln.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libedit/histedit.h -->