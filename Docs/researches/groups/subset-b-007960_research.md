# Research Report: subset-b-007960

This grouped report covers the XRootD proxy file cache files requested for `subset-b-007960`. Each source file section is wrapped with the exact reconciliation markers required by the research cron.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.hh

## Purpose
Declares `XrdPfcFSctl`, the file-system-control plugin facade that binds the proxy file cache (`XrdPfc::Cache`) into the XRootD OFS FSctl extension point. It is a header-only declaration in this subset; implementation lives elsewhere, but this file defines the ABI-facing methods that accept control requests from OFS clients.

## Important APIs, Types, and Functions
- `class XrdPfcFSctl : public XrdOfsFSctl_PI`: implements the OFS FSctl plugin interface.
- `Configure(const char *CfgFN, const char *Parms, XrdOucEnv *envP, const Plugins &plugs)`: configures the plugin with the XRootD configuration file, parameters, environment, and plugin bundle.
- `FSctl(int cmd, int alen, const char *args, XrdSfsFile &file, XrdOucErrInfo &eInfo, const XrdSecEntity *client)`: file-scoped control entry point.
- `FSctl(int cmd, XrdSfsFSctl &args, XrdOucErrInfo &eInfo, const XrdSecEntity *client)`: structured FSctl entry point.
- Constructor `XrdPfcFSctl(XrdPfc::Cache &cInst, XrdSysLogger *logP)` stores the cache singleton reference and logger-derived diagnostics.

## Control Flow
The header establishes the virtual callbacks expected by `XrdOfsFSctl_PI`. Runtime flow is: XRootD loads/configures the plugin, then OFS dispatches control commands through one of the two `FSctl` overloads. The class can use `myCache` to route those commands into proxy-cache operations and `hProc`/trace/log members for handle processing and diagnostics.

## State and Persistence Behavior
The class itself owns no persistent cache state. It holds references/pointers to runtime objects: `myCache`, `hProc`, `Log`, `sysTrace`, and `m_traceID`. Persistent effects, if any, are delegated to `XrdPfc::Cache` or the file object passed to `FSctl`.

## Dependencies and Integration Points
Depends on `XrdOfs/XrdOfsFSctl_PI.hh` for the plugin ABI and `XrdSys/XrdSysError.hh` for logging. Forward declarations connect to OFS handles, security identities, SFS files, and cache internals. Integration risk is ABI-sensitive because method signatures override a plugin interface.

## Risks and Test Signals
Risks include implementation/header signature drift against `XrdOfsFSctl_PI`, null logger/trace handling, and authorization behavior in command handlers. Useful tests are plugin load/configuration tests, command dispatch tests for both overloads, and negative tests for malformed arguments or unauthorized clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.cc

## Purpose
Implements `XrdPfc::File`, the central block cache object for the proxy file cache. It opens/creates local data and `.cinfo` metadata files, coordinates concurrent read requests, downloads missing blocks from remote `XrdOucCacheIO`, writes completed blocks to disk, persists block state, reports usage to `ResourceMonitor`, and drives prefetch.

## Important APIs, Types, and Functions
- `File::FileOpen()` constructs and opens a `File`, returning null on local open or metadata setup failure.
- `Open()` creates/opens the local data file and `.cinfo`, validates existing metadata/data consistency, applies checksum and URL CGI configuration, initializes access statistics, and registers the open with `ResourceMonitor`.
- `Close()` closes local handles, reconciles final `st_blocks`, and registers file close.
- `Read()` and `ReadV()` are the public entry points used by `IOFile`; complete files take a direct local disk fast path.
- `ReadOpusCoalescere()` is the main cache read planner: it splits user I/O into blocks, classifies chunks as RAM, disk, remote-cacheable, or direct remote bypass, issues asynchronous remote requests, and returns either bytes/error or `-EWOULDBLOCK`.
- `PrepareBlockRequest()`, `ProcessBlockRequest()`, `ProcessBlockResponse()`, `ProcessBlockSuccess()`, and `ProcessBlockError()` manage in-flight `Block` lifecycle.
- `WriteBlockToDisk()` writes downloaded blocks into the local data file, updates `Info` bitmaps, and schedules `Sync()`.
- `Sync()` fsyncs data, writes and fsyncs `.cinfo`, records access stats, and initiates emergency unlink/shutdown on sync failure.
- `Prefetch()` picks the next missing block and issues asynchronous fetches under prefetch flow control.
- `ioActive()`, `AddIO()`, `RemoveIO()`, `RequestSyncOfDetachStats()`, and `FinalizeSyncBeforeExit()` coordinate detach and final metadata flush.

## Control Flow
Open flow first waits for `ResourceMonitor` initial scan cross-check, creates data and metadata files in configured data/meta spaces, reads existing `.cinfo` if present, truncates/reset metadata when data size, checksum policy, or uvkeep rules make cached contents invalid, and registers an access record. Read flow locks `m_state_cond`, rejects shutdown/detaching IO, fast-paths complete files, otherwise walks requested blocks. Existing RAM blocks are refcounted, disk blocks are coalesced into local `ReadV`, missing blocks allocate RAM and remote reads, and RAM pressure causes direct remote `ReadV` bypass. Completion is split between synchronous disk/RAM work and asynchronous callbacks. Block callback flow writes successful downloads to disk through the cache write queue, notifies all waiting chunk requests, reissues failed blocks through another IO when possible, and finalizes read callbacks once all chunk/direct/sync parts complete.

## State and Persistence Behavior
Persistent state is split between the local data file and `Info` metadata file with extension `.cinfo`. `Info` tracks written/synced/prefetched block bitmaps, file size, block size, checksum mode, and access history. `File` maintains transient state in `m_block_map`, `m_io_set`, ref counts, write/sync counters, prefetch state, remote locations, and resource-monitor deltas. `Sync()` is the durability boundary: data is fsynced before `.cinfo` is updated so metadata does not advertise unsynced blocks. Emergency shutdown prevents further writes and causes future reads to return `-ENOENT`.

## Dependencies and Integration Points
Integrates with `Cache` for active-file lifetime, RAM allocation, write queue, sync scheduling, purge protection, config, xattrs, and remote cache-control storage. Uses `ResourceMonitor` tokens for open/update/close accounting. Uses `XrdOss` for local file operations, `XrdOucCacheIO` for remote reads, `XrdOucIOVec` and `XProtocol` limits for vector read chunking, `XrdCl::URL` for CGI options, and `XrdPfc::Info`/`Stats`/trace macros for metadata and diagnostics.

## Risks and Test Signals
High-risk areas are concurrency around `m_state_cond`, refcount/free ordering between read callbacks and write queue callbacks, recursive `Sync()` under writes-during-sync, and error recovery that unlinks active files. Other risks include wrong offset math for block-based files (`m_offset`), stale `.cinfo` acceptance, direct-read fallback when RAM is exhausted, and checksum downgrade/reset behavior. Strong tests should cover partial reads across block boundaries, concurrent ReadV against same missing block, failed remote reads with reissue through a second IO, sync failure unlink, prefetch stop/hold/complete transitions, CGI blocksize/prefetch parsing, and restart from existing `.cinfo` plus truncated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.hh

## Purpose
Declares the core proxy-cache file model and its read/block helper types. The header exposes the `File` API used by cache IO adapters while hiding local file handles, metadata state, block map, sync machinery, and prefetch internals.

## Important APIs, Types, and Functions
- `ReadReqRH`: internal callback wrapper carrying expected size, read sequence id, chunk count, and the external callback.
- `ReadRequest`: aggregate state for a logical read spanning disk, RAM, remote block, and direct remote sub-requests.
- `ChunkRequest`: maps a requested byte range within a block to the final user buffer and owning `ReadRequest`.
- `Block`: transient in-memory block with remote IO identity, buffer, offset/size, refcount, checksum vector, status, and pending chunk requests.
- `BlockResponseHandler` and `DirectResponseHandler`: callback adapters from remote reads back into `File`.
- `File`: public operations include `FileOpen`, `Read`, `ReadV`, `Sync`, `WriteBlockToDisk`, `Prefetch`, `Fstat`, IO attach/detach helpers, resource-monitor accessors, and emergency shutdown.

## Control Flow
The header defines a layered async model. IO adapters create `ReadReqRH` objects and call `File::Read`/`ReadV`. `File` creates `ReadRequest` only when asynchronous work is needed. Each missing or in-flight block receives `ChunkRequest` entries, while callback handlers call back into `File` to update block and read-request state. Inline `inc_ref_count`/`dec_ref_count` are always intended to run under `m_state_cond`, and `dec_ref_count` frees completed blocks when the last user/write-queue reference drops.

## State and Persistence Behavior
Persistent metadata is encapsulated in `Info m_cfi`; local persistence handles are `m_data_file` and `m_info_file`. Transient state includes active IO set, current prefetch IO, writes-during-sync vector, non-flushed count, block map, resource-monitor stats/deltas, remote locations, and prefetch score counters. The header makes the state invariants explicit: blocks may be freed only after finished and refcount zero, and sync state separates written from synced metadata.

## Dependencies and Integration Points
Depends on `XrdPfcTypes.hh`, `XrdPfcInfo.hh`, `XrdPfcStats.hh`, `XrdOucCache.hh`, and `XrdOucIOVec.hh`. It forward-declares `IO` and callback types to avoid circular includes. It is the primary contract between `Cache`, `IOFile`, `IOFileBlock`, remote `XrdOucCacheIO`, and resource monitoring.

## Risks and Test Signals
The main risks are ownership ambiguity for `ReadReqRH` and `ReadRequest`, callback ordering, and refcount misuse. Tests should stress callback completion ordering, block free after write queue removal, detach while reads/prefetches are active, and all paths where `ReadRequest::is_complete()` transitions from false to true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.cc

## Purpose
Implements `FsTraversal`, a cache-local namespace walker used by resource monitoring and purge code. It opens directories through `XrdOss`/`XrdOssAt`, maintains current traversal state, identifies subdirectories, and pairs data files with matching `.cinfo` files.

## Important APIs, Types, and Functions
- Constructor stores the `XrdOss` reference and initializes `XrdOssAt`.
- `begin_traversal(DirState*, root_path)` enables DirState maintenance, then opens and slurps the root.
- `begin_traversal(root_path)` opens a root directory and initializes path/level/handle stack.
- `end_traversal()` closes all directory handles and clears traversal state.
- `cd_down()` opens a child directory relative to the current handle, updates path/depth, optionally advances `DirState`, and slurps entries.
- `cd_up()` closes the current handle and restores parent state.
- `slurp_dir_ll()` reads directory entries and populates `m_current_dirs` and `m_current_files`.

## Control Flow
Traversal is stack-based. `begin_traversal` opens the first directory and calls `slurp_current_dir`. Recursive callers consume `m_current_dirs`, call `cd_down`, process that directory, and call `cd_up`. `slurp_dir_ll` clears prior entry buffers, loops over `Readdir`, skips `.`/`..` and transient `-ENOENT`, skips configured protected top-level dirs at relative level zero, and groups non-directory names by stripping `.cinfo` extension into `FilePairStat`.

## State and Persistence Behavior
No persistent state is written. Runtime state includes directory handles, current path with trailing slash, relative depth, current file/dir vectors, optional `DirState` cursor, and protected top-level directory names. The walker reports observed `stat` metadata to callers but does not delete or modify files itself except through exposed `unlink_at`.

## Dependencies and Integration Points
Depends on `XrdPfcDirState`, `XrdPfc::Cache` trace access, `Info::s_infoExtension`, `XrdOss`, `XrdOssAt`, and `XrdOucEnv`. `ResourceMonitor` uses it for initial scans and out-of-band LFN checks; purge-related code can use `open_at_ro`/`unlink_at` helpers.

## Risks and Test Signals
Risks include relying on `StatRet`/`Readdir` behavior for file type and stat data, fixed 256-byte entry buffer, path erasure assumptions with trailing slashes, and unclosed handles if callers skip `end_traversal`. Tests should cover empty dirs, protected top dirs, files with data only, `.cinfo` only, matching pairs, nested traversal, and failed `Opendir`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.hh

## Purpose
Declares the filesystem traversal helper used to inspect the cache namespace through the XRootD OSS abstraction. It provides mutable traversal state that callers can consume while recursively walking directories.

## Important APIs, Types, and Functions
- `FilePairStat`: stores `stat` for a data file and its `.cinfo` partner plus `has_data`/`has_cinfo` flags.
- `begin_traversal`, `end_traversal`, `cd_down`, and `cd_up`: traversal lifecycle and navigation.
- `open_at_ro`, `unlink_at`, and `close_delete`: relative file operations against the current directory handle.
- Public buffers `m_current_dirs` and `m_current_files`: caller-visible results from the most recent slurp.
- `m_protected_top_dirs`: names skipped at root depth.

## Control Flow
The class is intentionally stateful: callers begin at a root, inspect the current buffers, descend using `cd_down`, and return with `cd_up`. When constructed with a `DirState` root, directory navigation mirrors into `m_dir_state`.

## State and Persistence Behavior
The class persists no data. It owns open directory handles during traversal and exposes current path/depth and current directory contents. `unlink_at` can delete files if callers choose to use it, so consumers must ensure purge/consistency policy before invoking it.

## Dependencies and Integration Points
Includes `XrdOssAt` for relative operations and `XrdOucEnv` for OSS calls. Forward-declared `DirState` allows integration with the resource monitor tree without making traversal own directory accounting.

## Risks and Test Signals
Because the result buffers are public and reused, consumers must copy/swap them before reentrant or out-of-band slurps. Tests should verify stack depth handling, current path formatting, relative open/unlink behavior, and correct `FilePairStat` pairing semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFsTraversal.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.cc

## Purpose
Implements the base cache IO adapter that wraps an upstream `XrdOucCacheIO`, exposes common path/location/update behavior, and implements delayed detach scheduling shared by concrete cache IO types.

## Important APIs, Types, and Functions
- `IO::IO()` stores cache reference, trace id, active read counter, upstream IO pointer, and read sequence id.
- `Update()` atomically replaces the upstream IO, refreshes remote location, and logs the new source location.
- `SetInput()`/`GetInput()` manage the atomic input pointer.
- `GetFilename()` converts the upstream URL path into a local filename path via `XrdCl::URL`.
- `Detach()` finalizes immediately when `ioActive()` is false or schedules a nested `FutureDetach` job that polls with exponential backoff up to 120 seconds.

## Control Flow
Concrete `IO` subclasses implement `ioActive()` and `DetachFinalize()`. `Detach()` asks whether reads, prefetches, or blocks still need the object. If not active, it calls finalization and returns true. If active, it schedules `FutureDetach`, returns false, and the job repeatedly rechecks activity before finalizing and invoking `DetachDone()`.

## State and Persistence Behavior
No persistent state is owned. Transient state includes the upstream IO pointer, active read request counter, sequence ids, attach/detach state fields used by `File`, prefetch permissions, and error/incomplete-read counters for diagnostics.

## Dependencies and Integration Points
Depends on `XrdPfcIO.hh`, trace macros, `XrdCl::URL`, `Cache::schedP`, and `XrdJob`. Concrete integrations are `IOFile` and `IOFileBlock`, both of which delegate actual cache state to `File`.

## Risks and Test Signals
Risks include lifetime of the detach callback captured by `FutureDetach`, polling delay during shutdown, and upstream IO replacement while reads are active. Tests should cover immediate detach, delayed detach with active reads, Update during an open file, and callback completion exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.hh

## Purpose
Declares `XrdPfc::IO`, the abstract base class for proxy-cache `XrdOucCacheIO` adapters. It supplies common unsupported write/truncate behavior, source-path access, detach splitting, remote input management, read sequence ids, and shared counters.

## Important APIs, Types, and Functions
- Overrides `Path`, `Sync`, `Trunc`, `Write`, `Update`, and final `Detach`.
- Abstract `ioActive()` and `DetachFinalize()` define subclass-specific lifetime checks and destruction.
- `GetLocation()`, `GetTrace()`, `GetInput()`, `GetFilename()`, and `RefreshLocation()` expose upstream/cache context.
- `ReadReqRHCond` adapts `ReadReqRH` into a synchronous condition-variable callback.
- Friend relationship with `File` allows `File` to manage attach time, prefetch state, and detach flags under its own lock.

## Control Flow
Subclasses inherit the XRootD cache IO interface and implement read/stat behavior. Base `Detach()` centralizes delayed finalization so subclasses only answer whether active work remains and how to release their `File` references.

## State and Persistence Behavior
State is runtime-only: `m_io` points to the current upstream IO, `m_active_read_reqs` counts synchronous/asynchronous read operations, `m_read_seqid` tags logs, and detach/prefetch fields are managed by `File`. No disk state is written here.

## Dependencies and Integration Points
Depends on `XrdOucCache.hh`, `XrdSysRAtomic`, `XrdPfc.hh`, and `ReadReqRH` from `XrdPfcFile.hh` indirectly through include order. It is the common contract for `IOFile` and `IOFileBlock` and bridges XRootD cache APIs into PFC internals.

## Risks and Test Signals
Risks include abstract class coupling to `File` private state, atomic pointer assumptions, and unsupported write/truncate expectations. Tests should ensure write/truncate callers receive `-ENOTSUP`, sequence ids advance, and detach behavior is uniform across subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIO.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.cc

## Purpose
Implements `IOFile`, the standard whole-file proxy-cache adapter. It obtains a shared `File` for the upstream path, validates read bounds, converts sync/async XRootD cache reads into `File` calls, handles page-read checksum calculation, and releases the `File` at detach.

## Important APIs, Types, and Functions
- Constructor calls `Cache::GetInstance().GetFile(GetFilename(), this)`.
- `Fstat()` uses `initialStat()` during construction before `m_file` exists, otherwise delegates to `File::Fstat`.
- `initialStat()` obtains file size from existing local `.cinfo` or upstream `Fstat`.
- `Read()` and async `Read()` allocate `ReadReqRH` wrappers, call `ReadBegin`, wait/callback as needed, then call `ReadEnd`.
- `pgRead()` optionally calculates checksums for forced checksum reads after the data result.
- `ReadV()` and async `ReadV()` mirror the single-read flow for vector reads.
- `ioActive()` and `DetachFinalize()` delegate lifetime and release to `File`.

## Control Flow
Construction attaches to or creates the shared `File`. Each read increments `m_active_read_reqs`, bounds-checks against `FSize()`, sets `m_expected_size`, and delegates to `File`. If `File` returns `-EWOULDBLOCK`, synchronous callers wait on a condition and asynchronous callers return until callback. `ReadEnd` logs short reads/errors, forwards to the external callback, deletes the internal handler, and decrements the active counter.

## State and Persistence Behavior
`IOFile` itself persists nothing. It owns a `File*` reference released through `Cache::ReleaseFile`. Persistent data and `.cinfo` updates are handled by `File`. Error counts and incomplete-read counts are accumulated for detach-time logging.

## Dependencies and Integration Points
Depends on `XrdPfcIOFile.hh`, `Stats`, trace macros, `XrdOss`, `XrdSfs`, `XrdOucEnv`, and `XrdOucPgrwUtils`. It is the concrete adapter used when the cache stores the remote object as one local file.

## Risks and Test Signals
Risks include active read counter balance on all early-return paths, validating `ReadV` chunks against EOF, and `pgRead` lambda lifetime around `csvec`. Tests should cover zero-length/EOF reads, negative offsets, short upstream file size, sync and async callback paths, and `initialStat()` fallback from `.cinfo` to upstream stat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.hh

## Purpose
Declares `IOFile`, the whole-file cache IO implementation. It adapts the XRootD cache interface to the shared `File` object that stores a remote file in one local data file plus `.cinfo`.

## Important APIs, Types, and Functions
- `HasFile()`, `Fstat()`, and `FSize()` expose file availability and size/stat information.
- Overrides sync/async `Read`, `pgRead`, sync/async `ReadV`, `Update`, `ioActive`, and `DetachFinalize`.
- Private `ReadBegin`/`ReadEnd` and `ReadVBegin`/`ReadVEnd` centralize validation, expected-size tracking, callback forwarding, and active-read accounting.
- `initialStat()` is used during file acquisition to resolve size from local metadata or upstream IO.

## Control Flow
Public read methods create an internal response handler and call the begin/end helper pair. `Update` refreshes the base upstream IO and informs the `File` so remote location metadata remains current. Detach checks are delegated to `File::ioActive`.

## State and Persistence Behavior
Only runtime state is `File *m_file`. The pointed-to `File` owns persistence and metadata state. `IOFile` lifetime is tied to detach finalization.

## Dependencies and Integration Points
Includes `XrdPfcIO.hh`, `XrdPfc.hh`, `Stats`, and `XrdPfcFile.hh`. It is used by the proxy cache attach path for normal non-HDFS/block-split objects.

## Risks and Test Signals
Risks are mostly lifecycle-related: null `m_file`, duplicate finalization, read callbacks after detach, and construction-time `Fstat` behavior. Tests should include failed `GetFile`, detach during async read, and Update propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.cc

## Purpose
Implements the older block-file cache mode where one logical remote object is split across multiple local `File` objects, each representing an HDFS-style block. It maintains a top-level `.cinfo` for logical file size and lazily creates block files as read ranges touch them.

## Important APIs, Types, and Functions
- Constructor initializes `m_blocksize` from configuration or `hdfsbsize=` URL parameter and calls `initLocalStat()`.
- `initLocalStat()` reads an existing top-level `.cinfo` for file size or queries upstream `Fstat` and writes a new top-level `.cinfo`.
- `newBlockFile()` builds names of the form `<origpath>___<blocksize>_<offset>` and asks `Cache::GetFile` for a `File`.
- `Read()` splits the user range across logical blocks, gets/creates each block `File`, performs synchronous block reads, and falls back to upstream direct reads if block file creation failed.
- `Update()`, `ioActive()`, and `DetachFinalize()` iterate over all block `File` objects.
- `CloseInfoFile()` writes top-level access stats and closes the logical `.cinfo`.

## Control Flow
Read flow clamps to logical file size, computes first/last block, obtains the per-block `File` under `m_mutex`, adjusts per-block read size for edge blocks, performs a synchronous `File::Read` using an internal condition handler, then advances the output buffer and logical offset. A partial non-error block read is treated as `-EIO`; a negative read result is propagated.

## State and Persistence Behavior
Persistent state includes the top-level `.cinfo` for logical file size and per-block data/metadata files named with size/offset suffixes. Runtime state includes `m_blocks`, `m_localStat`, `m_info`, and `m_info_file`. Per-block persistence is delegated to each `File`.

## Dependencies and Integration Points
Depends on `Cache`, `File`, `Info`, `Stats`, `XrdOss`, `XrdSfs`, `XrdOucEnv`, and trace macros. It integrates with the same `File`/`Cache` machinery as whole-file mode but adds a map of block `File` references.

## Risks and Test Signals
Risks include non-obvious offset semantics when calling `fb->Read(this, buff, off, readBlockSize, ...)`, storing null `File*` in the block map after local open failure, memory ownership of `m_localStat`, and top-level `.cinfo` consistency versus per-block files. Tests should read ranges spanning first/middle/last blocks, simulate failed block-file open fallback, check detach releases every block, and restart from top-level `.cinfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.hh

## Purpose
Declares `IOFileBlock`, the block-splitting cache IO adapter. It is intended for configurations that store a logical remote object as multiple local cache files, each backed by a shared `File`.

## Important APIs, Types, and Functions
- Overrides `ioActive`, `DetachFinalize`, `Read`, `Fstat`, `FSize`, and `Update`.
- `m_blocksize`: logical split size.
- `m_blocks`: map from block index to lazily created `File*`.
- `m_localStat`, `m_info`, and `m_info_file`: logical file stat/metadata state.
- Private helpers parse block size from path, initialize local stat, create block files, and close the top-level info file.

## Control Flow
Callers use the same XRootD cache IO API as `IOFile`, but reads are internally divided into per-block `File` reads. Update and detach walk all block files under a mutex.

## State and Persistence Behavior
The adapter owns a logical `.cinfo` plus a runtime map of block files. Each block file has its own persistence through `File`. The top-level stat is cached in `m_localStat`.

## Dependencies and Integration Points
Depends on `XrdOucCache`, `XrdPfcIO`, `Info`, and `File` implementation details. It integrates with `Cache::GetFile` using generated block-suffixed filenames.

## Risks and Test Signals
The class is older and has comments questioning mutex necessity and suggesting `IOFileBlock` should be ditched. Tests should focus on thread safety of `m_blocks`, logical stat correctness, and compatibility with `File` offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.cc

## Purpose
Implements `.cinfo` metadata serialization for cached files. It records block size, file size, creation time, checksum policy/state, synced block bitmap, prefetch bitmap, and compacted access records, with compatibility readers for older metadata versions.

## Important APIs, Types, and Functions
- `Info::Write()` writes version 4 metadata: version, `Store`, store CRC32C, synced bitmap, access records, and combined bitmap/access CRC32C.
- `Info::Read()` reads v4 or dispatches to `ReadV2`/`ReadV3`, validates checksums, copies synced bitmap to written bitmap, and recomputes completion.
- `ResizeBits()` allocates and zeroes written/synced/prefetch bitmaps based on file size and buffer size.
- `SetBufferSizeFileSizeAndCreationTime()` initializes new metadata.
- `ResetCkSumCache()`/`ResetCkSumNet()` downgrade checksum state and set no-checksum timestamp.
- `CompactifyAccessRecords()` merges access records when exceeding `s_maxNumAccess`.
- `WriteIOStatAttach`, `WriteIOStat`, `WriteIOStatDetach`, and `WriteIOStatSingle` update access history.
- `ReadV2()` and `ReadV3()` read legacy MD5-protected formats and translate access records.

## Control Flow
New metadata initialization sets sizes, allocates bitmaps, and records creation time. Writes compact access records, update astat size, and emit checksummed sections. Reads first load the version; v4 validates `Store` checksum before allocating bitmaps, then validates synced bitmap plus access records. Legacy readers load size/bitmap/MD5, then tolerate truncated or corrupt trailing access records by reading until failure and skipping invalid entries.

## State and Persistence Behavior
The persistent `.cinfo` v4 format intentionally stores the synced bitmap, not merely the written bitmap, so restart does not trust blocks written after an incomplete fsync. `m_buff_written` is runtime download state, `m_buff_synced` is durable state, and optional `m_buff_prefetch` stores prefetch-source stats. Access records are persisted and compacted to a configured maximum.

## Dependencies and Integration Points
Depends on `XrdOssDF` positional IO, `XrdOucCRC32C`, `XrdCksCalcmd5`, `XrdPfcStats`, `Cache` configuration for checksum tests, and trace macros. `File`, `IOFileBlock`, purge state, print tooling, and resource monitoring consume `Info`.

## Risks and Test Signals
Risks include unchecked allocation failures, division by zero if buffer size is invalid, metadata endianness/ABI assumptions from raw struct serialization, and compatibility with partially written `.cinfo`. Tests should cover v4 checksum mismatch, v2/v3 migration, access compaction boundaries, incomplete fsync recovery, checksum downgrade timestamps, and empty/tiny file edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.hh

## Purpose
Declares `Info`, the in-memory representation and serializer for proxy-cache metadata files. It defines the persistent `Store` structure, access-stat records, block-state bitmaps, checksum-state helpers, and public metadata operations.

## Important APIs, Types, and Functions
- `Status`: bitfield storing `CkSumCheck_e` state.
- `AStat`: one access record with attach/detach time, IO count, duration, merge count, and hit/miss/bypass bytes.
- `Store`: persistent header with buffer size, file size, creation/no-checksum time, access count, status, and access vector size.
- Bit APIs: `SetBitWritten`, `TestBitWritten`, `SetBitSynced`, `SetAllBitsSynced`, `SetBitPrefetch`, `TestBitPrefetch`.
- Size/completion APIs: `ResizeBits`, `GetNBlocks`, `IsComplete`, `UpdateDownloadCompleteStatus`, `GetExpectedDataFileSize`.
- Serialization APIs: `Read`, `Write`, checksum calculators, v2/v3 readers.
- Access APIs: `WriteIOStat*`, `CompactifyAccessRecords`, `GetLatestDetachTime`, `GetLastAccessStats`.

## Control Flow
`File` uses the class by initializing sizes, marking blocks written/synced as data is downloaded and fsynced, then writing metadata. Restart paths read metadata, validate checksums, reconstruct written state from synced state, and use completion/expected-size helpers to decide whether local data is usable.

## State and Persistence Behavior
`Store`, synced bitmap, and access records are persisted. Written and prefetch buffers are runtime state, although prefetch bits can be used while the `Info` object lives. Static `s_infoExtension` defines `.cinfo`, and `s_maxNumAccess` bounds access history persistence.

## Dependencies and Integration Points
Depends on `XrdPfcTypes.hh`, `Stats`, `XrdOssDF`, `XrdCksCalc`, and `XrdSysTrace`. It is consumed by `File`, `IOFile`, `IOFileBlock`, `FsTraversal`, purge, and print tooling.

## Risks and Test Signals
Risk areas are inline bit operations relying on assertions, off-by-one in block count and expected data size, and raw serialized struct compatibility. Tests should exercise bitmaps around byte boundaries, last partial block, complete/incomplete transitions, and access record merge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPathParseTools.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPathParseTools.hh

## Purpose
Provides small path/string tokenization helpers used by resource-monitor code to map LFNs onto directory-state trees without pulling in heavier parser dependencies.

## Important APIs, Types, and Functions
- `SplitParser`: owns a duplicated mutable string and tokenizes it with C delimiter functions.
- `get_token()`, `get_token_as_string()`, `get_reminder()`, and `get_reminder_with_delim()` expose token stream and remaining suffix.
- `pre_count_n_tokens()` counts remaining tokens for reserve sizing.
- `PathTokenizer`: private `SplitParser` subclass that extracts directory components and a remainder from a path.
- `PathTokenizer::make_path()` reconstructs a slash-prefixed path from parsed components.

## Control Flow
`PathTokenizer` initializes a delimiter parser over `/`, optionally caps directory extraction by `max_depth`, optionally treats the last token as file remainder for LFNs, and stores pointers into the duplicated string. Consumers query directory count and individual directory names.

## State and Persistence Behavior
No persistent state. The tokenizer stores pointers into `SplitParser::f_str`; those pointers remain valid only while the tokenizer object lives.

## Dependencies and Integration Points
Uses only C/C++ standard string/vector and `strdup`/`free`/`strspn`/`strpbrk`. It integrates with `ResourceMonitor` and `DirState` path lookup logic.

## Risks and Test Signals
Risks include the misspelled `get_reminder` API, pointer lifetime misuse, mutation of delimiter characters, and behavior with repeated/trailing slashes. Tests should cover root path, repeated separators, max depth, parse-as-LFN true/false, and reconstructing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPathParseTools.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.cc

## Purpose
Implements the `pfc_print` utility for inspecting `.cinfo` metadata files or recursively walking cache directories and printing metadata in human-readable or JSON form.

## Important APIs, Types, and Functions
- `Print::Print()` configures units/format and dispatches to file or directory printing.
- `isInfoFile()` identifies `.cinfo` suffixes.
- `printFileJson()` reads `Info` metadata and emits JSON with version, creation time, checksum state, file/block sizes, completion state, optional block array, no-checksum time, and access records.
- `printFile()` emits equivalent text tables.
- `printDir()` recursively traverses directories and prints `.cinfo` files.
- `main()` parses CLI options, loads OSS configuration through `XrdOfsConfigPI`, supports `root:/` path mapping via `oss.localroot`, and instantiates `Print` for each path.

## Control Flow
CLI parsing validates units and flags, optionally attaches a config file, suppresses OSS init logs, loads the OSS plugin, then processes each path. A path ending in `.cinfo` is opened as metadata; otherwise the utility opens a directory and recursively prints metadata files below it.

## State and Persistence Behavior
The utility is read-only from the cache metadata perspective. It opens `.cinfo` files read-only and creates temporary `Info` objects. Output goes to stdout. It does not mutate access times except through underlying filesystem read semantics.

## Dependencies and Integration Points
Depends on `Info`, `XrdOucStream`, `XrdOucArgs`, `nlohmann::json` via `XrdOucJson`, `XrdOfsConfigPI`, `XrdSysLogger`, and `XrdOss`. It is operational tooling for administrators and tests.

## Risks and Test Signals
Risks include `isInfoFile()` indexing before the start for paths shorter than six characters, not checking all open failures before `Info::Read`, recursive directory loops if OSS exposes unusual entries, and JSON percentage division by zero for zero-block files. Tests should cover CLI validation, short paths, unreadable `.cinfo`, verbose block output, JSON schema, and config-based `root:/` mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.hh

## Purpose
Declares the `Print` helper used by the `pfc_print` command-line utility. It encapsulates OSS access, output units, verbosity, JSON formatting, indentation, and recursive metadata printing.

## Important APIs, Types, and Functions
- Constructor `Print(XrdOss* oss, char u, bool v, bool j, int i, const char* path)` immediately prints the requested path.
- Private `isInfoFile`, `printFileJson`, `printFile`, and `printDir` implement dispatch and output.
- Members store OSS handle, environment, unit shift/width/name, format flags, JSON indent, and OSS user.

## Control Flow
The constructor is the entry point and dispatches based on whether the path is a `.cinfo` file. Directory recursion and file formatting are implementation details.

## State and Persistence Behavior
State is command-runtime only. No persistent data is written by this class.

## Dependencies and Integration Points
Depends on `XrdOucEnv`, forward-declared `XrdOss`, and `XrdOssDF`. It is coupled to `Info` in the implementation.

## Risks and Test Signals
Risks are limited to utility behavior: constructor side effects, fixed OSS user `"nobody"`, and suffix handling. Tests should instantiate against a fake or test OSS tree and validate both JSON and text outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurge.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurge.cc

## Purpose
Implements the legacy purge driver used by `ResourceMonitor` purge tasks. It builds purge candidate maps, optionally invokes a quota plugin, removes `.cinfo` and data files while respecting active/protected files, and reports purges back to resource monitoring.

## Important APIs, Types, and Functions
- `UnlinkPurgeStateFilesInMap(FPurgeState&, long long bytes_to_remove, const std::string& root_path)`: deletes oldest purge candidates until enough `st_blocks` are removed, skipping active or purge-protected files.
- `OldStylePurgeDriver(DataFsPurgeshot&)`: orchestrates plugin-driven per-directory purge and default namespace-wide purge.
- Uses `FPurgeState::TraverseNamespace()` and `MoveListEntriesToMap()` to gather candidates sorted by access time.

## Control Flow
`OldStylePurgeDriver` first asks a configured `PurgePin` for bytes to recover per directory and purges those directories. If space-based or age-based requirements remain, it creates a default `FPurgeState`, applies cold-file or uvkeep thresholds, traverses `/`, and deletes enough candidates. `UnlinkPurgeStateFilesInMap` derives data paths from `.cinfo` paths, checks active/protected status, unlinks info then data, decrements target blocks, and registers file purges.

## State and Persistence Behavior
This code persistently deletes local cache data and `.cinfo` metadata. It also updates resource-monitor state via purge registration. Candidate maps are transient. Files are skipped when active or purge-protected.

## Dependencies and Integration Points
Depends on `Cache`, `DataFsPurgeshot`, `ResourceMonitor`, `FPurgeState`, `PurgePin`, `Info::s_infoExtensionLen`, `XrdOss`, and trace macros. It is scheduled asynchronously by `ResourceMonitor::perform_purge_check`.

## Risks and Test Signals
Risks include deleting metadata before data, stale candidate maps racing with opens, path derivation by stripping `.cinfo`, and accounting mismatch if unlink/stat fails. Tests should cover active-file protection, quota plugin paths, age-based purge markers, uvkeep thresholds, failed traversal, missing data/info pairs, and resource-monitor purge accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurge.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgePin.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgePin.hh

## Purpose
Declares the purge plugin interface. `PurgePin` allows external policy code to request per-directory byte recovery based on a resource-monitor purge snapshot.

## Important APIs, Types, and Functions
- `DirInfo`: plugin result/config record with directory path, byte quota, bytes to recover, and an internal `DirUsage` pointer.
- `CallPeriodically()`: indicates whether the plugin wants to be invoked even without space/age pressure; default true.
- Pure virtual `GetBytesToRecover(const DataFsPurgeshot&)`: fills recovery needs and returns total bytes to remove.
- `ConfigPurgePin(const char*)`: optional configuration parser, default success.
- `refDirInfos()`: mutable access to directory recovery list consumed by purge driver.

## Control Flow
The cache loads or owns a `PurgePin`, configures it, and during purge checks calls `GetBytesToRecover`. The old purge driver then iterates `refDirInfos()` and purges each requested directory.

## State and Persistence Behavior
`PurgePin` stores in-memory policy/output list only. Persistent deletion is performed by the purge driver, not by the interface.

## Dependencies and Integration Points
Forward-depends on `DataFsPurgeshot` and `DirUsage`. Implementations must be ABI-compatible with the cache plugin loader; `XrdPfcPurgeQuota.cc` is one implementation.

## Risks and Test Signals
Risks include plugin-provided paths outside intended cache scope, stale `DirUsage*` pointers after a purge snapshot, and default periodic invocation causing unexpected purge scans. Tests should validate plugin configuration, snapshot lookup failures, and empty/zero recovery lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgePin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgeQuota.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgeQuota.cc

## Purpose
Implements a `PurgePin` plugin that enforces directory byte quotas from a configuration file. It computes bytes to recover for each configured directory by comparing snapshot usage with configured quotas.

## Important APIs, Types, and Functions
- `class XrdPfcPurgeQuota : public XrdPfc::PurgePin`.
- `InitDirStatesForLocalPaths()` resolves each configured path to a `DirUsage` entry in the purge snapshot.
- `GetBytesToRecover()` computes `512 * st_blocks - quota` for each directory and returns total positive excess.
- `ConfigPurgePin()` parses a quota file where each line contains a directory path and quota, accepting size suffixes through `XrdOuca2x::a2sz`.
- `extern "C" XrdPfcGetPurgePin()` exports the plugin factory.

## Control Flow
Configuration opens the quota file, captures plugin-specific config lines, reads path/quota pairs, converts quota values, and appends `DirInfo` records. During purge, snapshot lookup populates `dirUsage`; missing dirs log errors and are skipped; excess bytes become `nBytesToRecover` for the old purge driver.

## State and Persistence Behavior
The plugin stores configured quotas in memory. It does not delete files directly. Persistent effects occur when `OldStylePurgeDriver` consumes the computed recovery list.

## Dependencies and Integration Points
Depends on `PurgePin`, `DataFsPurgeshot`, `XrdOucEnv`, `XrdOucStream`, `XrdOuca2x`, and `XrdSysError` logging. It integrates as a dynamically loaded purge plugin through `XrdPfcGetPurgePin`.

## Risks and Test Signals
Risks include continuing after quota file open failure, accepting invalid or duplicate paths, units conversion ambiguity, and quota paths not found in the snapshot. Tests should cover missing file, malformed lines, suffix and raw integer quotas, missing directories, and multiple quotas summing recovery bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgeQuota.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.cc

## Purpose
Implements `ResourceMonitor`, the background monitor for proxy-cache directory usage, per-file access stats, snapshots, and purge scheduling. It builds an initial `DirState` tree, ingests event queues from active files, writes directory-stat snapshots, computes purge needs, and schedules purge jobs.

## Important APIs, Types, and Functions
- `CrossCheckIfScanIsInProgress()` blocks file opens during initial namespace scan until their directory has been checked.
- `perform_initial_scan()` traverses the OSS namespace, builds baseline usage, handles pending open requests, and propagates initial usage upward.
- `process_queues()` swaps producer queues and applies open/update/close/purge records to `DirState`.
- `heart_beat()` is the infinite scheduler loop for queue processing, filesystem state updates, snapshot writing, and purge checks.
- `fill_sshot_vec_children()` and `fill_pshot_vec_children()` serialize `DirState` tree views into snapshot vectors.
- `update_vs_and_file_usage_info()` refreshes data/meta space totals and current file usage.
- `get_file_usage_bytes_to_remove()` computes bytes to remove from configured file-usage and disk-usage watermarks.
- `perform_purge_check()` creates `DataFsPurgeshot`, decides whether purge is required, and schedules an async purge job.
- `perform_purge_task()` runs `OldStylePurgeDriver`; cleanup marks purge completion and clears protection.

## Control Flow
Startup calls `init_before_main`, then `main_thread_function` performs an initial scan and processes queued open/update events that occurred during scanning. The heartbeat then sleeps until the nearest scheduled event, always processes queues, updates disk usage, optionally updates and resets directory stats, writes `/pfc-stats/DirStat.json`, and performs purge checks. Purge tasks run in scheduler jobs and communicate completion back through `m_purge_task_cond`.

## State and Persistence Behavior
The monitor owns `DataFsState`, access-token tables, write/read queues, current file usage in `st_blocks`, scan coordination lists, and purge-task status. It writes directory-stat JSON snapshots through OSS when enabled and updates in-memory directory usage/stat trees. Purge tasks persistently delete cache files indirectly through `OldStylePurgeDriver`.

## Dependencies and Integration Points
Depends on `Cache`, `FsTraversal`, `DirState`, snapshot/purgeshot structures, `PurgePin`, `XrdOss`, and trace macros. `File` calls `register_file_open`, `register_file_update_stats`, `register_file_close`, and purge registration methods. Purge code reports deletions back to this monitor.

## Risks and Test Signals
High-risk areas are scan/open coordination, token reuse, queue swap/update ordering, directory pointer validity during purge, fatal `_exit(1)` on `StatVS` failure, and purge scheduling while a prior task is active. Tests should simulate opens during initial scan, high-volume stat updates coalescing by token, purge records by pointer/path/LFN, snapshot vector parent ranges, watermark calculations, and purge task lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.hh

## Purpose
Declares the resource-monitor subsystem for proxy-cache usage accounting and purge decisions. It defines event queues, access tokens, scan coordination, registration APIs called by `File`, and heartbeat/purge helpers.

## Important APIs, Types, and Functions
- Template `Queue<ID, RECORD>` provides producer write queue, consumer read queue, atomic-ish swap, and shrink helpers under external locking.
- `AccessToken` ties a file open to filename, last stats queue position, swap generation, and resolved `DirState`.
- `OpenRecord`, `CloseRecord`, and `PurgeRecord` are queue payloads.
- Registration APIs: `register_file_open`, `register_file_update_stats`, `register_file_close`, `register_file_purge`, and multi-file purge variants.
- Actions: `process_queues`, `heart_beat`, `perform_initial_scan`, `scan_dir_and_recurse`, `perform_purge_check`, `perform_purge_task`, and cleanup.
- Scan coordination: `CrossCheckIfScanIsInProgress` and `m_dir_scan_open_requests`.

## Control Flow
File objects register events into queues under `m_queue_mutex`. The heartbeat swaps queues, increments `m_queue_swap_u1`, and consumes records in open, update, close, purge order. Initial scan coordination lets file opens wait while their directory is checked or later released after scan completion.

## State and Persistence Behavior
Persistent state is indirect: the monitor may write snapshot files and schedule purges. In-memory state includes `DataFsState`, access-token freelist, event queues, current usage, scan flags, and purge task timestamps/flags.

## Dependencies and Integration Points
Depends on `XrdPfcStats`, `XrdSysPthread`, `XrdOss`, and forward-declared directory/snapshot/purge structures. It is tightly integrated with `File`, `Cache`, `FsTraversal`, and purge plugin flows.

## Risks and Test Signals
Risks include token vector growth/reuse bugs, queue iterator constness oddities, stats updates before open resolution, and stale `DirState*` in purge records. Tests should validate queue coalescing, token release on close, scan wait signaling, and purge active/complete flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcResourceMonitor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcStats.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcStats.hh

## Purpose
Defines lightweight statistics containers for cache-file and directory-level accounting. `Stats` tracks IO/read/write/checksum counters; `DirStats` extends it with directory/file lifecycle and purge counters.

## Important APIs, Types, and Functions
- `Stats` fields: IO count, duration, bytes hit/missed/bypassed/written, `st_blocks` added, and checksum errors.
- `AddReadStats`, `AddBytesHit`, `AddWriteStats`, `IoAttach`, `IoDetach`, `BytesRead`, `BytesReadAndWritten`, `DeltaToReference`, `AddUp`, and `Reset`.
- `DirStats` adds removed blocks, opened/closed/created/removed file counts, and created/removed directory counts, with matching `DeltaToReference`, `AddUp`, and `Reset`.

## Control Flow
`File` accumulates `Stats` deltas and full stats, then reports them to `ResourceMonitor`. `ResourceMonitor` aggregates them into `DirState` and computes deltas/resets for reporting intervals.

## State and Persistence Behavior
The classes are plain in-memory counters. Their values are copied into `.cinfo` access records and directory snapshots by other code, but this header does not perform persistence.

## Dependencies and Integration Points
No external includes beyond namespace. Used by `File`, `Info`, `ResourceMonitor`, directory-state snapshots, and IO adapters.

## Risks and Test Signals
Risks include signed counter underflow in `DeltaToReference` if reference/current order is wrong, long-running counter overflow, and confusion between bytes and 512-byte `st_blocks`. Tests should cover add/reset/delta semantics and aggregation into access records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTrace.hh

## Purpose
Defines trace levels and trace macros for the proxy file cache. It centralizes log-level labels, error-string formatting, IO path obfuscation, and compile-out behavior when `NODEBUG` is defined.

## Important APIs, Types, and Functions
- Trace numeric levels `TRACE_None` through `TRACE_DumpXL` and string constants.
- `trace_what_strings[]` external declaration for dynamic integer trace levels.
- `ERRNO_AND_ERRSTR(err_code)` helper.
- `TRACE`, `TRACE_INT`, `TRACE_TEST`, `TRACE_PC`, `TRACEIO`, `TRACEF`, and `TRACEF_INT` macros.

## Control Flow
Macros check `XRD_TRACE What` against the requested level and call `SYSTRACE` with `m_traceID`. IO/file variants append obfuscated remote paths or local cache paths. `TRACE_PC` executes caller-supplied pre-code only when the trace level is enabled.

## State and Persistence Behavior
No persistent state. Runtime behavior depends on the current `XrdSysTrace` object returned by `GetTrace()` or a custom `XRD_TRACE` definition.

## Dependencies and Integration Points
Depends on `XrdSysTrace`, `XrdSysE2T`, and XrdOuc obfuscation helpers. Every traced class must expose `m_traceID` and `GetTrace()` compatible with these macros.

## Risks and Test Signals
Risks include macro side effects, `TRACE_INT` indexing invalid levels, compile errors in `NODEBUG` because not every macro has a stub (`TRACE_INT`/`TRACE_TEST` are not stubbed here), and reliance on local `m_traceID`. Tests are mostly compile-configuration tests with/without `NODEBUG` and runtime log-level filtering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTypes.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTypes.hh

## Purpose
Defines shared simple types for the proxy file cache, currently checksum policy flags and checksum-vector storage.

## Important APIs, Types, and Functions
- `enum CkSumCheck_e`: checksum states `CSChk_Unknown`, `CSChk_None`, `CSChk_Cache`, `CSChk_Net`, `CSChk_Both`, and configuration-only `CSChk_TLS`.
- `typedef std::vector<uint32_t> vCkSum_t`: checksum vector used by page read/write paths.

## Control Flow
No functions or control flow. The enum is consumed by configuration, `Info`, and `File` to decide whether to request network checksums, write cache checksums, or downgrade metadata state.

## State and Persistence Behavior
`CkSumCheck_e` values are persisted inside `Info::Status` bitfields in `.cinfo`; `vCkSum_t` is transient per block/read.

## Dependencies and Integration Points
Depends on `<cstdint>` and `<vector>`. Included by `Info`, `File`, and checksum-related cache code.

## Risks and Test Signals
Risks include treating `CSChk_TLS` as a persistent state even though the comment says it is configuration-only, and bitfield width compatibility with negative `CSChk_Unknown`. Tests should cover enum serialization through `Info` and configuration downgrade logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcTypes.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdPosix/CMakeLists.txt

## Purpose
Defines the CMake build targets for XRootD POSIX client libraries: the main `XrdPosix` shared library and the `XrdPosixPreload` shared library used for preload/interposition.

## Important APIs, Types, and Functions
- `add_library(XrdPosix SHARED ...)` compiles POSIX admin, cache, callback, config, dir, file, object, prep IO, stats, trace, and xrootd path/source files.
- `target_link_libraries(XrdPosix PRIVATE XrdCl XrdUtils ${CMAKE_THREAD_LIBS_INIT})`.
- `set_target_properties(XrdPosix PROPERTIES SOVERSION ... VERSION ...)`.
- `add_library(XrdPosixPreload SHARED ...)` builds preload/linkage sources.
- `target_link_libraries(XrdPosixPreload PRIVATE XrdPosix ${CMAKE_DL_LIBS})`.
- `install(TARGETS XrdPosix XrdPosixPreload LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})`.

## Control Flow
Build flow first defines the main POSIX shared library and links it against client/utils/thread libraries. It then defines the preload shared library that links to `XrdPosix` and dynamic loader libraries. Both targets receive version metadata and are installed as libraries.

## State and Persistence Behavior
CMake target state affects generated build system outputs and installed shared libraries. No runtime persistence is defined here.

## Dependencies and Integration Points
Integrates with top-level XRootD CMake variables `XRootD_VERSION_MAJOR`, `XRootD_LIBVERSION`, `CMAKE_THREAD_LIBS_INIT`, `CMAKE_DL_LIBS`, and `CMAKE_INSTALL_LIBDIR`. Source list integration determines which POSIX components participate in the library ABI.

## Risks and Test Signals
Risks include missing source/header entries after file renames, incorrect private link dependencies for downstream symbol resolution, and platform-specific preload/dl behavior. Build tests should compile both targets, inspect linked libraries, verify versioned sonames, and run install packaging checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/CMakeLists.txt -->
