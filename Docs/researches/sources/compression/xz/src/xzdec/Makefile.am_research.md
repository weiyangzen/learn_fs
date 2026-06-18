# sources/compression/xz/src/xzdec/Makefile.am

Purpose: Automake build definition for the small `xzdec` and `lzmadec` decompressor binaries and their man-page installation behavior.

Important build targets and variables: defines shared sources (`xzdec.c`, `tuklib_progname.c`, `tuklib_mbstr_nonprint.c`, `tuklib_exit.c`), optional Windows resource files, `xzdec_CPPFLAGS`, `xzdec_LDADD`, and `lzmadec_*` aliases. `lzmadec` is built from the same C file with `-DLZMADEC`. Conditional `bin_PROGRAMS` entries depend on `COND_XZDEC` and `COND_LZMADEC`.

Control flow: the `.rc.o` rule compiles Windows resources. Build flags disable gettext in tuklib for the tiny tools and include common/liblzma API headers. Optional gnulib and intl libraries are linked. Install hooks install translated `xzdec.1` man pages when available and create `lzmadec.1` symlinks only when both tools are enabled and the target man page exists.

State and persistence: affects generated build artifacts, installed binaries, installed man pages, and symlinks. It does not define runtime state.

Dependencies and integration: integrates with top-level configure conditionals, liblzma, optional gnulib, Windows resource compiler, NLS man-page directories, and Automake install/uninstall hooks.

Risks: the install hook intentionally uses Automake internals by overriding man variables, so Automake changes could break it. The symlink logic must honor transformed program names and avoid dangling links. `lzmadec` inherits most `xzdec` settings, so link flag changes must remain compatible with both formats.

Test signals: build-system validation should cover `--enable/disable-xzdec`, `--enable/disable-lzmadec`, Windows resources, NLS man-page installs, and uninstall cleanup.
