<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_routing_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_routing_test.go

Purpose: regression tests for S3 API mux routing, especially overlapping STS, embedded IAM, and bucket routes.

Important APIs/functions: `setupRoutingTestServer` creates a minimal server with enabled IAM, seeded static credentials, embedded IAM, and placeholder `STSHandlers`. `signRoutingTestRequest` signs requests with AWS SigV4 for a requested service. Tests cover query/body STS actions, authenticated IAM, matcher logic, GetFederationToken dispatch, and hostless path-style bucket fallback.

Control flow: tests construct a mux, call `s3a.registerRouter`, send synthetic requests through `router.ServeHTTP` or inspect `router.Match`, and assert status codes or matched routes. STS tests expect 503 from uninitialized STS as proof routing reached `STSHandlers`, while IAM tests assert requests do not reach STS. Host fallback tests only match routes and avoid invoking real handlers.

State and persistence behavior: the test server stores IAM identity state in memory and does not connect to filer/master services. Seeded credentials allow `UnifiedPostHandler` to pass `AuthSignatureOnly` and test body-based STS dispatch.

Dependencies and integration: uses gorilla/mux, AWS SDK v4 signer, memory credential manager, SeaweedFS IAM types, and testify assertions. It directly protects route ordering in `s3api_server.go`.

Risks: expected status codes are proxies for route selection, so unrelated handler validation changes can require test adjustment. The zero-value `STSHandlers` path is intentionally uninitialized; if STS readiness behavior changes, routing assertions may need a more explicit spy handler. Fake IAM setup bypasses some production initialization, so it is not a full auth integration test.

Test signals: this file is itself a signal that `Action=GetFederationToken` must route to STS whether supplied in query or authenticated body, anonymous STS body requests must hit fallback STS, authenticated non-STS POST must hit IAM, and bucket routes must still match arbitrary Host headers when `DomainName` is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_server_routing_test.go -->
