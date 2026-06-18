# Research: subset-b-007618

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/depcomp -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/depcomp

## Purpose
`depcomp` is the Automake dependency-compilation wrapper bundled with crcutil. It runs a compiler command while also producing a make-readable dependency file for the compiled source, normalizing many compiler-specific dependency formats into Automake's expected `.P*` files.

## Important inputs and modes
The script requires environment variables `depmode`, `source`, and `object`; it optionally uses `DEPDIR`, `depfile`, `tmpdepfile`, and `libtool`. With no command it errors; `--help` and `--version` print metadata. If `depfile` is unset, it maps an object like `sub/bar.o` to `sub/.deps/bar.Po`; if `tmpdepfile` is unset, it derives a temporary `.T*` file.

Supported modes include `gcc3`, `gcc`, `hp`, `sgi`, `aix`, `icc`, `hp2`, `tru64`, `dashmstdout`, `dashXmstdout`, `makedepend`, `cpp`, `msvisualcpp`, `msvcmsys`, and `none`. Some modes are aliases or markers used by Automake's `depend.m4`, such as `hp`, `dashXmstdout`, and `msvcmsys`.

## Control flow
The preamble validates required variables, computes output paths, removes stale temporary dependency files, and normalizes alias modes. The large case dispatch then executes the compiler command with mode-specific dependency flags or, for slower modes, runs the compile first and then derives dependencies through preprocessor output or `makedepend`.

For GCC-like modes it uses `-MD`, `-MP`, `-MF`, or `-Wp` flags and then rewrites the dependency file so the target is the requested object and every header also has a dummy `header:` rule. Vendor modes handle dependency files emitted in unusual locations, including AIX `.u`, HP `.d`, Tru64 `.o.d`, libtool `.libs` paths, and Intel compiler output. Preprocessor-based modes remove libtool wrappers and `-o object` arguments before extracting included file paths from stdout. `none` simply execs the compiler command without dependency generation.

## State and persistence behavior
The persistent output is `depfile`, usually under `.deps`, containing an object dependency rule plus dummy header rules to avoid deleted-header make failures. The script creates and removes `tmpdepfile` and compiler-specific temporary dependency outputs. On compiler failure, it deletes temporary files and exits with the compiler status. It does not maintain long-lived state outside generated dependency files.

## Dependencies and integration points
`depcomp` is called from Automake-generated `Makefile` rules selected by `configure`'s dependency-mode probes. It depends on a POSIX shell plus standard tools such as `sed`, `tr`, `sort`, `grep`, and optionally `cygpath` and `makedepend`. It integrates with libtool compile wrappers when `libtool=yes` and with make include syntax detected during configuration.

## Risks and edge cases
Dependency mode detection is compiler-specific and conservative; a compiler that accepts unknown flags with warnings can produce false positives, so configure greps stderr for Intel ignored-option messages. Path handling must account for DOS drive letters, spaces, object files in subdirectories, and libtool's `.libs` outputs. The generated dependency file can become stale if a compiler writes dependencies somewhere unexpected. Manual edits should be avoided because Automake may replace this file.

## Test signals
The strongest test is `./configure` dependency-style detection followed by a normal `make` with dependency tracking enabled. Inspect `.deps/*.Po` or `.Plo` files to ensure they reference the expected object and included headers. Rebuild after deleting a header from a dependency file to verify dummy header rules avoid make parse failures. Also validate `--disable-dependency-tracking`, which should bypass this wrapper for normal builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/depcomp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/doc/text/convert.awk -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/doc/text/convert.awk

## Purpose
This small AWK filter converts whitespace-separated input rows into a LaTeX-style table row format. It appears intended for documentation text generation, aligning the first column and emitting ampersand-separated fields followed by a LaTeX row terminator.

## Important variables and behavior
- `first_line` is initialized to `1` in `BEGIN`.
- On the first processed record, the script prints twenty leading spaces before any fields.
- For each field `i`, if it is the first field of a non-first line, it is printed in a fixed width of 20 characters without a leading ampersand.
- All other fields are printed as ` &` plus a six-character field width.
- Every input record ends with four spaces and `\\`, then `first_line` is set to `0`.

## Control flow
The script is purely streaming. AWK reads one input record at a time, loops `i = 1` through `NF`, emits formatted columns, prints the row terminator, and moves to the next input line. There are no pattern-specific branches beyond the `first_line` and first-field checks.

## State and persistence behavior
The only state is the in-memory `first_line` flag. There are no files opened by the script itself, no accumulated output, and no persistence across AWK invocations. Output goes to stdout.

## Dependencies and integration points
The script depends on a standard AWK implementation and on callers redirecting stdout to the desired documentation artifact. It integrates with crcutil's `doc/text` workflow, likely converting benchmark or tabular text data into LaTeX table rows for documentation.

## Risks and edge cases
Fields are split with AWK's default whitespace rules, so input values containing spaces cannot be preserved as a single table cell. Values wider than the fixed widths are not truncated, so alignment can drift. The script does not escape LaTeX-sensitive characters such as `_`, `%`, `&`, or `#`; callers must provide safe input or escape it earlier. Empty lines produce only the row terminator and spacing.

## Test signals
Run `awk -f convert.awk` on representative multi-row numeric/text input and verify the first row has an empty first-column pad while later rows place the first field in the 20-character slot. Include wide fields and LaTeX metacharacters in a manual test if the generated documentation will be compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/doc/text/convert.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.cc

## Purpose
This C++ file implements the clean `crcutil_interface::CRC` facade declared in `examples/interface.h`. It hides crcutil's template-heavy, macro-heavy implementation headers behind a stable virtual interface, centralizes CRC table allocation/alignment, and selects between generic, 128-bit SSE2-backed, and SSE4.2 CRC32C implementations.

## Important types and functions
- `kAlign` is a 4 KiB alignment boundary used for CRC tables and instances.
- Template class `Implementation<CrcImplementation, RollingCrcImplementation>` derives from `CRC` and adapts concrete crcutil implementations to the virtual facade.
- `Implementation::Create` uses `AlignedAlloc(sizeof(Self), offsetof(Self, crc_), kAlign, allocated_memory)` followed by placement new, ensuring internal CRC tables are aligned.
- `Delete` calls `AlignedFree(this)` rather than plain `delete`.
- Property methods expose generating polynomial, degree, canonical XOR value, rolling start value, rolling window size, and self-check CRC.
- Data methods implement `Compute`, `RollStart`, `Roll`, `CrcOfZeroes`, `ChangeStartValue`, `Concatenate`, `StoreComplementaryCrc`, `StoreCrc`, and `CrcOfCrc`.
- Static helper overloads `GetValue` and `SetValue` convert between the public `UINT64 lo/hi` representation and concrete crcutil CRC types.
- `CRC::IsSSE42Available` delegates to `Crc32cSSE4::IsSSE42Available()` on x86/x86_64 builds and returns false otherwise.
- `CRC::Create` validates arguments and chooses the implementation type.

## Control flow
The template adapter constructs `crc_` from polynomial, degree, and canonical mode, then constructs `rolling_crc_` from the CRC object, rolling window length, and rolling start value. Every virtual operation converts public `lo`/`hi` inputs to the concrete CRC type, delegates to crcutil's base or rolling implementation, and writes the result back through `SetValue`.

`CRC::Create` first rejects degree 0. For degrees above 64, it requires `HAVE_SSE2`, rejects degrees above 128, validates that polynomial and rolling start values fit the selected degree, chooses a `GenericCrc<uint128_sse2,...>` specialization based on architecture and GCC version, and returns an `Implementation<Crc128, RollingCrc<Crc128>>`. For 64-bit-or-smaller CRCs, it optionally selects `Crc32cSSE4` plus `RollingCrc32cSSE4` when `CRCUTIL_USE_MM_CRC32`, x86/x86_64, `use_sse4_2`, degree, polynomial, and high words match CRC32C constraints. Otherwise it validates that high words and out-of-degree bits are zero and returns a generic 64-bit implementation.

## State and persistence behavior
Instances are effectively immutable after construction: `crc_` and `rolling_crc_` are `const`, and no persistent global mutable state is modified besides the file-scope `kAlign`. Runtime state lives in allocated aligned memory owned by the returned `CRC*`. The caller must destroy it with `CRC::Delete`; the destructor is protected and not intended for direct deletion. `SelfCheckValue` computes a CRC over the in-memory `crc_` and `rolling_crc_` objects, providing a runtime integrity signal for generated tables.

## Dependencies and integration points
The implementation includes `aligned_alloc.h`, `crc32c_sse4.h`, `generic_crc.h`, `protected_crc.h`, and `rolling_crc.h` from crcutil, and `interface.h` for the public contract. It depends on configuration/architecture macros such as `HAVE_AMD64`, `HAVE_I386`, `HAVE_SSE2`, `CRCUTIL_USE_MM_CRC32`, and `GCC_VERSION_AVAILABLE`. It is demonstrated by `examples/usage.cc` and is a recommended pattern for projects that want to use crcutil without exposing internal template headers and macros across the whole codebase.

## Risks and edge cases
Memory management is nonstandard: callers must use `Delete`, and failed allocation is not explicitly checked before placement new. Public methods generally assume non-null `lo` and, for CRC widths above 64 bits, non-null `hi`; passing null `hi` for a 128-bit instance can dereference null in `GetValue`/`SetValue`. `offsetof` is locally redefined for GCC to avoid a warning, which is brittle. Degree validation uses shifts and has special cases for degree 64 and 128 to avoid undefined or meaningless checks. SSE4.2 selection is only correct for CRC32C and only after hardware availability is checked.

## Test signals
Build and run `examples/usage.cc`, which exercises both generic CRC32 and CRC32C paths, rolling CRC, zero CRC, start-value changes, concatenation, complementary CRC storage, CRC storage, and `CrcOfCrc`. Add tests for invalid `Create` arguments: degree 0, degree above 128, out-of-range polynomial bits, out-of-range rolling start bits, and SSE4.2 requested for non-CRC32C polynomials. On machines with and without SSE4.2, verify `IsSSE42Available` and output self-check values are stable for the same build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.h

## Purpose
This header declares a clean virtual CRC interface for projects that want to use crcutil without including crcutil's implementation templates and macros throughout their codebase. It is intentionally small and opaque: users create a `CRC` object through a factory, operate through virtual methods, and destroy through `Delete`.

## Important APIs and types
- `crcutil_interface::UINT64` is an unsigned long long alias used for the public low/high CRC representation.
- `CRC::Create` constructs an implementation from a reversed-bit polynomial split into low/high words, polynomial degree, canonical mode, rolling CRC start value, rolling window length, optional SSE4.2 preference, and optional allocated-memory output.
- `Delete` destroys an instance created by `Create`.
- `IsSSE42Available` reports hardware support for SSE4.2 CRC instructions where compiled.
- Property methods are `GeneratingPolynomial`, `Degree`, `CanonizeValue`, `RollStartValue`, `RollWindowBytes`, and `SelfCheckValue`.
- Computation methods are `Compute`, `RollStart`, `Roll`, `CrcOfZeroes`, `ChangeStartValue`, `Concatenate`, `StoreComplementaryCrc`, `StoreCrc`, and `CrcOfCrc`.
- The constructor and destructor are protected, enforcing factory allocation and custom deletion.

## Control flow and usage contract
Callers first invoke `CRC::Create`. If arguments are illegal, it returns `NULL`; otherwise it returns a polymorphic object. The caller initializes CRC values in `lo` and optionally `hi`, then passes pointers into computation methods. For CRC degrees 64 or less, `hi` is optional and not touched according to the interface comments. For rolling CRC, callers should call `RollStart` before `Roll`, and should avoid rolling operations when the configured rolling window length is zero.

## State and persistence behavior
The interface exposes no mutable member fields. Concrete implementations are intended to be immutable constants with precomputed tables, so applications should create a small number of instances and reuse them. Persistence is limited to process memory. The `allocated_memory` output can be used by callers to inspect or track the raw allocation returned by the aligned allocator in the implementation.

## Dependencies and integration points
The header includes `std_headers.h` for `size_t` and is implemented by `examples/interface.cc`. It integrates with crcutil's generic, rolling, and hardware-accelerated CRC implementations while keeping those dependencies out of downstream translation units. `examples/usage.cc` demonstrates the public contract.

## Risks and edge cases
The API uses raw pointers, nullable output parameters, and a custom lifecycle; misuse can leak memory or dereference null pointers. The comments say `RollStart` and `Roll` should not be called when rolling CRC is disabled, but enforcement is implementation-dependent. For CRC widths above 64 bits, callers must provide the high-word pointers even though many methods default `hi` to `NULL`; that default is only safe for 64-bit-or-smaller CRCs. `Create` returns `NULL` instead of an error object, so callers need explicit validation.

## Test signals
Compile a downstream file including only `interface.h` to ensure implementation details remain hidden. Exercise every public method with a known CRC32C configuration and verify full-message CRC equals incremental CRC, rolling results match direct computation, `Concatenate` matches direct concatenation, and stored CRC/complementary CRC properties hold. Add negative tests for illegal `Create` arguments and null pointer handling at the application boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/usage.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/usage.cc

## Purpose
This example program demonstrates how to use the `crcutil_interface::CRC` wrapper. It constructs CRC instances, prints their properties, computes CRCs in several ways, validates rolling and algebraic CRC operations, stores CRC bytes into a message buffer, and deletes the objects.

## Important functions and data
- `kRollWindow` is `4`, used for rolling CRC examples.
- `kTestData` is the sample message `"abcdefgh"`.
- `kTestDataHead` and `kTestDataTail` split the message for incremental and concatenation demonstrations.
- `xprintf` wraps `vprintf`, flushes stdout, and avoids GCC warnings about `long long` format handling in older GCC versions.
- `Show(const CRC*)` contains the full demonstration sequence.
- `ShowAndDelete(CRC*)` calls `Show` then `Delete`.
- `main` creates two 32-bit canonical CRC instances with different reversed polynomials and rolling start values, using `CRC::IsSSE42Available()` to allow the CRC32C hardware path where applicable.

## Control flow
`main` calls `CRC::Create` twice, first for polynomial `0xEB31D82E` and then for CRC32C/Castagnoli polynomial `0x82f63b78`, both degree 32. Each pointer is passed to `ShowAndDelete`. `Show` starts by reading and printing polynomial, degree, canonical value, rolling start value, rolling window length, and self-check value.

The computation section calculates a CRC over the whole message, then recomputes it incrementally over head and tail chunks. It compares `CrcOfZeroes` against an actual zero-filled buffer. For rolling CRC, it prints expected values by direct computation for each four-byte window and actual values by `RollStart` plus repeated `Roll`. It demonstrates `ChangeStartValue` by converting a CRC computed with start 0 to the value expected with start 1. It demonstrates `Concatenate` by combining CRCs of two message parts. Finally it demonstrates `StoreComplementaryCrc`, `StoreCrc`, and `CrcOfCrc` by appending bytes to a buffer and recomputing.

## State and persistence behavior
The program has only stack/local state and stdout output. `buffer` is reused for zero-data and message-plus-CRC tests. CRC objects allocate internal implementation state through `CRC::Create` and are released by `Delete` in `ShowAndDelete`. No files are read or written.

## Dependencies and integration points
The program includes `std_headers.h` and `interface.h`, depending on the facade rather than crcutil internals. It requires C varargs and stdio functions made available by `std_headers.h`. It links with `examples/interface.cc` and the crcutil implementation headers/templates pulled in there. As an example, it is also a practical smoke test for the facade and for build-system compiler/linker configuration.

## Risks and edge cases
`ShowAndDelete` does not check for `NULL`, so if `CRC::Create` rejects arguments or allocation fails, `Show` will dereference a null pointer. The output is demonstrative rather than assertive; mismatches are printed as `expected` values but do not cause a nonzero exit. Format strings assume `UINT64` is compatible with `%llx` and `%llu`, which matches the typedef here but is less portable if changed. The rolling expected loop iterates `i <= kRollWindow` for the eight-byte test string and four-byte window, which is correct for this sample but tied to the constants.

## Test signals
Run the example and manually or script-check that full and incremental CRCs match, `CrcOfZeroes` matches actual zero-buffer computation, rolling actual values match expected values, `ChangeStartValue` and `Concatenate` match direct recomputation, complementary CRC produces zero, and `CrcOfCrc` equals the predicted constant. Converting the printed comparisons into assertions would make this a stronger automated regression test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/examples/usage.cc -->
