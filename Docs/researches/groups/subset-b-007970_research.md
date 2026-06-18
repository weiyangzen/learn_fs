# subset-b-007970 Research

Grouped research for the XRootD Scalable Service Interface files in `sources/distributed-fs/xrootd/src/XrdSsi`. Each section preserves the original source path and is intended to be split into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResponder.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResponder.hh

## Purpose
`XrdSsiResponder.hh` declares the protected server-side response helper used by SSI service task objects to bind to an `XrdSsiRequest`, read request input, post alerts, and send exactly one final response. It is deliberately a companion/friend of `XrdSsiRequest`, hiding the request internals behind a responder API while preserving strict ownership and lifetime rules.

## Important APIs and Types
The public binding API is `BindRequest(XrdSsiRequest&)` and `UnBindRequest()`. Protected response methods include `Alert`, `GetRequest`, `ReleaseRequestBuffer`, `SetMetadata`, `SetErrResponse`, `SetNilResponse`, `SetResponse(const char *, int)`, `SetResponse(long long, int)`, and `SetResponse(XrdSsiStream *)`. The abstract `Finished(XrdSsiRequest&, const XrdSsiRespInfo&, bool cancel)` callback is the required cleanup hook for derived responders. `Status` reports `wasPosted`, `notPosted`, or `notActive`. `MaxMetaDataSZ` and `MaxDirectXfr` both cap direct metadata/data transfer at 2 MiB.

## Control Flow
A service-created responder first calls `BindRequest`, then may inspect request data or set metadata, and finally posts one response. The implementation in `XrdSsiResponder.cc` validates that a request is still bound, locks the responder mutex before the request mutex, fills `XrdSsiRespInfo`, and calls `XrdSsiRequest::ProcessResponse`. When the request finishes or is canceled, `XrdSsiRequest::Finished` invokes the derived `Finished` method; only after that should the responder call `UnBindRequest`.

## State and Persistence
The class persists no disk state. Its in-memory state is `spMutex`, `reqP`, and reserved ABI fields. The comments document that response buffers, metadata buffers, and stream objects must remain valid until `Finished` runs, so derived responders own these resources until the framework hands them back.

## Dependencies and Integration Points
It depends on `XrdSsiRequest.hh`, `XrdSsiStream`, `XrdSsiRespInfo`, `XrdSsiRespInfoMsg`, and SSI mutex semantics. Friend access is granted to `XrdSsiRequest` and `XrdSsiRRAgent`. `XrdSsiTaskReal` derives from this responder path to translate endpoint responses into SSI responses.

## Risks and Test Signals
The main risks are response-after-finish races, posting multiple responses, deleting a responder before unbinding, and buffers that are freed before `Finished`. Tests should exercise normal bind/respond/finish/unbind, cancellation, responder destruction while bound, metadata length bounds, direct transfer limit behavior, nil/error/file/stream responses, and alert recycling when no request is bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResponder.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.cc

## Purpose
`XrdSsiScale.cc` implements the lightweight channel allocator used by SSI client-side session handling to spread requests across endpoint user/channel identifiers and optionally grow that spread under load.

## Important APIs and Functions
`getEnt()` returns an available channel entry or `-1` when all entries are saturated. `retEnt(int)` releases a previously allocated entry. `rsvEnt(int)` reserves a specific existing entry for reusable sessions. `setSpread(short)` configures a fixed spread or, when negative, enables auto-tuning. Private helpers `Tune` and `Retune` manage expansion and the transition from newly added channels back into the full round-robin set.

## Control Flow
`getEnt` scans from `nowEnt` to the current spread, increments the first `pendCnt` below `maxPend`, and classifies the request as active in the original partition or re-active in a newly tuned partition. If a full scan fails and auto-tune is enabled, `Tune` expands the spread and retries. `retEnt` decrements a pending count and triggers `Retune` once the original partition has drained enough relative to the new partition.

## State and Persistence
All state is in memory under `entMutex`: pending counts per entry, active counts, current/beginning scan positions, spread size, and auto-tune flags. There is no persistence. The global `XrdSsi::sidScale` in `XrdSsiServReal.cc` is the process-wide allocator.

## Dependencies and Integration Points
The implementation uses `XrdSysMutex` and `XrdSysError` logging. `XrdSsiServReal` obtains new entries with `getEnt`, `XrdSsiSessReal` reserves/releases entries for reusable tasks, and endpoint URLs embed the user entry when non-zero.

## Risks and Test Signals
Risks concentrate around unsigned counter boundaries, `maxPend` saturation, and partition retuning under concurrent release. Tests should cover fixed spread, negative auto-spread, saturation returning `-1`, reserve/release on invalid entries, retune logging, expansion caps at `maxSprd`, and heavy concurrent `getEnt`/`retEnt` cycles that leave all pending counts balanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.hh

## Purpose
`XrdSsiScale.hh` declares the SSI channel scaling allocator. It provides a small concurrency-safe object that tracks pending request pressure per channel and exposes the constants that define default spread, hard limits, and auto-tuning thresholds.

## Important APIs and Types
The public surface is `getEnt`, `retEnt`, `rsvEnt`, and `setSpread`. Constants include `defSprd` 4, `maxSprd` 1024, `maxPend` 64000, and tuning thresholds `minTune`, `midTune`, `maxTune`, and `zipTune`. Private fields are protected by `entMutex` and include `Active`, `reActive`, `begEnt`, `nowEnt`, `curSpread`, `autoTune`, `needTune`, and `pendCnt[maxSprd]`.

## Control Flow
The header establishes that callers must treat entries as leased resources: acquire with `getEnt` or `rsvEnt` and return through `retEnt`. `setSpread` can switch from fixed spread to auto-tuned spread and vice versa.

## State and Persistence
State is volatile process memory only. The constructor initializes a four-channel fixed spread with zero pending counts; no state is serialized across restarts.

## Dependencies and Integration Points
The class depends only on C integer/string headers and `XrdSysPthread.hh`. It is used by the client-side SSI service/session implementation to control endpoint stream identifiers embedded in URLs and to enforce maximum pending work per entry.

## Risks and Test Signals
The ABI exposes constants but not internal layout stability. Tests should verify constructor defaults, spread clamping, negative spread enabling auto-tune, reservation failure after `maxPend`, and that `retEnt` ignores invalid or already-empty entries without underflowing counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiScale.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.cc

## Purpose
`XrdSsiServReal.cc` implements the concrete client-side `XrdSsiService` that routes SSI requests to endpoint servers using `XrdCl::File` sessions. It manages session allocation, reusable resource caching, endpoint URL construction, stream entry allocation, and service shutdown.

## Important APIs and Functions
`ProcessRequest` is the main entry point. `Recycle` returns or deletes sessions. `Stop` implements service shutdown semantics. `StopReuse` removes a cached reusable session. Private helpers `Alloc`, `GenURL`, and `ResReuse` allocate/reinitialize sessions, build `xroot://` endpoint URLs, and handle reusable/discard resource options.

## Control Flow
`ProcessRequest` rejects empty resource names, checks the reusable cache under `rcMutex`, obtains a channel from global `sidScale`, builds an endpoint URL containing manager node, resource name, avoid list, affinity, user, CGI info, and optional user entry, then allocates a session and provisions it. Held reusable sessions are stored in `resCache` after provisioning starts. A cache hit calls `Run` on the existing session unless discard/retry semantics force unhold and replacement.

## State and Persistence
The service owns in-memory session pools only: `freeSes`, `freeCnt`, `freeMax`, `actvSes`, `doStop`, `manNode`, and `resCache`. No state is persisted. Reuse cache keys combine `rUser`, `"@"`, and `rName`.

## Dependencies and Integration Points
It integrates `XrdSsiResource`, `XrdSsiRequest`, `XrdSsiSessReal`, `XrdSsiRRAgent`, `XrdSsiScale`, `XrdSsiUtils`, and SSI tracing. It uses `ENOSR`/`ENOSPC` fallback for stream exhaustion and feeds endpoint URLs to `XrdSsiSessReal::Provision`.

## Risks and Test Signals
Important risks include cache/session lifetime under concurrent discard, URL buffer overflow, leaking a channel entry on early returns, and `Stop` deleting `this`. Tests should cover missing resource names, long URL fields, retry/discard cache bypass, reusable session reuse after open, provision failure recycling, free-list limits, immediate and delayed stop, and `StopReuse` racing with `Recycle`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.hh

## Purpose
`XrdSsiServReal.hh` declares the concrete service implementation used on the client side of SSI routing. It specializes `XrdSsiService` with endpoint session pooling and resource reuse support.

## Important APIs and Types
The class overrides `ProcessRequest` and `Stop`, and adds `Recycle` and `StopReuse` for session lifecycle management. Private `Alloc`, `GenURL`, and `ResReuse` are the implementation hooks used by the `.cc` file. State includes a resource cache map from string keys to `XrdSsiSessReal*`, two mutexes, a manager node string, a free-session list, active/free counts, and stop state.

## Control Flow
The declaration shows a split between request processing, free-list recycling, and cache eviction. `Recycle` is called by sessions after unprovision/shutdown; `StopReuse` lets a session or service remove a reusable key before it becomes invalid.

## State and Persistence
All state is volatile. The constructor duplicates the manager contact string and sets the maximum retained session objects from `hObj`. The destructor frees `manNode` and free sessions.

## Dependencies and Integration Points
It depends on `XrdSsiService`, `XrdSsiSessReal`, `XrdSsiResource`, STL `map`, and `XrdSysMutex`. It is instantiated by SSI provider/client plumbing outside this work item.

## Risks and Test Signals
Raw session pointers in the cache and free list make ownership discipline central. Tests should check destructor cleanup with free sessions, cache erasure on reuse stop, active count accounting, and that `Stop(true)` refuses active sessions while `Stop(false)` allows completion-driven deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiServReal.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.cc

## Purpose
`XrdSsiService.cc` provides the global SSI provider pointer and the default implementation of `XrdSsiService::Prepare`.

## Important APIs and Functions
The file defines `XrdSsi::Provider = 0`. `XrdSsiService::Prepare(XrdSsiErrInfo&, const XrdSsiResource&)` asks the provider whether the resource exists and returns success for any status other than `notPresent`.

## Control Flow
When a derived service does not override `Prepare`, the SSI server can use this default path to validate resource availability. If `Provider` is set and `QueryResource(rName)` reports present or pending, preparation succeeds; otherwise `eInfo` is set to `"Resource not available."` with `ENOENT`.

## State and Persistence
Only the process-global provider pointer is stored. It is initialized during SSI configuration and is not persisted.

## Dependencies and Integration Points
The file depends on `XrdSsiProvider.hh` and `XrdSsiService.hh`. `XrdSsiSfsConfig::ConfigSvc` assigns `Provider`, while `XrdSsiSfs` and `XrdSsiStat` also query it for locate/stat behavior.

## Risks and Test Signals
The default is intentionally simple and treats pending resources as acceptable. Tests should cover null provider, provider returning present, pending, and not-present, and correct `ENOENT` propagation. Integration tests should verify services that need authorization or redirection override `Prepare`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.hh

## Purpose
`XrdSsiService.hh` defines the abstract Scalable Service Interface service contract. It is used both client-side, where many service instances may exist, and server-side, where one provider-supplied service processes all requests.

## Important APIs and Types
`SsiVersion` is the ABI/version gate. `GetVersion` returns that version. `Attach` is a virtual hook for foreground reattachment to backgrounded requests. `Prepare` is an optional preflight hook for resource authorization, redirect, or stall behavior. `ProcessRequest` is pure virtual and returns all results via the request callbacks. `Stop` is a client-side lifecycle hook with immediate or deferred semantics.

## Control Flow
Server-side SSI can call `Prepare` before subsequent requests and `ProcessRequest` to execute work. `Attach` receives the original server request and optional resource description, allowing services to reject attach attempts when the attaching client should not inherit the original detached work.

## State and Persistence
The base class stores no data. Derived classes own all request, session, and service state. The protected destructor enforces lifecycle through `Stop` rather than direct deletion.

## Dependencies and Integration Points
The contract references `XrdSsiErrInfo`, `XrdSsiRequest`, and `XrdSsiResource`. Providers return service objects through `XrdSsiProvider::GetService`; client and server plugin entry points must agree on `SsiVersion`.

## Risks and Test Signals
ABI mismatch is a key integration risk. Tests should verify version checking, default `Attach` acceptance, default `Stop` return values, and service-specific `Prepare` handling for EAGAIN redirect, EBUSY stall, and authorization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.cc

## Purpose
`XrdSsiSessReal.cc` implements the endpoint session object used by `XrdSsiServReal`. A session owns one `XrdCl::File` connection to an endpoint resource, queues one or more SSI task objects against it, handles asynchronous open/close events, and coordinates reusable-session shutdown.

## Important APIs and Functions
Public lifecycle methods implemented here include destructor cleanup, `InitSession`, `Provision`, `Run`, `TaskFinished`, `UnHold`, `Unprovision`, and `XeqEvent`. Private helpers `NewTask`, `RelTask`, and `Shutdown` allocate tasks, recycle/free them, and return the session to the service.

## Control Flow
`Provision` opens the endpoint file with optional refresh for retries and registers the session as the `XrdCl::ResponseHandler`. It immediately allocates a task and marks `inOpen`. `XeqEvent` handles the open completion: on failure it schedules errors on all pending tasks; on success it captures the endpoint `DataServer` property and sends queued requests. `Run` is used for an already held session and reserves the original channel entry before creating and sending a task. `TaskFinished` removes the task, releases the scale entry, and closes the endpoint when no non-held work remains.

## State and Persistence
Session state is in memory: session/task identifiers, endpoint file, task lists, free task list, resource key, resource/session names, endpoint node, open/held/reuse flags, user entry, and allocation budget. There is no disk persistence.

## Dependencies and Integration Points
The session integrates `XrdCl::File`, SSI request/task/agent utilities, global scheduler cleanup jobs, global `sidScale`, `XrdSsiServReal::Recycle`, and `XrdSsiTaskReal::SendRequest`. It uses a recursive session mutex plus a shared task mutex assigned to requests through `XrdSsiRRAgent::SetMutex`.

## Risks and Test Signals
Risks include object invalidation after `Shutdown`, callback ordering between task finish and open completion, leaked channel reservations when task creation fails, and held-session reuse after endpoint errors. Tests should cover open success/failure, multiple queued tasks before open completes, close failure recycling=false, unhold cleanup scheduling, retry refresh flag, `DataServer` property absence, and task ID wraparound boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.hh

## Purpose
`XrdSsiSessReal.hh` declares the client-side endpoint session object for SSI. It is both a session state holder and an `XrdSsiEvent` callback receiver for endpoint file open/close completions.

## Important APIs and Types
Public methods include `InitSession`, `Provision`, `Run`, `TaskFinished`, `UnHold`, `Unprovision`, `XeqEvent`, `GetKey`, `GetSID`, `SetKey`, `Lock`, `UnLock`, and `MutexP`. `epFile` is public because tasks need endpoint I/O access. Private helpers create/release tasks and handle shutdown.

## Control Flow
The header exposes a state machine: provision opens the endpoint, `XeqEvent` transitions out of open state and sends queued tasks, task completions decide whether to unprovision, and unhold removes reusable state.

## State and Persistence
The object stores endpoint and task state only in memory. The reusable resource key is duplicated and freed locally. `sessID` and `nextTID` identify sessions/tasks within the process, not across restarts.

## Dependencies and Integration Points
It depends on `XrdCl::File`, SSI atomics/events, SSI mutexes, `XrdSsiServReal`, and `XrdSsiTaskReal`. It is owned and recycled by `XrdSsiServReal`.

## Risks and Test Signals
The class relies on callers knowing when methods return with `sessMutex` unlocked or the object invalidated. Tests should inspect unprovision paths, free-task reuse when held, no-reuse marking, cleanup job behavior, and public `epFile` access under task concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.cc

## Purpose
`XrdSsiSfs.cc` implements the XRootD filesystem plugin wrapper for SSI. It initializes SSI configuration, exposes the `XrdSfsGetFileSystem2` entry point, routes locate/stat-like requests to SSI provider state, and optionally delegates ordinary filesystem operations to a stacked native filesystem for configured paths.

## Important APIs and Functions
The external entry point is `XrdSfsGetFileSystem2`. Filesystem overrides include `chksum`, `chmod`, `exists`, `fsctl`, `getStats`, `getVersion`, `mkdir`, `prepare`, `rem`, `remdir`, `rename`, two `stat` overloads, `truncate`, plus private `Emsg`, `Split`, and `setFeatures`.

## Control Flow
Initialization stores the native filesystem pointer in global `theFS`, wires logging/tracing/stats, configures SSI, and returns a static `XrdSsiSfs`. Most namespace operations delegate to `theFS` only when `fsChk` is enabled and `FSPath.Find(path)` matches; otherwise they return `ENOTSUP`. `fsctl` handles `SFS_FSCTL_LOCATE` by checking SSI provider resource status and returning this server's network destination through `XrdNetIF`.

## State and Persistence
The plugin uses process-global pointers for provider, native filesystem, network interface, logger, trace, and stats. No persistent state is written. `freeMax` controls retained file/session object limits elsewhere.

## Dependencies and Integration Points
It integrates XrdSfs interfaces, XrdCms locate semantics, `XrdSsiProvider`, `XrdSsiSfsConfig`, `XrdSsiStats`, `XrdNetIF`, `XrdOucErrInfo`, and `XrdSecEntity`. `newDir` and `newFile` allocate SSI-specific directory/file objects declared in the header.

## Risks and Test Signals
Risks include misconfigured stacking causing legitimate filesystem operations to return `ENOTSUP`, locate response formatting, `Split` not null-terminating copied paths after `strncpy`, and static object lifecycle. Tests should cover plugin initialization failure, locate for present/pending/missing resources, path delegation through `fspath`, checksum delegation toggle, stats composition, IPv4/IPv6/hname locate flags, and each unsupported operation error message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.hh

## Purpose
`XrdSsiSfs.hh` declares the SSI filesystem plugin class derived from `XrdSfsFileSystem`. It is the server-facing XRootD filesystem adapter that creates SSI directory/file objects and implements or delegates filesystem namespace operations.

## Important APIs and Types
`newDir` returns `XrdSsiDir`; `newFile` returns `XrdSsiFile`. The class overrides checksum, namespace mutation, existence, fsctl, stats, version, prepare, stat, and truncate methods. Static `setMax` controls `freeMax`. Private helpers format errors and split opaque CGI data from paths.

## Control Flow
The header indicates that this class sits in the XrdSfs callout vector. Operations either become SSI-specific calls in `XrdSsiFile`/`XrdSsiDir`, delegate to a previous filesystem, or reject unsupported namespace actions.

## State and Persistence
Only static `freeMax` is declared here; plugin/global state is defined in the `.cc` and config files. There is no per-instance persisted data, and the destructor comments that deletion is intentionally avoided.

## Dependencies and Integration Points
It depends on `XrdSfsInterface`, `XrdSsiDir`, `XrdSsiFile`, `XrdOucEnv`, and security entity types. `XrdSfsGetFileSystem2` constructs and returns the static instance.

## Risks and Test Signals
The class has a broad virtual API surface, so regressions often show as XRootD filesystem behavior changes rather than compile failures. Tests should cover new file/dir allocation, feature bits, delegation to stacked filesystems, and unsupported-operation return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.cc

## Purpose
`XrdSsiSfsConfig.cc` implements SSI plugin configuration. It parses `ssi.*` and `all.role` directives, initializes global SSI runtime objects, loads provider and optional CMS plugins, configures buffers and request limits, and obtains the server-side `XrdSsiService`.

## Important APIs and Functions
Public `Configure(const char *, XrdOucEnv *)` reads the config file and delegates to `Configure(XrdOucEnv *)` for phase-two initialization. Private functions include `ConfigCms`, `ConfigObj`, `ConfigSvc`, `ConfigXeq`, `Xlib`, `Xfsp`, `Xopts`, `Xrole`, and `Xtrace`.

## Control Flow
The file opens the config, captures SSI directives, validates that the role is server-compatible, validates `fspath` stacking requirements, then finds scheduler/environment/network objects. It creates buffer pools, configures CMS client/cluster behavior, loads `svclib` through `XrdSysPlugin`, resolves either `XrdSsiProviderServer` or `XrdSsiProviderLookup`, initializes the provider, and obtains the service unless running in CMS stat mode.

## State and Persistence
Configuration writes process-global state only: `SsiCms`, `Sched`, `BuffPool`, `FSPath`, `myIF`, `Provider`, `Service`, logger, response wait, request size limits, `fsChk`, and `detReqOK`. No config changes are persisted to disk.

## Dependencies and Integration Points
It integrates `XrdCms`, `XrdOucStream`, `XrdOuca2x`, `XrdSysPlugin`, `XrdSsiProvider`, `XrdSsiCms`, `XrdSsiFileReq`, `XrdSsiFileSess`, `XrdNetIF`, and XRootD versioning. It is used by both filesystem plugin startup and stat-info plugin startup.

## Risks and Test Signals
Risks include plugin symbol mismatches, incorrect role parsing, null environment pointers, option parsing bugs, and a likely typo where `detReqOK` is set from `fAut >= 0` instead of `fDet >= 0`. Tests should cover missing config, unknown directives, `svclib` load failure, provider init failure, CMS library/default paths, standalone role, fspath without stacked FS, trace/debug env, size/time option bounds, and CMS lookup mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.hh

## Purpose
`XrdSsiSfsConfig.hh` declares the configuration driver for the SSI filesystem/stat plugins. It owns parsed library paths, directive parameters, runtime role metadata, and the setup methods that build global SSI runtime state.

## Important APIs and Types
The public API is two `Configure` overloads and constructor/destructor. Public fields expose version, host/program/instance names, role, CMS cluster pointer, port, and mode flags (`isServer`, `isCms`). Private parsing/configuration methods match the directives handled in the `.cc` file.

## Control Flow
An instance is constructed with defaults derived from environment variables. `Configure(configFile, env)` parses the file and then calls `Configure(env)`, which loads CMS/provider/service objects.

## State and Persistence
The object owns duplicated strings for config filename and library/parameter directives and frees them in the destructor. Global runtime state is defined in the implementation file; this header stores no persistent data.

## Dependencies and Integration Points
Forward declarations cover `XrdOucEnv`, `XrdOucStream`, `XrdSsiCluster`, `XrdSsiServer`, and `XrdVersionInfo`. The class is instantiated by `XrdSfsGetFileSystem2` and `XrdOssStatInfoInit2`.

## Risks and Test Signals
Because many fields are public, tests should verify constructor defaults and cleanup after partial configuration failures. Integration tests should confirm CMS mode uses lookup provider symbol while normal server mode requires a service object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfsConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.cc

## Purpose
`XrdSsiShMam.cc` implements the default shared-memory map backend for `XrdSsiShMat`. It stores fixed-size typed values keyed by strings in a memory-mapped file, supports atomic publication by creating `.new` files and renaming them into place, and provides add/delete/get/enumerate/resize/sync operations.

## Important APIs and Functions
The public implementation covers `AddItem`, `Attach`, `Create`, `DelItem`, `Detach`, two `Enumerate` forms, `Export`, `GetItem`, `Info`, `Resize`, and three `Sync` forms. Internal helpers include `ExportIt`, `Find`, `Flush`, `HashVal`, `Lock`, `NewItem`, `ReMap`, `RetItem`, `SetLocking`, `Snooze`, `SwapMap`, `UnLock`, and `Updated`. The private on-disk header is `ShmInfo`.

## Control Flow
`Create` validates parameters, calculates header/index/item layout, creates `<path>.new`, sizes and maps it, initializes `ShmInfo`, and keeps relaxed locking until export. `Export` flushes if needed, optionally locks the previous file, renames the new file over the visible path, bumps the old version number to notify existing mappings, and resets locking. `Attach` waits for the file, locks it, maps it, validates type/implementation/hash compatibility, and checks inode stability. `AddItem`/`DelItem`/`GetItem` remap when version changes, optionally flock, find hash-chain entries, and update counts/free lists.

## State and Persistence
The map persists in a backing file whose first bytes are `ShmInfo`, followed by item storage and an index table. Runtime state tracks fd, mapping base/size, temp path, index pointer, slot/item/key sizing, locks, access mode, reuse/multiple-writer flags, version, timeout, and sync queue counters.

## Dependencies and Integration Points
The file depends on POSIX file, flock, mmap, rename, stat, pread/pwrite, zlib `crc32`, SSI atomics, `XrdSsiShMat`, and `XrdSysE2T`. It is constructed by `XrdSsiShMat::New` and wrapped by the templated `XrdSsi::ShMap<T>` API.

## Risks and Test Signals
Risks include crash consistency around rename/version bump, stale mappings during resize/export, `Info` buffer length off-by-one checks, reuse/free-list races, `Flush` returning the inverse of the local `rc` expectation, and sync queue size zero causing immediate flush checks. Tests should cover create/export/attach compatibility, add duplicate with and without replace, delete with/without returned value, reuse on/off, multiple writer locking, enumerate while updating, resize preserving keys, version-triggered remap, timeout waiting, permission validation, and sync mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.hh

## Purpose
`XrdSsiShMam.hh` declares `XrdSsiShMam`, the default mmap-backed shared-memory table implementation behind the abstract `XrdSsiShMat` interface.

## Important APIs and Types
It implements all `XrdSsiShMat` virtual methods: add, attach, create, export, delete, detach, enumerate, get, info, resize, and sync. Private `MemItem` stores a hash and atomic next offset. `LockType` distinguishes read-only and read-write locks. `XLockHelper` combines process/thread locking and deferred flush behavior.

## Control Flow
Public calls acquire a reader or writer helper, possibly remap if a newer file version is visible, optionally take a file lock, then perform hash-table operations. Destruction detaches the mapping and destroys pthread locks.

## State and Persistence
The header exposes the runtime fields used to represent the mapped file, layout sizes, locking policy, sync policy, access mode, and reuse/multiple-writer behavior. The persistent layout itself is defined privately in the `.cc` file.

## Dependencies and Integration Points
It depends on pthread locks, SSI atomics, and `XrdSsiShMat`. It is instantiated through `XrdSsiShMat::New` and used by `XrdSsi::ShMap<T>`.

## Risks and Test Signals
Tests should verify lock helper cleanup on errors, destructor safety after partial create/attach failure, RO versus RW access checks, and ABI stability for fields hidden behind the abstract interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMap.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMap.hh

## Purpose
`XrdSsiShMap.hh` defines the public templated typed key/value map API over `XrdSsiShMat`. It lets callers create or attach a shared-memory map for values of type `T` without directly handling raw buffers, implementation selection, or hash identifiers.

## Important APIs and Types
Namespace types include `ShMap_Access`, `ShMap_Parms`, `SyncOpt`, and `ShMap_Hash_t`. `ShMap<T>` exposes `Attach`, `Create`, `Detach`, `Export`, `Add`, `Del`, `Enumerate`, `Exists`, `Get`, `Info`, `Rep`, `Resize`, and `Sync`. The template stores an `XrdSsiShMat*`, optional hash function, type name, and implementation name. The method bodies are included from `XrdSsiShMap.icc`.

## Control Flow
`Create`/`Attach` build `XrdSsiShMat::NewParms`, allocate an implementation through `XrdSsiShMat::New`, and then delegate. Operations compute an optional caller-provided hash before forwarding to the abstract backend. `Attach` retries a bounded number of times on `EAGAIN`, which indicates the backing inode changed while attaching.

## State and Persistence
The template owns only the backend object and duplicated type/implementation strings. Persistence is entirely backend-controlled through the mapped file and explicit `Export`/`Sync`.

## Dependencies and Integration Points
It depends on `XrdSsiShMat` and the inline implementation file. The default implementation is `XrdSsiShMam`, but the abstraction leaves room for alternative `XrdSsiShMat` implementations.

## Risks and Test Signals
Risks include option-bit parsing using high-bit masks, custom hash functions that return zero or unstable hash IDs, type names longer than backend limits, and `Resize(nullptr)` path using default resize parameters. Tests should cover typed create/attach mismatch, custom hash ID compatibility, add/get/replace/delete, enumeration termination, sync options, retry on attach `EAGAIN`, and destructor detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.cc

## Purpose
`XrdSsiShMat.cc` implements the factory for shared-memory table backends.

## Important APIs and Functions
`XrdSsiShMat::New(NewParms&)` fills in a default implementation name of `"XrdSsiShMam"` when none is provided, constructs `XrdSsiShMam` for that implementation, and returns `0` with `errno = ENOTSUP` for unsupported implementation names.

## Control Flow
The factory mutates `parms.impl` when nil, performs a string comparison, and returns a newly allocated backend object. There is no plugin loading in this implementation; adding backends requires extending this file.

## State and Persistence
The factory itself stores no state and persists nothing. The returned backend owns its mapping state and backing-file persistence.

## Dependencies and Integration Points
It depends on `XrdSsiShMat.hh` and `XrdSsiShMam.hh`. `XrdSsi::ShMap<T>` calls this factory during create/attach.

## Risks and Test Signals
Tests should cover null implementation defaulting, explicit `"XrdSsiShMam"`, unsupported implementation error propagation, and caller cleanup when allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.hh

## Purpose
`XrdSsiShMat.hh` declares the abstract shared-memory table interface. It defines the raw, untyped contract implemented by `XrdSsiShMam` and wrapped by `XrdSsi::ShMap<T>`.

## Important APIs and Types
The interface includes pure virtual methods for `AddItem`, `Attach`, `Create`, `Export`, `DelItem`, `Detach`, two `Enumerate` forms, `Info`, `GetItem`, `Resize`, and three `Sync` forms. `CRZParms` describes create/resize sizing and options. `NewParms` describes implementation name, backing path, type name, type size, and hash ID. Static `New` is the backend factory.

## Control Flow
Callers allocate through `New`, then attach or create, operate through raw buffers keyed by strings and hashes, and eventually detach/delete. Implementations must ensure compatibility checks for type/implementation/hash at attach time.

## State and Persistence
The base stores duplicated strings for implementation, path, type, plus type size and hash ID. The virtual destructor frees those strings but warns derived destructors must detach their own mappings first.

## Dependencies and Integration Points
It has minimal dependencies on C allocation/string headers. `XrdSsiShMam` derives from it; `XrdSsiShMap.hh` provides the typed public API.

## Risks and Test Signals
ABI stability and ownership are central: callers pass raw pointers, and derived classes own external resources. Tests should cover constructor duplication, destructor cleanup, backend attach compatibility, unsupported `Info` names, read-only update failure, and sync behavior delegated through the virtual interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMat.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStat.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStat.cc

## Purpose
`XrdSsiStat.cc` implements a default OSS stat-info plugin for SSI resources. It lets XRootD stat calls represent provider-managed SSI resources as synthetic regular files and propagate resource add/remove notifications to the SSI provider.

## Important APIs and Functions
The external C functions are `XrdSsiStatInfo` and `XrdOssStatInfoInit2`. `XrdSsiStatInfo` handles both notification calls with null `stat` buffer and stat queries with a real buffer. `XrdOssStatInfoInit2` configures SSI in CMS/stat mode and returns the stat callback.

## Control Flow
For null buffers, the function ignores changes for delegated filesystem paths and otherwise calls `Provider->ResourceRemoved` or `ResourceAdded`. For stat queries, it delegates to the native filesystem when `fsChk` and `FSPath` match. Otherwise it asks the provider for resource status, fills a synthetic regular-file mode for present resources, and marks pending resources with `S_IFBLK` unless `XRDOSS_resonly` is set.

## State and Persistence
The file relies on global provider/config/path state and writes no persistent data. Resource add/remove effects are delegated to the provider implementation.

## Dependencies and Integration Points
It integrates XrdOss stat-info interfaces, `XrdSsiProvider`, `XrdSsiSfsConfig`, `XrdOucPList`, and XRootD version exports. It is loaded by the plugin manager through `XrdOssStatInfoInit2`.

## Risks and Test Signals
Risks include path versus logical filename mismatches, synthetic mode semantics for pending resources, and partial initialization leaving `Provider` null. Tests should cover add/remove notifications, fspath delegation, present/pending/not-present statuses, `XRDOSS_resonly`, init failure on bad config, and versioned symbol loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.cc

## Purpose
`XrdSsiStats.cc` defines the global SSI statistics object and implements XML-like statistics formatting for SSI request/response/resource counters, optionally appended with native filesystem statistics.

## Important APIs and Functions
The file defines `XrdSsi::Stats`. `XrdSsiStats::XrdSsiStats` initializes all counters and filesystem pointer. `XrdSsiStats::Stats(char *, int)` returns either the maximum required buffer size or writes formatted statistics into the provided buffer.

## Control Flow
If `buff` is null, the method formats maximum integer values into a dummy buffer and adds the native filesystem stats size when present. Otherwise it locks `statsMutex`, formats all SSI counters into `buff`, unlocks, then appends `fsP->getStats` output if a filesystem pointer was configured.

## State and Persistence
All counters are in process memory and reset at construction. No statistics are persisted. `setFS` in the header attaches an optional native filesystem stats source.

## Dependencies and Integration Points
It depends on `XrdSfsInterface` and `XrdSsiStats.hh`. `XrdSsiSfs::getStats` calls this method, and other SSI code increments the public counters.

## Risks and Test Signals
There is an apparent formatting typo in `statfmt`: `<mdb>%lld</mdb` lacks a closing `>`. Tests should check XML parsability, buffer-size calculation, appending native stats without overflow, counter values under lock, and behavior when `blen` is smaller than the formatted SSI stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.hh

## Purpose
`XrdSsiStats.hh` declares the SSI statistics collector. It extends `XrdOucStats` and exposes counters that track SSI request bytes, response types, callback counts, errors, resource changes, and lifecycle events.

## Important APIs and Types
The public fields are the counters updated by SSI request/response code. `setFS(XrdSfsFileSystem*)` configures a chained filesystem stats provider. `Stats(char *, int)` formats the counters. The private state is only `fsP`; locking is inherited through `XrdOucStats`.

## Control Flow
Other SSI components increment public counters directly, and `XrdSsiSfs::getStats` asks this object to serialize them.

## State and Persistence
Counters live in memory and reset on process start. No persistence or periodic flushing exists in this class.

## Dependencies and Integration Points
It depends on `XrdSysPthread.hh`, `XrdOucStats.hh`, and forward declarations for `XrdSfsFileSystem` and `XrdStats`. The global instance is defined in `XrdSsiStats.cc`.

## Risks and Test Signals
Public mutable counters can be incremented without consistent locking if callers are careless. Tests should cover constructor zeroing, stats serialization after increments, native filesystem stats inclusion, and concurrent updates during formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStream.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStream.hh

## Purpose
`XrdSsiStream.hh` declares the stream abstraction used when an SSI response cannot or should not be sent as one direct data buffer. Streams may be active, where the producer supplies buffers, or passive, where the framework/client supplies buffers to fill.

## Important APIs and Types
Nested `Buffer` contains a data pointer, next pointer, and pure virtual `Recycle`. Stream methods are `GetBuff` for active streams, asynchronous `SetBuff(XrdSsiErrInfo&, char *, int)` for passive client-side streams, synchronous `SetBuff(XrdSsiErrInfo&, char *, int, bool&)` for passive streams, and `Type`. `StreamType` has `isActive` and `isPassive`.

## Control Flow
A responder posts a stream with `XrdSsiResponder::SetResponse(XrdSsiStream*)`. Server-side active streams return `Buffer` objects until `last` is true; receivers recycle each buffer. Passive streams fill caller-provided buffers either synchronously or by scheduling a callback to `ProcessResponseData`.

## State and Persistence
The base stores only the immutable stream type. Implementations own all buffer queues, file handles, or generated data. No persistence is defined by the interface.

## Dependencies and Integration Points
It depends on `XrdSsiErrInfo` and errno constants. `XrdSsiResponder`, `XrdSsiRequest`, and endpoint task/file-session code use this abstraction to transfer large or incremental responses.

## Risks and Test Signals
Default methods set `EOPNOTSUPP`, so implementations must override the correct method for their stream type. Tests should cover active buffer recycle, passive sync EOF/error semantics, async scheduling errors, `last` handling, type mismatches, and large responses that cross the direct-transfer threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStream.hh -->
