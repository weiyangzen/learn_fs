# sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.hh

## Purpose

`EosMgmHttpHandler.hh` declares the EOS MGM implementation of `XrdHttpExtHandler`. It defines the class surface used by XRootD to initialize, match, and process HTTP requests, plus private helpers for EOS-specific plugin discovery, macaroon authorization, request body reading, REST gateway forwarding, and response header generation.

## Important APIs, Types, and Functions

- `class EosMgmHttpHandler : public XrdHttpExtHandler, public eos::common::LogId` is the plugin handler type.
- `using HdrsMapT = std::map<std::string, std::string>` names normalized request header maps used by REST forwarding.
- Constructor initializes HTTPS redirect to false and plugin pointers to null. `mRestApiGwUrl` defaults to `http://localhost:40054`; `mRestApiGwPath` defaults to `/v1/eos/rest/gateway/`.
- `Init(const char*) override` is intentionally a no-op because config-time arguments are handled in `Config()`.
- `Config(XrdSysError*, const char*, const char*, XrdOucEnv*)` is the real initialization hook.
- `MatchesPath(const char*, const char*) override` and `ProcessReq(XrdHttpExtReq&) override` form the XRootD request dispatch surface.
- `CopyXrdSecEntity()` is declared as a helper for security entity copying, but this source pair does not define or call it in the inspected implementation.
- Private library parsing/loading helpers declare the dynamic plugin integration contract for OFS, HTTP extension, and authorization plugins.
- `readBody()`, `IsMacaroonRequest()`, `ProcessMacaroonPOST()`, `IsRestApiRequest()`, `ProcessRestApiPost()`, `RestApiGwFrwAuthHeaders()`, `WriteCallback()`, and `generateResponseHeaders()` declare the request-processing helper set.

## Control Flow

The header encodes a lifecycle where XRootD constructs the handler through the exported C factory, calls `Init()` and `Config()`, asks `MatchesPath()` whether the plugin should receive a request, and then calls `ProcessReq()`. Internally, `ProcessReq()` can branch to macaroon plugin delegation, local REST grpc-gateway forwarding, or EOS MGM HTTP protocol handling.

The `IN_TEST_HARNESS` conditional moves private members into public visibility, suggesting unit tests can directly exercise configuration parsing and request classification helpers.

## State and Persistence Behavior

The class owns only runtime pointers and configuration flags. It has no persistent storage fields. Important mutable state includes:

- `mRedirectToHttps`, which affects response header rewriting.
- `mTokenHttpHandler`, the delegated XrdMacaroons HTTP handler.
- `mTokenAuthzHandler`, the chained token authorization object installed into MGM OFS.
- `mMgmOfsHandler`, the loaded MGM OFS plugin pointer used for routing and EOS HTTP handling.
- REST gateway URL/path string literals.

Because pointer ownership is not expressed with smart pointers, ownership and lifetime are delegated to XRootD plugin conventions and `XrdSysPlugin::Persist()` behavior in the implementation.

## Dependencies and Integration Points

The header depends on XRootD HTTP extension headers, XRootD versioning, XRootD authorization/security forward declarations, EOS common logging, EOS `HttpResponse`, and libcurl. It is intentionally coupled to the MGM OFS plugin through a forward declaration because implementation needs an `XrdMgmOfs*`.

The ABI-sensitive entry point itself is implemented in the `.cc` file, but this header defines the class that XRootD will call through virtual methods.

## Risks and Edge Cases

- `CopyXrdSecEntity()` appears declared but not implemented in the inspected file, which may indicate dead API, a missing definition in another build unit, or a latent link issue if used in tests.
- Raw pointers hide ownership. Destruction does not communicate whether delegated plugin handlers or authorization handlers are owned by this class.
- REST gateway URL/path are hard-coded default `const char*` members with no visible setter in the header.
- Several helper methods accept nullable XRootD pointers by comment, but the type signatures do not enforce null handling.
- The public API receives C strings from XRootD, so null or malformed `verb` and `path` handling depends on implementation assumptions.

## Test Signals

Header-level tests should compile the handler under `IN_TEST_HARNESS` and directly exercise helper methods. ABI tests should confirm `EosMgmHttpHandler` still satisfies `XrdHttpExtHandler` overrides after XRootD upgrades. Static checks should flag declared-but-unused/private helpers and raw pointer lifetime assumptions.
