# subset-b-009686 research

Grouped research report for mergerfs vendored headers and NFS-Ganesha build/pNFS Ceph files. Each section title preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/rapidhash/rapidhash.h -->
# sources/user-network-fs/mergerfs/vendored/rapidhash/rapidhash.h

Purpose: Header-only vendored rapidhash V3 implementation, derived from wyhash, providing fast deterministic 64-bit non-cryptographic hashes for mergerfs. The header exposes full, Micro, and Nano variants so callers can trade larger-input throughput against instruction footprint.

Important APIs, types, and functions: Public entry points are `rapidhash`, `rapidhash_withSeed`, `rapidhashMicro`, `rapidhashMicro_withSeed`, `rapidhashNano`, and `rapidhashNano_withSeed`. Internal helpers include `rapid_mum` for 64x64-to-128 multiplication, `rapid_mix` for xor-folded multiplication mixing, `rapid_read64` and `rapid_read32` for endian-normalized unaligned reads, and the `rapid_secret[8]` default secret table. Compile-time knobs include `RAPIDHASH_COMPACT` versus `RAPIDHASH_UNROLLED`, `RAPIDHASH_FAST` versus `RAPIDHASH_PROTECTED`, endianness macros, and inlining/noexcept/constexpr compatibility macros.

Control flow: Each hash seeds itself by mixing the caller seed with two secrets, then chooses a length path. Inputs up to 16 bytes are folded from the first/last 4 or 8 bytes, or selected single bytes for 1-3 byte inputs. Longer inputs process repeated 112-byte, 80-byte, or 48-byte stripes for the full, Micro, and Nano variants respectively, mix remaining 16-byte chunks, fold the final 16 bytes with the length, and finish with one multiply plus a final `rapid_mix`. The full implementation can optionally unroll 224-byte loops when `RAPIDHASH_UNROLLED` is defined.

State and persistence behavior: There is no mutable global state and no persistence. Hash output is determined only by input bytes, input length, seed, compile-time mode, platform integer behavior, and the secret table. `rapid_secret` is defined in the header as a constant object, so every translation unit can inline and optimize around it.

Dependencies and integration points: Depends only on `<stdint.h>`, `<string.h>`, compiler 128-bit multiply support or MSVC intrinsics when available, and portable fallback multiplication otherwise. In mergerfs it is used by inode hashing in `src/fs_inode.cpp`, compact hash storage in `src/hashset.hpp`, and pseudo-random generation in `src/rnd.cpp`. `tests/tests.cpp` includes a regression that checks seeded wrappers preserve canonical internal output for many offsets, lengths, and seeds, and verifies Micro/Nano match the full variant within their intended small-size ranges.

Risks: This is not a cryptographic hash; it should not be used for adversarial authentication or collision-resistant security decisions. Public functions do not validate `key`, so a null pointer is only safe for zero-length input. The internal `secret` pointer must address at least eight 64-bit words even though some comments still describe a smaller secret set. Build output can vary if incompatible macro combinations or endianness detection are wrong. HashSet callers that store only hashes accept the residual collision risk.

Test signals: Run mergerfs tests that include `test_rapidhash_withSeed_preserves_default_output`. Additional useful signals are deterministic vectors for empty, 1-3 byte, 4-7 byte, 8-16 byte, and large buffers under both compact and unrolled modes, plus cross-endian vector checks if big-endian support matters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/rapidhash/rapidhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/scope_guard/scope_guard.hpp -->
# sources/user-network-fs/mergerfs/vendored/scope_guard/scope_guard.hpp

Purpose: Header-only vendored `scope_guard` 0.9.1 implementation that provides RAII cleanup actions for scope exit, exception failure, exception success, and `DEFER`-style cleanup macros. mergerfs uses it to keep cleanup paths local in filesystem and vendored libfuse code.

Important APIs, types, and functions: Main types are `scope_guard::detail::scope_guard<F, P>`, `on_exit_policy`, `on_fail_policy`, and `on_success_policy`, with aliases `scope_exit`, `scope_fail`, and `scope_success`. Factory functions are `make_scope_exit`, `make_scope_fail`, and `make_scope_success`. Public macros include `SCOPE_EXIT`, `SCOPE_FAIL`, `SCOPE_SUCCESS`, `DEFER`, named `MAKE_*` forms, and `WITH_*` loop helpers. Configuration macros control throwable behavior: `SCOPE_GUARD_MAY_THROW_ACTION`, `SCOPE_GUARD_NO_THROW_ACTION`, `SCOPE_GUARD_SUPPRESS_THROW_ACTION`, `SCOPE_GUARD_NO_THROW_CONSTRUCTIBLE`, and `SCOPE_GUARD_CATCH_HANDLER`.

Control flow: A guard captures an rvalue no-argument void action and a policy initialized as active. On move, the new object takes the action and policy while dismissing the source. On destruction, `policy_.should_execute()` decides whether to run the action: always for exit, only when the uncaught exception count increased for fail, and only when it did not increase for success. `dismiss()` disables execution. The macro interface creates uniquely named const guards through `__COUNTER__` or `__LINE__`.

State and persistence behavior: State is strictly automatic object lifetime: each guard owns one decayed action and one policy flag or exception-count snapshot. There is no heap allocation by `scope_guard` itself, and class-specific `operator new` is deleted to prevent direct dynamic allocation. No state persists beyond the lexical scope.

Dependencies and integration points: Depends on `<type_traits>` and, on modern C++ modes, `<exception>` for `std::uncaught_exceptions()`. Older GCC/Clang paths read ABI exception globals directly; old MSVC has a `_getptd()` offset fallback. mergerfs includes this header in many cleanup-heavy paths such as readdir implementations, copy/clone helpers, procfs handling, API code, and vendored libfuse mutex/loop code.

Risks: In default `SCOPE_GUARD_MAY_THROW_ACTION` mode, a throwing cleanup action can propagate from a destructor and can terminate the process during stack unwinding. The suppressed mode swallows exceptions unless a custom catch handler is provided. The old compiler uncaught-exception fallbacks are ABI-sensitive. Actions must be no-argument `void` callables and are accepted only as rvalues by the core constructor, so storing references requires capture discipline. The macro helpers capture by reference, which is convenient but unsafe if used beyond normal lexical lifetime.

Test signals: Compile coverage is the main signal: files using `SCOPE_EXIT`/`DEFER` must compile under the repository's C++ standard and warning profile. Runtime tests should cover normal exit, dismissed guard, move construction, exception path for `SCOPE_FAIL`, non-exception path for `SCOPE_SUCCESS`, and destructor behavior under the selected throwable policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/scope_guard/scope_guard.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/subprocess/subprocess.hpp -->
# sources/user-network-fs/mergerfs/vendored/subprocess/subprocess.hpp

Purpose: Header-only C++ subprocess library vendored by mergerfs. It provides a Python-like `Popen` API plus `call`, `check_output`, and `pipeline` helpers for launching child processes, wiring standard streams, setting environment/cwd, and collecting output.

Important APIs, types, and functions: Public exceptions are `subprocess::OSError` and `subprocess::CalledProcessError`. Public option types include `bufsize`, `defer_spawn`, `close_fds`, `session_leader`, `shell`, `executable`, `cwd`, `environment`, `input`, `output`, `error`, and `preexec_func`. `Popen` exposes constructors for string, initializer-list, and vector commands plus `start_process`, `wait`, `poll`, `kill`, `send`, `communicate`, stream accessors, close helpers, and output buffer sizing. `OutBuffer` and `ErrBuffer` wrap resizable `std::vector<char>` storage and a populated length. Utility code handles split/join, pipe creation, close-on-exec flags, robust reads, and Windows command-line/environment conversion.

Control flow: Constructors collect command arguments, apply variadic options through `detail::ArgumentDeducer`, set up stream channels, and spawn immediately unless `defer_spawn{true}` is set. On POSIX, `execute_process` creates a close-on-exec error pipe, optionally rewrites the command through `/bin/sh -c`, prepends an explicit executable, forks, and has the child dup requested descriptors onto stdin/stdout/stderr before optional `chdir`, `preexec_func`, `setsid`, environment updates, and `execvp`. Child setup failures are written back through the error pipe so the parent can throw `CalledProcessError` and reap the child. On Windows, it builds a quoted UTF-16 command line, creates inheritable pipes, calls `CreateProcessW`, and starts an async cleanup task for child pipe handles. `communicate` uses a single-stream shortcut when possible and otherwise async reader tasks for stdout/stderr while writing stdin.

State and persistence behavior: `Popen` owns descriptor numbers, `FILE*` wrappers in shared pointers with `fclose` deleters, child pid or Windows process handle, return code, command vectors, cwd/env options, and flags. It does not persist state beyond the process and OS handles it creates. Output persistence only happens when callers choose filename-based `output` or `error`, which opens files append/create/read-write with mode `0640`.

Dependencies and integration points: Uses C and C++ standard headers, POSIX `fork`, `execvp`, `pipe`, `fcntl`, `dup2`, `waitpid`, `kill`, `setsid`, and `setenv`, or a manually declared subset of Windows API calls. In mergerfs, direct usage is narrow: `src/fs_mount.cpp` calls `subprocess::call({"mount", tgt})`, and `src/mergerfs_collect_info.cpp` runs diagnostic commands with `subprocess::output{file}`.

Risks: The string constructor uses a simple whitespace split and does not implement shell-like quoting; callers needing exact arguments should use initializer-list or vector forms. The destructor is disabled, so callers must call `wait`, `poll`, or `communicate` to avoid lingering children or unreaped POSIX processes. `communicate` can still block if a child keeps pipes open or if single-stream shortcut assumptions are wrong. `error{STDOUT}` checks `write_to_parent_` as a truthy integer, so the default `-1` can bypass the intended "output must be set first" error. Environment support only overlays variables and does not remove inherited variables. `close_fds` loops to `_SC_OPEN_MAX`, which can be expensive. `preexec_func` runs after fork and before exec, so only async-signal-safe behavior is ideal in multithreaded programs.

Test signals: Useful tests include successful `call`, non-zero `check_output` raising `CalledProcessError`, stdout/stderr pipe capture, stdin write and close behavior, cwd/env propagation, file output append, `defer_spawn` pipelines, `shell` on POSIX, and child exec failure propagation through the error pipe. mergerfs integration can be smoke-tested through `fs::mount` command construction and collect-info output files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/subprocess/subprocess.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/CMakeLists.txt

Purpose: Top-level CMake build and configuration script for NFS-Ganesha. It defines project versioning, platform and distro detection, feature options, dependency discovery, generated configuration/package files, subdirectory inclusion, executable targets, and documentation generation.

Important APIs, types, and functions: Uses CMake modules `CheckIncludeFiles`, `CheckLibraryExists`, `CheckCSourceCompiles`, `TestBigEndian`, `FindPkgConfig`, project-local `goption.cmake`, `maintainer_mode.cmake`, and sanitizer/toolchain modules. Major options include FSAL toggles (`USE_FSAL_CEPH`, `USE_FSAL_VFS`, `USE_FSAL_GLUSTER`, etc.), protocol toggles (`USE_NFS3`, `USE_NLM`, `USE_9P`, RDMA options), service integrations (`USE_DBUS`, `USE_NFSIDMAP`, `USE_GSS`, `USE_LTTNG`, RADOS options), allocator selection, test framework options, and packaging options. Generated outputs include `include/config.h`, `nfs-ganesha.spec`, systemd service files, Docker files when possible, and a configured `Doxyfile`.

Control flow: The script sets project metadata and install directories, detects Linux/FreeBSD/Darwin/Windows characteristics, computes linker undefined-symbol policy, captures git revision data, defines build options, optionally loads a shortcut build configuration, and mutates compiler flags for platform, debug, coverage, glibc, relative file paths, and VSOCK. It then validates dependencies for RDMA, GSS/Kerberos, Python tools, Sphinx man pages, ACLs, every enabled FSAL, allocator libraries, DBus, idmap, LTTng, RADOS, caps, blkid/uuid, unwind, and nTIRPC. After rolling dependencies into `SYSTEM_LIBRARIES`, it installs the sample config, adds all major source subdirectories, prints the resolved configuration, forces selected values into the cache, configures headers/spec/service files, and defines executables plus auxiliary targets.

State and persistence behavior: Persistent build state is in the CMake cache and generated files under the build or source tree. Notably, `nfs-ganesha.spec` and `scripts/systemd/nfs-ganesha-config.service` are configured into the source tree, while `config.h`, Docker files, and `Doxyfile` are generated under the build tree. The script also installs `ganesha.conf` only through a custom non-clobbering install helper.

Dependencies and integration points: This file is the root integration point for every subdirectory: `log`, `config_parsing`, `test`, `avl`, `hashtable`, `SAL`, `RPCAL`, `Protocols`, `support`, `os`, optional `monitoring`, `FSAL`, `idmapper`, `MainNFSD`, `tools`, optional `gtest`, optional `dbus`, optional `tracing`, `scripts`, and `doc`. It drives Ceph discovery through `find_package(CEPHFS)` and controls whether `FSAL/FSAL_CEPH` is added indirectly by `FSAL/CMakeLists.txt`.

Risks: The file has a large mutable option surface where one disabled dependency can silently turn off a feature unless the corresponding `*_REQUIRED` flag is set. Some generated outputs target the source tree, which can dirty working copies during configure. Distro detection parses `/etc/os-release` with simple string matching and can misclassify newer distributions. Several checks use global flags and directories, so option interactions can leak across targets. The Ceph pNFS code is controlled by compile definitions from detected Ceph capabilities and `config.h`; missing or stale detection can compile out whole pNFS paths.

Test signals: A successful configure is the primary signal, followed by verifying printed option summaries match intended features. Build targets to exercise include `ganesha.nfsd`, `verif_syntax`, `test_parsing`, optional `ganesha-rados-grace`, optional FSAL modules, and optional `doc`. Dependency matrix tests should cover minimal builds, Ceph-enabled builds, system versus bundled nTIRPC, DBus/LTTng/RADOS toggles, and packaging targets such as `dist`, `rpm`, or `srpm`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Doxyfile.in -->
# sources/user-network-fs/nfs-ganesha/src/Doxyfile.in

Purpose: Doxygen configuration template used by the top-level CMake `doc` target to generate NFS-Ganesha API/source documentation. CMake substitutes source and build paths before invoking Doxygen.

Important APIs, types, and functions: Key project settings are `PROJECT_NAME = "NFS-Ganesha"`, `PROJECT_BRIEF = "An NFS server in userspace"`, `OUTPUT_DIRECTORY = doc/doxygen`, `OPTIMIZE_OUTPUT_FOR_C = YES`, `TYPEDEF_HIDES_STRUCT = YES`, and `EXTENSION_MAPPING = h=C`. Input is `@CMAKE_CURRENT_SOURCE_DIR@`, recursion is enabled, and excludes remove tools, tests, scripts, packaging, samples, `FSAL_GPFS`, `FSAL_GLUSTER`, and `libntirpc`. Output settings enable HTML and LaTeX, disable man/XML/RTF, and leave source browser off. Warning settings enable documentation warnings but do not warn for undocumented members.

Control flow: During configure, `CMakeLists.txt` runs `configure_file(... @ONLY)` to create a concrete `Doxyfile` in the build directory. The `doc` custom target then runs `${DOXYGEN_EXECUTABLE}` against that file from the build directory. Doxygen recursively scans the configured source tree, applies excludes and preprocessing rules, emits HTML under `doc/doxygen/html`, and emits LaTeX under `doc/doxygen/latex`.

State and persistence behavior: The template itself is static. Generated documentation persists in the build tree under `doc/doxygen`. `HTML_TIMESTAMP = YES` means outputs include generation times and are not stable for byte-for-byte reproducibility unless changed. `WARN_LOGFILE` is empty, so warnings go to stderr rather than a persisted log.

Dependencies and integration points: Depends on Doxygen, optionally LaTeX tools for full LaTeX/PDF output, and optionally Graphviz if `HAVE_DOT` is changed from the current `NO`. It is only used if `find_package(Doxygen)` succeeds in the root build. The include/exclude choices shape which FSALs and subsystems appear in developer docs; Ceph FSAL is included, while GPFS and Gluster are explicitly excluded.

Risks: `PROJECT_NUMBER = pre-2.0` appears stale relative to the top-level Ganesha version and can mislabel generated docs. `EXTRACT_ALL = NO`, `EXTRACT_STATIC = NO`, no macro expansion, and source browser disabled mean much internal code and static functions may be absent even when relevant. The exclusion list may hide useful tests or FSAL implementations from API documentation. Enabling LaTeX by default can make the doc target heavier or fail later on hosts without a full TeX stack.

Test signals: Configure with Doxygen installed and run the `doc` target. Healthy output should include generated HTML for documented C APIs, warnings limited to expected doc issues, no path substitution literals left as `@CMAKE_CURRENT_SOURCE_DIR@`, and no accidental inclusion of excluded subtrees.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Doxyfile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/CMakeLists.txt

Purpose: FSAL dispatcher CMake file. It adds the common stackable and pseudo FSAL directories unconditionally and gates backend FSAL subdirectories according to top-level feature options.

Important APIs, types, and functions: Uses `add_subdirectory` only. Unconditional directories are `Stackable_FSALs` and `FSAL_PSEUDO`. Conditional directories include `FSAL_VFS` for any of `USE_FSAL_VFS`, `USE_FSAL_LUSTRE`, or `USE_FSAL_XFS`, plus `FSAL_PROXY_V4`, `FSAL_PROXY_V3`, `FSAL_CEPH`, `FSAL_RGW`, `FSAL_SAUNAFS`, `FSAL_GPFS`, `FSAL_GLUSTER`, `FSAL_LIZARDFS`, `FSAL_KVSFS`, and `FSAL_MEM`.

Control flow: CMake enters this file after the root script has already validated dependencies and normalized feature flags. Each `if(USE_FSAL_*)` block adds the matching backend directory. The VFS directory is shared by VFS, Lustre, and XFS support, so any of those options pulls in that subtree.

State and persistence behavior: This file creates no generated files or cache state. Its effect is build graph composition: which FSAL module targets and sources become visible to the build.

Dependencies and integration points: Depends entirely on options defined in the top-level `CMakeLists.txt`. It is the bridge from global dependency detection to backend-specific CMake files such as `FSAL/FSAL_CEPH/CMakeLists.txt`. Runtime FSAL availability follows from whether these module targets were built and installed.

Risks: Mis-set top-level options can omit an FSAL silently at this layer. The shared VFS/Lustre/XFS condition means maintainers must understand that disabling `USE_FSAL_VFS` alone does not necessarily exclude `FSAL_VFS` if Lustre or XFS remains enabled. There is no local validation here, so backend prerequisites must stay correct in the root script.

Test signals: Configure with selected FSAL toggles and inspect generated targets or the configure summary. A Ceph-enabled configure should enter `FSAL_CEPH`; a Ceph-disabled configure should not create the `fsalceph` module target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/CMakeLists.txt

Purpose: Backend-specific CMake file for the CephFS FSAL module. It defines the `fsalceph` shared module, its source list, include paths, libraries, sanitizer integration, version metadata, and install location.

Important APIs, types, and functions: Sets `_FILE_OFFSET_BITS=64`, builds `fsalceph_LIB_SRCS` from `main.c`, `export.c`, `handle.c`, `mds.c`, `ds.c`, `internal.c`, `internal.h`, and `statx_compat.h`, conditionally adds `statx_compat.c` when `CEPH_FS_CEPH_STATX` is false, includes `${CEPHFS_INCLUDE_DIR}`, creates `add_library(fsalceph MODULE ...)`, applies `add_sanitizers(fsalceph)`, links `ganesha_nfsd`, `${CEPHFS_LIBRARIES}`, `${SYSTEM_LIBRARIES}`, `${LTTNG_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`, sets version `4.2.0` and soversion `4`, and installs into `${FSAL_DESTINATION}`.

Control flow: This file is reached only when `USE_FSAL_CEPH` remains enabled in the parent build. It always includes `ds.c` in the source list, but that file's pNFS implementation is itself wrapped in `#ifdef CEPH_PNFS`. The statx compatibility source is added only when the detected CephFS headers/libraries do not provide the required statx interface.

State and persistence behavior: No runtime state is created by CMake. Build outputs are the `fsalceph` module artifact and install metadata. The compile definitions and configured `config.h` determine which Ceph feature paths are present in the final module.

Dependencies and integration points: Requires CephFS headers and libraries found by the root `find_package(CEPHFS)`. Links against the core `ganesha_nfsd` library and global system/LTTng dependencies. The module registers operations from `main.c`, including pNFS DS operations from `ds.c` when `CEPH_PNFS` is available.

Risks: `include_directories` is directory-scoped rather than target-scoped, which can leak includes to later targets in the same directory scope. `ds.c` can be present in the build but compile to an empty translation unit when `CEPH_PNFS` is not defined, so target presence alone does not prove pNFS support. Feature detection naming must remain aligned with Ceph API versions, especially for statx compatibility and pNFS-related symbols.

Test signals: A Ceph-enabled configure should print `CEPHFS_INCLUDE_DIR`, build `fsalceph`, and link without undefined symbols. Test both `CEPH_FS_CEPH_STATX` true and false environments if supported. Runtime smoke signals include module load/registration and Ceph export creation; pNFS-specific validation requires a build where `CEPH_PNFS` compiles in `pnfs_ds_ops_init`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/ds.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/ds.c

Purpose: CephFS pNFS data-server operation implementation for NFS-Ganesha. When `CEPH_PNFS` is defined, it provides DS handle creation, read, write, commit, and release operations for Ceph data-server filehandles.

Important APIs, types, and functions: Main functions are `pnfs_ds_ops_init`, `make_ds_handle`, `ds_handle_release`, `ds_read`, `ds_write`, `ds_commit`, and helper `local_invalidate`. Important data types are `struct fsal_pnfs_ds_ops`, `struct fsal_ds_handle`, Ceph-private `struct ds` and `struct ds_wire` from `internal.h`, NFSv4 types such as `stateid4`, `offset4`, `count4`, `stable_how4`, and `verifier4`, and Ganesha context `op_ctx`. Ceph calls include `ceph_get_local_osd`, `ceph_ll_get_stripe_osd`, `ceph_ll_read_block`, `ceph_ll_write_block`, `ceph_ll_connectable_m`, `fsal_ceph_ll_open`, `ceph_ll_write`, `ceph_ll_fsync`, and `ceph_ll_close`.

Control flow: `pnfs_ds_ops_init` starts from `def_pnfs_ds_ops` and overrides handle creation, handle release, read, write, and commit. `make_ds_handle` validates that the client-supplied buffer is exactly a `struct ds_wire` and that `fl_stripe_unit` is nonzero, allocates `struct ds`, stores the wire data, and marks it lazily disconnected. `ds_read` computes the target stripe and intra-stripe offset, verifies that the local OSD owns that stripe, reads at most the remaining bytes in the stripe with `ceph_ll_read_block`, returns the length read, and always sets EOF false. `ds_write` follows the same stripe ownership calculation, clamps writes to one stripe, and either routes `FILE_SYNC4` writes through a connected/opened MDS filehandle plus fsync and local invalidation, or uses `ceph_ll_write_block` directly for unstable/data-sync DS writes. `ds_commit` currently zeroes the write verifier, logs that commits should go to the MDS, and returns success; an optional `COMMIT_FIX` block can call `ceph_ll_commit_blocks`.

State and persistence behavior: Each DS handle stores copied wire layout/vino/snap data and a `connected` flag. The flag persists only for the handle lifetime and avoids repeated `ceph_ll_connectable_m` calls once a `FILE_SYNC4` write requires MDS connection. Reads do not mutate state. Writes persist data through Ceph OSD block writes or MDS writes depending on stability. Commit persistence is effectively delegated away in the default build.

Dependencies and integration points: Compiled only under `CEPH_PNFS`, declared in `internal.h`, and installed into the Ceph module operation table from `main.c`. Integrates with Ganesha pNFS core through `struct fsal_pnfs_ds_ops`, default DS methods in `FSAL/default_methods.c`, `pnfs_utils.h`, FSAL allocation helpers, `op_ctx`, and async cache invalidation through `up_async_invalidate`. It depends on Ceph low-level layout APIs and the Ceph export's `cmount`.

Risks: `ds_write` calls `ceph_get_local_osd` but does not explicitly handle a negative return before comparing against the stripe OSD, unlike `ds_read`; this can collapse a local OSD lookup failure into `NFS4ERR_PNFS_IO_HOLE` instead of a precise POSIX-derived error. Both read and write are intentionally limited to one stripe and rely on upper layers to split larger I/O correctly. EOF is always false on reads, which may be acceptable for pNFS block reads but is a behavioral assumption. `ds_commit` returns success while logging that commits should go to the MDS, so callers must not depend on it for DS durability unless `COMMIT_FIX` is enabled and correct. `make_ds_handle` validates size and stripe unit but not the authenticity of the wire content beyond that.

Test signals: Build with `CEPH_PNFS` enabled and verify `pnfs_ds_ops_init` is registered by the Ceph FSAL module. Functional tests should cover valid and invalid wire handles, zero stripe unit rejection, reads/writes for local and nonlocal stripes, write clamping at stripe boundaries, `FILE_SYNC4` connection/open/write/fsync/close behavior, cache invalidation after sync writes, negative Ceph error mapping, and commit semantics expected by the pNFS stack.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/ds.c -->
