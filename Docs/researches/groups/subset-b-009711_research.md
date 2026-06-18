# Research Group subset-b-009711

This grouped report covers NFS-Ganesha CMake discovery/build helpers, the generated-parser configuration subsystem, URL-backed config support, and shipped sample configuration fragments. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLTTng.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLTTng.cmake

## Purpose

`FindLTTng.cmake` discovers the LTTng userspace tracing development files and command-line tool for optional tracepoint support in NFS-Ganesha. It supports an explicit `LTTNG_PATH_HINT`, locates UST and control headers/libraries, and exports variables used by higher-level build logic when enabling LTTng instrumentation.

## Important APIs, Types, and Functions

The module defines CMake cache/results variables `LTTNG_FOUND`, `LTTNG_EXECUTABLE`, `LTTNG_LIBRARIES`, `LTTNG_INCLUDE_DIR`, `LTTNG_CTL_LIBRARIES`, and `LTTNG_CTL_INCLUDE_DIR`. Discovery is performed with `find_path`, `find_library`, `find_program`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

If `LTTNG_PATH_HINT` is set, the module reports that hint and uses it in all path searches. It first finds `lttng/tracepoint.h`, the `liblttng-ust.so` directory, `lttng-ust`, and `uuid`. It then optionally finds `lttng-ust-common`, adding it to `LTTNG_LIBRARIES` when present. A second pass finds `lttng/lttng.h` and `lttng-ctl`, then searches for an `lttng` or `lttng-ctl` executable.

## State and Persistence Behavior

State is limited to CMake cache variables and advanced cache entries for include/library directories. There is no filesystem mutation beyond CMake cache/configure behavior.

## Dependencies and Integration Points

The module depends on LTTng UST, LTTng control headers/libraries, `libuuid`, and CMake's `FindPackageHandleStandardArgs`. It integrates with targets that compile generated tracepoint code or link Ganesha against LTTng support.

## Risks and Edge Cases

`LTTNG_LIBRARIES` includes `UUID_LIBRARY` but package handling does not require `LTTNG_EXECUTABLE` or `LTTNG_CTL_LIBRARY`, despite separately discovering them. The second `find_program` mistakenly writes to `LEX_PROGRAM`, so default-path executable discovery may not update `LTTNG_EXECUTABLE`. Reusing `LTTNG_LIBRARY_DIR` for both UST and UST common can also hide partial installs.

## Test Signals

Useful signals are configure runs with and without `LTTNG_PATH_HINT`, builds with `USE_LTTNG`, generated trace header dependencies, and link checks confirming `lttng-ust`, optional `lttng-ust-common`, `lttng-ctl`, and `uuid` are all resolvable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLTTng.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLibACL.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLibACL.cmake

## Purpose

`FindLibACL.cmake` probes POSIX ACL header and library capabilities used by Ganesha ACL handling. It distinguishes Linux-style `acl/libacl.h` with `libacl` from systems such as FreeBSD that expose ACL APIs directly through `sys/acl.h`.

## Important APIs, Types, and Functions

The module uses `check_include_files`, `find_library`, `check_library_exists`, and `check_symbol_exists`. It sets feature variables such as `HAVE_SYS_ACL_H`, `HAVE_ACL_LIBACL_H`, `LIBACL_LIBRARY`, `HAVE_LIBACL`, `HAVE_ACL_GET_FD_NP`, and `HAVE_ACL_SET_FD_NP`.

## Control Flow

The configure step checks for `sys/acl.h` and `acl/libacl.h`, searches for library `acl`, validates `acl_get_file` when the libacl header is available, and checks FreeBSD-style `acl_get_fd_np` and `acl_set_fd_np` symbols when `sys/acl.h` exists.

## State and Persistence Behavior

All outputs are CMake feature/cache variables consumed by generated `config.h` or conditional build logic. The module does not create files or targets.

## Dependencies and Integration Points

It depends on CMake check modules being included by the parent build and on platform ACL headers/libraries. Results affect FSAL and permission code that needs ACL calls.

## Risks and Edge Cases

There is no `FindPackageHandleStandardArgs` call or canonical `LIBACL_FOUND`, so callers must rely on individual feature variables. Header/library mismatches can produce partial capability flags. `check_library_exists` is guarded by `HAVE_ACL_LIBACL_H`, which is reasonable on Linux but may miss nonstandard packaging.

## Test Signals

Configure on Linux with `libacl-devel`, Linux without it, and FreeBSD-like environments should exercise the expected combinations. Compile tests for files using `acl_get_file`, `acl_get_fd_np`, and `acl_set_fd_np` confirm the feature variables are wired correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLibACL.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindMSan.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindMSan.cmake

## Purpose

`FindMSan.cmake` adds optional MemorySanitizer support to selected targets. It exposes the `SANITIZE_MEMORY` option, validates platform constraints, probes compiler flags, and provides `add_sanitize_memory(TARGET)`.

## Important APIs, Types, and Functions

The main API is the CMake function `add_sanitize_memory`. It delegates flag probing and target mutation to `sanitizer_check_compiler_flags` and `sanitizer_add_flags` from `sanitize-helpers.cmake`.

## Control Flow

When `SANITIZE_MEMORY` is enabled, the module rejects non-Linux systems and non-64-bit builds by forcing the cache option back off. On a supported platform it checks `-g -fsanitize=memory` under the `MSan` prefix. `add_sanitize_memory` returns immediately if disabled; otherwise it appends the detected MSan flags to the target compile and link flags.

## State and Persistence Behavior

State is held in CMake cache variables such as `SANITIZE_MEMORY` and `MSan_<compiler>_FLAGS`. Target state is mutated through `COMPILE_FLAGS` and `LINK_FLAGS`.

## Dependencies and Integration Points

The module depends on `sanitize-helpers.cmake`, enabled CMake languages, and compiler support for MemorySanitizer. It is invoked indirectly by `FindSanitizers.cmake` and `add_sanitizers`.

## Risks and Edge Cases

MSan requires instrumented dependencies to avoid false positives and uninitialized data from external libraries, but the module only checks compiler flag availability. Warning messages reference `${TARGET}` during configure-time option checks even though no target is in scope. MSan is incompatible with TSan by policy in the sibling TSan module.

## Test Signals

Configure with Clang on 64-bit Linux and `-DSANITIZE_MEMORY=ON`, then verify selected targets receive `-fsanitize=memory`. Negative signals include non-Linux or 32-bit configure runs forcing the option off and mixed-compiler targets being rejected by helper logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindMSan.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNTIRPC.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNTIRPC.cmake

## Purpose

`FindNTIRPC.cmake` discovers the libntirpc RPC implementation required by NFS-Ganesha. It supports `NTIRPC_PREFIX`, locates headers and libraries, reads a version macro, and exposes optional tracepoint/monitoring libraries when present.

## Important APIs, Types, and Functions

The module sets `NTIRPC_FOUND`, `NTIRPC_INCLUDE_DIR`, `NTIRPC_LIBRARY`, `NTIRPC_VERSION`, and optional `NTIRPC_TRACEPOINTS`, `NTIRPC_LTTNG`, and `NTIRPC_MONITORING`. It uses `find_path`, `find_library`, `file(READ)`, regex extraction, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

With `NTIRPC_PREFIX`, discovery first searches only under that prefix. If include or library directories remain unset, it retries with default paths. It then finds `ntirpc` and optional support libraries in the detected library directory, reads `${NTIRPC_INCLUDE_DIR}/version.h`, extracts `NTIRPC_VERSION`, and validates the required include/library pair.

## State and Persistence Behavior

State is CMake cache/configure state only. Include and library variables are marked advanced. No targets or files are created.

## Dependencies and Integration Points

It depends on libntirpc headers containing `rpc/xdr.h` and library `libntirpc.so`. The detected values feed core RPC transport builds, and optional tracing libraries may be used when tracepoint support is enabled.

## Risks and Edge Cases

The module includes `LibFindMacros` but does not use it. `find_library(... NO_DEFAULT_PATH)` is used even when no custom directory was found, so a missing `NTIRPC_LIBRARY_DIR` can prevent default library discovery. Version extraction defaults to `0.0.0` when `version.h` is absent, which can make diagnostics less precise.

## Test Signals

Configure against a system libntirpc, a custom prefix, and a prefix containing only headers or only libraries. Build/link of the Ganesha RPC stack is the strongest integration signal, while configure logs should show the extracted `NTIRPC_VERSION`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNTIRPC.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNfsIdmap.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNfsIdmap.cmake

## Purpose

`FindNfsIdmap.cmake` locates libnfsidmap headers and library for NFS identity mapping support.

## Important APIs, Types, and Functions

The module sets `NFSIDMAP_INCLUDE_DIR`, `NFSIDMAP_LIBRARY`, and `NFSIDMAP_FOUND` using `FIND_PATH` and `FIND_LIBRARY`. It emits status or fatal messages based on `NFSIDMAP_FIND_QUIETLY` and `NfsIdmap_FIND_REQUIRED`.

## Control Flow

Configure searches for `nfsidmap.h` and `libnfsidmap`. If both are present, `NFSIDMAP_FOUND` becomes true and a status message is emitted unless quiet. If either is missing and the package is required, configuration aborts.

## State and Persistence Behavior

Only CMake variables are mutated. There is no target creation or generated output.

## Dependencies and Integration Points

The result feeds build paths that need NFSv4 name-to-id mapping. It depends on libnfsidmap development packaging.

## Risks and Edge Cases

The module does not use `FindPackageHandleStandardArgs`, does not mark variables advanced, and has inconsistent package-name casing in required checks. It does not verify any symbols or version, so a stale incompatible library could pass discovery.

## Test Signals

Configure runs with and without `libnfsidmap-devel` validate required/optional behavior. Compile and link of idmapping code is needed to catch header/library ABI mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNfsIdmap.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRADOS.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRADOS.cmake

## Purpose

`FindRADOS.cmake` discovers Ceph librados for Ceph-backed FSALs, RADOS recovery storage, and RADOS-backed configuration URL support. It supports `RADOS_PREFIX`, locates headers/libraries, and checks for a required librados operation symbol.

## Important APIs, Types, and Functions

The module exports `RADOS_FOUND`, `RADOS_INCLUDE_DIR`, `RADOS_LIBRARY_DIR`, `RADOS_LIBRARY`, and `RADOS_LIBRARIES`. It uses `find_path`, `find_library`, `check_library_exists`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

With `RADOS_PREFIX`, it first searches only under the prefix for `rados/librados.h` and `librados.so`. Missing pieces are retried in default paths. It then finds library `rados` within `RADOS_LIBRARY_DIR` and validates symbol `rados_read_op_omap_get_vals2`. If the symbol check fails, it clears cached include/library directory variables. Package handling requires the include and library directories.

## State and Persistence Behavior

The module writes CMake cache variables and can unset stale cache entries. It does not create build targets.

## Dependencies and Integration Points

It depends on Ceph librados and CMake check modules. Results are consumed by Ceph FSAL, RADOS recovery, and `ganesha_rados_urls` module linkage.

## Risks and Edge Cases

`FIND_PACKAGE_HANDLE_STANDARD_ARGS` requires `RADOS_LIBRARY_DIR` but not `RADOS_LIBRARY`, so a directory can pass even if the actual library variable is problematic. The symbol check uses `RADOS_LIBRARY_DIR` as the location argument and assumes linker search behavior. The unconditional status message may print `RADOS_LIBRARY-NOTFOUND`.

## Test Signals

Configure against supported and too-old Ceph versions to validate the symbol gate. Build and link of `conf_url_rados.c`, FSAL_CEPH, and RADOS recovery code are key signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRADOS.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRDMA.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRDMA.cmake

## Purpose

`FindRDMA.cmake` discovers the paired libibverbs and librdmacm dependencies needed for RDMA transport support. It accepts a combined `RDMA_PATH_HINT` or component-specific `LIBIBVERBS_PREFIX` and `LIBRDMACM_PREFIX`.

## Important APIs, Types, and Functions

The module exports `RDMA_FOUND`, `RDMA_LIBRARY`, and `RDMA_INCLUDE_DIR`, plus component variables from `libfind_pkg_detect`/`libfind_process` for `IBVERBS` and `RDMACM`.

## Control Flow

It seeds pkg-config include and library directory hints for ibverbs and rdmacm, detects `infiniband/verbs.h` with `ibverbs`, detects `rdma/rdma_cma.h` with `rdmacm`, processes each component, and sets aggregate RDMA variables only if both are found. Final validation uses `FindPackageHandleStandardArgs`.

## State and Persistence Behavior

All state is CMake configure/cache state. Component discoveries may mark include/library options advanced through `LibFindMacros`.

## Dependencies and Integration Points

It depends on `LibFindMacros.cmake`, pkg-config when available, libibverbs, and librdmacm. It integrates with RPC/RDMA transport builds and any target linking RDMA support.

## Risks and Edge Cases

Both component libraries are mandatory for `RDMA_FOUND`; partial installs cannot enable a degraded mode. The aggregate variables are singular names containing lists, which is conventional here but can surprise callers expecting plural variables. Version detection is commented out, so ABI compatibility relies on compile/link failures.

## Test Signals

Configure with system RDMA packages, separate component prefixes, only one component installed, and no RDMA packages. A transport build that includes RDMA headers and links both libraries is the integration test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRDMA.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRGW.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRGW.cmake

## Purpose

`FindRGW.cmake` discovers Ceph RGW file-interface support for the RGW FSAL. It finds librgw headers/libraries, verifies core and optional symbols, and extracts the `rgw_file.h` version.

## Important APIs, Types, and Functions

The module exports `RGW_FOUND`, `RGW_INCLUDE_DIR`, `RGW_LIBRARY_DIR`, `RGW_LIBRARY`, `RGW_LIBRARIES`, `RGW_FILE_VERSION`, `USE_FSAL_RGW_MOUNT2`, and `USE_FSAL_RGW_XATTRS`. It uses `find_path`, `find_library`, `check_library_exists`, `file(STRINGS)`, regex extraction, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

With `RGW_PREFIX`, discovery searches only under that prefix first. It then falls back to default paths for `include/rados/librgw.h` and `librgw.so`. It finds `rgw`, checks for required `rgw_mount`, then probes optional `rgw_mount2` and `rgw_getxattrs` to set feature toggles. It reads version macros from `${RGW_INCLUDE_DIR}/include/rados/rgw_file.h` and validates include/library directory variables.

## State and Persistence Behavior

State is CMake cache/configuration state. It can clear include/library directory cache entries when the required symbol is missing.

## Dependencies and Integration Points

It depends on librgw from Ceph and CMake symbol checks. Results drive conditional compilation of RGW FSAL functionality and compatibility code paths for older librgw versions.

## Risks and Edge Cases

The header search name includes `include/rados/librgw.h`, so `RGW_INCLUDE_DIR` may be a prefix rather than a normal include directory. Optional feature flags are global variables that must be consumed consistently by compile definitions. Package handling does not require `RGW_LIBRARY` directly.

## Test Signals

Configure against Ceph versions with and without `rgw_mount2` and `rgw_getxattrs`. Compile/link of RGW FSAL and tests that exercise mount and xattr code paths confirm feature flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRGW.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindReadline.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindReadline.cmake

## Purpose

`FindReadline.cmake` locates GNU Readline headers and library for any interactive command or utility support built by NFS-Ganesha.

## Important APIs, Types, and Functions

It defines `READLINE_INCLUDE_DIR`, `READLINE_LIBRARY`, and `READLINE_FOUND` via `FIND_PATH` and `FIND_LIBRARY`, then emits status or fatal diagnostics based on `Readline_FIND_QUIETLY` and `Readline_FIND_REQUIRED`.

## Control Flow

The module searches for `readline/readline.h` and `libreadline`. If both are found, it marks the package found and reports the library unless quiet. If not found and required, it aborts configuration.

## State and Persistence Behavior

Only CMake variables are changed. There is no file generation or target mutation.

## Dependencies and Integration Points

It depends on GNU Readline development files. Consumers must add include directories and link libraries themselves based on the exported variables.

## Risks and Edge Cases

There is no symbol/version check and no `FindPackageHandleStandardArgs`. It does not include terminal dependency libraries such as `ncurses`, so final link may still fail on systems where readline does not carry transitive metadata.

## Test Signals

Configure with Readline installed/missing and link any utility that uses Readline. A stricter smoke test should compile a small include of `readline/readline.h` and link a `readline()` call.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindReadline.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindSanitizers.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindSanitizers.cmake

## Purpose

`FindSanitizers.cmake` is the umbrella sanitizer module. It exposes static sanitizer runtime linking and imports ASan, TSan, MSan, and UBSan modules, then provides helpers to apply all enabled sanitizers to one or more targets.

## Important APIs, Types, and Functions

The public APIs are option `SANITIZE_LINK_STATIC`, function `sanitizer_add_blacklist_file(FILE)`, and function `add_sanitizers(...)`. It relies on `add_sanitize_address`, `add_sanitize_thread`, `add_sanitize_memory`, and `add_sanitize_undefined` from component modules.

## Control Flow

The module maps `Sanitizers_FIND_QUIETLY` to `FIND_QUIETLY_FLAG`, finds each component sanitizer package, and defines helper functions. `sanitizer_add_blacklist_file` resolves relative paths against `CMAKE_CURRENT_SOURCE_DIR` and probes `-fsanitize-blacklist=<file>`. `add_sanitizers` iterates over every target argument and invokes each enabled sanitizer's target function.

## State and Persistence Behavior

It stores detected sanitizer and blacklist flags in CMake cache variables managed by `sanitize-helpers.cmake`. Target compile/link flags are mutated only when `add_sanitizers` is called.

## Dependencies and Integration Points

It depends on component modules `FindASan`, `FindTSan`, `FindMSan`, `FindUBSan`, and `sanitize-helpers.cmake`. `config_parsing/CMakeLists.txt` uses `add_sanitizers(config_parsing)` and applies it to the RADOS URL module when built.

## Risks and Edge Cases

The module does not enforce sanitizer compatibility itself beyond component modules; users can still request combinations that fail at link/runtime. `-fsanitize-blacklist` has been renamed in newer Clang to ignorelist, so modern compilers may need updated flag candidates. Static sanitizer runtime linking is only attempted for GNU compilers in helper logic.

## Test Signals

Configure with each sanitizer option alone and in invalid combinations, then inspect target flags and build sanitized binaries. Runtime smoke tests should verify instrumented targets start and report sanitizer findings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindSanitizers.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTSan.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTSan.cmake

## Purpose

`FindTSan.cmake` provides optional ThreadSanitizer instrumentation for selected targets. It validates compatibility with MemorySanitizer, platform, and pointer width, probes compiler support, and exposes `add_sanitize_thread(TARGET)`.

## Important APIs, Types, and Functions

The main public API is function `add_sanitize_thread`. It uses option `SANITIZE_THREAD`, flag candidate `-g -fsanitize=thread`, and helper functions `sanitizer_check_compiler_flags` and `sanitizer_add_flags`.

## Control Flow

If both `SANITIZE_THREAD` and `SANITIZE_MEMORY` are enabled, configuration stops with a fatal error. When TSan is enabled, non-Linux and non-64-bit systems force the option off with warnings. Supported configurations probe TSan flags. `add_sanitize_thread` appends detected compile/link flags to the target only when enabled.

## State and Persistence Behavior

The module writes `SANITIZE_THREAD` and `TSan_<compiler>_FLAGS` cache state and mutates target properties when used.

## Dependencies and Integration Points

It depends on `sanitize-helpers.cmake`, CMake enabled language metadata, and compiler/runtime TSan support. It is used through `FindSanitizers.cmake`.

## Risks and Edge Cases

ThreadSanitizer changes runtime behavior and can conflict with low-level threading code, atomics, or unsupported libraries. As with MSan, warning messages refer to `${TARGET}` during global option validation. Mixed-language targets using different compiler IDs are rejected later by helper logic.

## Test Signals

Configure 64-bit Linux with `-DSANITIZE_THREAD=ON`, inspect flags, and run threaded unit/integration tests. Negative tests should cover `SANITIZE_MEMORY` conflict, non-Linux, and 32-bit builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTSan.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTcMalloc.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTcMalloc.cmake

## Purpose

`FindTcMalloc.cmake` discovers Google's tcmalloc allocator library for optional allocator replacement or profiling support.

## Important APIs, Types, and Functions

It exports `TCMALLOC_FOUND`, `TCMALLOC_ROOT_DIR`, `TCMALLOC_INCLUDE_DIR`, `TCMALLOC_INCLUDE_DIRS`, `TCMALLOC_LIBRARY`, and `TCMALLOC_LIBRARIES`. It uses environment fallback from `$TCMALLOC_ROOT_DIR`, `FIND_PATH`, `FIND_LIBRARY`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

If the CMake variable is absent but the environment variable exists, it seeds `TCMALLOC_ROOT_DIR`. It builds a search list including common system and package-manager locations, searches for `tcmalloc.h` under `include/tcmalloc`, searches for library `tcmalloc`, validates both, and populates plural variables on success.

## State and Persistence Behavior

Only CMake cache/configure variables are mutated and marked advanced. No targets are created.

## Dependencies and Integration Points

It depends on gperftools/tcmalloc development files. Higher-level build logic can link `${TCMALLOC_LIBRARIES}` and include `${TCMALLOC_INCLUDE_DIRS}` for allocator support.

## Risks and Edge Cases

The header can be packaged under `gperftools/tcmalloc.h` on some distributions, while this module looks for `tcmalloc.h` with a fixed suffix. It does not check allocator symbols or distinguish minimal/full/profiler variants.

## Test Signals

Configure with distro gperftools packages and custom `TCMALLOC_ROOT_DIR`, then link a target with `TCMALLOC_LIBRARIES`. Missing-header and missing-library cases should produce clear package-handle diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindTcMalloc.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindToolchain.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindToolchain.cmake

## Purpose

`FindToolchain.cmake` records basic host toolchain facts for conditional build behavior. It detects MSVC on Windows and GNU gold linker on Unix.

## Important APIs, Types, and Functions

The module sets `MSVC` when `CMAKE_SYSTEM_NAME` matches Windows and `CMAKE_CXX_COMPILER_ID` matches MSVC. It sets `GOLD_LINKER` when `ld -V` succeeds and reports `GNU gold`.

## Control Flow

On Windows it checks the C++ compiler ID. On Unix it runs `execute_process(COMMAND ld -V)`, captures result and output, and scans for `GNU gold`. It finishes with a status message.

## State and Persistence Behavior

State is limited to CMake variables in the configure process. The only external process is `ld -V`; no files are created.

## Dependencies and Integration Points

It depends on CMake system/compiler variables and an `ld` executable in PATH on Unix. Consumers can conditionally set linker flags or workarounds based on `GOLD_LINKER`.

## Risks and Edge Cases

Hardcoding `ld -V` may not reflect the actual linker used by the compiler driver, especially with Clang, lld, mold, cross-compilers, or `-fuse-ld`. The `MSVC` variable duplicates CMake's built-in `MSVC` semantics and may be redundant.

## Test Signals

Configure on GNU ld, gold, lld, and Windows/MSVC environments and inspect the resulting variables. Linker-specific flags should be tested through an actual target link.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindToolchain.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUBSan.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUBSan.cmake

## Purpose

`FindUBSan.cmake` adds optional UndefinedBehaviorSanitizer support to selected targets.

## Important APIs, Types, and Functions

It exposes option `SANITIZE_UNDEFINED` and function `add_sanitize_undefined(TARGET)`. It delegates compiler probing and target flag mutation to `sanitize-helpers.cmake` under prefix `UBSan`.

## Control Flow

When enabled, the module probes `-g -fsanitize=undefined`. `add_sanitize_undefined` returns if disabled and otherwise appends detected UBSan compile/link flags to the target.

## State and Persistence Behavior

It writes CMake cache variables such as `SANITIZE_UNDEFINED` and `UBSan_<compiler>_FLAGS`, plus target `COMPILE_FLAGS` and `LINK_FLAGS` when applied.

## Dependencies and Integration Points

It depends on compiler UBSan support and the shared sanitizer helper module. It is invoked through `FindSanitizers.cmake` and `add_sanitizers`.

## Risks and Edge Cases

UBSan runtime behavior varies by compiler and may require additional recover/trap options that this module does not expose. It does not validate runtime library availability separately from compiler flag acceptance.

## Test Signals

Configure with `-DSANITIZE_UNDEFINED=ON`, build targets, and run tests that exercise integer, alignment, and nullability edge cases. Inspect target flags to confirm both compile and link instrumentation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUBSan.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUnwind.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUnwind.cmake

## Purpose

`FindUnwind.cmake` discovers libunwind headers and library for stack unwinding support.

## Important APIs, Types, and Functions

The module accepts `UNWIND_PATH_HINT` and exports `UNWIND_FOUND`, `UNWIND_INCLUDE_DIR`, `UNWIND_LIBRARY`, and `UNWIND_LIBRARIES`. It uses `find_path`, `find_library`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

The module reports a path hint when provided, searches for `libunwind.h` in include suffixes, searches for library `unwind` in `lib` and `lib64`, sets `UNWIND_LIBRARIES`, validates required include/library variables, and marks them advanced.

## State and Persistence Behavior

Only CMake cache/configure variables are changed.

## Dependencies and Integration Points

It depends on libunwind development files. Consumers can link `${UNWIND_LIBRARIES}` for crash diagnostics, stack traces, or backtrace-enabled logging.

## Risks and Edge Cases

Some platforms split libunwind into architecture-specific or local/unwind-generic libraries; this module only searches `unwind`. It does not check symbols or ABI flavor.

## Test Signals

Configure with and without `UNWIND_PATH_HINT`, then compile/link a small target that includes `libunwind.h` and calls an unwind API. Runtime stack capture is the final integration signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUnwind.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindWBclient.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindWBclient.cmake

## Purpose

`FindWBclient.cmake` discovers a Samba Winbind4-compatible `wbclient` installation for identity and SID lookup integration.

## Important APIs, Types, and Functions

The module exports `WBCLIENT_INCLUDE_DIR`, `WBCLIENT_LIBRARIES`, `WBCLIENT_LIB_OK`, `WBCLIENT_H`, `WBCLIENT4_H`, and `WBCLIENT_FOUND`. It uses optional pkg-config, `find_path`, `find_library`, `check_library_exists`, `check_include_files`, and `check_c_source_compiles`.

## Control Flow

When `SAMBA4_PREFIX` is provided, it seeds include and library paths. On non-Windows systems it queries pkg-config module `wbclient`. It finds `wbclient.h` and library `wbclient`, checks for symbol `wbcLookupSids`, validates header inclusion with `stdint.h` and `stdbool.h`, and compiles a probe that references `enum wbcAuthUserLevel` and `WBC_AUTH_USER_LEVEL_PAC` to distinguish Winbind4 headers.

## State and Persistence Behavior

State is CMake configure/cache variables only. `CMAKE_REQUIRED_INCLUDES` is appended when checking headers.

## Dependencies and Integration Points

It depends on Samba/winbind client development files. Results feed code that integrates with Winbind for SID/account lookup and authentication metadata.

## Risks and Edge Cases

The status message prints `${WBCLIENT_LIB}`, but the discovered variable is `WBCLIENT_LIBRARIES`, so diagnostics may be blank. Required variable casing uses `WBclient_FIND_REQUIRED`, which can miss canonical package casing. `CMAKE_REQUIRED_INCLUDES` is appended globally and not restored, potentially influencing later checks.

## Test Signals

Configure against Samba4 headers/libraries, older incompatible wbclient headers, and missing packages. Compile/link of code using `wbcLookupSids` and `WBC_AUTH_USER_LEVEL_PAC` verifies the detected ABI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindWBclient.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake

## Purpose

`GetGitRevisionDescription.cmake` provides configure-time functions for deriving Git revision metadata while forcing CMake to reconfigure when `.git/HEAD` or the referenced branch file changes.

## Important APIs, Types, and Functions

Public functions are `get_git_head_revision(<refspecvar> <hashvar>)`, `git_describe(<var> [args...])`, and `git_get_exact_tag(<var> [args...])`. Internal state includes `_gitdescmoddir`, `GIT_DATA`, generated `grabRef.cmake`, `HEAD_REF`, and `HEAD_HASH`.

## Control Flow

The module guards against multiple inclusion, captures its own directory at include time, and uses `GANESHA_TOP_CMAKE_DIR` as the starting point for `.git` search. `get_git_head_revision` walks upward to find `.git`, copies `.git/HEAD` into `CMakeFiles/git-data`, configures the `.in` helper, includes it, and returns the ref and hash. `git_describe` finds Git, obtains the hash, runs `git describe <hash> ...` in the top source tree, and stores a `-NOTFOUND`-style string on failure. `git_get_exact_tag` calls `git_describe --exact-match`.

## State and Persistence Behavior

The module writes generated files under `${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/git-data` so CMake tracks Git ref files as configure inputs. Returned revision variables are caller-scoped through `PARENT_SCOPE`.

## Dependencies and Integration Points

It depends on Git, CMake `configure_file`, and the companion `GetGitRevisionDescription.cmake.in`. It feeds version strings such as package release metadata, including RPM release values using `_GIT_HEAD_COMMIT_ABBREV`.

## Risks and Edge Cases

It assumes `GANESHA_TOP_CMAKE_DIR` is set. Worktrees or `.git` files that point elsewhere may not be handled because the code expects `.git/HEAD` under a directory. The TODO command-injection check is commented out, although `execute_process` argument lists reduce shell injection risk. Shallow or tagless clones can yield `-NOTFOUND` descriptions.

## Test Signals

Configure in normal branch, detached HEAD, tag, shallow clone, and non-Git source archive states. Verify CMake re-runs after committing or changing branch refs and that package version variables update.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake.in -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake.in

## Purpose

`GetGitRevisionDescription.cmake.in` is the configured helper used to read the active Git HEAD reference or detached commit and expose `HEAD_REF` and `HEAD_HASH` to the parent module.

## Important APIs, Types, and Functions

It uses configured placeholders `@HEAD_FILE@`, `@GIT_DIR@`, and `@GIT_DATA@`. It sets `HEAD_HASH` and conditionally `HEAD_REF`.

## Control Flow

The helper reads the copied HEAD file, strips whitespace, and checks whether it contains a symbolic `ref`. For named branches it removes `ref: `, copies either the ref file or its log into `git-data/head-ref`, and in the log fallback sets `HEAD_HASH` to the ref name. For detached HEAD it copies `.git/HEAD` to `head-ref`. If `HEAD_HASH` was not set, it reads and strips `head-ref`.

## State and Persistence Behavior

It copies Git metadata into the build tree so CMake can track reconfiguration dependencies. It does not directly run Git.

## Dependencies and Integration Points

It is configured and included only by `GetGitRevisionDescription.cmake`. Its output variables are consumed by `get_git_head_revision`.

## Risks and Edge Cases

The branch-log fallback sets `HEAD_HASH` to the ref path rather than parsing the latest hash from the log, which may be intentional for reconfigure tracking but is not a commit hash. The helper does not support linked worktree `.git` files. It limits reads to 1024 bytes, adequate for normal HEAD files.

## Test Signals

Configure from branch, detached HEAD, and a missing direct ref file with log fallback. Inspect generated `CMakeFiles/git-data/head-ref` and returned variables after branch changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallClobberImmune.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallClobberImmune.cmake

## Purpose

`InstallClobberImmune.cmake` defines an install-time macro for configuration files that should not overwrite administrator-modified files under the install prefix.

## Important APIs, Types, and Functions

The public API is macro `InstallClobberImmune(_srcfile _dstfile)`. It emits an `install(CODE "...")` script using `CMAKE_COMMAND -E compare_files` and `configure_file(COPYONLY)`.

## Control Flow

At install time, the generated script computes `_destfile`, prepending `$ENV{DESTDIR}` when set. If the destination exists, it skips overwriting, compares source and destination, and installs `${_destfile}.example` only when contents differ. If the destination is missing, it copies the source directly to the destination.

## State and Persistence Behavior

The macro persists files during `make install`, either the real destination or a `.example` sidecar. It intentionally avoids clobbering existing config files.

## Dependencies and Integration Points

It is included by `InstallPackageConfigFile.cmake` and used for packaging/install rules for Ganesha configuration files.

## Risks and Edge Cases

The install script uses interpolated paths, so paths containing unusual characters or semicolons require care. `configure_file` inside `install(CODE)` does not update CMake install manifests as a normal `install(FILES)` would, as the comment notes. Directory existence and permissions are assumed to be handled by surrounding install rules.

## Test Signals

Run install into an empty DESTDIR, then install again after modifying the destination. Verify the original file is preserved and an `.example` appears only when content differs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallClobberImmune.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallPackageConfigFile.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallPackageConfigFile.cmake

## Purpose

`InstallPackageConfigFile.cmake` wraps installation of user-editable configuration files. It chooses normal package-manager install semantics in binary packaging mode and clobber-immune install behavior for local installs, while also creating explicit example-config targets.

## Important APIs, Types, and Functions

The public API is macro `InstallPackageConfigFile(_srcfile _dstdir _dstfilename)`. It uses `InstallClobberImmune`, `install(FILES)`, cache variable `INSTALLED_CONFIG_FILES`, target `install-example-configs`, and per-file target `install-example-config-<flattened-src>`.

## Control Flow

The macro builds `_dstfile`. In `BINARY_PACKAGING_MODE`, it installs the source normally, records the installed config path in `INSTALLED_CONFIG_FILES`, and on Apple also installs a `.example` file. Otherwise it delegates to `InstallClobberImmune`. It then ensures a top-level example target exists, flattens slashes in the source path for a legal target name, creates a custom target that copies the source to `${DESTDIR}${_dstfile}.example`, and adds it as a dependency.

## State and Persistence Behavior

It creates install rules, custom targets, and a cache string recording config files for package scripts. Runtime installation may write real config files and example files.

## Dependencies and Integration Points

It depends on `InstallClobberImmune.cmake`, CMake install/custom target support, and package scripts that consume `INSTALLED_CONFIG_FILES`.

## Risks and Edge Cases

Flattening only replaces `/`, so other target-name-problem characters in source paths may remain. The custom example target uses `DESTDIR` expansion in a CMake command context and assumes the destination directory exists. The cache string accumulates space-separated paths, which can be fragile for paths with spaces.

## Test Signals

Configure with and without `BINARY_PACKAGING_MODE`, run normal install and `install-example-configs` into DESTDIR, and verify package scripts see `INSTALLED_CONFIG_FILES`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallPackageConfigFile.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/LibFindMacros.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/LibFindMacros.cmake

## Purpose

`LibFindMacros.cmake` provides reusable CMake helper macros/functions for writing find modules. It wraps dependency discovery, pkg-config probing, version-header extraction, and final package result processing.

## Important APIs, Types, and Functions

Public helpers are `libfind_package(PREFIX PKG ...)`, `libfind_pkg_check_modules(...)`, `libfind_pkg_detect(PREFIX ...)`, `libfind_version_header(PREFIX VERSION_H DEFINE_NAME [QUIET])`, and `libfind_process(PREFIX)`.

## Control Flow

`libfind_package` forwards `REQUIRED` from the parent package and records dependencies. `libfind_pkg_detect` parses `FIND_PATH` and `FIND_LIBRARY` sections, runs quiet pkg-config, then searches for requested headers/libraries using pkg-config hints. `libfind_version_header` reads a header and extracts a string-valued `#define`. `libfind_process` aggregates include/library option variables from the package and dependencies, removes duplicates, checks missing values, validates requested versions, marks variables advanced on success, exports plural result variables, or emits detailed fatal/warning diagnostics.

## State and Persistence Behavior

The helpers mutate CMake variables in parent scope and mark cache entries advanced or visible. They do not create files or targets.

## Dependencies and Integration Points

The module depends optionally on CMake `FindPkgConfig`. `FindRDMA.cmake` uses it for ibverbs/rdmacm component discovery, and other local find modules can reuse it.

## Risks and Edge Cases

There is a likely typo in `libfind_process`: `({i}_INCLUDE_DIR STREQUAL ...` lacks `${`, which could affect dependency option inference. The macros assume conventional singular/plural variable names and can fatal if a dependency exports unusual names. Version extraction only supports quoted string defines.

## Test Signals

Exercise with simple packages found by pkg-config, packages without pkg-config, dependency chains, missing headers, missing libraries, and version constraints. Run configure with `LIBFIND_DEBUG` to verify exported include/library lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/LibFindMacros.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/sanitize-helpers.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/sanitize-helpers.cmake

## Purpose

`sanitize-helpers.cmake` implements shared sanitizer support logic: mapping target sources to languages/compilers, probing sanitizer flags per compiler, and appending sanitizer flags to targets safely.

## Important APIs, Types, and Functions

Functions are `sanitizer_lang_of_source(FILE RETURN_VAR)`, `sanitizer_target_compilers(TARGET RETURN_VAR)`, `sanitizer_check_compiler_flag(FLAG LANG VARIABLE)`, `sanitizer_check_compiler_flags(FLAG_CANDIDATES NAME PREFIX)`, and `sanitizer_add_flags(TARGET NAME PREFIX)`.

## Control Flow

`sanitizer_lang_of_source` compares a file extension with enabled language extension lists. `sanitizer_target_compilers` walks a target's `SOURCES`, ignores object-library generator expressions, maps sources to compiler IDs, and returns unique compilers. `sanitizer_check_compiler_flags` iterates enabled languages and candidate flags, uses language-specific CMake flag checks, optionally prepends GNU static sanitizer runtime flags, and caches `<PREFIX>_<COMPILER>_FLAGS`. `sanitizer_add_flags` rejects targets compiled by multiple compilers or with no supported sanitizer flag, then appends sanitizer and blacklist flags to `COMPILE_FLAGS` and sanitizer flags to `LINK_FLAGS`.

## State and Persistence Behavior

The helpers write cache variables for detected compiler flags and mutate target properties. They do not persist files.

## Dependencies and Integration Points

They depend on CMake enabled language metadata, `CheckCCompilerFlag`, `CheckCXXCompilerFlag`, optional `CheckFortranCompilerFlag`, and variables set by component sanitizer modules. `FindSanitizers.cmake` and `Find*San.cmake` modules call into these helpers.

## Risks and Edge Cases

Target source lists containing generated files, generator expressions other than `TARGET_OBJECTS`, or language-less sources can lead to no compiler detection. Mixed compiler targets are rejected, which is safer but may skip valid builds. Appending to legacy `COMPILE_FLAGS`/`LINK_FLAGS` properties can interact poorly with modern target options and generator expressions.

## Test Signals

Create C-only, CXX-only, mixed C/CXX same-compiler, mixed compiler, and object-library targets with sanitizer options enabled. Inspect target properties and verify flag checks are cached per compiler.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/sanitize-helpers.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindBISON.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindBISON.cmake

## Purpose

This portability `FindBISON.cmake` provides Bison discovery and a `BISON_TARGET` macro compatible with older CMake 2.8-era environments. NFS-Ganesha uses it to generate the configuration parser from `conf_yacc.y`.

## Important APIs, Types, and Functions

It exports `BISON_EXECUTABLE`, `BISON_VERSION`, `BISON_FOUND`, and macro `BISON_TARGET(Name BisonInput BisonOutput [VERBOSE file] [COMPILE_FLAGS string])`. Internal helper macros are `BISON_TARGET_option_verbose` and `BISON_TARGET_option_extraopts`.

## Control Flow

The module finds `bison` or `win_bison`, runs `--version` with `LC_ALL=C`, parses version strings for GNU Bison and Bison++, and defines `BISON_TARGET` when an executable is available. `BISON_TARGET` validates argument count, handles optional verbose and compile flags, forces `-d`, derives the generated header name by replacing `c` with `h` in the output extension, and creates an `add_custom_command` that runs Bison in `GANESHA_TOP_CMAKE_DIR`.

## State and Persistence Behavior

It creates generated parser source/header outputs in the build tree through custom commands and exposes per-target variables such as `BISON_<Name>_OUTPUTS`, `BISON_<Name>_OUTPUT_HEADER`, and `BISON_<Name>_COMPILE_FLAGS`.

## Dependencies and Integration Points

It depends on Bison and local `FindPackageHandleStandardArgs.cmake`. `config_parsing/CMakeLists.txt` uses `BISON_TARGET(ConfigParser ... COMPILE_FLAGS "--defines -pganesha_yy")`.

## Risks and Edge Cases

Header-name derivation uses a broad `string(REPLACE "c" "h" ...)`, which can alter extensions unexpectedly. Verbose output handling assumes Bison writes `<output-name>.output`. Running in `GANESHA_TOP_CMAKE_DIR` may matter for relative grammar includes.

## Test Signals

Configure with Bison present and absent, generate `conf_yacc.c`/header, and build the config parser. Version parsing should be checked against GNU Bison version formats and Windows `win_bison`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindBISON.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindFLEX.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindFLEX.cmake

## Purpose

This portability `FindFLEX.cmake` discovers Flex and defines macros to generate scanner sources and wire scanner/parser dependencies on older CMake versions.

## Important APIs, Types, and Functions

It exports `FLEX_FOUND`, `FLEX_EXECUTABLE`, `FLEX_VERSION`, `FLEX_LIBRARIES`, `FLEX_INCLUDE_DIRS`, and macros `FLEX_TARGET(Name Input Output [COMPILE_FLAGS string])` and `ADD_FLEX_BISON_DEPENDENCY(FlexTarget BisonTarget)`.

## Control Flow

The module finds `flex` or `win_flex`, optional `fl` library, and `FlexLexer.h`. It runs `flex --version` and parses the version. `FLEX_TARGET` validates optional compile flags and creates an `add_custom_command` running Flex with `-o<Output>` from `CMAKE_CURRENT_SOURCE_DIR`. `ADD_FLEX_BISON_DEPENDENCY` sets `OBJECT_DEPENDS` on generated scanner outputs to the Bison-generated header.

## State and Persistence Behavior

Generated scanner source is created in the build tree by custom commands. Per-target variables such as `FLEX_<Name>_OUTPUTS`, `FLEX_<Name>_INPUT`, and `FLEX_<Name>_COMPILE_FLAGS` are set.

## Dependencies and Integration Points

It depends on Flex and local `FindPackageHandleStandardArgs.cmake`. `config_parsing/CMakeLists.txt` uses it to generate `conf_lex.c` with prefix `ganeshun_yy` and adds a dependency on the Bison parser header.

## Risks and Edge Cases

The documented usage string misses a closing parenthesis, but diagnostics still identify the macro. `FLEX_EXECUTABLE_opts` is not explicitly reset at macro start, so repeated invocations could inherit options in some CMake scopes. The optional `fl` library/header variables are not required by package handling.

## Test Signals

Configure with Flex present/missing, generate `conf_lex.c`, and ensure scanner compilation waits for `conf_yacc.h`. Version parsing should be checked with old and new Flex output formats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindFLEX.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/rpmtools_config.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/rpmtools_config.cmake

## Purpose

`rpmtools_config.cmake` defines RPM metadata for packaging NFS-Ganesha.

## Important APIs, Types, and Functions

It sets variables including `RPM_NAME`, `PACKAGE_VERSION`, `RPM_SUMMARY`, `RPM_RELEASE_BASE`, `RPM_RELEASE`, `RPM_PACKAGE_LICENSE`, `RPM_PACKAGE_GROUP`, `RPM_URL`, `RPM_CHANGELOG_FILE`, and `RPM_DESCRIPTION`.

## Control Flow

At configure time, it derives `PACKAGE_VERSION` from `${PROJECT_NAME}_MAJOR_VERSION`, `${PROJECT_NAME}_MINOR_VERSION`, and `${PROJECT_NAME}_PATCH_LEVEL`. It derives `RPM_RELEASE` from `RPM_RELEASE_BASE` and `_GIT_HEAD_COMMIT_ABBREV`, then sets static descriptive metadata.

## State and Persistence Behavior

State is CMake packaging variable state consumed by rpm tooling. It does not write files directly.

## Dependencies and Integration Points

It depends on project version variables and Git revision metadata. It integrates with RPM generation modules or scripts that read the `RPM_*` variables and `rpm_changelog`.

## Risks and Edge Cases

If `_GIT_HEAD_COMMIT_ABBREV` is unset, the release string can contain an empty or invalid git suffix. The license string is `LGPLv3`, while source headers often say LGPL-3.0-or-later; package policy may require exact SPDX-like wording.

## Test Signals

Generate RPM packaging metadata from a Git checkout and a source archive, then inspect the produced spec/release strings and package description. Package linting should validate license/group fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/rpmtools_config.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/CMakeLists.txt

## Purpose

This CMake file builds the NFS-Ganesha configuration parser subsystem. It generates Bison and Flex sources, compiles parser support into an object library, and optionally builds a dynamically loaded RADOS URL provider module.

## Important APIs, Types, and Functions

Key build APIs are `BISON_TARGET(ConfigParser ...)`, `FLEX_TARGET(ConfigScanner ...)`, `ADD_FLEX_BISON_DEPENDENCY`, object library `config_parsing`, module library `ganesha_rados_urls`, and `add_sanitizers(...)`.

## Control Flow

Configure finds Bison and Flex, adds `-D__USE_GNU`, generates `conf_yacc.c` and `conf_lex.c` with Ganesha-specific symbol prefixes, and includes source and binary directories so generated headers are visible. It builds `config_parsing` from `analyse.c`, `config_parsing.c`, `conf_url.c`, `analyse.h`, and generated scanner/parser outputs. If LTTng is enabled, it depends on trace header generation. If `RADOS_URLS` is enabled, it builds `ganesha_rados_urls` from `conf_url_rados.c`, links it against `ganesha_nfsd`, system libraries, RADOS libraries, and a no-undefined linker flag, then installs it.

## State and Persistence Behavior

Build state includes generated parser/scanner files in the binary directory, object-library outputs, optional module library, and installed module artifacts. Sanitizer flags and `-fPIC` are applied to targets.

## Dependencies and Integration Points

It depends on local Bison/Flex modules, sanitizer modules, generated LTTng properties when tracing is enabled, RADOS discovery for URL support, and the main `ganesha_nfsd` target for module linkage.

## Risks and Edge Cases

Generated scanner flags specify both `-Pganeshun_yy` and `-olex.yy.c` while CMake names the output `${CMAKE_CURRENT_BINARY_DIR}/conf_lex.c`; compatibility depends on Flex command-line semantics. Linking a module against `ganesha_nfsd` can be sensitive to executable symbol export and platform linker behavior. `config_parsing` is an object library with explicit `-fPIC`, which must remain true for shared/module consumers.

## Test Signals

Clean builds should regenerate scanner/parser sources and compile `config_parsing`. Builds with `RADOS_URLS=ON`, `USE_LTTNG=ON`, and sanitizers enabled validate optional branches. `verif_syntax` or parser unit tests validate generated parser integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.c -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.c

## Purpose

`analyse.c` owns token interning, parse-tree display, parse-tree cleanup, and low-level config error formatting for the generated lexer/parser subsystem.

## Important APIs, Types, and Functions

Important functions are `sanitize_token_str`, `save_token`, `config_term_name`, `config_term_desc`, `print_parse_tree`, `free_parse_tree`, and `config_error`. Internal helpers include AVL token comparison/lookup, recursive `print_node`, `print_token_tree`, `free_node`, and `free_token_tree`.

## Control Flow

Scanner tokens flow through `save_token`. Quoted tokens are optionally sanitized in place, hashed with `CityHash64`, looked up in a static AVL tree, and either deduplicated or allocated as a new `token_tab`. Parse-tree printing emits a summary, file list, token table, and recursive block/statement/term structure. Cleanup recursively unlinks/free nodes, frees file-list paths, frees the token AVL tree, and frees the root. Errors are formatted into a stream with a form-feed separator and optionally mirrored to full-debug logs.

## State and Persistence Behavior

The token table is a static AVL tree shared by the parser implementation and guarded only by the current parse-root initialization flag. Tokens are persisted for the lifetime of a `config_root`; parse nodes reference interned token strings instead of owning them. `config_root` owns the file list, config directory, generation value, and parse tree.

## Dependencies and Integration Points

It depends on `analyse.h`, `config_parsing.h`, `gsh_list`, `avltree`, `CityHash64`, Ganesha memory wrappers, and logging globals. The generated scanner calls `save_token`, the parser creates nodes that store token pointers, and `config_parsing.c` consumes the tree.

## Risks and Edge Cases

The static token tree can be problematic if multiple parse trees are live or parsed concurrently; cleanup frees the static tree without resetting the static root. `config_error` uses `vsprintf` into a fixed `LOG_BUFF_LEN` buffer, so very long diagnostics can overflow unless upstream formatting bounds them. `sanitize_token_str` mutates scanner text, which is expected but should not be reused afterward.

## Test Signals

Parser tests should include repeated tokens to verify interning, quoted strings with escapes, parse tree print/free under valgrind or sanitizers, and malformed input producing separated diagnostics. Concurrent reload tests would expose token-tree global-state hazards.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.h -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.h

## Purpose

`analyse.h` declares the private parse tree, token table, file-list, parse-root, and parser-state structures shared by the scanner, parser, analysis code, and semantic config loader.

## Important APIs, Types, and Functions

Key types are `enum node_type`, `struct config_node`, `struct file_list`, `struct token_tab`, `struct config_root`, and `struct parser_state`. Declared functions include `save_token`, `ganesha_yyparse`, `ganeshun_yy_init_parser`, `ganeshun_yy_cleanup_parser`, `token_compare_hash`, `config_error`, `print_parse_tree`, and `free_parse_tree`.

## Control Flow

The scanner stores recognized tokens in `config_node` terminals and uses `parser_state` to track current scanner, include buffer stack, current file, block depth, and error sink. The parser builds `TYPE_BLOCK`, `TYPE_STMT`, and `TYPE_TERM` nodes under a `TYPE_ROOT`. Later semantic loading walks those lists.

## State and Persistence Behavior

`config_root` owns parse-tree memory, the initial config directory, included file list, generation number, and token-tree initialization flag. `config_node` stores filename pointers into the file list and token pointers into the intern table, so cleanup order matters.

## Dependencies and Integration Points

It depends on `gsh_list.h`, `avltree.h`, `city.h`, and public config term types from `config_parsing.h`. It is included by generated grammar/lexer sources and by `config_parsing.c`.

## Risks and Edge Cases

Because the structures are private but shared among generated files, changes require regenerating and recompiling the parser. `filename` and token strings are non-owning references, so consumers must not outlive the parse tree. The global token-tree implementation behind these declarations limits concurrency unless externally serialized.

## Test Signals

Compile tests for generated parser/scanner and semantic loader catch type drift. Runtime parse/free tests with includes and URL-backed configs validate ownership expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/analyse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_lex.l -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_lex.l

## Purpose

`conf_lex.l` is the Flex scanner for Ganesha configuration files. It tokenizes the configuration language, handles `%include`, `%dir`, and `%url` directives, manages nested input buffers, and supplies typed tokens to the Bison grammar.

## Important APIs, Types, and Functions

Important scanner states are `YY_INIT`, `DEFINITION`, `TERM`, `INCLUDE`, `URL`, and `INCL_DIR`. Key helper functions are `ganeshun_yy_init_parser`, `ganeshun_yy_cleanup_parser`, `process_dir`, `new_file`, `fetch_url`, `pop_file`, and `ganeshun_yywrap`. `struct bufstack` tracks nested files/URLs.

## Control Flow

The scanner starts in `YY_INIT`, accepts top-level block identifiers, moves to `DEFINITION` for statements/blocks, and to `TERM` after `=` for typed values. `%include` pushes a single file, `%dir` opens matching regular files from a directory, and `%url` fetches a URL-backed stream through `config_url_fetch`. EOF pops the current buffer and resumes the previous file. Token rules classify quoted strings, booleans, arithmetic operators, numbers, FSIDs, IPv4/IPv6 addresses and CIDRs, netgroups, paths, plain tokens, and wildcard regex tokens.

## State and Persistence Behavior

The scanner maintains a buffer stack of open `FILE *` handles or URL memory streams, current filename, line number, config directory, file list, block depth, and parse generation. It records all parsed files in the config root and rejects repeated file paths to avoid include loops.

## Dependencies and Integration Points

It depends on Flex reentrant/bison-bridge APIs, `conf_yacc.h`, `analyse.h`, `conf_url.h`, Ganesha memory wrappers, logging, `dirent`, `fnmatch`, and `libgen`. The Bison parser consumes tokens through `ganesha_yylex`.

## Risks and Edge Cases

`process_dir` order follows directory iteration and is not sorted, so config load order can vary by filesystem. It only includes regular files based on `dirent.d_type`, which can be `DT_UNKNOWN` on some filesystems. Include-loop detection uses constructed path strings without canonicalization, so symlinks or path variants can bypass it. URL recursion can be compiled out only with `NO_URL_RECURSION`.

## Test Signals

Syntax tests should cover nested includes, duplicate includes, directory includes with glob patterns, URL includes, string escaping, IPv6/CIDR forms, FSIDs, wildcard clients, and scanner errors. Leak tests should cover parse failures while multiple buffers are stacked.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_lex.l -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url.c -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url.c

## Purpose

`conf_url.c` implements the generic URL-provider registry and dispatch layer for `%url` configuration includes. It currently recognizes `rados://` URLs and can dynamically load the RADOS URL provider module.

## Important APIs, Types, and Functions

Public functions are `register_url_provider`, `config_url_init`, `config_url_shutdown`, `gsh_rados_url_setup_watch`, `gsh_rados_url_shutdown_watch`, `config_url_fetch`, and `config_url_release`. Internal helpers include `init_url_regex`, optional `load_rados_config`, and `match_dup`.

## Control Flow

Initialization creates the provider list and lock, optionally loads `libganesha_rados_urls.so`, calls its package initializer, and compiles a URL regex. Providers register by name under a write lock and run their `url_init` callback. `config_url_fetch` matches the URL, extracts type and provider-specific path, finds a provider under a read lock, and calls its `url_fetch`. Shutdown removes providers, calls their shutdown callbacks, frees the regex, closes the dynamic module, and destroys the lock.

## State and Persistence Behavior

State is process-global: `url_rwlock`, `url_providers`, compiled `url_regex`, and optional dynamic-library handles/function pointers. Fetched URL content is returned as a `FILE *` plus backing buffer and must be released with `config_url_release`.

## Dependencies and Integration Points

It depends on POSIX regex, pthread rwlocks, `dlopen`/`dlsym`, Ganesha list/log/memory wrappers, and provider definitions from `conf_url.h`. The scanner's `%url` directive calls `config_url_fetch`, and daemon reload paths can call RADOS watch setup/shutdown wrappers.

## Risks and Edge Cases

`register_url_provider` calls `url_init` and adds the provider even after detecting a duplicate name, returning `EEXIST` but still mutating state. The URL regex only accepts `rados` and a narrow character set. Dynamic loading behavior differs under ASan/FreeBSD by avoiding `RTLD_DEEPBIND`. `config_url_release` uses `free` for `fbuf`, matching `open_memstream` but requiring providers to follow that convention.

## Test Signals

Initialize/shutdown with and without `RADOS_URLS`, fetch valid and invalid URLs, register duplicate providers, and run `%url` parser tests. Dynamic module loading should be tested in normal and ASan builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url_rados.c -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url_rados.c

## Purpose

`conf_url_rados.c` implements the dynamically loaded `rados://` configuration URL provider. It reads Ganesha config fragments from Ceph RADOS objects and can watch a configured object to trigger daemon reloads.

## Important APIs, Types, and Functions

Key public/module functions are `conf_url_rados_pkginit`, `register_service_to_ceph`, `rados_url_setup_watch`, and `rados_url_shutdown_watch`. Important internals are `rados_urls_set_param_from_conf`, `rados_url_client_setup`, `cu_rados_url_init`, `cu_rados_url_shutdown`, `rados_url_parse`, `cu_rados_url_fetch`, `rados_url_watchcb`, and the `rados_url_provider` instance. The config block is `RADOS_URLS` with `ceph_conf`, `userid`, and `watch_url`.

## Control Flow

Package initialization registers the provider. Early provider init compiles the RADOS URL regex. Full init loads the `RADOS_URLS` config block, creates a librados cluster, reads the Ceph config, connects, and marks the provider initialized. Fetch parses a URL into pool, optional namespace, and object, creates an ioctx, reads the object in 1024-byte chunks into an `open_memstream`, rewinds it, and returns the stream/buffer to the scanner. Watch setup parses `watch_url`, ensures a client connection, creates an ioctx, registers `rados_watch3`, and the callback acknowledges notifications then sends `SIGHUP` to the process.

## State and Persistence Behavior

State is module-global: compiled regex, `rados_t cluster`, `initialized`, watch ioctx/cookie/object, service-update thread, and parsed `rados_url_param`. The service registration path can start a heartbeat thread that periodically updates Ceph service status while initialized. Fetched config data persists in a memory stream until released by the generic URL layer.

## Dependencies and Integration Points

It depends on librados, pthreads, POSIX regex, signals, Ganesha config loading APIs, `RADOS_URLS` block descriptors, and the generic URL provider API. It integrates with Ceph FSAL/RADOS deployments where configs and recovery metadata live in Ceph.

## Risks and Edge Cases

`cu_rados_url_shutdown` joins the service update thread while `initialized` is still true, so the loop may not exit before join unless another path changes state. `rados_url_parse` allows object-only URLs even though the comment questions the lack of a default pool; passing a null pool to `rados_ioctx_create` is risky. The read loop's write accounting uses `MIN(nread, 1024)` rather than the actual `wrt`, which can mis-handle short writes. Error logging uses `strerror(ret)` even though librados returns negative errno values.

## Test Signals

Integration tests need a Ceph cluster or mocked librados: parse object-only, pool/object, and pool/namespace/object URLs; fetch multi-chunk objects; validate memory stream contents; test missing `RADOS_URLS`; test watch callback SIGHUP behavior; and exercise clean shutdown with the heartbeat thread enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url_rados.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_yacc.y -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_yacc.y

## Purpose

`conf_yacc.y` is the Bison grammar for Ganesha configuration files. It builds the parse tree consumed by semantic config loading.

## Important APIs, Types, and Functions

Generated/parser-facing functions and helpers include `ganesha_yyparse`, `ganesha_yylex`, `config_parse_error`, `ganesha_yyerror`, `config_block`, `config_stmt`, `config_term`, `link_sibling`, `link_node`, `dump_all_blocks`, and global `all_blocks`. Grammar values are token strings and `struct config_node *`.

## Control Flow

The grammar accepts a `deflist` of definitions. A definition is either `IDENTIFIER = statement` or `IDENTIFIER { block }`. Statements are semicolon-terminated comma-separated expression lists. Expressions map scanner tokens into typed term nodes, preserving arithmetic opcodes for signed/complement numeric forms. Blocks and statements allocate nodes, attach child lists, and update parent pointers. Syntax errors in statements or blocks are reported and recovered at `;` or `}`.

## State and Persistence Behavior

The parser mutates the `config_root` tree in `parser_state` and appends every block node to global `all_blocks` for later name lookup. Nodes store non-owning token and filename pointers managed by the parse root.

## Dependencies and Integration Points

It depends on Bison pure parser mode, location tracking, the Flex scanner, `analyse.h`, `config_parsing.h`, Ganesha list/memory/log APIs, and term type definitions. `config_parsing.c` later loads typed structures from the tree.

## Risks and Edge Cases

Empty configuration files are reported but can still produce a parse root. `all_blocks` is global, so concurrent parses or multiple live parse trees need external discipline. `parse_block` in `config_parsing.c` relies on node names and statement values built here. Error recovery drops malformed subtrees, which can lead to later missing/unknown parameter diagnostics.

## Test Signals

Grammar tests should cover empty files, top-level blocks, nested blocks, empty blocks/statements, multiple expression values, arithmetic numeric forms, syntax recovery, and parent linkage through `get_parse_root`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_yacc.y -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/config_parsing.c -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/config_parsing.c

## Purpose

`config_parsing.c` is the semantic loader for Ganesha configuration. It parses files into trees, reports diagnostics, converts parse nodes into typed C structures using `config_item` descriptors, loads nested blocks through callbacks, and provides query helpers for reload/update paths.

## Important APIs, Types, and Functions

Public APIs include `config_ParseFile`, `config_GetBlockNode`, `config_Print`, `config_Free`, `err_type_str`, `init_error_type`, `config_proc_error`, `report_config_errors`, `find_unused_blocks`, `get_parse_root`, `get_config_generation`, `get_parse_root_generation`, `find_config_nodes`, `load_config_from_node`, and `load_config_from_parse`. Important internals include `convert_bool`, `convert_number`, `convert_fsid`, `convert_list`, `convert_enum`, `convert_inet_addr`, `do_block_init`, `do_block_load`, `proc_block`, and expression parser/matcher helpers.

## Control Flow

`config_ParseFile` initializes parser state, calls the generated parser, records syntax/resource errors, cleans up scanner buffers, and returns the parse root. Semantic loading initializes defaults from a `config_item` table, searches matching statement/block nodes, checks mandatory and unique constraints, converts terminal values by type, processes lists/enums/bools/IPs/FSIDs, invokes custom processors, recursively loads child blocks, and calls optional check/commit/display callbacks. Top-level loading scans root blocks by name and handles default initialization when no block exists unless disabled.

## State and Persistence Behavior

The parse root owns tree memory and a generation counter incremented by the scanner. `config_error_type` owns an `open_memstream` diagnostics buffer until `report_config_errors` closes and frees it. Semantic loading mutates caller-provided or callback-allocated config structures, sets bit masks for `CONFIG_MARK_SET`, marks parse nodes as found for unknown detection, and may dispose of partially loaded blocks through init callbacks on error.

## Dependencies and Integration Points

It depends on the generated parser/scanner, `analyse.h`, public `config_parsing.h` descriptors, Ganesha logging/memory/list APIs, socket/address APIs, and FSAL ID conversion types. It is the common loader used by core NFS, FSAL, export, logging, RADOS URL, and reload configuration blocks.

## Risks and Edge Cases

The conversion path is broad and sensitive to descriptor metadata. Numeric conversion has separate signed/unsigned paths and supports `~` only for unsigned masks; diagnostics for invalid unsigned opcodes say "signed values". `find_unused_blocks` reports unknown blocks but does not increment `errors`. Expression parsing has a likely bug `if (!(isalpha(*sp) || *sp != '_'))`, which accepts many non-underscore non-alpha starts. IP defaults and conversion rely on `getaddrinfo` behavior and address-family fallback. Several paths use global parse block state and are not obviously concurrent-safe.

## Test Signals

Strong tests include descriptor-table unit tests for every `CONFIG_*` type, mandatory/unique/unknown handling, nested block init/check/commit rollback, default-only block loading, mark-set masks, deprecated parameter warnings, IP address parsing, FSID parsing, error aggregation, `find_config_nodes` expressions, and full sample config loads under sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/config_parsing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/test_parse.c -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/test_parse.c

## Purpose

`test_parse.c` is a small standalone parser smoke-test program that parses a supplied config file, frees it, then parses it again to exercise parser cleanup and reload behavior.

## Important APIs, Types, and Functions

The only function is `main`. It calls `config_ParseFile` and `config_Free` from the config parser API and exits with `EINVAL` on usage or parse failure.

## Control Flow

The program requires one file path argument, parses it, prints the returned pointer, fails if null, frees it, parses the same file again, prints the new pointer, fails if null, frees it, and exits success.

## State and Persistence Behavior

It allocates and frees two complete parse trees. It does not initialize `config_error_type` before passing it, which may reflect an older API or make diagnostics unsafe depending on the current function signature.

## Dependencies and Integration Points

It depends on `config_parsing.h` and the parser library. It is useful as a developer smoke test rather than a production binary.

## Risks and Edge Cases

The local `err_type` is uninitialized, so if `config_ParseFile` expects `err_type->fp` to be valid, this test can produce undefined behavior on errors. Output lacks newlines, and usage errors call `exit(EINVAL)` after printing to stdout.

## Test Signals

Build and run against valid, invalid, include-heavy, and URL-free configs. Memory checking across the parse/free/parse/free cycle is the main value of this test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/test_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/verif_syntax.c -->
# sources/user-network-fs/nfs-ganesha/src/config_parsing/verif_syntax.c

## Purpose

`verif_syntax.c` is a command-line syntax checker for Ganesha configuration files.

## Important APIs, Types, and Functions

The only function is `main`. It uses `SetDefaultLogging`, `SetNamePgm`, `LogTest`, `config_ParseFile`, and `config_Free`.

## Control Flow

The program initializes test logging, requires one config file argument, calls `config_ParseFile`, logs an error and exits `EINVAL` if parsing fails, otherwise logs success and exits 0.

## State and Persistence Behavior

It creates a parse tree but exits immediately after logging success, making the subsequent `config_Free(config)` unreachable. It has no persistent state.

## Dependencies and Integration Points

It depends on the parser API and Ganesha logging. It is intended for build/test or operator syntax validation.

## Risks and Edge Cases

The call `config_ParseFile(fichier)` does not match the two-argument signature visible in `config_parsing.c`, suggesting API drift, macro overloading, or stale test code. The success path leaks the parse tree because it exits before freeing. The declared `errtxt` is unused.

## Test Signals

Build success is itself an API compatibility signal. Runtime tests should check valid/invalid configs and ensure the program returns shell-friendly status codes; leak checks would catch the unreachable free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_parsing/verif_syntax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/ceph.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/ceph.conf

## Purpose

`ceph.conf` is a sample NFS-Ganesha configuration for exporting CephFS through FSAL_CEPH, with optional RADOS-backed recovery and RADOS-backed configuration includes.

## Important APIs, Types, and Functions

The sample exercises config blocks `NFS_CORE_PARAM`, `NFSv4`, `MDCACHE`, `EXPORT`, nested `FSAL`, `CEPH`, `RADOS_KV`, and `RADOS_URLS`. It documents `%url rados://pool/namespace/object` usage.

## Control Flow

The config disables NLM and rquotad, restricts protocols to NFSv4, prefers NFSv4.1/4.2, minimizes MDCACHE directory chunking, defines a CephFS export at `/` with pseudo path `/cephfs_a/`, and selects FSAL `CEPH`. Later blocks provide optional Ceph cluster, recovery, and config-URL parameters.

## State and Persistence Behavior

At runtime this configuration can use Ceph for exported filesystem state, recovery records, and even configuration storage. Defaults leave many Ceph authentication and recovery parameters commented, so actual persistence depends on administrator-provided values.

## Dependencies and Integration Points

It integrates with FSAL_CEPH, libcephfs, RADOS recovery backends, `RADOS_URLS`, NFSv4 recovery, MDCACHE, and export handling. It is also a parser regression sample covering nested blocks, strings, booleans, integers, and comments.

## Risks and Edge Cases

The sample exports `/` because FSAL_CEPH lacks subtree checking, which is correct for safety but broad. It warns delegations are not recommended in clustered configurations. RADOS URL/recovery comments imply separate Ceph clients and keyring requirements that operators must satisfy.

## Test Signals

`verif_syntax` should accept the sample. Integration tests require a Ceph cluster and should validate NFSv4 mount, recovery backend selection, FSAL_CEPH auth, and optional `RADOS_URLS` fetch/watch behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/ceph.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/ds.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/ds.conf

## Purpose

`ds.conf` is a minimal Data Server configuration sample for pNFS/DS-style setups.

## Important APIs, Types, and Functions

It defines a `DS` block with optional `Number` and nested `FSAL` block setting `Name = GPFS`.

## Control Flow

The parser reads one top-level `DS` block. Semantic loading should assign DS number 0 and associate the DS with the GPFS FSAL.

## State and Persistence Behavior

The file itself persists no runtime state; it configures a server role and FSAL binding. DS identity uniqueness matters when multiple DS instances are deployed.

## Dependencies and Integration Points

It integrates with GPFS FSAL and any Ganesha pNFS data-server configuration loader.

## Risks and Edge Cases

It is intentionally minimal and omits access/export details, so it is not a full operational config. Duplicate DS numbers in a larger deployment would be a semantic risk.

## Test Signals

Parser syntax validation and DS block loader tests should accept this sample and apply the default number. GPFS-enabled builds are needed for runtime validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/ds.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gluster.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/gluster.conf

## Purpose

`gluster.conf` is a minimal export sample for serving a Gluster volume through NFS-Ganesha.

## Important APIs, Types, and Functions

It exercises an `EXPORT` block with `Export_Id`, `Path`, `Pseudo`, `Access_Type`, `Squash`, `SecType`, and nested `FSAL` fields `Name`, `Hostname`, `Volume`, `enable_upcall`, and `Transport`.

## Control Flow

The sample defines one export of `/testvol` at pseudo path `/testvol`, grants read/write access, disables root squashing, selects sys security, and binds the export to FSAL `GLUSTER` on localhost volume `testvol` over TCP.

## State and Persistence Behavior

Runtime state is in the Gluster volume and Ganesha export table. The config enables upcalls, so cache coherency depends on Gluster notification support.

## Dependencies and Integration Points

It depends on FSAL_GLUSTER, Gluster client libraries, export handling, MDCACHE/upcall integration, and NFS security flavor parsing.

## Risks and Edge Cases

`No_Root_Squash` is permissive and should be reviewed before production use. The sample uses localhost and a fixed volume name, so operators must adjust deployment-specific values. RDMA transport is mentioned but not selected.

## Test Signals

Syntax validation should pass. Runtime validation requires a Gluster volume named `testvol`, FSAL_GLUSTER built, NFS mount of `/testvol`, and upcall behavior tests when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gluster.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.conf

## Purpose

`gpfs.conf` is a basic GPFS export sample showing GPFS-specific defaults, clustered NFS core settings, NFSv4 lease configuration, and one export.

## Important APIs, Types, and Functions

It uses `EXPORT_DEFAULTS`, `NFS_Core_Param`, `NFSv4`, `GPFS`, and `EXPORT` with nested `FSAL { Name = GPFS; }`.

## Control Flow

The sample sets a long attribute expiration default appropriate for GPFS invalidate upcalls, enables clustered mode, sets NFSv4 lease lifetime to 90, enables read delegations in the `GPFS` block, and exports `/ibm/gpfs0` at matching pseudo path with read/write access.

## State and Persistence Behavior

Runtime persistence lives in GPFS and Ganesha's export/config state. Longer attribute caching relies on GPFS invalidation upcalls for correctness.

## Dependencies and Integration Points

It depends on FSAL_GPFS, NFSv4 configuration, export defaults, and clustered core behavior.

## Risks and Edge Cases

Delegations and long cache lifetimes must match GPFS callback behavior and cluster topology. Export ID 77 and path `/ibm/gpfs0` are placeholders and can conflict or fail if reused unchanged.

## Test Signals

Syntax validation plus GPFS-enabled runtime tests should verify export load, NFSv4 mount, delegation behavior, and cache invalidation under file changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.exports.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.exports.conf

## Purpose

`gpfs.ganesha.exports.conf` is an empty placeholder include file for GPFS export definitions in the split GPFS sample configuration set.

## Important APIs, Types, and Functions

The file contains no statements or blocks. Its role is structural: `gpfs.ganesha.nfsd.conf` includes it after main and log fragments.

## Control Flow

When included, the scanner reaches EOF without emitting config definitions. Depending on parser behavior for empty files, this may be harmless in an include context or may generate an empty-configuration diagnostic if parsed directly.

## State and Persistence Behavior

It persists no runtime configuration state. Operators are expected to populate it with `EXPORT` blocks.

## Dependencies and Integration Points

It integrates with the `%include` directive and the GPFS split-config sample layout.

## Risks and Edge Cases

Parsing this file directly may be treated as an empty configuration. Deployments using the top-level include file without adding exports may start without exported filesystems.

## Test Signals

Syntax tests should include the top-level `gpfs.ganesha.nfsd.conf` to confirm an empty included fragment is acceptable. Operational tests should add at least one GPFS export before expecting client mounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.exports.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.log.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.log.conf

## Purpose

`gpfs.ganesha.log.conf` is the logging fragment for the split GPFS sample configuration.

## Important APIs, Types, and Functions

It defines a `LOG` block with `Default_log_level`, nested `Facility`, `Format`, and `Components` subblocks. Facility fields include `name`, `destination`, `max_level`, `headers`, and `enable`.

## Control Flow

The sample configures default log level `EVENT`, a file facility at `/var/log/ganesha/nfs-ganesha.log` with full-debug maximum, detailed ISO-8601 formatting fields, and component level `ALL = EVENT`.

## State and Persistence Behavior

At runtime it writes logs to the configured destination and controls log verbosity/format. It does not affect parser state beyond normal block loading.

## Dependencies and Integration Points

It integrates with Ganesha's logging configuration loader, file facility backend, and component-level filtering.

## Risks and Edge Cases

The destination directory must exist and be writable by the daemon. `max_level = FULL_DEBUG` can permit high-volume logging if enabled, though component default remains `EVENT`.

## Test Signals

Syntax validation should pass, and runtime tests should confirm log file creation, selected headers/format fields, and component level behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.log.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.main.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.main.conf

## Purpose

`gpfs.ganesha.main.conf` is the main GPFS split-config fragment. It sets GPFS behavior, core NFS parameters, NFSv4 behavior, directory services, MDCACHE sizing, and export defaults.

## Important APIs, Types, and Functions

It defines `GPFS`, `NFS_Core_Param`, `NFSv4`, `DIRECTORY_SERVICES`, `MDCACHE`, and `Export_Defaults` blocks with many scalar, boolean, list, and enum parameters.

## Control Flow

The fragment enables GPFS trace, disables GPFS grace, enables clustered core mode, allows NFSv3/v4, sets ports and RPC connection/thread limits, configures NFSv4 lease/grace/minor versions, enables idmapping for a domain, sizes MDCACHE, and establishes conservative export defaults such as no access, TCP transports, sys security, root squash, and disabled commit.

## State and Persistence Behavior

Runtime state includes global daemon protocol/transport settings, idmapping behavior, cache sizing thresholds, and defaults inherited by later `EXPORT` blocks. It is intended to be included before export fragments.

## Dependencies and Integration Points

It integrates with GPFS FSAL, NFS core, NFSv4, directory services/idmapping, MDCACHE, and export loaders.

## Risks and Edge Cases

High cache and RPC limits may be inappropriate for small systems. `Access_Type = none` in defaults requires exports to override access. `NFS_Commit = FALSE` changes write durability semantics and must match deployment expectations. Domain name is sample-specific.

## Test Signals

Syntax validation should pass. Runtime tests should inspect effective core settings, idmapping domain, cache thresholds, and export defaults inherited by a sample export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.main.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.nfsd.conf -->
# sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.nfsd.conf

## Purpose

`gpfs.ganesha.nfsd.conf` is the top-level split GPFS sample config. It composes main, logging, and export fragments using `%include`.

## Important APIs, Types, and Functions

It uses three scanner directives: `%include /etc/ganesha/gpfs.ganesha.main.conf`, `%include /etc/ganesha/gpfs.ganesha.log.conf`, and `%include /etc/ganesha/gpfs.ganesha.exports.conf`.

## Control Flow

The scanner processes includes in listed order, pushing each file onto the input stack. Main/global settings are loaded first, logging second, and export definitions last.

## State and Persistence Behavior

This file stores composition state only; the included fragments define runtime behavior. Include paths are absolute and assume files are installed under `/etc/ganesha`.

## Dependencies and Integration Points

It depends on the parser `%include` implementation and the split GPFS sample files being installed at the referenced paths.

## Risks and Edge Cases

Absolute include paths will fail in source-tree syntax tests unless files are staged into `/etc/ganesha` or paths are adjusted. If the exports fragment remains empty, the composed config may define no exports.

## Test Signals

Install-layout tests should validate all three includes resolve. Parser tests can use a temporary `/etc/ganesha`-like directory or rewrite paths to test include stack behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/gpfs.ganesha.nfsd.conf -->
