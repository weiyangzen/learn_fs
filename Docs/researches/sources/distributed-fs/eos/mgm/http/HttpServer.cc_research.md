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
