# subset-b-007941 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.cc -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.cc

## Purpose

`XrdHttpMon.cc` implements the global HTTP monitoring collector for the XrdHTTP protocol plugin. It records per-request operation/status metrics for the `XrdXrootdGStream` JSON monitoring path and simpler verb/status counters for `XrdMonRoll`. The implementation is process-global and is initialized from `XrdHttpProtocol::Config()` when either monitoring integration is present in the protocol environment.

## Important APIs, Types, And Functions

- Static storage: `statsInfo`, `verbCounters`, `statusCounters`, `statsSchema`, `gStream`, `mrollP`, `flushPeriod`, `hasGStream`, `hasMonRoll`, and `isInitialized`.
- `Initialize(logP, gStream, mrollP)` wires logging, stores monitoring sinks, derives `flushPeriod` from `gStream->GetAutoFlush()`, registers the MonRoll schema, and marks monitoring initialized.
- `Start(void*)` is the background thread entry point. It sleeps for `flushPeriod` and repeatedly calls `Report()`.
- `Report()` serializes `GetMonitoringJson()` and inserts it into the GStream buffer.
- `Record(XrdHttpReq &req, int code)` is the central request lifecycle hook used by `XrdHttpProtocol` response senders. It ignores interim codes under 200, validates `req.request`, derives `StatusCodes`, and advances `req.monState`.
- `RecordCount()`, `RecordSuccess()`, `RecordErrProt()`, and `RecordErrNet()` update the GStream matrix.
- `GetMonitoringJson()` emits keys like `HTTP_GET_200` containing count, network error count, xrootd/protocol error count, success count, and total duration in seconds.
- `GetOperationString()`, `GetStatusCodeString()`, and `ToStatusCode()` map sparse public request/status codes into compact monitoring dimensions.

## Control Flow

Initialization is opt-in. `XrdHttpProtocol::Config()` passes GStream and MonRoll pointers from `XrdOucEnv`; if GStream is enabled it also starts `XrdHttpMon::Start()` on a thread. Normal response paths call `XrdHttpMon::Record()` from `SendSimpleResp()`, `StartChunkedResp()`, `ChunkResp()`, and network-error branches. `Record()` uses `XrdHttpMonState` as a small state machine: `NEW` records the request count and verb, `ACTIVE` records success and status, `ERR_NET` records network failure, `ERR_PROT` records backend/protocol failure after an HTTP response has begun, and `DONE` logs an unexpected duplicate record.

The GStream accounting intentionally splits total request count from final outcome. A response start records count by transitioning `NEW` to `ACTIVE`; final send or final chunk records success or error and transitions to `DONE`. MonRoll records only request verb at the first transition and status at final outcome transitions.

## State And Persistence

All counters are static process memory backed by `RAtomic_uint64_t`; resets only happen on process restart. `statsSchema` stores references to the MonRoll counters and must stay aligned with `XrdHttpReq::ReqType` and `StatusCodes`. `req.monState` and `req.startTime` live per request and are reset in `XrdHttpReq::reset()`. There is no on-disk persistence.

## Dependencies And Integration Points

This file depends on `XrdHttpMon.hh`, `XrdHttpReq.hh`, `XrdSysError`, `XrdXrootdGStream`, `XrdMonRoll`, C++ atomics wrappers, and `std::chrono`. It integrates with protocol response sending in `XrdHttpProtocol.cc`, request lifecycle state from `XrdHttpMonState.hh`, and request verb definitions in `XrdHttpReq.hh`.

## Risks And Edge Cases

- `Start()` loops forever and assumes a nonzero `flushPeriod`; with GStream enabled this is normally set, but defensive handling is minimal.
- `Report()` dereferences `gStream`; it is only started when GStream exists, so misuse outside `Config()` would be unsafe.
- MonRoll schema uses fixed enum index positions. Adding or reordering `XrdHttpReq::ReqType` without updating this mapping corrupts monitoring labels.
- `GetOperationString()` does not explicitly map `rtOPTIONS`, `rtPATCH`, `rtPOST`, or `rtCOPY`, so GStream may classify those as `UNKNOWN` while MonRoll has counters for them.
- Duration accumulation casts an atomic count through `std::chrono::microseconds` and then `std::chrono::duration<double>`; the variable name `duration_us` in `GetMonitoringJson()` is misleading because the JSON field is seconds.
- Duplicate calls after `DONE` only log; they do not repair counters.

## Test Signals

Useful tests should cover status-code mapping, verb mapping alignment, no-op behavior before initialization, state transitions `NEW -> ACTIVE -> DONE`, network/protocol error transitions, interim `100 Continue` not being counted as final, JSON serialization skipping zero-count entries, and MonRoll schema alignment when `ReqType` changes. An integration test can simulate `SendSimpleResp()` and chunked response paths with a fake request and monitoring sink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.hh

## Purpose

`XrdHttpMon.hh` declares the static monitoring facade used by XrdHTTP to collect request and response metrics. It exposes a small public API for initialization, background reporting, and response-path recording while hiding the global counter tables and mapping helpers.

## Important APIs, Types, And Functions

- `enum StatusCodes` defines a compact, dense set of monitored HTTP status buckets plus `sc_UNKNOWN` and `sc_Count`.
- `struct HttpInfo` stores cumulative atomic counters: total count, network errors, XRootD/protocol errors, successes, and summed duration in microseconds.
- `Initialize(XrdSysLogger*, XrdXrootdGStream*, XrdMonRoll*)` configures monitoring sinks.
- `Start(void*)` is the thread entry point for periodic GStream flushing.
- `Record(XrdHttpReq&, int)` is the only public per-response update API.
- `IsInitialized()` lets callers cheaply test global setup state.
- Private helpers `Record*`, `RecordGStream*`, and `RecordMonRoll*` keep runtime overhead low when a monitoring backend is disabled.

## Control Flow

The header establishes a split backend model. When GStream exists, the detailed `statsInfo[ReqType][StatusCodes]` matrix is updated and periodically serialized. When MonRoll exists, only `verbCounters` and `statusCounters` are incremented through a registered schema. The inline conditional helpers are intended to compile down to fast checks in response hot paths.

## State And Persistence

All state is static and process-wide. The stats matrix is indexed by `XrdHttpReq::ReqType::rtCount` and `StatusCodes::sc_Count`; `statsSchema` refers to static atomic counters. The class cannot be instantiated or destroyed by consumers.

## Dependencies And Integration Points

The header includes `Xrd/XrdMonRoll.hh`, `XrdHttpReq.hh`, `XrdSys/XrdSysRAtomic.hh`, and standard `array`, `chrono`, `string`, and `vector`. It forward-declares `XrdXrootdGStream` and `XrdSysLogger`. It is included by `XrdHttpProtocol.cc` and implemented by `XrdHttpMon.cc`.

## Risks And Edge Cases

- Public declarations depend on `XrdHttpReq.hh`, so changes to request type definitions can break monitoring dimensions.
- The dense `StatusCodes` enum must remain synchronized with `ToStatusCode()` and `statsSchema`.
- Static mutable members imply global lifetime and thread-safety concerns; counter fields are atomic but configuration flags and pointers are plain static values set during startup.
- `RecordMonRollVerb()` and `RecordMonRollStatus()` index arrays directly and rely on prior range checks in `Record()`.

## Test Signals

Header-level compatibility tests should compile with modified `ReqType` values and fail if schema/index assumptions are stale. Unit tests should exercise `IsInitialized()`, conditional updates when only one backend is enabled, and atomic counter increments through the public `Record()` path rather than private helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMonState.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMonState.hh

## Purpose

`XrdHttpMonState.hh` defines the request-local monitoring lifecycle enum used by `XrdHttpReq` and `XrdHttpMon` to classify outcomes across multi-step HTTP responses.

## Important APIs, Types, And Functions

- `enum class XrdHttpMonState : int` has five values:
  - `NEW`: request has not yet been counted.
  - `ACTIVE`: initial response has started and final outcome is pending.
  - `ERR_NET`: socket/TLS send failure should be recorded as a network error.
  - `ERR_PROT`: backend/protocol failure after a valid HTTP response began.
  - `DONE`: final monitoring record has been emitted.

## Control Flow

`XrdHttpReq::reset()` initializes `monState` to `NEW`. `XrdHttpMon::Record()` transitions `NEW` to `ACTIVE` on the first final response code and then transitions active/error states to `DONE`. `XrdHttpProtocol::SendData()` sets `ERR_NET` on failed send. `XrdHttpProtocol::ChunkResp()` sets `ERR_PROT` for final chunked responses when the bridge indicates `kXR_error` and monitoring is still `ACTIVE`.

## State And Persistence

The enum itself is stateless; persistence is the `XrdHttpReq::monState` field for a single request. It is intentionally reset per request and has no durable storage.

## Dependencies And Integration Points

It is included by `XrdHttpReq.hh`, and indirectly consumed by `XrdHttpMon.cc` and `XrdHttpProtocol.cc`. The file has no external dependencies beyond include guards.

## Risks And Edge Cases

- Correct classification depends on every response path calling `XrdHttpMon::Record()` in the expected order.
- Network errors before the first monitoring call may be represented differently than failures after `ACTIVE`.
- `DONE` duplicate detection is logging-only, so over-calling remains a correctness risk for metrics consumers.

## Test Signals

Tests should force simple response success, failed socket send, chunked response backend error, and duplicate finalization to confirm the expected `Record()` classification. Reset behavior should be verified by reusing an `XrdHttpReq` object across requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpMonState.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.cc -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.cc

## Purpose

`XrdHttpProtocol.cc` implements the connection-level HTTP/HTTPS protocol adapter for XRootD. It detects HTTP or TLS clients, owns the socket buffer and TLS session, parses the configuration file, authenticates clients, logs into the XRootD bridge, delegates logical HTTP/WebDAV work to `XrdHttpReq`, sends HTTP responses, loads plugins, and provides helper bridge operations such as stat and checksum queries.

## Important APIs, Types, And Functions

- Static configuration and runtime globals include TLS paths/options, redirect/listing/static-resource settings, token `secretkey`, gridmap/secxtractor state, external handlers, CORS handler, checksum handler, read-range config, static response headers, packet marking handle, and protocol object pool `ProtStack`.
- `XrdHttpProtocol(bool imhttps)`, `Reset()`, `Cleanup()`, and `Recycle()` manage object reuse, buffer ownership, SSL shutdown, `SecEntity` memory, and bridge/request state.
- `Match(XrdLink*)` peeks the connection to decide HTTP versus HTTPS, obtains/reuses a protocol instance, marks the link dialect as HTTPS for the framework, allocates a 1 MiB buffer, and binds the link.
- `Process(XrdLink*)` is the main state machine. It performs TLS handshake, token authentication for plain HTTP redirects, bridge login, header parsing, self-redirect, user-agent monitor info setting, and finally `CurrentReq.ProcessHTTPReq()`.
- Buffer helpers `BuffgetLine()`, `getDataOneShot()`, `BuffAvailable()`, `BuffUsed()`, `BuffConsume()`, and `BuffgetData()` implement a circular read buffer over `XrdLink` or OpenSSL.
- Response helpers `SendData()`, `StartSimpleResp()`, `SendSimpleResp()`, `StartChunkedResp()`, `ChunkResp()`, `ChunkRespHeader()`, and `ChunkRespFooter()` format HTTP/1.1 responses, apply static and CORS headers, integrate monitoring, and write through TLS or raw link.
- `Configure()` and `Config()` wire XRootD environment services, monitoring, checksums, OpenSSL BIOs, TLS context selection, plugin loading, CORS, header-to-CGI mappings, static headers, role detection, and object-pool cleanup.
- Directive parsers include TLS (`xhttpsmode`, `xsslcert`, `xsslkey`, `xsslcadir`, `xsslcafile`, `xsslverifydepth`, `xsslcipherfilter`, `xtlsreuse`, `xtlsclientauth`), auth/security (`xsecretkey`, `xgmap`, `xsecxtractor`, `xauth`), behavior (`xlistdeny`, `xlisting`, `xlistredir`, `xdesthttps`, `xselfhttps2http`, `xmaxdelay`), static content (`xembeddedstatic`, `xstaticredir`, `xstaticpreload`, `xstaticheader`), CORS/external handlers, tracing, and `xheader2cgi`.
- Plugin loaders `LoadSecXtractor()`, `LoadExtHandlerNoTls()`, `LoadExtHandler()`, `LoadCorsHandler()`, `ExtHandlerLoaded()`, and `FindMatchingExtHandler()` support dynamic extension points.
- `doStat()` and `doChksum()` construct bridge requests for `kXR_stat` and `kXR_query/kXR_Qcksum`.

## Control Flow

Connection dispatch begins in `Match()`, which classifies printable data as HTTP and non-printable TLS-like data as HTTPS only when HTTPS is configured. The selected protocol object is bound to the link and later processed by `Process()`.

`Process()` first initializes request timing for monitoring and ensures a client host is present in `SecEntity`. HTTPS connections run a nonblocking `SSL_accept()` flow, optional `secxtractor` SSL initialization, client auth through `HandleAuthentication()`, and then set `ssldone`. Plain HTTP with an opaque `xrdhttptk` validates redirect tokens and reconstructs security fields from signed CGI parameters; plain HTTP without a valid token is rejected when `secretkey` is configured.

After authentication, if no external handler matches, the protocol logs into `XrdXrootd::Bridge` using the derived `SecEntity`. Bridge login is asynchronous: `DoingLogin` and `DoneSetInfo` coordinate callbacks and optional `monitor info <user-agent>` submission through a `kXR_set` bridge request. Once logged in, buffered header lines are parsed into `CurrentReq`; incomplete headers return `1` to await more data, while malformed headers send `400` and close. A configured `selfhttps2http` path redirects suitable HTTPS requests to this same endpoint over HTTP with signed opaque credentials. Finally `CurrentReq.ProcessHTTPReq()` performs method-specific work.

Config flow starts in `Configure()`, records scheduler/buffer/logger/env handles, then calls `Config()`. `Config()` imports `XRD_READV_LIMITS`, initializes monitoring and optional thread, sets up checksum handling, constructs OpenSSL BIO callbacks, parses `http.*` directives, computes static header strings, loads CORS, resolves HTTPS auto/manual/disabled modes, initializes TLS if needed, loads external handlers, and initializes security.

## State And Persistence

Most settings are static process-global configuration. Per-connection state includes `Link`, `myBuff`, circular buffer pointers, `SecEntity`, TLS objects, `Bridge`, and `CurrentReq`. `Reset()` prepares an object for reuse but does not free all static configuration. `Cleanup()` returns buffers and frees TLS/security strings for the current connection. There is no persistent storage except configured files read at startup, preloaded static files stored in memory, and MonRoll/GStream process metrics.

## Dependencies And Integration Points

This file is tightly integrated with the XRootD core: `XrdProtocol`, `XrdLink`, `XrdBuffer`, `XrdBuffManager`, `XrdScheduler`, `XrdXrootd::Bridge`, `ClientRequest`, TLS (`XrdTlsContext`, OpenSSL `SSL/BIO`), security (`XrdSecEntity`, gridmap, secxtractor), tracing, packet marking, checksum handler, CORS plugin, external HTTP handlers, and monitoring. `XrdHttpReq` is a friend and directly accesses protocol internals such as `Bridge`, `Link`, response helpers, static settings, CORS, and buffer methods.

## Risks And Edge Cases

- Protocol detection is intentionally loose: printable bytes are accepted as HTTP, and TLS detection depends on `httpsmode`.
- `Match()` unconditionally marks the link address dialect as HTTPS/TLS after match, even before plain HTTP handling; this is a framework workaround and may surprise other integrations.
- The circular buffer code uses pointer arithmetic and aborts on invariant violations. Off-by-one mistakes or oversized headers can terminate the process.
- TLS handshake temporarily sets socket timeouts and relies on custom BIO callbacks; failures must not leak `ssl` or leave stale `sbio`.
- `xsecretkey()` permission check uses bitwise chaining in a way that may not express the intended "world readable or group writable" policy clearly.
- Static global config is mutable during startup and not protected by locks; runtime reconfiguration would be unsafe.
- `StartSimpleResp()` accepts arbitrary `header_to_add`; callers must ensure CRLF-safe content.
- Static preload reads up to 64 KiB but can leak allocated `StaticPreloadInfo` on failure after allocation.
- External handlers and secxtractor are dynamically loaded and trusted; matching happens before bridge login for paths they own.
- Monitoring finalization depends on response helper call order. `SendData()` failures set `ERR_NET`; callers must call monitoring again to record the error.

## Test Signals

High-value tests include HTTP/HTTPS protocol match, TLS disabled behavior, token-auth success/failure and expiry, self-redirect URL construction for IPv4/IPv6, header parsing with partial circular-buffer wrap, malformed and oversized headers, response header generation with static headers and CORS, chunked final/trailer monitoring paths, config parser directives including invalid inputs, external handler matching and no-TLS loading, `header2cgi` strip-on-redirect behavior, checksum query construction, and cleanup/recycle memory ownership. Integration tests should exercise bridge login callbacks, `DoingLogin` user-agent `kXR_set`, and keepalive versus close return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.hh

## Purpose

`XrdHttpProtocol.hh` declares the XRootD protocol plugin class that presents HTTP/WebDAV over the XRootD framework. It defines the connection adapter, configuration surface, bridge integration, buffer utilities, TLS/security state, response helpers, plugin registries, static resource settings, monitoring-adjacent dependencies, and friend access needed by `XrdHttpReq` and external request wrappers.

## Important APIs, Types, And Functions

- `class XrdHttpProtocol : public XrdProtocol` is the protocol object managed by `XrdObjectQ`.
- Public lifecycle and framework hooks: `Configure()`, `Match()`, `Process()`, `Recycle()`, `Stats()`, `DoIt()`, constructor/destructor, copy constructor, and assignment operator.
- Public helper operations: `doStat()`, `doChksum()`, `parseHeader2CGI()`, `isHTTPS()`.
- Public/static shared objects: `ProtStack`, `ProtLink`, `SecEntity`, `cksumHandler`, and `ReadRangeConfig`.
- Private response API used by `XrdHttpReq`: `StartSimpleResp()`, `SendSimpleResp()`, `StartChunkedResp()`, `ChunkResp()`, `ChunkRespHeader()`, `ChunkRespFooter()`, and `SendData()`.
- Private connection helpers: `CreateBIO()`, `getDataOneShot()`, `BuffgetLine()`, `BuffgetData()`, `BuffConsume()`, `BuffAvailable()`, `BuffUsed()`, `BuffFree()`, `GetClientIPStr()`, `Cleanup()`, and `Reset()`.
- Configuration parsers and loaders cover TLS, security extractors, CORS, external handlers, listings, static assets, header-to-CGI rules, trace, auth, and delay limits.
- `extHInfo` temporarily stores external handler load requests until enough config/environment context exists.
- `XrdHttpExtHandlerInfo` stores up to four loaded external handler instances by short name.
- Static configuration fields model role, TLS, redirects, static content, checksum list, packet marking, credential forwarding, and static response headers.

## Control Flow

The header shapes a two-level state machine. The XRootD framework calls `Match()` to claim a link, then `Process()` repeatedly as socket or bridge events arrive. `Process()` uses buffer methods and TLS helpers, then lets `CurrentReq` drive HTTP method work through bridge callbacks. `DoIt()` invokes `Resume` if set, but this code path is mostly dormant in the observed implementation.

Configuration functions are static because they apply to the protocol plugin rather than an individual connection. Loaded plugins and TLS context are shared by all instances. `friend class XrdHttpReq` and `friend class XrdHttpExtReq` intentionally expose protocol internals so request handlers can issue bridge commands and send responses without a large public API.

## State And Persistence

Per-instance mutable state includes the link, client address string, current request, bridge pointer, socket buffer, TLS session/BIO, security entity, login flags, resume fields, and HTTPS flags. Static state includes all configuration and plugin pointers. The object pool `ProtStack` reuses instances; destructor and recycle paths call `Cleanup()`/`Reset()`. There is no durable persistence defined by the header.

## Dependencies And Integration Points

This header pulls in many framework interfaces: `XrdProtocol`, `XrdObject`, `XrdSysError/Pthread`, `XrdSecInterface`, `XrdXrootdBridge`, `XrdOucStream/Hash`, `XrdHttpChecksumHandler`, `XrdHttpReadRangeHandler`, `XrdNetPMark`, `XrdHttpCors`, and `XrdHttpReq`. It also depends on OpenSSL and standard containers. Its primary local consumers are `XrdHttpProtocol.cc` and `XrdHttpReq.cc`.

## Risks And Edge Cases

- Friend-based coupling makes `XrdHttpReq` sensitive to private field changes.
- Static configuration fields mean tests and embedded uses must isolate global state carefully.
- `MAX_XRDHTTPEXTHANDLERS` is fixed at four and handler names are limited to 15 stored characters plus terminator.
- Raw pointers and manual ownership dominate TLS paths, security strings, buffers, preloaded static data, and plugins.
- `operator=` returns by value and is effectively a no-op; accidental use would be surprising.
- The response helper overloads have similar names but different semantics; misuse can skip monitoring or produce malformed headers.

## Test Signals

Compile and API tests should detect changes to friend-required private methods, handler limits, and static field declarations. Functional tests should instantiate protocol objects with fake `XrdLink`/buffer manager services, exercise recycle/reset behavior, and verify response helpers through `XrdHttpReq` because the intended API is friend-mediated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.cc -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.cc

## Purpose

`XrdHttpReadRangeHandler.cc` implements HTTP Range header parsing and converts client byte ranges into bounded XRootD `read` or `readv` requests. It also tracks returned bytes across short reads, split chunks, and multipart response boundaries so `XrdHttpReq` can send correct single-range or multipart/byteranges output.

## Important APIs, Types, And Functions

- `Configure(Eroute, parms, cfg)` parses `XRD_READV_LIMITS`-style values `<readv_ior_max>,<readv_iov_max>` into `Configuration`.
- `getError()`, `isFullFile()`, `getMaxRanges()`, `isSingleRange()`, and `ListResolvedRanges()` expose current request interpretation and error state.
- `ParseContentRange(line)` parses the HTTP `Range:` value. Despite the name, it accepts strings like `bytes=15-17,20-25`.
- `SetFilesize(fs)` supplies file length before resolving open-ended or suffix ranges.
- `NextReadList()` returns the next `XrdHttpIOList` to issue through bridge `read`/`readv`.
- `NotifyReadResult(ret, urp, start, allend)` advances handler state after bytes arrive and reports multipart boundary conditions.
- `NotifyError()` forces a generic error state.
- Private helpers `parseOneRange()`, `rangeFig()`, `resolveRanges()`, `splitRanges()`, and `trimSplit()` parse, normalize, split, and retry ranges.

## Control Flow

The handler begins with `reset()` for each HTTP request. Header parsing stores raw `UserRange` entries with possibly missing start or end offsets. Later, after file open/stat, `SetFilesize()` records the size. On the first call to `isSingleRange()`, `ListResolvedRanges()`, or `NextReadList()`, `resolveRanges()` translates raw ranges into absolute inclusive offsets using the file size, clamps ranges that extend past EOF, skips ranges beyond EOF, adds a full-file range when no Range header exists and the file is non-empty, and sets HTTP 416 when all requested ranges miss the file.

`NextReadList()` lazily splits resolved user ranges. If a previous split was partially read, it calls `trimSplit()` to remove acknowledged data and reissue the remaining portion; if no bytes were read for a nonempty pending split, it sets a 500 error to avoid infinite retries. `splitRanges()` uses one large `kXR_read` for full-file or single-range reads and packs multiple bounded chunks for multi-range `kXR_readv`, honoring `vectorReadMaxChunkSize_`, `vectorReadMaxChunks_`, and `rRequestMaxBytes_`.

`NotifyReadResult()` validates that ranges are resolved and a split is active, advances current split and resolved range offsets, detects crossing chunk or user-range boundaries, and reports whether the returned bytes start a user range or finish all user ranges. `XrdHttpReq` uses these flags to insert multipart headers and final boundaries.

## State And Persistence

All state is per handler instance and reset per request: raw ranges, resolved ranges, current split list, file size, split cursors, response cursors, and error state. There is no persistence beyond the `XrdHttpReq` that owns the handler. `reset()` clears and `shrink_to_fit()`s vectors, which releases capacity but may increase churn under repeated requests.

## Dependencies And Integration Points

The implementation depends on `XrdHttpUtils.hh` for `XrdHttpIOList`, `XrdOuca2x` for config parsing, `XrdOucTUtils::splitString`, `XrdOucUtils::trim`, C string tokenization, and standard containers. `XrdHttpReq.cc` calls it during header parsing, open/stat post-processing, GET header formation, read scheduling, read callback handling, and footer error handling.

## Risks And Edge Cases

- `ParseContentRange()` uses `strdup(line)` without checking allocation failure and assumes `line` is non-null.
- Invalid syntax clears all raw ranges and deliberately ignores the header, matching HTTP behavior, but callers cannot distinguish invalid range syntax from no Range header.
- `rangeFig()` accepts negative values from `strtoll()`; later logic does not explicitly reject negative start/end values.
- `filesize_` defaults to zero. Calling resolve paths before `SetFilesize()` can classify all explicit ranges as unsatisfiable.
- `splitRanges()` calls `isSingleRange()`, which may call `resolveRanges()` recursively only when unresolved; current state prevents infinite recursion but the coupling is subtle.
- `NotifyReadResult()` assumes bridge results arrive in the same order and sizes do not cross split or user-range boundaries.
- Repeated `shrink_to_fit()` in `reset()` may be expensive under high request rate.
- The hardcoded 500 errors for internal range tracking failures are appropriate for server issues but can obscure backend short-read behavior.

## Test Signals

Unit tests should cover no Range header, empty file, closed ranges, suffix ranges, open-ended ranges, overlapping and out-of-order multi-ranges, ranges beyond EOF, malformed headers ignored as full-file, `XRD_READV_LIMITS` parsing, negative values, split limits, partial read retry through `trimSplit()`, zero-byte read protection, `NotifyReadResult()` boundary flags, readv ordering assumptions, and 416 error generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.hh

## Purpose

`XrdHttpReadRangeHandler.hh` declares the request-local helper that interprets HTTP Range headers and manages the read scheduling/acknowledgement state for GET responses. It hides the details of HTTP byte-range normalization and XRootD read/readv chunking behind a compact API consumed by `XrdHttpReq`.

## Important APIs, Types, And Functions

- Constants `READV_MAXCHUNKS`, `READV_MAXCHUNKSIZE`, and `RREQ_MAXSIZE` provide default limits of 512 chunks, 512 KiB per readv chunk, and 8 MiB per whole read request.
- `struct Configuration` optionally overrides chunk size, number of chunks, and total request size.
- `struct Error` stores an HTTP return code and message with `operator bool()` for error presence.
- `struct UserRange` represents raw or resolved ranges with independent start/end presence flags.
- `using UserRangeList` aliases `std::vector<UserRange>`.
- Public methods include constructor, static `Configure()`, `getError()`, `getMaxRanges()`, `isFullFile()`, `isSingleRange()`, `ListResolvedRanges()`, `NextReadList()`, `NotifyError()`, `NotifyReadResult()`, `ParseContentRange()`, `reset()`, and `SetFilesize()`.
- Private state fields track raw ranges, resolved ranges, split read chunks, file size, and multiple cursor offsets for both issued chunks and received data.

## Control Flow

Construction sets default limits or configured limits, then resets state. The expected call order is: `ParseContentRange()` during header parsing, `SetFilesize()` after open/stat, `ListResolvedRanges()` or `NextReadList()` to resolve and split, repeated bridge reads using returned `XrdHttpIOList`, and `NotifyReadResult()` for every received data segment. `reset()` makes the instance reusable for the next HTTP request.

## State And Persistence

State is entirely in the object. The handler owns all vectors it returns references to; callers must treat references as invalid after `reset()` or the next splitting call. `Error` state is sticky until reset. The referenced `Configuration` is copied into scalar limits by the constructor, so the caller does not need to keep the configuration object alive despite the comment saying otherwise.

## Dependencies And Integration Points

The header includes `XrdHttpUtils.hh`, `vector`, and `string`, and references `XrdSysError` through the `Configure()` declaration via included dependencies. The central integration is `XrdHttpReq`, which owns a handler instance and uses it to decide `kXR_seqio`, build GET headers, choose read versus readv, format multipart bodies, and decide trailer errors.

## Risks And Edge Cases

- Comments contain a few terminology errors (`Content-Range` versus `Range`, "Incidcates", "eiter"), which can mislead maintainers but not runtime behavior.
- Public methods return const references to internal containers, so caller lifetime discipline matters.
- `SetFilesize()` must occur before resolution; after resolution, changing file size is an error.
- The API does not expose whether a malformed Range header was ignored.
- Offsets use `off_t`, but chunk sizes are `size_t` and `int` in places; very large files/ranges need careful conversion tests.

## Test Signals

API-level tests should validate constructor defaults and overrides, reference invalidation expectations, sticky errors, call-order errors such as `SetFilesize()` after resolution, and `getMaxRanges()` behavior before file size is known. Integration tests should confirm `XrdHttpReq` chooses `kXR_seqio` only when `getMaxRanges() <= 1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.cc -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.cc

## Purpose

`XrdHttpReq.cc` implements the logical HTTP/WebDAV request handler sitting behind `XrdHttpProtocol`. It parses request lines and headers, maps HTTP methods to XRootD bridge operations, handles GET/HEAD/PUT/DELETE/PROPFIND/MKCOL/MOVE/OPTIONS behavior, formats responses, processes bridge callbacks, manages range reads and chunked transfers, constructs redirects and opaque credentials, and resets per-request state for keepalive reuse.

## Important APIs, Types, And Functions

- Parsing helpers: `parseFirstLine()`, `parseLine()`, `parseHost()`, `parseScitag()`, `parseResource()`, `sanitizeResourcePfx()`, `addCgi()`, `parseBody()`, `trim()`, and `ISOdatetime()`.
- Bridge callback methods inherited from `XrdXrootd::Bridge::Result`: `Data()`, `File()`, `Done()`, `Error()`, and `Redir()`.
- Request execution: `ProcessHTTPReq()` is the main method-specific state machine.
- Response post-processing: `PostProcessHTTPReq()`, `PostProcessChecksum()`, `PostProcessListing()`, `ReturnGetHeaders()`, and `sendFooterError()`.
- Range and read helpers: `ReqReadV()`, `clientMarshallReadAheadList()`, `clientUnMarshallReadAheadList()`, `buildPartialHdr()`, `buildPartialHdrEnd()`, `getfhandle()`, `getReadResponse()`, `sendReadResponseSingleRange()`, and `sendReadResponsesMultiRanges()`.
- Header helpers: `prepareChecksumQuery()`, `setTransferStatusHeader()`, `addAgeHeader()`, and `addETagHeader()`.
- Security/redirect helper: `appendOpaque()` carries existing opaque parameters and optionally signed HTTP token fields into redirect URLs.
- `reset()` clears request-local state, read range state, digest state, bridge state, body counters, headers, opaque environment, monitoring state, and timing.

## Control Flow

`XrdHttpProtocol::Process()` feeds the first line to `parseFirstLine()` and each header to `parseLine()`. The first line selects `ReqType` and resource. Header parsing records all headers for plugins, handles keepalive, host, Range, validated Content-Length, Destination, digest preference headers, WebDAV depth, `Expect: 100-continue`, trailer support, validated `Transfer-Encoding: chunked`, `X-Transfer-Status`, packet marking `scitag`, user-agent, Origin for CORS, and configured header-to-CGI mappings.

Before method dispatch, `ProcessHTTPReq()` appends `oss.asize` for PUTs with known length and appends configured header-to-CGI opaque parameters once. At `reqstate == 0`, external handlers get first chance through `FindMatchingExtHandler()`.

For `GET`, the request state machine opens the file with `kXR_open` and `kXR_retstat`, optionally performs a checksum query for Want-Digest/Want-Repr-Digest, closes directory handles, performs directory listing, sends GET response headers once, then repeatedly issues `kXR_read` or `kXR_readv` using `XrdHttpReadRangeHandler::NextReadList()`. Completion closes the file. Static `/static/` resources can be served from embedded constants, redirected, or served from preloaded memory.

For `HEAD`, the code stats the path, optionally runs a checksum query, and sends headers without a body. For `PUT`, it opens for write, optionally sends `100 Continue`, then writes fixed-length body bytes or parses chunked request framing and writes each chunk until close, finally sending `201`. `DELETE` stats first to choose `kXR_rmdir` or `kXR_rm`. `PROPFIND` reads an optional small XML body, stats the target, and optionally dirlists depth-one children into a WebDAV multistatus response. `MKCOL` maps to `kXR_mkdir`; `MOVE` validates destination host for manager role and maps to `kXR_mv`; `OPTIONS` returns DAV/Allow headers; `PATCH` and unsupported methods return 501.

Bridge callbacks store response fields and call `PostProcessHTTPReq()`. The post-processor interprets current method and `reqstate`, parses stat strings, extracts file handles, builds checksums and listings, advances read/write counters, sends errors or success responses, and returns `0`, `1`, or `-1` to indicate more bridge work, completion, or connection failure.

## State And Persistence

State is per request object and reset between keepalive requests. Major fields include parsed headers, resource and opaque parameters, request type, body length, keepalive, depth, file handle, file size/flags/modtime/etag, bridge request/response state, I/O vectors valid only during callbacks, string response accumulator, written byte count, digest request/cache state, range handler, chunked-transfer offsets, trailer flags, packet marking scitag, monitoring state, and start time. There is no durable persistence; `resourceplusopaque` is mutated during processing to include internal query parameters.

## Dependencies And Integration Points

This file depends on `XrdHttpReq.hh`, `XrdHttpProtocol.hh`, `XrdHttpTrace.hh`, `XrdHttpExtHandler.hh`, `XrdHttpHeaderUtils`, `XrdHttpUtils`, `XrdHttpStatic`, XRootD bridge/protocol types, packet marking, checksum handler, read range handler, and utility encoding/hash functions. It is tightly coupled to `XrdHttpProtocol` via friend access for bridge, link, buffer, response, config, CORS/static behavior, and security state. It integrates with monitoring through `monState`, `startTime`, and response helper calls in `XrdHttpProtocol`.

## Risks And Edge Cases

- Request parsing is mostly in-place C string manipulation; malformed lines, long tokens, and missing CRLFs are rejected, but maintainers must preserve bounds checks.
- `parseLine()` stores `allheaders[key]` with original header casing; later lookup for header-to-CGI is case-insensitive by iterating config mappings.
- `parseResource()` strips `http://` and `https://` prefixes and collapses double slashes, which is protective but may alter unusual valid paths.
- `appendOpaque()` always appends `?`; URLs already containing query strings rely on prior redirection context to avoid malformed separators.
- PUT chunked parser intentionally ignores trailer headers and caps chunk-size line length, but chunk extensions are only lightly parsed.
- Range handling depends on ordered bridge responses and correct short-read behavior.
- Multipart responses use hardcoded boundary `123456`, which could theoretically collide with payload content.
- Directory listing and PROPFIND build XML/HTML strings in memory; very large listings may grow `stringresp`.
- Several responses pass body length `0` with non-null bodies, relying on `SendSimpleResp()` to calculate length.
- Once a GET body has started, non-trailer clients cannot receive a normal HTTP error; `sendFooterError()` can only return failure unless `X-Transfer-Status` trailers were negotiated.
- `reset()` calls `memset(&xrdresp, 0, sizeof(xrdresp))` after assigning response enums; this is probably harmless for scalar enum storage but visually confusing.
- Security-sensitive header parsing for Content-Length and Transfer-Encoding has explicit smuggling defenses; regressions here are high risk.

## Test Signals

Tests should cover request-line parsing for all methods, invalid leading space, unknown methods, resource decoding/sanitization, duplicate and conflicting Content-Length, `Transfer-Encoding` validation, CL+TE rejection in both orders, Range parsing integration, `Expect: 100-continue`, scitag CGI injection, header2cgi opaque append, Want-Digest and Want-Repr-Digest selection, GET full/single/multi-range headers, 416 behavior, read/readv response formatting, chunked response trailers, PUT fixed-length and chunked uploads, static file serving/redirect/preload, directory GET listing, PROPFIND depth 0/1 XML, DELETE file versus directory, MOVE host enforcement, redirect host CRLF rejection, opaque credential propagation, keepalive reset, and monitoring state reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.cc -->
