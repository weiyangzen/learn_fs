<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/configure.ac -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/configure.ac

## Purpose
This is the concise Autoconf source used to generate crcutil's large `configure` script. It declares the crcutil 1.0 package, requests Automake support, chooses output files, and lists the platform probes needed by the crcutil C/C++ build.

## Important macros and generated outputs
- `AC_PREREQ([2.65])` requires Autoconf 2.65 semantics.
- `AC_INIT(crcutil, 1.0, crcutil@googlegroups.com)` defines package metadata.
- `AM_INIT_AUTOMAKE(crcutil, 1.0)` enables Automake integration for the package.
- `AC_CONFIG_SRCDIR([tests/aligned_alloc.h])` validates that configure is run against the intended source tree.
- `AC_CONFIG_HEADERS([config.h])` makes `config.h` the generated preprocessor configuration header.
- `AC_CONFIG_FILES([Makefile])` makes `Makefile` the generated build file from `Makefile.in`.
- Tool probes are `AC_PROG_CXX`, `AC_PROG_CC`, `AC_PROG_INSTALL`, and `AC_PROG_MAKE_SET`.
- Header probes cover `stddef.h`, `stdlib.h`, and `string.h`.
- Type/compiler probes cover `AC_HEADER_STDBOOL`, `AC_C_INLINE`, `AC_TYPE_SIZE_T`, and `AC_CHECK_TYPES([ptrdiff_t])`.
- Function probes cover `memset`, `strchr`, and `strrchr`.

## Control flow
Autoconf processes these macros into a script that first establishes package identity and output targets, then checks source-tree validity, then searches for build programs, and finally emits compile/link/preprocessor probes for headers, typedefs, compiler keywords, and C library functions. `AC_OUTPUT` appears twice in this file; in generated Autoconf output this still results in the final configuration emission lane, but the duplicate macro is unusual and should be treated carefully if modernizing the build system.

## State and persistence behavior
The file itself has no runtime state. When expanded and executed, it causes `configure` and `config.status` to persist `Makefile`, `config.h`, `config.log`, dependency setup, and cache state. The most important persistent contract is that `config.h` will define or leave undefined macros consumed by crcutil portability headers and sources.

## Dependencies and integration points
This file depends on Autoconf 2.65 and Automake macros being available during regeneration. It integrates with `Makefile.am`/`Makefile.in`, `config.h.in`, and the generated helper scripts such as `depcomp`, `install-sh`, and `missing`. The checked headers/functions are C-level portability signals for the C++ implementation, particularly the custom `std_headers.h` layer used by crcutil examples and implementation headers.

## Risks and edge cases
The duplicate `AC_OUTPUT()` can confuse maintainers and is worth removing during any deliberate regeneration pass after confirming generated output remains equivalent. The source directory sentinel `tests/aligned_alloc.h` couples configuration to the tests folder. The probe list is minimal; crcutil has architecture-sensitive code elsewhere, so CPU/SIMD feature macros likely come from headers or compiler definitions rather than this configure source. Updating to newer Autoconf/Automake may change generated script behavior and dependency tracking defaults.

## Test signals
After editing this file, regenerate with the repository's expected Autotools versions, then compare the generated `configure` and run `./configure`, `make`, and any available `make check`. Confirm `config.h` contains definitions for `HAVE_STDLIB_H`, `HAVE_STRING_H`, `HAVE_STDBOOL_H`, `HAVE__BOOL`, `inline` fallback when needed, `HAVE_PTRDIFF_T`, and the three checked functions on a normal Linux host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/configure.ac -->
