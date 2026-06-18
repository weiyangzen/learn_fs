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
