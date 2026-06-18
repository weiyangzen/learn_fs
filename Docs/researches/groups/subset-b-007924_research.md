# Research: subset-b-007924 XrdCl local file, message, operation, and queue support

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.cc

## Purpose

This file implements `XrdCl::LocalFileHandler`, the local-file backend used when XRootD client requests target `localhost` or a local redirect. It translates XRootD open/read/write/stat/sync/truncate/vector I/O and fattr requests into POSIX/XrdSys local filesystem calls while preserving the normal asynchronous client callback model.

## Important APIs, Types, And Functions

The main exported methods are `Open`, `Close`, `Stat`, `Read`, `ReadV`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `SetXAttr`, `GetXAttr`, `DelXAttr`, `ListXAttr`, `QueueTask`, `MkdirPath`, and `ExecRequest`. `OpenImpl` performs URL validation, flag translation, file opening, stat parsing, and `OpenInfo` construction. `XAttrImpl` parses `kXR_fattr` request bodies and dispatches to the xattr methods.

The anonymous `AioCtx` class wraps POSIX `aiocb` for non-Apple async read/write/fsync. It chooses `SIGEV_SIGNAL` with `SIGUSR1` or `SIGEV_THREAD` based on the `AioSignal` environment setting, converts `aio_return`/`aio_error` results into `XRootDStatus` plus optional `ChunkInfo`, and queues a `LocalFileTask` through the `JobManager` unless the handler is synchronous.

## Control Flow

User-facing calls either complete synchronously and enqueue a `LocalFileTask`, or submit POSIX AIO and return immediately. `Open` calls `OpenImpl`; if the error is not local it returns directly, otherwise the status and response are delivered through `QueueTask`. `ExecRequest` decodes `ClientRequest::header.requestid` and routes protocol messages to the matching method, including virtual readv/writev cases carried through `MessageSendParams::chunkList`.

`OpenImpl` accepts only valid URLs with hostname `localhost`, maps XRootD flags to `O_CREAT`, `O_EXCL`, `O_WRONLY`, `O_RDWR`, `O_RDONLY`, and `O_TRUNC`, optionally creates parent directories, opens with `XrdSysFD_Open`, builds `StatInfo` from `fstat`, and records a single host entry for callbacks. Reads and writes use `aio_read`/`aio_write` on most platforms and `pread`/`pwrite` on Apple. Vector reads/writes iterate `ChunkList` or iovec arrays and return `VectorReadInfo` where appropriate.

## State And Persistence

The handler stores an open file descriptor `fd`, the current URL `pUrl`, and a host list `pHostList`. Persistent effects are real local filesystem effects: file creation, truncation, writes, fsync, and extended attribute changes. There is no recovery journal. Callback state is heap-owned by `XRootDStatus`, `AnyObject`, `HostList`, `LocalFileTask`, and `AioCtx` until the response handler consumes it.

## Dependencies And Integration Points

The file integrates with `DefaultEnv`, `PostMaster`, `JobManager`, `LocalFileTask`, `MessageUtils`, XRootD protocol request structures, `XrdSysFD_Open`, `XrdSysXAttr`, `XrdSysFAttr`, `XProtocol::mapError`, `StatInfo`, `OpenInfo`, `VectorReadInfo`, `ChunkInfo`, and `SyncResponseHandler`. It depends heavily on POSIX APIs: `open`, `close`, `fstat`, `pread`, `pwrite`, `readv`, `writev`, `preadv`, `pwritev`, `ftruncate`, `fsync`, and POSIX AIO.

## Risks

The AIO path uses a single process signal (`SIGUSR1`) when configured, which can conflict with embedding applications. `AioCtx` owns a raw `HostList*` allocated in its constructor and never visibly deletes it, so ownership depends on `LocalFileTask` after success/error queueing and can leak if `aio_read`/`aio_write` submission fails. `WriteV` uses a variable-length stack array, which is non-standard C++ and risks large stack allocation for large vectors. Several write paths treat non-negative short writes differently: Apple `Write` loops, `VectorWrite` does not. `XAttrImpl` parsing is sensitive to body length and NUL termination. `Close` does not reset `fd`, so repeated close or later operations on a closed descriptor are hazardous.

## Test Signals

Useful tests include local `root://localhost/...` open/read/write/stat/close flows, open with `kXR_mkpath`, failure on non-localhost URLs, sync handler and async handler callback delivery, short read and EOF behavior, vector read/write with multiple chunks, writev partial-write simulation, xattr get/set/list/delete including malformed fattr bodies, AIO signal and thread modes, Apple and non-Apple builds, and error mapping for permission, missing file, invalid path, and closed descriptor cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.hh

## Purpose

This header declares `XrdCl::LocalFileHandler`, the client-side adapter that exposes the usual XRootD file operation surface for local files. It lets the rest of XrdCl execute protocol-shaped requests without knowing whether the target is remote or a local filesystem object.

## Important APIs, Types, And Functions

The public API mirrors file operations: `Open`, local redirect `Open(const URL*, const Message*, AnyObject*&)`, `Close`, `Stat`, `Read`, `ReadV`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, xattr methods, `QueueTask`, `MkdirPath`, `SetHostList`, `GetHostList`, and `ExecRequest`. Private helpers are `OpenImpl` and `XAttrImpl`.

The class owns `int fd`, `std::string pUrl`, and `HostList pHostList`. It accepts `ResponseHandler` callbacks and `MessageSendParams`, and returns `XRootDStatus` immediately while actual operation results are usually delivered later.

## Control Flow

Callers may invoke the typed methods directly, or `ExecRequest` may translate an incoming XRootD `Message` into a typed method. Most methods report completion through `QueueTask`, which creates or bypasses a `LocalFileTask` depending on the response handler type.

The overload accepting `URL` plus `Message` exists for local redirect handling: it extracts open flags and mode from a `ClientOpenRequest` and calls the same open implementation used by normal `Open`.

## State And Persistence

The header defines the state contract: one handler instance represents one local open file descriptor and a host list used for callback metadata. Local filesystem persistence is implemented in the `.cc` file, but the API exposes mutating operations such as write, truncate, sync, and xattr modification.

## Dependencies And Integration Points

The declaration depends on `XrdClJobManager.hh`, `XrdClLocalFileTask.hh`, `XrdClDefaultEnv.hh`, `XrdClLog.hh`, `sys/uio.h`, XrdCl response types, `ChunkList`, `xattr_t`, `Message`, `MessageSendParams`, `URL`, and `ResponseHandler`. It is consumed by message routing and postmaster code that needs to service local redirects.

## Risks

The class is not marked thread-safe, yet shared descriptor state could be used from asynchronous callbacks. Timeout parameters are present on most methods but local operations mostly ignore them after dispatch. `Fcntl` and `Visa` are declared in the same surface but implemented as unsupported, which callers must handle. The API accepts raw pointers for handlers, buffers, chunk lists, and response objects, so ownership discipline is critical.

## Test Signals

Header-level signals are build coverage across platforms, ABI compatibility for all declared overloads, successful compilation of code paths that use `ExecRequest`, and tests that direct file API calls and protocol-message calls produce equivalent statuses/responses for open, read, write, stat, sync, truncate, vector I/O, and xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.cc

## Purpose

This file implements the small job object used to deliver completed local-file results through the XrdCl job manager. It decouples local filesystem completion from user callback execution.

## Important APIs, Types, And Functions

`LocalFileTask::LocalFileTask` stores pointers to `XRootDStatus`, `AnyObject`, `HostList`, and `ResponseHandler`. `Run(void*)` invokes `responsehandler->HandleResponseWithHosts(st, obj, hosts)` when a handler exists. If no handler exists it deletes the status, response, and host list itself. It then deletes `this`.

## Control Flow

`LocalFileHandler::QueueTask` or AIO completion creates a `LocalFileTask` and queues it to `JobManager`. When the job manager runs it, ownership of response data transfers to the response handler through `HandleResponseWithHosts`; otherwise the task cleans up. The task self-destructs at the end of `Run`.

## State And Persistence

The task only stores transient heap pointers until execution. It has no persistent state and performs no filesystem mutation. Its persistence impact is indirect: it determines whether local operation results are delivered or deallocated.

## Dependencies And Integration Points

It depends on `XrdClLocalFileTask.hh`, `Job`, `ResponseHandler`, `HostList`, `XRootDStatus`, and `AnyObject`. It is queued by `LocalFileHandler` and executed by `JobManager`.

## Risks

The task assumes the response handler takes ownership of `st`, `obj`, and `hosts`. If a handler implementation does not delete or otherwise manage them, leaks result. `delete this` makes stack allocation or external ownership invalid, though current construction uses `new`. The unused `arg` parameter confirms this job is not context-driven.

## Test Signals

Tests should verify callback invocation with host metadata, cleanup when handler is null, no double-delete when handlers consume responses, and that synchronous local operations queued through the job manager eventually execute exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.hh

## Purpose

This header declares `XrdCl::LocalFileTask`, a `Job` subclass that packages a local-file operation result for asynchronous response delivery.

## Important APIs, Types, And Functions

The class exposes a constructor taking `XRootDStatus*`, `AnyObject*`, `HostList*`, and `ResponseHandler*`, a destructor, and `Run(void*)`. Private members retain those four pointers until the job runs.

## Control Flow

`LocalFileHandler` creates this job after local operations that should behave like normal asynchronous XrdCl operations. `JobManager` later calls `Run`, which is implemented in the `.cc` file.

## State And Persistence

All state is transient response state. The header establishes raw-pointer ownership passing from the producer to the job and then to the response handler or deletion path.

## Dependencies And Integration Points

It includes `XrdClStatus.hh`, `XrdClAnyObject.hh`, `XrdClJobManager.hh`, and `XrdClXRootDResponses.hh`. It integrates with the generic `Job` abstraction and `ResponseHandler` callback API.

## Risks

The ownership contract is implicit and raw-pointer-based. Copying is not disabled in the declaration, so accidental copies would duplicate pointer ownership; the class is only intended for heap allocation and single execution by the job manager.

## Test Signals

Build coverage, static analysis for accidental copies, and job-manager tests that local file tasks deliver or free all payload pointers are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.cc

## Purpose

This file implements XrdCl diagnostic output sinks and message formatting. It turns severity/topic-gated log calls into timestamped lines written to stderr or a configured file.

## Important APIs, Types, And Functions

`LogOutFile::Open`, `Close`, and `Write` manage append-only file output. `LogOutCerr::Write` writes to `std::cerr` under `XrdSysMutex`. `Log::Say` formats printf-style messages, prefixes each line with local timestamp, severity, topic string, and optional PID, then delegates to the current output sink. `SetTopicName`, `LogLevelToString`, `StringToLogLevel`, `TopicToString`, and severity wrappers `Error`, `Warning`, `Info`, `Debug`, and `Dump` implement the public logging behavior.

## Control Flow

Each severity method first checks the current log level and topic mask. If enabled, it starts a `va_list` and calls `Say`. `Say` grows a temporary buffer until `vsnprintf` fits, splits multi-line messages with `XrdOucTokenizer`, formats metadata, and writes the final string once.

## State And Persistence

`LogOutFile` persists messages to a file descriptor opened with `O_WRONLY | O_APPEND | O_CREAT` and user read/write permissions. `Log` maintains topic names, maximum topic width, masks, output sink pointer, and optional PID. The file does not persist configuration itself; it only writes log lines.

## Dependencies And Integration Points

It uses POSIX file APIs, `XrdSysE2T` for errno text, `XrdOucTokenizer` for line splitting, `XrdClOptimizers.hh` branch hints, and `XrdClLog.hh` declarations. It is used throughout XrdCl through `DefaultEnv::GetLog()`.

## Risks

`Log::SetOutput` deletes the current sink without synchronization, so changing sinks while other threads log is unsafe. `LogOutFile::Write` does not retry partial writes. `pTopicMap.rbegin()` is used by `RegisterTopic` in the header and requires at least one topic to exist before dynamic registration. Formatting errors are reported through the log output but not otherwise surfaced.

## Test Signals

Good signals include severity filtering, topic mask filtering, file-open failure behavior, multi-line formatting, long-message buffer growth, concurrent stderr writes, optional PID formatting, string-to-level parsing, and partial/closed file descriptor error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.hh

## Purpose

This header defines the XrdCl logging interface, output sink abstraction, severity levels, topic masking, and topic-name registry used across the client library.

## Important APIs, Types, And Functions

`LogOut` is the sink interface. `LogOutFile` writes to a file descriptor and `LogOutCerr` writes to stderr. `Log` exposes `Error`, `Warning`, `Info`, `Debug`, `Dump`, `Say`, `SetLevel`, `SetOutput`, `SetMask`, `SetTopicName`, `RegisterTopic`, `GetLevel`, and `SetPid`. `LogLevel` defines `NoMsg`, `ErrorMsg`, `WarningMsg`, `InfoMsg`, `DebugMsg`, and `DumpMsg`.

## Control Flow

Callers invoke a severity method with a topic bit and printf-style format. The implementation checks atomic `pLevel`, applies the mask for that severity, then formats in `Say`. Topic registration left-shifts the current highest topic number and stores a padded display name.

## State And Persistence

`Log` stores an atomic log level, masks indexed by severity, a heap-owned output sink, topic map, topic width, and PID. `LogOutFile` stores an open file descriptor. Persistence is limited to the sink chosen by the embedding environment.

## Dependencies And Integration Points

The header uses `<atomic>`, `<map>`, `<string>`, `<cstdarg>`, `XrdSysPthread.hh`, and compiler format attributes. It is included by nearly every XrdCl subsystem that emits diagnostics.

## Risks

Only the level is atomic; masks, topic map, output replacement, and PID are not guarded. `RegisterTopic` assumes an initialized topic map and can fail if called before any topic exists. `SetOutput` transfers ownership by raw pointer and deletes the previous output. Format attributes help GCC catch mismatches, but only for direct calls with visible format strings.

## Test Signals

Compile-time format checking, runtime severity and mask tests, dynamic topic registration tests, output replacement tests, and threaded logging stress are useful. ABI-sensitive tests should verify enum values and method signatures because logging is a cross-cutting service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMessage.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClMessage.hh

## Purpose

This header defines `XrdCl::Message`, the buffer-derived request/response container used throughout XrdCl for protocol messages plus metadata that is not part of the raw wire bytes.

## Important APIs, Types, And Functions

`Message` inherits `Buffer` and adds marshalled state, session ID, human-readable description, obfuscated description, and virtual request ID. Important methods are constructors, move assignment, `IsMarshalled`, `SetIsMarshalled`, `SetDescription`, `GetDescription`, `GetObfuscatedDescription`, `SetSessionId`, `GetSessionId`, `SetVirtReqID`, and `GetVirtReqID`.

## Control Flow

Message construction optionally allocates and zeroes the underlying buffer. Transport code marshals/unmarshals the raw buffer and flips `pIsMarshalled`. Higher layers set descriptions for logging and set virtual request IDs to distinguish synthetic operations such as virtual readv.

## State And Persistence

All state is in memory. Moving a message transfers the buffer and copies/moves metadata. `SetDescription` also stores `pObfuscatedDescription` by calling `obfuscateAuth`, preventing authorization parameters from leaking into logs.

## Dependencies And Integration Points

It depends on `XrdClBuffer.hh`, `XrdOucUtils.hh`, and `XrdOucPrivateUtils.hh`. It is consumed by `MessageUtils`, transports, message handlers, local file routing, redirectors, and logging.

## Risks

The move constructor does not clear the moved-from metadata, so moved-from objects should not be reused except destructively. `pIsMarshalled` must stay accurate; parsing code such as metalink CGI extraction branches on it. Descriptions are not automatically tied to buffer mutations except where callers update them, so stale descriptions are possible.

## Test Signals

Tests should cover construction with zeroing, move construction/assignment, description obfuscation for auth CGI parameters, session ID propagation, virtual request ID propagation, and marshalled flag use across transport round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMessage.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.cc

## Purpose

This file implements central helpers for sending, redirecting, rewriting, and constructing XRootD messages. It is the bridge between prepared `Message` buffers, stream ID management, `XRootDMsgHandler`, `PostMaster`, redirector registry, timeout defaults, CGI rewriting, and xattr protocol body encoding.

## Important APIs, Types, And Functions

`MessageUtils::SendMessage` allocates a stream ID, handles checkpoint embedded stream IDs, marshals the request, configures an `XRootDMsgHandler`, attaches host/load-balancer/chunk/kernel-buffer/CRC state, and calls `PostMaster::Send`. `RedirectMessage` registers a virtual redirector, marshals the request, configures a redirect-aware message handler, and calls `PostMaster::Redirect`.

`ProcessSendParams` fills default request timeout, expiry, and redirect limit from `DefaultEnv`. `RewriteCGIAndPath` updates path-bearing request bodies after redirects. `MergeCGI` merges parameter maps with replace-or-append semantics. The two `CreateXAttrVec` overloads encode xattr name/value vectors while enforcing protocol limits.

## Control Flow

Normal send flow obtains `PostMaster` and `SIDManager`, allocates `streamid`, marshals the message, creates `XRootDMsgHandler`, sets behavior flags from `MessageSendParams`, builds or takes ownership of a `HostList`, and sends. On send failure it unmarshals the request, releases the stream ID, deletes the handler, and returns the error.

Redirect flow registers the URL as a virtual redirector, marks the load-balancer host as manager/meta/virtual redirector, enables metalink following, and schedules a redirect through the postmaster. CGI rewriting inspects the protocol request ID, edits the path payload at offset 24 for supported request types, handles `mv` target path specially, and refreshes the transport description.

## State And Persistence

This file mutates transient message buffers, `MessageSendParams`, stream ID allocation state, redirector registry state, and handler-owned host lists. It does not persist to disk. Send failure cleanup is important because stream IDs are persistent within the SID manager until released.

## Dependencies And Integration Points

Dependencies include `DefaultEnv`, `Log`, `SIDManager`, `PostMaster`, `XRootDTransport`, `XRootDMsgHandler`, `RedirectorRegistry`, `URL`, XRootD protocol structures, `XProtocol`, xattr limits, and optional `LocalFileHandler`. It is called by high-level file and filesystem APIs before messages enter the transport layer.

## Risks

Ownership of `sendParams.hostList` is transferred by nulling the pointer; callers must not reuse it. If marshalled state or buffer sizes are wrong, `RewriteCGIAndPath` can corrupt request bodies. `RedirectMessage` deletes `list` after deleting `msgHandler` on failure, so handler ownership must match that cleanup path. `CreateXAttrVec` uses protocol limits but not semantic validation of attribute names. `ProcessSendParams` uses wall-clock `time(0)` and can be affected by time jumps.

## Test Signals

Test signals include successful send path with stream ID allocation/release on failure, checkpoint xeq stream ID rewrite, redirect setup flags, host list ownership transfer, timeout/default expiry behavior, CGI merge for open/stat/mv/locate with replace and append modes, xattr vector limit enforcement, and message description refresh after path rewrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.hh

## Purpose

This header declares message send parameters, synchronous/null response helpers, request construction helpers, and utility functions for sending, redirecting, rewriting, and xattr body construction.

## Important APIs, Types, And Functions

`SyncResponseHandler` blocks callers until `HandleResponse` stores a status and response. `NullResponseHandler` deletes itself when a response arrives and ignores the payload. `MessageSendParams` carries timeout, expiry, load balancer, redirect/chunk/stateful flags, host list, chunk list, redirect limit, kernel buffer, and CRC32C digests.

`MessageUtils` declares `WaitForStatus`, templated `WaitForResponse`, templated `CreateRequest`, `SendMessage`, `RedirectMessage`, `ProcessSendParams`, `RewriteCGIAndPath`, `MergeCGI`, `CreateXAttrVec`, and templated `CreateXAttrBody`.

## Control Flow

Synchronous callers create a `SyncResponseHandler`, submit an operation, wait on its condition variable, then extract and delete the status through `WaitForStatus` or extract a typed response through `WaitForResponse`. Request creation allocates a zeroed `Message` sized for a request struct plus payload. `CreateXAttrBody` builds the fattr body after the header and updates `dlen`.

## State And Persistence

`SyncResponseHandler` holds status/response pointers and a condition variable until consumed. `MessageSendParams` owns no memory by default but may transfer pointers to handlers during send. All state is transient.

## Dependencies And Integration Points

It includes response types, `URL`, `Message`, `XrdSysKernelBuffer`, and `XrdSysPthread`. It forward-declares `LocalFileHandler` and integrates with file/filesystem APIs, local redirects, transports, and xattr operations.

## Risks

`SyncResponseHandler::WaitForResponse` waits indefinitely if a response is never delivered. `NullResponseHandler` does not delete status/response/host payloads, relying on upstream behavior or intentionally leaking ignored responses. `WaitForResponse` sets the `AnyObject` to an `int*` null to detach the typed response; this depends on `AnyObject` semantics. `MessageSendParams` exposes raw pointers with unclear ownership until send-time conventions are followed.

## Test Signals

Useful tests include synchronous success/error waits, typed response extraction and ownership, request buffer sizing/zeroing, xattr body layout with path prefix, send parameter defaults, and static analysis of raw pointer ownership in `hostList`, `chunkList`, and kernel buffer fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMessageUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.cc

## Purpose

This file implements a virtual redirector backed by a metalink file. It downloads and parses the metalink, records target/checksum/replica metadata, and answers virtual redirect requests with the next untried replica or a protocol error.

## Important APIs, Types, And Functions

`MetalinkOpenHandler` opens the metalink and starts reading. `MetalinkReadHandler` reads chunks until EOF, accumulates content, parses it, finalizes initialization, and notifies the user. `MetalinkRedirector::Load`, `Parse`, `FinalizeInitialization`, `GetResponse`, `GetErrorMsg`, `HandleRequestImpl`, `HandleRequest`, `Count`, `InitCksum`, `InitReplicas`, `GetReplica`, and `GetCgiInfo` implement the redirector behavior. `DeallocArgs` is a helper for discarded callback payloads.

## Control Flow

`Load` opens the metalink URL with a `File` object created with `DisableVirtRedirect`. On open success, `MetalinkOpenHandler` schedules the first read. `MetalinkReadHandler` appends each `ChunkInfo` into `pContent` and schedules another read while bytes are returned. A zero-byte read closes the file object, parses the metalink using `XrdXmlMetaLink`, finalizes the redirector, handles pending redirect requests, and responds to the user handler.

Requests that arrive before parsing completes are queued in `pPendingRedirects` under `pMutex`. After readiness, `HandleRequestImpl` creates a synthetic `ServerResponse` with `kXR_redirect` and port `-1` for full-URL redirects, or a `kXR_error` message when loading failed or replicas are exhausted.

## State And Persistence

Persistent in-memory redirector state includes `pUrl`, `pFile`, checksum map, replica vector, readiness flag, initialization status, target name, file size, pending redirect list, and mutex. It does not persist to disk. Replica selection is stateless except for reading the request CGI `tried` list.

## Dependencies And Integration Points

It integrates with `File`, response handlers, `DefaultEnv`, `Log`, `JobManager`, `PostMaster`, `RedirectJob`, `VirtualRedirector`, `RedirectorRegistry`, `XrdXmlMetaLink`, `XrdOucFileInfo`, `URL`, `Utils::splitString`, and XRootD protocol response structs. The environment keys `GlfnRedirector` and `TlsMetalink` alter parsing and replica protocol rewriting.

## Risks

The read handler accumulates the whole metalink in memory without an explicit size cap. `FinalizeInitialization` calls `HandleRequestImpl` while holding `pMutex`, which can be risky if future redirect handling re-enters the redirector. `GetCgiInfo` searches for the key substring after `?` rather than parsing parameters exactly, so keys embedded in other names could match. `Count` subtracts vector iterators and returns `int`, which assumes vector size fits. Invalid or oversized replica URLs are silently skipped; an empty replica list becomes a runtime no-replicas error.

## Test Signals

Tests should cover successful metalink load, malformed XML, metalink with multiple files, empty replica list, checksum extraction including adler32/a32 mapping, target and size extraction, pending request replay, `tried` CGI filtering, `TlsMetalink` root-to-roots rewriting, synthetic redirect response wire layout, and callback cleanup on open/read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.hh

## Purpose

This header declares `XrdCl::MetalinkRedirector`, a `VirtualRedirector` implementation that serves redirects from replicas listed in a metalink file.

## Important APIs, Types, And Functions

Public methods are `MetalinkRedirector(const std::string&)`, `~MetalinkRedirector`, `Load`, `HandleRequest`, `GetTargetName`, `GetCheckSum`, `GetSupportedCheckSums`, `GetSize`, `GetReplicas`, and `Count`. Private methods include request handling, parsing, initialization finalization, response/error generation, checksum and replica initialization, replica selection, and CGI extraction.

State types include `RedirectList`, `CksumMap`, and `ReplicaList`. Friends `MetalinkOpenHandler` and `MetalinkReadHandler` access private members during asynchronous loading.

## Control Flow

Users construct with the metalink URL and call `Load`. Until loading completes, `HandleRequest` queues `(Message*, MsgHandler*)` pairs. After completion, requests are converted immediately into virtual redirect/error responses.

## State And Persistence

The object stores the metalink URL, a temporary `File`, parsed checksums and replicas, readiness status, target name, file size, pending redirects, and mutex. All persistence is in memory for the lifetime of the redirector.

## Dependencies And Integration Points

It includes `XrdClMessageUtils.hh` and `XrdClRedirectorRegistry.hh`, forward-declares `File`, `Message`, and `XrdOucFileInfo`, and derives from `VirtualRedirector`. It is used by the redirector registry and message handlers when following metalink redirects.

## Risks

The header exposes `GetReplicas` as a non-const reference to internal vector state, so callers can mutate replica order/content. Pending redirects store raw pointers to messages and handlers; they must remain valid until initialization. The checksum type mapping special-cases adler32/a32, so unknown aliases are not normalized.

## Test Signals

Header/API tests should verify virtual redirector polymorphism, loading lifecycle, checksum lookup behavior, supported checksum ordering, replica vector access, pending request behavior, and `Count` semantics for messages with and without `tried` CGI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMetalinkRedirector.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMonitor.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClMonitor.hh

## Purpose

This header defines the plugin interface for client-side monitoring. A shared library named by `XRD_CLIENTMONITOR` can provide `XrdClGetMonitor` and receive structured connection, file, copy, checksum, and error events.

## Important APIs, Types, And Functions

`Monitor` is an abstract base class with pure virtual `Event(EventCode, void*)`. Event payload structs are `ConnectInfo`, `DisconnectInfo`, `OpenInfo`, `CloseInfo`, `ErrorInfo`, `TransferInfo`, `CopyBInfo`, `CopyEInfo`, and `CheckSumInfo`. `EventCode` includes `EvCopyBeg`, `EvCopyEnd`, `EvCheckSum`, `EvOpen`, `EvClose`, `EvErrIO`, `EvConnect`, and `EvDisconnect`.

## Control Flow

The client runtime loads the monitor plugin externally and calls `Event` with an event code plus a pointer to the corresponding struct. The plugin casts based on the event code. Constructors initialize numeric counters, pointers, statuses, and timeval fields to safe defaults.

## State And Persistence

The header itself stores no runtime state. Each event struct is transient. Monitoring persistence depends entirely on the plugin implementation; this interface only defines data passed to it.

## Dependencies And Integration Points

It depends on `XrdClFileSystem.hh`, `URL`, `XRootDStatus`, `Status`, and `sys/time.h`. It integrates with connection management, file open/close accounting, copy jobs, checksum validation, and error reporting.

## Risks

The `void*` event payload API is ABI-sensitive and type-unsafe. Plugins must ignore unknown future event codes and must not retain pointers past their validity unless they copy data. Several struct fields are raw pointers to URL/status objects owned elsewhere. Typo-level interface stability matters because external shared libraries compile against this header.

## Test Signals

Signals include loading a test monitor through `XRD_CLIENTMONITOR`, verifying every event code receives the expected struct shape, connection byte/time accounting, file read/write counters, copy begin/end ordering, checksum timing/status reporting, error op-code classification, and ABI compatibility across builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClMonitor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationHandlers.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationHandlers.hh

## Purpose

This header provides response-handler adapters used by the operation pipeline DSL. It converts raw XrdCl callbacks into lambdas, packaged tasks, futures, single-xattr callbacks, extended-open callbacks, and raw forwarding handlers.

## Important APIs, Types, And Functions

Key classes are `UnpackXAttrStatus`, `UnpackXAttr`, `FunctionWrapper<Response>`, `FunctionWrapper<void>`, `TaskWrapper<Response, Return>`, `TaskWrapper<void, Return>`, `ExOpenFuncWrapper`, `PipelineException`, `FutureWrapperBase<Response>`, `FutureWrapper<Response>`, `FutureWrapper<void>`, `RawWrapper`, `RespBase<Response>`, `Resp<Response>`, and `Resp<void>`. Helpers `GetResponse<Response>(AnyObject*)` and `GetResponse<Response>(XRootDStatus*, AnyObject*)` extract typed payloads.

## Control Flow

Factories in `Resp` build a `ResponseHandler` from a raw handler pointer/reference, `std::future`, `std::function`, lambda-converted function, or packaged task. On callback, wrappers own and delete `XRootDStatus`, `AnyObject`, and sometimes `HostList` using `unique_ptr`, then call user code with references or fulfill promises. Xattr unpackers convert bulk xattr responses into single-operation responses for APIs that expect one attribute.

## State And Persistence

Wrappers store only transient user functions, tasks, promises, futures, or raw handler pointers. `FutureWrapperBase` records whether a promise was fulfilled and sets an exception in the destructor if not. There is no external persistence.

## Dependencies And Integration Points

It depends on `XrdClFile.hh`, `XrdClCtx.hh`, response types, `ResponseHandler`, `AnyObject`, `HostList`, `std::function`, `std::future`, `std::packaged_task`, and the operation pipeline in `XrdClOperations.hh`. `ExOpenFuncWrapper` integrates with `Ctx<File>` and calls `File::Stat` after open.

## Risks

`RawWrapper` forwards to a non-owned handler, so lifetime must exceed pipeline execution. `UnpackXAttrStatus` forwards error status without deleting `response`; callers rely on downstream ownership. `UnpackXAttr` deletes the extracted vector manually after resetting the response object, which depends on `AnyObject` ownership semantics. Function wrappers default-construct dummy responses on errors, requiring `Response` to be default-constructible. `ExOpenFuncWrapper` does not use the status returned by `f->Stat(false, info)` before dereferencing `info`, which is risky on stat failure.

## Test Signals

Tests should cover lambda, future, packaged task, raw handler, void response, non-void response, error response, missing response object, xattr single/bulk adapters, promise exception on abandoned future wrapper, extended-open stat success/failure, and handler lifetime under pipeline replacement/repeat paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationHandlers.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationTimeout.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationTimeout.hh

## Purpose

This header defines a lightweight timeout budget object for operation pipelines. It converts an original timeout into remaining seconds and throws when the operation has expired.

## Important APIs, Types, And Functions

`operation_expired` is an exception marker. `Timeout` has default and timeout constructors, copy constructor, assignment operator, and conversion operator `operator time_t() const`.

## Control Flow

Pipeline code stores a `Timeout` and passes it to operation runs. When converted to `time_t`, a zero timeout returns zero, otherwise elapsed wall-clock seconds are subtracted from the original budget. If elapsed time exceeds the budget, `operation_expired` is thrown and pipeline execution maps it to `errOperationExpired`.

## State And Persistence

`Timeout` stores `timeout` and `start` as `time_t`. There is no persistence. Copies preserve the original start time, so the budget travels through the pipeline.

## Dependencies And Integration Points

It uses `<ctime>`, `<cstdint>`, and `<exception>`. `XrdClOperations.hh` catches `operation_expired` in `Operation::Run`.

## Risks

The implementation uses `time(0)`, so system clock jumps can lengthen or shorten budgets. Resolution is one second. `operation_expired` does not override `what()`, which is fine for control flow but less useful for diagnostics.

## Test Signals

Tests should check zero timeout behavior, remaining-time conversion after delays, copy/assignment preserving start time, expiration throwing, boundary behavior when elapsed equals timeout, and pipeline mapping to `errOperationExpired`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationTimeout.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.cc

## Purpose

This file implements the runtime mechanics for the operation pipeline DSL declared in `XrdClOperations.hh`. It handles response propagation, pipeline finalization, repeat/replace/stop/ignore control actions, and movement of final callbacks.

## Important APIs, Types, And Functions

Internal exception-like control structs are `StopPipeline`, `RepeatOpeation`, `ReplaceOperation`, `ReplacePipeline`, and `IgnoreError`. Implemented methods include `PipelineHandler` constructor, `AddOperation`, `HandleResponseImpl`, `HandleResponseWithHosts`, `HandleResponse`, `Assign`, `PreparePipelineStart`, and the static `Pipeline::Stop`, `Repeat`, `Replace`, and `Ignore` methods.

## Control Flow

When an operation completes, `PipelineHandler::HandleResponseImpl` takes ownership of `this`, copies the status, calls the user response handler if present, and catches control exceptions thrown by user code. Stop finalizes the promise with a supplied status. Repeat reruns the current operation with the same handler. Replace swaps in a new operation or pipeline. Ignore converts a failed status to OK and continues.

If no control action occurs, the handler deallocates payloads when there is no user handler, finalizes the promise on error or end-of-pipeline, or runs the next operation with the carried promise/final callback. `PreparePipelineStart` moves a final callback attached to the last handler to the first handler before execution starts.

## State And Persistence

Pipeline state is transient: current and next operations, response handler, timeout budget, promise, and final callback. No external persistence exists. Completion is persisted only into a `std::future` result or thrown exception path.

## Dependencies And Integration Points

It depends on `XrdClOperations.hh`, logging/default environment headers indirectly, `ResponseJob`, `JobManager`, and the operation handler wrappers. It is used by the pipeline operators and high-level APIs that return futures or wait synchronously.

## Risks

The typo `RepeatOpeation` is harmless internally but can confuse maintenance. Control flow relies on exceptions thrown from user callbacks, so catching broad exceptions in user code may break pipeline controls. `ReplacePipeline` runs the replacement without explicitly attaching `myself`, changing handler ownership flow. `HandleResponseImpl` copies the status before user callback because the callback may delete it; custom handlers must still follow ownership rules. Promise fulfillment must happen exactly once across all control paths.

## Test Signals

Pipeline tests should cover normal multi-operation success, failure stopping, final callback execution, stop with custom status, repeat current operation, replace current operation, replace whole pipeline, ignore error and continue, no-user-handler cleanup, host list propagation, and future value/exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.hh

## Purpose

This header defines the XrdCl operation pipeline DSL. It represents once-use operations, chains them with `|`, binds handlers with `>>`, runs them asynchronously or synchronously, and supports final operations.

## Important APIs, Types, And Functions

`Operation<HasHndl>` is the abstract base with `ToString`, `Move`, `ToHandled`, `Run`, `RunImpl`, and `AddOperation`. `PipelineHandler` is the internal response handler that advances the pipeline. `Pipeline` owns the first operation and exposes chaining, conversion, `Run`, and static controls `Stop`, `Repeat`, `Replace`, and `Ignore`. Helper functions `Async` and `WaitFor` execute a pipeline. `ConcreteOperation<Derived, HasHndl, HdlrFactory, Args...>` is the CRTP base for concrete operations and implements `>>`, `|`, `Move`, `ToHandled`, and per-operation timeout setting.

## Control Flow

Concrete operations start unhandled. `operator>>` wraps a user handler in `PipelineHandler` and returns a handled operation. `operator|` ensures the left side has a pipeline handler, appends the right operation, and returns a handled operation. `Pipeline::Run` creates a promise/future pair, releases the first operation, prepares final callbacks, and invokes `Operation::Run`.

`Operation::Run` assigns timeout/promise/final/current operation to the handler, releases handler ownership, calls the concrete `RunImpl`, and schedules a `ResponseJob` if `RunImpl` fails synchronously or throws a mapped exception.

## State And Persistence

Operations are deliberately once-use. Move construction invalidates the source, and invalid operations should not be reused. Pipeline state is in `unique_ptr` operations/handlers plus a `std::future<XRootDStatus>`. No disk or long-term persistence is involved.

## Dependencies And Integration Points

The header pulls in response types, operation handlers, argument helpers, timeouts, final operations, `ResponseJob`, `JobManager`, `PostMaster`, and `DefaultEnv`. Concrete operation classes elsewhere derive from `ConcreteOperation` and provide `RunImpl`.

## Risks

`Pipeline::Run` has `if( !operation ) std::logic_error("Empty pipeline!")` without `throw`, so an empty pipeline can continue to dereference null. `ConcreteOperation::Timeout` returns `std::move(*me)`, invalidating the current object by convention but not marking `valid` itself. The once-use validity model depends on move constructors being used correctly. `Operation::Run` assumes `DefaultEnv::GetPostMaster()->GetJobManager()` exists when scheduling synchronous failure responses.

## Test Signals

Tests should verify invalid reuse throws, handler binding, pipeline chaining across handled/unhandled operations, final operation movement, per-operation timeout propagation, sync failure scheduling, exception mapping, empty pipeline behavior, `Async` future completion, and `WaitFor` blocking semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOperations.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOptimizers.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOptimizers.hh

## Purpose

This header centralizes branch prediction macros used in performance-sensitive XrdCl code.

## Important APIs, Types, And Functions

It defines `likely(x)` and `unlikely(x)`. With GCC they expand to `__builtin_expect(!!(x), 1)` and `__builtin_expect(!!(x), 0)`. On non-GCC compilers they evaluate to `x`.

## Control Flow

Call sites wrap conditions where the common or uncommon path is known. The macros do not change semantics; they only provide compiler hints where supported.

## State And Persistence

There is no state and no persistence.

## Dependencies And Integration Points

The macros are included by logging and other low-level code. They depend only on the `__GNUC__` preprocessor define.

## Risks

Overuse or wrong hints can hurt generated code layout. The non-GCC fallback lacks parentheses around `x`, so unusual expressions can behave differently in macro contexts. Macros live globally after inclusion and can collide with other definitions.

## Test Signals

Build tests on GCC and non-GCC compilers are sufficient. Preprocessor checks should confirm expressions compile in `if(likely(...))` and `if(unlikely(...))` contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOptimizers.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOptional.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOptional.hh

## Purpose

This header implements a small pre-`std::optional`-style `Optional<T>` plus a `none` sentinel for APIs that need optional values without depending on newer standard library facilities.

## Important APIs, Types, And Functions

`None` and global `none` represent an empty value. `Optional<T>` provides construction from `T`, construction from `None`, copy/move constructors, destructor, copy/move assignment, boolean conversion, and dereference operators. It uses a union `Storage` to reserve aligned memory without always constructing `T`.

## Control Flow

Constructing from `T` placement-news a value and sets `optional` to false. Constructing from `none` leaves storage uninitialized and sets `optional` to true. Copy/move constructors construct a value only when the source has one. Dereference returns `memory.value`.

## State And Persistence

Each instance stores a boolean flag and in-place storage for `T`. There is no persistence outside object lifetime.

## Dependencies And Integration Points

It uses `<utility>` for move operations. It can be used anywhere in XrdCl needing lightweight optional values.

## Risks

The boolean naming is inverted and the destructor appears wrong: `~Optional()` calls `memory.value.~T()` when `optional` is true, which is the empty state, and skips destruction when a value exists. That can destroy uninitialized storage for empty optionals and leak resources for populated optionals. Copy/move assignment also does not construct or destroy when transitioning between empty and populated states, so non-trivial `T` types are unsafe. Boolean conversion returns `optional`, meaning it is true when empty, opposite of `std::optional`.

## Test Signals

Tests should use a non-trivial tracking type to verify construction/destruction counts for empty and populated optionals, transitions through copy/move assignment, boolean semantics, dereference only when populated, and sanitizer coverage for uninitialized destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOptional.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.cc

## Purpose

This file implements `OutQueue`, a queue of outgoing messages and their handlers used by connection/postmaster code to buffer, retry, expire, or fail pending sends.

## Important APIs, Types, And Functions

Implemented methods are `PushBack`, `PushFront`, `PopMessage`, `PopFront`, `Report`, `GetSizeStateless`, `GrabExpired`, `GrabStateful`, and `GrabItems`. Each queue item stores a `Message*`, `MsgHandler*`, expiration timestamp, and `stateful` flag.

## Control Flow

Producers push messages at the back or front. Send loops call `PopMessage`, which returns the front message and outputs handler, expiry, and statefulness while removing the item. Failure/cleanup paths call `Report` to notify all queued handlers. Maintenance paths move selected messages from one queue to another: expired items by `expires <= exp`, stateful items by flag, or all items.

## State And Persistence

The queue stores an in-memory `std::list<MsgHelper>`. It does not own persistence. Ownership of message/handler pointers is transferred by queue operations but not deleted by `OutQueue` itself.

## Dependencies And Integration Points

It depends on `XrdClOutQueue.hh` and `XrdClPostMasterInterfaces.hh` for `MsgHandler::OnStatusReady`. It is used by transport/postmaster components managing pending sends, disconnects, and retry behavior.

## Risks

Despite the header comment saying synchronized, this implementation has no internal locking; callers must serialize access. `Report` assumes every item has a non-null handler. `PopFront` on an empty queue is undefined. Expiration comparison treats `expires == exp` as expired and default `exp = 0` will grab items whose expiry is zero. No deletion occurs for items left in a destroyed queue.

## Test Signals

Tests should cover FIFO/LIFO push behavior, pop metadata, stateless counting, expired transfer boundaries, stateful transfer, full transfer, report callback delivery, empty queue behavior under caller guards, and externally synchronized concurrent use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.hh

## Purpose

This header declares `XrdCl::OutQueue`, the outgoing message queue abstraction used to hold messages with their handlers, expiry times, and stateful/stateless retry semantics.

## Important APIs, Types, And Functions

The API includes `PushBack`, `PushFront`, `PopMessage`, `PopFront`, `Report`, `IsEmpty`, `GetSize`, `GetSizeStateless`, `GrabExpired`, `GrabStateful`, and `GrabItems`. `MsgHelper` is the per-item record with `Message* msg`, `MsgHandler* handler`, `time_t expires`, `bool stateful`, and `Reset`.

## Control Flow

Callers enqueue outgoing messages, pop them for transmission, report status to all pending handlers, or move subsets of items between queues based on expiry or statefulness. The queue uses `std::list` so moving/erasing while iterating is straightforward in the implementation.

## State And Persistence

`OutQueue` stores only in-memory list state. It does not own deletion semantics in the declaration; pointer lifetime is governed by the postmaster/transport code using it.

## Dependencies And Integration Points

It includes `<list>`, `<utility>`, and `XrdClXRootDResponses.hh`, and forward-declares `Message` and `MsgHandler`. It integrates with send queues, retry queues, expired queues, and disconnect handling.

## Risks

The "synchronized queue" comment is misleading because no mutex appears in the type. `MsgHelper::Reset` sets a bool to `0`, which works but shows C-style assumptions. Raw pointer ownership is implicit. `PopFront` has no empty check. `GetSize` returns `uint64_t` from `std::list::size`, which is fine but may hide native size type.

## Test Signals

Signals include compile coverage for forward declarations, queue size/is-empty behavior, stateless counting, movement methods preserving item order, status reporting through `MsgHandler`, and thread-safety tests at the caller level rather than inside `OutQueue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClOutQueue.hh -->
