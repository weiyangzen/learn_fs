# sources/distributed-fs/eos/unit_tests/mgm/http/HttpServerTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/http/HttpServerTests.cc

Purpose: tests static HTTP path and opaque-token parsing helpers in `HttpServer`.

Important APIs and types: `HttpServer::BuildPathAndEnvOpaque`, `extractPathAndOpaque`, `extractOpaqueWithoutAuthz`, `XrdOucEnv`, normalized HTTP header maps, `xrd-http-fullresource`, `authorization`, `authz`, and `eos.app`.

Control flow: `ParsePathAndToken` verifies missing resource failure, plain resource success, authz from query opaque, authz from header, conflict rejection when both are present, propagation of extra opaque fields, default `eos.app=http`, and client app suffixing as `http/<value>`. Table-driven tests split full paths into path/opaque pairs and strip `authz` from opaque strings regardless of position.

State and persistence: parsing creates a per-call `XrdOucEnv` object; no global state.

Dependencies and integration: uses `IN_TEST_HARNESS` to access test-visible `HttpServer` internals. These helpers integrate HTTP requests with MGM authorization and opaque-info conventions.

Risks and test signals: token precedence and duplicate `eos.app` handling are security-sensitive. The tests assert conflict failure when authorization is supplied both in header and opaque data.
