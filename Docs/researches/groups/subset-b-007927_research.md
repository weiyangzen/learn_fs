# Research: subset-b-007927

This grouped report covers the XrdCl utility, extreme-copy, XRootD message handler, and response object implementation files assigned to `subset-b-007927`. Each section is bounded by reconciliation markers so the guard can split the content into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.cc

## Purpose
`XrdClUtils.cc` implements the static utility surface declared in `XrdClUtils.hh`. It centralizes environment/URL parameter lookup, DNS address resolution and logging, time/byte formatting, checksum discovery and calculation, third-party-copy capability probes, lightweight config parsing, erasure-coding redirect validation, checksum-type inference, and chunk-list splitting for the XRootD C++ client.

## Important APIs, Types, And Functions
- `Utils::GetIntParameter` and `Utils::GetStringParameter` read a default from `DefaultEnv::GetEnv()` and let URL CGI parameters named `XrdCl.<name>` override it.
- `Utils::String2AddressType`, `GetHostAddresses`, and `LogHostAddresses` translate user-facing address-family preferences into `XrdNetUtils::AddrOpts`, resolve `host:port`, order IPv4/IPv6 partitions using `PreferIPv4`, optionally shuffle each partition, and log formatted network addresses.
- `Utils::TimeToString`, `GetElapsedMicroSecs`, and `BytesToString` provide formatting helpers used by diagnostics and user output.
- `Utils::GetRemoteCheckSum`, `GetLocalCheckSum`, `GetSupportedCheckSums`, `NormalizeChecksum`, and `InferChecksumType` coordinate checksum query/calculation and choose an interoperable checksum type across local files, metalinks, ZIP extraction, and remote `root`/`xroot` endpoints.
- `Utils::CheckTPC` and `CheckTPCLite` query server config for third-party copy and TPC-lite support, returning `suDone`, `suPartial`, or an error/fatal status depending on response shape.
- `Utils::GetDirectoryEntries`, `ProcessConfig`, `ProcessConfigDir`, and `Trim` provide small configuration-file helpers for `.conf` key-value input.
- `Utils::LogPropertyList` obfuscates sensitive values through `obfuscateAuth` before dump-level logging.
- `Utils::CheckEC` validates erasure-coded redirects behind `WITH_XRDEC`.
- `Utils::SplitChunks` breaks large `ChunkInfo` entries and/or long `ChunkList`s into bounded lists according to maximum chunk size and count.

## Control Flow
Most functions are single-purpose, synchronous helpers. Network-facing calls construct a `FileSystem`, `Buffer`, or `URL`, perform an XRootD query, validate the shape of the response, and translate malformed or unsupported responses into `XRootDStatus`/`Status`. `InferChecksumType` builds source and destination capability lists, gives local endpoints a fixed supported set, optionally extracts metalink/ZIP-supported checksums, and returns the first compatible type. `SplitChunks` walks an input `ChunkList`, starts a new output list when `maxc` is reached, and slices an in-progress `ChunkInfo` when its remaining length exceeds `maxcs`.

## State And Persistence Behavior
This file does not persist durable state. It reads global client environment values such as `PreferIPv4`, `IPNoShuffle`, `ZipMtlnCksum`, and checksum-manager state from `DefaultEnv`. `ProcessConfig` clears and repopulates the caller-provided map; `ProcessConfigDir` repeatedly calls `ProcessConfig`, so a later valid file replaces previously loaded entries because `ProcessConfig` clears the map on each file. DNS shuffling uses a static random engine seeded from system time. Output parameters carry results for address vectors, checksum strings, config maps, and chunk-list vectors.

## Dependencies And Integration Points
The implementation depends on `XrdClFileSystem`, `DefaultEnv`, `CheckSumManager`, `RedirectorRegistry`, `Message`, `Optimizers`, `XrdNetUtils`, `XrdNetAddr`, `XrdOucTUtils`, and XRootD protocol constants. It integrates with copy/checksum code, transport capability checks through `DefaultEnv::GetPostMaster()` in inline functions from the header, logging via `DefaultEnv::GetLog()`, and metalink redirector state through `RedirectorRegistry::Instance()`.

## Risks And Edge Cases
- `ProcessConfigDir` can unintentionally discard earlier parsed config entries because every `ProcessConfig` call clears `config`.
- `LogHostAddresses` erases the last comma without guarding an empty address vector, so callers must only log non-empty results.
- `NormalizeChecksum` strips leading zeroes for `adler32` and `crc32`; downstream comparisons must use normalized forms.
- Remote checksum parsing assumes exactly two whitespace-separated fields and matching type names.
- `CheckEC` uses `std::stoul` on URL parameters under `WITH_XRDEC`; malformed numeric CGI values can throw unless caught higher up.
- DNS order and shuffle behavior is environment-dependent, which can make connection selection nondeterministic unless `IPNoShuffle` is enabled.

## Test Signals
Useful coverage includes URL CGI override precedence, address-family option selection and no-shuffle behavior, malformed checksum/config responses, TPC/TPC-lite query responses including empty and partial support cases, EC redirect parameter validation, local/remote/ZIP checksum inference matrices, and `SplitChunks` boundaries for `maxcs`, `maxc`, zero-length inputs, and buffer pointer advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.hh

## Purpose
`XrdClUtils.hh` declares the XrdCl utility namespace class and small RAII helpers used across the client. It exposes shared helper APIs for parameter lookup, address resolution, checksum handling, TPC/EC/protocol capability checks, config parsing, logging, and chunk splitting.

## Important APIs, Types, And Functions
- `class Utils` is a static-method utility class with no instance state.
- `Utils::splitString` forwards to `XrdOucTUtils::splitString`, keeping XrdCl and XrdHttp on a shared split implementation.
- `enum AddressType` encodes `IPAuto`, `IPAll`, `IPv6`, `IPv4`, and `IPv4Mapped6`.
- Inline capability methods `GetProtocolVersion`, `HasXAttr`, `HasKSameFS`, and `HasPgRW` query the active transport through `DefaultEnv::GetPostMaster()->QueryTransport`.
- `Utils::SplitChunks` uses `ChunkList`/`ChunkInfo` from `XrdClXRootDResponses.hh`.
- `ScopedDescriptor` closes a POSIX file descriptor on destruction unless released.
- Linux-only `ScopedFsUidSetter` temporarily sets filesystem UID/GID with `setfsuid`/`setfsgid` and restores previous values in the destructor.

## Control Flow
The header is mostly declarations plus small inline helpers. `GetProtocolVersion` queries a transport property into an `AnyObject`, extracts a heap-allocated `int`, writes the output parameter, deletes the temporary, and returns transport status. Capability helpers short-circuit local files where appropriate and compare protocol versions to constants such as `kXR_PROTXATTVERSION`, `kXR_PROTCLONEVERSION`, and `kXR_PROTPGRWVERSION`. RAII helper destructors release OS-level state automatically.

## State And Persistence Behavior
`Utils` itself is stateless. `ScopedDescriptor` owns one integer descriptor until `Release()`. `ScopedFsUidSetter` stores requested UID/GID, previous UID/GID, stream name, and an `IsOk()` flag. The fsuid/fsgid changes affect the current process/thread filesystem credential state while the object is alive on Linux, so construction and destruction timing is significant.

## Dependencies And Integration Points
The header pulls in core XrdCl types (`Status`, `Log`, `URL`, `PropertyList`, `DefaultEnv`, `PostMaster`, `XRootDTransport`, `ChunkList`, `Message`) plus XrdNet and XrdOuc helpers. It is included by copy sources (`XrdClXCpSrc.cc`), response parsing, message handling, and other XrdCl modules needing common utilities.

## Risks And Edge Cases
- `ScopedFsUidSetter` calls `setfsuid`/`setfsgid` twice to verify state and can leave partial changes if one setter succeeds and the other fails before destruction restores only recorded previous values.
- `GetProtocolVersion` returns an OK status even when `AnyObject` does not contain an `int`; callers then see the unchanged `protver`.
- `HasPgRW` returns false for local files even though other capabilities return true locally; this distinction matters for page read/write copy logic.
- The header includes many dependencies, so changes here can increase rebuild cost and coupling.

## Test Signals
Compile-time tests should cover Linux and non-Linux builds, protocol-version thresholds, missing transport query data, local-file short-circuits, `ScopedDescriptor::Release()`, and fsuid/fsgid restore behavior in privileged or mocked environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.cc

## Purpose
`XrdClXCpCtx.cc` implements `XCpCtx`, the coordinator for "extreme copy" multi-source downloads. It owns the replica URL queue, source-thread list, shared sink of downloaded `PageInfo` chunks, block allocation cursor, file-size coordination, completion signaling, and reference-counted lifecycle used by `XCpSrc` workers.

## Important APIs, Types, And Functions
- `XCpCtx::XCpCtx` initializes URL queue, block/chunk/parallelism settings, offsets, condition variables, counters, and optionally calls `SetFileSize`.
- `~XCpCtx` drains remaining sink chunks and frees them through `XCpSrc::DeleteChunk`.
- `GetNextUrl` pops the next replica URL under `pMtx`.
- `WeakestLink` selects the running source with data and the lowest `TransferRate`, excluding a requester, and returns a retained source pointer via `Self()`.
- `PutChunk` pushes a downloaded `PageInfo*` into `pSink`.
- `GetBlock` allocates the next contiguous file range from `pOffset` and `pBlockSize`.
- `SetFileSize` publishes file size, broadcasts waiters, and adjusts `pBlockSize` relative to source parallelism and chunk size.
- `Initialize` creates `pParallelSrc` `XCpSrc` objects and starts their threads.
- `GetChunk` is the consumer-facing method that returns `suContinue` with a chunk, `suRetry` for a null wakeup, `suDone` when all data was received, or `errNoMoreReplicas` when all sources stopped.
- `NotifyIdleSrc`, `AllDone`, and `GetRunning` coordinate idle source wakeups and progress checks.

## Control Flow
After construction, the caller invokes `Initialize`, which creates source objects and starts one thread per source. Each source opens replicas, obtains blocks through `GetBlock`, reads chunks asynchronously, and calls `PutChunk`. The main copy loop repeatedly calls `GetChunk`; it marks the context done once `pDataReceived` equals `pFileSize`, fails if no source is running, otherwise consumes `pSink`. Idle sources use `AllDone` to sleep up to 60 seconds or wake when another source fails and work may be stealable.

## State And Persistence Behavior
`XCpCtx` keeps all state in memory. `pUrls` is destructively consumed. `pOffset` monotonically tracks allocated file ranges. `pFileSize` starts at `-1` until supplied by metalink input or discovered by a source stat. `pDataReceived` tracks bytes delivered to the consumer, not necessarily bytes still queued in `pSink`. `pDone` signals global completion/failure to source threads. `pRefCount`, `pDeleteCV`, and `pDelete` implement cooperative deletion: the creator calls `Delete()`, sources call `Release()`, and destruction waits until source-held references are gone.

## Dependencies And Integration Points
This file depends on `XCpSrc`, `SyncQueue<PageInfo*>`, `XrdSysMutex`, `XrdSysCondVar`, `DefaultEnv::GetLog()`, and XrdCl status constants. It is the bridge between higher-level copy code consuming `PageInfo` chunks and source workers reading from XRootD replicas.

## Risks And Edge Cases
- `GetBlock` assumes a known non-negative `pFileSize`; if called before `SetFileSize`, casting `-1` to `uint64_t` would be wrong. Source initialization sets file size before block allocation when unknown.
- `SetFileSize` can compute `pFileSize / pParallelSrc`; `pParallelSrc` must be nonzero.
- `GetChunk` compares `pDataReceived` to `pFileSize`; duplicate/stolen chunks or size mismatches must be prevented by `XCpSrc` or the completion logic can misfire.
- `AllDone` uses a 60-second timeout as both wakeup and periodic degradation check, which affects responsiveness.
- The lifecycle is manually reference-counted and sensitive to lock ordering documented in the header.

## Test Signals
Test with known and unknown file sizes, no valid replicas, partial source startup failures, zero-byte files, block-size adjustment around chunk boundaries, null wakeups from failed sources, and stealing scenarios where one source fails while holding ongoing work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.hh

## Purpose
`XrdClXCpCtx.hh` declares `XCpCtx`, the shared coordination object for the extreme-copy implementation. It documents the producer/consumer model where `XCpSrc` threads fetch chunks from multiple replicas and a caller consumes completed `PageInfo` objects from a synchronized sink.

## Important APIs, Types, And Functions
- Constructor accepts replica URLs, block size, parallel source count, chunk size, per-source chunk parallelism, and optional known file size.
- `Delete`, `Release`, and `Self` are the reference-counting API.
- `GetNextUrl`, `WeakestLink`, `RemoveSrc`, and `NotifyIdleSrc` are source coordination APIs.
- `PutChunk`, `GetChunk`, `GetBlock`, `SetFileSize`, and `GetSize` form the transfer coordination API.
- `Initialize` starts source threads.
- `AllDone` blocks idle sources until global completion, source failure, or timeout.
- Private state includes `pUrls`, `pSources`, `pSink`, `pOffset`, `pFileSize`, `pDataReceived`, completion/delete condition variables, and mutex/refcount fields.

## Control Flow
The intended lifecycle is: construct context, call `Initialize`, let sources call `Self()` and `Release()`, consume chunks through `GetChunk`, and finally call `Delete()` exactly once. `GetSize` waits on `pFileSizeCV` until `SetFileSize` publishes a non-negative file size or no sources remain running. The header explicitly records lock-order requirements for `pFileSizeCV`/`pMtx` and `pMtx`/`pDeleteCV`.

## State And Persistence Behavior
The class owns in-memory coordination state only. It does not own `pSources` pointers according to the comments; sources remove themselves on destruction. It owns queued `PageInfo*` chunks in `pSink` until the consumer takes them or the destructor frees leftovers. The reference-counting fields ensure the context outlives source threads.

## Dependencies And Integration Points
The header depends on `XrdClSyncQueue.hh`, `XrdClXRootDResponses.hh` for `PageInfo`, and `XrdSysPthread.hh`. It forward-declares `XCpSrc`, avoiding a full source-header dependency in the declaration. Higher-level copy code includes this header to start and consume multi-source transfers.

## Risks And Edge Cases
- `Delete()` must only be called once; the header states this but does not enforce it.
- The source list contains non-owned raw pointers, so source destruction/removal races are controlled only by the class's mutex and manual references.
- The `pDone` flag doubles as successful completion and failure shutdown signal for idle sources.
- `uint8_t` parallelism fields can overflow or truncate if callers pass larger values before construction.

## Test Signals
Useful tests exercise lifecycle ordering, concurrent `Self`/`Release`, blocking and wakeup of `GetSize`, all `GetChunk` status codes, and `WeakestLink` returning a retained source that remains valid until `Delete()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpCtx.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.cc

## Purpose
`XrdClXCpSrc.cc` implements a source worker for extreme copy. Each `XCpSrc` runs in its own thread, opens one replica at a time, optionally stats the file, reads chunks asynchronously with `File::Read` or `File::PgRead`, reports completed `PageInfo` chunks to `XCpCtx`, recovers from failing replicas, and steals work from slower or failed peers.

## Important APIs, Types, And Functions
- Local `ChunkHandler` is a `ResponseHandler` for async reads. It converts `AnyObject` responses into `PageInfo`, validates returned length, deletes buffers on errors, reports to the owning source, and self-deletes.
- `XCpSrc::Start`, static `Run`, and `StartDownloading` implement thread startup and the main worker loop.
- `Initialize` opens the next available URL, applies `ReadRecovery`, checks security/local metalink conditions for page-read support, stats unknown file size, publishes it to the context, and obtains the first block.
- `Recover` opens another URL, moves all ongoing chunks to `pRecovered`, clears outstanding work, and resets transfer-rate accounting.
- `ReadChunks` prioritizes recovered chunks, then reads new chunks from the current block up to `pParallel` asynchronous operations.
- `ReportResponse` reconciles async completion, failed handles, ignored stale responses, source file closure, report queueing, byte counters, and context chunk delivery.
- `Steal` transfers work from a failed or slower source using lock ordering based on mutex addresses.
- `GetWork` obtains another block or steals from `XCpCtx::WeakestLink`.
- `TransferRate` computes bytes per second using accumulated transfer time plus current active duration.

## Control Flow
The worker starts by calling `Initialize`. If initialization fails, it stops, wakes file-size waiters, and pushes a null chunk to prevent the consumer from blocking. The main loop calls `ReadChunks`. `suPartial` means no new local work remains but async reads are outstanding, so the source may request another block. `suDone` means no outstanding or local work; the source tries to get more work, then idles via `XCpCtx::AllDone`, periodically waking to steal degraded work. When an async status arrives from `pReports`, errors trigger `Recover`; if no replica remains, the source stops, wakes idle peers, pushes a null chunk, and waits until its outstanding work has been stolen or the copy completes.

## State And Persistence Behavior
`XCpSrc` owns an active `File*`, failed file handles tracked with outstanding counts, current URL, current block cursor/end, ongoing and recovered chunk maps keyed by offset, async status queue, transfer counters, and an atomic running flag. It holds a reference to `XCpCtx` for its lifetime. Buffers allocated for reads are transferred into `PageInfo` on success and eventually freed by the copy consumer or cleanup helpers. No durable state is written.

## Dependencies And Integration Points
The file integrates `XrdCl::File`, `ResponseHandler`, `AnyObject`, `PageInfo`, `XCpCtx`, `DefaultEnv`, `Utils::HasPgRW`, XRootD copy constants, pthreads, atomics, and logging. It is tightly coupled to `XCpCtx` block allocation and sink semantics and to the File async API's callback ownership model.

## Risks And Edge Cases
- In `Recover`, the page-read support condition differs from `Initialize` (`pFile->IsSecure()` check appears inverted), which may be intentional or a subtle inconsistency.
- `StartDownloading` contains a busy wait `while( HasData() && !pCtx->AllDone() );` after unrecoverable failure.
- `ReportResponse` must handle stale async responses after recovery or stealing; mistakes can double-free buffers or leak file handles.
- Work stealing removes ongoing chunks from another source; late responses from that source must be ignored by the erased-offset path.
- `TransferRate` adds one second to avoid division by zero, but sources with no data can still appear very slow and be selected as weak links only when `HasData()` is true.
- The code relies on manual self-deleting handlers and manual reference counts.

## Test Signals
Tests should cover failed open/stat and recovery to later replicas, length mismatch in `ChunkHandler`, stale async responses after recovery, PgRead enablement based on environment and protocol, chunk stealing from failed, recovered, block, and ongoing maps, and consumer wakeup on null chunk after source failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.hh

## Purpose
`XrdClXCpSrc.hh` declares `XCpSrc`, a per-replica worker used by extreme copy. It exposes thread lifecycle, reference counting, status/throughput inspection, and chunk cleanup helpers while keeping read, recovery, and stealing mechanics private.

## Important APIs, Types, And Functions
- Public constructor accepts chunk size, async parallelism, optional file size, and the shared `XCpCtx`.
- `Start`, `Stop`, `IsRunning`, `HasData`, `TransferRate`, `Self`, and `Delete` are used by the context and peer sources.
- `DeleteChunk` frees the buffer inside a `PageInfo` and deletes the `PageInfo` object.
- Private methods include `Run`, `StartDownloading`, `Initialize`, `Recover`, `ReadChunks`, `Steal`, `GetWork`, and `ReportResponse`.
- `FilesEqual` compares `File` objects by `LastURL` after stripping CGI query strings, helping separate active-handle responses from failed-handle responses.
- State fields include `pFile`, `pFailed`, `pOngoing`, `pRecovered`, `pReports`, recursive mutex, atomic running flag, and PgRead toggle.

## Control Flow
The public `Start` method spawns a pthread running `Run`. The thread calls `StartDownloading`, then `Delete`, making `XCpSrc` mostly self-owned after start. Async callbacks enter through friend `ChunkHandler`, which can call `ReportResponse`. Source peers and the context coordinate via `HasData`, `TransferRate`, and `Steal`.

## State And Persistence Behavior
`XCpSrc` stores transient transfer state. `pCurrentOffset`/`pBlkEnd` define the assigned block, `pOngoing` tracks issued async reads, `pRecovered` tracks chunks that must be retried or stolen, and `pFailed` defers closing failed file handles until their outstanding callbacks arrive. `pDataTransfered`, `pStartTime`, and `pTransferTime` are used for scheduling/stealing heuristics. No state survives process lifetime.

## Dependencies And Integration Points
The header depends on `XrdClFile.hh`, `SyncQueue`, pthread helpers, and C++ atomics. It forward-declares `XCpCtx`, but its implementation depends on `XCpCtx`, `Utils`, `DefaultEnv`, and XRootD response types. It is an internal part of the copy subsystem rather than a broad public API.

## Risks And Edge Cases
- Manual reference counting plus self-deleting thread flow makes ownership mistakes high impact.
- `Self()` can return `nullptr` if the object is already in destruction, so callers must check retained pointers.
- `DeleteChunk` assumes the `PageInfo` buffer was allocated with `new[] char`, which must match every producer path.
- `pParallel` and `pChunkSize` control memory pressure because each outstanding read allocates a buffer.

## Test Signals
Coverage should include `FilesEqual` with CGI differences, `Self()` during destruction, `HasData` for each work map/cursor condition, `DeleteChunk` ownership conventions, and thread start failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXCpSrc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.cc

## Purpose
`XrdClXRootDMsgHandler.cc` implements the main per-request XRootD protocol response handler. It matches incoming server responses to a request, decides whether bodies should be read normally or in raw mode, unmarshals protocol responses, handles redirects/waits/errors/retries, writes raw request bodies, parses typed responses for user handlers, manages stream IDs, and coordinates final callback delivery.

## Important APIs, Types, And Functions
- Local `WaitTask` resends a request after a `kXR_wait` delay; `HandleRspJob` moves callback processing to the job manager when needed.
- `Examine` matches stream IDs, classifies response statuses, sets up raw readers, handles partial `kXR_oksofar` and `kXR_status`, and returns transport action flags such as `Raw`, `RemoveHandler`, `NoProcess`, and `Ignore`.
- `InspectStatusRsp` unmarshals V2 status bodies for page read/write and decides whether more raw data or retry data must be read.
- `Process` unmarshals normal bodies, updates host protocol/flags, handles `kXR_ok`, `kXR_status`, `kXR_oksofar`, `kXR_error`, `kXR_redirect`, `kXR_wait`, `kXR_waitresp`, and invalid responses.
- `ReadMessageBody` delegates raw reads to `AsyncPageReader` for `pgread` or `pBodyReader` for read/readv/discard cases.
- `OnStatusReady` reconciles send-completion notifications with possibly already received responses and delayed retries.
- `IsRaw` and `WriteMessageBody` handle raw request bodies for write, writev, pgwrite, and checkpoint-execute requests, including kernel-buffer and TLS fallback behavior.
- `HandleResponse`, `ProcessStatus`, `ParseResponse`, and `ParseXAttrResponse` build `XRootDStatus`/`AnyObject` results and invoke the user's `ResponseHandler`.
- `RewriteRequestRedirect`, `RewriteRequestWait`, `UpdateTriedCGI`, and `SwitchOnRefreshFlag` mutate marshaled requests across redirect/wait/retry paths.
- `HandleError`, `RetryAtServer`, `HandleLocalRedirect`, `IsRetriable`, `OmitWait`, `RetriableErrorResponse`, and `DumpRedirectTraceBack` implement recovery policy and diagnostics.

## Control Flow
Outgoing send status and incoming response status race through `pSendingState` flags. On incoming data, `Examine` takes ownership of matching responses and tells the transport whether raw body handling is needed. `Process` then unmarshals and either completes, parses partial data, schedules waits, follows redirects, or calls `HandleError`. Recoverable errors can update `tried` CGI, refresh flags, and requeue the same request through `RetryAtServer`; fatal or expired conditions flow to `HandleRspOrQueue` and then `HandleResponse`. Final responses release stream IDs when appropriate, transfer host-list ownership to `HandleResponseWithHosts`, and delete the handler.

## State And Persistence Behavior
The handler owns the request unless it carries a session ID, current and partial responses, a response handler pointer, current URL, host trace, optional load balancer, SID manager, redirect counters, not-authorized retry counter, raw reader/writer offsets, PgWrite checksum cursor state, partial directory-list state, timeout fence, and redirect traceback. It mutates the in-memory request buffer during redirects/waits/retries and maintains `pHosts` as a path history. It does not persist durable state, but its request mutations affect subsequent sends on the same handler.

## Dependencies And Integration Points
This file is a central integration point for `PostMaster`, `TaskManager`, `JobManager`, `SIDManager`, `Message`, `MessageUtils`, `XRootDTransport`, `LocalFileHandler`, `RedirectorRegistry`, async raw/vector/page readers, sockets, TLS state, Xrd protocol structs/constants, `XrdOucPgrwUtils`, CRC/page-size helpers, and `DefaultEnv` configuration. It feeds typed objects defined in `XrdClXRootDResponses.hh` to user-facing response handlers.

## Risks And Edge Cases
- Send-completion and response-arrival races are subtle; incorrect `pSendingState` transitions can leak SIDs, invoke callbacks too early, or use a deleted handler.
- Redirect handling preserves selected CGI keys and credentials, rewrites paths, may collapse redirects, and can turn non-XRootD redirects into user-visible answers; small URL parsing changes can affect auth and recovery.
- Raw `pgwrite` writes checksum/data page pairs and tracks several offsets; off-by-one errors corrupt payload framing.
- `ParseResponse` contains many request-specific parsers; malformed lengths can cause invalid-response errors, but any missing guard risks buffer misuse.
- Retriable errors are policy-heavy and environment-dependent (`OpenRecovery`, `NotAuthorizedRetryLimit`, `MaxMetalinkWait`).
- `HandleLocalRedirect` bypasses normal final handling and deletes `this` after invoking local file handling.
- Manual ownership of `AnyObject`, response objects, host lists, requests, and self-deleting handler lifecycle increases leak/double-delete risk.

## Test Signals
High-value tests include response/request stream-ID matching, ok/oksofar/status partial read flows, read/readv raw body handling, pgread checksum/page framing and size mismatch detection, pgwrite retry body parsing, redirect URL/CGI preservation, redirect limits, wait scheduling and expiration, retriable errors through meta-manager and virtual redirector load balancers, TLS transient error downgrade limit, SID release/timeout behavior, local-file redirects, xattr parsing for set/get/list, and send/response race ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.hh

## Purpose
`XrdClXRootDMsgHandler.hh` declares `XRootDMsgHandler`, the `MsgHandler` implementation responsible for one XRootD client request, plus `RedirectEntry` for retry/redirect tracebacks. It defines the handler's public transport interface, private recovery/parsing helpers, and all state needed for asynchronous protocol processing.

## Important APIs, Types, And Functions
- `RedirectEntry` records `from`, `to`, redirect/retry/wait type, final status, and formats diagnostic trace entries.
- `XRootDMsgHandler` constructor wires request, user response handler, current URL, SID manager, local-file handler, default flags, and an async body reader selected by request id (`readv`, `read`, or discard).
- Public overrides implement `Examine`, `InspectStatusRsp`, `GetSid`, `Process`, `ReadMessageBody`, `OnStreamEvent`, `OnStatusReady`, `IsRaw`, and `WriteMessageBody`.
- Configuration setters include expiration, redirect-as-answer, oksofar-as-answer, load balancer, host list, chunk list, CRC digests, kernel buffer, redirect counter, metalink following, and stateful mode.
- Private helpers cover error recovery, retry, response parsing, request rewriting, tried-CGI updates, refresh flags, local redirects, retry eligibility, metalink wait omission, retriable error classification, traceback dumping, and buffer reads.
- `ChunkStatus`, constants `CksumSize`, `PageWithCksum`, `MaxSslErrRetry`, and `NbPgPerRsp` support page read/write checksum handling.

## Control Flow
The header shows the split between transport-facing callbacks and private state-machine methods. The handler starts with a marshaled request and becomes the rendezvous point for send notifications, incoming response headers/bodies, raw socket I/O, timer wakeups, and user callbacks. Atomic flags in `pSendingState` encode send done, response seen, final response, ready-to-send, retry-at-server, and in-flight completion milestones.

## State And Persistence Behavior
`XRootDMsgHandler` stores transient per-request state only. It may own `pRequest`, shares response messages with the message reader, owns partial responses, condition variables for oksofar-as-answer synchronization, raw-reader instances, redirect traceback entries, host list, redirect/effective data-server URLs, and mutable retry counters. Fields such as `pAsyncOffset`, `pAsyncChunkIndex`, and PgWrite checksum fields persist across socket retry writes within the same request.

## Dependencies And Integration Points
The header ties together `PostMasterInterfaces`, response models, `DefaultEnv`, `Message`, XRootD protocol headers, async readers, pthread/condvar utilities, kernel buffers, page-size helpers, `XrdOucPgrwUtils`, sockets, URLs, local-file handling, and SID management. Any module creating XRootD requests through the transport depends on this contract.

## Risks And Edge Cases
- The class is self-deleting after final responses, so public callbacks must not access it afterward.
- `pRequest` ownership changes when session IDs are present; destructor behavior depends on `pHasSessionId`.
- `pChunkList`, `pKBuff`, `pResponseHandler`, and `pLFileHandler` are raw pointers with lifetimes managed externally or by convention.
- `NbPgPerRsp` is sensitive to page alignment and checksum bytes; protocol changes require careful updates.
- Condition-variable use for oksofar responses must avoid deadlocks while partial responses are processed.

## Test Signals
Compile and behavioral coverage should exercise constructor reader selection, setter side effects (`SetChunkList` resizing status vector), `NbPgPerRsp` alignment cases, self-deletion final callback ownership, oksofar synchronization, and raw pointer lifetime assumptions under redirects and local-file handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDMsgHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.cc

## Purpose
`XrdClXRootDResponses.cc` implements the response model classes declared in `XrdClXRootDResponses.hh`. It parses textual and binary protocol response payloads into typed objects such as locations, stat information, directory listings, page read info, page-write retry info, and response-handler wrappers.

## Important APIs, Types, And Functions
- `LocationInfo::ParseServerResponse` and `ProcessLocation` parse space-separated location tokens into manager/server and access-type records.
- `StatInfoImpl::ParseServerResponse` parses normal and extended stat fields, including optional checksum bracket notation; public `StatInfo` accessors expose id, size, flags, times, mode, owner, group, and checksum state.
- `StatInfoVFS::ParseServerResponse` parses six VFS capacity/utilization fields.
- `DirectoryList::ParseServerResponse` handles normal line-separated entries and `kXR_dstat` style alternating entry/stat lines; `HasStatInfo` detects the stat-prefixed format.
- `PageInfo` wraps page/chunk offset, length, data buffer, CRC32C checksums, and repaired page count using a movable pimpl.
- `RetryInfo` wraps page offsets and lengths that need retransmission after `pgwrite` checksum errors.
- `ResponseHandler::Wrap` creates self-deleting response handlers from lambdas, with overloads for reference-style and pointer-style callbacks.

## Control Flow
Parser methods validate null/empty input, split payloads, convert numeric fields with `strtoll`/`strtol`, and return boolean success/failure. `DirectoryList` selects normal or stat-aware parsing based on a fixed prefix, constructs `ListEntry` objects, and attaches `StatInfo` to statful entries. `PageInfo` and `RetryInfo` are thin containers used by `XRootDMsgHandler::ParseResponse`. Lambda wrappers call user functions and delete themselves only on final responses, treating `suContinue` as partial.

## State And Persistence Behavior
All state is process memory in typed response objects. `StatInfo` uses a unique pimpl to keep implementation fields private while supporting copy construction. `DirectoryList` owns and deletes `ListEntry*` elements. `PageInfo` stores a raw buffer pointer but does not delete it in the destructor; buffer ownership is handled by consumers such as `XCpSrc::DeleteChunk` or higher-level read APIs. `ResponseHandler::Wrap` transfers ownership of status/response to `unique_ptr` only in the reference-style overload; the pointer-style overload passes raw ownership to the callback.

## Dependencies And Integration Points
This implementation depends on `XrdClXRootDResponses.hh`, logging/default environment headers, constants, `Utils::splitString`, C library conversion functions, and protocol constants. It is consumed by `XRootDMsgHandler` parsers and user-facing XrdCl response APIs.

## Risks And Edge Cases
- `StatInfoImpl` optional checksum parsing checks `chunks[11]` when `chunks.size() >= 10`; malformed responses with 10 or 11 fields could index out of bounds.
- `DirectoryList::ParseServerResponse` can leak objects on parse failure after adding entries because it returns false before local cleanup, relying on destructor only if the caller deletes the list.
- `PageInfo` raw buffer ownership is non-obvious and must match producer/consumer conventions.
- `ResponseHandler::Wrap` self-deletes on final response; callbacks must not retain the wrapper pointer.
- Numeric parsing accepts base auto-detection; unusual prefixes can affect interpretation.

## Test Signals
Tests should cover valid/invalid location tokens, stat parsing with minimal, extended, and checksum forms, malformed optional checksum field counts, VFS stat field conversion errors, directory lists with and without stat info and odd stat entry counts, `PageInfo` move assignment preserving buffer pointer and checksum vector, `RetryInfo` indexing, and lambda wrappers for partial versus final responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.cc -->
