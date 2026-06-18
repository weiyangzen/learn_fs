# Research: subset-b-007976

This grouped report covers the XRootD protocol AIO, bridge, callback, configuration, file handle, file locking, and file statistics files assigned to `subset-b-007976`. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.cc

Purpose: implements the base async-I/O buffer object used by normal xrootd AIO tasks. It connects an `XrdSfsAio` completion object to an `XrdXrootdAioTask`, owns a temporary `XrdBuffer` segment from the global `XrdXrootd::BPool`, and returns completed operations to the task.

Important APIs and functions: `XrdXrootdAioBuff::Alloc()` obtains a protocol segment-sized buffer, reuses an object from a static free queue when possible, initializes `sfsAio.aio_buf`, `aio_nbytes`, `cksVec`, `reqP`, and `buffP`, then increments the protocol AIO counter with `aioUpdate(1)`. `doneRead()` and `doneWrite()` both call `reqP->Completed(this)`. `Recycle()` decrements the protocol AIO counter, releases the buffer back to `BPool`, and either caches the object on a mutex-protected free list or deletes it once `maxKeep` is reached.

Control flow and state: the file maintains process-local static state `fqFirst`, `numFree`, and `fqMutex`; only AIO objects are cached, not data buffers. The callback path is intentionally short: filesystem completion calls `doneRead()` or `doneWrite()`, which enqueues the buffer in the request; request code later calls `Recycle()`.

Dependencies and integration: depends on `XrdBuffer`, `XrdSfsAio`, `XrdXrootdAioTask`, `XrdXrootdProtocol`, global `BPool`, and tracing. It is the normal buffer class beneath `XrdXrootdNormAio`-style file/link transfers; page read/write uses the derived `XrdXrootdAioPgrw`.

Risks and test signals: correctness depends on balanced `aioUpdate()` calls and exactly one `Recycle()` per allocation. Races concentrate around the free queue and around callbacks arriving after a task goes offline. Useful tests include buffer-pool exhaustion, concurrent completions, delayed completions after client disconnect, and tracing/counter assertions that active AIO counts return to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.hh

Purpose: declares the base async-I/O buffer class that adapts `XrdSfsAio` completions to xrootd protocol tasks. The type stores the associated task and buffer, while preserving a hook (`pgrwP`) for the page-read/write derived type.

Important APIs and types: `XrdXrootdAioBuff` inherits from `XrdSfsAio` and overrides `doneRead()`, `doneWrite()`, and `Recycle()`. `Alloc(XrdXrootdAioTask*)` is the factory. Public `next` is used by task pending queues and the static free list. `pgrwP` is a constant pointer set to null for base buffers or to the derived `XrdXrootdAioPgrw` instance for page I/O. Protected members `reqP` and `buffP` hold the owning task and the current pool buffer.

Control flow and state: constructors are simple placement-style initializers used by factories. The class deliberately exposes queue linkage rather than hiding it behind containers because these objects are hot-path completion nodes.

Dependencies and integration: includes only `XrdSfs/XrdSfsAio.hh` and forward-declares buffer, task, normal AIO, and page AIO classes. Implementations integrate with the global buffer manager and `XrdXrootdAioTask::Completed()`.

Risks and test signals: because `next` and `pgrwP` serve multiple queues and downcast-free access paths, misuse can cause stale links or wrong derived-object handling. Tests should cover reuse after recycle, derived-object allocation through base free-list storage, and completion callbacks for both read and write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioBuff.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.cc

Purpose: implements a per-file async read freight/order buffer that serializes AIO task execution by xrootd stream/path id. It prevents multiple AIO tasks for the same protocol path from running concurrently while allowing different path ids to progress independently.

Important APIs and functions: `Schedule(XrdXrootdAioTask*)` either sends a task to the global `XrdScheduler` immediately or appends it to the per-path linked queue if that path is already running. `Schedule(XrdXrootdProtocol*)` is called when a task finishes and starts the next queued task for that protocol path. `Reset()` discards all queued work; `Reset(XrdXrootdProtocol*)` discards queued work for one path. `Notify()` provides trace messages with operation type, offset, length, and file key.

Control flow and state: `Running[pathID]` is the key state bit. Under `fobMutex`, a newly scheduled task sees either `Running == false` and becomes active, or joins `aioQ[pathID]`. Completion calls the protocol overload, which dequeues one item and schedules it or clears `Running`. Reset recycles queued tasks with `Recycle(true)` and marks paths idle.

Dependencies and integration: uses `XrdScheduler`, `XrdXrootdAioTask`, `XrdXrootdFile`, `XrdXrootdProtocol::getPathID()`, and tracing. It is owned from `XrdXrootdFile::aioFob` and is reset on file destruction or link failure.

Risks and test signals: path ids must remain within `XrdXrootdProtocol::maxStreams`. Task cancellation must not race with scheduler dispatch. Tests should exercise same-stream serialization, multi-stream parallelism, reset during queued work, and disconnect cleanup that calls `Reset(protP)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.hh

Purpose: declares `XrdXrootdAioFob`, the queue manager used to order AIO tasks per protocol stream/path. It is a small synchronization and scheduling helper, not an I/O implementation itself.

Important APIs and types: public methods are `Reset()`, `Reset(XrdXrootdProtocol*)`, `Schedule(XrdXrootdAioTask*)`, and `Schedule(XrdXrootdProtocol*)`. Internal `AioTasks` stores `first` and `last` pointers for each per-stream queue. `Running[]` tracks whether a stream currently has a scheduled task. `maxQ` bounds reset scanning to streams that have been used.

Control flow and state: all queue mutation is protected by `fobMutex`. The task class is a friend only indirectly through public scheduling; the linked-list node is `XrdXrootdAioTask::nextTask`. The destructor calls `Reset()` so queued tasks do not leak when the owning file is closed.

Dependencies and integration: includes `XrdXrootdProtocol.hh` for `maxStreams` and path-id semantics, plus `XrdSysPthread` for the mutex. Owned by `XrdXrootdFile` and used by AIO task implementations.

Risks and test signals: the fixed array assumes protocol path ids are stable and bounded. Tests should check destructor cleanup, queue tail updates after dequeue, and handling of reset when `maxQ` is lower than `maxStreams`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.cc

Purpose: implements the page-read/page-write AIO buffer variant. It extends the base AIO buffer with checksum slots and an interleaved `iovec` layout for xrootd page data, where each page has a checksum followed by page bytes.

Important APIs and functions: the constructor lays out `ioVec` as alternating checksum and page entries, reserves `ioVec[0]` as a network-leading element, initializes `cksVec`, and labels the AIO object. `Alloc()` caches whole page AIO objects and keeps their larger `aioSZ` buffers instead of returning buffers on every recycle. `Setup2Recv()` and `Setup2Send()` call `XrdOucPgrwUtils::{recvLayout,sendLayout}` to validate offsets and lengths, set first/last segment lengths, choose the data pointer into the backing buffer, and fill `sfsAio`. `iov4Recv()`, `iov4Send()`, and `iov4Data()` expose correctly sized vectors; `iov4Send()` can convert checksums to network order.

Control flow and state: `csNum` is the active checksum/page count, and `iovReset` remembers a shortened last page segment that must be restored before reuse. `Recycle()` returns the full object to a smaller static free list (`maxKeep` 64) and intentionally retains the buffer to avoid churn for page I/O.

Dependencies and integration: uses `XrdOucPgrwUtils`, protocol page constants, `XrdXrootdPgrwAio::aioSZ`, global `BPool`, and file stats/tracing infrastructure. It is allocated by page-read/write task code and completed through the base `XrdSfsAio` callbacks.

Risks and test signals: off-by-one errors in `ioVec` indexing can corrupt checksum/data framing. Important tests include unaligned offsets, partial first and last pages, full 16-page segments, checksum byte-order conversion, no-checksum fallback via `noChkSums()`, and reuse after a truncated segment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.hh

Purpose: declares the page-read/write AIO buffer class used for xrootd page I/O requests. It specializes `XrdXrootdAioBuff` by adding checksum storage and scatter/gather layouts.

Important APIs and types: `Alloc()` returns a page buffer instance. `Setup2Recv()` prepares the object to receive page-write data from a socket and then write file data. `Setup2Send()` prepares file-read data for page-read response framing. `iov4Recv()`, `iov4Send()`, and `iov4Data()` expose `struct iovec` arrays for socket/file transfer stages. `noChkSums()` tests and optionally restores checksum-vector availability. Static constants `aioSZ` and `acsSZ` define the fixed page segment capacity.

Control flow and state: private `csVec[acsSZ]` stores checksums, while `ioVec[acsSZ*2+1]` stores the response/receive layout. `csNum` and `iovReset` are mutable per-operation state, reset across setup calls.

Dependencies and integration: includes xrootd protocol page constants and `XrdXrootdPgrwAio.hh`. It is tied to `XrdSfsAio` through the base class, and to protocol serialization through the iovec-returning APIs.

Risks and test signals: the header exposes low-level buffers where callers must honor returned counts and lengths. Tests should validate maximum segment capacity, short page framing, checksum restoration after `noChkSums()`, and ABI compatibility of the fixed iovec layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.cc

Purpose: implements common async task behavior for file-to-link reads and link-to-file writes. It coordinates completed AIO buffers, waits for outstanding operations, handles disconnects, validates read ordering, and maps filesystem/protocol errors to client responses.

Important APIs and functions: `Completed()` is called by AIO buffers and queues completions on `pendQ`, waking a waiting task or rescheduling an offline one. `getBuff()` returns the next completed buffer, optionally waiting via `Wait4Buff()`. `Drain()` recycles completed buffers while waiting briefly for in-flight requests, then marks the task offline/done. `gdDone()` and `gdFail()` implement network get-data callbacks for link-to-file writes. `SendError()` and `SendFSError()` log and send mapped xrootd errors. `Validate()` handles negative AIO results, short reads, zero-length EOF, embedded short blocks, and high-offset tracking.

Control flow and state: `aioMutex` protects `pendQ`, `Status`, and wait transitions. `inFlight` and `isDone` are atomic because completions can arrive from filesystem threads. `Status` cycles through `Running`, `Waiting`, and `Offline`. `finalRead` stores the one allowed short read; `pendWrite` stores a write buffer awaiting full network delivery.

Dependencies and integration: derives from `XrdJob` and implements `XrdXrootdProtocol::gdCallBack`. It uses `XrdScheduler`, `XrdXrootdResponse`, `XrdSfs` errors, `XrdXrootdAioFob`, `XrdXrootdFile`, and trace/error logging.

Risks and test signals: the most fragile areas are races between client failure, queued completions, and task recycle; timeout behavior in `Wait4Buff()`; and EOF validation for parallel reads. Tests should cover short reads at end-of-data, embedded zero blocks, AIO errors, link abort during read and write, drain with tardy completions, and ensuring `Recycle(true)` only happens after references are safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.hh

Purpose: declares the abstract base class for xrootd asynchronous file-transfer tasks. It provides shared queueing, error, drain, and callback machinery while requiring derived classes to implement actual read/write copy loops.

Important APIs and types: public `Init()` binds a task to a protocol, response, and file. `Read()`, `Write()`, and `Recycle()` are pure virtual. Protected pure virtuals `CopyF2L()`, `CopyL2F()`, and `CopyL2F(XrdXrootdAioBuff*)` define data movement. Shared helpers include `Completed()`, `getBuff()`, `Drain()`, `SendError()`, `SendFSError()`, and `Validate()`. The class is both an `XrdJob` and a `gdCallBack`.

Control flow and state: the class owns pending-completion pointers, protocol/file/link references, offset and length counters, state flags (`aioDead`, `aioHeld`, `aioPage`, `aioRead`, `aioSchd`), in-flight count, done flag, and status enum. A union reuses linkage fields for normal AIO, page AIO, or FOB task queues; another union reuses `finalRead` and `pendWrite`.

Dependencies and integration: includes protocol and pthread/atomic helpers, forward-declares buffers and file objects, and is scheduled through `XrdScheduler`. `XrdXrootdAioFob` is a friend for queue linkage.

Risks and test signals: because unions reuse pointers by operation mode, derived classes must set `aioState` and lifecycle fields consistently. Tests should focus on derived-class interactions with `inFlight`, `Status`, callback failure, and recycle paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.cc

Purpose: provides the concrete entry point for creating an xrootd protocol bridge session for non-xrootd protocol frontends. The implementation delegates bridge creation to the transit protocol layer.

Important APIs and functions: `XrdXrootd::Bridge::Login()` accepts a result callback object, an `XrdLink`, a security entity, a short client name, and protocol name. It returns `XrdXrootdTransit::Alloc(...)`, typed as `Bridge*`.

Control flow and state: there is no local persistent state in this file. It is intentionally a thin factory, keeping the public bridge API decoupled from the actual transit implementation.

Dependencies and integration: includes `XrdXrootdBridge.hh` and `XrdXrootdTransit.hh`. The bridge API is used by other protocol stacks such as HTTP-style frontends that need to inject xrootd-format requests and rewrite responses through `Bridge::Result`.

Risks and test signals: failures depend on `XrdXrootdTransit::Alloc()` semantics, not on this wrapper. Tests should verify login propagates null/error conditions correctly and that transit allocation receives the exact callback, link, security, name, and protocol arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.hh

Purpose: defines the public bridge interface that lets another request/response protocol reuse the xrootd protocol stack. It documents threading constraints, request injection, response rewriting, sendfile handoff, wait handling, and teardown.

Important APIs and types: `Bridge::Login()` creates a session bridge. Virtual `Run()` injects a network-format xrootd request plus optional data. `Disc()` disbands the bridge. `setSF()` toggles sendfile for an open handle. `SetWait()` configures wait handling. `Bridge::Context` carries link, request code, and stream id and has a virtual `Send()` for completing a pending sendfile response. `Bridge::Result` defines callbacks: `Data()`, `Done()`, `Error()`, `File()`, `Free()`, `Redir()`, `Wait()`, and `WaitResp()`.

Control flow and state: the API models asynchronous execution. `Run()` accepts one request; completion comes later through `Result`. For write requests, caller-owned buffers remain pinned until `Free()`. For sendfile responses, `File()` lets the foreign protocol reframe headers/trailers and explicitly call `Context::Send()`.

Dependencies and integration: uses xrootd wire types from `XPtypes.hh`, `XrdLink`, and `XrdSecEntity`. The concrete implementation is `XrdXrootdTransit`.

Risks and test signals: the interface requires callers to be thread-safe and not depend on thread-local state. Tests should cover one-request-at-a-time rejection, buffer lifetime through `Free()`, wait behavior with `SetWait()`, sendfile callback completion, and callback return values that terminate the bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.cc

Purpose: implements asynchronous filesystem callback handling for xrootd operations. It schedules response work away from the filesystem callback thread, then converts SFS callback results into xrootd response packets.

Important APIs and functions: internal `XrdXrootdCBJob::Alloc()` reuses callback jobs from a static free list. `DoIt()` dispatches special close, open, and statx handling, sends success or error responses, calls any nested errinfo callback, deletes or recycles state, and frees close file objects. `DoClose()` validates close results, sends final close responses, and returns the file object for disposal. `DoStatx()` rewrites statx text into xrootd file-type flags. `XrdXrootdCallBack::Done()` schedules a job. `sendError()` handles `SFS_DATAVEC`, `SFS_ERROR`, `SFS_REDIRECT`, stalls, `SFS_DATA`, and unknown SFS results. `sendResp()` and `sendVesp()` send async responses by request id.

Control flow and state: global static pointers to error logger, stats, scheduler, and port are installed by `setVals()`. `XrdOucErrInfo::getErrArg()` carries a packed `XrdXrootdReqID`; for close it is temporarily replaced from the file's saved callback argument.

Dependencies and integration: integrates SFS async callbacks with `XrdXrootdResponse`, `XrdXrootdMonitor::Redirect`, stats counters, scheduler jobs, and file lifecycle. It is initialized from protocol configuration before filesystem callbacks are possible.

Risks and test signals: response correctness depends on `ErrInfo` contents and callback result conventions. Tests should cover async open wait-zero retry, close success and invalid close result, redirect monitoring, vectored data responses, stall responses, missing clients during async send, and cleanup of external errinfo buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.hh

Purpose: declares the callback object passed into asynchronous SFS operations so xrootd can send delayed responses after filesystem completion.

Important APIs and types: `XrdXrootdCallBack` inherits `XrdOucEICB`. `Done()` is the callback entry point. `Func()` and `Oper()` expose operation metadata. `Same()` compares callback arguments by link id. `sendError()`, `sendResp()`, and `sendVesp()` format responses. Static `setVals()` installs logger, stats, scheduler, and port dependencies shared by all callbacks.

Control flow and state: each callback object stores only `Opname` and `Opcode`; most execution state is carried in `XrdOucErrInfo` and the static environment initialized at startup. `Done()` schedules asynchronous response work rather than performing all response I/O inline.

Dependencies and integration: includes xrootd protocol definitions, `XrdOucErrInfo`, and pthread support. Used throughout protocol methods that call asynchronous SFS functions.

Risks and test signals: static environment must be set before use. Tests should verify operation names/codes used in tracing, callback-argument matching, and response helper behavior for empty messages and vectored data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdConfig.cc

Purpose: implements startup-time configuration for the xrootd protocol layer. It parses `xrootd.*` directives, wires global protocol services, loads plugins, initializes security, monitoring, filesystem wrappers, redirects, AIO settings, file locking, admin sockets, prepare handling, TLS requirements, and advertised server role flags.

Important APIs and functions: `XrdXrootdProtocol::Configure()` is the top-level load-time initializer. It copies scheduler, buffer pool, stats, TLS, port, environment, and config pointers from `XrdProtocol_Config`; parses command-line exports; calls `Config()`; initializes packet marking, security, monitoring, filesystem, digfs, redirect plugins, AIO/sendfile policy, file locking, protocol/transit object stacks, prepare queue, redirect role, admin socket, extended attribute capability, bypass validation, and feature flags. `Config()` scans the config file and dispatches directives such as `async`, `bindif`, `chksum`, `diglib`, `export`, `fslib`, `fsoverload`, `gpflib`, `log`, `mongstream`, `monitor`, `prep`, `redirect`, `redirlib`, `seclib`, `tls`, `tlsreuse`, `trace`, and `limit`.

Control flow and state: directive parsers mutate many static protocol fields and local static plugin-path variables before `Configure()` consumes them. `ConfigFS()` loads a base filesystem and optional wrapper chain. `ConfigSecurity()` records daemon uid/gid names, exposes TLS/security pointers in the environment, loads the security service, and calls `CheckTLS()` when auth protocols require TLS. Redirect parsing stores function and path routes in `Route`, `RPList`, `RQList`, and client-domain settings. AIO parsing sets limits, segment sizes, timeouts, force/off/syncw/nosf/nocache flags, with final disabling based on filesystem features.

Dependencies and integration: depends on nearly every xrootd subsystem: SFS, net interfaces, TLS, security, monitoring, redirection plugins, admin sockets, `XrdBuffer`, `XrdLink`, request-id generation, and filesystem loaders. It exports environment variables such as `XRDEXPORTS`, `XRD_READV_LIMITS`, and checksum lists for other components.

Risks and test signals: this file has high blast radius. Risks include order-dependent initialization, stale heap strings when directives are repeated, mismatched TLS capability bits, redirect host parsing with dual public/private hosts, wrapper-chain load failures, and AIO settings inconsistent with buffer-pool recalculation. Tests should include config parser unit cases, integration boot tests for default/no config, TLS required without context, filesystem wrapper stacks, redirect path/function routes, monitor plus gstream options, async boundary values, and role flag advertisement for proxy/cache/pgrw/gpf features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdConfigMon.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdConfigMon.cc

Purpose: implements monitor and generic stream configuration for the xrootd protocol. It parses `monitor` and `mongstream` directives, stores defaults in a temporary parameter object, constructs g-stream providers, configures TPC monitoring, and initializes `XrdXrootdMonitor`.

Important APIs and functions: `ConfigMon()` applies `MonParms` defaults to `XrdXrootdMonitor`, initializes phase-one monitoring, calls `ConfigGStream()`, then enables monitoring. `ConfigGStream()` creates `XrdXrootdGSReal` objects for enabled provider streams (`ccm`, `oss`, `http`, `pfc`, `TcpMon`, `Throttle`, `Tpc`) and publishes them into the xrootd or outer environment. `xmon()` parses event monitoring options including flush intervals, file-stat options (`lfn`, `ops`, `ssq`, `xfr`), buffer sizes, ident records, redirection stream counts, timing window, and up to two UDP destinations. `xmondest()` validates and canonicalizes host:port endpoints. `xmongs()` selects g-streams and applies `flush`, `maxlen`, and `send` options. `xmongsend()` parses output format, header style, `noident`, and destination.

Control flow and state: `MP` accumulates multi-line monitor directives, with `...` continuing prior state. Destination-dependent mode bits are merged and duplicate destinations are coalesced. `gsObj` is static global stream configuration and persists until `ConfigGStream()` materializes stream objects.

Dependencies and integration: uses `XrdXrootdMonitor`, `XrdXrootdGSReal`, `XrdXrootdTpcMon`, `XrdNetAddr`, `XrdOucEnv`, and numeric parsers. Plugins can retrieve g-stream pointers from the environment.

Risks and test signals: parser behavior is stateful across continuation lines and supports two destination slots only. Tests should cover duplicate destinations, invalid endpoints, `fstat ssq` on non-IEEE platforms, implied `files` when `io` is selected, all g-stream selection, no-header send formats, and environment publication for HTTP/TPC streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdConfigMon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.cc

Purpose: implements xrootd's per-open-file wrapper and per-link file table. It tracks SFS file objects, sendfile and mmap capability, file statistics, AIO freight objects, file lock release, reference serialization, handle allocation, deferred handle reuse, and monitor close accounting.

Important APIs and functions: `XrdXrootdFile::XrdXrootdFile()` initializes stats, discovers sendfile fd support via `fctl(SFS_FCTL_GETFD)`, detects memory mapping with `getMmap()`, and records file size from mmap or `stat()`. `Init()` installs the global lock manager and logger. The destructor resets AIO, waits for outstanding references with `Serialize()`, deletes the SFS file, unlocks the file path, returns deferred handles through `XrdXrootdFileHP`, deletes freight objects, and frees `FileKey`. `Ref()` adjusts active references and wakes serialization waiters. `XrdXrootdFileTable::Add()` allocates file handles from an inline table, an expandable external table, or recycled deferred handles. `Del()` removes or holds a file entry, rolls page-read/write stats into normal read/write counters, reports monitor close events, and optionally defers deletion. `Recycle()` closes every table entry and destroys the table.

Control flow and state: table manipulation is externally serialized at the link level. `heldSpotP` marks a handle reserved for deferred close/reuse. `XrdXrootdFileHP` tracks handles that become reusable only after close callbacks finish. File-level `refCount` protects destructor-time cleanup from active requests.

Dependencies and integration: integrates SFS files, `XrdXrootdFileLock`, `XrdXrootdAioFob`, `XrdXrootdPgwFob`, monitoring, sendfile, mmap, and trace logging.

Risks and test signals: lifecycle is subtle around async close, deferred handles, and outstanding AIO. Tests should cover table growth, handle reuse after async close, monitor accounting, destructor waiting for references, sendfile disabled by fd discovery, mmap size detection, and lock release on all close paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.hh

Purpose: declares the per-open-file object, deferred file-handle processor, and per-link file table used by the xrootd protocol.

Important APIs and types: `XrdXrootdFileHP` stores reusable handles with reference-counted lifetime, `Avail()`, `Delete()`, `Get()`, and `Ref()`. `XrdXrootdFile` exposes SFS pointer, mmap/callback union, file key, mode, async and mmap flags, sendfile state, fd/handle union, AIO/page-write freight pointers, deferred handle processor, user id, and `XrdXrootdFileStats`. Its APIs are `Init()`, `Ref()`, `Serialize()`, constructor, and destructor. `XrdXrootdFileTable` has fixed `FTab[16]`, expandable `XTab`, `Add()`, `Del()`, `Get()`, and `Recycle()`.

Control flow and state: `Get()` rejects `heldSpotP` placeholders. `XrdXrootdFileHP` can outlive the table until all deferred file close operations return handles. `XrdXrootdFile` uses a semaphore pointer to let the destructor wait for request references to drain.

Dependencies and integration: includes protocol wire types, pthread helpers, and file stats. It forward-declares SFS, lock, monitor, and freight classes to keep the header relatively light.

Risks and test signals: external serialization is required for table mutation, so misuse can race with request handlers. Tests should verify `Get()` behavior for invalid and held handles, external table expansion, `XrdXrootdFileHP` deletion with outstanding refs, and reference wait/wakeup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock.hh

Purpose: defines the abstract file lock manager interface used by xrootd file open/close handling. It separates protocol code from the concrete lock-table implementation.

Important APIs and types: `Lock(path, mode, force)` attempts to acquire a read or write lock and returns zero on success or a conflict count/sign on failure. `numLocks(path, rcnt, wcnt)` reports current reader and writer counts. `Unlock(path, mode)` releases a lock and returns status.

Control flow and state: this header has no state. Concrete implementations decide lock persistence and conflict policy.

Dependencies and integration: used by `XrdXrootdFile::Init()` and file destruction to enforce export/open locking. The default configured implementation in this subset is `XrdXrootdFileLock1`.

Risks and test signals: protocol code assumes unlock is available at file destruction and that lock modes match open modes. Tests should cover read/write conflict semantics in implementations and forced-lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.cc

Purpose: implements the default single-process, per-host file lock manager using an in-memory hash table keyed by path. It tracks reader and writer counts and enforces simple read/write exclusion unless forced.

Important APIs and functions: `Lock()` looks up path state in global `XrdXrootdLockTable`. A read lock conflicts with existing writers unless `force` is true; a write lock conflicts with any reader or writer unless forced. It increments counts or creates a new `XrdXrootdFileLockInfo`. `numLocks()` returns current counts. `Unlock()` decrements the relevant count, rejects missing or underflowed locks, and deletes the hash entry when both counts reach zero.

Control flow and state: all hash access is protected by static `LTMutex`, wrapped by a small RAII helper `XrdXrootdLockFileLock`. State persists for the process lifetime in `XrdXrootdLockTable`.

Dependencies and integration: depends on `XrdOucHash`, `XrdSysMutex`, and the abstract `XrdXrootdFileLock` interface. Instantiated during protocol configuration and used by file open/close paths.

Risks and test signals: this manager is not distributed and only protects one server process. Tests should cover multiple readers, writer conflicts, forced locks, unlock without lock, count deletion at zero, and concurrent lock/unlock calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.hh

Purpose: declares the default in-memory implementation of the xrootd file lock interface for a single server per host.

Important APIs and types: `XrdXrootdFileLock1` implements `Lock()`, `numLocks()`, and `Unlock()` from `XrdXrootdFileLock`. It owns static `LTMutex` and a trace id in the implementation file. The destructor notes that the object is never destroyed in normal operation.

Control flow and state: lock table state is global to the implementation, not instance-local. This matches startup configuration that allocates one lock manager and installs it into `XrdXrootdFile`.

Dependencies and integration: includes pthread helpers and `XrdXrootdFileLock.hh`. It is created by `XrdXrootdProtocol::Configure()`.

Risks and test signals: inheritance is written without an explicit `public` keyword, so outside upcasts depend on construction/casts in implementation context; this is worth checking against compiler access expectations. Tests should compile and exercise the lock manager through the abstract interface and validate process-local semantics are documented for multi-server deployments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileStats.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileStats.hh

Purpose: defines per-file monitoring counters for transfer bytes, operation counts, page read/write activity, and optional sum-of-squares statistics used by xrootd monitoring.

Important APIs and types: fields include `FileID`, monitor table entry, monitor level, transfer-executed flag, opened file size, `XrdXrootdMonStatXFR`, `OPS`, and `PRW` structs, plus `ssq` accumulators. `Init()` resets all fields and establishes minimum sentinel values. Inline update methods include `pgrOps()`, `pgwOps()`, `pgUpdt()`, `rdOps()`, `rvOps()`, `wrOps()`, and `wvOps()`.

Control flow and state: updates are gated by `monLvl`; deeper stats are collected only at higher levels (`monOps`, `monSsq`). Normal reads/writes update byte counters, operation counts, min/max sizes, and optional sum-of-squares. Page read/write counters are accumulated separately and later folded into normal counters on file close by `XrdXrootdFileTable::Del()`.

Dependencies and integration: includes `XrdXrootdMonData.hh`, and is embedded directly in `XrdXrootdFile`. Monitoring close paths pass these counters to `XrdXrootdMonitor` and `XrdXrootdMonFile`.

Risks and test signals: counters are inline and likely updated from request paths, so thread safety depends on surrounding file/request serialization. Tests should validate min/max initialization, level-gated updates, page retry/error accounting, writev treatment as write, and close-time aggregation of page stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileStats.hh -->
