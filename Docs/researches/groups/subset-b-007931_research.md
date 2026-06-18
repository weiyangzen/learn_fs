# subset-b-007931 Research

Grouped source research for the XRootD S3 client plugin wrappers and selected `XrdCms` cluster-management components. Each source file has a marker-delimited section for deterministic reconciliation into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.hh -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.hh

## Purpose
Declares the `XrdClS3::Factory` plugin factory for mapping `s3://` client URLs onto the XRootD HTTP client plugin. It centralizes S3 URL translation, AWS V4 request signing, endpoint/region/service configuration, bucket credential lookup, and test/configuration setters.

## Important APIs, Types, and Functions
`Factory` derives from `XrdCl::PlugInFactory` and overrides `CreateFile()` and `CreateFileSystem()`. Static helpers include `GenerateHttpUrl()`, `GenerateV4Signature()`, `GetBucketFromHttpsUrl()`, `GetCredentialsForBucket()`, `PathEncode()`, `CanonicalizeQueryString()`, `CleanObjectName()`, `ExtractHostname()`, and `TrimView()`. The private `Credentials` struct stores access/secret key material.

## Control Flow
The factory is the entry point used by XrdCl plugin loading. File and filesystem wrappers call its static helpers on every S3 operation: first to translate a logical S3 URL into an HTTPS URL, then from HTTP header callouts to produce per-request authorization headers.

## State and Persistence Behavior
Configuration is static process state: endpoint, service, region, URL style, mkdir sentinel, default credentials, per-bucket credentials, and a bucket credential cache with timestamps. `m_init_once` guards initialization; `m_bucket_auth_map_mutex` protects cached credential reads/writes. There is no file persistence here, but credentials may be sourced from XRootD client configuration in the implementation.

## Dependencies and Integration Points
Depends on `XrdCl::PlugInFactory`, `XrdCl::FilePlugIn`, `XrdCl::FileSystemPlugIn`, `XrdCl::Log`, STL strings, maps, tuples, chrono, mutexes, and shared mutexes. It integrates with `XrdClS3File`, `XrdClS3Filesystem`, and the `XrdClHttpHeaderCallout` property used by the HTTP plugin.

## Risks and Edge Cases
Static setters and credential maps can affect all plugin instances in-process. V4 signing is sensitive to canonical path/query/header ordering and exact bucket extraction. Credential cache invalidation, per-bucket override precedence, and query cleaning are security-relevant. `SetBucketCredentials()` mutates `m_bucket_location_map` without the same visible lock used for the auth cache.

## Test Signals
Unit tests should cover virtual-hosted and path-style URL generation, bucket extraction, query canonicalization, object-name cleaning, path encoding, whitespace trimming, credential precedence/cache reset, and V4 signing against known AWS examples. Integration tests should verify signed HTTP requests through `XrdClS3::File` and `Filesystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3File.cc -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3File.cc

## Purpose
Implements the S3 file plugin by wrapping a real `XrdCl::File` that talks HTTPS. It translates the original S3 URL, forces creation of the underlying HTTP plugin object, injects an S3 signing header callout, and delegates file operations.

## Important APIs, Types, and Functions
Defines `OpenResponseHandler` and `CloseResponseHandler` to update `m_is_opened` around asynchronous open/close callbacks. Implements `File::GetFileHandle()`, `Open()`, `Close()`, `IsOpen()`, `GetProperty()`, `SetProperty()`, `Read()`, `PgRead()`, `VectorRead()`, `Write()` overloads, `Stat()`, and `S3HeaderCallout::GetHeaders()`.

## Control Flow
`Open()` rejects already-open files, calls `GetFileHandle()`, then opens the HTTPS URL through the wrapped file with an `OpenResponseHandler`. `GetFileHandle()` normalizes accidental double slash after the S3 bucket, calls `Factory::GenerateHttpUrl()`, validates the resulting `XrdCl::URL`, opens once with `OpenFlags::Compress` to instantiate the HTTP plugin, sets `XrdClHttpHeaderCallout` to the callout object's address encoded as hex, and stores the wrapped handle. All data methods then delegate to `m_wrapped_file`.

## State and Persistence Behavior
State is per plugin instance: open flag, cached HTTPS URL, logger, arbitrary property map protected by `m_properties_mutex`, a unique wrapped `XrdCl::File`, and the embedded signing callout. No durable persistence is used. The open flag is mutated from async response handlers, so it reflects successful callback completion rather than just synchronous method return.

## Dependencies and Integration Points
Depends on `XrdClS3Factory`, `XrdClS3File.hh`, `XrdCl::File`, `XrdCl::URL`, `XrdCl::ResponseHandler`, `XrdClHttp::HeaderCallout`, and the HTTP plugin's `XrdClHttpHeaderCallout` property convention.

## Risks and Edge Cases
Most methods assume `m_wrapped_file` is initialized; calling read/write/stat before successful `Open()` may dereference null. The callout pointer is passed as a string address, so lifetime must outlive the HTTP plugin object. `m_is_opened` is not atomic, which may matter for concurrent `IsOpen()` and callback execution. `GetFileHandle()` has careful but narrow double-slash normalization logic.

## Test Signals
Mocked HTTP-plugin tests should verify property injection, handler ownership/deletion, open/close flag transitions, error propagation from URL generation, and delegation of read/write/stat calls. Integration tests should assert Authorization headers are generated for GET, PUT, HEAD, and range reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3File.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3File.hh -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3File.hh

## Purpose
Declares the `XrdClS3::File` final `XrdCl::FilePlugIn` implementation used for S3 object I/O through XRootD's HTTP client.

## Important APIs, Types, and Functions
The class overrides the file plugin surface: `Open`, `Close`, `IsOpen`, `Read`, `PgRead`, `VectorRead`, `Write`, `Stat`, `GetProperty`, and `SetProperty`. Private `GetFileHandle()` lazily constructs the HTTPS handle. Nested `S3HeaderCallout` implements `XrdClHttp::HeaderCallout::GetHeaders()`.

## Control Flow
Callers interact through the standard XrdCl file API. The first open resolves the S3 URL and configures a wrapped HTTP file; subsequent file operations are forwarded to that handle. The nested header callout is invoked by the HTTP layer for each request and calls the factory signing function.

## State and Persistence Behavior
The object stores open status, original/open URL data, a logger pointer, an in-memory property map, a wrapped `XrdCl::File`, and an embedded header callout. No persistent filesystem state is owned by the wrapper.

## Dependencies and Integration Points
Includes `XrdClHttpHeaderCallout.hh` and `XrdClFile.hh`. Integrates with `XrdClS3Factory` at implementation time and with the HTTP plugin through a property that points at `m_header_callout`.

## Risks and Edge Cases
The declared `m_open_flags` is present but not used by the implementation read. Thread-safety covers property access but not all file lifecycle state. Header callout pointer wiring requires object lifetime discipline.

## Test Signals
Compile/API tests should ensure all `XrdCl::FilePlugIn` overrides match the current XrdCl ABI. Behavior tests should cover property get/set, open lifecycle, and header callout invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3File.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.cc -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.cc

## Purpose
Implements an S3 filesystem plugin that maps XRootD filesystem operations onto HTTPS/S3 operations. It supports directory listing through S3 `ListObjectsV2`, stat fallback from object to pseudo-directory, mkdir/rmdir through sentinel objects, and delegation of locate/query/remove/stat to endpoint-specific HTTP filesystem handles.

## Important APIs, Types, and Functions
Local helpers include `urlquote()`, `JoinUrl()`, `StatHandler`, `StatHandlerDirectory`, `DirListResponseHandler`, and `MkdirHandler`. Main methods are `Filesystem::DirList()`, `GetFSHandle()`, `Locate()`, `MkDir()`, `Query()`, `Rm()`, `RmDir()`, `Stat()`, property accessors, and `S3HeaderCallout::GetHeaders()`.

## Control Flow
`DirList()` converts S3 path to HTTPS bucket URL, appends `list-type=2`, delimiter, encoding, and prefix parameters, then downloads the listing with a signing callout. `DirListResponseHandler` parses XML into `XrdCl::DirectoryList`, follows continuation tokens until complete, and can short-circuit for existence checks. `Stat()` first delegates to HTTP stat; on not-found it issues a listing for the same prefix and converts a successful prefix match into directory `StatInfo`. `MkDir()` writes a zero-byte sentinel object and closes it asynchronously via `MkdirHandler`.

## State and Persistence Behavior
Per-instance state includes base `XrdCl::URL`, logger, properties, a shared-mutex-protected map from HTTPS endpoint to `XrdCl::FileSystem*`, and an embedded header callout. Persistent remote effects are S3 object creation/removal, especially sentinel files used to model empty directories.

## Dependencies and Integration Points
Depends on TinyXML, `XrdClS3DownloadHandler`, `XrdClS3Factory`, XrdCl URL/log/filesystem/stat/list classes, and the HTTP header callout property convention. It integrates S3 directory semantics into XRootD's filesystem plugin contract.

## Risks and Edge Cases
`urlquote()` uses `std::to_string(val)` after `%`, which emits decimal rather than two-digit hex percent encoding and may mishandle negative `char` values. XML parsing assumes a non-null root and specific S3 element names. Time parsing uses `mktime()` on UTC-looking `Z` timestamps, which can apply local timezone. Handler self-ownership patterns require every async path to release/delete exactly once. Endpoint handles are raw pointers and are not visibly freed in the destructor.

## Test Signals
Tests should exercise listing XML with files, common prefixes, continuation tokens, empty prefixes, sentinel-only directories, malformed XML, timeout expiry, and not-found stat fallback. Integration tests should verify mkdir/rmdir sentinel behavior and signed filesystem calls against an S3-compatible endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.hh -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.hh

## Purpose
Declares the final `XrdClS3::Filesystem` plugin that exposes S3 buckets/objects through the `XrdCl::FileSystemPlugIn` API.

## Important APIs, Types, and Functions
Overrides `DirList`, `Locate`, `MkDir`, `Query`, `Rm`, `RmDir`, `Stat`, `GetProperty`, and `SetProperty`. Private `GetFSHandle()` returns endpoint-specific wrapped `XrdCl::FileSystem` objects. Nested `S3HeaderCallout` signs HTTP filesystem requests.

## Control Flow
The filesystem instance holds a base S3 URL with path/query stripped. Operations join that base URL with the requested path, translate/sign as needed, and either perform custom S3 logic for directory-like operations or delegate to a cached HTTP filesystem handle.

## State and Persistence Behavior
The class owns in-memory properties, a cache of raw `XrdCl::FileSystem*` handles keyed by endpoint, the base URL, logger, locks, and a header callout. S3-visible persistence is created by implementation methods, not by the declaration itself.

## Dependencies and Integration Points
Includes the HTTP header callout interface and XrdCl plugin interface. Implementation integrates with TinyXML, S3 URL/signing factory helpers, and XRootD HTTP filesystem operations.

## Risks and Edge Cases
The header declares `m_is_opened` though filesystem open state is not used in the implementation. Raw handle ownership in `m_handles` needs destructor cleanup auditing. Property locking is narrow, while lifecycle and handle-cache access use a separate shared mutex.

## Test Signals
ABI compile tests should verify override signatures against XrdCl. Unit tests should cover handle caching, property access, base URL normalization, and callout lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdCms/CMakeLists.txt

## Purpose
Defines build integration for the XRootD cluster management service (`cmsd`), the XrdServer CMS client sources, and the local redirect plugin module.

## Important APIs, Types, and Functions
Adds CMS client/clustering source files to `XrdServer` with `target_sources()`. Defines the `cmsd` executable from Xrd core startup/config sources and many `XrdCms*` manager/server components. Defines the `XrdCmsRedirectLocal-${PLUGIN_VERSION}` module from `XrdCmsRedirLocal.cc/.hh`.

## Control Flow
CMake first attaches client-side CMS implementation files to the server library, then builds `cmsd`, applies GNU-specific `-msse4.2` as an interface compile option, links required libraries, and installs the executable and redirect-local plugin.

## State and Persistence Behavior
No runtime state. It controls build graph membership, linkage, and install destinations.

## Dependencies and Integration Points
Links `cmsd` against `XrdServer`, `XrdUtils`, thread, atomic, extra, and socket libraries. It integrates CMS code with top-level CMake variables such as `PLUGIN_VERSION`, `CMAKE_INSTALL_BINDIR`, and `CMAKE_INSTALL_LIBDIR`.

## Risks and Edge Cases
Source omissions here become link-time or runtime plugin availability failures. The GNU `target_compile_options(cmsd INTERFACE -msse4.2)` line may not apply as intended to the executable's own compilation because `INTERFACE` usage requirements are normally consumed by dependents.

## Test Signals
Build tests should verify `XrdServer`, `cmsd`, and `XrdCmsRedirLocal` build/install on supported compilers and platforms. Packaging checks should confirm installed binary and module names/locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.cc

## Purpose
Implements administrative and notification channels for `cmsd`: primary/proxy/admin login handling, suspension/resume commands, alternate data-server monitoring, event relaying, and forwarding of file availability/removal events to managers.

## Important APIs, Types, and Functions
Local `AdminReq` queues relay requests with static semaphore/mutex state. Thread entry points include `AdminLogin`, `AdminMonAds`, `AdminMonARE`, and `AdminSend`. Public methods implemented include `InitAREvents()`, `Login()`, `MonAds()`, `Notes()`, `Relay()`, `RelayAREvent()`, `Send()`, and `Start()`. Private helpers include `AddEvent()`, `BegAds()`, `CheckVNid()`, `Con2Ads()`, `do_Login()`, `do_Perf()`, `do_RmDid()`, and `do_RmDud()`.

## Control Flow
`Start()` launches the relay thread, optionally begins alternate data-server monitoring, then accepts admin sockets and spawns login handlers. `Login()` requires an initial `login` command and then dispatches text commands such as `resume`, `suspend`, `perf`, `rmdid`, and `newfn`. Primary login sets frontend state and hands the socket to `Relay()`. Notification sockets loop over `gone`, `have`, `stage`, and related events. ARE mode queues events to `RelayAREvent()`, which calls the external stat event function and informs managers.

## State and Persistence Behavior
Static state tracks admin relay queues, ARE queue/list/semaphore, primary-online flag, and optional startup sync semaphore. Instance state stores stream, server type/name, and primary flag. No durable storage is written, but CMS cluster state, prepare queues, and manager notifications are mutated.

## Dependencies and Integration Points
Depends on X/Y protocol headers, CMS config/manager/meter/prepare/state/trace, XrdNet sockets, name translation, semaphores, timers, and OSS stat callback types. Integrates with `XrdCmsManager::Inform`, `CmsState.Update`, `PrepQ`, and `XrdOucName2Name`.

## Risks and Edge Cases
Thread entry passes the address of local `InSock` into a new thread, creating a race if the accept loop overwrites it before the thread reads it. `AdminReq::numinQ` is read without locking in `Send()`. Several loops are intentionally infinite. Login and notification parsing trust command token order. Name translation failures can suppress events. Relay write failure requeues the current item and reconnect behavior depends on primary login.

## Test Signals
Tests should cover login role validation, VNID mismatch handling, suspend/resume state updates, duplicate primary rejection, relay queue overflow, notification command parsing, PFN/LFN translation paths, alternate data-server reconnect, and ARE callback delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.hh

## Purpose
Declares the `XrdCmsAdmin` class, the administrative socket/session object for CMS control, notification, relay, and ARE event handling.

## Important APIs, Types, and Functions
Public API includes `InitAREvents`, `Login`, `MonAds`, `setSync`, `Notes`, `Relay`, `RelayAREvent`, `Send`, and `Start`. Private API covers event addition, alternate data-server setup, VNID checking, ADS connection, and command-specific handlers.

## Control Flow
The class is used as a per-connection handler for admin sessions and as a holder of static relay/event queues shared by background threads. `Start()` and static thread entry points in the implementation drive the lifecycle.

## State and Persistence Behavior
Static members hold ARE callback/queue state, startup sync, mutexes, semaphore, and primary-online status. Instance members hold the `XrdOucStream`, role string, allocated server name, and primary marker.

## Dependencies and Integration Points
Includes CMS protocol/RR data, OSS stat info callback type, stream parsing, and pthread wrappers. Forward-declares sockets and token lists. It is integrated by `cmsd` startup and manager/server control paths.

## Risks and Edge Cases
The class mixes static global state and per-session state; tests need isolation or explicit resets. `Sname` is heap-owned and freed in the destructor. Static API is not namespaced under `XrdCms`, unlike some implementation globals.

## Test Signals
Compile tests should catch protocol and callback ABI drift. Unit or harness tests should instantiate sessions with mock streams/sockets and verify static state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsAdmin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.cc

## Purpose
Implements the CMS base filesystem existence checker and throttled lookup queue. It decides whether file existence can be answered locally, must be queued/rate-limited, or should be forwarded to other cluster nodes.

## Important APIs, Types, and Functions
Implements `Bypass()`, `Exists(XrdCmsRRData&, XrdCmsPInfo&, int)`, `Exists(char*, int, int)`, `hasDir()`, `Init()`, `Limit()`, `Pacer()`, `Queue()`, `Runner()`, `Start()`, and `Xeq()`. Thread entry points call `Pacer()` and `Runner()`.

## Control Flow
`Exists()` first checks whether local stat is enabled; otherwise it queues/forwards. With local stat, optional directory-miss caching can reject paths early. Rate limiting can allow inline execution, enqueue into a paced queue, or force queueing. `Pacer()` moves pending requests to the runnable queue at the configured rate; `Runner()` executes them and calls the configured callback. `Xeq()` performs final stat/forward callback logic.

## State and Persistence Behavior
In-memory state includes directory presence/miss hash entries with lifetimes, request queues with semaphores and high-water accounting, rate-limit counters, and mode flags. Filesystem state is only observed through `Config.ossFS->Stat`; prepare queue state can make missing staged files appear pending.

## Dependencies and Integration Points
Depends on CMS config, prepare queue, trace, `XrdOss` stat interface, SFS flags, timers, semaphores, and protocol request data. Callback `cBack` integrates lookup completion with higher-level routing/selection.

## Risks and Edge Cases
`Bypass()` logs to `std::cerr`, which may be noisy in production. Queue overrun handling logs but still enqueues. Path buffers are temporarily modified in-place around directory stat checks, requiring mutable/null-terminated input and careful restoration. Bad stat errors are rate-limited by counters and may hide intermittent problems.

## Test Signals
Tests should cover local stat online/pending/directory/missing cases, prepare-queue pending fallback, directory miss/present cache, rate-limit queue flow, queue overrun logging, callback behavior for local and non-local modes, and mutable path restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.hh

## Purpose
Declares the base filesystem lookup engine and its queued request record type for CMS file-location decisions.

## Important APIs, Types, and Functions
`XrdCmsBaseFR` stores route masks, request stream/modifier, path buffer, path length, and parent-directory position. `XrdCmsBaseFS` exposes `Exists()` overloads, `Init()`, `Limit()`, `Pacer()`, `Runner()`, `Start()`, retry setters/getters, and flags such as `Cntrl`, `DFSys`, `Immed`, and `Servr`.

## Control Flow
The header defines the contracts used by routing code: existence can return online, pending, unknown queued, or missing. Queue state is split into paced and runnable lists and consumed by background threads.

## State and Persistence Behavior
State includes callback pointer, directory hash cache, queue semaphores/lists/counters, retry counts, cache lifetimes, and mode flags. `XrdCmsBaseFR` may steal the request buffer from `XrdCmsRRData` and frees it in its destructor.

## Dependencies and Integration Points
Includes CMS path/list/request/types, generic hash, and pthread primitives. Exposes global `XrdCms::baseFS` for cluster components.

## Risks and Edge Cases
Ownership differs between the two `XrdCmsBaseFR` constructors, so misuse can lead to leaks or double frees. The callback pointer is raw and must outlive the baseFS object. Queue semantics depend on signed `PDirLen` encoding.

## Test Signals
Compile tests should catch struct/protocol field drift. Unit tests should cover `XrdCmsBaseFR` ownership behavior, `Init()` flag combinations, `Limit()` calculations, and retry defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.cc

## Purpose
Implements dynamic CMS blacklist/whitelist loading, matching, logging, and optional redirect target generation for cluster host admission decisions.

## Important APIs, Types, and Functions
Local `BL_Grip` manages temporary linked lists. `BL_Info` packs exact/wildcard/redirect metadata into an `XrdOucTList` value. Main methods are `AddBL()`, `AddRD()` overloads, `DoIt()`, `Flatten()`, `GetBL()`, `Init()`, `Present()`, and `MidNightTask::Ring()`.

## Control Flow
`Init()` chooses blacklist vs whitelist mode, resolves the file path, reads an initial file if present, schedules periodic `DoIt()`, and registers midnight logging. `DoIt()` stats the file, reloads on modification/removal, atomically swaps global lists under `blMutex`, updates the cluster, frees old lists, and reschedules itself. `Present()` scans exact or wildcard entries and returns allow/deny/redirect status.

## State and Persistence Behavior
Global state stores scheduler/cluster pointers, current real list, redirect vector, config filename, modification time, check interval, redirect count, and whitelist mode. Persistence is the external blacklist/whitelist file; the process holds parsed in-memory lists.

## Dependencies and Integration Points
Depends on scheduler jobs, CMS cluster update hooks, network address normalization, token/list/stream utilities, config environment, logger midnight tasks, and manager parsing utilities.

## Risks and Edge Cases
Wildcard matching uses one `*` with prefix/suffix lengths and may surprise users expecting glob semantics. Redirect data is flattened into a bounded 4096-byte buffer and truncated silently once full. `AddRD(XrdOucTList **, ...)` is declared `bool` but returns `-1` on errors, which converts to `true`; this is suspicious. Global mode/state make multiple independent blacklist instances impractical.

## Test Signals
Tests should parse exact names, wildcard names, IPv6 redirect specs, missing ports, too many redirects, file removal, reload failures, whitelist inversion, redirect buffer sizing, midnight logging, and `Present()` return conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.hh

## Purpose
Declares `XrdCmsBlackList`, an `XrdJob` that periodically reloads blacklist/whitelist configuration and answers host-present queries with optional redirect payloads.

## Important APIs, Types, and Functions
Public API is `DoIt()`, static `Init()`, and static `Present()`. Private helpers parse blacklist and redirect records and flatten redirect target lists. The documented `Present()` return values distinguish deny, allow, redirect size, and insufficient redirect buffer.

## Control Flow
The scheduler invokes `DoIt()` after `Init()` schedules the job. Runtime callers use `Present()` to query the current parsed list.

## State and Persistence Behavior
The header exposes no instance fields; implementation state is file-scope/global. It depends on an external list file for durable configuration.

## Dependencies and Integration Points
Includes `XrdJob.hh` and forward-declares cluster, scheduler, and list types. Used by CMS cluster admission/selection code.

## Risks and Edge Cases
Because most state is static, initialization order and test isolation matter. Callers must honor the redirect-buffer return convention to avoid dropping redirect data.

## Test Signals
Header-level tests should verify job inheritance and API compatibility with scheduler and cluster code. Behavior tests should focus on `Init()`/`Present()` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBlackList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.cc

## Purpose
Implements the CMS path-location cache used to remember which servers have, might have, or are being queried for a file, and to dispatch waiting requests when location data arrives.

## Important APIs, Types, and Functions
Defines global `XrdCms::Cache`, local scheduled `XrdCmsCacheJob`, and tick thread entry `XrdCmsStartTickTock`. Public methods implemented are `AddFile()`, `DelFile()`, `GetFile()`, `UnkFile()`, `WT4File()`, `Bounce()`, `Drop()`, `Init()`, and `TickTock()`. Private helpers are `Add2Q()`, `Dispatch()`, `getBVec()`, and `Recycle()`.

## Control Flow
`AddFile()` creates or updates path entries and dispatches read/write wait queues when enough location data is known. `GetFile()` returns current vectors, invalidating entries affected by server bounce clocks and query deadlines. `WT4File()` attaches callback info to an entry when clients should wait. `TickTock()` advances the cache clock, unloads expired entries, and schedules asynchronous recycle jobs.

## State and Persistence Behavior
All state is in memory: `XrdCmsNash` cache table, path anchor, valid server vector, bounce history, tick clock, nil-entry timeout, query/deadline settings, wait queues, and statistics. No durable cache exists; cluster events repopulate it.

## Dependencies and Integration Points
Depends on `XrdCmsKey`, `XrdCmsNash`, `XrdCmsSelect`, `XrdCmsRRQ`, scheduler jobs, timers, and mutexes. Integrates with server bounce/drop events and request callback queues.

## Risks and Edge Cases
Cache correctness depends on `TODRef` fast-path validation and bounce-clock math. `nilTMO` is raised to avoid infinite lookup delay but can still retain negative entries. Shared-everything vs shared-nothing dispatch behavior differs substantially. The fixed message in `Recycle()` reports cache allocator state and can be noisy under churn.

## Test Signals
Tests should cover add/update/delete semantics, pending vs online vectors, stale bounce invalidation, wait queue dispatch for read/write paths, DFS vs non-DFS dispatch, nil timeout expiry, tick unload/recycle behavior, and server drop removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.hh

## Purpose
Declares the CMS in-memory path-location cache and its public manipulation/administrative API.

## Important APIs, Types, and Functions
Public members include `Paths`, `AddFile`, `DelFile`, `GetFile`, `UnkFile`, `WT4File`, `Bounce`, `Drop`, `Init`, and `TickTock`. Private state includes `Bhistory`, mutex, `XrdCmsNash` table, bounced array, valid-node vector, clocks, timeout/delay fields, hit/miss counters, and DFS mode.

## Control Flow
Callers update or query cache entries around locate/prepare workflows, while the background tick thread ages entries and scheduled recycle jobs reclaim them.

## State and Persistence Behavior
The cache is process-local, protected by `myMutex`, and never deleted. Entry lifetime is controlled by tick windows and optional nil timeout. No disk persistence.

## Dependencies and Integration Points
Includes scheduler/job, key/nash/path list/select/types, and pthread wrappers. Exposes global `XrdCms::Cache`.

## Risks and Edge Cases
The `Bounced` array is indexed by server number up to `STMax`; callers must bound server IDs. The global singleton complicates isolated tests. Time values mix seconds and tick windows.

## Test Signals
Compile tests should catch `SMask_t`, `STMax`, and key API drift. Unit tests should validate constructor defaults and public method contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.cc

## Purpose
Provides the ABI-compatible default CMS client factory used when no external CMS client plugin is loaded.

## Important APIs, Types, and Functions
Defines `XrdCms::GetDefaultClient(XrdSysLogger*, int opMode, int myPort)`. It returns `XrdCmsFinderRMT` for redirector mode, `XrdCmsFinderTRG` for target/server mode, or null for unsupported mode combinations.

## Control Flow
The factory checks `opMode` flags in priority order: `IsRedir` first, then `IsTarget`. Construction arguments are passed through to the selected finder class.

## State and Persistence Behavior
No persistent state. It allocates a new client object for the caller, which owns the returned pointer.

## Dependencies and Integration Points
Depends on `XrdCmsClient.hh` and `XrdCmsFinder.hh`. It is part of the CMS plugin/client instantiation boundary described in the header.

## Risks and Edge Cases
If both redirector and target flags are set, redirector wins. Null return on unsupported mode must be handled by caller initialization. Allocation failures are not locally caught.

## Test Signals
Tests should verify opMode-to-class selection, null result for no recognized role, and ABI linkage for the factory function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.hh

## Purpose
Declares the CMS client abstraction used by XRootD OFS/cms integrations to locate files, forward metadata operations, prepare files, report server state, and query cluster space.

## Important APIs, Types, and Functions
`XrdCmsClient` defines virtual methods including `Configure`, `Locate`, `Space`, `Forward`, `Prepare`, `Added`, `Removed`, `Resume`, `Suspend`, `Resource`, `Reserve`, `Release`, `Managers`, and `Utilization`. It documents return and callback conventions. It defines `Persona` and mode flags `IsProxy`, `IsRedir`, `IsTarget`, and `IsMeta`, plus plugin factory typedef `XrdCmsClient_t`.

## Control Flow
Implementations are configured once, then receive locate/forward/prepare calls from server code. Methods can complete synchronously, redirect, return data, report errors, or return `SFS_STARTED` to finish later through callback mechanics.

## State and Persistence Behavior
The base class only stores `myPersona`. Derived implementations own cluster connection state. Resource/reserve/release default to no-ops.

## Dependencies and Integration Points
Forward-declares OFS/Ouc/logger/env/prep types and includes no implementation-heavy headers. It is the ABI contract for external CMS plugins and for the built-in `GetDefaultClient()`.

## Risks and Edge Cases
Callback semantics are non-trivial; implementers must use persistent callback objects and avoid non-causal replies. Several default methods silently do nothing or return success-like values, so derived classes must override where behavior is required.

## Test Signals
ABI compatibility tests for plugin loading, derived-class override coverage, return convention tests for locate/forward/prepare, and callback timing tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.cc

## Purpose
Implements CMS client configuration parsing for managers, supervisors, and servers, including admin socket paths, manager lists, request timing, tracing, VNID/system ID setup, and performance monitor plugin loading.

## Important APIs, Types, and Functions
Implements destructor cleanup, `Configure()`, `ConfigProc()`, `ConfigSID()`, `ConfigXeq()`, and directive parsers `xapath()`, `xcidt()`, `xconw()`, `xmang()`, `xperf()`, `xreqs()`, `xtrac()`, and `xvnid()`.

## Control Flow
`Configure()` seeds environment-derived defaults, parses the config file, validates required manager/proxy manager lists, exports local CMS path variables, computes role-specific socket paths, initializes the message pool, and optionally loads a performance monitor. `ConfigProc()` scans `cms.`, `odc.`, and compatibility directives. `xmang()` handles role modifiers, selection modes, ports, conditionals, and manager list parsing.

## State and Persistence Behavior
The object owns heap strings for paths, VNID/perf plugin data, cluster ID tag, and linked manager/proxy lists. It exports `XRDCMSPATH`, `XRDOLBPATH`, and `XRDCMSMAN` into the process environment. No config file is written.

## Dependencies and Integration Points
Depends on CMS message/security/perf/trace/utils, Ouc config streams, environment utilities, time/int parsing, and dynamic plugin loading. Integrates with `XrdCmsClientMsg::Init()` and `XrdCmsSecurity` system ID/VNID helpers.

## Risks and Edge Cases
Directive parsing is token-order sensitive and keeps many compatibility aliases. `ConfigProc()` passes `var+4` even for `all.manager`, which relies on prefix shape. Performance monitor loading only happens when both `prfLib` and `cmsMon` are set. Environment exports affect later components globally.

## Test Signals
Tests should parse adminpath, cidtag length, conwait, manager modes/ports/conditionals, request options, trace flags including negation, VNID forms, perf plugin options, missing manager errors, supervisor path rewrites, and environment exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.hh

## Purpose
Declares the configuration holder and parser API for CMS client roles.

## Important APIs, Types, and Functions
Defines `configHow`, `configWhat`, `Configure()`, timing fields (`ConWait`, `RepWait`, `RepDelay`, etc.), path/identity fields (`CMSPath`, `myHost`, `myName`, `myVNID`, `cidTag`), manager lists, performance monitor pointer/interval, and selection modes `FailOver`/`RoundRob`.

## Control Flow
Consumers construct this object, call `Configure()`, then use the populated public fields to initialize manager connections, local sockets, performance reporting, and request handling.

## State and Persistence Behavior
Most state is public mutable configuration. Private fields store parser/plugin intermediates and role booleans. The destructor frees owned linked lists and heap strings.

## Dependencies and Integration Points
Includes `XrdOucTList` and conversion utilities. Forward-declares stream/error/perf classes. Used by CMS finder/client manager setup.

## Risks and Edge Cases
Public mutable fields make invariants dependent on call order and caller discipline. Ownership is manual C allocation/free. Defaults encode operational policy and should be reviewed when changing protocol timing.

## Test Signals
Constructor default tests, destructor leak checks, and configuration parser integration tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.cc

## Purpose
Implements a persistent client-side connection to one CMS manager, including login, request sending, response receiving, delayed asynchronous replies, status updates, and reconnect/backoff behavior.

## Important APIs, Types, and Functions
Defines static buffer pool, network pointer, debug/config state, and mutex. Implements constructor/destructor, `delayResp()`, two `Send()` overloads, `Start()`, `whatsUp()`, and private `Hookup()`, `Receive()`, `relayResp()`, `chkStatus()`, and `setStatus()`.

## Control Flow
`Start()` loops forever: connect/login through `Hookup()`, receive CMS headers and payloads, route async responses to `relayResp()`, process status updates, or pass regular replies to `XrdCmsClientMsg::Reply()`. On disconnect it closes the link, marks the manager inactive/suspended, logs, sleeps, and reconnects. `Send()` writes requests only while active. `delayResp()` converts wait-response IDs into delayed response objects.

## State and Persistence Behavior
Per-manager state includes host/prefix, port, link, active/silent/suspend counters, instance number, manager mask, reconnect delay, wait/backoff timing, response queue, network buffer, and last update/timeout timestamps. State is protected by `myData` and static `manMutex` for global debug bits. No durable persistence.

## Dependencies and Integration Points
Depends on CMS login, client message table, responses, trace, XrdInet/XrdLink, SFS return codes, timers, and error reporting. Integrates with manager selection code via linked `Next` and mask/status APIs.

## Risks and Edge Cases
The constructor uses `1 << Instance++` into `manMask`; many managers can overflow an `int`. `maxMsgID` is not initialized in the constructor in the read source. `Receive()` allows resizing only for `kYR_data`; excessive other payloads are logged and treated as failure. Silent manager detection closes links after configured no-response thresholds.

## Test Signals
Tests should cover connection/login retries, suspended status changes, send failure instance bumping, wait-response synchronization, delayed async response delivery, no-response backoff/delay calculation, payload sizing, and reconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.hh

## Purpose
Declares `XrdCmsClientMan`, the object representing one remote CMS manager connection from a client/redirector perspective.

## Important APIs, Types, and Functions
Public API includes `delayResp`, `isActive`, `nextManager`, `Name`, `NPfx`, `manPort`, `Send()` overloads, `Start`, `Suspended`, `setNext`, `setNetwork`, `setConfig`, `whatsUp`, and `waitTime`. Private helpers handle hookup, receive, async response relay, status check, and status set.

## Control Flow
Higher-level CMS clients create one object per manager, run `Start()` in a thread, send requests through `Send()`, and query active/suspended state while manager replies are matched through `XrdCmsClientMsg` and `XrdCmsRespQ`.

## State and Persistence Behavior
State includes static network/config/buffer-pool data, linked-list pointer, connection link, host strings, port, instance/mask values, counters, timing fields, response header, and reusable network buffer. State is process-local and manually owned.

## Dependencies and Integration Points
Includes YProtocol headers, CMS response queues, Ouc buffer/error info, atomics, and pthread wrappers. Forward-declares `XrdInet` and `XrdLink`.

## Risks and Edge Cases
Inline atomic macros hide locking behavior and should be kept consistent with implementation locks. Manual memory ownership of `Host`, `HPfx`, `NetBuff`, and `Link` requires destructor coverage. Static network pointer must be set before connection threads start.

## Test Signals
Compile tests should catch protocol header changes. Unit tests should cover constructor defaults, linked manager chaining, static network/config setup, and suspended/active accessors under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.cc -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.cc

## Purpose
Implements a fixed-size table of outstanding CMS client messages, assigning stream IDs, waiting for manager replies, decoding replies, and recycling message slots.

## Important APIs, Types, and Functions
Implements `Alloc()`, `Init()`, `Recycle()`, static `Reply()`, and private `RemFromWaitQ()`. Static state includes `nextid`, `numinQ`, `msgTab`, `nextfree`, and `FreeMsgQ`.

## Control Flow
`Init()` allocates 1024 message objects and links them into the free list. `Alloc()` pops one, assigns a generation-encoded ID, stores the caller's `XrdOucErrInfo`, locks its condition variable, and marks it waiting. `Reply()` removes the matching slot by stream ID, decodes the response through `XrdCmsParser::Decode()`, signals the waiter, and unlocks. `Recycle()` removes a waiter from service and returns it to the free list.

## State and Persistence Behavior
All state is process-local and fixed-size. IDs combine a low-bit table index with generation bits to reject stale replies. No durable persistence.

## Dependencies and Integration Points
Depends on CMS wire headers, parser, trace, Ouc buffers/error info, and pthread condition variables. Used by `XrdCmsClientMan` when sending synchronous manager requests.

## Risks and Edge Cases
At most 1024 concurrent messages can be outstanding. `numinQ` is a static counter guarded only around free-list operations but returned without locking. `Recycle()` substitutes a static dummy response because replies may race with recycling. Stale or unknown replies are logged only at debug level.

## Test Signals
Tests should cover ID generation/wrap, stale reply rejection, table exhaustion, wait/signal behavior, decode result propagation, concurrent allocation/recycle, and in-queue accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.hh -->
# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.hh

## Purpose
Declares the outstanding-message slot used by CMS clients to wait for manager replies.

## Important APIs, Types, and Functions
Public API includes static `Alloc`, `Init`, `inQ`, and `Reply`; instance methods include `ID`, `getResult`, `Lock`, `UnLock`, `Wait4Reply`, and `Recycle`. Constants define a 1024-slot table with generation increments.

## Control Flow
Callers allocate a locked message slot, send its `ID()` as the stream ID, wait on `Wait4Reply()`, read `getResult()`, then recycle. Manager receive code calls static `Reply()` to match and signal the slot.

## State and Persistence Behavior
Each slot stores a next pointer, condition variable, waiting flag, ID, response pointer, and decoded result. Static free-list/table state is process lifetime.

## Dependencies and Integration Points
Includes CMS protocol headers and pthread primitives; forward-declares `XrdOucErrInfo` and `XrdOucBuffer`. Integrated with `XrdCmsClientMan` and `XrdCmsParser`.

## Risks and Edge Cases
The fixed slot count is a hard concurrency limit. Correctness depends on callers respecting lock ownership comments: `Alloc()` and `RemFromWaitQ()` return locked objects, and `Recycle()` expects the lock to be held.

## Test Signals
Tests should check lock/wait/recycle protocol, fixed-capacity failure, and stale generation handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.hh -->
