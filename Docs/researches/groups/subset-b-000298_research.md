# subset-b-000298 research

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/puff.c -->
# sources/compression/zlib/contrib/puff/puff.c

Purpose: `puff.c` is a compact, reference-oriented raw DEFLATE inflater. It documents RFC 1951 behavior through executable code and exposes only `puff()` while keeping all decoding helpers local. It is optimized for clarity and small code size, not throughput.

Important APIs, types, and functions: `struct state` holds input, output, bit-buffer, counters, and a `jmp_buf` used for input exhaustion. `bits()` pulls little-endian DEFLATE bits and longjmps on EOF. `stored()`, `fixed()`, and `dynamic()` implement block kinds. `struct huffman`, `construct()`, and `decode()` build and consume canonical Huffman tables. `codes()` handles literals, end-of-block, and length/distance copies. `puff()` initializes state, loops over blocks, returns documented positive/negative error codes, and updates `destlen`/`sourcelen` only on success or invalid-data errors.

Control flow: `puff()` reads the final-block bit and two-bit type, dispatches to stored/fixed/dynamic block handlers, and repeats until the final block or an error. Fixed blocks lazily construct static Huffman tables. Dynamic blocks read HLIT/HDIST/HCLEN, construct the code-length decoder, expand run-length encoded code lengths, validate end-of-block and incomplete-code cases, then call `codes()`.

State and persistence: All per-call decode state is stack-local except fixed Huffman tables guarded by the static `virgin` flag. That lazy initialization is persistent and not explicitly synchronized. No heap allocation occurs. Output may be `NIL` for sizing-only scans.

Dependencies and integration points: Includes `setjmp.h` and `puff.h`. It is consumed by `pufftest.c`, the puff library targets, and coverage tests that exercise precise error returns. It expects raw DEFLATE data, not zlib/gzip wrappers.

Risks: Fixed-table lazy initialization can race in multithreaded first use. `longjmp` makes control flow non-local. The optional `INFLATE_ALLOW_INVALID_DISTANCE_TOOFAR_ARRR` changes invalid-distance semantics. Public lengths are `unsigned long`, so callers must account for platform width and buffer sizing.

Test signals: `puff/test/tester.cmake` verifies a successful inflate of `zeros.raw`; `tester-cov.cmake` feeds byte strings expecting specific error codes across stored, fixed, dynamic, EOF, output exhaustion, and invalid-distance paths.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/puff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/puff.h -->
# sources/compression/zlib/contrib/puff/puff.h

Purpose: This header defines the standalone public interface for the puff raw DEFLATE inflater and carries the zlib-style license for the puff component.

Important APIs, types, and functions: It defines `NIL` as `((unsigned char *)0)` when absent, enabling the sizing-only mode documented in `puff.c`. It declares `int puff(unsigned char *dest, unsigned long *destlen, const unsigned char *source, unsigned long *sourcelen)`.

Control flow: The header has no runtime control flow. Its include behavior is minimal: only `NIL` is guarded, and there is no conventional whole-header include guard because the declarations are idempotent.

State and persistence: No state is stored here. State ownership belongs to callers through source/destination buffers and length pointers passed into `puff()`.

Dependencies and integration points: Used by `puff.c`, `pufftest.c`, and CMake puff targets. Because it does not include system headers, consumers must provide compatible standard C types implicitly available from their compilation environment.

Risks: The absence of a full include guard is low risk for this simple declaration but differs from typical project style. `NIL` is a macro in the global namespace and could conflict with callers that use a different sentinel. The ABI fixes lengths as `unsigned long`.

Test signals: Build tests compile consumers against shared and static puff targets. Runtime tests indirectly validate that the declared prototype matches `puff.c`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/puff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/puffConfig.cmake.in -->
# sources/compression/zlib/contrib/puff/puffConfig.cmake.in

Purpose: Installed CMake package configuration for the puff contrib library. It resolves optional `shared` and `static` components and imports generated target files.

Important APIs, types, and functions: Uses `puff_FIND_COMPONENTS`, `_puff_supported_components`, `include(... OPTIONAL RESULT_VARIABLE ...)`, `puff_FOUND`, `puff_NOT_FOUND_MESSAGE`, and component-specific variables like `puff_shared_FOUND`.

Control flow: If components are requested, each component must be in the supported list and must load `puff-${component}.cmake`; otherwise `puff_FOUND` is false. If no components are requested, it tries both shared and static configs and then requires both `PUFF::PUFF` and `PUFF::PUFFSTATIC` to exist.

State and persistence: It mutates CMake package-discovery variables in the caller configure process. No files are generated by this template at package-use time.

Dependencies and integration points: Installed by puff CMake packaging and exercised by find-package tests. The config depends on adjacent generated target config files named by component.

Risks: Error messages mention `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC` even though the targets checked are `PUFF::PUFF` and `PUFF::PUFFSTATIC`, which can confuse diagnosis. No-component mode fails unless both library variants were installed.

Test signals: `find_package_test.cmake.in`, `find_package_no_components_test.cmake.in`, and `find_package_wrong_components_test.cmake.in` cover valid components, no-component behavior, and unsupported components.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/puffConfig.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/pufftest.c -->
# sources/compression/zlib/contrib/puff/pufftest.c

Purpose: Command-line example and test driver for `puff()`. It reads raw DEFLATE data from a file or stdin, optionally skips wrapper bytes, determines inflated size, and optionally writes inflated bytes to stdout.

Important APIs, types, and functions: `bythirds()` grows input buffers by roughly the cube root of two to limit allocation slack. `load()` reads the entire stream into heap memory. `main()` parses `-w`, `-f`, and `-nnn`, calls `puff(NIL, ...)` for sizing, and calls `puff(dest, ...)` for output.

Control flow: Arguments are validated first. Input is loaded entirely, skip is applied, and a sizing inflate is attempted. On success it reports decompressed length and unused compressed bytes. With `-w` or `-f`, it allocates an output buffer and inflates again; `-f` halves the destination length to intentionally trigger output-space failure for coverage.

State and persistence: Uses heap buffers for input and optional output, frees them before exit, and writes diagnostics to stderr. It changes stdout to binary mode on DOS/Windows-like platforms before writing bytes.

Dependencies and integration points: Includes `stdio.h`, `stdlib.h`, and `puff.h`; conditionally includes `fcntl.h` and `io.h`. CMake tests compile it against puff shared/static libraries and coverage variants.

Risks: Entire input is loaded into memory, so it is unsuitable for unbounded streams. Return code is the raw `puff()` result, including negative values that shells may map modulo 256. The second inflate ignores its return value after the coverage/fail path.

Test signals: `tester.cmake` runs it on `zeros.raw`; `tester-cov.cmake` pipes crafted byte strings through this executable and checks exact process exit codes.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/pufftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/CMakeLists.txt -->
# sources/compression/zlib/contrib/puff/test/CMakeLists.txt

Purpose: Defines CTest coverage for puff runtime behavior and CMake integration scenarios.

Important APIs, types, and functions: Uses `add_test`, `set_tests_properties`, fixtures, `configure_file`, generator/platform propagation, `add_executable`, `target_link_libraries`, and optional gcov coverage targets. Key variables include `ZLIB_PUFF_BUILD_SHARED`, `ZLIB_PUFF_BUILD_STATIC`, `ZLIB_BUILD_PUFF`, `WORK_DIR`, `inst_setup`, `ZLIB_ARG`, `GCOV_EXECUTABLE`, and `ZLIB_CONTRIB_PREFIX`.

Control flow: When puff is tested standalone, it first installs puff into a private prefix and uses a fixture. It builds shared/static `pufftest` executables on non-Windows, optionally with coverage instrumentation. It then configures template projects for `find_package`, `add_subdirectory`, excluded subdirectory, no-component package discovery, and wrong-component package discovery, registering configure/build tests with fixture dependencies.

State and persistence: Generates temporary test projects and build trees under `WORK_DIR`, and an install tree under `test_install` for package-discovery tests.

Dependencies and integration points: Integrates puff targets with CTest, the top-level zlib build when embedded, and installed package configs. Runtime tests depend on `tester.cmake`, `tester-cov.cmake`, `pufftest.c`, `puff.c`, `puff.h`, and `zeros.raw`.

Risks: Runtime executable tests are skipped on Windows due to `NOT WIN32`. No-component find-package is expected to fail when not both shared and static libraries are built, making test outcome configuration-sensitive. Generator platform handling stores `-A ${GENERATOR}` as one list item, which can be fragile for some CMake command parsing.

Test signals: Provides the primary test matrix for puff: shared/static linking, package import, subdirectory use, excluded-from-all use, unsupported components, and coverage-specific malformed DEFLATE inputs.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/add_subdirectory_exclude_test.cmake.in -->
# sources/compression/zlib/contrib/puff/test/add_subdirectory_exclude_test.cmake.in

Purpose: Template for a consumer project that verifies puff can be embedded with `add_subdirectory(... EXCLUDE_FROM_ALL)`.

Important APIs, types, and functions: Declares project metadata, sets `ZLIB_PUFF_BUILD_TESTING` off, mirrors shared/static build options, calls `add_subdirectory`, builds `test_example` and/or `test_example_static`, and links `PUFF::PUFF` / `PUFF::PUFFSTATIC`.

Control flow: The generated project adds puff from the source tree while excluding puff's default targets from the all target. It then explicitly creates consumer executables only for enabled variants.

State and persistence: It only affects the generated test build directory and CMake target graph.

Dependencies and integration points: Depends on configured `@puff_SOURCE_DIR@`, `@puff_VERSION@`, and build-option substitutions from the parent test CMake.

Risks: The source list uses `pufftest.c`, which is a full CLI test driver, so target construction validates linking more than a library-like minimal API call. Behavior depends on the parent-provided shared/static option values.

Test signals: Parent CTest configures and builds this project to ensure exported alias targets are available even when puff is excluded from the default build.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/add_subdirectory_exclude_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/add_subdirectory_test.cmake.in -->
# sources/compression/zlib/contrib/puff/test/add_subdirectory_test.cmake.in

Purpose: Template for a consumer project that verifies normal source-tree embedding of puff with `add_subdirectory`.

Important APIs, types, and functions: Sets the generated project, disables puff's own tests, mirrors `ZLIB_PUFF_BUILD_SHARED` and `ZLIB_PUFF_BUILD_STATIC`, calls `add_subdirectory(@puff_SOURCE_DIR@ ...)`, and links generated test executables to `PUFF::PUFF` and `PUFF::PUFFSTATIC`.

Control flow: Configure-time options determine which executable targets are created. CMake then builds the consumer executables against the in-tree puff targets.

State and persistence: No persistent state beyond the generated build tree and target definitions.

Dependencies and integration points: Validates that puff's CMakeLists exports usable alias targets for in-tree consumers.

Risks: Because tests are disabled, this checks build/link integration but not runtime behavior. The consumer compiles `pufftest.c`, so any future dependency changes in that test driver can affect this integration test.

Test signals: Registered by the parent test suite as configure and build CTest entries with fixture ordering.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/add_subdirectory_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/find_package_no_components_test.cmake.in -->
# sources/compression/zlib/contrib/puff/test/find_package_no_components_test.cmake.in

Purpose: Template for testing `find_package(puff REQUIRED CONFIG)` without explicit components.

Important APIs, types, and functions: Defines shared/static options, calls `find_package(puff REQUIRED CONFIG)`, builds `test_example` and/or `test_example_static`, and links imported `PUFF::PUFF` / `PUFF::PUFFSTATIC`.

Control flow: Package discovery occurs before target creation. The template then creates consumers for each enabled build variant.

State and persistence: Uses only generated build-tree state. It reads installed package config files from the prefix provided by the parent test.

Dependencies and integration points: Exercises `puffConfig.cmake` no-component behavior and installed target files.

Risks: The config requires both shared and static targets when no components are requested; the parent test marks configure as `WILL_FAIL` when either variant is disabled. This is intentional but can surprise downstream users expecting no-component discovery to accept any available variant.

Test signals: Parent CTest expects success only when both puff library variants are available.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/find_package_no_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/find_package_test.cmake.in -->
# sources/compression/zlib/contrib/puff/test/find_package_test.cmake.in

Purpose: Template for testing explicit component discovery of installed puff packages.

Important APIs, types, and functions: Uses `find_package(puff REQUIRED COMPONENTS shared CONFIG)` for shared builds and `find_package(puff REQUIRED COMPONENTS static CONFIG)` for static builds, then links `PUFF::PUFF` and `PUFF::PUFFSTATIC` respectively.

Control flow: Shared and static branches run independently based on configured options. Each branch discovers the matching component before creating the executable that links it.

State and persistence: Produces only generated test build targets and CMake cache entries.

Dependencies and integration points: Validates installed `puff-shared.cmake`, `puff-static.cmake`, and `puffConfig.cmake` component handling.

Risks: It does not run the produced executable, so it only catches configure/link problems. Component names are hard-coded to the package config contract.

Test signals: Parent CTest registers configure and build tests after the install fixture, making this the positive package-import path.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/find_package_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/find_package_wrong_components_test.cmake.in -->
# sources/compression/zlib/contrib/puff/test/find_package_wrong_components_test.cmake.in

Purpose: Negative package-discovery template ensuring unsupported puff components fail.

Important APIs, types, and functions: Calls `find_package(puff REQUIRED COMPONENTS wrong CONFIG)` and contains normal shared/static consumer target definitions that should not be reached successfully.

Control flow: Configure should fail during `find_package` because `wrong` is not in `_puff_supported_components`. Parent CTest marks the configure test `WILL_FAIL`.

State and persistence: Only generated CMake configure state is created; no successful build targets are expected.

Dependencies and integration points: Directly validates error handling in `puffConfig.cmake.in`.

Risks: If package config stops rejecting unknown components, this negative test would unexpectedly pass and expose a package contract regression. Later target definitions are mostly incidental.

Test signals: Parent CTest's `WILL_FAIL TRUE` setting makes successful configuration a failure signal.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/find_package_wrong_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/tester-cov.cmake -->
# sources/compression/zlib/contrib/puff/test/tester-cov.cmake

Purpose: CMake script that drives coverage-oriented puff runtime tests using crafted raw DEFLATE byte streams and expected process exit codes.

Important APIs, types, and functions: Defines `puff_cov_test(test_string expected_result)`, using `execute_process` with `cmake -E echo_append` piped through a binary writer and then into the coverage executable. It also invokes gcov at the end.

Control flow: The script first runs the coverage executable with `-w` on `zeros.raw`, then checks many malformed or edge-case streams with expected returns such as `2`, `254`, `249`, and other shell-mapped negative puff codes. It switches to `-f` mode to exercise output exhaustion and finalizes by running gcov on `puff.c.gcno`.

State and persistence: Generates coverage data files in the test working directory and relies on executable exit statuses. No CMake cache mutations are made.

Dependencies and integration points: Called by `puff/test/CMakeLists.txt` coverage tests. Requires the puff coverage executable, source directory, binary writer executable, and gcov executable arguments.

Risks: Negative C return codes are observed as platform-specific process codes, so expected values can be sensitive to shell/OS conventions. The argument comments are stale relative to actual argument use, increasing maintenance risk.

Test signals: Strongly exercises rare branches in `stored()`, `dynamic()`, `codes()`, EOF handling, invalid block types, output exhaustion, and gcov report generation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/tester-cov.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/tester.cmake -->
# sources/compression/zlib/contrib/puff/test/tester.cmake

Purpose: Minimal CMake runtime smoke test for the puff test executable.

Important APIs, types, and functions: Uses `execute_process` to run the executable path in `CMAKE_ARGV3` with `zeros.raw` from `CMAKE_ARGV4` as stdin, captures `RESULT_VARIABLE`, and emits `message(FATAL_ERROR)` on nonzero result.

Control flow: The script performs one command invocation and fails the CTest if the command exit code is nonzero.

State and persistence: No persistent state is written. It streams an input file into the test process.

Dependencies and integration points: Registered for shared and static puff test executables by `puff/test/CMakeLists.txt`.

Risks: It validates only one successful inflate path and does not inspect stdout/stderr. The fatal error text contains a typo, but behavior is unaffected.

Test signals: Confirms the built `pufftest` can successfully read and inflate the canonical `zeros.raw` input.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/puff/test/tester.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/testzlib/CMakeLists.txt -->
# sources/compression/zlib/contrib/testzlib/CMakeLists.txt

Purpose: CMake build definition for the Windows-oriented `testzlib` benchmark/test executable.

Important APIs, types, and functions: Defines project metadata, options `ZLIB_TESTZLIB_BUILD_SHARED`, `ZLIB_TESTZLIB_BUILD_STATIC`, and `ZLIB_TESTZLIB_INSTALL`, computes `REQUIRED_COMPONENTS`, optionally calls `find_package(ZLIB REQUIRED COMPONENTS ... CONFIG)`, and creates shared/static-linked executable targets.

Control flow: When built from the main zlib project, options mirror top-level zlib build flags. Outside zlib, it discovers installed ZLIB components. It conditionally adds `testzlib` linked to `ZLIB::ZLIB` and `testzlibStatic` linked to `ZLIB::ZLIBSTATIC`, then optionally installs runtime executables.

State and persistence: Mutates CMake cache options and install rules. No tests are registered here.

Dependencies and integration points: Integrates with zlib's CMake package targets and install directory variables. The source itself depends on Windows APIs, so successful compilation is platform-specific.

Risks: Shared/static requested components must match available package exports. The script defaults to building both variants, which can fail if only one installed component exists. It does not guard `testzlib.c`'s Windows-only headers.

Test signals: Build/link success is the primary signal. Runtime validation is manual through the produced executable.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/testzlib/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/testzlib/testzlib.c -->
# sources/compression/zlib/contrib/testzlib/testzlib.c

Purpose: Windows command-line utility that compresses and decompresses a file with zlib while reporting timing from `GetTickCount`, `QueryPerformanceCounter`, and optionally `rdtsc`.

Important APIs, types, and functions: Includes Windows and zlib APIs. `MyDoMinus64()` subtracts `LARGE_INTEGER` values. `BeginCountRdtsc()` / `GetResRdtsc()` provide CPU-cycle timing on x86/x64. `BeginCountPerfCounter()` and `GetMsecSincePerfCounter()` provide wall-clock timing. `ReadFileMemory()` loads a file. `main()` runs `deflateInit`/`deflate`/`deflateEnd` and `inflateInit`/`inflate`/`inflateEnd`, then compares output with `memcmp`.

Control flow: After argument parsing and file loading, it allocates an estimated compression buffer, compresses in chunks using `Z_SYNC_FLUSH` until the final `Z_FINISH`, shrinks the compressed buffer, allocates an uncompressed buffer, inflates in chunks, prints timings and sizes, and reports compare success when lengths and bytes match.

State and persistence: Uses heap buffers for file, compressed, and uncompressed data but does not free them before process exit. It maintains timing state in `LARGE_INTEGER` locals.

Dependencies and integration points: Built by `contrib/testzlib/CMakeLists.txt` against shared or static zlib targets. It is Windows-specific due to `windows.h`, `DWORD`, inline assembly/MSVC intrinsics, `min`, and `%I64x`.

Risks: Minimal zlib return checking; loops assume progress and can misbehave on unexpected errors. Buffer-size estimates may be inadequate for pathological data/settings. Uses `long` for file sizes, limiting large files on some builds. No explicit cleanup on early allocation/read failures.

Test signals: Manual run reports compressed/uncompressed sizes, timings, and `compare ok`; no CTest automation is defined in this directory.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/testzlib/testzlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/CMakeLists.txt -->
# sources/compression/zlib/contrib/zlib1-dll/CMakeLists.txt

Purpose: CMake build, install, and test definition for legacy Windows `zlib1.dll` and `zlibwapi.dll` binaries containing zlib plus minizip.

Important APIs, types, and functions: Requires Windows, defines options for bzip2, install, and testing, includes CMake feature-check and package helper modules, generates a configured `zconf.h`, defines public/private header and source lists, creates shared libraries `zlib1` and `zlibwapi`, and exports aliases `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.

Control flow: The script aborts on non-Windows. If embedded in zlib, options mirror top-level settings. It optionally finds BZip2, checks platform functions/types/headers, configures `zconf.h`, builds both DLL variants from zlib and minizip sources, applies compile definitions and include paths, installs targets/config files/headers/license, and optionally adds the test subdirectory.

State and persistence: Writes `zconf.h.cmakein`, `zconf.h`, installed CMake package files, exported target files, headers, DLL import artifacts, and optional PDB files. It also uses cache/internal variables such as `ZLIB_CONF_WRITTEN` and `ZCONF_IN_ZLIB1`.

Dependencies and integration points: Depends on core zlib sources, minizip sources, Windows resource files, CPack, GNUInstallDirs, CMakePackageConfigHelpers, and optional BZip2. It is consumed by its test templates and by downstream `find_package(ZLIB1DLL)`.

Risks: The `foreach(item IN LISTS ${ZCONF_CONTENT})` pattern is suspicious because file content is not a list variable name. Installation config uses `INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/zlib` while install files go to `cmake/zlib1dll`, which may affect relocatability metadata. Non-Windows builds hard fail by design. Exported package naming uses hyphenated project variables, which CMake supports but is easy to mishandle.

Test signals: Test subdirectory validates install/package import and add-subdirectory consumption. Build success also compiles the combined zlib/minizip DLL sources and generated config.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/CMakeLists.txt -->
# sources/compression/zlib/contrib/zlib1-dll/test/CMakeLists.txt

Purpose: CTest suite for zlib1-dll CMake packaging and source embedding.

Important APIs, types, and functions: Uses standalone install fixture, `configure_file` for consumer project templates, generator/platform propagation, `add_test`, and `set_tests_properties`. Key tests cover find-package configure/build, add-subdirectory configure/build, and add-subdirectory with `EXCLUDE_FROM_ALL`.

Control flow: Standalone builds first install zlib1-dll into a private prefix. The script configures three consumer projects and then registers configure and build tests for each, using fixtures to order install/configure/build phases.

State and persistence: Creates generated project directories, build directories, and a private install prefix under `WORK_DIR`.

Dependencies and integration points: Depends on parent `zlib1-dll` targets, `ZLIB1DLLConfig.cmake`, exported targets, and minizip example source lists in the templates.

Risks: Tests always pass `--fresh`, requiring CMake versions that support it; this file itself has no version guard around that flag. Fixture names are reused for multiple configure tests, which is acceptable but can make dependency graphs harder to inspect.

Test signals: Confirms installed package import and in-tree target aliases can link minizip-based consumers against both `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_exclude_test.cmake.in -->
# sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_exclude_test.cmake.in

Purpose: Consumer-project template verifying `zlib1-dll` works when added as an excluded subdirectory.

Important APIs, types, and functions: Calls `add_subdirectory(@zlib1-dll_SOURCE_DIR@ ... EXCLUDE_FROM_ALL)`, defines minizip example sources including conditional `iowin32.c`, creates `test_example` and `test_example_wapi`, and links them to `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.

Control flow: Configure embeds the zlib1-dll project without adding its default targets to `all`, then explicitly builds consumer executables that force the needed DLL targets through link dependencies.

State and persistence: Affects only generated build-tree targets.

Dependencies and integration points: Integrates zlib1-dll with minizip sources and verifies both exported aliases in an embedded build.

Risks: Uses `${WIN32}` inside a generator expression in configured content, so the generated project's platform semantics matter. The test compiles minizip CLI source rather than a minimal symbol check.

Test signals: Parent CTest configures and builds this project to validate excluded-subdirectory consumption.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_exclude_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_test.cmake.in -->
# sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_test.cmake.in

Purpose: Consumer-project template verifying ordinary `add_subdirectory` use of the zlib1-dll project.

Important APIs, types, and functions: Adds `@zlib1-dll_SOURCE_DIR@`, declares minizip example source files, creates two executables, and links against `ZLIB1DLL::ZLIB1DLL` and `ZLIB1DLL::ZLIBWAPI`.

Control flow: The generated project configures zlib1-dll in a sub-build directory and then builds consumers against both DLL variants.

State and persistence: Only generated build-tree targets and CMake cache entries are produced.

Dependencies and integration points: Exercises in-tree aliases and include/link propagation from zlib1-dll to minizip consumers.

Risks: Since zlib1-dll hard-fails off Windows, this template is only meaningful in a Windows test environment. It does not execute the produced binaries.

Test signals: Parent configure/build CTest entries validate that both normal aliases link successfully.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/add_subdirectory_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/find_package_test.cmake.in -->
# sources/compression/zlib/contrib/zlib1-dll/test/find_package_test.cmake.in

Purpose: Consumer-project template for installed `find_package(ZLIB1DLL)` behavior.

Important APIs, types, and functions: Defines a minizip source list, calls `find_package(ZLIB1DLL @zlib1-dll_VERSION@ CONFIG REQUIRED)`, creates `test_example` and `test_example_wapi`, and links imported `ZLIB1DLL::ZLIB1DLL` / `ZLIB1DLL::ZLIBWAPI`.

Control flow: Package discovery must succeed before consumer targets are created. The build then validates imported include paths and link libraries for both DLL variants.

State and persistence: Uses CMake cache state and installed package files from the private test prefix.

Dependencies and integration points: Exercises `zlib1dllConfig.cmake.in`, version files, installed exported targets, and minizip headers/sources.

Risks: Only validates configure/link, not runtime DLL loading. Version compatibility is `AnyNewerVersion` from the producer, so this test should accept newer patch-level configs but is pinned to the configured project version.

Test signals: Parent CTest runs configure and build after the install fixture.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/test/find_package_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/zlib1dllConfig.cmake.in -->
# sources/compression/zlib/contrib/zlib1-dll/zlib1dllConfig.cmake.in

Purpose: Installed package configuration template for the zlib1-dll CMake package.

Important APIs, types, and functions: Uses `@PACKAGE_INIT@`, optionally includes adjacent `ZLIB1DLLTargets.cmake`, and calls `check_required_components(ZLIB1-DLL)`.

Control flow: At package discovery time, CMake package initialization runs, targets are imported if the target file exists, and component requirements are checked.

State and persistence: Mutates the caller's package-discovery variables and imports targets into the caller's CMake target graph.

Dependencies and integration points: Generated and installed by `contrib/zlib1-dll/CMakeLists.txt`; consumed by the find-package test template and downstream projects.

Risks: The include is `OPTIONAL`, so missing target files may not fail until target use or component checks. The component name passed to `check_required_components` uses `ZLIB1-DLL`, while consumers call `find_package(ZLIB1DLL)`, which may be inconsistent with conventional package variable names.

Test signals: `zlib1-dll/test/find_package_test.cmake.in` validates that imported targets are actually available after package discovery.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/zlib1-dll/zlib1dllConfig.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/crc32.c -->
# sources/compression/zlib/crc32.c

Purpose: Implements zlib's CRC-32 calculation, table generation, hardware/braided acceleration paths, and CRC combination APIs.

Important APIs, types, and functions: Public exports are `get_crc_table()`, `crc32_z()`, `crc32()`, `crc32_combine_gen64()`, `crc32_combine_gen()`, `crc32_combine_op()`, `crc32_combine64()`, and `crc32_combine()`. Internal helpers include `byte_swap()`, `multmodp()`, `x2nmodp()`, `make_crc_table()`, `braid()`, `crc_word()`, and `crc_word_big()`. Compile-time controls include `DYNAMIC_CRC_TABLE`, `MAKECRCH`, `HAVE_S390X_VX`, `ARMCRC32`, `Z_TESTN`, `Z_TESTW`, `N`, and `W`.

Control flow: Static builds include generated `crc32.h`; dynamic builds initialize tables through `z_once(&made, make_crc_table)`. `crc32_z()` handles null-buffer initialization, preconditions the CRC, optionally uses ARM CRC32 instructions, otherwise aligns input, processes large spans with N-way braided word CRCs on little or big endian machines, finishes remaining bytes with the byte table, and postconditions the result. `crc32()` delegates to an s390x hook when enabled. Combination functions compute x^(len*8) modulo the polynomial and merge CRCs.

State and persistence: CRC tables and x-power tables are static global data, either compiled in or generated once. The dynamic-table mode uses zlib's once primitive but comments still warn callers to initialize before threaded use in some configurations. `MAKECRCH` turns the file into a generator executable that writes `crc32.h`.

Dependencies and integration points: Includes `zutil.h`, generated `crc32.h` in static-table builds, optional s390x vector hooks, and optional ARM inline assembly. This file is compiled into core zlib and the `zlib1-dll` contrib target.

Risks: Acceleration paths depend on compile-time architecture macros and unaligned/word access assumptions after explicit alignment. Negative lengths for combine generation return zero. Dynamic table generation must be correct before concurrent CRC use. Big-endian and less-common `N`/`W` combinations are more specialized and need regression coverage.

Test signals: Core zlib checks exercise known CRC values and combine behavior; `MAKECRCH` can regenerate table headers. `zlib1-dll` builds include this file, giving additional compile/link coverage for Windows DLL packaging.
<!-- END_FILE_RESEARCH: sources/compression/zlib/crc32.c -->
