# Research Report: subset-b-000295

Grouped research for the compression-related XZ test/build files and zlib build, CI, checksum, and contrib files assigned to `subset-b-000295`. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_suffix.sh -->
# sources/compression/xz/tests/test_suffix.sh

Purpose: shell regression test for `xz` suffix handling, especially raw-format compression/decompression where a suffix is required to derive output file names. It also covers stdin/stdout behavior and `--files`/`--files0` filename-list paths that previously regressed.

Important APIs/functions: uses the `xz` command-line interface with `-z`, `-d`, `-f`, `-k`, `--suffix`, `-Fraw`, `--lzma1=preset=0`, `--lzma2=preset=0`, `--files`, `--files0`, and `-c`. Exit code `77` is the skip signal expected by Automake/CMake.

Control flow: resolves the `xz` executable from argument `$1` or `../src/xz/xz`, skips if unavailable, and skips if an Autotools `config.h` says encoder or decoder support is missing. It creates a temporary input file, validates raw compression with an explicit suffix, asserts raw compression/decompression without suffix fails, validates `.xz` compression with an explicit custom suffix, checks stdin raw mode writes to stdout implicitly, exercises newline- and NUL-delimited file lists, then checks unknown file-type decompression copies to stdout only with `-c`.

State and persistence: creates and removes `suffix_temp`, `suffix_temp.foo`, `suffix_temp_files`, and `suffix_temp_files0` in the current working directory. The test assumes a scratch working directory and removes leftovers before and after the run.

Dependencies and integration: integrated by `tests.cmake` as `test_suffix.sh` on Unix builds with encoder and decoder support. It depends on a built `xz` binary, shell utilities, and optional `../config.h` feature probes.

Risks: cleanup has one duplicate entry in the early `rm -f` list and relies on no unrelated files sharing the temporary names. The CMake build has no `config.h`, so the script assumes full feature availability when invoked there; `tests.cmake` compensates by gating on CMake feature variables.

Test signals: failure messages identify the exact suffix scenario. Passing protects raw suffix errors, file-list suffix renaming, stdin raw mode, and unknown-file passthrough semantics.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_suffix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/test_vli.c -->
# sources/compression/xz/tests/test_vli.c

Purpose: C unit test for liblzma variable-length integer helpers: `lzma_vli_size()`, `lzma_vli_encode()`, and `lzma_vli_decode()`.

Important APIs/functions: uses `lzma_vli_size`, `lzma_vli_encode`, `lzma_vli_decode`, `LZMA_VLI_MAX`, `LZMA_VLI_UNKNOWN`, `LZMA_VLI_BYTES_MAX`, `LZMA_OK`, `LZMA_STREAM_END`, `LZMA_BUF_ERROR`, `LZMA_DATA_ERROR`, and `LZMA_PROG_ERROR`. Test helpers `encode_single_call_mode`, `encode_multi_call_mode`, `decode_single_call_mode`, and `decode_multi_call_mode` compare against precomputed VLI byte sequences.

Control flow: `test_lzma_vli_size` verifies invalid values return zero and that encoded length increases every seven value bits. Encode tests first verify invalid inputs do not mutate positions or output, then cover all one- through nine-byte encodings in single-call and byte-by-byte multi-call modes. Decode tests cover empty input, malformed continuation bytes, invalid positions, and the same one- through nine-byte values in single- and multi-call modes.

State and persistence: in-memory only. It uses fixed arrays of expected bytes and stack output buffers.

Dependencies and integration: includes `tests.h`, which supplies liblzma headers and `tuktest` assertions. Compile-time feature macros gate encoder and decoder tests; missing support produces skipped subtests instead of compilation failures.

Risks: the test assumes the precomputed encoded values are authoritative; an error in those constants would enshrine incorrect behavior. It does not fuzz malformed encodings beyond a few boundary cases.

Test signals: `main` registers the three test functions with `tuktest`. Failures report enum names through `assert_lzma_ret`; skip behavior reflects disabled encoders/decoders.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/test_vli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/tests.cmake -->
# sources/compression/xz/tests/tests.cmake

Purpose: optional CMake test harness for XZ Utils. It builds liblzma unit-test executables and registers command-line shell tests without letting the `tests` directory affect ordinary builds when excluded.

Important APIs/functions: uses CMake `include(CTest)`, `add_library(OBJECT)`, `add_executable`, `target_include_directories`, `target_link_libraries`, `add_test`, `set_tests_properties`, and feature variables such as `XZ_ENCODERS`, `XZ_DECODERS`, `SUPPORTED_FILTERS`, `SUPPORTED_CHECKS`, `XZ_CHECKS`, `ENABLE_SCRIPTS`, and `XZ_LZIP_DECODER`.

Control flow: when `BUILD_TESTING` is on, creates `tests_w32res` for Windows manifests, defines the `LIBLZMA_TESTS` list, conditionally appends `test_microlzma`, builds each test into `tests_bin`, and registers it with `srcdir` and skip code 77. It computes whether all encoders, decoders, and checks are enabled, then conditionally registers shell tests for scripts, suffixes, compression vectors, and file decompression.

State and persistence: emits test binaries under `${CMAKE_CURRENT_BINARY_DIR}/tests_bin` and scratch directories for shell tests. It does not persist runtime state beyond build artifacts and CTest metadata.

Dependencies and integration: depends on the main CMake build creating `liblzma`, source include directories, feature variables, and optional Windows resource dependencies. It integrates with CTest and mirrors Autotools skip semantics.

Risks: feature gating is necessarily approximate for shell scripts because CMake builds lack `config.h`. Shell tests are Unix-only. Windows manifest object generation uses a header-only dummy source and explicit linker language to satisfy CMake/Ninja.

Test signals: CTest names correspond to test programs or scripts. `SKIP_RETURN_CODE 77` is set consistently so disabled features do not become failures.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/tests.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/tests.h -->
# sources/compression/xz/tests/tests.h

Purpose: common header for XZ C test applications, wiring liblzma types into the `tuktest` assertion framework.

Important APIs/types: includes `sysdefs.h`, `tuklib_integer.h`, `lzma.h`, and `tuktest.h`. Defines `INVALID_LZMA_CHECK_ID`, `enum_strings_lzma_ret`, `assert_lzma_ret`, `enum_strings_lzma_check`, and `assert_lzma_check`.

Control flow: no runtime control flow beyond static initialization of enum-name arrays. Assertion macros delegate to `assert_enum_eq`.

State and persistence: header-local static constant arrays are compiled into each test translation unit; no persistent state.

Dependencies and integration: used by liblzma tests such as `test_vli.c`. Its enum string arrays must track the public liblzma enum ordering to keep diagnostics accurate.

Risks: if liblzma adds or reorders `lzma_ret` or `lzma_check` values, assertion diagnostics may become misleading or out of bounds. The invalid check value intentionally avoids the `LZMA_` prefix to prevent confusion with API values.

Test signals: improves failed assertion output by showing symbolic liblzma return and check names instead of raw integers.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/tests/tuktest.h -->
# sources/compression/xz/tests/tuktest.h

Purpose: standalone C99/C11 test framework for small XZ test programs. It provides test registration, pass/fail/skip/error accounting, optional TAP output, optional coloring, allocation cleanup, file-loading helpers, and assertion macros.

Important APIs/types/functions: public macros include `tuktest_start`, `tuktest_run`, `tuktest_end`, `tuktest_early_skip`, `tuktest_error`, `tuktest_malloc`, `tuktest_free`, `tuktest_file_from_srcdir`, `tuktest_file_from_builddir`, `assert_fail`, `assert_skip`, `assert_error`, `assert_true`, `assert_false`, integer, enum, bit, string, and array assertions. Internal state includes `enum tuktest_result`, `tuktest_stats`, `tuktest_argc`, `tuktest_argv`, `tuktest_name`, `tuktest_jmpenv`, and allocation-record lists.

Control flow: `tuktest_start` records `argc/argv` and prints a header. `tuktest_run_test` optionally filters by test name, sets a `setjmp` target, calls the test, and uses `longjmp` results from assertions to count fail/skip/error. Hard errors exit through `tuktest_end`. `tuktest_end` frees tracked allocations, prints TAP or summary output, checks stdout errors, and returns Automake-compatible exit status. File helpers validate names, size, emptiness, and read completeness before returning managed buffers.

State and persistence: state is process-global in static variables. `tuktest_malloc` tracks allocations separately for per-test and global lifetimes and frees them at test end or program end. File helpers read from `srcdir` or the build directory but do not write.

Dependencies and integration: depends on standard C headers and optional `PRIu64` availability. Integrated by XZ test programs through `tests.h` or direct inclusion. Exit codes are designed for Automake, Meson, and CMake with `SKIP_RETURN_CODE 77`.

Risks: assertions are only valid under `tuktest_run`; using them elsewhere is undefined by design. The framework uses global state, `setjmp`/`longjmp`, and process exit for hard errors, so it is not thread-safe and not suitable for embedding in long-lived processes. TAP mode always exits success, relying on TAP consumers for interpretation.

Test signals: produces concise per-test result lines and final totals, supports command-line selection by test function name, and reports mistyped test names as hard errors when fewer tests run than requested.
<!-- END_FILE_RESEARCH: sources/compression/xz/tests/tuktest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/windows/build.bash -->
# sources/compression/xz/windows/build.bash

Purpose: packaging script for XZ Utils Windows binary distributions using the GNU Autotools build system and MinGW-w64/MSYS toolchains.

Important APIs/functions: shell functions `buildit` and `txtcp`. `buildit` runs two configure/build cycles per architecture: a size-optimized static tool set and a normal speed-optimized `xz.exe` plus `liblzma.dll`. `txtcp` copies text files while converting LF to CRLF.

Control flow: validates working directory and required MinGW runtime license file, derives make job count, detects native MSYS builds for optional `make check`, builds i686 SSE2 and x86-64 variants if compilers are in `PATH`, optionally builds PDFs, copies headers/docs/examples into `pkg`, then uses 7-Zip if found to create `.zip` and `.7z` packages.

State and persistence: mutates the source/build tree with `make distclean`, creates `pkg/`, copies binaries/docs, strips outputs, and optionally creates `xz-<version>-windows.zip` and `.7z` at the package root.

Dependencies and integration: requires generated distribution files from `make mydist`, Autotools, MinGW-w64 GCC triplets, make, optional `ps2pdf`, optional 7-Zip, and `windows/COPYING.MinGW-w64-runtime.txt`.

Risks: `set -e` aborts on any failed command; repeated `distclean` means it should be run only in a disposable distribution tree. Whitespace detection in the current directory is conservative. If triplet-specific `windres`/`strip` are missing, it prepends the GCC directory to `PATH` to avoid mixing toolchains.

Test signals: native MSYS builds run `make check` or `make -C tests check`; cross-compilation skips runtime tests. The script ends with a success message only after packaging steps complete or optional archive creation is skipped.
<!-- END_FILE_RESEARCH: sources/compression/xz/windows/build.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.cmake-format.yaml -->
# sources/compression/zlib/.cmake-format.yaml

Purpose: repository formatting/lint configuration for `cmake-format` and its parser, formatter, markup, lint, encoding, and misc settings.

Important settings: line width 80, four-space indentation, Unix line endings, canonical command case, unchanged keyword case, sorting enabled but autosort disabled, comment markup enabled, UTF-8 input/output, and linter naming patterns for functions, macros, variables, and keywords.

Control flow: declarative YAML only; no runtime behavior. The sample `additional_commands.foo` parser entry describes flag and keyword argument shapes for custom command parsing.

State and persistence: affects formatting output when the external `cmake-format` tool is run; no state is persisted by this file itself.

Dependencies and integration: consumed by `cmake-format`/`cmake-lint`. It shapes formatting of zlib CMake files and helps CI or contributors get consistent style.

Risks: many `_help_*` entries are generated explanatory defaults, so real policy is mixed with documentation noise. If `cmake-format` changes option names or semantics, this full default-style config can drift.

Test signals: indirect; formatting/lint runs would detect CMake style violations according to these settings.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.cmake-format.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.github/workflows/c-std.yml -->
# sources/compression/zlib/.github/workflows/c-std.yml

Purpose: GitHub Actions workflow that compiles zlib across many C language standards, compilers, architectures, operating systems, and build systems with warnings treated as errors.

Important jobs: `main` covers GCC/Clang on Linux, macOS, Windows, and Windows ARM64 across configure and CMake builders and C89 through C2x/GNU2x modes. `msvc` covers MSVC CMake builds with default, C11, C17, and latest modes across supported Windows architectures.

Control flow: matrix exclusions remove unsupported combinations such as configure on Windows, 32-bit macOS, 32-bit Windows GCC, and GCC on Windows ARM64. Configure jobs run `./configure`, `make`, and `make test`; CMake jobs configure, build, and run CTest. MSVC builds both a no-test build and a build with tests/minizip.

State and persistence: CI-only build directories and installed packages; no repository state is changed. Linux 32-bit jobs install multilib packages, Windows jobs install Ninja.

Dependencies and integration: uses `actions/checkout@v6`, system compilers, Chocolatey, CMake, CTest, make, and zlib options such as `ZLIB_BUILD_TESTING` and `ZLIB_BUILD_MINIZIP`.

Risks: the matrix is large and costly. Older C modes require `-DZLIB_INSECURE` to compile code paths that use legacy prototypes. `ctest ./build` is unusual but intended to run tests for the build tree.

Test signals: strong standards-compatibility signal because `-Werror -Wall -Wextra` is applied broadly; CTest and `make test` verify runtime examples where enabled.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.github/workflows/c-std.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.github/workflows/cmake.yml -->
# sources/compression/zlib/.github/workflows/cmake.yml

Purpose: primary CMake CI workflow for zlib shared/static/package variants on Linux, macOS, and Windows.

Important jobs/settings: `ci-cmake` matrix includes GCC, Clang, MSVC Win32/Win64/ARM64, Windows GCC/Ninja, and multiple macOS GCC versions. It toggles `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, `ZLIB_BUILD_MINIZIP`, `MINIZIP_ENABLE_BZIP2`, and build type.

Control flow: installs platform packages (`nsis` on Windows, `libbz2-dev` on Linux), configures into `../build`, builds, runs CTest from that build directory, builds package targets, and uploads CMake logs on failure.

State and persistence: CI build outputs live outside the checkout in `../build`; failure artifacts retain CMake logs for seven days.

Dependencies and integration: uses `actions/checkout@v6`, CMake/CPack, NSIS, bzip2 development headers, compilers, and zlib install/package rules.

Risks: `ctest -C Release` is used even for the Debug matrix item, which can be harmless for single-config generators but is a mismatch risk. Package target names differ by generator/platform and are encoded in the matrix.

Test signals: validates CMake configure/build/test/package behavior for shared-only, static-only, optimized, debug, and minizip-enabled builds.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.github/workflows/cmake.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.github/workflows/configure.yml -->
# sources/compression/zlib/.github/workflows/configure.yml

Purpose: CI workflow for the traditional `./configure` and `Makefile.in` build path, including native, out-of-source, and cross-compiled targets.

Important jobs/settings: matrix covers Ubuntu GCC, out-of-source build, ARM soft/hard float, AArch64, PowerPC, PowerPC64, PowerPC64LE, s390x, and macOS GCC/Clang. Cross jobs set `CHOST`, cross `CC`, optional static flags, and `QEMU_RUN`.

Control flow: installs cross toolchains/QEMU as needed, creates the build directory, invokes `${src-dir}/configure --warn`, runs `make -j2`, then `make test` with optional QEMU wrappers. Uploads `configure.log` on failure.

State and persistence: writes configure/build outputs either in the checkout or `../build`. Artifact retention keeps configure diagnostics for failed jobs.

Dependencies and integration: depends on GNU make, shell configure script, cross compilers, QEMU user emulation, and zlib's `QEMU_RUN` Makefile variable.

Risks: static cross-builds depend on correct libc cross packages and QEMU paths. `chost` for PPC64 is set to `powerpc-linux-gnu` in the matrix while the compiler is `powerpc64-linux-gnu-gcc`, which deserves scrutiny if cross-prefix tools are used.

Test signals: validates the non-CMake path, large platform spread, out-of-source operation, and runtime examples under emulation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.github/workflows/configure.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.github/workflows/contribs.yml -->
# sources/compression/zlib/.github/workflows/contribs.yml

Purpose: CI workflow for zlib contributed modules, both all-at-once from the root project and standalone contrib subprojects.

Important jobs/settings: matrix builds all contribs on Ubuntu and Windows, plus standalone Ada, blast, iostream3, minizip, puff, testzlib, and zlib1-dll jobs. Root all-contrib jobs toggle options such as `ZLIB_BUILD_ADA`, `ZLIB_BUILD_BLAST`, `ZLIB_WITH_CRC32VX`, and `ZLIB_WITH_GVMAT64`.

Control flow: checks out source, installs Linux packages (`gnat`, `libbz2-dev`), optionally builds and installs root zlib before standalone contrib builds, configures the chosen source directory, builds, and runs CTest.

State and persistence: CI-local `../build-zlib` and `../build` directories; optional install into the runner system using `sudo` on Linux.

Dependencies and integration: exercises `contrib/CMakeLists.txt`, subproject `find_package(ZLIB CONFIG)` paths, GNAT Ada support, CMake install exports, and Windows-specific contrib projects.

Risks: standalone tests depend on installing zlib into a discoverable prefix, which can differ by runner permissions and CMake package cache behavior. Windows matrix values use both `windows-latest` and `Windows-latest`; GitHub is case-insensitive today but consistency would reduce risk.

Test signals: verifies contributed CMake packages can build both as root subdirectories and as standalone consumers of installed zlib.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.github/workflows/contribs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.github/workflows/fuzz.yml -->
# sources/compression/zlib/.github/workflows/fuzz.yml

Purpose: pull-request CI workflow that builds and runs zlib OSS-Fuzz fuzzers through CIFuzz.

Important APIs/actions: uses `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, `run_fuzzers@master`, and `actions/upload-artifact@v6`.

Control flow: on pull requests, builds fuzzers for OSS-Fuzz project `zlib`, runs them for 300 seconds, and uploads crash artifacts if any step fails.

State and persistence: CI-only `./out/artifacts` crash output retained as a workflow artifact on failure.

Dependencies and integration: depends on OSS-Fuzz infrastructure, zlib's external OSS-Fuzz project definition, and GitHub Actions Ubuntu runners.

Risks: actions are pinned to `master`, so upstream action changes can affect reproducibility. A 300-second fuzz window is a regression smoke test, not exhaustive fuzzing.

Test signals: detects sanitizer/fuzzer crashes triggered by current corpus and short exploratory fuzzing in pull requests.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.github/workflows/fuzz.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.github/workflows/msys-cygwin.yml -->
# sources/compression/zlib/.github/workflows/msys-cygwin.yml

Purpose: Windows CI for MSYS2 and Cygwin environments using CMake.

Important jobs/settings: `MSys` matrix covers `mingw32`, `mingw64`, `ucrt64`, `clang64`, and `clangarm64` with `clangarm64` on Windows ARM. `cygwin` uses the Cygwin install action with CMake, GCC, and Ninja packages.

Control flow: MSYS2 jobs configure with Unix Makefiles, selecting `CC=clang` for clang64, then build and run CTest. Cygwin configures from the checkout path using Ninja, builds with `-j1`, and runs CTest.

State and persistence: build directories under the CI workspace; no repository modifications.

Dependencies and integration: uses `msys2/setup-msys2@v2`, `cygwin/cygwin-install-action@master`, CMake, make/Ninja, pacboy toolchains, and minizip options.

Risks: Cygwin action is pinned to `master`; fixed checkout path `/cygdrive/d/a/zlib/zlib` assumes GitHub workspace layout. `MINIZIP_ENABLE_BZIP2` is disabled for Cygwin, reducing coverage there.

Test signals: validates Unix-like Windows toolchains, DLL lookup behavior, minizip builds, and CTest execution under MSYS/Cygwin shells.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.github/workflows/msys-cygwin.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/.github/workflows/others.yml -->
# sources/compression/zlib/.github/workflows/others.yml

Purpose: CI workflow for less common operating systems through VM-based GitHub Actions.

Important jobs/settings: covers DragonFlyBSD, FreeBSD aarch64/x86_64, NetBSD aarch64/x86_64, OmniOS, OpenBSD aarch64/x86_64/riscv64, and Solaris. OpenIndiana is present but commented out.

Control flow: each VM job checks out source, installs CMake and bzip2 or equivalent packages, configures zlib with minizip and bzip2 enabled where supported, builds, and runs CTest. FreeBSD excludes tests matching `.*summary`.

State and persistence: VM-local build directories only; `copyback: false` avoids syncing generated files back.

Dependencies and integration: uses `vmactions/*-vm` actions, platform package managers, CMake, and CTest. Exercises portability of root CMake and minizip paths.

Risks: VM actions and package repositories are external moving parts. Some jobs run `ctest` without `--output-on-failure`, reducing diagnostic detail. OpenBSD prepare contains a bare `bzip2` line after `pkg_add cmake`, which may be intentional command availability check or a typo.

Test signals: broad OS portability signal for configure-free CMake builds, especially non-Linux Unix variants.
<!-- END_FILE_RESEARCH: sources/compression/zlib/.github/workflows/others.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/BUILD.bazel -->
# sources/compression/zlib/BUILD.bazel

Purpose: Bazel build definition for zlib, adapted from Bazel Central Registry and protobuf third-party packaging.

Important APIs/targets: loads `cc_library` and `license`; defines `:license`, `copy_public_headers` genrule, `mingw_gcc_compiler` config setting, public `cc_library(name = "z")`, and alias `:zlib`.

Control flow: `_ZLIB_HEADERS` enumerates internal/public headers. `copy_public_headers` copies headers into `zlib/include/` so `includes` propagation is contained. `cc_library :z` compiles core zlib sources and includes unprefixed headers in `srcs` to handle mixed quote/angle includes. `copts` vary for MinGW, Windows, and default platforms.

State and persistence: Bazel-generated header copies live under the genrule output tree, not the source tree. No runtime persistence.

Dependencies and integration: depends on `rules_cc`, `rules_license`, and `platforms` declared in `MODULE.bazel`. Exposes a public Bazel target for downstream users.

Risks: suppresses several compiler diagnostics on default platforms, which may hide issues outside CI. Header copying command assumes output directory layout exists as Bazel creates it. Source list must stay synchronized with zlib core files.

Test signals: no tests are defined here; build success validates compilation only.
<!-- END_FILE_RESEARCH: sources/compression/zlib/BUILD.bazel -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/CMakeLists.txt -->
# sources/compression/zlib/CMakeLists.txt

Purpose: primary CMake build, install, package, and test entry point for zlib.

Important APIs/options: project `zlib` version `1.3.2.1`; options `ZLIB_BUILD_TESTING`, `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, `ZLIB_INSTALL`, and `ZLIB_PREFIX`. Uses feature checks for `off64_t`, `fseeko`, `stdarg.h`, `unistd.h`, and hidden visibility. Exports targets `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC`.

Control flow: sets a default Release build for single-config generators, generates a CMake-specific `zconf.h.cmakein` from `zconf.h`, runs platform feature checks, configures `zlib.pc` and `zconf.h`, declares source/header lists, builds shared and/or static libraries, sets platform-specific names/version scripts, installs exports/config files/headers/docs/pkg-config metadata, enables tests, and always enters `contrib`.

State and persistence: writes generated `zconf.h.cmakein`, `zconf.h`, `zlib.pc`, CMake package config files, build artifacts, install tree content, and CPack metadata.

Dependencies and integration: integrates with CMakePackageConfigHelpers, CPack, GNUInstallDirs, the `test` subdirectory, and all contrib option dispatch. Consumers use installed `ZLIBConfig.cmake` or pkg-config.

Risks: the `zconf.h` generation uses fixed read offsets from the source header, so upstream header layout changes can break generated content. Version-script linking excludes AIX and SunOS but may need maintenance for more Unix variants. Building contrib unconditionally delegates option checks to `contrib/CMakeLists.txt`.

Test signals: `ZLIB_BUILD_TESTING` enables the `test` subdirectory; CI workflows also validate packaging, install exports, shared/static variants, and minizip integration.
<!-- END_FILE_RESEARCH: sources/compression/zlib/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/MODULE.bazel -->
# sources/compression/zlib/MODULE.bazel

Purpose: Bazel module metadata for the zlib package.

Important APIs/settings: declares `module(name = "zlib", version = "0.0.0", compatibility_level = 1)` and `bazel_dep` entries for `platforms`, `rules_cc`, and `rules_license`.

Control flow: declarative Bzlmod configuration only; Bazel resolves dependencies before loading `BUILD.bazel`.

State and persistence: affects Bazel external dependency resolution; no source-tree mutation.

Dependencies and integration: paired with `BUILD.bazel` to make the package buildable under Bazel/Bzlmod.

Risks: version `0.0.0` is a placeholder, so consumers relying on module version semantics may need registry-provided metadata instead. Dependency versions must remain compatible with the BUILD file APIs.

Test signals: Bazel module resolution and `:z` build success are the main signals.
<!-- END_FILE_RESEARCH: sources/compression/zlib/MODULE.bazel -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/Makefile -->
# sources/compression/zlib/Makefile

Purpose: placeholder Makefile used before `./configure` generates the real build Makefile.

Important targets: `all` prints “Please use ./configure first. Thank you.”; `distclean` delegates to `make -f Makefile.in distclean`.

Control flow: intentionally prevents accidental use of unconfigured make rules while still allowing cleanup through the template Makefile.

State and persistence: `distclean` may regenerate this placeholder after removing configured outputs.

Dependencies and integration: used by the traditional configure flow; overwritten by `configure` from `Makefile.in`.

Risks: users running `make` without configuring receive only a message, not a build. The `distclean` target depends on `Makefile.in` being present.

Test signals: none beyond basic command behavior.
<!-- END_FILE_RESEARCH: sources/compression/zlib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/Makefile.in -->
# sources/compression/zlib/Makefile.in

Purpose: template Makefile for zlib's traditional configure/make build, tests, install, coverage, and cleanup.

Important targets/variables: variables for compiler, flags, library names, install prefixes, object lists, PIC objects, QEMU runner, and s390x vector flags. Targets include `all`, `static`, `shared`, `test`, `teststatic`, `testshared`, `test64`, `cover`, `libz.a`, shared library, examples, install/uninstall, docs, zconf, minizip-test, clean, distclean, and tags.

Control flow: `configure` rewrites variables and target prerequisites. Static builds create `libz.a`, `example`, and `minigzip`; shared builds create versioned shared library symlinks plus shared examples. Tests pipe “hello world” through minigzip and run example programs, optionally via `QEMU_RUN`. Install copies libraries, symlinks, man page, pkg-config file, and headers under `DESTDIR`.

State and persistence: creates object files, PIC `.lo` files, `objs/`, libraries, symlinks, examples, coverage files, docs, installed files, and generated placeholder Makefile on `distclean`.

Dependencies and integration: driven by `configure`, uses core zlib sources, optional `contrib/crc32vx`, test sources, `zlib.map`, `zlib.pc`, system `ar`, `ranlib`, `ldconfig`, `tar`, `groff`, `ps2pdf`, and shell utilities.

Risks: manual dependency lists must stay synchronized with source headers. Shared library symlink handling assumes Unix-like semantics. Test temporary cleanup uses shell PID suffixes and can leave files after interrupted runs. `LLVM_GCOV_FLAG` default has a spelling placeholder that configure is expected to replace for coverage.

Test signals: `make test`, `make test64`, minigzip pipe tests, example programs, and `cover`/`infcover` provide runtime and coverage signals for the configure path.
<!-- END_FILE_RESEARCH: sources/compression/zlib/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/adler32.c -->
# sources/compression/zlib/adler32.c

Purpose: implements Adler-32 checksum calculation and checksum combination for zlib streams.

Important APIs/functions: exports `adler32_z`, `adler32`, `adler32_combine`, and `adler32_combine64`; internal `adler32_combine_`. Uses constants `BASE` 65521 and `NMAX` 5552 plus unrolled macros `DO1` through `DO16` and modulo macros that can avoid division under `NO_DIVIDE`.

Control flow: `adler32_z` splits the incoming checksum into low/high sums, fast-paths one-byte inputs, returns initial checksum `1` for `Z_NULL`, handles short buffers, processes long buffers in `NMAX` chunks with unrolled 16-byte loops, then recombines sums. Combine functions validate `len2`, reduce it modulo `BASE`, and apply the Adler concatenation formula.

State and persistence: stateless; all work is local to each call.

Dependencies and integration: includes `zutil.h` for zlib types/macros. Called by public zlib checksum APIs and used by compression/decompression consumers needing stream integrity.

Risks: performance and correctness depend on avoiding 32-bit overflow via `NMAX` and modulo scheduling. `buf == Z_NULL` is checked after the `len == 1` fast path, so callers must not pass null with length one. Negative combine lengths return `0xffffffffUL` as a debugging clue, not a normal error code.

Test signals: covered indirectly by zlib example tests, checksum tests elsewhere, and broad CI standard/platform builds.
<!-- END_FILE_RESEARCH: sources/compression/zlib/adler32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/compress.c -->
# sources/compression/zlib/compress.c

Purpose: implements convenience APIs for compressing an entire memory buffer and computing a conservative compression bound.

Important APIs/functions: exports `compress2_z`, `compress2`, `compress_z`, `compress`, `compressBound_z`, and `compressBound`. Uses `z_stream`, `deflateInit`, `deflate`, and `deflateEnd`.

Control flow: `compress2_z` validates pointer/length combinations, zeroes the destination length, initializes deflate with the requested level, feeds input and output in chunks no larger than `uInt` max, loops until `deflate` stops returning `Z_OK`, finalizes the stream, and maps `Z_STREAM_END` to `Z_OK`. Wrapper functions adapt `uLong`/`uLongf` arguments and default compression level. `compressBound_z` computes the documented upper bound and returns `(z_size_t)-1` on overflow.

State and persistence: stack-local stream state only; output is written into caller-provided memory and `*destLen` is updated.

Dependencies and integration: includes `zlib.h` with `ZLIB_INTERNAL`. This is the simple-buffer API layered on the streaming deflate implementation in `deflate.c`.

Risks: callers must provide a large enough destination buffer or receive `Z_BUF_ERROR`. `compress2` casts `z_size_t` back to `uLong`, so very large sizes are constrained by the legacy API width. Pointer validation permits zero-length null buffers but rejects nonzero lengths with null pointers.

Test signals: exercised by zlib examples, minigzip-related tests indirectly, and C standard CI across many compilers.
<!-- END_FILE_RESEARCH: sources/compression/zlib/compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/configure -->
# sources/compression/zlib/configure

Purpose: portable shell configure script for the traditional zlib make build. It detects compilers, platform linker flags, library naming, feature macros, optional sanitizer/coverage settings, and s390x vector CRC support, then generates `Makefile`, `zlib.pc`, and `zconf.h`.

Important functions/variables: shell helpers `leave`, `show`, `try`, and `tryboth`; command-line options such as `--prefix`, `--static`, `--shared`, `--solo`, `--cover`, `--zprefix`, `--64`, `--archs`, `--const`, `--warn`, sanitizer flags, `--insecure`, and `--disable-crcvx`. Key outputs include `CC`, `CFLAGS`, `SFLAGS`, `LDSHARED`, `SHAREDLIB*`, `OBJC`, `PIC_OBJC`, `VGFMAFLAG`, `ALL`, and `TEST`.

Control flow: logs invocation to `configure.log`, determines source directory and cross-prefix from `CHOST`, parses options, detects GCC/Clang, assembles flags by platform, probes shared-library support, checks `size_t`, large-file support, `fseeko`, `strerror`, `unistd.h`, `stdarg.h`, printf variants, hidden visibility, s390x, and s390x VX intrinsics. It edits `zconf.h`, substitutes variables into `Makefile.in` and `zlib.pc.in`, and cleans temporary probes through `leave`.

State and persistence: appends `configure.log`; writes `zconf.h`, `Makefile`, and `zlib.pc`; creates temporary `ztest$$` files removed on exit.

Dependencies and integration: pairs with `Makefile.in`, `zconf.h.in`, `zlib.pc.in`, system shell tools, C compiler, archiver, ranlib, nm, and optional cross tools. CI `configure.yml` exercises this path extensively.

Risks: shell substitution writes unescaped user-provided paths/flags into sed replacements, so unusual characters can break generation. Cross builds cannot run probe executables for some checks. Security-related printf fallback requires `--insecure` but the script records warnings rather than universally aborting.

Test signals: generated `make test`, `make test64`, configure CI cross-builds, and `configure.log` probe output provide diagnostics.
<!-- END_FILE_RESEARCH: sources/compression/zlib/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/CMakeLists.txt -->
# sources/compression/zlib/contrib/CMakeLists.txt

Purpose: option dispatcher for zlib contrib features and sub-libraries in the root CMake build.

Important APIs/functions: defines `zlib_add_contrib_lib(name description dir)` and `zlib_add_contrib_feature(name description dir [default])`. Sets `WORK_DIR`, `ZLIB_CONTRIB_PREFIX`, and `inst_setup`, then declares feature/library options for GVMAT64, INFBACK9, CRC32VX, ADA, BLAST, IOSTREAM3, MINIZIP, PUFF, TESTZLIB, and ZLIB1_DLL.

Control flow: contrib libraries inherit root shared/static/testing/install options unless explicitly set, then add their subdirectory only when enabled. Feature toggles add subdirectories directly. Windows-only blocks expose testzlib and legacy zlib1-dll support.

State and persistence: CMake cache options control which contrib directories participate in the build.

Dependencies and integration: included unconditionally by root `CMakeLists.txt`; delegates to each contrib subproject. CRC32VX can modify root zlib targets by adding source files.

Risks: `ZLIB_BUILD_ZLIB1_DLL` is checked before its `option()` declaration, so the first configure relies on an externally supplied value or defaults to no subdirectory until reconfigure. Global `WORK_DIR`/prefix variables are shared by subprojects.

Test signals: `contribs.yml` validates all-contrib and standalone contrib configurations.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/CMakeLists.txt -->
# sources/compression/zlib/contrib/ada/CMakeLists.txt

Purpose: CMake build for zlib Ada bindings and stream wrappers.

Important APIs/options: project `zlibAda` with languages C and ADA; options `ZLIB_ADA_BUILD_SHARED`, `ZLIB_ADA_BUILD_STATIC`, and `ZLIB_ADA_BUILD_TESTING`. Uses custom `ada_add_library`, `ada_find_ali`, and `find_package(ZLIB COMPONENTS shared/static CONFIG)` when standalone.

Control flow: when built from the root, inherits zlib shared/static/testing/install options. Standalone builds require installed ZLIB components matching requested library kinds. Shared and static paths build `zlib_ada_Ada`/`zlib_ada_AdaStatic` from `zlib-thin.adb` and `zlib.adb`, then stream libraries from `zlib-streams.adb`, linking to the corresponding zlib target. Tests are added when enabled.

State and persistence: creates Ada object and ALI files plus CMake targets; additional clean files are configured by the custom Ada language support.

Dependencies and integration: relies on custom Ada CMake modules in `cmake/Modules`, GNAT, and zlib CMake package targets. Integrated by root contrib options and standalone contrib CI.

Risks: custom Ada support is GNAT-oriented and may not support other Ada compilers. Link interfaces use `INTERFACE` for base Ada-to-zlib linkage, which affects consumers rather than necessarily the library link line in all contexts.

Test signals: `contrib/ada/test/CMakeLists.txt` builds demos/tests for shared and static variants; `contribs.yml` installs GNAT and runs them on Ubuntu.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADACompiler.cmake.in -->
# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADACompiler.cmake.in

Purpose: generated CMake platform-info template for the custom ADA language.

Important variables: sets `CMAKE_ADA_COMPILER`, compiler args/id/version/platform, `CMAKE_AR`, compiler loaded/work flags, source and ignored extensions, environment variable name `ADA`, and paths to binder/compiler/link helper scripts.

Control flow: no logic beyond variable assignment. `CMakeDetermineADACompiler.cmake` configures this template into `CMakeADACompiler.cmake` under CMake's platform information directory.

State and persistence: generated output persists in the CMake build tree and tells subsequent configure/generate steps how to invoke Ada tools.

Dependencies and integration: included by CMake's language enablement flow for the custom `ADA` language.

Risks: commented-out ranlib/linker/ABI variables mean this language definition is intentionally minimal. If helper script paths move, configured builds fail until regenerated.

Test signals: successful `project(... LANGUAGES C ADA)` and `try_compile` in `CMakeTestADACompiler.cmake` validate that the generated file is usable.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADACompiler.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADAInformation.cmake -->
# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADAInformation.cmake

Purpose: CMake language information module defining compile, bind, link, static archive, and helper functions for Ada targets.

Important APIs/functions: sets Ada output extension and per-config flags; defines `CMAKE_ADA_CREATE_SHARED_LIBRARY`, `CMAKE_ADA_CREATE_STATIC_LIBRARY`, `CMAKE_ADA_COMPILE_OBJECT`, and `CMAKE_ADA_LINK_EXECUTABLE`; exposes `ada_add_executable`, `ada_add_library`, and `ada_find_ali`.

Control flow: initializes language flags from `ADAFLAGS`, applies optional user rule overrides, configures standard libraries and launchers, installs custom rule commands that call helper scripts, and wraps normal CMake targets to add ALI cleanup files and `-aO` link options.

State and persistence: modifies CMake target properties including `ADDITIONAL_CLEAN_FILES`, `ALI_FLAG`, `LINK_FLAGS`, and link options. Generated Ada binder artifacts are marked for cleanup.

Dependencies and integration: depends on CMake internal modules `CMakeLanguageInformation`, `CMakeCommonLanguageInclude`, and helper scripts in `contrib/ada/cmake`.

Risks: function loops use argument ranges and source-name string replacement that assume `.adb` source paths and simple names. Target `LINK_FLAGS` assembly from linked libraries can be fragile for transitive dependencies.

Test signals: Ada contrib builds and tests exercise compile/link rules for shared/static libraries and executables.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADAInformation.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeDetermineADACompiler.cmake -->
# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeDetermineADACompiler.cmake

Purpose: custom CMake compiler-detection module for the Ada language.

Important APIs/variables: includes `CMakeDetermineCompiler.cmake`, optional platform Ada modules, `CMAKE_ADA_COMPILER_NAMES`, `_cmake_find_compiler`, `_cmake_find_compiler_path`, `CMAKE_ADA_COMPILER_ID`, and helper script path variables.

Control flow: seeds compiler names with `gnat` and `gnat-11` through `gnat-99` if none are provided, finds the compiler or compiler path, marks it advanced, assumes GNU identity, sets helper script commands using `${CMAKE_COMMAND} -P`, and configures `CMakeADACompiler.cmake.in`.

State and persistence: writes CMake platform info for Ada into the build tree and stores compiler cache entries.

Dependencies and integration: invoked by CMake when enabling `LANGUAGES ADA` in the Ada project. Assumes GNAT-style command interface.

Risks: compiler ID is hard-coded to `GNU`; non-GNAT Ada compilers are effectively unsupported. Helper script paths use `CMAKE_CURRENT_SOURCE_DIR`, so standalone/root inclusion must preserve expected layout.

Test signals: followed by `CMakeTestADACompiler.cmake`, which performs a simple compile test.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeDetermineADACompiler.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeTestADACompiler.cmake -->
# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeTestADACompiler.cmake

Purpose: CMake language test module that verifies the configured Ada compiler can build a simple program.

Important APIs/functions: uses `include(CMakeTestCompilerCommon)`, `PrintTestCompilerStatus`, `file(WRITE)`, `try_compile`, `CMakeError.log`, and `CMakeOutput.log`.

Control flow: clears cached `CMAKE_ADA_COMPILER_WORKS`, writes `main.adb` that prints “Hello, World!”, runs `try_compile`, then either logs failure and raises `FATAL_ERROR` or logs success.

State and persistence: writes temporary source under `CMakeFiles/CMakeTmp` and appends compiler output to CMake logs.

Dependencies and integration: called during Ada language enablement after compiler detection. Relies on custom Ada compile/link rules from the language modules.

Risks: a compiler that can compile but not run is sufficient because `try_compile` only builds; runtime Ada library discovery issues may still appear later. Error text says CMake cannot generate the project on failure, which is accurate for Ada targets.

Test signals: first-line configure gate for Ada contrib; failing it blocks all Ada builds.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/Modules/CMakeTestADACompiler.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/binder_helper.cmake -->
# sources/compression/zlib/contrib/ada/cmake/binder_helper.cmake

Purpose: CMake script wrapper around GNAT binding for Ada object/ALI files.

Important inputs: expects `CMAKE_ARGV3` as binder/compiler command and `CMAKE_ARGV4` as an object path convertible to `.ali`. Parses later arguments after `FLAGS` while ignoring `-O` output flags.

Control flow: derives the ALI filename and search path, appends `-aO<search_path>`, attempts `gnat bind`, retries with `bind -n` if no main function is present, fails on binder errors, and touches the original object path for CMake dependency satisfaction.

State and persistence: creates or updates binder artifacts through GNAT and touches the target object path.

Dependencies and integration: used by `CMAKE_ADA_CREATE_SHARED_LIBRARY` and `CMAKE_ADA_LINK_EXECUTABLE` rules.

Risks: argument parsing is positional and assumes CMake command templates. `RESULT` is only set on the retry path; if the first bind succeeds, the later `if(RESULT)` relies on unset variable behavior.

Test signals: Ada executable/library link steps fail early if binding cannot resolve ALI files or main/no-main mode.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/binder_helper.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/compile_helper.cmake -->
# sources/compression/zlib/contrib/ada/cmake/compile_helper.cmake

Purpose: CMake script wrapper around GNAT Ada compilation.

Important inputs: expects compiler in `CMAKE_ARGV3`, object directory in `CMAKE_ARGV4`, source file in `CMAKE_ARGV5`, and remaining arguments as flags.

Control flow: validates required arguments, collects flags, executes `${compiler} compile <flags> <source>` in the object directory, and fails the CMake step on nonzero result.

State and persistence: writes Ada object and ALI files into the object directory via GNAT.

Dependencies and integration: used by `CMAKE_ADA_COMPILE_OBJECT` in `CMakeADAInformation.cmake`.

Risks: assumes GNAT command syntax (`gnat compile`). Output is discarded except error text, which can reduce diagnostics.

Test signals: every Ada source compilation uses this wrapper; CMake build failure indicates compiler or flags problems.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/compile_helper.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/exe_link_helper.cmake -->
# sources/compression/zlib/contrib/ada/cmake/exe_link_helper.cmake

Purpose: CMake script wrapper around GNAT executable linking.

Important inputs: linker/compiler in `CMAKE_ARGV3`, output in `CMAKE_ARGV4`, `OBJ` and `LIBS` sentinels separating object and library arguments.

Control flow: scans arguments to find the first object, converts it to an ALI path, collects non-ALI flags and libraries, then runs `${linker} link <ali> -o <output> <flags> <objects> <libs>`.

State and persistence: produces the Ada executable target.

Dependencies and integration: used by `CMAKE_ADA_LINK_EXECUTABLE`.

Risks: `OTHER_OBJECTS` is referenced but not populated in the script, so extra non-main objects may be omitted unless GNAT resolves them from ALI metadata. The first-object-to-ALI heuristic assumes object ordering has the main unit first.

Test signals: Ada test/demos link through this helper, exposing argument parsing or library lookup failures.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/exe_link_helper.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/shared_link_helper.cmake -->
# sources/compression/zlib/contrib/ada/cmake/shared_link_helper.cmake

Purpose: CMake script wrapper that creates an Ada shared library using GNAT.

Important inputs: linker/compiler in `CMAKE_ARGV3`, output library in `CMAKE_ARGV4`, object files before the `LIBS` sentinel, and libraries after it.

Control flow: parses object and library arguments, writes a dummy Ada procedure `dummylib.adb`, compiles and binds it with no main, then links a shared library from `dummylib.ali`, collected object files, and libraries.

State and persistence: creates `dummylib.adb`, `dummylib.ali`, `dummylib.o`, and the shared library; cleanup files are registered by `ada_add_library`.

Dependencies and integration: used by `CMAKE_ADA_CREATE_SHARED_LIBRARY`.

Risks: the parser sets `REACHED_FILES` but checks `REACHED_LIBS`, so library collection appears broken unless CMake argument behavior masks it. Intermediate dummy files are written in the current build directory and can conflict if parallel targets share it.

Test signals: shared Ada library builds and downstream tests reveal link failures.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/shared_link_helper.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/static_link_helper.cmake -->
# sources/compression/zlib/contrib/ada/cmake/static_link_helper.cmake

Purpose: CMake script wrapper for creating Ada static libraries.

Important inputs: archiver path in `CMAKE_ARGV3`, output archive in `CMAKE_ARGV4`, and object files in subsequent arguments.

Control flow: validates the archiver, collects object file arguments except the final CMake sentinel, then runs `${ar} rcs <archive> <objects>`.

State and persistence: writes the static archive target.

Dependencies and integration: used by `CMAKE_ADA_CREATE_STATIC_LIBRARY`; typically receives `CMAKE_AR`.

Risks: the `foreach` starts at range 5 but also has a second range expression ending at `CMAKE_ARGC`; positional mistakes can omit or include unintended arguments. Error message says “linker not set” although the tool is an archiver.

Test signals: static Ada target and static Ada tests link against archives produced here.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/cmake/static_link_helper.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/ada/test/CMakeLists.txt -->
# sources/compression/zlib/contrib/ada/test/CMakeLists.txt

Purpose: CTest definitions for zlib Ada binding examples and tests.

Important APIs/functions: defines `ZLIB_ADA_findTestEnv` to add the zlib DLL directory to `PATH` on Windows-like environments. Uses `ada_add_executable`, `target_link_libraries`, `ada_find_ali`, `add_test`, fixtures, and resource locks.

Control flow: for shared builds, creates and tests `zlib_ada_test`, `zlib_ada_buffer_demo`, and `zlib_ada_read`; builds but does not test `mtest` because it is an endless loop. Static builds create analogous `*Static` targets/tests. A cleanup test removes `testzlib.in`, `.out`, and `.zlb` as fixture cleanup.

State and persistence: test programs create temporary test files in the binary directory; cleanup removes them. CTest resource locks serialize tests using shared Ada test files.

Dependencies and integration: links against Ada binding targets and zlib targets. Windows-like shared tests need PATH updates for DLL discovery.

Risks: function name is defined with uppercase segments but called as lowercase in some places; CMake commands are case-insensitive, so this works. One shared test calls `zlib_ada_findtestenv(zlib_ada_ada-test)`, which does not match the registered `zlib_ada_test` test name and may fail to set the intended environment.

Test signals: validates shared/static Ada APIs, stream wrappers, demos, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/ada/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/CMakeLists.txt -->
# sources/compression/zlib/contrib/blast/CMakeLists.txt

Purpose: CMake build/install/package entry for the `blast` PKWare DCL decompression library.

Important APIs/options: project `blast` version `1.3.0`; options `ZLIB_BLAST_BUILD_SHARED`, `ZLIB_BLAST_BUILD_STATIC`, `ZLIB_BLAST_BUILD_TESTING`, and `ZLIB_BLAST_INSTALL`. Exports aliases `BLAST::BLAST` and `BLAST::BLASTSTATIC`.

Control flow: inherits root zlib contrib defaults when built from root, sets Windows static suffix and export-all behavior, builds shared and/or static libraries from `blast.c`/`blast.h`, adds tests when enabled, and installs targets, CMake package files, version files, and `blast.h`.

State and persistence: creates library artifacts, CMake export files, install tree entries, and configured package config files.

Dependencies and integration: uses GNUInstallDirs and CMakePackageConfigHelpers. The test subdirectory validates package consumption through `find_package` and `add_subdirectory`.

Risks: project description says “creating zipfiles based in zlib,” which does not match blast's decompression role. Shared install rules omit an explicit `LIBRARY DESTINATION`, relying on platform behavior.

Test signals: `contrib/blast/test/CMakeLists.txt` builds shared/static test executables and package-consumer fixtures.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/Makefile -->
# sources/compression/zlib/contrib/blast/Makefile

Purpose: minimal standalone make build and test for the blast library.

Important targets: `libblast.so`, `blast-test`, `test`, `clean`, and default `all: test`.

Control flow: compiles `blast.c` into a shared library, builds `blast-test` against it, runs `blast-test < test.pk | cmp - test.txt` with `LD_LIBRARY_PATH=./`, and removes generated files on clean.

State and persistence: writes `libblast.so`, `blast-test.o`, and `blast-test`.

Dependencies and integration: uses system `cc`, `cmp`, shell redirection, and test fixtures `test.pk`/`test.txt`.

Risks: Unix/Linux oriented; no portability flags, install rules, or static build. Runtime loader setup is hard-coded to `LD_LIBRARY_PATH`.

Test signals: exact decompressed output comparison against `test.txt`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blast-test.c -->
# sources/compression/zlib/contrib/blast/blast-test.c

Purpose: command-line example/test program for the `blast()` decompressor.

Important functions: `inf` reads up to `CHUNK` bytes from a `FILE *` into a static buffer; `outf` writes a buffer to a `FILE *`; `main` invokes `blast(inf, stdin, outf, stdout, &left, NULL)`.

Control flow: decompresses stdin to stdout, reports nonzero blast errors to stderr, drains any leftover input bytes to count unused data, reports a warning if leftovers exist, and returns the blast error code.

State and persistence: uses a static input buffer and standard streams only; no files are opened directly.

Dependencies and integration: includes `blast.h` and standard I/O. Used by the Makefile and CMake tests with `test.pk` and `test.txt`.

Risks: static input buffer makes `inf` non-reentrant. The program is intended as a single-stream filter and does not set binary mode on Windows by itself.

Test signals: nonzero process exit indicates decompressor error; output comparison in tests verifies decompressed bytes.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blast-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blast.c -->
# sources/compression/zlib/contrib/blast/blast.c

Purpose: streaming decompressor for the PKWare Data Compression Library format, implementing functionality similar to PKWare `explode()`.

Important APIs/types/functions: public `blast(blast_in, void *, blast_out, void *, unsigned *, unsigned char **)`; internal `struct state`, `bits`, `struct huffman`, `decode`, `construct`, and `decomp`. Constants include `MAXBITS` 13 and `MAXWIN` 4096.

Control flow: `blast` initializes input/output state, optionally consumes caller-provided leftover input, uses `setjmp` to convert input exhaustion from `bits`/`decode` into error code `2`, calls `decomp`, returns unused input pointers, and flushes pending output. `decomp` constructs static Huffman tables once, reads literal/dictionary header bytes, then loops over literal or length/distance items until end code. It validates literal flag, dictionary size, and early distances, maintains a 4 KiB sliding output window, and calls the output callback whenever the window fills.

State and persistence: per-call state is stack-local except for static Huffman tables and a static `virgin` initialization flag. Output persistence is entirely through caller callbacks.

Dependencies and integration: includes `blast.h`, `stddef.h`, and `setjmp.h`. Consumed by blast tests, CMake package targets, and any application needing PKWare DCL decompression.

Risks: static table initialization is not thread-safe on first concurrent use. `longjmp`-based input exhaustion bypasses normal local unwinding. Callback contracts must be honored exactly; returning zero bytes from input is an input error and nonzero output callback result is output error. The decompressor assumes trusted enough callback pointers and buffer lifetimes.

Test signals: `blast-test` validates a known compressed fixture; package tests validate the library target can be consumed in multiple CMake modes.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blast.h -->
# sources/compression/zlib/contrib/blast/blast.h

Purpose: public interface and documentation for the blast PKWare DCL decompressor.

Important APIs/types: defines `local` as `static`, callback types `blast_in` and `blast_out`, and the `blast()` prototype with leftover-input reporting through `left` and `in`.

Control flow: declarative header; comments define callback invocation and return-code semantics. Input callback provides bytes on demand; output callback receives chunks no larger than 4096 bytes.

State and persistence: no header state. Applications pass opaque `inhow` and `outhow` handles for their own state.

Dependencies and integration: included by `blast.c`, `blast-test.c`, and downstream users. Warns callers to use binary mode for stdio streams to avoid data corruption.

Risks: the global `local` macro can conflict if included in source that already uses that identifier. The API uses raw pointers and callback contracts without size types wider than `unsigned`.

Test signals: return codes documented here are asserted indirectly through `blast-test` process exit and output comparison.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blastConfig.cmake.in -->
# sources/compression/zlib/contrib/blast/blastConfig.cmake.in

Purpose: installed CMake package configuration template for `find_package(blast CONFIG)`.

Important variables/control: `_blast_supported_components` contains `shared` and `static`. Requested `blast_FIND_COMPONENTS` drive optional inclusion of `blast-<component>.cmake`; no-components mode includes both component exports and requires both targets to exist.

Control flow: for each requested component, rejects unsupported names, includes the component export file, and sets `blast_<component>_FOUND`. Without components, attempts to include both exports and marks package not found if either `BLAST::BLAST` or `BLAST::BLASTSTATIC` is missing.

State and persistence: executed during downstream CMake configure; sets `blast_FOUND`, `blast_NOT_FOUND_MESSAGE`, and component variables.

Dependencies and integration: generated and installed by blast CMakeLists. Tested by package consumer templates under `contrib/blast/test`.

Risks: no-components mode requires both shared and static targets, which can surprise consumers of shared-only or static-only installs. Error messages mention `ZLIB::ZLIB` target names, likely copy/paste from zlib and misleading for blast.

Test signals: `find_package_no_components` and `find_package_wrong_components` tests intentionally cover success/failure behavior.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/blastConfig.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/CMakeLists.txt -->
# sources/compression/zlib/contrib/blast/test/CMakeLists.txt

Purpose: CTest harness for blast runtime tests and CMake package-consumption scenarios.

Important APIs/functions: defines `blast_findTestEnv`, configures five CMake consumer templates, and registers configure/build tests for `find_package`, `add_subdirectory`, `EXCLUDE_FROM_ALL`, no-components, and wrong-components cases.

Control flow: if install testing is enabled and the project is standalone, first installs blast into a test prefix. It configures consumer projects into `WORK_DIR`, runs CMake configure/build tests with the active generator/compiler/platform, marks fixture dependencies, and sets expected failure for wrong components and no-components when not both library kinds are built. It also builds shared/static `blast-test` executables and runs them through `tester.cmake`.

State and persistence: creates multiple test source and build directories under `WORK_DIR`, optional `test_install`, and transient `output.txt` from runtime tests.

Dependencies and integration: relies on `BLAST::BLAST`/`BLAST::BLASTSTATIC` targets, installed package exports, CTest fixtures, and CMake generator expressions. Windows-like shared tests get PATH updated for DLL lookup.

Risks: tests are complex and generator-sensitive; passing `-DCMAKE_BUILD_TYPE=$<CONFIG>` to single-config generators can produce odd values under some CTest contexts. Environment function casing is inconsistent but CMake tolerates command names case-insensitively.

Test signals: validates runtime decompression, standalone install exports, component selection, add_subdirectory use, and expected package failure paths.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/add_subdirectory_exclude_test.cmake.in -->
# sources/compression/zlib/contrib/blast/test/add_subdirectory_exclude_test.cmake.in

Purpose: generated consumer project that verifies blast can be added by `add_subdirectory(... EXCLUDE_FROM_ALL)`.

Important APIs/settings: options mirror `ZLIB_BLAST_BUILD_SHARED`, `ZLIB_BLAST_BUILD_STATIC`, and `ZLIB_BLAST_BUILD_TESTING`; links test executables to `BLAST::BLAST` and/or `BLAST::BLASTSTATIC`.

Control flow: adds the blast source directory into a local binary dir excluded from the default all target, then creates explicit executables from `blast-test.c` for enabled library kinds.

State and persistence: generated into the test work directory and produces consumer build artifacts.

Dependencies and integration: configured by blast test CMakeLists using `@blast_SOURCE_DIR@` and option substitutions.

Risks: because blast is excluded from all, target dependencies must correctly bring in the library when test executables are built; this template is designed to catch that.

Test signals: configure/build success proves exported aliases work even with `EXCLUDE_FROM_ALL`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/add_subdirectory_exclude_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/add_subdirectory_test.cmake.in -->
# sources/compression/zlib/contrib/blast/test/add_subdirectory_test.cmake.in

Purpose: generated consumer project that verifies normal `add_subdirectory` consumption of blast.

Important APIs/settings: mirrors shared/static/testing options and links `blast-test.c` executables against `BLAST::BLAST` and/or `BLAST::BLASTSTATIC`.

Control flow: adds the blast source directory, defines one executable per enabled library kind, and links through the public alias targets.

State and persistence: generated source project and build artifacts under the blast test work directory.

Dependencies and integration: exercises source-tree embedding rather than installed package discovery.

Risks: assumes the blast source path is valid and reusable as a subproject from another binary directory.

Test signals: configure/build success proves subdirectory integration and alias target visibility.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/add_subdirectory_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/find_package_no_components_test.cmake.in -->
# sources/compression/zlib/contrib/blast/test/find_package_no_components_test.cmake.in

Purpose: generated consumer project that verifies default `find_package(blast REQUIRED CONFIG)` behavior without component selection.

Important APIs/settings: calls `find_package(blast REQUIRED CONFIG)`, then links test executables to shared/static targets according to substituted build options.

Control flow: package config decides whether both targets are available. The parent test marks this configure as expected failure when either shared or static blast was not built.

State and persistence: generated and configured under the blast test work directory.

Dependencies and integration: validates installed `blastConfig.cmake` no-components semantics.

Risks: no-components requiring both shared and static can be stricter than consumer expectations, but the test documents current behavior.

Test signals: configure success only when installed package exposes both component targets.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/find_package_no_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/find_package_test.cmake.in -->
# sources/compression/zlib/contrib/blast/test/find_package_test.cmake.in

Purpose: generated consumer project that verifies explicit blast package component discovery.

Important APIs/settings: conditionally calls `find_package(blast REQUIRED COMPONENTS shared CONFIG)` and/or `find_package(blast REQUIRED COMPONENTS static CONFIG)`, then links `blast-test.c` against the matching alias targets.

Control flow: only requests components for enabled library kinds, then builds consumer executables.

State and persistence: generated source and consumer build outputs in the test work directory.

Dependencies and integration: validates installed component export files `blast-shared.cmake` and `blast-static.cmake`.

Risks: repeated `find_package` calls for separate components depend on CMake package state remaining consistent.

Test signals: configure/build success proves explicit component usage works for shared and static installs.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/find_package_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/find_package_wrong_components_test.cmake.in -->
# sources/compression/zlib/contrib/blast/test/find_package_wrong_components_test.cmake.in

Purpose: generated negative test for unsupported blast package components.

Important APIs/settings: calls `find_package(blast REQUIRED COMPONENTS wrong CONFIG)` and contains normal executable linkage blocks that should not be reached on successful failure.

Control flow: package config should reject `wrong`, set not-found state, and cause configure failure because `REQUIRED` is used. Parent CTest marks this configure with `WILL_FAIL TRUE`.

State and persistence: generated under test work directory; expected to fail during configure before build artifacts matter.

Dependencies and integration: validates component validation in `blastConfig.cmake.in`.

Risks: if package config stops rejecting unknown components, this test will fail by unexpectedly succeeding.

Test signals: expected configure failure is the signal.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/find_package_wrong_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/tester.cmake -->
# sources/compression/zlib/contrib/blast/test/tester.cmake

Purpose: CMake script test runner for blast decompression fixtures.

Important inputs: `CMAKE_ARGV3` target executable, `CMAKE_ARGV4` source test directory, and `CMAKE_ARGV5` binary output directory.

Control flow: runs the executable with `test.pk` as input and writes `output.txt`, fails if the command returns nonzero, compares `output.txt` with `test.txt` using `cmake -E compare_files`, removes `output.txt`, and fails if files differ.

State and persistence: transiently writes and removes `output.txt` in the binary directory.

Dependencies and integration: invoked by CTest for shared and static blast test executables.

Risks: typo “exitited” in error message only affects diagnostics. If comparison fails, `output.txt` is still removed before the fatal error, which can make debugging harder.

Test signals: exact fixture comparison validates decompression output.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/blast/test/tester.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/crc32vx/CMakeLists.txt -->
# sources/compression/zlib/contrib/crc32vx/CMakeLists.txt

Purpose: CMake feature probe and target integration for IBM s390x vector-accelerated CRC-32.

Important APIs/settings: uses `CHECK_C_SOURCE_COMPILES`, `ZLIB_WITH_CRC32VX`, `HAS_S390X_SUPPORT`, `HAS_S390X_VX_SUPPORT`, `HAS_Z13_S390X_VX_SUPPORT`, `VGFMAFLAG`, `target_sources`, `target_compile_definitions`, and `set_source_files_properties`.

Control flow: first verifies `__s390x__`, then checks vector intrinsics with `-fzvector` for Clang or `-mzarch` otherwise. If the first check fails, retries with `-march=z13`. On success, adds `crc32_vx.c` and header to shared/static zlib targets, defines `HAVE_S390X_VX=1`, and applies compile options to the source.

State and persistence: modifies CMake target source lists, compile definitions, and source compile options.

Dependencies and integration: included via contrib feature dispatch. Requires root zlib targets to already exist, compiler support for `<vecintrin.h>`, and s390x vector facility.

Risks: compile definitions are added PUBLIC, so consumers see `HAVE_S390X_VX=1`; that may be intentional for headers but broadens ABI/compile surface. `list(APPEND VGFMAFLAG "-march=z13")` makes a CMake list, which may need correct expansion as compile options.

Test signals: contrib CI enables `ZLIB_WITH_CRC32VX`; actual vector compilation is only meaningful on s390x-capable toolchains.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/crc32vx/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/crc32vx/crc32_vx.c -->
# sources/compression/zlib/contrib/crc32vx/crc32_vx.c

Purpose: Linux on IBM z Systems hardware-accelerated CRC-32 implementation using z/Architecture Vector Extension Facility.

Important APIs/functions: internal vector routine `crc32_le_vgfm_16`, wrapper `s390_crc32_vx`, one-time setup `s390_crc32_setup`, initializer `s390_crc32_init`, and exported internal function pointer `crc32_z_hook`. Uses vector types `uv16qi`, `uv4si`, `uv2di`, `vec_gfmsum_*`, `vec_perm`, `getauxval(AT_HWCAP)`, and `HWCAP_S390_VX`.

Control flow: compile-time guard rejects Clang versions with a known broken optimization. At runtime the hook initially points to `s390_crc32_init`, which uses `z_once` to set `crc32_z_hook` to vector or generic `crc32_z` based on hardware capabilities. The vector path aligns input, processes 64-byte and 16-byte chunks with GF(2) folding and Barrett reduction, then finishes remaining bytes with generic `crc32_z`.

State and persistence: process-global hook pointer and once flag cache CPU capability selection. No persistent storage.

Dependencies and integration: includes zlib internals via `../../zutil.h` and `crc32_vx_hooks.h`, Linux auxiliary vector APIs, and s390x vector intrinsics. Built into zlib only when configure/CMake detects support.

Risks: architecture-specific pointer casts assume alignment after prealignment and vector type behavior. Runtime hook mutation must be thread-safe via `z_once`; direct external mutation of `crc32_z_hook` would be unsafe. It depends on Linux `getauxval`, so portability is limited.

Test signals: generic zlib checksum tests should pass with the hook enabled; configure/CMake probes catch compiler intrinsic support, while runtime hardware path requires s390x VX hardware or emulation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/crc32vx/crc32_vx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/crc32vx/crc32_vx_hooks.h -->
# sources/compression/zlib/contrib/crc32vx/crc32_vx_hooks.h

Purpose: internal declaration for the s390x CRC-32 hook pointer.

Important APIs/types: include guard `CRC32_VX_HOOKS_H`; declares `ZLIB_INTERNAL extern unsigned long (*crc32_z_hook)(unsigned long crc, const unsigned char FAR *buf, z_size_t len);`.

Control flow: header-only declaration; no runtime behavior.

State and persistence: exposes process-global hook state defined in `crc32_vx.c`.

Dependencies and integration: included by `crc32_vx.c` and referenced by Makefile dependencies. Requires zlib internal macros/types from `zutil.h` or equivalent prior includes.

Risks: because it declares a mutable function pointer, all users must respect one-time initialization semantics. It is internal and should not be installed as public API.

Test signals: compile/link success verifies the hook definition and declaration match.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/crc32vx/crc32_vx_hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/delphi/zlibd32.mak -->
# sources/compression/zlib/contrib/delphi/zlibd32.mak

Purpose: Borland C++/Delphi-compatible Win32 makefile for building zlib with Delphi calling conventions.

Important variables/targets: sets `LOC = -DZEXPORT=__fastcall -DZEXPORTVA=__cdecl`, `CC=bcc32`, `AR=tlib`, `ZLIB_LIB=zlib.lib`, object lists split into `OBJ1`/`OBJ2` and `OBJP1`/`OBJP2`, targets `all`, pattern `.c.obj`, `test`, `example.exe`, `minigzip.exe`, and `clean`.

Control flow: compiles C sources to `.obj`, archives objects into `zlib.lib` in two `tlib` commands to satisfy old MS-DOS command-line limits, links example and minigzip, and tests by running `example` and piping text through `minigzip`.

State and persistence: creates `.obj`, `.exe`, `.lib`, `.tds`, `zlib.bak`, and `foo.gz` artifacts; clean deletes them with DOS-style `del`.

Dependencies and integration: targets legacy Borland C++ Builder and Delphi Win32 consumers using register/fastcall conventions. Uses core zlib sources and test programs.

Risks: legacy toolchain-specific; flags and calling conventions are unsuitable for normal C ABI builds. Command-line splitting reflects old make limitations and should be preserved if maintaining this file.

Test signals: `make test` validates example and minigzip under the Borland-produced library.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/delphi/zlibd32.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/AssemblyInfo.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/AssemblyInfo.cs

Purpose: .NET assembly metadata for the DotZLib bindings project.

Important attributes: `AssemblyTitle("DotZLib")`, description for “.Net bindings for ZLib compression dll 1.2.x”, company/copyright metadata, `AssemblyVersion("1.0.*")`, and strong-name attributes `AssemblyDelaySign(false)`, empty `AssemblyKeyFile`, and empty `AssemblyKeyName`.

Control flow: declarative assembly attributes only; compiled into the .NET assembly.

State and persistence: affects assembly identity, generated version, and signing metadata. No runtime state.

Dependencies and integration: uses `System.Reflection` and `System.Runtime.CompilerServices`; consumed by legacy .NET project files in DotZLib.

Risks: wildcard assembly version creates build-dependent identities, which can complicate reproducible builds and binding redirects. Description references zlib 1.2.x and may be stale relative to current zlib sources.

Test signals: compile success of DotZLib validates metadata syntax; no functional tests are present in this file.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/AssemblyInfo.cs -->
