# subset-b-008392 Research

Grouped source research for FoundationDB CMake build, packaging, dependency discovery, Swift/C# tooling, POSIX import wrapper generation, and Joshua binding-test scripts. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/AddFdbTest.cmake -->
# sources/storage-engines/foundationdb/cmake/AddFdbTest.cmake

## Purpose
Configures FoundationDB test registration, simulation test bookkeeping, correctness package staging, binding tester packaging, and client-test wrappers for CTest/Joshua workflows.

## Important APIs, Types, and Functions
Defines `configure_testing`, `verify_testing`, `add_fdb_test`, correctness package builders, `prepare_binding_test_files`, `package_bindingtester`, `package_bindingtester2`, `collect_unit_tests`, `add_python_venv_test`, `add_fdbclient_test`, `add_unavailable_fdbclient_test`, `add_multi_fdbclient_test`, and `add_java_test`.

## Control Flow and Integration
The module first records `.txt` and `.toml` simulation files, then each `add_fdb_test` removes assigned files from the unassigned list, filters by include/exclude settings, and emits a `TestRunner` CTest command. Packaging functions stage binaries, test files, CMake cache, Joshua scripts, local-cluster helpers, and generated language bindings into tarballs. Client tests run through a Python virtual environment and temporary cluster wrappers.

## State and Persistence
Depends on Python3, CTest, FoundationDB build targets (`fdbserver`, `fdbcli`, `fdb_c`, `fdb_flow_tester`), generated bindings, Java/Go/Swift options, `TestRunner`, Joshua scripts, and CMake package targets.

## Dependencies
Persistent build state is held in CMake parent-scope variables such as `fdb_test_files`, `TEST_NAMES`, `LONG_RUNNING_TEST_NAMES`, `TEST_FILES_<name>`, and custom targets/tarball outputs under the build tree. Runtime tests create logs, venv contents, cluster files, and package archives.

## Risks and Test Signals
Risks include stale unassigned-test detection, platform conditionals that skip Windows/IDE packaging, timeout differences under valgrind/sanitizers, shell quoting in venv commands, and binding package dependency ordering. Test signals are CTest registration output, `verify_testing` errors, generated tarballs, and successful temporary-cluster client tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/AddFdbTest.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/AssertFileDoesntExist.cmake -->
# sources/storage-engines/foundationdb/cmake/AssertFileDoesntExist.cmake

## Purpose
Provides a configure-time guard that fails if a legacy generated file exists in the source tree.

## Important APIs, Types, and Functions
Uses the `FILE` variable supplied by the caller, builds a multi-line diagnostic in `error_msg`, joins it, and calls `message(FATAL_ERROR)` when the file exists.

## Control Flow and Integration
The caller includes or runs this script with `FILE` set. The script checks `EXISTS`, reports that a previous old `make` build likely left `versions.h`, and tells the user to clean the source directory.

## State and Persistence
Depends only on CMake built-ins `if(EXISTS)`, `list(JOIN)`, and `message`.

## Dependencies
No persistent state is written; it only observes source-tree filesystem state.

## Risks and Test Signals
Risk is limited to caller-provided `FILE`: an unset or wrong path weakens the guard or blocks an unrelated file. Test signal is a deliberate configure failure when the legacy artifact is present.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/AssertFileDoesntExist.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CPackConfig.cmake -->
# sources/storage-engines/foundationdb/cmake/CPackConfig.cmake

## Purpose
Selects CPack component sets and package metadata inputs based on the active package generator.

## Important APIs, Types, and Functions
Sets `CPACK_PACKAGING_INSTALL_PREFIX`, `CPACK_COMPONENTS_ALL`, `CPACK_RESOURCE_FILE_README`, `CPACK_RESOURCE_FILE_LICENSE`, and `CPACK_STRIP_FILES` for RPM, DEB, and TGZ branches.

## Control Flow and Integration
`InstallLayout.cmake` configures this file into the build packaging directory and assigns it as `CPACK_PROJECT_CONFIG_FILE`. At CPack runtime, the script matches `CPACK_GENERATOR` and enables the correct client/server/versioned components.

## State and Persistence
Depends on CPack variables, project `README.md` and `LICENSE`, and component names created by install rules.

## Dependencies
No long-lived state beyond CPack variables; effects are consumed by package generation.

## Risks and Test Signals
Risks are unsupported generator fatal errors and component-name drift between install rules and package config. Test signals are successful RPM/DEB/TGZ package creation with expected components.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CPackConfig.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CheckForPthreads.c -->
# sources/storage-engines/foundationdb/cmake/CheckForPthreads.c

## Purpose
Acts as the C source used by custom `FindThreads.cmake` to verify that `-pthread` both compiles and links.

## Important APIs, Types, and Functions
Contains `start_routine` and `main`, calling `pthread_create` and `pthread_join` against `<pthread.h>`.

## Control Flow and Integration
`FindThreads.cmake` passes this file to `try_compile` with `LINK_LIBRARIES=-pthread`. The source is not intended to execute; successful compilation/linking proves the flag is usable.

## State and Persistence
Depends on POSIX pthread headers and linker support.

## Dependencies
No persistence; compiled temporary artifacts live under CMake try-compile directories.

## Risks and Test Signals
Risks are false negatives on unusual toolchains or cross-compilation environments. Test signal is the `THREADS_HAVE_PTHREAD_ARG` result and CMake check output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CheckForPthreads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileActorCompiler.cmake -->
# sources/storage-engines/foundationdb/cmake/CompileActorCompiler.cmake

## Purpose
Configures the actor compiler command used to translate `.actor.cpp` and `.actor.h` sources into generated C++ during Flow target builds.

## Important APIs, Types, and Functions
Defines Python source lists, legacy C# source lists, `ACTORCOMPILER_PY_COMMAND`, `ACTORCOMPILER_CSHARP_COMMAND`, `ACTORCOMPILER_COMMAND`, and the `actorcompiler` custom target.

## Control Flow and Integration
The module always creates a Python actor compiler target. If C# tools are enabled and found, it builds a C# actor compiler using MSBuild/CSharp on Windows, Mono, or `dotnet_build`; when present, the C# command overrides the Python command. `FlowCommands.cmake` consumes `ACTORCOMPILER_COMMAND` for generated actor files.

## State and Persistence
Depends on Python3, optional C# toolchain variables from `EnableCsharp.cmake`, Mono/dotnet helpers, and Flow actor compiler source files.

## Dependencies
State is stored in CMake cache/internal variables and generated executables such as `actorcompiler.exe` or dotnet output DLLs.

## Risks and Test Signals
Risks include divergent Python/C# compiler output, stale generated actor files, and missing `CSHARP_TOOLCHAIN_FOUND`. Test signals include actor generation custom commands and compare mode in `FlowCommands.cmake` when both compilers are available.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileActorCompiler.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileBoost.cmake -->
# sources/storage-engines/foundationdb/cmake/CompileBoost.cmake

## Purpose
Finds or builds the exact Boost 1.86.0 libraries required by FoundationDB, with special handling for sanitizers, libc++, Clang, Windows, and CI prebuilt roots.

## Important APIs, Types, and Functions
Defines `compile_boost(TARGET ...)`, imported static library targets for context/filesystem/iostreams/serialization/system/url/program_options, and interface targets `boost_target` and `boost_target_program_options`.

## Control Flow and Integration
The module first forces source builds for sanitizer configurations. Otherwise it looks under `/opt/boost_1_86_0*` and `BOOST_ROOT`, uses Boost config mode, then falls back to `ExternalProject_add` downloading Boost with a SHA256. The helper configures `user-config.jam` and b2 flags from compiler/linker settings.

## State and Persistence
Depends on Boost archive URL/hash, ExternalProject, CMake compiler/linker variables, zstd for Boost iostreams on some platforms, and sanitizer flag lists from `ConfigureCompiler.cmake`.

## Dependencies
State persists in `boost_install` under the build tree, imported target properties, and CMake prefix/hint variables.

## Risks and Test Signals
Risks include ABI mismatch between Clang/libc++ and GCC/libstdc++, stale prebuilt Boost, URL availability, and generator-expression flag drift. Test signals are `find_package(Boost)` success, ExternalProject byproducts, and downstream link of FDB targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileBoost.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileCoverageTool.cmake -->
# sources/storage-engines/foundationdb/cmake/CompileCoverageTool.cmake

## Purpose
Builds the C# coverage tool used to generate per-target XML coverage metadata for Flow libraries and executables.

## Important APIs, Types, and Functions
Defines coverage tool source/project paths, the `coveragetool` target, `coveragetool_exe`, and cached `coveragetool_command`.

## Control Flow and Integration
On Windows it creates a CSharp executable target with .NET references. Under Mono it invokes `mcs` to produce `coveragetool.exe`. Otherwise it uses `dotnet_build`. `FlowCommands.cmake` later invokes `coveragetool_command` from `generate_coverage_xml`.

## State and Persistence
Depends on C# toolchain variables, Mono/dotnet support, and coverage tool source files under `flow/coveragetool`.

## Dependencies
Generated tool binaries persist in the CMake binary directory or dotnet project `bin` folder; command selection is cached internally.

## Risks and Test Signals
Risks include missing toolchain setup, command not set if platform branches change, and stale coverage XML. Test signals are successful `coveragetool` target build and generated `coverage.<target>.xml` files.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileCoverageTool.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileRocksDB.cmake -->
# sources/storage-engines/foundationdb/cmake/CompileRocksDB.cmake

## Purpose
Configures FoundationDB's RocksDB dependency, generates an FDB RocksDB version header, finds a compatible system RocksDB when allowed, or builds RocksDB from a pinned release/commit.

## Important APIs, Types, and Functions
Uses `RocksDBVersion.cmake`, `FDBRocksDBVersion.h.in`, `find_package(RocksDB)`, `ExternalProject_Add(rocksdb)`, `ROCKSDB_LIBRARIES`, `ROCKSDB_INCLUDE_DIR`, and many RocksDB CMake args.

## Control Flow and Integration
The module validates that exactly one of `ROCKSDB_VERSION` or `ROCKSDB_GIT_HASH` is selected. For commit hashes it downloads `version.h` to parse major/minor/patch. It generates `FDBRocksDBVersion.h`, tries a system package only for version-based builds, then defines or imports the `rocksdb` build target.

## State and Persistence
Depends on network access for commit version probing/build downloads, SHA256 values, LZ4/liburing/sanitizer settings, and the custom `FindRocksDB.cmake`.

## Dependencies
Persists downloaded version checks, generated header under `fdbserver/core/include`, ExternalProject source/build directories, and target variables.

## Risks and Test Signals
Risks include configure-time network requirement, stale hash/version mismatch, system package overriding configured variables, and ABI mismatch from forwarded compiler flags. Test signals are generated header contents, RocksDB target byproducts, and fdbserver RocksDB storage tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileRocksDB.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileVexillographer.cmake -->
# sources/storage-engines/foundationdb/cmake/CompileVexillographer.cmake

## Purpose
Builds or selects the Vexillographer tool that generates FDB option bindings for C, C++, Java, Python, and Ruby.

## Important APIs, Types, and Functions
Defines `VEXILLOGRAPHER_COMMAND`, `VEXILLOGRAPHER_DEPENDS`, source/project variables, and `vexillographer_compile(TARGET LANG OUT OUTPUT ... ALL)`.

## Control Flow and Integration
The module prefers C# tooling when enabled: Visual Studio CSharp on Windows, Mono on Unix, or dotnet. If no C# toolchain is available it falls back to the Python implementation. `vexillographer_compile` emits custom commands that run the selected command over `fdb.options` and creates per-language custom targets.

## State and Persistence
Depends on `EnableCsharp.cmake`/toolchain discovery, Python3 fallback, `dotnet_build`, Mono, and `fdbclient/vexillographer/fdb.options`.

## Dependencies
State includes generated option files, built `vexillographer.exe`/DLLs, and cached command variables.

## Risks and Test Signals
Risks include language generator parity between C# and Python, missing dependency on generated outputs, and Windows/non-Windows branch drift. Test signals are generated options files and downstream binding builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileVexillographer.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileZstd.cmake -->
# sources/storage-engines/foundationdb/cmake/CompileZstd.cmake

## Purpose
Provides a helper to fetch and add zstd v1.5.2 to the FoundationDB build.

## Important APIs, Types, and Functions
Defines `compile_zstd()` and sets internal `ZSTD_LIB_INCLUDE_DIR`.

## Control Flow and Integration
The function declares zstd with FetchContent, populates it once, adds its `build/cmake` subdirectory, and suppresses selected Clang warnings on `zstd`, `libzstd_static`, and `zstd-frugal` targets.

## State and Persistence
Depends on GitHub zstd tag `v1.5.2`, FetchContent, and target names exported by zstd's CMake project.

## Dependencies
FetchContent state and zstd build artifacts persist in the binary tree; include path is cached internally.

## Risks and Test Signals
Risks include unpinned-by-hash FetchContent, target name changes upstream, and warning suppressions hiding real issues. Test signal is successful zstd target build and consumers finding `ZSTD_LIB_INCLUDE_DIR`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompileZstd.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompilerChecks.cmake -->
# sources/storage-engines/foundationdb/cmake/CompilerChecks.cmake

## Purpose
Collects small CMake compiler/toolchain decision helpers used by the main compiler configuration.

## Important APIs, Types, and Functions
Defines `env_set`, `default_linker`, `use_libcxx`, `static_link_libcxx`, and `check_swift_source_compiles`.

## Control Flow and Integration
`ConfigureCompiler.cmake` calls these helpers to turn environment variables into cache options, prefer LLD for Clang when present, default libc++ for Apple/Clang, decide when static C++ runtime linking is supported, and validate Swift snippets with `try_compile`.

## State and Persistence
Depends on CMake compiler IDs, `find_program`, `find_library`, and Swift/C++ compilers when Swift checks run.

## Dependencies
State is CMake cache variables produced by callers and temporary Swift files under `CMakeTmp`.

## Risks and Test Signals
Risks include decisions made before dependent options are initialized, environment overrides with unexpected values, and Swift try-compile behavior under cross-compilation. Test signals are configure messages and cache values used by `ConfigureCompiler.cmake`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/CompilerChecks.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Config.cmake.in -->
# sources/storage-engines/foundationdb/cmake/Config.cmake.in

## Purpose
Template for an installed FoundationDB CMake package config that includes the generated exported target file.

## Important APIs, Types, and Functions
Contains one `include("${CMAKE_CURRENT_LIST_DIR}/@targets_export_name@.cmake")` directive.

## Control Flow and Integration
`fdb_configure_and_install` configures this template per package/install layout so downstream CMake projects can import FoundationDB targets from the install tree.

## State and Persistence
Depends on `targets_export_name` substitution and corresponding installed export files.

## Dependencies
No runtime state; configured package files persist in generated/install directories.

## Risks and Test Signals
Risks are broken installed package discovery if export name or destination changes. Test signal is a downstream `find_package` or include of the installed config file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Config.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/ConfigureCompiler.cmake -->
# sources/storage-engines/foundationdb/cmake/ConfigureCompiler.cmake

## Purpose
Centralizes FoundationDB compiler, linker, sanitizer, allocator, warning, debug-symbol, LTO, vector-instruction, libc++, pthread, and Swift compile settings.

## Important APIs, Types, and Functions
Defines many cache options through `env_set`, computes `USE_SANITIZER`, configures C/C++ standards, clang-tidy, linkers, sanitizer flags, Boost flag propagation, warning suppressions, architecture flags, DTrace/aligned allocation checks, and Swift C++ interop flags.

## Control Flow and Integration
The file includes `CompilerChecks`, sets defaults, validates incompatible options, finds required thread support, then branches heavily by Windows vs Unix and compiler family. Swift support appends target/sdk/resource/module-cache flags, imports cross-compile helper when needed, and verifies `import CxxStdlib`.

## State and Persistence
Depends on `FindThreads.cmake`, CMake check modules, optional Gperftools, LLD/libc++/libatomic, sanitizer runtimes, platform headers, and Swift toolchain metadata.

## Dependencies
State persists in CMake cache flags, global compile/link options, environment library paths for libc++, compile definitions, and Swift module cache paths.

## Risks and Test Signals
Risks are broad global side effects, duplicate/wrong flags for non-C++ languages, fragile compiler ID detection, and incompatible sanitizer/static-link configurations. Test signals are configure checks, compiler command lines, successful target builds, and sanitizer/Swift CI lanes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/ConfigureCompiler.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/DotnetImports.props.in -->
# sources/storage-engines/foundationdb/cmake/DotnetImports.props.in

## Purpose
MSBuild property template used by dotnet-based C# tool builds.

## Important APIs, Types, and Functions
Defines `<OutDir>`, `<DOTNET_PACKAGE_VERSION>`, and injectable custom build props.

## Control Flow and Integration
`Finddotnet.cmake`/tooling can configure this file to route dotnet build outputs into a known directory and propagate package version metadata.

## State and Persistence
Depends on `_DN_OUTPUT_PATH`, `_DN_VERSION`, and `_DN_CUSTOM_BUILDPROPS` substitutions.

## Dependencies
Configured props files persist in the generated build tree; no runtime state.

## Risks and Test Signals
Risks are malformed XML from custom props or paths, and output directory mismatches. Test signal is successful dotnet project build using configured imports.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/DotnetImports.props.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/EnableCsharp.cmake -->
# sources/storage-engines/foundationdb/cmake/EnableCsharp.cmake

## Purpose
Selects the C# build path for FoundationDB build tools.

## Important APIs, Types, and Functions
Calls `enable_language(CSharp)` on Windows, otherwise tries `find_package(dotnet 9.0)` and falls back to required Mono, setting `CSHARP_USE_MONO`.

## Control Flow and Integration
The module returns after the first valid branch. If neither dotnet nor Mono is found on non-Windows, configure fails.

## State and Persistence
Depends on custom `Finddotnet.cmake`, `Findmono.cmake`, CMake CSharp language support, dotnet 9.0, and Mono `mcs`/runtime.

## Dependencies
State is held in CMake language enablement and `CSHARP_USE_MONO`; downstream modules use discovered executable variables.

## Risks and Test Signals
Risks include no explicit `CSHARP_TOOLCHAIN_FOUND` set here, dotnet version parsing ambiguity, and platform-specific CSharp behavior. Test signals are actor compiler, coverage tool, and vexillographer builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/EnableCsharp.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBBenchmark.cmake -->
# sources/storage-engines/foundationdb/cmake/FDBBenchmark.cmake

## Purpose
Configures Google Benchmark as an interface dependency for FoundationDB benchmark targets.

## Important APIs, Types, and Functions
Defines `fdb_setup_googlebenchmark()` and interface target `fdb_google_benchmark`.

## Control Flow and Integration
The helper first chooses prebuilt roots under `/opt` based on compiler/libc++ mode, runs `find_package(benchmark)`, and links the imported target if found. If not, it configures and builds `benchmark-download.cmake`, adds the downloaded source subtree, and links the local `benchmark` target.

## State and Persistence
Depends on custom `Findbenchmark.cmake`, CMake generator availability, GitHub fetches, and benchmark CMake target names.

## Dependencies
State persists in downloaded googlebenchmark/googletest source/build directories and the `fdb_google_benchmark` target.

## Risks and Test Signals
Risks include configure-time network/build failures, prebuilt ABI mismatch, and old benchmark/googletest pins. Test signals are fdbrpc benchmark target configuration and successful benchmark executable link.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBBenchmark.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBComponents.cmake -->
# sources/storage-engines/foundationdb/cmake/FDBComponents.cmake

## Purpose
Discovers and gates optional FoundationDB components and language bindings.

## Important APIs, Types, and Functions
Sets component flags for jemalloc, valgrind, OpenSSL/ZLIB, Swift, Python/C/Java/Go/Ruby bindings, documentation, mako, RocksDB, toml11, coroutine implementation, AWS backup, gRPC, and `packages`; defines `print_components`.

## Control Flow and Integration
The module resolves dependencies in order: low-level alloc/profiling, crypto/compression, language runtimes, binding prerequisites, external libraries, and package directory setup. Options and found tools decide `WITH_*` flags, and `FORCE_ALL_COMPONENTS` can turn missing optional dependencies into configure errors.

## State and Persistence
Depends on many custom find/compile modules, Python/JNI/Java/Go/Ruby/Swift tools, OpenSSL/ZLIB, RocksDB, protobuf/gRPC/absl, and external network sources.

## Dependencies
State is mostly CMake cache/options and global `WITH_*` variables; it may also FetchContent toml11 or Swift bindings into the source tree when absent.

## Risks and Test Signals
Risks include hidden downloads, binding flags depending on earlier C binding/Python decisions, sanitizer disabling Go/Swift, and version checks for protoc/Swift. Test signals are component overview output and successful builds of selected bindings/packages.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBComponents.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBInstall.cmake -->
# sources/storage-engines/foundationdb/cmake/FDBInstall.cmake

## Purpose
Provides generic installation helper functions used by FoundationDB package layout code.

## Important APIs, Types, and Functions
Defines package/dir registries, symlink helpers, `pop_front`, `install_destinations`, `get_install_dest`, `copy_install_destinations`, `fdb_configure_and_install`, and `fdb_install`.

## Control Flow and Integration
`InstallLayout.cmake` registers package names and logical install dirs, then these helpers expand logical destinations into per-package `install()` calls and configured template installs. Symlink helpers synthesize component-specific relative symlinks.

## State and Persistence
Depends on CMake install rules, package/component names, and caller-defined `generated_dir`.

## Dependencies
State is stored in parent-scope variables like `FDB_INSTALL_PACKAGES`, `FDB_INSTALL_DIRS`, and private `__install_dest_<pkg>_<dir>` variables; generated configured files go under `generated_dir`.

## Risks and Test Signals
Risks include duplicated symlink helper definitions with `InstallLayout.cmake`, platform-condition confusion, and fatal errors for unknown logical dirs. Test signals are install manifests and package contents matching expected paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBInstall.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBRocksDBVersion.h.in -->
# sources/storage-engines/foundationdb/cmake/FDBRocksDBVersion.h.in

## Purpose
Template for the generated C++ header that exposes the RocksDB version compiled into FoundationDB.

## Important APIs, Types, and Functions
Defines include guard and macros `FDB_ROCKSDB_MAJOR`, `FDB_ROCKSDB_MINOR`, `FDB_ROCKSDB_PATCH`, and `FDB_ROCKSDB_GIT_HASH`.

## Control Flow and Integration
`CompileRocksDB.cmake` configures this file into `fdbserver/core/include/fdbserver/core/FDBRocksDBVersion.h` during CMake configure.

## State and Persistence
Depends on version variables parsed from `RocksDBVersion.cmake` or downloaded RocksDB `version.h`.

## Dependencies
Generated header persists in the build include tree and should not be committed.

## Risks and Test Signals
Risks are stale generated headers after changing RocksDB config and empty git hash semantics for release builds. Test signals are compile-time use from RocksDB storage code and generated macro values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FDBRocksDBVersion.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindCoroutines.cmake -->
# sources/storage-engines/foundationdb/cmake/FindCoroutines.cmake

## Purpose
Detects C++ coroutine header/library support and creates an imported target for consumers.

## Important APIs, Types, and Functions
Defines result variables `CXX_COROUTINES_HAVE_COROUTINES`, `CXX_COROUTINES_HEADER`, `CXX_COROUTINES_NAMESPACE`, `Coroutines_FOUND`, and imported target `std::coroutines`.

## Control Flow and Integration
The module probes compiler flags (`/await`, `-fcoroutines-ts`, `-fcoroutines`), normalizes requested components (`Final`, `Experimental`), checks headers and compilation snippets, then builds an interface target with extra compile options if needed.

## State and Persistence
Depends on CMake check modules and compiler support for C++17/C++20 coroutine syntax.

## Dependencies
State is cached in CMake variables and target properties.

## Risks and Test Signals
Risks include old TS/final coroutine ambiguity, flag checks passing but target code failing, and stale cached results after compiler changes. Test signal is successful compilation of the embedded coroutine factorial snippet.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindCoroutines.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindGperftools.cmake -->
# sources/storage-engines/foundationdb/cmake/FindGperftools.cmake

## Purpose
Finds gperftools tcmalloc/profiler support and exposes it as an imported target.

## Important APIs, Types, and Functions
Searches `GPERFTOOLS_TCMALLOC`, `GPERFTOOLS_PROFILER`, `GPERFTOOLS_TCMALLOC_AND_PROFILER`, `GPERFTOOLS_INCLUDE_DIR`, sets `GPERFTOOLS_LIBRARIES`, and creates imported target `gperftools`.

## Control Flow and Integration
When `USE_GPERFTOOLS` is enabled by `ConfigureCompiler.cmake`, `find_package(Gperftools REQUIRED)` invokes this module and fails if the combined library or headers are missing.

## State and Persistence
Depends on `Gperftools_ROOT_DIR`, `find_library`, `find_path`, and `FindPackageHandleStandardArgs`.

## Dependencies
No generated state; variables and imported target properties persist in the CMake configure.

## Risks and Test Signals
Risks include requiring `tcmalloc_and_profiler` even if separate libs exist, and root variable naming mismatch expectations. Test signal is successful required find and link of profiling builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindGperftools.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindJinja2.cmake -->
# sources/storage-engines/foundationdb/cmake/FindJinja2.cmake

## Purpose
Detects the Python Jinja2 templating package for generation workflows.

## Important APIs, Types, and Functions
Finds Python3 interpreter and runs `python -c 'import jinja2; print(jinja2.__version__)'`, producing `Jinja2_VERSION` and `Jinja2_FOUND`.

## Control Flow and Integration
The module uses Python import success as the only discovery path, then delegates result validation to `find_package_handle_standard_args`.

## State and Persistence
Depends on Python3 and an importable `jinja2` package in that interpreter environment.

## Dependencies
No persistence beyond CMake variables.

## Risks and Test Signals
Risks include mismatch between configure Python and build/runtime Python. Test signal is configure-time Jinja2 version detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindJinja2.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindLZ4.cmake -->
# sources/storage-engines/foundationdb/cmake/FindLZ4.cmake

## Purpose
Finds LZ4 headers/library and exposes imported target `LZ4::LZ4`.

## Important APIs, Types, and Functions
Searches `LZ4_INCLUDE_DIR`, `LZ4_LIBRARY`, parses version macros from `lz4.h`, and sets `LZ4_INCLUDE_DIRS`, `LZ4_LIBRARIES`, `LZ4_VERSION`.

## Control Flow and Integration
Used by RocksDB-enabled fdbserver builds before `CompileRocksDB.cmake`; if found, downstream code links the imported target or variables.

## State and Persistence
Depends on `LZ4_ROOT` or environment root, `FindPackageHandleStandardArgs`, and `lz4.h` version macros.

## Dependencies
No generated state; CMake cache variables and imported target properties persist.

## Risks and Test Signals
Risks include regex parsing across LZ4 header changes and library/header version mismatch. Test signal is required `find_package(LZ4)` success and RocksDB/FDB link.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindLZ4.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindRocksDB.cmake -->
# sources/storage-engines/foundationdb/cmake/FindRocksDB.cmake

## Purpose
Finds a system RocksDB installation and extracts its version.

## Important APIs, Types, and Functions
Searches `ROCKSDB_INCLUDE_DIR`, parses `rocksdb/version.h` macros, finds `ROCKSDB_LIBRARY`, and sets `ROCKSDB_FOUND`, `ROCKSDB_VERSION`, include/library variables.

## Control Flow and Integration
`CompileRocksDB.cmake` calls this only for configured release-version builds. If it fails, `CompileRocksDB.cmake` restores configured version and builds RocksDB externally.

## State and Persistence
Depends on `ROCKSDB_ROOT`/environment root and RocksDB's standard include layout.

## Dependencies
No generated state; result variables are cached/advanced.

## Risks and Test Signals
Risks include overwriting `ROCKSDB_VERSION` used for configured version selection and accepting ABI-incompatible system libraries. Test signal is version message and successful fdbserver link.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindRocksDB.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindSphinx.cmake -->
# sources/storage-engines/foundationdb/cmake/FindSphinx.cmake

## Purpose
Discovers the `sphinx-build` executable for documentation builds.

## Important APIs, Types, and Functions
Sets `Sphinx_EXECUTABLE`, parses `Sphinx_VERSION` from `sphinx-build --version`, and reports `Sphinx_FOUND`.

## Control Flow and Integration
Documentation-related CMake can require or use this module when `WITH_DOCUMENTATION` is enabled.

## State and Persistence
Depends on `Sphinx_ROOT` or PATH lookup and the executable's version output format.

## Dependencies
No persistence beyond CMake variables.

## Risks and Test Signals
Risks include version substring parsing if Sphinx output changes. Test signal is documentation target configure/build success.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindSphinx.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindSwiftLibs.cmake -->
# sources/storage-engines/foundationdb/cmake/FindSwiftLibs.cmake

## Purpose
Provides helper functions to query Swift runtime library search and resource paths from the active Swift compiler.

## Important APIs, Types, and Functions
Defines `swift_get_linker_search_paths(var)` and `swift_get_resource_path(var)`.

## Control Flow and Integration
Each function runs `${CMAKE_Swift_COMPILER} -print-target-info` with Apple SDK flags when needed, parses JSON path fields, and returns path lists to the caller. fdbserver Swift integration uses these to link Swift runtime libraries and module maps.

## State and Persistence
Depends on Swift compiler JSON output, CMake `string(JSON)`, and `CMAKE_OSX_SYSROOT` on Apple.

## Dependencies
No persisted files; results are parent-scope variables.

## Risks and Test Signals
Risks include malformed JSON, empty path arrays, cross-compile target mismatch, and duplicated code between helpers. Test signals are Swift-enabled fdbserver link and generated module-map/header flows.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindSwiftLibs.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindThreads.cmake -->
# sources/storage-engines/foundationdb/cmake/FindThreads.cmake

## Purpose
Custom thread discovery module based on CMake's FindThreads with FoundationDB Swift-aware pthread handling.

## Important APIs, Types, and Functions
Defines internal macros `_threads_check_libc`, `_threads_check_lib`, `_threads_check_flag_pthread`; sets `CMAKE_THREAD_LIBS_INIT`, `CMAKE_USE_PTHREADS_INIT`, `Threads_FOUND`; creates `Threads::Threads`.

## Control Flow and Integration
The module compiles a pthread test, optionally tries `-pthread` first, checks pthread libraries, handles Windows/HP-UX/Cygwin cases, and assigns generator expressions so Swift links use `-lpthread` while non-Swift C/C++ uses `-pthread`.

## State and Persistence
Depends on `CheckForPthreads.c`, C/C++ compiler availability, pthread headers/libraries, and CMake check modules.

## Dependencies
State is cached check results and imported target compile/link properties; try-compile output may be appended to `CMakeError.log`.

## Risks and Test Signals
Risks include the custom Swift generator expressions diverging from upstream CMake, cross-language link behavior, and cached check results after toolchain changes. Test signals are `find_package(Threads REQUIRED)` success and Swift/C++ linked binaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindThreads.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindWIX.cmake -->
# sources/storage-engines/foundationdb/cmake/FindWIX.cmake

## Purpose
Locates WiX Toolset executables for Windows installer generation.

## Important APIs, Types, and Functions
Finds `WIX_CANDLE` and `WIX_LIGHT` under `$WIX/bin` or PATH and reports via `find_package_handle_standard_args`.

## Control Flow and Integration
Windows packaging code can require this module before building MSI artifacts.

## State and Persistence
Depends on WiX environment variable/path and CMake package handle standard args.

## Dependencies
No generated state; only CMake variables.

## Risks and Test Signals
Risks include the script appearing to miss a closing parenthesis in the checked source, which would break inclusion unless patched elsewhere. Test signal is successful CMake parsing and WiX executable discovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FindWIX.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findbenchmark.cmake -->
# sources/storage-engines/foundationdb/cmake/Findbenchmark.cmake

## Purpose
Finds static Google Benchmark libraries and creates imported targets.

## Important APIs, Types, and Functions
Defines `_finalize_find_package_benchmark`, variables `benchmark_INCLUDE_DIR`, `benchmark_LIBRARY`, `benchmark_main_LIBRARY`, `benchmark_FOUND`, and targets `benchmark::benchmark`, `benchmark::benchmark_main`.

## Control Flow and Integration
The module looks for `benchmark/benchmark.h`, `libbenchmark.a`, and `libbenchmark_main.a` under `benchmark_ROOT`; early returns finalize negative discovery cleanly.

## State and Persistence
Depends on static benchmark library naming and root hints.

## Dependencies
No generated state; imported targets are configure-time state.

## Risks and Test Signals
Risks include only recognizing `.a` static names and not setting include dirs on `benchmark::benchmark_main`. Test signals are `FDBBenchmark.cmake` finding and linking benchmark targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findbenchmark.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Finddotnet.cmake -->
# sources/storage-engines/foundationdb/cmake/Finddotnet.cmake

## Purpose
Finds the dotnet executable and provides a helper to build .NET projects into predictable DLL outputs.

## Important APIs, Types, and Functions
Sets `dotnet_EXECUTABLE`, `dotnet_VERSION`, `dotnet_FOUND`, and defines `dotnet_build(project_file_path SOURCE ... CONFIGURATION ...)`.

## Control Flow and Integration
Discovery runs `dotnet` and captures output as a version string. `dotnet_build` computes the project stem and bin path, creates a custom command invoking `dotnet build --configuration ... --output ... --self-contained false -p:UseAppHost=false`, then exposes `<project>_EXECUTABLE_PATH`.

## State and Persistence
Depends on dotnet CLI, CMake `cmake_path`, project files, and source dependency lists.

## Dependencies
State persists in generated dotnet output directories and custom targets.

## Risks and Test Signals
Risks include weak version parsing, a likely `oneValueArg`/`oneValueArgs` typo affecting argument parsing, and stale project outputs if source lists are incomplete. Test signals are built actorcompiler/coveragetool/vexillographer DLLs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Finddotnet.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findjemalloc.cmake -->
# sources/storage-engines/foundationdb/cmake/Findjemalloc.cmake

## Purpose
Finds jemalloc headers/static libraries, preferring `jemalloc-config`, and creates imported targets.

## Important APIs, Types, and Functions
Defines macros to configure from `jemalloc-config`, create `jemalloc::jemalloc` and `jemalloc_pic::jemalloc_pic`, and finalize package results.

## Control Flow and Integration
The module first asks `jemalloc-config` for include/lib/version data and locates static libraries. If that fails, it searches headers and `libjemalloc.a`/`libjemalloc_pic.a` manually.

## State and Persistence
Depends on `jemalloc_ROOT`, `jemalloc-config`, static jemalloc libraries, and `FindPackageHandleStandardArgs`.

## Dependencies
No file persistence; imported targets and cache variables carry discovery state.

## Risks and Test Signals
Risks include a typo in `jemalloc_pic_LIBRARTY` target property, possible requirement of PIC library even when not needed, and static-only naming. Test signals are `find_package(jemalloc 5.3.0 REQUIRED)` success or fallback to `Jemalloc.cmake`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findjemalloc.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findmono.cmake -->
# sources/storage-engines/foundationdb/cmake/Findmono.cmake

## Purpose
Discovers Mono runtime and C# compiler for non-Windows C# tool builds.

## Important APIs, Types, and Functions
Finds `MONO_EXECUTABLE` and `CSHARP_COMPILER_EXECUTABLE` (`mcs`), setting `mono_FOUND`.

## Control Flow and Integration
`EnableCsharp.cmake` requires this module when dotnet is unavailable, and C# compile modules use the executable paths to build and run tools.

## State and Persistence
Depends on `mono_ROOT` or PATH and the legacy `mcs` compiler rather than Microsoft `csc`.

## Dependencies
No persisted state beyond CMake variables.

## Risks and Test Signals
Risks include modern Mono distributions without `mcs`, and no standard package-handle diagnostics. Test signals are Mono messages and successful C# tool custom commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findmono.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findsccache.cmake -->
# sources/storage-engines/foundationdb/cmake/Findsccache.cmake

## Purpose
Finds `sccache` and configures it as the C/C++ compiler launcher.

## Important APIs, Types, and Functions
Sets `SCCACHE_EXECUTABLE`, `sccache_FOUND`, `CMAKE_C_COMPILER_LAUNCHER`, and `CMAKE_CXX_COMPILER_LAUNCHER`.

## Control Flow and Integration
When included, the module looks under `sccache_ROOT`/PATH and immediately mutates compiler launcher variables if found.

## State and Persistence
Depends on the `sccache` executable and CMake launcher support.

## Dependencies
State is CMake launcher variables; cache files are managed by sccache outside this script.

## Risks and Test Signals
Risks include global side effects when found and lack of package-handle standard args. Test signal is compiler commands routed through sccache.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findsccache.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findtoml11.cmake -->
# sources/storage-engines/foundationdb/cmake/Findtoml11.cmake

## Purpose
Finds an installed toml11 header-only library and exposes CMake variables.

## Important APIs, Types, and Functions
Searches `toml11_INCLUDE_DIRS`, reads version macros from toml11 headers when available, and reports `toml11_FOUND`/`toml11_VERSION`.

## Control Flow and Integration
`FDBComponents.cmake` first tries config-mode `find_package(toml11 3.8.1 EXACT QUIET CONFIG)` and uses FetchContent fallback, while this module supports manual root-based discovery where requested.

## State and Persistence
Depends on `toml11_ROOT` and toml11 include layout/version defines.

## Dependencies
No generated state; variables are advanced.

## Risks and Test Signals
Risks include duplicate discovery paths between config mode and this module. Test signal is `toml11::toml11` availability for C++ code.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findtoml11.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Finduring.cmake -->
# sources/storage-engines/foundationdb/cmake/Finduring.cmake

## Purpose
Finds liburing headers and library for optional RocksDB/io_uring support.

## Important APIs, Types, and Functions
Sets `uring_INCLUDE_DIR`, `uring_LIBRARY`, `uring_FOUND`, and creates imported target `uring::uring` when found.

## Control Flow and Integration
RocksDB-enabled fdbserver configuration may require this module when `WITH_LIBURING` is enabled.

## State and Persistence
Depends on liburing install paths and `FindPackageHandleStandardArgs`.

## Dependencies
No generated files; imported target state persists in CMake.

## Risks and Test Signals
Risks include no version validation and target availability only when both header/library are found. Test signal is RocksDB build with `-DWITH_LIBURING=ON` linking successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Finduring.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findvalgrind.cmake -->
# sources/storage-engines/foundationdb/cmake/Findvalgrind.cmake

## Purpose
Finds Valgrind headers and executable for valgrind-enabled builds.

## Important APIs, Types, and Functions
Searches include dirs for Valgrind headers, finds `valgrind_EXECUTABLE`, sets `valgrind_INCLUDE_DIRS`, `valgrind_FOUND`, and related variables.

## Control Flow and Integration
`FDBComponents.cmake` uses this module when `USE_VALGRIND` is enabled and creates an interface target carrying include dirs.

## State and Persistence
Depends on Valgrind development headers and binary.

## Dependencies
No generated state; discovery variables persist.

## Risks and Test Signals
Risks include enabling Valgrind compile definitions without matching runtime environment. Test signals are configure success under `USE_VALGRIND` and valgrind CTest runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Findvalgrind.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FlowCommands.cmake -->
# sources/storage-engines/foundationdb/cmake/FlowCommands.cmake

## Purpose
Defines the core FoundationDB target-building DSL for Flow/C++ sources, actor compilation, coverage XML, header copying, and stripped package binaries.

## Important APIs, Types, and Functions
Defines target properties `SOURCE_FILES` and `COVERAGE_FILTERS`, `generate_coverage_xml`, `strip_debug_symbols`, `copy_headers`, and `add_flow_target`.

## Control Flow and Integration
`add_flow_target` expands `.actor.*` inputs into generated `.actor.g.*` files using actor compiler commands, creates executable/static/dynamic/link-test targets, wires fdboptions dependencies, marks generated files, emits coverage targets, and creates strip/debug-symbol package targets. It also passes `COMPILATION_UNIT` compile definitions when enabled.

## State and Persistence
Depends on `ACTORCOMPILER_COMMAND`, `coveragetool_command`, `fdboptions`, CMake target properties, platform strip/objcopy tools, and helper functions from `utils.cmake`.

## Dependencies
State is extensive: generated actor files, custom targets, target properties, package-stripped binaries under `packages/bin` or `packages/lib`, and coverage XML files.

## Risks and Test Signals
Risks include generated-file dependency mistakes, broad global output directory changes for link tests, coverage filter property mismatch, and platform strip behavior. Test signals are successful actor generation, target builds, coverage XML, and package stripped artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/FlowCommands.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/GenerateModulemap.cmake -->
# sources/storage-engines/foundationdb/cmake/GenerateModulemap.cmake

## Purpose
Generates Swift module maps and VFS overlays for C++ headers of a CMake target.

## Important APIs, Types, and Functions
Defines `generate_modulemap(out module target OMIT ... HEADERS ...)`.

## Control Flow and Integration
The function reads target `HEADER_FILES` unless explicit headers are provided, builds `header` entries while omitting requested names, detects generated vs source headers, and configures `empty.modulemap` and `headeroverlay.yaml` templates.

## State and Persistence
Depends on target header properties set by `FlowCommands.cmake`, CMake path operations, and Swift build support templates.

## Dependencies
Generated `module.modulemap` and `headeroverlay.yaml` persist under the requested output directory.

## Risks and Test Signals
Risks include heuristic directory handling for only a few nesting levels and source/generated path overlay mismatches. Test signals are Swift compilation importing the generated module.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/GenerateModulemap.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/GetFmt.cmake -->
# sources/storage-engines/foundationdb/cmake/GetFmt.cmake

## Purpose
Provides fmt dependency acquisition for the FoundationDB build.

## Important APIs, Types, and Functions
Runs `find_package(fmt 11.1.4 EXACT CONFIG)` and falls back to FetchContent from `fmtlib/fmt` tag `11.1.4`.

## Control Flow and Integration
Consumers include this file before linking `fmt` targets. If no installed exact config exists, the dependency is added from source.

## State and Persistence
Depends on installed fmt config or network access to GitHub.

## Dependencies
FetchContent source/build state persists under the build tree.

## Risks and Test Signals
Risks include unverified FetchContent git tag and exact-version rigidity. Test signal is `fmt` target availability and successful downstream link.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/GetFmt.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/GetMsgpack.cmake -->
# sources/storage-engines/foundationdb/cmake/GetMsgpack.cmake

## Purpose
Normalizes msgpack C++ dependency discovery behind an interface target.

## Important APIs, Types, and Functions
Finds legacy/new msgpack package names, creates `msgpack` interface target, links to detected imported targets, or downloads msgpack-c 3.3.0 with SHA256 via ExternalProject.

## Control Flow and Integration
Downstream code links `msgpack`; the module hides whether the dependency came from config packages or external headers.

## State and Persistence
Depends on msgpack CMake packages or the pinned release tarball.

## Dependencies
State includes ExternalProject source dir and `msgpack` interface include directories/dependencies.

## Risks and Test Signals
Risks include multiple msgpack package naming variants and header-only external project not rebuilding if include path changes. Test signal is C++ compilation using msgpack headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/GetMsgpack.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/InstallLayout.cmake -->
# sources/storage-engines/foundationdb/cmake/InstallLayout.cmake

## Purpose
Defines FoundationDB package layouts, CPack metadata, multiversion scripts, Docker packaging copies, and server/client install destinations.

## Important APIs, Types, and Functions
Includes `FDBInstall`, registers `TGZ`, `DEB`, `EL9`, and `VERSIONED` packages, sets logical dirs, configures CPack RPM/DEB/TGZ variables, and installs configuration/service/init files.

## Control Flow and Integration
The module maps package types to filesystem destinations, configures multiversion postinst/prerm scripts, sets component dependencies and filenames, creates empty log/data/etc dirs, excludes RPM auto filelist paths, and installs server config/service assets.

## State and Persistence
Depends on `FDBInstall.cmake`, packaging templates/scripts, project version variables, CPack, systemd/init assets, and package component names.

## Dependencies
State persists in package install variables, generated packaging scripts under `packaging/multiversion`, copied Docker assets, random cluster description cache strings, and CPack variables.

## Risks and Test Signals
Risks include duplicate symlink helper definitions, package filename/version drift, architecture-specific Debian naming, and random cluster descriptions in cache. Test signals are CPack RPM/DEB/TGZ outputs and package install/uninstall tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/InstallLayout.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Jemalloc.cmake -->
# sources/storage-engines/foundationdb/cmake/Jemalloc.cmake

## Purpose
Builds a custom jemalloc 5.3.0 dependency when system jemalloc is not used.

## Important APIs, Types, and Functions
Creates interface `jemalloc`, imported `jemalloc::jemalloc`, imported `jemalloc_pic::jemalloc_pic`, and ExternalProject `Jemalloc_project`.

## Control Flow and Integration
If `USE_JEMALLOC` is off the module returns. Otherwise it downloads the pinned jemalloc tarball, configures static/profile-enabled jemalloc with current C/C++ compilers, runs make/install, and points imported targets at the produced libraries.

## State and Persistence
Depends on ExternalProject, make, configured compilers, and jemalloc release archive/hash.

## Dependencies
State persists in `${CMAKE_BINARY_DIR}/jemalloc` and imported target dependencies/properties.

## Risks and Test Signals
Risks include source build tool availability, static/PIC target assumptions, and profile-enabled build differences. Test signal is FDB link against `jemalloc::jemalloc` or PIC library.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Jemalloc.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/RocksDBVersion.cmake -->
# sources/storage-engines/foundationdb/cmake/RocksDBVersion.cmake

## Purpose
Source-controlled configuration selecting the RocksDB release or commit used by FoundationDB.

## Important APIs, Types, and Functions
Currently sets `ROCKSDB_VERSION` to `9.7.3` and `ROCKSDB_VERSION_SHA256`; alternative commented variables allow `ROCKSDB_GIT_HASH` and `ROCKSDB_GIT_HASH_SHA256`.

## Control Flow and Integration
`CompileRocksDB.cmake` includes this file, validates mutual exclusivity, generates version macros, and builds/downloads RocksDB using these values.

## State and Persistence
Depends on RocksDB GitHub archive naming and maintainers keeping SHA256 values synchronized.

## Dependencies
State is source-controlled CMake variables; no generated files here.

## Risks and Test Signals
Risks include enabling both options, wrong SHA256, or changing version without updating generated-header expectations. Test signal is successful `CompileRocksDB.cmake` configure and archive verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/RocksDBVersion.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Sandbox.conf.cmake -->
# sources/storage-engines/foundationdb/cmake/Sandbox.conf.cmake

## Purpose
Template for a local sandbox `foundationdb.conf` used by build-tree development clusters.

## Important APIs, Types, and Functions
Defines `[fdbmonitor]`, `[general]`, default `[fdbserver]`, and `[fdbserver.4000]` sections with build-tree binary, cluster, data, and log paths.

## Control Flow and Integration
Configured by CMake for local cluster/sandbox runs so fdbmonitor launches the just-built `fdbserver` with build-local storage and logs.

## State and Persistence
Depends on `CMAKE_BINARY_DIR` substitution and built `bin/fdbserver`.

## Dependencies
Runtime state is external to the template: generated config, cluster file, data dir, and log dir under the CMake binary tree.

## Risks and Test Signals
Risks include build-tree path invalidation after moving directories and single-process defaults not matching production. Test signal is local sandbox cluster startup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/Sandbox.conf.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/SwiftCrossCompileForceModuleRebuild.cmake -->
# sources/storage-engines/foundationdb/cmake/SwiftCrossCompileForceModuleRebuild.cmake

## Purpose
Forces Swift builtin modules to rebuild from `.swiftinterface` files during cross-compilation.

## Important APIs, Types, and Functions
Defines `swift_force_import_rebuild_of_stdlib()`.

## Control Flow and Integration
The function rewrites `CMAKE_Swift_FLAGS` into frontend-safe flags, adds strict implicit module context, compiles tiny `import Swift` and `import CxxStdlib` Swift files, and fails if either import/rebuild fails.

## State and Persistence
Depends on Swift compiler, correct resource-dir/sysroot flags, and cross-compile toolchain setup from `ConfigureCompiler.cmake`/toolchain file.

## Dependencies
Temporary Swift source/object files persist under `CMakeTmp`; no project outputs are installed.

## Risks and Test Signals
Risks include brittle flag tokenization on spaces and strict module rebuild failures with mismatched host/target Swift versions. Test signal is configure-time successful import of Swift and CxxStdlib.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/SwiftCrossCompileForceModuleRebuild.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/SwiftToCXXInterop.cmake -->
# sources/storage-engines/foundationdb/cmake/SwiftToCXXInterop.cmake

## Purpose
Creates custom targets that emit C++ headers for Swift modules using Swift's reverse C++ interoperability.

## Important APIs, Types, and Functions
Defines `add_swift_to_cxx_header_gen_target(target_name header_target_name header_path SOURCES ... FLAGS ...)`.

## Control Flow and Integration
The function verifies Swift reverse interop support/version, resolves Swift sources, extracts selected flags from `CMAKE_Swift_FLAGS`, then runs `swiftc -frontend -typecheck -emit-clang-header-path` with target include dirs and frontend options.

## State and Persistence
Depends on Swift toolchain `experimental-interoperability-version.json`, Swift compiler frontend, target include properties, and `FindSwiftLibs`/`CompilerChecks` includes.

## Dependencies
Generated C++ header persists at `header_path` and is represented by `header_target_name`.

## Risks and Test Signals
Risks include regex flag extraction missing quoted/complex flags, toolchain version gating, and header generation not tracking all transitive module dependencies. Test signal is generated header and successful C++ compilation against Swift APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/SwiftToCXXInterop.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/awssdk.cmake -->
# sources/storage-engines/foundationdb/cmake/awssdk.cmake

## Purpose
Builds a static AWS SDK C++ core dependency bundle for FoundationDB S3 backup support.

## Important APIs, Types, and Functions
Defines ExternalProject `awssdk_project`, imported static targets for AWS core/CRT/C libraries, curl, zlib, and interface target `awssdk_target`.

## Control Flow and Integration
The module checks libc++ compiler flags, fetches a pinned AWS SDK commit, builds only core with static libs, BYO crypto, curl, and zlib, then wires a long dependency-ordered link list into `awssdk_target`.

## State and Persistence
Depends on GitHub aws-sdk-cpp, CMake ExternalProject, current C++ compiler, curl/zlib produced by the AWS build, and static library paths under `lib64`/external install.

## Dependencies
State persists in `awssdk-src`, `awssdk-build`, installed static libraries, and imported target properties.

## Risks and Test Signals
Risks include dependency order fragility, ABI mismatch when compiler/libc++ flags are incomplete, large external build cost, and hard-coded library paths. Test signal is successful `BUILD_AWS_BACKUP` link and S3 backup tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/awssdk.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/benchmark-download.cmake -->
# sources/storage-engines/foundationdb/cmake/benchmark-download.cmake

## Purpose
ExternalProject bootstrap project used by `FDBBenchmark.cmake` to download Google Benchmark and Googletest sources.

## Important APIs, Types, and Functions
Declares `googlebenchmark` and dependent `googletest` ExternalProjects with pinned commits and shallow clones.

## Control Flow and Integration
`FDBBenchmark.cmake` copies this file as a standalone CMakeLists, configures/builds it, then adds the downloaded benchmark source directory to the main build.

## State and Persistence
Depends on Git, GitHub availability, and the pinned benchmark/googletest commits.

## Dependencies
State is downloaded source/build trees under `googlebenchmark-download`.

## Risks and Test Signals
Risks include no hash verification for git clones and old dependency versions. Test signal is populated `googlebenchmark-src` with googletest before benchmark target configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/benchmark-download.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/foundationdb-client.pc.in -->
# sources/storage-engines/foundationdb/cmake/foundationdb-client.pc.in

## Purpose
Pkg-config template for the FoundationDB C client library.

## Important APIs, Types, and Functions
Defines `libdir`, `includedir`, package `Name`, `Description`, `Version`, `Libs`, and `Cflags`.

## Control Flow and Integration
`fdb_configure_and_install` configures this per package/install destination so C clients can discover `-lfdb_c` and include paths.

## State and Persistence
Depends on `LIB_DIR`, `INCLUDE_DIR`, and `FDB_VERSION` substitutions.

## Dependencies
Configured `.pc` files persist in package install trees.

## Risks and Test Signals
Risks include wrong libdir for EL9 lib64 layouts or versioned packages. Test signal is `pkg-config --libs --cflags foundationdb-client` after install.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/foundationdb-client.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/toolchain/macos-to-linux.cmake -->
# sources/storage-engines/foundationdb/cmake/toolchain/macos-to-linux.cmake

## Purpose
CMake toolchain file for cross-compiling FoundationDB from macOS to x86_64 Linux with Swift/C++ interop.

## Important APIs, Types, and Functions
Sets `FOUNDATIONDB_CROSS_COMPILING`, Linux system name/processor, Swift/Clang/LLD/LLVM tools, Mono, Python3, sysroot, external GCC toolchain, C/C++ flags, Boost cross flags, and disables Mach-O search path behavior.

## Control Flow and Integration
CMake reads this before project configuration. It validates required toolchain roots and container root, wires compilers/linker/ar/ranlib, discovers host Python, and forces sysroot/target flags.

## State and Persistence
Depends on `FOUNDATIONDB_SWIFT_TOOLCHAIN_ROOT`, `FOUNDATIONDB_LLVM_TOOLCHAIN_ROOT`, `FOUNDATIONDB_LINUX_CONTAINER_ROOT`, Mono framework paths, and devtoolset-11 inside sysroot.

## Dependencies
State is forced CMake cache variables; no generated files here.

## Risks and Test Signals
Risks include hard-coded x86_64 target, hard-coded Mono/devtoolset paths, and host `which python3` variability. Test signal is a complete cross-configure and Swift stdlib rebuild.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/toolchain/macos-to-linux.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/user-config.jam.cmake -->
# sources/storage-engines/foundationdb/cmake/user-config.jam.cmake

## Purpose
Boost.Build user-config template generated for source-built Boost.

## Important APIs, Types, and Functions
Contains `using <toolset>` with compiler and additional options, plus zstd include/search configuration.

## Control Flow and Integration
`CompileBoost.cmake` configures this into the build tree and passes it to b2 via `--user-config` so Boost uses the same compiler/linker settings as FoundationDB.

## State and Persistence
Depends on `BOOST_TOOLSET`, `BOOST_CXX_COMPILER`, `BOOST_ADDITIONAL_COMPILE_OPTIONS`, and `CMAKE_BINARY_DIR` substitutions.

## Dependencies
Configured `user-config.jam` persists in the CMake binary directory.

## Risks and Test Signals
Risks include stale options after reconfiguring toolchains and zstd version/path assumptions. Test signal is successful Boost ExternalProject build.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/user-config.jam.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/utils.cmake -->
# sources/storage-engines/foundationdb/cmake/utils.cmake

## Purpose
Provides general CMake utility functions for source classification, path manipulation, source discovery, and gRPC/protobuf generation.

## Important APIs, Types, and Functions
Defines `is_header`, `remove_prefix`, `is_prefix`, `create_build_dirs`, `fdb_find_sources`, `package_name_to_path`, `package_name_to_proto_target`, and `generate_grpc_protobuf`.

## Control Flow and Integration
Flow build files use these helpers to prepare generated directories and collect sources. gRPC users call `generate_grpc_protobuf`, which creates a static target, sets include/link dependencies, invokes protobuf generation for `.pb` and `.grpc.pb` outputs, and marks generated files to skip linting.

## State and Persistence
Depends on Protobuf and gRPC CMake functions/targets and current source/binary directory context.

## Dependencies
State includes created build directories, generated protobuf sources under `${CMAKE_BINARY_DIR}/generated`, and CMake target properties.

## Risks and Test Signals
Risks include glob-based source discovery hiding new file types, absolute-path handling in `create_build_dirs`, and generated source target property assumptions. Test signals are target generation and successful protobuf/gRPC compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/cmake/utils.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/CMakeLists.txt

## Purpose
Adds third-party and contrib libraries/tools used by FoundationDB.

## Important APIs, Types, and Functions
Creates `rapidjson` interface include target and adds subdirectories for crc32, stacktrace, folly_memcpy, rapidxml, sqlite, SimpleOpt, md5, libb64, plus non-Windows linenoise/debug_determinism/monitoring.

## Control Flow and Integration
Top-level FoundationDB CMake includes this directory to make bundled contrib dependencies available to main targets.

## State and Persistence
Depends on the listed contrib directories and platform variable `WIN32`.

## Dependencies
State is the CMake targets exported by each contrib subdirectory; no files generated here directly.

## Risks and Test Signals
Risks include missing subdirectories and platform-only tools not being built on Windows. Test signal is successful configuration of all contrib subdirectories.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Implib.so/arch/aarch64/config.ini -->
# sources/storage-engines/foundationdb/contrib/Implib.so/arch/aarch64/config.ini

## Purpose
Architecture metadata for the POSIX import-library generator on aarch64.

## Important APIs, Types, and Functions
Defines `PointerSize = 8` and `SymbolReloc = R_AARCH64_ABS64` in an `[Arch]` section.

## Control Flow and Integration
`implib-gen.py` selects this file when the target triple starts with aarch64/armv8 and uses it to parse relocated vtable/data entries.

## State and Persistence
Depends on GNU readelf relocation type names matching `R_AARCH64_ABS64`.

## Dependencies
No dynamic state; static config file.

## Risks and Test Signals
Risks include incomplete relocation coverage for more complex aarch64 shared objects. Test signal is generated trampolines/import wrapper for an aarch64 ELF library.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Implib.so/arch/aarch64/config.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Implib.so/arch/x86_64/config.ini -->
# sources/storage-engines/foundationdb/contrib/Implib.so/arch/x86_64/config.ini

## Purpose
Architecture metadata for the POSIX import-library generator on x86_64.

## Important APIs, Types, and Functions
Defines 8-byte pointer size and relocation type `R_X86_64_64`.

## Control Flow and Integration
`implib-gen.py` reads this when target architecture is x86_64 and uses it while reconstructing relocated data/vtable definitions.

## State and Persistence
Depends on readelf relocation names for x86_64 ELF.

## Dependencies
No dynamic state; static config file.

## Risks and Test Signals
Risks include not handling relative or GOT relocation forms for all exported data cases. Test signal is wrapper generation for x86_64 shared libraries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Implib.so/arch/x86_64/config.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Implib.so/implib-gen.py -->
# sources/storage-engines/foundationdb/contrib/Implib.so/implib-gen.py

## Purpose
Generates static import-wrapper sources for POSIX shared libraries by inspecting exported ELF symbols and emitting architecture-specific trampolines plus C++ initialization code.

## Important APIs, Types, and Functions
Defines helpers `warn`, `error`, `run`, `make_toc`, `parse_row`, `collect_syms`, `collect_relocs`, `collect_sections`, `read_unrelocated_data`, `collect_relocated_data`, `generate_vtables`, and `main` CLI handling.

## Control Flow and Integration
The script normalizes target architecture, reads `arch/<target>/config.ini`, runs `readelf`/`c++filt`, filters exported non-versioned functions, optionally reads a symbol list/filter/prefix, optionally reconstructs vtable data, and writes `<library>.tramp.S` and `<library>.init.cpp` from templates.

## State and Persistence
Depends on Python3, GNU `readelf`, `c++filt`, architecture templates, common init template, ELF symbol formats, and config.ini relocation metadata.

## Dependencies
Generated wrapper files persist in `--outdir`; no in-place source state is changed. Subprocesses run with English locale for parsable output.

## Risks and Test Signals
Risks include treating any stderr from tools as fatal, lack of versioned symbol support, fragile parsing across binutils versions, and experimental vtable interception. Test signals are generated assembly/C++ compiling and linking against the target library.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Implib.so/implib-gen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTest.sh -->
# sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTest.sh

## Purpose
Joshua entrypoint for the legacy binding tester package.

## Important APIs, Types, and Functions
Sets script directory, enables core dumps, unsets external client directory, creates a per-process temp work directory, and invokes `bindingTestScript.sh 1` with test environment variables.

## Control Flow and Integration
Joshua copies this as `joshua_test`; when run from a package directory it prepares isolation and delegates all cluster/test work to the main script.

## State and Persistence
Depends on sibling `bindingTestScript.sh` and package layout with binaries/scripts in the working directory.

## Dependencies
Runtime state is `tmp/$$` under the current directory, core dump settings, and environment variables.

## Risks and Test Signals
Risks include temp directory collisions only guarded by PID and inherited environment leakage except for one unset variable. Test signal is one successful binding tester cycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTestScript.sh -->
# sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTestScript.sh

## Purpose
Main legacy Joshua binding tester runner that starts a local cluster, runs binding tests, and saves diagnostics on failure.

## Important APIs, Types, and Functions
Uses `localClusterStart.sh` functions such as `startCluster`, `stopCluster`, and `displayMessage`; configures `BINDIR`, `LIBDIR`, `PYTHONDIR`, `testScript`, `SAVEONERROR`, and `VERSION`.

## Control Flow and Integration
After argument validation it starts a cluster, traps exit to stop it, runs `tests/bindingtester/run_binding_tester.sh` with `PYTHONPATH`, `LD_LIBRARY_PATH`, `FDB_CLUSTER_FILE`, console logging, and cycle count. On failure it captures directory listings, processes, cluster file, severity-40 logs, netstat, disk, and environment.

## State and Persistence
Depends on package-local binaries, Python bindings, binding tester shell script, local cluster script, grep/netstat/df/ps, and LD_LIBRARY_PATH behavior.

## Dependencies
Runtime state includes cluster files/logs from `localClusterStart.sh`, console log, error logs, and optional diagnostics under `LOGDIR`.

## Risks and Test Signals
Risks include shell word-splitting from unquoted source, Linux-centric diagnostics, and cleanup only if `stopCluster` succeeds. Test signal is exit status plus captured logs and severity errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTestScript.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTimeout.sh -->
# sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTimeout.sh

## Purpose
Joshua timeout diagnostic script for the legacy binding tester package.

## Important APIs, Types, and Functions
Scans for `startcluster.log`, `fdbclient.log`, and `console.log`, printing useful content when a binding test times out.

## Control Flow and Integration
If startup logs contain `Could not create database`, it prints those logs and related fdbclient logs, then always prints console logs found under the current tree.

## State and Persistence
Depends on `find`, `grep`, `cat`, and expected log names from `bindingTestScript.sh`/local cluster startup.

## Dependencies
No persistent state is written; it reads logs produced by the test run.

## Risks and Test Signals
Risks include unbounded log output and backtick-based `find` loops misbehaving on paths with whitespace. Test signal is informative timeout output in Joshua.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/bindingTimeout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/binding_test_start.sh -->
# sources/storage-engines/foundationdb/contrib/Joshua/scripts/binding_test_start.sh

## Purpose
Joshua entrypoint for the newer `bindingtester2` package using `contrib/local_cluster` Python tooling.

## Important APIs, Types, and Functions
Runs with `set -e` and `pipefail`, then executes `python3 ./binding_test.py` with fdbserver/fdbcli/libfdb paths, operation counts, concurrency, timeout, random mode, and tees output to `output.log`.

## Control Flow and Integration
Packaged as `joshua_test` by `package_bindingtester2`; it expects to run from the package root containing binaries and `binding_test.py`.

## State and Persistence
Depends on Python3, packaged `binding_test.py`, fdbserver/fdbcli/libfdb, and tee.

## Dependencies
Runtime state is `output.log` and any local-cluster artifacts created by `binding_test.py`.

## Risks and Test Signals
Risks include hard-coded workload sizes/timeouts and package-root assumptions. Test signal is zero exit status from binding_test.py and captured output.log.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/binding_test_start.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/binding_test_timeout.sh -->
# sources/storage-engines/foundationdb/contrib/Joshua/scripts/binding_test_timeout.sh

## Purpose
Simple timeout reporter for the newer binding tester package.

## Important APIs, Types, and Functions
Prints `Binding test timed out` and cats `output.log`.

## Control Flow and Integration
Joshua uses this as `joshua_timeout` for `bindingtester2` packages so timeout output includes the tee'd test stream.

## State and Persistence
Depends on the start script creating `output.log` before timeout.

## Dependencies
No state is written; reads `output.log` from the test working directory.

## Risks and Test Signals
Risks include missing `output.log` causing a secondary error and no additional cluster diagnostics. Test signal is visible timeout transcript in Joshua output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/binding_test_timeout.sh -->
