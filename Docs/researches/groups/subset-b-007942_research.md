# subset-b-007942 research

Grouped research for the XRootD HTTP, CORS, HTTP third-party-copy, and Macaroons files listed in `subset-b-007942`. Each file section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.hh

Purpose: Declares `XrdHttpReq`, the main HTTP/WebDAV request object used by `XrdHttpProtocol` to parse HTTP input, hold request metadata, drive XRootD bridge operations, and translate asynchronous bridge callbacks into HTTP responses.

Important APIs/types/functions: `ReqType` enumerates supported verbs and is explicitly tied to monitoring verb counter order. The class inherits `XrdXrootd::Bridge::Result` and overrides `Data`, `Done`, `Error`, `File`, and `Redir`. Public parser and execution entry points are `parseFirstLine`, `parseLine`, `parseBody`, `ProcessHTTPReq`, `ReqReadV`, multipart header builders, `appendOpaque`, `addCgi`, and transfer-status helpers. Request state includes resource strings, opaque env, headers, host/destination, digest maps, checksum handler pointers, range handling, xrootd request/response fields, file metadata, monitoring state, scitag, and chunk/trailer flags.

Control flow: Header/body parsing populates the fast-access fields, then `ProcessHTTPReq` issues xrootd bridge operations according to `reqstate`. Bridge callbacks place response data into `iovP/iovN/iovL/final`, map errors and redirects, and call post-processing helpers. GET handling is split between open/stat header emission, directory listing post-processing, single-range/multipart response streaming, footer error handling, and optional digest/checksum headers. PUT and write flows use `length`, `writtenbytes`, `m_appended_asize`, and opaque construction to coordinate with the bridge.

State and persistence: The class is per-request but long-lived across asynchronous callbacks. It persists current HTTP status, first emitted status, request headers, opaque values, file handle bytes, chunk offsets, checksum results, and monitoring timestamps until `reset()` or destruction. No durable storage is owned here; persistence is in the backend xrootd/SFS layer.

Dependencies and integration points: Integrates `XProtocol`, `XrdXrootdBridge`, `XrdOucEnv/String`, checksum and range handlers, `XrdHttpProtocol`, and `XrdHttpMonState`. `appendOpaque` and `addCgi` connect HTTP metadata to xrootd opaque arguments. `ReqType` and `monState` feed monitoring.

Risks: This header exposes many mutable public fields, so state-machine invariants are distributed across implementation files. Header parsing must enforce RFC `Content-Length` rules and avoid duplicate/ambiguous length handling. Any change to `ReqType` must be synchronized with monitoring schemas. Late I/O errors after response start rely on trailers/footers and can otherwise be hard to report correctly.

Test signals: Exercise malformed headers, duplicate content lengths, all supported verbs, single and multipart ranges, directory listings, chunked/trailer status, redirects, checksum/digest negotiation, bridge error mappings, and keepalive reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecXtractor.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecXtractor.hh

Purpose: Defines the HTTP security extractor plugin ABI used to populate `XrdSecEntity` from TLS links, commonly for VOMS or certificate-derived attributes.

Important APIs/types/functions: `XrdHttpSecXtractor` is an abstract base with required `GetSecData(XrdLink *, XrdSecEntity &, SSL *)` and `Init(SSL_CTX *, int)`. Optional `InitSSL` and `FreeSSL` default to failure. The C plugin entry point is `XrdHttpGetSecXtractor(XrdHttpSecXtractorArgs)`, with arguments carrying an error destination, config filename, and namelib parameters.

Control flow: `XrdHttpProtocol::InitSecurity` loads an implementation, calls `Init` with the process TLS context and trace mask, and later authentication calls `GetSecData` per TLS connection.

State and persistence: The interface does not prescribe state. Implementations may keep process-wide config after `Init` and per-SSL state via `InitSSL`/`FreeSSL`.

Dependencies and integration points: Depends on OpenSSL `SSL`/`SSL_CTX`, `XrdLink`, `XrdSecEntity`, and `XrdSysError`. The version-info guidance recommends declaring an XRootD version symbol for ABI compatibility.

Risks: ABI compatibility is sensitive because this is a dynamically loaded plugin interface. Required extractors can reject otherwise valid TLS authentication if VOMS extraction fails. Implementations must be thread-safe at creation and careful with ownership of `XrdSecEntity` strings.

Test signals: Load a minimal extractor, verify `Init` is called, validate successful and failing `GetSecData`, and test required-extractor behavior during TLS client-cert authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecXtractor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecurity.cc -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecurity.cc

Purpose: Implements HTTP TLS security initialization and client-certificate authentication for `XrdHttpProtocol`, including grid-map lookup and optional security extractor integration.

Important APIs/types/functions: `InitSecurity` initializes the ssl crypto factory, grid-map service, and optional sec extractor. `HandleAuthentication` validates the OpenSSL peer result, parses the peer certificate chain, stores the DN in `SecEntity.moninfo`, invokes VOMS extraction, and delegates name mapping. `HandleGridMap` maps certificate DN to a local user or fallback name. `GetVOMSData` calls the extractor and preserves gridmap-derived names when needed.

Control flow: Initialization obtains `XrdCryptoFactory::GetCryptoFactory("ssl")`, loads `XrdOucGMap` if `gridmap` is configured, and initializes the extractor with `xrdctx->Context()`. During authentication, OpenSSL verification failure returns an error. Missing peer cert returns success with no identity. A valid chain yields DN and hash, VOMS data extraction, optional required-extractor enforcement, and grid-map or fallback identity assignment.

State and persistence: Static `servGMap` and `myCryptoFactory` persist for the process. Per-connection authentication mutates `SecEntity.moninfo`, `SecEntity.name`, entity attributes, and link ID. No durable state is written.

Dependencies and integration points: Uses `XrdTlsPeerCerts`, `XrdTlsContext`, `XrdCryptoX509Chain`, `XrdCryptoFactory`, `XrdOucGMap`, `XrdSecEntityAttr`, OpenSSL, and the `XrdHttpSecXtractor` ABI. `TRACEI`/`eDest` report security diagnostics.

Risks: Fallback identity generation from DN/CN is compatibility-driven and can produce surprising names if gridmap is absent. Memory ownership of `SecEntity` string fields is manual. Required gridmap/extractor settings turn mapping failures into hard authentication failures. OpenSSL context access is noted as undesirable in the source comment.

Test signals: Certificate-present and certificate-absent TLS cases, gridmap success/failure with required and optional modes, extractor success/failure, fallback hash/CN naming, and cleanup of replaced `SecEntity.moninfo/name`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecurity.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpStatic.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpStatic.hh

Purpose: Central include for small compiled-in HTTP static assets used by the XrdHTTP directory/listing UI.

Important APIs/types/functions: No functions or classes. Includes `static/xrdhttp_css.h` and `static/xrdhttp_favicon_ico.h`; a logo include is present but commented out.

Control flow: Consumers include this header to get the asset arrays and lengths in translation units that serve static resources.

State and persistence: Asset bytes are compiled into process memory. No runtime mutation or persistence occurs.

Dependencies and integration points: Depends on generated C headers produced from static resources, likely by a binary-to-C tool. Integrates with the XrdHTTP static file serving path.

Risks: Included headers define global arrays rather than `extern` declarations, so multiple inclusion across translation units can cause duplicate symbol/link issues unless only included in controlled places. Asset regeneration must preserve symbol names.

Test signals: Build/link with all consumers, request CSS and favicon resources, and verify lengths match served payload bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpStatic.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpTrace.hh

Purpose: Defines XrdHTTP tracing flags and convenience macros around `XrdSysTrace`.

Important APIs/types/functions: Flags include `TRACE_AUTH`, `TRACE_DEBUG`, `TRACE_MEM`, `TRACE_REQ`, `TRACE_REDIR`, `TRACE_RSP`, and `TRACE_ALL`. In debug builds it declares external `XrdHttpTrace` and defines `TRACE`, `TRACEI`, `TRACING`, and `EPNAME`; in `NODEBUG` builds these are no-ops.

Control flow: Call sites set a local `TraceID` and optionally `TRACELINK`, then macros emit through `SYSTRACE` only when the relevant `XrdHttpTrace.What` bit is enabled.

State and persistence: Trace state is centralized in the external `XrdHttpTrace` object. This header itself has no storage.

Dependencies and integration points: Integrates with `XrdSysHeaders` and `XrdSysTrace`; used throughout HTTP security, request, protocol, and plugin code for runtime diagnostics.

Risks: Macros depend on call-site names such as `TraceID` and `TRACELINK`, so misuse produces compile failures or wrong link context. Trace option changes must stay aligned with config parsing.

Test signals: Compile with and without `NODEBUG`, enable individual trace masks, and verify link-scoped and non-link-scoped messages appear as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.cc

Purpose: Implements shared HTTP utility functions for encoding, checksums, base64/hex conversion, XML escaping, HMAC redirection hashes, and xrootd/errno to HTTP status mapping.

Important APIs/types/functions: `Tobase64` overloads encode raw bytes or `vector<uint8_t>`. `base64ToBytes`, `bytesToHex`, `base64DecodeHex`, and `Fromhexdigest` convert digest forms. `calcHashes` computes an HMAC-SHA256-derived base64 hash using OpenSSL 3 `EVP_MAC` or legacy `HMAC_CTX`. `quote`, `unquote`, and `escapeXML` allocate transformed strings. `mapXrdErrToHttp`, `mapErrNoToHttp`, and `httpStatusToString` normalize errors and status text.

Control flow: Most helpers are direct transforms. `calcHashes` builds a keyed MAC over filename, request code, selected `XrdSecEntity` fields, and a timestamp string, then encodes half of the digest. Error mapping first converts xrootd protocol errors to errno, then to HTTP status.

State and persistence: Stateless except for caller-owned output buffers and malloc-returned strings. OpenSSL BIO/MAC objects are created and freed per call.

Dependencies and integration points: Depends on OpenSSL BIO/HMAC/EVP APIs, XRootD protocol and security types, and errno constants. Used by request parsing, redirects, digest handling, TPC error reporting, and static response construction.

Risks: `quote`, `unquote`, and `escapeXML` return malloc-owned buffers and require explicit `free`. `unquote` accepts percent sequences without validating hex digits. `Fromhexdigest` reserves but does not clear output, so callers should pass an empty vector or clear it first. `itos` uses `sprintf` into a fixed buffer but only for a `long`.

Test signals: Round-trip URL encoding/decoding, invalid percent and hex input, base64/hex digest conversions, OpenSSL 1.1/3 builds, HMAC stability, errno coverage, and status string fallbacks for unknown ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.hh

Purpose: Declares common XrdHTTP utility APIs and HTTP status constants used across the HTTP core and plugins.

Important APIs/types/functions: Defines numeric constants for 1xx through 5xx HTTP statuses, `itos`, `mystrchrnul`, `calcHashes`, `compareHash`, digest/base64/hex helpers, URL `quote`/`unquote` wrappers (`decode_raw`, `encode_raw`, `encode_str`, `decode_str`), `encode_opaque`, `escapeXML`, error mapping helpers, `httpStatusToString`, and `XrdHttpIOList` as `vector<XrdOucIOVec2>`.

Control flow: Inline wrappers allocate temporary mutable buffers where required and free intermediate encoded/decoded values. `encode_opaque` splits an opaque query string on `&`, encodes key/value pairs containing `=`, and rebuilds a query body.

State and persistence: Header has no persistent state. Inline helpers allocate per call and return values or malloc-owned pointers depending on API.

Dependencies and integration points: Includes XRootD protocol, `XrdSecEntity`, `XrdOucIOVec`, `XrdOucTUtils`, and standard containers/strings. It is a central dependency for request handling, TPC, Macaroons, and response generation.

Risks: Mixed ownership conventions (`std::string` wrappers versus malloc-returned raw pointers) can leak or double-free if callers are careless. `encode_opaque` silently drops tokens without `=`, which is appropriate for key/value opaque data but may surprise callers expecting pass-through semantics.

Test signals: Compile consumers, verify constants match expected HTTP codes, test `encode_opaque` with authorization-like values, and assert mapping helpers produce expected statuses for representative errno and xrootd errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_css.h -->
# sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_css.h

Purpose: Embeds the XrdHTTP directory/listing stylesheet as a C byte array.

Important APIs/types/functions: Defines `unsigned char static_css_xrdhttp_css[]` and `unsigned int static_css_xrdhttp_css_len`. The bytes decode to CSS for HTML/body defaults, links, header, file table columns/classes, file/folder icons, link coloring, metadata links, footer, and request-by text.

Control flow: No executable control flow. The HTTP static resource path serves the byte array with the recorded length.

State and persistence: Static compiled asset data only. No mutation or durable state.

Dependencies and integration points: Included by `XrdHttpStatic.hh` and consumed by static response serving code. The original CSS likely lives beside it as `xrdhttp.css`.

Risks: Global definitions in a header can duplicate symbols if included from multiple translation units. Regeneration must keep symbol names and length accurate. The CSS references `/icons/generic.gif` and `/icons/folder.gif`, so serving those paths affects visual completeness.

Test signals: Verify served CSS byte length equals `static_css_xrdhttp_css_len`, content type is correct, directory listing uses the expected styles, and no duplicate-symbol link failures occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_css.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_favicon_ico.h -->
# sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_favicon_ico.h

Purpose: Embeds the XrdHTTP favicon asset as a C byte array.

Important APIs/types/functions: Defines `unsigned char favicon_ico[]` and `unsigned int favicon_ico_len`. The data begins with a GIF signature despite the `.ico` naming, so consumers should serve the bytes as the established favicon resource rather than infer strict ICO structure from the symbol name.

Control flow: No executable control flow. Static serving code writes the byte array to clients.

State and persistence: Compiled read-only asset data. No runtime state.

Dependencies and integration points: Included by `XrdHttpStatic.hh`; used by the HTTP static resource endpoint.

Risks: Header-defined globals can duplicate at link time if included broadly. MIME/type assumptions around favicon `.ico` versus embedded GIF bytes may matter for strict clients, though browsers are tolerant. Asset regeneration must keep `favicon_ico_len` synchronized.

Test signals: Request the favicon path, verify response body size and browser display, and run a full link build to catch duplicate symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_favicon_ico.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdHttpCors/CMakeLists.txt

Purpose: Builds and installs the CORS HTTP extension plugin.

Important APIs/types/functions: Defines module target `XrdHttpCors-${PLUGIN_VERSION}`, compiles `XrdHttpCorsHandler.cc`, links `XrdUtils`, and installs the module to `${CMAKE_INSTALL_LIBDIR}`.

Control flow: The CMake file has no feature gating here; inclusion from the parent build determines whether it is evaluated.

State and persistence: Build metadata only.

Dependencies and integration points: Produces a dynamically loadable XRootD HTTP CORS plugin that exposes `XrdHttpCorsGetHandler`.

Risks: Missing source/header in the target list would break plugin ABI export at runtime. The target links only `XrdUtils`; if handler implementation starts using other non-header-only libraries, link dependencies must be updated.

Test signals: Configure/build with the plugin enabled, inspect the installed module name, and load it through the XRootD HTTP CORS configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCors.hh -->
# sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCors.hh

Purpose: Declares the CORS plugin interface for XRootD HTTP.

Important APIs/types/functions: `XrdHttpCors` declares `Configure`, `addAllowedOrigin`, and `getCORSAllowOriginHeader`. The getter type `XrdHttpCorsget_t` describes dynamic loader lookup, and `extern "C" XrdHttpCorsGetHandler` is the concrete plugin entry point.

Control flow: The HTTP layer loads an implementation, calls `Configure` with the config file and error object, adds origins as needed, and asks for an `Access-Control-Allow-Origin` header for a request origin. Returning `std::nullopt` means the origin is not trusted.

State and persistence: Interface only; implementations own origin state in memory.

Dependencies and integration points: Uses `std::optional`, strings, `XrdOucEnv`, `XrdSysError`, and XRootD plugin loading conventions.

Risks: The interface returns a fully formed header string, so callers must avoid adding duplicate header names or CRLF unexpectedly. ABI compatibility depends on C++ standard library and plugin build matching the server.

Test signals: Load handler entry point, configure allowed origins, request both matching and non-matching origins, and verify no CORS header is emitted for untrusted origins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCors.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.cc

Purpose: Implements the default basic CORS plugin.

Important APIs/types/functions: `XrdHttpCorsGetHandler` returns a new `XrdHttpCorsHandler`. `Configure` gathers `cors.origin` directives with `XrdOucGatherConf`. `addAllowedOrigin` trims and stores origins in an unordered set. `getCORSAllowOriginHeader` returns `Access-Control-Allow-Origin: <origin>` for exact matches.

Control flow: Configuration gathers all `cors.origin` tokens from the config body, iterates tokens, and calls `addAllowedOrigin`. At request time the plugin performs exact string lookup against the set and returns either a formed header or `nullopt`.

State and persistence: Allowed origins live in `m_origins` for the plugin instance lifetime. No disk writes or dynamic refresh are present.

Dependencies and integration points: Depends on `XrdOucGatherConf`, `XrdOucUtils::trim`, `XrdVersion` plugin metadata, and the `XrdHttpCors` ABI.

Risks: Origin matching is exact and does not normalize scheme/host case or trailing slash beyond trimming whitespace. It does not generate other CORS headers such as methods, headers, or credentials. Multiple tokens are accepted without syntactic validation.

Test signals: Config with repeated and space-delimited `cors.origin`, whitespace trimming, exact mismatch behavior, empty token suppression, and plugin version symbol loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.hh

Purpose: Declares the default `XrdHttpCorsHandler` implementation.

Important APIs/types/functions: Inherits `XrdHttpCors`, overrides `Configure`, `addAllowedOrigin`, and `getCORSAllowOriginHeader`, and stores origins in `std::unordered_set<std::string> m_origins`.

Control flow: The header only defines the object shape used by the implementation and loader.

State and persistence: Per-plugin instance in-memory origin set. No persistence.

Dependencies and integration points: Includes the CORS interface and standard unordered set. Used by `XrdHttpCorsHandler.cc`.

Risks: The data structure is not explicitly synchronized; safety depends on configure-before-use or external locking if runtime origin changes are introduced.

Test signals: Compile with C++17 optional support, instantiate handler, add origins, and query allowed/non-allowed values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpCors/XrdHttpCorsHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/CMakeLists.txt

Purpose: Configures build/install of the HTTP third-party-copy plugin.

Important APIs/types/functions: Requires `ENABLE_HTTP`, finds CURL, sets `BUILD_TPC`, builds module `XrdHttpTPC-${PLUGIN_VERSION}` from configure, multistream, PMark, state, stream, handler, and utility sources, links XRootD server/utils/http utils, `CURL::libcurl`, OpenSSL, pthreads, and dl, and applies an ELF version script on non-Apple platforms.

Control flow: If HTTP is disabled or CURL is unavailable, returns without building. With `FORCE_ENABLED`, CURL is required and configure failure is hard.

State and persistence: Build metadata only.

Dependencies and integration points: Produces the `XrdHttpGetExtHandler` module used by XrdHTTP to handle `COPY` and `OPTIONS`.

Risks: Plugin availability is conditional on CURL and HTTP. Link dependency list must stay in sync with added OpenSSL/XRootD subsystem usage. Version-script handling is platform-specific.

Test signals: Configure with and without CURL, with `FORCE_ENABLED`, on non-Apple and Apple platforms, and load the installed TPC module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcConfigure.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcConfigure.cc

Purpose: Parses HTTP TPC plugin configuration and initializes filesystem, TLS CA, logging, routing, and transfer policy state.

Important APIs/types/functions: `TPCHandler::Configure` reads directives such as `http.desthttps`, `tpc.allow`, `tpc.deny`, `tpc.trace`, `tpc.fixed_route`, `tpc.header2cgi`, and `tpc.timeout`. `ConfigureLogger` maps trace words to `LogMask` bits.

Control flow: The config stream captures HTTP TPC directives, validates each directive, updates handler fields, removes `authorization` from `hdr2cgimap`, initializes CA/CRL material from `http.cadir`/`http.cafile` or `XRDTPC_CADIR`, and obtains `XrdSfsFileSystem*` from the environment.

State and persistence: Mutates handler instance fields for allow/deny private/local routing, HTTPS redirect preference, fixed-route mode, timeouts, CA paths, CA temp file, `usingEC`, CRL policy, SFS pointer, and header-to-CGI map. `XrdTlsTempCA` may create temporary CA/CRL artifacts managed by that helper.

Dependencies and integration points: Uses `XrdOucStream`, `XrdOuca2x`, `XrdOucEnv`, `XrdTlsTempCA`, `XrdHttpProtocol::parseHeader2CGI`, environment variables, and the XRootD SFS object.

Risks: A bad directive aborts plugin configuration. `http.desthttps` validation error text says `https.desthttps`, a minor diagnostic mismatch. Missing SFS object is fatal. `XRDTPC_CADIR` bypasses temp CA generation and CRL workaround behavior.

Test signals: Config parse success/failure for every directive, header2cgi authorization removal, timeout defaults, CA/CRL setup with empty CRLs, environment overrides, and absence of SFS pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcConfigure.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcMultistream.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcMultistream.cc

Purpose: Implements multi-stream pull transfers for HTTP TPC using libcurl multi handles, duplicated `State` objects, and reordering buffers in `Stream`.

Important APIs/types/functions: Internal `MultiCurlHandler` manages active/available curl handles, transfer scheduling, completion accounting, buffer-aware throttling, and error aggregation. `TPCHandler::RunCurlWithStreamsImpl` performs the multi-stream transfer loop. `RunCurlWithStreams` wraps implementation errors and deletes allocated `State` objects.

Control flow: The first state is moved from the caller and duplicated up to `streams * m_pipelining_multiplier`. A libcurl multi handle is configured with host connection limits, a chunked 202 response is started, byte ranges are scheduled in `m_block_size` chunks, and the loop alternates `curl_multi_perform`, PMark start, completion harvesting, new range scheduling, progress markers, timeout checks, and `curl_multi_wait`. Finalization flushes stream buffers, validates full content offset, closes the file, sends success/failure chunk, and terminates chunked response.

State and persistence: Runtime state includes current offset, active/idle handles, aggregate bytes/status/error, and reordering buffers in the shared `Stream`. The only durable effect is local file writes through the SFS file handle.

Dependencies and integration points: Uses `TPC::State`, `TPC::Stream`, libcurl multi API, TPC perf marker methods, PMark manager, and XRootD logging/error response functions.

Risks: Manual `new`/`delete` for `State` objects requires all exception paths to clean up. Buffer availability controls concurrency; logic bugs can deadlock or exhaust memory. Progress timeout currently compares `current_offset`, which reflects scheduled bytes, not necessarily flushed bytes. Multi-stream is pull-only in this code path.

Test signals: Multi-stream pulls with 1, 2, and high stream counts, remote failures on one range, buffer exhaustion, timeout with stalled server, final short block, interrupted chunk response, and verification that the final file is complete and ordered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcMultistream.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.cc

Purpose: Implements packet marking management for HTTP TPC sockets so transfer traffic can emit flow metadata when PMark/scitag is configured.

Important APIs/types/functions: `SocketInfo` captures an fd and address as `XrdNetAddr` and `XrdSecEntity`. `PMarkManager::connect` optionally performs a timed socket connect and registers data-transfer sockets. `startTransfer`, `beginPMarks`, `endPmark`, and `isEnabled` control marker lifetime.

Control flow: Before transfer, `connect` either lets libcurl connect normally or connects with `XrdNetUtils::ConnectWithTimeout` when PMark is enabled. After `startTransfer`, newly connected sockets are queued. `beginPMarks` creates a primary handle with `scitag.flow` and a direction-swapped `pmark.appname` (`http-put` for pull, `http-get` for push), then derives additional handles from the first. `endPmark` erases the handle before socket close.

State and persistence: Maintains queued socket infos and active `unique_ptr<XrdNetPMark::Handle>` handles keyed by fd. No durable storage.

Dependencies and integration points: Uses `XrdNetPMark`, `XrdNetUtils`, `XrdNetAddr`, `XrdSecEntity`, `XrdHttpExtReq`, and `TPC::TpcType`. Called from TPC libcurl open/close socket callbacks and transfer loops.

Risks: PMark is enabled only when both `req.pmark` and non-negative scitag exist. If derived handle creation fails, queued sockets remain for retry. Timing of `startTransfer` is important to avoid marking control connections. Socket close must call `endPmark` before `close` to preserve accounting.

Test signals: Transfers with and without scitag, pull and push appname direction, multistream derived handles, failed timed connect, PMark begin failure retry, and close callback cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.hh -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.hh

Purpose: Declares the HTTP TPC packet marking manager and socket metadata helper.

Important APIs/types/functions: `XrdHttpTpc::PMarkManager`, nested `SocketInfo`, `connect`, `isEnabled`, `startTransfer`, `beginPMarks`, `endPmark`, and private `addFd`. Members include a queue of socket infos, a map of fd-to-handle, `XrdNetPMark*`, request reference, transfer-start flag, and TPC type.

Control flow: Header documents the intended sequence: connect/register sockets, call `startTransfer` before data transfer, call `beginPMarks` after `curl_multi_perform`, and call `endPmark` before socket close.

State and persistence: Per-transfer in-memory queues and handles. No persistent storage.

Dependencies and integration points: Depends on XRootD networking, security, PMark, and HTTP extension request types. It is embedded in `TPCLogRecord`.

Risks: Holds a reference to `XrdHttpExtReq`, so lifetime must not exceed the request. Public API relies on caller sequence for correct marking and accounting.

Test signals: Unit-level sequencing tests with fake PMark, and integration tests through libcurl socket callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcPMarkManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.cc

Purpose: Implements libcurl callback state for individual HTTP TPC HEAD, pull, and push transfers.

Important APIs/types/functions: Destructor frees curl header lists. `InstallHandlers` sets user agent, header callbacks, read/write callbacks, redirect/auth options, upload mode, low-speed limits, and push size. `SetupHeaders` and `SetupHeadersForHEAD` forward copy/transfer headers and digest negotiation. `Header`, `WriteCB`, `PushRespCB`, `ReadCB`, `Write`, `Read`, `Flush`, `Finalize`, `Duplicate`, `SetTransferParameters`, and `GetConnectionDescription` implement transfer behavior.

Control flow: Curl delivers headers first; `Header` parses status, content length, and `Repr-Digest`. Pull write callbacks reject body before headers, collect up to 1KB of remote error body for >=400 statuses, or write to the local `Stream`. Push read callbacks read from the local stream after successful remote status. Duplicates copy curl options and custom header lists for multistream range transfers. Finalization delegates to `Stream`.

State and persistence: Tracks per-request offset, start offset, status code, error code/message, content length, push length, header state, curl handle, header list, protocol string, transfer-state flag, credential-forwarding flag, and parsed repr digests. Durable effects occur via `Stream` read/write/close.

Dependencies and integration points: Uses libcurl easy options and callbacks, `XrdSfsFile` via `Stream`, `XrdHttpExtReq`, `XrdHttpHeaderUtils::parseReprDigest`, and XrdVersion for user agent.

Risks: `Move` copies most fields but assigns `other.m_repr_digests = m_repr_digests`, which appears reversed from normal move semantics and could lose digest state in the moved-to object if ever relevant. `SetupHeaders` calls `curl_slist_append(list, reprDigestHeader.c_str())` without assigning the return value in the push digest branch, so that appended header may be dropped. Header parsing returns zero on malformed input, causing curl aborts. Manual curl-slist ownership is delicate.

Test signals: HEAD content-length and repr-digest parsing, push and pull error-body capture, copy-header/transferheader forwarding, Want-Repr-Digest formation, duplicate handles retaining headers, range setup, IPv6 connection description formatting, and finalization error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.hh -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.hh

Purpose: Declares `TPC::State`, the per-curl-handle state object used for HEAD, push, pull, and multistream range operations.

Important APIs/types/functions: Constructors distinguish default, HEAD-only, and transfer states. Public methods configure transfer range and headers, expose bytes/status/error/content length/digests, reset transient state, duplicate/move state, flush/finalize the stream, and report connection description. Private static callbacks bridge libcurl to member methods.

Control flow: State owns callback data for libcurl but borrows the curl handle. Transfer state attaches read callbacks for push or write callbacks for pull; HEAD state only installs header handling. Multistream uses `Duplicate` and `Move` to clone handles and reset transients between ranges.

State and persistence: Tracks all curl/transfer transients and a non-owning `Stream*`. Header lists are owned by the `State` object. Underlying file data persists through `Stream`.

Dependencies and integration points: Forward-declares CURL and XRootD file/request types; implementation links to libcurl and SFS. Used heavily by `TPCHandler`.

Risks: Borrowed curl and stream pointers require careful lifetime ordering. The default constructor creates an inert state that must be populated by `Move` before use. Copy is disabled but move is manual, not C++ move semantics.

Test signals: Constructor variants, destructor header cleanup, duplicate/move lifecycle in multistream, and behavior when curl handle allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.cc

Purpose: Implements the file stream abstraction used by HTTP TPC to read local files for push and write local files for pull, including out-of-order buffering for multistream downloads.

Important APIs/types/functions: Destructor deletes buffers and closes the file handle. `Finalize` deletes buffers, closes the file, and verifies all reordering buffers are available. `Stat`, `Read`, `Write`, `WriteImpl`, and `DumpBuffers` wrap SFS operations and diagnostics.

Control flow: Writes reject closed streams and prior offsets. In-order MB-aligned or forced writes go directly to SFS. Otherwise, data is accepted into `Entry` buffers, and the stream repeatedly tries to flush buffers whose offset matches `m_offset`. Forced zero-size writes flush partial buffers at EOF. Memory for unused buffers may shrink under low occupancy.

State and persistence: Holds `unique_ptr<XrdSfsFile>`, current write offset, open-for-write flag, available-buffer count, vector of `Entry*`, and last error message. Durable persistence is the SFS file being written/closed.

Dependencies and integration points: Depends on `XrdSfsFile`, `XrdSysError`, and the TPC `State` callbacks. Supports HDFS/RADOS constraints described in comments by presenting sequential/aligned writes.

Risks: `Finalize` deletes all buffer entries before checking `m_avail_count == m_buffers.size()`, so outstanding-buffer detection relies on the saved count rather than inspecting entries. Destructor closes the file even after `Finalize` already closed it, unless SFS close is idempotent. Buffer management is pointer-based and sensitive to partial accept/write logic.

Test signals: Ordered writes, out-of-order range writes, forced final flush, buffer exhaustion, short write and SFS error propagation, finalize with outstanding buffers, destructor after finalize, and push `Read` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.hh -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.hh

Purpose: Declares `TPC::Stream`, a file-handle abstraction with buffering for single-stream-compatible writes during multi-stream TPC pulls.

Important APIs/types/functions: Public API includes `Stat`, `Read`, `Write`, `AvailableBuffers`, `DumpBuffers`, `Finalize`, and `GetErrorMessage`. Nested `Entry` buffers track offset, capacity, size, availability, accepting bytes, write eligibility, and memory shrinkage.

Control flow: The interface is designed for curl callbacks: push reads call `Read`, pull writes call `Write`, and transfer completion calls `Finalize`. The nested `Entry` class only writes when its offset equals the stream offset and, unless forced, when the buffer is full.

State and persistence: Owns an `XrdSfsFile` and heap-allocated reordering buffers. Writes persist through the SFS backend.

Dependencies and integration points: Depends on XRootD SFS and logging. Shared across `State`, single-stream, and multistream TPC paths.

Risks: The constructor sets `m_open_for_write = true` even for streams used for push reads with zero buffers; push code only calls `Read`, but lifecycle semantics are still write-oriented. Raw `Entry*` vector requires destructor/finalize discipline.

Test signals: Buffer lifecycle, no-buffer push stream behavior, and capacity calculation for `streams * m_pipelining_multiplier`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcStream.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.cc

Purpose: Implements the HTTP TPC extension handler that processes `COPY` and `OPTIONS`, performs pull/push transfers via libcurl and SFS, emits progress markers, handles redirects, and reports monitoring.

Important APIs/types/functions: Static plugin entry `XrdHttpGetExtHandler`, `TPCHandler` constructor/destructor, `MatchesPath`, `ProcessReq`, `ProcessOptionsReq`, `ProcessPullReq`, `ProcessPushReq`, `RunCurlWithUpdates`, `SendPerfMarker`, `PerformHEADRequest`, `GetRemoteFileInfoTPCPull`, `RedirectTransfer`, `OpenWaitStall`, `ConfigureCurlCA`, socket/SSL callbacks, `mismatchReprDigest`, `GetAuthz`, `prepareURL`, and `logTransferEvent`.

Control flow: `ProcessReq` rejects unsupported credential modes, chooses pull on `Source` and push on `Destination`, normalizes `davs/s3/s3s` source schemes to HTTPS, and only allows HTTP(S). Pull initializes curl, optionally binds fixed route interface, opens local file for write with `oss.task=httptpc` and `oss.asize`, fetches remote HEAD info and repr digests, verifies client-provided digest, then streams single or multistream. Push opens local file read-only, handles filesystem redirects, uploads to remote, and streams progress. Both modes use chunked 202 responses with periodic performance markers and final success/failure text.

State and persistence: Static state includes monitor ID, marker period, block sizes, mutex, and CRL policy. Per-transfer `TPCLogRecord` captures local/remote URLs, user, stream count, status, bytes, IP version, PMark manager, and reports to `XrdXrootdTpcMon` on destruction. Durable effects are local file create/truncate/write for pull and remote upload for push.

Dependencies and integration points: Integrates XrdHTTP extension ABI, XRootD SFS, `XrdSecEntity`, `XrdXrootdRedirHelper`, `XrdXrootdTpcMon`, `XrdNetUtils`, `XrdTlsTempCA`, libcurl, OpenSSL, PMark, HTTP utils, and TPC state/stream utilities.

Risks: Network callbacks enforce private/local address policy but depend on libcurl using the custom open socket path. `allowMissingCRL` disables a CRL failure in the OpenSSL verify callback only for a specific error. `m_monid++` in pull is not protected by the mutex unlike push. Redirect URL construction must preserve full resource query and encode xrootd opaque data correctly. `OpenWaitStall` breaks after a single stall/started sleep rather than looping to retry multiple times.

Test signals: COPY pull/push happy paths, unsupported credential and missing source/destination, scheme filtering, local/private address blocking, SFS redirect with and without redirect plugin rewrite, fixed-route interface, HEAD failures, digest mismatch 412, CRL/no-CRL CA behavior, chunked progress markers, timeout on no progress, remote HTTP errors, and monitor record output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.hh -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.hh

Purpose: Declares the HTTP TPC extension handler, transfer logging record, transfer type enums, and libcurl handle management types.

Important APIs/types/functions: `LogMask`, `TpcType`, `CurlDeleter`, `ManagedCurlHandle`, `TPCHandler`, nested `TPCLogRecord`, static `OSS_TASK_OPAQUE`, and numerous private helpers for curl callbacks, transfer processing, redirects, headers, logging, and digest verification.

Control flow: The class implements `XrdHttpExtHandler::MatchesPath` and `ProcessReq`, then routes to push/pull implementations. Helper declarations mirror the full lifecycle: configure, open local/remote resources, run curl, emit markers, and generate client errors.

State and persistence: Handler fields persist configuration for local/private routing, HTTPS redirects, fixed route, timeouts, CA paths, SFS pointer, temp CA, EC mode, header-to-CGI map, and static monitoring counters. `TPCLogRecord` persists one transfer's monitoring/logging state until destruction.

Dependencies and integration points: Includes XRootD HTTP extension, HTTP utils, TLS temp CA, PMark manager, curl, OpenSSL, and pthread mutex. Exposes the module through `XrdHttpGetExtHandler`.

Risks: Many static and instance settings affect security-sensitive transfer behavior. The nested `TPCLogRecord` holds references to request state and owns a PMark manager, so object lifetime is tied to the request function stack.

Test signals: Header-level compile against current XRootD APIs, plugin ABI symbol lookup, and transfer log record destructor reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.cc

Purpose: Implements construction of the local XRootD open URL for HTTP TPC requests.

Important APIs/types/functions: `XrdHttpTpcUtils::prepareOpenURL` consumes `PrepareOpenURLParams`, appends `oss.task=httptpc`, merges `xrd-http-query`, moves `authz=` into `Authorization` when missing, appends configured header-to-CGI mappings, and adds the first alphabetically ordered `Repr-Digest` as `cks.type`/`cks.value`.

Control flow: It starts an opaque query with `?oss.task=httptpc`. If `xrd-http-query` exists, it splits tokens on `&`; `authz=` is stripped from opaque and copied to request headers, while other tokens remain opaque. It then scans request headers case-insensitively for configured header-to-CGI entries and appends matching values. Finally it appends digest information if present and returns `reqResource + opaque`.

State and persistence: Mutates the request header map by adding `Authorization` if an authz opaque token is present and no auth header already exists. No persistent state.

Dependencies and integration points: Uses `XrdOucTUtils`, TPC handler `OSS_TASK_OPAQUE`, and the HTTP extension request model. Its output is passed to SFS `open`.

Risks: Header-to-CGI values are appended without URL encoding here, so callers/configuration must ensure safe values or rely on upstream encoding. Only the first sorted digest is propagated. `authz=` matching is case-sensitive.

Test signals: Queries with and without `authz`, existing Authorization header preservation, multiple opaque tokens, header2cgi case-insensitive matches, digest propagation order, and resources with preexisting query assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.hh

Purpose: Declares the HTTP TPC URL preparation utility.

Important APIs/types/functions: `XrdHttpTpcUtils::PrepareOpenURLParams` holds references to the request resource, mutable headers, configured header-to-CGI map, and repr-digest map. Static `prepareOpenURL` returns the XRootD open URL with TPC opaque metadata.

Control flow: Header documents the key behavior: always append `oss.task=httptpc`, fold `xrd-http-query` into opaque parameters, strip `authz` into Authorization, append configured header CGI values, and include digest metadata.

State and persistence: No owned state. The params struct deliberately passes request headers by mutable reference.

Dependencies and integration points: Includes `XrdHttpExtHandler` for request header map types and is used by `TPCHandler::prepareURL`.

Risks: Because the utility mutates headers, callers need to avoid unintended reuse side effects. Reference members require all referenced maps/strings to outlive the params object.

Test signals: Compile and unit-test `prepareOpenURL` with representative request/header maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/xrootd-test-tpc -->
# sources/distributed-fs/xrootd/src/XrdHttpTpc/xrootd-test-tpc

Purpose: Python helper script to drive manual HTTP TPC COPY transfers using bearer tokens.

Important APIs/types/functions: `parse_args` handles token paths, push/pull/auto mode, overwrite, streams, source, and destination. `get_token` reads the first non-comment token line. `determine_mode` sends OPTIONS to the destination and chooses pull if COPY is advertised. `main` builds headers and sends the COPY request with `requests`.

Control flow: Token paths are resolved from explicit arguments, `SCITOKEN`, `~/.scitokens/token`, or `/tmp/scitoken_u<euid>`. In auto mode, OPTIONS decides whether destination can pull. Pull mode sends COPY to destination with `Source` and destination auth, plus `Copy-Header` for source auth. Push mode sends COPY to source with `Destination` and source auth, plus destination auth as `Copy-Header`.

State and persistence: No persistence beyond reading token files. It prints response status, headers, and body.

Dependencies and integration points: Uses Python `requests`, CA verification at `/etc/grid-security/certificates`, and the HTTP TPC plugin's headers (`Authorization`, `Source`, `Destination`, `Copy-Header`, `Overwrite`, `X-Number-Of-Streams`).

Risks: The script uses Python 2 print syntax and may not run under Python 3 despite a generic `#!/usr/bin/python`. It sets a fixed CA verification path and does not retry despite a `try_again` variable. Token content is injected into headers, so output/log handling should avoid leaking tokens.

Test signals: Run under the supported Python interpreter, test auto/pull/push modes, missing token discovery, stream validation, and successful COPY against a test pair of HTTP TPC endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdHttpTpc/xrootd-test-tpc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdMacaroons/CMakeLists.txt

Purpose: Configures build/install of the Macaroons authorization and HTTP extension plugin.

Important APIs/types/functions: Requires `ENABLE_MACAROONS`, HTTP support when force-enabled, `Macaroons`, `json-c` on non-Apple, and `BUILD_HTTP`. Builds module `XrdMacaroons-${PLUGIN_VERSION}` from plugin entry, authz, configure, and handler sources. Links `XrdHttpUtils`, `XrdUtils`, `XrdServer`, `uuid`, OpenSSL crypto, Macaroons, JSON, and dl, with an ELF version script on non-Apple.

Control flow: Missing feature flags or dependencies return without building unless force-enabled paths require hard errors.

State and persistence: Build metadata only.

Dependencies and integration points: Produces both authorization plugin symbols and HTTP extension handler symbols for macaroon issuance/validation.

Risks: `JSON_FOUND` is referenced even on Apple where pkg-config block is skipped; parent CMake may define it, but platform behavior should be checked. Macaroons requires HTTP build support.

Test signals: Configure with enabled/disabled macaroons, missing libmacaroons/json-c, force-enabled HTTP absence, non-Apple version-script link, and plugin load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroons.cc -->
# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroons.cc

Purpose: Provides dynamic plugin entry points for Macaroons authorization and HTTP extension handler creation.

Important APIs/types/functions: Exports `XrdAccAuthorizeObjAdd`, `XrdAccAuthorizeObject`, and `XrdHttpGetExtHandler`, with version symbols for all three. Also defines global `XrdSciTokensHelper *SciTokensHelper`.

Control flow: `XrdAccAuthorizeObjAdd` wraps an existing chained authorization object with `Macaroons::Authz`. `XrdAccAuthorizeObject` optionally loads a chained auth library from parameters via `XrdOucPinPath`, `dlopen`, and `dlsym`, otherwise obtains the default authorizer, then wraps it. `XrdHttpGetExtHandler` obtains the default authorizer from the environment and creates a `Macaroons::Handler`.

State and persistence: `SciTokensHelper` is set to each new `Authz` instance, exposing macaroon validation through the SciTokens helper interface. Dynamically loaded chained library handles are not retained in visible state except by the loaded plugin/runtime.

Dependencies and integration points: Integrates XrdAcc authorization ABI, XrdHTTP extension ABI, dynamic loading, default authorization object lookup, `XrdMacaroonsAuthz`, `XrdMacaroonsHandler`, and XRootD version metadata.

Risks: The chained library handle is not closed on success, which is normally needed to keep symbols alive but means process-lifetime residency. Error paths must close handles on failures. Global `SciTokensHelper` can be overwritten if multiple instances are created. Parameter parsing assumes first token is the chained library.

Test signals: Load as primary authz, load with chained authz params, failure to resolve/load chained library, HTTP handler creation with `XrdAccAuthorize*` env pointer, and SciTokens helper validation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroons.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.cc -->
# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.cc

Purpose: Implements macaroon-based authorization and token validation for XRootD access operations.

Important APIs/types/functions: Internal `AuthzCheck` verifies `before`, `activity`, `path`, and `name` caveats. `AddPriv` maps `Access_Operation` to `XrdAccPrivs`. `Authz::Access` verifies request-specific or ZTN-session macaroon tokens and grants only the requested operation. `Authz::Validate` minimally validates non-expired session tokens. `validate_verify_empty` accepts path/name/activity caveats for validation-only mode.

Control flow: `Access` bypasses macaroon issuing tests (`AOP_Any`) to the chain, extracts `authz` from env stripping `Bearer%20`, falls back to ZTN entity creds, and on missing/parse failure delegates to configured on-missing behavior. For macaroons, it creates a verifier, installs caveat validators, checks location against `all.sitename`, verifies with the shared secret, logs ID on success, copies `name:` into `Entity->eaAPI` as `request.name`, and returns only the privilege for the requested operation.

State and persistence: `Authz` holds max token duration, chained authorizer, logger, shared secret, location, and on-missing behavior. No token revocation or durable state is stored. Entity attributes may be augmented per request.

Dependencies and integration points: Depends on libmacaroons, XrdAcc, XrdSecEntity attributes, XrdOuc private path helpers (`NormalizeSlashes`, `is_subdirectory`), and `Handler::Config` for shared config parsing. Implements `XrdSciTokensHelper`.

Risks: Location comparison uses `strncmp` with macaroon location size, so a shorter configured location with a longer token location should be reviewed for prefix edge cases. `Entity->creds[Entity->credslen] == '\0'` assumes a readable byte at that index. On failed verification it falls back to chain authz, allowing mixed-token deployments but requiring chain policy to be intentional. Max-duration rejects tokens whose `before` caveat is too far in the future.

Test signals: Caveat verification for expiration, activity mapping, path subtree and substring rejection, stat/mkdir parent allowances, name attribute injection, missing token passthrough/allow/deny, invalid macaroon fallback, wrong location, wrong secret, and `Validate` session-token behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.hh -->
# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.hh

Purpose: Declares the `Macaroons::Authz` class that wraps XRootD authorization with macaroon validation and also implements `XrdSciTokensHelper`.

Important APIs/types/functions: Constructor takes logger, config, and chained authorizer. Overrides `Access`, `Validate`, `Audit`, `Test`, and `IssuerList`. Private `OnMissing` applies configured behavior when no usable macaroon is present.

Control flow: `Access` and `Validate` are implemented in the `.cc`; `Audit` and `Test` are no-ops returning 0, and `IssuerList` returns empty because macaroons have no issuer concept here.

State and persistence: Holds max duration, chain pointer, logger, secret, location, and authz behavior. No persistence.

Dependencies and integration points: Inherits XrdAcc authorization and SciTokens helper interfaces. Used by plugin entry points in `XrdMacaroons.cc`.

Risks: The class does not own the chained authorizer by smart pointer, so ownership/lifetime are external. Empty issuer list may affect clients expecting token issuer discovery.

Test signals: Construction from config, all overridden interface methods, and chained authorizer lifetime expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsAuthz.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsConfigure.cc -->
# sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsConfigure.cc

Purpose: Parses Macaroons plugin configuration and loads the shared secret key.

Important APIs/types/functions: `Handler::Config` reads `all.sitename` and `macaroons.*` directives. Helpers include `xonmissing`, `xtrace`, `xmaxduration`, `xsitename`, and `xsecretkey`.

Control flow: The config stream captures macaroons directives, initializes default trace mask and max duration, recognizes `macaroons.secretkey`, `all.sitename`/`macaroons.sitename`, `macaroons.trace`, `macaroons.maxduration`, and `macaroons.onmissing`, and ignores unknown directives with a warning. Secret-key loading opens a base64 file, decodes through OpenSSL BIO filters into memory, enforces at least 32 decoded bytes, and stores the raw secret string.

State and persistence: Outputs location, secret, max duration, and on-missing behavior by reference. The secret is held in memory by the caller. No files are written.

Dependencies and integration points: Uses `XrdOucStream`, `XrdSysError`, OpenSSL BIO/EVP, errno, and `Macaroons::Handler` enum/types from the handler header.

Risks: `errno` is not reset before `strtoll`, so stale errno could theoretically influence diagnostics after successful parse. Secret-key read loop has an unreachable inner `inlen < 0` branch inside `while ((inlen = BIO_read(...)) > 0)`, but the post-loop error path handles negative results. Missing `all.sitename` is fatal.

Test signals: Valid config, missing sitename, missing/short/unreadable secret file, trace option combinations including `none/off`, invalid onmissing, invalid maxduration, and unknown directive warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdMacaroons/XrdMacaroonsConfigure.cc -->
