# subset-b-007034 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpHandler.cc -->
# sources/distributed-fs/eos/mgm/http/HttpHandler.cc

## Purpose
`HttpHandler.cc` implements the MGM-side plain HTTP protocol handler. It dispatches HTTP verbs, delegates REST URLs to `RestApiManager`, maps file and directory operations to EOS/XRootD namespace calls, and builds `PlainHttpResponse` objects or redirect/stall/error responses for clients.

## Important APIs, Types, and Functions
`HttpHandler::Matches()` accepts standard HTTP verbs. `HandleRequest()` decides REST versus plain HTTP, adds the `eos.app` tag, applies MGM routing via `gOFS->ShouldRoute()`, updates `MgmStats`, and invokes verb-specific methods. `Get()` handles access checks, symlink redirects, ETag conditions, directory index redirects, tape-offline rejection, SFS file open/read, and HEAD support through `isHEAD`. `Put()` handles OwnCloud chunking, partial PUT, ETag preconditions, booking/target size opaque parameters, mtime and `ArchiveMetadata`, SFS open/create retries, and redirect/error translation. `Delete()` drives `/proc/user` `mgm.cmd=rm`. `Options()` advertises WebDAV-capable verbs, while `Post()`, `Trace()`, `Connect()`, and `Patch()` return `501`.

## Control Flow
Requests enter through `HandleRequest()`. REST paths are routed directly to the registered REST handler with the current virtual identity. Plain requests first pass the EOS routing module; a route match returns a redirect without running verb logic. Otherwise the parsed method selects the handler branch. GET/HEAD perform access and stat before choosing directory, file, redirect, or error responses. PUT prepares an EOS opaque query, opens an SFS file, and usually returns `201 Created` or a redirect to the storage endpoint. DELETE validates existence, builds a proc command, and maps EOS return codes to HTTP status.

## State and Persistence Behavior
The handler itself is request-scoped and persists only `mHttpResponse`. Persistent effects are delegated to EOS: file reads use `gOFS->newFile()`, writes/open-create use SFS flags and opaque options, deletes invoke MGM proc commands, and stats/attrs/checksums come from the namespace. ETags and mtime headers reflect namespace metadata. OwnCloud chunk headers and atomic-upload options influence downstream persistence but are not stored in this class.

## Dependencies and Integration Points
The implementation depends on `gOFS`, `XrdMgmOfs`, `XrdSfsFile`, `XrdSecEntity`, `ProcCommand`, `MgmStats`, `HttpServer` response helpers, `OwnCloud` remapping/chunk helpers, EOS mode/timing utilities, and `RestApiManager`. It integrates with the MGM redirector, FST redirects, WebDAV advertisement, CTA archive metadata, and tape-aware namespace flags.

## Risks
Several logging lines check lowercase header keys but print mixed-case variants, which can insert empty map entries or log the wrong value. GET reads the whole file body into memory when no redirect occurs, which is risky for large files or proc-style files. The directory browsing path is intentionally disabled unless `sys.http.index` exists. The tape-offline guard returns `424 Failed Dependency` for files with backup and offline flags. PUT has nuanced OwnCloud and partial-upload behavior where opaque query composition and redirect CGI must remain exact.

## Test Signals
Tests should cover REST bypass, route redirects, all verb dispatch stats, GET/HEAD ETag preconditions, external symlink redirects, directory index attr redirects, tape-offline GET rejection, checksum digest on HEAD, GET SFS redirect/error/data/stall paths, PUT OwnCloud chunk and partial uploads, booking/target size query creation, archive metadata propagation, ENOENT create retry, DELETE file and recursive directory removal, and unimplemented verb status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpHandler.hh -->
# sources/distributed-fs/eos/mgm/http/HttpHandler.hh

## Purpose
`HttpHandler.hh` declares the MGM plain HTTP protocol handler class. It adapts the common HTTP protocol-handler interface to EOS MGM behavior for GET, HEAD, POST, PUT, DELETE, TRACE, OPTIONS, CONNECT, and PATCH requests.

## Important APIs, Types, and Functions
`HttpHandler` derives from `eos::common::HttpHandler` and is constructed with a `VirtualIdentity` pointer that is forwarded to the protocol-handler base. `Matches()` is the protocol-selection predicate used by `ProtocolHandlerFactory`. `HandleRequest()` is the top-level request dispatcher. The verb methods return owning raw `eos::common::HttpResponse*` values and expose `Get(request, isHEAD=false)` so HEAD can reuse GET metadata logic while suppressing a body.

## Control Flow
The factory first calls `Matches()` after WebDAV matching fails. Once selected, the server gives an `HttpRequest` to `HandleRequest()`, which fills the inherited response slot. Consumers later read the response through the common protocol-handler interface.

## State and Persistence Behavior
The header defines no persistent fields of its own. It relies on inherited `ProtocolHandler`/`HttpHandler` state for the virtual identity, accumulated body, and response pointer. All namespace state changes are implementation details in `HttpHandler.cc`.

## Dependencies and Integration Points
The declaration depends on `common/http/HttpHandler.hh`, `mgm/Namespace.hh`, and standard string/map types. It is instantiated by `mgm/http/ProtocolHandlerFactory.hh` and called by both the libmicrohttpd and XrdHttp server paths in `HttpServer.cc`.

## Risks
Ownership is raw-pointer based: the constructor receives a raw `VirtualIdentity*`, and verb methods return raw response pointers. Correct lifetime depends on the common protocol-handler framework and server cleanup paths. Since `Matches()` is broad, WebDAV must be checked first to prevent WebDAV methods or headers from falling into plain HTTP accidentally.

## Test Signals
Header-level tests should verify factory selection order, method matching for all supported verbs, HEAD reusing GET behavior, and response ownership cleanup through the common protocol-handler lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpServer.cc -->
# sources/distributed-fs/eos/mgm/http/HttpServer.cc

## Purpose
`HttpServer.cc` implements the MGM HTTP front end for both the legacy libmicrohttpd path and the XrdHttp extension path. It normalizes headers, authenticates clients, maps them to EOS virtual identities, builds `HttpRequest` objects, invokes a protocol handler, and returns the generated response.

## Important APIs, Types, and Functions
Under `EOS_MICRO_HTTPD`, `Handler()` manages libmicrohttpd's multi-call body lifecycle and `CompleteHandler()` logs disconnect reasons. `MapHttpVerbToAOP()` maps GET/PUT/DELETE to XRootD authorization operations. `XrdHttpHandler()` is the XrdHttp entry point and supports native XrdHttp, nginx/proxy, and S3 authorization cases. `BuildPathAndEnvOpaque()` extracts `xrd-http-fullresource`, merges authorization and `xrd-http-query`, rejects duplicate authz sources, and appends `eos.app=http`. `extractOpaqueWithoutAuthz()` removes authz from forwarded opaque data. `ProcessClientDN()` converts RFC2253 comma/reversed DNs to legacy slash order. `Authenticate()` maps SSL DN or `Remote-User` through `/etc/grid-security/grid-mapfile` or username mapping, then calls `Mapping::IdMap()`.

## Control Flow
The microhttpd path authenticates on the first callback, creates a protocol handler, accumulates upload data across callbacks, and queues the final response after `HandleRequest()`. The XrdHttp path waits for namespace boot, sanitizes gateway headers, decides native versus proxy/S3 mapping, creates or authenticates a `VirtualIdentity`, updates `vid->name` and `scope`, creates the protocol handler, builds an `HttpRequest`, and runs it synchronously.

## State and Persistence Behavior
Server-local persistent state is the cached grid-map file content and its last modification time. It is guarded by a static mutex and reloaded when `/etc/grid-security/grid-mapfile` changes. Per-request state lives in headers, cookies, body strings, `VirtualIdentity`, and protocol handler instances. No file data is persisted here; namespace operations happen in downstream handlers.

## Dependencies and Integration Points
The file depends on XrdHttp, XrdAcc authorization, XrdNet address resolution, EOS `Mapping`, `SecEntity`, `Path`, `StringTokenizer`, `ErrnoToString`, `ProtocolHandlerFactory`, and global `gOFS`. It is the bridge between HTTP clients, reverse proxies/gateways, token/authz opaque data, gridmap identity mapping, REST/plain HTTP/WebDAV handlers, and XRootD authorization plugins.

## Risks
Header trust is subtle: `x-forwarded-for`, `x-real-ip`, `remote-user`, and gateway authorization are accepted only after gateway/sudoer checks, so regressions can become privilege escalation. `BuildPathAndEnvOpaque()` deliberately rejects simultaneous opaque and header authz. Gridmap parsing assumes quoted DN plus username per line and returns null on malformed entries. The destructor joins `mThreadId`, so construction/start lifecycle must ensure the thread is joinable or safe in the base class. Native/proxy path differences need parity for identity fields and opaque query behavior.

## Test Signals
Tests should cover native XrdHttp authz merging, duplicate authz rejection, proxy/S3 authentication, gateway header stripping, sudoer `remote-user` retention, RFC2253 DN conversion, proxy certificate DN fallback, numeric `Remote-User` mapping, gridmap reload on mtime changes, IPv6 `x-real-ip` handling, `vid->scope` population, microhttpd body accumulation, and error behavior for missing `xrd-http-fullresource`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpServer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpServer.hh -->
# sources/distributed-fs/eos/mgm/http/HttpServer.hh

## Purpose
`HttpServer.hh` declares the MGM-specific HTTP server class. It extends the common EOS HTTP server with MGM authentication, XrdHttp request handling, path/opaque normalization, and cached gridmap state.

## Important APIs, Types, and Functions
`HttpServer` derives from `eos::common::HttpServer`. Its constructor sets the port and initializes `mGridMapFileLastModTime`. The destructor logs and joins `mThreadId`. Conditional `Handler()` and `CompleteHandler()` declarations support libmicrohttpd builds. `Authenticate()` maps normalized HTTP headers to a `VirtualIdentity`. `XrdHttpHandler()` is the public XrdHttp extension hook. `extractPathAndOpaque()` splits a full path on `?`, canonicalizes the path with `eos::common::Path`, and returns opaque data without the leading question mark. Private helpers include `ProcessClientDN()`, `BuildPathAndEnvOpaque()`, and `extractOpaqueWithoutAuthz()`.

## Control Flow
Callers enter either through the microhttpd handler or through `XrdHttpHandler()`. Both paths authenticate, select a protocol handler, and delegate final request processing. The helper functions normalize path/opaque data before identity mapping so authorization checks see canonical paths and EOS opaque data.

## State and Persistence Behavior
The class stores only cached gridmap contents and modification time. This cache affects future identity mappings but is derived from `/etc/grid-security/grid-mapfile`; it is not an EOS persistence layer. Request bodies, headers, identities, and responses are transient.

## Dependencies and Integration Points
The header includes common HTTP server/protocol abstractions, `common/Mapping`, `common/Path`, XrdHttp extension types, and the tape REST handler declaration. It is consumed by MGM startup and XrdHttp integration code, and it supplies response helper methods inherited from the common server base to `HttpHandler.cc`.

## Risks
The destructor's unconditional `join()` requires the inherited thread member to be in a valid state. The inline `extractPathAndOpaque()` canonicalizes paths after splitting, so callers must not expect raw URI spelling. Private helper visibility is relaxed under `IN_TEST_HARNESS`, signaling that authentication and opaque handling are important unit-test surfaces.

## Test Signals
Tests should target `extractPathAndOpaque()` canonicalization, empty/missing opaque handling, authz stripping, DN processing, gridmap cache reload behavior, destructor lifecycle, and `XrdHttpHandler()` returning null with an explanatory error when required headers or mappings fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/HttpServer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/ProtocolHandlerFactory.hh -->
# sources/distributed-fs/eos/mgm/http/ProtocolHandlerFactory.hh

## Purpose
`ProtocolHandlerFactory.hh` declares the MGM protocol-handler factory. It chooses between WebDAV and plain HTTP handlers for a request after authentication has produced a `VirtualIdentity`.

## Important APIs, Types, and Functions
`ProtocolHandlerFactory` derives from `eos::common::ProtocolHandlerFactory` and implements inline `CreateProtocolHandler(method, headers, vid)`. It checks `WebDAVHandler::Matches()` first, then `HttpHandler::Matches()`, returning a newly allocated `WebDAVHandler` or `HttpHandler`, or `NULL` if no protocol matches.

## Control Flow
`HttpServer.cc` constructs this factory per request after identity mapping. The factory does not inspect URLs or bodies; method and headers determine the protocol. WebDAV precedence is important because plain HTTP accepts many ordinary verbs and could otherwise steal WebDAV-style requests.

## State and Persistence Behavior
The factory is stateless. It transfers the raw `VirtualIdentity*` to the selected handler constructor. No persistent storage or namespace state is touched.

## Dependencies and Integration Points
The header depends on MGM `HttpHandler`, `WebDAVHandler`, and the common protocol factory. It is a central integration point between server authentication and request-specific protocol implementations.

## Risks
Ownership and failure paths are raw-pointer based. If no handler matches, the caller remains responsible for the `VirtualIdentity*` passed into the factory; current callers use `vid.release()` when constructing the handler, so null returns need careful leak avoidance. Match ordering is behaviorally significant and should not be casually reordered.

## Test Signals
Tests should verify WebDAV precedence, plain HTTP fallback, null return for unknown methods, virtual identity ownership on success/failure, and factory behavior when WebDAV matching depends on headers rather than method alone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/ProtocolHandlerFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml.hpp -->
# sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml.hpp

## Purpose
`rapidxml.hpp` is the embedded RapidXML 1.13 header providing a non-validating XML parser and DOM implementation. It is designed for speed, in-place parsing, and pool-backed DOM allocation.

## Important APIs, Types, and Functions
The public surface includes `parse_error`, parse flags such as `parse_non_destructive`, `parse_fastest`, and `parse_full`, `node_type`, `memory_pool<Ch>`, `xml_base<Ch>`, `xml_attribute<Ch>`, `xml_node<Ch>`, and `xml_document<Ch>`. `memory_pool` allocates nodes, attributes, and strings from a static block plus dynamic blocks. `xml_node` exposes tree/attribute traversal and mutation methods. `xml_document::parse<Flags>()` is the main parser entry and `clear()` resets the DOM and pool.

## Control Flow
Parsing starts with BOM skipping, then repeatedly scans top-level nodes. `parse_node()` dispatches elements, declarations, processing instructions, comments, CDATA, and doctype. Element parsing extracts the name, attributes, and contents. Text and attribute values are scanned through lookup-table predicates, optionally translating XML entities, normalizing whitespace, trimming text, and inserting string terminators into the source buffer. Closing tag validation is optional.

## State and Persistence Behavior
DOM nodes do not own external strings unless those strings were allocated from the document pool. By default parsing mutates the input buffer by inserting null terminators and replacing entity references. `parse_non_destructive` prevents those mutations at the cost of requiring `name_size()` and `value_size()` aware consumers. All pool allocations are freed together by `clear()` or destruction; individual free is not supported.

## Dependencies and Integration Points
The header is self-contained apart from standard library headers unless `RAPIDXML_NO_STDLIB` or `RAPIDXML_NO_EXCEPTIONS` are defined. In this EOS tree it supports XML parsing used by MGM HTTP/WebDAV code and is paired with `rapidxml_print.hpp` and `rapidxml_utils.hpp`.

## Risks
The parser is non-validating and accepts some constructs leniently, including multiple doctypes unless flags dictate otherwise. Input buffers must outlive the DOM and must be mutable unless non-destructive parsing is selected. Many accessors rely on assertions for misuse such as requesting last child when none exists. There is no built-in XXE expansion, but doctype text can be retained if requested. Deep or hostile XML can consume pool memory or recursion-like call depth through nested parsing.

## Test Signals
Tests should cover destructive versus non-destructive parsing, entity translation, UTF-8 numeric entities, whitespace trim/normalize combinations, closing-tag validation, comments/declarations/PI/doctype flags, CDATA handling, DOM mutation methods, memory-pool custom allocators, clear/reparse lifecycle, and malformed XML exceptions with useful `where()` pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_print.hpp -->
# sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_print.hpp

## Purpose
`rapidxml_print.hpp` implements RapidXML DOM serialization. It prints XML nodes to output iterators or streams, escaping data and attributes and optionally suppressing indentation.

## Important APIs, Types, and Functions
The public API is `print(out, node, flags)`, stream `print(out, node, flags)`, `operator<<`, and `print_no_indenting`. Internal helpers include `print_node()`, `print_children()`, `print_attributes()`, and node-type-specific printers for data, CDATA, element, declaration, comment, doctype, and processing-instruction nodes. Character helpers copy, escape, fill indentation, and choose attribute quote style.

## Control Flow
`print()` dispatches by node type. Document nodes print children. Element nodes print an opening tag and attributes, then either self-close, print inline data, or recursively print children with increased indentation before writing the closing tag. Attribute values are escaped and quoted with the quote character that minimizes expansion. Data nodes escape XML-sensitive characters, while CDATA, comments, doctype, and PI values are emitted mostly verbatim.

## State and Persistence Behavior
The printer is stateless and does not mutate the DOM. Output is streamed through the caller's iterator or stream. Formatting state is limited to flags and the current indentation depth.

## Dependencies and Integration Points
It depends on `rapidxml.hpp` and optionally `<ostream>`/`<iterator>` unless `RAPIDXML_NO_STREAMS` is defined. It is the serialization companion for XML DOMs built by the embedded RapidXML parser.

## Risks
CDATA, comments, PI, and doctype values are not validated or escaped, so invalid sequences already present in the DOM can produce invalid XML. Indenting uses tabs and appends a newline after every printed node unless disabled. Attribute printing skips attributes with null name or value pointers. Output iterators must be valid and capable of receiving all emitted characters.

## Test Signals
Tests should cover escaping for text and attributes, quote selection, self-closing elements, inline data versus child-node formatting, `print_no_indenting`, stream operator output, declaration/comment/doctype/PI serialization, and invalid DOM content behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_print.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_utils.hpp -->
# sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_utils.hpp

## Purpose
`rapidxml_utils.hpp` provides small convenience utilities around RapidXML: loading an entire file/stream into a null-terminated buffer and counting a node's children or attributes.

## Important APIs, Types, and Functions
`rapidxml::file<Ch>` owns a `std::vector<Ch>` buffer and has constructors for filenames and input streams. `data()` returns mutable or const buffer pointers, and `size()` returns the vector size including the trailing zero. `count_children(node)` and `count_attributes(node)` iterate sibling/attribute lists and return counts.

## Control Flow
The filename constructor opens a binary stream, determines size with seek/tell, resizes the vector to `size + 1`, reads the content, and appends a zero. The stream constructor reads via iterators, checks stream state, and appends a zero. Counting helpers walk `first_node()/next_sibling()` or `first_attribute()/next_attribute()`.

## State and Persistence Behavior
`file<Ch>` owns the buffer for its lifetime, which is important because RapidXML DOM nodes usually point into the parsed source buffer. The helpers do not persist anything outside memory.

## Dependencies and Integration Points
The header depends on `rapidxml.hpp`, `vector`, `string`, `fstream`, and `stdexcept`. It is useful for callers that need a mutable, null-terminated buffer before passing data to `xml_document::parse()`.

## Risks
`size()` includes the trailing null, which can surprise callers expecting file byte count. The filename constructor uses `tellg()` cast to `size_t`, so stream errors or huge files need care. Loading is all-at-once and unsuitable for unbounded XML inputs. Counting helpers assume a valid node pointer.

## Test Signals
Tests should cover successful file and stream loading, missing-file exceptions, stream read failures, null termination, mutable `data()` compatibility with parsing, count helpers on empty and populated nodes, and expected `size()` semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rapidxml/rapidxml_utils.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/Constants.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/Constants.hh

## Purpose
`Constants.hh` centralizes a few REST API string constants used by the MGM tape REST API and URL parameter parsing.

## Important APIs, Types, and Functions
The header defines `TAPE_REST_API_SWITCH_ON_OFF` as `taperestapi.status`, `TAPE_REST_API_STAGE_SWITCH_ON_OFF` as `taperestapi.stage`, and inline `std::string URLPARAM_ID` as `{id}` inside the REST namespace.

## Control Flow
There is no runtime control flow. Other REST components include this header when checking configuration switches or extracting route parameters from URL patterns.

## State and Persistence Behavior
The constants are compile-time or inline static values. The switch names refer to external configuration state, but this header does not read or write configuration.

## Dependencies and Integration Points
It depends on `mgm/Namespace.hh` for REST namespace macros. `URLPARAM_ID` is used by stage actions with `URLParser::matchesAndExtractParameters()` to retrieve bulk request identifiers.

## Risks
String constants become part of the API/configuration contract. Renaming either tape switch or the `{id}` token without migrating router/business code would silently break feature toggles or parameter extraction.

## Test Signals
Tests should verify route templates and action code use the same `{id}` token, and configuration tests should assert both tape REST switch names match documented MGM configuration keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/Constants.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/Action.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/Action.hh

## Purpose
`Action.hh` declares the abstract base class for MGM REST actions. It binds an HTTP method and access URL pattern to a polymorphic `run()` operation.

## Important APIs, Types, and Functions
`Action` stores `mAccessURLPattern` and `mMethod`. The constructor initializes both. `run(HttpRequest*, const VirtualIdentity*)` is pure virtual and returns an owning `HttpResponse*`. `getAccessURLPattern()` and `getMethod()` expose routing metadata. The destructor is virtual.

## Control Flow
REST handlers build a set of concrete `Action` objects, match incoming requests by URL pattern and method, then call `run()` with the request and mapped identity. Concrete actions own request validation, business calls, and response creation.

## State and Persistence Behavior
The class stores only routing metadata. It does not persist request data or mutate EOS state. Persistence is delegated to concrete action business layers.

## Dependencies and Integration Points
The declaration depends on `VirtualIdentity`, common HTTP request/response/handler types, and JSONifier headers. It is extended by `TapeAction` and concrete tape REST operations.

## Risks
The response ownership contract is raw-pointer based. `run()` implementations need consistent exception handling because the base interface does not encode errors. The URL pattern string is unvalidated here, so router/action registration must keep patterns coherent.

## Test Signals
Tests should cover method/pattern getters, virtual dispatch through `Action*`, response ownership expectations, and router behavior when multiple actions share similar patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/Action.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeAction.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeAction.hh

## Purpose
`TapeAction.hh` declares the abstract base for tape-specific REST actions. It adds access to the tape business interface and common REST response factory on top of the generic `Action` contract.

## Important APIs, Types, and Functions
`TapeAction` derives from `Action`. Its constructor accepts an access URL pattern, HTTP method, and `shared_ptr<ITapeRestApiBusiness>`. It keeps `mTapeRestApiBusiness` and a `RestResponseFactory` member for concrete actions. `run()` remains pure virtual.

## Control Flow
Concrete tape actions receive parsed HTTP requests from the tape REST handler. They validate JSON or URL parameters, invoke `mTapeRestApiBusiness`, and use `mResponseFactory` to create protocol responses.

## State and Persistence Behavior
`TapeAction` itself stores shared business-service ownership and response-factory state. Persistent tape request state is created, queried, canceled, or deleted by the business layer, not this base class.

## Dependencies and Integration Points
The header depends on `Action`, `ITapeRestApiBusiness`, `RestResponseFactory`, and tape REST configuration. It is the common parent for stage, release, and archive-info action classes.

## Risks
The business pointer is not checked for null in the constructor. All concrete actions assume it and their JSON builders/jsonifiers are valid. Shared ownership can hide lifecycle cycles if handlers/business objects retain actions.

## Test Signals
Tests should instantiate simple derived actions with mock `ITapeRestApiBusiness`, verify method/pattern inheritance, and validate consistent error response construction through `RestResponseFactory`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeAction.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeActions.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeActions.hh

## Purpose
`TapeActions.hh` consolidates declarations for the tape REST action classes. It provides a single include for stage bulk request creation/query/cancel/delete, archive info lookup, and release bulk request creation.

## Important APIs, Types, and Functions
The header declares `CreateStageBulkRequest`, `GetStageBulkRequest`, `CancelStageBulkRequest`, `DeleteStageBulkRequest`, `GetArchiveInfo`, and `CreateReleaseBulkRequest`, all deriving from `TapeAction`. Constructors inject URL/method metadata, `ITapeRestApiBusiness`, input `JsonModelBuilder` instances, output `TapeRestApiJsonifier` instances where needed, and for create-stage a `TapeRestHandler` used to generate the `Location` URL.

## Control Flow
Each class overrides `run()`, implemented in the corresponding `.cc` files. The consolidated declarations let handler/factory code register actions from one header while older per-action headers can include this file or duplicate declarations.

## State and Persistence Behavior
The classes retain builder/jsonifier/business dependencies but do not store per-request state. Persistent state is owned by the bulk-request and tape business layers.

## Dependencies and Integration Points
The header depends on tape models, JSON builders/jsonifiers, `TapeRestHandler`, and the tape business interface. It is a registration and compatibility point for the tape REST API implementation.

## Risks
This file overlaps with individual action headers that declare the same class names. Include ordering and one-definition consistency are important. Constructor dependency lists are long and not null-checked, so handler setup tests need to catch missing builders/jsonifiers.

## Test Signals
Tests should compile handler registration through both consolidated and per-action includes, verify all constructors preserve method/pattern metadata, and use mocks to ensure each `run()` path calls the expected business method and response jsonifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeActions.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.cc -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.cc

## Purpose
`GetArchiveInfo.cc` implements the tape REST action that returns archive/tape information for a submitted list of paths.

## Important APIs, Types, and Functions
`GetArchiveInfo::run()` parses the request body into `PathsModel` using `mInputJsonModelBuilder`, calls `mTapeRestApiBusiness->getFileInfo(paths.get(), vid)`, wraps the resulting `bulk::QueryPrepareResponse` in `GetArchiveInfoResponseModel`, assigns `mOutputObjectJsonifier`, and returns an `OK` JSON response.

## Control Flow
The action first validates JSON. `JsonValidationException` becomes `400 Bad Request`. Business exceptions from `getFileInfo()` become `500 Internal Error`. On success, response-model creation and jsonification are delegated to the response factory.

## State and Persistence Behavior
The action does not persist state. It queries archive information through the tape business interface. Any backend reads or cache effects happen below `ITapeRestApiBusiness`.

## Dependencies and Integration Points
It depends on `GetArchiveInfo.hh`, REST exceptions, `GetArchiveInfoResponseModel`, `PathsModel`, `bulk::QueryPrepareResponse`, and `RestResponseFactory`. It integrates the HTTP REST layer with the tape prepare/query business path.

## Risks
Only `TapeRestApiBusinessException` is caught from the business call; other exceptions propagate through the REST handler. A null builder, business pointer, or jsonifier would fail at runtime. The action returns `500` for all business-layer failures, so client-visible error specificity is limited.

## Test Signals
Tests should cover malformed JSON, valid path lists, business success json output, business exception to `500`, empty path-list validation, virtual identity forwarding, and jsonifier invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.hh

## Purpose
`GetArchiveInfo.hh` declares the tape REST action for archive information queries over a JSON path list.

## Important APIs, Types, and Functions
`GetArchiveInfo` derives from `TapeAction`. Its constructor injects access URL, method, tape business service, `JsonModelBuilder<PathsModel>`, and `TapeRestApiJsonifier<GetArchiveInfoResponseModel>`. `run()` is overridden in the `.cc` file. The class stores the input builder and output jsonifier as shared pointers.

## Control Flow
The tape REST handler registers this action for its route. At runtime, `run()` builds `PathsModel`, queries business state, and serializes a response model.

## State and Persistence Behavior
The header defines dependency state only. It does not own request or archive metadata. Persistent archive state is queried through the business dependency.

## Dependencies and Integration Points
It includes `TapeAction`, `JsonModelBuilder`, `TapeRestApiJsonifier`, and `GetArchiveInfoResponseModel`. `PathsModel` is referenced as the expected input model through included tape action/model headers.

## Risks
Dependency pointers are assumed valid. This per-action declaration overlaps with the consolidated `TapeActions.hh` declaration, so duplicate declarations must remain structurally identical.

## Test Signals
Compile tests should include this header alone and alongside `TapeActions.hh`. Unit tests should inject mock builders/jsonifiers/business services and verify constructor wiring through `run()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.cc -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.cc

## Purpose
`CreateReleaseBulkRequest.cc` implements the tape REST action that asks the tape business layer to release disk replicas for a JSON list of paths.

## Important APIs, Types, and Functions
`CreateReleaseBulkRequest::run()` parses the request body into `PathsModel`, calls `mTapeRestApiBusiness->releasePaths(paths.get(), vid)`, and returns an empty `200 OK` response on success. JSON validation errors produce `400 Bad Request`; tape business exceptions produce `500 Internal Error`.

## Control Flow
The action is a direct validate-call-respond adapter. No URL parameters are read and no response model is built because success is represented by an empty OK response.

## State and Persistence Behavior
The action itself has no persistence. Releasing paths may mutate file residency or tape-related state in the business/backend layer, but that is outside this HTTP adapter.

## Dependencies and Integration Points
It depends on `CreateReleaseBulkRequest.hh`, REST exceptions, `PathsModel`, `JsonModelBuilder`, `ITapeRestApiBusiness`, and `RestResponseFactory`. It maps the REST release endpoint to `releasePaths()`.

## Risks
All domain failures are collapsed to `500` except JSON validation. There is no explicit not-found or per-path partial-failure response at this layer. Null dependencies would fail at runtime.

## Test Signals
Tests should cover invalid JSON, successful release with identity forwarding, empty success response, business exception mapping, empty/missing path-list validation, and ensuring no output jsonifier is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.hh

## Purpose
`CreateReleaseBulkRequest.hh` declares the tape REST action for release requests that operate on a JSON list of paths.

## Important APIs, Types, and Functions
`CreateReleaseBulkRequest` derives from `TapeAction`. Its constructor injects URL, method, tape business service, and a `JsonModelBuilder<PathsModel>`. The class stores the builder and overrides `run()`.

## Control Flow
The registered action parses request JSON and delegates to `releasePaths()` in its implementation. It does not use URL parameters or output model serialization.

## State and Persistence Behavior
Only shared dependency pointers are stored. Persistent release effects are delegated to the tape business implementation.

## Dependencies and Integration Points
It includes `TapeAction`, `JsonModelBuilder`, and tape JSON headers. The file includes `TapeAction.hh` twice, which is harmless because of include guards but unnecessary.

## Risks
The duplicated include is low risk but signals header churn. Like other per-action headers, it must stay in sync with `TapeActions.hh` if both declaration styles remain. Constructor dependencies are unchecked.

## Test Signals
Compile tests should include this header with and without `TapeActions.hh`. Unit tests should mock the builder and business layer to validate `run()` behavior for success and validation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CancelStageBulkRequest.cc -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CancelStageBulkRequest.cc

## Purpose
`CancelStageBulkRequest.cc` implements cancellation of selected paths within an existing tape stage bulk request.

## Important APIs, Types, and Functions
`CancelStageBulkRequest::run()` parses a `PathsModel` from the request body, extracts `{id}` from the URL using `URLParser::matchesAndExtractParameters()`, and calls `mTapeRestApiBusiness->cancelStageBulkRequest(requestId, paths.get(), vid)`. It maps `JsonValidationException` to `400`, `ObjectNotFoundException` to `404`, and `FileDoesNotBelongToBulkRequestException` to `400`.

## Control Flow
The action validates body JSON before URL-derived business execution. After parameter extraction, the business layer performs ownership and cancellation checks. Success returns an empty `200 OK`.

## State and Persistence Behavior
The action has no local persistence. Cancellation state and path membership are maintained by the bulk-request backend through the business layer.

## Dependencies and Integration Points
It depends on `URLParser`, `URLBuilder` headers, `PathsModel`, REST exceptions, `Constants.hh`, and the tape business interface. It integrates the REST route pattern's `{id}` token with bulk-request cancellation.

## Risks
The extracted `requestParameters[URLPARAM_ID]` is used without checking whether the parser actually matched and populated the key. Unexpected business exceptions are not caught. The included `RealMgmFileSystemInterface.hh` appears unused in this file, adding compile coupling.

## Test Signals
Tests should cover invalid JSON, route match and missing-id behavior, not-found to `404`, non-member path to `400`, successful partial cancellation, identity forwarding, and no mutation when JSON parsing fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CancelStageBulkRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CancelStageBulkRequest.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CancelStageBulkRequest.hh

## Purpose
`CancelStageBulkRequest.hh` declares the tape REST action used to cancel paths from an existing stage bulk request.

## Important APIs, Types, and Functions
`CancelStageBulkRequest` derives from `TapeAction`. Its constructor injects URL, method, tape business service, and `JsonModelBuilder<PathsModel>`. It stores the builder and overrides `run()`.

## Control Flow
At runtime, the implementation parses path JSON, extracts the request id from the registered URL pattern, and delegates cancellation to the business layer.

## State and Persistence Behavior
Only action dependencies are stored. Bulk-request cancellation state is persisted by the business/backend implementation, not by the action.

## Dependencies and Integration Points
The header depends on `TapeAction`, `JsonModelBuilder`, `PathsModel`, and `TapeRestApiBusiness`/`ITapeRestApiBusiness` types. It is registered by the tape REST handler for cancel-stage endpoints.

## Risks
The header includes the concrete `TapeRestApiBusiness.hh` even though the constructor takes the interface pointer, increasing compile coupling. Null dependency handling is absent. It must remain declaration-compatible with `TapeActions.hh`.

## Test Signals
Compile tests should include this header independently. Unit tests should validate constructor dependency wiring and `run()` behavior with mocked JSON parsing and business cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CancelStageBulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.cc -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.cc

## Purpose
`CreateStageBulkRequest.cc` implements creation of a tape stage bulk request from a JSON request body and returns a response containing the new request id and `Location` URL.

## Important APIs, Types, and Functions
`CreateStageBulkRequest::run()` builds a `CreateStageBulkRequestModel`, calls `mTapeRestApiBusiness->createStageBulkRequest(model.get(), vid)`, constructs `CreatedStageBulkRequestResponseModel` from `bulkRequest->getId()`, assigns `mOutputObjectJsonifier`, and returns a `201 Created` response with a `Location` header. `generateAccessURL()` uses `mTapeRestHandler->getAccessURLBuilder()->add(getAccessURLPattern())->add(bulkRequestId)->build()`.

## Control Flow
The action validates JSON, delegates creation, builds response metadata, and returns. JSON validation errors become `400`; tape business exceptions become `500`. Successful control flow depends on the business layer returning a non-null `bulk::BulkRequest`.

## State and Persistence Behavior
The action persists nothing directly. Stage bulk request creation and any MGM bulk-request records are performed by `ITapeRestApiBusiness`. The action exposes the persistent request id through the response body and `Location` header.

## Dependencies and Integration Points
It depends on `BulkRequest`, tape models/jsonifiers, `TapeRestHandler` URL building, REST exceptions, and the global MGM headers included for broader context. It is the REST entry point for staging files from tape back to disk.

## Risks
`mTapeRestHandler` and returned access URL builder are assumed non-null. The generated URL concatenates the action pattern and id; pattern semantics must match router expectations. All business failures map to `500`, and unexpected exceptions are not caught. The implementation includes several headers that appear unused, increasing compile coupling.

## Test Signals
Tests should cover invalid JSON, business failure, successful request id propagation, `201` status, `Location` header construction, jsonifier use, identity forwarding, and null/empty bulk request id handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.hh

## Purpose
`CreateStageBulkRequest.hh` is a compatibility include for the create-stage action declaration now provided by the consolidated `TapeActions.hh`.

## Important APIs, Types, and Functions
The header includes `mgm/http/rest-api/action/tape/TapeActions.hh` and then contains `using CreateStageBulkRequest = CreateStageBulkRequest;` inside the REST namespace.

## Control Flow
There is no request-time control flow in this header. Its intended role is to let code include the historical per-action path while resolving the class declaration from `TapeActions.hh`.

## State and Persistence Behavior
The header defines no state and performs no persistence. Runtime behavior lives in `CreateStageBulkRequest.cc` and the class declaration in `TapeActions.hh`.

## Dependencies and Integration Points
It depends on `mgm/Namespace.hh` and `TapeActions.hh`. It is included by `CreateStageBulkRequest.cc` and possibly by older registration code that has not moved to the consolidated header.

## Risks
The self-referential alias form is suspicious: because `TapeActions.hh` declares `CreateStageBulkRequest` in the same namespace, `using CreateStageBulkRequest = CreateStageBulkRequest;` can be redundant at best and a compile-surface risk depending on compiler/name-lookup rules. This header should be covered by compile tests before refactoring.

## Test Signals
Tests should compile this header alone, include it after `TapeActions.hh`, include it before code that instantiates `CreateStageBulkRequest`, and verify no duplicate-declaration or alias diagnostics occur on supported compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.cc -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.cc

## Purpose
`DeleteStageBulkRequest.cc` implements deletion of an existing tape stage bulk request identified by the URL `{id}` parameter.

## Important APIs, Types, and Functions
`DeleteStageBulkRequest::run()` constructs a `URLParser` from the request URL, extracts `URLPARAM_ID` from `mAccessURLPattern`, and calls `mTapeRestApiBusiness->deleteStageBulkRequest(requestId, vid)`. `ObjectNotFoundException` maps to `404`; `TapeRestApiBusinessException` maps to `500`; success returns an empty `200 OK`.

## Control Flow
No request body is parsed. The URL id is extracted, the business layer deletes the request, and the response factory converts the result into HTTP status.

## State and Persistence Behavior
Persistent deletion happens in the tape bulk-request business/backend layer. This action stores no request state and does not directly modify files or namespace metadata.

## Dependencies and Integration Points
It depends on `URLParser`, `Constants.hh`, REST exceptions, and the tape business interface. It integrates the REST route for deleting or forgetting stage bulk requests with backend state cleanup.

## Risks
The action does not verify that URL parsing matched before indexing `requestParameters[URLPARAM_ID]`. It returns `200 OK` instead of `204 No Content`, which may be an intentional API contract but should be documented. Unexpected exceptions propagate.

## Test Signals
Tests should cover successful delete, not-found mapping, generic business failure, missing or malformed id routes, identity forwarding, and response status/body expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.hh

## Purpose
`DeleteStageBulkRequest.hh` declares the tape REST action for deleting a stage bulk request by id.

## Important APIs, Types, and Functions
`DeleteStageBulkRequest` derives from `TapeAction`. Its constructor injects access URL, method, and tape business service, then forwards them to the base. It overrides `run()` and stores no additional members.

## Control Flow
The concrete implementation extracts the request id from the URL and delegates deletion to the business layer. The header only provides the type contract for registration and dispatch.

## State and Persistence Behavior
No additional state is stored beyond the base `TapeAction` members. Backend persistence is handled by `deleteStageBulkRequest()`.

## Dependencies and Integration Points
It includes `TapeAction.hh` and MGM namespace macros. It is registered by the tape REST handler for delete-stage endpoints and overlaps with the declaration in `TapeActions.hh`.

## Risks
Duplicate declarations between this header and `TapeActions.hh` must stay identical. The class has no builder/jsonifier dependencies, so route setup mistakes may only appear at runtime through URL parsing.

## Test Signals
Compile tests should include both declaration paths. Unit tests should instantiate the action with a mock business service and verify deletion status mapping through `run()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.cc -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.cc

## Purpose
`GetStageBulkRequest.cc` implements retrieval of a tape stage bulk request status/model by id.

## Important APIs, Types, and Functions
`GetStageBulkRequest::run()` extracts `{id}` from the URL with `URLParser`, calls `mTapeRestApiBusiness->getStageBulkRequest(requestId, vid)`, sets `mOutputObjectJsonifier` on the returned `GetStageBulkRequestResponseModel`, and returns an `OK` response. It maps `ObjectNotFoundException` to `404` and `TapeRestApiBusinessException` to `500`.

## Control Flow
The action has no request body. It resolves the route id, asks the business layer for a response model, attaches serialization behavior, and delegates HTTP response construction to `RestResponseFactory`.

## State and Persistence Behavior
The action is read-only at this layer. Persistent bulk-request state is read through the business implementation; no local cache is maintained.

## Dependencies and Integration Points
It depends on `GetStageBulkRequestResponseModel`, `URLParser`, `Constants.hh`, REST exceptions, `TapeRestApiJsonifier`, and `ITapeRestApiBusiness`. It connects the REST status endpoint to bulk-request state.

## Risks
Missing id extraction is not checked before map indexing. A null response model from the business layer would be dereferenced. The response model is responsible for serialization after `setJsonifier()`, so jsonifier misconfiguration breaks output late.

## Test Signals
Tests should cover successful retrieval, output JSON shape, not-found and generic failure mapping, missing id behavior, null response-model protection, identity forwarding, and jsonifier assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.hh -->
# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.hh

## Purpose
`GetStageBulkRequest.hh` declares the tape REST action that returns status/details for a stage bulk request.

## Important APIs, Types, and Functions
`GetStageBulkRequest` derives from `TapeAction`. Its constructor injects URL, method, tape business service, and `TapeRestApiJsonifier<GetStageBulkRequestResponseModel>`. It stores the jsonifier and overrides `run()`.

## Control Flow
The handler dispatches matched GET requests to `run()`, which extracts a request id, fetches the response model, and serializes it.

## State and Persistence Behavior
Only dependency pointers are stored. Stage bulk request state is read from backend services through the business layer.

## Dependencies and Integration Points
The header depends on `TapeAction`, `TapeRestApiJsonifier`, and `GetStageBulkRequestResponseModel`. It is part of the tape REST action registration surface and mirrors a declaration in `TapeActions.hh`.

## Risks
The constructor parameter formatting is tight but valid; more importantly, duplicate declarations must stay synchronized. Null jsonifier/business dependencies are not guarded.

## Test Signals
Compile tests should include this header alone and with `TapeActions.hh`. Unit tests should mock the business response model and ensure `run()` sets the jsonifier before response creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.hh -->
