# Research Group subset-b-007962

This grouped report covers the XRootD POSIX client facade and proxy storage system files assigned to subset-b-007962. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.hh

Purpose: Declares `XrdPosixObject`, the common base and descriptor registry for POSIX-layer file and directory objects. It turns XRootD-backed `XrdPosixFile` and `XrdPosixDir` instances into POSIX-like integer file descriptors, tracks references, and provides locking and error-message storage.

Important APIs/types/functions: `AssignFD()` reserves a descriptor slot, optionally for a stream descriptor. `Init()` sizes the static descriptor table, `Shutdown()` tears it down, `Valid()` identifies descriptors owned by the XRootD POSIX layer, and `Release*()` removes file or directory objects from the registry. `File()` and `Dir()` map descriptors back to typed objects, with optional caller locking behavior. `Who()` is a virtual downcast hook implemented by derived file/dir classes. `ecMsg` stores object-specific extended error state.

Control flow and state: Static state includes `myFiles`, `baseFD`, `highFD`, `lastFD`, `freeFD`, `posxFD`, and `devNull`, protected by `fdMutex`. Per-object state includes `fdNum`, `refCnt`, a recursive update mutex, and an RW lock. The destructor automatically releases an assigned descriptor, so object lifetime is tied tightly to registry cleanup.

Dependencies/integration: Used throughout `XrdPosixXrootd.cc`, preload wrappers, and PSS to distinguish local descriptors from XRootD descriptors. It depends on XrdSys locking and atomics plus `XrdOucECMsg`.

Risks and test signals: Descriptor allocation/release bugs can surface as `EBADF`, descriptor leaks, accidental interception of local descriptors, or delayed-delete races. Tests should cover descriptor-table limits, concurrent `File()/ReleaseFile()`, close during outstanding async I/O, and object-specific `QueryError()` after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixOsDep.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixOsDep.hh

Purpose: Provides standalone platform compatibility definitions for the POSIX preload/client layer. It normalizes 64-bit POSIX names and missing errno values across Solaris, macOS, FreeBSD, GNU/Hurd, and GNU/kFreeBSD without pulling in heavier XRootD platform headers.

Important APIs/types/functions: There are no functions. The header aliases `statfs64`, `dirent64`, `off64_t`, `stat64`, `statvfs64`, and `ELIBACC` where platform libc headers lack those symbols or use different names.

Control flow and state: Compile-time only. The file is included by preload and POSIX headers before symbol wrappers are defined, so macro ordering matters. It intentionally duplicates selected platform logic because it must be usable as a standalone include.

Dependencies/integration: Integrated with `XrdPosixPreload.cc`, `XrdPosixPreload32.cc`, and `XrdPosixXrootd.hh`. The wrappers depend on these aliases so exported `stat64`, `readdir64`, `statvfs64`, and offset APIs compile consistently.

Risks and test signals: Main risk is ABI drift with libc or OS headers. Incorrect aliases can cause wrapper signature mismatches, structure-size corruption, or missing symbols in preload builds. Build tests should cover Linux/glibc, macOS, FreeBSD, Solaris-like branches when available, and musl configurations that explicitly undefine libc redirections in the preload source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixOsDep.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload.cc

Purpose: Exports the LD_PRELOAD/libc interposition layer for the 64-bit POSIX API. Each `extern "C"` function initializes `XrdPosixLinkage` once and forwards intercepted libc-style calls to the XRootD POSIX wrapper functions in `XrdPosixExtern.hh`, or to native libc via `Xunix` in lite mode.

Important APIs/types/functions: The file wraps `access`, `acl`, `chdir`, `close`, `closedir`, `creat64`, `fclose`, `fcntl64`, `fdatasync`, `fflush`, `fopen64`, `fread`, `fseek`, `fseeko64`, `fstat64` or `__fxstat64`, `fstatat64`, `fsync`, `ftell`, `ftello64`, `ftruncate64`, `fwrite`, Linux xattr calls, `lseek64`, `llseek`, `lstat64` or `__lxstat64`, `mkdir`, `open64`, `openat`, `opendir`, `pathconf`, `pread64`, `pwrite64`, `read`, `readv`, `readdir64`, `readdir64_r`, `rename`, directory positioning, `stat64` or `__xstat64`, `statfs64`, `statvfs64`, optional `statx`, `truncate64`, `unlink`, `write`, and `writev`.

Control flow and state: Each wrapper uses a function-local static `Init = Xunix.Init(&Init)` to avoid repeated initialization. `isLite` is initialized from `XRD_POSIX_PRELOAD_LITE`; when true, selected namespace/directory operations bypass the XRootD POSIX layer and call native libc through `Xunix`. The file also adapts Linux versioned stat entry points and platform conditionals.

Dependencies/integration: It is the user-facing preload entrypoint over `XrdPosix_*` C wrappers and `XrdPosixLinkage`. It depends on OS compatibility macros from `XrdPosixOsDep.hh` and musl cleanup of redirected symbol names.

Risks and test signals: Interposition bugs can deadlock during initialization, recurse into wrappers, or mishandle variadic `open/fcntl` arguments. Test signals include preload smoke tests for local and `root://` paths, lite mode behavior, xattr/stat/statfs wrappers, openat/fstatat handling, and musl/glibc versioned symbol builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload32.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload32.cc

Purpose: Supplies 32-bit ABI-compatible preload wrappers and structure conversion helpers when building on environments where 32-bit POSIX entry points coexist with the 64-bit XRootD POSIX implementation. It is guarded by LP64-related conditionals and disables large-file macro remapping for the ABI surface it defines.

Important APIs/types/functions: `XrdPosix_CopyDirent()` converts `dirent64` into `dirent` with overflow detection. `XrdPosix_CopyStat()` converts `stat64` to `stat`, saturating selected fields or returning `EOVERFLOW` for regular files/directories too large for the ABI. Wrappers include `creat`, `fcntl`, `fseeko`, `fstat`/versioned variants, `fstatat`, `ftello`, `ftruncate`, `lseek`, `lstat`, `open`, `pread`, `pwrite`, `readdir`, `readdir_r`, `stat`, `statfs`, `statvfs`, and `truncate`.

Control flow and state: Like the 64-bit preload file, each wrapper initializes `Xunix` once. For path/stat wrappers on Linux and macOS, non-XRootD paths may be passed to native `Xunix` based on `XrdPosix_isMyPath()` or `XrdPosixXrootd::myFD()`. XRootD paths use the 64-bit internal calls and are converted down to ABI structures as needed.

Dependencies/integration: Works with `XrdPosixPreload.cc`, `XrdPosixExtern.hh`, `XrdPosixXrootd.hh`, and platform macros. `XRD_POSIX_PRELOAD_LITE` again influences directory reads.

Risks and test signals: Main risks are overflow handling, wrong structure layout assumptions, and accidental interception of non-XRootD paths. Tests should exercise large file sizes, large inode/offset fields, versioned stat symbols, 32-bit readdir conversion, FreeBSD/Solaris exclusions, and local passthrough for regular files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload32.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.cc

Purpose: Implements deferred-open cache I/O for files whose open is postponed by an `XrdOucCache`. It allows the cache layer to accept a file object before the underlying `XrdCl::File` is opened and then performs the real open lazily on first I/O/stat/control operation.

Important APIs/types/functions: `Disable()` marks the deferred open as shut down using `-ESHUTDOWN`. `Init()` is the core lazy-open routine called by inline methods in `XrdPosixPrepIO.hh`. It locks the backing `XrdPosixFile`, avoids repeated opens, opens `fileP->clFile` with stored `clFlags`/`clMode`, maps open errors through `XrdPosixMap::Result`, updates global POSIX and cache statistics, calls `fileP->Stat(Status)` on success, and tells the cache `fileP->XCio->Update(*fileP)`.

Control flow and state: `openRC` caches the first open failure and prevents retries. `iCalls` tracks unexpected repeated use and logs as a power-of-two threshold grows. All entrypoints in the header call `Init()` before delegating to `XrdPosixFile`, and async variants complete callbacks with `openRC` if the open failed.

Dependencies/integration: Created by `OpenDefer()` in `XrdPosixXrootd.cc` when `theCache->Prepare()` asks for deferral. It integrates with `XrdOucCache`, `XrdOucCacheIOCB`, `XrdPosixObjGuard`, stats, trace, and auth-obfuscated debug logging.

Risks and test signals: Lazy open changes timing of errors and can surprise callers that expect `open()` to fail immediately. Tests should verify cache deferral success, deferred ENOENT/ELOOP behavior, async callback completion on failure, `Disable()` during shutdown, stats increments, and no deadlock while updating the cache I/O object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.hh

Purpose: Declares `XrdPosixPrepIO`, an `XrdOucCacheIO` implementation that fronts a not-yet-opened `XrdPosixFile`. It exposes the cache I/O interface while deferring the real XRootD open until a method needs file metadata or bytes.

Important APIs/types/functions: Inline methods implement `Fcntl`, `FSize`, `Fstat`, `Open`, `Read`, async `Read`, `ReadV`, async `ReadV`, `Sync`, async `Sync`, `Trunc`, `Write`, and async `Write`. Each calls private `Init()` and then delegates to `fileP`, or returns/completes with `openRC` if initialization failed. `Detach()` always returns true. `Path()` forwards to `fileP->Path()`. `Disable()` is implemented in the `.cc`.

Control flow and state: The object stores `fileP`, `openRC`, `iCalls`, and the XRootD open flags/mode needed by lazy open. There is no owned persistence beyond the backing file object; it is a transitional object updated into the real file cache I/O once opening succeeds.

Dependencies/integration: Depends on `XrdOucCacheIO`, `XrdPosixFile`, and XrdCl open flag/access enums. Used by `XrdPosixXrootd::Open()` when cache prepare returns a positive deferral signal.

Risks and test signals: Because most behavior is inline, ABI and include dependencies matter. Tests should cover every forwarded operation both before and after successful lazy open, failure propagation to sync and async APIs, cache detach interactions, and preservation of the original open flags and access mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixStats.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixStats.hh

Purpose: Defines a small thread-safe statistics accumulator for the POSIX facade. It currently tracks open/close counts and errors and is used by the XRootD POSIX client layer and config stats reporting.

Important APIs/types/functions: `PosixStats` contains `Opens`, `OpenErrs`, `Closes`, and `CloseErrs`. `Get()` snapshots counters into another `XrdPosixStats`. `Add()`, `Count()`, and `Set()` update counters under `sMutex`; `Count()` uses XrdSys atomic macros while holding the mutex. `Lock()` and `UnLock()` expose coarse locking for external grouped operations.

Control flow and state: State is process-local and in-memory. Construction zeroes the counter struct with `memset`. There is no persistent storage and no automatic export here; callers must ask for or format stats elsewhere.

Dependencies/integration: `XrdPosixGlobals::Stats` is defined in `XrdPosixXrootd.cc` and incremented during open/deferred-open error paths. PSS exposes stats through `XrdPssSys::Stats()` via `XrdPosixConfig::Stats("pss", ...)`.

Risks and test signals: Counter coverage is limited; increments are easy to miss when new open/close paths are added. Tests should verify concurrent increments, snapshot consistency, stats text output from PSS/POSIX config, and error-path increments for normal open, deferred open, and close failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixTrace.hh

Purpose: Provides debug trace macros for the POSIX layer. It centralizes the debug bit, namespace declaration for `XrdPosixGlobals::Trace`, and no-op behavior under `NODEBUG`.

Important APIs/types/functions: `TRACE_Debug` defines the debug mask. In debug builds, `DMSG`, `DEBUGON`, `DEBUG`, and `EPNAME` wrap `XrdSysTrace` logging. In `NODEBUG`, `DEBUG` and `EPNAME` compile away and `DEBUGON` is false.

Control flow and state: Runtime state is the global `XrdSysTrace Trace` object defined in `XrdPosixXrootd.cc`; its mask is initialized from `XRDPOSIX_DEBUG`. Callers commonly create `EPNAME("Function")` and then guard debug-only string building with `DEBUGON`.

Dependencies/integration: Used by `XrdPosixPrepIO.cc`, `XrdPosixXrootd.cc`, `XrdPosixXrootdPath.cc`, and other POSIX files. PSS has a separate but similar tracing header.

Risks and test signals: Logging macros should not evaluate expensive or unsafe expressions when disabled. Tests are mostly build/runtime smoke signals: debug and `NODEBUG` builds must both compile, `XRDPOSIX_DEBUG` should enable expected trace output, and logs must obfuscate auth data where callers use `obfuscateAuth()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.cc

Purpose: Implements `XrdPosixXrootd`, the central POSIX-style client facade over XrdCl. It maps file, directory, metadata, filesystem, extended-attribute, checksum, and async I/O operations onto XRootD client APIs while preserving POSIX return conventions and errno/error-message behavior.

Important APIs/types/functions: Public methods implement `Access`, `Open`, `Close`, `Opendir`, `Closedir`, `Read`, `Pread`, `Write`, `Pwrite`, `Readv`, `Writev`, `VRead`, `Fstat`, `Stat`, `Statfs`, `Statvfs`, `Fsync`, `Ftruncate`, `Truncate`, `Mkdir`, `Rmdir`, `Rename`, `Unlink`, directory iteration/positioning, `Getxattr`, `QueryChksum`, `QueryOpaque`, `QueryError`, `StatRet`, `endPoint`, `myFD`, and async variants. Private helpers include `Fault()`, `OpenCache()`, and erasure-coding helpers `EcRename`, `EcStat`, and `EcUnlink`.

Control flow and state: Constructor performs one-time static initialization, optional `XRDPOSIX_CONFIG` client config loading, EC detection via `XRDCL_EC`, and descriptor-table initialization. `Open()` translates POSIX flags to XrdCl flags, handles stream descriptors, cache prepare/deferred opens, sync/async XrdCl open, descriptor assignment, and final stat collection. I/O paths look up and lock `XrdPosixFile` objects, enforce `int`-sized XrdCl I/O lengths, delegate through cache I/O (`XCio`), update offsets and size, and map failures through `ecMsg`. Admin operations use `XrdPosixAdmin` and notify cache for namespace mutations. EC helpers deep-locate file replicas and perform special stat/rename/unlink handling.

Dependencies/integration: Depends on XrdCl file/filesystem APIs, `XrdPosixFile`, `XrdPosixDir`, `XrdPosixAdmin`, `XrdPosixMap`, cache interfaces, config, stats, trace, and path translation. It is called by preload C wrappers and by the PSS proxy storage plugin.

Risks and test signals: High-risk areas include descriptor lifetime with async callbacks, cache deferral timing, errno vs negative-return conventions, read/write size overflow, `Writev()` short-write semantics, EC path behavior, and query-response ownership. Tests should cover open/create/truncate flag combinations, cache-hit and cache-miss stat/open behavior, async I/O close races, directory `StatRet`, EC redirector vs server paths, xattr/checksum queries, and preload interposition over local passthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.hh

Purpose: Declares the public static POSIX facade used by preload wrappers, direct clients, and PSS. The class documents the POSIX-like methods and XRootD-specific extensions and owns one-time descriptor-origin initialization through its constructor.

Important APIs/types/functions: The API includes POSIX calls (`Access`, `Close`, `Fstat`, `Fsync`, `Ftruncate`, `Lseek`, `Mkdir`, `Open`, `Opendir`, `Pread`, `Pwrite`, `Read`, `Readv`, `Readdir*`, `Rename`, `Rmdir`, `Stat`, `Statfs`, `Statvfs`, `Truncate`, `Unlink`, `Write`, `Writev`) plus extensions (`endPoint`, async read/write/fsync, `VRead`, `QueryChksum`, `QueryOpaque`, `QueryError`, `Getxattr`, `Fcntl`, `StatRet`, `isXrootdDir`, `myFD`). `isStream` is an internal open flag. `Fcop` currently exposes `QFInfo`.

Control flow and state: Static `baseFD` identifies the descriptor range owned by XRootD POSIX, and `initDone` guards one-time initialization. The constructor’s `maxfd` argument configures descriptor capacity; negative values request absolute max and no shadow descriptors per comments.

Dependencies/integration: Includes POSIX platform headers and `XrdPosixOsDep.hh`. It is the stable contract for `XrdPosixPreload*.cc`, `XrdPosixExtern` wrappers, and XrdPss files.

Risks and test signals: Because this header is a broad ABI/API contract, signature changes affect preload symbols and PSS. Tests should compile direct API users, preload builds, and PSS, and should validate documented extension semantics such as async `Open()` returning `-1`/`EINPROGRESS` while completing with the descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.cc

Purpose: Implements path and URL translation for the POSIX layer. It maps local paths to XRootD URLs using `XROOTD_VMP`, converts supported XRootD URLs back to local/translated logical paths for cache/name2name use, and allows extra protocol prefixes.

Important APIs/types/functions: Constructor parses `XROOTD_VMP` tokens of the form `server:path[=replacement]` into linked `xpath` entries. `AddProto()` registers additional protocol prefixes in the fixed-size `protoTab`. `CWD()` stores a normalized current working directory for relative `./` paths. `P2L()` recognizes supported XRootD protocols, strips URL prefix/path/cgi, optionally appends `?src=` and CGI for N2N translators, invokes `theN2N->pfn2lfn()`, and returns either the original path or allocated replacement. `URL()` maps a path to `root://server/path`, applying CWD and optional replacement path.

Control flow and state: Per-instance state is `xplist`, `pBase`, `cwdPath`, and `cwdPlen`. Global state in `XrdPosixGlobals` includes `protoTab`, `theN2N`, `oidsOK`, `p2lSRC`, and `p2lSGI`. `P2L()` returns allocated memory through `relP` only when translation happened; callers must free it.

Dependencies/integration: Used by POSIX config/path handling and cache mutation paths in `XrdPosixXrootd.cc`. Integrates with `XrdOucName2Name`, `XrdOucTokenizer`, and trace macros.

Risks and test signals: Risks include fixed protocol-table capacity, malformed `XROOTD_VMP` tokens, buffer limits, URL CGI preservation, and object-id/double-slash semantics. Tests should cover protocol registration, VMP replacement, relative CWD paths, N2N success/failure errno propagation, CGI handling, object-id allowance, and auth-obfuscated debug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.hh

Purpose: Declares `XrdPosixXrootPath`, the POSIX-layer path translator. It stores virtual mount mappings and exposes helpers for local-path to URL and URL/path to logical-path conversion.

Important APIs/types/functions: `AddProto()` extends the recognized protocol list. `CWD()` records the current working directory for relative path expansion. Static `P2L()` converts supported XRootD URLs to logical/local paths, optionally returning only the path component. `URL()` converts a local path into a URL using configured virtual mount mappings. Internal `xpath` stores linked-list entries with server, source path, and optional replacement path lengths.

Control flow and state: The constructor builds `xplist` from environment configuration; the destructor frees the linked list. `pBase` owns the mutable copy of the environment string used by entries; `cwdPath` tracks relative path context.

Dependencies/integration: Included by `XrdPosixXrootdPath.cc` and consumers that need mapping declarations. Depends only on `<cstring>` in the header to keep it light.

Risks and test signals: Memory ownership is subtle because `xpath` fields point into `pBase`; destructor currently deletes nodes but the research should verify whether `pBase` and `cwdPath` are freed elsewhere or leak intentionally for process lifetime. Tests should include constructor/destructor under repeated initialization, malformed mapping strings, and `URL()` buffer-length failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootdPath.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdPss/CMakeLists.txt

Purpose: Defines the XrdPss proxy storage system plugin build target. It creates a versioned module library and links it against the POSIX client layer, utility library, and server library.

Important APIs/types/functions: `set(XrdPss XrdPss-${PLUGIN_VERSION})` names the module. `add_library(... MODULE ...)` includes `XrdPss.cc/.hh`, async files, checksum files, config, trace, URL info, and utility sources. `target_link_libraries(${XrdPss} PRIVATE XrdPosix XrdUtils XrdServer)` supplies dependencies. `install(TARGETS ... LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})` installs the plugin.

Control flow and state: Build-system only. It does not configure runtime state but determines which source units are packaged into `libXrdPss` and which symbols/plugins are available.

Dependencies/integration: The target depends directly on `XrdPosix`, so PSS can call `XrdPosixXrootd` and `XrdPosixExtra`. It also requires server-side OSS/OFS/SFS interfaces from `XrdServer` and utility/config support from `XrdUtils`.

Risks and test signals: Omitting a source breaks plugin entrypoints such as `XrdOssGetStorageSystem2` or checksum initialization. Tests should include CMake configure/build, module install path verification, plugin loading by XRootD server, and link checks for PSS config/URL utility symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPss.cc

Purpose: Implements the XRootD Proxy Storage System (PSS) plugin: an `XrdOss` implementation that proxies namespace and file operations to remote XRootD origins through `XrdPosixXrootd`. It also implements proxy file and directory objects, identity mapping hooks, cache-control handling, outgoing proxy URL rewriting, and third-party-copy special cases.

Important APIs/types/functions: `XrdOssGetStorageSystem2()` exports the plugin instance. `XrdPssSys` implements OSS operations including `Init`, `Connect`, `Disc`, `EnvInfo`, `FSctl`, `Lfn2Pfn`, `Mkdir`, `Remdir`, `Rename`, `Stat`, `Stats`, `Truncate`, `Unlink`, `P2DST`, `P2OUT`, `P2URL`, and `Info`. `XrdPssDir` implements `Opendir`, `Readdir`, `StatRet`, `Close`, and error retrieval. `XrdPssFile` implements `Open`, `Close`, sync file I/O, page read/write with checksums, `Fctl`, `Fstat`, `Fsync`, and `Ftruncate`.

Control flow and state: Initialization configures globals, logger/trace, versioning, exported path policy, scheduler/env links, and optional cache FSctl. `P2URL()` is the central path-to-remote URL converter; it applies N2N mapping, origin headers, CGI, generated identities, or outgoing proxy authorization. File open enforces read-only policies, handles `O_DIRECT` as cache I/O hint, checks `only-if-cached`, supports TPC write opens by stashing `tpcPath`, and optionally uses file-cache open handoff. File/directory methods proxy through `XrdPosixXrootd` and store extended error text from `QueryError()`.

Dependencies/integration: Depends on OSS/SFS interfaces, XrdPosix client APIs, XrdPss config/url/util files, XrdNetSecurity, XrdSec entity and sss ID mapping, page read/write utilities, and OFS cache-control plugin interfaces.

Risks and test signals: Risks include mixed errno conventions, read-only/export policy mistakes, unsafe CGI/header URL construction, TPC/reproxy stat fallback behavior, identity mapping lifetime, and cache-control coupling. Tests should run PSS as an OSS plugin against a test origin, covering stat/open/read/write/rename/unlink, exported read-only paths, outgoing proxy authorization, N2N mapping, `only-if-cached`, directory `StatRet`, TPC write-open/fstat/close, and propagated extended errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPss.hh

Purpose: Declares the PSS plugin classes implementing the server-side OSS proxy interface: `XrdPssDir`, `XrdPssFile`, and `XrdPssSys`. It defines the core class contracts used by `XrdPss.cc`, async I/O, checksum, and config files.

Important APIs/types/functions: `XrdPssDir` derives from `XrdOssDF` and provides directory open/read/close/stat-return behavior plus stored error text. `XrdPssFile` derives from `XrdOssDF` and exposes sync/async file I/O, page read/write, file controls, stats, truncate, sync, and open/close. It stores `tprInfo` for TPC reproxy state, `tpcPath`, client `entity`, and last error info. `XrdPssSys` derives from `XrdOss`, constructs file/dir objects, implements namespace operations, config entrypoints, path-to-URL helpers, feature reporting, and static configuration fields.

Control flow and state: Static fields such as `XPList`, `Police`, `ManList`, `fileOrgn`, `protName`, `hdrData`, `Streams`, `Workers`, `Trace`, `dca*`, `xLfn2Pfn`, `deferID`, and `reProxy` are configured elsewhere and consumed by runtime methods. Per-file state tracks open descriptor, TPC/reproxy metadata, identity, and extended error text.

Dependencies/integration: Uses `XrdOss`, `XrdOucCache`, `XrdOucName2Name`, `XrdOucPList`, `XrdSecEntity`, and POSIX facade types. Async methods are implemented in `XrdPssAio.cc`; checksum plugin in `XrdPssCks.*`.

Risks and test signals: Header-level risks are virtual override compatibility and state ownership. Tests should compile against current OSS ABI, verify destructor closes file/dir resources, exercise `getErrMsg()` clearing semantics, and confirm `Features()` advertises only supported capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPss.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAio.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssAio.cc

Purpose: Implements asynchronous file and page I/O methods for `XrdPssFile`. It adapts server-side `XrdSfsAio` requests to the async callback APIs exposed by `XrdPosixXrootd` and `XrdPosixExtra`.

Important APIs/types/functions: `Fsync(XrdSfsAio*)` queues async fsync. `Read(XrdSfsAio*)` and `Write(XrdSfsAio*)` queue async pread/pwrite. `pgRead(XrdSfsAio*, opts)` queues page-read and optionally forces checksum retrieval. `pgWrite(XrdSfsAio*, opts)` optionally verifies caller checksums, calculates or copies CRC vectors, then queues page-write through `XrdPosixExtra::pgWrite()`.

Control flow and state: Each async method allocates an `XrdPssAioCB` bound to the `XrdSfsAio`, read/write direction, and page-read/write mode. For page writes, checksum handling is performed synchronously before queuing so invalid checksums return `-EDOM` immediately. Completion is handled later by the callback object, which writes result fields and invokes done callbacks.

Dependencies/integration: Depends on `XrdPosixXrootd` async methods, `XrdPosixExtra` page I/O, `XrdOucPgrwUtils`, `XrdSfsAio`, and `XrdPssAioCB`.

Risks and test signals: The methods do not check `fd < 0` before queueing, so caller/open-state assumptions are important. Async tests should cover successful read/write/fsync, failed descriptor paths, pgRead checksum copyback, pgWrite verify failure, generated checksum return to caller, callback recycling, and close while operations are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.cc

Purpose: Implements the pooled callback adapter from POSIX async completion to `XrdSfsAio` completion. It lets PSS reuse callback objects and transfer async results and page-read checksum vectors back to server request objects.

Important APIs/types/functions: Static members `myMutex`, `freeCB`, `numFree`, and `maxFree` implement the free list. `Alloc()` pops a callback from the pool or allocates one, initializes `theAIOP`, `isWrite`, and `isPGrw`. `Complete()` maps negative results to `-errno`, copies checksum vectors for successful page reads, calls `doneWrite()` or `doneRead()`, and recycles. `Recycle()` either deletes the callback if the pool is full or pushes it onto the free list after clearing `csVec`.

Control flow and state: A union stores either the active `XrdSfsAio*` or next free-list pointer. Pool mutations are mutex-protected; active completion state is per callback. `maxFree` defaults to 100 and can be set through the header.

Dependencies/integration: Used exclusively by `XrdPssAio.cc` and derives from `XrdPosixCallBackIO`. Completion assumes `errno` still represents the async failure when `result < 0`.

Risks and test signals: Reliance on global `errno` at callback time can be fragile if async providers pass negative errno codes differently. Tests should cover negative completions, checksum copyback, read vs write done callbacks, pool growth/limit behavior, and concurrent callback allocation/recycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.hh

Purpose: Declares `XrdPssAioCB`, the callback adapter used by PSS asynchronous I/O. It bridges `XrdPosixCallBackIO` completions to `XrdSfsAio` server callbacks and provides a small object pool.

Important APIs/types/functions: `Alloc()` creates or reuses a callback for a given `XrdSfsAio`, operation direction, and page-read/write flag. `Complete()` is the virtual callback invoked by POSIX async operations. `Recycle()` returns the object to the pool. `SetMax()` controls maximum cached callbacks. Public `csVec` carries page I/O checksum vectors.

Control flow and state: Static pool state is guarded by `myMutex`. Active state includes a union of `theAIOP`/`next`, booleans `isWrite` and `isPGrw`, and the checksum vector. Constructor/destructor are private to force allocation through `Alloc()`.

Dependencies/integration: Includes `XrdPosixCallBack.hh` and `XrdSysPthread.hh`; forward-declares `XrdSfsAio`. It is owned by async PSS methods.

Risks and test signals: Misuse outside `Alloc()` is prevented, but lifetime correctness depends on every completion calling `Recycle()` exactly once. Tests should include high-concurrency async operations, pool max changes, page checksum vector reuse after recycle, and no use-after-free when callbacks complete after file close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssAioCB.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.cc -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.cc

Purpose: Implements the PSS checksum plugin. It proxies checksum requests to the remote XRootD origin by constructing a PSS URL, issuing `XrdPosixXrootd::QueryChksum()`, and translating the response into `XrdCksData`.

Important APIs/types/functions: `XrdCksInit()` exports a new `XrdPssCks`. Constructor preloads supported algorithms: `adler32`, `crc32`, `md5`, and `crc32c`. `Find()` looks up algorithm metadata. `Get()` builds `cks.type=<name>` CGI, applies `XrdPssSys::P2URL()`, queries checksum and mtime, tokenizes `<name> <value>`, sets `Cks` fields, and returns checksum length. `Init()` can move a supported default algorithm to the front. `Name()` enumerates supported names. `Size()` returns digest length. `Ver()` retrieves and compares checksum data.

Control flow and state: State is a fixed `csTab[8]` and `csLast`. It does not calculate checksums locally; `Calc()` in the header calls `Get()`, and `Set/Del/List` are unsupported or null. `Get()` also uses the caller environment in `Cks.envP` to include identity/CGI handling.

Dependencies/integration: Depends on PSS URL conversion, POSIX checksum query, XrdCks interfaces, tokenization, and trace. Used as a loadable checksum component beside the storage-system plugin.

Risks and test signals: Response parsing is simple and assumes a tokenized checksum response. Tests should cover each supported algorithm, unsupported digest names, remote ENOTSUP/ENOATTR behavior, default algorithm reorder, environment identity propagation, malformed checksum responses, and `Ver()` mismatch and match cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.hh -->
# sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.hh

Purpose: Declares `XrdPssCks`, an `XrdCks` implementation that exposes checksum operations for proxied files. It supports remote retrieval and verification but does not support mutating checksum metadata.

Important APIs/types/functions: `Calc()` delegates to `Get()`. `Get()`, `Init()`, `Name()`, `Size()`, and `Ver()` are implemented in the `.cc`. `Del()` and `Set()` return `-ENOTSUP`; `List()` returns null; `Config()` accepts config lines as a no-op success. Internal `csInfo` stores a checksum algorithm name and byte length.

Control flow and state: `csTab` is a fixed-size table of up to eight supported algorithms, with `csLast` marking the last populated entry. The class uses inherited `XrdCks` error destination for config messages.

Dependencies/integration: Includes `XrdCks` and `XrdCksData`; forward-declares `XrdSysError`. The implementation integrates with PSS URL mapping and `XrdPosixXrootd`.

Risks and test signals: Header behavior signals that local calculation and metadata mutation are intentionally unsupported despite `Calc()` name. Tests should ensure callers handle `-ENOTSUP`, algorithm size reporting is stable, default selection from `Init()` works, and verification does not mutate caller data unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPss/XrdPssCks.hh -->
