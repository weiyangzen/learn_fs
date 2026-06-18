# sources/distributed-fs/coda/coda-src/vtools/Makefile.am

## Purpose

`vtools/Makefile.am` is the Automake manifest for Coda venus/client-side command tools. The complete 50-line file was read. It selects installed programs, scripts, man pages, source files, distribution extras, and clean files for the `vtools` directory.

## Important APIs, Types, and Functions

This is build metadata, not C/C++ code. Important Automake variables are `bin_PROGRAMS`, `dist_man_MANS`, `bin_SCRIPTS`, `sbin_PROGRAMS`, per-target `_SOURCES`, `EXTRA_DIST`, and `CLEANFILES`. Conditional blocks use `BUILD_CLIENT` and `HAVE_PYTHON`.

## Control Flow

Automake conditionals install client tools only when `BUILD_CLIENT` is true. If Python is available, `gcodacon` is installed as a script. `codaconfedit` is always listed as an sbin program. Source variables map each program target to its implementation files.

## State and Persistence Behavior

There is no runtime state. Build-time outputs include generated `Makefile.in`, compiled tool binaries, installed man pages, optional scripts, distributed helper scripts, and cleaned generated script files.

## Dependencies and Integration Points

The manifest integrates with the repository's Autotools build system and source files such as `codacon.cc`, `cfs.cc`, `cmon.cc`, `coda_replay.cc`, `hoard.cc`, and `spy.cc`. It also ensures logging helper scripts are included in distribution tarballs through `EXTRA_DIST`.

## Risks and Test Signals

Risks include missing sources causing build failures, conditional installation mismatches, generated script cleanup issues, and tools/man pages drifting out of sync. Test signals are `autoreconf`/`automake` generation, `make distcheck`, builds with `BUILD_CLIENT` on/off, builds with `HAVE_PYTHON` on/off, and install-manifest checks.
