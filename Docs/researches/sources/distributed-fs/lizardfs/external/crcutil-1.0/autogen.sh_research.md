# sources/distributed-fs/lizardfs/external/crcutil-1.0/autogen.sh

## Purpose

`autogen.sh` regenerates the crcutil Autotools build system and optionally configures or builds it. It removes stale generated files, synthesizes `configure.ac` from `autoscan`, writes `Makefile.am`, runs `aclocal`, `autoconf`, `autoheader`, and `automake --add-missing`, then invokes `./configure` with optimized compiler flags before optionally running `make`.

## Important APIs, commands, and modes

The script has a small argument protocol. `autogen.sh clean` removes build and generated Autotools outputs and exits. `autogen.sh clean clean` removes an even fuller generated set because the condition treats argument 2 equal to `clean` as full cleanup. `autogen.sh configure` performs regeneration and configure but exits before `make`. Other first arguments are passed to `make $1`, and the second argument is appended to generated `CFLAGS`/`CXXFLAGS`.

It writes `configure.ac` with `AC_INIT(crcutil, 1.0, crcutil@googlegroups.com)`, `AM_INIT_AUTOMAKE`, `AC_CONFIG_FILES([Makefile])`, and `AC_OUTPUT()`. It writes `Makefile.am` entries for `AM_CXXFLAGS`, optional static `AM_LDFLAGS`, unit test and usage targets, and source lists discovered from `tests/`, `code/`, and `examples/`, excluding files matching `intrinsic`.

## Control flow, state, and persistence

The script is destructive to local generated state: it removes `Makefile`, `Makefile.am`, `Makefile.in`, `aclocal.m4`, `config.h.in`, `configure`, `.deps`, `autom4te.cache`, `config.status`, `config.log`, and related files depending on mode. It then persists regenerated `configure.ac`, `Makefile.am`, `Makefile.in`, and `config.h.in`. Configure output persists `config.h`, `Makefile`, and cache/status files.

## Dependencies and integration points

It depends on Bash, GNU-ish test syntax, `make`, `autoscan`, `sed`, `aclocal`, `autoconf`, `autoheader`, `automake`, `c++ -dumpversion`, `uname`, `ls`, `grep`, and `tr`. It integrates with the code directory by discovering `code/*.cc` and `code/*.h`, and it controls compilation flags consumed by `platform.h` and the CRC intrinsic headers.

## Risks and test signals

The string comparison `[[ "$(c++ -dumpversion)" > "4.4.9" ]]` is lexical, not a robust semantic version check. The script removes generated files without prompting, so it should not be run in a tree with uncommitted generated changes unless that is intended. Static linking is enabled on non-Darwin systems for newer GCC versions, which can fail on environments lacking static libraries. Validation signals are successful Autotools regeneration, successful `./configure`, and a successful `make` or `make check` after script completion.
