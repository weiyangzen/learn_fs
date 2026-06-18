# subset-b-007940 Research

Grouped research for the requested XRootD/XrdFrm and XrdHttp source files. Each section is source-tree-aligned and bounded by markers for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.cc

Purpose: implements `XrdFrmFileset` and `XrdFrmFiles`, the namespace scanner and fileset assembler used by purge and migration. It walks configured storage paths, groups a base file with migration sidecars such as `.lock`, `.pin`, `.fail`, and `.pfn`, and exposes refreshed stat/xattr state to higher-level policy code.

Important APIs and control flow: `XrdFrmFiles::Get()` drains already-built filesets, otherwise calls `XrdOucNSWalk::Index()` for a directory and `Process()` to hash entries by base filename. `Process()` handles compressed directory storage, recognizes suffixes through `XrdOssPath::pathType()`, ignores/removes some old-mode artifacts in new-run mode, and emits one fileset per logical base name. `XrdFrmFileset::Screen()` rejects orphaned sidecars or missing copy-time evidence, optionally deleting orphans when `Config.Fix` is set. `Refresh()` re-stats base and lock files, checks file locks, and refreshes pin/copy xattrs.

State and persistence: file state is read from filesystem stat records, old-mode lock-file mtimes, and new-mode `XrdFrcXAttrCpy`/`XrdFrcXAttrPin` xattrs. `BadFiles` suppresses repeated error messages until purged by callers.

Dependencies and integration: used by `XrdFrmMigrate::Scan()` and `XrdFrmPurge::Scan()`. It depends on global `XrdFrm::Config`, `XrdOucNSWalk`, `XrdOssPath`, xattr helpers, and `XrdFrc::Say` logging.

Risks and test signals: `Mkfn()` is explicitly non-reentrant when directory compression is enabled; callers must not share one fileset across threads. Path construction assumes enough shared directory buffer for filenames. Tests should cover old/new run modes, orphan sidecar removal, compressed directory mode, lock contention, xattr absence, symlink `Link` paths, and recursive scan error propagation via `rc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.hh

Purpose: declares the fileset model and directory scanner API shared by XrdFrm purge and migration. `XrdFrmFileset` represents one base file plus recognized sidecar entries; `XrdFrmFiles` is an iterator over filesystem walks that returns those sets.

Important APIs/types: `XrdFrmFileset` exposes sidecar accessors (`baseFile()`, `failFile()`, `lockFile()`, `pinFile()`, `pfnFile()`), path constructors, `dirPath()`, `Refresh()`, `Screen()`, and `setCpyTime()`. It owns `XrdOucNSWalk::NSEnt *File[XrdOssPath::sfxNum]`, xattr wrappers for copy and pin metadata, a shared directory `XrdOucTList`, and linked-list fields `Next`/`Age`. `XrdFrmFiles::Get()` is the public iterator. Its options control recursion, shared directory compression, caller-owned filesets, and copy-time initialization.

State and persistence: the header encodes that file metadata is not copied into a separate durable object; it is represented by live `NSEnt` entries, stat buffers, sidecar suffix slots, and optional xattrs. The shared directory object uses `ival[dLen]` and `ival[dRef]` as implicit layout constants.

Dependencies and integration: the API binds to `XrdOucNSWalk`, `XrdOucHash`, `XrdOucXAttr`, `XrdFrcXAttr`, and `XrdOssPath`. Callers in purge/migrate rely on `NoAutoDel` to take ownership of returned sets.

Risks and test signals: memory ownership is subtle because `NoAutoDel` changes deletion behavior and shared directory buffers use reference counting in `XrdOucTList`. Tests should verify destructor cleanup, shared directory refcounts, `Get(noBase)` behavior, and xattr refresh semantics for old/new compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.cc

Purpose: implements the automatic migration scanner. It periodically walks configured paths, selects files that changed since the last copy time, waits for idle files to age past `Config.IdleHold`, and queues internal migration requests into `XrdFrmXfrQueue`.

Important APIs and control flow: `Migrate(1)` starts a detached migration scan thread; `Migrate(0)` runs the infinite loop. Each cycle calls `Scan()`, then repeatedly calls `Advance()` to reprocess deferred files until the wait budget expires. `Scan()` constructs `XrdFrmFiles` with recursion, compressed directories, and manual deletion, then screens filesets and sends eligible ones through `Add()`. `Eligible()` rejects missing copy time, unchanged files, and recent fail files. `Queue()` converts a fileset into an `XrdFrcRequest` with `Migrate` option, internal ID, logical path, and `migQ`.

State and persistence: migration state is mostly derived from base file mtime and persisted copy-time metadata (`cpyInfo`, lock-file mtime, or xattr). Fail files persist transfer retry suppression. `fsDefer` is an in-memory sorted linked list by base mtime; it is discarded after each cycle.

Dependencies and integration: depends on `XrdFrmFiles`, `XrdFrmTransfer::checkFF()`, `XrdFrmXfrQueue::Add()`, global `Config.pathList`, and the transfer daemon started by `XrdFrmXfrDaemon`. It logs through `Say`/trace macros.

Risks and test signals: `nowT` in `Scan()` is static-initialized, so the bad-file purge interval check may not observe time progression as intended. Queue request IDs use a static incrementing int without persistence. Tests should cover idle deferral ordering, fail-file hold behavior, logical path failures, unchanged-file suppression, and background thread startup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.hh

Purpose: declares the static migration coordinator used by `frm_xfrd` to discover migratable resident files and inject transfer requests. The class has no per-instance state; it is a process-global service.

Important APIs/types: public methods are `Display()` for configuration reporting, `Queue()` for converting an already-selected fileset to a request, and `Migrate()` for starting or running the scanner. Private helpers `Add()`, `Advance()`, `Defer()`, `Eligible()`, and `Scan()` implement screening and deferred-idle handling. Static variables `fsDefer` and `numMig` track the current cycle's deferred files and selected count.

State and persistence: only in-memory cycle state is declared here. Durable eligibility comes from fileset metadata read by `XrdFrmFileset` and fail files checked by transfer code.

Dependencies and integration: forward declares `XrdFrmFileset`, `XrdFrmXfrQueue`, and `XrdOucTList`. It is initialized by `XrdFrmXfrDaemon::Init()` when migratable paths and output copy commands are configured.

Risks and test signals: because the interface is fully static, multiple independent migration policies cannot coexist in one process. Tests should exercise the class as a singleton, including cleanup of deferred files and interactions with transfer queue failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.cc

Purpose: implements XrdFrm monitoring event emission for info, stage, migration, and purge activity. It builds XRootD monitor map packets and sends them to up to two configured collectors.

Important APIs and control flow: `Defaults()` accepts strdup-owned destination strings plus mode masks, normalizes empty destination/mode combinations, and sets `monMIGR`, `monPURGE`, and `monSTAGE` feature flags. `Init()` creates a server identity via `XrdOucUtils::Ident()`, constructs an identification record, opens `XrdNetMsg` destinations, and optionally starts a periodic `Ident()` thread. `Map()` converts user/path data into `XrdXrootdMonMap`, handles special transfer event codes, fills a header, and routes the packet through `Send()`. `fillHeader()` assigns sequence bytes under a mutex.

State and persistence: all monitor state is process-global static memory: destination strings, `XrdNetMsg` objects, identity record, sequence counter, start time, and event-mode booleans. No durable state is written.

Dependencies and integration: transfer and purge paths call `XrdFrmMonitor::Map()` when monitor flags are enabled. It uses `XrdXrootdMonData` packet layouts, `XrdNetMsg` network delivery, `XrdSysThread`, and global `Say` logging.

Risks and test signals: `Map()` copies username and path into fixed buffers; long inputs require bounds-sensitive tests. `Send(-1, ...)` in `Ident()` intentionally targets any destination whose mode intersects `-1`, but this bitmask idiom should be tested. Initialization failure messages include an unused `etext` pointer. Tests should verify mode routing, sequence wrap, dual collectors, identity record length, and thread startup failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.hh

Purpose: declares the XrdFrm monitor facade and event masks. It is the shared API for enabling and sending monitoring records from stage, migration, and purge code.

Important APIs/types: macros define `XROOTD_MON_INFO`, `XROOTD_MON_STAGE`, `XROOTD_MON_MIGR`, and `XROOTD_MON_PURGE`. Public static methods configure defaults, initialize identity/network state, emit identity records, and map activity records. Public static chars `monMIGR`, `monPURGE`, and `monSTAGE` are fast-path flags used by hot transfer/purge code to avoid building monitor records when disabled.

State and persistence: private static members describe two destinations, modes, `XrdNetMsg` pointers, process start time, identity buffer/length, server id string, and identity interval. This is runtime-only state.

Dependencies and integration: depends on `XrdXrootdMonData.hh` and protocol integer types. Forward declares `XrdNetMsg` so most consumers only need the header without pulling network implementation.

Risks and test signals: public writable flag chars can be mutated outside initialization, so tests should treat them as part of the ABI. Validate that `Defaults()` ownership expectations for destination strings are respected by callers and that `Init()` is not called twice without cleanup leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurgMain.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurgMain.cc

Purpose: provides the `frm_purge` executable entry point. It parses daemon/one-shot options through `XrdFrmConfig`, installs logging and signal defaults, builds purge policies, and drives repeated purge cycles.

Important APIs and control flow: `main()` blocks signals, sets thread stack size, calls `Config.Configure(argc, argv, &mainConfig)`, displays configuration, then either performs one purge pass for `-O` mode or loops forever. The loop honors `Config.StopPurge` by sleeping while the stop file exists. `mainConfig()` converts configured policy records into `XrdFrmPurge::Policy()` objects, ensures a `public` policy and policies for all spaces, applies one-time overrides through `XrdFrmPurge::Init()`, and starts a UDP server placeholder thread for daemon mode.

State and persistence: process state is global `XrdFrm::Config`, `XrdLog`, and `XrdTrace`. The command may create/administer PID/log files via configuration, and purge actions persist through filesystem deletions performed by `XrdFrmPurge`.

Dependencies and integration: integrates `XrdFrmConfig`, `XrdFrmPurge`, XrdNet socket creation for admin path, and XrdSys logging/thread utilities. `mainServer()` is currently a stub with server logic commented out.

Risks and test signals: command-line behavior is safety-sensitive because `-T` test mode disables actual purge and clears fix mode. Tests should cover one-shot argument validation, stop-file suspension, missing policy defaults, disabled spaces, UDP socket startup, and that test mode prevents destructive `Config.Fix`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurgMain.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.cc

Purpose: implements space-based purge policy. It scans namespaces, selects eligible resident files by access age and migration/pin state, optionally asks an external policy program, removes files through the OSS layer, notifies CMS/CNS, emits monitor records, and trims old empty directories.

Important APIs and control flow: `Policy()` creates per-space policy objects. `Init()` prunes policies without spaces, enables requested spaces, converts percent thresholds to byte thresholds, and starts `PolProg` when external policy is used. `Purge()` calls `LowOnSpace()`, reports `Stats()`, then rotates over enabled spaces calling `PurgeFile()` until each reaches `maxFSpace` or cannot proceed. `Scan()` walks configured paths using `XrdFrmFiles`, screens filesets, calls `Add()`, and may use `XrdFrmPurgeDir` callback to remove empty directories. `Eligible()` enforces hold time, fail files, migration copy-time, and pin flags. `PurgeFile(fset,pfn)` unlinks via `Config.ossFS`, converts PFN to LFN when possible, notifies `cmsPath`/`XrdFrmCns`, and maps purge monitor data.

State and persistence: per-policy state tracks free/used space, thresholds, counts, deferred queues, and an `XrdFrmTSort` of candidates. Persistent effects include deleted data, removed directories, CNS/CMS updates, and external fail/sidecar files observed by `XrdFrmFileset`.

Dependencies and integration: uses `XrdOssVSInfo` space stats, `XrdFrmFiles`, `XrdFrmTSort`, `XrdFrmCns`, `XrdFrmMonitor`, `XrdNetCmsNotify`, and optional `XrdOucProg` policy program.

Risks and test signals: destructive behavior depends on many gates; test mode must be verified for file and directory removal. `Advance()` appears to return no deferred item when `time(0) - DeferT[n] > Hold`, which is counterintuitive for an age threshold and deserves regression coverage. `nowT` static initialization in `Scan()` can stale time-dependent scheduling. Tests should cover pin variants, migrated/unmigrated old/new metadata, external policy responses `y/n/a`, CMS/CNS notifications, space threshold math, and directory mtime restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.hh

Purpose: declares the process-global purge policy manager and per-space policy object. It is the core API for configuring purge thresholds and running purge cycles from `frm_purge`.

Important APIs/types: public static methods include `Display()`, `Init()`, `Policy()`, and `Purge()`. Private helpers manage candidate addition, deferred queue advancement, eligibility, low-space detection, namespace scanning, stats, deletion, verbose tracking, and external policy checks. Per-object fields hold space stats, min/max free thresholds, hold intervals, external policy flag, counters, stop/enabled state, an `XrdFrmTSort`, and fixed-size deferred queues.

State and persistence: static `First`/`Default` form the policy list, `PolProg`/`PolStream` encapsulate an external program, and reset timers coordinate rescans. Persistent effects happen in the `.cc` implementation through OSS/CNS/CMS operations.

Dependencies and integration: includes `XrdFrmTSort.hh` and `XrdOssSpace.hh`, and forward declares filesets, policy program, streams, and `XrdOucTList`. `XrdFrmPurgMain.cc` owns setup, while purge implementation owns execution.

Risks and test signals: fixed `DeferQsz` buckets and process-global static state make behavior sensitive to long-running daemon lifetimes. Tests should validate policy replacement, default policy discovery, destructor `Clear()` deletion of deferred/candidate filesets, and one-time override application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.cc

Purpose: implements a request-boss worker for one request persona (`pstg`, `migr`, `getf`, or `putf`). It persists client requests in priority queue files, drains them in priority order, and hands executable requests to `XrdFrmXfrQueue`.

Important APIs and control flow: `Start()` creates queue directories and `XrdFrcReqFile` objects for each priority, then starts the processing thread. `Add()` clamps request priority, stamps add time, appends to the proper request file, and wakes the thread. `Del()` cancels matching request IDs from all priority files. `Process()` waits via `Wakeup(0)`, then scans priorities high-to-low; each priority drains up to `i+1` pulls, registering cluster IDs or enqueueing transfers. `Register()` interprets request ID as a PID and stores cluster identity in `CID`.

State and persistence: `rQueue[]` is backed by request files under the queue path; `rqReady` and `isPosted` implement a binary semaphore to avoid wakeup storms. Registered cluster identity persists in the `CID` facility.

Dependencies and integration: used by `XrdFrmXfrDaemon` bosses. It depends on `XrdFrcReqFile`, `XrdFrcRequest`, `XrdFrmXfrQueue`, `XrdFrcCID`, and `XrdFrcUtils`.

Risks and test signals: queue fairness is weighted by priority and may starve lower priorities under continuous high-priority load. `Wakeup()` uses a static mutex shared across all bosses. Tests should cover restart persistence, cancellation, priority clamping, register request deletion on `CID.Add()` failure, and behavior when transfer queue rejects a request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.hh

Purpose: declares the request-boss abstraction that owns one family of priority request files and a processing thread.

Important APIs/types: public methods `Add()`, `Del()`, `Process()`, `Start()`, and `Wakeup()` provide queue mutation, worker execution, initialization, and semaphore signaling. `Server()` is declared but not implemented in this subset. Private `Register()` handles cluster registration requests. Fields include an `XrdSysSemaphore`, an array of `XrdFrcReqFile *` by priority, the persona name, queue number, and a posted flag.

State and persistence: persistent state is delegated to `XrdFrcReqFile`; the class itself manages runtime thread synchronization and queue identity.

Dependencies and integration: included by `XrdFrmXfrDaemon.hh`; queue numbers are `XrdFrcRequest` queue constants. It is the bridge between external request ingestion and the in-memory transfer queue.

Risks and test signals: the declared `Server()` without a nearby definition should be checked by link coverage. Tests should instantiate multiple bosses to ensure the static wakeup mutex in the implementation does not cause missed signals or unintended serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.cc

Purpose: implements a lightweight age sorter for purge candidates. It returns filesets from oldest access time to newest, optionally ordering equally old entries by decreasing file size.

Important APIs and control flow: `Add()` rejects entries with future access time, computes `Age = baseT - st_atime`, and places the entry into a day bucket capped at 63. `Oldest()` walks the multi-level table from seconds to minutes to hours to days, lazily rebucketing lists with `Bin()` as it descends. `Bin()` extracts six-bit time fields and optionally calls `Insert()` at the seconds level when size sorting is enabled. `Purge()` deletes every remaining fileset and resets state.

State and persistence: all state is in memory: `FSTab[4][64]`, `baseT`, entry counts, and current highest non-empty bucket indexes. Fileset ownership transfers to the sorter until `Oldest()` returns it or `Purge()` deletes it.

Dependencies and integration: used by `XrdFrmPurge` as `FSTab` for eligible candidates. It depends on `XrdFrmFileset::baseFile()` stat data.

Risks and test signals: time bucketing is approximate and capped at 63 days for the day bucket. Future atimes are silently rejected. Tests should validate oldest-first ordering across bucket boundaries, size ordering only in final bucket, ownership deletion on purge, and behavior when `baseT` is fixed at reset while scans take time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.hh

Purpose: declares the purge candidate sorter. It is specialized for `XrdFrmFileset` objects and access-time aging, not a general container.

Important APIs/types: `Add()` transfers a fileset into the sorter, `Oldest()` removes and returns the next purge candidate, `Count()` reports the number of entries, and `Purge()` deletes all queued entries. Constants define four six-bit time tiers: seconds, minutes, hours, and days. `sortSZ` controls whether final-bin insertion sorts by file size.

State and persistence: runtime-only arrays and counters track bucket heads and high-water indices. The class owns queued fileset pointers.

Dependencies and integration: forward declares `XrdFrmFileset`, so consumers can include the header without scanner internals. `XrdFrmPurge` embeds one sorter per space policy.

Risks and test signals: copy/assignment are not disabled despite pointer ownership; accidental copying would double-delete. Tests or static analysis should flag copying, and unit tests should cover destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.cc

Purpose: implements transfer workers for stage/fetch, copy-in, copy-out, migration, and migration-with-purge. It wraps externally configured copy commands, fail-file throttling, local/remote path translation, copy-time persistence, notifications, and monitoring.

Important APIs and control flow: `Init()` initializes cluster IDs, the transfer queue, and worker threads split between in/out/any queues. `Start()` loops on `XrdFrmXfrQueue::Get()`, dispatching to `Fetch()` for inbound queues or `Throw()` for outbound/migration queues, then calls `Done()`. `Fetch()` resolves a remote source, checks fail files, skips existing local files, optionally creates `.anew` placeholders, runs the command, finalizes with `FetchDone()`, removes temp files on failure, and notifies CMS. `Throw()` resolves a remote destination, checks resident source and fail files, validates migration eligibility with `ThrowOK()`, runs the outgoing command, verifies no source modification, and either purges local data or calls `ThrowDone()`. `SetupCmd()` performs macro substitution for command arguments.

State and persistence: fail files persist retry state; `.anew`, `.lock`, and copy xattrs persist transfer/migration metadata. `pTab` caches created remote directories for `cmdMDP`. Successful operations update CNS/CMS and monitor streams.

Dependencies and integration: depends on `XrdFrmXfrQueue`, `XrdFrmXfrJob`, `XrdFrcRequest`, `XrdOucProg`, `XrdOss`, xattr helpers, `CID`, `XrdFrmCns`, `XrdFrmMonitor`, and global configuration.

Risks and test signals: high risk centers on external command exit semantics, path buffer mutation (`PFN[pfnEnd]` sidecar suffixes), fail-file directory length limits, and verifying files modified during copy. Tests should cover URL/non-URL command selection, `cmdAlloc`, `cmdRME`, `cmdMDP`, nofile fail mtimes, old/new copy-time persistence, purge-on-success, monitor payloads, and notification return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.hh

Purpose: declares the transfer worker class and its helper methods. The class is instantiated per worker thread and owns command objects used to run configured copy operations.

Important APIs/types: public static `checkFF()` inspects and ages fail files; `Init()` starts global queue/worker infrastructure; `Start()` is the worker loop. Private methods separate inbound fetch, outbound throw, fail-file creation/checking, command setup, directory creation tracking, migration validation, and migration completion. Static `pMutex`/`pTab` coordinate remote directory tracking across workers. Per-worker fields include four `XrdOucProg *` command slots, the current `XrdFrmXfrJob *`, and `cmdBuff`.

State and persistence: this header shows mixed static and per-worker state. Durable state is handled by implementation through fail files, xattrs, sidecars, and namespace notifications.

Dependencies and integration: forward declares transfer helper structs, jobs, and `XrdOucProg`; includes hash and thread primitives. Called from `XrdFrmXfrDaemon::Init()` and transfer worker threads.

Risks and test signals: the current job pointer is a mutable member, so one `XrdFrmTransfer` object must not be shared across threads. Tests should verify one object per thread and command object setup for all four transfer directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.cc

Purpose: implements the external request-agent process mode. It reads textual requests from stdin, parses operation-specific fields, and forwards them to persistent `XrdFrcReqAgent` queues for stage, get, migrate, and put operations.

Important APIs and control flow: static agents are created for `getf`, `migr`, `pstg`, and `putf`. `Start()` initializes each agent against `Config.QPath`, attaches stdin to an `XrdOucStream`, and processes lines until EOF. `Process()` dispatches operations: `+` stage, `<` copy in, `>`/`=` copy out, `&`/`^` migrate, `-` cancel inbound/stage, `~` cancel outbound/migrate, `?` list, and `!` ping. `Add()` parses request ID, notify path, priority, mode, and one or more paths; it maps mode to options, handles opaque query offsets, validates URL or absolute path, and enqueues each request. `Del()` and `List()` handle cancellation and queue inspection.

State and persistence: request state is persisted by `XrdFrcReqAgent` under the queue path. The agent process itself only keeps static agent objects and the current parsed request.

Dependencies and integration: pairs with `XrdFrmXfrDaemon::Pong()` and `XrdFrmReqBoss` queue files. It uses `XrdFrcUtils` for URL/mode mapping and global `Config` for process identity/admin mode.

Risks and test signals: parsing is positional and mutates path tokens to strip opaque fields. Tests should cover multi-path requests, trace/user suffixes in op tokens, priority clamping, invalid URLs, cancel shorthand, list item filters, stdin EOF exit code, and unsupported operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.hh

Purpose: declares the request-agent facade used by non-daemon `frm_xfr*` personas to translate command input into request queue operations.

Important APIs/types: public static `Start()` runs the stdin loop and `Process()` handles one parsed stream command. Private helpers `Add()`, `Del()`, `List()`, and `Agent()` map operation tokens to one of four static `XrdFrcReqAgent` instances.

State and persistence: the header declares static agents for get, put, migrate, and stage; durable request persistence is owned by those agent objects.

Dependencies and integration: includes `XrdFrcReqAgent.hh` and forward declares `XrdOucStream`. The daemon can also reuse `Process()` to handle UDP agent messages.

Risks and test signals: because all agents are static, repeated `Start()` calls in the same process are not isolated. Tests should verify operation-to-agent mapping and initialization failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrAgent.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.cc

Purpose: implements the transfer daemon coordinator. It ensures singleton daemon execution, starts transfer workers and migration scanning, starts request bosses, listens for UDP agent messages, and periodically wakes queues.

Important APIs and control flow: `Init()` acquires a unique lock file under `Config.QPath`, initializes `XrdFrmTransfer`, adjusts migration wait time, starts auto-migration when path and output command configuration allow it, and starts all four `XrdFrmReqBoss` instances. `Pong()` has two phases: first call creates a UDP socket at `xfrd.udp` and spawns a listener thread; re-entered thread attaches the socket to `XrdOucStream`, ignores list messages, handles wakeup pings by posting matching bosses, and delegates other messages to `XrdFrmXfrAgent::Process()`. `Start()` starts the ponger and loops waking every boss at `Config.WaitQChk`.

State and persistence: static bosses own persistent request files. The daemon lock file prevents duplicate daemons. UDP socket state is static inside `Pong()`.

Dependencies and integration: ties together `XrdFrmReqBoss`, `XrdFrmTransfer`, `XrdFrmMigrate`, `XrdFrmXfrAgent`, `XrdNetSocket`, and global configuration.

Risks and test signals: `Pong()` recursive/threaded initialization is compact and easy to break; tests should verify first-call socket setup, listener reentry, wakeup command parsing, duplicate daemon lock handling, migration disabled warnings, and periodic wakeups when UDP is silent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.hh

Purpose: declares the singleton transfer daemon facade and its four request bosses.

Important APIs/types: public static `Init()` performs daemon setup, `Pong()` manages UDP listener/wakeup messages, and `Start()` runs the daemon loop. Private `Boss()` maps an operation character to the proper `XrdFrmReqBoss`. Static `GetBoss`, `PutBoss`, `MigBoss`, and `StgBoss` represent request streams.

State and persistence: persistent queue state is delegated to the bosses; daemon identity is enforced in the implementation by a lock file.

Dependencies and integration: includes `XrdFrmReqBoss.hh`. The main executable calls this header's API when not running in agent mode.

Risks and test signals: static bosses mean queue personas are fixed at compile time. Tests should assert operation mapping for all request tokens and that daemon setup failure prevents `Start()` from running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrDaemon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrJob.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrJob.hh

Purpose: defines the transfer job record passed between `XrdFrmXfrQueue` and `XrdFrmTransfer` workers.

Important APIs/types: `XrdFrmXfrJob` is a plain aggregate with linked-list field `Next`, extra notification destinations `NoteList`, source request file pointer `reqFQ`, request-file key `reqFile`, copied `XrdFrcRequest reqData`, display strings `Type`/`Act`, local `PFN` buffer, `pfnEnd` suffix offset, `RetCode`, and queue number.

State and persistence: the job is runtime state only, but it points back to persistent request files so `Done()` can delete completed requests. The PFN buffer reserves room for sidecar suffixes such as `.fail`, `.anew`, and `.lock`.

Dependencies and integration: used by `XrdFrmXfrQueue` for queue ownership and by `XrdFrmTransfer` for execution. Includes request type and platform path limits.

Risks and test signals: no constructor initializes fields, so queue initialization must set every field before worker use. Tests should validate PFN suffix bounds and cleanup of `NoteList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrMain.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrMain.cc

Purpose: provides the shared main program for transfer daemon and agent personas. The executable behaves as `frm_xfrd` when named accordingly; otherwise it runs in agent mode.

Important APIs and control flow: `main()` blocks signals, sets stack size, determines persona from `argv[0]`, configures logging, calls `Config.Configure(argc, argv, &mainConfig)`, then exits with `XrdFrmXfrAgent::Start()` or `XrdFrmXfrDaemon::Start()`. `mainConfig()` initializes the daemon only when not in agent mode; agents defer initialization to `Start()`.

State and persistence: global `XrdFrm::Config`, `XrdLog`, and `XrdTrace` are instantiated for the transfer subsystem. Daemon mode persists queue/lock state through downstream components.

Dependencies and integration: integrates `XrdFrmConfig`, `XrdFrmXfrAgent`, `XrdFrmXfrDaemon`, and XrdSys logging/thread utilities. Command-line options include background daemon mode, config, debug, fix, log rotation, instance/site names, test mode, verbosity, and log flushing.

Risks and test signals: persona detection uses `strncmp("frm_xfrd", pP, 8)`, so symlink/binary names drive behavior. Tests should cover agent/daemon naming, configuration callback return inversion, invalid config exit code, and test-mode propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrMain.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.cc -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.cc

Purpose: implements the in-memory transfer job queues, duplicate suppression table, notification delivery, free-job pool, stop-file monitoring, and fair queue selection used by transfer workers.

Important APIs and control flow: `Init()` creates per-queue stop-file names, starts one `StopMon()` thread per queue, and preallocates `2 * Config.xfrMax` free jobs for each queue. `Add()` validates queue number, suppresses duplicate active/pending work by request key, translates LFN to PFN, checks inbound/outbound existence preconditions, allocates a job, stores it in `hTab`, appends to the queue, and posts `qReady`. `Get()` waits for a job acceptable to the worker's IO type and calls `Pull()`. `Pull()` alternates between inbound and outbound queue pairs, skips stopped queues, chooses older add time, and dequeues. `Done()` sends notifications, deletes the persistent request, removes the active hash entry, and returns the job to the free pool.

State and persistence: in-memory state is protected by `hMutex` and `qMutex`. Persistent request files are deleted through `reqFQ`; notification side effects write to file or UDP destinations. Stop files under `Config.AdminPath` suspend queues until removed.

Dependencies and integration: used by `XrdFrmReqBoss`, `XrdFrmMigrate`, and transfer workers. Depends on `XrdFrcReqFile`, `XrdFrcRequest`, `XrdNetMsg`, `XrdOss`, and global `Config`.

Risks and test signals: notification parsing mutates `Notify` by replacing carriage returns with NULs, so copied request data must be isolated. `Pull()` indexes `xfrQ[theQ]` even when both queues are nil unless guarded by surrounding state; stopped-empty cases need tests. Tests should cover duplicate notification aggregation, stop-file suspend/resume, worker lane selection, free-pool exhaustion blocking, inbound/outbound existence rules, and unsupported notification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.hh -->
## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.hh

Purpose: declares the static transfer queue service shared by request bosses, migration scanner, and transfer workers.

Important APIs/types: `Add()` enqueues a request, `Get()` blocks until a matching job is available, `Done()` completes a job, `Init()` sets up pools and stop monitors, and `StopMon()` is the monitor thread entry. Queue selection constants distinguish inbound-only, outbound-only, and any queue workers. Private `theQueue` stores semaphores, free and pending lists, stop-file metadata, and queue identity.

State and persistence: static hash `hTab` suppresses duplicates; `xfrQ[]` stores in-memory queues and free lists; request-file and notification persistence are handled by implementation collaborators.

Dependencies and integration: includes request, hash, and thread primitives; forward declares request files and jobs. `XrdFrmTransfer::Init()` must call `Init()` before workers call `Get()`.

Risks and test signals: all methods are static, so test isolation requires explicit process or state reset. Verify queue array sizing against `XrdFrcRequest::numQ` and stop-file naming conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHeaders.cmake -->
## sources/distributed-fs/xrootd/src/XrdHeaders.cmake

Purpose: defines installation of public and private XRootD headers. It is a build-system manifest that controls which headers are exposed under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd` and its `private` subdirectory.

Important APIs and control flow: `install_headers(destination files)` iterates a header list, extracts the subdirectory with a regex, and installs each file under the matching destination subtree. The script installs generated `XrdVersion.hh`, defines `XROOTD_PUBLIC_HEADERS`, conditionally appends server-only headers when `NOT XRDCL_ONLY`, defines `XROOTD_PRIVATE_HEADERS`, conditionally appends private server/plugin headers and VOMS headers, then calls `install_headers()` for public and private groups.

State and persistence: persistent effect is CMake install metadata and installed header layout. No runtime state exists.

Dependencies and integration: consumed by the top-level XRootD build. Variables include `CMAKE_BINARY_DIR`, `CMAKE_INSTALL_INCLUDEDIR`, `XRDCL_ONLY`, and `BUILD_VOMS`. The manifest includes `XrdHttp/XrdHttpSecXtractor.hh` publicly and `XrdHttp/XrdHttpExtHandler.hh` privately, affecting plugin ABI consumers.

Risks and test signals: duplicate public entries exist for some headers in server-only append blocks, which CMake install may tolerate but packaging tests should catch. The regex assumes paths contain a directory component. Tests should validate install manifests for client-only and full builds, private/public ABI expectations, and generated version header presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHeaders.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdHttp/CMakeLists.txt

Purpose: builds and installs the XrdHttp utility shared library and HTTP protocol module when `BUILD_HTTP` is enabled.

Important APIs and control flow: the file returns immediately if HTTP is disabled. `XrdHttpUtils` is built as a shared library from checksum, extension handler, protocol, range, request, monitoring, security, static, tracing, utility, and header utility sources. It sets library version properties, links privately to `XrdServer`, `XrdUtils`, and `XrdCrypto`, and publicly to OpenSSL SSL/Crypto. It then builds module `${XrdHttp}` from `XrdHttpModule.cc`, links it against `XrdUtils` and `XrdHttpUtils`, sets `.so` suffix, and installs both targets to the library directory.

State and persistence: build artifacts are the shared `XrdHttpUtils` library and versioned HTTP module plugin. Install rules persist them in `${CMAKE_INSTALL_LIBDIR}`.

Dependencies and integration: integrates the HTTP protocol with the XRootD plugin loader. The comment notes that HTTP extension plugins are expected to link against `XrdHttpUtils` for `XrdHttpExt` implementations.

Risks and test signals: link visibility is important because plugins consume `XrdHttpUtils`; ABI changes in headers should be tested with downstream plugin builds. Build tests should cover `BUILD_HTTP=OFF`, shared library versioning, OpenSSL link propagation, and plugin suffix/name conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.cc -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.cc

Purpose: implements a small value object describing one checksum algorithm mapping between XRootD configuration naming and HTTP digest naming.

Important APIs and control flow: the constructor stores the XRootD config digest name, the HTTP name, a base64-padding flag, and precomputes a lowercase HTTP name using `std::transform(::tolower)`. Getters return copies of the three strings and the padding flag.

State and persistence: all state is immutable after construction by convention, stored in private string/bool members. There is no persistence or external side effect.

Dependencies and integration: used by `XrdHttpChecksumHandlerImpl` to build supported checksum maps and configured checksum vectors.

Risks and test signals: `::tolower` on plain `char` can be undefined for negative signed-char values, though algorithm names are ASCII. Tests should validate lowercase conversion, HTTP/config aliases, and padding flags for supported checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.hh -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.hh

Purpose: declares `XrdHttpChecksum`, a simple checksum metadata holder for the HTTP checksum negotiation layer.

Important APIs/types: constructor accepts XRootD config digest name, HTTP RFC-style name, and whether the checksum value needs base64 padding. Getters expose XRootD config name, HTTP name, lowercase HTTP name, and padding requirement.

State and persistence: private members store the names and flag. The object is used as static/shared metadata by checksum handler maps.

Dependencies and integration: depends only on `<string>`, making it lightweight and reusable in unit tests. It is included by checksum handler headers.

Risks and test signals: getters return by value rather than reference, which is safe but may allocate. Unit tests should assert exact names for md5, sha aliases, adler/adler32 compatibility, and padding choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksum.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.cc -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.cc

Purpose: implements checksum algorithm configuration and negotiation for HTTP `Want-Digest` and `Want-Repr-Digest` headers.

Important APIs and control flow: `configure()` initializes a static map of supported algorithms, then parses the configured checksum list. `initializeCksumsMaps()` registers md5, adler32/adler, sha1/sha-256/sha-512, UNIX cksum, crc32, and crc32c mappings. `initializeXRootDConfiguredCksums()` parses config entries like `0:adler32`, stores HTTP-compatible configured checksum pointers, and records non-IANA/unknown names. `getChecksumToRunWantDigest()` lowercases and strips q-values from user digests, returns the first configured checksum requested by the client, or the first configured checksum as fallback. `getChecksumToRunWantReprDigest()` chooses the configured checksum with the highest client preference, defaulting to the first configured entry.

State and persistence: static `XROOTD_DIGEST_NAME_TO_CKSUMS` owns checksum objects; each handler instance stores raw pointers into that map plus unknown configured names. There is no durable state.

Dependencies and integration: used by HTTP request handling to decide which XRootD checksum command to run and how to name the HTTP response digest. It relies on `XrdOucTUtils::splitString()` and `XrdOucUtils::trim()`.

Risks and test signals: repeated `configure()` appends to instance vectors without clearing and reinitializes static maps; tests should check idempotence expectations. `getElement(..., position)` assumes the split has enough elements, so malformed config or q-value strings can throw/out-of-range depending split behavior. Tests should cover malformed config, duplicate aliases, adler32 adding both adler32 and adler, unknown algorithms, case-insensitive Want-Digest, and tie behavior for Want-Repr-Digest map ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.hh -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.hh

Purpose: declares the implementation and public wrapper for HTTP checksum negotiation.

Important APIs/types: `XrdHttpChecksumHandlerImpl` owns configuration logic and exposes raw checksum pointers for selected algorithms, non-IANA configured names, and testing visibility into configured checksums. `XrdHttpChecksumHandler` is a thin facade forwarding `configure()`, `getChecksumToRunWantDigest()`, `getChecksumToRunWantReprDigest()`, and `getNonIANAConfiguredCksums()` to its implementation member.

State and persistence: the implementation combines static supported-checksum maps with per-instance configured checksum raw pointers. The raw pointers are valid as long as the static map contents remain alive and stable.

Dependencies and integration: includes checksum metadata and standard containers. The facade is likely embedded in the HTTP protocol/request handling layer.

Risks and test signals: exposing raw pointers to objects owned by a static map makes map reinitialization and concurrency important. Unit tests should exercise configure-before-use, no-compatible-checksum behavior returning `nullptr`, preference selection, and multiple handler instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpChecksumHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.cc -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.cc

Purpose: implements `XrdHttpExtReq`, the request summary and response adapter passed to external HTTP extension plugins.

Important APIs and control flow: response helpers delegate to the owning `XrdHttpProtocol`: `SendSimpleResp()`, `StartSimpleResp()`, `SendData()`, `StartChunkedResp()`, `ChunkResp()`, and `BuffgetData()` all return `-1` if no protocol pointer exists. `GetClientID()` asks the underlying `XrdLink` for a client string. `GetSecEntity()` returns the protocol security entity. The constructor copies request verb/resource, references the request header map, injects XRootD-specific synthetic headers for query/fullresource/protocol, extracts client DN/host/groups from `SecEntity`, and exposes packet marking, SciTag, Repr-Digest, Want-Repr-Digest, credential forwarding, and request length.

State and persistence: `XrdHttpExtReq` stores request snapshot fields plus a reference to the original header map; modifying `headers` can affect the request's header map. No durable state is written.

Dependencies and integration: bridges `XrdHttpReq`, `XrdHttpProtocol`, `XrdLink`, `XrdSecEntity`, and plugin code implementing `XrdHttpExtHandler`. It is built into `XrdHttpUtils` for plugins.

Risks and test signals: `StartSimpleResp()` ignores its `keepalive` argument and passes `true`, which should be verified against intended API. Header reference lifetime depends on the original request. Tests should cover null-protocol guards, synthetic headers, security field trimming, chunked response lifecycle, body buffering with wait/no-wait, and digest map propagation to plugins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.hh -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.hh

Purpose: defines the external HTTP handler plugin ABI and the request object supplied to plugins.

Important APIs/types: `XrdHttpExtReq` exposes HTTP verb/resource, mutable headers reference, client identity fields, length, packet-marking handle, TPC credential-forwarding flag, SciTag, Repr-Digest and Want-Repr-Digest maps, security entity access, request body buffer access, and response-sending helpers. `XrdHttpExtHandler` is an abstract base with `MatchesPath()`, `ProcessReq()`, and `Init()`. The header declares the required plugin factory `XrdHttpGetExtHandler()` and `XrdHttpExtHandlerArgs` macro.

State and persistence: plugin state is owned by concrete handlers; the request object is per-request adapter state and references protocol/request internals.

Dependencies and integration: private installed header for HTTP extension plugins. It depends on `XrdNetPMark`, forward-declared XRootD protocol/security types, and the XRootD version-info convention for plugin ABI tracking.

Risks and test signals: this is ABI-facing; field layout and virtual method changes can break plugins. Tests should include building a minimal plugin, path matching, request processing, factory symbol loading, and version-info declaration compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.cc -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.cc

Purpose: implements parsers for HTTP digest headers, Content-Length, and Transfer-Encoding. These helpers centralize security-sensitive header interpretation for the HTTP protocol.

Important APIs and control flow: `parseReprDigest()` splits comma-separated entries, expects `<name>=:<base64>:`, trims the name/value, base64-decodes the digest to hex bytes via `base64DecodeHex()`, lowercases the digest name, and stores it in an output map while ignoring malformed entries. `parseWantReprDigest()` parses comma-separated `<name>=<uint8>` preferences, lowercases names, clamps preferences to 10, and discards invalid values. `parseContentLength()` strips trailing CRLF/OWS, rejects empty, non-digit, signed, embedded-whitespace, and overflow values, returning distinct negative error codes. `parseTransferEncoding()` splits tokens, trims/lowercases them, requires whole-token `chunked`, and requires it to be the final non-empty token.

State and persistence: all functions are stateless and write only caller-supplied maps or return codes.

Dependencies and integration: used by `XrdHttpProtocol`/request parsing to populate request digest maps and validate message framing. It relies on `XrdOucTUtils`, `XrdOucUtils`, and `XrdHttpUtils::base64DecodeHex`.

Risks and test signals: Content-Length and Transfer-Encoding parsing are request-smuggling defenses and need exhaustive malformed-input tests. Repr-Digest silently ignores malformed data, so callers must decide whether leniency is acceptable. Tests should cover whitespace, case, duplicate keys, invalid base64, overflow, plus/minus signs, multiple TE codings, `chunked` substrings, and chunked-not-last.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.hh -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.hh

Purpose: declares static HTTP header parsing utilities for digest negotiation and safe request framing.

Important APIs/types: `parseReprDigest()` fills a map of digest name to decoded digest value. `parseWantReprDigest()` fills a map of lowercase digest name to preference. `parseContentLength()` returns parsed `ssize_t` or specific negative errors for empty, malformed, or overflow values. `parseTransferEncoding()` returns success only when a non-empty transfer-coding list contains `chunked` as the last token, with specific negative errors for empty, missing, or misplaced chunked.

State and persistence: no class instances or static data are declared; output is entirely caller-owned.

Dependencies and integration: included by HTTP request parsing code. The comments explicitly tie behavior to RFC 9112 and RFC 7230 framing rules, making this a security boundary.

Risks and test signals: keep comments and implementation synchronized because callers may map error codes to HTTP 400 responses. Tests should assert every documented negative code and ensure no valid legacy inputs are accidentally rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpHeaderUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpModule.cc -->
## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpModule.cc

Purpose: provides the dynamically loaded HTTP protocol module entry points required by the XRootD protocol driver.

Important APIs and control flow: `XrdVERSIONINFO(XrdgetProtocol, xrdhttp)` declares version metadata for the protocol factory. `XrdgetProtocol()` logs initialization banners, calls `XrdHttpProtocol::Configure(parms, pi)`, returns a new `XrdHttpProtocol(false)` on success, and logs completion/failure. `XrdVERSIONINFO(XrdgetProtocolPort, xrdhttp)` marks the port callback. `XrdgetProtocolPort()` returns default HTTP/XRootD port `1094` when `pi->Port < 0`, otherwise returns the configured port.

State and persistence: no persistent state is owned here; module loading allocates a protocol object and relies on `XrdHttpProtocol` static configuration.

Dependencies and integration: compiled as the `XrdHttp-${PLUGIN_VERSION}.so` module. It includes `XrdVersion.hh` and `XrdHttpProtocol.hh` and exposes C symbols expected by XRootD.

Risks and test signals: module ABI depends on exact extern "C" symbol names and version macros. Tests should load the plugin through the protocol loader, verify failure when configuration fails, verify banner logging, and check port default/override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpModule.cc -->
