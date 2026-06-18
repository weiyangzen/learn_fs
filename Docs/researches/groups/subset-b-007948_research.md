# subset-b-007948 research

Grouped research for XRootD OSS cache, configuration, path, copy, relocation, remote storage, mmap, stat-plugin, and usage/quota support. Each section preserves the source path and is delimited for deterministic split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.cc

## Purpose
Implements the static cache-space allocator and scanner used by the OSS layer when `oss.space`/legacy `oss.cache` configure one or more writable cache partitions. It tracks filesystem devices, cache groups, allocation roots, free-space estimates, quota/usage hooks, and Linux device identifiers.

## Important APIs, types, and functions
`XrdOssCache_FSData::XrdOssCache_FSData()` records one physical filesystem, its size/free bytes from `statfs/statvfs`, the real path, device id, update time, and OSS-local device/partition ids. `XrdOssCache_FS::XrdOssCache_FS()` validates duplicate group/path pairs, creates XA group subdirectories via `XrdOssPath::genPath()`, joins the global circular FS list, and appends allocation paths to the owning `XrdOssCache_Group`. `Add()` adds unnamed filesystems for reporting only. `freeSpace()` and `getSpace()` expose whole-system, per-path, and per-cache-group space summaries. `XrdOssCache::Alloc()` is the main allocator: it parses requested group/path constraints, chooses a partition by available space and fuzz policy, generates a PFN, optionally creates the file, and pessimistically debits free space. `Adjust()` variants reconcile usage/free-space deltas after creates, truncates, relocations, and symlink-backed files. `Find()`, `Parse()`, `List()`, `DevInfo()`, `MapDevs()`, `MapDM()`, and `Scan()` support symlink lookup, `group:path` parsing, effective-config display, device remapping, and periodic statfs refresh.

## Control flow
Configuration builds `XrdOssCache_FS` objects, then calls `Init()` to wire usage/quota persistence and allocation policy. Runtime create/relocate paths fill `allocInfo`, call `Alloc()`, and later call `Adjust()` once a real data size is known. The scan thread loops forever unless invoked with `cscanint <= 0`; each tick locks the cache, refreshes free-space snapshots, conditionally reads quotas, and reloads persisted usage counters.

## State and persistence
Most state is process-global static data: `fsfirst/fslast` circular list, `fsdata`, global free-space counters, allocation policy (`minAlloc`, `ovhAlloc`, `fuzAlloc`), and group list rooted at `XrdOssCache_Group::fsgroups`. `Mutex` protects mutable runtime counters. Persistence is delegated to `XrdOssSpace` when usage or quotas are configured; group usage is assigned a persistent group id and refreshed from the usage file.

## Dependencies and integration points
Depends on platform `statfs/statvfs`, `XrdOssPath` for cache PFN layout, `XrdOssSpace` for quotas and persistent usage, `XrdOssOpaque` for default group names, `XrdOssTrace` for debug logging, and `/proc/partitions` plus `/sys/devices/virtual/block/*/slaves` on Linux for device mapping. Called by `XrdOssCreate.cc`, `XrdOssReloc.cc`, `XrdOssRename.cc`, and config display/stat reporting.

## Risks and test signals
Allocation correctness depends on stale free-space snapshots being corrected by `Scan()` and by `Adjust()` calls after data movement. Symlink and XA suffix parsing must stay consistent with `XrdOssPath`. Tests should cover duplicate spaces, forced group/path allocation, ENOSPC, directory auto-creation, quota file reload, usage file recovery, Linux DM mapping fallback, and races between allocation and scanner refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.hh

## Purpose
Declares the cache-space data model used by the OSS implementation: per-filesystem statistics, logical cache groups, partition allocation vectors, allocation requests, and the static `XrdOssCache` service API.

## Important APIs, types, and functions
Platform macros normalize `statfs/statvfs` as `STATFS_t`, `FS_Stat`, `FS_BLKSZ`, and `FS_FFREE`. `XrdOssCache_Space` is a value object returned to virtual-space callers, holding total/free/max/largest/inode/usage/quota counters. `XrdOssCache_FSData` models one physical filesystem and carries flags `OFFLINE`, `ADJUSTED`, and `REFRESH`. `XrdOssCache_FS` models one configured allocation root and exposes `Add()`, `freeSpace()`, and `getSpace()`. `XrdOssCache_FSAP` links a partition to all allocation paths inside that partition. `XrdOssCache_Group` stores logical group metadata, usage/quota, current round-robin pointer, and static public-group references. `XrdOssCache::allocInfo` is the mutable request/response record used by create and relocate operations.

## Control flow
The header establishes a static-service pattern: configuration creates `XrdOssCache_FS` instances, then runtime operations call `XrdOssCache::Alloc()`, `Adjust()`, and `Find()` without owning a cache object. The public API separates initialization (`Init()` overloads), reporting (`List()`, `DevInfo()`), allocation (`Alloc()`), and scanning (`Scan()`).

## State and persistence
Static members declared here define all cache process state: global mutex, aggregate size/free counters, first/last filesystem list pointers, raw filesystem data list, allocation policy, and booleans indicating quota/usage support. Persistent storage is not in the header but is represented by `Usage`/`Quotas` flags that cause calls into `XrdOssSpace`.

## Dependencies and integration points
Includes `XrdOssVS.hh` for virtual-space partition reporting, `XrdSysError` for display/logging, and `XrdSysPthread` for the cache mutex. Its public fields are intentionally accessible to other OSS files, notably create/relocate/rename code that needs group names, suffixes, and target FS pointers.

## Risks and test signals
The API exposes raw pointers and mutable public fields, so lifetime and locking discipline are implicit. Tests should exercise all platform stat macro variants where supported, `allocInfo` buffer limits, group quota/usage visibility, and callers that use `cgPsfx` to distinguish XA from non-XA cache targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.cc

## Purpose
Implements OSS subsystem initialization and parsing of `oss.*` configuration directives. It sets process limits, export/path flags, cache spaces, usage/quota files, staging/RSS commands, name-to-name and stat plugins, mmap policy, preread policy, transfer policy, and final display/stat-reporting state.

## Important APIs, types, and functions
`XrdOssSys::XrdOssSys()` initializes defaults for staging, cache scanning, FD fences, allocation, transfer, preread, stat plugin, and PFC mode. `Configure()` is the orchestration entry point: it registers OSS error tables, raises FD limits, maps devices, parses config with `ConfigProc()`, loads N2N/stat plugins, initializes cache/usage, configures staging, AIO, mmap, PFC, space reporting, prefix generation, stats, and the cache-scan thread. `ConfigXeq()` dispatches directives to handlers such as `xalloc`, `xspace`, `xpath`, `xstg`, `xstl`, `xusage`, and `xxfr`. `ConfigStage()` and `ConfigStageC()` validate remote storage/stage command requirements and start real-time stage threads or queue-style programs. `ConfigCache()`, `ConfigMio()`, `ConfigSpace()`, `ConfigStats()`, and `Config_Display()` resolve derived state.

## Control flow
Parsing is two-stage. `ConfigProc()` reads only `oss.*` and `all.export`, recording requested settings. `Configure()` then performs dependent passes in order: plugin loading, usage/quota init, staging/RSS setup, mmap/PFC flag reconciliation, export-list defaults, final space/stat setup, background scan startup, and final display. `xspace()` either builds one space, expands a wildcard directory into multiple spaces, or records assign/default mappings in `SPList`.

## State and persistence
This file mutates many `XrdOssSys` members and global integration points: `XrdOssRPList`, `OssTrace.What`, `RSSProg`, `StageProg`, `StageFrm`, `STT_Func/Fund`, `RPList`, `SPList`, `DPList`, cache group counts, and usage/quota paths. Persistence is configured by `oss.usage log` and `oss.usage quotafile`, which are passed to `XrdOssCache::Init()`/`XrdOssSpace`. Staging state can persist externally through queue programs or FRM admin paths.

## Dependencies and integration points
Heavy integration with `XrdOucStream`, `XrdOucExport`, `XrdOuca2x`, `XrdOucN2NLoader`, `XrdOucPinLoader`, `XrdOucProg`, `XrdFrcProxy`, `XrdOssCache`, `XrdOssMio`, `XrdOssSpace`, and the OSS API/export flag model. Environment variables such as `XRDDEBUG`, `XRDREDIRECT`, `XRDOSSCSCAN`, `XRDADMINPATH`, `XRDOFSEVENTS`, and `oss.runmode` alter behavior.

## Risks and test signals
This file is a high-blast-radius config hub. Risk areas include directive ordering, deprecated compatibility (`oss.cache`, `msscmd`), path wildcard expansion, mount verification return semantics, FD-limit platform quirks, PFC flag rewrites, plugin ABI selection, stage/RSS requirements, and error-text table length mismatch. Tests should use config fixtures that cover all directive handlers, invalid values, manager/solitary/PFC modes, macOS FD handling, and no-config defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.hh

## Purpose
Provides small shared configuration definitions for the OSS implementation: version string, success constant, option flags, dual-path records, and the structured argument used while constructing cache spaces.

## Important APIs, types, and functions
`XRDOSS_VERSION` is the OSS config version string. `XrdOssOK` normalizes success to zero. `XrdOss_USRPRTY` and `XrdOss_CacheFS` are flags stored in `XrdOssSys::OptFlags`. `OssDPath` is a linked-list node pairing logical and physical paths for stats reporting. `OssSpaceConfig` holds references to a space name, path, and mount name while parsing/building `oss.space`; it also carries booleans for XA path layout, mount-check failure handling, and whether mount checking is enabled.

## Control flow
The header has no executable control flow. Its objects are populated by `XrdOssConfig.cc`: `OssSpaceConfig` starts as XA-enabled, no-fail false, and no mount check, then `xspace()` mutates the flags before `xspaceBuild()` creates an `XrdOssCache_FS`.

## State and persistence
`OssDPath` owns duplicated path strings indirectly through its fields but has no destructor, matching process-lifetime config storage. `OssSpaceConfig` stores references to `XrdOucString` instances owned by the parser stack and is not persistent beyond build time.

## Dependencies and integration points
Forward-declares `XrdOucString` to avoid pulling the full string implementation into all users. Consumed primarily by `XrdOssConfig.cc`, with `OptFlags` values used by other OSS code to detect cache filesystem and user-priority staging behavior.

## Risks and test signals
The reference fields in `OssSpaceConfig` require stack-lifetime discipline. Tests should cover config paths that set `XrdOss_CacheFS`, `XrdOss_USRPRTY`, and `OssDPath` generation for stats, plus wildcard `oss.space` expansion that repeatedly reuses the same `OssSpaceConfig` object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.cc

## Purpose
Implements file-copy support used by relocation. It optimizes same-filesystem copies with hard links, otherwise copies data in mmap-backed segments with a traditional pread/pwrite fallback, then copies xattrs and preserves mtime.

## Important APIs, types, and functions
`XrdOssCopy::Copy(inFn, outFn, outFD)` owns the input fd and the pre-opened output fd through local RAII wrappers. It stats both files, hard-links when source and destination devices match, copies in 1 MiB segments via `mmap()` and `Write()`, falls back to buffered `pread()` only when no segment was copied, copies extended attributes through `XrdSysFAttr::Xat->Copy()`, and sets atime/mtime with `utime()`. `Write()` is a retry loop around `pwrite()` that handles EINTR and returns logged negative errors.

## Control flow
The fast path is: open input, stat input/output, resolve symlink source if needed, unlink output placeholder, create a hard link, return file size. The cross-device path maps each segment and writes it. If mmap fails before any data transfer, it logs and attempts a full traditional copy. Partial mmap failure after some bytes returns `-EIO`.

## State and persistence
No global state is modified. Persistence effects are the destination file content, copied extended attributes, and destination timestamps. The output fd is always closed by the local wrapper.

## Dependencies and integration points
Used by `XrdOssReloc.cc`. Depends on POSIX file APIs, `mmap`, `utime`, `XrdSysFAttr`, `OssEroute`, and `OssTrace`. It assumes the caller already created/preallocated the destination file descriptor and handles cleanup on failure.

## Risks and test signals
The fallback only runs if nothing was copied; failures after partial mmap writes leave cleanup to the caller. Hard-linking a symlink requires careful `lstat/readlink` behavior. Tests should cover same-device regular files and symlinks, cross-device copy, mmap failure fallback, EINTR handling, xattr copy failures, timestamp preservation, and cleanup behavior when `Copy()` returns a negative code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.hh

## Purpose
Declares the small static copy helper used by OSS relocation code.

## Important APIs, types, and functions
`XrdOssCopy::Copy(const char *inFn, const char *outFn, int outFD)` copies or links data from an input pathname into a caller-supplied destination fd/path pair and returns the copied size or a negative error. The private `Write()` helper writes a buffer at an offset and is implemented in the `.cc`.

## Control flow
There is no header control flow. The public API intentionally exposes only a static operation; no instance state is needed.

## State and persistence
The class has no data members. All persistence effects occur in the implementation by modifying the destination file, copying xattrs, and changing timestamps.

## Dependencies and integration points
Forward-only declaration avoids include dependencies. Included by `XrdOssReloc.cc` and `XrdOssCreate.cc` even though relocation is the direct data-copy caller in this subset.

## Risks and test signals
Callers must pass an already valid output fd and must expect `Copy()` to close it. Tests should check this ownership contract and negative return propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCreate.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCreate.cc

## Purpose
Implements `XrdOssSys::Create()`, including local creation, cache-space allocation, remote-storage prechecks/creates, stage-command routing for creates, colocation, symlink creation for cache PFNs, and copy-time/PFN xattr setup.

## Important APIs, types, and functions
`XrdOssCreateInfo` carries path, LFN, mode, create options, and resolved export flags. `Create()` checks path writability via `Check_RO`, generates the local path, handles dangling symlinks, processes `XRDOSS_coloc` by resolving `oss.coloc` into a cache group/path, routes missing-file creates to `Stage()` when `StageCreate` is enabled, reopens existing files unless `XRDOSS_new` is set, creates parent directories for `XRDOSS_mkpath`, validates/creates MSS-side files for remote exports, and chooses `Alloc_Cache()` or `Alloc_Local()`. `Alloc_Cache()` parses `oss.asize` and `oss.cgroup`, applies `SPList` assign/default rules, calls `XrdOssCache::Alloc()`, sets the PFN xattr, sets copy-time metadata, and symlinks the logical path to the cache PFN. `Alloc_Local()` creates a normal local file. `SetFattr()` records `XrdFrcXAttrCpy` ctime where migration xattrs are enabled.

## Control flow
Existing paths short-circuit through open/truncate/xattr handling. Missing paths can go through remote checks, cache allocation, or local allocation. Cache allocation creates a hidden PFN first, then atomically replaces/creates the logical symlink; failures unlink the PFN where possible.

## State and persistence
Creates files, directories, symlinks, remote MSS entries, xattrs, and cache free-space reservations. If xattrs are unsupported, it marks the export path `XRDEXP_NOXATTR` through `RPList`. Truncating a symlink-backed existing file adjusts cache accounting.

## Dependencies and integration points
Integrates with `XrdOssCache`, `XrdOssPath`, `XrdOssSpace`, `XrdOucEnv`, `XrdOucExport`, `XrdFrcXAttr`, `XrdSysFAttr`, remote MSS helpers, and the global `XrdOssSS` staging interface. Opaque env keys from `XrdOssOpaque.hh` drive allocation size, cache group, and colocation.

## Risks and test signals
High-risk paths include dangling symlink cleanup, colocation URL decoding, remote/local consistency when MSS create succeeds but local allocation fails, PFN xattr failure, xattr unsupported fallback, and symlink replacement races. Tests should cover new/existing/truncate, mkpath, StageCreate, RCREATE/NOCHECK combinations, cache and non-cache exports, forced colocation, ENOSPC, and unsupported xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssCreate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssDefaultSS.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssDefaultSS.hh

## Purpose
Declares the external factory for obtaining the default OSS storage-system object.

## Important APIs, types, and functions
`XrdOssDefaultSS(XrdSysLogger *logger, const char *cfg_fn, XrdVersionInfo &urVer)` returns an `XrdOss *` for callers that want the default configured storage system. It requires a logger, an optional/required config path depending on the environment, and the caller's version info for compatibility checks.

## Control flow
The header has no implementation. Its documented call flow is: include the header, provide `XrdVERSIONINFODEF`/`XrdVersionInfo`, and call the factory. The implementation elsewhere is expected to configure and return an OSS object or null.

## State and persistence
No state is declared here. The returned object likely owns process-level storage-system configuration, but that is outside this file.

## Dependencies and integration points
Includes `XrdVersion.hh` and `XrdOss.hh`, so it bridges plugin/factory users to the OSS API. It is an ABI-facing declaration for code that loads or embeds the default storage system.

## Risks and test signals
Version compatibility and null-return handling are the main contract points. Tests should verify callers pass compatible version metadata and fail cleanly on missing or invalid configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssDefaultSS.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssError.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssError.hh

## Purpose
Defines OSS-specific error-code numbers, mappings to system `errno` values, and human-readable text used by the OSS error table registered during configuration.

## Important APIs, types, and functions
`XRDOSS_EBASE` and `XRDOSS_ELAST` delimit the custom error range 8001 to 8028. `XRDOSS_E80xx` names individual OSS codes. `XRDOSS_N80xx` maps each custom code to a POSIX errno such as `EROFS`, `EPERM`, `EFBIG`, `EXDEV`, `ENOSPC`, or `EAGAIN`. `XRDOSS_T80xx` provides the message text used by `XrdOssErrorText` in `XrdOssConfig.cc`.

## Control flow
No executable control flow exists. `XrdOssSys::Configure()` constructs `XrdSysError_Table` and `XrdSysError_Table_Errno` from the text and errno mappings.

## State and persistence
No mutable state. The definitions are compile-time constants.

## Dependencies and integration points
Included by most OSS implementation files to return consistent negative OSS errors. The mappings are used by `XrdSysError` so callers can see both custom OSS diagnostics and conventional errno behavior.

## Risks and test signals
The range includes a commented-out `XRDOSS_E8016` while `XRDOSS_N8016` and text still exist; table ordering and array length must remain aligned with `XRDOSS_EBASE`. Tests should check every code maps to intended errno/text, especially remote storage response errors, creation-prohibited, relative-path, and dynamic-cast failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssError.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMSS.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMSS.cc

## Purpose
Implements the legacy command-based remote/mass-storage-system interface used for directory listing, stat/existence checks, create, unlink, and rename operations through an external RSS/MSS command.

## Important APIs, types, and functions
`XrdOssHandle` wraps a directory stream and flags EOF/type state. `MSS_Opendir()` runs `dlist` and returns a stream-backed handle. `MSS_Readdir()` returns one remote directory entry per stream line and handles EOF/error propagation. `MSS_Closedir()` validates and deletes the handle. `MSS_Create()` invokes `create <path> <mode>`. `MSS_Stat()` either checks existence (`exists` or `statx` for `msscmd`) or parses a `statx` record into `struct stat`; `tranmode()` converts rwx triplets. `MSS_Unlink()` invokes `rm`, and `MSS_Rename()` invokes `mv`. `MSS_Xeq()` is the core executor: it runs `RSSProg`, waits for a response with `RSSTout`, parses the leading return code, logs unexpected failures, and returns a stream to callers that need more data.

## Control flow
All public operations validate path length, issue a command through `MSS_Xeq()`, and return zero or negative errors. Directory open intentionally leaves the command stream alive until readdir/closedir. Stat with a buffer performs command execution, first-line response parsing, stat-field conversion, and stream deletion.

## State and persistence
No file-local persistent state except static `NoResp` throttling timeout logs. External state changes occur in the remote storage service through command execution. Directory handles own subprocess streams and must be closed.

## Dependencies and integration points
Depends on `XrdOucProg`/`XrdOucStream`, `RSSProg`, `RSSCmd`, `RSSTout`, `isMSSC`, global logging/tracing, and config-stage setup in `XrdOssConfig.cc`. Called by create, rename, stat, unlink, and directory operations in the wider OSS implementation.

## Risks and test signals
The command protocol is brittle: first response line must be numeric and statx formatting must match `sscanf`. Timeout behavior maps no response to custom OSS errors. Tests should use fake RSS programs for success, ENOENT-ok cases, malformed replies, delayed replies, statx directories/links/files, long paths, and handle misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMSS.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.cc

## Purpose
Implements memory-mapped read optimization for OSS files, including mapping reuse, optional `mlock`, optional page preloading, idle reclamation, and configuration display/update.

## Important APIs, types, and functions
Static state includes `MM_Hash`, `MM_Mutex`, permanent and idle queues, enable/check/preload flags, max bytes, page size/count, and current mapped bytes. `Display()` prints effective `oss.memfile` settings. `Map()` stats the fd, creates a device+inode hash key, reuses an existing mapping when present, reclaims idle mappings if `MM_max` would be exceeded, `mmap()`s the whole file, optionally `mlock()`s it, creates an `XrdOssMioFile`, adds it to the hash, queues permanent mappings, and starts a preload thread when configured. `preLoad()` touches one byte per page and then recycles. `Recycle()` decrements use count and moves non-permanent mappings to the idle list. `Reclaim()` removes idle mappings from queues/hash. `Set()` overloads update boolean mode flags and max-memory policy.

## Control flow
Map callers get a shared `XrdOssMioFile` whose `inUse` count protects the mapping. When callers finish, they call `Recycle()`. Idle mappings remain cached until memory pressure triggers `Reclaim(amount)` or a reuse path removes them from the idle list.

## State and persistence
State is entirely in-process memory. `XrdOssMioFile::~XrdOssMioFile()` unmaps memory when the hash deletes the object. No disk persistence occurs.

## Dependencies and integration points
Configured by `oss.memfile` in `XrdOssConfig.cc` and likely used by OSS file open/read paths outside this subset. Depends on POSIX mmap/mlock support, `XrdOucHash`, `XrdSysThread`, `XrdOucUtils::bin2hex`, and OSS logging/tracing.

## Risks and test signals
Risk areas include zero-length files passed to `mmap`, `MM_inuse` not decremented on some `mmap`/object-allocation failure paths after it is incremented, preload thread races with reuse/recycle, and platform support differences. Tests should exercise reuse, idle reclaim ordering, permanent mappings, max percent parsing, mlock permission failure, preload lifecycle, and non-POSIX-mapped builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.hh

## Purpose
Declares the static mmap manager used by OSS to enable, cache, and reclaim memory-mapped file views.

## Important APIs, types, and functions
Defines option bits `OSSMIO_MLOK`, `OSSMIO_MMAP`, and `OSSMIO_MPRM`. Public methods are `Display()`, `isAuto()`, `isOn()`, `Map()`, `preLoad()`, `Recycle()`, and `Set()` overloads. Private methods reclaim mappings by byte amount or object pointer. Static members store the hash table, mutex, permanent queue, idle queue, mode flags, page sizing, max mapping budget, and current in-use byte count.

## Control flow
The header exposes a static lifecycle: config uses `Set()`, open paths use `Map()`, read paths export memory through `XrdOssMioFile`, and close paths call `Recycle()`. Reclaim is internal to `Map()` and reuse handling.

## State and persistence
All declared members are process-static and volatile. No persistent storage is represented.

## Dependencies and integration points
Includes `XrdOssMioFile.hh`, `XrdOucHash`, `XrdSysPthread`, and `XrdSysError`. Used by config parsing/display and file I/O paths that want mmap acceleration.

## Risks and test signals
Because the class is entirely static, tests should isolate state between cases or reset via `Set()` and controlled recycle/reclaim. Callers must honor the `Recycle()` contract to prevent retained mappings and budget exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMioFile.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMioFile.hh

## Purpose
Defines the object representing one mapped file in the OSS mmap manager.

## Important APIs, types, and functions
`XrdOssMioFile` is a friend of `XrdOssMio`. The public `Export(void **Addr)` returns the mapping base address via `Addr` and the mapped size as `off_t`. The constructor copies a hash name and initializes use count, list pointer, and size. The destructor is implemented in `XrdOssMio.cc` and unmaps the file when POSIX mapped files are available.

## Control flow
Objects are created by `XrdOssMio::Map()`, stored in `MM_Hash`, linked into permanent or idle lists, exported to file readers, recycled through `XrdOssMio::Recycle()`, and destroyed when reclaimed from the hash.

## State and persistence
Each object stores `Next`, device, inode, status flags, use count, mapped base, size, and a fixed-size hash name. State is in memory only.

## Dependencies and integration points
Requires system `dev_t`, `ino_t`, and `off_t`. It intentionally exposes little beyond `Export()`; lifecycle management stays in `XrdOssMio`.

## Risks and test signals
The constructor uses `strcpy()` into `HashName[64]`; safety depends on `XrdOssMio::Map()` generating bounded keys. Tests should check export size/address, destructor unmapping through reclaim, and that hash names generated from large platform `dev_t/ino_t` values fit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssMioFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssOpaque.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssOpaque.hh

## Purpose
Defines opaque environment keys and constants used to pass OSS-specific allocation and staging hints through `XrdOucEnv`.

## Important APIs, types, and functions
`OSS_ASIZE` names the estimated allocation size key. `OSS_CGROUP` names the requested cache group or `group:path` constraint. `OSS_USRPRTY` and `OSS_SYSPRTY` carry user/system staging priority keys. `OSS_CGROUP_DEFAULT` is `"public"`. `OSS_VARLEN` caps variable length, `OSS_MAX_PRTY` caps priorities, and `OSS_USE_PRTY` is the default priority.

## Control flow
No executable flow. Runtime create/stage paths read these keys from env objects to influence allocation and queueing.

## State and persistence
No mutable state. The macros cast string literals to `char *`, matching older APIs that expect mutable `char *` names.

## Dependencies and integration points
Used by `XrdOssCreate.cc`, `XrdOssCache.cc`, staging/transfer code, and callers that set opaque URL/env parameters. `OSS_CGROUP_DEFAULT` must match the public group logic in `XrdOssCache_Group`.

## Risks and test signals
Because keys are macros rather than typed constants, typo resistance is low. Tests should cover `oss.asize`, `oss.cgroup`, default group fallback, priority bounds, and interaction with URL-decoded colocation parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssOpaque.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.cc

## Purpose
Implements cache path encoding/decoding helpers for XA cache spaces, old-style cache paths, suffix classification, cache-group extraction, PFN generation, and cache filename prefix initialization.

## Important APIs, types, and functions
`Convert()` converts an old symlink target into a new target by preserving the prefix before `%` and tamping slashes in the new path. `Extract()` reads a symlink or path and returns the cache group while trimming the buffer to the cache base. `genPath()` ensures a cache group directory exists in a path and builds a four-byte suffix encoding group-position and group-name length. `genPFN(fnInfo&, ...)` generates either old-style tamped PFNs or XA PFNs using a per-process prefix, two-level sequence directory, encoded sequence, and suffix. `genPFN(char*,...)` reverses a tamped path after `%`. `getCname()` extracts the cache group from a symlink. `pathType()` classifies migration/memory suffixes such as `.anew`, `.fail`, `.mmap`, and `.pfn`. `Trim2Base()` truncates extended cache paths to the allocation root. `InitPrefix()` seeds the PFN prefix from time, pid, and encoded network address. `posCname()` decodes cache-group position from the suffix.

## Control flow
Configuration calls `genPath()` and later `InitPrefix()` once cache FS mode is known. Allocation calls `genPFN()` for every cache target. Rename/relocate/accounting paths call `getCname()`, `Trim2Base()`, `Convert()`, and `pathType()` to interpret symlink targets and sidecar suffix files.

## State and persistence
Static `h2c`, `pfnPfx`, and suffix table are process-global. Generated PFN names and symlink targets are persistent filesystem artifacts. `genPFN()` uses a static mutex-protected sequence counter for uniqueness within one process, combined with the prefix for broader uniqueness.

## Dependencies and integration points
Depends on `XrdOssSpace` for space-name limits, `XrdNetUtils` for address encoding, and POSIX `lstat/readlink`. Tight coupling exists with `XrdOssCache` suffix fields and symlink layout assumptions in create/rename/relocate.

## Risks and test signals
Encoding is compact and easy to break. Tests should cover long group names, paths near `MAXPATHLEN`, missing `pfnPfx`, network-address encoding failure, suffix classification ranges, old-style tamped paths, XA symlink targets ending in `%`, and `Trim2Base()` on malformed input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.hh

## Purpose
Declares the static path utility interface and suffix constants used throughout OSS cache-space code.

## Important APIs, types, and functions
`fnInfo` packages allocation-root path, path length, generated slash position, and XA suffix pointer for `genPFN()`. `xChar` is `%`, the escape/sentinel character used in cache symlinks and suffix encodings. `sfxLen` is four bytes. Public static helpers include `Convert()`, `Extract()`, `genPath()`, `genPFN()` overloads, `getCname()`, `isXA()`, `InitPrefix()`, `pathType()`, and `Trim2Base()`. `theSfx` enumerates base, migration, memory, and PFN suffix types. `chkMem`, `chkMig`, `chkPfn`, and `chkAll` select suffix classification ranges.

## Control flow
No header execution. The declaration shapes call flow across cache construction, allocation, rename, relocation, stat/open path handling, and cleanup of sidecar migration/memory files.

## State and persistence
Declares static `h2c` and `pfnPfx`. These are initialized in the `.cc` and influence persistent PFN names.

## Dependencies and integration points
Includes only basic system headers through implementation users. It is included by cache, create, rename, relocate, and config files, making it the central contract for cache path layout.

## Risks and test signals
Public APIs operate on caller-provided buffers and raw C strings. Tests should verify buffer length failures, exact suffix enum ordering, `isXA()` behavior on empty/short strings, and consistency between `genPath()` suffix production and `posCname()` decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssPath.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssReloc.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssReloc.cc

## Purpose
Implements cache relocation/copying of an existing file to another cache group or partition, optionally anchoring a copy under a separate namespace path.

## Important APIs, types, and functions
`XrdOssSys::Reloc(tident, path, cgName, anchor)` is the sole exported operation. It uses a local `pendFiles` cleanup helper to close pending fds and unlink temporary PFNs/links on failure. It supports pure PFN relocation when `anchor` is `"."`, normal LFN relocation through `GenLocalPath()`, and copy-to-anchor mode when `anchor` is a base path. It parses target `cgName` through `XrdOssCache::Parse()`, gets current cache group/path from `XrdOssPath::getCname()`, allocates an XA target through `XrdOssCache::Alloc()`, copies data with `XrdOssCopy::Copy()`, creates a symlink to the target, atomically renames it over the original for relocation, and adjusts cache usage/free counters.

## Control flow
Relocation validates that the source exists and is a regular file, rejects no-op moves to the same group/path, allocates the target PFN, copies data, creates either an `.anew` replacement symlink or an anchored copy symlink, and finally removes/adjusts the old cache target when this was a move rather than a copy.

## State and persistence
Creates a new cache PFN, new symlink, and possibly removes the old PFN/symlink. Updates cache accounting for old and new locations through `XrdOssCache::Adjust()`. The cleanup object removes incomplete artifacts on early return.

## Dependencies and integration points
Depends on `XrdOssCache`, `XrdOssPath`, `XrdOssCopy`, `XrdOucUtils::makePath`, and global logging/tracing. It assumes XA cache spaces because it rejects allocations without `cgPsfx`.

## Risks and test signals
Important tests include no-op detection, pure PFN relocation, anchored copy preserving original, atomic replacement, cleanup on copy/symlink failure, old symlink target deletion, accounting deltas for old/new filesystems, and non-XA target rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssReloc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssRename.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssRename.cc

## Purpose
Implements OSS rename semantics for local files, cache symlinks, and remote/MSS-backed files while enforcing compatible export options.

## Important APIs, types, and functions
`XrdOssSys::Rename()` checks write permissions/export flags for old and new names, rejects renames across incompatible remote/migration attributes, generates local and optional remote paths, prevents overwriting remote or symlink targets, creates parent directories, renames either a normal local path or a symlink-backed cache file, then mirrors the rename to MSS when appropriate. `RenameLink()` handles symlink targets: for XA cache targets ending in `%`, it calls `RenameLink3()` and may adjust solitary usage for offline `.anew` stage-ins; for old-style targets it converts the target with `XrdOssPath::Convert()`, creates the new logical symlink, renames the real PFN, and unlinks the old logical path. `RenameLink3()` updates the PFN xattr to the new logical path before renaming the symlink and restores the old attribute if rename fails.

## Control flow
The local rename runs first. Remote rename is attempted only for remote exports and when local rename succeeded or the local path was missing. Symlink-specific flow preserves cache target integrity and xattrs.

## State and persistence
Renames local files/symlinks, old-style real PFNs, remote MSS paths, and PFN xattrs. It may create destination parent directories. In solitary usage mode, it adjusts cache usage when an offline `.anew` link becomes visible.

## Dependencies and integration points
Uses `Check_RO`, `GenLocalPath`, `GenRemotePath`, `MSS_Rename`, `XrdOssPath`, `XrdSysFAttr`, `XrdFrcXAttrPfn`, and export flags from `XrdOucExport`.

## Risks and test signals
Remote/local consistency can diverge if MSS rename fails after local rename. Symlink overwrite prevention is stricter than normal local rename. Tests should cover remote-only/local-only incompatibility, old-style and XA cache symlink renames, xattr rollback failure, existing destination handling, parent path creation, and solitary `.anew` usage adjustment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssRename.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssSIgpfsT.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssSIgpfsT.cc

## Purpose
Provides a stat-info plugin for GPFS backed by tape, allowing stat calls to hide offline/nonresident files or report them depending on configured program/role-specific parameters.

## Important APIs, types, and functions
The exported global `XrdOssStatInfoResOnly` stores the errno policy for nonresident files, defaulting to `ENOENT`. `XrdOssStatInfo()` performs `stat()`, treats size-zero or allocated-block files as online, and for nonresident files either returns `ENOENT` when `XRDOSS_resonly` is requested, returns the configured errno, or succeeds when all files are allowed. `XrdOssStatInfoParm()` parses `all`, `online`, and `online:eperm`. `XrdOssStatInfoInit()` reads parameters from `XrdOucEnv`, applying increasingly specific keys `stat`, `stat.<prog>`, and `stat.<prog>.<role>`, normalizes legacy role names, logs the effective policy, and returns the stat hook. `XrdVERSIONINFO` publishes plugin version metadata.

## Control flow
Initialization evaluates global, program-specific, then role-specific settings so later matches override earlier policy. Runtime stat calls are simple: real stat, online heuristic, policy-based errno assignment.

## State and persistence
Only process-global policy state is persisted in memory. No disk writes occur.

## Dependencies and integration points
Loaded by `oss.statlib` through `XrdOssConfig.cc`. Uses `XRDPROG` and `XRDROLE` environment variables, `XrdOucEnv` parsing, and the `XrdOssStatInfo` plugin ABI.

## Risks and test signals
The online heuristic relies on `st_blocks`, which is filesystem-specific. Tests should cover all parameter scopes and override order, invalid parameter rejection, role normalization, `XRDOSS_resonly`, zero-size files, sparse/offline files, and both `ENOENT`/`EPERM` policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssSIgpfsT.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.cc

## Purpose
Implements persistent cache-group usage accounting and quota-file loading for OSS cache spaces.

## Important APIs, types, and functions
Static members hold quota/usage filenames, update filename, in-memory `uEnt` table, active-entry vector, free entry, usage fd, sync counters, solitary flag, and last modification times. `Adjust()` updates a group usage field (`Serv`, `Pstg`, `Purg`, or `Admin`), using file locks for non-server updates and converting solitary server changes to post-stage/purge fields. `Assign()` finds or creates a usage entry for a cache group and returns its index. `Init()` configures quota and usage files, creates `.Usage`/`.Usage.upd`, reads or initializes the fixed-size table, and exports file paths to the environment. `Quotas()` reloads the quota file when mtime changes and updates matching `XrdOssCache_Group` quota fields. `Readjust()` rereads the usage file when the update marker changes and merges pending staged/purged/admin adjustments into server usage. `Unassign()` clears a group entry. `Usage()` overloads return counters with optional reread. `UsageLock()` wraps blocking `fcntl` file locks.

## Control flow
Configuration calls `Init()` then `XrdOssCache::Init()` assigns cache groups. Runtime operations call `Adjust()` for size changes. The cache scan thread calls `Quotas()` and `Readjust()` to refresh quotas and reconcile usage deltas from other processes.

## State and persistence
Persistence is the fixed-size `.Usage` file plus `.Usage.upd` marker and optional quota file. Updates use positional reads/writes into `uEnt` records, optional fsync batching, and file locks to coordinate multiprocess access. In-memory state mirrors active records.

## Dependencies and integration points
Depends on `XrdOssCache_Group`, `XrdOuca2x`, `XrdOucEnv`, `XrdOucStream`, `XrdOucUtils::InstName`, `XrdSysFD_Open`, and OSS logging. The quota file directly names cache groups configured in `XrdOssCache`.

## Risks and test signals
The fixed-size table can fill, `Unassign()` appears to write from `uData[freeEnt]` after clearing `uData[i]`, and `UsageLock()` has a local static mutex shadowing the namespace mutex in a confusing way. Tests should cover fresh and existing usage files, invalid file size, concurrent adjust/readjust, sync batching, solitary conversions, quota reload mtime behavior, unknown quota groups, table overflow, and unassign correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.cc -->
