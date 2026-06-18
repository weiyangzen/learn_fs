# sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.cc

## Purpose

`EosMgmHttpHandler.cc` implements the EOS MGM XRootD HTTP extension handler. It is the runtime bridge between XRootD HTTP requests and EOS MGM services: it loads the EOS MGM OFS plugin, optionally wires token authorization plugins, recognizes macaroon and REST gateway requests, normalizes request headers, forwards request bodies into EOS HTTP protocol handlers, and sends responses back through `XrdHttpExtReq::SendSimpleResp`.

The file also provides the `extern "C"` plugin entry point `XrdHttpGetExtHandler`, so it is part of the dynamically loaded XRootD plugin ABI rather than only an internal EOS class implementation.

## Important APIs, Types, and Functions

- `XrdHttpGetExtHandler(...)` is the exported factory. It allocates `EosMgmHttpHandler`, calls `Init()` and `Config()`, and returns the handler pointer or `nullptr` on initialization failure.
- `EosMgmHttpHandler::Config()` parses the XRootD/MGM configuration file, detects `eos::mgm::http::redirect-to-https=1`, finds `xrootd.fslib`, parses `mgmofs.macaroonslib`, loads the MGM OFS plugin, and chains token authorization plugins.
- `MatchesPath()` accepts most HTTP paths and rejects only `COPY` and `OPTIONS`, leaving those to the XrdHttpTPC plugin.
- `generateResponseHeaders()` adds `Date` and `X-Eos-Mgm-Version`, copies response headers except `Content-Length`, and rewrites `Location` to `https:` when redirect-to-HTTPS is enabled and request proxy headers allow it.
- `ProcessReq()` is the main dispatcher for shutdown handling, macaroon requests, REST gateway requests, REST-manager body reads, PROPFIND bodies, EOS HTTP handler invocation, and final response transmission.
- `ProcessMacaroonPOST()` remaps VOMS-authenticated identities through EOS VID mapping before delegating the request to the XrdMacaroons handler.
- `ProcessRestApiPost()` forwards REST API gateway POSTs to the local grpc-gateway URL using libcurl.
- `RestApiGwFrwAuthHeaders()` converts XRootD security and authorization data into `Grpc-Metadata-*` headers.
- `GetOfsLibPath()`, `GetAuthzLibPaths()`, and `GetHttpExtLibPath()` parse configured library tokens.
- `GetOfsPlugin()`, `GetHttpExtPlugin()`, and `GetAuthzPlugin()` resolve shared libraries with `XrdOucPinPath`, load symbols with `XrdSysPlugin`, and persist the loaded plugins.
- `readBody()` drains `XrdHttpExtReq` body buffers in 1 MiB aggregate reads backed by 256 KiB XRootD buffer chunks.
- `IsMacaroonRequest()` detects `POST` requests with `Content-Type: application/macaroon-request`.
- `IsRestApiRequest()` detects `POST` resources containing `/v1/eos/rest/gateway/`.

## Control Flow

Startup enters through `XrdHttpGetExtHandler`. The handler object is created, `Init()` is effectively a no-op, and `Config()` performs the meaningful work. Config parsing is line-oriented. When an `xrootd.fslib` line is seen, the file loads `XrdSfsGetFileSystem` from the configured library and stores the resulting `XrdMgmOfs*`. When a `mgmofs.macaroonslib` line is seen, it records the macaroon HTTP extension library and one or two authorization libraries. Missing macaroon configuration is not fatal; missing MGM OFS/authz after token configuration is fatal.

During request handling, `ProcessReq()` first rejects requests if the MGM OFS shutdown flag is set. It then lowercases all incoming header names into a normalized map. Macaroon token requests are routed through MGM redirection first via `ShouldRoute()`, because a slave MGM should redirect to the HTTP port of the current master. If no redirect is needed and the macaroon plugin is available, control is delegated to `ProcessMacaroonPOST()`.

If the MGM REST grpc server is available and the resource path matches the REST gateway prefix, `ProcessRestApiPost()` reads the body, extracts the final path segment as the EOS command name, builds `mRestApiGwUrl + mRestApiGwPath + command`, forwards auth metadata with curl, and returns either a 200 response containing grpc-gateway data or a 500 error.

All remaining requests go through EOS's internal HTTP stack. REST-manager requests have their body read with `readBody()`. Non-REST `PROPFIND` bodies are read directly from XRootD buffers. The code then calls `mMgmOfsHandler->mHttpd->XrdHttpHandler(...)` with verb, resource, normalized headers, empty cookies, request body, client security entity, optional token authz handler, and an error string. The returned `ProtocolHandler` supplies an `HttpResponse`, which is serialized into XRootD's simple response API. `HEAD` is special-cased to return no body while preserving the parsed content length.

## State and Persistence Behavior

This file keeps only process-local handler state. It stores pointers to dynamically loaded plugins (`mTokenHttpHandler`, `mTokenAuthzHandler`, `mMgmOfsHandler`) and configuration values (`mRedirectToHttps`, REST gateway URL/path). It mutates MGM global state once by calling `mMgmOfsHandler->SetTokenAuthzHandler(mTokenAuthzHandler)` after successful authz chaining. It does not persist data to disk or namespace storage.

Plugin objects are persisted in memory by `XrdSysPlugin::Persist()`. The destructor logs its invocation but does not unload plugin state or free the plugin pointers explicitly, which matches the usual XRootD plugin lifetime assumption but means ownership is intentionally non-obvious.

## Dependencies and Integration Points

The implementation is tightly integrated with XRootD HTTP extension APIs (`XrdHttpExtHandler`, `XrdHttpExtReq`), XRootD plugin loading (`XrdSysPlugin`, `XrdOucPinPath`), XRootD security (`XrdSecEntity`), XRootD authorization (`XrdAccAuthorize`), EOS MGM OFS (`XrdMgmOfs`), EOS HTTP infrastructure (`HttpServer`, `ProtocolHandler`, `HttpResponse`), EOS VID mapping (`eos::common::Mapping`), and libcurl for grpc-gateway forwarding.

Config semantics depend on `xrootd.fslib` and `mgmofs.macaroonslib` directive shape. Runtime routing depends on MGM master/slave routing via `XrdMgmOfs::ShouldRoute`. REST handling depends on `mRestGrpcSrv`, `mRestApiManager`, and a grpc-gateway listening at the configured local URL.

## Risks and Edge Cases

- `GetHttpExtPlugin()` unconditionally uses `myEnv->PutPtr(...)`; if XRootD ever invokes config with a null environment, this path can dereference null despite comments allowing null.
- `RestApiGwFrwAuthHeaders()` allocates a `curl_slist` and attaches it to the curl handle, but `ProcessRestApiPost()` only calls `curl_easy_cleanup()` and does not call `curl_slist_free_all()`, so repeated REST gateway calls may leak header-list allocations.
- `ProcessRestApiPost()` returns early on `RestApiGwFrwAuthHeaders()` failure without cleaning the initialized curl handle.
- `IsMacaroonRequest()` looks up exactly `Content-Type` in the original header map, while `ProcessReq()` already builds lower-case headers. A lower-case `content-type` header may not be recognized as a macaroon request.
- REST gateway response handling always sends HTTP 200 on successful curl transport and does not propagate grpc-gateway HTTP status codes.
- Redirect rewriting inserts `s` at offset 4 for any `Location` header if redirect conditions match. It assumes the value starts with `http`, so malformed or already-HTTPS values could be rewritten incorrectly.
- Body reading loops until `contentLeft` is zero. If `BuffgetData()` returns 0 before consuming the announced length, `contentLeft` is not reduced and the outer loop can spin indefinitely.
- Plugin loading depends on exact symbols (`XrdSfsGetFileSystem`, `XrdHttpGetExtHandler`, `XrdAccAuthorizeObjAdd`) and ABI compatibility with the compiled XRootD version.

## Test Signals

Useful tests include config-line parsing for `xrootd.fslib` variants and `mgmofs.macaroonslib`, plugin-load failure paths, macaroon request detection with varied header casing, HTTPS redirect header rewriting, `HEAD` content-length behavior, REST gateway forwarding with mocked curl/status handling, shutdown rejection, and body-read error/short-read behavior. Integration tests should exercise MGM master/slave redirection for macaroon requests and verify that token authz chaining falls back to MGM authz in the configured order.
