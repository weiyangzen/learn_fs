# subset-b-009530 Research

Grouped source research for xfstests-bld terminal/filesystem helper programs and the vendored `popt` Autotools configuration templates. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/resize.c -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/resize.c

## Purpose

`sources/test-tools/xfstests-bld/fstests-bld/misc/resize.c` is a small terminal-size discovery and update helper derived from xterm's `resize.c` and simplified for kvm-xfstests. It talks directly to the controlling terminal, asks the terminal emulator for its cursor-position response after moving to a very large row/column, then uses the answer to set the kernel's terminal window size with `TIOCSWINSZ`. It also prints shell-style `COLUMNS=` and `LINES=` assignments for consumers that want to update their environment.

The source was read as a complete 207-line C file for this report.

## Important APIs, Types, and Functions

Important constants and globals: `ESCAPE(string)` builds ANSI escape sequences, `TIMEOUT` is the 10-second read deadline, `myname` is used in diagnostics, `tty` and `ttyfp` refer to `/dev/tty`, and `tioorig` stores the original terminal attributes for cleanup. The escape templates are `getsize` (`ESC 7`, reset scroll region, move to `999;999`, device status report), `restore` (`ESC 8`), and `size` (`ESC "[%d;%dR"`).

`failed(const char *s)` preserves `errno`, writes a program-name prefix directly to stderr, calls `perror`, and exits. `onintr(int sig)` restores the original termios settings with `tcsetattr(TCSADRAIN)` and exits. `resize_timeout(int sig)` reports a timeout and reuses the interrupt cleanup path. `readstring(FILE *fp, char *buf, const char *str)` arms `SIGALRM`, reads a terminal response until the expected final byte from the format string, normalizes the single-byte CSI value `0233` into `ESC [` when present, and aborts if the first byte does not match the expected response.

`main` owns the full program lifecycle: open `/dev/tty`, put it into noncanonical/no-echo 8-bit mode, query terminal dimensions, restore terminal state, update `struct winsize`, call `ioctl(TIOCSWINSZ)`, and print `COLUMNS`/`LINES`.

## Control Flow

Startup opens `/dev/tty` read/write and records its file descriptor. The program copies current termios settings, disables CR-to-NL translation, disables canonical input and echo, forces `CS8`, and sets `VMIN=6` and `VTIME=1` so escape-response reads have a minimum shape and short inter-byte timeout. It installs `SIGINT`, `SIGQUIT`, and `SIGTERM` handlers only after the original settings are captured.

After switching the terminal into the temporary raw-ish mode, the program writes the size query escape sequence to the terminal. The terminal should save the cursor, reset the scroll region, move to a clamped bottom-right position, and respond to the device-status-report request with `ESC[row;colR`. `readstring` collects that response and `sscanf(buf, size, &rows, &cols)` parses the discovered dimensions. The cursor is restored, the original terminal settings are restored, and signal handlers are reset to default.

The final phase reads the existing kernel window size with `TIOCGWINSZ` when possible. If existing pixel dimensions and row/column counts are available, it scales `ws_xpixel` and `ws_ypixel` proportionally to the newly discovered columns and rows. It then writes the new `ws_row` and `ws_col` via `TIOCSWINSZ`, reports an ioctl error without changing the success exit path, prints the environment assignments, and exits 0.

## State and Persistence Behavior

The only persistent external state mutation is the terminal driver's window-size record for the controlling tty through `TIOCSWINSZ`. The program temporarily mutates terminal line discipline settings but stores `tioorig` and restores it on normal completion, handled signals, and timeout paths. It does not persist files or configuration. Its printed `COLUMNS` and `LINES` values are not applied to the parent shell unless a caller evaluates or otherwise consumes the output.

## Dependencies and Integration Points

The helper depends on a real controlling terminal at `/dev/tty`, ANSI/VT-style escape behavior, POSIX termios, Unix signals and alarms, and `TIOCGWINSZ`/`TIOCSWINSZ` ioctls from `<sys/ioctl.h>`. In xfstests-bld/kvm-xfstests, it integrates with scripts or login/session setup that need terminal dimensions inside VM consoles where inherited window size may be missing or stale.

## Risks and Edge Cases

The program can block until the 10-second alarm if the terminal does not answer the escape query, if stdin/stdout are not connected to an interactive terminal, or if the terminal response is malformed. `readstring` does not check EOF while filling `buf`, and the loop trusts that the expected final byte will eventually appear before the alarm. Signal handling uses functions such as `tcsetattr`, `fprintf`, and `exit` from handlers; this is common in older terminal utilities but not async-signal-safe. `tcsetattr` after entering raw mode is not checked before the query, so write/read failures are diagnosed later and not at the exact failing operation. Pixel scaling uses integer division based on the old row/column counts, so pixel values can lose precision or remain zero.

## Test Signals

Useful signals include compiling the helper on Linux with warnings enabled; running it under a pseudo-terminal that returns a controlled `ESC[24;80R` response and verifying `TIOCSWINSZ` receives 24 rows and 80 columns; timeout testing with a pty that never responds; interruption testing that confirms termios settings are restored after `SIGINT`; and integration testing from a kvm-xfstests console to verify both kernel winsize and emitted `COLUMNS`/`LINES` values match the actual terminal.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/resize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/syncfs.c -->
# sources/test-tools/xfstests-bld/fstests-bld/misc/syncfs.c

## Purpose

`sources/test-tools/xfstests-bld/fstests-bld/misc/syncfs.c` is a minimal command-line wrapper around the Linux `syncfs(2)` system call. Given a path to a file or directory, it opens that path and asks the kernel to flush all dirty data and metadata for the filesystem containing the opened file descriptor. This gives shell-based filesystem tests a precise way to issue filesystem-scoped syncs without syncing every mounted filesystem.

The source was read as a complete 40-line C file for this report.

## Important APIs, Types, and Functions

The file defines `_GNU_SOURCE` so glibc exposes the `syncfs` prototype from `<unistd.h>`. `progname` holds `argv[0]` for usage output. `usage(void)` prints `Usage: <progname> <file>` and exits 1. `main(int argc, char **argv)` validates that exactly one path argument was supplied, opens it read-only with `open(argv[1], O_RDONLY)`, reports open failures with `perror(argv[1])`, calls `syncfs(fd)`, reports sync failures with `perror("syncfs")`, and returns 0 on success.

## Control Flow

The control flow is deliberately linear. Argument validation happens first; incorrect invocation never attempts filesystem work. A successful `open` anchors the operation to the target file's mount. A successful `syncfs` completes the requested flush and the program exits 0. There is no retry logic, option parsing, directory traversal, or fallback to global `sync(2)`.

## State and Persistence Behavior

This helper does not maintain application state or write files directly. Its external side effect is forcing writeback for dirty data and metadata associated with the filesystem that owns the opened file descriptor. The file descriptor is not explicitly closed, relying on process exit for cleanup. It does not change the target file's contents, permissions, or timestamps except for any effects the kernel filesystem implementation associates with completing pending writeback.

## Dependencies and Integration Points

The program depends on Linux or another libc/kernel combination that provides `syncfs`, plus ordinary POSIX file APIs from `<fcntl.h>` and `<unistd.h>`. It integrates with xfstests-bld shell tests that need to flush a specific mounted test filesystem before crash simulation, remount, snapshot comparison, or durability assertions.

## Risks and Edge Cases

`syncfs` is Linux-specific and gated by `_GNU_SOURCE`, so portability to non-Linux targets is intentionally limited. Opening the path read-only can fail for permission, missing file, stale mount, or path resolution errors; the program reports the path but does not add contextual mount information. It does not use `O_DIRECTORY`, so both files and directories work, but symlinks are followed by default. The helper exits immediately after a failed `syncfs` without closing the descriptor, which is acceptable for a short-lived utility but not a reusable library pattern. Tests that need to distinguish writeback errors from earlier failed writes must remember that `syncfs` can surface delayed filesystem errors.

## Test Signals

Useful signals include a compile test on the intended Linux toolchain; invoking without arguments and with too many arguments to confirm usage failure; invoking on an existing file and directory on a writable test filesystem; invoking on a missing path to confirm the path-specific `perror`; and fault-injection or special-device tests that can make `syncfs` return an error and confirm the utility exits nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/misc/syncfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/Makefile.in

## Purpose

`sources/test-tools/xfstests-bld/fstests-bld/popt/Makefile.in` is the Automake-generated build template for the vendored `popt` command-line option parsing library inside xfstests-bld. `configure` substitutes the `@...@` variables to produce `Makefile`, which then builds `libpopt.la`, local test programs, generated metadata files, installation targets, distribution archives, and maintainer utilities. The template preserves upstream Autotools behavior so xfstests-bld can build the bundled library in controlled test images without depending on a system `popt` package.

The source was read as a complete 1234-line generated Makefile template for this report.

## Important APIs, Types, and Functions

The file is Make syntax rather than C, so its important "APIs" are targets, variables, and generated build contracts. Core substituted variables include compiler/toolchain settings (`CC`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `LIBTOOL`, `AR`, `RANLIB`, `INSTALL`), package metadata (`PACKAGE`, `VERSION`, `PACKAGE_STRING`), paths (`prefix`, `libdir`, `includedir`, `mandir`, `srcdir`, `top_srcdir`, `builddir`), gettext/iconv libraries (`LIBINTL`, `LIBICONV`, `LTLIBINTL`, `LTLIBICONV`), and host/build/target triplets.

The main library contract is `usrlib_LTLIBRARIES = libpopt.la`, with `libpopt_la_SOURCES = popt.c poptparse.c poptconfig.c popthelp.c poptint.c` and `libpopt_la_LDFLAGS = -no-undefined @LTLIBINTL@ @LTLIBICONV@ $(am__append_1)`. When configure detects linker version-script support, `am__append_1` adds `-Wl,--version-script=$(top_srcdir)/libpopt.vers`. Public install artifacts are `include_HEADERS = popt.h`, `pkgconfig_DATA = popt.pc`, and `man_MANS = popt.3`.

Test and developer targets include no-install programs `test1`, `test2`, and `tdict`, `TESTS = $(top_srcdir)/testit.sh`, `TESTS_ENVIRONMENT` that points `test1` at the build product, `lint`, `mccabe`, `doxygen`, `lcov-reset`, `lcov`, `lcov-run`, `lcov-report`, `sources`, and `updatepo`.

## Control Flow

The default `all` target requires `$(BUILT_SOURCES)` and `config.h`, then enters `all-recursive`. Because `SUBDIRS = .`, recursive targets normally dispatch back to local `*-am` targets. `config.h` is generated through `stamp-h1`, which invokes `config.status config.h` using `config.h.in` as the source template. Other configured files are generated similarly: `Doxyfile`, `popt.pc`, `popt.spec`, and `test-poptrc`.

Compilation uses Automake's dependency-tracking recipes for `.c.o`, `.c.obj`, and `.c.lo`, with libtool wrapping shared-library compilation and linking. `libpopt.la` links the five libpopt objects and installs into `$(usrlibdir)`, which is set to `$(libdir)`. Test programs link against `$(usrlib_LTLIBRARIES)`, so they exercise the just-built library rather than a system copy.

Install flow is split across generated targets: `install-usrlibLTLIBRARIES` installs the libtool library under `$(DESTDIR)$(usrlibdir)`, `install-includeHEADERS` installs `popt.h`, `install-pkgconfigDATA` installs `popt.pc`, and `install-man3` installs `popt.3`. `install-data-am` includes all four, so this generated file treats the library installation as data-side work for this package. Clean and distclean paths remove build products, dependency directories, generated config outputs, libtool state, and `.ccache` through `distclean-local`.

Distribution flow builds a dist directory from `DISTFILES`, supports multiple archive formats, and runs `distcheck` by unpacking, configuring in a VPATH build, building, checking, installing, uninstalling, and validating that no unexpected files remain. The generated `check-TESTS` target implements Automake's PASS/FAIL/XFAIL/SKIP reporting around `testit.sh`.

## State and Persistence Behavior

The template itself is static until regenerated by Automake, but the produced `Makefile` creates and removes many build-tree artifacts: `config.h`, `stamp-h1`, dependency files under `$(DEPDIR)`, libtool objects and `.libs`, test binaries, generated package files, coverage directories, Doxygen output, and distribution archives. Install targets persist library/header/pkg-config/manpage files under `DESTDIR` and configured prefixes. Maintainer-mode regeneration can update `Makefile.in`, `configure`, `aclocal.m4`, and `config.h.in` when source Autotools inputs change.

## Dependencies and Integration Points

This file integrates the vendored `popt` sources with GNU Autotools: Automake 1.11-era generated rules, Autoconf `config.status`, libtool, optional gettext and iconv support, optional linker version scripts, and optional developer tools such as `splint`, `pmccabe`, `doxygen`, `lcov`, and `genhtml`. It also references upstream distribution inputs like `README`, `ABOUT-NLS`, `COPYING`, `m4/*.m4`, `libpopt.vers`, `popt.pc.in`, `popt.spec.in`, `test-poptrc.in`, and `testit.sh`. For xfstests-bld, this template is part of the local build graph that can produce a bundled `libpopt` and its tests inside the broader filesystem test tooling image.

## Risks and Edge Cases

This is generated code, so hand edits are likely to be overwritten by Automake or `config.status`; behavioral fixes should generally be made in `Makefile.am` or configure inputs when those are available. The template assumes a Unix-like shell environment and Autotools helper scripts, making it fragile if copied into a minimal environment without `sed`, `awk`, `find`, `install-sh`, libtool, or dependency tracking support. Some paths are old-style, such as `pkgconfigdir = $(prefix)/lib/pkgconfig`, which may not match multilib distributions expecting `$(libdir)/pkgconfig`. `distcheck` is intentionally strict and can fail because of missing optional documentation/test tools or generated files left behind. Maintainer targets can mutate generated files and require exact tool versions to avoid churn.

## Test Signals

Important signals include running `./configure` in the `popt` directory and verifying `Makefile` and `config.h` are generated; `make all` to build `libpopt.la`, `test1`, `test2`, and `tdict`; `make check` to execute `testit.sh` against the built `test1`; `make DESTDIR=<tmp> install` followed by inspection of library, header, pkg-config, and manpage locations; `make distcheck` when distribution integrity matters; and `make distclean` to confirm generated build state is removed without deleting source templates.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/config.h.in -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/config.h.in

## Purpose

`sources/test-tools/xfstests-bld/fstests-bld/popt/config.h.in` is the Autoheader-generated C preprocessor template used by `configure` to produce `config.h` for the vendored `popt` library. It lists package metadata, portability feature probes, internationalization support, and large-file settings as `#undef` placeholders. `config.status` rewrites these into concrete `#define` or commented-out entries based on the target build environment.

The source was read as a complete 144-line generated header template for this report.

## Important APIs, Types, and Functions

There are no functions or types; the file's interface is its preprocessor macro set. Internationalization and platform macros include `ENABLE_NLS`, `HAVE_GETTEXT`, `HAVE_DCGETTEXT`, `HAVE_ICONV`, `HAVE_LIBINTL_H`, `HAVE_LANGINFO_H`, `HAVE_CFLOCALECOPYCURRENT`, and `HAVE_CFPREFERENCESCOPYAPPVALUE`. Header and libc capability probes include `HAVE_DLFCN_H`, `HAVE_FLOAT_H`, `HAVE_FNMATCH_H`, `HAVE_GLOB_H`, `HAVE_INTTYPES_H`, `HAVE_MEMORY_H`, `HAVE_STDINT_H`, `HAVE_STDLIB_H`, `HAVE_STRINGS_H`, `HAVE_STRING_H`, `HAVE_SYS_STAT_H`, `HAVE_SYS_TYPES_H`, `HAVE_UNISTD_H`, `HAVE_GETEUID`, `HAVE_GETUID`, `HAVE_MTRACE`, `HAVE_SETREGID`, `HAVE_SRANDOM`, `HAVE_STPCPY`, `HAVE_STRERROR`, `HAVE_VASPRINTF`, and `HAVE___SECURE_GETENV`.

Package and build-layout macros include `PACKAGE`, `PACKAGE_BUGREPORT`, `PACKAGE_NAME`, `PACKAGE_STRING`, `PACKAGE_TARNAME`, `PACKAGE_VERSION`, `VERSION`, `LT_OBJDIR`, `POPT_SOURCE_PATH`, and `POPT_SYSCONFDIR`. Prototype and large-file compatibility macros include `PROTOTYPES`, `__PROTOTYPES`, `STDC_HEADERS`, `_FILE_OFFSET_BITS`, and `_LARGE_FILES`.

## Control Flow

The template has no runtime control flow. Its build-time flow is controlled by Autoconf: `autoheader` generated the template from `configure.ac`; `Makefile.in` has a `stamp-h1` rule that runs `config.status config.h`; and `config.status` substitutes each `#undef` based on configure tests. C source files then include the resulting `config.h` so conditional compilation can select the correct headers, replacement functions, security APIs, gettext/iconv paths, and large-file behavior.

## State and Persistence Behavior

`config.h.in` is source-tree state and should remain stable unless configure probes change. The generated `config.h` is build-tree state and is removed by `distclean-hdr`/`distclean`. Macro choices persist for the lifetime of a configured build directory: changing compilers, libc, prefix, or feature flags requires rerunning `configure` or `config.status` so the generated header remains accurate.

## Dependencies and Integration Points

The template integrates with Autoconf, Autoheader, and the generated `Makefile.in` rules. It is consumed by the `popt` C files and internal headers to guard use of optional system headers/functions, enable native language support, locate the default popt configuration directory, record package identity, and request large-file ABI settings where needed. It also coordinates with gettext/iconv m4 macros and libtool's `LT_OBJDIR` convention.

## Risks and Edge Cases

As a generated template, manual edits can be lost when `autoheader` is rerun; durable changes belong in `configure.ac` or the relevant m4 macros. Incorrect feature detection can cause compile failures or subtler runtime behavior, for example using unavailable secure environment helpers, missing gettext declarations, or building without required large-file flags. Package path macros such as `POPT_SYSCONFDIR` and `POPT_SOURCE_PATH` can embed configure-time paths, so stale generated headers are risky after relocating a build tree. Header inclusion order matters: system headers that depend on `_FILE_OFFSET_BITS`, `_LARGE_FILES`, or prototype macros must see the generated definitions early enough.

## Test Signals

Useful signals include running `autoheader` only in maintainer workflows and confirming the template changes match intended configure checks; running `./configure` and inspecting generated `config.h` for expected package paths, NLS settings, and large-file macros; compiling all `popt` sources with warnings enabled; testing configurations with and without gettext/iconv support; and running `make distclean` to verify generated `config.h` and `stamp-h1` are removed while `config.h.in` remains.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/config.h.in -->
