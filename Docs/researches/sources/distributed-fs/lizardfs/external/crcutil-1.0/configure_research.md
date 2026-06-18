<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/configure -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/configure

## Purpose
This is the generated GNU Autoconf 2.65 configure script for the bundled crcutil 1.0 library. Its job is to adapt the crcutil build to the local platform by validating the source tree, locating build tools, probing C and C++ compiler behavior, selecting Automake dependency tracking modes, checking required headers/types/functions, and generating `Makefile`, `config.h`, dependency include stubs, `config.status`, `config.log`, and optional `config.cache` entries.

## Important APIs, variables, and script functions
- Shell entrypoint accepts standard Autoconf options such as `--help`, `--version`, `--prefix`, `--srcdir`, `--host`, `--build`, `--cache-file`, `--disable-dependency-tracking`, and tool overrides like `CC`, `CXX`, `CFLAGS`, `CXXFLAGS`, `CPPFLAGS`, `LDFLAGS`, and `LIBS`.
- Package identity variables are `PACKAGE_NAME=crcutil`, `PACKAGE_VERSION=1.0`, `PACKAGE_BUGREPORT=crcutil@googlegroups.com`, and `ac_unique_file=tests/aligned_alloc.h`.
- Portable helper functions include `as_fn_unset`, `as_fn_set_status`, `as_fn_exit`, `as_fn_mkdir_p`, `as_fn_append`, `as_fn_arith`, and `as_fn_error`.
- Compiler and preprocessor helpers include `ac_fn_cxx_try_compile`, `ac_fn_c_try_compile`, `ac_fn_c_try_cpp`, `ac_fn_c_try_run`, `ac_fn_c_try_link`, `ac_fn_c_check_header_mongrel`, `ac_fn_c_check_header_compile`, `ac_fn_c_check_type`, and `ac_fn_c_check_func`.
- Substitution outputs are driven by `ac_subst_vars`, `ac_config_files="Makefile"`, `ac_config_headers="config.h"`, and `ac_config_commands="depfiles"`.

## Control flow
The script starts with M4sh portability setup: it normalizes shell behavior, `PATH_SEPARATOR`, `IFS`, echo implementations, line-number handling, `expr`/`basename`/`dirname`, temporary directory creation, and executable testing. It then parses command-line options, validates installation directory arguments, determines `srcdir`, verifies `tests/aligned_alloc.h`, handles `--help`/`--version`, opens logging, and loads or validates cache variables.

The main body locates Automake support files (`install-sh`, `missing`, `depcomp`), probes a BSD-compatible install tool, checks build-environment sanity with timestamp ordering, selects `strip`, `mkdir -p`, `awk`, and `make`, and defines package macros. It then locates a C++ compiler from prefixed and unprefixed candidates, checks whether it can build and run programs, determines executable and object suffixes, checks GNU compiler status and `-g` support, and evaluates the C++ dependency mode using the bundled `depcomp`.

After that it locates a C compiler, checks GNU status, debug flag support, ISO C89 mode flags, and C dependency tracking. The header/type/function lane runs the C preprocessor sanity check, finds robust `grep`/`egrep`, checks ANSI C headers, checks `sys/types.h`, `sys/stat.h`, `stdlib.h`, `string.h`, `memory.h`, `strings.h`, `inttypes.h`, `stdint.h`, `unistd.h`, explicitly checks `stddef.h`, `stdlib.h`, and `string.h`, verifies `stdbool.h`, `_Bool`, `inline`, `size_t`, `ptrdiff_t`, and functions `memset`, `strchr`, and `strrchr`.

The final phase writes cache state, computes `DEFS=-DHAVE_CONFIG_H`, validates Automake conditionals, emits `config.status`, and runs it unless `--no-create` is set. `config.status` substitutes Makefile variables with generated awk/sed scripts, transforms `config.h.in` into `config.h`, writes stamp files, and creates dummy dependency files for Automake include targets.

## State and persistence behavior
The script persists configuration decisions to `config.log`, `config.status`, generated `Makefile`, generated `config.h`, `stamp-h*`, dependency stubs under `.deps`, and optionally `config.cache`. It creates and removes many `conftest*`, `conf$$*`, and temporary build directories during probing. Cache variables are namespaced as `ac_cv_*` and dependency mode variables as `am_cv_*`; stale cache values are rejected if precious environment variables changed.

## Dependencies and integration points
It depends on POSIX-like `/bin/sh`, Autoconf/Automake helper files, C and C++ compilers, `make`, `awk`, `sed`, `grep`, `egrep`, `mkdir`, `install`, and optionally `cygpath`. It integrates with crcutil's `Makefile.in`, `config.h.in`, and Automake dependency tracking. Downstream crcutil source files include `config.h` or rely on macros discovered here, while `Makefile` uses `CCDEPMODE`, `CXXDEPMODE`, `DEPDIR`, and `am__fastdep*` variables to compile the bundled library and examples.

## Risks and edge cases
This is generated code, so manual edits are brittle and should normally be made in `configure.ac` followed by regeneration. It assumes the source tree contains `tests/aligned_alloc.h`; moving that file without updating `AC_CONFIG_SRCDIR` breaks configuration. Cross-compilation changes runtime checks, especially ANSI header validation and executable tests. Dependency tracking is sensitive to compiler quirks and the bundled `depcomp` script. Paths containing shell metacharacters, unsafe `srcdir` values, broken `ls`, broken `grep`, or old shells cause explicit failures.

## Test signals
Useful validation is `./configure` from the crcutil directory, with and without `--disable-dependency-tracking`, followed by `make` and `make check` if the package test target is available. Inspect `config.log` for failed probes, verify `config.h` contains expected `HAVE_*`, `STDC_HEADERS`, `HAVE_STDBOOL_H`, and type macros, and confirm generated `Makefile` contains the selected compiler and dependency mode. A clean out-of-tree configure run is a strong signal because the script checks for source directories already configured in-place.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/configure -->
