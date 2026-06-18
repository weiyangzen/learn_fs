# subset-b-007930 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpReadV.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpReadV.cc

## Purpose

This file implements `XrdClHttp::CurlVectorReadOp`, the HTTP plugin's vector-read operation. It translates an XRootD `ChunkList` into a single HTTP `Range` request containing multiple byte ranges, parses either single-range or `multipart/byteranges` responses, copies returned data into caller-provided buffers, and reports an `XrdCl::VectorReadInfo` to the response handler.

## Important APIs, types, and functions

`CurlVectorReadOp::Setup` installs the libcurl write callback and builds the comma-separated `Range: bytes=start-end,...` header from non-empty chunks. `Fail` adds vector-read offset/length context to errors. `Success` emits any partial final chunk, sets the total size consumed, wraps the `VectorReadInfo` in an `AnyObject`, and invokes the handler. `ReleaseHandle` clears write callback/header/socket options before delegating to `CurlOperation`.

The core parser is `Write`. It handles status `200` as a whole-object response, non-multipart range responses by using `HeaderParser::GetOffset`, and multipart responses by parsing boundary lines and per-part `Content-Range` headers. `CalculateNextBuffer` chooses the requested chunk whose offset best matches the current response part, possibly setting `m_skip_bytes` when the server returns a larger/coalesced range.

State fields inherited from `XrdClHttpOps.hh` include `m_chunk_list`, `m_vr`, `m_current_op`, `m_response_idx`, `m_chunk_buffer_idx`, `m_bytes_consumed`, `m_skip_bytes`, and `m_response_headers`.

## Control flow

The worker calls `Setup`, then libcurl streams body data into `WriteCallback`. `Write` first updates byte statistics, classifies the response shape from parsed headers, then loops through the incoming buffer. If a current response range is active, it skips unwanted bytes, copies useful bytes into the selected `ChunkInfo` buffer, emits completed chunks into `VectorReadInfo`, and advances to the next request or response segment.

At multipart boundaries, `Write` assembles CRLF-delimited lines across callbacks, tolerates blank lines before boundaries, recognizes the terminating boundary, reads MIME-style part headers, and requires a valid `Content-Range` header for each non-final segment. Bad boundaries, malformed headers, missing ranges, negative lengths, or impossible buffer progress call `FailCallback`, which records a callback error for the worker to convert into an XRootD failure.

## State and persistence behavior

There is no durable persistence. Runtime state is per-operation and owns only the `VectorReadInfo`; the actual target buffers remain owned by the XRootD caller through `ChunkInfo` pointers. `m_chunk_list` may grow when a server response covers only part of a requested chunk; the remainder is appended as a new request entry backed by the original buffer pointer plus offset.

## Dependencies and integration points

The file depends on libcurl callbacks through `CurlOperation`, XRootD `ChunkList`, `ChunkInfo`, `VectorReadInfo`, `AnyObject`, and `XRootDStatus`, and on `HeaderParser` for status, multipart separator, and range metadata. It is produced by file/filesystem readv paths and executed by `CurlWorker`.

## Risks and edge cases

The multipart parser is strict: it fails on missing `Content-Range`, invalid boundaries, unsupported range units, out-of-range numeric values, and malformed header lines. The `std::stoll(value.data(), &count)` usage relies on curl-provided CRLF-backed buffers being safely terminated before parse overrun, which is subtle. Status `200` is treated as enough data to satisfy requested chunks from offset zero; sparse reads against servers that ignore multi-range requests can waste data or produce short results depending on response length. Out-of-order, coalesced, and partial ranges are supported, but overlapping or duplicate requested ranges depend on `CalculateNextBuffer` choosing the least-skip match.

## Test signals

The class exposes `SetSeparator`, `SetStatusCode`, and public `Write` for unit testing. Useful tests should cover single full response, single `Content-Range`, multipart responses split across callbacks, out-of-order/coalesced parts, malformed boundaries, missing or invalid `Content-Range`, zero-length requested chunks, and partial responses that append remainder chunks. No focused test file for this class was found in the checkout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpReadV.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpStat.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpStat.cc

## Purpose

This file implements `CurlStatOp`, the HTTP stat/open metadata operation. It can use either `HEAD` or WebDAV `PROPFIND` depending on endpoint capabilities cached from `OPTIONS`, parses object size and directory state, and returns either plain XRootD stat/open responses or extended response-info wrappers.

## Important APIs, types, and functions

`Setup` installs the write callback and chooses `HEAD` or `PROPFIND` using `VerbsCache`. `RequiresOptions` asks the worker to probe endpoints whose allowed verbs are unset. `OptionsDone` reconfigures the in-flight handle after a successful OPTIONS result. `Redirect` preserves headers while redirecting, then decides whether the redirected endpoint needs another OPTIONS lookup. `WriteCallback` stores PROPFIND XML bodies up to 1 MB. `GetStatInfo`, `ParseProp`, and `SuccessImpl` convert HTTP/WebDAV metadata into XRootD response objects.

`Success` calls `SuccessImpl(true)`, while `CurlOpenOp` reuses `SuccessImpl(false)` to avoid returning a stat object when open metadata is only used internally.

## Control flow

For cached PROPFIND support, setup sends `PROPFIND` with `Depth: 0` and enables a body callback; otherwise it sends `HEAD` with `CURLOPT_NOBODY`. If no capability is cached, the worker runs `CurlOptionsOp` first, then calls `OptionsDone` and executes the parent stat operation. On redirect, the operation resets the target through `CurlOperation::Redirect`; if the target has unknown verb support, the worker reinvokes OPTIONS before restarting.

On success, `GetStatInfo` reads `Content-Length` for `HEAD` or parses a WebDAV `D:multistatus/D:response/D:propstat/D:prop` XML body for `getcontentlength` and `resourcetype`. Directories may omit length and are reported as size zero. `SuccessImpl` emits `StatInfo`/`StatResponse` or `OpenResponseInfo` and moves accumulated `ResponseInfo` when requested.

## State and persistence behavior

The only persistent state is indirect: discovered PROPFIND support is stored in the global `VerbsCache`. Per-operation state tracks whether PROPFIND is active, buffered XML, directory flag, parsed length, and the response-info option. `ReleaseHandle` resets curl options so handles can be recycled safely.

## Dependencies and integration points

The implementation depends on TinyXML, `VerbsCache`, `HeaderParser`, `CurlWorker` OPTIONS chaining, and `XrdClHttpResponses.hh` wrappers. It is used by file open/stat, filesystem stat, checksum inheritance, and query operations that derive from `CurlStatOp`.

## Risks and edge cases

PROPFIND response parsing assumes `D:` or `lp1:` prefixed element names and can reject namespace-equivalent XML using different prefixes. `std::stoll` exceptions from bad content length are not caught in `ParseProp`, so malformed XML values could throw through the worker. The cache key is endpoint-level, not path-level, so mixed endpoint behavior can cause suboptimal verb choice. Redirects require careful restoration of pre-redirect headers when an OPTIONS probe must be inserted.

## Test signals

Important tests should exercise HEAD size extraction, PROPFIND directory/file parsing, 1 MB XML body cap, missing size failure for non-directory objects, capability cache miss/hit paths, redirect-to-unknown-endpoint OPTIONS reinvocation, and extended response-info object creation. No dedicated stat tests were found in the checkout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpStat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.cc

## Purpose

This file implements the shared `CurlOperation` base behavior for all HTTP operations. It owns libcurl handle setup/cleanup, header parsing, response-info collection, redirects, adaptive timeout and transfer-rate checks, client certificate setup, connection-broker callouts, fake DNS mappings for preconnected sockets, operation statistics, and generic failure delivery.

## Important APIs, types, and functions

`CalculateExpiry` converts a relative `timespec` timeout to a steady-clock deadline with a 30-second default. The two `CurlOperation` constructors accept relative or absolute header expiry. `Setup` binds common libcurl options, callbacks, URL, X.509 credentials, progress callback, and optional connection callout plumbing. `FinishSetup` applies normal headers or header-callout-generated headers, treating callout `Content-Length` specially as `CURLOPT_INFILESIZE_LARGE`.

`HeaderCallback` and `Header` feed `HeaderParser` and append completed response header maps to `ResponseInfo`. `Redirect` rewrites relative locations, reconfigures TLS client certs, resets parser/timing state, and may create a new connection callout for the redirected target. `HeaderTimeoutExpired`, `OperationTimeoutExpired`, `TransferStalled`, `StatisticsReset`, `SetPaused`, `FailCallback`, and `Fail` provide timeout/error accounting and final response delivery.

The socket callbacks `OpenSocketCallback`, `SockOptCallback`, `CloseSocketCallback`, `WaitSocketCallback`, `StartConnectionCallout`, and `CleanupDnsCache` implement broker-provided connected sockets. Thread-local maps generate fake `169.254.x.y:port` endpoints so curl's `CONNECT_TO` can route a hostname to a broker socket without normal DNS.

## Control flow

Each concrete operation is created with a handler and target URL, then a `CurlWorker` calls `Setup` and `FinishSetup`. As curl receives headers, `HeaderParser` updates status, content metadata, allowed verbs, redirects, digests, and response-info maps. During transfer, `XferInfoCallback` checks header deadline, whole-operation deadline, stall interval, and exponentially weighted average transfer rate; returning non-zero makes curl report an aborted callback, which the worker later converts using `GetError`.

Redirect handling resets per-request state and updates `CURLOPT_URL`; when a connection broker is configured, redirects may create a fresh broker callout and fake DNS mapping. Release resets socket, TLS, header, and connect-to options and releases the easy handle back to the worker.

## State and persistence behavior

There is no disk persistence. Process-wide state includes static stall interval and minimum transfer rate configuration. Thread-local fake-DNS maps and refcounts persist across operations in a worker thread until entries are unused and older than one minute. Each operation stores response headers, error code, callback error, curl error buffer, timeout timestamps, bytes since last statistics reset, pause duration, callout state, and the owned easy handle while active.

## Dependencies and integration points

The file depends on libcurl, XRootD status/response/log/default environment APIs, `XrdCl::URL`, POSIX sockets, `getrandom` or `arc4random`, and local connection/header callout interfaces. It is the base layer consumed by all operation-specific `.cc` files and by `CurlWorker` in `XrdClHttpUtil.cc`.

## Risks and edge cases

The fake DNS mechanism is intentionally intricate: refcount and reverse-map bugs could leak entries or close valid sockets. Some callback paths throw or call `Fail` after partial curl setup, so worker cleanup must avoid double-freeing handles. Header-callout `Content-Length` parsing uses `stoull` without local error handling. Adaptive slow-transfer failures depend on the configured minimum rate and stall interval and can abort slow but healthy transfers. Redirect state must keep response-info from prior responses while resetting parser state for the next request.

## Test signals

High-value tests should cover header parsing into response-info, redirect URL rewriting including relative locations, callback failures, timeout classifications, pause-duration accounting, slow-transfer thresholds, connection callout success/failure/timeout, fake DNS cleanup, and handle release reset behavior. Runtime worker metrics and adjacent operation tests are the main current signals; no focused base-operation unit tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.hh

## Purpose

This header defines the HTTP operation class hierarchy used by the XRootD HTTP client plugin. It declares the abstract `CurlOperation` contract and concrete operation classes for OPTIONS, stat/open/checksum/delete/mkdir/query/read/prefetch/vector-read/page-read/listdir/copy/put.

## Important APIs, types, and functions

`CurlOperation` exposes operation lifecycle (`Setup`, `FinishSetup`, `Success`, `Fail`, `ReleaseHandle`), verb identity (`HttpVerb`, `GetVerb`, `GetVerbString`), timeout checks, redirect handling, connection callout hooks, continuation queue hooks, response-info movement, curl handle access, statistics reset, and static tunables for stall timeout and slow transfer rate.

Derived classes model protocol operations: `CurlOptionsOp` probes allowed verbs and resumes a parent operation; `CurlStatOp` implements HEAD/PROPFIND stat; `CurlOpenOp` adds file-open side effects; `CurlChecksumOp` reads checksum headers; `CurlDeleteOp` and `CurlMkcolOp` mutate objects; `CurlQueryOp` returns query buffers; `CurlReadOp`, `CurlPrefetchOpenOp`, and `CurlPgReadOp` implement normal reads and prefetch/page-read variants; `CurlVectorReadOp` implements multi-range reads; `CurlListdirOp` parses WebDAV listings; `CurlCopyOp` implements third-party copy over HTTP COPY; `CurlPutOp` streams uploads with pause/continue support.

## Control flow

The header establishes the worker contract: operations are queued, configured with curl handles by `CurlWorker`, optionally paused/continued through `HandlerQueue`, and completed by invoking a response handler exactly once. Operations needing endpoint capability discovery return `RequiresOptions()`, causing the worker to execute a `CurlOptionsOp` before the original operation. Redirects return `Fail`, `Reinvoke`, or `ReinvokeAfterAllow` so the worker can restart immediately or probe allowed verbs at the new endpoint.

## State and persistence behavior

State is per-operation and in-memory. `CurlOperation` owns the easy handle while running, header parser, response-info object, curl header list, timeout and transfer counters, broker callout object, fake DNS curl resolve list, and handler pointer. Derived classes add operation-specific buffers and references to caller-owned buffers or file objects. No class in this header persists data to disk.

## Dependencies and integration points

The header depends on local connection/header callout APIs, response-info APIs, checksum utilities, XRootD buffer/response types, `curl/curl.h`, and the worker/queue abstractions. It is the main integration surface between `XrdClHttpFile`, `XrdClHttpFilesystem`, `XrdClHttpFactory`, and the operation implementation files.

## Risks and edge cases

Most classes own or reference resources with different lifetimes: handler pointers, caller buffers, curl handles, `File` objects, shared queues, and response-info wrappers. New operation implementations must release curl options for handle recycling and must not call handler callbacks twice. Derived classes that pause transfers must handle race conditions where a worker has already failed an operation before a continuation arrives.

## Test signals

The public methods intended for tests include vector-read separator/status injection, static timeout/rate setters, monitoring JSON, and factory/header timeout paths. Compile-time coverage through all operation `.cc` files is important because this header coordinates many cross-file virtual methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.cc

## Purpose

This file implements the singleton lifecycle and expiry behavior for `VerbsCache`, the endpoint capability cache used to remember whether an HTTP endpoint supports WebDAV `PROPFIND`.

## Important APIs, types, and functions

Static storage is defined for `VerbsCache::g_cache`, `m_expiry_launch`, `m_shutdown_lock`, `m_shutdown_requested_cv`, `m_shutdown_requested`, `m_expire_tid`, and the shutdown trigger. `Instance` starts the background expiry thread exactly once unless shutdown is already underway. `ExpireThread` wakes every 30 seconds until shutdown and calls `g_cache.Expire`. `Expire` removes expired map entries. `Shutdown` sets the shutdown flag, notifies the expiry thread, and joins it if needed.

## Control flow

First use of `VerbsCache::Instance` launches `ExpireThread` with `std::call_once`. Consumers call header/OPTIONS paths to `Put` and `Get` entries defined inline in the header. At plugin/library shutdown, static `shutdown_s` invokes `Shutdown`, causing the worker thread to exit cleanly before static storage disappears.

## State and persistence behavior

All state is process-local and volatile. Known positive entries live for six hours, negative/unknown entries for fifteen minutes, and the background thread prunes expired entries. No endpoint capability information is persisted across process restarts.

## Dependencies and integration points

This implementation depends on C++ threading primitives and `curl/curl.h` inclusion. It is integrated by `CurlStatOp` and `CurlWorker` OPTIONS handling. Its shutdown timing matters because the HTTP plugin can be loaded and unloaded dynamically.

## Risks and edge cases

`Instance` returns `g_cache` even during shutdown, but suppresses launching a new expiry thread. Long-running users that call after shutdown could see stale entries without maintenance. Expiration is periodic and opportunistic; expired entries are also treated as misses by `Get`, so delayed cleanup should not affect correctness. Static destructor ordering remains a classic plugin-unload risk.

## Test signals

Tests should cover first-use thread launch, `Expire` removing stale entries, shutdown join behavior, and that `Instance` does not relaunch the thread after shutdown. No direct tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.hh

## Purpose

This header defines `XrdClHttp::VerbsCache`, a thread-safe process-wide cache mapping URL authorities to discovered HTTP verb capabilities, currently focused on whether `PROPFIND` is available.

## Important APIs, types, and functions

`HttpVerb` is a bitmask enum with `kUnset`, `kUnknown`, and `kPROPFIND`. `HttpVerbs` wraps bit operations and `IsSet`. `Put` normalizes a URL to an authority key, sets positive entries for six hours and unknown entries for fifteen minutes, and avoids overwriting known entries with unknown results. `Get` returns cached verbs when present and unexpired while counting hit/miss atomics. `GetUrlKey` extracts `scheme://authority`, stripping user-info if present. `Expire`, `Instance`, `ExpireThread`, and `Shutdown` are implemented in the `.cc`.

## Control flow

Stat operations call `Get` before choosing HEAD versus PROPFIND. If the result is unset, the worker inserts an OPTIONS operation. `HeaderParser` parses `Allow` headers into `HttpVerbs`, and `CurlOptionsOp` stores them with `Put`. Redirects repeat this process for the redirected authority.

## State and persistence behavior

`m_verbs_map` is guarded by a `shared_mutex`, hit/miss counts are atomic, and cache entries expire based on steady-clock deadlines. The key deliberately ignores path and query; capabilities are assumed authority-wide. State is not durable.

## Dependencies and integration points

The cache is included by operation, utility, and factory code. It uses heterogeneous lookup for `std::string`/`std::string_view` on C++20 and falls back to allocating a string on older standards.

## Risks and edge cases

Authority-level caching can be wrong for servers that vary WebDAV support by path. `GetUrlKey` returns an empty view for malformed URLs, so malformed inputs can collide in the cache if stored. The `GetVerbString` switch has no fallback return outside enum cases, which can warn or become undefined for invalid enum values. User-info stripping changes the key, which is desired for credentials but means two credentialed URLs share one capability entry.

## Test signals

Useful tests include key extraction with credentials, ports, no path, malformed URLs, positive versus unknown overwrite rules, expiration, hit/miss counters, and C++ standard-specific heterogeneous lookup behavior. No dedicated tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOptionsCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.cc

## Purpose

This file implements parsing and formatting of HTTP plugin timeout durations. It accepts a Go-like sequence of numeric values with units and converts them to `timespec`, then marshals `timespec` values back into seconds plus milliseconds.

## Important APIs, types, and functions

`ParseTimeout` recognizes `ns`, `us`, `ms`, `s`, `m`, and `h`, rejects empty strings, negative values, missing units, unknown units, invalid numbers, and out-of-range `stod` values. It treats exact `"0"` as `{0,0}`. `MarshalDuration` emits `"0s"` for zero and otherwise writes `<sec>s<ms>ms`, truncating nanoseconds to milliseconds.

## Control flow

Parsing repeatedly calls `std::stod` on the remaining string, extracts up to two non-digit unit characters, adds scaled seconds/nanoseconds to an accumulator, normalizes nanoseconds over one billion, and advances by the unit length. Errors set `errmsg` and return false.

## State and persistence behavior

The functions are stateless and deterministic except for floating-point rounding/truncation during unit conversion. They do not persist configuration; callers store the parsed values in factory/file static settings.

## Dependencies and integration points

The parser is used by HTTP factory and file configuration paths for settings such as stall timeout, minimum client timeout, and default header timeout. It depends only on standard C/C++ string/time facilities.

## Risks and edge cases

Decimal nanoseconds/microseconds can be truncated by assignment to integer `tv_nsec`. The normalization uses `>` rather than `>=`, so exactly `1,000,000,000` nanoseconds is not normalized until more nanoseconds are added. Unit extraction looks at two non-digit characters, so unexpected alphabetic suffixes produce unknown-unit errors. `MarshalDuration` loses sub-millisecond precision.

## Test signals

Tests should cover valid compound durations (`1h5m`, `30ms`, decimals), `"0"`, missing units, empty input, negative values, unknown units, exact nanosecond normalization boundaries, and marshal precision truncation. No direct tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.hh

## Purpose

This header declares the timeout duration parser and formatter used by the XrdCl HTTP plugin configuration layer.

## Important APIs, types, and functions

`ParseTimeout(const std::string&, struct timespec&, std::string&)` returns a success flag and writes a diagnostic error message on invalid input. `MarshalDuration(const struct timespec&)` returns a Go-style duration string with seconds and milliseconds.

## Control flow

Callers pass configuration strings into `ParseTimeout` before updating static timeout settings. On false, they log `errmsg` and typically keep defaults. `MarshalDuration` is used for converting a stored `timespec` back to display/config text.

## State and persistence behavior

The header declares stateless functions only. Parsed state belongs to callers.

## Dependencies and integration points

It includes `<time.h>` for `timespec` and `<string>`. `XrdClHttpFactory.cc` and `XrdClHttpFile.cc` include it for environment/property parsing.

## Risks and edge cases

Consumers must handle a false parse and should not assume `result` was changed meaningfully on failure. The documented format excludes the UTF-8 microsecond symbol even though Go accepts it.

## Test signals

Compile coverage is broad because factory/file code includes this header. Behavioral tests should target the `.cc` parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponseInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponseInfo.hh

## Purpose

This header defines `XrdClHttp::ResponseInfo`, the opt-in container for raw HTTP response headers collected during an operation, including redirects.

## Important APIs, types, and functions

`HeaderValues` is a vector of values for repeated headers. `HeaderMap` maps canonical, case-sensitive header names to value lists. `HeaderResponses` is a vector of header maps, one per HTTP response observed by the operation. `AddResponse` appends a completed header map, and `GetHeaderResponse` returns the collected responses by const reference.

## Control flow

`CurlOperation::Header` creates a `ResponseInfo` lazily when the first header block finishes and pushes the parser's header map. Operation-specific response wrappers then move the `ResponseInfo` into returned XRootD response objects when the `XrdClResponseInfo` property is enabled.

## State and persistence behavior

State is per response object and memory-only. Header key lookup is intentionally case-sensitive after local canonicalization, so callers must use the canonical header spelling documented by the header.

## Dependencies and integration points

This is consumed by connection callouts, header response wrappers, `CurlOperation`, and users of the public response-info property. It is small but ABI-sensitive because it is exposed to plugin consumers.

## Risks and edge cases

The container preserves multiple response blocks but does not label which block is a redirect versus final response except by order. It stores all headers accepted by `HeaderParser`, which may exclude malformed headers. Consumers must use canonical header keys or miss values.

## Test signals

Tests should verify repeated header storage, redirect header ordering, canonical key expectations, and movement into derived response objects. No direct tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponseInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponses.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponses.hh

## Purpose

This public header defines response wrapper classes that carry `ResponseInfo` alongside normal XRootD response payloads when the file or filesystem property `XrdClResponseInfo` is set to `"true"`.

## Important APIs, types, and functions

`ResponseInfoProperty` names the opt-in property. `DirectoryListResponse`, `StatResponse`, `QueryResponse`, `OpenResponseInfo`, `DeleteResponseInfo`, `MkdirResponseInfo`, and `ReadResponseInfo` each store a `std::unique_ptr<ResponseInfo>` and expose `GetResponseInfo`/`SetResponseInfo`. Some derive from existing XRootD response classes (`DirectoryList`, `StatInfo`, `Buffer`, `ChunkInfo`); open/delete/mkdir use standalone virtual classes.

## Control flow

Operation success paths decide whether to allocate a wrapper based on `SendResponseInfo()`. They move the operation's accumulated `ResponseInfo` into the wrapper and return it in `AnyObject`. Callers that opt in are responsible for extracting the derived response type and consuming the response-info pointer.

## State and persistence behavior

Response-info state is transferred by move and is not durable. The comment notes that not all XRootD base response classes have virtual destructors; if objects are deleted through base pointers without extracting response-info, memory can leak.

## Dependencies and integration points

The header depends on XRootD response classes and `XrdClHttpResponseInfo.hh`. It is used by stat, listdir, query, open, delete, mkdir, checksum, and read paths.

## Risks and edge cases

The opt-in contract is subtle: callers must know when a returned object is a derived wrapper and must release embedded response info. ABI compatibility matters because this is public plugin-facing API. Mixed use of base and derived response objects can cause casts to fail if the property was not set.

## Test signals

Tests should cover every response wrapper type, property-enabled and property-disabled paths, ownership transfer from `GetResponseInfo`, and safe deletion/extraction behavior. No direct tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponses.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.cc

## Purpose

This file implements the HTTP plugin's utility and runtime engine layer: HTTP-to-XRootD error mapping, header parsing, checksum digest parsing, curl handle defaults, a pollable bounded operation queue, thread-local curl handle recycling, multi-curl worker threads, continuation queues, OPTIONS chaining, redirect handling, broker socket waiting, monitoring metrics, and global curl initialization/shutdown.

## Important APIs, types, and functions

Status helpers are `HTTPStatusIsError`, `HTTPStatusConvert`, and local `CurlCodeConvert`. `HeaderParser` implements `Parse`, `Canonicalize`, `ParseDigest`, `Base64Decode`, and `ChecksumTypeToDigestName`, recording content length/range, multipart boundaries, allowed verbs, location, ETag, cache-control, and digest checksums. `GetHandle` creates a curl easy handle with user agent, optional verbose header dump, CA file/dir from XRootD env or X509 env vars, and 32 KiB buffer size.

`HandlerQueue` implements `Produce`, `Consume`, `TryConsume`, `Expire`, `GetHandle`, `RecycleHandle`, `ReleaseHandles`, `Shutdown`, and `GetMonitoringJson`. It uses a pipe as a pollable readiness FD and condition variables for bounded producers/consumers.

`CurlWorker` implements constructor setup, `Run`, `RunStatic`, `Start`, `Shutdown`, `ShutdownAll`, `ClientX509CertKeyFile`, `OpRecord`, and `GetMonitoringJson`. Static `initcontrol` calls `curl_global_init` and later shuts workers down and calls `curl_global_cleanup`.

## Control flow

Clients produce `CurlOperation` objects into the shared queue. Worker threads consume operations up to `m_max_ops`, allocate/reuse easy handles, call operation setup, optionally inject an OPTIONS operation when `RequiresOptions()` is true, and add handles to a curl multi handle. The loop polls the shared queue FD, continuation queue FD, shutdown pipe, broker FDs, and curl's own wait set at short intervals.

Completed curl messages are classified. HTTP error statuses map through `HTTPStatusConvert` and fail the operation. Successful OPTIONS operations update cache and start their parent. Successful redirects call the operation's `Redirect`, possibly starting another OPTIONS probe for unknown target capabilities. Callback-aborted transfers are mapped from `CurlOperation::OpError` to header timeout, operation timeout, slow transfer, client/server stall, or callback error. Ordinary curl errors map through `CurlCodeConvert`, with `CURLE_COULDNT_CONNECT` able to trigger one broker retry when a connection callout exists.

## State and persistence behavior

All state is process-local. `HandlerQueue` tracks operation counters and thread-local easy handles. `CurlWorker` tracks static worker list, per-verb/status metrics, connection-callout counters, and per-worker liveness timestamps. No data is persisted to disk, but `GetMonitoringJson` is intended for the factory's monitoring output path.

## Dependencies and integration points

The file integrates libcurl multi, OpenSSL BIO/EVP for digest decoding, XRootD environment/log/status/response APIs, XRootD protocol error codes, local `CurlOperation`, `VerbsCache`, `File`, and worker headers, POSIX pipes/fcntl/read/write/syscall, and optional dump logging with authorization redaction. It is central to every HTTP operation.

## Risks and edge cases

This is concurrency- and lifetime-heavy code. Queue pipe bytes must stay synchronized with deque entries, expired operations are failed after unlocking to avoid callback reentrancy deadlocks, and continuation races are explicitly handled when operations have already completed. Worker handle accounting around OPTIONS parents, redirects, broker waits, and failures is complex and can leak or double-count handles if changed carelessly. `HeaderParser::ParseDigest` has to support both standard and legacy base64 CRC32C forms. Header canonicalization rejects invalid bytes, which is good for safety but can abort on unusual server behavior.

## Test signals

Important tests should cover status and curl error mappings, header canonicalization, content-range and multipart detection, digest parsing for MD5/CRC32C, queue backpressure/expiry/shutdown, handle recycling, worker OPTIONS chaining, redirect behavior, broker wait success/failure/timeout, continuation after pause, monitoring JSON, and global shutdown. This checkout does not contain focused XrdClHttp unit tests; integration/build coverage is the main visible signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.hh

## Purpose

This header declares shared utilities for the HTTP client plugin: status conversion helpers, string trimming, curl handle construction, header parsing, the pollable operation queue, and monitoring/handle lifecycle hooks.

## Important APIs, types, and functions

Top-level utilities include `kLogXrdClHttp`, `HTTPStatusIsError`, `HTTPStatusConvert`, `ltrim_view`, `trim_view`, and `GetHandle`. `HeaderParser` exposes parsed response metadata and static helpers for canonicalization, digest parsing, base64 decode, and checksum digest names. `HandlerQueue` exposes bounded producer/consumer operations, poll FD access, easy-handle recycling, expiry, shutdown, handle cleanup, and monitoring JSON.

## Control flow

Concrete operations rely on `HeaderParser` through the base `CurlOperation` header callback. Factory and worker code rely on `HandlerQueue` as the bridge between XRootD API threads and curl worker threads; the queue can be polled by curl's event loop while still offering blocking condition-variable behavior to producers/consumers.

## State and persistence behavior

`HeaderParser` is per-operation state. `HandlerQueue` owns an in-memory deque, pipe FDs, thread-local curl-handle cache, and static counters. There is no durable persistence.

## Dependencies and integration points

The header includes checksum, options-cache, and response-info headers and forward-declares curl and XRootD classes. It is included by operation implementations, factory/filesystem/file code, and worker code.

## Risks and edge cases

`HeaderParser::MoveHeaders` is destructive and should only be called after `HeadersDone()`. `HandlerQueue::Produce` can fail an operation if it waits in a full queue past the operation expiry. Consumers must call `Shutdown` and `ReleaseHandles` during plugin unload to avoid leaving curl handles or FDs live.

## Test signals

Compile coverage should catch most declaration drift. Behavioral tests should target parser metadata, queue poll-FD synchronization, queue expiry, and monitoring counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpWorker.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpWorker.hh

## Purpose

This header declares `XrdClHttp::CurlWorker`, the worker-thread object that drives libcurl multi handles for queued HTTP operations.

## Important APIs, types, and functions

Public methods include the constructor, deleted copy constructor, `Run`, static `RunStatic`, `Start`, `ClientX509CertKeyFile`, `SetMaintenancePeriod`, and static `GetMonitoringJson`. Private lifecycle methods are `ShutdownAll` and `Shutdown`. `OpStats` tracks per-verb/status counts and durations; `OpKind` classifies metric updates; `OpRecord` records operation statistics.

Static members maintain the global worker list, worker mutex, maintenance period, connection-callout counters, per-verb/status metric array, and vectors pointing to per-worker liveness atomics. Each instance owns the shared queue, continuation queue, active curl operation map, shutdown pipe, startup synchronization, thread object, logger, X.509 credential filenames, and metric offsets.

## Control flow

`XrdClHttpFactory` constructs workers and starts `RunStatic` in threads. `Start` transfers ownership into the static worker list and releases `RunStatic` once the thread object is known. `Run` consumes queued operations, manages curl multi state, and exits on shutdown. Static `initcontrol` handles global curl initialization and all-worker shutdown on plugin unload.

## State and persistence behavior

All state is process-local. Metrics live in static atomics for monitoring and are not persisted unless factory monitoring writes them elsewhere. The worker stores X.509 client cert/key paths read at construction so operations can configure curl handles without rereading environment each time.

## Dependencies and integration points

The header depends on `XrdClHttpOps.hh`, atomics, chrono, mutexes, condition variables, unordered maps, and forward-declared curl/XRootD classes. It is implemented in `XrdClHttpUtil.cc` and constructed by `XrdClHttpFactory.cc`.

## Risks and edge cases

The static worker list owns live worker objects and is also used during shutdown, so lock ordering and thread joins matter. `m_op_map` ties raw curl handles to shared operations and timestamps; any worker change must preserve handle removal/recycling invariants. `m_max_ops` is fixed at 20 per worker while queue size is configurable, which affects backpressure behavior.

## Test signals

Tests should cover startup synchronization, shutdown before/after launch, maintenance-period overrides, monitoring JSON while workers are active, and X.509 cert/key propagation to operations. No direct worker tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpWorker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdClS3/CMakeLists.txt

## Purpose

This CMake file builds and installs the XRootD S3 client plugin. It conditionally enables the plugin based on libcurl availability and packages S3 file/filesystem/factory/download code into a versioned module.

## Important APIs, types, and functions

The script calls `find_package(CURL REQUIRED)` when `FORCE_ENABLED` is set and optional `find_package(CURL)` otherwise. If curl is unavailable, it returns early. It builds `XrdClS3Obj` as an object library from the S3 source/header set, links it privately with `XrdCl`, `XrdUtils`, `XrdXml`, `CURL::libcurl`, `OpenSSL::Crypto`, and `Threads::Threads`, forces PIC, then links a module library named `XrdClS3-${PLUGIN_VERSION}`.

On non-Apple platforms it applies the `configs/export-lib-symbols` version script and installs the module into `${CMAKE_INSTALL_LIBDIR}`.

## Control flow

The top-level source CMake adds this directory. If curl is found, object compilation and module creation proceed; otherwise the directory contributes no target. The module uses XRootD's plugin entry point exported by the factory implementation.

## State and persistence behavior

The file has no runtime state. Build outputs are the object library and installed plugin module.

## Dependencies and integration points

It depends on CMake targets for XRootD, libcurl, OpenSSL crypto, XML utilities, and threads. It includes the download handler, factory, file, and filesystem components, so build failures here catch cross-file API drift.

## Risks and edge cases

Optional curl discovery means S3 support can silently disappear unless `FORCE_ENABLED` is used. The version script is skipped on Apple, so exported symbol behavior differs by platform. Any new S3 source file must be added to `XrdClS3Obj`.

## Test signals

The primary signal is configuring/building with and without curl, with `FORCE_ENABLED` both true and false, plus install layout verification for the versioned module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.cc -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.cc

## Purpose

This file implements `XrdClS3::DownloadUrl`, a helper that downloads an HTTP/S3-backed object completely into an `XrdCl::Buffer` using the existing HTTP file plugin. It is used by S3 filesystem operations that need full XML/listing/stat-like responses.

## Important APIs, types, and functions

The anonymous `S3DownloadHandler` owns an opened `XrdCl::File`, caller handler, cumulative buffer, and expiry time. Its nested `ReadHandler` handles each async read result and schedules the next read. Its nested `CloseHandler` reports either a read error, close error, or final buffer. `GetTimeout` returns remaining seconds and whether the deadline is still valid. `DownloadUrl` creates an `XrdCl::File`, forces plugin object creation with an initial `Open(... Compress ...)`, sets HTTP header callout and full-download properties, then performs the real async read open with `S3DownloadHandler`.

## Control flow

On open success, `S3DownloadHandler::HandleResponse` starts a read at offset zero for 32 KiB. Each `ReadHandler` checks remaining time, closes and reports on read error, validates `ChunkInfo`, treats a zero-length chunk as EOF, shrinks the buffer to used size, closes the file, and finally returns the buffer. Non-zero chunks advance the cursor, grow the buffer by another 32 KiB, and issue the next read at the current cursor offset.

`CloseHandler` prefers the original read error over close status. On successful close after EOF, it wraps the owned buffer in an `AnyObject` with ownership transfer and calls the original handler.

## State and persistence behavior

State is transient and heap-owned through self-owning response handlers. The cumulative buffer grows to the full object size in memory. No data is persisted to disk. The helper stores a raw header-callout pointer in an HTTP file property as a hexadecimal integer string so the underlying HTTP plugin can invoke S3 signing.

## Dependencies and integration points

The implementation depends on `XrdCl::File`, `XrdCl::Buffer`, response handlers, default request timeout, XRootD open/read/close APIs, and HTTP plugin properties `XrdClHttpHeaderCallout` and `XrdClHttpFullDownload`. It integrates with `XrdClS3Filesystem.cc` listing/stat flows.

## Risks and edge cases

Full downloads can consume large memory because the buffer grows until EOF with no explicit cap. The first dummy open is a hack to force plugin object creation before setting properties; changes in XRootD plugin creation behavior could break this assumption. Timeout is checked between async callbacks, not during an individual HTTP read. The pointer-to-string callout bridge requires the referenced callout object to outlive the HTTP operation.

## Test signals

Tests should cover open failure, timeout before read, read error followed by close, missing `ChunkInfo`, zero-length EOF, close failure, multi-chunk accumulation, header-callout property propagation, and large object memory behavior. No direct tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.hh

## Purpose

This header declares the S3 full-download helper used by the S3 filesystem layer.

## Important APIs, types, and functions

`XrdClS3::DownloadUrl(const std::string &url, XrdClHttp::HeaderCallout *header_callout, XrdCl::ResponseHandler *handler, time_t timeout)` starts an asynchronous full-object download and returns the immediate XRootD status from initiating the open/read chain.

## Control flow

Callers pass an already generated HTTPS URL and optional S3 signing header callout. The implementation opens the URL through the HTTP plugin and eventually calls the supplied response handler with either an error status or an owned `XrdCl::Buffer`.

## State and persistence behavior

The header owns no state. Runtime state is in the implementation's response handlers.

## Dependencies and integration points

It includes `XrdClS3Filesystem.hh` for `XrdClHttp::HeaderCallout` visibility and XRootD response headers. It is used by S3 filesystem stat/listing helpers.

## Risks and edge cases

The declaration exposes a raw `HeaderCallout *`; lifetime is the caller's responsibility. The API returns only initiation status, while final success/failure is asynchronous through `handler`.

## Test signals

Compile coverage verifies the S3 filesystem integration. Behavioral tests should target the `.cc` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.cc -->
# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.cc

## Purpose

This file implements the S3 XRootD plugin factory and the shared S3 URL/signing utilities. It initializes S3 configuration from XRootD environment keys, creates S3 file/filesystem plugin objects, converts `s3://` URLs to HTTPS endpoints, loads and caches bucket credentials, and generates AWS Signature V4 authorization headers.

## Important APIs, types, and functions

The factory exports `XrdClGetPlugIn` and implements `CreateFile`/`CreateFileSystem`. `InitS3Config` reads defaults and environment imports for endpoint, URL style, region, mkdir sentinel, default credential file locations, and per-bucket credential configs. `GenerateHttpUrl` maps S3 URLs into path-style or virtual-hosted-style HTTPS URLs and strips internal `authz` query parameters via `CleanObjectName`. `ExtractHostname`, `GetBucketFromHttpsUrl`, `PathEncode`, `CanonicalizeQueryString`, `TrimView`, and local `AmazonURLEncode` support URL canonicalization.

`GenerateV4Signature` loads credentials with `GetCredentialsForBucket`, adds required `Host`, `X-Amz-Date`, and `X-Amz-Content-Sha256` headers, builds canonical request and string-to-sign, derives the AWS4 HMAC key chain using OpenSSL HMAC/SHA256, and returns the `Authorization` header value. `ReadShortFile` and `FullRead` read credential files up to 32 KiB. Static testing/config setters live in the header.

## Control flow

The constructor runs initialization once, obtains the default log/env, sets topic name, and marks the factory initialized. File/filesystem creation returns null if initialization failed. Header callouts in S3 file/filesystem code call `GenerateV4Signature` for each HTTP request. If credentials are missing or configured as public, the auth token is empty and no signing is needed. Credential reads are cached per bucket for one minute on success/public access and ten seconds on failures.

URL generation handles several modes: if no global endpoint is configured or the URL bucket matches the endpoint, the endpoint is taken from the URL authority and the real bucket is parsed from the path; otherwise endpoint/region/url-style settings determine the HTTPS authority and path.

## State and persistence behavior

Static process-wide state includes initialization flags, log pointer, endpoint/service/region/url-style, mkdir sentinel, default credential locations, per-bucket credential locations, and a credential-value cache protected by `m_bucket_auth_map_mutex`. Secrets are read from files and kept in memory briefly. Nothing is persisted by this code.

## Dependencies and integration points

The file depends on OpenSSL EVP/HMAC for SHA256/HMAC, XRootD plugin factory/log/env APIs, POSIX file reads, and S3 file/filesystem classes. It integrates with the HTTP plugin through S3 header callouts that add SigV4 headers to HTTP operations.

## Risks and edge cases

SigV4 canonicalization is security-sensitive. The code computes `value_trimmed` and compresses spaces but then stores the original `value` in `transformed_headers`, so canonical headers may not use the normalized value intended by the comments. Query canonicalization skips empty values in some paths, which may differ from AWS rules for empty-valued parameters. Virtual-host URL generation with an empty region constructs `bucket..endpoint`. Credential cache entries store secret material in memory and use short TTLs but no explicit zeroization. `TrimView` can index an empty view if called with all whitespace because it uses the original input size while indexing the trimmed view.

## Test signals

High-value tests should cover path and virtual URL generation, endpoint-in-URL mode, `authz` stripping while preserving other query parameters, bucket extraction, path/query canonicalization, public buckets, missing/mismatched credential files, credential cache TTL and reset, SigV4 known test vectors, header normalization, empty/all-whitespace trim inputs, and plugin initialization without env/log. No dedicated S3 factory tests were found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.cc -->
