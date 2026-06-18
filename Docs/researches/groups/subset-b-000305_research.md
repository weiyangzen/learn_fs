# subset-b-000305 research

This grouped report covers zlib utility internals and zstd build, CI, contrib, and Linux-kernel integration files. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/zutil.c -->
# sources/compression/zlib/zutil.c

Purpose: zlib target-dependent utility implementation. It provides exported version/compile-flag queries, public error-string conversion, internal debug failure handling, fallback byte memory routines, and default allocation/free hooks used by deflate/inflate state setup.

Important APIs and control flow: `zlibVersion()` returns the compiled `ZLIB_VERSION`. `zlibCompileFlags()` encodes sizes of `uInt`, `uLong`, pointers, and `z_off_t`, plus feature macros such as `ZLIB_DEBUG`, `ZLIB_WINAPI`, `BUILDFIXED`, `DYNAMIC_CRC_TABLE`, gzip disables, workaround/fastest flags, and snprintf availability into a bitfield. `zError()` maps status codes through `ERR_MSG`. When `HAVE_MEMCPY` is absent, `zmemcpy`, `zmemcmp`, and `zmemzero` provide simple byte loops. `zcalloc`/`zcfree` have special 16-bit Turbo C and Microsoft C branches, otherwise use `malloc` for large `uInt` platforms and `calloc` for 16-bit-size arithmetic compatibility.

State and dependencies: normal builds are stateless except for `z_errmsg`. Debug builds add global `z_verbose`. Turbo C 16-bit allocation keeps a static pointer normalization table, so that path is not thread-safe. Dependencies are `zutil.h`, optionally `gzguts.h`, libc allocation/string facilities, and legacy compiler APIs.

Integration points, risks, and test signals: this file underpins zlib public diagnostics and all default internal allocation. Risks are mostly portability: integer multiplication in default `malloc(items * size)`, 16-bit table exhaustion, and compile flag drift if feature macros change. Test signals are indirect through zlib API tests, allocation failure paths, and build matrix coverage across configured macro combinations.
<!-- END_FILE_RESEARCH: sources/compression/zlib/zutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/zutil.h -->
# sources/compression/zlib/zutil.h

Purpose: private zlib implementation header that centralizes target configuration, internal types/macros, allocation wrappers, diagnostics, byte swapping, and optional one-time initialization support. Applications should use `zlib.h`, not this file.

Important APIs/types: it defines `ZLIB_INTERNAL`, `local`, byte/word aliases (`uch`, `ush`, `ulg`), optional 64-bit type `Z_U8`, `z_errmsg`, `ERR_MSG`, `ERR_RETURN`, defaults for window/memory level, block-kind constants, match length constants, `OS_CODE`, and `F_OPEN`. It maps `zmemcpy`/`zmemcmp`/`zmemzero` either to libc/far-memory variants or declares local fallbacks. `ZALLOC`, `ZFREE`, and `TRY_FREE` wrap stream allocators. `ZSWAP32` performs 32-bit byte swapping.

Control flow and state: the file is preprocessor-driven. It selects platform headers and gzip OS identifiers for DOS, VMS, z/OS, Atari, OS/2, Mac, RISC OS, Windows, BeOS, IBM i, Apple, and default Unix. Under `ZLIB_DEBUG`, trace/assert macros call `z_error`; otherwise they compile away. Under `Z_ONCE`, it defines `z_once_t` and a local `z_once()` using C11 atomics when available, falling back to a warning-producing non-thread-safe volatile implementation.

Dependencies, integration, risks, and test signals: every core zlib C file includes this header, so macro changes affect ABI internals and cross-platform builds. Risks include legacy compiler branches, macro collisions, non-atomic `Z_ONCE` fallback, and assumptions about endian/size constants. Test signals come from broad zlib compile matrices, debug builds, `Z_SOLO`, no-memcpy builds, and threaded users of one-time CRC/table initialization.
<!-- END_FILE_RESEARCH: sources/compression/zlib/zutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.cirrus.yml -->
# sources/compression/zstd/.cirrus.yml

Purpose: Cirrus CI entry for FreeBSD validation outside GitHub Actions. It proves the make-based build and core test suite work on a FreeBSD ZFS image.

Important behavior: the single task uses a `freebsd-15-0-amd64-zfs` image, installs `gmake` and `coreutils`, then runs `MOREFLAGS="-Werror" gmake -j all` followed by `gmake check`. The `-Werror` flag makes compiler warnings fatal on this platform, and `gmake` is required because the zstd makefiles use GNU Make features.

State, dependencies, and integration: CI state is only the checked-out tree and FreeBSD packages. It integrates with zstd's top-level `Makefile` targets `all` and `check`, covering library, program, tests, examples, manual/contrib subsets reached by `all`.

Risks and test signals: the workflow depends on Cirrus image availability and FreeBSD package names. It is a strong portability signal for POSIX assumptions, but narrower than the GitHub workflows because it does not run sanitizer, CMake, Meson, or cross-architecture jobs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.cirrus.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/dependabot.yml -->
# sources/compression/zstd/.github/dependabot.yml

Purpose: Dependabot configuration for GitHub Actions dependency updates.

Important behavior: version 2 config contains one update rule for the `github-actions` ecosystem at repository root, scheduled monthly. That means pinned actions in `.github/workflows` are periodically proposed for updates.

State, dependencies, and integration: no runtime state is persisted in this file. It integrates with GitHub Dependabot and the workflow files that pin action versions or SHAs. Because many workflows use SHA-pinned actions with tag comments, Dependabot can help keep supply-chain pins current while preserving reviewable diffs.

Risks and test signals: monthly cadence reduces noise but can leave action security fixes unapplied for several weeks. Dependabot PRs themselves become test signals because all affected workflows should run on the proposed update branch. The file does not manage Docker images, apt packages, or language dependencies.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/android-ndk-build.yml -->
# sources/compression/zstd/.github/workflows/android-ndk-build.yml

Purpose: GitHub Actions workflow validating zstd builds for Android arm64 using both the make build and CMake/NDK toolchain path.

Important behavior: it runs on pull requests to `dev`, `release`, and `actionsTest`, plus pushes to `actionsTest` or branches matching `*ndk*`. Steps check out the code, install JDK 17, set up the Android SDK, install NDK `27.0.12077973`, export `ANDROID_NDK_HOME`, then build with `aarch64-linux-android21-clang`, `llvm-ar`, `llvm-ranlib`, and `llvm-strip`. A second path configures `build/cmake` with the Android toolchain, ABI `arm64-v8a`, platform `android-21`, and Release build.

State, dependencies, and integration: ephemeral state is the installed NDK and `build-android` directory. It integrates top-level `make`, `build/cmake`, and Android SDK tooling.

Risks and test signals: NDK version pinning gives reproducibility but can age. The workflow tests compilation only, not runtime execution on device/emulator. It is the primary signal for Android compiler, archive tool, CMake toolchain, and minimum API compatibility.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/android-ndk-build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/cmake-tests.yml -->
# sources/compression/zstd/.github/workflows/cmake-tests.yml

Purpose: focused CMake validation across root wrapper configuration, make-wrapper integration, path handling, Windows generators, and macOS ARM64.

Important behavior: common env sets short test timeouts and warning-as-error flags with tests enabled. Jobs cover `cmake -S .` root build, `make cmakebuild`, source paths containing spaces on Linux/Windows/macOS, Visual Studio 2022 x64/Win32/ARM64, MinGW, Clang-CL, Clang-CL AVX2, a no-`ZSTD_BUILD_TESTS` regression case, and Apple Silicon build/test. Windows jobs configure from `build/cmake`, build Debug, and run `ctest`; macOS builds Release and runs `ctest`.

State, dependencies, and integration: build directories and installed artifacts are ephemeral. It integrates the root `CMakeLists.txt` shim, `build/cmake` project, CTest labels, MSBuild setup, NMake/MinGW generators, and platform runners.

Risks and test signals: runner image changes and Windows ARM availability can affect stability. The spaces-in-path job is a useful packaging robustness check. Test coverage emphasizes CMake behavior rather than the full make/sanitizer matrix.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/cmake-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/commit.yml -->
# sources/compression/zstd/.github/workflows/commit.yml

Purpose: legacy-style commit and pull-request workflow for the `dev` branch, running short build/test suites and regression result comparison.

Important behavior: `short-tests-0` runs license checks, compiler version display, `allmost` with strict flags, C99/C11 builds, regressiontest, `make check`, and C++ compile test. `short-tests-1` installs cross compilers and validates GNU dialects, PPC/PPC64/ARM/AArch64 builds, legacy and long-match tests, and non-multithreaded lib build. `regression-test` restores a cache keyed on regression data, builds `programs/zstd`, runs regression tests, generates `results.csv`, diffs it against the committed baseline, and uploads artifacts.

State, dependencies, and integration: jobs use apt dependencies, a CircleCI-derived Docker image service, GitHub cache/artifacts, top-level make targets, tests/regression, and lib/program sub-makefiles.

Risks and test signals: `actions/cache` key syntax appears CircleCI-like inside `${{ }}`-less braces and should be watched. The regression diff is a strong guard against performance/ratio drift, while cross-compile jobs protect portability.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/commit.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/dev-long-tests.yml -->
# sources/compression/zstd/.github/workflows/dev-long-tests.yml

Purpose: long-running pull-request workflow for expensive zstd validation on `dev`, `release`, and `actionsTest` branches.

Important behavior: jobs run `make all`, full `make test` on Linux/macOS/32-bit, large dictionary tests, no-intrinsics fuzzing, TSAN/UASAN/MSAN/ASAN fuzz and zstream/test-zstd variants, GCC 8 sanitizer jobs, regression under sanitizers, QEMU ARM fuzz, Valgrind stack/fuzzer checks, MSYS2 MinGW long fuzzing, and OSS-Fuzz CIFuzz builds/runs for address, undefined, and memory sanitizers. Concurrency cancels older runs for the same ref.

State, dependencies, and integration: state includes apt-installed compilers/tools, downloaded packages, sanitizer runtimes, QEMU, MSYS2 packages, OSS-Fuzz outputs, and uploaded crash artifacts. Integration spans make targets in root/tests/fuzz/regression and external OSS-Fuzz actions.

Risks and test signals: long wall time and external package repositories are the main flake sources. The workflow is the strongest signal for memory safety, race detection, fuzz stability, dictionary-heavy behavior, and emulator portability.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/dev-long-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/dev-short-tests.yml -->
# sources/compression/zstd/.github/workflows/dev-short-tests.yml

Purpose: broad but faster pull-request workflow covering build variants, packaging systems, Windows/MSYS/Cygwin, external compressors, architecture emulation, size budgets, and compiler feature switches.

Important behavior: jobs validate linux-kernel import/test, benchmarking, 32-bit check, C89/C++/GNU90/C99 compatibility, dynamic library linkage, GCC 7/8 builds, MinGW cross compile, ARM build, shellcheck, zlib wrapper with Valgrind, LZ4/threadpool/library build scripts, AVX2 and 32-bit builds, external compressor matrices, implicit fallthrough warnings, Meson Linux/Windows/MinGW, Visual Studio matrices, lib size thresholds, minified decompressor macros, dynamic BMI2 modes, all program variants, QEMU consistency across many architectures, MSYS2 MinGW short tests, Visual Studio runtime tests, Cygwin tests, pkg-config install/use, version compatibility, PGO, musl, Intel CET/SDE, and Intel oneAPI `icx`.

State, dependencies, and integration: it touches nearly every build system and many package managers. It integrates top-level make, lib/program/test targets, Meson, CMake indirectly, Visual Studio solutions, kernel contrib, wrappers, and examples.

Risks and test signals: breadth creates external-service/package flake risk, but failures are high-signal because this workflow encodes zstd's portability contract across compilers, OS layers, optional libraries, and CPU features.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/dev-short-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/nightly.yml -->
# sources/compression/zstd/.github/workflows/nightly.yml

Purpose: scheduled and branch-triggered nightly regression workflow.

Important behavior: runs daily at midnight UTC and on pushes to `release`, `dev`, and branches matching `*nightly*`. The active job checks out code, installs `libcurl4-openssl-dev`, builds `programs/zstd`, and builds/runs `tests/regression`. A block of longer historical tests is left commented as documentation for possible nightly expansion.

State, dependencies, and integration: state is only apt packages and build outputs. It integrates the program build and regression harness, but does not upload comparison artifacts in this workflow.

Risks and test signals: as written it is much narrower than the long/short PR workflows and may duplicate only part of commit regression coverage. It is still useful as a scheduled signal for drift in runner images, package dependencies, and regression test health between active development events.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/nightly.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/publish-release-artifacts.yml -->
# sources/compression/zstd/.github/workflows/publish-release-artifacts.yml

Purpose: release-published workflow that creates signed and checksummed source archives and uploads them as GitHub release assets.

Important behavior: it runs only for published releases and tag refs. The archive step derives `TAG` from `GITHUB_REF`, maps `vX.Y.Z` to artifact version `X.Y.Z`, creates `zstd-$VERSION.tar` via `git archive`, compresses it with `zstd -19` and `gzip -9`, computes SHA256 files, and optionally imports a GPG key from secrets to create detached armored signatures. The publish step uses `skx/github-action-publish-binaries` with `GITHUB_TOKEN` to upload `artifacts/*`.

State, dependencies, and integration: depends on Git, zstd/gzip/sha256sum/gpg on the Ubuntu runner, release secrets, and GitHub release permissions. Artifacts are generated in an `artifacts` subdirectory.

Risks and test signals: secret handling and tag parsing are critical. The workflow assumes a `zstd` binary is available on the runner. Validation is mostly by successful release upload; release_check/manual workflows provide complementary pre-release signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/publish-release-artifacts.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/release_check.yml -->
# sources/compression/zstd/.github/workflows/release_check.yml

Purpose: release-branch guard ensuring generated documentation is committed before release.

Important behavior: on pushes and pull requests to `release`, `verify-manual` saves `doc/zstd_manual.html`, runs `make manual`, and fails if the regenerated file differs. `verify-man-pages` installs Ruby and `ronn`, saves `programs/zstd.1`, `zstdgrep.1`, and `zstdless.1`, runs `make -C programs man`, and fails if any regenerated man page differs.

State, dependencies, and integration: temporary `.saved` files are created in the checkout. It integrates `contrib/gen_html`, the top-level manual target, `programs` man generation, and Ruby gem tooling.

Risks and test signals: the workflow depends on deterministic generator output and current `ronn` behavior. It is a strong release hygiene signal, but it does not validate archive packaging or binaries; those are separate release workflows.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/release_check.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/scorecards.yml -->
# sources/compression/zstd/.github/workflows/scorecards.yml

Purpose: OpenSSF Scorecards supply-chain security analysis for the canonical `facebook/zstd` repository.

Important behavior: triggers on branch protection rule changes, weekly schedule, and pushes to `dev`. The job is gated by `github.repository == 'facebook/zstd'`, checks out code without persisted credentials, runs `ossf/scorecard-action` to produce SARIF and publish public results, uploads the SARIF as an artifact with five-day retention, and uploads it to GitHub code scanning.

State, dependencies, and integration: depends on GitHub security-events/id-token permissions, Scorecards action, artifact upload, and CodeQL SARIF upload. Generated state is `results.sarif`.

Risks and test signals: this is not a build test; it reports repository security posture. Action SHAs are pinned, which supports supply-chain integrity. Failures or score regressions signal branch protection, pinned dependency, token, or workflow-hardening issues.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/scorecards.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/.github/workflows/windows-artifacts.yml -->
# sources/compression/zstd/.github/workflows/windows-artifacts.yml

Purpose: build and publish Windows binary artifact packages for x86_64, i686, and ARM64.

Important behavior: runs on selected branches and published releases. The matrix uses MSYS2 for mingw64/mingw32 and CMake/Visual Studio on `windows-11-arm` for ARM64. MSYS2 jobs build static zlib and LZ4 dependencies, then build zstd programs with static linking and external library support. ARM64 configures `build/cmake` for Visual Studio 2022 ARM64 with programs/shared/static enabled. All variants run `lib/dll/example/build_package.bat`, rename `bin` to `zstd-${ref}-${ziparch}`, upload an inspection artifact, package a zip, and upload it to a GitHub release on release events.

State, dependencies, and integration: state includes cloned zlib/lz4 repos, MSYS2 packages, CMake build dirs, generated bin directories, artifacts, and release assets.

Risks and test signals: branch/ref names flow into artifact names. Static dependency versions are pinned by tags. The workflow tests packaging scripts and release upload path, but not full CLI runtime behavior beyond successful package build.
<!-- END_FILE_RESEARCH: sources/compression/zstd/.github/workflows/windows-artifacts.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/CMakeLists.txt -->
# sources/compression/zstd/CMakeLists.txt

Purpose: thin top-level CMake wrapper so users can run `cmake -S .` at the repository root while keeping real policy and language configuration under `build/cmake`.

Important behavior: requires CMake 3.10, declares `project(zstd-superbuild LANGUAGES NONE)`, rejects in-source builds by comparing `CMAKE_SOURCE_DIR` and `CMAKE_BINARY_DIR`, and delegates with `add_subdirectory(build/cmake)`.

State, dependencies, and integration: no persistent state beyond generated CMake build files. It integrates with root-level CMake workflows and downstream users who expect the repository root to be configurable, while avoiding language enablement at the wrapper layer.

Risks and test signals: the main risk is divergence between root invocation and direct `build/cmake` invocation. The `cmake-root-basic` workflow explicitly validates this wrapper, and spaces-in-path CMake tests provide additional coverage.
<!-- END_FILE_RESEARCH: sources/compression/zstd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/Makefile -->
# sources/compression/zstd/Makefile

Purpose: top-level GNU Make orchestrator for zstd library, CLI, tests, examples, documentation, contrib tools, install/uninstall, and a large set of CI-oriented build variants.

Important targets and control flow: defaults build `lib-release` and `zstd-release`. `all` expands to `allmost examples manual contrib`; `allzstd` builds lib, programs, and tests; `zstd`/`zstd-release` build programs and symlink the root binary; `test` builds all program variants, runs tests, and educational decoder tests; `check` delegates to tests. Install/list targets are enabled on supported POSIX OSes. Variant targets cover compiler versions, C standards, cross-compilation, QEMU fuzz/test, sanitizers, static analysis, CMake, Meson, PGO, and dependency installation helpers.

State, dependencies, and integration: state is build outputs across `lib`, `programs`, `tests`, `examples`, `contrib`, wrapper dirs, `cmakebuild`, `mesonbuild`, and install staging. It depends on included `lib/install_oses.mk`, platform `uname`, compiler/tool variables, and optional external libraries.

Risks and test signals: many targets mutate shared build directories and call `clean`, so parallel external invocation needs care. The GitHub workflows exercise this file extensively; failures here usually indicate broad build-system regressions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/Package.swift -->
# sources/compression/zstd/Package.swift

Purpose: Swift Package Manager manifest exposing zstd's C library as a Swift-consumable package product.

Important behavior: declares package `zstd`, supports macOS 10.10, iOS 9, and tvOS 9, and exports one library product `libzstd`. The single target points at `lib`, includes source subdirectories `common`, `compress`, `decompress`, and `dictBuilder`, publishes headers from `.`, and adds `.` as a C header search path. Swift language version is 5, C standard is GNU11, and C++ standard is GNU++14.

State, dependencies, and integration: no external package dependencies are declared. It integrates SwiftPM with the repository's C source layout and public headers.

Risks and test signals: source list maintenance is the main risk; new required lib subdirectories must be reflected here. SwiftPM builds may expose header visibility or platform-availability problems not covered by make/CMake workflows unless explicitly tested downstream.
<!-- END_FILE_RESEARCH: sources/compression/zstd/Package.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/cleanTabs -->
# sources/compression/zstd/contrib/cleanTabs

Purpose: small maintenance script to replace tab characters with four spaces across selected zstd source and contrib files.

Important behavior: runs a single `sed -i ''` substitution over globbed headers/C files in `lib`, `programs`, `tests`, contrib headers/C++ files, examples, and zlibWrapper. The `$'...'` shell quoting is used to express a literal tab.

State, dependencies, and integration: it mutates source files in place and depends on shell glob expansion plus a BSD/macOS-style `sed -i ''` interface. The top-level `Makefile` exposes it through the `cleanTabs` target by running inside `contrib`.

Risks and test signals: this script is destructive formatting maintenance, not a test. It may fail on GNU sed unless compatible handling is available, and glob patterns may miss nested files or expand differently by shell. Review diffs after running it.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/cleanTabs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/diagnose_corruption/Makefile -->
# sources/compression/zstd/contrib/diagnose_corruption/Makefile

Purpose: build recipe for the `check_flipped_bits` corruption-diagnosis utility.

Important behavior: target `all` builds `check_flipped_bits`. It points `ZSTDLIBDIR` at `../../lib`, appends include paths for lib root/common/compress/decompress, enables an extensive warning set, and links `check_flipped_bits.c` with `libzstd.a`. The static library target delegates to `make -C ../../lib libzstd.a`. `clean` removes the binary.

State, dependencies, and integration: build outputs are the local executable and `../../lib/libzstd.a`. It integrates with zstd static-linking-only APIs used by the C file.

Risks and test signals: warnings are strong but not forced to `-Werror` unless `MOREFLAGS` supplies it. The clean target does not remove `.exe` extensions even though the compile target honors `$(EXT)`, which can leave Windows artifacts.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/diagnose_corruption/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/diagnose_corruption/check_flipped_bits.c -->
# sources/compression/zstd/contrib/diagnose_corruption/check_flipped_bits.c

Purpose: standalone diagnostic tool that mutates a compressed input one bit/byte at a time and records whether the perturbed blob still decompresses, helping investigate corruption detection behavior and error-code distribution.

Important APIs and control flow: `stuff_t` owns input, perturbed buffer, output buffer, optional dictionary data/DDict, DCtx, success count, and per-error counters. `readFile()` loads regular files. `readDict()` and `readDictByID()` create dictionaries, including directory lookup by `DICTID.zstd-dict`. `init_stuff()` parses `input [-d dict] [-D dir]`, loads buffers, creates dictionary/context, and initializes counters. `test_decompress()` resets the DCtx, selects cached or perturbation-requested dictionary, streams decompression with `ZSTD_decompressStream`, and counts `ZSTD_getErrorCode()` failures. `perturb_bits()` flips each bit; `perturb_bytes()` tries all byte values; `main()` first requires the original blob to fail, then runs both perturbation passes.

State, dependencies, and risks: state is heap-owned and mostly freed by `free_stuff`, but early init failures can leak partial allocations. Dictionary-by-ID depends on frame headers and directory naming. It uses `%m`, POSIX stat, and asserts/exit-style failures, so it is diagnostic rather than robust library code. Test signals are manual: successful runs summarize decompression successes and error counts.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/diagnose_corruption/check_flipped_bits.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/docker/Dockerfile -->
# sources/compression/zstd/contrib/docker/Dockerfile

Purpose: multi-stage Dockerfile producing a minimal Alpine image containing installed zstd binaries/libraries.

Important behavior: the builder stage uses a pinned Alpine image digest, installs `make gcc libc-dev`, copies the repository to `/src`, runs `make`, and installs into `/pkg` via `make DESTDIR=/pkg install`. The final stage uses the same pinned Alpine digest, copies `/pkg` into the image, creates a license directory, copies `LICENSE`, and defaults `CMD` to `/usr/local/bin/zstd`.

State, dependencies, and integration: build state is confined to Docker layers. It integrates the top-level make/install path with Alpine/musl packaging expectations.

Risks and test signals: the final `COPY` path uses `/usr/local/share/licences/zstd/` while the directory created is `/usr/local/share/licenses/zstd`, a spelling mismatch that can place the license under an unintended directory. The image does not run tests; successful build/install is the signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/Makefile -->
# sources/compression/zstd/contrib/externalSequenceProducer/Makefile

Purpose: build recipe for the external sequence producer example program.

Important behavior: defines `PROGDIR`, `LIBDIR`, and `LIBZSTD`, includes lib root/compress/common headers, uses GNU99 plus broad warning flags, and builds `externalSequenceProducer` from `sequence_producer.c`, `main.c`, and `libzstd.a`. The library target delegates to `make -C ../../lib libzstd.a CFLAGS=...`; `clean` removes local objects, cleans the lib directory, and removes the executable.

State, dependencies, and integration: local executable/object files and `../../lib/libzstd.a` are build state. It integrates with zstd static-linking-only sequence producer APIs and internal compression headers.

Risks and test signals: cleaning the shared lib directory can affect other concurrent builds. The example is built by top-level contrib target, which serves as the main regression signal for API compatibility.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/main.c -->
# sources/compression/zstd/contrib/externalSequenceProducer/main.c

Purpose: executable example showing how to register an external sequence producer with a zstd compression context and validate round-trip compression.

Important behavior: expects one file path. It creates a `ZSTD_CCtx`, registers `simpleSequenceProducer` with an integer state pointer, enables `ZSTD_c_enableSeqProducerFallback`, reads the whole file into memory, allocates `ZSTD_compressBound(srcSize)` destination, compresses with `ZSTD_compress2`, decompresses with `ZSTD_decompress`, and compares source/validation buffers. `CHECK` prints zstd error names and returns failure.

State, dependencies, and integration: state is heap buffers and a compression context. It depends on `ZSTD_STATIC_LINKING_ONLY`, public/static zstd APIs, `zstd_errors.h`, and the local producer header.

Risks and test signals: file I/O uses `assert`, `ftell` result is stored in `size_t`, and all input is held in memory, so this is example code rather than robust CLI code. The success message and byte-for-byte comparison are its runtime test signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.c -->
# sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.c

Purpose: simple demonstration match finder implementing `ZSTD_sequenceProducer_F` for the external sequence producer API.

Important behavior: uses a 1024-entry hash table with match length search size 4. For each input position, it hashes the current bytes with `ZSTD_hashPtr`, checks the previous index in the table, counts match length with `ZSTD_count`, emits a `ZSTD_Sequence` when the match meets `ZSTD_MINMATCH_MIN` and the offset fits the provided `windowSize`, advances by match length, and finally emits a terminal literal-only sequence. Dict inputs, capacity, compression level, and producer state are ignored.

State, dependencies, and integration: state is a stack hash table per call. It depends on `zstd_compress_internal.h` internals and the local header, so it is tied to static/internal API compatibility.

Risks and test signals: it does not honor `outSeqsCapacity`, so unusual small capacities could overflow. It ignores dictionaries and is intentionally naive; round-trip validation in `main.c` and contrib build coverage are the key signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.h -->
# sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.h

Purpose: public header for the external sequence producer example.

Important APIs: includes `zstd.h` with `ZSTD_STATIC_LINKING_ONLY` and declares `simpleSequenceProducer()` using the zstd external sequence producer callback signature: producer state, output sequence buffer/capacity, source buffer/size, dictionary buffer/size, compression level, and window size.

State, dependencies, and integration: the header has no state. It is included by `main.c` and implemented by `sequence_producer.c`, binding the example to static-linking-only zstd sequence types.

Risks and test signals: include guard name `MATCHFINDER_H` is generic and could collide in larger integrations. Any signature drift in zstd's static sequence producer API will break this example at compile time, which the contrib build catches.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/externalSequenceProducer/sequence_producer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/freestanding_lib/freestanding.py -->
# sources/compression/zstd/contrib/freestanding_lib/freestanding.py

Purpose: generator that copies and rewrites zstd library sources into a freestanding/embedded-friendly output tree, especially for the Linux kernel import path.

Important APIs and control flow: constants choose included subdirs, skipped threading/pool/dependency files, and optional xxhash omission. `FileLines` reads/writes files. `PartialPreprocessor` repeatedly simplifies simple `#if/#ifdef/#ifndef/#elif defined(...)` blocks using supplied defines, replaces, and undefs, with partial handling for `&&`/`||` and integer comparisons. `Freestanding.go()` copies selected source files, substitutes `zstd_deps.h` and `mem.h`, hardwires macros, removes marked excluded sections, rewrites includes, optionally renames external `XXH64` symbols/types, applies Python-regex sed replacements, and inserts SPDX identifiers. CLI parsing supports `-D`, `-U`, `-R`, `-E`, `--rewrite-include`, `--xxhash`, `--xxh64-state`, `--xxh64-prefix`, `--sed`, and `--spdx`; it always undefines multithreading and disables tracing by default.

State, dependencies, and integration: persistent state is the generated output directory. It depends on Python stdlib, source zstd layout, replacement dependency headers, and predictable preprocessor patterns. Linux-kernel `Makefile` is a major consumer.

Risks and test signals: the partial preprocessor is intentionally incomplete and can mis-handle complex/multiline preprocessor logic. Regex include/sed rewrites are powerful but fragile. Kernel import tests and generated library builds are the main validation signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/freestanding_lib/freestanding.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/gen_html/Makefile -->
# sources/compression/zstd/contrib/gen_html/Makefile

Purpose: build and run the zstd API manual HTML generator.

Important behavior: compiles `gen_html.cpp` with C++ warning flags, derives library version components from `../../lib/zstd.h` using `sed`, and generates `../../doc/zstd_manual.html` by invoking `./gen_html$(EXT) $(LIBVER) $(ZSTDAPI) $(ZSTDMANUAL)`. `manual` depends on the generator and output; `clean` removes the executable.

State, dependencies, and integration: state is the local `gen_html` binary and generated manual under `doc`. It integrates with top-level `make manual` and release-check workflow.

Risks and test signals: version extraction depends on exact macro formatting in `zstd.h`. Generator output must be deterministic, because release checks compare regenerated manual against committed HTML. Windows extension handling is included but shell tooling remains POSIX-like.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/gen_html/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/gen_html/gen-zstd-manual.sh -->
# sources/compression/zstd/contrib/gen_html/gen-zstd-manual.sh

Purpose: convenience shell script to generate a local `zstd_manual.html` from `../../lib/zstd.h` using the already-built `gen_html` executable.

Important behavior: extracts major/minor/release macros with `sed`, combines them into `LIBVER_SCRIPT`, echoes the version, and runs `./gen_html $LIBVER_SCRIPT ../../lib/zstd.h ./zstd_manual.html`.

State, dependencies, and integration: writes `./zstd_manual.html` in the contrib directory rather than the committed `doc/zstd_manual.html` path used by the Makefile. It depends on POSIX shell, sed, and a compiled `gen_html` binary.

Risks and test signals: because it emits to a local path, it is more of a manual helper than the release path. Macro-format drift or missing executable causes failure. The release workflow validates the Makefile path, not necessarily this helper.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/gen_html/gen-zstd-manual.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/gen_html/gen_html.cpp -->
# sources/compression/zstd/contrib/gen_html/gen_html.cpp

Purpose: C++ parser/generator that extracts documented API comments and declarations from `zstd.h` and emits an HTML manual.

Important APIs and control flow: `trim()` strips selected characters from both ends, `trim_comments()` extracts C comment bodies, `get_lines()` collects input lines until a terminator or blank-line boundary, and `print_line()` removes `ZSTDLIB_API` and toggles bold around inline comments. `main()` reads version/input/output args, loads all input lines, scans for typedef blocks, inline member comments, and comment markers (`/**=`, `/*!`, `/**`, `/*-`, `/*=`). It emits bold declarations, paragraph comments, chapter anchors, a table of contents, and fixed ISO-8859-1 HTML boilerplate.

State, dependencies, and integration: state is in vectors/stringstreams during one run. It depends only on C++ standard streams/strings/vectors and zstd comment conventions. It integrates with `contrib/gen_html/Makefile` and release checks.

Risks and test signals: parsing is ad hoc and sensitive to comment/declaration formatting. It does not HTML-escape arbitrary content robustly. Deterministic output comparison in `release_check.yml` is the main test signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/gen_html/gen_html.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/largeNbDicts/Makefile -->
# sources/compression/zstd/contrib/largeNbDicts/Makefile

Purpose: build recipe for the `largeNbDicts` benchmark tool, including shared program utility objects.

Important behavior: includes zstd lib/common/dictBuilder and programs headers, uses GNU99 with broad warning flags, builds `largeNbDicts` from local C plus `util.o`, `timefn.o`, `benchfn.o`, `datagen.o`, `xxhash.o`, and `libzstd.a`. Utility objects are compiled from `../../programs`, xxhash from `../../lib/common`, and libzstd via delegated make. `clean` removes local objects, cleans the lib directory, and deletes the executable.

State, dependencies, and integration: local objects/executable and `../../lib/libzstd.a` are build state. It integrates benchmark helper APIs, dictionary builder APIs, and static zstd.

Risks and test signals: cleaning the shared lib can disrupt parallel builds. Build coverage through top-level `contrib` catches compile drift; benchmark correctness is mostly manual/runtime.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/largeNbDicts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/largeNbDicts/largeNbDicts.c -->
# sources/compression/zstd/contrib/largeNbDicts/largeNbDicts.c

Purpose: benchmark utility for measuring compression or decompression performance when cycling through a very large number of zstd dictionaries, stressing cache behavior and dictionary attach/search choices.

Important APIs and control flow: buffer helpers load files and optionally train a 4 KiB dictionary with `ZDICT_trainFromBuffer`. Slice helpers split input into blocks or repeat/truncate to a requested block count. Dictionary collection helpers allocate many `ZSTD_CDict`/`ZSTD_DDict` objects and shuffle pointers to avoid linear-address artifacts. `compressBlocks()` precompresses source slices and records compressed sizes. `benchMem()` builds `BMK_benchParams_t`, cycles through dictionaries in `compress()` or `decompress()` callbacks, runs timed rounds, aggregates fastest or median speed, and appends CSV output named after the executable. `bench()` orchestrates loading, slicing, dictionary creation, no-dict/dict compression ratio reporting, result buffer allocation, benchmark execution, and cleanup. `main()` parses options for compression/decompression, recursion, block size/count, dictionary count/file, rounds, level, dedicated dict search, dict content/attach preferences, and prefetch.

State, dependencies, and risks: state is heap-heavy and intentionally large, capped at 1200 MB input. It depends on program utilities, benchmark framework, zstd static APIs, and dictionary builder. Many failures use `assert`/abort, so it is not hardened CLI code. Test signals are compile coverage and benchmark CSV/output sanity.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/largeNbDicts/largeNbDicts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/Makefile -->
# sources/compression/zstd/contrib/linux-kernel/Makefile

Purpose: generate, import, and test a Linux-kernel-shaped zstd source tree from upstream zstd.

Important behavior: `libzstd` deletes/recreates `linux/`, invokes `freestanding.py` with kernel-specific dependency rewrites, external xxhash mapping, SPDX insertion, disabled intrinsics/ASM/multithreading/legacy support, Linux/compiler macro choices, sanitizer disables, heap compression mode, and visibility/fallthrough replacements. It removes AMD64 assembly, moves public headers to `linux/include/linux`, copies the kernel wrapper header/modules/source lists, and installs `linux.mk` as the generated lib Makefile. `import` copies generated headers/lib into `$(LINUX)`. `import-upstream` copies raw upstream sources with selected removals. `test` regenerates and runs `make -C test run-test` with strict warnings.

State, dependencies, and integration: generated state is `contrib/linux-kernel/linux`. It depends on `freestanding.py`, kernel shim files, upstream lib layout, and test fixtures.

Risks and test signals: macro hardwiring is fragile when upstream internals change. The `test` target is the key signal, also exercised by `dev-short-tests` linux-kernel job.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/btrfs-benchmark.sh -->
# sources/compression/zstd/contrib/linux-kernel/btrfs-benchmark.sh

Purpose: manual benchmark script comparing Btrfs compression modes using the Silesia corpus.

Important behavior: sets `BENCHMARK_DIR=$HOME/silesia/` and `N=10`, unmounts/remounts `/mnt/btrfs` on `/dev/sda3` with user-supplied mount options, clears the filesystem, copies the corpus ten times while timing compression, estimates ratio from `df` and `du`, remounts to reduce cache effects, times a tar read for decompression, then cleans and unmounts. Historical result comments compare none, lzo, zlib, and zstd levels.

State, dependencies, and integration: it mutates `/mnt/btrfs` and `/dev/sda3` data destructively. It depends on sudo, btrfs, coreutils, tar, Silesia corpus, and a specific benchmark environment.

Risks and test signals: this is dangerous outside a prepared VM because it deletes filesystem contents. It is not automated CI; results are manual performance signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/btrfs-benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/btrfs-extract-benchmark.sh -->
# sources/compression/zstd/contrib/linux-kernel/btrfs-extract-benchmark.sh

Purpose: manual benchmark script for Btrfs compression behavior while copying, extracting, and reading a Linux kernel tarball.

Important behavior: uses `$HOME/linux-4.11.6.tar`, remounts `/mnt/btrfs` on `/dev/sda3` with supplied compression options, clears the filesystem, times copying the tarball, estimates tarball ratio, remounts, times extraction, removes the tarball, remounts again, estimates extracted-tree ratio, times reading via tar, then cleans and unmounts. Commented historical results compare none, lzo, zlib, and zstd level 1.

State, dependencies, and integration: destructively modifies `/mnt/btrfs` and requires sudo, btrfs, tar, df/du, and the benchmark tarball.

Risks and test signals: high risk if run on the wrong block device. It is documentation/manual benchmarking, not CI. Useful signals are elapsed copy/extract/read times and approximate disk-usage ratios.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/btrfs-extract-benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/decompress_sources.h -->
# sources/compression/zstd/contrib/linux-kernel/decompress_sources.h

Purpose: include-list header for kernel boot/decompression contexts that need all zstd decompression sources in one translation unit.

Important behavior: defines `ZSTD_DISABLE_ASM 1` so assembly Huffman code is excluded, then includes common debug/entropy/error/FSE/zstd common sources, decompression Huffman/DDict/decompress/block sources, and `zstd_decompress_module.c`.

State, dependencies, and integration: no runtime state. It depends on the generated kernel source layout under `lib/zstd` and is copied by the linux-kernel Makefile. It is used by kernel decompression code such as `lib/decompress_unzstd.c` where normal multi-object linking may not be available.

Risks and test signals: direct inclusion of `.c` files is sensitive to duplicate symbols, include order, and macro configuration. The linux-kernel test target validates that the generated source set remains buildable.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/decompress_sources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/linux.mk -->
# sources/compression/zstd/contrib/linux-kernel/linux.mk

Purpose: Linux kernel Kbuild makefile for generated zstd library objects.

Important behavior: declares `obj-$(CONFIG_ZSTD_COMPRESS)`, `obj-$(CONFIG_ZSTD_DECOMPRESS)`, and `obj-$(CONFIG_ZSTD_COMMON)`. It lists compression module/core objects, decompression module/core objects, and common debug/entropy/error/FSE/common objects in `zstd_compress-y`, `zstd_decompress-y`, and `zstd_common-y` respectively.

State, dependencies, and integration: no standalone state; Kbuild consumes it after `contrib/linux-kernel/Makefile` copies it to `linux/lib/zstd/Makefile` or an actual Linux tree. It integrates generated source files with kernel config symbols.

Risks and test signals: object lists must stay synchronized with upstream zstd source dependencies and generated module wrappers. Kernel import/build tests catch missing or obsolete objects.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/linux.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/linux_zstd.h -->
# sources/compression/zstd/contrib/linux-kernel/linux_zstd.h

Purpose: kernel-style wrapper API header around upstream zstd APIs, exposing a stable, lower-case `zstd_*` surface for Linux users while hiding direct upstream symbols.

Important APIs/types: aliases upstream error, memory, dictionary, parameter, context, stream, buffer, frame, and sequence types to kernel names. Declares helper functions for bounds, errors, compression levels, parameter selection, context parameter setting, workspace-bound/init APIs for compression/decompression and streams, one-shot compression/decompression with dictionaries, advanced context/dictionary allocation/free, streaming compress/flush/end/decompress, frame-size/header inspection, external sequence producer registration, and sequence/literal compression.

State and integration: header-only declarations with no state. It includes `linux/types.h`, generated `linux/zstd_errors.h`, and `linux/zstd_lib.h`, and is installed as `linux/include/linux/zstd.h` by the generator. Module wrapper C files provide the definitions and export selected symbols.

Risks and test signals: it must track upstream API changes and kernel consumers' exported-symbol needs. Workspace lifetime requirements are critical in kernel callers. The linux-kernel test build and macro tests are primary signals; actual kernel integration adds ABI/API pressure.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/linux_zstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/mem.h -->
# sources/compression/zstd/contrib/linux-kernel/mem.h

Purpose: Linux-kernel replacement for zstd's `mem.h`, mapping zstd memory I/O helpers onto kernel unaligned access, byte-swap, and type facilities.

Important APIs and control flow: defines zstd basic integer aliases (`BYTE`, `U8`...`S64`) and static inline helpers for 32/64-bit detection, endian detection via `__LITTLE_ENDIAN`, native unaligned reads/writes, little-endian and big-endian reads/writes for 16/24/32/64/size_t, and byte swaps. Implementations call kernel-style `get_unaligned*`, `put_unaligned*`, `swab32`, and `swab64`; size_t helpers branch on `MEM_32bits()`.

State, dependencies, and integration: no state. It depends on `linux/unaligned.h`, `linux/compiler.h`, `linux/swab.h`, `linux/types.h`, and zstd `debug.h`. `freestanding.py` copies it into generated `common/mem.h`.

Risks and test signals: endian macro assumptions and test shim correctness are important. The 24-bit helpers manually compose bytes. Kernel import tests validate compilation and basic behavior through zstd round trips.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/squashfs-benchmark.sh -->
# sources/compression/zstd/contrib/linux-kernel/squashfs-benchmark.sh

Purpose: manual benchmark script for SquashFS compression/decompression using a prepared Ubuntu filesystem tree.

Important behavior: defines `BENCHMARK_DIR=$HOME/squashfs-root/` and `BENCHMARK_FS=$HOME/filesystem.squashfs`, removes prior filesystem output and unmounts `/mnt/squashfs`, runs `sudo mksquashfs` with user-supplied options while timing compression, estimates ratio using `du`, mounts the generated SquashFS, times reading it through tar, and unmounts.

State, dependencies, and integration: writes/removes `$HOME/filesystem.squashfs` and mounts `/mnt/squashfs`. Depends on sudo, squashfs-tools, tar, du, and a pre-extracted benchmark directory.

Risks and test signals: manual only, and mount/remove operations require care. Useful outputs are compression time, approximate ratio, and decompression read time for comparing SquashFS compressor choices.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/squashfs-benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/Makefile -->
# sources/compression/zstd/contrib/linux-kernel/test/Makefile

Purpose: user-space test harness Makefile for the generated Linux-kernel zstd source tree.

Important behavior: points `LINUX` to `../linux`, derives generated source/object lists from module/common/compress/decompress directories, adds include paths for generated linux headers, generated zstd lib, and local shim headers, defines `NDEBUG`, disables deprecated warnings, and sets `ZSTD_ASAN_DONT_POISON_WORKSPACE` because static workspace reuse conflicts with poisoning. It builds assembly objects, archives `liblinuxzstd.a`, links `test` against it, builds `static_test`, and `run-test` executes `macro-test.sh`, `test`, and `static_test`. `clean` removes generated objects and local test binaries/libs.

State, dependencies, and integration: state is generated object files, archive, and test executables. It integrates generated kernel sources with local fake Linux headers.

Risks and test signals: wildcard object selection may hide missing-source intent changes. `run-test` is the main validation gate for generated kernel import.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/compiler.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/compiler.h

Purpose: minimal user-space shim for Linux compiler annotations needed by the kernel zstd test harness.

Important behavior: defines `inline` as `__inline __attribute__((unused))` if absent, `noinline` as `__attribute__((noinline))`, and `fallthrough` as GCC's fallthrough attribute.

State, dependencies, and integration: no state and no external includes. It is included indirectly by generated kernel zstd files through `linux/compiler.h` when compiling outside a real kernel tree.

Risks and test signals: only covers the annotations currently needed by the generated sources. Missing future compiler macros will surface as linux-kernel test compile failures.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/errno.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/errno.h

Purpose: minimal `linux/errno.h` shim for the kernel zstd user-space tests.

Important behavior: defines only `EINVAL` as `22` under an include guard.

State, dependencies, and integration: no state and no includes. It satisfies generated code that needs invalid-argument error constants without pulling real kernel headers.

Risks and test signals: any generated source needing additional errno values will fail to compile until the shim is extended. The linux-kernel test target is the signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/kernel.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/kernel.h

Purpose: minimal `linux/kernel.h` shim providing alignment and warning macros for user-space kernel-zstd tests.

Important behavior: defines `WARN_ON(x)` as a no-op, `PTR_ALIGN(p,a)` using `ALIGN`, and `ALIGN`/`ALIGN_MASK` arithmetic macros for power-of-two alignment.

State, dependencies, and integration: no state or includes. It supports generated zstd code compiled outside the Linux kernel.

Risks and test signals: `WARN_ON` does not evaluate/report like the real kernel macro, so tests may miss warning-side effects. Alignment macros rely on `typeof`, so GCC/Clang extensions are required. Compile/runtime kernel tests are the signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/limits.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/limits.h

Purpose: shim mapping `linux/limits.h` to the host C library limits for user-space kernel-zstd tests.

Important behavior: include guard plus `#include <limits.h>`.

State, dependencies, and integration: no state. It satisfies include rewrites performed by the freestanding generator.

Risks and test signals: host libc limits may not perfectly match kernel limits, but zstd's generated code primarily needs numeric bounds. Compile failures or behavioral test failures indicate missing compatibility.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/math64.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/math64.h

Purpose: minimal `linux/math64.h` shim for user-space kernel-zstd tests.

Important behavior: defines `div_u64(dividend, divisor)` as plain C division.

State, dependencies, and integration: no state and no includes. It provides the one 64-bit division helper needed by generated code in the test environment.

Risks and test signals: real kernel helpers handle architecture-specific details; this shim assumes host C supports the division directly. Additional math64 needs will surface during linux-kernel test compilation.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/math64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/module.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/module.h

Purpose: user-space shim for Linux module export/license macros used by generated zstd module wrappers.

Important behavior: `EXPORT_SYMBOL(symbol)` and `EXPORT_SYMBOL_GPL(symbol)` create a pointer variable `__symbol` referencing the exported symbol, forcing the symbol to be type-checked/retained. `MODULE_LICENSE` and `MODULE_DESCRIPTION` are no-ops.

State, dependencies, and integration: export macros create global pointer variables in test builds. This helps validate wrapper symbols without requiring kernel module infrastructure.

Risks and test signals: it does not model real kernel export visibility or license enforcement. Compile/link success in the linux-kernel tests is the main signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/printk.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/printk.h

Purpose: minimal logging shim for generated kernel-zstd code compiled in user space.

Important behavior: defines `pr_debug(...)` as a no-op.

State, dependencies, and integration: no state and no includes. It satisfies kernel logging calls without producing output during tests.

Risks and test signals: debug messages are suppressed, so diagnostics differ from kernel builds. If generated code requires other printk levels, compilation will fail and prompt shim expansion.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/stddef.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/stddef.h

Purpose: shim mapping `linux/stddef.h` to standard C `stddef.h` for user-space tests.

Important behavior: include guard plus `#include <stddef.h>`.

State, dependencies, and integration: no state. It supplies size and null-related definitions required after include rewriting.

Risks and test signals: standard C definitions are sufficient for current generated zstd code. Missing kernel-specific typedefs/macros would show up as compile failures.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/stddef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/swab.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/swab.h

Purpose: byte-swap shim for user-space kernel-zstd tests.

Important behavior: defines `swab32(x)` and `swab64(x)` using compiler builtins `__builtin_bswap32` and `__builtin_bswap64`.

State, dependencies, and integration: no state or includes. It supports `contrib/linux-kernel/mem.h` byte-swap helpers.

Risks and test signals: requires GCC/Clang-compatible builtins. Any need for 16-bit or other swap helpers will fail at compile time until added.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/types.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/types.h

Purpose: minimal Linux types shim for user-space compilation of generated kernel zstd sources.

Important behavior: includes `<stddef.h>` and `<stdint.h>` under an include guard, providing `size_t`, `ptrdiff_t`, and fixed-width integer types used by the generated sources.

State, dependencies, and integration: no state. It is a foundational shim included by other fake Linux headers and generated zstd code.

Risks and test signals: real kernel-specific aliases are absent; current generated zstd code uses standard fixed-width types. Compile failures indicate the shim needs to grow.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/unaligned.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/unaligned.h

Purpose: user-space implementation of Linux unaligned access helpers for the kernel-zstd test harness.

Important APIs and control flow: detects little endian from compiler macros and asserts runtime agreement. Implements little-endian and big-endian unaligned get/put helpers for 16/32/64-bit values using `__builtin_memcpy` and byte swaps. Generic macros `__get_unaligned_le/be` and `__put_unaligned_le/be` dispatch by pointed-to type size using `__builtin_choose_expr` or switch, calling `__bad_unaligned_access_size()` for unsupported sizes. `get_unaligned`/`put_unaligned` map to little- or big-endian variants based on host endian.

State, dependencies, and integration: no persistent state. It depends on `assert.h`, `linux/types.h`, GCC extensions, and compiler bswap/memcpy builtins. `mem.h` uses these helpers for zstd memory I/O.

Risks and test signals: `_swap16()` appears to mask nibbles rather than bytes, which would be wrong on big-endian paths for 16-bit conversions. Most CI hosts are little-endian, so big-endian coverage matters. Linux-kernel tests and QEMU big-endian jobs are useful signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/unaligned.h -->
