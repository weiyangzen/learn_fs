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
