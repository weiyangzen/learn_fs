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
