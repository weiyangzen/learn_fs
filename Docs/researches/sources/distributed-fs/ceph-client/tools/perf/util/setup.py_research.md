# sources/distributed-fs/ceph-client/tools/perf/util/setup.py

`setup.py` builds perf's Python extension module named `perf`. It adapts compiler flags from the surrounding Linux/perf build, filters incompatible Python sysconfig flags for clang, and defines custom setuptools commands so extension artifacts are emitted into build directories selected by environment variables.

Required environment inputs are `CC` and `srctree`; the script asserts both. `CC` may include extra options, as in cross or Yocto builds, so the script splits the executable from `cc_options`. It detects clang by running `CC -v` and checking stderr for `clang version`. `src_feature_tests` points at `tools/build/feature`, and `clang_has_option()` compiles `test-hello.c` with a candidate option to detect unsupported clang flags.

When clang is used, the script mutates `sysconfig.get_config_vars()` for `CFLAGS` and `OPT`, removing `-specs=...` and removing options that the detected clang cannot handle, including `-mcet`, `-fcf-protection`, `-fstack-clash-protection`, `-fstack-protector-strong`, `-fno-semantic-interposition`, `-ffat-lto-objects`, `-ftree-loop-distribute-patterns`, and `-gno-variable-location-views`. This prevents Python's build configuration from injecting GCC-oriented flags into the perf extension build.

The custom `build_ext` and `install_lib` classes override `finalize_options()` to force `build_lib`, `build_temp`, and install build directory values from `PYTHON_EXTBUILD_LIB` and `PYTHON_EXTBUILD_TMP`. The `perf` extension compiles `tools/perf/util/python.c`, includes `util/include`, and appends warning/aliasing flags. Clang gets `-Wno-unused-command-line-argument` and optionally `-Wno-cast-function-type-mismatch`; non-clang gets `-Wno-cast-function-type`. All builds add `-fno-strict-aliasing`, write-string/unused/redundant-decl suppressions, and `-Wno-declaration-after-statement`.

State and persistence are build-system side effects: it reads environment variables and compiler diagnostics, mutates Python sysconfig variables in-process, and writes compiled extension outputs through setuptools into the configured build directories. It does not persist configuration files.

Dependencies include Python setuptools, sysconfig, subprocess, regex substitution, shell-like splitting, the Linux source tree, a working C compiler, and the perf `util/python.c` source. Integration points are perf's Makefile/build flow for Python bindings and distro/cross-build systems that set `CC`, `CFLAGS`, `srctree`, and Python extension build directories.

Risks include naive `cc.split()` handling quoted compiler paths or options, possible blocking or partial stderr reads from `Popen([cc, "-v"])`, repeated compiler probes for clang options, assertions producing abrupt failures when environment variables are omitted, and direct mutation of global sysconfig flags affecting any later setuptools behavior in the same process. `build_lib` and `build_tmp` may be `None` if the expected environment variables are missing.

Test signals should include GCC and clang builds, clang builds with GCC-only Python flags, cross-build `CC` values with sysroot/options, missing environment variable failures, build directory overrides, and importing the resulting `perf` Python module.
