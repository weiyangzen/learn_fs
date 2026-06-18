# subset-b-007949 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.hh

Purpose: declares `XrdOssSpace`, the static accounting interface used by the OSS cache layer to track per-space usage and quotas. The class models named spaces and byte totals for service, prestage, purge, admin, reserved, and additive categories.

Important APIs/types/functions: `sType`, `uEnt`, `Adjust(int/off_t/sType)`, `Adjust(const char*/off_t/sType)`, `Init()`, `Init(aPath,qFile,isSOL,us)`, `Quotas()`, `Unassign()`, and `Usage()` by group id or group name. Private helpers `Assign`, `findEnt`, `Readjust`, and `UsageLock` implement table management and synchronized usage-file access.

Control flow: the header exposes only contracts. Callers initialize the shared accounting files, assign or find a named entry, adjust byte counters as files are added/removed, and query totals. The `haveUsage` and `haveQuota` flags tell callers which backing features are active.

State and persistence behavior: state is static and process-global. `uData` and `uDvec` form an in-memory table capped by `DataSz/sizeof(uEnt)`, while `qFname`, `uFname`, `uUname`, file descriptor `aFD`, mtimes, free/fence cursors, and sync/adjust flags indicate persistent usage/quota files. `Solitary` controls whether one process owns the files.

Dependencies: forward-declares `XrdSysError`; implementation integrates with `XrdOssCache` via friendship and with filesystem locking and quota files elsewhere in XrdOss.

Integration points: `XrdOssCache` uses this class for cache-group usage accounting, quota decisions, and stat reports such as `StatLS`/`StatVS`.

Risks: fixed-size tables can overflow for many cache groups; stale file mtimes or failed locks can desynchronize counters; all state is static, so tests and multiple OSS instances need isolation. Byte adjustments must be paired with unlink/create paths or usage drifts.

Test signals: initialize with and without quota files, verify named/group-id `Usage`, exercise concurrent `Adjust`, overflow group count, stale usage-file reload, and quota-disabled behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.cc

Purpose: implements OSS staging from remote/mass storage to local disk. It supports queued staging through an external staging message program or FRC proxy, and real-time staging through internal priority queues and worker threads.

Important APIs/types/functions: `XrdOssSys::Stage`, `Stage_QT`, `Stage_RT`, `Stage_In`, `CalcTime`, `GetFile`, `getID`, `HasFile`, callback predicates `XrdOssFind_Prty` and `XrdOssFind_Req`, and the no-op scrub callback `XrdOssScrubScan`.

Control flow: `Stage()` dispatches to real-time or queued mode. Queued mode first checks `.fail` hold files, scrubs a path table, suppresses duplicate requests, optionally sends to `StageFrm`, otherwise formats a default or substituted stage message and feeds `StageProg`. Real-time mode rejects missing commands, deduplicates against `StageQ.fullList`, retries or holds failures, translates local/remote paths, stats remote size unless `XRDEXP_NOCHECK`, inserts a request into `fullList` and priority-ordered `pendList`, posts a semaphore, and returns an ETA. `Stage_In()` workers wait on `ReadyRequest`, pop pending requests, mark active, run `GetFile()` without holding the lock, update moving averages, delete successful requests, or mark failures with a hold timeout.

State and persistence behavior: global static queues, mutexes, semaphores, path hash tables, moving counters (`pndbytes`, `stgbytes`, `totbytes`, `totreqs`, `badreqs`), speed estimates, and failure hold timestamps drive runtime behavior. Persistent side effects are external: staged files appear on local storage, `.fail` files suppress retry loops, and external programs/scripts perform transfers.

Dependencies: `XrdOssApi`, `XrdOssOpaque`, `XrdOucEnv`, `XrdOucProg`, `XrdOucMsubs`, `XrdOucReqID`, `XrdFrcProxy`, local/remote name-to-name mappers, mass-storage `MSS_Stat`, and global `OssEroute`.

Integration points: called by OSS open/prepare paths when a file is remote. It bridges XRootD requests, FRC queues, external staging scripts, path translation, priority CGI variables, and cache accounting by delivering local files for later OSS operations.

Risks: queue state is shared across threads and lock scope is delicate; `req.path` is allocated before some early returns; external command output/return codes define correctness; `.fail` timestamps can suppress valid retries; ETA uses moving averages and can be inaccurate; real-time duplicate detection depends on hash plus string compare.

Test signals: queued duplicate suppression, `.fail` hold expiry, FRC and `StageProg` failures, priority ordering, worker success/failure state transitions, `XRDEXP_NOCHECK`, remote stat failures, and concurrency stress with multiple stage threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.hh

Purpose: declares `XrdOssStage_Req`, the queue node used by OSS real-time staging.

Important APIs/types/functions: flag macros `XRDOSS_REQ_FAIL`, `XRDOSS_REQ_ENOF`, and `XRDOSS_REQ_ACTV`; list members `fullList` and `pendList`; path hash, path, size, flags, signal/ETA time, and priority fields; static `StageMutex`, `ReadyRequest`, and sentinel `StageQ`.

Control flow: the constructor initializes both intrusive list nodes to point at the request and duplicates the path when provided. The sentinel constructor form points list nodes at another object. The destructor frees the path and removes the node from both intrusive lists, so deleting a request also unlinks it from queue state.

State and persistence behavior: request state is in memory only. It records whether a stage is pending, active, failed, or failed because the remote file is absent, plus byte size and ETA/failure hold time.

Dependencies: `XrdOucDLlist`, `XrdSysError`, `XrdSysPthread`, C time/stat types.

Integration points: consumed by `XrdOssStage.cc` worker and lookup predicates. The intrusive list behavior makes ownership and deletion the queue-management mechanism.

Risks: destructor side effects require all deletion to occur under `StageMutex`; copying is not disabled; a failed allocation in `strdup` leaves `path` null; default size is a large estimate that influences ETA before remote size is known.

Test signals: list insertion/removal invariants, destructor unlinking, duplicate lookup, active/failure flag transitions, and worker deletion under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStat.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStat.cc

Purpose: implements OSS stat and space-query operations for files, physical files, logical space, extended attributes, export attributes, and XML-like OSS statistics.

Important APIs/types/functions: `XrdOssSys::Stat`, `StatFS` overloads, `StatLS`, `StatPF`, `StatVS`, `StatXA`, `StatXP`, `getCname`, and `getStats`.

Control flow: `Stat()` translates LFN to local PFN when configured, invokes a stat plug-in or `stat`, masks write bits for read-only exports, optionally updates atime, and falls back to remote MSS stat when local ENOENT can mean offline data. `StatFS()` derives export flags from `PathOpts`, asks `XrdOssCache_FS` for free/total bytes, and formats protocol responses. `StatLS()` maps path/env to a cache group and formats CGI-style space data. `StatPF()` returns physical file stat or device/partition metadata. `StatVS()` optionally rescans cache state, returns aggregate or named-space totals, and can request partition vectors for `+space`. `StatXA()` emits logical attributes; `StatXP()` returns export option flags. `getStats()` formats path and space statistics for daemon monitoring.

State and persistence behavior: mostly read-only queries, except `Stat()` can mutate file atime with `utime()` and `StatVS(updt)` can trigger cache scans. Reported state comes from local files, remote MSS, cache group tables, quota/usage accounting, and path export options.

Dependencies: `XrdOssCache`, `XrdOssConfig`, `XrdOssOpaque`, `XrdOssPath`, `XrdOssSpace`, `XrdOucEnv`, `XrdOucName2Name`, `XrdOucPList`, stat plug-in hooks, and POSIX stat/utime.

Integration points: backs XRootD stat, query, filesystem, locate, and monitoring paths. It connects namespace translation, cache partition accounting, remote MSS presence, virtual-space API (`XrdOssVSInfo`), and optional stat plug-ins.

Risks: remote fallback relies on `errno` after plug-in/stat failures; formatted responses must fit caller buffers; atime updates are side effects in a stat path; cache stats can be stale without scans; `StatPF` intentionally bypasses the custom stat plug-in; `StatVS` partition vectors transfer ownership to callers.

Test signals: local hit/miss, remote offline hit, read-only bit masking, atime update, stat plug-in v1/v2 behavior, cache/no-cache `StatLS`, `+space` partition return, buffer truncation, and monitor stats sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStatInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStatInfo.hh

Purpose: defines the plug-in ABI for replacing or augmenting OSS stat behavior, including optional file-add/remove event relay for cmsd server mode.

Important APIs/types/functions: `XrdOssStatEvent::{FileAdded,PendAdded,FileRemoved}`, function pointer types `XrdOssStatInfo_t` and `XrdOssStatInfo2_t`, and initialization typedefs `XrdOssStatInfoInit_t` and `XrdOssStatInfoInit2_t`.

Control flow: the header describes two call forms. V1 receives path, stat buffer, options, and environment; V2 additionally receives the logical filename. For event relay, `buff == 0` signals a set/event operation rather than a query, and `opts` is one of the event constants.

State and persistence behavior: no local state. Plug-ins can read external metadata or update external state when event relay is enabled. Returned stat structures influence OSS file visibility and attributes.

Dependencies: forward declarations for `XrdOss`, `XrdOucEnv`, `XrdSysLogger`, and `struct stat`. Plug-ins are loaded through `oss.statlib` and must expose C linkage plus `XrdVERSIONINFO`.

Integration points: `XrdOssSys::Stat()` preferentially uses this ABI when configured. cmsd/xrootd/frm context is communicated through `XRDPROG` and `XRDROLE` environment variables.

Risks: ABI stability matters for external shared libraries; V1/V2 mismatch will fail initialization or pass incomplete context; return convention is `-1` with `errno`, unlike many internal XRootD APIs that return `-errno`; event return values are not inspected.

Test signals: load v1 and v2 plug-ins, verify logical-name parameter, failure errno propagation, arevents mode, version info enforcement, and environment context for cmsd/xrootd roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssStatInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssTrace.hh

Purpose: defines OSS trace flags and lightweight macros used throughout XrdOss for conditional tracing and debug output.

Important APIs/types/functions: flags `TRACE_ALL`, `TRACE_Opendir`, `TRACE_Open`, `TRACE_AIO`, `TRACE_Debug`; macros `QTRACE`, `TRACE`, `TRACEReturn`, `DEBUG`, and `EPNAME`.

Control flow: in non-`NODEBUG` builds, trace macros check `OssTrace.What` against the selected flag and route messages through `SYSTRACE` with `tident` and `epname`. In `NODEBUG` builds, the macros compile to no-ops or direct returns.

State and persistence behavior: no owned state; behavior depends on the global `OssTrace` object configured elsewhere. Trace output is persisted only if the process logger writes it.

Dependencies: `XrdSysTrace.hh` and, for debug builds, `XrdSysHeaders.hh`. Call sites must define visible `OssTrace`, `tident`, and `epname` as expected by the macro expansion.

Integration points: used by OSS operations such as unlink, open, directory, and async I/O paths to make runtime diagnostics conditional without per-call virtual dispatch.

Risks: macro expansion depends on names in caller scope; `TRACEReturn` changes control flow; debug logging can expose paths and identifiers; `NODEBUG` changes observability significantly.

Test signals: compile with and without `NODEBUG`, enable each trace flag via config, verify messages include endpoint names, and ensure `TRACEReturn` returns expected error codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssUnlink.cc -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssUnlink.cc

Purpose: implements OSS removal operations for files, directories, symlinks, and optional remote/MSS copies, including cache usage adjustment.

Important APIs/types/functions: `XrdOssSys::Remdir`, `XrdOssSys::Unlink`, and private `BreakLink`.

Control flow: `Remdir()` translates to a local path unless already a PFN, verifies the target is a directory, and delegates to `Unlink()`. `Unlink()` builds local and remote paths, enforces read-only checks for LFNs, handles ENOENT as success locally, breaks symlinks by deleting their target, removes directories with `rmdir`, unlinks files, adjusts cache usage by device or cache-group path, and then, when permitted, removes the remote copy with `MSS_Unlink`.

State and persistence behavior: deletes filesystem namespace entries and can delete remote mass-storage entries. It updates in-memory/cache usage through `XrdOssCache::Adjust`. Symlink handling can remove both the link target and usage for the backing cache object.

Dependencies: `XrdOssApi`, `XrdOssCache`, `XrdOssConfig`, `XrdOssOpaque`, `XrdOssPath`, `XrdOssTrace`, POSIX `lstat`, `stat`, `readlink`, `unlink`, `rmdir`, and global `OssEroute`/`OssTrace`.

Integration points: backs client remove/rmdir operations and cleanup paths. It cooperates with path export flags, name translation, cache layout conventions, and remote-storage commands.

Risks: `BreakLink()` trusts symlink contents enough to unlink the target; path buffers are fixed-size; remote deletion after local ENOENT can remove offline data unless `XRDOSS_Online` is set; cache accounting depends on stat size and cache layout suffix detection; `Check_RO` result is stored as `remotefs`, making option semantics subtle.

Test signals: remove file, directory, symlink target, missing local file, remote-only file, online-only removal, read-only export rejection, cache adjustment for old/new cache layouts, and remote `MSS_Unlink` ENOENT handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssUnlink.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssVS.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssVS.hh

Purpose: declares virtual-space result structures returned by `XrdOss::StatVS`.

Important APIs/types/functions: `XrdOssVSPart`, `XrdOssVSInfo`, and `XrdOssVSInfo::Export`.

Control flow: no runtime logic beyond constructors, destructor, and `Export()`. `Export()` transfers ownership of `vsPart` out of `XrdOssVSInfo`, clears the member, and returns the partition count.

State and persistence behavior: purely transient query result state. `XrdOssVSPart` describes a partition path, allocation paths, total/free bytes, block-device id, and partition id. `XrdOssVSInfo` aggregates totals, largest/free extents, usage, quota, extent count, and optional partition vector.

Dependencies: none beyond C++ core types. Populated by OSS cache/stat code.

Integration points: used by `XrdOssSys::StatVS` and consumers that need space totals or partition placement information for scheduling and monitoring.

Risks: ownership of `pPath` and `aPath` is not described by constructors; callers must delete only the exported `vsPart` array and not inner pointers unless documented elsewhere. Device identifiers may be zero or ambiguous on non-Linux/software filesystems.

Test signals: aggregate-only `StatVS`, `+space` partition-vector queries, `Export()` ownership transfer, destructor cleanup, and platform-specific bdev/part id reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssVS.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssWrapper.hh -->
# sources/distributed-fs/xrootd/src/XrdOss/XrdOssWrapper.hh

Purpose: provides pass-through wrapper classes for OSS plug-ins that want to intercept selected `XrdOss`, `XrdOssDF`, directory, or file methods while delegating the rest to an underlying implementation.

Important APIs/types/functions: `XrdOssWrapDF` wraps `XrdOssDF` methods; `XrdOssWrapper` wraps top-level `XrdOss` methods. It forwards directory methods (`Opendir`, `Readdir`, `StatRet`), file methods (`Open`, `Read`, `Write`, vector I/O, page I/O, async I/O, clone, truncate, sync, mmap, compression), common close/error/Fctl methods, top-level namespace methods (`Create`, `Mkdir`, `Rename`, `Remdir`, `Unlink`, `Stat*`, `Truncate`, `Reloc`), lifecycle methods, and LFN-to-PFN translation.

Control flow: every method is inline and immediately calls the same method on `wrapDF` or `wrapPI`. Derived wrappers override only the operations they need; non-overridden operations preserve the underlying OSS behavior.

State and persistence behavior: the wrappers own no persistent state. They hold references to underlying objects; underlying operations perform all filesystem, cache, and remote side effects.

Dependencies: `XrdOss/XrdOss.hh` supplies the full interface and related types such as `XrdOucEnv`, `XrdSfsAio`, `XrdOucIOVec`, `XrdOssVSInfo`, and `XrdOucCloneSeg`.

Integration points: `XrdOssArc` uses this pattern to wrap an existing OSS and enforce archive behavior. Other pushed OSS plug-ins can stack wrappers without reimplementing the complete interface.

Risks: wrapper lifetimes are reference-based; the creator remains responsible for deleting underlying objects. Missing an override means behavior silently passes through. Inline forwarding can hide ownership semantics for `newDir/newFile`, `resp` buffers, and error-message thread locality.

Test signals: derive a wrapper that intercepts one method and verify all other methods pass through, destructor/lifetime tests for wrapped DF objects, error-message propagation, and API coverage after adding new `XrdOss` virtual methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOss/XrdOssWrapper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdOssArc/CMakeLists.txt

Purpose: controls whether and how the `XrdOssArc` archive storage-system plug-in is built and installed.

Important APIs/types/functions: CMake option gate `BUILD_XRDOSSARC`, module target `XrdOssArc-${PLUGIN_VERSION}`, source list for archive wrapper, backup, compose, config, directory, file, FS monitor, stage, stop monitor, trace, and zip-file code, and install rule to `${CMAKE_INSTALL_LIBDIR}`.

Control flow: if `BUILD_XRDOSSARC` is false, CMake returns immediately. Otherwise it creates a module library, links it privately with `XrdUtils`, `XrdServer`, `libzip::zip`, and thread libraries, then installs the module.

State and persistence behavior: build-system state only. It determines whether the runtime plug-in exists and which implementation files are compiled into it.

Dependencies: project variables `PLUGIN_VERSION`, `CMAKE_THREAD_LIBS_INIT`, install dirs, and imported `libzip::zip`.

Integration points: this is the build entry for the OSS archive overlay loaded by XRootD. Missing files here mean corresponding wrapper, backup, staging, or zip behavior is unavailable at runtime.

Risks: builds without `BUILD_XRDOSSARC` hide compile errors; `libzip::zip` availability controls the module; header files in the source list help IDEs but do not enforce separate compilation.

Test signals: configure with flag on/off, link against libzip and server libraries, install packaging checks, and module-load smoke test through `osslib`/pushed OSS configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.cc

Purpose: implements the top-level archive OSS wrapper and plug-in entry point. It adds read-only archive/backup namespace behavior over an already loaded OSS.

Important APIs/types/functions: global `XrdOssArcGlobals`, extern "C" `XrdOssAddStorageSystem2`, `XrdOssArc::InitArc`, mutation blockers `Chmod/Create/Mkdir/Remdir/Rename/Truncate/Unlink`, `Features`, `FSctl`, `getErrMsg`, `Lfn2Pfn` overloads, and archive-aware `Stat`.

Control flow: `XrdOssAddStorageSystem2()` installs logging, constructs `XrdOssArc`, stores the underlying OSS pointer, initializes configuration, and returns the wrapper or null. `InitArc()` obtains a scheduler from env or starts a private one, logs startup, and delegates config. Mutation methods reject paths under archive/backup prefixes with `-EROFS`, otherwise pass through. `Lfn2Pfn` rejects internal archive paths with `-EPERM`. `Stat()` constructs `XrdOssArcCompose`; non-archive paths pass through, archive paths stat the archive zip on tape buffer, and file-in-archive requests ask backup utilities for metadata.

State and persistence behavior: installs global pointers (`ArcSS`, `ossP`, `schedP`), global config, logger, trace object, and thread-local extended error messages. It starts/schedules background backup work through configuration. It does not mutate archive contents through top-level namespace calls.

Dependencies: `XrdOssWrapper`, `XrdOssArcCompose`, `Config`, `Stage`, `ZipFile`, `XrdScheduler`, `XrdOucEnv`, `XrdOucECMsg`, `XrdSecEntity`, POSIX stat, and XRootD version macro.

Integration points: loaded as a pushed OSS plug-in by OFS, wrapping the native storage system. It advertises `XRDOSS_HASXERT` and creates archive-aware dir/file wrappers through the header.

Risks: global singleton design prevents independent instances; scheduler fallback creates an unmanaged scheduler; archive prefixes depend on configured strings; `getErrMsg()` returns only archive thread-local messages and not pass-through messages at top level; mutation checks must stay consistent with compose parsing.

Test signals: plug-in load/unload smoke, config failure returns null, mutation under `/archive` and `/backup` returns `EROFS`, normal paths pass through, stat archive zip vs member metadata, LFN mapping denial for internal paths, and feature flag preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.hh

Purpose: declares `XrdOssArc`, the archive-aware `XrdOssWrapper` subclass.

Important APIs/types/functions: overrides `newDir`, `newFile`, mutation methods, `Features`, `FSctl`, `getErrMsg`, `Lfn2Pfn`, `Stat`, `Truncate`, `Unlink`, and `InitArc`. `newDir` returns `XrdOssArcDir`; `newFile` returns `XrdOssArcFile`.

Control flow: the header defines wrapper construction and factory overrides inline, with operational behavior implemented in `XrdOssArc.cc` and archive file behavior in companion files.

State and persistence behavior: owns no additional members beyond `XrdOssWrapper::wrapPI`; runtime state is global in the implementation and in returned dir/file wrappers.

Dependencies: `XrdOssWrapper.hh`, `XrdOssArcDir.hh`, `XrdOssArcFile.hh`, and `XrdOucEnv`.

Integration points: used by the plug-in entry point to present a complete OSS interface to OFS while routing archive paths to special dir/file wrappers.

Risks: `newDir/newFile` do not check whether `wrapPI.newDir/newFile` returned null before constructing wrappers, so allocation or underlying factory failure handling depends on wrapper constructors/usage. Adding new `XrdOss` virtual methods requires updating this wrapper if archive behavior should intercept them.

Test signals: factory creation with valid and null underlying objects, override coverage, compile against current `XrdOss` ABI, and archive/normal path routing through returned DF wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.cc

Purpose: implements background dataset backup orchestration: discover datasets needing backup, stage them into an arena, reserve tape-buffer space, run preparation/archive/post scripts, and mark metadata complete.

Important APIs/types/functions: `XrdOssArcBackupTask::{BkpXeq,~XrdOssArcBackupTask}`, `XrdOssArcBackup::BkpWorker::DoIt`, constructor, `Add2Bkp`, `Archive`, `DoIt`, `GetManifest`, and `StartWorkers`. Static queue state includes `dsBkpQ`, `dsBkpQMtx`, `dsBkpQCV`, `numRunning`, and `maxRunning`.

Control flow: each scope job periodically calls `GetManifest()`, which runs `BkpUtilProg list` and enqueues new dataset names until `%%%`. Worker jobs pop tasks forever. A task creates a dataset arena, runs `bkputils setup` to get file/byte counts and manifest, optionally waits for `fsMon.Permit`, optionally runs `preparc`, runs the archive utility, optionally runs `postarc`, then runs `bkputils finish` to update metadata. `Archive()` builds a local or remote tape path and executes the archiver script.

State and persistence behavior: persistent effects are extensive: creates staging directories under `dsetRepoPFN`, writes manifests, creates/moves zip archives under the tape buffer or remote target, optionally deletes staging, and updates Rucio-like metadata keys. Runtime state tracks queued datasets, per-scope duplicate suppression sets, reserved bytes in `fsMon`, and scheduler jobs.

Dependencies: `XrdScheduler`, underlying `XrdOss`, `XrdOssArcConfig`, `XrdOssArcCompose`, `XrdOssArcFSMon`, `XrdOssArcStopMon`, `XrdOucProg`, `XrdOucStream`, `XrdOucUtils`, and XrdSys mutex/condition primitives.

Integration points: started by `XrdOssArcConfig::Configure`. It relies on external utilities (`XrdOssArc_BkpUtils`, archiver, optional pre/post tools) as the actual metadata and archive engines.

Risks: workers loop forever and are never deleted; failed tasks are deleted and rely on later manifest polls for retry; `numRunning` is decremented when idle and may not reflect live worker objects clearly; duplicate set owns `char*` pointers shared with tasks; external script output format is strict; local-space waits depend on semaphore redrive from `fsMon.Release`.

Test signals: manifest EOF handling, duplicate suppression, setup output parsing, local/remote archive path formation, pre/post script failures, finish failure, insufficient-space wait/release, stop-file pause behavior, and retry on next poll after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.hh

Purpose: declares the backup scheduler job, backup task, worker job, and queue/set state used by the archive plug-in.

Important APIs/types/functions: `XrdOssArcBackupTask` fields `Owner`, `theScope`, `theDSN`, `numBytes`, `numFiles`, `relSpace`, and `btSem`; task method `BkpXeq`; `XrdOssArcBackup` methods `Archive`, `Arena`, `DoIt`, `StartWorkers`, `theScope`, constructor, private `Add2Bkp` and `GetManifest`; nested `BkpWorker`; comparator `cmp_str`.

Control flow: class inheritance from `XrdJob` lets both per-scope backup scans and worker loops run on `XrdScheduler`. Tasks wait on their own semaphore when filesystem space is unavailable.

State and persistence behavior: header declares process-global queue state shared by all scopes plus per-scope duplicate sets and arena path. Persistent effects are in implementation through external tools and filesystem staging.

Dependencies: STL `deque`, `set`, `string`, `XrdJob`, and `XrdSysPthread`.

Integration points: used by config to schedule backups and by `XrdOssArcFSMon` to wake waiting tasks.

Risks: static queue state spans all archive scopes; `char*` ownership is manual; comparator assumes non-null C strings; jobs are intentionally never deleted; the destructor does not free `myArena`.

Test signals: construction creates arena, `StartWorkers` schedules expected jobs, duplicate set erase on task destruction, semaphore wake from FS monitor, and multi-scope queue fairness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.cc

Purpose: parses archive/backup logical paths and CGI into dataset/file/archive identifiers, builds archive/member paths, and asks metadata utilities where files live or what their stat metadata is.

Important APIs/types/functions: constructor, `ArcMember`, `ArcPath`, `DSN2Dir`, `Dir2DSN`, `getDSN`, `isArcFile`, `isArcPath`, `isBkpPath`, `isMine`, `SetarName`, static `Stat`, `StatDecode`, and `StatGet`.

Control flow: constructor classifies path as archive or backup by configured prefixes, extracts dataset scope/name, rejects write operations, optionally extracts archive filename from path, otherwise reads `ossarc.fn` from env, parses file scope/name, rejects invalid backup archive filenames, and calls `SetarName()` when a file must be mapped to an archive zip. `SetarName()` runs `BkpUtilProg which` and interprets `!ENOENT`/`!ENOANO`. `Stat()` runs `BkpUtilProg stat cgi`, then decodes CGI fields into a POSIX `stat`.

State and persistence behavior: object state is parsed strings (`dsScope`, `dsName`, `flScope`, `flName`, `arName`) and `didType`. No direct persistence; external utility calls query metadata systems. `DSN2Dir`/`Dir2DSN` encode slashes as `%` for staging directories.

Dependencies: global `Config`, `Elog`, thread-local `ecMsg`, `XrdOucEnv`, `XrdOucProg`, `XrdOucStream`, and `XrdSysE2T`.

Integration points: central parser for `XrdOssArc::Stat`, directory/file wrappers, backup staging, and archive member extraction.

Risks: `minLenFN` is declared but filename validation uses `minLenDSN`; prefix matching accepts configured strings exactly and has a special short archive-prefix case; utility output is single-line/string-protocol based; error details are thread-local; path and CGI ambiguity can select different archive names.

Test signals: archive dataset path, archive member path, backup path requiring `ossarc.fn`, file scope parsing with/without colon, archive suffix rejection for backup, utility `which` success and `!ENOANO`, stat CGI decode, and long path/member buffer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.hh

Purpose: declares `XrdOssArcCompose`, the data-id parser and path composer for archive and backup namespaces.

Important APIs/types/functions: public string fields for dataset/file/archive names, enum `pType {isARC,isBKP}`, `ArcMember`, `ArcPath`, static directory encoders, path classifiers, static `Stat`, and constructor with `isW`/`optfn` controls.

Control flow: the constructor returns status through an `int&` instead of throwing. Callers inspect `EDOM` to pass non-archive paths through and other errors to fail archive handling.

State and persistence behavior: transient parse result only. It does not own external resources and has a trivial destructor.

Dependencies: `<cstring>`, `<string>`, forward declarations for `stat` and `XrdOucEnv`.

Integration points: used by nearly every archive wrapper to determine whether a path belongs to this plug-in and how to address archive files and members.

Risks: public mutable fields make invariants easy to break after construction; static minimum lengths are private but not configurable here; return-by-reference status requires disciplined callers.

Test signals: construction return codes, public field population, static classifier consistency with configured prefixes, path/member composition, and non-archive `EDOM` pass-through.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcCompose.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.cc

Purpose: implements archive plug-in configuration, validation, helper-program setup, environment export, filesystem monitor initialization, and scheduling of backup scopes/workers.

Important APIs/types/functions: constructor defaults, `BuildPath`, `Configure`, `ConfigPath`, `ConfigProc`, `ConfigXeq`, `GenLocalPath`, `Usable`, directive parsers `xqArcsz`, `xqBkup`, `xqBkupPS`, `xqBkupScope`, `xqGrab`, `xqManf`, `xqPaths`, `xqRse`, `xqRucio`, `xqStage`, `xqTrace`, and `xqUtils`.

Control flow: defaults establish utility names, logical prefixes, admin/stop/tape/stage paths, metadata names, poll limits, backup mode, archive size policy, and tracing. `Configure()` gathers `ossarc.*` directives, exports debug/RSE/Rucio/checksum/size env vars, creates/validates admin and stop paths, initializes stop and free-space monitors, validates source data, builds the dataset backup arena, resolves and sets up helper programs, exports MSS settings, verifies metadata keys, constructs backup jobs for configured scopes, starts workers, and schedules initial scans. Directive parsing accepts `arcsize`, `backup`, `manifest`, `msscmd`, `paths`, `rsedcl`, `rucio`, `stage`, `trace`, and `utils`.

State and persistence behavior: stores configuration in heap-allocated C strings and program objects for daemon lifetime. It creates directories for admin and dataset backup arenas, initializes stop-file monitoring, exports environment variables consumed by external scripts, and schedules recurring jobs.

Dependencies: `XrdScheduler`, underlying `XrdOss`, backup/FS/stop monitors, `XrdOuca2x`, `XrdOucGatherConf`, `XrdOucProg`, `XrdOucUtils`, POSIX stat/access concepts, and global `ossP`, `schedP`, `Elog`, `ArcTrace`, `fsMon`, `ecMsg`.

Integration points: called from `XrdOssArc::InitArc`; it wires all external scripts (`BkpUtil`, `MssCom`, archiver, optional pre/post) and starts archive background processing.

Risks: manual string ownership and daemon-lifetime leaks; `Usable()` permission checks compare group write bit with `st_uid` instead of group id; unknown directives mostly warn but missing required RSE/scopes fail; external helper setup is startup-critical; no dynamic reconfiguration; path prefixes and tape paths are mutable global assumptions.

Test signals: parse every directive and invalid option, relative path rejection, RSE/scopes required, env exports, helper path qualification, local vs remote backup mode, archive-size range validation, metadata key failure warning, stop/admin/tape path validation, worker scheduling only when no fatal config errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.hh

Purpose: declares the daemon-lifetime configuration object for the archive OSS plug-in.

Important APIs/types/functions: public methods `BuildPath`, `Configure`, `GenTapePath`, constructor/destructor; public fields for helper programs/paths, logical and physical paths, metadata keys, RSEs, backup policy, staging policy, archive naming/size policy, stop monitoring, and local/remote mode; private directive parser helpers.

Control flow: the public API is intentionally broad: other archive modules read config fields directly instead of accessor methods. Private parser methods correspond to `ossarc.*` config directives.

State and persistence behavior: holds process-global configuration and program handles for the lifetime of the plug-in. Many members are `char*` with manual ownership and are initialized in the constructor or parsers.

Dependencies: forward declarations for `XrdOucEnv`, `XrdOucProg`, `XrdOucGatherConf`, and `XrdOssArcStopMon`.

Integration points: global `XrdOssArcGlobals::Config` is used by compose, backup, file, stage, directory, FS monitor, and stop monitor modules.

Risks: public mutable fields allow modules to observe partially initialized state if used before `Configure()` succeeds; destructor intentionally does no cleanup; declared `GenTapePath` is not implemented in the read source, which is a link/maintenance signal unless provided elsewhere.

Test signals: construction default values, successful `Configure()` populates required fields/programs, compile/link check for declared methods, and read-only access by dependent modules after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.cc

Purpose: implements archive-aware directory wrapper behavior, mainly opening archive zip files as directory-like objects while delegating non-archive paths.

Important APIs/types/functions: destructor, `Close`, `getErrMsg`, and `Opendir`.

Control flow: `Opendir()` creates a minimal `XrdOssArcCompose` with no env. Non-archive paths are forwarded to the underlying `ossDF`. Backup paths reject directory listing with `EPERM`. Archive paths compose the archive zip path, open it with `XrdSysFD_Open`, then promote the fd into the wrapped DF via `Fctl_setFD` to bypass normal name translation. `Close()` closes and deletes `zFile` if present, otherwise closes `ossDF`.

State and persistence behavior: owns the underlying `XrdOssDF*` and optional `XrdOssArcZipFile*`. It opens local/tape-buffer archive files read-only and does not modify archive contents.

Dependencies: `XrdOssArcCompose`, `XrdOssArcZipFile`, `XrdOucEnv`, `XrdOucECMsg`, `XrdSysFD`, `XrdSysError`, and the wrapper base class.

Integration points: returned by `XrdOssArc::newDir`. It lets archive paths participate in OSS directory operations by adapting an opened archive file descriptor into the existing OSS DF abstraction.

Risks: return for backup listing is positive `EPERM` instead of `-EPERM`, unlike surrounding methods; `zFile` is never assigned in this file, suggesting companion behavior or dead state; promoting an fd depends on underlying `Fctl_setFD` support; path buffer diagnostics can log uninitialized `arcPath` on composition failure.

Test signals: non-archive pass-through, backup `Opendir` denial sign convention, archive path open failure, successful fd promotion, close after promotion, error-message composition with underlying OSS messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.hh -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.hh

Purpose: declares `XrdOssArcDir`, the archive directory/file wrapper returned for directory operations.

Important APIs/types/functions: overrides `Close`, `getErrMsg`, and `Opendir`; constructor accepts trace id and underlying `XrdOssDF*`; private members `ossDF` and `zFile`.

Control flow: methods not overridden are inherited from `XrdOssWrapDF` and pass through to the underlying object. The constructor initializes the base wrapper with `*df` and stores `df` for ownership.

State and persistence behavior: owns and deletes the underlying DF object and optional zip-file adapter.

Dependencies: `XrdOssWrapper.hh`, forward declarations for `XrdOssArcZipFile`, `XrdOucEnv`, and `stat`.

Integration points: created by `XrdOssArc::newDir`; works with compose and zip modules to expose archives through OSS directory APIs.

Risks: constructor dereferences `df` immediately, so null underlying objects crash; ownership is implicit and differs from base reference semantics; most methods still pass through and may not be archive-safe unless intercepted elsewhere.

Test signals: null-underlying defensive tests, destructor ownership, pass-through inherited methods, and overridden close/open/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.cc -->
# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.cc

Purpose: monitors tape-buffer filesystem capacity and gates local backup tasks so the archive process preserves configured free space.

Important APIs/types/functions: `XrdOssArcFSMon::Init`, `DoIt`, `Permit`, `Release`, and private `getFSpace`. Platform macros map `statfs` fields across Linux/BSD/macOS.

Control flow: `Init()` reads filesystem size/free bytes, computes minimum free space from either percentage (negative config value) or bytes, logs startup capacity, stores path/update interval, and schedules periodic updates. `DoIt()` refreshes size/free/used counters under lock and reschedules itself. `Permit()` reserves bytes for a backup if `fs_inUse + fs_inBkp + taskBytes <= fs_MaxUsed`; otherwise it queues the task and tells caller to wait. `Release()` drops reserved bytes, refreshes filesystem stats, posts semaphores for queued tasks that now fit, and logs remaining blocked backups.

State and persistence behavior: runtime memory state tracks filesystem size, free, minimum free, maximum used, bytes already committed to backups, update interval, path, mutex, and waiting task queue. It does not persist data, but controls when backup tasks create large archive files.

Dependencies: platform `statfs`, `XrdScheduler`, `XrdOssArcBackupTask`, `XrdOucUtils::HSize`, `XrdSysError`, and trace globals.

Integration points: initialized by config and used by backup tasks in local backup mode. It is the resource lease manager for tape-buffer disk space.

Risks: queued tasks are raw pointers owned by backup workers; if a task is destroyed while queued, the wait queue would dangle. `Release()` posts waiters but only increments local `nTot`, not `fs_inBkp`, until waiters rerun `Permit()`, so races depend on mutex/semaphore sequencing. `size_t` arithmetic can overflow on very large filesystems or task sizes.

Test signals: percentage and absolute minfree calculations, startup below-minfree warning, permit success/failure, release waking multiple tasks in order, periodic refresh, statfs failure logging, and concurrent permit/release stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.cc -->
