# subset-b-007959 Research

Source-tree-aligned grouped research for work item `subset-b-007959`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.cc

## Purpose

`XrdOucUtils.cc` implements a broad set of process, path, parsing, identity, formatting, URL, and filesystem utility routines used throughout XRootD. It is the implementation behind the static `XrdOucUtils` facade and also defines a few free helper functions used by URL/auth sanitization paths.

## Important APIs, Types, And Functions

- Anonymous `idInfo`, `gidMap`, `uidMap`, `AddID()`, and `LookUp()` implement TTL-cached UID/GID name lookup guarded by `XrdSysMutex`.
- `argList()`, `Token()`, `is1of()`, `doIf()`, `parseLib()`, and `parseHome()` support configuration parsing.
- `bin2hex()`, `hex2bin()`, `i2bstr()`, `Log2()`, `Log10()`, `fmtBytes()`, `HSize()`, and `genHumanSize()` provide text/binary/size conversions.
- `getFile()`, `findPgm()`, `getGID()`, `getUID()`, `GidName()`, `UidName()`, `GroupName()`, and `UserName()` wrap common POSIX filesystem and account queries.
- `genPath()`, `makeHome()`, `makePath()`, `mode2mask()`, `ReLink()`, `subLogfn()`, `ValPath()`, `PidFile()`, and `getModificationTime()` manipulate paths and persistent filesystem artifacts.
- `Ident()` and local `genSID()` derive a server identity string and 48-bit fingerprint from host, port, program, instance, site, SHA3, and CRC32C.
- `Undercover()` daemonizes on non-Windows platforms by double-forking, creating a new session, redirecting descriptors to `/dev/null`, and optionally reporting status through a pipe.
- `UrlEncode()`, `UrlDecode()`, `obfuscateAuth()`, `stripCgi()`, and `splitHostCgi()` support HTTP/query-string handling and secret redaction.

## Control Flow

Most functions are independent static utilities. Configuration helpers consume tokens from `XrdOucStream` in place: `doIf()` evaluates host, environment, executable, and instance-name predicates; `parseLib()` reads a plugin path and optional trailing parameters; `parseHome()` validates an absolute home path plus an optional `group` modifier. Filesystem helpers either return negative errno values or emit messages through `XrdSysError`.

Identity generation is lazy-static: `Ident()` initializes `theSID` once through `genSID()`, then formats per-call user/process/site details around that process-global fingerprint. The URL redaction helpers scan strings for CGI or authorization token patterns and rewrite only selected token values, leaving other query content intact.

## State And Persistence

The UID/GID caches are process-global maps with TTL expiration and heap-owned strings. `Ident()` stores static process identity state after first use. `makeHome()`, `makePath()`, `ReLink()`, `PidFile()`, and `Undercover()` persistently affect directories, symlinks, pid files, working directory, process session, and file descriptors. `getFile()` returns a heap buffer that callers must free; `genPath()` and parts of version/path handling also return `strdup()` memory.

## Dependencies And Integration Points

This file depends on POSIX account and filesystem APIs, `XrdNetUtils`, `XrdOucCRC`, `XrdOucSHA3`, `XrdOucStream`, `XrdOucString`, `XrdOucEnv`, `XrdSysError`, `XrdSysE2T`, `XrdSysMutex`, and platform wrappers. It is a shared support layer for config parsers, daemon startup, logging path setup, auth redaction, and path validation in many XRootD components.

## Risks And Edge Cases

- Several APIs mutate input buffers in place (`argList`, `makePath`, `subLogfn`, `Sanitize`) and require caller-owned writable memory.
- `genPath(const char*, const char*, const char*)` uses a fixed 2048-byte stack buffer and unchecked `strcat()` after the initial copy.
- `argList()` supports simple quotes but not escapes; malformed quotes return `-EINVAL`.
- `a UID/GID` cache insertion keeps the first value until TTL expiration and ignores later updates for the same id.
- `touint8_t()` returns `static_cast<unsigned short>` from a `uint8_t` function and does not check for unconsumed trailing characters after `from_chars`.
- `obfuscateAuth()` has a static POSIX regex whose initialization can throw during first use.
- `stripCgi()` removes token-character runs after a key but does not fully parse query separators, so unusual CGI syntax can leave doubled separators.

## Test Signals

Useful tests should cover malformed quoted argument lists, odd-length and invalid hex decoding, `doIf()` branches for host/defined/exec/named predicates, path creation with existing directories and reset mode, UID/GID cache expiry, URL encode/decode round trips, authorization redaction for bearer and `authz=` forms, `stripCgi()` at first/middle/last query positions, daemonization pipe status behavior, and `Ident()` stability for repeated calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.hh

## Purpose

`XrdOucUtils.hh` declares the static `XrdOucUtils` utility facade used by XRootD code for configuration parsing, filesystem setup, identity generation, size formatting, account lookup, URL encoding, and daemon/process helpers.

## Important APIs, Types, And Functions

- `pathMode` is the common directory mode for generated paths.
- Parsing APIs include `argList()`, `doIf()`, `parseLib()`, `parseHome()`, `mode2mask()`, and `Token()`.
- Conversion APIs include `bin2hex()`, `hex2bin()`, `fmtBytes()`, `genHumanSize()`, `HSize()`, `i2bstr()`, `Log2()`, `Log10()`, and `touint8_t()`.
- Filesystem/process APIs include `findPgm()`, `genPath()`, `getFile()`, `makeHome()`, `makePath()`, `ReLink()`, `subLogfn()`, `Undercover()`, `ValPath()`, `PidFile()`, and `getModificationTime()`.
- Account APIs include `getGID()`, `getUID()`, `GidName()`, `GroupName()`, `UidName()`, and `UserName()`.
- URL/text APIs include `Sanitize()`, `toLower()`, `trim()`, `UrlEncode()`, and `UrlDecode()`.

## Control Flow

The header exposes only static methods, so consumers do not need object lifetime management. Most routines return either boolean success, a byte/character count, `0` on success with negative errno-style failure, or a heap pointer on success. The declarations also reveal ownership-sensitive APIs: `genPath()` and `getFile()` return allocated buffers, while many routines require caller-supplied mutable buffers.

## State And Persistence

The header itself has no state, but it declares APIs whose implementation maintains process-global UID/GID caches and generated identity state. Several calls create or validate persistent filesystem objects and can change the process working directory or daemon state.

## Dependencies And Integration Points

The header uses `sys/types.h`, `sys/stat.h`, `string`, `string_view` via declarations, `unordered_set`, `vector`, and `cstdint`, plus forward declarations for `XrdSysError`, `XrdOucString`, and `XrdOucStream`. It is a low-level dependency of configuration, startup, cache, HTTP, and logging code.

## Risks And Edge Cases

- Return conventions are mixed: some functions return negative errno, some positive errno, some `false`, and some null pointers.
- Ownership is not encoded in types for allocated `char*` results.
- Many APIs predate modern C++ string types and expose raw buffers with caller-provided lengths.
- `touint8_t()` can throw exceptions unlike most other utilities, which use error codes or logging.

## Test Signals

Header-level tests are mostly compile and contract tests: include it from C++17 translation units, verify declaration availability for `std::string_view`, check overload resolution for `trim`, and exercise representative APIs for return convention documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.cc

## Purpose

`XrdOucVerName.cc` implements shared-library plugin name versioning. It detects already-versioned plugin paths, recognizes official strict plugin names, and constructs versioned library filenames such as `libXrdFoo-5.so`.

## Important APIs, Types, And Functions

- Anonymous `StrictName[]` is initialized from `XrdVERSIONPLUGINSTRICT` and lists official plugin filenames that require strict version handling.
- `XrdOucVerName::hasVersion()` detects a trailing `-<number>.so` component and optionally returns an unversioned fallback path for official plugin names.
- `XrdOucVerName::isOurs()` strips directory prefixes and tests membership in `StrictName`.
- `XrdOucVerName::Version()` inserts `-<version>` before the filename extension and reports whether fallback is disallowed.

## Control Flow

`hasVersion()` searches the full path for the last dash, parses the following decimal value, and accepts it only when the remaining suffix is `.so`. If a caller asks for an unversioned fallback, it reconstructs the path without the numeric suffix and returns it only when that unversioned name is in the strict official-name table.

`Version()` splits the path into directory, basename, and extension, checks strict-name membership by basename, sets `noFBK`, and formats the versioned result into the supplied buffer.

## State And Persistence

The file has no mutable state and no persistent I/O. It may allocate an alternate path through `strdup()` in `hasVersion()`; the caller owns that memory.

## Dependencies And Integration Points

It depends on `XrdVersionPlugin.hh` for `XrdVERSIONPLUGINSTRICT` and on `XrdOucVerName.hh` for declarations. It integrates with plugin loaders that need ABI-versioned module lookup and fallback behavior.

## Risks And Edge Cases

- Version detection only accepts `.so`, so platform-specific shared-library suffixes are outside this implementation.
- `hasVersion()` uses a fixed 2048-byte stack buffer for fallback construction.
- `Version()` calls `snprintf(buff, blen-1, ...)`, which leaves one byte unused and can behave badly for very small `blen`.
- Only official strict names get unversioned fallback handling; third-party versioned libraries return no alternate path.

## Test Signals

Tests should cover strict official names, non-strict third-party names, paths with multiple dashes, no-extension names, insufficient output buffers, already-versioned `.so` paths, and ownership/freeing of `piNoVN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.hh

## Purpose

`XrdOucVerName.hh` declares a small static helper class for applying and detecting XRootD plugin shared-library version suffixes.

## Important APIs, Types, And Functions

- `hasVersion(const char *piPath, char **piNoVN = 0)` returns an embedded numeric version and optionally an allocated unversioned fallback.
- `Version(const char *piVers, const char *piPath, bool &noFBK, char *buff, int blen)` writes a versioned path into caller storage and reports fallback policy.
- Private `isOurs()` checks whether a basename belongs to the official strict-name table.

## Control Flow

Consumers typically call `Version()` when resolving configured plugin paths against the running XRootD plugin version, and `hasVersion()` to warn or adjust behavior when a user supplied an already-versioned library.

## State And Persistence

The class has no instance state and is not meant to be instantiated. Memory returned through `piNoVN` is heap allocated by the implementation.

## Dependencies And Integration Points

The header is intentionally minimal and avoids pulling in plugin loader headers. It is integrated by shared library loading paths that need versioned module names.

## Risks And Edge Cases

- The API uses raw `char*` ownership and caller-managed buffers.
- `noFBK` is an output policy flag whose meaning is easy to miss: strict official names must load the exact versioned path.
- Documentation contains minor typos, so tests and call-site behavior are the reliable contract.

## Test Signals

Compile tests should confirm the header is standalone. Behavior tests should pair the declarations with implementation cases for official names, third-party names, already-versioned names, and buffer-too-small outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucVerName.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucXAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucXAttr.hh

## Purpose

`XrdOucXAttr.hh` defines a template wrapper around XRootD filesystem extended attributes. It lets callers bind a typed attribute payload object to `Del`, `Get`, and `Set` operations without repeating xattr name, size, and pre/post formatting code.

## Important APIs, Types, And Functions

- The template parameter `T` must provide `Name()`, `sizeGet()`, `sizeSet()`, `postGet(int)`, and `preSet(T&)`.
- `XrdOucXAttr<T>::Attr` is the in-object typed attribute value.
- `Del(const char *Path, int fd = -1)` calls `XrdSysFAttr::Xat->Del()`.
- `Get(const char *Path, int fd = -1)` reads into `Attr` and lets `postGet()` transform or validate the result.
- `Set(const char *Path, int fd = -1)` lets `preSet()` return either `this` or a formatted temporary object before writing.

## Control Flow

The wrapper is thin: callers populate or inspect `Attr`; operations delegate to the active `XrdSysFAttr` implementation with either a path or a file descriptor. `Set()` creates a stack temporary `T xA`, passes it to `Attr.preSet(xA)`, then writes from the returned pointer for `Attr.sizeSet()` bytes.

## State And Persistence

The only instance state is `Attr`. Persistence is external: the actual xattr value is stored on the target filesystem object through the active xattr backend.

## Dependencies And Integration Points

The template depends on `XrdSys/XrdSysFAttr.hh` and the global `XrdSysFAttr::Xat` backend. It is a reusable adapter for code that stores metadata in filesystem xattrs, including cache metadata paths elsewhere in XRootD.

## Risks And Edge Cases

- `XrdSysFAttr::Xat` is dereferenced without a null check.
- Template requirements are documented by comments, not enforced by concepts or traits.
- `preSet()` can return a pointer to invalid storage if implemented incorrectly.
- The API assumes `sizeGet()` and `sizeSet()` match the serialized format of `T`.

## Test Signals

Tests should use a fake `XrdSysFAttr` backend and a sample `T` to verify path and fd forms, `postGet()` return propagation, `preSet()` temporary formatting, delete errors, and behavior when payload sizes differ from object size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucXAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.cc

## Purpose

`XrdOuca2x.cc` implements ASCII-to-value conversion utilities used by configuration parsers. It converts numeric strings, sizes, durations, percentages, ports, file modes, scaled decimals, and hex/binary data while logging consistent configuration errors through `XrdSysError`.

## Important APIs, Types, And Functions

- `a2i()` and `a2ll()` parse signed decimal integers with min/max checks.
- `a2fm()` parses octal file modes and maps user/group/other bits to `S_I*` masks.
- `a2p()` parses numeric ports, service names, and optional `any`.
- `a2sn()` parses scaled decimal values using caller-provided scale.
- `a2sp()` parses storage values or percentages, encoding percentages as negative values.
- `a2sz()` parses byte sizes with `k/m/g/t` binary suffixes.
- `a2tm()` parses durations with `s/m/h/d` suffixes.
- `a2vp()` parses values or percentages, also encoding percentages as negative values.
- `b2x()` and `x2b()` convert between binary bytes and lower-case hex text.
- Private `Emsg()` overloads format bound-check failures.

## Control Flow

Each parser validates presence, calls a C library conversion routine, checks `errno` and trailing characters, applies optional range limits, and returns `0` on success or `-1` on failure after logging. Suffix parsers treat a missing suffix as base units. The port parser uses `XrdNetUtils::ServPort()` for named services.

## State And Persistence

The file has no persistent state. It writes parsed values through caller-provided pointers and emits errors to the supplied `XrdSysError`.

## Dependencies And Integration Points

It depends on `XrdSysError`, POSIX mode bits, and `XrdNetUtils`. It is heavily used by XRootD config parsing, including `XrdPfcConfiguration.cc` for cache watermarks, RAM, block size, prefetch counts, purge intervals, checksum retention, and command test parameters.

## Risks And Edge Cases

- `a2fm()` uses `strtol(item, NULL, 8)`, so trailing non-octal text is not checked.
- `a2sp()` appears to check `if (*val > maxv)` twice; the second branch formats a "less than" error but should likely compare against `minv`.
- Percentage encodings as negative values require every consumer to know the convention.
- `a2tm()` multiplies a `strtoll()` result into an `int*`, so very large values depend on range checks and integer conversion behavior.
- `b2x()` returns `slen*2+1`, including the null terminator, unlike many length APIs.

## Test Signals

Tests should cover valid and invalid suffixes, min/max failures, service-name ports, `any` allowed/disallowed, percentage encoding, decimal scaled parsing, file-mode conversion, malformed octal text, odd-length hex with and without right adjustment, destination buffer too small, and the suspected `a2sp()` minimum-bound bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.hh

## Purpose

`XrdOuca2x.hh` declares the static conversion utility class used by XRootD configuration code to parse human-entered numbers, modes, sizes, ports, times, percentages, and hex/binary strings.

## Important APIs, Types, And Functions

- Public parsers: `a2i`, `a2ll`, `a2fm`, `a2p`, `a2sn`, `a2sp`, `a2sz`, `a2tm`, and `a2vp`.
- Public encoders/decoders: `b2x` and `x2b`.
- Private `Emsg()` overloads centralize formatted error reporting for `double`, `int`, and `long long` bounds.

## Control Flow

The class is a namespace-like holder of static methods. Callers pass a logger, an error-message prefix, source text, output storage, and optional bounds. The implementation logs failures and returns `-1`; successful conversions store through the output pointer and return `0`, except `a2p()` returns the parsed port number or `0` for allowed `any`.

## State And Persistence

The header declares no state and no object instances. All persistence is in caller-owned output variables.

## Dependencies And Integration Points

It includes `XrdSys/XrdSysError.hh` and is a common dependency of server, plugin, and cache configuration parsers.

## Risks And Edge Cases

- Mixed return conventions make `a2p()` different from the other `a2*` routines.
- Percentage values are represented by negative integers/long longs, an implicit API contract.
- The header does not document accepted suffixes; consumers need implementation knowledge or external docs.

## Test Signals

Compile and behavior tests should verify each declaration links to the implementation and that callers handle `a2p()` and negative percentage conventions correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdPfc/CMakeLists.txt

## Purpose

`XrdPfc/CMakeLists.txt` builds and installs the proxy file cache plugin, the blacklist decision plugin, the purge quota plugin, and the `xrdpfc_print` inspection tool.

## Important APIs, Types, And Functions

- Defines module targets `${XrdBlacklistDecision}`, `${XrdPfc}`, and `${XrdPfcPurgeQuota}` with `${PLUGIN_VERSION}` suffixes.
- Builds `${XrdPfc}` from core cache, configuration, command, directory-state, purge, file, IO, info, traversal, and resource monitor sources.
- Installs public PFC headers under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd/XrdPfc`.
- Links `${XrdPfc}` with `XrdCl`, `XrdUtils`, `XrdServer`, and `XrdPosix`.
- Installs a compatibility symlink from `libXrdFileCache.so` to the versioned `libXrdPfc` module.
- Builds `xrdpfc_print` from info/print sources for reading cache metadata.

## Control Flow

The build file declares plugins first, then install rules for headers and libraries, then a post-install symlink action, then the standalone print executable. Source list membership controls what participates in the runtime cache module.

## State And Persistence

CMake produces installed shared libraries, headers, the compatibility symlink, and the `xrdpfc_print` binary. No runtime state is affected directly.

## Dependencies And Integration Points

The target integrates XrdPfc into the XRootD plugin system through module libraries and exported headers. The symlink preserves older `XrdFileCache` naming for deployments or configs that still use it.

## Risks And Edge Cases

- The install-time `ln -sf` assumes a Unix-like environment and a library name prefix of `lib`.
- Public header installation must stay aligned with headers included by external purge/decision tooling.
- Adding source files without updating this list can silently omit implementation from the plugin module.

## Test Signals

Build tests should verify all three modules build, `xrdpfc_print` links, headers install, and the compatibility symlink points to the versioned PFC module in staged installs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.cc

## Purpose

`XrdPfc.cc` implements the main proxy file cache plugin entry point and the runtime `XrdPfc::Cache` object. It decides whether to wrap remote IO, manages active cached files, write-back queues, RAM buffers, prefetch scheduling, cache metadata/xattrs, local-file-path lookup, deferred opens, stat/only-if-cached behavior, unlink/eviction, and HTTP cache-control validation.

## Important APIs, Types, And Functions

- `XrdOucGetCache()` is the exported plugin factory. It obtains or creates a scheduler, creates/configures the singleton cache, starts resource monitor/write/prefetch threads, registers `XrdPfcFSctl`, and returns `XrdOucCache*`.
- Singleton APIs: `CreateInstance()`, `GetInstance()`, `TheOne()`, `Conf()`, and `ResMon()`.
- IO APIs: `Attach()`, `Prepare()`, `Stat()`, `LocalFilePath()`, `ConsiderCached()`, and `Unlink()`.
- Active-file APIs: `GetFile()`, `ReleaseFile()`, `inc_ref_cnt()`, `dec_ref_cnt()`, `schedule_file_sync()`, and `FileSyncDone()`.
- Write queue APIs: `AddWriteTask()`, `RemoveWriteQEntriesFor()`, `ProcessWriteTasks()`, and `WritesSinceLastCall()`.
- RAM APIs: `RequestRAM()` and `ReleaseRAM()` maintain an allocation budget and reusable standard-size block list.
- Prefetch APIs: `RegisterPrefetchFile()`, `DeRegisterPrefetchFile()`, `GetNextFileToPrefetch()`, and `Prefetch()`.
- Metadata APIs: `WriteCacheControlXAttr()`, `WriteFileSizeXAttr()`, `DetermineFullFileSize()`, `GetCacheControlXAttr()`, `DecideIfConsideredCached()`, and `is_http_cache_valid()`.

## Control Flow

Startup enters through `XrdOucGetCache()`: config is parsed before background threads are launched. `Attach()` passes through writes unless write-through is enabled, asks configured decision plugins whether the logical filename should be cached, and wraps eligible reads in `IOFile` or block-mode IO. If a local file cannot be opened, it falls back to the original remote IO.

Read paths use `GetFile()` to serialize creation of one `File` per local path. The active map stores `nullptr` while an open is in progress so other attachers wait. Refcount drops go through `dec_ref_cnt()`; the last reference may schedule a final sync, close the file, remove it from `m_active`, emit a g-stream `file_close` JSON record, and delete the `File`.

`Prepare()` implements deferred open by returning `1` when a `.cinfo` metadata file exists. It also intercepts `/xrdpfc_command/` URLs by scheduling a command job and returning `-EAGAIN`. `LocalFilePath()`, `Stat()`, and `ConsiderCached()` read active `File` state or on-disk `.cinfo` metadata to determine completeness and only-if-cached status. `UnlinkFile()` coordinates active-file emergency shutdown or protected placeholder insertion, removes queued blocks, unlinks data plus `.cinfo`, updates resource monitor purge accounting, and broadcasts active-map changes.

## State And Persistence

Runtime state includes the singleton pointer, scheduler pointer, config, OSS handle, trace/log objects, decision plugins, purge plugin, resource monitor, active file map, purge-delay set, write queue, RAM block pool, and prefetch list. Persistent state is the cache data file, `.cinfo` metadata file, xattrs `pfc.cache-control` and `pfc.fsize`, chmod changes for direct local access, and resource-monitor accounting.

## Dependencies And Integration Points

The file integrates with `XrdOucCache`, `XrdOucCacheIO`, `XrdOucEnv`, `XrdOss`, `XrdScheduler`, `XrdSysThread`, `XrdSysXAttr`, `XrdXrootdGStream`, `XrdCl::URL`, `XrdPosixExtra::FSctl`, `XrdPfcFile`, `XrdPfcInfo`, `XrdPfcIOFile`, `XrdPfcIOFileBlock`, `XrdPfcResourceMonitor`, and `XrdPfcFSctl`. It exports the plugin symbol consumed by XRootD configuration.

## Risks And Edge Cases

- Background write, prefetch, and resource monitor loops run indefinitely and depend on process shutdown for termination.
- `RequestRAM()` increments `m_RAM_used` before `posix_memalign()`; allocation failure returns null without rolling back the budget.
- `GetFile()` sets `errno = res` for negative `Fstat()` values, likely mixing negative errno with positive `errno`.
- `is_http_cache_valid()` parses xattr JSON without local exception handling; malformed xattrs can throw.
- `LocalFilePath()` keeps purge protection by inserting paths into `m_purge_delay_set`; cleanup depends on `ClearPurgeProtectedSet()`.
- `UnlinkFile()` returns `std::min(f_ret, i_ret)`, so mixed success/failure semantics depend on XrdOss return ordering.

## Test Signals

Tests should cover plugin startup without scheduler, decision pass/deny paths, fallback when local file open fails, active-map waiting for concurrent opens, write queue removal during emergency unlink, RAM budget rollback on allocation failure, deferred `Prepare()` with and without `.cinfo`, `LocalFilePath()` completeness and chmod behavior, only-if-cached thresholds, xattr fallback to `.cinfo`, HTTP cache-control revalidation, FSctl eviction integration, and g-stream close record insertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.hh

## Purpose

`XrdPfc.hh` declares the proxy file cache configuration model and the central `XrdPfc::Cache` class that implements the `XrdOucCache` plugin interface.

## Important APIs, Types, And Functions

- `MutexHolder` is a small RAII locker for XRootD-style mutexes.
- `Configuration` stores all cache tunables: write-through, HDFS mode, command URLs, spaces, disk/file watermarks, purge intervals, directory stats, block size, RAM, write queue, prefetch, checksum policy, only-if-cached thresholds, HTTP cache-control, and QFS redirection.
- `TmpConfiguration` stores raw config strings that require OSS capacity before conversion.
- `Cache` inherits `XrdOucCache` and declares overrides for `Attach`, `LocalFilePath`, `Prepare`, `Stat`, `Unlink`, and `ConsiderCached`.
- The class exposes cache internals needed by file IO, resource monitor, purge, and FSctl code: `GetFile`, `ReleaseFile`, write queue management, RAM management, prefetch registration, active/purge protection, metadata xattr helpers, and command execution.

## Control Flow

The header defines the public contract used by XRootD core and by other XrdPfc components. Configuration is parsed through `Config()` and private directive helpers; runtime IO enters through `Attach()` and related `XrdOucCache` virtual methods. Other PFC classes use `GetInstance()`/`Conf()` to access process-global cache state.

## State And Persistence

The declaration shows major mutable state: singleton `m_instance`, scheduler pointer, environment/logger/trace, OSS instance, g-stream pointer, resource monitor, plugin vectors, purge pin, configuration, prefetch condition/list, RAM accounting, active map, purge-delay set, and write queue. Persistent effects happen through the OSS and metadata helpers declared here.

## Dependencies And Integration Points

It depends on XRootD scheduler, threading, cache, callback, URL, PFC file, and decision headers. It is included by most XrdPfc implementation files and by code that needs cache plugin types.

## Risks And Edge Cases

- The singleton design assumes one cache instance per process.
- Many shared structures are manually protected by `XrdSysCondVar`/`XrdSysMutex`; correct lock ownership is a cross-file contract.
- Private config parser helpers are exposed only through the header, so test code may need friend-like access or integration tests.
- `Configuration::is_purge_plugin_set_up()` currently always returns false despite `m_purge_pin` support in `Cache`.

## Test Signals

Compile tests should ensure external consumers can include installed headers. Runtime tests should validate default `Configuration` values, checksum helper predicates, singleton lifecycle, cache virtual method dispatch, and thread-safety assumptions around active map and write queue via integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcAllowDecision.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcAllowDecision.cc

## Purpose

`XrdPfcAllowDecision.cc` implements the simplest decision plugin for XrdPfc: every path is allowed to be cached.

## Important APIs, Types, And Functions

- `AllowDecision` derives from `XrdPfc::Decision`.
- `Decide(std::string&, XrdOss&) const` always returns `true`.
- Exported `XrdPfcGetDecision(XrdSysError&)` creates a new `AllowDecision`.

## Control Flow

When configured as a decision library, `Cache::xdlib()` resolves `XrdPfcGetDecision`, stores the returned object, and later `Cache::Decide()` invokes `Decide()` for each candidate file. This plugin never rejects.

## State And Persistence

The plugin has no state and does not touch persistent storage.

## Dependencies And Integration Points

It depends on `XrdPfcDecision.hh` and `XrdSysError`. It is loaded dynamically through `XrdOucPinLoader` using the fixed exported symbol.

## Risks And Edge Cases

- This plugin provides no filtering and is mainly useful as an example or explicit allow-all policy.
- The `Decide` signature uses non-const `std::string&`, differing from the base declaration's const reference in the header; it still compiles here only if the effective declaration matches through permissive overload behavior would be risky. In this source, `virtual bool Decide(std::string &, XrdOss &) const` should be checked against the base `const std::string&` contract.

## Test Signals

Tests should load the module, resolve `XrdPfcGetDecision`, call `ConfigDecision()` through the base default, and verify `Decide()` returns true for arbitrary paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcAllowDecision.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcBlacklistDecision.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcBlacklistDecision.cc

## Purpose

`XrdPfcBlacklistDecision.cc` implements a dynamic decision plugin that permits caching unless the logical filename matches one of the configured blacklist glob patterns.

## Important APIs, Types, And Functions

- `BlacklistDecision` derives from `XrdPfc::Decision`.
- `ConfigDecision(const char *parms)` treats `parms` as a blacklist file path, reads nonblank trimmed lines, and stores them in `m_blacklist`.
- `Decide(const std::string &lfn, XrdOss&) const` rejects paths where `fnmatch(pattern, lfn, FNM_PATHNAME)` succeeds.
- Exported `XrdPfcGetDecision(XrdSysError&)` returns a new `BlacklistDecision`.

## Control Flow

Configuration loading opens and parses the blacklist file at plugin setup time. Runtime decisions iterate the vector in file order and return false on the first match; otherwise they allow caching.

## State And Persistence

The plugin stores blacklist patterns in memory and logs configuration details. It reads but does not write the blacklist file.

## Dependencies And Integration Points

It depends on `XrdPfcDecision.hh`, `XrdSysError`, `fnmatch`, `stdio`, and `errno`. It integrates through `Cache::xdlib()` and the `XrdPfcGetDecision` symbol.

## Risks And Edge Cases

- Lines with leading whitespace are trimmed, but trailing spaces other than newline are kept as part of the pattern.
- Comment syntax is not supported; a line beginning with `#` becomes a real pattern.
- Parse errors after partial reads are logged but `ConfigDecision()` still returns true.
- Large blacklist files are stored entirely in memory and checked linearly per attach.

## Test Signals

Tests should cover missing parameter, unreadable file, blank and whitespace-only lines, newline trimming, `FNM_PATHNAME` behavior across slashes, first-match rejection, no-match allow, and parse-error logging behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcBlacklistDecision.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcCommand.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcCommand.cc

## Purpose

`XrdPfcCommand.cc` implements internal `/xrdpfc_command/...` URLs used to create or remove cache files for testing, maintenance, and purge validation.

## Important APIs, Types, And Functions

- `Cache::ExecuteCommandUrl()` is the command dispatcher.
- `SplitParser` tokenizes command URL path components.
- `create_file` supports options `-h`, `-s filesize`, `-b blocksize`, `-t access_time`, and `-d access_duration`.
- `remove_file` supports `-h` and removes a cache file through `UnlinkFile(..., true)`.
- The create path uses `Info` metadata, `XrdOss` create/open calls, `posix_fallocate()`, resource monitor registration, and write-queue accounting.

## Control Flow

`Cache::Prepare()` schedules a `CommandExecutor` job for command URLs. The executor calls `ExecuteCommandUrl()`, which requires the first token to be `xrdpfc_command`, then dispatches on the command token. `create_file` parses an option subfield, validates size and block size with `XrdOuca2x`, creates data and `.cinfo` files, preallocates the data file, marks all blocks synced in `Info`, writes synthetic access records, adjusts metadata mtime, and registers synthetic resource-monitor stats. `remove_file` parses options and calls `UnlinkFile()` with `fail_if_open=true`.

## State And Persistence

`create_file` persistently creates data and `.cinfo` files in configured OSS data/meta spaces and writes cache metadata. It also mutates write-queue and resource monitor accounting. `remove_file` persistently unlinks cache data and metadata if the file is not open.

## Dependencies And Integration Points

It depends on `XrdPfcInfo`, `XrdPfcPathParseTools`, `XrdPfcResourceMonitor`, `XrdOfsConfigPI`, `XrdOss`, `XrdOuca2x`, `XrdOucEnv`, `XrdOucStream`, and fallocate/time APIs. It is reachable only when `pfc.allow_xrdpfc_command` is enabled.

## Risks And Edge Cases

- Command URLs can create large files up to 32 GiB; enabling the feature in production is risky.
- `access_time` and `access_duration` arrays have fixed `MAX_ACCESSES` length, but repeated `-t`/`-d` parsing does not visibly guard overflow.
- Error cleanup is partial: failures after data-file creation may leave stale files.
- The command interface relies on path token formatting with placeholder spaces between separators.
- The example Python script is embedded in a block comment and is Python 2 style.

## Test Signals

Tests should cover disabled command handling in `Prepare()`, malformed command URLs, help options, missing path/options, size/block bounds, mismatched access time/duration counts, repeated access records, refusal to overwrite existing `.cinfo`, cleanup on intermediate failures, resource monitor updates, and `remove_file` behavior for open and closed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcCommand.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcConfiguration.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcConfiguration.cc

## Purpose

`XrdPfcConfiguration.cc` implements configuration parsing and startup validation for the proxy file cache plugin. It defines defaults, parses `pfc.*` directives, loads OSS/decision/purge plugins, checks filesystem spaces and xattr support, derives watermarks from capacity, and publishes effective settings to the environment and logs.

## Important APIs, Types, And Functions

- `XrdVERSIONINFO(XrdOucGetCache, XrdPfc)` exposes plugin version metadata.
- `Configuration::Configuration()` sets default cache policy values.
- `cfg2bytes()`, `blocksize_str2value()`, and `prefetch_str2value()` convert config strings.
- Directive parsers include `xcschk()`, `xdlib()`, `xplib()`, `xtrace()`, and `ConfigParameters()`.
- `test_oss_basics_and_features()` probes data/meta spaces by creating, opening, writing, xattr-setting, xattr-reading, and unlinking test files.
- `Cache::Config()` orchestrates full parsing, OSS loading, capacity validation, derived settings, resource monitor creation, and g-stream lookup.

## Control Flow

`Config()` opens the config file, creates an `XrdOucStream`, captures `pfc` directives, and uses `XrdOfsConfigPI` to parse/load the OSS plugin. It loops through `pfc.*` directives: known plugin/trace/checksum directives use dedicated parsers, while most tunables go through `ConfigParameters()`. After parsing, it sets `oss.runmode=pfc`, optionally inserts `libXrdOssCsi.so` for cache checksum checking, loads the OSS, restores run mode, probes spaces, computes watermarks using `StatVS`, parses flush and RAM defaults, logs the effective config, exports `XRDPFC.SEGSIZE`, enables prefetch when configured, records the g-stream pointer, and initializes `ResourceMonitor`.

## State And Persistence

The function mutates `m_configuration`, `m_trace->What`, `m_decisionpoints`, `m_purge_pin`, `m_oss`, xattr feature flags, `m_prefetch_enabled`, `Info::s_maxNumAccess`, `m_gstream`, and `m_res_mon`. It exports environment values `XRDPFC` and `XRDPFC.SEGSIZE`, sets `psx.CSNet`, and creates/removes probe files in configured OSS spaces.

## Dependencies And Integration Points

It integrates with `XrdOfsConfigPI`, `XrdOucStream`, `XrdOucPinLoader`, `XrdOuca2x`, `XrdOucUtils`, `XrdOss`, `XrdSysXAttr`, `XrdPfcInfo`, `XrdPfcResourceMonitor`, and purge/decision plugin symbols. It is called by `XrdOucGetCache()` before worker threads start.

## Risks And Edge Cases

- `xdlib()` and `xplib()` ignore a false return from plugin `ConfigDecision()`/`ConfigPurgePin()`.
- `test_oss_basics_and_features()` has early returns that can leak opened `XrdOssDF` objects on some failure branches.
- Some config errors log without returning false, for example unknown subdirectives in parts of `diskusage` or `onlyifcached`.
- `pfc.hdfsmode` returns false as unsupported after unreachable assignment code.
- `pfc.httpcc` calls `strcmp(val, ...)` without checking a missing value.
- Directory stats parsing prints to stdout in addition to logging.

## Test Signals

Tests should cover default config, client-mode defaults, every directive, bad units and bounds, disk/file watermark ordering, separate data/meta spaces, OSS load failure, xattr supported/unsupported probes, checksum/TLS environment export, decision and purge plugin load/config failure, effective log content, HTTP cache-control toggles, qfsredir toggles, and malformed missing-argument cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcConfiguration.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDecision.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDecision.hh

## Purpose

`XrdPfcDecision.hh` declares the plugin interface used by XrdPfc to decide whether a source file should be cached.

## Important APIs, Types, And Functions

- `XrdPfc::Decision` is an abstract base class with a virtual destructor.
- `Decide(const std::string&, XrdOss&) const` is the required runtime policy method.
- `ConfigDecision(const char *params)` is an optional configuration hook with a default success implementation.

## Control Flow

`Cache::xdlib()` loads a shared object, resolves `XrdPfcGetDecision`, constructs a `Decision`, optionally calls `ConfigDecision()`, and stores it. `Cache::Decide()` then requires every configured decision object to return true before wrapping an IO in the cache.

## State And Persistence

The base class has no state. Implementations may store policy data and may inspect the `XrdOss` namespace during decisions.

## Dependencies And Integration Points

It forward-declares `XrdOss` and `XrdSysError` and includes `string`. External plugins must export `XrdPfcGetDecision(XrdSysError&)` returning a `Decision*`.

## Risks And Edge Cases

- The loader currently does not reject a plugin whose `ConfigDecision()` returns false.
- Runtime decisions are synchronous on the attach path, so slow policy checks can delay file opens.
- The interface returns only boolean allow/deny, with no reason code for diagnostics.

## Test Signals

Tests should verify ABI-compatible plugin loading, default `ConfigDecision()` behavior, multiple decision plugins combining by logical AND, and handling of null plugin pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDecision.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.cc

## Purpose

`XrdPfcDirState.cc` implements the in-memory directory tree used by XrdPfc resource monitoring to track per-directory cache usage and IO statistics, propagate child usage upward, remove empty leaf directories, reset interval counters, and dump diagnostic views.

## Important APIs, Types, And Functions

- `DirState` constructors create root or child nodes with parent/depth metadata.
- `create_child()`, `find_path_tok()`, `find_path()`, and `find_dir()` manage tree lookup and optional creation.
- `generate_dir_path()` reconstructs an absolute path from parent links.
- `upward_propagate_initial_scan_usages()` folds initial child usage into parent recursive usage.
- `update_stats_and_usages()` recursively accumulates stats, updates usage counters, and optionally unlinks/erases empty leaf directories.
- `reset_stats()`, `reset_sshot_stats()`, `count_dirs_to_level()`, and `dump_recursively()` support resource monitor intervals and diagnostics.
- `DataFsState` wrappers drive root-level update, reset, and dump operations with timestamps.

## Control Flow

Path lookup tokenizes a path with `PathTokenizer`, descends one component at a time, and optionally creates missing nodes. Updates run post-order: children update first, then parent recursive stats/usages are accumulated. Empty directory purge only removes leaf nodes whose current stats/usages indicate no files or subdirectories and whose unlink callback succeeds.

## State And Persistence

`DirState` stores current interval stats, recursive subdir stats, current usage, recursive usage, snapshot stats, parent pointer, child map, depth, and scan status. Persistent effects are indirect: `update_stats_and_usages()` can call an injected unlink function to remove empty directories from the underlying namespace.

## Dependencies And Integration Points

It depends on `XrdPfcDirState.hh`, `XrdPfcPathParseTools.hh`, `DirStats`, and `DirUsage`. It is used by `XrdPfcResourceMonitor` and snapshot/purge representations.

## Risks And Edge Cases

- Recursive traversal over deep directory trees can be expensive and stack-heavy.
- `generate_dir_path()` relies on parent links and root naming assumptions; root returns an empty prefix.
- Empty-directory purge intentionally removes only one level at a time, so repeated updates may be needed.
- Stats reset and update ordering must be coordinated by the resource monitor lock discipline.

## Test Signals

Tests should cover path creation, max-depth tokenization, last-existing-dir reporting, initial scan propagation, update propagation, empty leaf unlink success/failure, snapshot stats reset, counting by depth, and generated paths for root and nested directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.hh

## Purpose

`XrdPfcDirState.hh` declares the in-memory tree form of XrdPfc directory usage/statistics state and the `DataFsState` root manager.

## Important APIs, Types, And Functions

- `unlink_func` abstracts directory removal callbacks.
- Forward declarations link tree state with snapshot (`DirStateElement`, `DataFsSnapshot`) and purge (`DirPurgeElement`, `DataFsPurgeshot`) vector forms.
- `DirState` extends `DirStateBase` with here/recursive stats and usage, snapshot stats, parent pointer, child map, depth, and scanned flag.
- `DataFsState` extends `DataFsStateBase` with root node and stat reset timestamps.

## Control Flow

Resource monitor code finds or creates `DirState` nodes by LFN, records deltas in the relevant stats/usage fields, periodically calls `DataFsState::update_stats_and_usages()`, and resets interval or snapshot counters after reporting.

## State And Persistence

The header declares all in-memory directory state. Persistence occurs only when consumers export snapshots or when the update routine calls a supplied unlink function.

## Dependencies And Integration Points

It depends on `XrdPfcStats.hh`, `XrdPfcDirStateBase.hh`, `ctime`, `functional`, `map`, and `string`. `XrdPfcResourceMonitor` is the main integration point.

## Risks And Edge Cases

- Tree nodes are stored by value in `std::map`, so pointers to nodes remain stable only under map semantics and while nodes are not erased.
- Parent raw pointers require careful construction and no copying outside map-managed use.
- `m_scanned` state is public and cross-component code must update it consistently.

## Test Signals

Tests should validate declarations via resource monitor integration, pointer stability across child insertions, erase behavior during empty purge, and timestamp reset behavior on `DataFsState`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateBase.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateBase.hh

## Purpose

`XrdPfcDirStateBase.hh` defines shared data structures used by both live directory-state trees and flattened snapshot/purge representations.

## Important APIs, Types, And Functions

- `DirUsage` stores last open/close times, disk blocks, open file count, file count, and directory count.
- `DirUsage(const DirUsage&, const DirUsage&)` combines two usage records.
- `DirUsage::update_from_stats()` applies `DirStats` deltas to usage totals.
- `DirUsage::update_last_times()` keeps maximum last-open and last-close timestamps.
- `DirStateBase` stores a directory name.
- `DataFsStateBase` stores filesystem-level usage update time and data/meta capacity/usage fields.

## Control Flow

Live tree code updates `DirUsage` from interval `DirStats`; snapshot and purge structs inherit the same base fields so they can represent equivalent usage without depending on live tree pointers.

## State And Persistence

All fields are plain in-memory counters/timestamps. Snapshot code serializes these fields to JSON, but this header does not perform I/O.

## Dependencies And Integration Points

It includes `XrdPfcStats.hh` and standard `ctime`/`string`. It is included by `XrdPfcDirState.hh`, `XrdPfcDirStateSnapshot.hh`, and `XrdPfcDirStatePurgeshot.hh`.

## Risks And Edge Cases

- Usage updates can go negative if stats deltas are unbalanced.
- `m_StBlocks` is in filesystem blocks, while other code often converts by multiplying by 512; unit consistency matters.
- Combining usage records sums file counts but takes maximum timestamps, which is correct for recency but not for historical distributions.

## Test Signals

Tests should cover `update_from_stats()` for create/remove/open/close/block deltas, combined constructor totals, timestamp max behavior, and serialization compatibility through snapshot code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateBase.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStatePurgeshot.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStatePurgeshot.hh

## Purpose

`XrdPfcDirStatePurgeshot.hh` declares the flattened directory-usage view used by purge logic to make path-based usage queries without traversing the live `DirState` tree.

## Important APIs, Types, And Functions

- `DirPurgeElement` extends `DirStateBase` with combined `DirUsage`, parent index, and daughter index range.
- `DataFsPurgeshot` extends `DataFsStateBase` with purge target bytes, estimated write-queue writes, purge mode flags, and `m_dir_vec`.
- `find_dir_entry_from_tok()`, `find_dir_entry_for_dir_path()`, and `find_dir_usage_for_dir_path()` locate directory usage by path.

## Control Flow

The vector form represents a tree with contiguous daughter ranges. Path lookup tokenizes an absolute directory path, starts at root index 0, scans the current node's daughter range for each component, and returns either the matching entry or `-1`.

## State And Persistence

The structures are in-memory snapshots. They do not own live tree pointers and do not perform persistence. They carry purge intent fields such as bytes to remove and age/space mode flags.

## Dependencies And Integration Points

It depends on `XrdPfcDirStateBase.hh` and `XrdPfcPathParseTools.hh`. Resource monitor or purge code constructs it from live state; purge policy code can query it by directory.

## Risks And Edge Cases

- Lookup assumes `m_dir_vec[0]` exists and daughter ranges are valid.
- Daughter search is linear within each directory.
- `last_existing_entry` is only set on a failed component, not updated for successful descent at each level.

## Test Signals

Tests should build small vector trees and verify root lookup, nested lookup, missing paths, last-existing behavior, usage pointer return/null return, and malformed empty-vector handling if callers can provide it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStatePurgeshot.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.cc

## Purpose

`XrdPfcDirStateSnapshot.cc` serializes flattened directory-state snapshots to JSON and writes them into the cache namespace as complete cache-managed files.

## Important APIs, Types, And Functions

- `PFC_DEFINE_TYPE_NON_INTRUSIVE` extends nlohmann JSON macros for both `json` and `ordered_json`.
- JSON serializers are defined for `DirStats`, `DirUsage`, `DirStateElement`, and `DataFsSnapshot`.
- `DataFsSnapshot::write_json_file()` writes snapshot JSON data and a synced `.cinfo` metadata file through `XrdOss`.
- `DataFsSnapshot::dump()` prints the ordered JSON representation to stdout.

## Control Flow

`write_json_file()` creates the target file in the configured data space, opens it, optionally wraps the snapshot under a `dirstate_snapshot` preamble, serializes ordered JSON, truncates and writes the data, then creates and writes the `.cinfo` file with all bits marked synced. `dump()` performs only in-memory serialization and stdout output.

## State And Persistence

The function persistently writes a JSON snapshot file and a corresponding `.cinfo` metadata file in the cache namespace. It uses configuration-derived user and space values and fixed advisory sizes/modes.

## Dependencies And Integration Points

It depends on `XrdPfcDirStateSnapshot.hh`, `XrdPfcPathParseTools`, `XrdPfc.hh`, `XrdPfcTrace`, `XrdOucJson`, `XrdOucEnv`, `XrdOss`, and `XrdPfcInfo`. It is used by resource monitor directory-stat reporting.

## Risks And Edge Cases

- Error handling is logging-only; callers do not receive success/failure.
- There are suspicious cleanup calls: after a failed `.cinfo` create/open, code references `myFile` after it has already been closed/deleted in the data-file phase.
- Writes do not check return length from `myFile->Write()`.
- JSON serialization can throw, and this function does not catch exceptions.
- The output mode is `0644`, making snapshots world-readable depending on OSS semantics.

## Test Signals

Tests should cover JSON field names/order, preamble on/off, OSS create/open/write failures for data and `.cinfo`, write-length failures, `.cinfo` completeness via `Info`, dump output, and exception behavior for serialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.hh

## Purpose

`XrdPfcDirStateSnapshot.hh` declares flattened JSON-exportable directory state structures for XrdPfc resource monitor snapshots.

## Important APIs, Types, And Functions

- `DirStateElement` extends `DirStateBase` with snapshot `DirStats`, combined `DirUsage`, parent index, and daughter index range.
- `DataFsSnapshot` extends `DataFsStateBase` with `m_dir_states` and `m_sshot_stats_reset_time`.
- `write_json_file()` persists a snapshot through `XrdOss`.
- `dump()` prints the snapshot as JSON.

## Control Flow

Resource monitor code converts live `DirState` trees into `DataFsSnapshot` vectors. This header keeps the flattened representation independent from live child maps, while the implementation handles serialization and cache-file writing.

## State And Persistence

The structures hold snapshot data in memory. `write_json_file()` persists it as a data file plus `.cinfo`.

## Dependencies And Integration Points

It includes `XrdPfcDirState.hh` and `vector`, and forward-declares `XrdOss`. It bridges resource monitor state to on-disk JSON reporting.

## Risks And Edge Cases

- Parent/daughter indices must be built consistently by external conversion code.
- Snapshot stats use `m_sshot_stats`, so callers must reset snapshot stats at the right time to avoid duplicate reporting.
- The representation does not validate tree consistency.

## Test Signals

Tests should validate construction from `DirState`, vector parent/daughter consistency, serialized field coverage through the implementation, and reset timestamp propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirStateSnapshot.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.cc

## Purpose

`XrdPfcFPurgeState.cc` implements file-level purge candidate discovery for XrdPfc. It traverses the cache namespace, identifies data files with matching `.cinfo` metadata, and keeps enough oldest or age-expired files to satisfy a requested purge size.

## Important APIs, Types, And Functions

- `FPurgeState::FPurgeState()` converts requested bytes to required 512-byte block count and initializes accumulators.
- `MoveListEntriesToMap()` moves unconditional list candidates into the time-sorted multimap.
- `CheckFile()` accounts file blocks and inserts candidates into either the age-expired list or LRU multimap.
- `ProcessDirAndRecurse()` scans current traversal files and descends into child directories.
- `TraverseNamespace()` creates `FsTraversal`, protects `pfc-stats`, and starts recursive traversal.

## Control Flow

During traversal, only entries with both data and `.cinfo` are considered. `CheckFile()` uses `.cinfo` mtime as access time. Files older than `m_tMinTimeStamp` go to `m_flist` with timestamp 0 and are counted immediately. Otherwise, the multimap keeps the oldest candidates until accumulated blocks reach the requested target; if too many blocks are held, newest candidates are removed from the map.

## State And Persistence

The object stores references to the OSS, requested/accumulated/total block counts, time thresholds, a list of age-expired candidates, and a time-sorted multimap of LRU candidates. This implementation does not unlink files; the commented `UnlinkInfoAndData()` shows older or planned unlink behavior.

## Dependencies And Integration Points

It depends on `XrdPfcFsTraversal`, `XrdPfcInfo`, `XrdPfcTrace`, `XrdOucEnv`, `XrdOucUtils`, `XrdOss`, and `XrdOssAt`. It feeds purge logic elsewhere with candidate lists/maps.

## Risks And Edge Cases

- Access time is derived from `.cinfo` mtime, so metadata timestamp accuracy controls LRU quality.
- Inconsistent pairs where data or `.cinfo` is missing are skipped, not repaired.
- `m_tMinUVKeepTimeStamp` is stored but not used in visible logic.
- `PurgeCandidate` path is built by concatenating traversal current path and filename; separator correctness depends on `FsTraversal`.
- Protected top directories are hard-coded to `pfc-stats`.

## Test Signals

Tests should cover candidate ordering, byte target trimming, age threshold list insertion, list-to-map movement, traversal with missing pairs, protected directory skipping, total block accounting, and zero/very small requested byte values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.hh

## Purpose

`XrdPfcFPurgeState.hh` declares the state object used to collect file purge candidates from the XrdPfc cache namespace.

## Important APIs, Types, And Functions

- `PurgeCandidate` stores a candidate path, block count, and timestamp.
- `list_t` holds unconditional candidates; `map_t` is a `std::multimap<time_t, PurgeCandidate>` for LRU ordering.
- Accessors expose candidate containers and block/byte totals.
- Threshold setters configure normal age and unverified-checksum retention ages.
- `CheckFile()`, `ProcessDirAndRecurse()`, and `TraverseNamespace()` perform candidate discovery.

## Control Flow

Callers construct the object with a requested byte count, optionally set age thresholds, traverse a namespace root, then consume `refList()` and `refMap()` for purge execution.

## State And Persistence

The class holds candidate state in memory and references the OSS. It does not itself persist changes in the active implementation.

## Dependencies And Integration Points

It forward-declares `XrdOss`, `Info`, and `FsTraversal`, and uses standard list/map/string/stat types. It is part of the cache purge subsystem.

## Risks And Edge Cases

- Exposing mutable references to internal containers lets callers break invariants.
- Timestamp multimap allows duplicate times, which is intended but means deterministic tie order depends on insertion order only indirectly.
- Requested bytes are rounded to blocks with `(bytes >> 9) + 1`, so exact multiples request one extra block.

## Test Signals

Tests should validate constructor rounding, accessor totals, threshold setters, mutable container behavior, and integration with traversal fake data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.cc

## Purpose

`XrdPfcFSctl.cc` implements the filesystem-control plugin adapter that exposes cache management commands such as eviction and cached-state checks through XRootD FSctl.

## Important APIs, Types, And Functions

- `XrdPfcFSctl::XrdPfcFSctl()` stores the cache reference, logger, trace pointer, and trace id.
- `Configure()` obtains `XrdOfsHandle*` from the environment for hiding evicted paths.
- File-based `FSctl()` rejects all file-specific commands as unsupported.
- Base `FSctl()` handles `SFS_FSCTL_PLUGXC` commands `evict`, `fevict`, and `cached`.

## Control Flow

The base command path first verifies that the command is a plugin cache command and that an argument exists. `evict` and `fevict` require the special argument form (`Arg2Len == -2`), call `Cache::UnlinkFile()`, translate cache return codes to SFS return/error values, and hide the path from the OFS handle on success. `cached` calls `Cache::ConsiderCached()` and returns OK only when the cache considers the path sufficiently cached.

## State And Persistence

`evict`/`fevict` can persistently remove cache data and `.cinfo` metadata via `UnlinkFile()`. Successful eviction also updates OFS handle visibility through `Hide()`. `cached` is read-only except for any metadata/stat side effects inside cache checks.

## Dependencies And Integration Points

It depends on `XrdOfsHandle`, `XrdOucEnv`, `XrdOucErrInfo`, `XrdOucCache`, `XrdPfc::Cache`, `XrdPfcTrace`, `XrdSfsInterface`, and `XrdSysTrace`. `XrdOucGetCache()` installs an instance into the environment as `XrdFSCtl_PC*`.

## Risks And Edge Cases

- The code logs `rc=` and `ec=` with the same `ec` value, reducing diagnostic clarity.
- The `cached` command is checked after the eviction branch; invalid forms can flow through earlier error setup before cached handling.
- `Configure()` ignores config parameters and plugin set except for handle lookup.
- File-based FSctl is categorically unsupported.

## Test Signals

Tests should cover missing handle configuration, unsupported file FSctl, wrong command id, missing arguments, `evict` success/ENOENT/EBUSY/EAGAIN/default failures, forced `fevict`, path hiding on success, and `cached` success/failure mapping to `SFS_OK`/`SFS_ERROR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.cc -->
