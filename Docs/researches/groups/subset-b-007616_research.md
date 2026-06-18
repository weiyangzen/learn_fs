# subset-b-007616 Research Group

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs.go -->
# sources/distributed-fs/juicefs/pkg/vfs/vfs.go

## Purpose
This file is the central JuiceFS VFS operation layer. It maps FUSE-style filesystem operations onto the metadata client, chunk reader/writer, internal pseudo-files, access logging, Prometheus metrics, ACL encoding, xattr handling, and directory-handle invalidation. It also defines the exported configuration structures used by mount setup: `FuseOptions`, `SecurityConfig`, `Config`, `AnonymousAccount`, and the `VFS` object itself.

## Important APIs, Types, and Functions
`FuseOptions.StripOptions` canonicalizes mount options for comparisons by dropping kernel-only or non-user options, removing `nonempty`, and sorting options. `Lookup`, `GetAttr`, `Mknod`, `Mkdir`, `Unlink`, `Rmdir`, `Symlink`, `Readlink`, `Rename`, and `Link` perform namespace operations with name-length checks and special internal-node protection. `Create`, `Open`, `Read`, `Write`, `Truncate`, `Fallocate`, `CopyFileRange`, `Flush`, `Fsync`, and `Release` drive file I/O through `DataReader` and `DataWriter`. `SetXattr`, `GetXattr`, `ListXattr`, and `RemoveXattr` handle normal xattrs plus POSIX ACL xattr translation through `encodeACL` and `decodeACL`. `NewVFS`, `FlushAll`, `InitMetrics`, and `InitMemoryBufferMetrics` initialize runtime state and metrics.

## Control Flow and State
Most methods validate special-node rules, bounds, and handle state, call `v.Meta`, then update read/write caches or directory handles. File creation and open allocate file handles with reader/writer subobjects. Writes lock the handle, write into the async data writer, invalidate reader ranges, and mark attributes modified. Reads flush pending writer data for read-after-write consistency, then read through the reader. `Truncate`, `Fallocate`, and `CopyFileRange` flush pending data before metadata mutations and update writer/reader length or invalidation state. Directory reads maintain a per-handle `dirHandler` and `readAt` timestamp; offset updates tell the handler how far the kernel consumed.

Persistent state lives mainly outside this file in metadata and object storage. This file keeps volatile mount state: open handles, handle-to-inode maps, recently modified inode timestamps, internal file buffers, metrics registry, and cache filler. `NewVFS` can load prior open-handle state from `_FUSE_STATE_PATH` or `/tmp/state<ppid>.json`, renames that file to `.bak`, starts modified-state cleanup, and trims internal nodes for subdir mounts.

## Dependencies and Integration Points
The file depends heavily on `pkg/meta` for inode state, permissions, directory listings, xattrs, locks, and copy/truncate/fallocate operations; `pkg/chunk` for data storage; `pkg/acl` for ACL rule representation; `pkg/utils` for buffers, logging, and helpers; and Prometheus for metrics. Internal nodes such as `.control`, `.stats`, `.config`, and `.accesslog` integrate with control-message handlers, metrics collection, config JSON serialization with secrets removed, and access-log streams. Platform differences are delegated to `vfs_unix.go` and `vfs_windows.go`.

## Risks and Edge Cases
Correctness depends on flushing before reads and metadata-changing operations; missing a flush would expose stale data or commit metadata before data. Handle locking is central: cancellation paths can return `EINTR`, and release waits for active readers/writers before flushing and unlocking server-side locks. Special internal nodes bypass normal metadata and must remain protected from destructive operations. Size bounds use `maxFileSize`; off-by-one behavior rejects offsets or ranges where `off+size >= maxFileSize`. ACL decode rejects malformed or incomplete mask-bearing ACLs. `O_TMPFILE` support creates a temporary named file and unlinks it, with a warning that `O_EXCL` is unsupported.

## Test Signals
`vfs_test.go` exercises basic namespace operations, long-name failures, I/O, truncate, fallocate, copy-file-range errors, xattrs, internal files, control messages, hide-internal behavior, and directory cache behavior across metadata engines. Separate tests for access and locks cover helper behavior in platform files. Metrics registration is indirectly covered by `.stats` internal file reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs_test.go -->
# sources/distributed-fs/juicefs/pkg/vfs/vfs_test.go

## Purpose
This test file validates the JuiceFS VFS operation surface against an in-memory object store and multiple metadata engines. It is not a mock-only unit suite; it builds a real `VFS` using `meta.NewClient`, `chunk.NewCachedStore`, a memory object backend, and a wrapped Prometheus registry, then exercises namespace, I/O, xattr, lock, internal-file, and readdir paths.

## Important APIs, Types, and Functions
`createTestVFS` is the shared fixture builder. It creates a metadata format, initializes the metadata client, constructs `Config`, creates a memory object store, wraps metrics labels, builds a cached chunk store, and returns `NewVFS`. Tests include `TestVFSBasic`, `TestVFSIO`, `TestVFSXattrs`, `TestAccessMode`, `TestSetattrStr`, `TestVFSLocks`, `TestInternalFile`, `TestHideInternal`, `TestReaddirCache`, `TestVFSReadDirSort`, `TestReadDirBatch`, and `TestReaddir`. Helper functions include `assertEqual`, `testReaddirCache`, `testVFSReadDirSort`, `testReaddirBatch`, and `testReaddir`.

## Control Flow and State
Each test creates files and directories through VFS calls and then observes metadata effects through lookups, attributes, reads, and errors. I/O tests write sparse and large ranges, force `Fsync` and `Flush`, read through holes and copied ranges, and manipulate handles to validate `EBADF` paths. The internal-file test reads generated `.config`, `.stats`, and `.accesslog` data, then writes structured control messages with binary command and size headers, polling for progress and response frames.

The readdir tests intentionally mutate directories between batched reads and offset updates to validate cache invalidation and deterministic pagination. Several tests run against `memkv://`, `sqlite3://:memory:`, and Redis URIs, so the suite is designed to reveal backend-specific directory iteration differences when those backends are available.

## Dependencies and Integration Points
The suite depends on `pkg/meta`, `pkg/chunk`, `pkg/object`, `pkg/utils`, Prometheus, `golang.org/x/sys/unix`, and `stretchr/testify/require`. It exercises integration between metadata, chunk storage, VFS handle management, xattr/ACL filtering, lock operations, internal control handlers, and metrics generation.

## Risks and Edge Cases
Some tests assume local services or optional drivers: Redis-backed cases can fail if Redis is unavailable, and SQLite behavior depends on build tags or driver availability elsewhere in the project. Timing-sensitive checks include background flush waits and lock wait timeouts. The tests directly mutate handle internals to force invalid states, which is useful for coverage but couples the suite to private implementation details.

## Test Signals
This file is itself the primary test signal for `vfs.go`, `vfs_unix.go`, and `writer.go`. It confirms expected errnos for long names, invalid fds, too-large offsets, read-only/write-only handles, internal nodes, malformed xattrs, unsupported ACL xattrs, lock conflicts, and malformed control messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs_unix.go -->
# sources/distributed-fs/juicefs/pkg/vfs/vfs_unix.go

## Purpose
This non-Windows file supplies Unix-specific VFS operations and constants: `O_ACCMODE`, `F_UNLCK`, statfs reporting, permission testing, setattr handling, advisory lock APIs, flock APIs, and Linux-style ioctl flag support.

## Important APIs, Types, and Functions
`Statfs` is a compact filesystem-capacity response type. `StatFS` maps `Meta.StatFS` values to `Total`, `Avail`, `Files`, and `Favail`. `accessTest` implements owner/group/other permission checks for internal nodes and root bypass. `Access` converts Unix `R_OK`, `W_OK`, and `X_OK` to JuiceFS mode masks and delegates to metadata for ordinary inodes. `setattrStr` formats trace output. `SetAttr` handles size changes through `Truncate`, permission checks for mtime changes, writer mtime updates, and metadata setattr. `Getlk`, `Setlk`, and `Flock` wrap metadata lock APIs while recording per-handle lock ownership. `Ioctl` supports flag get/set operations for immutable, append-only, and skip-trash mappings.

## Control Flow and State
`SetAttr` treats internal nodes as immutable metadata-backed pseudo-files and returns their internal attributes. For real files, it truncates first when size is set, then populates a partial attr object for mode, uid, gid, atime, and mtime. Mtime changes may update pending writer slice timestamps before `Meta.SetAttr` persists attributes. Lock operations validate type, reject special nodes, require a valid file handle, call metadata, then update handle-local lock bitfields and owners so `Flush`/`Release` can unlock later.

`Ioctl` distinguishes set from get by command direction bits. Set operations decode 4- or 8-byte input, enforce root-only control over protected flags when permission checks are active, translate supported filesystem flags into `meta.Attr.Flags`, and reject unknown bits. Get operations translate metadata flags back into ext-style flag buffers or `FS_IOC_FSGETXATTR` output.

## Dependencies and Integration Points
The file integrates with `golang.org/x/sys/unix` constants, Go `syscall`, JuiceFS `meta` attribute and lock APIs, and `utils.NativeEndian` for ioctl buffer encoding. `vfs.go` calls these methods through platform build selection.

## Risks and Edge Cases
The simple `accessTest` only checks a single gid, so supplemental group handling is delegated to metadata access for normal inodes. `SetAttr` has special logic around pure size changes; ordering is important to avoid losing length updates. Lock owner handling mixes owner and file handle for flock, and release/flush depends on these fields. `Ioctl` is strict about buffer sizes and unknown flag bits, which may differ from kernel callers' expectations.

## Test Signals
`TestAccessMode`, `TestSetattrStr`, `TestVFSBasic`, and `TestVFSLocks` cover access checks, formatting, setattr effects, flock/POSIX lock behavior, invalid lock types, invalid handles, and special-node rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs_windows.go -->
# sources/distributed-fs/juicefs/pkg/vfs/vfs_windows.go

## Purpose
This Windows-specific file supplies the minimal platform replacements needed by the shared VFS code: Windows-compatible `O_ACCMODE` and `F_UNLCK` constants plus `ChFlags` for setting inode flags through metadata.

## Important APIs, Types, and Functions
`O_ACCMODE` is derived from WinFsp cgofuse's `fuse.O_ACCMODE`. `F_UNLCK` is set to `0x01`. `ChFlags` rejects internal special nodes, checks setattr permission when required, and calls `Meta.SetAttr` with `meta.SetAttrFlag`.

## Control Flow and State
`ChFlags` constructs an attr with only `Flags` populated. If the context enforces permission checks, it first asks metadata to validate the flag change. It then persists the new flag value with `SetAttr`. No local VFS state is updated here; state persistence is entirely in the metadata layer.

## Dependencies and Integration Points
The file depends on `github.com/winfsp/cgofuse/fuse` for Windows open-flag semantics and on JuiceFS `meta` for flag mutation. It is selected only for Windows builds and complements the Unix-only `SetAttr`, lock, statfs, access, and ioctl implementation.

## Risks and Edge Cases
The implementation only handles flag changes and leaves other platform-specific operations to other files. Internal nodes are protected with `EPERM`. The hard-coded unlock constant must stay compatible with WinFsp/cgofuse lock semantics used elsewhere.

## Test Signals
No Windows-specific test appears in this target set. Shared VFS tests cover cross-platform code paths, but `ChFlags` needs Windows or build-tag-specific coverage to validate permission behavior and WinFsp constant compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/vfs_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/writer.go -->
# sources/distributed-fs/juicefs/pkg/vfs/writer.go

## Purpose
This file implements JuiceFS buffered asynchronous writes. It exposes `FileWriter` and `DataWriter` interfaces and implements them with `dataWriter`, `fileWriter`, `chunkWriter`, and `sliceWriter`. The writer accepts byte ranges from VFS handles, groups them into chunk slices, uploads slice data to the chunk store, commits slice metadata in order, invalidates read cache ranges, and flushes pending writes on demand or in the background.

## Important APIs, Types, and Functions
`FileWriter` defines `Write`, `Flush`, `Close`, `GetLength`, and `Truncate`. `DataWriter` defines inode-scoped `Open`, `Flush`, `GetLength`, `Truncate`, `UpdateMtime`, and `FlushAll`. `sliceWriter.prepareID`, `write`, `flushData`, and `markDone` manage slice object IDs and upload completion. `chunkWriter.findWritableSlice` and `commitThread` choose writable slices and commit finished slices to metadata. `fileWriter.Write`, `writeChunk`, `flush`, `Flush`, `Close`, `Truncate`, and `updateMtime` manage file-level buffering. `dataWriter.flushAll`, `Open`, `free`, and `FlushAll` manage global writer lifetime and background flushing.

## Control Flow and State
A write enters `fileWriter.Write`, throttles when too many slices or too much buffer memory exists, waits for active flushes, splits data across metadata chunks, and calls `writeChunk`. A chunk either reuses a non-frozen slice or creates a new `sliceWriter` backed by `ChunkStore.NewWriter`. New slice IDs are allocated asynchronously with `Meta.NewSlice`; full or aged slices freeze and upload via `flushData`. Each `chunkWriter` has a `commitThread` that waits for slices to finish, waits for dependency slices when growing file length across chunks, writes slice metadata with `Meta.Write`, invalidates reader cache, records errors, and frees chunks.

Volatile state includes per-file length, error state, pending chunk/slice maps, wait counters, reference counts, and conditions. Persistent state is the uploaded chunk object plus the metadata slice committed by `Meta.Write`. `Flush` freezes all pending slices and waits until chunks drain, honoring cancellation after put-timeout windows and enforcing a computed deadline. `FlushAll` walks all open writers and returns the first nonzero errno as an error.

## Dependencies and Integration Points
The writer depends on `meta.Meta` for slice IDs and metadata commits, `chunk.ChunkStore` for object writers and memory accounting, `DataReader` for invalidation, and `utils.Cond` for wait/notify. `vfs.go` calls it from open/create/write/read/truncate/fallocate/copy/release/fsync/flush paths.

## Risks and Edge Cases
Ordering is subtle: growing slices can depend on prior chunk slices so metadata length does not advance out of order. Overlapping writes that cannot fit the latest writable slice create new slices or may return nil from `findWritableSlice`, relying on metadata overlay semantics. `Truncate` only adjusts buffered length and has a TODO to truncate buffered data when shrinking. Background goroutines and reference counting must stay balanced to avoid leaked file writers. Flush timeouts dump goroutine stacks and return `EIO`; long object-store stalls can surface as write failures. Memory throttling uses process allocation minus store memory, which may be noisy.

## Test Signals
`TestVFSIO` stresses this writer through sparse writes, fallocate, fsync, copy-file-range, sequential 128 KiB writes, many small overlapping writes, background flush waiting, read-after-write, and invalid fd paths. The writer itself has no direct tests in this target set, so most coverage is integration-level through VFS I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/vfs/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/CMakeLists.txt

## Purpose
This is the top-level LizardFS CMake build definition. It establishes build policy, install paths, feature toggles, package versioning, compiler flags, platform definitions, dependency/environment checks, generated config header output, and the project subdirectory graph.

## Important APIs, Types, and Functions
The file defines many CMake options, including tests, docs, client library, NFS-Ganesha, crc, tracing, allocators, polonaise, ccache, official build suffixes, and warning behavior. It sets install subdirectories via `GNUInstallDirs`, default runtime values such as user/group/master host, package version variables, C/C++ flags, and preprocessor definitions. It includes `EnvTests`, `Libraries`, `CollectSources`, and `CreateUnitTest`, then calls `configure_file(config.h.in config.h)`.

## Control Flow and State
Configuration starts by rejecting in-source builds. It optionally enables ccache, sets install path aliases, logs option values, and derives `PACKAGE_VERSION_SUFFIX` from Git SHA, official build state, or RC number. Enabling tests forces `THROW_INSTEAD_OF_ABORT`, `ENABLE_CLIENT_LIB`, `BUILD_TESTS`, `BUILD_UTILS`, and debug logging. `ENABLE_CLIENT_LIB` enables PIC targets. Build type defaults to Debug. After environment and library detection, it adds subsystem directories conditionally: common mount components always, non-MinGW daemons/tools/docs/FUSE mount conditionally, tests when enabled, and uraft when enabled.

## Dependencies and Integration Points
The file integrates with local CMake modules in `cmake/`, generated `config.h`, external bundled libraries, source subtrees under `src/`, docs, tests, utilities, and platform-specific flags for SunOS and MinGW. It relies on `git rev-parse HEAD` when available for development version suffixes.

## Risks and Edge Cases
Although `ENABLE_WERROR` defaults off, the file unconditionally adds `-Werror`, so warning sensitivity may be higher than the option name implies. Dependency discovery must run before checking `Boost_INCLUDE_DIRS`; missing Boost headers are fatal. Tests silently force other options, which can surprise package builds. In-source build protection is strong but requires cleanup after failed attempts. CMake minimum version is old (`2.8`), constraining available constructs.

## Test Signals
Configuration-time signals include fatal errors for in-source builds, missing Boost, missing FUSE on non-MinGW, incompatible allocator options, and missing request-log dependencies. Build/test signal comes from enabling `BUILD_TESTS` and adding `src/unittests` and `tests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckCXXExpression.cmake -->
# sources/distributed-fs/lizardfs/cmake/CheckCXXExpression.cmake

## Purpose
This helper defines `check_cxx_expression`, a CMake function for compile-time validation of a C++ boolean expression after including one or more headers.

## Important APIs, Types, and Functions
`check_cxx_expression(_EXPR _HEADER _RESULT)` builds source text containing `#include` lines for each header, a template that only defines `value_type` for `true`, and a `main` that instantiates the expression as a boolean. It calls `CHECK_CXX_SOURCE_COMPILES` with the generated source and stores the result in `_RESULT`.

## Control Flow and State
The function accumulates include directives, creates a single source string, and lets CMake's compiler-check machinery cache the result. There is no persistent runtime state; outputs are CMake cache/config variables consumed by `EnvTests.cmake` and ultimately `config.h.in`.

## Dependencies and Integration Points
It includes `CheckCXXSourceRuns`, though the implementation uses `CHECK_CXX_SOURCE_COMPILES`. It is used by `EnvTests.cmake` to check standard-library expressions such as steady-clock and allocator-traits support.

## Risks and Edge Cases
Header names are interpolated directly into angle-bracket includes. The check verifies compilation, not runtime behavior. The included module name is broader than necessary but harmless if CMake provides the compile macro elsewhere.

## Test Signals
Failures appear as false CMake variables such as `LIZARDFS_HAVE_STD_CHRONO_STEADY_CLOCK` or `LIZARDFS_HAVE_STD_ALLOCATOR_TRAITS`, influencing generated feature macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckCXXExpression.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckFunctions.cmake -->
# sources/distributed-fs/lizardfs/cmake/CheckFunctions.cmake

## Purpose
This module centralizes function-existence probes for C and C++ build configuration.

## Important APIs, Types, and Functions
`check_functions(FUNCTIONS REQUIRED)` loops over function names, creates uppercase `LIZARDFS_HAVE_<FUNC>` variables, calls `CHECK_FUNCTION_EXISTS`, and emits `SEND_ERROR` when required functions are missing. `check_template_function_exists(HEADER CALL OUTPUT_VARIABLE)` compiles a small C++ program including `HEADER` and executing `CALL`.

## Control Flow and State
The functions set CMake cache/config variables consumed later by `config.h.in`. Required failures do not immediately call `FATAL_ERROR`, but `SEND_ERROR` makes configuration fail at generation.

## Dependencies and Integration Points
`EnvTests.cmake` invokes these helpers for POSIX functions, optional functions, and standard-library template functions. The caller is responsible for including CMake's `CheckFunctionExists` and `CheckCXXSourceCompiles` modules.

## Risks and Edge Cases
The required check tests for empty string or non-`1` values and may be sensitive to CMake truthiness. The template helper only checks if the output variable is undefined, so stale cache values can mask compiler changes.

## Test Signals
Configuration output and generated `LIZARDFS_HAVE_*` macros are the main signals. Missing required functions produce CMake errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckFunctions.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckIncludes.cmake -->
# sources/distributed-fs/lizardfs/cmake/CheckIncludes.cmake

## Purpose
This module probes for header availability and creates normalized `LIZARDFS_HAVE_*` variables for found includes.

## Important APIs, Types, and Functions
`check_includes(INCLUDES)` loops over include file names, converts each to a valid CMake identifier for `check_include_files`, stores `<include>_FOUND`, and when present defines an uppercase macro-style variable with slashes, dots, and dashes converted to underscores.

## Control Flow and State
Missing headers are accumulated and reported with a message after the loop. Found headers are exposed in the parent scope so `config.h.in` can produce `#define` lines. The function does not fail configuration on missing headers.

## Dependencies and Integration Points
It includes CMake's `CheckIncludeFiles` and is used by `EnvTests.cmake` for platform and optional headers such as socket, systemd, zlib, and ISA-L related files.

## Risks and Edge Cases
The function creates variables like `arpa/inet.h_FOUND`, which are not ideal CMake identifiers, alongside sanitized internal names. Missing required headers must be enforced elsewhere. Reporting is informational only.

## Test Signals
Signals are configuration messages for missing includes and generated macros such as `LIZARDFS_HAVE_SYS_SOCKET_H`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckIncludes.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckMembers.cmake -->
# sources/distributed-fs/lizardfs/cmake/CheckMembers.cmake

## Purpose
This helper probes whether a C/C++ struct has particular members and records feature macros.

## Important APIs, Types, and Functions
`check_members(STRUCT MEMBERS HEADER)` builds variable names such as `LIZARDFS_HAVE_STRUCT_STAT_ST_BLOCKS`, calls `CHECK_STRUCT_HAS_MEMBER`, and warns plus sets the variable to `0` when absent.

## Control Flow and State
Each member probe feeds CMake configuration variables that become optional macros in `config.h`. Missing members are non-fatal and are expected on some platforms.

## Dependencies and Integration Points
`EnvTests.cmake` uses this for `struct stat`, `struct tm`, and `struct rusage`. The caller includes `CheckStructHasMember`.

## Risks and Edge Cases
The helper assumes CMake result variables compare numerically to `1`; unusual CMake false values could be awkward. It only supports one header argument string, so multi-header checks need caller-side setup.

## Test Signals
Warnings during configure indicate portability differences. Generated macros guide conditional compilation in the C++ source tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CheckMembers.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CollectSources.cmake -->
# sources/distributed-fs/lizardfs/cmake/CollectSources.cmake

## Purpose
This macro provides a conventional way for subdirectories to collect local sources, tests, and main files.

## Important APIs, Types, and Functions
`collect_sources(VAR_PREFIX)` populates `${VAR_PREFIX}_TESTS` with `*_unittest.cc`, `${VAR_PREFIX}_SOURCES` with local `.cc`, `.c`, and `.h`, and `${VAR_PREFIX}_MAIN` with `main.cc` or `main.c`. If main or test files exist, it removes them from the generic source list.

## Control Flow and State
The macro uses CMake `file(GLOB ...)` at configure time. It mutates variables named by prefix in the caller's scope.

## Dependencies and Integration Points
Included by top-level `CMakeLists.txt`, it is intended for source subdirectories that build libraries, binaries, and unit-test libraries from consistent naming conventions.

## Risks and Edge Cases
Globbing is configure-time only, so adding source files may require rerunning CMake. The `if(${VAR_PREFIX}_MAIN OR ${VAR_PREFIX}_TESTS)` expression can be brittle when variables expand to lists with special content. Only one directory level is scanned.

## Test Signals
Build target source lists are the practical signal. Missing files in targets after adding new sources suggests CMake was not rerun or naming conventions were not followed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CollectSources.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CreateUnitTest.cmake -->
# sources/distributed-fs/lizardfs/cmake/CreateUnitTest.cmake

## Purpose
This module defines helper functions for registering unit-test libraries and their link dependencies when tests are enabled.

## Important APIs, Types, and Functions
`create_unittest(TEST_NAME ...)` returns unless `BUILD_TESTS` is true and sources were provided. It removes the test name from `ARGV`, creates a library named `${TEST_NAME}_unittest`, includes GTest headers, and appends the test name to cached `UNITTEST_TEST_NAMES`. `link_unittest(TEST_NAME ...)` stores link libraries in cached `${TEST_NAME}_UNITTEST_LINKLIST`.

## Control Flow and State
Both helpers use CMake internal cache variables as a cross-directory registry. They avoid doing any work when tests are disabled.

## Dependencies and Integration Points
They rely on `GTEST_INCLUDE_DIRS` from dependency discovery and on later unit-test aggregation logic in the source tree that consumes `UNITTEST_TEST_NAMES` and per-test link lists.

## Risks and Edge Cases
Because state is cached with `FORCE`, stale test registration can persist across configure changes unless cache is cleared carefully. The functions silently return with too few args, which can hide misconfigured tests.

## Test Signals
When `ENABLE_TESTS` is on, generated unit-test libraries and cache variables should appear. Link failures or absent tests indicate missing `create_unittest` or `link_unittest` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/CreateUnitTest.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/DownloadExternal.cmake -->
# sources/distributed-fs/lizardfs/cmake/DownloadExternal.cmake

## Purpose
This helper downloads, verifies, extracts, and optionally patches bundled external dependencies when they are not already present under `external/`.

## Important APIs, Types, and Functions
`download_external(PCKG_NAME PCKG_DIR_NAME PCKG_URL [md5] [patch_name])` caches the package directory name, downloads a zip to the binary directory with optional expected MD5, unzips it into the source `external` directory, verifies the expected directory exists, and optionally applies a patch from `external/<patch_name>.patch`.

## Control Flow and State
The function is a configure-time side-effect tool. If the target source directory exists, it just reports the package as found. Otherwise it performs network download, unzip, and patch commands, failing configuration with `FATAL_ERROR` on any problem.

## Dependencies and Integration Points
`Libraries.cmake` uses it for NFS-Ganesha and ntirpc when `ENABLE_NFS_GANESHA` is enabled. It depends on CMake `file(DOWNLOAD)`, an `unzip` executable, and a `patch` executable when patching.

## Risks and Edge Cases
The function writes into the source tree during configure, which can dirty checkouts and break read-only source builds. It has network and tool availability risks. The unzip error message references `${ARCHIVE_NAME}`, which is not defined. Patch paths are hard-coded relative to `external`.

## Test Signals
Configure output reports download, unpack, patch, or found status. Fatal configure errors are the main failure signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/DownloadExternal.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/EnvTests.cmake -->
# sources/distributed-fs/lizardfs/cmake/EnvTests.cmake

## Purpose
This module runs the build's portability and environment probes, replacing older autotools checks and generating variables used by `config.h.in`.

## Important APIs, Types, and Functions
It includes CMake check modules plus local helpers, defines the header list, handles FreeBSD include paths, calls `check_includes`, detects endianness, checks integer and system type sizes, probes struct members, required functions, optional functions, `clock_gettime`, mmap-related functions, C++ standard-library features, compiler flags, CPU dispatch support, Apple poll/select conversion, fallocate punch-hole constants, and `std::future`.

## Control Flow and State
The module runs during CMake configure before `config.h` generation. Required functions include POSIX and C library calls; non-MinGW builds add `getpass`, `poll`, and `realpath`. It temporarily changes `CMAKE_REQUIRED_INCLUDES` and `CMAKE_REQUIRED_FLAGS` for scoped probes, then unsets them.

## Dependencies and Integration Points
It depends on helper modules `CheckCXXExpression`, `CheckFunctions`, `CheckIncludes`, `CheckMembers`, and `SharedLibraries`. Its output variables map directly to `#cmakedefine` entries in `config.h.in`, influencing conditional compilation across LizardFS.

## Risks and Edge Cases
Probe order matters: some checks depend on include paths or compiler flags. The Judy bug/runtime check can be expensive when Judy is found. `sys/rusage.h` may not exist on all platforms but is included in the header list. Required function policy may need adjustment for newer or less POSIX-like platforms.

## Test Signals
Configure messages and generated macros are the signal. Required function misses produce errors; optional misses produce disabled feature macros. Build success across Linux, FreeBSD, macOS, SunOS, and MinGW validates this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/EnvTests.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindDB.cmake -->
# sources/distributed-fs/lizardfs/cmake/FindDB.cmake

## Purpose
This find module locates Berkeley DB headers and library and extracts a version string from `db.h`.

## Important APIs, Types, and Functions
It sets `DB_LIBRARY`, `DB_INCLUDE_DIR`, `DB_VERSION_STRING`, and `LIZARDFS_HAVE_DB` when found. It uses `find_library(db)`, `find_path(db.h)`, `file(STRINGS ...)`, regex extraction of version macros, and `find_package_handle_standard_args`.

## Control Flow and State
If headers are found, version macro lines are read and transformed into a five-component version string. Package handling requires both library and include dir and accepts a version variable for CMake's find-package reporting.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(DB 11.2.5.2)`. `config.h.in` can emit `LIZARDFS_HAVE_DB`.

## Risks and Edge Cases
The regex assumes Berkeley DB version macros are present and formatted as expected. Version extraction may produce incorrect strings if the header changes. The module does not set include/library variables into a namespaced imported target.

## Test Signals
CMake find-package success and generated `LIZARDFS_HAVE_DB` are the primary signals. Build targets depending on Berkeley DB will reveal missing link/include propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindDB.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindFUSE.cmake -->
# sources/distributed-fs/lizardfs/cmake/FindFUSE.cmake

## Purpose
This find module locates FUSE 2.x libraries and headers, with separate handling for Apple/pkg-config and non-Apple layouts.

## Important APIs, Types, and Functions
It sets `FUSE_LIBRARY`, `FUSE_LIBRARY_DIR`, `FUSE_INCLUDE_DIR`, `FUSE_CFLAGS`, `FUSE_CFLAGS_OTHER`, and `FUSE_VERSION_STRING` when possible. On Apple it uses `pkg_check_modules(PC_FUSE fuse)` and searches for `fuse.h`. Elsewhere it finds `libfuse` and `fuse/fuse.h`, then reads `fuse_common.h` for major/minor versions.

## Control Flow and State
The module's control path depends on `APPLE`. Version extraction only occurs when an include directory is discovered. `find_package_handle_standard_args` enforces library and include presence for `FUSE_FOUND`.

## Dependencies and Integration Points
`Libraries.cmake` requires FUSE or FUSE3 for non-MinGW builds, and top-level `CMakeLists.txt` adds `src/mount/fuse` when either is found. Link directories include `${FUSE_LIBRARY_DIR}`.

## Risks and Edge Cases
Header layout assumptions differ between platforms. On non-Apple, the module rewrites `FUSE_INCLUDE_DIR` to append `/fuse`, which consumers must expect. pkg-config is required on Apple. No imported target is created.

## Test Signals
Configure reports FUSE discovery. Missing both FUSE and FUSE3 is fatal on non-MinGW. FUSE mount target compile/link success validates include and library variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindFUSE.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindFUSE3.cmake -->
# sources/distributed-fs/lizardfs/cmake/FindFUSE3.cmake

## Purpose
This find module locates FUSE 3 libraries and headers.

## Important APIs, Types, and Functions
It sets `FUSE3_LIBRARY`, `FUSE3_INCLUDE_DIR`, `FUSE3_VERSION_STRING`, and `FUSE3_FOUND`. It finds `libfuse3`, searches for `fuse3/fuse.h`, appends `/fuse3` to the include directory, reads `fuse_common.h`, extracts major/minor version macros, and uses `find_package_handle_standard_args`.

## Control Flow and State
The module is linear and only computes version information when the include directory is present. It does not configure compile definitions directly; callers consume the found variables.

## Dependencies and Integration Points
`Libraries.cmake` runs this alongside FUSE 2 discovery. Top-level build logic includes the FUSE mount implementation when either FUSE family is found.

## Risks and Edge Cases
The include path rewrite must match consumers' include style. Version parsing assumes upstream macro format. There is no pkg-config fallback, which may matter on systems where FUSE3 is installed in nonstandard locations.

## Test Signals
Configure-time `FUSE3_FOUND` and mount target compilation are the practical signals. Missing both FUSE modules is fatal outside MinGW.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindFUSE3.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindJudy.cmake -->
# sources/distributed-fs/lizardfs/cmake/FindJudy.cmake

## Purpose
This find module locates Judy headers and library and performs a runtime check for a Judy1 behavior issue.

## Important APIs, Types, and Functions
It sets `JUDY_INCLUDE_DIR`, `JUDY_LIBRARY`, `JUDY_FOUND`, and `JUDY_HAVE_WORKING_JUDY1`. The runtime check compiles and runs a C program that repeatedly calls `Judy1Set` for many indexes and fails on `JERR` or false insertion.

## Control Flow and State
After finding the path/library, it sets `CMAKE_REQUIRED_INCLUDES` and `CMAKE_REQUIRED_LIBRARIES`, runs `check_c_source_runs`, unsets those variables, and delegates final package handling to `find_package_handle_standard_args`.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(Judy)` and maps success to `LIZARDFS_HAVE_JUDY` and `LIZARDFS_HAVE_WORKING_JUDY1`, which are emitted by `config.h.in`.

## Risks and Edge Cases
The runtime test loops up to 50 million iterations, which can slow configuration or be impossible under cross-compilation. Runtime checks also fail when compiled binaries cannot execute on the configure host.

## Test Signals
Configure-time Judy discovery and the working-Judy macro are the signals. Source code using Judy should be guarded by these macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindJudy.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindPAM.cmake -->
# sources/distributed-fs/lizardfs/cmake/FindPAM.cmake

## Purpose
This find module locates PAM headers and both `pam` and `pam_misc` libraries.

## Important APIs, Types, and Functions
It sets `PAM_INCLUDE_DIR`, `PAM_LIBRARY`, `PAM_MISC_LIBRARY`, `PAM_LIBRARIES`, and `PAM_FOUND`. It searches for `pam_appl.h` with `security` and `pam` path suffixes, then requires both libraries and the include directory through `find_package_handle_standard_args`.

## Control Flow and State
If both libraries are found, `PAM_LIBRARIES` is assembled as a two-library list. No compile tests are run.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(PAM)` and sets `LIZARDFS_HAVE_PAM` when found. `config.h.in` exposes that macro to code that supports PAM authentication.

## Risks and Edge Cases
Some systems may have PAM without `pam_misc`, causing the whole package to be considered not found. The module does not provide imported targets or version checks.

## Test Signals
Configure discovery and `LIZARDFS_HAVE_PAM` are the main signals. PAM-enabled source/link success validates the variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindPAM.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindSocket.cmake -->
# sources/distributed-fs/lizardfs/cmake/FindSocket.cmake

## Purpose
This module locates Berkeley socket support, either as a libc function or via a separate socket library.

## Important APIs, Types, and Functions
It checks `socket()` with `check_function_exists`. If missing, it searches for `ws2_32` or `socket` in default paths and `${SOCKET_PREFIX}`. It sets `SOCKET_FOUND`, `SOCKET_LIBRARIES`, and `LIZARDFS_HAVE_SOCKET`.

## Control Flow and State
The module exits early if `SOCKET_FOUND` or `NO_SOCKET` is set. If `socket()` is in libc, it marks found with an empty library list. If not, it tries library discovery and either succeeds, fatals when required, or logs a skip message.

## Dependencies and Integration Points
`Libraries.cmake` requires `find_package(Socket REQUIRED)`. Socket variables feed link libraries for networking code and feature macros in `config.h.in`.

## Risks and Edge Cases
The line `set(LIZARDFS_HAVE_SOCKET)` in the library-found branch clears rather than sets the variable, which may be intentional or a bug depending on macro expectations. The search paths are minimal. The module spelling says "berkley" in comments but behavior is standard socket discovery.

## Test Signals
Required package failure stops configuration. Successful network target link on MinGW, illumos, or libc-socket systems validates behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindSocket.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindThrift.cmake -->
# sources/distributed-fs/lizardfs/cmake/FindThrift.cmake

## Purpose
This module locates Apache Thrift headers, library, and optionally compiler, with Boost headers as a prerequisite.

## Important APIs, Types, and Functions
Inputs include `THRIFT_ROOT` and requested `Thrift_FIND_COMPONENTS`. Outputs include `THRIFT_FOUND`, `THRIFT_INCLUDE_DIRS`, `THRIFT_LIBRARIES`, and `THRIFT_COMPILER`. It searches environment and CMake root hints plus legacy `/opt/thrift-0.9.x` paths.

## Control Flow and State
If Boost headers are unavailable, it either fatals for required finds or returns after a status message. It builds a `REQUIRED_ITEMS` list based on requested components: `library`, `compiler`, or default library components. Unknown components fatal. `find_package_handle_standard_args` computes success.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(Thrift COMPONENTS library)` and treats Thrift as optional. When found, code can use Thrift include/library variables for components that need RPC support.

## Risks and Edge Cases
The module does not version-check Thrift. It uses older hard-coded search hints. It requires Boost even for compiler-only scenarios because the Boost check happens before component handling.

## Test Signals
Configure status messages report found or missing Thrift. Link/compile of Thrift-enabled code validates variables when optional support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/FindThrift.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/Libraries.cmake -->
# sources/distributed-fs/lizardfs/cmake/Libraries.cmake

## Purpose
This module discovers external libraries, tools, and optional bundled components used by the LizardFS build.

## Important APIs, Types, and Functions
It conditionally finds GTest for tests, requires `fmt`, `spdlog`, sockets, threads, and FUSE/FUSE3 on non-MinGW, detects `rt`, tcmalloc, jemalloc, `a2x`, zlib, systemd via pkg-config, Boost, Thrift, Polonaise, crcutil, Judy, PAM, Berkeley DB, ISA-L, and optional NFS-Ganesha/ntirpc downloads.

## Control Flow and State
The module is configure-time dependency orchestration. It sets feature macros and variables such as `LIZARDFS_HAVE_ZLIB_H`, `LIZARDFS_HAVE_SYSTEMD_SD_DAEMON_H`, `HAVE_CRCUTIL`, `CRCUTIL_LIBRARIES`, `CRCUTIL_INCLUDE_DIRS`, `LIZARDFS_HAVE_JUDY`, and `LIZARDFS_HAVE_PAM`. It fatals when mutually exclusive allocators are both enabled, when required fmt/spdlog/socket/thread/FUSE dependencies are missing, or when request-specific dependencies are unavailable elsewhere.

## Dependencies and Integration Points
Top-level `CMakeLists.txt` includes this before adding subdirectories. It integrates with local find modules, `DownloadExternal`, pkg-config, Boost CMake files, and external bundled `crcutil`. Variables feed `config.h.in`, link libraries, include directories, and optional subdirectory behavior.

## Risks and Edge Cases
Dependency policy is mixed: some missing packages are fatal, others only log optional support. FUSE is mandatory on non-MinGW even if a build might not need the mount client. Bundled crcutil is enabled on little-endian systems when system libcrcutil is absent. Optional NFS-Ganesha triggers network downloads into the source tree. Allocator options are manually exclusive.

## Test Signals
Configure logs are detailed signals. Build success of subsystem targets validates include/link propagation. Enabling tests validates GTest; enabling docs validates `a2x`; enabling NFS-Ganesha validates download and external build paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/Libraries.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/SharedLibraries.cmake -->
# sources/distributed-fs/lizardfs/cmake/SharedLibraries.cmake

## Purpose
This module provides helper functions to build paired static and position-independent libraries for components that may be linked into shared libraries.

## Important APIs, Types, and Functions
`shared_add_library(NAME ...)` creates a normal library and, when `ENABLE_PIC_TARGETS` is true, an additional `${NAME}_pic` library from the same sources with position-independent code. `shared_target_link_libraries(TARGET ...)` links the normal target and, when PIC targets are enabled, links the PIC target with PIC equivalents where available.

## Control Flow and State
`shared_target_link_libraries` parses mode tokens `STATIC`, `SHARED`, and `MIXED`. In mixed mode it links static targets against the original library and PIC targets against `${library}_pic` if that target exists. It mutates target link libraries for both target variants.

## Dependencies and Integration Points
Included by `EnvTests.cmake`, then used by external and source subdirectories. Top-level `CMakeLists.txt` sets `ENABLE_PIC_TARGETS` when `ENABLE_CLIENT_LIB` is enabled.

## Risks and Edge Cases
The function signature uses variadic syntax compatible with older CMake patterns. Target existence checks are simple and depend on consistent `_pic` naming. Incorrect scan-mode ordering can link dependencies to only one variant.

## Test Signals
Building with `ENABLE_CLIENT_LIB=ON` should produce `_pic` library variants and shared-client link success. Static-only builds should produce only normal targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/SharedLibraries.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/mingw32-toolchain.cmake -->
# sources/distributed-fs/lizardfs/cmake/mingw32-toolchain.cmake

## Purpose
This CMake toolchain file configures 32-bit MinGW cross-compilation for Windows.

## Important APIs, Types, and Functions
It sets `CMAKE_SYSTEM_NAME` to `Windows`, `CMAKE_SYSTEM_VERSION` to `8`, C, C++, and resource compilers to `i686-w64-mingw32-*`, and root paths to `/usr/i686-w64-mingw32/` and `/usr/local/i686-w64-mingw32/`.

## Control Flow and State
The file is consumed by CMake before project configuration. It directs find behavior: programs are searched on the host, while libraries and includes are searched only in the target root. It clears shared-library link flags for C and C++.

## Dependencies and Integration Points
It is used with `cmake -DCMAKE_TOOLCHAIN_FILE=cmake/mingw32-toolchain.cmake ...`. Top-level MinGW checks then add Windows definitions and skip non-MinGW subsystems.

## Risks and Edge Cases
Compiler names and root paths are distro-specific. Clearing shared-library link flags may be required for this project but can surprise future shared targets. The system version is fixed at Windows 8.

## Test Signals
Successful CMake configure with this toolchain and compilation of MinGW-supported targets are the signals. Missing cross compiler fails early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/mingw32-toolchain.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/mingw32-w64-toolchain.cmake -->
# sources/distributed-fs/lizardfs/cmake/mingw32-w64-toolchain.cmake

## Purpose
This CMake toolchain file configures 64-bit MinGW-w64 cross-compilation for Windows.

## Important APIs, Types, and Functions
It sets `CMAKE_SYSTEM_NAME` to `Windows`, `CMAKE_SYSTEM_VERSION` to `8`, C, C++, and resource compilers to `x86_64-w64-mingw32-*`, and root paths to `/usr/x86_64-w64-mingw32/` and `/usr/local/x86_64-w64-mingw32/`.

## Control Flow and State
The file directs CMake discovery so build tools come from the host while libraries and includes come from target roots. Shared-library link flags for C and C++ are cleared.

## Dependencies and Integration Points
It is selected via `CMAKE_TOOLCHAIN_FILE` and interacts with top-level MinGW conditionals that alter compiler flags, definitions, and enabled subdirectories.

## Risks and Edge Cases
Hard-coded toolchain names and sysroots may not match all distributions. Like the 32-bit file, it fixes the target Windows version and clears shared-link flags globally.

## Test Signals
Configure and build success with an installed `x86_64-w64-mingw32` toolchain are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/cmake/mingw32-w64-toolchain.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/config.h.in -->
# sources/distributed-fs/lizardfs/config.h.in

## Purpose
This template becomes generated `config.h`, collecting package version constants, install paths, defaults, chunk geometry, portability macros, optional dependency macros, and compiler compatibility fixes for LizardFS C/C++ code.

## Important APIs, Types, and Functions
It defines static macros such as `LIZARDFS_HAVE_PWD_H`, `LIZARDFS_HAVE_STRERROR_R`, and `MASTERINFO_WITH_VERSION`; substitutes package version fields and `LIZARDFS_VERSHEX`; substitutes protocol base, block counts/sizes, install paths, and default daemon/user settings; defines a GCC 4.6 workaround for `override`; and contains many `#cmakedefine` entries for includes, structs, functions, libraries, endianness, debug, CRC, allocator, CPU, and standard-library features.

## Control Flow and State
CMake `configure_file(config.h.in config.h)` performs variable substitution and emits defines for variables set during `EnvTests.cmake`, `Libraries.cmake`, and top-level configuration. The generated header is included from the binary directory and used at compile time only.

## Dependencies and Integration Points
This template is the destination for top-level CMake variables, dependency discovery variables, and environment test outputs. It is included by source files guarded by `LIZARDFS_HAVE_CONFIG_H`.

## Risks and Edge Cases
Hard-coded "extra definitions" bypass actual checks and may become stale. Any mismatch between variable names in CMake probes and `#cmakedefine` entries silently disables expected macros. Install-path substitutions embed absolute paths into binaries/config behavior.

## Test Signals
Generated `config.h` content is the main signal. Cross-platform builds validate conditional macro coverage. Missing macros surface as compile failures or disabled optional code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/config.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/configure -->
# sources/distributed-fs/lizardfs/configure

## Purpose
This shell script is a compatibility wrapper that provides a traditional `./configure` entry point while delegating actual configuration to CMake.

## Important APIs, Types, and Functions
It accepts `--with-doc`, `--without-doc`, `--with-uraft`, and `--without-uraft`, sets defaults, creates `build-pack`, removes stale `CMakeCache.txt`, sets default environment-controlled official/RC build variables, runs CMake with packaging-oriented options, and writes a wrapper `Makefile` in the source root.

## Control Flow and State
The script changes to its own directory, creates an out-of-tree `build-pack`, and configures Release mode with tests off, install prefix `/`, docs according to parsed options, client library on, NFS-Ganesha off, uraft hard-coded on in the CMake invocation, and Polonaise off. It then writes Makefile targets that forward `all`, `clean`, and `install` to `build-pack`; `distclean` removes build artifacts and external gtest plus the wrapper Makefile.

## Dependencies and Integration Points
Debian packaging rules call this script. It depends on CMake, make, shell, and the top-level CMake project. Environment variables `LIZARDFS_OFFICIAL_BUILD` and `LIZARDFS_SET_RC_BUILD_NUMBER` feed package versioning.

## Risks and Edge Cases
The parsed `uraft` variable is not used; the CMake command always passes `-DENABLE_URAFT=YES`, so `--without-uraft` is ineffective. The script rewrites a source-root Makefile and removes external gtest on distclean. It assumes CMake can configure from `build-pack`.

## Test Signals
Running `./configure` should create `build-pack` and a forwarding Makefile. Debian package builds are the primary integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/create-deb-package.sh -->
# sources/distributed-fs/lizardfs/create-deb-package.sh

## Purpose
This script builds Debian packages from a clean cloned copy of the current source tree.

## Important APIs, Types, and Functions
It sets `LIZARDFS_OFFICIAL_BUILD=NO`, determines output/source/working directories, detects distro release with `lsb_release`, chooses systemd or non-systemd rules, clones sources to `/tmp/lizardfs_deb_working_directory/lizardfs`, copies service files into `debian/`, edits changelog version metadata, and runs `dpkg-buildpackage`.

## Control Flow and State
The script deletes and recreates the working directory, clones the repository, copies RPM service files for Debian packaging, strips `-devel` from the first changelog line, derives a package version, optionally appends `BUILD_DATE`, prepends a vendor test-release changelog entry with the current commit, and builds with either default rules or `debian/rules-nosystemd`. Resulting package files are copied back to the original working directory before cleanup.

## Dependencies and Integration Points
It depends on Git, Debian packaging tools, `lsb_release`, `dpkg-buildpackage`, Debian metadata, RPM service-file sources, and the `debian/rules` scripts. The `version` environment variable is consumed by `dh_gencontrol`.

## Risks and Edge Cases
The working directory is a fixed `/tmp` path and is removed recursively. Distribution matching only disables systemd for Debian 7 and Ubuntu 12/14. Changelog parsing is fragile and assumes the first matching header shape. `set -eux` exposes commands and exits on failures.

## Test Signals
Successful `.deb`, `.dsc`, or related artifacts copied to the output directory are the main signal. Build failure from rules, missing deps, or changelog parsing stops the script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/create-deb-package.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/create-osx-package.sh -->
# sources/distributed-fs/lizardfs/create-osx-package.sh

## Purpose
This script builds a macOS `.pkg` installer for LizardFS from a clean cloned source tree.

## Important APIs, Types, and Functions
It computes `lizard_version` by grepping package version fields from `CMakeLists.txt`, clones the source into `/tmp/lizardfs_osx_working_directory/lizardfs`, configures a Release build with tests off and docs on, runs `make`, installs into a staging directory with `DESTDIR`, and calls `pkgbuild`.

## Control Flow and State
The script deletes and recreates the working directory, clones the source, optionally appends Jenkins `BUILD_NUMBER` when `OFFICIAL_RELEASE=false`, builds under `build`, installs under `build-osx`, and packages that root with identifier `com.lizardfs` and the computed version. Result artifacts are copied back to the original directory, then the working directory is removed.

## Dependencies and Integration Points
It depends on Git, CMake, make, macOS `pkgbuild`, docs tooling if docs are enabled, and top-level CMake install rules.

## Risks and Edge Cases
The fixed `/tmp` working path is destructive. Version extraction by grep/awk is brittle. The condition `[[ ${BUILD_NUMBER:-} && ${OFFICIAL_RELEASE:-} == "false" ]]` depends on Bash semantics and CI variables. Docs are forced on, so missing `a2x` may affect manpage generation.

## Test Signals
The resulting `lizardfs-<version>.pkg` copied to the output directory is the success signal. Configure/build/pkgbuild failures terminate due to `set -eux`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/create-osx-package.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/create-rpm-package.sh -->
# sources/distributed-fs/lizardfs/create-rpm-package.sh

## Purpose
This script builds RPM and source RPM packages for supported Red Hat/Fedora-like distributions.

## Important APIs, Types, and Functions
It detects distro family by numeric extraction from `/etc/redhat-release`, maps to `el7`, `el8`, `fc34`, or `fc35`, creates an rpmbuild tree under `/tmp/lizardfs_rpm_working_directory`, derives version from `rpm/lizardfs.spec`, creates a Git archive source tarball, substitutes `@DISTRO@` into the spec, and runs `rpmbuild -ba`.

## Control Flow and State
The script validates the distro, removes and recreates a fixed working tree, archives `HEAD` with prefix `lizardfs-$version/`, writes the spec into `SPECS`, builds binary and source packages, copies generated packages to the original directory, and removes the working tree.

## Dependencies and Integration Points
It depends on Git, RPM build tools, `/etc/redhat-release`, `gzip`, `awk`, and `rpm/lizardfs.spec`. CMake/build behavior is delegated to the spec.

## Risks and Edge Cases
The distro detection is narrow and may reject newer releases. The working directory is fixed and removed recursively. It packages exactly `HEAD`, so uncommitted changes are excluded. Only `RPMS/x86_64` is copied, so other architectures are not handled.

## Test Signals
Successful `.rpm` and `.src.rpm` artifacts in the output directory are the main signal. Unsupported distro or rpmbuild failures stop execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/create-rpm-package.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/debian/rules -->
# sources/distributed-fs/lizardfs/debian/rules

## Purpose
This Debian debhelper rules file builds LizardFS packages with documentation and systemd/init integration.

## Important APIs, Types, and Functions
It overrides `dh_auto_configure`, `dh_gencontrol`, `dh_strip`, `dh_installinit`, and `dh_installsystemd`. The default `%` target delegates to `dh $@`.

## Control Flow and State
Configure runs `./configure --with-doc`, which delegates to CMake. `dh_gencontrol` passes an optional `-v$(version)` when the environment variable is set by package scripts. Strip output goes to `lizardfs-dbg`. Init and systemd install steps use `--no-start`, and systemd also uses `--no-enable`; both handle the `lizardfs-uraft` package with service name `lizardfs-ha-master`.

## Dependencies and Integration Points
It integrates with `configure`, Debian debhelper, package metadata, service files copied by `create-deb-package.sh`, and the `version` environment variable.

## Risks and Edge Cases
Documentation is always requested. Service behavior intentionally avoids starting/enabling daemons during install. The uraft service naming must match package/service files. Build behavior inherits the `configure` script's limitation that `--without-uraft` is ineffective.

## Test Signals
Debian package build logs from debhelper are the signal. Generated control version, debug package, init scripts, and systemd units should reflect these overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/debian/rules-nosystemd -->
# sources/distributed-fs/lizardfs/debian/rules-nosystemd

## Purpose
This Debian debhelper rules file builds LizardFS packages for older distributions without systemd integration.

## Important APIs, Types, and Functions
It overrides `dh_auto_configure` to run `./configure --with-doc` and `dh_strip` to emit `lizardfs-dbg`. The `%` target delegates all other commands to `dh $@`.

## Control Flow and State
Unlike `debian/rules`, this file does not override init or systemd steps and does not override `dh_gencontrol`; it is selected by `create-deb-package.sh` for Debian 7 and Ubuntu 12/14.

## Dependencies and Integration Points
It depends on the same `configure` wrapper and debhelper package metadata, but intentionally omits systemd-specific installation behavior.

## Risks and Edge Cases
Documentation is still forced on. Version override support from `debian/rules` is absent here, so package version handling can differ between systemd and non-systemd builds. Older distro toolchains may also interact poorly with modern C++17 flags.

## Test Signals
Successful package builds on selected older distros validate this file. Absence of systemd unit handling is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/debian/rules-nosystemd -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/doc/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/doc/CMakeLists.txt

## Purpose
This CMake file builds and installs LizardFS manual pages from AsciiDoc sources using `a2x`.

## Important APIs, Types, and Functions
It checks `A2X_BINARY`, defines the `MANPAGES` list, creates custom commands for each existing `<manpage>.txt`, installs generated manpages into `${MAN_SUBDIR}/man<section>`, synthesizes `mfsmount3.1.txt` by replacing `mfsmount` with `mfsmount3`, and creates an `ALL` custom target `manpages`.

## Control Flow and State
If `a2x` is unavailable, it warns and returns early. For each listed manpage, it builds a symlink to the source text in the binary dir and runs `a2x -L -f manpage`, optionally with verbose/keep-artifacts flags. It installs each generated manpage even though generation only occurs for source files that exist. The special `mfsmount3.1` output is always generated from `mfsmount.1.txt`.

## Dependencies and Integration Points
Top-level `CMakeLists.txt` adds `doc` when `ENABLE_DOCS` is on. This file depends on `a2x`, source `.txt` files, CMake install paths, and `ENABLE_VERBOSE_ASCIIDOC`.

## Risks and Edge Cases
The loop calls `install(FILES ${GENERATED_MANPAGE_PATH} ...)` for every listed page, even entries without source files and without generated output, which can cause install-time issues depending on CMake behavior. The `mfsmount3` text replacement is global and may alter more than command names. `ln -s` is Unix-specific.

## Test Signals
The `manpages` target and installed man files are the signals. Missing `a2x` disables generation with a warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/doc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/external/CMakeLists.txt

## Purpose
This CMake file builds the bundled crcutil library when a system crcutil is not found but CRC support is enabled.

## Important APIs, Types, and Functions
It checks `CRCUTIL_FOUND` and `HAVE_CRCUTIL`, includes `${CRCUTIL_INCLUDE_DIRS}`, appends crcutil-specific flags plus `-w` to suppress warnings, globs `${CRCUTIL_SOURCE_DIR}/*.cc`, and calls `shared_add_library(crcutil ...)`.

## Control Flow and State
The file does nothing when system crcutil is found or CRC support is disabled. Otherwise it builds a local `crcutil` target, possibly with a `_pic` variant when PIC targets are enabled.

## Dependencies and Integration Points
`Libraries.cmake` sets crcutil variables and top-level build adds `external` before source subdirectories. It depends on `SharedLibraries.cmake` helper functions already included.

## Risks and Edge Cases
It globally mutates `CMAKE_CXX_FLAGS` to add crcutil flags and disable warnings, which can leak to later targets. Globbing source files requires reconfiguration when bundled sources change.

## Test Signals
Build output should include the bundled `crcutil` target when system libcrcutil is absent on little-endian systems. CRC-enabled code link success validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile

## Purpose
This is a generated Automake Makefile for the bundled Google crcutil 1.0 package. In this repository it is primarily legacy/vendor build metadata; LizardFS' CMake build usually consumes crcutil sources directly through `external/CMakeLists.txt`.

## Important APIs, Types, and Functions
It defines package/install variables, compiler variables, `AM_CXXFLAGS`/`AM_CFLAGS`, `crcutil_ut` as a check program and test, `usage` as a temporary program, source lists for crcutil code, tests, and examples, pattern rules for `.c` and `.cc`, explicit object rules, `check-TESTS`, distribution targets, install/uninstall targets, and clean/distclean/maintainer-clean targets.

## Control Flow and State
The default `all` target depends on `config.h` and delegates to `all-am`. Build rules compile crcutil implementation files and link `crcutil_ut` and `usage`. `check` builds and runs `crcutil_ut`. Install behavior installs only temporary programs to `${tmpdir}`. Distribution targets create tarballs and run standard Automake distcheck flows.

## Dependencies and Integration Points
It depends on generated autotools files such as `configure`, `config.status`, `config.h.in`, dependency files under `.deps`, GCC/G++, and crcutil source directories. LizardFS CMake does not rely on this Makefile for normal bundled compilation.

## Risks and Edge Cases
As generated vendor output, it contains absolute paths from its original generation environment, old Automake assumptions, and many generated rules that are not maintained manually. It uses SSE/MMX flags and architecture-specific sources, which can fail on unsupported compilers or architectures if this Makefile is used directly. Because CMake builds crcutil separately, changes here may not affect the main build.

## Test Signals
Standalone `make check` would run `crcutil_ut`. In the LizardFS CMake path, the more relevant signal is whether bundled crcutil sources compile and link into LizardFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.am -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.am

## Purpose
This is the concise Automake source file that generated the crcutil `Makefile`. It describes compiler flags, test binary sources, and example usage program sources for standalone crcutil builds.

## Important APIs, Types, and Functions
It sets `AM_CXXFLAGS` to enable CRCUTIL's MM CRC32 mode, warnings, SSE2, and `-Icode`; mirrors that into `AM_CFLAGS`; declares `crcutil_ut` as both `check_PROGRAMS` and `TESTS`; sets `tmpdir=/tmp`; declares `usage` as a temporary program; and lists all crcutil, test, and example sources.

## Control Flow and State
Automake consumes this file to produce the much larger `Makefile.in`/`Makefile` logic. It has no runtime control flow.

## Dependencies and Integration Points
It depends on crcutil source directories `code/`, `tests/`, and `examples/`, plus Automake/autoconf when regenerating vendor build files. The main LizardFS CMake build does not read this file directly.

## Risks and Edge Cases
The hard-coded `-msse2` and CRC mode are architecture-specific. Standalone build behavior can diverge from LizardFS CMake's bundled crcutil target. Regenerating autotools files may change the generated Makefile substantially.

## Test Signals
Standalone `make check` should build and run `crcutil_ut`. CMake builds of bundled crcutil provide the integration-level signal for LizardFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/Makefile.am -->
