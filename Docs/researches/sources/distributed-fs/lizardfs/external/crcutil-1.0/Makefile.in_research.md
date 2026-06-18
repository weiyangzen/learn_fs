# sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.in

## Purpose

`Makefile.in` is an Automake 1.11.1 generated build template for crcutil. It becomes the concrete `Makefile` after `configure` substitutes compiler, linker, installation, dependency, and package variables. In this vendored LizardFS copy it defines how crcutil builds its unit-test binary `crcutil_ut`, the example/usage binary `usage`, generated headers such as `config.h`, distribution archives, tags, install/uninstall targets, and the Automake test runner.

## Important APIs, types, and targets

The public build surface is made of make targets rather than C++ APIs. `all` depends on `config.h` and `all-am`; `check` builds `crcutil_ut` and runs `check-TESTS`; `usage` is listed in `tmp_PROGRAMS` and installed under `tmpdir=/tmp`; `dist`, `distcheck`, `clean`, `distclean`, `maintainer-clean`, `install`, and `uninstall` are standard Automake targets. `crcutil_ut_SOURCES` and `usage_SOURCES` enumerate the crcutil source headers and architecture-specific implementation files covered by this work item, plus tests or examples.

Important substituted variables include `CC`, `CXX`, `CXXFLAGS`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `OBJEXT`, `EXEEXT`, `srcdir`, `top_srcdir`, `DEPDIR`, and install paths. The crcutil-specific defaults are `AM_CXXFLAGS = -DCRCUTIL_USE_MM_CRC32=1 -Wall -msse2 -Icode` and `AM_CFLAGS = $(AM_CXXFLAGS)`.

## Control flow, state, and persistence

The Makefile controls generated build state: `config.status`, `config.h`, `stamp-h1`, dependency files under `.deps`, object files, binaries, distribution directories, and archives. Rules for `Makefile`, `configure`, `aclocal.m4`, and `config.h.in` rerun Autotools when inputs change. Compile rules emit `.Po` dependency files through `depcomp` when Automake dependency tracking is enabled. `check-TESTS` runs each test executable, classifies PASS/FAIL/SKIP/XFAIL, and returns a failing status on unexpected failure.

## Dependencies and integration points

This file integrates crcutil with Autoconf/Automake, GNU make, shell tools, `awk`, `sed`, `find`, `tar`, compressors, `ctags`/`etags`, and the configured C/C++ toolchain. It wires the core C++ code to tests under `tests/` and examples under `examples/`. The `-msse2` and `CRCUTIL_USE_MM_CRC32` flags affect source-level conditional compilation in `platform.h`, `crc32c_sse4_intrin.h`, and the architecture-specific `.cc` files.

## Risks and test signals

The template is generated, so manual edits can be lost if `automake` reruns from `Makefile.am`. The default `-msse2` and optional `-mcrc32` expectations are x86-centric and can break non-x86 or older toolchains if not configured carefully. Installing `usage` into `/tmp` is unusual and should be treated as a demo artifact rather than a library install contract. The strongest validation signal is `make check`, which builds and runs `crcutil_ut`; `distcheck` adds a heavier signal by verifying VPATH build, install, uninstall, and distribution completeness.
