# subset-b-007969 research

Grouped research for the XRootD SSI files listed in work item `subset-b-007969`. Each file section preserves the source path and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.cc

Purpose: implements the concrete `XrdSsiCms` adapter that lets SSI providers interact with XRootD CMS cluster management while counting SSI resource statistics. The constructor snapshots the manager list from an `XrdCmsClient`, storing each manager as `host:port` strings in a private array that is later exposed through the header API.

Important APIs and control flow: `XrdSsiCms::XrdSsiCms(XrdCmsClient *)` walks `cmsP->Managers()`, counts entries, allocates `manList`, and duplicates formatted manager endpoints. `Added()` and `Removed()` increment `Stats.ResAdds` and `Stats.ResRems` before delegating to `XrdCmsClient::Added()` or `Removed()` if a CMS client exists. The destructor frees every duplicated manager string and deletes the array.

State and persistence: state is process-local only: `theCms`, `manList`, and `manNum`. There is no disk persistence or network I/O in this file beyond delegating to the CMS object. Dependencies include `XrdCmsClient`, `XrdOucTList`, and the global `XrdSsi::Stats`.

Integration points: used wherever SSI needs a cluster object implementing `XrdSsiCluster` for provider initialization and resource advertisements. Risks include trusting the CMS manager list lifetime during construction, fixed 1024-byte formatting buffer for endpoints, and null `theCms` behavior that silently turns methods into no-ops. Test signals should cover empty and multi-manager CMS lists, stats bumps on add/remove, delegation when `theCms` is non-null, and destructor cleanup under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.hh

Purpose: declares `XrdSsiCms`, an `XrdSsiCluster` implementation backed by an `XrdCmsClient`. It exposes cluster resource lifecycle and capacity methods to SSI provider code while hiding the CMS client representation.

Important APIs/types: public methods include `Added()`, `Removed()`, `Managers(int &)`, `Resume()`, `Suspend()`, `Resource()`, `Reserve()`, `Release()`, and `Utilization()`. `DataContext()` always returns true, indicating this cluster adapter works in a data-serving context. Constructors support an inert default instance and a CMS-backed instance; the destructor owns `manList`.

Control flow and state: most methods are thin guards around `theCms`; if `theCms` is null they return neutral values or do nothing. `Managers()` returns an internal array of duplicated endpoint strings and sets the count. Private state is `XrdCmsClient *theCms`, `char **manList`, and `int manNum`.

Dependencies and integration: depends on `XrdCms/XrdCmsClient.hh` and the SSI cluster base class. It is a server-side integration point for provider initialization and CMS resource publication. Risks include callers treating `Managers()` output as mutable or longer lived than the object, and neutral returns hiding misconfiguration. Test signals should validate null-object behavior, forwarding semantics, and that the manager count/list remain stable after construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCms.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.cc

Purpose: implements an `XrdSfsDirectory` adapter for SSI. SSI itself does not provide directory listing semantics; this file delegates directory operations to the underlying configured filesystem only when the path is allowed by the global filesystem path list.

Important APIs and control flow: `open()` rejects reuse when `dirP` is already set, checks `fsChk && FSPath.Find(dir_path)`, allocates a real directory via `theFS->newDir()`, copies error context, and delegates `open()`. If the path is not filesystem-backed it returns `ENOTSUP`. `nextEntry()`, `close()`, `autoStat()`, and `FName()` all forward to `dirP` when open and otherwise set `EBADF`.

State and persistence: state is a single delegated `XrdSfsDirectory *dirP` owned by the wrapper. No persistent storage is modified. Global dependencies are `XrdSsi::theFS`, `XrdSsi::FSPath`, and `XrdSsi::fsChk`.

Integration points: used by the SSI SFS layer to support directory operations only for passthrough filesystem paths. This keeps service-request paths from accidentally exposing directory semantics. Risks include returning `ENOTSUP` for all non-FS paths, lifecycle reliance on `dirP` ownership, and propagation of delegated error state. Test signals should cover open twice, non-FS paths with and without `fsChk`, delegated happy paths, and EBADF behavior before open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.hh

Purpose: declares `XrdSsiDir`, the SSI directory wrapper implementing the XRootD SFS directory interface. It is a small ownership and delegation class rather than an SSI directory service.

Important APIs/types: overrides `open()`, `nextEntry()`, `close()`, `FName()`, and `autoStat()`. `copyError()` copies the wrapper error object into a caller-supplied `XrdOucErrInfo`. Constructor forwards user and monitor ID to `XrdSfsDirectory` and initializes `dirP` to null.

Control flow and state: the object is either unopened (`dirP == 0`) or delegates every operation to a real `XrdSfsDirectory`. Destructor deletes `dirP` if present. Private fields are `dirP`, `tident`, and `myEInfo`; `myEInfo` is constructed but the implementation mainly uses inherited `error`.

Dependencies and integration: depends on `XrdSfsInterface.hh` and is instantiated by SSI SFS plumbing. Risks include shallow `tident` storage from constructor input, possible confusion between `error` and `myEInfo`, and lack of reset after `close()` because the delegated object remains allocated. Test signals should include destructor cleanup and error propagation through `copyError()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEntity.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEntity.hh

Purpose: defines `XrdSsiEntity`, the SSI representation of authenticated client identity passed to provider/resource code. It mirrors fields commonly available from `XrdSecEntity` while keeping SSI-facing code independent of the security package.

Important APIs/types: public fields include protocol ID `prot`, `name`, `host`, `vorg`, `role`, `grps`, `endorsements`, raw `creds` plus `credslen`, reserved integer, and `tident`. `XrdSsiPROTOIDSIZE` is 8, and the constructor copies a protocol name into the fixed field with null termination.

Control flow and state: this is a plain data holder with no methods beyond construction/destruction. It does not own the string pointers by default; callers such as `XrdSsiFileResource::Init()` point fields at data owned by security/environment objects. There is no persistence.

Dependencies and integration: used by `XrdSsiResource::client` and populated from `XrdSecEntity`. Risks are lifetime-related: most members are borrowed pointers, so provider code must not retain an `XrdSsiEntity` beyond the resource/session lifetime unless it copies data. Test signals should check protocol truncation/null termination and safe behavior when optional identity fields are null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEntity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.cc

Purpose: provides the platform/XRootD error-text conversion hook for `XrdSsiErrInfo`. It keeps errno-to-message mapping out of the header while delegating to the canonical XRootD helper.

Important APIs and control flow: the only implemented function is `XrdSsiErrInfo::Errno2Text(int ecode)`, which returns `XrdSysE2T(ecode)`. It is called by `XrdSsiErrInfo::Set()` when no explicit message is supplied or the supplied string is empty.

State and persistence: no local state, no persistence, no allocation. Dependencies are `XrdSsiErrInfo.hh` and `XrdSys/XrdSysE2T.hh`.

Integration points: used throughout SSI request/session/provider code to create stable error text for errno values. Risks are limited to the semantics of `XrdSysE2T`, especially for zero or non-errno values. Test signals should cover explicit message preservation in the header class and fallback text for representative errno values through this implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.hh

Purpose: declares `XrdSsiErrInfo`, SSI's lightweight error container used by client requests, providers, and server-side prepare/response paths. It stores an error number, optional argument, and message.

Important APIs/types: `Clr()`, `Get(int &)`, `Get()`, `GetArg()`, `hasError()`, `isOK()`, and two `Set()` overloads for C strings and `std::string`. Assignment and copy construction preserve all three stored values. `Errno2Text()` is private and implemented in the `.cc` file.

Control flow and state: `Set()` uses explicit non-empty text when available; otherwise it maps `eNum` to text. `errArg` carries secondary data used by paths such as redirect/stall handling. The class owns `errText` but not any external data. It has no locking, so instances are expected to be thread-confined or externally synchronized.

Dependencies and integration: heavily used in `XrdSsiProvider`, `XrdSsiRequest`, `XrdSsiResponder`, `XrdSsiFileReq`, and `XrdSsiFileSess`. Risks include `hasError()` treating `errNum == 0` as success even when text is non-empty, and callers using `Get().c_str()` beyond the object's lifetime or after mutation. Test signals should cover copy/assignment, zero-code messages, fallback errno text, and `errArg` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.cc

Purpose: implements asynchronous client-response event serialization for SSI objects that are both `XrdCl::ResponseHandler`s and scheduler jobs. It converts network callbacks into scheduler-executed `XeqEvent()` calls while preserving event order.

Important APIs and control flow: `AddEvent()` locks `evMutex`, records the first event in `thisEvent`, schedules the job if not running, and appends later events using pooled `EventData` nodes. `DoIt()` repeatedly moves the pending list into a local copy, unlocks, calls virtual `XeqEvent()` for each event, clears consumed events, and finally calls `XeqEvFin()`. Positive `XeqEvent()` return flushes normally; zero continues; negative halts because the object became invalid. `ClrEvent()` deletes status/response payloads and recycles chained nodes.

State and persistence: state is in-memory queue data: `thisEvent`, `lastEvent`, `running`, `isClear`, and static `freeEvent`, protected by `evMutex` plus static `frMutex`. No persistence occurs.

Dependencies and integration: depends on `XrdCl` response objects, `XrdScheduler`, and SSI tracing/mutex utilities. It is suitable for client-side service implementations that need ordered callback handling without executing complex code in the network callback thread. Risks include object deletion during `XeqEvent()`, correctness of event ownership/deletion, and pooled `EventData` reuse. Test signals should stress multiple queued callbacks, destructor cleanup with pending events, `XeqEvent()` return-code behavior, and scheduler single-run behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.hh

Purpose: declares `XrdSsiEvent`, an abstract base that adapts XRootD client responses into SSI scheduler jobs. Subclasses implement the actual event execution and completion hooks.

Important APIs/types: public `AddEvent()`, `ClrEvent()`, `DoIt()`, and `HandleResponse()` implement the queueing/dispatch contract. Subclasses must implement `XeqEvent(XrdCl::XRootDStatus *, XrdCl::AnyObject **)` and `XeqEvFin()`. The nested `EventData` stores one status/response pair and a next pointer; `Move2()` transfers ownership without copying payloads.

Control flow and state: `HandleResponse()` simply calls `AddEvent()`. `DoIt()` is invoked by the scheduler, not directly by the client callback. Protected `tident` is wired to `XrdJob::Comment` for trace output. Destructor clears pending events when the object is not already clear.

Dependencies and integration: depends on `XrdJob`, `XrdClXRootDResponses`, and `XrdSsiAtomics` for mutex helpers. Risks include subclass obligations: `XeqEvent()` must respect ownership of `response` and return negative only when the object is unsafe to touch. Test signals should use a fake subclass to assert event order, callback-to-scheduler transition, and cleanup after early halt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.cc

Purpose: implements `XrdSsiFile`, the SFS file adapter that either delegates to a real filesystem file for configured paths or exposes an SSI request/response session as file-like operations. This is the entry point translating XRootD file calls into SSI request protocol calls.

Important APIs and control flow: `open()` rejects reuse, optionally delegates to `theFS->newFile()` when `fsChk && FSPath.Find(path)`, otherwise builds an `XrdOucEnv`, allocates `XrdSsiFileSess`, and calls session `open()`. Most methods route to `fsFile` when present and to `fSessP` otherwise: `read()`, `write()`, `truncate()`, `fctl()`, `SendData()`, `setXio()`, and `FName()`. Unsupported SSI operations include `readv()` and `sync()`, while AIO read/write are executed synchronously then completed.

State and persistence: owns either `fsFile` or `fSessP`; destructor deletes the delegated file or recycles the session. It also defines `XrdSsi::EmsgPool`, used elsewhere for error-message buffers. No disk persistence is introduced except through delegated filesystem file operations.

Dependencies and integration: depends on SFS interfaces, `XrdOucEnv`, path-list routing, `XrdSsiFileSess`, and SSI utility error formatting. Risks include mode/operation mismatches, synchronous AIO behavior, null `fSessP` assumptions after failed open, and split semantics between passthrough filesystem paths and SSI resources. Test signals should cover both routing branches, open failure cleanup, fctl GETFD behavior enabling `SendData`, sync/readv unsupported returns, and session destruction on file object deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.hh

Purpose: declares `XrdSsiFile`, the SFS file wrapper used by the SSI filesystem plugin. It preserves the full `XrdSfsFile` interface while hiding whether a request is served by SSI or a passthrough filesystem.

Important APIs/types: overrides open/close, two `fctl()` forms, `FName()`, compression and mmap queries, sync/preread/read/readv/AIO read, `SendData()`, `setXio()`, `stat()`, truncate, write, and AIO write. Constructor initializes the base `XrdSfsFile` with `myEInfo`.

Control flow and state: private fields are `XrdSfsFile *fsFile`, `XrdSsiFileSess *fSessP`, and `XrdOucErrInfo myEInfo`. Exactly one backend should be active after a successful open. The destructor owns cleanup for both backends.

Dependencies and integration: depends on `XrdSfsInterface.hh` and forward-declares `XrdSsiFileSess`. It is instantiated by SSI SFS server code. Risks include every new SFS method needing the same passthrough-vs-SSI routing decision, and maintaining backend exclusivity. Test signals should instantiate via the SFS factory and verify method routing under both backend kinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileReq.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileReq.cc

Purpose: implements server-side SSI request execution for the SFS file protocol. `XrdSsiFileReq` is simultaneously an `XrdSsiRequest`, callback object, and scheduler job; it owns request bytes, receives provider responses, queues alerts, and streams response data back through read/sendfile calls.

Important APIs and control flow: `Alloc()` uses a static free list, initializes request/session pointers, and assigns a request ID. `Activate()` records the request buffer and schedules `DoIt()`. `DoIt()` handles responder state: new requests call `Service->ProcessRequest()`, aborted requests recycle, and done requests wake waiters, post finish semaphores, update stats, and call `Finished(cancel)`. `ProcessResponse()` validates active state, records response type (`isData`, `isError`, `isFile`, `isStream`), sets `haveResp`, and wakes waiting clients. `WantResponse()` is called from session `fctl()` to return alerts, direct responses, or defer via callback. `Read()` and `Send()` drain data/error/file/stream responses; active and passive stream helpers use `GetBuff()` or `SetBuff()`. `Finalize()` sequences cancellation, unbound/bound states, pending alert cleanup, response wakeups, and `Finished()`. `Recycle()` releases request buffers and returns objects to the pool.

State and persistence: important mutable state includes `myState` (`wtReq`, `xqReq`, `wtRsp`, `doRsp`, `odRsp`, `erRsp`), `urState` (`isNew`, `isBegun`, `isBound`, `isAbort`, `isDone`), request buffers (`oucBuff` or `sfsBref`), response offsets/lengths, stream buffer, callback pointer/argument, alert queues, and ending flags. All state is in-memory and heavily synchronized by recursive `frqMutex`.

Dependencies and integration: integrates `XrdSsiService`, `XrdSsiResponder`, `XrdSsiFileSess`, `XrdSsiRRTable`, `XrdSfsDio`, streams, alerts, scheduler, stats, tracing, and error routing. Risks are high: intertwined state machines, callbacks while locks are intentionally dropped, object-pool reuse, alert ordering, file descriptor response reads, and deferred finalization races. Test signals should include concurrent response-before-wait and wait-before-response paths, alert ordering, direct metadata/data responses, stream active/passive reads, cancellation via truncate, sendfile continuation, and sanitizer/thread-sanitizer runs around finalize/recycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileReq.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileReq.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileReq.hh

Purpose: declares the request object that bridges SSI service processing to the XRootD SFS file protocol. It packages request lifecycle, callback handling, scheduler execution, response draining, and object pooling.

Important APIs/types: inherits `XrdSsiRequest`, `XrdOucEICB`, and `XrdJob`. Public methods include `Activate()`, `Alert()`, static `Alloc()`, `DeferredFinalize()`, `Finalize()`, `GetRequest()`, `ProcessResponse()`, `Read()`, `RelRequestBuffer()`, `Send()`, `WantResponse()`, callback `Done()`, and job `DoIt()`. State enums `reqState` and `rspState` encode client delivery and responder binding state.

Control flow and state: private methods `BindDone()` and `Dispose()` override request hooks used by responder lifecycle. `Emsg()` variants format errors, `readStrmA/P()` and `sendStrmA()` handle stream response transfer, and `WakeUp()` invokes deferred response callbacks. Static members implement a free list. Instance fields track request/session pointers, callback info, alert queues, response offsets, request buffers, stream buffer, state flags, and compact textual request ID.

Dependencies and integration: depends on SFS XIO/DIO types, scheduler jobs, SSI request/responder/stream classes, and file-session/resource classes. Risks are ABI/lifecycle sensitive: callers must not delete pooled objects directly, callback fields must match pending `fctl()` state, and state enum transitions must remain compatible with the implementation. Test signals should assert all public paths leave objects recyclable and that `SetMax()` limits pool growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileReq.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.cc

Purpose: initializes an SSI resource object from an SFS open path and `XrdOucEnv`. It maps security identity and SSI CGI/user metadata into the generic `XrdSsiResource` fields used by providers.

Important APIs and control flow: `XrdSsiFileResource::Init()` obtains `XrdSecEntity` from the environment. When present, it copies the protocol ID, borrows identity pointers, optionally resolves host through `addrInfo->Name()` when authenticated DNS is enabled, and assigns credentials. It sets `client = &mySec`, stores `rName = path`, reads `ssi.user` into `rUser`, and extracts full `ssi.cgi` content from the environment string into `rInfo`.

State and persistence: state is in the inherited resource fields and private `mySec`. There is no persistence. Most security strings are borrowed; `rName`, `rUser`, and `rInfo` are owning `std::string`s.

Dependencies and integration: depends on `XrdOucEnv`, `XrdSecEntity`, `XrdNetAddrInfo`, and `XrdSsiEntity`. It is called from `XrdSsiFileSess::open()` before `Service->Prepare()`. Risks include lifetime of borrowed `XrdSecEntity` fields, DNS lookup behavior when `authDNS` is enabled, and a suspicious duplicate assignment where `mySec.role` is assigned `entP->vorg` then overwritten by `entP->role`, leaving `vorg` unset. Test signals should cover no-security opens, `ssi.user`, raw `ssi.cgi` extraction, authenticated-DNS host selection, and VO/role mapping expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.hh

Purpose: declares `XrdSsiFileResource`, a concrete `XrdSsiResource` specialized for resources opened through the SFS file/session adapter.

Important APIs/types: `Init(const char *path, XrdOucEnv &envP, bool aDNS)` populates inherited resource metadata and private security identity. Constructor initializes the base resource with an empty name and default `mySec`.

Control flow and state: private `XrdSsiEntity mySec` backs the inherited `client` pointer after initialization. The object is owned by `XrdSsiFileSess`, so providers should copy data they need beyond the request/session lifetime.

Dependencies and integration: depends on `XrdSsiEntity`, `XrdSsiResource`, and `XrdOucEnv`. It is the resource argument passed to `Service->Prepare()` and `Service->ProcessRequest()`. Risks center on borrowed identity field lifetimes and whether providers assume `client` is always non-null. Test signals should assert inherited fields after typical opaque/security inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileSess.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileSess.cc

Purpose: implements the SSI file session that makes XRootD file operations behave like a request/response transport. A session prepares a resource, collects request bytes from writes, tracks outstanding request objects, exposes response readiness through `fctl()`, and drains responses through reads or `SendData()`.

Important APIs and control flow: `Alloc()` and `Recycle()` manage a free list with adaptive `freeMax`. `open()` initializes `fileResource`, calls `Service->Prepare()`, sets a display/session name (`gigID`), and maps provider errors to redirect (`EAGAIN`), stall (`EBUSY`), or regular errors. `write()` decodes `XrdSsiRRInfo` from the file offset, validates size/max request constraints, collects request bytes either by claiming an XIO buffer or allocating an `XrdOucBuffer`, then calls `NewRequest()`. `fctl()` validates `SFS_FCTL_SPEC1`, looks up a request, and either returns response/alert data immediately or installs `fctlCallBack` and returns `SFS_STARTED`. `read()` and `SendData()` look up the request by encoded ID and delegate to `XrdSsiFileReq`; completion removes/finalizes the request and marks EOF. `truncate()` is repurposed as cancel for `XrdSsiRRInfo::Can`. `AttnInfo()` builds the attention response header/vector, optionally sends metadata and direct data, and arranges finalization for complete direct responses.

State and persistence: session state includes `fileResource`, `eInfo`, user/session strings, `xioP`, partial request buffer, `reqSize/reqLeft`, `isOpen/inProg`, EOF bit vector, request table, and callback-held table items. No disk persistence is introduced. Synchronization relies on request-table internals, callback object ownership, and the file protocol's assumption that writes for different requests are not interleaved while a partial request is in progress.

Dependencies and integration: integrates SFS file operations, `XrdOucBuffPool`, `XrdSsiService`, `XrdSsiRRInfo`, `XrdSsiRRTable`, stats, tracing, and provider resource preparation. Risks include partial-write state corruption if interleaving assumptions break, request ID collisions, direct-response size limits, callback lifetime while `rTab` is mutating, and provider error-code interpretation. Test signals should cover prepare success/error/redirect/stall, single-write and multi-write request assembly, fctl immediate/deferred response, direct metadata/data attention responses, EOF one-shot behavior, cancellation, close with outstanding requests, and free-list reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileSess.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileSess.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileSess.hh

Purpose: declares the in-memory session object backing SSI-mode `XrdSsiFile` instances. It owns resource preparation state and the table of active `XrdSsiFileReq` objects.

Important APIs/types: public methods include static `Alloc()`, `AttnInfo()`, request-table finalization wrappers, `close()`, `fctl()`, `open()`, `read()`, `SendData()`, `SetAuthDNS()`, `setXio()`, `truncate()`, and `write()`. `Resource()` exposes the current `XrdSsiFileResource`. The nested `reqItemCB` keeps a table lookup reference alive across async callback completion.

Control flow and state: private `Init()`, `NewRequest()`, `Reset()`, and `writeAdd()` support lifecycle and multi-segment writes. Static free-list members are protected by `arMutex`; instance state includes resource, identity strings, current partial write buffer, open/progress booleans, EOF bit vector, `XrdSsiRRTable<XrdSsiFileReq>`, and two callback holders.

Dependencies and integration: depends on SFS, XIO, SSI request/resource/table classes, and pthread mutexes. It is not copyable and is created/recycled through static methods. Risks include static pool sizing, stale pointer fields after reuse, and callback-held table items delaying finalization. Test signals should inspect reuse reset, callback reference release, and behavior when close/reset races with outstanding requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileSess.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.cc

Purpose: implements SSI logging globals and the `XrdSsiLogger` static API. It routes server messages to `XrdSysError`/`XrdSysLogger` and can intercept XRootD client log output through an `XrdCl::LogOut` adapter.

Important APIs and control flow: globals include `XrdSsi::Log`, `Logger`, `Trace`, `msgCB`, and `msgCBCl`. `Msg()`, `Msgf()`, and `Msgv()` write prefixed errors with `Log.Emsg()` or unprefixed lines with `Log.Say()`. The iovec overload writes directly with `Logger->Put()`. `SetMCB()` stores server callback and, for client/all modes, replaces the `XrdCl::DefaultEnv` log output with `LogMCB`. `LogMCB::Write()` strips leading XrdCl bracket fields, captures time/thread ID, and calls the configured callback. `TBeg()`/`TEnd()` wrap trace-stream output.

State and persistence: state is process-global logging configuration. No persistent storage is written here, but messages flow to the configured XRootD logger. Dependencies include XRootD logging, tracing, pthread thread numbering, and client default environment.

Integration points: used by SSI provider/service code and optionally by plugin callbacks installed at library initialization. Risks include `Logger` being null before initialized, ownership/leak expectations for `new LogMCB`, callback thread-safety, format truncation at 2048 bytes, and macro typos in the header using `XrdSSiLogger` capitalization. Test signals should cover callback installation, client log stripping, null client log behavior, and server `Msg*` output formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.hh

Purpose: declares the SSI logging facade exposed to provider/service code. It abstracts direct XRootD logger calls and supports application-defined message callbacks.

Important APIs/types: static methods are `Msg()`, `Msgf()`, `Msgv()` with `va_list`, `Msgv(iovec *, int)`, `SetMCB()`, `TBeg()`, and `TEnd()`. `MCB_t` defines callback signature with timestamp, thread ID, message pointer, and length. `mcbType` selects all/client/server callback installation. Macros `SSI_LOG` and `SSI_SAY` wrap stream output.

Control flow and state: the class itself stores no instance data; all behavior is static and implemented in the `.cc`. The callback API is intended to be called during static initialization. Header comments define an alternate plugin-level `XrdSsiLoggerMCB` pointer for server-side log routing.

Dependencies and integration: depends on `<cstdarg>` and forward-declared `iovec`; implementation depends on XRootD logging. Risks include global initialization ordering, callback lifetime, and the `SSI_LOG`/`SSI_SAY` macro references spelling `XrdSSiLogger` instead of `XrdSsiLogger`, which would fail if those macros are compiled as written. Test signals should compile macro users, install callbacks in each mode, and verify varargs truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogger.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogging.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogging.cc

Purpose: implements the XRootD log plugin initializer that loads an SSI logging callback provider from configuration. It lets `-l@` route XRootD logging into a provider-defined SSI callback.

Important APIs and control flow: local `ConfigLog(const char *cFN)` opens the config, scans for `ssi.loglib` or `ssi.svclib`, prefers `loglib` and falls back to `svclib`, loads the selected shared library with `XrdSysPlugin`, and looks up `XrdSsiLoggerMCB` if global `msgCB` was not already set by dynamic initialization. `XrdSysLogPInit()` is the exported C entry point; it calls `ConfigLog()` and returns `msgCB`. `XrdVERSIONINFO` registers plugin version information.

State and persistence: global state is `XrdSsi::msgCB`; loaded plugins are persisted with `myLib->Persist()` when a callback is available. No file writes occur. Dependencies include `XrdOucStream` config parsing, `XrdSysPlugin`, version macros, and errno text conversion.

Integration points: used by XRootD's logging plugin mechanism, not by normal SSI request flow. Risks include config parse errors, ambiguous fallback from `loglib` to `svclib`, error message typo saying callback "was found" when it likely means not found, plugin symbol type assumptions, and persistence only after callback discovery. Test signals should include configs with only `ssi.svclib`, only `ssi.loglib`, missing directives, invalid paths, symbol missing, and a plugin that sets `msgCB` during load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogging.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiProvider.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiProvider.hh

Purpose: defines the abstract provider contract for SSI. Providers answer resource availability, create service objects, initialize server-side operation, and accept client-side tuning options.

Important APIs/types: `Control()` handles future control operations with default `CTL_None` support. `GetService()` returns an `XrdSsiService` for client or server use, defaulting to `ENOTSUP`. `SsiVersion`/`GetVersion()` support ABI compatibility. Pure virtual `Init()` and `QueryResource()` are mandatory. Optional hooks include `ResourceAdded()`, `ResourceRemoved()`, deprecated `SetCBThreads()`, `SetConfig()`, `SetSpread()`, and `SetTimeout()`. Enums include `rStat` and timeout type `tmoType`.

Control flow and state: this header declares behavior only; implementations must be thread-safe except for initialization. The protected destructor documents that provider objects are plugin/global owned and not explicitly deleted by SSI.

Dependencies and integration: depends on `XrdSsiErrInfo` and `XrdSsiResource`, with forward declarations for cluster/logger/service. It is central to plugin integration on both client and server. Risks include ABI/version mismatches, provider methods not being thread-safe, callers relying on optional configuration methods that providers ignore, and ambiguous error semantics for `EAGAIN`/`EBUSY` later interpreted by session open. Test signals should include mock providers for all `rStat` values, initialization failure logging, version checks, and client option validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiProvider.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRAgent.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRAgent.hh

Purpose: declares a privileged helper class that bridges private state between `XrdSsiRequest`, `XrdSsiResponder`, and transport-specific implementations. It avoids exposing lifecycle internals as public API.

Important APIs/types: static methods forward alerts, cleanup, disposal, and accessors for request error/response state. `isaRetry()` tests and optionally clears retry flags. `onServer()` marks a request as server-side. `Request()` gets the responder's bound request. `SetNode()`, `ResetResponder()`, and `SetMutex()` mutate endpoint, responder binding, and request mutex.

Control flow and state: all methods are inline and operate on private fields by friendship. `ResetResponder()` locks the responder mutex before clearing `reqP`. There is no owned state or persistence.

Dependencies and integration: used by lower-level request/session/client code that must coordinate responder binding and request reuse. Risks include misspelled forward declaration `XrdSsiMuex`, bypassing normal invariants, and potential misuse that clears responder/request links without completing lifecycle. Test signals should focus on flows that depend on these helpers: request cleanup before reuse, retry flag one-shot behavior, server/client `ProcessResponse` branch selection, and responder reset under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRAgent.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRInfo.hh

Purpose: defines compact request/response protocol metadata encoded into XRootD file offsets and attention responses. It is the wire-format helper used by `XrdSsiFileSess` and clients.

Important APIs/types: `XrdSsiRRInfo` stores an operation command in the top byte of `reqId`, a 24-bit request ID, and a 32-bit request size. `Opc` values are `Rxq`, `Rwt`, and `Can`. Methods set/get command, ID, size, raw data pointer, and packed `Info()`. `XrdSsiRRInfoAttn` describes attention responses with tag values `alrtResp`, `fullResp`, and `pendResp`, plus prefix and metadata lengths.

Control flow and state: setters use network byte order for ID/size, preserving the command byte during ID changes. `Info()` packs the stored network-order fields into a 64-bit value for file offsets. There is no dynamic allocation or persistence.

Dependencies and integration: depends on `arpa/inet.h` and response info definitions. Used by file-session `write()`, `read()`, `truncate()`, and `fctl()` to identify requests and commands. Risks include 24-bit ID wrap/collision, endian correctness, union aliasing assumptions, and callers confusing request size with actual write length. Test signals should cover pack/unpack across commands, max ID masking, zero-size requests, cancellation offsets, and attention-header network byte order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRTable.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRTable.hh

Purpose: provides a reference-counted table for active request/response objects keyed by request ID. It supports safe lookup handles, deletion, deferred finalization, and blocking reset while callbacks may still hold references.

Important APIs/types: `XrdSsiRRTableItem<T>` is a move-only RAII handle that releases a table reference on destruction. `XrdSsiRRTable<T>` methods include `Add()`, `LookUp()`, `Del()`, `DelFinalize()`, `DeferFinalize()`, `DeferredFinalizeDone()`, `Release()`, `Reset()`, `Clear()`, and `Num()`. It has a special `baseItem` fast slot plus a `std::map` for additional entries.

Control flow and state: `Add()` starts refcount at 2: one for table ownership and one for the returned handle. `LookUp()` increments refcount unless deleted. `Del()` marks deleted and drops table ownership. When refcount reaches zero, the table either erases immediately or calls `DeferredFinalize()`/`Finalize()` depending on flags. `DelFinalize()` blocks until the entry disappears. `Reset()` marks all entries deleted, finalizes eligible ones outside the table lock, and waits for deferred finalization count `nDef` to drain via condition variable.

Dependencies and integration: depends on SSI mutex/condition helpers, `std::map`, and `std::vector`. Used by `XrdSsiFileSess` to keep `XrdSsiFileReq` alive across reads, fctl callbacks, direct attention responses, close, and cancellation. Risks are high: refcount underflow, missed condition broadcasts, typoed `deferedFinalize` naming hiding logic mistakes, blocking waits under unusual callback order, and `Clear()` dropping items without finalization. Test signals should include duplicate add rejection, lookup/delete races, callback-held item release, reset with live references, direct `DelFinalize()`, and thread-sanitizer stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRTable.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRequest.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRequest.cc

Purpose: implements common request lifecycle behavior shared by client-side and server-side SSI requests. It manages response metadata/data access, responder finish handoff, retry flagging, and cleanup for object reuse.

Important APIs and control flow: constructor initializes request ID, default unbound mutex, empty responder, endpoint, timeout, and client-side flag. `CleanUp()` resets `Resp`, clears `errInfo`, endpoint, and returns the mutex pointer to the global unbound mutex. `CopyData()` validates a caller buffer, copies available data response bytes, advances `Resp.buff/blen`, unlocks, and invokes `ProcessResponseData()`. `Finished()` atomically detaches `theRespond`, then calls responder `Finished()` if present. `GetEndPoint()` and `GetMetadata()` read guarded state. `GetResponseData()` dispatches to stream `SetBuff()` for stream responses, copies ordinary data responses, or reports `ENODATA`. `ReleaseRequestBuffer()` calls the virtual buffer-release hook under lock. `SetRetry()` toggles the private retry flag.

State and persistence: state is per-request and in-memory: response info, error info, responder pointer, endpoint, mutex pointer, TTL/timeout, client/server marker, and flags. The file defines global recursive `XrdSsi::ubMutex` for unbound requests.

Dependencies and integration: used by `XrdSsiResponder`, `XrdSsiRRAgent`, `XrdSsiFileReq`, and client service implementations. Risks include touching request state after `Finished()` when ownership may transfer, `CopyData()` mutating `Resp.buff` pointer, lock/unlock before callbacks, and default constructor ignoring the `tmo` argument by setting `tOut` to zero. Test signals should cover data-response chunking, stream setup failure, no-responder `Finished()`, cleanup before reuse, retry flag through `XrdSsiRRAgent`, and metadata lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRequest.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRequest.hh

Purpose: declares the abstract SSI request API used on both client and server sides. It is the core contract between service execution, responder posting, and client response consumption.

Important APIs/types: public API includes `Finished()`, `GetDetachTTL()`, `GetEndPoint()`, `GetMetadata()`, pure virtual `GetRequest()`, `GetRequestID()`, `GetResponseData()`, `GetTimeOut()`, pure virtual `ProcessResponse()`, optional `ProcessResponseData()`, and `ReleaseRequestBuffer()`. Protected hooks include `Alert()`, `RelRequestBuffer()`, `SetDetachTTL()`, `SetRetry()`, `SetTimeOut()`, and protected destructor. Private hooks `BindDone()`, `CleanUp()`, `CopyData()`, and `Dispose()` are used via friends.

Control flow and state: `XrdSsiResponder` and `XrdSsiRRAgent` are friends because they need to bind responders, set response info, set mutexes, and reset objects. Private state stores request ID, current mutex, responder pointer, `XrdSsiRespInfo`, `XrdSsiErrInfo`, endpoint, detach TTL, timeout, client/server marker, and flags.

Dependencies and integration: depends on SSI atomics, errors, and response info. It is subclassed by transport-specific request types such as `XrdSsiFileReq` and by client applications. Risks include strict lifecycle requirements: creator may delete only after `Finished()`/unbind, response buffers must remain valid until `Finished()`, and protected setters must be called before processing starts. Test signals should compile minimal subclasses and exercise response, alert, detach, retry, and buffer-release contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResource.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResource.hh

Purpose: defines `XrdSsiResource`, the provider-facing description of a resource needed for SSI request execution. It carries resource name, user, routing hints, client identity, affinity, and handling options.

Important APIs/types: public fields are `rName`, `rUser`, `rInfo`, `hAvoid`, `client`, `affinity`, and `rOpts`. `Affinity` values are `Default`, `None`, `Weak`, `Strong`, and `Strict`. Resource options are `Reusable` and `Discard`. The constructor initializes all fields with defaults and sets `client` to null.

Control flow and state: this is a simple value-like data holder using owning `std::string`s for text fields and a borrowed `XrdSsiEntity *` for identity. There are no methods beyond constructor/destructor and no persistence.

Dependencies and integration: consumed by `XrdSsiProvider::QueryResource()`, `XrdSsiService::Prepare()/ProcessRequest()`, and concrete `XrdSsiFileResource`. Risks include public mutable fields, ambiguous ownership of `client`, and providers retaining borrowed pointers beyond lifetime. Test signals should cover constructor defaults, option bit combinations, affinity interpretation in client routing code, and copied resource behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResource.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRespInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRespInfo.hh

Purpose: defines the SSI response payload representation and alert-message abstraction. It is used mainly by server-side responders and transport code to communicate response type, metadata, and payload handle.

Important APIs/types: `XrdSsiRespInfo` has response union fields for data buffer, error message, file size, or stream pointer; a second union for buffer length, errno, or file descriptor; metadata length/pointer; and `Resp_t` values `isNone`, `isData`, `isError`, `isFile`, `isStream`, and `isHandle`. `Init()` resets all fields, and `State()` returns a textual state. `XrdSsiRespInfoMsg` wraps alert messages with `GetMsg()` and pure virtual `RecycleMsg(bool sent)`.

Control flow and state: `XrdSsiResponder::SetResponse()` fills this structure, and request/session code interprets it to return direct data, stream data, file data, or errors. The structure borrows all payload pointers/file descriptors; ownership and lifetime are controlled by responder `Finished()`.

Dependencies and integration: forward-declares `XrdSsiStream` and is included by request/responder/table protocol code. Risks include union misuse when `rType` is wrong, missing ownership semantics for file descriptors/streams/buffers, `isHandle` being declared but not handled by all transport code, and metadata pointer lifetime. Test signals should cover every `Resp_t`, `Init()` reset, `State()` strings, alert recycling on sent/unsent paths, and responder-finished cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRespInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResponder.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResponder.cc

Purpose: implements the server-side companion object that binds to an `XrdSsiRequest` and posts metadata, data, file, stream, or error responses. It is the controlled way for service tasks to reach private request response state.

Important APIs and control flow: `BindRequest()` links responder and request under `spMutex` then request mutex, resets response/error state, and calls request `BindDone()`. `Alert()` forwards alert messages or recycles them unsent. `GetRequest()` and `ReleaseRequestBuffer()` forward to the bound request. `SetMetadata()` validates metadata length and stores metadata without completing the response. `SetErrResponse()` copies error text into request `errInfo`, fills `Resp`, and executes response delivery. Other `SetResponse()` overloads fill data, file, or stream response fields. Macros `SSI_VAL_RESPONSE` and `SSI_XEQ_RESPONSE` enforce active binding, single-response posting, lock order, and client/server callback branching. `UnBindRequest()` succeeds only after `Finished()` cleared request `theRespond`, then calls request `Dispose()` and clears `reqP`. Destructor installs a static `ForceUnBind` responder if deleted before finish so eventual `Finished()` disposes safely.

State and persistence: state is per-responder `spMutex`, `reqP`, and reserved ABI fields. No persistence. The static `ForceUnBind` responder disposes orphaned server requests.

Dependencies and integration: depends on `XrdSsiRequest`, `XrdSsiRespInfo`, `XrdSsiStream`, and `XrdSsiRRAgent`. It is inherited by service/task objects that implement `Finished()`. Risks include strict lock ordering, response buffers needing to outlive `Finished()`, only one response allowed, destructor-before-unbind edge cases, and `SetMetadata()` not checking whether a response already exists. Test signals should cover normal bind/respond/finish/unbind, responder deletion before finish, duplicate responses returning `notPosted`, metadata size validation, client-side versus server-side `ProcessResponse()` execution, and alert forwarding after unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResponder.cc -->
