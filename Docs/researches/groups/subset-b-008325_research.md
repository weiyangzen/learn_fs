# subset-b-008325 Research

Grouped research for the mapped CryFS test scaffolding, CryFS flaky-test tooling, and ecryptfs-utils build/runtime/key-module files. Each section is source-tree aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.cpp

Purpose: implements the `MockFilesystem` constructor/destructor and the `FuseTest` Google Test fixture used by CryFS FUSE integration tests. It centralizes default filesystem mock behavior and supplies helpers that make FUSE-visible files, directories, and file descriptors appear through `lstat`/`fstat`.

Important APIs/functions: `FuseTest::TestFS()` creates a mounted temporary FUSE filesystem; `TempTestFS` owns `TempDir`, `fspp::fuse::Fuse`, and `FuseThread`; static gmock actions `ReturnIsFile`, `ReturnIsFileWithSize`, `ReturnIsFileFstat`, `ReturnIsDir`, and `ReturnDoesntExist` populate `stat` results or throw `FuseErrnoException`.

Control flow: the fixture constructor installs pessimistic `ON_CALL` defaults that throw `EIO` or `ENOENT`, then whitelists `access()` and root metadata. `TempTestFS` starts FUSE in a background thread on construction and stops it in the destructor. Test helpers add repeated expectations for specific paths/descriptors.

State/persistence: state is in-memory only: shared `MockFilesystem`, optional captured `fspp::Context`, temporary mount directory, and static action objects. No persistent files are written except transient mount-directory activity.

Dependencies/integration: depends on gtest/gmock, Boost filesystem, cpp-utils unique/tempdir, and `fspp::fuse::Fuse`. It integrates with the FUSE callback layer by supplying a filesystem factory returning the shared mock.

Risks: defaults intentionally fail, so tests must configure expected operations. Busy FUSE lifecycle issues are delegated to `FuseThread`. Static non-const actions can be affected by global initialization order but are simple constant gmock actions.

Test signals: this is test infrastructure; coverage appears through downstream FUSE tests that mount `TempTestFS` and assert mock calls.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.h

Purpose: declares the CryFS FUSE test fixture and a full Google Mock implementation of `fspp::fuse::Filesystem`.

Important APIs/types: `MockFilesystem` mocks context setup, open/close, stat, truncate, read/write, sync, access, creation/removal, rename, directory reads, timestamps, `statfs`, ownership/mode changes, and symlink operations. `FuseTest` exposes `fsimpl`, `context()`, `TestFS()`, metadata-return helpers, and `OnOpenReturnFileDescriptor()`. Nested `TempTestFS` owns the mounted test filesystem.

Control flow: tests derive from `FuseTest`, configure `fsimpl` expectations, call `TestFS()`, operate on `mountDir()`, and let RAII tear down FUSE.

State/persistence: `FuseTest` keeps a shared mock and optional `fspp::Context`. `TempTestFS` keeps a temporary directory, a `Fuse` object, and the thread wrapper. Lifetime is scoped to the test.

Dependencies/integration: pulls in gtest/gmock, `Filesystem.h`, `FuseErrnoException`, `Fuse`, `Dir`, Boost filesystem, cpp-utils tempdir, and `FuseThread`.

Risks: the mock API mirrors the production filesystem interface, so signature drift breaks many tests. `context()` asserts if FUSE did not call `setContext()`, which is useful but makes initialization ordering visible.

Test signals: no direct tests, but it is the main fixture contract for FUSE behavior tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.cpp

Purpose: implements a small thread wrapper that runs a `fspp::fuse::Fuse` instance in foreground mode during tests.

Important APIs/functions: constructor stores a raw `Fuse*`; `start(mountDir, fuseOptions)` launches a `boost::thread` that calls `runInForeground()`; `stop()` calls `Fuse::stop()` and waits for clean shutdown.

Control flow: `start()` spawns the child thread, busy-waits until `Fuse::running()` reports true, and on Apple sleeps briefly because macFUSE reports readiness early. `stop()` requests shutdown, joins with a 10 second timeout, asserts success, then busy-waits until `running()` is false.

State/persistence: holds only a non-owning pointer and the boost thread. No persistent state.

Dependencies/integration: depends on Boost thread/chrono, Boost filesystem path, cpp-utils assert, and `fspp::fuse::Fuse`.

Risks: busy-wait loops can spin CPU if FUSE never changes state. The raw pointer requires the caller to outlive the thread wrapper. The hard 10 second assertion makes hangs fail fast in tests.

Test signals: exercised indirectly by `FuseTest::TempTestFS` lifecycle.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.h

Purpose: declares the non-copyable helper for running a FUSE instance in a background test thread.

Important APIs/types: `FuseThread(fspp::fuse::Fuse*)`, `start(const boost::filesystem::path&, const std::vector<std::string>&)`, and `stop()`.

Control flow/state: the header defines ownership boundaries: `FuseThread` does not own `_fuse`, but it owns `_child`. Copy and assignment are disabled through cpp-utils macros to avoid double-stop or thread ownership mistakes.

Dependencies/integration: Boost thread/chrono/path, cpp-utils macros, and a forward declaration of `fspp::fuse::Fuse`.

Risks: because the `Fuse*` is raw and non-owning, callers must preserve object lifetime. The class has no destructor, so users must call `stop()` explicitly or embed it in an RAII owner such as `TempTestFS`.

Test signals: no standalone tests; correctness is visible through FUSE test fixture startup/shutdown stability.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseThread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.cpp

Purpose: implements simple byte-buffer backed file objects for tests.

Important APIs/functions: `InMemoryFile::read()` copies a bounded slice from `_data`; `data()`, `size()`, and `fileContentEquals()` expose raw content checks. `WriteableInMemoryFile::write()` extends then overwrites; `sizeUnchanged()` and `regionUnchanged()` compare against original data.

Control flow: reads compute `min(count, data_size - offset)` and copy from `dataOffset()`. Writes call `_extendFileSizeIfNecessary(count + offset)`, allocate a new `Data` object if needed, copy old bytes, then write the caller buffer.

State/persistence: all state is process memory. `WriteableInMemoryFile` snapshots `_originalData` at construction for later assertions. There is no disk persistence.

Dependencies/integration: uses `cpputils::Data`, `fspp::num_bytes_t`, `std::memcpy`, and `std::memcmp`.

Risks: callers must provide valid offsets; subtracting an offset beyond size could underflow depending on `num_bytes_t` behavior. `_extendFileSize()` does not explicitly zero-fill new space beyond whatever `Data(size)` initializes.

Test signals: these helpers support tests that verify read/write offsets, growth, and unchanged regions without touching real files.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.h

Purpose: declares immutable and writable in-memory file helpers for CryFS tests.

Important APIs/types: `InMemoryFile` owns protected `cpputils::Data _data` and exposes `read`, `data`, `size`, and `fileContentEquals`. `WriteableInMemoryFile` adds `write`, `sizeUnchanged`, and `regionUnchanged`, plus private extension helpers and `_originalData`.

Control flow/state: construction moves in a `Data` buffer; the writable subclass uses inheritance to mutate `_data` and keeps an original copy for assertions.

Dependencies/integration: includes cpp-utils `Data` and fspp byte-count types. It is designed to plug into mock read/write tests.

Risks: raw `const void*` exposure lets callers compare or copy data but not safely know lifetime beyond the object. The class is not synchronized.

Test signals: expected to be used in unit tests for file operation semantics; no direct tests in this header.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/OpenFileHandle.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/OpenFileHandle.cpp

Purpose: translation unit for the header-only `OpenFileHandle` RAII helper.

Important APIs/functions: it only includes `OpenFileHandle.h`; all behavior is inline in the header.

Control flow/state: no runtime logic is added here. The file exists so the build can compile or link the test utility as a conventional source if needed.

Dependencies/integration: depends solely on the header.

Risks: minimal; any behavior change lives in the header. A one-line `.cpp` can hide the fact that the class is inline-only.

Test signals: build coverage verifies the header compiles in a separate translation unit.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/OpenFileHandle.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/OpenFileHandle.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/OpenFileHandle.h

Purpose: defines a non-copyable RAII wrapper around a POSIX-style file descriptor for tests.

Important APIs/types: constructors call `::open(path, flags)` or `::open(path, flags, mode)`, preserving `errno` into `errno_` when open fails. `fd()` returns the descriptor, `errorcode()` returns captured errno, and `release()` prevents destructor close.

Control flow: destructor closes any non-negative descriptor. On Apple it sleeps 50 ms after close to allow file-release timing in macOS tests.

State/persistence: state is the descriptor integer and immutable saved errno. It affects real filesystem state only through open/close.

Dependencies/integration: includes `fcntl.h`, `errno.h`, platform `unistd.h` or `io.h`, thread/chrono, and cpp-utils copy prevention.

Risks: `fd()` and `errorcode()` are non-const. `release()` leaks ownership intentionally, so tests must close externally. No retry on interrupted close.

Test signals: supports tests needing deterministic fd cleanup and access to open failure errno.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/OpenFileHandle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/gitversion/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/gitversion/CMakeLists.txt

Purpose: builds and registers the `gitversion-test` executable.

Important APIs/targets: declares `ParserTest.cpp` and `VersionCompareTest.cpp` as sources, creates an executable, links `my-gtest-main`, `googletest`, and `gitversion`, registers it with CTest via `add_test`, and applies local C++14/style-warning helpers.

Control flow/state: no runtime state; it determines build graph and test discovery.

Dependencies/integration: depends on the local `gitversion` library and shared Google Test main library.

Risks: missing helper macros or target names break configuration. The target relies on `my-gtest-main` to provide `main()`.

Test signals: the CTest entry makes parser and comparator regressions visible in normal test runs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/gitversion/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/gitversion/ParserTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/gitversion/ParserTest.cpp

Purpose: provides comprehensive unit tests for `gitversion::Parser::parse`.

Important APIs/functions: each `TEST(ParserTest, ...)` parses a version string into `VersionInfo` and checks `majorVersion`, `minorVersion`, `hotfixVersion`, `isDevVersion`, `isStableVersion`, `gitCommitId`, `versionTag`, and `commitsSinceTag`.

Control flow: tests cover unknown versions, release strings with and without leading zeros, dirty release/dev builds, stable/alpha/rc/beta tags, missing minor/hotfix components, and git describe suffixes like `+20.g0123abcdef.dirty`.

State/persistence: no state beyond local `VersionInfo` values.

Dependencies/integration: includes gtest and `gitversion/parser.h`; validates the parser contract consumed by version display and comparison code.

Risks: expectations preserve string forms for numeric parts, including leading zeros, so changing parser normalization would break tests. The coverage is broad for accepted formats but not focused on invalid-input error handling.

Test signals: direct assertions make version parsing regressions easy to localize.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/gitversion/ParserTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/gitversion/VersionCompareTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/gitversion/VersionCompareTest.cpp

Purpose: unit tests ordering semantics for `gitversion::VersionCompare::isOlderThan`.

Important APIs/functions: fixture helpers `EXPECT_IS_OLDER_THAN` and `EXPECT_IS_SAME_AGE` assert both directions for asymmetric and equal-age comparisons.

Control flow: cases cover numeric version ordering, missing components treated as zero, zero prefixes, tag ordering (`alpha`, `beta`, `rc`, release), milestone-like tags, and dev suffix ordering by commit count while ignoring commit id differences at same count.

State/persistence: no persistent state.

Dependencies/integration: includes gtest and `gitversion/VersionCompare.h`; indirectly relies on parser behavior.

Risks: tag precedence is encoded by examples rather than a table, so new tags may need explicit tests. Dirty markers are treated as same age when commit count matches.

Test signals: CTest runs these through `gitversion-test`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/gitversion/VersionCompareTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/CMakeLists.txt

Purpose: builds the shared static library that supplies a common Google Test/Mock main function.

Important APIs/targets: creates `my-gtest-main` from `my-gtest-main.cpp`, links `googletest` and `cpp-utils`, adds Boost filesystem/system, exposes the current directory as a public include path, and enables C++14/style warnings.

Control flow/state: build-only file.

Dependencies/integration: used by multiple CryFS test executables that need one consistent `main()` and access to `get_executable()`.

Risks: because the library is static and public-includes `.`, duplicate symbols would occur if a test also defines `main()`.

Test signals: all linked test targets depend on this target building successfully.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.cpp

Purpose: implements the common test executable entrypoint and records the executable path for tests.

Important APIs/functions: `get_executable()` returns a stored `boost::filesystem::path`; `main()` stores `argv[0]`, initializes Google Mock/Test, and returns `RUN_ALL_TESTS()`.

Control flow: executable path is stored in an anonymous-namespace `boost::optional`. `get_executable()` asserts it was initialized before use. Google Mock initialization covers Google Test initialization.

State/persistence: process-global optional path; no persistence.

Dependencies/integration: gmock/gtest, Boost optional/filesystem, and cpp-utils assert. Linked into test executables via `my-gtest-main`.

Risks: `argv[0]` may be relative depending on invocation. Global state is initialized once per process and not thread-protected, but test startup is single-threaded.

Test signals: every test executable linked against this library validates basic startup.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.h -->
# sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.h

Purpose: exposes the shared test executable path accessor.

Important APIs/types: declares `const boost::filesystem::path& get_executable();`.

Control flow/state: callers receive a reference to process-global state set by `main()`.

Dependencies/integration: includes Boost filesystem path and is public through the `my-gtest-main` target.

Risks: invalid to call before the common `main()` initializes the optional path, though normal linked test executables satisfy that.

Test signals: compile-time coverage from tests including this header.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/my-gtest-main/my-gtest-main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/CMakeLists.txt

Purpose: builds and registers the `parallelaccessstore-test` executable.

Important APIs/targets: uses `ParallelAccessBaseStoreTest.cpp` and `DummyTest.cpp`, links `my-gtest-main`, `googletest`, and `parallelaccessstore`, registers with CTest, and applies style/C++14 helpers.

Control flow/state: build graph only.

Dependencies/integration: ensures the `parallelaccessstore` library can be included/linked in the test suite.

Risks: current source tests are skeletal, so the target mainly catches build/interface failures rather than behavior regressions.

Test signals: `DummyTest` guarantees at least one gtest case; include-only test catches header compile errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/DummyTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/DummyTest.cpp

Purpose: supplies a minimal Google Test case for the parallel access store test executable.

Important APIs/functions: `TEST(Dummy, DummyTest)` has an empty body and always passes if the binary starts.

Control flow/state: no state or assertions.

Dependencies/integration: includes gtest; provides a test case so CTest/gtest output is non-empty.

Risks: it provides no behavioral coverage and can mask that the suite has not yet implemented real tests.

Test signals: useful only as a smoke signal that the executable links and runs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/DummyTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/ParallelAccessBaseStoreTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/ParallelAccessBaseStoreTest.cpp

Purpose: compile-only test for `parallelaccessstore/ParallelAccessBaseStore.h`.

Important APIs/functions: includes the production header and contains no test body.

Control flow/state: no runtime behavior.

Dependencies/integration: validates that the header is self-contained enough to compile in a test translation unit and that the test target can link the library.

Risks: does not exercise any `ParallelAccessBaseStore` behavior. Header-only compilation can still miss template instantiation or runtime concurrency issues.

Test signals: build failure is the only signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/parallelaccessstore/ParallelAccessBaseStoreTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/tools/detect-flaky-tests.py -->
# sources/security-integrity/cryfs/tools/detect-flaky-tests.py

Purpose: standalone Python/uv tool for detecting flaky Rust tests by building once and then running `cargo test` repeatedly with logs, adaptive timeouts, and optional Rich TUI display.

Important APIs/types/functions: `parse_args`, `repo_root`, `run_cargo`, `run_all`, `_setup_log_dir`, `Display`, `PlainDisplay`, `TuiDisplay`, `ReaderState`, `LogBuffer`, and `StatusState`. Constants define first-run timeout, subsequent timeout formula, log directory, refresh rate, reader polling, and process kill grace periods.

Control flow: `main()` validates POSIX, parses `--plain` and run count, creates `.flaky-runs/<timestamp>/`, forces `RUST_BACKTRACE=1` unless already more verbose, selects TUI/PTY only for interactive stdout, then calls `run_all()`. `run_all()` executes `cargo test --no-run` once, then loops N `cargo test` invocations. `run_cargo()` starts cargo in a new session, streams stdout/stderr to a reader thread, logs output, and kills the entire process group on timeout or interrupt.

State/persistence: persists `build.log`, `run-N.log`, and a best-effort `.flaky-runs/latest` symlink. In-memory status tracks elapsed durations for adaptive timeouts and display.

Dependencies/integration: Python 3.9+, uv PEP 723 metadata, Rich, POSIX process groups, PTYs, `cargo`, and CryFS repo root detection by `Cargo.toml`.

Risks: POSIX-only; PTY/log reader behavior is carefully handled but still may warn if descendants inherit pipes. It kills process groups, so forwarded cargo commands must not intentionally share unrelated processes in the same session. Logs can include test output secrets.

Test signals: the tool is itself a test harness; failures are build failure, first failing repeated run, timeout, reader error, or all-runs-success summary.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/tools/detect-flaky-tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/Makefile.am

Purpose: top-level Automake file for ecryptfs-utils distribution and recursive builds.

Important APIs/targets: sets foreign Automake mode with bzip2 dist, `ACLOCAL_AMFLAGS=-I m4`, extensive `MAINTAINERCLEANFILES`, `SUBDIRS = doc src po tests`, `EXTRA_DIST = autogen.sh`, installs `README`, and ensures `m4` exists in `dist-hook`.

Control flow/state: drives recursive build and distribution packaging.

Dependencies/integration: consumed by Autotools generated Makefiles and aligned with `configure.ac` subdir configuration.

Risks: `MAINTAINERCLEANFILES` includes generated Autotools files and Debian directory, so maintainer-clean can remove packaging scaffolding. Recursive `SUBDIRS` assumes all configured directories exist.

Test signals: `make dist`, maintainer-clean, and recursive build success validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/autogen.sh -->
# sources/security-integrity/ecryptfs-utils/autogen.sh

Purpose: bootstraps Autotools and intltool generated files.

Important APIs/functions: runs `autoreconf -i -v -f` and `intltoolize --copy --force` under `sh -e`.

Control flow/state: stops at first failure; writes generated configure/build support files into the working tree.

Dependencies/integration: requires autoreconf and intltoolize; used by Debian `dh_autoreconf`, release scripts, and developers.

Risks: force mode overwrites generated files. Tooling versions affect generated output.

Test signals: success is prerequisite for `./configure` in fresh checkouts.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/configure.ac -->
# sources/security-integrity/ecryptfs-utils/configure.ac

Purpose: Autoconf configuration script for ecryptfs-utils version 104.

Important APIs/macros: initializes package/config headers, libtool, compiler, gettext/intltool, Python/SWIG, and many feature switches: NSS, pywrap, OpenSSL, pkcs11-helper, TSPI, GPG, PAM, GUI, docs/docs-gen, tests, and mudflap. Defines `ECRYPTFS_DEFAULT_KEY_MOD_DIR`, substitutes library flags and install directories, and emits Makefiles for doc, src, key modules, daemon, desktop, PAM, SWIG, tests, and po.

Control flow: options default mostly to detect/no/yes depending on feature. Dependency checks fail explicitly when a requested feature is missing. Docs generation requires TeX/postscript tools. Kernel version support is not checked here, but `/dev/ecryptfs` support is a daemon runtime check.

State/persistence: writes generated `config.h`, Makefiles, pkg-config file, and configured desktop files.

Dependencies/integration: keyutils is mandatory; NSS can become crypto backend; OpenSSL, pkcs11-helper, TrouSerS, GPGME, PAM, GTK, Python, SWIG, gettext, and intltool are optional/conditional.

Risks: old shell tests use `==`, which is not portable to all `/bin/sh` implementations. Python wrapper targets are Python 2-era. Feature defaults influence security surface, especially key modules and PAM.

Test signals: configure-time dependency failures, conditional build coverage, and generated Makefiles.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/debian/rules -->
# sources/security-integrity/ecryptfs-utils/debian/rules

Purpose: Debian packaging rules using debhelper.

Important APIs/targets: default rule invokes `dh --with autoreconf,python2`; overrides run `autogen.sh`, configure with static build, NSS, PAM, disabled GUI/OpenSSL/PKCS11/TSPI/GPG, optional TPM flags on non-s390, install PAM config, remove useless `.pyc/.la/.a`, gzip debs, set setuid bit on `mount.ecryptfs_private`, strip translation marker from `ecryptfs-record-passphrase`, and create debug package.

Control flow/state: packaging modifies staged `debian/tmp` and `debian/ecryptfs-utils` trees.

Dependencies/integration: Debian build tools, dpkg-buildflags, python2 debhelper addon, pam-auth-update file, and package install manifests.

Risks: `chmod 4755` is a security-sensitive packaging decision. `--fail-missing` makes packaging strict. Python 2 dependency is obsolete in modern distributions.

Test signals: Debian package build, install tree validation, and lintian/security review.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/doc/Makefile.am

Purpose: Automake documentation root.

Important APIs/targets: recurses into `manpage`, installs/distributes FAQ HTML and mount-private text, and conditionally installs PKCS11 helper documentation when `BUILD_PKCS11_HELPER` is enabled.

Control flow/state: `dist_doc_DATA`, `dist_noinst_DATA`, `dist_html_DATA`, and `dist_pkgdata_DATA` decide install/distribution behavior.

Dependencies/integration: controlled by configure conditionals and used by `make dist`.

Risks: PKCS11 doc install changes with build feature flags, which can affect package contents.

Test signals: `make distcheck` and docs install checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/beginners_guide/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/doc/beginners_guide/Makefile.am

Purpose: builds, packages, and optionally installs the eCryptfs beginner guide.

Important APIs/targets: `FILENAME=ecryptfs_beginners_guide`; `final-hook` creates a `final` directory containing HTML assets and PDF; tarball hook packages it; `BUILD_DOCS` installs `final/*`; `BUILD_DOCS_GEN` enables regeneration and clean rules.

Control flow/state: LaTeX produces DVI, DVIPS produces PS, PS2PDF produces PDF, and latex2html produces HTML. Generated artifacts are included in distributions so users need not regenerate docs.

Dependencies/integration: configure supplies `TAR`, `PS2PDF`, `DVIPS`, `LATEX2HTML`, and `LATEX` when docs generation is enabled.

Risks: recipes prefixed with `-` ignore generation failures in several places, which may hide broken docs. Generated `final` content can become stale.

Test signals: docs generation, `make dist`, and package docs install.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/beginners_guide/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/design_doc/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/doc/design_doc/Makefile.am

Purpose: builds and packages the eCryptfs design document.

Important APIs/targets: tracks TeX sources, diagrams, EPS files, generated TOC, final directory, and tarball. `final-hook`, PDF/PS/DVI/HTML targets, and clean rules mirror the beginner guide but with stricter commands in some recipes.

Control flow/state: generated PDF and HTML are copied into `final`; optional install controlled by `BUILD_DOCS`, regeneration by `BUILD_DOCS_GEN`.

Dependencies/integration: relies on LaTeX, DVIPS, PS2PDF, latex2html, and tar from configure.

Risks: diagram sources and generated EPS/HTML/PDF can drift. Unlike the beginner guide, some commands are not ignored, so docs-gen failures may stop builds.

Test signals: docs-gen and dist build validate this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/design_doc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/manpage/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/doc/manpage/Makefile.am

Purpose: installs and distributes ecryptfs-utils manual pages.

Important APIs/targets: `dist_man_MANS` lists section 1, 7, and 8 man pages for mount helpers, utilities, PAM integration, setup/recovery, passphrase wrapping, and stat/verify commands.

Control flow/state: Automake handles install and distribution of listed man pages.

Dependencies/integration: configured as `doc/manpage/Makefile` and recursed from `doc/Makefile.am`.

Risks: man page list must stay synchronized with installed utilities; stale entries break dist/install.

Test signals: `make install`, `make distcheck`, and packaging file checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/doc/manpage/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/po/POTFILES.in -->
# sources/security-integrity/ecryptfs-utils/po/POTFILES.in

Purpose: gettext/intltool input list for translatable files.

Important APIs/data: includes desktop files, `ecryptfs-record-passphrase`, and several shell utilities such as mount/private/recover/rewrite/setup/swap/umount.

Control flow/state: gettext tooling scans these paths to generate/update translation templates.

Dependencies/integration: used by `AM_GLIB_GNU_GETTEXT` and intltool during build/dist.

Risks: missing files lead to untranslated user-facing strings; stale paths break translation updates.

Test signals: `make update-po` or distribution translation generation.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/po/POTFILES.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/build-full-tarball.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/build-full-tarball.sh

Purpose: legacy release helper that packages userspace and kernel eCryptfs trees into a dated tarball.

Important APIs/commands: copies `ecryptfs-utils-git` and `ecryptfs-kernel-git`, bootstraps each with aclocal/libtoolize/automake/autoconf, symlinks kernel `src`, removes build/VCS cruft, creates `.tar.bz2`, and removes the staging tree.

Control flow/state: destructive cleanup happens in copied staging directories and final tarball is written in the caller directory.

Dependencies/integration: assumes sibling git trees, kernel version directories, Autotools, and tar.

Risks: many unquoted variables and broad `find ... -exec rm -rf` patterns. Safe only in expected legacy release layout.

Test signals: successful tarball build and clean staged contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/build-full-tarball.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/build-ubuntu.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/build-ubuntu.sh

Purpose: builds an Ubuntu source/binary package from a generated upstream release tarball.

Important APIs/commands: runs `release.sh --nosign`, moves `*.orig.tar.gz` into a fresh `ubuntu` directory, extracts it, copies Debian packaging from the original checkout, and invokes `debuild -uc -us`.

Control flow/state: deletes/recreates sibling `ubuntu`, moves release artifacts, and builds without signing.

Dependencies/integration: Debian packaging tools, `release.sh`, and expected directory naming.

Risks: destructive `rm -rf ubuntu`; assumes current working directory basename and tarball naming.

Test signals: successful `debuild` output.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/build-ubuntu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/current-version.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/current-version.sh

Purpose: defines a shell environment variable for the current eCryptfs kernel version used by legacy scripts.

Important APIs/data: exports `ECRYPTFS_VERSION="2.6.20-rc2-mm1"`.

Control flow/state: sourced by other scripts; no standalone behavior.

Dependencies/integration: used by `rebuild-patches.sh`, `sync-kernel.sh`, and `test.sh`.

Risks: hard-coded old kernel version must be updated manually; `test.sh` supplies a fallback only if empty.

Test signals: scripts echo/use the expected version.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/current-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/delete-cruft.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/delete-cruft.sh

Purpose: removes generated/build/VCS cruft from an ecryptfs-utils working tree after validating it looks like the expected project.

Important APIs/commands: calls `scripts/validate-dir.sh`, removes `.git`, generated Makefiles, Debian old package dirs, libtool/build artifacts, reject/orig/temp files, patch directories, `nohup.out`, `cscope.out`, and `gui` directories.

Control flow/state: aborts if validation fails; otherwise performs many destructive removals in the current tree.

Dependencies/integration: used by tarball/release workflows.

Risks: broad `find -exec rm -rf` and unquoted patterns are dangerous outside the expected directory. Validation is shallow and only checks for marker files.

Test signals: directory validation and resulting clean tree.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/delete-cruft.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/make.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/make.sh

Purpose: interactive legacy installer for building and installing both kernel and userspace eCryptfs components.

Important APIs/commands: prints install locations and mount instructions, warns if not root, waits for ENTER, builds `ecryptfs-kernel`, installs it, then configures/builds/installs `ecryptfs-util --prefix=/usr`.

Control flow/state: changes into fixed sibling directories and runs configure/make/make install. It writes to system directories when run as root.

Dependencies/integration: assumes combined kernel/userspace source layout and a compatible system build environment.

Risks: root install script with no dry-run, hard-coded old paths, and minimal error recovery. Uses bash-style redirection/tests under `/bin/sh`.

Test signals: successful configure/build/install; not suitable as automated unit test.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/make.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/rebuild-patches.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/rebuild-patches.sh

Purpose: regenerates backpatch diffs from the current kernel eCryptfs version to legacy kernel directories.

Important APIs/commands: sources `current-version.sh`, cleans multiple kernel version trees, copies `ecryptfs-kernel-git`, swaps `src` to version-specific directories, runs `diff -Naur`, and writes backpatch files under `backpatches/`.

Control flow/state: destructive cleanup and temporary clone directories in the caller's parent layout.

Dependencies/integration: assumes `ecryptfs-kernel-git` with version directories 2.6.16/17/18 and `$ECRYPTFS_VERSION`.

Risks: repetitive unquoted `rm -rf`, hard-coded kernel versions, and no `set -e`, so partial failures can still produce misleading patches.

Test signals: generated patch files and clean temporary directories.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/rebuild-patches.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/release.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/release.sh

Purpose: creates and optionally signs an upstream release tarball and prints follow-up Launchpad/Debian release instructions.

Important APIs/functions: `error()` aborts; checks `debian/changelog` contains `unreleased`; extracts current version; runs autogen/configure/make dist; renames tarball to Debian orig format; optionally signs with GPG; tags with bzr; builds source package with copied Debian directory; prints next-version commands.

Control flow/state: writes tarballs in parent directory, mutates bzr tags, extracts release tarball, and may run `debuild -S`.

Dependencies/integration: Autotools, GPG, Bazaar, Debian devscripts, Launchpad workflow.

Risks: old bzr/Launchpad assumptions, version extraction by sed, and signing/tagging side effects. `--nosign` exits before tagging/package steps.

Test signals: successful tarball, signature, bzr tag, and source package.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/release.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/sync-kernel.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/sync-kernel.sh

Purpose: synchronizes eCryptfs kernel code from a Linux tree into legacy ecryptfs-kernel-git version directories.

Important APIs/commands: sources current version, copies `linux-git/fs/ecryptfs/*.[ch]`, applies a netlink patch and backpatches to create 2.6.18/17/16 directories.

Control flow/state: removes old kernel version directories, renames/copies `src`, and applies patches in sequence.

Dependencies/integration: requires sibling `linux-git`, `ecryptfs-kernel-git`, patches, and current version directory.

Risks: destructive to kernel mirror directories; no robust error handling around patch failures.

Test signals: patched version directories and patch command success.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/sync-kernel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/test.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/test.sh

Purpose: prints the configured eCryptfs kernel version for legacy scripts.

Important APIs/commands: sources `./current-version.sh`, falls back to `2.6.18-rc4-mm2` if `ECRYPTFS_VERSION` is empty, then echoes it.

Control flow/state: read-only except environment variable assignment in the shell process.

Dependencies/integration: smoke helper for current-version behavior.

Risks: uses bash-style `==` under `/bin/sh` on some platforms. Relative sourcing requires execution from the scripts directory.

Test signals: echoed version.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/validate-dir.sh -->
# sources/security-integrity/ecryptfs-utils/scripts/validate-dir.sh

Purpose: shallow safety check that the current directory looks like an ecryptfs-utils tree.

Important APIs/commands: checks marker files `AUTHORS COPYING ChangeLog INSTALL Makefile.am NEWS README THANKS configure`; exits 1 on first missing file, otherwise exits 0.

Control flow/state: read-only; prints found/missing messages.

Dependencies/integration: called before destructive cleanup by `delete-cruft.sh`.

Risks: marker-file validation can be spoofed and does not verify paths before deletion. Requires generated `configure` to exist.

Test signals: shell exit code and printed validation success.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/scripts/validate-dir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/Makefile.am

Purpose: recursive Automake root for ecryptfs-utils source components.

Important APIs/targets: `SUBDIRS = key_mod libecryptfs utils daemon desktop include pam_ecryptfs libecryptfs-swig`; maintainer-clean removes generated Makefile input.

Control flow/state: build order ensures key modules, library, utilities, daemon, desktop files, headers, PAM module, and SWIG wrapper are included.

Dependencies/integration: subdirectories are conditionally populated by their own Makefiles/configure conditionals.

Risks: unconditional subdirs must be configured even when features are disabled internally. Build order can matter for libraries consumed by utilities/daemon.

Test signals: recursive source build and install.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/daemon/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/daemon/Makefile.am

Purpose: builds the `ecryptfsd` userspace daemon.

Important APIs/targets: `bin_PROGRAMS=ecryptfsd`; source `main.c`; CFLAGS include libgcrypt/keyutils flags; LDADD links `libecryptfs.la`, keyutils, and libgcrypt.

Control flow/state: Automake compiles and links the daemon into the installable binary set.

Dependencies/integration: depends on built libecryptfs and kernel key/messaging libraries.

Risks: daemon link flags must match configure substitutions; missing libgcrypt variable detection would break builds.

Test signals: daemon compile/link and any runtime daemon tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/daemon/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/daemon/main.c -->
# sources/security-integrity/ecryptfs-utils/src/daemon/main.c

Purpose: implements `ecryptfsd`, the userspace daemon that responds to eCryptfs kernel module requests over `/dev/ecryptfs`.

Important APIs/functions: `prompt_callback()` runs an external prompt program and reads password output; `daemonize()` double-forks, redirects stdio to `/dev/null`, closes fds, and ignores initial signals; `sigterm_handler()` exits through `ecryptfsd_exit()`; `main()` parses options, validates kernel version, configures daemon mode/chroot/pidfile/signals, initializes messaging, sends `ECRYPTFS_MSG_HELO`, runs `ecryptfs_run_daemon()`, then sends quit/cleans up.

Control flow: command-line options include pidfile, foreground, chroot, prompt program, version, and help. The daemon refuses kernels lacking miscdev support when version retrieval succeeds. It disables core dumps to avoid secret leakage. A global messaging context is protected by `mctx_mux` around state changes and signal-driven exit.

State/persistence: optional pidfile is written/unlinked; environment `TERM_DEVICE` records tty; daemon may chroot; syslog records events. Messaging state persists in `mctx`.

Dependencies/integration: libc/POSIX process APIs, pthread, syslog, `config.h`, and libecryptfs messaging/key prompt APIs.

Risks: `prompt_callback()` waits for child completion before reading pipe output, so large prompt output could deadlock, though password output should be small. `daemonize()` loops `dup2(null, 0)` for fd 0..2, likely intending `dup2(null, fd)`. Signal handler performs mutex and complex cleanup, which is not async-signal-safe.

Test signals: daemon startup against `/dev/ecryptfs`, option parsing, pidfile cleanup, and kernel message round-trip tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/daemon/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/desktop/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/desktop/Makefile.am

Purpose: builds and installs desktop integration files and the passphrase-record helper script.

Important APIs/targets: installs `ecryptfs-record-passphrase` under ecryptfs-utils data root; transforms `.desktop.in` files into `.desktop` files through intltool; installs desktop entries under the same data root.

Control flow/state: Automake/intltool generate translated desktop files.

Dependencies/integration: configure-generated intltool desktop rule and translation domain.

Risks: install location is application data root, not standard global applications directory, so downstream packaging may move/copy. Desktop entry Exec paths are absolute `/usr/bin`.

Test signals: install tree and intltool generation.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/desktop/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-mount-private.desktop.in -->
# sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-mount-private.desktop.in

Purpose: desktop launcher metadata for accessing an encrypted private directory.

Important data: translated name/generic name "Access Your Private Data", `Exec=/usr/bin/ecryptfs-mount-private`, `Terminal=true`, application type, System/Security categories, and Ubuntu gettext domain.

Control flow/state: no code; desktop environment launches the command in a terminal.

Dependencies/integration: processed by intltool and installed by desktop Makefile.

Risks: absolute `/usr/bin` path must match package install. Terminal prompt behavior is user-visible.

Test signals: desktop file validation and launcher execution.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-mount-private.desktop.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-setup-private.desktop.in -->
# sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-setup-private.desktop.in

Purpose: desktop launcher metadata for setting up an encrypted private directory.

Important data: translated name/generic name "Setup Your Encrypted Private Directory", `Exec=/usr/bin/ecryptfs-setup-private`, `Terminal=true`, Settings/Security categories, and Ubuntu gettext domain.

Control flow/state: no code; launches setup utility in a terminal.

Dependencies/integration: intltool, desktop Makefile, and installed utility path.

Risks: absolute path and terminal interaction must match distro packaging. Setup utility handles sensitive passphrases, so launcher should not suppress terminal prompts.

Test signals: desktop-file validation and manual launcher test.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/desktop/ecryptfs-setup-private.desktop.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/include/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/include/Makefile.am

Purpose: installs public and private headers.

Important APIs/targets: `include_HEADERS = ecryptfs.h`; `dist_noinst_HEADERS = decision_graph.h`.

Control flow/state: public API header is installed; decision graph header is distributed but not installed.

Dependencies/integration: used by libecryptfs, utilities, daemon, key modules, and SWIG wrapper.

Risks: exposing `ecryptfs.h` means ABI/API compatibility matters. `decision_graph.h` remains internal but is shared across source subdirs.

Test signals: install checks and downstream compile.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/include/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/include/decision_graph.h -->
# sources/security-integrity/ecryptfs-utils/src/include/decision_graph.h

Purpose: declares the internal decision-graph structures that drive interactive and option-file mount/key-module configuration.

Important APIs/types: `val_node`, `transition_node`, `param_node`, `prompt_elem`, flags for prompt behavior/validation/defaults/transitions, and functions for adding/dumping graph nodes, setting exits, inserting name/value params, and evaluating parameter trees.

Control flow model: a `param_node` represents a mount option prompt/value; transitions choose next nodes based on values or default matches and may run `trans_func`. `val_node` works as a stack of generated mount options or intermediate values. Return tokens such as `DEFAULT_TOK`, `MOUNT_ERROR`, and `WRONG_VALUE` steer traversal.

State/persistence: graph nodes hold mutable `val`, defaults, suggestions, flags, and transition arrays; no persistence by themselves.

Dependencies/integration: included by key modules and libecryptfs decision graph implementation. It references `ecryptfs_ctx` and name/value pairs.

Risks: fixed-size arrays (`MAX_NUM_MNT_OPT_NAMES`, `MAX_NUM_TRANSITIONS`) can constrain modules. Comments warn structures are shared kernel/userspace width-sensitive, though these decision graph structs are mostly userspace.

Test signals: mount option parsing and key-module decision graph traversal tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/include/decision_graph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/include/ecryptfs.h -->
# sources/security-integrity/ecryptfs-utils/src/include/ecryptfs.h

Purpose: primary public userspace header for ecryptfs-utils and libecryptfs.

Important APIs/types: defines version feature flags, sizes/constants for salts/signatures/keys/messages/tags, auth token structures shared with the kernel, password/private-key/session-key structures, messaging contexts, key module operation table, key module state, mount context, crypt stat view, and many libecryptfs function prototypes.

Control flow contracts: callers use version checks to choose mount features; decision graph functions gather mount/key options; passphrase/key-module functions insert auth tokens into kernel keyrings; messaging functions initialize `/dev/ecryptfs`, send messages, and run the daemon; wrapping/unwrapping helpers manage wrapped passphrase files.

State/persistence: structures encode key material, signatures, salts, encrypted/decrypted session keys, key module blobs, file metadata, and messaging state. Some APIs operate on keyrings, rc files, signature caches, wrapped passphrase files, shared memory/semaphores, and `/proc` mount data.

Dependencies/integration: libc, Linux types, pthread, termios, syslog, keyutils-backed libecryptfs implementation, daemon, utilities, PAM, key modules, and SWIG wrapper.

Risks: packed auth token layout must match kernel ABI and architecture width expectations. Many APIs pass raw pointers and fixed-size buffers containing secrets; callers must zero/free carefully. Default salt constants and default key module affect security posture.

Test signals: broad compile coverage plus runtime mount/keyring/messaging/passphrase wrapping tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/include/ecryptfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/key_mod/Makefile.am

Purpose: builds installable eCryptfs key module plugins.

Important APIs/targets: always builds passphrase module; conditionally builds OpenSSL, pkcs11-helper, TSPI, and GPG modules. Each libtool module uses `-module -avoid-version -shared` and links relevant provider libraries. Install hook removes `.la` and `.a`; uninstall removes `.so`.

Control flow/state: configure conditionals control plugin set. Modules install under `ecryptfskeymoddir`.

Dependencies/integration: OpenSSL, pkcs11-helper, TrouSerS, GPGME, libgcrypt, and libecryptfs plugin loader contract.

Risks: plugin ABI is the `get_key_mod_ops()` function and operation table; mismatches fail at runtime. Removing static/libtool files is intentional for runtime plugin cleanliness.

Test signals: conditional build/link/install of each enabled plugin and plugin loading by libecryptfs.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_gpg.c -->
# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_gpg.c

Purpose: partial/disabled GPGME key module skeleton for eCryptfs public-key support.

Important APIs/functions: defines `key_mod_gpg`, stub serialization/deserialization, key metadata, generate/encrypt/decrypt stubs, GPG key listing transition functions, `gpg_transition`, `ecryptfs_gpg_init`, and `get_key_mod_ops()`.

Control flow: entering the subgraph allocates a GPGME context and starts key listing. `tf_gpg_keysig` iterates keys/subkeys and fills transition values with subkey key IDs. However `ecryptfs_gpg_init()` returns `-EINVAL` after setting alias, explicitly disabling the module.

State/persistence: intended state includes GPGME context, selected key signature, eCryptfs signature, and serialized blob. Current serialize/deserialize stubs do not persist meaningful data.

Dependencies/integration: GPGME, passwd/getuid, syslog, decision graph, ecryptfs key module ops.

Risks: many TODOs/stubs, incomplete memory cleanup for GPGME keys, and disabled init make it nonfunctional. If enabled without completion, encryption/decryption would falsely succeed or fail unpredictably.

Test signals: build-only when `--enable-gpg`; no meaningful runtime behavior until implemented.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_gpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_openssl.c -->
# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_openssl.c

Purpose: OpenSSL-backed public-key key module for eCryptfs, using PEM RSA private keys to wrap/unwrap session keys and generate key signatures.

Important APIs/functions: `ecryptfs_openssl_serialize/deserialize`, `ecryptfs_openssl_generate_signature`, key file mkdir/write/read helpers, `ecryptfs_openssl_get_key_sig`, `ecryptfs_openssl_generate_key`, `ecryptfs_openssl_encrypt`, `ecryptfs_openssl_decrypt`, decision-graph transition functions for keyfile/passphrase/passphrase-file, generation subgraph functions, `ecryptfs_openssl_init`, and `get_key_mod_ops()`.

Control flow: decision graph captures PEM key path and passphrase, serializes them into the key module blob, inserts the key module auth token into the keyring, pushes `ecryptfs_sig=<sig>` and a `max_key_bytes` option. Encryption/decryption re-read the RSA private key from the serialized path/passphrase and use RSA OAEP padding. Key generation writes a 1024-bit encrypted RSA private key under a suggested `~/.ecryptfs/pki/openssl/key.pem`.

State/persistence: persistent key material lives in the PEM key file. Runtime state includes serialized path/passphrase blob, suggested path strings, and mount option stack values. Passphrases are heap strings and not consistently zeroed before free.

Dependencies/integration: OpenSSL PEM/RSA/ERR/ENGINE APIs, syslog, passwd home lookup, decision graph, libecryptfs keyring APIs.

Risks: 1024-bit RSA is obsolete. OpenSSL APIs used are legacy. Serialized blobs contain passphrases. `tf_ssl_passwd_fd` returns `ENOSYS` without negation, likely inconsistent error semantics. File permissions rely on recursive mkdir mode and OpenSSL file write behavior.

Test signals: plugin build with OpenSSL enabled, key generation, keyring insertion, and mount with OpenSSL key module.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_openssl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_passphrase.c

Purpose: built-in passphrase key module that gathers passphrase/salt values and inserts a passphrase auth token into the kernel keyring.

Important APIs/functions: `tf_passwd`, `tf_pass_file`, `tf_salt`, static `passphrase_param_nodes`, `passphrase_transition`, `ecryptfs_passphrase_get_param_subgraph_trans_node`, `ecryptfs_passphrase_init`, `get_key_mod_ops`, and `passphrase_get_key_mod_ops`.

Control flow: decision graph chooses direct passphrase, passphrase file, or passphrase fd. Password and salt are pushed on the value stack; `tf_salt` defaults salt if absent, converts hex salt to bytes, calls `ecryptfs_add_passphrase_key_to_keyring`, and pushes `ecryptfs_sig=<sig>` for mount options.

State/persistence: uses transient heap strings and parsed option files/fds. It inserts auth token state into the user session keyring; no module blob persistence.

Dependencies/integration: libecryptfs stack/name-value helpers, `parse_options_file`, `free_name_val_pairs`, salt conversion, keyring insertion, syslog.

Risks: default salt is allowed and can weaken passphrase-derived key uniqueness. Secrets are freed but not always wiped. File descriptor mode trusts caller-provided fd integer.

Test signals: mount helper passphrase flows, passphrase file/fd parsing, keyring insertion, and default salt warnings in higher layers.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_passphrase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_pkcs11_helper.c -->
# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_pkcs11_helper.c

Purpose: PKCS#11 smart-card/token key module using pkcs11-helper and OpenSSL X.509/RSA APIs.

Important APIs/functions: serialization/deserialization of `pkcs11h_data`, token/PIN prompt hooks, public-key extraction from certificate blobs, key signature generation, RSA encrypt/decrypt, certificate ID enumeration, key processing into eCryptfs keyring, provider/global/key decision graph transition functions, `.ecryptfsrc.pkcs11` parser, init/finalize, and `get_key_mod_ops()`.

Control flow: init sets pkcs11-helper log/token/PIN hooks, default protected auth, then parses `~/.ecryptfsrc.pkcs11` for global and provider settings. The key subgraph captures serialized certificate id, passphrase source, and optional X.509 PEM file. Processing creates a pkcs11-helper certificate, loads a certificate blob if needed, serializes module state, inserts a key module auth token, and pushes `ecryptfs_sig=<sig>`. Encryption uses the certificate public RSA key; decryption asks pkcs11-helper to decrypt with the token private key.

State/persistence: stores serialized PKCS#11 id, certificate DER blob, and passphrase in the key module blob. Reads user rc file for providers. PINs may come from callback or stored passphrase.

Dependencies/integration: pkcs11-helper, OpenSSL X509/RSA/BIO, libecryptfs decision graph/keyring, syslog, passwd home lookup.

Risks: RSA encryption uses `RSA_PKCS1_PADDING` rather than OAEP. Some allocations use `sizeof(*ctx)` where the intended struct is larger/different, suggesting memory sizing bugs in provider/key context allocation. Serialized blobs can contain passphrases. `.ecryptfsrc.pkcs11` parsing errors are mostly ignored in init.

Test signals: build with pkcs11-helper enabled, rc-provider parsing, token enumeration, PIN prompt callback, keyring insertion, and real token encryption/decryption.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_pkcs11_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_tspi.c -->
# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_tspi.c

Purpose: TrouSerS/TPM key module that seals/unseals eCryptfs session keys using TPM-stored keys identified by UUID.

Important APIs/functions: UUID serialization/deserialization and parsing, TPM public-key signature generation, `ecryptfs_tspi_get_key_sig`, connection ticket pool (`grab_ticket`/`release_ticket`), `ecryptfs_tspi_encrypt`, `ecryptfs_tspi_decrypt`, parameter handling for `tspi_uuid`, `ecryptfs_tspi_init/get_params/get_blob/destroy/finalize`, and `get_key_mod_ops()`.

Control flow: init builds a free list of up to 10 connection tickets. Blob generation converts a hex UUID string into `TSS_UUID`. Encryption/decryption deserialize UUID, grab a connected TSS context ticket, load the SRK with the well-known secret, load the user key by UUID, and seal/unseal data. Decrypt caches loaded key handles in a global UUID mapper. Finalize waits briefly for used tickets, closes initialized contexts, and reports busy if tickets remain.

State/persistence: persistent TPM keys live in TrouSerS persistent storage. Runtime state includes ticket lists/counters, connected TSS contexts, cached key handles, static SRK handles/policies, and serialized UUID blobs.

Dependencies/integration: TrouSerS TSS APIs, pthread mutexes, OpenSSL SHA1, ecryptfs key module ops.

Risks: ticket list manipulation appears to assume simple head movement and may mishandle non-head used tickets. Global encrypt/decrypt locks serialize operations. SRK well-known secret is assumed. Error paths may leak TSS objects or allocated mapper entries.

Test signals: requires TPM/TrouSerS environment; build with `--enable-tspi`, UUID parameter parsing, signature generation, and seal/unseal integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_tspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/Makefile.am

Purpose: conditionally builds Python SWIG bindings for libecryptfs.

Important APIs/targets: under `BUILD_PYWRAP`, generates `libecryptfs_wrap.c` from `libecryptfs.i`, installs `libecryptfs.py`, builds `_libecryptfs.la`, includes SWIG Python CPP flags and ecryptfs headers, and links against built `libecryptfs.la`.

Control flow/state: SWIG generation is a build step; wrapper C is a built source.

Dependencies/integration: configure must find Python and SWIG; Python package imports `_libecryptfs`.

Risks: Python 2-era build macros and generated wrapper may not work on modern Python. Direct link path to `../libecryptfs/.libs/libecryptfs.la` is build-tree specific.

Test signals: Python wrapper build/import and calling exposed functions.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/libecryptfs.py -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/libecryptfs.py

Purpose: SWIG-generated Python proxy module for a small subset of libecryptfs.

Important APIs/functions: imports `_libecryptfs`, defines SWIG attribute helpers, and exposes `ecryptfs_passphrase_blob`, `ecryptfs_passphrase_sig_from_blob`, and `ecryptfs_add_blob_to_keyring`.

Control flow/state: import-time binding maps Python names to extension-module functions. Helper functions support old-style/new-style SWIG classes but no classes are exposed in this snippet.

Dependencies/integration: generated by SWIG 1.3.36, imports Python 2 `new` module, and requires compiled `_libecryptfs`.

Risks: incompatible with Python 3 due to `new` and old exception syntax (`raise AttributeError,name`). File header says not to modify directly; source of truth is SWIG interface.

Test signals: Python import and function invocation against keyring-capable system.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/libecryptfs.py -->
