# Research: subset-b-007961

Scope: XRootD `src/XrdPosix` POSIX compatibility, cache, file, directory, callback, linkage, and mapping layer.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.cc

Purpose: implements the exported C POSIX wrapper entry points that decide whether each operation targets XRootD or native Unix. It owns the global `XrdPosixXrootd Xroot`, `XrdPosixXrootPath XrootPath`, and references the native linkage vector `Xunix`.

Important APIs/functions: `XrdPosix_Access`, `Open`, `Openat`, `Fopen`, `Read`, `Write`, `Pread`, `Pwrite`, `Readv`, `Writev`, `Stat`, `Fstat`, `Fstatat`, `Statx`, `Opendir`, readdir variants, `Rename`, `Unlink`, `Truncate`, xattr wrappers, `XrdPosix_isMyPath`, and `XrdPosix_URL`. `XrdResolveLink()` is a local helper that follows local symlinks with `realpath()`/`readlink()` before URL classification. `fseterr()` and `fseteof()` manipulate libc `FILE` internals so stdio wrappers can report XRootD read/write status.

Control flow: path-based calls resolve links, pass the resolved path through `XrootPath.URL()`, then dispatch to `Xroot` for remote paths or `Xunix`/direct syscalls for local paths. Descriptor-based calls use `Xroot.myFD()` and directory calls use `Xroot.isXrootdDir()`. `Fopen()` translates mode strings to open flags, opens through `Xroot`, and wraps the returned descriptor with `fdopen()`. `Creat()` delegates to `Open()`.

State and persistence: no durable state is written here. Runtime state is in global XRootD path/FD registries and libc streams. `Chdir()` updates `XrootPath.CWD()` only after native `chdir()` succeeds.

Dependencies/integration: integrates with `XrdPosixXrootd`, `XrdPosixXrootdPath`, `XrdPosixLinkage`, `XrdSysStatxHelpers`, libc, and platform syscalls. It is the LD-preload or macro-facing boundary for applications.

Risks: symlink resolution uses fixed 2048/2049 buffers and only follows 10 links. Some local fallback paths call raw syscalls instead of `Xunix`, creating platform-specific behavior. `Fcntl()` returns success for XRootD FDs without implementing command semantics. `Statx()` calls `XrdPosix_Stat()` with an already translated path, which is worth regression testing. FILE flag manipulation is libc-layout-sensitive.

Test signals: exercise local-vs-remote dispatch for all wrappers; remote stdio EOF/error behavior; symlink to remote URL; `openat`/`fstatat` with and without `AT_SYMLINK_NOFOLLOW`; xattr unsupported cases; directory iteration; `statx` conversion; mixed local and XRootD descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.hh

Purpose: public include that redirects common POSIX and stdio function names to the XRootD-aware `XrdPosix_*` wrappers. It is intended for source-level interposition where platform-specific wrapper mechanisms are unreliable.

Important APIs/types: includes `XrdPosixExtern.hh` and defines macros for `access`, `chdir`, `close`, directory functions, `open`, `openat`, read/write variants, stat functions, xattr functions, and `statx`.

Control flow: there is no runtime flow; inclusion rewrites subsequent source references through preprocessor macros. `open` and `openat` are macro aliases without argument lists so varargs survive. `rewinddir` is explicitly undefined first to handle prior macro definitions.

State and persistence: no state. It changes compile-time symbol binding for translation units that include it.

Dependencies/integration: depends on `dirent.h` and the ABI-safe declarations in `XrdPosixExtern.hh`. It integrates with both preload-style exported symbols and direct source inclusion.

Risks: macro interposition is broad and can unexpectedly affect third-party headers included afterward. `lstat` is mapped to `XrdPosix_Stat` rather than `XrdPosix_Lstat`, which intentionally follows the same semantics as the implementation but is surprising. Missing coverage for functions not listed here will bypass XRootD dispatch.

Test signals: compile representative clients with this header; verify varargs calls still compile; confirm local and remote behavior for `lstat`, `open`, `statx`, and xattrs; test inclusion order with system headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.cc

Purpose: implements administrative filesystem operations around `XrdCl::FileSystem`, primarily locate, query, and stat for a URL.

Important APIs/functions: `FanOut(int&)`, `Query(QueryCode, void*, int)`, `Query(QueryCode, std::string&)`, `Stat(mode_t*, time_t*)`, and `Stat(struct stat&)`.

Control flow: each method first validates the URL through `isOK()`. `FanOut()` performs `DeepLocate()` with `PrefName`, converts each returned address through `XrdNetAddr`, clones the original URL, replaces host/port, and returns a newly allocated URL array. `Query()` sends the path-with-params as an `XrdCl::Buffer`, validates response buffer size, and copies to caller storage or string. `Stat()` calls `Xrd.Stat()`, maps protocol flags to POSIX mode, fills size, inode, blocks, timestamps, and extended permissions when present.

State and persistence: no persistent state. Per-call heap responses (`LocationInfo`, `StatInfo`, `Buffer`) are deleted before return. Errors are stored in the referenced `XrdOucECMsg` and `errno` via `XrdPosixMap::Result()`.

Dependencies/integration: wraps `XrdCl::URL`, `XrdCl::FileSystem`, `XrdCl` response types, `XrdNetAddr`, and `XrdPosixMap`. Used by directory listing, stat-like wrappers, and extended filesystem control paths.

Risks: callers own the `FanOut()` returned array. `Stat.st_blocks` uses `size/512 + size%512`, which overcounts for nonzero remainders by bytes rather than block boolean. Buffer query requires `bsz >= rspSz + 1`; callers must pass enough storage. `strtoll()` inode parsing has no error handling.

Test signals: locate with multiple replicas; invalid URL error message; query response with and without trailing NUL; too-small buffer returns `ERANGE`; stat extended and non-extended format permissions/timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.hh

Purpose: declares `XrdPosixAdmin`, a small URL-bound administrative facade for XRootD filesystem metadata and query operations.

Important APIs/types: public members `Url`, `Xrd`, and `ecMsg`; methods `isOK()`, `FanOut()`, `Query()` overloads, and `Stat()` overloads. Constructor binds a path string to `XrdCl::URL` and `XrdCl::FileSystem`.

Control flow: callers construct an admin object per path/URL and call an operation. `isOK()` centralizes URL validation, fills `ecMsg`, and sets `errno=EINVAL` on invalid URLs.

State and persistence: owns an `XrdCl::URL` and `XrdCl::FileSystem` by value; references an external `XrdOucECMsg`. It writes no durable state.

Dependencies/integration: includes `XrdClFile`, `XrdClFileSystem`, `XrdClURL`, XRootD response types, and `XrdOucECMsg`. It is used by `XrdPosixDir`, `XrdPosixExtra`, and stat/administrative paths.

Risks: public mutable members allow callers to alter URL/filesystem state directly. `ecMsg` lifetime must exceed the admin object. `isOK()` has side effects, so validation is not a pure predicate.

Test signals: constructing with invalid and valid URLs; repeated operations after mutating `Url`; lifecycle where shared `ecMsg` captures errors across calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.cc

Purpose: provides the POSIX cache-context adapter methods that forward to the process-global `XrdOucCache`.

Important APIs/functions: `CachePath`, `CacheQuery`, `Rmdir`, `Rename`, `Stat`, `Statistics`, `Truncate`, and `Unlink`.

Control flow: all methods dereference `XrdPosixGlobals::theCache`. `CachePath()` requests a local cache path with `ForPath`; `CacheQuery()` uses `ForAccess` when holding a cached file or `ForInfo` for status-only checks and maps `0` to fully cached, `-EREMOTE` to not fully cached, and other failures to `-1`.

State and persistence: the adapter does not maintain state but operates on the underlying cache, which may persist local cache entries and statistics. `Statistics()` copies cache counters from `theCache->Statistics`.

Dependencies/integration: integrates `XrdOucCache`, `XrdOucCacheStats`, and the global cache set by configuration. Used by cache context manager initialization and cache-aware POSIX operations.

Risks: no null checks before using `theCache`; callers must ensure cache initialization. Return-value semantics mix negative errno-style cache values with POSIX-style `-1`. Some operations may be unsupported by a cache implementation despite being exposed here.

Test signals: cache enabled/disabled setup; `LocalFilePath()` return mapping for full, remote/incomplete, and error states; cache stat/unlink/rename behavior; statistics population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.hh

Purpose: declares `XrdPosixCache`, the adapter class exposed to cache context manager code for path lookup, status, metadata, mutation, and statistics operations.

Important APIs/types: `CachePath`, `CacheQuery`, `Rmdir`, `Rename`, `Stat`, `Statistics`, `Truncate`, `Unlink`; forward declaration of `XrdOucCacheStats`.

Control flow: header documents expected return contracts, including `CacheQuery()` full/partial/missing semantics and mutation method error values.

State and persistence: class has no fields; it is a stateless facade over a global cache implementation.

Dependencies/integration: the implementation depends on `XrdOucCache`; callers use this type as the POSIX cache interface. It is constructed statically in `XrdPosixConfig::initCCM()`.

Risks: documentation comments for some methods are copy-paste inaccurate, calling stat/statistics "Rename"; this can confuse implementers. Lack of explicit cache pointer in the type hides dependency on global initialization.

Test signals: API contract tests against a fake or instrumented cache; verify documented negative error cases, especially `Unlink()` returning `-EBUSY`, `-EAGAIN`, or `-errno`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.cc

Purpose: implements completion glue for asynchronous POSIX I/O callbacks.

Important APIs/functions: `XrdPosixCallBackIO::Done(int result)`.

Control flow: when cache/XRootD I/O completes, `Done()` first unreferences the associated `XrdPosixFile`, translates negative internal result values into `errno=-result` and callback result `-1`, then calls the user-implemented `Complete(ssize_t)`.

State and persistence: uses `theFile` pointer set by async issuers. It mutates only object reference counts and thread-local/process `errno`; no durable state.

Dependencies/integration: depends on `XrdPosixCallBack.hh` and `XrdPosixFile.hh`. Called through `XrdOucCacheIOCB` response scheduling in `XrdPosixFileRH` and extended pgread/pgwrite paths.

Risks: `Done()` assumes `theFile` is valid when invoked. Callback code runs after unref, so callers must not expect the file to remain alive unless they own another reference. `errno` is process/thread-local side effect before user callback.

Test signals: async success and failure callbacks; file close racing with async completion; callback observing correct result and `errno`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.hh

Purpose: defines callback interfaces for asynchronous open and asynchronous file I/O in the POSIX layer.

Important APIs/types: `XrdPosixCallBack` with pure virtual `Complete(int)`, and `XrdPosixCallBackIO` deriving from `XrdOucCacheIOCB` with pure virtual `Complete(ssize_t)`, private `Done(int)`, and `XrdPosixFile *theFile`.

Control flow: async open always returns `-1` with `errno=EINPROGRESS` on accepted work and later calls `Complete()` with the synchronous-style result. Async I/O completion is routed through `Done()`, which is friend-accessed by `XrdPosixExtra` and `XrdPosixXrootd`.

State and persistence: only stores a transient file pointer for outstanding I/O; no persistence.

Dependencies/integration: depends on `XrdOucCacheIOCB` and is consumed by `XrdPosixFile`, `XrdPosixFileRH`, `XrdPosixExtra`, and open paths.

Risks: documentation says callback objects are caller-owned after invocation; misuse can leak or double-delete callbacks. Immediate-error callbacks may run on the calling thread, so user locks must be reentrant if callback re-enters guarded code.

Test signals: accepted async open, rejected async open, immediate async I/O error, scheduled async I/O completion, callback deletion policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixCallBack.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.cc

Purpose: implements global configuration and initialization hooks for the POSIX layer, including scheduler/logger wiring, client environment settings, cache setup, connection cleanup tracking, default stat fields, and statistics formatting.

Important APIs/functions: `conTracker`, `EnvInfo`, `initCCM`, `initEnv(char*)`, `initEnv(XrdOucEnv&,...)`, `initStat`, `initXdev`, `OpenFC`, `SetConfig`, `SetDebug`, `SetEnv` overloads, `SetIPV4`, `setOids`, and `Stats`.

Control flow: `SetConfig()` is the main entry point from `XrdOucPsx`: it installs loggers, configures name-to-name PFN/LFN translation, applies client environment values, debug/trace, response-handler cache size, delayed-destroy retry policy, optional automatic pgread/TLS behavior, and either external cache, cache context manager, or memory cache. `initEnv()` parses `XRDPOSIX_CACHE` CGI-style options into `XrdRmc::Parms` and preread parameters. `conTracker()` registers a postmaster connect handler and returns a cleanup handler that can disconnect tracked SSS contacts.

State and persistence: writes many `XrdPosixGlobals` values: scheduler, cache, logger, name mapper, stats/tracing flags, directory-list flags, delayed-destroy settings, and feature booleans. It updates `XrdCl::DefaultEnv`. No files are persisted here, but cache plugins may persist data.

Dependencies/integration: integrates `XrdCl::DefaultEnv`, `JobManager`, `PostMaster`, `XrdOucPsx`, `XrdOucCache`, `XrdRmc`, `XrdSecsssCon`, `XrdSysError`, tracing, stats, and file response-handler configuration.

Risks: global mutable configuration is order-sensitive. `initXdev()` uses `stat("/tmp")` after POSIX macro interposition may be active. `Stats()` manually sizes XML-like text and returns `0` on truncation after partial formatting. `optsf` suffix uses `strdup()` and is not freed. Cache global can be overwritten by config paths.

Test signals: configure external cache, memory cache, and no cache; parse numeric suffixes and invalid values; directory-list flag precedence; IPv4 vs all-stack setting; stats buffer length query and truncation; delayed destroy parameters; auto pgread enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.hh

Purpose: declares the static configuration facade for XrdPosix runtime setup and status.

Important APIs/types: `XrdPosixConfig` static methods `conTracker`, `EnvInfo`, `initStat`, `SetConfig`, `OpenFC`, `SetEnv` overloads, `setOids`, and `Stats`; private helpers for cache/env/debug/IP/device initialization.

Control flow: callers do not instantiate meaningful state; all behavior is static and affects process globals. `OpenFC()` bridges configuration-aware open decisions into an `XrdPosixInfo` result.

State and persistence: no instance fields. The implementation mutates `XrdPosixGlobals` and `XrdCl::DefaultEnv`.

Dependencies/integration: forward-declares `XrdOucEnv`, `XrdOucPsx`, `XrdScheduler`, `XrdPosixInfo`, `XrdSecsssCon`, and `XrdSysLogger`; includes POSIX types. It is a central integration point for plugins/server-side setup.

Risks: static-only design makes tests sensitive to global residue between cases. Missing explicit reset API. `SetEnv` names include internal keys not obvious from the header.

Test signals: isolate configuration tests with process reset or explicit cleanup; verify `OpenFC()` behavior with cache direct-open info; check that `initStat()` stable defaults match target platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.cc

Purpose: implements remote directory listing as POSIX `DIR`/`dirent64` style iteration over `XrdCl::DirectoryList`.

Important APIs/functions: `nextEntry(dirent64*)`, `StatRet(struct stat*)`, and `Open()`.

Control flow: `Open()` allocates a padded local `dirent64`, calls `DAdmin.Xrd.DirList()` with global directory-list flags, stores the returned directory vector, and returns a fake `DIR*` pointing at the object FD. `nextEntry()` lazily opens when needed, bounds iteration by `numEnt`, copies entry name and platform-specific inode/offset fields, optionally maps entry stat info into `myBuf`, then advances `nxtEnt`. `rewind()` in the header clears cached listing so the next call refetches.

State and persistence: per-object state includes `myDirVec`, allocated `myDirEnt`, optional stat output pointer, current/total entry counters, and last error. No durable state.

Dependencies/integration: uses `XrdPosixAdmin`, `XrdPosixMap::Result`, `XrdPosixMap::Entry2Buf`, and global `dlFlag` configured by `XrdPosixConfig`.

Risks: returned `DIR*` is not a real libc directory stream; only XrdPosix wrappers should consume it. Entry names are truncated to 256 bytes. `StatRet()` stores a caller-provided pointer and depends on the next `nextEntry()` call. Missing stat info becomes an error when stat output is requested.

Test signals: empty directory; long names; rewind and seek/tell behavior; directory listing with `DirlistAll` stat flags; `readdir_r` result/status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.hh

Purpose: declares `XrdPosixDir`, the remote directory object stored in the XrdPosix descriptor table.

Important APIs/types: derives from `XrdPosixObject`; contains `XrdPosixAdmin DAdmin`, `XrdCl::DirectoryList *myDirVec`, `dirent64 *myDirEnt`, optional `struct stat *myBuf`, counters, and error state. Provides `dirNo(DIR*)`, `getEntries`, `getOffset`, `setOffset`, `nextEntry`, `Open`, `StatRet`, `rewind`, `Status`, `Unread`, and `Who(XrdPosixDir**)`.

Control flow: descriptor table lookup uses `Who()` to downcast. `DIR*` values are synthesized from the object FD, and `dirNo()` reverses that encoding.

State and persistence: all state is in-memory per open directory. Destructor deletes the directory list and frees the synthetic dirent buffer.

Dependencies/integration: includes `XrdPosixAdmin.hh` and `XrdPosixObject.hh`. It is used by `XrdPosixXrootd` directory wrappers and `XrdPosix.cc` dispatchers.

Risks: synthetic `DIR*` representation depends on callers never passing it to native libc. `setOffset()` does not validate bounds. `maxDlen=256` can truncate longer protocol names.

Test signals: descriptor-table `Who()` behavior; close cleanup; seek/tell offsets beyond list size; concurrent directory access locking via base object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtern.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtern.hh

Purpose: declares the C ABI exported XrdPosix wrapper functions and helper probes for use by macro wrappers or preload clients.

Important APIs/types: extern declarations for POSIX wrappers including file, stdio, directory, stat/statfs/statvfs/statx, xattr, and path helpers `XrdPosix_isMyPath` and `XrdPosix_URL`.

Control flow: compile-time only. The header enforces large-file compile flags unless building `XRDPOSIXPRELOAD32`, predeclares structs to avoid symbol conflicts, and wraps declarations in `extern "C"` for C++.

State and persistence: none.

Dependencies/integration: includes `XrdSysStatx.hh`, `dirent.h`, `stdio.h`/`cstdio`, `unistd.h`, `sys/types.h`, and `XrdPosixOsDep.hh`. It must match implementations in `XrdPosix.cc` and preload symbol expectations.

Risks: ABI correctness is critical: signature mismatches break LD-preload interception. Some declarations are platform-conditional; build matrix coverage is needed. The large-file preprocessor guard can fail consumers that include the header before setting required macros.

Test signals: compile C and C++ clients with required flags; symbol export/`nm` checks; 32-bit preload compatibility; platform builds for Linux, macOS, Solaris/BSD variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtern.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.cc

Purpose: implements non-standard extended XrdPosix APIs for file/filesystem control queries and page read/write operations with checksums and optional async callbacks.

Important APIs/functions: `Fctl`, `FSctl`, `pgRead`, `pgWrite`, and two `PreRead` overloads.

Control flow: `Fctl()` currently supports `QFinfo`, resolves the descriptor to `XrdPosixFile`, then calls the file/cache I/O `Fcntl()`. `FSctl()` supports `QFSinfo`, optionally routes to global cache `Fcntl()`, otherwise constructs `XrdPosixAdmin`, optionally stats first for redirect resolution, and queries filesystem info. `pgRead()`/`pgWrite()` resolve and lock the file, validate size fits signed 32-bit, manage checksum vectors, dispatch sync through `XCio` or async by setting `cbp->theFile`, taking a file reference, and releasing the lock.

State and persistence: no durable state. Async calls temporarily extend file lifetime by reference. `pgWrite()` updates cached size on sync success.

Dependencies/integration: uses `XrdOucCacheOp`, `XrdOucPgrwUtils`, `XrdPosixObject::File`, `XrdPosixFile`, `XrdPosixCallBackIO`, global cache and thread-local `ecMsg`.

Risks: `PreRead()` is effectively a stub returning success after descriptor validation. Async invalid-FD path calls `Complete(-1)` without setting `errno` locally. Checksum vector count validation is important for partial pages. `Fctl()` comment is truncated in source.

Test signals: `QFinfo` on valid/invalid FD; `QFSinfo` via cache and direct admin; pgread force checksum behavior; pgwrite generated and caller-provided checksums; async callback lifetime; oversized I/O returns `EOVERFLOW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.hh

Purpose: declares the extended POSIX-to-XRootD interface beyond standard POSIX calls.

Important APIs/types: static `XrdPosixExtra::Fctl`, `FSctl`, `pgRead`, `pgWrite`, `PreRead` overloads, and option constant `forceCS`.

Control flow: API comments define sync versus async behavior. For pgread/pgwrite, absence of callback returns byte count or `-1`; callback presence returns `0` and completes later.

State and persistence: class has no fields. Operations act on open file descriptors, cache state, and caller-provided buffers/checksum vectors.

Dependencies/integration: includes `XrdOucCache.hh` for operation codes and range lists, and standard vector/string/POSIX types. Bridges public callers to `XrdPosixFile`/cache internals.

Risks: caller must preserve buffers and checksum vectors until async completion. `void* buffer` for write could be `const void*` semantically but is mutable in signature. `PreRead` documentation promises behavior not yet implemented by source.

Test signals: header/implementation contract for async ownership; range-list preread advertised success; checksum option compatibility with cache plugins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixExtra.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.cc

Purpose: implements the core remote file object, combining descriptor-object behavior, `XrdOucCacheIO` backend methods, `XrdCl::File` operations, async response handling, cache attachment, stat caching, and delayed destruction.

Important APIs/functions: constructor/destructor, `DelayedDestroy` thread and enqueue overload, `Close`, `Fcntl`, `Finalize`, `Fstat`, `HandleResponse` for async open, `Location`, pgread/pgwrite sync and async overloads, `Read`, `ReadV`, `Stat`, `Sync`, `Trunc`, and `Write`.

Control flow: construction stores origin/cache paths, applies name-to-name translation when a cache exists, and sets cache options. `Finalize()` initializes current offset, stats an open file or uses deferred `PrepIO`, then attaches cache if configured. I/O methods take a reference, call the relevant `XrdCl::File` operation, unref on synchronous completion, or hand a response handler the responsibility to unref. Read can auto-convert to pgread when configured. `DelayedDestroy()` runs in a background thread and retries closing files whose reference count or remote close status prevents immediate deletion.

State and persistence: per-file state includes `XCio`, optional deferred `PrepIO`, `clFile`, size/timestamps/mode/inode/rdev, current offset, callback/linked-list union fields, origin/cache path/location, cache options, stream flag, and static delayed-destroy queues. No direct durable writes except remote file/cache I/O.

Dependencies/integration: integrates `XrdCl::File`, cache interfaces, `XrdPosixConfig`, `XrdPosixFileRH`, `XrdPosixPrepIO`, stats/trace, name mapping, and global delayed-destroy/cache settings.

Risks: heavy global/static lifetime complexity. Union reuse for current offset/callback/next pointer and cache option/try count requires strict phase separation. Delayed destroy can leak into `ddLost` after retry exhaustion. Size/block calculations and stat field population must match admin stat behavior. Async paths rely on balanced `Ref()`/`unRef()`.

Test signals: sync and async read/write/readv/pgread/pgwrite; close during active I/O; deferred open/cache attach; failed close retry and lost counters; auto pgread mode; stat extended metadata; location refresh property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.hh

Purpose: declares `XrdPosixFile`, the central file object stored in the POSIX descriptor table and exposed as an `XrdOucCacheIO` backend.

Important APIs/types: inherits `XrdPosixObject`, `XrdOucCacheIO`, `XrdOucCacheIOCD`, and `XrdCl::ResponseHandler`. Public fields include `XCio`, `PrepIO`, `clFile`, stat metadata, delayed-destroy statics, structured-file suffix settings, and option flags `realFD`, `isStrm`, `isUpdt`. Methods cover offset management, close/finalize/stat, cache I/O operations, async response handling, location, and write size updates.

Control flow: descriptor lookups downcast via `Who(XrdPosixFile**)`. Cache operations call virtual `Read`, `Write`, `ReadV`, `Sync`, `Trunc`, `FSize`, `Fstat`, `Path`, `Location`, and page I/O methods. Offset and size are protected by `updMutex`, while object lifetime/descriptor access is protected by base-class locks and references.

State and persistence: maintains in-memory metadata and references for a single open remote file. Static delayed-destroy queues hold files that cannot be immediately closed/deleted.

Dependencies/integration: includes XrdCl file/filesystem/url/response types, `XrdOucCache`, `XrdPosixMap`, and `XrdPosixObject`. Used by standard wrappers, cache, extra page APIs, and response handlers.

Risks: public mutable metadata can be changed by collaborators. Header exposes implementation-specific statics. Correct lock ordering between object lock, update mutex, and FD mutex is critical. `FSize()` returns cached size under lock but may differ from remote if not refreshed.

Test signals: class-level tests with mocked `XrdCl::File`; offset update under concurrent reads/writes; cache detach lifecycle; destructor close accounting; static delayed-destroy configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFileRH.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFileRH.cc

Purpose: implements reusable async response handlers that translate XrdCl responses into `XrdOucCacheIOCB` completions.

Important APIs/functions: static `Alloc`, `HandleResponse`, `Recycle`, `Sched`, and helper thread entry `callDoIt`.

Control flow: `Alloc()` pulls a handler from a bounded free list or allocates one, initializes callback/file/offset/result/type/checksum fields, and returns it to the I/O issuer. `HandleResponse()` maps failed status to negative errno, extracts read length from `ChunkInfo`, extracts page length/checksums/repair count from `PageInfo`, optionally computes checksums when forced, updates file size for writes, deletes response objects, unreferences the file, and schedules `DoIt()` through the global scheduler or a new thread. `Sched()` handles immediate errors similarly.

State and persistence: static free list protected by `myMutex`, configurable `maxFree`; per-handler transient callback, file, checksum, offset, result, and type. No durable state.

Dependencies/integration: uses `XrdScheduler`, `XrdOucCacheIOCB`, `XrdOucPgrwUtils`, `XrdPosixFile`, and `XrdPosixMap`. It is central to all async file/cache I/O completion.

Risks: for `isWrite`, size update uses `offset+result`; if `result` is an initial requested length rather than actual completion length, partial-write semantics need scrutiny. Scheduling fallback creates a thread per completion when no scheduler exists. Free-list reuse demands all fields be reset in `Alloc()`.

Test signals: async read/readv/write/sync/page-read success and error; forced checksum generation; repair count propagation; no-scheduler fallback; free-list max behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFileRH.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFileRH.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFileRH.hh

Purpose: declares the response-handler/job class used to complete asynchronous file operations.

Important APIs/types: `XrdPosixFileRH` inherits `XrdJob` and `XrdCl::ResponseHandler`. `ioType` enumerates `nonIO`, read/readv/write/page read/page write. Public methods include `Alloc`, `DoIt`, `HandleResponse`, `Recycle`, `setCSVec`, `SetMax`, and `Sched`.

Control flow: `HandleResponse()` records a result, schedules the object as an `XrdJob`, `DoIt()` calls `theCB->Done(result)`, then recycles the handler.

State and persistence: static free-list state plus per-operation callback/file/checksum/result fields. It holds no persistent storage.

Dependencies/integration: includes Xrd job, XrdCl file response handler, and pthread utilities; forward-declares `XrdOucCacheIOCB` and `XrdPosixFile`.

Risks: lifecycle depends on callback and file pointers remaining valid until completion; issuers must take file refs before submitting. Private destructor means objects are managed only by allocation/recycle logic. `isWriteP` exists but implementation treats page write as `isWrite`.

Test signals: allocation/recycle under concurrency; `SetMax(0)` behavior; callback ordering; page-write type expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFileRH.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixInfo.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixInfo.hh

Purpose: defines `XrdPosixInfo`, a small open-result carrier used when a caller needs callback, descriptor, and cache direct-file information from an open attempt.

Important APIs/types: fields `cbP`, `fileFD`, `ffReady`, `cacheURL[7]`, and `cachePath[MAXPATHLEN]`; constructor initializes callback, `fileFD=-1`, `ffReady=false`, `cacheURL` to `"file://"`, and empty cache path.

Control flow: populated by open/config code, especially `XrdPosixConfig::OpenFC()` and `XrdPosixXrootd::Open()` paths. `ffReady` plus `cachePath` can signal a direct local cache file is ready.

State and persistence: plain stack/heap data carrier; no ownership beyond callback pointer reference.

Dependencies/integration: includes platform `MAXPATHLEN` support and forward-declares `XrdPosixCallBack`.

Risks: `cacheURL[7]` stores exactly six characters plus NUL for `"file://"`; callers must not append in place beyond bounds. Callback pointer ownership is external. `cachePath` fixed length can truncate if writers are careless.

Test signals: constructor defaults; direct cache open result path; async open callback propagation; maximum path length handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.cc

Purpose: implements the native Unix callout vector for interposed POSIX functions, resolving real libc symbols with `dlsym(RTLD_NEXT)` and providing failure stubs.

Important APIs/functions: global `XrdPosixLinkage Xunix`; `Resolve()`, `Load_Error()`, `Missing()`, `LOOKUP_UNIX` macro, and many `Xrd_U_*` unresolved stubs.

Control flow: static construction calls `Init()`/`Resolve()`. Each symbol pointer is loaded from the next shared object; missing symbols are replaced by a stub and recorded. Wrapper code calls `Xunix.<Function>()` for local paths. `Load_Error()` reports unresolved calls through native write paths when available, sets `errno=ELIBACC`, and returns a failure value. If `XRDPOSIX_REPORT` is set, all missing symbols are printed.

State and persistence: stores function pointers in the global `Xunix` object and a process-local linked list of missing symbol names. No durable state.

Dependencies/integration: depends on `dlfcn.h`, platform linker headers, `XrdPosixLinkage.hh`, libc, and OS-specific symbol names. It is foundational for preload safety.

Risks: symbol signatures in the header must exactly match platform libc. Fallback report string in `Missing()` appears to omit a closing quote/paren formatting. Some stubs abort for void directory functions. Duplicate `LOOKUP_UNIX(Fsync)` appears in `Resolve()`. Static initialization order matters.

Test signals: LD_PRELOAD smoke tests; `XRDPOSIX_REPORT` missing-symbol output; platform builds for Linux/macOS/Solaris; local passthrough for every wrapper; unresolved symbol failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.hh

Purpose: defines platform-specific native POSIX symbol names, return types, argument lists, and the `XrdPosixLinkage` function-pointer table.

Important APIs/types: `Symb_*`, `Retv_*`, and `Args_*` macros for access, open, stat variants, stdio, directory, xattr, and I/O calls; class `XrdPosixLinkage` with function-pointer members, `Init`, `Load_Error`, private `Resolve`, and `Missing`.

Control flow: constructor initializes the table by resolving symbols. Wrappers use table entries for local passthrough. Macro definitions account for Linux `_STAT_VER` symbols, macOS 64-bit aliasing, and optional `statx`.

State and persistence: one object holds resolved pointers and `Done` initialization flag. No persistence.

Dependencies/integration: includes POSIX headers, `XrdPosixOsDep.hh`, `XrdPosixXrootd.hh`, platform/statx helpers. Must remain consistent with `XrdPosixLinkage.cc` and system ABI.

Risks: `Args_Openat`/`Args_Openat64` macros omit the `dirfd` parameter shape expected by POSIX `openat`; this warrants platform build verification even if not used in `Resolve()` currently. Conditional macro complexity can hide ABI drift. Function pointer varargs are inherently hard to type-check.

Test signals: compile with strict warnings on each supported OS; compare resolved symbol names using `dlsym`; run local passthrough operations with `_FILE_OFFSET_BITS=64`; validate stat ABI variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixLinkage.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.cc

Purpose: implements translation between XRootD client/protocol metadata/status and POSIX modes, stat buffers, access modes, `errno`, and return values.

Important APIs/functions: `Flags2Mode`, `Entry2Buf`, private `mapCode`, `Mode2Access`, and `Result`.

Control flow: `Flags2Mode()` maps `XrdCl::StatInfo` flags to `S_IF*` and user permission bits, plus special XRootD SFS flags through `st_rdev`. `Entry2Buf()` maps directory-list stat info into `struct stat`, preserving extended POSIX permission mode when available or widening owner bits to other bits when not. `mapCode()` maps `XrdCl` client error codes to errno values. `Result()` handles success, protocol error responses via `XProtocol::toErrno`, generic client errors through `mapCode`, stores the message into `ecMsg`, sets `errno`, and returns either `-1` or `-errno`.

State and persistence: only static `Debug` flag. No durable state.

Dependencies/integration: uses `XrdCl` status/stat/list types, `XProtocol`, `XrdSfsFlags`, `XrdOucECMsg`, and system `stat` flags. It is used throughout admin, file, directory, and wrapper layers.

Risks: errno mapping choices affect all POSIX semantics and may not match caller expectations, for example `errNotFound` to `EIDRM`. `Entry2Buf()` sets `st_dev=1` to avoid offline translation side effects, which is protocol-coupled. `st_blocks` overcount issue appears here too. `mapError` is declared in the header but not defined/used.

Test signals: exhaustive status-code mapping tests; extended/non-extended stat conversion; directory entry without stat info returns `EIO`; mode-to-access mapping for all permission bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.hh

Purpose: declares the static mapping utilities that convert XRootD client statuses and metadata into POSIX-facing values.

Important APIs/types: `XrdPosixMap::Flags2Mode`, `Entry2Buf`, `Mode2Access`, `Result`, and `SetDebug`.

Control flow: all functions are stateless static helpers except the debug flag. Callers provide protocol objects and receive POSIX return codes, stat fields, access modes, and `errno` side effects.

State and persistence: static `Debug` boolean only.

Dependencies/integration: includes `XrdClFileSystem.hh` and `XrdClXRootDResponses.hh`; forward-declares `XrdOucECMsg` and `struct stat`. Used across the XrdPosix implementation.

Risks: private `mapError(int)` is declared but has no implementation in the researched source, suggesting dead API or historical leftover. Because `Result()` sets global/thread `errno`, tests must isolate side effects.

Test signals: compile/link coverage for all declared functions; direct tests for `SetDebug`; callers expecting `-errno` versus `-1` return modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObjGuard.hh -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObjGuard.hh

Purpose: provides an RAII guard for an `XrdPosixFile` that combines file reference management with the file update mutex.

Important APIs/types: `XrdPosixObjGuard` with constructor, destructor, `Init(XrdPosixFile*)`, and `Release()`.

Control flow: `Init()` releases any currently guarded file, stores the new file, increments its reference count, and locks its update mutex. `Release()` unreferences and unlocks, then clears the pointer. Destructor calls `Release()`.

State and persistence: holds one transient `XrdPosixFile *guardP`. No durable state.

Dependencies/integration: includes `XrdPosixFile.hh`; used where offset/size updates need lifetime and mutex protection together.

Risks: release order is `unRef()` before `updUnLock()`. If unref can delete the object immediately, unlocking afterward would be unsafe; correctness depends on reference/destruction semantics elsewhere. `Init()` does not handle null input. Copying is not disabled, so accidental copies could double-release.

Test signals: guard construction/destruction around mocked file refs/locks; reinitialization to another file; static analysis for copy usage; close/destruction races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObjGuard.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.cc -->
## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.cc

Purpose: implements the shared descriptor-table and object lookup/release machinery for XrdPosix file and directory objects.

Important APIs/functions: `AssignFD`, `Dir`, `File`, `Init`, `Release`, `ReleaseDir`, `ReleaseFile`, and `Shutdown`.

Control flow: `Init()` opens `/dev/null`, raises/reads `RLIMIT_NOFILE`, allocates `myFiles`, and optionally sets a virtual-FD base when `fdnum` is negative. `AssignFD()` either finds a virtual slot or duplicates `/dev/null` to obtain a real FD, then stores `this` in `myFiles` and sets `fdNum`. `File()`/`Dir()` validate descriptor range, fetch the object under global `fdMutex`, downcast through `Who()`, try to acquire object read/write lock with bounded retries, and return the typed object. Release paths remove table entries and close real shadow FDs when used. `Shutdown()` deletes all registered objects.

State and persistence: static in-memory descriptor table, high/last/base/free FD counters, and `/dev/null` FD. No durable state.

Dependencies/integration: uses `XrdSysMutex`, object locks from `XrdPosixObject.hh`, `XrdSysTimer`, POSIX resource limits, and thread-local `ecMsg`. All file/directory wrappers rely on this registry to distinguish XRootD descriptors from native descriptors.

Risks: descriptor shadowing assumes applications do not close shadow FDs behind XrdPosix; detection logs but continues. Lookup can wait up to roughly one minute, then returns `ETIMEDOUT`. `Init()` may raise process FD limits to `maxFD`. Release always unlocks `fdMutex`, so callers must pass `needlk` accurately. Shutdown deletes objects while bypassing delayed close logic.

Test signals: FD assignment in real and virtual modes; stream FD limit behavior; invalid descriptor returns `EBADF`; lookup timeout under held object lock; release/free slot reuse; shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.cc -->
